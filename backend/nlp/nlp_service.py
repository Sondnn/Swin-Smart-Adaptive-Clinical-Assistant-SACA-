from typing import List
from collections.abc import Iterable
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import warnings
import wave

from pydantic import BaseModel

try:
    import speech_recognition as sr
except ImportError:
    sr = None

from config import MODEL_FEATURES_FILE
from nlp.walmadjari_stt import transcribe_walmadjari

WMT_EN_DICT_FILE = Path(__file__).resolve().with_name("wmt_en_dict.json")
WMT_LOG_PATH = Path(os.environ.get(
    "WMT_LOG_PATH",
    str(Path(__file__).resolve().parents[1] / "logs" / "wmt_transcripts.jsonl"),
))

# Language codes:
#   1 = English (en-AU) -- handled by Google STT
#   0 = Walmadjari -- fixed-answer questions go through audio matching (see
#       nlp/wmt_audio_matcher.py); free-form symptoms (q=3) go through Whisper
#       + word translation.
LANGUAGE_MAP = {
    1: "en-AU",
    0: "wmt",
}


def load_wmt_en_dict() -> dict:
    try:
        return json.loads(WMT_EN_DICT_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


WMT_EN_DICT = load_wmt_en_dict()


FALLBACK_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "or", "that",
    "the", "to", "was", "were", "will", "with",
}


class ExtractSymptomsRequest(BaseModel):
    language: int = 1
    symptoms_description: str = ""
    symptoms: List[str] = []


class ExtractSymptomsResponse(BaseModel):
    symptoms_description: str
    extracted_symptoms: List[str]
    negated_symptoms: List[str]
    symptoms: List[str]


def build_symptom_patterns(feature_columns: Iterable[str]) -> dict[str, list[str]]:
    symptom_patterns: dict[str, list[str]] = {}
    for column in feature_columns:
        if not column.startswith("symptom__"):
            continue
        phrase = column.removeprefix("symptom__").replace("_", " ").strip()
        if not phrase:
            continue
        symptom_key = column.removeprefix("symptom__")
        symptom_patterns[symptom_key] = [phrase]
    return symptom_patterns


def load_symptom_patterns() -> dict[str, list[str]]:
    feature_columns = json.loads(MODEL_FEATURES_FILE.read_text())
    return build_symptom_patterns(feature_columns)


SYMPTOM_PATTERNS = load_symptom_patterns()


def load_spacy_components():
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.",
                category=UserWarning,
            )
            import spacy
        nlp = spacy.blank("en")
        stopwords = set(nlp.Defaults.stop_words)
        return nlp, stopwords
    except Exception:
        return None, FALLBACK_STOPWORDS


def load_nltk_components():
    try:
        from nltk.stem import PorterStemmer
        from nltk.tokenize import TreebankWordTokenizer
        return TreebankWordTokenizer(), PorterStemmer()
    except Exception:
        return None, None


# NLP components initialized once at module load
_nlp, _stopwords = load_spacy_components()
_tokenizer, _stemmer = load_nltk_components()


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text)

def translate_indigenous_to_english(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"Expected text to be str, got {type(text).__name__}")
    if not WMT_EN_DICT:
        return text

    translated_text = text
    for english_word, indigenous_words in WMT_EN_DICT.items():
        candidates = indigenous_words if isinstance(indigenous_words, list) else [indigenous_words]
        for indigenous_word in candidates:
            translated_text = re.sub(
                r"\b" + re.escape(indigenous_word) + r"\b",
                english_word,
                translated_text,
                flags=re.IGNORECASE,
            )

    return translated_text

def tokenize_with_spacy(nlp, text: str) -> list[str]:
    if nlp is None:
        return []
    doc = nlp(text)
    return [token.text for token in doc if not token.is_space]


def tokenize_with_nltk(tokenizer, text: str) -> list[str]:
    if tokenizer is None:
        return text.split()
    return [token.lower() for token in tokenizer.tokenize(text)]


