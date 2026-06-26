# KapMan KB 4.0 — Design Plan

> **Consolidated into [`Kapman_System_Integration_Plan_v1.0.md`](Kapman_System_Integration_Plan_v1.0.md) (2026-06-25)** — that document is now the canonical master plan; this file remains as detailed design background for the memory + logging layer.

**Status:** Approved design, not yet built.
**Date:** 2026-06-17
**Owner:** vkapella

KB 4.0 turns the KapMan KB from a stateless, chat-driven decision system into a
CLI-run system with two new capabilities:

1. A **managed running-memory layer** so the operator stops re-supplying state every session.
2. **Complete logging** of every Pass 1 recommendation and every Pass 2 trade + targets.

It also lays the (deferred) groundwork for integrating `kapman-tradelog` and
`kapman-polygon-viewer`.

---

## 1. The spine: three planes, one rule

| Plane | Repo | Visibility | Built in 4.0? |
|---|---|---|---|
| **Decision** — the runbooks that screen & validate | `kapman-kb` | public | yes (instructions only) |
| **Memory + Log** — operator state and real trade history | **new `kapman-journal`** | **private** | yes |
| **Durable analytics** — querying, outcome scoring | `kapman-tradelog`, `kapman-polygon-viewer` | public / private | **designed, not built** |

**The one rule that prevents leakage and fragility:** *public instructions, private
data.* The public KB gains the **instructions** to read/write memory and logs; every
byte of real positions, picks, and outcomes lives in the private journal repo. The
public KB never learns a single real trade.

---

## 2. New private repo: `kapman-journal`

A standalone private git repo, added as a CLI working directory (the CLI already runs
with all KapMan repos as working dirs, so this slots in the same way). Proposed layout:

```
kapman-journal/                  (private, own remote)
├── memory/                      # mutable session state (overwritten)
│   ├── positions.md             # open positions + entry-time regime snapshot
│   ├── overrides.md             # standing operator overrides
│   └── watchlist.md             # active universe
└── log/                         # append-only history (never edited)
    ├── pass1/2026-06.md         # monthly rec logs, every screened row
    └── pass2/2026-06.md         # monthly trade logs, exact strike/exp/targets
```

Append-only logs are partitioned by month to keep files small and diffs clean. Memory
files are small and mutable.

---

## 3. Running-memory layer

**Holds:** open positions + their entry-time regime snapshot, prior Pass 1 recs /
Pass 2 trades (read from the log), standing overrides, active watchlist.

**Never holds:** confirmed Wyckoff phase / resolved direction — deliberately excluded.
They stay session-scoped via the propose-confirm protocol so a stale phase can never
silently drive a decision.

**Read:** at session start the runbook loads `memory/` as *starting context*, then
announces what it loaded so the operator can see it.

**Precedence (safety rule):** operator/broker input in the live session **always**
overrides memory. Memory is a convenience cache to stop re-pasting, never an authority.
If memory and pasted input disagree, the pasted value wins and the discrepancy is
surfaced.

**Boundary honored:** memory persists *decisions and identifiers*, never *numeric
regime reads* (DGPI, walls, IV/HV) — those are still re-fetched at Pass 2 exactly as
today. The Pass1→Pass2 boundary is untouched.

---

## 4. The recommendation / trade log

- **Granularity:** every Pass 1 row including `NO_TRADE` and `WAIT` (with disposition +
  reason), and every Pass 2 trade with exact strike/exp/entry/targets/scale. A true
  audit of what was passed on and why.
- **Format:** human-readable Markdown, but each entry carries a structured header block
  (frontmatter-style key/values) mirroring the existing Pass 1 / Pass 2 report fields —
  readable now, machine-parseable later for tradelog ingestion. It shadows
  `REPORT_FORMAT_v3.0`; no new schema invented.
- **Join keys baked in now** (for the deferred closed loop): a stable `rec_id` per row,
  plus `{date, ticker, structure, pass}`, and for Pass 2 the `{ticker, strike,
  expiration}` tuple that will later match a `kapman-tradelog` execution.
- **Forward-compatibility fields** (added for the 4.x edge layer; see
  `KB_4.x_EDGE_LAYER.md`): every row also carries a **decision anchor** — `decided_at`
  timestamp + `underlying_ref` price at decision (Pass 2 also logs `option_mid`) — so the
  viewer forward-eval can later measure what a ticker did after a yes/no, including
  refusals. Two reserved, nullable arrays — `attack_flags[]` and
  `invalidation_conditions[]` — stay empty in 4.0 and are populated when the hybrid
  red-team lands. Each record carries `schema_version`. These are written-but-mostly-empty
  in 4.0: no behavior change, but the deferred loops become drop-ins, not reshapes.
- **Write trigger:** auto-write, **end-of-run, single commit** — entries are staged
  during the run and written in one pass at the end, mirroring the KB's existing
  two-stage *compute-then-render* discipline. No mid-analysis file churn.
- **Never blocks output:** if a write fails, the report still renders; the failure is
  reported, not swallowed.

---

## 5. Changes to the public KB (`kapman-kb`)

