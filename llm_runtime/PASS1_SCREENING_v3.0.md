---
system: KapMan
doc_type: runbook
kb_version: 3.0.0-alpha
file_last_updated: 2026-05-11
status: draft
tier: T2
---

# PASS1 SCREENING

## Principle

Pass 1 screening is the eligible-set determination pass: it takes the operator's candidate list and returns, for each ticker, one of three outputs — Eligible, NO_TRADE, or WAIT — together with a recommended structure, a resolved direction, and candidate zones that Pass 2 uses to find specific contracts in the live chain. The governing judgment is that Pass 1's job is to compose all five regime inputs — Wyckoff phase (operator-confirmed via the propose-confirm protocol), dealer regime (MCP-delivered per DEALER), volatility regime (MCP-delivered per VOLATILITY, using Pass 1 IV source), macro state (SPY-derived, evaluated once per run before any per-candidate work begins), and the SIGNAL trigger contracts that convert those regime reads into eligibility and structure decisions — into a single coherent determination for each candidate, without producing any output that requires Pass 2 chain validation to be safe. The anti-hallucination floor is not a constraint imposed on Pass 1 from outside; it is what it means to be a Pass 1 output: every eligible candidate carries a structure (spread or naked), a direction (BULLISH, BEARISH, or NEUTRAL), and candidate zones expressed as price ranges and DTE bands — never exact strikes, never exact expirations, never risk-reward ratios — because those require the live Schwab chain that only Pass 2 has seen. When a regime input is degraded, the corresponding SIGNAL trigger fires at its conservative default, and the candidate receives a structured NO_TRADE or WAIT rather than a permissive read on incomplete data; a screening run with degraded inputs produces a shorter eligible set and a set of explicitly-reasoned refusals, not a set of unexamined approvals. Pass 1 data does not carry forward as authoritative into Pass 2: regime reads fetched at Pass 1 are starting context, not validated inputs — Pass 2 re-fetches what it needs, because context compaction in long screening sessions can silently approximate numeric values that Pass 2 decisions require to be exact.


## Operational heuristics

**The macro gate runs once per screening run, before any per-candidate evaluation begins.**

The hostile-macro composite is SPY-derived: both conditions must hold — SPY spot well below its gamma flip AND SPY DGPI in the weakening tier or worse (≤ −20) — for hostile macro to be active. The macro gate is evaluated first, before the candidate list is touched, because its result applies uniformly to every candidate in the run. When hostile macro is active, long-premium directional structures (long calls, long puts, call debit spreads) are refused for every candidate without per-candidate re-evaluation; the eligible-set redirect — CSPs, long puts, hedges, LEAPs — applies run-wide. When only one hostile-macro condition holds (SPY below flip with DGPI > −20, or SPY above flip with DGPI ≤ −20), the macro layer reads as mixed and is treated as the more conservative of the two readings throughout the run. When SPY dealer-status is LIMITED or INVALID, the macro layer is read with reduced confidence and the run output says so; macro regime is not asserted as supportive on weak SPY data, and the conservative read applies. A hostile-macro run is not an empty run — it is a redirected run, and the report surfaces the eligible alternatives explicitly for each candidate rather than returning a wall of refusals.

**A valid screening request has three elements; PASS1 treats each differently.**

The operator provides a candidate ticker list, optional context declarations, and optional override declarations. The ticker list is the work queue — every ticker on it receives a Pass 1 determination before the run closes; no ticker is silently skipped. Context declarations (operator-stated Wyckoff phases, sector notes, prior-session observations) are treated as operator-declared readings: authoritative for the session, but flagged as declared rather than propose-confirmed in the data-quality surface of the output. Override declarations (explicit macro-gate or veto overrides per GUARDRAILS) are applied per-request and noted in the report subtitle or footnote; they do not carry across to the next run. When the operator's request is ambiguous — the mode is unclear, the ticker list is absent, or an override declaration is incomplete — Pass 1 does not guess and produce output; it asks before proceeding.

