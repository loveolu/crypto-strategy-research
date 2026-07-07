"""
Phase 11: Deflated Sharpe Ratio audit of the champion (TrendVolTarget).

Uses freqtrade_dsr.py (user-provided, ported from Forven). Two angles:

1. Per-trade DSR from the REAL freqtrade engine backtest zip (2026-06-11).
2. Per-day DSR from the harness daily return stream (the statistically
   stronger test: ~2000 observations instead of ~50 trades).

The single most important input is n_trials. Honest accounting across the
whole project:
  - 61 constructs in the autonomous search
  - ~24 more in the deep-dive phases (blends, sweeps, overlays, universes)
  - parameter sweep variants (SMA 150-250 x ROC 20-40 x tv 30-50 ...)
So we report DSR at n_trials = 85 (constructs), 300 (constructs x sweep
variants, conservative), and 1000 (paranoid upper bound).
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')

import numpy as np
import pandas as pd
from pathlib import Path

from freqtrade_dsr import deflated_sharpe_ratio, returns_from_freqtrade

ZIP = 'C:/Users/Comec/Projects/freqtrade/user_data/backtest_results/backtest-result-2026-06-11_01-06-44.zip'

# ---------------------------------------------------------------- per-trade
print("=" * 78)
print("1) PER-TRADE DSR — real freqtrade engine run (TrendVolTarget, 6.5y)")
print("=" * 78)
trades = returns_from_freqtrade(ZIP)
print(f"trades: {len(trades)}  mean {np.mean(trades)*100:+.2f}%  win rate {np.mean([t > 0 for t in trades])*100:.0f}%")
for nt in (85, 300, 1000):
    res = deflated_sharpe_ratio(trades, n_trials=nt)
    print(f"  n_trials={nt:5d}:  DSR={res['dsr']:.4f}   sr_hat/trade={res['sr_hat_per_trade']:+.3f}  "
          f"benchmark sr0={res['sr0_benchmark']:.3f}  skew={res['skew']:+.2f} kurt={res['kurtosis']:.1f}")

# ---------------------------------------------------------------- per-day
print()
print("=" * 78)
print("2) PER-DAY DSR — harness daily returns (TVT BTC+ETH, phase9 replication)")
print("=" * 78)
FEE = 0.0015
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()
def load_fut(sym):
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype({c: float for c in ['open', 'high', 'low', 'close', 'volume']})

SYMS = ['BTC', 'ETH']
closes = pd.DataFrame({s: load_fut(s)['close'] for s in SYMS}).sort_index()
ret_mat = closes.pct_change()
core, scale = pd.DataFrame(index=closes.index), pd.DataFrame(index=closes.index)
for s in SYMS:
    c = closes[s]
    core[s] = ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)
    rv = c.pct_change().rolling(30).std() * np.sqrt(365)
    scale[s] = (0.40 / rv).clip(0, 1)
W = (((core * scale) / 0.25).round() * 0.25).clip(0, 1) / len(SYMS)
pos = W.shift(2).fillna(0)
gross = (pos * ret_mat.fillna(0)).sum(axis=1)
turn = pos.diff().abs().sum(axis=1)
turn.iloc[0] = pos.iloc[0].abs().sum()
daily = (gross - turn * FEE).dropna()

ann_sr = daily.mean() / daily.std() * np.sqrt(365)
print(f"days: {len(daily)}   annualized Sharpe {ann_sr:.2f}")
for nt in (85, 300, 1000):
    res = deflated_sharpe_ratio(daily.tolist(), n_trials=nt)
    sr0_ann = res['sr0_benchmark'] * np.sqrt(365)
    print(f"  n_trials={nt:5d}:  DSR={res['dsr']:.4f}   benchmark (annualized) Sharpe {sr0_ann:.2f}  "
          f"skew={res['skew']:+.2f} kurt={res['kurtosis']:.1f}")

# Include ALL days (with flat periods) vs only in-market days
in_market = daily[pos.sum(axis=1).reindex(daily.index) > 0]
print(f"\n  in-market days only: {len(in_market)}")
for nt in (85, 300):
    res = deflated_sharpe_ratio(in_market.tolist(), n_trials=nt)
    print(f"  n_trials={nt:5d}:  DSR={res['dsr']:.4f}")

# ---------------------------------------------------------------- context
print()
print("=" * 78)
print("3) CONTEXT — DSR of buy-and-hold BTC over the same window (n_trials=1)")
print("=" * 78)
bh = ret_mat['BTC'].dropna()
res = deflated_sharpe_ratio(bh.tolist(), n_trials=1)
print(f"  BTC HODL: DSR={res['dsr']:.4f}  (annualized Sharpe {bh.mean()/bh.std()*np.sqrt(365):.2f})")
