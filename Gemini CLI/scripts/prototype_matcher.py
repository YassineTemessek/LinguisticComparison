"""
Prototype Matcher for Gemini CLI.
Implements the 'DiscoveryScore' algorithm from Master Foundation v3.2 (Section 9).
Refactored for modularity and future expansion.
"""

import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

# --- Configuration ---
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_FILE = OUTPUT_DIR / "prototype_leads.jsonl"

# Default Weights (Master Foundation v3.2)
DEFAULT_WEIGHTS = {
    "skeleton": 3.0,
    "artic": 3.0,
    "ort": 2.0,
    "sem": 2.0
}

def clean_html(raw_html: str) -> str:
    """Remove HTML tags and entities from gloss."""
    if not raw_html:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', raw_html)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    # Basic range for Arabic block
    return any('\u0600' <= c <= '\u06FF' for c in text)

class ConceptMapper:
    """Maps words to Concept IDs using a synonym registry."""
    def __init__(self, concepts_path: Optional[Path]):
        self.synonym_map: Dict[str, str] = {}
        self.concept_data: Dict[str, Dict] = {}
        if concepts_path:
            self.load(concepts_path)

    def load(self, path: Path):
        print(f"Loading concepts from {path}...")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        c = json.loads(line)
                        cid = c.get("concept_id")
                        if not cid: continue
                        
                        self.concept_data[cid] = c
                        
                        # Map core gloss
                        if c.get("core_gloss_en"):
                            self.synonym_map[c["core_gloss_en"].lower()] = cid
                            
                        # Map synonyms
                        for syn in c.get("synonyms_en", []):
                            self.synonym_map[syn.lower()] = cid
                    except json.JSONDecodeError:
                        pass
            print(f"Loaded {len(self.concept_data)} concepts with {len(self.synonym_map)} synonym triggers.")
        except Exception as e:
            print(f"Error loading concepts: {e}")

    def get_concept_id(self, text_tokens: List[str]) -> Optional[str]:
        """Try to find a concept ID from a list of tokens (lemmas or gloss keywords)."""
        # Prioritize exact match of longer phrases if we had them, 
        # but here we do simple token lookup.
        # Check specific tokens first
        for token in text_tokens:
            token_clean = token.lower().strip()
            if token_clean in self.synonym_map:
                return self.synonym_map[token_clean]
        return None

class DiscoveryScorer:
    def __init__(self, weights: Dict[str, float] = DEFAULT_WEIGHTS, mapper: Optional[ConceptMapper] = None):
        self.weights = weights
        self.mapper = mapper

    def score_skeleton(self, skel1: List[str], skel2: List[str]) -> float:
        """Jaccard similarity on skeletons."""
        if not skel1 or not skel2: return 0.0
        s1, s2 = set(skel1), set(skel2)
        union = len(s1 | s2)
        return len(s1 & s2) / union if union > 0 else 0.0

    def score_ort(self, trace1: List[str], trace2: List[str]) -> float:
        """Overlap ratio for ORT trace."""
        if not trace1 or not trace2: return 0.0
        s1, s2 = set(trace1), set(trace2)
        match_count = sum(1 for char in s1 if char in s2)
        return min(match_count * 0.3, 1.0)

    def score_artic(self, vector1: Any, vector2: Any) -> float:
        """Placeholder for Articulatory Cosine Similarity."""
        # TODO: Implement real vector comparison
        return 0.5

    def score_semantics(self, lex1: Dict, lex2: Dict) -> float:
        """
        Score based on Concept ID match or Gloss overlap.
        """
        # 1. Exact Concept ID Match (High Confidence)
        c1 = lex1.get("concept_id")
        c2 = lex2.get("concept_id")
        if c1 and c2 and c1 == c2:
            return 1.0
            
        # 2. Gloss/Keyword Overlap (Fallback)
        # Assuming lex["keywords"] is populated
        k1 = set(lex1.get("keywords", []))
        k2 = set(lex2.get("keywords", []))
        
        if k1 and k2:
            overlap = k1 & k2
            if overlap:
                # Weighted by length of overlap vs total length
                return min(len(overlap) * 0.5, 0.8) # Max 0.8 for keyword match w/o ID
                
        return 0.0

    def generate_features(self, lex: Dict) -> Dict:
        """
        Lazy generation of features (skeleton, ort, concept_id).
        """
        # 1. Text Pre-processing
        lemma = lex.get("lemma", "")
        gloss = lex.get("gloss", "") or lex.get("definition", "")
        
        # Clean Gloss if HTML
        if "<" in gloss and ">" in gloss:
            gloss = clean_html(gloss)
            lex["gloss"] = gloss

        # Generate Keywords (simple tokenizer)
        # Use lemma for English, Gloss for Arabic (usually)
        text_source = f"{lemma} {gloss}"
        tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text_source)]
        lex["keywords"] = tokens

        # 2. Assign Concept ID if missing
        if "concept_id" not in lex and self.mapper:
            cid = self.mapper.get_concept_id(tokens)
            if cid:
                lex["concept_id"] = cid

        # 3. Generate Skeleton (if missing)
        if "skeleton" not in lex:
            src = lex.get("ipa", "") or lex.get("translit", "") or lex.get("orthography", "") or lemma
            vowels = set("aeiouyɑæɛɪɔʊʌəɨʉɯaːeːiːoːuː")
            # Filter for consonants
            skel = [c for c in src if c.isalpha() and c.lower() not in vowels]
            lex["skeleton"] = skel

        # 4. Generate ORT Trace (if missing)
        if "ort" not in lex:
            orth = lex.get("orthography", "") or lemma
            lex["ort"] = {"trace": list(orth)}
            
        return lex

    def calculate_score(self, sem_lex: Dict, ie_lex: Dict) -> Dict:
        """Compute the full DiscoveryScore."""
        # Ensure features exist
        sem_lex = self.generate_features(sem_lex)
        ie_lex = self.generate_features(ie_lex)

        s_skel = self.score_skeleton(sem_lex.get("skeleton", []), ie_lex.get("skeleton", []))
        s_ort = self.score_ort(sem_lex.get("ort", {}).get("trace", []), ie_lex.get("ort", {}).get("trace", []))
        s_artic = self.score_artic(None, None)
        s_sem = self.score_semantics(sem_lex, ie_lex)
        
        raw_score = (
            (s_skel * self.weights["skeleton"]) +
            (s_artic * self.weights["artic"]) +
            (s_ort * self.weights["ort"]) +
            (s_sem * self.weights["sem"])
        )
        
        return {
            "sem_id": sem_lex.get("id", sem_lex.get("lemma", "unknown")),
            "sem_gloss": sem_lex.get("gloss", "")[:30],
            "ie_id": ie_lex.get("id", ie_lex.get("lemma", "unknown")),
            "ie_gloss": ie_lex.get("lemma", "")[:30], # English lemma is usually the gloss
            "score": round(raw_score, 2),
            "concept_match": sem_lex.get("concept_id") if sem_lex.get("concept_id") == ie_lex.get("concept_id") else None,
            "components": {
                "skel": round(s_skel, 2),
                "artic": round(s_artic, 2),
                "ort": round(s_ort, 2),
                "sem": round(s_sem, 2)
            }
        }

