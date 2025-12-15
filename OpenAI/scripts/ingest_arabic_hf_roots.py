"""
Ingest Arabic roots from HF parquet (Resources/arabic_roots_hf/train-00000-of-00001.parquet)
into a simple JSONL with translit/IPA.

Output: data/processed/arabic/hf_roots.jsonl
Fields: lemma (root), definition (raw), translit, ipa, language=ara, source=arabic_roots_hf
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from enrich_quran_translit import translit_and_ipa
from processed_schema import ensure_min_schema, normalize_ipa


def ingest(parquet_path: Path, out_path: Path) -> int:
    df = pd.read_parquet(parquet_path, engine="pyarrow")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_path.open("w", encoding="utf-8") as out_f:
        for _, row in df.iterrows():
            lemma = str(row.get("root", "")).strip()
            definition = str(row.get("definition", "")).strip()
            tr, ipa = translit_and_ipa(lemma)
            rec = {
                "lemma": lemma,
                "definition": definition,
                "translit": tr,
                "ipa_raw": ipa,
                "ipa": normalize_ipa(ipa),
                "language": "ara",
                "stage": "Classical",
                "script": "Arabic",
                "source": "arabic_roots_hf",
                "lemma_status": "auto_brut",
            }
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path(r"C:/AI Projects/Resources/arabic_roots_hf/train-00000-of-00001.parquet"))
    ap.add_argument("--output", type=Path, default=Path("data/processed/arabic/hf_roots.jsonl"))
    args = ap.parse_args()
    total = ingest(args.input, args.output)
    print(f"Wrote {total} records to {args.output}")


if __name__ == "__main__":
    main()
