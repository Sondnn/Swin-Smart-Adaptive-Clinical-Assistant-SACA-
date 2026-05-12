"""Unit tests for temperature scaling and rare-class filtering."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.train import (
    _apply_temperature as train_apply_temperature,
    _filter_rare_diseases,
    _fit_temperature,
    RARE_DISEASE_MIN,
)
from ml.predict_service import _apply_temperature as service_apply_temperature


# --------------------------------------------------------------------------- #
# _apply_temperature (training-side, 2-D)
# --------------------------------------------------------------------------- #

class TestApplyTemperatureTraining:
    def test_identity_when_T_is_one(self):
        probs = np.array([[0.1, 0.7, 0.2], [0.5, 0.25, 0.25]])
        out = train_apply_temperature(probs, T=1.0)
        np.testing.assert_allclose(out, probs, atol=1e-9)

    def test_rows_sum_to_one(self):
        probs = np.array([[0.1, 0.7, 0.2], [0.5, 0.25, 0.25]])
        for T in [0.3, 0.7, 1.5, 3.0]:
            out = train_apply_temperature(probs, T=T)
            np.testing.assert_allclose(out.sum(axis=1), 1.0, atol=1e-9)

    def test_low_T_sharpens(self):
        probs = np.array([[0.4, 0.35, 0.25]])
        sharpened = train_apply_temperature(probs, T=0.5)
        assert sharpened.max() > probs.max()

    def test_high_T_smooths(self):
        probs = np.array([[0.8, 0.15, 0.05]])
        smoothed = train_apply_temperature(probs, T=3.0)
        assert smoothed.max() < probs.max()

    def test_argmax_preserved(self):
        # Temperature scaling is monotonic — top class should be unchanged.
        probs = np.array([[0.1, 0.6, 0.3], [0.45, 0.4, 0.15]])
        for T in [0.2, 0.7, 1.5, 4.0]:
            out = train_apply_temperature(probs, T=T)
            np.testing.assert_array_equal(out.argmax(axis=1), probs.argmax(axis=1))

    def test_handles_zero_probabilities(self):
        # Should not produce NaN/inf even if a class has zero probability.
        probs = np.array([[0.0, 0.999, 0.001]])
        out = train_apply_temperature(probs, T=0.5)
        assert np.isfinite(out).all()
        np.testing.assert_allclose(out.sum(), 1.0, atol=1e-9)


# --------------------------------------------------------------------------- #
# _apply_temperature (service-side, 1-D)
# --------------------------------------------------------------------------- #

class TestApplyTemperatureService:
    def test_identity_when_T_is_one(self):
        proba = np.array([0.1, 0.7, 0.2])
        out = service_apply_temperature(proba, T=1.0)
        # Fast-path returns the same array.
        assert out is proba

    def test_sums_to_one(self):
        proba = np.array([0.1, 0.7, 0.2])
        for T in [0.3, 0.7, 1.5, 3.0]:
            out = service_apply_temperature(proba, T=T)
            np.testing.assert_allclose(out.sum(), 1.0, atol=1e-9)

    def test_low_T_increases_top_confidence(self):
        proba = np.array([0.4, 0.35, 0.25])
        out = service_apply_temperature(proba, T=0.5)
        assert out.max() > proba.max()

    def test_consistent_with_training_apply(self):
        # Service (1-D) and training (2-D) implementations must match.
        proba = np.array([0.05, 0.6, 0.25, 0.1])
        T = 0.4
        from_service = service_apply_temperature(proba, T)
        from_train = train_apply_temperature(proba.reshape(1, -1), T)[0]
        np.testing.assert_allclose(from_service, from_train, atol=1e-9)


# --------------------------------------------------------------------------- #
# _fit_temperature
# --------------------------------------------------------------------------- #

class TestFitTemperature:
    def test_overconfident_probs_yield_T_above_one(self):
        # Build over-confident model output: true label gets 0.95, others tiny.
        rng = np.random.default_rng(0)
        n, k = 200, 5
        y = rng.integers(0, k, size=n)
        probs = np.full((n, k), 0.05 / (k - 1))
        probs[np.arange(n), y] = 0.95
        # Flip 30% of true labels so the model is genuinely over-confident.
        flip = rng.choice(n, size=int(n * 0.3), replace=False)
        y[flip] = (y[flip] + 1) % k

        T = _fit_temperature(probs, y)
        assert T > 1.0, f"Expected T>1 to smooth over-confident probs, got {T}"

    def test_underconfident_probs_yield_T_below_one(self):
        # Build under-confident output: top class gets only slight margin.
        rng = np.random.default_rng(1)
        n, k = 200, 5
        y = rng.integers(0, k, size=n)
        probs = np.full((n, k), (1 - 0.3) / (k - 1))
        probs[np.arange(n), y] = 0.3
        # Model is mostly correct (top-1 acc ~100% by construction), so it
        # could afford to be more confident → expect T < 1.

        T = _fit_temperature(probs, y)
        assert T < 1.0, f"Expected T<1 to sharpen under-confident probs, got {T}"

    def test_returns_value_in_search_bounds(self):
        rng = np.random.default_rng(2)
        n, k = 50, 4
        probs = rng.dirichlet(np.ones(k), size=n)
        y = rng.integers(0, k, size=n)
        T = _fit_temperature(probs, y)
        assert 0.05 <= T <= 5.0


# --------------------------------------------------------------------------- #
# _filter_rare_diseases
# --------------------------------------------------------------------------- #

class TestFilterRareDiseases:
    def _make_data(self, label_counts: dict):
        rows = []
        for label, n in label_counts.items():
            rows.extend([label] * n)
        y = pd.Series(rows, name="disease")
        X = pd.DataFrame({"f1": np.arange(len(y)), "f2": np.arange(len(y)) * 2})
        groups = np.arange(len(y))
        return X, y, groups

    def test_drops_classes_below_threshold(self):
        X, y, groups = self._make_data({
            "common_a": RARE_DISEASE_MIN + 10,
            "common_b": RARE_DISEASE_MIN + 5,
            "rare": RARE_DISEASE_MIN - 1,
        })
        X_out, y_out, groups_out = _filter_rare_diseases(X, y, groups)

        assert "rare" not in set(y_out)
        assert set(y_out) == {"common_a", "common_b"}
        assert len(X_out) == len(y_out) == len(groups_out)

    def test_no_drop_when_all_classes_meet_threshold(self):
        X, y, groups = self._make_data({
            "a": RARE_DISEASE_MIN,
            "b": RARE_DISEASE_MIN + 100,
        })
        X_out, y_out, groups_out = _filter_rare_diseases(X, y, groups)

        assert len(y_out) == len(y)
        np.testing.assert_array_equal(groups_out, groups)

    def test_groups_stay_aligned_with_kept_rows(self):
        # Construct so each row's group_id == its position; after filtering
        # the surviving group_ids must match the surviving row positions.
        X, y, groups = self._make_data({
            "keep": RARE_DISEASE_MIN + 1,
            "drop": 2,
        })
        X_out, y_out, groups_out = _filter_rare_diseases(X, y, groups)

        kept_positions = np.where(y == "keep")[0]
        np.testing.assert_array_equal(groups_out, kept_positions)

    def test_indices_reset_after_drop(self):
        X, y, groups = self._make_data({
            "drop": 5,
            "keep": RARE_DISEASE_MIN + 3,
        })
        X_out, y_out, _ = _filter_rare_diseases(X, y, groups)
        # Both should be re-indexed from 0.
        assert list(X_out.index) == list(range(len(X_out)))
        assert list(y_out.index) == list(range(len(y_out)))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
