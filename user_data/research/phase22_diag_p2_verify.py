"""
Director verification of the H-IVSizing P2 stop (cycle #15, 2026-07-12).

Independent code path — does NOT import or reuse phase22_ivsizing.py logic.
Rebuilds champion weights, the max(rv30, DVOL/100) variant, the affected-day
census, and the P2 harm comparison from scratch, with three robustness twists
the engineer's script did not have:

  V1. Recount P1: in-market days, affected days, distinct episodes.
  V2. P2 as run by the engineer (forward 10d champion net return from day t).
  V3. P2 lag-consistent: forward 10d from t+2 (when the weight change would
      actually take effect through the 2-bar lag).
  V4. P2 on raw asset forward returns (equal-weight BTC/ETH close-to-close),
      removing the strategy's own sizing from the measurement entirely.

The stop stands only if the affected-day distribution is NOT worse than
unconditional under the lag-consistent and raw-asset views as well.
"""
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
DVOL_FEATHER = Path('C:/Users/Comec/Projects/freqtrade/user_data/research/data/dvol/btc_dvol_daily.feather')
START, END = pd.Timestamp('2021-03-24', tz='UTC'), pd.Timestamp('2026-05-31', tz='UTC')
FEE, ANN, VT, LB, Q, FWD = 0.0015, 365, 0.40, 30, 0.25, 10
SYMS = ['BTC', 'ETH']

def load(sym):
    df = pd.read_feather(DATA_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    df = df.set_index('date').sort_index()
    df.index = pd.to_datetime(df.index, utc=True)
    return df['close'].astype(float)

closes = pd.concat({s: load(s) for s in SYMS}, axis=1).loc[START:END].dropna()

dv = pd.read_feather(DVOL_FEATHER)
dv.columns = [c.lower() for c in dv.columns]
dcol = next(c for c in dv.columns if 'date' in c or 'time' in c)
vcol = next(c for c in dv.columns if c != dcol)
dv[dcol] = pd.to_datetime(dv[dcol], utc=True)
dvol = dv.set_index(dcol)[vcol].sort_index().reindex(closes.index).ffill(limit=2)

def weights(use_iv):
    W = {}
    for s in SYMS:
        c = closes[s]
        core = ((c > c.rolling(200).mean())
                & (c.pct_change(30) > 0)
                & (c.ewm(span=20, adjust=False).mean() > c.ewm(span=50, adjust=False).mean()))
        rv = c.pct_change().rolling(LB).std() * np.sqrt(ANN)
        den = np.maximum(rv, dvol / 100.0) if use_iv else rv
        scale = (VT / den).clip(0, 1)
        raw = core.astype(float) * scale
        W[s] = ((raw.fillna(0) / Q).round() * Q).clip(0, 1) / len(SYMS)
    return pd.DataFrame(W)

Wc, Wv = weights(False), weights(True)

pos_c = Wc.shift(2).fillna(0)
ret_c = (pos_c * closes.pct_change().fillna(0)).sum(axis=1) - pos_c.diff().abs().sum(axis=1).fillna(0) * FEE

in_mkt = pos_c.sum(axis=1) > 0                      # lagged in-market (position on)
diff = (Wc - Wv).sum(axis=1) > 1e-10                # decision-date weight reduction
affected = diff & in_mkt

# episodes on decision-date diff
runs = (diff != diff.shift()).cumsum()[diff]
n_eps = runs.nunique()

print(f'V1 counts: in-market {int(in_mkt.sum())} | diff days {int(diff.sum())} '
      f'| affected (diff & in-mkt) {int(affected.sum())} | episodes {n_eps}')

def fwd_sum(series, dates, offset):
    out = []
    idx = series.index
    for dt in dates:
        i = idx.get_loc(dt) + offset
        out.append(series.iloc[i:i + FWD].sum())
    return np.array(out)

aff_dates = affected[affected].index
unc_dates = in_mkt[in_mkt].index

raw_ret = closes.pct_change().mean(axis=1).fillna(0)  # equal-weight asset return

any_worse = False
for label, series, off in [
        ('V2 engineer-style (champ net, from t)',  ret_c,   0),
        ('V3 lag-consistent  (champ net, from t+2)', ret_c,  2),
        ('V4 raw-asset       (EW BTC/ETH, from t+2)', raw_ret, 2)]:
    fa = fwd_sum(series, aff_dates, off)
    fu = fwd_sum(series, unc_dates, off)
    worse = (np.median(fa) < np.median(fu)) or (fa.mean() < fu.mean())
    any_worse |= worse
    print(f'{label}: affected med {np.median(fa)*100:+.2f}% mean {fa.mean()*100:+.2f}% | '
          f'uncond med {np.median(fu)*100:+.2f}% mean {fu.mean()*100:+.2f}% | '
          f'affected WORSE: {worse}')

print()
print('P2 stop OVERTURN CANDIDATE — at least one view shows harm; escalate.'
      if any_worse else
      'P2 stop VERIFIED — no view shows affected days as worse than unconditional.')
