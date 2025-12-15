"""
Validate sample lexeme file for required fields and normalized views.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SAMPLE = BASE / "data" / "samples" / "lexeme_sample.jsonl"

REQUIRED_KEYS = [
    "id",
    "language",
    "stage",
    "script",
    "date_window",
    "orthography",
    "translit",
    "gloss",
    "concept_id",
    "sense_id",
    "register",
    "mapping_type",
    "lemma_anchor",
    "provenance",
]


def main() -> None:
    missing_any = False
    count = 0
    for line in SAMPLE.read_text(encoding="utf-8").splitlines():
        count += 1
        obj = json.loads(line)
        missing = [k for k in REQUIRED_KEYS if k not in obj]
        if missing:
            missing_any = True
            print(f"Row {count} missing keys: {missing}")
    if not missing_any:
        print(f"Validated {count} rows; all required keys present.")


if __name__ == "__main__":
    main()
