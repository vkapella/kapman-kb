---
system: KapMan
doc_type: principle
kb_version: 3.0.0-alpha
file_last_updated: 2026-05-11
status: draft
tier: T1
---

# VOLATILITY

## Principle

Volatility regime is a market-state signal read from delivered MCP fields, not a quantity the runtime derives. The volatility-metrics MCP tool surface delivers per-ticker average IV, IV percentile, IV rank, IV dispersion, IV skew, term-structure level and slope, and a processing-confidence label per ticker, computed by the data provider from filtered option-chain data. The runtime's job is to interpret those outputs as a regime — and to enforce the source-authority rules that govern *which* delivered IV value is trustworthy for *which* decision — not to re-derive the metrics: the formulas, window choices, weighting schemes, and tool-surface parameters that produce the numbers are documented in the engineering-only MCP reference for cross-checking against tool documentation. The governing judgment is that volatility regime affects structure choice and sizing in two distinct ways, and the runtime must keep them separate. The first is the IV/HV ratio, which compares forward-looking implied volatility to recent realized volatility on the same name and answers a structure-choice question: when implied vol is materially richer than realized, long-premium structures are expensive and a spread is mandatory; when implied is roughly in line with or cheaper than realized, naked long-premium is appropriate. The second is the IV rank tier, which places current IV against the same ticker's own recent history and answers a regime question: low-rank tickers are in a quiet vol environment that favors patient debit entries, elevated-rank tickers are in a stretched vol environment that favors premium-selling structures, and extreme-rank tickers are in a regime where any structure must account for an imminent mean-reversion risk. These two readings can disagree — a ticker with elevated IV rank and a near-1 IV/HV ratio is in a high-vol regime where realized has already caught up to implied — and when they disagree, the runtime reports both rather than collapsing them. The volatility regime is per-ticker, not market-wide; the v3.0 KB does not maintain a separate macro volatility layer, and broad-market vol context (VIX, VVIX) when relevant is consumed through DEALER's SPY-derived regime, not through VOLATILITY. IV source authority is the second load-bearing concern: when MCP delivers IV from multiple providers (Polygon `avg_iv`, Schwab ATM chain values, derived theoretical values), the source-authority rules govern which value is consumed in which pass and which fields are refused outright — Polygon `avg_iv` is the canonical source for Pass 1 directional screening, Schwab ATM chain per-contract values are the canonical source for Pass 2 spread-decision IV/HV calculation, and Schwab's `theoreticalVolatility` field is never read because it carries a hardcoded sentinel value rather than market IV. Data depth is a precondition: when the chain underlying the volatility metrics is thin or the IV history is short, the FULL/LIMITED/INVALID-equivalent label delivered by the tool surface is taken at face value, and weak-confidence volatility signals are not laundered into confident regime calls. As with dealer regime, the runtime does not paper over degraded sourcing by interpolating, reaching for stale prior readings, or silently substituting one source's value when the canonical source for the current pass is unavailable.

## Operational heuristics

**The IV/HV ratio and the IV rank tier answer different questions and are read separately.**
The IV/HV ratio compares forward IV to recent realized vol on the same name; it is a structure-choice signal. The IV rank tier places current IV against the same ticker's own history; it is a regime-context signal. The runtime does not collapse them into a single composite — a ticker can have a moderate IV/HV ratio while sitting in an elevated IV rank tier (recent realized has been high, and forward IV is roughly tracking it at an elevated absolute level), and that combination is legitimately different from a ticker with the same IV/HV ratio in a low IV rank tier. The two readings are surfaced separately in the report.

**IV/HV bands govern structure choice and are anchored to the 1.0 line.**
An IV/HV ratio comfortably below 1.0 means forward IV is cheaper than recent realized — long-premium structures are appropriate, and naked long calls or puts are acceptable subject to other regime gates. An IV/HV ratio in a neutral band around 1.0 means forward IV is roughly in line with realized — long-premium remains eligible but spreads are preferred as a sizing-efficiency choice. An IV/HV ratio comfortably above 1.0 means forward IV is materially richer than realized — long-premium is expensive and a vertical spread is mandatory for new directional entries. The specific band boundaries live in the Appendix; the principle is that the further IV departs upward from realized vol, the more aggressively the runtime defends against paying for that premium.

**IV rank tier names are a vocabulary, not a scoring system.**
Delivered IV rank is bounded to [0, 100] by the tool surface. The runtime reads the value into one of four tiers — low, moderate, elevated, extreme — using bands in the Appendix. The tier name is what downstream files consume; the raw number appears in the report for transparency but doesn't drive behavior beyond tier resolution. As with DGPI tiers, a value sitting on a tier boundary resolves into the more conservative adjacent tier — boundary cases are interpreted defensively because the bands describe regime, not precision.

**IV rank tier biases structure preference rather than gating directly.**
Low-rank tickers favor patient debit entries (naked long calls or puts where IV/HV permits) because the regime offers room for IV to expand into the position. Moderate-rank is neutral on premium-selling versus premium-buying; structure choice falls through to IV/HV. Elevated-rank tilts toward premium-selling structures (CSPs and credit spreads) and away from naked long-premium even when IV/HV allows it, because the rank reading signals that current IV is stretched relative to the name's own history. Extreme-rank tickers require explicit acknowledgment of mean-reversion risk on any structure — short premium positions are exposed to vol crush mechanics, long premium positions are exposed to vol expansion failure — and entries in this tier surface a *"Stretched IV"* annotation regardless of structure direction.

