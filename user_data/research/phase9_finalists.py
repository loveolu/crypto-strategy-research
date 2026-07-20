"""
Phase 9: OOS discipline on the finalists.

For each finalist: 70/15/15 chronological split + 4 walk-forward windows +
Monte Carlo. The key question: does ANY expanded-universe variant hold up
better than the BTC+ETH champion in the held-out recent period (2024-2026)?
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

def net_returns(W, port_vol_target=None):
    W = W.reindex(closes.index).fillna(0)
    if port_vol_target:
        pos0 = W.shift(2).fillna(0)
        r0 = (pos0 * ret_mat.fillna(0)).sum(axis=1)
        pvol = r0.rolling(30).std() * np.sqrt(365)
        pscale = ((port_vol_target / pvol).clip(0, 1.0) / 0.25).round() * 0.25
        W = W.mul(pscale, axis=0)
    pos = W.shift(2).fillna(0)
    gross = (pos * ret_mat.fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    return gross - turn * FEE

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
    sh_tr, dd_tr, cg_tr = m(ret.iloc[:i1])
    sh_vl, dd_vl, cg_vl = m(ret.iloc[i1:i2])
    sh_te, dd_te, cg_te = m(ret.iloc[i2:])
    # walk-forward quarters of the second half
    wf = []
    for k in range(4):
        s_i = int(n * (0.5 + k * 0.125))
        e_i = min(int(n * (0.5 + (k + 1) * 0.125)), n)
        wf.append(m(ret.iloc[s_i:e_i]))
    # MC: monthly block shuffle
    blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
    rng = np.random.default_rng(11)
    dds = []
    for _ in range(500):
        seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        eq = np.cumprod(1 + seq)
        dds.append((eq / np.maximum.accumulate(eq) - 1).min())
    print(f"\n{label}")
    print(f"  FULL  Sharpe {sh_f:5.2f}  DD {dd_f*100:6.1f}%  CAGR {cg_f*100:+6.1f}%")
    print(f"  TRAIN Sharpe {sh_tr:5.2f}  | VAL Sharpe {sh_vl:5.2f}  | TEST Sharpe {sh_te:5.2f}  (TEST CAGR {cg_te*100:+5.1f}%, DD {dd_te*100:5.1f}%)")
    print(f"  WF Sharpes: " + "  ".join(f"{x[0]:+.2f}" for x in wf) + f"   | positive {sum(1 for x in wf if x[2] > 0)}/4")
    print(f"  MC median DD {np.percentile(dds, 50)*100:.1f}%  p5 (worst) {np.percentile(dds, 5)*100:.1f}%  P(DD<-25%) {(np.array(dds) < -0.25).mean()*100:.0f}%")
    return sh_te

def tvt_W(symlist):
    q = ((core_mat[symlist] * scale_mat[symlist]) / 0.25).round() * 0.25
    return q.clip(0, 1) / len(symlist)

def hybrid_W(sat_w=0.15, K=2):
    alts = [s for s in SYMS if s != 'BTC']
    q_btc = ((core_mat[['BTC']] * scale_mat[['BTC']]) / 0.25).round() * 0.25
    ram = ramom_mat[alts].where(core_mat[alts] > 0)
    sel = (ram.rank(axis=1, ascending=False) <= K).astype(float)
    q_alt = ((sel * scale_mat[alts]) / 0.25).round() * 0.25
    return pd.concat([q_btc.clip(0, 1) * 0.5, q_alt.clip(0, 1) * sat_w], axis=1)

full_validation(net_returns(tvt_W(['BTC', 'ETH'])), "CHAMPION: TVT BTC+ETH")
full_validation(net_returns(tvt_W(['BTC', 'ETH', 'SOL']), port_vol_target=0.25), "FINALIST A: BTC+ETH+SOL + portvol 25%")
full_validation(net_returns(hybrid_W(0.15, 2)), "FINALIST B: hybrid BTC-core + top-2 alts @15%")
full_validation(net_returns(tvt_W(SYMS), port_vol_target=0.25), "FINALIST C: 9-asset + portvol 25%")
