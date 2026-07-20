---
system: KapMan
doc_type: reference
kb_version: 4.0.0
file_last_updated: 2026-07-20
status: active
tier: —
---

# FINNHUB MCP REFERENCE

## Purpose

This file documents the tool-surface contract for `Finnhub MCP Server` — the
earnings source-of-authority named by `llm_runtime/SIGNAL_v4.0.md` Heuristic 0
and consumed by PASS1 Step 0, the PASS2 earnings re-check, and PORTFOLIO_MGMT's
Earnings-exposure advisory. The runtime files own the behavioral contract
(block/caution windows, escalation on unavailability, day-count semantics);
this file owns endpoint mechanics, response shapes, and free-tier constraints.

The server is `kapman-finnhub-mcp-server` (private repo), deployed at
`https://kapman-finnhub-mcp-server.fly.dev/mcp` (Fly.io, scale-to-zero,
~1s cold resume). 28 tools cover the full Finnhub free REST tier; only the
earnings-calendar tool is load-bearing for the KB runtime today.

## Contents

### The load-bearing tool

| Item | Value |
|---|---|
| Tool name | `get_earnings_calendar` |
| Runtime citation form | `Finnhub MCP Server:get_earnings_calendar` |
| Parameters | `symbol` (ticker, uppercase), `from_date` / `to_date` (YYYY-MM-DD) |
| KB query window | screening date → screening date + `EARNINGS_CAUTION_DAYS` + 7d buffer (PASS1/PASS2); position expiration bounds the window for the Portfolio advisory |
| Response | `{earningsCalendar: [{date, hour, quarter, year, epsEstimate, epsActual, revenueEstimate, revenueActual, symbol}]}` |
| `hour` vocabulary | `bmo` (before market open), `amc` (after market close), `dmh` (during market hours) — context only, never shifts the calendar-day count per SIGNAL Heuristic 0 |
| Empty result | `{earningsCalendar: []}` — a **validated absence** for the queried window, not a degraded read |
| Error shape | `{"error": "..."}` — the server never raises; a present `error` key is the "tool unavailable" condition that escalates to the operator gate per SIGNAL Heuristic 0 |

### Free-tier constraints that matter to the runtime

| Constraint | Value | Runtime consequence |
|---|---|---|
| Rate limit | 60 calls/min (shared budget with the fair-value app's fundamentals refresh) | One call per candidate; a 30-symbol Pass-1 batch = 30 calls, within budget. Do not interleave with bulk fundamentals pulls in the same minute. |
| History depth | 1 month back | Irrelevant to the runtime — all KB queries are forward-looking |
| Market scope | US listings | Matches the KapMan universe. NYSE/NASDAQ ADRs (e.g. TSM) resolve dates via the primary listing correctly; `epsEstimate` for those rows may arrive in local currency — the runtime consumes **dates and hour only**, never the estimate fields |
| 429 response | `{"error": "...rate limit..."}` after server-side self-throttle | Treat as tool-unavailable (operator-gate escalation) if retry within the session fails |

### Adjacent tools (available, not yet load-bearing)

`get_earnings_surprises` (last 4 quarters, beat/miss history) and
`get_recommendation_trends` are fetched by the same server and may inform
future KB layers (e.g. earnings-quality context in the KB 4.x edge layer);
no runtime file consumes them today. The full 28-tool inventory is in the
server repo's README.

### Provenance

Free/premium endpoint split verified 2026-07-19 against the Finnhub docs'
embedded Swagger spec (per-endpoint `premium` flag). Earnings-calendar
behavior live-verified in production against AAPL/NVDA/BWXT/TSM 2026-07-19.

## Legacy anchors

None — this file is new in v4.0 (issue #93); no legacy rule IDs resolve here.

## Appendix

None.
