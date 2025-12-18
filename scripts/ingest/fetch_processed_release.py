"""
Download a prebuilt `data/processed/` bundle from GitHub Releases and extract it.

This repo intentionally does not commit large processed datasets. The recommended
collaboration pattern is:

  - small samples: `resources/samples/processed/*_sample.jsonl` (committed)
  - full processed outputs: GitHub Release asset (zip)

By default this script downloads:
  https://github.com/<repo>/releases/latest/download/processed_canonicals.zip
and extracts it into the repo root so paths like `data/processed/...` land in
the correct place.
"""

from __future__ import annotations

import argparse
import os
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_REPO = "YassineTemessek/LinguisticComparison"
DEFAULT_ASSET = "processed_canonicals.zip"


@dataclass(frozen=True)
class DownloadResult:
    url: str
    path: Path
    bytes: int


def download(url: str, out_path: Path) -> DownloadResult:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "LinguisticComparison/processed-fetch"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    out_path.write_bytes(data)
    return DownloadResult(url=url, path=out_path, bytes=len(data))


def safe_extract(zip_path: Path, dest_dir: Path, *, overwrite: bool) -> dict[str, int]:
    extracted = 0
    skipped = 0
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            name = member.filename
            if not name or name.endswith("/"):
                continue
            target = (dest_dir / name).resolve()
            if not str(target).startswith(str(dest_dir.resolve())):
                raise SystemExit(f"Refusing to extract path outside dest: {name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and not overwrite:
                skipped += 1
                continue
            with zf.open(member) as src, target.open("wb") as dst:
                dst.write(src.read())
            extracted += 1
    return {"extracted_files": extracted, "skipped_files": skipped}


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--repo", type=str, default=DEFAULT_REPO, help="GitHub repo in owner/name form.")
    ap.add_argument("--asset", type=str, default=DEFAULT_ASSET, help="Release asset filename.")
    ap.add_argument("--url", type=str, default=None, help="Optional direct URL override (skips --repo/--asset).")
    ap.add_argument("--dest", type=Path, default=repo_root, help="Destination directory for extraction.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files when extracting.")
    ap.add_argument("--out-zip", type=Path, default=Path("outputs/downloads/processed_canonicals.zip"), help="Download target path.")
    args = ap.parse_args()

    url = args.url or f"https://github.com/{args.repo}/releases/latest/download/{args.asset}"
    out_zip = args.out_zip if args.out_zip.is_absolute() else (repo_root / args.out_zip)

    # Allow token-auth if user sets it (useful for private repos).
    token = os.environ.get("GITHUB_TOKEN")
    if token and args.url is None:
        opener = urllib.request.build_opener()
        opener.addheaders = [("Authorization", f"token {token}")]
        urllib.request.install_opener(opener)

    res = download(url, out_zip)
    print(f"Downloaded: {res.url}")
    print(f"Saved: {res.path} ({res.bytes} bytes)")

    dest = args.dest if args.dest.is_absolute() else (repo_root / args.dest)
    stats = safe_extract(out_zip, dest, overwrite=bool(args.overwrite))
    print(f"Extracted files: {stats['extracted_files']}")
    print(f"Skipped existing: {stats['skipped_files']}")


if __name__ == "__main__":
    main()

