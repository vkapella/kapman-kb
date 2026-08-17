# Phase 2 — point-in-time harness

**Run:** 2026-08-17 · **Status:** COMPLETE · **Code:** `phase2_harness.py`

Builds the as-of data layer for the backtest and proves it cannot see the
future. Operator ruling applied: **Tier 2-ext runs segmented, never pooled.**

---

## 1. A real data bug, found by building the harness

The concatenated `treasury_par_yield.csv` produced by Phase 1 was **silently
wrong for every row after 2017**, and would have corrupted variable 2.2 across
the entire backtest.

**Cause.** Treasury has added tenors over time. Fetching per-year and appending
with a single retained header misaligns every later row:

| Years | Columns |
|---|---|
| 2006–2017 | 12 |
| 2018–2021 | 13 (+2 Mo) |
| 2022–2024 | 14 (+4 Mo) |
| 2025–2026 | 15 (+1.5 Mo) |

Reading the fixed position for `"10 Yr"` on a 2026 row returns the **3-year**
yield. Measured on 2026-08-14: **4.24 against a true 4.68 — a 44bp error**, and
2s10s wrong by a similar margin.

**How it surfaced.** Only by validating the harness against a logged live run.
Seven variables reproduced to the decimal; 2.2 did not. Nothing in the file
itself looked malformed — every row parsed, no exception, no missing values.

**Fix.** 2.2 now loads **FRED `DGS2` / `DGS10`** (Federal Reserve) — clean
two-column series with no alignment surface. Treasury.gov is retained per-year
under `data/treasury_by_year/` and parsed with each file's *own* header as an
independent cross-check.

> **Lesson for spec §8, in the kapman-mcp idiom:** *a wide government CSV whose
> column set changes over time is a silent-corruption source when years are
> concatenated. Parse each vintage against its own header, or use a
> single-series feed. The failure is invisible — no error, no gap, no null.*

---

## 2. Cross-validation

| Check | Result |
|---|---|
| FRED vs Treasury.gov, 2y and 10y | **5,159 dates compared, 0 disagreements > 2bp** |
| Lookahead assertions across sampled call dates | **0 violations** |
| COT report age at call time | min 3d, **median 3d**, max 10d |

The COT distribution confirms the publication model: CFTC posts Friday ~15:30
ET for the prior Tuesday, so a 3-day age is the norm; the 10-day tail is
holiday-delayed publication, correctly handled rather than smoothed.

---

## 3. Validated against the live 2026-08-16 run

Harness recomputation vs the logged entry, at call date 2026-08-14:

| Variable | Harness | Logged | |
|---|---|---|---|
| 1.4 RSP/SPY 13wk | +5.23% | +5.23% | ✅ exact |
| 1.5 XLY/XLP 13wk | −0.28% | −0.28% | ✅ exact |
| 1.6 VIX3M/VIX | +29.5% | +29.5% | ✅ exact |
| 2.1 HYG/LQD 13wk | +1.96% | +1.96% | ✅ exact |
| 2.2 10y / 2s10s | 4.68 / +51bp | 4.68 / +51bp | ✅ exact |
| 2.3 UUP 13wk | +1.22% | +1.22% | ✅ exact |
| 2.4 CPER/GLD 13wk | +9.03% | +9.03% | ✅ exact |
| 2.5 COT net | −280,446 | −280,446 | ✅ exact |
| SPY close | 776.34 | 776.34 | ✅ exact |
| 1.7 hv20/hv60 | 0.9612 | 0.9447 | ⚠️ see below |
| 2.2 13wk Δ10y | +9bp | +7bp | ⚠️ see below |

### Known reconstruction differences

**1.7 realized vol (0.9612 vs 0.9447, ~1.7% relative).** The live runs read
kapman-polygon's `realized_vol` block; the harness computes hv20/hv60 from
Schwab daily closes with sample variance and √252 annualization. The producer's
convention (population vs sample variance, bar count, inclusion of the current
bar) is not documented. **This matters because 1.7's rule is a comparison to
1.0** — the 08-09 run scored it "boundary (~1.0) → no contribution" at 0.9922,
so a 1.7% shift can flip that read. Backtest 1.7 results are therefore not
strictly comparable to live 1.7 scoring. Options: pin the producer's formula,
or run 1.7 both ways and report the disagreement rate. **Needs a ruling.**

