"""
Split Large JSONL Files.
Usage: python split_large_jsonl.py <input_file> [--lines 50000]

Splits a large .jsonl file into smaller parts named <filename>_part_XXX.jsonl
Saves them in a subfolder named <filename>_parts/
"""

import argparse
from pathlib import Path
import math

def split_jsonl(input_path: Path, lines_per_chunk: int):
    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        return

    # Create output directory
    output_dir = input_path.parent / f"{input_path.stem}_parts"
    output_dir.mkdir(exist_ok=True)
    
    print(f"Splitting {input_path.name} into chunks of {lines_per_chunk} lines...")
    print(f"Output directory: {output_dir}")

    part_num = 1
    current_lines = []
    total_lines = 0

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                current_lines.append(line)
                total_lines += 1
                
                if len(current_lines) >= lines_per_chunk:
                    write_chunk(output_dir, input_path.stem, part_num, current_lines)
                    part_num += 1
                    current_lines = []
            
            # Write remaining lines
            if current_lines:
                write_chunk(output_dir, input_path.stem, part_num, current_lines)

        print(f"Done! Split {total_lines} lines into {part_num} files.")

    except Exception as e:
        print(f"Error processing file: {e}")

def write_chunk(output_dir, stem, part_num, lines):
    filename = f"{stem}_part_{part_num:03d}.jsonl"
    out_path = output_dir / filename
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"  Wrote {out_path.name} ({len(lines)} lines)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split large JSONL files")
    parser.add_argument("input_file", help="Path to input .jsonl file")
    parser.add_argument("--lines", type=int, default=50000, help="Lines per chunk")
    
    args = parser.parse_args()
    split_jsonl(Path(args.input_file), args.lines)
