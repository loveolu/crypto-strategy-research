"""Batch 4: ensembles and long-short market-neutral."""
import sys
import time
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from validator import (load, signal_to_returns, extract_trades, metrics,
                       yearly_breakdown, yearly_pnl_dollar_concentration,
                       split_70_15_15, monte_carlo, Verdict, save_verdict, print_verdict,
                       ANNUALIZATION_DAILY, COMMISSION, SLIPPAGE, validate)
import strategies as S
import multi_asset as MA


def _ema(s, n): return s.ewm(span=n, adjust=False).mean()
def _sma(s, n): return s.rolling(n).mean()


# ---- Ensemble strategies ----

def ensemble_trend_mom_revert(df):
    """Equal-weight vote across 3 strategies: ADX trend + ROC momentum + RSI revert (filtered)."""
    # signal 1: ADX > 25 AND ema20 > ema50
    h, l, c = df['high'], df['low'], df['close']
    up = h.diff(); dn = -l.diff()
    plus_dm = ((up > dn) & (up > 0)) * up
    minus_dm = ((dn > up) & (dn > 0)) * dn
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/14, adjust=False).mean()
    pdi = 100*plus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
    mdi = 100*minus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
    dx = 100*(pdi-mdi).abs() / (pdi+mdi).replace(0,np.nan)
    adx = dx.ewm(alpha=1/14, adjust=False).mean()
    s1 = ((adx > 25) & (_ema(c, 20) > _ema(c, 50))).astype(float)
    # signal 2: ROC30 > 0
    s2 = (c.pct_change(30) > 0).astype(float)
    # signal 3: regime up + RSI not overbought
    d = c.diff()
    up_r = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    dn_r = -d.clip(upper=0).ewm(alpha=1/14, adjust=False).mean()
    rsi = 100 - 100/(1 + up_r/dn_r.replace(0,np.nan))
    s3 = ((c > _sma(c, 200)) & (rsi < 70)).astype(float)

    avg = (s1 + s2 + s3) / 3
    return (avg > 0.5).astype(float)


def ensemble_voted(df):
    """Long only when 3-of-3 agree. Stricter — high signal quality."""
    h, l, c = df['high'], df['low'], df['close']
    s1 = (c > _sma(c, 200)).astype(float)
    s2 = (c.pct_change(30) > 0).astype(float)
    s3 = (_ema(c, 20) > _ema(c, 50)).astype(float)
    return ((s1 + s2 + s3) >= 3).astype(float)


def ensemble_2of3(df):
    """Long when 2-of-3 agree."""
    h, l, c = df['high'], df['low'], df['close']
    s1 = (c > _sma(c, 200)).astype(float)
    s2 = (c.pct_change(30) > 0).astype(float)
    s3 = (_ema(c, 20) > _ema(c, 50)).astype(float)
    return ((s1 + s2 + s3) >= 2).astype(float)


def hmm_plus_pullback(df):
    """Best 1d strategy (hmm) + only buy on RSI < 55 dip → reduces drawdown by avoiding chasing tops."""
    ret = df['close'].pct_change()
    rv = ret.rolling(60).std() * np.sqrt(365)
    rv_high = rv.rolling(365).quantile(0.80)
    mom = df['close'].pct_change(30)
    sma100 = _sma(df['close'], 100)
    d = df['close'].diff()
    up_r = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    dn_r = -d.clip(upper=0).ewm(alpha=1/14, adjust=False).mean()
    rsi = 100 - 100/(1 + up_r/dn_r.replace(0,np.nan))
    bull = (mom > 0) & (df['close'] > sma100) & (rv < rv_high) & (rsi < 60)
    return bull.astype(float)


# ---- Long-short market-neutral BTC-ETH ----

