# MIGRATION_v2_to_v3.md

## Overview

One-time migration from KapMan KB v2.3 → v3.0. This file is the
version-specific addendum to `AGENTS.md`. It exists for the duration of
the v3.0 refactor and gets archived (or deleted) once v3.0 reaches
`status: active` across all files in `llm_runtime/` and
`engineering_only/`.

Anything that is true for *every* migration (git workflow, file template
structure, validation requirements, off-limits behaviors) lives in
`AGENTS.md` and is referenced here, not duplicated. This file contains
only what is specific to the v2.3 → v3.0 transition.

## Read first

Before executing any step in this file, read `AGENTS.md` in full. This
migration follows every rule there. Specifically:

| Topic                                  | Where it lives                            |
|----------------------------------------|--------------------------------------------|
| Mechanical vs substantive work split   | `AGENTS.md` → "How to work in this repository" |
| Git and GitHub workflow steps          | `AGENTS.md` → "Git and GitHub workflow"   |
| File naming convention                 | `AGENTS.md` → "File naming convention"    |
| File template (frontmatter + sections) | `AGENTS.md` → "File template"             |
| Legacy rule-ID handling principle      | `AGENTS.md` → "Legacy rule-ID handling"   |
| Validation scripts and checklist       | `AGENTS.md` → "Validation and testing"    |
| General off-limits behaviors           | `AGENTS.md` → "Off-limits"                |

If this file contradicts `AGENTS.md`, `AGENTS.md` wins.

## Scope

This migration is **mechanical only**, per the split in `AGENTS.md`.
That means:

| In scope (do autonomously)                                  | Out of scope (Claude.ai session, human-in-loop)              |
|--------------------------------------------------------------|---------------------------------------------------------------|
| Create the v3.0 directory structure                          | Write principle paragraphs                                    |
| Scaffold v3.0 files with frontmatter + section headers       | Rewrite RISK_005 as bands of judgment                         |
| Extract legacy rule IDs from `archive/v2.3/*.md`             | Consolidate Wyckoff phase + event content                     |
| Generate `INDEX.md` migration table                          | Decide what content to drop vs. preserve                      |
| Generate initial `CHANGELOG.md`, `README.md`, `.gitignore`   | Draft operational heuristics                                  |
| Run validation; open PR per `AGENTS.md` workflow             | Translate threshold cliffs into judgment language             |

Substantive content work begins in separate Claude.ai sessions after
this mechanical migration completes and is merged to `main`.

## Preconditions — verify before any writes

1. `archive/v2.3/` exists and contains exactly these 14 files:
   - `CONSTANTS_AND_CONFIG_v2.3.md`
   - `DEALER_POSITIONING_RULES_v2.3.md`
   - `KAPMAN_PROJECT_INSTRUCTIONS_v2.3.md`
   - `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v2.3.md`
   - `KAPMAN_REPORT_STYLE_GLOSSARY_v2.3.md`
   - `KAPMAN_SCORING_STUBS_v2.3.md`
   - `PIPELINE_ORCHESTRATION_v2.3.md`
   - `RISK_MANAGEMENT_RULES_v2.3.md`
   - `SIC_SECTOR_ETF_MAPPING_v2.3.md`
   - `SIGNAL_ENTRY_EXIT_RULES_v2.3.md`
   - `VALIDATION_STRIKE_SELECTION_v2.3.md`
   - `VOLATILITY_REGIME_RULES_v2.3.md`
   - `WYCKOFF_EVENT_DETECTION_RULES_v2.3.md`
   - `WYCKOFF_PHASE_CLASSIFICATION_v2.3.md`

2. `llm_runtime/` and `engineering_only/` do not exist OR are empty.

3. No `INDEX.md`, `CHANGELOG.md`, or `README.md` at repo root, OR the
   user has confirmed overwrite is acceptable.

4. `AGENTS.md` exists at repo root.

If any precondition fails, STOP and report. Do not guess or auto-fix.

## v2.3 → v3.0 file mapping

This is the canonical mapping for the migration. Every v2.3 source file
contributes legacy rule IDs to one or more v3.0 destinations.

