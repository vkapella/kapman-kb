---
system: KapMan
doc_type: runbook
kb_version: 3.0.1
file_last_updated: 2026-05-28
status: active
tier: T2
---

# PORTFOLIO MGMT

## Principle

Portfolio management is the position lifecycle layer: it takes operator-supplied position data — broker screenshots, CSV exports, or manually entered records — and evaluates whether each open position's original thesis still holds. The judgment portfolio management exercises is not re-screening — it does not re-evaluate whether a position should have been entered, and it does not re-validate strikes or chains. Its judgment is about the current state of a live position: whether the regime that authorized the entry has decayed materially enough to surface an advisory, whether the underlying has reached an alert level that warrants action, and whether the time remaining in the position warrants a roll or close decision before expiration pressure removes the choice.

Position context is the bundle of fields that makes this judgment possible — strikes, expiration, entry date, entry price, actual size, the exit-trigger fields that SIGNAL computed at entry, and the entry-time regime snapshot that records the confirmed Wyckoff phase, DGPI tier, flip-zone relationship, dealer-status label, IV/HV band, and volatility-status label that were current when the trade was validated. Claude has no memory between sessions; the operator supplies position context at the start of every Portfolio mode session from whatever records they maintain. PORTFOLIO_MGMT defines the schema that context must conform to and degrades gracefully when fields are missing — but without the entry-time regime snapshot, the Regime exit advisory cannot evaluate decay, and without the exit-trigger fields, Stop and Profit target alert levels have no anchor. Position context is the precondition for everything else portfolio management produces.

## Operational heuristics

**Position context is the entry contract for every Portfolio mode session — PORTFOLIO_MGMT does not proceed without it.**

The operator supplies position data at session start: broker screenshots, CSV exports, or manually entered records. PORTFOLIO_MGMT reads whatever is supplied and maps it to the position context schema. When fields are missing from the supplied data, PORTFOLIO_MGMT names the gap explicitly and degrades the dependent evaluation — it does not infer missing values, does not reach for stale prior values from conversation context, and does not proceed as if the field were present. The minimum viable context for a useful portfolio session is: ticker, structure, strikes, expiration, entry date, and entry price. Everything beyond that minimum enables progressively richer evaluation; the Regime exit advisory requires the full entry-time regime snapshot, and the exit-trigger evaluation requires the four SIGNAL-computed alert fields.

**Portfolio mode and Hybrid mode have distinct entry points and distinct output shapes.**

In Portfolio mode, the operator is asking about existing positions only. PORTFOLIO_MGMT drives the session: it fetches current regime data for each open position, evaluates exit triggers, evaluates the Regime exit advisory, and assembles the portfolio view. No screening workflow runs. In Hybrid mode, a PASS1/PASS2 screening run is also underway in the same session. PORTFOLIO_MGMT produces the portfolio view as a complement to the screening output, in a clearly titled second section per GUARDRAILS' Hybrid output discipline (Screening first, Portfolio second). In Hybrid mode, regime data fetched during screening — dealer metrics, volatility metrics, Wyckoff phase confirmations — satisfies the portfolio monitoring fetch requirement for the same tickers; separate re-fetches for those tickers are not required. For tickers that appear only in the portfolio and not in the screening run, PORTFOLIO_MGMT fetches regime data independently.

**The Portfolio mode workflow runs in a fixed sequence for every session.**

