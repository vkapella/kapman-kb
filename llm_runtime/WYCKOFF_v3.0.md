---
system: KapMan
doc_type: principle
kb_version: 3.0.4
file_last_updated: 2026-06-26
status: active
tier: T1
---

# WYCKOFF

## Principle

Wyckoff phase identification is the regime-setting judgment that determines whether a long-premium position has structural tailwind, structural headwind, or no directional context — and therefore sets the ceiling within which every downstream sizing and structure decision operates. The four recognized phases are **Accumulation**, **Markup**, **Distribution**, and **Markdown**, cycling in that order; a ticker that has not yet received a confirmed phase reading in the current session is in an **UNKNOWN** state, which is treated as the most conservative case for all dependent triggers. The named events that anchor phase transitions — Selling Climax, Automatic Rally, Spring, Sign of Strength, Buying Climax, AR_TOP, Upthrust, Sign of Weakness — are the landmarks the runtime reasons from.

Phase identification follows a **two-path runtime**: the **viewer-ingest path** and the **estimation path**. The path taken depends on whether a current viewer/v2 reading is available for the ticker — in Stage 1 delivered as a pasted handoff row, by a direct export later — and on how confidently that reading is held.

**Viewer-ingest path.** The KapMan viewer (Polygon-fed) is the live pipeline source. When a viewer reading is present and passes the validity gate (recognized regime, current snapshot, clean fields), the runtime applies the **confidence tier gate** to the reading's `regime_confidence` and `phase_confidence`. The gating confidence is `min(regime_confidence, phase_confidence)`, or `regime_confidence` alone when `phase_confidence` is null (the ticker is trending with no active phase). When the gating confidence is at or above `τ_high` (per SYSTEM_PARAMS) and no hard force-flag is present, the reading is accepted as authoritative for the session without a propose-confirm exchange; the confirmation status is `pipeline-accepted`. When it falls in `[τ_low, τ_high)` — or when a hard force-flag is present at any confidence — the reading is surfaced to the operator under the flagged-reading exchange; the status is `pipeline-flagged` until the operator resolves it. When it falls below `τ_low`, the viewer reading is not usable as a pipeline reading and the runtime falls to the estimation path. Viewer/v2 confidence already prices in dealer and volatility cross-check disagreement and is capped below certainty, so the value is itself a meaningful gate — unlike the prior pipeline, which pinned confidence to a constant and could not be gated on it.

**Estimation path.** When no viewer reading is available for the ticker, the reading falls below `τ_low`, or the reading fails the validity gate for reasons other than a flaggable quality condition, the runtime falls back to the estimation path: live price and volume metrics (RVOL, VSI, historical volatility, and candle price action — from the Polygon and Schwab tool surfaces) serve as building blocks; the runtime assembles those building blocks into a proposed phase-and-event reading with explicit reasoning; the operator confirms or corrects; and only the operator-confirmed reading is authoritative. When the operator declines to confirm or the propose-confirm protocol is not run, all Wyckoff-dependent triggers degrade to their conservative defaults: the Wyckoff veto fires, the sizing band ceiling closes to the conditional floor, and the directional fallback reads NEUTRAL.

A confirmed reading — by any path — is scoped to the current session and is not memory-persisted between sessions. A new conversation begins with all tickers in UNKNOWN state regardless of what was confirmed in any prior session.


## Operational heuristics

**The two-path runtime entry sequence.**

At the start of any Wyckoff read for a ticker, the runtime looks for a current viewer/v2 reading. In Stage 1 that reading arrives as a pasted handoff row carrying the §A1 fields (`regime`, `regime_confidence`, `phase`, `phase_confidence`, `last_event`, `last_event_date`, `setup_tags`, the `range` block, and the dealer/volatility/IV fields used downstream); later it may arrive by a direct viewer export. The viewer's own watchlist filter — the operator narrowing a watchlist to a 10–15 ticker candidate set in the viewer before pasting — is the batch triage step; it stands in for any per-ticker pipeline call and is not itself a Wyckoff reading. When a viewer reading is present for the ticker, the viewer-ingest path runs and the confidence tier gate resolves it. When no viewer reading is present for the ticker, the estimation path runs against the live Polygon/Schwab metric surface. A full Wyckoff read per ticker — by whichever path applies — remains required before trigger evaluation.

**The viewer-ingest validity gate and confidence tier gate.**

A viewer reading passes the **validity gate** when all of the following are true:

| Criterion | Source | Passing condition |
|---|---|---|
| A reading is present for the ticker | viewer handoff row | The §A1 fields are present for the symbol |
| `regime` is a recognized phase | viewer `regime` | One of: Accumulation, Markup, Distribution, Markdown |
| Snapshot is current | viewer `as_of` / `data_through` | Within the run's freshness window; not stale relative to the session date |
| Regime/confidence fields are non-null | viewer `regime`, `regime_confidence` | Both present; `phase_confidence` may legitimately be null when trending |

A reading that passes the validity gate is then resolved by the **confidence tier gate**. The gating confidence is `g = min(regime_confidence, phase_confidence)`; when `phase_confidence` is null (trending, no active phase), `g = regime_confidence`.

| Gating confidence `g` | Status | Behavior |
|---|---|---|
| `g ≥ τ_high` and no hard force-flag | `pipeline-accepted` | Authoritative for the session; surfaced briefly, no propose-confirm |
| `τ_low ≤ g < τ_high`, or any hard force-flag present | `pipeline-flagged` | Flagged-reading exchange; UNKNOWN until the operator resolves it |
| `g < τ_low` | (no usable reading) | Estimation path runs |

`τ_high` and `τ_low` are defined in SYSTEM_PARAMS (`TIER_GATE_TAU_HIGH` / `TIER_GATE_TAU_LOW`). Unlike the excised pipeline — whose confidence was pinned to `1.0` and was explicitly *not* a validity criterion — viewer/v2 `regime_confidence` is a genuine [0, 0.95] score that already scales down for each failed dealer/volatility cross-check, so it is the primary gate here. The score is capped below 1.0, so `τ_high` must stay below 0.95.

**Hard force-flags** override a high confidence and force `pipeline-flagged` regardless of `g`:

