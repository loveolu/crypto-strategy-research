"""S5 majors/alts cascade spread — reusable core (A-013, 2026-09-04).
Base rules exactly as specified 2026-09-03 and run in A-012:
  legs: long 0.25 BTC + 0.25 ETH; short 0.5/len(alts) each alt; dollar-neutral, gross 1.0
  regime: basket-level dsd_168 rolling-720 percentile; enter >= ENTER, exit <= EXIT
  execution: taker all legs at next-bar open; A-011 measured per-instrument costs
Variants are parameters; nothing here reads a result before deciding a rule."""
import functools, numpy as np, pandas as pd
ROOT=r"C:\Users\Comec\Projects\freqtrade"
FUT=f"{ROOT}/user_data/data/okx/futures"
P9=["BTC","ETH","SOL","BNB","XRP","ADA","AVAX","DOT","LINK"]
COSTS=pd.read_csv(f"{ROOT}/user_data/research/data/okx_micro/adverse_selection_results.csv").set_index("inst")
SIDE={i:float(COSTS.loc[i,"half"]+5.0+COSTS.loc[i,"slip_$5k"]) for i in P9}

def _load(i,tf):
    d=pd.read_feather(f"{FUT}/{i}_USDT_USDT-{tf}-futures.feather").set_index("date").sort_index()
    return d[~d.index.duplicated()]

@functools.lru_cache(maxsize=None)
def data():
    H={i:_load(i,"1h") for i in P9}; D={i:_load(i,"1d") for i in P9}
    idx=functools.reduce(lambda a,b:a.intersection(b),[H[i].index for i in P9])
    C=pd.DataFrame({i:H[i]["close"].reindex(idx) for i in P9})
    O=pd.DataFrame({i:H[i]["open"].reindex(idx) for i in P9})
    R=C.pct_change()
    didx=functools.reduce(lambda a,b:a.intersection(b),[D[i].index for i in P9])
    Dc=pd.DataFrame({i:D[i]["close"].reindex(didx) for i in P9})
    F={}
    for i in P9:
        try:
            f=pd.read_feather(f"{FUT}/{i}_USDT_USDT-1h-funding_rate.feather").set_index("date").sort_index()
            F[i]=f[~f.index.duplicated()]["open"].astype(float)   # freqtrade stores rate in 'open'
        except Exception: pass
    return C,O,R,Dc,F

def run(majors=("BTC","ETH"), alts=("SOL","BNB","XRP","ADA","AVAX","DOT","LINK"),
        enter=0.80, exit_=0.50, gate="dispersion", beta_neutral=False, funding=False,
        w_gross=1.0):
    C,O,R,Dc,F=data()
    bk=R[list(P9)].mean(axis=1)
    if gate=="dispersion":
        dsd=np.sqrt((np.minimum(bk,0)**2).rolling(168).mean()); sig=dsd.rolling(720).rank(pct=True)
        on_enter=lambda k: sig.iat[k-1]>=enter; on_exit=lambda k: sig.iat[k-1]<=exit_
    elif gate=="trend":   # spread ON when daily basket index < SMA200 (bear regime), evaluated on prior day
        bi=(1+Dc[list(P9)].pct_change().mean(axis=1)).cumprod(); g=(bi<bi.rolling(200).mean()).astype(float)
        g1h=g.reindex(R.index,method="ffill").shift(24).fillna(0)
        on_enter=lambda k: g1h.iat[k-1]>0; on_exit=lambda k: g1h.iat[k-1]==0
    elif gate=="always":
        on_enter=lambda k: True; on_exit=lambda k: False
    else: raise ValueError(gate)
    wm=w_gross/2/len(majors); wa=w_gross/2/len(alts)
    if beta_neutral:   # scale alt leg so vol contributions match, using trailing-30d vol ratio (causal)
        vm=R[list(majors)].mean(axis=1).rolling(720).std(); va=R[list(alts)].mean(axis=1).rolling(720).std()
        ratio=(vm/va).clip(0.3,1.0).shift(1).fillna(1.0)
    else: ratio=pd.Series(1.0,index=R.index)
    ret_m=R[list(majors)].mean(axis=1); ret_a=R[list(alts)].mean(axis=1)
    spread=(w_gross/2)*ret_m-(w_gross/2)*ratio*ret_a
    if funding and F:   # short alt legs RECEIVE funding when positive; long majors PAY. Applied at settlement bars only.
        fa=pd.DataFrame({a:F[a].reindex(R.index) for a in alts if a in F}).fillna(0).mean(axis=1)
        fm=pd.DataFrame({m:F[m].reindex(R.index) for m in majors if m in F}).fillna(0).mean(axis=1)
        spread=spread+(w_gross/2)*ratio*fa-(w_gross/2)*fm
    leg_cost=(wm*sum(SIDE[m] for m in majors)+wa*sum(SIDE[a] for a in alts))/1e4
    out=pd.Series(0.0,index=R.index); inpos=False; n=0; sp=spread.values; rt=ratio.values
    for k in range(721,len(R)-1):
        if not inpos and on_enter(k): inpos=True; out.iat[k]=sp[k]-leg_cost*(1+rt[k])/2*1; n+=1
        elif inpos and on_exit(k): inpos=False; out.iat[k]=-leg_cost*(1+rt[k])/2
        elif inpos: out.iat[k]=sp[k]
    return out,n

WINDOWS={"TRAIN":("2023-01-22","2024-11-22 23:00"),"VAL":("2024-11-23","2025-04-21 23:00"),
         "TEST":("2025-04-22","2025-09-19 23:00"),"FWD (spent)":("2025-09-20","2026-09-01")}
def stats(s,lo,hi):
    w=s[(s.index>=pd.Timestamp(lo,tz="UTC"))&(s.index<=pd.Timestamp(hi,tz="UTC"))]
    if not len(w): return (0,0,0,0)
    eq=(1+w).cumprod(); yrs=len(w)/8760
    ret=(eq.iloc[-1]-1)*100; ann=((eq.iloc[-1])**(1/yrs)-1)*100 if yrs>0 else 0
    dd=(eq/eq.cummax()-1).min()*100; sh=w.mean()/w.std()*np.sqrt(8760) if w.std()>0 else 0
    return ret,ann,dd,sh
def report(label,s,n):
    print(f"\n{label}   (regime entries over full series: {n})")
    print(f"  {'window':12s} {'return %':>9s} {'ann %':>8s} {'maxDD %':>8s} {'Sharpe':>7s}")
    for k,(lo,hi) in WINDOWS.items():
        r,a,d,sh=stats(s,lo,hi); print(f"  {k:12s} {r:9.2f} {a:8.2f} {d:8.2f} {sh:7.2f}")
    yr=(1+s[s.index>="2023-01-22"]).groupby(s[s.index>="2023-01-22"].index.year).prod()-1
    print("  by year: "+"  ".join(f"{y}: {v*100:+.2f}%" for y,v in yr.items()))
