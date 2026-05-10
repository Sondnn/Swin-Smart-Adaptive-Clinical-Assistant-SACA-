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

ESCALATION_SYMPTOM_MAP = {
    "escalation__chest_pain": "symptom__chest_pain",
    "escalation__breathing_difficulty_at_rest": "symptom__breathing_difficulty",
    "escalation__sudden_confusion_or_loc": "symptom__altered_consciousness",
    "escalation__sudden_weakness_one_side": "symptom__one_sided_weakness",
    "escalation__severe_allergic_reaction": "symptom__anaphylaxis",
}

ESCALATION_FORCE_CAT1 = {
    "escalation__severe_allergic_reaction",
    "escalation__sudden_confusion_or_loc",
}
ESCALATION_FORCE_CAT2 = {
    "escalation__chest_pain",
    "escalation__breathing_difficulty_at_rest",
    "escalation__sudden_weakness_one_side",
}

CARDIO_RESP_SYMPTOMS = {
    "symptom__chest_pain", "symptom__breathing_difficulty",
    "symptom__radiating_chest_pain", "symptom__rapid_breathing",
    "symptom__pain_when_breathing", "symptom__chest_pressure",
}

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


def assign_triage(row: dict) -> int:
    if any(row.get(s, 0) == 1 for s in ESCALATION_FORCE_CAT1):
        return 1
    if any(row.get(s, 0) == 1 for s in CAT1_SYMPTOMS):
        return 1
    if any(row.get(s, 0) == 1 for s in ESCALATION_FORCE_CAT2):
        return 2
    if any(row.get(s, 0) == 1 for s in CAT2_SYMPTOMS):
        return 2

    if any(row.get(s, 0) == 1 for s in CAT3_SYMPTOMS) or row.get("symptom_severity", 0) >= 4:
        cat = 3
    elif any(row.get(s, 0) == 1 for s in CAT4_SYMPTOMS):
        cat = 4
    elif any(row.get(s, 0) == 1 for s in CAT5_SYMPTOMS):
        cat = 5
    else:
        cat = 6

    cardio_chronic = (row.get("chronic__heart_disease") == 1 or row.get("chronic__asthma_copd") == 1)
    has_cardio_resp_symptom = any(row.get(s, 0) == 1 for s in CARDIO_RESP_SYMPTOMS)
    if cardio_chronic and has_cardio_resp_symptom and cat >= 3:
        cat = max(cat - 1, 2)

    if row.get("had_symptoms_before") == 1 and cat in (4, 5):
        cat = min(cat + 1, 6)

    return cat
