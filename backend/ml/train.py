import datetime
import json
import time

import joblib
import numpy as np
import pandas as pd
import sklearn
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
    cross_validate,
)
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

sklearn.set_config(enable_metadata_routing=True)

from config import (
    DISEASE_TRAINING_CSV,
    MODEL_DIR,
    REPORTS_DIR,
    TRIAGE_TRAINING_CSV,
)

RANDOM_STATE = 42
TEST_SIZE = 0.2
N_FOLDS = 3
RARE_TRIAGE_MIN = 40
RARE_DISEASE_MIN = 40
XGB_N_ITER = 15
CALIBRATION_SIZE = 0.1


def main(skip_disease: bool = False):
    MODEL_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    grand_t0 = time.perf_counter()
    triage_metrics = run_triage()
    disease_metrics = (
        None
        if skip_disease
        else (run_disease() if DISEASE_TRAINING_CSV.exists() else None)
    )
    total_seconds = round(time.perf_counter() - grand_t0, 2)

    _print_timing_summary(triage_metrics, disease_metrics, total_seconds)
    _write_metrics(triage_metrics, disease_metrics, total_seconds)


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #
def run_triage():
    df = pd.read_csv(TRIAGE_TRAINING_CSV)
    for col in ("triage_category", "group_id"):
        if col not in df.columns:
            raise ValueError(f"Triage dataset must contain '{col}' column")
    df = _drop_rare_classes(df, "triage_category", RARE_TRIAGE_MIN)

    X = df.drop(columns=["triage_category", "group_id"])
    feature_columns = list(X.columns)
    encoder = LabelEncoder()
    y = encoder.fit_transform(df["triage_category"])
    groups = df["group_id"].to_numpy()

    return train_triage_model(X, y, groups, encoder, feature_columns)


def run_disease():
    df = pd.read_csv(DISEASE_TRAINING_CSV)
    for col in ("disease", "group_id"):
        if col not in df.columns:
            raise ValueError(f"Disease dataset must contain '{col}' column")

    X = df.drop(columns=["disease", "group_id"])
    disease_y_raw = df["disease"].astype(str).reset_index(drop=True)
    groups = df["group_id"].to_numpy()
    return train_disease_model(X, disease_y_raw, groups)


def _drop_rare_classes(df: pd.DataFrame, col: str, min_count: int) -> pd.DataFrame:
    counts = df[col].value_counts()
    rare = counts[counts < min_count].index.tolist()
    if rare:
        print(f"Dropping rare {col} values with <{min_count} rows: {rare}")
        df = df[~df[col].isin(rare)].reset_index(drop=True)
    return df


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
    ).set_fit_request(sample_weight=True)


def _fit_xgb(
    X_train,
    y_train,
    groups_train,
    xgb_param_grid,
    *,
    sample_weight=None,
    scoring="neg_log_loss",
):
    cv = StratifiedGroupKFold(
        n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE
    )
    t0 = time.perf_counter()
    search = RandomizedSearchCV(
        estimator=_build_xgb(),
        param_distributions=xgb_param_grid,
        n_iter=XGB_N_ITER,
        scoring=scoring,
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        refit=True,
    )
    fit_kwargs = {"groups": groups_train}
    if sample_weight is not None:
        fit_kwargs["sample_weight"] = sample_weight
    search.fit(X_train, y_train, **fit_kwargs)
    return search.best_estimator_, {
        "xgb_search_seconds": round(time.perf_counter() - t0, 2),
        "best_xgb_params": search.best_params_,
        "best_xgb_cv_neg_log_loss": float(search.best_score_),
    }


