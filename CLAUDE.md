# CLAUDE.md — KapMan Knowledge Base

## First: which kind of session is this?

This repo serves two different jobs. Determine the mode for each request
before acting — mode decides which instructions govern and which repo is
writable. Mode is per-request, not per-session: re-evaluate on each new ask,
and say so in one line when it flips ("switching to maintenance for this
request").

**USE — operate the methodology.** Signals: a pasted viewer/tradelog export;
"run pass 1 / pass 2 / screening / portfolio review"; ticker lists; questions
about positions or regime.
→ Your instructions are `llm_runtime/`, entered via
`KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md` (T0) and its session entry
sequence. Treat THIS repo as **read-only**; run artifacts (handoffs, pass
logs, memory) are written to `kapman-journal` per `JOURNAL_MGMT_v4.0.md`.
If a USE session surfaces a KB defect, flag it or open an issue — never fix
KB content mid-run.

**MAINTAIN — edit the knowledge base.** Signals: "edit/update/fix/scaffold
<file>"; rule-ID or INDEX/CHANGELOG work; frontmatter, validation scripts,
version bumps, archiving.
→ Read **`AGENTS.md`** before any change and follow its workflow. Write only
to this repo; never write trade data anywhere.

**Ambiguous** ("fix the earnings screen" could be either): ask one scoped
question before proceeding. Do not guess and produce output.

### USE-mode routing (order matters; details live in the named files)

1. `INDEX.md` → current file inventory (never hardcode file names)
2. `llm_runtime/KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md` → session entry
   sequence (date, mode detection, memory load, lineage, macro gate)
3. `kapman-journal/memory/` → load and announce per `JOURNAL_MGMT_v4.0.md`
4. On a pasted export: derive lineage from `exported_at`, stage the handoff
5. Proceed to mode output per the T1/T2/T3 files KPSI routes to
6. Stage journal writes (Rule 7 log manifest) before rendering output

This section is a router only. It restates no rule; when it appears to
conflict with a `llm_runtime/` file, that file governs.

## What this repo is
A versioned **markdown knowledge base** consumed by LLMs at chat time — not
application code. No servers, no build, no functional tests. "Validation" is
structural: file presence, rule-ID parity, frontmatter integrity (run
`scripts/verify_frontmatter.sh` and `scripts/verify_anchors.sh`).

## The four things to get right
1. **The upload split is hard.** `llm_runtime/` is uploaded to LLM project
   knowledge; `engineering_only/` is NOT. Never let content leak across that
   boundary in either direction.
2. **`archive/` is read-only.** Never modify, rename, or delete anything under
   `archive/` without an issue and explicit user approval.
3. **Mechanical vs. substantive split.** Scaffolding, file moves, INDEX/CHANGELOG
   updates, and git ops are fully autonomous. Writing or rewriting principle
   paragraphs, judgment bands, and rule consolidations is human-in-the-loop —
   draft those turn-by-turn with the user, never autonomously.
   The mechanical/substantive split applies to MAINTAIN sessions; USE
   sessions do not edit this repo at all.
4. **Sources of truth.** Consult `INDEX.md` for the current file inventory; do
   not hardcode file names. Legacy rule IDs are load-bearing — never drop one
   silently.

## Delivery default for this repo
Work is delivered **directly to `main`** (no feature branch, no PR). Still
**create a GitHub issue before the change and close it after**, reference the
issue in the commit, and run the validation suite before committing. Full
details and the definition of done are in `AGENTS.md`.
This section governs MAINTAIN sessions only; USE-session deliverables are
reports and `kapman-journal` writes, not commits here.