**IV source authority is pass-specific and non-negotiable.**
Pass 1 directional screening uses Polygon `avg_iv` delivered via the canonical single-symbol and multi-symbol options-metrics endpoints. Pass 2 spread-decision IV/HV calculation uses Schwab ATM chain per-contract IV at the nearest-to-money strike. Schwab's `theoreticalVolatility` field is never read in either pass — it carries a hardcoded sentinel that does not represent market IV, and consuming it would silently corrupt every downstream regime read. Polygon `avg_iv` carries a small structural positive bias relative to Schwab ATM (roughly +1 to +4 percentage points) that is acceptable for Pass 1 directional classification but unacceptable as the sole input to a Pass 2 spread-mandate decision. The pass-specific separation exists because each pass asks a different question of IV: Pass 1 asks "is this ticker's IV roughly in a useful range," Pass 2 asks "is this ticker's forward IV rich enough relative to realized that the spread mandate triggers."

**Source-substitution is never silent.**
When the canonical source for the current pass is unavailable, the runtime does not silently fall back to the other pass's canonical source. A Pass 2 IV/HV calculation that cannot reach a valid Schwab ATM IV does not substitute Polygon `avg_iv` and proceed; it surfaces the gap and the structure decision is reported as *Needs chain validation* per the GUARDRAILS data-quality vocabulary. A Pass 1 screening that cannot reach Polygon `avg_iv` reports the ticker with a *Volatility regime not assessed* annotation rather than reaching for Schwab data that was sized and filtered for a different question.

**Volatility-status labels are taken at face value.**
The FULL / LIMITED / INVALID label delivered by the volatility tool surface governs how much weight the regime read carries downstream. FULL data permits full structure-choice and sizing behavior. LIMITED data restricts long-premium structures to floor-of-band sizing per RISK regardless of what IV/HV reads, and the report acknowledges the data limitation in the rationale. INVALID data means the volatility regime is not read at all for that ticker — the ticker layer is treated as absent, downstream sizing reads as if no IV signal exists, and the spread-mandate decision defaults to "spread required" because the absence of a confident IV/HV reading cannot authorize the cheaper naked structure. The runtime does not interpolate, does not substitute stale prior values, and does not infer FULL conditions from partial tool-surface output.

**IV history depth is a precondition for IV rank and IV percentile.**
The tool surface requires a minimum history before computing IV rank or IV percentile; when history is below the floor, both values are delivered as null and accompanied by an `insufficient_iv_history` diagnostic. The runtime treats null IV rank as no IV rank tier reading — not as a "low" tier. Structure choice in this case falls back to IV/HV alone, and the report surfaces the gap as *"IV rank not available — limited history"*. Reaching for a stale prior IV rank from a different session is not permitted; the runtime consumes only the current-session delivered value.

**Term-structure outputs are context, not gates.**
Delivered term-structure level (back-month IV minus front-month IV) and slope (level per DTE) are read as context that refines the runtime's interpretation of the IV rank tier and the IV/HV ratio. Steep backwardation (back-month IV materially below front-month) reinforces an elevated-IV-rank reading by indicating that the elevated front-month IV reflects near-term event premium rather than persistent regime change. Steep contango (back-month IV materially above front-month) cuts the other direction — an elevated front-month IV alongside steep contango suggests a regime shift toward sustained higher vol rather than a transient event spike. Term-structure does not by itself authorize or block a setup; it qualifies the rationale text.

**Skew and dispersion are surfaced when the structure is asymmetric.**
Delivered IV skew (put IV minus call IV, scaled to percentage points) and IV dispersion (population stddev across contracts) are read as context fields that surface in rationale text when they materially affect structure choice. Positive skew (put premium) is relevant when selecting between naked long calls (which become relatively cheaper) and naked long puts (which become relatively expensive). High dispersion signals that the chain's IV is unevenly distributed across strikes — a condition that can degrade the quality of the IV/HV reading itself and that the runtime acknowledges in the data-quality section. Neither skew nor dispersion is a primary gate.

**Stale readings degrade the layer; the runtime does not auto-refresh.**
Volatility metrics carry a freshness timestamp from the tool surface. When metrics fall outside the freshness window, the volatility layer for that ticker is degraded: stale readings are treated identically to INVALID for sizing and structure-choice purposes, and the report surfaces the staleness explicitly with a *"Stale volatility data"* label and a refresh prompt naming the affected ticker and last-refresh timestamp. The runtime does not initiate refreshes — refresh is operator-initiated — and does not infer that a stale supportive reading is "probably still supportive."

## Workflow integration

**Position in the document hierarchy.** VOLATILITY is tier T1 — a principle file. It owns the runtime interpretation of volatility regime: how delivered MCP fields translate into a structure-choice signal (IV/HV ratio) and a regime-context signal (IV rank tier), how the IV source-authority rules govern which delivered value is consumed in which pass, and what data quality means for trust in those readings. VOLATILITY does not compute its own inputs; the volatility-metrics MCP tool surface, documented in the engineering-only MCP reference, produces every number and label VOLATILITY consumes. VOLATILITY does not enforce sizing, does not refuse structures, and does not render output — those are downstream concerns owned by RISK, GUARDRAILS / SIGNAL, and the report layer respectively.

**Inputs VOLATILITY reads from MCP.**

