"""
Clean `word_root_map.jsonl` by removing high-noise rows (e.g., empty roots) and
adding a lightweight `type` classification so downstream matchers can ignore
function words/clitics by default.

Input:  data/processed/arabic/word_root_map.jsonl
Output: data/processed/arabic/word_root_map_filtered.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re

from processed_schema import ensure_min_schema


AR_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u0640]")


def strip_arabic_diacritics(text: str) -> str:
    return AR_DIACRITICS_RE.sub("", text or "")


CLITIC_FORMS = {
    "و",
    "ف",
    "ب",
    "ك",
    "ل",
    "س",
    "ال",
    "ٱل",
    "وال",
    "بال",
    "كال",
    "لل",
}


def classify(lemma: str, root: str) -> str:
    if root:
        return "content_word"
    norm = strip_arabic_diacritics(lemma)
    if norm in CLITIC_FORMS:
        return "clitic"
    return "function_word"


def clean(input_path: pathlib.Path, output_path: pathlib.Path, *, keep_empty_root: bool) -> int:
    total = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with input_path.open("r", encoding="utf-8") as inp, output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            if not line.strip():
                continue
            rec = json.loads(line)
            lemma = str(rec.get("lemma") or "")
            root = str(rec.get("root") or "").strip()
            rec["root"] = root
            rec["type"] = classify(lemma, root)
            if (not keep_empty_root) and (not root):
                continue
            rec = ensure_min_schema(rec, default_language="ara", default_stage="Classical", default_script="Arabic", default_source="word_root_map.csv", default_lemma_status="auto_brut")
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=pathlib.Path("data/processed/arabic/word_root_map.jsonl"))
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/arabic/word_root_map_filtered.jsonl"))
    ap.add_argument("--keep-empty-root", action="store_true", help="Keep rows with empty root (still classified).")
    args = ap.parse_args()

    total = clean(args.input, args.output, keep_empty_root=bool(args.keep_empty_root))
    print(f"Wrote {total} rows to {args.output}")


if __name__ == "__main__":
    main()

