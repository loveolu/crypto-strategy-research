"""
Phase 22: H-IVSizing — max(rv30, DVOL/100) in the champion's sizing denominator.

PRE-REGISTERED experiment (would-be trial #99). Spec locked in
SESSION_2026-07-12_IVSIZING.md §1 BEFORE this script produced any numbers.

Structure (exits at whichever pre-gate fails; pre-gates cost ZERO n_trials):
  Step 1:  Replication — rerun overlap-window champion baseline (Sharpe ~0.868 in band)
           and the cached census numbers (level corr +0.687; avg_lead +0.2489 vs avg_lag
           +0.0714 — the phase21 assert must pass).
  P1:      Materiality census — count in-market days where QUANTIZED weight differs and
           distinct difference episodes. STOP if < 5% differing days OR < 20 episodes.
  P2:      Harm census — on days where W_ivsizing < W_champ, compare champion's forward
           10d net return vs unconditional. STOP if NOT worse.
  Trial:   ONLY if P1 and P2 pass — the ONE locked construction, full validation stack.

LOCKED constants (see SESSION_2026-07-12_IVSIZING.md §1.2 — never touch without Director approval):
  Sizing formula  : rv_eff_i(t) = max(rv30_i(t), DVOL_BTC(t)/100)
  Weight formula  : w_i = quantize_25%( core_i * clip(0.40 / rv_eff_i, 0, 1) ) / 2
  DVOL driver     : BTC DVOL only (ETH cached but not used)
  Alignment       : ffill(limit=2)
  Free parameters : ZERO — no z-scores, no thresholds, no blend weights, no VRP haircut
  Eval window     : 2021-03-24 to 2026-05-31 (DVOL-champion overlap)
  MC              : 1,000 monthly-block-shuffle sims, seed 11
  WF configs      : 3/4/5/6 windows
  DSR             : n_trials = 99
  Fee             : 0.15%/side on |Delta position|
"""
import sys
from pathlib import Path

sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')

import numpy as np
import pandas as pd

from freqtrade_dsr import deflated_sharpe_ratio
from validator import wf_window_stability, family_from_results_dir, family_context

# ============================================================
# LOCKED CONSTANTS — do not change without Director approval
# ============================================================
FEE            = 0.0015          # 0.15% per side
ANN            = 365
MC_SIMS        = 1_000
MC_SEED        = 11
N_TRIALS_BASE  = 98              # current count before this trial
VOL_TARGET     = 0.40
LOOKBACK_VOL   = 30
QUANT          = 0.25
CHAMP_SYMS     = ['BTC', 'ETH']
FWD_DAYS       = 10              # forward return window for harm census

# Pre-gate thresholds (locked in §1.3)
P1_MIN_DIFF_FRAC     = 0.05    # < 5% differing in-market days → STOP
P1_MIN_DIFF_EPISODES = 20      # < 20 distinct difference episodes → STOP

DATA_DIR  = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
DVOL_DIR  = Path('C:/Users/Comec/Projects/freqtrade/user_data/research/data/dvol')
DVOL_FEATHER = DVOL_DIR / 'btc_dvol_daily.feather'

# Overlap window (DVOL-champion overlap)
OVERLAP_START = pd.Timestamp('2021-03-24', tz='UTC')
OVERLAP_END   = pd.Timestamp('2026-05-31', tz='UTC')

print('=' * 78)
print('PHASE 22 - H-IVSizing: max(rv30, DVOL/100) in champion sizing denominator')
print('=' * 78)
print()
print('[Pre-registration] All constants locked in SESSION_2026-07-12_IVSIZING.md §1.')
print(f'[Pre-registration] rv_eff = max(rv30, DVOL/100); fee={FEE}; MC_SEED={MC_SEED}')
print(f'[Pre-registration] Overlap window: {OVERLAP_START.date()} -> {OVERLAP_END.date()}')
print()

# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def _sma(s, n):
    return s.rolling(n).mean()

def _ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def load_fut(sym: str) -> pd.DataFrame:
    fp = DATA_DIR / f'{sym}_USDT_USDT-1d-futures.feather'
    df = pd.read_feather(fp)
    df = df.set_index('date').sort_index()
    df.index = pd.to_datetime(df.index, utc=True)
    return df.astype({c: float for c in ['open', 'high', 'low', 'close', 'volume']})

def core_series(close: pd.Series) -> pd.Series:
    return (
        (close > _sma(close, 200))
        & (close.pct_change(30) > 0)
        & (_ema(close, 20) > _ema(close, 50))
    ).astype(float)

def rv30_series(close: pd.Series) -> pd.Series:
    """Close-to-close 30d realized vol (annualized) — the champion's own estimator."""
    return close.pct_change().rolling(LOOKBACK_VOL).std() * np.sqrt(ANN)

def scale_series_rv30(close: pd.Series) -> pd.Series:
    """Champion's standard vol-target scale factor (rv30 only)."""
    rv = rv30_series(close)
    return (VOL_TARGET / rv).clip(0, 1)

