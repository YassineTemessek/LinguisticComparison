"""
Full RCG Pipeline Orchestrator.
Runs the matching engine across all available English data parts against the Semitic source.
"""

import argparse
import json
import time
from pathlib import Path
from prototype_matcher import DiscoveryScorer, ConceptMapper, load_jsonl, is_arabic

# Configuration
BASE_DIR = Path(__file__).resolve().parents[2]
SEMITIC_FILE = BASE_DIR / "data/processed/wiktionary_stardict/filtered/Arabic-English_Wiktionary_dictionary_stardict_filtered.jsonl"
LEGACY_SEMITIC_FILES = [
    BASE_DIR / "data/processed/wiktionary_stardict/normalized/Arabic-English_Wiktionary_dictionary_stardict_normalized.jsonl",
    BASE_DIR / "data/processed/wiktionary_stardict/raw/Arabic-English_Wiktionary_dictionary_stardict.jsonl",
]
ENGLISH_PARTS_DIR = BASE_DIR / "data/processed/_parts/english_ipa_merged_pos"
LEGACY_ENGLISH_PARTS_DIR = BASE_DIR / "data/processed/_parts/english_ipa_merged"
CONCEPTS_FILE = BASE_DIR / "resources/concepts/concepts_v3_2_enriched.jsonl"
LEGACY_CONCEPTS_FILES = [
    BASE_DIR / "data/processed/concepts/concepts_v3_2_enriched.jsonl",
]
OUTPUT_FILE = BASE_DIR / "outputs/leads_full.jsonl"

# Weights (tuned from prototype)
WEIGHTS = {
    "skeleton": 3.0,
    "artic": 2.0,
    "ort": 1.0,
    "sem": 4.0
}

def run_pipeline(
    *,
    limit_per_part: int = 0,
    semitic_path: Path | None = None,
    english_path: Path | None = None,
    english_parts_dir: Path | None = None,
    concepts_path: Path | None = None,
    output_path: Path | None = None,
):
    print("=== Starting Full RCG Pipeline ===")
    start_time = time.time()
    
    # 1. Load Resources
    concepts_path_resolved = concepts_path or CONCEPTS_FILE
    if not concepts_path_resolved.exists():
        for candidate in LEGACY_CONCEPTS_FILES:
            if candidate.exists():
                concepts_path_resolved = candidate
                break
    print(f"Loading Concept Map from {concepts_path_resolved}...")
    mapper = ConceptMapper(concepts_path_resolved if concepts_path_resolved.exists() else None)
    
    semitic_path_resolved = semitic_path or SEMITIC_FILE
    if not semitic_path_resolved.exists():
        for candidate in LEGACY_SEMITIC_FILES:
            if candidate.exists():
                semitic_path_resolved = candidate
                break
    print(f"Loading Semitic Data from {semitic_path_resolved}...")
    semitic_data = load_jsonl(semitic_path_resolved, limit=0, filter_arabic=True)
    print(f"Loaded {len(semitic_data)} Semitic lexemes.")
    
    # 2. Setup Scorer
    scorer = DiscoveryScorer(weights=WEIGHTS, mapper=mapper)
    
    # 3. Iterate English inputs
    english_files: list[Path] = []
    if english_path is not None:
        english_files = [english_path]
    else:
        parts_dir = english_parts_dir or ENGLISH_PARTS_DIR
        english_files = sorted(list(parts_dir.glob("*.jsonl")))
        if not english_files and LEGACY_ENGLISH_PARTS_DIR.exists():
            english_files = sorted(list(LEGACY_ENGLISH_PARTS_DIR.glob("*.jsonl")))
        if not english_files:
            print(f"No English parts found in {parts_dir}")
            return

    total_leads = 0
    
    # Clear output file first
    out_path = output_path or OUTPUT_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        pass

    for i, eng_file in enumerate(english_files):
        part_start = time.time()
        label = f"Part {i+1}/{len(english_files)}" if len(english_files) > 1 else "English"
        print(f"\nProcessing {label}: {eng_file.name}...")
        
        ie_data = load_jsonl(eng_file, limit=limit_per_part, filter_arabic=False)
        print(f"  Loaded {len(ie_data)} English lexemes.")
        
        leads_buffer = []
        comparisons = 0
        
        for sem in semitic_data:
            for ie in ie_data:
                comparisons += 1
                lead = scorer.calculate_score(sem, ie)
                
                # Dynamic Thresholding
                # If we have a semantic hit (score_sem > 0), accept lower threshold
                threshold = 2.0
                if lead["components"]["sem"] > 0.5:
                    threshold = 1.5 
                
                if lead["score"] >= threshold:
                    leads_buffer.append(lead)

        # Append to master file
        with open(out_path, 'a', encoding='utf-8') as f:
            for lead in leads_buffer:
                f.write(json.dumps(lead, ensure_ascii=False) + "\n")
        
        total_leads += len(leads_buffer)
        part_duration = time.time() - part_start
        print(f"  Finished {comparisons} comparisons in {part_duration:.2f}s.")
        print(f"  Found {len(leads_buffer)} leads in this part.")

    total_duration = time.time() - start_time
    print(f"\n=== Pipeline Complete ===")
    print(f"Total Time: {total_duration:.2f}s")
    print(f"Total Leads: {total_leads}")
    print(f"Output: {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Limit rows per English part for testing")
    parser.add_argument("--semitic", type=Path, default=None, help="Optional Semitic JSONL override (default: canonical processed file).")
    parser.add_argument("--english", type=Path, default=None, help="Optional English JSONL override (use a single file instead of parts).")
    parser.add_argument("--english-parts-dir", type=Path, default=None, help="Optional folder override for English parts JSONL.")
    parser.add_argument("--concepts", type=Path, default=None, help="Optional concepts JSONL override.")
    parser.add_argument("--output", type=Path, default=None, help="Optional output JSONL path override.")
    args = parser.parse_args()
    
    run_pipeline(
        limit_per_part=args.limit,
        semitic_path=args.semitic,
        english_path=args.english,
        english_parts_dir=args.english_parts_dir,
        concepts_path=args.concepts,
        output_path=args.output,
    )