def long_short_btc_eth_pair(data, n=30, z_in=1.5, z_out=0.3):
    """True long-short: long one, SHORT the other. Net beta ~ 0."""
    a, b = list(data.keys())
    idx = sorted(set(data[a].index) & set(data[b].index))
    pa = data[a]["close"].reindex(idx).ffill()
    pb = data[b]["close"].reindex(idx).ffill()
    spread = np.log(pa / pb)
    mu = spread.rolling(n).mean()
    sd = spread.rolling(n).std()
    z = (spread - mu) / sd

    sig_a = pd.Series(np.nan, index=idx)
    sig_b = pd.Series(np.nan, index=idx)
    # spread high (a expensive vs b): short a, long b
    sig_a[z > z_in] = -1.0
    sig_b[z > z_in] = 1.0
    # spread low (a cheap vs b): long a, short b
    sig_a[z < -z_in] = 1.0
    sig_b[z < -z_in] = -1.0
    # exit
    sig_a[z.abs() < z_out] = 0.0
    sig_b[z.abs() < z_out] = 0.0
    return {
        a: sig_a.ffill().fillna(0).reindex(data[a].index).fillna(0),
        b: sig_b.ffill().fillna(0).reindex(data[b].index).fillna(0),
    }


def cross_sectional_long_short(data, lookback=30):
    """Long the winner, short the loser (each momentum)."""
    syms = list(data.keys())
    mom = {s: data[s]["close"].pct_change(lookback) for s in syms}
    idx = sorted(set().union(*[m.index for m in mom.values()]))
    mom_df = pd.DataFrame({s: mom[s].reindex(idx) for s in syms}).ffill()
    out = {s: pd.Series(0.0, index=idx) for s in syms}
    for i in range(len(idx)):
        row = mom_df.iloc[i]
        if row.isna().any():
            continue
        top = row.idxmax()
        bot = row.idxmin()
        if top != bot:
            out[top].iloc[i] = 1.0
            out[bot].iloc[i] = -1.0
    return {s: out[s].reindex(data[s].index).fillna(0) for s in syms}


df_btc1d = load('BTC/USDT', '1d')
df_btc4h = load('BTC/USDT', '4h')
df_eth1d = load('ETH/USDT', '1d')

# Align for multi-asset
common_start = max(df_btc1d.index.min(), df_eth1d.index.min())
data_be = {"BTC": df_btc1d.loc[common_start:], "ETH": df_eth1d.loc[common_start:]}


single_tests = [
    ("ensemble_trend_mom_revert_btc1d", df_btc1d, ensemble_trend_mom_revert, 365),
    ("ensemble_voted_3of3_btc1d", df_btc1d, ensemble_voted, 365),
    ("ensemble_2of3_btc1d", df_btc1d, ensemble_2of3, 365),
    ("hmm_plus_pullback_btc1d", df_btc1d, hmm_plus_pullback, 365),
    ("ensemble_trend_mom_revert_btc4h", df_btc4h, ensemble_trend_mom_revert, 365*6),
    ("ensemble_2of3_btc4h", df_btc4h, ensemble_2of3, 365*6),
]

multi_tests = [
    ("long_short_btc_eth_30_1.5", lambda d: long_short_btc_eth_pair(d, 30, 1.5, 0.3)),
    ("long_short_btc_eth_60_2.0", lambda d: long_short_btc_eth_pair(d, 60, 2.0, 0.5)),
    ("xsect_long_short_30d_btc_eth", lambda d: cross_sectional_long_short(d, 30)),
    ("xsect_long_short_60d_btc_eth", lambda d: cross_sectional_long_short(d, 60)),
]

passed = []
for name, df, fn, bpy in single_tests:
    t0 = time.time()
    try:
        v = validate(name, df, fn, bars_per_year=bpy)
    except Exception as e:
        print(f"[{name}] ERROR: {e}"); import traceback; traceback.print_exc(); continue
    save_verdict(v); print_verdict(v)
    print(f"  (took {time.time()-t0:.1f}s)")
    if v.passed: passed.append(name)

for name, fn in multi_tests:
    t0 = time.time()
    try:
        v = MA.validate_multi(name, data_be, fn, bars_per_year=ANNUALIZATION_DAILY)
    except Exception as e:
        print(f"[{name}] ERROR: {e}"); import traceback; traceback.print_exc(); continue
    save_verdict(v); print_verdict(v)
    print(f"  (took {time.time()-t0:.1f}s)")
    if v.passed: passed.append(name)

print("\n" + "="*70)
print(f"BATCH 4: {len(passed)}/{len(single_tests)+len(multi_tests)} passed")
print("="*70)
for p in passed: print(f"  PASS: {p}")
