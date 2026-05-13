---
system: KapMan
doc_type: principle
kb_version: 3.0.0
file_last_updated: 2026-05-13
status: active
tier: T1
---

# DEALER

## Principle

Dealer regime is a market-state signal read from delivered MCP fields, not a quantity the runtime derives. The dealer-metrics pipeline computes net GEX, the gamma flip level, call and put walls, GEX slope, and the bounded Dealer Gamma Pressure Index (DGPI) from filtered option-chain data, and surfaces them as a small set of numbers and labels per ticker. The runtime's job is to interpret those outputs as a regime, not to re-derive them: the formulas, filter thresholds, and pipeline defaults that produce the numbers are engineering concerns and live in the engineering-only reference. The governing judgment is that dealer positioning exerts a directional pressure on price that varies with where spot sits relative to the gamma flip and with how the DGPI score is leaning, and that this pressure is meaningful enough to gate structure selection and sizing — but only when the underlying data is deep enough to trust. Two layers of dealer regime apply simultaneously and serve different purposes. The macro layer is the SPY dealer regime; it gates whether long-premium directional structures are eligible at all across every ticker in the eligible set, and the hostile macro refusal owned by `KAPMAN_GUARDRAILS_v3.0.md` is the behavioral consequence of that layer turning red. The ticker layer is the per-name dealer regime; it narrows the sizing band within whatever ceiling Wyckoff has already set, and is consumed by `RISK_v3.0.md`. The two layers can disagree — a ticker can show a strongly supportive DGPI while SPY is below its own flip with deeply negative DGPI — and when they disagree, the macro layer takes precedence by default, with operator override available per GUARDRAILS. The flip level is interpreted as a behavioral boundary, not a hard threshold: spot well above the flip lives in a regime where dealer hedging dampens moves, spot well below it lives in a regime where dealer hedging amplifies them, and spot close to the flip is a near-flip zone where the regime is unstable enough to warrant a defensive one-tier sizing reduction. Data depth is a precondition for trusting any of this — when the chain underlying the dealer metrics is thin, the FULL/LIMITED/INVALID quality label delivered by the pipeline is taken at face value, and weak-confidence dealer signals are not laundered into confident regime calls.

## Operational heuristics

**The macro layer is read from SPY, not from a composite.**
"Macro dealer regime" means the SPY dealer regime as delivered by MCP. There is no aggregate-of-tickers macro composite; SPY's DGPI, SPY's distance to its own gamma flip, and SPY's FULL/LIMITED/INVALID label are the three readings that define macro state. When SPY's dealer-metrics quality is degraded (LIMITED or INVALID), the macro layer is read with reduced confidence and the report says so plainly; macro regime is not asserted as supportive on weak SPY data.

**DGPI tier names are a vocabulary, not a scoring system.**
Delivered DGPI is bounded to roughly ±100 by the pipeline. The runtime reads the score into one of five tiers — strongly supportive, moderately supportive, near-neutral, weakening, hostile — using bands in the Appendix. The tier name is what downstream files consume; the raw number appears in the report for transparency but doesn't drive behavior beyond tier resolution. A DGPI sitting on a tier boundary is read into the more conservative tier (e.g., a value at the boundary between moderately supportive and near-neutral is read as near-neutral), because the bands describe regime, not precision.

**Spot's position relative to the flip dominates DGPI in the macro layer.**
For macro gating, where SPY sits relative to its gamma flip is the primary read, with DGPI as the modifier. SPY well above its flip with positive DGPI is supportive macro; SPY well below its flip with negative DGPI is hostile macro and triggers the long-premium refusal owned by GUARDRAILS; SPY above its flip but with negative DGPI, or below its flip with positive DGPI, is mixed macro and is treated as the more conservative of the two readings. "Well above" and "well below" mean comfortably outside the near-flip zone defined in the Appendix.

**Near-flip is a behavioral zone, not a single line.**
SPY (for macro) or the ticker (for per-name) sitting within a narrow symmetric band on either side of its gamma flip is the near-flip zone — the band width is defined in the Appendix as a percentage of spot, not as an absolute dollar amount, so the same definition scales across SPY at any price and across tickers at any price. The behavioral consequence is the one-tier sizing step-down enforced by RISK and required by GUARDRAILS — it is not a refusal. The zone applies symmetrically: just above the flip and just below it are both unstable. "Well above" and "well below" mean outside this band on the favorable and unfavorable side respectively.