| Field | Source | What VOLATILITY does with it |
|---|---|---|
| `avg_iv` (per ticker, Polygon-sourced for Pass 1) | Polygon MCP options-metrics tool surface | Read as the canonical Pass 1 IV value for directional screening; consumed by the IV rank tier read indirectly via the tool surface's IV rank computation |
| ATM chain per-contract IV at nearest-to-money strike (per ticker, Schwab-sourced for Pass 2) | Schwab MCP options chain tool surface | Read as the canonical Pass 2 IV input for the IV/HV ratio calculation that drives spread-mandate decisions |
| IV rank (per ticker, bounded [0, 100]) | Volatility-metrics MCP tool surface | Mapped to tier vocabulary (low / moderate / elevated / extreme) per Appendix bands |
| IV percentile (per ticker, bounded [0, 100]) | Volatility-metrics MCP tool surface | Read as a secondary regime-context field; surfaced in rationale alongside IV rank but not separately tier-mapped |
| IV/HV ratio (per ticker) | Volatility-metrics MCP tool surface (computed from Pass 2 Schwab ATM IV and provider-computed HV) | Mapped to band (cheap / neutral / elevated) per Appendix bands; drives the structure-choice decision consumed by SIGNAL |
| Term-structure level and slope (per ticker) | Volatility-metrics MCP tool surface | Read as context modifiers on the IV rank tier read; surface in rationale text when materially refining the regime call |
| IV skew (per ticker) | Volatility-metrics MCP tool surface | Read as asymmetry context surfaced in rationale when it materially affects directional structure choice (long calls vs. long puts) |
| IV dispersion (per ticker) | Volatility-metrics MCP tool surface | Read as a chain-quality context field; high dispersion surfaces in the data-quality section as a confidence qualifier on the IV/HV reading |
| Volatility-status label (FULL / LIMITED / INVALID) | Volatility-metrics MCP tool surface (resolved from processing status and confidence tiers) | Governs how much weight the volatility regime carries downstream; taken at face value |
| `insufficient_iv_history` diagnostic (boolean) | Volatility-metrics MCP tool surface | Signals that IV rank and IV percentile are delivered null; runtime falls back to IV/HV alone for structure choice and surfaces the gap in the report |
| Freshness timestamp | Volatility-metrics MCP tool surface | Compared to the tool surface's freshness window to determine whether the reading is current or stale |

VOLATILITY reads these fields as delivered; it does not recompute any of them, does not interpolate when a field is missing, and does not reach for stale prior values when a current field is degraded.

**Where VOLATILITY outputs flow downstream.**

| Output | Consumed by | What the downstream file does with it |
|---|---|---|
| IV/HV band (cheap / neutral / elevated) — per ticker | `SIGNAL_v3.0.md` (forthcoming) | Triggers the spread-mandate decision; elevated band → spread required; neutral → spread preferred; cheap → naked long-premium eligible |
| IV/HV band — secondarily | `RISK_v3.0.md` | Read alongside SIGNAL's structure choice to determine the sizing denominator (underlying-notional for naked, spread-risk for spread) |
| IV rank tier (low / moderate / elevated / extreme) — per ticker | `RISK_v3.0.md`, `PASS1_SCREENING_v3.0.md` (forthcoming), `PASS2_VALIDATION_v3.0.md` (forthcoming) | RISK reads tier as a sizing-band qualifier; PASS1 may filter candidates by tier; PASS2 reads tier into structure-validation context |
| IV rank tier | `REPORT_FORMAT_v3.0.md` | Rendered in the volatility regime field of the recommendation row; *"Stretched IV"* annotation surfaces for extreme tier |
| IV rank tier null (insufficient history) | `RISK_v3.0.md`, `REPORT_FORMAT_v3.0.md` | RISK falls back to IV/HV alone for sizing band; REPORT_FORMAT surfaces *"IV rank not available — limited history"* in the data-quality section |
| Volatility-status label (FULL / LIMITED / INVALID) — per ticker | `RISK_v3.0.md`, `PASS2_VALIDATION_v3.0.md`, `REPORT_FORMAT_v3.0.md` | RISK reads LIMITED as floor-of-band; PASS2 cross-references with chain quality to determine validation outcome; REPORT_FORMAT surfaces the label in the data-quality section |
| Stale-data flag | `RISK_v3.0.md`, `REPORT_FORMAT_v3.0.md`, `KAPMAN_GUARDRAILS_v3.0.md` | RISK applies the same restriction as INVALID for the affected ticker; GUARDRAILS treats stale as degraded data not to be laundered; REPORT_FORMAT surfaces the *"Stale volatility data"* label with timestamp |
| Term-structure qualifier | `REPORT_FORMAT_v3.0.md` | Rendered as part of the rationale text where it materially refines the regime read; not a standalone field |
| IV skew qualifier | `REPORT_FORMAT_v3.0.md` | Rendered in rationale when materially relevant to directional structure choice |
| IV dispersion qualifier | `REPORT_FORMAT_v3.0.md` | Surfaces in data-quality section when high enough to flag confidence concerns on the IV/HV reading |
| IV source-authority decision (Pass 1 source vs. Pass 2 source) | `PASS1_SCREENING_v3.0.md`, `PASS2_VALIDATION_v3.0.md`, `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` | PASS1 calls the canonical Pass 1 endpoint; PASS2 calls the canonical Pass 2 endpoint; MCP reference holds the specific tool-surface names and parameter shapes |

**Entry point for every volatility regime read.** Before consuming volatility regime for structure choice or sizing, four conditions must hold in the working context:

1. The MCP volatility-metrics fields for the ticker have been fetched in the current session using the canonical source for the active pass — Polygon `avg_iv` via the options-metrics endpoint for Pass 1, Schwab ATM chain per-contract IV for Pass 2.
2. The freshness timestamp is within the tool surface's defined window — stale readings degrade the layer rather than being silently consumed.
3. The volatility-status label is read as delivered — FULL, LIMITED, or INVALID — and weighted accordingly. Degraded labels are not laundered into confident reads.
4. The active pass is unambiguous. If a structure-choice decision is being made for a ticker that has not been routed through Pass 2 (and therefore has no Schwab ATM IV reading), the IV/HV band is reported as *Needs chain validation* and the structure decision defers to Pass 2 rather than being computed from Pass 1 data.

