# Assessment — How much of the KB is code vs. Claude judgment?

Prompted by an observation from the pilot: to run Pass-1, Claude wrote a Python
script that took the viewer's JSON handoff and computed the eligible set
deterministically. That raises two questions:

1. Should that Python code live in the viewer (so the export carries the
   disposition, not just the raw fields)?
2. More broadly — **how much of the knowledge base could live in code, and how much
   is actually exercising Claude's judgment?**

Short answer: **a large fraction of the Pass-1/Pass-2 *mechanics* is deterministic
and belongs in tested code; Claude's enduring value is a narrower judgment layer.**
The pilot effectively ran the experiment — the script *was* the deterministic part,
and everything Claude did around it (interpreting the macro, adjudicating drift,
catching its own bug, auditing report conformance, reconciling contracts) was the
judgment part. They separate cleanly.

---

## The two kinds of content the pilot made visible

**(A) Deterministic contracts.** Given structured inputs, the output is mechanical —
no interpretation. The Python screen computed Eligible / NO_TRADE / WAIT, structure,
and candidate zones with **zero LLM reasoning**. These are code expressed as prose.

**(B) Judgment.** Requires weighing incomplete, conflicting, edge, or novel
information — or deciding *how conservative* to be. No lookup table resolves it.

A clean litmus test for any KB rule:
- Evaluates to a definite output from structured inputs, no ambiguity → **code**.
- Requires weighing incomplete/conflicting/novel info, or a conservatism call →
  **judgment**.
- Produces a deterministic output but the *threshold* is a tuning decision → **code
  implements it, the KB owns the value, operator/Claude calibrates it.**

## Where each KB component lands

