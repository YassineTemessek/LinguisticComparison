"""
Filter normalized stardict JSONL by removing non-lexical entries and multiword/abbreviation-like lemmas.

Usage:
  python scripts/filter_stardict.py --input data/processed/wiktionary_stardict/Latin-English_Wiktionary_dictionary_stardict_normalized.jsonl --output data/processed/wiktionary_stardict/Latin-English_Wiktionary_dictionary_stardict_filtered.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re

BANNED_POS = {"phrase", "character", "symbol", "punct", "abbreviation", "name"}

def is_ok_lemma(lemma: str) -> bool:
    if not lemma:
        return False
    if " " in lemma:
        return False
    if "." in lemma:
        return False
    if re.match(r"^[^A-Za-z\u0370-\u03ff\u0400-\u04ff\u0590-\u05ff\u0600-\u06ff]+$", lemma):
        return False
    # drop all-uppercase short initialisms
    if len(lemma) <= 5 and lemma.isupper():
        return False
    return True


def filter_file(input_path: pathlib.Path, output_path: pathlib.Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with input_path.open("r", encoding="utf-8") as inp, output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            rec = json.loads(line)
            lemma = rec.get("lemma", "")
            pos = rec.get("pos", "")
            if isinstance(pos, list):
                pos_val = pos[0] if pos else ""
            else:
                pos_val = pos
            if pos_val.lower() in BANNED_POS:
                continue
            if not is_ok_lemma(lemma):
                continue
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    args = ap.parse_args()
    total = filter_file(args.input, args.output)
    print(f"Filtered {total} records to {args.output}")


if __name__ == "__main__":
    main()
