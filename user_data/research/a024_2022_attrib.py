"""2022 attribution: is the TSMOM-short +50% one coin, and how does it compare to the naive ceiling?"""
import sys, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import strat5 as S
S.P9 = [p for p in S.P9 if p != "BNB"]; S.ALT7 = [p for p in S.ALT7 if p != "BNB"]
for fn in (S.h1, S.d1, S.h4, S.idx4, S.gates, S.feats): fn.cache_clear()
lo, hi = pd.Timestamp("2022-02-08", tz="UTC"), pd.Timestamp("2023-01-01", tz="UTC")
print("per-coin: buy-and-hold Feb-Dec 2022 | TSMOM-4h SHORT-only sleeve (its own 1/8 of the book) | avg vol-target weight")
tot = []
for i in S.P9:
    f = S.feats(i); c = f["c"]; r = f["r"]; w = (f.index >= lo) & (f.index < hi)
    hold = (c[w].iloc[-1] / c[w].iloc[0] - 1) * 100
    sig = np.sign(c / c.shift(90) - 1); vol = r.rolling(30).std() * np.sqrt(S.PPY); wt = (0.40 / vol).clip(0, 1)
    pos = (sig * wt).clip(upper=0).fillna(0); ret = pos.shift(1) * r - (pos.shift(1) - pos.shift(2)).abs() * S.SIDE[i] / 1e4
    sl = ((1 + ret[w]).prod() - 1) * 100; tot.append(sl)
    print(f"  {i:5s} hold {hold:+7.1f}%   short-sleeve {sl:+6.1f}%   avg |w| {pos[w].abs().mean():.2f}   share of bars short {(pos[w] < 0).mean():.0%}")
print(f"  equal-weight short book = mean of sleeves = {np.mean(tot):+.1f}%   (max single sleeve {max(tot):+.1f}%, without it {np.mean(sorted(tot)[:-1]):+.1f}%)")
R = pd.DataFrame({i: S.feats(i)["r"] for i in S.P9}).mean(axis=1)[(S.idx4() >= lo) & (S.idx4() < hi)]
naive = ((1 - R).prod() - 1) * 100   # always short the basket 1:1, no costs
print(f"\nceiling: always-short the 8-coin basket 1:1, no costs, no signal, Feb-Dec 2022 = {naive:+.1f}%")
print(f"TSMOM short captured {np.mean(tot)/naive*100:.0f}% of that ceiling at roughly half size (vol-target) with lag, whipsaw and costs.")
