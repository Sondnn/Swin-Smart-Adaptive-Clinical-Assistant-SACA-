# Build the SACA training dataset from dhivyeshrk/diseases-and-symptoms-dataset.
from __future__ import annotations

import csv
import json
import random
from collections import Counter
from pathlib import Path

import pandas as pd

from symptom_mapping import map_v2_symptom
from triage_rules import CAT1_SYMPTOMS, CAT2_SYMPTOMS, CAT3_SYMPTOMS, assign_triage

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw_v2"
DATASET_CSV = RAW_DATA_DIR / "Final_Augmented_dataset_Diseases_and_Symptoms.csv"
OUTPUT_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_FILE = OUTPUT_DIR / "training_data.csv"
MODEL_FEATURES_FILE = OUTPUT_DIR / "model_features.json"
DISEASE_CLASSES_FILE = OUTPUT_DIR / "disease_classes.json"
INGEST_REPORT_FILE = REPORTS_DIR / "ingest_report.json"

SEED = 42
TOP_N_DISEASES = 150
ROWS_PER_DISEASE = 40
N_AUGMENTED_COPIES = 1
DROP_PROB = 0.3
ADD_PROB = 0.3

HIGH_ACUITY = set(CAT1_SYMPTOMS) | set(CAT2_SYMPTOMS) | set(CAT3_SYMPTOMS)


def _proxy_severity(present: set[str]) -> int:
    """Coarse 1-5 severity from how many high-acuity symptoms are present."""
    high = sum(1 for c in present if c in HIGH_ACUITY)
    if high >= 3:
        return 5
    if high == 2:
        return 4
    if high == 1:
        return 3
    return 2 if len(present) >= 2 else 1


def _finalize_case(present: set[str], feature_columns: list[str]) -> dict:
    case = {col: 0 for col in feature_columns}
    case["gender"] = 2
    case["age_over_65"] = 2
    case["had_symptoms_before"] = 2
    case["had_contact"] = 2
    case["symptoms_duration"] = 24
    for c in present:
        case[c] = 1
    case["symptom_severity"] = _proxy_severity(present)
    case["symptom__otherwise_well"] = 1 if case["symptom_severity"] <= 2 else 0
    case["triage_category"] = assign_triage(case)
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

    df = pd.read_csv(DATASET_CSV)

    # 1) Keep top-N diseases by frequency.
    top_diseases = df["diseases"].value_counts().head(TOP_N_DISEASES).index
    df = df[df["diseases"].isin(top_diseases)].reset_index(drop=True)

    # 2) Stratified subsample to ROWS_PER_DISEASE.
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

        base = _finalize_case(present, feature_columns)
        rows.append(base); diseases.append(disease); group_ids.append(idx)

        for _ in range(N_AUGMENTED_COPIES):
            aug_present = _augment(present, schema_symptom_cols, rng)
            if not aug_present:
                continue
            aug = _finalize_case(aug_present, feature_columns)
            rows.append(aug); diseases.append(disease); group_ids.append(idx)
            n_augmented += 1

    header = feature_columns + ["triage_category", "disease", "group_id"]
    OUTPUT_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r, d, g in zip(rows, diseases, group_ids):
            writer.writerow(
                [r.get(col, 0) for col in feature_columns] + [r["triage_category"], d, g]
            )

    disease_classes = sorted(set(diseases))
    DISEASE_CLASSES_FILE.write_text(json.dumps(disease_classes, indent=2))

    triage_counts = Counter(r["triage_category"] for r in rows)
    disease_counts = Counter(diseases)
    report = {
        "source": str(DATASET_CSV.relative_to(BASE_DIR)),
        "top_n_diseases": TOP_N_DISEASES,
        "rows_per_disease_cap": ROWS_PER_DISEASE,
        "n_rows": len(rows),
        "n_groups": len(set(group_ids)),
        "n_augmented": n_augmented,
        "n_skipped_empty": n_skipped,
        "n_diseases": len(disease_classes),
        "mapped_columns": sum(1 for v in col_mapping.values() if v),
        "unmapped_columns_dropped": unmapped_cols,
        "triage_distribution": dict(sorted(triage_counts.items())),
        "disease_distribution": dict(disease_counts.most_common()),
    }
    INGEST_REPORT_FILE.write_text(json.dumps(report, indent=2))

    print(
        f"Wrote {len(rows)} rows ({len(set(group_ids))} groups, "
        f"{n_augmented} augmented) to {OUTPUT_FILE}"
    )
    print(f"Diseases: {len(disease_classes)} (top-{TOP_N_DISEASES}); "
          f"mapped cols: {sum(1 for v in col_mapping.values() if v)}/{len(raw_symptom_cols)}")
    print(f"Triage distribution: {dict(sorted(triage_counts.items()))}")
    print(f"Full report: {INGEST_REPORT_FILE}")


if __name__ == "__main__":
    main()
