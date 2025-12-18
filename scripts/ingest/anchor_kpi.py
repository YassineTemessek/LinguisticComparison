"""
Simple KPI helper for Latin anchor coverage/confidence.

Reads: resources/anchors/latin_anchor_table_v0_full.csv
Outputs coverage (non-empty lat_lemma) and confidence (gold+silver share).
"""

import argparse
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANCHOR_PATH = REPO_ROOT / "resources" / "anchors" / "latin_anchor_table_v0_full.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--anchors",
        type=Path,
        default=DEFAULT_ANCHOR_PATH,
        help="Path to the anchors CSV (default: resources/anchors/latin_anchor_table_v0_full.csv)",
    )
    args = parser.parse_args()

    anchor_path: Path = args.anchors
    if not anchor_path.exists():
        raise SystemExit(f"Missing anchor file: {anchor_path}")

    with anchor_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    coverage = sum(1 for r in rows if r["lat_lemma"].strip()) / total if total else 0.0
    confidence = sum(1 for r in rows if r["lemma_status"] in {"gold", "silver"}) / total if total else 0.0

    print(f"Anchors file: {anchor_path}")
    print(f"Total concepts: {total}")
    print(f"Coverage (non-empty lat_lemma): {coverage:.1%}")
    print(f"Confidence (gold+silver share): {confidence:.1%}")


if __name__ == "__main__":
    main()
