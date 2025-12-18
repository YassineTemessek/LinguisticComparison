"""
Quick validation checklist for processed lexeme files.
Checks:
  - Row count
  - % entries with IPA (or translit)
  - % entries with POS (if present)
  - Sample few rows

Usage examples:
  python validate_ingest.py --input data/processed/arabic/hf_roots.jsonl --sample 5
  python validate_ingest.py --input data/processed/english/english_ipa_merged_pos.jsonl --pos-field pos
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, List
import random


def validate(path: Path, ipa_field: str = "ipa", pos_field: Optional[str] = None, sample: int = 5, sample_out: Optional[Path] = None) -> None:
    total = 0
    ipa_count = 0
    pos_count = 0
    rows: List[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            rows.append(rec)
            total += 1
            if rec.get(ipa_field) or rec.get("translit"):
                ipa_count += 1
            if pos_field:
                pos_val = rec.get(pos_field, [])
                if pos_val:
                    if isinstance(pos_val, list) and len(pos_val) > 0:
                        pos_count += 1
                    elif isinstance(pos_val, str) and pos_val.strip():
                        pos_count += 1
    print(f"File: {path}")
    print(f"Total rows: {total}")
    if total > 0:
        print(f"IPA/translit coverage: {ipa_count/total:.2%}")
        if pos_field:
            print(f"POS coverage: {pos_count/total:.2%}")
    samples = random.sample(rows, min(sample, len(rows))) if sample and rows else []
    if sample_out and samples:
        sample_out.parent.mkdir(parents=True, exist_ok=True)
        with sample_out.open("w", encoding="utf-8") as f:
            for rec in samples:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"Wrote samples to {sample_out}")
    elif samples:
        print("Samples:")
        for rec in samples:
            try:
                print(json.dumps(rec, ensure_ascii=False))
            except Exception:
                print("<sample has non-printable characters; use --sample-out to write to file>")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--ipa-field", type=str, default="ipa")
    ap.add_argument("--pos-field", type=str, default=None)
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--sample-out", type=Path, default=None, help="Optional path to write samples as UTF-8 JSONL")
    args = ap.parse_args()
    validate(args.input, ipa_field=args.ipa_field, pos_field=args.pos_field, sample=args.sample, sample_out=args.sample_out)


if __name__ == "__main__":
    main()
