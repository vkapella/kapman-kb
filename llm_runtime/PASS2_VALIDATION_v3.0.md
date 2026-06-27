---
system: KapMan
doc_type: runbook
kb_version: 3.0.1
file_last_updated: 2026-06-27
status: active
tier: T2
---

# PASS2 VALIDATION

## Principle

Pass 2 is the validation pass: it takes the eligible set that Pass 1 delivers and converts candidate zones into trade-ready contract specifications by interrogating the live Schwab option chain. The judgment Pass 2 exercises is not a re-screening — it does not re-evaluate whether a candidate should be traded; Pass 1 owns that determination. Pass 2's judgment is about what, exactly, can be traded: which strike, which expiration, at what structure, at what entry price range, given what the chain actually shows. The output of that judgment is either a validated trade specification — exact strike, exact expiration, confirmed structure, entry price range, sizing band — ready for the operator to execute, or a named disposition explaining why the specification could not be completed.

Three events govern every Pass 2 run. First, dealer metrics are re-fetched fresh from Schwab regardless of what Pass 1 established — numeric regime values do not carry forward, and the wall levels and DGPI that inform strike selection must reflect the chain as it exists at validation time, not at screening time. Second, the spread-mandate determination that Pass 1 labeled *Needs chain validation* is resolved definitively using the Schwab ATM chain IV that only Pass 2 has access to: the mandate is either confirmed, overridden, or fires by default when the chain cannot support the IV/HV computation. Third, the Schwab chain itself is classified for quality — Full, Limited, or Weak — and that classification governs whether the resulting specification is trade-ready, flagged for operator review, or rejected as unspecifiable from the available data.

Pass 2 does not produce exact strikes or expirations by assertion. It produces them by selection from a validated chain, within the candidate zones and DTE bands that Pass 1 established, informed by wall levels and chain quality. When the chain cannot support that selection — because it is truncated, too thin, or absent for the relevant zone — the output reverts to zones with a named data-quality label rather than to invented specifics. The anti-hallucination floor does not lift at Pass 2; it narrows: exact values are permitted only to the extent the chain has been validated.

## Operational heuristics

**Pass 2 begins with the PASS1 eligible set as its entry contract — and only that.**

The entry contract for every Pass 2 run is the eligible-set output that Pass 1 produced in the current session: per-candidate structure, direction, candidate zones, DTE band, Pass 1 IV source label, sizing band note, and confidence value. Pass 2 does not accept candidates that did not clear Pass 1. Pass 2 does not re-evaluate the Wyckoff veto, the dealer-timing veto, or the hostile-macro gate — those determinations are Pass 1's and are carried forward with full authority. The one Pass 1 output that Pass 2 may surface for operator review rather than consume silently is regime drift: when the fresh Pass 2 dealer fetch shows a material change since Pass 1 ran, Pass 2 names the drift before proceeding on the affected candidates. It does not silently apply a new veto; the Pass 1 determination is the baseline.

**Dealer metrics are re-fetched fresh at the start of every Pass 2 run — this is not optional.**

Before any chain fetch, Pass 2 re-fetches Schwab dealer metrics for every candidate ticker and for SPY. The wall levels and DGPI tier that inform strike selection must come from this fresh fetch, not from values established at Pass 1 or compacted in conversation context. A Pass 2 run that reuses Pass 1 dealer values for strike selection violates the data boundary that PIPELINE_011 (now owned by PASS1) established and that Pass 2 is required to enforce on its own behalf. The fresh fetch also produces the dealer-status label (FULL / LIMITED / INVALID) that Pass 2 reads alongside chain quality as two independent dimensions of data confidence.

**Regime drift is a named heuristic, not an implicit behavior.**

