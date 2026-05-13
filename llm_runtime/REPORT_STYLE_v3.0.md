---
system: KapMan
doc_type: style
kb_version: 3.0.0
file_last_updated: 2026-05-13
status: active
tier: T3
---

# REPORT STYLE

## Principle

REPORT_STYLE owns the visual surface of every report Claude produces: the typography, color palette, semantic row classes, badge vocabulary and CSS, column widths, two-column layout, footnote rendering, source bar styling, and the legend/footer visual treatment. It does not own what appears in any field, how fields are ordered, or any behavioral rule — those belong to REPORT_FORMAT and the upstream T1/T2 files respectively. The governing principle of REPORT_STYLE is that visual weight must match decision urgency. A Monday-morning operator scanning a portfolio view must be able to locate the highest-urgency item — an Expired position requiring acknowledgment — without reading every row; the next-highest-urgency item — an Advisory position with an active decay warning — must be distinguishable from a routine Open position at a glance; and routine Open positions must not compete visually with either. The palette is therefore structured as a four-level urgency hierarchy: neutral (Open), cautionary (DTE decay warning active), advisory (State = Advisory), and critical (State = Expired, unacknowledged). Each level is visually distinct from the adjacent level, not merely from the extremes. The same hierarchy governs the screening surface: the Macro Regime card, NO_TRADE rows, and chain quality degradation badges each occupy a distinct urgency band. REPORT_STYLE does not introduce new urgency levels; it implements the ones REPORT_FORMAT and PORTFOLIO_MGMT have already specified. Every CSS decision in this file is derivable from that principle: if a visual choice does not serve scan speed or urgency disambiguation, it is not in this file.

---

## Operational heuristics

**The urgency hierarchy has four levels. Never collapse adjacent levels into the same visual treatment.**

The four levels, from lowest to highest urgency, are: Open (neutral), DTE decay warning active (cautionary), State = Advisory (advisory), State = Expired unacknowledged (critical). Each level must be distinguishable from its immediate neighbors — it is not sufficient that Expired looks different from Open; Advisory must also look different from DTE-warning-only at a glance, without requiring the operator to read the State field. The color and weight choices in the Appendix palette are calibrated for this adjacency requirement. When both DTE decay warning AND Advisory state are active simultaneously, `.advisory` governs — it is the higher urgency tier; the DTE condition is noted in the Flags cell text, not by escalating the row class further.

**Visual weight is allocated by urgency, not by data density.**

A row with more populated fields is not a more important row. The semantic row class is the only determinant of row background. Badge weight, text color, and cell emphasis follow the urgency level of the State field and active flags, not the volume of content in the row. A sparse Expired row outranks a densely populated Open row in every visual dimension.

**Badges label state, not quantity. One badge per cell is the default; two is the maximum.**

The badge vocabulary has a fixed mapping to conditions: chain quality labels go on chain quality cells; action labels go on the Action field; confidence labels go on the Confidence field. Badges are not stacked arbitrarily. When two conditions require simultaneous badging in the same cell (e.g., a Flags cell showing both an advisory flag and a DTE decay warning), one badge renders and the second renders as plain text with an appropriate semantic text color class. A cell never carries three badges.

**The semantic row class is applied once, to the `<tr>`. It is never applied at the cell level.**

Row color uniformity is required — partial row highlighting is not a valid state. If a cell's content warrants emphasis within a row, use a semantic text color class (`.red`, `.orange`, etc.) or a badge, not a second row-class applied to a `<td>`.

**The rationale column is left-aligned. All short data columns are center-aligned. This is not optional.**

Left-alignment on rationale, action, note, and flags cells is required because word-wrapped text becomes unreadable when center-aligned. Center-alignment on data cells (spot, DGPI score, DTE, confidence label, ticker, strike, expiration) is required because numeric comparison across rows depends on alignment. The column-alignment rules in the Appendix are hard specifications, not defaults.

**Print output suppresses background color unless `-webkit-print-color-adjust: exact` is declared.**

The reference CSS block in the Appendix includes both `-webkit-print-color-adjust: exact` and `print-color-adjust: exact`. Removing either declaration causes semantic row backgrounds and badge fills to disappear in print, leaving the operator with a monochrome output that loses all urgency signaling. Any print-path that uses a non-CSS rendering method must compensate with border or weight treatments that survive black-and-white output.

---

## Workflow integration

**Position in the document hierarchy.**

