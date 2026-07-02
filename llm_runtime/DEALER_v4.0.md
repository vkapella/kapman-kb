---
system: KapMan
doc_type: principle
kb_version: 4.0.0
file_last_updated: 2026-07-02
status: active
tier: T1
---

# DEALER

## Principle

Dealer regime is a market-state signal read from delivered MCP fields, not a quantity the runtime derives. The dealer-metrics pipeline computes net GEX, the gamma flip level, call and put walls, GEX slope, and the bounded Dealer Gamma Pressure Index (DGPI) from filtered option-chain data, and surfaces them as a small set of numbers and labels per ticker. The runtime's job is to interpret those outputs as a regime, not to re-derive them: the formulas, filter thresholds, and pipeline defaults that produce the numbers are engineering concerns and live in the engineering-only reference. The governing judgment is that dealer positioning exerts a directional pressure on price that varies with where spot sits relative to the gamma flip and with how the DGPI score is leaning, and that this pressure is meaningful enough to gate structure selection and sizing — but only when the underlying data is deep enough to trust. Two layers of dealer regime apply simultaneously and serve different purposes. The macro layer is the SPY dealer regime; it gates whether long-premium directional structures are eligible at all across every ticker in the eligible set, and the hostile macro refusal owned by `KAPMAN_GUARDRAILS_v4.0.md` is the behavioral consequence of that layer turning red — a refusal scoped to **bullish** long-premium (long calls, call debit spreads), because a hostile, falling tape is the regime a long put is aligned with, so bearish long-premium is the directionally-aligned redirect rather than a refused structure. The ticker layer is the per-name dealer regime; it narrows the sizing band within whatever ceiling Wyckoff has already set, and is consumed by `RISK_v4.0.md`. The two layers can disagree — a ticker can show a strongly supportive DGPI while SPY is below its own flip with deeply negative DGPI — and when they disagree, the macro layer takes precedence by default, with operator override available per GUARDRAILS. The flip level is interpreted as a behavioral boundary, not a hard threshold: spot well above the flip lives in a regime where dealer hedging dampens moves, spot well below it lives in a regime where dealer hedging amplifies them, and spot close to the flip is a near-flip zone where the regime is unstable enough to warrant a defensive one-tier sizing reduction. Because dampening helps a long and amplification helps a long put, the DGPI tier vocabulary and the spot-vs-flip read are interpreted **relative to the position's direction**: the bands are framed for a long (bullish) position, and a bearish position (a long put) reads their mirror — a dealer regime supportive of a long is adverse to a long put, and a regime hostile to a long is supportive of one. Data depth is a precondition for trusting any of this — when the chain underlying the dealer metrics is thin, the emitted `confidence` rating (`high`/`medium`/`low`/`invalid`) is taken at face value, and weak-confidence dealer signals are not laundered into confident regime calls.

## Operational heuristics

**The macro layer is read from SPY, not from a composite.**
"Macro dealer regime" means the SPY dealer regime as delivered by MCP. There is no aggregate-of-tickers macro composite; SPY's DGPI, SPY's distance to its own gamma flip, and SPY's emitted `confidence` are the three readings that define macro state. When SPY's dealer `confidence` is degraded (`low` or `invalid`), the macro layer is read with reduced confidence and the report says so plainly; macro regime is not asserted as supportive on weak SPY data.

**DGPI tier names are a vocabulary, not a scoring system.**
Delivered DGPI is bounded to roughly ±100 by the pipeline. The runtime reads the score into one of five tiers — strongly supportive, moderately supportive, near-neutral, weakening, hostile — using bands in the Appendix. The tier name is what downstream files consume; the raw number appears in the report for transparency but doesn't drive behavior beyond tier resolution. A DGPI sitting on a tier boundary is read into the more conservative tier (e.g., a value at the boundary between moderately supportive and near-neutral is read as near-neutral), because the bands describe regime, not precision.

**Spot's position relative to the flip dominates DGPI in the macro layer.**
For macro gating, where SPY sits relative to its gamma flip is the primary read, with DGPI as the modifier. SPY well above its flip with positive DGPI is supportive macro; SPY well below its flip with negative DGPI is hostile macro and triggers the **bullish** long-premium refusal owned by GUARDRAILS (long calls refused; long puts are the directionally-aligned redirect); SPY above its flip but with negative DGPI, or below its flip with positive DGPI, is mixed macro and is treated as the more conservative of the two readings. "Well above" and "well below" mean comfortably outside the near-flip zone defined in the Appendix.

**Near-flip is a behavioral zone, not a single line.**
SPY (for macro) or the ticker (for per-name) sitting within a narrow symmetric band on either side of its gamma flip is the near-flip zone — the band width is defined in the Appendix as a percentage of spot, not as an absolute dollar amount, so the same definition scales across SPY at any price and across tickers at any price. The behavioral consequence is the one-tier sizing step-down enforced by RISK and required by GUARDRAILS — it is not a refusal. The zone applies symmetrically: just above the flip and just below it are both unstable. "Well above" and "well below" mean outside this band on the favorable and unfavorable side respectively.