If any condition fails, the affected layer reads as absent and the report surfaces the gap explicitly. A volatility regime read on incomplete or wrong-pass data is a guardrail violation, not a VOLATILITY violation — but the failure surfaces in the report as a degraded-confidence or no-regime output.

**Cross-references this file expects to be honored.**

- `KAPMAN_GUARDRAILS_v3.0.md` — owns the honesty floor that prevents degraded IV signals from being laundered. VOLATILITY aligns its data-quality vocabulary with GUARDRAILS' labels (*Needs chain validation*, *Weak chain*, *Not provided*, *Limited liquidity*) and adds *"Stale volatility data"* and *"IV rank not available — limited history"* as VOLATILITY-specific extensions of the same vocabulary.
- `RISK_v3.0.md` — consumes IV/HV band and IV rank tier as sizing inputs. RISK does not re-derive any volatility regime; it reads VOLATILITY's output. The "elevated IV mandates spread" rule that RISK references is operationalized here as the IV/HV elevated band, and the consequence (spread-mandated sizing using spread-risk denominator) is RISK's to enforce.
- `DEALER_v3.0.md` — runs in parallel with VOLATILITY; both feed RISK. DEALER does not consume volatility regime, and VOLATILITY does not consume dealer regime, but DEALER's DGPI computation in the tool surface optionally consumes the same IV rank value that VOLATILITY surfaces as a runtime tier. The optional IV-rank weighting in DEALER's DGPI formula is tool-surface-internal and not a runtime cross-reference; the runtime sees DGPI as already-computed.
- `SIGNAL_v3.0.md` (forthcoming) — consumes the IV/HV band as the trigger for the spread-mandate decision. The named trigger formerly known as `iv_forbids_long_premium` is operationalized as "IV/HV band reads elevated"; SIGNAL owns the trigger's behavioral consequence (spread required for new directional entries), VOLATILITY owns the band definition.
- `PASS1_SCREENING_v3.0.md` (forthcoming) — consumes IV rank tier as a candidate filter input and consumes the volatility-status label for confidence weighting. PASS1 uses the Pass 1 IV source (Polygon `avg_iv`) per the source-authority rule.
- `PASS2_VALIDATION_v3.0.md` (forthcoming) — consumes the IV/HV band for structure validation and triggers the canonical Pass 2 IV source (Schwab ATM chain per-contract IV) for the IV/HV ratio calculation. PASS2's chain-quality categorization (full / limited / weak) and VOLATILITY's volatility-status label (FULL / LIMITED / INVALID) are distinct dimensions and both must be honored.
- `REPORT_FORMAT_v3.0.md` — renders VOLATILITY's outputs (IV rank tier, IV/HV band, volatility-status label, stale-data flag, refresh prompt, *"Stretched IV"* annotation, term-structure and skew qualifiers in rationale) into the report. VOLATILITY does not own report formatting; it owns what the report has to say about volatility regime.
- `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming) — documents the Polygon and Schwab volatility-metrics tool-surface contracts: field names, return shapes, freshness windows, formulas, window choices, weighting schemes, percentile methods, history lookbacks, confidence cutoffs, status thresholds, tool-surface endpoint names, and other tool-surface parameters that produce the inputs VOLATILITY reads. The runtime VOLATILITY file is silent on all of these by design — it consumes the MCP-delivered output, never the underlying mechanics.

**When VOLATILITY is silent.** VOLATILITY does not own:

- MCP tool-surface computation. The formulas for `avg_iv` (OI-weighted vs. arithmetic), IV percentile, IV rank, IV dispersion (stddev choice), IV skew, term-structure level and slope, and 25-delta IV retrieval all live inside the MCP data provider's implementation. The engineering-only MCP reference documents these for cross-checking against provider documentation. The runtime reads outputs; it does not derive them.
- HV computation. Historical volatility window choice, return-series construction, and HV-from-returns formula all live inside the MCP data provider's implementation and are documented in the engineering-only MCP reference. VOLATILITY consumes the resulting IV/HV ratio, not the HV value itself.
- MCP tool-surface cutoffs. Contract-count thresholds for FULL / LIMITED / INVALID resolution, tenor-coverage minimums, history-floor (`min_history_points`), and `DEFAULT_HISTORY_LOOKBACK` are MCP-internal parameters set by the data provider and do not appear in this file.
- MCP endpoint names and parameter shapes. The Pass 1 endpoint name and its batch variant, the include-flag semantics, the Schwab chain endpoint name, and the per-contract field naming are documented in the engineering-only MCP reference. The runtime VOLATILITY file names the *sources* (Polygon `avg_iv`, Schwab ATM chain per-contract IV) but not the specific endpoint signatures.
- Refresh orchestration. The runtime does not initiate refreshes; that is operator-driven.
- Macro volatility. Per the v3.0 design decision, there is no macro vol layer in VOLATILITY. Broad-market vol context (VIX, VVIX) is not consumed by VOLATILITY; when relevant for macro regime, it flows through DEALER's SPY-derived metrics.
- Cross-ticker IV comparisons (e.g., "this name's IV is unusually high relative to its sector"). The tool surface delivers per-ticker values; cross-ticker comparative analysis is operator work, not runtime work.

A volatility-regime question that doesn't fit one of the rules above is a question VOLATILITY does not govern.

## Legacy anchors (for legend citations and back-compat)

**VOLATILITY_001** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 term-structure and history window defaults (`short_dte=30`, `long_dte=90`, `short_tolerance=15`, `long_tolerance=30`, `min_history_points=20`) are pipeline horizon parameters that govern which contracts the pipeline reaches for to compute front-month and back-month IV anchors and how much history must exist before IV rank and IV percentile are computed. They have no LLM runtime effect — the runtime consumes the delivered term-structure level and slope, the delivered IV rank, and the delivered IV percentile, and never selects the DTE windows or history floor — and are preserved in the engineering-only MCP reference. Body-text references in legacy report legends (e.g., "Rules applied: VOLATILITY_001") remain valid; the legend entry resolves to the engineering-only destination, and the runtime behavioral consequence the legend implies (that term-structure outputs are anchored to a stable horizon) is captured here under § Operational heuristics, "Term-structure outputs are context, not gates" and "IV history depth is a precondition for IV rank and IV percentile."

**VOLATILITY_002** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The OI-weighted `avg_iv` formula (`avg_iv = sum(iv*open_interest)/sum(open_interest)` when total OI is positive, arithmetic mean otherwise) is pipeline computation. The runtime never derives `avg_iv` and never sees the unrolled formula. Preserved in engineering-only for back-compat with legacy report legends and for engineering maintenance of the MCP reference.

**VOLATILITY_003** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The put/call OI ratio formula (`put_oi / call_oi` when `call_oi > 0`, null otherwise) is pipeline computation with a denominator guard. Runtime consumes the ratio as a delivered context value where surfaced in rationale; it does not aggregate option-chain OI itself.

**VOLATILITY_004** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The put/call volume ratio formula (`put_volume / call_volume` when `call_volume > 0`, null otherwise) is pipeline computation with a denominator guard. Preserved in engineering-only alongside VOLATILITY_003 as a paired chain-pressure ratio.

**VOLATILITY_005** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The OI ratio formula (`total_volume / total_open_interest` when total OI is positive, null otherwise) is pipeline computation. Runtime consumes the turnover ratio as a delivered context value.

**VOLATILITY_006** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The IV dispersion formula (population standard deviation across contract IVs, `ddof=0`) is pipeline computation. The behavioral consequence — that dispersion is read as a chain-quality qualifier on the IV/HV reading — is captured here under § Operational heuristics, "Skew and dispersion are surfaced when the structure is asymmetric." The choice of population vs. sample stddev is a pipeline decision with no runtime exposure.

**VOLATILITY_007** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The 25-delta IV retrieval fallback chain (nearest-delta within `0.15` tolerance → 25th/75th-percentile-by-strike → median-by-strike) is pipeline data-quality preprocessing for skew computation. Runtime consumes the resulting 25-delta IV anchors as delivered and does not see the fallback ordering. Preserved in engineering-only as documentation of the pipeline's skew-computation robustness logic.

**VOLATILITY_008** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The IV skew formula (`(put_iv - call_iv) * 100`, scaled to percentage points) is pipeline computation. The behavioral consequence — that positive skew indicates put premium and asymmetrically affects directional structure choice — is captured here under § Operational heuristics, "Skew and dispersion are surfaced when the structure is asymmetric."

**VOLATILITY_009** → § Operational heuristics, "Term-structure outputs are context, not gates"; computation portion to `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 anchor combined the *interpretation* of term-structure level and slope as regime-context modifiers with the *computation* of those values from front-month and back-month IV anchors. The interpretation — that backwardation and contango cut different directions on an elevated-IV-rank reading — is load-bearing for the runtime and is preserved here under the term-structure heuristic. The level formula (`(long_iv - short_iv) * 100`), the slope formula (`((back - front) * 100) / (long_dte - short_dte)`), and the front/back DTE target windows (30±15, 90±30) belong to the tool surface and are preserved in engineering-only.

