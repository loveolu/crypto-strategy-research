"""
Phase 15: H-RangeVol — range-based volatility estimator in TrendVolTarget's sizing layer.

PRE-REGISTERED experiment (trials #97 and #98 in the project's cumulative DSR ledger).
Spec locked in SESSION_2026-07-10_RANGEVOL.md section 1 BEFORE this script produced any
numbers. The trading signal (SMA200 / ROC30 / EMA20>EMA50) is NOT touched — only the
volatility input to the vol-target sizing changes.

  Trial #97 (primary):   Garman-Klass 30d      rv = sqrt(mean_30(gk_var) * 365)
                         gk_var = 0.5*ln(H/L)^2 - (2ln2 - 1)*ln(C/O)^2
  Trial #98 (secondary): EWMA close-to-close   var_t = 0.94*var_{t-1} + 0.06*r_t^2
                         (RiskMetrics lambda=0.94), rv = sqrt(var * 365)

Primary pre-registered prediction: MC P(MaxDD < -25%) drops to <= 20% (baseline 28-38%).
Sharpe only needs non-inferiority (TEST >= 0.35).

Frozen: VOL_TARGET 0.40, lookback 30, QUANT_STEP 0.25, per-pair 50% (weights/2 on the
2-pair basket), core signal, exits, fees 0.15%/side, 2-bar lag, BTC+ETH 1d universe.

Pipeline conventions identical to phase13/14: futures feathers, 70/15/15 chronological
split, 4-window walk-forward, monthly-block Monte Carlo (1,000 sims here per NEXT_TASK),
DSR from freqtrade_dsr.py at n_trials=98 (baseline recomputed at 98 for like-for-like).
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
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')

VOL_TARGET = 0.40
LOOKBACK = 30
QUANT = 0.25
LAMBDA = 0.94          # RiskMetrics, pre-registered, not tuned
N_TRIALS = 98          # cumulative project trial count incl. both variants
MC_SIMS = 1000
ANN = 365

SYMS2 = ['BTC', 'ETH']
SYMS9 = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'BNB']


# ---------------------------------------------------------------- estimators
def rv_cc(df: pd.DataFrame, lookback: int = LOOKBACK) -> pd.Series:
    """Champion's estimator: close-to-close rolling std, annualized."""
    return df['close'].pct_change().rolling(lookback).std() * np.sqrt(ANN)


def rv_gk(df: pd.DataFrame, lookback: int = LOOKBACK) -> pd.Series:
    """Garman-Klass (1980): uses OHLC range; assumes no opening jump (valid 24/7)."""
    log_hl = np.log(df['high'] / df['low'])
    log_co = np.log(df['close'] / df['open'])
    gk_var = 0.5 * log_hl ** 2 - (2 * np.log(2) - 1) * log_co ** 2
    return np.sqrt(gk_var.rolling(lookback).mean() * ANN)


def rv_ewma(df: pd.DataFrame, lam: float = LAMBDA) -> pd.Series:
    """EWMA close-to-close variance (RiskMetrics). min_periods=30 to match CC warmup."""
    r = df['close'].pct_change()
    var = (r ** 2).ewm(alpha=1 - lam, adjust=False, min_periods=LOOKBACK).mean()
    return np.sqrt(var * ANN)


# ---------------------------------------------------------------- sanity checks
# NOTE: first implementation (single seed, threshold derived from TRUE vol) was
# statistically invalid — see SESSION_2026-07-10_RANGEVOL.md section 2.0 for the
# documented failure and the refined spec (declared before this version was run).
def synth_ohlc(sigma_daily: np.ndarray, seed: int, n_intra: int = 100) -> pd.DataFrame:
    """Synthetic zero-drift GBM daily OHLC bars built from n_intra intrabar steps."""
    rng = np.random.default_rng(seed)
    n = len(sigma_daily)
    incr = rng.normal(0.0, 1.0, (n, n_intra)) * (sigma_daily[:, None] / np.sqrt(n_intra))
    logp = np.cumsum(incr.reshape(-1)).reshape(n, n_intra) + np.log(100.0)
    close = np.exp(logp[:, -1])
    open_ = np.concatenate([[100.0], close[:-1]])
    log_open = np.log(open_)
    high = np.exp(np.maximum(logp.max(axis=1), log_open))
    low = np.exp(np.minimum(logp.min(axis=1), log_open))
    idx = pd.date_range('2020-01-01', periods=n, freq='D', tz='UTC')
    return pd.DataFrame({'open': open_, 'high': high, 'low': low, 'close': close}, index=idx)


