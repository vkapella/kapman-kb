# AGENTS.md

## Project overview
KapMan Knowledge Base is a versioned markdown repository containing the
operational rules and reference documentation for the KapMan systematic
options-trading framework. It is consumed by LLMs (Claude, Gemini, and
others) at chat time, not by application code. Files in `llm_runtime/`
are uploaded to LLM project knowledge; files in `engineering_only/` are
reference for humans and code agents and are NOT uploaded to LLMs.

Use `INDEX.md` as the source of truth for the current file list and the
rule-ID migration table. Use `CHANGELOG.md` as the source of truth for
what changed in each release. Use any `MIGRATION_*.md` file at the repo
root for one-time guidance during a specific major-version refactor;
those files get archived after cutover.

This is a documentation repository, not application code. There are no
runtime servers, build systems, or unit tests. Validation is structural
(file presence, rule-ID parity, frontmatter integrity), not functional.

## How to work in this repository

This repository has a hard split between two kinds of work. Agents must
respect this split — it is the most important rule in this file.

### Mechanical work — FULLY AUTONOMOUS

Execute end-to-end without stopping. Examples:
- Creating directory structure
- Scaffolding empty files with frontmatter and section headers
- Extracting legacy rule IDs from archived source files
- Building or updating `INDEX.md` migration table
- Adding `CHANGELOG.md` entries
- File moves, renames, and deletions per an explicit mapping
- Setting up `.gitignore`, `README.md`, frontmatter fields
- Running validation scripts and fixing structural failures
- Git operations (issue, commit, push to `main`, close issue)

### Substantive content work — HUMAN-IN-THE-LOOP

Do NOT execute autonomously. Always draft in a Claude.ai chat session
with the user reviewing turn-by-turn. Examples:
- Writing principle paragraphs
- Rewriting threshold cliffs as judgment bands
- Drafting operational heuristics
- Consolidating rule content from multiple archived sources
- Deciding what content to drop vs. preserve
- Translating formulas into prose explanations
- Authoring new content for any file in `llm_runtime/`

If an issue is mixed (e.g., "scaffold the file and write the principle"),
execute only the mechanical half. Stop with a clear handoff note listing
what content work remains.

### General rules
- Make the most conservative reasonable assumption when details are
  missing in a mechanical task.
- For substantive tasks, STOP and report — do not guess.
- Before editing, inspect existing files and follow established patterns.
- After each meaningful change, run the narrowest relevant validation step.
- Preserve `archive/` as read-only. Never modify, rename, or delete files
  in any archived version folder.

## Git and GitHub workflow — FULLY AUTONOMOUS for mechanical work

**Delivery model: direct-to-`main`.** This repo ships changes by committing
straight to `main` — no feature branch, no pull request, no auto-merge. A
GitHub issue is still created before and closed after every change. For
mechanical changes, execute ALL of the steps below without stopping. For
substantive content changes, the user drives — you only execute Git steps
after the user has approved the content in a Claude.ai session.

### Step 1 — Create a GitHub issue before any change

```bash
gh issue create --title "<short title>" --body "<acceptance criteria>"
```

Note the issue number returned. Every commit for this change must
reference this issue number.

### Step 2 — Implement on `main`, then commit with the issue reference

Work directly on `main` (confirm with `git status -sb` first). Commit with
a conventional-commit prefix and a `(closes #NNN)` trailer so merging the
commit closes the issue:

```bash
git commit -m "<prefix>: <description> (closes #NNN)"
```

Prefix conventions:
- `refactor:` — major-version refactor work
- `chore:` — tooling, scripts, validation infrastructure
- `docs:` — non-refactor documentation edits
- `fix:` — corrections to existing active content
- `archive:` — archiving past major versions

### Step 3 — Run the full validation suite yourself — do not skip any step

```bash
# Verify no archive files were touched
git diff --name-only origin/main..HEAD | grep '^archive/' && \
  echo "ERROR: archive/ must not be modified" && exit 1

# Verify legacy anchor parity (if script exists)
[ -x scripts/verify_anchors.sh ] && scripts/verify_anchors.sh

# Verify frontmatter integrity (if script exists)
[ -x scripts/verify_frontmatter.sh ] && scripts/verify_frontmatter.sh
```

