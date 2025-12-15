# Gemini workspace

This folder contains **Gemini-side scripts** and **Gemini-generated outputs**.

## Inputs

Gemini scripts are designed to consume the canonical processed datasets under `data/processed/` (built by `OpenAI/scripts/run_ingest_all.py`), especially:

- `data/processed/wiktionary_stardict/filtered/Arabic-English_Wiktionary_dictionary_stardict_filtered.jsonl`
- `data/processed/_parts/english_ipa_merged_pos/*.jsonl`
- `data/processed/concepts/concepts_v3_2_enriched.jsonl`

## Outputs

All Gemini outputs go under `Gemini/output/`.

## Common runs

- Full matching pipeline: `python "Gemini/scripts/run_full_matching_pipeline.py"`
- Validate a processed JSONL file: `python "Gemini/scripts/validate_ingest.py" <path>`
- Prototype matcher (quick smoke test): `python "Gemini/scripts/prototype_matcher.py" --limit 200`
