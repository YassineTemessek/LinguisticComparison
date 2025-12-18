# Ingest documentation

Ingest and pipeline documentation lives in `docs/INGEST.md`.

## Quick commands

- Ingest (all): `python "scripts/ingest/run_ingest_all.py"`
- Ingest (skipping missing inputs): `python "scripts/ingest/run_ingest_all.py" --skip-missing-inputs`
- Validate canonical outputs: `python "scripts/ingest/validate_processed.py" --all`

## Where outputs go

- Canonical processed outputs: `data/processed/` (local, not committed by default)
- Run artifacts (manifests, caches): `outputs/` (local, not committed by default)

## Next step after ingest

Run LV3 discovery retrieval + hybrid scoring:

- `python "scripts/discovery/run_discovery_retrieval.py" --source ... --target ...`
