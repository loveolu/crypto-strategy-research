"""
Strategy battery for autonomous validation.

Each function takes a DataFrame with OHLCV and returns a Series of {-1, 0, 1}
position targets, aligned to df.index. Signal at bar t is acted on at bar t+1 open.

Indicators are pure pandas/numpy (no TA-Lib dependency).
"""
import numpy as np
import pandas as pd


def _ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def _sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n).mean()


def _rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = -d.clip(upper=0).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    up = h.diff()
    dn = -l.diff()
    plus_dm = ((up > dn) & (up > 0)) * up
    minus_dm = ((dn > up) & (dn > 0)) * dn
    atr = _atr(df, n)
    pdi = 100 * plus_dm.ewm(alpha=1 / n, adjust=False).mean() / atr
    mdi = 100 * minus_dm.ewm(alpha=1 / n, adjust=False).mean() / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def _macd(s: pd.Series, fast: int = 12, slow: int = 26, sig: int = 9):
    f = _ema(s, fast)
    sl = _ema(s, slow)
    macd = f - sl
    signal = _ema(macd, sig)
    return macd, signal, macd - signal


# ---------- STRATEGIES ----------

def donchian_breakout(df: pd.DataFrame, lookback: int = 20, exit_lookback: int = 10) -> pd.Series:
    """Turtle-style: enter long when close breaks N-day high, exit when below M-day low."""
    hi = df["high"].rolling(lookback).max().shift(1)
    lo = df["low"].rolling(exit_lookback).min().shift(1)
    c = df["close"]
    pos = pd.Series(0.0, index=df.index)
    in_pos = False
    for i in range(len(c)):
        if not in_pos and c.iloc[i] > hi.iloc[i] if pd.notna(hi.iloc[i]) else False:
            in_pos = True
        elif in_pos and (c.iloc[i] < lo.iloc[i] if pd.notna(lo.iloc[i]) else False):
            in_pos = False
        pos.iloc[i] = 1 if in_pos else 0
    return pos


def donchian_breakout_vec(df: pd.DataFrame, lookback: int = 20, exit_lookback: int = 10) -> pd.Series:
    """Vectorized Donchian: position = 1 while close > rolling high, switches on cross."""
    c = df["close"]
    hi = df["high"].rolling(lookback).max().shift(1)
    lo = df["low"].rolling(exit_lookback).min().shift(1)
    enter = c > hi
    exit_ = c < lo
    pos_state = pd.Series(np.nan, index=df.index)
    pos_state[enter] = 1.0
    pos_state[exit_ & ~enter] = 0.0
    pos = pos_state.ffill().fillna(0)
    return pos


def ma_cross(df: pd.DataFrame, fast: int = 50, slow: int = 200) -> pd.Series:
    f = _sma(df["close"], fast)
    s = _sma(df["close"], slow)
    return (f > s).astype(float)


def rsi_mean_reversion(df: pd.DataFrame, n: int = 2, lo: int = 10, hi: int = 50) -> pd.Series:
    """Larry Connors-style: long when RSI(2) < lo, exit when RSI(2) > hi."""
    r = _rsi(df["close"], n)
    sig = pd.Series(np.nan, index=df.index)
    sig[r < lo] = 1.0
    sig[r > hi] = 0.0
    return sig.ffill().fillna(0)


def macd_trend(df: pd.DataFrame) -> pd.Series:
    """Long when MACD > signal AND price > EMA200."""
    macd, sig, hist = _macd(df["close"])
    ema200 = _ema(df["close"], 200)
    long = (macd > sig) & (df["close"] > ema200)
    return long.astype(float)


def bollinger_revert(df: pd.DataFrame, n: int = 20, k: float = 2.0) -> pd.Series:
    """Long when close < lower band AND price > SMA200 (only fade dips in uptrend)."""
    m = _sma(df["close"], n)
    sd = df["close"].rolling(n).std()
    lower = m - k * sd
    sma200 = _sma(df["close"], 200)
    sig = pd.Series(np.nan, index=df.index)
    sig[(df["close"] < lower) & (df["close"] > sma200)] = 1.0
    sig[df["close"] > m] = 0.0
    return sig.ffill().fillna(0)


