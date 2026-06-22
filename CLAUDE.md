# CLAUDE.md — KapMan Knowledge Base

Full workflow, hard rules, and templates live in **`AGENTS.md`** — read it
before any change. `INDEX.md` is the source of truth for the file list and the
rule-ID migration table; `CHANGELOG.md` is the source of truth for what changed
per release. This file is the short orientation those don't lead with.

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
4. **Sources of truth.** Consult `INDEX.md` for the current file inventory; do
   not hardcode file names. Legacy rule IDs are load-bearing — never drop one
   silently.

## Delivery default for this repo
Work is delivered **directly to `main`** (no feature branch, no PR). Still
**create a GitHub issue before the change and close it after**, reference the
issue in the commit, and run the validation suite before committing. Full
details and the definition of done are in `AGENTS.md`.