| v2.3 source                                  | v3.0 destination(s)                                                                                                                |
|----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `WYCKOFF_PHASE_CLASSIFICATION_v2.3.md`       | `llm_runtime/WYCKOFF_v3.0.md`                                                                                                       |
| `WYCKOFF_EVENT_DETECTION_RULES_v2.3.md`      | `llm_runtime/WYCKOFF_v3.0.md`                                                                                                       |
| `DEALER_POSITIONING_RULES_v2.3.md`           | `llm_runtime/DEALER_v3.0.md`                                                                                                        |
| `VOLATILITY_REGIME_RULES_v2.3.md`            | `llm_runtime/VOLATILITY_v3.0.md`                                                                                                    |
| `RISK_MANAGEMENT_RULES_v2.3.md`              | `llm_runtime/RISK_v3.0.md` (RISK_005); `engineering_only/BACKEND_PIPELINE_v3.0.md` (RISK_001–004)                                   |
| `SIGNAL_ENTRY_EXIT_RULES_v2.3.md`            | `llm_runtime/SIGNAL_v3.0.md` (SIGNAL_005–010); `engineering_only/BACKEND_PIPELINE_v3.0.md` (SIGNAL_001–004)                         |
| `VALIDATION_STRIKE_SELECTION_v2.3.md`        | `llm_runtime/KAPMAN_GUARDRAILS_v3.0.md` (VALIDATION_001); `engineering_only/BACKEND_PIPELINE_v3.0.md` (VALIDATION_002–010)          |
| `KAPMAN_PROJECT_INSTRUCTIONS_v2.3.md`        | `llm_runtime/REPORT_FORMAT_v3.0.md`, `PASS1_SCREENING_v3.0.md`, `PASS2_VALIDATION_v3.0.md`, `PORTFOLIO_MGMT_v3.0.md`, `KAPMAN_GUARDRAILS_v3.0.md` |
| `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v2.3.md` | `llm_runtime/KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md`                                                                            |
| `KAPMAN_REPORT_STYLE_GLOSSARY_v2.3.md`       | `llm_runtime/REPORT_STYLE_v3.0.md`                                                                                                  |
| `SIC_SECTOR_ETF_MAPPING_v2.3.md`             | `llm_runtime/SIC_SECTOR_MAP_v3.0.md`                                                                                                |
| `CONSTANTS_AND_CONFIG_v2.3.md`               | `engineering_only/BACKEND_PIPELINE_v3.0.md`                                                                                         |
| `KAPMAN_SCORING_STUBS_v2.3.md`               | NONE — mark all rule IDs as `DROPPED` in `INDEX.md`                                                                                 |
| `PIPELINE_ORCHESTRATION_v2.3.md`             | `engineering_only/BACKEND_PIPELINE_v3.0.md` (PIPELINE_001–009); `engineering_only/TOOL_SURFACE_v3.0.md` (PIPELINE_010, 012); `llm_runtime/PASS2_VALIDATION_v3.0.md` (PIPELINE_011) |

## Target directory structure to create

```
kapman-kb/
├── README.md
├── INDEX.md
├── CHANGELOG.md
├── .gitignore
├── AGENTS.md                                              ← already exists
├── MIGRATION_v2_to_v3.md                                  ← this file
├── llm_runtime/
│   ├── KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md
│   ├── KAPMAN_GUARDRAILS_v3.0.md
│   ├── WYCKOFF_v3.0.md
│   ├── DEALER_v3.0.md
│   ├── VOLATILITY_v3.0.md
│   ├── RISK_v3.0.md
│   ├── SIGNAL_v3.0.md
│   ├── PASS1_SCREENING_v3.0.md
│   ├── PASS2_VALIDATION_v3.0.md
│   ├── PORTFOLIO_MGMT_v3.0.md
│   ├── REPORT_STYLE_v3.0.md
│   ├── REPORT_FORMAT_v3.0.md
│   └── SIC_SECTOR_MAP_v3.0.md
├── engineering_only/
│   ├── BACKEND_PIPELINE_v3.0.md
│   └── TOOL_SURFACE_v3.0.md
└── archive/v2.3/                                          ← already populated, DO NOT MODIFY
```

## Frontmatter values for this migration

Use the file template from `AGENTS.md`. For every v3.0 file created in
this migration, fill in the template placeholders as follows:

| Field                | Value for this migration                                |
|----------------------|---------------------------------------------------------|
| `kb_version`         | `3.0.0-alpha`                                           |
| `file_last_updated`  | Today's date in YYYY-MM-DD                              |
| `status`             | `scaffolding` (Claude sessions will bump to `draft` then `active`) |
| `tier`               | Per the table below                                     |

Tier assignments for this migration:

| File                                                | Tier | `doc_type`     |
|-----------------------------------------------------|------|----------------|
| `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md`        | T0   | `orientation`  |
| `KAPMAN_GUARDRAILS_v3.0.md`                         | T0   | `principle`    |
| `WYCKOFF_v3.0.md`                                   | T1   | `principle`    |
| `DEALER_v3.0.md`                                    | T1   | `principle`    |
| `VOLATILITY_v3.0.md`                                | T1   | `principle`    |
| `RISK_v3.0.md`                                      | T1   | `principle`    |
| `SIGNAL_v3.0.md`                                    | T1   | `principle`    |
| `PASS1_SCREENING_v3.0.md`                           | T2   | `runbook`      |
| `PASS2_VALIDATION_v3.0.md`                          | T2   | `runbook`      |
| `PORTFOLIO_MGMT_v3.0.md`                            | T2   | `runbook`      |
| `REPORT_STYLE_v3.0.md`                              | T3   | `style`        |
| `REPORT_FORMAT_v3.0.md`                             | T3   | `style`        |
| `SIC_SECTOR_MAP_v3.0.md`                            | T3   | `reference`    |
| `BACKEND_PIPELINE_v3.0.md`                          | T4   | `reference`    |
| `TOOL_SURFACE_v3.0.md`                              | T4   | `reference`    |

Files in `engineering_only/` use the section structure documented in
`AGENTS.md` for `doc_type: reference`: `## Purpose / ## Contents /
## Legacy anchors / ## Appendix`.

