"""Batch 5: classical oscillators, weekly timeframe, regime hybrids."""
import sys
import time
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from validator import (load, validate, save_verdict, print_verdict, ANNUALIZATION_DAILY)

def _ema(s, n): return s.ewm(span=n, adjust=False).mean()
def _sma(s, n): return s.rolling(n).mean()
def _atr(df, n=14):
    h, l, c = df['high'], df['low'], df['close']
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()


def cci_trend(df, n=20, threshold=100):
    """Commodity Channel Index: long when CCI crosses above +threshold."""
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma = tp.rolling(n).mean()
    md = (tp - sma).abs().rolling(n).mean()
    cci = (tp - sma) / (0.015 * md)
    long = (cci > threshold)
    exit_ = (cci < 0)
    sig = pd.Series(np.nan, index=df.index)
    sig[long] = 1.0
    sig[exit_] = 0.0
    return sig.ffill().fillna(0)


def tsi_momentum(df, n_slow=25, n_fast=13, sig_n=7):
    """True Strength Index: double-smoothed momentum."""
    m = df['close'].diff()
    abs_m = m.abs()
    s1 = _ema(_ema(m, n_slow), n_fast)
    s2 = _ema(_ema(abs_m, n_slow), n_fast)
    tsi = 100 * s1 / s2.replace(0, np.nan)
    tsi_sig = _ema(tsi, sig_n)
    sma200 = _sma(df['close'], 200)
    long = (tsi > tsi_sig) & (df['close'] > sma200) & (tsi > 0)
    return long.astype(float)


def coppock_curve(df, roc_long=294, roc_short=231, wma_n=70):
    """Coppock: WMA of ROC(11mo) + ROC(14mo). Daily approx: 294/231/70."""
    c = df['close']
    roc1 = c.pct_change(roc_long) * 100
    roc2 = c.pct_change(roc_short) * 100
    coppock = (roc1 + roc2).rolling(wma_n).mean()
    sma200 = _sma(c, 200)
    long = (coppock > 0) & (c > sma200)
    return long.astype(float)


def williams_r_trend(df, n=14, thresh=-50):
    """Williams %R: long when %R > -50 AND price > EMA50."""
    high_n = df['high'].rolling(n).max()
    low_n = df['low'].rolling(n).min()
    wr = -100 * (high_n - df['close']) / (high_n - low_n)
    ema50 = _ema(df['close'], 50)
    return ((wr > thresh) & (df['close'] > ema50)).astype(float)


def kama_trend(df, n=10, fast=2, slow=30):
    """Kaufman Adaptive Moving Average crossover."""
    c = df['close']
    change = (c - c.shift(n)).abs()
    vol = c.diff().abs().rolling(n).sum()
    er = change / vol.replace(0, np.nan)
    sc = (er * (2/(fast+1) - 2/(slow+1)) + 2/(slow+1)) ** 2
    kama = c.copy()
    for i in range(1, len(c)):
        if pd.notna(sc.iloc[i]) and pd.notna(kama.iloc[i-1]):
            kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (c.iloc[i] - kama.iloc[i-1])
        else:
            kama.iloc[i] = c.iloc[i]
    long = c > kama
    return long.astype(float)


def chandelier_exit(df, n=22, atr_mult=3.0):
    """Long when close > 22-day EMA. Exit on chandelier stop: highest_high(n) - atr_mult*ATR."""
    ema22 = _ema(df['close'], n)
    atr = _atr(df, 22)
    chand_long = df['high'].rolling(n).max() - atr_mult * atr
    c = df['close']
    pos = np.zeros(len(c))
    in_pos = False
    trail = -np.inf
    for i in range(len(c)):
        if pd.isna(ema22.iloc[i]) or pd.isna(chand_long.iloc[i]):
            continue
        if not in_pos:
            if c.iloc[i] > ema22.iloc[i]:
                in_pos = True
                trail = chand_long.iloc[i]
        else:
            new_trail = chand_long.iloc[i]
            if new_trail > trail: trail = new_trail
            if c.iloc[i] < trail:
                in_pos = False
                trail = -np.inf
        pos[i] = 1.0 if in_pos else 0.0
    return pd.Series(pos, index=df.index)


def hmm_strict(df):
    """hmm_two_state with additional ATR-based stop (try to reduce DD from -35% toward -25%)."""
    ret = df['close'].pct_change()
    rv = ret.rolling(60).std() * np.sqrt(365)
    rv_high = rv.rolling(365).quantile(0.80)
    mom = df['close'].pct_change(30)
    sma100 = _sma(df['close'], 100)
    # add: ALSO require ADX > 20 for entry
    h, l, c = df['high'], df['low'], df['close']
    up = h.diff(); dn = -l.diff()
    plus_dm = ((up > dn) & (up > 0)) * up
    minus_dm = ((dn > up) & (dn > 0)) * dn
    atr = _atr(df, 14)
    pdi = 100*plus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
    mdi = 100*minus_dm.ewm(alpha=1/14, adjust=False).mean() / atr
    dx = 100*(pdi-mdi).abs() / (pdi+mdi).replace(0, np.nan)
    adx = dx.ewm(alpha=1/14, adjust=False).mean()

    base = (mom > 0) & (c > sma100) & (rv < rv_high)
    # exit if ADX falls or close < SMA50
    sma50 = _sma(c, 50)
    sig = pd.Series(np.nan, index=df.index)
    sig[base & (adx > 20)] = 1.0
    sig[(c < sma50) | (~base)] = 0.0
    return sig.ffill().fillna(0)


