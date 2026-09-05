"""Session-B: walk-forward for the five pre-registered strategies (strat5.py). 11 windows,
12m train / 3m test / 3m step, 2024-01 -> 2026-09. Only declared data-derived parameters are re-fit
per window (S1 thresholds; S5 model). Kill conditions were fixed in strat5.py's header and in the
research note BEFORE this ran. Survivors get cost stress (x2, x3)."""
import sys, time, pickle, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import strat5 as S
OUT = Path(__file__).resolve().parents[2] / "research" / "measurements" / "SESSION_B_strat5_wf.pkl"
WIN = S.windows(); t0 = time.time()
segs = {k: [] for k in ["S1 long (B2)", "S1 short (strict bear gate)", "S1 LS-Cascade combined",
                        "S2 TSMOM-4h LONG", "S2 TSMOM-4h SHORT", "S2 TSMOM-4h L/S", "S2 L/S LB42", "S2 L/S LB168",
                        "S3 AltBTC-MR", "S4 CascadeSpread", "S5 GBM p>=.60", "S5 GBM p>=.55", "S5 GBM p>=.65"]}
per_win = {k: [] for k in segs}; ntr = {"S1 long (B2)": 0, "S1 short (strict bear gate)": 0, "S4 CascadeSpread": 0, "S5 GBM p>=.60": 0}
for (a, b, c) in WIN:
    p = S.s1_fit(a, b); r = S.s1_run(p, b, c)
    segs["S1 long (B2)"].append(r["long"]); segs["S1 short (strict bear gate)"].append(r["short"]); segs["S1 LS-Cascade combined"].append(r["combined"])
    ntr["S1 long (B2)"] += r["n_long"]; ntr["S1 short (strict bear gate)"] += r["n_short"]
    segs["S2 TSMOM-4h LONG"].append(S.s2_run(90, "long", b, c)); segs["S2 TSMOM-4h SHORT"].append(S.s2_run(90, "short", b, c))
    segs["S2 TSMOM-4h L/S"].append(S.s2_run(90, "ls", b, c)); segs["S2 L/S LB42"].append(S.s2_run(42, "ls", b, c)); segs["S2 L/S LB168"].append(S.s2_run(168, "ls", b, c))
    segs["S3 AltBTC-MR"].append(S.s3_run(b, c))
    s4, n4 = S.s4_run(b, c); segs["S4 CascadeSpread"].append(s4); ntr["S4 CascadeSpread"] += n4
    for thr, key in ((0.60, "S5 GBM p>=.60"), (0.55, "S5 GBM p>=.55"), (0.65, "S5 GBM p>=.65")):
        s5, n5, mdl, base = S.s5_window(a, b, c, p_thr=thr)
        segs[key].append(s5)
        if thr == 0.60: ntr["S5 GBM p>=.60"] += n5; last_mdl, last_win = mdl, (a, b, c)
    for k in segs: per_win[k].append(S._stats(segs[k][-1])["ret"])
    print(f"  window test {b.date()} done  ({time.time()-t0:.0f}s)  thr_L {p['thr_L']*100:.2f}%  thr_S {p['thr_S']*100:.2f}%", flush=True)

res = {}
print("\n" + "=" * 140)
print(f"{'config':30s} {'WF ret':>7s} {'ann':>6s} {'DD':>6s} {'Sh':>5s} {'So':>5s} {'Cal':>5s} | {'2024':>6s} {'2025':>6s} {'2026':>6s} | {'365d':>6s} | +win  n")
print("-" * 140)
for k, segl in segs.items():
    s = pd.concat(segl).sort_index(); s = s[~s.index.duplicated()]; sm = S.summarise(s, k); res[k] = dict(series=s, sm=sm, per_win=per_win[k])
    pw = per_win[k]; print(f"{k:30s} {sm['ret']:7.1f} {sm['ann']:6.1f} {sm['dd']:6.1f} {sm['sh']:5.2f} {sm['so']:5.2f} {sm['cal']:5.2f} | {sm['y24']:+6.1f} {sm['y25']:+6.1f} {sm['y26']:+6.1f} | {sm['r365']:+6.1f} | {sum(x>0 for x in pw)}/{len(pw)}  {ntr.get(k,'')}")
