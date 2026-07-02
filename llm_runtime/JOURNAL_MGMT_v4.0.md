---
system: KapMan
doc_type: runbook
kb_version: 4.0.3
file_last_updated: 2026-06-28
status: active
tier: T2
---

# JOURNAL MANAGEMENT

## Principle

Journal management is the persistence discipline for the KapMan system: it governs how a session loads prior state, derives lineage, and writes a complete, tamper-evident record of every screening and validation decision — all of it isolated to the private `kapman-journal` repo, with the public KB holding only the instructions, never a byte of real trade data. The governing judgment is that the journal is the system's memory and audit trail but never its authority: the files under `memory/` are a convenience cache loaded at session start to spare the operator from re-keying state, and live operator or broker input always overrides them, with any disagreement surfaced rather than silently resolved. Logging is complete by construction — every Pass 1 row including NO_TRADE and WAIT, and every Pass 2 trade with its exact strike, expiration, and targets — because the log's value is in what was passed on and why, not only in what was taken. Logs are append-only and written one file per run, never reopened, so the clone→commit→push round-trip stays conflict-free; memory files are overwritten in place. Every write rides a single end-of-run commit, staged during the run in the same compute-then-render discipline the report already follows, and a failed write degrades to logged-on-screen-plus-error — it never blocks the report. Lineage is derived, not invented: the shared lineage ID comes from the pasted export's own `exported_at` timestamp plus a per-day sequence suffix, is copied verbatim across all three logs, and is echoed back in-session so the operator can eyeball it against what the viewer exported. The Pass 1 → Pass 2 boundary is untouched — numeric regime reads are never persisted as authoritative, the sole exemption being the immutable entry-time snapshot in `positions.md`, a historical record that is never re-read to seed a new decision.

## Operational heuristics

**All journal writes are isolated to the private `kapman-journal` repo; the KB carries only the instructions.**

Every byte of real position, pick, and outcome data is written to `kapman-journal` and nowhere public. This runbook — and the KB that contains it — hold the *instructions* to read and write that data, never the data itself. Nothing from the KB's `llm_runtime/` is copied into the journal, and nothing from the journal is surfaced into the KB or into any report artifact that leaves the private boundary. The journal is a separate working directory with its own private remote; a session operates on it as it would any repo, but the public/private split is absolute — it is the reason the system can log real trades at all. When a write would cross that boundary in either direction, the write does not happen and the conflict is surfaced.

**At session start, the runbook loads `memory/` as starting context and announces what it loaded.**

Before any screening or portfolio work, the session reads `memory/positions.md`, `memory/overrides.md`, and `memory/watchlist.md` and states, in-session, what it found — open positions and their entry-time context, any standing overrides, and the active universe — so the operator sees the starting state and can correct it immediately. The load is orientation, not instruction: it reports what was true as of the last write, not what to do now. An empty or absent memory file is reported as such, never silently treated as "no state" — the announcement distinguishes "no open positions recorded" from "positions file not loaded."

**Live operator or broker input always overrides memory, and disagreements are surfaced, never silently resolved.**

Memory is a convenience cache; it is never the authority a decision rests on. When the operator states something — or a broker/tradelog snapshot shows something — that conflicts with what `memory/` holds, the live value wins and the session says so explicitly ("memory has three open SPY puts; you're reporting two — proceeding with two, flagging the mismatch"). The session does not quietly prefer either side and does not average them. This precedence is what lets memory be a convenience without becoming a stale authority: the cost of a wrong remembered value is a surfaced discrepancy, not a bad decision. (The behavioral floor lives in `KAPMAN_GUARDRAILS`; this runbook owns the load-and-reconcile mechanics.)

**The lineage ID is derived from the export's own `exported_at` timestamp, copied verbatim everywhere, and echoed back in-session.**

