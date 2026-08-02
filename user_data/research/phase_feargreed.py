"""T-035 / H-FearGreed pre-gate script.

READ-IF-EXISTS GUARD ADDED 2026-08-01 (A-008). This is a frozen phase*.py
reproduction artifact and ARCHIVE_COST_NOTE.md rule 1 normally forbids editing
it. The exemption is overridden here, deliberately, and the reasoning is
recorded so it is not reverted as a rule violation:

  * The exemption exists to protect ARCHIVED NUMBERS. This guard changes no
    number the script computes. It changes only where the raw bytes come from —
    disk instead of the network — and on an unchanged file that is the same
    input. Reproduction fidelity is preserved, not weakened.
  * The script is not inert history. It is EXECUTABLE AND DESTRUCTIVE: it opened
    its raw artifact with mode "w" and re-fetched unconditionally on every run.
  * The Independent Reviewer standard actively instructs people to re-run the
    Engineer's scripts unmodified. Those two facts compose into a trap where
    performing the audit destroys the evidence the audit exists to check.
  * It has already happened. On 2026-08-01 a reviewer-probe run overwrote
    user_data/research/data/fear_greed/fng_raw.json (347,198 B / 2026-07-21 ->
    348,514 B / 2026-08-01). The file had never been committed, so no baseline
    existed, and the T-035 state is PERMANENTLY UNRECOVERABLE — restoration by
    truncation was tested and is arithmetically impossible.

A frozen script that eats evidence when re-run is not preserved history. The
guard makes this script safe to re-run, which is what "frozen reproduction
artifact" was supposed to mean.

A REFRESH IS AN A-XXX OPS TASK writing to an explicit new filename
(fng_raw_<YYYY-MM-DD>.json), never an in-place overwrite. Standard:
PROJECT_OPERATOR_MANUAL.md, "Data acquisition is not research" -> carve-out.
"""

import sys
import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

def fail(step, msg):
    print(f"\n[FAIL] Step {step}: {msg}")
    sys.exit(0)

def pass_step(step, msg):
    print(f"[PASS] Step {step}: {msg}")