**The ticker layer narrows within the Wyckoff ceiling, never above it.**
A per-name DGPI in the strongly supportive tier does not promote a setup beyond what Wyckoff has authorized. If Wyckoff phase has set the ceiling at mid-band (e.g., accumulation pre-Spring), a strongly supportive ticker DGPI keeps the sizing at the top of the conditional range, not above it. Dealer regime can only step a setup down within the ceiling, or — in the supportive case — hold it at the top of whatever ceiling Wyckoff allows.

**Ticker-level DGPI and ticker-level flip distance combine the same way as macro.**
Within the ticker layer, the same interpretation applies, read relative to the position's direction: where spot sits relative to the ticker's flip is the dominant read, with the ticker's DGPI as a modifier. For a long, a ticker well above its flip with a moderately supportive DGPI earns the top of its sizing band and a ticker below its flip with a weakening DGPI earns the floor; for a long put this mirrors — spot well below the flip with a DGPI adverse to the underlying earns the top of its band, spot above the flip with a long-supportive DGPI earns the floor. The regime that does not align with the position's direction closes the long-premium band entirely regardless of how the ticker's dealer regime reads — for a long that is a distribution-family or markdown regime, for a long put its mirror — and that is a Wyckoff decision, not a dealer decision.

**Dealer regime is read relative to the position's direction.**
The DGPI tier vocabulary and the spot-vs-flip read are framed for a long (bullish) position: a positive DGPI with spot above the flip is supportive because dealer hedging dampens the tape, and a negative DGPI with spot below the flip is hostile because hedging amplifies the downside. A **bearish** position (a long put) reads the exact mirror of the same delivered numbers, sign-flipped: a strongly supportive (long) DGPI is **strongly adverse** to a long put and a hostile (long) DGPI is **supportive** of one; spot well above the flip is adverse to a long put, well below is supportive. The pipeline emits one DGPI with a fixed sign convention; the runtime interprets it against the position's direction and never re-derives it. The **per-ticker bearish-mirror DGPI band** — the ticker dealer regime adverse to a bearish position, defined in the Appendix as the sign-flipped mirror of the bullish per-ticker hostile band — is the band `SIGNAL_v4.0.md`'s dealer-timing veto and `RISK_v4.0.md`'s dealer-narrowing both reference. This is a ticker-layer reading; the macro hostile-macro composite stays bullish-scoped (long puts are its aligned redirect, not a structure it refuses).

**Walls are reference levels, not entry triggers.**
Call and put walls delivered by the pipeline mark strike levels where dealer hedging is concentrated. They inform structure selection (a long call entered just below a strong call wall is paying premium against likely resistance) and inform stop placement (a stop placed just on the wrong side of a wall is more likely to be tagged). Walls do not by themselves block or authorize a setup. When dealer `confidence` is `low`, the walls are reported but not used to adjust structure.

**GEX slope is a confirmation signal, not a primary read.**
GEX slope around spot is delivered alongside DGPI and refines the regime read by indicating how rapidly dealer hedging pressure is changing with price. A positive slope in supportive territory reinforces the supportive read; a steeply negative slope near the flip is a warning that the near-flip zone is unstable in the unfavorable direction. Slope does not have its own tier vocabulary; it is consumed as a qualifier inside the rationale, not as a standalone gate.

**The emitted `confidence` is taken at face value and keys the dealer-trust behavior.**
Both producers emit a `confidence` field (`high`/`medium`/`low`/`invalid`) governing how much weight the dealer regime carries; there is no separate `FULL/LIMITED/INVALID` "dealer-status" — neither producer emits one. Trusted confidence (`high` or `medium`) permits the full sizing band and the full hostile-macro refusal behavior. `low` confidence restricts the ticker to floor-of-band sizing regardless of what DGPI reads, and the report acknowledges the limitation in the rationale. `invalid` confidence means the dealer regime is not read at all for that ticker — the macro gate still applies via SPY, but the ticker layer is treated as absent rather than as supportive or hostile. The runtime does not paper over `low` or `invalid` reads by interpolating or by reaching for stale prior readings.

**The two-layer ordering is fixed: macro first, ticker second.**
For any candidate, the macro gate is checked first against SPY. If macro is hostile, the structure-eligibility set is constrained per GUARDRAILS before the ticker layer is consulted. Only after the macro gate has been passed (or explicitly overridden) does the ticker dealer regime narrow the sizing band. Reversing the order — letting a ticker's strong DGPI drive a setup that the macro gate would refuse — is the failure mode this ordering exists to prevent.

**Overrides act on the layer they name.**
A "macro gate override" operator phrase relaxes the macro layer for the named structure on the named ticker; it does not change how the ticker layer reads. A ticker with a hostile own-flip position and weakening DGPI remains a poor sizing candidate even when macro has been overridden, and that read still flows through to RISK as floor-of-band sizing. Override granularity matters: macro and ticker are separately overrideable in principle, though in practice the macro gate is the override that comes up.

