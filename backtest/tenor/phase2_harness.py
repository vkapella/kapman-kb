#!/usr/bin/env python3
"""
Phase 2 — point-in-time harness for the Swing Tenor Scan backtest.

Provides as-of accessors that CANNOT return data published after the call
date, plus a coverage/lookahead validation report.

Lookahead rules enforced here:
  * COT   : CFTC publishes Friday ~15:30 ET for the prior Tuesday. A report
            dated Tuesday T is available from T+3 (that Friday). Runs happen
            after Friday close (16:00 ET), so the same-Friday publication IS
            available. Rule: report_date + 3 days <= call_date.
  * Rates : Treasury posts the par yield curve ~15:30 ET same day. Latest
            row dated <= call_date.
  * Vol   : CBOE index closes, dated <= call_date.
  * Price : daily closes dated <= call_date; weekly bars are the last
            trading day of each ISO week.
  * 52-wk high (1.3): trailing window only, never forward.

Run:  python3 phase2_harness.py
"""
import csv, json, os, sys, bisect
from datetime import date, timedelta
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

SYMBOLS = ["SPY", "QQQ", "IWM", "RSP", "XLY", "XLP",
           "HYG", "LQD", "UUP", "GLD", "CPER", "COPX"]


def _d(s):
    return date(*map(int, s.split("-")))


# ---------------------------------------------------------------- loaders
def load_prices(sym):
    p = os.path.join(DATA, f"{sym.lower()}_daily_schwab.csv")
    if not os.path.exists(p):
        return None
    out = []
    with open(p) as f:
        for r in csv.DictReader(f):
            out.append((_d(r["date"]), float(r["high"]), float(r["low"]),
                        float(r["close"])))
    out.sort()
    return out


def load_cboe(fn):
    out = []
    with open(os.path.join(DATA, fn)) as f:
        rd = csv.reader(f)
        next(rd)
        for r in rd:
            if not r or not r[0]:
                continue
            m, dd, y = r[0].split("/")
            try:
                out.append((date(int(y), int(m), int(dd)), float(r[-1])))
            except ValueError:
                continue
    out.sort()
    return out


def _load_fred(series):
    out = {}
    with open(os.path.join(DATA, f"fred_{series}.csv")) as f:
        for r in csv.DictReader(f):
            v = r[series]
            if v in (".", "", None):     # FRED marks holidays with "."
                continue
            out[_d(r["observation_date"])] = float(v)
    return out


def load_treasury():
    """
    2y / 10y constant-maturity yields from FRED (Federal Reserve).

    NOT parsed from the concatenated Treasury.gov par-yield CSV. That file is
    unusable when years are appended blind: Treasury has added columns over
    time (12 cols 2006-2017 -> 13 in 2018 -> 14 in 2022 -> 15 in 2025, as
    1.5-month, 2-month and 4-month bills were introduced), so a fixed header
    silently reads the wrong tenor for recent rows. That bug produced a 10y of
    4.24 (actually the 3-year) against a true 4.68 on 2026-08-14 -- a 44bp
    error that would have corrupted 2.2 across the whole backtest.

    Per-year files are kept under data/treasury_by_year/ as an independent
    cross-check; see cross_check_treasury().
    """
    y2, y10 = _load_fred("DGS2"), _load_fred("DGS10")
    return sorted((d, y2[d], y10[d]) for d in set(y2) & set(y10))


def cross_check_treasury(tsy, tol=0.02):
    """Validate FRED against Treasury.gov, parsing each year's own header."""
    import glob
    fred = {d: (a, b) for d, a, b in tsy}
    checked = bad = 0
    for p in sorted(glob.glob(os.path.join(DATA, "treasury_by_year", "*.csv"))):
        with open(p) as f:
            for r in csv.DictReader(f):          # per-file header: correct
                try:
                    m, dd, y = r["Date"].split("/")
                    d = date(int(y), int(m), int(dd))
                    t2, t10 = float(r["2 Yr"]), float(r["10 Yr"])
                except (ValueError, KeyError, TypeError):
                    continue
                if d not in fred:
                    continue
                checked += 1
                f2, f10 = fred[d]
                if abs(f2 - t2) > tol or abs(f10 - t10) > tol:
                    bad += 1
    return checked, bad


def load_cot():
    rows = json.load(open(os.path.join(DATA, "cftc_tff_emini_sp500.json")))
    out = []
    for r in rows:
        try:
            out.append((_d(r["report_date_as_yyyy_mm_dd"][:10]),
                        int(r["lev_money_positions_long"]),
                        int(r["lev_money_positions_short"]),
                        int(r["open_interest_all"])))
        except (KeyError, TypeError, ValueError):
            continue
    out.sort()
    return out