**Wyckoff status is checked per candidate, in sequence, before trigger evaluation for that candidate.**

For each ticker in the candidate list, the first per-candidate question is whether an operator-confirmed Wyckoff phase reading exists in the current session. If a confirmed reading exists — either from the propose-confirm protocol run earlier in this session, or from an operator declaration at session start — the confirmed phase and any confirmed events are consumed directly and trigger evaluation proceeds. If no confirmed reading exists, the propose-confirm protocol runs inline for that ticker before evaluation: the runtime reads available MCP price and volume metrics, assembles a phase-and-event proposal with explicit metric reasoning, presents it to the operator, and waits for confirmation. Only after the operator confirms or corrects does trigger evaluation proceed for that ticker. If the operator declines to confirm or asks to skip the Wyckoff read for a ticker, that ticker is assigned UNKNOWN phase and all Wyckoff-dependent triggers degrade to their conservative defaults; trigger evaluation proceeds immediately on the conservative read without further delay. This inline-sequential ordering — propose-confirm for ticker N, evaluate ticker N, then move to ticker N+1 — keeps the propose-confirm exchange tightly coupled to the evaluation it governs and avoids front-loading the operator with a batch of confirmation prompts before any output is visible. The runtime does not re-propose for a ticker that already has a confirmed reading in the current session, even if the ticker appears multiple times in the candidate list.

**Trigger evaluation applies SIGNAL's entry-side contracts in a fixed sequence.**

For each candidate with a resolved Wyckoff status, the trigger sequence is: Wyckoff veto first, then dealer-timing veto, then spread-mandate. The Wyckoff veto is evaluated first because it is the strongest entry-side gate — a veto here ends long-premium eligibility for the candidate regardless of how supportive the dealer or volatility regime reads. If the Wyckoff veto does not fire, the dealer-timing veto is evaluated next using the per-ticker DGPI tier, flip-zone, near-flip flag, and dealer-status label delivered by MCP, plus the macro hostile-macro flag already established at Step 1. If the dealer-timing veto does not fire, the spread-mandate is evaluated using the Pass 1 IV source (Polygon `avg_iv`) and the IV/HV band it produces. The sequence stops at the first veto that fires for long-premium structures; when a veto fires, the candidate receives a NO_TRADE primary output with eligible alternatives surfaced, and the spread-mandate evaluation is skipped because there is no eligible structure to mandate a spread on. The spread-mandate is not a veto — it does not remove the candidate from the eligible set; it constrains the eligible structure to a vertical spread and shifts the sizing denominator accordingly.

**Direction is resolved for every eligible candidate before the candidate zone is assembled.**

Direction resolution follows a priority sequence. Primary signals — confirmed Wyckoff phase alignment with a post-Spring accumulation or confirmed markup (BULLISH), confirmed distribution or markdown (BEARISH), or a confirmed dealer regime read that is unambiguous — resolve direction when they are present and in agreement. When primary signals are absent or in conflict, the Wyckoff-event directional fallback applies: confirmed SOS → BULLISH, confirmed SOW → BEARISH, neither confirmed → NEUTRAL. The operator can override the NEUTRAL fallback by stating direction explicitly in the screening request, per GUARDRAILS override discipline. A candidate that resolves to NEUTRAL receives a NEUTRAL-direction eligible output; the eligible structure for a NEUTRAL candidate is typically a defined-risk spread or CSP rather than a directional naked position. Direction is resolved at Pass 1 and carried into the candidate zone; Pass 2 consumes the resolved direction without re-deriving it.

**The Pass 1 IV source is Polygon `avg_iv`; its outputs are labeled accordingly.**

