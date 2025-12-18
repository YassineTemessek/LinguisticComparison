# Next Data Improvements (ordered)

These are the next concrete tasks to improve **data quality and usefulness** (not just code).

## 1) Rebuild + make validation “green”

Goal: every canonical processed JSONL passes `validate_processed.py` (no missing required fields, no malformed rows).

- Rebuild Arabic only (using your external folder): `python "scripts/ingest/run_ingest_all.py" --only arabic --resources-dir "C:/AI Projects/Resources" --require-inputs --fail-fast`
- Validate: `python "scripts/ingest/validate_processed.py" --all --require-files`

If validation still fails after rebuild, fix the ingest scripts to:

- Skip rows with empty/invalid `lemma`.
- Guarantee `id` is present (via `processed_schema.ensure_min_schema`).
- Normalize `ipa_raw`/`ipa` consistently.

## 2) Add KPI coverage reports (per language + per concept)

Goal: measure improvements with numbers (coverage, IPA availability, POS availability, duplicates).

Use: `python "scripts/ingest/kpi_processed.py" --all` (writes JSON + CSV under `outputs/`).

It should output a CSV/JSON report with:

- Row counts per canonical file
- % missing IPA per language/source
- % missing POS where expected
- # duplicates by `(language, stage, lemma)` or `id`
- Concept coverage: how many concepts have at least N candidate lexemes per language

## 3) Tighten Wiktionary/StarDict filtering rules

Goal: reduce obvious noise that pollutes top-ranked candidates.

Improve `scripts/ingest/filter_stardict.py` to better exclude:

- Abbreviations/initialisms
- Proper names (where detectable)
- Entries with no real lemma content after normalization

Also improve POS normalization/mapping so `pos` becomes more useful for semantic gating.

## 4) Improve IPA normalization and fallbacks

Goal: make `sound_score` stronger and more comparable across sources.

- Strengthen IPA normalization (consistent whitespace/diacritics policy, strip wrappers, stable symbols).
- Add fallbacks when IPA is missing (language-specific transliteration or phonetic approximations where justified).

## 5) Dedupe + provenance tightening

Goal: avoid repeated entries across sources and keep traceability.

- Deduplicate near-identical records (keep best provenance).
- Ensure every record has stable `source` + (optional) `source_ref` fields so you can trace back to origin lines/keys.
