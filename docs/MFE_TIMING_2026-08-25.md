# MFE Timing — Exit-Truncated Measurement — 2026-08-25

Measured from the operator's realized trade record, prompted by the working
belief that swing trades are opened at 60–120 DTE but reach maximum favorable
excursion in under 10 days. **Purpose of this file: be found and settled at the
forward-log maturation window (~mid-September 2026), alongside
`ECONOMICS_STUDY_2026-07-02.md` — see the Re-evaluation checklist at the
bottom.** Tracked as kapman-kb#132.

The headline observation is confirmed. The inference usually drawn from it is
not supported, and the two candidate explanations prescribe opposite changes to
`SWING_DTE_BAND`. Nothing here changes a runtime contract.

Tags follow PILOT_LESSONS convention: **[KB]** runtime contract change (HITL),
**[ENG]** engineering/code, **[CAL]** parameter calibration, **[PROC]**
process/tooling.

## Provenance

- Source: tradelog `GET /api/analysis/excursions` — `LotExcursion` records
  computed on daily marks from `HistoricalMark`, joined to matched lots.
- 622 closed lots returned; **588** carry a usable
  `openTradeDate` / `mfeDate` / `closeTradeDate` triple and positive holding
  period. Pulled 2026-08-26T02:0xZ.
- Lot open dates 2024-01-05 → 2026-08-10; closes 2024-01-16 → 2026-08-18.
- Setup tags: `long_call` 287, `cash_secured_put` 122, `covered_call` 56,
  `bull_vertical` 45, `diagonal` 25, `stock` 20, `long_put` 12, `calendar` 11,
  `short_call` 7, `bear_vertical` 3.
- Cross-reference: `docs/economics_study_2026-07-02/live_onsets.csv`
  (99 onsets, `fwd_bars` median 6 / max 12).
- No repository was modified by the measurement; this commit is archival.

## Measurement

Days-to-MFE is `mfeDate − openTradeDate`. "MFE position" is that value as a
fraction of the holding period — 0% means the peak came at entry, 100% means it
came at the exit.

| Cohort | n | median days to MFE | median hold | MFE position | ≤10d |
|:---|---:|---:|---:|---:|---:|
| All closed lots | 588 | 6 | 11.5 | 93% | 67% |
| `long_call` | 287 | 6 | 12 | 83% | 67% |
| `cash_secured_put` | 122 | 6 | 9 | 100% | 70% |
| `covered_call` | 56 | 5 | 7.5 | 100% | 73% |
| `bull_vertical` | 45 | 7 | 11 | 71% | 69% |
| **held 30+ days** | **76** | **32.5** | **46** | **91%** | **24%** |

## The headline is confirmed; the inference is not

Long calls do reach MFE at a median of 6 days, with 67% peaking inside 10 days.
That much matches the working belief.

The MFE-position column is what undermines the usual reading. If the move
genuinely exhausted around day 6 and then gave back, the peak would sit at
roughly 30–50% of the holding period. It sits at **83%** for long calls and
**100%** for cash-secured puts and covered calls — the best price is at or
immediately adjacent to the exit. Positions are typically still climbing when
they are closed.

So MFE is not arriving at day 6 because the edge decays at day 6. It is arriving
at day 6 because the median position is closed at day 12. The measurement is
truncated by exit behavior.

The 30+ day cohort isolates this. Holding longer moves the median peak to 32.5
days and drops the ≤10-day share from 67% to 24%, while MFE position stays at
91%. Days-to-MFE tracks the holding period rather than resting at a fixed
horizon — which is what exit truncation looks like and what a genuine 10-day
edge window does not.

## Two explanations, opposite prescriptions

1. **The move is genuinely fast.** 60–120 DTE buys optionality the trade never
   uses; shorten expirations and stop paying for it. **[CAL]**
2. **Exits are early.** The DTE band is appropriate and winners are being cut
   before the move completes; the fix is holding discipline, not contract
   selection. **[KB]**

The evidence currently tilts toward (2), primarily on the MFE-position and
30+ day results. Acting on (1) would be precisely backwards if (2) holds, which
is why this file exists rather than a parameter change.

## What neither dataset can settle

The discriminating measurement is **post-exit continuation** — what the
underlying does after the position is closed. If price keeps advancing past the
exit, exits are early. If it stalls or reverses, the move really was finished.

Neither available dataset reaches it. `live_onsets.csv` is right-censored at
`fwd_bars` max 12, well inside the horizon in question, and the excursion
records stop at the close by construction. This requires new data, not
reanalysis.

## What stands regardless of which explanation wins

**The DTE/hold mismatch is real either way.** Contracts are bought with 60–120
days of life against a 12-day median hold — three to ten weeks of optionality
purchased, roughly one and a half used. Both candidate fixes address it; they
simply move in opposite directions.

**Knock-on for the weekly-conflict force-flag.** The case for the weekly
timeframe carrying weight in the Wyckoff read rests on the swing band implying
10–17 week holds. The realized median hold is 12 days, a horizon on which the
daily read is closer to governing. The weekly-conflict flag accounted for 18 of
37 queued items on the 2026-08-26 run (kapman-kb#127), so any rule written for
it should be settled together with this question, not ahead of it. **[KB]**

## Re-evaluation checklist (run when the forward log has cooked)

1. Recompute the table above on the matured record; confirm whether MFE position
   still clusters at 83–100% once the sample includes more long holds.
2. Measure post-exit continuation: for each closed lot, the underlying's path
   over the 20 and 60 trading days following `closeTradeDate`. This is the
   discriminating test and it needs new data.
3. If continuation is positive and material → explanation (2); address holding
   discipline and leave `SWING_DTE_BAND` alone.
4. If continuation is flat or negative → explanation (1); re-derive the DTE band
   from realized hold distribution and re-price the theta saved.
5. Either way, re-derive the band from the realized hold distribution rather
   than from the nominal swing horizon.
6. Settle the weekly-conflict force-flag rule (kapman-kb#127) only after 3–5
   resolve, since the governing timeframe follows from the realized hold.
7. Cross-check against `ECONOMICS_STUDY_2026-07-02.md`'s own checklist — both
   are queued for the same window and both bear on structure selection.

## Caveats

Daily marks only — intraday MFE is invisible, so true peaks are understated and
their timing is quantized to the day. 100 of 622 lots carry unpriced-day gaps
(median 0, so the typical lot is fully priced). Excursions are computed per
matched lot, so a scaled-out position contributes several lots rather than one
position-level path. `setupTag` is assigned by the tradelog, not by the KB
runtime, so cohorts are not strictly Pass-1 dispositions. The sample spans
2024-01 → 2026-08 and mixes regimes without adjustment. Nothing here is
risk-adjusted or slippage-adjusted, and no causal claim is made about why exits
land where they do.
