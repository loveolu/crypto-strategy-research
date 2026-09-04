"""A-014 (2026-09-04): five structural constructs, pre-registered, run ONCE each.
  C  MAR  majors/alts momentum rotation, 90d lookback, beta-neutral, daily, 2-bar lag
  A  RS   S2 (1h) when daily gate ON  +  V5-beta (1h) when gate OFF
  K  RF   benchmark basket rebalanced daily / weekly / monthly at measured costs
  E  PF   50% S3 + 50% V5-beta (daily), sleeves fixed-weight
  J  S3g  S3 with the vol-target removed (gate x 1.0)
Kill conditions (pre-registered): C: full-cycle Sharpe <= V5-beta;  A: <= S2;  K: daily <= monthly;
E: <= max(S3, V5);  J: diagnostic only. Reference rows recomputed identically."""
import sys, io, contextlib, numpy as np, pandas as pd
sys.path.insert(0,r"C:\Users\Comec\Projects\freqtrade\user_data\research")
import s5_spread as S
with contextlib.redirect_stdout(io.StringIO()): import bt_five_A012 as B
C,O,R,Dc,F=S.data(); P9=S.P9; MAJ=["BTC","ETH"]; ALT=[p for p in P9 if p not in MAJ]; SIDE=S.SIDE
Rd=Dc.pct_change().dropna(); M=Rd[MAJ].mean(axis=1); A=Rd[ALT].mean(axis=1)

# ---- C. MAR ----
LB=90
cm=(1+M).rolling(LB).apply(np.prod,raw=True)-1; ca=(1+A).rolling(LB).apply(np.prod,raw=True)-1
sig=np.sign(cm-ca); ratio=(M.rolling(30).std()/A.rolling(30).std()).clip(0.3,1.0)
pos=sig.shift(2).fillna(0); rat=ratio.shift(2).fillna(1.0)
legc=(0.25*(SIDE["BTC"]+SIDE["ETH"])+(0.5/7)*sum(SIDE[a] for a in ALT))/1e4
turn=(pos-pos.shift(1)).abs().fillna(0)
mar=pos*(0.5*M-0.5*rat*A)-turn*legc*(1+rat)/2
n_flips=int((turn>0).sum())

# ---- V5-beta (1h and daily) ----
v5,_=S.run(beta_neutral=True); v5d=((1+v5).resample("D").prod()-1)

# ---- A. RS ----
gate=B.gate3; g1h=gate.reindex(v5.index,method="ffill").shift(24).fillna(0)
s2=B.s2t.reindex(v5.index).fillna(0); rs=s2+v5*(1-g1h)

# ---- E. PF ----
pf=0.5*B.s3+0.5*v5d.reindex(B.s3.index).fillna(0)

# ---- J. S3 gate-only ----
m=gate.astype(float); s3g=m.shift(2)*B.b-(m.shift(2)-m.shift(3)).abs()*B.side_b/1e4

# ---- K. RF ----
Rb=B.R1d
def rebal(Rm, every):   # every: 'D','W', or 'M'
    w=np.full(9,1/9); out=[]; idx=Rm.index
    if every=="M": mark=idx.to_series().groupby([idx.year,idx.month]).transform("max")
    elif every=="W": mark=idx.to_series().groupby([idx.isocalendar().year,idx.isocalendar().week]).transform("max")
    else: mark=idx.to_series()
    for t,row in Rm.iterrows():
        g=float((w*row.values).sum()); w=w*(1+row.values); w=w/w.sum(); c=0.0
        if t==mark.loc[t] and t!=idx[-1]:
            tgt=np.full(9,1/9); c=sum(abs(tgt[k]-w[k])*SIDE[P9[k]] for k in range(9))/1e4; w=tgt
        out.append(g-c)
    return pd.Series(out,index=idx)
rf_d=rebal(Rb,"D"); rf_w=rebal(Rb,"W"); rf_m=B.b