If any command exits non-zero, fix all failures before proceeding.
Do not proceed with a broken state. Do not report failures to the human
and ask what to do — fix them.

### Step 4 — Push `main` to origin

```bash
git push origin main
```

`main` is not branch-protected, so the push lands directly. If a push is
ever rejected (protection added later, non-fast-forward, etc.), report the
exact blocker and the exact command to resolve it — do not silently retry
with force.

### Step 5 — Confirm the issue closed; close it explicitly if not

A pushed commit carrying `(closes #NNN)` closes the issue automatically.
Verify, and close manually if the trailer was missed:

```bash
gh issue view NNN --json state -q .state   # expect: CLOSED
gh issue close NNN --comment "Resolved in <commit-sha>"   # only if still OPEN
```

### Step 6 — Confirm a clean local checkout

```bash
git status -sb
```

The final status must show `main` tracking `origin/main`, up to date, with
no uncommitted changes left behind.

## Repository layout

```
kapman-kb/
├── README.md
├── INDEX.md             ← single source of truth for current file list + rule-ID migration table
├── CHANGELOG.md         ← release log, one section per version
├── AGENTS.md            ← this file
├── MIGRATION_*.md       ← optional, one per active major-version migration; archived after cutover
├── .gitignore
├── llm_runtime/         ← uploaded to LLM project knowledge (Claude.ai, Gemini, etc.)
├── engineering_only/    ← NOT uploaded to LLMs; reference for humans and code agents
├── archive/             ← one folder per archived major.minor version; read-only
│   ├── vX.Y/
│   └── vA.B/
└── scripts/             ← validation scripts (verify_anchors.sh, verify_frontmatter.sh, ...)
```

The specific file list inside `llm_runtime/`, `engineering_only/`, and
`archive/` changes per release. **Always consult `INDEX.md` for the
current file inventory** — do not hardcode file names into this guide
or into scripts that survive across releases.

New files follow this layout:

| Type                            | Location              |
|---------------------------------|------------------------|
| New principle (T1)              | `llm_runtime/`         |
| New runbook (T2)                | `llm_runtime/`         |
| New style or format spec (T3)   | `llm_runtime/`         |
| New engineering reference (T4)  | `engineering_only/`    |
| Validation script               | `scripts/verify_<purpose>.sh` |

Tier model (lives in file frontmatter — not directory paths):

| Tier | Role                                  | Folder              |
|------|---------------------------------------|---------------------|
| T0   | Guardrails and orientation            | `llm_runtime/`      |
| T1   | Principles (one per trading domain)   | `llm_runtime/`      |
| T2   | Runbooks (procedural workflows)       | `llm_runtime/`      |
| T3   | Style, output format, reference maps  | `llm_runtime/`      |
| T4   | Backend pipeline and tool reference   | `engineering_only/` |

## File naming convention
- Format: `<NAME>_vMAJOR.MINOR.md` (dots, not underscores).
- Filename suffix bumps only on **major** version (`vN.0` → `v(N+1).0`).
- Patch and minor changes within a major track in the file's
  `kb_version` frontmatter field and in `CHANGELOG.md`, NOT in the
  filename. Renaming every file on a patch release is the brittleness
  pattern this rule exists to prevent.
- Archive folder is `archive/vMAJOR.MINOR/`.

## Architecture boundaries
- `llm_runtime/` ⇄ `engineering_only/` separation is hard. Operational
  rules consumed by LLMs at chat time go in `llm_runtime/`. Backend
  pipeline rules, deprecated tool inventories, schema bounds, and other
  engineering reference go in `engineering_only/`.
- `archive/` is read-only. Never modify files in any archived version
  folder. If correcting a typo in an archived file is unavoidable, raise
  an issue first and get explicit user approval.
- `INDEX.md` is the single source of truth for the rule-ID migration
  table. Every legacy rule ID from every archived version must have one
  row mapping it to its current destination (or to `DROPPED` status).
- `CHANGELOG.md` is the single source of truth for release-level
  history. Per-file changelog tables are NOT used; rely on git log plus
  frontmatter `file_last_updated`.

## File template — principle-first

Every file in `llm_runtime/` follows this template:

