# Swing Tenor Scan — final recommendation

**Date:** 2026-08-17 · **Issue:** kapman-kb#95
**Scope:** closes the backtest study (Phases 0–3b). Supersedes the A/B
recommendations in `MAINTAIN_tenor_shadow_scoring.md`, which this study refutes.
**Status:** for operator ruling. Nothing in the pilot spec has been edited, and
no logged call in `kapman-journal/log/tenor/` has been touched.

---

## 1. Recommendation

**Retire the directional UP/DOWN/CHOP call. Keep the weekly evidence review and
the invalidation conditions. Do not codify `MARKET_TENOR`, and do not wire any
part of this to Pass 1 or Pass 2.**

The pilot asked whether a 13-variable composite could forecast market tenor over
60–120 days well enough to beat the equity-drift baseline. Measured over
2007–2026, it does not, and the ways it might be repaired do not work either.

The pilot did its job. It returned a negative, roughly eight weeks before the
forward record could have produced one.

---

## 2. Evidence

| Phase | Finding |
|---|---|
| **0** | Always-UP baseline is **44.3% (60d) / 44.1% (120d)**. Class balance healthy (CHOP 43–47%), so the design was testable as written. |
| **1** | Sources moved to issuing authorities (Treasury/FRED, CFTC, CBOE, federalreserve.gov). Two plan assumptions corrected: TFF starts 2006-06 not 2010-06; VIX3M starts 2009-09 not 2002-12. |
| **2** | Point-in-time harness, 0 lookahead violations, reproduces the logged 2026-08-16 run on 9 of 11 readings. Caught a silent 44bp corruption in the treasury cache. |
| **3** | **Composite edge vs baseline: −8.0 (60d), +0.0 (120d)** on non-overlapping windows. Shadow schemes A1/A2/B all *worse*, even given best-in-sample thresholds. |
| **3b** | ~3 of 11 variables carry weak, sign-stable signal (\|IC\| 0.06–0.33); one is scored **backwards** by the spec. Both Bonferroni-passing in-sample results **reversed sign** out of sample. |

### §7 criteria

| # | Criterion | Verdict |
|---|---|---|
| 1 | Beat always-UP | **Not met.** −8.0 / ±0.0 non-overlapping. |
| 2 | Confidence calibration | **Untestable.** Depends on degradation states a backtest cannot reproduce. |
| 3 | CHOP usefulness | **Not met.** CHOP issued on 61% of windows against a 43–47% occurrence rate — the residual-bucket failure the criterion warns of. |
| 4 | Invalidation quality | **Holds.** Never under test, and still the strongest part of the design. |

---

## 3. Why it cannot be repaired

**The binding constraint is the horizon, not the design.** A 60–120 day forecast
yields ~4–6 independent observations per year; two decades gives ~40–80. A
forecaster with \|IC\| ~0.2 cannot be validated at that sample size — the
confidence interval will always swamp the effect.

This is a property of the question the scan asks. Rebuilding around the three
surviving variables hits the identical wall: by the time enough independent
observations accumulate to demonstrate edge, the regime that produced it has
turned over.

Corollary: **any future proposal to fix the scan by re-scoring, re-weighting or
adding variables should be rejected on sample-size grounds alone**, unless it
also shortens the forecast horizon.

---

## 4. What to keep

1. **The four invalidation conditions.** Price-observable, refreshed weekly,
   with named transmission paths. This is the tenor report's real advantage over
   narrative research, which names risks but nothing that could falsify itself.
2. **The weekly variable pull, as monitoring rather than forecast.** Diffing COT
   positioning, dealer gamma, vol term structure, credit and breadth week over
   week is useful situational awareness whether or not it predicts. The error was
   compressing it into "S = +3, UP."
3. **The append-only discipline and the segmentation idiom.** Both worked, and
   both are why this study could be trusted.

## 5. What to drop

1. The composite `S = 2×L1 + L2` and the §4 UP/DOWN/CHOP mapping.
2. The weekly confidence rating — it never varied with S because S never
   varied in the live sample.
3. `MAINTAIN_tenor_shadow_scoring.md` proposals **A (shadow scoring)** and
   **B (block voting)** — withdrawn, refuted by Phase 3.
4. The Wyckoff `as_of` harvest — S1 yields 11–21 independent observations and
   cannot resolve 1.1's contribution. 2 of 627 scans recorded; harvest stopped
   deliberately.

## 6. Still open, for the operator

1. **1.3's inverted sign** — the one finding with consistent sign in and out of
   sample (distance-from-52wk-high predicts *lower* forward returns at this
   horizon). Rests on \|IC\| ~0.2 with OOS n=13–24. **Not actionable**; recorded
   as the place to start if this is ever revisited.
2. **1.7 reconstruction** — the harness and the kapman-polygon producer disagree
   (0.9612 vs 0.9447) on an undocumented variance convention, which can flip a
   boundary read. Worth pinning regardless, since 1.7 is used elsewhere.
3. **Monthly insurance harvest** (144 scans) against the rolling 5-year window —
   cheap, but it buys description, not inference. Default: skip.
4. **Whether to keep running the weekly report at all** in monitoring-only form,
   or stand it down entirely.

---

## 7. Corrections made during this study

Recorded because the study's credibility rests on them having been caught.

| Claim | Status |
|---|---|
| "The layer scores are constants" | **Wrong.** S ranges −6..+6 over S2. True only within sustained uptrends. |
| "The design cannot disagree with always-UP, arithmetically" | **Wrong.** It disagrees 66% of the time. |
| "The `D<5%` drawdown gate is the binding term" | **Wrong.** The return threshold binds; R and D are negatively correlated. |
| "CFTC TFF starts 2010-06" / "VIX3M starts 2002-12" | **Wrong.** 2006-06 and 2009-09. |
| Treasury.gov concatenation is safe | **Wrong.** Silent 44bp corruption from column drift. |
| Inverted-sign variables are a real finding | **Mostly wrong.** Both strongest results reversed out of sample. |

The last one is the important one: the in-sample table told a confident,
coherent story about systematically inverted variables. The out-of-sample check
refuted it. Had the study stopped at Phase 3b's first half, it would have
delivered a wrong conclusion with more confidence than the correct one.
