"""A-012 (operator-directed 2026-09-03): backtest 5 candidate strategies + the benchmark
on 2025-09-01 .. 2026-09-01. Rules FIXED as specified 2026-09-03 before any run; no tuning.
Costs: per-instrument, MEASURED (A-011). All indicators computed on the FULL series, then
sliced (directive 8). Self-contained: reads feathers + A-011 cost CSV directly.
NOTE: this window lies inside the perps reserved holdout; it is spent for these constructs."""
import sys, functools, numpy as np, pandas as pd
ROOT=r"C:\Users\Comec\Projects\freqtrade"
FUT=f"{ROOT}/user_data/data/okx/futures"; FUND=f"{ROOT}/user_data/research/data/funding"
COSTS=pd.read_csv(f"{ROOT}/user_data/research/data/okx_micro/adverse_selection_results.csv").set_index("inst")
W0,W1=pd.Timestamp("2025-09-01",tz="UTC"),pd.Timestamp("2026-09-01",tz="UTC")
P9=["BTC","ETH","SOL","BNB","XRP","ADA","AVAX","DOT","LINK"]
MAJ=["BTC","ETH"]; ALT=[p for p in P9 if p not in MAJ]; S1U=["BTC","ETH","SOL","XRP","BNB"]
FEE_T,FEE_M=5.0,2.0
side_t={i:float(COSTS.loc[i,"half"]+FEE_T+COSTS.loc[i,"slip_$5k"]) for i in P9}   # taker bps/side
half={i:float(COSTS.loc[i,"half"]) for i in P9}

def load(i,tf):
    d=pd.read_feather(f"{FUT}/{i}_USDT_USDT-{tf}-futures.feather").set_index("date").sort_index()
    return d[~d.index.duplicated()]
H={i:load(i,"1h") for i in P9}; D={i:load(i,"1d") for i in P9}
print("data end:", min(H[i].index.max() for i in P9), "| 1d:", min(D[i].index.max() for i in P9))

# ---------- 1h conditioners (full series) ----------
def cond1h(df):
    c=df["close"]; r=c/c.shift(1)-1
    dsd=np.sqrt((np.minimum(r,0)**2).rolling(168).mean())
    pct=dsd.rolling(720).rank(pct=True)
    mom=c/c.shift(24)-1
    return pd.DataFrame({"o":df["open"],"h":df["high"],"l":df["low"],"c":c,"r":r,"dsd":dsd,"pct":pct,"mom":mom})
C1={i:cond1h(H[i]) for i in P9}

# ---------- daily gates (full series) ----------
def gate_d(df):
    c=df["close"]; return ((c>c.rolling(200).mean())&(c.ewm(span=20).mean()>c.ewm(span=50).mean())).astype(int)
G={i:gate_d(D[i]) for i in P9}

# ---------- BENCHMARK: equal-weight, monthly rebalance, taker cost on turnover ----------
idx=functools.reduce(lambda a,b_: a.intersection(b_), [D[i].index for i in P9])
R1d=pd.DataFrame({i:D[i]["close"].reindex(idx).pct_change() for i in P9}).dropna()
def basket_monthly(R):
    w=np.full(len(P9),1/9); out=[]; me=R.index.to_series().groupby([R.index.year,R.index.month]).transform("max")
    for t,row in R.iterrows():
        gross=float((w*row.values).sum()); w=w*(1+row.values); w=w/w.sum()
        cost=0.0
        if t==me.loc[t] and t!=R.index[-1]:
            tgt=np.full(len(P9),1/9); cost=float(sum(abs(tgt[k]-w[k])*side_t[P9[k]] for k in range(len(P9))))/1e4; w=tgt
        out.append(gross-cost)
    return pd.Series(out,index=R.index)
b=basket_monthly(R1d)

# ---------- S3: gate x vol-target on the basket, validator 2-bar convention ----------
bi=(1+b).cumprod(); gate3=(bi>bi.rolling(200).mean()).astype(float)
rv=b.rolling(30).std(ddof=1)*np.sqrt(365); vt=(0.40/rv).clip(0,1.0); vt=(np.round(vt/0.25)*0.25)
m3=(gate3*vt).fillna(0); side_b=float(np.mean([side_t[i] for i in P9]))
s3=m3.shift(2)*b-(m3.shift(2)-m3.shift(3)).abs()*side_b/1e4

# ---------- S1/S2: cascade reversion, per-instrument, non-overlapping 24h ----------
def cascade(i,gated,maker):
    x=C1[i]; g=None
    if gated:
        g=G[i].reindex(x.index,method="ffill").shift(24).fillna(0)   # yesterday's daily gate applies to today's bars
    o,hh,ll,c,pct,mom=x.o.values,x.h.values,x.l.values,x.c.values,x.pct.values,x.mom.values
    n=len(x); ret=np.zeros(n); ntr=0; t=720
    while t<n-26:
        trig=(pct[t]>=0.80) and (mom[t]<0) and (not gated or g.iloc[t]>0)
        if not trig: t+=1; continue
        if maker:
            bid=c[t]*(1-half[i]/1e4)
            if not (ll[t+1]<bid): t+=1; continue
            ep=bid; ec=FEE_M
        else:
            ep=o[t+1]*(1+(side_t[i]-FEE_T)/1e4); ec=FEE_T
        k=t+1; end=min(t+1+24,n-2)
        while k<end and not (pct[k]<0.50): k+=1
        xp=o[k+1]*(1-(side_t[i]-FEE_T)/1e4); xc=FEE_T
        ret[k+1]=(xp/ep-1)-(ec+xc)/1e4; ntr+=1; t=k+2
    return pd.Series(ret,index=x.index), ntr
