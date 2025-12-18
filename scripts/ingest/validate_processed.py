"""
Validate processed JSONL outputs against the project's shared minimal schema.

Default behavior is CI-friendly:
  - missing files are skipped
  - validation fails only on malformed/invalid rows in files that exist

Usage:
  python scripts/ingest/validate_processed.py --all
  python scripts/ingest/validate_processed.py data/processed/arabic/quran_lemmas_enriched.jsonl
  python scripts/ingest/validate_processed.py --require-files --all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


REQUIRED = ("id", "lemma", "language", "stage", "script", "source", "lemma_status")

DEFAULT_CANONICAL: tuple[Path, ...] = (
    Path("data/processed/arabic/quran_lemmas_enriched.jsonl"),
    Path("data/processed/arabic/hf_roots.jsonl"),
    Path("data/processed/arabic/word_root_map_filtered.jsonl"),
    Path("data/processed/english/english_ipa_merged_pos.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Latin-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Ancient_Greek-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Arabic-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
)


def is_wrapped_ipa(value: str) -> bool:
    value = (value or "").strip()
    return len(value) >= 2 and ((value[0] == "/" and value[-1] == "/") or (value[0] == "[" and value[-1] == "]"))


def validate_jsonl(path: Path, *, sample_errors: int = 10) -> dict[str, Any]:
    total = 0
    invalid = 0
    missing_required = {k: 0 for k in REQUIRED}
    pos_type_errors = 0
    wrapped_ipa = 0

    with path.open("r", encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                invalid += 1
                if invalid <= sample_errors:
                    print(f"{path} [line {line_num}] invalid JSON")
                continue

            row_errors: list[str] = []
            for k in REQUIRED:
                if not rec.get(k):
                    missing_required[k] += 1
                    row_errors.append(f"missing:{k}")

            if "pos" in rec and not isinstance(rec.get("pos"), list):
                pos_type_errors += 1
                row_errors.append("pos_not_list")

            if isinstance(rec.get("ipa"), str) and is_wrapped_ipa(rec["ipa"]):
                wrapped_ipa += 1
                row_errors.append("ipa_wrapped")

            if row_errors:
                invalid += 1
                if invalid <= sample_errors:
                    print(f"{path} [line {line_num}] " + ", ".join(row_errors))

    return {
        "path": str(path),
        "total_rows": total,
        "invalid_rows": invalid,
        "missing_required": missing_required,
        "pos_type_errors": pos_type_errors,
        "wrapped_ipa": wrapped_ipa,
    }


def iter_paths(args_paths: Iterable[Path], *, all_paths: bool, repo_root: Path) -> list[Path]:
    out: list[Path] = []
    if all_paths:
        out.extend(repo_root / p for p in DEFAULT_CANONICAL)
    out.extend(p if p.is_absolute() else (repo_root / p) for p in args_paths)
    # de-dupe while preserving order
    seen: set[str] = set()
    deduped: list[Path] = []
    for p in out:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="JSONL file paths to validate.")
    ap.add_argument("--all", action="store_true", help="Validate the canonical processed outputs list.")
    ap.add_argument("--require-files", action="store_true", help="Fail if any requested file is missing.")
    ap.add_argument("--warn-only", action="store_true", help="Always exit 0 (still prints FAIL lines).")
    ap.add_argument("--sample-errors", type=int, default=10, help="Max per-file row errors printed.")
    args = ap.parse_args()

    targets = iter_paths(args.paths, all_paths=bool(args.all), repo_root=repo_root)
    if not targets:
        print("No files selected. Pass paths or use --all.")
        raise SystemExit(2)

    any_failed = False
    for path in targets:
        if not path.exists():
            msg = f"Missing: {path}"
            if args.require_files:
                print(msg)
                any_failed = True
            else:
                print(f"Skip missing: {path}")
            continue

        if path.suffix.lower() != ".jsonl":
            print(f"Skip non-JSONL: {path}")
            continue

        summary = validate_jsonl(path, sample_errors=int(args.sample_errors))
        invalid = int(summary["invalid_rows"])
        total = int(summary["total_rows"])
        print(f"OK: {path} (rows={total}, invalid={invalid})" if invalid == 0 else f"FAIL: {path} (rows={total}, invalid={invalid})")
        if invalid != 0:
            any_failed = True

    raise SystemExit(0 if args.warn_only else (2 if any_failed else 0))


if __name__ == "__main__":
    main()