# ---------------------------------------------------------- as-of lookups
def asof(series, t, lag_days=0):
    """Latest element of `series` whose date + lag_days <= t. None if none."""
    keys = [s[0] + timedelta(days=lag_days) for s in series]
    i = bisect.bisect_right(keys, t) - 1
    return series[i] if i >= 0 else None


class Harness:
    def __init__(self):
        self.px = {s: load_prices(s) for s in SYMBOLS}
        self.px = {k: v for k, v in self.px.items() if v}
        self.vix = load_cboe("cboe_vix.csv")
        self.vix3m = load_cboe("cboe_vix3m.csv")
        self.tsy = load_treasury()
        self.cot = load_cot()
        # weekly bars: last trading day of each ISO week, per symbol
        self.weekly = {}
        for s, rows in self.px.items():
            bw = defaultdict(list)
            for r in rows:
                bw[r[0].isocalendar()[:2]].append(r)
            self.weekly[s] = sorted((max(v)[0], max(v)[3]) for v in bw.values())

    # -- accessors; every one is strictly <= t
    def close(self, sym, t):
        r = asof(self.px.get(sym, []), t)
        return r[3] if r else None

    def weekly_close(self, sym, t, weeks_back=0):
        w = self.weekly.get(sym, [])
        i = bisect.bisect_right([x[0] for x in w], t) - 1
        j = i - weeks_back
        return w[j][1] if j >= 0 else None

    def ratio_13wk(self, a, b, t):
        """13-week change in the a/b ratio, as the runs compute it."""
        na, nb = self.weekly_close(a, t), self.weekly_close(b, t)
        oa, ob = self.weekly_close(a, t, 13), self.weekly_close(b, t, 13)
        if None in (na, nb, oa, ob) or not ob or not nb:
            return None
        now, then = na / nb, oa / ob
        return None if not then else (now / then - 1.0)

    def pct_13wk(self, sym, t):
        """13-week % change in a single series (2.3 UUP)."""
        now, then = self.weekly_close(sym, t), self.weekly_close(sym, t, 13)
        if now is None or not then:
            return None
        return now / then - 1.0

    def realized_vol(self, t):
        """1.7 — hv20 / hv60 from trailing daily log returns, annualized."""
        import math
        rows = self.px.get("SPY", [])
        i = bisect.bisect_right([r[0] for r in rows], t)
        if i < 61:
            return None
        cl = [r[3] for r in rows[:i]]
        rets = [math.log(cl[k] / cl[k - 1]) for k in range(1, len(cl))]

        def hv(n):
            s = rets[-n:]
            m = sum(s) / n
            var = sum((x - m) ** 2 for x in s) / (n - 1)
            return math.sqrt(var * 252)

        h20, h60 = hv(20), hv(60)
        return None if not h60 else {"hv20": h20, "hv60": h60,
                                     "ratio": h20 / h60}

    def vol_term(self, t):
        v, v3 = asof(self.vix, t), asof(self.vix3m, t)
        if not v or not v3 or not v[1]:
            return None
        if v[0] != v3[0]:            # publish-lag mismatch: use intersection
            return None
        return v3[1] / v[1] - 1.0

    def curve(self, t):
        now, then = asof(self.tsy, t), asof(self.tsy, t - timedelta(days=91))
        if not now or not then:
            return None
        return {"y10": now[2], "y2": now[1],
                "d10_13wk_bp": (now[2] - then[2]) * 100.0,
                "s2s10_bp": (now[2] - now[1]) * 100.0}

    def cot_asof(self, t):
        """CFTC publishes Fri ~15:30 ET for prior Tue -> 3-day lag."""
        r = asof(self.cot, t, lag_days=3)
        if not r:
            return None
        return {"report_date": r[0], "net": r[1] - r[2], "oi": r[3]}

    def high_52wk(self, sym, t):
        rows = self.px.get(sym, [])
        lo = t - timedelta(days=365)
        i = bisect.bisect_right([r[0] for r in rows], t)
        seg = [r[1] for r in rows[:i] if r[0] > lo]
        return max(seg) if seg else None

    def call_dates(self, start, end):
        w = self.weekly.get("SPY", [])
        return [d for d, _ in w if start <= d <= end]


