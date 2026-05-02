# Swin-Smart-Adaptive-Clinical-Assistant-SACA

This repo holds an entire stack
- **backend** - API service, NLP, Machine Learning
- **android** - Android Mobile App *(Android Application that helps patients assess the urgency of their symptoms and returns the triage level and recommendation.)*
- **window** - Window Desktop App *(add your description here)*

## Description

### NLP

### ML

#### How to run

##### Step 1: Generate Training Data (if needed)
``` bash
python3 backend/ml/generate_training_data.py
```
This generates `backend/models/training_data_v1.csv` with 5000 synthetic patient cases.

##### Step 2: Train data
```bash
python3 backend/ml/train.py
```
This will:
- Load the training CSV
- Train a Random Forest and Extra Trees classifier
- Save the best performing model to `backend/models/best_model.joblib`
- Save the feature schema to `backend/models/feature_columns.json`


### Android

### Window

### Backend

#### API Service

```bash
cd backend
python3 -m uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`
Testing in `http://127.0.0.1:8000/docs`

## Repository Layout

## Prerequisite

