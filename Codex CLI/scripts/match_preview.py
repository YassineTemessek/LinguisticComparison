"""
Quick RCG-like preview for a few Tier-A concepts using existing processed data.
Languages: English (eng), Latin (lat), Ancient Greek (grc), Arabic (ara).
Scoring: normalized Levenshtein on IPA/translit; skeleton overlap.
Outputs:
  - output/match_preview.csv
  - output/match_preview_heatmap.png
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Concepts to run
CONCEPTS = {
    "EYE": {
        "eng": ["eye"],
        "lat": ["oculus"],
        "grc": ["οφθαλμος", "ὀφθαλμός"],
        "ara": ["عين", "عَيْن"],
    },
    "HAND": {
        "eng": ["hand"],
        "lat": ["manus"],
        "grc": ["χειρ", "χείρ"],
        "ara": ["يد", "يَد"],
    },
    "HEART": {
        "eng": ["heart"],
        "lat": ["cor"],
        "grc": ["καρδια", "καρδία"],
        "ara": ["قلب", "قَلْب"],
    },
}

LANGS = ["eng", "lat", "grc", "ara"]

PATHS = {
    "eng": Path("data/processed/english/english_ipa_merged_pos.jsonl"),
    "lat": Path("data/processed/wiktionary_stardict/filtered/Latin-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    "grc": Path("data/processed/wiktionary_stardict/filtered/Ancient_Greek-English_Wiktionary_dictionary_stardict_filtered.jsonl"),
    "ara": Path("data/processed/arabic/quran_lemmas_enriched.jsonl"),
}


def lev(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[-1][-1]


def sim(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    d = lev(a, b)
    m = max(len(a), len(b))
    return max(0.0, 1 - d / m)


def skeleton(s: str) -> str:
    return "".join(ch for ch in s if ch.isalpha() and ch.lower() not in "aeiouāīūɛɔαεηιουω")


def load_first_match(path: Path, targets: List[str]) -> Dict[str, str]:
    targets_lc = {t.lower() for t in targets}
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            lemma = str(rec.get("lemma", "")).lower()
            if lemma in targets_lc:
                ipa = rec.get("ipa", "") or rec.get("translit", "") or lemma
                return {"lemma": rec.get("lemma", ""), "ipa": ipa}
    return {"lemma": "", "ipa": ""}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output_csv", type=Path, default=Path("output/match_preview.csv"))
    ap.add_argument("--output_png", type=Path, default=Path("output/match_preview_heatmap.png"))
    args = ap.parse_args()

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for concept, targ in CONCEPTS.items():
        forms = {}
        for lang in LANGS:
            forms[lang] = load_first_match(PATHS[lang], targ.get(lang, []))
        row = {"concept": concept}
        for (l1, l2) in combinations(LANGS, 2):
            ipa1 = forms[l1]["ipa"]
            ipa2 = forms[l2]["ipa"]
            sk1 = skeleton(ipa1)
            sk2 = skeleton(ipa2)
            score = 0.7 * sim(ipa1, ipa2) + 0.3 * sim(sk1, sk2)
            row[f"{l1}-{l2}"] = round(score, 3)
        rows.append((concept, row, forms))

    # write CSV
    headers = ["concept"] + [f"{l1}-{l2}" for l1, l2 in combinations(LANGS, 2)]
    with args.output_csv.open("w", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for _, r, _ in rows:
            f.write(",".join(str(r[h]) for h in headers) + "\n")

    # heatmaps per concept
    fig, axes = plt.subplots(1, len(rows), figsize=(4 * len(rows), 4))
    if len(rows) == 1:
        axes = [axes]
    for ax, (concept, r, _) in zip(axes, rows):
        mat = np.ones((len(LANGS), len(LANGS)))
        for i, l1 in enumerate(LANGS):
            for j, l2 in enumerate(LANGS):
                if i == j:
                    mat[i, j] = 1.0
                elif i < j:
                    key = f"{l1}-{l2}"
                    mat[i, j] = float(r[key])
                    mat[j, i] = float(r[key])
        sns.heatmap(mat, vmin=0, vmax=1, annot=True, fmt=".2f", xticklabels=LANGS, yticklabels=LANGS, ax=ax, cmap="Blues")
        ax.set_title(concept)
    plt.tight_layout()
    plt.savefig(args.output_png, dpi=150)
    plt.close()
    print("Wrote", args.output_csv)
    print("Wrote", args.output_png)


if __name__ == "__main__":
    main()