- Step 1: Load position context from operator-supplied data. Map to schema. Name any missing fields.
- Step 2: Fetch current regime data — dealer metrics and volatility metrics for each open position's ticker. In Hybrid mode, consume screening-session regime data for overlapping tickers rather than re-fetching.
- Step 3: Fetch current spot price and option chain snapshot for each open position, for exit-trigger context and DTE calculation.
- Step 4: Evaluate the Regime exit advisory per position — compare the entry-time regime snapshot to the current regime across all four decay branches. Surface named decay reasons for any branch that fires.
- Step 5: Evaluate DTE decay warnings — flag any open position whose remaining DTE has fallen below `DTE_DECAY_WARNING_THRESHOLD` per SYSTEM_PARAMS.
- Step 6: Evaluate exit-trigger proximity. When entry-time Stop and Profit target alert levels are present in position context, compare current spot and current option price to those levels and surface proximity language when either level is imminently relevant. When entry-time alert levels are absent from position context, do not suppress this step — instead apply the SIGNAL approximation formula fresh from current-session data: use current-session Greeks (from broker screenshot or live chain pull), Schwab dealer flip as Stop anchor, nearest call wall above spot as Profit target anchor, and the SIGNAL trail-stop reference band (20–30% mark for long calls and long puts; 15–25% mark for LEAPs; 25–35% bid/ask for long calls and long puts; 20–30% bid/ask for LEAPs). Surface all four mandatory fields per position with an inline note: "Current-session computed — entry-time levels not supplied."
- Step 7: Assemble and surface the portfolio view. Execute the sub-sequence below in order — do not skip steps.

  - Step 7a: State the mandatory per-position field list from REPORT_FORMAT before generating any output. For every open position, confirm a data source or named fallback exists for each field. This manifest is stated inline before the first position block is written.
  - Step 7b: For each open position, confirm each of the following has a data source or a named fallback reason: (1) current regime summary — DGPI tier, flip-zone, Wyckoff if confirmed this session; (2) Stop alert — anchor identified (Schwab dealer flip), estimated option price computable via delta-gamma approximation, trail mark and trail bid/ask values computable from SIGNAL reference band; (3) Profit target alert — same four fields as Stop alert; (4) DTE decay warning — checked against DTE_DECAY_WARNING_THRESHOLD per SYSTEM_PARAMS; (5) Regime exit advisory — all four branches evaluated or labeled data-absent with named reason. Any field without a data source and without a named fallback reason is a Rule 5 self-report violation and must be surfaced before output is generated.
  - Step 7c: Generate the portfolio view table and per-position detail blocks.
  - Step 7d: After all positions are generated, state the output self-audit result: number of positions processed, number of fields computed fresh from current-session data, number of named fallbacks applied.
  - Step 7e: Surface Exited positions summary and Expired positions requiring acknowledgment where applicable.

**Position lifecycle has four states: Open, Advisory, Exited, Expired.**

Open is the default state for a position that has been entered and has not been closed or expired. Advisory is a sub-state of Open — the position is still live but the Regime exit advisory has fired on one or more decay branches; the operator has not yet acted. Advisory does not force a close; it flags. Exited is when the operator has closed the position — by Stop alert trigger, Profit target alert trigger, or operator discretion. Expired is when the option's expiration date has passed without a recorded exit. Expired is a failure state: PORTFOLIO_MGMT surfaces it explicitly and requires operator acknowledgment; it is never silently discarded or treated as equivalent to Exited. A position moves from Advisory back to Open when the operator reviews and the current-session regime re-evaluation no longer fires any decay branch — the advisory clears when the regime recovers, not when the operator says so.

**The Regime exit advisory is evaluated branch by branch — each branch is independent, each fired branch is named.**

*Wyckoff phase succession branch:* Compare the entry-time confirmed phase to the current session's confirmed phase. A phase change that moves in the unfavorable direction per WYCKOFF's succession table fires this branch — Markup to Distribution, Accumulation post-Spring to Distribution, or any succession that closes the long-premium eligible set for the position's structure. If the current session has no confirmed Wyckoff reading for the ticker, this branch is suppressed and the advisory notes "Wyckoff phase not confirmed this session — branch not evaluated." The branch does not fire conservatively on an absent reading; it is skipped and labeled.

*DGPI tier degradation branch:* Compare the entry-time DGPI tier to the current DGPI tier for the position's ticker. Two or more tiers of degradation in the unfavorable direction fires this branch — Strongly supportive to Near-neutral, Moderately supportive to Weakening, Near-neutral to Hostile. One-tier drift is normal regime noise and does not fire. If the current dealer-status is INVALID, this branch is labeled data-absent and skipped; it does not fire conservatively on absent data, because INVALID dealer data on a monitoring session does not constitute evidence of degradation.

*Spot-vs-flip crossing branch:* Compare the entry-time spot-vs-flip relationship to the current spot-vs-flip relationship for the position's ticker. This branch fires when the relationship has inverted: position entered with spot well above flip and current spot is now well below flip, or position entered with spot well below flip (e.g., a long put) and current spot is now well above flip. Near-flip at either time point is noted in the rationale but does not by itself fire the branch — crossing requires a full zone inversion, not proximity to the boundary.

