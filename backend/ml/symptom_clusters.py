SCENARIOS = [
    # Acute coronary syndrome
    ["symptom__chest_pain", "symptom__radiating_chest_pain", "symptom__cold_sweats",
     "symptom__chest_pressure", "symptom__shortness_of_breath"],
    # Stroke (FAST pattern)
    ["symptom__sudden_weakness", "symptom__facial_droop", "symptom__one_sided_weakness",
     "symptom__difficulty_speaking", "symptom__slurred_speech"],
    # Anaphylaxis
    ["symptom__anaphylaxis", "symptom__tongue_swelling", "symptom__lip_swelling",
     "symptom__breathing_difficulty", "symptom__hives"],
    # Sepsis / severe infection
    ["symptom__high_fever", "symptom__chills", "symptom__confusion",
     "symptom__rapid_breathing", "symptom__fast_heart_rate"],
    # Pulmonary embolism
    ["symptom__shortness_of_breath", "symptom__chest_pain", "symptom__pain_when_breathing",
     "symptom__blood_clot_symptoms", "symptom__calf_pain"],
    # Subarachnoid haemorrhage
    ["symptom__sudden_severe_headache", "symptom__neck_stiffness", "symptom__vomiting",
     "symptom__light_sensitivity"],
    # Common cold (negative case for triage)
    ["symptom__runny_nose", "symptom__sore_throat", "symptom__cough", "symptom__sneezing",
     "symptom__nasal_congestion"],
    # Migraine
    ["symptom__migraine", "symptom__headache", "symptom__nausea", "symptom__light_sensitivity"],
    # Gastro
    ["symptom__vomiting", "symptom__diarrhoea", "symptom__abdominal_pain", "symptom__nausea"],
    # UTI
    ["symptom__painful_urination", "symptom__frequent_urination", "symptom__cloudy_urine",
     "symptom__kidney_pain"],
]