**VOLATILITY_010** → § Operational heuristics, "IV rank tier names are a vocabulary, not a scoring system" and "IV history depth is a precondition for IV rank and IV percentile"; computation portion to `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 IV percentile formula (rank fraction of history values ≤ current, scaled to [0, 100]) is pipeline computation. The runtime contract is that IV percentile arrives bounded to [0, 100] with the same history-floor precondition as IV rank — when delivered null, the runtime falls back to IV/HV alone for structure choice. IV percentile is read as a secondary regime-context field alongside IV rank rather than as a separately tier-mapped vocabulary; the rationale is that IV rank is the primary regime indicator (it normalizes against the full historical range and is what DEALER's DGPI optionally weights), and a parallel tier vocabulary for IV percentile would duplicate the runtime surface without adding regime resolution.

**VOLATILITY_011** → § Operational heuristics, "IV rank tier names are a vocabulary, not a scoring system" and § Appendix; computation portion to `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 IV rank formula (`(current - iv_min) / (iv_max - iv_min) * 100`, clamped to [0, 100], requiring `iv_max != iv_min`) is pipeline computation and is preserved in engineering-only with no runtime exposure. The runtime contract is that IV rank arrives bounded to [0, 100] with the history-floor precondition; the tier mapping that converts that score into runtime regime vocabulary (low / moderate / elevated / extreme) is owned by this file and lives in the Appendix.