*IV/HV band crossing branch:* Compare the entry-time IV/HV band to the current IV/HV band for the position's ticker, evaluated against the position's structure. This branch fires when the band has crossed in a direction that is adverse to the position structure: a position entered as naked long-premium when IV/HV was cheap, where current IV/HV now reads elevated and the spread-mandate would fire on a new entry of the same structure. It also fires in the reverse direction — a position entered as a spread when IV/HV was elevated, where current IV/HV now reads cheap — not to force restructuring but to surface that the original spread constraint is no longer operative. The reverse direction is advisory only; the operator may choose to hold the spread regardless.

**DTE decay warning surfaces when remaining DTE falls below the threshold — it is a monitoring output, not a veto.**

When an open position's remaining DTE falls below `DTE_DECAY_WARNING_THRESHOLD` per SYSTEM_PARAMS, PORTFOLIO_MGMT surfaces a named warning in the portfolio view: the position is approaching expiration and the operator may want to roll or close rather than hold to expiration. The warning does not block the position from remaining Open. It does not change the position's lifecycle state. It is informational, in the same spirit as the Regime exit advisory — it names a condition and surfaces it; the operator decides what to do. Positions in the DTE decay warning zone that also carry an active Regime exit advisory surface both flags together.

**Exit-trigger proximity is re-evaluated at every session using current spot and current option price.**

Stop alert and Profit target alert levels were computed by SIGNAL at entry and are carried in position context; PORTFOLIO_MGMT does not recompute them. At each session, PORTFOLIO_MGMT compares current spot to the underlying alert price and current option price to the estimated option price at alert for each position. When either comparison shows the position is within a meaningful distance of an alert level, the portfolio view surfaces proximity language — not a new alert level, but a flag that the operator-set broker alert may be imminently relevant. The distance threshold for proximity language is a judgment band; it does not require a named parameter in SYSTEM_PARAMS. When the Greeks needed for the delta-gamma approximation update are available from the current chain snapshot, PORTFOLIO_MGMT may refresh the estimated option price at alert using the same formula SIGNAL owns; when Greeks are unavailable, the carried entry-time estimate remains and the portfolio view notes it may be stale.

**Position entry recording — what the operator must supply, what PORTFOLIO_MGMT carries forward.**

When a Pass 2 Validated or Flagged candidate becomes an actual position, the operator records the execution. PORTFOLIO_MGMT requires the operator to supply: actual fill price, actual size entered, and execution date if different from the recommendation date. PORTFOLIO_MGMT carries forward from the Pass 2 output without re-entry: structure, direction, ticker, strikes, expiration, entry price range (as the Pass 2 reference), sizing band note, chain quality label, dealer-status label, and the full entry-time regime snapshot. When the operator's actual size differs from the Pass 2 sizing band, PORTFOLIO_MGMT records both — the Pass 2 sizing band note and the actual size entered — and notes the deviation. It does not re-size, does not re-validate, and does not refuse to record a position whose actual size differs from the Pass 2 band; that is an operator decision.

**Exited positions are summarized; Expired positions require explicit acknowledgment.**

When the operator reports that a position has been closed, PORTFOLIO_MGMT records it as Exited. If the operator supplies the actual exit price, PORTFOLIO_MGMT computes and surfaces realized P&L (exit price minus entry price, in dollar and percentage terms relative to the position size). If the operator does not supply an exit price, the position is recorded as Exited with P&L labeled unknown — it is not estimated, not inferred from the last known option price, and not omitted from the summary. Exited positions remain visible in the portfolio view as a summary row until the operator removes them. Expired positions — positions whose expiration date has passed without a recorded exit — are surfaced as a named failure state requiring operator acknowledgment. The operator must explicitly acknowledge an Expired position before it is removed from the active portfolio view. PORTFOLIO_MGMT does not silently transition a position from Open to Expired; it surfaces the expiration and waits.

**Sizing band confirmation at entry is recorded, not re-evaluated.**

When a validated trade specification arrives from Pass 2 and the operator confirms execution, PORTFOLIO_MGMT records the sizing band as delivered by Pass 2. It does not re-run the sizing band ladder at the moment of entry recording, does not re-evaluate chain quality, and does not re-fetch dealer or volatility metrics for sizing purposes. The sizing decision was made at Pass 2; PORTFOLIO_MGMT records the outcome.

## Workflow integration

**What PORTFOLIO_MGMT receives from each upstream file.**

