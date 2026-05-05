import json
import random
import csv
from collections import Counter
from collections import Counter
from pathlib import Path

from ml.symptom_clusters import SCENARIOS

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BASE_DIR / "models" / "training_data.csv"
OUTPUT_FILE = BASE_DIR / "models" / "training_data.csv"
FEATURE_COLUMNS_FILE = BASE_DIR / "models" / "feature_columns.json"

SEED = 42
N_ROWS = 5000
SCENARIO_PROBABILITY = 0.25

SEED = 42
N_ROWS = 5000
SCENARIO_PROBABILITY = 0.25

feature_columns = json.loads(FEATURE_COLUMNS_FILE.read_text())
HEADER = feature_columns + ["triage_category"]

# Symptoms eligible for random sampling — exclude flag-only fields
SYMPTOM_COLS = [
    c for c in HEADER
    if c.startswith("symptom__") and c != "symptom__otherwise_well"
]


CAT1_SYMPTOMS = [
    "symptom__collapse", "symptom__unconscious", "symptom__altered_consciousness",
    "symptom__cardiac_arrest", "symptom__cyanosis", "symptom__paralysis",
    "symptom__anaphylaxis", "symptom__floppy_infant",
]

CAT2_SYMPTOMS = [
    "symptom__breathing_difficulty", "symptom__stridor", "symptom__choking",
    "symptom__heavy_bleeding", "symptom__uncontrolled_bleeding", "symptom__vomiting_blood",
    "symptom__chest_pain", "symptom__head_or_spinal_injury",
    "symptom__seizure", "symptom__stroke", "symptom__facial_droop", "symptom__sudden_weakness",
    "symptom__pregnancy_pain_or_bleeding", "symptom__reduced_foetal_movement",
    "symptom__in_labour_or_ruptured_membranes", "symptom__drug_overdose",
    "symptom__poisoning_or_overdose", "symptom__snake_bite", "symptom__extensive_burns",
    "symptom__electric_shock", "symptom__suicidal_thoughts",
    "symptom__sudden_severe_headache", "symptom__sudden_blindness",
    "symptom__blood_clot_symptoms", "symptom__radiating_chest_pain",
    "symptom__chest_pressure", "symptom__one_sided_weakness", "symptom__one_sided_numbness",
    "symptom__difficulty_understanding_speech", "symptom__difficulty_speaking",
]

CAT3_SYMPTOMS = [
    "symptom__severe_pain", "symptom__severe_headache", "symptom__severe_abdominal_pain",
    "symptom__severe_rash", "symptom__severe_flu_like_symptoms",
    "symptom__high_fever", "symptom__neck_stiffness",
    "symptom__confusion", "symptom__drowsy", "symptom__vision_loss",
    "symptom__unable_to_urinate", "symptom__urinary_retention",
    "symptom__continuous_vomiting", "symptom__unable_to_keep_fluids",
    "symptom__abuse_or_assault", "symptom__psychological_distress",
    "symptom__post_op_problem",
    "symptom__cellulitis", "symptom__dental_abscess", "symptom__abscess",
    "symptom__petechiae", "symptom__jaundice", "symptom__yellow_skin",
    "symptom__hallucinations", "symptom__paranoia", "symptom__agitation",
    "symptom__pain_when_breathing", "symptom__rapid_breathing",
]

CAT4_SYMPTOMS = [
    "symptom__injured_limb_or_possible_fracture", "symptom__fracture", "symptom__dislocation",
    "symptom__cut_or_laceration", "symptom__deep_cut", "symptom__infected_wound",
    "symptom__eye_injury_or_chemical", "symptom__foreign_body_in_eye",
    "symptom__burn", "symptom__chemical_burn",
    "symptom__abdominal_pain", "symptom__back_pain", "symptom__ear_pain",
    "symptom__testicular_pain", "symptom__pelvic_pain",
    "symptom__panic_attack", "symptom__extreme_concern",
    "symptom__migraine", "symptom__breast_lump", "symptom__breast_pain",
    "symptom__boil", "symptom__pain_during_sex", "symptom__genital_sores",
]