IV/HV band computation at Pass 1 uses the Polygon options-metrics endpoint as the IV source — single-symbol for one ticker, batch (capped at 30 symbols per call) for multiple tickers. The resulting IV/HV band is a valid Pass 1 classification for directional screening and for the spread-mandate's firing condition. When the spread-mandate fires on Pass 1 IV, the eligible-set output carries a *Needs chain validation* label on the spread-mandate determination, because the definitive mandate requires the Schwab ATM IV source that only Pass 2 has access to. The spread-mandate fires by default when the Pass 1 IV source is unavailable (source-substitution is never silent); the candidate receives a spread-mandated output labeled accordingly. Pass 1 never uses Schwab ATM chain IV — that is a Pass 2 source — and never substitutes Pass 2 source data for Pass 1 source data even if it appears available in the conversation context.

**Pass 1 outputs are candidate zones, not validated specifics.**

Every eligible candidate output contains: the resolved structure (long call, long put, debit spread, CSP, or LEAP), the resolved direction (BULLISH, BEARISH, or NEUTRAL), a candidate strike zone expressed as a price range relative to current spot (e.g., "ATM to slightly OTM"), and a DTE target band appropriate to the intended trade horizon (`SWING_DTE_BAND` for swing trades, `CSP_DTE_BAND` for cash-secured puts, `LEAP_DTE_BAND` for LEAPs, per SYSTEM_PARAMS). Exact strikes, exact expiration dates, entry prices, stop-loss prices, profit targets, and risk-reward ratios are never produced at Pass 1 — these require Pass 2 chain validation. When a candidate's structure would naturally call for a specific level (e.g., a CSP candidate's put strike), Pass 1 expresses it as a zone anchored to structural levels (e.g., "below the current support shelf, ATM to 5% OTM") rather than as a price or delta. Confidence values are assigned per the band discipline in the Appendix; alternatives carry strictly lower confidence than the primary.

**Degraded inputs degrade outputs — the conservative default is the safety mechanism.**

When any regime input is degraded, the dependent SIGNAL trigger fires at its conservative default, and the candidate receives the conservative output. The degraded cases and their outputs are:

| Degraded input | Conservative default behavior | Pass 1 output |
|---|---|---|
| Wyckoff phase unconfirmed (propose-confirm declined or skipped) | Wyckoff veto fires | NO_TRADE — Wyckoff phase unconfirmed; WAIT alternative |
| Dealer-status INVALID (per-ticker) | Dealer-timing veto fires for long-premium candidates | NO_TRADE — dealer regime absent; WAIT alternative |
| Dealer-status LIMITED (per-ticker) | Full dealer read; sizing restricted to floor-of-band | Eligible at floor sizing; rationale notes LIMITED data |
| SPY dealer-status INVALID or stale | Macro layer read with reduced confidence; conservative macro read applied | Eligible set treated as mixed-macro; rationale notes degraded SPY data |
| Volatility-status INVALID (per-ticker) | Spread-mandate fires by default | Eligible — spread mandated; *Needs chain validation* label |
| Pass 1 IV source unavailable | Spread-mandate fires by default | Eligible — spread mandated; source-unavailable noted |
| Multiple inputs simultaneously degraded | Most conservative applicable default; WAIT unless structural alignment is unambiguous | NO_TRADE with named reasons; WAIT alternative when candidate is structurally screenable |

A WAIT output means: the candidate is structurally screenable but a required input is degraded or missing; the candidate is not refused — it is deferred until the input is refreshed. A NO_TRADE output means: the candidate is refused for this screening run on the named basis; it does not enter a retry state within this run.

**Pass 1 data does not carry forward as authoritative into Pass 2.**

Regime reads established at Pass 1 — dealer metrics, volatility metrics, Polygon IV values — are starting context for the screening run, not validated inputs that Pass 2 may reuse. Pass 2 re-fetches dealer metrics fresh from Schwab regardless of whether Pass 1 values appear present in the conversation context, because context compaction in long screening sessions can silently approximate numeric values that Pass 2 strike selection and spread-mandate validation require to be exact. This is not a soft recommendation — it is a hard operational boundary. The only Pass 1 outputs that carry forward with full authority into Pass 2 are the operator-confirmed Wyckoff readings (which are session-scoped and owned by WYCKOFF's propose-confirm protocol) and the resolved direction and structure determinations (which are Pass 1's primary deliverable to Pass 2). Numeric regime values do not carry forward.