| Source file | What PORTFOLIO_MGMT consumes | How PORTFOLIO_MGMT uses it |
|---|---|---|
| `PASS2_VALIDATION_v3.0.md` (T2) | Validated trade specifications: structure, direction, ticker, strikes, expiration, entry price range, sizing band, chain quality label, dealer-status label, entry-time regime snapshot | Carried forward as the reference record when the operator confirms execution and supplies actual fill details; forms the foundation of the position context schema |
| `SIGNAL_v3.0.md` (T1) | Stop alert and Profit target alert four-field output; Regime exit advisory firing condition and four decay branches; delta-gamma approximation formula | PORTFOLIO_MGMT carries the four exit-trigger fields in position context; evaluates the Regime exit advisory branch by branch per Operational heuristics; may refresh the estimated option price at alert using the delta-gamma formula when current Greeks are available |
| `DEALER_v3.0.md` (T1) | Fresh dealer metrics per session: DGPI tier, flip-zone classification, dealer-status label, call/put wall levels | Fetched fresh at each Portfolio mode session for each open position's ticker; DGPI tier and flip-zone used for Regime exit advisory DGPI and spot-vs-flip branches; dealer-status label used to determine whether the DGPI branch can evaluate or must be labeled data-absent |
| `VOLATILITY_v3.0.md` (T1) | Fresh volatility metrics per session: IV/HV band, IV rank tier, volatility-status label | Fetched fresh at each Portfolio mode session; IV/HV band used for the Regime exit advisory volatility branch; volatility-status label used to determine branch evaluability |
| `WYCKOFF_v3.0.md` (T1) | Current session's confirmed Wyckoff phase per ticker, via propose-confirm protocol | Consumed for the Regime exit advisory Wyckoff phase succession branch; if no confirmed reading exists for a ticker in the current session, the Wyckoff branch is suppressed and labeled rather than fired conservatively |
| `KAPMAN_GUARDRAILS_v3.0.md` (T0) | Mode discipline (Portfolio / Hybrid); data-quality vocabulary; override discipline; Hybrid output section ordering | PORTFOLIO_MGMT confirms mode at session start per GUARDRAILS; applies data-quality labels to all degraded or missing fields; honors the Hybrid output discipline (Screening first, Portfolio second) |
| `SYSTEM_PARAMS_v3.0.md` (T3) | `DTE_DECAY_WARNING_THRESHOLD` | Applied at Step 5 of the Portfolio mode workflow to surface DTE decay warnings for positions approaching expiration |

**What PORTFOLIO_MGMT delivers to each downstream file.**

| Destination file | What PORTFOLIO_MGMT delivers | How that file uses it |
|---|---|---|
| `REPORT_FORMAT_v3.0.md` (T3) | Full portfolio view: Open positions with current regime status, Advisory positions with named decay reasons, exit-trigger proximity flags, DTE decay warnings, Exited positions summary, Expired positions requiring acknowledgment | REPORT_FORMAT renders the Portfolio section of the output; PORTFOLIO_MGMT does not own report rendering |
| `REPORT_STYLE_v3.0.md` (T3) | (Indirectly) the portfolio view output surface | REPORT_STYLE governs field length caps and label vocabulary; PORTFOLIO_MGMT respects these constraints in the rationale text it assembles |

**What PORTFOLIO_MGMT does not own.**

| Concern | Owner |
|---|---|
| Stop alert and Profit target alert computation | `SIGNAL_v3.0.md` — PORTFOLIO_MGMT carries the four-field output; it does not recompute alert levels |
| Regime exit advisory firing condition | `SIGNAL_v3.0.md` — PORTFOLIO_MGMT operationalizes the evaluation procedure; SIGNAL owns the contract |
| Delta-gamma approximation formula | `SIGNAL_v3.0.md` — PORTFOLIO_MGMT may reference the formula when refreshing the option-price-at-alert estimate from a current chain snapshot |
| Sizing band ladder | `RISK_v3.0.md` — PORTFOLIO_MGMT records the Pass 2 sizing band note; it does not define or re-run the ladder |
| Override discipline | `KAPMAN_GUARDRAILS_v3.0.md` |
| Wyckoff propose-confirm protocol | `WYCKOFF_v3.0.md` — PORTFOLIO_MGMT consumes the confirmed phase output; it does not run propose-confirm itself |
| Report rendering | `REPORT_FORMAT_v3.0.md`, `REPORT_STYLE_v3.0.md` |
| MCP endpoint names, parameter shapes, position-persistence implementation details | `engineering_only/PORTFOLIO_MGMT_MCP_REFERENCE_v3.0.md` (forthcoming) |

