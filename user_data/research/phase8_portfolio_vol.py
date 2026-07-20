"""
Phase 8: Portfolio-level vol targeting on the leading constructs.

Classic two-layer risk control: per-asset vol sizing (already in) + scale the
ENTIRE portfolio by target_vol / realized_portfolio_vol. Theory-driven, one
parameter (target), swept for plateau.
Also sensitivity: satellite weight in the hybrid.
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
    return df.set_index('date').sort_index().astype({c: float for c in ['open','high','low','close','volume']})

SYMS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'BNB']
closes = pd.DataFrame({s: load_fut(s)['close'] for s in SYMS}).sort_index()
ret_mat = closes.pct_change()

core_mat = pd.DataFrame(index=closes.index)
scale_mat = pd.DataFrame(index=closes.index)
ramom_mat = pd.DataFrame(index=closes.index)
for s in SYMS:
    c = closes[s]
    core_mat[s] = ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)
    rv = c.pct_change().rolling(30).std() * np.sqrt(365)
    scale_mat[s] = (0.40 / rv).clip(0, 1)
    ramom_mat[s] = c.pct_change(30) / (rv / np.sqrt(365)) / np.sqrt(30)

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
    print(f"{label:40s} CAGR {cagr*100:+6.1f}%  Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  posyrs {pos_y}/{len(yearly)}{extra}")
    return sh, dd, cagr

def run_weights(W, label, port_vol_target=None, show_yearly=True):
    W = W.reindex(closes.index).fillna(0)
    if port_vol_target:
        # estimate realized portfolio vol from the recent UNscaled portfolio returns
        pos0 = W.shift(2).fillna(0)
        r0 = (pos0 * ret_mat.fillna(0)).sum(axis=1)
        pvol = r0.rolling(30).std() * np.sqrt(365)
        pscale = (port_vol_target / pvol).clip(0, 1.0)
        pscale = ((pscale / 0.25).round() * 0.25)  # quantize portfolio scale too
        W = W.mul(pscale, axis=0)
    pos = W.shift(2).fillna(0)
    gross = (pos * ret_mat.fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    net = gross - turn * FEE
    return stats(net, label, show_yearly), net

def hybrid_W(sat_w=0.25, K=2):
    alts = [s for s in SYMS if s != 'BTC']
    q_btc = ((core_mat[['BTC']] * scale_mat[['BTC']]) / 0.25).round() * 0.25
    ram = ramom_mat[alts].where(core_mat[alts] > 0)
    sel = (ram.rank(axis=1, ascending=False) <= K).astype(float)
    q_alt = ((sel * scale_mat[alts]) / 0.25).round() * 0.25
    return pd.concat([q_btc.clip(0, 1) * 0.5, q_alt.clip(0, 1) * sat_w], axis=1)

def tvt_W(symlist):
    q = ((core_mat[symlist] * scale_mat[symlist]) / 0.25).round() * 0.25
    return q.clip(0, 1) / len(symlist)

print("=" * 118)
print("PORTFOLIO-LEVEL VOL TARGET on hybrid (BTC 50% + top-2 alts 25%)")
print("=" * 118)
run_weights(hybrid_W(), "hybrid (no port overlay)")
for pv in [0.20, 0.25, 0.30, 0.35]:
    run_weights(hybrid_W(), f"hybrid + portvol {int(pv*100)}%", port_vol_target=pv)

print()
print("SATELLITE WEIGHT SENSITIVITY (no overlay):")
for sw in [0.15, 0.20, 0.25, 0.30]:
    run_weights(hybrid_W(sat_w=sw), f"hybrid sat={int(sw*100)}%", show_yearly=False)
print("SATELLITE K SENSITIVITY:")
for K in [1, 2, 3]:
    run_weights(hybrid_W(K=K), f"hybrid K={K}", show_yearly=False)

print()
print("=" * 118)
print("PORTFOLIO-LEVEL VOL TARGET on BTC+ETH+SOL and 9-asset baskets")
print("=" * 118)
run_weights(tvt_W(['BTC', 'ETH', 'SOL']), "BTC+ETH+SOL (no overlay)")
for pv in [0.20, 0.25, 0.30]:
    run_weights(tvt_W(['BTC', 'ETH', 'SOL']), f"BTC+ETH+SOL + portvol {int(pv*100)}%", port_vol_target=pv)
run_weights(tvt_W(SYMS), "9-asset (no overlay)")
for pv in [0.20, 0.25, 0.30]:
    run_weights(tvt_W(SYMS), f"9-asset + portvol {int(pv*100)}%", port_vol_target=pv)
