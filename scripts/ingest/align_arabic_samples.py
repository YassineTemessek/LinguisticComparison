"""
Quick alignment between HF roots and Quran lemmas to test recall.
Scoring: normalized Levenshtein on IPA/translit + skeleton overlap.
Outputs: outputs/arabic_alignment_samples.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple
from itertools import product

def lev(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    dp = [[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(len(a)+1):
        dp[i][0] = i
    for j in range(len(b)+1):
        dp[0][j] = j
    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[-1][-1]

def sim(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    d = lev(a, b)
    m = max(len(a), len(b))
    return max(0.0, 1 - d/m)

def skeleton(s: str) -> str:
    vowels = set("aeiouāīūɛɔ")
    return "".join(ch for ch in s if ch.isalpha() and ch.lower() not in vowels)

def load_jsonl(path: Path, limit: int) -> List[dict]:
    items = []
    with path.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= limit:
                break
            items.append(json.loads(line))
    return items

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hf", type=Path, default=Path("data/processed/arabic/hf_roots.jsonl"))
    ap.add_argument("--quran", type=Path, default=Path("data/processed/arabic/quran_lemmas_enriched.jsonl"))
    ap.add_argument("--hf-limit", type=int, default=200)
    ap.add_argument("--quran-limit", type=int, default=200)
    ap.add_argument("--out", type=Path, default=Path("outputs/arabic_alignment_samples.csv"))
    args = ap.parse_args()

    hf = load_jsonl(args.hf, args.hf_limit)
    quran = load_jsonl(args.quran, args.quran_limit)

    headers = ["hf_lemma","hf_ipa","qur_lemma","qur_ipa","score"]
    rows = []
    for h in hf:
        h_ipa = h.get("ipa","") or h.get("translit","") or h.get("lemma","")
        hs = skeleton(h_ipa)
        for q in quran:
            q_ipa = q.get("ipa","") or q.get("translit","") or q.get("lemma","")
            qs = skeleton(q_ipa)
            score = 0.7*sim(h_ipa, q_ipa) + 0.3*sim(hs, qs)
            if score > 0.5:
                rows.append([h.get("lemma",""), h_ipa, q.get("lemma",""), q_ipa, round(score,3)])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        f.write(",".join(headers)+"\n")
        for r in rows:
            f.write(",".join(str(x) for x in r)+"\n")
    print(f"Wrote {len(rows)} alignments to {args.out}")

if __name__ == "__main__":
    main()
