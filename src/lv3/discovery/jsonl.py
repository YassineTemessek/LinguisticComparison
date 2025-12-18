from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class LexemeRow:
    row_idx: int
    data: dict[str, Any]

    @property
    def lemma(self) -> str:
        return str(self.data.get("lemma") or "").strip()

    @property
    def lexeme_id(self) -> str:
        raw = self.data.get("id")
        if raw is None or str(raw).strip() == "":
            return f"row:{self.row_idx}"
        return str(raw)


def read_jsonl_rows(path: Path, *, limit: int = 0) -> list[LexemeRow]:
    rows: list[LexemeRow] = []
    if not path.exists():
        raise FileNotFoundError(str(path))

    with path.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if limit and len(rows) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            rows.append(LexemeRow(row_idx=i, data=json.loads(line)))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