**Stale readings degrade the layer they affect; the runtime does not auto-refresh.**
Dealer metrics carry a freshness timestamp from the pipeline. When metrics fall outside the pipeline's freshness window, the affected layer is degraded: stale SPY restricts the macro gate to the conservative read (long-premium structures restricted by default, same as near-flip behavior) until fresh data is available; a stale ticker reads the same as `invalid` confidence and drops the ticker layer for that name. The runtime does not initiate refreshes — refresh is operator-initiated — but the report surfaces the staleness explicitly with a *"Stale dealer data"* label and a refresh prompt naming the affected ticker and last-refresh timestamp. The operator decides whether to refresh-and-retry or proceed with degraded confidence.

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
| `position` — gamma regime (long_gamma / short_gamma / neutral) | Dealer-metrics pipeline via MCP | The dealer gamma regime (from net-GEX sign + magnitude threshold); cross-referenced with DGPI sign/tier — a `position`/DGPI disagreement near the neutral deadzone signals tier-boundary territory |
| `position_vs_flip` (above_flip / below_flip / at_flip / unknown) | Dealer-metrics pipeline via MCP | The spot-vs-flip location; the near-flip-zone source (the `at_flip` value is the near-flip band) |
| `confidence` (high / medium / low / invalid) | Dealer-metrics pipeline via MCP | The dealer data-quality field; keys the dealer-trust behavioral contract directly (trusted high/medium → full; low → floor; invalid → drop the ticker layer) — there is no separate derived dealer-status |
| Freshness timestamp | Dealer-metrics pipeline via MCP | Compared to the pipeline's freshness window to determine whether the reading is current or stale |

DEALER reads these fields as delivered; it does not recompute any of them, does not interpolate when a field is missing, and does not reach for stale prior values when a current field is degraded.

**Where DEALER outputs flow downstream.**

| Output | Consumed by | What the downstream file does with it |
|---|---|---|
| DGPI tier (strongly supportive / moderately supportive / near-neutral / weakening / hostile) — per ticker | `RISK_v4.0.md`, `SIGNAL_v4.0.md` | Narrows the sizing band within the Wyckoff ceiling, **read relative to the position's direction**: a tier supportive of the position's direction earns top-of-band, an adverse tier earns floor (for a long put the tiers mirror — the per-ticker bearish-mirror band, Appendix); SIGNAL's dealer-timing veto reads the same tier + flip-zone direction-relative |
| DGPI tier — for SPY (macro layer) | `KAPMAN_GUARDRAILS_v4.0.md` | Combined with SPY flip distance to determine hostile-macro refusal |
| Flip-zone classification (well above / near-flip / well below) — per ticker | `RISK_v4.0.md` | Refines sizing band within the DGPI tier; near-flip triggers the one-tier step-down |
| Flip-zone classification — for SPY | `KAPMAN_GUARDRAILS_v4.0.md` | The "SPY below flip" half of the hostile-macro definition; near-flip SPY triggers the macro-level size step-down |
| Near-flip flag (boolean, per ticker including SPY) | `RISK_v4.0.md`, `KAPMAN_GUARDRAILS_v4.0.md` | RISK applies the one-tier step-down to the selected band; GUARDRAILS enforces that the step-down is applied and not silently relaxed |
| Hostile-macro flag (boolean, SPY-derived) | `KAPMAN_GUARDRAILS_v4.0.md` | Triggers the **bullish** long-premium refusal and the eligible-set redirect (long puts / put debit spreads as the directionally-aligned structures, plus CSPs, hedges, LEAPs) |
| Call/put wall levels (per ticker) | `PASS2_VALIDATION_v4.0.md`, `REPORT_FORMAT_v4.0.md` | PASS2 informs structure selection (avoid paying premium against a near-strike wall); REPORT_FORMAT renders the walls in the rationale where relevant |
| Dealer `confidence` (high / medium / low / invalid) — per ticker | `PASS2_VALIDATION_v4.0.md`, `RISK_v4.0.md`, `REPORT_FORMAT_v4.0.md` | PASS2 may drop a candidate when `confidence` is `invalid` and chain quality is also degraded; RISK reads `low` as floor-of-band; REPORT_FORMAT surfaces the confidence in the data-quality section |
| Stale-data flag (per ticker) | `RISK_v4.0.md`, `REPORT_FORMAT_v4.0.md`, `KAPMAN_GUARDRAILS_v4.0.md` | RISK drops the affected ticker dealer layer (same as `invalid` confidence); GUARDRAILS treats stale SPY as the conservative macro read; REPORT_FORMAT surfaces the *"Stale dealer data"* label with timestamp |
| GEX slope qualifier | `REPORT_FORMAT_v4.0.md` | Rendered as part of the rationale text where it materially refines the regime read; not a standalone field |

**Entry point for every dealer regime read.** Before consuming dealer regime for sizing or gating, four conditions must hold in the working context:

1. The MCP dealer-metrics fields for the ticker (and for SPY, for macro reads) have been fetched in the current session.
2. The freshness timestamps are within the pipeline's defined window — stale readings degrade the layer they affect rather than being silently consumed.
3. The emitted `confidence` is read as delivered — `high`, `medium`, `low`, or `invalid` — and weighted accordingly. Degraded reads are not laundered into confident reads.
4. The macro layer is resolved against SPY before the ticker layer is consulted. The fixed ordering is non-negotiable absent an explicit override.

