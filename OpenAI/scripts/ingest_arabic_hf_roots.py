"""
Ingest Arabic roots from HF parquet (default: data/raw/arabic/arabic_roots_hf/train-00000-of-00001.parquet)
into a simple JSONL with translit/IPA.

Output: data/processed/arabic/hf_roots.jsonl
Fields: lemma (root), definition (raw), translit, ipa, language=ara, source=arabic_roots_hf

If you keep datasets outside the repo, set `LC_RESOURCES_DIR` to point at that folder
and the default input will become: %LC_RESOURCES_DIR%/arabic_roots_hf/train-00000-of-00001.parquet
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from enrich_quran_translit import translit_and_ipa
from processed_schema import ensure_min_schema, normalize_ipa


def default_input_path() -> Path:
    resources_dir = os.environ.get("LC_RESOURCES_DIR")
    if resources_dir:
        return Path(resources_dir) / "arabic_roots_hf" / "train-00000-of-00001.parquet"
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "data" / "raw" / "arabic" / "arabic_roots_hf" / "train-00000-of-00001.parquet"


def ingest(parquet_path: Path, out_path: Path) -> int:
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency 'pandas'. Install dependencies (and 'pyarrow' for parquet) or run via the project's recommended environment."
        ) from exc

    df = pd.read_parquet(parquet_path, engine="pyarrow")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_path.open("w", encoding="utf-8") as out_f:
        for row_num, (_, row) in enumerate(df.iterrows(), start=1):
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
                "source_ref": f"arabic_roots_hf:row:{row_num}",
                "lemma_status": "auto_brut",
            }
            rec = ensure_min_schema(rec)
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument(
        "--input",
        type=Path,
        default=default_input_path(),
        help="Input parquet path (or set LC_RESOURCES_DIR to use an external datasets folder).",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/arabic/hf_roots.jsonl"),
        help="Output JSONL path.",
    )
    args = ap.parse_args()
    total = ingest(args.input, args.output)
    print(f"Wrote {total} records to {args.output}")


if __name__ == "__main__":
    main()
