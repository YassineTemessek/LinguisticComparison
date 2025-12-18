"""
Package selected `data/processed/` outputs into a single zip for GitHub Releases.

This repo intentionally does not commit large processed datasets. Instead:
  - commit collaboration samples under `resources/samples/processed/`
  - publish full processed canonicals as a GitHub Release asset (zip)

Typical usage (after rebuilding processed outputs locally):
  python scripts/ingest/package_processed_release.py --all

Then upload the produced zip to a GitHub Release (see docs/RELEASE_ASSETS.md).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_CANONICAL: tuple[Path, ...] = (
    Path("data/processed/arabic/quran_lemmas_enriched.jsonl"),
    Path("data/processed/arabic/hf_roots.jsonl"),
    Path("data/processed/arabic/word_root_map_filtered.jsonl"),
    Path("data/processed/english/english_ipa_merged_pos.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Latin-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Ancient_Greek-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Arabic-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/concepts/concepts_v3_2_enriched.jsonl"),
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_targets(repo_root: Path, *, all_canonical: bool, paths: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    if all_canonical:
        out.extend(repo_root / p for p in DEFAULT_CANONICAL)
    out.extend(p if p.is_absolute() else (repo_root / p) for p in paths)
    seen: set[str] = set()
    deduped: list[Path] = []
    for p in out:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped


def try_git_rev(repo_root: Path) -> str | None:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_root), check=False, capture_output=True, text=True)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="Optional paths to include (in addition to --all).")
    ap.add_argument("--all", action="store_true", help="Include the canonical processed outputs list.")
    ap.add_argument("--require-files", action="store_true", help="Fail if any requested file is missing.")
    ap.add_argument(
        "--out-zip",
        type=Path,
        default=Path("outputs/release_assets/processed_canonicals.zip"),
        help="Zip output path.",
    )
    ap.add_argument(
        "--out-manifest",
        type=Path,
        default=Path("outputs/release_assets/processed_canonicals_manifest.json"),
        help="Manifest JSON output path (file list, sizes, hashes).",
    )
    args = ap.parse_args()

    targets = iter_targets(repo_root, all_canonical=bool(args.all), paths=args.paths)
    if not targets:
        raise SystemExit("No files selected. Pass paths or use --all.")

    missing = [str(p) for p in targets if not p.exists()]
    if missing and args.require_files:
        raise SystemExit("Missing required files:\n" + "\n".join(missing))

    out_zip = args.out_zip if args.out_zip.is_absolute() else (repo_root / args.out_zip)
    out_manifest = args.out_manifest if args.out_manifest.is_absolute() else (repo_root / args.out_manifest)
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.parent.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, Any]] = []
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for abs_path in targets:
            if not abs_path.exists():
                items.append({"path": str(abs_path), "missing": True})
                continue

            rel_path = abs_path.resolve().relative_to(repo_root.resolve())
            arcname = str(rel_path).replace("\\", "/")
            zf.write(abs_path, arcname=arcname)
            st = abs_path.stat()
            items.append({"path": arcname, "bytes": st.st_size, "sha256": _sha256(abs_path)})

    payload = {
        "type": "processed_release_bundle",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repo": "YassineTemessek/LinguisticComparison",
        "git_rev": try_git_rev(repo_root),
        "zip_path": str(out_zip),
        "files": items,
    }

    out_manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {out_zip}")
    print(f"Wrote: {out_manifest}")


if __name__ == "__main__":
    main()