REPORT_STYLE is tier T3 — the visual implementation layer. It sits alongside REPORT_FORMAT in the rendering tier, consuming constraints that REPORT_FORMAT has already set, and applying them as CSS and typography. REPORT_STYLE does not override REPORT_FORMAT field caps; it implements them. REPORT_STYLE does not override GUARDRAILS behavioral mandates; it gives them visual form. The Expired row's critical visual treatment is the visual expression of PORTFOLIO_MGMT's mandate that Expired positions require acknowledgment — REPORT_STYLE does not define that requirement; it makes it impossible to miss.

**What REPORT_STYLE receives from upstream files.**

| Source file | What REPORT_STYLE consumes | How REPORT_STYLE uses it |
|---|---|---|
| `REPORT_FORMAT_v3.0.md` (T3) | Field cap numeric values; footnote numbering convention; source bar placement rule; legend/footer internal order | Implements column-width CSS from field caps; implements superscript CSS for footnote references; implements source bar visual block; implements legend/footer visual block |
| `PORTFOLIO_MGMT_v3.0.md` (T2) | Lifecycle state labels (Open/Advisory/Exited/Expired); DTE decay warning flag format; Advisory flag format | Assigns semantic row class and badge treatment per state label |
| `KAPMAN_GUARDRAILS_v3.0.md` (T0) | Urgency mandate for Expired positions; override acknowledgment placement | Implements critical visual tier (`.expired`) for Expired rows; ensures override acknowledgment text is visually distinct in subtitle or footnote position |
| `DEALER_v3.0.md` (T1) | Dealer-status labels (FULL/LIMITED/INVALID); chain quality badge vocabulary | Maps chain quality labels to tag color classes |
| `SIGNAL_v3.0.md` (T1) | Confidence band labels (High/Med/Low); action labels (ACT TODAY/MONITOR/NO_TRADE/WAIT) | Maps action labels to row class and badge class |

**What REPORT_STYLE does not own.**

| Concern | Owner |
|---|---|
| Which sections appear in which modes | `REPORT_FORMAT_v3.0.md` |
| Field cap word/line counts | `REPORT_FORMAT_v3.0.md` |
| When a lifecycle state is assigned | `PORTFOLIO_MGMT_v3.0.md` |
| When the DTE decay warning fires | `PORTFOLIO_MGMT_v3.0.md`, `SYSTEM_PARAMS_v3.0.md` |
| When the Expired state requires acknowledgment | `PORTFOLIO_MGMT_v3.0.md` |
| Label vocabulary for any badge | The T1 file that owns the domain |
| Override discipline | `KAPMAN_GUARDRAILS_v3.0.md` |

---

## Legacy anchors (for legend citations and back-compat)

**`KAPMAN_REPORT_STYLE_GLOSSARY_v2.3.md` — full migration.**

REPORT_STYLE_v3.0.md is the direct successor to `KAPMAN_REPORT_STYLE_GLOSSARY_v2.3.md`. All v2.3 content migrates; nothing is dropped. The following v2.3 sections map to v3.0 Appendix locations:

| v2.3 section | v3.0 Appendix section | Changes in v3.0 |
|---|---|---|
| TYPOGRAPHY | Typography | Body size updated 7.8pt → 7pt to align with table cell size; eliminates prose/table weight mismatch; source bar color updated from #555 → #444 to match footnote color for consistency |
| SPACING | Spacing | No changes |
| COLORS | Color palette | No changes to existing values |
| SEMANTIC ROW BACKGROUNDS | Semantic row classes | Four new classes added: `.advisory`, `.warn` (repurposed to DTE decay warning; was already present in v2.3 for caution rows — usage now specified more precisely), `.exited`, `.expired`; existing six classes preserved unchanged |
| SEMANTIC TEXT COLORS | Semantic text colors | No changes |
| BADGE TAGS | Badge vocabulary | New badge labels added for v3.0 portfolio constructs: `Advisory`, `DTE Warning`, `Exited`, `Expired`; new class `.tag-critical` added for Expired badge (inverted); existing labels and classes preserved |
| TABLE RULES | Table rules | No changes |
| COLUMN WIDTH CONSTRAINTS | Column widths | `rationale-col` confirmed at 180px (consistent with 20-word cap at 7pt Arial); `flags-col` added at 200px for portfolio view Flags field |
| TWO-COLUMN LAYOUT | Two-column layout | No changes |
| FOOTNOTE SECTION | Footnote CSS | No changes |
| SOURCE BAR | Source bar CSS | Source bar text color updated from #555 → #444 to match typography update |
| LEGEND / FOOTER | Legend/footer CSS | No changes |
| PRINT | Print spec | `-webkit-print-color-adjust: exact` and `print-color-adjust: exact` now explicitly required in print spec and reference CSS |
| REFERENCE CSS | Reference CSS block | Updated with new semantic row classes, `.tag-critical`, `.flags-col`, print-color-adjust declarations, and body font-size correction |

