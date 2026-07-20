"""Diagnostic: mirrored-gate episode census on the extended BTC spot window (2018 bear incl.)."""
import numpy as np
import pandas as pd

df = pd.read_feather('user_data/data/okx/BTC_USDT-1d.feather').set_index('date').sort_index()
c = df['close']
g = ((c < c.rolling(200).mean()) & (c.pct_change(30) < 0)
     & (c.ewm(span=20, adjust=False).mean() < c.ewm(span=50, adjust=False).mean())).astype(float)
active = (g > 0).values
eps, start = [], None
for i, a in enumerate(active):
    if a and start is None:
        start = i
    elif not a and start is not None:
        eps.append((start, i - 1)); start = None
if start is not None:
    eps.append((start, len(active) - 1))
rows = []
for a, b in eps:
    ei, xi = min(a + 1, len(c) - 1), min(b + 1, len(c) - 1)
    rows.append({'start': c.index[a], 'len': b - a + 1, 'gross': -(c.iloc[xi] / c.iloc[ei] - 1)})
d = pd.DataFrame(rows)
lens = d['len'].values
print(f'BTC spot extended ({c.index[0].date()} -> {c.index[-1].date()}): n={len(d)} episodes')
print(f'  median len {np.median(lens):.0f}  q25 {np.percentile(lens, 25):.0f}  '
      f'q75 {np.percentile(lens, 75):.0f}  max {lens.max()}  share<=3 {100 * (lens <= 3).mean():.0f}%')
print(f'  gross short: median {d.gross.median() * 100:+.1f}%  mean {d.gross.mean() * 100:+.1f}%  '
      f'pos {100 * (d.gross > 0).mean():.0f}%  sum {d.gross.sum() * 100:+.1f}%')
d['year'] = d['start'].dt.year
for y, gg in d.groupby('year'):
    print(f'    {y}: n={len(gg):2d}  median len {gg["len"].median():4.0f}  sum gross {gg.gross.sum() * 100:+6.1f}%')