def stem_tokens(tokens: Iterable[str], stopwords: set[str], stemmer) -> list[str]:
    if stemmer is None:
        return [token for token in tokens if token and token not in stopwords]
    return [stemmer.stem(token) for token in tokens if token and token not in stopwords]


def convert_text_to_text(json_data: dict) -> str:
    return json_data.get("symptom_description", "")


def convert_wav_to_text(wav_file_path: str, language: int = 1) -> str:
    if language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language code: {language}. Use 1 (English) or 0 (Indigenous).")

    if not os.path.isfile(wav_file_path):
        raise FileNotFoundError(f"WAV file not found: {wav_file_path}")

    try:
        with wave.open(wav_file_path, "rb") as wav_file:
            _ = wav_file.getnframes()
    except wave.Error as exc:
        raise ValueError(
            f"Invalid WAV audio file: {wav_file_path}. File must be RIFF/PCM WAV."
        ) from exc

    if language == 0:
        transcript = transcribe_walmadjari(wav_file_path)
        print(f"Transcription (wmt, backend={os.environ.get('WMT_ASR_BACKEND', 'whisper')}): {transcript}")
        return transcript

    if sr is None:
        raise ImportError(
            "Missing dependency 'speech_recognition'.\n"
            "Install backend requirements to enable audio transcription."
        )

    language_code = LANGUAGE_MAP[language]
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as source:
        audio = recognizer.record(source)

    transcript = recognizer.recognize_google(audio, language=language_code)
    print(f"Transcription ({language_code}): {transcript}")
    return transcript


def transcribe_upload(file_obj, language: int = 1) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(file_obj, tmp)
        tmp_path = tmp.name

    try:
        return convert_wav_to_text(tmp_path, language=language)
    finally:
        os.unlink(tmp_path)


# def process_symptom_description(symptom_description: str, language: int = 1) -> dict:
#     if language not in LANGUAGE_MAP:
#         raise ValueError(f"Unsupported language code: {language}. Use 1 (English) or 0 (Indigenous).")

#     if language == 0:
#         text_to_process = translate_indigenous_to_english(symptom_description)
#     else:
#         text_to_process = symptom_description
        
#     normalized_text = normalize_text(text_to_process)

#     spacy_tokens = tokenize_with_spacy(_nlp, normalized_text)
#     nltk_tokens = tokenize_with_nltk(_tokenizer, normalized_text)

#     spacy_stems = set(stem_tokens(spacy_tokens, _stopwords, _stemmer))
#     nltk_stems = set(stem_tokens(nltk_tokens, _stopwords, _stemmer))
#     combined_stems = spacy_stems | nltk_stems

#     result = {
#         "symptom_description": symptom_description,
#         "translated_text": text_to_process,
#         "stemmed_tokens": list(combined_stems),
#     }

#     extracted = []
#     negated = []
#     negation_words = {"no", "not", "without", "don't", "doesn't", "didn't"}

#     for symptom, phrases in SYMPTOM_PATTERNS.items():
#         for phrase in phrases:
#             phrase_normalized = normalize_text(phrase)
#             phrase_stems = set(stem_tokens(phrase_normalized.split(), _stopwords, _stemmer))

#             if phrase_normalized in normalized_text:
#                 phrase_index = normalized_text.find(phrase_normalized)
#                 text_before = normalized_text[:phrase_index].split()
#                 if text_before and text_before[-1] in negation_words:
#                     negated.append(symptom)
#                 else:
#                     extracted.append(symptom)
#                 break

#             if phrase_stems and phrase_stems.issubset(combined_stems):
#                 negation_found = False
#                 for negation_word in negation_words:
#                     if re.search(negation_word + r"\s+.*?" + phrase_normalized, normalized_text):
#                         negated.append(symptom)
#                         negation_found = True
#                         break
#                 if not negation_found:
#                     extracted.append(symptom)
#                 break

#     result["extracted_symptoms"] = list(dict.fromkeys(extracted))
#     result["negated_symptoms"] = list(dict.fromkeys(negated))

#     return result

