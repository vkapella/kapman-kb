---
system: KapMan
doc_type: principle
kb_version: 3.0.1
file_last_updated: 2026-06-28
status: active
tier: T1
---

# RISK

## Principle

Position sizing is the mechanism by which conviction and regime translate into capital at risk. Every other guardrail in KapMan — data honesty, structure selection, macro gating — exists to make sure the *direction* of a trade is sound; sizing is what determines whether a sound trade can survive being wrong, and whether an unsound trade can do real damage when it fails. The governing judgment is that sizing is regime-conditional, never fixed: the same ticker with the same Wyckoff regime deserves different allocation depending on dealer regime, volatility regime, and chain quality, and the regime assessments themselves live in their own principle files (`WYCKOFF_v3.0.md`, `DEALER_v3.0.md`, `VOLATILITY_v3.0.md`). RISK does not re-derive those regimes; it consumes them and converts them into a sizing band. The sizing denominator is the combined value of all funded, real-capital accounts in the operator's household; paper accounts are excluded from the denominator even when they execute the same screening output, because the dollars at risk are notional. The one rule that survives every regime is that no single position is ever a portfolio-shaping event — the absolute ceiling exists so that being catastrophically wrong on a single name cannot end the portfolio's ability to keep operating. Below that ceiling, sizing moves in bands, not cliffs: a clean direction-aligned trend (a long in `markup`, a long put in `markdown`) — or a post-phase-C continuation branch (`reaccumulation`/`redistribution`) — with supportive dealer regime and a full liquid chain earns the top of the band; the same setup with thin chain liquidity, elevated IV, or weakening dealer support earns the bottom; pre-confirmation setups (a range regime without its confirmed phase-C — `spring`/`shakeout` on the bullish side, `utad` on the bearish side) earn only conditional sizing (and are refused outright by the SIGNAL Wyckoff veto unless the operator overrides); and hostile macro regimes refuse the structure outright per `KAPMAN_GUARDRAILS_v3.0.md`. The near-flip one-tier reduction from GUARDRAILS steps down from whichever band RISK has selected, never replaces it. CSP sizing is governed by margin capacity, not premium percentage — premium-as-percent-of-portfolio is the wrong denominator for a structure whose risk is defined by assigned share cost. The operator retains override authority over individual sizing decisions, but the override mechanics live in GUARDRAILS; RISK enforces only the bands and the absolute ceiling.

## Operational heuristics

**Sizing bands are anchored to regime quality, not ticker score.**
A ticker's screening score gets it into the eligible set; the regime determines how much capital it earns. A high-score ticker in a thin-chain, elevated-IV, weak-dealer environment sizes smaller than a moderate-score ticker in a clean direction-aligned trend (`markup` for a long, `markdown` for a long put) with full chain liquidity. A high score does not round the band up — the sizing band reflects the environment the trade has to survive, not the confidence in the entry.