**VOLATILITY_012** → § Operational heuristics, "Volatility-status labels are taken at face value"; computation portion to `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 anchor defined the A4 processing-status classifier that distinguishes `MISSING_OPTIONS` (no snapshot or no contracts), `PARTIAL` (contracts exist but `avg_iv` is null), and `SUCCESS` (full pipeline output), with `insufficient_iv_history` as a parallel diagnostic when history is below the 20-point floor. In v3.0 the runtime no longer consumes these three values directly; the tool surface now resolves processing status and confidence (per VOLATILITY_013) into a single runtime-facing label FULL / LIMITED / INVALID that mirrors DEALER's vocabulary. The v2.3 three-way processing status is preserved in engineering-only as the underlying tool-surface state; the runtime sees only the resolved label and the `insufficient_iv_history` diagnostic (which the runtime continues to honor as the trigger for the IV-rank-null fallback heuristic).

**VOLATILITY_013** → § Operational heuristics, "Volatility-status labels are taken at face value"; computation portion to `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 confidence-tier classifier (high requires `contracts_with_iv >= 40` AND `front_month_contracts >= 5` AND `back_month_contracts >= 5`; medium requires `contracts_with_iv >= 20`; low otherwise; forced low when processing status is not SUCCESS) is pipeline data-depth and tenor-coverage assessment. In v3.0 the runtime no longer consumes high/medium/low separately; the tool surface now combines confidence with processing status to produce the FULL / LIMITED / INVALID runtime label per the same cross-product collapse used in DEALER. The numeric cutoffs (40, 20, 5/5) are tool-surface parameters and live in engineering-only; the runtime vocabulary FULL / LIMITED / INVALID and its behavioral contract — FULL permits full structure-choice and sizing behavior, LIMITED restricts long-premium to floor-of-band sizing, INVALID drops the volatility layer entirely — are owned by this file and are load-bearing for RISK, SIGNAL, and PASS2 downstream.

**VOLATILITY_014** → `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming). The `DEFAULT_HISTORY_LOOKBACK = 252` parameter is a tool-surface default that caps the IV history fetch window to approximately one trading year and anchors IV percentile and IV rank calculations to that window. It has no LLM runtime effect — the runtime consumes the resulting bounded values regardless of which lookback produced them — and is preserved in engineering-only for engineering maintenance and reproducibility.

**VOLATILITY_015** → § Principle and § Operational heuristics, "IV source authority is pass-specific and non-negotiable" and "Source-substitution is never silent." The v2.3 source-authority rule — Polygon `avg_iv` via the canonical options-metrics endpoint for Pass 1 directional screening (accepting the residual +1 to +4 percentage point positive bias as structurally expected), Schwab ATM chain per-contract IV at the nearest-to-money strike for Pass 2 IV/HV calculation, never Schwab's `theoreticalVolatility` field (hardcoded `29.0` sentinel, not market IV), and never Polygon `avg_iv` as the sole basis for the SIGNAL_008 spread-mandate trigger — is the most load-bearing runtime rule in the volatility domain and is preserved here in full as both a Principle commitment and an Operational heuristic. The specific tool-surface names (`get_options_metrics`, `get_batch_options_metrics`, the `include=['volatility']` flag semantics, the batch-30-symbol cap, the Schwab chain endpoint and per-contract field shape) are engineering concerns and live in `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming); the runtime contract is the *source-authority decision* (which provider, which field, which pass), not the *endpoint signature*. The deprecated `get_volatility_metrics` tool surface noted in the v2.3 context block is preserved in engineering-only as deprecation documentation; the runtime sees only the canonical replacement and does not need to know that an older surface ever existed. The Pass 2 anti-pattern preserved from v2.3 ("Polygon `avg_iv` is never the sole basis for the SIGNAL_008 trigger") is elevated in v3.0 from anti-pattern to standing operational heuristic ("Source-substitution is never silent") because v2.3 surfaced it as a recurring failure mode worth stating as principle rather than as exception. Body-text references in legacy report legends (e.g., "Rules applied: VOLATILITY_015") remain valid and will continue to be honored in report output.

## Appendix — formulas and reference tables

**IV rank tier bands.** Delivered IV rank is bounded by the tool surface to [0, 100]. The runtime reads the score into one of four tiers using the bands below. Boundary values resolve to the more conservative adjacent tier per § Operational heuristics.

| IV rank band | Tier name | Structure preference bias | Behavioral consequence |
|---|---|---|---|
| 0 to 24 | Low | Favors patient debit entries (naked long calls or puts where IV/HV permits) | IV rank does not by itself restrict structure; subject to IV/HV band and other regime gates |
| 25 to 49 | Moderate | Neutral on premium-selling vs. premium-buying | Structure choice falls through to IV/HV band |
| 50 to 74 | Elevated | Tilts toward premium-selling structures (CSPs, credit spreads); biases away from naked long-premium even when IV/HV allows it | Long-premium entries in this tier surface a qualifier in rationale; spread structures preferred over naked even at the lower end of the IV/HV ratio |
| 75 to 100 | Extreme | Requires explicit mean-reversion-risk acknowledgment regardless of direction | *"Stretched IV"* annotation surfaces in report regardless of structure direction; short-premium positions flagged for vol-crush exposure, long-premium positions flagged for vol-expansion-failure exposure |

The 25-point band width is anchored to the [0, 100] bounded scale and produces four roughly equal tiers. The mean-reversion-aware extreme tier is the analog to DEALER's hostile DGPI tier — it does not refuse structures, but it requires the runtime to acknowledge regime risk in the rationale.

**IV/HV ratio bands.** Delivered IV/HV ratio compares Pass 2 Schwab ATM IV to tool-surface-computed historical volatility on the same name. The runtime reads the ratio into one of three bands using the values below. Boundary values resolve to the more conservative adjacent band.

