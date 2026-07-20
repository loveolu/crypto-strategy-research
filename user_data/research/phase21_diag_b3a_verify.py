"""
Director diagnostic (cycle #15): independently verify the B3a episode census
in phase21_ivgate.py.

Checks:
 1. Rebuild z_iv from the cached DVOL feather with an INDEPENDENT (vectorized)
    episode finder and compare episode count/boundaries with the engineer's loop.
 2. Audit the in-market mask alignment: a tz/calendar mismatch in the reindex
    would fillna(False) true in-market days -> false B3a stop (cycle-#13 class).
 3. Print every episode with onset, length, peak z_iv, lagged champion weights
    at onset, and the in-market verdict, so the 4-of-9 split is auditable.
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
DVOL_FEATHER = Path(__file__).parent / 'data' / 'dvol' / 'btc_dvol_daily.feather'
OVERLAP_START = pd.Timestamp('2021-03-24', tz='UTC')
OVERLAP_END = pd.Timestamp('2026-05-31', tz='UTC')
Z_WINDOW, Z_THRESH = 365, 2.0
LOOKBACK_VOL, VOL_TARGET, QUANT, ANN = 30, 0.40, 0.25, 365
CHAMP_SYMS = ['BTC', 'ETH']

def load_fut(sym):
    df = pd.read_feather(DATA_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    df = df.set_index('date').sort_index()
    df.index = pd.to_datetime(df.index, utc=True)
    return df

def core(close):
    sma200 = close.rolling(200).mean()
    e20 = close.ewm(span=20, adjust=False).mean()
    e50 = close.ewm(span=50, adjust=False).mean()
    return ((close > sma200) & (close.pct_change(30) > 0) & (e20 > e50)).astype(float)

def weights(closes):
    W = pd.DataFrame(index=closes.index)
    for s in CHAMP_SYMS:
        rv = closes[s].pct_change().rolling(LOOKBACK_VOL).std() * np.sqrt(ANN)
        raw = core(closes[s]) * (VOL_TARGET / rv).clip(0, 1)
        W[s] = ((raw.fillna(0) / QUANT).round() * QUANT).clip(0, 1) / len(CHAMP_SYMS)
    return W

def rolling_z(s, window=Z_WINDOW):
    mu = s.rolling(window, min_periods=window // 2).mean()
    sd = s.rolling(window, min_periods=window // 2).std()
    return (s - mu) / sd.replace(0, np.nan)

closes = pd.DataFrame({s: load_fut(s)['close'] for s in CHAMP_SYMS})
closes = closes.loc[(closes.index >= OVERLAP_START) & (closes.index <= OVERLAP_END)].dropna()
W = weights(closes)

dvol = pd.read_feather(DVOL_FEATHER)
dcol = [c for c in dvol.columns if 'date' in c.lower() or 'time' in c.lower()][0]
vcol = [c for c in dvol.columns if c != dcol][0]
dvol[dcol] = pd.to_datetime(dvol[dcol], utc=True)
iv = dvol.set_index(dcol)[vcol].sort_index()

dvol_aligned = iv.reindex(closes.index).ffill(limit=2)
z_iv = rolling_z(dvol_aligned)
rv30 = closes['BTC'].pct_change().rolling(LOOKBACK_VOL).std() * np.sqrt(ANN)
z_rv = rolling_z(rv30)
valid = z_iv.notna() & z_rv.notna()
z_iv_v = z_iv[valid]
print(f'Valid z obs: {valid.sum()} ({z_iv_v.index[0].date()} -> {z_iv_v.index[-1].date()})  '
      f'[engineer: 1,680]')
print(f'Level corr z_iv/z_rv: {z_iv_v.corr(z_rv[valid]):+.4f}  [engineer: +0.6870]')

# Independent vectorized episode finder
flag = (z_iv_v > Z_THRESH).astype(int)
d = flag.diff().fillna(flag.iloc[0])
starts = list(z_iv_v.index[d == 1])
ends = list(z_iv_v.index[flag.diff(-1).fillna(flag.iloc[-1]) == 1])
episodes = list(zip(starts, ends))
print(f'\nIndependent episode count: {len(episodes)}  [engineer: 9]')

# In-market mask + alignment audit
in_mkt_raw = (W.shift(2).fillna(0).abs().sum(axis=1) > 0)
in_mkt_re = in_mkt_raw.reindex(z_iv_v.index)
n_nan = int(in_mkt_re.isna().sum())
print(f'Alignment audit: {n_nan} of {len(in_mkt_re)} z_iv days missing from champion calendar '
      f'(fillna(False) risk)')
in_mkt = in_mkt_re.fillna(False).astype(bool)
print(f'Champion in-market fraction on z_iv calendar: {in_mkt.mean():.1%}')

print(f'\n{"onset":<12} {"end":<12} {"len":>4} {"peak z":>7} {"BTC_w":>6} {"ETH_w":>6}  in-market?')
n_in = 0
Wl = W.shift(2).fillna(0)
for s, e in episodes:
    seg = z_iv_v.loc[s:e]
    bw, ew = float(Wl.loc[s, 'BTC']), float(Wl.loc[s, 'ETH'])
    inm = bool(in_mkt.loc[s])
    n_in += inm
    print(f'{str(s.date()):<12} {str(e.date()):<12} {len(seg):>4} {seg.max():>7.2f} '
          f'{bw:>6.2f} {ew:>6.2f}  {"YES" if inm else "no"}')

print(f'\nIn-market spike-onset episodes: {n_in}  [engineer: 4; stop rule < 6]')
print('VERDICT:', 'B3a FAIL confirmed' if n_in < 6 else 'B3a stop NOT confirmed — DISCREPANCY')
