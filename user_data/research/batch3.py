"""Batch 3: 4h BTC and stricter filters."""
import sys
import time
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
from validator import load, validate, print_verdict, save_verdict
import strategies as S
import numpy as np
import pandas as pd


def _ema(s, n): return s.ewm(span=n, adjust=False).mean()
def _sma(s, n): return s.rolling(n).mean()
def _rsi(s, n=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    dn = -d.clip(upper=0).ewm(alpha=1/n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100/(1+rs)
def _atr(df, n=14):
    h, l, c = df['high'], df['low'], df['close']
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()


# ---- 4h-specific strategies ----

def trend_filtered_breakout_4h(df, breakout_n=24, sma_n=200):
    """Long when close breaks 24-bar (4d) high AND above SMA200."""
    hi = df['high'].rolling(breakout_n).max().shift(1)
    sma = _sma(df['close'], sma_n)
    long = (df['close'] > hi) & (df['close'] > sma)
    exit_lo = df['low'].rolling(breakout_n//2).min().shift(1)
    exit_ = df['close'] < exit_lo
    sig = pd.Series(np.nan, index=df.index)
    sig[long] = 1.0
    sig[exit_] = 0.0
    return sig.ffill().fillna(0)


def trend_pullback_4h(df, ema_fast=20, ema_slow=100, rsi_dip=40, rsi_exit=70):
    """Pullback in uptrend: EMA fast > slow (uptrend), buy when RSI dips below 40, exit on RSI > 70 or EMA cross down."""
    ef = _ema(df['close'], ema_fast)
    es = _ema(df['close'], ema_slow)
    trend_up = ef > es
    r = _rsi(df['close'], 14)
    entry = trend_up & (r < rsi_dip) & (df['close'] > es)
    exit_ = (r > rsi_exit) | (~trend_up)
    sig = pd.Series(np.nan, index=df.index)
    sig[entry] = 1.0
    sig[exit_] = 0.0
    return sig.ffill().fillna(0)


def adx_4h(df, adx_min=22, ema_n=50):
    """Trend strength gate."""
    h, l, c = df['high'], df['low'], df['close']
    up = h.diff(); dn = -l.diff()
    plus_dm = ((up > dn) & (up > 0)) * up
    minus_dm = ((dn > up) & (dn > 0)) * dn
    atr = _atr(df, 14)
    pdi = 100*plus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
    mdi = 100*minus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
    dx = 100*(pdi-mdi).abs() / (pdi+mdi).replace(0,np.nan)
    adx = dx.ewm(alpha=1/14, adjust=False).mean()
    ema = _ema(c, ema_n)
    return ((adx > adx_min) & (c > ema)).astype(float)


def supertrend_4h(df, atr_n=10, mult=3.0):
    """Simplified supertrend: trail by ATR multiple."""
    h, l, c = df['high'], df['low'], df['close']
    atr = _atr(df, atr_n)
    hl2 = (h+l)/2
    upper = hl2 + mult*atr
    lower = hl2 - mult*atr
    direction = pd.Series(1.0, index=df.index)
    final_upper = upper.copy()
    final_lower = lower.copy()
    for i in range(1, len(c)):
        final_upper.iloc[i] = min(upper.iloc[i], final_upper.iloc[i-1]) if c.iloc[i-1] <= final_upper.iloc[i-1] else upper.iloc[i]
        final_lower.iloc[i] = max(lower.iloc[i], final_lower.iloc[i-1]) if c.iloc[i-1] >= final_lower.iloc[i-1] else lower.iloc[i]
        if direction.iloc[i-1] > 0:
            direction.iloc[i] = -1.0 if c.iloc[i] < final_lower.iloc[i] else 1.0
        else:
            direction.iloc[i] = 1.0 if c.iloc[i] > final_upper.iloc[i] else -1.0
    return (direction > 0).astype(float)


def bbands_squeeze_breakout_4h(df, n=20, k=2.0, squeeze_lookback=120, squeeze_quantile=0.25):
    """Long when BB width is in bottom quartile of last 120 bars THEN price breaks upper band."""
    m = _sma(df['close'], n)
    sd = df['close'].rolling(n).std()
    upper = m + k*sd
    lower = m - k*sd
    width = (upper - lower) / m
    width_q = width.rolling(squeeze_lookback).quantile(squeeze_quantile)
    squeeze = width < width_q
    breakout_up = (df['close'] > upper) & squeeze.shift(1)
    exit_ = df['close'] < m
    sig = pd.Series(np.nan, index=df.index)
    sig[breakout_up] = 1.0
    sig[exit_] = 0.0
    return sig.ffill().fillna(0)


def vol_regime_btc_1d(df, lookback=30, vol_quantile=0.30):
    """Long when realized vol is BELOW historical median (low-vol regime) AND price above SMA50."""
    ret = df['close'].pct_change()
    rv = ret.rolling(lookback).std() * np.sqrt(365)
    rv_q = rv.rolling(365*2).quantile(vol_quantile)
    low_vol = rv < rv_q
    sma50 = _sma(df['close'], 50)
    return ((df['close'] > sma50) & low_vol).astype(float)


def ema_crossover_with_atr_stop_4h(df, fast=20, slow=50, atr_mult=2.5):
    """Cross above slow EMA = enter; trail by ATR(14) * mult."""
    ef = _ema(df['close'], fast)
    es = _ema(df['close'], slow)
    atr = _atr(df, 14)
    c = df['close']

    pos = np.zeros(len(c))
    trail = -np.inf
    in_pos = False
    for i in range(len(c)):
        if pd.isna(ef.iloc[i]) or pd.isna(es.iloc[i]) or pd.isna(atr.iloc[i]):
            continue
        if not in_pos:
            if ef.iloc[i] > es.iloc[i] and ef.iloc[i-1] <= es.iloc[i-1]:
                in_pos = True
                trail = c.iloc[i] - atr_mult*atr.iloc[i]
        else:
            new_trail = c.iloc[i] - atr_mult*atr.iloc[i]
            if new_trail > trail: trail = new_trail
            if c.iloc[i] < trail or ef.iloc[i] < es.iloc[i]:
                in_pos = False
                trail = -np.inf
        pos[i] = 1.0 if in_pos else 0.0
    return pd.Series(pos, index=df.index)


def hist_vol_breakout_4h(df, atr_n=14, atr_mult=2.5):
    """Buy when close > yesterday's close + ATR*mult; exit at SMA(20)."""
    atr = _atr(df, atr_n)
    trigger = df['close'].shift(1) + atr_mult*atr.shift(1)
    sma20 = _sma(df['close'], 20)
    entry = df['close'] > trigger
    exit_ = df['close'] < sma20
    sig = pd.Series(np.nan, index=df.index)
    sig[entry] = 1.0
    sig[exit_] = 0.0
    return sig.ffill().fillna(0)


def hmm_like_two_state_btc(df, vol_n=60, mom_n=30):
    """Two-state filter: 'bull' = mom>0 AND vol normal; 'bear/chop' = flat."""
    ret = df['close'].pct_change()
    rv = ret.rolling(vol_n).std() * np.sqrt(365)
    rv_low = rv.rolling(365).quantile(0.30)
    rv_high = rv.rolling(365).quantile(0.80)
    mom = df['close'].pct_change(mom_n)
    sma100 = _sma(df['close'], 100)
    bull = (mom > 0) & (df['close'] > sma100) & (rv < rv_high)
    return bull.astype(float)


def double_ma_w_pullback_btc1d(df, sma_fast=50, sma_slow=200, pullback_pct=0.05, exit_sma=20):
    """Trend regime up + buy when close pulls back 5% below recent peak, exit when reaches SMA20."""
    sf = _sma(df['close'], sma_fast)
    ss = _sma(df['close'], sma_slow)
    trend = sf > ss
    peak = df['close'].rolling(20).max()
    pullback = df['close'] < peak * (1 - pullback_pct)
    sma_exit = _sma(df['close'], exit_sma)
    entry = trend & pullback
    exit_ = df['close'] > sma_exit * 1.02
    sig = pd.Series(np.nan, index=df.index)
    sig[entry] = 1.0
    sig[exit_] = 0.0
    return sig.ffill().fillna(0)


# Build test list
df_btc1d = load('BTC/USDT', '1d')
df_btc4h = load('BTC/USDT', '4h')
df_btc1h = load('BTC/USDT', '1h')

TESTS = [
    ("trend_filt_breakout_btc4h", df_btc4h, lambda d: trend_filtered_breakout_4h(d, 24, 200), 365*6),
    ("trend_filt_breakout_btc4h_48", df_btc4h, lambda d: trend_filtered_breakout_4h(d, 48, 200), 365*6),
    ("trend_pullback_btc4h", df_btc4h, lambda d: trend_pullback_4h(d, 20, 100, 40, 70), 365*6),
    ("adx_btc4h_22_50", df_btc4h, lambda d: adx_4h(d, 22, 50), 365*6),
    ("adx_btc4h_30_50", df_btc4h, lambda d: adx_4h(d, 30, 50), 365*6),
    ("supertrend_btc4h_10_3", df_btc4h, lambda d: supertrend_4h(d, 10, 3.0), 365*6),
    ("bbands_squeeze_btc4h", df_btc4h, lambda d: bbands_squeeze_breakout_4h(d, 20, 2.0, 120, 0.25), 365*6),
    ("vol_regime_btc1d", df_btc1d, lambda d: vol_regime_btc_1d(d, 30, 0.30), 365),
    ("ema_xover_atr_btc4h", df_btc4h, lambda d: ema_crossover_with_atr_stop_4h(d, 20, 50, 2.5), 365*6),
    ("hist_vol_breakout_btc4h", df_btc4h, lambda d: hist_vol_breakout_4h(d, 14, 2.5), 365*6),
    ("hmm_two_state_btc1d", df_btc1d, lambda d: hmm_like_two_state_btc(d, 60, 30), 365),
    ("double_ma_pullback_btc1d", df_btc1d, lambda d: double_ma_w_pullback_btc1d(d, 50, 200, 0.05, 20), 365),
]

passed = []
for name, df, fn, bpy in TESTS:
    t0 = time.time()
    try:
        v = validate(name, df, fn, bars_per_year=bpy)
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
        import traceback; traceback.print_exc()
        continue
    save_verdict(v)
    print_verdict(v)
    print(f"  (took {time.time()-t0:.1f}s)")
    if v.passed:
        passed.append(name)

print("\n" + "="*70)
print(f"BATCH 3: {len(passed)}/{len(TESTS)} passed")
print("="*70)
for p in passed: print(f"  PASS: {p}")
