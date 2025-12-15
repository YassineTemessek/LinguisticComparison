# OpenAI workspace

This folder contains **OpenAI-side scripts** and **OpenAI-generated outputs**.

## Scripts

Main entrypoint:

- Build/refresh canonical processed datasets: `python "OpenAI/scripts/run_ingest_all.py"`
  - List steps: `python "OpenAI/scripts/run_ingest_all.py" --list`
  - Run a subset: `python "OpenAI/scripts/run_ingest_all.py" --only arabic`
  - Use external datasets: `python "OpenAI/scripts/run_ingest_all.py" --resources-dir "C:/AI Projects/Resources"`

Other common tools:

- Split large JSONL into parts: `python "OpenAI/scripts/split_processed_jsonl.py" data/processed/english/english_ipa_merged_pos.jsonl --lines 50000`
- Build a QA manifest: `python "OpenAI/scripts/build_processed_manifest.py"`
- Validate canonical processed outputs: `python "OpenAI/scripts/validate_processed.py" --all`

## Outputs

All OpenAI outputs go under `OpenAI/output/` (ignored by git by default).
