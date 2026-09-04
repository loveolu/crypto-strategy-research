"""CRYPTO-EXP-007 / A-016: S2-strict. Hypothesis (from EXP-006 diagnosis): the cascade-reversion edge
lives in the largest prior-24h drops; a magnitude filter on mom_24 concentrates it.
PROTOCOL: threshold = 25th percentile of entry mom_24 among TRAIN trigger bars (TRAIN only,
2023-01-22 .. 2024-11-22), then FIXED. Evaluated on VAL / TEST / FWD separately, rolling quarters,
recent 365d, trade concentration. Loose S2 shown alongside for every window. 5- and 9-universe."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,r"C:\Users\Comec\Projects\freqtrade\user_data\research"); import s2_cascade as S2
T0,T1=pd.Timestamp("2023-01-22",tz="UTC"),pd.Timestamp("2024-11-22 23:00",tz="UTC")
W={"TRAIN (in-sample)":(T0,T1),"VAL":(pd.Timestamp("2024-11-23",tz="UTC"),pd.Timestamp("2025-04-21 23:00",tz="UTC")),
   "TEST":(pd.Timestamp("2025-04-22",tz="UTC"),pd.Timestamp("2025-09-19 23:00",tz="UTC")),
   "FWD":(pd.Timestamp("2025-09-20",tz="UTC"),pd.Timestamp("2026-09-01",tz="UTC")),
   "VAL+TEST+FWD (all OOS)":(pd.Timestamp("2024-11-23",tz="UTC"),pd.Timestamp("2026-09-01",tz="UTC"))}
def win(s,tr,lo,hi): return s[(s.index>=lo)&(s.index<=hi)], tr[(tr.entry>=lo)&(tr.entry<=hi)]
def fmt(m): return f"ret {m.get('ret',0):6.1f}%  Sh {m.get('sharpe',0):5.2f}  DD {m.get('dd',0):6.1f}%  PF {m.get('pf',0):4.2f}  n {m.get('n',0):3d}  exp {m.get('exp_bps',0):6.1f}"
for lbl,univ in (("5-UNIVERSE",S2.U5),("9-UNIVERSE",S2.P9)):
    N=len(univ)
    tr0,s0=S2.basket(univ)                                   # loose
    _,ttr=win(s0,tr0,T0,T1); thr=float(-np.percentile(ttr.entry_mom,25))   # TRAIN-only quartile boundary
    tr1,s1=S2.basket(univ,mom_thr=thr)                       # strict, fixed threshold
    print("="*112); print(f"{lbl}   TRAIN-derived threshold: mom_24 <= -{thr*100:.2f}%   (loose = mom_24 < 0)"); print("="*112)
    print(f"{'window':24s} | {'LOOSE S2':^58s} | {'STRICT S2':^58s}")
    for k,(lo,hi) in W.items():
        a=S2.metrics(*win(s0,tr0,lo,hi),N); b=S2.metrics(*win(s1,tr1,lo,hi),N)
        print(f"{k:24s} | {fmt(a)} | {fmt(b)}")
    # rolling OOS quarters (post-TRAIN only)
    starts=pd.date_range("2024-12-01","2026-06-01",freq="3MS",tz="UTC"); ra=[];rb=[]
    for a_ in starts:
        b_=a_+pd.DateOffset(months=3)
        ma=S2.metrics(*win(s0,tr0,a_,b_),N); mb=S2.metrics(*win(s1,tr1,a_,b_),N)
        ra.append(ma.get("ret",0)); rb.append(mb.get("ret",0))
    print(f"  rolling OOS quarters  loose: "+" ".join(f"{x:+5.1f}" for x in ra)+f"  -> {sum(x>0 for x in ra)}/{len(ra)} pos, sum {sum(ra):+.1f}%")
    print(f"                        strict: "+" ".join(f"{x:+5.1f}" for x in rb)+f"  -> {sum(x>0 for x in rb)}/{len(rb)} pos, sum {sum(rb):+.1f}%")
    # recent 365
    lo=pd.Timestamp("2026-09-01",tz="UTC")-pd.Timedelta(days=365); hi=pd.Timestamp("2026-09-01",tz="UTC")
    print(f"  last 365d             loose: {fmt(S2.metrics(*win(s0,tr0,lo,hi),N))}")
    print(f"                        strict: {fmt(S2.metrics(*win(s1,tr1,lo,hi),N))}")
    # concentration on OOS trades
    _,o1=win(s1,tr1,W["VAL+TEST+FWD (all OOS)"][0],W["VAL+TEST+FWD (all OOS)"][1]); o1=o1.sort_values("net",ascending=False)
    if len(o1): print(f"  strict OOS concentration: all {o1.net.sum()/N*100:+.1f}% | drop top5% {o1.iloc[int(len(o1)*.05):].net.sum()/N*100:+.1f}% | drop top10% {o1.iloc[int(len(o1)*.10):].net.sum()/N*100:+.1f}%  (n={len(o1)})")
    # cost stress on strict, full OOS
    for cm,cl in ((1.5,"x1.5"),(2.0,"x2.0")):
        trc,sc=S2.basket(univ,mom_thr=thr,cost_mult=cm); print(f"  strict OOS cost {cl}: {fmt(S2.metrics(*win(sc,trc,W['VAL+TEST+FWD (all OOS)'][0],W['VAL+TEST+FWD (all OOS)'][1]),N))}")
