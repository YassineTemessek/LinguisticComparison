# Processed samples (tracked)

The full datasets under `data/raw/` and `data/processed/` are intentionally **not committed** to Git.

This folder contains **small JSONL samples** of canonical processed outputs so contributors can:

- Validate schema expectations quickly
- Run small-scale matching experiments
- Review typical row shapes without downloading large datasets

## How to update samples

Samples should be produced in LV0 (data core) and then copied into this folder when they change.

LV0 repo:

- `https://github.com/YassineTemessek/LinguisticDataCore-LV0`

## Notes

- Samples are meant for development/QA only; they are not representative of full coverage.
- If you plan to share full datasets publicly, confirm source licenses first.


## Project Status & Progress
- Project-wide progress log: docs/PROGRESS_LOG.md`n- Raw data flow (Resources -> LV0 -> processed): docs/RAW_DATA_FLOW.md`n
