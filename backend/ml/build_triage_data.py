from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import pyreadr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import (
    BASE_DIR,
    MODEL_DIR,
    MODEL_FEATURES_FILE,
    RAW_TRIAGE_FILE,
    REPORTS_DIR,
    TRIAGE_INGEST_REPORT,
    TRIAGE_TRAINING_CSV,
)
from triage_rules import assign_triage

SEED = 42
SAMPLE_ROWS = 120_000
DURATION_BUCKETS = [1, 2, 4, 8, 12, 24, 48, 72, 120]
DURATION_WEIGHTS = [4, 6, 8, 9, 10, 12, 10, 8, 6]
HAD_SYMPTOMS_BEFORE_DIST = {0: 0.65, 1: 0.25, 2: 0.10}
HAD_CONTACT_DIST = {0: 0.75, 1: 0.15, 2: 0.10}

SEVERITY_DIST = {1: 0.20, 2: 0.25, 3: 0.25, 4: 0.18, 5: 0.12}

AUGMENT_PER_SYMPTOM = 60
AUGMENT_COMBO_ROWS = 20_000
AUGMENT_COMBO_MAX_SYMPTOMS = 4
AUGMENT_ESCALATION_PER_TRIGGER = 400


def _sample_choice(rng: random.Random, dist: dict[int, float]) -> int:
    return rng.choices(list(dist), weights=list(dist.values()), k=1)[0]


def _fill_random_context(rng: random.Random, row: dict) -> None:
    row["gender"] = rng.choice([0, 1, 2])
    row["age_over_65"] = rng.choice([0, 1, 2])
    row["symptom_severity"] = _sample_choice(rng, SEVERITY_DIST)
    row["symptoms_duration"] = rng.choices(
        DURATION_BUCKETS, weights=DURATION_WEIGHTS, k=1
    )[0]
    row["had_symptoms_before"] = _sample_choice(rng, HAD_SYMPTOMS_BEFORE_DIST)
    row["had_contact"] = _sample_choice(rng, HAD_CONTACT_DIST)
    for c in row:
        if c.startswith("chronic__"):
            row[c] = 1 if rng.random() < 0.2 else 0
    if "symptom__otherwise_well" in row:
        row["symptom__otherwise_well"] = 1 if row["symptom_severity"] <= 2 else 0


def _augment_symptom_coverage(
    feature_columns: list[str], rng: random.Random, start_group_id: int
) -> list[dict]:
    symptom_cols = [c for c in feature_columns if c.startswith("symptom__")]
    rows: list[dict] = []
    gid = start_group_id

    # Single-symptom rows: guarantee every symptom's isolated POPGUNS mapping.
    for sym in symptom_cols:
        for _ in range(AUGMENT_PER_SYMPTOM):
            row = {c: 0 for c in feature_columns}
            row[sym] = 1
            _fill_random_context(rng, row)
            row["triage_category"] = assign_triage(row)
            row["group_id"] = gid
            gid += 1
            rows.append(row)

    # Multi-symptom rows: teach the model that the most urgent category wins.
    for _ in range(AUGMENT_COMBO_ROWS):
        row = {c: 0 for c in feature_columns}
        k = rng.randint(2, AUGMENT_COMBO_MAX_SYMPTOMS)
        for sym in rng.sample(symptom_cols, k):
            row[sym] = 1
        _fill_random_context(rng, row)
        row["triage_category"] = assign_triage(row)
        row["group_id"] = gid
        gid += 1
        rows.append(row)

    escalation_cols = [c for c in feature_columns if c.startswith("escalation__")]
    for esc in escalation_cols:
        for _ in range(AUGMENT_ESCALATION_PER_TRIGGER):
            row = {c: 0 for c in feature_columns}
            row[esc] = 1
            for sym in rng.sample(symptom_cols, rng.randint(0, 3)):
                row[sym] = 1
            _fill_random_context(rng, row)
            row["triage_category"] = assign_triage(row)
            row["group_id"] = gid
            gid += 1
            rows.append(row)

    return rows

