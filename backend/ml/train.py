import json
import datetime
import time
import pandas as pd
from pathlib import Path
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split, RandomizedSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, VotingClassifier
from xgboost import XGBClassifier


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "models" / "training_data.csv"
MODELS_DIR = BASE_DIR / "models"


def main():
    MODELS_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    if "triage_category" not in df.columns:
        raise ValueError("Dataset must contain 'triage_category' column")
    has_disease = "disease" in df.columns

    # Stratified 5-fold CV needs at least 5 samples per class. Drop ultra-rare
    # triage categories so training is well-defined.
    triage_counts = df["triage_category"].value_counts()
    rare = triage_counts[triage_counts < 10].index.tolist()
    if rare:
        print(f"Dropping rare triage categories with <10 rows: {rare}")
        df = df[~df["triage_category"].isin(rare)].reset_index(drop=True)

    y = df["triage_category"]
    drop_cols = ["triage_category"] + (["disease"] if has_disease else [])
    X = df.drop(columns=drop_cols)
    disease_y_raw = df["disease"] if has_disease else None

    feature_columns = list(X.columns)

    # Encode the target variable so XGBoost (which requires 0-indexed labels) is happy.
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    
    # 80/20 outer split
    X_dev, X_test, y_dev, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    
    # Inside the 80%, use StratifiedKFold(5) to hyperparam search and ensemble eval.
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Timer
    train_time_start = time.perf_counter()
    
    # Algorithm 1: Random Forest
    rf = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced"
    )
    rf.fit(X_dev, y_dev)
    rf_pred = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    rf_time = time.perf_counter() - train_time_start

    print("\n=== Random Forest Results ===")
    print("Accuracy:", rf_acc)
    print(classification_report(y_test, rf_pred))

    # Algorithm 2: Extra Trees
    et = ExtraTreesClassifier(
        n_estimators=500,
        random_state=42,
        class_weight="balanced"
    )
    et.fit(X_dev, y_dev)
    et_pred = et.predict(X_test)
    et_acc = accuracy_score(y_test, et_pred)
    et_time = time.perf_counter() - train_time_start - rf_time

    print("\n=== Extra Trees Results ===")
    print("Accuracy:", et_acc)
    print(classification_report(y_test, et_pred))
    
    # Algorithm 3: XGBoost
    xgb = XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
    )
    
    xgb_search_space = {
        "n_estimators": [200, 300, 400, 600, 800],
        "max_depth": [4, 6, 8, 10],
        "learning_rate": [0.03, 0.05, 0.1, 0.15],
        "subsample": [0.7, 0.85, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
        "min_child_weight": [1, 3, 5],
    }
    
    xgb_search = RandomizedSearchCV(
        estimator=xgb,
        param_distributions=xgb_search_space,
        n_iter=30,
        scoring="f1_macro",
        cv=cv,
        random_state=42,
        n_jobs=-1,
        refit=True,
    )
    
    xgb_search.fit(X_dev, y_dev)
    xgb_best = xgb_search.best_estimator_
    xgb_search_time = time.perf_counter() - train_time_start - rf_time - et_time
    print("\n=== XGBoost Results ===")
    print(f"Best XGBoost params: {xgb_search.best_params_}")
    print(f"Best XGBoost CV F1 Macro: {xgb_search.best_score_:.4f}")

    #Ensemble: soft voting averages predicted probabilities fromn both models
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("et", et), ("xgb", xgb_best)],
        voting="soft",
        n_jobs=-1,
    )
    
    # Cross validate ensemble metrics on the dev set
    cv_acc = cross_val_score(ensemble, X_dev, y_dev, cv=cv, scoring="accuracy", n_jobs=-1)
    cv_f1 = cross_val_score(ensemble, X_dev, y_dev, cv=cv, scoring="f1_macro", n_jobs=-1)
    print(f"\nEnsemble CV Accuracy: {cv_acc.mean():.4f} +/- {cv_acc.std():.4f}")
    print(f"Ensemble CV F1 Macro: {cv_f1.mean():.4f} +/- {cv_f1.std():.4f}")
    
    # Final Full dev set
    ensemble.fit(X_dev, y_dev)
    ensemble_time = time.perf_counter() - train_time_start - rf_time - et_time - xgb_search_time
    total_time = time.perf_counter() - train_time_start

    y_pred = ensemble.predict(X_test)

    # Decode 0..5 → original 1..6 labels for human-readable reports.
    y_test_orig = label_encoder.inverse_transform(y_test)
    y_pred_orig = label_encoder.inverse_transform(y_pred)
    original_classes = sorted(label_encoder.classes_.tolist())

    acc = accuracy_score(y_test_orig, y_pred_orig)
    macro_f1 = f1_score(y_test_orig, y_pred_orig, average="macro")
    weight_f1 = f1_score(y_test_orig, y_pred_orig, average="weighted")
    report_str = classification_report(y_test_orig, y_pred_orig, digits=3)
    cm = confusion_matrix(y_test_orig, y_pred_orig, labels=original_classes)

    print(f"Accuracy: {acc:.4f}")
    print(f"Macro-F1: {macro_f1:.4f}")
    print(f"Weighted-F1: {weight_f1:.4f}")
    print("\nPer-class:")
    print(report_str)
    print(f"\nConfusion matrix (rows=true, cols=pred), categories {original_classes}:")
    print(cm)

    print("\n=== Training Time Calculation ===")
    print(f"  RandomForest fit:    {rf_time:6.1f}s")
    print(f"  ExtraTrees fit:      {et_time:6.1f}s")
    print(f"  XGB RandomizedCV:    {xgb_search_time:6.1f}s")
    print(f"  Ensemble CV + fit:   {ensemble_time:6.1f}s")
    print(f"  TOTAL:               {total_time:6.1f}s")

    # save model + schema
    joblib.dump(ensemble, MODELS_DIR / "ensemble.joblib")
    joblib.dump(label_encoder, MODELS_DIR / "label_encoder.joblib")
    (MODELS_DIR / "best_model_name.txt").write_text("VotingClassifier")
    (MODELS_DIR / "feature_columns.json").write_text(json.dumps(feature_columns, indent=2))

    print("\nSaved model files into backend/models/")
    print("- ensemble.joblib")
    print("- label_encoder.joblib")
    print("- best_model_name.txt")
    print("- feature_columns.json")

    # ---- Disease classifier (real-world labels from Kaggle) ----
    disease_metrics = None
    if has_disease:
        disease_metrics = train_disease_model(X, disease_y_raw, feature_columns)

    # Save metric metadata
    metrics = {
    "trained_at": datetime.datetime.now().isoformat(timespec="seconds"),
    "cv_accuracy_mean": float(cv_acc.mean()),
    "cv_accuracy_std":  float(cv_acc.std()),
    "cv_macro_f1_mean": float(cv_f1.mean()),
    "cv_macro_f1_std":  float(cv_f1.std()),
    "test_accuracy":    float(acc),
    "test_macro_f1":    float(macro_f1),
    "test_weighted_f1": float(weight_f1),
    "best_xgb_params":  xgb_search.best_params_,
    "confusion_matrix": cm.tolist(),
    "n_features":       len(feature_columns),
    "n_train":          len(X_dev),
    "n_test":           len(X_test),
    "timing_seconds": {
        "random_forest_fit": round(rf_time, 2),
        "extra_trees_fit":   round(et_time, 2),
        "xgb_randomized_cv": round(xgb_search_time, 2),
        "ensemble_cv_fit":   round(ensemble_time, 2),
        "total":             round(total_time, 2),
    },
    }
    
    if disease_metrics is not None:
        metrics["disease_model"] = disease_metrics

    (MODELS_DIR / "ml_metrics.json").write_text(json.dumps(metrics, indent=2))


