"""
Generate basic transliteration and IPA for Quran lemmas (Arabic script).
This is a lightweight, rule-based mapper for quick comparison runs; it is not
phonologically complete. Extend mapping for higher fidelity.

Input: data/processed/arabic/quran_lemmas.jsonl
Output: data/processed/arabic/quran_lemmas_enriched.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Dict, Tuple, List

# Consonant mapping (Arabic letter -> (translit, ipa))
CONS_MAP: Dict[str, Tuple[str, str]] = {
    "ء": ("'", "ʔ"),
    "ا": ("a", "aː"),
    "أ": ("a", "ʔaː"),
    "إ": ("i", "ʔiː"),
    "آ": ("a", "ʔaː"),
    "ب": ("b", "b"),
    "ت": ("t", "t"),
    "ث": ("th", "θ"),
    "ج": ("j", "d͡ʒ"),
    "ح": ("ḥ", "ħ"),
    "خ": ("kh", "x"),
    "د": ("d", "d"),
    "ذ": ("dh", "ð"),
    "ر": ("r", "r"),
    "ز": ("z", "z"),
    "س": ("s", "s"),
    "ش": ("sh", "ʃ"),
    "ص": ("ṣ", "sˤ"),
    "ض": ("ḍ", "dˤ"),
    "ط": ("ṭ", "tˤ"),
    "ظ": ("ẓ", "ðˤ"),
    "ع": ("ʿ", "ʕ"),
    "غ": ("gh", "ɣ"),
    "ف": ("f", "f"),
    "ق": ("q", "q"),
    "ك": ("k", "k"),
    "ل": ("l", "l"),
    "م": ("m", "m"),
    "ن": ("n", "n"),
    "ه": ("h", "h"),
    "و": ("w", "w"),
    "ي": ("y", "j"),
    "ة": ("h", "h"),
    "ى": ("ā", "aː"),
}

# Short vowels and tanwin
DIAC_MAP = {
    "َ": ("a", "a"),
    "ُ": ("u", "u"),
    "ِ": ("i", "i"),
    "ً": ("an", "an"),
    "ٌ": ("un", "un"),
    "ٍ": ("in", "in"),
}

SHADDA = "ّ"
SUKUN = "ْ"


def translit_and_ipa(text: str) -> Tuple[str, str]:
    tr_out: List[str] = []
    ipa_out: List[str] = []
    for ch in text:
        if ch == SHADDA:
            if tr_out:
                tr_out[-1] = tr_out[-1] * 2
            if ipa_out:
                ipa_out[-1] = ipa_out[-1] * 2
            continue
        if ch == SUKUN:
            continue
        if ch in DIAC_MAP:
            tr_v, ipa_v = DIAC_MAP[ch]
            tr_out.append(tr_v)
            ipa_out.append(ipa_v)
            continue
        if ch in CONS_MAP:
            tr_c, ipa_c = CONS_MAP[ch]
            tr_out.append(tr_c)
            ipa_out.append(ipa_c)
            continue
        # fallback: keep character
        tr_out.append(ch)
        ipa_out.append(ch)
    return "".join(tr_out), "".join(ipa_out)


def enrich(input_path: pathlib.Path, output_path: pathlib.Path) -> int:
    total = 0
    with input_path.open("r", encoding="utf-8") as inp, output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            rec = json.loads(line)
            lemma = rec.get("lemma", "")
            tr, ipa = translit_and_ipa(lemma)
            rec["translit"] = tr
            rec["ipa"] = ipa
            rec["source_ipa"] = "rule_based_ar"
            rec["lemma_status"] = rec.get("lemma_status", "silver")
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=pathlib.Path("data/processed/arabic/quran_lemmas.jsonl"))
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/arabic/quran_lemmas_enriched.jsonl"))
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    total = enrich(args.input, args.output)
    print(f"Wrote {total} records to {args.output}")


if __name__ == "__main__":
    main()
