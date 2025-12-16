"""
Build a simple Modern English IPA lexicon from ipa-dict (en_US + en_UK).

Output: JSONL at data/processed/_intermediate/english/english_ipa.jsonl
Fields: lemma, orthography, ipa, language, stage, script, lemma_status, source, variant.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Dict, List

from processed_schema import ensure_min_schema, normalize_ipa

IPA_FILES = [
    ("en_US", pathlib.Path("data/raw/english/ipa-dict/data/en_US.txt")),
    ("en_UK", pathlib.Path("data/raw/english/ipa-dict/data/en_UK.txt")),
]


def load_ipa_file(path: pathlib.Path) -> Dict[str, List[str]]:
    entries: Dict[str, List[str]] = {}
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "\t" not in line:
                continue
            word, ipa = line.split("\t", 1)
            entries.setdefault(word, []).append(ipa)
    return entries


def merge_sources() -> List[dict]:
    combined: Dict[str, Dict[str, List[str]]] = {}
    for variant, path in IPA_FILES:
        if not path.exists():
            continue
        data = load_ipa_file(path)
        for word, ipas in data.items():
            combined.setdefault(word, {}).setdefault("ipa_by_variant", {}).setdefault(variant, []).extend(ipas)
    records: List[dict] = []
    for word, info in combined.items():
        ipa_by_variant = info["ipa_by_variant"]
        for variant, ipa_list in ipa_by_variant.items():
            for idx, ipa in enumerate(ipa_list, start=1):
                rec = {
                    "lemma": word,
                    "orthography": word,
                    "ipa_raw": ipa,
                    "ipa": normalize_ipa(ipa),
                    "language": "eng",
                    "stage": "Modern",
                    "script": "Latin",
                    "lemma_status": "auto_brut",
                    "source": f"ipa-dict:{variant}",
                    "source_ref": f"ipa-dict:{variant}:{word}:{idx}",
                    "variant": variant,
                }
                rec = ensure_min_schema(rec)
                records.append(rec)
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_ipa.jsonl"))
    args = ap.parse_args()

    records = merge_sources()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out_f:
        for rec in records:
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
