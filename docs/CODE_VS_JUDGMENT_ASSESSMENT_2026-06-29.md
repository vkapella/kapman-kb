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

---

# Appendix — the pilot screen script (the deterministic core, verbatim)

This is the throwaway Python Claude wrote to run Pass-1 on the four viewer Export
handoffs. It is reproduced here as **evidence for the argument above**: every
function below is a mechanical evaluation of a runtime contract — no LLM reasoning —
i.e. exactly the part that should become a tested module in the viewer so the export
carries the disposition. The dealer-veto bug (Appendix B) is the case-in-point: a
hand-rolled implementation shipped a logic error a unit test would have caught.

> **Not a spec.** The KB (SYSTEM_PARAMS + the SIGNAL/PASS1/DEALER/VOLATILITY
> contracts) remains the source of truth; this is one *implementation* of it, frozen
> at the pilot. Thresholds (`τ`, `IV_HV_ELEVATED`) were provisional. The
> `position_vs_flip` modelling is corrected in Appendix B.
>
> The per-view **candidate data tables** (`CALLS` 73 / `PUTS` 76 / `LEAPS` 51 /
> `CSP` 79, and `CALLS2`) are **elided** below — they are pilot *inputs*, not
> algorithm, and are preserved in the journal handoff records
> (`kapman-journal/handoffs/viewer/2026-06/VS-2026062*`). Only the logic is kept.

## A. `pilot_pass1.py` — tier gate + SIGNAL trigger sequence

