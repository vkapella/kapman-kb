---
system: KapMan
doc_type: reference
kb_version: 3.0.0-alpha
file_last_updated: 2026-05-11
status: draft
tier: T3
---

# SYSTEM_PARAMS

## Principle

System parameters are the operator-configurable numeric and band values that trading logic files reference by name rather than by hardcoded value. Every parameter here has exactly one authoritative definition — this file — and zero authoritative definitions anywhere else in `llm_runtime/`. When a parameter value changes, this file changes and no other runtime file changes. Runtime files that consume a parameter name its source explicitly ("per SYSTEM_PARAMS") so the dependency is visible and the update surface is bounded.

Parameters in this file are trading-logic inputs, not tool-surface or pipeline parameters. Tool-surface numeric defaults (chain filter thresholds, batch caps, endpoint-specific field bounds) belong in the relevant `engineering_only/` reference file. Pipeline computation constants (z-score thresholds, sequence windows, DGPI formula clamps) belong in `engineering_only/` as well. This file owns only the parameters that the LLM runtime consumes directly when making structure, sizing, or expiration decisions.

## Operational heuristics

**Parameters are consumed by name, not by value.**
Runtime files reference parameters as named quantities — "the swing DTE band per SYSTEM_PARAMS," "the IV/HV elevated threshold per SYSTEM_PARAMS" — rather than embedding the numeric value in prose or table cells. This is what makes the parameter table below the single update point. A runtime file that embeds the numeric value directly is a fragility that this file exists to prevent.

**Parameter changes require a KB version bump and a CHANGELOG entry.**
A parameter value change is a substantive content change, not a mechanical patch. It requires operator review in a Claude.ai session, a CHANGELOG entry noting the old and new value and the rationale, and a `kb_version` bump in this file's frontmatter. No parameter value is changed autonomously by a code agent.

**Parameters have behavioral owners — this file has none.**
SYSTEM_PARAMS defines values. It does not define what to do with them. The behavioral consequence of each parameter lives in the file that consumes it: DTE band enforcement belongs to PASS1 and PASS2; IV/HV threshold enforcement belongs to VOLATILITY and SIGNAL; near-flip band enforcement belongs to DEALER and GUARDRAILS. When a parameter's behavioral consequence and its numeric value appear to conflict, the consuming file's behavioral contract governs and the discrepancy is flagged for operator review.

## Parameter table

| Parameter name | Current value | Unit | Consuming files | Notes |
|---|---|---|---|---|
| `SWING_DTE_BAND` | 60–120 | calendar days | PASS1, PASS2, SIGNAL | Applies to standard directional swing trades (long calls, long puts, debit spreads). Lower bound is the minimum acceptable DTE at entry; upper bound is the maximum. |
| `CSP_DTE_BAND` | 45–60 | calendar days | PASS1, PASS2 | Applies to cash-secured puts. Shorter than the swing band — CSPs target premium decay in the 45–60 DTE window where theta accelerates most efficiently. Listed separately from `SWING_DTE_BAND` so it can be tuned independently. |
| `LEAP_DTE_BAND` | 12–24 | months | PASS1, PASS2 | Applies to LEAP long calls. Expressed in months because LEAPS expirations are sparsely listed and month-level granularity is the practical selection unit. |
| `IV_HV_ELEVATED_THRESHOLD` | 1.20 | ratio (IV ÷ HV) | VOLATILITY, SIGNAL | The IV/HV ratio at or above which the spread-mandate fires for new directional entries. Boundary value resolves to elevated (conservative) per VOLATILITY heuristics. |
| `IV_RANK_EXTREME_FLOOR` | 75 | IV rank score [0–100] | VOLATILITY, SIGNAL | The IV rank score at or above which the extreme tier activates, reinforcing the spread-mandate even when IV/HV reads neutral. |
| `NEAR_FLIP_BAND_PCT` | 0.25 | percent of spot (±) | DEALER, GUARDRAILS | The symmetric percentage band around the gamma flip level that defines the near-flip zone. Applies identically to SPY (macro layer) and per-ticker. |

## Workflow integration

This file is consumed by:

- `PASS1_SCREENING_v3.0.md` — reads `SWING_DTE_BAND`, `CSP_DTE_BAND`, `LEAP_DTE_BAND` for candidate zone DTE band assembly
- `PASS2_VALIDATION_v3.0.md` — reads the same DTE bands for expiration selection scope; reads `IV_HV_ELEVATED_THRESHOLD` and `IV_RANK_EXTREME_FLOOR` as spread-mandate resolution inputs
- `SIGNAL_v3.0.md` — reads `IV_HV_ELEVATED_THRESHOLD` and `IV_RANK_EXTREME_FLOOR` for spread-mandate trigger specification; reads `SWING_DTE_BAND` and `CSP_DTE_BAND` for anti-hallucination label text
- `VOLATILITY_v3.0.md` — reads `IV_HV_ELEVATED_THRESHOLD` and `IV_RANK_EXTREME_FLOOR` as the Appendix band boundary values
- `DEALER_v3.0.md` — reads `NEAR_FLIP_BAND_PCT` as the near-flip zone Appendix band value

This file does not consume any other runtime file. It has no upstream dependencies within `llm_runtime/`.

## Legacy anchors (for legend citations and back-compat)

No legacy rule IDs map to this file. SYSTEM_PARAMS is a new v3.0 construct with no v2.3 antecedent. The parameter values it owns were previously hardcoded across multiple runtime files; their v2.3 source locations are documented in the consuming files' legacy anchor sections and in `engineering_only/` references.

## Appendix — parameter change log

Changes to individual parameter values are recorded here in addition to the top-level `CHANGELOG.md` entry, so the history of each parameter is visible without reading the full changelog.

| Date | Parameter | Old value | New value | Rationale |
|---|---|---|---|---|
| 2026-05-11 | `SWING_DTE_BAND` | 45–60 days (hardcoded in PASS1, SIGNAL) | 60–120 days | Corrects a v3.0 authoring error; 45–60 DTE was carried from a v2.3 scaffold without operator validation and conflicts with actual operator practice of 60–120 DTE for swing trades |
| 2026-05-11 | `CSP_DTE_BAND` | 45–60 days (implied, same hardcode as swing) | 45–60 days | Value is correct; CSP band is now explicitly separated from swing band and defined independently in SYSTEM_PARAMS rather than implied by the swing band default |
