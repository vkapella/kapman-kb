# Swing Tenor Scan — historical backtest: assessment and plan

**Drafted:** 2026-08-17 · **Relates to:** kapman-kb#95, `SWING_TENOR_SCAN_PILOT_v0.1.md` §7
**Status:** assessment for operator decision. No code written, no spec edited.

---

## 0. Why this exists

The forward pilot cannot answer §7 criteria 1 and 2. Four weekly observations
of a single bull tape, `S` pinned at +3 in every run, and zero disagreements
with the always-UP baseline in the governing post-08-03 series. A three-class
UP/DOWN/CHOP classifier that has never observed a DOWN or a genuine CHOP tape
cannot be validated on hit rate at any sample size.

A backtest answers a **different and prior** question: *do these variables
separate regimes at all?* It does not replace the pilot — data degradation,
producer bugs and operator judgment only surface in forward runs — but it is
the only way to get criteria 1 and 2 answered before the October gate.

---

## 1. Feasibility probes run 2026-08-17 (evidence, not assumption)

Per the spec's own kapman-mcp lesson — *never infer a producer gap from one
failed call; vary the parameter and retry* — three probes were run before
planning.

### Probe 1 — the Wyckoff engine has a real backtest entry point ✅

`get_wyckoff_scan` accepts **`as_of: YYYY-MM-DD`**, documented as *"Computes
the analysis as of that date using only data through that date (the backtest
entry point)"*, and the engine is described as **strictly causal**.

Verified live at `as_of=2023-08-17`: returned a complete analysis —
`regime: "markup"` (conf 0.73), 7 dated events, full decision block with bias,
conviction, invalidation and price targets, `bars_analyzed: 503`,
`data_through: "2023-08-17"`, and `options_status:
"skipped_historical_as_of"`. This removes what I previously assessed as the
project's single biggest blocker (reimplementing the Wyckoff engine, +3–5 days
and high transfer risk). **1.1 is backtestable natively.**

### Probe 2 — but Polygon history has a rolling ~5-year floor ⚠️

`as_of=2022-06-17` failed: *"Insufficient history: 211 bars available, 250
required."* Re-running the **same date with `days=3650` returned the identical
211 bars** — so the constraint is data availability, not the request window.

Triangulating: 2022-06-17 − 211 trading bars ≈ 2021-08-17, and 2023-08-17 −
503 bars ≈ 2021-08-17. Both point to the same floor, exactly five years before
today. **Inferred: a rolling 5-year history cap.** Two data points and a varied
parameter support it; confirm with the producer before relying on it.

Consequences:
- Earliest usable `as_of` = floor + 250 bars ≈ **2022-08**.
- **Usable Wyckoff range: 2022-08 → 2026-08. ~208 weekly runs, 4 years.**
- Contains: the 2022 H2 bear tail (SPX low Oct 2022) and the 2023 Aug–Oct
  correction (−10%). **Excludes 2020 COVID, 2018 Q4, 2015–16, 2011.**
- **Time-sensitive:** the window *rolls*. Every month of delay costs a month
  of the oldest and most valuable history. Re-running this in 2027 loses most
  of 2022 — the only genuine bear in range.

### Probe 3 — Schwab serves deep history ✅

`get_price_history_every_week(RSP, 2005-01-01 → 2006-01-01)` returned 52 clean
weekly candles. RSP's inception is 2003-04. Schwab — already the spec's source
of record for every weekly-bar variable — is therefore not a constraint for
1.2–1.5, 1.7, 2.1, 2.3, 2.4.

---

## 2. Variable-by-variable feasibility

