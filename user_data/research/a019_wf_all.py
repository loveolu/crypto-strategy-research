"""CRYPTO-EXP-012: walk-forward (12m train / 3m test / 3m step, 11 windows) for the cascade family.
Configs pre-registered: S2-strict at 1h/2h/4h/8h; B2 = 4h + BTC-drop condition; B3 = 4h vol-expansion
(opposite mechanism). Only the magnitude threshold is re-fit per window. Output saved for ranking."""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,r"C:\Users\Comec\Projects\freqtrade\user_data\research"); import wf_cascade as WF, s2_cascade as S2
CONF=[("S2-strict 1h","1h",{}),("S2-strict 2h","2h",{}),("S2-strict 4h","4h",{}),("S2-strict 8h","8h",{}),
      ("B2 4h + BTC-drop cond","4h",{"btc_cond":True}),("B3 4h vol-EXPANSION (opposite)","4h",{"pct_expansion":True})]
out={}
print(f"{'config':32s} {'WF ret':>8s} {'ann':>7s} {'DD':>7s} {'Sh':>6s} {'So':>6s} {'Cal':>5s} | {'2024':>7s} {'2025':>7s} {'2026':>7s} | {'90d':>6s} {'180d':>6s} {'365d':>6s} | +win")
print("-"*130)
for lbl,tf,kw in CONF:
    oos,tab=WF.walk_forward(tf,**kw); sm=WF.summarise(oos,tf,lbl); out[lbl]=dict(oos=oos,tab=tab,sm=sm)
    y=sm["yrs"]; r=sm["rec"]
    print(f"{lbl:32s} {sm['wf_ret']:8.1f} {sm['ann']:7.1f} {sm['dd']:7.1f} {sm['sh']:6.2f} {sm['so']:6.2f} {sm['cal']:5.2f} | {y.get(2024,0)*100:+7.1f} {y.get(2025,0)*100:+7.1f} {y.get(2026,0)*100:+7.1f} | {r[90]:+6.1f} {r[180]:+6.1f} {r[365]:+6.1f} | {(tab.ret>0).sum()}/{len(tab)}")
print("\nper-window detail, S2-strict 4h:")
t=out["S2-strict 4h"]["tab"]; print("  "+"  ".join(f"{r.test_start}:{r.ret:+5.1f}%/{r.n}t(thr {r.thr*100:.1f}%)" for r in t.itertuples()))
print("per-window detail, B2 4h+BTC:")
t=out["B2 4h + BTC-drop cond"]["tab"]; print("  "+"  ".join(f"{r.test_start}:{r.ret:+5.1f}%/{r.n}t" for r in t.itertuples()))
pickle.dump({k:{"oos":v["oos"],"tab":v["tab"],"sm":v["sm"]} for k,v in out.items()},open(r"research/measurements/A019_wf.pkl","wb"))
