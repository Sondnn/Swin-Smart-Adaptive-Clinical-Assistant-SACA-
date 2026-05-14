from __future__ import annotations

import os
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Optional


class WalmadjariTranscriber(ABC):
    @abstractmethod
    def transcribe(self, wav_path: str) -> str:
        ...


class WhisperTranscriber(WalmadjariTranscriber):
    def __init__(self, model_size: Optional[str] = None):
        self._model_size = model_size or os.environ.get("WMT_WHISPER_MODEL", "base")
        self._model = None

    def _ensure_model(self):
        if self._model is not None:
            return
        from faster_whisper import WhisperModel
        self._model = WhisperModel(self._model_size, device="cpu", compute_type="int8")

    def transcribe(self, wav_path: str) -> str:
        self._ensure_model()
        segments, _info = self._model.transcribe(wav_path, language=None, beam_size=1)
        return " ".join(seg.text for seg in segments).strip().lower()


class PhonemeTranscriber(WalmadjariTranscriber):
    DEFAULT_MODEL = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"

    def __init__(self, model_name: Optional[str] = None):
        self._model_name = model_name or os.environ.get("WMT_PHONEME_MODEL", self.DEFAULT_MODEL)
        self._processor = None
        self._model = None

    def _ensure_model(self):
        if self._model is not None:
            return
        from transformers import AutoProcessor, AutoModelForCTC
        self._processor = AutoProcessor.from_pretrained(self._model_name)
        self._model = AutoModelForCTC.from_pretrained(self._model_name)

    def transcribe(self, wav_path: str) -> str:
        import torch
        import soundfile as sf
        self._ensure_model()
        audio, sample_rate = sf.read(wav_path)
        if sample_rate != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
        inputs = self._processor(audio, sampling_rate=16000, return_tensors="pt")
        with torch.no_grad():
            logits = self._model(inputs.input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcript = self._processor.batch_decode(predicted_ids)[0]
        return transcript.strip().lower()


@lru_cache(maxsize=1)
def get_transcriber() -> WalmadjariTranscriber:
    backend = os.environ.get("WMT_ASR_BACKEND", "whisper").lower()
    if backend == "phoneme":
        return PhonemeTranscriber()
    return WhisperTranscriber()


def transcribe_walmadjari(wav_path: str) -> str:
    return get_transcriber().transcribe(wav_path)
