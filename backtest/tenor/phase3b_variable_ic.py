#!/usr/bin/env python3
"""
Phase 3b — per-variable information coefficient.

Phase 3 showed the COMPOSITE call has no edge. This tests whether any
INDIVIDUAL variable carries signal, which distinguishes two very different
conclusions:

  * no variable separates outcomes  -> the inputs are the problem; no
    rescoring or recompositing will help; abandon.
  * one or two do                   -> the compositing destroyed it (majority
    -voting 13 correlated variables averages signal into noise); rebuild small
    around the survivors.

Method: Spearman rank IC between each variable's bullish-positive reading and
the forward SPY return, on S2 (2012-02..2026-08). Reported on the full
overlapping sample AND on non-overlapping subsamples, which is the only one
that supports a t-stat.

Run:  python3 phase3b_variable_ic.py
"""
import sys, os, math
from datetime import date, timedelta
import bisect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase2_harness import Harness                      # noqa: E402
from phase3_scoring import score_vars, score_all        # noqa: E402

# Orient every magnitude so that MORE POSITIVE = MORE BULLISH.
#   1.7 stores (hv20/hv60 - 1); a falling ratio is the bullish read -> flip.
#   2.2 is deliberately non-monotonic under spec §9.2 (both tails bearish);
#       tested as raw 13wk 10y change and flagged rather than force-fitted.
DIRECTION = {"1.2": +1, "1.3": +1, "1.4": +1, "1.5": +1, "1.6": +1,
             "1.7": -1, "2.1": +1, "2.2": -1, "2.3": +1, "2.4": +1,
             "2.5": +1}

LABEL = {"1.2": "40wk MA slope", "1.3": "dist from 52wk high",
         "1.4": "breadth RSP/SPY", "1.5": "offense XLY/XLP",
         "1.6": "vol term structure", "1.7": "realized vol regime",
         "2.1": "credit HYG/LQD", "2.2": "rate impulse (10y)",
         "2.3": "dollar UUP", "2.4": "copper/gold", "2.5": "COT z"}


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 4:
        return None
    ra, rb = rank(a), rank(b)
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((x - mb) ** 2 for x in rb))
    return None if not da or not db else num / (da * db)


def tstat(ic, n):
    if ic is None or n < 4 or abs(ic) >= 1:
        return None
    return ic * math.sqrt((n - 2) / (1 - ic * ic))


def fwd_return(h, t, ndays):
    rows = h.px["SPY"]
    ds = [r[0] for r in rows]
    i = bisect.bisect_right(ds, t) - 1
    end = t + timedelta(days=ndays)
    if end > ds[-1]:
        return None
    j = bisect.bisect_right(ds, end) - 1
    return None if j <= i else rows[j][3] / rows[i][3] - 1.0


if __name__ == "__main__":
    h = Harness()
    cds = h.call_dates(date(2012, 2, 1), date(2026, 8, 14))

    recs = []
    for t in cds:
        v = score_vars(h, t)
        sc, _ = score_all(h, t)
        rec = {"t": t, "S": sc["live_S"],
               "r60": fwd_return(h, t, 60), "r120": fwd_return(h, t, 120)}
        for k, (c, mag) in v.items():
            rec[k] = None if mag is None else mag * DIRECTION.get(k, 1)
        recs.append(rec)

    print("=" * 88)
    print("PER-VARIABLE INFORMATION COEFFICIENT — S2 core (2012-02 .. 2026-08)")
    print("Spearman rank IC vs forward SPY return; magnitudes oriented "
          "bullish-positive")
    print("=" * 88)

    for horizon, nd in (("r120", 120), ("r60", 60)):
        stride = int(math.ceil(nd / 7.0)) + 1
        sub = recs[::stride]
        print()
        print(f"--- {horizon} ---   full n={sum(1 for r in recs if r[horizon])}"
              f"   non-overlapping n={sum(1 for r in sub if r[horizon])}"
              f"   (stride {stride}w)")
        print(f"  {'var':5s} {'name':22s} {'IC full':>8s} {'IC n-ovl':>9s}"
              f" {'t':>6s} {'p<.05':>6s}   {'botT%':>7s} {'topT%':>7s}"
              f" {'spread':>7s}")
        rows_out = []
        for k in sorted(LABEL):
            pairs = [(r[k], r[horizon]) for r in recs
                     if r.get(k) is not None and r[horizon] is not None]
            if len(pairs) < 30:
                continue
            ic_full = spearman([p[0] for p in pairs], [p[1] for p in pairs])
            sp = [(r[k], r[horizon]) for r in sub
                  if r.get(k) is not None and r[horizon] is not None]
            ic_sub = spearman([p[0] for p in sp], [p[1] for p in sp])
            tv = tstat(ic_sub, len(sp))
            sig = "yes" if tv is not None and abs(tv) > 1.96 else ""
            ordered = sorted(pairs)
            n3 = len(ordered) // 3
            bot = 100.0 * sum(p[1] for p in ordered[:n3]) / max(n3, 1)
            top = 100.0 * sum(p[1] for p in ordered[-n3:]) / max(n3, 1)
            rows_out.append((abs(ic_sub or 0), k, ic_full, ic_sub, tv, sig,
                             bot, top, top - bot))
        for _, k, icf, ics, tv, sig, bot, top, spr in sorted(
                rows_out, reverse=True):
            print(f"  {k:5s} {LABEL[k]:22s} {icf:+8.3f} {ics:+9.3f}"
                  f" {tv if tv is not None else 0:+6.2f} {sig:>6s}"
                  f"   {bot:+7.2f} {top:+7.2f} {spr:+7.2f}")
        # composite for comparison
        pairs = [(r["S"], r[horizon]) for r in recs if r[horizon] is not None]
        sp = [(r["S"], r[horizon]) for r in sub if r[horizon] is not None]
        icf, ics = spearman(*zip(*pairs)), spearman(*zip(*sp))
        tv = tstat(ics, len(sp))
        print(f"  {'S':5s} {'COMPOSITE (live)':22s} {icf:+8.3f} {ics:+9.3f}"
              f" {tv if tv is not None else 0:+6.2f}")

    print()
    print("=" * 88)
    print("MULTIPLE-TESTING NOTE")
    print("=" * 88)
    print("  11 variables x 2 horizons = 22 tests. At p<.05 roughly 1 false")
    print("  positive is expected by chance. Bonferroni-corrected threshold")
    print("  is |t| > 2.85 (p<.05/22). Treat any single 'yes' at |t| ~2 as")
    print("  noise unless it holds on BOTH horizons.")