**Wyckoff regime sets the band ceiling, relative to the position's direction.**
The band ceiling is set by the position's regime read **relative to the position's direction** (WYCKOFF's decision-layer table is long-framed; the bearish bands are its mirror). A direction-aligned **confirmed trend** — `markup` for a long, `markdown` for a long put — earns the **upper** band by default. A direction-aligned **continuation branch confirmed at phase C** — `reaccumulation` (post-`spring`/`shakeout`) for a long, `redistribution` (post-`utad`) for a long put — also earns the **upper** band (it is the highest-odds continuation context). A direction-aligned **base regime confirmed at phase C** — `accumulation` (post-`spring`/`shakeout`) for a long, `distribution` (post-`utad`) for a long put — earns the **conditional-top** band: the phase-C test has confirmed but the breakout/breakdown has not, so it sizes below a confirmed trend. A direction-aligned range regime **without its phase-C** earns only the **conditional floor**, and is in any case refused by the SIGNAL Wyckoff veto unless the operator overrides — the trade may be right, but the regime hasn't yet provided the confirmation that would justify a normal-sized entry. A regime that does **not** align with the position's direction (the refusal set for that direction), `ranging_undefined`, or an unconfirmed reading (`UNKNOWN`) closes the long-premium band entirely; the eligible structures shift to the directionally-aligned alternatives plus CSPs, hedges, and LEAPs per GUARDRAILS, and those structures have their own sizing logic (margin capacity for CSPs, time-decoupled allocation for LEAPs).

**Dealer regime narrows the band within the Wyckoff ceiling.**
Within an eligible (direction-aligned, phase-C-confirmed or trend) regime, a dealer regime **supportive of the position's direction** earns the top of the band; a near-neutral or direction-adverse dealer regime steps the band down. For a long this is DGPI deep in supportive (positive) territory; for a long put it is the mirror — a dealer regime adverse to the underlying (the exact bearish-mirror DGPI band is a `DEALER_v3.0.md` reconciliation item). The specific dealer thresholds live in `DEALER_v3.0.md`. Hostile macro is not a sizing question — it's a refusal, owned by GUARDRAILS.

**Chain quality is a sizing factor, not just a structure factor.**
A full liquid chain (open interest and volume comfortably above execution thresholds) supports normal sizing. A limited chain — typically 5–24 contracts of acceptable liquidity — drops sizing to the floor of the band regardless of other factors, and caps contract count to what the chain can actually absorb. A chain too thin to execute against drops the candidate from eligible-set entirely, which is a Pass 2 validation outcome, not a RISK decision.

**Volatility regime governs structure choice, which feeds back into sizing.**
Elevated IV (IV/HV materially above 1) makes long-premium structures expensive and mandates a spread rather than a naked long. The spread sizing is then governed by spread risk (debit paid), not by underlying notional. Low-IV environments where naked longs are appropriate use underlying-notional sizing within the band.

**Near-flip steps down one tier.**
When `DEALER_v3.0.md` flags near-flip conditions, the sizing band is selected normally, then stepped down one tier from that band. The reduction is mechanical; it is not a refusal and is not optional. If the selected band is already at the conditional floor (e.g., a direction-aligned regime pre-phase-C, or a limited chain), the step-down produces no-new-entry for that candidate rather than negative sizing.

**CSP sizing is margin-capacity-driven.**
A CSP's risk is the cost of taking assignment on the underlying, not the premium collected. Sizing therefore looks at how many shares the operator can absorb at the strike across the combined account base, not at premium as a percentage of portfolio value. The absolute ceiling (single-position cap) applies to the *assignment cost*, not the premium. A CSP whose assignment cost would exceed the single-position cap is too large regardless of how attractive the premium looks.

**LEAP sizing decouples from short-term regime.**
LEAPs with 12+ months to expiration are not meaningfully governed by current dealer or volatility regime — those regimes will turn over multiple times before the position closes. LEAP sizing is governed by conviction in the underlying thesis and by the absolute ceiling. A LEAP entered during hostile macro is still bounded by the single-position cap, but is not refused under the macro gate.

**Portfolio-level concentration limits apply across structures.**
The single-position ceiling is per-name across all structures combined. A long call, a CSP, and a hedge on the same ticker are one position for ceiling purposes. Sector concentration is a separate band: when multiple positions in the same sector approach a combined limit, new entries in that sector size to the floor of their individual band until the concentration eases. The specific sector concentration band is in the Appendix.

**Sizing denominator is real-capital-only.**
Percentage caps apply to the combined value of all funded, live-trading accounts. Paper accounts (Schwab paper in the current configuration) are excluded from the denominator even when they execute the same screening output, because the dollars at risk are notional. As real accounts are added, they join the denominator; as accounts transition from paper to funded, they join automatically. The operator declares the real-capital total at the start of a session (or carries it from a prior session); sizing math uses that declared value. If the operator has not declared a real-capital total for the current session, sizing output is deferred and the denominator is requested before the report proceeds. The declared value lives in the session context only — it is not persisted to memory or project knowledge.

**Short-DTE clustering is a portfolio risk, not a per-trade risk.**
When multiple open positions share short DTE (a cluster of expirations within a narrow window), the portfolio is exposed to a single-day liquidity event that can affect all of them simultaneously. New entries that would add to an existing short-DTE cluster size to the floor of their band; if the cluster is already heavy, new short-DTE entries are deferred.

**Cash floor is a hard floor, not a target.**
The operator maintains a cash reserve floor across the combined account base for opportunistic entries and for margin headroom under stress. New entries that would breach the floor are refused even if they otherwise pass every other check. The specific floor percentage is operator-set and lives in the Appendix as a reference, not a mandate.

**Downside protection is sized to portfolio delta, not to individual longs.**
Hedges (SPY puts, VIX calls, sector inverse exposure) are sized against aggregate long-delta exposure, not against any individual position. A portfolio with $X of net long delta calls for a hedge sized to offset a defined fraction of that delta under a defined drawdown scenario. The specific hedge ratio is in the Appendix.

## Workflow integration

**Position in the document hierarchy.** RISK is tier T1 — a principle file. It governs *how much* capital a structure earns once that structure has been deemed eligible by upstream regime principles and validated by the screening runbooks. RISK does not detect regime, does not validate chain data, and does not select structures; it consumes those outputs and converts them into a sizing band.

**Where each upstream input comes from.**

| Input | Owned by | How RISK consumes it |
|---|---|---|
| Wyckoff regime + phase (A–E) | `WYCKOFF_v3.0.md` | Sets the band ceiling relative to the position's direction (per WYCKOFF's decision layer, mirrored for a long put): direction-aligned trend (`markup`/`markdown`) or post-phase-C continuation (`reaccumulation`/`redistribution`) → upper band; post-phase-C base (`accumulation`/`distribution`) → conditional-top; pre-phase-C → conditional floor (override-only); non-aligned regime / `ranging_undefined` / `UNKNOWN` → long-premium band closed |
| Dealer regime (DGPI tier) | `DEALER_v3.0.md` | Narrows the band within the Wyckoff ceiling: dealer regime supportive of the position's direction → top of band, near-neutral/direction-adverse → step down (bullish keys on positive DGPI; bearish on the mirror — exact band per DEALER reconciliation) |
| Near-flip flag | `DEALER_v3.0.md` | Triggers the mechanical one-tier step-down per GUARDRAILS |
| Hostile macro flag | `DEALER_v3.0.md` (definition), `KAPMAN_GUARDRAILS_v3.0.md` (behavior) | Not a sizing input — a refusal. RISK does not size long-premium structures when hostile macro is active |
| Volatility regime (IV/HV, IV source tier) | `VOLATILITY_v3.0.md` | Governs structure choice (naked vs. spread), which determines the sizing denominator |
| Chain quality (full / limited / weak) | `PASS2_VALIDATION_v3.0.md` | Full → normal sizing within band, limited → floor of band, weak → drops from eligible-set entirely |
| Screening score | `PASS1_SCREENING_v3.0.md`, `SIGNAL_v3.0.md` | Gates eligibility only — does not adjust the band |
| Override status | `KAPMAN_GUARDRAILS_v3.0.md` | RISK applies the bands; an active override changes which structures are eligible, not which band applies |