**The ticker layer narrows within the Wyckoff ceiling, never above it.**
A per-name DGPI in the strongly supportive tier does not promote a setup beyond what Wyckoff has authorized. If Wyckoff phase has set the ceiling at mid-band (e.g., accumulation pre-Spring), a strongly supportive ticker DGPI keeps the sizing at the top of the conditional range, not above it. Dealer regime can only step a setup down within the ceiling, or — in the supportive case — hold it at the top of whatever ceiling Wyckoff allows.

**Ticker-level DGPI and ticker-level flip distance combine the same way as macro.**
Within the ticker layer, the same interpretation applies: where spot sits relative to the ticker's flip is the dominant read, with the ticker's DGPI as a modifier. A ticker well above its flip with a moderately supportive DGPI earns the top of its sizing band; a ticker below its flip with a weakening DGPI earns the floor. Distribution and markdown phases close the long-premium band entirely regardless of how the ticker's dealer regime reads — that is a Wyckoff decision, not a dealer decision.

**Walls are reference levels, not entry triggers.**
Call and put walls delivered by the pipeline mark strike levels where dealer hedging is concentrated. They inform structure selection (a long call entered just below a strong call wall is paying premium against likely resistance) and inform stop placement (a stop placed just on the wrong side of a wall is more likely to be tagged). Walls do not by themselves block or authorize a setup. When wall data is delivered as LIMITED, the walls are reported but not used to adjust structure.

**GEX slope is a confirmation signal, not a primary read.**
GEX slope around spot is delivered alongside DGPI and refines the regime read by indicating how rapidly dealer hedging pressure is changing with price. A positive slope in supportive territory reinforces the supportive read; a steeply negative slope near the flip is a warning that the near-flip zone is unstable in the unfavorable direction. Slope does not have its own tier vocabulary; it is consumed as a qualifier inside the rationale, not as a standalone gate.

**Data quality labels are taken at face value.**
The FULL/LIMITED/INVALID label delivered by the pipeline governs how much weight the dealer regime carries. FULL data permits the full sizing band and the full hostile-macro refusal behavior. LIMITED data restricts the ticker to floor-of-band sizing regardless of what DGPI reads, and the report acknowledges the data limitation in the rationale. INVALID data means the dealer regime is not read at all for that ticker — the macro gate still applies via SPY, but the ticker layer is treated as absent rather than as supportive or hostile. The runtime does not paper over LIMITED or INVALID labels by interpolating or by reaching for stale prior readings.

**The two-layer ordering is fixed: macro first, ticker second.**
For any candidate, the macro gate is checked first against SPY. If macro is hostile, the structure-eligibility set is constrained per GUARDRAILS before the ticker layer is consulted. Only after the macro gate has been passed (or explicitly overridden) does the ticker dealer regime narrow the sizing band. Reversing the order — letting a ticker's strong DGPI drive a setup that the macro gate would refuse — is the failure mode this ordering exists to prevent.

**Overrides act on the layer they name.**
A "macro gate override" operator phrase relaxes the macro layer for the named structure on the named ticker; it does not change how the ticker layer reads. A ticker with a hostile own-flip position and weakening DGPI remains a poor sizing candidate even when macro has been overridden, and that read still flows through to RISK as floor-of-band sizing. Override granularity matters: macro and ticker are separately overrideable in principle, though in practice the macro gate is the override that comes up.

**Stale readings degrade the layer they affect; the runtime does not auto-refresh.**
Dealer metrics carry a freshness timestamp from the pipeline. When metrics fall outside the pipeline's freshness window, the affected layer is degraded: stale SPY restricts the macro gate to the conservative read (long-premium structures restricted by default, same as near-flip behavior) until fresh data is available; stale ticker reads identical to INVALID and drops the ticker layer for that name. The runtime does not initiate refreshes — refresh is operator-initiated — but the report surfaces the staleness explicitly with a *"Stale dealer data"* label and a refresh prompt naming the affected ticker and last-refresh timestamp. The operator decides whether to refresh-and-retry or proceed with degraded confidence.