print("-" * 140)
B2 = res["S1 long (B2)"]["sm"]
def K(name, cond, why): print(f"  {name:28s} {'KILLED' if cond else 'SURVIVES':9s} {why}")
print("\nKILL CHECKS (pre-registered):")
c1 = res["S1 LS-Cascade combined"]["sm"]; c1s = res["S1 short (strict bear gate)"]["sm"]
K("S1 LS-Cascade", c1["sh"] <= B2["sh"] or c1s["y24"] < -5, f"combined Sh {c1['sh']:.2f} vs B2 {B2['sh']:.2f}; short 2024 {c1s['y24']:+.1f}% (kill if < -5)")
c2 = res["S2 TSMOM-4h L/S"]["sm"]; c2s = res["S2 TSMOM-4h SHORT"]["sm"]
K("S2 TSMOM-4h", c2["sh"] <= 0.5 or c2s["y25"] <= 0, f"L/S Sh {c2['sh']:.2f} (kill <= 0.5); short 2025 {c2s['y25']:+.1f}% (kill <= 0)")
c3 = res["S3 AltBTC-MR"]["sm"]; K("S3 AltBTC-MR", c3["sh"] <= 0.3, f"Sh {c3['sh']:.2f} (kill <= 0.3)")
c4 = res["S4 CascadeSpread"]["sm"]; K("S4 CascadeSpread", c4["sh"] <= 0.3, f"Sh {c4['sh']:.2f} (kill <= 0.3); {ntr['S4 CascadeSpread']} spreads")
c5 = res["S5 GBM p>=.60"]["sm"]; K("S5 GBM-Cascade", c5["sh"] <= B2["sh"], f"Sh {c5['sh']:.2f} vs B2 {B2['sh']:.2f}; n {ntr['S5 GBM p>=.60']}")
try:
    from sklearn.inspection import permutation_importance
    a, b, c = last_win; X, y = [], []
    for i in S.P9:
        f = S.feats(i); w = f[(f.index >= b) & (f.index < c)].dropna(subset=S.FEATS + ["fwd6"]); X.append(w[S.FEATS]); y.append((w["fwd6"] > 2 * S.SIDE[i] / 1e4).astype(int))
    X = pd.concat(X); y = pd.concat(y); pi = permutation_importance(last_mdl, X, y, n_repeats=5, random_state=0, scoring="roc_auc")
    print("  S5 permutation importance (last window, AUC drop): " + ", ".join(f"{f} {v:+.3f}" for f, v in sorted(zip(S.FEATS, pi.importances_mean), key=lambda x: -x[1])))
except Exception as e: print("  (importance skipped:", e, ")")
print("\nCOST STRESS on survivors (SIDE x2, x3), full WF re-run:")
surv = [k for k, cond in (("S1 LS-Cascade combined", not (c1["sh"] <= B2["sh"] or c1s["y24"] < -5)), ("S2 TSMOM-4h L/S", not (c2["sh"] <= 0.5 or c2s["y25"] <= 0)),
                           ("S3 AltBTC-MR", c3["sh"] > 0.3), ("S4 CascadeSpread", c4["sh"] > 0.3), ("S5 GBM p>=.60", c5["sh"] > B2["sh"])) if cond]
base_side = dict(S.SIDE)
for k in surv:
    for mult in (2.0, 3.0):
        for i in S.SIDE: S.SIDE[i] = base_side[i] * mult
        segl = []
        for (a, b, c) in WIN:
            if k.startswith("S1"): segl.append(S.s1_run(S.s1_fit(a, b), b, c)["combined"])
            elif k.startswith("S2"): segl.append(S.s2_run(90, "ls", b, c))
            elif k.startswith("S3"): segl.append(S.s3_run(b, c))
            elif k.startswith("S4"): segl.append(S.s4_run(b, c)[0])
            elif k.startswith("S5"): segl.append(S.s5_window(a, b, c, 0.60)[0])
        s = pd.concat(segl).sort_index(); m = S._stats(s); print(f"  {k:28s} x{mult}: ret {m['ret']:+6.1f}%  Sh {m['sh']:5.2f}  DD {m['dd']:6.1f}%")
    for i in S.SIDE: S.SIDE[i] = base_side[i]
if not surv: print("  (no survivors)")
pickle.dump({k: {"series": v["series"], "sm": v["sm"], "per_win": v["per_win"]} for k, v in res.items()}, open(OUT, "wb"))
print(f"\nsaved {OUT.name}; elapsed {time.time()-t0:.0f}s")
