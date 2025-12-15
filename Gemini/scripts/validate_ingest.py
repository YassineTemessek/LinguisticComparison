"""
Validate processed JSONL files against the project's shared minimal schema.

Required fields:
  id, lemma, language, stage, script, source, lemma_status

Optional normalization checks (if present):
  - pos is a list
  - ipa is not wrapped in /.../ or [...]

Usage:
  python validate_ingest.py data/processed/english/english_ipa_merged_pos.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = ("id", "lemma", "language", "stage", "script", "source", "lemma_status")


def is_wrapped_ipa(value: str) -> bool:
    value = (value or "").strip()
    return len(value) >= 2 and ((value[0] == "/" and value[-1] == "/") or (value[0] == "[" and value[-1] == "]"))


def validate(path: Path, *, sample_errors: int = 10) -> int:
    total = 0
    invalid = 0
    missing_required = {k: 0 for k in REQUIRED}
    pos_type_errors = 0
    wrapped_ipa = 0

    with path.open("r", encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                invalid += 1
                if invalid <= sample_errors:
                    print(f"[line {line_num}] invalid JSON")
                continue

            row_errors: list[str] = []
            for k in REQUIRED:
                if not rec.get(k):
                    missing_required[k] += 1
                    row_errors.append(f"missing:{k}")

            if "pos" in rec and not isinstance(rec.get("pos"), list):
                pos_type_errors += 1
                row_errors.append("pos_not_list")

            if isinstance(rec.get("ipa"), str) and is_wrapped_ipa(rec["ipa"]):
                wrapped_ipa += 1
                row_errors.append("ipa_wrapped")

            if row_errors:
                invalid += 1
                if invalid <= sample_errors:
                    print(f"[line {line_num}] " + ", ".join(row_errors))

    print(f"File: {path}")
    print(f"Total rows: {total}")
    print(f"Invalid rows: {invalid}")
    for k in REQUIRED:
        if total:
            pct = (missing_required[k] / total) * 100.0
            print(f"Missing `{k}`: {missing_required[k]} ({pct:.2f}%)")
        else:
            print(f"Missing `{k}`: {missing_required[k]}")
    if total:
        print(f"pos type errors: {pos_type_errors} ({(pos_type_errors/total)*100.0:.2f}%)")
        print(f"wrapped ipa: {wrapped_ipa} ({(wrapped_ipa/total)*100.0:.2f}%)")
    return 0 if invalid == 0 else 2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--sample-errors", type=int, default=10)
    args = ap.parse_args()
    raise SystemExit(validate(args.path, sample_errors=args.sample_errors))


if __name__ == "__main__":
    main()