## Workflow integration

**Position in the document hierarchy.** DEALER is tier T1 — a principle file. It owns the runtime interpretation of dealer regime: how delivered MCP fields translate into a regime label, how the macro and ticker layers combine, and what data quality means for trust in those readings. DEALER does not compute its own inputs; the dealer-metrics pipeline, documented in the engineering-only reference, produces every number and label DEALER consumes. DEALER does not enforce sizing, does not refuse structures, and does not render output — those are downstream concerns owned by RISK, GUARDRAILS, and the report layer respectively.

**Inputs DEALER reads from the pipeline.**

| Field | Source | What DEALER does with it |
|---|---|---|
| Net GEX (per ticker) | Dealer-metrics pipeline via MCP | Read as a magnitude/sign reference; not directly tier-mapped at the runtime — the bounded DGPI is the runtime-facing signal |
| Gamma flip level (per ticker) | Dealer-metrics pipeline via MCP | Compared to spot to determine well-above / near-flip / well-below zone |
| Call wall, put wall (per ticker, ranked list) | Dealer-metrics pipeline via MCP | Read as strike-level reference points for structure selection and stop placement |
| GEX slope around spot (per ticker) | Dealer-metrics pipeline via MCP | Read as a confirmation modifier on the DGPI tier read |
| DGPI score (per ticker, bounded ±100) | Dealer-metrics pipeline via MCP | Mapped to tier vocabulary (strongly supportive / moderately supportive / near-neutral / weakening / hostile) per Appendix bands |
| Position class (long_gamma / short_gamma / neutral) | Dealer-metrics pipeline via MCP | Cross-referenced with DGPI tier; a position-class flip near the neutral deadzone is a signal that DGPI is in tier-boundary territory |
| Confidence level (high / medium / low / invalid) | Dealer-metrics pipeline via MCP | Combined with eligible-options count to resolve the FULL/LIMITED/INVALID dealer-status label |
| Dealer status (FULL / LIMITED / INVALID) | Dealer-metrics pipeline via MCP | Governs how much weight the regime read carries downstream; taken at face value |
| Freshness timestamp | Dealer-metrics pipeline via MCP | Compared to the pipeline's freshness window to determine whether the reading is current or stale |

DEALER reads these fields as delivered; it does not recompute any of them, does not interpolate when a field is missing, and does not reach for stale prior values when a current field is degraded.

**Where DEALER outputs flow downstream.**

| Output | Consumed by | What the downstream file does with it |
|---|---|---|
| DGPI tier (strongly supportive / moderately supportive / near-neutral / weakening / hostile) — per ticker | `RISK_v3.0.md` | Narrows the sizing band within the Wyckoff ceiling: supportive tiers earn top-of-band, weakening earns floor |
| DGPI tier — for SPY (macro layer) | `KAPMAN_GUARDRAILS_v3.0.md` | Combined with SPY flip distance to determine hostile-macro refusal |
| Flip-zone classification (well above / near-flip / well below) — per ticker | `RISK_v3.0.md` | Refines sizing band within the DGPI tier; near-flip triggers the one-tier step-down |
| Flip-zone classification — for SPY | `KAPMAN_GUARDRAILS_v3.0.md` | The "SPY below flip" half of the hostile-macro definition; near-flip SPY triggers the macro-level size step-down |
| Near-flip flag (boolean, per ticker including SPY) | `RISK_v3.0.md`, `KAPMAN_GUARDRAILS_v3.0.md` | RISK applies the one-tier step-down to the selected band; GUARDRAILS enforces that the step-down is applied and not silently relaxed |
| Hostile-macro flag (boolean, SPY-derived) | `KAPMAN_GUARDRAILS_v3.0.md` | Triggers the long-premium refusal and the eligible-set redirect (CSPs, hedges, LEAPs) |
| Call/put wall levels (per ticker) | `PASS2_VALIDATION_v3.0.md`, `REPORT_FORMAT_v3.0.md` | PASS2 informs structure selection (avoid paying premium against a near-strike wall); REPORT_FORMAT renders the walls in the rationale where relevant |
| Dealer-status label (FULL / LIMITED / INVALID) — per ticker | `PASS2_VALIDATION_v3.0.md`, `RISK_v3.0.md`, `REPORT_FORMAT_v3.0.md` | PASS2 may drop a candidate when status is INVALID and chain quality is also degraded; RISK reads LIMITED as floor-of-band; REPORT_FORMAT surfaces the label in the data-quality section |
| Stale-data flag (per ticker) | `RISK_v3.0.md`, `REPORT_FORMAT_v3.0.md`, `KAPMAN_GUARDRAILS_v3.0.md` | RISK applies the same restriction as INVALID for affected ticker layer; GUARDRAILS treats stale SPY as the conservative macro read; REPORT_FORMAT surfaces the *"Stale dealer data"* label with timestamp |
| GEX slope qualifier | `REPORT_FORMAT_v3.0.md` | Rendered as part of the rationale text where it materially refines the regime read; not a standalone field |

