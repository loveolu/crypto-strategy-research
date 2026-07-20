"""
Phase 16: H-BearShort — mirror-image trend gate as a short sleeve (trial #98).

PRE-REGISTERED experiment. Spec locked in SESSION_2026-07-10_BEARSHORT.md section 1
BEFORE this script was written or produced any numbers. Assignment: research/NEXT_TASK.md
(2026-07-10, Research Director cycle #2).

  Sole variant (trial #98): short BTC+ETH perpetual futures when the champion's gate is
  fully mirrored:  close < SMA200  AND  ROC30 < 0  AND  EMA20 < EMA50  (all three).
  Exit when any condition breaks. Sizing identical to the champion, mirrored:
  clip(0.40 / rv30_cc, 0, 1) quantized to 0.25 steps, weights/2 across the 2-pair
  basket (50% per-pair cap). Fees 0.15%/side, 2-bar signal lag, -30% disaster brake
  mirrored (fires on a +30% adverse price move against the short within an episode).
  Carry: -10%/yr pro-rated daily on short notional (primary); 0%/yr and -20%/yr as
  pre-registered sensitivity bounds. NOTHING is tuned; every parameter is frozen at
  the champion's values.

Order of operations (per pre-registration):
  [1] Zero-cost pre-gates (activity census, whipsaw census) — stop rules pre-declared.
  [2] Baseline replication (unmodified champion through the same harness).
  [3] Trial #98 standalone sleeve: full gate stack + calendar years + carry sensitivity.
  [4] Cross-asset transfer of the mirrored gate (9 assets, reporting).
  [5] Correlation + overlap analysis sleeve-vs-champion.
  [6] Combined portfolio (pre-registered construction) full gate stack + carry sens.
  [7] Extended-window BTC-only spot check ~2017->2026 (reporting only).
  [8] DSR table at n_trials=98 (champion baseline, sleeve, combined).
  [9] Promotion-criteria scorecard (all six pre-registered criteria).

Pipeline conventions identical to phase13/14/15: futures feathers, 70/15/15
chronological split, 4-window walk-forward on the second half, monthly-block Monte
Carlo (1,000 sims, seed 11), fees 0.15%/side, 2-bar lag, DSR from freqtrade_dsr.py.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from freqtrade_dsr import deflated_sharpe_ratio  # AGPL module, repo root — imported, not copied

FEE = 0.0015
FEE_STRESS = FEE + 0.001  # 2x-slippage stress convention (phase15)
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
SPOT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx')

VOL_TARGET = 0.40
LOOKBACK = 30
QUANT = 0.25
BRAKE = 0.30           # disaster brake, mirrored: adverse move against the short
CARRY_PRIMARY = 0.10   # -10%/yr carry charged on short notional (pre-registered primary)
N_TRIALS = 98
MC_SIMS = 1000
ANN = 365

SYMS2 = ['BTC', 'ETH']
SYMS9 = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'BNB']


# ---------------------------------------------------------------- data / indicators
def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()


def load_fut(sym: str) -> pd.DataFrame:
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})


def load_spot(sym: str) -> pd.DataFrame:
    df = pd.read_feather(SPOT_DIR / f'{sym}_USDT-1d.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})


def rv_cc(df: pd.DataFrame, lookback: int = LOOKBACK) -> pd.Series:
    """Champion's estimator: close-to-close rolling std, annualized. FROZEN."""
    return df['close'].pct_change().rolling(lookback).std() * np.sqrt(ANN)


def quantize(w):
    return ((w / QUANT).round() * QUANT).clip(0, 1)


def core_bull(df: pd.DataFrame) -> pd.Series:
    """Champion's 3-of-3 gate (unchanged)."""
    c = df['close']
    return ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)


def core_bear(df: pd.DataFrame) -> pd.Series:
    """Mirrored 3-of-3 gate (the sleeve's signal). All parameters frozen."""
    c = df['close']
    return ((c < _sma(c, 200)) & (c.pct_change(30) < 0) & (_ema(c, 20) < _ema(c, 50))).astype(float)


