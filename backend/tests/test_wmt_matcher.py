"""Unit tests for the Walmadjari keyword matcher in nlp_service.

Covers the pure-logic layer only -- no audio, no Whisper. Each test calls
either `_wmt_best_option_match` (the generic scorer) or `_match_wmt_options`
(the per-question-id router) with synthetic transcripts that simulate what a
noisy STT pass would produce.
"""

import pytest

from nlp import nlp_service as svc


# ---------------------------------------------------------------------------
# _wmt_best_option_match -- generic scorer, returns (key|None, score)
# ---------------------------------------------------------------------------

class TestBestOptionMatch:
    def test_exact_match(self):
        key, score = svc._wmt_best_option_match("yapajarra", {"a": ["yapajarra"], "b": ["karli"]})
        assert key == "a"
        assert score == 100

    def test_match_inside_noisy_transcript(self):
        # partial_ratio should find the phrase embedded in surrounding noise
        key, _ = svc._wmt_best_option_match("umm yapajarra please", {"a": ["yapajarra"], "b": ["karli"]})
        assert key == "a"

    def test_close_misspelling_within_threshold(self):
        key, _ = svc._wmt_best_option_match("yapajara", {"a": ["yapajarra"]})
        assert key == "a"

    def test_rejects_below_threshold(self):
        key, _ = svc._wmt_best_option_match("totally different", {"a": ["yapajarra"]})
        assert key is None

    def test_empty_transcript_returns_none(self):
        key, _ = svc._wmt_best_option_match("", {"a": ["yapajarra"]})
        assert key is None

    def test_empty_options_returns_none(self):
        key, _ = svc._wmt_best_option_match("yapajarra", {})
        assert key is None

    def test_skips_empty_phrases(self):
        key, _ = svc._wmt_best_option_match("karli", {"a": [], "b": ["karli"]})
        assert key == "b"
        key, _ = svc._wmt_best_option_match("anything", {"a": []})
        assert key is None

    def test_picks_highest_scoring_option(self):
        options = {"low": ["karlarra-wana"], "mild": ["kujarra-wana"]}
        key, _ = svc._wmt_best_option_match("kujarra-wana", options)
        assert key == "mild"

    def test_case_insensitive(self):
        key, _ = svc._wmt_best_option_match("yapajarra", {"a": ["YapaJARRA"]})
        assert key == "a"

    def test_returns_none_when_rapidfuzz_unavailable(self, monkeypatch):
        monkeypatch.setattr(svc, "fuzz", None)
        key, _ = svc._wmt_best_option_match("yapajarra", {"a": ["yapajarra"]})
        assert key is None

    def test_margin_rejects_close_ties(self, monkeypatch):
        """Two options scoring within WMT_OPTION_MATCH_MARGIN of each other return None."""
        class StubFuzz:
            scores = {"option_a": 90, "option_b": 88}
            @classmethod
            def partial_ratio(cls, a, b):
                # cheat: read intended score from the phrase string itself
                for k, v in cls.scores.items():
                    if k in a or k in b:
                        return v
                return 0
        monkeypatch.setattr(svc, "fuzz", StubFuzz)
        monkeypatch.setattr(svc, "jellyfish", None)  # disable phonetic so scoring is pure stub
        key, _ = svc._wmt_best_option_match("transcript", {"a": ["option_a"], "b": ["option_b"]})
        assert key is None


# ---------------------------------------------------------------------------
# Phonetic matching -- regression-pins the v2 win
# ---------------------------------------------------------------------------

class TestPhoneticMatching:
    def test_phonetic_rescues_whisper_drift(self):
        """The actual case that motivated v2: macOS English TTS reading
        'kujarra wana' comes out of Whisper as 'kijeroana'. Char-fuzz scored
        50 (below threshold 75); metaphone scores ~86. Both sides encode to
        similar metaphone keys, so the matcher should now find it."""
        options = {"1": ["kujarra-wana"], "4": ["jukurra-wana"]}
        key, score = svc._wmt_best_option_match("kijeroana", options)
        assert key == "1"
        assert score >= svc.WMT_OPTION_MATCH_THRESHOLD

    def test_phonetic_does_not_match_unrelated_noise(self):
        key, _ = svc._wmt_best_option_match("totally unrelated talk", {"1": ["kujarra-wana"]})
        assert key is None

    def test_phonetic_encode_handles_punctuation(self):
        # Hyphens, capitalization, accents shouldn't break the encoder
        a = svc._phonetic_encode("Kujarra-Wana!")
        b = svc._phonetic_encode("kujarra wana")
        assert a == b

    def test_phonetic_encode_empty_string(self):
        assert svc._phonetic_encode("") == ""

    def test_phonetic_encode_returns_empty_when_jellyfish_missing(self, monkeypatch):
        monkeypatch.setattr(svc, "jellyfish", None)
        assert svc._phonetic_encode("kujarra wana") == ""


# ---------------------------------------------------------------------------
# _match_wmt_options -- per-question routing, returns (parsed|None, score)
# ---------------------------------------------------------------------------

