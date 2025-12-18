"""
LV3 discovery-first retrieval using:
- Meta SONAR for multilingual semantic similarity (raw script)
- CANINE for multilingual form similarity (raw Unicode)

This script is intended to generate *ranked leads* for human review (LV3).
It does not attempt LV4-style validation.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"

import sys

sys.path.insert(0, str(SRC_DIR))

from lv3.discovery.embeddings import CanineConfig, CanineEmbedder, SonarConfig, SonarEmbedder  # noqa: E402
from lv3.discovery.hybrid_scoring import HybridWeights, compute_hybrid  # noqa: E402
from lv3.discovery.index import FaissIndex, build_flat_ip  # noqa: E402
from lv3.discovery.jsonl import LexemeRow, read_jsonl_rows, write_jsonl  # noqa: E402
from lv3.discovery.lang import resolve_sonar_lang  # noqa: E402


@dataclass(frozen=True)
class CorpusSpec:
    lang: str
    stage: str
    path: Path
    sonar_lang: str | None = None

    @property
    def label(self) -> str:
        stage = self.stage or "unknown"
        return f"{self.lang}:{stage}"


def parse_spec(value: str) -> CorpusSpec:
    # Format: <lang>[@<stage>][@<sonar_lang>]=<path>
    # Examples:
    # - ara@modern=data/processed/arabic/quran_lemmas_enriched.jsonl
    # - eng@old@eng_Latn=data/processed/english/english_ipa_merged_pos.jsonl
    if "=" not in value:
        raise ValueError(f"Invalid spec {value!r}. Expected <lang>[@<stage>][@<sonar_lang>]=<path>.")
    left, right = value.split("=", 1)
    parts = [p for p in left.split("@") if p != ""]
    if not parts:
        raise ValueError(f"Invalid spec {value!r}: missing <lang>.")
    lang = parts[0]
    stage = parts[1] if len(parts) >= 2 else "unknown"
    sonar_lang = parts[2] if len(parts) >= 3 else None
    return CorpusSpec(lang=lang, stage=stage, path=Path(right), sonar_lang=sonar_lang)


def _safe_text(text: str) -> str:
    out = " ".join(str(text or "").split()).strip()
    return out if out else ""


def load_lexemes(spec: CorpusSpec, *, limit: int) -> list[LexemeRow]:
    path = spec.path
    if not path.is_absolute():
        path = REPO_ROOT / path
    rows = read_jsonl_rows(path, limit=limit)
    return rows


def cache_paths(*, model: str, spec: CorpusSpec) -> tuple[Path, Path, Path, Path]:
    base = REPO_ROOT / "OpenAI" / "output"
    embeddings_dir = base / "embeddings" / model / spec.lang / (spec.stage or "unknown")
    vectors_path = embeddings_dir / "vectors.npy"
    rows_path = embeddings_dir / "rows.jsonl"

    indexes_dir = base / "indexes" / model / spec.lang / (spec.stage or "unknown")
    index_path = indexes_dir / "index.faiss"
    meta_path = indexes_dir / "meta.json"
    return vectors_path, rows_path, index_path, meta_path


def maybe_load_vectors(vectors_path: Path, rows_path: Path):
    if vectors_path.exists() and rows_path.exists():
        import numpy as np

        vecs = np.load(vectors_path)
        rows = read_jsonl_rows(rows_path, limit=0)
        return vecs, rows
    return None, None


def save_vectors(vectors_path: Path, rows_path: Path, vecs, rows: list[LexemeRow]) -> None:
    import numpy as np

    vectors_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(vectors_path, vecs)
    write_jsonl(rows_path, (r.data | {"_row_idx": r.row_idx} for r in rows))


def embed_corpus(
    *,
    model: str,
    spec: CorpusSpec,
    rows: list[LexemeRow],
    limit: int,
    device: str,
    sonar_cfg: SonarConfig,
    canine_cfg: CanineConfig,
    rebuild_cache: bool,
):
    vectors_path, rows_path, _, _ = cache_paths(model=model, spec=spec)
    if not rebuild_cache:
        vecs, cached_rows = maybe_load_vectors(vectors_path, rows_path)
        if vecs is not None and cached_rows is not None:
            return vecs, cached_rows

    texts: list[str] = []
    for r in rows:
        t = _safe_text(r.lemma)
        texts.append(t if t else r.lexeme_id)
    if model == "sonar":
        embedder = SonarEmbedder(config=sonar_cfg)
        sonar_lang = resolve_sonar_lang(spec.lang, spec.sonar_lang)
        vecs = embedder.embed(texts, sonar_lang=sonar_lang)
    elif model == "canine":
        embedder = CanineEmbedder(config=canine_cfg, device=device)
        vecs = embedder.embed(texts)
    else:
        raise ValueError(f"Unknown model {model!r}.")

    save_vectors(vectors_path, rows_path, vecs, rows)
    return vecs, rows


def build_or_load_index(*, model: str, spec: CorpusSpec, vectors, rebuild_index: bool):
    _, _, index_path, meta_path = cache_paths(model=model, spec=spec)
    idx_meta = FaissIndex(index_path=index_path, meta_path=meta_path, dim=int(vectors.shape[1]))

    if not rebuild_index and index_path.exists():
        return idx_meta.load()

    index, dim = build_flat_ip(vectors)
    idx_meta = FaissIndex(index_path=index_path, meta_path=meta_path, dim=dim)
    idx_meta.save(index)
    return index


def search_index(index, query_vectors, topk: int):
    import numpy as np

    topk = int(topk)
    if topk <= 0:
        raise ValueError("topk must be > 0")
    scores, idxs = index.search(np.asarray(query_vectors, dtype="float32"), topk)
    return scores, idxs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Repeatable. Format: <lang>[@<stage>][@<sonar_lang>]=<path>",
    )
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="Repeatable. Format: <lang>[@<stage>][@<sonar_lang>]=<path>",
    )
    parser.add_argument("--models", nargs="+", default=["sonar", "canine"], choices=["sonar", "canine"])
    parser.add_argument("--topk", type=int, default=200, help="Top-K candidates per target corpus (per model).")
    parser.add_argument("--max-out", type=int, default=200, help="Max leads written per source lexeme.")
    parser.add_argument("--limit", type=int, default=0, help="Limit rows loaded per corpus (0 = no limit).")
    parser.add_argument("--device", type=str, default=os.environ.get("LV3_DEVICE", "cpu"))
    parser.add_argument("--rebuild-cache", action="store_true", help="Recompute embeddings even if cached.")
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild FAISS indexes even if cached.")
    parser.add_argument("--sonar-encoder", type=str, default="text_sonar_basic_encoder")
    parser.add_argument("--sonar-tokenizer", type=str, default="text_sonar_basic_encoder")
    parser.add_argument("--canine-model", type=str, default="google/canine-c")
    parser.add_argument("--canine-pooling", type=str, default="mean", choices=["mean", "cls"])
    parser.add_argument("--no-hybrid", action="store_true", help="Disable heuristic scoring after retrieval.")
    parser.add_argument("--w-sonar", type=float, default=HybridWeights.sonar)
    parser.add_argument("--w-canine", type=float, default=HybridWeights.canine)
    parser.add_argument("--w-orth", type=float, default=HybridWeights.orthography)
    parser.add_argument("--w-sound", type=float, default=HybridWeights.sound)
    parser.add_argument("--w-skeleton", type=float, default=HybridWeights.skeleton)
    parser.add_argument("--output", type=Path, default=None, help="Override output JSONL path.")
    args = parser.parse_args()

    if not args.source or not args.target:
        raise SystemExit("Provide at least one --source and one --target.")

    sources = [parse_spec(s) for s in args.source]
    targets = [parse_spec(t) for t in args.target]

    sonar_cfg = SonarConfig(encoder=args.sonar_encoder, tokenizer=args.sonar_tokenizer)
    canine_cfg = CanineConfig(model_id=args.canine_model, pooling=args.canine_pooling)
    hybrid_weights = HybridWeights(
        sonar=float(args.w_sonar),
        canine=float(args.w_canine),
        orthography=float(args.w_orth),
        sound=float(args.w_sound),
        skeleton=float(args.w_skeleton),
    )

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = args.output or (REPO_ROOT / "Gemini" / "output" / "leads" / f"discovery_{run_id}.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    target_indexes: dict[str, list[tuple[CorpusSpec, Any, list[LexemeRow]]]] = {m: [] for m in args.models}

    for model in args.models:
        for spec in targets:
            rows = load_lexemes(spec, limit=args.limit)
            vecs, cached_rows = embed_corpus(
                model=model,
                spec=spec,
                rows=rows,
                limit=args.limit,
                device=args.device,
                sonar_cfg=sonar_cfg,
                canine_cfg=canine_cfg,
                rebuild_cache=args.rebuild_cache,
            )
            index = build_or_load_index(model=model, spec=spec, vectors=vecs, rebuild_index=args.rebuild_index)
            target_indexes[model].append((spec, index, cached_rows))

    with out_path.open("w", encoding="utf-8") as out_fh:
        for source_spec in sources:
            source_rows = load_lexemes(source_spec, limit=args.limit)
            # Compute embeddings for the source corpus per model (cached).
            source_vectors_by_model: dict[str, Any] = {}
            source_rows_by_model: dict[str, list[LexemeRow]] = {}
            for model in args.models:
                vecs, cached_rows = embed_corpus(
                    model=model,
                    spec=source_spec,
                    rows=source_rows,
                    limit=args.limit,
                    device=args.device,
                    sonar_cfg=sonar_cfg,
                    canine_cfg=canine_cfg,
                    rebuild_cache=args.rebuild_cache,
                )
                source_vectors_by_model[model] = vecs
                source_rows_by_model[model] = cached_rows

            # Stream results per source lexeme (avoid huge in-memory joins).
            max_out = int(args.max_out)
            topk = int(args.topk)
            for i, src_row in enumerate(source_rows):
                candidates: dict[str, dict[str, Any]] = {}

                for model in args.models:
                    src_vec = source_vectors_by_model[model][i : i + 1]
                    for tgt_spec, tgt_index, tgt_rows in target_indexes[model]:
                        scores, idxs = search_index(tgt_index, src_vec, topk=topk)
                        for score, idx in zip(scores[0].tolist(), idxs[0].tolist(), strict=True):
                            if idx < 0:
                                continue
                            tgt_row = tgt_rows[idx]
                            key = f"{tgt_spec.lang}|{tgt_spec.stage}|{tgt_row.lexeme_id}|{tgt_row.row_idx}"
                            entry = candidates.get(key)
                            if entry is None:
                                entry = {
                                    "run_id": run_id,
                                    "source": {
                                        "id": src_row.lexeme_id,
                                        "row_idx": src_row.row_idx,
                                        "lemma": src_row.lemma,
                                        "lang": source_spec.lang,
                                        "stage": source_spec.stage,
                                    },
                                    "target": {
                                        "id": tgt_row.lexeme_id,
                                        "row_idx": tgt_row.row_idx,
                                        "lemma": tgt_row.lemma,
                                        "lang": tgt_spec.lang,
                                        "stage": tgt_spec.stage,
                                    },
                                    "scores": {},
                                    "retrieved_by": [],
                                    "_source_fields": {
                                        "lemma": src_row.data.get("lemma"),
                                        "translit": src_row.data.get("translit"),
                                        "ipa": src_row.data.get("ipa"),
                                        "ipa_raw": src_row.data.get("ipa_raw"),
                                    },
                                    "_target_fields": {
                                        "lemma": tgt_row.data.get("lemma"),
                                        "translit": tgt_row.data.get("translit"),
                                        "ipa": tgt_row.data.get("ipa"),
                                        "ipa_raw": tgt_row.data.get("ipa_raw"),
                                    },
                                }
                                candidates[key] = entry
                            entry["scores"][model] = float(score)
                            if model not in entry["retrieved_by"]:
                                entry["retrieved_by"].append(model)

                # Category assignment: discovery triage signal (not validation).
                for entry in candidates.values():
                    got_sonar = "sonar" in entry["scores"]
                    got_canine = "canine" in entry["scores"]
                    if got_sonar and got_canine:
                        entry["category"] = "strong_union"
                    elif got_sonar:
                        entry["category"] = "semantic_only"
                    elif got_canine:
                        entry["category"] = "form_only"
                    else:
                        entry["category"] = "unclassified"

                    if not args.no_hybrid:
                        entry["hybrid"] = compute_hybrid(
                            source=entry.get("_source_fields", {}),
                            target=entry.get("_target_fields", {}),
                            sonar=entry["scores"].get("sonar"),
                            canine=entry["scores"].get("canine"),
                            weights=hybrid_weights,
                        )

                    entry["provenance"] = {
                        "lv": "LV3",
                        "mode": "discovery_retrieval",
                        "models": args.models,
                        "topk_per_target": topk,
                        "max_out_per_source": max_out,
                    }

                def sort_key(e: dict[str, Any]):
                    scores = e.get("scores", {})
                    hybrid = e.get("hybrid") or {}
                    combined = hybrid.get("combined_score")
                    return (
                        float(combined) if combined is not None else -1e9,
                        2 if e.get("category") == "strong_union" else 1,
                        float(scores.get("sonar", -1e9)),
                        float(scores.get("canine", -1e9)),
                    )

                ranked = sorted(candidates.values(), key=sort_key, reverse=True)[:max_out]
                for row in ranked:
                    row.pop("_source_fields", None)
                    row.pop("_target_fields", None)
                    out_fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote discovery leads: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