| Force-flag condition | Detection |
|---|---|
| Structural cross-check conflict | viewer `structure_conflict: true` |
| Higher-timeframe disagreement | viewer `weekly_agrees: false` against the regime's directional bias |
| Stale snapshot | viewer `as_of` / `data_through` outside the run's freshness window |
| SOW-gated markdown | `regime` is Markdown with no confirmed Sign of Weakness in `last_event` / `setup_tags` |

**Viewer-ingest pipeline-accepted behavior.** When the validity gate passes, `g ≥ τ_high`, and no hard force-flag is present:

1. Extract `regime` as the authoritative phase for the session.
2. Extract `last_event` (with `last_event_date`) and `setup_tags` as the primary confirmed event and setup class if non-null. The viewer's detector has already qualified the event; no additional runtime acceptance threshold is required.
3. Record confirmation status as `pipeline-accepted`.
4. Surface the reading briefly to the operator: *"Viewer reads [TICKER] as [phase] — [last_event if applicable] (as of [snapshot date], confidence [g]). Proceeding."* Do not wait for operator response.
5. Downstream triggers engage at full authority — identical to `confirmed` status.

**The flagged-reading exchange.**

A reading is `pipeline-flagged` whenever the gating confidence falls in the `[τ_low, τ_high)` band or a hard force-flag is present (per the tier gate above). Mid-confidence and force-flag are not mutually exclusive — a reading may be flagged for either or both, and the exchange names whichever applies. When `pipeline-flagged`, the runtime presents the operator with the following explicit exchange:

*"Viewer reads [TICKER] as [phase] (as of [snapshot date], confidence [g]). Flagged because: [mid-confidence band and/or named force-flag(s)]. Options: (1) Accept as-is, (2) Override with your reading, (3) Request independent estimation from building-block metrics, (4) Defer — leave [TICKER] as UNKNOWN for this session."*

The default on a flagged reading is conservative: do not silently promote to `pipeline-accepted`. The ticker remains UNKNOWN until the operator responds. The operator's choice governs: accept → `pipeline-accepted`; override → `declared`; estimation → estimation path runs, propose-confirm follows; defer → UNKNOWN, conservative defaults.

**Reading the viewer event fields.**

The viewer reading carries event and structural context in three field groups, which are not interchangeable:

| Field | What it contains | How to use it |
|---|---|---|
| `last_event` (+ `last_event_date`) | The most recent named Wyckoff event the viewer detected (SC, AR, Spring, SOS, BC, AR_TOP, UT, SOW) and its date | Primary source for the current-session confirmed event; recency is read from `last_event_date` relative to the session date |
| `setup_tags` | The viewer's setup classification (e.g., `phase_c_spring_long`) encoding phase, event, and intended direction | The setup class that corroborates the regime/event reading and seeds direction; consumed by PASS1 as the confirmed setup class |
| `range` block (`support`, `resistance`, `midpoint`, `type`, `started`, `duration_bars`) | The active trading range the viewer fit, with boundaries and duration | Supporting structural context — candidate support/resistance shelves and range maturity; not a substitute for named-event structural levels |

`last_event_date` governs event recency: a `last_event` whose date is well outside the run's freshness window is historical context, not a current regime assertion, and should not by itself drive a phase reading. A Markdown regime requires a confirmed SOW in `last_event` / `setup_tags`; a stale or absent SOW under a Markdown regime forces the flagged-reading exchange via the SOW-gated-markdown force-flag.

**The estimation path — propose-confirm protocol.**

When the viewer-ingest path is not available or is not taken, the estimation path runs. The propose-confirm protocol is the mechanism by which estimation-path readings become authoritative.

The runtime reads available price and volume metrics for the ticker from the live tool surface — `Polygon MCP Server:get_batch_wyckoff_scan` / `get_options_metrics` with `include=['price']`, or `Schwab MCP Server:get_price_history_every_day` for candle history — assembles a phase-and-event reading with explicit reasoning stated in plain language, presents the reading to the operator with a confirmation prompt, and waits. The operator confirms, corrects, or declines. A confirmed reading — whether the operator accepts the proposal or substitutes a correction — is immediately authoritative for the session with status `confirmed`. A declined or skipped propose-confirm leaves the ticker in UNKNOWN state with conservative defaults.

The runtime does not infer confirmation from context, from prior-session memory, or from the operator's acceptance of a trade recommendation that depended on a Wyckoff reading. Confirmation on the estimation path requires an explicit exchange in the current conversation.

**Propose-confirm phrasing follows a fixed pattern.**

A phase proposal reads: *"Based on [metric observations], I read [TICKER] as [phase] — [event context if applicable]. Confirm or correct?"* The reasoning must name the specific metrics observed (e.g., RVOL contracting below 1.0, VSI near zero, price holding a defined support shelf) and the phase they support. Vague proposals ("this looks like accumulation") without metric grounding are not valid proposals — they give the operator nothing to evaluate. When the operator corrects, the runtime accepts the correction as authoritative without pushback; the operator's judgment supersedes the metric-based proposal. When the operator confirms, the runtime records the confirmed phase and any confirmed events as the authoritative reading for the session.

**Event confirmation is a separate, lighter-weight exchange.**

Phase confirmation establishes the broad regime (Accumulation, Markup, Distribution, Markdown). Event confirmation establishes a specific named landmark within or adjacent to that regime (Spring, SOS, SOW, Upthrust, AR_TOP). The two are independent: the operator may confirm a phase without confirming any specific event, or may confirm an event (particularly SOS or SOW for the directional fallback) while deferring full phase confirmation. An event proposal reads: *"I observe characteristics consistent with a [event name] on [TICKER] — [metric reasoning]. Confirm?"* Event confirmation does not update the phase reading; phase confirmation does not retroactively confirm events unless the operator explicitly names them.

**The priority order governs readings when multiple event signals appear in the same session.**

