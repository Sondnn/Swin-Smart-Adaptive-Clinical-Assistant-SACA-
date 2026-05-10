# Build the SACA training dataset from the real-world Kaggle Disease-Symptom dataset (itachi9604/disease-symptom-description-dataset).
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from symptom_mapping import (
    DROPPED_SYMPTOMS,
    KAGGLE_TO_SCHEMA,
    normalize_kaggle_symptom,
)

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
DATASET_CSV = RAW_DIR / "dataset.csv"
SEVERITY_CSV = RAW_DIR / "Symptom-severity.csv"
OUTPUT_DIR = BASE_DIR / "models"
OUTPUT_FILE = OUTPUT_DIR / "training_data.csv"
FEATURE_COLUMNS_FILE = OUTPUT_DIR / "feature_columns.json"
DISEASE_CLASSES_FILE = OUTPUT_DIR / "disease_classes.json"
INGEST_REPORT_FILE = OUTPUT_DIR / "ingest_report.json"

from triage_rules import assign_triage

# Severity weight (1-7 in Kaggle's Symptom-severity.csv) -> mapped 1-5 scale
# the model already trains on. Highest weight in the row drives the case.
SEVERITY_BUCKETS = [
    (1, 1),
    (2, 2),
    (4, 3),
    (5, 4),
    (7, 5),
]


def _bucket_severity(max_weight: int) -> int:
    for ceiling, bucket in SEVERITY_BUCKETS:
        if max_weight <= ceiling:
            return bucket
    return 5


def _normalize_disease(name: str) -> str:
    return " ".join((name or "").split()).strip()


def load_severity_table() -> dict[str, int]:
    df = pd.read_csv(SEVERITY_CSV)
    df["Symptom"] = df["Symptom"].map(normalize_kaggle_symptom)
    return dict(zip(df["Symptom"], df["weight"].astype(int)))


def load_feature_columns() -> list[str]:
    return json.loads(FEATURE_COLUMNS_FILE.read_text())


def main():
    feature_columns = load_feature_columns()
    feature_set = set(feature_columns)
    severity_weights = load_severity_table()

    df = pd.read_csv(DATASET_CSV)

    symptom_cols = [c for c in df.columns if c.startswith("Symptom_")]

    rows: list[dict] = []
    diseases: list[str] = []
    unmapped = Counter()
    dropped = Counter()
    mapped_count = 0

    for _, raw in df.iterrows():
        disease = _normalize_disease(str(raw["Disease"]))

        case = {col: 0 for col in feature_columns}
        # Tri-state demographics & history we cannot derive from Kaggle.
        case["gender"] = 2
        case["age_over_65"] = 2
        case["had_symptoms_before"] = 2
        case["had_contact"] = 2
        case["symptoms_duration"] = 24

        max_weight = 0
        any_symptom_set = False
        for sc in symptom_cols:
            cell = raw[sc]
            if pd.isna(cell):
                continue
            kaggle_name = normalize_kaggle_symptom(str(cell))
            if not kaggle_name:
                continue

            if kaggle_name in DROPPED_SYMPTOMS:
                dropped[kaggle_name] += 1
                continue

            schema_col = KAGGLE_TO_SCHEMA.get(kaggle_name)
            if schema_col is None:
                unmapped[kaggle_name] += 1
                continue
            if schema_col not in feature_set:
                # Mapping target was deleted from the schema — surface loudly.
                raise KeyError(
                    f"Mapping target '{schema_col}' for kaggle symptom "
                    f"'{kaggle_name}' is not in feature_columns.json"
                )

            case[schema_col] = 1
            mapped_count += 1
            any_symptom_set = True
            w = severity_weights.get(kaggle_name, 0)
            if w > max_weight:
                max_weight = w

        if not any_symptom_set:
            # No mappable symptom -> useless training row.
            continue

        case["symptom_severity"] = _bucket_severity(max_weight) if max_weight else 3
        case["symptom__otherwise_well"] = 1 if case["symptom_severity"] <= 2 else 0
        case["triage_category"] = assign_triage(case)

        rows.append(case)
        diseases.append(disease)

    # Write training_data.csv with disease appended at the end.
    header = feature_columns + ["triage_category", "disease"]
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r, d in zip(rows, diseases):
            writer.writerow([r.get(col, 0) for col in feature_columns] + [r["triage_category"], d])

    disease_classes = sorted(set(diseases))
    DISEASE_CLASSES_FILE.write_text(json.dumps(disease_classes, indent=2))

    triage_counts = Counter(r["triage_category"] for r in rows)
    disease_counts = Counter(diseases)
    report = {
        "n_rows": len(rows),
        "n_diseases": len(disease_classes),
        "mapped_symptom_cells": mapped_count,
        "triage_distribution": dict(sorted(triage_counts.items())),
        "disease_distribution": dict(sorted(disease_counts.items())),
        "unmapped_symptoms": dict(unmapped),
        "dropped_symptoms": dict(dropped),
    }
    INGEST_REPORT_FILE.write_text(json.dumps(report, indent=2))

    print(f"Wrote {len(rows)} rows to {OUTPUT_FILE}")
    print(f"Diseases: {len(disease_classes)}")
    print(f"Triage distribution: {dict(sorted(triage_counts.items()))}")
    if unmapped:
        print(f"Unmapped Kaggle symptoms (dropped): {dict(unmapped)}")
    print(f"Full report: {INGEST_REPORT_FILE}")


if __name__ == "__main__":
    main()
