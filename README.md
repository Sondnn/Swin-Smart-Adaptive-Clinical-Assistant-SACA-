# Swin-Smart-Adaptive-Clinical-Assistant-SACA

This repo holds an entire stack
- **backend** - API service, NLP, Machine Learning
- **android** - Android Mobile App *(Android Application that helps patients assess the urgency of their symptoms and returns the triage level and recommendation.)*
- **window** - Window Desktop App *(add your description here)*

## Description

### Backend

#### API Service

```bash
cd backend && python3 -m uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`
Testing in `http://127.0.0.1:8000/docs`

#### NLP

##### Speech-to-text

`/speech-to-text-page` accepts a WAV plus `language` (1=English, 0=Walmadjari) and `question_id`, and returns a structured answer code for that question. The English path uses Google STT (`en-AU`). The Walmadjari path runs locally — see below.

##### Walmadjari handling (in a nutshell)

Walmadjari isn't supported by any mainstream ASR. Rather than trying to transcribe it, we use **audio-to-audio matching**: a reference WAV is recorded for each expected answer, and incoming audio is matched against those references using MFCC features + Dynamic Time Warping.

| Question | Path |
|---|---|
| Fixed-answer (1, 2, 5, 6, 7, 8, 9) | `nlp/wmt_audio_matcher.py` — MFCC + DTW against the reference bank |
| Symptoms (q=3, free-form) | `nlp/walmadjari_stt.py` — Whisper (forced `language="en"` for Latin-script output) → `wmt_en_dict.json` word translation → English parser |

**Setting up the reference bank**

Drop reference WAVs into `backend/data/wmt_references/<question_id>/<answer_code>/*.wav` — see `backend/data/wmt_references/README.md` for the layout and answer-code table. One clip per answer is enough for a single-speaker demo; more refs across speakers helps generalisation.

**Response envelope** (returned by `/speech-to-text-page`)

```json
{
  "question_id": 5,
  "parsed_response": {"symptom_severity": "1"},
  "confidence": 0.93,
  "transcript": "",
  "matched_reference": "mild.wav"
}
```

For audio-matched questions `transcript` is `""` and `matched_reference` is set; for the symptoms path it's the reverse.

**Tuning knobs** (in `nlp/wmt_audio_matcher.py`)

- `WMT_AUDIO_MATCH_MAX_COST` — accept a match only if normalized DTW cost is below this.
- `WMT_AUDIO_MATCH_MARGIN_RATIO` — winner must beat the runner-up by this ratio; close-call answers return `None` rather than guess.
- `WMT_REFERENCES_DIR` env var — override the reference bank location.
- `WMT_LOG_PATH` env var — JSONL telemetry log per Walmadjari request (default `backend/logs/wmt_transcripts.jsonl`, set to `/dev/null` to disable).

#### Testing

Install pytest and run the test suite:
```bash
pip install pytest
cd backend && pytest tests/ -v
```

`tests/test_wmt_audio_matcher.py` covers the matcher with synthetic tones (exact match, ambiguous-margin rejection, noise rejection, threshold pinning, reference-loading discovery). No audio files or speakers required.

For end-to-end testing with real audio:

1. **Single-clip check** — point `process_audio_response` at one WAV:
   ```bash
   cd backend
   python3 -c "
   import sys; sys.path.insert(0, '.')
   from nlp.nlp_service import process_audio_response
   with open('<your.wav>', 'rb') as f:
       print(process_audio_response(f, language=0, question_id=<id>))
   "
   ```
2. **Through the API** (mirrors what the Android app does):
   ```bash
   curl -X POST http://127.0.0.1:8000/speech-to-text-page \
     -F language=0 -F question_id=5 -F files=@your.wav
   ```
3. **Batch evaluation** — drop clips into `backend/data/wmt_audio/` with a `manifest.json` and run `python3 backend/scripts/eval_walmadjari_stt.py` for predicted-vs-expected accuracy.

Audio prep: clips should be 16 kHz mono PCM WAV. Convert with `ffmpeg -i input.m4a -ar 16000 -ac 1 -c:a pcm_s16le output.wav`.

Don't forget the regression check: `language=1` (English) must still hit Google STT and parse correctly.

#### ML

The `/predict` endpoint returns two things:

* A **triage category** (ESI 1–5) trained on the Kaggle hospital triage dataset [`maalona/hospital-triage-and-patient-history-data`](https://www.kaggle.com/datasets/maalona/hospital-triage-and-patient-history-data) (~560k ED visits, nurse-assigned ESI labels). Only API-compatible features are used (symptoms, age, gender, severity, duration, chronic flags).
* A **disease prediction** (top-1 + top-5 probabilities) trained on [`dhivyeshrk/diseases-and-symptoms-dataset`](https://www.kaggle.com/datasets/dhivyeshrk/diseases-and-symptoms-dataset), with temperature-scaled probabilities.

##### Prerequisite

Both raw datasets must be present:
* `backend/data/raw_triage/5v_cleandf.rdata`
* `backend/data/raw_disease/Final_Augmented_dataset_Diseases_and_Symptoms.csv`

The pipeline auto-downloads them from Kaggle on first run if `kaggle` CLI is configured (`~/.kaggle/kaggle.json`).

##### All-in-one Pipeline

```bash
python3 backend/scripts/run_ml_pipeline.py
```

Flags:
- `--skip-build` — retrain only, reuse existing `training_data_triage.csv` and `training_data_disease.csv`.
- `--skip-train` — ingest only, leave models untouched.

##### Manual stages

Useful when repeating on a single stage.

###### Step 1: Build training data

Two ingest scripts, one per dataset:
```bash
cd backend && python3 ml/build_triage_data.py
cd backend && python3 ml/build_disease_data.py
```
The first loads the `.rdata` via `pyreadr`, takes a stratified 50k slice by ESI, and projects `cc_*` onto the `symptom__` schema. The second mirrors the previous behavior on the disease-symptom CSV (top-150 diseases, light row-level augmentation).

Outputs:
- `backend/models/`: `training_data_triage.csv`, `training_data_disease.csv`, `disease_classes.json`, `model_features.json`
- `backend/reports/`: `ingest_report_triage.json`, `ingest_report_disease.json`

###### Step 2: Train both models
```bash
cd backend && python3 -m ml.train
```
Trains the triage XGBoost classifier and the disease XGBoost classifier with temperature scaling, each via group-aware RandomizedSearchCV (3-fold). Outputs:
- `backend/models/`: `triage_model.joblib`, `triage_label_encoder.joblib`, `model_features.json`, `disease_model.joblib`, `disease_label_encoder.joblib`, `disease_temperature.json`.
- `backend/reports/`: `training_metrics.json`.


### Android

## Description
This triage Android app is built using Kotlin and Jetpack Compose, the triage process is designed based on POPGUNS, the app allow users to select or voice input through the process, and analysis their symptoms and current conditions to predict the severity level and give suggestions.

## Getting Started
The Android app program is under the /android folder

### Dependencies
* Android Studio
* Backend API

### Installing

- Open the \android folder in Android Studio

- Open the build.gradle and sync dependencies

### Executing program

* How to run the program

1. Go the the Constants file to make sure the base URL is same as the running backend API

2. Choose the emulator and build the app 

3. Click the "Run" button to get started

### Window

## Repository Layout

## Prerequisite

