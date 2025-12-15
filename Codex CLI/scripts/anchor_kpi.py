"""
Simple KPI helper for Latin anchor coverage/confidence.

Reads: data/processed/anchors/latin_anchor_table_v0_full.csv
Outputs coverage (non-empty lat_lemma) and confidence (gold+silver share).
"""

import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ANCHOR_PATH = BASE / "data" / "processed" / "anchors" / "latin_anchor_table_v0_full.csv"


def main() -> None:
    if not ANCHOR_PATH.exists():
        raise SystemExit(f"Missing anchor file: {ANCHOR_PATH}")
    with ANCHOR_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    coverage = sum(1 for r in rows if r["lat_lemma"].strip()) / total if total else 0.0
    confidence = sum(1 for r in rows if r["lemma_status"] in {"gold", "silver"}) / total if total else 0.0

    print(f"Anchors file: {ANCHOR_PATH}")
    print(f"Total concepts: {total}")
    print(f"Coverage (non-empty lat_lemma): {coverage:.1%}")
    print(f"Confidence (gold+silver share): {confidence:.1%}")


if __name__ == "__main__":
    main()
