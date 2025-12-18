"""
Build a small QA manifest for `data/processed/` JSONL/CSV outputs.

This is meant to be run locally (datasets are not committed to Git by default).

Output (default): outputs/processed_manifest.json
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = ("id", "lemma", "language", "stage", "script", "source", "lemma_status")


def summarize_jsonl(path: Path, sample: int = 2000) -> dict[str, Any]:
    total = 0
    counts: dict[str, int] = {k: 0 for k in REQUIRED_FIELDS}
    optional = {
        "ipa": 0,
        "ipa_raw": 0,
        "pos": 0,
        "gloss_plain": 0,
        "gloss_html": 0,
    }
    key_counts: dict[str, int] = {}

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            if total <= sample:
                for k in rec.keys():
                    key_counts[k] = key_counts.get(k, 0) + 1

            for k in REQUIRED_FIELDS:
                if rec.get(k):
                    counts[k] += 1
            for k in optional:
                v = rec.get(k)
                if v and v != []:
                    optional[k] += 1

    def pct(n: int) -> float:
        return 0.0 if total == 0 else round(n * 100.0 / total, 2)

    return {
        "type": "jsonl",
        "path": str(path.as_posix()),
        "bytes": path.stat().st_size,
        "lines": total,
        "required_coverage_pct": {k: pct(v) for k, v in counts.items()},
        "optional_coverage_pct": {k: pct(v) for k, v in optional.items()},
        "keys_sampled_top": sorted(key_counts.items(), key=lambda kv: kv[1], reverse=True)[:25],
    }


def summarize_csv(path: Path) -> dict[str, Any]:
    total = 0
    headers: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        for i, row in enumerate(reader):
            if i == 0:
                headers = row
                continue
            total += 1
    return {
        "type": "csv",
        "path": str(path.as_posix()),
        "bytes": path.stat().st_size,
        "rows": total,
        "headers": headers,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("data/processed"))
    ap.add_argument("--out", type=Path, default=Path("outputs/processed_manifest.json"))
    ap.add_argument("--sample", type=int, default=2000, help="How many rows to sample for key presence stats.")
    ap.add_argument("--include-intermediate", action="store_true", help="Include `data/processed/_intermediate` in the manifest.")
    args = ap.parse_args()

    root = args.root
    items: list[dict[str, Any]] = []

    if not root.exists():
        raise SystemExit(f"Missing folder: {root}")

    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if "_parts" in path.parts:
            continue
        if (not args.include_intermediate) and ("_intermediate" in path.parts):
            continue
        if path.suffix.lower() == ".jsonl":
            items.append(summarize_jsonl(path, sample=args.sample))
        elif path.suffix.lower() == ".csv":
            items.append(summarize_csv(path))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"root": str(root.as_posix()), "items": items}
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote manifest with {len(items)} items to {args.out}")


if __name__ == "__main__":
    main()
