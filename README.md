# Swin-Smart-Adaptive-Clinical-Assistant-SACA

This repo holds an entire stack
- **backend** - API service, NLP, Machine Learning
- **android** - Android Mobile App *(Android Application that helps patients assess the urgency of their symptoms and returns the triage level and recommendation.)*
- **window** - Window Desktop App *(add your description here)*

## Description

### Backend

#### API Service

```bash
cd backend && python3 -m uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`
Testing in `http://127.0.0.1:8000/docs`

#### NLP

#### ML

The `/predict` endpoint returns two things:

* A **triage category** (ESI 1–5) trained on the Kaggle hospital triage dataset [`maalona/hospital-triage-and-patient-history-data`](https://www.kaggle.com/datasets/maalona/hospital-triage-and-patient-history-data) (~560k ED visits, nurse-assigned ESI labels). Only API-compatible features are used (symptoms, age, gender, severity, duration, chronic flags).
* A **disease prediction** (top-1 + top-5 probabilities) trained on [`dhivyeshrk/diseases-and-symptoms-dataset`](https://www.kaggle.com/datasets/dhivyeshrk/diseases-and-symptoms-dataset), with temperature-scaled probabilities.

##### Prerequisite

Both raw datasets must be present:
* `backend/data/raw_triage/5v_cleandf.rdata`
* `backend/data/raw_disease/Final_Augmented_dataset_Diseases_and_Symptoms.csv`

The pipeline auto-downloads them from Kaggle on first run if `kaggle` CLI is configured (`~/.kaggle/kaggle.json`).

##### All-in-one Pipeline

```bash
python3 backend/scripts/run_ml_pipeline.py
```

Flags:
- `--skip-build` — retrain only, reuse existing `training_data_triage.csv` and `training_data_disease.csv`.
- `--skip-train` — ingest only, leave models untouched.

##### Manual stages

Useful when repeating on a single stage.

###### Step 1: Build training data

Two ingest scripts, one per dataset:
```bash
cd backend && python3 ml/build_triage_data.py
cd backend && python3 ml/build_disease_data.py
```
The first loads the `.rdata` via `pyreadr`, takes a stratified 50k slice by ESI, and projects `cc_*` onto the `symptom__` schema. The second mirrors the previous behavior on the disease-symptom CSV (top-150 diseases, light row-level augmentation).

Outputs:
- `backend/models/`: `training_data_triage.csv`, `training_data_disease.csv`, `disease_classes.json`, `model_features.json`
- `backend/reports/`: `ingest_report_triage.json`, `ingest_report_disease.json`

###### Step 2: Train both models
```bash
cd backend && python3 -m ml.train
```
Trains the triage XGBoost classifier and the disease XGBoost classifier with temperature scaling, each via group-aware RandomizedSearchCV (3-fold). Outputs:
- `backend/models/`: `triage_model.joblib`, `triage_label_encoder.joblib`, `model_features.json`, `disease_model.joblib`, `disease_label_encoder.joblib`, `disease_temperature.json`.
- `backend/reports/`: `training_metrics.json`.


### Android

### Window

## Repository Layout

## Prerequisite

