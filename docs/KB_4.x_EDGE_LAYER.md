# KapMan KB 4.x — Edge Layer (OpenAnt-inspired)

> **Consolidated into [`Kapman_System_Integration_Plan_v1.0.md`](Kapman_System_Integration_Plan_v1.0.md) (2026-06-25)** — that document is now the canonical master plan; this file remains as detailed design background for the precision / adversarial-verify layer (Stage 3).

**Status:** Approved direction, not yet built. Layers on top of KB 4.0.
**Date:** 2026-06-18
**Owner:** vkapella
**Companion:** `KB_4.0_DESIGN.md` (the foundation this builds on)

Evaluation of [OpenAnt](https://github.com/knostic/OpenAnt) (Knostic; Apache-2; Go CLI +
Python runtime) for architectural ideas applicable to KapMan, plus the decisions taken.
Objective driving the evaluation: a more robust system for identifying tickers/options to
pursue the KapMan investment plan's 100% YoY target. *Any pipeline that provides edge
helps* — but not at the cost of fragility.

---

## 1. The core insight

OpenAnt and KapMan are the **same problem shape**: a high-recall detector feeding an
adversarial verifier whose job is to *kill* candidates so only real ones survive
("Stage 1 detects. Stage 2 attacks. What survives is real."). KapMan already has the
skeleton — Pass 1 detects, Pass 2 validates — but **Pass 2 today is a *confirmer*, not an
*attacker***: it re-fetches the live chain and confirms feasibility/exactness; it does not
actively try to *refute the thesis*. For a 100% YoY target, removing losers is as
load-bearing as finding winners, and adversarial verification is a loser-removal machine.

---

## 2. What OpenAnt actually is (grounded in the repo)

- **Seven-phase linear pipeline:** `parse → enhance → analyze → verify → build-output →
  report`, plus internal phases `app_context`, `llm_reach`, `dynamic_test`.
- **Artifact-passing on disk:** "Each step picks up the output of the previous one from
  the project's scan directory." Stateful projects under
  `~/.openant/projects/<org>/<repo>/scans/`; individual stages can be re-run.
- **Per-phase (provider, model) pairs** via versioned `config.json` (`$schema_version`):
  stronger reasoning models (e.g. Claude Opus) for detect/verify/reachability, lighter
  models for context/report/test-gen. Tool-calling drives the `enhance`/`verify` agentic
  loops.
- **Dual goal:** minimize false positives (verify demands evidence; findings must survive
  the attack) *and* false negatives (strong reasoning + systematic exploration).

---

## 3. Concept → KapMan mapping (ranked by edge)

| OpenAnt concept | KapMan import | Edge |
|---|---|---|
| Stage 2 attacks / "what survives is real" | Red-team that tries to refute the long thesis | Highest |
| Artifact-passing between stages | Carry structured artifacts, not fragile context | High |
| Per-phase model assignment | Tier by stage; deterministic-MCP vs LLM per stage | High |
| `llm_reach` (reachability) | **Tradeability gate** — can you actually fill/exit? | High |
| Targets FP *and* FN | Logging NO_TRADE/WAIT becomes FN *measurement* | High |
| `dynamic_test` (run the exploit) | viewer `forward_panel` forward-eval | Medium |
| `$schema_version` config-as-contract | Version log records; externalize *tunables* only | Medium |

---

## 4. Decisions taken (interview, 2026-06-18)

