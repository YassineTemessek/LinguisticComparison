## Summary

Explain what changed and why.

## How to test

- [ ] `python -m compileall OpenAI/scripts Gemini/scripts src`
- [ ] `python OpenAI/scripts/run_ingest_all.py --list`
- [ ] `python OpenAI/scripts/validate_processed.py --all`

## Notes

- Any changes to canonical output contracts? (paths/schema)
- Any new datasets required under `data/raw/`?

