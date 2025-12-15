"""
Analyze Prototype Leads.
Reads the output of prototype_matcher.py and generates a summary.
"""

import json
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE / "output" / "prototype_leads.jsonl"
OUTPUT_REPORT = BASE / "output" / "leads_analysis.txt"

def main():
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return

    leads = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                leads.append(json.loads(line))

    # Sort by score descending
    leads.sort(key=lambda x: x['score'], reverse=True)

    # Analysis
    total = len(leads)
    top_20 = leads[:20]
    
    # Score Distribution
    scores = [l['score'] for l in leads]
    avg_score = sum(scores) / total if total else 0
    
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write("=== PROTOTYPE LEADS ANALYSIS ===\n")
        f.write(f"Total Leads (Score >= 2.0): {total}\n")
        f.write(f"Average Score: {avg_score:.2f}\n")
        f.write(f"Max Score: {scores[0] if scores else 0}\n\n")
        
        f.write("--- TOP 20 CANDIDATES ---\\n")
        f.write(f"{ 'SCORE':<8} | { 'SEM_ID':<20} | { 'IE_ID':<20} | { 'SKEL':<6} | { 'ORT':<6} | { 'ARTIC'}\n")
        f.write("-" * 80 + "\n")
        
        for lead in top_20:
            comps = lead['components']
            f.write(f"{lead['score']:<8} | {str(lead['sem_id'])[:18]:<20} | {str(lead['ie_id'])[:18]:<20} | {comps['skel']:<6} | {comps['ort']:<6} | {comps['artic']}\n")
            
    print(f"Analysis written to {OUTPUT_REPORT}")
    
    # Print to console as well
    print(Path(OUTPUT_REPORT).read_text(encoding='utf-8'))

if __name__ == "__main__":
    main()
