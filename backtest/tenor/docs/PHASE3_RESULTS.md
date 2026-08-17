# Phase 3 — scoring results

**Run:** 2026-08-17 · **Code:** `phase3_scoring.py` · **Segments:** S2, S3, S4
(S1 pending the Wyckoff harvest — see §6)

---

## 1. Headline

**On the only segment with meaningful sample size, the scan does not beat the
always-UP baseline.**

### S2 core — 2012-02 → 2026-08, 759 call dates

| Horizon | Scheme | Overlapping hit / base / edge | **Non-overlapping** hit / base / **edge** |
|---|---|---|---|
| 60d | live | 42.7 / 43.9 / −1.2 | n=75 → 41.3 / 49.3 / **−8.0** |
| 120d | live | 50.1 / 44.9 / **+5.1** | n=39 → 48.7 / 48.7 / **+0.0** |

**The +5.1 edge at 120d is an artifact of overlapping windows.** On
non-overlapping data — stride 19 weeks, so no two forward windows share a day —
it is exactly **zero**. The 60-day result is negative on both treatments.

759 weekly observations with 120-day windows are ~90% overlapping and carry
roughly **39 independent observations**, not 759. Any hit rate quoted against
the larger n is not a measurement.

---

## 2. The shadow schemes are not supported by the evidence

This contradicts the central recommendation of
`MAINTAIN_tenor_shadow_scoring.md`. Reported plainly rather than buried.

Each shadow was given its **best threshold chosen in-sample** from a sweep
(A1: 13 candidates, A2: 11, B: 7) — a deliberately generous test:

| Segment / horizon | Scheme | In-sample edge | Non-overlapping edge |
|---|---|---|---|
| S2 60d | A1@12 | +0.1 | **−6.7** |
| S2 60d | A2@11 | +0.4 | **−16.0** |
| S2 60d | B@8 | −0.1 | **−13.3** |
| S2 120d | A1@12 | +5.4 | **−5.1** |
| S2 120d | A2@9 | +6.1 | **−7.7** |
| S2 120d | B@5 | +5.3 | **−7.7** |

Every scheme shows the classic overfitting signature: a marginal in-sample gain
from cherry-picked thresholds that **evaporates or inverts out of sample**. On
S2 120d the live scheme (+0.0) beats all three shadows (−5.1, −7.7, −7.7)
despite them being handed their best threshold and live being handed none.

**Magnitude banding, raw summing and block voting do not improve this scan.**
The A/B recommendations should not proceed to the live spec on this evidence.

---

## 3. Correction to the earlier analysis

Two claims made before the backtest existed are **wrong in their general form**
and are corrected here rather than quietly dropped.

**Claim 1 — "the layer scores are constants."** False as a property of the
design. Live composite S over S2 ranges **−6 to +6** with wide dispersion:

```
S: -6:3  -5:16  -4:19  -3:56  -2:22  -1:29  0:62
   +1:170 +2:119 +3:153 +4:56  +5:42  +6:12
```

**Claim 2 — "the design cannot disagree with always-UP; arithmetically, not
empirically."** False. The scan calls non-UP **66% of the time** in S2.

What actually survives: within a *sustained uptrend* S clusters at +1..+3 and
non-UP calls become rare. That explains the live pilot's flat record — five
runs in a uniformly bullish tape — but it is a **property of that sample, not
of the mapping**. The "arithmetically" framing overstated the case and was
wrong.

**The real finding is different, and worse.** The scan is not silent; it
disagrees with the baseline constantly. Its disagreements simply are not right
more often than chance. A scan that never disagrees is fixable by recalibration;
a scan that disagrees at 66% and lands at zero edge has no signal to recalibrate
toward. That is a stronger negative than the one originally hypothesized, and it
rests on measurement rather than arithmetic.

---

## 4. S3 and S4 are not interpretable

| Segment | Horizon | Non-overlapping n | Live edge |
|---|---|---|---|
| S3 | 60d | 13 | +7.7 |
| S3 | 120d | **7** | +28.6 |
| S4 | 60d | 12 | +33.3 |
| S4 | 120d | **7** | +42.9 |

