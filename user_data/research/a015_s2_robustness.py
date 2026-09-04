"""CRYPTO-EXP-005 / A-015: S2 full robustness protocol. Parameters FIXED at base; every variation
below is a sensitivity, not a search. Window 2023-01-22 .. 2026-09-01. Results printed and saved."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,r"C:\Users\Comec\Projects\freqtrade\user_data\research"); import s2_cascade as S2
LO,HI=pd.Timestamp("2023-01-22",tz="UTC"),pd.Timestamp("2026-09-01",tz="UTC")
def win(s,tr,lo=LO,hi=HI): return s[(s.index>=lo)&(s.index<=hi)], tr[(tr.entry>=lo)&(tr.entry<=hi)]
def M(univ=S2.U5,lo=LO,hi=HI,**kw):
    tr,s=S2.basket(univ,**kw); w,t=win(s,tr,lo,hi); return S2.metrics(w,t,len(univ)),w,t
def row(lbl,m,extra=""):
    print(f"{lbl:26s} ret {m.get('ret',0):7.1f}%  ann {m.get('ann',0):6.1f}%  DD {m.get('dd',0):6.1f}%  Sh {m.get('sharpe',0):5.2f}  So {m.get('sortino',0):5.2f}  PF {m.get('pf',0):4.2f}  n {m.get('n',0):4d}  exp {m.get('exp_bps',0):6.1f}bps {extra}")
out={}

print("="*118); print("A. BASE S2 — full metric set, 2023-01-22 .. 2026-09-01, realistic (taker measured) costs"); print("="*118)
m,w,t=M(); out["base"]=m
for k,v in m.items(): print(f"  {k:10s} {v:10.2f}" if isinstance(v,float) else f"  {k:10s} {v}")

print("\n"+"="*118); print("B. RECENT PERFORMANCE (ending 2026-09-01)"); print("="*118)
_,s_full,tr_full=M(lo=pd.Timestamp("2022-01-01",tz="UTC"))
for d in (30,90,180,365):
    lo=HI-pd.Timedelta(days=d); ww,tt=win(s_full,tr_full,lo,HI); mm=S2.metrics(ww,tt,5); out[f"recent_{d}"]=mm
    row(f"last {d:3d} days",mm)

print("\n"+"="*118); print("C. ROLLING 3-MONTH OUT-OF-SAMPLE WINDOWS (fixed params — consistency check, not optimisation)"); print("="*118)
starts=pd.date_range("2023-04-01","2026-06-01",freq="3MS",tz="UTC"); pos=0; rows=[]
for a in starts:
    b=a+pd.DateOffset(months=3); ww,tt=win(s_full,tr_full,a,b); mm=S2.metrics(ww,tt,5)
    if mm: rows.append((a.date(),mm["ret"],mm["sharpe"],mm["n"])); pos+=mm["ret"]>0
print("  "+"  ".join(f"{r[0]}: {r[1]:+5.1f}%/{r[3]}t" for r in rows)); print(f"  positive windows: {pos}/{len(rows)}"); out["rolling"]=rows

print("\n"+"="*118); print("D. COST SCENARIOS"); print("="*118)
for lbl,kw in (("optimistic (maker entry)",dict(cost="maker")),("realistic (taker measured)",dict()),("stressed (taker x1.5)",dict(cost_mult=1.5)),("severe (taker x2.0)",dict(cost_mult=2.0))):
    mm,_,_=M(**kw); out[f"cost_{lbl}"]=mm; row(lbl,mm)

print("\n"+"="*118); print("E. ENTRY DELAY"); print("="*118)
for d in (0,1,2): mm,_,_=M(delay=d); out[f"delay_{d}"]=mm; row(f"delay {d} bar(s)",mm)

print("\n"+"="*118); print("F. TOP-TRADE REMOVAL (from base trade list; return = sum of net/5)"); print("="*118)
base_tr=t.sort_values("net",ascending=False); tot=base_tr.net.sum()/5*100
for k,lbl in ((0,"all trades"),(10,"drop top 10"),(int(len(base_tr)*0.05),"drop top 5%"),(int(len(base_tr)*0.10),"drop top 10%")):
    rem=base_tr.iloc[k:]; print(f"  {lbl:14s}  simple-sum return {rem.net.sum()/5*100:7.1f}%   (n={len(rem)}, PF {rem.net[rem.net>0].sum()/abs(rem.net[rem.net<0].sum()):.2f})")

print("\n"+"="*118); print("G. PARAMETER SENSITIVITY — one at a time, others at base (W168 PW720 THR.80 EXIT.50 HOLD24)"); print("="*118)
grid={"W":[134,151,168,185,202],"THR":[0.72,0.76,0.80,0.84,0.88],"EXIT":[0.40,0.45,0.50,0.55,0.60],"HOLD":[16,20,24,28,32],"PW":[576,648,720,792,864]}
sens={}
for p,vals in grid.items():
    line=[]
    for v in vals:
        mm,_,_=M(**{p:v}); sens[(p,v)]=mm; line.append(f"{v}: Sh {mm['sharpe']:.2f} / {mm['ret']:+.0f}%")
    print(f"  {p:5s} "+" | ".join(line))
out["sens"]=sens

print("\n"+"="*118); print("H. COIN SENSITIVITY"); print("="*118)
for i in S2.P9:
    tr,s=S2.trades(i); ww=s[(s.index>=LO)&(s.index<=HI)]; tt=tr[(tr.entry>=LO)&(tr.entry<=HI)]; mm=S2.metrics(ww,tt,1)
    row(f"  {i} alone",mm)
m9,_,_=M(univ=S2.P9); row("9-instrument basket",m9); out["univ9"]=m9

print("\n"+"="*118); print("I. REGIME SPLIT (basket trailing-30d realised vol, top vs bottom half; and by year)"); print("="*118)
C=pd.DataFrame({i:S2.load(i,"1h")["close"] for i in S2.U5}).pct_change().mean(axis=1)
rv=C.rolling(720).std().reindex(w.index); med=rv.median()
for lbl,mask in (("HIGH vol half",rv>=med),("LOW vol half",rv<med)):
    ww=w[mask.fillna(False)]; print(f"  {lbl:14s} ann {((1+ww).prod()**(8760/len(ww))-1)*100:6.1f}%  Sh {ww.mean()/ww.std()*np.sqrt(8760):5.2f}  bars {len(ww)}")
yr=(1+w).groupby(w.index.year).prod()-1; print("  by year: "+"  ".join(f"{y}: {v*100:+.1f}%" for y,v in yr.items()))

print("\n"+"="*118); print("J. SHORT MIRROR (usd pct >= .80 & mom>0 & gate OFF -> short 24h) — diagnostic"); print("="*118)
ms,_,_=M(short=True); out["short"]=ms; row("S2 short mirror",ms)
pd.to_pickle(out,r"C:\Users\Comec\Projects\freqtrade\research\measurements\A015_results.pkl")