When price action presents evidence of more than one event type in the same period, the priority order determines which event is treated as regime-setting for the phase proposal: Selling Climax → Spring → Sign of Strength → Buying Climax → Upthrust → Sign of Weakness. This priority is not a recommendation to ignore lower-priority signals — all observed signals should appear in the proposal reasoning — but the dominant phase reading derives from the highest-priority event present. The operator may confirm a lower-priority event as regime-setting if the reading better fits their judgment; the runtime accepts that correction without resistance.

**The session-start state for all tickers is UNKNOWN.**

No Wyckoff reading carries forward from a prior conversation. At the start of every session, every ticker is UNKNOWN regardless of what was confirmed previously. The runtime does not assert a prior-session phase as a starting point, does not ask the operator to re-confirm a reading from yesterday, and does not treat the operator's mention of a prior reading ("we confirmed accumulation on AAPL last week") as confirmation for the current session. If the operator states a phase directly at session start without running propose-confirm or receiving a pipeline-accepted reading, the runtime treats that statement as an operator-declared override rather than a propose-confirm confirmation; the behavioral consequence is the same (the stated phase becomes authoritative), but the runtime notes that the reading was declared rather than pipeline-accepted or propose-confirmed, which informs the data-quality surface in the report.

**Markdown requires a confirmed Sign of Weakness; soft markdown without SOW is not active.**

A ticker does not enter a Markdown reading without a confirmed SOW event. This applies on both paths: a viewer `regime` of Markdown without a confirmed SOW in `last_event` / `setup_tags` triggers the SOW-gated-markdown force-flag and the flagged-reading exchange rather than auto-accepting. Distribution can persist — and the distribution-phase behavioral consequences apply — without a confirmed SOW. The transition from Distribution to Markdown is SOW-gated on both paths. Soft markdown (distribution rolling into markdown without explicit weakness confirmation) is disabled in the runtime by default.

**Phase succession requires that the prior phase has been present for a meaningful period.**

A phase change proposed within a very short window after the prior phase was established is a signal that the prior reading may have been noise rather than a genuine regime. When the propose-confirm reasoning for a phase succession involves a prior phase that appears to have lasted only a few bars, the proposal should acknowledge the short duration and invite the operator to weigh whether the prior phase was genuine. The runtime does not apply a hard bar count at chat time — that is a pipeline parameter — but the proposal reasoning should flag short-duration prior phases as a confidence qualifier.

**The Secondary Test is not delivered by the viewer/v2 tool surface.**

The Secondary Test (ST) is a recognized Wyckoff event in the methodology. It is not implemented in the viewer/v2 tool surface — parameters exist in the underlying configuration but no detection branch is active. When price action shows characteristics consistent with a Secondary Test (a low-volume revisit of the Selling Climax or Buying Climax area), the runtime may note the observation in the proposal reasoning as supporting context, but it does not propose a confirmed ST event and does not name ST as a regime-setting event.

**The minimum history guard applies before any proposal is made.**

A Wyckoff proposal requires sufficient price history to establish support and resistance shelves, identify climax events, and read volume behavior in context. When available price history is thin — fewer bars than the range-construction minimum — the propose-confirm protocol acknowledges the limitation explicitly and the proposal is marked as low-confidence. The runtime does not refuse to propose on thin history, but the proposal reasoning names the limitation and the operator's confirmation carries that caveat forward into the session's Wyckoff reading.

**Structural levels from the viewer are supporting context, not named Wyckoff anchors.**

The viewer reading's `range` block returns `support`, `resistance`, and `midpoint` as the boundaries of the fitted trading range, plus `type`, `started`, and `duration_bars` for range maturity. These are generic range-fit levels. There is no mapping from `range.support` to SC low, AR_TOP low, or any named Wyckoff anchor. Treat them as supporting technical context only. Named Wyckoff structural levels (SC low, AR high, Spring low, BC high, AR_TOP low, etc.) must be identified from the named event in `last_event` and the OHLCV history, not from the `range` boundaries.

**When the viewer-ingest path is not taken, all unconfirmed tickers degrade conservatively.**

An unconfirmed ticker — one that is UNKNOWN, pipeline-flagged and deferred, or on the estimation path with no operator confirmation — reads as UNKNOWN for all downstream triggers. The behavioral consequences of UNKNOWN are identical across all dependent triggers: the Wyckoff veto fires as if the phase were Distribution or Markdown, the sizing band ceiling closes to the conditional floor, and the directional fallback reads NEUTRAL. There is no middle state where some triggers engage and others do not based on partial metric evidence. `pipeline-accepted` is the only non-operator-confirmation status that preserves full trigger engagement.


## Workflow integration

**Position in the document hierarchy.**

WYCKOFF is tier T1 — a principle file. It owns the phase and event vocabulary that the runtime consumes, the two-path runtime entry sequence, and the confirmation-status vocabulary. WYCKOFF does not enforce sizing, does not validate option chains, does not assess dealer regime, does not assess volatility regime, and does not compose trigger contracts. Those are concerns of RISK, PASS2, DEALER, VOLATILITY, and SIGNAL respectively. WYCKOFF's sole runtime output is an authoritative phase reading and event set for a given ticker in a given session, obtained by whichever path applies; every file downstream of WYCKOFF consumes that output and is silent on how the reading was obtained.

**Inputs WYCKOFF reads.**

On the viewer-ingest path the inputs arrive in the pasted handoff row; on the estimation path they are fetched live from the Polygon/Schwab tool surface.

| Input | Viewer-ingest source | Estimation-path source | What WYCKOFF reads from it |
|---|---|---|---|
| Pipeline regime reading | viewer `regime`, `regime_confidence`, `phase`, `phase_confidence` | — (assembled by propose-confirm from metrics) | Phase label and the confidence that drives the tier gate; confirmation status |
| Event / setup context | viewer `last_event`, `last_event_date`, `setup_tags` | Named-event reasoning from OHLCV | Primary confirmed event and setup class; event recency |
| Range / structural context | viewer `range{support,resistance,midpoint,type,started,duration_bars}` | OHLCV-derived shelves | Supporting support/resistance context and range maturity |
| Price metrics (RVOL, VSI, HV) | carried in the handoff where present | `Polygon MCP Server:get_batch_wyckoff_scan` / `get_options_metrics` with `include=['price']` | Volume contraction/expansion; directional volume pressure; regime volatility context |
| Cross-check signals | viewer `weekly_agrees`, `structure_conflict` | — (not available; conservative default) | Hard force-flags that force the flagged-reading exchange regardless of confidence |
| Price candle data | — (the `range` block only) | `Schwab MCP Server:get_price_history_every_day` or equivalent | Support/resistance shelf identification; Spring and Upthrust candidacy; climax bar identification |