**Where RISK outputs flow downstream.**

| Output | Consumed by | What the downstream file does with it |
|---|---|---|
| Sizing band (top / mid / floor / conditional / refused) | `REPORT_FORMAT_v3.0.md` | Renders the position size field in the recommendation row |
| Contract count cap (under limited chain) | `PASS2_VALIDATION_v3.0.md`, `REPORT_FORMAT_v3.0.md` | Constrains exact-contract output and rationale text |
| Single-position ceiling check | `PORTFOLIO_MGMT_v3.0.md` | Portfolio mode validates that combined exposure to a name across structures does not exceed the ceiling |
| Sector concentration band | `PORTFOLIO_MGMT_v3.0.md` | Portfolio mode flags new entries that would push sector exposure past the band |
| Real-capital denominator | `PORTFOLIO_MGMT_v3.0.md`, `REPORT_FORMAT_v3.0.md` | Both screening and portfolio reports use the declared real-capital denominator; paper account values are not in the denominator |
| Cash floor refusal | `PORTFOLIO_MGMT_v3.0.md` | Portfolio mode owns enforcement; RISK owns the principle |
| Hedge sizing ratio | `PORTFOLIO_MGMT_v3.0.md` | Portfolio mode computes the required hedge against aggregate long delta using RISK's ratio |

**Entry point for every sizing decision.** Before emitting a position size, four confirmations must already exist in the working context:

1. Eligible structure has been determined (long call, debit spread, CSP, LEAP, hedge, or refused) — this is upstream of RISK.
2. Wyckoff regime + phase (A–E), dealer regime, volatility regime, and chain quality are all assessed — RISK reads these as inputs.
3. No active hostile-macro refusal applies to the structure under consideration, *or* an explicit override per GUARDRAILS is in effect.
4. The real-capital denominator is established for this session — either declared by the operator or carried from a prior session. If undeclared, sizing does not proceed; the denominator is requested before output continues.

If any of these is missing or ambiguous, sizing does not proceed. A sizing band emitted on incomplete regime input or against an undeclared denominator is a guardrail violation, not a RISK violation — but the failure surfaces in the report as a no-size output.

**Cross-references this file expects to be honored.**