CC_TO_SYMPTOMS: dict[str, list[str]] = {
    "cc_abdominalcramping": ["symptom__abdominal_pain", "symptom__stomach_cramps"],
    "cc_abdominaldistention": ["symptom__abdominal_swelling", "symptom__bloating"],
    "cc_abdominalpain": ["symptom__abdominal_pain"],
    "cc_abdominalpainpregnant": ["symptom__pregnancy_pain_or_bleeding"],
    "cc_abnormallab": [],
    "cc_abscess": ["symptom__abscess"],
    "cc_addictionproblem": [],
    "cc_agitation": ["symptom__agitation"],
    "cc_alcoholintoxication": ["symptom__alcohol_intoxication"],
    "cc_alcoholproblem": ["symptom__alcohol_intoxication"],
    "cc_allergicreaction": ["symptom__allergic_reaction"],
    "cc_alteredmentalstatus": ["symptom__altered_consciousness", "symptom__confusion"],
    "cc_animalbite": ["symptom__animal_bite"],
    "cc_ankleinjury": ["symptom__sprain"],
    "cc_anklepain": ["symptom__joint_pain"],
    "cc_anxiety": ["symptom__anxiety"],
    "cc_arminjury": ["symptom__injured_limb_or_possible_fracture"],
    "cc_armpain": ["symptom_c_arm_pain"],
    "cc_armswelling": ["symptom__swelling"],
    "cc_assaultvictim": ["symptom__abuse_or_assault"],
    "cc_asthma": ["symptom__wheezing", "symptom__breathing_difficulty"],
    "cc_backpain": ["symptom__back_pain"],
    "cc_bleeding/bruising": ["symptom__bruising", "symptom__easy_bruising"],
    "cc_blurredvision": ["symptom__blurred_vision"],
    "cc_bodyfluidexposure": [],
    "cc_breastpain": ["symptom__breast_pain"],
    "cc_breathingdifficulty": ["symptom__breathing_difficulty"],
    "cc_breathingproblem": ["symptom__breathing_difficulty"],
    "cc_burn": ["symptom__burn"],
    "cc_cardiacarrest": ["symptom__cardiac_arrest"],
    "cc_cellulitis": ["symptom__cellulitis"],
    "cc_chestpain": ["symptom__chest_pain"],
    "cc_chesttightness": ["symptom__chest_tightness"],
    "cc_chills": ["symptom__chills"],
    "cc_coldlikesymptoms": ["symptom__flu_like_symptoms"],
    "cc_confusion": ["symptom__confusion"],
    "cc_conjunctivitis": ["symptom__red_eye", "symptom__eye_discharge"],
    "cc_constipation": ["symptom__constipation"],
    "cc_cough": ["symptom__cough"],
    "cc_cyst": ["symptom__abscess"],
    "cc_decreasedbloodsugar-symptomatic": ["symptom__weakness", "symptom__dizziness"],
    "cc_dehydration": ["symptom__dehydration"],
    "cc_dentalpain": ["symptom__toothache"],
    "cc_depression": ["symptom__depression"],
    "cc_detoxevaluation": [],
    "cc_diarrhea": ["symptom__diarrhoea"],
    "cc_dizziness": ["symptom__dizziness"],
    "cc_drug/alcoholassessment": [],
    "cc_drugproblem": [],
    "cc_dyspnea": ["symptom__shortness_of_breath"],
    "cc_dysuria": ["symptom__painful_urination"],
    "cc_earpain": ["symptom__ear_pain"],
    "cc_earproblem": ["symptom__ear_discharge"],
    "cc_edema": ["symptom__swelling"],
    "cc_elbowpain": ["symptom__joint_pain"],
    "cc_elevatedbloodsugar-nosymptoms": [],
    "cc_elevatedbloodsugar-symptomatic": ["symptom__excessive_thirst", "symptom__frequent_urination"],
    "cc_emesis": ["symptom__vomiting"],
    "cc_epigastricpain": ["symptom__abdominal_pain", "symptom__heartburn"],
    "cc_epistaxis": ["symptom__nosebleed"],
    "cc_exposuretostd": [],
    "cc_extremitylaceration": ["symptom__cut_or_laceration"],
    "cc_extremityweakness": ["symptom__sudden_weakness"],
    "cc_eyeinjury": ["symptom__eye_injury_or_chemical"],
    "cc_eyepain": ["symptom__eye_pain"],
    "cc_eyeproblem": ["symptom__eye_or_ear_infection_or_pain"],
    "cc_eyeredness": ["symptom__red_eye"],
    "cc_facialinjury": ["symptom__head_injury"],
    "cc_faciallaceration": ["symptom__cut_or_laceration"],
    "cc_facialpain": ["symptom__facial_pain"],
    "cc_facialswelling": ["symptom__facial_swelling"],
    "cc_fall": ["symptom__head_injury"],
    "cc_fall>65": ["symptom__head_injury"],
    "cc_fatigue": ["symptom__fatigue"],
    "cc_femaleguproblem": ["symptom__vaginal_discharge"],
    "cc_fever": ["symptom__fever"],
    "cc_fever-75yearsorolder": ["symptom__fever", "symptom__high_fever"],
    "cc_fever-9weeksto74years": ["symptom__fever"],
    "cc_feverimmunocompromised": ["symptom__fever", "symptom__high_fever"],
    "cc_fingerinjury": ["symptom__injured_limb_or_possible_fracture"],
    "cc_fingerpain": ["symptom__pain"],
    "cc_fingerswelling": ["symptom__swelling"],
    "cc_flankpain": ["symptom__flank_pain"],
    "cc_follow-upcellulitis": ["symptom__cellulitis"],
    "cc_footinjury": ["symptom__injured_limb_or_possible_fracture"],
    "cc_footpain": ["symptom__pain"],
    "cc_footswelling": ["symptom__swelling"],
    "cc_foreignbodyineye": ["symptom__foreign_body_in_eye"],
    "cc_fulltrauma": ["symptom__head_or_spinal_injury"],
    "cc_generalizedbodyaches": ["symptom__body_aches"],
    "cc_gibleeding": ["symptom__blood_in_stool"],
    "cc_giproblem": ["symptom__abdominal_pain"],
    "cc_groinpain": ["symptom__pelvic_pain"],
    "cc_hallucinations": ["symptom__hallucinations"],
    "cc_handinjury": ["symptom__injured_limb_or_possible_fracture"],
    "cc_handpain": ["symptom__pain"],
    "cc_headache": ["symptom__headache"],
    "cc_headache-newonsetornewsymptoms": ["symptom__headache", "symptom__sudden_severe_headache"],
    "cc_headache-recurrentorknowndxmigraines": ["symptom__migraine"],
    "cc_headachere-evaluation": ["symptom__headache"],
    "cc_headinjury": ["symptom__head_injury"],
    "cc_headlaceration": ["symptom__cut_or_laceration", "symptom__head_injury"],
    "cc_hematuria": ["symptom__blood_in_urine"],
    "cc_hemoptysis": ["symptom__coughing_blood"],
    "cc_hippain": ["symptom__hip_pain"],
    "cc_homicidal": ["symptom__psychological_distress"],
    "cc_hyperglycemia": ["symptom__excessive_thirst"],
    "cc_hypertension": ["symptom__high_blood_pressure"],
    "cc_hypotension": ["symptom__low_blood_pressure"],
    "cc_influenza": ["symptom__flu_like_symptoms"],
    "cc_ingestion": ["symptom__poisoning_or_overdose"],
    "cc_insectbite": ["symptom__insect_bite"],
    "cc_irregularheartbeat": ["symptom__irregular_heartbeat"],
    "cc_jawpain": ["symptom__jaw_pain"],
    "cc_jointswelling": ["symptom__swollen_joint"],
    "cc_kneeinjury": ["symptom__sprain"],
    "cc_kneepain": ["symptom__knee_pain"],
    "cc_laceration": ["symptom__cut_or_laceration"],
    "cc_leginjury": ["symptom__injured_limb_or_possible_fracture"],
    "cc_legpain": ["symptom__leg_pain"],
    "cc_legswelling": ["symptom__leg_swelling"],
    "cc_lethargy": ["symptom__fatigue", "symptom__drowsy"],
    "cc_lossofconsciousness": ["symptom__unconscious", "symptom__fainting"],
    "cc_maleguproblem": [],
    "cc_mass": [],
    "cc_medicalproblem": [],
    "cc_medicalscreening": [],
    "cc_medicationproblem": [],
    "cc_medicationrefill": [],
    "cc_migraine": ["symptom__migraine"],
    "cc_modifiedtrauma": ["symptom__head_or_spinal_injury"],
    "cc_motorcyclecrash": ["symptom__head_or_spinal_injury"],
    "cc_motorvehiclecrash": ["symptom__head_or_spinal_injury"],
    "cc_multiplefalls": ["symptom__head_injury"],
    "cc_nasalcongestion": ["symptom__nasal_congestion"],
    "cc_nausea": ["symptom__nausea"],
    "cc_nearsyncope": ["symptom__fainting", "symptom__dizziness"],
    "cc_neckpain": ["symptom__neck_pain"],
    "cc_neurologicproblem": ["symptom__numbness"],
    "cc_numbness": ["symptom__numbness"],
    "cc_oralswelling": ["symptom__lip_swelling", "symptom__tongue_swelling"],
    "cc_otalgia": ["symptom__ear_pain"],
    "cc_other": [],
    "cc_overdose-accidental": ["symptom__drug_overdose", "symptom__poisoning_or_overdose"],
    "cc_overdose-intentional": ["symptom__drug_overdose", "symptom__suicidal_thoughts"],
    "cc_pain": ["symptom__pain"],
    "cc_palpitations": ["symptom__heart_palpitations"],
    "cc_panicattack": ["symptom__panic_attack"],
    "cc_pelvicpain": ["symptom__pelvic_pain"],
    "cc_poisoning": ["symptom__poisoning_or_overdose"],
    "cc_post-opproblem": ["symptom__post_op_problem"],
    "cc_psychiatricevaluation": ["symptom__psychological_distress"],
    "cc_psychoticsymptoms": ["symptom__hallucinations", "symptom__paranoia"],
    "cc_rapidheartrate": ["symptom__fast_heart_rate"],
    "cc_rash": ["symptom__rash"],
    "cc_rectalbleeding": ["symptom__blood_in_stool"],
    "cc_rectalpain": ["symptom__pain"],
    "cc_respiratorydistress": ["symptom__breathing_difficulty", "symptom__rapid_breathing"],
    "cc_ribinjury": ["symptom__pain_when_breathing"],
    "cc_ribpain": ["symptom__pain_when_breathing"],
    "cc_seizure-newonset": ["symptom__seizure"],
    "cc_seizure-priorhxof": ["symptom__seizure"],
    "cc_seizures": ["symptom__seizure"],
    "cc_shortnessofbreath": ["symptom__shortness_of_breath"],
    "cc_shoulderinjury": ["symptom__shoulder_pain"],
    "cc_shoulderpain": ["symptom__shoulder_pain"],
    "cc_sicklecellpain": ["symptom__severe_pain"],
    "cc_sinusproblem": ["symptom__sinus_pain"],
    "cc_skinirritation": ["symptom__itching", "symptom__rash"],
    "cc_skinproblem": ["symptom__rash"],
    "cc_sorethroat": ["symptom__sore_throat"],
    "cc_stdcheck": [],
    "cc_strokealert": ["symptom__stroke"],
    "cc_suicidal": ["symptom__suicidal_thoughts"],
    "cc_suture/stapleremoval": [],
    "cc_swallowedforeignbody": ["symptom__difficulty_swallowing"],
    "cc_syncope": ["symptom__fainting"],
    "cc_tachycardia": ["symptom__fast_heart_rate"],
    "cc_testiclepain": ["symptom__testicular_pain"],
    "cc_thumbinjury": ["symptom__injured_limb_or_possible_fracture"],
    "cc_tickremoval": ["symptom__insect_bite"],
    "cc_toeinjury": ["symptom__injured_limb_or_possible_fracture"],
    "cc_toepain": ["symptom__pain"],
    "cc_trauma": ["symptom__head_or_spinal_injury"],
    "cc_unresponsive": ["symptom__unconscious", "symptom__altered_consciousness"],
    "cc_uri": ["symptom__flu_like_symptoms", "symptom__cough"],
    "cc_urinaryfrequency": ["symptom__frequent_urination"],
    "cc_urinaryretention": ["symptom__urinary_retention"],
    "cc_urinarytractinfection": ["symptom__painful_urination"],
    "cc_vaginalbleeding": ["symptom__vaginal_bleeding"],
    "cc_vaginaldischarge": ["symptom__vaginal_discharge"],
    "cc_vaginalpain": ["symptom__pelvic_pain"],
    "cc_weakness": ["symptom__weakness"],
    "cc_wheezing": ["symptom__wheezing"],
    "cc_withdrawal-alcohol": ["symptom__agitation"],
    "cc_woundcheck": ["symptom__infected_wound"],
    "cc_woundinfection": ["symptom__infected_wound"],
    "cc_woundre-evaluation": ["symptom__infected_wound"],
    "cc_wristinjury": ["symptom__injured_limb_or_possible_fracture"],
    "cc_wristpain": ["symptom__pain"],
}


