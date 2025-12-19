# Ingest documentation

LV3 does not own ingest anymore.

Raw → processed canonical datasets live in LV0:

- `https://github.com/YassineTemessek/LinguisticDataCore-LV0`

See `docs/LV0_DATA_CORE.md`.

## Quick commands

- Fetch LV0 release bundles: `ldc fetch --release latest --dest .`

## Where outputs go

- Canonical processed outputs: `data/processed/` (local, not committed by default)
- Run artifacts (leads, caches): `outputs/` (local, not committed by default)

## Next step after ingest

Run LV3 discovery retrieval + hybrid scoring:

- `python "scripts/discovery/run_discovery_retrieval.py" --source ... --target ...`
