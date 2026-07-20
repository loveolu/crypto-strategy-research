"""
Phase 14: H-COT — CFTC Commitment-of-Traders crowding filter on TrendVolTarget.

PRE-REGISTERED experiment (trial #96 in the project's cumulative DSR ledger).
ONE feature, ONE rule, no variants:

  Feature: am_net_frac = (asset_mgr_positions_long - asset_mgr_positions_short)
           / open_interest_all, from the CFTC Traders-in-Financial-Futures
           (Futures Only) report for BITCOIN - CHICAGO MERCANTILE EXCHANGE.
           z-scored over a trailing 52-week window (rolling, min 26 weeks;
           NaN / no-filter before that).
  Rule:    when z > +2 (crowded institutional longs), halve the champion's
           vt_scale (post-quantization, i.e. quantized scale * 0.5) on BOTH
           legs (BTC and ETH) — the hypothesis names CME *Bitcoin* futures
           positioning as the crowding gauge for the whole champion.
           The filter NEVER increases exposure and never touches entry/exit.

Timing hygiene (no lookahead):
  report_date_as_yyyy_mm_dd is the Tuesday the data is AS OF; public release
  is the following Friday ~15:30 ET. Each report's values become usable only
  from report_date + 6 calendar days (the following Monday), then are
  forward-filled to daily frequency. On top of that the harness applies its
  standard 2-bar execution lag. So each COT value is 6-12 days old when it
  first affects a position, plus 2 more days of execution lag.

Data cache: user_data/research/data/cot/{BITCOIN,ETHER}_tff_futonly.csv
  (full raw Socrata rows; re-download skipped if cache exists).

Pipeline conventions identical to phase11/12/13: fees 0.15%/side, 2-bar lag,
70/15/15 chronological split, 4-window walk-forward, monthly-block Monte
Carlo (500 sims), daily feather files from user_data/data/okx/futures/.
DSR from freqtrade_dsr.py (repo root) at n_trials=96.
"""
import sys
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')

import json
import urllib.request
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd

from freqtrade_dsr import deflated_sharpe_ratio  # AGPL module, repo root — imported, not copied

FEE = 0.0015
FUT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/data/okx/futures')
COT_DIR = Path('C:/Users/Comec/Projects/freqtrade/user_data/research/data/cot')
COT_DIR.mkdir(parents=True, exist_ok=True)

SOCRATA_URL = 'https://publicreporting.cftc.gov/resource/gpe5-46if.json'
# NOTE: the CME ETH contract is named 'ETHER CASH SETTLED' in the Socrata
# dataset (plain 'ETHER' returns 0 rows). Naming fix only — the pre-registered
# rule uses BITCOIN data; ETH COT is cached as a deliverable.
COT_MARKETS = ['BITCOIN', 'ETHER CASH SETTLED']
RELEASE_LAG_DAYS = 6          # report Tuesday -> usable following Monday
Z_WINDOW = 52                 # trailing weeks for z-score
Z_MIN_PERIODS = 26            # minimum weeks before signal usable
Z_THRESHOLD = 2.0             # pre-registered: z > +2 -> halve vt_scale
FILTER_MULT = 0.5
N_TRIALS = 96                 # cumulative project trial count incl. this one


# ---------------------------------------------------------------- download
def download_cot(market: str) -> Path:
    """Download full TFF FutOnly history for one contract_market_name; cache CSV."""
    fp = COT_DIR / f"{market.replace(' ', '_')}_tff_futonly.csv"
    if fp.exists():
        print(f"  cache hit: {fp.name}")
        return fp
    rows, offset, limit = [], 0, 50000
    while True:
        params = {
            '$where': f"contract_market_name='{market}'",
            '$order': 'report_date_as_yyyy_mm_dd',
            '$limit': str(limit),
            '$offset': str(offset),
        }
        url = SOCRATA_URL + '?' + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=60) as r:
            batch = json.loads(r.read().decode())
        rows.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    df = pd.DataFrame(rows)
    df.to_csv(fp, index=False)
    print(f"  downloaded {len(df)} rows -> {fp.name}")
    return fp


def load_cot(market: str) -> pd.DataFrame:
    fp = download_cot(market)
    df = pd.read_csv(fp)
    df['report_date'] = pd.to_datetime(df['report_date_as_yyyy_mm_dd'])
    cols = ['open_interest_all', 'asset_mgr_positions_long', 'asset_mgr_positions_short',
            'lev_money_positions_long', 'lev_money_positions_short']
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df[['report_date'] + cols].sort_values('report_date').drop_duplicates('report_date')
    return df.set_index('report_date')