| # | Variable | Source for backtest | History floor | Verdict |
|---|---|---|---|---|
| 1.1 | Weekly Wyckoff SPY/QQQ/IWM | polygon `get_wyckoff_scan(as_of=)` | **~2022-08** | ✅ native, but binds Tier 1 |
| 1.2 | 40-wk MA position + slope | Schwab weekly SPY | 1993 (SPY inception) | ✅ trivial |
| 1.3 | Distance from 52-wk high | Schwab weekly SPY | 1993 | ✅ trivial |
| 1.4 | Breadth RSP/SPY | Schwab weekly | **2003-04** (RSP) | ✅ |
| 1.5 | XLY/XLP | Schwab weekly | 1998-12 | ✅ |
| 1.6 | VIX vs VIX3M | **CBOE index history CSV** | **2009-09-18** ⚠️ *corrected Phase 1* | ✅ **now the Tier 2 binding constraint** |
| 1.7 | HV20/HV60 | computed from SPY daily closes | 1993 | ✅ trivial |
| 1.8 | 60–120 DTE dealer map | — | — | ❌ **drop: annotation only, not scored.** Historical chains+OI are expensive and the spec excludes 1.8 from the score |
| 2.1 | Credit HYG/LQD | Schwab weekly | **2007-04** (HYG) | ✅ |
| 2.2 | 10y impulse + 2s10s | **home.treasury.gov par yield CSV** (FMP retired) | 2007-01 verified, 4,891 rows | ✅ |
| 2.3 | Dollar UUP | Schwab weekly; DXY substitute pre-2007 | **2007-02** (UUP) | ✅ |
| 2.4 | Copper/gold | **HG/GC futures** per spec, not CPER/GLD | long | ✅ CPER inception 2011-11 makes futures mandatory |
| 2.5 | COT leveraged money | CFTC Socrata `gpe5-46if` | **2006-06-13** ⚠️ *corrected Phase 1 — 4 yrs earlier than assumed* | ✅ no longer binds |
| 2.6 | Event map | deterministic reconstruction | any | ⚠️ see §3 |

### 2.6 is almost certainly a degenerate condition

Any 60-day window contains ~2 CPI prints, ~2 employment reports and 1–2 FOMC
meetings — **≥5 events against a `≥3` threshold**. It has fired in 5 of 5
pilot runs. The backtest should confirm this fires ~100% of the time
historically, in which case the **L2 chop-pressure flag is a constant** and
belongs in the same finding as the constant layer scores. Cheap to verify;
potentially a second degenerate boolean in the design.

---

## 3. Two tiers — and the overlap is the interesting part

*Windows revised by Phase 1 — see `PHASE1_SOURCES.md` §5.*

| | **Tier 1 — full fidelity** | **Tier 2 — statistical power** | **Tier 2-ext** |
|---|---|---|---|
| Window | 2022-08 → 2026-08 | **2009-12 → 2026-08** | 2007-07 → 2009-12 |
| Weekly runs | ~208 | ~865 | ~130 |
| Variables | all 12 scored (incl. 1.1) | 11 (1.1 dropped) | 10 (1.6 also degraded) |
| Binding constraint | Polygon rolling 5-yr | **VIX3M 2009-09-18** | HYG 2007-04 |
| Regimes covered | 2022 bear tail, 2023 correction | + 2011, 2015–16, 2018 Feb & Q4, **2020 COVID**, full 2022 bear | **2008 crisis** |

Tier 2-ext requires an operator ruling — it buys 2008 only at the cost of
scoring 1.6 degraded through the period where the vol term structure was the
strongest available DOWN signal. See `PHASE1_SOURCES.md` §5.

**Run both, and exploit the overlap.** Over the shared 2022-08 → 2026-08
window you can score Tier 1 *with* 1.1 and *without* it, on identical data.
That directly measures 1.1's marginal contribution — which is the one real
uncertainty in Tier 2, and it happens to test a claim already made in the
shadow-scoring analysis: that 1.1/1.2/1.3 are three readings of one fact and
dropping 1.1 costs little. If the two Tier 1 variants agree, Tier 2's
conclusions carry.

---

## 4. Phased plan

### Phase 0 — realized class distribution ✅ **COMPLETE 2026-08-17**

Ran over Schwab SPY daily bars, 2009-11-30 → 2026-08-14. Integrity clean:
4,202 bars, 0 duplicates, 0 malformed, 0 gaps > 5 calendar days, 867 weekly
call dates (last trading day of each ISO week, from 2010-01-08).
Script: `phase0.py`.

| | 60-day (R≥+3%, D<5%) | 120-day (R≥+5%, D<5%) |
|---|---|---|
| **UP** | **44.3%** | **44.1%** |
| CHOP | 43.0% | 47.1% |
| DOWN | 12.7% | 8.8% |
| n | 858 | 849 |

**Result: the project is not killed. Proceed.**