When the operator pastes a viewer or tradelog export, the session derives a single lineage ID from the payload's own `exported_at` timestamp plus a per-day sequence suffix — never from the session's notion of "now," which has no reliable clock. The format is `VS-YYYYMMDD-HHMM-NN`: a source prefix, the export date and time mirrored from `exported_at`, and a two-digit per-day sequence that disambiguates collisions. That ID is the shared spine of the run — written verbatim into the handoff record and copied, never reformatted or regenerated, into the Pass 1 and Pass 2 records that descend from it. On receipt the session echoes it back with the payload's `row_count` and `as_of` ("received VS-20260625-1335-01, 47 rows, as_of 2026-06-25") so the operator can eyeball it against what the viewer exported, and it prints the same ID in the header of every Pass 1 / Pass 2 table it renders, so lineage is visible in-session, not only in the file. If a pasted export carries no `exported_at`, lineage cannot be derived — the session surfaces "lineage unavailable — export carries no `exported_at`" and proceeds with the run's logs flagged lineage-degraded; it never fabricates an ID from the session clock.

**The journal holds three logs — the input split by source, the two outputs by pass — each written one file per run and never reopened.**

Handoffs are partitioned first by source, because a viewer scan and a tradelog positions snapshot are different payloads feeding different modes: `handoffs/viewer/<YYYY-MM>/` captures the pasted viewer export that feeds Pass 1, and `handoffs/tradelog/<YYYY-MM>/` captures the pasted tradelog positions snapshot that feeds Portfolio mode (together, LOG 1, the input). `log/pass1/<YYYY-MM>/` captures every Pass 1 determination, including NO_TRADE and WAIT with disposition and reason (LOG 2). `log/pass2/<YYYY-MM>/` captures every Pass 2 trade with exact strike, expiration, entry range, and targets (LOG 3). Each run writes a new file named by its lineage ID under the matching source-or-pass and month directory; a prior run's file is never edited or reopened. The month directory is a partition for tidy diffs, not a shared file — there is no read-modify-write on a monthly file, which is what keeps the clone→commit→push round-trip conflict-free even from a stale clone. The handoff's `kind`/`source` frontmatter still records the payload type for machine parsing; the directory split makes that fact visible on the filesystem without opening the file. The lineage chain is recorded by parent links: the Pass 1 record carries `source_handoff`, the Pass 2 record carries `parent_pass1`, so the three logs join back to a single handoff.

**Memory files are written end-of-run, overwritten in place, on the trigger that owns each file.**

The three memory files change on distinct triggers, and each write is a full overwrite of that file, never an append. `positions.md` is written at two moments: at Pass 2 validation of a new entry, when the position and its immutable entry-time regime snapshot (entry Wyckoff regime, DGPI tier, flip-zone, IV/HV band, vol-status, and the eight SIGNAL stop/profit levels) are recorded; and on a Portfolio-mode positions refresh from a tradelog or broker snapshot, when the open/closed set and live fields (mark, net_qty, unrealized P&L) are reconciled. A refresh updates live state only — the entry-time snapshot is write-once and is never rewritten. `overrides.md` is written when the operator explicitly states a standing preference to remember across sessions (e.g., "always block earnings within seven days"); it is never inferred from conversational context, and a standing override recorded here does not activate the per-request macro-gate override defined in `KAPMAN_GUARDRAILS` — it is a remembered convenience, not an active gate. `watchlist.md` is written when the active universe changes — a new viewer handoff defines or refreshes it, or the operator adds or removes tickers. All three writes ride the same end-of-run commit as the logs.

**Numeric regime reads are never persisted as authoritative; the entry-time snapshot is the sole, narrow exemption.**