**Cross-references this file expects to be honored.**

- `SIGNAL_v3.0.md` owns the Regime exit advisory firing condition and the four decay branch definitions. When SIGNAL and PORTFOLIO_MGMT appear to specify different branch behavior, SIGNAL governs.
- `DEALER_v3.0.md` owns the DGPI tier vocabulary and the flip-zone vocabulary. PORTFOLIO_MGMT consumes these labels as delivered; it does not re-interpret raw DGPI scores.
- `WYCKOFF_v3.0.md` owns the phase succession table. PORTFOLIO_MGMT reads phase succession against that table when evaluating the Wyckoff branch of the Regime exit advisory; it does not define its own succession logic.
- `KAPMAN_GUARDRAILS_v3.0.md` owns mode discipline and the Hybrid output section ordering. PORTFOLIO_MGMT's Hybrid mode behavior is constrained by GUARDRAILS' Hybrid output discipline; PORTFOLIO_MGMT does not define its own Hybrid section ordering.
- `SYSTEM_PARAMS_v3.0.md` is the single update point for `DTE_DECAY_WARNING_THRESHOLD`. PORTFOLIO_MGMT references the parameter by name; it does not hardcode the value.

## Legacy anchors (for legend citations and back-compat)

PORTFOLIO_MGMT is a net-new v3.0 construct with no v2.3 antecedent. No v2.3 source file contains rules governing position tracking, exit discipline, portfolio-mode workflow sequencing, or position lifecycle state management. The v2.3 source set reviewed for this session — `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v2.3.md` and `DEALER_POSITIONING_RULES_v2.3.md` — contains no PORTFOLIO_MGMT-scoped content. The PIPELINE_ORCHESTRATION_v2.3.md rules absorbed in prior sessions likewise contained no portfolio-management-specific anchors; PIPELINE_011 (context compaction guard) resolved into PASS1_SCREENING_v3.0.md and PASS2_VALIDATION_v3.0.md, not here.

No legacy rule IDs map to this file. Body-text references in legacy report legends that cite portfolio or position management behavior have no v2.3 rule ID to resolve against; they resolve to this file's Operational heuristics by domain, not by anchor ID.

## Appendix — formulas and reference tables

**Position context schema — full field inventory.**

