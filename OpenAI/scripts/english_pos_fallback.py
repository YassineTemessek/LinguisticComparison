"""
Add simple heuristic POS to English IPA merged file when WordNet POS is missing.

Input: data/processed/_intermediate/english/english_ipa_merged.jsonl
Output: data/processed/english/english_ipa_merged_pos.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib

from processed_schema import ensure_min_schema


def heuristic_pos(word: str) -> str:
    w = word.lower()
    if "-" in w or " " in w:
        return ""
    if w.endswith(("ing", "ed")):
        return "V"
    if w.endswith(("ly",)):
        return "ADV"
    if w.endswith(("ous", "ive", "able", "ible", "al", "ic", "ish", "less", "ful")):
        return "ADJ"
    if w.endswith(("ness", "ment", "tion", "sion", "hood", "ship", "ity", "ism")):
        return "N"
    return ""


def enrich(input_path: pathlib.Path, output_path: pathlib.Path) -> int:
    total = 0
    with input_path.open("r", encoding="utf-8") as inp, output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            rec = json.loads(line)
            pos = rec.get("pos", [])
            if isinstance(pos, list):
                pos_list = pos
            elif pos:
                pos_list = [pos]
            else:
                pos_list = []
            if not pos_list:
                guess = heuristic_pos(rec.get("lemma", ""))
                if guess:
                    pos_list = [guess]
            rec["pos"] = pos_list
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_ipa_merged.jsonl"))
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/english/english_ipa_merged_pos.jsonl"))
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    total = enrich(args.input, args.output)
    print(f"Wrote {total} records to {args.output}")


if __name__ == "__main__":
    main()
