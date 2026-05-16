---
system: KapMan
doc_type: format
kb_version: 3.0.6
file_last_updated: 2026-05-16
status: active
tier: T3
---

# REPORT FORMAT

## Principle

A KapMan report is a decision surface, not a compliance document. It is designed to be scanned in under five minutes by an operator under Monday-morning time pressure, and every structural decision in this file follows from that requirement. REPORT_FORMAT owns the information architecture of every report Claude produces: which sections appear, in what order, in what modes, and at what length. It does not own the content those sections carry — content is owned by the T1 principles and T2 runbooks — and it does not own the visual presentation of the surface — that belongs to REPORT_STYLE. REPORT_FORMAT occupies the layer between them: it specifies that a rationale cell exists and that it holds at most 20 words, but not what those words should say or what color the cell is. The governing tension REPORT_FORMAT must hold structurally is completeness against readability: a report that omits a required field has failed the operator's decision needs; a report that exceeds its field caps has failed the operator's time constraints. Footnote overflow is the mechanism that resolves this tension — excess content is preserved but displaced, so the scan surface stays clean and the full record remains accessible. Every field cap in this file is a hard limit, not a guideline, because a cap that yields under pressure is not a cap.

---

## Operational heuristics

**The report has three modes, each with a fixed section order. Mode determines structure — structure does not adapt to content.**

- Screening mode: Macro Regime card (when active) → Report header → Screening table → Alternatives Summary (when NO_TRADE or WAIT candidates present) → Per-ticker detailed analysis → Legend/footer.
- Portfolio mode: Report header → Portfolio view table → Per-position detail → Exited positions summary (when present) → Expired positions requiring acknowledgment (when present) → Legend/footer.
- Hybrid mode: Full Screening section (titled) → Full Portfolio section (titled) → Shared legend/footer. Screening comes first, always. The two sections are not interleaved.
- A section that is absent because mode doesn't call for it leaves no placeholder, no blank space, and no explanatory note. Absent means absent.

The subtitle line for Screening mode carries, at minimum: session date, mode label, watchlist name, and tickers-evaluated count. Format: "Session: YYYY-MM-DD | Mode: Screening | Watchlist: [name] | Tickers evaluated: N". Ticker-count breakdown (eligible, blocked, caution-gated, NO_TRADE counts) may also appear in the subtitle when space permits; it must not appear in the legend/footer session metadata element.

**The Macro Regime card appears above the screening table when hostile macro is active — and only then.**

- When hostile macro is active, the card appears as the first element after the report header, before the screening table. It is not a row in the table; it is a distinct block.
- When hostile macro is not active, the card is absent — no placeholder, no "macro clear" line in its place. The absence is the signal.
- The card contains, in order: SPY spot, SPY flip level, SPY DGPI tier, regime label, eligible-set redirect statement. Five elements, no more. GUARDRAILS owns when the card fires; REPORT_FORMAT owns what it says.
- The eligible-set redirect statement names the structures that remain eligible (e.g., "Eligible: long puts, CSPs, LEAPs, equity hedges"). It does not editorialize.

**Field caps are hard limits. Content that exceeds a cap goes to footnotes — it does not compress, truncate, or get omitted.**

- Every field in every table has a word or line cap defined in the Appendix. The cap is the maximum allowed in the rendered cell.
- When content exceeds the cap, the overflow moves to a numbered footnote in the legend/footer section. The cell carries a superscript reference (¹, ², ³...). The footnote is complete — it contains everything that didn't fit plus enough context to stand alone.
- Footnotes are numbered sequentially across the entire report. A superscript in the screening table and a superscript in the portfolio table share the same numbering sequence.
- The cap discipline applies to rationale cells above all others. Rationale overflow is the most common case and the most important to handle correctly — a rationale cell that runs long breaks the scan rhythm of the whole table.

**The source bar appears immediately below the subtitle in every report section that surfaces MCP-sourced data.**

- The source bar is a single line (or at most two lines) identifying: data sources used, their freshness timestamps, and any chain quality or dealer-status degradation flags active for this report.
- The source bar is not part of the legend/footer. It sits between the subtitle and the first table of its section.
- In Hybrid mode, each section (Screening, Portfolio) carries its own source bar. The shared legend/footer does not repeat source information already stated in the bars.
- Degradation flags in the source bar use the vocabulary from GUARDRAILS: "Stale dealer data [timestamp]", "Limited chain — [ticker]", "Dealer-status INVALID — [ticker]". The source bar is where these flags surface structurally; rationale cells reference the condition but do not re-state the full flag.

