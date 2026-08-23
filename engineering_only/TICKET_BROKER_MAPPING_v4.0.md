---
system: KapMan
doc_type: reference
kb_version: 4.0.0
file_last_updated: 2026-08-23
status: active
tier: —
---

# TICKET_BROKER_MAPPING

The `trade_ticket` → broker-order translation contract (kb#116, Increment 0 of the
ticket layer). The ticket grammar is owned by `llm_runtime/JOURNAL_MGMT_v4.0.md`;
this file owns only the mapping from ticket + APPROVED-event fields to a Schwab
Trader API order payload. **This is a paper contract in Increment 0** — the
`translate(ticket, approval)` function is Increment 4 work (`kapman-execution`),
and its golden tests must assert against this table. No translation code ships
before then: Schwab's Trader API offers no individual-developer paper sandbox, so
code written now would sit untested.

The design rule this file enforces: **the ticket is Schwab-derivable, never
Schwab-shaped.** The record grammar is broker-neutral (a manual Fidelity fill and
an API-routed Schwab fill are the same record shape); everything broker-specific
lives in this mapping and in the APPROVED event.

## Scope

Single-leg structures only: `LONG_CALL`, `LONG_PUT`, `CSP`, `LEAP_LONG_CALL`,
`LEAP_SHORT_PUT`. **Multi-leg structures (call/put debit spreads) are a named
limitation of Increment 0** — Pass 2 validates them regularly, and a spread
ticket needs a legs list this grammar does not yet define. Tracked as its own
follow-up issue; until it lands, spread recommendations produce no ticket and the
run's Rule 7 manifest names the omission.

## The OSI symbol rule

`osi_symbol = root padded right with spaces to 6 chars + YYMMDD + C|P +
strike×1000 zero-padded to 8 digits`

Example: AMZN · 2026-11-20 · Call · 280 → `AMZN  261120C00280000`
(two spaces after AMZN; strike field `00280000`).

The symbol is **derived at ticket-write time, never typed.** It doubles as the
manual-entry string pasted at the broker, which is what makes
which-contract-did-I-actually-buy questions structurally impossible.

## Field mapping — ticket + APPROVED event → Trader API order

| Source | Ticket / event field | Trader API field | Rule |
|---|---|---|---|
| ticket | `instrument.osi_symbol` | `orderLegCollection[0].instrument.symbol` | verbatim |
| ticket | `instrument.asset_type` = `OPTION` | `orderLegCollection[0].instrument.assetType` | `OPTION` |
| approved | `quantity` | `orderLegCollection[0].quantity` | integer, computed at approval (sizing band × destination-account denominator ÷ approved limit) |
| approved | `instruction` | `orderLegCollection[0].instruction` | derived, stamped never typed — see table below |
| approved | `limit_price` | `price` | string, 2 decimals; MUST fall inside the ticket's `entry_range` or the APPROVED event carries an explicit override note |
| approved | `duration` = `DAY` \| `GTC` | `duration` | `DAY` \| `GOOD_TILL_CANCEL` |
| — | (fixed) | `orderType` | `LIMIT` — always; the entry-range rule makes market orders unrepresentable by design |
| — | (fixed) | `session` | `NORMAL` |
| — | (fixed) | `orderStrategyType` | `SINGLE` |
| — | (fixed) | `complexOrderStrategyType` | `NONE` |

## Instruction derivation

| Structure | side: open | side: close (reserved — future increment) |
|---|---|---|
| `LONG_CALL`, `LONG_PUT`, `LEAP_LONG_CALL` | `BUY_TO_OPEN` | `SELL_TO_CLOSE` |
| `CSP`, `LEAP_SHORT_PUT` | `SELL_TO_OPEN` | `BUY_TO_CLOSE` |

## Guards the translator must enforce (mirroring the grammar)

- **Staleness:** a ticket past its TTL (origin session + first 30 minutes of the
  next regular session) is EXPIRED and untranslatable — the path back is a fresh
  Pass 2, never a translated stale range.
- **Range:** `limit_price` outside `entry_range` without an override note →
  refuse to translate.
- **Status:** only a ticket with an APPROVED event translates; PROPOSED /
  REJECTED / EXPIRED never reach the broker.
- **No regime fields:** the payload carries no thesis or regime content — those
  are ticket/journal concerns, and "the thesis still holds" is a fresh-fetch
  question, never a translated one.

## Worked example

Ticket `VS-20260807-1425-01/P2-01/T1` (AMZN LONG_CALL 280 × 2026-11-20, entry
range 16.60–16.90) + APPROVED {limit_price 16.85, duration DAY, quantity 2}:

```json
{
  "orderType": "LIMIT",
  "session": "NORMAL",
  "duration": "DAY",
  "orderStrategyType": "SINGLE",
  "complexOrderStrategyType": "NONE",
  "price": "16.85",
  "orderLegCollection": [
    {
      "instruction": "BUY_TO_OPEN",
      "quantity": 2,
      "instrument": { "symbol": "AMZN  261120C00280000", "assetType": "OPTION" }
    }
  ]
}
```
