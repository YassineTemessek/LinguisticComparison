"""
Merge English IPA sources into a single lexeme file.

Inputs:
- data/processed/_intermediate/english/english_ipa_with_pos.jsonl (ipa-dict, per-variant)
- data/processed/_intermediate/english/english_cmudict_ipa_with_pos.jsonl (cmudict)

Outputs:
- data/processed/_intermediate/english/english_ipa_merged.jsonl

Notes:
- De-duplicates by (lemma_lower, ipa) and unions POS where possible.
- Adds `source_priority` (lower is higher priority): ipa-dict=1, cmudict=2.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

from processed_schema import coerce_pos_list, ensure_min_schema, normalize_ipa


def iter_jsonl(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def merge(
    ipa_dict_path: pathlib.Path,
    cmudict_path: pathlib.Path,
    out_path: pathlib.Path,
) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    merged: dict[tuple[str, str], dict] = {}

    def upsert(rec: dict, priority: int) -> None:
        lemma = str(rec.get("lemma") or "").strip()
        ipa_val = normalize_ipa(str(rec.get("ipa") or rec.get("ipa_raw") or ""))
        if not lemma or not ipa_val:
            return
        key = (lemma.lower(), ipa_val)

        rec["lemma"] = lemma
        rec["ipa_raw"] = rec.get("ipa_raw", rec.get("ipa", ""))
        rec["ipa"] = ipa_val
        rec["pos"] = coerce_pos_list(rec.get("pos"))
        rec["source_priority"] = priority
        rec = ensure_min_schema(rec, default_language="eng", default_stage="Modern", default_script="Latin", default_lemma_status="auto_brut")

        if key not in merged:
            merged[key] = rec
            return

        cur = merged[key]
        cur_pos = set(coerce_pos_list(cur.get("pos")))
        new_pos = set(coerce_pos_list(rec.get("pos")))
        if new_pos:
            cur["pos"] = sorted(cur_pos | new_pos)

        if int(cur.get("source_priority", 999)) <= priority:
            return
        # Replace payload with higher-priority record, but keep unioned POS.
        pos_union = cur.get("pos", [])
        merged[key] = rec
        merged[key]["pos"] = pos_union

    for rec in iter_jsonl(ipa_dict_path):
        upsert(rec, priority=1)
    for rec in iter_jsonl(cmudict_path):
        # Ensure source/variant are present for clarity.
        rec.setdefault("source", "cmudict")
        rec.setdefault("variant", "cmudict")
        upsert(rec, priority=2)

    total = 0
    with out_path.open("w", encoding="utf-8") as out_f:
        for _, rec in sorted(merged.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ipa_dict", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_ipa_with_pos.jsonl"))
    ap.add_argument("--cmudict", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_cmudict_ipa_with_pos.jsonl"))
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/processed/_intermediate/english/english_ipa_merged.jsonl"))
    args = ap.parse_args()

    total = merge(args.ipa_dict, args.cmudict, args.output)
    print(f"Wrote {total} merged records to {args.output}")


if __name__ == "__main__":
    main()
