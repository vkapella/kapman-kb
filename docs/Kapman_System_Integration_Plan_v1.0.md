# KapMan System Integration Plan — v1.0

**Status:** Approved direction, not yet built.
**Date:** 2026-06-25
**Owner:** vkapella
**Consolidates:** `KB_4.0_DESIGN.md` (memory + logging) and `KB_4.x_EDGE_LAYER.md` (precision/verify) — this document is the canonical master; the other two remain as detailed design background.

This plan unifies three previously separate threads into one program:

1. **KB 4.0** — running memory + complete Pass 1 / Pass 2 logging in a private `kapman-journal` repo.
2. **KB 4.x** — adversarial verify, tradeability gate, and a self-measuring loop layered on the 4.0 log.
3. **System integration** — stitching the existing apps (`kapman-polygon-viewer`, `kapman-tradelog`) into the KB's Pass 1/2 and Portfolio runbooks, with feedback loops.

The unifying realization: the viewer + `kapman-polygon-mcp-v2` already compute ~80% of what KB Pass 1 rebuilds by hand (regime, phase, events, bias, conviction, setup tags, invalidation, DGPI, flip, walls, IV skew), *and* a forward-log that scores MAE/MFE and predicted-vs-realized hit-rates. This is a **connect-what-exists** program, not a build-from-scratch one.

---

## 1. Goal

