# coding: utf-8
from __future__ import annotations

"""
Convert extracted StarDict dictionaries (from the Wiktionary-Dictionaries repo)
into JSONL for downstream ingest.

Usage:
  python scripts/convert_stardict.py --root data/raw/wiktionary_extracted --out data/processed/wiktionary_stardict/raw
  python scripts/convert_stardict.py --package "data/raw/wiktionary_extracted/Arabic-English Wiktionary dictionary stardict/Arabic-English Wiktionary dictionary stardict" --lang ara --out data/processed/wiktionary_stardict/raw
"""

import argparse
import gzip
import json
import pathlib
from typing import Iterable, Iterator, List, Tuple

from processed_schema import ensure_min_schema, strip_html


def read_ifo(ifo_path: pathlib.Path) -> dict:
    meta: dict = {}
    for line in ifo_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in line:
            key, val = line.split("=", 1)
            meta[key.strip()] = val.strip()
    return meta


def iter_idx(idx_path: pathlib.Path, offset_bits: int) -> Iterator[Tuple[str, int, int]]:
    data = idx_path.read_bytes()
    pos = 0
    while pos < len(data):
        end = data.find(b"\x00", pos)
        if end == -1:
            break
        word = data[pos:end].decode("utf-8", errors="ignore")
        pos = end + 1
        if offset_bits == 64:
            offset = int.from_bytes(data[pos : pos + 8], "big")
            pos += 8
        else:
            offset = int.from_bytes(data[pos : pos + 4], "big")
            pos += 4
        size = int.from_bytes(data[pos : pos + 4], "big")
        pos += 4
        yield word, offset, size


def load_dict_bytes(dict_path: pathlib.Path) -> bytes:
    if dict_path.suffix == ".dz":
        with gzip.open(dict_path, "rb") as fh:
            return fh.read()
    return dict_path.read_bytes()


LANG_META = {
    # Semitic / Arabic varieties
    "Arabic-English": ("ara", "Modern", "Arabic"),
    "Egyptian_Arabic-English": ("arz", "Modern", "Arabic"),
    "Gulf_Arabic-English": ("afb", "Modern", "Arabic"),
    "Hijazi_Arabic-English": ("acw", "Modern", "Arabic"),
    "South_Levantine_Arabic-English": ("apc", "Modern", "Arabic"),
    "Classical_Syriac-English": ("syc", "Classical", "Syriac"),
    "Aramaic-English": ("arc", "Classical", "Aramaic"),
    "Assyrian_Neo-Aramaic-English": ("aii", "Modern", "Syriac"),
    "Ugaritic-English": ("uga", "Ancient", "Ugaritic"),
    "Akkadian-English": ("akk", "Ancient", "Cuneiform"),
    "Ge'ez-English": ("gez", "Classical", "Ethiopic"),
    "Hebrew-English": ("heb", "Modern", "Hebrew"),
    # Indo-European / others
    "Latin-English": ("lat", "Classical", "Latin"),
    "Ancient_Greek-English": ("grc", "Classical", "Greek"),
    "Greek-English": ("ell", "Modern", "Greek"),
    "Old_English-English": ("ang", "Old", "Latin"),
    "Middle_English-English": ("enm", "Middle", "Latin"),
}


def label_from_safe_slug(safe_slug: str) -> str:
    suffix = "_Wiktionary_dictionary_stardict"
    if safe_slug.endswith(suffix):
        return safe_slug[: -len(suffix)]
    return safe_slug


def infer_lang_stage_script(safe_slug: str, inferred_lang: str) -> tuple[str, str, str]:
    label = label_from_safe_slug(safe_slug)
    meta = LANG_META.get(label)
    if meta:
        return meta
    # fallback (keeps older behavior but fills required fields)
    return inferred_lang, "Attested", "Unknown"


def convert_package(
    pkg_dir: pathlib.Path,
    lang: str,
    stage: str,
    script: str,
    out_path: pathlib.Path,
    source: str = "wiktionary-stardict",
    source_ref_prefix: str | None = None,
    limit: int | None = None,
) -> int:
    ifo = next(pkg_dir.glob("*.ifo"), None)
    if not ifo:
        raise FileNotFoundError(f"No .ifo file in {pkg_dir}")
    idx = next(pkg_dir.glob("*.idx"), None)
    if not idx:
        raise FileNotFoundError(f"No .idx file in {pkg_dir}")
    dict_file = next((p for p in pkg_dir.glob("*.dict*") if p.suffix in {".dict", ".dz"} or p.name.endswith(".dict.dz")), None)
    if not dict_file:
        raise FileNotFoundError(f"No .dict/.dict.dz file in {pkg_dir}")

    meta = read_ifo(ifo)
    offset_bits = int(meta.get("idxoffsetbits", "32"))
    dict_bytes = load_dict_bytes(dict_file)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_path.open("w", encoding="utf-8") as out_f:
        for word, offset, size in iter_idx(idx, offset_bits):
            gloss_bytes = dict_bytes[offset : offset + size]
            gloss = gloss_bytes.decode("utf-8", errors="ignore")
            gloss_plain = strip_html(gloss)
            entry = {
                "lemma": word,
                "gloss_html": gloss,
                "gloss_plain": gloss_plain,
                "language": lang,
                "stage": stage,
                "script": script,
                "source": source,
                "source_ref": f"{source_ref_prefix}:{word}" if source_ref_prefix else word,
                "lemma_status": "auto_brut",
                "pos": [],
            }
            entry = ensure_min_schema(entry)
            out_f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            count += 1
            if limit and count >= limit:
                break
    return count


def discover_packages(root: pathlib.Path) -> List[pathlib.Path]:
    return [p for p in root.rglob("*.ifo")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=pathlib.Path, help="Root folder containing extracted stardict packages (searches recursively for .ifo).")
    ap.add_argument("--package", type=pathlib.Path, help="Specific package folder containing .ifo/.idx/.dict(.dz).")
    ap.add_argument("--out", type=pathlib.Path, required=True, help="Output directory for JSONL files.")
    ap.add_argument("--lang", type=str, default=None, help="Language code override. If omitted, language is inferred from folder name prefix before first space.")
    ap.add_argument("--limit", type=int, default=None, help="Optional limit for debugging.")
    args = ap.parse_args()

    packages: Iterable[pathlib.Path]
    if args.package:
        packages = [args.package]
    elif args.root:
        packages = [ifo.parent for ifo in discover_packages(args.root)]
    else:
        ap.error("Provide --package or --root")
        return

    for pkg in packages:
        folder_name = pkg.name
        inferred_lang = args.lang or folder_name.split(" ")[0].lower()
        safe_slug = folder_name.replace(" ", "_")
        lang_code, stage, script = infer_lang_stage_script(safe_slug, inferred_lang)
        out_file = args.out / f"{safe_slug}.jsonl"
        try:
            total = convert_package(pkg, lang_code, stage, script, out_file, source_ref_prefix=safe_slug, limit=args.limit)
            print(f"[ok] {pkg} -> {out_file} ({total} entries, lang={lang_code}, stage={stage}, script={script})")
        except Exception as exc:  # noqa: BLE001
            print(f"[fail] {pkg}: {exc}")


if __name__ == "__main__":
    main()
