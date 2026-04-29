import json
import random
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BASE_DIR / "models" / "training_data_v1.csv"
FEATURE_COLUMNS_FILE = BASE_DIR / "models" / "feature_columns.json"

feature_columns = json.loads(FEATURE_COLUMNS_FILE.read_text())
HEADER = feature_columns + ["triage_category"]

SYMPTOM_COLS = [c for c in HEADER if c.startswith("symptom__") and "duration" not in c and c != "symptom__otherwise_well"]


def assign_triage(row):
    # Category 1 - Immediate
    if any(row.get(s, 0) == 1 for s in [
        "symptom__collapse", "symptom__unconscious", "symptom__altered_consciousness",
        "symptom__cardiac_arrest", "symptom__cyanosis", "symptom__paralysis",
        "symptom__anaphylaxis", "symptom__floppy_infant", "symptom__child_not_responding"
    ]):
        return 1

    # Category 2 - Emergency
    if any(row.get(s, 0) == 1 for s in [
        "symptom__breathing_difficulty", "symptom__stridor", "symptom__choking",
        "symptom__heavy_bleeding", "symptom__uncontrolled_bleeding", "symptom__vomiting_blood",
        "symptom__chest_pain", "symptom__head_or_spinal_injury", "symptom__paralysis",
        "symptom__seizure", "symptom__stroke", "symptom__facial_droop", "symptom__sudden_weakness",
        "symptom__pregnancy_pain_or_bleeding", "symptom__reduced_foetal_movement",
        "symptom__in_labour_or_ruptured_membranes", "symptom__drug_overdose",
        "symptom__poisoning_or_overdose", "symptom__snake_bite", "symptom__extensive_burns",
        "symptom__electric_shock", "symptom__suicidal_thoughts"
    ]):
        return 2

    # Category 3 - Urgent
    if any(row.get(s, 0) == 1 for s in [
        "symptom__severe_pain", "symptom__severe_headache", "symptom__severe_abdominal_pain",
        "symptom__severe_rash", "symptom__severe_flu_like_symptoms",
        "symptom__high_fever", "symptom__neck_stiffness",
        "symptom__confusion", "symptom__drowsy", "symptom__vision_loss",
        "symptom__unable_to_urinate", "symptom__urinary_retention",
        "symptom__continuous_vomiting", "symptom__unable_to_keep_fluids",
        "symptom__abuse_or_assault", "symptom__psychological_distress",
        "symptom__post_op_problem"
    ]) or row.get("symptom_severity", 0) >= 4:
        return 3

    # Category 4 - Semi-Urgent
    if any(row.get(s, 0) == 1 for s in [
        "symptom__injured_limb_or_possible_fracture", "symptom__fracture", "symptom__dislocation",
        "symptom__cut_or_laceration", "symptom__deep_cut", "symptom__infected_wound",
        "symptom__eye_injury_or_chemical", "symptom__foreign_body_in_eye",
        "symptom__burn", "symptom__chemical_burn",
        "symptom__abdominal_pain", "symptom__back_pain", "symptom__ear_pain",
        "symptom__testicular_pain", "symptom__pelvic_pain",
        "symptom__panic_attack", "symptom__extreme_concern"
    ]):
        return 4

    # Category 5 - Non-Urgent
    if any(row.get(s, 0) == 1 for s in [
        "symptom__fever", "symptom__vomiting", "symptom__diarrhoea",
        "symptom__rash", "symptom__headache", "symptom__dizziness",
        "symptom__nausea", "symptom__cough", "symptom__fatigue",
        "symptom__sore_throat", "symptom__ear_discharge", "symptom__eye_discharge",
        "symptom__painful_urination", "symptom__constipation",
        "symptom__muscle_pain", "symptom__joint_pain", "symptom__sprain",
        "symptom__insect_bite", "symptom__wound_redness"
    ]):
        return 5

    return 6


def generate_case():
    row = {col: 0 for col in HEADER}

    row["gender"] = random.choice([0, 1])
    row["age_over_65"] = random.choices([0, 1], weights=[85, 15])[0]
    row["symptom_severity"] = random.randint(1, 5)
    row["symptoms_duration"] = random.choice([1, 2, 4, 6, 12, 24, 48, 72])

    row["symptom__short_symptom_duration"] = 1 if row["symptoms_duration"] < 24 else 0
    row["symptom__long_symptom_duration"] = 1 if row["symptoms_duration"] >= 24 else 0

    # bias toward critical symptoms occasionally
    symptom_count = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
    chosen = random.sample(SYMPTOM_COLS, symptom_count)
    for s in chosen:
        row[s] = 1

    if row["symptom__severe_pain"] == 1:
        row["symptom_severity"] = random.choice([4, 5])

    row["symptom__otherwise_well"] = 1 if row["symptom_severity"] <= 2 else 0
    row["triage_category"] = assign_triage(row)
    return row


def main():
    rows = [generate_case() for _ in range(5000)]

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)

        for r in rows:
            writer.writerow([r.get(col, 0) for col in HEADER])

    print(f"Generated {len(rows)} rows into {OUTPUT_FILE}")


if __name__ == "__main__":
    main()