def main():
    print("Starting phase_feargreed.py...")
    # Step 1: Reachability pre-gate
    url = "https://api.alternative.me/fng/?limit=0&format=json"
    out_dir = os.path.join("user_data", "research", "data", "fear_greed")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fng_raw.json")

    # READ-IF-EXISTS GUARD (A-008, 2026-08-01). If the raw artifact is already on
    # disk it IS the evidence — load it and do not touch the network. Re-fetching
    # here would overwrite the very bytes a Reviewer is auditing, which is how the
    # T-035 artifact was permanently lost. See the module docstring.
    #
    # To refresh: that is an A-XXX ops task writing to an explicit NEW filename.
    # Do not delete this file to force a re-fetch — that destroys the baseline.
    if os.path.exists(out_path):
        print(f"[GUARD] Raw artifact exists, loading from disk (no fetch): {out_path}")
        with open(out_path, "r") as f:
            fng_raw = json.load(f)
    else:
        print("Fetching F&G data...")
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            fng_raw = resp.json()
        except Exception as e:
            fail(1, f"Failed to fetch F&G API: {e}")
        with open(out_path, "w") as f:
            json.dump(fng_raw, f, indent=2)
        print(f"[GUARD] No prior artifact; fetched and saved: {out_path}")

    data = fng_raw.get("data", [])
    if not data:
        fail(1, "No data array in F&G response.")
        
    print(f"First 3 records: {data[:3]}")
    print(f"Last 3 records: {data[-3:]}")

    # Load BTC data
    btc_path = os.path.join("user_data", "data", "okx", "BTC_USDT-1d.feather")
    try:
        btc_df = pd.read_feather(btc_path)
    except Exception as e:
        fail(1, f"Failed to load BTC feather: {e}")

    btc_df['date'] = pd.to_datetime(btc_df['date']).dt.tz_localize(None).dt.normalize()
    latest_btc_date = btc_df['date'].max()
    print(f"Latest BTC date: {latest_btc_date}")
    
    # Check 90% coverage
    fng_df = pd.DataFrame(data)
    fng_df['date'] = pd.to_datetime(fng_df['timestamp'].astype(int), unit='s').dt.normalize()
    fng_df['value'] = pd.to_numeric(fng_df['value'])
    fng_df = fng_df.sort_values('date').drop_duplicates('date').set_index('date')
    
    start_date = pd.to_datetime("2018-02-01")
    cal_days = pd.date_range(start=start_date, end=latest_btc_date, freq='D')
    covered_days = fng_df.index.intersection(cal_days)
    coverage = len(covered_days) / len(cal_days)
    
    print(f"F&G coverage between {start_date.date()} and {latest_btc_date.date()}: {coverage:.2%} ({len(covered_days)}/{len(cal_days)} days)")
    
    if coverage < 0.90:
        fail(1, "F&G data covers less than 90% of calendar days.")
    pass_step(1, "Reachability pre-gate passed.")
    
    # Prepare BTC metrics
    btc_df = btc_df.sort_values('date').set_index('date')
    btc_df['rv30'] = btc_df['close'].pct_change().rolling(30).std() * np.sqrt(365)
    btc_df['roc30'] = btc_df['close'].pct_change(30)
    btc_df['sma200'] = btc_df['close'].rolling(200).mean()
    btc_df['ema20'] = btc_df['close'].ewm(span=20, adjust=False).mean()
    btc_df['ema50'] = btc_df['close'].ewm(span=50, adjust=False).mean()
    btc_df['core'] = ((btc_df['close'] > btc_df['sma200']) & 
                      (btc_df['roc30'] > 0) & 
                      (btc_df['ema20'] > btc_df['ema50'])).astype(int)
    
    # Step 2: Redundancy
    merged = btc_df[['rv30', 'roc30']].join(fng_df[['value']], how='inner').dropna()
    corr_rv30 = merged['value'].corr(merged['rv30'])
    corr_roc30 = merged['value'].corr(merged['roc30'])
    print(f"Correlation vs rv30: {corr_rv30:.4f}, vs roc30: {corr_roc30:.4f}")
    if abs(corr_rv30) >= 0.90 or abs(corr_roc30) >= 0.90:
        fail(2, "Redundancy check failed. Correlation >= 0.90")
    pass_step(2, "Redundancy pre-gate passed.")
    
    # Step 3: Lead/lag
    merged['fng_diff'] = merged['value'].diff()
    merged['fwd_5d_ret'] = btc_df['close'].shift(-5) / btc_df['close'] - 1
    merged['fwd_rv30_diff'] = btc_df['rv30'].shift(-5) - btc_df['rv30']
    
    def cross_corr(target, lags):
        corrs = {}
        for lag in lags:
            corrs[lag] = merged['fng_diff'].shift(lag).corr(merged[target])
        return corrs
        
    pos_lags = list(range(1, 11))
    neg_lags = list(range(-10, 0))
    
    cc_ret = cross_corr('fwd_5d_ret', neg_lags + pos_lags)
    cc_rv = cross_corr('fwd_rv30_diff', neg_lags + pos_lags)
    
    avg_pos_ret = np.mean([abs(cc_ret[l]) for l in pos_lags])
    avg_neg_ret = np.mean([abs(cc_ret[l]) for l in neg_lags])
    
    avg_pos_rv = np.mean([abs(cc_rv[l]) for l in pos_lags])
    avg_neg_rv = np.mean([abs(cc_rv[l]) for l in neg_lags])
    
    print(f"Target Returns: avg |pos lag| (F&G leads) = {avg_pos_ret:.4f}, avg |neg lag| (F&G lags) = {avg_neg_ret:.4f}")
    print(f"Target RV30 diff: avg |pos lag| (F&G leads) = {avg_pos_rv:.4f}, avg |neg lag| (F&G lags) = {avg_neg_rv:.4f}")
    
    if (avg_pos_ret <= avg_neg_ret) and (avg_pos_rv <= avg_neg_rv):
        fail(3, "Lead/lag pre-gate failed. Positive-lag (leading) corr is not greater than negative-lag.")
    pass_step(3, "Lead/lag pre-gate passed.")
    
    # Prepare ETH data
    eth_path = os.path.join("user_data", "data", "okx", "ETH_USDT-1d.feather")
    try:
        eth_df = pd.read_feather(eth_path)
    except Exception as e:
        fail(4, f"Failed to load ETH feather: {e}")

    eth_df['date'] = pd.to_datetime(eth_df['date']).dt.tz_localize(None).dt.normalize()
    eth_df = eth_df.sort_values('date').set_index('date')
    eth_df['roc30'] = eth_df['close'].pct_change(30)
    eth_df['sma200'] = eth_df['close'].rolling(200).mean()
    eth_df['ema20'] = eth_df['close'].ewm(span=20, adjust=False).mean()
    eth_df['ema50'] = eth_df['close'].ewm(span=50, adjust=False).mean()
    eth_df['core'] = ((eth_df['close'] > eth_df['sma200']) & 
                      (eth_df['roc30'] > 0) & 
                      (eth_df['ema20'] > eth_df['ema50'])).astype(int)

    # Step 4: Episode-count floor
    fng_series = fng_df['value']
    is_extreme_greed = fng_series >= 75
    onset_mask = is_extreme_greed & (~is_extreme_greed.shift(1).fillna(False))
    onset_days = onset_mask[onset_mask].index

    in_market_onsets = []
    for d in onset_days:
        btc_in = (d in btc_df.index) and (btc_df.loc[d, 'core'] == 1)
        eth_in = (d in eth_df.index) and (eth_df.loc[d, 'core'] == 1)
        if btc_in or eth_in:
            in_market_onsets.append(d)
            
    num_episodes = len(in_market_onsets)
    print(f"Found {num_episodes} in-market Extreme Greed onset episodes.")
    
    if num_episodes < 6:
        fail(4, f"Insufficient episodes. Count {num_episodes} < 6.")
    pass_step(4, "Episode-count floor passed.")

    # Step 5: Harm census
    onset_fwd_returns = []
    for d in in_market_onsets:
        btc_in = (d in btc_df.index) and (btc_df.loc[d, 'core'] == 1)
        eth_in = (d in eth_df.index) and (eth_df.loc[d, 'core'] == 1)
        if btc_in:
            idx = btc_df.index.get_loc(d)
            if idx + 10 < len(btc_df):
                ret = btc_df['close'].iloc[idx+10] / btc_df['close'].iloc[idx] - 1
                onset_fwd_returns.append(ret)
        if eth_in:
            idx = eth_df.index.get_loc(d)
            if idx + 10 < len(eth_df):
                ret = eth_df['close'].iloc[idx+10] / eth_df['close'].iloc[idx] - 1
                onset_fwd_returns.append(ret)
                
    all_fwd_returns = []
    btc_in_market = btc_df[btc_df['core'] == 1]
    for d in btc_in_market.index:
        idx = btc_df.index.get_loc(d)
        if idx + 10 < len(btc_df):
            ret = btc_df['close'].iloc[idx+10] / btc_df['close'].iloc[idx] - 1
            all_fwd_returns.append(ret)
            
    eth_in_market = eth_df[eth_df['core'] == 1]
    for d in eth_in_market.index:
        idx = eth_df.index.get_loc(d)
        if idx + 10 < len(eth_df):
            ret = eth_df['close'].iloc[idx+10] / eth_df['close'].iloc[idx] - 1
            all_fwd_returns.append(ret)
            
    onset_med = np.median(onset_fwd_returns)
    onset_mean = np.mean(onset_fwd_returns)
    all_med = np.median(all_fwd_returns)
    all_mean = np.mean(all_fwd_returns)
    
    print(f"Onset forward-10d (n={len(onset_fwd_returns)}): Median = {onset_med:.4f}, Mean = {onset_mean:.4f}")
    print(f"Unconditional forward-10d (n={len(all_fwd_returns)}): Median = {all_med:.4f}, Mean = {all_mean:.4f}")
    
    if (onset_med >= all_med) and (onset_mean >= all_mean):
        fail(5, "Harm census failed. Extreme-Greed-onset returns are not worse than unconditional.")
    pass_step(5, "Harm census passed.")

    # Step 6: TEST-split concentration check
    test_start = pd.to_datetime("2025-08-17")
    test_end = pd.to_datetime("2026-05-27")
    
    firing_days = []
    for d in cal_days:
        if test_start <= d <= test_end:
            if d in fng_series.index and fng_series.loc[d] >= 75:
                curr_d = d
                while curr_d in fng_series.index and fng_series.loc[curr_d] >= 75:
                    prev_d = curr_d - pd.Timedelta(days=1)
                    if prev_d not in fng_series.index or fng_series.loc[prev_d] < 75:
                        break
                    curr_d = prev_d
                onset_d = curr_d
                
                btc_in = (onset_d in btc_df.index) and (btc_df.loc[onset_d, 'core'] == 1)
                eth_in = (onset_d in eth_df.index) and (eth_df.loc[onset_d, 'core'] == 1)
                if btc_in or eth_in:
                    firing_days.append(d)

    test_total_days = len(pd.date_range(start=test_start, end=test_end, freq='D'))
    
    if not firing_days:
        fail(6, "TEST-split concentration check failed: 0 firing days in TEST split.")
        
    distinct_months = set((d.year, d.month) for d in firing_days)
    num_months = len(distinct_months)
    
    last_firing_day = max(firing_days)
    postdate_days = len(pd.date_range(start=last_firing_day + pd.Timedelta(days=1), end=test_end, freq='D'))
    postdate_pct = postdate_days / test_total_days
    
    print(f"TEST firing days: {len(firing_days)}, spanning {num_months} distinct months.")
    print(f"Last firing day: {last_firing_day.date()}, postdate days: {postdate_days} ({postdate_pct:.1%})")
    
    if num_months < 3:
        fail(6, "TEST-split concentration check failed. Firing days span < 3 distinct months.")
    if postdate_pct > 0.50:
        fail(6, "TEST-split concentration check failed. >50% of TEST-split postdate the last firing day.")
        
    pass_step(6, "TEST-split concentration check passed. All pre-gates cleared.")
    print("\nALL PRE-GATES PASSED. PROCEED TO FULL FREQTRADE BACKTEST (STEP 7).")

if __name__ == "__main__":
    main()
