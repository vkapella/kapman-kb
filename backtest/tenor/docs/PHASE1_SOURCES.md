# Phase 1 — source verification spike

**Run:** 2026-08-17 · **Status:** COMPLETE
**Method:** every source called live and its actual range measured. Per the
spec's kapman-mcp lesson — *never infer a producer gap from one failed call;
vary the parameter and retry.* Nothing below is assumed.

---

## 1. Two plan assumptions were wrong

Both had been carried into `TENOR_BACKTEST_PLAN.md` §2 unverified. Phase 1
exists to catch exactly this, and it did.

| Assumption | Plan said | Measured | Effect |
|---|---|---|---|
| CFTC TFF inception | 2010-06 | **2006-06-13** | Tier 2 could reach **4 years further back, including 2008** |
| VIX3M history | 2002-12 | **2009-09-18** | **VIX3M is the binding constraint**, not COT |

The TFF error came from dating the dataset to when CFTC *introduced* the TFF
report rather than how far they back-filled it: 1,053 weekly reports,
~52/year continuously from 2007.

The VIX3M error is a trap worth recording. `VXV_History.csv` — the pre-rename
ticker, which I expected to carry the long history — **is a 24-row stub
starting 2017-09-19**, not a deep archive. The real series is
`VIX3M_History.csv`, and it starts **2009-09-18**. Anyone reaching for VXV
expecting 2002 history will get a file that looks valid and is nearly empty.

---

## 2. Verified sources

All primary/government issuers, no gated vendor intermediaries.

| # | Input | Source | Verified range | Rows |
|---|---|---|---|---|
| 2.2 | Treasury par yield curve (1mo–30yr, incl. 2y/10y) | `home.treasury.gov` CSV, per-year | 2007-01-02 → 2026-08 | **4,891** |
| 2.5 | COT, TFF futures-only, E-MINI S&P 500 | `publicreporting.cftc.gov` `gpe5-46if` | 2006-06-13 → 2026-08-11 | **1,053** |
| 1.6 | VIX | `cdn.cboe.com` `VIX_History.csv` | 1990-01-02 → 2026-08-14 | **9,251** |
| 1.6 | VIX3M | `cdn.cboe.com` `VIX3M_History.csv` | **2009-09-18** → 2026-08-17 | **4,253** |
| 2.6 | FOMC calendar | `federalreserve.gov/monetarypolicy/fomccalendars.htm` | HTTP 200, 164 KB, 2024–2026 present | — |
| prices | SPY daily | Schwab MCP | 2009-11-30 → 2026-08-14 | **4,202** |
| prices | HYG weekly | Schwab MCP | serves from inception 2007-04-09 | — |
| prices | RSP weekly | Schwab MCP | verified at 2005 | — |
| 1.1 | Wyckoff regime, SPY/QQQ/IWM | kapman-polygon `get_wyckoff_scan(as_of=)` | floor **~2021-08-17** | — |

**Schwab serves deep history and is not a constraint.** HYG returns candles
from its 2007-04 inception. Remaining symbols (QQQ, IWM, RSP, XLY, XLP, LQD,
UUP, GLD) all predate the binding constraints and will be verified in bulk at
Phase 2 rather than by eight separate probes here.

**The Wyckoff floor is account-level, not symbol-level.** SPY, QQQ and IWM all
return the identical *"211 bars available, 250 required"* at `as_of=2022-06-17`,
and re-requesting with `days=3650` returns the same 211 bars — so the limit is
data availability, not the request window. Triangulated floor ≈ **2021-08-17**,
exactly five years before the probe date: a **rolling** 5-year window.

---

## 3. Retired sources

Per the spec's own documented failures and the operator instruction to use
issuing authorities rather than resellers.