def mapping_symptoms(transcript: str) -> dict:        
    normalized_text = normalize_text(transcript)

    spacy_tokens = tokenize_with_spacy(_nlp, normalized_text)
    nltk_tokens = tokenize_with_nltk(_tokenizer, normalized_text)

    spacy_stems = set(stem_tokens(spacy_tokens, _stopwords, _stemmer))
    nltk_stems = set(stem_tokens(nltk_tokens, _stopwords, _stemmer))
    combined_stems = spacy_stems | nltk_stems

    result = {
        "transcript": transcript,
        "translated_text": transcript,
        "stemmed_tokens": list(combined_stems),
    }

    extracted = []
    negated = []
    negation_words = {"no", "not", "without", "don't", "doesn't", "didn't"}

    for symptom, phrases in SYMPTOM_PATTERNS.items():
        for phrase in phrases:
            phrase_normalized = normalize_text(phrase)
            phrase_stems = set(stem_tokens(phrase_normalized.split(), _stopwords, _stemmer))

            if phrase_normalized in normalized_text:
                phrase_index = normalized_text.find(phrase_normalized)
                text_before = normalized_text[:phrase_index].split()
                if text_before and text_before[-1] in negation_words:
                    negated.append(symptom)
                else:
                    extracted.append(symptom)
                break

            if phrase_stems and phrase_stems.issubset(combined_stems):
                negation_found = False
                for negation_word in negation_words:
                    if re.search(negation_word + r"\s+.*?" + phrase_normalized, normalized_text):
                        negated.append(symptom)
                        negation_found = True
                        break
                if not negation_found:
                    extracted.append(symptom)
                break

    result["extracted_symptoms"] = list(dict.fromkeys(extracted))
    result["negated_symptoms"] = list(dict.fromkeys(negated))

    return result

# def extract_symptoms(request: ExtractSymptomsRequest) -> ExtractSymptomsResponse:
#     processed = process_symptom_description(request.symptoms_description, language=request.language)
#     extracted = processed.get("extracted_symptoms", [])
#     all_symptoms = list(dict.fromkeys(request.symptoms + extracted))

#     return ExtractSymptomsResponse(
#         symptoms_description=request.symptoms_description,
#         extracted_symptoms=extracted,
#         negated_symptoms=processed.get("negated_symptoms", []),
#         symptoms=all_symptoms,
#     )

def _parse_symptoms(transcript: str) -> dict | None:
    processed = mapping_symptoms(transcript)
    extracted = processed.get("extracted_symptoms", [])
    all_symptoms = list(dict.fromkeys(extracted))
    if extracted:
        return {"symptoms": all_symptoms}
    return None

def _parse_additional_symptoms(transcript: str) -> dict | None:
    ##
    return None

def _parse_gender(transcript: str) -> dict | None:
    if "female" in transcript:
        return {"gender": "0"}
    if "male" in transcript or "mail" in transcript:
        return {"gender": "1"}
    if "unknown" in transcript or "prefer not to say" in transcript:
        return {"gender": "2"}
    return None


def _parse_age(transcript: str) -> dict | None:
    has_65 = "65" in transcript or "sixty-five" in transcript or "sixty five" in transcript
    if not has_65:
        return None
    over_words = {"older", "over", "above", "more", "greater"}
    under_words = {"younger", "under", "below", "less", "fewer"}
    if any(w in transcript for w in over_words):
        return {"age_over_65": "1"}
    if any(w in transcript for w in under_words):
        return {"age_over_65": "0"}
    if "unknown" in transcript or "prefer not to say" in transcript:
        return {"age_over_65": "2"}
    return None

def _parse_severity(transript: str) -> dict | None:
    if "mild" in transript or "mould" in transript:
        return {"symptom_severity": "1"}
    if "low" in transript:
        return {"symptom_severity": "2"}
    if "moderate" in transript:
        return {"symptom_severity": "3"}
    if "high" in transript:
        return {"symptom_severity": "4"}
    if "severe" in transript:
        return {"symptom_severity": "5"}
    return None