When the fresh Pass 2 dealer fetch reveals a material regime change relative to Pass 1 context — SPY has crossed below its flip level, a per-ticker DGPI tier has moved two or more tiers, or a near-flip flag has become newly active on a candidate ticker — Pass 2 surfaces the drift explicitly before proceeding on the affected candidates. The operator decides whether to re-screen the affected candidates or proceed on the Pass 1 baseline with the drift noted. Pass 2 does not independently veto a candidate based on drift; it returns the candidate to the operator's judgment with the drift named and the implication stated. Candidates not affected by the drift proceed to chain fetch without interruption. When drift is minor — a DGPI tier shift of one, a wall level move within the candidate zone — Pass 2 notes it in the output rationale without pausing. The materiality thresholds for what triggers a pause versus a rationale note are in the Appendix.

**Chain fetch scope is bounded by the PASS1 candidate zone and DTE band.**

For each eligible candidate, Pass 2 fetches the Schwab option chain constrained to the candidate zone and DTE band that Pass 1 specified. The chain fetch does not re-open the full chain; it fetches within the zone to limit result set size and reduce the probability of PIPELINE_012 truncation. When the candidate zone is narrow and the DTE band is the swing trade range per `SWING_DTE_BAND` in SYSTEM_PARAMS, a single targeted fetch typically covers the zone. When the candidate is a LEAP (DTE band per `LEAP_DTE_BAND` in SYSTEM_PARAMS), the fetch targets the LEAPS expiration calendar within the band, which is sparser than the standard chain; LEAP chain fetches are expected to return fewer contracts and wider bid/ask spreads, and that expectation is reflected in chain quality classification for LEAPs.

**When a chain fetch appears truncated, reduce and re-fetch before classifying — never treat a truncated chain as complete.**

A chain fetch result that shows fewer contracts than expected for the zone and DTE band, missing far strikes within the zone, or incomplete expiration coverage within the DTE band is a truncation signal per PIPELINE_012. When truncation is suspected, Pass 2 reduces the strike count parameter and re-fetches, or splits the fetch by targeted expiration, before classifying chain quality or selecting strikes. A chain that has not been confirmed complete cannot be classified Full. If the re-fetch resolves the truncation, classification proceeds on the complete result. If the re-fetch does not resolve it, the chain is classified at its actual quality level with the truncation noted, and the output for the affected candidate is Flagged rather than Validated. The numeric strike-count parameters and the re-fetch mechanics belong in `engineering_only/PASS2_MCP_REFERENCE_v3.0.md`; the behavioral contract — never treat a truncated chain as complete — is this file's to own.

**Chain quality classification is Pass 2's data-quality gate, independent of dealer-status.**

Every chain fetch produces a chain quality classification: Full, Limited, or Weak. This classification is independent of the dealer-status label (FULL / LIMITED / INVALID) that the fresh dealer fetch produces. Both dimensions apply simultaneously. Chain quality thresholds (contract count floors, bid/ask spread limits, OI floors per contract) are MCP-internal parameters that belong in `engineering_only/PASS2_MCP_REFERENCE_v3.0.md`. The runtime classification vocabulary — Full, Limited, Weak — and the behavioral consequence for each combination with dealer-status are this file's to own. The combination matrix is in the Appendix.

**The spread-mandate is resolved definitively at Pass 2 — three outcomes, no others.**

When Pass 1 delivered a candidate with a *Needs chain validation* label on its spread-mandate determination, Pass 2 resolves that label to one of three states using the Schwab ATM chain IV at the nearest-to-money strike as the Pass 2 IV source, per VOLATILITY's source-authority discipline. The three outcomes and their conditions are in the Appendix. A Pass 2 output that carries *Needs chain validation* forward unresolved is incomplete and must not be delivered to the operator as Validated. When the mandate fires by default, the candidate may still be Validated or Flagged depending on chain quality — the default-fire state constrains structure, it does not by itself reject the candidate.

**Strike selection navigates from the candidate zone to a specific strike using the validated chain, informed by wall levels.**

