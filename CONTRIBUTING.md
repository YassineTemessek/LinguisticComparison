# Contributing

## Project goal

LV3 produces (discovery-first):

- Canonical processed tables under `data/processed/`
- Ranked “lead” candidates under `outputs/`
- Local caches/artifacts under `outputs/` (manifests, embeddings, indexes, previews)

LV3 is **iterative discovery**: we compare + score aggressively to see what results look like.
Stricter “validation/proof” lives in LV4.

## Data policy

Large datasets under `data/raw/` and generated artifacts under `data/processed/`, `outputs/`, and `outputs/` are intentionally not committed by default.

## Setup

- Create venv: `python -m venv .venv`
- Activate (PowerShell): `.\.venv\Scripts\Activate.ps1`
- Install deps: `python -m pip install -r requirements.txt`
- If you want SONAR/CANINE discovery runs: `python -m pip install -r requirements.embeddings.txt`

## Run + validate

- Get/build processed data via LV0: see `docs/LV0_DATA_CORE.md`
- Discover + score (SONAR/CANINE retrieval + hybrid scoring): `python "scripts/discovery/run_discovery_retrieval.py" --source ... --target ...`
- Legacy matcher (classic scoring): `python "scripts/discovery/run_full_matching_pipeline.py"`

## Where to start (recommended)

1) Read `docs/START_HERE.md`
2) Run discovery on tracked samples (fast smoke test):

```bash
python "scripts/discovery/run_discovery_retrieval.py" \
  --source ara@modern@arb_Arab="resources/samples/processed/Arabic-English_Wiktionary_dictionary_stardict_filtered_sample.jsonl" \
  --target eng@modern@eng_Latn="resources/samples/processed/english_ipa_merged_pos_sample.jsonl" \
  --models sonar canine --topk 200 --max-out 200 --limit 200
```

## Conventions

- Treat `lang`/`stage` as free-text labels in LV3, but keep them stable once used in outputs.
- Prefer adding new signals as additional `hybrid.components.*` fields rather than replacing existing fields.
- Keep CI lightweight: do not require model downloads in CI.

## Before opening a PR

- Ensure CI passes (compile).
- Update docs when you change file contracts or CLI behavior.
- Keep generated data out of git; add/update docs instead (`data/README.md`, `outputs/README.md`, `outputs/README.md`).
