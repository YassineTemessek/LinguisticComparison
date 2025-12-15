# Data folder

This project uses large linguistic datasets under `data/`. They are intentionally **not** committed to GitHub by default (see `.gitignore`) to keep the repository lightweight.

## `data/raw/` (inputs)

**What it is:** Original, third-party source files as downloaded/extracted (TSV/XML/JSON/etc.). These are treated as read-only inputs.

**What it's for:** Feeding the ingestion/normalization scripts to create consistent machine-readable datasets for matching and analysis.

**Examples in this project:** Wiktionary dictionary dumps, Greek lexica XML, IPA dictionaries, Aramaic/Syriac corpora, and other language resources.

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

## How to use

- Put downloaded sources under `data/raw/`.
- Run the ingest scripts (see `OpenAI/scripts/run_ingest_all.py`) to generate/refresh `data/processed/`.
- Downstream preview/matching scripts consume `data/processed/` and `resources/` (and write results under `OpenAI/output/` or `Gemini/output/`).