**Rule IDs appear once per report, in the legend/footer "Rules applied" line — nowhere else.**

- Body text, rationale cells, and the Macro Regime card use descriptive language only. "Spread mandatory — elevated IV/HV" not "SIGNAL_008 fires."
- The "Rules applied" line in the legend/footer lists rule IDs as a comma-separated sequence. It is one line, not a table, not an annotated list.
- Legacy rule IDs cited by the operator in conversation (e.g., "WYCKOFF_PHASE_002") are valid in legend references and remain honored. No new domain_NNN IDs are introduced in report output.

**Override acknowledgment is mandatory and has a fixed placement.**

- When an override is active, the report states it in the subtitle line: *"Override active: [structure] shown despite [condition] per operator instruction."*
- If the subtitle is occupied, the acknowledgment moves to a footnote: *"¹ [Structure] entries shown under explicit operator override; [condition] remains active per [DGPI or regime read]."*
- The acknowledgment is never omitted. A report that does not surface an active override is a guardrail violation per GUARDRAILS.

**Pass label discipline: zone outputs and validated outputs render differently.**

- Strike fields from Pass 1 (unvalidated) render as zones: "Candidate zone $X–$Y" or "Candidate zone near $X." They do not carry specific strike values.
- Strike fields from Pass 2 (validated) render as exact values: "$247.50" or "247.50/252.50 spread."
- Expiration fields from Pass 1 render as bands: "Candidate expiration [DTE band per SYSTEM_PARAMS]." They do not carry specific dates.
- Expiration fields from Pass 2 render as exact dates: "2026-06-20."
- This distinction is visible in the table. A row that mixes zone and exact values signals that Pass 2 is incomplete for that candidate — which is valid for WAIT candidates and must be rendered faithfully.

**NO_TRADE and WAIT rows are populated differently from Eligible rows — but they are never empty.**

- A NO_TRADE row carries: Ticker, Type = NONE, Action = NO_TRADE, reason in the Rationale cell, all remaining fields labeled "—". The row is present in the table; the candidate is not silently dropped.
- A WAIT row carries: Ticker, Type = NONE, Action = WAIT, deferral reason in the Rationale cell, all remaining fields labeled "—". The candidate is not dropped; it is deferred.
- The distinction between NO_TRADE and WAIT is the Rationale cell. NO_TRADE names the refusal reason; WAIT names the missing input that, when resolved, would allow the candidate to re-enter screening.

**Confidence renders as a labeled band — numeric value in parentheses when available.**

- Primary recommendations: High (≥80), Med (60–79), Low (<60). The numeric value appears in parentheses when SIGNAL produces one: "High (84)."
- Alternatives render in descending confidence order, strictly below the primary. Each alternative carries its own labeled band.
- When confidence is unavailable (degraded inputs), the field renders as "Low — degraded inputs" rather than blank.

**The legend/footer has a fixed internal order.**

- "Rules applied:" line (rule IDs, one line, comma-separated)
- Data sources (MCP tool surfaces used, with timestamps)
- Chain quality badge key (Full / Limited / Invalid definitions, one line each)
- Footnotes (numbered sequentially, each on its own line)
- Session metadata (date, pass sequence completed, mode)

The legend/footer is the only section that may expand without a hard cap — footnote volume is determined by overflow, not by the operator. The legend/footer never appears mid-report; it is always the final element.

**Run timing and token estimate are recorded at two fixed points — not reconstructed at render time.**

The run start timestamp is the moment the first MCP call of the run fires: the SPY macro gate fetch for Pass 1, or the first live chain fetch for Pass 2 when Pass 2 begins as a standalone run. The render timestamp is the moment Claude begins assembling the final HTML output. Both are noted inline during the session as they occur and carried into the session metadata block — they are never back-calculated or approximated. If no reliable clock signal is present in context, the timestamp renders as `--:-- ET (unavailable)`; timestamps are never fabricated. The token estimate uses the runtime formula `(N_tickers × 4,000) + 60,000`, where N_tickers is the count of candidates that received a Pass 1 determination (Eligible, NO_TRADE, or WAIT) in the current run. Round to the nearest 1,000 and label `~NNNk tokens est.` This is a planning estimate, not a metered API count. When Pass 2 has also run, append `+ P2 chain validation` to the label without adjusting the formula. The `session-meta-timing` CSS class is reserved for the session metadata block only. It must not be used for ticker-count summary lines or any other content. Ticker-count summary data (tickers evaluated, eligible count, blocked count) belongs in the subtitle line of the report header, not in the legend/footer session metadata element.