def load_jsonl(path: Path, limit: int = 0, filter_arabic: bool = False) -> List[Dict]:
    data = []
    if not path.exists():
        print(f"Warning: {path} not found. returning empty list.")
        return data
    
    count = 0
    print(f"Reading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    row = json.loads(line)
                    # Filter for Arabic script if requested
                    if filter_arabic:
                        if not is_arabic(row.get("lemma", "")):
                            continue
                            
                    data.append(row)
                    count += 1
                    if limit > 0 and count >= limit:
                        break
                except json.JSONDecodeError:
                    pass
    print(f"Loaded {len(data)} items.")
    return data

def run(semitic_path: Optional[str] = None, ie_path: Optional[str] = None, concepts_path: Optional[str] = None, weights: Optional[Dict[str, float]] = None, limit: int = 1000):
    
    # Initialize Mapper
    mapper = ConceptMapper(Path(concepts_path)) if concepts_path else None
    scorer = DiscoveryScorer(weights if weights else DEFAULT_WEIGHTS, mapper=mapper)
    
    if semitic_path and ie_path:
        semitic_data = load_jsonl(Path(semitic_path), limit, filter_arabic=True)
        ie_data = load_jsonl(Path(ie_path), limit, filter_arabic=False)
    else:
        print("No input paths provided. Using MOCK data.")
        # Mock Data
        semitic_data = [
            {"lemma": "عَيْن", "gloss": "eye; spring", "ipa": "ʕayn"},
            {"lemma": "رَأْس", "gloss": "head", "ipa": "raʔs"}
        ]
        ie_data = [
            {"lemma": "eye", "ipa": "aɪ"},
            {"lemma": "head", "ipa": "hɛd"}
        ]

    leads = []
    print(f"Matching {len(semitic_data)} Semitic x {len(ie_data)} IE lexemes...")
    
    for sem in semitic_data:
        for ie in ie_data:
            lead = scorer.calculate_score(sem, ie)
            # Filter low scores 
            # If Semantic Match exists (score > 0), threshold can be lower.
            # If Phono only, threshold must be high.
            threshold = 2.0
            if lead["components"]["sem"] > 0.5:
                threshold = 1.5 # Boost semantic matches even if phono is weak
                
            if lead["score"] >= threshold:
                leads.append(lead)

    # Sort by score descending
    leads.sort(key=lambda x: x['score'], reverse=True)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for lead in leads:
            f.write(json.dumps(lead) + "\n")
            
    print(f"Generated {len(leads)} leads. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Prototype Matcher")
    parser.add_argument("--semitic", help="Path to Semitic JSONL")
    parser.add_argument("--ie", help="Path to Indo-European JSONL")
    parser.add_argument("--concepts", help="Path to Concepts JSONL")
    
    # Weight arguments
    parser.add_argument("--w_skel", type=float, default=DEFAULT_WEIGHTS["skeleton"])
    parser.add_argument("--w_artic", type=float, default=DEFAULT_WEIGHTS["artic"])
    parser.add_argument("--w_ort", type=float, default=DEFAULT_WEIGHTS["ort"])
    parser.add_argument("--w_sem", type=float, default=DEFAULT_WEIGHTS["sem"])
    parser.add_argument("--limit", type=int, default=1000)
    
    args = parser.parse_args()
    
    custom_weights = {
        "skeleton": args.w_skel,
        "artic": args.w_artic,
        "ort": args.w_ort,
        "sem": args.w_sem
    }
    
    run(args.semitic, args.ie, args.concepts, weights=custom_weights, limit=args.limit)