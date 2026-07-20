"""
Phase 19 diagnostic (reporting-only, zero n_trials): decompose WHERE the continuous
bound's degradation vs the step25 baseline concentrates. No new scheme is evaluated;
this only decomposes the two streams pre-gate A already produced (same convention as
phase15's post-hoc diagnostics of the GK TEST collapse). Helper functions duplicated
from phase19_sizingband.py verbatim so importing does not re-run the pipeline.
"""
from pathlib import Path

import numpy as np
import pandas as pd

FEE = 0.0015
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
VOL_TARGET, LOOKBACK, QUANT_BASE, ANN = 0.40, 30, 0.25, 365
SYMS = ['BTC', 'ETH']


def load_fut(sym):
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})


def core_series(df):
    c = df['close']
    return ((c > c.rolling(200).mean()) & (c.pct_change(30) > 0)
            & (c.ewm(span=20, adjust=False).mean() > c.ewm(span=50, adjust=False).mean())).astype(float)


def cont_scale(df):
    rv = df['close'].pct_change().rolling(LOOKBACK).std() * np.sqrt(ANN)
    return (VOL_TARGET / rv).clip(0, 1)


def weights_step(dfs, step):
    idx = sorted(set().union(*[dfs[s].index for s in SYMS]))
    W = pd.DataFrame(index=pd.DatetimeIndex(idx))
    for s in SYMS:
        raw = core_series(dfs[s]) * cont_scale(dfs[s])
        if step is not None:
            raw = ((raw / step).round() * step).clip(0, 1)
        W[s] = raw.reindex(W.index) / len(SYMS)
    return W.fillna(0)


def positions(W, closes):
    return W.reindex(closes.index).fillna(0).shift(2).fillna(0)


def turnover_series(pos):
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    return turn


def sharpe(ret):
    ret = ret.dropna()
    return float(ret.mean() / ret.std() * np.sqrt(ANN)) if ret.std() > 0 else 0.0


dfs = {s: load_fut(s) for s in SYMS}
closes = pd.DataFrame({s: dfs[s]['close'] for s in SYMS}).sort_index()

W_base = weights_step(dfs, QUANT_BASE)
W_cont = weights_step(dfs, None)
pos_base = positions(W_base, closes)
pos_cont = positions(W_cont, closes)
rets = closes.pct_change().fillna(0)
turn_base = turnover_series(pos_base)

ret_base = ((pos_base * rets).sum(axis=1) - turn_base * FEE).dropna()
ret_bound = ((pos_cont * rets).sum(axis=1) - turn_base * FEE).dropna()

n = len(ret_base)
te = slice(int(n * 0.85), n)

print('[a] Mean exposure (sum of position weights), full / TEST:')
print(f"  step25 full {pos_base.sum(axis=1).mean():.3f}  TEST {pos_base.iloc[te].sum(axis=1).mean():.3f}")
print(f"  cont   full {pos_cont.sum(axis=1).mean():.3f}  TEST {pos_cont.iloc[te].sum(axis=1).mean():.3f}")
print(f"  mean |pos_cont - pos_base| per day (sum assets): full "
      f"{(pos_cont - pos_base).abs().sum(axis=1).mean():.4f}  TEST "
      f"{(pos_cont - pos_base).iloc[te].abs().sum(axis=1).mean():.4f}")

print('\n[b] Quantization direction: how often does step25 hold MORE than the cont target?')
d = (pos_base - pos_cont).sum(axis=1)
print(f"  full: rounds up {(d > 1e-9).mean()*100:.1f}% of days, "
      f"down {(d < -1e-9).mean()*100:.1f}%, equal {(d.abs() <= 1e-9).mean()*100:.1f}%")
print(f"  mean signed (base - cont) exposure: full {d.mean():+.4f}  TEST {d.iloc[te].mean():+.4f}")
inmkt = pos_cont.sum(axis=1) > 0
print(f"  in-market days only: mean signed {d[inmkt].mean():+.4f}  "
      f"({(d[inmkt] > 1e-9).mean()*100:.1f}% up / {(d[inmkt] < -1e-9).mean()*100:.1f}% down)")

print('\n[c] Cumulative return difference (bound - baseline) by year:')
diff = ret_bound - ret_base
for yr in sorted(set(diff.index.year)):
    dy = diff[diff.index.year == yr]
    print(f"  {yr}: {dy.sum()*100:+6.2f}%  (worst month "
          f"{dy.groupby(dy.index.month).sum().min()*100:+.2f}%)")

print('\n[d] TEST-split months, difference (bound - baseline):')
dt = diff.iloc[te]
bym = dt.groupby([dt.index.year, dt.index.month]).sum().sort_values()
print('  worst 5:', [(f"{y}-{mth:02d}", f"{v*100:+.2f}%") for (y, mth), v in bym.head(5).items()])
print('  best 5: ', [(f"{y}-{mth:02d}", f"{v*100:+.2f}%") for (y, mth), v in bym.tail(5).items()])

print(f"\n[e] TEST Sharpe: baseline {sharpe(ret_base.iloc[te]):.3f}   bound {sharpe(ret_bound.iloc[te]):.3f}")
print(f"    TEST span: {ret_base.index[int(n*0.85)].date()} -> {ret_base.index[-1].date()}")
