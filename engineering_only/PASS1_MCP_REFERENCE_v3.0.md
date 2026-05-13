---
system: KapMan
doc_type: reference
kb_version: 3.0.0-alpha
file_last_updated: 2026-05-13
status: draft
tier: —
---

# PASS1 MCP REFERENCE

## Purpose

This file documents the Pass 1 MCP tool-surface mechanics extracted from `llm_runtime/PASS1_SCREENING_v3.0.md`. The runtime PASS1 file owns eligible-set behavior and screening flow; this file owns endpoint names, batch caps, parameter shapes, deprecated endpoint prohibitions, scoring pass-through bounds, and other mechanical references.

## Contents

### Polygon MCP endpoint routing

| Item | Extracted value |
|---|---|
| Single-symbol canonical endpoint | `get_options_metrics` |
| Batch canonical endpoint | `get_batch_options_metrics` |
| Volatility include flag | `include=['volatility']` |
| Batch cap | `30` symbols per call |
| Deprecated endpoints that must never be called | [CONTENT GAP — operator input required] Source anchor says the full inventory exists but does not list the deprecated endpoint names. |
| Full endpoint parameter shapes | [CONTENT GAP — operator input required] Source anchor names `include=['volatility']` but does not provide the complete parameter schema. |

### Scoring pass-through

| Item | Extracted value |
|---|---|
| BC Score | Pass-through context value only; no formula computation occurs in the active pipeline |
| Spring Score | Pass-through context value only; no formula computation occurs in the active pipeline |
| Composite Score | Pass-through context value only; no entry should be blocked or approved based solely on Composite Score until a formula and threshold are formally implemented |
| BC Score storage bound | `0–28` |
| Spring Score storage bound | `0–12` |
| Composite Score storage bound | [CONTENT GAP — operator input required] Source anchor names Composite Score but does not provide a storage bound. |
| Payload reference | `c4_batch_ai_screening_job.py` payload |

### Fallback confidence reference values

| Item | Extracted value |
|---|---|
| Primary NO_TRADE, Wyckoff-veto cause | `75` |
| Primary NO_TRADE, other cause | `60` |
| WAIT alternative | `primary - 20` |
| Long-premium ENTER alternative when `iv_forbids_long_premium` is the cause | `primary - 30` |

### Context compaction observation

| Item | Extracted value |
|---|---|
| Platform-behavior observation | Claude Sonnet 4.6 / Opus 4.6 context compaction active in beta as of 2026-03 |
| Runtime residue | Pass 2 must re-fetch Schwab dealer metrics live and must not reuse Pass 1 numeric regime values from conversation history. |

## Legacy anchors

- `PIPELINE_010` → Contents / Polygon MCP endpoint routing.
- `SCORING_001` → Contents / Scoring pass-through.
- `SIGNAL_009` reference values → Contents / Fallback confidence reference values. Canonical SIGNAL persistence mechanics are also documented in `engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md`.
- `PIPELINE_011` platform observation → Contents / Context compaction observation. Runtime behavior remains in `llm_runtime/PASS1_SCREENING_v3.0.md`.

## Appendix

### Verbatim extracted endpoint and parameter values

| Source anchor | Extract |
|---|---|
| `PIPELINE_010` | `get_options_metrics`, `get_batch_options_metrics` with `include=['volatility']` |
| `PIPELINE_010` | Batch cap of `30` symbols per call |
| `SCORING_001` | BC Score `0–28`, Spring Score `0–12` |
| `SIGNAL_009` reference values | Base `75/60`, deltas `−20/−30` |
| `PIPELINE_011` observation | Claude Sonnet 4.6 / Opus 4.6 context compaction active in beta as of 2026-03 |
