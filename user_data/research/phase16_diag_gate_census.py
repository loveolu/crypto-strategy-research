"""Descriptive diagnostics for the H-BearShort pre-gate-2 STOP (no backtest, zero trial cost).

Produces the comparison tables for SESSION_2026-07-10_BEARSHORT.md:
  [A] bull gate vs mirrored bear gate episode census (same window, same construction)
  [B] per-episode gross short return by episode-length bucket
  [C] P&L concentration (top episodes) and calendar distribution
"""
import numpy as np
import pandas as pd
from pathlib import Path

FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
SYMS2 = ['BTC', 'ETH']


def load_fut(sym):
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index()


def gate(df, bear: bool):
    c = df['close']
    sma, roc = c.rolling(200).mean(), c.pct_change(30)
    e20 = c.ewm(span=20, adjust=False).mean()
    e50 = c.ewm(span=50, adjust=False).mean()
    if bear:
        return ((c < sma) & (roc < 0) & (e20 < e50)).astype(float)
    return ((c > sma) & (roc > 0) & (e20 > e50)).astype(float)


def episodes(w):
    active = (w > 0).values
    eps, start = [], None
    for i, a in enumerate(active):
        if a and start is None:
            start = i
        elif not a and start is not None:
            eps.append((start, i - 1)); start = None
    if start is not None:
        eps.append((start, len(active) - 1))
    return eps


def census(bear: bool):
    rows = []
    for s in SYMS2:
        df = load_fut(s)
        c = df['close']
        g = gate(df, bear)
        for a, b in episodes(g):
            ei, xi = min(a + 1, len(c) - 1), min(b + 1, len(c) - 1)  # 1-bar exec lag refs
            r = (c.iloc[xi] / c.iloc[ei] - 1)
            if bear:
                r = -r  # short gross return
            rows.append({'sym': s, 'start': c.index[a], 'len': b - a + 1, 'gross': r})
    return pd.DataFrame(rows)


print('[A] Episode census: champion bull gate vs mirrored bear gate (BTC+ETH futures window)')
for label, bear in [('BULL (champion)', False), ('BEAR (mirror)', True)]:
    d = census(bear)
    lens = d['len'].values
    print(f"  {label:<16} n={len(d):3d}  median len {np.median(lens):4.0f}  "
          f"q25 {np.percentile(lens, 25):3.0f}  q75 {np.percentile(lens, 75):4.0f}  "
          f"max {lens.max():3d}  share<=3bars {100 * (lens <= 3).mean():3.0f}%  "
          f"gross: median {d['gross'].median() * 100:+5.1f}%  mean {d['gross'].mean() * 100:+5.1f}%  "
          f"pos {100 * (d['gross'] > 0).mean():3.0f}%")

print('\n[B] Mirrored bear gate: gross short return by episode-length bucket')
d = census(True)
for lo, hi, tag in [(1, 3, '1-3 bars'), (4, 10, '4-10 bars'), (11, 30, '11-30 bars'), (31, 999, '>30 bars')]:
    sub = d[(d['len'] >= lo) & (d['len'] <= hi)]
    if len(sub) == 0:
        continue
    print(f"  {tag:<10} n={len(sub):3d}  median {sub['gross'].median() * 100:+5.1f}%  "
          f"mean {sub['gross'].mean() * 100:+5.1f}%  pos {100 * (sub['gross'] > 0).mean():3.0f}%  "
          f"sum {sub['gross'].sum() * 100:+6.1f}%")

print('\n[C] Concentration and calendar distribution (mirrored gate)')
d_sorted = d.sort_values('gross', ascending=False)
total = d['gross'].sum()
top3 = d_sorted.head(3)
print(f"  total gross (sum of episode returns): {total * 100:+.1f}%")
print(f"  top-3 episodes sum: {top3['gross'].sum() * 100:+.1f}%  "
      f"({[f'{r.sym} {r.start.date()} len{r.len} {r.gross * 100:+.0f}%' for r in top3.itertuples()]})")
print(f"  sum EXCLUDING top-3: {(total - top3['gross'].sum()) * 100:+.1f}%")
d['year'] = d['start'].dt.year
print('  episodes per calendar year (count / median len / sum gross):')
for y, g in d.groupby('year'):
    print(f"    {y}: n={len(g):3d}  median len {g['len'].median():4.0f}  sum {g['gross'].sum() * 100:+6.1f}%")

print('\n[D] Fee floor context: 106 round trips x 0.30% fees/RT vs gross')
n_rt = len(d)
print(f"  round trips {n_rt}; fee drag ~{n_rt * 0.003 * 100 / 2:.1f}% per pair-notional unit "
      f"(0.15%/side); median episode gross {d['gross'].median() * 100:+.2f}% vs 0.30% RT cost")
