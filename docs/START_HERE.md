# Start Here (LV3)

This repo is a **data pipeline + scoring engine** for linguistic comparison.

The workflow is always:

1) **Raw data** goes in `data/raw/` (not committed).
2) **Ingest** converts raw sources into **canonical processed tables** in `data/processed/` (not committed).
3) **Matching** consumes the canonical tables + `resources/` to produce **ranked leads** + **QA** under `Gemini/output/` and `OpenAI/output/` (not committed).

## What “good” looks like

- `data/processed/*` files exist and pass validation (`id`, `lemma`, etc. are present; IPA is normalized).
- Matching outputs contain `orthography_score`, `sound_score`, and `combined_score` with provenance fields so results are traceable.
- Each ingest run produces a manifest JSON under `OpenAI/output/manifests/` recording what ran and what outputs exist.

## Core commands

- Ingest (all): `python "OpenAI/scripts/run_ingest_all.py"`
- Ingest (only Arabic): `python "OpenAI/scripts/run_ingest_all.py" --only arabic`
- Validate canonical outputs: `python "OpenAI/scripts/validate_processed.py" --all`
- Match: `python "Gemini/scripts/run_full_matching_pipeline.py"`

## Where to read next

- Pipeline details: `docs/INGEST.md`
- Data layout: `data/README.md`
- Processed data contract: `data/processed/README.md`
- Scoring model: `docs/SIMILARITY_SCORING_SPEC.md`

