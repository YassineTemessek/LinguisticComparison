# Start Here (LV3)

This repo is a **data pipeline + scoring engine** for linguistic comparison.

The workflow is always:

1) **Raw data** goes in `data/raw/` (not committed).
2) **Ingest** converts raw sources into **canonical processed tables** in `data/processed/` (not committed).
3) **Matching** consumes the canonical tables + `resources/` to produce **ranked leads** + **QA** under `Gemini/output/` and `OpenAI/output/` (not committed).

## What "good" looks like

- `data/processed/*` files exist and pass validation (`id`, `lemma`, etc. are present; IPA is normalized).
- Matching outputs contain `orthography_score`, `sound_score`, and `combined_score` with provenance fields so results are traceable.
- Each ingest run produces a manifest JSON under `OpenAI/output/manifests/` recording what ran and what outputs exist.

## Collaboration-friendly samples (tracked)

Full datasets are not committed by default, but small samples are tracked under `resources/samples/processed/`.

- Build samples: `python "OpenAI/scripts/build_processed_samples.py" --all --rows 1000`
- Run a quick matching smoke test on samples:
  - `python "Gemini/scripts/run_full_matching_pipeline.py" --semitic "resources/samples/processed/Arabic-English_Wiktionary_dictionary_stardict_filtered_sample.jsonl" --english "resources/samples/processed/english_ipa_merged_pos_sample.jsonl" --limit 200`

## Core commands

- Ingest (all): `python "OpenAI/scripts/run_ingest_all.py"`
- Ingest (only Arabic): `python "OpenAI/scripts/run_ingest_all.py" --only arabic`
- Validate canonical outputs: `python "OpenAI/scripts/validate_processed.py" --all`
- KPI/coverage report (JSON + CSV): `python "OpenAI/scripts/kpi_processed.py" --all`
- Match: `python "Gemini/scripts/run_full_matching_pipeline.py"`

## Getting full processed data (optional)

If you don't want to rebuild `data/processed/` locally, you can download a maintainer-published Release zip:

- `python "OpenAI/scripts/fetch_processed_release.py"`
- Details: `docs/RELEASE_ASSETS.md`

## Where to read next

- Pipeline details: `docs/INGEST.md`
- Data layout: `data/README.md`
- Processed data contract: `data/processed/README.md`
- Scoring model: `docs/SIMILARITY_SCORING_SPEC.md`
