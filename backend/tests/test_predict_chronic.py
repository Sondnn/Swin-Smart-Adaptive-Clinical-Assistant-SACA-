"""BE-08 — Predict: chronic conditions influence the triage probability distribution.

Submitting the same symptoms once without chronic conditions and once with
["hypertension", "type2_diabetes"] must:
  * both return HTTP 200, and
  * produce different probability distributions, where the chronic version
    skews toward higher acuity (more probability mass on lower-numbered,
    more-urgent POPGUNS categories).

Note: the original UAT payload also set escalation_triggers=["chest_pain"].
Escalation triggers now force Category 1, which would override and mask the
chronic effect, so the chronic-influence assertions use no escalation trigger.
A separate test documents the escalation override.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

# Same symptoms/context for both calls; only chronic_conditions changes.
BASE_PAYLOAD = {
    "gender": 1,
    "age_over_65": 0,
    "symptom_severity": 3,
    "symptoms_duration": 2,
    "symptoms": ["fever", "cough"],
    "escalation_triggers": [],
    "had_symptoms_before": 0,
    "had_contact": 1,
}
CHRONIC = ["hypertension", "type2_diabetes"]


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def _category(key: str) -> int:
    # "category_3" -> 3
    return int(key.split("_")[1])


def _prob_at_or_above_acuity(probs: dict, max_category: int) -> float:
    """Total probability on categories <= max_category (more urgent)."""
    return sum(v for k, v in probs.items() if _category(k) <= max_category)


def _expected_category(probs: dict) -> float:
    """Probability-weighted mean category. Lower = more acute."""
    return sum(_category(k) * v for k, v in probs.items())


def _predict(client: TestClient, chronic: list[str]) -> dict:
    resp = client.post(
        "/predict", json={**BASE_PAYLOAD, "chronic_conditions": chronic}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


class TestChronicConditionsInfluence:
    def test_both_requests_succeed(self, client):
        without = _predict(client, [])
        with_chronic = _predict(client, CHRONIC)
        for body in (without, with_chronic):
            assert "probabilities" in body
            assert pytest.approx(sum(body["probabilities"].values()), abs=1e-3) == 1.0
        # Echoed back correctly.
        assert without["input_summary"]["chronic_conditions"] == []
        assert with_chronic["input_summary"]["chronic_conditions"] == CHRONIC

    def test_distribution_differs(self, client):
        without = _predict(client, [])["probabilities"]
        with_chronic = _predict(client, CHRONIC)["probabilities"]
        assert without != with_chronic

    def test_chronic_skews_to_higher_acuity(self, client):
        without = _predict(client, [])["probabilities"]
        with_chronic = _predict(client, CHRONIC)["probabilities"]

        # More probability mass on urgent categories (<= 4) with chronic.
        assert _prob_at_or_above_acuity(with_chronic, 4) > _prob_at_or_above_acuity(without, 4)
        # Lower probability-weighted mean category with chronic (more acute).
        assert _expected_category(with_chronic) < _expected_category(without)


class TestEscalationOverridesChronic:
    """Documents that an escalation red flag forces Category 1 regardless of chronic."""

    def test_escalation_forces_category_1(self, client):
        payload = {**BASE_PAYLOAD, "escalation_triggers": ["chest_pain"]}
        for chronic in ([], CHRONIC):
            resp = client.post("/predict", json={**payload, "chronic_conditions": chronic})
            assert resp.status_code == 200, resp.text
            assert resp.json()["triage_category"] == 1