| IV/HV ratio band | Band name | Structure-choice consequence |
|---|---|---|
| ≤ 0.95 | Cheap | Long-premium structures eligible; naked long calls or puts acceptable subject to other regime gates; spread not required |
| 0.96 to 1.19 | Neutral | Long-premium eligible; vertical spread preferred for sizing efficiency but not mandatory; structure choice may fall through to operator preference or RISK band optimization |
| ≥ 1.20 | Elevated | Vertical spread mandatory for new directional entries; naked long-premium refused regardless of conviction; SIGNAL's spread-mandate trigger fires |

The 1.20 threshold for the elevated band is the v2.3 carryover referenced in `RISK_v3.0.md` ("elevated IV (≥ 1.2)") and is preserved here as the v3.0 reference value. The neutral band (roughly 0.96 to 1.19) is new content in v3.0: v2.3 had a single threshold separating "spread mandatory" from "naked OK," and v3.0 introduces the neutral band to give RISK sizing room to breathe at near-1.0 ratios where neither structure is clearly forced. The cheap band ceiling (0.95) is symmetric with the neutral floor.

**FULL / LIMITED / INVALID volatility-status label semantics.** The label delivered by the tool surface (resolved from the v2.3 processing status and confidence tiers per VOLATILITY_012 and VOLATILITY_013) carries a defined runtime behavioral contract:

| Label | Tool-surface meaning (informational; mechanics in engineering-only) | Runtime behavioral consequence |
|---|---|---|
| FULL | Volatility metrics computed from a deep chain with adequate front-month and back-month tenor coverage and confident IV history depth | Full structure-choice and sizing behavior per RISK; full IV rank tier read; full IV/HV band read; term-structure and skew qualifiers consumed as context |
| LIMITED | Volatility metrics computed but with degraded chain depth, partial tenor coverage, or insufficient confidence; processing status is PARTIAL or SUCCESS-with-low-confidence | Sizing restricted to floor-of-band per RISK regardless of IV/HV band; IV rank tier read but with reduced confidence; *"Weak volatility signal — LIMITED chain depth"* surfaces in rationale; spread structures preferred over naked even at cheap IV/HV |
| INVALID | Insufficient data for trustworthy volatility-metrics computation; processing status is MISSING_OPTIONS, or PARTIAL with `avg_iv` null and no other recoverable signal | Volatility layer reads as absent; no IV rank tier consumed; IV/HV band defaults to *Needs chain validation*; spread-mandate decision defaults to "spread required" because the absence of confident IV/HV cannot authorize the cheaper naked structure |

