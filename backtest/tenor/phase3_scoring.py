#!/usr/bin/env python3
"""
Phase 3 — variable scoring and call generation.

Implements the live scoring rules (spec §3/§4 with the §9 clarifications)
plus the shadow variants proposed in MAINTAIN_tenor_shadow_scoring.md:
  A2  linear raw sum
  A3  coverage-normalized
  A1  magnitude banding
  B   block voting (trend / vol / rotation)

Scores segments S2/S3/S4, where 1.1 (Wyckoff) is structurally dark and no
MCP harvest is required. S1 is scored by phase3_s1.py once the harvest lands.

[CAL] choices are marked; none are invented where a logged run established a
precedent. Where the spec is silent the run-log convention is followed and
labelled.

Run:  python3 phase3_scoring.py
"""
import sys, os, math, bisect
from datetime import date, timedelta
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase2_harness import Harness, SEGMENTS, asof   # noqa: E402

BULL, BEAR, NEUT, DARK = 1, -1, 0, None

# ---- [CAL] thresholds: taken from the run log, not invented here ----------
FLAT_MA_SLOPE   = 0.005    # 1.2  ±0.5% / 10wk           (spec §3)
NEAR_HIGH       = 0.03     # 1.3  within 3%              (spec §3)
FAR_HIGH        = 0.10     # 1.3  >10% off               (spec §3)
CONTANGO_MIN    = 0.05     # 1.6  >5%                    (spec §3)
HV_BOUNDARY     = 0.02     # 1.7  |ratio-1| < 2% = boundary  [CAL, run-log]
RATE_BAND_BP    = 40.0     # 2.2  ±40bp                  (spec §9.2)
COT_EXTREME_Z   = 2.0      # 2.5  |z| > 2 over 52wk      [CAL, un-parameterized
                           #      in spec; flagged at 2026-08-16 §7]


def s(x):
    """sign -> BULL/BEAR/NEUT"""
    return BULL if x > 0 else (BEAR if x < 0 else NEUT)


def band(x):
    """A1 magnitude banding: <1% -> 0, 1-5% -> ±1, >=5% -> ±2"""
    a = abs(x)
    m = 0 if a < 0.01 else (1 if a < 0.05 else 2)
    return m if x > 0 else -m


# --------------------------------------------------------------- variables
def score_vars(h, t):
    """Return {var: (contribution, magnitude_or_None)} for one call date."""
    v = {}

    # 1.2 — 40wk MA position + slope
    c = h.close("SPY", t)
    ma = [h.weekly_close("SPY", t, k) for k in range(40)]
    ma = [x for x in ma if x is not None]
    ma_now = sum(ma) / len(ma) if ma else None
    ma_prev = [h.weekly_close("SPY", t, k) for k in range(10, 50)]
    ma_prev = [x for x in ma_prev if x is not None]
    ma_prev = sum(ma_prev) / len(ma_prev) if ma_prev else None
    if None in (c, ma_now, ma_prev) or not ma_prev:
        v["1.2"] = (DARK, None)
    else:
        slope = ma_now / ma_prev - 1.0
        above = c > ma_now
        if abs(slope) <= FLAT_MA_SLOPE:
            v["1.2"] = (NEUT, slope)               # flat -> chop condition
        else:
            v["1.2"] = (BULL if (above and slope > 0) else
                        (BEAR if (not above and slope < 0) else NEUT), slope)

    # 1.3 — distance from 52wk high
    hi = h.high_52wk("SPY", t)
    if c is None or hi is None or not hi:
        v["1.3"] = (DARK, None)
    else:
        off = c / hi - 1.0                          # negative = below high
        v["1.3"] = (BULL if off >= -NEAR_HIGH else
                    (BEAR if off <= -FAR_HIGH else NEUT), off)

    # 1.4 / 1.5 / 2.1 / 2.4 — 13wk ratio trends
    for key, (a, b) in {"1.4": ("RSP", "SPY"), "1.5": ("XLY", "XLP"),
                        "2.1": ("HYG", "LQD"), "2.4": ("CPER", "GLD")}.items():
        r = h.ratio_13wk(a, b, t)
        v[key] = (DARK, None) if r is None else (s(r), r)

    # 1.6 — vol term structure
    ct = h.vol_term(t)
    if ct is None:
        v["1.6"] = (DARK, None)
    else:
        v["1.6"] = (BULL if ct >= CONTANGO_MIN else
                    (BEAR if ct < 0 else NEUT), ct)

    # 1.7 — realized vol regime
    rv = h.realized_vol(t)
    if rv is None:
        v["1.7"] = (DARK, None)
    else:
        r = rv["ratio"]
        v["1.7"] = (NEUT if abs(r - 1.0) < HV_BOUNDARY else
                    (BULL if r < 1.0 else BEAR), r - 1.0)

    # 2.2 — rate impulse primary, slope qualifier (spec §9.2)
    cv = h.curve(t)
    if cv is None:
        v["2.2"] = (DARK, None)
    else:
        d10 = cv["d10_13wk_bp"]
        if d10 >= RATE_BAND_BP:
            v["2.2"] = (BEAR, d10 / 100.0)
        elif d10 <= -RATE_BAND_BP:
            prev = asof(h.tsy, t - timedelta(days=91))
            steep = (cv["s2s10_bp"] - (prev[2] - prev[1]) * 100.0) if prev else 0
            v["2.2"] = (BEAR if steep > 0 else BULL, d10 / 100.0)
        else:
            v["2.2"] = (NEUT, d10 / 100.0)

    # 2.3 — dollar (strength = headwind)
    u = h.pct_13wk("UUP", t)
    v["2.3"] = (DARK, None) if u is None else (-s(u), -u)

    # 2.5 — COT: trend confirms, extremes read contrarian
    q = h.cot_asof(t)
    if q is None:
        v["2.5"] = (DARK, None)
    else:
        hist = [(d, l - sh) for d, l, sh, _ in h.cot if d <= q["report_date"]]
        if len(hist) < 53:
            v["2.5"] = (DARK, None)
        else:
            net = hist[-1][1]
            trend = net - hist[-14][1]              # 13 weekly reports back
            w = [x for _, x in hist[-52:]]
            mu = sum(w) / len(w)
            sd = math.sqrt(sum((x - mu) ** 2 for x in w) / (len(w) - 1))
            z = (net - mu) / sd if sd else 0.0
            # extreme -> contrarian, offsets the trend read (2026-08-16 §2.5)
            v["2.5"] = (NEUT if abs(z) > COT_EXTREME_Z else s(trend), z)
    return v


