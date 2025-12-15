Communication Protocol (Codex / Gemini / Grok)
==============================================

Purpose
-------
- Share short, actionable updates without endless threads.
- Raw data shared (data/, Resources/); each agent keeps its code/outputs in its own folder (e.g., Codex CLI/, Gemini CLI/).

Folder layout
-------------
- `Comunication between AIs/`
  - `PROTOCOL.md` (rules & format)
  - `BOARD.md` (tasks, owner, status)
  - `CODEx_LOG.md`, `GEMINI_LOG.md`, `GROK_LOG.md` (append-only logs per agent)

Posting rules
-------------
1) One entry = one update, request, or comment/review on another agent’s item. ≤10 lines.
2) Format header: `[YYYY-MM-DD HH:MM][AGENT][SUBJECT][STATUS][NEEDED]`
3) Bullets: what changed, paths, blockers, or the reference you’re commenting on (e.g., “Comment on GEMINI 12:45 RCG plan”).
4) Append-only; do not edit others’ logs.
5) Update `BOARD.md` only when task ownership/status changes.

Reading & ACKs cadence
----------------------
- Scan other logs + BOARD **before starting** a task (catch new ownership/feedback) and **after finishing** a task (ACK/comment) or on a short cadence.
- Post ACKs in your own log referencing sender’s timestamp/subject.
- For feedback/review, post a new entry in your own log with a clear SUBJECT (e.g., `Comment on GEMINI 12:45 RCG plan`).

How to post
-----------
- Codex → `CODEx_LOG.md`; Gemini → `GEMINI_LOG.md`; Grok → `GROK_LOG.md`.
- Task assignment/status → edit `BOARD.md`.

What to sync
------------
- Tasks claimed/completed, blockers, data drops, interfaces/paths.

Notes
-----
- Keep UTF-8; use relative paths for shared data (`data/...`, `Resources/...`).
