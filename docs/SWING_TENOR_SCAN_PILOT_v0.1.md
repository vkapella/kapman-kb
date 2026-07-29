# Swing Tenor Scan — Pilot Spec v0.1 (2026-07-28)

**Status:** Pilot — runnable procedure, NOT KB runtime content. Lives in `docs/`
deliberately: nothing here is uploaded to LLM project knowledge, nothing here is
consumed by Pass 1 / Pass 2, and no `llm_runtime/` file references this spec.
**Owner:** vkapella. **Issue:** #95.
**Re-evaluation:** after 8–12 logged weekly runs (~October 2026), alongside the
September 2026 re-evaluation items already pinned in `PASS1_SCREENING` and the
2026-07-02 economics study.

Tags follow PILOT_LESSONS convention: **[CAL]** marks every provisional
threshold that calibrates during the pilot.

---

## 1. Purpose and boundary

The KB's existing market-context layer answers *"is the tape safe today?"* —
the SPY hostile-macro composite is a days-scale gamma-positioning read, Wyckoff
is daily structure (weekly only as an agree/conflict flag), and IV/HV is a
~30-DTE snapshot. Nothing forecasts the likely market **tenor — UP / DOWN /
CHOP — over the 60–120 day `SWING_DTE_BAND`** a swing position actually lives
through.

This scan fills that gap as a **standalone weekly report**:

- It does **not** gate, veto, tilt, or size anything in Pass 1 / Pass 2.
- Its calls are logged privately in kapman-journal (`log/tenor/`) and scored
  deterministically at +60d and +120d.
- KB codification (a future `MARKET_TENOR` file, any Pass-1 wiring) happens
  **only if** the forward record beats the naive always-UP baseline at the
  re-evaluation. Until then this is context for operator judgment only.

Every report carries the label: *"Standalone context — not consumed by
Pass 1 / Pass 2."*

## 2. Cadence

- **Weekly**, after Friday close / before Monday open (one run per week).
- **Early re-run trigger:** an invalidation condition from the standing call is
  hit intra-week (e.g., weekly-equivalent close through the 40-week MA, VIX
  term-structure inversion). The re-run replaces the standing call and is
  logged as a new entry with `trigger: invalidation` instead of
  `trigger: scheduled`.
- **Correction trigger:** a variable that ran **degraded** later proves to have
  been retrievable at run time (a source that was reachable but wasn't called,
  or a producer fix landing). The corrected run is logged as a **new**
  superseding entry with `trigger: correction` and a `supersedes:` lineage
  field; the superseded entry is **never edited** — the append-only rule is
  what makes the forward record trustworthy, and a correction that rewrites
  history is indistinguishable from massaging a call. Only the superseding
  entry carries the outcome back-fill, so a corrected week contributes exactly
  one record to the §7 evaluation, not two.

## 3. Signal layers and variables

