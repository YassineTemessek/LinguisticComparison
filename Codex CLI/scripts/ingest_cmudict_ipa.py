"""
Convert CMUdict ARPAbet to IPA and emit a simple English lexicon.

Input: data/raw/english/cmudict/cmudict.dict
Output: data/processed/english/english_cmudict_ipa.jsonl

Fields: lemma, orthography, ipa, language=eng, stage=Modern, script=Latin, lemma_status=auto_brut, source=cmudict, pos="" (CMUdict has no POS).
"""

from __future__ import annotations

import argparse
import json
import pathlib

ARPABET_TO_IPA = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ",
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "EH": "ɛ", "ER": "ɝ", "EY": "eɪ",
    "F": "f", "G": "ɡ", "HH": "h", "IH": "ɪ", "IY": "i", "JH": "dʒ", "K": "k",
    "L": "l", "M": "m", "N": "n", "NG": "ŋ", "OW": "oʊ", "OY": "ɔɪ", "P": "p",
    "R": "ɹ", "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "UH": "ʊ", "UW": "u",
    "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ",
}


def arpabet_to_ipa(phones: list[str]) -> str:
    ipa_parts = []
    for ph in phones:
        base = ph.rstrip("012345")
        ipa = ARPABET_TO_IPA.get(base, base.lower())
        ipa_parts.append(ipa)
    return "".join(ipa_parts)


def parse_cmudict(path: pathlib.Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line or line.startswith(";"):
                continue
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            word = parts[0]
            phones = parts[1:]
            ipa = arpabet_to_ipa(phones)
            rec = {
                "lemma": word.lower(),
                "orthography": word,
                "ipa": ipa,
                "language": "eng",
                "stage": "Modern",
                "script": "Latin",
                "lemma_status": "auto_brut",
                "source": "cmudict",
                "pos": "",
            }
            records.append(rec)
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=pathlib.Path("data/raw/english/cmudict/cmudict.dict"))
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/english/english_cmudict_ipa.jsonl"))
    args = ap.parse_args()

    records = parse_cmudict(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out_f:
        for rec in records:
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
