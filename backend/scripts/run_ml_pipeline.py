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

KAGGLE_DATASET = "dhivyeshrk/diseases-and-symptoms-dataset"
REQUIRED_RAW = ["Final_Augmented_dataset_Diseases_and_Symptoms.csv"]


def download_raw_data() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cmd = ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET, "--unzip"]
    print(f"\n>>> [download] {' '.join(cmd)}  (cwd={RAW_DIR})")
    try:
        result = subprocess.run(cmd, cwd=RAW_DIR)
    except FileNotFoundError:
        print(
            "ERROR: `kaggle` CLI not found. Install and authenticate with:\n"
            "  pip install kaggle\n"
            "  # then place your API token at ~/.kaggle/kaggle.json "
            "(Kaggle → Account → Create API Token)",
            file=sys.stderr,
        )
        sys.exit(1)
    if result.returncode != 0:
        print(
            f"ERROR: kaggle download failed (exit {result.returncode}). "
            "Check that ~/.kaggle/kaggle.json exists and is chmod 600.",
            file=sys.stderr,
        )
        sys.exit(result.returncode)


def check_raw_data() -> None:
    missing = [f for f in REQUIRED_RAW if not (RAW_DIR / f).exists()]
    if not missing:
        return

    print(f"Missing raw files in {RAW_DIR}: {missing} — downloading from Kaggle...")
    download_raw_data()

    still_missing = [f for f in REQUIRED_RAW if not (RAW_DIR / f).exists()]
    if still_missing:
        print(
            f"ERROR: still missing after download: {still_missing}",
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
