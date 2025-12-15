# LinguisticComparison

Repository for building a reproducible **linguistic ingest + comparison** pipeline (Arabic + Indo‑European) and running discovery-style matching.

## Layout

- `OpenAI/`: OpenAI-side scripts + local outputs
- `Gemini/`: Gemini-side scripts + local outputs
- `data/`: local datasets (ignored by default) and processed outputs docs (`data/README.md`, `data/processed/README.md`)
- `resources/`: tracked reference assets (small, versioned)
- `src/`: reusable code/stubs (planned shared library)
- `docs/`: project documentation (`docs/INGEST.md`)

## Quickstart

1) Put datasets under `data/raw/` (see `data/README.md`).
2) Build processed tables: `python "OpenAI/scripts/run_ingest_all.py"`
3) Run matching: `python "Gemini/scripts/run_full_matching_pipeline.py"`
