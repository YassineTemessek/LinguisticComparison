"""
Ingest word_root_map.csv into a JSONL with simple transliteration/IPA.

Input (default): data/raw/arabic/word_root_map.csv
Output: data/processed/_intermediate/arabic/word_root_map.jsonl

If you keep datasets outside the repo, set `LC_RESOURCES_DIR` to point at that folder
and the default input will become: %LC_RESOURCES_DIR%/word_root_map.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
from typing import Tuple, List, Dict

# Reuse a simple transliteration/IPA map (same as enrich_quran_translit.py)
from enrich_quran_translit import translit_and_ipa
from processed_schema import ensure_min_schema, normalize_ipa


def default_input_path() -> pathlib.Path:
    resources_dir = os.environ.get("LC_RESOURCES_DIR")
    if resources_dir:
        return pathlib.Path(resources_dir) / "word_root_map.csv"
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    return repo_root / "data" / "raw" / "arabic" / "word_root_map.csv"


def ingest(input_path: pathlib.Path, output_path: pathlib.Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with input_path.open("r", encoding="utf-8") as fh, output_path.open("w", encoding="utf-8") as out_f:
        reader = csv.DictReader(fh)
        for row in reader:
            word = row.get("word") or row.get("word_form") or ""
            root = row.get("root") or ""
            tr, ipa = translit_and_ipa(word)
            rec: Dict[str, str] = {
                "lemma": word,
                "root": root,
                "translit": tr,
                "ipa_raw": ipa,
                "ipa": normalize_ipa(ipa),
                "language": "ara",
                "stage": "Classical",
                "script": "Arabic",
                "source": "word_root_map.csv",
                "lemma_status": "auto_brut",
                "pos": [],
            }
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument(
        "--input",
        type=pathlib.Path,
        default=default_input_path(),
        help="Input CSV path (or set LC_RESOURCES_DIR to use an external datasets folder).",
    )
    ap.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("data/processed/_intermediate/arabic/word_root_map.jsonl"),
        help="Output JSONL path.",
    )
    args = ap.parse_args()
    total = ingest(args.input, args.output)
    print(f"Wrote {total} records to {args.output}")


if __name__ == "__main__":
    main()
