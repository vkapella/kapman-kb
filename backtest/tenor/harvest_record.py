#!/usr/bin/env python3
"""
Record a Wyckoff `as_of` scan into the resumable harvest cache.

The scans are the ONLY backtest input that expires: kapman-polygon serves a
rolling ~5-year window, so these become unretrievable as it advances. The
cache is append-only and keyed on (as_of, symbol); re-recording is a no-op.

Usage:  python3 harvest_record.py < scan.json
        python3 harvest_record.py --status
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "data", "wyckoff", "scans.jsonl")
MANIFEST = os.path.join(HERE, "data", "wyckoff", "_manifest.json")

# Only the fields variable 1.1 actually reads, plus provenance.
def extract(d):
    cs = d.get("current_state", {})
    wc = cs.get("weekly_context", {}) or {}
    md = d.get("metadata", {}) or {}
    rng = cs.get("range") or {}
    return {
        "as_of": d.get("as_of"),
        "symbol": d.get("symbol"),
        "regime": cs.get("regime"),
        "regime_confidence": cs.get("regime_confidence"),
        "phase": cs.get("phase"),
        "phase_confidence": cs.get("phase_confidence"),
        "range_low": rng.get("low") if isinstance(rng, dict) else None,
        "range_high": rng.get("high") if isinstance(rng, dict) else None,
        "weekly_trend": wc.get("trend"),
        "weekly_regime_hint": wc.get("regime_hint"),
        "close_vs_30w": wc.get("close_vs_30w"),
        "bars_analyzed": md.get("bars_analyzed"),
        "engine_version": md.get("engine_version"),
        "config_hash": md.get("config_hash"),
    }


def load_done():
    done = set()
    if os.path.exists(CACHE):
        for ln in open(CACHE):
            try:
                r = json.loads(ln)
                done.add((r["as_of"], r["symbol"]))
            except Exception:
                continue
    return done


def status():
    m = json.load(open(MANIFEST))
    done = load_done()
    todo = [(d, s) for d in m["call_dates"] for s in m["symbols"]]
    rem = [x for x in todo if x not in done]
    print(f"harvest: {len(done)}/{len(todo)} recorded, {len(rem)} remaining")
    if rem:
        print("next:", rem[:9])
    # engine drift check
    vers = set()
    if os.path.exists(CACHE):
        for ln in open(CACHE):
            r = json.loads(ln)
            vers.add((r.get("engine_version"), r.get("config_hash")))
    if len(vers) > 1:
        print(f"!! ENGINE DRIFT across cached scans: {vers}")
    elif vers:
        print(f"engine pinned: {vers.pop()}")


if __name__ == "__main__":
    if "--status" in sys.argv:
        status()
        sys.exit(0)
    d = json.load(sys.stdin)
    if "error" in d:
        print(f"skip (producer error): {d.get('symbol')} {d['error'][:60]}")
        sys.exit(0)
    rec = extract(d)
    if (rec["as_of"], rec["symbol"]) in load_done():
        print(f"already recorded: {rec['symbol']} {rec['as_of']}")
        sys.exit(0)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"recorded {rec['symbol']} {rec['as_of']}: {rec['regime']} "
          f"(conf {rec['regime_confidence']}) weekly={rec['weekly_trend']}")
