"""
Create small, committed samples of large processed JSONL files for collaboration.

Why:
  - Full `data/processed/` outputs are intentionally not committed.
  - Samples under `resources/` let contributors run quick experiments and validate
    schemas without downloading large datasets.

Default output folder: resources/samples/processed
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_CANONICAL: tuple[Path, ...] = (
    Path("data/processed/arabic/quran_lemmas_enriched.jsonl"),
    Path("data/processed/arabic/hf_roots.jsonl"),
    Path("data/processed/arabic/word_root_map_filtered.jsonl"),
    Path("data/processed/english/english_ipa_merged_pos.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Latin-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Ancient_Greek-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Arabic-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
)


@dataclass(frozen=True)
class SampleSpec:
    input_path: Path
    output_path: Path
    max_rows: int


def iter_targets(repo_root: Path, *, all_canonical: bool, paths: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    if all_canonical:
        out.extend(repo_root / p for p in DEFAULT_CANONICAL)
    out.extend(p if p.is_absolute() else (repo_root / p) for p in paths)
    seen: set[str] = set()
    deduped: list[Path] = []
    for p in out:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped


def sample_jsonl(spec: SampleSpec) -> dict[str, Any]:
    spec.output_path.parent.mkdir(parents=True, exist_ok=True)
    rows_in = 0
    rows_out = 0
    invalid_json = 0
    with spec.input_path.open("r", encoding="utf-8", errors="replace") as inp, spec.output_path.open("w", encoding="utf-8") as out_f:
        for line in inp:
            line = line.strip()
            if not line:
                continue
            rows_in += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                invalid_json += 1
                continue
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            rows_out += 1
            if rows_out >= spec.max_rows:
                break
    return {
        "input": str(spec.input_path),
        "output": str(spec.output_path),
        "rows_scanned": rows_in,
        "rows_written": rows_out,
        "invalid_json_rows_skipped": invalid_json,
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="Optional JSONL paths to sample (in addition to --all).")
    ap.add_argument("--all", action="store_true", help="Sample the canonical processed outputs list.")
    ap.add_argument("--rows", type=int, default=1000, help="Max valid JSON rows written per file.")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("resources/samples/processed"),
        help="Output folder for sampled JSONL files.",
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=Path("resources/samples/processed/manifest.json"),
        help="Manifest JSON written alongside samples.",
    )
    args = ap.parse_args()

    targets = iter_targets(repo_root, all_canonical=bool(args.all), paths=args.paths)
    if not targets:
        raise SystemExit("No files selected. Pass paths or use --all.")

    out_dir = args.out_dir if args.out_dir.is_absolute() else (repo_root / args.out_dir)
    manifest_path = args.manifest if args.manifest.is_absolute() else (repo_root / args.manifest)
    max_rows = max(1, int(args.rows))

    items: list[dict[str, Any]] = []
    for path in targets:
        if not path.exists():
            items.append({"input": str(path), "missing": True})
            continue
        if path.suffix.lower() != ".jsonl":
            items.append({"input": str(path), "skipped": "not_jsonl"})
            continue

        out_name = path.name.replace(".jsonl", "_sample.jsonl")
        out_path = out_dir / out_name
        items.append(sample_jsonl(SampleSpec(input_path=path, output_path=out_path, max_rows=max_rows)))

    payload = {
        "type": "processed_samples_manifest",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "rows_per_file": max_rows,
        "items": items,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote samples to {out_dir}")
    print(f"Wrote manifest to {manifest_path}")


if __name__ == "__main__":
    main()

