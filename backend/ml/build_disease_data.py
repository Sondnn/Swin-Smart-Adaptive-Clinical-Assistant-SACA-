from __future__ import annotations

import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import (
    BASE_DIR,
    DISEASE_CLASSES_FILE,
    DISEASE_INGEST_REPORT,
    DISEASE_TRAINING_CSV,
    MODEL_DIR,
    MODEL_FEATURES_FILE,
    RAW_DISEASE_FILE,
    REPORTS_DIR,
)
from symptom_mapping import map_v2_symptom
from triage_rules import CAT1_SYMPTOMS, CAT2_SYMPTOMS, CAT3_SYMPTOMS

SEED = 42
TOP_N_DISEASES = 150
ROWS_PER_DISEASE = 40
N_AUGMENTED_COPIES = 1
DROP_PROB = 0.3
ADD_PROB = 0.3

HIGH_ACUITY = set(CAT1_SYMPTOMS) | set(CAT2_SYMPTOMS) | set(CAT3_SYMPTOMS)

TRISTATE_DISTRIBUTIONS = {
    "gender": {0: 0.47, 1: 0.47, 2: 0.06},
    "age_over_65": {0: 0.78, 1: 0.17, 2: 0.05},
    "had_symptoms_before": {0: 0.65, 1: 0.25, 2: 0.10},
    "had_contact": {0: 0.75, 1: 0.15, 2: 0.10},
}

DURATION_BUCKETS = [1, 2, 4, 8, 12, 24, 48, 72, 120]
DURATION_WEIGHTS = [4, 6, 8, 9, 10, 12, 10, 8, 6]


def _sample_demographics(rng: random.Random) -> dict:
    out = {
        col: rng.choices(list(dist.keys()), weights=list(dist.values()), k=1)[0]
        for col, dist in TRISTATE_DISTRIBUTIONS.items()
    }
    out["symptoms_duration"] = rng.choices(
        DURATION_BUCKETS, weights=DURATION_WEIGHTS, k=1
    )[0]
    return out


def _proxy_severity(present: set[str]) -> int:
    high = sum(1 for c in present if c in HIGH_ACUITY)
    if high >= 3:
        return 5
    if high == 2:
        return 4
    if high == 1:
        return 3
    return 2 if len(present) >= 2 else 1


def _finalize_case(
        present: set[str], feature_columns: list[str], demographics: dict
) -> dict:
    case = {col: 0 for col in feature_columns}
    case.update(demographics)
    for c in present:
        case[c] = 1
    case["symptom_severity"] = _proxy_severity(present)
    case["symptom__otherwise_well"] = 1 if case["symptom_severity"] <= 2 else 0
    return case


def _augment(present: set[str], all_symptoms: list[str], rng: random.Random) -> set[str]:
    out = set(present)
    if out and rng.random() < DROP_PROB:
        out.discard(rng.choice(sorted(out)))
    if rng.random() < ADD_PROB:
        absent = [c for c in all_symptoms if c not in out]
        if absent:
            out.add(rng.choice(absent))
    return out


def main():
    feature_columns = json.loads(MODEL_FEATURES_FILE.read_text())
    feature_set = set(feature_columns)
    schema_symptom_cols = [c for c in feature_columns if c.startswith("symptom__")]

    df = pd.read_csv(RAW_DISEASE_FILE)

    top_diseases = df["diseases"].value_counts().head(TOP_N_DISEASES).index
    df = df[df["diseases"].isin(top_diseases)].reset_index(drop=True)

    df = (
        df.groupby("diseases", group_keys=False)
        .sample(n=ROWS_PER_DISEASE, replace=False, random_state=SEED)
        .reset_index(drop=True)
    )

    raw_symptom_cols = [c for c in df.columns if c != "diseases"]
    col_mapping = {c: map_v2_symptom(c, feature_set) for c in raw_symptom_cols}
    unmapped_cols = [c for c, v in col_mapping.items() if v is None]

    rng = random.Random(SEED)
    rows: list[dict] = []
    diseases: list[str] = []
    group_ids: list[int] = []
    n_augmented = 0
    n_skipped = 0

    name_to_idx = {c: i for i, c in enumerate(df.columns)}
    for tup in df.itertuples(index=True, name=None):
        idx = tup[0]
        disease = " ".join(str(tup[name_to_idx["diseases"] + 1]).split()).strip()

        present: set[str] = set()
        for raw_col in raw_symptom_cols:
            target = col_mapping[raw_col]
            if target is None:
                continue
            if tup[name_to_idx[raw_col] + 1] == 1:
                present.add(target)

        if not present:
            n_skipped += 1
            continue

        demographics = _sample_demographics(rng)
        base = _finalize_case(present, feature_columns, demographics)
        rows.append(base);
        diseases.append(disease);
        group_ids.append(idx)

        for _ in range(N_AUGMENTED_COPIES):
            aug_present = _augment(present, schema_symptom_cols, rng)
            if not aug_present:
                continue
            aug = _finalize_case(aug_present, feature_columns, demographics)
            rows.append(aug);
            diseases.append(disease);
            group_ids.append(idx)
            n_augmented += 1

    header = feature_columns + ["disease", "group_id"]
    MODEL_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    with open(DISEASE_TRAINING_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r, d, g in zip(rows, diseases, group_ids):
            writer.writerow([r.get(col, 0) for col in feature_columns] + [d, g])

    disease_classes = sorted(set(diseases))
    DISEASE_CLASSES_FILE.write_text(json.dumps(disease_classes, indent=2))

    disease_counts = Counter(diseases)
    report = {
        "source": str(RAW_DISEASE_FILE.relative_to(BASE_DIR)),
        "top_n_diseases": TOP_N_DISEASES,
        "rows_per_disease_cap": ROWS_PER_DISEASE,
        "n_rows": len(rows),
        "n_groups": len(set(group_ids)),
        "n_augmented": n_augmented,
        "n_skipped_empty": n_skipped,
        "n_diseases": len(disease_classes),
        "mapped_columns": sum(1 for v in col_mapping.values() if v),
        "unmapped_columns_dropped": unmapped_cols,
        "disease_distribution": dict(disease_counts.most_common()),
    }
    DISEASE_INGEST_REPORT.write_text(json.dumps(report, indent=2))

    mapped = sum(1 for v in col_mapping.values() if v)
    print(f"Top diseases: {len(disease_classes)} (cap top-{TOP_N_DISEASES})")
    print(f"Symptom columns mapped: {mapped}/{len(raw_symptom_cols)}")
    print(
        f"Rows: {len(rows):,} "
        f"({len(set(group_ids)):,} base groups, {n_augmented:,} augmented, "
        f"{n_skipped:,} skipped empty)"
    )
    print(f"Wrote -> {DISEASE_TRAINING_CSV.relative_to(BASE_DIR)}")
    print(f"Report -> {DISEASE_INGEST_REPORT.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