**Entry point for every dealer regime read.** Before consuming dealer regime for sizing or gating, four conditions must hold in the working context:

1. The MCP dealer-metrics fields for the ticker (and for SPY, for macro reads) have been fetched in the current session.
2. The freshness timestamps are within the pipeline's defined window — stale readings degrade the layer they affect rather than being silently consumed.
3. The dealer-status label is read as delivered — FULL, LIMITED, or INVALID — and weighted accordingly. Degraded labels are not laundered into confident reads.
4. The macro layer is resolved against SPY before the ticker layer is consulted. The fixed ordering is non-negotiable absent an explicit override.

If any condition fails, the affected layer reads as absent (for ticker) or as the conservative default (for macro), and the report surfaces the gap explicitly. A dealer regime read on incomplete data is a guardrail violation, not a DEALER violation — but the failure surfaces in the report as a degraded-confidence or no-regime output.

**Cross-references this file expects to be honored.**

- `KAPMAN_GUARDRAILS_v3.0.md` — owns the behavioral consequence of hostile macro (the long-premium refusal) and the override discipline. DEALER provides the trigger conditions; GUARDRAILS owns what happens when those conditions are met.
- `RISK_v3.0.md` — consumes DGPI tiers, flip-zone classifications, and the near-flip flag as sizing inputs. RISK does not re-derive any dealer regime; it reads DEALER's output and converts to a sizing band.
- `WYCKOFF_v3.0.md` — sets the sizing-band ceiling that DEALER's ticker layer narrows within. DEALER cannot promote a setup beyond what Wyckoff has authorized.
- `VOLATILITY_v3.0.md` — runs in parallel with DEALER; both feed RISK. DEALER does not consume volatility regime, and volatility does not consume dealer regime, but both layer onto the same sizing decision downstream.
- `PASS2_VALIDATION_v3.0.md` — uses dealer-status labels and wall levels during structure validation. PASS2 owns chain-quality categorization (full / limited / weak) which is distinct from dealer-status (FULL / LIMITED / INVALID) — the two labels can co-occur in any combination and both must be honored.
- `REPORT_FORMAT_v3.0.md` — renders DEALER's outputs (tier label, flip zone, walls, dealer status, stale-data flag, refresh prompt) into the report. DEALER does not own report formatting; it owns what the report has to say about regime.
- `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming) — owns every formula, filter threshold, weighting tier, slope window, confidence cutoff, and runtime default that produces the inputs DEALER reads. The runtime DEALER file is silent on all of these by design.

**When DEALER is silent.** DEALER does not own:

- Pipeline computation. The formulas for net GEX, strike-level GEX, gamma flip interpolation, wall weighting, slope, DGPI, position class, and confidence resolution all live in the engineering-only pipeline reference. The runtime reads outputs; it does not derive them.
- Filter thresholds. DTE windows, open-interest minimums, volume minimums, max moneyness, and similar pipeline parameters are engineering concerns and do not appear in this file.
- Pipeline defaults. The walls-top-n value, the slope-range percentage, the contract multiplier, and other backend defaults are engineering concerns.
- Eligible-options count cutoffs that produce FULL/LIMITED/INVALID labels. The runtime consumes the label, not the count.
- Chain-quality categorization (full / limited / weak as it relates to executable contract depth). That is PASS2's domain. DEALER's status labels (FULL / LIMITED / INVALID) measure data depth for the dealer-metrics calculation specifically and are not the same thing as PASS2's executable chain quality.
- Refresh orchestration. The runtime does not initiate refreshes; that is operator-driven.
- Per-ticker historical comparisons (e.g., "DGPI is unusually negative for this name relative to its 6-month range"). The pipeline delivers point-in-time values; comparative analysis is operator work, not runtime work.

A dealer-regime question that doesn't fit one of the rules above is a question DEALER does not govern.

## Legacy anchors (for legend citations and back-compat)

**DEALER_001** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The v2.3 contract-filtering thresholds (`dte <= 90`, `open_interest >= 100`, `volume >= 1`, gamma present) are pipeline data-quality controls applied before any dealer metric is computed. They have no LLM runtime effect — the runtime consumes the filtered output, never the raw chain — and are preserved in the engineering-only pipeline reference rather than in this file. Body-text references in legacy report legends (e.g., "Rules applied: DEALER_001") remain valid; the legend entry resolves to the engineering-only destination, and the runtime behavioral consequence the legend implies (that downstream metrics are trustworthy because contracts were filtered) is captured here under § Operational heuristics, "Data quality labels are taken at face value."

**DEALER_002** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The per-contract GEX formula (`gex = gamma * open_interest * spot^2 * 0.01 * contract_multiplier`, with call-side sign inversion) is pipeline computation; the runtime never derives per-contract GEX and never sees the unrolled formula. Preserved in engineering-only for back-compat with legacy report legends and for engineering maintenance of the pipeline.

**DEALER_003** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The strike-level GEX aggregation rule (additive across contracts at the same strike) is pipeline computation. Runtime consumes the strike ladder as a delivered input to flip and slope; it does not aggregate strike-level GEX itself.

**DEALER_004** → § Operational heuristics, "Spot's position relative to the flip dominates DGPI in the macro layer" and "Near-flip is a behavioral zone, not a single line"; computation portion to `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The v2.3 anchor combined the *interpretation* of the gamma flip as a regime-changing boundary with the *computation* of the flip level by zero-cross interpolation. The interpretation — that the flip marks where dealer hedge behavior changes regime — is load-bearing for the runtime and is preserved here as the spot-vs-flip dominance heuristic and the near-flip zone heuristic. The interpolation computation belongs to the pipeline and is preserved in engineering-only.

