"""
Phase 19: H-SizingBand — rebalance-granularity / no-trade-band refinement of the
champion's vol-target sizing layer.

PRE-REGISTERED experiment (would-have-been trial #98). Spec locked in
SESSION_2026-07-10_SIZINGBAND.md section 1 BEFORE this script produced any numbers.
The trading signal (SMA200 / ROC30 / EMA20>EMA50) is NOT touched — only HOW the
vol-target weights are discretized changes.

Structure (exits at whichever gate fails; pre-gates cost ZERO n_trials):
  Pre-gate A: continuous-sizing upper bound (fee-free incremental turnover) vs the
              25%-step baseline. STOP unless the bound improves MC P(DD<-25%) by
              >= 5pp AND degrades neither full nor TEST Sharpe by more than 0.05.
              Baseline replication gate runs first (as in phase15/17).
  Pre-gate B: turnover / fee-drag / tracking-error census over the FIXED scheme set
              {continuous, step10, step25 baseline, band10}. STOP unless a scheme
              qualifies by the locked formula (incremental fee drag < prorated gross
              benefit) AND captures >= 80% of the tracking improvement. Candidate =
              lowest incremental fee drag among that intersection.
  Trial #98:  ONLY if both pre-gates pass. Full stack on the selected scheme:
              70/15/15 TEST, wf_window_stability 3/4/5/6, MC 1000 seed 11, DSR at
              n_trials=98, family_context, look-ahead audit of the band logic.

Frozen: VOL_TARGET 0.40, LOOKBACK 30, PER_PAIR_CAP 0.50 (weights / 2 on the 2-pair
basket), core signal, exits, fees 0.15%/side, 2-bar lag, BTC+ETH 1d futures universe.
Band width 10% and fine step 10% locked by NEXT_TASK — no sweeps.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')

from pathlib import Path

import numpy as np
import pandas as pd

from freqtrade_dsr import deflated_sharpe_ratio          # AGPL module, repo root
from validator import wf_window_stability, family_from_results_dir, family_context

FEE = 0.0015
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')

VOL_TARGET = 0.40
LOOKBACK = 30
QUANT_BASE = 0.25      # champion baseline step
QUANT_FINE = 0.10      # locked fine step (NEXT_TASK)
BAND = 0.10            # locked no-trade band width, fraction of total equity (NEXT_TASK)
N_TRIALS = 98          # only reached if both pre-gates pass
MC_SIMS = 1000
MC_SEED = 11
ANN = 365

SYMS = ['BTC', 'ETH']


# ---------------------------------------------------------------- data / signal
def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()


def load_fut(sym: str) -> pd.DataFrame:
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})


def core_series(df: pd.DataFrame) -> pd.Series:
    c = df['close']
    return ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)


def cont_scale(df: pd.DataFrame) -> pd.Series:
    """Continuous (unquantized) vol-target scale in [0, 1]."""
    rv = df['close'].pct_change().rolling(LOOKBACK).std() * np.sqrt(ANN)
    return (VOL_TARGET / rv).clip(0, 1)


# ---------------------------------------------------------------- schemes
# Each returns the SIGNAL-TIME per-asset weight matrix (fraction of total equity,
# already divided by 2 for the 2-pair basket). Execution lag applied later.

def weights_step(dfs: dict, step: float | None) -> pd.DataFrame:
    idx = sorted(set().union(*[dfs[s].index for s in SYMS]))
    W = pd.DataFrame(index=pd.DatetimeIndex(idx))
    for s in SYMS:
        raw = core_series(dfs[s]) * cont_scale(dfs[s])
        if step is not None:
            raw = ((raw / step).round() * step).clip(0, 1)
        W[s] = raw.reindex(W.index) / len(SYMS)
    return W.fillna(0)


def weights_band(dfs: dict, band: float = BAND) -> pd.DataFrame:
    """No-trade band scheme (locked constant #7 of the pre-registration):
    - core==0  -> weight 0 (gate exit ALWAYS executes; band never delays an exit)
    - flat -> long (prev 0, core 1) -> enter at the full continuous target
    - otherwise hold previous weight unless |held - target| > band (fraction of
      total equity), in which case rebalance exactly TO the continuous target.
    Iteration is strictly forward in signal time (causal by construction)."""
    Wc = weights_step(dfs, None)                      # continuous targets (already /2)
    core = pd.DataFrame({s: core_series(dfs[s]).reindex(Wc.index).fillna(0) for s in SYMS})
    out = np.zeros(Wc.shape)
    tgt = Wc.values
    cor = core.values
    for i in range(len(Wc)):
        for j in range(len(SYMS)):
            prev = out[i - 1, j] if i > 0 else 0.0
            if cor[i, j] == 0:
                out[i, j] = 0.0
            elif prev == 0.0:
                out[i, j] = tgt[i, j]
            elif abs(prev - tgt[i, j]) > band:
                out[i, j] = tgt[i, j]
            else:
                out[i, j] = prev
    return pd.DataFrame(out, index=Wc.index, columns=Wc.columns)


def positions(W: pd.DataFrame, closes: pd.DataFrame) -> pd.DataFrame:
    """Held positions after the 2-bar execution lag."""
    return W.reindex(closes.index).fillna(0).shift(2).fillna(0)


def turnover_series(pos: pd.DataFrame) -> pd.Series:
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    return turn


def net_returns(W: pd.DataFrame, closes: pd.DataFrame, fee: float = FEE) -> pd.Series:
    pos = positions(W, closes)
    gross = (pos * closes.pct_change().fillna(0)).sum(axis=1)
    return (gross - turnover_series(pos) * fee).dropna()


# ---------------------------------------------------------------- metrics
def m(ret: pd.Series) -> tuple[float, float, float, float]:
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


def mc_tail(ret: pd.Series, sims: int = MC_SIMS, seed: int = MC_SEED) -> tuple[float, float]:
    """(P(maxDD < -25%), median maxDD) over monthly-block shuffles."""
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
    print(f"  {label:<22} FULL Sh {sh_f:5.2f}  DD {dd_f*100:6.1f}%  CAGR {cg_f*100:+6.1f}%  "
          f"| TEST Sh {sh_te:5.2f}  | MC tail {p25*100:5.1f}%  medDD {med*100:6.1f}%")
    return {'full_sh': sh_f, 'full_dd': dd_f, 'full_cagr': cg_f,
            'test_sh': sh_te, 'test_dd': dd_te, 'test_cagr': cg_te,
            'mc_p25': p25, 'mc_med': med}


# =================================================================
print('=' * 78)
print('PHASE 19 — H-SizingBand: rebalance granularity / no-trade band (pre-gated)')
print('=' * 78)

print('\n[1] Loading data (BTC+ETH futures 1d)')
dfs = {s: load_fut(s) for s in SYMS}
closes = pd.DataFrame({s: dfs[s]['close'] for s in SYMS}).sort_index()

# ---------------------------------------------------------------- pre-gate A
print('\n[2] PRE-GATE A — continuous-sizing upper bound (zero n_trials)')

W_base = weights_step(dfs, QUANT_BASE)
ret_base = net_returns(W_base, closes)
res_base = report('BASELINE step25', ret_base)

ok = (0.30 <= res_base['test_sh'] <= 0.50 and 1.0 <= res_base['full_sh'] <= 1.4
      and 0.20 <= res_base['mc_p25'] <= 0.45)
print(f"\n  Replication gate: TEST {res_base['test_sh']:.2f} (0.30-0.50), "
      f"FULL {res_base['full_sh']:.2f} (1.0-1.4), MC tail {res_base['mc_p25']*100:.1f}% "
      f"(20-45%) -> {'OK' if ok else 'MISMATCH — STOP'}")
if not ok:
    sys.exit('Baseline replication failed; aborting before pre-gate A evaluation.')

# Continuous bound: continuous gross, fees charged ONLY on the baseline's fee events.
W_cont = weights_step(dfs, None)
pos_cont = positions(W_cont, closes)
gross_cont = (pos_cont * closes.pct_change().fillna(0)).sum(axis=1)
pos_base = positions(W_base, closes)
ret_bound = (gross_cont - turnover_series(pos_base) * FEE).dropna()
res_bound = report('BOUND continuous*', ret_bound)
print('  (* fee-free incremental turnover — deliberately unrealistic upper bound)')

d_tail = res_base['mc_p25'] - res_bound['mc_p25']
d_full = res_bound['full_sh'] - res_base['full_sh']
d_test = res_bound['test_sh'] - res_base['test_sh']
print(f"\n  Bound vs baseline: dMCtail {d_tail*100:+.1f}pp (need >= +5.0pp)  "
      f"dFULL Sh {d_full:+.3f} (need >= -0.05)  dTEST Sh {d_test:+.3f} (need >= -0.05)")
print(f"  dMaxDD {(res_bound['full_dd'] - res_base['full_dd'])*100:+.1f}pp  "
      f"dMC medDD {(res_bound['mc_med'] - res_base['mc_med'])*100:+.1f}pp")

gate_a = (d_tail >= 0.05) and (d_full >= -0.05) and (d_test >= -0.05)
print(f"\n  PRE-GATE A: {'PASS' if gate_a else 'FAIL'}")
if not gate_a:
    print('\n  STOP RULE TRIGGERED: even the fee-free continuous bound cannot deliver the')
    print('  required tail improvement without Sharpe damage. No discretization scheme can')
    print('  beat this bound. SIZING LAYER DECLARED CLOSED AT ITS EFFICIENT FRONTIER.')
    print('  Zero trials spent; n_trials remains 97.')
    sys.exit(0)

# ---------------------------------------------------------------- pre-gate B
print('\n[3] PRE-GATE B — turnover / fee-drag census (zero n_trials; cost accounting only)')

B_ann = (ret_bound.mean() - ret_base.mean()) * ANN
print(f"  Annualized gross benefit implied by the bound: {B_ann*100:+.2f}%/yr")

schemes = {
    'continuous': W_cont,
    'step10': weights_step(dfs, QUANT_FINE),
    'step25': W_base,
    'band10': weights_band(dfs),
}
pos_all = {k: positions(w, closes) for k, w in schemes.items()}
te_base = (pos_all['step25'] - pos_cont).abs().sum(axis=1).mean()
fee_base_ann = turnover_series(pos_all['step25']).mean() * ANN * FEE

rows = {}
for k, pos in pos_all.items():
    turn_ann = turnover_series(pos).mean() * ANN
    fee_ann = turn_ann * FEE
    te = (pos - pos_cont).abs().sum(axis=1).mean()
    capture = (te_base - te) / te_base if te_base > 0 else float('nan')
    inc_drag = fee_ann - fee_base_ann
    benefit = B_ann * capture
    qualifies = inc_drag < benefit
    rows[k] = dict(turn_ann=turn_ann, fee_ann=fee_ann, te=te, capture=capture,
                   inc_drag=inc_drag, benefit=benefit, qualifies=qualifies)
    print(f"  {k:<11} turnover {turn_ann:5.1f}x/yr  fee drag {fee_ann*100:5.2f}%/yr "
          f"(incr {inc_drag*100:+5.2f}%)  TE {te:.4f}  capture {capture*100:6.1f}%  "
          f"prorated benefit {benefit*100:+5.2f}%  -> {'QUALIFIES' if qualifies else 'no'}")

cands = {k: v for k, v in rows.items()
         if k != 'step25' and v['qualifies'] and v['capture'] >= 0.80}
gate_b = len(cands) > 0
if gate_b:
    pick = min(cands, key=lambda k: cands[k]['inc_drag'])
    print(f"\n  PRE-GATE B: PASS — trial candidate (formula-selected): {pick}")
else:
    print('\n  PRE-GATE B: FAIL — no scheme both qualifies on the fee-vs-benefit formula')
    print('  and captures >= 80% of the tracking improvement. No trial. n_trials stays 97.')
    sys.exit(0)

# ---------------------------------------------------------------- trial #98
print(f'\n[4] TRIAL #98 — champion with {pick} discretization (real fees), full stack')

ret_trial = net_returns(schemes[pick], closes)
res_trial = report(f'TRIAL {pick}', ret_trial)
n = len(ret_trial)
i1, i2 = int(n * 0.70), int(n * 0.85)
sh_tr, _, _, _ = m(ret_trial.iloc[:i1])
sh_vl, _, _, _ = m(ret_trial.iloc[i1:i2])
print(f"  TRAIN {sh_tr:.2f} | VAL {sh_vl:.2f} | TEST {res_trial['test_sh']:.2f}")

print('\n[4a] Walk-forward window stability (validator.wf_window_stability, 3/4/5/6)')
wf_t = wf_window_stability(ret_trial)
wf_b = wf_window_stability(ret_base)
maj = 0
for k in (3, 4, 5, 6):
    t, b = wf_t[k], wf_b[k]
    maj += int(t['majority_positive'])
    print(f"  {k} windows: trial {t['windows_positive']}/{k} pos "
          f"(maj {'Y' if t['majority_positive'] else 'N'}) sharpes {t['window_sharpes']} | "
          f"baseline {b['windows_positive']}/{k} pos")
print(f"  Majority-positive configs: {maj}/4 (bar: >= 3)")

print(f'\n[4b] DSR at n_trials={N_TRIALS} (freqtrade_dsr.py)')
dsr_t = deflated_sharpe_ratio(ret_trial.tolist(), n_trials=N_TRIALS)
dsr_b = deflated_sharpe_ratio(ret_base.tolist(), n_trials=N_TRIALS)
print(f"  trial {pick}: DSR={dsr_t['dsr']:.4f}  (skew {dsr_t['skew']:+.2f}, "
      f"kurt {dsr_t['kurtosis']:.1f}, n_obs {dsr_t['n_obs']})")
print(f"  baseline @98: DSR={dsr_b['dsr']:.4f}   (recorded baseline @97: 0.626)")

print('\n[4c] Family context (Kaufman average-of-all-tests, from results dir)')
fam = family_from_results_dir()
ctx = family_context(f'sizingband_{pick}', res_trial['full_sh'], res_trial['test_sh'], fam)
ts = ctx['test_sharpe']
print(f"  TEST Sharpe family (n={ts.get('n_family')}): mean {ts.get('mean')} / "
      f"median {ts.get('median')} / max {ts.get('max')}; candidate {ts.get('candidate')} "
      f"(rank {ts.get('candidate_rank')}, pctile {ts.get('candidate_percentile')})")

print('\n[4d] Look-ahead audit: band/scheme weights must be prefix-stable')
la_ok = True
for cut in (int(n * 0.6), int(n * 0.8), n - 30):
    idx_cut = schemes[pick].index[cut]
    dfs_cut = {s: dfs[s].loc[:idx_cut] for s in SYMS}
    W_cut = (weights_band(dfs_cut) if pick == 'band10'
             else weights_step(dfs_cut, None if pick == 'continuous' else QUANT_FINE))
    full_pref = schemes[pick].loc[W_cut.index]
    diff = (W_cut - full_pref).abs().max().max()
    la_ok &= diff < 1e-12
    print(f"  cut at {idx_cut.date()}: max |W_cut - W_full_prefix| = {diff:.2e} "
          f"{'OK' if diff < 1e-12 else 'LOOKAHEAD VIOLATION'}")

print('\n[4e] Per-year turnover / fee accounting (trial vs baseline; bar 5 of validation)')
pos_trial = positions(schemes[pick], closes)
t_trial, t_base = turnover_series(pos_trial), turnover_series(pos_base)
for yr in sorted(set(ret_trial.index.year)):
    tt = t_trial[t_trial.index.year == yr].sum()
    tb = t_base[t_base.index.year == yr].sum()
    print(f"  {yr}: trial turnover {tt:5.2f}x (fees {tt*FEE*100:.2f}%)  "
          f"baseline {tb:5.2f}x (fees {tb*FEE*100:.2f}%)")

print('\n[5] Validation scorecard (ALL must hold; bars pre-declared)')
c1 = res_trial['mc_p25'] <= 0.20
c2 = (res_trial['test_sh'] >= res_base['test_sh'] - 0.05
      and res_trial['full_sh'] >= res_base['full_sh'] - 0.05)
c3 = maj >= 3
c4 = dsr_t['dsr'] >= 0.626
c5 = la_ok
print(f"  1 MC tail <= 20%:                {'PASS' if c1 else 'FAIL'} ({res_trial['mc_p25']*100:.1f}%)")
print(f"  2 TEST & FULL Sh >= base - 0.05: {'PASS' if c2 else 'FAIL'} "
      f"(TEST {res_trial['test_sh']:.2f} vs {res_base['test_sh']:.2f}; "
      f"FULL {res_trial['full_sh']:.2f} vs {res_base['full_sh']:.2f})")
print(f"  3 WF majority-pos >= 3/4 configs:{'PASS' if c3 else 'FAIL'} ({maj}/4)")
print(f"  4 DSR@98 >= 0.626:               {'PASS' if c4 else 'FAIL'} ({dsr_t['dsr']:.4f})")
print(f"  5 No look-ahead:                 {'PASS' if c5 else 'FAIL'}")
print(f"\n  -> {'ALL PASS: promote the discretization into the champion' if all([c1, c2, c3, c4, c5]) else 'REJECT: champion unchanged'}")
print(f"  n_trials advances to {N_TRIALS} (trial was run).")