def _parse_duration(transcript: str) -> dict | None:
    over_words = {"longer", "over", "more", "greater"}
    under_words = {"shorter", "under", "less", "fewer"}
    if any(w in transcript for w in under_words):
        return {"symptoms_duration": "0"}
    if any(w in transcript for w in over_words):
        return {"symptoms_duration": "1"}
    if "unknown" in transcript or "don't know" in transcript or "not sure" in transcript:
        return {"symptoms_duration": "2"}

def _parse_chronic_conditions(transcript: str) -> dict | None:
    conditions = set()
    if "hypertension" in transcript:
        conditions.add("hypertension")
    if "type 2 diabetes" in transcript:
        conditions.add("type_2_diabetes")
    if "heart disease" in transcript:
        conditions.add("heart_disease")
    if "asthma" in transcript or "copd" in transcript:
        conditions.add("asthma_copd")
    if "depression" in transcript or "anxiety" in transcript:
        conditions.add("depression_anxiety")
    return {"chronic_conditions": conditions} if conditions else None

def _parse_escalation_triggers(transcript: str) -> dict | None:
    triggers = set()
    if "difficulty breathing" in transcript or "shortness of breath" in transcript:
        triggers.add("difficulty_breathing")
    if "chest pain" in transcript:
        triggers.add("chest_pain")
    if "confusion" in transcript:
        triggers.add("confusion")
    if "persistent high fever" in transcript:
        triggers.add("persistent_high_fever")
    if "severe weakness" in transcript:
        triggers.add("severe_weakness")
    return {"escalation_triggers": triggers} if triggers else None

def _parse_had_symptoms_before(transcript: str) -> dict | None:
    if "don't know" in transcript or "not sure" in transcript or "unknown" in transcript:
        return {"had_symptoms_before": "2"}
    if "yes" in transcript or "yeah" in transcript or "yep" in transcript:
        return {"had_symptoms_before": "1"}
    if "no" in transcript or "not" in transcript or "nah" in transcript:
        return {"had_symptoms_before": "0"}
    return None

def _parse_had_contact(transcript: str) -> dict | None:
    if "don't know" in transcript or "not sure" in transcript or "unknown" in transcript:
        return {"had_contact": "2"}    
    if "yes" in transcript or "yeah" in transcript or "yep" in transcript:
        return {"had_contact": "1"}
    if "no" in transcript or "not" in transcript or "nah" in transcript:
        return {"had_contact": "0"}
    return None

_QUESTION_PARSERS = {
    1: _parse_gender, #check
    2: _parse_age, #check
    3: _parse_symptoms, #check
    #4: _parse_additional_symptoms, #not implemented yet
    5: _parse_severity, #check
    6: _parse_duration, #check
    7: _parse_had_symptoms_before, #check
    8: _parse_chronic_conditions, #check
    9: _parse_had_contact, #check
    #10: _parse_escalation_triggers, #not implemented yet
}

# Questions whose Walmadjari answers are matched directly against pre-recorded
# reference WAVs (audio-to-audio matching, no STT). Question 3 (free-form
# symptoms) stays on the Whisper + word-translation + text-parser path.
WMT_AUDIO_MATCH_QUESTIONS = {1, 2, 5, 6, 7, 8, 9}

_FIELD_FOR_QUESTION = {
    1: "gender",
    2: "age_over_65",
    5: "symptom_severity",
    6: "symptoms_duration",
    7: "had_symptoms_before",
    8: "chronic_conditions",
    9: "had_contact",
}