**The eligible-set summary surfaces before Pass 2 begins.**

After all candidates have been evaluated, Pass 1 assembles and surfaces the eligible set — every candidate that received an Eligible output, with its structure, direction, and candidate zones — for operator review before Pass 2 begins. Candidates that received NO_TRADE or WAIT outputs are listed with their reasons. The operator may add, remove, or redirect candidates at this point before Pass 2 begins; any addition at this stage must go through the Pass 1 trigger sequence before it enters the eligible set. Pass 2 does not begin until the operator has reviewed the eligible-set summary.


## Workflow integration

**Position in the document hierarchy.**

PASS1 SCREENING is tier T2 — a runbook. It is the primary consumer of every T1 principle file in the system and the entry point through which operator screening requests become structured eligible-set determinations. PASS1 does not own any regime vocabulary, trigger contract, or override mechanic — it invokes the contracts that the T1 files define and assembles their outputs into a per-candidate determination. When PASS1 and a T1 file appear to conflict, the T1 file's contract governs; when PASS1 and GUARDRAILS appear to conflict, GUARDRAILS governs. PASS1 is the procedural layer; the T1 files are the judgment layer.

**What PASS1 receives from each upstream file.**

| Source file | What PASS1 consumes | How PASS1 uses it |
|---|---|---|
| `KAPMAN_GUARDRAILS_v3.0.md` (T0) | Data-quality vocabulary; override discipline; hostile-macro eligible-set redirect; anti-hallucination floor | PASS1 applies the data-quality labels to every degraded output; applies override discipline at the screening-request entry point; applies the hostile-macro redirect run-wide when macro gate fires; enforces the anti-hallucination floor on every candidate zone |
| `DEALER_v3.0.md` (T1) | SPY hostile-macro composite (both conditions); per-ticker DGPI tier, flip-zone, near-flip flag, dealer-status label; macro-layer dealer-status | PASS1 evaluates the hostile-macro composite once at run start; reads per-ticker dealer regime for the dealer-timing veto; reads near-flip flag for the one-tier sizing step-down note in the candidate output |
| `VOLATILITY_v3.0.md` (T1) | IV/HV band (Pass 1 source: Polygon `avg_iv`); IV rank tier; volatility-status label; source-authority discipline | PASS1 uses Pass 1 IV source for the spread-mandate firing condition; applies *Needs chain validation* label when the mandate fires on Pass 1 source; degrades to fire-by-default when Pass 1 source is unavailable |
| `WYCKOFF_v3.0.md` (T1) | Propose-confirm protocol; confirmed phase and event readings; UNKNOWN state; conservative-default behavior; operator-declared phase handling | PASS1 invokes propose-confirm inline per candidate for unconfirmed tickers; consumes confirmed phase for Wyckoff veto evaluation; consumes confirmed SOS/SOW for directional fallback; assigns UNKNOWN and conservative defaults when propose-confirm is declined |
| `SIGNAL_v3.0.md` (T1) | Wyckoff veto contract (heuristic 1); dealer-timing veto contract (heuristic 2); spread-mandate contract (heuristic 3); directional fallback (heuristic 11); NO_TRADE consistency (heuristic 7); alternative-confidence ordering (heuristic 8); degraded-input fallback (heuristic 9); anti-hallucination floor (heuristic 10) | PASS1 applies the trigger contracts in fixed sequence per candidate; assembles NO_TRADE outputs with NONE structure; assigns confidence values that honor the ordering rule; applies structured fallback on degraded inputs |
| `RISK_v3.0.md` (T1) | Sizing band ladder (phase-ceiling → dealer-tier → volatility-tier); near-flip one-tier step-down | PASS1 notes the applicable sizing band in the candidate output so Pass 2 and the operator have the sizing context; PASS1 does not compute exact position size — that is RISK and operator work |

