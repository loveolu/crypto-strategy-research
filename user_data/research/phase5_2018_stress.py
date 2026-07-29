"""Phase 5a: 2018-bear stress test (BTC-only variant, 8.4y window)."""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from validator import load

# FROZEN HISTORICAL COST — see the identical note in phase4_deep_validation.py.
# This reproduces a June-2026 run at 0.15%/side. New work must use
# validator.per_side_cost() (see COST_MODEL).
FEE = 0.0015
def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()

btc = load('BTC/USDT', '1d')
close = btc['close']

s1 = (close > _sma(close, 200)).astype(float)
s2 = (close.pct_change(30) > 0).astype(float)
s3 = (_ema(close, 20) > _ema(close, 50)).astype(float)
core = ((s1 + s2 + s3) >= 3).astype(float)
rv = close.pct_change().rolling(30).std() * np.sqrt(365)
scale = (0.40 / rv).clip(0, 1)
sig = (core * scale / 0.25).round() * 0.25
sig = sig.clip(0, 1)

pos = sig.shift(2).fillna(0)
net = pos * close.pct_change().fillna(0) - pos.diff().abs().fillna(pos.abs()) * FEE

ret = net.dropna()
eq = (1 + ret).cumprod()
yrs = len(ret) / 365
cagr = eq.iloc[-1] ** (1 / yrs) - 1
sharpe = ret.mean() / ret.std() * np.sqrt(365)
dd = (eq / eq.cummax() - 1).min()
yearly = (1 + ret).groupby(ret.index.year).prod() - 1
print(f"BTC-only TrendVolTarget, {yrs:.1f}y window ({ret.index[0].date()}..{ret.index[-1].date()})")
print(f"CAGR {cagr*100:+.1f}%  Sharpe {sharpe:.2f}  MaxDD {dd*100:.1f}%")
print("Yearly: " + " ".join(f"{y}:{v*100:+.1f}%" for y, v in yearly.items()))

# 2018 detail: was it in the market during the crash?
print()
mask_2018 = (ret.index.year == 2018)
print(f"2018: return {((1+ret[mask_2018]).prod()-1)*100:+.2f}%  "
      f"days in market: {(pos[mask_2018] > 0).sum()}/{mask_2018.sum()}  "
      f"avg position when in: {pos[mask_2018][pos[mask_2018]>0].mean():.2f}")
mask_2022 = (ret.index.year == 2022)
print(f"2022: return {((1+ret[mask_2022]).prod()-1)*100:+.2f}%  "
      f"days in market: {(pos[mask_2022] > 0).sum()}/{mask_2022.sum()}")
# trade count estimate: position changes
changes = (sig.diff().abs() > 0).sum()
print(f"\nPosition adjustments over {yrs:.1f}y: {changes} (~{changes/yrs:.0f}/yr)")
# discrete entries from flat
entries = ((sig > 0) & (sig.shift(1) == 0)).sum()
print(f"Entries from flat: {entries} (~{entries/yrs:.1f}/yr)")
