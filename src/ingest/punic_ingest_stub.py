"""
Stub for Punic/Phoenician ingest/normalize (secondary, high priority).

Targets: Phoenician/Punic/Neo-Punic inscriptions with transliterations,
date windows, and lemma anchors.
"""

from pathlib import Path
from typing import List, Dict, Any

from .utils import normalize_record

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data" / "raw" / "phn"
OUT = BASE / "data" / "processed"


def ingest_sources() -> List[Dict[str, Any]]:
    """
    Placeholder: parse epigraphic datasets and transliteration tables.
    Expected fields similar to arabic stub.
    """
    # TODO: implement real ingestion for Punic/Phoenician.
    return []


def normalize(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Placeholder: schema enforcement + skeleton/ORT/articulatory derivation.
    """
    return [normalize_record(r) for r in records]


def save(records: List[Dict[str, Any]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # TODO: write to OUT / f"phn_lexemes.jsonl"
    return


def run() -> None:
    recs = ingest_sources()
    recs = normalize(recs)
    save(recs)


if __name__ == "__main__":
    run()
