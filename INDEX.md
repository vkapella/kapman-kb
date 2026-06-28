# KapMan KB Index

## Repository structure

This repository separates runtime and engineering materials:
- llm_runtime/ files are uploaded to LLM project knowledge.
- engineering_only/ files are reference material for humans and engineering tools and are not uploaded to LLM projects.
- archive/ stores historical version snapshots and is read-only.

## Version status

- **Active line: v4.0 (in progress).** Opened 2026-06-26 per the KapMan System
  Integration Plan v1.0 (`docs/Kapman_System_Integration_Plan_v1.0.md`),
  Stage 1a. The substantive v4.0 content — new `JOURNAL_MGMT` runbook, WYCKOFF
  live-source tier gate, the §A1–A3 field contracts, the 4th (Calibration/Review)
  mode, and the memory/no-persist guardrail — is authored in **Stage 1b
  (human-in-the-loop)** and is not yet present. Until each runtime file is
  rewritten to v4.0 content, the live `llm_runtime/`+`engineering_only/` files
  remain at their `_v3.0` filenames and `kb_version` (filename bumps are coupled
  to the substantive per-file rewrites, not to this cutover).
- **Archived: v3.0** — frozen read-only snapshot at `archive/v3.0/`
  (`llm_runtime/` + `engineering_only/` split preserved), with a `v3.0` git tag
  at the cutover commit. The v3.0 inventory and v2.3→v3.0 migration tables below
  remain authoritative for both the archived snapshot and the still-live `_v3.0`
  working files.
