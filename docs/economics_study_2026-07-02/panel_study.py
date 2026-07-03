"""Live forward-panel analysis from the operator's raw-records CSV export.

Reconstructs onsets exactly like viewer forward_eval (regime flip into
markup/markdown between consecutive snapshots), fetches true forward OHLC from
Polygon, and measures:
  - onset inventory (direction, context, resolution speed)
  - up-base touch (unconditional) vs the 10%-stop race  -> quantifies the
    resolved-subsample bias in the UI calibration table
  - regime-flip exit returns, split BY DIRECTION (and a leaves-bull variant)
  - segmentation: conviction buckets, pt_calibration context, phase
  - live vs fresh-backtest touch-curve comparison uses matched short windows
    (computed separately in touch_curve.py)

Limitations of this export: no pt_down_* tiers (markdown onsets: stop/MAE/flip
only), no conservative/stretch tiers, no dealer fields.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import numpy as np

SCRATCH = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRATCH, "forward_records.csv")
OHLC_CACHE = os.path.join(SCRATCH, "panel_ohlc.json")
ONSETS_OUT = os.path.join(SCRATCH, "live_onsets.csv")
END_DATE = "2026-07-02"
STOP_PCT = 0.10

# ---------- load panel ----------
rows = []
with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append(r)

def pf(x):
    x = (x or "").replace("%", "").strip()
    return float(x) if x else None

panel = defaultdict(list)  # sym -> [(date, regime, row)]
for r in rows:
    panel[r["Symbol"]].append((r["Log Date"], r["Regime"].strip(), r))
for sym in panel:
    panel[sym].sort(key=lambda t: t[0])

dates_all = sorted({r["Log Date"] for r in rows})
print(f"panel: {len(rows)} rows, {len(panel)} symbols, "
      f"{len(dates_all)} snapshot days {dates_all[0]}..{dates_all[-1]}")

# ---------- reconstruct onsets ----------
onsets = []
for sym, series in panel.items():
    for i in range(1, len(series)):
        d, reg, row = series[i]
        prev = series[i - 1][1]
        for target, up in (("markup", True), ("markdown", False)):
            if reg == target and prev != target:
                # flip-exit: first later snapshot whose regime leaves the onset regime
                exit_date, exit_leaves_bull = None, None
                BULL = {"accumulation", "reaccumulation", "markup"}
                for j in range(i + 1, len(series)):
                    if series[j][1] != target and exit_date is None:
                        exit_date = series[j][0]
                    if up and series[j][1] not in BULL and exit_leaves_bull is None:
                        exit_leaves_bull = series[j][0]
                    if exit_date and (not up or exit_leaves_bull):
                        break
                onsets.append({
                    "symbol": sym, "onset_date": d, "dir": "up" if up else "down",
                    "regime": target, "prev_regime": prev,
                    "context": row["PT Calibration"].strip() or None,
                    "conviction": pf(row["Conviction"]),
                    "regime_conf": pf(row["Regime Confidence"]),
                    "phase": row["Phase"].strip() or None,
                    "tags": row["Setup Tags"].strip(),
                    "snap_price": pf(row["Price"]),
                    "up_base": pf(row["Up Base"]),
                    "up_base_prob": pf(row["Up Base Prob"]),
                    "invalidation": pf(row["Invalidation"]),
                    "exit_flip_date": exit_date,
                    "exit_bull_date": exit_leaves_bull if up else None,
                })

ups = [o for o in onsets if o["dir"] == "up"]
downs = [o for o in onsets if o["dir"] == "down"]
print(f"onsets: {len(onsets)} total ({len(ups)} up, {len(downs)} down), "
      f"{len({o['symbol'] for o in onsets})} symbols, "
      f"flip-closed: {sum(1 for o in onsets if o['exit_flip_date'])}")

# ---------- fetch OHLC ----------
def _read_key():
    for line in open("/Volumes/OWC Envoy Pro SX/App Development/kapman-polygon-mcp-v2/.env"):
        line = line.strip()
        if line.startswith("POLYGON_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("no POLYGON_API_KEY")

def fetch(sym, key):
    url = (f"https://api.polygon.io/v2/aggs/ticker/{sym}/range/1/day/"
           f"2026-06-13/{END_DATE}?adjusted=true&sort=asc&limit=120&apiKey={key}")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.load(resp)
            bars = [{"d": date.fromtimestamp(b["t"] / 1000).isoformat(),
                     "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"]}
                    for b in data.get("results", [])]
            return sym, bars
        except Exception:
            time.sleep(2 * (attempt + 1))
    return sym, []

need = sorted({o["symbol"] for o in onsets})
if os.path.exists(OHLC_CACHE):
    ohlc = json.load(open(OHLC_CACHE))
else:
    ohlc = {}
missing = [s for s in need if s not in ohlc]
if missing:
    key = _read_key()
    with ThreadPoolExecutor(max_workers=5) as ex:
        for sym, bars in ex.map(lambda s: fetch(s, key), missing):
            ohlc[sym] = bars
    json.dump(ohlc, open(OHLC_CACHE, "w"))
empty = [s for s in need if not ohlc.get(s)]
print(f"ohlc: {len(need)} symbols needed, {len(empty)} failed/empty {empty[:8]}")

# ---------- measure ----------
def bars_after(sym, d):
    return [b for b in ohlc.get(sym, []) if b["d"] > d]

for o in onsets:
    fwd = bars_after(o["symbol"], o["onset_date"])
    o["fwd_bars"] = len(fwd)
    if not fwd:
        continue
    entry = fwd[0]["o"]
    o["entry"] = entry
    up = o["dir"] == "up"
    his = [b["h"] for b in fwd]; los = [b["l"] for b in fwd]
    o["mae_pct"] = round(100 * ((entry - min(los)) / entry if up
                                else (max(his) - entry) / entry), 2)
    o["mfe_pct"] = round(100 * ((max(his) - entry) / entry if up
                                else (entry - min(los)) / entry), 2)
    # up-base touch + stop race (up onsets only; export has no down targets)
    if up and o["up_base"]:
        stop = entry * (1 - STOP_PCT)
        tb = next((i for i, b in enumerate(fwd) if b["h"] >= o["up_base"]), None)
        sb = next((i for i, b in enumerate(fwd) if b["l"] <= stop), None)
        o["base_touch"] = tb is not None
        o["base_touch_bar"] = tb
        o["stop_bar"] = sb
        if tb is not None and (sb is None or tb <= sb):
            o["race"] = "hit_base"
        elif sb is not None:
            o["race"] = "stopped"
        else:
            o["race"] = "in_flight"
        # UI-style status vs unconditional touch (bias quantification)
        o["stopped_then_touched"] = (o["race"] == "stopped" and tb is not None)
    # flip exits (directional return)
    for fld, dcol in (("flip_ret", "exit_flip_date"), ("bull_ret", "exit_bull_date")):
        xd = o.get(dcol)
        if xd:
            after = [b for b in ohlc.get(o["symbol"], []) if b["d"] > xd]
            if after:
                xp = after[0]["o"]
                r = (xp - entry) / entry if up else (entry - xp) / entry
                o[fld] = round(100 * r, 2)
                o[fld.replace("_ret", "_hold")] = sum(1 for b in fwd if b["d"] <= xd)

# ---------- report ----------
def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    ctr = p + z * z / (2 * n)
    rad = z * math_sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((ctr - rad) / den, (ctr + rad) / den)

from math import sqrt as math_sqrt  # noqa: E402

def seg_table(items, keyfn, title, valfn=lambda o: o.get("race") == "hit_base",
              elig=lambda o: o.get("race") in ("hit_base", "stopped")):
    print(f"\n--- {title} ---")
    groups = defaultdict(list)
    for o in items:
        groups[keyfn(o)].append(o)
    for g in sorted(groups, key=lambda x: str(x)):
        os_ = [o for o in groups[g] if elig(o)]
        n = len(os_)
        alln = len(groups[g])
        if alln == 0:
            continue
        k = sum(1 for o in os_ if valfn(o))
        lo, hi = wilson(k, n) if n else (0, 0)
        fr = [o["flip_ret"] for o in groups[g] if o.get("flip_ret") is not None]
        mfr = f"{np.median(fr):+.1f}%" if fr else "  --"
        print(f"  {str(g):24s} n_all={alln:>3} resolved={n:>3} hit={k:>3}"
              f" rate={100*k/max(n,1):>4.0f}% CI[{100*lo:.0f},{100*hi:.0f}]"
              f" medFlipRet={mfr}")

print("\n================ LIVE PANEL MEASURES ================")
res_up = [o for o in ups if o.get("race")]
resolved = [o for o in res_up if o["race"] in ("hit_base", "stopped")]
inflight = [o for o in res_up if o["race"] == "in_flight"]
print(f"up onsets with base target: {len(res_up)}  resolved={len(resolved)} "
      f"in_flight={len(inflight)}")
if resolved:
    hits = sum(1 for o in resolved if o["race"] == "hit_base")
    print(f"resolved base-hit rate: {hits}/{len(resolved)} = {100*hits/len(resolved):.0f}%")
    stt = sum(1 for o in res_up if o.get("stopped_then_touched"))
    print(f"stopped-but-later-touched-base (bias cases): {stt}")
    pred = [o["up_base_prob"] for o in resolved if o["up_base_prob"]]
    print(f"engine predicted base prob (resolved cohort mean): {np.mean(pred):.0f}%")
    un_t = sum(1 for o in res_up if o.get("base_touch"))
    print(f"unconditional base-touch so far (all up onsets w/ target): "
          f"{un_t}/{len(res_up)} = {100*un_t/len(res_up):.0f}%")
    wl = [o["fwd_bars"] for o in res_up]
    print(f"forward window bars: median {np.median(wl):.0f}, max {max(wl)}")
    rb = [o["base_touch_bar"] for o in res_up if o.get("base_touch_bar") is not None]
    sb = [o["stop_bar"] for o in res_up if o.get("stop_bar") is not None]
    if rb: print(f"touch speed: median {np.median(rb):.0f} bars; stop speed: "
                 f"median {np.median(sb):.0f} bars (n={len(sb)})")

for d in ("up", "down"):
    fr = [o["flip_ret"] for o in onsets if o["dir"] == d and o.get("flip_ret") is not None]
    if fr:
        print(f"\nflip-exit ({d}, n={len(fr)}): mean {np.mean(fr):+.1f}%  "
              f"median {np.median(fr):+.1f}%  win {100*np.mean([x>0 for x in fr]):.0f}%")
br = [o["bull_ret"] for o in onsets if o.get("bull_ret") is not None]
if br:
    print(f"leaves-BULL exit (up, n={len(br)}): mean {np.mean(br):+.1f}%  "
          f"median {np.median(br):+.1f}%  win {100*np.mean([x>0 for x in br]):.0f}%")

def conv_bucket(o):
    c = o.get("conviction")
    if c is None: return "unknown"
    return "high>=66" if c >= 66 else ("med33-66" if c >= 33 else "low<33")

seg_table(res_up, lambda o: o.get("context"), "UP onsets by context (base-hit race)")
seg_table(res_up, conv_bucket, "UP onsets by conviction bucket")
seg_table(res_up, lambda o: o.get("phase") or "?", "UP onsets by phase")

md = [o for o in downs if o.get("entry")]
if md:
    print(f"\nmarkdown onsets (no targets in export): n={len(md)}  "
          f"median MAE {np.median([o['mae_pct'] for o in md]):.1f}%  "
          f"median MFE {np.median([o['mfe_pct'] for o in md]):.1f}%")

# dump per-onset CSV for operator review
flds = ["symbol", "onset_date", "dir", "prev_regime", "context", "phase",
        "conviction", "regime_conf", "tags", "entry", "up_base", "up_base_prob",
        "fwd_bars", "race", "base_touch", "base_touch_bar", "stop_bar",
        "stopped_then_touched", "mae_pct", "mfe_pct", "exit_flip_date",
        "flip_ret", "flip_hold", "bull_ret", "invalidation"]
with open(ONSETS_OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=flds, extrasaction="ignore")
    w.writeheader()
    for o in sorted(onsets, key=lambda x: (x["onset_date"], x["symbol"])):
        w.writerow(o)
print(f"\nper-onset detail written: {ONSETS_OUT}")