Once chain quality is classified and the spread-mandate is resolved, strike selection operates within the candidate zone that Pass 1 specified. When multiple strikes fall within the candidate zone, the selection prefers the strike with the best combination of liquidity (OI and bid/ask spread) and structural alignment (proximity to Wyckoff structural levels from the confirmed phase reading). A strike at the boundary of the candidate zone is acceptable when liquidity is materially better there than at interior strikes. A strike outside the candidate zone is not selected; if no strike within the zone meets the minimum liquidity floor, the candidate is Flagged with a named reason (no valid strike in zone) rather than widened silently.

Wall levels from the fresh dealer fetch inform but do not veto strike selection. For a bullish candidate, the selected call strike is evaluated against the nearest call wall: when the wall sits between the entry strike and a reasonable profit target, that structural headwind is noted in the output rationale. For a bearish candidate, the put wall informs the short leg of a put spread. Wall levels do not independently prevent a strike selection; they shape the rationale and may prompt the operator to reconsider. When wall levels are absent or stale from the fresh fetch, strike selection proceeds without them and the rationale notes the absence.

For LEAP candidates, strike selection targets the slightly ITM to ATM delta range — higher delta reduces time-decay sensitivity relative to far-OTM strikes — within the LEAPS expiration calendar available in the DTE band per `LEAP_DTE_BAND` in SYSTEM_PARAMS. LEAP chain quality typically classifies Limited or Weak due to lower OI and wider bid/ask spreads at far expiries; a Limited classification on a LEAP chain is not a validation failure. Strike selection for LEAPs tolerates wider bid/ask spreads than swing-trade chains, and that tolerance is noted explicitly in the output rather than silently applied.

**Expiration selection picks the available expiration within the DTE band that best balances time buffer against theta decay.**

From the expirations available in the validated chain within the Pass 1 DTE band, Pass 2 selects the expiration that best balances time buffer against theta decay. For swing trades, this generally favors expirations toward the longer end of the `SWING_DTE_BAND` when multiple expirations are available within it. For CSPs, expiration selection targets the range within `CSP_DTE_BAND` where theta decay accelerates most efficiently for premium-selling structures. For LEAPs, Pass 2 selects the nearest available LEAPS expiration within the `LEAP_DTE_BAND`; LEAPS calendars are sparse and exact-midpoint targeting is not meaningful. When no expiration falls within the DTE band, the candidate is Flagged with a named reason (no valid expiration in DTE band) rather than selecting outside the band without operator acknowledgment. When two expirations are equidistant within the band, the later expiration is preferred for swing trades and spread structures.

**CSP validation follows a distinct path from directional spread validation.**

A CSP candidate from Pass 1 does not go through spread-mandate resolution — CSPs are defined-risk from the premium-selling side and the mandate does not apply. CSP validation at Pass 2 evaluates: the put strike zone against the ticker's support structure and put wall from the fresh dealer fetch; the expiration within `CSP_DTE_BAND` per SYSTEM_PARAMS; and the entry premium relative to the notional (yield on capital). Chain quality classification applies to CSP candidates identically to directional candidates. When the put strike zone and put wall are in conflict — the put wall sits above the candidate strike zone, suggesting dealer support that could pin the underlying above the short put — the rationale notes the structural alignment; it does not override the strike selection.

**The entry price range is a bid/ask bracket from the validated chain snapshot — no exact fill price is promised.**

Pass 2 produces an entry price range expressed as the bid/ask midpoint ± half-spread, or as the bid/ask bracket, sourced from the chain snapshot at the time of the Pass 2 fetch. This range is what the operator uses to set limit orders; it is not a fill guarantee. The range narrows as chain quality improves. For spread structures, the entry price range covers the net debit or net credit; the individual leg prices are not promised separately. When the bid/ask spread is wider than a threshold that makes the entry price range operationally useless (chain quality Weak), the candidate is Flagged rather than Validated.

**Sizing adjustments at Pass 2 are chain-quality-driven and inherit the PASS1 sizing band note.**