```markdown
---
system: KapMan
doc_type: principle               # or "orientation" for top-level project system instructions
kb_version: <MAJOR.MINOR.PATCH>
file_last_updated: YYYY-MM-DD
status: scaffolding | draft | active
tier: T0 | T1 | T2 | T3
---

# {DOMAIN}

## Principle
One paragraph stating the judgment governing this domain.

## Operational heuristics
Bands of judgment, not threshold cliffs. Bullet list.

## Workflow integration
Cross-references to relevant runbooks.

## Legacy anchors (for legend citations and back-compat)
Every legacy rule ID that maps to this file, with a short pointer to
the section above that supersedes it.

## Appendix — formulas and reference tables
Mathematical formulas, decision tables, and any content that doesn't
fit naturally into the principle / heuristics / workflow structure.
```

## File template — reference (lookup tables)

Files in `llm_runtime/` with `doc_type: reference` are pure lookup tables with no
behavioral rules. They use a reduced template:

```markdown
---
system: KapMan
doc_type: reference
kb_version: <MAJOR.MINOR.PATCH>
file_last_updated: YYYY-MM-DD
status: scaffolding | draft | active
tier: T0 | T1 | T2 | T3
---

# {DOMAIN}

One paragraph stating what this file contains and what it does not own.

## {Primary content section}
The lookup table or data content.

## Legacy anchors (for legend citations and back-compat)
Every legacy rule ID that maps to this file, or a statement that none exist.
```

This template applies to `SIC_SECTOR_MAP_v3.0.md`, `SYSTEM_PARAMS_v3.0.md`, and any
future `doc_type: reference` file added to `llm_runtime/`. The Principle, Operational
heuristics, Workflow integration, and Appendix sections are not required for reference
files; their omission is not a template compliance defect.

Files in `engineering_only/` use `doc_type: reference` and the section
structure: `## Purpose / ## Contents / ## Legacy anchors / ## Appendix`.

## Legacy rule-ID handling
Legacy rule IDs (e.g., `DEALER_009`, `SIGNAL_008`, `RISK_005`) from
prior major versions appear in chat memory references, report
legends/footers, and past trade journals. They are load-bearing and
must not be silently dropped.

Rules:
1. Every legacy rule ID from any archived version appears in `INDEX.md`'s
   migration table with a clear destination.
2. When a rule's content migrates into a current-version file, the rule
   ID becomes a named anchor in the destination file's `## Legacy anchors`
   section.
3. When a rule's content is intentionally dropped, the `INDEX.md` row is
   marked `DROPPED` with a short rationale.
4. The current major version uses named anchors, not new rule IDs.
   Creating new `<DOMAIN>_NNN` IDs is the brittleness pattern this rule
   exists to prevent.

## Rule-add discipline (for substantive content sessions)

Before drafting any new anchor, principle, or threshold in a Claude.ai
session, every answer below must be "no":

| # | Question                                                                              | If yes                                                |
|---|----------------------------------------------------------------------------------------|--------------------------------------------------------|
| 1 | Does an existing principle cover this if I generalize its language?                    | Modify the principle, don't add a new anchor.          |
| 2 | Is this the **third** version of a similar pattern (a "v1/v2/v3" patch thread)?        | Refactor the parent principle. Third version = brittleness alarm. |
| 3 | Is this a hardcoded numeric threshold handling an edge case?                           | Replace the parent's threshold with a band of judgment. |
| 4 | Is this a tool-surface or endpoint-name detail?                                        | Goes in the tool-surface reference in `engineering_only/`. |
| 5 | Is this backend pipeline behavior with no LLM runtime effect?                          | Goes in the backend reference in `engineering_only/`.  |
| 6 | Is this a single-incident observation?                                                 | Capture as journal note. Wait for the pattern to recur 3× before encoding. |
| 7 | Does the rationale begin with "in incident X..."?                                      | Pattern hasn't matured. Wait.                          |

## Refactor signals

Stop adding content and refactor when:

| Signal                                                          | Interpretation                                       |
|------------------------------------------------------------------|------------------------------------------------------|
| Same domain gains 3+ anchors in 6 months                        | Consolidate to a principle                           |
| An anchor has been amended 2+ times                             | Rewrite as judgment band, not threshold              |
| Exception clause is bigger than the rule body                   | Invert — the exception *is* the rule                 |
| Confidence downgraded STRICT → STRONG → MODERATE                | It's a heuristic, not a rule; move tier              |
| Two anchors cite each other in their logic                      | Coupling alarm; introduce a parent principle         |
| `[NOT YET IMPLEMENTED]` interim guidance > 12 months old        | Either implement or delete the placeholder           |

