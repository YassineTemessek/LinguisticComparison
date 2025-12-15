"""
Enrich Quran lemma list with Buckwalter -> IPA conversion when possible.

Input: data/processed/_intermediate/arabic/quran_lemmas.jsonl
Output: data/processed/_intermediate/arabic/quran_lemmas_with_ipa.jsonl

Assumes lemmas are in Arabic script; we also accept Buckwalter in features (ROOT/LEM) and try to convert.
If no mapping is possible, ipa field is left empty.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Dict

from buckwalter_to_ipa import bw_to_ipa
from processed_schema import ensure_min_schema, normalize_ipa


def guess_bw(form: str) -> str | None:
    # Heuristic: return None; for proper conversion, supply a transliterator.
    return None


def enrich(input_path: pathlib.Path, output_path: pathlib.Path) -> int:
    count = 0
    with input_path.open("r", encoding="utf-8") as inp, output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            rec = json.loads(line)
            ipa = ""
            # Try Buckwalter in features first.
            feats: Dict[str, str] = rec.get("features", {})
            bw_form = feats.get("LEM")
            if bw_form:
                ipa = bw_to_ipa(bw_form)
            elif rec.get("lemma"):
                bw_guess = guess_bw(rec["lemma"])
                if bw_guess:
                    ipa = bw_to_ipa(bw_guess)
            rec["ipa_raw"] = ipa
            rec["ipa"] = normalize_ipa(ipa)
            rec["lemma_status"] = rec.get("lemma_status", "silver")
            rec["source_ipa"] = "buckwalter_to_ipa" if ipa else ""
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/arabic/quran_lemmas.jsonl"))
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/arabic/quran_lemmas_with_ipa.jsonl"))
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    total = enrich(args.input, args.output)
    print(f"Wrote {total} records to {args.output}")


if __name__ == "__main__":
    main()