| Field | Required? | Source | Notes |
|---|---|---|---|
| Ticker | Required | Operator-supplied | |
| Structure | Required | Pass 2 / operator-supplied | Long call, long put, call debit spread, put debit spread, CSP, LEAP |
| Direction | Required | Pass 2 / operator-supplied | BULLISH / BEARISH |
| Strike(s) | Required | Pass 2 / operator-supplied | Both legs for spreads |
| Expiration | Required | Pass 2 / operator-supplied | Calendar date |
| Entry date | Required | Operator-supplied | Execution date |
| Entry price (actual fill) | Required | Operator-supplied | Single-leg midpoint or net debit/credit for spreads |
| Entry price range (Pass 2 reference) | Recommended | Pass 2 output | Carried as reference; not required for minimum viable session |
| Actual size entered | Required | Operator-supplied | Dollar amount or contract count |
| Pass 2 sizing band note | Recommended | Pass 2 output | Deviation from band noted when actual size differs |
| Chain quality label at entry | Recommended | Pass 2 output | Full / Limited / Weak |
| Dealer-status label at entry | Recommended | Pass 2 output | FULL / LIMITED / INVALID |
| Entry-time Wyckoff phase | Advisory-required (Wyckoff branch) | Pass 2 / operator-supplied | Confirmed phase at entry session |
| Entry-time DGPI tier | Advisory-required (DGPI branch) | Pass 2 / operator-supplied | Strongly supportive / Moderately supportive / Near-neutral / Weakening / Hostile |
| Entry-time flip-zone relationship | Advisory-required (spot-vs-flip branch) | Pass 2 / operator-supplied | Well above flip / Near-flip / Well below flip |
| Entry-time IV/HV band | Advisory-required (IV/HV branch) | Pass 2 / operator-supplied | Cheap / Neutral / Elevated |
| Entry-time volatility-status label | Advisory-required (IV/HV branch) | Pass 2 / operator-supplied | FULL / LIMITED / INVALID |
| Entry-time IV rank tier | Recommended | Pass 2 / operator-supplied | Supports IV/HV branch context |
| Stop alert — underlying price | Exit-trigger-required | SIGNAL output at entry | Unfavorable-side alert level |
| Stop alert — estimated option price | Exit-trigger-required | SIGNAL output at entry | Delta-gamma approximation; may be refreshed from current chain |
| Stop alert — trail-stop bid/ask | Exit-trigger-required | SIGNAL output at entry | Fidelity-compatible |
| Stop alert — trail-stop mark | Exit-trigger-required | SIGNAL output at entry | Schwab-compatible |
| Profit target alert — underlying price | Exit-trigger-required | SIGNAL output at entry | Favorable-side alert level |
| Profit target alert — estimated option price | Exit-trigger-required | SIGNAL output at entry | Delta-gamma approximation; may be refreshed from current chain |
| Profit target alert — trail-stop bid/ask | Exit-trigger-required | SIGNAL output at entry | Fidelity-compatible |
| Profit target alert — trail-stop mark | Exit-trigger-required | SIGNAL output at entry | Schwab-compatible |
| Position state | Required | PORTFOLIO_MGMT | Open / Advisory / Exited / Expired |
| Advisory reason(s) | Present when state is Advisory | PORTFOLIO_MGMT | Named decay branch(es) that fired |
| Exit date | Present when state is Exited | Operator-supplied | |
| Exit price | Present when state is Exited | Operator-supplied | Labeled unknown if not supplied |
| Realized P&L | Present when state is Exited and exit price supplied | PORTFOLIO_MGMT | Exit price minus entry price, dollar and percentage |
| Expiration outcome | Present when state is Expired | PORTFOLIO_MGMT | Surfaced as failure state; requires operator acknowledgment |

**Position lifecycle state machine.**

| From state | Trigger | To state |
|---|---|---|
| Open | Regime exit advisory fires on one or more branches | Advisory |
| Advisory | Current-session regime re-evaluation fires no decay branches | Open |
| Advisory | Operator closes position (Stop alert, Profit target alert, or discretion) | Exited |
| Open | Operator closes position | Exited |
| Open | Expiration date passes without recorded exit | Expired |
| Advisory | Expiration date passes without recorded exit | Expired |
| Expired | Operator acknowledges | Removed from active portfolio view |
| Exited | Operator removes from summary | Removed from active portfolio view |

**Regime exit advisory branch evaluability reference.**

| Branch | Fires when | Suppressed when | Skipped (data-absent) when |
|---|---|---|---|
| Wyckoff phase succession | Entry-time phase has rolled to a less-supportive phase per WYCKOFF succession table | Current session has no confirmed Wyckoff reading for the ticker | — |
| DGPI tier degradation | Two or more tiers of degradation in unfavorable direction since entry | — | Current dealer-status is INVALID |
| Spot-vs-flip crossing | Spot-vs-flip relationship has fully inverted since entry | Near-flip at either time point (noted in rationale, does not fire) | — |
| IV/HV band crossing | Band has crossed in direction adverse to position structure | — | Current volatility-status is INVALID |

**Hybrid mode regime data reuse reference.**

| Ticker appears in | Regime data source for portfolio monitoring |
|---|---|
| Screening run only | Not relevant — no open position |
| Portfolio only | PORTFOLIO_MGMT fetches dealer metrics, volatility metrics independently |
| Both screening run and portfolio | Screening-session regime data satisfies portfolio monitoring fetch; no re-fetch required |

**DTE decay warning — behavior reference.**

| Condition | Output | Position state change? |
|---|---|---|
| Remaining DTE ≥ `DTE_DECAY_WARNING_THRESHOLD` | No warning | No |
| Remaining DTE < `DTE_DECAY_WARNING_THRESHOLD` | Named warning surfaced in portfolio view | No — state remains Open or Advisory |
| Remaining DTE < `DTE_DECAY_WARNING_THRESHOLD` AND Regime exit advisory active | Both flags surfaced together | No |
| Position expires without recorded exit | Surfaced as Expired state | Yes — Open or Advisory → Expired |
