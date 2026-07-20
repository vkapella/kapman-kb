---
system: KapMan
doc_type: runbook
kb_version: 4.0.2
file_last_updated: 2026-07-20
status: active
tier: T2
---

# PASS1 SCREENING

## Principle

Pass 1 screening is the eligible-set determination pass: it takes the operator's candidate list and returns, for each ticker, one of three outputs — Eligible, NO_TRADE, or WAIT — together with a recommended structure, a resolved direction, and candidate zones that Pass 2 uses to find specific contracts in the live chain. The governing judgment is that Pass 1's job is to compose all five regime inputs — Wyckoff regime + phase (operator-confirmed via the propose-confirm protocol), dealer regime (MCP-delivered per DEALER), volatility regime (MCP-delivered per VOLATILITY, using Pass 1 IV source), macro state (SPY-derived, evaluated once per run before any per-candidate work begins), and the SIGNAL trigger contracts that convert those regime reads into eligibility and structure decisions — into a single coherent determination for each candidate, without producing any output that requires Pass 2 chain validation to be safe. The anti-hallucination floor is not a constraint imposed on Pass 1 from outside; it is what it means to be a Pass 1 output: every eligible candidate carries a structure (spread or naked), a direction (BULLISH, BEARISH, or NEUTRAL), and candidate zones expressed as price ranges and DTE bands — never exact strikes, never exact expirations, never risk-reward ratios — because those require the live Schwab chain that only Pass 2 has seen. When a regime input is degraded, the corresponding SIGNAL trigger fires at its conservative default, and the candidate receives a structured NO_TRADE or WAIT rather than a permissive read on incomplete data; a screening run with degraded inputs produces a shorter eligible set and a set of explicitly-reasoned refusals, not a set of unexamined approvals. Pass 1 data does not carry forward as authoritative into Pass 2: regime reads fetched at Pass 1 are starting context, not validated inputs — Pass 2 re-fetches what it needs, because context compaction in long screening sessions can silently approximate numeric values that Pass 2 decisions require to be exact.


## Operational heuristics

**The macro gate runs once per screening run, before any per-candidate evaluation begins.**

