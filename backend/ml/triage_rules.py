CHRONIC_COLS = [
    "chronic__hypertension",
    "chronic__type2_diabetes",
    "chronic__heart_disease",
    "chronic__asthma_copd",
    "chronic__depression_anxiety",
]

ESCALATION_COLS = [
    "escalation__chest_pain",
    "escalation__breathing_difficulty_at_rest",
    "escalation__sudden_confusion_or_loc",
    "escalation__sudden_weakness_one_side",
    "escalation__severe_allergic_reaction",
]

CAT1_SYMPTOMS = [
    "symptom__chest_pain", "symptom__radiating_chest_pain",
    "symptom__chest_pressure", "symptom__chest_tightness",
    "symptom__breathing_difficulty", "symptom__shortness_of_breath",
    "symptom__stridor", "symptom__choking", "symptom__cyanosis",
    "symptom__trouble_talking",
    "symptom__anaphylaxis", "symptom__facial_swelling",
    "symptom__tongue_swelling", "symptom__lip_swelling", "symptom__swollen_throat",
    "symptom__collapse", "symptom__unconscious", "symptom__altered_consciousness",
    "symptom__cardiac_arrest", "symptom__fainting",
    "symptom__facial_droop", "symptom__facial_or_limb_weakness",
    "symptom__one_sided_weakness", "symptom__sudden_weakness",
    "symptom__slurred_speech", "symptom__stroke", "symptom__paralysis",
    "symptom__extensive_burns",
    "symptom__very_unwell", "symptom__child_not_responding",
]

CAT2_SYMPTOMS = [
    "symptom__seizure",
    "symptom__heavy_bleeding", "symptom__uncontrolled_bleeding",
    "symptom__vomiting_blood", "symptom__coughing_blood",
    "symptom__head_injury", "symptom__head_or_spinal_injury", "symptom__spinal_pain",
    "symptom__snake_bite", "symptom__electric_shock",
    "symptom__heart_palpitations", "symptom__irregular_heartbeat",
    "symptom__fast_heart_rate",
    "symptom__in_labour_or_ruptured_membranes",
    "symptom__neck_stiffness",
    "symptom__sudden_severe_headache", "symptom__sudden_blindness",
    "symptom__blood_clot_symptoms",
]

CAT3_SYMPTOMS = [
    "symptom__unable_to_urinate", "symptom__urinary_retention",
    "symptom__floppy_infant", "symptom__poor_feeding",
    "symptom__poisoning_or_overdose", "symptom__drug_overdose",
    "symptom__eye_injury_or_chemical", "symptom__foreign_body_in_eye",
    "symptom__chemical_burn",
    "symptom__severe_pain", "symptom__severe_abdominal_pain", "symptom__severe_headache",
    "symptom__injured_limb_or_possible_fracture", "symptom__fracture",
    "symptom__dislocation", "symptom__cannot_move_limb",
    "symptom__suicidal_thoughts",
    "symptom__vision_loss",
]

CAT4_SYMPTOMS = [
    "symptom__pregnancy_pain_or_bleeding", "symptom__pregnancy_bleeding",
    "symptom__vaginal_bleeding", "symptom__reduced_foetal_movement",
    "symptom__abuse_or_assault",
    "symptom__visual_disturbance", "symptom__blurred_vision",
    "symptom__double_vision", "symptom__flashing_lights",
    "symptom__extreme_concern",
    "symptom__psychological_distress", "symptom__hallucinations",
    "symptom__paranoia", "symptom__agitation", "symptom__panic_attack",
    "symptom__unable_to_keep_fluids",
]

CAT5_SYMPTOMS = [
    "symptom__severe_rash",
    "symptom__cut_or_laceration", "symptom__deep_cut",
    "symptom__severe_flu_like_symptoms",
    "symptom__post_op_problem", "symptom__infection_after_surgery",
    "symptom__wound_opening",
    "symptom__eye_or_ear_infection_or_pain", "symptom__ear_pain",
    "symptom__eye_pain", "symptom__red_eye", "symptom__eye_discharge",
    "symptom__ear_discharge", "symptom__eye_redness",
    "symptom__dehydration",
    "symptom__infected_wound", "symptom__cellulitis", "symptom__abscess",
    "symptom__dental_abscess", "symptom__skin_infection",
]


FEVER_GI_PAIN_SYMPTOMS = [
    "symptom__fever", "symptom__high_fever",
    "symptom__vomiting", "symptom__continuous_vomiting",
    "symptom__diarrhoea",
    "symptom__abdominal_pain", "symptom__stomach_cramps",
    "symptom__nausea", "symptom__pain",
]

HIGH_ACUITY_THRESHOLD_HOURS = 24

CHRONIC_SENSITIVE_SYMPTOMS = [
    "symptom__fever", "symptom__high_fever",
    "symptom__cough", "symptom__dry_cough", "symptom__productive_cough",
    "symptom__cough_with_phlegm", "symptom__chest_congestion",
    "symptom__flu_like_symptoms", "symptom__severe_flu_like_symptoms",
    "symptom__shortness_of_breath", "symptom__wheezing",
    "symptom__rapid_breathing", "symptom__pain_when_breathing",
    "symptom__chest_tightness",
    "symptom__vomiting", "symptom__continuous_vomiting", "symptom__diarrhoea",
    "symptom__dehydration", "symptom__fatigue", "symptom__weakness",
    "symptom__body_aches", "symptom__dizziness",
]


def _has_chronic_condition(row: dict) -> bool:
    return any(row.get(c, 0) == 1 for c in CHRONIC_COLS)


def assign_triage(row: dict) -> int:
    def has(group) -> bool:
        return any(row.get(s, 0) == 1 for s in group)

    if has(ESCALATION_COLS):
        return 1

    if has(CAT1_SYMPTOMS):
        return 1
    if has(CAT2_SYMPTOMS):
        return 2
    if has(CAT3_SYMPTOMS):
        return 3

    if has(CAT4_SYMPTOMS):
        cat = 4
    elif has(FEVER_GI_PAIN_SYMPTOMS):
        vulnerable = row.get("age_over_65") == 1
        duration_hours = row.get("symptoms_duration", 0) or 0
        cat = 4 if (vulnerable and duration_hours > HIGH_ACUITY_THRESHOLD_HOURS) else 5
    elif has(CAT5_SYMPTOMS):
        cat = 5
    else:
        cat = 6

    # Chronic comorbidity raises urgency for systemic / cardiorespiratory illness.
    if cat >= 4 and _has_chronic_condition(row) and has(CHRONIC_SENSITIVE_SYMPTOMS):
        cat -= 1

    return cat
