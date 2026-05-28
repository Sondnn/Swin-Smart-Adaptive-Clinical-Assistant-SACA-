"""Run the SACA ML pipeline end-to-end (triage + disease).

Usage:
python3 backend/scripts/run_ml_pipeline.py
python3 backend/scripts/run_ml_pipeline.py --skip-build     # retrain only
python3 backend/scripts/run_ml_pipeline.py --skip-train     # ingest only

The pipeline trains two models from two distinct Kaggle datasets:
* Triage (POPGUNS 1-6): maalona/hospital-triage-and-patient-history-data
* Disease classifier: dhivyeshrk/diseases-and-symptoms-dataset

Prerequisite
* Must setup Kaggle CLI
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import BASE_DIR, RAW_DISEASE_DIR, RAW_DISEASE_FILE, RAW_TRIAGE_DIR, RAW_TRIAGE_FILE

BACKEND_DIR = BASE_DIR
ML_DIR = BACKEND_DIR / "ml"

DATASETS = [
    {
        "name": "triage",
        "kaggle": "maalona/hospital-triage-and-patient-history-data",
        "raw_dir": RAW_TRIAGE_DIR,
        "required": [RAW_TRIAGE_FILE.name],
        "build_script": "build_triage_data.py",
    },
    {
        "name": "disease",
        "kaggle": "dhivyeshrk/diseases-and-symptoms-dataset",
        "raw_dir": RAW_DISEASE_DIR,
        "required": [RAW_DISEASE_FILE.name],
        "build_script": "build_disease_data.py",
    },
]


BANNER = "=" * 60


def _banner(text: str) -> None:
    print(f"\n{BANNER}\n  {text}\n{BANNER}", flush=True)


def download_raw_data(kaggle: str, raw_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["kaggle", "datasets", "download", "-d", kaggle, "--unzip"]
    print(f"  downloading {kaggle} -> {raw_dir.relative_to(BACKEND_DIR)}")
    try:
        result = subprocess.run(cmd, cwd=raw_dir)
    except FileNotFoundError:
        print(
            "ERROR: `kaggle` CLI not found. Install and authenticate with:\n"
            "  pip install kaggle\n"
            "  # then place your API token at ~/.kaggle/kaggle.json",
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


def ensure_raw(dataset: dict) -> None:
    missing = [f for f in dataset["required"] if not (dataset["raw_dir"] / f).exists()]
    if not missing:
        return
    print(f"  missing raw files: {missing}")
    download_raw_data(dataset["kaggle"], dataset["raw_dir"])
    still_missing = [f for f in dataset["required"] if not (dataset["raw_dir"] / f).exists()]
    if still_missing:
        print(f"ERROR: still missing after download: {still_missing}", file=sys.stderr)
        sys.exit(1)


def run(label: str, cmd: list[str], cwd: Path) -> None:
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
        for ds in DATASETS:
            _banner(f"Ingest: {ds['name']}")
            ensure_raw(ds)
            run(f"ingest:{ds['name']}", [sys.executable, ds["build_script"]], cwd=ML_DIR)

    if not args.skip_train:
        _banner("Train")
        run("train", [sys.executable, "-m", "ml.train"], cwd=BACKEND_DIR)

    print("\nPipeline finished.")


if __name__ == "__main__":
    main()