- **v4.0 files authored so far (Stage 1b, in progress):**
  - `llm_runtime/JOURNAL_MGMT_v4.0.md` — new T2 runbook (journal persistence: memory
    load, lineage derivation, three-log write, no-persist boundary; `positions.md` record
    grammar added in #75; §A1 lineage degradation in #76). `kb_version 4.0.2`.
  - Substantive v4.0 content has also been added to `llm_runtime/KAPMAN_GUARDRAILS_v3.0.md`
    (memory-not-authority + numeric-no-persist guardrail; `kb_version 3.0.3`). It keeps its
    `_v3.0` filename pending the coordinated `_v3.0 → _v4.0` rename + cross-reference sweep
    at the end of Stage 1. New v4.0-era content uses **version-less cross-references**.
  - **Workflow 1 (viewer → Pass 1) ingest** (Stage 1b, Integration Plan §6/§A1/§A5):
    `WYCKOFF_v3.0.md` (`kb_version 3.0.4`) repoints the pipeline-reading source from the
    now-excised `kapman-mcp` surface to the live viewer/v2 (Polygon) source and adds the
    confidence **tier gate** (`τ_high`/`τ_low` on `min(regime_confidence, phase_confidence)`);
    `PASS1_SCREENING_v3.0.md` (`kb_version 3.0.6`) adds the viewer/v2 handoff candidate source
    and the §A1 ingest map (dual-path: paste now, tool later), preserving the Pass 1 → Pass 2
    Schwab-re-fetch boundary; `SYSTEM_PARAMS_v3.0.md` (`kb_version 3.0.2`) adds the provisional
    `TIER_GATE_TAU_HIGH` / `TIER_GATE_TAU_LOW` parameters. The `kapman-mcp` tool surface and
    name are fully excised from `llm_runtime/`. Files keep their `_v3.0` filenames pending the
    end-of-Stage-1 rename.
  - **Workflow 2 (trade log → Portfolio) §A2 ingest** (Stage 1b, Integration Plan §7/§A2/§A5):
    `PORTFOLIO_MGMT_v3.0.md` (`kb_version 3.0.2`) adds the tradelog `portfolio_snapshot` §A2 ingest
    (Step 1 → 1a ingest / 1b entry-context read), the Appendix §A2 source map, structure/direction
    derivation, MAE/MFE as advisory display only, re-points the position-context schema Source column
    (live fields → tradelog snapshot; the 6 entry-time regime + 8 SIGNAL alert rows → `positions.md`),
    and the absent/partial entry-context degradation; `PASS2_VALIDATION_v3.0.md` (`kb_version 3.0.1`)
    adds the at-validation capture of the entry-time snapshot + the eight SIGNAL levels + `option_mid`
    into `positions.md` (write-once, sole no-persist exemption). Join key `(instrument_key, account_id)`.
    `docs/Kapman_System_Integration_Plan_v1.0.md` §A2/§7 corrected to the real per-leg export fields
    (MAE/MFE = compute-on-export from `HistoricalMark`, advisory). Files keep their `_v3.0` filenames
    pending the end-of-Stage-1 rename.
  - **Session-layer wiring (KPSI)** (Stage 1b, Integration Plan §10/§A5): `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md`
    (`kb_version 3.0.3 → 3.0.4`) adds `JOURNAL_MGMT_v4.0.md` to the KB file inventory + tier model, expands the
    session entry sequence from five to seven steps (new step 2 session-start memory load + announce; new step 4
    lineage derivation + handoff staging on paste), reconciles position-context load with the §A2 export +
    `positions.md`, extends **Rule 7** with the log-manifest check, and reserves a 4th (Calibration/Review) mode
    for Stage 3 (not active — no-dangling-capability). Closes the session-wiring blockers the Stage-1 pilot
    dry-run surfaced (the §A1/§A2 ingest logic + `(instrument_key, account_id)` bridge themselves validated).
    File keeps its `_v3.0` filename pending the end-of-Stage-1 rename.
  - **§A2/journal contract-hardening** (Stage 1b, Integration Plan §A2; pilot-surfaced):
    `PORTFOLIO_MGMT_v3.0.md` (`kb_version 3.0.2 → 3.0.3`) adds §A2 structure/direction derivation
    rules (debit/credit by summed `cost_basis` sign; LEAP by original DTE ≥ `LEAP_DTE_BAND` floor;
    standalone `short_put` → CSP) and a matched-but-partial entry-context condition (per-field regime /
    per-alert SIGNAL degradation) plus the `option_mid`-vs-`entry_price` distinction; `JOURNAL_MGMT_v4.0.md`
    (`kb_version 4.0.0 → 4.0.1`) adds a canonical `positions.md` record grammar (named
    `(instrument_key, account_id)` join key, write-once entry snapshot vs live-refresh split, Wyckoff field
    constrained to the four named phases) and aligns the live-field label to `net_qty`. Files keep their
    existing filenames.
  - **§A1 ingest hardening** (Stage 1b, Integration Plan §A1; pilot-surfaced): `PASS1_SCREENING_v3.0.md`
    (`kb_version 3.0.6 → 3.0.7`) rewords the dangling dealer/vol cross-check map note to informational (already
    priced into `regime_confidence`) and adds a §A1 required-field contract + per-field degradation
    (`exported_at`/`as_of`/`row_count`/force-flags; earnings clarified KB-side, not a handoff field);
    `WYCKOFF_v3.0.md` (`kb_version 3.0.4 → 3.0.5`) adds a force-flag-input-completeness rule — an absent
    `weekly_agrees`/`structure_conflict` downgrades a would-be `pipeline-accepted` reading to `pipeline-flagged`
    ("force-flags unevaluated") rather than silently auto-accepting; `JOURNAL_MGMT_v4.0.md`
    (`kb_version 4.0.1 → 4.0.2`) adds the missing-`exported_at` lineage degradation. The Integration Plan §A1
    mirrors the cross-check rewording. Files keep their existing filenames.
  - **§12 PASS2 hygiene** (Stage 1b, Integration Plan §12): `PASS2_VALIDATION_v3.0.md` (`kb_version 3.0.1 → 3.0.2`)
    adds a heuristic that viewer/v2 outputs (`pt_*`/calibration, IV/flip, dealer reads) are Pass-1 context, not
    Pass-2 truth — Pass 2 re-derives the entry-price range, exit anchors, IV/flip, and chain-quality from the live
    Schwab chain it fetches itself. The §12 "align chain-quality gate" item resolved to a no-op (the viewer emits
    no `volatility_chain_truncated` flag — audited 2026-06-27). File keeps its `_v3.0` filename.
  - **§A1 Wyckoff-vocabulary reconciliation** (Stage 1b, Integration Plan §A1; pilot-found, IN PROGRESS): aligns the
    KB §A1 layer to the viewer's canonical regime(7)/phase(A–E)/event(~27) glossary (operator-supplied 2026-06-27).
    Design D1–D4 approved (two-axis regime+phase model; lowercase event vocab). **P1 done** — `WYCKOFF_v3.0.md`
    (`kb_version 3.0.5 → 3.0.6`) re-keys the `weekly_agrees`/`structure_conflict` hard force-flags from boolean to the
    real string value `"conflict"` (they previously could never fire against live data). **P2 + P3 done** (Stage B,
    WYCKOFF core) — `WYCKOFF_v3.0.md` (`kb_version 3.0.6 → 3.0.7`) embeds the viewer/v2 glossary **verbatim** as the
    canonical regime(7)/phase(A–E)/event(~27) vocabulary (Appendix), replaces the four-phase cycle with a regime
    decision-layer + succession **graph** (`reaccumulation`/`redistribution` as continuation branches), re-keys the
    Principle, validity gate, event-to-regime priority table, event reading guide, structural levels, and
    propose-confirm examples to the lowercase vocabulary (`AR_TOP`→`ar_dist`), and marks the legacy anchors historical
    (preserved verbatim). **P4** (dealer/flip vocab) and the **consumer files** (SIGNAL/RISK/PORTFOLIO/PASS1/PASS2/
    JOURNAL/GUARDRAILS, Stages C–E) remain pending under #78.

## v3.0 file directory

| path | tier | doc_type | role |
|---|---|---|---|
| llm_runtime/KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md | T0 | orientation | Top-level project system instructions |
| llm_runtime/KAPMAN_GUARDRAILS_v3.0.md | T0 | principle | Guardrail principles |
| llm_runtime/WYCKOFF_v3.0.md | T1 | principle | Wyckoff domain principles |
| llm_runtime/DEALER_v3.0.md | T1 | principle | Dealer positioning principles |
| llm_runtime/VOLATILITY_v3.0.md | T1 | principle | Volatility regime principles |
| llm_runtime/RISK_v3.0.md | T1 | principle | Risk management principles |
| llm_runtime/SIGNAL_v3.0.md | T1 | principle | Signal entry/exit principles |
| llm_runtime/PASS1_SCREENING_v3.0.md | T2 | runbook | Pass 1 screening workflow |
| llm_runtime/PASS2_VALIDATION_v3.0.md | T2 | runbook | Pass 2 validation workflow |
| llm_runtime/PORTFOLIO_MGMT_v3.0.md | T2 | runbook | Portfolio management workflow |
| llm_runtime/REPORT_STYLE_v3.0.md | T3 | style | Report style guidance |
| llm_runtime/REPORT_TEMPLATE_PASS1_v3.0.html | T3 | template | Canonical HTML skeleton for Pass 1 screening report; column structure, section order, legend/footer pre-built per REPORT_FORMAT and REPORT_STYLE; consumed by Runtime Rule 6 at render time |
| llm_runtime/REPORT_FORMAT_v3.0.md | T3 | format | Report format guidance |
| llm_runtime/SIC_SECTOR_MAP_v3.0.md | T3 | reference | SIC to sector map reference |
| llm_runtime/SYSTEM_PARAMS_v3.0.md | T3 | reference | Operator-configurable parameter reference; includes `DTE_DECAY_WARNING_THRESHOLD` (21 days) |
| engineering_only/BACKEND_PIPELINE_v3.0.md | T4 | reference | Backend pipeline reference |
| engineering_only/TOOL_SURFACE_v3.0.md | T4 | reference | Tool-surface reference |
| engineering_only/DEALER_PIPELINE_v3.0.md | — | reference | Dealer pipeline formulas and parameters |
| engineering_only/PASS1_MCP_REFERENCE_v3.0.md | — | reference | Pass 1 MCP endpoint and scoring reference |
| engineering_only/PASS2_MCP_REFERENCE_v3.0.md | — | reference | Pass 2 MCP chain-validation reference |
| engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | — | reference | SIGNAL persistence and fallback reference |
| engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | — | reference | Volatility MCP formulas and source-authority reference |
| engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | — | reference | Wyckoff MCP detection and scoring reference |
| engineering_only/PORTFOLIO_MGMT_MCP_REFERENCE_v3.0.md | — | reference | Portfolio-management MCP and persistence reference |

### Current file inventory table

| File | Tier | Status | Session |
|---|---|---|---|
| `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md` | T0 | active | 12 |
| `REPORT_STYLE_v3.0.md` | T3 | active | 11 |
| `SIC_SECTOR_MAP_v3.0.md` | T3 | active | 13 |
| `engineering_only/DEALER_PIPELINE_v3.0.md` | — | draft | 15 |
| `engineering_only/PASS1_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/PASS2_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/PORTFOLIO_MGMT_MCP_REFERENCE_v3.0.md` | — | draft | 15 |

### v3.0.1 patch file version/status

| File | kb_version | status |
|---|---|---|
| SYSTEM_PARAMS_v3.0.md | 3.0.2 | active |
| SIGNAL_v3.0.md | 3.0.2 | active |
| PASS1_SCREENING_v3.0.md | 3.0.7 | active |
| WYCKOFF_v3.0.md | 3.0.7 | active |
| PORTFOLIO_MGMT_v3.0.md | 3.0.3 | active |
| PASS2_VALIDATION_v3.0.md | 3.0.2 | active |
| KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md | 3.0.4 | active |

### v3.0.1 report metadata patch

| File | kb_version | file_last_updated |
|---|---|---|
| REPORT_TEMPLATE_PASS1_v3.0.html | 3.0.5 | 2026-05-14 |
| KAPMAN_GUARDRAILS_v3.0.md | 3.0.3 | 2026-06-26 |
| REPORT_STYLE_v3.0.md | 3.0.4 | 2026-05-31 |
| WYCKOFF_v3.0.md | 3.0.7 | 2026-06-27 |
| PASS1_SCREENING_v3.0.md | 3.0.7 | 2026-06-27 |
| PORTFOLIO_MGMT_v3.0.md | 3.0.3 | 2026-06-27 |
| PASS2_VALIDATION_v3.0.md | 3.0.2 | 2026-06-27 |
| REPORT_FORMAT_v3.0.md | 3.0.8 | 2026-05-29 |
| KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md | 3.0.4 | 2026-06-27 |

### Session 14 llm_runtime inventory verification

| File | Tier | doc_type | Status |
|---|---|---|---|
| `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md` | T0 | orientation | active |
| `KAPMAN_GUARDRAILS_v3.0.md` | T0 | principle | active |
| `DEALER_v3.0.md` | T1 | principle | active |
| `RISK_v3.0.md` | T1 | principle | active |
| `SIGNAL_v3.0.md` | T1 | principle | active |
| `VOLATILITY_v3.0.md` | T1 | principle | active |
| `WYCKOFF_v3.0.md` | T1 | principle | active |
| `PASS1_SCREENING_v3.0.md` | T2 | runbook | active |
| `PASS2_VALIDATION_v3.0.md` | T2 | runbook | active |
| `PORTFOLIO_MGMT_v3.0.md` | T2 | runbook | active |
| `REPORT_FORMAT_v3.0.md` | T3 | format | active |
| `REPORT_STYLE_v3.0.md` | T3 | style | active |
| `SYSTEM_PARAMS_v3.0.md` | T3 | reference | active |
| `SIC_SECTOR_MAP_v3.0.md` | T3 | reference | active |

## v2.3 -> v3.0 rule-ID migration table

| Legacy ID | v3.0 destination file | Anchor name | Status |
|---|---|---|---|
| WYCKOFF_PHASE_001 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — minimum history guard | WYCKOFF_PHASE_001 | MIGRATED |
| WYCKOFF_PHASE_002 | llm_runtime/WYCKOFF_v3.0.md § Principle — phase vocabulary (Accumulation) | WYCKOFF_PHASE_002 | MIGRATED |
| WYCKOFF_PHASE_003 | llm_runtime/WYCKOFF_v3.0.md § Principle — phase vocabulary (Markup) | WYCKOFF_PHASE_003 | MIGRATED |
| WYCKOFF_PHASE_004 | llm_runtime/WYCKOFF_v3.0.md § Principle — phase vocabulary (Distribution) | WYCKOFF_PHASE_004 | MIGRATED |
| WYCKOFF_PHASE_005 | llm_runtime/WYCKOFF_v3.0.md § Principle — phase vocabulary (Markdown) | WYCKOFF_PHASE_005 | MIGRATED |
| WYCKOFF_PHASE_006 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — Markdown requires SOW | WYCKOFF_PHASE_006 | MIGRATED |
| WYCKOFF_PHASE_007 | engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_PHASE_007 | MIGRATED |
| WYCKOFF_PHASE_008 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — priority order | WYCKOFF_PHASE_008 | MIGRATED |
| WYCKOFF_PHASE_009 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics; engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_PHASE_009 | MIGRATED |
| WYCKOFF_PHASE_010 | llm_runtime/WYCKOFF_v3.0.md § Principle + § Operational heuristics — UNKNOWN state | WYCKOFF_PHASE_010 | MIGRATED |
| WYCKOFF_PHASE_011 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — phase succession duration | WYCKOFF_PHASE_011 | MIGRATED |
| WYCKOFF_PHASE_012 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — SOS/SOW sequence eligibility | WYCKOFF_PHASE_012 | MIGRATED |
| WYCKOFF_PHASE_013 | engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_PHASE_013 | MIGRATED |
| WYCKOFF_EVENT_001 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — minimum history guard | WYCKOFF_EVENT_001 | MIGRATED |
| WYCKOFF_EVENT_002 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (SC) | WYCKOFF_EVENT_002 | MIGRATED |
| WYCKOFF_EVENT_003 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (SC prior trend) | WYCKOFF_EVENT_003 | MIGRATED |
| WYCKOFF_EVENT_004 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (BC) | WYCKOFF_EVENT_004 | MIGRATED |
| WYCKOFF_EVENT_005 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (BC prior trend) | WYCKOFF_EVENT_005 | MIGRATED |
| WYCKOFF_EVENT_006 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (AR) | WYCKOFF_EVENT_006 | MIGRATED |
| WYCKOFF_EVENT_007 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (AR_TOP) | WYCKOFF_EVENT_007 | MIGRATED |
| WYCKOFF_EVENT_008 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (Spring) | WYCKOFF_EVENT_008 | MIGRATED |
| WYCKOFF_EVENT_009 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (UT) | WYCKOFF_EVENT_009 | MIGRATED |
| WYCKOFF_EVENT_010 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (SOS) | WYCKOFF_EVENT_010 | MIGRATED |
| WYCKOFF_EVENT_011 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (SOW) | WYCKOFF_EVENT_011 | MIGRATED |
| WYCKOFF_EVENT_012 | engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_EVENT_012 | MIGRATED |
| WYCKOFF_EVENT_013 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — ST not delivered | WYCKOFF_EVENT_013 | MIGRATED |
| DEALER_001 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_001 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_002 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_002 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_003 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_003 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_004 | llm_runtime/DEALER_v3.0.md § Operational heuristics; engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_004 | Runtime interpretation retained in DEALER principle; pipeline computation details moved to engineering-only spec. |
| DEALER_005 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_005 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_006 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_006 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_007 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_007 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_008 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_008 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_009 | llm_runtime/DEALER_v3.0.md § Principle, § Operational heuristics, § Appendix; engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_009 | Runtime semantics retained in DEALER principle and appendix; pipeline computation details moved to engineering-only spec. |
| DEALER_010 | llm_runtime/DEALER_v3.0.md § Operational heuristics, § Appendix; engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_010 | Runtime semantics retained in DEALER principle and appendix; pipeline computation details moved to engineering-only spec. |
| DEALER_011 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_011 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_012 | llm_runtime/DEALER_v3.0.md § Operational heuristics; engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_012 | Runtime interpretation retained in DEALER principle; pipeline computation details moved to engineering-only spec. |
| DEALER_013 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_013 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_014 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_014 | Migrated to engineering-only pipeline spec (formula and computation details). |
| VOLATILITY_001 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_001 | MIGRATED |
| VOLATILITY_002 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_002 | MIGRATED |
| VOLATILITY_003 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_003 | MIGRATED |
| VOLATILITY_004 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_004 | MIGRATED |
| VOLATILITY_005 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_005 | MIGRATED |
| VOLATILITY_006 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_006 | MIGRATED |
| VOLATILITY_007 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_007 | MIGRATED |
| VOLATILITY_008 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_008 | MIGRATED |
| VOLATILITY_009 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_009 | MIGRATED |
| VOLATILITY_010 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_010 | MIGRATED |
| VOLATILITY_011 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics and Appendix; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_011 | MIGRATED |
| VOLATILITY_012 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_012 | MIGRATED |
| VOLATILITY_013 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_013 | MIGRATED |
| VOLATILITY_014 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_014 | MIGRATED |
| VOLATILITY_015 | llm_runtime/VOLATILITY_v3.0.md § Principle and Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_015 | MIGRATED |
| RISK_005 | llm_runtime/RISK_v3.0.md | RISK_005 | PENDING REWRITE |
| POSITION_SIZING_001 | RISK_v3.0.md § Principle and § Operational heuristics | Superseded by band-based judgment model; v2.3 sizing ladder preserved as reference in Appendix |
| RISK_001 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_001 | PENDING REWRITE |
| RISK_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_002 | PENDING REWRITE |
| RISK_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_003 | PENDING REWRITE |
| RISK_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_004 | PENDING REWRITE |
| SIGNAL_005 | llm_runtime/SIGNAL_v3.0.md § Operational heuristics; engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_005 | MIGRATED |
| SIGNAL_006 | llm_runtime/SIGNAL_v3.0.md § Operational heuristics; engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_006 | MIGRATED |
| SIGNAL_007 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_007 | PENDING REWRITE |
| SIGNAL_008 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_008 | PENDING REWRITE |
| SIGNAL_009 | llm_runtime/SIGNAL_v3.0.md § Operational heuristics; engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_009 | MIGRATED |
| SIGNAL_010 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_010 | PENDING REWRITE |
| SIGNAL_001 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_001 | MIGRATED |
| SIGNAL_002 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_002 | MIGRATED |
| SIGNAL_003 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_003 | MIGRATED |
| SIGNAL_004 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_004 | MIGRATED |
| VALIDATION_001 | llm_runtime/KAPMAN_GUARDRAILS_v3.0.md | VALIDATION_001 | PENDING REWRITE |
| VALIDATION_001 (PASS2 residue) | PASS2_VALIDATION_v3.0.md § Legacy anchors; engineering_only/PASS2_MCP_REFERENCE_v3.0.md | Active — anti-hallucination floor narrowing at Pass 2; persistence-boundary controls in engineering-only |
| VALIDATION_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_002 | PENDING REWRITE |
| VALIDATION_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_003 | PENDING REWRITE |
| VALIDATION_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_004 | PENDING REWRITE |
| VALIDATION_005 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_005 | PENDING REWRITE |
| VALIDATION_006 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_006 | PENDING REWRITE |
| VALIDATION_007 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_007 | PENDING REWRITE |
| VALIDATION_008 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_008 | PENDING REWRITE |
| VALIDATION_009 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_009 | PENDING REWRITE |
| VALIDATION_010 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_010 | PENDING REWRITE |
| CONSTANTS_001 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_001 | PENDING REWRITE |
| CONSTANTS_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_002 | PENDING REWRITE |
| CONSTANTS_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_003 | PENDING REWRITE |
| CONSTANTS_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_004 | PENDING REWRITE |
| CONSTANTS_005 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_005 | PENDING REWRITE |
| CONSTANTS_006 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_006 | PENDING REWRITE |
| CONSTANTS_007 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_007 | PENDING REWRITE |
| CONSTANTS_008 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_008 | PENDING REWRITE |
| CONSTANTS_009 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_009 | PENDING REWRITE |
| CONSTANTS_010 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_010 | PENDING REWRITE |
| CONSTANTS_011 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_011 | PENDING REWRITE |
| CONSTANTS_012 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_012 | PENDING REWRITE |
| CONSTANTS_013 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_013 | PENDING REWRITE |
| PIPELINE_001 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_001 | PENDING REWRITE |
| PIPELINE_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_002 | PENDING REWRITE |
| PIPELINE_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_003 | PENDING REWRITE |
| PIPELINE_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_004 | PENDING REWRITE |
| PIPELINE_005 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_005 | PENDING REWRITE |
| PIPELINE_006 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_006 | PENDING REWRITE |
| PIPELINE_007 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_007 | PENDING REWRITE |
| PIPELINE_008 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_008 | PENDING REWRITE |
| PIPELINE_009 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_009 | PENDING REWRITE |
| PIPELINE_010 | engineering_only/PASS1_MCP_REFERENCE_v3.0.md — full endpoint inventory; runtime behavioral residue in llm_runtime/PASS1_SCREENING_v3.0.md § Operational heuristics ("The Pass 1 IV source is Polygon avg_iv") | PIPELINE_010 | MIGRATED |
| PIPELINE_012 | PASS2_VALIDATION_v3.0.md § Legacy anchors; engineering_only/PASS2_MCP_REFERENCE_v3.0.md | PIPELINE_012 | MIGRATED |
| PIPELINE_011 | llm_runtime/PASS1_SCREENING_v3.0.md § Operational heuristics ("Pass 1 data does not carry forward as authoritative into Pass 2") | PIPELINE_011 | MIGRATED |
| PIPELINE_011 (mis-filing note) | PASS2_VALIDATION_v3.0.md § Legacy anchors | Mis-filing resolved; authoritative destination is PASS1 |
| SCORING_001 | engineering_only/PASS1_MCP_REFERENCE_v3.0.md — pass-through constraint and storage bounds; runtime: not referenced in any trigger evaluation | SCORING_001 | MIGRATED |

### Session 14 migration coverage verification rows

| Legacy ID | v3.0 destination file | Anchor name | Status |
|---|---|---|---|
| DEALER_001–DEALER_014 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_001–DEALER_014 | VERIFIED |
| PIPELINE_010, SCORING_001 | engineering_only/PASS1_MCP_REFERENCE_v3.0.md | PIPELINE_010, SCORING_001 | VERIFIED |
| PIPELINE_011 | REPORT_FORMAT_v3.0.md § Operational heuristics — pass label discipline | PIPELINE_011 | VERIFIED |
| PIPELINE_012 | PASS2_VALIDATION_v3.0.md § Operational heuristics — truncation heuristic; engineering_only/PASS2_MCP_REFERENCE_v3.0.md | PIPELINE_012 | VERIFIED |
| VALIDATION_001 | KAPMAN_GUARDRAILS_v3.0.md § Operational heuristics; REPORT_FORMAT_v3.0.md § Operational heuristics | VALIDATION_001 | VERIFIED |
| RISK_005 | RISK_v3.0.md § Principle and § Operational heuristics | RISK_005 | VERIFIED |
| SIGNAL_001–SIGNAL_004 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_001–SIGNAL_004 | VERIFIED |
| SIGNAL_005 | SIGNAL_v3.0.md § Operational heuristics — anti-hallucination floor; computation to engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_005 | VERIFIED |
| SIGNAL_006 | SIGNAL_v3.0.md § Operational heuristics — NO_TRADE consistency | SIGNAL_006 | VERIFIED |
| SIGNAL_009 | SIGNAL_v3.0.md § Operational heuristics — fallback policy; engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_009 | VERIFIED |
| VOLATILITY_001–VOLATILITY_015 | Per individual anchor entries in VOLATILITY_v3.0.md § Legacy anchors; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_001–VOLATILITY_015 | VERIFIED |
| WYCKOFF_PHASE_001–WYCKOFF_PHASE_013 | Per individual anchor entries in WYCKOFF_v3.0.md § Legacy anchors; engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_PHASE_001–WYCKOFF_PHASE_013 | VERIFIED |
| WYCKOFF_EVENT_002–WYCKOFF_EVENT_012 | Per individual anchor entries in WYCKOFF_v3.0.md § Legacy anchors; engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_EVENT_002–WYCKOFF_EVENT_012 | VERIFIED |

### RISK v3.0 rewrite resolution (2026-05-10)

| Legacy ID | v3.0 destination | Status | Rationale |
|---|---|---|---|
| RISK_001 | — | DROPPED | C4 pipeline null-write observation; engineering-state, no LLM runtime effect |
| RISK_002 | — | DROPPED | AI base disclaimer implementation detail; not a risk principle |
| RISK_003 | — | DROPPED | Schema check-constraint absence; backend observation only |
| RISK_004 | — | DROPPED | C4 authority_constraints injection gap; backend reference, not LLM rule |
| RISK_005 | llm_runtime/RISK_v3.0.md § Legacy anchors | MIGRATED | Sizing ladder rewritten as judgment bands; percentages preserved in Appendix as reference points |
