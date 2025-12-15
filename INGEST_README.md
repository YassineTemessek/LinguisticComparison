# Ingest Plan (Prioritized Languages)

Primary hub:
- Classical / Qur'anic Arabic (Quranic Arabic Corpus morphology mirror)
- Iraqi Arabic dialect (open approximations via Wiktionary stardict; LDC dataset pending)
- Old Arabic epigraphy (Safaitic, Hismaic, Dadanitic/Taymanitic) as supporting

Secondary Semitic:
- Phoenician/Punic
- Imperial/Biblical Aramaic
- Classical Syriac (syriac-corpus + Peshitta; Wiktionary stardict)

Anchor/contrast:
- English (Old, Middle, Modern) — CMUdict/ipa-dict + Wiktionary stardict
- Latin (Classical) — Whitaker’s Words repo + Latin WordNet archive
- Classical Greek (Attic/Ionic) — Perseus/LSJ + Wiktionary stardict

## Files
- `src/ingest/arabic_ingest_stub.py` - Arabic hub (classical/qur, Iraqi, epigraphy)
- `src/ingest/punic_ingest_stub.py` - Phoenician/Punic/Neo-Punic
- `src/ingest/aramaic_ingest_stub.py` - Imperial/Biblical Aramaic, Syriac
- `src/ingest/english_ingest_stub.py` - Old/Middle/Modern English
- `src/ingest/latin_ingest_stub.py` - Classical Latin
- `src/ingest/greek_ingest_stub.py` - Classical Greek

## New utility scripts
- `scripts/convert_stardict.py` — convert extracted Wiktionary StarDict bundles to JSONL (`lemma`, `gloss`, `language`, `source=wiktionary-stardict`, `lemma_status=auto_brut`).
  Example: `python scripts/convert_stardict.py --root data/raw/wiktionary_extracted --out data/processed/wiktionary_stardict`
- `scripts/ingest_quran_morphology.py` — parse Quranic Arabic Corpus morphology mirror into unique lemma/root list.
  Example: `python scripts/ingest_quran_morphology.py --input data/raw/arabic/quran-morphology/quran-morphology.txt --output data/processed/arabic/quran_lemmas.jsonl`

## Current raw data on disk (open)
- Wiktionary stardict extractions: Arabic, Aramaic, Assyrian Neo-Aramaic, Classical Syriac, Ancient/Modern Greek, Latin, Middle/Old English, Akkadian, Ugaritic, Hebrew, Egyptian/Gulf/Hijazi/South Levantine Arabic, Ge’ez (`data/raw/wiktionary_extracted/...`).
- Quran morphology mirror (`data/raw/arabic/quran-morphology`).
- WordNet 3.1 dict (`data/raw/english/dict`).
- CMUdict, ipa-dict (`data/raw/english/...`).
- Perseus lexica (`data/raw/greek/lexica`).
- Whitaker’s Words repo (`data/raw/latin/words`), Latin WordNet archive (`data/raw/latin/latinwordnet-archive`).
- Syriac corpora (`data/raw/aramaic/syriac-corpus`, `data/raw/aramaic/peshitta`).

## Gaps / pending
- Kaikki/Wiktextract full dump: not yet downloaded (URLs failing).
- LisanCorpus / Iraqi Arabic LDC2025L01: still blocked (license/404).
- Whitaker’s SourceForge zip was invalid; using repo clone instead.

## Next steps to implement
1) Arabic ingest: run `ingest_quran_morphology.py` → seed lemma list; integrate AraMorph/Buckwalter once available; keep epigraphic loaders planned.
2) Wiktionary stardict: run `convert_stardict.py` over target languages; filter by concept categories and add POS mapping; mark `lemma_status=auto_brut`.
3) Aramaic/Syriac: mine `syriac-corpus` and `peshitta` for lemmas/frequencies; optionally add Payne-Smith/Dukhrana when available.
4) Anchor languages: parse Whitaker’s Words + Latin WordNet; Perseus/LSJ for Greek; map IPA via rule-based converters later.
5) English: merge CMUdict + ipa-dict; align with WordNet synsets.
6) Add normalization utilities (skeleton/ORT/articulatory) shared across ingests; expand test harness to validate schema compliance on the new JSONL outputs.