The numeric thresholds underlying these labels (contracts-with-IV cutoffs of 40 and 20, front/back-month tenor minimums of 5/5, history-floor of 20 points) are MCP-internal parameters documented in `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming).

**Insufficient-IV-history diagnostic.** When the tool surface cannot compute IV rank or IV percentile due to history below the floor, the diagnostic flag is delivered alongside any otherwise-valid metrics and carries the following runtime behavioral contract:

| Condition | Runtime behavioral consequence | Report surfacing |
|---|---|---|
| `insufficient_iv_history` diagnostic active, other metrics FULL | IV rank tier read as null; structure choice falls back to IV/HV band alone; IV percentile also null | *"IV rank not available — limited history"* surfaces in data-quality section |
| `insufficient_iv_history` diagnostic active, other metrics LIMITED or INVALID | Same as INVALID label behavior; insufficient-history diagnostic does not override LIMITED/INVALID, it accompanies it | Both labels surface in data-quality section |

The runtime does not substitute IV percentile for IV rank when only one is available; both share the same history-floor precondition and are null or non-null together.

**Stale-data label semantics.** When delivered volatility-metrics freshness falls outside the tool surface's freshness window, a stale flag accompanies the reading and carries the following runtime behavioral contract:

| Condition | Runtime behavioral consequence | Report surfacing |
|---|---|---|
| Stale volatility data, per-ticker | Volatility layer reads identical to INVALID; floor-of-band sizing per RISK; IV/HV band defaults to *Needs chain validation*; IV rank tier not consumed | *"Stale volatility data — [ticker], last refreshed [timestamp]"* in data-quality section; refresh prompt |

The runtime does not initiate refreshes; refresh is operator-driven. The freshness window itself is set by the MCP data provider and is documented in engineering-only.

**IV source-authority reference.** The pass-specific source rules from VOLATILITY_015 are preserved here as the v3.0 reference table. Specific tool-surface names are noted for cross-reference with `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` (forthcoming); the runtime contract is the source-authority decision, not the endpoint signature.

| Pass | Decision question | Canonical source | Field consumed | Acceptable bias / known limitation |
|---|---|---|---|---|
| Pass 1 | Directional screening (is this ticker's IV roughly in a useful range for the screening run?) | Polygon options-metrics endpoint (single-symbol or batch variant with `include=['volatility']`); batch capped at 30 symbols per call | `avg_iv` | Residual +1 to +4 percentage point positive bias vs. Schwab ATM IV is structurally expected and acceptable for directional classification |
| Pass 2 | Spread-mandate decision (is this ticker's forward IV rich enough relative to realized to mandate a vertical spread?) | Schwab options chain endpoint, ATM portion | Per-contract `volatility` field at the nearest-to-money strike | None — Schwab ATM is the canonical Pass 2 source by definition |
| Either pass | Any decision requiring market IV | Never Schwab `theoreticalVolatility` field | — | Hardcoded `29.0` sentinel, not market IV; consuming it would silently corrupt every downstream regime read |
| Pass 2 SIGNAL_008 spread-mandate trigger | Spread required (Y/N) | Schwab ATM per-contract IV (not Polygon `avg_iv`) | IV/HV ratio computed from Schwab ATM IV and tool-surface-computed HV | Polygon `avg_iv` is never the sole basis for this trigger; substitution is never silent (per § Operational heuristics) |

**Source-substitution refusal contract.** When the canonical source for the current pass is unavailable, the runtime surfaces the gap rather than substituting. This contract operationalizes the "Source-substitution is never silent" heuristic:

| Canonical source unavailable | Runtime behavior | Report surfacing |
|---|---|---|
| Polygon `avg_iv` unavailable in Pass 1 | Volatility regime for the ticker reads as INVALID; IV rank tier not consumed; ticker remains screenable on non-volatility criteria but rationale surfaces the gap | *"Volatility regime not assessed — Pass 1 source unavailable"* in data-quality section |
| Schwab ATM IV unavailable in Pass 2 | IV/HV band reads as *Needs chain validation*; spread-mandate decision defers to Pass 2 retry rather than computing from Pass 1 data; structure decision reported as deferred | *"IV/HV deferred — Pass 2 source unavailable"* in data-quality section |
| Both sources unavailable | Volatility layer reads as INVALID across both passes; no IV regime consumed in any downstream decision | Combined annotation surfaces in data-quality section |

**Vocabulary alignment with data-quality labels.** Standard report surfacing for VOLATILITY-owned data conditions, aligned with the data-quality vocabulary in `KAPMAN_GUARDRAILS_v3.0.md` and with DEALER's parallel label scheme:

| Condition | Report label | When used |
|---|---|---|
| FULL volatility-status, fresh data, IV rank available | (No label required; regime reported as resolved tier and band) | Normal case |
| LIMITED volatility-status | *"Weak volatility signal — LIMITED chain depth"* | Volatility-status label LIMITED |
| INVALID volatility-status | *"Volatility regime not assessed — INVALID data"* | Volatility layer absent |
| Stale volatility data | *"Stale volatility data — [ticker], last refreshed [timestamp]"* | Freshness window exceeded |
| IV rank null due to insufficient history | *"IV rank not available — limited history"* | `insufficient_iv_history` diagnostic active |
| Pass 1 source unavailable | *"Volatility regime not assessed — Pass 1 source unavailable"* | Polygon `avg_iv` unreachable |
| Pass 2 source unavailable | *"IV/HV deferred — Pass 2 source unavailable"* | Schwab ATM IV unreachable |
| Extreme IV rank tier active | *"Stretched IV"* | IV rank in 75-100 band |
| IV/HV elevated | *"Spread mandated — elevated IV/HV"* | IV/HV ratio ≥ 1.20 |

**Metric vocabulary reference.** The metrics this file consumes, named consistently across the KB:

| Term | Definition | Owner of definition |
|---|---|---|
| `avg_iv` | Open-interest-weighted average implied volatility across eligible contracts for a ticker (Polygon-sourced for Pass 1); falls back to arithmetic mean when OI is zero | engineering-only (formula) |
| Schwab ATM IV | Per-contract `volatility` field from the Schwab options chain at the nearest-to-money strike; canonical Pass 2 IV input | engineering-only (chain navigation) |
| IV rank | Current `avg_iv` normalized between historical min and max over the lookback window, bounded [0, 100] | engineering-only (formula); this file (tier vocabulary and bands) |
| IV percentile | Rank fraction of historical `avg_iv` values ≤ current, scaled to [0, 100] | engineering-only (formula); this file (secondary regime-context interpretation) |
| IV/HV ratio | Pass 2 Schwab ATM IV divided by tool-surface-computed historical volatility on the same name | engineering-only (HV computation, ratio assembly); this file (band vocabulary) |
| IV dispersion | Population standard deviation across contract IVs (`ddof=0`) | engineering-only (formula); this file (chain-quality qualifier interpretation) |
| IV skew | Put 25-delta IV minus call 25-delta IV, scaled to percentage points | engineering-only (formula, 25-delta retrieval); this file (asymmetry qualifier interpretation) |
| Term-structure level | Back-month IV minus front-month IV, scaled to percentage points | engineering-only (formula, front/back DTE targets); this file (context modifier interpretation) |
| Term-structure slope | Term-structure level per DTE between front and back anchors | engineering-only (formula); this file (context modifier interpretation) |
| Volatility-status label | Categorical label (FULL / LIMITED / INVALID) representing trustworthiness of the full volatility-metrics output for a ticker | engineering-only (cutoffs); this file (behavioral contract) |
| `insufficient_iv_history` | Diagnostic flag signaling that IV rank and IV percentile are delivered null due to history below the floor | engineering-only (floor value); this file (fallback heuristic) |
| Stale volatility data | Reading older than the tool surface's freshness window | engineering-only (window); this file (behavioral consequence) |

**v2.3-to-v3.0 IV rank tier mapping reference.** The v2.3 source did not maintain a runtime tier vocabulary for IV rank — IV rank was a computed value with no LLM-facing band structure. The v3.0 four-tier vocabulary (low / moderate / elevated / extreme) is new content; the bands above are the v3.0 reference values and become the canonical IV rank vocabulary for the KB going forward.

| v3.0 tier | IV rank band | Reference allocation reasoning |
|---|---|---|
| Low | 0-24 | Quiet vol regime; IV expansion has room; debit entries patient |
| Moderate | 25-49 | Neutral regime; structure choice falls through to IV/HV |
| Elevated | 50-74 | Stretched regime; premium-selling biased; long-premium discouraged |
| Extreme | 75-100 | Mean-reversion regime; any structure surfaces the *"Stretched IV"* annotation |