def adx_trend(df: pd.DataFrame, adx_min: float = 25, ema_fast: int = 20, ema_slow: int = 50) -> pd.Series:
    """Long when trend strong (ADX>25) AND EMA fast > slow."""
    adx = _adx(df)
    ef = _ema(df["close"], ema_fast)
    es = _ema(df["close"], ema_slow)
    return ((adx > adx_min) & (ef > es)).astype(float)


def roc_momentum(df: pd.DataFrame, lookback: int = 30, hold: int = 5) -> pd.Series:
    """Long when N-day ROC > 0 (simple time-series momentum), held while positive."""
    roc = df["close"].pct_change(lookback)
    return (roc > 0).astype(float)


def channel_breakout_atr(df: pd.DataFrame, lookback: int = 50, atr_mult: float = 2.0) -> pd.Series:
    """Enter long on N-day high break, trail by atr_mult * ATR."""
    c = df["close"]
    hi = df["high"].rolling(lookback).max().shift(1)
    atr = _atr(df, 14)

    pos = np.zeros(len(c))
    trail = np.full(len(c), np.nan)
    in_pos = False
    cur_trail = -np.inf
    for i in range(len(c)):
        if not in_pos:
            if pd.notna(hi.iloc[i]) and c.iloc[i] > hi.iloc[i]:
                in_pos = True
                cur_trail = c.iloc[i] - atr_mult * atr.iloc[i]
        else:
            new_trail = c.iloc[i] - atr_mult * atr.iloc[i]
            if new_trail > cur_trail:
                cur_trail = new_trail
            if c.iloc[i] < cur_trail:
                in_pos = False
                cur_trail = -np.inf
        pos[i] = 1.0 if in_pos else 0.0
        trail[i] = cur_trail
    return pd.Series(pos, index=df.index)


def vol_target_btc(df: pd.DataFrame, target_vol: float = 0.40) -> pd.Series:
    """Variable exposure: scale by 30d realized vol vs target. Capped [0, 1]."""
    ret = df["close"].pct_change()
    rv = ret.rolling(30).std() * np.sqrt(365)
    pos = (target_vol / rv).clip(0, 1)
    return pos.fillna(0)


def regime_trend(df: pd.DataFrame, sma_n: int = 200, slope_lookback: int = 20) -> pd.Series:
    """Long when close > SMA200 AND SMA200 is rising."""
    sma = _sma(df["close"], sma_n)
    rising = sma.diff(slope_lookback) > 0
    long = (df["close"] > sma) & rising
    return long.astype(float)


def stoch_rsi_revert(df: pd.DataFrame) -> pd.Series:
    """Long when StochRSI < 0.2, exit at > 0.8."""
    r = _rsi(df["close"], 14)
    sr = (r - r.rolling(14).min()) / (r.rolling(14).max() - r.rolling(14).min())
    sig = pd.Series(np.nan, index=df.index)
    sig[sr < 0.2] = 1.0
    sig[sr > 0.8] = 0.0
    return sig.ffill().fillna(0)


def keltner_breakout(df: pd.DataFrame, n: int = 20, k: float = 1.5) -> pd.Series:
    """Long when close > upper Keltner channel (EMA + k*ATR)."""
    ema = _ema(df["close"], n)
    atr = _atr(df, n)
    upper = ema + k * atr
    lower = ema - k * atr
    sig = pd.Series(np.nan, index=df.index)
    sig[df["close"] > upper] = 1.0
    sig[df["close"] < lower] = 0.0
    return sig.ffill().fillna(0)


def triple_screen(df: pd.DataFrame) -> pd.Series:
    """Elder triple screen-style: long if EMA20 rising AND MACD > sig AND RSI > 50."""
    ema20 = _ema(df["close"], 20)
    macd, sig, _ = _macd(df["close"])
    r = _rsi(df["close"], 14)
    long = (ema20 > ema20.shift(1)) & (macd > sig) & (r > 50)
    return long.astype(float)
