from collections.abc import Iterable
import json
import os
import re
import warnings
import wave

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - import guard for optional dependency
    sr = None

# This code snippet is designed to normalize user input describing symptoms, making it easier for an NLP model to process the information
# The `normalize_text` function converts the input text to lowercase, removes unwanted characters, and collapses multiple spaces into a single space
# The normalized text is then structured as a JSON object, which can be sent to an NLP model for further analysis
def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text)

# A dictionary of symptom patterns that maps common symptoms to various phrases that may be used to describe them in user input
SYMPTOM_PATTERNS = {
    "cold": ["cold", "chills", "shivering"],
    "fever": ["fever", "high temperature", "hot"],
    "cough": ["cough", "coughing"],
    "headache": ["headache", "head pain", "migraine"],
    "stomach ache": ["stomach ache", "belly pain", "abdominal pain"],
}

# A set of common stopwords that may be used as a fallback if the Spacy library is not available
FALLBACK_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
}

# A function to load Spacy components, including the NLP model and stopwords
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

# A function to load NLTK components, including the tokenizer and stemmer
def load_nltk_components():
    try:
        from nltk.stem import PorterStemmer
        from nltk.tokenize import TreebankWordTokenizer

        return TreebankWordTokenizer(), PorterStemmer()
    except Exception:
        return None, None

# A function to tokenize text using Spacy, which returns a list of tokens while ignoring whitespace
def tokenize_with_spacy(nlp, text: str) -> list[str]:
    if nlp is None:
        return []
    doc = nlp(text)
    return [token.text for token in doc if not token.is_space]

# A function to tokenize text using NLTK, which returns a list of lowercase tokens
# If the tokenizer is not available, it falls back to splitting the text by spaces
def tokenize_with_nltk(tokenizer, text: str) -> list[str]:
    if tokenizer is None:
        return text.split()
    return [token.lower() for token in tokenizer.tokenize(text)]

# A function to stem tokens using a provided stemmer and filter out stopwords
# If the stemmer is not available, it simply returns the tokens that are not stopwords
def stem_tokens(tokens: Iterable[str], stopwords: set[str], stemmer) -> list[str]:
    if stemmer is None:
        return [token for token in tokens if token and token not in stopwords]
    return [stemmer.stem(token) for token in tokens if token and token not in stopwords]

# A function to convert the text (user input) symptom description to a JSON object, which can then be processed by the NLP model
def convert_text_to_text(json_data: dict) -> str:
    return json_data.get("symptom_description", "")

# A function to convert the wav files to text using a speech-to-text model, which can then be processed by the NLP model
def convert_wav_to_text(wav_file_path: str) -> str:
    if sr is None:
        raise ImportError(
            "Missing dependency 'speech_recognition'.\n"
            "Install backend requirements to enable audio transcription."
        )
    
    if not os.path.isfile(wav_file_path):
        raise FileNotFoundError(f"WAV file not found: {wav_file_path}")

    # Validate that the file is readable as a WAV before processing.
    try:
        with wave.open(wav_file_path, "rb") as wav_file:
            _ = wav_file.getnframes()
    except wave.Error as exc:
        raise ValueError(
            f"Invalid WAV audio file: {wav_file_path}. File must be RIFF/PCM WAV."
        ) from exc
    
    # A function uses Google Cloud Speech-to-Text API to convert the audio in the wav file to text, which can then be processed by the NLP model
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.record(source)
    
    transcript = recognizer.recognize_google(audio)
    
    print(f"Transcription: {transcript}")
    
    return transcript

# A function to process the symptom description provided by the user, which includes normalization, tokenization, stemming, and symptom extraction based on predefined patterns
# The function returns a JSON object containing the original symptom description, the stemmed tokens, the extracted symptoms, and any negated symptoms
def process_symptom_description(symptom_description: str, nlp, stopwords, tokenizer, stemmer) -> dict:
    # normalize the user input text
    normalized_text = normalize_text(symptom_description)
    
    # tokenize the normalized text using both Spacy and NLTK tokenizers
    spacy_tokens = tokenize_with_spacy(nlp, normalized_text)
    nltk_tokens = tokenize_with_nltk(tokenizer, normalized_text)
    
    # stem the tokens and filter out stopwords
    # combine the stemmed tokens from both Spacy and NLTK into a single set to ensure uniqueness
    spacy_stems = set(stem_tokens(spacy_tokens, stopwords, stemmer))
    nltk_stems = set(stem_tokens(nltk_tokens, stopwords, stemmer))
    combined_stems = spacy_stems | nltk_stems

    input_text = {"symptom_description": symptom_description}
    input_text["stemmed_tokens"] = list(combined_stems)
    
    # extract symptoms based on predefined patterns and add them to the input text JSON object
    extracted = []
    negated = []
    negation_words = {"no", "not", "without", "don't", "doesn't", "didn't"}
    
    for symptom, phrases in SYMPTOM_PATTERNS.items():
        for phrase in phrases:
            phrase_normalized = normalize_text(phrase)
            phrase_tokens = phrase_normalized.split()
            phrase_stems = set(stem_tokens(phrase_tokens, stopwords, stemmer))

            # check if the normalized phrase is directly present in the normalized user input text
            if phrase_normalized in normalized_text:
                # check if preceded by negation word
                phrase_index = normalized_text.find(phrase_normalized)
                text_before = normalized_text[:phrase_index].split()
                if text_before and text_before[-1] in negation_words:
                    negated.append(symptom)
                else:
                    extracted.append(symptom)
                break

            # if the stemmed tokens of the phrase are a subset of the combined stemmed tokens from the user input, consider it a match
            if phrase_stems and phrase_stems.issubset(combined_stems):
                # check if preceded by negation word in original text
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
    
    # add the extracted symptoms to the input text JSON object
    # add the negated symptoms to the input text JSON object
    # use dict.fromkeys to remove duplicates while preserving order, and sort the final list of extracted symptoms
    input_text["extracted_symptoms"] = list(dict.fromkeys(extracted))
    input_text["negated_symptoms"] = list(dict.fromkeys(negated))
    
    return input_text

def main() -> None:
    nlp, stopwords = load_spacy_components()
    tokenizer, stemmer = load_nltk_components()
    
    # hardcode - user input (text) under description of the symptoms
    # symptom_description = json.loads('{"symptom_description": "I feel cold and had belly pain"}')
    # symptom_description = json.loads('{"symptom_description": "I have cold and fever but no headache."}')
    # symptom_description = convert_text_to_text(symptom_description)
    wav_input = "/Users/jasperl/Downloads/test1.wav"
    # symptom_description = "I feel cold and had belly pain"

    if os.path.isfile(wav_input):
        try:
            symptom_description = convert_wav_to_text(wav_input)
        except (ImportError, FileNotFoundError, ValueError) as exc:
            warnings.warn(
                f"Audio transcription skipped: {exc}. Falling back to text input.",
                stacklevel=1,
            )
    
    result = process_symptom_description(
        symptom_description,
        nlp,
        stopwords,
        tokenizer,
        stemmer
    )

    # convert the final processed data into a JSON string and print it
    nlp_text = json.dumps(result)
    print(nlp_text)

if __name__ == "__main__":
    main()