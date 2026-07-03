# Economics Validation Study — 2026-07-02

Fresh strategy-economics evidence produced ahead of the forward-log maturation
window. **Purpose of this file: be found and incorporated when the forward log
has cooked (~mid-September 2026) — see the Re-evaluation Checklist at the
bottom.** Raw outputs, scripts, and source data live in
`docs/economics_study_2026-07-02/`.

Tags follow PILOT_LESSONS convention: **[KB]** runtime contract change (HITL),
**[ENG]** engineering/code, **[CAL]** parameter calibration, **[PROC]**
process/tooling.

## Provenance

- Engine: kapman-polygon-mcp-v2 @ config `2def36946a84`, frozen fixtures.
- Universes: **battery** = 25 curated tickers (engine tuning set — friendly);
  **cohort** = 144 random liquid names (honest universe). Bars 2021-06 → 2026-06.
- Existing studies re-run unchanged: `backtest/markup_targets.py`,
  `backtest/regime_trade.py`, `backtest/option_pnl.py`.
- New studies (archived here, not committed to v2): `econ_study.py`
  (option P&L: entries × exits × IV paths, bootstrap CIs), `panel_study.py`
  (live forward-panel onset analysis).
- Live data: operator's 220-symbol forward-panel CSV export
  (`My_Watchlist_raw-records-2.csv`, archived as `forward_records.csv`),
  15 snapshot days 2026-06-14 → 2026-07-02, + fresh Polygon daily OHLC
  (cached in `panel_ohlc.json`).
- No repository was modified by the study itself; this commit is archival.

## Results

### 1. Underlying signal quality (`markup_targets.py`)

Base-target touch within 60 bars of a markup onset:

| | n | trigger | conserv. | base | stretch | med MAE | base b/4 −10% stop |
|---|---|---|---|---|---|---|---|
| Battery | 414 | 91% | 82% | 64% | 45% | 8.4% | 60% |
| Cohort | 2008 | 90% | 79% | 60% | 41% | 10.6% | 53% |
| Cohort markdown | 1829 | 90% | 75% | 46% | 26% | 14.2% | 38% |

Late-entry persistence (cohort): base-touch 60/64/69/78% at K=0/5/10/20.
The viewer's frozen `backtest_baseline.py` constants (62/73/80) REPRODUCE.
Downside is structurally weaker than upside.

### 2. Underlying trade economics (`regime_trade.py`, exit = regime flip)

| Strategy | Universe | n | win% | mean | median | avgW | avgL | PF | med hold |
|---|---|---|---|---|---|---|---|---|---|
| bull-state | battery | 534 | 46% | +2.3% | −0.5% | +12.7% | −6.6% | 1.65 | 17b |
| bull-state | cohort | 2731 | 43% | +1.6% | −1.2% | +13.9% | −7.8% | 1.36 | 17b |
| markup only | cohort | 2125 | 41% | +0.9% | −1.3% | +10.7% | −5.9% | 1.25 | 15b |
| spring+reg | cohort | 2271 | 26% | +2.2% | −5.1% | +30.1% | −7.7% | 1.39 | 21b |

**[CAL]** The forward-log spec's "PF up to 1.88" does NOT reproduce on the
current engine (older config `9985ee457ecb`; never pinned). Current honest
number: 1.36 cohort / 1.65 battery.

### 3. Option-space economics (`option_pnl.py` + new `econ_study.py`)

ATM calls, DTE 90, premium-normalized returns, flat IV=HV unless noted:

| Entry | Exit | IV path | Universe | n | win% | mean | median | PF | 95% CI |
|---|---|---|---|---|---|---|---|---|---|
| markup | target/stop | flat | battery | 413 | 49% | +0% | −2% | 1.00 | [−7,+8] |
| markup | target/stop | flat | cohort | 2008 | 45% | −4% | −15% | 0.90 | [−7,+0] |
| markup | flip | flat | battery | 419 | 37% | +16% | −19% | 1.53 | [+4,+27] |
| markup | flip | flat | cohort | 2043 | 34% | +1% | −22% | 1.04 | [−3,+6] |
| spring | flip | flat | battery | 376 | 33% | +23% | −42% | 1.58 | [+8,+39] |
| **spring** | **flip** | **flat** | **cohort** | **2211** | **27%** | **+14%** | **−46%** | **1.33** | **[+7,+21]** |

IV sensitivity on the best trade (spring+flip, cohort, DTE 90):

| IV scenario | mean | PF | 95% CI |
|---|---|---|---|
| flat (IV = HV) | +14% | 1.33 | [+7,+21] |
| 15% IV drift-down while held | +7% | 1.14 | [+0,+14] |
| entry premium at 1.2×HV | −4% | 0.92 | [−9,+2] |

Rich entry (1.2×HV ≈ the IV/HV 1.2 spread-mandate line) turns EVERY
combination negative (markup+flip 0.64, markup+target 0.69, cohort).
DTE 180 is worse under crush (markup+flip 0.70).

Skew: 27% win / −46% median ⇒ implied average winner ≈ +190% of premium.
The expectancy lives in the tail beyond a 100–150% scale-out level.

### 4. Live forward-panel measures (99 onsets; matches UI 51/39/9)

- 99 onsets (37 up / 62 down), 71 symbols, 33 flip-closed.
- Forward windows: **median 6 bars, max 12** (vs 60-bar predictions).
- Up onsets resolved (hit/stop race): 18/34; base-hit 8/18 = 44% vs
  engine-predicted 70%. Hits resolve at median bar 0; stops at median bar 4.
