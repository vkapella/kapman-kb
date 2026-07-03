"""Option-P&L extension study (read-only; imports v2 backtest libs).

Adds what backtest/option_pnl.py does not cover:
  1. REGIME-FLIP exit in option space (the exit regime_trade.py showed works on
     the underlying) vs the fixed base-target/stop exit.
  2. Spring-entry calls (spring/shakeout detected_at inside accumulation-family
     ranges) with the flip exit -- the event class with the proven edge.
  3. IV-path sensitivity: flat IV=HV (option_pnl's assumption), vol crush
     (exit sigma = 0.85x entry), vol pop (1.15x), and rich entry (entry premium
     priced at 1.2x HV, exits repriced at 1.0x HV -- the "bought elevated IV,
     it normalized" case the KB's spread-mandate worries about).
  4. DTE 90 and 180, ATM strikes; bootstrap 95% CI on mean return.

Run:  .venv/bin/python econ_study.py [--cohort]   (cwd = kapman-polygon-mcp-v2)
"""
from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/Volumes/OWC Envoy Pro SX/App Development/kapman-polygon-mcp-v2")

from lib.wyckoff import WyckoffConfig, analyze  # noqa: E402
from backtest.calibrate_targets import load_universe, apply_filters  # noqa: E402
from backtest.markup_targets import _resolving_range, _onsets  # noqa: E402
from backtest.option_pnl import bs_call, hv, TRADING_TO_CAL  # noqa: E402

HORIZON = 60          # bars cap for every exit style (parity with option_pnl)
BULL = {"accumulation", "reaccumulation", "markup"}
LONG_EVENTS = {"spring", "shakeout"}

# (label, entry_iv_mult, exit_iv_mult): sigma used to price entry / exit.
IV_PATHS = (
    ("flat",        1.00, 1.00),   # option_pnl.py assumption
    ("crush15",     1.00, 0.85),   # IV drifts down 15% while held
    ("pop15",       1.00, 1.15),   # IV expands 15%
    ("rich_entry",  1.20, 1.00),   # paid 1.2x HV going in, normalized at exit
)


