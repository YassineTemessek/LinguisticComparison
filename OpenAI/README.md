# OpenAI workspace

This folder contains **OpenAI-side scripts** and **OpenAI-generated outputs**.

## Scripts

Main entrypoint:

- Build/refresh canonical processed datasets: `python "OpenAI/scripts/run_ingest_all.py"`

Other common tools:

- Split large JSONL into parts: `python "OpenAI/scripts/split_processed_jsonl.py" data/processed/english/english_ipa_merged_pos.jsonl --lines 50000`
- Build a QA manifest: `python "OpenAI/scripts/build_processed_manifest.py"`

## Outputs

All OpenAI outputs go under `OpenAI/output/` (ignored by git by default).

