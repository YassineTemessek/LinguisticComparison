"""
Validation Script for Master Foundation V3.2 Lexeme Schema.
Usage: python validate_ingest.py <path_to_jsonl_file>

Checks for:
1. Presence of all required fields from Section 6.2.
2. Validity of 'lemma_status' (gold, silver, auto_brut).
3. Structure of nested objects (ort, lemma_anchor).
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

# --- Schema Definition (Master Foundation v3.2) ---

REQUIRED_FIELDS = [
    "id", "language", "stage", "script", "date_window",
    "orthography", "ipa", "skeleton", "vowel_matrix", "syllable_template",
    "ort", "gloss", "concept_id", "sense_id", "register",
    "mapping_type", "lemma_anchor", "provenance", "notes"
]

REQUIRED_NESTED = {
    "ort": ["trace", "flags"],
    "lemma_anchor": ["is_anchor", "lemma_form", "lemma_pos", "lemma_status", "lemma_source"],
    "provenance": ["source", "ref"] # minimally source or ref
}

VALID_LEMMA_STATUS = ["gold", "silver", "auto_brut"]

# --- Validation Logic ---

def validate_row(row: Dict[str, Any], line_num: int) -> List[str]:
    errors = []
    
    # 1. Check Top-Level Fields
    for field in REQUIRED_FIELDS:
        if field not in row:
            errors.append(f"Missing required field: '{field}'")
    
    # 2. Check Nested Fields
    if "ort" in row and isinstance(row["ort"], dict):
        for subfield in REQUIRED_NESTED["ort"]:
            if subfield not in row["ort"]:
                errors.append(f"Missing nested field: 'ort.{subfield}'")
    
    if "lemma_anchor" in row and isinstance(row["lemma_anchor"], dict):
        for subfield in REQUIRED_NESTED["lemma_anchor"]:
            if subfield not in row["lemma_anchor"]:
                errors.append(f"Missing nested field: 'lemma_anchor.{subfield}'")
        
        # 3. Check Enum Values
        status = row["lemma_anchor"].get("lemma_status")
        if status and status not in VALID_LEMMA_STATUS:
            errors.append(f"Invalid lemma_status: '{status}' (Must be {VALID_LEMMA_STATUS})")

    return errors

def process_file(file_path: Path):
    print(f"Validating: {file_path}")
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return

    total_rows = 0
    valid_rows = 0
    invalid_rows = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line: continue
                
                total_rows += 1
                try:
                    data = json.loads(line)
                    errors = validate_row(data, line_num)
                    
                    if errors:
                        invalid_rows += 1
                        # Print first 5 errors only to avoid spam
                        if invalid_rows <= 5:
                            print(f"[Row {line_num}] Errors: {', '.join(errors)}")
                    else:
                        valid_rows += 1
                        
                except json.JSONDecodeError:
                    print(f"[Row {line_num}] Invalid JSON format.")
                    invalid_rows += 1

        print("-" * 40)
        print(f"Validation Complete.")
        print(f"Total Rows: {total_rows}")
        print(f"Valid Rows: {valid_rows}")
        print(f"Invalid Rows: {invalid_rows}")
        print("-" * 40)

    except Exception as e:
        print(f"Fatal Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Validate Lexeme JSONL against V3.2 Schema")
    parser.add_argument("file_path", help="Path to the JSONL file to validate")
    args = parser.parse_args()
    
    process_file(Path(args.file_path))

if __name__ == "__main__":
    main()