ESTIMATORS = [('CC30', rv_cc), ('GK30', rv_gk), ('EWMA', rv_ewma)]


def _const_run_stats(ann_sig: float, n_seeds: int, n_bars: int, n_intra: int) -> dict:
    """Per-estimator (mean level, mean time-series std) across seeds at constant vol."""
    daily = np.full(n_bars, ann_sig / np.sqrt(ANN))
    levels = {k: [] for k, _ in ESTIMATORS}
    stds = {k: [] for k, _ in ESTIMATORS}
    for seed in range(n_seeds):
        df = synth_ohlc(daily, seed=1000 + seed, n_intra=n_intra)
        for k, fn in ESTIMATORS:
            est = fn(df).dropna()
            levels[k].append(est.mean())
            stds[k].append(est.std())
    return {k: (float(np.mean(levels[k])), float(np.mean(stds[k]))) for k, _ in ESTIMATORS}


def sanity_checks() -> bool:
    print('\n[1] Estimator sanity checks — refined spec (see session report 2.0)')
    ann_sig = 0.60  # 60% annualized — crypto-like
    n_seeds_a, n_bars_a = 100, 1000

    # ---- (a) constant-vol GBM: agreement in expectation + efficiency
    stats100 = _const_run_stats(ann_sig, n_seeds_a, n_bars_a, n_intra=100)
    stats1k = _const_run_stats(ann_sig, 20, n_bars_a, n_intra=1000)
    print(f"  (a) constant-vol GBM ({n_seeds_a} seeds x {n_bars_a} bars, true ann vol {ann_sig:.2f}):")
    ok_a = True
    for k, _ in ESTIMATORS:
        lvl, sd = stats100[k]
        rel = lvl / ann_sig - 1
        print(f"      {k:<5} mean {lvl:.4f} ({rel:+.1%} vs true)   estimator std {sd:.4f} "
              f"({sd / stats100['CC30'][1]:.2f}x CC)")
        if k != 'GK30':
            ok_a &= abs(rel) < 0.10
    gk_bias_100 = stats100['GK30'][0] / ann_sig - 1
    gk_bias_1k = stats1k['GK30'][0] / ann_sig - 1
    bias_shrinks = abs(gk_bias_1k) < abs(gk_bias_100)
    ok_a &= abs(gk_bias_100) < 0.10 and bias_shrinks
    print(f"      GK discretization bias: {gk_bias_100:+.1%} @100 intrabar steps -> "
          f"{gk_bias_1k:+.1%} @1000 steps ({'shrinks: OK, discretization artifact' if bias_shrinks else 'DOES NOT SHRINK: FAIL'})")

    # ---- (b) vol jump, measured against each estimator's OWN pre/post levels
    n_seeds_b, pre, post = 200, 200, 90
    sig = np.full(pre + post, ann_sig / np.sqrt(ANN))
    sig[pre:] *= 2.0
    own_pre = {k: stats100[k][0] for k, _ in ESTIMATORS}          # own asymptote at sigma1
    own_post = {k: 2.0 * v for k, v in own_pre.items()}           # bias is multiplicative
    first_touch = {k: [] for k, _ in ESTIMATORS}
    sustained = {k: [] for k, _ in ESTIMATORS}
    horizon = 60
    for seed in range(n_seeds_b):
        df = synth_ohlc(sig, seed=5000 + seed)
        for k, fn in ESTIMATORS:
            est = fn(df).values[pre:pre + horizon]
            mid = 0.5 * (own_pre[k] + own_post[k])
            hit = np.where(est >= mid)[0]
            first_touch[k].append(hit[0] + 1 if len(hit) else horizon + 1)
            inside = np.abs(est - own_post[k]) / own_post[k] <= 0.15
            sus = horizon + 1
            for i in range(horizon):
                if inside[i:].all():
                    sus = i + 1
                    break
            sustained[k].append(sus)
    print(f"  (b) vol-jump 0.60->1.20 ann ({n_seeds_b} seeds), vs each estimator's OWN levels:")
    med_ft = {k: float(np.median(first_touch[k])) for k, _ in ESTIMATORS}
    med_su = {k: float(np.median(sustained[k])) for k, _ in ESTIMATORS}
    for k, _ in ESTIMATORS:
        print(f"      {k:<5} median first-touch {med_ft[k]:5.1f} bars   "
              f"median sustained(+/-15%, holds thru bar {horizon}) {med_su[k]:5.1f} bars")
    verdict = {}
    for k in ('GK30', 'EWMA'):
        verdict[k] = (med_su[k] < med_su['CC30']) and (med_ft[k] <= med_ft['CC30'] + 2)
        print(f"      {k}: {'PASS' if verdict[k] else 'FAIL'} "
              f"(sustained {med_su[k]:.1f} vs CC {med_su['CC30']:.1f}; "
              f"first-touch {med_ft[k]:.1f} vs CC {med_ft['CC30']:.1f}+2)")
    print(f"  Sanity verdict: agreement {'OK' if ok_a else 'FAIL'}; "
          f"GK30 {'PASS' if verdict['GK30'] else 'FAIL'}, EWMA {'PASS' if verdict['EWMA'] else 'FAIL'}")
    globals()['SANITY_PASS'] = {k: (ok_a and v) for k, v in verdict.items()}
    return ok_a and (verdict['GK30'] or verdict['EWMA'])