L1_VARS = ["1.2", "1.3", "1.4", "1.5", "1.6", "1.7"]   # 1.1 dark in S2-S4
L2_VARS = ["2.1", "2.2", "2.3", "2.4", "2.5"]
BLOCKS = {"trend": ["1.2", "1.3"], "vol": ["1.6", "1.7"],
          "rotation": ["1.4", "1.5"]}


def majority(vals):
    """Live mapping: directional majority -> ±1, unanimous -> ±2."""
    live = [x for x in vals if x is not None]
    if not live:
        return 0
    b, r = sum(1 for x in live if x > 0), sum(1 for x in live if x < 0)
    if b == r:
        return 0
    d = 1 if b > r else -1
    return d * (2 if (b == 0 or r == 0) and len(live) >= 4 else 1)


def l1_chop_flag(v):
    """§3 literal test, minus 1.1 which is dark: >=2 of 3 fire."""
    f = 0
    if v["1.2"][0] is not None and v["1.2"][1] is not None \
            and abs(v["1.2"][1]) <= FLAT_MA_SLOPE:
        f += 1
    if v["1.4"][0] is not None and v["1.4"][1] is not None and v["1.4"][1] < 0:
        f += 1
    if v["1.6"][0] is not None and v["1.6"][1] is not None \
            and v["1.6"][1] < CONTANGO_MIN:
        f += 1
    return f >= 2


def call_from(S, chop):
    if S >= 3 and not chop:
        return "UP"
    if S <= -3 and not chop:
        return "DOWN"
    return "CHOP"


def score_all(h, t):
    v = score_vars(h, t)
    c1 = [v[k][0] for k in L1_VARS]
    c2 = [v[k][0] for k in L2_VARS]
    chop = l1_chop_flag(v)

    live_S = 2 * majority(c1) + majority(c2)
    out = {"live": call_from(live_S, chop), "live_S": live_S, "chop": chop}

    # A2 raw sum
    r1 = sum(x for x in c1 if x is not None)
    r2 = sum(x for x in c2 if x is not None)
    out["A2_S"] = 2 * r1 + r2

    # A3 coverage-normalized
    n1 = sum(1 for x in c1 if x is not None) or 1
    n2 = sum(1 for x in c2 if x is not None) or 1
    out["A3_S"] = 2 * (r1 / n1) + (r2 / n2)

    # A1 magnitude banding (percentage-valued variables only)
    BANDABLE = {"1.3", "1.4", "1.5", "1.6", "2.1", "2.3", "2.4"}
    b1 = sum(band(v[k][1]) if k in BANDABLE and v[k][1] is not None
             else (v[k][0] or 0) for k in L1_VARS)
    b2 = sum(band(v[k][1]) if k in BANDABLE and v[k][1] is not None
             else (v[k][0] or 0) for k in L2_VARS)
    out["A1_S"] = 2 * b1 + b2

    # B block voting
    blk = 0
    for members in BLOCKS.values():
        vs = [v[m][0] for m in members if v[m][0] is not None]
        blk += s(sum(vs)) if vs else 0
    out["B_L1"] = blk
    out["B_S"] = 2 * blk + majority(c2)
    return out, v


