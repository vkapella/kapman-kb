# KapMan KB Changelog

## 2026-07-20 — Earnings source-of-authority: Finnhub MCP validates earnings exposure (closes #93)

### Changed — `llm_runtime/` (runtime rule additions; operator must re-upload to project knowledge)

**`llm_runtime/SIGNAL_v4.0.md`** (`4.0.0 → 4.0.1`): Heuristic 0 names its data source —
`Finnhub MCP Server:get_earnings_calendar`, query window = screening date → +`EARNINGS_CAUTION_DAYS`
+ 7d buffer, date-only calendar-day counts with session hour (`bmo`/`amc`/`dmh`) as context.
Operator-declared dates take session precedence (labeled *declared*); model-internal knowledge is
never an earnings source. Two outcome changes: a tool query returning no date in-window is a
**validated absence** ("No earnings within [N]d — validated via Finnhub [timestamp]"), and a tool
that is unavailable **escalates to the operator-approval WAIT gate** — the prior "no date → veto
does not fire, 'Earnings date not provided'" silent pass is retired.

**`llm_runtime/PASS1_SCREENING_v4.0.md`** (`4.0.1 → 4.0.2`): Step-0 prose, the §A1 absent-field
row, and the workflow table replace "KB-side lookup" with the named Finnhub fetch (one call per
candidate, within the shared 60/min free-tier budget at the 30-symbol batch cap); unavailable-source
candidates route to the operator-gated WAIT.

**`llm_runtime/PASS2_VALIDATION_v4.0.md`** (`4.0.0 → 4.0.1`): new heuristic "The earnings screen is
re-run at Pass 2" — same contract as Pass 1, applied at validation time per the re-fetch-at-decision-time
doctrine that already governs dealer metrics.

