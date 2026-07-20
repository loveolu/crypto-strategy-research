"""
Phase 7: Expanded-universe portfolio constructs.

(a) Equal-weight basket of per-asset TrendVolTarget streams (N = 2..9)
(b) Cross-sectional top-K: among in-regime assets, long the K best by
    risk-adjusted 30d momentum, vol-target sized
(c) The champion BTC+ETH for reference
All fees included at stream level; joint sims charge fees on weight changes.
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
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})

SYMS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'BNB']
closes = pd.DataFrame({s: load_fut(s)['close'] for s in SYMS})
closes = closes.sort_index()

def stats(ret, label, show_yearly=True):
    ret = ret.dropna()
    eq = (1 + ret).cumprod()
    yrs = len(ret) / 365
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1
    sh = ret.mean() / ret.std() * np.sqrt(365) if ret.std() > 0 else 0
    dd = (eq / eq.cummax() - 1).min()
    yearly = (1 + ret).groupby(ret.index.year).prod() - 1
    pos_y = (yearly > 0).sum()
    extra = "  " + " ".join(f"{y}:{v*100:+.0f}" for y, v in yearly.items()) if show_yearly else ""
    print(f"{label:34s} CAGR {cagr*100:+6.1f}%  Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  posyrs {pos_y}/{len(yearly)}{extra}")
    return sh, dd, cagr

# ---------- per-asset building blocks ----------
core_mat = pd.DataFrame(index=closes.index)
scale_mat = pd.DataFrame(index=closes.index)
ramom_mat = pd.DataFrame(index=closes.index)
for s in SYMS:
    c = closes[s]
    s1 = (c > _sma(c, 200))
    s2 = (c.pct_change(30) > 0)
    s3 = (_ema(c, 20) > _ema(c, 50))
    core_mat[s] = (s1 & s2 & s3).astype(float)
    rv = c.pct_change().rolling(30).std() * np.sqrt(365)
    scale_mat[s] = (0.40 / rv).clip(0, 1)
    ramom_mat[s] = c.pct_change(30) / (rv / np.sqrt(365)) / np.sqrt(30)  # risk-adjusted momentum

ret_mat = closes.pct_change()

def joint_sim(weight_fn, label, show_yearly=True):
    """weight_fn(t_index) -> target weights DataFrame aligned to closes.
    Weights applied with 2-bar lag; fees on weight changes."""
    W = weight_fn()
    W = W.reindex(closes.index).fillna(0)
    pos = W.shift(2).fillna(0)
    gross = (pos * ret_mat.fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    net = gross - turn * FEE
    return stats(net, label, show_yearly), net

print("=" * 115)
print("(a) EQUAL-WEIGHT TVT BASKETS (quantized scale, common window = union of asset histories)")
print("=" * 115)

def tvt_weights(symlist):
    def fn():
        q = ((core_mat[symlist] * scale_mat[symlist]) / 0.25).round() * 0.25
        return q.clip(0, 1) / len(symlist)
    return fn

(_, net2) = joint_sim(tvt_weights(['BTC', 'ETH']), "TVT BTC+ETH (champion ref)")
(_, net3) = joint_sim(tvt_weights(['BTC', 'ETH', 'SOL']), "TVT BTC+ETH+SOL")
(_, net5) = joint_sim(tvt_weights(['BTC', 'ETH', 'SOL', 'XRP', 'LINK']), "TVT 5-asset")
(_, net7) = joint_sim(tvt_weights(['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'LINK']), "TVT 7-asset")
(_, net9) = joint_sim(tvt_weights(SYMS), "TVT 9-asset")

print()
print("=" * 115)
print("(b) CROSS-SECTIONAL TOP-K (in-regime assets ranked by risk-adj momentum, vol-sized)")
print("=" * 115)

def topk_weights(K, symlist=SYMS):
    def fn():
        ram = ramom_mat[symlist].where(core_mat[symlist] > 0)
        ranks = ram.rank(axis=1, ascending=False)
        sel = (ranks <= K).astype(float)
        q = ((sel * scale_mat[symlist]) / 0.25).round() * 0.25
        return q.clip(0, 1) / K
    return fn

for K in [1, 2, 3, 4]:
    joint_sim(topk_weights(K), f"XSect top-{K} of 9 (vol-sized)")

print()
print("=" * 115)
print("(c) HYBRID: BTC core position + top-2 alt satellite")
print("=" * 115)

def hybrid_weights():
    alts = ['ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'BNB']
    q_btc = ((core_mat[['BTC']] * scale_mat[['BTC']]) / 0.25).round() * 0.25
    ram = ramom_mat[alts].where(core_mat[alts] > 0)
    ranks = ram.rank(axis=1, ascending=False)
    sel = (ranks <= 2).astype(float)
    q_alt = ((sel * scale_mat[alts]) / 0.25).round() * 0.25
    W = pd.concat([q_btc.clip(0, 1) * 0.5, q_alt.clip(0, 1) * 0.25], axis=1)
    return W

joint_sim(hybrid_weights, "BTC 50% core + top-2 alts 25% each")

print()
print("=" * 115)
print("(d) CORRELATION of basket sizes — TVT stream correlations on expanded universe")
print("=" * 115)
streams = pd.read_parquet('C:/Users/Comec/Projects/freqtrade/user_data/research/tvt_streams.parquet')
corr = streams.corr()
print(corr.round(2).to_string())
print(f"\nMean pairwise correlation: {corr.values[np.triu_indices_from(corr.values, 1)].mean():.2f}")
