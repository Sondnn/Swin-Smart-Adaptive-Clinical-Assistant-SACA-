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

##### Walmadjari STT (in a nutshell)

No mainstream ASR supports Walmadjari, so this is a **keyword-spotting** pipeline, not real transcription:

1. **Transcribe.** `backend/nlp/walmadjari_stt.py` runs the audio through one of two backends, selected by env var `WMT_ASR_BACKEND`:
   - `whisper` (default) — `faster-whisper` with `language=None`; produces English-orthography phonetic guesses.
   - `phoneme` — wav2vec2 XLSR IPA model
2. **Translate known words.** `backend/nlp/wmt_en_dict.json` rewrites Walmadjari clinical terms (e.g. `ngalak → headache`) so the existing English parsers can fire.
3. **Fuzzy-match options.** If the English parser comes up empty, `_match_wmt_options` runs `rapidfuzz.partial_ratio` against `backend/nlp/option_vocab_wmt.json` (gender / age / severity / duration / yes-no / chronic) at threshold 75 and returns the same answer codes as the English path.

Switch backends with `WMT_ASR_BACKEND=whisper` or `WMT_ASR_BACKEND=phoneme`. First Walmadjari request downloads the Whisper base model (~145 MB).

#### Testing

Install pytest and run the test suite:
```bash
pip install pytest
cd backend && pytest tests/ -v
```

For any one without Walmadjari audio or speakers, test in order:

1. **Unit-test the matcher** — `backend/tests/test_wmt_matcher.py` already covers every question_id branch, threshold boundaries, empty/placeholder vocab, and the rapidfuzz-missing fallback. No audio, no model.
2. **Mock the transcriber** — patch `nlp.walmadjari_stt.get_transcriber` to return a stub that emits a canned string, then hit `/speech-to-text-page` with any WAV. Verifies the full API contract without loading Whisper.
3. **Read the spellings out loud** — record yourself phonetically saying Walmadjari option words on your phone, POST the WAV. Tests the pipeline end-to-end with real (if accented) speech.
4. **Evaluation harness with synthesized clips** — `backend/scripts/eval_walmadjari_stt.py` loops over `backend/data/wmt_audio/*.wav` plus a `manifest.json` and prints predicted-vs-expected accuracy. Useful for A/B-testing the two backends:
   ```bash
   WMT_ASR_BACKEND=whisper python3 backend/scripts/eval_walmadjari_stt.py
   WMT_ASR_BACKEND=phoneme python3 backend/scripts/eval_walmadjari_stt.py
   ```
5. **Real Walmadjari recordings** — the only test that tells you about *recognition quality*. Likely sources: AIATSIS language collections, PARADISEC archive, Kimberley Language Resource Centre, community YouTube videos (`yt-dlp -x --audio-format wav`).

Don't forget the regression check: `language=1` (English) must still hit Google STT and parse correctly — branching on language should leave that path untouched.

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

### Window

## Repository Layout

## Prerequisite

