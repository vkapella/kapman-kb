---
system: KapMan
doc_type: reference
kb_version: 4.0.0-alpha
file_last_updated: 2026-07-02
status: draft
tier: —
---

# VOLATILITY MCP REFERENCE

## Purpose

This file documents volatility-metrics MCP tool-surface mechanics extracted from `llm_runtime/VOLATILITY_v4.0.md`. The runtime VOLATILITY file owns source-authority behavior and regime interpretation; this file owns formulas, windows, weighting schemes, history lookbacks, status thresholds, endpoint references, and provider-specific mechanical details.

## Contents

### Horizon and history parameters

| Parameter | Extracted value |
|---|---|
| `short_dte` | `30` |
| `long_dte` | `90` |
| `short_tolerance` | `15` |
| `long_tolerance` | `30` |
| `min_history_points` | `20` |
| `DEFAULT_HISTORY_LOOKBACK` | `252` |

### Chain metric formulas

| Metric | Extracted formula or mechanic |
|---|---|
| OI-weighted `avg_iv` | `avg_iv = sum(iv*open_interest)/sum(open_interest)` when total OI is positive; arithmetic mean otherwise |
| Put/call OI ratio | `put_oi / call_oi` when `call_oi > 0`, null otherwise |
| Put/call volume ratio | `put_volume / call_volume` when `call_volume > 0`, null otherwise |
| OI ratio | `total_volume / total_open_interest` when total OI is positive, null otherwise |
| IV dispersion | Population standard deviation across contract IVs, `ddof=0` |
| IV skew | `(put_iv - call_iv) * 100`, scaled to percentage points |

### 25-delta IV retrieval fallback chain

| Step | Extracted mechanic |
|---|---|
| 1 | Nearest-delta within `0.15` tolerance |
| 2 | 25th/75th-percentile-by-strike |
| 3 | Median-by-strike |

### Term-structure formulas

| Metric | Extracted formula or parameter |
|---|---|
| Term-structure level | `(long_iv - short_iv) * 100` |
| Term-structure slope | `((back - front) * 100) / (long_dte - short_dte)` |
| Front/back target windows | `30±15`, `90±30` |

### IV percentile and rank

| Metric | Extracted formula or guard |
|---|---|
| IV percentile | Rank fraction of history values ≤ current, scaled to `[0, 100]` |
| IV rank | `(current - iv_min) / (iv_max - iv_min) * 100`, clamped to `[0, 100]` |
| IV rank guard | Requires `iv_max != iv_min` |
| History-floor precondition | `min_history_points=20` |

### Processing status and confidence

| Item | Extracted value |
|---|---|
| Processing status: `MISSING_OPTIONS` | No snapshot or no contracts |
| Processing status: `PARTIAL` | Contracts exist but `avg_iv` is null |
| Processing status: `SUCCESS` | Full pipeline output |
| Parallel diagnostic | `insufficient_iv_history` when history is below the 20-point floor |
| Confidence high | `contracts_with_iv >= 40` AND `front_month_contracts >= 5` AND `back_month_contracts >= 5` |
| Confidence medium | `contracts_with_iv >= 20` |
| Confidence low | Otherwise |
| Forced low | Processing status is not `SUCCESS` |

### Source authority and endpoints

| Item | Extracted value |
|---|---|
| Pass 1 canonical endpoints | `get_options_metrics`, `get_batch_options_metrics` |
| Pass 1 include flag | `include=['volatility']` |
| Pass 1 batch cap | `30` symbols per call |
| Deprecated endpoint | `get_volatility_metrics` |
| Pass 1 IV field | Polygon `avg_iv` |
| Pass 1 accepted bias | Residual `+1` to `+4` percentage point positive bias vs. Schwab ATM IV |
| Pass 2 canonical source | Schwab options chain endpoint, ATM portion |
| Pass 2 IV field | Per-contract `volatility` field at nearest-to-money strike |
| Field never read | Schwab `theoreticalVolatility` |
| Schwab sentinel value | Hardcoded `29.0` sentinel, not market IV |
| Schwab chain endpoint name and parameter shape | [CONTENT GAP — operator input required] Source text assigns this to engineering-only but does not provide the exact endpoint name or schema. |
| Freshness window | [CONTENT GAP — operator input required] Source text says the freshness window is set by the MCP data provider but does not provide a value. |

## Legacy anchors

- `VOLATILITY_001` → Contents / Horizon and history parameters.
- `VOLATILITY_002` → Contents / OI-weighted `avg_iv`.
- `VOLATILITY_003` → Contents / Put/call OI ratio.
- `VOLATILITY_004` → Contents / Put/call volume ratio.
- `VOLATILITY_005` → Contents / OI ratio.
- `VOLATILITY_006` → Contents / IV dispersion.
- `VOLATILITY_007` → Contents / 25-delta IV retrieval fallback chain.
- `VOLATILITY_008` → Contents / IV skew.
- `VOLATILITY_009` → Contents / Term-structure formulas.
- `VOLATILITY_010` → Contents / IV percentile.
- `VOLATILITY_011` → Contents / IV rank.
- `VOLATILITY_012` → Contents / Processing status.
- `VOLATILITY_013` → Contents / Confidence.
- `VOLATILITY_014` → Contents / `DEFAULT_HISTORY_LOOKBACK`.
- `VOLATILITY_015` → Contents / Source authority and endpoints.

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