Three layers. The two quantitative layers each produce a **directional score
in −2..+2** and a **chop-pressure flag**; the sentiment layer produces no
score — it is a contrarian check only. Any variable whose source fails to
resolve is recorded as **degraded** and scored 0 (never silently favorable —
same idiom as the KB's degraded-input discipline).

### Layer 1 — Market-internal (primary; weight ×2)

| # | Variable | Read | Source |
|---|---|---|---|
| 1.1 | Weekly-bar Wyckoff regime, SPY/QQQ/IWM | Propose-style regime read over ~150 weekly bars: markup / accumulation-family → bullish; markdown / distribution-family → bearish; ranging → chop pressure | Schwab `get_price_history_every_week`; kapman-polygon `get_wyckoff_scan` as daily cross-check |
| 1.2 | 40-week MA position + slope (SPY) | Close above rising 40-wk MA → bullish; below falling → bearish; flat slope (±0.5%/10wk **[CAL]**) → chop pressure | computed from 1.1 history |
| 1.3 | Distance from 52-week high (SPY) | Within 3% **[CAL]** → bullish context; >10% off **[CAL]** → bearish context | computed from 1.1 history |
| 1.4 | Breadth: RSP/SPY ratio trend | Equal-weight outperforming (13-wk ratio slope up) → bullish confirmation; deteriorating while SPY holds high → divergence, chop/top pressure | Schwab weekly history RSP, SPY |
| 1.5 | Offensive vs defensive: XLY/XLP ratio trend | 13-wk slope up → bullish; down → bearish | Schwab weekly history XLY, XLP |
| 1.6 | Vol term structure: VIX vs VIX3M | Contango (VIX3M > VIX by >5% **[CAL]**) → trend-supportive; flat (<5%) → chop pressure; backwardation → bearish + chop pressure | Schwab quotes `$VIX`, `$VIX3M` |
| 1.7 | Realized-vol regime: HV20 vs HV60 (SPY proxy) | `hv20_hv60_ratio` < 1 with both falling → calming tape, trend-supportive; ratio > 1 and rising → destabilizing. Boundary (~1.0) → no contribution | kapman-polygon `get_options_metrics(include=["price"])` → `realized_vol.{hv20, hv60, hv20_hv60_ratio}` |
| 1.8 | Longer-dated dealer structure (SPY) | GEX/wall map on expiries 60–120 DTE: large put-wall shelf below spot → downside support context; heavy call walls just overhead → capped-upside chop context. Context only — never a directional score by itself | **kapman-polygon `get_options_metrics(include=["dealer"], dte_min=60, dte_max=120)`** — the primary source; Schwab `get_dealer_metrics` at the same window is an optional cross-check, not a dependency. Plus the quarterly OpEx map |

Layer score **[CAL]**: majority read of 1.1–1.7 mapped to −2..+2; 1.8 is
annotation. Chop-pressure flag set when ≥2 of {1.1 ranging, 1.2 flat, 1.4
divergence, 1.6 flat/inverted} fire.

### Layer 2 — Cross-asset + macro (confirming; weight ×1)

| # | Variable | Read | Source |
|---|---|---|---|
| 2.1 | Credit: HYG/LQD ratio trend | 13-wk slope up (spreads tightening) → bullish; rolling over → bearish lead | Schwab weekly history HYG, LQD |
| 2.2 | Yield curve: 2s10s level + 13-wk change | Steepening from inversion → regime-dependent; rapid bull-steepening (recession signature) → bearish | FMP `economics` treasury rates |
| 2.3 | Dollar: UUP 13-wk trend | Sharp sustained dollar strength → equity headwind; falling/stable → supportive | Schwab weekly history UUP |
| 2.4 | Copper/gold ratio 13-wk trend | Up → growth-bullish; down → defensive/bearish | FMP `commodity` (HG, GC) or CPER/GLD weekly history |
| 2.5 | COT: index-futures net positioning trend | Extremes read contrarian; trend of large-spec positioning read as confirmation | FMP `commitmentOfTraders` (ES/SPX) |
| 2.6 | Known-event map, next 120 days | FOMC, CPI, jobs, quarterly OpEx, earnings-season windows. Not scored — defines chop-likely windows and annotates the call | FMP `economics` calendar, Finnhub `get_earnings_calendar`, published FOMC schedule |

Layer score **[CAL]**: majority read of 2.1–2.5 mapped to −2..+2. Chop-pressure
flag set when the event map is dense in the first 60 days (≥3 major
macro events **[CAL]**) or COT sits at a contrarian extreme.

### Layer 3 — News/sentiment (contrarian check only; no score)

| # | Variable | Read | Source |
|---|---|---|---|
| 3.1 | Market-narrative summary | What is the consensus story for the next quarter? Recorded verbatim-brief in the report | Bigdata.com `bigdata_market_tearsheet` / `bigdata_search`; Finnhub `get_market_news` |
| 3.2 | Sentiment extreme check | Uniform euphoria at highs, or uniform despair at lows, **caps confidence at medium** for the aligned directional call (contrarian brake). Mixed/neutral sentiment → no effect | same |

Layer 3 can never flip a call's direction and never contributes to the score —
it only degrades confidence when the crowd is fully aligned with the call.

## 4. Composition rule **[CAL]**

Weighted sum `S = 2×L1 + 1×L2` (range −6..+6):

| Condition | Tenor call |
|---|---|
| S ≥ +3 and no chop-pressure flag from L1 | **UP** |
| S ≤ −3 and no chop-pressure flag from L1 | **DOWN** |
| L1 and L2 scores have opposite signs | **CHOP** (conflict) |
| Any other case (−3 < S < +3, or chop-pressure flag set) | **CHOP** |

Boundary and conflict cases resolve to CHOP — the conservative read, matching
the KB's conservative-default idiom.

**Confidence:** high = |S| ≥ 5 with both layers agreeing and no chop flags;
medium = call made with one dissenting variable group or a sentiment brake
(3.2); low = call made with any layer degraded. A call with ≥2 degraded
variables in L1 is reported as CHOP / low regardless of S.

**Invalidation conditions:** every call names 2–4 observable conditions that
flip or void it (e.g., "weekly close below the 40-wk MA", "VIX term structure
inverts", "HYG/LQD breaks the 26-wk low"). These drive the early re-run
trigger (§2) and are scored at outcome time (§6).

## 5. Report format

One markdown report per run (rendered HTML optional), sections in order:

1. **Tenor call** — UP / DOWN / CHOP, confidence, window (today → +120d),
   and the standing label *"Standalone context — not consumed by Pass 1 / Pass 2."*
2. **Per-layer evidence table** — every variable, its reading, its
   contribution, degraded flags.
3. **Invalidation conditions** — the named list.
4. **Event map** — dated FOMC/CPI/jobs/OpEx/earnings-season windows inside +120d.
5. **Data-quality notes** — every degraded or unresolvable source named.

## 6. Forward log and outcome scoring (deterministic)

Calls are logged in **kapman-journal** `log/tenor/<YYYY-MM>/tenor_YYYY-MM-DD.md`
(record grammar in that repo's `log/tenor/README.md`). Real calls and outcomes
never live in kapman-kb (public-instructions / private-data split).

**Outcome classification is fixed here, up front — no after-the-fact judgment.**
At +60d and +120d, classify the realized SPY window from the call date:

| Realized window (SPY total return R, max drawdown D from call-date close) | Class |
|---|---|
| R ≥ +3% (60d) / +5% (120d) and D < 5% **[CAL]** | UP |
| R ≤ −3% (60d) / −5% (120d) and max run-up < 5% **[CAL]** | DOWN |
| Anything else | CHOP |

Invalidation hits are logged separately with their date: a call invalidated
before window close is scored as **invalidated** (its named condition worked),
distinct from a call that simply drifted wrong.

## 7. Pilot success criteria (re-evaluation gate)

After 8–12 logged weeks, the pilot is judged on:

1. **Hit rate vs naive baseline** — calls must beat "always UP" (the equity
   drift baseline) on the same windows.
2. **Confidence calibration** — high-confidence calls must hit more often than
   medium/low. If they don't, the confidence rule is noise.
3. **CHOP usefulness** — CHOP calls must correspond to realized rangebound
   windows (and to windows where 60–120 DTE directional swings would have
   chopped out), not just be the residual bucket.
4. **Invalidation quality** — invalidation conditions should fire before the
   adverse outcome in the majority of wrong-direction calls.

Only a record that clears (1) and (2) earns KB codification (a `MARKET_TENOR`
runtime file and any Pass-1 wiring — both HITL, drafted turn-by-turn per
`AGENTS.md`). Anything less: recalibrate **[CAL]** items and extend the pilot,
or kill it and record the lesson in PILOT_LESSONS.

## 8. Tool-surface notes (first-run verified)

The "kapman-mcp lesson" applies: this spec names only fields the producers
actually emit, verified in the 2026-07-28 first run. Corrections from that run:

- **VIX symbology (1.6):** Schwab quotes resolve `$VIX` / `$VIX3M`; the
  `$VIX.X` / `$VIX3M.X` forms are rejected as invalid symbols.
- **Polygon `iv_term_structure` is unavailable for liquid names — do not
  depend on it.** The producer returned null for SPY ("insufficient contracts
  in short (15–45) or long (60–120 DTE) buckets"). Root cause confirmed in
  source (kapman-polygon-mcp-v2#24): the chain fetch paginates in
  expiration-ascending order and hard-breaks at a 4000-contract cap, so a
  dense front chain starves the 60–120 DTE bucket every time —
  `term_structure_long_contracts: 0`. It fails on precisely the liquid
  underlyings this scan uses. **VIX vs VIX3M is the operative term-structure
  read**; treat `iv_term_structure` as a bonus that will be absent until #24
  lands.
- **1.7 (HV20 vs HV60) — RESOLVED 2026-07-28.** The first run scored 1.7
  degraded because the producer emitted only a single HV20-class
  `historical_volatility`. Fixed upstream in kapman-polygon-mcp-v2#26: the
  price block now carries `realized_vol` =
  `{hv10, hv20, hv60, hv120, hv20_hv60_ratio, insufficient_history}`. **1.7 is
  now a fully scored variable**; the ATM-IV ÷ HV20 substitute is retired (it
  measured implied-vs-realized premium richness, a different signal). Two
  operating notes: `hv20` is byte-identical to the scalar
  `historical_volatility`, so either may be cited; and `hv120` returns null at
  the default `days=100` (~69 trading bars) with `insufficient_history`
  naming it — request a wider `days` if the 120-day window is wanted, and
  never read a shorter window as a substitute.
- **1.8 (60–120 DTE dealer map) — CORRECTED 2026-07-28.** The first run scored
  1.8 degraded after Schwab `get_dealer_metrics` came back approval-gated, and
  fell back to the Wyckoff scan's embedded 0–60 DTE block. **That was a
  procedure error, not a capability gap:** kapman-polygon's
  `get_options_metrics` already accepts `dte_min` / `dte_max`, and calling it
  at 60–120 returns a clean far-dated read — verified live on SPY the same
  session: 1630 source contracts, **no truncation** (the date-bounded fetch
  starts at today+60 and so skips the near-dated mass that truncates the
  0–120 window). 1.8 is therefore a **fully available variable with no Schwab
  dependency**; treat a degraded 1.8 as a bug in the run, not an environment
  limitation. Bigdata.com tearsheet and FMP `economics` /
  `commitmentOfTraders` remain genuinely approval-gated (2.2, 2.5 degraded;
  event map from public schedules).
- **Do not read the far-dated dealer block through `get_wyckoff_scan`** — its
  embedded options block is hardcoded to 0–60 DTE and cannot be
  re-parameterized (tracked: kapman-polygon-mcp-v2#27). Call
  `get_options_metrics` separately for the swing window.
- **Near-dated `gamma_flip` is not trustworthy without a sanity check.** The
  0–60 DTE read returned a flip of 497.25 against spot 739.09 (33% below) with
  `confidence: "high"` and no rejection reason, because the producer has no
  distance-from-spot guard (tracked: kapman-polygon-mcp-v2#25). Sanity-check
  any flip against spot before using it, and prefer the far-dated read, which
  degrades honestly (`no_zero_cross_in_window` → `position_vs_flip: unknown`).
- **Weekly Wyckoff (1.1) source note:** the kapman-polygon `get_wyckoff_scan`
  runs on daily bars but emits a `weekly_context` block (trend / regime_hint /
  close_vs_30w) plus range + regime + phase — sufficient for the 1.1 read
  alongside the Schwab weekly candles; no separate weekly-bar engine needed.
