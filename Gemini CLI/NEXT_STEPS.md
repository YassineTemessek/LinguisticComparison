# Gemini CLI Plan: Rapid Candidate Generation (RCG)

**Role:** Lead Architect & Matching Engine Lead
**Objective:** Implement the "Rapid Candidate Generation" pipeline to find connections between Semitic and Indo-European lexemes.

## Folder Policy
- **Scripts:** All my execution logic resides in `Gemini CLI/scripts/`.
- **Outputs:** All my results (Leads, Heatmaps) go to `Gemini CLI/output/`.
- **Inputs:** I will read from `Codex CLI/output/` (if available) or generate my own mock data for testing.

## Phase 1: Infrastructure Setup (Completed)
- [x] Initialize `src/score` module (The Matcher).
- [x] Create `Gemini CLI/scripts/prototype_matcher.py` to test matching logic.
- [x] Define `DiscoveryScore` algorithm explicitly.

## Phase 2: The Matcher Logic (RCG) (Completed)
- [x] **Skeleton Matcher:** Implement Consonant-only matching (Levenshtein on skeletons).
- [x] **ORT Matcher:** Implement Orthographic Trace matching (English fossils).
- [x] **Scoring Engine:** Implement the weighted formula with Semantic Gating.
  `DiscoveryScore = w1*Skel + w2*Artic + w3*ORT + w4*Sem`
- [x] **Validation:** Validated on 2k x 2k sample with Semantic Gating (Score 5.0 matches found).

## Phase 3: Integration & Scale (Current)
- [x] **Pipeline Orchestration:** Created `run_full_matching_pipeline.py` to handle chunked inputs.
- [ ] **Full Run:** Execute the pipeline on the full dataset (~4 hours).
- [ ] **Heatmap Visualization:** Generate `comparison_heatmap.png` from the final `leads.jsonl`.

## Immediate Next Steps
1. Execute `python "Gemini CLI/scripts/run_full_matching_pipeline.py"` (No limit) when ready.
2. Analyze the full output (likely >100k leads).
3. Generate visualization.