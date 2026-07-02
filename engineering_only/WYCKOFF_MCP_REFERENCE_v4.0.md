---
system: KapMan
doc_type: reference
kb_version: 4.0.0-alpha
file_last_updated: 2026-07-02
status: draft
tier: —
---

# WYCKOFF MCP REFERENCE

## Purpose

This file documents Wyckoff MCP detection and chart-rendering mechanics extracted from `llm_runtime/WYCKOFF_v4.0.md`. The runtime WYCKOFF file owns the propose-confirm protocol, phase vocabulary, and qualitative event-reading behavior; this file owns bar-count thresholds, disabled config defaults, event detection thresholds, sequence formulas, and event-score payload mechanics.

## Contents

### Phase and regime mechanics

| Item | Extracted value |
|---|---|
| Minimum bars in range | `min_bars_in_range = 20` |
| Soft markdown without SOW | `allow_soft_markdown_without_sow = False` |
| Chart-edge extension | Extend first and last detected structural phases to chart edges |
| Event priority order | SC → SPRING → SOS → BC → UT → SOW |
| Event-triggered confidence | Regime confidence set to `1.0` on event-triggered state changes |
| Non-event confidence persistence | Prior confidence carried forward on non-event days |
| Initial prior state | `regime=UNKNOWN, confidence=None, set_by_event=None` |
| Prior-duration threshold | `prior_duration >= 5 bars` |
| Terminal-event sequence eligibility | [CONTENT GAP — operator input required] Source anchor says eligibility is gated on prior regime and carried in runtime notes, but does not provide the mechanical prior-regime matrix. |
| Sequence confidence | `min(1.0, round(0.6 + 0.1 × max(0, n), 4))` |

### Event detection thresholds

| Event | Extracted mechanic |
|---|---|
| Selling Climax (SC) | `tr_z >= 2.0`, `vol_z >= 2.0`, `close_pos >= 0.5` |
| SC prior trend | `sma_slope < 0` when trend gating was enabled |
| Buying Climax (BC) | `tr_z >= 2.0`, `vol_z >= 2.0`, `close_pos >= 0.6` |
| BC prior trend | `sma_slope > 0` |
| Automatic Rally (AR) | First qualifying up-close after SC with `tr_z > 0.5` |
| AR_TOP | First qualifying down-close after BC with `tr_z > 0.5` |
| Spring | Support break > `1%`, re-entry within `2` bars, `close_pos >= 0.6`, `vol_z >= 0.8` |
| Upthrust (UT) | Resistance break > `1%`, re-entry within `2` bars, `close_pos <= 0.4` |
| Sign of Strength (SOS) | Close above resistance with `tr_z >= 1.5` |
| Sign of Weakness (SOW) | Close below support with `tr_z >= 1.5` |

### Event score payload

| Event group | Extracted score value |
|---|---|
| SC, BC, Spring | `vol_z` |
| AR, AR_TOP, UT, SOS, SOW | `tr_z` |

## Legacy anchors

- `WYCKOFF_PHASE_001` → Contents / Minimum bars in range.
- `WYCKOFF_PHASE_002` → Runtime phase vocabulary in `llm_runtime/WYCKOFF_v4.0.md`; no engineering-only mechanic extracted.
- `WYCKOFF_PHASE_003` → Runtime phase vocabulary in `llm_runtime/WYCKOFF_v4.0.md`; no engineering-only mechanic extracted.
- `WYCKOFF_PHASE_004` → Runtime phase vocabulary in `llm_runtime/WYCKOFF_v4.0.md`; no engineering-only mechanic extracted.
- `WYCKOFF_PHASE_005` → Runtime phase vocabulary in `llm_runtime/WYCKOFF_v4.0.md`; no engineering-only mechanic extracted.
- `WYCKOFF_PHASE_006` → Contents / Soft markdown without SOW.
- `WYCKOFF_PHASE_007` → Contents / Chart-edge extension.
- `WYCKOFF_PHASE_008` → Contents / Event priority order.
- `WYCKOFF_PHASE_009` → Contents / Event-triggered confidence and non-event persistence.
- `WYCKOFF_PHASE_010` → Contents / Initial prior state.
- `WYCKOFF_PHASE_011` → Contents / Prior-duration threshold.
- `WYCKOFF_PHASE_012` → Contents / Terminal-event sequence eligibility.
- `WYCKOFF_PHASE_013` → Contents / Sequence confidence.
- `WYCKOFF_EVENT_002` → Contents / Selling Climax thresholds.
- `WYCKOFF_EVENT_003` → Contents / SC prior trend.
- `WYCKOFF_EVENT_004` → Contents / Buying Climax thresholds.
- `WYCKOFF_EVENT_005` → Contents / BC prior trend.
- `WYCKOFF_EVENT_006` → Contents / AR threshold.
- `WYCKOFF_EVENT_007` → Contents / AR_TOP threshold.
- `WYCKOFF_EVENT_008` → Contents / Spring thresholds.
- `WYCKOFF_EVENT_009` → Contents / UT thresholds.
- `WYCKOFF_EVENT_010` → Contents / SOS threshold.
- `WYCKOFF_EVENT_011` → Contents / SOW threshold.
- `WYCKOFF_EVENT_012` → Contents / Event score payload.

## Appendix

### Verbatim extracted parameters, formulas, and thresholds

| Source anchor | Extract |
|---|---|
| `WYCKOFF_PHASE_001` | `min_bars_in_range = 20` |
| `WYCKOFF_PHASE_006` | `allow_soft_markdown_without_sow = False` |
| `WYCKOFF_PHASE_008` | SC → SPRING → SOS → BC → UT → SOW |
| `WYCKOFF_PHASE_009` | Regime confidence set to `1.0` on event-triggered state changes; prior confidence carried forward on non-event days |
| `WYCKOFF_PHASE_010` | `regime=UNKNOWN, confidence=None, set_by_event=None` |
| `WYCKOFF_PHASE_011` | `prior_duration >= 5 bars` |
| `WYCKOFF_PHASE_013` | `min(1.0, round(0.6 + 0.1 × max(0, n), 4))` |
| `WYCKOFF_EVENT_002` | `tr_z >= 2.0`, `vol_z >= 2.0`, `close_pos >= 0.5` |
| `WYCKOFF_EVENT_003` | `sma_slope < 0` |
| `WYCKOFF_EVENT_004` | `tr_z >= 2.0`, `vol_z >= 2.0`, `close_pos >= 0.6` |
| `WYCKOFF_EVENT_005` | `sma_slope > 0` |
| `WYCKOFF_EVENT_006` | `tr_z > 0.5` |
| `WYCKOFF_EVENT_007` | `tr_z > 0.5` |
| `WYCKOFF_EVENT_008` | Support break > `1%`, re-entry within `2` bars, `close_pos >= 0.6`, `vol_z >= 0.8` |
| `WYCKOFF_EVENT_009` | Resistance break > `1%`, re-entry within `2` bars, `close_pos <= 0.4` |
| `WYCKOFF_EVENT_010` | `tr_z >= 1.5` |
| `WYCKOFF_EVENT_011` | `tr_z >= 1.5` |
| `WYCKOFF_EVENT_012` | `vol_z` for SC, BC, Spring; `tr_z` for AR, AR_TOP, UT, SOS, SOW |
