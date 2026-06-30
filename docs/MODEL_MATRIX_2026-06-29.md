# Model/Effort Matrix — running the KB pilot across configs (2026-06-29)

**Status: INTERIM.** Sonnet-Med scoring + the aggregate scorecard failed on a session
rate limit and are being completed via resume (`wf_1702cc41-297`). This records the
findings from the cells that completed; it will be filled out when the resume lands.

Companion to [CODE_VS_JUDGMENT_ASSESSMENT_2026-06-29.md](CODE_VS_JUDGMENT_ASSESSMENT_2026-06-29.md)
— that doc argued the KB splits ~¾ deterministic / ~¼ judgment; this experiment tests
that claim empirically by running the *same* KB on the *same* frozen inputs under five
model/effort configs and measuring where the outputs diverge.

## Design

- **Matrix:** 5 configs × 5 datasets. Configs: **Opus-High (baseline)**, Opus-Med,
  Opus-Low, Sonnet-High, Sonnet-Med. Datasets: the 4 Pass-1 view handoffs (calls, puts,
  LEAPS, CSP) + the Portfolio snapshot `TL-20260629-2032-01`.
- **Controls:** every cell reads the same pinned KB (`kapman-kb` @ `8093abd`), the same
  frozen input artifact, and an identical prompt; only `(model, effort)` vary. No live
  MCP fetches inside a cell (the inputs are self-contained — for the portfolio cell the
  current-regime snapshot is frozen too), so cells test the model, not data drift.
- **Scoring:** each variant cell is judged against the Opus-High baseline for the same
  dataset. Deterministic layer (tier gate, veto sequence, spread-mandate, structure/
  direction derivation) *should* be identical — divergence there is a regression.
  Judgment layer (flagged-reading handling, anomaly catch-rate, conformance) is the signal.
- **Harness:** `scratchpad/model-matrix/matrix.workflow.js` (Workflow), 46 agents
  (25 producers + 20 scorers + 1 scorecard).

## Results — completed cells (variant vs Opus-High baseline)

| Config | calls (d1) | puts (d2) | LEAPS (d3) | CSP (d4) | portfolio (d5) |
|---|---|---|---|---|---|
| **Opus-Med** | tier **100%** · jac **1.0** · **0** det-err · conf 5/5 | tier 100% · jac 1.0 · 0 · 5/5 | tier 100% · jac 1.0 · 0 · 5/5 | tier 100% · jac 0.97 · 2 · 4/5 | deriv 100% · **6/11** anomalies · adv✓ dte✓ |
| **Opus-Low** | tier 75% · jac 1.0 · **17** det-err · 3/5 | **MATERIAL REGRESSION** · jac 0.83 · 5 det-err · 4/5 | tier 100% · 0 · 4/5 | tier 100% · 0 · 3/5 | deriv 100% · **9/11** · adv✓ dte✓ |
| **Sonnet-High** | tier 98.6% · jac 1.0 · 0 · 5/5 | _pending resume_ | tier 100% · jac 1.0 · 0 · 4/5 | _pending_ | _pending_ |
| **Sonnet-Med** | _pending resume_ | _pending_ | _pending_ | _pending_ | _pending_ |

(`tier` = tier-gate agreement; `jac` = eligible-set Jaccard; `det-err` = deterministic-layer
errors; `conf` = REPORT_FORMAT conformance /5; `anomalies` = portfolio anomalies caught of 11.)
Verdicts so far: Opus-Med 5× minor-drift; Opus-Low 3× minor-drift, 1 matches, **1 material
regression**; Sonnet-High 2× minor-drift (3 pending).

## Findings

