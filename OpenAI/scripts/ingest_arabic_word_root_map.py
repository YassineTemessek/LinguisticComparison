"""
Ingest word_root_map.csv into a JSONL with simple transliteration/IPA.

Input: C:/AI Projects/Resources/word_root_map.csv
Output: data/processed/_intermediate/arabic/word_root_map.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
from typing import Tuple, List, Dict

# Reuse a simple transliteration/IPA map (same as enrich_quran_translit.py)
from enrich_quran_translit import translit_and_ipa
from processed_schema import ensure_min_schema, normalize_ipa


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=pathlib.Path(r"C:/AI Projects/Resources/word_root_map.csv"))
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/arabic/word_root_map.jsonl"))
    args = ap.parse_args()
    total = ingest(args.input, args.output)
    print(f"Wrote {total} records to {args.output}")


if __name__ == "__main__":
    main()