Close the loop the operator runs manually today — idea → watchlist → screen → trade → log → portfolio review — into a stitched flow that is **faster** (remove manual hand-offs), **more accurate** (calibrated, cross-checked, statistically gated), **more profitable** (size to measured edge; tune stops/targets to measured MAE/MFE; prune setups that don't pay), and crucially **fully remote, simple, and low-fragility**.

Design constraints locked with the operator:
- **Fully remote** — must run from iPhone, iPad, or a work browser. No dependency on a local Mac.
- **As simple as possible** — minimum new infrastructure; reuse what already exists.
- **Low fragility** — append-only, no live sync, no second engine, nothing that breaks when a machine is asleep.

---

## 2. Delivery model (locked)

| Element | Decision |
|---|---|
| **Claude surface** | **Claude Code on the web / mobile** (`claude.ai/code`). Cloud-hosted, GitHub-native, reachable from phone / iPad / work browser. Not Cowork (Mac-desktop-anchored) and not the local CLI (Mac-bound). |
| **Knowledge base** | `kapman-kb` on GitHub — read (runbooks). |
| **Journal** | **`kapman-journal`** — new **private GitHub repo**, read/write. Canonical copy lives on GitHub; pull locally when desired. |
| **Transport** | **Clipboard copy/paste**. Operator copies the viewer (or tradelog) export and pastes it into the session. |
| **Lineage ID** | **Claude mints a plain unique ID on paste** (zero app development for v1). All three logs for a run share that ID. |
| **Logs** | **Three append-only logs** in `kapman-journal`: `handoffs/`, `log/pass1/`, `log/pass2/`. New files per run; nothing overwritten. |
| **Inline echo** | Claude prints the lineage ID in the header of every Pass 1 / Pass 2 table it renders, so lineage is visible in-session, not just in the file. |
| **Integrity** | Git commits provide tamper-evident, timestamped content hashes for every logged output — output integrity "for free," with no hashing asked of Claude. |

### Why this is low-fragility
- The operator (a human) and Claude only ever **echo** the lineage ID — never compute a hash. Echoing a short unique ID is reliable; hashing in-chat is not.
- Logs are **append-only with unique IDs**, so the GitHub clone→commit→push round-trip is **conflict-free** (each run adds new files).
- **Nothing depends on the operator's Mac** — KB, journal, viewer, tradelog, brokers are all cloud/web.
- Two residual operational risks, both cheaply mitigated:
  - *Echo fidelity* — keep the ID short and human-checkable (e.g., `VS-20260625-0935-7f3a`); runbook rule: *copy the lineage ID verbatim; never regenerate or reformat it.*
  - *Paste integrity* — the payload header carries `row_count` + `as_of`; Claude echoes them back ("received `VS-…`, 47 rows, as_of 2026-06-25") so the operator eyeballs against what the viewer exported.

### Deferred / noted
- **ID-minting can move into the viewer later** (so the ID rides inside the clipboard at source) — a small v2 viewer feature; not required for lineage to work.
- **Broker CSV → tradelog import** is the one step best done at a full browser (iOS file download→upload is awkward); it is occasional, not per-session.

---

## 3. The unified spine — one program, three stages

| Stage | What | New server? | Absorbs |
|---|---|---|---|
| **1 — Human-mediated** | KB hygiene; v4.0 memory + complete logging in `kapman-journal` (MD, written by the session); contracts authored; tiered auto-accept applied; pilot | **No** | **KB 4.0** + integration Phase 0 |
| **2 — Smoother hand-offs** | Optional viewer "best-Wyckoff Pass-1 export" button; optional viewer-side ID minting; marks→excursions job kept fresh | Minor app polish | integration Phase 1 |
| **3 — Precision + closed loop** | Adversarial verify + tradeability gate inside Pass 2; self-measuring loop + realized-performance feedback → `SYSTEM_PARAMS` tuning | No new server | **KB 4.x** + integration feedback half |

The operator's stated sequence — *human-mediated first, then smoother tooling, then precision* — maps exactly onto Stage 1 → 2 → 3. KB 4.0's whole memory+logging layer **is** Stage 1: it is MD files the session writes to the `kapman-journal` working dir, no server required.

---

## 4. The three logs + lineage (backtest/forward-test backbone)

```
kapman-journal/
├── memory/                 # mutable session state (overwritten)
│   ├── positions.md        # open positions + entry-time regime snapshot  ← Portfolio entry-context
│   ├── overrides.md        # standing operator overrides
│   └── watchlist.md        # active universe
├── handoffs/2026-06/       # LOG 1 — viewer/tradelog exports, lineage-stamped (INPUT)
└── log/
    ├── pass1/2026-06.md    # LOG 2 — every Pass 1 row incl NO_TRADE/WAIT (OUTPUT)
    └── pass2/2026-06.md    # LOG 3 — every Pass 2 trade w/ exact strike/exp/targets (OUTPUT)
```

**Lineage chain** (one shared ID + parent links):
```
handoff_id ──▶ Pass1 entry (records source_handoff_id + own rec_id)
                   └──▶ Pass2 entry (records parent_pass1_rec_id + own rec_id, exact strike/exp)
                             └──▶ tradelog execution (matches on {ticker, strike, expiration, entry date})
```

**Record discipline** (inherited from `KB_4.0_DESIGN.md` §4):
- Each entry carries a structured header block shadowing `REPORT_FORMAT_v3.0` — readable now, machine-parseable later. **No new schema invented.**
- Join keys baked in now: `rec_id`, `{date, ticker, structure, pass}`, and for Pass 2 `{ticker, strike, expiration}`.
- **Decision anchor:** `decided_at` + `underlying_ref` at decision (Pass 2 also logs `option_mid`) so the viewer forward-eval can later measure what a ticker did after a yes/no/refusal.
- Reserved nullable arrays `attack_flags[]` / `invalidation_conditions[]` (empty until Stage 3) and `schema_version` on every record.

**What this enables:**
- **Backtest** — join the three logs by lineage; outcomes come from the viewer forward-log or tradelog marks.
- **Forward-test** — from the decision anchor forward, track what the ticker did (underlying anchor from the viewer handoff; option-leg anchor `option_mid` captured at Pass 2).
- **Reproducibility** — pin a calibration run to an exact set of handoff IDs + git commit SHAs.

---

## 5. The interlock rule (KB changes sync with the tooling)

Two rules keep the KB and the tools shipping locked together and prevent a recurrence of the disconnected-`kapman-mcp` problem:

1. **Dual-path clauses, one contract.** Every KB clause that consumes tool data is written once against a versioned field contract, with two execution paths:
   > "Consume the operator-pasted viewer export per the field contract" (Stage 1) — *and later* — "pull the same fields from the viewer export button" (Stage 2).
   Same fields, same `schema_version`; only the fetcher changes. So Stage 1 KB edits already interlock with Stage 2 tooling.
2. **No-dangling-capability rule.** No KB runbook may reference a tool field that the current contract does not provide. If it is not in the contract, the runbook falls back to operator-paste, explicitly labeled. The KB can never again point at a capability the runtime cannot reach.

---

## 6. Priority Workflow 1 — Viewer → Pass 1 / Pass 2

**Goal:** the viewer watchlist becomes the screening front-end; the session consumes structured Wyckoff/dealer/IV instead of rebuilding it by hand.

**Flow:**
1. Filter the viewer to the best-Wyckoff candidates for long calls / CSPs (existing saved-view + column filters).
2. Copy the export to clipboard → paste into a Claude Code session.
3. Claude mints the lineage ID, writes the handoff to `kapman-journal/handoffs/`, and treats the rows as the candidate list + pre-computed pipeline reading.
4. **Tiered-by-confidence auto-accept** (the operator's chosen protocol) resolves each ticker's Wyckoff status from the viewer's confidence/cross-check columns — re-pointing WYCKOFF's existing `pipeline-accepted` / `pipeline-flagged` machinery at the live Polygon-v2/viewer engine:
   - **Auto-accept** when `regime_confidence ≥ τ_high` AND `phase_confidence ≥ τ_high` AND `dealer_consistent` AND `volatility_consistent` AND flip unambiguous.
   - **Propose-confirm** when confidence ∈ `[τ_low, τ_high)` OR any cross-check inconsistent.
   - **Conservative/UNKNOWN** below `τ_low` or on degraded data.
5. KB Pass 1 runs its trigger sequence (Wyckoff veto → dealer-timing veto → spread-mandate); the **earnings screen (FMP)** stays in the KB.
6. Eligible set → **Pass 2 unchanged**: re-fetch **Schwab** dealer metrics (flip authority) and **Schwab ATM IV** (spread-mandate) and validate the live chain. The viewer's v2/Polygon flip & IV are **Pass-1 triage only** — the Schwab-at-Pass-2 boundary is preserved exactly as the KB already mandates.

Net KB change is small: PASS1 gains a viewer-ingest candidate source + the §A1 map; WYCKOFF gains the live-source tier gate (`τ_high`/`τ_low` in `SYSTEM_PARAMS`).

---

## 7. Priority Workflow 2 — Trade log → Portfolio mode

**Goal:** open positions flow from the tradelog into Portfolio advisories without re-keying, and the Regime-exit advisory actually runs (today it usually can't).

**Flow:**
1. Pull open positions from tradelog (positions snapshot) → symbol, underlying, optionType, strike, expiration, netQty, costBasis, account + live mark/unrealized P&L; `LotExcursion` (`--include-open`) supplies **live MAE/MFE** per open lot.
2. Map to the KB position-context schema (§A2).
3. **Entry-context home = `kapman-journal/memory/positions.md`** (per KB 4.0), *not* a new tradelog table. At Pass 2 validation the session writes the entry-time regime snapshot (Wyckoff phase, DGPI tier, flip-zone, IV/HV band, vol-status) + the eight SIGNAL Stop/Profit alert levels into `positions.md`. This is the bridge that lets Portfolio's Regime-exit advisory evaluate decay.
4. Portfolio mode runs its sequence: current-regime re-fetch → four Regime-exit branches (now evaluable) → DTE decay → exit-trigger proximity → portfolio view.
5. **MAE/MFE as a live input** (new): feed `LotExcursion.maePct/mfePct` into the advisory — e.g., "already taken −12% heat vs your −15% stop" / "gave back 8% from peak MFE."

---

## 8. Feedback & self-correction (Stage 3 spine)

Two complementary streams; using both is what makes the system self-correcting.

- **Stream 1 — forward-test accuracy** (viewer forward-log): "was the *signal logic* right, on paper?" Scorecards by `setup_tag / context / phase / conviction / ADX / HV` with `hit_base%`, `median MAE`, regime-flip return, and predicted-vs-realized calibration — each with **N + 95% Wilson CI + readability** (`readable` N≥20, `directional` 10–19, `noise` <10). Reads the logged decision anchors, including refusals (false-negative measurement).
- **Stream 2 — realized performance** (tradelog): "did I actually make money, after execution/slippage/timing?" Matched-lot realized P&L/outcome/hold-days; `LotExcursion` MAE/MFE; setup-level winRate/expectancy; account-level return/drawdown/profit factor.

**Calibration/Review mode** (new 4th KB mode + new T2 runbook) periodically:
1. Ingests both streams.
2. Runs **signal→outcome attribution** (join logged recs to tradelog executions by `{ticker, strike, expiration, entry}`): did the realized trade behave like the forward-test predicted? Divergence splits the diagnosis into **model problem vs execution problem** — the single most useful feedback the system can produce.
3. Proposes parameter deltas to `SYSTEM_PARAMS` (`τ` thresholds, RISK sizing bands, SIGNAL stop/target bands), **gated by readability (N≥20) and operator approval** — never auto-applied.

**Concrete first correction:** the viewer's own research found **conviction does NOT rank edge**, yet the KB treats conviction as a first-class decision input. Stop letting conviction drive sizing; size to measured per-setup expectancy instead.

---

## 9. Relationship to KB 4.0 / KB 4.x (dependency map)

These are not competitors — they are layers of one loop, and they are mutually dependent (design-time simultaneous, build-time sequential):

- **Integration depends on 4.0:** Workflow 2's entry-context lives in 4.0's `positions.md`; the feedback loop can only measure decisions 4.0 logged; signal→outcome attribution needs 4.0's join keys; `τ` self-tuning needs the logged confirmation status.
- **4.0 depends on integration:** 4.0 *names* the `positions.md` snapshot fields but the integration contract says *where each is sourced*; 4.0's deferred "closed loop" (§6) **is** the integration feedback design; 4.0's reserved `attack_flags[]`/anchor fields are filled by 4.x + the self-measuring loop; logging every NO_TRADE/WAIT only pays off through false-negative measurement.
- **Shared schema:** 4.0's log record format and the integration contracts (§A1/§A2/§A3) are **one versioned artifact** — the fields the handoff carries must equal the fields the logs record, or the join breaks.

Therefore: build order is **4.0 (Stage 1) first**, *because* it was co-designed with the integration plan. One program, one plan — this document.

---

## 10. Build sequence + decision gates

- **Stage 1 — Contracts & pilot (no new infra; fully remote).**
  - KB hygiene (§12).
  - Stand up `kapman-journal` private GitHub repo + `memory/`, `handoffs/`, `log/` scaffolding; connect GitHub to Claude Code on the web.
  - New T2 runbook `JOURNAL_MGMT_v4.0.md` (session-start memory load; lineage-ID minting on paste; three-log write; inline echo; precedence: live/broker input always overrides memory; numeric regime reads never persisted).
  - Author the §A1/§A2/§A3 contracts as dual-path clauses (paste now, tool later), all `schema_version`'d.
  - Implement tiered auto-accept in WYCKOFF; define `τ_high`/`τ_low` in `SYSTEM_PARAMS`.
  - Capture entry-context into `positions.md` (Gap closed via journal, not tradelog).
  - **Pilot:** viewer→Pass 1 dry-run + tradelog→Portfolio dry-run, from a browser.
  - **Gate:** auto-accept tiers feel right; entry-context captures what Portfolio needs; logging is complete end-to-end.
- **Stage 2 — Smoother hand-offs.** Optional viewer "best-Wyckoff Pass-1 export" button + optional viewer-side ID minting; stand up the marks→excursions job so MAE/MFE stays fresh. **Gate:** one-click export replaces manual filtering; first calibration has fresh excursions.
- **Stage 3 — Precision + closed loop.** 4.x adversarial verify (flag-don't-kill) + tradeability gate inside Pass 2; self-measuring loop + realized-perf feedback → `SYSTEM_PARAMS` tuning. **Gate:** first defensible parameter delta produced, N≥20-gated.

---

## 11. Archive + version cutover (from KB 4.0 §5)

When Stage 1 KB edits land: snapshot current v3.0 `llm_runtime/` + `engineering_only/` into `archive/v3.0/` (read-only) + a `v3.0` git tag at the cutover commit; the live `llm_runtime/` becomes v4.0; INDEX/CHANGELOG note the archival. This is mechanical work per AGENTS.md and stays autonomous; the substantive runbook authoring (JOURNAL_MGMT, WYCKOFF tier gate, the contracts) is human-in-the-loop.

---

## 12. Governance / hygiene (fold into Stage 1)
- **Naming:** reconcile `kapman-mcp` ↔ `kapman-trader` across the KB + memory; state the canonical live source for pipeline readings (today: Polygon v2 / viewer). `kapman-mcp` is the disconnected MCP surface of the `kapman-trader` server — not dead code.
- **PASS2 review:** bump from v3.0.0; reconcile with v2 `price_targets`/calibration; reaffirm Schwab IV/flip authority; align chain-quality gate (`isChainTruncated:false` ↔ v2 `volatility_chain_truncated`).
- **HTML/markdown default:** reconcile retained memory (HTML-default) with Rule 6 (markdown-default; Rule 6 wins).
- **Engineering-only MCP reference tier:** the scaffolding placeholders are the right home for the live-tool→KB-field contract; fill as contracts solidify.

---

# SPEC APPENDIX

## §A1 — Viewer/v2 → KB Pass 1 field contract
| Viewer/v2 field | KB Pass 1 consumer | Notes |
|---|---|---|
| `symbol` | candidate ticker | work-queue item |
| `regime`, `regime_confidence` | Wyckoff reading + tier gate | drives auto-accept vs flagged |
| `phase`, `phase_confidence` | Wyckoff reading + tier gate | A–E; null when trending |
| `last_event`, `last_event_date`, `setup_tags` | confirmed event / setup class | e.g. `phase_c_spring_long` |
| `invalidation_level` | SIGNAL Stop anchor | structural stop |
| `dgpi`, `gamma_flip`, `position_vs_flip`, `net_gex`, `gex_slope`, `dealer_confidence` | dealer-timing veto (Pass-1 triage) | **Schwab re-fetch at Pass 2** |
| `iv_skew_25delta`, `average_iv`, `historical_volatility` | IV/HV band + spread-mandate Pass-1 firing | labeled *Needs chain validation* |
| `dealer_consistent`, `volatility_consistent` | cross-check gate / conviction trim | from v2 `cross_checks` |
| `pt_up_*`, `pt_down_*` + `*_prob` | candidate zone + expectancy context | calibrated hit-rates |
| `price`, `as_of` / `data_through` | decision anchor + freshness label | `price` = underlying_ref anchor |

## §A2 — Trade log → KB Portfolio position-context contract
| KB position-context field | Source | Status |
|---|---|---|
| ticker / structure / direction / strikes / expiration | tradelog OpenPosition | direct |
| entry date / entry price / size | tradelog Execution/MatchedLot; costBasis, netQty | direct |
| current option price / unrealized P&L | tradelog PositionSnapshot.mark | direct |
| live MAE / MFE | tradelog LotExcursion.maePct/mfePct (`--include-open`) | **new KB input** |
| entry-time Wyckoff phase / DGPI tier / flip-zone / IV-HV band / vol-status | **`kapman-journal/memory/positions.md`** (written at Pass 2) | journal, not tradelog |
| 8× Stop + Profit alert levels | **`positions.md`** (SIGNAL output captured at Pass 2) | journal, not tradelog |
| exit date / exit price / realized P&L | tradelog MatchedLot / realizedPnl | direct (closed) |

## §A3 — Feedback contract
- Viewer forward-log evaluate → scorecards (`by_setup_tag/context/phase/conviction/adx/hv`), calibration, MAE/MFE, regime-flip returns, each with N + Wilson CI + readability.
- Tradelog setups (winRate/expectancy/avgHoldDays), excursions (MAE/MFE), overview summary (profit factor, drawdown, return).
- Calibration/Review mode joins both on `{ticker, decision date}` / `{ticker,strike,expiration,entry}` → proposes `SYSTEM_PARAMS` deltas, gated by N≥20 + operator approval.

## §A4 — Log record shapes (illustrative)
**Handoff frontmatter (`handoffs/`):**
```
kind: pass1_handoff | portfolio_snapshot
source: kapman-polygon-viewer | kapman-tradelog
lineage_id: VS-20260625-0935-7f3a   # minted by Claude on paste
exported_at: 2026-06-25T13:35:03Z    # not part of identity
as_of: 2026-06-25
schema_version: 4.0
row_count: 47
```
**Pass 1 entry header (`log/pass1/`):** `rec_id`, `source_handoff: <lineage_id>`, `{date,ticker,structure,pass}`, disposition (Eligible/NO_TRADE/WAIT) + reason, candidate zone, `decided_at`, `underlying_ref`, `schema_version`, reserved `attack_flags[]`/`invalidation_conditions[]`.
**Pass 2 entry header (`log/pass2/`):** `rec_id`, `parent_pass1: <rec_id>`, `{ticker,strike,expiration}`, exact spec, entry price range, targets, `option_mid`, `decided_at`, `schema_version`.

## §A5 — KB edit list (Stage 1 unless noted)
- **New T2 runbook** `JOURNAL_MGMT_v4.0.md` — memory load, lineage minting, three-log write, inline echo, precedence.
- **New T2 runbook** `PERFORMANCE_FEEDBACK`/`CALIBRATION` (Stage 3) — dual streams, attribution, param-delta proposals.
- **`KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS`** — add 4th mode (Calibration/Review); session-start memory-load step; Rule 7 "log manifest" line.
- **`WYCKOFF`** — re-point pipeline-reading source to live viewer/v2; define tier gate; decouple `pipeline-accepted` from the disconnected `kapman-mcp`.
- **`PASS1`** — add viewer-ingest candidate source + §A1 map; preserve Schwab-at-Pass-2 boundary.
- **`PASS2`** — version bump; reconcile v2 price-targets/calibration; reaffirm Schwab IV/flip authority; chain-quality gate alignment; capture entry-context + `option_mid` at validation.
- **`PORTFOLIO_MGMT`** — add §A2 ingestion contract; add MAE/MFE live input; read entry-context from `positions.md`.
- **`SYSTEM_PARAMS`** — add `τ_high`/`τ_low`, readability N floor, calibration cadence, MAE/MFE stop/target tuning params.
- **`SIGNAL`** — tie Stop/Profit bands to MAE/MFE feedback (Stage 3). **`RISK`** — tie sizing bands to per-setup expectancy (Stage 3).
- **New guardrail** — "Memory is convenience, not authority; live operator/broker input and data-honesty always win; numeric regime reads are never persisted as authoritative."

---

## 13. Verification / pilot (Stage 1, no build, from a browser)
1. **Viewer→Pass 1 dry-run:** filter a 10–15 ticker watchlist in the viewer, copy/paste into a Claude Code web session, apply §A1 + the tier rule; confirm the eligible set matches a manual propose-confirm run on the same tickers (catch `τ` mis-sets). Confirm the handoff + pass1 logs land in `kapman-journal` with a shared lineage ID and the ID echoes in the table header.
2. **Boundary check:** confirm Pass 2 re-fetches Schwab dealer + ATM IV and used viewer flip/IV only as Pass-1 triage.
3. **Trade log→Portfolio dry-run:** pull a positions snapshot; map via §A2; observe the Regime-exit advisory require entry-context → validates the `positions.md` bridge. Re-run with a hand-filled `positions.md` to confirm the advisory lights up.
4. **Feedback smoke test:** run the viewer forward-log; confirm scorecards carry N + CI + readability; pull setup expectancy; sketch one `SYSTEM_PARAMS` delta (e.g., sizing for the best/worst setup) gated by N≥20.
5. **Remote check:** run steps 1 and 3 entirely from an iPad / work browser to confirm zero Mac dependency.