1. **New T2 runbook** `JOURNAL_MGMT_v4.0.md` — session-start memory load, end-of-run
   log write, precedence rules, the public/private path contract. (T2 = runbook tier,
   same as PASS1/PASS2/PORTFOLIO.)
2. **Runtime rules** — add a session-start "load memory" step; extend the existing
   mandatory **Rule 7 pre-output self-audit** with a "log manifest" line (confirm every
   Pass 1 row + Pass 2 trade has a staged log entry before render).
3. **New guardrail** — "Memory is convenience, not authority; live operator/broker
   input and data-honesty always win; numeric regime reads are never persisted as
   authoritative."
4. **Archive v3.0 before the bump** — snapshot the current `llm_runtime/` and
   `engineering_only/` v3.0 files into `archive/v3.0/` as a frozen, read-only set,
   matching the existing `archive/` convention (where v2.3 already lives). Also apply a
   `v3.0` git tag at the cutover commit. The live `llm_runtime/` then becomes v4.0. This
   preserves a clean rollback point and a diffable record of exactly what 3.0 was at
   cutover. INDEX/CHANGELOG note the archival.
5. **Version + hygiene** — bump to v4.0 across INDEX/CHANGELOG/headers. This is a
   genuine major bump (the system gains persistence).

---

## 6. Designed-but-deferred (the closed loop)

Not built in 4.0, but the log schema is shaped so these are later drop-ins, not rewrites:

- **`kapman-tradelog`** — add a `TradeRecommendation` model + idempotent MD→Postgres
  ingest keyed on `rec_id`. Then join recs → imported executions on `{ticker, strike,
  expiration, entry date}` to answer "did I take it, and how did it do." (Today tradelog
  has no recommendation concept and stores no targets/stops — this is net-new but small.)
- **`kapman-polygon-viewer`** — its existing `forward_panel` + evaluation machinery
  already scores predicted targets vs forward bars. Feeding logged Pass 2 targets into
  that same pattern gives real, segmented hit-rates on actual picks. Reuse, don't rebuild.

---

## 7. Fragility guardrails (explicit)

- All writes isolated to the private repo; the public KB only ever gains text instructions.
- Single end-of-run write; a failed write degrades to "logged-to-screen + error", never
  blocks the report.
- Operator/broker input always authoritative over memory.
- No numeric regime values persisted — the Pass1→Pass2 boundary is untouched.
- Keyed, idempotent entries so a re-run never double-logs.

---

## 8. Build sequence

- **Phase 0** — (a) archive current KB 3.0 into `archive/v3.0/` (read-only snapshot) +
  `v3.0` git tag; (b) create `kapman-journal` (repo, remote, working-dir wiring, empty
  scaffolding).
- **Phase 1** — logging: the `JOURNAL_MGMT` write path + Rule 7 manifest extension.
  Prove "complete logging" end-to-end.
- **Phase 2** — memory: read-at-start + precedence + positions/overrides/watchlist
  round-trip.
- **Phase 3 (deferred)** — tradelog `TradeRecommendation` + ingest.
- **Phase 4 (deferred)** — viewer forward-eval on logged targets.

---

## 9. Open items to confirm before build (recommended defaults shown)

1. **Repo name** — `kapman-journal`? (vs `kapman-ledger` / `kapman-memory`).
2. **Memory file granularity** — the 3-file set above (positions / overrides /
   watchlist), vs a single `state.md`. *Recommend the 3-file set* — smaller diffs,
   clearer ownership.
3. **Log entry field list** — lock to the `REPORT_FORMAT_v3.0` Pass 1 columns + Pass 2
   exacts, plus join keys, plus the 4.x forward-compat fields (decision anchor; reserved
   `attack_flags[]` / `invalidation_conditions[]`; `schema_version`). Confirm nothing
   extra needs capturing at decision time (e.g., conviction note, free-text thesis).
4. **Archive scope** — default: archive `llm_runtime/` + `engineering_only/`; leave root
   docs (INDEX/README/AGENTS/CHANGELOG) living/evolving.

---

## Decisions locked (from planning interview, 2026-06-17)

- **Log of record:** MD primary (in `kapman-journal`), tradelog downstream (deferred).
- **Privacy:** new private git repo, not the public KB.
- **Memory scope:** open positions, prior recommendations, overrides & watchlist.
  *Not* confirmed Wyckoff/direction.
- **Closed loop:** design schema/keys now, build later.
- **Write trigger:** auto-write, end-of-run single commit.
- **Log granularity:** everything incl. `NO_TRADE` / `WAIT`.
- **Build scope for 4.0:** MD memory + log only; tradelog/viewer designed-but-deferred.
- **Archive:** snapshot v3.0 into `archive/v3.0/` + `v3.0` git tag at cutover.

---

## Follow-on

An OpenAnt-inspired precision layer is planned **after** 4.0 ships — see
`KB_4.x_EDGE_LAYER.md`. The only part that reaches back into 4.0 is the
forward-compatibility fields in §4; everything else layers on top of the 4.0 log.