```python
#!/usr/bin/env python3
"""KapMan Pass-1 pilot dry-run — deterministic §A1 tier-gate + SIGNAL trigger sequence.
Applies the runtime contracts (PASS1/SIGNAL/DEALER/VOLATILITY/SYSTEM_PARAMS v3.0)
to the four viewer Export handoffs. Macro gate established separately (mixed).
"""

# ---- SYSTEM_PARAMS thresholds ----
TAU_HIGH = 0.70
TAU_LOW = 0.45
IV_HV_ELEVATED = 1.20
DGPI_HOSTILE = -30  # ≤ -30 hostile tier (bullish-adverse); ≥ +30 supportive (bearish-adverse)

# ---- Macro gate (fetched live SPY/QQQ, prev-close 2026-06-26) ----
# SPY DGPI -100 (hostile) + short-gamma, but gamma_flip null -> below-flip half indeterminate.
# Two-condition hostile composite NOT fully met -> MIXED, conservative read (not run-wide refusal).
MACRO = "MIXED"  # not full hostile -> bullish long-premium NOT run-wide refused; cautionary overlay

# row fields: (sym, regime, rconf, phase, pconf, weekly, sconf, bias, tags, last_event, dgpi, flip, dconf, ivhv, ivstat)
N = None

def vol_status(ivstat):
    if ivstat == "OK": return "FULL"
    if ivstat == "ATM_FALLBACK_BAND": return "LIMITED"
    return "INVALID"  # INSUFFICIENT_CONTRACTS / NO_PRICE_HISTORY / HV_ZERO

def gating(rconf, pconf):
    return min(rconf, pconf) if pconf is not None else rconf

def tier(rconf, pconf, weekly, sconf):
    g = gating(rconf, pconf)
    forceflag = (weekly == "conflict") or (sconf == "conflict")
    if g >= TAU_HIGH and not forceflag:
        return "ACCEPT", g, forceflag
    if g >= TAU_LOW:
        return "FLAGGED", g, forceflag
    return "ESTIMATION", g, forceflag

PHASE_C_BULL_TAGS = ("phase_c_spring_long", "phase_d_lps_long", "sos_breakout_long")
PHASE_C_BULL_EVENTS = ("spring", "shakeout", "sos", "jac")
PHASE_C_BEAR_TAGS = ("phase_c_utad_short", "lpsy_short", "sow_breakdown_short")
PHASE_C_BEAR_EVENTS = ("utad", "ut", "sow")

def phase_c_confirmed(bias, tags, last_event, phase):
    tags = tags or ""
    if bias == "long":
        if any(t in tags for t in PHASE_C_BULL_TAGS): return True
        if last_event in PHASE_C_BULL_EVENTS: return True
    else:
        if any(t in tags for t in PHASE_C_BEAR_TAGS): return True
        if last_event in PHASE_C_BEAR_EVENTS: return True
    return False

def wyckoff_veto(regime, bias, tags, last_event, phase):
    """Returns (fired, kind, reason). kind in structural/conditional/standaside/silent."""
    if regime == "ranging_undefined":
        return True, "standaside", "ranging/undefined — stand aside"
    if bias == "long":
        if regime in ("distribution", "redistribution", "markdown"):
            return True, "structural", f"bullish candidate in {regime} — regime refuses long-premium"
        if regime in ("accumulation", "reaccumulation"):
            if not phase_c_confirmed(bias, tags, last_event, phase):
                return True, "conditional", f"{regime} pre-phase-C — awaiting spring confirmation"
        return False, "silent", "regime authorizes long-premium"
    else:  # short
        if regime in ("accumulation", "reaccumulation", "markup"):
            return True, "structural", f"bearish candidate in {regime} — regime refuses long-premium"
        if regime in ("distribution", "redistribution"):
            if not phase_c_confirmed(bias, tags, last_event, phase):
                return True, "conditional", f"{regime} pre-phase-C — awaiting UTAD confirmation"
        return False, "silent", "regime authorizes long-premium"

def dealer_veto(bias, dgpi, flip, dconf):
    """Per-ticker + macro dealer-timing veto. flip None => below/above-flip indeterminate.
    NOTE: this is the BUGGY original — it keys off "a flip level exists" rather than
    spot-vs-flip. See Appendix B for the corrected position_vs_flip version."""
    if dconf == "invalid":
        return True, "dealer confidence invalid — absent data refuses entry"
    # macro hostile AND bullish -> n/a here (MACRO=MIXED, not full hostile)
    # per-ticker adverse: bullish -> dgpi<=-30 AND spot well below own flip (needs known flip)
    if bias == "long" and dgpi is not None and dgpi <= DGPI_HOSTILE and flip is not None:
        # spot-below-flip can only be confirmed with a known flip; in these handoffs flip is
        # mostly null. (position_vs_flip carries the viewer's coarse read; not modeled here.)
        return True, f"bullish + DGPI {dgpi} hostile + below own flip"
    if bias == "short" and dgpi is not None and dgpi >= -DGPI_HOSTILE and flip is not None:
        return True, f"bearish + DGPI {dgpi} supportive + above own flip"
    return False, "dealer regime not adverse (or flip indeterminate)"

def spread_mandate(ivhv, ivstat):
    vs = vol_status(ivstat)
    if vs == "INVALID":
        return True, f"vol-status INVALID ({ivstat}) — fire-by-default"
    if vs == "LIMITED":
        return True, "vol-status LIMITED (ATM_FALLBACK_BAND) — spread preferred, floor sizing"
    if ivhv is not None and ivhv >= IV_HV_ELEVATED:
        return True, f"IV/HV {ivhv} ≥ {IV_HV_ELEVATED} elevated"
    return False, f"IV/HV {ivhv} not elevated — naked permitted"

def sizing_band(regime, bias, tags, last_event, phase, ivstat, near_flip=False):
    vs = vol_status(ivstat)
    if vs in ("LIMITED", "INVALID"):
        return "floor"
    confirmed_trend = regime in ("markup", "markdown")
    post_c_cont = regime in ("reaccumulation", "redistribution")
    post_c_base = regime in ("accumulation", "distribution")
    pc = phase_c_confirmed(bias, tags, last_event, phase)
    if confirmed_trend or (post_c_cont and pc):
        band = "upper"
    elif post_c_base and pc:
        band = "conditional-top"
    else:
        band = "conditional-floor"
    if near_flip and band == "upper":
        band = "conditional-top"  # one-tier step-down
    return band

def screen(rows, view):
    out = []
    counts = {"ACCEPT": 0, "FLAGGED": 0, "ESTIMATION": 0}
    disp = {"Eligible": 0, "NO_TRADE": 0, "WAIT": 0}
    for r in rows:
        sym, regime, rconf, phase, pconf, weekly, sconf, bias, tags, last_event, dgpi, flip, dconf, ivhv, ivstat = r
        t, g, ff = tier(rconf, pconf, weekly, sconf)
        counts[t] += 1
        rec = {"sym": sym, "regime": regime, "g": round(g, 2), "tier": t,
               "ivhv": ivhv, "vol": vol_status(ivstat), "dgpi": dgpi, "phase": phase,
               "bias": bias, "weekly": weekly, "sconf": sconf, "tags": tags, "ev": last_event}
        if t != "ACCEPT":
            why = []
            if g < TAU_HIGH and g >= TAU_LOW: why.append(f"conf {g:.2f}∈[0.45,0.70)")
            if g < TAU_LOW: why.append(f"conf {g:.2f}<0.45")
            if weekly == "conflict": why.append("weekly conflict")
            if sconf == "conflict": why.append("structure conflict")
            rec.update(disposition="WAIT",
                       reason=("flagged-reading exchange — operator propose-confirm" if t == "FLAGGED"
                               else "estimation path — operator regime confirmation") + " (" + "; ".join(why) + ")",
                       structure="NONE")
            disp["WAIT"] += 1
            out.append(rec); continue
        # ACCEPT -> trigger sequence
        wv, wkind, wreason = wyckoff_veto(regime, bias, tags, last_event, phase)
        if wv:
            rec.update(disposition="NO_TRADE", structure="NONE",
                       reason=f"Wyckoff veto ({wkind}): {wreason}")
            disp["NO_TRADE"] += 1; out.append(rec); continue
        dv, dreason = dealer_veto(bias, dgpi, flip, dconf)
        if dv:
            rec.update(disposition="NO_TRADE", structure="NONE",
                       reason=f"Dealer-timing veto: {dreason}")
            disp["NO_TRADE"] += 1; out.append(rec); continue
        sm, sreason = spread_mandate(ivhv, ivstat)
        base = "CALL" if bias == "long" else "PUT"
        structure = (f"{base}_DEBIT_SPREAD" if sm else f"LONG_{base}")
        band = sizing_band(regime, bias, tags, last_event, phase, ivstat)
        macro_note = ""
        if bias == "long":
            macro_note = " | macro-cautioned (SPY DGPI -100 short-gamma)"
        rec.update(disposition="Eligible", structure=structure, sizing=band,
                   reason=("spread-mandated: " + sreason if sm else "naked: " + sreason) + macro_note)
        disp["Eligible"] += 1
        out.append(rec)
    return out, counts, disp

# ============ DATA: CALLS (73) / PUTS (76) / LEAPS (51) / CSP (79) ============
# [ELIDED — pilot candidate inputs; preserved in kapman-journal/handoffs/viewer/2026-06/]
CALLS = PUTS = LEAPS = CSP = []   # see journal handoff records VS-20260629-0048-01..0049-04

def screen_csp(rows):
    """CSP = cash-secured put (premium SELL, not long-premium). Spread-mandate N/A.
    Eligibility: tier-accept + bullish/neutral structural backdrop (not markdown/dist/redist,
    and accum/reaccum need phase-C spring confirmed) + dealer not invalid. Ranked by IV/HV
    richness (higher = richer premium = better CSP, the opposite of the long-premium reading)."""
    out = []
    counts = {"ACCEPT": 0, "FLAGGED": 0, "ESTIMATION": 0}
    disp = {"Eligible": 0, "NO_TRADE": 0, "WAIT": 0}
    for r in rows:
        sym, regime, rconf, phase, pconf, weekly, sconf, bias, tags, last_event, dgpi, flip, dconf, ivhv, ivstat = r
        t, g, ff = tier(rconf, pconf, weekly, sconf)
        counts[t] += 1
        rec = {"sym": sym, "regime": regime, "g": round(g, 2), "tier": t, "ivhv": ivhv,
               "vol": vol_status(ivstat), "bias": bias, "dgpi": dgpi, "phase": phase,
               "weekly": weekly, "sconf": sconf, "tags": tags, "ev": last_event}
        if t != "ACCEPT":
            rec.update(disposition="WAIT", structure="NONE",
                       reason=("flagged — operator propose-confirm" if t == "FLAGGED" else "estimation path"))
            disp["WAIT"] += 1; out.append(rec); continue
        # structural gate for premium-sell: refuse if structurally bearish
        if regime in ("markdown", "distribution", "redistribution", "ranging_undefined"):
            rec.update(disposition="NO_TRADE", structure="NONE",
                       reason=f"{regime} — structurally bearish, no CSP (assignment into weakness)")
            disp["NO_TRADE"] += 1; out.append(rec); continue
        if regime in ("accumulation", "reaccumulation") and not phase_c_confirmed("long", tags, last_event, phase):
            rec.update(disposition="WAIT", structure="NONE",
                       reason=f"{regime} pre-phase-C — await spring before selling puts")
            disp["WAIT"] += 1; out.append(rec); continue
        if dconf == "invalid":
            rec.update(disposition="NO_TRADE", structure="NONE",
                       reason="dealer confidence invalid — absent data")
            disp["NO_TRADE"] += 1; out.append(rec); continue
        vs = vol_status(ivstat)
        prem = "RICH" if (ivhv is not None and ivhv >= IV_HV_ELEVATED) else "thin"
        band = "floor" if vs in ("LIMITED", "INVALID") else "conditional-top"
        rec.update(disposition="Eligible", structure="CSP", sizing=band,
                   reason=f"CSP eligible — premium {prem} (IV/HV {ivhv}); {regime}")
        disp["Eligible"] += 1; out.append(rec)
    return out, counts, disp
```

