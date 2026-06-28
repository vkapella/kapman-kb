---
system: KapMan
doc_type: reference
kb_version: 3.0.4
file_last_updated: 2026-06-28
status: active
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
SYSTEM_PARAMS defines values. It does not define what to do with them. The behavioral consequence of each parameter lives in the file that consumes it: DTE band enforcement belongs to PASS1 and PASS2; IV/HV threshold enforcement belongs to VOLATILITY and SIGNAL; near-flip band enforcement belongs to DEALER and GUARDRAILS; DTE decay warning enforcement belongs to PORTFOLIO_MGMT. When a parameter's behavioral consequence and its numeric value appear to conflict, the consuming file's behavioral contract governs and the discrepancy is flagged for operator review.

## Parameter table

| Parameter name | Current value | Unit | Consuming files | Notes |
|---|---|---|---|---|
| `SWING_DTE_BAND` | 60–120 | calendar days | PASS1, PASS2, SIGNAL | Applies to standard directional swing trades (long calls, long puts, debit spreads). Lower bound is the minimum acceptable DTE at entry; upper bound is the maximum. |
| `CSP_DTE_BAND` | 45–60 | calendar days | PASS1, PASS2 | Applies to cash-secured puts. Shorter than the swing band — CSPs target premium decay in the 45–60 DTE window where theta accelerates most efficiently. Listed separately from `SWING_DTE_BAND` so it can be tuned independently. |
| `LEAP_DTE_BAND` | 12–24 | months | PASS1, PASS2 | Applies to LEAP long calls. Expressed in months because LEAPS expirations are sparsely listed and month-level granularity is the practical selection unit. |
| `IV_HV_ELEVATED_THRESHOLD` | 1.20 | ratio (IV ÷ HV) | VOLATILITY, SIGNAL | The IV/HV ratio at or above which the spread-mandate fires for new directional entries. Boundary value resolves to elevated (conservative) per VOLATILITY heuristics. |
| `IV_RANK_EXTREME_FLOOR` | 75 | IV rank score [0–100] | VOLATILITY, SIGNAL | The IV rank score at or above which the extreme tier activates, reinforcing the spread-mandate even when IV/HV reads neutral. |
| `NEAR_FLIP_BAND_PCT` | 0.5 | percent of spot (±) | DEALER, GUARDRAILS | The symmetric percentage band around the gamma flip level that defines the near-flip zone (the `at_flip` band). Applies identically to SPY (macro) and per-ticker. **Aligned to the producers' 0.5% `at_flip` band** (kapman-polygon-mcp-v2 + kapman-schwab-MCP) — was 0.25%, which disagreed with both producers. |
| `DGPI_NEUTRAL_BAND` | 10 | DGPI magnitude (\|x\|) | DEALER | Below this magnitude (`-10 < DGPI < +10`) the dealer read is **near-neutral** (the producer's "low pressure" band). Matches the producer DGPI bands (kapman-polygon-mcp-v2 `dealer_metrics.py`: <10 low / 10-30 moderate / 30-60 significant / >60 extreme) and the viewer header's go/no-go light. |
| `DGPI_STRONG_BAND` | 30 | DGPI magnitude (\|x\|) | DEALER | At/above this magnitude the tier is **strongly supportive** (≥ +30) or **hostile** (≤ -30); between `DGPI_NEUTRAL_BAND` and this is moderately-supportive / weakening. The producer's "significant" + "extreme" (>60) bands fold into the strong tier (the KB does not surface a separate 60 cutpoint). |
| `HOSTILE_MACRO_DGPI_MAX` | -30 | signed DGPI | DEALER, GUARDRAILS | SPY DGPI at/below this (combined with SPY below gamma flip) is the DGPI half of the hostile-macro composite. Set to the hostile tier (-`DGPI_STRONG_BAND`). Because DGPI is log-compressed, SPY's \|DGPI\| is almost always large, so the hostile-macro gate is **sign-dominated** in practice — this threshold mainly prevents firing on a near-neutral SPY. Independently tunable. |
| `EARNINGS_BLOCK_DAYS` | 7 | calendar days | PASS1, SIGNAL | Hard WAIT. Earnings ≤ 7d from screening date: immediate WAIT output, no further regime evaluation, no override path. |
| `EARNINGS_CAUTION_DAYS` | 21 | calendar days | PASS1, SIGNAL | Soft WAIT. Earnings 8–21d out: WAIT with named operator-approval gate. Candidate does not advance to Eligible until operator explicitly redirects in current session. |
| `DTE_DECAY_WARNING_THRESHOLD` | 21 | calendar days | PORTFOLIO_MGMT | The remaining DTE at or below which PORTFOLIO_MGMT surfaces a DTE decay warning for an open position. Signals that the operator may want to roll or close rather than hold to expiration. Operator-configurable; 21 days is the default, corresponding to the point where theta decay accelerates materially for most structures. |
| `TIER_GATE_TAU_HIGH` (`τ_high`) | 0.70 | confidence score [0–0.95] | WYCKOFF, PASS1 | **Provisional — calibrate in the Stage-1 pilot.** Auto-accept threshold for the viewer/v2 ingest tier gate. When the gating confidence — `min(regime_confidence, phase_confidence)`, or `regime_confidence` alone when `phase_confidence` is null — is at or above this value, the viewer reading is accepted as `pipeline-accepted` without a propose-confirm exchange (hard force-flags still apply per WYCKOFF). Viewer/v2 confidence is capped at 0.95, so `τ_high` must stay strictly below 0.95. Boundary value resolves to accept. |
| `TIER_GATE_TAU_LOW` (`τ_low`) | 0.45 | confidence score [0–0.95] | WYCKOFF, PASS1 | **Provisional — calibrate in the Stage-1 pilot.** Flagged-vs-estimation boundary for the viewer/v2 ingest tier gate. When the gating confidence falls in `[τ_low, τ_high)` the reading is `pipeline-flagged` and surfaced for operator resolution; below `τ_low` the viewer reading is not usable as a pipeline reading and the ticker falls to the estimation path (propose-confirm) or UNKNOWN. Boundary value resolves to flagged (conservative). `τ_low ≤ τ_high` is an invariant. |
| `FORWARD_TEST_CONFLUENCE_BAND_PCT` | 0.5 | percent of spot (±) | SIGNAL, REPORT_FORMAT | **Provisional — pilot-calibrated.** The near-coincidence tolerance within which the viewer's forward-tested target (`pt_*`) is treated as confluent with the SIGNAL structural+validated exit anchor, so its calibrated hit-rate (`*_prob`) rides as a confidence annotation on the alert level; beyond ±this band the target is divergent and both levels surface for operator judgment. Annotation context only — never the broker order price (anti-hallucination floor). Symmetric, anchored to spot so it scales across tickers. |
| `CONDITIONAL_TOP_SIZE_PCT` | 1.0 | percent of real-capital denominator | RISK | The sizing magnitude for the **conditional-top** band — a direction-aligned base regime (`accumulation` long / `distribution` long put) confirmed at phase C (`spring`/`shakeout` / `utad`) but not yet broken out; sizes below a confirmed trend (JD1). Operator-tunable. RISK's other band reference magnitudes (~3%/2%/1%/0.5%, 5% ceiling) remain v2.3 reference points in RISK's Appendix; the conditional-top is the v4.0-new band promoted here as the named tunable value. |

## Workflow integration

This file is consumed by:

- `PASS1_SCREENING_v3.0.md` — reads `SWING_DTE_BAND`, `CSP_DTE_BAND`, `LEAP_DTE_BAND` for candidate zone DTE band assembly
- `PASS2_VALIDATION_v3.0.md` — reads the same DTE bands for expiration selection scope; reads `IV_HV_ELEVATED_THRESHOLD` and `IV_RANK_EXTREME_FLOOR` as spread-mandate resolution inputs
- `SIGNAL_v3.0.md` — reads `IV_HV_ELEVATED_THRESHOLD` and `IV_RANK_EXTREME_FLOOR` for spread-mandate trigger specification; reads `SWING_DTE_BAND` and `CSP_DTE_BAND` for anti-hallucination label text; reads `FORWARD_TEST_CONFLUENCE_BAND_PCT` as the forward-tested-target confluence tolerance on the exit anchors
- `REPORT_FORMAT_v3.0.md` — reads `FORWARD_TEST_CONFLUENCE_BAND_PCT` as the divergence boundary for rendering the forward-tested-target confidence suffix on the exit-plan / exit-trigger-proximity rows
- `RISK_v3.0.md` — reads `CONDITIONAL_TOP_SIZE_PCT` as the conditional-top sizing-band magnitude
- `VOLATILITY_v3.0.md` — reads `IV_HV_ELEVATED_THRESHOLD` and `IV_RANK_EXTREME_FLOOR` as the Appendix band boundary values
- `DEALER_v3.0.md` — reads `NEAR_FLIP_BAND_PCT` as the near-flip zone Appendix band value, and `DGPI_NEUTRAL_BAND` / `DGPI_STRONG_BAND` / `HOSTILE_MACRO_DGPI_MAX` as the DGPI tier cutpoints and hostile-macro DGPI threshold
- `PORTFOLIO_MGMT_v3.0.md` — reads `DTE_DECAY_WARNING_THRESHOLD` for DTE decay warning evaluation at Step 5 of the Portfolio mode workflow
- `WYCKOFF_v3.0.md` — reads `TIER_GATE_TAU_HIGH` and `TIER_GATE_TAU_LOW` as the viewer/v2 ingest tier-gate boundaries that resolve a pasted reading to `pipeline-accepted`, `pipeline-flagged`, or estimation-path
- `PASS1_SCREENING_v3.0.md` — reads `TIER_GATE_TAU_HIGH` and `TIER_GATE_TAU_LOW` indirectly via WYCKOFF when ingesting a viewer/v2 handoff as the candidate source; PASS1 does not re-implement the gate, it consumes WYCKOFF's resolved confirmation status

This file does not consume any other runtime file. It has no upstream dependencies within `llm_runtime/`.

## Legacy anchors (for legend citations and back-compat)

No legacy rule IDs map to this file. SYSTEM_PARAMS is a new v3.0 construct with no v2.3 antecedent. The parameter values it owns were previously hardcoded across multiple runtime files; their v2.3 source locations are documented in the consuming files' legacy anchor sections and in `engineering_only/` references.

## Appendix — parameter change log

Changes to individual parameter values are recorded here in addition to the top-level `CHANGELOG.md` entry, so the history of each parameter is visible without reading the full changelog.

| Date | Parameter | Old value | New value | Rationale |
|---|---|---|---|---|
| 2026-05-11 | `SWING_DTE_BAND` | 45–60 days (hardcoded in PASS1, SIGNAL) | 60–120 days | Corrects a v3.0 authoring error; 45–60 DTE was carried from a v2.3 scaffold without operator validation and conflicts with actual operator practice of 60–120 DTE for swing trades |
| 2026-05-11 | `CSP_DTE_BAND` | 45–60 days (implied, same hardcode as swing) | 45–60 days | Value is correct; CSP band is now explicitly separated from swing band and defined independently in SYSTEM_PARAMS rather than implied by the swing band default |
| 2026-05-12 | `DTE_DECAY_WARNING_THRESHOLD` | (not previously defined) | 21 days | New parameter added in session 9 for PORTFOLIO_MGMT. 21 days is the default threshold at which theta decay accelerates materially for most structures; operator may recalibrate based on their roll/close discipline |
| 2026-06-26 | `TIER_GATE_TAU_HIGH` | (not previously defined) | 0.70 (provisional) | New parameter for the v4.0 viewer/v2 ingest tier gate (Integration Plan §A1/§A5). Provisional default pending Stage-1 pilot calibration; the pilot's viewer→Pass-1 dry-run exists specifically to catch a τ mis-set against a manual propose-confirm run on the same 10–15 tickers. Must stay below the 0.95 confidence cap |
| 2026-06-26 | `TIER_GATE_TAU_LOW` | (not previously defined) | 0.45 (provisional) | New parameter for the v4.0 viewer/v2 ingest tier gate (Integration Plan §A1/§A5). Provisional default pending Stage-1 pilot calibration. Invariant: `τ_low ≤ τ_high` |
| 2026-06-28 | `FORWARD_TEST_CONFLUENCE_BAND_PCT` | (not previously defined) | 0.5 (provisional) | New v4.0 param for the SIGNAL forward-tested-target confluence annotation (#78). The near-coincidence tolerance deciding when the viewer `pt_*`/`*_prob` rides as a confidence annotation on the exit anchor vs both levels surfacing. Provisional ±0.5% of spot pending pilot calibration; resolves the "SYSTEM_PARAMS follow-up" placeholders SIGNAL/REPORT_FORMAT carried |
| 2026-06-28 | `CONDITIONAL_TOP_SIZE_PCT` | ~1% (reference point in RISK Appendix) | 1.0 | Promotes the v4.0 conditional-top sizing magnitude (JD1) from a RISK Appendix reference point to a named operator-tunable SYSTEM_PARAMS value (#78); RISK now references it by name. Value unchanged (~1% → 1.0%); only the ownership/tunability surface changes |
| 2026-06-28 | `NEAR_FLIP_BAND_PCT` | 0.25 | 0.5 | Dealer contract reconciliation: aligned the KB near-flip band to the producers' actual 0.5% `at_flip` band (both kapman-polygon-mcp-v2 and kapman-schwab-MCP); the prior 0.25% disagreed with both. |
| 2026-06-28 | `DGPI_NEUTRAL_BAND` / `DGPI_STRONG_BAND` / `HOSTILE_MACRO_DGPI_MAX` | (DEALER-hardcoded 20/50; macro ≤ -20) | 10 / 30 / -30 | Dealer contract reconciliation: re-keyed DEALER's DGPI tier cutpoints to the producer's signed-DGPI 10/30/60 magnitude bands (kapman-polygon-mcp-v2 `calculate_dgpi`), matching the viewer header; promoted from DEALER-hardcoded to named tunables. Hostile-macro set to the hostile tier (-30); sign-dominated in practice. |