| KB component | Determinism | Home |
|---|---|---|
| Tier gate: `gating = min(rconf,pconf)`, τ thresholds, force-flags | Pure deterministic | **Code** |
| Wyckoff veto (direction × regime × phase-C confirmation table) | Deterministic given a confirmed read | **Code** |
| Dealer-timing veto (DGPI tier × `position_vs_flip`) | Deterministic | **Code** — and the pilot's bug proves it needs *tested* code |
| Spread-mandate (`iv_hv ≥ 1.20`, vol-status, IV-rank reinforce) | Deterministic | **Code** |
| DGPI tiers, DTE bands, near-flip step-down, sizing bands | Lookup/arithmetic | **Code** (values owned by SYSTEM_PARAMS) |
| Candidate-zone + DTE-band assembly | Deterministic | **Code** |
| Chain-quality / truncation classification; strike selection mechanics | Mostly deterministic | **Code** |
| Lineage-ID derivation, log file paths, schema | Pure deterministic | **Code** (already specified mechanically) |
| Report rendering: field caps, section order, legend order, zone formatting | Deterministic structure | **Code / template** (REPORT_TEMPLATE already exists) |
| Spread-mandate IV/HV re-confirm (re-fetch + compare) | Deterministic | **Code** |
| — | — | — |
| Propose-confirm Wyckoff regime/phase (when flagged/estimation) | **Judgment** | **Claude + operator** |
| Flagged-reading exchange resolution | **Judgment** | **Claude + operator** |
| Drift adjudication (name material change → return to operator) | Threshold is code; framing + handoff is judgment | **Claude** |
| Conservative reads on degraded/edge data (null flip→mixed; `at_flip`; sentinel detection; INVALID handling) | **Judgment / principle** | **Claude** |
| Report rationale prose (the 20-word "why") | **Judgment** | **Claude** |
| Novel situations the rules don't cover | **Judgment** | **Claude** (the reason an LLM runtime exists) |
| Contract reconciliation (#79/#80, tooling mismatches, these lessons) | **Judgment** | **Claude + operator** |

## Rough proportions (honest estimate from the pilot)

- **Pass-1 screening:** ~**70–80 %** of the mechanical work is deterministic
  (codifiable); ~20–30 % is judgment — the flagged/estimation tier, the macro/degraded
  edge reads, and the report narrative.
- **Pass-2 validation:** ~**50–60 %** deterministic (chain fetch, quality
  classification, strike mechanics, spread-mandate re-confirm); ~40–50 % judgment —
  drift adjudication and the Validated/Flagged/Rejected call on ambiguous reads.
- **The regime reads themselves** (Wyckoff / dealer / volatility) are **already
  engine code** (the v2 producers + the polygon-mcp). The judgment there is the
  *confirmation and override discipline*, not the computation.

## Direct answer to the question: yes, move the deterministic screen into code

The viewer already runs the v2 Wyckoff engine and the dealer/IV producers. Adding the
deterministic screen there means **the export carries the eligible set + structure +
candidate zones + sizing band**, not just the raw fields. Concretely it should emit,
per row, the tier verdict (accept/flag/estimation), the trigger outcomes, the
structure (naked vs spread), the candidate zone, and the sizing band.

Why this is the right call:
- **It kills the bug class.** The pilot's dealer-veto error was a hand-rolled logic
  bug; the transcription of 73 rows per run is slow and error-prone. One tested
  implementation with unit tests (the viewer already has catalog↔flatten parity
  tests — same discipline) removes both.
- **It frees Claude for what only Claude does** — confirming flagged reads,
  adjudicating drift, the conservative edge calls, the report narrative, and evolving
  the contracts. Claude stops re-deriving a deterministic screen each run.
- **It matches the plan.** Integration Plan Stage 2 already calls for an "optional
  viewer best-Wyckoff Pass-1 export button" and viewer-side ID minting. This is that,
  accelerated — and the pilot showed the deterministic core is stable enough to lift.

## The caveats that keep judgment (and the KB) load-bearing

1. **The code consumes a *confirmed* read, not a raw one.** The viewer's regime is the
   v2 engine's classification; the KB's tier gate exists precisely to decide whether
   to trust it (auto-accept) or route it to the operator (flagged). Code can produce
   the *auto-accept* eligible set; it cannot replace the propose-confirm exchange for
   the flagged tier. So the screen-in-code emits the auto-accept set + the flagged
   queue; Claude/operator still resolves the queue.
2. **The edges are judgment, not rules.** Null-flip→mixed macro, `at_flip`, the
   `theoreticalVolatility` sentinel, stale targets, the Polygon↔Schwab DGPI sign-flip
   — these need the conservative-read *principle* and Claude's adjudication. Hard-coding
   them produces brittle rules that fail on the next unanticipated shape.
3. **Drift is a human-in-the-loop handoff by design.** Pass-2 *names* material drift
   and returns to the operator. The threshold is code; the "frame it and hand it back"
   is judgment.
4. **The contracts keep changing.** This pilot alone produced eight lessons. Code
   freezes a snapshot; the **KB stays the source of truth for the spec**, and the code
   is an implementation that must track it under a parity discipline. Codifying does
   *not* shrink the KB to nothing — it changes the KB's job from "thing Claude
   re-interprets every run" to "spec the code implements + principles Claude reasons
   with."

## Recommended architecture (the synthesis)

- **Code (viewer or a thin service), with unit tests:** the deterministic screen —
  tier gate, trigger sequence, structure, candidate zone, sizing band, lineage ID,
  chain-quality classification, and report rendering. Spec = SYSTEM_PARAMS + the
  trigger/format contracts.
- **Claude (runtime judgment):** propose-confirm + flagged resolution, drift
  adjudication, conservative reads on degraded/edge data, report rationale/narrative,
  novel-situation handling, and turning lessons-learned into KB changes.
- **The KB:** stays the source of truth for the *contracts* (so the code has a spec)
  **and** the *principles that are judgment* (conservative-read discipline,
  anti-hallucination floor, the Pass-1→Pass-2 boundary). The split inside the KB:
  the mechanical contracts increasingly point at an implementation (as the
  `engineering_only/*_MCP_REFERENCE` files already foreshadow); the `llm_runtime`
  principle files keep the judgment.

## One-line takeaway

The pilot showed Pass-1's screen is ~3/4 deterministic and should be lifted into
tested code in the viewer; Claude's durable value is the ~1/4 that is genuine
judgment — confirmation, drift, conservative edge calls, narrative, and evolving the
contracts — plus owning the spec the code implements.
