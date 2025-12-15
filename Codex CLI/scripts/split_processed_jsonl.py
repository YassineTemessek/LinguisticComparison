"""
Split a large processed JSONL file into smaller parts under `data/processed/_parts/`.

Example:
  python split_processed_jsonl.py data/processed/english/english_ipa_merged_pos.jsonl --lines 50000

Output:
  data/processed/_parts/english_ipa_merged_pos/english_ipa_merged_pos_part_001.jsonl
  ...
"""

from __future__ import annotations

import argparse
from pathlib import Path


def split_jsonl(input_path: Path, out_dir: Path, lines_per_chunk: int) -> int:
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))

    out_dir.mkdir(parents=True, exist_ok=True)

    part_num = 1
    current_lines: list[str] = []
    total_lines = 0

    with input_path.open("r", encoding="utf-8") as infile:
        for line in infile:
            current_lines.append(line)
            total_lines += 1

            if len(current_lines) >= lines_per_chunk:
                write_chunk(out_dir, input_path.stem, part_num, current_lines)
                part_num += 1
                current_lines = []

        if current_lines:
            write_chunk(out_dir, input_path.stem, part_num, current_lines)

    return total_lines


def write_chunk(out_dir: Path, stem: str, part_num: int, lines: list[str]) -> None:
    filename = f"{stem}_part_{part_num:03d}.jsonl"
    out_path = out_dir / filename
    with out_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"[ok] {out_path} ({len(lines)} lines)")


def default_out_dir(processed_root: Path, input_path: Path) -> Path:
    # data/processed/_parts/<stem>/
    return processed_root / "_parts" / input_path.stem


def main() -> None:
    ap = argparse.ArgumentParser(description="Split processed JSONL into standardized parts folder.")
    ap.add_argument("input_file", type=Path, help="Path to input .jsonl file")
    ap.add_argument("--lines", type=int, default=50000, help="Lines per chunk")
    ap.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    ap.add_argument("--out-dir", type=Path, default=None, help="Override output directory")
    args = ap.parse_args()

    out_dir = args.out_dir or default_out_dir(args.processed_root, args.input_file)
    total = split_jsonl(args.input_file, out_dir, args.lines)
    print(f"Done. Split {total} lines into {out_dir}")


if __name__ == "__main__":
    main()