(The `report_view` console printer and the `write_journal` LOG-1/LOG-2 emitter are
omitted — they are presentation/IO, not screen logic. `write_journal` is the
deterministic lineage-record writer: derives `PASS1-<lineage_id>`, writes the handoff
manifest + the Eligible/NO_TRADE/WAIT record + `memory/watchlist.md` — itself a clean
"belongs in code" example.)

## B. `run_v2.py` — RTH re-run **with the dealer-veto bugfix**

The original `dealer_veto` (Appendix A) fired the bullish veto on *"a flip level
exists"* instead of the contract's *"spot is below its flip"*. The fix keys off the
handoff's `position_vs_flip` field. This is the single most important artifact in the
appendix: **the bug, and its one-line-conceptual fix, is the empirical case for moving
this logic into a tested module.**

```python
#!/usr/bin/env python3
"""Pass-1 screen on the fresh 2026-06-29T13:48 Swing Long Calls export (RTH refresh).
Same Wyckoff read (as_of 2026-06-26); live-refreshed dealer + IV/HV. Macro still MIXED
(SPY DGPI -96.81 short-gamma, flip null). Lineage VS-20260629-1348-05."""
import os
import pilot_pass1
from pilot_pass1 import screen, report_view, vol_status, MACRO

# ---- BUGFIX: dealer-timing veto must check spot-vs-flip (position_vs_flip), not just
# "a flip level exists". Field 12 below is now position_vs_flip (string), not the flip level.
def dealer_veto_fixed(bias, dgpi, posflip, dconf):
    if dconf == "invalid":
        return True, "dealer confidence invalid — absent data refuses entry"
    if bias == "long" and dgpi is not None and dgpi <= -30 and posflip == "below_flip":
        return True, f"bullish + DGPI {dgpi} hostile + spot below own flip"
    if bias == "short" and dgpi is not None and dgpi >= 30 and posflip == "above_flip":
        return True, f"bearish + DGPI {dgpi} supportive + spot above own flip"
    return False, "dealer regime not adverse (DGPI not hostile, or spot not below flip)"
pilot_pass1.dealer_veto = dealer_veto_fixed   # screen() calls the module-level name

# CALLS2 = [...]  # RTH-refreshed candidate rows — ELIDED (see journal VS-20260629-1348-05)
# POSFLIP = {...} # per-ticker position_vs_flip from the handoff — ELIDED
# Field 12 (old flip level) is overwritten with position_vs_flip before screening:
CALLS2 = [r[:11] + (POSFLIP.get(r[0], "unknown"),) + r[12:] for r in CALLS2]

LID = "VS-20260629-1348-05"; VIEW = "Export - Swing Long Calls"
EXPORTED = "2026-06-29T13:48:01.290Z"; ASOF = "2026-06-26"

out, counts, disp = screen(CALLS2, VIEW)
report_view(VIEW + " [RTH refresh " + LID + "]", out, counts, disp)
# ... lineage-record writes (handoffs/viewer + log/pass1) — same shape as write_journal()
```

**What the fix changed at runtime** (vs the first export, `VS-20260629-0048-01`):
candidates that are `above_flip` with hostile DGPI — ARM, MRVL, FLEX in calls/LEAPS —
were wrongly `NO_TRADE`'d by the buggy version and are correctly **eligible** under the
fix; the bearish-mirror names (COP/LHX/CVX/SHEL, `below_flip`) were always fine for
puts. The earlier pilot records (`…0048-01..04`) therefore *understate* their eligible
sets — flagged in [PILOT_LESSONS_2026-06-29.md](PILOT_LESSONS_2026-06-29.md) §3.