def basket_weights(dfs: dict, core_fn, syms: list) -> pd.DataFrame:
    """Quantized vol-target weight magnitudes, /len(syms) (per-pair cap 50% on 2-pair)."""
    idx = sorted(set().union(*[dfs[s].index for s in syms]))
    W = pd.DataFrame(index=pd.DatetimeIndex(idx))
    for s in syms:
        core = core_fn(dfs[s])
        rv = rv_cc(dfs[s])
        scale = (VOL_TARGET / rv).clip(0, 1)
        W[s] = quantize(core * scale).reindex(W.index) / len(syms)
    return W.fillna(0)


# ---------------------------------------------------------------- execution machinery
def positions_from_weights(W: pd.DataFrame, closes: pd.DataFrame) -> pd.DataFrame:
    """Signal close[t] -> exec open[t+1] -> held close[t+1]: pos = W.shift(2)."""
    return W.reindex(closes.index).fillna(0).shift(2).fillna(0)


def apply_short_brake(pos_mag: pd.Series, close: pd.Series, brake: float = BRAKE) -> pd.Series:
    """Mirrored -30% disaster brake for a SHORT position magnitude series.

    Within each contiguous held episode, entry reference = close of the bar before the
    first held bar (close-to-close convention). If close rises >= entry*(1+brake), the
    short is stopped: exposure is zeroed from the NEXT bar until the episode ends (the
    loss bar itself is realized — no lookahead). The gate must break and re-form to
    re-enter, matching the freqtrade stoploss-then-resignal behavior at daily scale.
    """
    pos = pos_mag.copy()
    vals = pos.values
    px = close.values
    in_ep = False
    entry = np.nan
    braked = False
    for i in range(len(vals)):
        if vals[i] > 0:
            if not in_ep:
                entry = px[i - 1] if i > 0 else px[i]
                braked = False
                in_ep = True
            if braked:
                vals[i] = 0.0
            elif px[i] >= entry * (1 + brake):
                braked = True  # this bar's loss is kept; flat from next bar
        else:
            in_ep = False
    return pd.Series(vals, index=pos.index)


