"""CRYPTO-EXP-010: robustness sub-protocol for S2-strict at 4h (EXP-009 leader). Base mapping W42 PW180
HOLD6 mom6 gate_shift6, TRAIN thr -3.85%. One-at-a-time parameter sensitivity, entry delay, coin
sensitivity, rolling OOS quarters. Reported on OOS (2024-11-23..2026-09-01) — a stability check of a
fixed rule, not a selection; base position in the region is what matters."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,r"C:\Users\Comec\Projects\freqtrade\user_data\research"); import s2_cascade as S2
T0,T1=pd.Timestamp("2023-01-22",tz="UTC"),pd.Timestamp("2024-11-22 23:00",tz="UTC")
O0,O1=pd.Timestamp("2024-11-23",tz="UTC"),pd.Timestamp("2026-09-01",tz="UTC")
def win(s,tr,lo,hi): return s[(s.index>=lo)&(s.index<=hi)], tr[(tr.entry>=lo)&(tr.entry<=hi)]
BASE=dict(tf="4h",W=42,PW=180,HOLD=6,mom_bars=6,gate_shift=6); THR=0.0385; N=9; PPY=2190
def oos(**kw):
    k={**BASE,**kw}; tr,s=S2.basket(S2.P9,mom_thr=THR,**k); m=S2.metrics(*win(s,tr,O0,O1),N,ppy=PPY); return m
def f(m): return f"Sh {m.get('sharpe',0):5.2f} / {m.get('ret',0):+5.1f}% / n {m.get('n',0)}"
print("A. PARAMETER SENSITIVITY at 4h — OOS, one-at-a-time (base: W42 PW180 THR.80 HOLD6)")
grid={"W":[34,38,42,46,50],"PW":[144,162,180,198,216],"THR":[0.72,0.76,0.80,0.84,0.88],"HOLD":[4,5,6,7,8]}
allsh=[]
for p,vals in grid.items():
    line=[]
    for v in vals:
        m=oos(**{p:v}); allsh.append(m["sharpe"]); line.append(f"{v}: {f(m)}")
    print(f"  {p:4s} "+" | ".join(line))
print(f"  region: min Sh {min(allsh):.2f}, max {max(allsh):.2f}, base 1.31; all positive: {all(x>0 for x in allsh)}")
print("\nB. ENTRY DELAY at 4h (1 bar = 4h)")
for d in (0,1,2): print(f"  delay {d}: {f(oos(delay=d))}")
print("\nC. COST STRESS (OOS)")
for cm in (1.0,1.5,2.0,3.0): print(f"  x{cm}: {f(oos(cost_mult=cm))}")
print("\nD. COIN SENSITIVITY at 4h (OOS, each alone)")
for i in S2.P9:
    tr,s=S2.trades(i,mom_thr=THR,**BASE); m=S2.metrics(*win(s,tr,O0,O1),1,ppy=PPY); print(f"  {i:5s} {f(m)}  PF {m.get('pf',0):.2f}")
print("\nE. ROLLING OOS QUARTERS (4h strict)")
tr,s=S2.basket(S2.P9,mom_thr=THR,**BASE); q=[]
for a in pd.date_range("2024-12-01","2026-06-01",freq="3MS",tz="UTC"):
    m=S2.metrics(*win(s,tr,a,a+pd.DateOffset(months=3)),N,ppy=PPY); q.append(m.get("ret",0))
print("  "+" ".join(f"{x:+5.1f}" for x in q)+f"   -> {sum(x>0 for x in q)}/{len(q)} positive, sum {sum(q):+.1f}%")
print("\nF. RECENT (4h strict): ", end="")
for d in (30,90,180,365):
    m=S2.metrics(*win(s,tr,O1-pd.Timedelta(days=d),O1),N,ppy=PPY); print(f"{d}d {m.get('ret',0):+.1f}%/n{m.get('n',0)}  ", end="")
print()
