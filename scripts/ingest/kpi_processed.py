"""
Generate simple KPI/coverage reports for canonical `data/processed/` outputs.

Outputs:
  - JSON summary (default): outputs/kpi_processed.json
  - Per-file CSV (default): outputs/kpi_processed_files.csv
  - IPA/POS coverage CSV (default): outputs/kpi_processed_ipa_by_source.csv

Notes:
  - Designed to stream JSONL (no pandas dependency).
  - Duplicate detection can be memory-heavy; it is optional and can be bounded.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REQUIRED_FIELDS = ("id", "lemma", "language", "stage", "script", "source", "lemma_status")

DEFAULT_CANONICAL: tuple[Path, ...] = (
    Path("data/processed/arabic/quran_lemmas_enriched.jsonl"),
    Path("data/processed/arabic/hf_roots.jsonl"),
    Path("data/processed/arabic/word_root_map_filtered.jsonl"),
    Path("data/processed/english/english_ipa_merged_pos.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Latin-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Ancient_Greek-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    Path("data/processed/wiktionary_stardict/filtered/Arabic-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
)

DEFAULT_ANCHORS = Path("resources/anchors/latin_anchor_table_v0_full.csv")


def _is_wrapped_ipa(value: str) -> bool:
    value = (value or "").strip()
    return len(value) >= 2 and ((value[0] == "/" and value[-1] == "/") or (value[0] == "[" and value[-1] == "]"))


def _has_text(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    return True


def _pos_present(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, list):
        return any(_has_text(item) for item in v)
    if isinstance(v, str):
        return bool(v.strip())
    return True


def _norm_lemma(lemma: str) -> str:
    return (lemma or "").strip().casefold()


def _hash_key(text: str) -> int:
    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big", signed=False)


@dataclass(frozen=True)
class DuplicateConfig:
    enabled: bool
    max_rows: int


@dataclass
class JsonlSummary:
    path: str
    exists: bool
    bytes: int | None = None
    total_rows: int = 0
    invalid_json_rows: int = 0
    missing_required: dict[str, int] | None = None
    wrapped_ipa_rows: int = 0
    ipa_present_rows: int = 0
    pos_present_rows: int = 0
    duplicates: dict[str, Any] | None = None


def summarize_jsonl(
    path: Path,
    *,
    duplicate_cfg: DuplicateConfig,
    sample_errors: int = 0,
) -> tuple[JsonlSummary, dict[tuple[str, str], dict[str, int]]]:
    if not path.exists():
        return JsonlSummary(path=str(path), exists=False), {}

    summary = JsonlSummary(
        path=str(path),
        exists=True,
        bytes=path.stat().st_size,
        missing_required={k: 0 for k in REQUIRED_FIELDS},
        duplicates=None,
    )

    by_lang_source: dict[tuple[str, str], dict[str, int]] = {}

    seen_id: set[int] | None = set() if duplicate_cfg.enabled else None
    seen_lemma_key: set[int] | None = set() if duplicate_cfg.enabled else None
    dup_id = 0
    dup_lemma_key = 0
    dup_rows_scanned = 0
    dup_truncated = False

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            summary.total_rows += 1

            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                summary.invalid_json_rows += 1
                if sample_errors and summary.invalid_json_rows <= sample_errors:
                    print(f"{path} [line {line_num}] invalid JSON")
                continue

            lang = str(rec.get("language") or "").strip()
            source = str(rec.get("source") or "").strip()
            bucket = by_lang_source.setdefault((lang, source), {"rows": 0, "ipa_present": 0, "pos_present": 0})
            bucket["rows"] += 1

            for k in REQUIRED_FIELDS:
                if not _has_text(rec.get(k)):
                    assert summary.missing_required is not None
                    summary.missing_required[k] += 1

            ipa = rec.get("ipa")
            if isinstance(ipa, str) and _has_text(ipa):
                summary.ipa_present_rows += 1
                bucket["ipa_present"] += 1
                if _is_wrapped_ipa(ipa):
                    summary.wrapped_ipa_rows += 1

            if _pos_present(rec.get("pos")):
                summary.pos_present_rows += 1
                bucket["pos_present"] += 1

            if duplicate_cfg.enabled:
                if duplicate_cfg.max_rows and dup_rows_scanned >= duplicate_cfg.max_rows:
                    dup_truncated = True
                    continue
                dup_rows_scanned += 1

                id_hash = _hash_key(str(rec.get("id") or ""))
                if id_hash and seen_id is not None:
                    if id_hash in seen_id:
                        dup_id += 1
                    else:
                        seen_id.add(id_hash)

                lemma_key = "\t".join(
                    [
                        str(rec.get("language") or ""),
                        str(rec.get("stage") or ""),
                        _norm_lemma(str(rec.get("lemma") or "")),
                    ]
                )
                lemma_key_hash = _hash_key(lemma_key)
                if lemma_key_hash and seen_lemma_key is not None:
                    if lemma_key_hash in seen_lemma_key:
                        dup_lemma_key += 1
                    else:
                        seen_lemma_key.add(lemma_key_hash)

    if duplicate_cfg.enabled:
        summary.duplicates = {
            "enabled": True,
            "rows_scanned": dup_rows_scanned,
            "truncated": dup_truncated,
            "duplicate_ids": dup_id,
            "duplicate_language_stage_lemma": dup_lemma_key,
        }

    return summary, by_lang_source


def load_anchors(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def build_lemma_set(path: Path) -> set[str]:
    lemmas: set[str] = set()
    if not path.exists():
        return lemmas
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            lemma = rec.get("lemma")
            if isinstance(lemma, str) and lemma.strip():
                lemmas.add(_norm_lemma(lemma))
    return lemmas


def pct(n: int, d: int) -> float:
    return 0.0 if d <= 0 else round(n * 100.0 / d, 2)


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


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="Optional JSONL paths to summarize (in addition to --all).")
    ap.add_argument("--all", action="store_true", help="Summarize the canonical processed outputs list.")
    ap.add_argument("--out-json", type=Path, default=Path("outputs/kpi_processed.json"), help="Output JSON path.")
    ap.add_argument("--out-files-csv", type=Path, default=Path("outputs/kpi_processed_files.csv"), help="Output per-file CSV path.")
    ap.add_argument(
        "--out-ipa-csv",
        type=Path,
        default=Path("outputs/kpi_processed_ipa_by_source.csv"),
        help="Output per-(language,source) IPA/POS coverage CSV path.",
    )
    ap.add_argument("--compute-duplicates", action="store_true", help="Compute duplicate counts (can be memory-heavy).")
    ap.add_argument(
        "--duplicates-max-rows",
        type=int,
        default=500_000,
        help="Max rows per file for duplicate detection (0 = unlimited).",
    )
    ap.add_argument("--anchors", type=Path, default=DEFAULT_ANCHORS, help="Anchor CSV used for concept coverage.")
    ap.add_argument(
        "--latin-lexicon",
        type=Path,
        default=Path("data/processed/wiktionary_stardict/filtered/Latin-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
        help="Latin lexeme JSONL to check anchors against.",
    )
    args = ap.parse_args()

    targets = iter_targets(repo_root, all_canonical=bool(args.all), paths=args.paths)
    if not targets:
        raise SystemExit("No files selected. Pass paths or use --all.")

    duplicate_cfg = DuplicateConfig(enabled=bool(args.compute_duplicates), max_rows=max(0, int(args.duplicates_max_rows)))

    per_file: list[dict[str, Any]] = []
    by_lang_source_total: dict[tuple[str, str], dict[str, int]] = {}

    for path in targets:
        if path.suffix.lower() != ".jsonl":
            continue
        summary, by_lang_source = summarize_jsonl(path, duplicate_cfg=duplicate_cfg)
        per_file.append(
            {
                "path": summary.path,
                "exists": summary.exists,
                "bytes": summary.bytes,
                "rows": summary.total_rows,
                "invalid_json_rows": summary.invalid_json_rows,
                "missing_required": summary.missing_required,
                "missing_required_pct": {
                    k: pct(int(summary.missing_required[k]), int(summary.total_rows)) if summary.missing_required else 0.0
                    for k in REQUIRED_FIELDS
                },
                "ipa_present_pct": pct(summary.ipa_present_rows, summary.total_rows),
                "pos_present_pct": pct(summary.pos_present_rows, summary.total_rows),
                "wrapped_ipa_rows": summary.wrapped_ipa_rows,
                "duplicates": summary.duplicates,
            }
        )

        for key, bucket in by_lang_source.items():
            agg = by_lang_source_total.setdefault(key, {"rows": 0, "ipa_present": 0, "pos_present": 0})
            agg["rows"] += int(bucket.get("rows", 0))
            agg["ipa_present"] += int(bucket.get("ipa_present", 0))
            agg["pos_present"] += int(bucket.get("pos_present", 0))

    # Anchor coverage (Latin)
    anchors_path = args.anchors if args.anchors.is_absolute() else (repo_root / args.anchors)
    latin_lexicon_path = args.latin_lexicon if args.latin_lexicon.is_absolute() else (repo_root / args.latin_lexicon)
    anchor_coverage: dict[str, Any] = {"enabled": False}
    if anchors_path.exists():
        anchors = load_anchors(anchors_path)
        latin_lemmas = build_lemma_set(latin_lexicon_path)
        with_lemma = 0
        found = 0
        found_by_status: dict[str, dict[str, int]] = {}
        for row in anchors:
            lemma = (row.get("lat_lemma") or "").strip()
            if not lemma:
                continue
            with_lemma += 1
            status = (row.get("lemma_status") or "").strip() or "unknown"
            b = found_by_status.setdefault(status, {"with_lemma": 0, "found": 0})
            b["with_lemma"] += 1
            if _norm_lemma(lemma) in latin_lemmas:
                found += 1
                b["found"] += 1

        anchor_coverage = {
            "enabled": True,
            "anchors_path": str(anchors_path),
            "latin_lexicon_path": str(latin_lexicon_path),
            "concept_rows": len(anchors),
            "concepts_with_lat_lemma": with_lemma,
            "concepts_with_lat_lemma_found_in_lexicon": found,
            "coverage_pct": pct(found, with_lemma),
            "by_lemma_status": {
                status: {
                    **counts,
                    "coverage_pct": pct(int(counts["found"]), int(counts["with_lemma"])),
                }
                for status, counts in sorted(found_by_status.items(), key=lambda kv: kv[0])
            },
        }

    payload = {
        "type": "kpi_processed",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "files": per_file,
        "ipa_by_language_source": [
            {
                "language": lang,
                "source": source,
                "rows": stats["rows"],
                "ipa_present_pct": pct(stats["ipa_present"], stats["rows"]),
                "pos_present_pct": pct(stats["pos_present"], stats["rows"]),
            }
            for (lang, source), stats in sorted(by_lang_source_total.items(), key=lambda kv: (kv[0][0], kv[0][1]))
        ],
        "anchor_coverage": anchor_coverage,
    }

    out_json = args.out_json if args.out_json.is_absolute() else (repo_root / args.out_json)
    out_files_csv = args.out_files_csv if args.out_files_csv.is_absolute() else (repo_root / args.out_files_csv)
    out_ipa_csv = args.out_ipa_csv if args.out_ipa_csv.is_absolute() else (repo_root / args.out_ipa_csv)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    out_files_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_files_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "path",
                "exists",
                "bytes",
                "rows",
                "invalid_json_rows",
                *[f"missing_{k}_pct" for k in REQUIRED_FIELDS],
                "ipa_present_pct",
                "pos_present_pct",
                "wrapped_ipa_rows",
                "duplicates_rows_scanned",
                "duplicates_truncated",
                "duplicate_ids",
                "duplicate_language_stage_lemma",
            ],
        )
        writer.writeheader()
        for item in per_file:
            row: dict[str, Any] = {
                "path": item["path"],
                "exists": item["exists"],
                "bytes": item["bytes"],
                "rows": item["rows"],
                "invalid_json_rows": item["invalid_json_rows"],
                "ipa_present_pct": item["ipa_present_pct"],
                "pos_present_pct": item["pos_present_pct"],
                "wrapped_ipa_rows": item["wrapped_ipa_rows"],
            }
            mrp = item.get("missing_required_pct") or {}
            for k in REQUIRED_FIELDS:
                row[f"missing_{k}_pct"] = mrp.get(k, 0.0)
            d = item.get("duplicates") or {}
            row["duplicates_rows_scanned"] = d.get("rows_scanned")
            row["duplicates_truncated"] = d.get("truncated")
            row["duplicate_ids"] = d.get("duplicate_ids")
            row["duplicate_language_stage_lemma"] = d.get("duplicate_language_stage_lemma")
            writer.writerow(row)

    out_ipa_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_ipa_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["language", "source", "rows", "ipa_present_pct", "pos_present_pct"])
        writer.writeheader()
        for item in payload["ipa_by_language_source"]:
            writer.writerow(item)

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_files_csv}")
    print(f"Wrote: {out_ipa_csv}")


if __name__ == "__main__":
    main()