def net_from_positions(pos: pd.DataFrame, closes: pd.DataFrame,
                       fee: float = FEE, carry_ann: float = 0.0) -> pd.Series:
    """Net daily returns from a signed position matrix.

    Negative positions are shorts. Turnover = sum |delta pos| (a long->short flip is
    2x turnover). Carry charged pro-rated daily on the SHORT notional only (funding
    proxy; longs on spot/perp carry is not charged, consistent with the champion
    baseline convention).
    """
    pos = pos.reindex(closes.index).fillna(0)
    ret_mat = closes.pct_change()
    gross = (pos * ret_mat.fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    short_notional = (-pos.clip(upper=0)).sum(axis=1)
    carry_cost = short_notional * (carry_ann / ANN)
    return (gross - turn * fee - carry_cost).dropna()


# ---------------------------------------------------------------- evaluation
def m(ret: pd.Series):
    """(sharpe, max_dd, cagr, total_return)"""
    ret = ret.dropna()
    if len(ret) < 10 or ret.std() == 0:
        return 0.0, 0.0, 0.0, 0.0
    eq = (1 + ret).cumprod()
    yrs = len(ret) / ANN
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1
    sh = ret.mean() / ret.std() * np.sqrt(ANN)
    dd = float((eq / eq.cummax() - 1).min())
    return float(sh), dd, float(cagr), float(eq.iloc[-1] - 1)


@dataclass
class ValResult:
    label: str
    full_sharpe: float; full_dd: float; full_cagr: float; full_ret: float
    train_sh: float; val_sh: float; test_sh: float
    test_dd: float; test_cagr: float
    wf_sharpes: list; wf_rets: list; wf_pos: int
    mc_med_dd: float; mc_p_dd25: float
    stress_full_sh: float; stress_test_sh: float


def full_validation(ret: pd.Series, label: str, ret_stress: pd.Series) -> ValResult:
    """full + 70/15/15 + 4-window WF + 1000-sim monthly-block MC + slippage stress."""
    ret = ret.dropna()
    n = len(ret)
    i1, i2 = int(n * 0.70), int(n * 0.85)
    sh_f, dd_f, cg_f, tr_f = m(ret)
    sh_tr, _, _, _ = m(ret.iloc[:i1])
    sh_vl, _, _, _ = m(ret.iloc[i1:i2])
    sh_te, dd_te, cg_te, _ = m(ret.iloc[i2:])
    wf_sh, wf_rt = [], []
    for k in range(4):
        s_i, e_i = int(n * (0.5 + k * 0.125)), min(int(n * (0.5 + (k + 1) * 0.125)), n)
        w = m(ret.iloc[s_i:e_i])
        wf_sh.append(w[0]); wf_rt.append(w[3])
    blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
    rng = np.random.default_rng(11)
    dds = []
    for _ in range(MC_SIMS):
        seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        eq = np.cumprod(1 + seq)
        dds.append((eq / np.maximum.accumulate(eq) - 1).min())
    p_dd25 = float((np.array(dds) < -0.25).mean())
    st_f, _, _, _ = m(ret_stress)
    st_te, _, _, _ = m(ret_stress.iloc[int(len(ret_stress) * 0.85):])
    r = ValResult(label, sh_f, dd_f, cg_f, tr_f, sh_tr, sh_vl, sh_te, dd_te, cg_te,
                  wf_sh, wf_rt, sum(1 for x in wf_rt if x > 0),
                  float(np.percentile(dds, 50)), p_dd25, st_f, st_te)
    print(f"\n{label}")
    print(f"  FULL  Sharpe {sh_f:5.2f}  DD {dd_f*100:6.1f}%  CAGR {cg_f*100:+6.1f}%  total {tr_f*100:+.0f}%")
    print(f"  TRAIN {sh_tr:5.2f} | VAL {sh_vl:5.2f} | TEST {sh_te:5.2f}  "
          f"(TEST CAGR {cg_te*100:+5.1f}%, DD {dd_te*100:5.1f}%)")
    print(f"  WF Sharpe: " + " ".join(f"{x:+.2f}" for x in wf_sh)
          + "   WF ret: " + " ".join(f"{x*100:+.1f}%" for x in wf_rt)
          + f"   pos {r.wf_pos}/4")
    print(f"  MC({MC_SIMS}) medDD {r.mc_med_dd*100:.1f}%  P(DD<-25%) {p_dd25*100:.1f}%"
          f"   | stress(2x slip) FULL Sh {st_f:.2f} TEST Sh {st_te:.2f}")
    return r


def calendar_years(ret: pd.Series) -> dict:
    out = {}
    for y, g in ret.groupby(ret.index.year):
        out[int(y)] = float((1 + g).prod() - 1)
    return out


def episodes(w: pd.Series) -> list:
    """Contiguous runs of w>0 -> list of (start_idx, end_idx) integer positions."""
    active = (w > 0).values
    eps = []
    start = None
    for i, a in enumerate(active):
        if a and start is None:
            start = i
        elif not a and start is not None:
            eps.append((start, i - 1)); start = None
    if start is not None:
        eps.append((start, len(active) - 1))
    return eps


# =================================================================
print('=' * 78)
print('PHASE 16 — H-BearShort: mirrored trend gate as a short sleeve (trial #98)')
print('  pre-registered in SESSION_2026-07-10_BEARSHORT.md before any results')
print('=' * 78)

print('\n[0] Loading data')
dfs = {s: load_fut(s) for s in SYMS9}
closes2 = pd.DataFrame({s: dfs[s]['close'] for s in SYMS2}).sort_index()
for s in SYMS2:
    print(f"  {s} futures 1d: {dfs[s].index[0].date()} -> {dfs[s].index[-1].date()}  ({len(dfs[s])} bars)")
spot_btc = load_spot('BTC')
print(f"  BTC spot 1d (extended window): {spot_btc.index[0].date()} -> {spot_btc.index[-1].date()}  ({len(spot_btc)} bars)")

# Weight matrices (magnitudes)
W_bull = basket_weights(dfs, core_bull, SYMS2)   # champion
W_bear = basket_weights(dfs, core_bear, SYMS2)   # mirrored sleeve

# ---------------------------------------------------------------- [1] pre-gates
print('\n[1] PRE-GATE 1 — activity census (mirrored gate, BTC+ETH futures window)')
n_idx = len(W_bear)
i_test = int(n_idx * 0.85)  # last 15% of the harness calendar index
total_eps = 0
inmkt_full = ((W_bear > 0).any(axis=1)).sum()
inmkt_test = ((W_bear.iloc[i_test:] > 0).any(axis=1)).sum()
per_pair_eps = {}
for s in SYMS2:
    eps = episodes(W_bear[s])
    per_pair_eps[s] = eps
    total_eps += len(eps)
    gate_days = int((W_bear[s] > 0).sum())
    print(f"  {s}: {len(eps)} round trips, {gate_days} in-market (weight>0) days")
print(f"  TOTAL round trips (both pairs): {total_eps}   basket in-market days full-window: {inmkt_full}")
print(f"  TEST-split (last 15% of index, from {W_bear.index[i_test].date()}): basket in-market days: {inmkt_test}")
gate1_ok = (total_eps >= 15) and (inmkt_test >= 20)
print(f"  PRE-GATE 1: {'PASS' if gate1_ok else 'FAIL -> STOP, verdict UNTESTABLE, zero trials spent'}"
      f"  (need >=15 round trips full-window AND >=20 in-market days in TEST)")

print('\n[1b] PRE-GATE 2 — whipsaw census (episode lengths + per-episode gross short returns)')
all_lens, all_gross = [], []
for s in SYMS2:
    c = dfs[s]['close'].reindex(W_bear.index)
    for (a, b) in per_pair_eps[s]:
        length = b - a + 1
        # exec lag: entry ref = close[a+1], exit ref = close[min(b+1, end)]
        ei = min(a + 1, len(c) - 1)
        xi = min(b + 1, len(c) - 1)
        if pd.notna(c.iloc[ei]) and pd.notna(c.iloc[xi]) and c.iloc[ei] > 0:
            all_gross.append(1 - c.iloc[xi] / c.iloc[ei])  # short gross return
        all_lens.append(length)
lens = np.array(all_lens); gross = np.array(all_gross)
print(f"  episodes n={len(lens)}  length bars: median {np.median(lens):.0f}  "
      f"q25 {np.percentile(lens,25):.0f}  q75 {np.percentile(lens,75):.0f}  max {lens.max()}")
print(f"  per-episode gross short return: median {np.median(gross)*100:+.1f}%  "
      f"mean {np.mean(gross)*100:+.1f}%  positive {np.mean(gross>0)*100:.0f}%  "
      f"best {gross.max()*100:+.1f}%  worst {gross.min()*100:+.1f}%")
gate2_ok = np.median(lens) > 3
print(f"  PRE-GATE 2: {'PASS' if gate2_ok else 'FAIL -> STOP (gate is structurally a whipsaw detector)'}"
      f"  (need median episode length > 3 bars)")

if not (gate1_ok and gate2_ok):
    sys.exit('\nPRE-GATE FAILURE — stopping before the trial. Zero n_trials spent (stays 97).')

# ---------------------------------------------------------------- [2] baseline replication
print('\n[2] Baseline replication check (unmodified champion, identical harness)')
pos_bull = positions_from_weights(W_bull, closes2)
ret_base = net_from_positions(pos_bull, closes2)
ret_base_st = net_from_positions(pos_bull, closes2, fee=FEE_STRESS)
res_base = full_validation(ret_base, 'BASELINE: champion TVT BTC+ETH long (cc30)', ret_base_st)
ok = 0.35 <= res_base.test_sh <= 0.45 and 1.0 <= res_base.full_sharpe <= 1.4 \
    and 0.25 <= res_base.mc_p_dd25 <= 0.40
print(f"\n  Replication: TEST Sharpe {res_base.test_sh:.2f} (require ~0.39-0.41), "
      f"FULL {res_base.full_sharpe:.2f}, MC tail {res_base.mc_p_dd25*100:.1f}% (require ~28-38%)"
      f" -> {'OK' if ok else 'MISMATCH — STOP'}")
if not ok:
    sys.exit('Baseline replication failed; aborting before the sleeve trial.')

# ---------------------------------------------------------------- [3] trial #98 sleeve
print('\n[3] TRIAL #98 — standalone short sleeve (mirrored gate, mirrored brake)')
pos_bear_mag = positions_from_weights(W_bear, closes2)
for s in SYMS2:
    pos_bear_mag[s] = apply_short_brake(pos_bear_mag[s], closes2[s])
pos_sleeve = -pos_bear_mag
raw_mag = positions_from_weights(W_bear, closes2)
braked_days = int(((raw_mag > 0) & (pos_bear_mag == 0)).sum().sum())
print(f"  disaster brake (-30% adverse, mirrored): {braked_days} pair-days zeroed by the brake")

ret_sleeve = {}
for carry, tag in [(CARRY_PRIMARY, '-10%/yr'), (0.0, '0%/yr'), (0.20, '-20%/yr')]:
    ret_sleeve[tag] = net_from_positions(pos_sleeve, closes2, carry_ann=carry)
ret_sl = ret_sleeve['-10%/yr']  # primary
ret_sl_st = net_from_positions(pos_sleeve, closes2, fee=FEE_STRESS, carry_ann=CARRY_PRIMARY)
res_sleeve = full_validation(ret_sl, 'TRIAL #98: BearShort sleeve @ -10%/yr carry (PRIMARY)', ret_sl_st)

print('\n  Carry sensitivity (same position stream, re-priced):')
for tag in ['0%/yr', '-10%/yr', '-20%/yr']:
    sh, dd, cg, tr = m(ret_sleeve[tag])
    sh_te = m(ret_sleeve[tag].iloc[int(len(ret_sleeve[tag]) * 0.85):])[0]
    print(f"    carry {tag:>8}: FULL Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  CAGR {cg*100:+6.1f}%  "
          f"total {tr*100:+6.1f}%  TEST Sh {sh_te:5.2f}")

print('\n  Calendar years (sleeve @ -10%/yr carry vs champion baseline):')
cy_sl = calendar_years(ret_sl)
cy_base = calendar_years(ret_base)
for y in sorted(set(cy_sl) | set(cy_base)):
    print(f"    {y}: sleeve {cy_sl.get(y, 0)*100:+7.1f}%   champion {cy_base.get(y, 0)*100:+7.1f}%")

rt_count = total_eps
print(f"\n  Round trips (gate episodes, both pairs): {rt_count}   "
      f"in-market days (held, either pair): {int((pos_bear_mag.sum(axis=1) > 0).sum())}")

# ---------------------------------------------------------------- [4] cross-asset transfer
print('\n[4] Cross-asset transfer — mirrored gate, single-asset sleeves, unchanged params, -10%/yr carry')
x_sh = []
for s in SYMS9:
    core = core_bear(dfs[s])
    rv = rv_cc(dfs[s])
    w = quantize(core * (VOL_TARGET / rv).clip(0, 1)).to_frame(s)
    cl = dfs[s][['close']].rename(columns={'close': s})
    pm = positions_from_weights(w, cl)
    pm[s] = apply_short_brake(pm[s], cl[s])
    r = net_from_positions(-pm, cl, carry_ann=CARRY_PRIMARY)
    x_sh.append(m(r)[0])
pos_n = sum(1 for x in x_sh if x >= 0)
print(f"  non-negative {pos_n}/9  median {np.median(x_sh):.2f}  " +
      " ".join(f"{s}:{x:+.2f}" for s, x in zip(SYMS9, x_sh)))
print(f"  (soft expectation >=6/9 non-negative — reporting only, not a promotion criterion)")

# ---------------------------------------------------------------- [5] correlation / overlap
print('\n[5] Correlation & overlap analysis (sleeve @ -10% vs champion baseline)')
ix = ret_sl.index.intersection(ret_base.index)
corr_full = float(ret_sl[ix].corr(ret_base[ix]))
n_i = len(ix); i_te = int(n_i * 0.85)
te_ix = ix[i_te:]
corr_test = float(ret_sl[te_ix].corr(ret_base[te_ix]))
both_active = ((pos_bull.reindex(ix).sum(axis=1) > 0) & (pos_bear_mag.reindex(ix).sum(axis=1) > 0))
print(f"  daily-return correlation: FULL {corr_full:+.3f}   TEST {corr_test:+.3f}   (bar: < 0.4)")
print(f"  overlap census: days champion long AND sleeve short simultaneously (cross-pair): "
      f"{int(both_active.sum())} of {n_i}")

# ---------------------------------------------------------------- [6] combined portfolio
print('\n[6] COMBINED PORTFOLIO (pre-registered: champion long pos minus braked sleeve pos)')
pos_comb = (pos_bull - pos_bear_mag).clip(-0.5, 0.5)  # per-pair net cap +/-50%
ret_comb = {}
for carry, tag in [(CARRY_PRIMARY, '-10%/yr'), (0.0, '0%/yr'), (0.20, '-20%/yr')]:
    ret_comb[tag] = net_from_positions(pos_comb, closes2, carry_ann=carry)
ret_cb = ret_comb['-10%/yr']
ret_cb_st = net_from_positions(pos_comb, closes2, fee=FEE_STRESS, carry_ann=CARRY_PRIMARY)
res_comb = full_validation(ret_cb, 'COMBINED: champion + BearShort sleeve @ -10%/yr carry (PRIMARY)', ret_cb_st)

print('\n  Combined carry sensitivity:')
for tag in ['0%/yr', '-10%/yr', '-20%/yr']:
    sh, dd, cg, tr = m(ret_comb[tag])
    sh_te = m(ret_comb[tag].iloc[int(len(ret_comb[tag]) * 0.85):])[0]
    print(f"    carry {tag:>8}: FULL Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  CAGR {cg*100:+6.1f}%  TEST Sh {sh_te:5.2f}")

print('\n  Calendar years (combined @ -10% vs champion):')
cy_cb = calendar_years(ret_cb)
for y in sorted(set(cy_cb) | set(cy_base)):
    print(f"    {y}: combined {cy_cb.get(y, 0)*100:+7.1f}%   champion {cy_base.get(y, 0)*100:+7.1f}%")

# ---------------------------------------------------------------- [7] extended spot window
print('\n[7] Extended-window check — BTC-only sleeve on spot (~2017->, incl. 2018 bear), '
      'spot as perp proxy, -10%/yr carry, REPORTING ONLY')
core_x = core_bear(spot_btc)
rv_x = rv_cc(spot_btc)
w_x = quantize(core_x * (VOL_TARGET / rv_x).clip(0, 1)).to_frame('BTC')
cl_x = spot_btc[['close']].rename(columns={'close': 'BTC'})
pm_x = positions_from_weights(w_x, cl_x)
pm_x['BTC'] = apply_short_brake(pm_x['BTC'], cl_x['BTC'])
ret_x = net_from_positions(-pm_x, cl_x, carry_ann=CARRY_PRIMARY)
sh, dd, cg, tr = m(ret_x)
print(f"  FULL ({ret_x.index[0].date()} -> {ret_x.index[-1].date()}): "
      f"Sharpe {sh:.2f}  DD {dd*100:.1f}%  CAGR {cg*100:+.1f}%  total {tr*100:+.1f}%")
print('  calendar years:')
for y, v in calendar_years(ret_x).items():
    print(f"    {y}: {v*100:+7.1f}%")

# ---------------------------------------------------------------- [8] DSR
print(f'\n[8] Deflated Sharpe Ratio (daily returns, n_trials={N_TRIALS})')
dsr_out = {}
for tag, r in [('champion baseline', ret_base), ('sleeve @ -10%', ret_sl), ('combined @ -10%', ret_cb)]:
    res = deflated_sharpe_ratio(r.tolist(), n_trials=N_TRIALS)
    dsr_out[tag] = res['dsr']
    print(f"  {tag:<20} DSR={res['dsr']:.4f}  (skew {res['skew']:+.2f}, "
          f"kurt {res['kurtosis']:.1f}, n_obs {res['n_obs']})")

# ---------------------------------------------------------------- [9] scorecard
print('\n[9] Promotion-criteria scorecard (ALL must hold; judged at -10%/yr carry)')
cy_worst = min(cy_sl.values())
c1 = (res_comb.full_sharpe >= res_base.full_sharpe) and (res_comb.mc_p_dd25 <= res_base.mc_p_dd25)
c2 = (res_sleeve.full_sharpe >= 0.5 and res_sleeve.test_sh > 0.20
      and cy_sl.get(2022, 0) > 0 and cy_worst >= -0.15 and rt_count >= 15)
c3 = (corr_full < 0.4) and (corr_test < 0.4)
flip = any(bb > 0 and vv < -0.05 for bb, vv in zip(res_base.wf_rets, res_comb.wf_rets))
c4 = (res_comb.wf_pos >= 3) and not flip
c5 = dsr_out['combined @ -10%'] >= dsr_out['champion baseline']
sh20, _, _, tr20 = m(ret_sleeve['-20%/yr'])
sh20_te = m(ret_sleeve['-20%/yr'].iloc[int(len(ret_sleeve['-20%/yr']) * 0.85):])[0]
sh20c = m(ret_comb['-20%/yr'])[0]
# criterion 6: criteria 1-2 must hold DIRECTIONALLY at -20%/yr (small degradation allowed);
# a sign flip of the sleeve's full-window return is a hard FAIL.
c6 = (tr20 > 0) and (sh20 >= 0.40) and (sh20_te > 0.15) and (sh20c >= res_base.full_sharpe - 0.05)
print(f"  1 PRIMARY combined Sharpe >= baseline AND MC tail <= baseline: {'PASS' if c1 else 'FAIL'}"
      f"  (Sh {res_comb.full_sharpe:.2f} vs {res_base.full_sharpe:.2f}; "
      f"tail {res_comb.mc_p_dd25*100:.1f}% vs {res_base.mc_p_dd25*100:.1f}%)")
print(f"  2 sleeve standalone: FULL Sh>=0.5 ({res_sleeve.full_sharpe:.2f}), TEST>0.20 ({res_sleeve.test_sh:.2f}), "
      f"2022>0 ({cy_sl.get(2022, 0)*100:+.1f}%), worst yr>=-15% ({cy_worst*100:+.1f}%), "
      f">=15 RTs ({rt_count}): {'PASS' if c2 else 'FAIL'}")
print(f"  3 correlation < 0.4 (full {corr_full:+.3f}, test {corr_test:+.3f}): {'PASS' if c3 else 'FAIL'}")
print(f"  4 combined WF >=3/4 pos ({res_comb.wf_pos}/4), no champion-positive window flipping < -5% "
      f"(flip={flip}): {'PASS' if c4 else 'FAIL'}")
print(f"  5 combined DSR >= champion DSR at n_trials=98 "
      f"({dsr_out['combined @ -10%']:.4f} vs {dsr_out['champion baseline']:.4f}): {'PASS' if c5 else 'FAIL'}")
print(f"  6 carry robustness at -20%/yr: sleeve total {tr20*100:+.1f}% (sign flip=FAIL), "
      f"sleeve Sh {sh20:.2f}, combined Sh {sh20c:.2f}: {'PASS' if c6 else 'FAIL'}")
verdict = all([c1, c2, c3, c4, c5, c6])
print(f"\n  VERDICT: {'ALL PASS — sleeve earns portfolio slot 2' if verdict else 'REJECT — sleeve does not earn a portfolio slot'}")