[Note: the viewer's watchlist filter narrows the candidate set before paste and is the batch triage step; there is no per-ticker pipeline call to make. Dealer and volatility metrics (DGPI, gamma flip, IV rank) ride the same viewer handoff for Pass-1 triage and are consumed by DEALER and VOLATILITY in parallel, not by WYCKOFF directly; per the Pass-1/Pass-2 boundary, Pass 2 re-fetches dealer and ATM-IV data live from Schwab.]

**Confirmation-status vocabulary and downstream behavioral consequences.**

| Status | How obtained | Downstream trigger engagement |
|---|---|---|
| `pipeline-accepted` | Viewer-ingest path; validity gate passed; `g ≥ τ_high`; no hard force-flag | Full — identical to `confirmed` |
| `confirmed` | Estimation path; operator accepted propose-confirm exchange | Full |
| `declared` | Operator stated phase directly without propose-confirm; no viewer pipeline reading | Full; data-quality surface notes declared status |
| `pipeline-flagged` | Viewer-ingest path; `g` in `[τ_low, τ_high)` or a hard force-flag present; operator has not yet resolved | UNKNOWN — conservative defaults until resolved; resolves to `pipeline-accepted`, `declared`, or estimation path `confirmed` |
| `unconfirmed` | Estimation path; operator declined or propose-confirm not run | UNKNOWN — conservative defaults |

**Where WYCKOFF outputs flow downstream.**

| Output | Consumed by | What the downstream file does with it |
|---|---|---|
| Confirmed phase (Accumulation / Markup / Distribution / Markdown / UNKNOWN) | `SIGNAL_v3.0.md` | Drives the Wyckoff veto firing condition (heuristic 1); sets the entry-time phase snapshot for the Regime exit advisory (heuristic 6) |
| Confirmed phase | `RISK_v3.0.md` | Sets the sizing-band ceiling: Markup authorizes the upper band; Accumulation post-Spring authorizes the conditional range; Accumulation pre-Spring caps at the conditional floor; Distribution and Markdown close the long-premium band; UNKNOWN is treated as the most conservative case |
| Confirmed phase | `DEALER_v3.0.md` | The ticker's DGPI tier narrows within the Wyckoff ceiling, never above it; Distribution and Markdown close the long-premium band regardless of how supportive the dealer regime reads |
| Confirmed Spring event | `SIGNAL_v3.0.md` | Distinguishes accumulation-pre-Spring (Wyckoff veto fires) from accumulation-post-Spring (eligible for long-premium entry) within heuristic 1 |
| Confirmed SOS event | `SIGNAL_v3.0.md` | Drives the directional fallback to BULLISH when primary directional signals are absent or in conflict (heuristic 11) |
| Confirmed SOW event | `SIGNAL_v3.0.md` | Drives the directional fallback to BEARISH (heuristic 11); also gates the Markdown phase reading (no markdown without confirmed SOW) |
| Confirmed phase succession (unfavorable direction) | `SIGNAL_v3.0.md` | Fires the Regime exit advisory when the entry-time phase has rolled to a less-supportive phase (heuristic 6) |
| Confirmed structural levels (support shelf, resistance shelf, range boundaries) | `SIGNAL_v3.0.md` | Candidate alert-price anchors for the Stop alert and Profit target alert when no dealer wall is closer; the Wyckoff structural level is the fallback anchor |
| Confirmed phase and events | `PASS1_SCREENING_v3.0.md` | Phase gates the eligible-set determination; UNKNOWN tickers are screened as if in distribution or markdown for long-premium eligibility |
| Confirmed phase and events | `PASS2_VALIDATION_v3.0.md` | Phase and event confirmation status is carried into structure validation context |
| Confirmed phase and confirmation status | `REPORT_FORMAT_v3.0.md` | Rendered in the Wyckoff regime field of the recommendation row; confirmation status (pipeline-accepted / confirmed / declared / pipeline-flagged / unconfirmed) surfaces in the data-quality section |

**Cross-references this file expects to be honored.**

- `KAPMAN_GUARDRAILS_v3.0.md` — owns the data-quality vocabulary that WYCKOFF's confirmation-status labels align with; owns the override discipline that applies when an operator declares a phase without running propose-confirm; owns the anti-hallucination floor that prevents the runtime from asserting a confirmed phase it has not actually confirmed. When this file and GUARDRAILS appear to conflict, GUARDRAILS wins per the T0/T1 tier discipline.
- `SIGNAL_v3.0.md` — consumes the confirmed phase and event outputs; owns what happens when those outputs are consumed by the Wyckoff veto, the directional fallback, and the Regime exit advisory. WYCKOFF does not know about SIGNAL's trigger contracts; SIGNAL does not know how confirmation happened.
- `RISK_v3.0.md` — consumes the confirmed phase as the sizing-band ceiling; owns the specific band ladder that the phase ceiling authorizes. WYCKOFF names the phase; RISK translates the phase into a sizing range.
- `DEALER_v3.0.md` — runs in parallel with WYCKOFF as a separate regime read; the dealer regime narrows within the Wyckoff ceiling. WYCKOFF does not read dealer outputs and DEALER does not read Wyckoff outputs; SIGNAL and RISK are the compositing layers.
- `VOLATILITY_v3.0.md` — runs in parallel with WYCKOFF as a separate regime read; no direct dependency in either direction.
- `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` (forthcoming) — owns the specific tool-surface contracts, z-score thresholds, boolean configuration flags, source file references, and the sequence confidence formula. The LLM runtime reads building-block metrics and applies qualitative reasoning patterns; the engineering-only reference holds the numeric parameters that the viewer/v2 pipeline uses to compute those metrics.


## Legacy anchors (for legend citations and back-compat)

**WYCKOFF_PHASE_001** → § Operational heuristics, "The minimum history guard applies before any proposal is made." The v2.3 rule enforced a hard minimum-bars constraint (`min_bars_in_range = 20`) that aborted all event and phase detection on insufficient history. The LLM runtime analog is the qualitative history guard in the heuristic: proposals on thin history are marked low-confidence rather than refused, because the operator can supply judgment the tool surface cannot. The specific bar-count threshold lives in `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` (forthcoming). Body-text references in legacy report legends remain valid.

**WYCKOFF_PHASE_002** → § Principle, phase vocabulary (Accumulation). The v2.3 rule defined Accumulation as the phase spanning from Selling Climax to Sign of Strength. The Appendix phase-succession table preserves this boundary logic. Body-text references remain valid.

**WYCKOFF_PHASE_003** → § Principle, phase vocabulary (Markup). The v2.3 rule defined Markup as spanning from Accumulation end to Buying Climax. The Appendix phase-succession table preserves the handoff-boundary logic. Body-text references remain valid.

**WYCKOFF_PHASE_004** → § Principle, phase vocabulary (Distribution). The v2.3 rule defined Distribution as spanning from Buying Climax to Sign of Weakness. The Appendix phase-succession table preserves the boundary logic. Body-text references remain valid.

**WYCKOFF_PHASE_005** → § Principle, phase vocabulary (Markdown). The v2.3 rule defined Markdown as spanning from Sign of Weakness to the next Selling Climax or the final available bar. The Appendix phase-succession table preserves this. Body-text references remain valid.

**WYCKOFF_PHASE_006** → § Operational heuristics, "Markdown requires a confirmed Sign of Weakness; soft markdown without SOW is not active." The v2.3 rule made the soft-markdown fallback a disabled-by-default config option (`allow_soft_markdown_without_sow = False`). The v3.0 heuristic encodes the same behavioral default as a standing runtime posture on both paths. The config parameter lives in `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` (forthcoming). Body-text references remain valid.

**WYCKOFF_PHASE_007** → `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 rule governed extending the first and last detected structural phases to chart edges. This is a chart-rendering behavior with no LLM runtime effect. Body-text references in legacy report legends remain valid.

**WYCKOFF_PHASE_008** → § Operational heuristics, "The priority order governs readings when multiple event signals appear in the same session." The v2.3 rule specified a deterministic event-to-regime mapping with fixed priority: SC → SPRING → SOS → BC → UT → SOW. The heuristic preserves this priority order as the governing read when multiple signals appear. Body-text references remain valid.

**WYCKOFF_PHASE_009** → § Operational heuristics, "The viewer-ingest validity gate and confidence tier gate." The v2.3 rule set regime confidence to 1.0 on event-triggered state changes and carried prior confidence forward on non-event days — a persistence parameter of the now-excised pipeline, which is why that source's confidence could not serve as a quality gate. The viewer/v2 source that replaced it emits a genuine [0, 0.95] `regime_confidence` that already scales down for failed cross-checks, so confidence is now the primary gate (`τ_high`/`τ_low` per SYSTEM_PARAMS); the tier-gate heuristic documents the contrast explicitly. Body-text references in legacy report legends remain valid.

**WYCKOFF_PHASE_010** → § Principle ("a ticker that has not yet received a confirmed phase reading in the current session is in an UNKNOWN state") and § Operational heuristics, "The session-start state for all tickers is UNKNOWN." The v2.3 rule initialized the prior state to `regime=UNKNOWN, confidence=None, set_by_event=None` when no prior regime existed. The v3.0 Principle elevates this to a session-scope invariant on both paths. Body-text references remain valid.

**WYCKOFF_PHASE_011** → § Operational heuristics, "Phase succession requires that the prior phase has been present for a meaningful period." The v2.3 rule required `prior_duration >= 5 bars` before persisting a regime transition. The v3.0 heuristic preserves the duration-qualification principle as a confidence qualifier. The specific 5-bar threshold lives in engineering-only. Body-text references remain valid.

**WYCKOFF_PHASE_012** → § Operational heuristics, "The priority order governs readings when multiple event signals appear in the same session" (sequence eligibility aspect) and § Appendix, event reading guide (SOS and SOW sequence eligibility notes). The v2.3 rule gated terminal-event sequence eligibility on the prior regime. The v3.0 Appendix event reading guide carries this as a reading-context qualifier for SOS and SOW proposals. Body-text references remain valid.

**WYCKOFF_PHASE_013** → `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 rule specified the sequence confidence formula: `min(1.0, round(0.6 + 0.1 × max(0, n), 4))`. Pipeline computation parameter with no LLM runtime effect. Body-text references remain valid.

**WYCKOFF_EVENT_001** → § Operational heuristics, "The minimum history guard applies before any proposal is made." Shared destination with WYCKOFF_PHASE_001. Body-text references remain valid.

**WYCKOFF_EVENT_002** → § Appendix, event reading guide (Selling Climax — SC). The v2.3 rule specified SC detection thresholds: `tr_z >= 2.0`, `vol_z >= 2.0`, `close_pos >= 0.5`. The Appendix entry translates these into qualitative reading patterns. Specific thresholds in engineering-only. Body-text references remain valid.

**WYCKOFF_EVENT_003** → § Appendix, event reading guide (Selling Climax — prior trend context). The v2.3 rule gated SC candidacy on `sma_slope < 0` when trend gating was enabled. The Appendix entry carries the prior-downtrend context as a reading qualifier. Body-text references remain valid.

**WYCKOFF_EVENT_004** → § Appendix, event reading guide (Buying Climax — BC). The v2.3 rule specified BC detection thresholds: `tr_z >= 2.0`, `vol_z >= 2.0`, `close_pos >= 0.6`. The Appendix entry translates these into qualitative reading patterns. Specific thresholds in engineering-only. Body-text references remain valid.

**WYCKOFF_EVENT_005** → § Appendix, event reading guide (Buying Climax — prior trend context). The v2.3 rule gated BC candidacy on `sma_slope > 0`. The Appendix entry carries the prior-uptrend context as a reading qualifier. Body-text references remain valid.

**WYCKOFF_EVENT_006** → § Appendix, event reading guide (Automatic Rally — AR). The v2.3 rule defined AR as the first qualifying up-close after SC with `tr_z > 0.5`. The Appendix entry carries this as: the first meaningful upward reaction after a Selling Climax on above-average range expansion. Specific threshold in engineering-only. Body-text references remain valid.

**WYCKOFF_EVENT_007** → § Appendix, event reading guide (AR_TOP). The v2.3 rule defined AR_TOP as the first qualifying down-close after BC with `tr_z > 0.5`. The Appendix entry carries this as the distribution-side analog of the Automatic Rally. Specific threshold in engineering-only. Body-text references remain valid.

**WYCKOFF_EVENT_008** → § Appendix, event reading guide (Spring). The v2.3 rule specified Spring detection: support break > 1%, re-entry within 2 bars, `close_pos >= 0.6`, `vol_z >= 0.8`. The Appendix entry translates these into qualitative reading patterns. Specific thresholds in engineering-only. Body-text references remain valid.

**WYCKOFF_EVENT_009** → § Appendix, event reading guide (Upthrust — UT). The v2.3 rule specified UT detection: resistance break > 1%, re-entry within 2 bars, `close_pos <= 0.4`. The Appendix entry translates these into qualitative reading patterns. Specific thresholds in engineering-only. Body-text references remain valid.

**WYCKOFF_EVENT_010** → § Appendix, event reading guide (Sign of Strength — SOS). The v2.3 rule specified SOS: close above resistance with `tr_z >= 1.5`. The Appendix entry carries the qualitative pattern. Specific threshold in engineering-only. Body-text references remain valid.

**WYCKOFF_EVENT_011** → § Appendix, event reading guide (Sign of Weakness — SOW). The v2.3 rule specified SOW: close below support with `tr_z >= 1.5`. The Appendix entry carries the qualitative pattern. Specific threshold in engineering-only. Body-text references remain valid.

**WYCKOFF_EVENT_012** → `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 rule specified the event score payload formula: `vol_z` for SC, BC, Spring; `tr_z` for AR, AR_TOP, UT, SOS, SOW. Pipeline scalar with no LLM runtime effect. Body-text references remain valid.

**WYCKOFF_EVENT_013** → § Operational heuristics, "The Secondary Test is not delivered by the viewer/v2 tool surface." ST parameters exist in configuration but no detection branch is implemented. ST observations appear in proposal reasoning as supporting context only; never proposed as confirmed events. Body-text references remain valid.


## Appendix — formulas and reference tables

**Phase vocabulary and succession sequence.**

The four recognized phases cycle in a defined order. The succession sequence is the authoritative reference for phase-change proposals and regime exit advisory readings.

| Phase | Regime character | Authorized entry structures | Sizing-band ceiling | Succeeds to |
|---|---|---|---|---|
| Accumulation (pre-Spring) | Range-bound; supply being absorbed; no confirmed breakout | Conditional — long-premium refused per Wyckoff veto; CSPs, hedges, LEAPs eligible | Conditional floor | Accumulation post-Spring (Spring confirmation within phase) or Markup (SOS confirmation) |
| Accumulation (post-Spring) | Range-bound; Spring confirmed; demand beginning to dominate | Long-premium eligible subject to other regime gates | Conditional range — top of conditional | Markup |
| Markup | Trending higher; demand in control; SOS confirmed breakout | Long-premium fully eligible | Upper band | Distribution |
| Distribution | Range-bound at highs; supply re-entering; BC confirmed | Long-premium refused per Wyckoff veto; eligible set redirected | Long-premium band closed | Markdown (SOW required) |
| Markdown | Trending lower; supply in control; SOW confirmed breakdown | Long-premium refused; structures targeting opposite direction eligible | Long-premium band closed | Accumulation (next SC) |
| UNKNOWN | No confirmed reading in current session | Treated as most conservative case — same as Distribution/Markdown for entry purposes | Long-premium band closed | Any phase (first confirmed reading on either path resolves) |

Allowed transitions: Accumulation → Markup → Distribution → Markdown → Accumulation. No other transitions are recognized. A proposed phase change that skips a step in the cycle (e.g., Accumulation → Distribution directly) is not a valid succession; the proposal should name the intermediate phase as either compressed or unobserved and invite operator judgment.

**Event-to-phase mapping and priority order.**

When multiple events are observed in the same session period, the priority order determines which event is regime-setting for the phase proposal. Lower-priority events are included in the proposal reasoning as supporting or qualifying context.

| Priority | Event | Phase signal | Directional implication |
|---|---|---|---|
| 1 | Selling Climax (SC) | → Accumulation begins | Bullish setup forming (not yet confirmed) |
| 2 | Spring | → Accumulation (confirms phase C character) | Bullish — accumulation completing |
| 3 | Sign of Strength (SOS) | → Markup begins | Bullish — confirmed breakout |
| 4 | Buying Climax (BC) | → Distribution begins | Bearish setup forming (not yet confirmed) |
| 5 | Upthrust (UT) | → Distribution (confirms failed breakout character) | Bearish — distribution completing |
| 6 | Sign of Weakness (SOW) | → Markdown begins | Bearish — confirmed breakdown |
| — | Automatic Rally (AR) | Accumulation context — first post-SC reaction | Neutral — range upper boundary reference |
| — | AR_TOP | Distribution context — first post-BC reaction | Neutral — range lower boundary reference |

AR and AR_TOP are not regime-setting events. They are structural landmarks that define range boundaries and inform support/resistance shelf identification for the proposal reasoning.

**Event reading guide — qualitative patterns for proposal assembly.**

The following table translates v2.3 event detection logic into the qualitative price/volume patterns the runtime reads from the live-delivered metrics to assemble a proposal. Specific z-score thresholds and configuration parameters are in `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` (forthcoming).

| Event | Price pattern | Volume pattern | Prior context required | Notes |
|---|---|---|---|---|
| Selling Climax (SC) | Wide-range bar; close recovers off the bar low (closes in upper half of bar) | Volume well above recent average — a spike relative to the period | Prior declining trend strengthens the reading; SC without prior downtrend is a weaker proposal | Regime-setting: → Accumulation. First event in the accumulation structure |
| Automatic Rally (AR) | First meaningful up-close after SC; range expansion relative to nearby bars | Above-average range; volume need not spike | SC must be established | Not regime-setting. Defines the upper boundary of the accumulation range (resistance shelf) |
| Spring | Price briefly pierces the established support shelf (SC low area), then recovers back inside the range within one or two bars; closes in the upper portion of the bar | Above-average volume on the break and recovery — not required to be a spike but should be above recent baseline | Accumulation must be established (SC must exist); support shelf must be defined | Regime-setting within accumulation: confirms accumulation phase C character. Spring confirmation is what unlocks post-Spring long-premium eligibility per SIGNAL's Wyckoff veto. Only the first Spring in a period is regime-setting |
| Sign of Strength (SOS) | Close above the established resistance shelf (AR high area) on a range-expansion bar | Above-average range expansion; volume expansion reinforces the reading | Accumulation or Markdown prior regime strengthens eligibility; SOS in a Distribution or Markup prior regime is a contradictory signal and should be flagged in the proposal | Regime-setting: → Markup. Closes the accumulation phase. SOS confirmation is a directional fallback input for SIGNAL heuristic 11 (BULLISH) |
| Buying Climax (BC) | Wide-range bar; close near the bar high (closes in upper portion) | Volume well above recent average — a spike | Prior uptrending context strengthens the reading; BC without prior uptrend is a weaker proposal | Regime-setting: → Distribution. First event in the distribution structure |
| AR_TOP | First meaningful down-close after BC; range expansion relative to nearby bars | Above-average range | BC must be established | Not regime-setting. Defines the lower boundary of the distribution range (support shelf). Distribution-side analog of AR |
| Upthrust (UT) | Price briefly pierces the established resistance shelf (BC high area), then fails to hold above it within one or two bars; closes in the lower portion of the bar | Volume not required to spike; weak close is the primary signal | Distribution must be established (BC must exist); resistance shelf must be defined | Regime-setting within distribution: confirms distribution phase C character. Distribution-side analog of Spring. Only the first UT in a period is regime-setting |
| Sign of Weakness (SOW) | Close below the established support shelf (AR_TOP low area) on a range-expansion bar | Above-average range expansion | Distribution or Markup prior regime strengthens eligibility; SOW in an Accumulation or Markdown prior regime is a contradictory signal | Regime-setting: → Markdown. Closes the distribution phase. Required for Markdown — soft markdown without SOW is not active. SOW confirmation is a directional fallback input for SIGNAL heuristic 11 (BEARISH) |
| Secondary Test (ST) | Low-volume revisit of the SC or BC area without breaking the prior extreme | Volume noticeably below the SC or BC bar — contraction is the signal | SC (for accumulation ST) or BC (for distribution ST) must be established | Not delivered by the viewer/v2 tool surface — no active detection branch. May appear in proposal reasoning as supporting context only; never proposed as a confirmed event |

**`get_wyckoff_scan` and `get_batch_wyckoff_scan` — features block output fields.**

The following fields are returned in the `features` block of the scan response. This is
the authoritative field list for the Polygon MCP scan surface. All fields are computed
from the OHLCV DataFrame; none require a live options chain.

| Field | Type | Description | Pass 1 use |
|---|---|---|---|
| `latest_price` | float | Last close price | Spot anchor for regime context |
| `sma_20` | float | 20-day simple moving average | Markup/markdown classification input |
| `sma_50` | float | 50-day simple moving average | Markup/markdown classification input |
| `sma_200` | float | 200-day simple moving average | Markup/markdown classification input |
| `adx_14` | float | 14-day Average Directional Index | Trend strength gate (≥20 hard markup, 15–19 soft markup) |
| `plus_di` | float | +DI (positive directional indicator) | Directional dominance check (+DI > −DI required for markup) |
| `minus_di` | float | −DI (negative directional indicator) | Directional dominance check |
| `atr_14` | float | 14-day Average True Range | Volatility context; event detection input |
| `bbw_percentile` | float | Bollinger Band Width percentile rank (200-bar trailing) | Range compression context; low percentile = range-bound behavior |
| `obv` | float | On-Balance Volume (cumulative) | Volume trend context |
| `obv_slope_20` | float | OBV change over trailing 20 bars | Directional volume pressure; distribution classification input |
| `vol_z_score` | float | Volume z-score (20-bar) — alias for `vsi_20` | Volume surge context |
| `close_position` | float | Close location within bar range (0=low, 1=high) | Event candidacy (Spring, Upthrust, climax bars) |
| `vwap_offset_pct` | float | Percent deviation of close from 14-day VWAP | Price vs. volume-weighted mean context |
| `force_index` | float | Force Index (13-bar) | Buying/selling pressure magnitude |
| `cmf_20` | float | Chaikin Money Flow (20-bar) | Accumulation/distribution money flow context |
| `rvol_20` | float | Relative volume vs. 20-day average | Volume conviction context (>1.0 = above average) |
| `vsi_20` | float | Volume Surge Index — z-score of current volume (20-bar) | Directional volume pressure qualifier for SOS/SOW proposals |
| `historical_volatility` | float | Annualized 20-day historical volatility from log returns | Regime volatility context; IV/HV signal numerator denominator in triage report |

`historical_volatility` was added in `kapman-trader` patch `feat: add historical_volatility
to compute_wyckoff_snapshot()` (2026-05-16). Prior scan responses will not contain this
field. Triage report IV/HV Signal column requires this field to be non-null; the column
renders `—` when the field is absent or null.

**Structural levels owned by WYCKOFF.**

Wyckoff structural levels are the price anchors that emerge from the phase and event structure. They are candidate inputs to SIGNAL's Stop alert and Profit target alert when dealer walls are absent or farther than the Wyckoff level. These are identified from the named event in `last_event` and OHLCV history — not from the viewer's `range` block, which contains generic range-fit levels only.

| Level | Definition | Phase context | SIGNAL use |
|---|---|---|---|
| Support shelf | Low established by SC (accumulation) or AR_TOP (distribution); the price area the range has held above | Accumulation, Distribution | Stop alert anchor when spot is above support and the position is long |
| Resistance shelf | High established by AR (accumulation) or BC high (distribution); the price area the range has held below | Accumulation, Distribution | Profit target anchor when the position is long and resistance is the next structural ceiling |
| Spring low | The intrabar low of the Spring bar; defines the tested-and-rejected support extreme | Accumulation post-Spring | Tight stop anchor for long entries entered after Spring confirmation |
| Upthrust high | The intrabar high of the UT bar; defines the tested-and-rejected resistance extreme | Distribution | Reference level for short-structure entries |
| Creek | The resistance shelf in accumulation — synonymous with the AR high area; the level a SOS close must exceed | Accumulation | Breakout confirmation reference; Profit target anchor zone for entries made before SOS |
| Projected markup target | Estimated by adding the accumulation range height to the Creek level; a width-of-range projection | Post-SOS Markup | Profit target anchor zone for long entries confirmed by SOS; expressed as a zone, not a precise price |
| Distribution range upper | BC high or UT high — the upper boundary of the distribution range | Distribution | Reference for short-structure entries; Stop alert anchor for short positions |
| Distribution range lower | AR_TOP low or SOW level — the lower boundary of the distribution range | Distribution, Markdown | Breakdown confirmation reference; Profit target anchor zone for short entries |

Structural levels are expressed as zones in the report, not as precise prices, until Pass 2 validates the specific level against current chain data. The anti-hallucination floor from GUARDRAILS applies: a Wyckoff structural level is a candidate anchor zone, not a validated strike price.

**Propose-confirm phrasing reference.**

Non-exhaustive examples of valid propose-confirm exchanges. The operator's confirmation phrase need not be formal; unambiguous assent in any form is valid.

| Scenario | Example proposal | Example confirmation | Example correction |
|---|---|---|---|
| Viewer-ingest pipeline-accepted | *"Viewer reads AAPL as Accumulation post-Spring — Spring (2026-05-08, confidence 0.82). Proceeding."* | (no response required) | — |
| Viewer-ingest pipeline-flagged | *"Viewer reads NVDA as Distribution (as of 2026-05-08, confidence 0.52). Flagged because: mid-confidence band (below τ_high) and structure_conflict:true. Accept, override, request independent estimation, or defer?"* | *"Accept"* | *"Override — I see it as Markup now"* |
| Phase proposal — accumulation pre-Spring (estimation path) | *"Based on AAPL ranging several weeks with RVOL contracting below 1.0 and VSI near zero, SC low from [date] acting as support, no Spring confirmed. I read this as Accumulation pre-Spring. Confirm or correct?"* | *"Confirmed"* / *"Yes"* / *"That's right"* | *"It already had a Spring — I saw it break and recover last Tuesday"* |
| Phase proposal — markup (estimation path) | *"Based on NVDA closing above the resistance shelf on strong range expansion with RVOL elevated, prior accumulation structure visible from [date range]. I read this as Markup — SOS confirmed. Confirm or correct?"* | *"Confirmed"* | *"No, I think this is a re-test, still in accumulation"* |
| Event confirmation — Spring only | *"TSLA's low today pierced the [price] support level and recovered back above it by close, closing in the upper half of the bar on above-average volume. I observe characteristics consistent with a Spring. Confirm?"* | *"Confirmed"* | *"Volume wasn't there — I wouldn't count that as a Spring"* |
| Event confirmation — SOS | *"META closed above the [price] resistance shelf on above-average range expansion. I observe characteristics consistent with a Sign of Strength. Confirm?"* | *"Yes, SOS confirmed"* | *"It's close but I want to see one more day — leave it unconfirmed for now"* |
| Operator declaration (no propose-confirm) | Operator states: *"MSFT is in markup — I confirmed that yesterday"* | Runtime treats this as an operator-declared phase (authoritative for the session); notes in the data-quality surface that the reading was declared rather than pipeline-accepted or propose-confirmed in the current session | — |
| Declined confirm | Operator states: *"Skip the Wyckoff read for now"* | Ticker remains UNKNOWN; all dependent triggers at conservative defaults; runtime does not re-propose unless operator requests | — |

**Metric reading patterns for proposal assembly (estimation path).**

How each live metric informs the phase and event proposal on the estimation path. These are reasoning patterns, not detection thresholds; thresholds live in engineering-only. On the viewer-ingest path the regime reading is taken from the viewer fields directly and these patterns are not re-derived; the viewer's `regime_confidence` already prices in the dealer/volatility cross-check disagreement that the estimation path would weigh here.

| Metric | What contraction suggests | What expansion suggests | Phase/event relevance |
|---|---|---|---|
| RVOL (relative volume vs. period average) | Volume drying up — consistent with accumulation or distribution range behavior; low-conviction price moves | Volume picking up — consistent with climax events (SC, BC), breakout events (SOS, SOW), or Spring/UT reversals | Primary volume context for all event proposals |
| VSI (volume strength index) | Near zero: balanced buying/selling pressure — supports range-phase reading (accumulation or distribution) | Directional: positive on up-moves supports SOS candidacy; negative on down-moves supports SOW candidacy | Directional volume pressure qualifier for SOS/SOW proposals |
| HV (historical volatility) | Contracting HV in a range: consistent with accumulation or distribution character | Expanding HV on a directional move: consistent with markup or markdown character | Regime-context qualifier; reinforces phase reading but not a primary event signal. Source on batch scan path: `features.historical_volatility` in `get_batch_wyckoff_scan` response (annualized 20-day, log-returns). Source on single-ticker path: `get_options_metrics` with `include=['price']`. |
| HV-IV spread | Narrow or negative spread: vol premium not elevated; neutral options-context | Wide positive spread: elevated vol premium; informs confidence language when IV is extreme relative to realized vol | Options-context qualifier only; does not affect phase or event reading directly |
| Price candle behavior | Tight range, price respecting a shelf: supports range-phase reading | Wide-range bar closing away from its extreme in the recovery direction: SC or Spring candidacy (recovery off low); BC or UT candidacy (failure off high) | Primary pattern input for climax and reversal event proposals |
