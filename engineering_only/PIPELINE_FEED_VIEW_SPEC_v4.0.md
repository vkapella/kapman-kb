---
system: KapMan
doc_type: reference
kb_version: 4.0.1
file_last_updated: 2026-07-02
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
the source-authority rules live in `llm_runtime/VOLATILITY_v4.0.md`, and the §A1
ingest contract lives in `llm_runtime/PASS1_SCREENING_v4.0.md`. This file names
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
freshness, per VOLATILITY_v4.0 ("Volatility-status is derived by the runtime").
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

## §A1 ingest-map reconciliation (LANDED — `PASS1_SCREENING_v4.0.md` 3.0.12)

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

## The deterministic Pass-1 screen columns (2026-07-01, viewer #53 / KB #84)

The Stage-1 pilot's conclusion (`docs/CODE_VS_JUDGMENT_ASSESSMENT_2026-06-29.md`) is
implemented: the viewer computes the deterministic Pass-1 screen per row
(`backend/app/pass1_screen.py`, `SCREEN_VERSION 1.1` — v1.1 shipped 2026-07-02,
viewer #54, off the Stage-F SATS finding) and the export carries the disposition,
not just the raw fields.

**Five screen columns**, on the three **long-premium** Export views only (the CSP
view stays raw — the premium-sell screen contract is unpinned):

| Column | id | What it carries |
|---|---|---|
| Screen Tier | `screen_tier` | WYCKOFF validity gate + confidence tier gate (τ per SYSTEM_PARAMS) + all four hard force-flags (weekly conflict, structure conflict, SOW-gated markdown; the **stale-snapshot** flag since v1.1 — v1.0 implemented three) → `ACCEPT` / `FLAGGED` / `ESTIMATION` |
| Screen Disposition | `screen_disposition` | SIGNAL trigger sequence (direction-aware Wyckoff veto → dealer-timing veto) for the resolved direction → `ELIGIBLE` / `NO_TRADE` / `WAIT` |
| Screen Structure | `screen_structure` | `LONG_CALL` / `LONG_PUT`, or `CALL_DEBIT_SPREAD` / `PUT_DEBIT_SPREAD` when the spread-mandate fires; `NONE` otherwise |
| Screen Sizing | `screen_sizing` | RISK band note: regime ceiling → dealer-tier narrowing → vol/confidence floors → near-flip step-down |
| Screen Reasons | `screen_reasons` | semicolon-joined audit trail (named causes + tier-gate value) |

`A1_FIELDS` carries the five fields for **every** view (fixed §A1 projection; on the
CSP export they are the row's long-premium read). The envelope adds
`screen_version`, `screen_thresholds` (echoed from `/api/catalog`, single source of
truth = the viewer module), and `macro_context` (as_of, market_open, the full SPY
MarketSignal from the header market-context; `macro_context.as_of` is ISO 8601
since v1.1 — v1.0 leaked the header state's raw epoch float). The §A1 ingest-map addition landed in
`PASS1_SCREENING_v4.0.md` 3.0.13 — the KB consumes the disposition and verifies
rather than re-derives; Step-0 earnings, the macro gate, and flagged/estimation
resolution stay KB-side.

**Contract readings the implementation follows** (recorded so code and prose agree):

- **LIMITED (`ATM_FALLBACK_BAND`) does not mandate a spread** — floor sizing +
  *spread preferred* per VOLATILITY's behavioral table; a fallback-based ratio ≥
  `IV_HV_ELEVATED_THRESHOLD` still mandates via the ratio branch.
- **Direction resolution** per PASS1's priority: v2 `bias` when directional, else
  the regime's natural direction, else the `sos`/`sow` fallback — so v2's
  neutral-bias pre-phase-C rows receive the *named* conditional Wyckoff veto
  (NO_TRADE), not a WAIT.
- **Dealer-tier sizing narrowing** is a coarse encoding of DEALER's ticker-layer
  table: direction-relative DGPI ≤ −`DGPI_NEUTRAL_BAND` floors; |DGPI| <
  `DGPI_NEUTRAL_BAND` steps down one tier.
- **Operator-absent FLAGGED/ESTIMATION → WAIT** (pinned in PASS1 3.0.13).
- **Stale-snapshot force-flag (v1.1, viewer #54):** fires when the row's `as_of`
  (fallback `data_through`) lags the scan date by more than the **viewer-pinned**
  `STALE_SNAPSHOT_MAX_LAG_DAYS = 4` calendar days (echoed in `screen_thresholds`;
  deliberately NOT a SYSTEM_PARAMS name — the KB keeps run-level freshness a
  judgment, the deterministic screen needs a pinned rule). Absent/unparseable
  dates never fire it (missing-date degradation stays with the KB's §A1
  required-field contract). Provenance: the Stage-F SATS row — v2 stamps `as_of`
  from the **last price bar**, so a halted/non-printing ticker re-scans "fresh"
  forever with a frozen read (refresh-fresh ≠ data-fresh); v1.0 screened it
  ACCEPT/ELIGIBLE. **The KB's own ingest freshness check (WYCKOFF stale-snapshot
  force-flag) remains the authoritative layer** — the screen flag is
  defense-in-depth so the export's tier column stops asserting eligibility the
  KB will flag anyway.
- **Phase-C confirmation** uses the completed-phase evidence set (pinned in SIGNAL
  3.0.8).
- **Deliberate exclusions** (in the module docstring): Step-0 earnings (no viewer
  earnings field — dispositions are pre-event-screen), macro gate (envelope-only),
  IV-rank mandate arm (producer emits no IV rank), SOW-*recency* (the screen
  implements the code-detectable **absence** half; staleness stays a run-level
  freshness judgment — **kb#85 decided not to parameterize it**, see WYCKOFF_v4.0
  3.0.10), CSP screen.

**Drift discipline:** the viewer's `test_pass1_screen.py::KbParityTests` parses
`SYSTEM_PARAMS_v4.0.md` from the sibling checkout (τ_high / τ_low /
IV_HV_ELEVATED_THRESHOLD / DGPI_STRONG_BAND / DGPI_NEUTRAL_BAND) and
`KbDriftTests` anchors the same numbers in the viewer docs — a SYSTEM_PARAMS
recalibration trips viewer `pytest`. Semantic changes (veto tables, force-flag
set, mandate branches, band ladder) have **no guardrail** — re-read
`pass1_screen.py` on any change to WYCKOFF/SIGNAL/DEALER/VOLATILITY/RISK/PASS1,
and expect a `SCREEN_VERSION` bump on any behavioral change.

**4.x self-measuring note:** the screen fields freeze into
`forward_panel.payload_json` automatically, but the viewer's snapshot writer
prefers the **no-options** cache — frozen verdicts read "NO_TRADE — dealer regime
absent" regardless of the live options-on grid. Before the self-measuring loop
consumes frozen screen verdicts, either flip the snapshot preference to the
options cache (viewer change) or treat frozen screen fields as options-off reads.

## Status tracking

| Item | Side | Status |
|---|---|---|
| Producer emits `atm_iv` / `iv_hv_ratio` / `iv_hv_status` | kapman-polygon-mcp-v2 (#19) | **Landed** (958850c, Fly v12) |
| Surface ATM IV / IV-HV / status as grid columns | viewer | **Landed** |
| Four `Export - …` pipeline-feed presets | viewer | **Landed** |
| Carry the canonical IV/HV + full dealer/Wyckoff in the §A1 export | viewer (`A1_FIELDS`) | **Landed** |
| §A1 ingest map consumes `atm_iv` / `iv_hv_ratio` / `iv_hv_status` from the handoff | KB (`PASS1_SCREENING_v4.0.md` 3.0.12) | **Landed** |
| Deterministic Pass-1 screen columns + envelope (`screen_version` / `screen_thresholds` / `macro_context`) | viewer (#53, `pass1_screen.py` 1.0) | **Landed** (8f83693..52aa887) |
| §A1 ingest map consumes `screen_*`; FLAGGED→WAIT pin; phase-C predicate pin; near-flip prose fix | KB (#84; PASS1 3.0.13, SIGNAL 3.0.8) | **Landed** (this change) |
| SOW-recency window parameter (operator calibration) | KB (#85) | **Decided — not parameterized** (staleness stays a run-level judgment; WYCKOFF 3.0.10) |

## Related

- `llm_runtime/VOLATILITY_v4.0.md` — IV source-authority; the producer's `atm_iv` /
  `iv_hv_ratio` and the derived FULL/LIMITED/INVALID volatility-status.
- `llm_runtime/PASS1_SCREENING_v4.0.md` — the §A1 ingest map this spec reconciles.
- `engineering_only/VOLATILITY_MCP_REFERENCE_v4.0.md` — producer tool-surface
  mechanics (formulas, windows, thresholds).
- `kapman-polygon-viewer/docs/pipeline-feed-views.md` — the viewer-side story and
  acceptance criteria.
