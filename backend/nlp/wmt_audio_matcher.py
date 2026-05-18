"""Audio-to-audio matching for Walmadjari fixed-answer questions.
Reference directory layout:
    backend/data/wmt_references/
        <question_id>/
            <answer_code>/
                anything.wav
                another.wav
        ...
Example:
    backend/data/wmt_references/
        1/0/female.wav          # gender = female
        1/1/male.wav            # gender = male
        1/2/prefer_not.wav      # gender = prefer not to say
        5/1/mild.wav            # symptom_severity = 1 (mild)
        5/5/severe.wav          # symptom_severity = 5 (severe)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

REFERENCES_DIR = Path(os.environ.get(
    "WMT_REFERENCES_DIR",
    str(Path(__file__).resolve().parents[1] / "data" / "wmt_references"),
))

SAMPLE_RATE = 16000

WMT_AUDIO_MATCH_MAX_COST = 35.0

WMT_AUDIO_MATCH_MARGIN_RATIO = 0.10


@dataclass
class AudioMatch:
    answer_key: Optional[str]
    cost: float
    similarity: float
    matched_reference: str
    refs_considered: int


def _extract_mfcc(wav_path: str):
    try:
        import librosa  # lazy
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
    answer_key: str
    wav_path: Path
    mfcc: object


@lru_cache(maxsize=32)
def _load_references(question_id: int) -> tuple[_Reference, ...]:
    q_dir = REFERENCES_DIR / str(question_id)
    if not q_dir.is_dir():
        return ()
    refs: list[_Reference] = []
    for answer_dir in sorted(q_dir.iterdir()):
        if not answer_dir.is_dir():
            continue
        for wav in sorted(answer_dir.glob("*.wav")):
            mfcc = _extract_mfcc(str(wav))
            if mfcc is None or mfcc.shape[1] < 5:
                continue
            refs.append(_Reference(answer_key=answer_dir.name, wav_path=wav, mfcc=mfcc))
    return tuple(refs)


def match_audio(wav_path: str, question_id: int) -> AudioMatch:
    refs = _load_references(question_id)
    if not refs:
        return AudioMatch(None, 0.0, 0.0, "", 0)

    query_mfcc = _extract_mfcc(wav_path)
    if query_mfcc is None or query_mfcc.shape[1] < 5:
        return AudioMatch(None, 0.0, 0.0, "", len(refs))

    try:
        import librosa  # lazy
    except ImportError:
        return AudioMatch(None, 0.0, 0.0, "", len(refs))

    per_ref_cost: list[tuple[_Reference, float]] = []
    for ref in refs:
        D, _ = librosa.sequence.dtw(X=ref.mfcc, Y=query_mfcc, metric="euclidean")
        path_len = D.shape[0] + D.shape[1]
        cost = float(D[-1, -1]) / max(1, path_len)
        per_ref_cost.append((ref, cost))

    best_per_answer: dict[str, tuple[_Reference, float]] = {}
    for ref, cost in per_ref_cost:
        if ref.answer_key not in best_per_answer or cost < best_per_answer[ref.answer_key][1]:
            best_per_answer[ref.answer_key] = (ref, cost)

    ranked = sorted(best_per_answer.items(), key=lambda kv: kv[1][1])
    winner_key, (winner_ref, winner_cost) = ranked[0]
    runner_cost = ranked[1][1][1] if len(ranked) > 1 else float("inf")

    if winner_cost > WMT_AUDIO_MATCH_MAX_COST:
        return AudioMatch(None, winner_cost, 0.0, winner_ref.wav_path.name, len(refs))

    if runner_cost != float("inf") and winner_cost > 1e-6:
        if runner_cost / winner_cost < 1.0 + WMT_AUDIO_MATCH_MARGIN_RATIO:
            return AudioMatch(None, winner_cost, 0.0, winner_ref.wav_path.name, len(refs))

    similarity = WMT_AUDIO_MATCH_MAX_COST / (WMT_AUDIO_MATCH_MAX_COST + winner_cost)
    return AudioMatch(winner_key, winner_cost, similarity, winner_ref.wav_path.name, len(refs))


def clear_reference_cache() -> None:
    _load_references.cache_clear()
