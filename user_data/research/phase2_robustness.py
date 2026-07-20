"""
Phase 2: Parameter robustness sweeps on the two leaders.

A robust strategy shows a PLATEAU: neighboring parameter values give similar
performance. A curve-fit strategy shows a SPIKE: tiny parameter moves kill it.

Sweep ranges: roughly +/-10% to +/-50% around base values.
Metric reported: full-window Sharpe and DD on BTC 1d (2018+ for ens3/adx).
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from validator import load, signal_to_returns

def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()
def _atr(df, n=14):
    h, l, c = df['high'], df['low'], df['close']
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()

btc = load('BTC/USDT', '1d')

def quick_perf(ret):
    eq = (1 + ret).cumprod()
    n_years = len(ret) / 365
    cagr = eq.iloc[-1] ** (1 / n_years) - 1 if eq.iloc[-1] > 0 else -1
    sharpe = ret.mean() / ret.std() * np.sqrt(365) if ret.std() > 0 else 0
    dd = (eq / eq.cummax() - 1).min()
    return sharpe, dd, cagr


def run(signal):
    r = signal_to_returns(btc, signal)
    return quick_perf(r["ret_net"])


print("=" * 78)
print("SWEEP 1: ens3 (SMA_n x ROC_n x EMA pair)  [base: 200 / 30 / 20-50]")
print("=" * 78)
c = btc['close']
for sma_n in [150, 175, 200, 225, 250]:
    for roc_n in [20, 25, 30, 35, 40]:
        s1 = (c > _sma(c, sma_n)).astype(float)
        s2 = (c.pct_change(roc_n) > 0).astype(float)
        s3 = (_ema(c, 20) > _ema(c, 50)).astype(float)
        sig = ((s1 + s2 + s3) >= 3).astype(float)
        sh, dd, cagr = run(sig)
        flag = " <== base" if (sma_n == 200 and roc_n == 30) else ""
        print(f"  sma={sma_n:3d} roc={roc_n:2d}: Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  CAGR {cagr*100:+6.1f}%{flag}")

print()
print("EMA pair sweep (sma=200, roc=30 fixed):")
for ef, es in [(10, 30), (15, 40), (20, 50), (25, 60), (30, 75)]:
    s1 = (c > _sma(c, 200)).astype(float)
    s2 = (c.pct_change(30) > 0).astype(float)
    s3 = (_ema(c, ef) > _ema(c, es)).astype(float)
    sig = ((s1 + s2 + s3) >= 3).astype(float)
    sh, dd, cagr = run(sig)
    flag = " <== base" if (ef, es) == (20, 50) else ""
    print(f"  ema {ef:2d}/{es:2d}: Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  CAGR {cagr*100:+6.1f}%{flag}")

print()
print("=" * 78)
print("SWEEP 2: adx_trend (ADX threshold x EMA pair)  [base: 25 / 20-50]")
print("=" * 78)
h, l = btc['high'], btc['low']
up = h.diff(); dn = -l.diff()
plus_dm = ((up > dn) & (up > 0)) * up
minus_dm = ((dn > up) & (dn > 0)) * dn
atr = _atr(btc, 14)
pdi = 100 * plus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
mdi = 100 * minus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
adx14 = dx.ewm(alpha=1/14, adjust=False).mean()

for thresh in [15, 20, 25, 30, 35]:
    for ef, es in [(15, 40), (20, 50), (25, 60)]:
        sig = ((adx14 > thresh) & (_ema(c, ef) > _ema(c, es))).astype(float)
        sh, dd, cagr = run(sig)
        flag = " <== base" if (thresh == 25 and (ef, es) == (20, 50)) else ""
        print(f"  adx>{thresh:2d} ema {ef:2d}/{es:2d}: Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  CAGR {cagr*100:+6.1f}%{flag}")

print()
print("=" * 78)
print("SWEEP 3: hmm_two_state (mom_n x vol quantile x sma_n)  [base: 30 / 0.80 / 100]")
print("=" * 78)
ret_d = c.pct_change()
for mom_n in [20, 25, 30, 35, 40]:
    for q in [0.70, 0.80, 0.90]:
        rv = ret_d.rolling(60).std() * np.sqrt(365)
        rv_high = rv.rolling(365).quantile(q)
        mom = c.pct_change(mom_n)
        sig = ((mom > 0) & (c > _sma(c, 100)) & (rv < rv_high)).astype(float)
        sh, dd, cagr = run(sig)
        flag = " <== base" if (mom_n == 30 and q == 0.80) else ""
        print(f"  mom={mom_n:2d} q={q:.2f}: Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  CAGR {cagr*100:+6.1f}%{flag}")