# --------------------------------------------------------------------------- #
# Triage model
# --------------------------------------------------------------------------- #
def train_triage_model(X, y, groups, encoder, feature_columns):
    print("\n--- Triage classifier (ESI 1-5) ---")
    t0 = time.perf_counter()
    outer = GroupShuffleSplit(
        n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    train_idx, test_idx = next(outer.split(X, y, groups))
    X_dev, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_dev, y_test = y[train_idx], y[test_idx]
    groups_dev = groups[train_idx]
    print(f"  Train: {len(X_dev):,} | Test: {len(X_test):,} | Features: {len(feature_columns)}")

    xgb_grid = {
        "n_estimators": [200, 300, 400],
        "max_depth": [4, 6, 8],
        "learning_rate": [0.05, 0.1, 0.15],
        "subsample": [0.85, 1.0],
        "colsample_bytree": [0.8, 1.0],
    }
    sample_weight_dev = np.sqrt(compute_sample_weight("balanced", y_dev))
    model, fit_info = _fit_xgb(
        X_dev, y_dev, groups_dev, xgb_grid,
        sample_weight=sample_weight_dev,
    )

    cv = StratifiedGroupKFold(
        n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE
    )
    cv_results = cross_validate(
        model, X_dev, y_dev, cv=cv,
        scoring=["accuracy", "f1_macro"],
        n_jobs=-1,
        params={"groups": groups_dev, "sample_weight": sample_weight_dev},
    )
    cv_acc = cv_results["test_accuracy"]
    cv_f1 = cv_results["test_f1_macro"]

    y_pred = model.predict(X_test)
    y_test_orig = encoder.inverse_transform(y_test)
    y_pred_orig = encoder.inverse_transform(y_pred)
    classes_orig = sorted(encoder.classes_.tolist())

    acc = accuracy_score(y_test_orig, y_pred_orig)
    macro_f1 = f1_score(y_test_orig, y_pred_orig, average="macro")
    weight_f1 = f1_score(y_test_orig, y_pred_orig, average="weighted")
    cm = confusion_matrix(y_test_orig, y_pred_orig, labels=classes_orig)
    per_class_f1 = f1_score(y_test_orig, y_pred_orig, labels=classes_orig, average=None)

    print(f"  CV accuracy : {cv_acc.mean():.4f} +/- {cv_acc.std():.4f}")
    print(f"  CV macro-F1 : {cv_f1.mean():.4f} +/- {cv_f1.std():.4f}")
    print(f"  Test acc    : {acc:.4f} | macro-F1: {macro_f1:.4f} | weighted-F1: {weight_f1:.4f}")
    per_class_str = "  ".join(f"ESI {c}: {f:.3f}" for c, f in zip(classes_orig, per_class_f1))
    print(f"  Per-class F1: {per_class_str}")

    joblib.dump(model, MODEL_DIR / "triage_model.joblib")
    joblib.dump(encoder, MODEL_DIR / "triage_label_encoder.joblib")
    (MODEL_DIR / "model_features.json").write_text(
        json.dumps(feature_columns, indent=2)
    )
    print("  Saved: triage_model.joblib, triage_label_encoder.joblib, model_features.json")

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
        "labels": classes_orig,
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
    print("\n--- Disease classifier ---")
    t0 = time.perf_counter()
    X, disease_y_raw, groups = _filter_rare_diseases(X, disease_y_raw, groups)

    outer = GroupShuffleSplit(
        n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    train_idx, test_idx = next(outer.split(X, disease_y_raw, groups))

    train_classes = sorted(set(disease_y_raw.iloc[train_idx]))
    encoder = LabelEncoder().fit(train_classes)

    test_mask = disease_y_raw.iloc[test_idx].isin(train_classes).to_numpy()
    test_idx = test_idx[test_mask]
    if (n_dropped := int((~test_mask).sum())):
        print(f"Dropped {n_dropped} test rows whose disease was unseen in train.")

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

    val_proba = model.predict_proba(X_val)
    temperature = _fit_temperature(val_proba, y_val)

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
    print(f"  Train: {len(X_train):,} | Cal: {len(X_val):,} | Test: {len(X_test):,} | Classes: {len(encoder.classes_)}")
    print(
        f"  Test top-1: {metrics['test_top1_accuracy']:.4f} | "
        f"top-3: {metrics['test_top3_accuracy']:.4f} | "
        f"top-5: {metrics['test_top5_accuracy']:.4f} | "
        f"macro-F1: {metrics['test_macro_f1']:.4f}"
    )
    print(
        f"  Temperature T={temperature:.4f} | "
        f"log-loss raw {metrics['test_log_loss_raw']:.4f} -> scaled {metrics['test_log_loss_scaled']:.4f} | "
        f"mean conf raw {metrics['test_top1_confidence_mean_raw']:.4f} -> scaled {metrics['test_top1_confidence_mean_scaled']:.4f}"
    )

    joblib.dump(model, MODEL_DIR / "disease_model.joblib")
    joblib.dump(encoder, MODEL_DIR / "disease_label_encoder.joblib")
    (MODEL_DIR / "disease_classes.json").write_text(
        json.dumps(encoder.classes_.tolist(), indent=2)
    )
    (MODEL_DIR / "disease_temperature.json").write_text(
        json.dumps({"temperature": float(temperature)}, indent=2)
    )
    print("  Saved: disease_model.joblib, disease_label_encoder.joblib, disease_classes.json, disease_temperature.json")
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
    eps = 1e-12
    logp = np.log(np.clip(probs, eps, 1.0)) / T
    logp -= logp.max(axis=1, keepdims=True)
    e = np.exp(logp)
    return e / e.sum(axis=1, keepdims=True)


def _fit_temperature(probs: np.ndarray, y_true: np.ndarray) -> float:
    labels = np.arange(probs.shape[1])

    def objective(T: float) -> float:
        return log_loss(y_true, _apply_temperature(probs, T), labels=labels)

    res = minimize_scalar(objective, bounds=(0.05, 5.0), method="bounded")
    return float(res.x)


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def _print_timing_summary(triage_metrics, disease_metrics, total_seconds):
    print("\n--- Summary ---")
    print(f"  {'Stage':<10} {'XGB search':>12} {'Total':>10}")
    print(f"  {'-'*10} {'-'*12} {'-'*10}")
    print(
        f"  {'Triage':<10} "
        f"{triage_metrics['xgb_search_seconds']:>10.1f}s "
        f"{triage_metrics['total_seconds']:>9.1f}s"
    )
    if disease_metrics is not None:
        print(
            f"  {'Disease':<10} "
            f"{disease_metrics['xgb_search_seconds']:>10.1f}s "
            f"{disease_metrics['total_seconds']:>9.1f}s"
        )
    print(f"  {'-'*10} {'-'*12} {'-'*10}")
    print(f"  {'Total':<10} {'':>12} {total_seconds:>9.1f}s")


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
    import argparse

    parser = argparse.ArgumentParser(description="Train SACA models.")
    parser.add_argument(
        "--skip-disease",
        action="store_true",
        help="Train only the triage model (skip the slow disease model).",
    )
    args = parser.parse_args()
    main(skip_disease=args.skip_disease)