class TestMatchWmtOptions:

    # --- gender (q=1) ------------------------------------------------------
    def test_gender_female(self):
        parsed, score = svc._match_wmt_options(1, "yapajarra")
        assert parsed == {"gender": "0"}
        assert score >= svc.WMT_OPTION_MATCH_THRESHOLD

    def test_gender_male(self):
        parsed, _ = svc._match_wmt_options(1, "karli karli")
        assert parsed == {"gender": "1"}

    def test_gender_prefer_not_to_say(self):
        parsed, _ = svc._match_wmt_options(1, "karra yimi-rna")
        assert parsed == {"gender": "2"}

    def test_gender_no_match(self):
        parsed, _ = svc._match_wmt_options(1, "completely unrelated text")
        assert parsed is None

    # --- age over 65 (q=2) -------------------------------------------------
    def test_age_over_65(self):
        parsed, _ = svc._match_wmt_options(2, "65 ngurra-wana karrinyanu-warlangu")
        assert parsed == {"age_over_65": "1"}

    def test_age_under_65(self):
        parsed, _ = svc._match_wmt_options(2, "65 ngurra-wana karrinyanu-wana")
        assert parsed == {"age_over_65": "0"}

    # --- severity (q=5) ----------------------------------------------------
    @pytest.mark.parametrize("phrase,expected", [
        ("kujarra-wana",     "1"),
        ("karlarra-wana",    "2"),
        ("yirrarni-wana",    "3"),
        ("jukurra-wana",     "4"),
        ("karlarra jukurra", "5"),
    ])
    def test_severity_all_levels(self, phrase, expected):
        parsed, _ = svc._match_wmt_options(5, phrase)
        assert parsed == {"symptom_severity": expected}

    # --- duration (q=6) ----------------------------------------------------
    def test_duration_less_than_day(self):
        parsed, _ = svc._match_wmt_options(6, "ngurra-wana kujarra")
        assert parsed == {"symptoms_duration": "0"}

    def test_duration_more_than_day(self):
        parsed, _ = svc._match_wmt_options(6, "ngurra-wana karlarra")
        assert parsed == {"symptoms_duration": "1"}

    def test_duration_unknown(self):
        parsed, _ = svc._match_wmt_options(6, "karra yimi")
        assert parsed == {"symptoms_duration": "2"}

    # --- yes/no (q=7 had_symptoms_before, q=9 had_contact) -----------------
    def test_had_symptoms_before_unknown(self):
        parsed, _ = svc._match_wmt_options(7, "karra yimi")
        assert parsed == {"had_symptoms_before": "2"}

    def test_had_contact_unknown(self):
        parsed, _ = svc._match_wmt_options(9, "karra yimi")
        assert parsed == {"had_contact": "2"}

    def test_yes_no_yes_returns_none_until_vocab_filled(self):
        # placeholder: source strings are still "(WMT) Yes" -- vocab list is
        # empty by design until a Walmadjari speaker reviews. This test pins
        # that contract so removing it intentionally trips a review.
        parsed, _ = svc._match_wmt_options(7, "yes please")
        assert parsed is None

    # --- chronic conditions (q=8, multi-select) ----------------------------
    def test_chronic_conditions_empty_vocab_returns_none(self):
        parsed, _ = svc._match_wmt_options(8, "anything")
        assert parsed is None

    def test_chronic_conditions_matches_when_vocab_populated(self, monkeypatch):
        patched = {
            **svc.WMT_OPTION_VOCAB,
            "chronic_conditions": {
                "hypertension":      ["nyurra-pressure"],
                "type_2_diabetes":   ["ngarrku-sugar"],
                "heart_disease":     [],
                "asthma_copd":       [],
                "depression_anxiety": [],
            },
        }
        monkeypatch.setattr(svc, "WMT_OPTION_VOCAB", patched)
        parsed, score = svc._match_wmt_options(8, "nyurra-pressure and also ngarrku-sugar")
        assert parsed == {"chronic_conditions": {"hypertension", "type_2_diabetes"}}
        assert score >= svc.WMT_OPTION_MATCH_THRESHOLD

    # --- routing -----------------------------------------------------------
    def test_unknown_question_id_returns_none(self):
        parsed, _ = svc._match_wmt_options(999, "yapajarra")
        assert parsed is None

    def test_question_3_symptoms_not_routed_here(self):
        parsed, _ = svc._match_wmt_options(3, "ngalak")
        assert parsed is None


# ---------------------------------------------------------------------------
# Threshold + margin -- pin the tuning so silent drift gets caught
# ---------------------------------------------------------------------------

class TestThreshold:
    def test_threshold_value(self):
        assert svc.WMT_OPTION_MATCH_THRESHOLD == 75

    def test_margin_value(self):
        assert svc.WMT_OPTION_MATCH_MARGIN == 5

    def test_score_just_above_threshold_matches(self, monkeypatch):
        class StubFuzz:
            @staticmethod
            def partial_ratio(a, b):
                return svc.WMT_OPTION_MATCH_THRESHOLD + 1
        monkeypatch.setattr(svc, "fuzz", StubFuzz)
        monkeypatch.setattr(svc, "jellyfish", None)
        key, _ = svc._wmt_best_option_match("x", {"a": ["x"]})
        assert key == "a"

    def test_score_just_below_threshold_rejected(self, monkeypatch):
        class StubFuzz:
            @staticmethod
            def partial_ratio(a, b):
                return svc.WMT_OPTION_MATCH_THRESHOLD - 1
        monkeypatch.setattr(svc, "fuzz", StubFuzz)
        monkeypatch.setattr(svc, "jellyfish", None)
        key, _ = svc._wmt_best_option_match("x", {"a": ["x"]})
        assert key is None