CAT5_SYMPTOMS = [
    "symptom__fever", "symptom__vomiting", "symptom__diarrhoea",
    "symptom__rash", "symptom__headache", "symptom__dizziness",
    "symptom__nausea", "symptom__cough", "symptom__fatigue",
    "symptom__sore_throat", "symptom__ear_discharge", "symptom__eye_discharge",
    "symptom__painful_urination", "symptom__constipation",
    "symptom__muscle_pain", "symptom__joint_pain", "symptom__sprain",
    "symptom__insect_bite", "symptom__wound_redness",
    "symptom__runny_nose", "symptom__blocked_nose", "symptom__nasal_congestion",
    "symptom__sneezing", "symptom__sinus_pain", "symptom__hay_fever",
    "symptom__loss_of_smell", "symptom__loss_of_taste",
    "symptom__dry_cough", "symptom__productive_cough", "symptom__cough_with_phlegm",
    "symptom__heartburn", "symptom__acid_reflux", "symptom__indigestion",
    "symptom__bloating", "symptom__gas", "symptom__belching",
    "symptom__toothache", "symptom__gum_swelling", "symptom__mouth_ulcer",
    "symptom__body_aches", "symptom__night_sweats", "symptom__flu_like_symptoms",
    "symptom__bruising", "symptom__easy_bruising",
    "symptom__tinnitus", "symptom__vertigo",
    "symptom__anxiety", "symptom__depression", "symptom__insomnia",
]


# Drift-prevention: every symptom referenced in the rules must exist in the schema
RULE_SYMPTOMS = (
    set(CAT1_SYMPTOMS) | set(CAT2_SYMPTOMS) | set(CAT3_SYMPTOMS)
    | set(CAT4_SYMPTOMS) | set(CAT5_SYMPTOMS)
    | {"symptom__otherwise_well", "symptom__severe_pain"} 
)
_missing = RULE_SYMPTOMS - set(feature_columns)
if _missing:
    raise ValueError(
        f"Rules reference symptoms not in feature_columns.json: {sorted(_missing)}. "
        "Add them to the schema or remove them from the rules."
    )


def assign_triage(row):
    if any(row.get(s, 0) == 1 for s in CAT1_SYMPTOMS):
        return 1
    if any(row.get(s, 0) == 1 for s in CAT2_SYMPTOMS):
        return 2
    if any(row.get(s, 0) == 1 for s in CAT3_SYMPTOMS) or row.get("symptom_severity", 0) >= 4:
        return 3
    if any(row.get(s, 0) == 1 for s in CAT4_SYMPTOMS):
        return 4
    if any(row.get(s, 0) == 1 for s in CAT5_SYMPTOMS):
        return 5
    return 6


def pick_symptoms():
    # Return a list of symptom column names for one synthetic case.
    if random.random() < SCENARIO_PROBABILITY:
        scenario = random.choice(SCENARIOS)
        chosen = list(scenario)
        if random.random() < 0.4:
            chosen.append(random.choice(SYMPTOM_COLS))
        return chosen

    symptom_count = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
    return random.sample(SYMPTOM_COLS, symptom_count)


def generate_case():
    row = {col: 0 for col in HEADER}

    row["gender"] = random.choice([0, 1])
    row["age_over_65"] = random.choices([0, 1], weights=[85, 15])[0]
    row["symptom_severity"] = random.randint(1, 5)
    row["symptoms_duration"] = random.choice([1, 2, 4, 6, 12, 24, 48, 72])

    for s in pick_symptoms():
        if s in row:
            row[s] = 1

    if row.get("symptom__severe_pain") == 1:
        row["symptom_severity"] = random.choice([4, 5])

    row["symptom__otherwise_well"] = 1 if row["symptom_severity"] <= 2 else 0
    row["triage_category"] = assign_triage(row)
    return row


def main():
    random.seed(SEED)
    rows = [generate_case() for _ in range(N_ROWS)]

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for r in rows:
            writer.writerow([r.get(col, 0) for col in HEADER])

    counts = Counter(r["triage_category"] for r in rows)
    print(f"Generated {len(rows)} rows into {OUTPUT_FILE}")
    print("Label distribution:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
