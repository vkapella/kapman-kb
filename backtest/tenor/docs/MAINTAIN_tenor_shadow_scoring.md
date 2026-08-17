# MAINTAIN proposal — Swing Tenor Scan pilot: shadow scoring, de-correlation, baseline logging

**Target:** `kapman-kb/docs/SWING_TENOR_SCAN_PILOT_v0.1.md` (issue #95)
**Proposed by:** analysis session 2026-08-17
**Status:** DRAFT — operator ruling required, HITL turn-by-turn per `AGENTS.md`
**Affects:** §3 (layer scoring), §5 (report format), §6 (frontmatter grammar), §7
(re-evaluation criteria). **Does not touch** §4 composition, any `[CAL]`
threshold, or any logged entry.

---

## 1. Finding that motivates this

Across all five logged run dates, **`layer1_score` and `layer2_score` have
never taken any value other than `+1`**, and `composite_S` never anything other
than `+3`:

| Run | Call | L1 | L2 | S | Degraded | SPY |
|---|---|---|---|---|---|---|
| 2026-07-28 (c1) | CHOP/low | +1 | +1 | +3 | 3 | 739.09 |
| 2026-07-29 (c1) | CHOP/low | +1 | +1 | +3 | 2 | 737.91 |
| 2026-08-03 (c1) | UP/low | +1 | +1 | +3 | 1 | 747.03 |
| 2026-08-09 (c2) | UP/med | +1 | +1 | +3 | 0 | 773.26 |
| 2026-08-16 | UP/med | +1 | +1 | +3 | 0 | 776.34 |

Over that span SPY rose 5.0%, QQQ went distribution → reaccumulation phase D,
COT moved from "not a contrarian extreme" to z +2.06, and the VIX complex
degraded and recovered. Thirteen variables moved; the score moved zero times.

The §7 note already suspects a weaker version of this ("does S ever leave
−3..+3?"). The actual result is stronger: **S is a constant, not a
range-bound variable.** The single call change in the record (CHOP → UP at
08-03) came from the §9.1 rule clarification, not from data — so 100% of
observed call variation is attributable to a spec edit and 0% to the market.

### Root cause — two compounding effects

**(a) Sign-only voting discards magnitude.** "Majority read mapped to −2..+2"
resolves in practice to: any directional majority → ±1, near-unanimity → ±2.
With 7 and 5 variables per layer, unanimity effectively never occurs. A 6-of-7
majority and a 4-of-7 majority both produce +1.

**(b) L1's variables are correlated, and the correlated cluster is the one the
naive baseline already knows.** Variables 1.1 (Wyckoff regime), 1.2 (40-wk MA
position/slope) and 1.3 (distance from 52-wk high) are three readings of one
fact: *SPY is in an uptrend near its highs*. Three of seven votes. In any
uptrend they deliver +3 automatically; vol is typically calm in the same
regime, adding 1.6 and 1.7. Five of seven votes are locked bullish before
breadth or leadership is consulted. **L1 = +1 is structurally guaranteed in an
uptrend**, and L1 carries double weight.

### Consequence for the §7 gate

- **Criterion 1 (beat always-UP)** — the post-2026-08-03 governing series is
  four runs, four UP calls, **zero disagreements with the baseline**. A
  forecaster that never disagrees with its benchmark cannot beat it. This is
  arithmetic, not sample size; more weeks cannot change it.
- **Criterion 2 (confidence calibration)** — confidence has varied only with
  degradation counts and dissent counts, never with S, because S is constant.
  There is nothing to calibrate.
- **Criterion 4 (invalidation quality)** — unaffected and working. This part
  of the design should survive regardless of what happens to the scoring.

---

## 2. What is and is not being proposed

The spec's §7 rule — *"do not self-tune `[CAL]` items mid-pilot"* — is correct
and this proposal does not break it. The distinction being drawn:

| | Handling |
|---|---|
| A `[CAL]` threshold is mis-set | **Leave alone.** This is what the pilot exists to discover. The ±40bp band, 3% distance, 5% contango, ±0.5% slope all stay untouched. |
| The instrument reads a constant | **Not a calibration question.** No quantity of additional weeks produces evidence about an invariant instrument. Six more runs yield six more `S = +3`. |

Accordingly: **no live scoring rule changes, no call changes, no threshold
changes.** Everything below is either an additional logged field or a
parallel computation that makes no call.

---

## 3. Proposal A — shadow scoring (primary)

Compute two additional scores each run, alongside the live one. Neither
produces a call. Both are recorded in frontmatter.

### A1. Magnitude banding — the highest-value change

Replace sign-only contributions with a three-band magnitude read **for the
shadow score only**, using percentages the runs already compute and log:

| Band | Contribution |
|---|---|
| \|Δ\| < 1% | 0 |
| 1% ≤ \|Δ\| < 5% | ±1 |
| \|Δ\| ≥ 5% | ±2 |

Applicable as-is to 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.3, 2.4 — eight of the
twelve scored variables — with no new data collection. 1.1 (regime), 1.7
(ratio vs 1.0), 2.2 (rule-banded already) and 2.5 (positioning) keep their
current −1/0/+1 reads until a banding is proposed separately.

**Evidence this matters.** Applying the band retroactively to the rotation
pair, from the logged percentages:

| Run | 1.4 breadth | 1.5 XLY/XLP | Rotation (banded) | Rotation (live, sign-only) |
|---|---|---|---|---|
| 07-28 | +3.45% → +1 | −7.90% → −2 | **−1** | 0 |
| 07-29 | +4.37% → +1 | −8.24% → −2 | **−1** | 0 |
| 08-03 | +2.27% → +1 | −3.15% → −1 | **0** | 0 |
| 08-09 | +2.86% → +1 | −1.38% → −1 | **0** | 0 |
| 08-16 | +5.23% → +2 | −0.28% → **0** | **+2** | 0 |

The rotation signal travels **−1 → +2 across the pilot** — defensive
leadership collapsing from −7.9% to −0.28% while breadth strengthens from
+3.45% to +5.23% — and the live scan records 0 every week. Sign-only voting
treats −7.90% and −0.28% as the same reading.

### A2. Linear raw sum

Each variable −1/0/+1 (or banded per A1), summed rather than majority-voted.
L1 ∈ −7..+7 (1.1–1.7), L2 ∈ −5..+5 (2.1–2.5), `S_shadow = 2×L1 + L2`.
1.8 and 2.6 remain annotation and are excluded.

Back-computed from the logged evidence tables, unbanded:

| Run | L1 raw | L2 raw | S_shadow | Live S |
|---|---|---|---|---|
| 07-28 | +3 | +1 | **+7** | +3 |
| 07-29 | +4 | +1 | **+9** | +3 |
| 08-03 | +4 | +1 | **+9** | +3 |
| 08-09 | +4 | +2 | **+10** | +3 |
| 08-16 | +5 | +1 | **+11** | +3 |

**Caveat, stated up front:** the degraded count falls 3 → 2 → 1 → 1 → 0 across
these same runs, and degraded scores 0, so a recovering data pipeline
mechanically inflates a raw sum. Decomposing the +7 → +11 move: **+2 from 1.7
recovering (tooling) and +2 from 1.1 genuinely improving (ranging → markup).**
Half the dispersion is real. A2 must therefore always be logged alongside A3.

### A3. Coverage-normalized shadow

`L_norm = raw ÷ (count of non-degraded scored variables in the layer)`;
`S_norm = 2×L1_norm + L2_norm`. Controls for the pipeline confound above.

| Run | L1 norm | L2 norm | S_norm |
|---|---|---|---|
| 07-28 | 3/6 = 0.500 | 1/3 = 0.333 | **1.33** |
| 07-29 | 4/7 = 0.571 | 1/3 = 0.333 | **1.48** |
| 08-03 | 4/7 = 0.571 | 1/4 = 0.250 | **1.39** |
| 08-09 | 4/6 = 0.667 | 2/5 = 0.400 | **1.73** |
| 08-16 | 5/7 = 0.714 | 1/5 = 0.200 | **1.63** |

Non-monotone, and it separates layer behaviour the live score cannot: at 08-16
L1 improves (0.667 → 0.714) while **L2 deteriorates sharply (0.400 → 0.200)**
on the arriving COT extreme. The live instrument recorded `+1 / +1`.

### Why this is append-only-safe

All three are computable **retroactively from the evidence tables already
written**, without editing a single logged entry. The logged calls, scores and
outcomes stand exactly as recorded; the shadows are a parallel column. This
converts five flat records into five records with dispersion **today**, and
yields ~12 shadow observations by the October gate — enough to set thresholds
by observed percentile rather than a priori.

---

## 4. Proposal B — de-correlate L1 by block voting (shadow only)

Group 1.1–1.7 into three blocks; each block votes the sign (or banded sum) of
its members, and L1_block ∈ −3..+3:

| Block | Members | Measures |
|---|---|---|
| Trend | 1.1, 1.2, 1.3 | SPY is in an uptrend near highs |
| Vol | 1.6, 1.7 | Vol is calm |
| Rotation | 1.4, 1.5 | Internals / leadership |

Back-computed, sign-only:

| Run | Trend | Vol | Rotation | L1_block |
|---|---|---|---|---|
| 07-28 | +1 | +1 | **0** | +2 |
| 07-29 | +1 | +1 | **0** | +2 |
| 08-03 | +1 | +1 | **0** | +2 |
| 08-09 | +1 | 0 | **0** | +1 |
| 08-16 | +1 | +1 | **0** | +2 |

**Block voting alone is necessary but not sufficient, and the back-computation
proves it: the rotation block is 0 in all five runs**, because 1.4 and 1.5
cancel exactly every time under sign voting. L1 ends up decided entirely by
trend and vol — i.e. by what always-UP already knows.

**B must therefore be combined with A1.** Banded, the rotation block varies
−1/−1/0/0/+2 as shown in §3. Neither change works alone; together they give
breadth and leadership real weight against the triple-counted trend cluster.

---

## 5. Proposal C — log baseline disagreement (free)

Add one frontmatter field:

```yaml
disagrees_with_always_up: true | false
```

`true` when `call != UP`. Makes §7 criterion 1's status legible every week
instead of only at the gate. On the current record it reads `false` four times
in four for the governing post-08-03 series — a fact worth surfacing weekly
rather than discovering in October.

Optionally also `shadow_call_would_be:` once shadow thresholds exist, to track
whether the shadow scheme *would* have disagreed. That is the actual test of
whether A/B are worth adopting live.

---

## 6. Proposal E — cheap guards (no scoring impact)

**E1. Wyckoff range-contains-spot assertion.** Assert the 1.1 range brackets
the current close; log `range_stale: true` when it does not.

*Live instance:* the 2026-08-16 run recorded IWM as "reaccumulation **phase C**,
range 284.07–302.72" while IWM closed at **305.09** — 0.8% *above* the cited
range top and 0.03% off its 52-week high (305.18, verified 2026-08-17). The
run classified a broken-out index as still range-bound. It did not change the
call (IWM scored bullish via `trend: up` / `close_vs_30w: above`, and the L1
ranging condition needs ≥2 of 3), but it is load-bearing for the CHOP boundary
and it understated the strongest available evidence for the breadth thesis.

**E2. Single-name event risk in the 2.6 map.** The event map is macro-only by
construction. Add the next 1–2 mega-cap earnings dates as **unscored**
annotations. *Live instance:* NVDA reports 2026-08-26 — inside the first 60
days of the 08-16 window, and plausibly the largest single-name index-risk
item in it — and appears nowhere in that run's event map.

**E3. Vol-scaled outcome bands, logged in parallel.** §6's fixed ±3%/60d and
±5%/120d are ≈0.5σ at hv60 = 0.1375 (σ₆₀ ≈ 5.6%, σ₁₂₀ ≈ 7.9%) — internally
consistent, to the spec's credit.

> **Corrected 2026-08-17 by the Phase 0 measurement.** An earlier draft of this
> item argued the `D < 5%` drawdown gate was "near a coin flip and the binding
> term," reasoning from an expected max drawdown of ~0.8σ for a driftless walk.
> **That was wrong.** Measured over 858/849 weekly windows 2010–2026: of the
> windows that meet the return bar, only **6.2% (60d) and 12.0% (120d)** are
> killed by `D ≥ 5%`. The gate costs ~3 points at 60d and ~6 at 120d. **The
> return threshold is the binding constraint, not the drawdown gate.** The error
> was treating R and D as independent; they are strongly negatively correlated,
> because paths delivering +3%/+5% are predominantly low-drawdown paths.
> Realized-CHOP is also *not* the dominant residual (43.0% / 47.1%, comparable
> to UP), so criterion 3 is testable as written.

E3 therefore **loses its urgency but stays as a cheap diagnostic**: log
σ-scaled classifications alongside the fixed ones at back-fill, change nothing
about the fixed rule. It is now a nice-to-have, not a correction of a defect,
and should be dropped if it costs anything.

---

## 7. Not proposed — deliberately out of scope

- **Rate-path expectations** (2.2 reads only the realized 10y level; it has no
  band for a hawkish-minutes surprise). Real gap, but scope growth.
- **Index concentration** (no top-N weight measure alongside RSP/SPY breadth).
- **Any `[CAL]` threshold change.** Correctly deferred to the gate.
- **Historical backtest.** This is the real answer to the sample-size gap
  (§8) and probably the highest-value work after A/B — but it is a multi-day
  build, not a spec amendment, and belongs in its own proposal.

---

## 8. Sample size — recommend restating §7, not extending it

§7 assumes 8–12 logged weeks yields 8–12 observations. It does not:

- Five run dates, not six. **07-28 and 07-29 are one day apart** — the 07-29
  entry itself flags it as operator-directed and off-cycle and warns readers to
  weight the gap. Four weekly observations.
- 60–120 day windows from weekly runs overlap ~90%, all sampling one bull tape.
  Effective independent observations ≈ 1.
- At the October gate: roughly 3–4 `+60d` outcomes and **zero** `+120d`
  outcomes. The earliest `+120d` back-fill is 2026-11-25.
- The pilot has never observed a DOWN or a genuine CHOP tape. A three-class
  classifier that has only seen one class cannot be validated on hit rate.

**Recommendation:** keep the October date, change the question. Not *"did the
pilot beat always-UP?"* — that is already answerable and the answer is "it never
disagreed, so no." Instead: *"does shadow scoring produce dispersion worth
building on, and do the variables separate regimes out of sample?"* Same
calendar, honest question, and it is answerable with what will exist by then.

---

## 9. Summary of proposed edits

| § | Change | Type |
|---|---|---|
| §3 | Add shadow scoring definitions (A1 banding, A2 raw sum, A3 normalized, B blocks). **Live scoring unchanged.** | Additive |
| §5 | Add a "Shadow scores" report section, after the per-layer tables | Additive |
| §6 | Frontmatter: `shadow_S`, `shadow_S_norm`, `shadow_L1_block`, `disagrees_with_always_up`, `range_stale` | Additive |
| §6 | Log σ-scaled outcome classes alongside fixed at back-fill (E3) | Additive |
| §7 | Restate the gate question per §8; add shadow dispersion as an explicit criterion | Substantive |
| §3/2.6 | Mega-cap earnings dates as unscored event-map annotations (E2) | Additive |
| §8 | Wyckoff range-contains-spot guard as a run procedure note (E1) | Additive |

Every row except the §7 restatement is purely additive: no logged call changes,
no `[CAL]` threshold moves, no §4 composition change, no entry edited.

## 10. Open questions for the operator

1. Adopt A1+B as the shadow scheme, or A2/A3 only (banding is the bigger change
   and the bigger claim)?
2. Back-compute the five logged runs into a **separate** `log/tenor/shadow/`
   analysis file, or leave them uncomputed and start shadowing from the next
   run? (Back-computing is append-only-safe — it edits nothing — but it does
   produce derived numbers for calls already made.)
3. Restate the §7 gate question now, or leave §7 and note the limitation in the
   October write-up?
4. Is a historical backtest in scope at all before the gate?
