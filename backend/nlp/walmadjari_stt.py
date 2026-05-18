from __future__ import annotations

import os
from functools import lru_cache


class WhisperTranscriber:
    def __init__(self, model_size: str | None = None):
        self._model_size = model_size or os.environ.get("WMT_WHISPER_MODEL", "base")
        self._model = None

    def _ensure_model(self):
        if self._model is not None:
            return
        from faster_whisper import WhisperModel  # lazy
        self._model = WhisperModel(self._model_size, device="cpu", compute_type="int8")

    def transcribe(self, wav_path: str) -> str:
        self._ensure_model()
        segments, _info = self._model.transcribe(wav_path, language="en", beam_size=1)
        return " ".join(seg.text for seg in segments).strip().lower()


@lru_cache(maxsize=1)
def get_transcriber() -> WhisperTranscriber:
    return WhisperTranscriber()


def transcribe_walmadjari(wav_path: str) -> str:
    return get_transcriber().transcribe(wav_path)
