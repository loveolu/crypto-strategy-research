"""A-011: maker-vs-taker realized cost from 1m OKX candles + sampled books.
Question: if a signal says BUY at bar t, what does execution actually cost?

TAKER  : crosses the spread now. cost = half_spread + fee_taker + book-walk slippage.
MAKER  : posts a bid at (close - half_spread). Fills only if next bar's low trades
         through it. cost = fee_maker - half_spread + ADVERSE SELECTION, where
         adverse selection a_k = E[drift_k | filled] - E[drift_k | all]  (bps),
         drift_k = close[t+k]/close[t] - 1. Negative a_k = price kept falling after
         filling you. Plus the trade is MISSED with prob (1 - fill rate).
Symmetric on the sell side; both sides averaged. TRAIN/TEST/holdout irrelevant:
this measures execution, not a signal, on the most recent 30 days."""
import json, glob, os, numpy as np, pandas as pd
D="user_data/research/data/okx_micro"
FEE_MAKER, FEE_TAKER = 2.0, 5.0     # bps/side, OKX regular tier (validator.COST_MODEL)
CTVAL={'BTC':0.01,'ETH':0.1,'SOL':1,'BNB':0.01,'XRP':100,'ADA':100,'AVAX':1,'DOT':1,'LINK':1}
HORIZONS=(1,5,15,60)

def load_candles(iid):
    rows=[]
    for line in open(f"{D}/{iid}_1m_raw.jsonl",encoding="utf-8"):
        rows.extend(json.loads(line)["data"])
    df=pd.DataFrame(rows,columns=["ts","o","h","l","c","v","vc","vq","conf"]).astype({"ts":"int64","o":float,"h":float,"l":float,"c":float})
    return df.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)

def spread_and_slippage(inst):
    """median quoted spread (bps) and book-walk slippage (bps beyond mid) for order sizes."""
    sp=[]; slip={1000:[],5000:[],20000:[]}
    for line in open(f"{D}/book_samples.jsonl",encoding="utf-8"):
        j=json.loads(line)
        if not j["instId"].startswith(inst+"-"): continue
        b=j["book"]; bid=float(b["bids"][0][0]); ask=float(b["asks"][0][0]); mid=(bid+ask)/2
        sp.append((ask-bid)/mid*1e4)
        for usd in slip:
            need=usd/(CTVAL[inst]*mid); got=0.0; cost=0.0
            for px,sz,*_ in b["asks"]:
                px=float(px); sz=float(sz); take=min(sz,need-got); cost+=take*px; got+=take
                if got>=need-1e-12: break
            slip[usd].append((cost/got/mid-1)*1e4 if got>0 else np.nan)
    return float(np.median(sp)), {k:float(np.nanmedian(v)) for k,v in slip.items()}

out=[]
for f in sorted(glob.glob(f"{D}/*_1m_raw.jsonl")):
    inst=os.path.basename(f).split("-")[0]
    df=load_candles(f"{inst}-USDT-SWAP"); c=df.c.to_numpy(); l=df.l.to_numpy(); h=df.h.to_numpy(); n=len(c)
    sp,slip=spread_and_slippage(inst); hs=sp/2
    rec={"inst":inst,"bars":n,"days":round(n/1440,1),"spread_bps":sp,"half":hs,**{f"slip_${k//1000}k":v for k,v in slip.items()}}
    for K in HORIZONS:
        T=n-K-1
        drift=(c[1+K:1+K+T]/c[:T]-1)*1e4           # drift from bar t close to bar t+K close (execution at t+1 open ~ t close)
        # BUY side: bid at c[t]*(1-hs); filled if low[t+1] < bid  (strict: price traded THROUGH)
        bid=c[:T]*(1-hs/1e4); fb=l[1:1+T]<bid
        # SELL side: ask at c[t]*(1+hs); filled if high[t+1] > ask
        ask=c[:T]*(1+hs/1e4); fs=h[1:1+T]>ask
        a_buy = drift[fb].mean()-drift.mean()      # want positive drift after buying; conditional-on-fill deficit
        a_sell= -(drift[fs].mean()-drift.mean())   # want negative drift after selling; sign flipped so negative = bad
        a=(a_buy+a_sell)/2; p=(fb.mean()+fs.mean())/2
        rec[f"fill_{K}"]=p; rec[f"adv_{K}"]=a
    out.append(rec)

R=pd.DataFrame(out).set_index("inst").loc[[i for i in ['BTC','ETH','SOL','BNB','XRP','ADA','AVAX','DOT','LINK'] if i in [o['inst'] for o in out]]]
print(f"OKX 1m candles, {R.days.min()}-{R.days.max()} days per instrument. bps everywhere.\n")
print("--- 1. QUOTED SPREAD & TAKER SLIPPAGE (book walk, beyond mid) ---")
print(f"{'inst':5s} {'spread':>7s} {'slip $1k':>9s} {'slip $5k':>9s} {'slip $20k':>10s}")
for i,r in R.iterrows(): print(f"{i:5s} {r.spread_bps:7.3f} {r['slip_$1k']:9.3f} {r['slip_$5k']:9.3f} {r['slip_$20k']:10.3f}")
print(f"{'MEAN':5s} {R.spread_bps.mean():7.3f} {R['slip_$1k'].mean():9.3f} {R['slip_$5k'].mean():9.3f} {R['slip_$20k'].mean():10.3f}")

print("\n--- 2. MAKER FILL RATE (next bar trades through your quote) ---")
print(f"{'inst':5s} "+" ".join(f"{'fill@'+str(k)+'m':>9s}" for k in HORIZONS))
for i,r in R.iterrows(): print(f"{i:5s} "+" ".join(f"{r[f'fill_{k}']*100:8.1f}%" for k in HORIZONS))

print("\n--- 3. ADVERSE SELECTION a_k = E[drift|filled] - E[drift|all]  (negative = price kept going against you) ---")
print(f"{'inst':5s} "+" ".join(f"{'a@'+str(k)+'m':>8s}" for k in HORIZONS))
for i,r in R.iterrows(): print(f"{i:5s} "+" ".join(f"{r[f'adv_{k}']:8.2f}" for k in HORIZONS))
print(f"{'MEAN':5s} "+" ".join(f"{R[f'adv_{k}'].mean():8.2f}" for k in HORIZONS))

print("\n--- 4. ALL-IN COST PER SIDE, $5k order (bps) ---")
print(f"{'inst':5s} {'TAKER':>7s} | "+" ".join(f"{'MAKER@'+str(k)+'m':>10s}" for k in HORIZONS)+"  | model TAKER=9.0")
tk=[];mk={k:[] for k in HORIZONS}
for i,r in R.iterrows():
    taker=r.half+FEE_TAKER+r['slip_$5k']; tk.append(taker)
    row=f"{i:5s} {taker:7.2f} | "
    for k in HORIZONS:
        m=FEE_MAKER-r.half-r[f'adv_{k}']; mk[k].append(m); row+=f"{m:10.2f} "
    print(row)
print(f"{'MEAN':5s} {np.mean(tk):7.2f} | "+" ".join(f"{np.mean(mk[k]):10.2f}" for k in HORIZONS))
print("\nRound trip = 2x per-side. Model assumed 18.0 bps taker RT.")
R.to_csv(f"{D}/adverse_selection_results.csv")
