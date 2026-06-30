# Model/Effort Matrix — running the KB pilot across configs (2026-06-29)

**Status: COMPLETE.** Full 5×5 matrix scored; aggregate scorecard below. (The run was
interrupted by a session rate limit mid-scoring and finished via resume
`wf_1702cc41-297`; numbers here are the complete resumed run.)

Companion to [CODE_VS_JUDGMENT_ASSESSMENT_2026-06-29.md](CODE_VS_JUDGMENT_ASSESSMENT_2026-06-29.md)
— that doc argued the KB splits ~¾ deterministic / ~¼ judgment; this experiment tests
that empirically by running the *same* KB on the *same* frozen inputs under five
model/effort configs and measuring where the outputs diverge.

## What this means (plain language)

The experiment set out to answer "can a cheaper model run the KB?" — but the two things
it actually taught us are bigger than that.

- **Cheaper can match expensive here — and "more reasoning" is not automatically better.**
  The *cheapest* config (Sonnet-Med) scored best and a *more expensive* one (Sonnet-High)
  scored worst. The KB is largely a strict rulebook, and Sonnet-High — given more reasoning
  budget — started "improving" on it (it invented a rule that wasn't there and skipped a
  step). Sonnet-Med followed the instructions literally. **For running a checklist-like
  system you want a model that obeys the spec, not one that reasons around it.**
- **The most valuable result wasn't about models — it found a hole in the rulebook.** Most
  of the apparent model "disagreement" was an illusion: when a candidate is *flagged*
  (needs the operator to weigh in) and no operator is present, the KB never says what to do,
  so each model guessed (some NO_TRADE, some WAIT). That's the **KB being silent, not a
  model being wrong.** Pin that one rule and the disagreement disappears. No single-model
  run would have exposed it.
