"""
Lightweight normalization helpers for ingest stubs.
These are intentionally simple placeholders; replace with full phonology/ORT logic later.
"""

import re
from typing import Dict, Any, List

VOWELS = set("aeiouAEIOU")


def derive_skeleton(translit: str) -> List[str]:
    """Return consonant sequence from a transliterated string (ASCII-only approximation)."""
    if not translit:
        return []
    return [ch for ch in translit if ch.isalpha() and ch not in VOWELS]


def derive_ort_trace(orth: str) -> List[str]:
    """Return raw orthographic trace as a list of characters."""
    return list(orth) if orth else []


def minimal_lexeme_defaults(row: Dict[str, Any]) -> Dict[str, Any]:
    """Fill missing optional fields with neutral defaults."""
    row.setdefault("register", "standard")
    row.setdefault("mapping_type", "literal")
    row.setdefault("notes", "")
    return row


def normalize_record(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply quick normalization: skeleton, ort.trace, ensure required keys exist.
    Assumes transliteration in row.get('translit') and orthography in row.get('orthography').
    """
    row = minimal_lexeme_defaults(dict(row))
    row["skeleton"] = derive_skeleton(row.get("translit", ""))
    row["ort"] = {
        "trace": derive_ort_trace(row.get("orthography", "")),
        "flags": [],
    }
    # Articulatory placeholder: downstream modules can enrich this.
    row.setdefault("articulatory", {})
    return row
