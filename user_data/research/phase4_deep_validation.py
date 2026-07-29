"""
Phase 4: Deep validation of the final candidate.

CANDIDATE "TrendVolTarget" :=
  Per asset (BTC, ETH):
    core = (close > SMA200) AND (ROC30 > 0) AND (EMA20 > EMA50)   [ens3, plateau-robust]
    scale = clip(0.40 / realized_vol_30d_annualized, 0, 1)         [vol targeting]
    position = core * scale * 0.5                                  [50/50 split]

Validation battery:
  1. Yearly breakdown + benchmarks (BTC HODL, 50/50 HODL, vol-target HODL, ens3 no overlay)
  2. 70/15/15 train/val/test (params were chosen on plateau, never tuned to test)
  3. Walk-forward 4 windows
  4. Monte Carlo with extra slippage
  5. Turnover + fee accounting
  6. Quantized sizing (0/0.25/0.5/0.75/1 steps) — implementability check
  7. Vol-target parameter plateau check (already partially done in phase 3)
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from validator import load

# FROZEN HISTORICAL COST — do not re-point at COST_MODEL. This one-shot script is
# the reproduction record of a June-2026 run made under the old 0.10% commission +
# 0.05% slippage per-side model. Changing it would silently invalidate the archived
# numbers. New work must use validator.per_side_cost() (see COST_MODEL).
FEE = 0.0015

def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()

btc = load('BTC/USDT', '1d')
eth = load('ETH/USDT', '1d')
common_start = max(btc.index.min(), eth.index.min())
b = btc.loc[common_start:]; e = eth.loc[common_start:]
idx = b.index.intersection(e.index)
b = b.reindex(idx); e = e.reindex(idx)


def ens3_sig(close):
    s1 = (close > _sma(close, 200)).astype(float)
    s2 = (close.pct_change(30) > 0).astype(float)
    s3 = (_ema(close, 20) > _ema(close, 50)).astype(float)
    return ((s1 + s2 + s3) >= 3).astype(float)


def vt_scale(close, tv=0.40, n=30):
    rv = close.pct_change().rolling(n).std() * np.sqrt(365)
    return (tv / rv).clip(0, 1)


def strat_returns(dfs: dict, tv=0.40, quantize=None, fee=FEE):
    """Returns net daily portfolio returns for the candidate."""
    total_ret = None
    total_turnover = None
    for sym, df in dfs.items():
        close = df['close']
        sig = ens3_sig(close) * vt_scale(close, tv)
        if quantize:
            sig = (sig / quantize).round() * quantize
        sig = sig.clip(0, 1) * (1.0 / len(dfs))
        pos = sig.shift(2).fillna(0)
        bar_ret = close.pct_change().fillna(0)
        gross = pos * bar_ret
        turn = pos.diff().abs().fillna(pos.abs())
        net = gross - turn * fee
        total_ret = net if total_ret is None else total_ret + net
        total_turnover = turn if total_turnover is None else total_turnover + turn
    return total_ret, total_turnover


def perf(ret, label, show_yearly=True):
    ret = ret.dropna()
    eq = (1 + ret).cumprod()
    n_years = len(ret) / 365
    cagr = eq.iloc[-1] ** (1 / n_years) - 1 if eq.iloc[-1] > 0 else -1
    sharpe = ret.mean() / ret.std() * np.sqrt(365) if ret.std() > 0 else 0
    dn = ret[ret < 0].std()
    sortino = ret.mean() / dn * np.sqrt(365) if dn > 0 else 0
    dd = (eq / eq.cummax() - 1).min()
    yearly = (1 + ret).groupby(ret.index.year).prod() - 1
    pos = (yearly > 0).sum()
    line = (f"{label:34s} CAGR {cagr*100:+6.1f}%  Sharpe {sharpe:5.2f}  Sortino {sortino:5.2f}  "
            f"DD {dd*100:6.1f}%  posyrs {pos}/{len(yearly)}")
    print(line)
    if show_yearly:
        print(" " * 4 + " ".join(f"{y}:{v*100:+.0f}%" for y, v in yearly.items()))
    return {"cagr": cagr, "sharpe": sharpe, "dd": dd, "yearly": yearly}


dfs = {"BTC": b, "ETH": e}

print("=" * 90)
print("1) CANDIDATE vs BENCHMARKS  (window 2019-12 .. 2026-05, 6.5y)")
print("=" * 90)
cand_ret, cand_turn = strat_returns(dfs, tv=0.40)
m_cand = perf(cand_ret, "TrendVolTarget (candidate)")

# benchmarks
hodl_btc = b['close'].pct_change().fillna(0)
perf(hodl_btc, "BTC HODL")
hodl5050 = (b['close'].pct_change().fillna(0) + e['close'].pct_change().fillna(0)) / 2
perf(hodl5050, "50/50 BTC-ETH HODL (daily rebal)")
# vol-target HODL (no trend filter) — isolates the trend filter's contribution
vt_only = None
for sym, df in dfs.items():
    close = df['close']
    sig = vt_scale(close, 0.40).clip(0, 1) * 0.5
    pos = sig.shift(2).fillna(0)
    net = pos * close.pct_change().fillna(0) - pos.diff().abs().fillna(pos.abs()) * FEE
    vt_only = net if vt_only is None else vt_only + net
perf(vt_only, "VolTarget HODL (no trend filter)")
# trend only, no vol target
trend_only = None
for sym, df in dfs.items():
    close = df['close']
    sig = ens3_sig(close) * 0.5
    pos = sig.shift(2).fillna(0)
    net = pos * close.pct_change().fillna(0) - pos.diff().abs().fillna(pos.abs()) * FEE
    trend_only = net if trend_only is None else trend_only + net
perf(trend_only, "Trend only (no vol target)")

print()
print("=" * 90)
print("2) TRAIN / VAL / TEST  (70/15/15 chronological)")
print("=" * 90)
n = len(cand_ret)
i1, i2 = int(n * 0.70), int(n * 0.85)
perf(cand_ret.iloc[:i1], "TRAIN (70%)")
perf(cand_ret.iloc[i1:i2], "VAL (15%)")
perf(cand_ret.iloc[i2:], "TEST (15%, untouched)")

print()
print("=" * 90)
print("3) WALK-FORWARD (4 expanding-anchor OOS windows)")
print("=" * 90)
for k in range(1, 5):
    s_i = int(n * (0.5 + (k - 1) * 0.125))
    e_i = min(int(n * (0.5 + k * 0.125)), n)
    sub = cand_ret.iloc[s_i:e_i]
    perf(sub, f"WF window {k} ({sub.index[0].date()}..{sub.index[-1].date()})", show_yearly=False)

print()
print("=" * 90)
print("4) MONTE CARLO (1000 sims: shuffle monthly blocks + extra 0.05% slippage/turnover)")
print("=" * 90)
# Block-shuffle months to preserve intra-month autocorrelation
monthly_groups = [g for _, g in cand_ret.groupby([cand_ret.index.year, cand_ret.index.month])]
rng = np.random.default_rng(7)
sharpes, dds, cagrs = [], [], []
extra_cost_per_day = (cand_turn * 0.0005)
ret_stressed = cand_ret - extra_cost_per_day
monthly_stressed = [g for _, g in ret_stressed.groupby([ret_stressed.index.year, ret_stressed.index.month])]
for _ in range(1000):
    order = rng.permutation(len(monthly_stressed))
    seq = np.concatenate([monthly_stressed[i].values for i in order])
    eq = np.cumprod(1 + seq)
    yrs = len(seq) / 365
    cagrs.append(eq[-1] ** (1 / yrs) - 1)
    sharpes.append(seq.mean() / seq.std() * np.sqrt(365))
    peak = np.maximum.accumulate(eq)
    dds.append((eq / peak - 1).min())
print(f"  Sharpe: p5 {np.percentile(sharpes, 5):.2f}  p50 {np.percentile(sharpes, 50):.2f}  p95 {np.percentile(sharpes, 95):.2f}")
print(f"  CAGR:   p5 {np.percentile(cagrs, 5)*100:+.1f}%  p50 {np.percentile(cagrs, 50)*100:+.1f}%")
print(f"  MaxDD:  p5 (worst) {np.percentile(dds, 5)*100:.1f}%  p50 {np.percentile(dds, 50)*100:.1f}%  p95 (best) {np.percentile(dds, 95)*100:.1f}%")
print(f"  P(DD worse than -25%): {(np.array(dds) < -0.25).mean()*100:.1f}%")
print(f"  P(Sharpe < 0): {(np.array(sharpes) < 0).mean()*100:.1f}%")

print()
print("=" * 90)
print("5) TURNOVER & FEES")
print("=" * 90)
ann_turn = cand_turn.mean() * 365
print(f"  Mean daily turnover: {cand_turn.mean()*100:.2f}% of equity  (~{ann_turn:.1f}x equity per year)")
print(f"  Annual fee drag at 0.15%/side: {ann_turn * FEE * 100:.2f}% of equity")

print()
print("=" * 90)
print("6) QUANTIZED SIZING (0.25 steps — implementable in freqtrade via position adjustments)")
print("=" * 90)
for q in [None, 0.25, 0.5]:
    r, t = strat_returns(dfs, tv=0.40, quantize=q)
    label = f"quantize={q}" if q else "continuous (reference)"
    perf(r, label, show_yearly=False)

print()
print("=" * 90)
print("7) VOL-TARGET PLATEAU (tv sweep, quantized 0.25)")
print("=" * 90)
for tv in [0.30, 0.35, 0.40, 0.45, 0.50]:
    r, t = strat_returns(dfs, tv=tv, quantize=0.25)
    perf(r, f"tv={int(tv*100)}%", show_yearly=False)

print()
print("=" * 90)
print("8) SMA/ROC PLATEAU re-check ON THE FULL CONSTRUCT (quantized, tv=40%)")
print("=" * 90)
def strat_returns_params(dfs, sma_n, roc_n, tv=0.40, quantize=0.25, fee=FEE):
    total = None
    for sym, df in dfs.items():
        close = df['close']
        s1 = (close > _sma(close, sma_n)).astype(float)
        s2 = (close.pct_change(roc_n) > 0).astype(float)
        s3 = (_ema(close, 20) > _ema(close, 50)).astype(float)
        core = ((s1 + s2 + s3) >= 3).astype(float)
        sig = core * vt_scale(close, tv)
        sig = (sig / quantize).round() * quantize
        sig = sig.clip(0, 1) * 0.5
        pos = sig.shift(2).fillna(0)
        net = pos * close.pct_change().fillna(0) - pos.diff().abs().fillna(pos.abs()) * fee
        total = net if total is None else total + net
    return total

for sma_n in [150, 200, 250]:
    for roc_n in [20, 30, 40]:
        r = strat_returns_params(dfs, sma_n, roc_n)
        ret = r.dropna()
        eq = (1 + ret).cumprod()
        sh = ret.mean() / ret.std() * np.sqrt(365)
        dd = (eq / eq.cummax() - 1).min()
        cagr = eq.iloc[-1] ** (365 / len(ret)) - 1
        print(f"  sma={sma_n} roc={roc_n}: Sharpe {sh:5.2f}  DD {dd*100:6.1f}%  CAGR {cagr*100:+6.1f}%")
