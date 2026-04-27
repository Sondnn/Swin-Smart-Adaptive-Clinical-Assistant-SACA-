from __future__ import annotations
import pandas as pd
from typing import Iterable, List

NON_FEATURE_COLUMNS = {"case_id", "triage_category", "triage_label", "triage_action", "active_symptoms"}

def load_training_data(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)

def get_feature_columns(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if c not in NON_FEATURE_COLUMNS]

def normalize_symptom_names(symptoms: Iterable[str], feature_columns: Iterable[str]) -> List[str]:
    feature_set = set(feature_columns)
    normalized = []
    invalid = []
    for symptom in symptoms:
        s = symptom.strip().lower()
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
    pregnant: int,
    is_child_under_12: int,
    age_over_65: int,
    duration_hours: int,
    pain_score: int,
    previous_major_condition: int,
    symptoms: list[str],
) -> pd.DataFrame:
    row = {c: 0 for c in feature_columns}
    for base_field, value in {
        "gender": gender,
        "pregnant": pregnant,
        "is_child_under_12": is_child_under_12,
        "age_over_65": age_over_65,
        "duration_hours": duration_hours,
        "pain_score": pain_score,
        "previous_major_condition": previous_major_condition,
    }.items():
        if base_field in row:
            row[base_field] = value

    normalized_symptoms = normalize_symptom_names(symptoms, feature_columns)
    for symptom in normalized_symptoms:
        row[symptom] = 1

    if "symptom__short_symptom_duration" in row:
        row["symptom__short_symptom_duration"] = 1 if duration_hours < 24 else 0
    if "symptom__long_symptom_duration" in row:
        row["symptom__long_symptom_duration"] = 1 if duration_hours > 24 else 0

    return pd.DataFrame([row], columns=feature_columns)