If any condition fails, the affected layer reads as absent (for ticker) or as the conservative default (for macro), and the report surfaces the gap explicitly. A dealer regime read on incomplete data is a guardrail violation, not a DEALER violation — but the failure surfaces in the report as a degraded-confidence or no-regime output.

**Cross-references this file expects to be honored.**

- `KAPMAN_GUARDRAILS_v4.0.md` — owns the behavioral consequence of hostile macro (the long-premium refusal) and the override discipline. DEALER provides the trigger conditions; GUARDRAILS owns what happens when those conditions are met.
- `RISK_v4.0.md` — consumes DGPI tiers, flip-zone classifications, and the near-flip flag as sizing inputs. RISK does not re-derive any dealer regime; it reads DEALER's output and converts to a sizing band.
- `WYCKOFF_v4.0.md` — sets the sizing-band ceiling that DEALER's ticker layer narrows within. DEALER cannot promote a setup beyond what Wyckoff has authorized.
- `VOLATILITY_v4.0.md` — runs in parallel with DEALER; both feed RISK. DEALER does not consume volatility regime, and volatility does not consume dealer regime, but both layer onto the same sizing decision downstream.
- `PASS2_VALIDATION_v4.0.md` — uses dealer `confidence` and wall levels during structure validation. PASS2 owns chain-quality categorization (full / limited / weak) which is a distinct dimension from dealer `confidence` (high / medium / low / invalid) — the two can co-occur in any combination and both must be honored.
- `REPORT_FORMAT_v4.0.md` — renders DEALER's outputs (tier label, flip zone, walls, dealer confidence, stale-data flag, refresh prompt) into the report. DEALER does not own report formatting; it owns what the report has to say about regime.
- `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming) — owns every formula, filter threshold, weighting tier, slope window, confidence cutoff, and runtime default that produces the inputs DEALER reads. The runtime DEALER file is silent on all of these by design.

**When DEALER is silent.** DEALER does not own:

- Pipeline computation. The formulas for net GEX, strike-level GEX, gamma flip interpolation, wall weighting, slope, DGPI, position class, and confidence resolution all live in the engineering-only pipeline reference. The runtime reads outputs; it does not derive them.
- Filter thresholds. DTE windows, open-interest minimums, volume minimums, max moneyness, and similar pipeline parameters are engineering concerns and do not appear in this file.
- Pipeline defaults. The walls-top-n value, the slope-range percentage, the contract multiplier, and other backend defaults are engineering concerns.
- Chain-depth / OI cutoffs that produce the `confidence` rating. The runtime consumes the rating, not the count.
- Chain-quality categorization (full / limited / weak as it relates to executable contract depth). That is PASS2's domain. DEALER's `confidence` (high / medium / low / invalid) measures data depth for the dealer-metrics calculation specifically and is not the same thing as PASS2's executable chain quality.
- Refresh orchestration. The runtime does not initiate refreshes; that is operator-driven.
- Per-ticker historical comparisons (e.g., "DGPI is unusually negative for this name relative to its 6-month range"). The pipeline delivers point-in-time values; comparative analysis is operator work, not runtime work.

A dealer-regime question that doesn't fit one of the rules above is a question DEALER does not govern.

## Legacy anchors (for legend citations and back-compat)

> **Historical note (dealer-contract reconciliation, 2026-06-28).** The anchors below (esp. `DEALER_011`/`DEALER_012`/`DEALER_013`) describe a v2.3 pipeline classifier that resolved a `FULL/LIMITED/INVALID` "dealer-status" label. That derived label is **superseded**: neither live producer (kapman-polygon-mcp-v2, kapman-schwab-MCP) emits it — both emit a `confidence` field (`high`/`medium`/`low`/`invalid`), and the runtime now keys its dealer-trust behavior directly on that `confidence` (trusted `high`/`medium` → full; `low` → floor-of-band; `invalid` → drop the ticker layer), per § Operational heuristics ("The emitted `confidence` is taken at face value") and the Appendix "Dealer-confidence behavioral contract." The anchors are preserved **verbatim** for legend/back-compat; where they say `FULL/LIMITED/INVALID dealer-status`, read it as the `confidence` contract above. The signed-DGPI tier cutpoints likewise moved from a hardcoded 20/50 to the producers' 10/30/60 (named in `SYSTEM_PARAMS_v4.0.md`).

**DEALER_001** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The v2.3 contract-filtering thresholds (`dte <= 90`, `open_interest >= 100`, `volume >= 1`, gamma present) are pipeline data-quality controls applied before any dealer metric is computed. They have no LLM runtime effect — the runtime consumes the filtered output, never the raw chain — and are preserved in the engineering-only pipeline reference rather than in this file. Body-text references in legacy report legends (e.g., "Rules applied: DEALER_001") remain valid; the legend entry resolves to the engineering-only destination, and the runtime behavioral consequence the legend implies (that downstream metrics are trustworthy because contracts were filtered) is captured here under § Operational heuristics, "Data quality labels are taken at face value."

**DEALER_002** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The per-contract GEX formula (`gex = gamma * open_interest * spot^2 * 0.01 * contract_multiplier`, with call-side sign inversion) is pipeline computation; the runtime never derives per-contract GEX and never sees the unrolled formula. Preserved in engineering-only for back-compat with legacy report legends and for engineering maintenance of the pipeline.

**DEALER_003** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The strike-level GEX aggregation rule (additive across contracts at the same strike) is pipeline computation. Runtime consumes the strike ladder as a delivered input to flip and slope; it does not aggregate strike-level GEX itself.

**DEALER_004** → § Operational heuristics, "Spot's position relative to the flip dominates DGPI in the macro layer" and "Near-flip is a behavioral zone, not a single line"; computation portion to `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The v2.3 anchor combined the *interpretation* of the gamma flip as a regime-changing boundary with the *computation* of the flip level by zero-cross interpolation. The interpretation — that the flip marks where dealer hedge behavior changes regime — is load-bearing for the runtime and is preserved here as the spot-vs-flip dominance heuristic and the near-flip zone heuristic. The interpolation computation belongs to the pipeline and is preserved in engineering-only.