**What PASS1 hands to each downstream file.**

| Destination file | What PASS1 delivers | How that file uses it |
|---|---|---|
| `PASS2_VALIDATION_v3.0.md` (T2) | Eligible-set: per-candidate structure, direction, candidate zones, DTE band, Pass 1 IV source label, sizing band note, confidence value | PASS2 takes each eligible candidate and validates the structure and direction against the live Schwab chain; selects specific strikes and expirations within the candidate zones; confirms or overrides the spread-mandate using Pass 2 IV source |
| `REPORT_FORMAT_v3.0.md` (T3) | Full Pass 1 output: Eligible/NO_TRADE/WAIT determinations with rationale, candidate zones, alternatives with confidence, data-quality labels, macro gate result, override acknowledgments | REPORT_FORMAT renders the Pass 1 section of the screening report; PASS1 does not own report rendering |
| `REPORT_STYLE_v3.0.md` (T3) | (Indirectly) the Pass 1 output surface | REPORT_STYLE governs field length caps, label vocabulary, and rationale density; PASS1 respects these constraints in the rationale text it assembles |
| `PORTFOLIO_MGMT_v3.0.md` (T2) | (Indirectly, after Pass 2) The entry-time regime snapshots that Pass 2 completes | PORTFOLIO_MGMT carries regime snapshots in position context; PASS1 is the regime-read origin for the Wyckoff phase and direction that eventually become the entry-time snapshot |

**What PASS1 does not own.**

| Concern | Owner |
|---|---|
| Trigger contracts and firing conditions | `SIGNAL_v3.0.md` |
| Phase and event vocabulary | `WYCKOFF_v3.0.md` |
| Propose-confirm mechanics | `WYCKOFF_v3.0.md` |
| Dealer regime tier vocabulary | `DEALER_v3.0.md` |
| IV/HV band vocabulary and source-authority rules | `VOLATILITY_v3.0.md` |
| Sizing band ladder and near-flip step-down math | `RISK_v3.0.md` |
| Override discipline | `KAPMAN_GUARDRAILS_v3.0.md` |
| MCP tool-surface endpoint names, batch caps, parameter shapes | `engineering_only/PASS1_MCP_REFERENCE_v3.0.md` (forthcoming) |
| Chain validation, exact strikes, expiration selection | `PASS2_VALIDATION_v3.0.md` |
| Report rendering and field length caps | `REPORT_FORMAT_v3.0.md`, `REPORT_STYLE_v3.0.md` |
| Position monitoring and portfolio management | `PORTFOLIO_MGMT_v3.0.md` |

**Entry point for every Pass 1 run.**

Before per-candidate evaluation begins, three conditions must hold:

1. Mode is established as Screening or Hybrid — PASS1 does not run in Portfolio mode. If mode is ambiguous, GUARDRAILS requires asking before producing output.
2. The macro gate has been evaluated — SPY dealer metrics have been fetched in the current session and the hostile-macro composite has been resolved. If SPY dealer metrics are absent or stale, the macro layer reads with reduced confidence and the run proceeds on the conservative macro read; the run does not block on SPY data, but the output surfaces the degraded SPY status explicitly.
3. The candidate ticker list is present — if the operator's request contains no tickers, PASS1 asks for the list before proceeding.

**Cross-references this file expects to be honored.**

- `SIGNAL_v3.0.md` owns the trigger contracts PASS1 enforces. When SIGNAL and PASS1 appear to specify different firing conditions for the same trigger, SIGNAL governs.
- `WYCKOFF_v3.0.md` owns the propose-confirm protocol PASS1 invokes. PASS1 specifies *when* propose-confirm runs in the screening workflow; WYCKOFF specifies *how* it runs.
- `KAPMAN_GUARDRAILS_v3.0.md` owns the override discipline and the anti-hallucination floor. Neither may be relaxed by PASS1 heuristics, even implicitly.
- `VOLATILITY_v3.0.md` owns the IV source-authority rules. PASS1's use of Polygon `avg_iv` as Pass 1 source is an application of VOLATILITY's source-authority discipline, not an independent PASS1 decision.
- `engineering_only/PASS1_MCP_REFERENCE_v3.0.md` (forthcoming) owns the specific MCP tool-surface contracts for Pass 1 data fetching — endpoint names, batch caps, parameter shapes, and the Polygon deprecated-endpoint inventory. PASS1 is silent on these; operators and engineers consult the engineering-only reference for tool-surface details.


