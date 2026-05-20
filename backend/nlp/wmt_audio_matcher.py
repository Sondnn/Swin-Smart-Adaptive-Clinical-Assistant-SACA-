"""Audio-to-audio matching for Walmadjari fixed-answer questions.
Reference directory layout:
    backend/data/wmt_references/
        female/        clip.wav
        male/          another.wav
        yes/           clip.wav
        no/            clip.wav
        unknown/       clip.wav
        mild/          clip.wav
        severe/        clip.wav
        over_65/       clip.wav        # -> "over 65"
        type_2_diabetes/ clip.wav      # -> "type 2 diabetes"

"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

REFERENCES_DIR = Path(os.environ.get(
    "WMT_REFERENCES_DIR",
    str(Path(__file__).resolve().parents[1] / "data" / "wmt_references"),
))

SAMPLE_RATE = 16000

WMT_AUDIO_MATCH_MAX_COST = 35.0

WMT_AUDIO_MATCH_MARGIN_RATIO = 0.10


def label_to_text(label: str) -> str:
    """Folder label -> parser-ready English phrase ('over_65' -> 'over 65')."""
    return label.replace("_", " ").strip().lower()


@dataclass
class AudioMatch:
    matched_label: Optional[str]   # folder label, e.g. "female"; None if no match
    cost: float
    similarity: float
    matched_reference: str         # matched wav filename, "" if no match
    refs_considered: int


def _extract_mfcc(wav_path: str):
    try:
        import librosa
        import numpy as np
    except ImportError:
        return None
    y, _ = librosa.load(wav_path, sr=SAMPLE_RATE, mono=True)
    if y.size == 0:
        return None
    y, _ = librosa.effects.trim(y, top_db=30)
    mfcc = librosa.feature.mfcc(y=y, sr=SAMPLE_RATE, n_mfcc=13)
    mfcc = (mfcc - mfcc.mean(axis=1, keepdims=True)) / (mfcc.std(axis=1, keepdims=True) + 1e-9)
    return mfcc.astype(np.float32)


@dataclass
class _Reference:
    label: str
    wav_path: Path
    mfcc: object


@lru_cache(maxsize=1)
def _load_references() -> tuple[_Reference, ...]:
    if not REFERENCES_DIR.is_dir():
        return ()
    refs: list[_Reference] = []
    for label_dir in sorted(REFERENCES_DIR.iterdir()):
        if not label_dir.is_dir():
            continue
        for wav in sorted(label_dir.glob("*.wav")):
            mfcc = _extract_mfcc(str(wav))
            if mfcc is None or mfcc.shape[1] < 5:
                continue
            refs.append(_Reference(label=label_dir.name, wav_path=wav, mfcc=mfcc))
    return tuple(refs)


def available_labels() -> tuple[str, ...]:
    """Distinct labels present in the reference bank, in sorted order."""
    return tuple(dict.fromkeys(ref.label for ref in _load_references()))


def match_audio(wav_path: str, allowed_labels: Optional[Iterable[str]] = None) -> AudioMatch:
    refs = _load_references()
    if allowed_labels is not None:
        allowed = set(allowed_labels)
        refs = tuple(ref for ref in refs if ref.label in allowed)
    if not refs:
        return AudioMatch(None, 0.0, 0.0, "", 0)

    query_mfcc = _extract_mfcc(wav_path)
    if query_mfcc is None or query_mfcc.shape[1] < 5:
        return AudioMatch(None, 0.0, 0.0, "", len(refs))

    try:
        import librosa
    except ImportError:
        return AudioMatch(None, 0.0, 0.0, "", len(refs))

    per_ref_cost: list[tuple[_Reference, float]] = []
    for ref in refs:
        D, _ = librosa.sequence.dtw(X=ref.mfcc, Y=query_mfcc, metric="euclidean")
        path_len = D.shape[0] + D.shape[1]
        cost = float(D[-1, -1]) / max(1, path_len)
        per_ref_cost.append((ref, cost))

    best_per_label: dict[str, tuple[_Reference, float]] = {}
    for ref, cost in per_ref_cost:
        if ref.label not in best_per_label or cost < best_per_label[ref.label][1]:
            best_per_label[ref.label] = (ref, cost)

    ranked = sorted(best_per_label.items(), key=lambda kv: kv[1][1])
    winner_label, (winner_ref, winner_cost) = ranked[0]
    runner_cost = ranked[1][1][1] if len(ranked) > 1 else float("inf")

    if winner_cost > WMT_AUDIO_MATCH_MAX_COST:
        return AudioMatch(None, winner_cost, 0.0, winner_ref.wav_path.name, len(refs))

    if runner_cost != float("inf") and winner_cost > 1e-6:
        if runner_cost / winner_cost < 1.0 + WMT_AUDIO_MATCH_MARGIN_RATIO:
            return AudioMatch(None, winner_cost, 0.0, winner_ref.wav_path.name, len(refs))

    similarity = WMT_AUDIO_MATCH_MAX_COST / (WMT_AUDIO_MATCH_MAX_COST + winner_cost)
    return AudioMatch(winner_label, winner_cost, similarity, winner_ref.wav_path.name, len(refs))


def clear_reference_cache() -> None:
    _load_references.cache_clear()
