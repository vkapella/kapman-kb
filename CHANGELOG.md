# KapMan KB Changelog

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
