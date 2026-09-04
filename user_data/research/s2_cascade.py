"""S2 trend-gated cascade reversion — parameterised core with trade-level output.
Base (as A-012/A-013/A-014): W=168 dsd window, PW=720 rolling-percentile window, THR=0.80 entry,
EXIT=0.50, HOLD=24 bars, mom_24<0, daily gate close>SMA200 & EMA20>EMA50 (prior day), taker at
next-bar open, universe BTC/ETH/SOL/XRP/BNB, 1/N sizing. All indicators on full series."""
import functools, numpy as np, pandas as pd
ROOT=r"C:\Users\Comec\Projects\freqtrade"; FUT=f"{ROOT}/user_data/data/okx/futures"
P9=["BTC","ETH","SOL","BNB","XRP","ADA","AVAX","DOT","LINK"]; U5=["BTC","ETH","SOL","XRP","BNB"]
COSTS=pd.read_csv(f"{ROOT}/user_data/research/data/okx_micro/adverse_selection_results.csv").set_index("inst")
FEE_T,FEE_M=5.0,2.0
def side_taker(i): return float(COSTS.loc[i,"half"]+FEE_T+COSTS.loc[i,"slip_$5k"])
def half(i): return float(COSTS.loc[i,"half"])

@functools.lru_cache(maxsize=None)
def load(i,tf):
    d=pd.read_feather(f"{FUT}/{i}_USDT_USDT-{tf}-futures.feather").set_index("date").sort_index()
    return d[~d.index.duplicated()]

@functools.lru_cache(maxsize=None)
def gate(i,slope=False):
    c=load(i,"1d")["close"]; sma=c.rolling(200).mean()
    g=(c>sma)&(c.ewm(span=20).mean()>c.ewm(span=50).mean())
    if slope: g=g&(sma>sma.shift(20))           # SMA200 must be RISING (Kaufman trend-maturity)
    return g.astype(float)

@functools.lru_cache(maxsize=None)
def cond(i,W,PW):
    d=load(i,"1h"); c=d["close"]; r=c/c.shift(1)-1
    dsd=np.sqrt((np.minimum(r,0)**2).rolling(W).mean()); usd=np.sqrt((np.maximum(r,0)**2).rolling(W).mean())
    return pd.DataFrame({"o":d["open"],"h":d["high"],"l":d["low"],"c":c,"r":r,
        "pct":dsd.rolling(PW).rank(pct=True),"upct":usd.rolling(PW).rank(pct=True),"mom":c/c.shift(24)-1})

def trades(i,W=168,PW=720,THR=0.80,EXIT=0.50,HOLD=24,delay=0,gated=True,short=False,cost="taker",cost_mult=1.0,mom_thr=0.0,slope=False):
    """Returns DataFrame of trades and a 1h net-return Series for this instrument (1.0 = full sleeve)."""
    x=cond(i,W,PW); n=len(x)
    g=gate(i,slope).reindex(x.index,method="ffill").shift(24).fillna(0).values if gated else np.ones(n)
    o,l,h,c,pct,upct,mom=x.o.values,x.l.values,x.h.values,x.c.values,x.pct.values,x.upct.values,x.mom.values
    st=side_taker(i)*cost_mult; hs=half(i)
    ret=np.zeros(n); rows=[]; t=PW
    while t<n-HOLD-delay-3:
        if short: trig=(upct[t]>=THR) and (mom[t]>0) and (g[t]==0)
        else:     trig=(pct[t]>=THR) and (mom[t]<=-mom_thr) and (g[t]>0)
        if not trig: t+=1; continue
        e=t+1+delay
        if cost=="maker" and not short:
            bid=c[t]*(1-hs/1e4)
            if not (l[e]<bid): t+=1; continue
            ep=bid; ec=FEE_M*cost_mult
        else:
            ep=o[e]*(1+(st-FEE_T*cost_mult)/1e4*(-1 if short else 1)); ec=FEE_T*cost_mult
        k=e; end=min(e+HOLD,n-2); sig=upct if short else pct
        while k<end and not (sig[k]<EXIT): k+=1
        xp=o[k+1]*(1-(st-FEE_T*cost_mult)/1e4*(-1 if short else 1)); xc=FEE_T*cost_mult
        gross=(ep/xp-1) if short else (xp/ep-1); cst=(ec+xc)/1e4; net=gross-cst
        ret[k+1]=net; rows.append((x.index[e],x.index[k+1],gross,net,cst,k+1-e,pct[t],mom[t])); t=k+2
    tr=pd.DataFrame(rows,columns=["entry","exit","gross","net","cost","bars","entry_pct","entry_mom"])
    return tr,pd.Series(ret,index=x.index)

def basket(univ=U5,**kw):
    T=[];S=[]
    for i in univ:
        tr,s=trades(i,**kw); tr["inst"]=i; T.append(tr); S.append(s)
    tr=pd.concat(T).sort_values("entry").reset_index(drop=True); s=pd.concat(S,axis=1).mean(axis=1)
    return tr,s

def metrics(s,tr,n_univ,ppy=8760):
    s=s.dropna()
    if not len(s) or not len(tr): return {}
    eq=(1+s).cumprod(); yrs=len(s)/ppy; ann=(eq.iloc[-1]**(1/yrs)-1) if yrs>0 else 0
    dd=(eq/eq.cummax()-1).min(); neg=s[s<0]
    d=(1+s).resample("D").prod()-1; wk=(1+s).resample("W").prod()-1; mo=(1+s).resample("ME").prod()-1
    net=tr.net.values; wins=net[net>0]; loss=net[net<0]
    streak=0;mx=0
    for v in net: streak=streak+1 if v<0 else 0; mx=max(mx,streak)
    return dict(ret=(eq.iloc[-1]-1)*100, ann=ann*100, dd=dd*100,
        sharpe=s.mean()/s.std()*np.sqrt(ppy) if s.std()>0 else 0,
        sortino=s.mean()/np.sqrt((np.minimum(s,0)**2).mean())*np.sqrt(ppy) if (s<0).any() else 0,
        calmar=ann/abs(dd) if dd<0 else 0, n=len(tr), per_day=len(tr)/(len(s)/24),
        winrate=(net>0).mean()*100, pf=wins.sum()/abs(loss.sum()) if len(loss) and loss.sum()<0 else np.inf,
        exp_bps=net.mean()*1e4, avg_win=wins.mean()*1e4 if len(wins) else 0, avg_loss=loss.mean()*1e4 if len(loss) else 0,
        median=np.median(net)*1e4, hold_h=tr.bars.mean(), fees_pct=tr.cost.sum()/n_univ*100,
        streak=mx, worst_day=d.min()*100, worst_wk=wk.min()*100, worst_mo=mo.min()*100,
        pos_days=(d>0).sum()/max((d!=0).sum(),1)*100)
