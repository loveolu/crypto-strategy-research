"""
Phase 17: A-ValidatorAudit — Kaufman Ch.21 diagnostics run against the EXISTING champion.

THIS IS AN AUDIT, NOT A TRIAL. Zero n_trials cost: no new construct is selected, no
parameter is changed, no new strategy is backtested. Cumulative n_trials stays at 97.
Spec locked in SESSION_2026-07-10_VALIDATOR_AUDIT.md section 1 BEFORE this script was
written or produced any numbers. Assignment: research/NEXT_TASK.md (the reissued
validator-audit assignment, Research Director cycles #3/#4 of 2026-07-10).

Order of operations:
  [0] Reconstruct the champion daily stream (phase15/16 baseline convention) and
      REPLICATION-GATE it against recorded bands before any diagnostic runs.
  [1] Diagnostic 1 — price-shock P&L decomposition (two pre-declared shock
      definitions), champion vs BTC buy-and-hold on the identical window.
      Downgrade trigger A evaluated per the pre-registered operationalization.
  [2] Diagnostic 2 — walk-forward window-stability at 3/4/5/6 windows over the same
      OOS region, plus rolling 18-month Sharpe (monthly step). Trigger B evaluated.
  [3] Diagnostic 3 — average-of-all-tests family context from the EXISTING records
      (results/*.json of the 2026-06-11 search + documented extended-session variants;
      nothing re-run).
  [4] JSON dump of everything to results/phase17_validator_audit.json.

Harness conventions identical to phase15/16: futures feathers, fees 0.15%/side,
2-bar signal lag, quantized vol-target weights / 2, monthly-block MC seed 11.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')

import json
from pathlib import Path

import numpy as np
import pandas as pd

from validator import (shock_day_mask, shock_pnl_decomposition, top_day_concentration,
                       wf_window_stability, rolling_sharpe_series, family_context,
                       family_from_results_dir)

FEE = 0.0015
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
RESULTS_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/research/results')

VOL_TARGET = 0.40
LOOKBACK = 30
QUANT = 0.25
ANN = 365
MC_SIMS = 1000
SYMS2 = ['BTC', 'ETH']

audit: dict = {}


# ---------------------------------------------------------------- champion harness (frozen, phase15/16 convention)
def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()


def load_fut(sym: str) -> pd.DataFrame:
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})


def rv_cc(df: pd.DataFrame, lookback: int = LOOKBACK) -> pd.Series:
    return df['close'].pct_change().rolling(lookback).std() * np.sqrt(ANN)


def quantize(w):
    return ((w / QUANT).round() * QUANT).clip(0, 1)


def core_bull(df: pd.DataFrame) -> pd.Series:
    c = df['close']
    return ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)


def basket_weights(dfs: dict, syms: list) -> pd.DataFrame:
    idx = sorted(set().union(*[dfs[s].index for s in syms]))
    W = pd.DataFrame(index=pd.DatetimeIndex(idx))
    for s in syms:
        core = core_bull(dfs[s])
        rv = rv_cc(dfs[s])
        scale = (VOL_TARGET / rv).clip(0, 1)
        W[s] = quantize(core * scale).reindex(W.index) / len(syms)
    return W.fillna(0)


def net_from_weights(W: pd.DataFrame, closes: pd.DataFrame, fee: float = FEE) -> pd.Series:
    W = W.reindex(closes.index).fillna(0)
    pos = W.shift(2).fillna(0)  # signal close[t] -> exec open[t+1] -> held close[t+1]
    ret_mat = closes.pct_change()
    gross = (pos * ret_mat.fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    return (gross - turn * fee).dropna()


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


# =================================================================
print('=' * 78)
print('PHASE 17 — A-ValidatorAudit: Kaufman Ch.21 diagnostics on the champion')
print('  AUDIT ONLY — zero n_trials cost (stays 97); nothing new is backtested')
print('=' * 78)

print('\n[0] Champion stream reconstruction + replication gate')
dfs = {s: load_fut(s) for s in SYMS2}
closes2 = pd.DataFrame({s: dfs[s]['close'] for s in SYMS2}).sort_index()
for s in SYMS2:
    print(f"  {s} futures 1d: {dfs[s].index[0].date()} -> {dfs[s].index[-1].date()}  ({len(dfs[s])} bars)")
W = basket_weights(dfs, SYMS2)
ret = net_from_weights(W, closes2)

n = len(ret)
i_te = int(n * 0.85)
sh_f, dd_f, cg_f, tr_f = m(ret)
sh_te = m(ret.iloc[i_te:])[0]
blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
rng = np.random.default_rng(11)
dds = []
for _ in range(MC_SIMS):
    seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
    eq = np.cumprod(1 + seq)
    dds.append((eq / np.maximum.accumulate(eq) - 1).min())
mc_tail = float((np.array(dds) < -0.25).mean())
print(f"  FULL Sharpe {sh_f:.2f}  DD {dd_f*100:.1f}%  CAGR {cg_f*100:+.1f}%  total {tr_f*100:+.0f}%"
      f"  | TEST Sharpe {sh_te:.2f}  | MC({MC_SIMS}) P(DD<-25%) {mc_tail*100:.1f}%")
ok = (0.35 <= sh_te <= 0.45) and (1.0 <= sh_f <= 1.4) and (0.25 <= mc_tail <= 0.40)
print(f"  Replication gate (TEST 0.35-0.45, FULL 1.0-1.4, MC tail 25-40%): {'OK' if ok else 'MISMATCH — STOP'}")
if not ok:
    sys.exit('Baseline replication failed; aborting audit before diagnostics.')
audit['replication'] = {'full_sharpe': sh_f, 'full_dd': dd_f, 'full_cagr': cg_f,
                        'test_sharpe': sh_te, 'mc_p_dd25': mc_tail}

# BTC buy-and-hold baseline on the identical calendar window (fee-free: conservative
# direction — biases the shock comparison AGAINST the champion, which pays fees).
hold = closes2['BTC'].pct_change().reindex(ret.index).fillna(0.0)
sh_h, dd_h, cg_h, tr_h = m(hold)
print(f"  BTC hold same window: Sharpe {sh_h:.2f}  DD {dd_h*100:.1f}%  CAGR {cg_h*100:+.1f}%  total {tr_h*100:+.0f}%")

# ---------------------------------------------------------------- [1] shock decomposition
print('\n[1] DIAGNOSTIC 1 — price-shock P&L decomposition (definitions pre-declared)')
und = pd.DataFrame({s: dfs[s]['close'].pct_change() for s in SYMS2}).reindex(ret.index)

masks = {
    'A_p99_static': shock_day_mask(und, method='p99', pctile=0.99),
    'B_3sigma_rolling30': shock_day_mask(und, method='3sigma', sigma_mult=3.0, vol_lookback=30),
}
audit['shock'] = {}
for tag, mask in masks.items():
    mask = mask.reindex(ret.index).fillna(False)
    n_shock = int(mask.sum())
    in_mkt = W.shift(2).reindex(ret.index).fillna(0).sum(axis=1) > 0
    n_shock_inmkt = int((mask & in_mkt).sum())
    print(f"\n  Definition {tag}: {n_shock} shock days of {len(ret)} "
          f"({n_shock/len(ret)*100:.1f}%); champion in-market on {n_shock_inmkt} of them")
    champ = shock_pnl_decomposition(ret, mask)
    hold_d = shock_pnl_decomposition(hold, mask)
    for label, d in [('CHAMPION', champ), ('BTC HOLD', hold_d)]:
        a, e = d['all'], d['ex_all_shock']
        print(f"    {label:<9} all days:      total {a['total_return']*100:+8.1f}%  Sharpe {a['sharpe']:5.2f}")
        print(f"    {label:<9} ex ALL shock:  total {e['total_return']*100:+8.1f}%  Sharpe {e['sharpe']:5.2f}"
              f"   (shock days carry {e['log_pnl_share_of_shock_days']*100:+.1f}% of log-P&L)")
        for k in (5, 10, 20):
            t = d[f'top{k}']
            print(f"    {label:<9} top{k:<2} shock:  ex-best total {t['ex_best']['total_return']*100:+8.1f}% "
                  f"(Sh {t['ex_best']['sharpe']:4.2f})  ex-worst {t['ex_worst']['total_return']*100:+8.1f}% "
                  f"(Sh {t['ex_worst']['sharpe']:4.2f})  ex-both {t['ex_both']['total_return']*100:+8.1f}% "
                  f"(Sh {t['ex_both']['sharpe']:4.2f})  best-{k} log-share {t['log_pnl_share_of_best']*100:+.1f}%")
    audit['shock'][tag] = {'n_shock_days': n_shock, 'n_shock_days_in_market': n_shock_inmkt,
                           'champion': champ, 'btc_hold': hold_d}

print('\n  Strategy-own top-day concentration (any day, not just shock days):')
audit['top_days'] = {}
for label, series in [('CHAMPION', ret), ('BTC HOLD', hold)]:
    d = top_day_concentration(series)
    audit['top_days'][label] = d
    for k in (5, 10, 20):
        t = d[f'top{k}']
        print(f"    {label:<9} top{k:<2} own days: ex-best total {t['ex_best']['total_return']*100:+8.1f}%  "
              f"ex-worst {t['ex_worst']['total_return']*100:+8.1f}%  ex-both {t['ex_both']['total_return']*100:+8.1f}%  "
              f"best-{k} log-share {t['log_pnl_share_of_best']*100:+.1f}%")

# Trigger A (pre-registered operationalization): Definition A primary, B corroboration.
ca = audit['shock']['A_p99_static']['champion']['top10']['log_pnl_share_of_best']
ha = audit['shock']['A_p99_static']['btc_hold']['top10']['log_pnl_share_of_best']
trigger_a = (ca > 0.50) and (ca - ha > 0.10)
cb = audit['shock']['B_3sigma_rolling30']['champion']['top10']['log_pnl_share_of_best']
hb = audit['shock']['B_3sigma_rolling30']['btc_hold']['top10']['log_pnl_share_of_best']
print(f"\n  DOWNGRADE TRIGGER A: champion top-10-positive-shock log-share {ca*100:.1f}% "
      f"(>50%? {'YES' if ca > 0.50 else 'no'}); vs BTC hold {ha*100:.1f}% "
      f"(gap {abs(ca-ha)*100:+.1f}pp, champion more dependent by >10pp? "
      f"{'YES' if ca - ha > 0.10 else 'no'})")
print(f"    Definition B corroboration: champion {cb*100:.1f}% vs hold {hb*100:.1f}%")
print(f"    TRIGGER A: {'FIRES' if trigger_a else 'does NOT fire'}")
audit['trigger_A'] = {'fires': bool(trigger_a), 'champ_shareA': ca, 'hold_shareA': ha,
                      'champ_shareB': cb, 'hold_shareB': hb}

# ---------------------------------------------------------------- [2] WF window stability
print('\n[2] DIAGNOSTIC 2 — walk-forward window-stability (3/4/5/6 windows, same OOS region)')
wfs = wf_window_stability(ret, window_counts=(3, 4, 5, 6), oos_start_frac=0.5)
audit['wf_stability'] = wfs
minority = 0
for k, d in wfs.items():
    flag = 'majority-pos' if d['majority_positive'] else 'MINORITY-POS'
    minority += 0 if d['majority_positive'] else 1
    print(f"  {k} windows: {d['windows_positive']}/{d['windows_total']} positive ({flag})   "
          f"Sharpes " + " ".join(f"{s:+.2f}" for s in d['window_sharpes'])
          + f"   worst {d['worst_window_sharpe']:+.2f}  spread {d['sharpe_spread']:.2f}")
    print(f"    returns " + " ".join(f"{r*100:+.1f}%" for r in d['window_returns']))
trigger_b = minority >= 2
print(f"\n  DOWNGRADE TRIGGER B: minority-positive at {minority}/4 configurations "
      f"(fires at >=2) -> {'FIRES' if trigger_b else 'does NOT fire'}")
audit['trigger_B'] = {'fires': bool(trigger_b), 'minority_configs': minority}

print('\n  Rolling 18-month Sharpe (monthly step) on the champion daily stream:')
rs = rolling_sharpe_series(ret, window_days=548)
worst_t = rs.idxmin()
neg_share = float((rs < 0).mean())
print(f"    evaluations: {len(rs)}  (first {rs.index[0].date()}, last {rs.index[-1].date()})")
print(f"    median {rs.median():.2f}   min {rs.min():.2f} (18m ending {worst_t.date()})   "
      f"max {rs.max():.2f}   share negative {neg_share*100:.1f}%")
audit['rolling_18m'] = {'n_evals': len(rs), 'median': float(rs.median()),
                        'min': float(rs.min()), 'min_ending': str(worst_t.date()),
                        'max': float(rs.max()), 'share_negative': neg_share,
                        'series': {str(t.date()): round(float(v), 3) for t, v in rs.items()}}

# ---------------------------------------------------------------- [3] family context
print('\n[3] DIAGNOSTIC 3 — average-of-all-tests family context (existing records only)')
fam = family_from_results_dir(RESULTS_DIR)
print(f"  Loaded {len(fam)} recorded verdicts from results/*.json (2026-06-11 search)")

# Extended-session TVT-family variants documented in the session records (nothing
# re-run; each line cites its source). test_sharpe None where the record has no
# TEST-split number.
DOCUMENTED_VARIANTS = [
    # BEST_STRATEGY_REPORT.md "Comparison vs benchmarks" (harness, same window/fees)
    {'name': 'tvt_trend_only_no_vol_sizing', 'full_sharpe': 1.25, 'test_sharpe': None},
    {'name': 'tvt_voltarget_only_no_trend', 'full_sharpe': 0.97, 'test_sharpe': None},
    # SESSION_2026-06-11_FINAL_SUMMARY.md rankings
    {'name': 'tvt_9asset_portfolio_vol_overlay', 'full_sharpe': 1.10, 'test_sharpe': 0.23},
    {'name': 'hybrid_btc_core_top2_momentum_alts', 'full_sharpe': 1.28, 'test_sharpe': 0.12},
]
fam_all = fam + DOCUMENTED_VARIANTS
# Champion's recorded numbers in the same records: harness full-window Sharpe 1.33
# (BEST_STRATEGY_REPORT.md; this session's futures-window replication gives 1.1) and
# held-out TEST Sharpe 0.41. Report family context against BOTH champion figures.
ctx = family_context('TrendVolTarget', 1.33, 0.41, fam_all)
audit['family_context'] = ctx
for metric in ('full_sharpe', 'test_sharpe'):
    s = ctx[metric]
    print(f"  {metric}: family n={s['n_family']}  mean {s['mean']}  median {s['median']}  "
          f"max {s['max']}  min {s['min']}   champion {s['candidate']} "
          f"(rank {s['candidate_rank']}, pctile {s['candidate_percentile']})")
# Note the recorded sweep RANGES that exist only as ranges in the record:
print("  (Recorded-as-ranges, not individual cells: SMA150-250 x ROC20-40 sweep Sharpe "
      "0.81-1.33; EMA pair sweep 1.15-1.17; vol-target 30-50% sweep 1.24-1.33 — "
      "BEST_STRATEGY_REPORT.md. These widen the family below its recorded mean.)")

# How many recorded TEST sharpes are >= champion's 0.41?
test_vals = [f['test_sharpe'] for f in fam_all if f.get('test_sharpe') is not None]
n_ge = sum(1 for v in test_vals if v >= 0.41)
print(f"  Of {len(test_vals)} recorded TEST Sharpes, {n_ge} are >= the champion's 0.41")
audit['family_test_ge_champion'] = {'n_test_recorded': len(test_vals), 'n_ge_champion': n_ge}

# ---------------------------------------------------------------- [4] dump
out_fp = RESULTS_DIR / 'phase17_validator_audit.json'
with open(out_fp, 'w') as f:
    json.dump(audit, f, indent=2, default=str)
print(f"\n[4] Audit payload saved to {out_fp}")
print('\nAUDIT COMPLETE — n_trials unchanged at 97.')