- Stopped-then-later-touched-base bias cases: 0 so far (will accrue).
- Race by context: accumulation 4/6, reaccumulation 4/6, **distribution 0/6**.
- Conviction: high ≥66 → 7/11 vs med 33–66 → 1/7 (opposite of the backtest's
  "conviction does not rank edge"; tiny n — keep measuring, no action).
- Flip-exit returns (closed trades only): up −2.5% (n=15), down −5.4% (n=17).

**Interpretation guard:** the dashboard's red calibration gaps are dominated by
window immaturity (6-bar windows vs 60-bar predictions), and the negative live
flip-exit returns are closed-trade censoring (fast failures close first;
66/99 onsets still open hold the potential winners). **The live log cannot
support τ, exit, or sizing tuning yet.**

## Plain-language summary

The engine is good at pointing at trends (60% of finish lines get touched on
the honest universe; 78% if the trend survives 20 days). Trading the stock
itself on those signals makes modest money (PF 1.36). But buying CALLS on
fresh trend-starts with target/stop exits LOSES after theta (PF 0.90). The
only call strategy that survives the honest universe is: **buy the phase-C
spring (the panic-dip fake-out at the bottom of a base), pay fair IV, and hold
until the regime flips** — +14% mean per trade, 27% win rate, winners ~+190%.
Overpaying IV by 20% deletes the whole edge, and capping winners at +100–150%
would amputate the tail that carries all the profit. Expect long losing
streaks; sizing must survive them.

## Recommendations (status at time of writing: pending operator approval)

1. **[KB]** Elevate spring/phase-C entries over markup-chase in Pass-1
   priority (this also reframes the τ-paradox: the flagged fresh-spring cohort
   is the economically good one). HITL draft.
2. **[KB]** Entry-IV ceiling: naked long calls at IV/HV ≥ 1.2 stay refused
   (now empirically proven, not just prudent); consider a caution band below
   1.2 given crush sensitivity. HITL draft.
3. **[KB]** Re-decide the playbook's "scale out at 100–150%" rule vs flip-style
   exits — the backtest says the tail carries the expectancy. HITL decision.
4. **[KB]** Harden the counter-structure refusal (live 0/6 matches backtest).
5. **[ENG]** Pin the economics: commit `econ_study.py` + these results into
   kapman-polygon-mcp-v2's backtest ledger (issue → run → commit), so the
   trading-economics layer gets the same rigor as the engine battery.
6. **[ENG]** Viewer changes (all deferred until re-evaluation): spring-event
   onsets in the forward log (highest value — the live loop cannot currently
   see the only CI-positive entry class); window-maturity caveat on the
   calibration tab; late-entry survival-conditioning parity fix
   (forward_eval.py enters at onset+K unconditionally vs markup_targets.py:88
   requiring regime survival) + censoring annotation (`mature` = base-hit OR
   full window biases young readings high); dealer scorecard dimension;
   full-field records export (pt_down tiers, conservative/stretch, dealer,
   ADX/HV missing from current CSV export).
7. **[ENG]** Build a portfolio-level simulator (concurrent positions, sizing
   bands, theta bleed, drawdown paths). With a 27%-win skew profile this is
   the most important unbuilt component in the ecosystem.
8. **[PROC]** Doc reconciliation after numbers are pinned: wyckoff_engine.md
   mixes battery epochs (77.1%/20-cut table vs 81.8%/100-check headline);
   forward-log-spec.md quotes the stale PF 1.88; backtest_baseline.py
   constants confirmed OK but still flagged APPROXIMATE.

## Re-evaluation checklist (run when the forward log has cooked)

**Trigger: ~2026-09-15**, or earlier if ≥20 bullish-context onsets have
COMPLETE 60-bar windows (first onsets are 2026-06-15; 60 trading bars ≈
2026-09-10).

1. Export the full-field forward-log records (needs the richer export — see
   recommendation 6; at minimum include pt_down tiers, all pt_*_prob, dealer
   fields). Re-run `panel_study.py` (archived here) against it.
2. Compare live realized vs this study's backtest numbers per §1–§3 above:
   base-touch by context/direction, flip-exit returns BY DIRECTION on closed
   trades with mature windows, stopped-then-touched count (quantifies the
   resolved-subsample bias), conviction buckets (live said high-conviction
   ranks, backtest said it doesn't — adjudicate with real N).
3. Only then decide: τ thresholds, exit convention (target vs flip vs hybrid),
   scale-out rule, spring-onset viewer work, engine pt_*_prob context
   conditioning (the counter-structure over-promise).
4. Re-check the two live cells this study flagged: distribution-context
   up-onsets (0/6 at archive time) and the markdown side (weaker everywhere).
5. Apply the N≥20 readability discipline per cell throughout — the same gates
   the viewer UI uses.

## Caveats

Black-Scholes with IV = trailing HV (no smile, no earnings vol), no bid/ask or
slippage, perfect fills at touched levels, fixed ATM strikes, engine tuned
in-sample on the battery, single 2021–26 window, cohort survivorship tilt
(names selected liquid today), live sample 3 weeks old. Backtest numbers are
friendly-case ceilings / honest first estimates. The forward log is the
out-of-sample arbiter.

## File manifest (`docs/economics_study_2026-07-02/`)

- `econ_study.py`, `panel_study.py` — the new studies (runnable from the v2
  repo root with its `.venv`).
- `run_markup_{battery,cohort}.txt`, `run_regime_{battery,cohort}.txt`,
  `run_option_{battery,cohort}.txt`, `run_econ_{battery,cohort}.txt` — raw
  outputs of all eight runs.
- `forward_records.csv` — the operator's live panel export (source data).
- `live_onsets.csv` — per-onset reconstruction (99 onsets) with race status,
  MAE/MFE, flip returns.
- `panel_ohlc.json` — cached Polygon OHLC used for the live measures.