| Retired | Reason | Replacement |
|---|---|---|
| FMP `commitmentOfTraders` | plan-gated in all 5 pilot runs; already retired by spec §8 | CFTC Socrata (direct) |
| FMP `economics-calendar` | plan-gated (`ACCESS DENIED`) | federalreserve.gov + §5 arithmetic |
| FMP `treasury-rates` | *worked*, but is a vendor intermediary to public data with per-endpoint gating that has bitten repeatedly | **Treasury.gov primary** |
| polygon `get_symbol_data(timespan="week")` | silently truncates; partial final bar with a wrong close (#30) | Schwab weekly (spec source of record) |
| polygon `iv_term_structure` | null for liquid names; 60–120 DTE bucket starves (#24) | not needed — 1.6 is VIX/VIX3M per §8 |
| Schwab `get_dealer_metrics` | approval-gated | not needed — 1.8 is annotation-only, excluded from scoring |

---

## 4. BLS is a hard block — and it does not matter

`bls.gov/schedule/news_release/{cpi,empsit}.htm` return **HTTP 403**, and
still 403 with a browser user-agent. This confirms the 2026-08-16 run's
finding as a **persistent block, not a transient failure**.

**It does not block the backtest.** Variable 2.6 is unscored; its only function
is the L2 chop-pressure flag, and under §4 the L2 flag never gates the call —
only the L1 flag does. Further, event density is **degenerate by arithmetic**
and needs no data at all:

```
FOMC 8/yr + CPI 12/yr + jobs 12/yr + quarterly OpEx 4/yr = 36 events/yr
36 × (60/365) ≈ 5.9 major events per 60-day window,  threshold is >= 3
```

Every 60-day window in history clears the threshold. **The L2 chop-pressure
flag is a constant**, exactly as the layer scores are — it has fired in 5 of 5
pilot runs and would fire in 100% of backtest windows. Record it as a second
degenerate boolean in the §7 write-up; do not spend effort sourcing CPI dates.

---

## 5. Revised window structure

VIX3M at 2009-09-18 replaces COT as the binding constraint for a
full-fidelity Tier 2.

| Tier | Window | Weeks | Variables | Bound by |
|---|---|---|---|---|
| **1** | 2022-08 → 2026-08 | ~208 | all 12 scored | polygon rolling 5-yr (1.1) |
| **2** | **2009-12 → 2026-08** | ~865 | 11 (no 1.1) | **VIX3M (1.6)** + 13-wk warmup |
| **2-ext** | 2007-07 → 2009-12 | ~130 | 10 (1.6 degraded) | HYG 2007-04 / UUP 2007-02 |

### The 2008 decision — operator ruling needed

Phase 0 showed **DOWN is the scarce class** (12.7% at 60d, 8.8% at 120d,
clustered in 2011/2015/2018/2022 — 4–5 distinct episodes). 2008 would be the
single most valuable addition to that sample.

But Tier 2-ext buys 2008 only with **1.6 scored degraded (0)** for the whole
extension — and the vol term structure inverted violently through 2008, so it
would have been the *strongest available DOWN signal*. Scoring it 0 there
systematically understates the scan's ability to call DOWN, in the one episode
where that ability matters most. **This risks producing a confidently wrong
negative result.**

Three options, not self-selected:

1. **Skip 2008.** Tier 2 = 2009-12 onward, clean, all 11 variables. Accepts a
   thin DOWN sample.
2. **Run 2-ext with 1.6 degraded**, reported separately and **never pooled**
   with Tier 2 — the same segmentation idiom spec §7 already applies to the
   pre/post-2026-08-03 split.
3. **Proxy 1.6 pre-2009** with the VIX futures term structure (VX1/VX2, CBOE
   history from 2004). Different construction from VIX/VIX3M; spec §8 pins the
   latter. Would need an explicit `[CAL]` ruling and should not be self-tuned.

Recommend **(2)**, with (3) as a follow-on only if the DOWN sample proves
decisive at Phase 5.

---

## 6. Cached and committed

```
data/treasury_par_yield.csv        4,891 rows   2007-01-02 → 2026-08
data/cftc_tff_emini_sp500.json     1,053 rows   2006-06-13 → 2026-08-11
data/cboe_vix.csv                  9,251 rows   1990-01-02 → 2026-08-14
data/cboe_vix3m.csv                4,253 rows   2009-09-18 → 2026-08-17
data/spy_daily_schwab.csv          4,202 rows   2009-11-30 → 2026-08-14
```

Minor: VIX3M carries 2026-08-17 while VIX ends 2026-08-14 — the two CBOE files
publish on slightly different lags. Align on the intersection when computing
1.6; do not forward-fill.

## 7. Next

Phase 2 (point-in-time harness) and the **Wyckoff `as_of` harvest**, which
should start regardless of other sequencing — its source window rolls forward
and 2022, the only genuine bear inside Tier 1, expires first.