Pass 2 inherits the sizing band note from Pass 1 and may step it down based on Pass 2 chain quality, per RISK's band ladder. A Limited chain warrants a one-tier sizing step-down even when the Pass 1 sizing band note reflects a Full allocation. A Weak chain warrants a two-tier step-down, or a Flagged output with the sizing caveat named. The step-down is noted explicitly in the Pass 2 output; the operator sees both the Pass 1 sizing band note and the Pass 2 adjustment. Pass 2 does not step sizing up from the Pass 1 note — sizing adjustments at Pass 2 are defensive only.

**Pass 2 output states are Validated, Flagged, or Rejected — no intermediate states.**

Every candidate that enters Pass 2 exits in one of three states. Flagged is not Rejected: a Flagged candidate is potentially executable after operator review; a Rejected candidate is not executable from the current chain. The distinction matters for the validated-set summary: Flagged candidates appear in the summary with their caveat named; Rejected candidates are removed from the summary with their rejection reason noted separately. A candidate that was Validated or Flagged at Pass 2 is not demoted to Rejected by the operator's decision not to trade it — that is a portfolio decision, not a validation outcome. Output state definitions and minimum content requirements are in the Appendix.

**The validated-set summary is the final pre-trade output — it surfaces before execution, not after.**

After all candidates have been processed, Pass 2 assembles the validated-set summary for operator review before any execution action is taken. The summary presents Validated candidates first (in descending confidence order, per SIGNAL heuristic 8's alternative-confidence ordering applied to the validated set), then Flagged candidates with their named caveats, then Rejected candidates with their named rejection reasons. The summary is the handoff to PORTFOLIO_MGMT; no candidate moves to execution without appearing in this summary. The operator may decline any Validated candidate, acknowledge any Flagged candidate for execution, or accept any Rejected candidate's disposition — those are operator decisions. Pass 2 does not initiate execution.

**At validation, capture the entry-time snapshot into `positions.md` — write-once, and never read back at Pass 2.**

When a candidate is validated, Pass 2 captures three things into `kapman-journal/memory/positions.md` so Portfolio's Regime exit advisory can later measure decay against the conditions the trade was opened under: the entry-time regime snapshot (entry Wyckoff phase, DGPI tier, flip-zone, IV/HV band, vol-status), the eight SIGNAL Stop/Profit alert levels, and `option_mid` — the validated-chain bid/ask midpoint at entry. The regime snapshot and the eight SIGNAL levels are the one regime read Pass 2 persists: the sole exemption to the numeric-no-persist floor, written as immutable historical entry context — a record, not an authority — never re-read to seed a Pass 1 or Pass 2 decision, since a fresh decision always re-fetches the live regime. `option_mid` rides alongside as a position fact, not a regime read. Pass 2 owns only the trigger and timing of this write — validation of a new entry; `JOURNAL_MGMT_v4.0` owns the path, schema, and write-once mechanics, and `KAPMAN_GUARDRAILS` owns the exemption. The capture changes neither the Pass 1 → Pass 2 boundary nor the anti-hallucination floor: Pass 2 still validates from the live chain and persists a record, not an authority.

## Workflow integration

**What PASS2 receives from each upstream file.**

| Source file | What PASS2 consumes | How PASS2 uses it |
|---|---|---|
| `PASS1_SCREENING_v3.0.md` (T2) | Per-candidate eligible-set output: structure, direction, candidate zones, DTE band, Pass 1 IV source label, sizing band note, confidence value | Entry contract for every Pass 2 run; PASS2 does not re-derive any of these |
| `KAPMAN_GUARDRAILS_v3.0.md` (T0) | Anti-hallucination floor; data-quality vocabulary; override discipline | PASS2 enforces the floor on every output; exact strikes and expirations appear only from validated chain; data-quality labels applied throughout |
| `DEALER_v3.0.md` (T1) | Fresh dealer-status label (FULL / LIMITED / INVALID); call/put wall levels; DGPI tier; near-flip flag | Re-fetched fresh at Pass 2 start; wall levels inform strike selection; dealer-status combined with chain quality for output-state determination |
| `VOLATILITY_v3.0.md` (T1) | Pass 2 IV source (Schwab ATM chain per-contract IV); IV/HV band; IV rank tier; volatility-status label; source-authority discipline | Spread-mandate resolution: IV/HV band and IV rank tier determine confirmed / overridden / fire-by-default outcome |
| `SIGNAL_v3.0.md` (T1) | Spread-mandate contract (heuristic 3); anti-hallucination floor (heuristic 10); alternative-confidence ordering (heuristic 8) | PASS2 enforces the spread-mandate's three-outcome resolution; honors anti-hallucination floor on truncated chains; orders validated-set summary by descending confidence |
| `WYCKOFF_v3.0.md` (T1) | Operator-confirmed phase and event readings; structural levels from confirmed phase | Structural levels inform strike selection anchoring within the candidate zone |
| `RISK_v3.0.md` (T1) | Sizing band ladder; chain-quality sizing step-down discipline | PASS2 inherits Pass 1 sizing band note and may step down based on Pass 2 chain quality; step-down direction and magnitude follow RISK's band ladder |
| `SYSTEM_PARAMS_v3.0.md` (T3) | `SWING_DTE_BAND`, `CSP_DTE_BAND`, `LEAP_DTE_BAND`, `IV_HV_ELEVATED_THRESHOLD`, `IV_RANK_EXTREME_FLOOR` | DTE band values govern expiration selection scope; IV threshold values govern spread-mandate resolution |

**What PASS2 delivers to each downstream file.**

| Destination file | What PASS2 delivers | How that file uses it |
|---|---|---|
| `PORTFOLIO_MGMT_v3.0.md` (T2) | Validated trade specifications: exact strike, exact expiration, structure, direction, entry price range, sizing band, chain quality label, dealer-status label, entry-time regime snapshot | PORTFOLIO_MGMT carries the validated specification and regime snapshot in position context for monitoring and exit-trigger evaluation |
| `REPORT_FORMAT_v3.0.md` (T3) | Full Pass 2 output: Validated / Flagged / Rejected per candidate with named reasons; chain quality label; dealer-status label; spread-mandate resolution outcome; entry price range; sizing band | REPORT_FORMAT renders the Pass 2 section of the screening report; PASS2 does not own report rendering |
| `REPORT_STYLE_v3.0.md` (T3) | (Indirectly) the Pass 2 output surface | REPORT_STYLE governs field length caps and label vocabulary; PASS2 respects these constraints in the rationale text it assembles |

**What PASS2 does not own.**

| Concern | Owner |
|---|---|
| Trigger contracts and firing conditions | `SIGNAL_v3.0.md` |
| Phase and event vocabulary | `WYCKOFF_v3.0.md` |
| Dealer regime tier vocabulary | `DEALER_v3.0.md` |
| IV/HV band vocabulary and source-authority rules | `VOLATILITY_v3.0.md` |
| Sizing band ladder | `RISK_v3.0.md` |
| Override discipline | `KAPMAN_GUARDRAILS_v3.0.md` |
| Eligible-set determination | `PASS1_SCREENING_v3.0.md` |
| Report rendering | `REPORT_FORMAT_v3.0.md` |
| Position monitoring and portfolio management | `PORTFOLIO_MGMT_v3.0.md` |
| Operator-configurable parameter values | `SYSTEM_PARAMS_v3.0.md` |
| MCP endpoint names, parameter shapes, chain-quality numeric thresholds, chain truncation detection heuristics | `engineering_only/PASS2_MCP_REFERENCE_v3.0.md` (forthcoming) |

**Cross-references this file expects to be honored.**

- `SIGNAL_v3.0.md` owns the spread-mandate contract that PASS2 enforces. When SIGNAL and PASS2 appear to specify different spread-mandate outcomes, SIGNAL governs.
- `VOLATILITY_v3.0.md` owns the IV source-authority rules. PASS2's use of Schwab ATM chain IV as the Pass 2 source is an application of VOLATILITY's source-authority discipline, not an independent PASS2 decision.
- `KAPMAN_GUARDRAILS_v3.0.md` owns the anti-hallucination floor and override discipline. Neither may be relaxed by PASS2 heuristics, even implicitly.
- `RISK_v3.0.md` owns the sizing band ladder. PASS2 applies chain-quality sizing step-downs per RISK's ladder; it does not define its own step-down magnitudes.
- `engineering_only/PASS2_MCP_REFERENCE_v3.0.md` (forthcoming) owns the specific MCP tool-surface contracts for Pass 2 data fetching — endpoint names, chain-quality numeric thresholds, truncation detection heuristics, and strike-count reduction parameters. PASS2 is silent on all of these; operators and engineers consult the engineering-only reference for tool-surface details.
- `JOURNAL_MGMT_v4.0.md` owns where and how the entry-time snapshot Pass 2 captures at validation is written to `positions.md` (path, schema, write-once overwrite). PASS2 owns only the trigger (validation of a new entry) and the captured field set; it does not define the journal's write model.

## Legacy anchors (for legend citations and back-compat)

**PIPELINE_012** → § Operational heuristics, "When a chain fetch appears truncated, reduce and re-fetch before classifying — never treat a truncated chain as complete." The v2.3 anchor identified MCP result-size truncation as a failure mode specific to large option chains: when the Schwab chain fetch returns fewer contracts than expected for the requested zone and DTE band, the workaround is to reduce the `strike_count` parameter and re-fetch, or to split the fetch by targeted expiration rather than fetching the full zone in one call. The runtime behavioral contract — never classify a chain as Full when truncation has not been ruled out — is owned by this file's Operational heuristics. The numeric `strike_count` reduction parameters, the targeted-expiry split mechanics, and the truncation detection heuristics belong in `engineering_only/PASS2_MCP_REFERENCE_v3.0.md` (forthcoming). Body-text references in legacy report legends (e.g., "Rules applied: PIPELINE_012") remain valid; the legend entry resolves to this file's truncation heuristic for the runtime behavioral contract and to the engineering-only reference for the mechanical workaround.

**VALIDATION_001 (PASS2 residue)** → § Principle, "The anti-hallucination floor does not lift at Pass 2; it narrows." The v2.3 anchor was a system-prompt instruction at the model-control layer forbidding model-generated strike and expiration assumptions. The primary v3.0 destination is `KAPMAN_GUARDRAILS_v3.0.md` (owned there as the standing anti-hallucination floor). The PASS2-specific residue is the narrowing rule: the floor lifts only to the extent that the Schwab chain has been validated and is not truncated. A validated Full chain permits exact strike and expiration output; a truncated or Weak chain reverts output to candidate zones with a named data-quality label. The persistence-layer enforcement (VALIDATION_007: hardcoded null assignment for option_strike and option_expiration in C4 recommendation rows) is a tool-surface-internal control with no LLM runtime effect and belongs in `engineering_only/PASS2_MCP_REFERENCE_v3.0.md`.

**PIPELINE_011 (mis-filing note)** → This anchor does not belong in PASS2. The PASS2 scaffold contained a PIPELINE_011 placeholder; that placeholder was a mis-filing. PIPELINE_011 (context compaction guard — numeric regime reads do not carry forward as authoritative from Pass 1 into Pass 2) was resolved in session 7 into `PASS1_SCREENING_v3.0.md`'s Operational heuristics and Legacy anchors. PASS2 enforces the re-fetch requirement that PIPELINE_011 motivates, but it does not own the anchor. See `PASS1_SCREENING_v3.0.md` for the authoritative PIPELINE_011 destination.

## Appendix — formulas and reference tables

**Pass 2 output state definitions.**

| State | Specifiable from chain? | Named caveat present? | Operator action required before execution? | Minimum content |
|---|---|---|---|---|
| Validated | Yes — Full or Limited chain supports complete specification | No unresolved caveats | None — trade-ready as delivered | Exact strike, exact expiration, confirmed structure, entry price range, sizing band, chain quality label, dealer-status label |
| Flagged | Fully or partially — chain supports specification with known limitations | Yes — one or more named flags | Operator must acknowledge flag(s) before treating as executable | All Validated fields where available, plus named flag reason(s) |
| Rejected | No — chain cannot support a valid specification | Yes — named rejection reason | Candidate returns to Pass 1 state; no execution path without re-screening | Named rejection reason only; no strike or expiration produced |

**Chain quality × dealer-status combination matrix.**

| Chain quality | Dealer-status | Output state floor | Sizing consequence |
|---|---|---|---|
| Full | FULL | Validated eligible | Full sizing band per RISK |
| Full | LIMITED | Validated eligible | Floor-of-band sizing per RISK |
| Full | INVALID | Flagged | Floor-of-band sizing; dealer-data-absent label |
| Limited | FULL | Validated eligible with caveat noted | One-tier step-down per RISK |
| Limited | LIMITED | Flagged | One-tier step-down; both dimensions noted |
| Limited | INVALID | Flagged | One-tier step-down; dealer-data-absent label |
| Weak | FULL | Flagged | Two-tier step-down or Flagged with sizing caveat |
| Weak | LIMITED | Flagged | Two-tier step-down; both dimensions noted |
| Weak | INVALID | Rejected | No valid specification producible |

**Spread-mandate resolution quick reference.**

| Outcome | Pass 2 IV/HV condition | Pass 2 IV rank condition | Consequence |
|---|---|---|---|
| Confirmed | ≥ `IV_HV_ELEVATED_THRESHOLD` per SYSTEM_PARAMS | Any | Spread required; naked long-premium refused; sizing denominator = spread-risk |
| Confirmed (rank reinforcement) | Neutral band | ≥ `IV_RANK_EXTREME_FLOOR` per SYSTEM_PARAMS | Spread required despite neutral IV/HV; *Stretched IV* annotation |
| Overridden | Below elevated threshold | Below extreme floor | Spread mandate lifts; naked long-premium eligible; sizing denominator = underlying-notional |
| Fire-by-default | Schwab ATM IV unavailable or chain too degraded to compute reliable IV/HV | N/A | Spread required; *Spread mandated — chain validation failed* label |

**DTE band reference — per SYSTEM_PARAMS.**

| Trade type | Parameter | Current value | Expiration selection preference |
|---|---|---|---|
| Swing trade (directional) | `SWING_DTE_BAND` | 60–120 days | Favor longer end of band when two expirations are available; more time buffer reduces theta drag on directional conviction |
| Cash-secured put | `CSP_DTE_BAND` | 45–60 days | Target the range where theta decay accelerates most efficiently for premium-selling structures |
| LEAP | `LEAP_DTE_BAND` | 12–24 months | Select the nearest available LEAPS expiration within the band; LEAPS calendars are sparse and exact-midpoint targeting is not meaningful |

**Regime drift materiality reference.**

| Drift type | Material — pause and surface to operator? |
|---|---|
| SPY crossed below gamma flip since Pass 1 | Yes — always material |
| Per-ticker DGPI tier moved two or more tiers | Yes |
| Near-flip flag newly active on a candidate ticker | Yes |
| Dealer-status label changed from FULL or LIMITED to INVALID | Yes — surfaces as data-quality flag on the affected candidate |
| Per-ticker DGPI tier moved one tier | No — note in rationale; do not pause |
| Wall levels shifted within the candidate zone | No — note in rationale; do not pause |
| Dealer-status label changed from FULL to LIMITED | No — note in rationale; sizing consequence applied |
