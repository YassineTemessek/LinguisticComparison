# Source code (`src/`)

`src/` is reserved for reusable code and modules (planned shared library).

Current status:

- `src/ingest/*_stub.py`: language ingest stubs/plans (not the active pipeline).
- Ingest now lives in LV0 (data core); LV3 consumes processed data.
- LV3 discovery retrieval modules live under `src/lv3/` (SONAR + CANINE + indexing helpers).