**DEALER_005** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). Wall candidate filtering (contract-type match, positive OI, non-null gamma, `abs(strike-spot)/spot <= 0.2`) is pipeline preprocessing for wall ranking. Runtime consumes the filtered wall list as delivered.

**DEALER_006** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The tiered moneyness weighting for wall ranking (1.0 / 0.7 / 0.4 / 0.2 across the four moneyness bands) is pipeline computation. The behavioral consequence — that walls reflect proximity-weighted significance and should be read as such — is captured here under § Operational heuristics, "Walls are reference levels, not entry triggers," without exposing the specific weight values.

**DEALER_007** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). Wall ranking sort (descending weighted GEX, strike tie-break) and top-N truncation (default `top_n = 3`) are pipeline output formatting. Runtime consumes the ranked, truncated list as delivered.

**DEALER_008** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The GEX slope formula (`slope = (upper_gex - lower_gex) / price_range` over `±2%` of spot) is pipeline computation. The behavioral consequence — that slope refines the DGPI tier read as a directional indicator of hedging pressure change around current price — is captured here under § Operational heuristics, "GEX slope is a confirmation signal, not a primary read."

**DEALER_009** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming) for the formula; § Principle and § Operational heuristics, "DGPI tier names are a vocabulary, not a scoring system" for the runtime semantics. The DGPI formula itself — signed log-scaled net GEX, slope multiplier with `±0.3` clamp, optional IV-rank weighting, output clamp to `[-100, 100]` — is pipeline computation and is preserved in engineering-only with no runtime exposure. The runtime contract is that DGPI arrives bounded to roughly ±100 with a defined sign convention; the tier mapping that converts that score into runtime regime vocabulary is owned by this file and lives in the Appendix.