def sleeve_basket(univ,gated,maker):
    S=[];N=0
    for i in univ: s,n=cascade(i,gated,maker); S.append(s); N+=n
    return pd.concat(S,axis=1).mean(axis=1), N
s1t,n1t=sleeve_basket(S1U,False,False); s1m,n1m=sleeve_basket(S1U,False,True)
s2t,n2t=sleeve_basket(S1U,True,False);  s2m,n2m=sleeve_basket(S1U,True,True)

# ---------- S5: majors/alts spread on basket-level cascade regime ----------
hidx=functools.reduce(lambda a,b_: a.intersection(b_), [C1[i].index for i in P9])
R1h=pd.DataFrame({i:C1[i].r.reindex(hidx) for i in P9}).dropna()
bk1h=R1h.mean(axis=1); bdsd=np.sqrt((np.minimum(bk1h,0)**2).rolling(168).mean()); bpct=bdsd.rolling(720).rank(pct=True)
spread=0.25*(R1h.BTC+R1h.ETH)-(1/7)*0.5*R1h[ALT].sum(axis=1)
leg_cost=(0.25*(side_t["BTC"]+side_t["ETH"])+(0.5/7)*sum(side_t[a] for a in ALT))/1e4
inpos=False; s5=pd.Series(0.0,index=R1h.index); n5=0; bp=bpct.values; sp=spread.values
for k in range(1,len(R1h)-1):
    if not inpos and bp[k-1]>=0.80: inpos=True; s5.iloc[k]=sp[k]-leg_cost; n5+=1
    elif inpos and bp[k-1]<=0.50: inpos=False; s5.iloc[k]=-leg_cost
    elif inpos: s5.iloc[k]=sp[k]

# ---------- S4: funding-crowding overlay on S3 (only where funding exists) ----------
F={}
import os
for i in P9:
    fp=f"{FUND}/{i}-USDT-SWAP.csv"
    if not os.path.exists(fp): continue          # recorder tracks UNI, not XRP
    f=pd.read_csv(fp); f["t"]=pd.to_datetime(f.funding_time_utc); F[i]=f.set_index("t").funding_rate.astype(float)
Fz=pd.DataFrame(F); z=((Fz-Fz.rolling(90).mean())/Fz.rolling(90).std()).mean(axis=1)
zd=z.reindex(b.index,method="ffill")
m4=m3.copy(); m4[zd>=2]=0.0; m4[zd<=-2]=1.0
s4=m4.shift(2)*b-(m4.shift(2)-m4.shift(3)).abs()*side_b/1e4
fund_start=z.dropna().index.min()

# ---------- report ----------
def win(s): return s[(s.index>=W0)&(s.index<W1)]
def monthly(s): return (1+win(s)).groupby([win(s).index.year,win(s).index.month]).prod()-1
def stats(s,ppy):
    w=win(s); eq=(1+w).cumprod(); dd=(eq/eq.cummax()-1).min()
    sh=w.mean()/w.std()*np.sqrt(ppy) if w.std()>0 else 0
    return (eq.iloc[-1]-1)*100, dd*100, sh
strat={"BENCHMARK (hold basket)":(b,365),"S3 gated vol-target basket":(s3,365),
       "S1 cascade rev — TAKER":(s1t,8760),"S1 cascade rev — MAKER":(s1m,8760),
       "S2 trend-gated casc — TAKER":(s2t,8760),"S2 trend-gated casc — MAKER":(s2m,8760),
       "S5 majors/alts spread":(s5,8760)}
M=pd.DataFrame({k:monthly(v[0])*100 for k,(v) in strat.items()})
M.index=[f"{y}-{m:02d}" for y,m in M.index]
pd.set_option("display.width",200)
print("\n=== MONTHLY P&L, % of capital, 2025-09-01 .. 2026-09-01 (measured costs) ===")
print(M.round(2).to_string())
print("\n=== YEAR SUMMARY ===")
print(f"{'strategy':32s} {'return %':>9s} {'maxDD %':>8s} {'Sharpe':>7s} {'trades':>7s}")
tr={"S1 cascade rev — TAKER":n1t,"S1 cascade rev — MAKER":n1m,"S2 trend-gated casc — TAKER":n2t,"S2 trend-gated casc — MAKER":n2m,"S5 majors/alts spread":n5}
for k,(s,ppy) in strat.items():
    r,dd,sh=stats(s,ppy); print(f"{k:32s} {r:9.2f} {dd:8.2f} {sh:7.2f} {tr.get(k,'—'):>7}")
print(f"\n=== S4 funding overlay on S3, funding-covered window only ({fund_start.date()} ..) ===")
sub=lambda s: s[(s.index>=fund_start)&(s.index<W1)]
for k,s in (("S3 alone",s3),("S3 + S4 overlay",s4)):
    w=sub(s); eq=(1+w).cumprod(); print(f"  {k:18s} return {(eq.iloc[-1]-1)*100:7.2f}%   maxDD {(eq/eq.cummax()-1).min()*100:7.2f}%   z>=2 days {(sub(zd)>=2).sum()}  z<=-2 days {(sub(zd)<=-2).sum()}")
M.to_csv(f"{ROOT}/research/measurements/A012_monthly_pnl.csv")