**Default output format is markdown. HTML is produced only on explicit operator request.**

- The default output for all Pass 1 triage reports, Pass 2 validation reports, and portfolio reports is markdown (pipe-delimited tables with GitHub Flavored Markdown syntax).
- HTML output is produced only when the operator explicitly requests it: "give me the HTML report", "render as HTML", or equivalent.
- When markdown is the output mode, REPORT_TEMPLATE_PASS1_v3.0.html is not used. The section order, field caps, footnote convention, and all content rules in this file still apply — only the rendering surface changes.
- Markdown column alignment follows REPORT_STYLE column-alignment rules: left-align for text/rationale columns, left-align for all headers (`:---` separator syntax).
- When switching from markdown to HTML mid-session on operator request, Claude produces the full HTML block in one pass from already-computed intermediate data. Claude does not re-run MCP calls to produce the HTML version of a report already computed in markdown.

**HTML rendering discipline — generate in two stages, never inline.**

- Stage 1 (compute): Run all MCP calls, collect all structured data, resolve all field values, apply all KB rules. Save intermediate results to a structured scratch representation before emitting any output. Do not begin HTML emission until all data is resolved.
- Stage 2 (render): Emit the complete HTML block in one pass from the resolved data. No MCP calls, no rule evaluation, no field resolution during Stage 2.
- Violating the two-stage discipline — emitting partial HTML while still fetching data — is the primary cause of slow rendering. The operator sees an incomplete table growing incrementally, which is slower to scan than a complete table appearing at once.
- The HTML block must use the class-based stylesheet from REPORT_STYLE. No inline `style=` attributes on any `<td>` or `<tr>` element. Inline styles double the token output of the table and are the secondary cause of slow rendering.

---

## Workflow integration

**Position in the document hierarchy.**

REPORT_FORMAT is tier T3 — the rendering specification layer. It sits below the T0 guardrails, T1 principles, and T2 runbooks in authority, but it is the last file consulted before output reaches the operator. Every content decision has already been made by the time REPORT_FORMAT applies; REPORT_FORMAT's job is to place that content correctly and enforce the structural constraints that make it scannable.

When REPORT_FORMAT and a T1 or T2 file appear to conflict on a structural question, REPORT_FORMAT governs — the runbooks do not own rendering. When REPORT_FORMAT and GUARDRAILS appear to conflict, GUARDRAILS wins — field cap enforcement and override acknowledgment placement are REPORT_FORMAT's mechanics, but the mandate that they be enforced is GUARDRAILS'.

**What REPORT_FORMAT receives from each upstream file.**

