# KapMan KB Index

## Repository structure

This repository separates runtime and engineering materials:
- llm_runtime/ files are uploaded to LLM project knowledge.
- engineering_only/ files are reference material for humans and engineering tools and are not uploaded to LLM projects.
- archive/ stores historical version snapshots and is read-only.

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
| llm_runtime/PASS2_VALIDATION_v3.0.md | T2 | PASS2 validation runbook | Session 8 | Active |
| llm_runtime/PORTFOLIO_MGMT_v3.0.md | T2 | runbook | Portfolio management workflow | Session 9 | Draft |
| llm_runtime/REPORT_STYLE_v3.0.md | T3 | style | Report style guidance | Session 11 | Draft | Direct successor to `KAPMAN_REPORT_STYLE_GLOSSARY_v2.3.md` (full migration) |
| llm_runtime/REPORT_TEMPLATE_PASS1_v3.0.html | T3 | template | Canonical HTML skeleton for Pass 1 screening report; column structure, section order, legend/footer pre-built per REPORT_FORMAT and REPORT_STYLE; consumed by Runtime Rule 6 at render time | Session 16 | Active |
| llm_runtime/REPORT_FORMAT_v3.0.md | T3 | style | Report format guidance | Session 10 | Draft |
| llm_runtime/SIC_SECTOR_MAP_v3.0.md | T3 | reference | SIC to sector map reference |
| llm_runtime/SYSTEM_PARAMS_v3.0.md | T3 | Operator-configurable parameter reference; includes `DTE_DECAY_WARNING_THRESHOLD` (21 days) | Session 9 | Active |
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
| SYSTEM_PARAMS_v3.0.md | 3.0.1 | active |
| SIGNAL_v3.0.md | 3.0.1 | active |
| PASS1_SCREENING_v3.0.md | 3.0.1 | active |
| WYCKOFF_v3.0.md | 3.0.2 | active |

### v3.0.1 report metadata patch

| File | kb_version | file_last_updated |
|---|---|---|
| REPORT_FORMAT_v3.0.md | 3.0.3 | 2026-05-13 |
| KAPMAN_GUARDRAILS_v3.0.md | 3.0.1 | 2026-05-13 |
| REPORT_STYLE_v3.0.md | 3.0.1 | 2026-05-13 |
| WYCKOFF_v3.0.md | 3.0.2 | 2026-05-14 |
| PASS1_SCREENING_v3.0.md | 3.0.1 | 2026-05-13 |

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