**DEALER_010** → § Operational heuristics, "DGPI tier names are a vocabulary, not a scoring system" and § Appendix; computation portion to `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The v2.3 position-class threshold (`|net_gex| < 1,000,000` → neutral; positive → long_gamma; negative → short_gamma) is pipeline classification of net GEX into a categorical label. Runtime reads position_class as a delivered label and cross-references it with DGPI tier for boundary detection — a position-class flip near the neutral deadzone signals tier-boundary territory. The numeric `1,000,000` threshold is a pipeline parameter and lives in engineering-only; the *use* of position_class as a runtime cross-check is preserved here as part of the DGPI tier vocabulary heuristic.

**DEALER_011** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The confidence-level classifier (contracts-with-gamma 5/10 cutoffs, total OI ≥ 1000 for `high`, downgrades to `medium`/`low`/`invalid` below those bounds) is pipeline data-depth assessment. Runtime consumes the resulting confidence label only as input to the FULL/LIMITED/INVALID dealer-status resolution and does not see the raw cutoffs. Preserved in engineering-only.

**DEALER_012** → § Operational heuristics, "Data quality labels are taken at face value"; computation portion to `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The v2.3 anchor defined how the FULL / LIMITED / INVALID dealer-status label is resolved from eligible-options count, GEX validity, position-class validity, and confidence level. The numeric cutoffs (FULL requires `eligible_options >= 25`; LIMITED requires `>= 1`) are pipeline parameters and live in engineering-only. The runtime vocabulary (FULL / LIMITED / INVALID) and its behavioral contract — FULL permits full sizing band and full hostile-macro behavior; LIMITED restricts to floor-of-band; INVALID drops the ticker layer entirely — are owned by this file and are load-bearing for RISK and PASS2 downstream.

