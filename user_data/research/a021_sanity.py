"""Sanity before any walk-forward: S1's LONG leg with the B2 fixed threshold (-3.85%) must reproduce
B2's fixed-split OOS (+30.8%, Sh 1.42, 168 trades) from the main harness. If it does, the shared
loaders, gates, costs and execution convention are right. Also smoke-test each strategy once."""
import sys, time, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import strat5 as S
O0, O1 = pd.Timestamp("2024-11-23", tz="UTC"), pd.Timestamp("2026-09-01", tz="UTC")
t0 = time.time()
print(f"common 4h index: {S.idx4().min().date()} .. {S.idx4().max().date()}  ({len(S.idx4())} bars)")
r = S.s1_run({"thr_L": 0.0385, "thr_S": 0.05}, O0, O1); m = S._stats(r["long"])
print(f"S1 LONG leg @thr -3.85% fixed OOS: ret {m['ret']:+.1f}%  Sh {m['sh']:.2f}  DD {m['dd']:.1f}%  n {r['n_long']}   <- expect ~ +30.8% / 1.42 / 168 (B2)")
m = S._stats(r["short"]); print(f"S1 SHORT leg @thr +5% fixed OOS : ret {m['ret']:+.1f}%  Sh {m['sh']:.2f}  DD {m['dd']:.1f}%  n {r['n_short']}")
gd = pd.concat([S.gates(i)[1] for i in S.P9], axis=1).mean(axis=1)
print(f"strict bear gate ON share by year: " + "  ".join(f"{y}: {v:.0%}" for y, v in gd.groupby(gd.index.year).mean().items()))
for lb in (90,):
    s = S.s2_run(lb, "ls", O0, O1); m = S._stats(s); print(f"S2 TSMOM L/S LB{lb} fixed OOS: ret {m['ret']:+.1f}%  Sh {m['sh']:.2f}  DD {m['dd']:.1f}%")
s = S.s3_run(O0, O1); m = S._stats(s); print(f"S3 AltBTC-MR fixed OOS      : ret {m['ret']:+.1f}%  Sh {m['sh']:.2f}  DD {m['dd']:.1f}%")
s, n = S.s4_run(O0, O1); m = S._stats(s); print(f"S4 CascadeSpread fixed OOS  : ret {m['ret']:+.1f}%  Sh {m['sh']:.2f}  DD {m['dd']:.1f}%  spreads {n}")
a, b, c = S.windows()[0]
s, n, mdl, base = S.s5_window(a, b, c); m = S._stats(s)
print(f"S5 GBM first window {b.date()}..{c.date()}: ret {m['ret']:+.1f}%  Sh {m['sh']:.2f}  n {n}  (train base rate {base:.2f})")
print(f"elapsed {time.time()-t0:.0f}s")