# ---------------------------------------------------------------- feature
def build_daily_z(cot: pd.DataFrame, daily_index: pd.DatetimeIndex) -> pd.Series:
    """am_net_frac weekly z-score, release-lagged, forward-filled to daily."""
    amf = (cot['asset_mgr_positions_long'] - cot['asset_mgr_positions_short']) / cot['open_interest_all']
    mu = amf.rolling(Z_WINDOW, min_periods=Z_MIN_PERIODS).mean()
    sd = amf.rolling(Z_WINDOW, min_periods=Z_MIN_PERIODS).std()
    z = (amf - mu) / sd
    # release lag: usable only from report_date + RELEASE_LAG_DAYS (following Monday)
    z_eff = z.copy()
    z_eff.index = z_eff.index + pd.Timedelta(days=RELEASE_LAG_DAYS)
    # tz-align with OHLCV index (feather dates are tz-aware UTC)
    if daily_index.tz is not None and z_eff.index.tz is None:
        z_eff.index = z_eff.index.tz_localize(daily_index.tz)
    # forward-fill weekly values to daily
    combined = z_eff.reindex(z_eff.index.union(daily_index)).ffill()
    return combined.reindex(daily_index)


# ---------------------------------------------------------------- champion
def _sma(s, n): return s.rolling(n).mean()
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()

def load_fut(sym):
    df = pd.read_feather(FUT_DIR / f'{sym}_USDT_USDT-1d-futures.feather')
    return df.set_index('date').sort_index().astype(
        {c: float for c in ['open', 'high', 'low', 'close', 'volume']})

SYMS = ['BTC', 'ETH']
closes = pd.DataFrame({s: load_fut(s)['close'] for s in SYMS}).sort_index()
ret_mat = closes.pct_change()

core, scale = pd.DataFrame(index=closes.index), pd.DataFrame(index=closes.index)
for s in SYMS:
    c = closes[s]
    core[s] = ((c > _sma(c, 200)) & (c.pct_change(30) > 0) & (_ema(c, 20) > _ema(c, 50))).astype(float)
    rv = c.pct_change().rolling(30).std() * np.sqrt(365)
    scale[s] = (0.40 / rv).clip(0, 1)

vt_scale_q = ((core * scale) / 0.25).round() * 0.25  # quantized vt_scale per asset
vt_scale_q = vt_scale_q.clip(0, 1)


def net_from_weights(W):
    W = W.reindex(closes.index).fillna(0)
    pos = W.shift(2).fillna(0)  # 2-bar lag: signal close[t] -> exec open[t+1] -> held close[t+1]
    gross = (pos * ret_mat.fillna(0)).sum(axis=1)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()
    return (gross - turn * FEE).dropna(), pos


# ---------------------------------------------------------------- evaluation
def m(ret):
    ret = ret.dropna()
    if len(ret) < 10 or ret.std() == 0:
        return 0.0, 0.0, 0.0
    eq = (1 + ret).cumprod()
    yrs = len(ret) / 365
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1
    return ret.mean() / ret.std() * np.sqrt(365), float((eq / eq.cummax() - 1).min()), cagr


def full_validation(ret, label):
    """phase12/13 convention: full + 70/15/15 + 4-window WF + monthly-block MC."""
    ret = ret.dropna()
    n = len(ret)
    i1, i2 = int(n * 0.70), int(n * 0.85)
    sh_f, dd_f, cg_f = m(ret)
    sh_tr, _, _ = m(ret.iloc[:i1])
    sh_vl, _, _ = m(ret.iloc[i1:i2])
    sh_te, dd_te, cg_te = m(ret.iloc[i2:])
    wf = []
    for k in range(4):
        s_i, e_i = int(n * (0.5 + k * 0.125)), min(int(n * (0.5 + (k + 1) * 0.125)), n)
        wf.append(m(ret.iloc[s_i:e_i]))
    blocks = [g.values for _, g in ret.groupby([ret.index.year, ret.index.month])]
    rng = np.random.default_rng(11)
    dds = []
    for _ in range(500):
        seq = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        eq = np.cumprod(1 + seq)
        dds.append((eq / np.maximum.accumulate(eq) - 1).min())
    p_dd25 = float((np.array(dds) < -0.25).mean())
    print(f"\n{label}")
    print(f"  FULL  Sharpe {sh_f:5.2f}  DD {dd_f*100:6.1f}%  CAGR {cg_f*100:+6.1f}%")
    print(f"  TRAIN {sh_tr:5.2f} | VAL {sh_vl:5.2f} | TEST {sh_te:5.2f}  (TEST CAGR {cg_te*100:+5.1f}%, DD {dd_te*100:5.1f}%)")
    print(f"  WF: " + " ".join(f"{x[0]:+.2f}" for x in wf) + f"  pos {sum(1 for x in wf if x[2] > 0)}/4"
          f"   MC medDD {np.percentile(dds, 50)*100:.0f}% P(DD<-25%) {p_dd25*100:.0f}%")
    return {'full_sharpe': sh_f, 'full_dd': dd_f, 'full_cagr': cg_f,
            'train_sh': sh_tr, 'val_sh': sh_vl, 'test_sh': sh_te,
            'test_dd': dd_te, 'test_cagr': cg_te,
            'wf': [w[0] for w in wf], 'wf_pos': sum(1 for x in wf if x[2] > 0),
            'mc_med_dd': float(np.percentile(dds, 50)), 'mc_p_dd25': p_dd25}


