# Ingest & pipeline

This repo separates **code**, **tracked references**, and **local datasets**:

- `OpenAI/` and `Gemini/`: team workspaces (scripts + local outputs).
- `src/`: reusable code and stubs (future: shared library).
- `resources/`: tracked, lightweight reference assets (concept registry, anchors, small reference tables).
- `data/`: local datasets and generated tables (**not committed by default**; see `data/README.md`).

## What "ingest" means here

Ingest converts raw linguistic sources under `data/raw/` into consistent JSONL/CSV tables under `data/processed/` that downstream matchers can consume.

Canonical outputs are documented in `data/processed/README.md`.

## What "matching" means here (LV3)

Matching computes **separate component scores** (orthography vs sound) and a combined score to rank cross-language candidates per concept.

See `docs/SIMILARITY_SCORING_SPEC.md`.

## Run the pipeline (recommended)

1) Put datasets under `data/raw/` (see `data/README.md` for expected structure).

2) Build/refresh processed outputs:

- `python "OpenAI/scripts/run_ingest_all.py"`

Common options:

- List steps: `python "OpenAI/scripts/run_ingest_all.py" --list`
- Run only Arabic: `python "OpenAI/scripts/run_ingest_all.py" --only arabic`
- Run only English: `python "OpenAI/scripts/run_ingest_all.py" --only english`
- Use an external datasets folder: `python "OpenAI/scripts/run_ingest_all.py" --resources-dir "C:/AI Projects/Resources"`
- Produce a run manifest: enabled by default (disable with `--no-write-manifest`)

3) (Optional) Split large English JSONL for chunked matching:

- `python "OpenAI/scripts/split_processed_jsonl.py" data/processed/english/english_ipa_merged_pos.jsonl --lines 50000`

4) Run Gemini matching:

- `python "Gemini/scripts/run_full_matching_pipeline.py"`

## Validate outputs

- Validate canonical processed outputs (skips missing files): `python "OpenAI/scripts/validate_processed.py" --all`
- Fail on missing files too: `python "OpenAI/scripts/validate_processed.py" --all --require-files`

## Notes

- Some Arabic datasets may live outside the repo on your machine; for the related ingest scripts you can set `LC_RESOURCES_DIR` (e.g., `C:/AI Projects/Resources`) instead of copying files into `data/raw/`.
- `src/ingest/*_stub.py` are stubs/plans, not the current production ingest path (which is `OpenAI/scripts/*`).
