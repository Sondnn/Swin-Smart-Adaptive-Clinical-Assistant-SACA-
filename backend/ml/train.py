import json
import pandas as pd
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, VotingClassifier


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "models" / "training_data_v1.csv"
MODELS_DIR = BASE_DIR / "models"


def main():
    MODELS_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    if "triage_category" not in df.columns:
        raise ValueError("Dataset must contain 'triage_category' column")

    y = df["triage_category"]
    X = df.drop(columns=["triage_category"])

    feature_columns = list(X.columns)

    # split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Algorithm 1: Random Forest
    rf = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced"
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)

    print("\n=== Random Forest Results ===")
    print("Accuracy:", rf_acc)
    print(classification_report(y_test, rf_pred))

    # Algorithm 2: Extra Trees
    et = ExtraTreesClassifier(
        n_estimators=500,
        random_state=42,
        class_weight="balanced"
    )
    et.fit(X_train, y_train)
    et_pred = et.predict(X_test)
    et_acc = accuracy_score(y_test, et_pred)

    print("\n=== Extra Trees Results ===")
    print("Accuracy:", et_acc)
    print(classification_report(y_test, et_pred))

    #Ensemble: soft voting averages predicted probabilities fromn both models
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("et", et)],
        voting="soft"
    )
    ensemble.fit(X_train, y_train)
    ensemble_pred = ensemble.predict(X_test)
    ensemble_acc = accuracy_score(y_test, ensemble_pred)
    
    # # choose best model
    # if et_acc >= rf_acc:
    #     best_model = et
    #     best_name = "ExtraTreesClassifier"
    #     best_acc = et_acc
    # else:
    #     best_model = rf
    #     best_name = "RandomForestClassifier"
    #     best_acc = rf_acc

    print("\n=== VotingClassifier Results ===")
    print("Accuracy:", ensemble_acc)
    print(classification_report(y_test, ensemble_pred))

    # save model + schema
    joblib.dump(ensemble, MODELS_DIR / "best_model.joblib")
    (MODELS_DIR / "best_model_name.txt").write_text("VotingClassifier")
    (MODELS_DIR / "feature_columns.json").write_text(json.dumps(feature_columns, indent=2))

    print("\nSaved model files into backend/models/")
    print("- best_model.joblib")
    print("- best_model_name.txt")
    print("- feature_columns.json")


if __name__ == "__main__":
    main()