| Source file | What REPORT_FORMAT consumes | How REPORT_FORMAT uses it |
|---|---|---|
| `KAPMAN_GUARDRAILS_v3.0.md` (T0) | Hard-cap mandate; rule-ID-legend-only rule; override acknowledgment requirement; data-quality vocabulary; mode discipline | REPORT_FORMAT enforces caps numerically; places rule IDs in legend/footer only; places override acknowledgment in subtitle or footnote per heuristic; uses GUARDRAILS vocabulary in source bar flags |
| `SIGNAL_v3.0.md` (T1) | Label vocabulary for trigger states; four-field exit-trigger output format; NO_TRADE/WAIT consistency rule; confidence ordering rule; anti-hallucination floor substitution labels | REPORT_FORMAT renders trigger-state labels verbatim; renders the four exit-trigger fields as a matched pair per position; enforces NO_TRADE/WAIT row structure; renders alternatives in descending confidence order; renders zone substitutions per pass label discipline |
| `DEALER_v3.0.md` (T1) | DGPI tier names; flip-zone labels; dealer-status labels (FULL/LIMITED/INVALID); hostile-macro flag | REPORT_FORMAT renders DGPI tier in the screening table and Macro Regime card; renders flip-zone in rationale where relevant; renders dealer-status in the source bar and chain quality badge |
| `VOLATILITY_v3.0.md` (T1) | IV/HV band labels; IV rank tier labels; volatility-status labels; stale-data flag | REPORT_FORMAT renders volatility regime in the screening table; renders "Stretched IV" annotation for extreme tier; renders stale-data flag in source bar with timestamp |
| `WYCKOFF_v3.0.md` (T1) | Phase labels; event labels | REPORT_FORMAT renders Wyckoff phase in the screening table and portfolio detail; renders confirmed events in rationale |
| `PASS1_SCREENING_v3.0.md` (T2) | Eligible/NO_TRADE/WAIT determinations; candidate zones; alternatives with confidence; Pass 1 data-quality labels; macro gate result; override acknowledgments | REPORT_FORMAT renders the screening table and per-ticker detail from Pass 1 output; applies zone rendering to all Pass 1 strike and expiration fields |
| `PASS2_VALIDATION_v3.0.md` (T2) | Validated/Flagged/Rejected states; exact strikes and expirations; chain quality label; dealer-status label; entry price range; sizing band | REPORT_FORMAT renders exact values for Pass 2 validated candidates; renders Flagged and Rejected states with named reasons; renders chain quality badge in source bar |
| `PORTFOLIO_MGMT_v3.0.md` (T2) | Position context schema; lifecycle state labels (Open/Advisory/Exited/Expired); advisory flag format; DTE decay warning format; Regime exit advisory decay reasons | REPORT_FORMAT renders the portfolio view table and per-position detail from position context; renders advisory flag with named decay reason; renders DTE decay warning when active; renders Exited and Expired summary sections when present |
| `SYSTEM_PARAMS_v3.0.md` | DTE band values (SWING_DTE_BAND, CSP_DTE_BAND, DTE_DECAY_WARNING_THRESHOLD) | REPORT_FORMAT uses DTE band values as the canonical expiration-band labels in Pass 1 zone rendering; uses DTE_DECAY_WARNING_THRESHOLD to determine when the decay warning renders in the portfolio detail |

The HTML render artifact for Pass 1 reports is `REPORT_TEMPLATE_PASS1_v3.0.html` — the executable expression of the screening table column spec in this file's Appendix. The template fills at render time; this file remains the authoritative column-spec source. When the spec changes, the template is updated to match; the template never overrides the spec.

**What REPORT_FORMAT does not own.**

| Concern | Owner |
|---|---|
| Content of any field | T1 and T2 files |
| Behavioral rules that determine what content is produced | SIGNAL, GUARDRAILS, runbooks |
| Visual presentation (typography, color, HTML/CSS) | `REPORT_STYLE_v3.0.md` |
| Label vocabulary (DGPI tier names, dealer-status labels, chain quality labels) | Respective T1 files |
| Override discipline | `KAPMAN_GUARDRAILS_v3.0.md` |
| Regime exit advisory firing condition | `SIGNAL_v3.0.md` |
| DTE band numeric values | `SYSTEM_PARAMS_v3.0.md` |
| MCP tool-surface contracts | `engineering_only/` files |

**Where REPORT_FORMAT constraints flow downstream.**

| Constraint | Consumed by | How |
|---|---|---|
| Field cap numeric values | `REPORT_STYLE_v3.0.md` | REPORT_STYLE implements the caps visually (column width CSS); REPORT_FORMAT owns the word/line counts that drive those widths |
| Footnote numbering convention | `REPORT_STYLE_v3.0.md` | REPORT_STYLE owns the superscript CSS; REPORT_FORMAT owns the sequential numbering rule |
| Section presence and ordering rules | Every T2 runbook | Runbooks assemble output knowing where it will be placed; PASS1, PASS2, and PORTFOLIO_MGMT produce content in the sequence REPORT_FORMAT will render it |
| Source bar placement rule | `REPORT_STYLE_v3.0.md` | REPORT_STYLE owns source bar visual styling; REPORT_FORMAT owns that it appears below the subtitle and above the first table |
| Legend/footer internal order | `REPORT_STYLE_v3.0.md` | REPORT_STYLE owns legend/footer visual styling; REPORT_FORMAT owns the element sequence within it |

**Entry point for every report output.**