The large S4 crisis edges are the most eye-catching numbers in the study and
**should not be cited**. At n=7 the confidence interval spans essentially the
whole range; a single window flipping moves the edge by ~14 points. Phase 0
predicted this — DOWN occurs in only 4–5 distinct episodes across 16 years — and
the prediction held.

S4 additionally runs with three of twelve variables dark, including 1.6, whose
inversion was the crisis's loudest signal.

---

## 5. What this does and does not settle

**Settles:** the **11-variable** scan (1.1 dark) does not beat always-UP over
2012–2026 at either horizon once window overlap is accounted for. The proposed
shadow rescoring does not help.

**Does not settle:** whether the **12-variable** scan — including 1.1, the
Wyckoff regime read — behaves differently. That is what S1 exists for, and §6
argues S1 cannot answer it either.

**Does not settle:** live operational quality. Every source here resolves
cleanly; the pilot's actual failure modes (gated endpoints, stale ranges,
producer bugs) are invisible to a backtest.

---

## 6. The Wyckoff harvest — measured cost, and a recommendation against

Infrastructure is built and resumable (`harvest_record.py`, keyed on
`(as_of, symbol)`, engine-drift detection, 330-byte extracted records).

**Corrected S1 floor.** `as_of=2022-08-05` returns *"244 bars available, 250
required"*; 2022-08-19 succeeds at 254 bars. **S1 = 2022-08-19 → 2026-08-14,
209 call dates, 627 scans.**

**Measured cost: ~4.0 KB of JSON per scan × 627 ≈ 2.5 MB.** Every scan must
transit the assistant context to be recorded, so a full harvest is not
achievable in a single session and would consume a large multiple of what the
remaining analysis needs.

**And the value proposition has weakened.** S1's 209 weekly dates yield roughly
**11 (120d) to 21 (60d) non-overlapping observations**. S2, with 39, could not
distinguish +5.1 from 0.0. S1 cannot resolve 1.1's marginal contribution at a
third of that power — the measurement it was designed for is not available at
this sample size.

**Recommendation:** do **not** run the full 627. Two defensible options:

1. **Monthly insurance harvest** — every 4th week, 3 symbols ≈ **144 scans
   (~575 KB)**. Preserves a usable record against the rolling window at ~23% of
   the cost, accepting that it supports description, not inference.
2. **Skip it**, and record that 1.1's contribution is unresolvable with the
   history kapman-polygon retains.

The rolling-window argument still holds — 2022 expires first — so option 1 is
cheap insurance if there is any chance of revisiting. But it should be chosen
knowing it will not produce a hit-rate answer.

---

## 7. Implications for the §7 gate

- **Criterion 1 (beat always-UP):** not met by the 11-variable scan. −8.0 at
  60d, ±0.0 at 120d, non-overlapping.
- **Criterion 2 (confidence calibration):** untested here; needs the live
  confidence rule, which depends on degradation states a backtest cannot
  reproduce.
- **Criterion 3 (CHOP usefulness):** the scan called CHOP on **455 of 750** S2
  windows (61%) against a realized CHOP rate of ~43–47%. CHOP is over-issued
  relative to its occurrence — consistent with it being the residual bucket the
  criterion warns about.
- **Criterion 4 (invalidation quality):** unaffected, and still the strongest
  part of the design.

**The October gate now has a defensible answer to criteria 1 and 3 that four
more weeks of forward runs could not have produced.** That was the point of
building this.

---

## 8. Caveats on this result

- **1.1 is dark in every scored segment.** The backtest tests a reduced scan.
- **[CAL] thresholds** follow the run-log convention where the spec is silent
  (`HV_BOUNDARY` 2%, `COT_EXTREME_Z` 2.0). Neither was tuned to results; both
  are recorded in `phase3_scoring.py`.
- **1.7 reconstruction** differs from the polygon producer (Phase 2 §3) and can
  flip boundary reads. Unresolved, and it affects one of six L1 variables.
- **No block bootstrap yet.** Non-overlapping subsampling is a floor on rigour,
  not a substitute for interval estimates. The n=39 and n=7 samples deserve
  confidence intervals before anything is published beyond this repo.

---

# Phase 3b — per-variable information coefficient

**Run:** 2026-08-17 · **Code:** `phase3b_variable_ic.py`

