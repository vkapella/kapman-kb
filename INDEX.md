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
| llm_runtime/PASS2_VALIDATION_v3.0.md | T2 | runbook | Pass 2 validation workflow |
| llm_runtime/PORTFOLIO_MGMT_v3.0.md | T2 | runbook | Portfolio management workflow |
| llm_runtime/REPORT_STYLE_v3.0.md | T3 | style | Report style guidance |
| llm_runtime/REPORT_FORMAT_v3.0.md | T3 | style | Report format guidance |
| llm_runtime/SIC_SECTOR_MAP_v3.0.md | T3 | reference | SIC to sector map reference |
| engineering_only/BACKEND_PIPELINE_v3.0.md | T4 | reference | Backend pipeline reference |
| engineering_only/TOOL_SURFACE_v3.0.md | T4 | reference | Tool-surface reference |

## v2.3 -> v3.0 rule-ID migration table

| Legacy ID | v3.0 destination file | Anchor name | Status |
|---|---|---|---|
| WYCKOFF_PHASE_001 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_001 | PENDING REWRITE |
| WYCKOFF_PHASE_002 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_002 | PENDING REWRITE |
| WYCKOFF_PHASE_003 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_003 | PENDING REWRITE |
| WYCKOFF_PHASE_004 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_004 | PENDING REWRITE |
| WYCKOFF_PHASE_005 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_005 | PENDING REWRITE |
| WYCKOFF_PHASE_006 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_006 | PENDING REWRITE |
| WYCKOFF_PHASE_007 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_007 | PENDING REWRITE |
| WYCKOFF_PHASE_008 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_008 | PENDING REWRITE |
| WYCKOFF_PHASE_009 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_009 | PENDING REWRITE |
| WYCKOFF_PHASE_010 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_010 | PENDING REWRITE |
| WYCKOFF_PHASE_011 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_011 | PENDING REWRITE |
| WYCKOFF_PHASE_012 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_012 | PENDING REWRITE |
| WYCKOFF_PHASE_013 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_PHASE_013 | PENDING REWRITE |
| WYCKOFF_EVENT_001 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_001 | PENDING REWRITE |
| WYCKOFF_EVENT_002 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_002 | PENDING REWRITE |
| WYCKOFF_EVENT_003 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_003 | PENDING REWRITE |
| WYCKOFF_EVENT_004 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_004 | PENDING REWRITE |
| WYCKOFF_EVENT_005 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_005 | PENDING REWRITE |
| WYCKOFF_EVENT_006 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_006 | PENDING REWRITE |
| WYCKOFF_EVENT_007 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_007 | PENDING REWRITE |
| WYCKOFF_EVENT_008 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_008 | PENDING REWRITE |
| WYCKOFF_EVENT_009 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_009 | PENDING REWRITE |
| WYCKOFF_EVENT_010 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_010 | PENDING REWRITE |
| WYCKOFF_EVENT_011 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_011 | PENDING REWRITE |
| WYCKOFF_EVENT_012 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_012 | PENDING REWRITE |
| WYCKOFF_EVENT_013 | llm_runtime/WYCKOFF_v3.0.md | WYCKOFF_EVENT_013 | PENDING REWRITE |
| DEALER_001 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_001 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_002 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_002 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_003 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_003 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_004 | llm_runtime/DEALER_v3.0.md § Operational heuristics; engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_004 | Runtime interpretation retained in DEALER principle; pipeline computation details moved to engineering-only spec. |
| DEALER_005 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_005 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_006 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_006 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_007 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_007 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_008 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_008 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_009 | llm_runtime/DEALER_v3.0.md § Principle, § Operational heuristics, § Appendix; engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_009 | Runtime semantics retained in DEALER principle and appendix; pipeline computation details moved to engineering-only spec. |
| DEALER_010 | llm_runtime/DEALER_v3.0.md § Operational heuristics, § Appendix; engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_010 | Runtime semantics retained in DEALER principle and appendix; pipeline computation details moved to engineering-only spec. |
| DEALER_011 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_011 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_012 | llm_runtime/DEALER_v3.0.md § Operational heuristics; engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_012 | Runtime interpretation retained in DEALER principle; pipeline computation details moved to engineering-only spec. |
| DEALER_013 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_013 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_014 | engineering_only/DEALER_PIPELINE_v3.0.md (forthcoming) | DEALER_014 | Migrated to engineering-only pipeline spec (formula and computation details). |
| VOLATILITY_001 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_001 | PENDING REWRITE |
| VOLATILITY_002 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_002 | PENDING REWRITE |
| VOLATILITY_003 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_003 | PENDING REWRITE |
| VOLATILITY_004 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_004 | PENDING REWRITE |
| VOLATILITY_005 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_005 | PENDING REWRITE |
| VOLATILITY_006 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_006 | PENDING REWRITE |
| VOLATILITY_007 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_007 | PENDING REWRITE |
| VOLATILITY_008 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_008 | PENDING REWRITE |
| VOLATILITY_009 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_009 | PENDING REWRITE |
| VOLATILITY_010 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_010 | PENDING REWRITE |
| VOLATILITY_011 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_011 | PENDING REWRITE |
| VOLATILITY_012 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_012 | PENDING REWRITE |
| VOLATILITY_013 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_013 | PENDING REWRITE |
| VOLATILITY_014 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_014 | PENDING REWRITE |
| VOLATILITY_015 | llm_runtime/VOLATILITY_v3.0.md | VOLATILITY_015 | PENDING REWRITE |
| RISK_005 | llm_runtime/RISK_v3.0.md | RISK_005 | PENDING REWRITE |
| RISK_001 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_001 | PENDING REWRITE |
| RISK_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_002 | PENDING REWRITE |
| RISK_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_003 | PENDING REWRITE |
| RISK_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_004 | PENDING REWRITE |
| SIGNAL_005 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_005 | PENDING REWRITE |
| SIGNAL_006 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_006 | PENDING REWRITE |
| SIGNAL_007 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_007 | PENDING REWRITE |
| SIGNAL_008 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_008 | PENDING REWRITE |
| SIGNAL_009 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_009 | PENDING REWRITE |
| SIGNAL_010 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_010 | PENDING REWRITE |
| SIGNAL_001 | engineering_only/BACKEND_PIPELINE_v3.0.md | SIGNAL_001 | PENDING REWRITE |
| SIGNAL_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | SIGNAL_002 | PENDING REWRITE |
| SIGNAL_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | SIGNAL_003 | PENDING REWRITE |
| SIGNAL_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | SIGNAL_004 | PENDING REWRITE |
| VALIDATION_001 | llm_runtime/KAPMAN_GUARDRAILS_v3.0.md | VALIDATION_001 | PENDING REWRITE |
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
| PIPELINE_010 | engineering_only/TOOL_SURFACE_v3.0.md | PIPELINE_010 | PENDING REWRITE |
| PIPELINE_012 | engineering_only/TOOL_SURFACE_v3.0.md | PIPELINE_012 | PENDING REWRITE |
| PIPELINE_011 | llm_runtime/PASS2_VALIDATION_v3.0.md | PIPELINE_011 | PENDING REWRITE |
| SCORING_001 | DROPPED | N/A | DROPPED |

### RISK v3.0 rewrite resolution (2026-05-10)

| Legacy ID | v3.0 destination | Status | Rationale |
|---|---|---|---|
| RISK_001 | — | DROPPED | C4 pipeline null-write observation; engineering-state, no LLM runtime effect |
| RISK_002 | — | DROPPED | AI base disclaimer implementation detail; not a risk principle |
| RISK_003 | — | DROPPED | Schema check-constraint absence; backend observation only |
| RISK_004 | — | DROPPED | C4 authority_constraints injection gap; backend reference, not LLM rule |
| RISK_005 | llm_runtime/RISK_v3.0.md § Legacy anchors | MIGRATED | Sizing ladder rewritten as judgment bands; percentages preserved in Appendix as reference points |
