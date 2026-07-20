"""
Phase 18: H-CointPair — formal BTC-ETH cointegration pairs trading (would-be trial #98).

PRE-REGISTERED experiment. Spec locked in SESSION_2026-07-10_COINTPAIR.md section 1
BEFORE this script was written or produced any numbers. Assignment: research/NEXT_TASK.md
(2026-07-10, Research Director cycle #6).

Order of operations (per pre-registration):
  [1] Pre-gate 1 — stationarity / cointegration census (zero n_trials).
      Stop rule (ALL required): full-window EG p<0.05 (either direction) AND
      Johansen trace(r=0) > 95% cv AND >=60% of rolling 730-bar/91-step windows pass
      EG p<0.05 AND causal-spread OU half-life in [3, 60] days.
      Post-2024 EG sub-window reported as a regime-break flag either way.
      Secondary spot window (2019-12 -> 2026-05): same battery, REPORTING ONLY.
  [2] Pre-gate 2 — fee-hurdle amplitude census on the CAUSAL spread (zero n_trials).
      Stop rule (ALL required): median per-episode gross capture >= 1.80%
      (3 x 0.60% two-leg round-trip cost) AND episode count >= 40 AND
      aggregate gross - 0.60% x count > 0.
  [3] TRIAL #98 (ONLY if both pre-gates pass): the single pre-registered
      dollar-neutral construction; full validation stack; DSR at n_trials=98.

Statistical constructions (all pre-declared):
  - Causal hedge ratio: rolling OLS log(ETH) ~ log(BTC), 365 bars, shifted 1 bar.
  - Full-window OLS spread: DIAGNOSTIC ONLY (inside stationarity tests) — never
    feeds a trading decision.
  - OU half-life: regress d(z) on z.shift(1)-mean(z); HL = ln(2)/theta.
  - Causal z-score: rolling mean/std over L_z = clip(round(3*HL), 20, 180), shift 1.

Pipeline conventions identical to phase13-16: futures feathers, 2-bar signal lag,
fees 0.15%/side per leg, 70/15/15 split, monthly-block MC (1,000 sims, seed 11),
DSR from freqtrade_dsr.py, wf_window_stability/family_context from validator.py.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')

import math
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen

from freqtrade_dsr import deflated_sharpe_ratio          # AGPL module, repo root
from validator import wf_window_stability, family_from_results_dir, family_context

FEE = 0.0015            # per side per leg (bundles 0.10% commission + 0.05% slippage)
RT_COST = 4 * FEE       # 4 legs per round trip on the $1-per-leg census convention
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
SPOT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx')

HEDGE_WIN = 365         # rolling OLS hedge window (pre-declared)
ROLL_WIN = 730          # rolling EG window (pre-declared)
ROLL_STEP = 91          # rolling EG step (pre-declared)
Z_ENTRY, Z_EXIT, Z_BLOWOUT = 2.0, 0.5, 4.0
HL_BAND = (3.0, 60.0)   # tradeable OU half-life band, days (pre-declared)
MEDIAN_CAPTURE_BAR = 3 * RT_COST   # = 1.80%
EPISODE_FLOOR = 40
ROLL_PASS_FRAC = 0.60
N_TRIALS = 98
MC_SIMS = 1000
ANN = 365


# ---------------------------------------------------------------- data
def load_fut(sym):
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index()['close'].astype(float)


def load_spot(sym):
    df = pd.read_feather(SPOT_DIR / f'{sym}_USDT-1d.feather')
    return df.set_index('date').sort_index()['close'].astype(float)


# ---------------------------------------------------------------- statistics
def eg_pvalues(ly, lx):
    """Engle-Granger p-values in both normalization directions (trend='c', aic)."""
    p_yx = coint(ly.values, lx.values, trend='c', autolag='aic')[1]
    p_xy = coint(lx.values, ly.values, trend='c', autolag='aic')[1]
    return float(p_yx), float(p_xy)


def johansen_trace_r0(ly, lx):
    """Johansen trace statistic for r=0 and its 95% critical value."""
    mat = np.column_stack([ly.values, lx.values])
    res = coint_johansen(mat, det_order=0, k_ar_diff=1)
    return float(res.lr1[0]), float(res.cvt[0, 1])   # cvt columns: 90/95/99


def rolling_hedge(ly, lx, win=HEDGE_WIN):
    """Rolling OLS ly = a + b*lx over `win` bars, coefficients shifted 1 bar (causal)."""
    mx = lx.rolling(win).mean()
    my = ly.rolling(win).mean()
    cov = (lx * ly).rolling(win).mean() - mx * my
    var = (lx * lx).rolling(win).mean() - mx * mx
    beta = (cov / var).shift(1)
    alpha = (my - (cov / var) * mx).shift(1)
    return alpha, beta


def ou_half_life(z):
    """OU half-life in bars: regress dz on (z[t-1] - mean(z)); HL = ln2/theta."""
    z = z.dropna()
    dz = z.diff().dropna()
    zl = (z.shift(1) - z.mean()).dropna()
    ix = dz.index.intersection(zl.index)
    x, y = zl[ix].values, dz[ix].values
    slope = np.dot(x - x.mean(), y - y.mean()) / np.dot(x - x.mean(), x - x.mean())
    if slope >= 0:
        return float('inf')
    return float(-math.log(2) / slope)


def sharpe(ret):
    ret = ret.dropna()
    return float(ret.mean() / ret.std() * np.sqrt(ANN)) if len(ret) > 10 and ret.std() > 0 else 0.0


def max_dd(ret):
    eq = (1 + ret.dropna()).cumprod()
    return float((eq / eq.cummax() - 1).min()) if len(eq) else 0.0


# ================================================================= [0] data
print('=' * 78)
print('PHASE 18 — H-CointPair: formal BTC-ETH cointegration pairs (would-be trial #98)')
print('  pre-registered in SESSION_2026-07-10_COINTPAIR.md before any results')
print('=' * 78)

fb, fe = load_fut('BTC'), load_fut('ETH')
fut = pd.DataFrame({'BTC': fb, 'ETH': fe}).dropna()
sb, se = load_spot('BTC'), load_spot('ETH')
spot = pd.DataFrame({'BTC': sb, 'ETH': se}).dropna()
print(f"\n[0] Harness window (futures, inner join): {fut.index[0].date()} -> "
      f"{fut.index[-1].date()}  ({len(fut)} bars)")
print(f"    Secondary window (spot, inner join):  {spot.index[0].date()} -> "
      f"{spot.index[-1].date()}  ({len(spot)} bars)")
print("    NOTE (pre-registered honesty): common spot coverage starts 2019-12 "
      "(ETH feather), NOT ~2017-18 as the assignment hoped; 2018 bear unreachable.")

lB_f, lE_f = np.log(fut['BTC']), np.log(fut['ETH'])
lB_s, lE_s = np.log(spot['BTC']), np.log(spot['ETH'])

# ================================================================= [1] pre-gate 1
print('\n[1] PRE-GATE 1 — stationarity / cointegration census (zero n_trials)')

p_eb_f, p_be_f = eg_pvalues(lE_f, lB_f)
print(f"  EG full harness window: p(ETH~BTC) = {p_eb_f:.4f}   p(BTC~ETH) = {p_be_f:.4f}"
      f"   -> min {min(p_eb_f, p_be_f):.4f} (need < 0.05)")
tr_f, cv_f = johansen_trace_r0(lE_f, lB_f)
print(f"  Johansen full harness window: trace(r=0) = {tr_f:.2f}  vs 95% cv = {cv_f:.2f}"
      f"  ({'PASS' if tr_f > cv_f else 'fail'})")

# rolling EG census
rows = []
i = 0
while i + ROLL_WIN <= len(fut):
    w = fut.index[i:i + ROLL_WIN]
    ly, lx = lE_f[w], lB_f[w]
    p1, p2 = eg_pvalues(ly, lx)
    rows.append({'start': w[0].date(), 'end': w[-1].date(),
                 'p_eth_btc': p1, 'p_btc_eth': p2, 'pass': min(p1, p2) < 0.05})
    i += ROLL_STEP
roll = pd.DataFrame(rows)
n_pass = int(roll['pass'].sum())
frac = n_pass / len(roll) if len(roll) else 0.0
print(f"\n  Rolling EG ({ROLL_WIN}-bar windows, step {ROLL_STEP}): "
      f"{n_pass}/{len(roll)} pass p<0.05 ({frac*100:.0f}%; need >= {ROLL_PASS_FRAC*100:.0f}%)")
for r in rows:
    print(f"    {r['start']} -> {r['end']}: p(E~B) {r['p_eth_btc']:.3f}  "
          f"p(B~E) {r['p_btc_eth']:.3f}  {'PASS' if r['pass'] else '-'}")

# post-2024 regime-break flag
mask24 = fut.index >= '2024-01-01'
p1_24, p2_24 = eg_pvalues(lE_f[mask24], lB_f[mask24])
flag_24 = min(p1_24, p2_24) >= 0.05
print(f"\n  Post-2024 sub-window EG ({fut.index[mask24][0].date()} -> end, "
      f"{int(mask24.sum())} bars): p(E~B) {p1_24:.4f}  p(B~E) {p2_24:.4f}"
      f"  -> REGIME-BREAK FLAG: {'RAISED' if flag_24 else 'not raised'}")

# causal spread + OU half-life (harness)
alpha, beta = rolling_hedge(lE_f, lB_f)
z_raw = (lE_f - alpha - beta * lB_f).dropna()
hl_causal = ou_half_life(z_raw)
print(f"\n  Causal hedge ratio (365d rolling OLS, shift 1): spread starts "
      f"{z_raw.index[0].date()} ({len(z_raw)} bars); beta last {beta.dropna().iloc[-1]:.3f}, "
      f"range [{beta.min():.3f}, {beta.max():.3f}]")
print(f"  OU half-life, CAUSAL spread (harness): "
      f"{'inf (no mean reversion: theta >= 0)' if math.isinf(hl_causal) else f'{hl_causal:.1f} days'}"
      f"   (band: {HL_BAND[0]:.0f}-{HL_BAND[1]:.0f})")

# full-window-fit spread half-life (diagnostic only)
b_full = np.dot(lB_f - lB_f.mean(), lE_f - lE_f.mean()) / np.dot(lB_f - lB_f.mean(), lB_f - lB_f.mean())
z_full = lE_f - (lE_f.mean() - b_full * lB_f.mean()) - b_full * lB_f
hl_full = ou_half_life(z_full)
print(f"  OU half-life, full-window-fit spread (DIAGNOSTIC ONLY): "
      f"{'inf' if math.isinf(hl_full) else f'{hl_full:.1f} days'}  (full-window beta {b_full:.3f})")

# secondary spot window battery (reporting only)
print('\n  Secondary spot window (REPORTING ONLY, not in the stop rule):')
p_eb_s, p_be_s = eg_pvalues(lE_s, lB_s)
tr_s, cv_s = johansen_trace_r0(lE_s, lB_s)
print(f"    EG: p(E~B) {p_eb_s:.4f}  p(B~E) {p_be_s:.4f}   "
      f"Johansen trace(r=0) {tr_s:.2f} vs 95% cv {cv_s:.2f}")
rows_s = []
i = 0
while i + ROLL_WIN <= len(spot):
    w = spot.index[i:i + ROLL_WIN]
    p1, p2 = eg_pvalues(lE_s[w], lB_s[w])
    rows_s.append(min(p1, p2) < 0.05)
    i += ROLL_STEP
print(f"    Rolling EG: {sum(rows_s)}/{len(rows_s)} windows pass p<0.05")

# ---- stop rule
c1a = min(p_eb_f, p_be_f) < 0.05
c1b = tr_f > cv_f
c1c = frac >= ROLL_PASS_FRAC
c1d = HL_BAND[0] <= hl_causal <= HL_BAND[1]
print('\n  PRE-GATE 1 STOP-RULE SCORECARD (ALL required):')
print(f"    (1a) full-window EG p < 0.05 (either dir):        {'PASS' if c1a else 'FAIL'}"
      f"  (min p = {min(p_eb_f, p_be_f):.4f})")
print(f"    (1b) Johansen trace(r=0) > 95% cv:                {'PASS' if c1b else 'FAIL'}"
      f"  ({tr_f:.2f} vs {cv_f:.2f})")
print(f"    (1c) >= 60% rolling windows pass:                 {'PASS' if c1c else 'FAIL'}"
      f"  ({frac*100:.0f}%)")
print(f"    (1d) causal OU half-life in [3, 60] days:         {'PASS' if c1d else 'FAIL'}"
      f"  ({'inf' if math.isinf(hl_causal) else f'{hl_causal:.1f}'})")
print(f"    post-2024 regime-break flag: {'RAISED' if flag_24 else 'not raised'} (reported either way)")
gate1 = c1a and c1b and c1c and c1d
print(f"\n  PRE-GATE 1: {'PASS' if gate1 else 'FAIL -> STOP. Zero trials spent (n_trials stays 97).'}")

if not gate1:
    sys.exit('\nPRE-GATE 1 FAILURE — no mean-reverting object exists to trade. '
             'No trading rule was tested. Direction closed per NEXT_TASK.')

# ================================================================= [2] pre-gate 2
print('\n[2] PRE-GATE 2 — fee-hurdle amplitude census (zero n_trials)')
L_z = int(np.clip(round(3 * hl_causal), 20, 180))
t_stop = math.ceil(3 * hl_causal)
mu = z_raw.rolling(L_z).mean().shift(1)
sd = z_raw.rolling(L_z).std().shift(1)
z = ((z_raw - mu) / sd).dropna()
print(f"  L_z = clip(round(3 x {hl_causal:.1f}), 20, 180) = {L_z} bars;  "
      f"time-stop = ceil(3 x HL) = {t_stop} bars")

rB = fut['BTC'].pct_change()
rE = fut['ETH'].pct_change()

episodes = []
zi = z.values
zidx = z.index
i = 1
while i < len(zi):
    if abs(zi[i]) > Z_ENTRY and abs(zi[i - 1]) <= Z_ENTRY:
        s = -np.sign(zi[i])          # s=+1: long ETH / short BTC (z low -> ETH cheap)
        # find exit
        u = None
        for j in range(i + 1, min(i + t_stop + 1, len(zi))):
            if abs(zi[j]) < Z_EXIT:
                u = j
                break
        if u is None:
            u = min(i + t_stop, len(zi) - 1)
        # census pricing convention: 1-bar lag, close[t+1] -> close[u+1]
        t_e = zidx[min(i + 1, len(zi) - 1)]
        t_x = zidx[min(u + 1, len(zi) - 1)]
        if t_x > t_e:
            gE = fut['ETH'][t_x] / fut['ETH'][t_e] - 1
            gB = fut['BTC'][t_x] / fut['BTC'][t_e] - 1
            gross = s * (gE - gB)    # $1 per leg, buy-and-hold legs
            episodes.append({'entry': zidx[i].date(), 'exit': zidx[u].date(),
                             'dir': int(s), 'bars': u - i, 'gross': gross,
                             'timestop': abs(zi[u]) >= Z_EXIT})
        i = u + 1
    else:
        i += 1

eps = pd.DataFrame(episodes)
n_ep = len(eps)
if n_ep:
    med = float(eps['gross'].median())
    agg = float(eps['gross'].sum())
    print(f"\n  Episodes (|z| 2-crossing entries, exit |z|<0.5 or {t_stop}-bar time-stop, "
          f"1-bar lag pricing): n = {n_ep}")
    print(f"    gross capture per episode: median {med*100:+.2f}%  mean {eps['gross'].mean()*100:+.2f}%"
          f"  q25 {eps['gross'].quantile(.25)*100:+.2f}%  q75 {eps['gross'].quantile(.75)*100:+.2f}%")
    print(f"    best {eps['gross'].max()*100:+.2f}%  worst {eps['gross'].min()*100:+.2f}%  "
          f"positive {float((eps['gross'] > 0).mean())*100:.0f}%  "
          f"time-stopped {float(eps['timestop'].mean())*100:.0f}%")
    print(f"    episode length bars: median {eps['bars'].median():.0f}  max {eps['bars'].max()}")
    print(f"    aggregate gross {agg*100:+.2f}%  minus fee hurdle ({RT_COST*100:.2f}% x {n_ep} = "
          f"{RT_COST*n_ep*100:.2f}%) = {(agg - RT_COST*n_ep)*100:+.2f}%")
    yr = eps.assign(y=pd.to_datetime(eps['entry']).dt.year).groupby('y')['gross'].agg(['count', 'sum'])
    print('    by entry year: ' + '  '.join(f"{y}: n={int(r['count'])} sum {r['sum']*100:+.1f}%"
                                            for y, r in yr.iterrows()))
else:
    med, agg = 0.0, 0.0
    print('  ZERO episodes found.')

c2a = med >= MEDIAN_CAPTURE_BAR
c2b = n_ep >= EPISODE_FLOOR
c2c = (agg - RT_COST * n_ep) > 0
print('\n  PRE-GATE 2 STOP-RULE SCORECARD (ALL required):')
print(f"    (2a) median gross capture >= {MEDIAN_CAPTURE_BAR*100:.2f}%:  {'PASS' if c2a else 'FAIL'}"
      f"  (median {med*100:+.2f}%)")
print(f"    (2b) episode count >= {EPISODE_FLOOR}:                {'PASS' if c2b else 'FAIL'}  (n = {n_ep})")
print(f"    (2c) aggregate gross - fee hurdle > 0:      {'PASS' if c2c else 'FAIL'}"
      f"  ({(agg - RT_COST*n_ep)*100:+.2f}%)")
gate2 = c2a and c2b and c2c
print(f"\n  PRE-GATE 2: {'PASS' if gate2 else 'FAIL -> STOP. Zero trials spent (n_trials stays 97).'}")

if not gate2:
    sys.exit('\nPRE-GATE 2 FAILURE — the stationary spread exists but its excursions do not '
             'clear the two-leg fee hurdle. No trading rule was backtested. Direction closed.')

# ================================================================= [3] TRIAL #98
print('\n[3] TRIAL #98 — the single pre-registered construction (consumes n_trials 97 -> 98)')

# weights: +/-0.5 equity per leg, from causal z; blowout guard |z|>4
w_eth = pd.Series(0.0, index=z.index)
state = 0     # 0 flat, +1 long ETH/short BTC, -1 the reverse
entry_i = -1
blown = False
zi = z.values
for i in range(1, len(zi)):
    if state == 0:
        if blown:
            if abs(zi[i]) < Z_ENTRY:
                blown = False
        elif abs(zi[i]) > Z_ENTRY and abs(zi[i - 1]) <= Z_ENTRY:
            state = int(-np.sign(zi[i]))
            entry_i = i
    else:
        if abs(zi[i]) >= Z_BLOWOUT:
            state = 0
            blown = True
        elif abs(zi[i]) < Z_EXIT or (i - entry_i) >= t_stop:
            state = 0
    w_eth.iloc[i] = 0.5 * state

pos_e = w_eth.shift(2).fillna(0)          # 2-bar signal lag (harness convention)
pos_b = -pos_e
gross_ret = pos_e * rE.reindex(pos_e.index).fillna(0) + pos_b * rB.reindex(pos_b.index).fillna(0)
turn = pos_e.diff().abs().fillna(pos_e.abs()) + pos_b.diff().abs().fillna(pos_b.abs())
ret = (gross_ret - turn * FEE).dropna()

n = len(ret)
i1, i2 = int(n * 0.70), int(n * 0.85)
seg = {'FULL': ret, 'TRAIN': ret.iloc[:i1], 'VAL': ret.iloc[i1:i2], 'TEST': ret.iloc[i2:]}
for k, r in seg.items():
    eq = (1 + r).cumprod()
    print(f"  {k:<5} Sharpe {sharpe(r):5.2f}  DD {max_dd(r)*100:6.1f}%  "
          f"total {(eq.iloc[-1]-1)*100:+6.1f}%  ({len(r)} bars)")

test_idx = ret.index[i2:]
test_eps = sum(1 for e in episodes if pd.Timestamp(e['entry'], tz='UTC') >= test_idx[0])
print(f"  TEST-split episodes: {test_eps} (bar >= 10, else INCONCLUSIVE-BY-SAMPLE)")

print('\n  Calendar years:')
for y, g in ret.groupby(ret.index.year):
    print(f"    {y}: {((1+g).prod()-1)*100:+7.1f}%")

print('\n  wf_window_stability (3/4/5/6 windows on the OOS half):')
wfs = wf_window_stability(ret)
for k, v in wfs.items():
    print(f"    {k} windows: {v['windows_positive']}/{v['windows_total']} positive "
          f"(majority {'YES' if v['majority_positive'] else 'no'}); "
          f"Sharpes {v['window_sharpes']}")

blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
rng = np.random.default_rng(11)
mc_sh, mc_dd = [], []
for _ in range(MC_SIMS):
    seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
    eq = np.cumprod(1 + seq)
    mc_dd.append((eq / np.maximum.accumulate(eq) - 1).min())
    mc_sh.append(seq.mean() / seq.std() * np.sqrt(ANN) if seq.std() > 0 else 0)
mc_sh, mc_dd = np.array(mc_sh), np.array(mc_dd)
print(f"\n  Monte Carlo ({MC_SIMS} monthly-block sims, seed 11): "
      f"P(Sharpe<0) {float((mc_sh < 0).mean())*100:.1f}%  "
      f"P(DD<-25%) {float((mc_dd < -0.25).mean())*100:.1f}%  medDD {np.median(mc_dd)*100:.1f}%")
print("    (champion context: P(Sharpe<0)=0%, P(DD<-25%)~30.5%)")

dsr = deflated_sharpe_ratio(ret.tolist(), n_trials=N_TRIALS)
print(f"\n  DSR at n_trials={N_TRIALS}: {dsr['dsr']}  (skew {dsr['skew']:+.2f}, "
      f"kurt {dsr['kurtosis']:.1f}, n_obs {dsr['n_obs']})  [bar for real edge: >= 0.95]")

fam = family_from_results_dir()
fc = family_context('cointpair_trial98', sharpe(ret), sharpe(seg['TEST']), fam)
ts = fc['test_sharpe']
print(f"  family_context: TEST Sharpe mean {ts.get('mean')} / median {ts.get('median')} "
      f"/ max {ts.get('max')}; candidate {ts.get('candidate')} rank {ts.get('candidate_rank')}")

# champion correlation (same-session recompute, phase16 conventions)
def _ema(s, nn): return s.ewm(span=nn, adjust=False).mean()
champ_ret = pd.Series(0.0, index=fut.index)
for sym in ['BTC', 'ETH']:
    c = fut[sym]
    core = ((c > c.rolling(200).mean()) & (c.pct_change(30) > 0)
            & (_ema(c, 20) > _ema(c, 50))).astype(float)
    rv = c.pct_change().rolling(30).std() * np.sqrt(ANN)
    w = (((0.40 / rv).clip(0, 1) * core) / 0.25).round() * 0.25 / 2
    p = w.shift(2).fillna(0)
    champ_ret = champ_ret.add(p * c.pct_change().fillna(0)
                              - p.diff().abs().fillna(p.abs()) * FEE, fill_value=0)
ix = ret.index.intersection(champ_ret.index)
corr_full = float(ret[ix].corr(champ_ret[ix]))
te_ix = ix[int(len(ix) * 0.85):]
corr_test = float(ret[te_ix].corr(champ_ret[te_ix]))
print(f"\n  Correlation with champion daily stream: FULL {corr_full:+.3f}  "
      f"TEST {corr_test:+.3f}  (portfolio-slot bar: < 0.4)")

print('\n[4] Gate summary (see session report for the promotion decision):')
print(f"    TEST Sharpe standalone positive:  {'PASS' if sharpe(seg['TEST']) > 0 else 'FAIL'}")
print(f"    TEST activity >= 10 episodes:     {'PASS' if test_eps >= 10 else 'INCONCLUSIVE-BY-SAMPLE'}")
print(f"    WF majority-positive (4-window):  {'PASS' if wfs[4]['majority_positive'] else 'FAIL'}")
print(f"    DSR >= 0.95:                      {'PASS' if (dsr['dsr'] or 0) >= 0.95 else 'FAIL'}")
print(f"    corr < 0.4:                       {'PASS' if corr_full < 0.4 and corr_test < 0.4 else 'FAIL'}")
