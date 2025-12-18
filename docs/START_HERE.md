# Start Here (LV3)

This repo is a **data pipeline + discovery engine** for linguistic comparison.

The workflow is always:

1) **Raw data** goes in `data/raw/` (not committed).
2) **Ingest** converts raw sources into **canonical processed tables** in `data/processed/` (not committed).
3) **Discovery retrieval** consumes the canonical tables to produce **ranked leads** under `outputs/` and caches/indexes under `outputs/` (not committed).

## What "good" looks like

- `data/processed/*` files exist and pass validation (`id`, `lemma`, etc. are present; IPA is normalized).
- Discovery outputs contain lead rows with `sonar` and/or `canine` scores plus provenance fields so results are traceable.
- Each ingest run produces a manifest JSON under `outputs/manifests/` recording what ran and what outputs exist.

## Collaboration-friendly samples (tracked)

Full datasets are not committed by default, but small samples are tracked under `resources/samples/processed/`.

- Build samples: `python "scripts/ingest/build_processed_samples.py" --all --rows 1000`
- Run a quick discovery smoke test on samples:
  - `python "scripts/discovery/run_discovery_retrieval.py" --source ara@modern@arb_Arab="resources/samples/processed/Arabic-English_Wiktionary_dictionary_stardict_filtered_sample.jsonl" --target eng@modern@eng_Latn="resources/samples/processed/english_ipa_merged_pos_sample.jsonl" --models sonar canine --topk 200 --max-out 200 --limit 200`

## Core commands

- Ingest (all): `python "scripts/ingest/run_ingest_all.py"`
- Ingest (only Arabic): `python "scripts/ingest/run_ingest_all.py" --only arabic`
- Validate canonical outputs: `python "scripts/ingest/validate_processed.py" --all`
- KPI/coverage report (JSON + CSV): `python "scripts/ingest/kpi_processed.py" --all`
- Discover (SONAR/CANINE): `python "scripts/discovery/run_discovery_retrieval.py" ...`
- Legacy matcher: `python "scripts/discovery/run_full_matching_pipeline.py"`

## Discovery mode (SONAR + CANINE)

LV3’s recommended mode is embedding-first retrieval:

- **SONAR**: multilingual semantic retrieval (raw script)
- **CANINE**: multilingual character/form retrieval (raw Unicode)

After retrieval, LV3 applies **hybrid scoring** to the retrieved pairs (rough, iterative):

- orthography signal (n-grams + string ratio; prefers `translit` when available)
- sound signal (IPA when available)
- consonant skeleton signal

Stages are treated as **free text** and can be used to split corpora (e.g., `eng@old`, `eng@middle`, `eng@modern`).

Corpus spec format:

`<lang>[@<stage>][@<sonar_lang>]=<path>`

Where:

- `lang` is your project-level label (free text).
- `stage` is free text (defaults to `unknown`).
- `sonar_lang` is the SONAR language code (e.g., `eng_Latn`, `arb_Arab`). If omitted, LV3 uses a best-effort map for common languages.

## Getting full processed data (optional)

If you don't want to rebuild `data/processed/` locally, you can download a maintainer-published Release zip:

- `python "scripts/ingest/fetch_processed_release.py"`
- Details: `docs/RELEASE_ASSETS.md`

Temporary mirror (Google Drive):

- https://drive.google.com/drive/folders/13WZMxImkBikiyP7NXvcCth82bKJyUDj1?usp=sharing
- Download the folder (or its zip) and extract it into the repo root so paths like `data/processed/...` exist.

## Where to read next

- Pipeline details: `docs/INGEST.md`
- Data layout: `data/README.md`
- Processed data contract: `data/processed/README.md`
- Scoring model: `docs/SIMILARITY_SCORING_SPEC.md`
