"""Walk-forward harness for the cascade family. Rolling TRAIN 12 months -> TEST 3 months, step 3 months.
Per window the ONLY re-fit is the magnitude threshold (25th percentile of entry |mom| among the train
window's loose triggers). Everything else is the fixed mechanical mapping. Non-overlap is honoured by
running the strict rule on the full series per window and keeping that window's test-segment trades."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,r"C:\Users\Comec\Projects\freqtrade\user_data\research"); import s2_cascade as S2
MAP={"1h":dict(tf="1h",W=168,PW=720,HOLD=24,mom_bars=24,gate_shift=24),
     "2h":dict(tf="2h",W=84,PW=360,HOLD=12,mom_bars=12,gate_shift=12),
     "4h":dict(tf="4h",W=42,PW=180,HOLD=6,mom_bars=6,gate_shift=6),
     "8h":dict(tf="8h",W=21,PW=90,HOLD=3,mom_bars=3,gate_shift=3)}
PPY={"1h":8760,"2h":4380,"4h":2190,"8h":1095}
START=pd.Timestamp("2023-01-22",tz="UTC"); END=pd.Timestamp("2026-09-01",tz="UTC")
def windows(train_m=12,test_m=3,step_m=3):
    out=[]; t0=START
    while True:
        t1=t0+pd.DateOffset(months=train_m); t2=min(t1+pd.DateOffset(months=test_m),END)
        if t1>=END: break
        out.append((t0,t1,t2)); t0=t0+pd.DateOffset(months=step_m)
    return out
def walk_forward(tf,univ=S2.P9,pct_expansion=False,**extra):
    K={**MAP[tf],**extra}; segs=[]; rows=[]
    loose={i:S2.trades(i,**K)[0] for i in univ}
    for (a,b,c) in windows():
        tr_train=pd.concat([loose[i][(loose[i].entry>=a)&(loose[i].entry<b)] for i in univ])
        if len(tr_train)<20: continue
        thr=float(np.percentile(tr_train.entry_mom,75) if pct_expansion else -np.percentile(tr_train.entry_mom,25))
        S=[];T=[]
        for i in univ:
            tr,s=S2.trades(i,mom_thr=thr,expansion=pct_expansion,**K)
            S.append(s[(s.index>=b)&(s.index<c)]); T.append(tr[(tr.entry>=b)&(tr.entry<c)])
        seg=pd.concat(S,axis=1).mean(axis=1); trs=pd.concat(T) if len(T) else pd.DataFrame()
        segs.append(seg); m=S2.metrics(seg,trs,len(univ),ppy=PPY[tf]) if len(trs) else {}
        rows.append(dict(test_start=b.date(),thr=thr,n=m.get("n",0),ret=m.get("ret",0),sh=m.get("sharpe",0)))
    oos=pd.concat(segs).sort_index(); oos=oos[~oos.index.duplicated()]
    return oos,pd.DataFrame(rows)
def summarise(oos,tf,label):
    eq=(1+oos).cumprod(); yrs=len(oos)/PPY[tf]; ann=(eq.iloc[-1]**(1/yrs)-1)*100
    dd=(eq/eq.cummax()-1).min()*100; sh=oos.mean()/oos.std()*np.sqrt(PPY[tf]) if oos.std()>0 else 0
    neg=np.sqrt((np.minimum(oos,0)**2).mean()); so=oos.mean()/neg*np.sqrt(PPY[tf]) if neg>0 else 0
    yr=(1+oos).groupby(oos.index.year).prod()-1
    rec={}
    for d in (90,180,365):
        w=oos[oos.index>=END-pd.Timedelta(days=d)]; rec[d]=((1+w).prod()-1)*100 if len(w) else 0
    return dict(label=label,tf=tf,wf_ret=(eq.iloc[-1]-1)*100,ann=ann,dd=dd,sh=sh,so=so,cal=ann/abs(dd) if dd<0 else 0,
                span=f"{oos.index.min().date()}..{oos.index.max().date()}",yrs=yr.to_dict(),rec=rec)
if __name__=="__main__":
    print(f"windows: {len(windows())}  first test {windows()[0][1].date()}  last test ends {windows()[-1][2].date()}")
