from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from nlp.nlp_service import process_audio_response

AUDIO_DIR = BACKEND_DIR / "data" / "wmt_audio"
MANIFEST_FILE = AUDIO_DIR / "manifest.json"


def main() -> int:
    if not AUDIO_DIR.exists():
        print(f"No audio dir at {AUDIO_DIR}; nothing to evaluate.")
        return 0
    if not MANIFEST_FILE.exists():
        print(f"No manifest at {MANIFEST_FILE}; create one to run evaluation.")
        return 0

    manifest = json.loads(MANIFEST_FILE.read_text())
    backend = os.environ.get("WMT_ASR_BACKEND", "whisper")
    print(f"STT backend: {backend}")
    print(f"Samples: {len(manifest)}")

    correct = 0
    for entry in manifest:
        wav_path = AUDIO_DIR / entry["file"]
        with wav_path.open("rb") as f:
            result = process_audio_response(f, language=0, question_id=entry["question_id"])
        actual = result["parsed_response"]
        if isinstance(actual, dict):
            actual = {k: (sorted(v) if isinstance(v, set) else v) for k, v in actual.items()}
        expected = entry["expected"]
        match = actual == expected
        if match:
            correct += 1
        status = "OK" if match else "MISS"
        conf = result.get("confidence")
        conf_str = f"{conf:.2f}" if isinstance(conf, (int, float)) else "n/a"
        print(f"  [{status}] q={entry['question_id']:<2} file={entry['file']:<24} conf={conf_str} expected={expected} actual={actual}")

    if manifest:
        print(f"Accuracy: {correct}/{len(manifest)} ({100 * correct / len(manifest):.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
