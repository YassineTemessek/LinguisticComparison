# Start Here (LV3)

This repo is a **discovery engine** for linguistic comparison.

The workflow is always:

1) **Get processed data** from LV0 (canonical tables under `data/processed/`).
2) **Discovery retrieval** consumes the canonical tables to produce **ranked leads** under `outputs/` (not committed).

## What "good" looks like

- `data/processed/*` files exist and pass validation (`id`, `lemma`, etc. are present; IPA is normalized).
- Discovery outputs contain lead rows with `sonar` and/or `canine` scores plus provenance fields so results are traceable.
- Each LV0 ingest run produces a manifest JSON under LV0 `outputs/manifests/`.

## Collaboration-friendly samples (tracked)

Full datasets are not committed by default, but small samples are tracked under `resources/samples/processed/`.

- Run a quick discovery smoke test on samples:
  - `python "scripts/discovery/run_discovery_retrieval.py" --source ara@modern@arb_Arab="resources/samples/processed/Arabic-English_Wiktionary_dictionary_stardict_filtered_sample.jsonl" --target eng@modern@eng_Latn="resources/samples/processed/english_ipa_merged_pos_sample.jsonl" --models sonar canine --topk 200 --max-out 200 --limit 200`

## Core commands

- Get/build canonical processed outputs: see `docs/LV0_DATA_CORE.md`
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

See `docs/LV0_DATA_CORE.md` for fetching LV0 release bundles.

## Where to read next

- Pipeline details: `docs/INGEST.md`
- LV0 data core: `docs/LV0_DATA_CORE.md`
- Data layout: `data/README.md`
- Processed data contract: `data/processed/README.md`
- Scoring model: `docs/SIMILARITY_SCORING_SPEC.md`