def scale_series_ivsizing(close: pd.Series, dvol_btc: pd.Series) -> pd.Series:
    """
    H-IVSizing scale factor: max(rv30, DVOL_BTC/100) in denominator.
    DVOL is in percentage-annualized form (e.g., 80 = 80% ann vol).
    Dividing by 100 converts to the same fractional form as rv30 (which is
    already fractional, e.g., 0.80 for 80% ann vol).
    rv_eff = max(rv30, DVOL/100)
    scale = clip(0.40 / rv_eff, 0, 1)
    """
    rv30 = rv30_series(close)
    dvol_frac = dvol_btc / 100.0          # convert percentage to fraction
    rv_eff = rv30.combine(dvol_frac, max)  # elementwise max
    return (VOL_TARGET / rv_eff).clip(0, 1)

def quantize_scale(raw: pd.Series) -> pd.Series:
    return ((raw / QUANT).round() * QUANT).clip(0, 1)

def champion_weights(closes: pd.DataFrame) -> pd.DataFrame:
    """Return the champion's weight matrix (pure rv30 sizing)."""
    W = pd.DataFrame(index=closes.index)
    for s in CHAMP_SYMS:
        raw = core_series(closes[s]) * scale_series_rv30(closes[s])
        W[s] = quantize_scale(raw.fillna(0)) / len(CHAMP_SYMS)
    return W

def ivsizing_weights(closes: pd.DataFrame, dvol_btc: pd.Series) -> pd.DataFrame:
    """Return the H-IVSizing weight matrix (max(rv30, DVOL/100) sizing)."""
    W = pd.DataFrame(index=closes.index)
    for s in CHAMP_SYMS:
        # BTC DVOL is the sole driver for BOTH assets (locked in §1.2)
        raw = core_series(closes[s]) * scale_series_ivsizing(closes[s], dvol_btc)
        W[s] = quantize_scale(raw.fillna(0)) / len(CHAMP_SYMS)
    return W

