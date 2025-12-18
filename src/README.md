# Source code (`src/`)

`src/` is reserved for reusable code and modules (planned shared library).

Current status:

- `src/ingest/*_stub.py`: language ingest stubs/plans (not the active pipeline).
- The active ingestion pipeline lives under `scripts/ingest/`.
- LV3 discovery retrieval modules live under `src/lv3/` (SONAR + CANINE + indexing helpers).
