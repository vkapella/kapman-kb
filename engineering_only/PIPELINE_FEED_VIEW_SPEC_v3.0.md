---
system: KapMan
doc_type: reference
kb_version: 3.0.0
file_last_updated: 2026-06-28
status: active
tier: —
---

# PIPELINE-FEED VIEW SPEC

## Purpose

This file records the **column-set contract** for the viewer's purpose-built
"Export -" pipeline-feed views — the layouts whose displayed columns ARE the
§A1 Pass-1 handoff surface — and tracks the viewer-side surfacing of the
canonical ATM IV / IV-HV metrics and the KB-side §A1 ingest-map reconciliation
that closes the self-contained loop.

It is engineering coordination between `kapman-polygon-viewer` (the producer of
the handoff) and `kapman-kb` (the consumer). It is **not** a runtime principle:
the source-authority rules live in `llm_runtime/VOLATILITY_v3.0.md`, and the §A1
ingest contract lives in `llm_runtime/PASS1_SCREENING_v3.0.md`. This file names
*which columns the viewer exports for which strategy* and *what the §A1 map must
change to consume the new IV/HV fields* — the mechanical detail, not the
judgment.

## Provenance

- **Producer:** `kapman-polygon-mcp-v2` commit `958850c` ("Add ATM-anchored IV/HV
  metrics"), Fly release v12, issue #19 closed. Emits `atm_iv`, `atm_iv_source`,
  `atm_iv_dte_target`, `atm_iv_oi_floor` in `metrics.volatility`, and
  `iv_hv_ratio`, `iv_hv_methodology`, `iv_hv_status` in `metrics.price`.
- **Viewer change:** `kapman-polygon-viewer` — see `docs/pipeline-feed-views.md`.
  Surfaces `atm_iv` / `iv_hv_ratio` / `iv_hv_status` as grid columns, adds the four
  Export presets, and adds the new fields to the §A1 export (`A1_FIELDS`).
- **KB contracts already landed:** the VOLATILITY re-key to the Polygon producer's
  `atm_iv` / `iv_hv_ratio` and the KB-derived FULL/LIMITED/INVALID volatility-status
  (#80), and the DEALER signed-DGPI / confidence re-key (#79).

## The canonical IV/HV columns (viewer-derived, producer-equal)

The wyckoff-scan path the viewer consumes already carries `volatility.atm_iv` and
`features.historical_volatility` (HV20) — the same two inputs the producer's
`metrics.price` divides. The viewer derives the ratio/status locally
(`flatten.derive_iv_hv`), so the values **equal** the producer's with no extra
fetch and no second source.

| Viewer column | id | Source / derivation | Equals producer field |
|---|---|---|---|
| ATM IV | `atm_iv` | `scan.volatility.atm_iv` (pass-through) | `metrics.volatility.atm_iv` |
| IV/HV | `iv_hv_ratio` | `atm_iv ÷ HV20`, prefer `atm_iv`, fall back to `average_iv` | `metrics.price.iv_hv_ratio` |
| IV/HV Status | `iv_hv_status` | mechanical: `OK` / `ATM_FALLBACK_BAND` / `INSUFFICIENT_CONTRACTS` / `NO_PRICE_HISTORY` / `HV_ZERO` | `metrics.price.iv_hv_status` |

`iv_hv_status` reports mechanical availability only — the FULL/LIMITED/INVALID
volatility-status the runtime weights is **derived by the KB** from this status +
freshness, per VOLATILITY_v3.0 ("Volatility-status is derived by the runtime").
`atm_iv_source` is available in the scan but not surfaced as a column; the
`ATM_FALLBACK_BAND` status already flags the band-average fallback.

## Export view column-set contract

Every Export view carries the **feed base** (the comprehensive §A1 surface) plus a
strategy-specific target ladder, directional event, filter, and sort. The feed
base, in canonical decision-priority order, is:

- **Trust:** `regime`, `regime_confidence`, `weekly_agrees`, `structure_conflict`,
  `conviction`
- **Setup:** `bias`, `setup_tags`, `phase`, `phase_confidence`, `weekly_trend`,
  `last_event`, `last_event_date`, `range_support`, `range_resistance`, `range_type`
- **Targets / stops:** `price`, `invalidation_level`, `atr_14`, `rvol_20`,
  `pt_scenario`, `pt_calibration`
- **Dealer (full contract, #79):** `net_gex`, `gamma_flip`, `dgpi`,
  `dealer_position`, `position_vs_flip`, `gex_slope`, `dealer_confidence`,
  `dealer_consistent`
- **Volatility (full contract):** `atm_iv`, `iv_hv_ratio`, `iv_hv_status`,
  `average_iv`, `iv_skew_25delta`, `historical_volatility`, `iv_term_structure`,
  `put_call_ratio`, `volatility_consistent`
- **Lineage:** `options_status`, `as_of`, `data_through`, `engine_version`

| Export view | Strategy | Target ladder | Directional event | Filters | Sort |
|---|---|---|---|---|---|
| Export - Swing Long Calls | Long calls (bull) | up `pt_up_*` (+ trigger) | `last_spring_price` | bias=long; pt_scenario=up; regime∈{markup, accumulation, reaccumulation} | regime_confidence ↓, conviction ↓ |
| Export - Swing Long Put | Long puts (bear) | down `pt_down_*` (+ trigger) | `last_utad_price` | bias=short; pt_scenario=down; regime∈{markdown, distribution, redistribution} | regime_confidence ↓, conviction ↓ |
| Export - LEAPS | Long-horizon calls | up `pt_up_*` + `weekly_regime_hint`, `weekly_close_vs_30w`, `sma_50`, `sma_200`, `adx_14` | `last_spring_price` | weekly_trend=up; weekly_regime_hint∈{markup, late_markup}; weekly_close_vs_30w=above; regime∈{markup, accumulation, reaccumulation} | regime_confidence ↓, conviction ↓ |
| Export - CSP | Cash/margin-secured puts (bullish-neutral premium sell) | down `pt_down_*` (assignment-risk context) | `last_spring_price` | regime∈{accumulation, reaccumulation, markup}; weekly_trend∈{up, flat} | `iv_hv_ratio` ↓ (fattest premium first) |

The bear view is the exact mirror of the bull view (down ladder + UTAD in place of
up ladder + spring). The CSP view is bullish-to-neutral: it carries the bull
surface and the spring but sorts by IV/HV richness because the operator sells
premium where implied leads realized.

## §A1 ingest-map reconciliation (LANDED — `PASS1_SCREENING_v3.0.md` 3.0.12)

The viewer export (`A1_FIELDS`) carries the canonical IV/HV, and the KB §A1 ingest
map now consumes it from the handoff rather than reaching to the Polygon MCP live:

- **§A1 volatility row** now lists `atm_iv`, `iv_hv_ratio`, `iv_hv_status` (canonical
  spread-mandate input) alongside the `average_iv` / `iv_skew_25delta` /
  `iv_term_structure` / `put_call_ratio` / `historical_volatility` context reads.
  When `iv_hv_ratio` is present in the handoff, the spread-mandate fires off the
  handoff's canonical `iv_hv_ratio` (no live MCP fetch); `iv_hv_status` drives the
  runtime-derived volatility-status exactly as a direct fetch would. Absence still
  degrades to fire-by-default per VOLATILITY; the *Needs chain validation* label is
  unchanged (Pass 2 re-confirms on a fresh producer fetch).
- **§A1 dealer row** adds `dealer_position` for completeness of the dealer contract.

The Pass 1 → Pass 2 boundary is unchanged: the handoff is Pass-1 triage context;
Pass 2 re-fetches the producer fresh regardless. The single/batch live fetch is now
the path for tickers fetched directly (no handoff reading) and the fire-by-default
fallback.

## Status tracking

| Item | Side | Status |
|---|---|---|
| Producer emits `atm_iv` / `iv_hv_ratio` / `iv_hv_status` | kapman-polygon-mcp-v2 (#19) | **Landed** (958850c, Fly v12) |
| Surface ATM IV / IV-HV / status as grid columns | viewer | **Landed** |
| Four `Export - …` pipeline-feed presets | viewer | **Landed** |
| Carry the canonical IV/HV + full dealer/Wyckoff in the §A1 export | viewer (`A1_FIELDS`) | **Landed** |
| §A1 ingest map consumes `atm_iv` / `iv_hv_ratio` / `iv_hv_status` from the handoff | KB (`PASS1_SCREENING_v3.0.md` 3.0.12) | **Landed** (this change) |

## Related

- `llm_runtime/VOLATILITY_v3.0.md` — IV source-authority; the producer's `atm_iv` /
  `iv_hv_ratio` and the derived FULL/LIMITED/INVALID volatility-status.
- `llm_runtime/PASS1_SCREENING_v3.0.md` — the §A1 ingest map this spec reconciles.
- `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` — producer tool-surface
  mechanics (formulas, windows, thresholds).
- `kapman-polygon-viewer/docs/pipeline-feed-views.md` — the viewer-side story and
  acceptance criteria.