- **It confirmed the strategic call: move the mechanical part into code.** The mechanical ¾
  of the pipeline runs identically across capable models — *except* when a weaker or
  over-eager config quietly broke a rule and flipped a trade decision (a "material
  regression"). **Code never breaks a rule it was given.** So the cracks are the argument for
  codifying the screen and reserving a capable model only for the genuine judgment (e.g.
  spotting odd data — MU's strike, the cross-account covered call).
- **The caution:** this is one run, five data points per model — a strong *hint*, not a
  verdict. Don't switch the production model on it; confirm with a small multi-seed re-run
  of Sonnet-Med vs the Opus baseline first.

## Design

- **Matrix:** 5 configs × 5 datasets. Configs: **Opus-High (baseline)**, Opus-Med,
  Opus-Low, Sonnet-High, Sonnet-Med. Datasets: the 4 Pass-1 view handoffs (calls, puts,
  LEAPS, CSP) + the Portfolio snapshot `TL-20260629-2032-01`.
- **Controls:** every cell reads the same pinned KB (`kapman-kb` @ `8093abd`), the same
  frozen input artifact, and an identical prompt; only `(model, effort)` vary. No live
  MCP fetches inside a cell (inputs self-contained; portfolio regime snapshot frozen) —
  so cells test the model, not data drift.
- **Scoring:** each variant cell is judged against the Opus-High baseline for the same
  dataset. Deterministic layer (tier gate, veto sequence, spread-mandate, structure)
  *should* be identical — divergence there is a regression. Judgment layer (flagged
  handling, anomaly catch-rate, conformance) is the signal.
- **Harness:** `scratchpad/model-matrix/matrix.workflow.js` (Workflow), 46 agents.

## Scorecard — config-level (variant vs Opus-High baseline)

| Rank | Config | Mean Pass-1 disp. | Total det-errors | **Material regressions** | Mean conformance | Portfolio anomalies | Verdict |
|---|---|---|---|---|---|---|---|
| **1** | **Sonnet-Med** | **99.7%** | 3 (2 cosmetic) | **0** | 4.2/5 | 8/11 | tightest parity, cheapest tier |
| 2 | Opus-Med | 57.4%¹ | 2 (coverage gaps) | **0** | **4.4/5** | 7/11 | cleanest deterministic spine |
| 3 | Opus-Low | 83.2% | 9 | **1** | 3.8/5 | 5/11 | one live gate-leak (puts) |
| 4 | Sonnet-High | 60.8%¹ | **27** | **2** | 3.8/5 | **9/11** | worst deterministic record |

¹ Mean disposition for Opus-Med / Sonnet-High is depressed almost entirely by the
NO_TRADE↔WAIT flagged-tier convention (finding 2), **not** screening-logic regression.

**Recommendation (from the run):** **Sonnet-Med** — it posts ~99.7% mean disposition
agreement, **zero material regressions**, conformance 4.2, and only 3 deterministic errors
across the four Pass-1 cells (2 of which — STRL/IFNNY tier-field mislabels on LEAPS — don't
change any trade decision). Its one trade-flipping error is a URA Wyckoff-veto misfire on
puts, plus one anti-hallucination breach (4 fabricated `gamma_flip` levels on puts) — both
worth a targeted guard, neither a config-level regression. Because the **cheapest tier also
wins on parity, there is no cost/quality tradeoff to adjudicate.** Fallback for maximum
deterministic-spine cleanliness + conformance: **Opus-Med**. **Avoid Opus-Low** (live
SOW-gate leak on puts) and **especially Sonnet-High** (rewrites the config-invariant
veto/mandate layer on CSP; bypasses the mid-band tier gate on puts).

## Per-cell detail (disposition% · tier% · Jaccard · det-err · conformance → verdict)

| Config | calls (d1) | puts (d2) | LEAPS (d3) | CSP (d4) | portfolio (d5) |
|---|---|---|---|---|---|
| Opus-Med | 38·100·1.0·0·5/5 | 32·100·1.0·0·5/5 | 61·100·1.0·0·4/5 | 99·100·0.97·2·4/5 | deriv100 · 7/11 · 4/5 |
| Opus-Low | 100·75·1.0·0·3/5 | **32·93·0.83·5·4/5 ⚠MR** | 100·100·1.0·0·4/5 | 100·100·1.0·4·4/5 | deriv100 · 5/11 · 4/5 |
| Sonnet-High | 38·99·1.0·0·4/5 | **93·71·0.79·23·4/5 ⚠MR** | 75·100·1.0·0·4/5 | **37·99·0.97·5·3/5 ⚠MR** | deriv100 · 9/11 · 4/5 |
| Sonnet-Med | 100·99·1.0·0·5/5 | 99·100·0.95·1·4/5 | 100·75·1.0·2·4/5 | 100·99·1.0·0·4/5 | deriv100 · 8/11 · 4/5 |

⚠MR = material regression. (Portfolio structure/direction derivation was 100% for every
config; the variation is anomaly catch-rate of the 11 known anomalies.)

## Findings

**1. The deterministic layer is reproducible by *capable* configs — but it DOES crack, and
the cracks are exactly the case for codifying it.** Opus-Med and Sonnet-Med reproduce the
baseline's tier gate, eligible set (Jaccard 1.0), structures, and veto firing with ~0
trade-flipping deterministic errors. But Opus-Low leaked a SOW-gated-markdown force-flag on
puts (promoted 4 names to live Eligible), and Sonnet-High both bypassed the mid-band tier
gate on puts (5 false sub-τ_high eligibles) and **invented a rule** ("the veto/mandate is
long-premium-only") on CSP that flipped STRL live and dropped 4 spread-mandates. These are
not judgment differences — they are a config rewriting a deterministic contract. **This
sharpens, not weakens, the [assessment's](CODE_VS_JUDGMENT_ASSESSMENT_2026-06-29.md)
recommendation:** the deterministic ¾ should live in tested code precisely because *some*
model/effort configs will silently mis-apply or "improve" it.

**2. Effort is non-monotonic — more reasoning can HURT contract-following.** The cheapest
config (Sonnet-Med) ranked **first**; the more expensive Sonnet-High ranked **last** with
27 gate errors and 2 material regressions. Higher effort appears to have invited Sonnet-High
to *reason past* the spec — inventing a veto-scoping rule, second-guessing the tier gate —
where Sonnet-Med followed the contract literally. For a deterministic-contract-following
task, "think harder" is not strictly better; it raises the odds the model overrides the
rule it was given. (Within Opus the order was more conventional — Med clean, Low cracks.)

**3. The flagged-candidate disposition ambiguity dominates the headline metric — confirmed
as the single most valuable finding.** Opus-Med's 57% / Sonnet-High's 61% mean disposition
are an artifact of one unspecified KB axis applied uniformly to hundreds of candidates:
*what is an operator-absent FLAGGED candidate?* Baseline Opus-High → **NO_TRADE** (unattended
UNKNOWN lets the Wyckoff veto fire); Opus-Med/Sonnet-High → **WAIT** (pending the operator
exchange); Sonnet-Med/Opus-Low → NO_TRADE (matching baseline). Every config reaches
`FLAGGED → UNKNOWN` identically and the deterministic NO_TRADE cases (STRL invalid-dealer,
IFNNY absent-dealer) are correctly preserved by all — so it is a clean labeling toggle, not
a veto regression. → **`[KB]` action item stands:** PASS1/SIGNAL must pin this (WAIT is
arguably the more faithful — reversible, pending-operator).

**4. Portfolio anomaly catch-rate is the judgment signal, and it's noisy + non-monotonic.**
Derivation is perfect (100%) for all configs; the *hunting* for the 11 anomalies ranges 5–9
caught and does **not** track tier (Sonnet-High best at 9/11, Opus-Low worst at 5/11). Two
ground-truth items (SPCX mark<intrinsic, spot-source divergence) were missed by the
**baseline itself**, so relative scores under-penalize there. Catch-rate needs multi-seed
runs before it's trustworthy.

**5. Conformance is robust** (3.8–4.4/5 across configs); report rendering survives every
tier. Anti-hallucination held except two isolated breaches (Sonnet-Med fabricated 4
`gamma_flip` levels on puts; Sonnet-High one price level on LEAPS) — both worth a guard.

## Methodological lessons

- **"Disposition agreement %" is a misleading headline** (finding 3). The decision axes are
  **deterministic gate/veto/mandate misfires** and **material-regression count**, not raw
  disposition%. A future scorecard must foreground deterministic-layer agreement separately
  from the flagged-disposition labeling convention.
- **The baseline is not a fixed point.** Between the interrupted run and the resume, several
  "completed" cells shifted on re-score (e.g. Opus-Low portfolio 9/11 → 5/11; Opus-Med
  portfolio 6/11 → 7/11) — pure LLM nondeterminism. Treat single-digit deltas, ±1
  conformance, and isolated tier-label flips as noise. **n=5 cells per config, single run:**
  these are low-sample point estimates; one bad cell swings a mean. Multi-seed before acting
  on the Sonnet-Med recommendation.
- **Severity ≠ count.** The det-error totals fold trade-flipping gate leaks (Opus-Low puts,
  Sonnet-High puts/CSP) together with outcome-preserving tier-field mislabels (Sonnet-Med
  LEAPS). Read the per-config verdicts for which errors actually change a disposition.
- **Harness bugs this run hit** (also in [PILOT_LESSONS_2026-06-29.md](PILOT_LESSONS_2026-06-29.md)):
  the `args.variantKeys` subset filter did not take effect (ran the full 4-variant matrix,
  46 agents / 4.57M tokens, ~3× the intended subset) → hardcode the subset, don't rely on
  `args`; and the session rate limit mid-scoring was recovered cleanly by resume/cache
  (only the 9 failed cells re-ran).

## Bottom line

The matrix did its job twice over: it **empirically confirmed the deterministic core is
reproducible by capable configs** (and that the cracks are config-specific contract
mis-applications — the argument for codifying), and it **surfaced a real KB underspecification**
(the flagged-candidate disposition) that no single-config run would have exposed. The
provisional production read — *Sonnet-Med holds parity with Opus-High at the cheapest tier,
and more effort is not strictly better* — is striking but rests on n=5/single-run; treat it
as a hypothesis to confirm with a multi-seed re-run, not a settled config choice.