def hmm_with_chandelier(df):
    """Combine hmm entry with chandelier exit for tighter trailing stop."""
    ret = df['close'].pct_change()
    rv = ret.rolling(60).std() * np.sqrt(365)
    rv_high = rv.rolling(365).quantile(0.80)
    mom = df['close'].pct_change(30)
    sma100 = _sma(df['close'], 100)
    base = ((mom > 0) & (df['close'] > sma100) & (rv < rv_high)).astype(float)

    atr = _atr(df, 22)
    n = 22
    chand_long = df['high'].rolling(n).max() - 3.0 * atr
    c = df['close']
    pos = np.zeros(len(c))
    in_pos = False
    trail = -np.inf
    for i in range(len(c)):
        if pd.isna(base.iloc[i]) or pd.isna(chand_long.iloc[i]):
            continue
        if not in_pos:
            if base.iloc[i] > 0:
                in_pos = True
                trail = chand_long.iloc[i]
        else:
            new_trail = chand_long.iloc[i]
            if new_trail > trail: trail = new_trail
            if c.iloc[i] < trail or base.iloc[i] == 0:
                in_pos = False
                trail = -np.inf
        pos[i] = 1.0 if in_pos else 0.0
    return pd.Series(pos, index=df.index)


def keltner_w_atr_stop_4h(df, n=20, k=1.5, atr_mult=3.0):
    """Keltner entry on 4h with looser exit."""
    ema = _ema(df['close'], n)
    atr = _atr(df, n)
    upper = ema + k*atr
    entry = df['close'] > upper

    c = df['close']
    atr14 = _atr(df, 14)
    pos = np.zeros(len(c))
    in_pos = False
    trail = -np.inf
    for i in range(len(c)):
        if pd.isna(upper.iloc[i]) or pd.isna(atr14.iloc[i]):
            continue
        if not in_pos:
            if entry.iloc[i]:
                in_pos = True
                trail = c.iloc[i] - atr_mult * atr14.iloc[i]
        else:
            new_trail = c.iloc[i] - atr_mult * atr14.iloc[i]
            if new_trail > trail: trail = new_trail
            if c.iloc[i] < trail:
                in_pos = False
                trail = -np.inf
        pos[i] = 1.0 if in_pos else 0.0
    return pd.Series(pos, index=df.index)


def weekly_trend_btc(df_daily):
    """Resample daily BTC to weekly, apply trend filter, project back to daily."""
    weekly = df_daily.resample('W').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
    sma10w = _sma(weekly['close'], 10)
    sma30w = _sma(weekly['close'], 30)
    weekly_long = (weekly['close'] > sma10w) & (sma10w > sma30w)
    weekly_sig = weekly_long.astype(float)
    # forward-fill to daily index
    daily_sig = weekly_sig.reindex(df_daily.index, method='ffill').fillna(0)
    return daily_sig


df_btc1d = load('BTC/USDT', '1d')
df_btc4h = load('BTC/USDT', '4h')

TESTS = [
    ("cci_trend_btc1d", df_btc1d, lambda d: cci_trend(d, 20, 100), 365),
    ("cci_trend_btc4h", df_btc4h, lambda d: cci_trend(d, 20, 100), 365*6),
    ("tsi_momentum_btc1d", df_btc1d, tsi_momentum, 365),
    ("coppock_btc1d", df_btc1d, lambda d: coppock_curve(d, 294, 231, 70), 365),
    ("williams_r_btc1d", df_btc1d, lambda d: williams_r_trend(d, 14, -50), 365),
    ("williams_r_btc4h", df_btc4h, lambda d: williams_r_trend(d, 14, -50), 365*6),
    ("kama_trend_btc1d", df_btc1d, lambda d: kama_trend(d, 10, 2, 30), 365),
    ("chandelier_btc1d", df_btc1d, lambda d: chandelier_exit(d, 22, 3.0), 365),
    ("hmm_strict_btc1d", df_btc1d, hmm_strict, 365),
    ("hmm_with_chandelier_btc1d", df_btc1d, hmm_with_chandelier, 365),
    ("keltner_atr_stop_btc4h", df_btc4h, lambda d: keltner_w_atr_stop_4h(d, 20, 1.5, 3.0), 365*6),
    ("weekly_trend_btc", df_btc1d, weekly_trend_btc, 365),
]

passed = []
for name, df, fn, bpy in TESTS:
    t0 = time.time()
    try:
        v = validate(name, df, fn, bars_per_year=bpy)
    except Exception as e:
        print(f"[{name}] ERROR: {e}"); import traceback; traceback.print_exc(); continue
    save_verdict(v); print_verdict(v)
    print(f"  (took {time.time()-t0:.1f}s)")
    if v.passed: passed.append(name)

print("\n" + "="*70)
print(f"BATCH 5: {len(passed)}/{len(TESTS)} passed")
print("="*70)
for p in passed: print(f"  PASS: {p}")