# ---------------------------------------------------------------- champion harness
def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()


def load_fut(sym: str) -> pd.DataFrame:
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})


def quantize(w: pd.Series | pd.DataFrame):
    return ((w / QUANT).round() * QUANT).clip(0, 1)


def core_series(df: pd.DataFrame) -> pd.Series:
    c = df['close']
    return ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)


def basket_weights(dfs: dict[str, pd.DataFrame], rv_fn, syms: list[str], **rv_kw) -> pd.DataFrame:
    idx = sorted(set().union(*[dfs[s].index for s in syms]))
    W = pd.DataFrame(index=pd.DatetimeIndex(idx))
    for s in syms:
        core = core_series(dfs[s])
        rv = rv_fn(dfs[s], **rv_kw)
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


# ---------------------------------------------------------------- evaluation
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


@dataclass
class ValResult:
    label: str
    full_sharpe: float; full_dd: float; full_cagr: float
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
    sh_f, dd_f, cg_f, _ = m(ret)
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
    r = ValResult(label, sh_f, dd_f, cg_f, sh_tr, sh_vl, sh_te, dd_te, cg_te,
                  wf_sh, wf_rt, sum(1 for x in wf_rt if x > 0),
                  float(np.percentile(dds, 50)), p_dd25, st_f, st_te)
    print(f"\n{label}")
    print(f"  FULL  Sharpe {sh_f:5.2f}  DD {dd_f*100:6.1f}%  CAGR {cg_f*100:+6.1f}%")
    print(f"  TRAIN {sh_tr:5.2f} | VAL {sh_vl:5.2f} | TEST {sh_te:5.2f}  "
          f"(TEST CAGR {cg_te*100:+5.1f}%, DD {dd_te*100:5.1f}%)")
    print(f"  WF Sharpe: " + " ".join(f"{x:+.2f}" for x in wf_sh)
          + "   WF ret: " + " ".join(f"{x*100:+.1f}%" for x in wf_rt)
          + f"   pos {r.wf_pos}/4")
    print(f"  MC({MC_SIMS}) medDD {r.mc_med_dd*100:.1f}%  P(DD<-25%) {p_dd25*100:.1f}%"
          f"   | stress(2x slip) FULL Sh {st_f:.2f} TEST Sh {st_te:.2f}")
    return r


# =================================================================
print('=' * 78)
print('PHASE 15 — H-RangeVol: range-based vol estimator in champion sizing layer')
print('  trials #97 (Garman-Klass 30d) and #98 (EWMA lambda=0.94), pre-registered')
print('=' * 78)

if not sanity_checks():
    sys.exit('SANITY CHECK FAILED for both variants — mechanism absent; spending zero trials (per spec).')
RUN_GK = SANITY_PASS['GK30']       # noqa: F821 — set inside sanity_checks
RUN_EWMA = SANITY_PASS['EWMA']     # noqa: F821
N_TRIALS = 96 + int(RUN_GK) + int(RUN_EWMA)  # honest count: only backtested variants
print(f"\n  Variants proceeding: GK30={'YES' if RUN_GK else 'NO (sanity fail, zero-trial stop)'}, "
      f"EWMA={'YES' if RUN_EWMA else 'NO (sanity fail, zero-trial stop)'}  -> n_trials={N_TRIALS}")

print('\n[2] Loading data (BTC+ETH primary, 9-asset for cross-asset transfer)')
dfs = {s: load_fut(s) for s in SYMS9}
closes2 = pd.DataFrame({s: dfs[s]['close'] for s in SYMS2}).sort_index()
FEE_STRESS = FEE + 0.001  # +0.10%/side extra slippage stress