**Body font size reconciliation.** The v2.3 body size was 7.8pt with table cells at 7pt. In v3.0 the body size aligns to 7pt — the 7.8pt body created a visual rhythm mismatch where non-table prose appeared heavier than table content. Section headers remain at 8pt bold; title at 10.5pt.

**`rationale-col` pixel width and 20-word cap reconciliation.** At 7pt Arial (~4.5px/char average), 20 words × ~6 chars/word = ~120 chars ≈ 540px of inline text. In a 180px column this wraps to approximately 3 lines at line-height 1.25 — within the visual budget for compact row height. The 180px cap is confirmed consistent with REPORT_FORMAT's 20-word rationale cap. No pixel-width change required.

---

## Appendix — formulas and reference tables

### Typography

| Element | Size | Weight | Align | Other |
|---|---|---|---|---|
| body | 7pt | normal | — | Arial, sans-serif |
| title (h1) | 10.5pt | bold | center | letter-spacing .5px |
| subtitle (.subtitle) | 7pt | normal | center | color #444 |
| section header | 8pt | bold | left | white on dark bg |
| table header (th) | 6.8pt | bold | center | white on blue bg, nowrap |
| table cell (td) | 7pt | normal | — | line-height 1.25 |
| badge (.tag) | 6.5pt | bold | — | inline-block, nowrap |
| legend/footer | 6.5pt | normal | — | color #555 |
| footnote | 6.5pt | normal | — | color #444 |
| source bar | 6.5pt | normal | — | color #444, green left border |

---

### Spacing

| Element | Value |
|---|---|
| page padding | 10px 12px |
| print padding | 6px 8px |
| section header pad | 2px 6px |
| section margin | 5px top, 2px bottom |
| table header pad | 2px 3px |
| table cell pad | 1.5px 3px |
| table margin-bottom | 4px |
| two-col gap | 8px |
| badge pad | 0 4px |
| legend padding-top | 3px |
| legend margin-top | 4px |

---

### Color palette

| Role | Value | Usage |
|---|---|---|
| body text | #111 | default |
| muted text | #444 | subtitles, footnotes, secondary |
| gray text | #666 | notes, low-priority |
| section header bg | #1a1a2e | dark nav bar |
| section header text | #fff | — |
| table header bg | #2c3e6b | column headers |
| table header text | #fff | — |
| zebra stripe | #f7f8fc | even rows |
| row border | #e0e0e0 | cell bottom border |
| legend border | #ccc | top border above footer |
| footnote border | #ccc | dashed top border |

---

### Semantic row classes — complete v3.0 set

Apply to entire `<tr>` via class. Use `!important` to override zebra stripe. One class per row; the highest-urgency condition present determines the class.

| Class | Background | Urgency tier | Use when |
|---|---|---|---|
| (none) | #fff / #f7f8fc zebra | 0 — neutral | Open position, no active flags; Eligible candidate, no special state |
| `.monitor` | #f0f4ff | 0 — neutral/deferred | MONITOR action row; WAIT candidate; Exited position summary row |
| `.good` | #eafaf1 | 0 — positive | Profitable position; above flip; on track; positive P&L in Exited summary |
| `.exited` | #f0f0f0 | 0 — archive | Exited position summary row with neutral or unknown P&L |
| `.cond` | #f3e8ff | 1 — conditional | CONDITIONAL — blocked, awaiting trigger (screening use) |
| `.warn` | #fff8e1 | 1 — cautionary | DTE decay warning active, State = Open (no advisory); caution flag |
| `.act` | #fff3cd | 2 — action required | ACT TODAY action row |
| `.advisory` | #fde8e8 | 2 — advisory | State = Advisory; regime exit advisory active (one or more decay branches fired) |
| `.urgent` | #fde8e8 + left border | 3 — high urgency | Stop triggered; worst position; exit signal (screening/portfolio) |
| `.expired` | #c0392b bg, #fff text | 4 — critical | State = Expired, unacknowledged — highest urgency in the palette; reserved exclusively for this condition |

**Adjacency notes:**