# --------------------------------------------------------------- outcomes
def realized(h, t, ndays, rthr):
    rows = h.px["SPY"]
    ds = [r[0] for r in rows]
    i = bisect.bisect_right(ds, t) - 1
    end = t + timedelta(days=ndays)
    if end > ds[-1]:
        return None
    j = bisect.bisect_right(ds, end) - 1
    if j <= i:
        return None
    c0 = rows[i][3]
    seg = [r[3] for r in rows[i + 1:j + 1]]
    R = rows[j][3] / c0 - 1.0
    D = 1.0 - min(seg) / c0
    U = max(seg) / c0 - 1.0
    if R >= rthr and D < 0.05:
        return "UP"
    if R <= -rthr and U < 0.05:
        return "DOWN"
    return "CHOP"


def evaluate(rows, key, ndays_key):
    """Hit rate for a scheme, plus the always-UP baseline on the same rows."""
    ok = [r for r in rows if r[ndays_key]]
    if not ok:
        return None
    hits = sum(1 for r in ok if r[key] == r[ndays_key])
    base = sum(1 for r in ok if r[ndays_key] == "UP")
    dis = sum(1 for r in ok if r[key] != "UP")
    return {"n": len(ok), "hit": 100.0 * hits / len(ok),
            "base": 100.0 * base / len(ok),
            "disagree": 100.0 * dis / len(ok),
            "calls": Counter(r[key] for r in ok)}


def build(h, a, b):
    rows = []
    for t in h.call_dates(a, b):
        sc, _ = score_all(h, t)
        rec = dict(sc)
        rec["t"] = t
        rec["r60"] = realized(h, t, 60, 0.03)
        rec["r120"] = realized(h, t, 120, 0.05)
        rows.append(rec)
    return rows


def apply_threshold(rows, sk, thr):
    """Turn a shadow score into calls at a given symmetric threshold."""
    for r in rows:
        v = r[sk]
        r["_tmp"] = call_from(3 if v >= thr else (-3 if v <= -thr else 0),
                              r["chop"])
    return "_tmp"


def nonoverlap(rows, ndays):
    """Subsample so forward windows do not overlap. stride in weeks."""
    stride = int(math.ceil(ndays / 7.0)) + 1
    return rows[::stride]


if __name__ == "__main__":
    h = Harness()
    SWEEP = {"A1_S": range(2, 15), "A2_S": range(2, 13), "B_S": range(2, 9)}

    for name, a, b in SEGMENTS:
        if name.startswith("S1"):
            continue                      # needs the Wyckoff harvest
        rows = build(h, a, b)
        print("=" * 78)
        print(f"{name}   {a} -> {b}   {len(rows)} call dates")
        print("=" * 78)
        sd = Counter(r["live_S"] for r in rows)
        print(f"  live S distribution: {dict(sorted(sd.items()))}")
        print(f"  L1 chop flag set: {sum(1 for r in rows if r['chop'])}"
              f"/{len(rows)}")

        for horizon, nd in (("r60", 60), ("r120", 120)):
            sub = nonoverlap(rows, nd)
            e_full = evaluate(rows, "live", horizon)
            e_sub = evaluate(sub, "live", horizon)
            if not e_full:
                continue
            print(f"  --- {horizon} ---   overlapping n={e_full['n']}   "
                  f"NON-OVERLAPPING n={e_sub['n'] if e_sub else 0} "
                  f"(stride {int(math.ceil(nd/7.0))+1}w)")
            print(f"    {'scheme':10s} {'hit%':>6s} {'base%':>6s} {'edge':>7s}"
                  f" | {'NOL hit%':>8s} {'NOL base%':>9s} {'NOL edge':>8s}"
                  f"  disagree%")
            # live
            print(f"    {'live':10s} {e_full['hit']:6.1f} {e_full['base']:6.1f}"
                  f" {e_full['hit']-e_full['base']:+7.1f} |"
                  f" {e_sub['hit']:8.1f} {e_sub['base']:9.1f}"
                  f" {e_sub['hit']-e_sub['base']:+8.1f}"
                  f"  {e_full['disagree']:9.1f}")
            # shadows: report the BEST threshold, and say so
            for sk, rng in SWEEP.items():
                best = None
                for thr in rng:
                    k = apply_threshold(rows, sk, thr)
                    ev = evaluate(rows, k, horizon)
                    if ev and (best is None or ev["hit"] > best[1]["hit"]):
                        best = (thr, ev)
                if not best:
                    continue
                thr, ev = best
                k = apply_threshold(sub, sk, thr)
                evs = evaluate(sub, k, horizon)
                lbl = f"{sk[:2]}@{thr}"
                print(f"    {lbl:10s} {ev['hit']:6.1f} {ev['base']:6.1f}"
                      f" {ev['hit']-ev['base']:+7.1f} |"
                      f" {evs['hit']:8.1f} {evs['base']:9.1f}"
                      f" {evs['hit']-evs['base']:+8.1f}"
                      f"  {ev['disagree']:9.1f}   <- best-of-{len(list(rng))}"
                      f" threshold, IN-SAMPLE")
        print()