1. **Always-UP baseline = 44.3% (60d) / 44.1% (120d)** — ≈46% / 45% on an
   approximate total-return basis (Schwab candles are a price series; SPY
   yields ~1.2%/yr). **This is the number criterion 1 must beat.**
2. **Class balance is healthy, not degenerate.** CHOP at 43–47% is comparable
   to UP rather than swallowing the sample, so §7 criterion 3 is testable as
   the spec writes it.
3. **The drawdown-gate hypothesis was wrong** — see the correction box in the
   MAINTAIN proposal §E3. Of windows meeting the return bar, only 6.2% (60d)
   and 12.0% (120d) are killed by `D ≥ 5%`. **The return threshold binds, not
   the drawdown gate.** R and D are strongly negatively correlated; the earlier
   random-walk argument wrongly treated them as independent. Intraday-extreme
   measurement bites somewhat harder (UP 42.4% / 41.5%) but does not change the
   conclusion.
4. **DOWN is rare and clustered — the real sample-size problem.** 12.7% / 8.8%,
   concentrated in 2011, 2015, 2018 and 2022: roughly 4–5 distinct episodes
   behind 75–109 heavily overlapping windows. **Even the full Tier 2 backtest
   will validate DOWN calls weakly.** Plan for that rather than discovering it
   at Phase 5.
5. **Regime dispersion is large and real — the encouraging finding.** Annual UP
   rate ranges from **6% (2015, 120d) to 67% (2013)**; worst years 2015, 2022,
   2011, 2018, best 2013, 2020, 2019, 2010. This is precisely the variation a
   tenor scan exists to anticipate, and it is where signal would show up.

**Immediate implication for the live pilot:** the scan currently calls UP every
week, and always-UP scores 44%. On present form it is tracking to score ~44% —
exactly the baseline, wrong 56% of the time. The standing 2026-08-16 UP call is,
absent demonstrated edge, a 44% proposition into its 2026-10-15 window.

### Phase 1 — source verification spike ✅ **COMPLETE 2026-08-17**

Full results in `PHASE1_SOURCES.md`. Headlines:

- **Two plan assumptions were wrong** — CFTC TFF starts 2006-06-13 (not
  2010-06), and VIX3M starts 2009-09-18 (not 2002-12). `VXV_History.csv` is a
  24-row stub, not the deep archive it appears to be.
- **All vendor intermediaries retired** in favour of issuing authorities:
  Treasury.gov, CFTC, CBOE, federalreserve.gov. FMP is out entirely.
- **BLS is a hard 403** (persistent, browser-UA too) **and it doesn't matter** —
  2.6 is unscored, the L2 flag never gates the call, and event density is
  degenerate by arithmetic (~5.9 events per 60-day window vs a ≥3 threshold).
  **The L2 chop-pressure flag is a second constant** alongside the layer scores.
- **Polygon Wyckoff floor is account-level**, identical for SPY/QQQ/IWM, and
  **rolling** — confirmed by re-request at `days=3650`.
- ~1.6 MB of raw inputs cached and committed under `data/`.

### Phase 2 — point-in-time harness *(2 days)*

The lookahead traps, each with a specific rule:

- **COT publication lag.** Reports are published Friday ~3:30pm ET for the
  prior Tuesday. Use the report *available at run time*, never the report
  *dated nearest*. The `tenor_2026-08-09-c2` entry sets the precedent and its
  reasoning should be lifted verbatim.
- **Trailing-only 52-wk high** for 1.3.
- **Dividend adjustment consistency — a real trap.** HYG yields ~6% and LQD
  ~4%; a price-return vs total-return choice materially changes the 2.1 13-wk
  ratio trend. Every pilot run has noted "both legs fell in absolute terms —
  rate pressure, not risk appetite," which is exactly the signature of this
  effect. **Match whatever Schwab weekly closes actually are, and state it.**
  Consistency with the live runs matters more than theoretical correctness.
- **Engine version pinning.** The probe returned `engine_version: 2.1.4`,
  `config_hash: 59fdaa23fa16`, `schema_version: 2.1` — against a tool
  description citing 2.0, so drift is already visible. Record both with every
  cached scan; a mid-backtest engine change invalidates results.

### Phase 3 — variable computation *(2 days + 1 day Wyckoff)*

