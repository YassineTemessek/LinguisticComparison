# Processed data

`data/processed/` contains **machine-readable outputs** produced from `data/raw/` by the ingestion/enrichment scripts. These files are what downstream matching/analysis scripts should consume.

This repository does **not** commit the datasets themselves by default (see `.gitignore`), but we keep this README in Git to document the contract and expected outputs.

## Canonical outputs (downstream should use these)

These are the “stable targets” we optimize for and keep consistent across versions:

- `data/processed/arabic/quran_lemmas_enriched.jsonl` (Quran lemmas + translit + IPA)
- `data/processed/arabic/hf_roots.jsonl` (Arabic roots dataset with translit + IPA)
- `data/processed/english/english_ipa_merged_pos.jsonl` (merged English IPA lexicon with POS)
- `data/processed/wiktionary_stardict/filtered/*_filtered.jsonl` (filtered Wiktionary stardict exports for languages where we run filtering)
- `data/processed/concepts/concepts_v3_2_enriched.jsonl` (concept registry used for semantic gating/mapping)
- `data/processed/anchors/*.csv` (anchor tables/scaffolds)
- `data/processed/arabic/word_root_map_filtered.jsonl` (word→root mapping with high-noise rows removed; adds `type`)

Downstream scripts should prefer these paths and avoid hard-coding intermediate filenames.

## Common JSONL schema (target contract)

For JSONL lexeme files, we aim for a shared minimal schema:

- Always present: `id`, `lemma`, `language`, `stage`, `script`, `source`, `lemma_status`
- Optional but normalized when present:
  - `ipa_raw` + `ipa` (where `ipa` is normalized; no surrounding `/.../` or `[...]`)
  - `pos` (always a list)
  - `gloss_html` + `gloss_plain` (when a gloss exists)

## Intermediate outputs (debugging / pipeline stages)

These are useful for auditability, but should be treated as rebuildable intermediates:

- Stage-by-stage files under `data/processed/_intermediate/`
- Wiktionary StarDict stages under `data/processed/wiktionary_stardict/{raw,enriched,normalized}/`
- Chunked splits under `data/processed/_parts/` (generate on demand; do not treat as canonical storage)

For English, the intended build order is:

- `data/processed/_intermediate/english/english_ipa.jsonl` + `data/processed/_intermediate/english/english_cmudict_ipa.jsonl` (base sources)
- `*_with_pos.jsonl` via `enrich_english_pos.py`
- `data/processed/_intermediate/english/english_ipa_merged.jsonl` via `merge_english_ipa_sources.py`
- `data/processed/english/english_ipa_merged_pos.jsonl` via `english_pos_fallback.py` (fills missing POS heuristically)

For chunked processing (optional), prefer putting splits under:

- `data/processed/_parts/<stem>/...`

Use `Codex CLI/scripts/split_processed_jsonl.py` to generate these without cluttering language folders.

## Folder layout (summary)

- Canonical: language folders (`arabic/`, `english/`, `concepts/`, `anchors/`) + `wiktionary_stardict/filtered/`
- Intermediate: `data/processed/_intermediate/`
- Chunked parts: `data/processed/_parts/`
- Wiktionary staging: `data/processed/wiktionary_stardict/{raw,enriched,normalized,filtered}/`

## Naming + lifecycle conventions

- Canonical outputs: stable names (no timestamps), consistent schema, safe to depend on.
- Intermediate outputs: stage suffixes (`_normalized`, `_enriched`, `_with_pos`) and/or generated folders (`*_parts/`).
- Previews/checkpoints: should live under `Codex CLI/output/` or `Gemini CLI/output/`, not `data/processed/`.