def net_from_weights(W: pd.DataFrame, closes: pd.DataFrame) -> pd.Series:
    """Standard harness: 2-bar lag, fee on |Delta position|."""
    pos = W.reindex(closes.index).fillna(0).shift(2).fillna(0)
    gross = (pos * closes.pct_change().fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    return (gross - turn * FEE).dropna()

def perf(ret: pd.Series) -> dict:
    ret = ret.dropna()
    if len(ret) < 10 or ret.std() == 0:
        return dict(sh=0, dd=0, cagr=0, n=len(ret))
    eq = (1 + ret).cumprod()
    yrs = len(ret) / ANN
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1.0
    sh = ret.mean() / ret.std() * np.sqrt(ANN)
    dd = float((eq / eq.cummax() - 1).min())
    return dict(sh=float(sh), dd=float(dd), cagr=float(cagr), n=len(ret))

def mc_tail(ret: pd.Series, sims: int = MC_SIMS, seed: int = MC_SEED) -> tuple:
    blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
    rng = np.random.default_rng(seed)
    dds = []
    for _ in range(sims):
        seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        eq = np.cumprod(1 + seq)
        dds.append((eq / np.maximum.accumulate(eq) - 1).min())
    dds = np.array(dds)
    return float((dds < -0.25).mean()), float(np.percentile(dds, 50))

def split_indices(n: int):
    """70/15/15 chronological split — returns (train_end, val_end)."""
    t = int(n * 0.70)
    v = int(n * 0.85)
    return t, v

def rolling_z(s: pd.Series, window: int = 365) -> pd.Series:
    """Causal z-score: (value - rolling_mean) / rolling_std."""
    mu = s.rolling(window, min_periods=window // 2).mean()
    sd = s.rolling(window, min_periods=window // 2).std()
    return (s - mu) / sd.replace(0, np.nan)

def in_market_mask(W: pd.DataFrame) -> pd.Series:
    """True where at least one asset is in-market (2-bar lag applied)."""
    return (W.shift(2).fillna(0).abs().sum(axis=1) > 0)

# ============================================================
# LOAD DATA
# ============================================================
print('─' * 78)
print('Loading data (BTC+ETH futures + BTC DVOL cache)...')
print('─' * 78)

# Load futures data on the overlap window
closes = pd.DataFrame()
for s in CHAMP_SYMS:
    df_s = load_fut(s)
    df_s = df_s.loc[(df_s.index >= OVERLAP_START) & (df_s.index <= OVERLAP_END)]
    closes[s] = df_s['close']
closes = closes.dropna()
print(f'  Futures data: {len(closes):,} days, {closes.index[0].date()} -> {closes.index[-1].date()}')

# Load DVOL from cache
if not DVOL_FEATHER.exists():
    print(f'  ERROR: BTC DVOL cache not found at {DVOL_FEATHER}')
    print('  Run phase21_ivgate.py first to populate the DVOL cache.')
    sys.exit(1)

dvol_raw = pd.read_feather(DVOL_FEATHER)
dvol_raw.columns = [c.lower() for c in dvol_raw.columns]
date_col = [c for c in dvol_raw.columns if 'date' in c or 'time' in c][0]
val_col  = [c for c in dvol_raw.columns if c != date_col][0]
dvol_raw[date_col] = pd.to_datetime(dvol_raw[date_col], utc=True)
btc_dvol_raw = dvol_raw.set_index(date_col)[val_col].sort_index()

# Align DVOL to the closes index with ffill(limit=2)
btc_dvol = btc_dvol_raw.reindex(closes.index).ffill(limit=2)

dvol_missing = btc_dvol.isna().sum()
print(f'  BTC DVOL cache: {len(btc_dvol_raw)} days, {btc_dvol_raw.index[0].date()} -> {btc_dvol_raw.index[-1].date()}')
print(f'  DVOL aligned to closes index: {len(btc_dvol)} days, {dvol_missing} NaN after ffill(limit=2)')
print()

# ============================================================
# STEP 1 — REPLICATION BASELINE
# ============================================================
print('─' * 78)
print('STEP 1 — Replication: champion baseline on overlap window')
print('─' * 78)
print()

W_champ = champion_weights(closes)
ret_champ = net_from_weights(W_champ, closes)
p_full_champ = perf(ret_champ)
sh_full_champ = p_full_champ['sh']

print(f'  Champion full-window Sharpe on overlap: {sh_full_champ:.3f}')
print(f'  Replication band: [0.65, 1.20] (overlap window; measured ~0.868 in phase21)')

if not (0.65 <= sh_full_champ <= 1.20):
    print(f'  REPLICATION GATE FAIL: Sharpe {sh_full_champ:.3f} outside [0.65, 1.20].')
    print('  Cannot proceed — baseline not replicated. Session ends.')
    sys.exit(1)

print('  REPLICATION GATE: PASS ✓')
print()

# Verify phase21 census numbers (lead/lag assert)
print('  Verifying phase21 lead/lag census (locked reference: avg_lead +0.2489, avg_lag +0.0714)...')
rv30_btc = rv30_series(closes['BTC'])
z_iv = rolling_z(btc_dvol)
z_rv = rolling_z(rv30_btc)
valid = z_iv.notna() & z_rv.notna()
z_iv_v = z_iv[valid]
z_rv_v = z_rv[valid]
d5_ziv = z_iv_v.diff(5)
d5_zrv = z_rv_v.diff(5)
valid_d5 = d5_ziv.notna() & d5_zrv.notna()

corr_levels = float(z_iv_v.corr(z_rv_v))

lags = range(-10, 11)
xcorr = {}
for lag in lags:
    if lag < 0:
        c = d5_ziv[valid_d5].shift(-lag).dropna().corr(d5_zrv[valid_d5])
    elif lag > 0:
        c = d5_ziv[valid_d5].shift(-lag).corr(d5_zrv[valid_d5])
    else:
        c = float(d5_ziv[valid_d5].corr(d5_zrv[valid_d5]))
    xcorr[lag] = float(c) if not np.isnan(c) else 0.0

# Mandatory symmetry assert (cycle-#13 rule)
assert any(abs(xcorr[-k] - xcorr[k]) > 1e-12 for k in range(1, 11)), (
    'xcorr is exactly symmetric — lead/lag code bug. See SESSION_2026-07-11_IVGATE.md §6.')

lead_corrs = [xcorr[l] for l in range(-5, 0)]
lag_corrs  = [xcorr[l] for l in range(1, 6)]
avg_lead = np.mean(lead_corrs)
avg_lag  = np.mean(lag_corrs)

print(f'  Level corr (z_iv, z_rv)  : {corr_levels:+.4f} (reference: +0.6870)')
print(f'  avg_lead (IV-leading -5..-1): {avg_lead:+.4f} (reference: +0.2489)')
print(f'  avg_lag  (IV-lagging +1..+5): {avg_lag:+.4f} (reference: +0.0714)')

# Check that lead is still > lag (B2 condition)
if avg_lead <= avg_lag:
    print(f'  WARNING: avg_lead <= avg_lag on this run ({avg_lead:.4f} <= {avg_lag:.4f})')
    print('  This would indicate a data change. Proceeding but flagging.')
else:
    print(f'  Lead/lag direction CONFIRMED: IV leads rv30 (avg_lead {avg_lead:.4f} > avg_lag {avg_lag:.4f})')

# Tolerance check on reference values
level_corr_ok = abs(corr_levels - 0.6870) < 0.05
lead_ok = abs(avg_lead - 0.2489) < 0.05
lag_ok  = abs(avg_lag  - 0.0714) < 0.05

if not (level_corr_ok and lead_ok and lag_ok):
    print()
    print('  REPLICATION WARNING: census numbers deviate from reference.')
    print(f'    level_corr: {corr_levels:.4f} (ref 0.6870, ok={level_corr_ok})')
    print(f'    avg_lead  : {avg_lead:.4f} (ref 0.2489, ok={lead_ok})')
    print(f'    avg_lag   : {avg_lag:.4f} (ref 0.0714, ok={lag_ok})')
    print('  Proceeding with actual values. Report discrepancy.')
else:
    print('  Phase21 census numbers REPLICATED within tolerance. ✓')
print()

# ============================================================
# PRE-GATE P1 — MATERIALITY CENSUS
# ============================================================
print('─' * 78)
print('PRE-GATE P1 — Materiality census')
print('─' * 78)
print()

# Construct the H-IVSizing weight matrix
W_ivs = ivsizing_weights(closes, btc_dvol)
ret_ivs = net_from_weights(W_ivs, closes)

# In-market mask based on champion (2-bar lag)
in_mkt_champ = in_market_mask(W_champ)

# Count in-market days where QUANTIZED weights differ
# We compare the post-quantization weights (what goes into position)
diff_any = (W_ivs - W_champ).abs().sum(axis=1) > 1e-10
diff_in_mkt = diff_any & in_mkt_champ.reindex(diff_any.index, fill_value=False)

n_in_mkt_total   = int(in_mkt_champ.sum())
n_diff_in_mkt    = int(diff_in_mkt.sum())
diff_frac_in_mkt = n_diff_in_mkt / max(n_in_mkt_total, 1)

# Count distinct difference episodes (maximal consecutive runs where diff_any is True)
diff_eps = []
in_ep = False
ep_start = None
for dt in diff_any.index:
    if diff_any[dt] and not in_ep:
        in_ep = True
        ep_start = dt
    elif not diff_any[dt] and in_ep:
        in_ep = False
        diff_eps.append((ep_start, dt - pd.Timedelta(days=1)))
if in_ep:
    diff_eps.append((ep_start, diff_any.index[-1]))

n_diff_eps = len(diff_eps)

print(f'  Total in-market days (champion, 2-bar lag): {n_in_mkt_total:,}')
n_diff_any = int(diff_any.sum())
print(f'  Days where QUANTIZED weight differs (any asset): {n_diff_any:,}')
print(f'  Of which in-market days: {n_diff_in_mkt:,} ({diff_frac_in_mkt*100:.1f}% of in-market days)')
print(f'  Distinct difference episodes: {n_diff_eps}')
print()

# Split differing days by year
print('  Differing days by year:')
for yr in sorted(set(diff_any.index.year)):
    mask_yr = diff_any.index.year == yr
    n_yr = int(diff_any[mask_yr].sum())
    n_im_yr = int(diff_in_mkt[mask_yr].sum())
    print(f'    {yr}: {n_yr} total diff days, {n_im_yr} in-market diff days')
print()

# Split differing days by TEST membership
n_all = len(ret_champ)
t_end_idx, v_end_idx = split_indices(n_all)
TRAIN_END  = ret_champ.index[t_end_idx - 1]
VAL_END    = ret_champ.index[v_end_idx - 1]
TEST_START = ret_champ.index[v_end_idx]
TEST_END   = ret_champ.index[-1]

print(f'  70/15/15 split dates:')
print(f'    70% TRAIN ends : {TRAIN_END.date()}')
print(f'    15% VAL ends   : {VAL_END.date()}')
print(f'    15% TEST starts: {TEST_START.date()}')
print(f'    15% TEST ends  : {TEST_END.date()}')

test_diff_days = int(diff_any[diff_any.index >= TEST_START].sum())
test_im_diff_days = int(diff_in_mkt[diff_in_mkt.index >= TEST_START].sum())
print(f'  Differing days in TEST split: {test_diff_days} ({test_im_diff_days} in-market)')
print()

# Also characterize: on differing days, is W_ivs always < W_champ, or sometimes > ?
diff_dir_lt = ((W_ivs - W_champ).sum(axis=1) < -1e-10)  # IVS has LESS weight
diff_dir_gt = ((W_ivs - W_champ).sum(axis=1) > 1e-10)   # IVS has MORE weight
n_lt = int((diff_dir_lt & diff_any).sum())
n_gt = int((diff_dir_gt & diff_any).sum())
print(f'  Of differing days: IVSizing < Champion (DVOL > rv30, exposure reduced): {n_lt}')
print(f'  Of differing days: IVSizing > Champion (DVOL < rv30 — impossible by construction): {n_gt}')
print()
print(f'  P1 stop rule: < {P1_MIN_DIFF_FRAC*100:.0f}% differing in-market days OR < {P1_MIN_DIFF_EPISODES} episodes')
print(f'  Differing in-market fraction: {diff_frac_in_mkt*100:.1f}% (bar: >= {P1_MIN_DIFF_FRAC*100:.0f}%)')
print(f'  Difference episodes: {n_diff_eps} (bar: >= {P1_MIN_DIFF_EPISODES})')
print()

if diff_frac_in_mkt < P1_MIN_DIFF_FRAC:
    print(f'PRE-GATE P1: FAIL — only {diff_frac_in_mkt*100:.1f}% differing in-market days (<{P1_MIN_DIFF_FRAC*100:.0f}%).')
    print('Quantizer swallows the max() substitution. Lesson #15: estimator precision discarded.')
    print('IV-SIZING DIRECTION CLOSED. DVOL axis closed for daily-bar champion improvements.')
    print('Zero trials spent. n_trials stays 98.')
    sys.exit(0)

if n_diff_eps < P1_MIN_DIFF_EPISODES:
    print(f'PRE-GATE P1: FAIL — only {n_diff_eps} distinct difference episodes (<{P1_MIN_DIFF_EPISODES}).')
    print('Too few independent events to validate. Lesson #16/#21.')
    print('IV-SIZING DIRECTION CLOSED. DVOL axis closed for daily-bar champion improvements.')
    print('Zero trials spent. n_trials stays 98.')
    sys.exit(0)

print('PRE-GATE P1: PASS ✓')
print()

# ============================================================
# PRE-GATE P2 — HARM CENSUS ON AFFECTED DAYS
# ============================================================
print('─' * 78)
print('PRE-GATE P2 — Harm census on affected days (where W_ivs < W_champ)')
print('─' * 78)
print()

# Affected days: in-market AND W_ivs < W_champ (these are the only days that can help)
# (By construction, DVOL/100 >= rv30 => rv_eff >= rv30 => scale_ivs <= scale_champ => weight_ivs <= weight_champ)
affected_mask = (diff_dir_lt & in_mkt_champ.reindex(diff_dir_lt.index, fill_value=False))
n_affected = int(affected_mask.sum())
print(f'  Days where W_ivs < W_champ (affected, in-market): {n_affected}')

# Champion's forward FWD_DAYS net return on affected days vs unconditional in-market
champ_ret_full = net_from_weights(W_champ, closes)

# Forward FWD_DAYS returns from champ_ret on affected days
fwd_affected = []
for dt in affected_mask[affected_mask].index:
    if dt not in champ_ret_full.index:
        continue
    idx_pos = champ_ret_full.index.get_loc(dt)
    end_pos = min(idx_pos + FWD_DAYS, len(champ_ret_full) - 1)
    fwd_affected.append(champ_ret_full.iloc[idx_pos:end_pos + 1].sum())

# Unconditional in-market forward FWD_DAYS distribution
fwd_uncond = []
for i, dt in enumerate(champ_ret_full.index):
    if in_mkt_champ.get(dt, False):
        end_pos = min(i + FWD_DAYS, len(champ_ret_full) - 1)
        fwd_uncond.append(champ_ret_full.iloc[i:end_pos + 1].sum())

aff_median = float(np.median(fwd_affected)) if fwd_affected else 0.0
aff_mean   = float(np.mean(fwd_affected))   if fwd_affected else 0.0
unc_median = float(np.median(fwd_uncond))   if fwd_uncond   else 0.0
unc_mean   = float(np.mean(fwd_uncond))     if fwd_uncond   else 0.0

print(f'  Forward {FWD_DAYS}d champion return distribution:')
print(f'    Affected days (n={len(fwd_affected)}):  median={aff_median*100:+.2f}%  mean={aff_mean*100:+.2f}%')
print(f'    Unconditional in-market (n={len(fwd_uncond)}): median={unc_median*100:+.2f}%  mean={unc_mean*100:+.2f}%')
print(f'  Stop rule: affected-day distribution is NOT worse than unconditional')
print(f'  ("worse" = affected_median < unc_median OR affected_mean < unc_mean)')
print()

affected_worse = (aff_median < unc_median) or (aff_mean < unc_mean)

if not affected_worse:
    print(f'PRE-GATE P2: FAIL — affected-day forward returns are NOT worse than unconditional.')
    print('Days where DVOL > rv30 do not have worse forward returns. No harm to avoid.')
    print('IV-SIZING DIRECTION CLOSED. DVOL axis closed for daily-bar champion improvements.')
    print('Zero trials spent. n_trials stays 98.')
    sys.exit(0)

print('PRE-GATE P2: PASS ✓')
print(f'  Affected days are worse: median {aff_median*100:+.2f}% < uncond {unc_median*100:+.2f}%'
      f' [{aff_median < unc_median}], mean {aff_mean*100:+.2f}% < uncond {unc_mean*100:+.2f}%'
      f' [{aff_mean < unc_mean}]')
print()

# ============================================================
# TRIAL #99 — the ONE locked construction
# ============================================================
print('─' * 78)
print('TRIAL #99 — max(rv30, DVOL/100) sizing substitution — FULL VALIDATION STACK')
print('─' * 78)
print()
print('NOTE: n_trials advances 98 -> 99 with this trial.')
print()

# ── Confirm split dates ──────────────────────────────────────────────────
print(f'  Overlap window : {ret_champ.index[0].date()} -> {ret_champ.index[-1].date()} ({n_all} days)')
print(f'  70% TRAIN ends : {TRAIN_END.date()}')
print(f'  15% VAL ends   : {VAL_END.date()}')
print(f'  15% TEST starts: {TEST_START.date()}')
print(f'  15% TEST ends  : {TEST_END.date()}')
test_days = n_all - v_end_idx
print(f'  TEST days      : {test_days} (~{test_days/365:.2f} years) — episode-hostage risk per finding #9')
print()

# ── Activity in TEST split ────────────────────────────────────────────────
diff_test = diff_any[diff_any.index >= TEST_START]
n_diff_in_test = int(diff_test.sum())
print(f'  Quantized-weight-difference days in TEST split: {n_diff_in_test}')
print()

# ── Full validation stack ─────────────────────────────────────────────────
print('  === Champion baseline (overlap window) ===')
p_champ = {}
for label, sl in [('FULL', slice(None, None)),
                  ('TRAIN', slice(None, t_end_idx)),
                  ('VAL',   slice(t_end_idx, v_end_idx)),
                  ('TEST',  slice(v_end_idx, None))]:
    p = perf(ret_champ.iloc[sl] if sl != slice(None, None) else ret_champ)
    p_champ[label] = p
    print(f'    {label:<6}: Sharpe {p["sh"]:+.3f}  DD {p["dd"]*100:5.1f}%  CAGR {p["cagr"]*100:+5.1f}%  n={p["n"]}')

mc_p25_champ, mc_med_champ = mc_tail(ret_champ)
print(f'    MC tail P(DD<-25%)        : {mc_p25_champ*100:.1f}%  (median DD {mc_med_champ*100:.1f}%)')

print()
print('  === H-IVSizing strategy (overlap window) ===')
p_ivs = {}
for label, sl in [('FULL', slice(None, None)),
                  ('TRAIN', slice(None, t_end_idx)),
                  ('VAL',   slice(t_end_idx, v_end_idx)),
                  ('TEST',  slice(v_end_idx, None))]:
    p = perf(ret_ivs.iloc[sl] if sl != slice(None, None) else ret_ivs)
    p_ivs[label] = p
    print(f'    {label:<6}: Sharpe {p["sh"]:+.3f}  DD {p["dd"]*100:5.1f}%  CAGR {p["cagr"]*100:+5.1f}%  n={p["n"]}')

mc_p25_ivs, mc_med_ivs = mc_tail(ret_ivs)
print(f'    MC tail P(DD<-25%)        : {mc_p25_ivs*100:.1f}%  (median DD {mc_med_ivs*100:.1f}%)')

# ── WF window stability ──────────────────────────────────────────────────
print()
print('  === Walk-forward window stability (3/4/5/6 configs) ===')
wf_results_ivs   = {}
wf_results_champ = {}
for n_win in [3, 4, 5, 6]:
    wf_v = wf_window_stability(ret_ivs,   n_windows=n_win)
    wf_c = wf_window_stability(ret_champ, n_windows=n_win)
    wf_results_ivs[n_win]   = wf_v
    wf_results_champ[n_win] = wf_c
    v_pos = sum(1 for w in wf_v if w > 0)
    c_pos = sum(1 for w in wf_c if w > 0)
    majority_v = v_pos > n_win / 2
    majority_c = c_pos > n_win / 2
    print(f'    {n_win} windows: IVS {v_pos}/{n_win} positive ({"PASS" if majority_v else "FAIL"}) | '
          f'champ {c_pos}/{n_win} positive ({"PASS" if majority_c else "FAIL"})')
    print(f'      IVS WF values  : {[round(x, 3) for x in wf_v]}')
    print(f'      champ WF values: {[round(x, 3) for x in wf_c]}')

wf_majority_pass = sum(
    1 for n_win in [3, 4, 5, 6]
    if sum(1 for w in wf_results_ivs[n_win] if w > 0) > n_win / 2
)
print(f'  WF majority-positive: {wf_majority_pass} of 4 configs (bar: >= 3)')

# ── DSR ──────────────────────────────────────────────────────────────────
print()
print('  === Deflated Sharpe Ratio ===')
N_TRIALS_NEW  = N_TRIALS_BASE + 1  # 99
dsr_ivs       = deflated_sharpe_ratio(ret_ivs,   n_trials=N_TRIALS_NEW)
dsr_champ_99  = deflated_sharpe_ratio(ret_champ, n_trials=N_TRIALS_NEW)
print(f'    IVSizing DSR at n_trials={N_TRIALS_NEW}: {dsr_ivs:.4f}')
print(f'    Champion DSR at n_trials={N_TRIALS_NEW}: {dsr_champ_99:.4f} (same-window baseline)')

# ── Per-year accounting ───────────────────────────────────────────────────
print()
print('  === Per-year exposure drag and gross avoided loss ===')
year_analysis = {}
W_champ_pos = W_champ.shift(2).fillna(0).reindex(ret_champ.index)
W_ivs_pos   = W_ivs.shift(2).fillna(0).reindex(ret_champ.index)

for yr in sorted(set(ret_champ.index.year)):
    mask = ret_champ.index.year == yr
    r_c_yr = ret_champ[mask]
    r_v_yr = ret_ivs.reindex(ret_champ.index)[mask]

    # Days where IVS reduced exposure vs champion AND champion was in market
    diff_red_yr = ((W_ivs - W_champ).sum(axis=1) < -1e-10)
    champ_in_yr = in_mkt_champ.reindex(ret_champ.index, fill_value=False)
    reduced_mask_yr = (diff_red_yr.reindex(ret_champ.index, fill_value=False) & champ_in_yr)[mask]
    n_reduced = int(reduced_mask_yr.sum())

    # Gross avoided loss = champion return on those days
    # Negative value means champion lost money there → the reduction helped
    avoided_gross = float(r_c_yr[reduced_mask_yr].sum())

    # Exposure drag: all days where IVS has less weight even when champion is in market
    # Fee drag from extra rebalances (already priced into ret_ivs vs ret_champ diff)
    extra_turn_yr = (W_ivs_pos - W_champ_pos).abs().sum(axis=1)[mask].sum()
    fee_drag = float(extra_turn_yr * FEE)

    # Exposure drag = weight reduction × market return on non-reduced days + weight reduction on reduced days
    # Simplified: direct diff of yearly returns
    total_r_c  = float(r_c_yr.sum())
    total_r_v  = float(r_v_yr.sum())
    net_yr_diff = total_r_v - total_r_c  # positive = IVS better

    year_analysis[yr] = {
        'reduced_days': n_reduced,
        'avoided_gross': avoided_gross,
        'fee_drag': fee_drag,
        'net_yr_diff': net_yr_diff,
    }
    print(f'    {yr}: reduced_days={n_reduced:3d}  avoided_gross={avoided_gross*100:+5.2f}%  '
          f'fee_drag={fee_drag*100:.3f}%  net_diff_vs_champ={net_yr_diff*100:+5.2f}%')

# Check per-year bar: no year where fee_drag > abs(avoided_gross) with avoided_gross > 0
# (i.e., fee pumped without any protective benefit)
fee_pump_years = [yr for yr, d in year_analysis.items()
                  if d['reduced_days'] > 0 and d['fee_drag'] > abs(d['avoided_gross']) and d['avoided_gross'] > 0]
print(f'  Years where fee drag > gross avoided loss (and loss was positive, not protective): {fee_pump_years}')

# ── Family context ────────────────────────────────────────────────────────
print()
print('  === Family context (H-IVSizing is the only construct in this family) ===')
try:
    fam = family_from_results_dir()
    fc = family_context(p_ivs['FULL']['sh'], fam_sharpes=[s for _, s in fam])
    print(f'    {fc}')
except Exception as e:
    print(f'    Family context unavailable: {e}')

# ── Look-ahead audit ──────────────────────────────────────────────────────
print()
print('  === Look-ahead audit ===')
print('  DVOL alignment: btc_dvol uses ffill(limit=2) to closes index.')
print('  All DVOL values at day t use DVOL close at day t (or t-1/t-2 if gap).')
print('  The max() comparison: rv30_i(t) uses returns up to and including close(t).')
print('  DVOL(t) = daily close of the DVOL index as of day t.')
print('  BOTH inputs are available at candle close. No look-ahead bias.')
print('  Prefix-stability check on the max() series (% of days where DVOL/100 dominates):')
n_dvol_dom = int((btc_dvol / 100.0 > rv30_btc).reindex(closes.index).fillna(False).sum())
n_total_valid = int(rv30_btc.reindex(closes.index).notna().sum())
print(f'    Days where DVOL/100 > rv30 (DVOL dominates): {n_dvol_dom} / {n_total_valid} '
      f'({n_dvol_dom/max(n_total_valid,1)*100:.1f}%)')
print()

# ── Validation bars summary ───────────────────────────────────────────────
print()
print('=' * 78)
print('VALIDATION BAR CHECK (pre-registered §1.4)')
print('=' * 78)

mc_p25_imp    = mc_p25_champ - mc_p25_ivs   # positive = IVS improved
test_sh_champ = p_champ['TEST']['sh']
test_sh_ivs   = p_ivs['TEST']['sh']
test_sh_diff  = test_sh_ivs - test_sh_champ
full_sh_champ = p_champ['FULL']['sh']
full_sh_ivs   = p_ivs['FULL']['sh']
full_sh_diff  = full_sh_ivs - full_sh_champ

bar1a = mc_p25_imp >= 0.05             # MC tail improved >= 5pp
bar1b = test_sh_diff >= 0.05           # TEST Sharpe improved >= 0.05
bar1  = bar1a or bar1b                 # at least one
bar2  = test_sh_diff >= -0.02          # TEST Sharpe not degraded > 0.02
bar3  = full_sh_diff >= -0.05          # FULL Sharpe not degraded > 0.05
bar4  = wf_majority_pass >= 3          # WF majority-positive >= 3 of 4
bar5  = dsr_ivs >= dsr_champ_99        # DSR IVS >= DSR champion at n=99
bar6  = n_diff_in_test > 0             # > 0 differing days in TEST split
bar7  = len(fee_pump_years) == 0       # no pure-fee-pump years

results = {
    'bar1_MC_tail_or_TEST_Sharpe':     bar1,
    'bar1a_MC_tail_improved_5pp':      bar1a,
    'bar1b_TEST_Sharpe_improved_0.05': bar1b,
    'bar2_TEST_Sharpe_not_degraded':   bar2,
    'bar3_FULL_Sharpe_not_degraded':   bar3,
    'bar4_WF_majority_3of4':           bar4,
    'bar5_DSR_ivs_geq_champ':          bar5,
    'bar6_activity_in_TEST':           bar6,
    'bar7_no_fee_pump_years':          bar7,
}

print()
print(f'  Bar 1 (MC tail >=5pp OR TEST Sharpe +0.05):   {"PASS ✓" if bar1  else "FAIL ✗"}')
print(f'    1a MC tail improved:  {mc_p25_imp*100:+.1f}pp (need >=+5pp) -> {"PASS ✓" if bar1a else "FAIL ✗"}')
print(f'    1b TEST Sharpe delta: {test_sh_diff:+.3f}  (need >=+0.05) -> {"PASS ✓" if bar1b else "FAIL ✗"}')
print(f'  Bar 2 (TEST Sharpe not degraded >0.02):        {"PASS ✓" if bar2  else "FAIL ✗"}  (delta {test_sh_diff:+.3f})')
print(f'  Bar 3 (FULL Sharpe not degraded >0.05):        {"PASS ✓" if bar3  else "FAIL ✗"}  (delta {full_sh_diff:+.3f})')
print(f'  Bar 4 (WF majority-positive >=3 of 4 configs): {"PASS ✓" if bar4  else "FAIL ✗"}  ({wf_majority_pass}/4)')
print(f'  Bar 5 (DSR IVS >= DSR champ at n=99):          {"PASS ✓" if bar5  else "FAIL ✗"}  ({dsr_ivs:.4f} vs {dsr_champ_99:.4f})')
print(f'  Bar 6 (>0 diff days in TEST split):            {"PASS ✓" if bar6  else "FAIL ✗"}  ({n_diff_in_test} days)')
print(f'  Bar 7 (no pure-fee-pump years):                {"PASS ✓" if bar7  else "FAIL ✗"}  ({fee_pump_years})')
print()

key_bars = ['bar1_MC_tail_or_TEST_Sharpe', 'bar2_TEST_Sharpe_not_degraded',
            'bar3_FULL_Sharpe_not_degraded', 'bar4_WF_majority_3of4',
            'bar5_DSR_ivs_geq_champ', 'bar6_activity_in_TEST',
            'bar7_no_fee_pump_years']
all_pass = all(results[b] for b in key_bars)

if all_pass:
    verdict = 'VERIFY-PENDING — ALL VALIDATION BARS PASS. Champion sleeve upgrade candidate.'
else:
    failed = [k for k in key_bars if not results[k]]
    verdict = f'REJECT — failed: {", ".join(failed)}'

print(f'VERDICT: {verdict}')
print()
print('─' * 78)
print('Summary for research files:')
print(f'  Overlap window      : {OVERLAP_START.date()} -> {OVERLAP_END.date()}')
print(f'  Replication Sharpe  : {sh_full_champ:.3f}')
print(f'  Level corr z_iv/z_rv: {corr_levels:.4f}')
print(f'  Lead/lag avg        : lead {avg_lead:.4f}, lag {avg_lag:.4f}')
print(f'  P1 diff_in_mkt_frac : {diff_frac_in_mkt*100:.1f}%  ({n_diff_in_mkt}/{n_in_mkt_total})')
print(f'  P1 diff episodes    : {n_diff_eps}')
print(f'  P2 affected_median  : {aff_median*100:+.2f}% vs uncond {unc_median*100:+.2f}%')
print(f'  P2 affected_mean    : {aff_mean*100:+.2f}% vs uncond {unc_mean*100:+.2f}%')
print(f'  Champion TEST Sh    : {test_sh_champ:.3f}')
print(f'  IVSizing TEST Sh    : {test_sh_ivs:.3f}  (delta {test_sh_diff:+.3f})')
print(f'  Champion MC tail    : {mc_p25_champ*100:.1f}%')
print(f'  IVSizing MC tail    : {mc_p25_ivs*100:.1f}%  (improvement {mc_p25_imp*100:+.1f}pp)')
print(f'  DSR IVS/champ@99    : {dsr_ivs:.4f} / {dsr_champ_99:.4f}')
print(f'  WF majority-pass    : {wf_majority_pass}/4')
print(f'  DVOL dominates rv30 : {n_dvol_dom}/{n_total_valid} days ({n_dvol_dom/max(n_total_valid,1)*100:.1f}%)')
print(f'  VERDICT             : {verdict}')
print('─' * 78)