def process_audio_response(file_obj, language: int = 1, question_id: int = None) -> dict:
    """Run the right pipeline for one question, return a uniform envelope:

        {"parsed_response":    dict | None,
         "confidence":         float | None,   # 0..1 (None for English/Google STT)
         "transcript":         str,            # raw STT text, "" when audio-matched
         "matched_reference":  str}            # reference WAV name, "" when text-matched

    English (language=1) always goes through Google STT + text parsers.
    Walmadjari (language=0):
      - q=3 (symptoms, free-form): Whisper + wmt->en word translation + parser
      - everything else: MFCC+DTW match against backend/data/wmt_references/
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(file_obj, tmp)
        tmp_path = tmp.name

    try:
        if language not in LANGUAGE_MAP:
            raise ValueError(f"Unsupported language code: {language}. Use 1 (English) or 0 (Indigenous).")

        # ---- Walmadjari audio-match path (fixed-answer questions) -----------
        if language == 0 and question_id in WMT_AUDIO_MATCH_QUESTIONS:
            from nlp.wmt_audio_matcher import match_audio
            m = match_audio(tmp_path, question_id)
            parsed = None
            if m.answer_key is not None:
                field = _FIELD_FOR_QUESTION[question_id]
                if question_id == 8:
                    # Multi-select; for now one matched ref -> one condition. Future:
                    # run the matcher in multi-keyword mode against a sliding window.
                    parsed = {field: {m.answer_key}}
                else:
                    parsed = {field: m.answer_key}
            _log_wmt_transcript(
                tmp_path=tmp_path,
                question_id=question_id,
                raw_transcript="",
                translated_transcript="",
                parsed=parsed,
                confidence=m.similarity if m.answer_key else None,
                match_source="audio_match",
                extra={"matched_reference": m.matched_reference,
                       "cost": round(m.cost, 4),
                       "refs_considered": m.refs_considered},
            )
            return {
                "parsed_response": parsed,
                "confidence": m.similarity if m.answer_key else None,
                "transcript": "",
                "matched_reference": m.matched_reference,
            }

        # ---- Text path: English, OR Walmadjari symptoms (q=3) ---------------
        raw_transcript = convert_wav_to_text(tmp_path, language=language)
        if language == 0:
            transcript = translate_indigenous_to_english(raw_transcript).lower().strip()
        else:
            transcript = raw_transcript.lower().strip()

        parser = _QUESTION_PARSERS.get(question_id)
        parsed: dict | None = None
        confidence: float | None = None
        if parser:
            parsed = parser(transcript)
            if parsed is not None:
                confidence = 1.0

        if language == 0:
            _log_wmt_transcript(
                tmp_path=tmp_path,
                question_id=question_id,
                raw_transcript=raw_transcript,
                translated_transcript=transcript,
                parsed=parsed,
                confidence=confidence,
                match_source="text_parser",
            )

        return {
            "parsed_response": parsed,
            "confidence": confidence,
            "transcript": raw_transcript,
            "matched_reference": "",
        }
    finally:
        os.unlink(tmp_path)


def _log_wmt_transcript(
    *,
    tmp_path: str,
    question_id: int | None,
    raw_transcript: str,
    translated_transcript: str,
    parsed: dict | None,
    confidence: float | None,
    match_source: str,
    extra: dict | None = None,
) -> None:
    """Append one JSONL record for a Walmadjari request. Best-effort: any IO
    error is swallowed so logging never breaks the request. Disable by
    setting WMT_LOG_PATH=/dev/null.
    """
    try:
        if str(WMT_LOG_PATH) == os.devnull:
            return
        WMT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        wav_sha1 = ""
        try:
            with open(tmp_path, "rb") as fh:
                wav_sha1 = hashlib.sha1(fh.read()).hexdigest()
        except OSError:
            pass
        parsed_jsonable = parsed
        if isinstance(parsed, dict):
            parsed_jsonable = {
                k: (sorted(v) if isinstance(v, set) else v) for k, v in parsed.items()
            }
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "wav_sha1": wav_sha1,
            "question_id": question_id,
            "raw_transcript": raw_transcript,
            "translated_transcript": translated_transcript,
            "parsed": parsed_jsonable,
            "confidence": confidence,
            "match_source": match_source,
        }
        if extra:
            record.update(extra)
        with WMT_LOG_PATH.open("a", encoding="utf-8") as out:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass

def main() -> None:
    
    # test = process_audio_response(open("/Users/jasperl/Downloads/audio/type2diabetes.wav", "rb"), language=1, question_id=8)
    # print(test)
    
    test = translate_indigenous_to_english("karlarra waru, karlarra mirrirr, ngajirta karlarra parnta, ngajirta patanyja")
    # test = "i have fever, no cough"
    print(test)
    test = mapping_symptoms(test)
    print(test)


if __name__ == "__main__":
    main()
