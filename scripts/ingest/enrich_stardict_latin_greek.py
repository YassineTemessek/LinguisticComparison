"""
Enrich Latin/Greek Wiktionary stardict JSONL with IPA and POS extraction.

Inputs (JSONL):
- data/processed/wiktionary_stardict/Latin-English_Wiktionary_dictionary_stardict.jsonl
- data/processed/wiktionary_stardict/Ancient_Greek-English_Wiktionary_dictionary_stardict.jsonl

Outputs:
- data/processed/wiktionary_stardict/Latin-English_Wiktionary_dictionary_stardict_enriched.jsonl
- data/processed/wiktionary_stardict/Ancient_Greek-English_Wiktionary_dictionary_stardict_enriched.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Callable

from processed_schema import ensure_min_schema, normalize_ipa

POS_TAG_RE = re.compile(r"<i>([^<]+)</i>", re.IGNORECASE)


LATIN_MAP = {
    "a": "a", "b": "b", "c": "k", "d": "d", "e": "e", "f": "f", "g": "ɡ",
    "h": "h", "i": "i", "j": "j", "k": "k", "l": "l", "m": "m", "n": "n",
    "o": "o", "p": "p", "q": "k", "r": "r", "s": "s", "t": "t", "u": "u",
    "v": "w", "x": "ks", "y": "y", "z": "z", "æ": "ae", "œ": "oe",
    "ph": "pʰ", "th": "tʰ", "ch": "kʰ", "qu": "kw",
}

GREEK_MAP = {
    "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "zd",
    "η": "ɛː", "θ": "tʰ", "ι": "i", "κ": "k", "λ": "l", "μ": "m",
    "ν": "n", "ξ": "ks", "ο": "o", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
    "τ": "t", "υ": "y", "φ": "pʰ", "χ": "kʰ", "ψ": "ps", "ω": "ɔː",
    "αι": "ai", "ει": "ei", "οι": "oi", "υι": "yi", "αυ": "au", "ευ": "eu", "ου": "ou",
    "ἁ": "ha", "ἀ": "a", "ἑ": "he", "ἐ": "e", "ἱ": "hi", "ἰ": "i", "ὁ": "ho", "ὀ": "o", "ὑ": "hy", "ὐ": "y", "ὡ": "ho", "ὠ": "ɔː",
}


def to_ipa(text: str, mapping: dict[str, str]) -> str:
    out = []
    i = 0
    while i < len(text):
        # handle digraphs first
        if i + 1 < len(text):
            digraph = text[i : i + 2].lower()
            if digraph in mapping:
                out.append(mapping[digraph])
                i += 2
                continue
        ch = text[i]
        out.append(mapping.get(ch.lower(), ch))
        i += 1
    return "".join(out)


def extract_pos(gloss: str) -> str:
    m = POS_TAG_RE.search(gloss or "")
    if not m:
        return ""
    return m.group(1).strip().lower()


def enrich_file(input_path: pathlib.Path, output_path: pathlib.Path, mapper: Callable[[str], str], lang_code: str) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with input_path.open("r", encoding="utf-8") as inp, output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            rec = json.loads(line)
            lemma = rec.get("lemma", "")
            gloss = rec.get("gloss", "")
            ipa = mapper(lemma)
            rec["ipa_raw"] = ipa
            rec["ipa"] = normalize_ipa(ipa)
            raw_pos = extract_pos(gloss)
            rec["pos"] = [raw_pos] if raw_pos else []
            rec["language"] = lang_code
            rec["lemma_status"] = rec.get("lemma_status", "auto_brut")
            rec["source"] = rec.get("source", "wiktionary-stardict")
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--latin_in", type=pathlib.Path, default=pathlib.Path("data/processed/wiktionary_stardict/raw/Latin-English_Wiktionary_dictionary_stardict.jsonl"))
    ap.add_argument("--latin_out", type=pathlib.Path, default=pathlib.Path("data/processed/wiktionary_stardict/enriched/Latin-English_Wiktionary_dictionary_stardict_enriched.jsonl"))
    ap.add_argument("--greek_in", type=pathlib.Path, default=pathlib.Path("data/processed/wiktionary_stardict/raw/Ancient_Greek-English_Wiktionary_dictionary_stardict.jsonl"))
    ap.add_argument("--greek_out", type=pathlib.Path, default=pathlib.Path("data/processed/wiktionary_stardict/enriched/Ancient_Greek-English_Wiktionary_dictionary_stardict_enriched.jsonl"))
    args = ap.parse_args()

    lat_total = enrich_file(args.latin_in, args.latin_out, lambda s: to_ipa(s, LATIN_MAP), "lat")
    gr_total = enrich_file(args.greek_in, args.greek_out, lambda s: to_ipa(s, GREEK_MAP), "grc")
    print(f"Latin enriched: {lat_total}, Greek enriched: {gr_total}")


if __name__ == "__main__":
    main()