DGPI, gamma flip and walls, IV, HV, vol-status, and every other numeric regime value are re-fetched at Pass 2 from their source-of-authority tool and are never carried forward — from memory, a handoff, or a prior log — as the number a new decision is made on. The Pass 1 → Pass 2 boundary the KB already enforces is untouched: the journal persists decisions and identifiers, not live regime numbers. The one exemption is the entry-time snapshot in `positions.md` — persisted deliberately, as immutable historical entry context, so Portfolio's Regime-exit advisory can measure decay against the conditions a position was opened under. It is a record, not an authority, and is never re-read to seed a new Pass 1 or Pass 2 decision; a fresh decision always re-fetches the live regime. This is the same boundary the guardrail in `KAPMAN_GUARDRAILS` states as a refusal — this runbook owns where the exempt snapshot is written and read.

**Before any report renders, the Rule 7 self-audit confirms a staged log entry exists for every row.**

Logging is complete by construction only if completeness is checked before output, not after. The mandatory pre-output self-audit (Rule 7, owned by `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS`) carries a log-manifest line: every Pass 1 determination — including every NO_TRADE and WAIT — and every Pass 2 trade must have a staged journal entry before the report is rendered. A missing staged entry is a Rule 7 failure surfaced to the operator, not a silent omission; the report is not done until the manifest balances against the rows it contains. Because the write itself is end-of-run and non-blocking, the manifest check is what guarantees the run intended to log everything — the commit then persists it, and a write failure after a balanced manifest degrades to logged-on-screen-plus-error rather than a gap in the record.

## Workflow integration

**Session-start sequence.** Before any screening or portfolio output, the session: (1) confirms mode per `KAPMAN_GUARDRAILS` mode discipline; (2) loads `memory/` and announces what it found; (3) if the operator pastes an export, derives the lineage ID from `exported_at`, writes the handoff under `handoffs/viewer/` or `handoffs/tradelog/`, and echoes the ID + `row_count` + `as_of` back. Only then does Pass 1 / Portfolio work begin. The memory load is orientation; the handoff write is the first staged journal action of the run.

