"""
Stub for English ingest/normalize (Old, Middle, Modern).
"""

from pathlib import Path
from typing import List, Dict, Any

from .utils import normalize_record

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data" / "raw" / "eng"
OUT = BASE / "data" / "processed"


def ingest_sources() -> List[Dict[str, Any]]:
    """
    Placeholder: load attested English forms across stages with ORT fossils.
    """
    # TODO: implement ingestion for Old, Middle, Modern English entries per concept.
    return []


def normalize(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [normalize_record(r) for r in records]


def save(records: List[Dict[str, Any]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # TODO: write to OUT / f\"eng_lexemes.jsonl\"
    return


def run() -> None:
    recs = ingest_sources()
    recs = normalize(recs)
    save(recs)


if __name__ == "__main__":
    run()
