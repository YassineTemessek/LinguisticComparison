"""
Orchestrator to run Codex-side ingestion scripts (not src stubs).
This is a thin runner; add/remove scripts as they stabilize.
"""

import subprocess
from pathlib import Path

CODEX_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CODEX_DIR.parent
SCRIPTS_DIR = CODEX_DIR / "scripts"

COMMANDS = [
    ["python", str(SCRIPTS_DIR / "convert_stardict.py"), "--root", str(REPO_ROOT / "data" / "raw" / "wiktionary_extracted"), "--out", str(REPO_ROOT / "data" / "processed" / "wiktionary_stardict")],
    ["python", str(SCRIPTS_DIR / "ingest_quran_morphology.py"), "--input", str(REPO_ROOT / "data" / "raw" / "arabic" / "quran-morphology" / "quran-morphology.txt"), "--output", str(REPO_ROOT / "data" / "processed" / "arabic" / "quran_lemmas.jsonl")],
    ["python", str(SCRIPTS_DIR / "enrich_quran_translit.py"), "--input", str(REPO_ROOT / "data" / "processed" / "arabic" / "quran_lemmas.jsonl"), "--output", str(REPO_ROOT / "data" / "processed" / "arabic" / "quran_lemmas_enriched.jsonl")],
    ["python", str(SCRIPTS_DIR / "ingest_english_ipa.py")],
    ["python", str(SCRIPTS_DIR / "ingest_cmudict_ipa.py")],
    ["python", str(SCRIPTS_DIR / "enrich_english_pos.py")],
    ["python", str(SCRIPTS_DIR / "merge_english_ipa_sources.py")],
    ["python", str(SCRIPTS_DIR / "english_pos_fallback.py")],
    # add more as they become stable
]


def main() -> None:
    for cmd in COMMANDS:
        print("Running:", " ".join(str(c) for c in cmd))
        subprocess.run(cmd, check=False, cwd=str(REPO_ROOT))


if __name__ == "__main__":
    main()
