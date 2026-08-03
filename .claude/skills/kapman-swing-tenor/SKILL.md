---
name: kapman-swing-tenor
description: |
  Run the weekly KapMan Swing Tenor Scan — a standalone UP/DOWN/CHOP market-tenor
  call for the next 60-120 days (the SWING_DTE_BAND horizon), per the pilot spec
  in kapman-kb/docs/SWING_TENOR_SCAN_PILOT_v0.1.md.

  USE THIS SKILL when the user asks to: "run the tenor scan", "swing tenor",
  "market tenor", "weekly tenor", "what's the market tenor", "up/down/chop call",
  or to back-fill/score a past tenor call. This is NOT the daily market scan and
  NOT Pass 1 screening (use kapman-screen for that) — its output is standalone
  context, never consumed by Pass 1/Pass 2.

  Always use live MCP data (Schwab, kapman-polygon, FMP, Finnhub, Bigdata.com);
  never use training data for prices or vol values.
---

# Swing Tenor Scan

**Source of truth:** `kapman-kb/docs/SWING_TENOR_SCAN_PILOT_v0.1.md`. Read it
first — it owns the variables, composition rule, thresholds ([CAL] items), and
outcome-scoring rule. This skill is the run procedure; it never overrides the
spec. Forward log lives in `kapman-journal/log/tenor/` (record grammar in that
directory's README.md). Real calls/outcomes go ONLY in kapman-journal, never
in kapman-kb.

## Run procedure

### Step 0 — Housekeeping
1. Read the spec and the journal `log/tenor/README.md`.
2. Check the most recent `log/tenor/<YYYY-MM>/tenor_*.md` entries:
   - Back-fill any `Outcome` section whose +60d/+120d window has closed, using
     the deterministic rule in spec §6 (SPY total return + max drawdown from
     the call-date close — fetch SPY daily history for the window).
   - Note the standing call and its invalidation conditions.
3. Determine trigger: `scheduled` (weekly) or `invalidation` (a standing
   invalidation condition was hit — say which).

### Step 1 — Data pulls (all live; degraded = named + scored 0, never assumed favorable)
Layer 1 (market-internal): Schwab weekly history SPY/QQQ/IWM (~3y) + RSP,
XLY, XLP (~1y) — **Schwab is the source of record for every weekly bar**;
Schwab quotes `$VIX`, `$VIX3M` (NOT `$VIX.X`); kapman-polygon
`get_wyckoff_scan` on SPY/QQQ/IWM; **1.7 and 1.8 both come from kapman-polygon
`get_options_metrics(symbol="SPY", include=["dealer","price"], dte_min=60,
dte_max=120)`** — one call, no Schwab dependency. Do NOT read the far-dated
dealer block through `get_wyckoff_scan` (hardcoded 0–60 DTE), and do NOT
fall back to the 0–60 block for 1.8 — a degraded 1.8 is a bug in the run,
not an environment limit (spec §8).

Layer 2 (cross-asset/macro): Schwab weekly history HYG, LQD, UUP, CPER, GLD;
**2.2 via FMP `economics` `endpoint: treasury-rates` with explicit
`from_date`/`to_date` — pull both ends of the 13-wk window and difference the
10y and 2s10s. This endpoint is open; the plan gate is per-endpoint, so a
denied `economics-calendar` does NOT degrade 2.2.** FMP
`commitmentOfTraders` ES is genuinely plan-gated — mark 2.5 degraded and
build the event map from public FOMC/CPI/OpEx/earnings-season schedules.

Before writing "degraded" for any variable, vary the parameter and retry, and
check whether a sibling endpoint or producer serves it. Three of the pilot's
first four corrections came from assuming a gap instead of testing one.

Layer 3 (sentiment, contrarian check only): Finnhub `get_market_news` +
Bigdata.com market tearsheet/search for the consensus narrative.

### Step 2 — Compute (script it; no mental arithmetic)
Per spec §3: 40-wk MA level + 10-wk slope, distance from 52-wk high, 13-wk
ratio slopes (RSP/SPY, XLY/XLP, HYG/LQD, CPER/GLD), UUP 13-wk, VIX3M/VIX,
layer scores (−2..+2), chop-pressure flags.

### Step 3 — Compose the call (spec §4)
S = 2×L1 + L2; boundary/conflict/chop-flag cases resolve to CHOP; confidence
per the spec's rule (degraded layers cap it); name 2–4 observable invalidation
conditions.

**The L1 chop-pressure flag is the literal four-item test in spec §3** — 1.1
`ranging_undefined`, 1.2 flat MA slope, 1.4 negative breadth slope, 1.6
contango < 5% — and needs **≥2** to fire. Nothing else sets it. A flat weekly
trend or a cross-index regime-family split is real chop evidence but drives
the §4 **structural confidence brake** (caps at medium), not the flag. Record
which conditions fired and which did not; the flag decides UP/DOWN vs CHOP at
S = ±3, so show the work.

### Step 4 — Report + log
1. Render the report (spec §5 section order), labeled *"Standalone context —
   not consumed by Pass 1 / Pass 2."*
2. Write the journal entry `log/tenor/<YYYY-MM>/tenor_YYYY-MM-DD.md` per the
   README grammar (frontmatter + sections + PENDING Outcome). One file per
   run, append-only — never edit a prior run's call sections.
3. Commit/push kapman-journal per that repo's delivery rules.

## Hard rules
- Conservative defaults: conflicts → CHOP; degraded inputs are named, never
  silently favorable.
- Deterministic outcome scoring only (spec §6) — no after-the-fact judgment.
- Tenor calls never gate, veto, tilt, or size Pass 1/Pass 2 work.
- Threshold changes ([CAL] items) are operator decisions — propose, don't
  self-tune; the pilot re-evaluation gate is spec §7.
