from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import pytest

from nlp import wmt_audio_matcher as m


def _write_tone(path: Path, freq: float, seconds: float = 1.0, sample_rate: int = 16000):
    n = int(seconds * sample_rate)
    samples = (
        int(0.4 * 32767 * math.sin(2 * math.pi * freq * i / sample_rate))
        for i in range(n)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(struct.pack("<h", s) for s in samples))


def _write_noise(path: Path, seconds: float = 1.0, sample_rate: int = 16000):
    import random
    n = int(seconds * sample_rate)
    rng = random.Random(0)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(
            # Gaussian samples can exceed ±1; clip to int16 range
            struct.pack("<h", max(-32767, min(32767, int(rng.gauss(0, 0.3) * 32767))))
            for _ in range(n)
        ))


@pytest.fixture
def fake_refs(tmp_path, monkeypatch):
    refs_root = tmp_path / "wmt_references"
    _write_tone(refs_root / "99" / "a" / "tone.wav", freq=220.0)
    _write_tone(refs_root / "99" / "b" / "tone.wav", freq=1000.0)
    _write_tone(refs_root / "99" / "c" / "tone.wav", freq=3000.0)
    monkeypatch.setattr(m, "REFERENCES_DIR", refs_root)
    m.clear_reference_cache()
    return refs_root


class TestAudioMatcher:
    def test_no_references_returns_empty_match(self, tmp_path, monkeypatch):
        empty_dir = tmp_path / "nothing"
        monkeypatch.setattr(m, "REFERENCES_DIR", empty_dir)
        m.clear_reference_cache()
        # Need a query wav to call match_audio
        query = tmp_path / "q.wav"
        _write_tone(query, freq=440.0)
        result = m.match_audio(str(query), question_id=99)
        assert result.answer_key is None
        assert result.refs_considered == 0

    def test_exact_self_match(self, fake_refs, tmp_path):
        """A query identical to a reference should resolve to that reference."""
        query = tmp_path / "q.wav"
        _write_tone(query, freq=220.0)  # same as 'a'
        result = m.match_audio(str(query), question_id=99)
        assert result.answer_key == "a"
        assert result.similarity > 0.5
        assert result.matched_reference == "tone.wav"

    def test_ambiguous_close_match_rejected_by_margin(self, fake_refs, tmp_path):
        query = tmp_path / "q.wav"
        _write_tone(query, freq=950.0)
        result = m.match_audio(str(query), question_id=99)
        assert result.answer_key is None
        # Best raw cost is reported for logging
        assert result.cost > 0

    def test_noise_query_is_rejected(self, fake_refs, tmp_path):
        query = tmp_path / "noise.wav"
        _write_noise(query)
        result = m.match_audio(str(query), question_id=99)
        if result.answer_key is not None:
            assert result.similarity < 0.5

    def test_query_with_no_audio_returns_none(self, fake_refs, tmp_path):
        query = tmp_path / "silent.wav"
        with wave.open(str(query), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b"\x00\x00" * 160)
        result = m.match_audio(str(query), question_id=99)
        assert result.answer_key is None

    def test_unknown_question_id_returns_empty(self, fake_refs, tmp_path):
        query = tmp_path / "q.wav"
        _write_tone(query, freq=220.0)
        result = m.match_audio(str(query), question_id=12345)
        assert result.answer_key is None
        assert result.refs_considered == 0


class TestThresholds:
    def test_max_cost_constant_pinned(self):
        assert m.WMT_AUDIO_MATCH_MAX_COST == 35.0

    def test_margin_ratio_pinned(self):
        assert m.WMT_AUDIO_MATCH_MARGIN_RATIO == 0.10

    def test_above_threshold_cost_rejected(self, fake_refs, tmp_path, monkeypatch):
        monkeypatch.setattr(m, "WMT_AUDIO_MATCH_MAX_COST", 0.01)
        query = tmp_path / "q.wav"
        _write_tone(query, freq=440.0)  # not in the reference set
        result = m.match_audio(str(query), question_id=99)
        assert result.answer_key is None


class TestReferenceLoading:
    def test_skips_non_wav_files(self, tmp_path, monkeypatch):
        refs = tmp_path / "wmt_references"
        _write_tone(refs / "99" / "a" / "real.wav", freq=440.0)
        (refs / "99" / "a" / "notes.txt").write_text("ignored")
        (refs / "99" / "README.md").write_text("ignored")  # not under an answer dir
        monkeypatch.setattr(m, "REFERENCES_DIR", refs)
        m.clear_reference_cache()
        loaded = m._load_references(99)
        assert len(loaded) == 1
        assert loaded[0].wav_path.name == "real.wav"

    def test_multiple_refs_per_answer(self, tmp_path, monkeypatch):
        refs = tmp_path / "wmt_references"
        _write_tone(refs / "99" / "a" / "take1.wav", freq=440.0)
        _write_tone(refs / "99" / "a" / "take2.wav", freq=460.0)
        _write_tone(refs / "99" / "b" / "take1.wav", freq=1800.0)
        monkeypatch.setattr(m, "REFERENCES_DIR", refs)
        m.clear_reference_cache()
        loaded = m._load_references(99)
        assert len(loaded) == 3
        a_refs = [r for r in loaded if r.answer_key == "a"]
        assert len(a_refs) == 2
