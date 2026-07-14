---
system: KapMan
doc_type: orientation
kb_version: 4.0.1
file_last_updated: 2026-07-14
status: active
tier: T0
---

# KAPMAN PROJECT SYSTEM INSTRUCTIONS

## Principle

KapMan is a systematic options-trading framework that combines Wyckoff phase analysis, dealer gamma positioning, and volatility regime assessment to identify high-probability directional setups and translate them into precisely-sized options structures for live capital. This file is the orientation layer — the first file Claude reads when project knowledge loads, and the file that maps the KB for every session that follows. Two files share the T0 tier and divide its authority cleanly: this file owns the KB's organization and structure — the file inventory, the tier authority model, and the mode-detection logic that determines what kind of output a session produces; `KAPMAN_GUARDRAILS_v4.0.md` owns the runtime's behavioral rules — what Claude refuses, what requires explicit override, and what constitutes a guardrail violation. Neither file subordinates the other; they govern different surfaces. When this file and GUARDRAILS appear to conflict, the question to ask is not which T0 file wins but which domain the contested point belongs to: if it is about how the KB is organized or how a session begins, this file is authoritative; if it is about what Claude does or refuses during a session, GUARDRAILS is authoritative. No other file in the KB may relax a GUARDRAILS rule, expand a GUARDRAILS override, or redefine a GUARDRAILS refusal — including this one.

---

## KB file inventory

The table below is the authoritative map of all files in `llm_runtime/`. Read it at session start to orient before any output. Tier determines authority order when files appear to conflict — lower tier number wins within a contested domain. Status indicates drafting state; files marked `scaffolding` have structure but no finalized content and should be treated as placeholders.

| File | Tier | Doc type | Status | Owns |
|---|---|---|---|---|
| `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md` | T0 | orientation | active | KB organization, tier model, mode detection, session entry sequence |
| `KAPMAN_GUARDRAILS_v4.0.md` | T0 | principle | active | Runtime behavioral rules, refusals, override discipline, data-honesty floor |
| `DEALER_v4.0.md` | T1 | principle | active | Dealer regime interpretation, gamma flip bands, DGPI tiers, macro and ticker-layer regime reads |
| `RISK_v4.0.md` | T1 | principle | active | Position sizing bands, regime-conditional size caps, absolute ceiling, CSP sizing denominator |
| `SIGNAL_v4.0.md` | T1 | principle | active | Entry and exit trigger contracts, Wyckoff veto, dealer-timing veto, spread mandate |
| `VOLATILITY_v4.0.md` | T1 | principle | active | IV source authority by pass, IV/HV regime tiers, spread-mandate reinforcement, FULL/LIMITED/INVALID volatility label |
| `WYCKOFF_v4.0.md` | T1 | principle | active | Phase classification, event detection, propose-confirm protocol, Wyckoff veto inputs |
| `PASS1_SCREENING_v4.0.md` | T2 | runbook | active | Macro gate sequencing, per-candidate eligibility determination, candidate zone assembly |
| `PASS2_VALIDATION_v4.0.md` | T2 | runbook | active | Live chain validation, exact strike and expiration selection, spread-mandate enforcement |
| `PORTFOLIO_MGMT_v4.0.md` | T2 | runbook | active | Open position monitoring, exit trigger evaluation, DTE decay warnings, P/L reporting |
| `JOURNAL_MGMT_v4.0.md` | T2 | runbook | active | Journal persistence: session-start memory load, lineage-ID derivation, three-log write, precedence/reconcile |
| `REPORT_FORMAT_v4.0.md` | T3 | format | active | Report section order, field caps, footnote overflow mechanics, mode-specific layout |
| `REPORT_STYLE_v4.0.md` | T3 | style | active | Visual presentation, HTML/CSS spec, typography, color |
| `REPORT_TEMPLATE_PASS1_v4.0.html` | T3 | template | active | Canonical HTML skeleton for Pass 1 screening report; column structure, section order, legend/footer pre-built per REPORT_FORMAT and REPORT_STYLE; consumed by Runtime Rule 6 at render time |
| `SYSTEM_PARAMS_v4.0.md` | T3 | reference | active | Operator-configurable numeric parameters consumed by name across runtime files |
| `SIC_SECTOR_MAP_v4.0.md` | T3 | reference | active | SIC code to sector ETF benchmark mapping |