Before rendering any section, three structural checks apply:

1. Mode is confirmed — Screening, Portfolio, or Hybrid. The section structure for the confirmed mode is the template; no sections are added or removed based on content volume or operator preference within a mode.
2. Pass sequence is known — which passes completed in this session (Pass 1 only, Pass 1 + Pass 2, Portfolio only, or both for Hybrid). Pass label discipline in the strike and expiration fields depends on knowing which pass produced each candidate's data.
3. Override status is established — if any override is active, subtitle placement of the acknowledgment is confirmed before the first table renders. Override acknowledgment is never deferred to the end of the report.

---

## Legacy anchors (for legend citations and back-compat)

**Origin of REPORT_FORMAT content in v2.3.**

REPORT_FORMAT_v3.0.md has no direct v2.3 antecedent file. Its content was distributed across two v2.3 sources that mixed format and behavioral content:

- `KAPMAN_PROJECT_INSTRUCTIONS_v2.3.md` — contained section ordering, field sequence, the Macro Regime card format, the trade-sheet table structure, and the communication style rules that are now cleanly separated into GUARDRAILS (behavioral) and REPORT_FORMAT (structural).
- `KAPMAN_REPORT_STYLE_GLOSSARY_v2.3.md` — contained column width caps (rationale-col 180px, action-col 165px, scale-col 70px, stop-col 50px, note-col 150px), the footnote section structure, the source bar placement and content, and the legend/footer element list. These are FORMAT-scoped; the CSS implementation of these constraints migrates to REPORT_STYLE_v3.0.md.

**PIPELINE_011** → § Operational heuristics, "Pass label discipline" heuristic. The v2.3 compaction guard rule (always re-fetch Schwab dealer metrics at Pass 2; never reuse Pass 1 values even if visible in context) is absorbed into PASS2_VALIDATION_v3.0.md as the authoritative location. REPORT_FORMAT's pass label discipline (zone rendering for Pass 1 outputs, exact rendering for Pass 2 outputs) is the rendering expression of the same contract. Body-text references in legacy report legends citing PIPELINE_011 remain valid.

**VALIDATION_001** → § Operational heuristics, "Pass label discipline" heuristic. The anti-hallucination floor — zone substitutions in place of unvalidated strikes and expirations — is the rendering manifestation of VALIDATION_001. GUARDRAILS owns the floor as standing behavior; REPORT_FORMAT owns how zone substitutions appear in the rendered output. Body-text references in legacy report legends citing VALIDATION_001 remain valid.

**RISK_005** → § Operational heuristics, "Confidence renders as a labeled band" heuristic (indirectly). The v2.3 position size cap table (3%/2%/1%/0.5–1%/0%) is owned by RISK_v3.0.md. REPORT_FORMAT owns that the sizing band notation appears in the candidate row and per-position detail, but does not own the band values themselves. Body-text references in legacy report legends citing RISK_005 remain valid and are honored by RISK_v3.0.md.

**Macro Regime card** → § Operational heuristics, "The Macro Regime card appears above the screening table when hostile macro is active." The v2.3 card format appeared inline in `KAPMAN_PROJECT_INSTRUCTIONS_v2.3.md` Communication Style: `"SPY $X | Below flip ($Y) | DGPI [Z] | Regime: MARKDOWN | Long-call entries blocked. CSP / hedge / LEAPs eligible only."` The v3.0 card expands this to five named elements with explicit ordering (SPY spot, flip level, DGPI tier, regime label, eligible-set redirect) and clarifies that the card is a distinct block, not a table row. The pipe-delimited inline format from v2.3 is a valid rendering of the five elements and remains compatible with v3.0 structure.

**Trade-sheet table** → § Appendix, Screening table field sequence. The v2.3 trade-sheet column sequence (Ticker / Type / Action / Wyckoff Phase / DGPI / Strike / Exp / Entry / Exit / Scale / Confidence / Rationale) is preserved in v3.0 with additions for chain quality label and dealer-status label, which were implicit in v2.3 but not surfaced as discrete table columns.

---

## Appendix — formulas and reference tables

**Screening table field sequence and caps.**

One row per candidate. Fields render left to right in the order below. Fields marked "Pass 2 only" are blank (rendered as "—") for candidates that have not completed Pass 2.

