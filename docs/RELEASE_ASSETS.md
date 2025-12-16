# Release assets (full processed datasets)

This repo intentionally does **not** commit large `data/processed/` outputs.

Collaboration model:

- Small samples (tracked): `resources/samples/processed/*_sample.jsonl`
- Full processed outputs (distributed): **GitHub Release asset zip**

## Create a bundle (maintainers)

1) Rebuild processed outputs locally:

- `python OpenAI/scripts/run_ingest_all.py --require-inputs --fail-fast`
- `python OpenAI/scripts/validate_processed.py --all --require-files`

2) Package canonicals into a zip:

- `python OpenAI/scripts/package_processed_release.py --all --require-files`

This writes:

- `OpenAI/output/release_assets/processed_canonicals.zip`
- `OpenAI/output/release_assets/processed_canonicals_manifest.json`

3) Upload the zip to a GitHub Release

Create a release (tag any version you want) and upload `processed_canonicals.zip` as an asset.

## Download a bundle (contributors)

If a Release exists with an asset named `processed_canonicals.zip`:

- `python OpenAI/scripts/fetch_processed_release.py`

It downloads the zip and extracts it into the repo root, creating `data/processed/...`.

To avoid overwriting existing files, extraction skips files by default; pass `--overwrite` to replace.

## Temporary processed-data mirror (Google Drive)

Until a GitHub Release asset is available (or if you prefer Drive), maintainers may also share a Drive folder:

- https://drive.google.com/drive/folders/13WZMxImkBikiyP7NXvcCth82bKJyUDj1?usp=sharing

Notes:

- Drive links are convenient but not strongly versioned; prefer Release assets for reproducibility.
- After download, extract into the repo root so `data/processed/...` and any other included paths land correctly.