**DEALER_013** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The v2.3 secondary metadata-status classifier (with `min_eligible_threshold = 5` for the metadata-layer FULL/LIMITED resolution, distinct from the primary classifier's `25`) is a pipeline-internal payload-quality annotation. The runtime sees only the resolved status label and does not distinguish between primary and metadata classifiers — both resolve to the same FULL/LIMITED/INVALID vocabulary at the runtime boundary. Preserved in engineering-only as documentation of the pipeline's two-layer classification scheme.

**DEALER_014** → `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming). The pipeline runtime defaults (`walls_top_n = 3`, `gex_slope_range_pct = 0.02`, `max_moneyness = 0.2`) are pipeline parameters governing model behavior across runs. They have no LLM runtime effect — the runtime consumes the pipeline's output regardless of which defaults produced it — and are preserved in engineering-only for engineering maintenance and reproducibility.

## Appendix — formulas and reference tables

**DGPI tier bands.** Delivered DGPI is bounded by the pipeline to roughly ±100. The runtime reads the score into one of five tiers using the bands below. Boundary values resolve to the more conservative tier per § Operational heuristics.

| DGPI band | Tier name | Macro layer consequence (SPY) | Ticker layer consequence (per-name, within Wyckoff ceiling) |
|---|---|---|---|
| ≥ 50 | Strongly supportive | Supportive macro; long-premium structures eligible | Top of sizing band |
| 20 to 49 | Moderately supportive | Supportive macro; long-premium structures eligible | Mid sizing band |
| -19 to 19 | Near-neutral | Neutral macro; long-premium eligible but spot-vs-flip dominates the read | Mid-to-floor sizing band, weighted by spot-vs-flip |
| -49 to -20 | Weakening | Cautious macro; long-premium eligible only when SPY is comfortably above flip | Floor of sizing band |
| ≤ -50 | Hostile (when combined with SPY below flip — see hostile macro composite below) | Hostile macro refusal owned by GUARDRAILS when combined with below-flip | Floor of sizing band; combined with markdown Wyckoff phase, long-premium band closes entirely |

The bands above preserve the v2.3 carryover values referenced in `KAPMAN_GUARDRAILS_v3.0.md` and `RISK_v3.0.md` (DGPI ≥ 50 for strongly supportive, ≥ 20 for moderately supportive, ≤ -20 for the weakening floor, ≤ -50 sealing hostile macro when combined with below-flip).

**Hostile macro composite.** Hostile macro is a two-condition composite read from SPY only:

| Condition | Definition |
|---|---|
| SPY spot below gamma flip | Spot price strictly below the delivered SPY gamma flip level, comfortably outside the near-flip zone (i.e., Spot < SPY_flip × 0.9975) |
| SPY DGPI in weakening tier or worse | DGPI ≤ -20 |

When **both** conditions hold, hostile macro is active and triggers the long-premium refusal owned by `KAPMAN_GUARDRAILS_v3.0.md`. When only one condition holds (SPY below flip with DGPI > -20, or SPY above flip with DGPI ≤ -20), the macro layer reads as mixed and is treated as the more conservative of the two readings per § Operational heuristics. The composite is SPY-specific; ticker-level versions of the same composite are read into the ticker sizing band but do not by themselves trigger refusal.

**Near-flip zone.** Symmetric percentage band around the delivered gamma flip level, applied identically to SPY (for macro) and to per-name tickers (for ticker layer):

| Zone | Definition |
|---|---|
| Well above flip | Spot > flip × 1.0025 (i.e., more than 0.25% above flip) |
| Near-flip | flip × 0.9975 ≤ Spot ≤ flip × 1.0025 (i.e., within ±0.25% of flip) |
| Well below flip | Spot < flip × 0.9975 (i.e., more than 0.25% below flip) |

The 0.25% band is anchored to spot, which scales the zone correctly across SPY at any price and across tickers at any price. The zone is symmetric: just above the flip and just below it are both unstable. Near-flip triggers the one-tier sizing step-down enforced by RISK and required by GUARDRAILS; it is not a refusal. The mechanical step-down ladder (which selected band steps down to which) is owned by `RISK_v3.0.md` and lives there. The `NEAR_FLIP_BAND_PCT` (0.25%) value is defined as a named parameter in `SYSTEM_PARAMS_v3.0.md`; update that file when recalibrating the band.

**Dealer status label semantics.** The FULL / LIMITED / INVALID label delivered by the pipeline carries a defined runtime behavioral contract:

| Label | Pipeline meaning (informational; mechanics in engineering-only) | Runtime behavioral consequence |
|---|---|---|
| FULL | Dealer-metrics computed from a deep enough chain (eligible-options count above the FULL threshold) with high confidence | Full sizing band per RISK; full hostile-macro refusal behavior when applicable; walls and slope read as usable signals |
| LIMITED | Dealer-metrics computed from a shallow chain (eligible-options count between the LIMITED and FULL thresholds) or medium confidence | Sizing restricted to floor-of-band regardless of DGPI tier; walls reported but not used to adjust structure; rationale acknowledges data limitation |
| INVALID | Insufficient data for trustworthy dealer-metrics computation; eligible-options count below LIMITED threshold, or non-success processing status | Ticker layer reads as absent; macro gate via SPY still applies; no per-name DGPI tier consumed |

The numeric thresholds underlying these labels (eligible-options counts of 25 and 5/1, contracts-with-gamma cutoffs of 5/10, total OI ≥ 1000) are pipeline parameters and live in `engineering_only/DEALER_PIPELINE_v3.0.md` (forthcoming).

**Stale-data label semantics.** When delivered dealer-metrics freshness falls outside the pipeline's freshness window, a stale flag accompanies the reading and carries the following runtime behavioral contract:

| Affected layer | Runtime behavioral consequence | Report surfacing |
|---|---|---|
| SPY (macro) | Macro gate restricted to conservative read — long-premium structures restricted by default until fresh data, same as near-flip behavior; operator override per GUARDRAILS available | *"Stale dealer data — SPY, last refreshed [timestamp]"* in data-quality section; refresh prompt |
| Per-name ticker | Ticker layer reads identical to INVALID; floor-of-band sizing per RISK; macro gate via SPY still applies | *"Stale dealer data — [ticker], last refreshed [timestamp]"* in data-quality section; refresh prompt |

The runtime does not initiate refreshes; refresh is operator-driven. The freshness window itself is a pipeline parameter and lives in engineering-only.

**Position class cross-check.** Delivered position_class (long_gamma / short_gamma / neutral) is consumed as a runtime cross-check against the DGPI tier, not as an independent regime read:

| Observation | Runtime interpretation |
|---|---|
| position_class = long_gamma AND DGPI ≥ 20 | Tier read is well-grounded; supportive read is stable |
| position_class = short_gamma AND DGPI ≤ -20 | Tier read is well-grounded; weakening/hostile read is stable |
| position_class = neutral AND DGPI in -19 to 19 range | Tier read is well-grounded; near-neutral read is stable |
| Disagreement between position_class and DGPI tier (e.g., position_class = neutral but DGPI = 35) | Tier-boundary territory; read DGPI tier into the more conservative adjacent tier |

The numeric `|net_gex| < 1,000,000` threshold that the pipeline uses to assign position_class lives in engineering-only.

**Vocabulary alignment with data-quality labels.** Standard report surfacing for DEALER-owned data conditions, aligned with the data-quality vocabulary in `KAPMAN_GUARDRAILS_v3.0.md`:

| Condition | Report label | When used |
|---|---|---|
| FULL dealer-status, fresh data | (No label required; regime reported as resolved tier) | Normal case |
| LIMITED dealer-status | *"Weak dealer signal — LIMITED chain depth"* | Eligible-options count below FULL threshold |
| INVALID dealer-status | *"Dealer regime not assessed — INVALID data"* | Ticker layer absent |
| Stale dealer data | *"Stale dealer data — [ticker], last refreshed [timestamp]"* | Freshness window exceeded |
| Near-flip zone active (ticker) | *"Near-flip — sizing reduced one tier"* | Spot within ±0.25% of ticker flip |
| Near-flip zone active (SPY) | *"Near-flip macro — sizing reduced one tier across eligible set"* | Spot within ±0.25% of SPY flip |
| Hostile macro active | *"Hostile macro — long-premium refused; eligible set: CSPs, hedges, LEAPs"* | Both hostile-macro composite conditions met |
| Mixed macro | *"Mixed macro — conservative read"* | One but not both hostile-macro conditions met |

**Metric vocabulary reference.** The metrics this file consumes, named consistently across the KB:

| Term | Definition | Owner of definition |
|---|---|---|
| Net GEX | Aggregate signed gamma exposure across all eligible contracts for a ticker, in pipeline units | engineering-only (formula) |
| Gamma flip level | The strike at which cumulative GEX crosses zero, interpolated between adjacent strikes | engineering-only (formula); this file (interpretation) |
| Call wall, put wall | Top-N strike levels where dealer call-side / put-side hedging is concentrated, ranked by proximity-weighted GEX | engineering-only (formula); this file (interpretation) |
| GEX slope | Local gradient of GEX across a ±2% strike window around spot, expressed as units per dollar | engineering-only (formula); this file (interpretation as a confirmation signal) |
| DGPI (Dealer Gamma Pressure Index) | Bounded ±100 composite score derived from net GEX, slope, and optional IV weighting | engineering-only (formula); this file (tier vocabulary and bands) |
| Position class | Categorical label (long_gamma / short_gamma / neutral) derived from net GEX magnitude and sign | engineering-only (threshold); this file (cross-check usage) |
| Confidence | Categorical label (high / medium / low / invalid) derived from chain depth | engineering-only (cutoffs) |
| Dealer status | Categorical label (FULL / LIMITED / INVALID) representing trustworthiness of the full dealer-metrics output for a ticker | engineering-only (cutoffs); this file (behavioral contract) |
| Macro layer / ticker layer | Runtime distinction between SPY-derived dealer regime (macro) and per-name dealer regime (ticker) | this file |
| Near-flip zone | Symmetric ±0.25%-of-spot band around the gamma flip level where regime is treated as unstable | this file |
| Hostile macro | Two-condition composite (SPY below flip AND SPY DGPI ≤ -20) that triggers long-premium refusal | this file (composite); GUARDRAILS (refusal behavior) |
| Stale dealer data | Reading older than the pipeline's freshness window | engineering-only (window); this file (behavioral consequence) |