## Legacy anchors (for legend citations and back-compat)

**PIPELINE_010** → `engineering_only/PASS1_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 rule consolidated all Polygon MCP tool-surface routing decisions for Pass 1 data fetching: canonical endpoint names (`get_options_metrics`, `get_batch_options_metrics` with `include=['volatility']`), batch cap of 30 symbols per call, and the full inventory of deprecated endpoints that must never be called. These are MCP tool-surface contracts with no LLM runtime effect — the runtime reads delivered outputs; it does not select endpoints or enforce batch caps. The one behavioral residue that surfaces at the runtime layer is the data-quality consequence of the source-authority discipline (Polygon `avg_iv` as Pass 1 source, labeled *Needs chain validation* for spread-mandate outputs), which is owned by `VOLATILITY_v3.0.md` and applied by this file's heuristic "The Pass 1 IV source is Polygon `avg_iv`; its outputs are labeled accordingly." The full endpoint inventory, batch-cap enforcement, and deprecated-endpoint prohibition live in engineering-only. Body-text references in legacy report legends (e.g., "Rules applied: PIPELINE_010") remain valid; the legend entry resolves to the engineering-only destination.

**PIPELINE_011** → § Operational heuristics, "Pass 1 data does not carry forward as authoritative into Pass 2." The v2.3 rule was a hard operational guard against context compaction in long screening sessions: Pass 2 must always re-fetch Schwab dealer metrics live, never reusing Pass 1 values even if they appear present in conversation history, because compaction can silently approximate numeric values that Pass 2 decisions require to be exact. The behavioral intent — that Pass 1 numeric regime reads are starting context, not validated inputs — is load-bearing for the runtime and is preserved in the heuristic as the standing Pass 1 / Pass 2 data-boundary rule. The specific compaction behavior that motivated the rule (Claude Sonnet 4.6 / Opus 4.6 context compaction active in beta as of 2026-03) is a platform-behavior observation documented in the v2.3 source; the runtime rule it produced is durable regardless of whether compaction behavior changes. Body-text references in legacy report legends (e.g., "Rules applied: PIPELINE_011") remain valid.

**SCORING_001** → `engineering_only/PASS1_MCP_REFERENCE_v3.0.md` (forthcoming). The v2.3 rule established that BC Score, Spring Score, and Composite Score are pass-through context values only — no formula computation occurs anywhere in the active pipeline, and no entry should be blocked or approved based solely on Composite Score until a formula and threshold are formally implemented. In v3.0 this situation is unchanged: the scoring modules remain unimplemented, and PASS1 does not gate entries on these scores. The pass-through constraint and the storage bounds (BC Score 0–28, Spring Score 0–12) are preserved in engineering-only as reference against the schema and the `c4_batch_ai_screening_job.py` payload. The v3.0 runtime does not reference these scores in any trigger evaluation or eligible-set determination. Body-text references in legacy report legends (e.g., "Rules applied: SCORING_001") remain valid; the legend entry resolves to the engineering-only destination.


## Appendix — formulas and reference tables

**Pass 1 screening workflow — step summary.**

| Step | What runs | Scope | Governs |
|---|---|---|---|
| 1 — Macro gate | SPY hostile-macro composite evaluation | Once per run, before any per-candidate work | All candidates in the run |
| 2 — Wyckoff status | Propose-confirm (if unconfirmed) or confirmed-reading lookup | Per candidate, inline sequential | Wyckoff veto; directional fallback |
| 3 — Regime reads | MCP fetch: per-ticker dealer metrics, volatility metrics (Pass 1 IV source) | Per candidate | Dealer-timing veto; spread-mandate |
| 4 — Trigger evaluation | Wyckoff veto → dealer-timing veto → spread-mandate; direction resolution | Per candidate, fixed sequence | Eligible structure; resolved direction |
| 5 — Output assembly | Eligible / NO_TRADE / WAIT with rationale, candidate zones, alternatives | Per candidate | Pass 2 input; report input |
| 6 — Eligible-set summary | Surface eligible set for operator review | Once per run, after all candidates evaluated | Pass 2 entry gate |

**Pass 1 output state definitions.**

| Output state | Meaning | What it carries | Pass 2 disposition |
|---|---|---|---|
| Eligible | Candidate passed all applicable trigger gates; a structure and direction are determined | Structure, direction, candidate zone (strike range + DTE band), sizing band note, confidence, data-quality labels | Enters Pass 2 queue |
| NO_TRADE | Candidate refused for this screening run on a named basis | Named refusal reason, eligible alternatives with lower confidence, structure = NONE for primary | Does not enter Pass 2; alternatives may re-enter as separate candidates if operator directs |
| WAIT | Candidate is structurally screenable but a required input is degraded or absent | Named degraded input, recheck instruction, WAIT confidence below primary NO_TRADE | Does not enter Pass 2 until input is refreshed and candidate is re-screened |

**Candidate zone format.**

| Zone field | Format | Example |
|---|---|---|
| Structure | Named structure label | Long call / Long put / Call debit spread / Put debit spread / CSP / LEAP (long call) |
| Direction | BULLISH / BEARISH / NEUTRAL | BULLISH |
| Strike zone | Price range relative to current spot, or delta range | ATM to 5% OTM / Slightly ITM to ATM |
| DTE band | Calendar day range | `SWING_DTE_BAND` (swing, per SYSTEM_PARAMS) / `CSP_DTE_BAND` (CSP, per SYSTEM_PARAMS) / `LEAP_DTE_BAND` (LEAP, per SYSTEM_PARAMS) |
| IV source label | Data-quality label when spread-mandate fires on Pass 1 source | *Needs chain validation — spread-mandate fired on Polygon avg_iv; Pass 2 confirms* |

**Confidence band discipline.**

Specific base-confidence values and confidence deltas are MCP-internal output-formatting parameters documented in `engineering_only/PASS1_MCP_REFERENCE_v3.0.md` (forthcoming), preserving the v2.3 SIGNAL_009 reference values (base 75/60, deltas −20/−30) as engineering-only reference. The runtime band discipline is:

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
| Wyckoff unconfirmed | Wyckoff veto fires | NO_TRADE | WAIT |
| Dealer-status INVALID (ticker) | Dealer-timing veto fires (long-premium) | NO_TRADE | WAIT |
| Dealer-status LIMITED (ticker) | No veto; floor-of-band sizing | Eligible — floor sizing noted | — |
| SPY dealer INVALID / stale | Mixed macro; conservative read | Eligible set treated as mixed-macro | — |
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

Content owned by `engineering_only/PASS1_MCP_REFERENCE_v3.0.md` (forthcoming) and not reproduced in this file:

| Content | v2.3 source anchor |
|---|---|
| Polygon MCP canonical endpoint names and parameter shapes for Pass 1 fetching | PIPELINE_010 |
| Batch cap enforcement (30 symbols per call) and deprecated-endpoint inventory | PIPELINE_010 |
| BC Score, Spring Score, and Composite Score pass-through constraint and storage bounds | SCORING_001 |
| Base confidence values (75/60) and delta bands (−20/−30) for fallback policy | SIGNAL_009 (v2.3 reference values) |
| Context compaction platform-behavior observation that motivated PIPELINE_011 | PIPELINE_011 |
