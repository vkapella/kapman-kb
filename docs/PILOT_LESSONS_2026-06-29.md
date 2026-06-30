# Pilot Lessons Learned — 2026-06-28/29

Captured from the Stage-1 pilot runs (Integration Plan §13): four viewer Export
handoffs through Pass-1 (279 candidates), a Pass-2 mechanics dry-run (off-hours,
5 candidates), an RTH re-export through Pass-1, and a live RTH Pass-2 validation.
Journal lineage: `VS-20260629-0048-01..0049-04`, `VS-20260629-1348-05`,
`PASS2-20260629-mechanics-dryrun`, `PASS2-20260629-1352-live`.

This is the "feed lessons back into the KB" artifact. Items are tagged
**[KB]** (runtime contract change — HITL), **[ENG]** (engineering/MCP-reference or
viewer code), **[CAL]** (parameter calibration), or **[PROC]** (process/tooling).

---

## 1. What the pilot proved works

- **End-to-end spine is real.** Paste handoff → §A1 tier-gate → SIGNAL trigger
  sequence → eligible set → Pass-2 fresh re-fetch → drift surface → chain
  validation → trade spec → lineage-linked LOG 1/2/3. Every stage ran on real data.
- **Self-contained IV/HV (the #19/§A1 work) is validated end-to-end.** The
  spread-mandate fired off the viewer handoff's own `iv_hv_ratio` at Pass-1, and the
  Pass-2 Polygon re-fetch matched the handoff value to **< 1 %** on every name
  (BABA 1.601→1.608, NBIS 1.306→1.312, UNH 1.626→1.633). The loop is closed: the
  export carries the canonical mandate input; Pass-2 re-confirms identically.
- **Lineage logging works** — handoffs + pass1 + pass2 records land in
  `kapman-journal` with derived `VS-…`/`PASS2-…` IDs and parent links.

## 2. Calibration findings [CAL]

- **The τ paradox (highest-value finding).** Every fresh **phase-C spring** — the
  highest-conviction Wyckoff longs (HON, AMZN, GOOG/GOOGL, NVDA, EQIX, MRVL…) —
  scores `regime_confidence = 0.50`, so the tier gate (`τ_high = 0.70`) **flags**
  them. The auto-eligible set is *entirely* extended `markup_continuation` names.
  So τ routes the freshest, best-R/R setups to the operator exchange and
  auto-accepts the late ones. **Decision pending:** is this desired (fresh setups
  deserve operator eyes) or a τ/engine mis-set (the v2 engine assigns reaccumulation
  a flat 0.50)? Needs a multi-run pattern before moving `τ_high` or the engine's
  reaccumulation confidence.
- **`weekly_agrees = conflict` force-flags nearly all reaccumulation springs**
  (daily regime fresh, weekly not yet turned) — a *second* flag on top of the 0.50.
  The force-flag is doing heavy lifting; worth confirming it's intended.
- **`IV_HV_ELEVATED_THRESHOLD = 1.20` and `τ` are still provisional** (SYSTEM_PARAMS
  notes say so). The pilot gives the first real distribution to calibrate against.

## 3. Bugs and correctness [PROC]

- **Dealer-timing veto over-fired (fixed).** My Pass-1 screen script fired the
  bullish veto on `(DGPI ≤ −30 AND a flip level exists)` instead of the contract's
  `(DGPI ≤ −30 AND spot below its flip)`. It wrongly NO_TRADE'd candidates that were
  *above* their flip (ARM, MRVL, FLEX in calls/LEAPS) and — mirror side —
  COP/LHX/CVX/SHEL in puts (which are `below_flip`, fine for a put). **Effect:** the
  first four pilot records understate their eligible sets; the fix keys off
  `position_vs_flip`. The corrected `VS-…1348-05` run shows the right behavior.
  **Lesson:** the deterministic logic is subtle enough that a hand-rolled
  implementation will have bugs — it needs a tested reference implementation (see
  the code-vs-judgment assessment).
- **Transcription risk.** I rebuilt the handoff into a compact Python table by hand
  each run; that is both slow and error-prone. The eligible set should be computed
  by code from the raw handoff, not retyped.

## 4. Tooling / contract findings

- **Schwab dealer + chain surface is SOUND** [ENG]. `get_dealer_metrics` delivers
  walls, gamma flip with `flip_reliability`/`flip_method`/`flip_reasons`, signed
  DGPI, position, `position_vs_flip`, `confidence` — everything PASS2 consumes. No
  #79/#80-style gap. `get_option_chain` returns exact strikes, bid/ask/mark,
  per-contract IV + greeks, OI, `isChainTruncated`.
- **`theoreticalVolatility = 29` sentinel CONFIRMED** [KB/ENG] on every Schwab
  contract — exactly the hardcoded value VOLATILITY says never to read. The real IV
  is the per-contract `volatility` field. Belongs as an explicit warning in
  `engineering_only/PASS2_MCP_REFERENCE_v3.0.md` (forthcoming).
- **Non-standard adjusted contracts must be filtered** [ENG]. The Schwab chain
  returns adjusted series (e.g. `BABA2`, `$FIXED` deliverable, `volatility:-999`,
  0 OI) alongside standard. Pass-2 must filter to `nonStandard:false` / standard
  `optionRoot` or it will price garbage. → PASS2_MCP_REFERENCE.
- **Limited-expiration coverage = a chain-quality flag** [ENG]. Smaller names (CORZ)
  return only one monthly in the 60–120 band even with `isChainTruncated:false`.
  Treat single-expiry-in-band as **Limited** (Flagged), not Full.
- **Polygon can't bracket the SPY gamma flip; Schwab can** [CAL]. Across every run
  the Polygon producer returned SPY `gamma_flip = null` (`no_zero_cross_in_window`),
  so the Pass-1 macro read **mixed**; the Schwab re-fetch resolved the flip
  (737.5) at Pass-2. **Consequence:** the hostile-macro gate behaves differently by
  pass — mixed at Pass-1 (Polygon), resolvable at Pass-2 (Schwab). The "well below
  flip" criterion also matters: spot *at_flip* is not "well below," so even a
  resolved flip can keep the macro mixed-cautious.

## 5. Data-quality findings [CAL/ENG]

- **Stale price targets on extended markups.** `markup_continuation` names that ran
  well past their breakout range carry `pt_up_*` targets **below** current spot
  (CRWD spot 701, `pt_up_base` 491). The candidate zone and the Pass-2 profit target
  can't be sourced from `pt_*` for these — the viewer's price-target ladder is the
  original range projection, not refreshed to the live extension.
- **Polygon↔Schwab DGPI divergence (calibration flag).** PLTR read DGPI −68.5
  (Polygon, Pass-1) vs +58.7 (Schwab, Pass-2) — a full **sign flip**, larger than
  "different option universes" usually explains. Worth a focused look before trusting
  cross-source DGPI agreement.
- **Live-dealer drift between exports is real and material.** Between the Friday-PM
  and Monday-AM exports of the same view, MRVL's DGPI moved **−61.7 → +57.6**
  (NO_TRADE → Eligible). Dealer reads are time-sensitive; the as_of Wyckoff read is
  not. Intraday, MRVL then broke below its invalidation and was **rejected at Pass-2**
  — exactly the drift the fresh re-fetch exists to catch.

## 6. Report conformance [KB/PROC]

- **Default output is markdown; HTML only on explicit request** (REPORT_FORMAT). The
  first dry-run report was HTML by default — non-conformant. The live Pass-2 report
  is markdown and follows the standard.
- Other conformance gaps caught in the audit: the **Macro Regime card** is for
  *active hostile* only (a mixed read goes in the source bar); **NO_TRADE/WAIT rows
  belong in the table**, not only the alternatives summary; the **Per-ticker detail
  section is required**; **candidate zones render as `$X–$Y`**; the **legend has a
  fixed internal order**; **no inline styles**.

## 7. Boundary check (§13.2) — PASS

Pass-2 re-fetched Schwab dealer + Polygon IV/HV fresh and used the viewer's flip/IV
only as Pass-1 triage. It surfaced material drift (macro hardening, PLTR sign-flip,
MRVL invalidation breach) rather than rubber-stamping Pass-1 — the boundary holds.

## 8. Open / deferred

- [CAL] Resolve the τ paradox after more runs (don't move τ on one day).
- [ENG] Author `engineering_only/PASS2_MCP_REFERENCE_v3.0.md`: `theoreticalVolatility`
  sentinel, non-standard-contract filter, limited-expiry → Limited, strike-count/
  truncation mechanics.
- [CAL] Investigate the Polygon↔Schwab DGPI divergence (PLTR).
- [ENG] Decide whether the viewer should refresh `pt_*` for extended markups, or
  whether Pass-2 sets profit targets from a live continuation structure.
- [PROC] Move the deterministic screen into a tested implementation (see
  `CODE_VS_JUDGMENT_ASSESSMENT_2026-06-29.md`).
- [KB] **Pin the operator-absent FLAGGED-candidate disposition (NO_TRADE vs WAIT).**
  The model/effort matrix (`MODEL_MATRIX_2026-06-29.md`) found the configs split on
  this identical read — Opus-High → NO_TRADE (unattended UNKNOWN lets the Wyckoff veto
  fire), Opus-Med/Sonnet-High → WAIT (pending the operator exchange), Opus-Low →
  NO_TRADE. Every config reaches `FLAGGED → UNKNOWN` identically; the KB doesn't specify
  how that renders, so it's a coin-flip. PASS1/SIGNAL should pin it (WAIT is arguably the
  more faithful — reversible, pending-operator). This single gap dominated the matrix's
  agreement metric.
- [PROC] Portfolio dry-run (§13.3) **done** — first live Portfolio-mode pass on
  `TL-20260629-2032-01` (see the Portfolio-pilot record in `kapman-journal`); central
  finding: the Regime-exit advisory can't run on pre-pipeline positions (no entry-time
  baseline). Still untouched from §13: the feedback smoke test (§13.4).
- See `MODEL_MATRIX_2026-06-29.md` for the model/effort comparison (deterministic ¾ is
  model-invariant; judgment ¼ — anomaly catch-rate + flagged disposition — is where
  cheaper configs diverge) and its harness lessons (`args` subset filter unreliable;
  rate-limit recovered via resume/cache).