**2.2 13-week delta (+9bp vs +7bp).** The harness anchors "13 weeks ago" at
`t − 91 days`; the live run used a weekly-bar anchor. 2bp, immaterial against a
±40bp band, but recorded so the convention is explicit.

---

## 4. Segment structure — boundaries set by data, not round dates

Per the operator ruling, each segment is scored and reported **separately and
never pooled**, mirroring the pre/post-2026-08-03 idiom in spec §7.

| Segment | Window | Call dates | Live variables | Dark |
|---|---|---|---|---|
| **S1** full-fidelity | 2022-08-01 → 2026-08-14 | **211** | all 12 (incl. 1.1 Wyckoff) | — |
| **S2** core | 2012-02-01 → 2026-08-14 | **759** | 11 | 1.1 |
| **S3** extended | 2009-09-18 → 2012-02-01 | **124** | 10 | 1.1, 2.4 |
| **S4** crisis | 2007-07-01 → 2009-09-18 | **116** | 9 | 1.1, 2.4, 1.6 |

Boundaries derive from inception dates: **VIX3M 2009-09-18** (1.6) and **CPER
2011-11-15 + 13-week warmup** (2.4).

> **S1 deliberately overlaps S2.** It is the Wyckoff-inclusive overlay used to
> measure 1.1's marginal contribution by scoring the same 211 weeks with and
> without it. Pooling S1 with S2 would double-count those weeks.

### Coverage measured, not assumed

100% on every live variable in every segment, except the three dark cells and
2.1 in S4 (99% — HYG's 2007-04-11 inception plus 13-week warmup clips the first
fortnight).

### A note on S4's honesty

S4 buys 2008 with **three of twelve variables dark**, including 1.6, whose
inversion was the crisis's loudest signal. Spec §4's *"≥2 degraded in L1 →
CHOP/low regardless of S"* does **not** trigger (only 1.1 and 1.6 are L1, and
1.1 is structurally absent rather than degraded) — but S4 remains the weakest
evidence in the study and must be labelled as such wherever it is cited. It
exists to see whether the *surviving* variables detect 2008, not to score the
scan as specified.

---

## 5. Copper — 2.4's source problem

Spec §3 names *"FMP `commodity` (HG, GC) or CPER/GLD"*. FMP is retired, and
**Schwab has no continuous copper series**: `/HG` resolves to a single
front-month contract (`/HGU26`), so a continuous history would require stitching
per-contract data with a roll convention — a modelling decision, not a fetch.

`JJC` (iPath copper ETN) is delisted and returns `invalidSymbols`.

**CPER (inception 2011-11-15) is therefore the binding constraint** on a
fully-live Tier 2, and is why S2 begins 2012-02 rather than 2009-12.

**COPX was fetched (2010-04-20) and is deliberately NOT used.** It holds copper
*miner equities*, so inserting it into an equity-tenor model imports equity beta
into a variable meant to read industrial demand — circular by construction. It
is cached only so the decision is reproducible; do not substitute it without an
explicit ruling.

---

## 6. Cached inputs

```
spy/qqq/iwm/rsp/xly/xlp/hyg/lqd/uup/gld/cper/copx_daily_schwab.csv
fred_DGS2.csv, fred_DGS10.csv          5,379 rows each, 2006-01-03 -> 2026-08-14
treasury_by_year/{2006..2026}.csv      cross-check, per-year headers
cboe_vix.csv, cboe_vix3m.csv
cftc_tff_emini_sp500.json
```

`treasury_par_yield.csv` (the concatenated file) has been **deleted** — it is
the corrupted artifact described in §1 and must not be resurrected.

---

## 7. Next

**Phase 3** — variable scoring (live rules + shadow variants A1/A2/A3/B) over
S1–S4, and the **Wyckoff `as_of` harvest** for S1's 211 call dates × 3 symbols
≈ 633 cached scans. The harvest remains the only input that expires: polygon's
window is rolling, and 2022 — S1's sole bear episode — is first to go.

Open ruling from §3: how to reconcile 1.7 against the producer's undocumented
realized-vol convention.
