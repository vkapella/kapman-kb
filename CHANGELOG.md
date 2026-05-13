# KapMan KB Changelog

## [3.0.0-alpha] — 2026-05-13 — Session 13

### Session 13 — 2026-05-13

### Added
- `SIC_SECTOR_MAP_v3.0.md` (T3, draft) — SIC range -> sector -> benchmark ETF lookup table.
  Replaces `SIC_SECTOR_ETF_MAPPING_v2.3.md`. Changes from v2.3: XLP added for Consumer Staples
  (was —); redundant point-code sub-rows consolidated to ranges; Python lookup code and Quick
  Reference table moved to engineering_only (not yet created — pending). No legacy rule IDs
  carried; v2.3 antecedent had none.

### Updated
- `REPORT_STYLE_v3.0.md` — scaffold replaced with session-11 draft content. Status: scaffolding -> draft.

## [3.0.0-alpha] — 2026-05-13 — Session 12

### Session 12 — 2026-05-13
- `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md`: scaffolding → draft.
  Added: Principle (T0 peer authority split), KB file inventory table (14 files),
  tier model (T0–T3 with conflict resolution protocol), mode detection (3 modes,
  5-step ordered sequence), session entry sequence (5-step blocking checklist).
  Dropped: Legacy anchors section (no rule IDs map here), Appendix section
  (no unhoused formulas — all migrated to domain files in sessions 1–11).
  RISK_v3.0.md added to KB inventory after upload confirmation.

## [3.0.0-alpha] — 2026-05-12 — Session 11

### Added
- Added `REPORT_STYLE_v3.0.md` (T3, draft). Direct successor to
  `KAPMAN_REPORT_STYLE_GLOSSARY_v2.3.md` (full migration). New v3.0
  content: four-level urgency hierarchy for portfolio row classes
  (`.advisory`, `.warn` DTE-decay use, `.exited`, `.expired`);
  `.tag-critical` badge class for Expired unacknowledged positions;
  `.flags-col` 200px column class for portfolio Flags field;
  body font-size corrected 7.8pt -> 7pt; print-color-adjust declarations
  made explicit; `rationale-col` 180px confirmed consistent with
  REPORT_FORMAT 20-word cap.

## [3.0.0-alpha] — 2026-05-12 — Session 10

### Added
- `REPORT_FORMAT_v3.0.md` (T3, status: draft): information architecture specification for KapMan report output. Defines section presence and ordering rules by mode (Screening, Portfolio, Hybrid), field ordering and caps, source bar placement contract, legend/footer sequencing contract, and output structure for per-ticker and per-position details.

## [3.0.0-alpha] — 2026-05-12 — Session 9

### Added
- `PORTFOLIO_MGMT_v3.0.md` (T2 runbook): Position lifecycle layer. Owns position context schema, Portfolio mode workflow sequence (7 steps), position lifecycle state machine (Open / Advisory / Exited / Expired), Regime exit advisory operationalization (4 branches), DTE decay warning, exit-trigger proximity evaluation, Hybrid mode regime data reuse, position entry recording, Exited and Expired position handling. Net-new v3.0 construct; no v2.3 antecedent.

### Changed
- `SYSTEM_PARAMS_v3.0.md`: Added `DTE_DECAY_WARNING_THRESHOLD = 21 calendar days`, consumed by PORTFOLIO_MGMT. Updated Workflow integration section to reference PORTFOLIO_MGMT. Updated Operational heuristics to name PORTFOLIO_MGMT as a behavioral owner. Updated `file_last_updated` to 2026-05-12.

## [3.0.0-session8] — 2026-05-11

### Added
- `llm_runtime/SYSTEM_PARAMS_v3.0.md` (T3): new single-source-of-truth reference for all operator-configurable trading parameters. Parameters owned: SWING_DTE_BAND (60–120 days), CSP_DTE_BAND (45–60 days), LEAP_DTE_BAND (12–24 months), IV_HV_ELEVATED_THRESHOLD (1.20), IV_RANK_EXTREME_FLOOR (75), NEAR_FLIP_BAND_PCT (0.25%).
- `llm_runtime/PASS2_VALIDATION_v3.0.md` (T2): full Pass 2 validation runbook replacing scaffold. Owns: seven-step validation workflow, chain quality classification (Full/Limited/Weak), spread-mandate three-outcome resolution, strike and expiration selection, PIPELINE_012 chain truncation behavioral contract, regime drift handling, Validated/Flagged/Rejected output states.

### Changed
- `llm_runtime/PASS1_SCREENING_v3.0.md`: hardcoded DTE literals replaced with SYSTEM_PARAMS parameter name references.
- `llm_runtime/SIGNAL_v3.0.md`: hardcoded DTE label strings replaced with SYSTEM_PARAMS parameter name references.
- `llm_runtime/VOLATILITY_v3.0.md`: SYSTEM_PARAMS pointer sentence added to IV/HV ratio bands Appendix table.
- `llm_runtime/DEALER_v3.0.md`: SYSTEM_PARAMS pointer sentence added to near-flip zone Appendix table.

### Fixed
- SWING_DTE_BAND corrected from 45–60 days (v3.0 authoring error) to 60–120 days per actual operator practice.
- CSP_DTE_BAND explicitly separated from SWING_DTE_BAND; confirmed at 45–60 days.

### Legacy anchors resolved
- PIPELINE_012 → PASS2_VALIDATION_v3.0.md § Legacy anchors
- VALIDATION_001 (PASS2 residue) → PASS2_VALIDATION_v3.0.md § Legacy anchors
- PIPELINE_011 (mis-filing) → confirmed PASS1-owned; mis-filing note in PASS2 Legacy anchors

## [3.0.0-alpha] — 2026-05-11

### Added
- `llm_runtime/PASS1_SCREENING_v3.0.md` (status: draft) — Pass 1 screening
  runbook (T2). Operationalizes the six-step eligible-set determination
  workflow, inline-sequential propose-confirm for multi-ticker runs, Pass 1
  IV source discipline (Polygon avg_iv), candidate zone format, and the
  Pass 1 / Pass 2 data-boundary rule (PIPELINE_011 compaction guard).
  Legacy anchors: PIPELINE_010 → engineering_only; PIPELINE_011 → this file;
  SCORING_001 → engineering_only.

## [3.0.0-alpha] — 2026-05-11

### Added
- `llm_runtime/WYCKOFF_v3.0.md` — Wyckoff phase and event principle file.
  Session 6 of 15 in the v3.0 rewrite cycle. Owns the propose-confirm
  protocol, four-phase vocabulary (Accumulation/Markup/Distribution/Markdown),
  named-event reading guide, structural levels, and session-scope UNKNOWN
  state. Maps all 26 legacy anchors (WYCKOFF_PHASE_001-013,
  WYCKOFF_EVENT_001-013). Four anchors deferred to forthcoming
  engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md
  (PHASE_007, PHASE_009, PHASE_013, EVENT_012).

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
