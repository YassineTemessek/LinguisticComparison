"""
Normalize stardict JSONL outputs:
 - drop non-lexical/symbol-only lemmas
 - standardize POS labels (light mapping)

Usage:
  python scripts/normalize_stardict.py --input data/processed/wiktionary_stardict/Latin-English_Wiktionary_dictionary_stardict_enriched.jsonl --output data/processed/wiktionary_stardict/Latin-English_Wiktionary_dictionary_stardict_normalized.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Dict

from processed_schema import coerce_pos_list, ensure_min_schema

POS_MAP: Dict[str, str] = {
    "noun": "N",
    "n": "N",
    "proper noun": "name",
    "name": "name",
    "verb": "V",
    "v": "V",
    "adjective": "ADJ",
    "adj": "ADJ",
    "adverb": "ADV",
    "adv": "ADV",
    "pronoun": "PRON",
    "determiner": "DET",
    "conjunction": "CONJ",
    "particle": "PART",
    "interjection": "INTJ",
    "preposition": "PREP",
    "number": "NUM",
    "abbreviation": "abbreviation",
    "initialism": "abbreviation",
}

SYMBOL_RE = re.compile(r"^[^A-Za-z\u0370-\u03ff\u0400-\u04ff\u0590-\u05ff\u0600-\u06ff]+$")  # drops pure symbols/punct
POS_TAG_RE = re.compile(r"<i>([^<]+)</i>", re.IGNORECASE)


def normalize_pos(raw_pos: str) -> str:
    if not raw_pos:
        return ""
    key = raw_pos.lower()
    return POS_MAP.get(key, raw_pos.lower())

def extract_pos_from_gloss(gloss_html: str) -> str:
    m = POS_TAG_RE.search(gloss_html or "")
    if not m:
        return ""
    return m.group(1).strip().lower()


def normalize_file(input_path: pathlib.Path, output_path: pathlib.Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with input_path.open("r", encoding="utf-8") as inp, output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            rec = json.loads(line)
            lemma = str(rec.get("lemma", "")).strip()
            if not lemma or SYMBOL_RE.match(lemma):
                continue
            pos_list = coerce_pos_list(rec.get("pos"))
            raw_pos = pos_list[0] if pos_list else extract_pos_from_gloss(str(rec.get("gloss_html") or ""))
            norm = normalize_pos(raw_pos)
            rec["pos"] = [norm] if norm else []
            rec["lemma_status"] = rec.get("lemma_status", "auto_brut")
            rec["source"] = rec.get("source", "wiktionary-stardict")
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    args = ap.parse_args()
    total = normalize_file(args.input, args.output)
    print(f"Normalized {total} records to {args.output}")


if __name__ == "__main__":
    main()