def _boot_ci(rets: np.ndarray, n_boot: int = 3000, seed: int = 7) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = [rng.choice(rets, size=len(rets), replace=True).mean() for _ in range(n_boot)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _exit_bar_flip(regime: np.ndarray, start: int, n: int) -> int:
    """First bar >= start where regime leaves the bull set (or last bar)."""
    j = start
    while j < n - 1 and regime[j] in BULL:
        j += 1
    return j


def _price_call(S, K, dte_left_bars, dte0, sig):
    t = max(0.0, (dte0 - dte_left_bars * TRADING_TO_CAL) / 365.0)
    return bs_call(S, K, t, sig), t


def _simulate(entry_i, exit_style, regime, c, hi, lo, rng_obj, dte0, iv_entry_mult,
              iv_exit_mult, n):
    """One call trade entered at close of entry_i (strike ATM there).
    Returns premium-normalized return or None."""
    S0 = float(c[entry_i])
    sig0 = hv(c, entry_i)
    if sig0 is None:
        return None
    sig_in = sig0 * iv_entry_mult
    prem = bs_call(S0, S0, dte0 / 365.0, sig_in)
    if prem <= 0:
        return None
    K = S0

    if exit_style == "flip":
        xb = _exit_bar_flip(regime, entry_i + 1, n)
        hold = min(xb + 1 - entry_i, HORIZON)                     # exit at next open ~ close proxy
        hold = max(hold, 1)
        xi = min(entry_i + hold, n - 1)
        sig_path = sig0 * (iv_exit_mult + (iv_entry_mult - iv_exit_mult) * 0.0)
        exit_call, _ = _price_call(float(c[xi]), K, hold, dte0, sig_path)
        return (exit_call - prem) / prem

    # fixed target/stop exit (parity with option_pnl.py, but IV path applied)
    if rng_obj is None:
        return None
    base = rng_obj.resistance + 1.0 * rng_obj.height
    stop_px = S0 * 0.90
    for i in range(1, HORIZON + 1):
        if entry_i + i >= n:
            break
        frac = i / HORIZON
        sig_i = sig0 * (iv_entry_mult + (iv_exit_mult - iv_entry_mult) * frac)
        if hi[entry_i + i] >= base:
            ec, _ = _price_call(base, K, i, dte0, sig_i)
            return (ec - prem) / prem
        if lo[entry_i + i] <= stop_px:
            ec, _ = _price_call(stop_px, K, i, dte0, sig_i)
            return (ec - prem) / prem
        t_left = (dte0 - i * TRADING_TO_CAL)
        if t_left <= 0:
            return (max(0.0, float(c[entry_i + i]) - K) - prem) / prem
    xi = min(entry_i + HORIZON, n - 1)
    sig_f = sig0 * iv_exit_mult
    ec, _ = _price_call(float(c[xi]), K, HORIZON, dte0, sig_f)
    return (ec - prem) / prem


def measure(data, cfg, dte0):
    res = defaultdict(list)
    for sym, df in data.items():
        a = analyze(df, cfg)
        regime = a.timeline["regime"].astype(str).values
        c, hi, lo = df["close"].values, df["high"].values, df["low"].values
        n = len(df)
        onsets = [t for t in _onsets(regime, "markup") if t + 1 + HORIZON < n]
        springs = []
        for e in a.events:
            if (e.type in LONG_EVENTS and e.direction == "bullish"
                    and e.details.get("range_type") in ("accumulation", "reaccumulation")
                    and e.detected_at + 2 < n and e.detected_at + 1 + HORIZON < n):
                springs.append(e.detected_at)
        for iv_label, m_in, m_out in IV_PATHS:
            for t in onsets:
                r = _resolving_range(a.ranges, t)
                v = _simulate(t + 1, "target", regime, c, hi, lo, r, dte0, m_in, m_out, n)
                if v is not None:
                    res[("markup", "target/stop", iv_label)].append(v)
                v = _simulate(t + 1, "flip", regime, c, hi, lo, r, dte0, m_in, m_out, n)
                if v is not None:
                    res[("markup", "flip", iv_label)].append(v)
            for t0 in springs:
                v = _simulate(t0 + 1, "flip", regime, c, hi, lo, None, dte0, m_in, m_out, n)
                if v is not None:
                    res[("spring", "flip", iv_label)].append(v)
    return res


def report(res, title, dte0):
    print(f"\n=== ATM LONG CALL, DTE={dte0}  [{title}] ===")
    print(f"{'entry':8s}{'exit':13s}{'iv path':11s}{'n':>6}{'win%':>6}{'mean':>8}"
          f"{'med':>8}{'PF':>7}{'CI(mean)':>18}")
    for key in sorted(res):
        rs = np.array(res[key])
        if len(rs) < 5:
            continue
        w, l = rs[rs > 0], rs[rs <= 0]
        pf = (w.sum() / -l.sum()) if l.sum() < 0 else float("inf")
        lo_ci, hi_ci = _boot_ci(rs)
        pfs = "inf" if pf == float("inf") else f"{pf:.2f}"
        print(f"{key[0]:8s}{key[1]:13s}{key[2]:11s}{len(rs):>6}{100*(rs>0).mean():>5.0f}%"
              f"{rs.mean()*100:>+7.0f}%{np.median(rs)*100:>+7.0f}%{pfs:>7}"
              f"   [{lo_ci*100:+.0f}%, {hi_ci*100:+.0f}%]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", action="store_true")
    ap.add_argument("--pool", action="store_true")
    ap.add_argument("--csv")
    ap.add_argument("--tickers")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--min-price", type=float, default=0.0)
    ap.add_argument("--min-adv", type=float, default=0.0)
    ap.add_argument("--min-bars", type=int, default=300)
    args = ap.parse_args()
    cfg = WyckoffConfig()
    data, _ = apply_filters(load_universe(args), args)
    title = "cohort" if args.cohort else "battery"
    print(f"measuring {len(data)} tickers  [{title}] ...")
    for dte in (90, 180):
        report(measure(data, cfg, dte), title, dte)


if __name__ == "__main__":
    main()