def train_disease_model(X, disease_y_raw, feature_columns):
    """Train a separate disease classifier on the same feature matrix.

    Disease labels live in their own label space (40+ Kaggle diseases) so we
    keep this model and its encoder isolated from the triage pipeline.
    """
    print("\n=== Disease classifier ===")
    disease_encoder = LabelEncoder()
    y_disease = disease_encoder.fit_transform(disease_y_raw.astype(str))

    X_dev_d, X_test_d, y_dev_d, y_test_d = train_test_split(
        X, y_disease, test_size=0.2, random_state=42, stratify=y_disease
    )

    disease_clf = XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
    )
    t0 = time.perf_counter()
    disease_clf.fit(X_dev_d, y_dev_d)
    fit_time = time.perf_counter() - t0

    pred = disease_clf.predict(X_test_d)
    acc = accuracy_score(y_test_d, pred)
    macro_f1 = f1_score(y_test_d, pred, average="macro")
    print(f"Disease accuracy:  {acc:.4f}")
    print(f"Disease macro-F1:  {macro_f1:.4f}")

    joblib.dump(disease_clf, MODELS_DIR / "disease_model.joblib")
    joblib.dump(disease_encoder, MODELS_DIR / "disease_label_encoder.joblib")
    (MODELS_DIR / "disease_classes.json").write_text(
        json.dumps(disease_encoder.classes_.tolist(), indent=2)
    )
    print("Saved disease_model.joblib, disease_label_encoder.joblib, disease_classes.json")

    return {
        "test_accuracy": float(acc),
        "test_macro_f1": float(macro_f1),
        "n_classes": int(len(disease_encoder.classes_)),
        "n_train": int(len(X_dev_d)),
        "n_test": int(len(X_test_d)),
        "fit_seconds": round(fit_time, 2),
    }


if __name__ == "__main__":
    main()