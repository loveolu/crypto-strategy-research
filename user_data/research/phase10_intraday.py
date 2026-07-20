"""
Phase 10: Intraday seasonality scan on BTC 1h (2020-10 .. 2026-05).

Hour-of-day and weekday-hour mean returns, stability across period halves,
and a quick strategy test of any pattern that looks stable.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from validator import load

btc = load('BTC/USDT', '1h')
ret = btc['close'].pct_change().dropna()

print(f"BTC 1h: {ret.index.min()} .. {ret.index.max()}  ({len(ret)} bars)")
print()
print("Mean return by hour (UTC), full / first half / second half, t-stat full:")
half = len(ret) // 2
r1, r2 = ret.iloc[:half], ret.iloc[half:]
rows = []
for h in range(24):
    f = ret[ret.index.hour == h]
    a = r1[r1.index.hour == h]
    b = r2[r2.index.hour == h]
    t = f.mean() / (f.std() / np.sqrt(len(f)))
    rows.append((h, f.mean()*100, a.mean()*100, b.mean()*100, t, len(f)))
print(f"{'hr':>3} {'full%':>8} {'h1%':>8} {'h2%':>8} {'t':>6}")
stable = []
for h, fm, am, bm, t, n in rows:
    mark = ""
    if abs(t) > 2 and np.sign(am) == np.sign(bm):
        mark = "  <== |t|>2 & stable sign"
        stable.append((h, fm, t))
    print(f"{h:>3} {fm:>8.4f} {am:>8.4f} {bm:>8.4f} {t:>6.2f}{mark}")

print()
print("Weekend vs weekday hourly vol:")
we = ret[ret.index.dayofweek >= 5]
wd = ret[ret.index.dayofweek < 5]
print(f"  weekday std {wd.std()*100:.3f}%  weekend std {we.std()*100:.3f}%  "
      f"weekday mean {wd.mean()*100:+.4f}%  weekend mean {we.mean()*100:+.4f}%")

print()
print("Session returns (UTC): Asia 00-08, EU 08-16, US 16-24:")
for label, lo, hi in [("Asia", 0, 8), ("EU", 8, 16), ("US", 16, 24)]:
    f = ret[(ret.index.hour >= lo) & (ret.index.hour < hi)]
    a = r1[(r1.index.hour >= lo) & (r1.index.hour < hi)]
    b = r2[(r2.index.hour >= lo) & (r2.index.hour < hi)]
    ann = f.mean() * 8 * 365
    print(f"  {label:5s} mean/bar {f.mean()*100:+.4f}%  h1 {a.mean()*100:+.4f}%  h2 {b.mean()*100:+.4f}%  -> ann. if harvested {ann*100:+.0f}%")

if stable:
    print()
    print("Testing stable hours as a strategy (long only those hours, fees 0.15%/side):")
    FEE = 0.0015
    for h, fm, t in stable:
        # in at close of hour h-1, out at close of hour h: 2 fee events per day
        mask = (ret.index.hour == h)
        strat = ret[mask] - 2 * FEE  # round-trip cost per daily trade
        ann_gross = ret[mask].mean() * 365
        ann_net = strat.mean() * 365
        print(f"  hour {h:2d}: gross {ann_gross*100:+6.1f}%/yr  NET after fees {ann_net*100:+6.1f}%/yr")
else:
    print("\nNo hour passed |t|>2 with stable sign across halves.")
