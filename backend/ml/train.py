import datetime
import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    top_k_accuracy_score,
)
from sklearn.model_selection import (
    GroupShuffleSplit,
    RandomizedSearchCV,
    StratifiedGroupKFold,
    cross_val_score,
)
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "models" / "training_data.csv"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

RANDOM_STATE = 42
TEST_SIZE = 0.2
N_FOLDS = 3
RARE_TRIAGE_MIN = 40
RARE_DISEASE_MIN = 40
XGB_N_ITER = 15
CALIBRATION_SIZE = 0.1


def main():
    MODELS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    df = _load_dataset()
    has_disease = "disease" in df.columns

    df = _drop_rare_classes(df, "triage_category", RARE_TRIAGE_MIN)
    feature_columns, X, y_triage, groups, triage_encoder = _prepare_triage_inputs(df)
    disease_y_raw = (
        df["disease"].astype(str).reset_index(drop=True) if has_disease else None
    )

    grand_t0 = time.perf_counter()
    triage_metrics = train_triage_model(
        X, y_triage, groups, triage_encoder, feature_columns
    )
    disease_metrics = (
        train_disease_model(X, disease_y_raw, groups) if has_disease else None
    )
    total_seconds = round(time.perf_counter() - grand_t0, 2)

    _print_timing_summary(triage_metrics, disease_metrics, total_seconds)
    _write_metrics(triage_metrics, disease_metrics, total_seconds)

# --------------------------------------------------------------------------- #
# Data loading and prep
# --------------------------------------------------------------------------- #
def _load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    if "triage_category" not in df.columns:
        raise ValueError("Dataset must contain 'triage_category' column")
    if "group_id" not in df.columns:
        raise ValueError("Dataset must contain 'group_id' column for group-aware split")
    return df


def _drop_rare_classes(df: pd.DataFrame, col: str, min_count: int) -> pd.DataFrame:
    counts = df[col].value_counts()
    rare = counts[counts < min_count].index.tolist()
    if rare:
        print(f"Dropping rare {col} values with <{min_count} rows: {rare}")
        df = df[~df[col].isin(rare)].reset_index(drop=True)
    return df


def _prepare_triage_inputs(df: pd.DataFrame):
    drop_cols = ["triage_category", "group_id"] + (
        ["disease"] if "disease" in df.columns else []
    )
    X = df.drop(columns=drop_cols)
    feature_columns = list(X.columns)
    encoder = LabelEncoder()
    y = encoder.fit_transform(df["triage_category"])
    groups = df["group_id"].to_numpy()
    return feature_columns, X, y, groups, encoder

# --------------------------------------------------------------------------- #
# Model building blocks (shared by triage and disease)
# --------------------------------------------------------------------------- #
def _build_xgb() -> XGBClassifier:
    return XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method="hist",
    )


def _fit_xgb(X_train, y_train, groups_train, xgb_param_grid):
    """Fit XGB via group-aware RandomizedSearchCV and return the refit estimator."""
    cv = StratifiedGroupKFold(
        n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE
    )

    t0 = time.perf_counter()
    xgb_search = RandomizedSearchCV(
        estimator=_build_xgb(),
        param_distributions=xgb_param_grid,
        n_iter=XGB_N_ITER,
        scoring="neg_log_loss",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        refit=True,
    )
    xgb_search.fit(X_train, y_train, groups=groups_train)
    xgb_time = time.perf_counter() - t0

    fit_info = {
        "xgb_search_seconds": round(xgb_time, 2),
        "best_xgb_params": xgb_search.best_params_,
        "best_xgb_cv_neg_log_loss": float(xgb_search.best_score_),
    }
    return xgb_search.best_estimator_, fit_info


