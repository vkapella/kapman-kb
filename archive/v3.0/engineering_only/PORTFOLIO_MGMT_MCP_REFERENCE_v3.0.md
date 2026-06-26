---
system: KapMan
doc_type: reference
kb_version: 3.0.0-alpha
file_last_updated: 2026-05-13
status: draft
tier: —
---

# PORTFOLIO MGMT MCP REFERENCE

## Purpose

This file documents the portfolio-management MCP and persistence mechanics named by `llm_runtime/PORTFOLIO_MGMT_v3.0.md`. The runtime PORTFOLIO_MGMT file owns position lifecycle behavior, regime monitoring, advisory state, and portfolio-mode workflow; this file owns endpoint names, parameter shapes, and position-persistence implementation details once those mechanics are specified.

## Contents

### MCP endpoint and parameter surface

| Item | Extracted value |
|---|---|
| Portfolio MCP endpoint names | [CONTENT GAP — operator input required] Source workflow assigns MCP endpoint names to this file but provides no endpoint names. |
| Portfolio MCP parameter shapes | [CONTENT GAP — operator input required] Source workflow assigns parameter shapes to this file but provides no schemas. |

### Position-persistence implementation

| Item | Extracted value |
|---|---|
| Position-persistence implementation details | [CONTENT GAP — operator input required] Source workflow assigns persistence implementation details to this file but provides no backend path, schema, or storage contract. |
| Position context schema | Runtime-owned schema is documented in `llm_runtime/PORTFOLIO_MGMT_v3.0.md` Appendix; no backend persistence implementation is provided in the source anchors. |

### Extracted operational parameter cross-reference

| Parameter | Extracted value |
|---|---|
| `DTE_DECAY_WARNING_THRESHOLD` | Consumed from `SYSTEM_PARAMS_v3.0.md`; no numeric value is owned by this file. |

## Legacy anchors

No legacy rule IDs map to this file. `PORTFOLIO_MGMT_v3.0.md` is a net-new v3.0 construct with no v2.3 antecedent.

## Appendix

### Sparse-source gap register

| Area | Gap |
|---|---|
| Endpoint names | [CONTENT GAP — operator input required] |
| Parameter shapes | [CONTENT GAP — operator input required] |
| Position-persistence backend path | [CONTENT GAP — operator input required] |
| Position-persistence schema | [CONTENT GAP — operator input required] |
| Position-persistence storage contract | [CONTENT GAP — operator input required] |
