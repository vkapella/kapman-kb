# Swing Tenor Scan — backtest harness

Historical validation of `docs/SWING_TENOR_SCAN_PILOT_v0.1.md` (issue #95).

## Firewall — read before adding anything here

This directory follows the same boundary the pilot spec declares for itself:

- **NOT KB runtime content.** Nothing here is uploaded to LLM project
  knowledge, nothing here is consumed by Pass 1 / Pass 2, and no
  `llm_runtime/` file references it.
- **No private data, ever.** Everything here derives from public market data
  — Treasury.gov yields, CFTC public reports, CBOE index history, ETF prices.
  **No positions, no trades, no account data, no real calls.** If an analysis
  would require any of those, it does not belong in kapman-kb at all.
- **Synthetic calls are not real calls.** Backtest output contains calls that
  were never made. It must never be written to, copied into, or referenced
  from `kapman-journal/log/tenor/` — spec §7 evaluation reads that directory,
  and pooling ~900 synthetic calls with the real forward record would destroy
  exactly what the append-only rule protects.

## Why this exists

The forward pilot cannot answer §7 criteria 1 and 2. Across all five logged
run dates `layer1_score`, `layer2_score` and `composite_S` never took any
value other than `+1`, `+1`, `+3`; the governing post-2026-08-03 series has
disagreed with the always-UP baseline zero times in four runs. A forecaster
that never disagrees with its benchmark cannot beat it, at any sample size.

The backtest answers a prior question: **do these variables separate regimes
at all?** It does not replace the pilot — data degradation, producer bugs and
operator judgment only surface in live runs, and every source here resolves
cleanly by construction, so **the backtest will look better than live does.**

## Layout

```
phase0.py     realized class distribution (COMPLETE)
docs/         plan + MAINTAIN proposal
data/         cached raw inputs, committed
out/          results
```

## Data sources — primary/government only

Vendor intermediaries with per-endpoint plan gating have been retired in
favour of the issuing authority. See `docs/PHASE1_SOURCES.md` for verified
ranges, row counts and the retired-source table.

| Input | Source | Authority |
|---|---|---|
| Treasury yields (2.2) | `home.treasury.gov` daily par yield curve CSV | US Treasury |
| COT (2.5) | `publicreporting.cftc.gov` Socrata `gpe5-46if` | CFTC |
| VIX / VIX3M (1.6) | `cdn.cboe.com` index history CSV | CBOE (index publisher) |
| FOMC dates (2.6) | `federalreserve.gov` FOMC calendars | Federal Reserve |
| ETF/index prices | Schwab MCP (spec §8 source of record) | — |
| Wyckoff regime (1.1) | kapman-polygon `get_wyckoff_scan(as_of=)` | — |

## Reproducing

```bash
python3 phase0.py data/spy_daily_schwab.csv
```

Cached inputs are committed deliberately. Most are re-fetchable indefinitely;
**the Wyckoff `as_of` harvest is not** — kapman-polygon serves a rolling
~5-year window, so those scans cease to be retrievable as it advances. Treat
that cache as the only copy and never regenerate it destructively.

Record `engine_version` and `config_hash` with every cached Wyckoff scan
(observed 2026-08-17: `2.1.4` / `59fdaa23fa16`). A producer change invalidates
prior results and must be detectable.