The hostile-macro composite is SPY-derived: both conditions must hold — SPY spot well below its gamma flip AND SPY DGPI in the hostile tier (≤ −30, i.e. ≤ `HOSTILE_MACRO_DGPI_MAX` per SYSTEM_PARAMS) — for hostile macro to be active. The macro gate is evaluated first, before the candidate list is touched, because its result applies uniformly to every candidate in the run. When hostile macro is active, **bullish** long-premium directional structures (long calls, call debit spreads) are refused for every candidate without per-candidate re-evaluation; the eligible-set redirect — long puts, put debit spreads, CSPs, hedges, LEAPs — applies run-wide. (Hostile macro is a falling/unstable tape: it refuses the bullish direction, while the directionally-aligned bearish structures stay eligible — consistent with SIGNAL's dealer-timing veto and the Appendix hostile-macro redirect table.) When only one hostile-macro condition holds (SPY below flip with DGPI > −30, or SPY above flip with DGPI ≤ −30), the macro layer reads as mixed and is treated as the more conservative of the two readings throughout the run. When SPY dealer confidence is `low` or `invalid`, the macro layer is read with reduced confidence and the run output says so; macro regime is not asserted as supportive on weak SPY data, and the conservative read applies. A hostile-macro run is not an empty run — it is a redirected run, and the report surfaces the eligible alternatives explicitly for each candidate rather than returning a wall of refusals.

**The near-event-risk screen runs per candidate, before the macro gate.**

Earnings proximity is evaluated first for each candidate because it is the fastest-resolving veto: a confirmed date within EARNINGS_BLOCK_DAYS closes the candidate immediately with no further evaluation. The earnings date is fetched per candidate from `Finnhub MCP Server:get_earnings_calendar` — the earnings source-of-authority per `SIGNAL_v4.0.md` Heuristic 0, one call per candidate, comfortably inside the shared Finnhub free-tier budget (60 calls/min) at the 30-symbol batch cap. A candidate inside EARNINGS_CAUTION_DAYS receives a WAIT with an operator-approval gate and does not enter the eligible set until the operator explicitly redirects it; a candidate whose earnings screen cannot be evaluated (Finnhub unavailable, no operator-declared date) receives the same operator-gated WAIT rather than a silent pass. A candidate that was WAIT due to earnings proximity is re-evaluated fresh in any subsequent session where the earnings date has passed.

**A valid screening request has three elements; PASS1 treats each differently.**

The operator provides a candidate ticker list, optional context declarations, and optional override declarations. The ticker list is the work queue — every ticker on it receives a Pass 1 determination before the run closes; no ticker is silently skipped. Context declarations (operator-stated Wyckoff regime/phase readings, sector notes, prior-session observations) are treated as operator-declared readings: authoritative for the session, but flagged as declared rather than propose-confirmed in the data-quality surface of the output. Override declarations (explicit macro-gate or veto overrides per GUARDRAILS) are applied per-request and noted in the report subtitle or footnote; they do not carry across to the next run. When the operator's request is ambiguous — the mode is unclear, the ticker list is absent, or an override declaration is incomplete — Pass 1 does not guess and produce output; it asks before proceeding.

**The candidate list may arrive as a viewer/v2 handoff; the §A1 fields map directly into the Pass 1 regime reads.**

In the v4.0 runtime the candidate list is most often a filtered viewer/v2 watchlist, delivered as a pasted handoff in Stage 1 (a direct export later — the dual path is "paste now, tool later"). When a viewer handoff is present, each row is both a work-queue item and a pre-populated set of Pass-1 regime reads; PASS1 ingests the §A1 fields rather than re-fetching them, subject to the Pass 1 → Pass 2 boundary preserved below. A raw ticker list with no viewer fields remains a valid request — those tickers simply carry no pre-populated reads and are resolved through WYCKOFF's estimation path and live Pass-1 fetches. The §A1 ingest map:

| Viewer/v2 field | Pass 1 consumer | Notes |
|---|---|---|
| `symbol` | candidate ticker | work-queue item |
| `regime`, `regime_confidence`, `phase`, `phase_confidence` | WYCKOFF reading + tier gate | drives auto-accept vs flagged per WYCKOFF; PASS1 consumes the resolved confirmation status, not the raw confidence |
| `last_event`, `last_event_date`, `setup_tags` | confirmed event / setup class | e.g. `phase_c_spring_long`; seeds direction resolution |
| `weekly_agrees`, `structure_conflict` | WYCKOFF hard force-flags | force the flagged-reading exchange regardless of confidence |
| `invalidation_level` | SIGNAL Stop anchor | structural stop |
| `dgpi`, `gamma_flip`, `dealer_position`, `position_vs_flip`, `net_gex`, `gex_slope`, `dealer_confidence` | dealer-timing veto (Pass-1 triage) | **Schwab re-fetch at Pass 2** |
| `atm_iv`, `iv_hv_ratio`, `iv_hv_status`; `average_iv`, `iv_skew_25delta`, `iv_term_structure`, `put_call_ratio`, `historical_volatility` | IV/HV band + spread-mandate (Pass-1 firing) — the canonical `iv_hv_ratio` (ATM `atm_iv` ÷ HV20) is consumed directly from the handoff per VOLATILITY source-authority; `average_iv` is the band-average context read and the producer's flagged ATM fallback | labeled *Needs chain validation*; no live MCP fetch when `iv_hv_ratio` is present |
| `dealer_consistent`, `volatility_consistent` | informational — surfaced in the reading; no independent gate or trim | from v2 `cross_checks`; already priced into `regime_confidence` per WYCKOFF, so re-gating or trimming on them double-counts. A `false` is visible context only — it has already pulled `regime_confidence` down and may push the tier gate to the flagged-reading exchange |
| `pt_up_*`, `pt_down_*` + `*_prob` | candidate zone + expectancy context | calibrated hit-rates |
| `price`, `as_of` / `data_through` | decision anchor + freshness label | `price` = underlying_ref anchor |
| `screen_tier`, `screen_disposition`, `screen_structure`, `screen_sizing`, `screen_reasons` | the pre-computed deterministic screen (viewer `pass1_screen.py`, stamped by the envelope's `screen_version`) | **long-premium strategies only** — PASS1 consumes the disposition as the deterministic tier-gate + trigger-sequence result and *verifies* rather than re-derives; the runtime still owns Step-0 earnings, the Step-1 macro gate, and flagged/estimation resolution (the screen's WAIT rows are its queue). On the CSP view these fields are the row's long-premium read, not a CSP verdict. Absent (older exports) → PASS1 derives from the raw §A1 fields as before |

The viewer handoff is Pass-1 triage context, not Pass-2 truth: dealer fields are re-fetched live from Schwab at Pass 2 and the IV fields carry the *Needs chain validation* label, exactly as when those reads are fetched directly. Ingesting the handoff does not relax the Pass 1 → Pass 2 boundary; it only changes where the Pass-1 starting context comes from.

Two viewer dealer fields use vocabularies that must not be conflated with their Pass-2 counterparts:
- **`dealer_confidence`** (`high`/`medium`/`low`/`invalid`; `high`/`medium` are trusted) is the viewer's **Pass-1 data-quality self-rating on its own dealer read**. It is the **same four-value `confidence` field** the Schwab Pass-2 producer also emits — not a different vocabulary. The Pass-1↔Pass-2 distinction is **provenance and timing, not naming**: the viewer's `dealer_confidence` rates a Pass-1 triage read computed over the kapman-polygon-mcp-v2 option universe, while the Schwab `confidence` rates the live re-fetched read over the Schwab option universe, spot-anchored to the live flip. Because the two are computed over different universes, a trusted Pass-1 `dealer_confidence` never substitutes for the Pass-2 read and a degraded one never forces it — the dealer regime is re-fetched and re-rated at Pass 2 regardless, and the two are expected to **agree by confidence value and DGPI direction, not by exact value**.
- **`position_vs_flip`** (`above_flip`/`below_flip`/`at_flip`/`unknown`) is a **coarse Pass-1 triage** that maps onto `DEALER_v4.0.md`'s flip-zone vocabulary: `at_flip` ≈ **Near-flip**, `above_flip` / `below_flip` ≈ above / below the flip. The precise **Well above / Near-flip / Well below** resolution — keyed on the `NEAR_FLIP_BAND_PCT` band around the flip per SYSTEM_PARAMS — is a **Pass-2 determination** from the live Schwab flip distance; the viewer's three-way read is a starting hint, not that resolution. `unknown` is no Pass-1 flip hint — the dealer-timing triage proceeds without one, and Pass 2 re-fetches the live flip regardless.

**The handoff envelope may carry screen provenance and a macro-context block; both are triage context, never authority.**

A viewer export that carries the `screen_*` fields also carries `screen_version` (the implementation that produced them — cite it in the run's data-quality surface so dispositions stay attributable) and `screen_thresholds` (the τ / IV-HV / DGPI values that implementation used). When `screen_thresholds` disagree with SYSTEM_PARAMS, **SYSTEM_PARAMS governs**: the run flags the drift, treats the pre-computed dispositions as stale, and re-derives from the raw §A1 fields. The envelope's `macro_context` block (the viewer's SPY dealer read — signed DGPI, flip, `position_vs_flip`, `confidence` — as of export time) seeds the Step-1 macro gate exactly as a pasted SPY reading would; the gate is still evaluated by the runtime per DEALER, and a stale or absent block degrades to a live SPY fetch, never to an assumed-supportive macro.

**The §A1 ingest has a required-field contract; absence degrades, never silently passes.**

A pasted viewer handoff must carry the fields below for the §A1 ingest to be valid; when one is absent, the named degradation applies — the runtime never proceeds as if the field were favorable.

| Field | Role in the ingest | If absent |
|---|---|---|
| `exported_at` (envelope) | Lineage clock — the `lineage_id` derives from it per `JOURNAL_MGMT_v4.0.md`, never the session clock | Lineage cannot be derived; surface "lineage unavailable — export carries no `exported_at`" and flag the run lineage-degraded; do not substitute the session clock |
| `as_of` / `data_through` | Snapshot freshness + decision-anchor freshness | Freshness cannot be established; per `WYCKOFF_v4.0.md` this trips the stale-snapshot check, so the row cannot auto-accept — it drops to the estimation / flagged-reading path |
| `row_count` (envelope) | Paste-integrity echo / manifest | Surface "row_count not provided — paste integrity unverified" and proceed without the operator-eyeball check |
| `weekly_agrees`, `structure_conflict` | WYCKOFF hard force-flags | A missing field is read as *unknown*, not "clear" — it cannot confirm a high-confidence reading, so the reading routes to the flagged-reading exchange per `WYCKOFF_v4.0.md` rather than auto-accepting |
| `regime`, `regime_confidence` | WYCKOFF tier-gate input | The validity gate fails; the row runs the estimation path |
| earnings / next-earnings date | Step-0 near-event screen | Not a §A1 field — the earnings screen fetches live from `Finnhub MCP Server:get_earnings_calendar` per SIGNAL Heuristic 0; Step 0 runs that fetch regardless of the handoff |

The Pass 1 → Pass 2 boundary is unchanged by this contract: dealer fields are still re-fetched live from Schwab at Pass 2, and a present-but-degraded handoff field never becomes Pass-2 truth. `exported_at` and `row_count` are handoff envelope fields owned by `JOURNAL_MGMT_v4.0.md`, not per-row §A1 fields; this contract references them, it does not redefine the lineage format.

**Wyckoff status is checked per candidate, in sequence, before trigger evaluation for that candidate.**

For each ticker in the candidate list, the first per-candidate question is whether an operator-confirmed Wyckoff regime (and phase A–E) reading exists in the current session. If a confirmed reading exists — either from the propose-confirm protocol run earlier in this session, or from an operator declaration at session start — the confirmed regime/phase and any confirmed events are consumed directly and trigger evaluation proceeds. If no confirmed reading exists, WYCKOFF resolves the ticker before evaluation: when the viewer handoff carries a reading for the ticker, WYCKOFF's confidence tier gate resolves it (auto-accept at or above `τ_high`, else the flagged-reading exchange); when no viewer reading is present, the propose-confirm protocol runs inline against live price and volume metrics, assembles a regime/phase-and-event proposal with explicit metric reasoning, presents it to the operator, and waits for confirmation. Only after the operator confirms or corrects does trigger evaluation proceed for that ticker. If the operator declines to confirm or asks to skip the Wyckoff read for a ticker, that ticker is assigned UNKNOWN regime and all Wyckoff-dependent triggers degrade to their conservative defaults; trigger evaluation proceeds immediately on the conservative read without further delay. A *pending* flagged reading is not a declined one: when a reading is `pipeline-flagged` (or on the estimation path) and the operator has **not yet resolved it** — including operator-absent or unattended runs where no exchange is possible — the candidate's disposition is **WAIT** (reversible, pending the flagged-reading exchange), never NO_TRADE. A NO_TRADE on Wyckoff grounds requires a *resolved* reading: either a confirmed regime the veto refuses, or an operator who explicitly declined/skipped (UNKNOWN → conservative veto). This pins the operator-absent disposition the Stage-1 pilot found unspecified (the model-matrix agreement gap): FLAGGED → WAIT, ESTIMATION → WAIT. This inline-sequential ordering — propose-confirm for ticker N, evaluate ticker N, then move to ticker N+1 — keeps the propose-confirm exchange tightly coupled to the evaluation it governs and avoids front-loading the operator with a batch of confirmation prompts before any output is visible. The runtime does not re-propose for a ticker that already has a confirmed reading in the current session, even if the ticker appears multiple times in the candidate list.

**Trigger evaluation applies SIGNAL's entry-side contracts in a fixed sequence.**

For each candidate with a resolved Wyckoff status, the trigger sequence is: Wyckoff veto first, then dealer-timing veto, then spread-mandate. The Wyckoff veto is evaluated first because it is the strongest entry-side gate — a veto here ends the candidate's-direction long-premium eligibility regardless of how supportive the dealer or volatility regime reads. The veto is **direction-aware** (per SIGNAL): it evaluates whether the confirmed regime authorizes the candidate's resolved direction, so the candidate's direction (regime-natural or operator-declared, per the direction-resolution heuristic below) is established before the veto runs. If the Wyckoff veto does not fire, the dealer-timing veto is evaluated next using the per-ticker DGPI tier, flip-zone, near-flip flag, and dealer `confidence` (high/medium/low/invalid) delivered by MCP, plus the macro hostile-macro flag already established at Step 1. If the dealer-timing veto does not fire, the spread-mandate is evaluated using the Pass 1 IV source (Polygon `avg_iv`) and the IV/HV band it produces. The sequence stops at the first veto that fires for long-premium structures; when a veto fires, the candidate receives a NO_TRADE primary output with eligible alternatives surfaced, and the spread-mandate evaluation is skipped because there is no eligible structure to mandate a spread on. The spread-mandate is not a veto — it does not remove the candidate from the eligible set; it constrains the eligible structure to a vertical spread and shifts the sizing denominator accordingly.

**Direction is resolved for every eligible candidate before the candidate zone is assembled.**

Direction resolution follows a priority sequence, and the resolved direction is the axis SIGNAL's direction-aware Wyckoff veto evaluates against — so it is established from the confirmed regime and any operator declaration before the veto runs. Primary signals — the confirmed regime's natural direction (an accumulation-family regime, `accumulation`/`reaccumulation`, or confirmed `markup` → BULLISH; a distribution-family regime, `distribution`/`redistribution`, or confirmed `markdown` → BEARISH), an explicit operator direction declaration, or a confirmed dealer regime read that is unambiguous — resolve direction when they are present and in agreement. When primary signals are absent or in conflict, the Wyckoff-event directional fallback applies: confirmed `sos` → BULLISH, confirmed `sow` → BEARISH, neither confirmed → NEUTRAL. The operator can override the NEUTRAL fallback by stating direction explicitly in the screening request, per GUARDRAILS override discipline (an explicit "screen for long puts" is a BEARISH declaration). A candidate that resolves to NEUTRAL receives a NEUTRAL-direction eligible output; the eligible structure for a NEUTRAL candidate is typically a defined-risk spread or CSP rather than a directional naked position. Direction is resolved at Pass 1 and carried into the candidate zone; Pass 2 consumes the resolved direction without re-deriving it.

**The Pass 1 IV/HV read is the Polygon producer's `iv_hv_ratio`; its outputs are labeled accordingly.**

IV/HV band computation at Pass 1 reads the Polygon options-metrics producer's `iv_hv_ratio` (ATM `atm_iv` ÷ HV20) — single-symbol for one ticker, batch (capped at 30 symbols per call) for multiple tickers. When a viewer/v2 handoff carries the row's `atm_iv` / `iv_hv_ratio` / `iv_hv_status` (§A1), Pass 1 consumes those directly as the triage read rather than issuing a live fetch — the producer is the same source either way, so the handoff value is canonical, not a downgrade; the single-symbol/batch call is the path for tickers fetched directly (no handoff reading) and the fire-by-default fallback when no read is available. The resulting IV/HV band is a valid Pass 1 classification for directional screening and for the spread-mandate's firing condition. When the spread-mandate fires at Pass 1, the eligible-set output carries a *Needs chain validation* label on the spread-mandate determination, because the binding mandate is the Pass 2 re-confirm — a fresh re-fetch of the same producer against the validated chain. The spread-mandate fires by default when the Pass 1 read is unavailable (source-substitution is never silent); the candidate receives a spread-mandated output labeled accordingly. Pass 1 and Pass 2 read the same producer; Pass 2 re-fetches fresh rather than carrying the Pass 1 value forward.

**Pass 1 outputs are candidate zones, not validated specifics.**

Every eligible candidate output contains: the resolved structure (long call, long put, debit spread, CSP, or LEAP), the resolved direction (BULLISH, BEARISH, or NEUTRAL), a candidate strike zone expressed as a price range relative to current spot (e.g., "ATM to slightly OTM"), and a DTE target band appropriate to the intended trade horizon (`SWING_DTE_BAND` for swing trades, `CSP_DTE_BAND` for cash-secured puts, `LEAP_DTE_BAND` for LEAPs, per SYSTEM_PARAMS). Exact strikes, exact expiration dates, entry prices, stop-loss prices, profit targets, and risk-reward ratios are never produced at Pass 1 — these require Pass 2 chain validation. When a candidate's structure would naturally call for a specific level (e.g., a CSP candidate's put strike), Pass 1 expresses it as a zone anchored to structural levels (e.g., "below the current support shelf, ATM to 5% OTM") rather than as a price or delta. Confidence values are assigned per the band discipline in the Appendix; alternatives carry strictly lower confidence than the primary.

**Degraded inputs degrade outputs — the conservative default is the safety mechanism.**

When any regime input is degraded, the dependent SIGNAL trigger fires at its conservative default, and the candidate receives the conservative output. The degraded cases and their outputs are:

| Degraded input | Conservative default behavior | Pass 1 output |
|---|---|---|
| Wyckoff regime unconfirmed (propose-confirm declined or skipped) | Wyckoff veto fires | NO_TRADE — Wyckoff regime unconfirmed; WAIT alternative |
| Wyckoff reading `pipeline-flagged` / estimation-path, operator not yet resolved (incl. unattended runs) | No trigger evaluation — the reading is pending, not refused | WAIT — pending flagged-reading exchange |
| Dealer `confidence` = `invalid` (per-ticker) | Dealer-timing veto fires for long-premium candidates | NO_TRADE — dealer regime absent; WAIT alternative |
| Dealer `confidence` = `low` (per-ticker) | Full dealer read; sizing restricted to floor-of-band | Eligible at floor sizing; rationale notes low-confidence data |
| SPY dealer `confidence` = `invalid` or stale | Macro layer read with reduced confidence; conservative macro read applied | Eligible set treated as mixed-macro; rationale notes degraded SPY data |
| Volatility-status INVALID (per-ticker) | Spread-mandate fires by default | Eligible — spread mandated; *Needs chain validation* label |
| Pass 1 IV source unavailable | Spread-mandate fires by default | Eligible — spread mandated; source-unavailable noted |
| Multiple inputs simultaneously degraded | Most conservative applicable default; WAIT unless structural alignment is unambiguous | NO_TRADE with named reasons; WAIT alternative when candidate is structurally screenable |

A WAIT output means: the candidate is structurally screenable but a required input is degraded or missing; the candidate is not refused — it is deferred until the input is refreshed. A NO_TRADE output means: the candidate is refused for this screening run on the named basis; it does not enter a retry state within this run.

**Pass 1 data does not carry forward as authoritative into Pass 2.**

Regime reads established at Pass 1 — dealer metrics, volatility metrics, Polygon IV values — are starting context for the screening run, not validated inputs that Pass 2 may reuse. Pass 2 re-fetches dealer metrics fresh from Schwab regardless of whether Pass 1 values appear present in the conversation context, because context compaction in long screening sessions can silently approximate numeric values that Pass 2 strike selection and spread-mandate validation require to be exact. This is not a soft recommendation — it is a hard operational boundary. The only Pass 1 outputs that carry forward with full authority into Pass 2 are the operator-confirmed Wyckoff readings (which are session-scoped and owned by WYCKOFF's propose-confirm protocol) and the resolved direction and structure determinations (which are Pass 1's primary deliverable to Pass 2). Numeric regime values do not carry forward.

**The eligible-set summary surfaces before Pass 2 begins.**

After all candidates have been evaluated, Pass 1 assembles and surfaces the eligible set — every candidate that received an Eligible output, with its structure, direction, and candidate zones — for operator review before Pass 2 begins. Candidates that received NO_TRADE or WAIT outputs are listed with their reasons. The operator may add, remove, or redirect candidates at this point before Pass 2 begins; any addition at this stage must go through the Pass 1 trigger sequence before it enters the eligible set. Pass 2 does not begin until the operator has reviewed the eligible-set summary.

**The eligible set and the flagged-review queue are ordered by entry cohort — spring-cohort first.**

The spring cohort is every candidate whose current reading is an accumulation-family regime (`accumulation` or `reaccumulation`) with a confirmed bullish phase-C decisive test (`spring` or `shakeout`); the direction mirror is a distribution-family regime with a confirmed `utad` for bearish candidates. When Pass 1 surfaces the eligible-set summary, spring-cohort candidates render first, ahead of trend-continuation candidates; within each cohort the existing confidence ordering applies. The same ordering governs the flagged-reading review queue: when multiple readings await the flagged-reading exchange, spring-cohort candidates are presented for resolution first. Under current tier-gate calibration fresh springs commonly arrive `pipeline-flagged` (the reaccumulation confidence plateau), so without this ordering the highest-value cohort tends to sit unresolved behind auto-accepted continuation names — the ordering puts operator attention there first.

This is an attention-ordering rule, not a gate or sizing change. It does not alter tier-gate thresholds, veto outcomes, dispositions, sizing bands, or structure constraints; a flagged spring is still flagged and a vetoed spring is still refused. Provenance: the pinned 2026-07-02 economics study — spring-entry long calls were the only entry cohort whose mean-return confidence interval excluded zero on the broad backtest universe, while fresh-trend chase entries were breakeven at best; the bearish mirror rests on the battery's event-edge finding (the UTAD is the only bear-side entry edge), not yet on option-space economics. This rule is a KB-side pilot: whether deterministic cohort tagging moves into the viewer screen as a computed priority column is a September 2026 re-evaluation decision.


## Workflow integration

**Position in the document hierarchy.**

PASS1 SCREENING is tier T2 — a runbook. It is the primary consumer of every T1 principle file in the system and the entry point through which operator screening requests become structured eligible-set determinations. PASS1 does not own any regime vocabulary, trigger contract, or override mechanic — it invokes the contracts that the T1 files define and assembles their outputs into a per-candidate determination. When PASS1 and a T1 file appear to conflict, the T1 file's contract governs; when PASS1 and GUARDRAILS appear to conflict, GUARDRAILS governs. PASS1 is the procedural layer; the T1 files are the judgment layer.

**What PASS1 receives from each upstream file.**

| Source file | What PASS1 consumes | How PASS1 uses it |
|---|---|---|
| `KAPMAN_GUARDRAILS_v4.0.md` (T0) | Data-quality vocabulary; override discipline; hostile-macro eligible-set redirect; anti-hallucination floor | PASS1 applies the data-quality labels to every degraded output; applies override discipline at the screening-request entry point; applies the hostile-macro redirect run-wide when macro gate fires; enforces the anti-hallucination floor on every candidate zone |
| `DEALER_v4.0.md` (T1) | SPY hostile-macro composite (both conditions); per-ticker DGPI tier (signed), flip-zone, near-flip flag, dealer `confidence`; macro-layer dealer `confidence` | PASS1 evaluates the hostile-macro composite once at run start; reads per-ticker dealer regime for the dealer-timing veto; reads near-flip flag for the one-tier sizing step-down note in the candidate output |
| `VOLATILITY_v4.0.md` (T1) | IV/HV band (Pass 1 read: the Polygon producer's `iv_hv_ratio`); IV rank tier; volatility-status label; source-authority discipline | PASS1 reads the producer's IV/HV for the spread-mandate firing condition; applies *Needs chain validation* label when the mandate fires at Pass 1 (binding mandate is the Pass 2 re-confirm); degrades to fire-by-default when the Pass 1 read is unavailable |
| `WYCKOFF_v4.0.md` (T1) | Propose-confirm protocol; confirmed regime + phase (A–E) and event readings; UNKNOWN state; conservative-default behavior; operator-declared regime/phase handling | PASS1 invokes propose-confirm inline per candidate for unconfirmed tickers; consumes the confirmed regime/phase for Wyckoff veto evaluation; consumes confirmed `sos`/`sow` for directional fallback; assigns UNKNOWN and conservative defaults when propose-confirm is declined |
| `SIGNAL_v4.0.md` (T1) | Wyckoff veto contract (heuristic 1); dealer-timing veto contract (heuristic 2); spread-mandate contract (heuristic 3); directional fallback (heuristic 11); NO_TRADE consistency (heuristic 7); alternative-confidence ordering (heuristic 8); degraded-input fallback (heuristic 9); anti-hallucination floor (heuristic 10) | PASS1 applies the trigger contracts in fixed sequence per candidate; assembles NO_TRADE outputs with NONE structure; assigns confidence values that honor the ordering rule; applies structured fallback on degraded inputs |
| `RISK_v4.0.md` (T1) | Sizing band ladder (regime-ceiling → dealer-tier → volatility-tier), direction-relative; near-flip one-tier step-down | PASS1 notes the applicable sizing band in the candidate output so Pass 2 and the operator have the sizing context; PASS1 does not compute exact position size — that is RISK and operator work |

**What PASS1 hands to each downstream file.**

| Destination file | What PASS1 delivers | How that file uses it |
|---|---|---|
| `PASS2_VALIDATION_v4.0.md` (T2) | Eligible-set: per-candidate structure, direction, candidate zones, DTE band, Pass 1 IV source label, sizing band note, confidence value | PASS2 takes each eligible candidate and validates the structure and direction against the live Schwab chain; selects specific strikes and expirations within the candidate zones; re-confirms the spread-mandate by re-fetching the Polygon producer |
| `REPORT_FORMAT_v4.0.md` (T3) | Full Pass 1 output: Eligible/NO_TRADE/WAIT determinations with rationale, candidate zones, alternatives with confidence, data-quality labels, macro gate result, override acknowledgments | REPORT_FORMAT renders the Pass 1 section of the screening report; PASS1 does not own report rendering |
| `REPORT_STYLE_v4.0.md` (T3) | (Indirectly) the Pass 1 output surface | REPORT_STYLE governs field length caps, label vocabulary, and rationale density; PASS1 respects these constraints in the rationale text it assembles |
| `PORTFOLIO_MGMT_v4.0.md` (T2) | (Indirectly, after Pass 2) The entry-time regime snapshots that Pass 2 completes | PORTFOLIO_MGMT carries regime snapshots in position context; PASS1 is the regime-read origin for the Wyckoff regime (and phase) and direction that eventually become the entry-time snapshot |

**What PASS1 does not own.**

| Concern | Owner |
|---|---|
| Trigger contracts and firing conditions | `SIGNAL_v4.0.md` |
| Regime, phase, and event vocabulary | `WYCKOFF_v4.0.md` |
| Propose-confirm mechanics | `WYCKOFF_v4.0.md` |
| Dealer regime tier vocabulary | `DEALER_v4.0.md` |
| IV/HV band vocabulary and source-authority rules | `VOLATILITY_v4.0.md` |
| Sizing band ladder and near-flip step-down math | `RISK_v4.0.md` |
| Override discipline | `KAPMAN_GUARDRAILS_v4.0.md` |
| MCP tool-surface endpoint names, batch caps, parameter shapes | `engineering_only/PASS1_MCP_REFERENCE_v4.0.md` (forthcoming) |
| Chain validation, exact strikes, expiration selection | `PASS2_VALIDATION_v4.0.md` |
| Report rendering and field length caps | `REPORT_FORMAT_v4.0.md`, `REPORT_STYLE_v4.0.md` |
| Position monitoring and portfolio management | `PORTFOLIO_MGMT_v4.0.md` |

**Entry point for every Pass 1 run.**

Before per-candidate evaluation begins, three conditions must hold:

1. Mode is established as Screening or Hybrid — PASS1 does not run in Portfolio mode. If mode is ambiguous, GUARDRAILS requires asking before producing output.
2. The macro gate has been evaluated — SPY dealer metrics have been fetched in the current session and the hostile-macro composite has been resolved. If SPY dealer metrics are absent or stale, the macro layer reads with reduced confidence and the run proceeds on the conservative macro read; the run does not block on SPY data, but the output surfaces the degraded SPY status explicitly.
3. The candidate ticker list is present — if the operator's request contains no tickers, PASS1 asks for the list before proceeding.

**Cross-references this file expects to be honored.**

- `SIGNAL_v4.0.md` owns the trigger contracts PASS1 enforces. When SIGNAL and PASS1 appear to specify different firing conditions for the same trigger, SIGNAL governs.
- `WYCKOFF_v4.0.md` owns the propose-confirm protocol PASS1 invokes. PASS1 specifies *when* propose-confirm runs in the screening workflow; WYCKOFF specifies *how* it runs.
- `KAPMAN_GUARDRAILS_v4.0.md` owns the override discipline and the anti-hallucination floor. Neither may be relaxed by PASS1 heuristics, even implicitly.
- `VOLATILITY_v4.0.md` owns the IV source-authority rules. PASS1's use of the Polygon producer's `iv_hv_ratio` as the Pass 1 read is an application of VOLATILITY's source-authority discipline, not an independent PASS1 decision.
- `engineering_only/PASS1_MCP_REFERENCE_v4.0.md` (forthcoming) owns the specific MCP tool-surface contracts for Pass 1 data fetching — endpoint names, batch caps, parameter shapes, and the Polygon deprecated-endpoint inventory. PASS1 is silent on these; operators and engineers consult the engineering-only reference for tool-surface details.


## Legacy anchors (for legend citations and back-compat)

**PIPELINE_010** → `engineering_only/PASS1_MCP_REFERENCE_v4.0.md` (forthcoming). The v2.3 rule consolidated all Polygon MCP tool-surface routing decisions for Pass 1 data fetching: canonical endpoint names (`get_options_metrics`, `get_batch_options_metrics` with `include=['volatility']`), batch cap of 30 symbols per call, and the full inventory of deprecated endpoints that must never be called. These are MCP tool-surface contracts with no LLM runtime effect — the runtime reads delivered outputs; it does not select endpoints or enforce batch caps. The one behavioral residue that surfaces at the runtime layer is the data-quality consequence of the source-authority discipline (Polygon `avg_iv` as Pass 1 source, labeled *Needs chain validation* for spread-mandate outputs), which is owned by `VOLATILITY_v4.0.md` and applied by this file's heuristic "The Pass 1 IV source is Polygon `avg_iv`; its outputs are labeled accordingly." The full endpoint inventory, batch-cap enforcement, and deprecated-endpoint prohibition live in engineering-only. Body-text references in legacy report legends (e.g., "Rules applied: PIPELINE_010") remain valid; the legend entry resolves to the engineering-only destination. In the v4.0 runtime the full metrics payload (regime, dealer, volatility, IV/HV) arrives in the viewer/v2 handoff as Pass-1 triage context per the §A1 ingest map; the Polygon batch endpoint reference is unchanged — it remains the source for Polygon `avg_iv` specifically when a ticker is fetched directly rather than ingested from a handoff.

**PIPELINE_011** → § Operational heuristics, "Pass 1 data does not carry forward as authoritative into Pass 2." The v2.3 rule was a hard operational guard against context compaction in long screening sessions: Pass 2 must always re-fetch Schwab dealer metrics live, never reusing Pass 1 values even if they appear present in conversation history, because compaction can silently approximate numeric values that Pass 2 decisions require to be exact. The behavioral intent — that Pass 1 numeric regime reads are starting context, not validated inputs — is load-bearing for the runtime and is preserved in the heuristic as the standing Pass 1 / Pass 2 data-boundary rule. The specific compaction behavior that motivated the rule (Claude Sonnet 4.6 / Opus 4.6 context compaction active in beta as of 2026-03) is a platform-behavior observation documented in the v2.3 source; the runtime rule it produced is durable regardless of whether compaction behavior changes. Body-text references in legacy report legends (e.g., "Rules applied: PIPELINE_011") remain valid.

**SCORING_001** → `engineering_only/PASS1_MCP_REFERENCE_v4.0.md` (forthcoming). The v2.3 rule established that BC Score, Spring Score, and Composite Score are pass-through context values only — no formula computation occurs anywhere in the active pipeline, and no entry should be blocked or approved based solely on Composite Score until a formula and threshold are formally implemented. In v3.0 this situation is unchanged: the scoring modules remain unimplemented, and PASS1 does not gate entries on these scores. The pass-through constraint and the storage bounds (BC Score 0–28, Spring Score 0–12) are preserved in engineering-only as reference against the schema and the `c4_batch_ai_screening_job.py` payload. The v3.0 runtime does not reference these scores in any trigger evaluation or eligible-set determination. Body-text references in legacy report legends (e.g., "Rules applied: SCORING_001") remain valid; the legend entry resolves to the engineering-only destination.


## Appendix — formulas and reference tables

**Pass 1 screening workflow — step summary.**

| Step | What runs | Scope | Governs |
|---|---|---|---|
| 0 — Near-event-risk screen | Earnings date fetched live via `Finnhub MCP Server:get_earnings_calendar` (not the §A1 handoff, which carries no earnings field); EARNINGS_BLOCK_DAYS / EARNINGS_CAUTION_DAYS evaluation per SIGNAL | Per candidate, before macro gate | Immediate WAIT for block-window candidates; operator-approval WAIT for caution-window candidates and for candidates whose earnings screen cannot be evaluated (source unavailable) |
| 1 — Macro gate | SPY hostile-macro composite evaluation | Once per run, before any per-candidate work | All candidates in the run |
| 2 — Wyckoff status | Propose-confirm (if unconfirmed) or confirmed-reading lookup | Per candidate, inline sequential | Wyckoff veto; directional fallback |
| 3 — Regime reads | Regime/dealer/volatility reads ingested from the viewer/v2 handoff (§A1) as Pass-1 triage context where present; tickers without a handoff reading are fetched live (Polygon `avg_iv` for the Pass 1 IV source; dealer/volatility per DEALER/VOLATILITY). Dealer fields are re-fetched live from Schwab at Pass 2. | Per candidate | Dealer-timing veto; spread-mandate |
| 4 — Trigger evaluation | Direction resolved (regime-natural / operator-declared / `sos`–`sow` fallback) → Wyckoff veto (direction-aware) → dealer-timing veto → spread-mandate | Per candidate, fixed sequence | Eligible structure; resolved direction |
| 5 — Output assembly | Eligible / NO_TRADE / WAIT with rationale, candidate zones, alternatives | Per candidate | Pass 2 input; report input |
| 6 — Eligible-set summary | Surface eligible set for operator review | Once per run, after all candidates evaluated | Pass 2 entry gate |

**Pass 1 output state definitions.**

| Output state | Meaning | What it carries | Pass 2 disposition |
|---|---|---|---|
| Eligible | Candidate passed all applicable trigger gates; a structure and direction are determined | Structure, direction, candidate zone (strike range + DTE band), sizing band note, confidence, data-quality labels | Enters Pass 2 queue |
| NO_TRADE | Candidate refused for this screening run on a named basis | Named refusal reason, eligible alternatives with lower confidence, structure = NONE for primary. Full detail (Wyckoff read, dealer read, volatility read, alternatives, recheck trigger) renders in the Alternatives Summary section per REPORT_FORMAT_v4.0.0. | Does not enter Pass 2; alternatives may re-enter as separate candidates if operator directs |
| WAIT | Candidate is structurally screenable but a required input is degraded or absent | Named degraded input, recheck instruction, WAIT confidence below primary NO_TRADE. Full detail (Wyckoff read, dealer read, volatility read, recheck trigger) renders in the Alternatives Summary section per REPORT_FORMAT_v4.0.0. | Does not enter Pass 2 until input is refreshed and candidate is re-screened |
| WAIT — near event risk (block) | Earnings within EARNINGS_BLOCK_DAYS | Named earnings date and days remaining | Does not enter Pass 2; re-screens fresh in next session after earnings pass |
| WAIT — near event risk (caution) | Earnings within EARNINGS_CAUTION_DAYS, outside block window | Named earnings date, days remaining, operator-approval gate | Does not enter Pass 2 unless operator explicitly redirects in current session |

**Candidate zone format.**

| Zone field | Format | Example |
|---|---|---|
| Structure | Named structure label | Long call / Long put / Call debit spread / Put debit spread / CSP / LEAP (long call) |
| Direction | BULLISH / BEARISH / NEUTRAL | BULLISH |
| Strike zone | Price range relative to current spot, or delta range | ATM to 5% OTM / Slightly ITM to ATM |
| DTE band | Calendar day range | `SWING_DTE_BAND` (swing, per SYSTEM_PARAMS) / `CSP_DTE_BAND` (CSP, per SYSTEM_PARAMS) / `LEAP_DTE_BAND` (LEAP, per SYSTEM_PARAMS) |
| IV source label | Data-quality label when spread-mandate fires at Pass 1 | *Needs chain validation — spread-mandate fired on Pass 1 `iv_hv_ratio`; Pass 2 re-confirms* |

**Confidence band discipline.**

Specific base-confidence values and confidence deltas are MCP-internal output-formatting parameters documented in `engineering_only/PASS1_MCP_REFERENCE_v4.0.md` (forthcoming), preserving the v2.3 SIGNAL_009 reference values (base 75/60, deltas −20/−30) as engineering-only reference. The runtime band discipline is:

| Recommendation type | Confidence band | Ordering rule |
|---|---|---|
| Eligible primary | Upper band | Highest in the output for this candidate |
| NO_TRADE primary (Wyckoff veto cause) | Mid-upper band | Above WAIT alternative |
| NO_TRADE primary (other cause) | Mid band | Above WAIT alternative |
| WAIT alternative | Below primary | Strictly lower than primary |
| Structure alternative (when spread-mandate fires) | Below primary | Strictly lower than naked-structure primary would have been |
| Eligible alternatives (hostile-macro redirect) | Below primary | Strictly lower; surfaced in descending confidence order |

**Degraded-input conservative-default quick reference.**

| Degraded input | Trigger consequence | Primary output | Alternative |
|---|---|---|---|
| Wyckoff regime unconfirmed (operator declined/skipped) | Wyckoff veto fires | NO_TRADE | WAIT |
| Wyckoff reading flagged/estimation, operator not yet resolved | None — pending | WAIT | — |
| Dealer `confidence` = `invalid` (ticker) | Dealer-timing veto fires (long-premium) | NO_TRADE | WAIT |
| Dealer `confidence` = `low` (ticker) | No veto; floor-of-band sizing | Eligible — floor sizing noted | — |
| SPY dealer `confidence` = `invalid` / stale | Mixed macro; conservative read | Eligible set treated as mixed-macro | — |
| Volatility-status INVALID | Spread-mandate fires by default | Eligible — spread mandated; *Needs chain validation* | — |
| Pass 1 IV source unavailable | Spread-mandate fires by default | Eligible — spread mandated; source unavailable noted | — |
| Multiple inputs degraded | Most conservative applicable default | NO_TRADE with all named reasons | WAIT when structurally screenable |

**Hostile-macro eligible-set redirect (run-wide when macro gate fires).**

Per GUARDRAILS and DEALER. Reproduced here as Pass 1 quick reference.

| Structure | Eligible under hostile macro |
|---|---|
| Long calls | Refused (override required) |
| Long puts | Eligible |
| Call debit spreads | Refused (override required) |
| Put debit spreads | Eligible |
| Cash-secured puts | Eligible |
| LEAPs (long calls, 12+ months DTE) | Eligible |
| Equity hedges | Eligible |
| Closing existing positions | Always eligible |

**Engineering-only cross-reference.**

Content owned by `engineering_only/PASS1_MCP_REFERENCE_v4.0.md` (forthcoming) and not reproduced in this file:

| Content | v2.3 source anchor |
|---|---|
| Polygon MCP canonical endpoint names and parameter shapes for Pass 1 fetching | PIPELINE_010 |
| Batch cap enforcement (30 symbols per call) and deprecated-endpoint inventory | PIPELINE_010 |
| BC Score, Spring Score, and Composite Score pass-through constraint and storage bounds | SCORING_001 |
| Base confidence values (75/60) and delta bands (−20/−30) for fallback policy | SIGNAL_009 (v2.3 reference values) |
| Context compaction platform-behavior observation that motivated PIPELINE_011 | PIPELINE_011 |
