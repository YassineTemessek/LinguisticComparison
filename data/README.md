# Data folder

This project uses large linguistic datasets under `data/`. They are intentionally **not** committed to GitHub by default (see `.gitignore`) to keep the repository lightweight.

## `data/raw/` (inputs)

**What it is:** Original, third-party source files as downloaded/extracted (TSV/XML/JSON/etc.). These are treated as read-only inputs.

**What it's for:** Feeding the ingestion/normalization scripts to create consistent machine-readable datasets for matching and analysis.

**Examples in this project:** Wiktionary dictionary dumps, Greek lexica XML, IPA dictionaries, Aramaic/Syriac corpora, and other language resources.

## Expected folder layout (LV3)

This repository expects datasets under `data/raw/` in a stable, script-friendly structure:

- `data/raw/arabic/quran-morphology/quran-morphology.txt`
- `data/raw/arabic/word_root_map.csv` (used to build `data/processed/arabic/word_root_map_filtered.jsonl`)
- `data/raw/arabic/arabic_roots_hf/train-00000-of-00001.parquet` (used to build `data/processed/arabic/hf_roots.jsonl`)
- `data/raw/english/ipa-dict/data/en_US.txt` and/or `data/raw/english/ipa-dict/data/en_UK.txt`
- `data/raw/english/cmudict/cmudict.dict`
- `data/raw/wiktionary_extracted/` (StarDict-extracted Wiktionary dictionaries; used by `scripts/ingest/convert_stardict.py`)

If you keep datasets outside the repo, you can:

- Run specific scripts with `--input <path>`, or
- Set `LC_RESOURCES_DIR` (or pass `--resources-dir` to `scripts/ingest/run_ingest_all.py`) for Arabic "Resources-style" inputs.

## `data/processed/` (outputs)

**What it is:** Cleaned, normalized, merged datasets produced from `data/raw/` (typically `.jsonl`, `.json`, `.csv`). These files are designed to be stable "working tables" for the pipeline.

**What it's for:**

- Fast loading for experiments (matching, previews, statistics).
- Consistent schemas across languages (e.g., normalized lemma/IPA/metadata fields).
- Reproducible inputs for downstream scripts (so you don't re-parse huge raw files every run).

**Examples in this project:** Arabic roots/word-root mappings, English IPA merges (with/without POS), and other language-specific normalized outputs.

## Tracked references (not in `data/`)

Some small, stable resources are shared via Git and live under `resources/` instead of `data/`:

- `resources/concepts/` (concept registry used for semantic gating/mapping)
- `resources/anchors/` (anchor tables/scaffolds)
- `resources/samples/processed/` (small samples of canonical processed JSONL for collaboration)

## How to use

- Put downloaded sources under `data/raw/`.
- Run the ingest scripts (see `scripts/ingest/run_ingest_all.py`) to generate/refresh `data/processed/`.
- Downstream preview/matching scripts consume `data/processed/` and `resources/` (and write results under `outputs/` or `outputs/`).
