---
system: KapMan
doc_type: reference
kb_version: 3.0.0-alpha
file_last_updated: 2026-05-13
status: draft
tier: —
---

# SIGNAL MCP REFERENCE

## Purpose

This file documents the SIGNAL persistence-normalization and backend-output mechanics extracted from `llm_runtime/SIGNAL_v3.0.md`. The runtime SIGNAL file owns trigger vocabulary and behavioral output discipline; this file owns persistence-boundary enum mappings, schema quantization, tuple-null enforcement, and v2.3 fallback confidence constants.

## Contents

### Persistence flow reference

| Item | Extracted value |
|---|---|
| v2.3 persistence flow | `core/metrics/c4_batch_ai_screening_job.py` |
| Recommendation-emission validation venue | `core/providers/ai/base.py` |
| Whether the v2.3 persistence flow remains active in current chat-time runtime | [CONTENT GAP — operator input required] Source anchor explicitly defers this question to a future session. |

### Direction normalization

| Raw direction | Stored direction |
|---|---|
| `{BULLISH, LONG}` | `LONG` |
| `{BEARISH, SHORT}` | `SHORT` |
| Else | `NEUTRAL` |

### Recommendation-action mapping

| Raw action / direction | Stored action |
|---|---|
| Raw action `PROCEED` + direction `LONG` | `BUY` |
| Raw action `PROCEED` + direction `SHORT` | `SELL` |
| Raw action `HOLD` or `AVOID` | `HOLD` |
| Raw action `BUY` / `SELL` / `HEDGE` | Pass-through |
| Else | `HOLD` |

### Confidence quantization

| Item | Extracted value |
|---|---|
| Accepted range | Decimal in `[0, 1]` |
| Quantization precision | `0.001` |
| Out-of-range or non-parseable input | Stored as null |

### Strategy enum normalization

| Raw strategy | Stored strategy |
|---|---|
| `LONG_CALL` | Pass-through |
| `LONG_PUT` | Pass-through |
| `CSP` | Pass-through |
| `VERTICAL_SPREAD` | Pass-through |
| `CALL_DEBIT_SPREAD` | `VERTICAL_SPREAD` |
| `PUT_DEBIT_SPREAD` | `VERTICAL_SPREAD` |
| Else | Stored null |

### Anti-hallucination tuple nulling

| Field forced null at persistence tuple boundary |
|---|
| `entry_price_target` |
| `stop_loss` |
| `profit_target` |
| `risk_reward_ratio` |
| `option_strike` |
| `option_expiration` |

### NO_TRADE structure consistency

| Item | Extracted value |
|---|---|
| Refusal recommendation structure class | `strategy_class = NONE` |
| Enforcement venue | Validation at the recommendation-emission boundary in `core/providers/ai/base.py` |

### Fallback confidence constants

| Fallback scenario | Extracted value |
|---|---|
| Primary action when provider output is invalid | `NO_TRADE` |
| Primary confidence when `wyckoff_veto` is the cause | `75` |
| Primary confidence otherwise | `60` |
| WAIT alternative confidence | `primary - 20` |
| Long-premium `ENTER` alternative when `iv_forbids_long_premium` is the cause | `primary - 30` |

## Legacy anchors

- `SIGNAL_001` → Contents / Direction normalization.
- `SIGNAL_002` → Contents / Recommendation-action mapping.
- `SIGNAL_003` → Contents / Confidence quantization.
- `SIGNAL_004` → Contents / Strategy enum normalization.
- `SIGNAL_005` → Contents / Anti-hallucination tuple nulling.
- `SIGNAL_006` → Contents / NO_TRADE structure consistency.
- `SIGNAL_009` → Contents / Fallback confidence constants.

## Appendix

### Verbatim extracted mappings and constants

| Source anchor | Extract |
|---|---|
| `SIGNAL_001` | Raw direction in `{BULLISH, LONG}` → stored `LONG`; raw direction in `{BEARISH, SHORT}` → stored `SHORT`; else stored `NEUTRAL` |
| `SIGNAL_002` | Raw action `PROCEED` + direction `LONG` → stored `BUY`; `PROCEED` + `SHORT` → `SELL`; `HOLD` or `AVOID` → `HOLD`; `BUY`/`SELL`/`HEDGE` → pass-through; else → `HOLD` |
| `SIGNAL_003` | Decimal in `[0, 1]` quantized to `0.001` precision; out-of-range or non-parseable input stored as null |
| `SIGNAL_004` | `LONG_CALL`, `LONG_PUT`, `CSP`, `VERTICAL_SPREAD` pass-through; `CALL_DEBIT_SPREAD` and `PUT_DEBIT_SPREAD` mapped to `VERTICAL_SPREAD`; else stored null |
| `SIGNAL_005` | `entry_price_target`, `stop_loss`, `profit_target`, `risk_reward_ratio`, `option_strike`, `option_expiration` |
| `SIGNAL_006` | `NO_TRADE` recommendations carry `strategy_class = NONE` |
| `SIGNAL_009` | Primary action `NO_TRADE`, primary confidence `75` when `wyckoff_veto` is the cause and `60` otherwise, `WAIT` alternative with confidence `primary - 20`, and long-premium `ENTER` alternative with confidence `primary - 30` when `iv_forbids_long_premium` is the cause |