# --------------------------------------------------------------------------- #
# Triage model
# --------------------------------------------------------------------------- #
def train_triage_model(X, y, groups, encoder, feature_columns):
    print("\n=== Triage classifier ===")
    t0 = time.perf_counter()
    outer = GroupShuffleSplit(
        n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    train_idx, test_idx = next(outer.split(X, y, groups))
    X_dev, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_dev, y_test = y[train_idx], y[test_idx]
    groups_dev = groups[train_idx]

    xgb_grid = {
        "n_estimators": [100, 200, 300],
        "max_depth": [4, 6],
        "learning_rate": [0.1, 0.15],
        "subsample": [0.85, 1.0],
        "colsample_bytree": [0.8, 1.0],
    }
    model, fit_info = _fit_xgb(X_dev, y_dev, groups_dev, xgb_grid)

    cv = StratifiedGroupKFold(
        n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE
    )
    cv_acc = cross_val_score(
        model, X_dev, y_dev, cv=cv, scoring="accuracy",
        n_jobs=-1, groups=groups_dev,
    )
    cv_f1 = cross_val_score(
        model, X_dev, y_dev, cv=cv, scoring="f1_macro",
        n_jobs=-1, groups=groups_dev,
    )

    y_pred = model.predict(X_test)
    y_test_orig = encoder.inverse_transform(y_test)
    y_pred_orig = encoder.inverse_transform(y_pred)
    classes_orig = sorted(encoder.classes_.tolist())

    acc = accuracy_score(y_test_orig, y_pred_orig)
    macro_f1 = f1_score(y_test_orig, y_pred_orig, average="macro")
    weight_f1 = f1_score(y_test_orig, y_pred_orig, average="weighted")
    cm = confusion_matrix(y_test_orig, y_pred_orig, labels=classes_orig)

    print(f"Triage test accuracy:  {acc:.4f}")
    print(f"Triage test macro-F1:  {macro_f1:.4f}")
    print(classification_report(y_test_orig, y_pred_orig, digits=3))

    joblib.dump(model, MODELS_DIR / "triage_model.joblib")
    joblib.dump(encoder, MODELS_DIR / "triage_label_encoder.joblib")
    (MODELS_DIR / "model_features.json").write_text(
        json.dumps(feature_columns, indent=2)
    )

    total_seconds = round(time.perf_counter() - t0, 2)
    return {
        "split_strategy": (
            f"GroupShuffleSplit (outer) + StratifiedGroupKFold-{N_FOLDS} (inner)"
        ),
        "cv_accuracy_mean": float(cv_acc.mean()),
        "cv_accuracy_std": float(cv_acc.std()),
        "cv_macro_f1_mean": float(cv_f1.mean()),
        "cv_macro_f1_std": float(cv_f1.std()),
        "test_accuracy": float(acc),
        "test_macro_f1": float(macro_f1),
        "test_weighted_f1": float(weight_f1),
        "confusion_matrix": cm.tolist(),
        "n_features": len(feature_columns),
        "n_train": int(len(X_dev)),
        "n_test": int(len(X_test)),
        "total_seconds": total_seconds,
        **fit_info,
    }


# --------------------------------------------------------------------------- #
# Disease model
# --------------------------------------------------------------------------- #

def train_disease_model(X, disease_y_raw, groups):
    print("\n=== Disease classifier ===")
    t0 = time.perf_counter()
    X, disease_y_raw, groups = _filter_rare_diseases(X, disease_y_raw, groups)

    # Group-aware 80/20 outer split.
    outer = GroupShuffleSplit(
        n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    train_idx, test_idx = next(outer.split(X, disease_y_raw, groups))

    train_classes = sorted(set(disease_y_raw.iloc[train_idx]))
    encoder = LabelEncoder().fit(train_classes)

    # XGB needs contiguous 0..N-1 labels; drop test rows whose class never appeared in train.
    test_mask = disease_y_raw.iloc[test_idx].isin(train_classes).to_numpy()
    test_idx = test_idx[test_mask]
    if (n_dropped := int((~test_mask).sum())):
        print(f"Dropped {n_dropped} test rows whose disease was unseen in train.")

    # Carve a calibration slice out of the training set for temperature fitting.
    dev_groups = groups[train_idx]
    cal_split = GroupShuffleSplit(
        n_splits=1, test_size=CALIBRATION_SIZE, random_state=RANDOM_STATE
    )
    cal_train_local, cal_val_local = next(
        cal_split.split(X.iloc[train_idx], disease_y_raw.iloc[train_idx], dev_groups)
    )
    cal_train_idx = train_idx[cal_train_local]
    cal_val_idx = train_idx[cal_val_local]

    X_train = X.iloc[cal_train_idx]
    X_val = X.iloc[cal_val_idx]
    X_test = X.iloc[test_idx]
    y_train = encoder.transform(disease_y_raw.iloc[cal_train_idx])
    y_val = encoder.transform(disease_y_raw.iloc[cal_val_idx])
    y_test = encoder.transform(disease_y_raw.iloc[test_idx])
    groups_train = groups[cal_train_idx]

    xgb_grid = {
        "n_estimators": [200, 300, 400],
        "max_depth": [6, 8, 10],
        "learning_rate": [0.05, 0.1, 0.15],
        "subsample": [0.85, 1.0],
        "colsample_bytree": [0.8, 1.0],
    }
    model, fit_info = _fit_xgb(X_train, y_train, groups_train, xgb_grid)

    # Fit temperature on the held-out calibration slice.
    val_proba = model.predict_proba(X_val)
    temperature = _fit_temperature(val_proba, y_val)
    print(f"Fitted temperature: T={temperature:.4f}")

    # Evaluate test set with both raw and temperature-scaled probabilities.
    raw_proba = model.predict_proba(X_test)
    scaled_proba = _apply_temperature(raw_proba, temperature)
    pred = raw_proba.argmax(axis=1)
    labels = np.arange(len(encoder.classes_))

    metrics = {
        "test_top1_accuracy": float(accuracy_score(y_test, pred)),
        "test_top3_accuracy": float(
            top_k_accuracy_score(y_test, raw_proba, k=3, labels=labels)
        ),
        "test_top5_accuracy": float(
            top_k_accuracy_score(y_test, raw_proba, k=5, labels=labels)
        ),
        "test_macro_f1": float(f1_score(y_test, pred, average="macro")),
        "test_log_loss_raw": float(log_loss(y_test, raw_proba, labels=labels)),
        "test_log_loss_scaled": float(log_loss(y_test, scaled_proba, labels=labels)),
        "test_top1_confidence_mean_raw": float(raw_proba.max(axis=1).mean()),
        "test_top1_confidence_mean_scaled": float(scaled_proba.max(axis=1).mean()),
        "temperature": float(temperature),
        "n_classes": int(len(encoder.classes_)),
        "n_train": int(len(X_train)),
        "n_calibration": int(len(X_val)),
        "n_test": int(len(X_test)),
        "total_seconds": round(time.perf_counter() - t0, 2),
        **fit_info,
    }
    print(
        f"Disease — top1 {metrics['test_top1_accuracy']:.4f} | "
        f"top3 {metrics['test_top3_accuracy']:.4f} | "
        f"top5 {metrics['test_top5_accuracy']:.4f} | "
        f"mean conf raw {metrics['test_top1_confidence_mean_raw']:.4f} → "
        f"scaled {metrics['test_top1_confidence_mean_scaled']:.4f}"
    )

    joblib.dump(model, MODELS_DIR / "disease_model.joblib")
    joblib.dump(encoder, MODELS_DIR / "disease_label_encoder.joblib")
    (MODELS_DIR / "disease_classes.json").write_text(
        json.dumps(encoder.classes_.tolist(), indent=2)
    )
    (MODELS_DIR / "disease_temperature.json").write_text(
        json.dumps({"temperature": float(temperature)}, indent=2)
    )
    return metrics


def _filter_rare_diseases(X, disease_y_raw, groups):
    counts = disease_y_raw.value_counts()
    keep = disease_y_raw.isin(counts[counts >= RARE_DISEASE_MIN].index)
    n_dropped = int((~keep).sum())
    if n_dropped:
        n_rare_classes = int((counts < RARE_DISEASE_MIN).sum())
        print(
            f"Dropped {n_dropped} rows across {n_rare_classes} disease classes "
            f"with <{RARE_DISEASE_MIN} samples."
        )
    keep_arr = keep.to_numpy()
    return (
        X.loc[keep].reset_index(drop=True),
        disease_y_raw.loc[keep].reset_index(drop=True),
        groups[keep_arr],
    )


# --------------------------------------------------------------------------- #
# Temperature scaling
# --------------------------------------------------------------------------- #

def _apply_temperature(probs: np.ndarray, T: float) -> np.ndarray:
    """Re-softmax log(probs)/T. T<1 sharpens, T>1 smooths."""
    eps = 1e-12
    logp = np.log(np.clip(probs, eps, 1.0)) / T
    logp -= logp.max(axis=1, keepdims=True)
    e = np.exp(logp)
    return e / e.sum(axis=1, keepdims=True)


def _fit_temperature(probs: np.ndarray, y_true: np.ndarray) -> float:
    """Find T that minimizes log-loss after temperature scaling."""
    labels = np.arange(probs.shape[1])

    def objective(T: float) -> float:
        return log_loss(y_true, _apply_temperature(probs, T), labels=labels)

    res = minimize_scalar(objective, bounds=(0.05, 5.0), method="bounded")
    return float(res.x)


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

def _print_timing_summary(triage_metrics, disease_metrics, total_seconds):
    print("\n=== Training Time Calculation ===")

    def _row(label, info):
        print(f"  {label:<22} XGB-search {info['xgb_search_seconds']:6.1f}s | "
              f"total {info['total_seconds']:6.1f}s")

    _row("Triage:", triage_metrics)
    if disease_metrics is not None:
        _row("Disease:", disease_metrics)
    print(f"  {'GRAND TOTAL':<22} {total_seconds:6.1f}s")


def _write_metrics(triage_metrics, disease_metrics, total_seconds):
    out = {
        "trained_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "total_training_seconds": total_seconds,
        "triage_model": triage_metrics,
    }
    if disease_metrics is not None:
        out["disease_model"] = disease_metrics
    (REPORTS_DIR / "training_metrics.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
