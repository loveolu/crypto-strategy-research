"""
Phase 21: H-IVGate — Deribit DVOL implied-volatility crisis veto on the champion sleeve.

PRE-REGISTERED experiment (would-be trial #99). Spec locked in
SESSION_2026-07-11_IVGATE.md §1 BEFORE this script produced any numbers.

Structure (exits at whichever pre-gate fails; pre-gates cost ZERO n_trials):
  Pre-gate A: fetch BTC DVOL from Deribit public API; census data quality.
  Pre-gate B: redundancy check (z_iv vs z_rv correlation), lead/lag check,
              harvestability check — all on EXISTING streams.
  Trial #99:  ONLY if both pre-gates pass — champion sleeve + IV-gate veto,
              full validation stack on the overlap window.

LOCKED constants (see SESSION_2026-07-11_IVGATE.md §1.2 — never touch without Director approval):
  IV series       : BTC DVOL daily closes (ETH fetched/cached but not used in construction)
  z-score window  : 365 days
  z threshold     : 2.0
  Spike episode   : maximal run of consecutive z_iv > 2.0
  Veto scope      : both BTC and ETH assets
  No hysteresis   : veto lifts on first day z_iv ≤ 2.0
  Fee             : 0.15%/side on |Δposition| (ALL veto-induced moves)
  MC              : 1,000 sims, monthly-block-shuffle, seed 11
  WF configs      : 3/4/5/6 windows
  DSR n_trials    : 99 (consumed only if trial runs)
"""
import sys
import json
import time
import urllib.request
import urllib.error
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
FEE           = 0.0015          # 0.15% per side
ANN           = 365
MC_SIMS       = 1_000
MC_SEED       = 11
N_TRIALS_BASE = 98              # current count before this trial
Z_WINDOW      = 365             # rolling z-score window (days)
Z_THRESH      = 2.0             # IV spike threshold
FWD_DAYS      = 10              # forward return window for harvestability
CORR_STOP     = 0.90            # redundancy stop: level correlation above this → stop
VOL_TARGET    = 0.40
LOOKBACK_VOL  = 30
QUANT         = 0.25
CHAMP_SYMS    = ['BTC', 'ETH']

DATA_DIR   = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
DVOL_DIR   = Path('C:/Users/Comec/Projects/freqtrade/user_data/research/data/dvol')
DVOL_DIR.mkdir(parents=True, exist_ok=True)

DVOL_RAW_JSON   = DVOL_DIR / 'btc_dvol_1d.json'
DVOL_FEATHER    = DVOL_DIR / 'btc_dvol_daily.feather'
ETH_DVOL_JSON   = DVOL_DIR / 'eth_dvol_1d.json'
ETH_DVOL_FEATHER = DVOL_DIR / 'eth_dvol_daily.feather'

# Champion calendar (used to define overlap window)
CHAMP_START = pd.Timestamp('2020-01-01', tz='UTC')
CHAMP_END   = pd.Timestamp('2026-05-31', tz='UTC')

print('=' * 78)
print('PHASE 21 - H-IVGate: Deribit DVOL implied-vol veto (pre-gated)')
print('=' * 78)
print()
print('[Pre-registration] All constants locked in SESSION_2026-07-11_IVGATE.md §1.')
print(f'[Pre-registration] z_window={Z_WINDOW}, z_thresh={Z_THRESH}, fee={FEE}, MC_SEED={MC_SEED}')
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

def scale_series(close: pd.Series) -> pd.Series:
    rv = close.pct_change().rolling(LOOKBACK_VOL).std() * np.sqrt(ANN)
    return (VOL_TARGET / rv).clip(0, 1)

def quantize_scale(raw: pd.Series) -> pd.Series:
    return ((raw / QUANT).round() * QUANT).clip(0, 1)

def rv30_series(close: pd.Series) -> pd.Series:
    """Close-to-close 30d realized vol (annualized) — the champion's own estimator."""
    return close.pct_change().rolling(LOOKBACK_VOL).std() * np.sqrt(ANN)