**DEALER_005** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). Wall candidate filtering (contract-type match, positive OI, non-null gamma, `abs(strike-spot)/spot <= 0.2`) is pipeline preprocessing for wall ranking. Runtime consumes the filtered wall list as delivered.

**DEALER_006** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The tiered moneyness weighting for wall ranking (1.0 / 0.7 / 0.4 / 0.2 across the four moneyness bands) is pipeline computation. The behavioral consequence — that walls reflect proximity-weighted significance and should be read as such — is captured here under § Operational heuristics, "Walls are reference levels, not entry triggers," without exposing the specific weight values.

**DEALER_007** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). Wall ranking sort (descending weighted GEX, strike tie-break) and top-N truncation (default `top_n = 3`) are pipeline output formatting. Runtime consumes the ranked, truncated list as delivered.

**DEALER_008** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The GEX slope formula (`slope = (upper_gex - lower_gex) / price_range` over `±2%` of spot) is pipeline computation. The behavioral consequence — that slope refines the DGPI tier read as a directional indicator of hedging pressure change around current price — is captured here under § Operational heuristics, "GEX slope is a confirmation signal, not a primary read."

**DEALER_009** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming) for the formula; § Principle and § Operational heuristics, "DGPI tier names are a vocabulary, not a scoring system" for the runtime semantics. The DGPI formula itself — signed log-scaled net GEX, slope multiplier with `±0.3` clamp, optional IV-rank weighting, output clamp to `[-100, 100]` — is pipeline computation and is preserved in engineering-only with no runtime exposure. The runtime contract is that DGPI arrives bounded to roughly ±100 with a defined sign convention; the tier mapping that converts that score into runtime regime vocabulary is owned by this file and lives in the Appendix.

**DEALER_010** → § Operational heuristics, "DGPI tier names are a vocabulary, not a scoring system" and § Appendix; computation portion to `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The v2.3 position-class threshold (`|net_gex| < 1,000,000` → neutral; positive → long_gamma; negative → short_gamma) is pipeline classification of net GEX into a categorical label. Runtime reads position_class as a delivered label and cross-references it with DGPI tier for boundary detection — a position-class flip near the neutral deadzone signals tier-boundary territory. The numeric `1,000,000` threshold is a pipeline parameter and lives in engineering-only; the *use* of position_class as a runtime cross-check is preserved here as part of the DGPI tier vocabulary heuristic.

**DEALER_011** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The confidence-level classifier (contracts-with-gamma 5/10 cutoffs, total OI ≥ 1000 for `high`, downgrades to `medium`/`low`/`invalid` below those bounds) is pipeline data-depth assessment. Runtime consumes the resulting confidence label only as input to the FULL/LIMITED/INVALID dealer-status resolution and does not see the raw cutoffs. Preserved in engineering-only.

**DEALER_012** → § Operational heuristics, "Data quality labels are taken at face value"; computation portion to `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The v2.3 anchor defined how the FULL / LIMITED / INVALID dealer-status label is resolved from eligible-options count, GEX validity, position-class validity, and confidence level. The numeric cutoffs (FULL requires `eligible_options >= 25`; LIMITED requires `>= 1`) are pipeline parameters and live in engineering-only. The runtime vocabulary (FULL / LIMITED / INVALID) and its behavioral contract — FULL permits full sizing band and full hostile-macro behavior; LIMITED restricts to floor-of-band; INVALID drops the ticker layer entirely — are owned by this file and are load-bearing for RISK and PASS2 downstream.

