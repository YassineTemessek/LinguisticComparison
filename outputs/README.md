# Outputs

This folder contains **generated artifacts** produced by repository scripts (ingest + discovery).

By default, the actual output files are not committed to Git (see `.gitignore`). Keep this folder for local runs, sharing, and debugging.

Typical subfolders (created locally by scripts):

- `outputs/manifests/`: ingest run manifests
- `outputs/embeddings/`: cached SONAR/CANINE vectors
- `outputs/indexes/`: FAISS indexes
- `outputs/leads/`: ranked discovery leads (JSONL)