## Audit cadence

| Cadence            | Activity                                                                                          |
|--------------------|----------------------------------------------------------------------------------------------------|
| Monthly            | `git log --since='30 days ago' --diff-filter=A` on `llm_runtime/`. If >2 new anchors, raise refactor question. |
| Quarterly          | Full KB audit. Output: refactor backlog or explicit "no action." Tag a release marker either way. |
| Per major release  | Validate `INDEX.md` migration table is complete. No legacy ID without a destination.               |
| Per content session | Run rule-add checklist before any new content. Default to folding into a parent.                  |

## Validation and testing

This is a docs repo. "Tests" are structural checks, not functional unit tests.

### Required validation scripts (in `scripts/`)

`scripts/verify_anchors.sh` — verifies that every rule ID present in any
`archive/*/*.md` source file appears in `INDEX.md`'s migration table
with a destination (or with status `DROPPED`). Exits non-zero on missing
mappings.

`scripts/verify_frontmatter.sh` — verifies that every file in
`llm_runtime/` and `engineering_only/` has the required frontmatter
fields (`system`, `doc_type`, `kb_version`, `file_last_updated`,
`status`, `tier`). Exits non-zero on missing fields.

Both scripts must be executable (`chmod +x`). Both must pass before any
commit is pushed to `main`.

### Manual validation checklist (per substantive content session)

After the user reviews and approves a content draft in a Claude.ai
session, before pushing to `main`:

- [ ] All legacy rule IDs that should migrate to this file appear in
      the `## Legacy anchors` section
- [ ] No threshold cliff has been preserved when a judgment band was
      requested
- [ ] No content from `engineering_only/` has leaked into `llm_runtime/`
      (or vice versa)
- [ ] Frontmatter `file_last_updated` is set to today's date
- [ ] Frontmatter `status` is updated (`scaffolding` → `draft` → `active`)
- [ ] `CHANGELOG.md` has a new entry for this change
- [ ] `INDEX.md` is updated if any rule-ID destination changed

## Definition of done

Work is not complete unless all of the following are true and confirmed
by you, not reported to the human for confirmation:

For **mechanical work**:
- GitHub issue is open, referenced in the commit, and closed on completion
- `git diff` confirms no files in `archive/` were touched
- `scripts/verify_anchors.sh` exits 0 (or change does not affect anchors)
- `scripts/verify_frontmatter.sh` exits 0 (or change does not affect frontmatter)
- Commit is pushed to `main` (no PR); the issue is closed — verified via
  `gh issue view NNN --json state`
- Local checkout is on `main`, up to date with `origin/main`, with clean
  `git status -sb`

For **substantive content work**:
- All items above, PLUS
- The user has explicitly approved the content in the originating
  Claude.ai session before the changes were pushed
- The session transcript or summary is referenced in the commit message
- Manual validation checklist (above) is complete

## Off-limits
- **No autonomous content rewriting.** Principle paragraphs, judgment
  bands, operational heuristics, and rule consolidations are
  human-in-the-loop. Always.
- No modifying any folder under `archive/` for any reason without
  explicit user approval.
- No silent dropping of legacy rule IDs. Every dropped ID is explicitly
  marked `DROPPED` in `INDEX.md` with a rationale.
- No paraphrasing or summarizing archived content into current-version
  files during mechanical passes. Mechanical passes scaffold only.
- No new legacy-style rule IDs (e.g., `<DOMAIN>_NNN`). Current versions
  use named anchors instead.
- No directory nesting beyond the established `llm_runtime/` and
  `engineering_only/` flat structure. No subfolders within these.
- No filename version suffix bumps for patch or minor releases. Filename
  bumps are major-version-only.
- No per-file changelog tables. Use `CHANGELOG.md` and git log.
- No clarifying-question loops for mechanical work when a conservative
  implementation path exists.
- No instructing the human to run validation scripts, push commits, or
  close issues manually unless a true permission blocker exists and the
  exact unblocking command is provided.
- No version numbers hardcoded into this file or into scripts that
  survive across releases. Version-specific guidance lives in
  `INDEX.md`, `CHANGELOG.md`, or a one-time `MIGRATION_*.md` file.
