# LinguisticComparison LV3 — Similarity Scoring Spec

This repository (LV3) is a **similarity scoring engine + dataset registry + report outputs**.

Goal: compare **Arabic (and Arabic-related languages)** against selected **Indo‑European languages** (and more) and produce ranked candidate matches for human review.

LV3 supports two discovery strategies:

1) **Embedding-first retrieval (recommended):**
   - `sonar_score` (multilingual semantic similarity; raw script)
   - `canine_score` (character/form similarity; raw Unicode)
   - Category labels for triage (`strong_union`, `semantic_only`, `form_only`)

2) **Classic similarity scoring (legacy / secondary signal):**
   - `orthography_score` (shape / spelling / consonantal skeleton echoes)
   - `sound_score` (IPA / phonetic similarity)
   - `combined_score` (a weighted combination for ranking)

This LV3 repo is **discovery-first**: it ranks and surfaces candidates for human review. It does **not** attempt to prove historical directionality. The deeper “language history” thesis lives in the separate LV4 workspace.

## What’s tracked vs local

- `resources/` (tracked): small, versioned reference inputs used by all pipelines.
  - Concept registry (Tier A/B/C).
  - Anchor tables (e.g., Latin anchors) and scaffolds.
- `data/` (local, git‑ignored): raw dumps and generated processed tables.
- `outputs/` and `outputs/` (local, git‑ignored): run artifacts, previews, candidate lists.

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

## Embedding-first retrieval (SONAR + CANINE)

This is the primary LV3 discovery mode.

- **SONAR** provides multilingual sentence/word embeddings; similarity is cosine/inner-product over L2-normalized vectors.
- **CANINE** provides character-level embeddings over raw Unicode strings; similarity is cosine/inner-product over L2-normalized vectors.

In practice LV3 uses embedding retrieval to generate *candidates*, then applies a lightweight **hybrid scoring** pass on the retrieved pairs to produce additional component scores and a rough `combined_score` for ranking/inspection.

Entry point:

- `scripts/discovery/run_discovery_retrieval.py`

### Hybrid scoring (after retrieval)

Hybrid scoring is intentionally simple (LV3 “what results look like” iteration):

- `orthography`: character n-gram overlap + string ratio (prefers `translit` when available)
- `sound`: IPA similarity when present (`ipa`/`ipa_raw`)
- `skeleton`: consonant skeleton similarity (derived from `ipa`/`translit`/`lemma`)

The script produces `hybrid.combined_score` by a weighted average of available signals, including SONAR/CANINE retrieval scores.

Corpus identity:

- LV3 treats `lang` and `stage` as **free text** labels (e.g., `eng@old`, `eng@modern`, `grc@attic`).

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

## Output artifacts (outputs/, outputs/)

The default “product” of LV3 is a set of ranked candidate lists plus QA/KPI summaries.

Minimum useful artifacts:

- “leads” JSONL (ranked candidates with retrieval/scoring signals + provenance)
- coverage/KPI report (how many concepts have usable lemmas/IPA per language)
- small previews (CSV/Markdown) for human review

## Reproducible runs

The pipeline is designed to be runnable end‑to‑end from a clean checkout + local datasets:

- Processed data: build/fetch via LV0 (`docs/LV0_DATA_CORE.md`)
- Discovery retrieval: `python "scripts/discovery/run_discovery_retrieval.py" ...`
- Legacy matcher: `python "scripts/discovery/run_full_matching_pipeline.py"`

Each run should record:

- concept registry version
- anchor table version
- source versions (wiktionary dump date, dictionary repo commit, etc.)
- row counts per canonical processed output

## LV4 separation

The longer “theory / history / validation” document (`Master FoundationV3.2.txt`) is **not an LV3 requirement** and should live in the LV4 workspace (`Origin of Languages decoding LV4/`), while LV3 stays focused on **comparison + scoring + reporting**.
