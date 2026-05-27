from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Raw datasets (gitignored; auto-downloaded by run_ml_pipeline.py)
DATA_DIR = BASE_DIR / "data"
RAW_TRIAGE_DIR = DATA_DIR / "raw_triage"
RAW_DISEASE_DIR = DATA_DIR / "raw_disease"
RAW_TRIAGE_FILE = RAW_TRIAGE_DIR / "5v_cleandf.rdata"
RAW_DISEASE_FILE = RAW_DISEASE_DIR / "Final_Augmented_dataset_Diseases_and_Symptoms.csv"

# Trained models + intermediate training data
MODEL_DIR = BASE_DIR / "models"
TRIAGE_TRAINING_CSV = MODEL_DIR / "training_data_triage.csv"
DISEASE_TRAINING_CSV = MODEL_DIR / "training_data_disease.csv"
MODEL_FEATURES_FILE = MODEL_DIR / "model_features.json"
DISEASE_CLASSES_FILE = MODEL_DIR / "disease_classes.json"

# Reports
REPORTS_DIR = BASE_DIR / "reports"
TRIAGE_INGEST_REPORT = REPORTS_DIR / "ingest_report_triage.json"
DISEASE_INGEST_REPORT = REPORTS_DIR / "ingest_report_disease.json"