results: dict[str, ValResult] = {}
rets: dict[str, pd.Series] = {}

print('\n[3] Baseline replication check')
W = basket_weights(dfs, rv_cc, SYMS2)
ret_base = net_from_weights(W, closes2)
ret_base_st = net_from_weights(W, closes2, fee=FEE_STRESS)
res_base = full_validation(ret_base, 'BASELINE: champion TVT BTC+ETH (cc30)', ret_base_st)
results['base'] = res_base; rets['base'] = ret_base
ok = 0.30 <= res_base.test_sh <= 0.50 and 1.0 <= res_base.full_sharpe <= 1.4 \
    and 0.20 <= res_base.mc_p_dd25 <= 0.45
print(f"\n  Replication: TEST Sharpe {res_base.test_sh:.2f} (expect ~0.39-0.41), "
      f"FULL {res_base.full_sharpe:.2f} (expect ~1.1-1.3), "
      f"MC tail {res_base.mc_p_dd25*100:.0f}% (expect 28-38%) -> {'OK' if ok else 'MISMATCH — STOP'}")
if not ok:
    sys.exit('Baseline replication failed; aborting before variant evaluation.')

if RUN_GK:
    print('\n[4] Trial #97 — Garman-Klass 30d')
    W97 = basket_weights(dfs, rv_gk, SYMS2)
    ret97 = net_from_weights(W97, closes2)
    results['gk'] = full_validation(ret97, 'TRIAL #97: GK30 sizing', net_from_weights(W97, closes2, fee=FEE_STRESS))
    rets['gk'] = ret97
else:
    print('\n[4] Trial #97 (GK30) NOT RUN — failed sanity gate; zero-trial stop per spec.')

if RUN_EWMA:
    print('\n[5] Trial #98 — EWMA lambda=0.94')
    W98 = basket_weights(dfs, rv_ewma, SYMS2)
    ret98 = net_from_weights(W98, closes2)
    results['ewma'] = full_validation(ret98, 'TRIAL #98: EWMA(0.94) sizing', net_from_weights(W98, closes2, fee=FEE_STRESS))
    rets['ewma'] = ret98
else:
    print('\n[5] Trial #98 (EWMA) NOT RUN — failed sanity gate; zero-trial stop per spec.')

active = [t for t, k, run in [('GK30', 'gk', RUN_GK), ('EWMA', 'ewma', RUN_EWMA)] if run]

print('\n[6] Sizing-difference diagnostics (how different are the estimators in practice?)')
for tag, rv_fn in [t for t in [('GK30', rv_gk), ('EWMA', rv_ewma)] if t[0] in active]:
    diffs, corrs = [], []
    for s in SYMS2:
        a, b = rv_cc(dfs[s]).dropna(), rv_fn(dfs[s]).dropna()
        ix = a.index.intersection(b.index)
        corrs.append(a[ix].corr(b[ix]))
        qa = quantize((VOL_TARGET / a[ix]).clip(0, 1))
        qb = quantize((VOL_TARGET / b[ix]).clip(0, 1))
        diffs.append((qa != qb).mean())
    print(f"  {tag}: rv corr with cc30 {np.mean(corrs):.3f}; "
          f"quantized scale differs on {np.mean(diffs)*100:.1f}% of bars (avg BTC/ETH)")

print('\n[7] Cross-asset transfer (single-sleeve per asset, unchanged params)')
xasset: dict[str, list] = {}
for tag, rv_fn in [t for t in [('cc30', rv_cc), ('GK30', rv_gk), ('EWMA', rv_ewma)]
                   if t[0] == 'cc30' or t[0] in active]:
    shs = []
    for s in SYMS9:
        core = core_series(dfs[s])
        rv = rv_fn(dfs[s])
        w = quantize(core * (VOL_TARGET / rv).clip(0, 1)).to_frame(s)
        r = net_from_weights(w, dfs[s][['close']].rename(columns={'close': s}))
        shs.append(m(r)[0])
    xasset[tag] = shs
    pos = sum(1 for x in shs if x > 0)
    print(f"  {tag:<5} positive {pos}/9  median {np.median(shs):.2f}  " +
          " ".join(f"{s}:{x:+.2f}" for s, x in zip(SYMS9, shs)))

print(f'\n[8] Deflated Sharpe Ratio (per-day returns, n_trials={N_TRIALS})')
dsr_out = {}
dsr_rows = [('baseline cc30', rets['base'])] + \
    [(t, rets['gk' if t == 'GK30' else 'ewma']) for t in active]
