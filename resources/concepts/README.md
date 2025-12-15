# Concepts (tracked)

This folder contains the **tracked concept registry** used by the project for semantic mapping/gating.

Canonical files:

- `concepts_v3_2_enriched.jsonl`: current concept registry used by matching scripts.
- `concepts_v3_2_normalized.jsonl` (+ `.csv`): the normalized base list (useful for maintenance / regeneration).

Downstream scripts should prefer reading concepts from `resources/concepts/` (not from `data/processed/`).

