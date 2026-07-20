"""
Phase 18 diagnostic (descriptive only, zero n_trials): characterize the BTC-ETH
relative-pricing drift that failed pre-gate 1 of H-CointPair. No strategy returns
are computed anywhere in this file; it documents WHY the stationarity census failed.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')


def load_fut(sym):
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index()['close'].astype(float)


def rolling_hedge(ly, lx, win=365):
    """Same construction as phase18_cointpair.rolling_hedge (365d OLS, shift 1)."""
    mx, my = lx.rolling(win).mean(), ly.rolling(win).mean()
    cov = (lx * ly).rolling(win).mean() - mx * my
    var = (lx * lx).rolling(win).mean() - mx * mx
    return (my - (cov / var) * mx).shift(1), (cov / var).shift(1)


fut = pd.DataFrame({'BTC': load_fut('BTC'), 'ETH': load_fut('ETH')}).dropna()
lB, lE = np.log(fut['BTC']), np.log(fut['ETH'])
ratio = lE - lB

print('ETH/BTC log ratio — yearly drift (futures window):')
for y, g in ratio.groupby(ratio.index.year):
    print(f"  {y}: start {g.iloc[0]:+.3f}  end {g.iloc[-1]:+.3f}  "
          f"drift {g.iloc[-1]-g.iloc[0]:+.3f}  ({(np.exp(g.iloc[-1]-g.iloc[0])-1)*100:+.1f}% rel move)")
total = ratio.iloc[-1] - ratio.iloc[0]
print(f"  TOTAL {fut.index[0].date()} -> {fut.index[-1].date()}: drift {total:+.3f} "
      f"= ETH {'lost' if total < 0 else 'gained'} {(1-np.exp(total))*100:.0f}% vs BTC")

alpha, beta = rolling_hedge(lE, lB)
z_raw = (lE - alpha - beta * lB).dropna()
print('\nCausal (365d rolling-hedge) spread — yearly mean level:')
for y, g in z_raw.groupby(z_raw.index.year):
    print(f"  {y}: mean {g.mean():+.4f}  std {g.std():.4f}")

m24 = z_raw.index >= '2024-01-01'
p_pre = adfuller(z_raw[~m24].values, autolag='aic')[1]
p_post = adfuller(z_raw[m24].values, autolag='aic')[1]
print(f"\nADF on the causal spread: pre-2024 p = {p_pre:.4f}   post-2024 p = {p_post:.4f}")
