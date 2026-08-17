#!/usr/bin/env python3
"""
Phase 0 — realized tenor class distribution for SPY.

Classifies every weekly forward window per SWING_TENOR_SCAN_PILOT_v0.1 §6:
  UP   : R >= +3% (60d) / +5% (120d)  AND  max drawdown D < 5%
  DOWN : R <= -3% (60d) / -5% (120d)  AND  max run-up   U < 5%
  CHOP : anything else

Answers: what does the always-UP baseline actually score, and is the class
balance sane or degenerate?
"""
import json, sys, bisect
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict

SRC = sys.argv[1]

with open(SRC) as f:
    raw = json.load(f)
candles = raw["result"]["candles"]

bars = []
for c in candles:
    d = datetime.fromtimestamp(c["datetime"] / 1000, tz=timezone.utc).date()
    bars.append((d, c["high"], c["low"], c["close"]))
bars.sort(key=lambda r: r[0])

dates = [b[0] for b in bars]
high = [b[1] for b in bars]
low = [b[2] for b in bars]
close = [b[3] for b in bars]
idx = {d: i for i, d in enumerate(dates)}

print("=" * 74)
print("DATA INTEGRITY")
print("=" * 74)
print(f"bars              : {len(bars)}")
print(f"range             : {dates[0]} -> {dates[-1]}")
print(f"duplicate dates   : {len(dates) - len(set(dates))}")
print(f"malformed bars    : "
      f"{sum(1 for i in range(len(bars)) if close[i] <= 0 or high[i] < low[i])}")
gaps = [(dates[i-1], dates[i], (dates[i]-dates[i-1]).days)
        for i in range(1, len(dates)) if (dates[i]-dates[i-1]).days > 5]
print(f"gaps > 5 cal days : {len(gaps)}")
for g in gaps[:8]:
    print(f"      {g[0]} -> {g[1]}  ({g[2]}d)")

# weekly call dates = last trading day of each ISO week
byweek = defaultdict(list)
for d in dates:
    byweek[d.isocalendar()[:2]].append(d)
call_dates = sorted(max(v) for v in byweek.values())
call_dates = [d for d in call_dates if d >= datetime(2010, 1, 1).date()]
print(f"weekly call dates : {len(call_dates)}  ({call_dates[0]} -> {call_dates[-1]})")


def classify(t, ndays, rthr, use_intraday, dthr=0.05):
    """Return (class, R, D, U) or None if the forward window is incomplete."""
    i = idx[t]
    end = t + timedelta(days=ndays)
    if end > dates[-1]:
        return None
    j = bisect.bisect_right(dates, end) - 1
    if j <= i:
        return None
    c0 = close[i]
    seg_lo = low[i+1:j+1] if use_intraday else close[i+1:j+1]
    seg_hi = high[i+1:j+1] if use_intraday else close[i+1:j+1]
    R = close[j] / c0 - 1.0
    D = 1.0 - min(seg_lo) / c0       # max drawdown, positive
    U = max(seg_hi) / c0 - 1.0       # max run-up, positive
    if R >= rthr and D < dthr:
        k = "UP"
    elif R <= -rthr and U < dthr:
        k = "DOWN"
    else:
        k = "CHOP"
    return k, R, D, U


def report(ndays, rthr, use_intraday, label):
    rows = []
    for t in call_dates:
        r = classify(t, ndays, rthr, use_intraday)
        if r:
            rows.append((t,) + r)
    n = len(rows)
    cnt = Counter(r[1] for r in rows)
    print()
    print("=" * 74)
    print(f"{label}   (n={n} weekly windows)")
    print("=" * 74)
    for k in ("UP", "CHOP", "DOWN"):
        print(f"  {k:5s} {cnt[k]:5d}   {100.0*cnt[k]/n:5.1f}%")
    print(f"  --> ALWAYS-UP BASELINE HIT RATE = {100.0*cnt['UP']/n:.1f}%")

    ret_ok = [r for r in rows if r[2] >= rthr]
    dd_killed = [r for r in ret_ok if r[3] >= 0.05]
    print(f"  met the RETURN bar (R >= {rthr:+.0%}) : {len(ret_ok):4d}  "
          f"({100.0*len(ret_ok)/n:.1f}% of windows)")
    print(f"     of those, killed by D >= 5%   : {len(dd_killed):4d}  "
          f"({100.0*len(dd_killed)/max(len(ret_ok),1):.1f}% of them)")

    print("  UP rate if the drawdown gate were:")
    for dthr in (0.03, 0.05, 0.07, 0.10, 1.00):
        u = sum(1 for r in rows if r[2] >= rthr and r[3] < dthr)
        tag = "(no gate)" if dthr == 1.00 else ""
        print(f"     D < {dthr:4.0%} {tag:9s} -> UP {100.0*u/n:5.1f}%")

    print("  by year   UP / CHOP / DOWN")
    peryear = defaultdict(Counter)
    for r in rows:
        peryear[r[0].year][r[1]] += 1
    for y in sorted(peryear):
        c = peryear[y]
        tot = sum(c.values())
        print(f"     {y}   {c['UP']:3d} / {c['CHOP']:3d} / {c['DOWN']:3d}"
              f"    (UP {100.0*c['UP']/tot:3.0f}%)")
    return rows, cnt, n


print("\n\n########  PRIMARY: drawdown / run-up measured on CLOSES  ########")
report(60, 0.03, False, "60-DAY WINDOW   R>=+3%, D<5%")
report(120, 0.05, False, "120-DAY WINDOW  R>=+5%, D<5%")

print("\n\n########  SENSITIVITY: measured on INTRADAY LOWS / HIGHS  ########")
report(60, 0.03, True, "60-DAY WINDOW   (intraday)")
report(120, 0.05, True, "120-DAY WINDOW  (intraday)")

print()
print("=" * 74)
print("DIVIDEND SENSITIVITY")
print("=" * 74)
print("Schwab candles are a price series, so R above is PRICE return.")
print("SPY yields ~1.2%/yr => ~+0.20% over 60d, ~+0.40% over 120d.")
for ndays, rthr, add, lbl in ((60, 0.03, 0.0020, "60d"), (120, 0.05, 0.0040, "120d")):
    rows = [classify(t, ndays, rthr, False) for t in call_dates]
    rows = [r for r in rows if r]
    up_price = sum(1 for r in rows if r[0] == "UP")
    up_total = sum(1 for r in rows if r[1] + add >= rthr and r[2] < 0.05)
    print(f"  {lbl:5s}: UP {100.0*up_price/len(rows):5.1f}% (price return)"
          f"  ->  {100.0*up_total/len(rows):5.1f}% (approx total return)")
