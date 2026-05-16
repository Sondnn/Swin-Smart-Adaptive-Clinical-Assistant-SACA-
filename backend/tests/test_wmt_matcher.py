"""Unit tests for the Walmadjari keyword matcher in nlp_service.

Covers the pure-logic layer only -- no audio, no Whisper. Each test calls
either `_wmt_best_option_match` (the generic scorer) or `_match_wmt_options`
(the per-question-id router) with synthetic transcripts that simulate what a
noisy STT pass would produce.
"""

import pytest

from nlp import nlp_service as svc


# ---------------------------------------------------------------------------
# _wmt_best_option_match -- generic scorer
# ---------------------------------------------------------------------------

class TestBestOptionMatch:
    def test_exact_match(self):
        options = {"a": ["yapajarra"], "b": ["karli"]}
        assert svc._wmt_best_option_match("yapajarra", options) == "a"

    def test_match_inside_noisy_transcript(self):
        # partial_ratio should find the phrase embedded in surrounding noise
        options = {"a": ["yapajarra"], "b": ["karli"]}
        assert svc._wmt_best_option_match("umm yapajarra please", options) == "a"

    def test_close_misspelling_within_threshold(self):
        options = {"a": ["yapajarra"]}
        # single dropped char -- still well above threshold
        assert svc._wmt_best_option_match("yapajara", options) == "a"

    def test_rejects_below_threshold(self):
        options = {"a": ["yapajarra"]}
        assert svc._wmt_best_option_match("totally different", options) is None

    def test_empty_transcript_returns_none(self):
        options = {"a": ["yapajarra"]}
        assert svc._wmt_best_option_match("", options) is None

    def test_empty_options_returns_none(self):
        assert svc._wmt_best_option_match("yapajarra", {}) is None

    def test_skips_empty_phrases(self):
        # entries with [] (placeholder vocab) must not cause a crash or false match
        options = {"a": [], "b": ["karli"]}
        assert svc._wmt_best_option_match("karli", options) == "b"
        assert svc._wmt_best_option_match("anything", {"a": []}) is None

    def test_picks_highest_scoring_option(self):
        options = {
            "low":  ["karlarra-wana"],
            "mild": ["kujarra-wana"],
        }
        # transcript is exactly "kujarra-wana" -- should beat "karlarra-wana"
        assert svc._wmt_best_option_match("kujarra-wana", options) == "mild"

    def test_case_insensitive(self):
        options = {"a": ["YapaJARRA"]}
        assert svc._wmt_best_option_match("yapajarra", options) == "a"

    def test_returns_none_when_rapidfuzz_unavailable(self, monkeypatch):
        monkeypatch.setattr(svc, "fuzz", None)
        assert svc._wmt_best_option_match("yapajarra", {"a": ["yapajarra"]}) is None


# ---------------------------------------------------------------------------
# _match_wmt_options -- per-question routing
# ---------------------------------------------------------------------------

class TestMatchWmtOptions:

    # --- gender (q=1) ------------------------------------------------------
    def test_gender_female(self):
        assert svc._match_wmt_options(1, "yapajarra") == {"gender": "0"}

    def test_gender_male(self):
        assert svc._match_wmt_options(1, "karli karli") == {"gender": "1"}

    def test_gender_prefer_not_to_say(self):
        assert svc._match_wmt_options(1, "karra yimi-rna") == {"gender": "2"}

    def test_gender_no_match(self):
        assert svc._match_wmt_options(1, "completely unrelated text") is None

    # --- age over 65 (q=2) -------------------------------------------------
    def test_age_over_65(self):
        assert svc._match_wmt_options(
            2, "65 ngurra-wana karrinyanu-warlangu"
        ) == {"age_over_65": "1"}

    def test_age_under_65(self):
        assert svc._match_wmt_options(
            2, "65 ngurra-wana karrinyanu-wana"
        ) == {"age_over_65": "0"}

    # --- severity (q=5) ----------------------------------------------------
    @pytest.mark.parametrize("phrase,expected", [
        ("kujarra-wana",     "1"),
        ("karlarra-wana",    "2"),
        ("yirrarni-wana",    "3"),
        ("jukurra-wana",     "4"),
        ("karlarra jukurra", "5"),
    ])
    def test_severity_all_levels(self, phrase, expected):
        assert svc._match_wmt_options(5, phrase) == {"symptom_severity": expected}

    # --- duration (q=6) ----------------------------------------------------
    def test_duration_less_than_day(self):
        assert svc._match_wmt_options(6, "ngurra-wana kujarra") == {"symptoms_duration": "0"}

    def test_duration_more_than_day(self):
        assert svc._match_wmt_options(6, "ngurra-wana karlarra") == {"symptoms_duration": "1"}

    def test_duration_unknown(self):
        assert svc._match_wmt_options(6, "karra yimi") == {"symptoms_duration": "2"}

    # --- yes/no (q=7 had_symptoms_before, q=9 had_contact) -----------------
    def test_had_symptoms_before_unknown(self):
        assert svc._match_wmt_options(7, "karra yimi") == {"had_symptoms_before": "2"}

    def test_had_contact_unknown(self):
        assert svc._match_wmt_options(9, "karra yimi") == {"had_contact": "2"}

    def test_yes_no_yes_returns_none_until_vocab_filled(self):
        # placeholder: source strings are still "(WMT) Yes" -- vocab list is
        # empty by design until a Walmadjari speaker reviews. This test pins
        # that contract so removing it intentionally trips a review.
        assert svc._match_wmt_options(7, "yes please") is None

    # --- chronic conditions (q=8, multi-select) ----------------------------
    def test_chronic_conditions_empty_vocab_returns_none(self):
        # all chronic_conditions phrase lists are empty placeholders today
        assert svc._match_wmt_options(8, "anything") is None

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
        result = svc._match_wmt_options(8, "nyurra-pressure and also ngarrku-sugar")
        assert result == {"chronic_conditions": {"hypertension", "type_2_diabetes"}}

    # --- routing -----------------------------------------------------------
    def test_unknown_question_id_returns_none(self):
        assert svc._match_wmt_options(999, "yapajarra") is None

    def test_question_3_symptoms_not_routed_here(self):
        # q=3 (symptoms) goes through the English dict + parser path, not the
        # option-vocab fallback. The fallback router should not handle it.
        assert svc._match_wmt_options(3, "ngalak") is None


# ---------------------------------------------------------------------------
# Threshold boundary -- pins the tuning so silent drift gets caught
# ---------------------------------------------------------------------------

class TestThreshold:
    def test_threshold_value(self):
        # If this constant changes, every parametrized score above may shift.
        # Update tests deliberately rather than letting a tweak slide through.
        assert svc.WMT_OPTION_MATCH_THRESHOLD == 75

    def test_score_just_above_threshold_matches(self, monkeypatch):
        class StubFuzz:
            @staticmethod
            def partial_ratio(a, b):
                return svc.WMT_OPTION_MATCH_THRESHOLD + 1
        monkeypatch.setattr(svc, "fuzz", StubFuzz)
        assert svc._wmt_best_option_match("x", {"a": ["x"]}) == "a"

    def test_score_just_below_threshold_rejected(self, monkeypatch):
        class StubFuzz:
            @staticmethod
            def partial_ratio(a, b):
                return svc.WMT_OPTION_MATCH_THRESHOLD - 1
        monkeypatch.setattr(svc, "fuzz", StubFuzz)
        assert svc._wmt_best_option_match("x", {"a": ["x"]}) is None
