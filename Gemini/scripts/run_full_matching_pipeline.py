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
OUTPUT_FILE = BASE_DIR / "Gemini/output/leads_full.jsonl"

# Weights (tuned from prototype)
WEIGHTS = {
    "skeleton": 3.0,
    "artic": 2.0,
    "ort": 1.0,
    "sem": 4.0
}

def run_pipeline(limit_per_part: int = 0):
    print("=== Starting Full RCG Pipeline ===")
    start_time = time.time()
    
    # 1. Load Resources
    concepts_path = CONCEPTS_FILE
    if not concepts_path.exists():
        for candidate in LEGACY_CONCEPTS_FILES:
            if candidate.exists():
                concepts_path = candidate
                break
    print(f"Loading Concept Map from {concepts_path}...")
    mapper = ConceptMapper(concepts_path if concepts_path.exists() else None)
    
    semitic_path = SEMITIC_FILE
    if not semitic_path.exists():
        for candidate in LEGACY_SEMITIC_FILES:
            if candidate.exists():
                semitic_path = candidate
                break
    print(f"Loading Semitic Data from {semitic_path}...")
    semitic_data = load_jsonl(semitic_path, limit=0, filter_arabic=True)
    print(f"Loaded {len(semitic_data)} Semitic lexemes.")
    
    # 2. Setup Scorer
    scorer = DiscoveryScorer(weights=WEIGHTS, mapper=mapper)
    
    # 3. Iterate English Parts
    english_files = sorted(list(ENGLISH_PARTS_DIR.glob("*.jsonl")))
    if not english_files and LEGACY_ENGLISH_PARTS_DIR.exists():
        english_files = sorted(list(LEGACY_ENGLISH_PARTS_DIR.glob("*.jsonl")))
    if not english_files:
        print(f"No English parts found in {ENGLISH_PARTS_DIR}")
        return

    total_leads = 0
    
    # Clear output file first
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        pass

    for i, eng_file in enumerate(english_files):
        part_start = time.time()
        print(f"\nProcessing Part {i+1}/{len(english_files)}: {eng_file.name}...")
        
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
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
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
    print(f"Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Limit rows per English part for testing")
    args = parser.parse_args()
    
    run_pipeline(args.limit)
