---
system: KapMan
doc_type: reference
kb_version: 4.1.0-alpha
file_last_updated: 2026-08-17
status: draft
tier: —
---

# VOLATILITY MCP REFERENCE

## Purpose

This file documents the **live** volatility tool-surface mechanics behind the
fields `llm_runtime/VOLATILITY_v4.0.md` consumes: formulas, windows, filters,
caps, status vocabularies and endpoint references. The runtime VOLATILITY file
owns source-authority behavior and regime interpretation; this file owns the
mechanics.

**Read the two halves of this file differently.** The Contents section describes
what the producers do **today** — every row verified against producer source or
a live call, dated below. The Appendix (Verbatim extracted formulas) is a
historical record of what the **v2.3 anchors said**, kept verbatim for
back-compat with legend citations and past journals; it is not a statement about
any current surface, and the two disagree wherever v2.3 has been superseded.
When they conflict, Contents governs for engineering questions and the Appendix
governs for "what did `VOLATILITY_0NN` originally say".

Contents last verified **2026-08-17** (kb#114) against kapman-polygon-mcp-v2
(source plus live `get_options_metrics` calls) and kapman-polygon-viewer
(`backend/app/iv_history.py`).

## Contents

### Producers and division of labour

There are **two** producers, not one. Conflating them is what stranded the IV
tier in kb#112.

| Surface | Owns | Delivery |
|---|---|---|
| kapman-polygon-mcp-v2 `get_options_metrics` / `get_batch_options_metrics` | `atm_iv`, `average_iv`, `iv_skew_25delta`, `iv_term_structure`, `put_call_ratio`, `oi_ratio`, contract counts, chain-scope stamps | MCP tool call, either pass |
| kapman-polygon-viewer `backend/app/iv_history.py` | `iv_percentile`, `iv_rank`, `iv_rank_status`, `iv_seeded_share` | **§A1 handoff envelope only** — no MCP surface emits these |
| Schwab | Pass-2 chain validation for strike and structure selection | Never an IV source (see Source authority) |

### Chain scope and caps

| Parameter | Live value | Notes |
|---|---|---|
| `POLYGON_VOLATILITY_MONEYNESS_BAND` | `0.15` | env-overridable, clamped `[0.02, 0.50]`; emitted as `volatility_moneyness_band` |
| `POLYGON_VOLATILITY_CHAIN_DTE_MAX` | `120` | clamped `[60, 200]`; emitted as `volatility_chain_dte_max`, with `volatility_chain_truncated` |
| `POLYGON_VOLATILITY_CHAIN_MAX_CONTRACTS` | `4000` | floor is the options-chain cap |
| `POLYGON_VOLATILITY_LONG_BUCKET_DTE_MIN` | `60` | clamped `[31, 120]`; supplementary far-dated fetch |
| `POLYGON_VOLATILITY_LONG_BUCKET_MAX_CONTRACTS` | `2000` | |
| Batch cap | `30` symbols per `get_batch_options_metrics` call | |
| Batch defaults | `dte_min=0`, `dte_max=60`, `min_open_interest=100`, `strike_count=50`, `require_bid_ask=True` | |

### ATM IV anchor (`atm_iv`)

| Item | Live mechanic |
|---|---|
| Tenor window | `abs(dte - 30) <= 15`; emitted as `atm_iv_dte_target = 30` |
| IV sanity filter | `0 < iv <= 2.0` |
| Liquidity floor | `max(1, min_open_interest)`; emitted as `atm_iv_oi_floor` (100 at the default) |
| Selection ladder | strikes bracketing spot → linear interpolation → `atm_iv_source = atm_30dte_interp`; else nearest available side → `atm_30dte_nearest`; else the band-average `average_iv` → `fallback_band_avg` |
| Rounding | 4 decimal places |
| Downstream | numerator of `iv_hv_ratio` (`atm_iv` ÷ HV20); `fallback_band_avg` surfaces as `iv_hv_status = ATM_FALLBACK_BAND` |

### Chain metric formulas

| Metric | Live formula or mechanic |
|---|---|
| `average_iv` | OI-weighted `sum(iv*oi)/sum(oi)`; arithmetic mean when total OI is not positive; rounded 4 dp. Contract filter: `dte >= 7`, within the moneyness band (unless band fallback is active), `open_interest > 0` |
| `put_call_ratio` | `put_oi / call_oi` by open interest; null when `call_oi <= 0`; rounded 4 dp |
| `oi_ratio` | `total_volume / total_open_interest`; null when total OI is not positive; rounded 4 dp |
| `iv_skew_25delta` | `(put_25d_iv - call_25d_iv) * 100`, percentage points, rounded 2 dp. Reasons: `insufficient_25_delta_contracts`, or `skew_out_of_bounds` when `abs(skew) > 100` |

### 25-delta IV retrieval

**Single signed-delta bucket — there is no multi-step fallback chain.** The v2.3
percentile-by-strike and median-by-strike fallbacks do not exist on this surface.

| Item | Live mechanic |
|---|---|
| Target delta | `+0.25` for calls, `-0.25` for puts (signed) |
| Bucket width | target `± 0.10` |
| Candidate filter | usable IV, `open_interest >= min_open_interest`, `delta is not None` |
| Selection | contract closest to the target delta; `None` if the bucket is empty |

### Term structure (`iv_term_structure`)

ATM-to-ATM tenor comparison. Supersedes the v2.3 bucket-mean approach, which
averaged IV across every listed strike in a wide band and so measured smile shape
rather than tenor — it inverted the sign on SPY 2026-07-28 (bucket means read
`-1.81` backwardation against VIX/VIX3M at `+8.2%` contango).

| Item | Live mechanic |
|---|---|
| Formula | `(long_atm_iv - short_atm_iv) * 100`, percentage points, rounded 2 dp; positive = contango |
| Tenors | short `30 ± 15` DTE, long `90 ± 30` DTE |
| Anchor selection | candidates grouped by expiry and walked outward from the target DTE; the first expiry whose strikes bracket spot is interpolated linearly. Cross-expiry bracketing is deliberately avoided (#28) — the long-bucket fetch paginates expiration-ascending from ~60 DTE, so a window-wide bracket lands the "90-day" anchor on ~60–75 DTE strikes and biases toward apparent backwardation. Falls back to the nearest-strike contract at the closest expiry |
| Emitted method | `iv_term_structure_method = atm_interp` |
| Emitted anchors | `iv_term_structure_short_atm_iv` / `_long_atm_iv`, and the **realized** anchor DTEs `iv_term_structure_short_dte` / `_long_dte` (which need not equal the targets) |
| Unavailable | `iv_term_structure_reason` names which leg had no ATM-bracketing strikes |

### IV percentile, rank and status — viewer, not MCP

Computed in `kapman-polygon-viewer/backend/app/iv_history.py` (viewer #59) and
delivered only in the §A1 handoff envelope. **Both values are fractions in
`[0, 1]`** — not 0–100 scores. A threshold written on a 0–100 scale can never
fire against them.

| Item | Live value or formula |
|---|---|
| Trailing window | `WINDOW = 252` (~1 trading year) |
| History floor | `MIN_HISTORY = 60` points; fewer suppresses the reading rather than emitting a small-window rank |
| Illiquid-seed guard | `ILLIQUID_LOW_CONF_SHARE = 0.40` — a seed more than 40% low-confidence days is suppressed |
| `iv_rank` | `(last - min) / (max - min)` over the window, rounded 4 dp. `None` on fewer than 2 points or a flat window |
| `iv_percentile` | fraction of the window **strictly below** the as-of value: `count(v < last) / (len(window) - 1)`, rounded 4 dp |
| Series construction | offline Polygon flat-file reconstruction (`source='polygon_recon'`) stitched with native `atm_iv` accumulated daily by the forward panel; **native wins on overlapping dates**, so the seed ages out of the trailing window as native history grows |
| `iv_seeded_share` | share of the window still seeded; blanked to `None` on a suppressed row (a `0.0` would read as "fully native") |
| Headline stat | **percentile.** Rank hinges on the window's two extreme days — one differing spike shifts every reading for a year — while percentile uses the whole distribution |

### Status vocabularies (as emitted)

| Field | Values |
|---|---|
| `avg_iv_status` | `OK`, `INSUFFICIENT_CONTRACTS` (with a free-text `avg_iv_reason`) |
| `iv_hv_status` | `OK`, `ATM_FALLBACK_BAND`, `NO_PRICE_HISTORY`, `HV_ZERO`, `INSUFFICIENT_CONTRACTS` |
| `iv_rank_status` | `NATIVE`, `SEEDED`, `ILLIQUID_SEED`, `INSUFFICIENT_HISTORY`, `NO_LIVE_IV` |
| `atm_iv_source` | `atm_30dte_interp`, `atm_30dte_nearest`, `fallback_band_avg` |

No producer emits the v2.3 `MISSING_OPTIONS` / `PARTIAL` / `SUCCESS` processing
status, its `contracts_with_iv` confidence ladder, or the
`insufficient_iv_history` diagnostic. Chain quality is read from the emitted
counts — `contracts_analyzed`, `contracts_passing_filter`, `contracts_in_band`,
`volatility_band_fallback`, `volatility_chain_truncated` — each of which names a
specific defect. The v2.3 forms survive only in the Appendix.

### Source authority and endpoints

Per `VOLATILITY_015`. The v2.3 two-source model (Polygon `avg_iv` at Pass 1,
Schwab ATM at Pass 2, with an accepted `+1`–`+4` pp bias between them) is
**retired** — it survives in the Appendix as history, not as guidance.

| Item | Live value |
|---|---|
| Canonical IV producer, **both passes** | kapman-polygon-mcp-v2 `get_options_metrics` / `get_batch_options_metrics` |
| Include flag | `include=['volatility']` (add `'price'` for `iv_hv_ratio`) |
| Canonical IV field | `atm_iv` (ATM-anchored, ~30-DTE); `average_iv` is the producer's own flagged fallback, not a peer source |
| Pass 2 | **Re-fetch of the same producer** against a fresh chain — never a switch to a second source. The re-fetch re-confirms IV/HV; it cannot re-confirm the IV tier |
| IV tier source | Viewer §A1 handoff envelope only (`A1_FIELDS` since 2026-08-16) |
| Schwab's role | Pass-2 chain validator for strike and structure selection; never an IV source |
| Field never read | Schwab `theoreticalVolatility` — hardcoded `29.0` sentinel, not market IV |
| Deprecated endpoint | `get_volatility_metrics` |
| Freshness window | [CONTENT GAP — operator input required] No producer emits a freshness policy; the runtime derives staleness from `as_of` / `data_through` against a session judgment. Naming a value is a runtime decision, not a tool-surface fact |

## Legacy anchors

These map v2.3 rule IDs to the **Appendix**, which is where their original text
lives. They deliberately no longer point into `## Contents`: Contents describes
current producers, and several v2.3 anchors have no current counterpart.

- `VOLATILITY_001` → Appendix / `VOLATILITY_001`. Superseded: the live tenor windows are in Contents / Term structure; `min_history_points=20` is superseded by the viewer's `MIN_HISTORY = 60`.
- `VOLATILITY_002` → Appendix / `VOLATILITY_002`. Live counterpart: Contents / `average_iv`.
- `VOLATILITY_003` → Appendix / `VOLATILITY_003`. Live counterpart: Contents / `put_call_ratio`.
- `VOLATILITY_004` → Appendix / `VOLATILITY_004`. **No live counterpart** — no put/call *volume* ratio is emitted.
- `VOLATILITY_005` → Appendix / `VOLATILITY_005`. Live counterpart: Contents / `oi_ratio`.
- `VOLATILITY_006` → Appendix / `VOLATILITY_006`. **DROPPED from the runtime (kb#113)** — IV dispersion has no producer on any live surface.
- `VOLATILITY_007` → Appendix / `VOLATILITY_007`. Superseded: the live retrieval is a single signed-delta bucket at `± 0.10`, not the three-step fallback chain.
- `VOLATILITY_008` → Appendix / `VOLATILITY_008`. Live counterpart: Contents / `iv_skew_25delta`.
- `VOLATILITY_009` → Appendix / `VOLATILITY_009`. Superseded: bucket means replaced by the ATM-to-ATM comparison.
- `VOLATILITY_010` → Appendix / `VOLATILITY_010`. Superseded: percentile is viewer-computed on a `[0, 1]` scale, not `[0, 100]`.
- `VOLATILITY_011` → Appendix / `VOLATILITY_011`. Superseded: rank is viewer-computed on a `[0, 1]` scale, not `[0, 100]`.
- `VOLATILITY_012` → Appendix / `VOLATILITY_012`. **No live counterpart** — the processing-status trio and `insufficient_iv_history` are retired; see Contents / Status vocabularies.
- `VOLATILITY_013` → Appendix / `VOLATILITY_013`. **No live counterpart** — the `contracts_with_iv` confidence ladder is retired; chain quality is read from the emitted counts.
- `VOLATILITY_014` → Appendix / `VOLATILITY_014`. Superseded: `252` survives as the viewer's `WINDOW`, not as an MCP lookback default.
- `VOLATILITY_015` → Appendix / `VOLATILITY_015`. Live counterpart: Contents / Source authority and endpoints (the two-source model is retired).

## Appendix

### Verbatim extracted formulas and parameters

| Source anchor | Extract |
|---|---|
| `VOLATILITY_001` | `short_dte=30`, `long_dte=90`, `short_tolerance=15`, `long_tolerance=30`, `min_history_points=20` |
| `VOLATILITY_002` | `avg_iv = sum(iv*open_interest)/sum(open_interest)` when total OI is positive, arithmetic mean otherwise |
| `VOLATILITY_003` | `put_oi / call_oi` when `call_oi > 0`, null otherwise |
| `VOLATILITY_004` | `put_volume / call_volume` when `call_volume > 0`, null otherwise |
| `VOLATILITY_005` | `total_volume / total_open_interest` when total OI is positive, null otherwise |
| `VOLATILITY_006` | Population standard deviation across contract IVs, `ddof=0` |
| `VOLATILITY_007` | Nearest-delta within `0.15` tolerance → 25th/75th-percentile-by-strike → median-by-strike |
| `VOLATILITY_008` | `(put_iv - call_iv) * 100` |
| `VOLATILITY_009` | `(long_iv - short_iv) * 100`; `((back - front) * 100) / (long_dte - short_dte)`; `30±15`, `90±30` |
| `VOLATILITY_010` | Rank fraction of history values ≤ current, scaled to `[0, 100]` |
| `VOLATILITY_011` | `(current - iv_min) / (iv_max - iv_min) * 100`, clamped to `[0, 100]`, requiring `iv_max != iv_min` |
| `VOLATILITY_012` | `MISSING_OPTIONS`, `PARTIAL`, `SUCCESS`, `insufficient_iv_history` |
| `VOLATILITY_013` | High requires `contracts_with_iv >= 40` AND `front_month_contracts >= 5` AND `back_month_contracts >= 5`; medium requires `contracts_with_iv >= 20`; low otherwise; forced low when processing status is not SUCCESS |
| `VOLATILITY_014` | `DEFAULT_HISTORY_LOOKBACK = 252` |
| `VOLATILITY_015` | `get_options_metrics`, `get_batch_options_metrics`, `include=['volatility']`, batch-30-symbol cap, deprecated `get_volatility_metrics`, Schwab `theoreticalVolatility` hardcoded `29.0` sentinel |