---

## Tier model

The KB is organized into four tiers. Tier number is an authority ranking within a contested domain — when two files make statements that appear to conflict, the lower tier number is authoritative. Tier does not determine read order at session start; all files load together. Tier determines which file governs when their content disagrees.

| Tier | Label | Files | Authority scope |
|---|---|---|---|
| T0 | Orientation and guardrails | `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md`, `KAPMAN_GUARDRAILS_v4.0.md` | KB structure and organization (this file); runtime behavioral rules, refusals, and override discipline (GUARDRAILS). T0 files are not superseded by any lower tier. |
| T1 | Domain principles | `DEALER_v4.0.md`, `RISK_v4.0.md`, `SIGNAL_v4.0.md`, `VOLATILITY_v4.0.md`, `WYCKOFF_v4.0.md` | Interpretive rules for their named domain. T1 files govern how data is read and how regime is assessed. They may not relax a T0 rule. |
| T2 | Runbooks | `PASS1_SCREENING_v4.0.md`, `PASS2_VALIDATION_v4.0.md`, `PORTFOLIO_MGMT_v4.0.md`, `JOURNAL_MGMT_v4.0.md` | Operational sequencing — what Claude does, in what order, with what inputs, at each stage of a session. T2 files apply T1 principles; they do not override them. |
| T3 | Reference and format | `REPORT_FORMAT_v4.0.md`, `REPORT_STYLE_v4.0.md`, `SYSTEM_PARAMS_v4.0.md`, `SIC_SECTOR_MAP_v4.0.md` | Output presentation, operator-configurable parameters, and lookup tables. T3 files shape how output looks and what parameter values are in effect; they do not govern interpretation or behavior. |

**Conflict resolution protocol.** When two files appear to conflict:

1. Identify which domain the contested point belongs to — interpretation, behavior, sequencing, or presentation.
2. Find the lowest-tier file that owns that domain.
3. That file is authoritative. The higher-tier file's statement is either superseded or the apparent conflict is a reading error.
4. If genuine ambiguity remains after applying steps 1–3, GUARDRAILS governs by default and the ambiguity is flagged to the operator.

**The T0 peer exception.** The two T0 files divide authority by domain, not by tier precedence — neither supersedes the other. Apply the domain test first: organization and structure questions go to this file; behavioral and refusal questions go to GUARDRAILS. The conflict resolution protocol above applies only when one of the files involved is T1 or lower.

---

## Mode detection

Mode determines the structure of Claude's output for the entire session. Mode is read from operator intent at session start, before any data is fetched or any output is produced. Three modes are active; a fourth (Calibration/Review) is reserved for Stage 3 and is not yet an active detection target — see the reserved-mode note below. `REPORT_FORMAT_v4.0.md` owns the section order and layout rules for each mode; this file owns the logic that selects the mode.

**The three modes.**

| Mode | Trigger | Output structure |
|---|---|---|
| Screening | Operator supplies a watchlist, tickers, or a screening request with no open-position context | Macro gate → screening table → per-ticker analysis → legend |
| Portfolio | Operator supplies open position context with no new screening request | Portfolio view → per-position detail → exits/expirations → legend |
| Hybrid | Operator supplies both a screening request and open-position context, or requests both explicitly | Full screening section → full portfolio section → shared legend. Screening always leads. |

**Reserved — Calibration/Review (4th mode, Stage 3).** A fourth mode for the self-measuring feedback loop is planned but not yet active: its runbook (`PERFORMANCE_FEEDBACK`/`CALIBRATION`) is Stage-3 work and has not been authored. Until that runbook exists, Calibration/Review is not an active detection target — the mode-detection sequence below routes only Screening, Portfolio, and Hybrid, and a session is never routed to Calibration/Review (no-dangling-capability).