# ---- report ----
W={"TRAIN":("2023-01-22","2024-11-22 23:00"),"VAL":("2024-11-23","2025-04-21 23:00"),
   "TEST":("2025-04-22","2025-09-19 23:00"),"FWD":("2025-09-20","2026-09-01")}
def w(s,lo,hi): return s[(s.index>=pd.Timestamp(lo,tz="UTC"))&(s.index<=pd.Timestamp(hi,tz="UTC"))]
def full(s,ppy):
    t=s[(s.index>=pd.Timestamp("2023-01-22",tz="UTC"))&(s.index<=pd.Timestamp("2026-09-01",tz="UTC"))]
    eq=(1+t).cumprod(); yr=(1+t).groupby(t.index.year).prod()-1
    oos=w(s,"2025-04-22","2026-09-01"); eqo=(1+oos).cumprod()
    return dict(ret=(eq.iloc[-1]-1)*100, dd=(eq/eq.cummax()-1).min()*100,
                sh=t.mean()/t.std()*np.sqrt(ppy) if t.std()>0 else 0,
                y23=yr.get(2023,0)*100,y24=yr.get(2024,0)*100,y25=yr.get(2025,0)*100,y26=yr.get(2026,0)*100,
                oos=(eqo.iloc[-1]-1)*100)
rows=[("BENCHMARK (monthly rebal)",rf_m,365),("S3 gated vol-target",B.s3,365),("S2 trend-gated cascade",B.s2t,8760),
      ("V5-beta spread",v5,8760),("—",None,0),
      ("C  MAR rotation 90d",mar,365),("A  RS switch S2/V5",rs,8760),("E  PF 50/50 S3+V5",pf,365),
      ("J  S3 gate-only",s3g,365),("K  basket rebal DAILY",rf_d,365),("K  basket rebal WEEKLY",rf_w,365)]
print(f"{'construct':27s} {'full %':>8s} {'DD %':>7s} {'Sh':>6s} | {'2023':>7s} {'2024':>7s} {'2025':>7s} {'2026':>7s} | {'OOS %':>7s}")
print("-"*100)
res={}
for lbl,s,ppy in rows:
    if s is None: print("-"*100); continue
    r=full(s,ppy); res[lbl]=r
    print(f"{lbl:27s} {r['ret']:8.1f} {r['dd']:7.1f} {r['sh']:6.2f} | {r['y23']:+7.1f} {r['y24']:+7.1f} {r['y25']:+7.1f} {r['y26']:+7.1f} | {r['oos']:+7.1f}")
print(f"\nMAR: {n_flips} position changes over the series; MAR sign now: {int(sig.iloc[-1])} (+1 = long majors)")
print("\nKILL CHECKS:")
print(f"  C  MAR Sharpe {res['C  MAR rotation 90d']['sh']:.2f} vs V5 {res['V5-beta spread']['sh']:.2f} -> {'SURVIVES' if res['C  MAR rotation 90d']['sh']>res['V5-beta spread']['sh'] else 'KILLED'}")
print(f"  A  RS  Sharpe {res['A  RS switch S2/V5']['sh']:.2f} vs S2 {res['S2 trend-gated cascade']['sh']:.2f} -> {'SURVIVES' if res['A  RS switch S2/V5']['sh']>res['S2 trend-gated cascade']['sh'] else 'KILLED'}")
print(f"  E  PF  Sharpe {res['E  PF 50/50 S3+V5']['sh']:.2f} vs max(S3 {res['S3 gated vol-target']['sh']:.2f}, V5 {res['V5-beta spread']['sh']:.2f}) -> {'SURVIVES' if res['E  PF 50/50 S3+V5']['sh']>max(res['S3 gated vol-target']['sh'],res['V5-beta spread']['sh']) else 'KILLED'}")
print(f"  K  daily {res['K  basket rebal DAILY']['ret']:.1f}% vs monthly {res['BENCHMARK (monthly rebal)']['ret']:.1f}% -> {'SURVIVES' if res['K  basket rebal DAILY']['ret']>res['BENCHMARK (monthly rebal)']['ret'] else 'KILLED'}")
