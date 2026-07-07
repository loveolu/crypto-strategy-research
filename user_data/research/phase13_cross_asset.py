"""
Phase 13: Cross-asset ideas from Forven, adapted to our data.

1. BTC-dominance rotation proxy [btc_dominance_rotation.py]
   True dominance needs market caps; proxy = BTC price relative to an
   equal-weight alt basket. Rising relative strength -> concentrate in BTC,
   falling -> rotate into alts (only those with TVT core on). This adds a NEW
   information axis (relative strength between assets) on top of the champion.

2. ETH/BTC return-spread z-score fade [cross_asset_divergence.py]
   Long-only adaptation: buy the leg that underperformed by >2 sigma over 30d,
   exit when the spread normalizes (|z| < 0.5). Raw and regime-gated.

Same pipeline: fees 0.15%/side, 2-bar lag, 70/15/15, WF, MC.
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

SYMS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'BNB']
ALTS = [s for s in SYMS if s != 'BTC']
closes = pd.DataFrame({s: load_fut(s)['close'] for s in SYMS}).sort_index()
ret_mat = closes.pct_change()

core_mat, scale_mat = pd.DataFrame(index=closes.index), pd.DataFrame(index=closes.index)
for s in SYMS:
    c = closes[s]
    core_mat[s] = ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)
    rv = c.pct_change().rolling(30).std() * np.sqrt(365)
    scale_mat[s] = (0.40 / rv).clip(0, 1)


def net_from_weights(W):
    W = W.reindex(closes.index).fillna(0)
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
    return ret.mean() / ret.std() * np.sqrt(365), (eq / eq.cummax() - 1).min(), cagr


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
        s_i, e_i = int(n * (0.5 + k * 0.125)), min(int(n * (0.5 + (k + 1) * 0.125)), n)
        wf.append(m(ret.iloc[s_i:e_i]))
    blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
    rng = np.random.default_rng(11)
    dds = []
    for _ in range(500):
        seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        eq = np.cumprod(1 + seq)
        dds.append((eq / np.maximum.accumulate(eq) - 1).min())
    print(f"\n{label}")
    print(f"  FULL  Sharpe {sh_f:5.2f}  DD {dd_f*100:6.1f}%  CAGR {cg_f*100:+6.1f}%")
    print(f"  TRAIN {sh_tr:5.2f} | VAL {sh_vl:5.2f} | TEST {sh_te:5.2f}  (TEST CAGR {cg_te*100:+5.1f}%, DD {dd_te*100:5.1f}%)")
    print(f"  WF: " + " ".join(f"{x[0]:+.2f}" for x in wf) + f"  pos {sum(1 for x in wf if x[2] > 0)}/4"
          f"   MC medDD {np.percentile(dds, 50)*100:.0f}% P(DD<-25%) {(np.array(dds) < -0.25).mean()*100:.0f}%")
    return sh_te


def quantize(W):
    return ((W / 0.25).round() * 0.25).clip(0, 1)


# ------------------------------------------------- 1) dominance rotation
alt_basket = (1 + ret_mat[ALTS].fillna(0)).cumprod().mean(axis=1)
dom_proxy = closes['BTC'] / closes['BTC'].iloc[0] / alt_basket  # BTC rel strength vs alts

def rotation_W(lookback=14, btc_w_rising=1.0, btc_w_falling=0.30):
    rising = (dom_proxy > dom_proxy.shift(lookback)).astype(float)
    btc_w = rising * btc_w_rising + (1 - rising) * btc_w_falling
    W = pd.DataFrame(index=closes.index)
    W['BTC'] = quantize(core_mat['BTC'] * scale_mat['BTC']) * btc_w
    n_alts_on = core_mat[ALTS].sum(axis=1).replace(0, np.nan)
    alt_total = (1 - btc_w)
    for s in ALTS:
        W[s] = (quantize(core_mat[s] * scale_mat[s]) * alt_total / n_alts_on).fillna(0)
    # renormalize: cap gross exposure at 1
    gross = W.sum(axis=1)
    W = W.div(gross.where(gross > 1, 1), axis=0)
    return W

print("=" * 78)
print("1) BTC-DOMINANCE ROTATION PROXY (TVT-gated, vol-sized)")
print("=" * 78)
# reference points
Wc = pd.DataFrame({s: quantize(core_mat[s] * scale_mat[s]) / 2 for s in ['BTC', 'ETH']})
full_validation(net_from_weights(Wc), "BASELINE: champion TVT BTC+ETH")
for lb in (7, 14, 30):
    full_validation(net_from_weights(rotation_W(lookback=lb)), f"R: rotation lb={lb}d (BTC 100%/30%)")
full_validation(net_from_weights(rotation_W(14, 1.0, 0.0)), "R: rotation lb=14 hard switch (100%/0%)")

# ------------------------------------------------- 2) ETH/BTC z-score fade
print()
print("=" * 78)
print("2) ETH/BTC RETURN-SPREAD Z-SCORE FADE (long-only)")
print("=" * 78)
spread = ret_mat['ETH'] - ret_mat['BTC']
z = (spread - spread.rolling(30).mean()) / spread.rolling(30).std()

def zfade_sig(z_enter=2.0, z_exit=0.5, leg='ETH', gated=False):
    """Long `leg` when it UNDERperformed the other by z_enter sigma; exit at |z|<z_exit."""
    sgn = -1 if leg == 'ETH' else 1  # ETH underperforms when z very negative
    zz = z * sgn
    sig = np.zeros(len(z))
    in_pos = False
    zv = zz.values
    gate = core_mat[leg].values if gated else np.ones(len(z))
    for i in range(len(z)):
        if np.isnan(zv[i]):
            continue
        if not in_pos:
            if zv[i] > z_enter and gate[i] == 1:
                in_pos = True
        else:
            if abs(zv[i]) < z_exit or (gated and gate[i] == 0):
                in_pos = False
        sig[i] = 1.0 if in_pos else 0.0
    return pd.Series(sig, index=z.index)

for gated in (False, True):
    tag = "gated" if gated else "raw"
    W = pd.DataFrame(index=closes.index)
    W['ETH'] = zfade_sig(leg='ETH', gated=gated) * 0.5
    W['BTC'] = zfade_sig(leg='BTC', gated=gated) * 0.5
    full_validation(net_from_weights(W), f"Z: both-leg fade 2.0/0.5 ({tag})")

# combo: champion + z-fade sleeve at 25%
Wz = pd.DataFrame(index=closes.index)
Wz['ETH'] = zfade_sig(leg='ETH', gated=True) * 0.25
Wz['BTC'] = zfade_sig(leg='BTC', gated=True) * 0.25
Wcombo = Wc.reindex(closes.index).fillna(0) * 0.75
Wcombo['ETH'] = Wcombo['ETH'] + Wz['ETH']
Wcombo['BTC'] = Wcombo['BTC'] + Wz['BTC']
full_validation(net_from_weights(Wcombo.clip(0, 1)), "COMBO: 75% champion + 25% gated z-fade")
