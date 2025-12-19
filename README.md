# LinguisticComparison (LV3) 🔎

[![ci](https://github.com/YassineTemessek/LinguisticComparison/actions/workflows/ci.yml/badge.svg)](https://github.com/YassineTemessek/LinguisticComparison/actions/workflows/ci.yml)
![level](https://img.shields.io/badge/level-LV3-6f42c1)
![license](https://img.shields.io/badge/license-MIT-blue)

Reproducible **discovery pipeline** that produces **ranked cross-language candidates** + **QA-friendly outputs**.

LV3 is “discovery-first”: results are **not polished/final**, but we still **compare and score** aggressively to see what the outputs look like.
LV3 does not claim historical directionality.

## Project map 🧭

- LV0 (data core): `https://github.com/YassineTemessek/LinguisticDataCore-LV0`
- LV2 (Arabic decoding & clustering): `https://github.com/YassineTemessek/Arabic-s-Words-decoding-LV2`
- LV3 (this repo): `https://github.com/YassineTemessek/LinguisticComparison`
- LV4 (validation blueprint): `https://github.com/YassineTemessek/OriginOfLanguagesLvl4`

## What You Get

- Canonical, machine-readable lexeme tables under `data/processed/` (JSONL contract).
- Discovery outputs under `outputs/` (ranked leads, manifests, caches, previews).
- Validation tooling to catch broken rows early.

## Tools (current focus) 🧰

- **SONAR (Meta)**: multilingual semantic retrieval (shared embedding space across many languages; supports raw script).
- **CANINE (Google)**: character-level form retrieval (raw Unicode, tokenizer-free).
- **Hybrid scoring (LV3)**: after retrieval, compute additional rough scores on retrieved pairs (orthography/IPA/skeleton/etc.).

Future (planned):

- **MMS (Meta)**: speech/audio representation and reconstruction (for spoken or unwritten languages).

## Repo Policy (Important)

- Large datasets live under `data/raw/` and are **not committed** by default.
- Generated outputs under `data/processed/` and `outputs/` are **not committed** by default.

If you want to use prebuilt `data/processed/` outputs without rebuilding locally, see `docs/RELEASE_ASSETS.md` (Release zip + temporary Google Drive mirror).

## Layout

- `scripts/`: runnable pipeline entrypoints (ingest + discovery)
- `outputs/`: local run artifacts (ignored by default)
- `data/`: local datasets (ignored by default) and processed outputs docs (`data/README.md`, `data/processed/README.md`)
- `resources/`: tracked reference assets (small, versioned)
- `src/`: reusable code (LV3 discovery modules live here)
- `docs/`: project documentation (start with `docs/README.md`)

## Pipeline (LV3) 🧱

1) **Get canonical processed data (LV0)**: fetch release bundles or build locally in LV0.
2) **Discovery retrieval**: SONAR (meaning) and/or CANINE (form) retrieve top-K candidates.
3) **Hybrid scoring**: compute additional rough signals on the retrieved pairs and re-rank.
4) **Review/QA**: inspect `outputs/leads/` and iterate on data + scoring.

## Quickstart 🚀

LV3’s recommended discovery mode is:

- **Meta SONAR**: multilingual semantic retrieval (raw script)
- **CANINE**: character-level form retrieval (raw Unicode)
- **Hybrid scoring (LV3)**: after retrieval, compute additional rough scores (orthography / IPA / skeleton) on the retrieved pairs

Stages are treated as **free text** (e.g., `old`, `middle`, `modern`, `classical`, `attic`, …), and are included in outputs for review and filtering.

1) Create a Python environment and install dependencies:

- `python -m venv .venv`
- Activate (PowerShell): `.\.venv\Scripts\Activate.ps1`
- Activate (bash/zsh): `source .venv/bin/activate`
- Install base: `python -m pip install -r requirements.txt` (or `requirements.lock.txt` for pinned versions)
- Install embeddings (optional, required for SONAR/CANINE): `python -m pip install -r requirements.embeddings.txt`

2) Put datasets under `data/raw/` (see `data/README.md`).

3) Get canonical processed data (LV0):

- Option A (recommended): use LV0 release bundles (fast): install LV0 package and run `ldc fetch ...`
- Option B: build locally in the LV0 repo (most reproducible): `ldc ingest --all`

4) Run discovery retrieval (ranked leads):

- `python "scripts/discovery/run_discovery_retrieval.py" ...`

This script expects corpus specs in the format:

`<lang>[@<stage>][@<sonar_lang>]=<path>`

Where `sonar_lang` is a SONAR code like `arb_Arab`, `eng_Latn`, `grc_Grek`. If omitted, LV3 uses a best-effort map for common languages; otherwise provide it explicitly.

Example (small/sample run using tracked samples):

```bash
python "scripts/discovery/run_discovery_retrieval.py" \
  --source ara@modern@arb_Arab="resources/samples/processed/Arabic-English_Wiktionary_dictionary_stardict_filtered_sample.jsonl" \
  --target eng@modern@eng_Latn="resources/samples/processed/english_ipa_merged_pos_sample.jsonl" \
  --models sonar canine --topk 200 --max-out 200 --limit 200
```

Outputs are written to `outputs/leads/` and embeddings/index caches to `outputs/`.
By default the script also adds a `hybrid` section per lead with component scores and a `combined_score` for rough ranking.

## Contributing

See `CONTRIBUTING.md`.

## Legacy (Classic Scoring Pipeline)

The classic LV3 scorer (orthography vs IPA sound scoring) remains available:

- `python "scripts/discovery/run_full_matching_pipeline.py"`

## What this repo is (LV3)

LV3 is focused on **candidate discovery** and producing:

- embedding retrieval scores (SONAR meaning, CANINE form)
- ranked “leads” JSONL for human review
- QA/KPI helpers to keep the corpus stable

See `docs/START_HERE.md` and `docs/SIMILARITY_SCORING_SPEC.md`.

## Contact 🤝

For collaboration: `yassine.temessek@hotmail.com`

## Suggested GitHub “About” 📝

Discovery pipeline (LV3): SONAR/CANINE retrieval + hybrid scoring to surface ranked cross-language candidate pairs.
