import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

from pydantic import BaseModel

from ml.symptom_clusters import SCENARIOS

SYMPTOM_PREFIX = "symptom__"
MAX_SUGGESTIONS = 5
EXCLUDED_SYMPTOMS = {"symptom__otherwise_well"}


class SuggestSymptomsRequest(BaseModel):
    chosen_symptom: str

    model_config = {
        "json_schema_extra": {
            "example": {"chosen_symptom": "chest_pain"}
        }
    }


class SuggestSymptomsResponse(BaseModel):
    chosen_symptom: str
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
        feature_list = json.loads((self.models_dir / "feature_columns.json").read_text())
        self.feature_columns = {
            c for c in feature_list
            if c.startswith(SYMPTOM_PREFIX) and c not in EXCLUDED_SYMPTOMS
        }

        neighbours: Dict[str, Set[str]] = defaultdict(set)
        for cluster in SCENARIOS:
            members = [s for s in cluster if s in self.feature_columns]
            for s in members:
                neighbours[s].update(other for other in members if other != s)
        self.cluster_neighbours = {k: sorted(v) for k, v in neighbours.items()}

        self.cooccurrence = self._build_cooccurrence()
        self._loaded = True

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

        key = SYMPTOM_PREFIX + payload.chosen_symptom
        if key not in self.feature_columns:
            return SuggestSymptomsResponse(
                chosen_symptom=payload.chosen_symptom,
                suggested_symptoms=[],
            )

        ordered: List[str] = []
        seen: Set[str] = {key}
        for s in self.cluster_neighbours.get(key, []):
            if s not in seen:
                ordered.append(s)
                seen.add(s)
                if len(ordered) >= MAX_SUGGESTIONS:
                    break

        if len(ordered) < MAX_SUGGESTIONS:
            for s in self.cooccurrence.get(key, []):
                if s not in seen:
                    ordered.append(s)
                    seen.add(s)
                    if len(ordered) >= MAX_SUGGESTIONS:
                        break

        return SuggestSymptomsResponse(
            chosen_symptom=payload.chosen_symptom,
            suggested_symptoms=[s.removeprefix(SYMPTOM_PREFIX) for s in ordered],
        )
