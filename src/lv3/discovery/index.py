from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _require_faiss() -> None:
    try:
        import faiss  # noqa: F401
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency `faiss`. Install optional deps: `python -m pip install -r requirements.embeddings.txt`."
        ) from exc


@dataclass(frozen=True)
class FaissIndex:
    index_path: Path
    meta_path: Path
    dim: int

    def save(self, index) -> None:
        _require_faiss()
        import faiss

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self.index_path))
        self.meta_path.write_text(f'{{"dim": {self.dim}}}\n', encoding="utf-8")

    def load(self):
        _require_faiss()
        import faiss

        return faiss.read_index(str(self.index_path))


def build_flat_ip(vectors):
    _require_faiss()
    import faiss

    dim = int(vectors.shape[1])
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)
    return index, dim
