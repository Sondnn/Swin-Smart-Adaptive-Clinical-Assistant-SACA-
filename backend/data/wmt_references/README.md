# Walmadjari reference audio bank

Pre-recorded Walmadjari answer clips used for audio-to-audio matching on
fixed-answer questions. See `backend/nlp/wmt_audio_matcher.py`.

## Layout (flat, English-labelled)

One folder per **English meaning**. The folder name is the English phrase the
clip means; underscores become spaces (`over_65` -> "over 65"). Drop one or
more WAV clips of Walmadjari speakers saying that answer inside it:

```
wmt_references/
    female/        speaker1.wav  speaker2.wav
    male/          speaker1.wav
    unknown/       speaker1.wav
    mild/          speaker1.wav
    moderate/      speaker1.wav
    severe/        speaker1.wav
    yes/           speaker1.wav
    no/            speaker1.wav
    shorter/       speaker1.wav
    longer/        speaker1.wav
    over_65/       speaker1.wav
    under_65/      speaker1.wav
    hypertension/  speaker1.wav
    type_2_diabetes/ speaker1.wav
```

No `/` in any folder name — it is just a flat list of English words/phrases.
There is **no** per-question or answer-code structure: a clip is matched to an
English phrase, and that phrase is then run through the same English text
parser the English STT path uses. Question logic lives only in those parsers
(`backend/nlp/nlp_service.py`).

Shared answers are recorded once: `yes` / `no` / `unknown` cover both Q7
(had symptoms before) and Q9 (sick contact).

## Which labels each question accepts

A label is a valid candidate for a question only if that question's parser
accepts the phrase. Practical labels per question:

| Q | Field                 | Folder labels to record                                              |
|---|-----------------------|----------------------------------------------------------------------|
| 1 | gender                | `female`, `male`, `unknown`                                          |
| 2 | age_over_65           | `over_65`, `under_65` (see note on "unknown" below)                 |
| 5 | symptom_severity      | `mild`, `low`, `moderate`, `high`, `severe`                         |
| 6 | symptoms_duration     | `shorter`, `longer`, `unknown`                                      |
| 7 | had_symptoms_before   | `yes`, `no`, `unknown`                                              |
| 8 | chronic_conditions    | `hypertension`, `type_2_diabetes`, `heart_disease`, `asthma`, `copd`, `depression`, `anxiety` |
| 9 | had_contact           | `yes`, `no`, `unknown`                                              |

Q3 (free-form symptoms) does NOT use this bank — it goes through Whisper +
`wmt_en_dict.json` word translation.

Note on Q2 "unknown": `_parse_age` only accepts a phrase that also mentions 65,
so a plain `unknown/` clip is ignored for Q2. Either skip "unknown" for age, or
name the folder `unknown_65/`. (Cleaner long-term fix: broaden `_parse_age` to
parse spoken ages — tracked in the speech-to-text guide's "known gaps".)

## Audio format

16 kHz mono PCM WAV. Convert with:

```bash
ffmpeg -i input.m4a -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

## Tuning

In `wmt_audio_matcher.py`:

- `WMT_AUDIO_MATCH_MAX_COST` — reject matches whose normalized DTW cost exceeds
  this.
- `WMT_AUDIO_MATCH_MARGIN_RATIO` — the winner must beat the runner-up by this
  ratio, else the match is rejected as ambiguous (returns no answer rather than
  guessing). Tip: record one folder per distinct answer so two folders that
  mean the same thing don't trip the margin check.
- `WMT_REFERENCES_DIR` env var — override the bank location.

After adding or changing clips in a long-running process, call
`clear_reference_cache()` (the bank is cached on first load).
