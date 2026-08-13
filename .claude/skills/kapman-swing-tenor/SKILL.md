---
name: kapman-swing-tenor
description: |
  Run the weekly KapMan Swing Tenor Scan — a standalone UP/DOWN/CHOP market-tenor
  call for the next 60-120 days (the SWING_DTE_BAND horizon), per the pilot spec
  in kapman-kb/docs/SWING_TENOR_SCAN_PILOT_v0.1.md.

  USE THIS SKILL when the user asks to: "run the tenor scan", "swing tenor",
  "market tenor", "weekly tenor", "what's the market tenor", "up/down/chop call",
  or to back-fill/score a past tenor call. This is NOT the daily market scan and
  NOT Pass 1 screening (use kapman-screen for that) — its output is standalone
  context, never consumed by Pass 1/Pass 2.

  Always use live MCP data (Schwab, kapman-polygon, FMP, Finnhub, Bigdata.com);
  never use training data for prices or vol values.
metadata:
  spec: docs/SWING_TENOR_SCAN_PILOT_v0.1.md
  uploaded_revision: a476ee6
  uploaded_at: 2026-08-13
---

# Swing Tenor Scan

**Source of truth:** `kapman-kb/docs/SWING_TENOR_SCAN_PILOT_v0.1.md`. Read it
in full before Step 1 — it owns the variables and their producers (§3), the
composition rule and confidence brakes (§4), the report section order (§5),
the deterministic outcome-scoring rule (§6), the pilot re-evaluation gate (§7),
the verified tool-surface notes and endpoint corrections (§8), and the rule
clarifications effective 2026-08-03 (§9). Every threshold tagged **[CAL]**
lives there too.

**This file owns the run procedure only** — step sequencing, output routing,
and the hard rules below. It deliberately carries **no** copy of the variable
list, thresholds, producers, endpoints, tool-surface workarounds, composition
arithmetic, or scoring bands. **Where this file and the spec disagree, the
spec wins** — and if you find something here that looks like spec content,
that is a bug in this file, not a second opinion.

Why the rule is that blunt: this file used to paraphrase the spec, and the
paraphrase went stale **three times** — `4c2369f` (2026-07-29, the 1.8
far-dated dealer path), `059dad6` (2026-07-29, 1.7 consuming
`realized_vol.hv20_hv60_ratio`), and `7c2e99b` (2026-08-09, the pinned CFTC
field surface) each changed the spec while this file kept saying the old
thing. The stale 1.8 line is what degraded 1.8 on a live run. The fix is not
better copy discipline, it is holding no copy — the same reason
`kapman-screen` is only pointers and has never drifted.

Forward log lives in `kapman-journal/log/tenor/` (record grammar in that
directory's `README.md`). Real calls and outcomes go ONLY in kapman-journal,
never in kapman-kb.

## Run procedure

### Step 0 — Housekeeping
1. Read the spec in full, then the journal `log/tenor/README.md`.
2. Check the most recent `log/tenor/<YYYY-MM>/tenor_*.md` entries:
   - Back-fill any `Outcome` section whose +60d/+120d window has closed, by
     the deterministic rule in **spec §6** — fetch the SPY daily history the
     rule needs and apply it as written; no after-the-fact judgment.
   - Note the standing call and its invalidation conditions.
3. Determine the trigger — `scheduled`, `invalidation`, or `correction` — per
   **spec §2**, and say which condition or correction prompted a non-scheduled
   run.

### Step 1 — Data pulls (all live)
Pull every variable in **spec §3**, layer by layer, from the producer the spec
names for it. Read **spec §8** first and follow it exactly: it pins the
verified call shapes, the symbology, the dataset and field names, the retired
endpoints, and the known producer bugs and their workarounds. Those notes were
each written after a live run got it wrong; treat them as binding, not as
background.

A variable whose source fails to resolve is recorded as **degraded** and
scored 0 — named in the report, never silently assumed favorable (spec §3).
Before writing "degraded" for anything, vary the parameter, retry, and check
whether a sibling endpoint or producer serves it. Most of the pilot's early
corrections came from assuming a gap instead of testing one (spec §8).

### Step 2 — Compute (script it; no mental arithmetic)
Compute each **spec §3** variable and both layer scores, applying the §3
thresholds and the §9 clarifications as literally written. Record the value
behind every read so the report can show the work.

### Step 3 — Compose the call
Apply the **spec §4** composition rule to get the tenor call, then §4's
confidence rule including the structural confidence brake, then name the 2–4
observable invalidation conditions §4 requires.

Show the composition inputs and the chop-pressure flag's per-condition results
— which fired, which did not — in the report. The flag decides the call at the
§4 boundary, so an unshown flag is an unverifiable call. It is the literal
test in **spec §3**, sharpened in **§9.1**; nothing outside that list sets it.

### Step 4 — Report + log
1. Render the report in the **spec §5** section order, labeled *"Standalone
   context — not consumed by Pass 1 / Pass 2."*
2. Write the journal entry `log/tenor/<YYYY-MM>/tenor_YYYY-MM-DD.md` per the
   README grammar (frontmatter + sections + PENDING Outcome). One file per
   run, append-only — never edit a prior run's call sections; a correction is
   a new superseding entry (spec §2).
3. Commit/push kapman-journal per that repo's delivery rules.

## Hard rules
- The spec is the source of truth for every variable, threshold, producer, and
  rule. This file never overrides it, and never restates it.
- Conservative defaults: conflict and boundary cases resolve per spec §4;
  degraded inputs are named, never silently favorable.
- Deterministic outcome scoring only (spec §6) — no after-the-fact judgment.
- Tenor calls never gate, veto, tilt, or size Pass 1/Pass 2 work; the output is
  standalone context (spec §1).
- Threshold changes ([CAL] items) are operator decisions — propose, don't
  self-tune; the pilot re-evaluation gate is spec §7.
- Real calls and outcomes live only in kapman-journal, never in kapman-kb.