**1. The deterministic ¾ is model-invariant — the assessment's central claim, confirmed.**
Opus-Med and Sonnet-High reproduce the baseline's tier gate (100% / 98.6%), eligible set
(Jaccard 1.0), structures, veto firing, and spread-mandate with **zero deterministic
errors** on calls/puts/LEAPS. The screen does not care which capable model runs it — which
is exactly the case for lifting it into tested code (the assessment's recommendation).

**2. The matrix surfaced a real KB underspecification — the most valuable result.**
The low "disposition agreement" numbers (Opus-Med 38%/32% on calls/puts) are **not** model
degradation. They come from a single unspecified axis: *what disposition is an
operator-absent FLAGGED candidate?* The configs split three ways on the identical
upstream read —
- **Opus-High (baseline)** → **NO_TRADE** (the unattended FLAGGED → UNKNOWN read lets the
  Wyckoff veto fire as a hard refusal);
- **Opus-Med, Sonnet-High** → **WAIT** (deferred, pending the operator flagged-reading
  exchange; reversible on resolution);
- **Opus-Low** → back to **NO_TRADE** (coincidentally matching baseline → its disposition
  agreement reads 100% while its *tier* agreement is only 75%).

Every config reaches `FLAGGED → UNKNOWN` identically; they disagree only on whether that
state renders as a terminal veto or a pending flag. It's a coin-flip **because the KB
doesn't pin it.** Arguably WAIT is the more faithful disposition (the state genuinely is
"pending operator," and it's reversible). → **`[KB]` action item:** specify the
operator-absent FLAGGED-candidate disposition in PASS1/SIGNAL (NO_TRADE vs WAIT) so the
pipeline is deterministic here. This single ambiguity dominates the headline agreement
metric across the whole matrix.

**3. Opus-Low is where the deterministic layer actually cracks.** It produced the only
**material regression** (puts: eligible-set break, Jaccard 0.83 + 5 gate errors),
17 mis-tierings on calls (right final disposition, wrong tier path — fragile), and
conformance sliding to 3/5 on two sets. Low reasoning effort starts mis-applying the
contract, not just rephrasing the judgment.

**4. Portfolio anomaly catch-rate is the true judgment signal — noisy and effort-sensitive.**
Structure/direction derivation is perfect (100%) for every config, but the *hunting* for
the 11 known anomalies (MU-distribution-adverse, SPCX mark<intrinsic, XLU cross-account
covered call, CSCO-below-invalidation, …) varies: baseline 11, Opus-Low 9/11, Opus-Med
6/11. The deterministic derivation is free; the judgment-layer anomaly hunt is what
cheaper configs lose — and it doesn't move monotonically with tier (Opus-Low caught more
than Opus-Med here), so catch-rate needs multiple seeds before it's trustworthy.

**5. Conformance holds high** (4–5/5) for Opus-Med and Sonnet-High; only Opus-Low dips to
3/5. Report rendering is robust across configs.

## Methodological lessons (the metric + harness themselves)

- **"Disposition agreement %" is a misleading headline** — it's dominated by the one
  flagged-disposition ambiguity (finding 2). The scorecard must foreground
  **deterministic-layer agreement** (tier · Jaccard · structure · veto firing · det-err
  count) *separately* from **judgment-layer divergence** (flagged disposition, anomaly
  catch-rate). The per-cell scorers correctly classified the NO_TRADE/WAIT split as
  *judgment, not deterministic* — but the flat disp% number hides that.
- **The baseline is not a fixed point.** LLM nondeterminism means even Opus-High varies
  run-to-run; treat small agreement gaps as noise and score categorical/structural
  agreement, not prose. Multi-seed baselines would tighten this.
- **Harness bugs this run hit** (see [PILOT_LESSONS_2026-06-29.md](PILOT_LESSONS_2026-06-29.md)):
  the `args.variantKeys` subset filter did not take effect (ran the full 4-variant matrix,
  46 agents / 4.57M tokens, ~3× the intended subset) → hardcode the subset, don't rely on
  `args`; and the run hit a session rate limit mid-scoring (9 cells failed) → the
  resume/cache recovered it (cached producers, only failed cells re-run).

## Pending (on resume `wf_1702cc41-297`)

- Sonnet-Med scoring (all 5 cells) — **the config the run was meant to test** — plus the
  3 failed Sonnet-High scorers (d2/d4/d5) and the aggregate scorecard.
- Fill the results table + add the config-level ranking and the cheapest-that-holds-parity
  recommendation.
- Harness: relocate `scratchpad/model-matrix/` to a durable home if this becomes a
  repeatable eval; split the scorecard headline per the methodological lesson above.