The 11 non-Wyckoff variables are deterministic formulas straight from the
spec. Wyckoff needs ~208 weeks × 3 symbols ≈ **624 `as_of` calls** for Tier 1
— check rate limits, and **cache aggressively: `as_of` outputs are immutable,
and the source window is rolling away.**

> **Time-sensitive recommendation:** harvest and cache the historical Wyckoff
> scans **now**, ahead of the rest of the build. They are the only input that
> degrades with delay. This can run before the operator rules on anything else.

### Phase 4 — scoring engine *(1 day)*

Implement live scoring (majority-vote, §3/§4, with the §9 clarifications) plus
the shadow variants from the MAINTAIN proposal — A1 magnitude banding, A2 raw
sum, A3 coverage-normalized, B block voting. The backtest is the instrument
for deciding between them; it must compute all of them side by side.

### Phase 5 — outcome scoring and inference *(1–2 days)*

Mechanically easy, statistically the most dangerous phase.

**840 weekly runs with 120-day windows are ~90% overlapping.** Reporting
"n=840, hit rate 62%" would repeat the pilot's own sample-size error at larger
scale and with more false authority. Required treatment:
- non-overlapping subsamples (every 17th week for the 120d window), **and**
- block bootstrap with block length ≥ the window, for confidence intervals.

Report effective sample size explicitly alongside every hit rate.

### Phase 6 — write-up and recommendation *(1 day)*

Feeds the October gate and the MAINTAIN decision.

**Total: ~9–11 days Tier 2, +1–2 days for the Tier 1 overlay.**

---

## 5. What the backtest can and cannot settle

**Can:** whether the variables separate regimes out of sample; whether live or
shadow scoring produces more separation; whether confidence tiers calibrate;
whether CHOP is meaningful or residual (§7 criterion 3); whether the chop-flag
conditions ever fire in a bear; whether the ±40bp, 3%, 5%, ±0.5% `[CAL]`
thresholds sit anywhere near sensible; whether 2.6 event density is degenerate.

**Cannot:** operational quality — data degradation, producer bugs, source
gating, operator judgment. Every one of those has bitten the pilot (four
corrections in five runs) and none appear in a backtest, where all sources
resolve cleanly by construction. **A backtest will therefore look better than
live will.** Discount accordingly, and keep the forward pilot running.

Also unavailable: 1.8's dealer structure, which is annotation-only and so
excluded by design rather than by limitation.

---

## 6. Assessment — is it worth doing?

**Yes, conditional on Phase 0, and with one action starting immediately.**

The reasoning:

1. **Phase 0 is cheap and can kill it.** Half a day, no dependencies. If the
   outcome thresholds produce a degenerate class balance, that must be fixed
   before anything else — and it would be a bigger finding than the backtest.
2. **The alternative is worse.** Extending a forward pilot that structurally
   cannot produce evidence for criteria 1 and 2 spends the same calendar time
   and yields nothing. The backtest is the only path to an answerable gate.
3. **The Wyckoff `as_of` discovery makes it tractable.** Removing the engine
   reimplementation cuts the highest-risk item and roughly a third of the
   effort. Two weeks is a real but proportionate cost for the question.
4. **The 5-year rolling window makes it time-sensitive.** Waiting is not
   free — the most valuable history is the part expiring first.

**Recommended sequence:** Phase 0 standalone → operator ruling → Wyckoff
harvest (start early, in parallel with the ruling) → Phases 1–6.

**Scope discipline:** the backtest tests the scan **as specified**, including
its known weaknesses. It is not the place to add rate-path expectations, index
concentration, or single-name event risk. Those remain out of scope per the
MAINTAIN proposal §7.

---

## 7. Open questions for the operator

1. Run Phase 0 now as a standalone, before deciding on the rest?
2. Start the Wyckoff `as_of` harvest immediately given the rolling window, or
   accept the loss of 2022 if this slips?
3. Tier 2 only (more history, no 1.1), or both tiers with the overlap
   comparison? The overlap is ~1–2 extra days and directly tests the "1.1 is
   redundant with 1.2/1.3" claim.
4. Where do backtest outputs live? They are derived analysis, not calls —
   `log/tenor/` is for real calls, so a separate location (or kapman-kb, since
   nothing in them is private position data) may be the better fit. **This is
   a records-grammar question and needs a ruling before Phase 5 writes
   anything.**
