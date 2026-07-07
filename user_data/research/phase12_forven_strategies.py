"""
Phase 12: Strategy ideas mined from Forven (github.com/judder659/Forven).

Tested against our standard pipeline (fees 0.15%/side, 2-bar lag, 70/15/15,
walk-forward, MC). All variants get the same vol-target sizing overlay as the
champion so comparisons are apples-to-apples.

Candidates (the only Forven builtins that are new axes for us):
  A. Supertrend (10, 3.0) trend state machine          [supertrend.py]
  B. Supertrend gated by SMA200 regime                 [supertrend + our core]
  C. TVT core entry + Chandelier ATR trailing exit     [chandelier_exit.py]
  D. TVT core entry + Chandelier OR core-break exit
  BASELINE: TVT core (champion construct)
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from pathlib import Path

FEE = 0.0015
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')

def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()

def load_fut(sym):
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype({c: float for c in ['open', 'high', 'low', 'close', 'volume']})

SYMS = ['BTC', 'ETH']
DATA = {s: load_fut(s) for s in SYMS}
closes = pd.DataFrame({s: DATA[s]['close'] for s in SYMS}).sort_index()
ret_mat = closes.pct_change()


def true_range(df):
    pc = df['close'].shift(1)
    return pd.concat([df['high'] - df['low'], (df['high'] - pc).abs(), (df['low'] - pc).abs()], axis=1).max(axis=1)


def supertrend_dir(df, length=10, mult=3.0):
    """Canonical supertrend final-band state machine. Returns +1/-1 direction."""
    hl2 = (df['high'] + df['low']) / 2
    atr = true_range(df).ewm(alpha=1 / length, adjust=False).mean()  # Wilder
    ub, lb = (hl2 + mult * atr).values, (hl2 - mult * atr).values
    close = df['close'].values
    n = len(df)
    f_ub, f_lb = ub.copy(), lb.copy()
    direction = np.ones(n)
    for i in range(1, n):
        f_ub[i] = ub[i] if (ub[i] < f_ub[i - 1] or close[i - 1] > f_ub[i - 1]) else f_ub[i - 1]
        f_lb[i] = lb[i] if (lb[i] > f_lb[i - 1] or close[i - 1] < f_lb[i - 1]) else f_lb[i - 1]
        if direction[i - 1] > 0:
            direction[i] = -1 if close[i] < f_lb[i] else 1
        else:
            direction[i] = 1 if close[i] > f_ub[i] else -1
    return pd.Series(direction, index=df.index)


def tvt_core(df):
    c = df['close']
    return ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)


def chandelier_signal(df, core, atr_period=22, mult=3.0, lookback=22, core_exit=False):
    """Enter when core==1 and price above rolling chandelier stop.
    Exit when close < chandelier (optionally also when core breaks)."""
    atr = true_range(df).rolling(atr_period).mean()
    chand = df['high'].rolling(lookback).max() - mult * atr
    close, ch, co = df['close'].values, chand.values, core.values
    sig = np.zeros(len(df))
    in_pos = False
    for i in range(len(df)):
        if np.isnan(ch[i]):
            continue
        if not in_pos:
            if co[i] == 1 and close[i] > ch[i]:
                in_pos = True
        else:
            if close[i] < ch[i] or (core_exit and co[i] == 0):
                in_pos = False
        sig[i] = 1.0 if in_pos else 0.0
    return pd.Series(sig, index=df.index)


def vol_scale(df, target=0.40):
    rv = df['close'].pct_change().rolling(30).std() * np.sqrt(365)
    return (target / rv).clip(0, 1)


def portfolio_net(sig_by_sym):
    """Equal-weight portfolio with vol-target sizing, quantized, 2-bar lag, net of fees."""
    W = pd.DataFrame(index=closes.index)
    for s in SYMS:
        q = ((sig_by_sym[s].reindex(closes.index).fillna(0) * vol_scale(DATA[s]).reindex(closes.index)) / 0.25).round() * 0.25
        W[s] = q.clip(0, 1) / len(SYMS)
    pos = W.shift(2).fillna(0)
    gross = (pos * ret_mat.fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    return (gross - turn * FEE).dropna()


def m(ret):
    ret = ret.dropna()
    if len(ret) < 10 or ret.std() == 0:
        return 0, 0, 0
    eq = (1 + ret).cumprod()
    yrs = len(ret) / 365
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1
    sh = ret.mean() / ret.std() * np.sqrt(365)
    dd = (eq / eq.cummax() - 1).min()
    return sh, dd, cagr


def full_validation(ret, label):
    ret = ret.dropna()
    n = len(ret)
    i1, i2 = int(n * 0.70), int(n * 0.85)
    sh_f, dd_f, cg_f = m(ret)
    sh_tr, _, _ = m(ret.iloc[:i1])
    sh_vl, _, _ = m(ret.iloc[i1:i2])
    sh_te, dd_te, cg_te = m(ret.iloc[i2:])
    wf = []
    for k in range(4):
        s_i = int(n * (0.5 + k * 0.125))
        e_i = min(int(n * (0.5 + (k + 1) * 0.125)), n)
        wf.append(m(ret.iloc[s_i:e_i]))
    blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
    rng = np.random.default_rng(11)
    dds = []
    for _ in range(500):
        seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        eq = np.cumprod(1 + seq)
        dds.append((eq / np.maximum.accumulate(eq) - 1).min())
    yearly = (1 + ret).groupby(ret.index.year).prod() - 1
    ystr = " ".join(f"{y}:{v*100:+.0f}" for y, v in yearly.items())
    print(f"\n{label}")
    print(f"  FULL  Sharpe {sh_f:5.2f}  DD {dd_f*100:6.1f}%  CAGR {cg_f*100:+6.1f}%   [{ystr}]")
    print(f"  TRAIN {sh_tr:5.2f} | VAL {sh_vl:5.2f} | TEST {sh_te:5.2f}  (TEST CAGR {cg_te*100:+5.1f}%, DD {dd_te*100:5.1f}%)")
    print(f"  WF: " + " ".join(f"{x[0]:+.2f}" for x in wf) + f"  pos {sum(1 for x in wf if x[2] > 0)}/4"
          f"   MC medDD {np.percentile(dds, 50)*100:.0f}% P(DD<-25%) {(np.array(dds) < -0.25).mean()*100:.0f}%")
    return sh_te


# ------------------------------------------------------------------ variants
st_dir = {s: supertrend_dir(DATA[s]) for s in SYMS}
core = {s: tvt_core(DATA[s]) for s in SYMS}

variants = {
    "BASELINE: TVT core (champion)": {s: core[s] for s in SYMS},
    "A: Supertrend(10,3) alone": {s: (st_dir[s] > 0).astype(float) for s in SYMS},
    "B: Supertrend + SMA200 gate": {
        s: ((st_dir[s] > 0) & (DATA[s]['close'] > _sma(DATA[s]['close'], 200))).astype(float) for s in SYMS},
    "C: TVT entry + Chandelier(22,3) exit only": {
        s: chandelier_signal(DATA[s], core[s], core_exit=False) for s in SYMS},
    "D: TVT entry + Chandelier OR core exit": {
        s: chandelier_signal(DATA[s], core[s], core_exit=True) for s in SYMS},
}

for label, sigs in variants.items():
    full_validation(portfolio_net(sigs), label)