# =================================================================
print("=" * 78)
print("PHASE 14 — H-COT: CFTC asset-manager crowding filter on TrendVolTarget")
print("=" * 78)

print("\n[1] COT data download/cache")
cot = {mkt: load_cot(mkt) for mkt in COT_MARKETS}
for mkt, df in cot.items():
    print(f"  {mkt}: {len(df)} weekly reports, {df.index.min().date()} .. {df.index.max().date()}")

z_daily = build_daily_z(cot['BITCOIN'], closes.index)

print("\n[2] Baseline replication check (champion TVT BTC+ETH, phase13 convention)")
W_base = vt_scale_q / len(SYMS)
ret_base, pos_base = net_from_weights(W_base)
res_base = full_validation(ret_base, "BASELINE: champion TVT BTC+ETH")
ok = 0.30 <= res_base['test_sh'] <= 0.50 and 1.1 <= res_base['full_sharpe'] <= 1.4
print(f"\n  Replication check: TEST Sharpe {res_base['test_sh']:.2f} (expect ~0.39-0.41), "
      f"FULL Sharpe {res_base['full_sharpe']:.2f} (expect ~1.2-1.3) -> {'OK' if ok else 'MISMATCH — STOP'}")
if not ok:
    sys.exit("Baseline replication failed; aborting before filter evaluation.")

print("\n[3] Filter activity (BTC am_net_frac 52w z, release-lagged +6d)")
z_valid = z_daily.dropna()
active = z_daily > Z_THRESHOLD  # NaN -> False -> no filter (per spec)
in_market = pos_base.sum(axis=1) > 0
n_active = int(active.sum())
n_active_inmkt = int((active & in_market.reindex(active.index).fillna(False)).sum())
n_inmkt = int(in_market.sum())
print(f"  z coverage: {len(z_valid)}/{len(z_daily)} daily bars "
      f"({z_valid.index.min().date()} .. {z_valid.index.max().date()})")
print(f"  weekly reports with z>+2: {int(((cot['BITCOIN'].pipe(lambda d: (d['asset_mgr_positions_long']-d['asset_mgr_positions_short'])/d['open_interest_all']).pipe(lambda a: (a - a.rolling(Z_WINDOW, min_periods=Z_MIN_PERIODS).mean()) / a.rolling(Z_WINDOW, min_periods=Z_MIN_PERIODS).std())) > Z_THRESHOLD).sum())}"
      f" / {len(cot['BITCOIN'])}")
print(f"  daily bars filter active (z>+2): {n_active} ({n_active/len(z_daily)*100:.1f}% of all bars)")
print(f"  filter active AND champion in-market: {n_active_inmkt} of {n_inmkt} in-market days "
      f"({(n_active_inmkt/n_inmkt*100 if n_inmkt else 0):.1f}%)")

print("\n[4] Filtered variant (pre-registered rule: z>+2 -> vt_scale * 0.5)")
mult = pd.Series(np.where(active.values, FILTER_MULT, 1.0), index=closes.index)
W_filt = vt_scale_q.mul(mult, axis=0) / len(SYMS)
ret_filt, pos_filt = net_from_weights(W_filt)
res_filt = full_validation(ret_filt, "FILTERED: champion + COT crowding filter")

print("\n[5] Comparison (judged on TEST Sharpe, TEST DD, MC P(DD<-25%))")
print(f"  {'metric':<22}{'baseline':>12}{'filtered':>12}")
for k, fmt in [('test_sh', '{:.3f}'), ('test_dd', '{:.1%}'), ('test_cagr', '{:.1%}'),
               ('mc_p_dd25', '{:.1%}'), ('mc_med_dd', '{:.1%}'),
               ('full_sharpe', '{:.3f}'), ('full_dd', '{:.1%}'), ('wf_pos', '{}')]:
    print(f"  {k:<22}{fmt.format(res_base[k]):>12}{fmt.format(res_filt[k]):>12}")

print("\n[6] Deflated Sharpe Ratio (per-day returns, n_trials=96)")
for label, r in [("baseline (reference)", ret_base), ("FILTERED (this trial)", ret_filt)]:
    res = deflated_sharpe_ratio(r.tolist(), n_trials=N_TRIALS)
    sr0_ann = res['sr0_benchmark'] * np.sqrt(365)
    print(f"  {label:<22} DSR={res['dsr']:.4f}  (benchmark ann. Sharpe {sr0_ann:.2f}, "
          f"skew {res['skew']:+.2f}, kurt {res['kurtosis']:.1f}, n_obs {res['n_obs']})")

# thin-sample guard (pre-registered): <5% of in-market days -> INCONCLUSIVE
frac_inmkt = n_active_inmkt / n_inmkt if n_inmkt else 0.0
print("\n[7] Verdict inputs")
print(f"  filter touched {frac_inmkt*100:.1f}% of in-market days "
      f"({'>= 5% — sample adequate' if frac_inmkt >= 0.05 else '< 5% — SAMPLE TOO THIN, verdict is INCONCLUSIVE-THIN-SAMPLE'})")