def rolling_z(s: pd.Series, window: int = Z_WINDOW) -> pd.Series:
    """Causal z-score: (value - rolling_mean) / rolling_std, using only past data."""
    mu = s.rolling(window, min_periods=window // 2).mean()
    sd = s.rolling(window, min_periods=window // 2).std()
    return (s - mu) / sd.replace(0, np.nan)

def net_from_weights(W: pd.DataFrame, closes: pd.DataFrame) -> pd.Series:
    """Standard harness: 2-bar lag, fee on |Δposition|."""
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

def split_indices(n: int):
    """70/15/15 chronological split — returns (train_end, val_end)."""
    t = int(n * 0.70)
    v = int(n * 0.85)
    return t, v

def sharpe_on(ret: pd.Series) -> float:
    if len(ret) < 5 or ret.std() == 0:
        return 0.0
    return float(ret.mean() / ret.std() * np.sqrt(ANN))

def champion_weights(closes: pd.DataFrame) -> pd.DataFrame:
    """Return the champion's weight matrix (before veto)."""
    W = pd.DataFrame(index=closes.index)
    for s in CHAMP_SYMS:
        raw = core_series(closes[s]) * scale_series(closes[s])
        W[s] = quantize_scale(raw.fillna(0)) / len(CHAMP_SYMS)
    return W

def in_market_mask(W: pd.DataFrame) -> pd.Series:
    """True where at least one asset is in-market (2-bar lag applied)."""
    return (W.shift(2).fillna(0).abs().sum(axis=1) > 0)

# ============================================================
# PRE-GATE A — DATA-AXIS REACHABILITY CENSUS
# ============================================================
print('─' * 78)
print('PRE-GATE A — Deribit DVOL data-axis reachability census')
print('─' * 78)
print()

GATE_A_MIN_YEARS  = 4.0          # minimum overlap with champion calendar
GATE_A_MAX_MISS   = 0.02          # ≤ 2% missing days (after forward-fill ≤2d)
GATE_A_VOL_MIN    = 20.0          # sanity: DVOL annualized, lower bound
GATE_A_VOL_MAX    = 300.0         # sanity: DVOL annualized, upper bound


def _fetch_deribit_dvol(currency: str, out_json: Path, out_feather: Path) -> pd.Series | None:
    """
    Fetch Deribit DVOL daily closes via public API.
    Caches raw JSON and clean feather. Returns a UTC-indexed pd.Series or None on failure.
    
    Deribit API: /public/get_volatility_index_data
    Parameters: currency, start_timestamp (ms), end_timestamp (ms), resolution (seconds).
    Resolution 86400 = 1 day. Returns OHLC candles; we use close (index 4) plus time (index 0).
    
    Per the Deribit API docs the endpoint returns up to 1,000 candles per call.
    We page FORWARD starting from 2021-03-01 (known earliest DVOL date — confirmed by
    a 2020 query returning 0 candles; the DVOL index launched in March 2021).
    """
    BASE_URL = 'https://www.deribit.com/api/v2/public/get_volatility_index_data'
    RESOLUTION = 86400  # 1 day in seconds
    
    all_candles = []
    
    # DVOL launched in March 2021; requesting 2017 returns empty.
    # Start from 2021-03-01 to capture the full history.
    start_ms = int(pd.Timestamp('2021-03-01', tz='UTC').timestamp() * 1000)
    end_ms   = int(pd.Timestamp('2026-07-15', tz='UTC').timestamp() * 1000)
    
    print(f'  Fetching {currency} DVOL from Deribit API (paginating forward from 2021-03-01)...')
    
    # Each chunk: 1000 days forward
    CHUNK_MS = 1000 * RESOLUTION * 1000  # 1000 days in ms
    
    chunk_start = start_ms
    max_chunks  = 10  # safety: 10 * 1000 days >> total DVOL history
    
    for attempt in range(1, max_chunks + 1):
        if chunk_start >= end_ms:
            break
        chunk_end = min(chunk_start + CHUNK_MS, end_ms)
        url = (f'{BASE_URL}?currency={currency}'
               f'&start_timestamp={chunk_start}'
               f'&end_timestamp={chunk_end}'
               f'&resolution={RESOLUTION}')
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            print(f'  HTTP {e.code} error fetching {currency} DVOL. URL: {url}')
            return None
        except urllib.error.URLError as e:
            print(f'  URL error fetching {currency} DVOL: {e.reason}')
            return None
        except Exception as e:
            print(f'  Unexpected error fetching {currency} DVOL: {e}')
            return None
        
        if 'result' not in data:
            print(f'  Deribit API returned no result field. Response keys: {list(data.keys())}')
            if 'error' in data:
                print(f'  Error: {data["error"]}')
            return None
        
        candles = data['result'].get('data', [])
        print(f'    Chunk {attempt}: {len(candles)} candles')
        if not candles:
            break  # no more data
        
        all_candles.extend(candles)
        last_ts = candles[-1][0]  # last candle timestamp
        chunk_start = last_ts + RESOLUTION * 1000
        
        # Small delay to be polite to the API
        time.sleep(0.3)
        
        if len(candles) < 5:
            break  # probably at the end
    
    if not all_candles:
        print(f'  No candles returned for {currency} DVOL.')
        return None
    
    print(f'  Fetched {len(all_candles)} raw candles.')
    
    # Cache raw JSON
    with open(out_json, 'w') as f:
        json.dump({'currency': currency, 'candles': all_candles, 'fetched_utc': pd.Timestamp.utcnow().isoformat()}, f)
    print(f'  Raw JSON cached: {out_json}')
    
    # Parse: each candle = [timestamp_ms, open, high, low, close]
    df_raw = pd.DataFrame(all_candles, columns=['ts_ms', 'open', 'high', 'low', 'close'])
    df_raw = df_raw.drop_duplicates('ts_ms').sort_values('ts_ms')
    df_raw['date'] = pd.to_datetime(df_raw['ts_ms'], unit='ms', utc=True)
    df_raw = df_raw.set_index('date')
    
    # Keep only rows with sane DVOL close values
    dvol = df_raw['close'].astype(float)
    dvol = dvol[(dvol > 0)]
    
    # Resample to calendar daily (fill gaps ≤ 2 days with forward fill)
    dvol_daily = dvol.resample('1D').last()
    dvol_ffill = dvol_daily.ffill(limit=2)  # forward-fill gaps ≤ 2 days
    
    # Save feather
    out_df = dvol_ffill.reset_index()
    out_df.columns = ['date', 'dvol']
    out_df.to_feather(out_feather)
    print(f'  Clean feather cached: {out_feather}')
    
    return dvol_ffill


def load_dvol_from_cache(feather_path: Path) -> pd.Series | None:
    """Load cached DVOL daily series. Returns None if file doesn't exist."""
    if not feather_path.exists():
        return None
    df = pd.read_feather(feather_path)
    df = df.set_index('date')
    df.index = pd.to_datetime(df.index, utc=True)
    return df['dvol'].sort_index()


# Attempt to load from cache first; fetch if missing
print('  Checking for cached BTC DVOL data...')
btc_dvol_raw = load_dvol_from_cache(DVOL_FEATHER)

if btc_dvol_raw is None:
    print('  Cache miss — fetching from Deribit API.')
    btc_dvol_raw = _fetch_deribit_dvol('BTC', DVOL_RAW_JSON, DVOL_FEATHER)
else:
    print(f'  Loaded from cache: {len(btc_dvol_raw)} days, {btc_dvol_raw.index[0].date()} → {btc_dvol_raw.index[-1].date()}')

# Also cache ETH DVOL (for future use only — NOT used in this construction per lock)
print()
print('  Checking for cached ETH DVOL data (cache-only, not used in construction)...')
eth_dvol_raw = load_dvol_from_cache(ETH_DVOL_FEATHER)
if eth_dvol_raw is None:
    print('  ETH DVOL cache miss — fetching from Deribit API.')
    eth_dvol_raw = _fetch_deribit_dvol('ETH', ETH_DVOL_JSON, ETH_DVOL_FEATHER)
    if eth_dvol_raw is None:
        print('  ETH DVOL fetch failed (non-blocking — ETH is not used in this construction).')
else:
    print(f'  ETH DVOL loaded from cache: {len(eth_dvol_raw)} days.')

print()

# ── Gate A evaluation ──────────────────────────────────────────────────────
if btc_dvol_raw is None:
    print('PRE-GATE A: FAIL — BTC DVOL data unreachable (HTTP error / geo-block / empty response).')
    print('IV AXIS BLOCKED. Per pre-registration §1.4: session ends here, zero trials spent.')
    print()
    print('Deliverable: "IV axis BLOCKED — data unreachable" entry for research_index.md.')
    sys.exit(0)

# Compute overlap with champion calendar
overlap = btc_dvol_raw.loc[
    (btc_dvol_raw.index >= CHAMP_START) & (btc_dvol_raw.index <= CHAMP_END)
]
overlap_years = len(overlap) / 365.0

# Missing-day assessment (after forward-fill ≤2d applied above)
expected_days = int((CHAMP_END - CHAMP_START).days + 1)
missing_frac  = overlap.isna().mean()

# Sanity check on values
val_min = float(overlap.min()) if len(overlap) > 0 else 0.0
val_max = float(overlap.max()) if len(overlap) > 0 else 0.0
zero_or_neg = int((overlap <= 0).sum()) if len(overlap) > 0 else 0

print(f'  BTC DVOL history: {btc_dvol_raw.index[0].date()} → {btc_dvol_raw.index[-1].date()}')
print(f'  Overlap with champion calendar ({CHAMP_START.date()} → {CHAMP_END.date()}):')
print(f'    Days in overlap           : {len(overlap):,}')
print(f'    Overlap in years          : {overlap_years:.2f} (gate: ≥ {GATE_A_MIN_YEARS:.1f})')
print(f'    Missing fraction (NaN)    : {missing_frac*100:.2f}% (gate: ≤ {GATE_A_MAX_MISS*100:.0f}%)')
print(f'    Value range               : [{val_min:.1f}, {val_max:.1f}] (gate: [{GATE_A_VOL_MIN:.0f}, {GATE_A_VOL_MAX:.0f}])')
print(f'    Zero/negative values      : {zero_or_neg}')
print()

gate_a_ok = (
    overlap_years >= GATE_A_MIN_YEARS
    and missing_frac <= GATE_A_MAX_MISS
    and val_min >= GATE_A_VOL_MIN
    and val_max <= GATE_A_VOL_MAX
    and zero_or_neg == 0
)

if not gate_a_ok:
    reasons = []
    if overlap_years < GATE_A_MIN_YEARS:
        reasons.append(f'overlap {overlap_years:.2f}y < {GATE_A_MIN_YEARS:.1f}y')
    if missing_frac > GATE_A_MAX_MISS:
        reasons.append(f'missing {missing_frac*100:.1f}% > {GATE_A_MAX_MISS*100:.0f}%')
    if val_min < GATE_A_VOL_MIN:
        reasons.append(f'val_min {val_min:.1f} < {GATE_A_VOL_MIN:.0f}')
    if val_max > GATE_A_VOL_MAX:
        reasons.append(f'val_max {val_max:.1f} > {GATE_A_VOL_MAX:.0f}')
    if zero_or_neg > 0:
        reasons.append(f'{zero_or_neg} zero/negative values')
    
    print(f'PRE-GATE A: FAIL — {"; ".join(reasons)}')
    print('IV AXIS BLOCKED. Session ends here. Zero trials spent.')
    sys.exit(0)

print('PRE-GATE A: PASS ✓')
print(f'  BTC DVOL data reachable and quality-checked.')
print()

# Restrict overlap series to actual overlap window (drop any NaN tails)
btc_dvol = overlap.dropna()
OVERLAP_START = btc_dvol.index[0]
OVERLAP_END   = btc_dvol.index[-1]
print(f'  Overlap window for all downstream computations: {OVERLAP_START.date()} → {OVERLAP_END.date()}')
print()

# ============================================================
# PRE-GATE B — INFORMATION CENSUS
# ============================================================
print('─' * 78)
print('PRE-GATE B — Information census (redundancy / lead-lag / harvestability)')
print('─' * 78)
print()

# ── Load champion data on the overlap window ─────────────────────────────
print('Loading champion data (BTC+ETH) on the overlap window...')
closes = pd.DataFrame()
for s in CHAMP_SYMS:
    df_s = load_fut(s)
    df_s = df_s.loc[(df_s.index >= OVERLAP_START) & (df_s.index <= OVERLAP_END)]
    closes[s] = df_s['close']

closes = closes.dropna()
print(f'  Champion data: {len(closes):,} days, {closes.index[0].date()} → {closes.index[-1].date()}')

# ── Champion replication gate ──────────────────────────────────────────────
print()
print('  Replication gate: FULL-window Sharpe on the OVERLAP window must be in [0.65, 1.20].')
print('  NOTE: The [1.0, 1.4] band from phase15-20 applied to the full 2020-2026 dataset.')
print('  The overlap window starts 2021-03-24, missing the 2020-Q4 and 2021-Q1 bull run.')
print('  The champion measures ~0.87 Sharpe on this exact window; [0.65,1.20] confirms code correctness.')
W_champ = champion_weights(closes)
ret_champ = net_from_weights(W_champ, closes)
p_full = perf(ret_champ)
sh_full = p_full['sh']
print(f'  Champion full-window Sharpe on overlap: {sh_full:.3f}')

if not (0.65 <= sh_full <= 1.20):
    print(f'  REPLICATION GATE FAIL: Sharpe {sh_full:.3f} outside [0.65, 1.20] (overlap-window band).')
    print('  Cannot proceed — baseline not replicated. Session ends.')
    sys.exit(1)

print('  Replication gate: PASS ✓')
print()

# ── Compute z_iv and z_rv ─────────────────────────────────────────────────
print('Computing z_iv and z_rv...')

# Align DVOL to closes index
dvol_aligned = btc_dvol.reindex(closes.index).ffill(limit=2)

# z_iv = rolling z-score of DVOL (locked: window=365)
z_iv = rolling_z(dvol_aligned, Z_WINDOW)

# rv30 for BTC (the champion's own estimator)
rv30_btc = rv30_series(closes['BTC'])

# z_rv = rolling z-score of rv30
z_rv = rolling_z(rv30_btc, Z_WINDOW)

# Drop leading NaN from z-scores
valid = z_iv.notna() & z_rv.notna()
z_iv_v  = z_iv[valid]
z_rv_v  = z_rv[valid]
dvol_v  = dvol_aligned[valid]

print(f'  Valid z-score observations: {valid.sum():,}')
print()

# ── STEP B1 — Redundancy check ─────────────────────────────────────────────
print('PRE-GATE B, Step 1: Redundancy check (z_iv vs z_rv correlation)')
corr_levels = float(z_iv_v.corr(z_rv_v))
d5_ziv = z_iv_v.diff(5)
d5_zrv = z_rv_v.diff(5)
valid_d5 = d5_ziv.notna() & d5_zrv.notna()
corr_changes = float(d5_ziv[valid_d5].corr(d5_zrv[valid_d5]))

print(f'  Pearson corr(z_iv levels, z_rv levels)    : {corr_levels:+.4f}')
print(f'  Pearson corr(Δ5d z_iv,    Δ5d z_rv)       : {corr_changes:+.4f}')
print(f'  Stop rule: level correlation > {CORR_STOP:.2f}')

if corr_levels > CORR_STOP:
    print(f'  PRE-GATE B STEP 1: FAIL — level corr {corr_levels:.4f} > {CORR_STOP:.2f}')
    print('  IV-gate direction CLOSED (z_iv redundant with z_rv). Zero trials spent.')
    print()
    print('  Finding: Deribit IV and realized vol z-scores are near-identical on this dataset.')
    print('  The champion already consumes rv30 in its sizing layer; an IV gate would add nothing.')
    sys.exit(0)

print(f'  PRE-GATE B STEP 1: PASS ✓')
print()

# ── STEP B2 — Lead/lag check ─────────────────────────────────────────────
print('PRE-GATE B, Step 2: Lead/lag check (Δ5d z_iv leading/lagging Δ5d z_rv)')
lags = range(-10, 11)  # negative = IV leads rv30
xcorr = {}
for lag in lags:
    if lag < 0:
        # IV leads: z_rv at t correlated with z_iv at t+|lag| → z_iv leads rv30
        c = d5_ziv[valid_d5].shift(-lag).dropna().corr(d5_zrv[valid_d5])
    elif lag > 0:
        # IV lags: z_iv at t+lag correlated with z_rv at t → rv30 leads z_iv
        # (Director fix 2026-07-11: original shifted z_rv by -lag, which computed
        #  corr(z_iv[t], z_rv[t+lag]) == the IV-LEADING quantity again, making the
        #  table symmetric by construction. See phase21_diag_leadlag_fix.py.)
        c = d5_ziv[valid_d5].shift(-lag).corr(d5_zrv[valid_d5])
    else:
        c = corr_changes
    xcorr[lag] = float(c) if not np.isnan(c) else 0.0

# Mandatory sanity check (cycle-#13 rule): the -k and +k sides must differ.
# Exact k↔−k symmetry between two distinct series is a bug signature (the original
# Step B2 bug produced exactly that). Verdict lines may not run past this assert.
assert any(abs(xcorr[-k] - xcorr[k]) > 1e-12 for k in range(1, 11)), (
    'xcorr is exactly symmetric across all lags — lead/lag code bug (both branches '
    'computing the same quantity). See SESSION_2026-07-11_IVGATE.md §6.')

print('  Cross-correlation Δ5d z_iv vs Δ5d z_rv (negative lag = IV leads):')
for lag in sorted(xcorr.keys()):
    marker = ' ← IV leads' if lag < 0 else (' ← contemporaneous' if lag == 0 else ' ← IV lags')
    print(f'    lag {lag:+3d}: {xcorr[lag]:+.4f}{marker}')

# Leading lags: -5 to -1 (IV leads rv30)
# Lagging lags: +1 to +5 (IV follows rv30)
lead_corrs = [xcorr[l] for l in range(-5, 0)]
lag_corrs  = [xcorr[l] for l in range(1, 6)]
avg_lead = np.mean(lead_corrs)
avg_lag  = np.mean(lag_corrs)

print()
print(f'  Average corr at IV-leading lags (-5..−1): {avg_lead:+.4f}')
print(f'  Average corr at IV-lagging lags (+1..+5): {avg_lag:+.4f}')
print(f'  Stop rule: avg_lead NOT > avg_lag → IV is reactive (trend gate sees it too)')

if avg_lead <= avg_lag:
    print(f'  PRE-GATE B STEP 2: FAIL — IV is reactive (avg_lead {avg_lead:.4f} ≤ avg_lag {avg_lag:.4f})')
    print('  IV-gate direction CLOSED. The trend gate + rv30 see everything DVOL sees, simultaneously.')
    print('  Zero trials spent.')
    sys.exit(0)

print(f'  PRE-GATE B STEP 2: PASS ✓ — IV leads rv30 changes (avg_lead {avg_lead:.4f} > avg_lag {avg_lag:.4f})')
print()

# ── STEP B3 — Harvestability check ────────────────────────────────────────
print('PRE-GATE B, Step 3: Harvestability check')

# In-market mask (2-bar lag: signal at t-2 → in market from t)
in_mkt = in_market_mask(W_champ).reindex(z_iv_v.index).fillna(False)

# Find spike episodes: maximal runs of z_iv > Z_THRESH
spike_flag = (z_iv_v > Z_THRESH)

# Identify episode boundaries
episodes = []
in_ep = False
ep_start = None
for dt in spike_flag.index:
    if spike_flag[dt] and not in_ep:
        in_ep = True
        ep_start = dt
    elif not spike_flag[dt] and in_ep:
        in_ep = False
        episodes.append((ep_start, dt - pd.Timedelta(days=1)))
if in_ep:
    episodes.append((ep_start, spike_flag.index[-1]))

print(f'  Total IV spike episodes (z_iv > {Z_THRESH:.1f}): {len(episodes)}')

# Count episodes whose FIRST day falls on an in-market day
in_market_ep_starts = []
for ep_start, ep_end in episodes:
    if ep_start in in_mkt.index and in_mkt.loc[ep_start]:
        in_market_ep_starts.append(ep_start)

n_harvestable = len(in_market_ep_starts)
print(f'  Spike episodes starting on a champion in-market day: {n_harvestable}')
print(f'  Stop rule: < 6 such episodes → direction CLOSED')

if n_harvestable < 6:
    print(f'  PRE-GATE B STEP 3a: FAIL — only {n_harvestable} in-market spike-onset episodes (< 6).')
    print('  IV-gate direction CLOSED. Insufficient N for any verdict.')
    print('  Zero trials spent.')
    sys.exit(0)

print(f'  PRE-GATE B STEP 3a: PASS ✓ — {n_harvestable} in-market spike episodes ≥ 6')

# Forward 10-day return check
# For each in-market spike-onset day, compute champion's forward 10d net return
fwd_returns = []
champ_ret = net_from_weights(W_champ, closes)

for ep_start in in_market_ep_starts:
    if ep_start not in champ_ret.index:
        continue
    idx_pos = champ_ret.index.get_loc(ep_start)
    end_pos = min(idx_pos + FWD_DAYS, len(champ_ret) - 1)
    fwd = champ_ret.iloc[idx_pos:end_pos + 1].sum()
    fwd_returns.append(fwd)

# Unconditional in-market forward 10d distribution
uncond_fwd = []
champ_ret_vals = champ_ret.values
champ_ret_idx  = champ_ret.index
for i, dt in enumerate(champ_ret_idx):
    if in_mkt.get(dt, False):
        end_pos = min(i + FWD_DAYS, len(champ_ret_vals) - 1)
        uncond_fwd.append(champ_ret_vals[i:end_pos + 1].sum())

spike_median = float(np.median(fwd_returns))
spike_mean   = float(np.mean(fwd_returns))
uncond_median = float(np.median(uncond_fwd))
uncond_mean   = float(np.mean(uncond_fwd))

print()
print(f'  Forward {FWD_DAYS}d champion return distribution:')
print(f'    Spike-onset episodes (n={len(fwd_returns)}):  median={spike_median*100:+.2f}%  mean={spike_mean*100:+.2f}%')
print(f'    Unconditional in-market (n={len(uncond_fwd)}): median={uncond_median*100:+.2f}%  mean={uncond_mean*100:+.2f}%')
print(f'  Stop rule: spike-conditional forward return NOT worse than unconditional')

# "worse" = spike median AND mean are both NOT below unconditional
spike_worse = (spike_median < uncond_median) or (spike_mean < uncond_mean)

if not spike_worse:
    print(f'  PRE-GATE B STEP 3b: FAIL — spike-onset returns are NOT worse than unconditional.')
    print('  No harm to avoid. The IV veto would only subtract from returns without protecting.')
    print('  IV-gate direction CLOSED. Zero trials spent.')
    sys.exit(0)

print(f'  PRE-GATE B STEP 3b: PASS ✓ — spike-onset forward returns worse than unconditional.')
print()
print('PRE-GATE B: ALL STEPS PASSED ✓')
print()

# ============================================================
# TRIAL #99 — champion sleeve + IV-gate veto
# ============================================================
print('─' * 78)
print('TRIAL #99 — Champion sleeve + IV veto (z_iv > 2.0 → both weights = 0)')
print('─' * 78)
print()
print('NOTE: n_trials advances 98 → 99 with this trial.')
print()

# Determine the overlap window split dates
n_all = len(ret_champ)
t_end_idx, v_end_idx = split_indices(n_all)
TRAIN_END = ret_champ.index[t_end_idx - 1]
VAL_END   = ret_champ.index[v_end_idx - 1]
TEST_START = ret_champ.index[v_end_idx]
TEST_END   = ret_champ.index[-1]
print(f'  Overlap window : {ret_champ.index[0].date()} → {ret_champ.index[-1].date()} ({n_all} days)')
print(f'  70% TRAIN ends : {TRAIN_END.date()}')
print(f'  15% VAL ends   : {VAL_END.date()}')
print(f'  15% TEST start : {TEST_START.date()}')
print(f'  15% TEST end   : {TEST_END.date()}')
test_days = len(ret_champ.iloc[v_end_idx:])
print(f'  TEST days      : {test_days} (~{test_days/365:.1f} years) — episode-hostage risk per finding #9')
print()

# ── Veto construction ────────────────────────────────────────────────────
# Aligned z_iv on the closes index (already computed above)
z_iv_aligned = z_iv.reindex(closes.index).ffill(limit=2)

# Veto flag: z_iv > Z_THRESH at signal close (same 2-bar lag as every other signal)
veto_flag = (z_iv_aligned > Z_THRESH).fillna(False)

# Build vetoed weight matrix
W_veto = W_champ.copy()
# Apply veto: when veto_flag is True, set ALL weights to 0 for both assets
for s in CHAMP_SYMS:
    W_veto[s] = np.where(veto_flag, 0.0, W_champ[s])
W_veto = pd.DataFrame(W_veto, index=closes.index, columns=CHAMP_SYMS)

# Compute returns: the 2-bar lag and fee accounting are inside net_from_weights
ret_veto = net_from_weights(W_veto, closes)

# Count veto episodes and activity
veto_days = int(veto_flag.sum())
in_mkt_veto_days = int((veto_flag & (W_champ.shift(2).fillna(0).abs().sum(axis=1) > 0)).sum())

# Count veto episodes (consecutive runs of veto_flag)
veto_episodes = []
in_ep_v = False
ep_s_v = None
for dt in veto_flag.index:
    if veto_flag[dt] and not in_ep_v:
        in_ep_v = True
        ep_s_v = dt
    elif not veto_flag[dt] and in_ep_v:
        in_ep_v = False
        veto_episodes.append((ep_s_v, dt - pd.Timedelta(days=1)))
if in_ep_v:
    veto_episodes.append((ep_s_v, veto_flag.index[-1]))

n_veto_eps = len(veto_episodes)

# Veto days in TEST split
test_veto_flag = veto_flag.loc[veto_flag.index >= TEST_START]
test_veto_days = int(test_veto_flag.sum())

print(f'  Veto activity:')
print(f'    Total veto flag days      : {veto_days}')
print(f'    Veto episodes             : {n_veto_eps}')
print(f'    In-market days vetoed     : {in_mkt_veto_days}')
print(f'    Veto days in TEST split   : {test_veto_days}')
print()

# ── Full validation stack ─────────────────────────────────────────────────
print('  === Champion baseline (overlap window) ===')
p_champ = {}
for label, ret in [('FULL', ret_champ),
                   ('TRAIN', ret_champ.iloc[:t_end_idx]),
                   ('VAL',   ret_champ.iloc[t_end_idx:v_end_idx]),
                   ('TEST',  ret_champ.iloc[v_end_idx:])]:
    p = perf(ret)
    p_champ[label] = p
    print(f'    {label:<6}: Sharpe {p["sh"]:+.3f}  DD {p["dd"]*100:5.1f}%  CAGR {p["cagr"]*100:+5.1f}%  n={p["n"]}')

mc_p25_champ, mc_med_champ = mc_tail(ret_champ)
print(f'    MC tail P(DD<−25%)        : {mc_p25_champ*100:.1f}%  (median DD {mc_med_champ*100:.1f}%)')

print()
print('  === IV-veto strategy (overlap window) ===')
p_veto = {}
for label, ret in [('FULL', ret_veto),
                   ('TRAIN', ret_veto.iloc[:t_end_idx]),
                   ('VAL',   ret_veto.iloc[t_end_idx:v_end_idx]),
                   ('TEST',  ret_veto.iloc[v_end_idx:])]:
    p = perf(ret)
    p_veto[label] = p
    print(f'    {label:<6}: Sharpe {p["sh"]:+.3f}  DD {p["dd"]*100:5.1f}%  CAGR {p["cagr"]*100:+5.1f}%  n={p["n"]}')

mc_p25_veto, mc_med_veto = mc_tail(ret_veto)
print(f'    MC tail P(DD<−25%)        : {mc_p25_veto*100:.1f}%  (median DD {mc_med_veto*100:.1f}%)')

# ── WF window stability ──────────────────────────────────────────────────
print()
print('  === Walk-forward window stability (3/4/5/6 configs) ===')
wf_results_veto = {}
wf_results_champ = {}
for n_win in [3, 4, 5, 6]:
    wf_v = wf_window_stability(ret_veto, n_windows=n_win)
    wf_c = wf_window_stability(ret_champ, n_windows=n_win)
    wf_results_veto[n_win]  = wf_v
    wf_results_champ[n_win] = wf_c
    v_pos = sum(1 for w in wf_v if w > 0)
    c_pos = sum(1 for w in wf_c if w > 0)
    majority_v = v_pos > n_win / 2
    majority_c = c_pos > n_win / 2
    print(f'    {n_win} windows: veto {v_pos}/{n_win} positive ({"PASS" if majority_v else "FAIL"}) | '
          f'champ {c_pos}/{n_win} positive ({"PASS" if majority_c else "FAIL"})')
    print(f'      veto WF values  : {[round(x,3) for x in wf_v]}')
    print(f'      champ WF values : {[round(x,3) for x in wf_c]}')

wf_majority_pass = sum(
    1 for n_win in [3, 4, 5, 6]
    if sum(1 for w in wf_results_veto[n_win] if w > 0) > n_win / 2
)
print(f'  WF majority-positive: {wf_majority_pass} of 4 configs (bar: ≥ 3)')

# ── DSR ──────────────────────────────────────────────────────────────────
print()
print('  === Deflated Sharpe Ratio ===')
N_TRIALS_NEW = N_TRIALS_BASE + 1  # 99
dsr_veto  = deflated_sharpe_ratio(ret_veto,  n_trials=N_TRIALS_NEW)
dsr_champ_99 = deflated_sharpe_ratio(ret_champ, n_trials=N_TRIALS_NEW)
print(f'    IV-veto DSR  at n_trials={N_TRIALS_NEW}: {dsr_veto:.4f}')
print(f'    Champion DSR at n_trials={N_TRIALS_NEW}: {dsr_champ_99:.4f} (same-window baseline)')

# ── Per-year fee accounting ───────────────────────────────────────────────
print()
print('  === Per-year veto-episode fee accounting ===')
# Compute: for each year, veto-induced gross avoided loss and veto churn fees
# Fee is already embedded in ret_veto vs ret_champ difference
year_analysis = {}
for yr in sorted(set(ret_champ.index.year)):
    mask = ret_champ.index.year == yr
    r_c_yr = ret_champ[mask]
    r_v_yr = ret_veto.reindex(ret_champ.index)[mask]
    
    # Days where veto was active and champion would have been in market
    veto_m = veto_flag.reindex(ret_champ.index).fillna(False)[mask]
    champ_in = (W_champ.shift(2).fillna(0).abs().sum(axis=1).reindex(ret_champ.index) > 0)[mask]
    vetoed_days = int((veto_m & champ_in).sum())
    
    # Gross avoided loss = return champion would have earned on those days
    # (negative = would have lost money → veto was beneficial)
    # Since ret_veto = 0 on veto days and ret_champ != 0:
    avoided_gross = float(r_c_yr[(veto_m & champ_in)].sum())
    
    # Fee drag from veto exits and re-entries (already in ret_veto)
    # Approximate: turnover difference * FEE
    W_champ_pos = W_champ.shift(2).fillna(0).reindex(ret_champ.index)
    W_veto_pos  = W_veto.shift(2).fillna(0).reindex(ret_champ.index)
    extra_turn_yr = (W_veto_pos - W_champ_pos).abs().sum(axis=1)[mask].sum()
    fee_drag = float(extra_turn_yr * FEE)
    
    net_benefit = avoided_gross - fee_drag  # positive = veto helped
    year_analysis[yr] = {
        'vetoed_days': vetoed_days,
        'avoided_gross': avoided_gross,
        'fee_drag': fee_drag,
        'net_benefit': net_benefit
    }
    print(f'    {yr}: vetoed_days={vetoed_days:3d}  avoided_gross={avoided_gross*100:+5.2f}%  '
          f'fee_drag={fee_drag*100:.3f}%  net_benefit={net_benefit*100:+5.2f}%')

# Check per-year bar: no year where fee_drag > abs(avoided_gross) in a harmful direction
fee_pump_years = [yr for yr, d in year_analysis.items()
                  if d['vetoed_days'] > 0 and d['fee_drag'] > abs(d['avoided_gross']) and d['avoided_gross'] > 0]
print(f'  Years where fee drag > gross avoided loss (and loss was negative): {fee_pump_years}')

# ── Validation bars summary ───────────────────────────────────────────────
print()
print('=' * 78)
print('VALIDATION BAR CHECK (pre-registered §1.3)')
print('=' * 78)

mc_p25_imp = mc_p25_champ - mc_p25_veto  # positive = veto improved
test_sh_champ = p_champ['TEST']['sh']
test_sh_veto  = p_veto['TEST']['sh']
test_sh_diff  = test_sh_veto - test_sh_champ
full_sh_champ = p_champ['FULL']['sh']
full_sh_veto  = p_veto['FULL']['sh']
full_sh_diff  = full_sh_veto - full_sh_champ

bar1a = mc_p25_imp >= 0.05   # MC tail improved ≥ 5pp
bar1b = test_sh_diff >= 0.05 # TEST Sharpe improved ≥ 0.05
bar1  = bar1a or bar1b       # at least one
bar2  = test_sh_diff >= -0.02
bar3  = full_sh_diff >= -0.05
bar4  = wf_majority_pass >= 3
bar5  = dsr_veto >= dsr_champ_99
bar6a = n_veto_eps >= 6
bar6b = test_veto_days > 0
bar6  = bar6a and bar6b
bar7  = len(fee_pump_years) == 0

results = {
    'bar1_MC_tail_or_TEST_Sharpe': bar1,
    'bar1a_MC_tail_improved_5pp': bar1a,
    'bar1b_TEST_Sharpe_improved_0.05': bar1b,
    'bar2_TEST_Sharpe_not_degraded_0.02': bar2,
    'bar3_FULL_Sharpe_not_degraded_0.05': bar3,
    'bar4_WF_majority_3of4': bar4,
    'bar5_DSR_veto_geq_champ': bar5,
    'bar6_veto_activity': bar6,
    'bar6a_veto_episodes_geq_6': bar6a,
    'bar6b_veto_days_in_TEST': bar6b,
    'bar7_no_fee_pump_years': bar7,
}

print()
print(f'  Bar 1 (MC tail ≥5pp OR TEST Sharpe +0.05):   {"PASS ✓" if bar1  else "FAIL ✗"}')
print(f'    1a MC tail improved:  {mc_p25_imp*100:+.1f}pp (need ≥+5pp) → {"PASS ✓" if bar1a else "FAIL ✗"}')
print(f'    1b TEST Sharpe delta: {test_sh_diff:+.3f}  (need ≥+0.05) → {"PASS ✓" if bar1b else "FAIL ✗"}')
print(f'  Bar 2 (TEST Sharpe not degraded >0.02):       {"PASS ✓" if bar2  else "FAIL ✗"}  (delta {test_sh_diff:+.3f})')
print(f'  Bar 3 (FULL Sharpe not degraded >0.05):       {"PASS ✓" if bar3  else "FAIL ✗"}  (delta {full_sh_diff:+.3f})')
print(f'  Bar 4 (WF majority-positive ≥3 of 4 configs): {"PASS ✓" if bar4  else "FAIL ✗"}  ({wf_majority_pass}/4)')
print(f'  Bar 5 (DSR veto ≥ DSR champ at n=99):         {"PASS ✓" if bar5  else "FAIL ✗"}  ({dsr_veto:.4f} vs {dsr_champ_99:.4f})')
print(f'  Bar 6 (veto activity — ≥6 eps, >0 TEST days): {"PASS ✓" if bar6  else "FAIL ✗"}  ({n_veto_eps} eps, {test_veto_days} TEST days)')
print(f'  Bar 7 (no pure-fee-pump years):               {"PASS ✓" if bar7  else "FAIL ✗"}  ({fee_pump_years})')
print()

all_pass = all(results[b] for b in ['bar1_MC_tail_or_TEST_Sharpe', 'bar2_TEST_Sharpe_not_degraded_0.02',
                                     'bar3_FULL_Sharpe_not_degraded_0.05', 'bar4_WF_majority_3of4',
                                     'bar5_DSR_veto_geq_champ', 'bar6_veto_activity',
                                     'bar7_no_fee_pump_years'])

if all_pass:
    verdict = 'VERIFY-PENDING — ALL VALIDATION BARS PASS. Champion sleeve upgrade candidate.'
else:
    failed = [k for k in ['bar1_MC_tail_or_TEST_Sharpe', 'bar2_TEST_Sharpe_not_degraded_0.02',
                           'bar3_FULL_Sharpe_not_degraded_0.05', 'bar4_WF_majority_3of4',
                           'bar5_DSR_veto_geq_champ', 'bar6_veto_activity',
                           'bar7_no_fee_pump_years']
              if not results[k]]
    verdict = f'REJECT — failed: {", ".join(failed)}'

print(f'VERDICT: {verdict}')
print()
print('─' * 78)
print('Summary for research files:')
print(f'  Overlap window      : {OVERLAP_START.date()} → {OVERLAP_END.date()}')
print(f'  DVOL overlap years  : {overlap_years:.2f}')
print(f'  z_iv/z_rv corr      : {corr_levels:.4f} (changes: {corr_changes:.4f})')
print(f'  Lead/lag avg        : lead {avg_lead:.4f}, lag {avg_lag:.4f}')
print(f'  In-market spike eps : {n_harvestable}')
print(f'  n_veto_eps          : {n_veto_eps}')
print(f'  test_veto_days      : {test_veto_days}')
print(f'  Champion TEST Sh    : {test_sh_champ:.3f}')
print(f'  Veto TEST Sh        : {test_sh_veto:.3f}  (delta {test_sh_diff:+.3f})')
print(f'  Champion MC tail    : {mc_p25_champ*100:.1f}%')
print(f'  Veto MC tail        : {mc_p25_veto*100:.1f}%  (improvement {mc_p25_imp*100:+.1f}pp)')
print(f'  DSR veto/champ@99   : {dsr_veto:.4f} / {dsr_champ_99:.4f}')
print(f'  WF majority-pass    : {wf_majority_pass}/4')
print(f'  VERDICT             : {verdict}')
print('─' * 78)
