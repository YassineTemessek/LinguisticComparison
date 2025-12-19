# Data ingest (LV0) and LV3 pipeline

LV3 no longer owns ingest.

Raw → processed canonical datasets live in LV0:

- `https://github.com/YassineTemessek/LinguisticDataCore-LV0`

See `docs/LV0_DATA_CORE.md` for how to fetch/build processed data.

## LV3 pipeline (discovery)

LV3 consumes canonical processed tables (from LV0) and runs:

- SONAR/CANINE retrieval (high recall)
- Hybrid scoring (rough component scores + combined score)
- Output ranked leads under `outputs/`