Tests whether any *individual* variable carries signal, to distinguish "the
inputs are worthless" from "the compositing destroyed usable inputs."

## In-sample (S2, 2012-02..2026-08), Spearman IC vs forward return

Magnitudes oriented bullish-positive. Non-overlapping n=39 (120d) / 75 (60d).

| Var | Name | IC 120d | IC 60d |
|---|---|---|---|
| 1.6 | vol term structure | **−0.356** (t −2.32) | **−0.288** (t −2.57) |
| 1.3 | dist from 52wk high | **−0.328** (t −2.11) | **−0.254** (t −2.24) |
| 2.1 | credit HYG/LQD | −0.069 | **−0.358** (t −3.28) |
| 2.2 | rate impulse | +0.071 | **+0.324** (t +2.92) |
| S | composite (live) | +0.120 | −0.161 |

The composite has no IC, consistent with Phase 3. Several individual variables
do — **and the two strongest carry the sign OPPOSITE to how the spec scores
them.** More contango and closer-to-highs both predicted *lower* forward
returns, which is the well-documented behaviour of coincident risk-appetite
gauges: the spec reads "conditions are calm now" as "conditions will continue,"
and at a 60–120 day horizon that is backwards for mean-reverting state
variables.

## Out-of-sample sign check (S3+S4, 2007-07..2012-02)

A genuine holdout — this period played no part in finding the above.

| Var | IS 120d | OOS 120d | IS 60d | OOS 60d | Sign holds |
|---|---|---|---|---|---|
| 1.3 dist from 52wk high | −0.328 | −0.226 | −0.254 | −0.116 | **both** |
| 1.4 breadth RSP/SPY | +0.200 | +0.197 | +0.056 | +0.248 | **both** |
| 2.3 dollar UUP | +0.187 | +0.181 | +0.062 | +0.196 | **both** |
| 1.6 vol term structure | −0.356 | −0.006 | −0.288 | +0.028 | no |
| 2.1 credit HYG/LQD | −0.069 | +0.110 | **−0.358** | +0.186 | no |
| 2.2 rate impulse | +0.071 | −0.007 | **+0.324** | −0.196 | no |

**Both Bonferroni-passing in-sample results (2.1 at t −3.28, 2.2 at t +2.92)
reverse sign out of sample.** The strongest in-sample finding (1.6, −0.356)
collapses to ~0.00. This is a textbook demonstration that the in-sample
significance was a data-mining artifact, and it is why the OOS check was run
before drawing any conclusion.

## What survives

Three of eleven variables hold sign across all four tests:

| Var | Direction | vs spec |
|---|---|---|
| 1.4 breadth RSP/SPY | positive, IC +0.06..+0.25 | **correct** |
| 2.3 dollar (weakness bullish) | positive, IC +0.06..+0.20 | **correct** |
| 1.3 distance from 52wk high | negative, IC −0.12..−0.33 | **INVERTED** |

**Chance baseline:** with the first test fixing the sign, a variable holds
across the other three by coin-flip with probability ⅛, so ~1.4 of 11 are
expected by chance. Three is suggestive, not decisive. OOS n is 6–24 and the
OOS ICs are computed on overlapping samples (non-overlapping was too small even
to rank), so this is a *sign check*, not a significance test.

## Answer to the question Phase 3b was built to settle

Neither of the two framings. It is not "no signal anywhere," and not "good
inputs ruined by compositing." It is:

**~3 of 11 variables carry weak, directionally stable signal (|IC| 0.06–0.33);
one of those three is scored backwards by the spec; and the strongest
in-sample effects do not replicate.** Aggregating eleven variables of which
three are weakly informative, one is sign-inverted, and seven are noise
produces exactly the zero composite edge Phase 3 measured.

## The finding underneath all of it

The binding constraint is **the horizon, not the design**. A 60–120 day forecast
yields ~4–6 independent observations per year. Two decades of history gives
~40–80. No forecaster of modest edge (|IC| ~0.2) can be validated at that sample
size — the confidence intervals will always swamp the effect.

This is a property of the question the scan asks, not a fixable flaw in how it
asks it. Rebuilding around the three survivors would face the identical wall:
by the time enough independent observations accumulate to demonstrate edge, the
regime that produced it has turned over.
