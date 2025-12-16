# LinguisticComparison (LV3)

[![ci](https://github.com/YassineTemessek/LinguisticComparison/actions/workflows/ci.yml/badge.svg)](https://github.com/YassineTemessek/LinguisticComparison/actions/workflows/ci.yml)

Reproducible **linguistic ingest + similarity scoring** pipeline producing **ranked cross-language candidates** and **QA reports**.

LV3 is “discovery-first”: it surfaces candidates for human review; it does not claim historical directionality.

## What You Get

- Canonical, machine-readable lexeme tables under `data/processed/` (JSONL contract).
- Matching/scoring outputs under `Gemini/output/` (ranked leads) and `OpenAI/output/` (manifests/previews).
- Validation tooling to catch broken rows early.

## Repo Policy (Important)

- Large datasets live under `data/raw/` and are **not committed** by default.
- Generated outputs under `data/processed/`, `OpenAI/output/`, and `Gemini/output/` are **not committed** by default.

If you want to use prebuilt `data/processed/` outputs without rebuilding locally, see `docs/RELEASE_ASSETS.md` (Release zip + temporary Google Drive mirror).

## Layout

- `OpenAI/`: OpenAI-side scripts + local outputs
- `Gemini/`: Gemini-side scripts + local outputs
- `data/`: local datasets (ignored by default) and processed outputs docs (`data/README.md`, `data/processed/README.md`)
- `resources/`: tracked reference assets (small, versioned)
- `src/`: reusable code/stubs (planned shared library)
- `docs/`: project documentation (start with `docs/README.md`)

## Quickstart (Windows / PowerShell)

1) Create a Python environment and install dependencies:

- `python -m venv .venv`
- Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
- Install: `python -m pip install -r requirements.txt` (or `requirements.lock.txt` for pinned versions)

2) Put datasets under `data/raw/` (see `data/README.md`).

3) Build/refresh processed tables (writes a manifest under `OpenAI/output/manifests/`):

- `python "OpenAI/scripts/run_ingest_all.py"`

4) Validate canonical processed outputs:

- `python "OpenAI/scripts/validate_processed.py" --all --require-files`

5) Run matching:

- `python "Gemini/scripts/run_full_matching_pipeline.py"`

## What this repo is (LV3)

LV3 is focused on **scoring similarities** and producing:

- `orthography_score` (shape/spelling echoes)
- `sound_score` (IPA similarity)
- `combined_score` (rankable blend)

See `docs/SIMILARITY_SCORING_SPEC.md` and `docs/START_HERE.md`.