**`llm_runtime/PORTFOLIO_MGMT_v4.0.md`** (`4.0.0 → 4.0.1`): new Step 5b + principle block
"Earnings-exposure advisory" — every Portfolio run fetches each open position's next earnings date
and flags positions whose expiration falls on or after it ("holds through earnings unless closed or
rolled"). Non-blocking, fires at any distance, stacks with DTE decay and Regime exit advisories;
Finnhub-unavailable is labeled data-absent, never silently skipped. Added as item (6) to the Step 7b
self-audit.

**`llm_runtime/SYSTEM_PARAMS_v4.0.md`** (`4.0.0 → 4.0.1`): `EARNINGS_BLOCK_DAYS` /
`EARNINGS_CAUTION_DAYS` notes name the source and the fetch-window role; consuming-files columns
gain PASS2 (both) and PORTFOLIO_MGMT (caution). Values unchanged (7 / 21).

**`llm_runtime/KAPMAN_GUARDRAILS_v4.0.md`** (`4.0.0 → 4.0.1`): *Near event risk* label definition
names Finnhub (or operator declaration) as the only earnings-date sources, parallel to the
validated-Schwab-data rule for strikes.

### Added — `engineering_only/`

**`engineering_only/FINNHUB_MCP_REFERENCE_v4.0.md`** (new): tool-surface contract for
`Finnhub MCP Server` — endpoint parameters, response shape, `bmo`/`amc`/`dmh` semantics, error
shape, and the free-tier constraints that matter to the runtime (60 calls/min shared budget,
US scope, ADR estimate-currency caveat — dates only are consumed). PIPELINE_010 precedent.

Provenance: kapman-finnhub-mcp-server deployed to production 2026-07-19; free/premium split
verified against the Finnhub docs' embedded Swagger spec; operator approved the proposal and its
four decision points (unavailable→operator gate, Pass-2 re-check, date-only counts, any-distance
portfolio advisory) 2026-07-20.

## 2026-07-14 — Session entry: verify kapman-journal on disk before announcing "not loaded" (closes #92)

### Changed — `llm_runtime/` (runtime rule addition; operator must re-upload to project knowledge)

**`llm_runtime/KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md`** (`4.0.0 → 4.0.1`): Step 3 of the
session entry sequence ("Load journal memory and announce") gains a new paragraph — whether
`kapman-journal` is attached is determined by a direct filesystem check (read/list the repo path),
never by consulting a session's enumerated list of working directories in isolation, and this
check runs before the "not loaded" announcement, not after. Provenance: a live Pass 1 screening
session (2026-07-14) incorrectly announced the repo as unattached — it checked only the harness's
working-directory list, not the filesystem — and skipped session-start memory load and journal
writes as a result, corrected retroactively mid-session once the operator flagged that the repo
was in fact present and readable. Drafted turn-by-turn with operator, approved as-is 2026-07-14.

**`llm_runtime/JOURNAL_MGMT_v4.0.md`** (`4.0.3 → 4.0.4`): the parallel session-start heuristic
("At session start, the runbook loads `memory/` as starting context...") gains a one-line
cross-reference to the same filesystem-check rule, so it's visible from both files rather than
only the orientation file.

## 2026-07-03 — Pass-1 spring-first priority ordering: eligible set, flagged queue, report rows (closes #90)

### Changed — `llm_runtime/` (runtime rule addition; operator must re-upload to project knowledge)

**`llm_runtime/PASS1_SCREENING_v4.0.md`** (`4.0.0 → 4.0.1`): new principle block "The eligible set and the
flagged-review queue are ordered by entry cohort — spring-cohort first." Spring cohort = accumulation-family regime +
confirmed phase-C `spring`/`shakeout` (bearish mirror: distribution-family + confirmed `utad`). Attention-ordering
only — no change to tier-gate thresholds, vetoes, dispositions, sizing bands, or structures. Provenance: pinned
2026-07-02 economics study (docs/ECONOMICS_STUDY_2026-07-02.md; v2 docs/economics_2026-07-02.md) — spring-entry long
calls are the only CI-positive entry cohort on the broad backtest universe. KB-side pilot; viewer promotion of the
deterministic cohort tag is a September 2026 re-evaluation decision (drafted turn-by-turn with operator, approved
as-is 2026-07-03).

**`llm_runtime/REPORT_FORMAT_v4.0.md`** (`4.0.0 → 4.0.1`): new block "Screening-table rows render in entry-cohort
order" — Eligible spring-cohort first then descending confidence, WAIT rows next (cohort-first within the group),
NO_TRADE last; presentation only.

## 2026-07-02 — Pipeline-feed spec: record viewer screen v1.1 — stale-snapshot force-flag + ISO macro as_of (closes #87)

### Changed — engineering-only contract tracking (no runtime change; `llm_runtime/` untouched)

**`engineering_only/PIPELINE_FEED_VIEW_SPEC_v4.0.md`** (`4.0.0 → 4.0.1`): records viewer screen **v1.1** (viewer #54,
commit 1aa40ea — shipped off the Stage-F SATS finding). SCREEN_VERSION reference 1.0 → 1.1; the "all four hard
force-flags" tier cell (previously an overstatement — v1.0 implemented three) is now accurate with a v1.1 provenance
note; the envelope paragraph notes `macro_context.as_of` is ISO 8601 since v1.1 (v1.0 leaked the header's epoch float);
a new contract-readings bullet records the **stale-snapshot force-flag** semantics — viewer-pinned
`STALE_SNAPSHOT_MAX_LAG_DAYS = 4` calendar days (echoed in `screen_thresholds`, deliberately not a SYSTEM_PARAMS name),
absent/unparseable dates never fire it, and **the KB's own §A1 ingest freshness check remains the authoritative layer**
(the screen flag is defense-in-depth). Also recorded viewer-side that session: the viewer's `KbParityTests` drift guard
repointed to `SYSTEM_PARAMS_v4.0.md` after the #78 rename sweep (it had been silently skipping).

## 2026-07-02 — Tooling: harden `verify_anchors.sh` against a vacuous pass when `rg` is unavailable (closes #86)

### Changed — validation script only (no KB content)

`scripts/verify_anchors.sh`: the ID-extraction pipeline (`xargs rg … || true`) silently produced an **empty ID set and a
"passed" verdict** when no `rg` binary was on PATH (xargs can't invoke shell-function shims; exit 127 was swallowed).
Now: prefers `rg`, falls back to `grep -hoE` (same 107 IDs verified); guards the xargs exit status (0/1-BSD/123-GNU
no-match OK, 126/127/signals hard-fail); refuses to pass when archive markdown exists but zero IDs extract; per-ID INDEX
lookup switched to plain `grep -Fq`. Output now names the extractor. Tested: real pass (107 mapped), mixed
files-without-IDs pass, missing-ID failure, zero-extraction refusal.

## 2026-07-02 — v4.0 cutover complete — Stage F closeout: pilots pass, `_v3.0 → _v4.0` rename sweep lands (closes #78)

### Stage F pilots (validation, no KB edits required)

- **Structural validate — PASS.** `verify_frontmatter` + `verify_anchors` pass; anchor parity independently re-confirmed
  via grep (107 legacy rule IDs in `archive/`, all mapped in `INDEX.md`) after finding that `verify_anchors.sh` silently
  passes on an empty ID set when `rg` is unavailable (hardening tracked separately; not a parity break).
- **BEARISH fixture pilot — PASS, zero KB must-fixes.** Operator-produced Swing Long Put export
  (`kapman-journal` handoff `VS-20260702-1225-01`, 75 rows, `screen_version 1.0`). Every fixture value class reconciles
  with the committed KB: `screen_thresholds` match SYSTEM_PARAMS by name and value (τ 0.70/0.45, IV-HV 1.20, DGPI 30/10);
  gating `g = min(regime_confidence, phase_confidence)` matches WYCKOFF; all four hard force-flags fire on the re-keyed
  string values (`"conflict"`), including SOW-gated markdown; FLAGGED→WAIT and ESTIMATION→WAIT match the #84 pin on all
  47 WAIT rows; dealer `invalid`→veto (4 NO_TRADE rows) and `low`→floor-narrowing match SIGNAL/RISK verbatim; adverse-tier
  DGPI mirror-narrowing→floor matches DEALER's direction-relative read; `conditional-top` sizing (URA: `distribution`,
  post-phase-C) matches RISK's band; `iv_hv_status` values (`OK`/`ATM_FALLBACK_BAND`/`INSUFFICIENT_CONTRACTS`) match
  VOLATILITY's derived-status contract; spread-mandate fires at ≥ 1.2 (BABA/CEG/TRI). Macro card (SPY DGPI −93.83,
  short-gamma, flip unknown) reads mixed-conservative per PASS1 Step 1 — hostile-macro stays bullish-scoped, long puts
  aligned. **Divergence noted (producer-side, not KB):** the screen ACCEPTed the stale SATS row (`as_of` 2026-06-23 in an
  `as_of` 2026-07-01 export) — the KB's stale-snapshot force-flag catches it at ingest; a per-row freshness check is a
  candidate viewer follow-up. Coverage gaps (fixture, not KB): `msow`/`ice_break` events, `ranging_undefined` regime, and
  the full bearish-mirror dealer veto (DGPI ≥ +30 **and** well-above-flip on an ACCEPT-tier row) were not exercised.
- **BULLISH golden regression — PASS at the persisted summary level.** `VS-20260629-1348-05` (73 rows): all persisted
  tier/disposition/structure rows conform to the reconciled gate and disposition rules (raw per-row JSON was not
  persisted for the pilot handoffs; the deep read happened live in the #82 pilot, which the #78 slices reconciled to).
- **Estimation-path regression — PASS.** All `g < τ_low` rows (FSLR 0.27, NNE 0.42, ED 0.20) route ESTIMATION→WAIT,
  matching the estimation-path + operator-absent pins.

### Changed — end-of-Stage-1 `_v3.0 → _v4.0` rename sweep (mechanical, autonomous per AGENTS.md)

- **All 25 live files renamed** `_v3.0 → _v4.0` (git-mv, history preserved): 15 `llm_runtime/` (14 .md + the Pass-1 HTML
  template) + 10 `engineering_only/` .md. `JOURNAL_MGMT_v4.0.md` already carried the v4.0 name.
- **`kb_version` re-based to the 4.0 line:** renamed files reset `3.0.x → 4.0.0` (scaffolding placeholders
  `3.0.0-alpha → 4.0.0-alpha`); `JOURNAL_MGMT` keeps its running `4.0.3`. `file_last_updated → 2026-07-02` on renamed files.
- **Cross-references updated** in `llm_runtime/`, `engineering_only/`, and `INDEX.md` (`_v3.0.md/.html → _v4.0.md/.html`);
  version-pinned citations re-pinned to the live line (`REPORT_STYLE_v3.0.3`/`REPORT_FORMAT_v3.0.x` → `_v4.0.0` in the HTML
  template and PASS1). Historical/lineage mentions of v3.0 (v2.3→v3.0 migration notes, "net-new v3.0" rows) intentionally
  preserved. `archive/`, `CHANGELOG.md` history, and `docs/` plan documents untouched.
- **`INDEX.md`:** Version status rewritten to the completed-cutover state (v4.0 complete, Stage 1 closed 2026-07-02);
  Stage-1b authoring bullets re-marked historical; file directory re-headed "v4.0 file directory (live)" with all rows at
  `_v4.0`; `JOURNAL_MGMT_v4.0.md` added to the directory table (T2 runbook — previously tracked only in Version status).

### Still open after Stage 1 (carried forward, do not block the cutover)
P0-3a (RISK↔PASS2 Weak-chain), P0-3b, P0-4 (positions.md written at validation not fill), P0-5 (CSP "regime-aligned"
overclaim), P1-10, P1-11; deferred pilot-safe IV-rank dormancy pass + absolute-IV guard (phase-2 IV-history).

### Verification
`verify_frontmatter` + `verify_anchors` pass post-rename; grep re-check: no `_v3.0` filename references remain in
`llm_runtime/`/`engineering_only/`/`INDEX.md`; all live frontmatter `kb_version` on the 4.0 line; archive untouched.

## 2026-07-02 — SOW-staleness decision — resolve the SOW-recency window as a judgment call, not a parameter (closes #85)

### Changed — WYCKOFF SOW-gated-markdown recency clarification (substantive; HITL, operator-decided)

**`WYCKOFF_v3.0.md`** (`3.0.9 → 3.0.10`): the `last_event_date`/SOW paragraph now separates the flag's two halves on the
deterministic viewer-ingest path — the **absence** half is code-detectable (the viewer screen implements it: a `markdown`
with no `sow` in `last_event`/`setup_tags` force-flags), the **staleness** half stays a run-level freshness judgment, not a
pinned numeric window. Operator decision (#85): do NOT parameterize it. Rationale recorded inline — the stale-snapshot flag
(`as_of`/`data_through`) already catches a whole-reading gone stale, `structure_conflict` catches a `markdown` label in an
accumulation structure, `weekly_agrees` catches the higher-timeframe turn, and a present-but-old `sow` under a *current*
snapshot is the normal `markdown_continuation` shape (markdowns don't re-print a `sow` each bar), so a recency window would
re-flag healthy continuations. A discretionary too-old-`sow` call remains available to the operator; it is not automatic.

**`engineering_only/PIPELINE_FEED_VIEW_SPEC_v3.0.md`** (`3.0.1 → 3.0.2`): the SOW-recency exclusion note and status row
change from "pending a SYSTEM_PARAMS pin" to the resolved decision (not parameterized; staleness is a run-level judgment).

### Verification
Structural — `scripts/verify_frontmatter.sh` + `scripts/verify_anchors.sh` pass; archive untouched. No SYSTEM_PARAMS
change (that is the point of the decision). No viewer code change — the shipped absence-only detector is the faithful
implementation; the viewer's `pass1_screen.py` docstring exclusion note is updated to cite the resolved decision.

## 2026-07-01 — Deterministic Pass-1 screen reconciliation — viewer ships the screen; §A1 consumes the disposition; three pilot-surfaced pins land (#84)

### Changed — §A1 screen ingest + operator-absent disposition pin (substantive; HITL, operator-directed; viewer #53 shipped the implementation)

The viewer now computes the deterministic Pass-1 screen per row (`kapman-polygon-viewer` #53, `backend/app/pass1_screen.py`,
`SCREEN_VERSION 1.0` — the CODE_VS_JUDGMENT_ASSESSMENT recommendation, Integration Plan Stage 2 accelerated).
**`PASS1_SCREENING_v3.0.md`** (`3.0.12 → 3.0.13`): the §A1 ingest map adds the five `screen_*` fields — consumed as the
pre-computed tier-gate + trigger-sequence result for the long-premium strategies (PASS1 *verifies* rather than re-derives;
Step-0 earnings, the Step-1 macro gate, and flagged/estimation resolution stay runtime-owned; CSP rows carry a long-premium
read, not a CSP verdict; absence degrades to raw-field derivation). New envelope paragraph: `screen_version` /
`screen_thresholds` (SYSTEM_PARAMS governs on disagreement — drift flags, dispositions re-derived) and `macro_context`
(seeds the macro gate like a pasted SPY reading; stale/absent → live fetch, never assumed-supportive). **Pinned the
operator-absent FLAGGED disposition** (Pilot Lessons §8, the model-matrix agreement gap): a *pending* flagged/estimation
reading — operator not yet resolved, incl. unattended runs — is **WAIT**, never NO_TRADE; NO_TRADE on Wyckoff grounds
requires a resolved reading (confirmed-and-vetoed, or operator declined/skipped → UNKNOWN). Both degraded-input tables gain
the pending row.

### Changed — SIGNAL: near-flip prose aligned to the firing-condition table + phase-C evidence set pinned (substantive)

**`SIGNAL_v3.0.md`** (`3.0.7 → 3.0.8`): (1) the dealer-timing veto prose sentence "only when near-flip combines with
weakening or hostile DGPI does the trigger fire" contradicted the trigger's own firing-condition table (adverse-tier DGPI
AND spot *well* beyond the flip on the adverse side) — adversarial review of the viewer implementation surfaced the
internal contradiction; resolved in favor of the table: near-flip never fires the veto; near-flip + weakening/hostile DGPI
is a sizing consequence (RISK dealer-tier narrowing floors the band on top of the near-flip step-down), with the Pass-2
fresh flip read resolving the side. (2) The Wyckoff veto's conditional branch pins the **completed-phase evidence set**
for phase-C confirmation on the viewer-ingest path: the phase-C event itself (`spring`/`shakeout`; `utad`/`ut`) or
later-phase evidence that presupposes it (bull tags `phase_c_spring_long`/`phase_d_lps_long`/`sos_breakout_long`, events
`sos`/`jac`; bear tags `phase_c_utad_short`/`lpsy_short`/`sow_breakdown_short`, event `sow`) — demanding the phase-C event
as the *latest* event would re-veto structures that have already advanced.

### Changed — engineering-only spec records the shipped surface (mechanical)

**`engineering_only/PIPELINE_FEED_VIEW_SPEC_v3.0.md`** (`3.0.0 → 3.0.1`): new section for the five screen columns (three
long-premium Export views only), the `A1_FIELDS` + envelope additions, the contract readings the implementation follows
(LIMITED = preferred-not-mandated; PASS1 direction resolution; coarse dealer-tier narrowing; deliberate exclusions incl.
the SOW-recency absence-only detector), the viewer-side drift discipline (KbParityTests parse SYSTEM_PARAMS from the
sibling checkout), and the 4.x self-measuring note (snapshot writer prefers the no-options cache — flip before the loop
consumes frozen screen verdicts). Status table updated; **open**: the SOW-recency window parameter needs operator
calibration (follow-up issue; no parameter value set autonomously per SYSTEM_PARAMS discipline).

### Verification
Structural — `scripts/verify_frontmatter.sh` + `scripts/verify_anchors.sh` pass. Viewer side validated in its own repo
(239 backend tests incl. KbDrift/KbParity green against this checkout; live end-to-end against the v2 feed; multi-agent
adversarial review with refute-verify preceded the push).

## 2026-06-28 — Pipeline-feed view spec + §A1 self-contained reconciliation — viewer "Export -" views ship the canonical ATM IV / IV-HV; Pass-1 consumes it from the handoff

### Changed — §A1 ingest-map reconciliation (substantive; HITL, operator-approved; closes the self-contained loop)

The viewer now ships the canonical spread-mandate input in the Pass-1 handoff, so the KB no longer has to reach to the Polygon MCP
live for the IV/HV read. **`PASS1_SCREENING_v3.0.md`** (`3.0.11 → 3.0.12`): the §A1 ingest map's volatility row now lists
`atm_iv` / `iv_hv_ratio` / `iv_hv_status` (+ `iv_term_structure`, `put_call_ratio` context) and the dealer row adds `dealer_position`;
the IV/HV heuristic states that when a handoff carries `iv_hv_ratio`, Pass 1 consumes it directly (same producer either way — the
handoff value is canonical, not a downgrade), with the single/batch live fetch reserved for tickers fetched directly and the
fire-by-default fallback. The Pass 1 → Pass 2 boundary is unchanged: Pass 2 still re-confirms on a fresh producer fetch and the
*Needs chain validation* label is preserved; absence still degrades to fire-by-default per VOLATILITY. No SYSTEM_PARAMS change.

### Added — engineering-only coordination spec (mechanical; records the viewer change + the now-landed §A1 delta)

The viewer-side companion to the #80 volatility re-key. `kapman-polygon-viewer` now surfaces the producer's canonical ATM IV / IV-HV /
status (`atm_iv`, `iv_hv_ratio`, `iv_hv_status` — `kapman-polygon-mcp-v2` #19) as grid columns, adds four purpose-built **"Export -"
pipeline-feed presets** (Swing Long Calls, Swing Long Put, LEAPS, CSP) whose displayed columns ARE the §A1 handoff surface — the full
dealer contract (#79), Wyckoff completeness (phase confidence + the direction-specific spring/UTAD), ATR/RVOL stops, term structure,
and lineage — and carries the new fields in the Pass-1 export (`A1_FIELDS`). This makes the handoff **self-contained**: the canonical
spread-mandate input ships in the export rather than the KB reaching to the Polygon MCP live. The viewer derives `iv_hv_ratio` locally
from the scan's own `atm_iv ÷ HV20` (the same inputs the producer divides), so the value equals the producer's with no extra fetch.

- **`engineering_only/PIPELINE_FEED_VIEW_SPEC_v3.0.md`** (new, `3.0.0`, active) — records the Export-view column-set contract (feed
  base + per-strategy target ladder / directional event / filter / sort), the viewer-derived IV/HV columns and their producer-equality,
  and the §A1 ingest-map reconciliation as a ready-to-apply delta.
- **`INDEX.md`** — new doc registered in the v3.0 file directory + current file inventory tables; PASS1 patch-version bumped to 3.0.12.

### Verification
Structural — `scripts/verify_frontmatter.sh` + `scripts/verify_anchors.sh` pass; the new doc carries the required frontmatter and is
registered in INDEX. Viewer side validated in its own repo (158 backend tests; `tsc --noEmit` + `vite build` green).

## 2026-06-28 — Volatility-contract reconciliation — IV/HV spread-mandate re-keyed to the live Polygon `iv_hv_ratio` producer (4 files, atomic)

### Changed — volatility-contract reconciliation (substantive; HITL, decisions operator-approved; producer fixed + deployed in parallel)

The dealer reconciliation's sibling finding: the KB's IV/HV spread-mandate named **Schwab ATM chain IV** as the Pass-2 source —
a source the deployed Schwab tool does not produce (it emits only IV-skew / term-structure / OI) — and treated the volatility-status
`FULL/LIMITED/INVALID` as a label the tool *delivers*. The real IV/HV fusion lives at **Pass-1 Polygon** (`kapman-polygon-mcp-v2
get_options_metrics`), which already emits `average_iv` and `historical_volatility`. **Decision (Option B + B2, operator-approved):**
the operator extended the Polygon producer to emit an **ATM-anchored** `atm_iv` (implied vol interpolated to the nearest-to-money
strike at a ~30-DTE tenor, with a near-money band-average fallback), the `iv_hv_ratio` (`atm_iv` ÷ HV20, close-to-close annualized),
plus `iv_hv_status` and an `iv_hv_methodology` stamp — all additive — and deployed it. Verified live across **30 names** (all three
`atm_iv_source` paths and the degraded `iv_hv_status` values exercised; ratio arithmetic, orientation, and status honesty confirmed
by a 6-agent adversarial workflow). This commit re-keys the KB to that contract.

- **`VOLATILITY_v3.0.md`** (`3.0.0 → 3.0.1`, anchor) — **W1 (source):** both passes source the IV/HV read from the Polygon
  options-metrics producer; the spread-mandate input is the ATM-anchored `atm_iv` and the producer's `iv_hv_ratio`. **Pass 2
  re-confirms by re-fetching the same producer against a fresh chain (B2)** — not by switching to Schwab; *"Needs chain validation"*
  now means *"awaiting the fresh Pass-2 re-confirm."* Schwab is retired as an IV source (it remains the Pass-2 chain validator for
  strike/structure); `theoreticalVolatility` stays never-read. `VOLATILITY_015` reconciled in place (minimal, with a dated
  breadcrumb — no separate historical-note bloat). **W2 (vol-status):** the `FULL/LIMITED/INVALID` volatility-status is now
  **KB-derived** from the producer's `iv_hv_status` + freshness (the producer emits no semantic label): `OK` → FULL;
  `ATM_FALLBACK_BAND` → LIMITED (the ratio rests on the band-average fallback — floor-of-band, and a name too thin for a clean
  30-DTE ATM read is too thin to size aggressively); `NO_PRICE_HISTORY` / `HV_ZERO` / `INSUFFICIENT_CONTRACTS` / stale → INVALID.
  Downstream behavioral contract unchanged; only its provenance (derived, not delivered) corrected. `VOLATILITY_012/013` re-keyed
  to match.
- **Consumer cascade (W1 source only — W2 needed no consumer change, since consumers only *read* the label):**
  `SIGNAL_v3.0.md` (`3.0.6 → 3.0.7` — the spread-mandate trigger's source clause, the *Needs chain validation* / Pass-2 re-confirm
  wording, and the source-authority cross-reference), `PASS1_SCREENING_v3.0.md` (`3.0.10 → 3.0.11` — Pass-1 now reads the producer's
  `iv_hv_ratio`; the provisional→re-confirm reframing), `PASS2_VALIDATION_v3.0.md` (`3.0.5 → 3.0.6` — Pass-2 resolves the mandate by
  re-fetching the producer, not Schwab ATM).
- **Threshold:** `IV_HV_ELEVATED_THRESHOLD` held at **1.20** (cheap ceiling 0.95) — **provisional.** The ATM de-skew (band-average
  IV ran skew-inflated; ATM is generally lower) makes the line *stricter*, not looser, so it is not moved on one Friday's data;
  recalibrate against a multi-day panel. No SYSTEM_PARAMS change.
- **`INDEX.md`** — both version tables updated (VOLATILITY added at 3.0.1; SIGNAL/PASS1/PASS2 bumped) + a reconciliation status
  bullet + the `PIPELINE_010` pointer re-keyed to the renamed PASS1 heuristic.

### Deferred (tracked, not in this commit)
- **W3 — IV-rank / IV-percentile / IV-dispersion / *"Stretched IV"* dormancy honesty pass.** The KB still describes these as live
  reads; they are not produced. Pilot-safe because the existing `insufficient_iv_history` null-handling degrades a missing IV-rank
  read to *"not available"* rather than fabricating one. To be cleaned when IV-rank is revisited.
- **Absolute-IV guard.** The adversarial workflow found the IV/HV ratio is HV20-denominator-dominated, so it over-mandates spreads
  on low-absolute-IV names whose realized vol collapsed (HYG at ~8% IV is the canonical case). The correct fix is the IV-rank
  signal (phase-2 IV-history producer), not a band move; an interim `atm_iv` floor was considered and declined for phase 1.

### Verification
Conformance verified live (30 names) + by a 6-agent adversarial workflow (conformance audit + recalibration quant + 3 skeptical
lenses + synthesis). Post-cascade consistency sweep: **zero** surviving Schwab-ATM-as-IV-source / Pass-2-Schwab / `avg_iv`-as-source
references (only the intentional `theoreticalVolatility` anti-pattern, the `VOLATILITY_015` breadcrumb, and Schwab-as-chain-validator
remain). `verify_frontmatter` + `verify_anchors` pass.

## 2026-06-28 — Dealer-contract reconciliation — KB re-keyed to the live signed-DGPI / confidence producer contract (11 files, atomic)

### Changed — dealer-contract reconciliation (substantive; HITL, decisions operator-approved; producer fixed + deployed in parallel)

A code-grounded Stage-F audit found the KB's DEALER/VOLATILITY runtime contracts asserted Schwab fields that did not
exist — a signed ±100 DGPI tiered at ±20/±50, a `FULL/LIMITED/INVALID` "dealer-status", and a `long_gamma/short_gamma/neutral`
position-class — none of which the deployed `kapman-schwab-MCP` emitted (it emitted a magnitude-only DGPI, `above/below/at_flip`
position, and `confidence: high/med/low/invalid`). The KB's signed-DGPI model *did* match the **Pass-1 Polygon producer**
(`kapman-polygon-mcp-v2/lib/dealer_metrics.py`), which is what the viewer displays and the §A1 handoff exports; only the
Pass-2 Schwab tool diverged. **Decision (Option B):** the operator fixed `kapman-schwab-MCP` to match the Polygon contract
(signed DGPI `[-100,100]`, `position` gamma-regime, separate `position_vs_flip`, optional `iv_rank`), deployed + smoke-tested
(live SPY confirmed: DGPI −100 signed, Short Gamma, Below Flip, High). This commit re-keys the KB to that now-uniform contract,
**atomically across 11 files** (a half-applied KB would reference both contracts).

- **`llm_runtime/SYSTEM_PARAMS_v3.0.md`** (`3.0.3 → 3.0.4`): adds `DGPI_NEUTRAL_BAND` (10), `DGPI_STRONG_BAND` (30),
  `HOSTILE_MACRO_DGPI_MAX` (-30) — the producer's signed 10/30/60 bands, promoted to named tunables; `NEAR_FLIP_BAND_PCT`
  `0.25 → 0.5` (the producers' `at_flip` band).
- **`llm_runtime/DEALER_v3.0.md`** (`3.0.1 → 3.0.2`, anchor): DGPI tier table re-keyed `20/50 → 10/30/60` (signed, parametrized);
  the fictional `FULL/LIMITED/INVALID` "dealer-status" **removed** — dealer-trust behavior now keys directly on the emitted
  `confidence` (`high`/`medium` → full band + full hostile-macro; `low` → floor-of-band; `invalid` → drop the ticker layer);
  hostile-macro DGPI `≤ -20 → ≤ -30`; bearish-mirror band `≥ +50 → ≥ +30`; the `position` (gamma regime) / `position_vs_flip`
  (flip location) two-field split adopted; near-flip `0.25% → 0.5%`; a stale ticker drops the layer (was inconsistently
  floored); Pass-1↔Pass-2 dealer "agrees by tier/direction, never by exact value" (different option universes); legacy
  anchors `DEALER_011/012/013` preserved verbatim with a historical note marking the superseded dealer-status.
- **Consumer cascade** (dealer-sense `FULL/LIMITED/INVALID → confidence`, DGPI band re-keys, near-flip 0.5%):
  `SIGNAL_v3.0.md` (`3.0.5 → 3.0.6` — dealer-timing veto bands `-50/-20 → -30`, bearish-mirror `≥ +30`, the deferred "DEALER
  reconciliation" references resolved); `RISK_v3.0.md` (`3.0.2 → 3.0.3` — dealer-narrowing "reconciliation item" resolved to
  the `≥ +30` mirror band); `PASS2_VALIDATION_v3.0.md` (`3.0.4 → 3.0.5` — the chain-quality × dealer-confidence matrix; drift
  by tier/direction); `PASS1_SCREENING_v3.0.md` (`3.0.9 → 3.0.10` — hostile-macro `-30`; **the P4 paragraph corrected**: Schwab
  now emits `confidence`, so the Pass-1/Pass-2 distinction is *provenance and timing, not vocabulary*); `PORTFOLIO_MGMT_v3.0.md`
  (`3.0.4 → 3.0.5`); `KAPMAN_GUARDRAILS_v3.0.md` (`3.0.4 → 3.0.5` — hostile `≤ -30`; the now-false "v2.3 magnitude preserved"
  claim corrected); `REPORT_FORMAT_v3.0.md` (`3.0.10 → 3.0.11`); `REPORT_STYLE_v3.0.md` (`3.0.4 → 3.0.5`);
  `REPORT_TEMPLATE_PASS1_v3.0.html` (the source-bar degradation-flag label).
- **Deliberately untouched (separate findings):** the overloaded **volatility-status** `FULL/LIMITED/INVALID` (P0-2 — the vol
  tool still emits only skew/term/OI; not fixed by the dealer change) and **chain-quality** `Full/Limited/Weak` (P0-3a).
- **Behavior change (intended):** `high` and `medium` confidence are now treated identically (trusted, full band), so a ticker
  formerly floored under a "medium-confidence" read is promoted to full sizing.
- **`INDEX.md`** — bumped all 11 files in both version tables and added a dealer-contract-reconciliation status bullet.

### Verification
The anchor (DEALER + SYSTEM_PARAMS) was verified by an adversarial workflow (apply-readiness + faithfulness to the live
producer formulas + the locked decisions): faithfulness **pass** (signed-DGPI formula byte-identical between both producers;
the `10/30/60` tier mapping, the `confidence` behavioral contract, and the position split all correct; the live SPY read maps
to hostile-macro + full as intended). A second workflow produced the per-file cascade edit map with hard LEAVE-guards on the
overloaded vol-status/chain-quality labels. The cascade map's agent for **SIGNAL failed (returned null)**, so SIGNAL was
authored directly and caught by the post-apply consistency sweep (along with a PORTFOLIO orphan row and the HTML template).
Final sweep: **zero** surviving dealer-sense `dealer-status` / stale DGPI cutpoints; vol-status (6 files) + chain-quality intact;
`verify_frontmatter` + `verify_anchors` pass.

### Scope notes — still open
- **P0-2 (volatility contract)** — the vol tool emits only IV-skew/term/OI; no avg-IV/HV/rank/vol-status; the IV/HV
  spread-mandate path has no wired HV source. The single biggest remaining contract gap; no fix in flight.
- **P0-3a** (RISK↔PASS2 Weak-chain), **P0-4** (positions.md written at validation not fill), **P0-3b**, **P0-5** (CSP
  "regime-aligned" overclaim), **P1-10**, **P1-11** remain. #78 (Wyckoff vocabulary) stays open for Stage F (bearish pilot +
  rename), blocked on the operator's bearish fixture.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage E tail: P4 two-layer dealer vocab (PASS1) + WYCKOFF↔RISK UNKNOWN wording (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage E tail (two faithful clarifications; HITL — P4 softened after a verify catch)

The last two #78 reconciliation items before Stage F. Both are faithful documentation alignments, not new behavior.
After these, every consumer/parameter slice under #78 is done; only the Stage F closeout remains. #78 stays open.

- **`llm_runtime/PASS1_SCREENING_v3.0.md`** (`kb_version 3.0.8 → 3.0.9`) — **P4 (D-c two-layer dealer vocabulary).** Adds a
  clarifying paragraph to the §A1 ingest map distinguishing the two dealer layers that share a four-value shape:
  - `dealer_confidence` (`high`/`medium`/`low`/`invalid`; viewer marks high/medium trusted) is the viewer's **Pass-1**
    data-quality self-rating on its own dealer read — a **separate layer** from the Schwab **Pass-2** dealer-status
    `FULL`/`LIMITED`/`INVALID` that `DEALER_v3.0.md` resolves independently. A trusted Pass-1 read never substitutes for the
    Pass-2 status, and a degraded one never forces it (dealer regime re-fetched at Pass 2 regardless).
  - `position_vs_flip` (`above_flip`/`below_flip`/`at_flip`/`unknown`) is a **coarse Pass-1 triage** that maps onto DEALER's
    flip-zone (`at_flip` ≈ Near-flip; `above_flip`/`below_flip` ≈ above/below); the precise Well-above/Near-flip/Well-below
    resolution (per `NEAR_FLIP_BAND_PCT`) is a **Pass-2 determination** from the live Schwab flip distance.
  - **Scoped to faithful restatement.** The adversarial verify flagged a first draft for asserting *new* degradation
    behavior (a `dealer_confidence` reduced-weight/drop-at-invalid rule; a `position_vs_flip` "degrades per the
    required-field contract" reference to a clause that doesn't enumerate it) — unratified judgment per CLAUDE.md rule 3.
    Both were removed; the committed text states only the established two-layer distinction, the value mapping, and the
    already-committed Pass-1 → Pass-2 boundary. DEALER (its Schwab-layer pipeline confidence) and PASS2 (already correct)
    untouched.
- **`llm_runtime/WYCKOFF_v3.0.md`** (`kb_version 3.0.8 → 3.0.9`) — **WYCKOFF↔RISK UNKNOWN wording reconciliation.** The two
  UNKNOWN/unconfirmed degradation sites (the estimation-path-decline list and the UNKNOWN behavioral-consequences list)
  said the sizing band "closes to the **conditional floor**"; re-keyed to "the long-premium sizing band **closes
  entirely** (the most conservative case per RISK — distinct from the pre-phase-C conditional floor)". This aligns WYCKOFF
  to RISK 3.0.2 (UNKNOWN / non-aligned / `ranging_undefined` → long-premium band closed entirely) and to WYCKOFF's own
  decision layer (UNKNOWN = "the most conservative case"). The legitimate **pre-phase-C** conditional-floor references
  (decision table + downstream RISK row + bearish-mirror block) are correctly unchanged.
- **`INDEX.md`** — bumped PASS1 + WYCKOFF in both v3.0.1 version tables (3.0.8 → 3.0.9 each) and updated the §A1 status
  bullet (P4 + UNKNOWN done; all consumer/parameter slices complete, only Stage F remains).

### Verification
P4: focused adversarial workflow (faithfulness/correctness + apply-readiness) + judge returned **apply-with-fixes** —
the two-layer distinction and the coarse→precise flip mapping verified correct and boundary-respecting, with two
should-fixes for the unratified degradation assertions; both folded out (the committed text is strictly the faithful
subset). WYCKOFF UNKNOWN: faithful two-occurrence phrase alignment to RISK's committed wording (manually verified the
`replace_all` hit only the two UNKNOWN sites, not the pre-phase-C conditional-floor references). `verify_frontmatter` +
`verify_anchors` pass.

### Scope notes — remaining under #78
- **Stage F closeout only:** structural validate; golden pilot on the operator's real 73-row BULLISH Copy Pass-1 export +
  an operator-produced BEARISH fixture; completeness critic; estimation-path regression; then the `_v3.0 → _v4.0`
  filename rename sweep. **Blocked on the operator-produced BEARISH viewer fixture.**

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage D consumer re-key, PASS2 (entry-snapshot phase→regime + riders) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage D (PASS2 persistence-capture; faithful no-judgment re-key; applied on standing continue)

The last "entry Wyckoff phase" exempt-field wording lag, in the file that owns the *trigger and timing* of the entry-time
snapshot write. Faithful re-key matching the committed JOURNAL_MGMT 4.0.3 / PORTFOLIO 3.0.4 / GUARDRAILS 3.0.4 (the exempt
Wyckoff field holds the **regime** per D-d). #78 stays open.

- **`llm_runtime/PASS2_VALIDATION_v3.0.md`** (`kb_version 3.0.3 → 3.0.4`): in the "capture the entry-time snapshot into
  `positions.md`" heuristic, "entry Wyckoff **phase**" → "entry Wyckoff **regime**". The capture now also names the
  best-effort non-exempt entry-context **riders** (entry phase A–E, `phase_c_confirmed`, the confirmed `entry_wyckoff_event`)
  written at the same Pass-2 moment, and states explicitly that the riders and `option_mid` ride **outside** the exemption
  proper. The exempt set is unchanged — **exactly the regime snapshot's 5 fields + the 8 SIGNAL levels** (the "sole exemption
  to the numeric-no-persist floor"); `JOURNAL_MGMT_v4.0` owns the riders' grammar, `KAPMAN_GUARDRAILS` owns the exemption.
  The Pass 1 → Pass 2 boundary and anti-hallucination floor are untouched.
- **`INDEX.md`** — bumped PASS2 in both v3.0.1 version tables (3.0.3 → 3.0.4) and updated the §A1 status bullet (Stage D
  PASS2 done).

### Verification
Faithful single-paragraph re-key mirroring the committed exempt-snapshot definition (5 regime fields + 8 SIGNAL levels,
riders non-exempt) already verified across JOURNAL/PORTFOLIO/GUARDRAILS this cycle; OLD string confirmed unique; no
multi-lens workflow run (disproportionate for a faithful consumer re-key with established referents). `verify_frontmatter`
+ `verify_anchors` pass.

### Scope notes — deferred under #78
- **P4** (viewer `dealer_confidence` high/med/low/invalid at Pass 1 vs Schwab `FULL/LIMITED/INVALID` at Pass 2 — keep as two
  layers, clarify at each ref) and the **WYCKOFF↔RISK UNKNOWN** floor/closed wording item remain — then Stage F closeout.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage E parameters, SYSTEM_PARAMS confluence band + conditional-top (+ RISK/SIGNAL/REPORT_FORMAT wiring) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage E (SYSTEM_PARAMS + consumer wiring; substantive; HITL, parameter values operator-approved in session)

Adds the two operator-tunable parameters the prior direction-aware slices left as named-but-undefined follow-ups, and
wires the consumers to reference them by name (the SYSTEM_PARAMS "consumed by name, not value" principle). Parameter
values were chosen by the operator this session. Coordinated 4-file slice. #78 stays open.

- **`llm_runtime/SYSTEM_PARAMS_v3.0.md`** (`kb_version 3.0.2 → 3.0.3`): adds two parameters, both with consuming-files
  rows and Appendix change-log entries.
  - `FORWARD_TEST_CONFLUENCE_BAND_PCT` = **0.5** (percent of spot, ±) — **provisional, pilot-calibrated** (same status as
    `TIER_GATE_TAU_*`). The near-coincidence tolerance within which the viewer's forward-tested target (`pt_*`) is treated
    as confluent with the SIGNAL structural+validated exit anchor, so its calibrated hit-rate (`*_prob`) rides as a
    confidence annotation on the alert level; beyond ±this band the target diverges and both levels surface. Annotation
    context only — never the broker price (anti-hallucination floor). Consumed by SIGNAL + REPORT_FORMAT.
  - `CONDITIONAL_TOP_SIZE_PCT` = **1.0** (percent of real-capital denominator) — promotes the v4.0-new conditional-top
    sizing magnitude (JD1) from a RISK Appendix reference point to a named operator-tunable parameter. Value unchanged
    (~1% → 1.0%); only the ownership/tunability surface moves. Consumed by RISK. The other RISK band magnitudes
    (~3%/2%/1%/0.5%, 5% ceiling) remain v2.3 reference points in RISK's Appendix.
- **`llm_runtime/RISK_v3.0.md`** (`kb_version 3.0.1 → 3.0.2`): the Appendix sizing-band table's conditional-top row now
  cites `CONDITIONAL_TOP_SIZE_PCT` per SYSTEM_PARAMS by name (currently 1.0%); the table intro flags the conditional-top
  as the single parametrized exception while the other magnitudes stay v2.3 reference points. (The near-flip step-down
  ladder keeps the inline "~1%" as a step-destination reminder.)
- **`llm_runtime/SIGNAL_v3.0.md`** (`kb_version 3.0.4 → 3.0.5`) and **`llm_runtime/REPORT_FORMAT_v3.0.md`**
  (`kb_version 3.0.9 → 3.0.10`): resolve the three "a SYSTEM_PARAMS follow-up" placeholders (SIGNAL Stop + Profit-target
  exit triggers; REPORT_FORMAT Exit-plan row) to the named `FORWARD_TEST_CONFLUENCE_BAND_PCT`. No behavior change — the
  placeholders pointed at this now-defined parameter.
- **`INDEX.md`** — bumped all four files in both v3.0.1 version tables (added SYSTEM_PARAMS to the report-metadata table)
  and updated the §A1 status bullet.

### Verification
Adversarial workflow across all 4 files (values + faithfulness; cross-file/bidirectional wiring; apply-readiness) +
synthesis judge: values-faithful `pass` (0.5 / 1.0 correct; units + consumers correct; 1.0% equals the prior ~1%),
cross-file `pass` (consuming list bidirectionally consistent — RISK + REPORT_FORMAT newly added, SIGNAL extended; all 3
placeholders resolved with no fourth dangling; no stray hardcodes), apply-readiness `pass` (all 12 OLD blocks
verbatim + unique across the 4 files). Judge: `apply_ready: true`, apply-as-is, zero must-fix. `verify_frontmatter` +
`verify_anchors` pass; placeholder grep clean.

### Scope notes — deferred under #78
- **PASS2** (line 94 phase→regime + riders) — also touches the confluence behavior but consumes it indirectly via SIGNAL
  and references no tolerance width, so it is not a SYSTEM_PARAMS consumer. **P4** (dealer_confidence/position_vs_flip) and
  the WYCKOFF↔RISK UNKNOWN floor/closed wording item remain.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage E presentation, REPORT_FORMAT (render the forward-tested confluence suffix) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage E (REPORT_FORMAT presentation; faithful rendering of committed SIGNAL output; applied on standing continue)

SIGNAL 3.0.3/3.0.4 added a forward-tested-target confluence annotation to the Stop & Profit-target exit triggers — the
viewer's `pt_*`/`*_prob` calibrated hit-rate rides as a confidence annotation on the structural+validated underlying
alert level, never as the price. This slice specifies how REPORT_FORMAT renders that annotation. No new behavior — the
judgment landed in the SIGNAL slice; this is the presentation layer catching up. #78 stays open.

- **`llm_runtime/REPORT_FORMAT_v3.0.md`** (`kb_version 3.0.8 → 3.0.9`):
  - The screening per-ticker **Exit plan** subsection and the portfolio **Exit-trigger proximity** subsection now render
    the confluence suffix — *"…— viewer forward-tested hit-rate ~Z%, as-of [date]"* (verbatim from SIGNAL lines 65/76) —
    as a suffix on the underlying alert level when SIGNAL carries it, **never** as the alert price; the structural+validated
    level stays the broker order (anti-hallucination floor). On divergence beyond the near-coincidence tolerance, both
    levels surface per SIGNAL; the portfolio row notes overflow to footnote per the cap discipline.
  - The `SIGNAL_v3.0.md` cross-reference row records the annotation as a rendered output (suffix on the alert level, never
    the price).
  - Untouched (correctly): the compact 20-char screening "Exit"/"Stop Alert"/"Profit Alert" columns (too tight; annotation
    lives in the detail/footnote); the Portfolio pre-output self-audit underlying-level rows (a required-field completeness
    gate, not a rendering spec); the Macro Regime card eligible-set redirect (already lists long puts).
- **`INDEX.md`** — bumped REPORT_FORMAT in the report-metadata table (3.0.8 → 3.0.9), added it to the v3.0.1 version/status
  table (was absent), and updated the §A1 status bullet (Stage E REPORT_FORMAT done).

### Verification
Focused adversarial workflow (faithfulness to SIGNAL's committed annotation; placement/completeness; apply-readiness) +
synthesis judge: faithfulness `pass` (suffix a character-for-character match to SIGNAL 65/76; anti-hallucination framing
intact), placement `pass` (Exit plan + Exit-trigger proximity confirmed the right homes; rows 311/315 and the compact
columns correctly excluded), apply-readiness `pass` (all 4 OLD blocks verbatim + unique). Judge: `apply_ready: true`,
apply-as-is, zero must-fix. The "near-coincidence tolerance" wording was aligned to SIGNAL. `verify_frontmatter` +
`verify_anchors` pass.

### Scope notes — deferred under #78
- **SYSTEM_PARAMS** (the confluence-band/near-coincidence tolerance width + the conditional-top magnitude / JD1),
  **PASS2** (line 94 phase→regime + riders), **P4** (dealer_confidence/position_vs_flip), and the WYCKOFF↔RISK UNKNOWN
  floor/closed wording item remain.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage D/E consumer re-key, KAPMAN_GUARDRAILS (hostile-macro bullish-scope + exempt-field phase→regime) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage D/E (KAPMAN_GUARDRAILS T0 floor; substantive; HITL, approved turn-by-turn in session)

Brings the T0 behavioral-floor file into line with the committed direction-aware model. The work is faithful
reconciliation, not new judgment: GUARDRAILS' own hostile-regime eligible-set table already listed "Long puts —
Eligible — directional alignment with regime," and committed DEALER 3.0.1 + SIGNAL 3.0.4 already carry the bullish
scope (SIGNAL line 46 explicitly cites this GUARDRAILS table). Only the surrounding **prose** was lagging. #78 stays open.

- **`llm_runtime/KAPMAN_GUARDRAILS_v3.0.md`** (`kb_version 3.0.3 → 3.0.4`):
  - **Hostile-macro refusal scoped to bullish long-premium** in the Principle, the "Macro regime is a default" heuristic,
    and the Appendix "Hostile-regime eligible structures" intro: the macro gate refuses **bullish** long-premium (long
    calls / call debit spreads); long puts / put debit spreads are surfaced as the **directionally-aligned redirect**
    (then CSPs, hedges, LEAPs). Fixes two prose sites that dropped long puts from the surfaced eligible set — now matching
    the file's own eligible-set table and the committed DEALER report-label/eligible-set + SIGNAL veto.
  - **Exempt-snapshot field relabel (D-d):** in the sole no-persist exemption clause, "entry Wyckoff **phase**" → "entry
    Wyckoff **regime**" — the exempt field holds the confirmed regime (cycle-stage axis), matching JOURNAL_MGMT 4.0.3 +
    PORTFOLIO 3.0.4. The exempt set is unchanged: **exactly 5 regime fields + 8 SIGNAL stop/profit levels** (a label
    change, not a count change). The non-exempt `entry_phase`/`phase_c_confirmed`/event riders remain JOURNAL's grammar.
  - **DEALER-freshness:** the hostile-definition note's "subject to band revision when `DEALER_v3.0.md` is rewritten" is
    replaced — that rewrite landed (DEALER 3.0.1), the ≤ -20 magnitude was preserved, the refusal scoped to bullish, and
    the per-ticker bearish mirror defined.
  - Untouched (correctly): the hostile-regime eligible-set **table** (already direction-aware), the VALIDATION_001 legacy
    anchor, and line-29's direction-neutral "refuses that structure" framing.
- **`INDEX.md`** — bumped GUARDRAILS in the report-metadata table (3.0.3 → 3.0.4), added GUARDRAILS to the v3.0.1
  version/status table (was absent), and updated the §A1 status bullet (Stage D/E GUARDRAILS done).

### Verification
Focused adversarial workflow (faithfulness/internal-consistency vs DEALER 3.0.1 / SIGNAL 3.0.4 / JOURNAL 4.0.3;
completeness/prose-site sweep; apply-readiness) + synthesis judge: completeness `pass`, apply-readiness `pass` (all 7
OLD blocks verbatim + unique; the two line-14 Principle fragments confirmed disjoint), faithful-consistency `pass`
(prose now matches the file's own eligible-set table and the committed consumers; the 5+8 exempt set unchanged). Judge:
`apply_ready: true`, zero must-fix (the one finding was an annotation-only stale version in the draft header, corrected).
`verify_frontmatter` + `verify_anchors` pass.

### Scope notes — deferred under #78
- **REPORT_FORMAT** (forward-tested-confidence suffix on the exit-plan row), **SYSTEM_PARAMS** (confluence-band tolerance +
  conditional-top magnitude / JD1), **PASS2** (line 94 phase→regime + riders), **P4** (dealer_confidence/position_vs_flip),
  and the WYCKOFF↔RISK UNKNOWN floor/closed wording item remain.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage E consumer re-key, SIGNAL ("floor" → "conditional floor") (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage E (SIGNAL terminology; substantive but no-judgment; applied on standing continue)

A faithful one-term disambiguation: now that RISK (3.0.1) distinguishes the **conditional floor** (a direction-aligned
range regime pre-phase-C, override-only) from the **closed** band (non-aligned / `ranging_undefined` / `UNKNOWN`),
SIGNAL's committed band-ladder sentence carrying a bare "floor" for the pre-phase-C band is ambiguous. Tightened to match
RISK's name. No judgment change; not brought for separate sign-off (faithful no-judgment re-key per the slice cadence).
#78 stays open.

- **`llm_runtime/SIGNAL_v3.0.md`** (`kb_version 3.0.3 → 3.0.4`): in the Wyckoff-veto heuristic's sizing-band-ceiling
  sentence, "pre-phase-C the **floor**" → "pre-phase-C the **conditional floor**" — the band RISK names. The other "floor"
  uses in the file (the *anti-hallucination floor*, and structural *range/candidate floor* anchors) are unrelated and
  untouched.
- **`INDEX.md`** — bumped SIGNAL in the v3.0.1 version/status table (3.0.3 → 3.0.4), added the missing SIGNAL row to the
  report-metadata patch table, and updated the §A1 status bullet (Stage E SIGNAL done).

### Verification
`verify_frontmatter` + `verify_anchors` pass. OLD string confirmed unique (the band-ladder sentence). No multi-lens
workflow run — disproportionate for a faithful single-term re-key with a committed-consumer (RISK) referent.

### Scope notes — deferred under #78
- **GUARDRAILS** (hostile-macro language bullish-scope + line-46 "entry Wyckoff phase"), **PASS2** (line 94),
  **REPORT_FORMAT** (forward-tested-confidence suffix), **SYSTEM_PARAMS** (confluence-band tolerance + conditional-top
  magnitude), **P4** (dealer_confidence/position_vs_flip), and the WYCKOFF↔RISK UNKNOWN floor/closed wording item remain.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage D/E anchor refinement, WYCKOFF (decision-layer bearish mirror + conditional-top + projected-markdown + utad routing) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage D/E (WYCKOFF canonical model; substantive; HITL, approved turn-by-turn in session)

Makes the canonical decision-layer file direction-symmetric so consumers no longer have to *infer* the bearish mirror,
normalizes the band name the consumers already committed to, and adds the two downside structural/routing analogs the
direction-aware SIGNAL/RISK/PORTFOLIO slices reference. Faithful application of the already-approved symmetric model to
its source file. #78 stays open (P4 + remaining files).

- **`llm_runtime/WYCKOFF_v3.0.md`** (`kb_version 3.0.7 → 3.0.8`):
  - **Decision-layer bearish-mirror block.** The decision table stays long-framed (the canonical bullish reference); a
    compact mirror block + note is added beneath it spelling out the bearish reading a long put gets — `markup`↔`markdown`
    and `reaccumulation`↔`redistribution` (trend + post-phase-C continuation → upper band); `accumulation`↔`distribution`
    (gated base → conditional floor pre-C → conditional-top post-C); refusal sets swap; `ranging_undefined`/`UNKNOWN`
    refuse both directions. phase-C confirmer `spring`/`shakeout`↔`utad`, phase-D entry `lps`↔`lpsy`; favorable/unfavorable
    moves mirror. Matches committed RISK 3.0.1 / SIGNAL 3.0.3 / PORTFOLIO 3.0.4 verbatim in intent (not a 5th column — a
    mirror block, the way those consumers already read the layer direction-relative). The intro sentence + the line-182
    RISK and line-183 DEALER downstream-flow rows were made direction-relative to match.
  - **`conditional-top` normalization.** The two naming stragglers — `conditional range` (downstream RISK row) and
    `top-of-conditional` (decision table) — normalized to **`conditional-top`**, the name RISK committed to. `conditional
    floor` preserved everywhere (unchanged).
  - **Projected-markdown-target structural row** added to the structural-levels table — the exact downside analog of the
    projected-markup target (distribution range height projected *down* from the Ice level; post-`sow` `markdown`), the
    Ice-level projection SIGNAL line references for long-put profit-target anchors.
  - **`utad` downstream-routing row** added — the bearish phase-C mirror of the `spring` routing row, so SIGNAL's pre/post-
    `utad` veto distinction has the same downstream routing the bullish `spring` has.
  - Untouched (correctly): the canonical-vocabulary Appendix glossary (verbatim viewer/v2), the legacy
    WYCKOFF_PHASE_*/EVENT_* anchors + historical note (D-e). `utad` confirmed at phase C throughout (not phase E).
- **`INDEX.md`** — bumped WYCKOFF in both v3.0.1 version tables (3.0.7 → 3.0.8) and updated the §A1 status bullet (Stage D/E
  WYCKOFF done).

### Verification
Adversarial workflow pass (a dedicated bearish-mirror-correctness lens hunting sign inversions; cross-file consistency vs
RISK/SIGNAL/PORTFOLIO; completeness/straggler sweep; apply-readiness) + synthesis judge: **mirror-correctness `pass`** (every
bullish↔bearish pairing + shared ceiling verified, no inversion), **cross-file `pass`** (matches the committed consumers
exactly; `conditional-top` is RISK's name), **apply-readiness `pass`** (all 8 OLD blocks verbatim + unique; glossary +
legacy anchors outside the edit range), judge **apply-as-is, zero must-fix**. The line-183 DEALER-row direction-relative
annotation was folded from a completeness nit (DEALER reconciliation already landed this session, so annotated rather than
deferred). `verify_frontmatter` + `verify_anchors` pass; straggler grep clean (`conditional range`/`top-of-conditional`
both gone).

### Scope notes — deferred under #78
- **Known WYCKOFF↔RISK item:** WYCKOFF lines 20/143 describe UNKNOWN as closing to the "conditional floor" while RISK
  routes UNKNOWN to "long-premium band closed entirely." Behaviorally convergent (floor + veto-fires-on-UNKNOWN ⇒ no normal
  entry); a documentation-tone reconciliation tracked for a later #78 pass (not a `conditional-top` naming straggler;
  `conditional floor` must not change).
- **GUARDRAILS** (hostile-macro language + line-46 "entry Wyckoff phase"), **SIGNAL** ("floor"→"conditional floor"),
  **PASS2** (line 94), **REPORT_FORMAT**, **SYSTEM_PARAMS**, **P4** remain.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage D/E consumer re-key, DEALER (bearish-mirror DGPI band) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage D/E (DEALER consumer; substantive; HITL, approved turn-by-turn in session)

Defines the per-ticker bearish-mirror DGPI band that SIGNAL's dealer-timing veto (3.0.3) and RISK's dealer-narrowing
(3.0.1) already reference as a "DEALER reconciliation" item, and makes DEALER's directional framing symmetric so a long
put reads the dealer regime as the mirror of a long call. Operator decision this session: **symmetric mirror, v2.3
magnitudes preserved (sign-flip only)**, ticker-layer only. #78 stays open (P4 + remaining files).

- **`llm_runtime/DEALER_v3.0.md`** (`kb_version 3.0.0 → 3.0.1`):
  - **Per-ticker bearish-mirror DGPI band defined** (Appendix + new heuristic): the ticker dealer regime *adverse to a
    bearish position* = **DGPI ≥ +50 with spot well above the ticker's flip** — the exact sign-flipped mirror of the
    bullish per-ticker hostile band (DGPI ≤ -50 with spot well below flip). This is the band SIGNAL line 42/254 and RISK
    line 25/66 reference; magnitudes unchanged (≥+50/≥+20/≤-20/≤-50), only the sign is read against the position's
    direction.
  - **New heuristic "Dealer regime is read relative to the position's direction"** + a Principle clause: the DGPI tier
    vocabulary and spot-vs-flip read are framed for a long; a long put reads their mirror (strongly-supportive-for-a-long
    is strongly-adverse-for-a-put; above-flip ↔ below-flip). The ticker-layer narrowing heuristic re-keyed direction-
    relative; the "regime that does not align with the position's direction closes the band" generalized to the WYCKOFF
    refusal set (corrects the old "distribution and markdown" which omitted redistribution).
  - **Macro hostile-macro refusal bullish-scoped everywhere** (Principle, the macro heuristic, the Appendix composite,
    the outputs-table hostile-macro-flag row, the vocabulary row, and the rendered report-label string): refuses **bullish**
    long-premium (long calls / call debit spreads); long puts / put debit spreads are the directionally-aligned eligible
    redirect, not a refused structure — matching committed SIGNAL 3.0.3 + GUARDRAILS ("Long puts — Eligible").
  - **No macro mirror composite** ("supportive-macro refuses long puts") added — deliberately: no committed consumer reads
    one (SIGNAL has no bearish-adverse macro flag), so it would be a dangling capability. The bearish mirror is **ticker-
    layer only**; a supportive macro simply makes the per-ticker bearish-mirror band the relevant stability check. Full
    macro symmetry would be a coordinated SIGNAL+GUARDRAILS+DEALER change (out of scope, flagged).
  - Added `SIGNAL_v3.0.md` as a consumer of the per-ticker DGPI-tier output row (it reads tier + flip-zone direction-
    relative for the dealer-timing veto). Walls + GEX-slope prose left long-framed (SIGNAL owns wall-side direction-
    relativity). Stale-macro mentions left direction-neutral (per committed SIGNAL, stale macro fires direction-neutral).
    Legacy anchors DEALER_001–014 preserved verbatim; no heuristic renamed (a heading added, not renamed) → no historical
    note needed.
- **`INDEX.md`** — added DEALER to both v3.0.1 version tables (3.0.0 → 3.0.1) and updated the §A1 status bullet (Stage D/E
  DEALER done).

### Verification
Adversarial workflow pass (faithfulness to SIGNAL/RISK/GUARDRAILS + the operator's symmetric-mirror decision; a dedicated
no-dangling-capability lens on the macro-asymmetry call; completeness/dangling-framing; apply-readiness) + synthesis
judge: faithfulness `pass`, no-dangling-capability `pass` (the ticker-mirror-only / no-macro-mirror design independently
confirmed coherent and consumer-grounded — the per-ticker band IS consumed by SIGNAL+RISK, a macro mirror would NOT be),
apply-readiness `pass` (all 11 OLD blocks verbatim + unique, DEALER_001–014 intact). One must-fix folded — the rendered
"Hostile macro" report-label string (Appendix line 223) still read bare "long-premium refused" with long puts dropped
from the eligible set, an inconsistency the bullish-scoping edits created; corrected to match the outputs table.
`verify_frontmatter` + `verify_anchors` pass.

### Scope notes — deferred under #78
- **GUARDRAILS** (its hostile-macro language + the line-46 "entry Wyckoff phase" exempt-field wording), **WYCKOFF**
  (decision-layer bearish column + "conditional-top" normalization + projected-markdown-target row + `utad` routing),
  **SIGNAL** ("floor"→"conditional floor"), **PASS2** (line 94), **REPORT_FORMAT**, **SYSTEM_PARAMS**, **P4** remain.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage D persistence re-key, JOURNAL_MGMT (positions.md regime grammar + riders) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage D (JOURNAL_MGMT persistence; substantive; HITL, approved turn-by-turn in session)

Re-keys the `positions.md` record grammar to the two-axis canonical model so the riders PORTFOLIO (3.0.4) now
consumes get written, and so the entry-time snapshot speaks the same regime/phase/event vocabulary as the screening
spine. Faithful re-key + two net-new riders locked by decision D-d. #78 stays open (P4 + remaining files).

- **`llm_runtime/JOURNAL_MGMT_v4.0.md`** (`kb_version 4.0.2 → 4.0.3`):
  - **`entry_wyckoff_phase` now HOLDS the regime.** The load-bearing exempt field keeps its name (cited cross-file as
    the GUARDRAILS-exempt field) but its value domain is re-keyed from the old four Title-case phases
    (`Accumulation | Markup | Distribution | Markdown`) to the **seven lowercase canonical regimes** — the cycle-stage
    axis, per D-d. Matches the already-committed PORTFOLIO 3.0.4 ("the exempt-snapshot Wyckoff field holds the regime").
    `ranging_undefined`/`UNKNOWN` never populate a real entry (a position opens only on a confirmed, direction-aligned
    regime); the enum is the value domain.
  - **`entry_wyckoff_event` re-keyed to the lowercase ~27-event vocab** (WYCKOFF "Wyckoff canonical vocabulary" owns
    the set; old `SC|AR|Spring|SOS|BC|AR_TOP|UT|SOW` → lowercase, with bullish `spring/shakeout/lps/sos/jac` and bearish
    `utad/ut/lpsy/sow` exemplars).
  - **Two non-exempt riders added** (D-d): `entry_phase` (A–E) — the schematic phase, the recommended rider PORTFOLIO's
    D→B/A phase-regression sub-branch reads; and `phase_c_confirmed` (`true|false`) — records the post-/pre-phase-C
    distinction RISK applied live when sizing, **reserved** entry context with no current reader (framed like the
    reserved `attack_flags[]`/`invalidation_conditions[]`, empty until Stage 3).
  - **Exempt snapshot unchanged in scope:** still **exactly 5 regime fields + 8 SIGNAL levels**. The three riders sit
    **outside** the exemption — categorical/boolean structural facts, not numeric regime reads, so the numeric
    no-persist prohibition never reached them. The riders were grouped into their own labeled block so the 5+8 exempt
    set is unambiguous. Heuristic prose "entry Wyckoff phase" → "entry Wyckoff regime" in the 5-field list.
  - Not touched (correctly): the join-key tokens, `parent_pass2`, the 8 SIGNAL levels, `option_mid`, the live-refresh
    block, the §A4 record headers, the lineage/no-persist heuristics. JOURNAL has no legacy `DOMAIN_NNN` anchors
    (v4.0-native) — no historical note needed.
- **`INDEX.md`** — bumped the JOURNAL Version-status bullet (4.0.2 → 4.0.3) and updated the §A1-reconciliation status
  bullet (Stage D JOURNAL_MGMT done).

### Verification
Adversarial workflow pass (faithfulness to WYCKOFF/PORTFOLIO/GUARDRAILS, cross-file consistency, completeness/dangling
old-vocab, apply-readiness) + synthesis judge: apply-readiness `pass` (all 4 OLD blocks verbatim + unique);
faithfulness `pass` (exempt set independently re-counted as exactly 5+8, regimes byte-faithful to WYCKOFF, events
correctly sided); one confirmed must-fix folded in — the draft had over-claimed a present-tense "Stage-3 calibration
loop" consumer (ungrounded in `llm_runtime/`, and PORTFOLIO reads `entry_phase` not `phase_c_confirmed`), corrected to
the reserved-field framing. `verify_frontmatter` + `verify_anchors` pass; dangling-vocab grep clean.

### Scope notes — deferred under #78
- **PASS2_VALIDATION** (line 94) and **GUARDRAILS** (line 46) still say "entry Wyckoff phase" and don't list the three
  riders; both converge to "regime" + the riders in their own later slices.
- **DEALER** (bearish-mirror DGPI band), **WYCKOFF** (decision-layer bearish column + "conditional-top" normalization +
  projected-markdown-target row + `utad` routing), **SIGNAL** ("floor"→"conditional floor"), **REPORT_FORMAT**,
  **SYSTEM_PARAMS**, **P4** (dealer_confidence/position_vs_flip) remain pending.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage D consumer re-key, PASS1 (direction-aware screening) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage D (PASS1 consumer; substantive; HITL, approved turn-by-turn in session)

Re-keys the PASS1 screening body logic to the committed SIGNAL (3.0.3) direction-aware model — completing the
entry-side of the symmetric veto. The §A1 ingest map was already new-vocab (#72/#76); this is the heuristic/prose
layer catching up. #78 stays open (P4 + remaining files).

- **`llm_runtime/PASS1_SCREENING_v3.0.md`** (`kb_version 3.0.7 → 3.0.8`):
  - **Hostile-macro prose scoped to bullish** long-premium (long calls + call debit refused); long puts/put debit
    spreads are the directionally-aligned eligible redirect — reconciles the line-21 prose with the already-correct
    Appendix hostile-macro redirect table and SIGNAL's dealer-timing veto.
  - **Direction resolution made regime-natural + symmetric:** an accumulation-family regime
    (`accumulation`/`reaccumulation`) or `markup` → BULLISH; a distribution-family regime
    (`distribution`/`redistribution`) or `markdown` → BEARISH; `sos`/`sow` fallback (lowercased); explicit
    operator declaration ("screen for long puts" = BEARISH). The resolved direction is an **input** to the
    direction-aware Wyckoff veto and is established **before** the veto runs (step-4 sequence corrected to match).
  - Wyckoff-status heuristic, degraded-input tables, and the WYCKOFF/RISK/PORTFOLIO workflow rows re-keyed to
    regime + phase (A–E) vocabulary; "Phase and event vocabulary" → "Regime, phase, and event vocabulary".
  - **Behavioral completion (faithful to the approved model):** a confirmed bearish regime (`distribution`
    post-`utad` / `markdown`) now yields an **Eligible** bearish candidate (long put), where before it was
    NO_TRADE-with-redirect — the entry-side mirror of the symmetric veto.
  - Not touched (already correct): the §A1 ingest map + required-field contract (new-vocab from #72/#76); the
    Appendix hostile-macro redirect table; the legacy anchors (PIPELINE_010/011, SCORING_001 — MCP/scoring, not
    Wyckoff vocab, so no historical note).
- **`INDEX.md`** — bumped both version tables (3.0.7 → 3.0.8) and updated the §A1 status bullet (Stage D PASS1 done).

### Verification
Adversarial workflow pass (faithfulness, completeness, apply-readiness): apply-readiness `pass` (all 13 anchors
unique); `apply-with-fixes` — one internal sequencing regression in the step-4 summary (the `sos`/`sow` fallback
must precede the direction-aware veto, not follow it) and two stale-`phase` leftovers (lines 29, 134); all folded
in. `verify_frontmatter` + `verify_anchors` pass; dangling-vocab grep clean.

### Scope notes — deferred under #78
- **JOURNAL_MGMT** (Stage D): write `entry_phase` (A–E) + `phase_c_confirmed` riders + the `positions.md` grammar
  (PORTFOLIO now consumes these).
- **DEALER** (bearish-mirror DGPI band), **WYCKOFF** (decision-layer bearish column + "conditional-top"
  normalization), **SIGNAL** ("floor"→"conditional floor"), **GUARDRAILS**, **REPORT_FORMAT**, **SYSTEM_PARAMS**, **P4**.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage C consumer re-key, PORTFOLIO (regime exit advisory) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage C (PORTFOLIO consumer; substantive; HITL, approved turn-by-turn in session)

Re-keys the Regime exit advisory PORTFOLIO operationalizes to match the direction-aware advisory committed in
SIGNAL (3.0.3). Faithful consumer re-key, no new judgment points. #78 stays open (P4 + remaining consumers).

- **`llm_runtime/PORTFOLIO_MGMT_v3.0.md`** (`kb_version 3.0.3 → 3.0.4`):
  - The advisory's **"Wyckoff phase succession branch" → "Wyckoff regime succession & phase-regression branch"**:
    fires on an unfavorable **regime** move (per WYCKOFF's succession **graph**, read **relative to the position's
    direction** — long-framed graph, bearish = mirror) **OR** a **phase regression D→B/A** (D→C retest excluded).
    Direction-relative throughout (a long put's decay mirrors a long call's), matching SIGNAL.
  - **Decision D-d encoded:** the regime-succession sub-branch runs on the exempt Wyckoff-**regime** field; the
    phase-regression sub-branch consumes the **entry-phase (A–E)**, a non-exempt `positions.md` **rider** (parallel
    to the existing IV-rank rider) that degrades to data-absent when missing while the regime sub-branch still
    evaluates. Position-context schema split into an "Entry-time Wyckoff regime" (advisory-required) row + an
    "Entry-time Wyckoff phase (A–E)" (recommended rider) row.
  - Re-keyed: Principle snapshot list, the advisory branch, SIGNAL + WYCKOFF source rows, the WYCKOFF cross-ref,
    the branch-evaluability reference table, and the entry-time-context prose; "succession table" → "succession
    graph". PORTFOLIO has no legacy anchors (net-new v3.0) — no historical note needed.
  - Not in scope (correctly unchanged): the §A2 ingest structure/direction derivation (already lowercase +
    BULLISH/BEARISH from #73/#75).
- **`INDEX.md`** — bumped both version tables (3.0.3 → 3.0.4) and updated the §A1 status bullet (Stage C PORTFOLIO done).

### Verification
Adversarial workflow pass (faithfulness, completeness, apply-readiness): faithfulness + apply-readiness `pass`
(branch matches SIGNAL verbatim; all 8 anchors unique); `apply-with-fixes` for two stale-`phase` stragglers
(lines 111, 26), both folded in. `verify_frontmatter` + `verify_anchors` pass; dangling-vocab grep clean.

### Scope notes — deferred under #78
- **PASS1** (Stage D): veto/direction re-key + `SOS`/`SOW` → `sos`/`sow` + hostile-macro bullish-scope.
- **DEALER**: bearish-mirror DGPI band (referenced by SIGNAL + RISK; the spot-vs-flip advisory branch is already symmetric).
- **WYCKOFF**: decision-layer bearish column + "conditional-top" normalization.
- **JOURNAL_MGMT** (Stage D): write `entry_phase` (A–E) + `phase_c_confirmed` as the riders PORTFOLIO now consumes.
- **SIGNAL** ("floor"→"conditional floor"), GUARDRAILS, REPORT_FORMAT, SYSTEM_PARAMS per the prior slices.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage C consumer re-key, RISK (symmetric sizing bands) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage C (RISK consumer; substantive; HITL, approved turn-by-turn in session)

Re-keys RISK to the two-axis canonical model and makes the sizing bands **direction-relative/symmetric**, so RISK
enforces the per-regime band ceilings that SIGNAL (3.0.3) references and WYCKOFF (3.0.7) decision layer defines.
#78 stays open (P4 + remaining consumers).

- **`llm_runtime/RISK_v3.0.md`** (`kb_version 3.0.0 → 3.0.1`):
  - **Direction-relative symmetric sizing bands.** The band ceiling is set by the position's regime read relative to
    its direction (WYCKOFF's decision layer is long-framed; bearish = mirror): direction-aligned trend (`markup`
    long / `markdown` long put) and post-phase-C continuation branch (`reaccumulation`/`redistribution`) → **upper**;
    post-phase-C base regime (`accumulation`/`distribution`) → **conditional-top**; pre-phase-C → **conditional
    floor**; non-aligned regime / `ranging_undefined` / `UNKNOWN` → **long-premium band closed**. A long put in
    `markdown` earns the upper band, mirroring a long call in `markup`. v2.3 named-band magnitudes (3%/2%/1%/0.5–1%,
    5% ceiling) preserved unchanged; only the regime→band mapping is re-keyed and mirrored.
  - **Phase-C confirmer** is `spring`/`shakeout` (bullish) / `utad` (bearish) throughout.
  - **JD2 reconciliation:** pre-phase-C long-premium is *default-refused by the SIGNAL Wyckoff veto* and sized at the
    conditional floor only under operator override — resolving a prior SIGNAL↔RISK tension (SIGNAL refused it; old
    RISK gave it "conditional sizing").
  - Near-flip step-down ladder and the dealer-narrowing heuristic made direction-aware; every ladder rung is a real
    reduction (both ~1% bands step to the conditional floor ~0.5%).
  - Re-keyed: Principle, "Wyckoff regime sets the band ceiling" heuristic (renamed), inputs table (Wyckoff + dealer
    rows), entry-point checklist, WYCKOFF cross-ref, Appendix sizing-band table (9 direction-relative rows). Legacy
    RISK_005 preserved **verbatim** with a historical note (incl. a redirect for the renamed heuristic).
- **`INDEX.md`** — added RISK to both v3.0.1 version tables (3.0.0 → 3.0.1) and updated the §A1 status bullet (Stage C RISK done).

### Verification
Two adversarial workflow passes (faithfulness, cross-file consistency, completeness, apply-readiness): the first
returned `revise` (bullish phase-C token, a no-op near-flip ladder rung, two missed long-only sites); all folded
in; the re-verify returned `apply-as-is` / `apply_ready: true`. `verify_frontmatter` + `verify_anchors` pass;
dangling-vocab grep clean outside RISK_005 + the historical note.

### Scope notes — deferred under #78
- **DEALER**: bearish-mirror DGPI band for the direction-aware narrowing/veto (shared with SIGNAL's deferred item).
- **WYCKOFF**: decision-layer table is long-framed (consumers read it direction-relative); normalize the
  post-phase-C base-regime band name (line 182 "conditional range" / line 337 "top-of-conditional" → "conditional-top").
- **SIGNAL**: tighten the bare "floor" in its committed band sentence to "conditional floor" (RISK now has two floors).
- **JD1** (conditional-top magnitude ~1%) and **JD3** (bearish dealer mirror) remain operator-tunable.
- PORTFOLIO/PASS1/REPORT_FORMAT/SYSTEM_PARAMS per the SIGNAL slice follow-ups.

## 2026-06-28 — Stage 1b: §A1 reconciliation — Stage C consumer re-key, SIGNAL (symmetric veto + forward-test confluence) (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, Stage C (SIGNAL consumer; substantive; HITL, approved turn-by-turn in session)

Re-keys the first consumer file to the two-axis canonical model committed in Stage B, and — per two operator
decisions made this session — makes the veto layer direction-aware and wires the viewer's forward-tested targets
into the exit triggers. #78 stays open (P4 + remaining consumers).

- **`llm_runtime/SIGNAL_v3.0.md`** (`kb_version 3.0.2 → 3.0.3`):
  - **Direction-aware / symmetric veto layer** (operator-approved). The Wyckoff veto now evaluates against the
    candidate's resolved direction: bullish refused in `distribution`/`redistribution`/`markdown` or accumulation-family
    pre-`spring`; bearish refused in `accumulation`/`reaccumulation`/`markup` or distribution-family pre-`utad`; either
    direction refused in `ranging_undefined` or `UNKNOWN`. Long puts get a first-class bearish path mirroring long
    calls. The dealer-timing veto's hostile-macro branch is scoped to bullish long-premium (puts stay the aligned
    redirect), reconciling it with GUARDRAILS' "Long puts — Eligible — directional alignment with regime."
  - **Two-axis re-key** of the directional fallback (`sos`/`sow`), the regime exit advisory (unfavorable regime move
    per the succession graph read relative to the position's direction, OR a phase regression D→B/A), and all
    propagation tables (firing-condition summary matrix, vocab-alignment, metric-vocabulary, input/output tables,
    WYCKOFF cross-ref). Fixes a factual error: `utad` confirms distribution **phase C** (was "phase E"). Resolves the
    `lps`/`lpsy` side-awareness per the viewer glossary (`lps`=support, `lpsy`=supply; exit anchors selected by side).
  - **Forward-tested-target confluence annotation** (operator-approved) on the Stop & Profit-target exit triggers:
    the broker exit level stays a structural+validated anchor (anti-hallucination floor untouched); the viewer's
    forward-tested `pt_*` target + `*_prob` calibrated hit-rate rides as a confidence annotation on that level —
    surfaced, never emitted as the trade's price. New exit-output-field row + metric-vocab term.
  - Legacy `SIGNAL_00x` anchors preserved verbatim with a historical note.
- **`llm_runtime/PASS2_VALIDATION_v3.0.md`** (`kb_version 3.0.2 → 3.0.3`): the §12 hygiene's permissive "v2 targets
  *may* be surfaced as expectancy context" becomes a defined carry — the forward-tested target + `*_prob` is carried
  as the forward-tested confidence annotation on the SIGNAL exit anchor; Pass 2 re-derives/validates the level, the
  hit-rate rides as confidence, never as the trade's price.
- **`INDEX.md`** — bumped both version tables (SIGNAL 3.0.2→3.0.3, PASS2 3.0.2→3.0.3) and updated the
  §A1-reconciliation status bullet (Stage C SIGNAL done).

### Verification
Three adversarial workflow passes (symmetric-logic correctness, faithfulness to WYCKOFF, cross-file consistency,
completeness, and apply-readiness). All confirmed issues folded in; anti-hallucination floor verified intact; every
OLD anchor confirmed against the live files before applying. `verify_frontmatter` + `verify_anchors` pass;
dangling-old-vocab grep clean outside the legacy-anchors block and the v2.3-mapping column.

### Scope notes — deferred to later slices under #78
- **RISK** (Stage C): mirrored bearish sizing bands (`markdown`/`redistribution` upper; `distribution` conditional-top)
  + the regime rows, so RISK enforces what SIGNAL names.
- **PORTFOLIO_MGMT** (Stage C/D): add the D→B/A phase-regression branch; make the advisory direction-aware;
  "succession table" → "succession graph".
- **PASS1** (Stage D): veto/direction re-key (post-Spring → post-phase-C; reaccumulation/redistribution; symmetric
  bearish; ranging/UNKNOWN); `SOS`/`SOW` → `sos`/`sow`; hostile-macro → bullish-scoped.
- **DEALER**: define the bearish-mirror DGPI band for the per-ticker dealer-timing veto.
- **WYCKOFF**: add a "projected markdown target" structural-level row (the downside analog SIGNAL now references via
  the Ice-level projection); reconcile `utad` routing in the downstream-flow table.
- **REPORT_FORMAT** (Stage E): render the forward-tested-confidence suffix on the exit-plan row.
- **SYSTEM_PARAMS**: parametrize the forward-tested-target "confluence band" tolerance.

## 2026-06-27 — Stage 1b: §A1 Wyckoff-vocabulary reconciliation — P2+P3 WYCKOFF core rewrite (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, P2+P3 of 4 (Stage B, WYCKOFF core; substantive; HITL, approved turn-by-turn in session)

The KB adopts the viewer/v2 two-axis Wyckoff model as its own canonical model — **value-preserving**, because
flattening the viewer's 7 regimes to the legacy 4 phases at ingest would log `reaccumulation` (the viewer's
highest-hit-rate context) as `markup` and so break the Stage-3 calibration loop the integration exists to build.
This is the anchor slice (Stage B); the consumer files follow in Stages C–E. #78 stays open (P4 + consumers).

- **`llm_runtime/WYCKOFF_v3.0.md`** (`kb_version 3.0.6 → 3.0.7`):
  - **Verbatim canonical vocabulary (Appendix).** Embeds the operator-supplied viewer/v2 glossary **byte-faithfully**
    as the single source of truth — regime (7), phase (A–E), event (~27), and concept tables. The body no longer
    paraphrases these definitions; it points to the Appendix block.
  - **Two-axis model.** Principle rewritten to the **regime** (cycle-stage) × **phase** (A–E schematic) axes with
    events as the landmarks. Seven regimes: `accumulation`, `reaccumulation`, `markup`, `distribution`,
    `redistribution`, `markdown`, `ranging_undefined`. `UNKNOWN` clarified as a *session-state* (no read this
    session), distinct from the *confirmed* `ranging_undefined` stand-aside.
  - **Succession graph (decision layer).** Replaces the strict four-phase cycle with a regime decision-layer table
    (eligibility + sizing-band ceiling per regime) and a favorable/unfavorable succession **graph** —
    `reaccumulation`/`redistribution` are continuation branches, not loop steps. The Regime exit advisory fires on
    an unfavorable regime move (toward the refusal set) or a phase regression (D→B/A).
  - **Vocabulary re-key.** Validity gate, event-to-regime priority table, event reading guide, structural-levels
    table, and propose-confirm examples re-keyed to the lowercase vocabulary; `AR_TOP` → `ar_dist` everywhere except
    legacy anchors; the stale "ST not delivered by the viewer" note corrected (`st`/`st_dist` are in the canonical
    set); `structure_conflict:true` example corrected to `== "conflict"`.
  - **Legacy anchors** (`WYCKOFF_PHASE_*` / `WYCKOFF_EVENT_*`) preserved **verbatim** for back-compat (decision D-e),
    with a single historical note marking the superseded four-phase model and redirecting "phase-succession table"
    pointers to the new "Regime model and succession graph."
- **`INDEX.md`** — bumped both version tables (3.0.6 → 3.0.7) and updated the §A1-reconciliation status bullet
  (P1 + P2 + P3 done; P4 and the consumer files pending).

### Scope notes
- Pending under #78: **P4** (viewer `dealer_confidence`/`position_vs_flip` vocab vs Schwab Pass-2 dealer-status) and
  the **consumer files** — SIGNAL/RISK/PORTFOLIO (Stage C), JOURNAL/PASS1/PASS2/GUARDRAILS (Stage D),
  REPORT_FORMAT/DEALER/SYSTEM_PARAMS (Stage E) — then validate + golden(bullish)+bearish pilot and the
  `_v3.0 → _v4.0` rename sweep (Stage F).
- Decisions locked this slice: D-a succession graph; D-b estimation path = regime-setting subset, viewer-ingest =
  full vocab; D-c `dealer_confidence` (Pass-1) and FULL/LIMITED/INVALID (Pass-2) kept as two layers; D-d GUARDRAILS
  exempt stays 5 fields (`entry_wyckoff_phase` holds the regime; `entry_phase`/`phase_c_confirmed` non-exempt riders);
  D-e legacy anchors verbatim.
- The viewer producer already emits these values correctly; this unit aligns the KB consumer.

## 2026-06-27 — Stage 1b: §A1 Wyckoff-vocabulary reconciliation — P1 force-flag value fix (#78)

### Changed — §A1 Wyckoff-vocabulary reconciliation, P1 of 4 (substantive; HITL, approved turn-by-turn in session)

A real Copy Pass-1 export + the viewer's canonical Wyckoff glossary (operator-supplied) showed the KB §A1 layer
assumed value encodings the producer does not emit. Design (D1–D4) approved with the operator: adopt the viewer's
two-axis regime(7)+phase(A–E) model and lowercase ~27-event vocabulary. Landing in parts under #78; this is **P1,
the safety fix** (the issue stays open until P4).

- **`llm_runtime/WYCKOFF_v3.0.md`** (`kb_version 3.0.5 → 3.0.6`) — re-keyed the two hard force-flags to the real
  string encodings: `structure_conflict == "conflict"` (was boolean `true`) and `weekly_agrees == "conflict"` (was
  boolean `false`; values are `"agree"`/`"conflict"`/`"neutral"` — only `"conflict"` fires, `"neutral"` does not
  fire but is not clear confirmation). Updated the force-flag-input-completeness examples to the string encodings.
  Without this the force-flags silently never fired against live data, so a structurally-conflicted or
  HTF-disagreeing reading could auto-accept.
- **`INDEX.md`** — recorded the bump in both version tables and added a §A1-reconciliation status bullet (P1 done;
  P2–P4 pending).

### Scope notes
- Pending under #78: **P2** (event vocabulary — adopt the lowercase ~27-event set + classic a.k.a.; `AR_TOP`→`ar_dist`);
  **P3** (regime/phase two-axis model — regime(7) incl. reaccumulation/redistribution/ranging_undefined + phase A–E);
  **P4** (viewer `dealer_confidence`/`position_vs_flip` vocab vs Schwab Pass-2 dealer-status).
- The viewer producer already emits these values correctly; this unit aligns the KB consumer.
- New v4.0-era cross-references are version-less per the Stage-1 convention.

## 2026-06-27 — Stage 1b: §12 PASS2 hygiene — viewer/v2 outputs are Pass-1 context, not Pass-2 truth (closes #77)

### Changed — §12 PASS2 hygiene (substantive; HITL, approved turn-by-turn in session)

The PASS2-review bullet of Integration Plan §12. A read-only audit of `kapman-polygon-viewer` established that
the viewer emits no `volatility_chain_truncated` flag (it exists only in the plan's §12 note), so the planned
chain-quality-gate alignment is a no-op; this entry reflects that corrected reality.

- **`llm_runtime/PASS2_VALIDATION_v3.0.md`** (`kb_version 3.0.1 → 3.0.2`) — added the heuristic "When the eligible
  set arrived via a viewer/v2 handoff, its v2 outputs are Pass-1 context — not Pass-2 truth": the v2
  `pt_*`/`*_prob` price targets and calibration are not Pass-2 prices (Pass 2 derives the entry-price range from
  the validated chain and exit anchors from SIGNAL); the viewer IV/flip reads are Pass-1 triage only (Pass 2 uses
  Schwab ATM IV + the fresh Schwab dealer fetch); Pass 2 classifies the live Schwab chain's quality/truncation
  itself (PIPELINE_012) and consumes no Pass-1 chain-quality signal — the viewer emits none.
- **`docs/Kapman_System_Integration_Plan_v1.0.md`** §12 — corrected the PASS2-review bullet: the
  `isChainTruncated` ↔ `volatility_chain_truncated` alignment is N/A (the viewer emits no such flag; PASS2 owns
  its own check).
- **`INDEX.md`** — recorded the PASS2 bump in both version tables and added a §12 status bullet.

### Scope notes
- Producer-side finding (out of KB scope): the viewer's §A1 data largely exists in
  `GET /api/scan?include_options=true`, but the user-facing export is column-driven AG-Grid CSV with no envelope; a
  dedicated Pass-1 JSON export (download + clipboard) is being added to `kapman-polygon-viewer` separately.
- Out of scope (unchanged): the end-of-Stage-1 `_v3.0 → _v4.0` rename sweep.
- New v4.0-era cross-references are version-less per the Stage-1 convention.

## 2026-06-27 — Stage 1b: §A1 ingest hardening — cross-check resolution, required-field contract, force-flag completeness (closes #76)

### Changed — §A1 ingest hardening (substantive; HITL, approved turn-by-turn in session)

The Workflow-1 counterpart to #75, closing the §A1 gaps the Stage-1 pilot surfaced. Decisions taken with the
operator: the dealer/vol cross-check fields are **informational** (regime_confidence already nets them — an
independent gate would double-count); earnings stays a **KB-side lookup** (not a §A1 handoff field), SIGNAL's
existing no-date default left unchanged; an **absent** force-flag input downgrades a would-be auto-accept to
flagged rather than silently passing.

- **`llm_runtime/PASS1_SCREENING_v3.0.md`** (`kb_version 3.0.6 → 3.0.7`) — reworded the §A1 map's
  `dealer_consistent`/`volatility_consistent` row from a phantom "cross-check gate / conviction trim" to
  informational (already priced into `regime_confidence` per WYCKOFF); added a "§A1 ingest required-field
  contract" heuristic with per-field degradation for `exported_at`, `as_of`/`data_through`, `row_count`,
  `weekly_agrees`/`structure_conflict`, `regime`/`regime_confidence`, and earnings (clarified KB-side, not a
  handoff field), preserving the Pass 1 → Pass 2 Schwab-re-fetch boundary; clarified the Step-0 earnings source.
- **`llm_runtime/WYCKOFF_v3.0.md`** (`kb_version 3.0.4 → 3.0.5`) — added a **force-flag input-completeness**
  rule to the tier gate: a `weekly_agrees`/`structure_conflict` field that is absent (or present-but-null) cannot
  be evaluated, so a reading that would otherwise be `pipeline-accepted` is downgraded to `pipeline-flagged`
  ("force-flags unevaluated") and routed to the flagged-reading exchange — absence never reads as "clear." Scoped
  to those two fields (stale-snapshot is covered by the `as_of` validity check; SOW-gated markdown is an
  absence-detector). Amended the `pipeline-accepted` precondition, the tier-gate table, and the flagged-exchange
  reason bracket to match.
- **`llm_runtime/JOURNAL_MGMT_v4.0.md`** (`kb_version 4.0.1 → 4.0.2`) — added the missing-`exported_at`
  degradation to the lineage heuristic (lineage undeliverable → surfaced + logs flagged lineage-degraded; never
  a fabricated session-clock ID).
- **`docs/Kapman_System_Integration_Plan_v1.0.md`** §A1 — mirrored the cross-check rewording.
- **`INDEX.md`** — recorded the three version bumps (PASS1/WYCKOFF in both version tables; JOURNAL_MGMT in its
  Version-status bullet) and added a §A1 ingest-hardening bullet.

### Scope notes
- **Not** changed: SIGNAL Heuristic 0's no-earnings-date default (a separate SIGNAL judgment, deliberately out of
  scope); the viewer-producer emission of the required fields (`kapman-polygon-viewer` work — the KB states the
  contract + degradation only).
- Out of scope (unchanged): §12 PASS2 hygiene; the end-of-Stage-1 `_v3.0 → _v4.0` rename sweep.
- New v4.0-era cross-references are version-less per the Stage-1 convention.

## 2026-06-27 — Stage 1b: §A2/journal contract-hardening — derivation rules, positions.md grammar, partial-record (closes #75)

### Changed — §A2/journal contract-hardening (substantive; HITL, approved turn-by-turn in session)

Closes the §A2/journal under-specifications the Stage-1 pilot dry-run surfaced (including two real gaps in the
#73 §A2 source map). Scope is the tradelog→Portfolio→`positions.md` cluster; the §A1 items (cross-check
gate/trim, viewer export field set) remain a separate Workflow-1 follow-up. Decisions taken with the operator:
LEAP by **original DTE** (`expiration − entry_date`) ≥ the `LEAP_DTE_BAND` lower bound; debit/credit by the
**sign of summed `cost_basis`** across the `spread_group_id` legs (net-credit verticals flagged out-of-taxonomy,
not forced into a debit label); standalone `short_put` → **CSP** with collateral assumed; the `positions.md`
grammar as a **labeled-line key:value** record with a write-once / live-refresh split; SIGNAL partial-record
degradation **per-alert** (two four-field groups), regime degradation **per-field**.

- **`llm_runtime/PORTFOLIO_MGMT_v3.0.md`** (`kb_version 3.0.2 → 3.0.3`) — added a "§A2 structure/direction
  derivation rules" block to the Appendix (single-leg labels incl. uncovered short_call; LEAP original-DTE cutoff
  citing `LEAP_DTE_BAND`; spread debit/credit by summed `cost_basis` sign with the credit-spread out-of-taxonomy
  flag; thesis from structure+option_type, not the LONG/SHORT field). Hardened the "absent or partial"
  subsection: added a third condition — **record matched but field-level partial** — with per-field regime
  degradation and per-alert SIGNAL reconstruction, and a note that `option_mid` (Pass-2 reference) and
  `entry_price` (actual fill) are distinct fields, not a Step-1a reconcilable mismatch (with a Step 1a pointer).
- **`llm_runtime/JOURNAL_MGMT_v4.0.md`** (`kb_version 4.0.0 → 4.0.1`) — added a canonical **`positions.md`
  record grammar** to the Appendix: the `(instrument_key, account_id)` join key as two named tokens (not
  positional header text), one labeled line per field, the five entry-time regime fields (Wyckoff field
  constrained to WYCKOFF's four named phases; `entry_wyckoff_event` an optional non-exempt rider) + the eight
  SIGNAL levels + `option_mid` write-once, and a `mark`/`net_qty`/`unrealized_pnl`/`refreshed_as_of` live-refresh
  block overwritten in place. Fixed the line-40 live-field label `quantity` → `net_qty` to match the §A2 contract.
- **`INDEX.md`** — recorded both version bumps (PORTFOLIO in both version tables; JOURNAL_MGMT in its
  Version-status bullet) and added a §A2/journal contract-hardening bullet.

### Scope notes
- The five regime fields + eight SIGNAL levels in the new grammar equal the `KAPMAN_GUARDRAILS` exempt snapshot
  exactly; `entry_wyckoff_event` and the entry-time IV rank tier are explicitly non-exempt riders.
- Out of scope (separate follow-up): §A1 cross-check gate/trim + viewer export field set; §12 PASS2 hygiene;
  the end-of-Stage-1 `_v3.0 → _v4.0` rename sweep.
- New v4.0-era cross-references are version-less per the Stage-1 convention.

## 2026-06-27 — Stage 1b: KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS — wire the v4.0 journal session layer (closes #74)

### Changed — session entry sequence + orientation wired to the v4.0 journal layer (substantive; HITL, approved turn-by-turn in session)

KPSI predated the v4.0 journal layer (`kb_version 3.0.3`, 2026-05-29): it never loaded `kapman-journal`
memory, never minted/echoed a lineage_id or staged a handoff, and did not list `JOURNAL_MGMT_v4.0.md` in
its inventory — so the persistence layer #71/#72/#73 built was orphaned from the orientation file the
session reads first. A Stage-1 pilot dry-run (Workflows 1+2 against realistic pastes) confirmed the ingest
**logic is sound and the `(instrument_key, account_id)` `positions.md` bridge works**; every blocking gap
was session-wiring in KPSI. This unit closes them. Decisions taken with the operator: **extend Rule 7**
with the log-manifest sub-clause (preserving the rule number that JOURNAL_MGMT and §A5 cite); **reserve** the
4th (Calibration/Review) mode rather than activate it (its runbook is Stage 3 — no-dangling-capability).

- **`llm_runtime/KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md`** (`kb_version 3.0.3 → 3.0.4`) — added
  `JOURNAL_MGMT_v4.0.md` to the KB file inventory and the T2 tier-model row; expanded the session entry
  sequence from five to seven steps — new **step 2 "Load journal memory and announce"** (load `memory/`
  files, announce, live-input-overrides-memory precedence; cite JOURNAL_MGMT mechanics + GUARDRAILS floor)
  and new **step 4 "Derive lineage and stage the input handoff"** (lineage_id from `exported_at`,
  source-partitioned handoff write, in-session echo); reconciled the position-context step with the §A2
  export + `positions.md` Step 1a/1b and generalized "before screening output" → "before mode output";
  extended **Rule 7** with a log-manifest sub-clause (a logged determination without a staged journal entry
  is a Rule 7 failure); added a **reserved-mode note** for the Stage-3 Calibration/Review 4th mode. Keeps
  its `_v3.0` filename.
- **`INDEX.md`** — recorded the bump in both version tables and added a KPSI session-wiring bullet under
  "Version status."

### Scope notes
- Rule 7 also lives in the operator's session system prompt; the log-manifest extension must be mirrored
  there to be enforced (operator action, outside the KB).
- The Stage-1 pilot also surfaced a §A2/§A1 **contract-hardening backlog** (spread debit/credit derivation,
  LEAP DTE cutoff, standalone `short_put`→CSP, canonical `positions.md` grammar, entry-time Wyckoff phase
  normalization, §A1 cross-check "gate/trim", viewer export field set) — **out of scope here**, proposed as
  a separate follow-up.
- Out of scope (unchanged): §12 PASS2 hygiene; the end-of-Stage-1 `_v3.0 → _v4.0` rename sweep.
- New v4.0-era cross-references are version-less per the Stage-1 convention.

## 2026-06-27 — Stage 1b: Workflow 2 (trade log → Portfolio) §A2 ingest — PORTFOLIO_MGMT + PASS2 capture + plan §A2/§7 (closes #73)

### Changed — Workflow 2 (trade log → Portfolio) §A2 ingest path (substantive; HITL, approved turn-by-turn in session)

The Workflow-2 ingest unit of Integration Plan Stage 1b (§7, §A2, §A5). Wires the now-built/deployed
`kapman-tradelog` `portfolio_snapshot` export (`GET /api/export/portfolio-snapshot`, open-positions-only)
into Portfolio mode as the live §A2 producer, and captures the journal-owned entry-time baseline at Pass 2.
Design decisions taken with the operator: **join key `(instrument_key, account_id)`**; structure/direction
**derived** from the export's single-leg `structure` + `spread_group_id` + `option_type` + DTE (thesis from
structure+option_type, not the LONG/SHORT sidedness field); **MAE/MFE advisory display only**, never a
gate/trigger; absent/partial entry-context **degrades per-branch** — missing entry-time regime fields
suppress the affected Regime-exit branch (data-absent, not fired conservatively, not reconstructed), missing
SIGNAL alert levels fall through to current-session reconstruction.

- **`llm_runtime/PORTFOLIO_MGMT_v3.0.md`** (`kb_version 3.0.1 → 3.0.2`) — reconciled the Principle to the
  two-source model (live fields from the `portfolio_snapshot` export; entry-time snapshot + the eight SIGNAL
  levels from `positions.md`, written once at Pass 2); split workflow Step 1 into **1a** (ingest snapshot;
  live values override memory, surface mismatch; broker paste = fallback) and **1b** (read `positions.md`
  entry-context by `(instrument_key, account_id)`, orientation only). Added three Appendix subsections —
  "Tradelog `portfolio_snapshot` ingest — §A2 source map," "Entry-time context read — `positions.md`," and
  "When `positions.md` entry-context is absent or partial." Re-pointed the position-context schema Source
  column: live fields → **Tradelog snapshot (§A2)**; the five advisory-required entry-time regime rows + the
  eight SIGNAL alert rows → **`positions.md` (journal; written at Pass 2)**, with the entry-time IV rank tier
  re-pointed as a recommended journal rider (not part of the Pass-2 write). Added a `JOURNAL_MGMT_v4.0` upstream row and three
  cross-references (`JOURNAL_MGMT_v4.0`, `KAPMAN_GUARDRAILS` sole exemption, the §A2 contract).
- **`llm_runtime/PASS2_VALIDATION_v3.0.md`** (`kb_version 3.0.0 → 3.0.1`) — added the at-validation capture
  heuristic: the entry-time regime snapshot + the eight SIGNAL Stop/Profit levels + `option_mid` are written
  to `positions.md` (write-once; the regime snapshot + SIGNAL levels are the sole no-persist exemption,
  `option_mid` rides as a position fact; PASS2 owns trigger/timing, JOURNAL_MGMT owns path/schema; the
  Pass 1 → Pass 2 boundary and anti-hallucination floor are unchanged). Added a `JOURNAL_MGMT_v4.0`
  cross-reference.
- **`docs/Kapman_System_Integration_Plan_v1.0.md`** §A2 + §7 — corrected the source cells to the real
  per-leg `PortfolioSnapshotOpenLeg` fields and noted the export now exists; the live MAE/MFE row now reads
  **compute-on-export from `HistoricalMark`, gated by `open_excursions_available`, advisory** (was
  mis-attributed to `LotExcursion --include-open`); split the structure/direction cell to mark it derived;
  marked exit/realized fields out of scope (open-only export). Added a `**Last updated:** 2026-06-27` marker.
- **`INDEX.md`** — recorded the two version bumps in both version tables and added a Workflow-2 ingest bullet
  under "Version status."

### Scope notes
- `JOURNAL_MGMT_v4.0.md` and `KAPMAN_GUARDRAILS_v3.0.md` were **not** edited: they already own the
  `positions.md` write model and the sole no-persist exemption; this unit cites them, it does not restate them.
- MAE/MFE remains **advisory display only** — no gate, trigger, or sizing input (Stage-3 MAE/MFE tuning is
  out of scope).
- Out of scope (unchanged): closed-lot/§A3 feedback contract; Calibration/4th mode; §12 PASS2 hygiene; the
  end-of-Stage-1 `_v3.0 → _v4.0` rename sweep. Files keep their `_v3.0` filenames.
- New v4.0-era cross-references are version-less per the Stage-1 convention.

## 2026-06-26 — Stage 1b: viewer/v2 ingest — §A1 contract, WYCKOFF tier gate, kapman-mcp excision, τ params (closes #72)

### Changed — Workflow 1 (viewer → Pass 1) ingest path (substantive; HITL, approved turn-by-turn in session)

The Workflow-1 ingest unit of Integration Plan Stage 1b (§6, §A1, §A5, and the §12
`kapman-mcp` reconciliation). Repoints the Wyckoff pipeline-reading source to the live
viewer/v2 (Polygon) surface and excises the disconnected `kapman-mcp` tool surface and name.
Design decisions taken with the operator: **repoint + excise** `kapman-mcp` as a non-entity;
tier gate keys on **`min(regime_confidence, phase_confidence)`** (`regime_confidence` alone
when `phase_confidence` is null); **provisional** `τ_high = 0.70` / `τ_low = 0.45` pending
Stage-1 pilot calibration.

- **`llm_runtime/WYCKOFF_v3.0.md`** (`kb_version 3.0.3 → 3.0.4`) — replaced the two-path "MCP
  path / estimation path" runtime with **"viewer-ingest path / estimation path."** The viewer/v2
  reading now feeds a **confidence tier gate**: `g = min(regime_confidence, phase_confidence)` →
  `pipeline-accepted` at `g ≥ τ_high`, `pipeline-flagged` in `[τ_low, τ_high)` or on a hard
  force-flag, estimation path below `τ_low`. Hard force-flags (`structure_conflict`,
  `weekly_agrees:false`, stale snapshot, SOW-gated markdown) override a high confidence. Excised
  all `kapman-mcp` tool/name references (`get_wyckoff_proposal_context`, `get_metrics`,
  `get_metrics_batch`, `screen_watchlist`, `screen_symbols`); event/structural reads repointed to
  the viewer `last_event`/`setup_tags`/`range` fields; estimation path repointed to the live
  Polygon/Schwab surface. Reversed the prior "`regime_confidence` is not a validity criterion"
  note — viewer/v2 confidence (genuine [0, 0.95], already nets dealer/volatility cross-checks) is
  now the primary gate. Confirmation-status vocabulary preserved. Legacy anchors `WYCKOFF_PHASE_009`
  and `WYCKOFF_EVENT_013` re-pointed to their renamed heuristics.
- **`llm_runtime/PASS1_SCREENING_v3.0.md`** (`kb_version 3.0.5 → 3.0.6`) — added the **viewer/v2
  handoff as a candidate source** plus the **§A1 ingest map** (dual-path: paste now, tool later);
  a raw ticker list with no viewer fields remains valid (estimation path). Explicitly preserved the
  Pass 1 → Pass 2 boundary: dealer fields re-fetched live from Schwab at Pass 2, IV fields labeled
  *Needs chain validation*. Excised the `kapman-mcp` reference in the PIPELINE_010 anchor and the
  Step-3 workflow row.
- **`llm_runtime/SYSTEM_PARAMS_v3.0.md`** (`kb_version 3.0.1 → 3.0.2`) — added `TIER_GATE_TAU_HIGH`
  (0.70) and `TIER_GATE_TAU_LOW` (0.45), both **provisional, pilot-calibrated**; wired WYCKOFF and
  PASS1 into the consuming-files list; added two parameter-change-log rows. Invariant `τ_low ≤ τ_high`;
  `τ_high` must stay below the 0.95 confidence cap.
- **`INDEX.md`** — recorded the three version bumps in both version tables and added a Workflow-1
  ingest bullet under "Version status."

### Scope notes
- `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md` was **not** edited: its `get_dealer_metrics` call is a
  live **Schwab** tool (`Schwab get_dealer_metrics(["SPY"])`), not the `kapman-mcp` surface.
- `CHANGELOG.md` historical entries that mention `kapman-mcp` are left intact (history is not rewritten);
  the Integration Plan §12 already records the reconciliation.
- Files keep their `_v3.0` filenames pending the end-of-Stage-1 coordinated `_v3.0 → _v4.0` rename + cross-reference sweep.

## 2026-06-26 — Stage 1b spine: JOURNAL_MGMT_v4.0 runbook + memory/no-persist guardrail (closes #71)

### Added — journal persistence layer (substantive; HITL, approved turn-by-turn in session)

Spine of Integration Plan Stage 1b. Content drafted and approved chunk-by-chunk with
the operator before this commit.

- **`llm_runtime/JOURNAL_MGMT_v4.0.md`** (new T2 runbook, `kb_version 4.0.0`, `status: active`) —
  the public-instructions/private-data contract, session-start memory load + announce,
  live-input-overrides-memory precedence, lineage-ID derivation from the export's
  `exported_at` (`VS-`/`TL-` prefixes), the three logs (handoffs split by source; pass1/pass2
  outputs; one file per run, never reopened), the memory write model (overwrite-in-place,
  per-file triggers, write-once entry snapshot), the numeric-no-persist boundary with the
  sole entry-snapshot exemption, and the Rule 7 log-manifest tie-in. §A4 record shapes in
  the Appendix.
- **`llm_runtime/KAPMAN_GUARDRAILS_v3.0.md`** (`kb_version 3.0.2 → 3.0.3`) — added two T0
  guardrail blocks: *"Memory is convenience, not authority"* and *"Numeric regime reads are
  never persisted as authoritative"* (with the narrow entry-time-snapshot exemption). Added
  two downstream-enforcement rows and a cross-reference bullet pointing at `JOURNAL_MGMT_v4.0.md`.
  No legacy anchor (new behavior).
- **`docs/Kapman_System_Integration_Plan_v1.0.md`** §4 + §A4 — adopted **source-split handoffs**
  (`handoffs/viewer/` + `handoffs/tradelog/`), superseding the single-`handoffs/` layout. The
  `kind`/`source` frontmatter is retained for machine-parsing and now corroborates the path.
- **`INDEX.md`** — recorded the new v4.0 file and the guardrail edit under "Version status."

### Conventions adopted (Stage 1)
- New v4.0-era content uses **version-less cross-references**; existing `_v3.0` files keep
  their filenames until a **coordinated `_v3.0 → _v4.0` rename + cross-reference sweep at the
  end of Stage 1**. This is why `KAPMAN_GUARDRAILS` gained v4.0 content while keeping its
  `_v3.0` name and a v3-track `kb_version`.
- Lineage prefixes: `VS-` viewer, `TL-` tradelog.

### Companion change (separate repo)
- `kapman-journal` handoffs scaffold reconciled to `handoffs/viewer/` + `handoffs/tradelog/`
  (direct-to-`main` per that repo's model; no issue).

## 2026-06-26 — v3.0 archived; v4.0 line opened (Integration Plan Stage 1a) (closes #70)

### Archived — v3.0 snapshot + version cutover (mechanical; autonomous half of Stage 1a)

Mechanical archive + version-bookkeeping pass per the KapMan System Integration
Plan v1.0 (`docs/Kapman_System_Integration_Plan_v1.0.md`) §10/§11. No content
authoring — the substantive v4.0 work is Stage 1b (human-in-the-loop).

- **`archive/v3.0/`** — froze a read-only, byte-identical snapshot of the current
  v3.0 runtime, preserving the upload split: `archive/v3.0/llm_runtime/` (15 files,
  incl. `REPORT_TEMPLATE_PASS1_v3.0.html`) + `archive/v3.0/engineering_only/`
  (9 files). `archive/v2.3/` untouched.
- **`v3.0` git tag** — placed at the cutover commit to mark the v3.0 line.
- **`INDEX.md`** — added a "Version status" section: v4.0 is the active (in-progress)
  line opened per Stage 1a; v3.0 is archived. The existing v3.0 inventory and
  v2.3→v3.0 migration tables are left intact — they remain authoritative for both
  the archived snapshot and the still-live `_v3.0` working files.

### Deliberately deferred to Stage 1b (HITL — not in this pass)

- No rename of live `_v3.0` files to `_v4.0` and no `kb_version` bumps. The
  major-version filename bump is coupled to each file's substantive v4.0 rewrite,
  not to this cutover; renaming byte-identical files now would assert false version
  state and is the non-substantive rename the naming convention forbids.
- No v3.0→v4.0 migration table (no v4.0 anchors exist yet).

## [3.0.9] — 2026-05-29

### Changed — Mechanical KB hygiene pass

- **REPORT_TEMPLATE_PASS1_v3.0.html** — Header comments only (CSS unchanged):
  - Style citation updated: `REPORT_STYLE_v3.0.2` → `REPORT_STYLE_v3.0.3`
  - Format citation updated: `REPORT_FORMAT_v3.0.7` → `REPORT_FORMAT_v3.0.8`
  - Reference CSS comment label updated: `REPORT_STYLE_v3.0.2` → `REPORT_STYLE_v3.0.3`
- **SIGNAL_v3.0.md** — Removed `(forthcoming)` qualifiers for now-active runtime files only:
  - `PASS1_SCREENING_v3.0.md`
  - `PASS2_VALIDATION_v3.0.md`
  - `WYCKOFF_v3.0.md`
  - `PORTFOLIO_MGMT_v3.0.md`
  - `REPORT_FORMAT_v3.0.md`
  - Preserved `(forthcoming)` on `engineering_only/*` references.
- **SIGNAL_v3.0.md** frontmatter metadata updated:
  - `kb_version: 3.0.1` → `3.0.2`
  - `file_last_updated: 2026-05-13` → `2026-05-29`

## 2026-05-31 — KB audit conflict sync (Claude.ai session 2026-05-31)

### Fixed — version-tracking drift, stale cross-references, INDEX table hygiene

- **WYCKOFF_v3.0.md** — Backfilled CHANGELOG and INDEX records for the
  2026-05-16 content change (kb_version 3.0.2 → 3.0.3) committed without a
  CHANGELOG entry or INDEX update. The 3.0.3 change added the
  `get_wyckoff_scan` / `get_batch_wyckoff_scan` features-block field list to
  the Appendix and the `historical_volatility` field (annualized 20-day,
  log-returns; from the kapman-trader `feat: add historical_volatility to
  compute_wyckoff_snapshot()` patch). No frontmatter change in this entry —
  file was already at 3.0.3 / 2026-05-16; this documents it after the fact.

- **REPORT_STYLE_v3.0.md** — Badge vocabulary table: removed the stale
  `Weak chain` label from the `.tag-red` example-labels list. Chain-quality
  `Weak chain` maps to `.tag-orange` per the Badge label mapping table, the
  template legend, and REPORT_FORMAT 3.0.8 legend element #3; the `.tag-red`
  listing was a leftover from the 3.0.3 edit that moved chain-quality Weak to
  orange. `INVALID` (dealer-status) remains on `.tag-red`.
  (kb_version 3.0.3 → 3.0.4)

- **REPORT_TEMPLATE_PASS1_v3.0.html** — Comment-only: swept stale
  REPORT_FORMAT version references to v3.0.8 (banner "Format:
  REPORT_FORMAT_v3.0.7" → v3.0.8; SCREENING TABLE comment "Column order
  (REPORT_FORMAT_v3.0.3 Appendix)" → v3.0.8; LEGEND/FOOTER comment
  "(REPORT_FORMAT_v3.0.7 Appendix)" → v3.0.8). No structural, placeholder,
  CSS, or Style-banner changes.

- **INDEX.md** — Reconciled version-tracking tables to file frontmatter:
  WYCKOFF_v3.0.md 3.0.2 → 3.0.3 (both tables; date 2026-05-14 → 2026-05-16);
  KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md 3.0.2 / 2026-05-28 →
  3.0.3 / 2026-05-29 (file and CHANGELOG were already at 3.0.3; INDEX row was
  stale); REPORT_STYLE_v3.0.md 3.0.3 / 2026-05-29 → 3.0.4 / 2026-05-31.
  Also normalized the "v3.0 file directory" table: six rows
  (PASS2_VALIDATION, PORTFOLIO_MGMT, REPORT_STYLE, REPORT_TEMPLATE_PASS1,
  REPORT_FORMAT, SYSTEM_PARAMS) carried stray Session/Status columns and, in
  two cases, a wrong doc_type. Reconciled all to the 4-column
  path|tier|doc_type|role schema; corrected REPORT_FORMAT doc_type
  style → format, PASS2 doc_type to runbook, SYSTEM_PARAMS doc_type to
  reference; dropped stale "Draft" labels (all files are active per the
  Session-14 verification table and file frontmatter).

### Root cause
Claude.ai KB audit session 2026-05-31 found WYCKOFF 3.0.3 (2026-05-16) had
been committed without the AGENTS.md housekeeping steps (INDEX row, CHANGELOG
entry); residual cross-reference lag from the 2026-05-29 batch; and
long-standing column drift in the INDEX directory table. All content changes
reviewed and approved by operator before this prompt issued.

## [3.0.8] — 2026-05-29

### Fixed — KB audit conflicts (Claude.ai session 2026-05-29)

- **REPORT_STYLE_v3.0.md** — Alignment heuristic: removed "no exceptions" and
  "prior rule rescinded" language; explicitly authorized `text-align: center` for
  the eight named short numeric/date screening-table columns (`.col-ticker`,
  `.col-wyckoff`, `.col-dgpi`, `.col-strike`, `.col-exp`, `.col-entry`,
  `.col-exit`, `.col-confidence`). Added all eight classes to the Column widths
  table with alignment noted. This resolves the conflict between the heuristic's
  blanket left-align mandate and the template extension classes that have always
  rendered those columns centered. The centering remains authoritative in the
  template extensions; REPORT_STYLE now explicitly permits it.
  Badge vocabulary: "Chain quality: Invalid / INVALID / .tag-red" row updated to
  "Chain quality: Weak / Weak chain / .tag-orange" to match PASS2's vocabulary.
  (kb_version 3.0.2 → 3.0.3)

- **KAPMAN_GUARDRAILS_v3.0.md** — Near-flip heuristic and appendix: replaced
  fixed-dollar approximation ("roughly a dollar", "roughly $1") with a named
  parameter reference (`NEAR_FLIP_BAND_PCT`, currently ±0.25% of spot per
  SYSTEM_PARAMS). Eliminates drift between the guardrail prose and the
  authoritative parameter definition.
  Data-quality vocabulary table: "Weak chain" row pointer updated from
  `DEALER_v3.0.md` (incorrect) to `PASS2_VALIDATION_v3.0.md / engineering_only`
  (correct — chain quality classification is a Pass 2 / engineering-only concept,
  not a DEALER concept).
  (kb_version 3.0.1 → 3.0.2)

- **REPORT_TEMPLATE_PASS1_v3.0.html** — Legend/footer stale comment updated:
  "REPORT_FORMAT_v3.0.3 Appendix" → "REPORT_FORMAT_v3.0.7 Appendix".
  Chain quality badge key: third badge changed from
  `<span class="tag tag-red">INVALID</span>` to
  `<span class="tag tag-orange">Weak chain</span>` to match PASS2's
  Full / Limited / Weak vocabulary. INVALID is dealer-status vocabulary, not
  chain-quality vocabulary.

- **REPORT_FORMAT_v3.0.md** — Legend/footer element #3 definition updated:
  "Invalid chain: dropped from Pass 2" → "Weak chain: insufficient liquidity;
  dropped from Pass 2". Aligns with PASS2 chain-quality vocabulary.
  (kb_version 3.0.7 → 3.0.8)

### Root cause
Claude.ai KB audit session 2026-05-29 identified four confirmed conflicts against
source files. All content changes reviewed and approved by operator in that session
before this Codex prompt was issued.


## [3.0.7] — 2026-05-28

### Fixed
- **PORTFOLIO_MGMT_v3.0.md** — Step 6: Added explicit fallback path when entry-time
  Stop/Profit alert levels are absent from position context. Previously, absence caused
  full suppression of exit-trigger output. Now: apply SIGNAL delta-gamma approximation
  and trail-stop reference band from current-session data (Schwab dealer flip as Stop
  anchor, nearest call wall as Profit target anchor, SIGNAL band for trail values).
  Surface all four mandatory fields with inline note. (kb_version 3.0.0 → 3.0.1)
- **PORTFOLIO_MGMT_v3.0.md** — Step 7: Replaced single-line assembly step with numbered
  sub-sequence 7a–7e. Step 7a requires a pre-output field manifest before any position
  block is generated. Step 7b requires per-position field confirmation with named
  fallbacks. Step 7d requires a post-generation self-audit result statement.
- **REPORT_FORMAT_v3.0.md** — Added mandatory pre-output self-audit checklist table to
  Appendix, immediately before the per-position detail subsection sequence. Enumerates
  all 11 required per-position fields with fallback paths. Suppression without a named
  reason is a Rule 5 violation per this table. (kb_version 3.0.6 → 3.0.7)

### Added
- **KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md** — New section "Runtime operational
  rules" added before Legacy anchors. Contains Rule 7 (pre-output self-audit mandate)
  with reference to REPORT_FORMAT mandatory field table as the Portfolio mode checklist
  authority. (kb_version 3.0.1 → 3.0.2)

### Root cause
Portfolio management session 2026-05-28 identified that PORTFOLIO_MGMT Step 6 correctly
noted absent entry-time context but incorrectly suppressed exit-trigger output entirely
rather than applying SIGNAL fallback mechanics. The pre-output manifest pattern was
identified as the highest-reliability catch mechanism. All content approved in Claude.ai
session 2026-05-28.

### Post-merge operator action required
Rule 7 (above) must be appended to the Rules 1–6 block in the Claude.ai session system
prompt settings. The KB record alone is retrieval-based and does not guarantee
always-in-context enforcement.

## [3.0.5] — 2026-05-14

### Added
- **Alternatives Summary section** (REPORT_FORMAT, template, PASS1_SCREENING)
  Option B implementation: new sanctioned report section between the
  screening table and per-ticker detail, authorized exclusively for
  NO_TRADE and WAIT candidates. Provides six subsections per block
  (Refusal/deferral reason 20w · Wyckoff read 25w · Dealer read 25w ·
  Volatility read 25w · Alternatives 30w · Recheck trigger 20w;
  aggregate cap 145w). Eligible candidates are unaffected.
  Resolves the content-loss tradeoff surfaced in Mag-7 Pass 1 testing
  (session 12, 2026-05-14): NO_TRADE and WAIT candidates now have a
  compliant, sanctioned home for extended regime context and
  alternative structures, without violating the 20-word Rationale
  cell cap or producing non-compliant detail blocks.

### Changed
- REPORT_FORMAT_v3.0.md: section-order definition updated to include
  Alternatives Summary; new section spec added with subsection table
  and aggregate word cap.
- REPORT_TEMPLATE_PASS1_v3.0.html: new `.alt-summary` skeleton block
  with pre-render checklist; per-ticker detail checklist updated to
  reference Alternatives Summary as the correct home for NO_TRADE/WAIT
  content.
- PASS1_SCREENING_v3.0.md: NO_TRADE and WAIT output-state definitions
  updated with cross-reference to Alternatives Summary section.

### Files changed
- llm_runtime/REPORT_FORMAT_v3.0.md (3.0.4 → 3.0.5)
- llm_runtime/REPORT_TEMPLATE_PASS1_v3.0.html (3.0.4 → 3.0.5)
- llm_runtime/PASS1_SCREENING_v3.0.md (3.0.4 → 3.0.5)

## 2026-05-14

**Fixed.** Pass 1 report PDF/print rendering — Rationale column collapse in print mode despite previous min-width fix.

- `llm_runtime/REPORT_TEMPLATE_PASS1_v3.0.html` — added new `@media print` override block immediately after the existing `@media screen{.table-wrap{overflow-x:auto;}}` rule. The print override clears `min-width` to zero and `width:auto` on the nine `.col-*` columns plus `.scale-col`, removes `max-width:180px` and `word-break:break-word` on `.rationale-col`, shrinks `th`/`td` font to 6pt and padding to 1px/2px in print, and adds `page-break-inside:avoid` on screening rows.

Rationale: the previous min-width change (commit bb897e2) was necessary but insufficient. The screen path uses `@media screen{.table-wrap{overflow-x:auto;}}` which allows the table to exceed its container width — that masked the column-overflow problem on screen. In print, no equivalent override existed, so the browser compressed the only flexible column (Rationale) to fit, and the `word-break:break-word` rule produced single-character vertical text. The new `@media print` block strips the column floors and rationale caps under print only, leaving the screen path unchanged.

## 2026-05-14

**Fixed.** Print/PDF rendering of Pass 1 reports — Rationale column collapse to vertical text.
**Added.** Pre-render checklist comments in REPORT_TEMPLATE_PASS1_v3.0.html (screening-table tbody and per-ticker detail section) — Option B template-internal enforcement.

- `REPORT_TEMPLATE_PASS1_v3.0.html` — CSS fix: changed nine `.col-*` rules in /* Template extensions */ block from `width:Npx` to `min-width:Npx`. Added `.screening-table{table-layout:auto;width:100%;}` rule.
- `REPORT_TEMPLATE_PASS1_v3.0.html` — added pre-render checklist comment inside screening-table `<tbody>` covering column structure (Rule 6), rationale 20-word cap, and NO_TRADE/WAIT row structure.
- `REPORT_TEMPLATE_PASS1_v3.0.html` — added pre-render checklist comment at top of per-ticker detail section covering eligibility filter (Eligible-only) and seven-subsection structure with word caps.

Rationale (CSS fix): fixed widths summed to ~822px across columns 1–11, exceeding the ~750px usable width of a landscape Letter print area at the configured 0.35"/0.3" margins. Rationale column was getting starved of horizontal space and rendering one character per line in print/PDF. Switching to `min-width` lets empty-cell columns collapse when content is "—" and gives the slack to Rationale.

Rationale (checklist comments): existing template comments are descriptive ("X is required") and have been observed to not prevent content-discipline violations at render time under content pressure. Imperative pre-render checklists with binary checks ("Verify X before emitting") are more likely to fire as procedural steps during template fill. Spec authority is unchanged (REPORT_FORMAT_v3.0.md); the checklists reference the spec, they do not duplicate it.

## [Unreleased]
### Added
- New file added: `llm_runtime/REPORT_TEMPLATE_PASS1_v3.0.html` (tier T3, doc_type template).
### Rationale
- Eliminates Pass 1 report format drift across runs by replacing prose-derived rendering with template-fill rendering.
- Companion runtime rule: Runtime Rule 6 added to session-opener runtime rules (not in this commit; operator-managed).
### Files changed
- llm_runtime/REPORT_TEMPLATE_PASS1_v3.0.html (new)
- INDEX.md (inventory row added)
- llm_runtime/REPORT_FORMAT_v3.0.md (cross-reference added; 3.0.3 → 3.0.4)
- llm_runtime/KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md (KB inventory updated; 3.0.0 → 3.0.1)

### Changed
- WYCKOFF_v3.0.md (v3.0.2): Removed Marketdata-MCP:get_price_metrics as a fallback source. Polygon MCP Server:get_options_metrics with include=['price'] is now the sole external fallback in the estimation-path prose and MCP inputs table fallback rows (Price metrics and Volatility metrics).
- WYCKOFF_v3.0.md (v3.0.1): Extended two-path runtime entry sequence to include screen_symbols as a batch triage tool alongside screen_watchlist (30-symbol cap; not a replacement for per-ticker get_wyckoff_proposal_context). Added bracketed table note for get_metrics_batch availability on the Inputs table.
- PASS1_SCREENING_v3.0.md (v3.0.1): Updated Step 3 workflow table to note get_metrics_batch availability for initial candidate-list metric fetch. Updated PIPELINE_010 legacy anchor to reference new kapman-mcp batch tools (get_metrics_batch, screen_symbols) as preferred full-payload batch surface; Polygon batch endpoint unchanged as avg_iv source.

## [REPORT_FORMAT 3.0.3] — 2026-05-13
### Changed
- Clarified that `session-meta-timing` CSS class is reserved for legend/footer element #5
  only; ticker-count summary data belongs in the report subtitle, not the legend/footer.
- Added explicit subtitle spec for Screening mode: session date, mode, watchlist name,
  tickers evaluated, and optional count breakdown belong in the subtitle line.
- Added note to legend/footer element #5 table clarifying class usage and placement rule.
### Rationale
Operator observed that production reports were rendering ticker-count summary data inside
a session-meta-timing span in the legend/footer instead of in the subtitle, and were
omitting the required 2-line run timing / token estimate block (element #5). The spec was
correct in the KB; the disambiguation note closes the interpretation gap that caused the
rendering error.
### Files changed
- llm_runtime/REPORT_FORMAT_v3.0.md (3.0.2 → 3.0.3)

## [KAPMAN_GUARDRAILS 3.0.1] — 2026-05-13
### Added
- New rule: Report format immutability. Section order, column sequence, color coding,
  data granularity, notes discipline, field caps, and legend/footer structure are fixed
  between runs unless the operator invokes an explicit recognized override (Summary,
  Top-N, or Section exclusion). Unilateral format changes by Claude are a guardrail
  violation.
### Rationale
Operator observed session-to-session format drift with no operator instruction. No KB
rule previously prohibited this. The new rule closes the gap and defines the three
recognized override types with required subtitle acknowledgment.
### Files changed
- llm_runtime/KAPMAN_GUARDRAILS_v3.0.md (3.0.0 → 3.0.1)

## [3.0.2] — 2026-05-13
### Changed
- REPORT_FORMAT_v3.0.md: Wyckoff Phase field #4 Notes cell replaced. Previous spec collapsed all non-pipeline-accepted states to "Unconfirmed", discarding the phase label. New spec always renders [Phase] ([status]) using a six-state rendering contract: pipeline-accepted (phase only or phase + event), confirmed, declared, pipeline-flagged (phase? suffix), unconfirmed (phase? suffix), UNKNOWN. Phase abbreviations defined to fit 20-char cap.
### Rationale
Operator observed that NO_TRADE and WAIT rows were rendering "Unconfirmed" with no phase label, making it impossible to distinguish a Distribution veto from an Accumulation pre-Spring gate without reading the rationale cell. The MCP delivers the pipeline regime in all cases; the new spec surfaces it always.
### Files changed
- llm_runtime/REPORT_FORMAT_v3.0.md (3.0.1 → 3.0.2)

## [3.0.1] — 2026-05-13
### Changed
- REPORT_FORMAT_v3.0.md: legend/footer session metadata element #5 expanded from 1-line to 2-line cap; line 1 carries run start timestamp, render timestamp, elapsed time, and token estimate; new operational heuristic defines timestamp recording discipline and runtime token-estimate formula (N_tickers × 4,000) + 60,000.
- REPORT_STYLE_v3.0.md: added .session-meta-timing{color:#666;} CSS class; note added to Legend/footer CSS block.
### Rationale
Operator requested run timing and token cost visibility in report footer. Timestamps recorded at MCP call boundaries, not reconstructed. Token estimate is a planning figure, not a metered count.
### Files changed
- llm_runtime/REPORT_FORMAT_v3.0.md (3.0.0 → 3.0.1)
- llm_runtime/REPORT_STYLE_v3.0.md (3.0.0 → 3.0.1)

## v3.0.1 — 2026-05-13

### Patch: Earnings-proximity veto

**Problem:** Pass 1 session 2026-05-13 placed NVDA, ZM, ZS, SNOW, MRVL, COST in the Eligible table alongside WAIT badges instead of routing them exclusively to WAIT — Earnings Proximity. No named veto or blocking-window parameters existed.

**Changes:**
- SYSTEM_PARAMS_v3.0.md: Added EARNINGS_BLOCK_DAYS = 7 and EARNINGS_CAUTION_DAYS = 21 to parameter table.
- SIGNAL_v3.0.md: Added Heuristic 0 — near-event-risk veto, fires before Wyckoff veto and all other trigger evaluation.
- PASS1_SCREENING_v3.0.md: Added Step 0 to per-candidate sequence; added near-event-risk screen heuristic; added WAIT sub-type rows to output state definitions table.

**Behavioral change:** Candidates with confirmed earnings ≤ 7d are immediately WAIT — no Eligible row, no pass-through to Pass 2. Candidates 8–21d out are WAIT with explicit operator-approval gate.

**Files touched:** SYSTEM_PARAMS_v3.0.md, SIGNAL_v3.0.md, PASS1_SCREENING_v3.0.md, CHANGELOG.md

## [3.0.0] — Session 15 — 2026-05-13

### Status promotion — alpha exit
- All 14 llm_runtime/ files promoted from draft to active.
- kb_version bumped from 3.0.0-alpha to 3.0.0 across all llm_runtime/ files and INDEX.md.
- KapMan KB v3.0.0 is complete.

## [3.0.0-alpha] — Session 15 (engineering_only/) — 2026-05-13

### New files
- engineering_only/DEALER_PIPELINE_v3.0.md (draft)
- engineering_only/PASS1_MCP_REFERENCE_v3.0.md (draft)
- engineering_only/PASS2_MCP_REFERENCE_v3.0.md (draft)
- engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md (draft)
- engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md (draft)
- engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md (draft)
- engineering_only/PORTFOLIO_MGMT_MCP_REFERENCE_v3.0.md (draft)

### INDEX.md
- All seven engineering_only/ files added to file inventory.
- Forthcoming annotations removed from rule-ID migration table rows for all covered legacy IDs.

## [3.0.0-alpha] — Session 14 — 2026-05-13

### Audit pass
- Full KB audit across all 14 llm_runtime/ files (revised run, RISK_v3.0.md present).
- Frontmatter integrity: PASS — all 14 files, all 6 fields correct.
- Cross-file reference resolvability: PASS — 0 dangling references.
- Named anchor resolution: PASS.
- Stale forthcoming annotations removed: 47 total across SIGNAL (38), VOLATILITY (6),
  WYCKOFF (3). Annotation removal only; no content changes.
- KB inventory status corrected in KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS: REPORT_STYLE
  and SIC_SECTOR_MAP updated from scaffolding → draft.
- Legacy anchors section added to KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS (no v2.3
  antecedents; statement-of-absence pattern).
- AGENTS.md: reduced-template policy added for doc_type: reference files in llm_runtime/.
- INDEX.md migration table verified/updated.
- INDEX.md completeness audit: complete for known legacy IDs; full verification pending
  operator review of archive/ source files.
- Session 15: apply remaining fixes, promote all 14 files draft → active.

## [3.0.0-alpha] — 2026-05-13 — Session 13

### Session 13 — 2026-05-13

### Added
- `SIC_SECTOR_MAP_v3.0.md` (T3, draft) — SIC range -> sector -> benchmark ETF lookup table.
  Replaces `SIC_SECTOR_ETF_MAPPING_v2.3.md`. Changes from v2.3: XLP added for Consumer Staples
  (was —); redundant point-code sub-rows consolidated to ranges; Python lookup code and Quick
  Reference table moved to engineering_only (not yet created — pending). No legacy rule IDs
  carried; v2.3 antecedent had none.

### Updated
- `REPORT_STYLE_v3.0.md` — scaffold replaced with session-11 draft content. Status: scaffolding -> draft.

## [3.0.0-alpha] — 2026-05-13 — Session 12

### Session 12 — 2026-05-13
- `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md`: scaffolding → draft.
  Added: Principle (T0 peer authority split), KB file inventory table (14 files),
  tier model (T0–T3 with conflict resolution protocol), mode detection (3 modes,
  5-step ordered sequence), session entry sequence (5-step blocking checklist).
  Dropped: Legacy anchors section (no rule IDs map here), Appendix section
  (no unhoused formulas — all migrated to domain files in sessions 1–11).
  RISK_v3.0.md added to KB inventory after upload confirmation.

## [3.0.0-alpha] — 2026-05-12 — Session 11

### Added
- Added `REPORT_STYLE_v3.0.md` (T3, draft). Direct successor to
  `KAPMAN_REPORT_STYLE_GLOSSARY_v2.3.md` (full migration). New v3.0
  content: four-level urgency hierarchy for portfolio row classes
  (`.advisory`, `.warn` DTE-decay use, `.exited`, `.expired`);
  `.tag-critical` badge class for Expired unacknowledged positions;
  `.flags-col` 200px column class for portfolio Flags field;
  body font-size corrected 7.8pt -> 7pt; print-color-adjust declarations
  made explicit; `rationale-col` 180px confirmed consistent with
  REPORT_FORMAT 20-word cap.

## [3.0.0-alpha] — 2026-05-12 — Session 10

### Added
- `REPORT_FORMAT_v3.0.md` (T3, status: draft): information architecture specification for KapMan report output. Defines section presence and ordering rules by mode (Screening, Portfolio, Hybrid), field ordering and caps, source bar placement contract, legend/footer sequencing contract, and output structure for per-ticker and per-position details.

## [3.0.0-alpha] — 2026-05-12 — Session 9

### Added
- `PORTFOLIO_MGMT_v3.0.md` (T2 runbook): Position lifecycle layer. Owns position context schema, Portfolio mode workflow sequence (7 steps), position lifecycle state machine (Open / Advisory / Exited / Expired), Regime exit advisory operationalization (4 branches), DTE decay warning, exit-trigger proximity evaluation, Hybrid mode regime data reuse, position entry recording, Exited and Expired position handling. Net-new v3.0 construct; no v2.3 antecedent.

### Changed
- `SYSTEM_PARAMS_v3.0.md`: Added `DTE_DECAY_WARNING_THRESHOLD = 21 calendar days`, consumed by PORTFOLIO_MGMT. Updated Workflow integration section to reference PORTFOLIO_MGMT. Updated Operational heuristics to name PORTFOLIO_MGMT as a behavioral owner. Updated `file_last_updated` to 2026-05-12.

## [3.0.0-session8] — 2026-05-11

### Added
- `llm_runtime/SYSTEM_PARAMS_v3.0.md` (T3): new single-source-of-truth reference for all operator-configurable trading parameters. Parameters owned: SWING_DTE_BAND (60–120 days), CSP_DTE_BAND (45–60 days), LEAP_DTE_BAND (12–24 months), IV_HV_ELEVATED_THRESHOLD (1.20), IV_RANK_EXTREME_FLOOR (75), NEAR_FLIP_BAND_PCT (0.25%).
- `llm_runtime/PASS2_VALIDATION_v3.0.md` (T2): full Pass 2 validation runbook replacing scaffold. Owns: seven-step validation workflow, chain quality classification (Full/Limited/Weak), spread-mandate three-outcome resolution, strike and expiration selection, PIPELINE_012 chain truncation behavioral contract, regime drift handling, Validated/Flagged/Rejected output states.

### Changed
- `llm_runtime/PASS1_SCREENING_v3.0.md`: hardcoded DTE literals replaced with SYSTEM_PARAMS parameter name references.
- `llm_runtime/SIGNAL_v3.0.md`: hardcoded DTE label strings replaced with SYSTEM_PARAMS parameter name references.
- `llm_runtime/VOLATILITY_v3.0.md`: SYSTEM_PARAMS pointer sentence added to IV/HV ratio bands Appendix table.
- `llm_runtime/DEALER_v3.0.md`: SYSTEM_PARAMS pointer sentence added to near-flip zone Appendix table.

### Fixed
- SWING_DTE_BAND corrected from 45–60 days (v3.0 authoring error) to 60–120 days per actual operator practice.
- CSP_DTE_BAND explicitly separated from SWING_DTE_BAND; confirmed at 45–60 days.

### Legacy anchors resolved
- PIPELINE_012 → PASS2_VALIDATION_v3.0.md § Legacy anchors
- VALIDATION_001 (PASS2 residue) → PASS2_VALIDATION_v3.0.md § Legacy anchors
- PIPELINE_011 (mis-filing) → confirmed PASS1-owned; mis-filing note in PASS2 Legacy anchors

## [3.0.0-alpha] — 2026-05-11

### Added
- `llm_runtime/PASS1_SCREENING_v3.0.md` (status: draft) — Pass 1 screening
  runbook (T2). Operationalizes the six-step eligible-set determination
  workflow, inline-sequential propose-confirm for multi-ticker runs, Pass 1
  IV source discipline (Polygon avg_iv), candidate zone format, and the
  Pass 1 / Pass 2 data-boundary rule (PIPELINE_011 compaction guard).
  Legacy anchors: PIPELINE_010 → engineering_only; PIPELINE_011 → this file;
  SCORING_001 → engineering_only.

## [3.0.0-alpha] — 2026-05-11

### Added
- `llm_runtime/WYCKOFF_v3.0.md` — Wyckoff phase and event principle file.
  Session 6 of 15 in the v3.0 rewrite cycle. Owns the propose-confirm
  protocol, four-phase vocabulary (Accumulation/Markup/Distribution/Markdown),
  named-event reading guide, structural levels, and session-scope UNKNOWN
  state. Maps all 26 legacy anchors (WYCKOFF_PHASE_001-013,
  WYCKOFF_EVENT_001-013). Four anchors deferred to forthcoming
  engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md
  (PHASE_007, PHASE_009, PHASE_013, EVENT_012).

## [3.0.0-alpha] — 2026-05-10

### 2026-05-10 — DEALER_v3.0.md content cutover (session 3 of 15)

- Content for `llm_runtime/DEALER_v3.0.md` drafted and approved in Claude.ai session 3 of 15.
- File status moved from `scaffolding` to `draft`.
- Architectural decision: pipeline-computation content (formulas, filter thresholds, weighting tiers, slope window, confidence cutoffs, runtime defaults) moved to forthcoming `engineering_only/DEALER_PIPELINE_v3.0.md`; runtime-relevant content (DGPI tier vocabulary, hostile macro composite, near-flip zone, dealer-status label semantics, stale-data handling, two-layer macro/ticker model) preserved in `llm_runtime/DEALER_v3.0.md`.
- All 14 v2.3 DEALER_NNN anchors preserved in INDEX.md migration table; zero DROPPED.
- DGPI tier bands established as v3.0 reference values: ≥ 50 strongly supportive; 20 to 49 moderately supportive; -19 to 19 near-neutral; -49 to -20 weakening; ≤ -50 hostile.
- Hostile macro composite locked in as v3.0 reference: SPY below gamma flip AND SPY DGPI ≤ -20.
- Near-flip zone locked in as v3.0 reference: symmetric ±0.25% of spot band around the gamma flip level (scales across SPY and per-ticker layers).

### Changed
- `RISK_v3.0.md` rewritten from scaffolding to draft. Sizing ladder expressed as regime-conditional judgment bands; v2.3 percentages preserved in Appendix as reference points. New real-capital-only denominator model replaces v2.3 combined-account denominator.

### Migrated
- `RISK_005` → `llm_runtime/RISK_v3.0.md` § Legacy anchors. Body-text references in legacy report legends continue to resolve.

### Dropped
- `RISK_001`, `RISK_002`, `RISK_003`, `RISK_004` — engineering-state observations about C4 pipeline behavior, no LLM runtime effect. See INDEX.md for rationale.

## v3.0.0-alpha-setup - 2026-05-10

Mechanical scaffolding complete. Directory structure, file skeletons,
legacy anchor extraction, and migration table generated per
MIGRATION_v2_to_v3.md. No rule content rewritten yet. v2.3 files
preserved in archive/v2.3/.

## 2026-05-29

### KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md — v3.0.2 → v3.0.3
- KB file inventory table: Status column updated from `draft` to `active`
  for all 13 .md file entries. No behavioral changes; documentation
  accuracy fix only. (REPORT_TEMPLATE row was already `active`.)

### REPORT_TEMPLATE_PASS1_v3.0.html
- Banner comment updated: Style v3.0.1 → v3.0.2, Format v3.0.3 → v3.0.7
- Reference CSS comment label updated to v3.0.2
- `th` text-align corrected: `center` → `left` (aligns with REPORT_STYLE
  v3.0.2 reference block and REPORT_FORMAT left-align mandate)
- `td` text-align added: `left` (same source)
- No changes to HTML structure, placeholder tokens, or template extensions
