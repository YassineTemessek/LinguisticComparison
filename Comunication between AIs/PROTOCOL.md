Communication Protocol (Codex / Gemini / Grok)
===============================================

Message format (append-only logs)
---------------------------------
- Header: `[YYYY-MM-DD HH:MM][AGENT][SUBJECT][STATUS][NEEDED]`
- Follow with ≤5 bullet lines: what changed, paths, blockers, or reference you’re commenting on (e.g., “Comment on GEMINI 12:45 RCG plan”).
- Example:
  - `[2025-12-03 11:00][CODEX][RCG preview][INFO][NONE]`
    - Outputs: Codex CLI/output/match_preview.csv, ..._heatmap.png
    - Data: eng_ipa_merged_pos, Latin/Greek filtered, Quran lemmas

Files
-----
- `CODEx_LOG.md`, `GEMINI_LOG.md`, `GROK_LOG.md`: append your own entries only.
- `BOARD.md`: shared status board (tasks, owner, status).

Board fields
------------
- Task | Owner (Codex/Gemini/Grok) | Status (todo/in-progress/done/blocked) | Notes

Rules
-----
1) Append, do not delete. Keep entries short.
2) Reference files with relative paths.
3) For a response, add a new entry in your log referencing the item; do not edit others’ logs.
4) Update `BOARD.md` only when ownership/status changes.
5) Use UTC or include timezone if relevant.

Shared data
-----------
- Keep raw/processed data in `data/` and `Resources/`.
- Keep agent-specific code/outputs in respective folders (e.g., `Codex CLI/`).