| # | Field | Cap | Overflow | Notes |
|---|---|---|---|---|
| 1 | Ticker | 6 chars | None — tickers do not overflow | Symbol only; no company name |
| 2 | Type | 20 chars | None | Structure label: Long Call, Long Put, CSP, Vertical Spread, NONE |
| 3 | Action | 12 chars | None | ACT TODAY, MONITOR, NO_TRADE, WAIT — vocabulary fixed |
| 4 | Wyckoff Phase | 20 chars | None | Always render as [Phase] ([status]). Rendering contract by confirmation status — pipeline-accepted (clean): phase label only, e.g. "Markup" or "Accum post-Spring — SOS ✓"; pipeline-accepted (no primary event): phase label only, e.g. "Markup"; confirmed (estimation path): "Phase (confirmed)", e.g. "Markup (confirmed)"; declared (operator-stated): "Phase (declared)", e.g. "Distrib (declared)"; pipeline-flagged: "Phase? (flagged)", e.g. "Distrib? (flagged)"; unconfirmed (declined/skipped): "Phase? (unconfirm'd)", e.g. "Accum? (unconfirm'd)"; UNKNOWN (no read): "UNKNOWN". Phase abbreviations within 20-char cap: Accum pre-Spring, Accum post-Spring, Markup, Distrib, Markdown. The ? suffix on flagged and unconfirmed statuses signals to the operator that the phase shown is the pipeline's read, not a confirmed one. pipeline-accepted carries full trigger authority and needs no qualifier. |
| 5 | DGPI | 8 chars | None | Tier label (Strongly Supportive → Hostile) + raw score in parens: "Mod. Supportive (+34)" |
| 6 | Strike | 25 chars | Footnote | Pass 1: "Candidate zone $X–$Y"; Pass 2: exact value(s) |
| 7 | Exp | 15 chars | None | Pass 1: DTE band label per SYSTEM_PARAMS; Pass 2: exact date YYYY-MM-DD |
| 8 | Entry | 20 chars | Footnote | Pass 2 only; entry price range: "$3.40–$3.80" |
| 9 | Exit | 20 chars | Footnote | Pass 2 only; profit target alert level |
| 10 | Scale | 30 chars | Footnote | Two scale levels max: "50% at +50% / remainder at +100%" |
| 11 | Confidence | 18 chars | None | Labeled band + numeric: "High (84)"; "Low — degraded inputs" when unavailable |
| 12 | Rationale | 20 words | Footnote | Plain language; no rule IDs; descriptive trigger language only |

NO_TRADE rows: fields 1–3 populated; field 12 contains the refusal reason; fields 4–11 render as "—".
WAIT rows: fields 1–3 populated; field 12 contains the deferral reason and missing input; fields 4–11 render as "—".

---

**Portfolio view table field sequence and caps.**

One row per open position. Exited and Expired positions do not appear in the main portfolio view table — they appear in their own summary sections below.

| # | Field | Cap | Overflow | Notes |
|---|---|---|---|---|
| 1 | Ticker | 6 chars | None | Symbol only |
| 2 | Structure | 20 chars | None | Long Call, Long Put, CSP, Vertical Spread |
| 3 | Direction | 8 chars | None | BULLISH, BEARISH |
| 4 | Strike(s) | 20 chars | None | Exact; "247.50" or "247.50/252.50" |
| 5 | Expiration | 12 chars | None | Exact date YYYY-MM-DD |
| 6 | Entry Date | 12 chars | None | YYYY-MM-DD |
| 7 | Entry Price | 10 chars | None | Option premium paid: "$3.60" |
| 8 | Current Price | 10 chars | None | Current option mark: "$5.20" |
| 9 | Current Spot | 10 chars | None | Underlying spot price |
| 10 | DTE | 6 chars | None | Calendar days remaining: "34d" |
| 11 | Stop Alert | 20 chars | Footnote | Underlying alert price; "Pending" if unavailable |
| 12 | Profit Alert | 20 chars | Footnote | Underlying alert price; "Pending" if unavailable |
| 13 | State | 12 chars | None | Open, Advisory, Exited, Expired — vocabulary fixed |
| 14 | Flags | 30 chars | Footnote | Advisory flag text or DTE decay warning; "—" if none active |

---

**Per-ticker detailed analysis subsection sequence.**