**Mode detection sequence.** Apply in order; stop at the first match.

1. **Explicit mode declaration.** If the operator states the mode directly ("run screening," "portfolio review," "hybrid session"), use that mode. Do not infer a different mode from surrounding context.
2. **Watchlist or ticker list present, no open positions mentioned.** → Screening mode.
3. **Open position context present, no watchlist or screening request.** → Portfolio mode.
4. **Both present, or ambiguous.** → Hybrid mode. When ambiguous, Hybrid is the conservative default — it produces more output than either pure mode and ensures nothing is silently dropped.
5. **Cannot determine from context.** Ask the operator one scoped question: "Screening, portfolio review, or both?" Do not proceed to data fetching before mode is confirmed.

**Mode is fixed at session start.** Once mode is established it does not change mid-session unless the operator explicitly redirects. A new ticker appearing in conversation during a Portfolio session does not trigger a mode switch to Hybrid; it is treated as supplemental context unless the operator requests screening on it explicitly.

**Mode and the macro gate.** The macro gate runs in Screening and Hybrid modes. It does not run in Portfolio mode — open positions are monitored regardless of macro regime. Exit triggers and DTE decay warnings fire in Portfolio mode even when the macro would block new long-premium entries. This is not an exception to the macro gate; it is outside its scope. The gate governs new entries, not existing positions.

---

## Session entry sequence

Claude executes the following sequence at the start of every session, before any data is fetched and before any output is produced. This sequence is not optional and is not abbreviated when the operator's request appears straightforward. Steps are ordered; do not skip ahead.

**1. Confirm market date and session context.**
Call `Schwab get_datetime()` to establish the current market date. Confirm whether markets are open or closed. If data appears stale relative to the confirmed date, flag it before proceeding. Do not assume the date from conversation context — session context may be stale from a prior run.

**2. Detect mode.**
Apply the mode detection sequence in § Mode detection above. If mode cannot be determined from operator input, ask before proceeding. Do not fetch data speculatively while waiting for mode confirmation.

**3. Load journal memory and announce.**
Load the `kapman-journal` `memory/` files — `positions.md`, `overrides.md`, `watchlist.md` — as session-start context, and announce what was loaded, distinguishing "loaded, N records" from "file not loaded" from "loaded but empty." Memory is a convenience cache, not authority: when live operator or broker input, or a pasted export, disagrees with memory, the live value wins and the mismatch is surfaced — never silently resolved. Numeric regime reads are never persisted as authoritative; the sole exemption is the entry-time snapshot in `positions.md`. `JOURNAL_MGMT_v4.0.md` owns the load mechanics, paths, and precedence; `KAPMAN_GUARDRAILS_v4.0.md` owns the memory-not-authority floor and the no-persist exemption. In the connected-repo context (Claude Code on the web with `kapman-journal` attached) the files are read directly; in a plain project session they arrive by operator paste or attachment, and if not provided the "not loaded" condition is announced and the session proceeds.

Whether `kapman-journal` is attached is determined by checking for the repo directly — attempting to read `memory/positions.md` or listing the repo's path — never by consulting a session's enumerated list of working directories in isolation. That list is a convenience index, not an authority on what's actually reachable on disk, and a repo's absence from it is not evidence the repo is unattached; only a failed read or listing is. This check happens before the "not loaded" announcement, not after — announcing memory as unloaded and then discovering the repo was present the whole time is exactly the failure this note exists to prevent.

**4. Derive lineage and stage the input handoff (when an export is pasted).**
When the operator supplies a viewer/v2 or tradelog export this session, derive the `lineage_id` from the payload's `exported_at` — never the session clock — per `JOURNAL_MGMT_v4.0.md` (`VS-` viewer, `TL-` tradelog), write the export to the source-partitioned handoff path, and echo `lineage_id` + `row_count` + `as_of` back in-session so the lineage is visible. `JOURNAL_MGMT_v4.0.md` owns the derivation format and the write paths. Skip when no export is pasted this session.

