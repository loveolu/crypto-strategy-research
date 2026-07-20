"""
Phase 21 DIAGNOSTIC (Director cycle #13): corrected lead/lag check for H-IVGate.

The original phase21_ivgate.py Step B2 had a sign bug in the lag>0 branch:

    if lag < 0:
        c = d5_ziv.shift(-lag).corr(d5_zrv)          # corr(z_iv[t-k], z_rv[t]) — IV leads  (correct)
    elif lag > 0:
        c = d5_ziv.corr(d5_zrv.shift(-lag))          # corr(z_iv[t], z_rv[t+k]) — ALSO IV leads (bug)

corr(z_iv[t], z_rv[t+k]) == corr(z_iv[t-k], z_rv[t]) — both branches computed the
IV-LEADING cross-correlation, so the table was symmetric by construction and
avg_lead == avg_lag was a tautology, not a finding. The IV-LAGGING side was
never measured. This script recomputes the full cross-correlation with a single
consistent formula:

    xcorr[lag] = corr(d5_ziv.shift(-lag), d5_zrv)
      lag = -k → shift(+k): z_iv from k days ago vs z_rv today  → IV leads
      lag = +k → shift(-k): z_iv k days ahead vs z_rv today     → IV lags (rv leads)

Everything else (data, z construction, Δ5d, stop rule) is identical to the
locked spec in SESSION_2026-07-11_IVGATE.md §1.2. Census only — no strategy
construction, zero n_trials.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── locked constants (identical to phase21_ivgate.py) ──────────────────────
ANN          = 365
Z_WINDOW     = 365
LOOKBACK_VOL = 30

DATA_DIR     = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
DVOL_FEATHER = Path('C:/Users/Comec/Projects/freqtrade/user_data/research/data/dvol/btc_dvol_daily.feather')

CHAMP_START = pd.Timestamp('2020-01-01', tz='UTC')
CHAMP_END   = pd.Timestamp('2026-05-31', tz='UTC')

def load_fut(sym: str) -> pd.DataFrame:
    df = pd.read_feather(DATA_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    df = df.set_index('date').sort_index()
    df.index = pd.to_datetime(df.index, utc=True)
    return df.astype({c: float for c in ['open', 'high', 'low', 'close', 'volume']})

def rolling_z(s: pd.Series, window: int = Z_WINDOW) -> pd.Series:
    mu = s.rolling(window, min_periods=window // 2).mean()
    sd = s.rolling(window, min_periods=window // 2).std()
    return (s - mu) / sd.replace(0, np.nan)

# ── rebuild the exact series from phase21 ───────────────────────────────────
btc_dvol = pd.read_feather(DVOL_FEATHER)
btc_dvol = btc_dvol.set_index('date')['dvol'] if 'date' in btc_dvol.columns else btc_dvol.set_index(btc_dvol.columns[0]).iloc[:, 0]
btc_dvol.index = pd.to_datetime(btc_dvol.index, utc=True)
btc_dvol = btc_dvol.sort_index()

OVERLAP_START = max(CHAMP_START, btc_dvol.index[0])
OVERLAP_END   = min(CHAMP_END, btc_dvol.index[-1])

closes = pd.DataFrame()
for s in ['BTC', 'ETH']:
    df_s = load_fut(s)
    df_s = df_s.loc[(df_s.index >= OVERLAP_START) & (df_s.index <= OVERLAP_END)]
    closes[s] = df_s['close']
closes = closes.dropna()

dvol_aligned = btc_dvol.reindex(closes.index).ffill(limit=2)
z_iv = rolling_z(dvol_aligned)
rv30 = closes['BTC'].pct_change().rolling(LOOKBACK_VOL).std() * np.sqrt(ANN)
z_rv = rolling_z(rv30)

valid  = z_iv.notna() & z_rv.notna()
z_iv_v = z_iv[valid]
z_rv_v = z_rv[valid]

d5_ziv = z_iv_v.diff(5)
d5_zrv = z_rv_v.diff(5)

print(f'Overlap window : {closes.index[0].date()} -> {closes.index[-1].date()}  ({len(closes):,} days)')
print(f'Valid z obs    : {int(valid.sum()):,}')
print(f'corr(z levels) : {z_iv_v.corr(z_rv_v):+.4f}   (engineer reported +0.6870)')
print(f'corr(d5, lag 0): {d5_ziv.corr(d5_zrv):+.4f}   (engineer reported +0.2883)')
print()

# ── corrected cross-correlation ─────────────────────────────────────────────
print('Corrected cross-correlation, xcorr[lag] = corr(d5_ziv.shift(-lag), d5_zrv):')
xcorr = {}
for lag in range(-10, 11):
    xcorr[lag] = float(d5_ziv.shift(-lag).corr(d5_zrv))
    tag = 'IV leads' if lag < 0 else ('contemporaneous' if lag == 0 else 'IV lags')
    print(f'  lag {lag:+3d}: {xcorr[lag]:+.4f}   {tag}')

avg_lead = float(np.mean([xcorr[l] for l in range(-5, 0)]))
avg_lag  = float(np.mean([xcorr[l] for l in range(1, 6)]))
print()
print(f'avg corr, IV-leading lags (-5..-1): {avg_lead:+.4f}')
print(f'avg corr, IV-lagging lags (+1..+5): {avg_lag:+.4f}')
print()
if avg_lead > avg_lag:
    print('CORRECTED PRE-GATE B STEP 2: PASS — IV changes lead rv30 changes.')
else:
    print('CORRECTED PRE-GATE B STEP 2: FAIL — IV is reactive; closure stands on corrected numbers.')
