# Processed samples (tracked)

The full datasets under `data/raw/` and `data/processed/` are intentionally **not committed** to Git.

This folder contains **small JSONL samples** of canonical processed outputs so contributors can:

- Validate schema expectations quickly
- Run small-scale matching experiments
- Review typical row shapes without downloading large datasets

## Build/update samples

From repo root:

`python "OpenAI/scripts/build_processed_samples.py" --all --rows 1000`

This writes:

- `resources/samples/processed/*_sample.jsonl`
- `resources/samples/processed/manifest.json`

## Notes

- Samples are meant for development/QA only; they are not representative of full coverage.
- If you plan to share full datasets publicly, confirm source licenses first.