# --------------------------------------------------------------- validate
# Boundaries are set by DATA AVAILABILITY, not round dates.
#   CPER  inception 2011-11-15 (+13wk warmup) -> 2.4 live from ~2012-02
#   VIX3M inception 2009-09-18                -> 1.6 live from 2009-09-18
# S1 deliberately OVERLAPS S2: it is the Wyckoff-inclusive overlay used to
# measure 1.1's marginal contribution. NEVER pool S1 with S2.
SEGMENTS = [
    ("S1 full-fidelity", date(2022, 8, 1),  date(2026, 8, 14)),
    ("S2 core",          date(2012, 2, 1),  date(2026, 8, 14)),
    ("S3 extended",      date(2009, 9, 18), date(2012, 2, 1)),
    ("S4 crisis",        date(2007, 7, 1),  date(2009, 9, 18)),
]

VARS = {
    "1.2 40wk MA":    lambda h, t: h.weekly_close("SPY", t, 40),
    "1.3 52wk high":  lambda h, t: h.high_52wk("SPY", t),
    "1.4 RSP/SPY":    lambda h, t: h.ratio_13wk("RSP", "SPY", t),
    "1.5 XLY/XLP":    lambda h, t: h.ratio_13wk("XLY", "XLP", t),
    "1.6 VIX3M/VIX":  lambda h, t: h.vol_term(t),
    "1.7 HV20/HV60":  lambda h, t: h.realized_vol(t),
    "2.1 HYG/LQD":    lambda h, t: h.ratio_13wk("HYG", "LQD", t),
    "2.2 curve":      lambda h, t: h.curve(t),
    "2.3 UUP":        lambda h, t: h.pct_13wk("UUP", t),
    "2.4 CPER/GLD":   lambda h, t: h.ratio_13wk("CPER", "GLD", t),
    "2.5 COT":        lambda h, t: h.cot_asof(t),
}

if __name__ == "__main__":
    h = Harness()
    print("=" * 78)
    print("LOADED")
    print("=" * 78)
    for s in sorted(h.px):
        r = h.px[s]
        print(f"  {s:5s} {len(r):5d} daily  {r[0][0]} -> {r[-1][0]}"
              f"   ({len(h.weekly[s])} weekly)")
    for nm, ser in (("VIX", h.vix), ("VIX3M", h.vix3m),
                    ("Treasury", h.tsy), ("COT", h.cot)):
        print(f"  {nm:9s} {len(ser):5d}  {ser[0][0]} -> {ser[-1][0]}")

    # ---- lookahead assertions
    print()
    print("=" * 78)
    print("LOOKAHEAD ASSERTIONS")
    print("=" * 78)
    fails = 0
    for t in h.call_dates(date(2010, 1, 1), date(2026, 8, 14))[::20]:
        c = h.cot_asof(t)
        if c and c["report_date"] + timedelta(days=3) > t:
            fails += 1
        for ser, nm in ((h.vix, "vix"), (h.vix3m, "vix3m"), (h.tsy, "tsy")):
            r = asof(ser, t)
            if r and r[0] > t:
                fails += 1
        for s in h.px:
            r = asof(h.px[s], t)
            if r and r[0] > t:
                fails += 1
    print(f"  violations across sampled call dates: {fails}")
    assert fails == 0, "LOOKAHEAD DETECTED"
    lags = [(t - h.cot_asof(t)["report_date"]).days
            for t in h.call_dates(date(2012, 1, 1), date(2026, 8, 14))
            if h.cot_asof(t)]
    print(f"  COT report age at call time: min {min(lags)}d  "
          f"median {sorted(lags)[len(lags)//2]}d  max {max(lags)}d")

    ck, bad = cross_check_treasury(h.tsy)
    print(f"  FRED vs Treasury.gov 2y/10y: {ck} dates compared, "
          f"{bad} disagreements > 2bp")

    # ---- coverage per segment
    print()
    print("=" * 78)
    print("COVERAGE BY SEGMENT  (% of call dates where the variable resolves)")
    print("=" * 78)
    hdr = f"  {'variable':16s}" + "".join(f"{s[0][:2]:>9s}" for s in SEGMENTS)
    print(hdr)
    for vn, fn in VARS.items():
        line = f"  {vn:16s}"
        for _, a, b in SEGMENTS:
            cds = h.call_dates(a, b)
            ok = sum(1 for t in cds if fn(h, t) is not None)
            line += f"{100.0*ok/max(len(cds),1):8.0f}%"
        print(line)
    print()
    for nm, a, b in SEGMENTS:
        print(f"  {nm:18s} {a} -> {b}   {len(h.call_dates(a,b)):4d} call dates")
