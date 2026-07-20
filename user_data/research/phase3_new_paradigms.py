"""
Phase 3: untested paradigms + overlays.

A) Calendar effects: day-of-week, turn-of-month (never tested in this project)
B) Halving-cycle regime (BTC-specific structural feature)
C) Dual momentum (absolute + relative, Antonacci-style)
D) Vol-target overlay on the robust ens3 core (DD-reduction lever)
E) Drawdown-control overlay (cut size after equity DD breach)
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
import numpy as np
import pandas as pd
from validator import load, signal_to_returns

def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()

btc = load('BTC/USDT', '1d')
eth = load('ETH/USDT', '1d')
c = btc['close']


def perf(ret, label):
    ret = ret.dropna()
    eq = (1 + ret).cumprod()
    n_years = len(ret) / 365
    cagr = eq.iloc[-1] ** (1 / n_years) - 1 if eq.iloc[-1] > 0 else -1
    sharpe = ret.mean() / ret.std() * np.sqrt(365) if ret.std() > 0 else 0
    dd = (eq / eq.cummax() - 1).min()
    yearly = (1 + ret).groupby(ret.index.year).prod() - 1
    pos = (yearly > 0).sum()
    print(f"{label:36s} CAGR {cagr*100:+6.1f}%  Sharpe {sharpe:5.2f}  DD {dd*100:6.1f}%  posyrs {pos}/{len(yearly)}")
    return sharpe, dd


print("=" * 78)
print("A) CALENDAR EFFECTS (raw stats — mean daily return by weekday, 2018-2026)")
print("=" * 78)
dret = c.pct_change()
by_dow = dret.groupby(dret.index.dayofweek).agg(['mean', 'std', 'count'])
by_dow.index = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
by_dow['t_stat'] = by_dow['mean'] / (by_dow['std'] / np.sqrt(by_dow['count']))
print((by_dow[['mean', 't_stat', 'count']].assign(mean=lambda x: (x['mean']*100).round(3))).to_string())
print()
# Also by half of period to check stability
half = len(dret) // 2
for label, sl in [("first half", dret.iloc[:half]), ("second half", dret.iloc[half:])]:
    bd = sl.groupby(sl.index.dayofweek).mean() * 100
    print(f"  {label}: " + " ".join(f"{d}:{v:+.3f}%" for d, v in zip(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], bd)))

print()
print("Turn-of-month (last 2 + first 3 trading days):")
dom = dret.index.day
eom = dret.index.days_in_month
is_tom = (dom <= 3) | (dom >= eom - 1)
print(f"  TOM days mean: {dret[is_tom].mean()*100:+.3f}%/d (n={is_tom.sum()})  "
      f"non-TOM: {dret[~is_tom].mean()*100:+.3f}%/d (n={(~is_tom).sum()})")

print()
print("=" * 78)
print("B) HALVING-CYCLE REGIME")
print("=" * 78)
halvings = pd.to_datetime(['2016-07-09', '2020-05-11', '2024-04-19'], utc=True)
days_since = pd.Series(index=c.index, dtype=float)
for d in c.index:
    past = [h for h in halvings if h <= d]
    days_since[d] = (d - max(past)).days if past else np.nan
# mean daily ret by month-since-halving bucket
bucket = (days_since // 90).rename('q_since_halving')  # quarters since halving
stats = dret.groupby(bucket).agg(['mean', 'count'])
print("Mean daily return by QUARTER since halving (0 = first 90d after):")
for q, row in stats.iterrows():
    if not np.isnan(q) and row['count'] > 30:
        print(f"  Q{int(q):2d}: {row['mean']*100:+.3f}%/d  (n={int(row['count'])})")

# Strategy: long during quarters 1-6 after halving only (the classic bull window)
sig_halving = ((days_since >= 90) & (days_since <= 540)).astype(float)
r = signal_to_returns(btc, sig_halving)
perf(r['ret_net'], "halving_window_90_540d")
sig_halving2 = ((days_since >= 0) & (days_since <= 540)).astype(float)
r = signal_to_returns(btc, sig_halving2)
perf(r['ret_net'], "halving_window_0_540d")

print()
print("=" * 78)
print("C) DUAL MOMENTUM (BTC vs ETH vs cash, monthly-ish rebal)")
print("=" * 78)
common_start = max(btc.index.min(), eth.index.min())
b = btc.loc[common_start:]; e = eth.loc[common_start:]
idx = b.index.intersection(e.index)
pb, pe = b['close'].reindex(idx), e['close'].reindex(idx)
for lb in [30, 60, 90]:
    mb = pb.pct_change(lb); me = pe.pct_change(lb)
    # signals per asset
    sig_b = pd.Series(0.0, index=idx); sig_e = pd.Series(0.0, index=idx)
    pick_b = (mb >= me) & (mb > 0)
    pick_e = (me > mb) & (me > 0)
    sig_b[pick_b] = 1.0; sig_e[pick_e] = 1.0
    rb = signal_to_returns(b.reindex(idx), sig_b)['ret_net']
    re = signal_to_returns(e.reindex(idx), sig_e)['ret_net']
    perf(rb + re, f"dual_momentum_{lb}d")

print()
print("=" * 78)
print("D) VOL-TARGET OVERLAY on ens3 core")
print("=" * 78)
s1 = (c > _sma(c, 200)).astype(float)
s2 = (c.pct_change(30) > 0).astype(float)
s3 = (_ema(c, 20) > _ema(c, 50)).astype(float)
ens3 = ((s1 + s2 + s3) >= 3).astype(float)

r_base = signal_to_returns(btc, ens3)
perf(r_base['ret_net'], "ens3 (no overlay)")

rv = dret.rolling(30).std() * np.sqrt(365)
for tv in [0.30, 0.40, 0.50, 0.60]:
    scale = (tv / rv).clip(0, 1)
    sig = ens3 * scale
    r = signal_to_returns(btc, sig)
    perf(r['ret_net'], f"ens3 + voltarget {int(tv*100)}%")

print()
print("=" * 78)
print("E) DD-CONTROL OVERLAY on ens3 (halve size when strategy equity in >15% DD)")
print("=" * 78)
ret_base = r_base['ret_net']
eq = (1 + ret_base).cumprod()
in_dd = (eq / eq.cummax() - 1) < -0.15
# apply next-day (no lookahead): scale tomorrow's position by 0.5 if in DD today
scale_dd = pd.Series(1.0, index=btc.index)
scale_dd[in_dd.shift(1).fillna(False)] = 0.5
sig_ddctl = ens3 * scale_dd
r = signal_to_returns(btc, sig_ddctl)
perf(r['ret_net'], "ens3 + ddcontrol(15%,x0.5)")

print()
print("=" * 78)
print("F) COMBINED: ens3 + voltarget + ETH version + 50/50 blend")
print("=" * 78)
# ens3 on ETH
ce = e['close']
s1e = (ce > _sma(ce, 200)).astype(float)
s2e = (ce.pct_change(30) > 0).astype(float)
s3e = (_ema(ce, 20) > _ema(ce, 50)).astype(float)
ens3_eth = ((s1e + s2e + s3e) >= 3).astype(float)
dret_e = ce.pct_change()
rv_e = dret_e.rolling(30).std() * np.sqrt(365)

for tv in [0.40, 0.50]:
    scale_b = (tv / rv).clip(0, 1)
    scale_e = (tv / rv_e).clip(0, 1)
    sig_b2 = (ens3 * scale_b).reindex(idx).fillna(0)
    sig_e2 = (ens3_eth * scale_e).reindex(idx).fillna(0)
    rb = signal_to_returns(b.reindex(idx), sig_b2 * 0.5)['ret_net']
    re = signal_to_returns(e.reindex(idx), sig_e2 * 0.5)['ret_net']
    perf(rb + re, f"ens3_BTC+ETH 50/50 voltarget {int(tv*100)}%")