def _gender_code(value) -> int:
    if isinstance(value, str):
        v = value.strip().lower()
        if v == "male":
            return 1
        if v == "female":
            return 0
    return 2


def _age_over_65(value) -> int:
    try:
        age = int(value)
    except (TypeError, ValueError):
        return 2
    return 1 if age >= 65 else 0


def _stratified_slice(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    counts = df["esi"].value_counts()
    total = counts.sum()
    parts = []
    for label, c in counts.items():
        take = min(c, max(1, round(n * c / total)))
        parts.append(
            df[df["esi"] == label].sample(n=take, random_state=seed)
        )
    out = pd.concat(parts).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return out


def main():
    feature_columns: list[str] = json.loads(MODEL_FEATURES_FILE.read_text())
    feature_set = set(feature_columns)

    print(f"Loading {RAW_TRIAGE_FILE.name}...")
    df = next(iter(pyreadr.read_r(str(RAW_TRIAGE_FILE)).values()))

    df = df[df["esi"].notna()].copy()
    df["esi"] = df["esi"].astype(str).str.strip().astype(int)
    df = df[df["esi"].between(1, 5)].reset_index(drop=True)
    full_dist = {int(k): int(v) for k, v in df["esi"].value_counts().sort_index().items()}
    print(f"ESI rows after filter: {len(df):,}")
    for k, v in full_dist.items():
        print(f"  ESI {k}: {v:>8,}")

    df = _stratified_slice(df, SAMPLE_ROWS, SEED)
    slice_dist = {int(k): int(v) for k, v in df["esi"].value_counts().sort_index().items()}
    print(f"Stratified slice: {len(df):,} rows")
    for k, v in slice_dist.items():
        print(f"  ESI {k}: {v:>8,}")

    cc_present_cols = [c for c in CC_TO_SYMPTOMS if c in df.columns]
    dropped_cc = sorted(set(CC_TO_SYMPTOMS) - set(cc_present_cols))
    cc_map: dict[str, list[str]] = {}
    unknown_targets: list[str] = []
    for cc in cc_present_cols:
        targets = [s for s in CC_TO_SYMPTOMS[cc] if s in feature_set]
        cc_map[cc] = targets
        unknown_targets.extend(s for s in CC_TO_SYMPTOMS[cc] if s not in feature_set)

    chronic_sources = {
        "chronic__asthma_copd": [c for c in ("asthma", "copd") if c in df.columns],
        "chronic__heart_disease": [c for c in ("othheartdx",) if c in df.columns],
        "chronic__depression_anxiety": [c for c in ("anxietydisorders",) if c in df.columns],
    }

    rng = random.Random(SEED)
    rows: list[dict] = []
    triage_counts: Counter[int] = Counter()
    n_no_symptom = 0

    cc_arr = {cc: df[cc].to_numpy() for cc in cc_present_cols}
    chronic_arr = {
        k: [df[col].to_numpy() for col in cols] for k, cols in chronic_sources.items()
    }
    age_arr = df["age"].to_numpy()
    gender_arr = df["gender"].astype(object).to_numpy()

    for i in range(len(df)):
        present: set[str] = set()
        for cc in cc_present_cols:
            v = cc_arr[cc][i]
            if v is None:
                continue
            try:
                if int(v) == 1:
                    present.update(cc_map[cc])
            except (TypeError, ValueError):
                continue

        row = {c: 0 for c in feature_columns}
        for s in present:
            row[s] = 1

        for chronic_col, sources in chronic_arr.items():
            if chronic_col not in row:
                continue
            row[chronic_col] = 1 if any(int(s[i] or 0) == 1 for s in sources) else 0

        row["gender"] = _gender_code(gender_arr[i])
        row["age_over_65"] = _age_over_65(age_arr[i])
        row["symptom_severity"] = _sample_choice(rng, SEVERITY_DIST)
        row["symptoms_duration"] = rng.choices(
            DURATION_BUCKETS, weights=DURATION_WEIGHTS, k=1
        )[0]
        row["had_symptoms_before"] = _sample_choice(rng, HAD_SYMPTOMS_BEFORE_DIST)
        row["had_contact"] = _sample_choice(rng, HAD_CONTACT_DIST)
        if "symptom__otherwise_well" in row:
            row["symptom__otherwise_well"] = 1 if row["symptom_severity"] <= 2 else 0

        # POPGUNS category derived from the row's symptom presentation,
        # duration and age (not the source ESI acuity).
        triage = assign_triage(row)
        row["triage_category"] = triage
        row["group_id"] = i
        rows.append(row)
        triage_counts[triage] += 1
        if not present:
            n_no_symptom += 1

    aug_rows = _augment_symptom_coverage(feature_columns, rng, start_group_id=len(df))
    for r in aug_rows:
        triage_counts[r["triage_category"]] += 1
    rows.extend(aug_rows)
    print(f"Augmentation rows added for symptom coverage: {len(aug_rows):,}")

    MODEL_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    out_cols = feature_columns + ["triage_category", "group_id"]
    pd.DataFrame(rows, columns=out_cols).to_csv(TRIAGE_TRAINING_CSV, index=False)

    report = {
        "source": str(RAW_TRIAGE_FILE.relative_to(BASE_DIR)),
        "label_column": "triage_category (POPGUNS, derived via assign_triage)",
        "sample_rows_target": SAMPLE_ROWS,
        "n_rows": len(rows),
        "n_rows_augmented_for_coverage": len(aug_rows),
        "n_rows_without_mapped_symptom": n_no_symptom,
        "n_cc_columns_used": len(cc_present_cols),
        "n_cc_columns_dropped_missing_in_source": len(dropped_cc),
        "n_cc_targets_dropped_missing_in_schema": len(set(unknown_targets)),
        "triage_distribution": dict(sorted(triage_counts.items())),
    }
    TRIAGE_INGEST_REPORT.write_text(json.dumps(report, indent=2))

    print(
        f"cc_* columns used: {len(cc_present_cols)} "
        f"(missing in source: {len(dropped_cc)}, "
        f"targets outside schema: {len(set(unknown_targets))})"
    )
    print(f"Rows with no mapped symptom: {n_no_symptom:,}")
    print(f"Wrote {len(rows):,} rows -> {TRIAGE_TRAINING_CSV.relative_to(BASE_DIR)}")
    print(f"Report -> {TRIAGE_INGEST_REPORT.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
