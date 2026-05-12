"""Run the SACA ML pipeline end-to-end
Usage:
  python3 backend/scripts/run_ml_pipeline.py
  python3 backend/scripts/run_ml_pipeline.py --skip-build     # retrain only
  python3 backend/scripts/run_ml_pipeline.py --skip-train     # ingest only
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BACKEND_DIR / "data" / "raw_v2"
ML_DIR = BACKEND_DIR / "ml"

REQUIRED_RAW = ["Final_Augmented_dataset_Diseases_and_Symptoms.csv"]


def check_raw_data() -> None:
    missing = [f for f in REQUIRED_RAW if not (RAW_DIR / f).exists()]
    if missing:
        print(f"ERROR: missing Kaggle files in {RAW_DIR}: {missing}", file=sys.stderr)
        print(
            "Download once with:\n"
            "  cd backend/data/raw_v2 && kaggle datasets download "
            "-d dhivyeshrk/diseases-and-symptoms-dataset --unzip",
            file=sys.stderr,
        )
        sys.exit(1)


def run(label: str, cmd: list[str], cwd: Path) -> None:
    print(f"\n>>> [{label}] {' '.join(cmd)}  (cwd={cwd})")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"ERROR: {label} failed (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-build", action="store_true", help="Skip ingest stage.")
    parser.add_argument("--skip-train", action="store_true", help="Skip training stage.")
    args = parser.parse_args()

    if not args.skip_build:
        check_raw_data()
        # build_training_data.py uses bare imports — must run from ml/.
        run("ingest", [sys.executable, "build_training_data.py"], cwd=ML_DIR)

    if not args.skip_train:
        run("train", [sys.executable, "-m", "ml.train"], cwd=BACKEND_DIR)

    print("\nPipeline finished.")


if __name__ == "__main__":
    main()