**DEALER_013** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The v2.3 secondary metadata-status classifier (with `min_eligible_threshold = 5` for the metadata-layer FULL/LIMITED resolution, distinct from the primary classifier's `25`) is a pipeline-internal payload-quality annotation. The runtime sees only the resolved status label and does not distinguish between primary and metadata classifiers — both resolve to the same FULL/LIMITED/INVALID vocabulary at the runtime boundary. Preserved in engineering-only as documentation of the pipeline's two-layer classification scheme.

**DEALER_014** → `engineering_only/DEALER_PIPELINE_v4.0.md` (forthcoming). The pipeline runtime defaults (`walls_top_n = 3`, `gex_slope_range_pct = 0.02`, `max_moneyness = 0.2`) are pipeline parameters governing model behavior across runs. They have no LLM runtime effect — the runtime consumes the pipeline's output regardless of which defaults produced it — and are preserved in engineering-only for engineering maintenance and reproducibility.

## Appendix — formulas and reference tables

**DGPI tier bands.** Delivered DGPI is a **signed** score bounded to ±100 (both producers compute `sign(net_gex) · log10(|net_gex|+1) · 10`, slope- and IV-adjusted; kapman-polygon-mcp-v2 `calculate_dgpi`, kapman-schwab-MCP `dealer_gamma_pressure_index`) — **positive = supportive** (dealers dampen / support the tape), **negative = hostile**. The runtime reads the score into one of five tiers using the magnitude cutpoints `DGPI_NEUTRAL_BAND` and `DGPI_STRONG_BAND` per `SYSTEM_PARAMS_v4.0.md` (currently 10 and 30 — the producer's 10/30/60 bands, matching the viewer header). Because the score is log-compressed, most liquid names read high-magnitude; the tier names are a regime vocabulary, not a precision scale. Boundary values resolve to the more conservative tier.

| DGPI band (current cutpoints) | Tier name | Macro layer consequence (SPY) | Ticker layer consequence (per-name, within Wyckoff ceiling) |
|---|---|---|---|
| ≥ +30 (≥ `DGPI_STRONG_BAND`) | Strongly supportive | Supportive macro; long-premium structures eligible | Top of sizing band |
| +10 to +30 | Moderately supportive | Supportive macro; long-premium structures eligible | Mid sizing band |
| -10 to +10 (\|DGPI\| < `DGPI_NEUTRAL_BAND`) | Near-neutral | Neutral macro; long-premium eligible but spot-vs-flip dominates the read | Mid-to-floor sizing band, weighted by spot-vs-flip |
| -30 to -10 | Weakening | Cautious macro; long-premium eligible only when SPY is comfortably above flip | Floor of sizing band |
| ≤ -30 (≤ -`DGPI_STRONG_BAND`) | Hostile (when combined with SPY below flip — see hostile macro composite below) | Hostile macro refusal owned by GUARDRAILS when combined with below-flip | Floor of sizing band; combined with markdown Wyckoff phase, long-premium band closes entirely |

The cutpoints are the named `DGPI_NEUTRAL_BAND` / `DGPI_STRONG_BAND` parameters in `SYSTEM_PARAMS_v4.0.md` (currently 10 / 30 — the producer's signed-DGPI bands; the producer's >60 "extreme" band folds into the strong tier and is not surfaced as a separate KB tier); update that file to recalibrate. The signed DGPI is produced identically at Pass-1 (kapman-polygon-mcp-v2 — what the viewer shows and the §A1 handoff exports) and Pass-2 (kapman-schwab-MCP) — same sign convention and ±100 scale — but the two compute over different option universes, so the **value is re-derived at Pass 2, not carried; the Pass-2 read agrees with Pass-1 by tier and direction, never by exact value.**

**Direction-relative reading and the per-ticker bearish-mirror band.** The tier names above are framed for a **long** (bullish) position. For a **bearish** position (a long put), the same delivered DGPI maps to the **mirror** tier — strongly supportive (≥ +30, ≥ `DGPI_STRONG_BAND`) for a long is *strongly adverse* for a long put, hostile (≤ -30, ≤ -`DGPI_STRONG_BAND`) for a long is *strongly supportive* for a long put, and the intermediate tiers mirror correspondingly; the spot-vs-flip read flips identically (well above flip ↔ well below flip). The cutpoints are unchanged — only the sign is read against the position's direction. The **per-ticker bearish-mirror DGPI band** (the ticker dealer regime *adverse to a bearish position*, referenced by SIGNAL's dealer-timing veto and RISK's dealer-narrowing) is therefore **DGPI ≥ +30 (≥ `DGPI_STRONG_BAND`) with spot well above the ticker's flip** — the exact sign-flipped mirror of the bullish per-ticker hostile band (DGPI ≤ -30 with spot well below flip). This mirror is a **ticker-layer** definition; the macro hostile-macro composite below stays bullish-scoped (no mirror macro composite refuses a long put — a supportive macro simply makes the per-ticker bearish-mirror band the relevant stability check).

**Hostile macro composite.** Hostile macro is a two-condition composite read from SPY only:

| Condition | Definition |
|---|---|
| SPY spot below gamma flip | Spot price strictly below the delivered SPY gamma flip level, comfortably outside the near-flip zone (i.e., Spot < SPY_flip × 0.995) |
| SPY DGPI in the hostile tier | SPY DGPI ≤ `HOSTILE_MACRO_DGPI_MAX` per SYSTEM_PARAMS (currently -30). Because DGPI is log-compressed, SPY's \|DGPI\| is almost always large, so this condition is **sign-dominated** — it fires whenever SPY DGPI is meaningfully negative, and the threshold mainly excludes a near-neutral SPY. |

When **both** conditions hold, hostile macro is active and triggers the **bullish** long-premium refusal owned by `KAPMAN_GUARDRAILS_v4.0.md` (long calls and call debit spreads refused; long puts and put debit spreads are the directionally-aligned eligible redirect — a hostile, falling macro tape is the regime a long put is aligned with, not refused by). When only one condition holds (SPY below flip with DGPI > -30, or SPY above flip with DGPI ≤ -30), the macro layer reads as mixed and is treated as the more conservative of the two readings per § Operational heuristics. The composite is SPY-specific and bullish-scoped; there is deliberately **no mirror "supportive-macro refuses long puts" composite** — a supportive macro does not gate bearish entries, it simply makes the per-ticker bearish-mirror DGPI band (above) the relevant ticker-layer stability check, consumed by SIGNAL's dealer-timing veto and RISK's narrowing. Ticker-level versions of the hostile composite are read into the ticker sizing band but do not by themselves trigger refusal.

**Near-flip zone.** Symmetric percentage band around the delivered gamma flip level, applied identically to SPY (for macro) and to per-name tickers (for ticker layer):

| Zone | Definition |
|---|---|
| Well above flip | Spot > flip × 1.005 (i.e., more than 0.5% above flip) |
| Near-flip | flip × 0.995 ≤ Spot ≤ flip × 1.005 (i.e., within ±0.5% of flip) |
| Well below flip | Spot < flip × 0.995 (i.e., more than 0.5% below flip) |

The 0.5% band is anchored to spot, which scales the zone correctly across SPY at any price and across tickers at any price; it is the `at_flip` band both producers use. The zone is symmetric: just above the flip and just below it are both unstable. Near-flip triggers the one-tier sizing step-down enforced by RISK and required by GUARDRAILS; it is not a refusal. The mechanical step-down ladder (which selected band steps down to which) is owned by `RISK_v4.0.md` and lives there. The `NEAR_FLIP_BAND_PCT` (0.5%) value is defined as a named parameter in `SYSTEM_PARAMS_v4.0.md`; update that file when recalibrating the band.

**Dealer-confidence behavioral contract.** Both producers emit a `confidence` field (`high` / `medium` / `low` / `invalid`) rating the trustworthiness of the dealer-metrics computation (kapman-polygon-mcp-v2 `determine_confidence` from chain depth; kapman-schwab-MCP from flip-reliability + chain depth). There is **no `FULL/LIMITED/INVALID` "dealer-status" field — neither producer emits one**; the runtime keys its dealer-trust behavior directly on the emitted `confidence`:

| Emitted `confidence` | Runtime behavioral consequence |
|---|---|
| `high` or `medium` (trusted) | Full sizing band per RISK; full hostile-macro refusal behavior when applicable; walls and slope read as usable signals |
| `low` | Sizing restricted to floor-of-band regardless of DGPI tier; walls reported but not used to adjust structure; rationale acknowledges the low-confidence read |
| `invalid` | Ticker dealer layer reads as absent; the SPY macro gate still applies; no per-name DGPI tier consumed |

`high` and `medium` are treated identically (trusted, full behavior) — so a ticker that previously floored under a "medium-confidence" read is now sized at full band. The chain-depth thresholds the producers use to assign `confidence` are pipeline parameters (engineering-only). (Provenance note: the viewer's Pass-1 `dealer_confidence` and the Schwab Pass-2 `confidence` are the same four-value field from the two producers — Pass-1 is triage context, Pass-2 is the live re-rated read; see `PASS1_SCREENING_v4.0.md` §A1.)

**Stale-data label semantics.** When delivered dealer-metrics freshness falls outside the pipeline's freshness window, a stale flag accompanies the reading and carries the following runtime behavioral contract:

| Affected layer | Runtime behavioral consequence | Report surfacing |
|---|---|---|
| SPY (macro) | Macro gate restricted to conservative read — long-premium structures restricted by default until fresh data, same as near-flip behavior; operator override per GUARDRAILS available | *"Stale dealer data — SPY, last refreshed [timestamp]"* in data-quality section; refresh prompt |
| Per-name ticker | Ticker dealer layer reads as absent (same as `invalid` confidence — the layer is dropped, not floored); macro gate via SPY still applies | *"Stale dealer data — [ticker], last refreshed [timestamp]"* in data-quality section; refresh prompt |

The runtime does not initiate refreshes; refresh is operator-driven. The freshness window itself is a pipeline parameter and lives in engineering-only.

**Gamma-regime (`position`) cross-check.** Both producers emit `position` ∈ {`long_gamma`, `short_gamma`, `neutral`} (the dealer **gamma regime**, derived from net-GEX sign and a magnitude threshold) — distinct from `position_vs_flip` ∈ {`above_flip`, `below_flip`, `at_flip`, `unknown`} (the **spot-vs-flip location**, the near-flip-zone source). `position` is consumed as a runtime cross-check against the DGPI sign/tier, not as an independent regime read; `position_vs_flip` feeds the flip-zone read:

| Observation | Runtime interpretation |
|---|---|
| `position` = long_gamma AND DGPI ≥ +`DGPI_NEUTRAL_BAND` | Tier read well-grounded; supportive read is stable (both reflect positive net-GEX) |
| `position` = short_gamma AND DGPI ≤ -`DGPI_NEUTRAL_BAND` | Tier read well-grounded; weakening/hostile read is stable |
| `position` = neutral AND \|DGPI\| < `DGPI_NEUTRAL_BAND` | Tier read well-grounded; near-neutral read is stable |
| `position` and DGPI sign disagree (e.g., `position` = neutral but DGPI = +35) | Tier-boundary territory; read the DGPI tier into the more conservative adjacent tier |

`position` and DGPI both derive from net-GEX sign, so they normally agree; a disagreement is a near-threshold signal. The producers' net-GEX magnitude threshold for `neutral` is a pipeline parameter (engineering-only).

**Vocabulary alignment with data-quality labels.** Standard report surfacing for DEALER-owned data conditions, aligned with the data-quality vocabulary in `KAPMAN_GUARDRAILS_v4.0.md`:

| Condition | Report label | When used |
|---|---|---|
| Trusted dealer confidence (high/medium), fresh data | (No label required; regime reported as resolved tier) | Normal case |
| Low dealer confidence | *"Weak dealer signal — low confidence"* | Emitted `confidence` = `low` |
| Invalid dealer confidence | *"Dealer regime not assessed — invalid confidence"* | Emitted `confidence` = `invalid` |
| Stale dealer data | *"Stale dealer data — [ticker], last refreshed [timestamp]"* | Freshness window exceeded |
| Near-flip zone active (ticker) | *"Near-flip — sizing reduced one tier"* | Spot within ±0.5% of ticker flip |
| Near-flip zone active (SPY) | *"Near-flip macro — sizing reduced one tier across eligible set"* | Spot within ±0.5% of SPY flip |
| Hostile macro active | *"Hostile macro — bullish long-premium refused; eligible set: long puts / put debit spreads, CSPs, hedges, LEAPs"* | Both hostile-macro composite conditions met |
| Mixed macro | *"Mixed macro — conservative read"* | One but not both hostile-macro conditions met |

**Metric vocabulary reference.** The metrics this file consumes, named consistently across the KB:

| Term | Definition | Owner of definition |
|---|---|---|
| Net GEX | Aggregate signed gamma exposure across all eligible contracts for a ticker, in pipeline units | engineering-only (formula) |
| Gamma flip level | The strike at which cumulative GEX crosses zero, interpolated between adjacent strikes | engineering-only (formula); this file (interpretation) |
| Call wall, put wall | Top-N strike levels where dealer call-side / put-side hedging is concentrated, ranked by proximity-weighted GEX | engineering-only (formula); this file (interpretation) |
| GEX slope | Local gradient of GEX across a ±2% strike window around spot, expressed as units per dollar | engineering-only (formula); this file (interpretation as a confirmation signal) |
| DGPI (Dealer Gamma Pressure Index) | **Signed** ±100 composite (`sign(net_gex)·log10(\|net_gex\|+1)·10`, slope- and IV-adjusted); positive = supportive, negative = hostile | producers (formula); this file (tier vocabulary and bands) |
| `position` (gamma regime) | Categorical label (long_gamma / short_gamma / neutral) = dealer gamma regime, from net-GEX sign + magnitude threshold | producers (threshold); this file (cross-check usage) |
| `position_vs_flip` | Categorical label (above_flip / below_flip / at_flip / unknown) = spot vs gamma flip; the near-flip-zone source | producers; this file (flip-zone interpretation) |
| `confidence` | Categorical label (high / medium / low / invalid); the dealer data-quality field both producers emit; keys the dealer-trust behavioral contract (trusted high/medium → full; low → floor; invalid → drop) | producers (cutoffs); this file (behavioral contract) |
| Macro layer / ticker layer | Runtime distinction between SPY-derived dealer regime (macro) and per-name dealer regime (ticker) | this file |
| Near-flip zone | Symmetric ±0.5%-of-spot band (`NEAR_FLIP_BAND_PCT`) around the gamma flip level where regime is treated as unstable | this file |
| Hostile macro | Two-condition SPY composite (SPY below flip AND SPY DGPI ≤ `HOSTILE_MACRO_DGPI_MAX`, currently -30) that triggers the **bullish** long-premium refusal; long puts are its directionally-aligned redirect, not a refused structure | this file (composite); GUARDRAILS (refusal behavior) |
| Bearish-mirror DGPI band | The per-ticker dealer regime adverse to a bearish (long-put) position — the sign-flipped mirror of the bullish per-ticker hostile band (DGPI ≥ +30, ≥ `DGPI_STRONG_BAND`, with spot well above the ticker's flip); the DGPI tier vocabulary read direction-relative | this file |
| Stale dealer data | Reading older than the pipeline's freshness window | engineering-only (window); this file (behavioral consequence) |
