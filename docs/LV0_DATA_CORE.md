# LV0 Data Core

This repo (LV3) **does not** own ingest anymore.

Raw → processed canonical datasets live in the LV0 repo:

- `https://github.com/YassineTemessek/LinguisticDataCore-LV0`

Use LV0 to build or fetch processed data, then run LV3 discovery on top.

## Recommended: fetch LV0 release bundles

1) Install LV0 package (editable):

- `python -m pip install -e /path/to/LinguisticDataCore-LV0`

2) Fetch and extract latest release assets into your LV3 repo root:

- `ldc fetch --release latest --dest .`

This creates/refreshes `data/processed/...`.

## Alternative: build processed data locally (LV0)

In the LV0 repo:

- `ldc ingest --all`
- `ldc validate --all --require-files`
- `ldc package --version YYYY.MM.DD`