for tag, r in dsr_rows:
    res = deflated_sharpe_ratio(r.tolist(), n_trials=N_TRIALS)
    dsr_out[tag] = res['dsr']
    print(f"  {tag:<20} DSR={res['dsr']:.4f}  (skew {res['skew']:+.2f}, "
          f"kurt {res['kurtosis']:.1f}, n_obs {res['n_obs']})")

print('\n[9] GK lookback plateau sweep 20-40 (reporting-only; reported variant stays 30d)')
plateau = []
for lb in (20, 25, 30, 35, 40) if RUN_GK else ():
    Wp = basket_weights(dfs, rv_gk, SYMS2, lookback=lb)
    rp = net_from_weights(Wp, closes2)
    n = len(rp)
    sh_f, dd_f, _, _ = m(rp)
    sh_te, _, _, _ = m(rp.iloc[int(n * 0.85):])
    blocks = [g.values for _, g in rp.groupby([rp.index.year, rp.index.month])]
    rng = np.random.default_rng(11)
    dds = []
    for _ in range(MC_SIMS):
        seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        eq = np.cumprod(1 + seq)
        dds.append((eq / np.maximum.accumulate(eq) - 1).min())
    p25 = float((np.array(dds) < -0.25).mean())
    plateau.append((lb, sh_f, sh_te, dd_f, p25))
    print(f"  lb={lb:>2}: FULL Sh {sh_f:.2f}  TEST Sh {sh_te:.2f}  DD {dd_f*100:.1f}%  MC tail {p25*100:.1f}%")
if plateau:
    avg = np.mean([[p[1], p[2], p[4]] for p in plateau], axis=0)
    print(f"  AVERAGE of all sweep runs (Kaufman convention): FULL Sh {avg[0]:.2f}  "
          f"TEST Sh {avg[1]:.2f}  MC tail {avg[2]*100:.1f}%")
else:
    print('  (skipped — GK30 not run)')

print('\n[10] Champion historical portfolio-level realized vol (for reconciliation write-up)')
r = rets['base']
full_vol = r.std() * np.sqrt(ANN)
inmkt = r[W.shift(2).reindex(r.index).fillna(0).sum(axis=1) > 0]
inmkt_vol = inmkt.std() * np.sqrt(ANN)
roll30 = r.rolling(30).std() * np.sqrt(ANN)
print(f"  full-period realized vol (incl. flat days): {full_vol*100:.1f}% ann")
print(f"  in-market-days-only realized vol:           {inmkt_vol*100:.1f}% ann "
      f"({len(inmkt)}/{len(r)} days in market)")
print(f"  rolling 30d vol: median {roll30.median()*100:.1f}%, p90 {roll30.quantile(0.9)*100:.1f}%, "
      f"max {roll30.max()*100:.1f}%")

print('\n[11] Promotion-criteria scorecard (all must hold)')
for tag, key in [t for t in [('GK30', 'gk'), ('EWMA', 'ewma')] if t[0] in active]:
    v, b = results[key], results['base']
    c1 = v.mc_p_dd25 <= 0.20
    c2 = v.test_sh >= 0.35
    flipped = any(bb > 0 and vv < -0.05 for bb, vv in zip(b.wf_rets, v.wf_rets))
    c3 = abs(v.full_sharpe - b.full_sharpe) <= 0.10 and not flipped
    c4 = sum(1 for x in xasset[tag] if x > 0) >= 8
    c5 = dsr_out[tag] >= dsr_out['baseline cc30']
    print(f"  TRIAL {tag}:")
    print(f"    1 MC tail <=20%:        {'PASS' if c1 else 'FAIL'} ({v.mc_p_dd25*100:.1f}% vs baseline {b.mc_p_dd25*100:.1f}%)")
    print(f"    2 TEST Sharpe >=0.35:   {'PASS' if c2 else 'FAIL'} ({v.test_sh:.2f})")
    print(f"    3 FULL within 0.10, no WF flip: {'PASS' if c3 else 'FAIL'} "
          f"(delta {v.full_sharpe - b.full_sharpe:+.2f}, flip={flipped})")
    print(f"    4 cross-asset >=8/9:    {'PASS' if c4 else 'FAIL'}")
    print(f"    5 DSR >= baseline:      {'PASS' if c5 else 'FAIL'}")
    print(f"    -> {'ALL PASS (promote per criteria + plateau)' if all([c1, c2, c3, c4, c5]) else 'REJECT'}")
