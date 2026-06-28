# KapMan KB Index

## Repository structure

This repository separates runtime and engineering materials:
- llm_runtime/ files are uploaded to LLM project knowledge.
- engineering_only/ files are reference material for humans and engineering tools and are not uploaded to LLM projects.
- archive/ stores historical version snapshots and is read-only.

## Version status

- **Active line: v4.0 (in progress).** Opened 2026-06-26 per the KapMan System
  Integration Plan v1.0 (`docs/Kapman_System_Integration_Plan_v1.0.md`),
  Stage 1a. The substantive v4.0 content — new `JOURNAL_MGMT` runbook, WYCKOFF
  live-source tier gate, the §A1–A3 field contracts, the 4th (Calibration/Review)
  mode, and the memory/no-persist guardrail — is authored in **Stage 1b
  (human-in-the-loop)** and is not yet present. Until each runtime file is
  rewritten to v4.0 content, the live `llm_runtime/`+`engineering_only/` files
  remain at their `_v3.0` filenames and `kb_version` (filename bumps are coupled
  to the substantive per-file rewrites, not to this cutover).
- **Archived: v3.0** — frozen read-only snapshot at `archive/v3.0/`
  (`llm_runtime/` + `engineering_only/` split preserved), with a `v3.0` git tag
  at the cutover commit. The v3.0 inventory and v2.3→v3.0 migration tables below
  remain authoritative for both the archived snapshot and the still-live `_v3.0`
  working files.
