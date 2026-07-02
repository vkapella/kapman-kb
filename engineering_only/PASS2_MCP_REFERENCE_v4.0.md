---
system: KapMan
doc_type: reference
kb_version: 4.0.0-alpha
file_last_updated: 2026-07-02
status: draft
tier: —
---

# PASS2 MCP REFERENCE

## Purpose

This file documents the Pass 2 MCP and chain-fetch mechanics extracted from `llm_runtime/PASS2_VALIDATION_v4.0.md`. The runtime PASS2 file owns validation behavior and output-state consequences; this file owns endpoint names, parameter shapes, chain-quality thresholds, truncation detection, strike-count reduction mechanics, and persistence-boundary controls.

## Contents

### MCP endpoint and parameter surface

| Item | Extracted value |
|---|---|
| Schwab option-chain endpoint name | [CONTENT GAP — operator input required] Source text names the Schwab chain endpoint conceptually but does not provide the endpoint name. |
| Chain-fetch parameter shapes | [CONTENT GAP — operator input required] Source text says parameter shapes belong here but does not provide the schema. |
| `strike_count` parameter | Present; reduced when truncation is suspected |
| Numeric `strike_count` reduction parameters | [CONTENT GAP — operator input required] Source text assigns these to this file but does not provide numeric values. |
| Targeted-expiry split mechanics | Split fetch by targeted expiration rather than fetching the full zone in one call |
| Exact targeted-expiry parameter mechanics | [CONTENT GAP — operator input required] Source text names the mechanic but does not provide exact parameter syntax. |

### Chain truncation detection

| Truncation signal | Extracted value |
|---|---|
| Contract-count symptom | Fewer contracts than expected for the requested zone and DTE band |
| Strike-coverage symptom | Missing far strikes within the zone |
| Expiration-coverage symptom | Incomplete expiration coverage within the DTE band |
| Required response | Reduce `strike_count` and re-fetch, or split the fetch by targeted expiration |
| Full-chain prohibition | A chain that has not been confirmed complete cannot be classified Full |

### Chain-quality numeric thresholds

| Item | Extracted value |
|---|---|
| Contract count floors | [CONTENT GAP — operator input required] Source text says these thresholds belong here but does not provide values. |
| Bid/ask spread limits | [CONTENT GAP — operator input required] Source text says these thresholds belong here but does not provide values. |
| OI floors per contract | [CONTENT GAP — operator input required] Source text says these thresholds belong here but does not provide values. |

### Persistence-boundary controls

| Item | Extracted value |
|---|---|
| PASS2 anti-hallucination persistence control | `VALIDATION_007`: hardcoded null assignment for `option_strike` and `option_expiration` in C4 recommendation rows |
| Scope | Tool-surface-internal control with no LLM runtime effect |

## Legacy anchors

- `PIPELINE_012` → Contents / Chain truncation detection and MCP endpoint surface.
- `VALIDATION_001 (PASS2 residue)` → Contents / Persistence-boundary controls for the PASS2-specific anti-hallucination tail.

## Appendix

### Verbatim extracted mechanics and parameters

| Source anchor | Extract |
|---|---|
| `PIPELINE_012` | Reduce the `strike_count` parameter and re-fetch, or split the fetch by targeted expiration rather than fetching the full zone in one call. |
| `PIPELINE_012` | Truncation signal: fewer contracts than expected for the requested zone and DTE band, missing far strikes within the zone, or incomplete expiration coverage within the DTE band. |
| `PIPELINE_012` | A chain that has not been confirmed complete cannot be classified Full. |
| `VALIDATION_001 (PASS2 residue)` | `VALIDATION_007`: hardcoded null assignment for `option_strike` and `option_expiration` in C4 recommendation rows. |
