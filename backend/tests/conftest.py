import sys
from pathlib import Path

# Make `backend/` importable so tests can do `from nlp.nlp_service import ...`
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