- **v4.0 files authored so far (Stage 1b, in progress):**
  - `llm_runtime/JOURNAL_MGMT_v4.0.md` — new T2 runbook (journal persistence: memory
    load, lineage derivation, three-log write, no-persist boundary; `positions.md` record
    grammar added in #75; §A1 lineage degradation in #76; §A1 Wyckoff-vocabulary re-key of the
    `positions.md` grammar in #78 — `entry_wyckoff_phase` now holds the regime, lowercase ~27-event
    `entry_wyckoff_event`, `entry_phase`/`phase_c_confirmed` non-exempt riders). `kb_version 4.0.3`.
  - Substantive v4.0 content has also been added to `llm_runtime/KAPMAN_GUARDRAILS_v3.0.md`
    (memory-not-authority + numeric-no-persist guardrail; `kb_version 3.0.3`). It keeps its
    `_v3.0` filename pending the coordinated `_v3.0 → _v4.0` rename + cross-reference sweep
    at the end of Stage 1. New v4.0-era content uses **version-less cross-references**.
  - **Workflow 1 (viewer → Pass 1) ingest** (Stage 1b, Integration Plan §6/§A1/§A5):
    `WYCKOFF_v3.0.md` (`kb_version 3.0.4`) repoints the pipeline-reading source from the
    now-excised `kapman-mcp` surface to the live viewer/v2 (Polygon) source and adds the
    confidence **tier gate** (`τ_high`/`τ_low` on `min(regime_confidence, phase_confidence)`);
    `PASS1_SCREENING_v3.0.md` (`kb_version 3.0.6`) adds the viewer/v2 handoff candidate source
    and the §A1 ingest map (dual-path: paste now, tool later), preserving the Pass 1 → Pass 2
    Schwab-re-fetch boundary; `SYSTEM_PARAMS_v3.0.md` (`kb_version 3.0.2`) adds the provisional
    `TIER_GATE_TAU_HIGH` / `TIER_GATE_TAU_LOW` parameters. The `kapman-mcp` tool surface and
    name are fully excised from `llm_runtime/`. Files keep their `_v3.0` filenames pending the
    end-of-Stage-1 rename.
  - **Workflow 2 (trade log → Portfolio) §A2 ingest** (Stage 1b, Integration Plan §7/§A2/§A5):
    `PORTFOLIO_MGMT_v3.0.md` (`kb_version 3.0.2`) adds the tradelog `portfolio_snapshot` §A2 ingest
    (Step 1 → 1a ingest / 1b entry-context read), the Appendix §A2 source map, structure/direction
    derivation, MAE/MFE as advisory display only, re-points the position-context schema Source column
    (live fields → tradelog snapshot; the 6 entry-time regime + 8 SIGNAL alert rows → `positions.md`),
    and the absent/partial entry-context degradation; `PASS2_VALIDATION_v3.0.md` (`kb_version 3.0.1`)
    adds the at-validation capture of the entry-time snapshot + the eight SIGNAL levels + `option_mid`
    into `positions.md` (write-once, sole no-persist exemption). Join key `(instrument_key, account_id)`.
    `docs/Kapman_System_Integration_Plan_v1.0.md` §A2/§7 corrected to the real per-leg export fields
    (MAE/MFE = compute-on-export from `HistoricalMark`, advisory). Files keep their `_v3.0` filenames
    pending the end-of-Stage-1 rename.
  - **Session-layer wiring (KPSI)** (Stage 1b, Integration Plan §10/§A5): `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md`
    (`kb_version 3.0.3 → 3.0.4`) adds `JOURNAL_MGMT_v4.0.md` to the KB file inventory + tier model, expands the
    session entry sequence from five to seven steps (new step 2 session-start memory load + announce; new step 4
    lineage derivation + handoff staging on paste), reconciles position-context load with the §A2 export +
    `positions.md`, extends **Rule 7** with the log-manifest check, and reserves a 4th (Calibration/Review) mode
    for Stage 3 (not active — no-dangling-capability). Closes the session-wiring blockers the Stage-1 pilot
    dry-run surfaced (the §A1/§A2 ingest logic + `(instrument_key, account_id)` bridge themselves validated).
    File keeps its `_v3.0` filename pending the end-of-Stage-1 rename.
  - **§A2/journal contract-hardening** (Stage 1b, Integration Plan §A2; pilot-surfaced):
    `PORTFOLIO_MGMT_v3.0.md` (`kb_version 3.0.2 → 3.0.3`) adds §A2 structure/direction derivation
    rules (debit/credit by summed `cost_basis` sign; LEAP by original DTE ≥ `LEAP_DTE_BAND` floor;
    standalone `short_put` → CSP) and a matched-but-partial entry-context condition (per-field regime /
    per-alert SIGNAL degradation) plus the `option_mid`-vs-`entry_price` distinction; `JOURNAL_MGMT_v4.0.md`
    (`kb_version 4.0.0 → 4.0.1`) adds a canonical `positions.md` record grammar (named
    `(instrument_key, account_id)` join key, write-once entry snapshot vs live-refresh split, Wyckoff field
    constrained to the four named phases) and aligns the live-field label to `net_qty`. Files keep their
    existing filenames.
  - **§A1 ingest hardening** (Stage 1b, Integration Plan §A1; pilot-surfaced): `PASS1_SCREENING_v3.0.md`
    (`kb_version 3.0.6 → 3.0.7`) rewords the dangling dealer/vol cross-check map note to informational (already
    priced into `regime_confidence`) and adds a §A1 required-field contract + per-field degradation
    (`exported_at`/`as_of`/`row_count`/force-flags; earnings clarified KB-side, not a handoff field);
    `WYCKOFF_v3.0.md` (`kb_version 3.0.4 → 3.0.5`) adds a force-flag-input-completeness rule — an absent
    `weekly_agrees`/`structure_conflict` downgrades a would-be `pipeline-accepted` reading to `pipeline-flagged`
    ("force-flags unevaluated") rather than silently auto-accepting; `JOURNAL_MGMT_v4.0.md`
    (`kb_version 4.0.1 → 4.0.2`) adds the missing-`exported_at` lineage degradation. The Integration Plan §A1
    mirrors the cross-check rewording. Files keep their existing filenames.
  - **§12 PASS2 hygiene** (Stage 1b, Integration Plan §12): `PASS2_VALIDATION_v3.0.md` (`kb_version 3.0.1 → 3.0.2`)
    adds a heuristic that viewer/v2 outputs (`pt_*`/calibration, IV/flip, dealer reads) are Pass-1 context, not
    Pass-2 truth — Pass 2 re-derives the entry-price range, exit anchors, IV/flip, and chain-quality from the live
    Schwab chain it fetches itself. The §12 "align chain-quality gate" item resolved to a no-op (the viewer emits
    no `volatility_chain_truncated` flag — audited 2026-06-27). File keeps its `_v3.0` filename.
  - **§A1 Wyckoff-vocabulary reconciliation** (Stage 1b, Integration Plan §A1; pilot-found, IN PROGRESS): aligns the
    KB §A1 layer to the viewer's canonical regime(7)/phase(A–E)/event(~27) glossary (operator-supplied 2026-06-27).
    Design D1–D4 approved (two-axis regime+phase model; lowercase event vocab). **P1 done** — `WYCKOFF_v3.0.md`
    (`kb_version 3.0.5 → 3.0.6`) re-keys the `weekly_agrees`/`structure_conflict` hard force-flags from boolean to the
    real string value `"conflict"` (they previously could never fire against live data). **P2 + P3 done** (Stage B,
    WYCKOFF core) — `WYCKOFF_v3.0.md` (`kb_version 3.0.6 → 3.0.7`) embeds the viewer/v2 glossary **verbatim** as the
    canonical regime(7)/phase(A–E)/event(~27) vocabulary (Appendix), replaces the four-phase cycle with a regime
    decision-layer + succession **graph** (`reaccumulation`/`redistribution` as continuation branches), re-keys the
    Principle, validity gate, event-to-regime priority table, event reading guide, structural levels, and
    propose-confirm examples to the lowercase vocabulary (`AR_TOP`→`ar_dist`), and marks the legacy anchors historical
    (preserved verbatim). **Stage C (consumers) — SIGNAL done** — `SIGNAL_v3.0.md` (`kb_version 3.0.2 → 3.0.3`) +
    `PASS2_VALIDATION_v3.0.md` (`kb_version 3.0.2 → 3.0.3`): re-keys the Wyckoff veto, dealer-timing veto, directional
    fallback, regime exit advisory, and all propagation tables to the regime model, makes the veto layer
    **direction-aware/symmetric** (long puts get a first-class bearish path mirroring long calls — operator-approved),
    fixes the `utad` phase-E→phase-C error, resolves the `lps`/`lpsy` side-awareness, and adds a **forward-tested-target
    confluence annotation** to the exit triggers (the viewer `pt_*`/`*_prob` rides as a confidence annotation on the
    structural+validated level, never as the broker price; matching PASS2 §12 carry refinement). **Stage C — RISK
    done** — `RISK_v3.0.md` (`kb_version 3.0.0 → 3.0.1`): re-keys the sizing bands to the 7-regime model and makes
    them **direction-relative/symmetric** (a long put in `markdown` earns the upper band, mirroring a long call in
    `markup`) — trend & post-phase-C continuation → upper; post-phase-C base → conditional-top; pre-phase-C →
    conditional floor (default-refused by the SIGNAL veto, override-only, resolving a prior SIGNAL↔RISK tension);
    non-aligned/`ranging_undefined`/`UNKNOWN` → closed; v2.3 magnitudes preserved; near-flip ladder + dealer-narrowing
    made direction-aware; RISK_005 preserved verbatim. **Stage C — PORTFOLIO done** — `PORTFOLIO_MGMT_v3.0.md`
    (`kb_version 3.0.3 → 3.0.4`): re-keys the Regime exit advisory's Wyckoff branch to the **regime succession graph
    + phase regression (D→B/A)**, direction-relative (mirrors SIGNAL's committed advisory), with the phase-regression
    sub-branch consuming the entry-phase (A–E) **rider** (per D-d: regime is the exempt field, phase A–E is a non-exempt
    rider that degrades to data-absent when missing). **Stage D — PASS1 done** — `PASS1_SCREENING_v3.0.md`
    (`kb_version 3.0.7 → 3.0.8`): re-keys the screening body logic to the direction-aware model — hostile-macro prose
    scoped to **bullish** long-premium (puts the aligned redirect), direction resolution made **regime-natural +
    symmetric** (accumulation-family/`markup` → BULLISH; distribution-family/`markdown` → BEARISH; `sos`/`sow`
    fallback) and established **before** the direction-aware veto, Wyckoff-status/degraded-tables/workflow rows
    re-keyed to regime+phase. Behavioral completion: a confirmed bearish regime now yields an **Eligible** long put
    (was NO_TRADE+redirect). §A1 ingest map already new-vocab (untouched). **Stage D — JOURNAL_MGMT done** —
    `JOURNAL_MGMT_v4.0.md` (`kb_version 4.0.2 → 4.0.3`): re-keys the `positions.md` record grammar to the two-axis
    model — the load-bearing exempt field `entry_wyckoff_phase` now **holds the regime** (one of the 7 lowercase
    regimes, per D-d) rather than the old four Title-case phases; `entry_wyckoff_event` re-keyed to the lowercase
    ~27-event canonical vocab; **adds two non-exempt riders** `entry_phase` (A–E; the rider PORTFOLIO's phase-regression
    sub-branch consumes) and `phase_c_confirmed` (records the post-/pre-phase-C sizing gate; reserved entry context, no
    current reader — framed like the reserved `attack_flags[]`/`invalidation_conditions[]`). Exempt snapshot stays
    **exactly 5 regime fields + 8 SIGNAL levels**; the three riders sit outside it (categorical/boolean, not numeric
    regime reads, so the no-persist prohibition never reached them). PASS2 line 94 + GUARDRAILS line 46 still say "entry
    Wyckoff phase" — tracked to converge in their own slices. **Stage D/E — DEALER done** — `DEALER_v3.0.md`
    (`kb_version 3.0.0 → 3.0.1`): defines the **per-ticker bearish-mirror DGPI band** (`DGPI ≥ +50` with spot well above
    the ticker's flip — the exact sign-flipped mirror of the bullish per-ticker hostile band ≤ −50/well-below; magnitudes
    preserved, sign read direction-relative) that SIGNAL's dealer-timing veto and RISK's dealer-narrowing reference;
    adds a "dealer regime is read relative to the position's direction" heuristic + Appendix paragraph; **bullish-scopes**
    the macro hostile-macro refusal everywhere (Principle, heuristic, Appendix composite, outputs-table flag row, vocab
    row, rendered report-label) — long puts are the aligned redirect, matching committed SIGNAL/GUARDRAILS; **no** macro
    "supportive-macro refuses puts" mirror (no consumer → would dangle; the bearish mirror is ticker-layer only). Walls +
    GEX-slope left long-framed (SIGNAL owns wall-side direction-relativity). Legacy DEALER_001–014 untouched. **Stage D/E —
    WYCKOFF done** — `WYCKOFF_v3.0.md` (`kb_version 3.0.7 → 3.0.8`): adds an explicit **bearish-mirror block** beneath the
    long-framed decision-layer table (markup↔markdown / reaccumulation↔redistribution trend+continuation → upper;
    accumulation↔distribution gated-base → conditional floor pre-C → conditional-top post-C; refusal sets mirror;
    ranging_undefined/UNKNOWN refuse both; phase-C `spring`/`shakeout`↔`utad`, entry `lps`↔`lpsy`); normalizes the two
    naming stragglers (`conditional range`/`top-of-conditional` → **`conditional-top`**, RISK's committed name); adds a
    **projected-markdown-target** structural row (downside analog of the projected-markup target, the Ice-level projection
    SIGNAL references for long-put exits); adds a **`utad` downstream-routing row** (bearish phase-C mirror of the `spring`
    row); makes the line-182 RISK + line-183 DEALER downstream rows direction-relative. Canonical-vocabulary glossary +
    legacy WYCKOFF_PHASE_*/EVENT_* anchors untouched (D-e). Known-but-deferred: WYCKOFF↔RISK UNKNOWN wording (lines 20/143
    "conditional floor" vs RISK "band closed" — converges behaviorally). **Stage E — SIGNAL "floor"→"conditional floor"
    done** — `SIGNAL_v3.0.md` (`kb_version 3.0.3 → 3.0.4`): the committed band-ladder sentence's bare pre-phase-C "floor"
    tightened to **"conditional floor"** (faithful no-judgment re-key disambiguating it from RISK's "band closed", now that
    RISK has two floors). **Stage D/E — GUARDRAILS done** — `KAPMAN_GUARDRAILS_v3.0.md` (`kb_version 3.0.3 → 3.0.4`):
    reconciles the T0 prose with its own already-direction-aware eligible-set table + committed DEALER/SIGNAL — hostile-macro
    refusal scoped to **bullish** long-premium (long calls / call debit spreads) with long puts / put debit spreads surfaced
    as the directionally-aligned redirect (Principle, macro-default heuristic, Appendix eligible-set intro); line-46 exempt
    field "entry Wyckoff phase" → "entry Wyckoff **regime**" (D-d; exempt set stays exactly 5 regime fields + 8 SIGNAL
    levels — label change, not count); line-158 DEALER-freshness (DEALER 3.0.1 rewrite landed, magnitude preserved). The
    eligible-set table + VALIDATION_001 anchor untouched. **Stage E — REPORT_FORMAT done** — `REPORT_FORMAT_v3.0.md`
    (`kb_version 3.0.8 → 3.0.9`): renders the SIGNAL forward-tested-target **confluence suffix** (*"…— viewer forward-tested
    hit-rate ~Z%, as-of [date]"*) on the screening **Exit plan** subsection + the portfolio **Exit-trigger proximity**
    subsection + the SIGNAL cross-ref row — a suffix on the underlying alert level, **never** the alert price (structural+
    validated level stays the order; anti-hallucination floor intact). Faithful rendering of committed SIGNAL output;
    compact columns + self-audit completeness rows correctly untouched. **Stage E — SYSTEM_PARAMS (+ RISK/SIGNAL/
    REPORT_FORMAT wiring) done** — a coordinated 4-file slice adds two operator-set params to `SYSTEM_PARAMS_v3.0.md`
    (`3.0.2 → 3.0.3`): `FORWARD_TEST_CONFLUENCE_BAND_PCT` = **0.5** (±% of spot, provisional/pilot-calibrated; the
    near-coincidence tolerance for the forward-tested-target confluence annotation) and `CONDITIONAL_TOP_SIZE_PCT` = **1.0**
    (% of denominator; promotes the conditional-top magnitude / JD1 from a RISK reference point to a named tunable). `RISK`
    (`3.0.1 → 3.0.2`) cites `CONDITIONAL_TOP_SIZE_PCT` by name (other v2.3 band magnitudes stay reference points); `SIGNAL`
    (`3.0.4 → 3.0.5`) + `REPORT_FORMAT` (`3.0.9 → 3.0.10`) resolve their "a SYSTEM_PARAMS follow-up" placeholders to the
    named confluence param ("consumed by name" satisfied). **Stage D — PASS2 done** — `PASS2_VALIDATION_v3.0.md`
    (`kb_version 3.0.3 → 3.0.4`): the entry-time-snapshot capture heuristic re-keyed "entry Wyckoff **phase**" → "entry
    Wyckoff **regime**" (matching JOURNAL/PORTFOLIO/GUARDRAILS) and now names the best-effort non-exempt riders (entry
    phase A–E, `phase_c_confirmed`, `entry_wyckoff_event`) captured alongside; the exempt set stays exactly 5 regime fields
    + 8 SIGNAL levels (riders + `option_mid` explicitly outside the exemption). **Stage E — P4 + UNKNOWN-wording done** —
    `PASS1_SCREENING_v3.0.md` (`3.0.8 → 3.0.9`): adds a §A1-ingest clarification that the viewer's Pass-1 `dealer_confidence`
    (high/med/low/invalid) is a **separate layer** from the Schwab Pass-2 dealer-status `FULL/LIMITED/INVALID` (D-c — two
    layers, not conflated), and maps the coarse `position_vs_flip` (above/below/at_flip/unknown) onto DEALER's flip-zone
    with the precise Well-above/Near-flip/Well-below being a Pass-2 determination (faithful clarification — no new behavioral
    rule, per the verify catch). `WYCKOFF_v3.0.md` (`3.0.8 → 3.0.9`): the two UNKNOWN/unconfirmed degradation sites
    (lines 20/143) re-keyed from "sizing band ceiling closes to the **conditional floor**" → "the long-premium sizing band
    **closes entirely**" (aligns to RISK's UNKNOWN→band-closed + WYCKOFF's own "most conservative case"; the conditional
    floor is the distinct pre-phase-C override-only band). **All #78 consumer/parameter slices are now done; only Stage F
    closeout remains** (structural validate + golden/BEARISH pilot + completeness critic + estimation-path regression +
    `_v3.0 → _v4.0` rename sweep) — **blocked on the operator-produced BEARISH viewer fixture**.

- **Dealer-contract reconciliation (2026-06-28; a Stage-F-audit finding, separate from #78).** A code-grounded review found
  the KB's DEALER/VOLATILITY contracts asserted Schwab fields that did not exist (the "kapman-mcp lesson"). The operator
  fixed the **kapman-schwab-MCP** producer to match kapman-polygon-mcp-v2 (signed DGPI [-100,100], `position`
  long_gamma/short_gamma/neutral, separate `position_vs_flip`, `confidence`), deployed + smoke-tested. The KB-side re-key
  (this slice) landed atomically across **11 files**: `SYSTEM_PARAMS_v3.0.md` (3.0.3 → 3.0.4 — adds `DGPI_NEUTRAL_BAND=10`,
  `DGPI_STRONG_BAND=30`, `HOSTILE_MACRO_DGPI_MAX=-30`; `NEAR_FLIP_BAND_PCT 0.25 → 0.5`), `DEALER_v3.0.md` (3.0.1 → 3.0.2 —
  anchor: signed DGPI tiers re-keyed `20/50 → 10/30/60`, the fictional `FULL/LIMITED/INVALID` dealer-status replaced by the
  emitted `confidence` contract [high/med → full, low → floor, invalid → drop], `position`/`position_vs_flip` split, near-flip
  0.5%, Pass-1↔Pass-2 agrees by tier/direction not value, legacy-anchor historical note), and the consumer cascade
  `SIGNAL_v3.0.md` (3.0.5 → 3.0.6), `RISK_v3.0.md` (3.0.2 → 3.0.3), `PASS2_VALIDATION_v3.0.md` (3.0.4 → 3.0.5),
  `PASS1_SCREENING_v3.0.md` (3.0.9 → 3.0.10 — incl. the P4-paragraph correction: Schwab now emits `confidence`, so the
  Pass-1/Pass-2 distinction is provenance, not vocabulary), `PORTFOLIO_MGMT_v3.0.md` (3.0.4 → 3.0.5), `KAPMAN_GUARDRAILS_v3.0.md`
  (3.0.4 → 3.0.5 — hostile `≤ -30`, false-provenance claim fixed), `REPORT_FORMAT_v3.0.md` (3.0.10 → 3.0.11),
  `REPORT_STYLE_v3.0.md` (3.0.4 → 3.0.5), `REPORT_TEMPLATE_PASS1_v3.0.html` (degradation-flag label). The overloaded
  **volatility-status** `FULL/LIMITED/INVALID` (P0-2, still open) and **chain-quality** `Full/Limited/Weak` (P0-3a) were
  deliberately left untouched. Behavior change: a ticker formerly floored under "medium-confidence" is now promoted to full
  (high/medium both = trusted). Still open after this: P0-2 (volatility contract), P0-3a, P0-4, P0-5, P1-10, P1-11.
- **Volatility-contract reconciliation — IV/HV spread-mandate re-keyed to the live Polygon `iv_hv_ratio` producer (2026-06-28).**
  Same class as the dealer fix (KB asserted IV fields the producer didn't emit): the KB routed the Pass-2 spread-mandate IV/HV to a
  Schwab ATM source that doesn't exist, and treated vol-status `FULL/LIMITED/INVALID` as a delivered label. **Producer fixed +
  deployed** (kapman-polygon-mcp-v2 `get_options_metrics` now emits an ATM-anchored `atm_iv` [~30-DTE interp, band-avg fallback],
  `iv_hv_ratio` [`atm_iv` ÷ HV20], `iv_hv_status`, `iv_hv_methodology`; verified live across 30 names). KB re-key (Option B + B2):
  both passes source the IV/HV from the Polygon producer, Pass 2 **re-confirms on a fresh fetch** (no Schwab ATM); vol-status
  `FULL/LIMITED/INVALID` is now **KB-derived** from `iv_hv_status` + freshness (`ATM_FALLBACK_BAND` → LIMITED). Landed across
  **4 files**: `VOLATILITY_v3.0.md` (3.0.0 → 3.0.1, anchor), `SIGNAL_v3.0.md` (3.0.6 → 3.0.7), `PASS1_SCREENING_v3.0.md`
  (3.0.10 → 3.0.11), `PASS2_VALIDATION_v3.0.md` (3.0.5 → 3.0.6). Threshold held at 1.20/0.95 (provisional, pending a multi-day
  panel). **Deferred (tracked):** the IV-rank/percentile/dispersion dormancy honesty pass — existing `insufficient_iv_history`
  null-handling keeps it pilot-safe — and an absolute-IV guard for the ratio's low-absolute-IV blind spot (both await the phase-2
  IV-history producer). Closes the IV/HV + vol-status halves of P0-2.

## v3.0 file directory

| path | tier | doc_type | role |
|---|---|---|---|
| llm_runtime/KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md | T0 | orientation | Top-level project system instructions |
| llm_runtime/KAPMAN_GUARDRAILS_v3.0.md | T0 | principle | Guardrail principles |
| llm_runtime/WYCKOFF_v3.0.md | T1 | principle | Wyckoff domain principles |
| llm_runtime/DEALER_v3.0.md | T1 | principle | Dealer positioning principles |
| llm_runtime/VOLATILITY_v3.0.md | T1 | principle | Volatility regime principles |
| llm_runtime/RISK_v3.0.md | T1 | principle | Risk management principles |
| llm_runtime/SIGNAL_v3.0.md | T1 | principle | Signal entry/exit principles |
| llm_runtime/PASS1_SCREENING_v3.0.md | T2 | runbook | Pass 1 screening workflow |
| llm_runtime/PASS2_VALIDATION_v3.0.md | T2 | runbook | Pass 2 validation workflow |
| llm_runtime/PORTFOLIO_MGMT_v3.0.md | T2 | runbook | Portfolio management workflow |
| llm_runtime/REPORT_STYLE_v3.0.md | T3 | style | Report style guidance |
| llm_runtime/REPORT_TEMPLATE_PASS1_v3.0.html | T3 | template | Canonical HTML skeleton for Pass 1 screening report; column structure, section order, legend/footer pre-built per REPORT_FORMAT and REPORT_STYLE; consumed by Runtime Rule 6 at render time |
| llm_runtime/REPORT_FORMAT_v3.0.md | T3 | format | Report format guidance |
| llm_runtime/SIC_SECTOR_MAP_v3.0.md | T3 | reference | SIC to sector map reference |
| llm_runtime/SYSTEM_PARAMS_v3.0.md | T3 | reference | Operator-configurable parameter reference; includes `DTE_DECAY_WARNING_THRESHOLD` (21 days) |
| engineering_only/BACKEND_PIPELINE_v3.0.md | T4 | reference | Backend pipeline reference |
| engineering_only/TOOL_SURFACE_v3.0.md | T4 | reference | Tool-surface reference |
| engineering_only/DEALER_PIPELINE_v3.0.md | — | reference | Dealer pipeline formulas and parameters |
| engineering_only/PASS1_MCP_REFERENCE_v3.0.md | — | reference | Pass 1 MCP endpoint and scoring reference |
| engineering_only/PASS2_MCP_REFERENCE_v3.0.md | — | reference | Pass 2 MCP chain-validation reference |
| engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | — | reference | SIGNAL persistence and fallback reference |
| engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | — | reference | Volatility MCP formulas and source-authority reference |
| engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | — | reference | Wyckoff MCP detection and scoring reference |
| engineering_only/PORTFOLIO_MGMT_MCP_REFERENCE_v3.0.md | — | reference | Portfolio-management MCP and persistence reference |
| engineering_only/PIPELINE_FEED_VIEW_SPEC_v3.0.md | — | reference | Viewer "Export -" pipeline-feed view column-set contract; tracks the canonical ATM IV / IV-HV surfacing and the §A1 ingest-map reconciliation |

### Current file inventory table

| File | Tier | Status | Session |
|---|---|---|---|
| `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md` | T0 | active | 12 |
| `REPORT_STYLE_v3.0.md` | T3 | active | 11 |
| `SIC_SECTOR_MAP_v3.0.md` | T3 | active | 13 |
| `engineering_only/DEALER_PIPELINE_v3.0.md` | — | draft | 15 |
| `engineering_only/PASS1_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/PASS2_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/PORTFOLIO_MGMT_MCP_REFERENCE_v3.0.md` | — | draft | 15 |
| `engineering_only/PIPELINE_FEED_VIEW_SPEC_v3.0.md` | — | active | 16 |

### v3.0.1 patch file version/status

| File | kb_version | status |
|---|---|---|
| SYSTEM_PARAMS_v3.0.md | 3.0.4 | active |
| SIGNAL_v3.0.md | 3.0.7 | active |
| PASS1_SCREENING_v3.0.md | 3.0.12 | active |
| WYCKOFF_v3.0.md | 3.0.9 | active |
| PORTFOLIO_MGMT_v3.0.md | 3.0.5 | active |
| PASS2_VALIDATION_v3.0.md | 3.0.6 | active |
| VOLATILITY_v3.0.md | 3.0.1 | active |
| RISK_v3.0.md | 3.0.3 | active |
| DEALER_v3.0.md | 3.0.2 | active |
| KAPMAN_GUARDRAILS_v3.0.md | 3.0.5 | active |
| REPORT_FORMAT_v3.0.md | 3.0.11 | active |
| REPORT_STYLE_v3.0.md | 3.0.5 | active |
| KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md | 3.0.4 | active |

### v3.0.1 report metadata patch

| File | kb_version | file_last_updated |
|---|---|---|
| REPORT_TEMPLATE_PASS1_v3.0.html | 3.0.5 | 2026-05-14 |
| KAPMAN_GUARDRAILS_v3.0.md | 3.0.5 | 2026-06-28 |
| REPORT_STYLE_v3.0.md | 3.0.5 | 2026-06-28 |
| WYCKOFF_v3.0.md | 3.0.9 | 2026-06-28 |
| SIGNAL_v3.0.md | 3.0.7 | 2026-06-28 |
| PASS1_SCREENING_v3.0.md | 3.0.11 | 2026-06-28 |
| PORTFOLIO_MGMT_v3.0.md | 3.0.5 | 2026-06-28 |
| PASS2_VALIDATION_v3.0.md | 3.0.6 | 2026-06-28 |
| VOLATILITY_v3.0.md | 3.0.1 | 2026-06-28 |
| RISK_v3.0.md | 3.0.3 | 2026-06-28 |
| DEALER_v3.0.md | 3.0.2 | 2026-06-28 |
| REPORT_FORMAT_v3.0.md | 3.0.11 | 2026-06-28 |
| SYSTEM_PARAMS_v3.0.md | 3.0.4 | 2026-06-28 |
| KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md | 3.0.4 | 2026-06-27 |

### Session 14 llm_runtime inventory verification

| File | Tier | doc_type | Status |
|---|---|---|---|
| `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v3.0.md` | T0 | orientation | active |
| `KAPMAN_GUARDRAILS_v3.0.md` | T0 | principle | active |
| `DEALER_v3.0.md` | T1 | principle | active |
| `RISK_v3.0.md` | T1 | principle | active |
| `SIGNAL_v3.0.md` | T1 | principle | active |
| `VOLATILITY_v3.0.md` | T1 | principle | active |
| `WYCKOFF_v3.0.md` | T1 | principle | active |
| `PASS1_SCREENING_v3.0.md` | T2 | runbook | active |
| `PASS2_VALIDATION_v3.0.md` | T2 | runbook | active |
| `PORTFOLIO_MGMT_v3.0.md` | T2 | runbook | active |
| `REPORT_FORMAT_v3.0.md` | T3 | format | active |
| `REPORT_STYLE_v3.0.md` | T3 | style | active |
| `SYSTEM_PARAMS_v3.0.md` | T3 | reference | active |
| `SIC_SECTOR_MAP_v3.0.md` | T3 | reference | active |

## v2.3 -> v3.0 rule-ID migration table

| Legacy ID | v3.0 destination file | Anchor name | Status |
|---|---|---|---|
| WYCKOFF_PHASE_001 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — minimum history guard | WYCKOFF_PHASE_001 | MIGRATED |
| WYCKOFF_PHASE_002 | llm_runtime/WYCKOFF_v3.0.md § Principle — phase vocabulary (Accumulation) | WYCKOFF_PHASE_002 | MIGRATED |
| WYCKOFF_PHASE_003 | llm_runtime/WYCKOFF_v3.0.md § Principle — phase vocabulary (Markup) | WYCKOFF_PHASE_003 | MIGRATED |
| WYCKOFF_PHASE_004 | llm_runtime/WYCKOFF_v3.0.md § Principle — phase vocabulary (Distribution) | WYCKOFF_PHASE_004 | MIGRATED |
| WYCKOFF_PHASE_005 | llm_runtime/WYCKOFF_v3.0.md § Principle — phase vocabulary (Markdown) | WYCKOFF_PHASE_005 | MIGRATED |
| WYCKOFF_PHASE_006 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — Markdown requires SOW | WYCKOFF_PHASE_006 | MIGRATED |
| WYCKOFF_PHASE_007 | engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_PHASE_007 | MIGRATED |
| WYCKOFF_PHASE_008 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — priority order | WYCKOFF_PHASE_008 | MIGRATED |
| WYCKOFF_PHASE_009 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics; engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_PHASE_009 | MIGRATED |
| WYCKOFF_PHASE_010 | llm_runtime/WYCKOFF_v3.0.md § Principle + § Operational heuristics — UNKNOWN state | WYCKOFF_PHASE_010 | MIGRATED |
| WYCKOFF_PHASE_011 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — phase succession duration | WYCKOFF_PHASE_011 | MIGRATED |
| WYCKOFF_PHASE_012 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — SOS/SOW sequence eligibility | WYCKOFF_PHASE_012 | MIGRATED |
| WYCKOFF_PHASE_013 | engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_PHASE_013 | MIGRATED |
| WYCKOFF_EVENT_001 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — minimum history guard | WYCKOFF_EVENT_001 | MIGRATED |
| WYCKOFF_EVENT_002 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (SC) | WYCKOFF_EVENT_002 | MIGRATED |
| WYCKOFF_EVENT_003 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (SC prior trend) | WYCKOFF_EVENT_003 | MIGRATED |
| WYCKOFF_EVENT_004 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (BC) | WYCKOFF_EVENT_004 | MIGRATED |
| WYCKOFF_EVENT_005 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (BC prior trend) | WYCKOFF_EVENT_005 | MIGRATED |
| WYCKOFF_EVENT_006 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (AR) | WYCKOFF_EVENT_006 | MIGRATED |
| WYCKOFF_EVENT_007 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (AR_TOP) | WYCKOFF_EVENT_007 | MIGRATED |
| WYCKOFF_EVENT_008 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (Spring) | WYCKOFF_EVENT_008 | MIGRATED |
| WYCKOFF_EVENT_009 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (UT) | WYCKOFF_EVENT_009 | MIGRATED |
| WYCKOFF_EVENT_010 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (SOS) | WYCKOFF_EVENT_010 | MIGRATED |
| WYCKOFF_EVENT_011 | llm_runtime/WYCKOFF_v3.0.md § Appendix — event reading guide (SOW) | WYCKOFF_EVENT_011 | MIGRATED |
| WYCKOFF_EVENT_012 | engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_EVENT_012 | MIGRATED |
| WYCKOFF_EVENT_013 | llm_runtime/WYCKOFF_v3.0.md § Operational heuristics — ST not delivered | WYCKOFF_EVENT_013 | MIGRATED |
| DEALER_001 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_001 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_002 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_002 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_003 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_003 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_004 | llm_runtime/DEALER_v3.0.md § Operational heuristics; engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_004 | Runtime interpretation retained in DEALER principle; pipeline computation details moved to engineering-only spec. |
| DEALER_005 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_005 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_006 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_006 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_007 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_007 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_008 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_008 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_009 | llm_runtime/DEALER_v3.0.md § Principle, § Operational heuristics, § Appendix; engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_009 | Runtime semantics retained in DEALER principle and appendix; pipeline computation details moved to engineering-only spec. |
| DEALER_010 | llm_runtime/DEALER_v3.0.md § Operational heuristics, § Appendix; engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_010 | Runtime semantics retained in DEALER principle and appendix; pipeline computation details moved to engineering-only spec. |
| DEALER_011 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_011 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_012 | llm_runtime/DEALER_v3.0.md § Operational heuristics; engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_012 | Runtime interpretation retained in DEALER principle; pipeline computation details moved to engineering-only spec. |
| DEALER_013 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_013 | Migrated to engineering-only pipeline spec (formula and computation details). |
| DEALER_014 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_014 | Migrated to engineering-only pipeline spec (formula and computation details). |
| VOLATILITY_001 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_001 | MIGRATED |
| VOLATILITY_002 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_002 | MIGRATED |
| VOLATILITY_003 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_003 | MIGRATED |
| VOLATILITY_004 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_004 | MIGRATED |
| VOLATILITY_005 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_005 | MIGRATED |
| VOLATILITY_006 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_006 | MIGRATED |
| VOLATILITY_007 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_007 | MIGRATED |
| VOLATILITY_008 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_008 | MIGRATED |
| VOLATILITY_009 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_009 | MIGRATED |
| VOLATILITY_010 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_010 | MIGRATED |
| VOLATILITY_011 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics and Appendix; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_011 | MIGRATED |
| VOLATILITY_012 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_012 | MIGRATED |
| VOLATILITY_013 | llm_runtime/VOLATILITY_v3.0.md § Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_013 | MIGRATED |
| VOLATILITY_014 | engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_014 | MIGRATED |
| VOLATILITY_015 | llm_runtime/VOLATILITY_v3.0.md § Principle and Operational heuristics; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_015 | MIGRATED |
| RISK_005 | llm_runtime/RISK_v3.0.md | RISK_005 | PENDING REWRITE |
| POSITION_SIZING_001 | RISK_v3.0.md § Principle and § Operational heuristics | Superseded by band-based judgment model; v2.3 sizing ladder preserved as reference in Appendix |
| RISK_001 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_001 | PENDING REWRITE |
| RISK_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_002 | PENDING REWRITE |
| RISK_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_003 | PENDING REWRITE |
| RISK_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | RISK_004 | PENDING REWRITE |
| SIGNAL_005 | llm_runtime/SIGNAL_v3.0.md § Operational heuristics; engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_005 | MIGRATED |
| SIGNAL_006 | llm_runtime/SIGNAL_v3.0.md § Operational heuristics; engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_006 | MIGRATED |
| SIGNAL_007 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_007 | PENDING REWRITE |
| SIGNAL_008 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_008 | PENDING REWRITE |
| SIGNAL_009 | llm_runtime/SIGNAL_v3.0.md § Operational heuristics; engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_009 | MIGRATED |
| SIGNAL_010 | llm_runtime/SIGNAL_v3.0.md | SIGNAL_010 | PENDING REWRITE |
| SIGNAL_001 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_001 | MIGRATED |
| SIGNAL_002 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_002 | MIGRATED |
| SIGNAL_003 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_003 | MIGRATED |
| SIGNAL_004 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_004 | MIGRATED |
| VALIDATION_001 | llm_runtime/KAPMAN_GUARDRAILS_v3.0.md | VALIDATION_001 | PENDING REWRITE |
| VALIDATION_001 (PASS2 residue) | PASS2_VALIDATION_v3.0.md § Legacy anchors; engineering_only/PASS2_MCP_REFERENCE_v3.0.md | Active — anti-hallucination floor narrowing at Pass 2; persistence-boundary controls in engineering-only |
| VALIDATION_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_002 | PENDING REWRITE |
| VALIDATION_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_003 | PENDING REWRITE |
| VALIDATION_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_004 | PENDING REWRITE |
| VALIDATION_005 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_005 | PENDING REWRITE |
| VALIDATION_006 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_006 | PENDING REWRITE |
| VALIDATION_007 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_007 | PENDING REWRITE |
| VALIDATION_008 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_008 | PENDING REWRITE |
| VALIDATION_009 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_009 | PENDING REWRITE |
| VALIDATION_010 | engineering_only/BACKEND_PIPELINE_v3.0.md | VALIDATION_010 | PENDING REWRITE |
| CONSTANTS_001 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_001 | PENDING REWRITE |
| CONSTANTS_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_002 | PENDING REWRITE |
| CONSTANTS_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_003 | PENDING REWRITE |
| CONSTANTS_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_004 | PENDING REWRITE |
| CONSTANTS_005 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_005 | PENDING REWRITE |
| CONSTANTS_006 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_006 | PENDING REWRITE |
| CONSTANTS_007 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_007 | PENDING REWRITE |
| CONSTANTS_008 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_008 | PENDING REWRITE |
| CONSTANTS_009 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_009 | PENDING REWRITE |
| CONSTANTS_010 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_010 | PENDING REWRITE |
| CONSTANTS_011 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_011 | PENDING REWRITE |
| CONSTANTS_012 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_012 | PENDING REWRITE |
| CONSTANTS_013 | engineering_only/BACKEND_PIPELINE_v3.0.md | CONSTANTS_013 | PENDING REWRITE |
| PIPELINE_001 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_001 | PENDING REWRITE |
| PIPELINE_002 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_002 | PENDING REWRITE |
| PIPELINE_003 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_003 | PENDING REWRITE |
| PIPELINE_004 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_004 | PENDING REWRITE |
| PIPELINE_005 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_005 | PENDING REWRITE |
| PIPELINE_006 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_006 | PENDING REWRITE |
| PIPELINE_007 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_007 | PENDING REWRITE |
| PIPELINE_008 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_008 | PENDING REWRITE |
| PIPELINE_009 | engineering_only/BACKEND_PIPELINE_v3.0.md | PIPELINE_009 | PENDING REWRITE |
| PIPELINE_010 | engineering_only/PASS1_MCP_REFERENCE_v3.0.md — full endpoint inventory; runtime behavioral residue in llm_runtime/PASS1_SCREENING_v3.0.md § Operational heuristics ("The Pass 1 IV/HV read is the Polygon producer's iv_hv_ratio") | PIPELINE_010 | MIGRATED |
| PIPELINE_012 | PASS2_VALIDATION_v3.0.md § Legacy anchors; engineering_only/PASS2_MCP_REFERENCE_v3.0.md | PIPELINE_012 | MIGRATED |
| PIPELINE_011 | llm_runtime/PASS1_SCREENING_v3.0.md § Operational heuristics ("Pass 1 data does not carry forward as authoritative into Pass 2") | PIPELINE_011 | MIGRATED |
| PIPELINE_011 (mis-filing note) | PASS2_VALIDATION_v3.0.md § Legacy anchors | Mis-filing resolved; authoritative destination is PASS1 |
| SCORING_001 | engineering_only/PASS1_MCP_REFERENCE_v3.0.md — pass-through constraint and storage bounds; runtime: not referenced in any trigger evaluation | SCORING_001 | MIGRATED |

### Session 14 migration coverage verification rows

| Legacy ID | v3.0 destination file | Anchor name | Status |
|---|---|---|---|
| DEALER_001–DEALER_014 | engineering_only/DEALER_PIPELINE_v3.0.md | DEALER_001–DEALER_014 | VERIFIED |
| PIPELINE_010, SCORING_001 | engineering_only/PASS1_MCP_REFERENCE_v3.0.md | PIPELINE_010, SCORING_001 | VERIFIED |
| PIPELINE_011 | REPORT_FORMAT_v3.0.md § Operational heuristics — pass label discipline | PIPELINE_011 | VERIFIED |
| PIPELINE_012 | PASS2_VALIDATION_v3.0.md § Operational heuristics — truncation heuristic; engineering_only/PASS2_MCP_REFERENCE_v3.0.md | PIPELINE_012 | VERIFIED |
| VALIDATION_001 | KAPMAN_GUARDRAILS_v3.0.md § Operational heuristics; REPORT_FORMAT_v3.0.md § Operational heuristics | VALIDATION_001 | VERIFIED |
| RISK_005 | RISK_v3.0.md § Principle and § Operational heuristics | RISK_005 | VERIFIED |
| SIGNAL_001–SIGNAL_004 | engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_001–SIGNAL_004 | VERIFIED |
| SIGNAL_005 | SIGNAL_v3.0.md § Operational heuristics — anti-hallucination floor; computation to engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_005 | VERIFIED |
| SIGNAL_006 | SIGNAL_v3.0.md § Operational heuristics — NO_TRADE consistency | SIGNAL_006 | VERIFIED |
| SIGNAL_009 | SIGNAL_v3.0.md § Operational heuristics — fallback policy; engineering_only/SIGNAL_MCP_REFERENCE_v3.0.md | SIGNAL_009 | VERIFIED |
| VOLATILITY_001–VOLATILITY_015 | Per individual anchor entries in VOLATILITY_v3.0.md § Legacy anchors; engineering_only/VOLATILITY_MCP_REFERENCE_v3.0.md | VOLATILITY_001–VOLATILITY_015 | VERIFIED |
| WYCKOFF_PHASE_001–WYCKOFF_PHASE_013 | Per individual anchor entries in WYCKOFF_v3.0.md § Legacy anchors; engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_PHASE_001–WYCKOFF_PHASE_013 | VERIFIED |
| WYCKOFF_EVENT_002–WYCKOFF_EVENT_012 | Per individual anchor entries in WYCKOFF_v3.0.md § Legacy anchors; engineering_only/WYCKOFF_MCP_REFERENCE_v3.0.md | WYCKOFF_EVENT_002–WYCKOFF_EVENT_012 | VERIFIED |

### RISK v3.0 rewrite resolution (2026-05-10)

| Legacy ID | v3.0 destination | Status | Rationale |
|---|---|---|---|
| RISK_001 | — | DROPPED | C4 pipeline null-write observation; engineering-state, no LLM runtime effect |
| RISK_002 | — | DROPPED | AI base disclaimer implementation detail; not a risk principle |
| RISK_003 | — | DROPPED | Schema check-constraint absence; backend observation only |
| RISK_004 | — | DROPPED | C4 authority_constraints injection gap; backend reference, not LLM rule |
| RISK_005 | llm_runtime/RISK_v3.0.md § Legacy anchors | MIGRATED | Sizing ladder rewritten as judgment bands; percentages preserved in Appendix as reference points |
