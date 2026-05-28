import csv
import json
import logging
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

from fastapi import HTTPException
from pydantic import BaseModel

from ml.symptom_clusters import SCENARIOS

logger = logging.getLogger(__name__)

SYMPTOM_PREFIX = "symptom__"
MAX_SUGGESTIONS = 10
EXCLUDED_SYMPTOMS = {"symptom__otherwise_well"}


class SuggestSymptomsRequest(BaseModel):
    chosen_symptom: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {"chosen_symptom": ["chest_pain", "breathing_difficulty"]}
        }
    }


class SuggestSymptomsResponse(BaseModel):
    chosen_symptom: List[str]
    suggested_symptoms: List[str]


class SymptomSuggestionService:
    def __init__(self, models_dir: Path, training_csv: Path):
        self.models_dir = models_dir
        self.training_csv = training_csv
        self.feature_columns: Set[str] = set()
        self.cluster_neighbours: Dict[str, List[str]] = {}
        self.cooccurrence: Dict[str, List[str]] = {}
        self._loaded = False

    def load(self):
        feature_list = json.loads((self.models_dir / "model_features.json").read_text())
        self.feature_columns = {
            c for c in feature_list
            if c.startswith(SYMPTOM_PREFIX) and c not in EXCLUDED_SYMPTOMS
        }

        # For every cluster in `SCENARIOS`, every member maps to other members of every cluster it appears in.
        neighbours: Dict[str, Set[str]] = defaultdict(set)
        for name, cluster in SCENARIOS.items():
            unknown = [s for s in cluster if s not in self.feature_columns]
            if unknown:
                logger.warning(
                    "symptom_clusters: scenario %r references %d symptom(s) not in model_features.json: %s",
                    name, len(unknown), unknown,
                )
            members = [s for s in cluster if s in self.feature_columns]
            for s in members:
                neighbours[s].update(other for other in members if other != s)
        self.cluster_neighbours = {k: sorted(v) for k, v in neighbours.items()}

        self.cooccurrence = self._build_cooccurrence()
        self._loaded = True

    # Listed of other symptoms ranked by how often they appear in the same training row
    # The quality depend heavily on the quality of the training data, but it can capture relationships that cluster-based suggestions miss.
    def _build_cooccurrence(self) -> Dict[str, List[str]]:
        with self.training_csv.open(newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            symptom_idx = [(i, name) for i, name in enumerate(header) if name in self.feature_columns]

            counters: Dict[str, Counter] = defaultdict(Counter)
            for row in reader:
                present = [name for i, name in symptom_idx if row[i] == "1"]
                for a in present:
                    for b in present:
                        if a != b:
                            counters[a][b] += 1

        return {
            symptom: [other for other, _ in counter.most_common()]
            for symptom, counter in counters.items()
        }

    def suggest(self, payload: SuggestSymptomsRequest) -> SuggestSymptomsResponse:
        if not self._loaded:
            self.load()

        # BE-15: empty input is a client error, not an empty result.
        if not payload.chosen_symptom:
            raise HTTPException(
                status_code=422,
                detail="chosen_symptom must contain at least one symptom.",
            )

        # BE-16: unrecognised symptoms are a client error, not an empty result.
        invalid = [
            s for s in payload.chosen_symptom
            if (SYMPTOM_PREFIX + s) not in self.feature_columns
        ]
        if invalid:
            raise HTTPException(
                status_code=422,
                detail=f"Unrecognised symptom(s): {invalid}.",
            )

        valid_keys = [SYMPTOM_PREFIX + s for s in payload.chosen_symptom]

        ordered: List[str] = []
        seen: Set[str] = set(valid_keys)

        # Pass 1: cluster mates from every input symptom
        for key in valid_keys:
            for s in self.cluster_neighbours.get(key, []):
                if s not in seen:
                    ordered.append(s)
                    seen.add(s)
                    if len(ordered) >= MAX_SUGGESTIONS:
                        break
            if len(ordered) >= MAX_SUGGESTIONS:
                break

        # Pass 2: co-occurrence top-up if clusters didn't fill
        if len(ordered) < MAX_SUGGESTIONS:
            for key in valid_keys:
                for s in self.cooccurrence.get(key, []):
                    if s not in seen:
                        ordered.append(s)
                        seen.add(s)
                        if len(ordered) >= MAX_SUGGESTIONS:
                            break
                if len(ordered) >= MAX_SUGGESTIONS:
                    break

        return SuggestSymptomsResponse(
            chosen_symptom=payload.chosen_symptom,
            suggested_symptoms=[s.removeprefix(SYMPTOM_PREFIX) for s in ordered],
        )
