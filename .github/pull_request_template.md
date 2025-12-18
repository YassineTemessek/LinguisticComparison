## Summary

Explain what changed and why.

## How to test

- [ ] `python -m compileall scripts/ingest scripts/discovery src`
- [ ] `python scripts/ingest/run_ingest_all.py --list`
- [ ] `python scripts/ingest/validate_processed.py --all`

## Notes

- Any changes to canonical output contracts? (paths/schema)
- Any new datasets required under `data/raw/`?

