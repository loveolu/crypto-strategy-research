"""A-013 in-sample development: pre-registered S5 variants on TRAIN+VAL ONLY.
TEST is NOT printed here — it is reserved for ONE winner, chosen by TRAIN+VAL Sharpe.
Variants written down before any was run:
  base        as A-012
  always      diagnostic: spread on permanently (is the spread negative unconditionally?)
  V6 trend    regime = daily basket < SMA200 (bear), instead of dispersion percentile
  V2 cheap    drop ADA, DOT from short leg (COST rationale: 10.0 / 9.1 bps per side)
  V3 hyst     enter >= 0.90, exit <= 0.40 (fewer regime flips)
  V5 beta     scale alt leg by trailing-30d vol ratio (causal) so legs contribute equal vol
  V1 noBNB    drop BNB from short leg (exchange token) — HOLDOUT-INFORMED, flagged
  combo       V6 + V2 + V5"""
import sys, numpy as np, pandas as pd
sys.path.insert(0,r"C:\Users\Comec\Projects\freqtrade\user_data\research"); import s5_spread as S
ALL=("SOL","BNB","XRP","ADA","AVAX","DOT","LINK")
V={"base":dict(),
   "always (diag)":dict(gate="always"),
   "V6 trend-gate":dict(gate="trend"),
   "V2 drop ADA,DOT":dict(alts=tuple(a for a in ALL if a not in("ADA","DOT"))),
   "V3 hyst .90/.40":dict(enter=0.90,exit_=0.40),
   "V5 beta-neutral":dict(beta_neutral=True),
   "V1 drop BNB*":dict(alts=tuple(a for a in ALL if a!="BNB")),
   "combo V6+V2+V5":dict(gate="trend",alts=tuple(a for a in ALL if a not in("ADA","DOT")),beta_neutral=True)}
def w(s,lo,hi): return s[(s.index>=pd.Timestamp(lo,tz="UTC"))&(s.index<=pd.Timestamp(hi,tz="UTC"))]
def st(x):
    eq=(1+x).cumprod(); yrs=len(x)/8760
    return (eq.iloc[-1]-1)*100,(eq/eq.cummax()-1).min()*100,(x.mean()/x.std()*np.sqrt(8760) if x.std()>0 else 0)
print(f"{'variant':18s} | {'TRAIN ret':>9s} {'DD':>7s} {'Sh':>6s} | {'VAL ret':>8s} {'DD':>7s} {'Sh':>6s} | {'T+V ret':>8s} {'DD':>7s} {'Sh':>6s} | {'2023':>7s} {'2024':>7s} | entries")
print("-"*130)
rows={}
for name,kw in V.items():
    s,n=S.run(**kw)
    tr=w(s,"2023-01-22","2024-11-22 23:00"); va=w(s,"2024-11-23","2025-04-21 23:00"); tv=w(s,"2023-01-22","2025-04-21 23:00")
    a=st(tr);b=st(va);c=st(tv); yr=(1+tv).groupby(tv.index.year).prod()-1
    rows[name]=c[2]
    print(f"{name:18s} | {a[0]:9.2f} {a[1]:7.2f} {a[2]:6.2f} | {b[0]:8.2f} {b[1]:7.2f} {b[2]:6.2f} | {c[0]:8.2f} {c[1]:7.2f} {c[2]:6.2f} | {yr.get(2023,0)*100:+7.2f} {yr.get(2024,0)*100:+7.2f} | {n}")
best=max(rows,key=rows.get); print(f"\nbest by TRAIN+VAL Sharpe: {best}  ({rows[best]:.2f})   <- the ONE that gets a TEST run")
