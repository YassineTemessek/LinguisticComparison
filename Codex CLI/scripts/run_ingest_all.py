"""
Orchestrator to run Codex-side ingestion scripts (not src stubs).
This is a thin runner; add/remove scripts as they stabilize.
"""

import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

COMMANDS = [
    ["python", str(BASE / "scripts" / "convert_stardict.py"), "--root", str(BASE / "data" / "raw" / "wiktionary_extracted"), "--out", str(BASE / "data" / "processed" / "wiktionary_stardict")],
    ["python", str(BASE / "scripts" / "ingest_quran_morphology.py"), "--input", str(BASE / "data" / "raw" / "arabic" / "quran-morphology" / "quran-morphology.txt"), "--output", str(BASE / "data" / "processed" / "arabic" / "quran_lemmas.jsonl")],
    ["python", str(BASE / "scripts" / "enrich_quran_translit.py"), "--input", str(BASE / "data" / "processed" / "arabic" / "quran_lemmas.jsonl"), "--output", str(BASE / "data" / "processed" / "arabic" / "quran_lemmas_enriched.jsonl")],
    ["python", str(BASE / "scripts" / "ingest_english_ipa.py")],
    ["python", str(BASE / "scripts" / "ingest_cmudict_ipa.py")],
    ["python", str(BASE / "scripts" / "enrich_english_pos.py")],
    ["python", str(BASE / "scripts" / "merge_english_ipa_sources.py")],
    ["python", str(BASE / "scripts" / "english_pos_fallback.py")],
    # add more as they become stable
]


def main() -> None:
    for cmd in COMMANDS:
        print("Running:", " ".join(str(c) for c in cmd))
        subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