One block per screened candidate, appearing below the screening table in the same candidate order. Each subsection is a labeled paragraph, not a nested table.

| # | Subsection | Cap | Notes |
|---|---|---|---|
| 1 | Setup rationale | 40 words | What triggered the candidate; Wyckoff event and phase context |
| 2 | Wyckoff phase read | 25 words | Current phase, confirming events, proposed-confirm status |
| 3 | Dealer regime read | 25 words | DGPI tier, flip-zone, near-flip flag if active, dealer-status label |
| 4 | Volatility regime read | 25 words | IV/HV band, IV rank tier, spread-mandate outcome, volatility-status label |
| 5 | Exit plan | 60 words | Stop alert four fields + Profit target alert four fields as matched pair; "Pending" with reason if unavailable |
| 6 | Alternatives | 30 words | Present only when SIGNAL produced alternatives; descending confidence order; omitted entirely when absent |
| 7 | Caveats | 20 words | Data gaps, near-event risk, degraded inputs, chain quality issues; omitted when nothing to flag |

Overflow from any subsection goes to the footnote sequence. The subsection label remains in the block with a superscript; the full text appears in the numbered footnote.

---

**Alternatives Summary section.**

Present when the screening run contains at least one NO_TRADE or WAIT
candidate. Appears after the screening table and before the per-ticker
detailed analysis section. Omitted entirely when all candidates are
Eligible — no placeholder, no blank space, no heading.

One block per NO_TRADE or WAIT candidate, in the same order as the
candidate appears in the screening table. Each block is a labeled
`.alt-summary` div (see template). No block is rendered for Eligible
candidates — Eligible candidates receive a per-ticker detail block
instead.

Subsection sequence per block:

| # | Subsection | Cap | Notes |
|---|---|---|---|
| 1 | Refusal / deferral reason | 20 words | Restatement from Rationale cell; names the veto or missing input |
| 2 | Wyckoff phase read | 25 words | Current phase, confirming events, proposed-confirm status |
| 3 | Dealer regime read | 25 words | DGPI tier, flip-zone, near-flip flag if active, dealer-status label |
| 4 | Volatility regime read | 25 words | IV/HV band, IV rank tier, spread-mandate outcome, volatility-status label |
| 5 | Alternatives | 30 words | Named structure + direction + candidate zone + confidence, descending confidence order; omit subsection entirely when no alternatives exist |
| 6 | Recheck trigger | 20 words | What specific input change would flip this candidate to Eligible; names the blocking condition |

Aggregate word cap per block: 145 words (sum of subsection caps).
Overflow from any subsection goes to the footnote sequence using the
standard superscript convention. The subsection label remains in the
block with a superscript; the full text appears in the numbered
footnote.

The Alternatives subsection is omitted entirely when SIGNAL produced
no alternatives for the candidate. The Recheck trigger subsection is
always present for both NO_TRADE and WAIT candidates — it is the
forward-looking close of the block.

The section heading reads "ALTERNATIVES SUMMARY" and uses the
`.section-title` class, consistent with adjacent section headings.

---

**Per-position detail subsection sequence.**

One block per open position, appearing below the portfolio view table in the same row order.

| # | Subsection | Cap | Notes |
|---|---|---|---|
| 1 | Current regime summary | 35 words | Dealer regime (DGPI tier, flip-zone), volatility regime (IV/HV band, IV rank tier), Wyckoff phase if confirmed this session |
| 2 | Regime exit advisory | 50 words | Present only when State = Advisory; names each active decay branch; omitted entirely when no advisory active |
| 3 | Exit-trigger proximity | 30 words | Distance of current spot from Stop alert and Profit target alert levels; directional framing |
| 4 | DTE decay warning | 20 words | Present only when DTE ≤ DTE_DECAY_WARNING_THRESHOLD (per SYSTEM_PARAMS, currently 21 days); names DTE and threshold; omitted when DTE is above threshold |
| 5 | Position notes | 25 words | Operator-supplied notes from position context; omitted when position context contains no notes field |

---

**Macro Regime card format.**

The card is a distinct labeled block, not a table row. It contains exactly five elements in the order below. No element is optional when the card is active.

