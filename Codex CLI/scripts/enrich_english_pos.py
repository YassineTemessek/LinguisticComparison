"""
Add coarse POS tags to English IPA lexicons using WordNet index files.

Inputs:
- data/raw/english/dict/index.noun / index.verb / index.adj / index.adv
- data/processed/_intermediate/english/english_ipa.jsonl (from ipa-dict)
- data/processed/_intermediate/english/english_cmudict_ipa.jsonl (from cmudict)

Outputs:
- data/processed/_intermediate/english/english_ipa_with_pos.jsonl
- data/processed/_intermediate/english/english_cmudict_ipa_with_pos.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Dict, Set

from processed_schema import ensure_min_schema


def load_wordnet_pos(dict_dir: pathlib.Path) -> Dict[str, Set[str]]:
    pos_map: Dict[str, Set[str]] = {}
    files = {
        "n": dict_dir / "index.noun",
        "v": dict_dir / "index.verb",
        "a": dict_dir / "index.adj",
        "r": dict_dir / "index.adv",
    }
    for tag, path in files.items():
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line or line.startswith(" "):
                    continue
                if line.startswith("  "):
                    continue
                if line.startswith("sense"):
                    continue
                if line[0].isdigit():
                    continue
                parts = line.strip().split()
                if not parts:
                    continue
                lemma = parts[0]
                pos_map.setdefault(lemma, set()).add(tag)
    return pos_map


def enrich_file(input_path: pathlib.Path, output_path: pathlib.Path, pos_map: Dict[str, Set[str]]) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with input_path.open("r", encoding="utf-8") as inp, output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            rec = json.loads(line)
            lemma = rec.get("lemma", "").lower()
            tags = sorted(pos_map.get(lemma, []))
            rec["pos"] = tags
            rec["lemma_status"] = rec.get("lemma_status", "auto_brut")
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dict_dir", type=pathlib.Path, default=pathlib.Path("data/raw/english/dict"))
    ap.add_argument("--ipa_in", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_ipa.jsonl"))
    ap.add_argument("--ipa_out", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_ipa_with_pos.jsonl"))
    ap.add_argument("--cmu_in", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_cmudict_ipa.jsonl"))
    ap.add_argument("--cmu_out", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_cmudict_ipa_with_pos.jsonl"))
    args = ap.parse_args()

    pos_map = load_wordnet_pos(args.dict_dir)
    ipa_total = enrich_file(args.ipa_in, args.ipa_out, pos_map)
    cmu_total = enrich_file(args.cmu_in, args.cmu_out, pos_map)
    print(f"ipa-dict enriched: {ipa_total}; cmudict enriched: {cmu_total}")


if __name__ == "__main__":
    main()
