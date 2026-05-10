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

The `/predict` endpoint returns both a **triage category** (1–5; categories 4 and 6 are absent from the current dataset) from the ensemble triage model and a **disease prediction** (top-1 + top-3 probabilities) from a separate XGBoost classifier. Both models are trained from the real-world Kaggle Disease-Symptom dataset (`itachi9604/disease-symptom-description-dataset`).

##### Prerequisite

The Kaggle CSVs must be present in `backend/data/raw/` (`dataset.csv` and `Symptom-severity.csv`). This is a one-time setup; the pipeline does not redownload them.

##### All-in-one Pipeline

```bash
python3 backend/scripts/run_ml_pipeline.py
```

Flags:
- `--skip-build` — retrain only, reuse existing `training_data.csv`.
- `--skip-train` — ingest only, leave models untouched.

##### Manual stages

Useful when iterating on a single stage.

###### Step 1: Build training data
```bash
cd backend && python3 ml/build_training_data.py
```
Maps Kaggle symptoms onto the existing schema, derives triage labels via the rules in `triage_rules.py`, and writes:
- `backend/models/training_data.csv`
- `backend/models/disease_classes.json`
- `backend/models/ingest_report.json`

###### Step 2: Train both models
```bash
cd backend && python3 ml/train.py
```
Trains:
- Triage ensemble (Random Forest + Extra Trees + XGBoost RandomizedSearchCV → soft VotingClassifier).
- Disease XGBoost classifier on Kaggle disease labels.

Outputs into `backend/models/`: `ensemble.joblib`, `label_encoder.joblib`, `disease_model.joblib`, `disease_label_encoder.joblib`, `feature_columns.json`, `best_model_name.txt`, `ml_metrics.json`.


### Android

### Window

## Repository Layout

## Prerequisite