## Legacy rule-ID extraction

For each v2.3 source file in `archive/v2.3/`, parse out every line
matching `### RULE <ID>` or `RULE_ID: <ID>` and collect the IDs.

Expected ID prefixes and approximate counts (verify actual count
against archive files):

| Prefix          | Approximate count |
|-----------------|-------------------|
| `DEALER_`       | 14                |
| `WYCKOFF_EVENT_`| 13                |
| `WYCKOFF_PHASE_`| 13                |
| `VOLATILITY_`   | 15                |
| `RISK_`         | 5                 |
| `SIGNAL_`       | 10                |
| `VALIDATION_`   | 10                |
| `CONSTANTS_`    | 13                |
| `PIPELINE_`     | 12                |
| `SCORING_`      | 1                 |

For each extracted ID, write a placeholder line in the destination v3.0
file's `## Legacy anchors` section:

```
- <RULE_ID> → [content placeholder — to be filled in Claude session]
```

When a v2.3 source file splits across multiple v3.0 destinations (see
the mapping table above), route each rule ID to the correct destination
based on the sub-mapping noted in that table row.

## `INDEX.md` content

Generate `INDEX.md` with three sections:

1. **Repository structure** — brief description of `llm_runtime/` vs
   `engineering_only/` vs `archive/`. State that `llm_runtime/` files
   are uploaded to LLM project knowledge; `engineering_only/` files
   are not.

2. **v3.0 file directory** — table listing every v3.0 file with:
   `path`, `tier`, `doc_type`, brief role.

3. **v2.3 → v3.0 rule-ID migration table** — for every legacy rule ID
   extracted from `archive/v2.3/`, one row:

   ```
   | Legacy ID | v3.0 destination file | Anchor name | Status |
   ```

   `Status` is one of: `MIGRATED`, `DROPPED`, or `PENDING REWRITE`.
   For this mechanical pass, all status values are `PENDING REWRITE`
   except all `SCORING_*` IDs (currently just `SCORING_001`) which are
   `DROPPED` with rationale "Stub file with no implemented content;
   superseded by named anchors in destination principles."

## `CHANGELOG.md` initial content

```
# KapMan KB Changelog

## v3.0.0-alpha-setup — <today's date>

Mechanical scaffolding complete. Directory structure, file skeletons,
legacy anchor extraction, and migration table generated per
MIGRATION_v2_to_v3.md. No rule content rewritten yet. v2.3 files
preserved in archive/v2.3/.
```

## `README.md` initial content

Brief: state the repo is the KapMan trading-rules knowledge base.
Explain the two-folder model (`llm_runtime/` uploaded to LLM projects;
`engineering_only/` reference for humans and engineering tools).
Link to `INDEX.md` for the file directory and migration table. Link to
`AGENTS.md` for working rules. Note that the active KB version is
recorded in `CHANGELOG.md`.

## `.gitignore` initial content

```
.DS_Store
.vscode/
.idea/
*.swp
*.swo
~$*
.~lock.*
```

## Migration-specific hard constraints

(General off-limits behaviors are in `AGENTS.md`. These are additions
for this specific migration.)

- DO NOT write actual principle text, operational heuristics, judgment
  bands, formulas, or rule logic in any v3.0 file during this migration.
  All such content stays as `[content placeholder — to be filled in
  Claude session]`. Per `AGENTS.md`, content rewriting is substantive
  work and is out of scope here.
- DO NOT consolidate, paraphrase, or summarize v2.3 content into v3.0
  files in this pass. Only extract rule IDs.
- DO NOT initialize git if `.git/` already exists. If it doesn't exist,
  ASK before running `git init`.
- DO NOT create any v3.0 file not listed in the target directory
  structure above.

## Acceptance criteria — verify and report

When the mechanical migration is complete, output a report containing:

1. List of all directories created.
2. List of all files created, with byte counts.
3. Count of legacy rule IDs extracted per v2.3 source file.
4. Count of legacy anchors written per v3.0 destination file.
5. Parity check: legacy IDs extracted == legacy anchors written + IDs
   marked `DROPPED` in `INDEX.md`. Must match exactly.
6. `INDEX.md` migration table row count.
7. Verification that all files in `archive/v2.3/` are byte-identical
   to their pre-migration state.
8. Any STOP conditions hit or ambiguities encountered.

Then proceed through the full git workflow in `AGENTS.md` (issue, branch,
commit, validation, push, PR, auto-merge, issue close, cleanup).

## After this migration completes

This file's purpose ends when all `llm_runtime/` and `engineering_only/`
files have `status: active` in their frontmatter and the v3.0
content-rewrite sessions in Claude.ai are complete.

At that point:

1. Open an issue: "Archive MIGRATION_v2_to_v3.md — cutover complete."
2. Delete this file from the repo root, or move it to
   `archive/v2.3/MIGRATION_v2_to_v3.md` if a record is desired.
3. Add a `CHANGELOG.md` entry: "v3.0.0 — migration complete; v2.3
   archived; MIGRATION_v2_to_v3.md retired."

The cleanup confirms the migration is finished and prevents future
agents from following stale one-time guidance.
