"""
Phase 6: Cross-asset validation of the TrendVolTarget construct.

The strongest robustness test: apply the EXACT construct (no re-tuning)
to 7 assets it was never designed on. If the edge is real (trend regime
avoidance), it should show positive Sharpe on most of them. If it was
BTC/ETH-specific luck, it should fall apart.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from pathlib import Path

FEE = 0.0015  # 0.1% commission + 0.05% slippage per side
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')

def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()


def load_fut(sym):
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})


def tvt_returns(close, tv=0.40, fee=FEE):
    """TrendVolTarget single-asset return stream (exact champion spec)."""
    s1 = (close > _sma(close, 200)).astype(float)
    s2 = (close.pct_change(30) > 0).astype(float)
    s3 = (_ema(close, 20) > _ema(close, 50)).astype(float)
    core = ((s1 + s2 + s3) >= 3).astype(float)
    rv = close.pct_change().rolling(30).std() * np.sqrt(365)
    scale = (tv / rv).clip(0, 1)
    sig = ((core * scale) / 0.25).round() * 0.25
    sig = sig.clip(0, 1)
    pos = sig.shift(2).fillna(0)
    ret = pos * close.pct_change().fillna(0) - pos.diff().abs().fillna(pos.abs()) * fee
    return ret


def stats(ret, label):
    ret = ret.dropna()
    eq = (1 + ret).cumprod()
    yrs = len(ret) / 365
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1
    sh = ret.mean() / ret.std() * np.sqrt(365) if ret.std() > 0 else 0
    dd = (eq / eq.cummax() - 1).min()
    yearly = (1 + ret).groupby(ret.index.year).prod() - 1
    pos_y = (yearly > 0).sum()
    print(f"{label:10s} CAGR {cagr*100:+7.1f}%  Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  "
          f"posyrs {pos_y}/{len(yearly)}  " +
          " ".join(f"{y}:{v*100:+.0f}" for y, v in yearly.items()))
    return sh, dd, cagr


SYMS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'BNB']

print("=" * 110)
print("TrendVolTarget construct applied UNCHANGED to each asset (futures 1d data)")
print("=" * 110)
results = {}
rets = {}
for s in SYMS:
    df = load_fut(s)
    r = tvt_returns(df['close'])
    rets[s] = r
    results[s] = stats(r, s)

print()
print("Buy-and-hold reference per asset:")
for s in SYMS:
    df = load_fut(s)
    stats(df['close'].pct_change().fillna(0), f"{s}-HODL")

sharpes = [v[0] for v in results.values()]
print()
print(f"TVT construct: median Sharpe {np.median(sharpes):.2f}, "
      f"positive Sharpe on {sum(1 for x in sharpes if x > 0)}/{len(sharpes)} assets, "
      f"Sharpe > 0.5 on {sum(1 for x in sharpes if x > 0.5)}/{len(sharpes)}")

# Save return streams for phase 7 portfolio work
out = pd.DataFrame(rets)
out.to_parquet('C:/Users/Comec/Projects/freqtrade/user_data/research/tvt_streams.parquet')
print("\nSaved per-asset TVT return streams to tvt_streams.parquet")