## New utility scripts (Codex)
- `Codex CLI/scripts/convert_stardict.py` — convert extracted Wiktionary StarDict bundles to JSONL (`lemma`, `gloss`, `language`, `source=wiktionary-stardict`, `lemma_status=auto_brut`). Example:  
  `python "Codex CLI/scripts/convert_stardict.py" --root data/raw/wiktionary_extracted --out data/processed/wiktionary_stardict`
- `Codex CLI/scripts/ingest_quran_morphology.py` — parse Quranic Arabic Corpus morphology mirror into unique lemma/root list. Example:  
  `python "Codex CLI/scripts/ingest_quran_morphology.py" --input data/raw/arabic/quran-morphology/quran-morphology.txt --output data/processed/arabic/quran_lemmas.jsonl`
- `Codex CLI/scripts/ingest_english_ipa.py` and `ingest_cmudict_ipa.py` — build Modern English IPA lexicons (ipa-dict and CMUdict).
- `Codex CLI/scripts/run_ingest_all.py` — orchestrator for Codex-side scripts (not src stubs).

## Current raw data on disk (open)
- Wiktionary stardict extractions: Arabic, Aramaic, Assyrian Neo-Aramaic, Classical Syriac, Ancient/Modern Greek, Latin, Middle/Old English, Akkadian, Ugaritic, Hebrew, Egyptian/Gulf/Hijazi/South Levantine Arabic, Ge’ez (`data/raw/wiktionary_extracted/...`).
- Quran morphology mirror (`data/raw/arabic/quran-morphology`).
- WordNet 3.1 dict (`data/raw/english/dict`).
- CMUdict, ipa-dict (`data/raw/english/...`).
- Perseus lexica (`data/raw/greek/lexica`).
- Whitaker’s Words repo (`data/raw/latin/words`), Latin WordNet archive (`data/raw/latin/latinwordnet-archive`).
- Syriac corpora (`data/raw/aramaic/syriac-corpus`, `data/raw/aramaic/peshitta`).
- Arabic roots corpora (shared resources): `C:/AI Projects/Resources/arabic_roots_hf`, `arabic_roots_taj` (KhorsiCorpus), `word_root_map.csv`.

## Gaps / pending
- Kaikki/Wiktextract full dump: not yet downloaded (URLs failing).
- LisanCorpus / Iraqi Arabic LDC2025L01: still blocked (license/404).
- Whitaker’s SourceForge zip was invalid; using repo clone instead.
- Arabic transliteration/IPA still coarse; need proper converter and stems/POS ingest from roots corpora.

## Expected lexeme fields (per Master Foundation)
- id, language (ISO/dialect code), stage, script, date_window
- orthography (raw), transliteration, ipa
- skeleton, ort.trace/flags, articulatory profile
- gloss, concept_id, sense_id, register, mapping_type
- lemma_anchor {lemma_form, lemma_pos, lemma_status, lemma_source}
- provenance {source, ref}
- notes

## Next steps to implement (Codex focus)
1) Arabic ingest: run Codex scripts for Quran morphology; add high-quality stems/POS + transliteration/IPA from roots corpora when ready.
2) Wiktionary stardict: convert (done); keep filtered JSONL for discovery; POS mapping as needed.
3) Aramaic/Syriac: mine `syriac-corpus` and `peshitta` for lemmas/frequencies; optionally add Payne-Smith/Dukhrana when available.
4) Anchor languages: Whitaker’s + Latin WordNet; Perseus/LSJ for Greek; IPA mapping in progress.
5) English: merge CMUdict + ipa-dict (done); POS alignment from WordNet; heuristics for colloquials.
6) Build and run RCG previews (`Codex CLI/scripts/match_preview.py`) to generate leads and avoid ingest-only loops.

*Updated by Codex agent (2025-12-03).*