- `KAPMAN_GUARDRAILS_v3.0.md` — owns override mechanics, hostile-macro refusal behavior, near-flip step-down requirement (RISK owns the step-down's destination band), and the "no invented contract specifications" honesty floor that prevents sizing fields from being fabricated.
- `DEALER_v3.0.md` — owns the numeric definitions of DGPI tiers, hostile macro, and near-flip. RISK references these as named regimes, never as raw thresholds.
- `WYCKOFF_v3.0.md` — owns the canonical regime(7)/phase(A–E)/event vocabulary, the regime decision layer (the per-regime sizing-band ceiling RISK enforces, read direction-relative), and the phase-C confirmation criterion (`spring`/`shakeout` bullish / `utad` bearish) that distinguishes conditional-top from conditional-floor sizing.
- `VOLATILITY_v3.0.md` — owns IV/HV bands and IV source tiering. The "elevated IV mandates spread" rule is enforced upstream of RISK; RISK only consumes the resulting structure choice.
- `PASS2_VALIDATION_v3.0.md` — owns chain quality categorization (full / limited / weak) and the contract-count thresholds. RISK consumes the category, not the raw OI/volume numbers.
- `PORTFOLIO_MGMT_v3.0.md` — owns enforcement of the portfolio-level limits RISK defines (sector concentration, real-capital denominator application, short-DTE cluster, cash floor, hedge ratio). RISK defines the bands; portfolio mode applies them to the live book.
- `REPORT_FORMAT_v3.0.md` — owns the rendering of sizing output into the recommendation row, including the field length cap. Sizing rationale that exceeds the cap goes to a footnote.

**When RISK is silent.** A sizing question not addressed here is not a sizing question this principle governs. Specifically: tax-lot considerations, broker-specific margin rules, account-type restrictions (IRA cash-secured vs. margin), and execution mechanics (limit vs. market, working orders) are not RISK concerns. Those belong in operator-side execution practice and are not encoded in `llm_runtime/`.

## Legacy anchors (for legend citations and back-compat)

> **Historical note (v4.0 model change).** RISK_005 below describes the v2.3 sizing ladder in the superseded four-phase vocabulary (Wyckoff markup / accumulation / distribution / markdown) and the long-only frame. It is preserved **verbatim** for legend citations and back-compat — do not rewrite it. The canonical model is now the two-axis **regime(7) + phase(A–E)** vocabulary owned by `WYCKOFF_v3.0.md`, and the sizing bands are **direction-relative** (a long put in `markdown` earns the upper band, mirroring a long call in `markup`). The v2.3 named bands and their reference percentages are unchanged; only the regime→band mapping is re-keyed and mirrored (see the Appendix sizing band table). Where RISK_005 cites the heuristic *"Wyckoff phase sets the band ceiling,"* read it as its v4.0 rename *"Wyckoff regime sets the band ceiling, relative to the position's direction."*

**RISK_005** → § Principle and § Operational heuristics, "Wyckoff phase sets the band ceiling," "Dealer regime narrows the band within the Wyckoff ceiling," "Chain quality is a sizing factor, not just a structure factor," and "Volatility regime governs structure choice, which feeds back into sizing." The v2.3 sizing ladder — which expressed allocation as a stack of threshold cliffs keyed to Wyckoff phase, DGPI band, chain depth, and IV/HV ratio — is superseded in v3.0 by the band-based judgment model in those heuristics. The specific percentages from the v2.3 ladder (3%, 2%, 1%, 0.5–1%, 5% absolute ceiling) are preserved as reference points in the Appendix sizing band table, where they retain their original meaning under the original regime conditions. The v2.3 macro-gate override clause ("SPY below flip AND SPY DGPI ≤ -20 → no new long-call entries regardless of individual ticker regime") is *not* preserved in RISK; that behavior now lives in `KAPMAN_GUARDRAILS_v3.0.md` as the hostile-macro refusal. The v2.3 absolute ceiling ("No single position exceeds 5% of total portfolio") is preserved as the Principle's "no single position is ever a portfolio-shaping event" and as a numeric reference in the Appendix. The v2.3 cross-account denominator note ("Percentages apply to combined portfolio value across both Schwab and Fidelity accounts") is superseded by the real-capital-only denominator model: paper accounts are excluded from the sizing denominator regardless of whether they execute the same screening output. The v2.3 CSP anti-pattern ("NEVER apply RISK_005 percentage caps to CSP margin requirement calculations") is preserved and elevated from anti-pattern to operational heuristic ("CSP sizing is margin-capacity-driven") because v2.3 surfaced it as a recurring failure mode worth stating as principle rather than as exception. Body-text references in legacy report legends (e.g., "Rules applied: RISK_005") remain valid and will continue to be honored in report output.

## Appendix — formulas and reference tables

**Sizing band reference table.** The bands below preserve the v2.3 RISK_005 ladder as reference points under the original regime conditions. They are reference points, not threshold cliffs — the Operational heuristics describe how the bands narrow and step within these reference values.

| Regime composite | Sizing band | Reference allocation | Structure | v2.3 source clause |
|---|---|---|---|---|
| Direction-aligned trend (`markup` long / `markdown` long put) + dealer regime strongly supportive of direction + full chain + IV/HV not elevated | Top of band | ~3% of real-capital denominator | Direction-aligned long-premium (long call / long put) | v2.3 clause 1 |
| Direction-aligned trend + dealer regime moderately supportive of direction + full chain + IV/HV not elevated | Mid band | ~2% of real-capital denominator | Long call / long put | v2.3 clause 2 |
| Direction-aligned trend + dealer regime supportive of direction + full chain + IV/HV elevated (≥ 1.2) | Mid band, spread-mandated | ~2% of real-capital denominator | Vertical spread mandatory (call debit / put debit) | v2.3 clause 3 |
| Direction-aligned continuation branch post-phase-C (`reaccumulation` post-`spring`/`shakeout` / `redistribution` post-`utad`) + supportive dealer + full chain | Upper band (highest-odds continuation) | ~3% top / ~2% mid (dealer-narrowed) | Long call / long put | v4.0 (per WYCKOFF decision layer / SIGNAL committed prose) |
| Direction-aligned trend or continuation + limited chain (5–24 contracts) + any dealer | Floor of band | ~1% of real-capital denominator, max 2–3 contracts | Long call / long put / spread | v2.3 clause 4 |
| Direction-aligned base regime post-phase-C (`accumulation` post-`spring`/`shakeout` / `distribution` post-`utad`) | Conditional-top | ~1% of real-capital denominator (top of the conditional band) | Long call / long put, CONDITIONAL status | v4.0 (extends v2.3 clause 5; JD1) |
| Direction-aligned base/continuation pre-phase-C (no confirmed phase-C — `spring`/`shakeout` bullish; `utad` bearish) | Conditional floor — default refused by the SIGNAL Wyckoff veto; sized here only under operator override | ~0.5% of real-capital denominator | Long call / long put, CONDITIONAL status | v2.3 clause 5 |
| Regime not aligned with the position's direction (refusal set), or `ranging_undefined`, or `UNKNOWN` | Long-premium band closed | No new long-premium entries in that direction | Directionally-aligned alternatives + CSPs, hedges, LEAPs | v2.3 clause 6 (generalized) |
| Hostile macro (SPY below gamma flip AND SPY DGPI ≤ -20) | Refused (bullish long-premium) | No new bullish long-call entries; bearish long puts remain the aligned redirect | Override required per GUARDRAILS | v2.3 clause 7 |

**Absolute single-position ceiling.**

| Cap | Reference value | Scope |
|---|---|---|
| Single position, all structures combined | 5% of real-capital denominator | Per ticker, across long calls, spreads, CSPs (by assignment cost), LEAPs, and hedges on the same name |

The 5% ceiling is the only value in this Appendix that does not move with regime. The Principle's "no single position is ever a portfolio-shaping event" is operationalized as this number.

**Near-flip step-down mechanics.** When `DEALER_v3.0.md` flags near-flip conditions, the selected band steps down one tier in this order:

| Selected band | Steps down to |
|---|---|
| Top of band (~3%) | Mid band (~2%) |
| Mid band (~2%) | Floor of band (~1%) |
| Floor of band (~1%) | Conditional floor (~0.5%) |
| Conditional-top (~1%) | Conditional floor (~0.5%) |
| Conditional floor (~0.5%) | No new entry |
| Long-premium band closed | No change (already refused) |

**CSP sizing denominator.**

| Quantity | Formula | Notes |
|---|---|---|
| CSP single-position size | (Strike × 100 × contracts) ≤ 5% of real-capital denominator | Assignment cost is the risk denominator, not premium |
| CSP premium yield | (Premium × 100 × contracts) / (Strike × 100 × contracts) | Reported as % yield on capital-at-risk, not as % of portfolio |
| Margin-secured equivalent | Schwab margin requirement per contract × contracts | Used when CSP is held against margin rather than cash |

**LEAP sizing reference.**

| Quantity | Reference value | Notes |
|---|---|---|
| LEAP single-position ceiling | 5% of real-capital denominator (debit paid) | Same absolute ceiling as all other structures |
| LEAP eligibility under hostile macro | Eligible per GUARDRAILS | Time-decoupled from current regime |
| LEAP minimum DTE for "LEAP" classification | 365 days | Below 365 DTE, sizing follows long-call rules above |

**Portfolio-level reference bands.**

| Factor | Reference value | Notes |
|---|---|---|
| Sector concentration cap | ~15% of real-capital denominator per sector | Sectors per `SIC_SECTOR_MAP_v3.0.md`; when approached, new entries in sector size to floor of their individual band |
| Cash floor | ~10% of real-capital denominator | Operator-set; entries that would breach are refused regardless of other checks |
| Short-DTE cluster threshold | 3+ open positions within a 7-day expiration window | New entries adding to an established cluster size to floor; if cluster is heavy, deferred |
| Hedge ratio | ~25–35% of aggregate long-delta exposure | Hedged via SPY puts, VIX calls, or sector inverse; reference assumes a ~10% market drawdown scenario |

**Sizing denominator by household account composition.**

| Household account composition | Sizing denominator | Notes |
|---|---|---|
| Fidelity funded; Schwab paper | Fidelity value only | Schwab is data source (chain validation, market data) but not in sizing denominator |
| Fidelity funded; Schwab funded | Fidelity + Schwab | Both real-capital, combined denominator |
| Fidelity funded + additional real account(s) | Sum of all funded accounts | New real accounts join the denominator as they come online |
| Multiple real accounts, mixed account types (taxable / IRA / Roth) | Sum of all funded accounts | Account-type restrictions apply at execution, not at sizing |
| Operator has not declared real-capital total this session | Sizing not emitted | Denominator requested before sizing output proceeds |

A position taking 3% of the combined real-capital denominator with chain access only at Schwab is sized against the real-capital total and *executes from a real account*, not from paper. If no real account can execute the structure (e.g., chain depth available only at Schwab but Schwab is paper), the trade is flagged for execution-routing review rather than being sized against paper capital.

**Account-type restrictions are execution concerns, not sizing concerns.**

| Concern | Where enforced |
|---|---|
| IRA cash-secured-only (no naked puts) | Execution layer — structure routed to a non-IRA account if available, or rejected if no eligible account |
| Roth contribution and withdrawal rules | Operator-side; outside RISK scope |
| Taxable wash-sale tracking | Operator-side; outside RISK scope |
| Margin status differences between accounts | Execution layer — CSP-as-margin-secured routes only to margin-eligible accounts |
| Broker-specific assignment handling | Operator-side; outside RISK scope |

RISK sizes against the combined real-capital denominator. The execution layer (not encoded in `llm_runtime/`) determines which account the trade lands in based on structure eligibility per account type. This separation keeps RISK as a sizing principle and lets account-routing live where it belongs.

**Chain quality tier mapping (consumed from PASS2).**

| Chain quality tier | Definition (from PASS2) | Sizing consequence |
|---|---|---|
| Full | ≥ 25 contracts at acceptable liquidity in the target DTE/moneyness window | Normal sizing within selected band |
| Limited | 5–24 contracts at acceptable liquidity | Sizing drops to floor of band; contract count capped at what chain absorbs |
| Weak | < 5 contracts or open interest below execution thresholds | Candidate drops from eligible-set at PASS2; no RISK output |
| Invalid post-filter | All contracts dropped after min_oi filter | Candidate drops from eligible-set; no RISK output |

**Vocabulary alignment with GUARDRAILS data-quality labels.**

| Sizing output | Corresponds to GUARDRAILS label | When used |
|---|---|---|
| Reference band (e.g., "~2% / spread mandatory") | Resolved sizing under full chain | Pass 2 validated |
| Reference band with contract cap (e.g., "~1% / max 3 contracts") | Resolved sizing under limited chain | Pass 2 validated, limited chain |
| Candidate sizing zone (e.g., "~1–2% range") | *Candidate zone only* | Pass 1, pre-validation |
| No size emitted | *Invalid post-filter* / *Below flip* / *Poor structure* | Eligibility failed |
| No new entry | *Near event risk* / hostile macro / cluster-deferred | Eligible but timing or regime defers entry |