**Interleave with the screening runbooks.**
- **Pass 1** (`PASS1_SCREENING`): each determination — Eligible, NO_TRADE, WAIT — stages a Pass 1 record carrying `source_handoff` (the run's lineage ID), the `{date, ticker, structure, pass}` key, disposition + reason, candidate zone, `decided_at`, and `underlying_ref`. Nothing writes mid-run; entries stage and commit end-of-run.
- **Pass 2** (`PASS2_VALIDATION`): each validated trade stages a Pass 2 record carrying `parent_pass1`, `{ticker, strike, expiration}`, exact spec, entry range, targets, `option_mid`, `decided_at` — and writes the immutable entry-time snapshot into `positions.md`.
- **Portfolio** (`PORTFOLIO_MGMT`): a tradelog positions snapshot is pasted, written to `handoffs/tradelog/`, and reconciled into `positions.md` (live fields only; entry snapshot untouched); the Regime-exit advisory reads that entry-time snapshot.

**Where each artifact is written.**

| Artifact | Destination |
|---|---|
| Viewer export (input) | `handoffs/viewer/<YYYY-MM>/<lineage_id>.md` |
| Tradelog snapshot (input) | `handoffs/tradelog/<YYYY-MM>/<lineage_id>.md` |
| Pass 1 records (output) | `log/pass1/<YYYY-MM>/<lineage_id>.md` |
| Pass 2 records (output) | `log/pass2/<YYYY-MM>/<lineage_id>.md` |
| Position state + entry snapshot | `memory/positions.md` |
| Standing overrides | `memory/overrides.md` |
| Active universe | `memory/watchlist.md` |

**Cross-references this runbook expects honored.**
- `KAPMAN_GUARDRAILS` — the memory-not-authority / no-persist behavioral floor; this runbook owns the mechanics.
- `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS` — owns mode detection, the session-start memory-load step, and Rule 7 (the log-manifest line).
- The §A1 / §A2 / §A3 field contracts — define *which* export fields each record carries; this runbook owns *how and where* they're written, not the field list.
- `PASS1_SCREENING` / `PASS2_VALIDATION` / `PORTFOLIO_MGMT` — the consumers that produce the staged entries.

## Legacy anchors (for legend citations and back-compat)

This is a v4.0-native runbook; the journal layer did not exist in v3.0 or v2.3, so no legacy rule IDs map here. New behavior is expressed as named anchors in the sections above, not as `DOMAIN_NNN` IDs.

## Appendix — formulas and reference tables

**Lineage ID format.** `<SRC>-YYYYMMDD-HHMM-NN`
- `SRC` — source prefix: `VS` viewer scan, `TL` tradelog snapshot.
- `YYYYMMDD-HHMM` — mirrored from the export's `exported_at`, in the timezone the export carries.
- `NN` — two-digit per-day sequence for collisions (`01` first).
- Derived from `exported_at`, never the session clock; copied verbatim across all three logs; never reformatted.

**Directory layout.**
```
kapman-journal/
├── memory/
│   ├── positions.md
│   ├── overrides.md
│   └── watchlist.md
├── handoffs/
│   ├── viewer/<YYYY-MM>/      # LOG 1 — viewer exports (INPUT → Pass 1)
│   └── tradelog/<YYYY-MM>/    # LOG 1 — tradelog snapshots (INPUT → Portfolio)
└── log/
    ├── pass1/<YYYY-MM>/       # LOG 2 — every Pass 1 row incl. NO_TRADE/WAIT
    └── pass2/<YYYY-MM>/       # LOG 3 — every Pass 2 trade w/ exact strike/exp/targets
```

**Handoff frontmatter** (per §A4):
```
kind: pass1_handoff | portfolio_snapshot
source: kapman-polygon-viewer | kapman-tradelog
lineage_id: VS-20260625-1335-01      # derived from exported_at + per-day seq
exported_at: 2026-06-25T13:35:03Z    # source-of-truth timestamp
as_of: 2026-06-25
journal_schema_version: 4.0          # THIS repo's contract version
v2_schema_version: <echoed from export>  # viewer/v2 response contract — separate namespace
row_count: 47
```

**Pass 1 record header** (per §A4): `rec_id`, `source_handoff: <lineage_id>`, `{date, ticker, structure, pass}`, disposition (Eligible | NO_TRADE | WAIT) + reason, candidate zone, `decided_at`, `underlying_ref`, `journal_schema_version`, reserved `attack_flags[]` / `invalidation_conditions[]` (empty until Stage 3).

**Pass 2 record header** (per §A4): `rec_id`, `parent_pass1: <rec_id>`, `{ticker, strike, expiration}`, exact spec, entry range, targets, `option_mid`, `decided_at`, `journal_schema_version`.

**`positions.md` record grammar (per open position).** One record per open position; `positions.md` is overwritten in place, never appended (per the write model above). The join key is two distinct labeled tokens — `instrument_key` and `account_id` — parsed from named fields, never positional header text; `PORTFOLIO_MGMT` Step 1b matches the `(instrument_key, account_id)` pair. One labeled line per field. The five entry-time regime fields and the eight SIGNAL stop/profit levels are write-once at Pass 2 (the sole no-persist exemption); the live-refresh block is overwritten in place on each Portfolio refresh.

```
instrument_key: <stable instrument id>     # join key part 1 — named field, not header text
account_id:     <account id>               # join key part 2 — entry context is account-scoped; both required to match
parent_pass2:   <Pass 2 rec_id>            # lineage to the validating Pass 2 record
journal_schema_version: 4.0

# entry-time regime snapshot — the FIVE exempt fields; WRITE-ONCE at Pass 2; never rewritten on refresh (the no-persist exemption)
entry_wyckoff_phase: <accumulation | reaccumulation | markup | distribution | redistribution | markdown | ranging_undefined>   # holds the confirmed REGIME (cycle-stage axis, per D-d), NOT the A–E phase; in a real entry never `ranging_undefined`/`UNKNOWN` (a position opens only on a confirmed, direction-aligned regime)
entry_dgpi_tier:  <Strongly supportive | Moderately supportive | Near-neutral | Weakening | Hostile>
entry_flip_zone:  <Well above flip | Near-flip | Well below flip>
entry_iv_hv_band: <Cheap | Neutral | Elevated>
entry_vol_status: <FULL | LIMITED | INVALID>

# entry-time structural riders — WRITE-ONCE at Pass 2; NON-exempt entry context (outside the five-field exemption); categorical/boolean, not numeric regime reads; each may be absent
entry_wyckoff_event: <lowercase canonical event | null>   # confirmed entry landmark from WYCKOFF "Wyckoff canonical vocabulary" (~27 events): bullish e.g. spring/shakeout/lps/sos/jac; bearish e.g. utad/ut/lpsy/sow
entry_phase:         <A | B | C | D | E | null>           # schematic phase at entry (typically C test or D entry window; null when trending, no active range). The recommended rider PORTFOLIO's D→B/A phase-regression sub-branch reads
phase_c_confirmed:   <true | false>                       # was the decisive phase-C test confirmed at entry (bullish spring/shakeout; bearish utad)? Records the post-/pre-phase-C distinction RISK applied LIVE when sizing (post-C → upper/conditional-top; pre-C → conditional floor); reserved entry context — no current reader

# eight SIGNAL stop/profit levels — WRITE-ONCE at Pass 2; named individually, one per line
stop_underlying_price:   <price>
stop_est_option_price:   <price>
stop_trail_bidask:       <value>
stop_trail_mark:         <value>
profit_underlying_price: <price>
profit_est_option_price: <price>
profit_trail_bidask:     <value>
profit_trail_mark:       <value>

option_mid: <validated-chain bid/ask midpoint at entry>   # position fact, not a regime read; write-once

# live-refresh fields — OVERWRITTEN IN PLACE on each Portfolio-mode refresh; never appended
mark:            <current option price | null>
net_qty:         <signed contract count>
unrealized_pnl:  <value | null when mark is null>
refreshed_as_of: <the refreshing snapshot's as_of>
```

Everything above the live-refresh block is write-once entry context; a refresh that touches any write-once field is a grammar violation. The exempt-snapshot Wyckoff field `entry_wyckoff_phase` holds the confirmed **regime** — one of WYCKOFF's seven canonical regimes, the cycle-stage axis (per decision D-d) — not the A–E phase; the enum is the value domain (all seven), while a real entry is constrained to the direction-aligned eligible subset, so `ranging_undefined` and the `UNKNOWN` session-state never actually populate it (a position is opened only on a confirmed, direction-aligned regime). The five regime fields plus the eight SIGNAL levels are exactly the `KAPMAN_GUARDRAILS` entry-time exemption — the guaranteed write-once snapshot. The three structural riders — `entry_wyckoff_event` (a lowercase canonical event from WYCKOFF's vocabulary), `entry_phase` (the schematic phase A–E), and `phase_c_confirmed` (whether the decisive phase-C test was confirmed at entry) — are write-once entry context too, but **non-exempt**: they are categorical/boolean structural facts, not numeric regime reads, so the numeric no-persist prohibition never reached them; they sit outside the five-field exemption and may be absent even when the snapshot is present. `entry_phase` is the recommended rider PORTFOLIO's Regime-exit advisory reads for its D→B/A phase-regression sub-branch; `entry_wyckoff_event` and `phase_c_confirmed` are recorded as entry context with no current consumer — reserved for later calibration work, the same way the Pass-1 / Pass-2 records carry reserved `attack_flags[]` / `invalidation_conditions[]` (empty until Stage 3). `WYCKOFF_v4.0.md` owns the regime, phase, and event vocabulary.

**Schema-version namespaces.** `journal_schema_version` is this repo's contract version (4.0). `v2_schema_version` is echoed verbatim from the viewer/v2 export — a separate namespace carried for join reproducibility, never conflated.
