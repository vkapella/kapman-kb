---
system: KapMan
doc_type: reference
kb_version: 4.0.1-alpha
file_last_updated: 2026-08-17
status: draft
tier: —
---

# DEALER PIPELINE

## Purpose

This file documents the dealer-metrics pipeline mechanics extracted from `llm_runtime/DEALER_v4.0.md` legacy anchors. The runtime DEALER file owns the behavioral contract for interpreting delivered dealer outputs; this file owns the formulas, thresholds, filters, defaults, and data-depth mechanics that produce those outputs.

## Contents

### Contract filtering

| Item | Extracted value |
|---|---|
| DTE filter | `dte <= 90` |
| Open-interest filter | `open_interest >= 100` |
| Volume filter | `volume >= 1` |
| Gamma requirement | gamma present |

### GEX computation

| Item | Extracted value |
|---|---|
| Per-contract GEX | `gex = gamma * open_interest * spot^2 * 0.01 * contract_multiplier`, with call-side sign inversion |
| Strike-level GEX aggregation | Additive across contracts at the same strike |
| Gamma flip computation | Zero-cross interpolation |
| Gamma flip exact interpolation formula | [CONTENT GAP — operator input required] Source anchor names zero-cross interpolation but does not provide the exact interpolation formula. |

### Wall computation

| Item | Extracted value |
|---|---|
| Wall candidate filters | Contract-type match, positive OI, non-null gamma, `abs(strike-spot)/spot <= 0.2` |
| Wall ranking weights | `1.0 / 0.7 / 0.4 / 0.2` across four moneyness bands |
| Moneyness band cutoffs for weights | [CONTENT GAP — operator input required] Source anchor gives the four weight values but not the band boundaries. |
| Ranking sort | Descending weighted GEX, strike tie-break |
| Top-N truncation | Default `top_n = 3` |

### Slope and DGPI

| Item | Extracted value |
|---|---|
| GEX slope | `slope = (upper_gex - lower_gex) / price_range` over `±2%` of spot |
| Slope range default | `gex_slope_range_pct = 0.02` |
| DGPI components | Signed log-scaled net GEX, slope multiplier with `±0.3` clamp, optional IV-rank weighting (**dormant** — see below), output clamp to `[-100, 100]` |
| IV-rank weighting status | **Never applied in production.** `calculate_dgpi` accepts an optional `iv_rank` parameter, but the sole production call path omits it — and kapman-polygon-mcp-v2 emits no IV-rank surface, so it could not supply one (verified 2026-08-17; IV rank is viewer-computed and reaches the KB only via the §A1 envelope). Every delivered DGPI is unweighted |
| DGPI exact formula | [CONTENT GAP — operator input required] Source anchor names the components but does not provide the complete algebraic formula. |

### Position class

| Item | Extracted value |
|---|---|
| Neutral threshold | `|net_gex| < 1,000,000` → `neutral` |
| Positive net GEX class | `long_gamma` |
| Negative net GEX class | `short_gamma` |

### Confidence and dealer-status resolution

| Item | Extracted value |
|---|---|
| Contracts-with-gamma cutoffs | `5/10` cutoffs |
| High-confidence OI floor | Total OI `≥ 1000` for `high` |
| Other confidence labels | `medium` / `low` / `invalid` below source bounds |
| Primary FULL cutoff | FULL requires `eligible_options >= 25` |
| Primary LIMITED cutoff | LIMITED requires `eligible_options >= 1` |
| Dealer-status inputs | Eligible-options count, GEX validity, position-class validity, confidence level |
| Secondary metadata FULL/LIMITED threshold | `min_eligible_threshold = 5`, distinct from the primary classifier's `25` |

### Runtime defaults

| Parameter | Extracted value |
|---|---|
| `walls_top_n` | `3` |
| `gex_slope_range_pct` | `0.02` |
| `max_moneyness` | `0.2` |
| Freshness window | [CONTENT GAP — operator input required] Source workflow says timestamps are compared to the pipeline's freshness window, but no value is provided. |

## Legacy anchors

- `DEALER_001` → Contents / Contract filtering.
- `DEALER_002` → Appendix / Per-contract GEX formula.
- `DEALER_003` → Contents / Strike-level GEX aggregation.
- `DEALER_004` → Contents / Gamma flip computation; runtime interpretation remains in `llm_runtime/DEALER_v4.0.md`.
- `DEALER_005` → Contents / Wall computation filters.
- `DEALER_006` → Contents / Wall ranking weights.
- `DEALER_007` → Contents / Wall ranking sort and top-N truncation.
- `DEALER_008` → Appendix / GEX slope formula.
- `DEALER_009` → Contents / DGPI components; runtime tier semantics remain in `llm_runtime/DEALER_v4.0.md`.
- `DEALER_010` → Contents / Position class.
- `DEALER_011` → Contents / Confidence classifier.
- `DEALER_012` → Contents / Dealer-status resolution; runtime label semantics remain in `llm_runtime/DEALER_v4.0.md`.
- `DEALER_013` → Contents / Secondary metadata-status classifier.
- `DEALER_014` → Contents / Runtime defaults.

## Appendix

### Verbatim extracted formulas and parameters

| Source anchor | Extract |
|---|---|
| `DEALER_001` | `dte <= 90`, `open_interest >= 100`, `volume >= 1`, gamma present |
| `DEALER_002` | `gex = gamma * open_interest * spot^2 * 0.01 * contract_multiplier`, with call-side sign inversion |
| `DEALER_003` | Strike-level GEX aggregation is additive across contracts at the same strike. |
| `DEALER_004` | Gamma flip level computed by zero-cross interpolation. |
| `DEALER_005` | `abs(strike-spot)/spot <= 0.2` |
| `DEALER_006` | `1.0 / 0.7 / 0.4 / 0.2` |
| `DEALER_007` | Default `top_n = 3` |
| `DEALER_008` | `slope = (upper_gex - lower_gex) / price_range` over `±2%` of spot |
| `DEALER_009` | Signed log-scaled net GEX, slope multiplier with `±0.3` clamp, optional IV-rank weighting (dormant — never passed in production; see Slope and DGPI), output clamp to `[-100, 100]` |
| `DEALER_010` | `|net_gex| < 1,000,000` → neutral; positive → `long_gamma`; negative → `short_gamma` |
| `DEALER_011` | Contracts-with-gamma `5/10` cutoffs; total OI `≥ 1000` for `high` |
| `DEALER_012` | FULL requires `eligible_options >= 25`; LIMITED requires `>= 1` |
| `DEALER_013` | `min_eligible_threshold = 5`, distinct from the primary classifier's `25` |
| `DEALER_014` | `walls_top_n = 3`, `gex_slope_range_pct = 0.02`, `max_moneyness = 0.2` |