`.advisory` and `.urgent` share the same base background (#fde8e8) but are differentiated by the left border accent on `.urgent` (`border-left: 3px solid #c0392b`). An operator scanning without reading can distinguish an Advisory position (no border) from an Urgent exit signal (red left border) at a glance.

`.warn` (warm yellow, #fff8e1) is visually distinct from `.advisory` (pink-red wash, #fde8e8) at adjacent rows — the hue difference is sufficient for urgency disambiguation without requiring the operator to read the State field.

`.expired` is the only class that inverts the text/background relationship. Dark red background with white text is the strongest available signal in the palette and is reserved exclusively for Expired unacknowledged positions. It must not be repurposed.

When both DTE decay warning AND State = Advisory are active on the same position, `.advisory` is the governing class. The DTE condition is noted in the Flags cell as `.orange` text; no row-class escalation occurs beyond `.advisory`.

---

### Semantic text colors

| Class | Color | Weight | Use when |
|---|---|---|---|
| `.red` | #c0392b | bold | Negative P&L, stop levels, broken, loss; label text in `.expired` rows where inversion is insufficient |
| `.green` | #1a7a3c | bold | Positive P&L, above flip, supportive, gain |
| `.orange` | #d35400 | bold | Caution, approaching threshold; DTE decay warning label text; secondary flag text in advisory rows |
| `.blue` | #1a4fa0 | bold | Informational emphasis |
| `.gray` | #666 | normal | Secondary notes, N/A fields, "—" placeholders |

---

### Badge vocabulary — complete v3.0 set

All badges: `display: inline-block`, `padding: 0 4px`, `border-radius: 2px`, `font-size: 6.5pt`, bold, `white-space: nowrap`.

| Class | Background | Text | Example labels |
|---|---|---|---|
| `.tag-red` | #fde8e8 | #c0392b | Below flip, EXIT, STOP, Weak chain, INVALID |
| `.tag-green` | #eafaf1 | #1a7a3c | Above flip, ACT, Full chain, HOLD |
| `.tag-orange` | #fff3cd | #a04000 | MONITOR, Near flip, CONDITIONAL, DTE Warning |
| `.tag-gray` | #f0f0f0 | #555 | N/A, Low conf, Needs validation, Exited |
| `.tag-blue` | #e8f0fe | #1a4fa0 | Candidate zone, Info, Advisory |
| `.tag-purple` | #f3e8ff | #6b21a8 | Ranked conditional (#1, #2, #3) |
| `.tag-critical` | #c0392b | #fff | Expired (unacknowledged) — inverted; reserved exclusively for this badge |

**Badge label mapping — v3.0 portfolio constructs:**

| Condition | Badge label | Badge class | Notes |
|---|---|---|---|
| State = Advisory | `Advisory` | `.tag-blue` | Row class carries urgency signal; badge is informational |
| DTE decay warning only (State = Open) | `DTE Warning` | `.tag-orange` | Row class `.warn` |
| Both Advisory + DTE decay warning active | `Advisory` badge + `.orange` DTE text | `.tag-blue` + `.orange` | Row class `.advisory` governs; two elements, not two badges |
| State = Exited | `Exited` | `.tag-gray` | Row class `.exited` or `.monitor` |
| State = Expired (unacknowledged) | `Expired` | `.tag-critical` | Row class `.expired`; strongest signal in palette |
| Chain quality: Full | `Full chain` | `.tag-green` | Source bar and chain quality badge key |
| Chain quality: Limited | `Limited chain` | `.tag-orange` | Floor sizing applied |
| Chain quality: Invalid | `INVALID` | `.tag-red` | Candidate dropped from Pass 2 |

---

### Table rules

- `width: 100%`
- `border-collapse: collapse`
- Compact row height
- Bold centered headers
- Thin border-bottom on body cells (`1px solid #e0e0e0`)
- `vertical-align: middle`
- `line-height: 1.25`
- Zebra on even rows (`#f7f8fc`) — overridden by semantic row class via `!important`
- Left-align: rationale, action, note, flags cells
- Center-align: all short data cells (spot, DGPI, DTE, confidence, ticker, strike, expiration)

---

### Column widths

| Class | Max width | Alignment | Notes |
|---|---|---|---|
| `.rationale-col` | 180px | left | Confirmed consistent with 20-word cap at 7pt Arial; ~3 lines at line-height 1.25 |
| `.action-col` | 165px | left | Portfolio ACT table action field |
| `.note-col` | 150px | left | HOLD/MONITOR table note field |
| `.stop-col` | 50px | center | Underlying alert price only |
| `.scale-col` | 70px | center | Two scale levels max |
| `.flags-col` | 200px | left | Portfolio view Flags field — wider than rationale-col to accommodate dual-flag text (Advisory + DTE warning together without forcing footnote overflow) |

---

### Two-column layout

- `display: grid`
- `grid-template-columns: 1fr 1fr`
- `gap: 8px`
- `margin-top: 4px`

Used for sidebar sections below the main table (alerts, discards, risks, dealer snapshot, week-over-week changes, equities, checklist).

---

### Footnote CSS

- `font-size: 6.5pt`
- `color: #444`
- `border-top: 1px dashed #ccc`
- `padding-top: 2px`
- `margin-top: 2px`
- Placed between main content and legend/footer per REPORT_FORMAT element sequence

---

### Source bar CSS

- `font-size: 6.5pt`
- `color: #444`
- `background: #f0f7f0`
- `border-left: 3px solid #2c5e2c`
- `padding: 2px 6px`
- `margin: 0 0 2px 0`

Appears immediately below subtitle per REPORT_FORMAT placement rule. Text color updated from v2.3 #555 to #444 to match footnote color.

---

### Legend/footer CSS

- `font-size: 6.5pt`
- `color: #555`
- `margin-top: 4px`
- `border-top: 1px solid #ccc`
- `padding-top: 3px`

Internal element order governed by REPORT_FORMAT. REPORT_STYLE owns only the visual block.

---

### Print spec

- `@page size: landscape`
- `margins: 0.35in 0.3in`
- `body padding: 6px 8px`
- Target: one page or near-one-page
- Avoid long narrative and whitespace
- `-webkit-print-color-adjust: exact` and `print-color-adjust: exact` are required to preserve semantic row backgrounds and badge fills in print output. Both declarations must be present; `-webkit-print-color-adjust` alone is insufficient on non-WebKit print paths.

---

### Reference CSS block — complete v3.0

```css
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:Arial,sans-serif;font-size:7pt;color:#111;background:#fff;padding:10px 12px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
h1{font-size:10.5pt;font-weight:bold;text-align:center;letter-spacing:.5px;margin-bottom:3px;}
.subtitle{text-align:center;font-size:7pt;color:#444;margin-bottom:6px;}
.source-bar{font-size:6.5pt;color:#444;background:#f0f7f0;border-left:3px solid #2c5e2c;padding:2px 6px;margin:0 0 2px 0;}
.section-title{font-size:8pt;font-weight:bold;background:#1a1a2e;color:#fff;padding:2px 6px;margin:5px 0 2px 0;letter-spacing:.4px;}
table{width:100%;border-collapse:collapse;margin-bottom:4px;}
th{background:#2c3e6b;color:#fff;font-size:6.8pt;font-weight:bold;padding:2px 3px;text-align:center;white-space:nowrap;}
td{font-size:7pt;padding:1.5px 3px;border-bottom:1px solid #e0e0e0;vertical-align:middle;line-height:1.25;}
tr:nth-child(even) td{background:#f7f8fc;}
/* Semantic row classes — ordered by urgency tier */
.monitor{background:#f0f4ff!important;}
.good{background:#eafaf1!important;}
.exited{background:#f0f0f0!important;}
.cond{background:#f3e8ff!important;}
.warn{background:#fff8e1!important;}
.act{background:#fff3cd!important;}
.advisory{background:#fde8e8!important;}
.urgent{background:#fde8e8!important;border-left:3px solid #c0392b;}
.expired{background:#c0392b!important;color:#fff!important;}
.expired td{color:#fff!important;border-bottom:1px solid #a93226;}
/* Semantic text colors */
.red{color:#c0392b;font-weight:bold;}
.green{color:#1a7a3c;font-weight:bold;}
.orange{color:#d35400;font-weight:bold;}
.blue{color:#1a4fa0;font-weight:bold;}
.gray{color:#666;}
/* Badge tags */
.tag{display:inline-block;padding:0 4px;border-radius:2px;font-size:6.5pt;font-weight:bold;white-space:nowrap;}
.tag-red{background:#fde8e8;color:#c0392b;}
.tag-green{background:#eafaf1;color:#1a7a3c;}
.tag-orange{background:#fff3cd;color:#a04000;}
.tag-gray{background:#f0f0f0;color:#555;}
.tag-blue{background:#e8f0fe;color:#1a4fa0;}
.tag-purple{background:#f3e8ff;color:#6b21a8;}
.tag-critical{background:#c0392b;color:#fff;}
/* Column widths */
.rationale-col{max-width:180px;}
.action-col{max-width:165px;}
.note-col{max-width:150px;}
.stop-col{max-width:50px;}
.scale-col{max-width:70px;}
.flags-col{max-width:200px;}
/* Two-column layout */
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:4px;}
/* Footnote and legend */
.footnote{font-size:6.5pt;color:#444;border-top:1px dashed #ccc;padding-top:2px;margin-top:2px;}
.legend{font-size:6.5pt;color:#555;margin-top:4px;border-top:1px solid #ccc;padding-top:3px;}
/* Print */
@media print{body{padding:6px 8px;}@page{size:landscape;margin:.35in .3in;}}
</style>
```
