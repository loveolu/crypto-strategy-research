"""2022 out-of-sample test. No threshold was ever fit on 2022 (TRAIN = 2023-01..2024-11). BNB starts
2022-12-23, so this uses the other 8 perps. The daily SMA200 gate needs 200 days -> gated strategies
can trade from 2022-07-19; gate-free (market-neutral) strategies from 2022-02-08 after the 222-bar
dispersion warmup."""
import sys, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import strat5 as S
S.P9 = [p for p in S.P9 if p != "BNB"]; S.ALT7 = [p for p in S.ALT7 if p != "BNB"]
for fn in (S.h1, S.d1, S.h4, S.idx4, S.gates, S.feats): fn.cache_clear()
ix = S.idx4(); print(f"8-perp common 4h index: {ix.min().date()} .. {ix.max().date()}")
H2 = (pd.Timestamp("2022-07-19", tz="UTC"), pd.Timestamp("2023-01-01", tz="UTC"))
FY = (pd.Timestamp("2022-02-08", tz="UTC"), pd.Timestamp("2023-01-01", tz="UTC"))
def st(s, lo, hi):
    m = S._stats(s, lo, hi); return f"ret {m['ret']:+6.1f}%  Sh {m['sh']:5.2f}  DD {m['dd']:6.1f}%"
p = S.s1_fit(pd.Timestamp("2023-01-22", tz="UTC"), pd.Timestamp("2024-11-22", tz="UTC"))
print(f"thresholds from TRAIN 2023-24: long <= -{p['thr_L']*100:.2f}%, short >= +{p['thr_S']*100:.2f}%   (never saw 2022)\n")
gu = pd.concat([S.gates(i)[0] for i in S.P9], axis=1).mean(axis=1); gd = pd.concat([S.gates(i)[1] for i in S.P9], axis=1).mean(axis=1)
w = (gu.index >= H2[0]) & (gu.index < H2[1])
print(f"2022-H2 gate state: uptrend gate ON {gu[w].mean():.0%} of bars, strict-bear gate ON {gd[w].mean():.0%}\n")
print("=== 2022, 8 perps, OUT-OF-SAMPLE ===")
R = pd.DataFrame({i: S.feats(i)["r"] for i in S.P9}).mean(axis=1)
print(f"  HOLD basket (8 coins)      H2 {st(R, *H2)}   |  Feb-Dec {st(R, *FY)}")
r = S.s1_run(p, *H2)
print(f"  B2 long (gated)            H2 {st(r['long'], *H2)}   trades {r['n_long']}")
print(f"  short leg (strict bear)    H2 {st(r['short'], *H2)}   trades {r['n_short']}")
print(f"  LS-Cascade combined        H2 {st(r['combined'], *H2)}")
S4 = {}
for k in (3, 1):
    s, _ = S.s4_run(*FY, k=k); nz = s[s != 0]; S4[k] = s
    print(f"  CascadeSpread k={k} (neutral) Feb-Dec {st(s, *FY)}   spreads {len(nz)}   |  H2 only {st(s, *H2)}")
s = S.s2_run(90, "ls", *FY); print(f"  TSMOM-4h L/S               Feb-Dec {st(s, *FY)}")
s = S.s2_run(90, "short", *FY); print(f"  TSMOM-4h SHORT only        Feb-Dec {st(s, *FY)}")
s = S.s3_run(*FY); print(f"  AltBTC-MR (neutral)        Feb-Dec {st(s, *FY)}")
b2 = r["long"]; s4 = S4[3].reindex(b2.index).fillna(0)
pf = 0.5 * b2 + 0.5 * s4; print(f"  B2 + CascadeSpread 50/50   H2 {st(pf, *H2)}")
print("\n  by month 2022 (B2 long / CascadeSpread k=3 / k=1 / hold):")
for m in range(2, 13):
    lo = pd.Timestamp(f"2022-{m:02d}-01", tz="UTC"); hi = lo + pd.DateOffset(months=1)
    f = lambda s: ((1 + s[(s.index >= lo) & (s.index < hi)]).prod() - 1) * 100
    print(f"    2022-{m:02d}: B2 {f(b2) if m >= 7 else float('nan'):+6.1f}%   spread3 {f(S4[3]):+5.1f}%   spread1 {f(S4[1]):+5.1f}%   hold {f(R):+6.1f}%")