1. **Adversarial verify = HYBRID (flag, don't kill).** The red-team runs and surfaces
   named flags + invalidation conditions; it never auto-rejects. The operator decides.
2. **Pipeline shape = MINIMAL.** No discrete CLI stages / artifact-passing
   re-architecture. The new behavior is added *inside the existing Pass 2 runbook* on top
   of the 4.0 log.
3. **Sequencing = LAYER AS 4.x AFTER 4.0.** Ship 4.0 (memory + complete logging) first;
   this is a follow-on. Do not bloat the approved 4.0 plan.
4. **Self-measuring = DESIGN NOW, BUILD LATER.** Bake the keys/fields into the 4.0 log so
   the precision/false-negative loop is a later drop-in via the viewer forward-eval.

---

## 5. What this means concretely

### A. The one 4.0 touch (design-now): decision-anchor + reserved fields
Folded into `KB_4.0_DESIGN.md` §4/§9. Every logged row gains:
- a **decision anchor** — `decided_at` + `underlying_ref` (Pass 2 also logs `option_mid`)
  so the viewer can later measure what a ticker did after a yes/no, including refusals;
- reserved nullable arrays **`attack_flags[]`** and **`invalidation_conditions[]`** (empty
  in 4.0, populated when 5.B lands);
- `schema_version`.

Written-but-mostly-empty in 4.0 — no behavior change, but the deferred loops become
drop-ins, not reshapes.

### B. 4.x-1 — Hybrid adversarial verify (flag, don't kill)
Extends KapMan's *existing* Pass 2 `Flagged` state (not a new concept). Attacker lenses
run on survivors:
- **Structural** — distribution disguised as accumulation? (Wyckoff failure mode)
- **Dealer** — gamma flip / walls capping the target or fighting the move?
- **Vol** — IV-crush / vega risk: does the structure lose even if direction is right?
- **Tradeability** — spread width / OI / volume / exit-ability (see 4.x-2)
- **Event** — earnings/macro landmine inside the DTE window
- **Regime** — survives a hostile-SPY scenario, or just beta?

Outputs:
- named **attack flags** surfaced in the report's Flagged reasons — operator decides;
- **the novel closure:** attacks that *fail* to kill the trade are pre-registered
  invalidation conditions → written into the SIGNAL exit-trigger fields. **The red-team
  authors the stops.**

### C. 4.x-2 — Tradeability gate (from `llm_reach`)
A precision check inside Pass 2 — spread/OI/volume/exit-ability — that raises a flag, not
a veto. Cheap, options-specific false-positive reducer. A perfect setup on an untradeable
contract is the trading equivalent of a vuln in dead code.

### D. 4.x-3 — Self-measuring loop (designed now, built later)
Feed logged decision-anchors (including refusals) to the viewer `forward_panel` →
- **precision:** did recommended trades work;
- **false-negative rate:** did NO_TRADE/WAIT tickers run without you;
- output a periodic **scorecard** that tells you whether to loosen or tighten the
  confidence floor. Turns the log from audit into a tuning signal. Only 4.0 dependency is
  the anchor fields in (A).

### E. Optional / low-priority
**Model-compute tiering** (cheap breadth at screen, Opus depth at verify). Since KapMan's
compute is already mostly deterministic MCP, the higher-value axis is *deterministic-MCP
vs LLM-judgment per stage*, not which LLM. Nice-to-have, not a 4.x core item.

---

## 6. Explicitly declined (fragility line)

- Discrete CLI stage machinery / artifact-passing re-architecture (chose MINIMAL).
- Cross-provider model swapping (Claude Code is Anthropic-native; not worth the surface).
- Config-externalized **guardrails** — KapMan's guardrails being immutable is a deliberate
  safety feature. Externalize tunables and version log records; leave guardrails hard-coded.
- Cloning the Go-CLI + Python-runtime + adapter layer. KapMan's "CLI" *is* Claude Code;
  adopt the patterns, not the codebase.

---

## 7. Honest note on 100% YoY

No pipeline guarantees that number. What this architecture genuinely contributes is three
levers: **precision** (kill losers via the red-team), **breadth** (more shots per dollar
if tiering is ever adopted), and **survival-weighted conviction** (size up only on verified
edge). That is where pipeline design touches the return target; the rest is execution and
discipline.

---

## 8. Build order (all after 4.0 ships)

1. **4.x-1** Hybrid adversarial verify (inside Pass 2 runbook) — populates `attack_flags[]`
   + `invalidation_conditions[]` and the SIGNAL exit triggers.
2. **4.x-2** Tradeability gate (inside Pass 2).
3. **4.x-3** Self-measuring loop (viewer forward-eval on logged anchors) — the deferred
   closed loop from `KB_4.0_DESIGN.md` §6, now with a precision/FN scorecard.
