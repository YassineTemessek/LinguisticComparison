# LinguisticComparison

Repository for a reproducible **linguistic ingest + similarity scoring** pipeline (Arabic + related languages vs selected Indo‑European languages), producing ranked candidates and reports.

## Layout

- `OpenAI/`: OpenAI-side scripts + local outputs
- `Gemini/`: Gemini-side scripts + local outputs
- `data/`: local datasets (ignored by default) and processed outputs docs (`data/README.md`, `data/processed/README.md`)
- `resources/`: tracked reference assets (small, versioned)
- `src/`: reusable code/stubs (planned shared library)
- `docs/`: project documentation (`docs/INGEST.md`, `docs/SIMILARITY_SCORING_SPEC.md`)

## Quickstart

1) Put datasets under `data/raw/` (see `data/README.md`).
2) Build processed tables: `python "OpenAI/scripts/run_ingest_all.py"`
3) Run matching: `python "Gemini/scripts/run_full_matching_pipeline.py"`

## What this repo is (LV3)

LV3 is focused on **scoring similarities** and producing:

- `orthography_score` (shape/spelling echoes)
- `sound_score` (IPA similarity)
- `combined_score` (rankable blend)

See `docs/SIMILARITY_SCORING_SPEC.md`.
