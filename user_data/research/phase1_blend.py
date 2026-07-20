"""
Phase 1: Strategy return-stream blending.

Idea: individual strategies cap at Sharpe ~1.2, but if their return streams are
imperfectly correlated, an equal- or risk-weighted blend can exceed any single
component. This is the classical (and only data-free) way to lift Sharpe.

Selection-bias control: blend weights are fixed ex-ante (equal weight or
inverse-vol estimated on TRAIN only), never optimized on the full window.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from validator import load, signal_to_returns, ANNUALIZATION_DAILY
import strategies as S
import multi_asset as MA


def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()


# ---------- regenerate top candidate return streams ----------
btc = load('BTC/USDT', '1d')
eth = load('ETH/USDT', '1d')
common_start = max(btc.index.min(), eth.index.min())
btc_c = btc.loc[common_start:]
eth_c = eth.loc[common_start:]
data_be = {"BTC": btc_c, "ETH": eth_c}


def hmm_two_state(df):
    ret = df['close'].pct_change()
    rv = ret.rolling(60).std() * np.sqrt(365)
    rv_high = rv.rolling(365).quantile(0.80)
    mom = df['close'].pct_change(30)
    sma100 = _sma(df['close'], 100)
    return ((mom > 0) & (df['close'] > sma100) & (rv < rv_high)).astype(float)


def ensemble_3of3(df):
    c = df['close']
    s1 = (c > _sma(c, 200)).astype(float)
    s2 = (c.pct_change(30) > 0).astype(float)
    s3 = (_ema(c, 20) > _ema(c, 50)).astype(float)
    return ((s1 + s2 + s3) >= 3).astype(float)


def donchian_55_20(df):
    return S.donchian_breakout_vec(df, 55, 20)


def adx_trend(df):
    return S.adx_trend(df, 25, 20, 50)


streams = {}

# Single-asset BTC streams (on common window for comparability)
for name, fn in [
    ("hmm", hmm_two_state),
    ("ens3", ensemble_3of3),
    ("donch", donchian_55_20),
    ("adx", adx_trend),
]:
    r = signal_to_returns(btc_c, fn(btc_c))
    streams[name] = r["ret_net"]

# Multi-asset streams
for name, fn in [
    ("volbask", lambda d: MA.vol_adjusted_basket_trend(d, 200, 30, 0.40)),
    ("xsect30", lambda d: MA.cross_sectional_momentum(d, 30)),
    ("pairs", lambda d: MA.pairs_spread_revert(d, 30, 2.0, 0.5)),
]:
    sigs = fn(data_be)
    r = MA.portfolio_returns(data_be, sigs)
    streams[name] = r["ret_net"]

# Align all to common index
idx = streams["hmm"].index
R = pd.DataFrame({k: v.reindex(idx).fillna(0) for k, v in streams.items()})

print("Correlation matrix of daily strategy returns:")
print(R.corr().round(2).to_string())
print()

def perf(ret, label):
    eq = (1 + ret).cumprod()
    n_years = len(ret) / 365
    cagr = eq.iloc[-1] ** (1 / n_years) - 1
    sharpe = ret.mean() / ret.std() * np.sqrt(365) if ret.std() > 0 else 0
    peak = eq.cummax()
    dd = (eq / peak - 1).min()
    yearly = (1 + ret).groupby(ret.index.year).prod() - 1
    pos_years = (yearly > 0).sum()
    print(f"{label:28s} CAGR {cagr*100:+6.1f}%  Sharpe {sharpe:5.2f}  DD {dd*100:6.1f}%  "
          f"posyrs {pos_years}/{len(yearly)}  " +
          " ".join(f"{y}:{v*100:+.0f}%" for y, v in yearly.items()))
    return sharpe, dd, cagr

print("Individual streams (common window):")
for k in R.columns:
    perf(R[k], k)

print()
print("Blends:")

# Equal weight all 7
perf(R.mean(axis=1), "EW_all7")

# Equal weight top-Sharpe trio with low mutual correlation
perf(R[["hmm", "volbask", "pairs"]].mean(axis=1), "EW_hmm+volbask+pairs")
perf(R[["hmm", "volbask", "xsect30"]].mean(axis=1), "EW_hmm+volbask+xsect")
perf(R[["hmm", "pairs", "xsect30"]].mean(axis=1), "EW_hmm+pairs+xsect")
perf(R[["hmm", "volbask"]].mean(axis=1), "EW_hmm+volbask")
perf(R[["hmm", "volbask", "xsect30", "pairs"]].mean(axis=1), "EW_4core")
perf(R[["hmm", "ens3", "volbask", "xsect30", "pairs"]].mean(axis=1), "EW_5core")

# Inverse-vol weights estimated on TRAIN only (first 70%), applied to full window
n = len(R)
i_tr = int(n * 0.70)
train_vol = R.iloc[:i_tr].std()
iv_w = (1 / train_vol.replace(0, np.nan)).fillna(0)
core = ["hmm", "volbask", "xsect30", "pairs"]
w = iv_w[core] / iv_w[core].sum()
print(f"\nInverse-vol weights (train-estimated): {dict(w.round(3))}")
perf((R[core] * w).sum(axis=1), "IV_4core")

# IV blend evaluated on TEST only (last 30% truly held-out for blend choice)
blend_full = (R[core] * w).sum(axis=1)
print("\nTrain/test split of IV_4core blend (weights from train only):")
perf(blend_full.iloc[:i_tr], "IV_4core TRAIN")
perf(blend_full.iloc[i_tr:], "IV_4core TEST(held-out)")

ew4 = R[core].mean(axis=1)
print("\nTrain/test split of EW_4core blend (no estimation at all):")
perf(ew4.iloc[:i_tr], "EW_4core TRAIN")
perf(ew4.iloc[i_tr:], "EW_4core TEST(held-out)")
