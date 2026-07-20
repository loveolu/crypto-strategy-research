"""
Phase 20: H-TailAlloc — portfolio-level allocation between champion (TVT BTC+ETH)
and defensive variant (TVT 9-asset + 25% portfolio-vol overlay).

PRE-REGISTERED experiment (would-have-been trial #98). Spec locked in
SESSION_2026-07-11_TAILALLOC.md section 1 BEFORE this script produced any numbers.

Structure (exits at whichever gate fails; pre-gates cost ZERO n_trials):
  Pre-gate A: replicate BOTH endpoint daily return streams vs recorded bands.
  Pre-gate B: frontier census over w in {0..1 step 0.1}; formula-select w*.
  Trial #98: ONLY if both pre-gates pass — full validation stack on w* portfolio.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')

from pathlib import Path

import numpy as np
import pandas as pd

from freqtrade_dsr import deflated_sharpe_ratio
from validator import wf_window_stability, family_from_results_dir, family_context

FEE = 0.0015
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
ANN = 365
MC_SIMS = 1000
MC_SEED = 11
N_TRIALS = 98
VOL_TARGET = 0.40
LOOKBACK = 30
QUANT = 0.25
PORT_VOL = 0.25

CHAMP_SYMS = ['BTC', 'ETH']
DEF_SYMS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'BNB']
W_GRID = [round(x, 1) for x in np.arange(0.0, 1.01, 0.1)]


def _sma(s, n):
    return s.rolling(n).mean()


def _ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def load_fut(sym: str) -> pd.DataFrame:
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})


def core_series(close: pd.Series) -> pd.Series:
    return (
        (close > _sma(close, 200))
        & (close.pct_change(30) > 0)
        & (_ema(close, 20) > _ema(close, 50))
    ).astype(float)


def scale_series(close: pd.Series) -> pd.Series:
    rv = close.pct_change().rolling(LOOKBACK).std() * np.sqrt(ANN)
    return (VOL_TARGET / rv).clip(0, 1)


def quantize_scale(raw: pd.Series) -> pd.Series:
    return ((raw / QUANT).round() * QUANT).clip(0, 1)


def net_from_weights(W: pd.DataFrame, closes: pd.DataFrame) -> pd.Series:
    """Standard harness: 2-bar lag, fee on |Δposition|."""
    pos = W.reindex(closes.index).fillna(0).shift(2).fillna(0)
    gross = (pos * closes.pct_change().fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    return (gross - turn * FEE).dropna()


def champion_stream(closes: pd.DataFrame) -> pd.Series:
    W = pd.DataFrame(index=closes.index)
    for s in CHAMP_SYMS:
        raw = core_series(closes[s]) * scale_series(closes[s])
        W[s] = quantize_scale(raw.fillna(0)) / len(CHAMP_SYMS)
    return net_from_weights(W, closes)


def defensive_weights(closes: pd.DataFrame) -> pd.DataFrame:
    """9-asset equal weight (divisor 9, zero-weight pre-listing) + 25% port-vol overlay."""
    core_mat = pd.DataFrame(index=closes.index)
    scale_mat = pd.DataFrame(index=closes.index)
    for s in DEF_SYMS:
        c = closes[s]
        core_mat[s] = core_series(c).fillna(0)
        scale_mat[s] = scale_series(c).fillna(0)
    q = ((core_mat * scale_mat) / QUANT).round() * QUANT
    W = q.clip(0, 1) / len(DEF_SYMS)
    # portfolio-vol overlay (phase8/9 convention)
    ret_mat = closes.pct_change().fillna(0)
    pos0 = W.shift(2).fillna(0)
    r0 = (pos0 * ret_mat).sum(axis=1)
    pvol = r0.rolling(LOOKBACK).std() * np.sqrt(ANN)
    pscale = ((PORT_VOL / pvol).clip(0, 1.0) / QUANT).round() * QUANT
    return W.mul(pscale, axis=0)


def defensive_stream(closes: pd.DataFrame) -> pd.Series:
    return net_from_weights(defensive_weights(closes), closes)


def m(ret: pd.Series) -> tuple[float, float, float, float]:
    ret = ret.dropna()
    if len(ret) < 10 or ret.std() == 0:
        return 0.0, 0.0, 0.0, 0.0
    eq = (1 + ret).cumprod()
    yrs = len(ret) / ANN
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1
    sh = ret.mean() / ret.std() * np.sqrt(ANN)
    dd = float((eq / eq.cummax() - 1).min())
    return float(sh), dd, float(cagr), float(eq.iloc[-1] - 1)


def mc_tail(ret: pd.Series, sims: int = MC_SIMS, seed: int = MC_SEED) -> tuple[float, float]:
    blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
    rng = np.random.default_rng(seed)
    dds = []
    for _ in range(sims):
        seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        eq = np.cumprod(1 + seq)
        dds.append((eq / np.maximum.accumulate(eq) - 1).min())
    dds = np.array(dds)
    return float((dds < -0.25).mean()), float(np.percentile(dds, 50))


def report(label: str, ret: pd.Series) -> dict:
    n = len(ret)
    sh_f, dd_f, cg_f, _ = m(ret)
    sh_te, dd_te, cg_te, _ = m(ret.iloc[int(n * 0.85):])
    p25, med = mc_tail(ret)
    print(f"  {label:<28} FULL Sh {sh_f:5.2f}  DD {dd_f*100:6.1f}%  CAGR {cg_f*100:+6.1f}%  "
          f"| TEST Sh {sh_te:5.2f}  | MC tail {p25*100:5.1f}%  medDD {med*100:6.1f}%")
    return {'full_sh': sh_f, 'full_dd': dd_f, 'full_cagr': cg_f,
            'test_sh': sh_te, 'test_dd': dd_te, 'test_cagr': cg_te,
            'mc_p25': p25, 'mc_med': med}


def blend_daily(r_c: pd.Series, r_d: pd.Series, w: float) -> pd.Series:
    idx = r_c.index.intersection(r_d.index)
    return w * r_c.reindex(idx) + (1 - w) * r_d.reindex(idx)


def blend_monthly(r_c: pd.Series, r_d: pd.Series, w: float) -> pd.Series:
    """Fixed slices compounded separately; rebalance to (w, 1-w) at each month-end."""
    idx = r_c.index.intersection(r_d.index)
    rc, rd = r_c.reindex(idx).fillna(0), r_d.reindex(idx).fillna(0)
    v_c, v_d = float(w), float(1 - w)
    out = []
    month_ends = set(rc.groupby([rc.index.year, rc.index.month]).apply(lambda g: g.index[-1]))
    for i, dt in enumerate(rc.index):
        total_before = v_c + v_d
        v_c *= (1 + rc.iloc[i])
        v_d *= (1 + rd.iloc[i])
        total_after = v_c + v_d
        r_day = total_after / total_before - 1 if total_before > 0 else 0.0
        if dt in month_ends and i > 0 and total_after > 0:
            w_act = v_c / total_after
            turn = abs(w_act - w) * 2.0
            r_day -= turn * FEE
            total_after *= (1 - turn * FEE)
            v_c = w * total_after
            v_d = (1 - w) * total_after
        out.append(r_day)
    return pd.Series(out, index=rc.index)


def corr_report(r_c: pd.Series, r_d: pd.Series, exp_c: pd.Series, exp_d: pd.Series) -> None:
    idx = r_c.index.intersection(r_d.index)
    rc, rd = r_c.reindex(idx), r_d.reindex(idx)
    n = len(rc)
    i2 = int(n * 0.85)
    te_c, te_d = rc.iloc[i2:], rd.iloc[i2:]
    in_mkt = (exp_c.reindex(idx).shift(2).fillna(0) + exp_d.reindex(idx).shift(2).fillna(0)) > 0
    print("\n  Return correlation (Pearson):")
    print(f"    full window:           {rc.corr(rd):+.3f}")
    print(f"    TEST split:            {te_c.corr(te_d):+.3f}")
    print(f"    in-market days only:   {rc[in_mkt].corr(rd[in_mkt]):+.3f}")
    te_mkt = in_mkt.iloc[i2:]
    print(f"    TEST in-market only:   {te_c[te_mkt].corr(te_d[te_mkt]):+.3f}")


def exposure_series(W: pd.DataFrame) -> pd.Series:
    return W.shift(2).fillna(0).abs().sum(axis=1)


# =================================================================
print('=' * 78)
print('PHASE 20 - H-TailAlloc: champion/defensive portfolio allocation (pre-gated)')
print('=' * 78)

print('\n[1] Loading data - master calendar = BTC futures 1d (2020-01 to 2026-05)')
btc = load_fut('BTC')
master_idx = btc.index
closes_champ = pd.DataFrame({s: load_fut(s)['close'].reindex(master_idx) for s in CHAMP_SYMS})
closes_def = pd.DataFrame({s: load_fut(s)['close'].reindex(master_idx) for s in DEF_SYMS})

print('  Pre-listing rule: zero-weight, divisor=9 (locked pre-registration)')
for s in DEF_SYMS:
    first = closes_def[s].first_valid_index()
    print(f'    {s}: data from {first.date() if first else "N/A"}')

# ---------------------------------------------------------------- pre-gate A
print('\n[2] PRE-GATE A - endpoint stream replication (zero n_trials)')

r_champ = champion_stream(closes_champ)
W_def = defensive_weights(closes_def)
r_def = net_from_weights(W_def, closes_def)
res_ch = report('CHAMPION BTC+ETH', r_champ)
res_def = report('DEFENSIVE 9-asset+portvol', r_def)

ok_ch = (1.0 <= res_ch['full_sh'] <= 1.4
         and 0.30 <= res_ch['test_sh'] <= 0.50
         and 0.20 <= res_ch['mc_p25'] <= 0.45)
ok_def = (0.10 <= res_def['full_cagr'] <= 0.18
          and 0.9 <= res_def['full_sh'] <= 1.3
          and -0.17 <= res_def['full_dd'] <= -0.10
          and 0.13 <= res_def['test_sh'] <= 0.33
          and res_def['mc_p25'] <= 0.05)

print(f"\n  Champion gate:  FULL {res_ch['full_sh']:.2f} TEST {res_ch['test_sh']:.2f} "
      f"MC {res_ch['mc_p25']*100:.1f}% -> {'OK' if ok_ch else 'MISMATCH - STOP'}")
print(f"  Defensive gate: CAGR {res_def['full_cagr']*100:.1f}% Sh {res_def['full_sh']:.2f} "
      f"DD {res_def['full_dd']*100:.1f}% TEST {res_def['test_sh']:.2f} "
      f"MC {res_def['mc_p25']*100:.1f}% -> {'OK' if ok_def else 'MISMATCH - STOP'}")

if not (ok_ch and ok_def):
    print('\n  STOP RULE: endpoint replication failed - data-integrity finding.')
    print('  Zero trials spent; n_trials remains 97.')
    sys.exit(1)

# ---------------------------------------------------------------- pre-gate B
print('\n[3] PRE-GATE B - frontier census (zero n_trials)')

exp_c = exposure_series(
    pd.DataFrame({s: quantize_scale(core_series(closes_champ[s]) * scale_series(closes_champ[s]).fillna(0)) / 2
                  for s in CHAMP_SYMS}, index=master_idx))
exp_d = exposure_series(W_def)
corr_report(r_champ, r_def, exp_c, exp_d)

print('\n  Frontier on monthly-rebalanced fixed slices (stream ii); daily blend (i) at w=0.5 only:')
rows = {}
for w in W_GRID:
    r_m = blend_monthly(r_champ, r_def, w)
    rows[w] = report(f'w={w:.1f} monthly', r_m)
    if abs(w - 0.5) < 0.01:
        r_d = blend_daily(r_champ, r_def, w)
        report(f'w=0.5 daily (ref)', r_d)

candidates = [w for w in W_GRID if rows[w]['mc_p25'] <= 0.20]
w_star = max(candidates) if candidates else None

print('\n  Candidate selection: w* = LARGEST w with MC tail <= 20%')
if w_star is not None:
    print(f"  w* = {w_star:.1f}  (MC tail {rows[w_star]['mc_p25']*100:.1f}%, "
          f"TEST Sh {rows[w_star]['test_sh']:.2f}, CAGR {rows[w_star]['full_cagr']*100:+.1f}%)")
else:
    print('  w* = NONE (no w clears tail bar)')

gate_b = False
if w_star is not None:
    c1 = w_star >= 0.5
    c2 = rows[w_star]['test_sh'] >= res_ch['test_sh'] - 0.05
    c3 = rows[w_star]['full_cagr'] >= res_def['full_cagr'] + 0.02
    gate_b = c1 and c2 and c3
    print(f"\n  Pre-gate B conditions:")
    print(f"    w* >= 0.5:                    {'PASS' if c1 else 'FAIL'} ({w_star:.1f})")
    print(f"    TEST Sh >= champ - 0.05:      {'PASS' if c2 else 'FAIL'} "
          f"({rows[w_star]['test_sh']:.2f} vs {res_ch['test_sh']:.2f})")
    print(f"    CAGR >= def + 2pp:            {'PASS' if c3 else 'FAIL'} "
          f"({rows[w_star]['full_cagr']*100:.1f}% vs {res_def['full_cagr']*100:.1f}%+2)")
    print(f"\n  PRE-GATE B: {'PASS' if gate_b else 'FAIL'}")
else:
    print('\n  PRE-GATE B: FAIL (no interior tail fix)')

if not gate_b:
    print('\n  STOP RULE: portfolio-tail direction CLOSED.')
    print('  Zero trials spent; n_trials remains 97.')
    sys.exit(0)

# ---------------------------------------------------------------- trial #98
print(f'\n[4] TRIAL #98 - w*={w_star:.1f} monthly-rebalanced portfolio, full stack')

ret_trial = blend_monthly(r_champ, r_def, w_star)
res_trial = report(f'TRIAL w*={w_star:.1f}', ret_trial)
n = len(ret_trial)
i1, i2 = int(n * 0.70), int(n * 0.85)
sh_tr, _, _, _ = m(ret_trial.iloc[:i1])
sh_vl, _, _, _ = m(ret_trial.iloc[i1:i2])
print(f"  TRAIN {sh_tr:.2f} | VAL {sh_vl:.2f} | TEST {res_trial['test_sh']:.2f}")

print('\n[4a] Walk-forward window stability')
wf_t = wf_window_stability(ret_trial)
wf_c = wf_window_stability(r_champ)
maj = sum(int(wf_t[k]['majority_positive']) for k in (3, 4, 5, 6))
for k in (3, 4, 5, 6):
    t, c = wf_t[k], wf_c[k]
    print(f"  {k} windows: trial {t['windows_positive']}/{k} pos "
          f"(maj {'Y' if t['majority_positive'] else 'N'}) | champ {c['windows_positive']}/{k}")
print(f"  Majority-positive configs: {maj}/4 (bar >= 3)")

print(f'\n[4b] DSR at n_trials={N_TRIALS}')
dsr_t = deflated_sharpe_ratio(ret_trial.tolist(), n_trials=N_TRIALS)
dsr_c = deflated_sharpe_ratio(r_champ.tolist(), n_trials=N_TRIALS)
print(f"  trial w*={w_star}: DSR={dsr_t['dsr']:.4f}")
print(f"  champion @98:      DSR={dsr_c['dsr']:.4f}  (recorded @97: 0.626)")

print('\n[4c] Family context')
fam = family_from_results_dir()
ctx = family_context(f'tailalloc_w{w_star}', res_trial['full_sh'], res_trial['test_sh'], fam)
ts = ctx['test_sharpe']
print(f"  TEST Sharpe family: mean {ts.get('mean')} / candidate {ts.get('candidate')} "
      f"(rank {ts.get('candidate_rank')}, pctile {ts.get('candidate_percentile')})")

print('\n[4d] Look-ahead audit - rebalance uses completed month-end only')
la_ok = True
max_prefix_diff = 0.0
for cut in (int(n * 0.6), int(n * 0.8), n - 30):
    idx_cut = ret_trial.index[cut]
    sub = ret_trial.loc[:idx_cut]
    full_pref = blend_monthly(r_champ.loc[:idx_cut], r_def.loc[:idx_cut], w_star)
    diff = (sub - full_pref).abs().max()
    max_prefix_diff = max(max_prefix_diff, float(diff))
    ok = diff < 1e-4
    la_ok &= ok
    print(f"  cut {idx_cut.date()}: max |diff| = {diff:.2e} {'OK' if ok else 'VIOLATION'}")
print('  Structural: rebalance fires only on completed month-end dates (causal by construction)')
print(f'  Max prefix stability diff across cuts: {max_prefix_diff:.2e}')

print('\n[4e] Per-year fee accounting (monthly rebal vs champion standalone)')
# approximate: count month-end rebalance fees
for yr in sorted(set(ret_trial.index.year)):
    sub = ret_trial[ret_trial.index.year == yr]
    ch_yr = r_champ[r_champ.index.year == yr]
    print(f"  {yr}: trial return {(1+sub).prod()-1:+.1%}  champ {(1+ch_yr).prod()-1:+.1%}")

print('\n[5] Validation scorecard (ALL must hold)')
c1 = res_trial['mc_p25'] <= 0.20
c2 = (res_trial['test_sh'] >= res_ch['test_sh'] - 0.05
      and res_trial['full_sh'] >= res_ch['full_sh'] - 0.05)
c3 = maj >= 3
c4 = dsr_t['dsr'] >= dsr_c['dsr']
c5 = res_trial['full_cagr'] >= res_def['full_cagr'] + 0.02
c6 = la_ok
print(f"  1 MC tail <= 20%:                 {'PASS' if c1 else 'FAIL'} ({res_trial['mc_p25']*100:.1f}%)")
print(f"  2 TEST & FULL Sh >= champ - 0.05: {'PASS' if c2 else 'FAIL'}")
print(f"  3 WF majority-pos >= 3/4:         {'PASS' if c3 else 'FAIL'} ({maj}/4)")
print(f"  4 DSR@98 >= champ@98:             {'PASS' if c4 else 'FAIL'} ({dsr_t['dsr']:.4f} vs {dsr_c['dsr']:.4f})")
print(f"  5 CAGR >= def + 2pp:              {'PASS' if c5 else 'FAIL'}")
print(f"  6 No look-ahead:                  {'PASS' if c6 else 'FAIL'}")
all_pass = all([c1, c2, c3, c4, c5, c6])
print(f"\n  -> {'PORTFOLIO PROMOTION' if all_pass else 'REJECT - champion untouched'}")
print(f"  n_trials advances to {N_TRIALS} (trial was run).")
