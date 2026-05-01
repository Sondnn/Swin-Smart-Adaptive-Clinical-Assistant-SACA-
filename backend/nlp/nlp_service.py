from collections.abc import Iterable
import json
import os
import re
import shutil
import tempfile
import warnings
import wave
try:
    import speech_recognition as sr
except ImportError:
    sr = None


SYMPTOM_PATTERNS = {
    "cold": ["cold", "chills", "shivering"],
    "fever": ["fever", "high temperature", "hot"],
    "cough": ["cough", "coughing"],
    "headache": ["headache", "head pain", "migraine"],
    "stomach ache": ["stomach ache", "belly pain", "abdominal pain"],
}

FALLBACK_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "or", "that",
    "the", "to", "was", "were", "will", "with",
}

# Maps language int (from API) to Google Speech API language code
LANGUAGE_MAP = {
    1: "en-AU",
    0: "...",  # Replace with supported indigenous language code
}


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text)

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

    language_code = LANGUAGE_MAP[language]

    if sr is None:
        raise ImportError(
            "Missing dependency 'speech_recognition'.\n"
            "Install backend requirements to enable audio transcription."
        )

    if not os.path.isfile(wav_file_path):
        raise FileNotFoundError(f"WAV file not found: {wav_file_path}")

    try:
        with wave.open(wav_file_path, "rb") as wav_file:
            _ = wav_file.getnframes()
    except wave.Error as exc:
        raise ValueError(
            f"Invalid WAV audio file: {wav_file_path}. File must be RIFF/PCM WAV."
        ) from exc

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

def process_symptom_description(symptom_description: str, nlp, stopwords, tokenizer, stemmer) -> dict:
    normalized_text = normalize_text(symptom_description)

    spacy_tokens = tokenize_with_spacy(nlp, normalized_text)
    nltk_tokens = tokenize_with_nltk(tokenizer, normalized_text)

    spacy_stems = set(stem_tokens(spacy_tokens, stopwords, stemmer))
    nltk_stems = set(stem_tokens(nltk_tokens, stopwords, stemmer))
    combined_stems = spacy_stems | nltk_stems

    input_text = {
        "symptom_description": symptom_description,
        "stemmed_tokens": list(combined_stems),
    }

    extracted = []
    negated = []
    negation_words = {"no", "not", "without", "don't", "doesn't", "didn't"}

    for symptom, phrases in SYMPTOM_PATTERNS.items():
        for phrase in phrases:
            phrase_normalized = normalize_text(phrase)
            phrase_tokens = phrase_normalized.split()
            phrase_stems = set(stem_tokens(phrase_tokens, stopwords, stemmer))

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
                    pattern = negation_word + r"\s+.*?" + phrase_normalized
                    if re.search(pattern, normalized_text):
                        negated.append(symptom)
                        negation_found = True
                        break
                if not negation_found:
                    extracted.append(symptom)
                break

    input_text["extracted_symptoms"] = list(dict.fromkeys(extracted))
    input_text["negated_symptoms"] = list(dict.fromkeys(negated))

    return input_text

def main() -> None:
    nlp, stopwords = load_spacy_components()
    tokenizer, stemmer = load_nltk_components()

    wav_input = "/Users/jasperl/Downloads/test1.wav"
    symptom_description = convert_wav_to_text(wav_input)

    symptoms_extracted = process_symptom_description(
        symptom_description, nlp, stopwords, tokenizer, stemmer
    )

    print(json.dumps(symptoms_extracted))

if __name__ == "__main__":
    main()