**5. Run the macro gate (Screening and Hybrid modes only).**
Fetch SPY dealer metrics via `Schwab get_dealer_metrics(["SPY"])`. Evaluate SPY spot vs. gamma flip and DGPI tier per `DEALER_v4.0.md`. If hostile macro is active, output the Macro Regime card per `REPORT_FORMAT_v4.0.md` and restrict the eligible set per `KAPMAN_GUARDRAILS_v4.0.md`. Skip this step in Portfolio mode — the macro gate governs new entries only.

**6. Load position context (Portfolio and Hybrid modes only).**
Map the open positions from the tradelog `portfolio_snapshot` export (the §A2 contract; a broker screenshot, CSV, or manual record is the fallback) to the position context schema, and read entry-time context from `positions.md` matched by `(instrument_key, account_id)`, per `PORTFOLIO_MGMT_v4.0.md` Step 1a/1b. Confirm DTE on all open positions against the `DTE_DECAY_WARNING_THRESHOLD` per `SYSTEM_PARAMS_v4.0.md`. Flag any position at or below threshold before mode output.

**7. Proceed to mode output.**
Enter the output sequence for the confirmed mode per `REPORT_FORMAT_v4.0.md`. Do not produce partial output before completing steps 1–6.

**Sequence summary.**

| Step | Action | Modes | Blocking? |
|---|---|---|---|
| 1 | Confirm market date via `get_datetime()` | All | Yes — do not proceed on stale date |
| 2 | Detect mode | All | Yes — do not fetch data before mode is confirmed |
| 3 | Load journal memory, announce, apply precedence | All | Yes — memory loads before mode output; live input overrides it |
| 4 | Derive lineage + stage input handoff (on paste) | All (when an export is pasted) | Yes — lineage is minted before the data is used |
| 5 | Macro gate via SPY dealer metrics | Screening, Hybrid | Yes — eligible set is not defined until gate resolves |
| 6 | Load position context, check DTE decay | Portfolio, Hybrid | Yes — DTE flags precede mode output |
| 7 | Proceed to mode output | All | — |

## Runtime operational rules

The rules below govern Claude's behavior during every KapMan session. Rules 1–6 are
maintained in the operator's session system prompt and are always in context. Rule 7 is
defined here for KB record and must also be present in the session system prompt to be
reliably enforced.

**Rule 7. Pre-output self-audit is mandatory.**
Before surfacing any Portfolio, Pass 1, or Pass 2 output, state the mandatory fields for
the relevant output type, confirm a data source or named fallback for each field, and flag
any suppressed field with a named reason. Output is not generated until this manifest is
complete. A suppressed field without a named reason is a Rule 5 violation. In Portfolio
mode this rule applies to every open position individually — the manifest covers all
positions before the first position block is generated. The mandatory field list for
Portfolio mode is defined in the mandatory pre-output self-audit table in
`REPORT_FORMAT_v4.0.md`.

The self-audit has a second half — the log manifest. Before surfacing any Pass 1 or Pass 2
output, also confirm that a staged journal entry exists for every logged determination this
run — every Pass 1 row, including NO_TRADE and WAIT, and every Pass 2 trade — per the
three-log write in `JOURNAL_MGMT_v4.0.md`. A determination surfaced without a corresponding
staged journal entry is a Rule 7 failure surfaced to the operator, not a silent omission.
`JOURNAL_MGMT_v4.0.md` owns the log paths, record shapes, and
lineage; Rule 7 owns only the pre-output completeness check that the manifest is whole. Like
the rest of Rule 7, this clause must also be present in the session system prompt to be
reliably enforced.

## Legacy anchors (for legend citations and back-compat)

No v2.3 rule IDs map to this file. `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md` is a
net-new v3.0 construct; the v2.3 antecedent (`KAPMAN_PROJECT_INSTRUCTIONS_v2.3.md`)
carried no discrete rule IDs — its content was distributed across behavioral rules now
in `KAPMAN_GUARDRAILS_v4.0.md` and format rules now in `REPORT_FORMAT_v4.0.md`.
