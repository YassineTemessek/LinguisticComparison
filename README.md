# LinguisticComparison (LV3)

[![ci](https://github.com/YassineTemessek/LinguisticComparison/actions/workflows/ci.yml/badge.svg)](https://github.com/YassineTemessek/LinguisticComparison/actions/workflows/ci.yml)

Reproducible **linguistic ingest + discovery retrieval** pipeline producing **ranked cross-language candidates** and **QA-friendly outputs**.

LV3 is “discovery-first”: it surfaces candidates for human review; it does not claim historical directionality.

## What You Get

- Canonical, machine-readable lexeme tables under `data/processed/` (JSONL contract).
- Discovery outputs under `Gemini/output/` (ranked leads) and `OpenAI/output/` (manifests/caches/previews).
- Validation tooling to catch broken rows early.

## Repo Policy (Important)

- Large datasets live under `data/raw/` and are **not committed** by default.
- Generated outputs under `data/processed/`, `OpenAI/output/`, and `Gemini/output/` are **not committed** by default.

If you want to use prebuilt `data/processed/` outputs without rebuilding locally, see `docs/RELEASE_ASSETS.md` (Release zip + temporary Google Drive mirror).

## Layout

- `OpenAI/`: OpenAI-side scripts + local outputs
- `Gemini/`: Gemini-side scripts + local outputs
- `data/`: local datasets (ignored by default) and processed outputs docs (`data/README.md`, `data/processed/README.md`)
- `resources/`: tracked reference assets (small, versioned)
- `src/`: reusable code (LV3 discovery modules live here)
- `docs/`: project documentation (start with `docs/README.md`)

## Quickstart (Windows / PowerShell)

LV3’s recommended discovery mode is:

- **Meta SONAR**: multilingual semantic retrieval (raw script)
- **CANINE**: character-level form retrieval (raw Unicode)
- **Hybrid scoring (LV3)**: after retrieval, compute additional rough scores (orthography / IPA / skeleton) on the retrieved pairs

Stages are treated as **free text** (e.g., `old`, `middle`, `modern`, `classical`, `attic`, …), and are included in outputs for review and filtering.

1) Create a Python environment and install dependencies:

- `python -m venv .venv`
- Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
- Install base: `python -m pip install -r requirements.txt` (or `requirements.lock.txt` for pinned versions)
- Install embeddings (optional, required for SONAR/CANINE): `python -m pip install -r requirements.embeddings.txt`

2) Put datasets under `data/raw/` (see `data/README.md`).

3) Build/refresh processed tables (writes a manifest under `OpenAI/output/manifests/`):

- `python "OpenAI/scripts/run_ingest_all.py"`

4) Validate canonical processed outputs:

- `python "OpenAI/scripts/validate_processed.py" --all --require-files`

5) Run discovery retrieval (ranked leads):

This script expects corpus specs in the format:

`<lang>[@<stage>][@<sonar_lang>]=<path>`

Where `sonar_lang` is a SONAR code like `arb_Arab`, `eng_Latn`, `grc_Grek`. If omitted, LV3 uses a best-effort map for common languages; otherwise provide it explicitly.

Example (small/sample run using tracked samples):

```bash
python "Gemini/scripts/run_discovery_retrieval.py" \
  --source ara@modern@arb_Arab="resources/samples/processed/Arabic-English_Wiktionary_dictionary_stardict_filtered_sample.jsonl" \
  --target eng@modern@eng_Latn="resources/samples/processed/english_ipa_merged_pos_sample.jsonl" \
  --models sonar canine --topk 200 --max-out 200 --limit 200
```

Outputs are written to `Gemini/output/leads/` and embeddings/index caches to `OpenAI/output/`.
By default the script also adds a `hybrid` section per lead with component scores and a `combined_score` for rough ranking.

## Legacy (Classic Scoring Pipeline)

The classic LV3 scorer (orthography vs IPA sound scoring) remains available:

- `python "Gemini/scripts/run_full_matching_pipeline.py"`

## What this repo is (LV3)

LV3 is focused on **candidate discovery** and producing:

- embedding retrieval scores (SONAR meaning, CANINE form)
- ranked “leads” JSONL for human review
- QA/KPI helpers to keep the corpus stable

See `docs/START_HERE.md` and `docs/SIMILARITY_SCORING_SPEC.md`.
