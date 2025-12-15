# coding: utf-8
from __future__ import annotations

"""
Parse the Quranic Arabic Corpus morphology file into a lemma list (JSONL).

Default input: data/raw/arabic/quran-morphology/quran-morphology.txt
Default output: data/processed/arabic/quran_lemmas.jsonl
"""

import argparse
import json
import pathlib
from typing import Dict, Tuple

from processed_schema import ensure_min_schema


def parse_features(feat_str: str) -> Dict[str, str]:
    parts = feat_str.split("|")
    out: Dict[str, str] = {}
    for part in parts:
        if ":" in part:
            k, v = part.split(":", 1)
            out[k] = v
        else:
            out[part] = True
    return out


def read_morph(path: pathlib.Path) -> Dict[Tuple[str, str], Dict[str, str]]:
    records: Dict[Tuple[str, str], Dict[str, str]] = {}
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or "\t" not in line:
                continue
            try:
                _ref, surface, pos_tag, feats = line.split("\t", 3)
            except ValueError:
                continue
            feat_map = parse_features(feats)
            lemma = feat_map.get("LEM", surface)
            root = feat_map.get("ROOT", "")
            key = (lemma, root)
            if key not in records:
                records[key] = {
                    "lemma": lemma,
                    "root": root,
                    "pos_tag": pos_tag,
                    "pos": [pos_tag] if pos_tag else [],
                    "example_surface": surface,
                    "language": "ara-qur",
                    "stage": "Classical",
                    "script": "Arabic",
                    "lemma_status": "silver",
                    "source": "quranic-corpus-morphology",
                    "features": feat_map,
                }
    return records


def write_jsonl(records: Dict[Tuple[str, str], Dict[str, str]], out_path: pathlib.Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as out_f:
        for rec in records.values():
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return len(records)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=pathlib.Path("data/raw/arabic/quran-morphology/quran-morphology.txt"))
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/arabic/quran_lemmas.jsonl"))
    args = ap.parse_args()

    records = read_morph(args.input)
    total = write_jsonl(records, args.output)
    print(f"Wrote {total} lemma records to {args.output}")


if __name__ == "__main__":
    main()
