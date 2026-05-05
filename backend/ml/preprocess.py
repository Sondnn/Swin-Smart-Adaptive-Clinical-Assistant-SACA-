from __future__ import annotations
import pandas as pd
from typing import Iterable, List

NON_FEATURE_COLUMNS = {"language", "case_id", "triage_category", "triage_label", "triage_action", "active_symptoms"}

def normalize_symptom_names(symptoms: Iterable[str], feature_columns: Iterable[str]) -> List[str]:
    feature_set = set(feature_columns)
    normalized = []
    invalid = []
    for symptom in symptoms:
        # Normalize with normal wording symptoms
        s = symptom.strip().lower().replace(" ", "_")
        if not s:
            continue
        candidate = s if s.startswith("symptom__") else f"symptom__{s}"
        if candidate in feature_set:
            normalized.append(candidate)
        else:
            invalid.append(symptom)
    if invalid:
        valid_symptoms = sorted([c for c in feature_columns if c.startswith("symptom__")])
        raise ValueError(
            "These symptoms are not part of the trained feature schema: "
            + ", ".join(invalid)
            + "\nTry one of these names instead:\n"
            + ", ".join(valid_symptoms[:25])
        )
    return normalized

def make_single_case_dataframe(
    feature_columns: list[str],
    gender: int,
    age_over_65: int,
    symptom_severity: int,
    symptoms_duration: int,
    symptoms: list[str],
) -> pd.DataFrame:
    row = {c: 0 for c in feature_columns}
    for base_field, value in {
        "gender": gender,
        "age_over_65": age_over_65,
        "symptom_severity": symptom_severity,
        "symptoms_duration": symptoms_duration,
    }.items():
        if base_field in row:
            row[base_field] = value

    normalized_symptoms = normalize_symptom_names(symptoms, feature_columns)
    for symptom in normalized_symptoms:
        row[symptom] = 1
        
    return pd.DataFrame([row], columns=feature_columns)
