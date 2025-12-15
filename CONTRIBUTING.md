# Contributing

## Project goal

LV3 produces:

- Canonical processed tables under `data/processed/`
- Ranked “lead” candidates and QA artifacts under `Gemini/output/` and `OpenAI/output/`

## Data policy

Large datasets under `data/raw/` and generated artifacts under `data/processed/`, `OpenAI/output/`, and `Gemini/output/` are intentionally not committed by default.

## Setup

- Create venv: `python -m venv .venv`
- Activate (PowerShell): `.\.venv\Scripts\Activate.ps1`
- Install deps: `python -m pip install -r requirements.txt`

## Run + validate

- Ingest: `python "OpenAI/scripts/run_ingest_all.py"`
- Validate: `python "OpenAI/scripts/validate_processed.py" --all`
- Match: `python "Gemini/scripts/run_full_matching_pipeline.py"`

## Before opening a PR

- Ensure CI passes (compile + validation + ingest smoke).
- Update docs when you change file contracts or CLI behavior.

