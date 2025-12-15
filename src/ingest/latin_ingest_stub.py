"""
Stub for Latin ingest/normalize (anchor/contrast).
Scope: Classical Latin citation forms aligned to concept inventory.
"""

from pathlib import Path
from typing import List, Dict, Any

from .utils import normalize_record

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data" / "raw" / "lat"
OUT = BASE / "data" / "processed"


def ingest_sources() -> List[Dict[str, Any]]:
    """
    Placeholder: pull lemmas from Latin dictionaries aligned to concept IDs.
    Expected fields mirror lexeme schema.
    """
    # TODO: implement real ingestion (dictionary scrape/CSV).
    return []


def normalize(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [normalize_record(r) for r in records]


def save(records: List[Dict[str, Any]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # TODO: write to OUT / f\"lat_lexemes.jsonl\"
    return


def run() -> None:
    recs = ingest_sources()
    recs = normalize(recs)
    save(recs)


if __name__ == "__main__":
    run()
