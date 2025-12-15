"""
Stub for Arabic-centric ingest/normalize.

Scope for first tranche:
- Classical / Qur'anic Arabic (primary)
- Iraqi Arabic dialect
- Old Arabic epigraphy: Safaitic, Hismaic, Dadanitic/Taymanitic (as supporting)

Outputs should be lexeme schema compliant with Skeleton/ORT/Articulatory views.
"""

from pathlib import Path
from typing import List, Dict, Any

from .utils import normalize_record

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data" / "raw" / "ara"
OUT = BASE / "data" / "processed"


def ingest_sources() -> List[Dict[str, Any]]:
    """
    Placeholder: load attested forms from dictionaries/grammars and epigraphic corpora.
    Expected fields:
      - id, language (ara), stage (class/qur/iqa for Iraqi), script, date_window
      - orthography (raw), translit, ipa
      - gloss, concept_id, sense_id, register, mapping_type
      - lemma_anchor (lemma_form/pos/status/source)
      - provenance (source refs)
    """
    # TODO: implement actual ingestion for Classical/Qur'anic Arabic, Iraqi dialect,
    # and epigraphic corpora (Safaitic/Hismaic/Dadanitic).
    return []


def normalize(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Placeholder: derive skeleton, ORT trace, articulatory profile; enforce schema keys.
    """
    return [normalize_record(r) for r in records]


def save(records: List[Dict[str, Any]]) -> None:
    """
    Placeholder writer to processed jsonl/csv targets.
    """
    OUT.mkdir(parents=True, exist_ok=True)
    # TODO: write to OUT / f\"ara_lexemes.jsonl\"
    return


def run() -> None:
    recs = ingest_sources()
    recs = normalize(recs)
    save(recs)


if __name__ == "__main__":
    run()
