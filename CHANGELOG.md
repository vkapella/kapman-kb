# KapMan KB Changelog

## [3.0.0-alpha] — 2026-05-10

### 2026-05-10 — DEALER_v3.0.md content cutover (session 3 of 15)

- Content for `llm_runtime/DEALER_v3.0.md` drafted and approved in Claude.ai session 3 of 15.
- File status moved from `scaffolding` to `draft`.
- Architectural decision: pipeline-computation content (formulas, filter thresholds, weighting tiers, slope window, confidence cutoffs, runtime defaults) moved to forthcoming `engineering_only/DEALER_PIPELINE_v3.0.md`; runtime-relevant content (DGPI tier vocabulary, hostile macro composite, near-flip zone, dealer-status label semantics, stale-data handling, two-layer macro/ticker model) preserved in `llm_runtime/DEALER_v3.0.md`.
- All 14 v2.3 DEALER_NNN anchors preserved in INDEX.md migration table; zero DROPPED.
- DGPI tier bands established as v3.0 reference values: ≥ 50 strongly supportive; 20 to 49 moderately supportive; -19 to 19 near-neutral; -49 to -20 weakening; ≤ -50 hostile.
- Hostile macro composite locked in as v3.0 reference: SPY below gamma flip AND SPY DGPI ≤ -20.
- Near-flip zone locked in as v3.0 reference: symmetric ±0.25% of spot band around the gamma flip level (scales across SPY and per-ticker layers).

### Changed
- `RISK_v3.0.md` rewritten from scaffolding to draft. Sizing ladder expressed as regime-conditional judgment bands; v2.3 percentages preserved in Appendix as reference points. New real-capital-only denominator model replaces v2.3 combined-account denominator.

### Migrated
- `RISK_005` → `llm_runtime/RISK_v3.0.md` § Legacy anchors. Body-text references in legacy report legends continue to resolve.

### Dropped
- `RISK_001`, `RISK_002`, `RISK_003`, `RISK_004` — engineering-state observations about C4 pipeline behavior, no LLM runtime effect. See INDEX.md for rationale.

## v3.0.0-alpha-setup - 2026-05-10

Mechanical scaffolding complete. Directory structure, file skeletons,
legacy anchor extraction, and migration table generated per
MIGRATION_v2_to_v3.md. No rule content rewritten yet. v2.3 files
preserved in archive/v2.3/.
