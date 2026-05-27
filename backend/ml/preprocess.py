from __future__ import annotations
import pandas as pd
from typing import Iterable, List, Optional

NON_FEATURE_COLUMNS = {"language", "case_id", "triage_category", "triage_label", "triage_action", "active_symptoms"}


def _normalize_prefixed_names(
        values: Iterable[str],
        prefix: str,
        feature_columns: Iterable[str],
        strict: bool,
) -> List[str]:
    feature_set = set(feature_columns)
    normalized: List[str] = []
    invalid: List[str] = []
    for value in values:
        s = value.strip().lower().replace(" ", "_")
        if not s:
            continue
        candidate = s if s.startswith(prefix) else f"{prefix}{s}"
        if candidate in feature_set:
            normalized.append(candidate)
        else:
            invalid.append(value)
    if invalid and strict:
        valid = sorted(c for c in feature_columns if c.startswith(prefix))
        raise ValueError(
            f"These {prefix.rstrip('_')} values are not part of the trained feature schema: "
            + ", ".join(invalid)
            + "\nTry one of these names instead:\n"
            + ", ".join(valid[:25])
        )
    return normalized


def normalize_symptom_names(symptoms: Iterable[str], feature_columns: Iterable[str]) -> List[str]:
    return _normalize_prefixed_names(symptoms, "symptom__", feature_columns, strict=True)


def make_single_case_dataframe(
        feature_columns: List[str],
        gender: int,
        age_over_65: int,
        symptom_severity: int,
        symptoms_duration: int,
        symptoms: List[str],
        chronic_conditions: Optional[List[str]] = None,
        escalation_triggers: Optional[List[str]] = None,
        had_symptoms_before: int = 0,
        had_contact: int = 0,
) -> pd.DataFrame:
    chronic_conditions = chronic_conditions or []
    escalation_triggers = escalation_triggers or []

    row = {c: 0 for c in feature_columns}
    for base_field, value in {
        "gender": gender,
        "age_over_65": age_over_65,
        "symptom_severity": symptom_severity,
        "symptoms_duration": symptoms_duration,
        "had_symptoms_before": had_symptoms_before,
        "had_contact": had_contact,
    }.items():
        if base_field in row:
            row[base_field] = value

    for symptom in normalize_symptom_names(symptoms, feature_columns):
        row[symptom] = 1

    for ch in _normalize_prefixed_names(chronic_conditions, "chronic__", feature_columns, strict=True):
        row[ch] = 1
    for esc in _normalize_prefixed_names(escalation_triggers, "escalation__", feature_columns, strict=True):
        row[esc] = 1

    return pd.DataFrame([row], columns=feature_columns)