| # | Element | Cap | Format example |
|---|---|---|---|
| 1 | SPY spot | 10 chars | "SPY $542.30" |
| 2 | SPY flip level | 18 chars | "Below flip ($548.00)" |
| 3 | SPY DGPI tier | 28 chars | "DGPI: Hostile (−62)" |
| 4 | Regime label | 20 chars | "Regime: MARKDOWN" |
| 5 | Eligible-set redirect | 50 chars | "Eligible: long puts, CSPs, LEAPs, equity hedges" |

The card does not carry rationale, caveats, or elaboration. It is a state-of-record block. Operators who want the full dealer read consult the source bar and per-ticker dealer regime reads.

---

**Source bar format.**

The source bar appears immediately below the subtitle in every section that surfaces MCP-sourced data. It is one line in standard sessions; it may extend to two lines when multiple degradation flags are active.

| Element | Cap | Format |
|---|---|---|
| Data sources | 60 chars | "Schwab dealer metrics, Polygon options metrics, Schwab chain" |
| Freshness timestamps | 30 chars | "as of HH:MM ET" or "as of YYYY-MM-DD HH:MM ET" for prior-day data |
| Degradation flags | 40 chars per flag | "Stale dealer data [HH:MM ET] — [ticker]"; "Dealer-status INVALID — [ticker]"; "Limited chain — [ticker]" |

Multiple degradation flags are comma-separated on the source bar line. When flags exceed the two-line cap, they move to the first footnote of the session (footnote ¹), and the source bar carries "See footnote ¹ for data quality details."

---

**Legend/footer element sequence and caps.**

| # | Element | Cap | Format |
|---|---|---|---|
| 1 | Rules applied | 1 line | "Rules applied: VALIDATION_001, PIPELINE_011, RISK_005" — comma-separated rule IDs only |
| 2 | Data sources | 2 lines | MCP tool surfaces used; matches source bar but may include additional detail |
| 3 | Chain quality badge key | 3 lines | "Full chain: complete OI and volume data / Limited chain: partial data, floor sizing applied / Invalid chain: dropped from Pass 2" |
| 4 | Footnotes | No cap — determined by overflow volume | Each footnote on its own line; format: "¹ [Full overflow content, self-contained]" |
| 5 | Session metadata | 2 lines | Line 1: `Run: HH:MM ET → HH:MM ET (Xh Ym) \| ~NNNk tokens est.` Line 2: `Date: YYYY-MM-DD \| Mode: [Screening / Portfolio / Hybrid] \| Passes: [Pass 1 / Pass 1 + Pass 2 / Portfolio / Both]` |

The session-meta-timing CSS class applies to both lines of element #5. Element #5 is always the last item in the legend/footer. It is never used as a container for ticker-count summary data; that data belongs in the report subtitle.

---

**Footnote numbering convention.**

- Footnotes are numbered sequentially (¹, ², ³...) across the entire report, regardless of which section generated the overflow.
- The superscript appears immediately after the last word of the capped content in the cell: "Spring confirmed, dealer long gamma¹"
- Footnotes appear in the legend/footer in the order their superscripts appear in the report, top to bottom, left to right.
- A footnote is self-contained: it begins with the ticker or position it refers to, then the field name, then the full content. Format: "¹ HON | Rationale: Spring confirmed on above-average volume with dealer flipping long gamma intraday; IV rank at 34th percentile supports naked long-call structure at current sizing band; near-flip flag not active."
- When a source bar overflow moves to footnote ¹, all other footnotes in the session shift to ² onward.

---

**Exited positions summary format.**

Present when at least one position carries State = Exited. Appears after per-position detail, before Expired positions section.

One row per Exited position: Ticker, Structure, Direction, Strike(s), Expiration, Entry Date, Exit Date, Entry Price, Exit Price, P/L (dollar and percent), Exit reason (20 chars cap: "Profit target hit", "Stop hit", "Operator close", "Expired worthless").

---

**Expired positions requiring acknowledgment format.**

Present when at least one position carries State = Expired. Never absent when Expired positions exist. Appears as the final section before the legend/footer in Portfolio and Hybrid modes.

One row per Expired position: Ticker, Structure, Strike(s), Expiration, Entry Price, Expiry value (usually $0.00), P/L. A one-line acknowledgment prompt follows the table: "Expired positions above require operator acknowledgment and removal from active position context before next session."

The acknowledgment prompt is not a footnote — it is body text within the section. It is the only body text in the report that addresses the operator directly.
