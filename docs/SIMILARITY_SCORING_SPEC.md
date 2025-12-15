# LinguisticComparison LV3 — Similarity Scoring Spec

This repository (LV3) is a **similarity scoring engine + dataset registry + report outputs**.

Goal: for a shared list of **essential concepts** (Tier A/B/C), compare **Arabic (and Arabic-related languages)** against selected **Indo‑European languages** and produce:

- `orthography_score` (shape / spelling / consonantal skeleton echoes)
- `sound_score` (IPA / phonetic similarity)
- `combined_score` (a weighted combination for ranking)

This LV3 repo is **discovery-first**: it ranks and surfaces candidates for human review. It does **not** attempt to prove historical directionality. The deeper “language history” thesis lives in the separate LV4 workspace.

## What’s tracked vs local

- `resources/` (tracked): small, versioned reference inputs used by all pipelines.
  - Concept registry (Tier A/B/C).
  - Anchor tables (e.g., Latin anchors) and scaffolds.
- `data/` (local, git‑ignored): raw dumps and generated processed tables.
- `OpenAI/output/` and `Gemini/output/` (local, git‑ignored): run artifacts, previews, candidate lists.

## Core languages (LV3 v1)

This is the current “core set” for LV3 work (can expand later):

- Arabic
- Hebrew
- Aramaic / Syriac
- Latin
- Greek
- English (Old / Middle / Modern as separate stages when available)
- French
- German

## Key tracked inputs (resources/)

- `resources/concepts/concepts_v3_2_enriched.jsonl`: concept registry (Tier A/B/C) + metadata used to index comparisons.
- `resources/anchors/latin_anchor_table_v0_full.csv`: Latin lemma anchors aligned to concepts (quality tracked via `lemma_status`).

The concept registry is the **semantic join key**: everything downstream should be indexable by concept id (or a stable concept label).

## Canonical local outputs (data/processed/)

Ingest scripts normalize raw sources into consistent tables under `data/processed/` (see `data/processed/README.md` for the canonical file list).

The matcher should only depend on these *canonical outputs* (not intermediate scratch files).

## Similarity scoring model (LV3)

We always compute **separate component scores**, then a combined score.

### 1) `orthography_score` (shape)

Purpose: capture spelling/shape echoes (including “fossils” like silent letters, digraphs, and stable consonant clusters).

Inputs (depending on language/script availability):

- `lemma` (raw lemma)
- script-aware transliteration when available (e.g., Arabic Buckwalter)
- consonantal skeleton views (drop vowels/diacritics under a defined policy)

Implementation direction (v1):

- normalize text per script (casefold, strip punctuation, normalize diacritics)
- compute similarity from:
  - consonant-only edit distance
  - n‑gram overlap (2–4 grams)
  - optional “ORT” features when present

### 2) `sound_score` (phonetic)

Purpose: capture sound similarity across scripts and orthographies.

Inputs:

- `ipa_raw` (as found in sources)
- `ipa` (normalized IPA; no slashes, consistent spacing, consistent diacritics policy)

Implementation direction (v1):

- normalize IPA to a stable internal form
- compute similarity using a phoneme‑aware distance (initially a weighted edit distance; later: feature vectors / articulatory classes)

### 3) `combined_score`

Purpose: a single rankable score while preserving interpretability.

Default (v1) is a weighted blend:

- `combined_score = w_sound * sound_score + w_orth * orthography_score`

Weights should be configurable per run (and may differ by language/script coverage).

## Output artifacts (OpenAI/output/, Gemini/output/)

The default “product” of LV3 is a set of ranked candidate lists plus QA/KPI summaries.

Minimum useful artifacts:

- “leads” JSONL (top candidates per concept, with component scores + provenance)
- coverage/KPI report (how many concepts have usable lemmas/IPA per language)
- small previews (CSV/Markdown) for human review

## Reproducible runs

The pipeline is designed to be runnable end‑to‑end from a clean checkout + local datasets:

- Ingest: `python "OpenAI/scripts/run_ingest_all.py"`
- Matching: `python "Gemini/scripts/run_full_matching_pipeline.py"`

Each run should record:

- concept registry version
- anchor table version
- source versions (wiktionary dump date, dictionary repo commit, etc.)
- row counts per canonical processed output

## LV4 separation

The longer “theory / history / validation” document (`Master FoundationV3.2.txt`) is **not an LV3 requirement** and should live in the LV4 workspace (`Origin of Languages decoding LV4/`), while LV3 stays focused on **comparison + scoring + reporting**.
