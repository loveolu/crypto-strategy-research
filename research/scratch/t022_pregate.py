import pandas as pd
import numpy as np

# Load OKX data
btc_df = pd.read_feather("user_data/data/okx/BTC_USDT-1d.feather")
btc_df['date'] = pd.to_datetime(btc_df['date'])
btc_df.set_index('date', inplace=True)

# Calculate champion's core signal
c = btc_df['close']
btc_df['sma200'] = c.rolling(200).mean()
btc_df['roc30'] = c.pct_change(30)
btc_df['ema20'] = c.ewm(span=20, adjust=False).mean()
btc_df['ema50'] = c.ewm(span=50, adjust=False).mean()

btc_df['core'] = (
    (c > btc_df['sma200']) & 
    (btc_df['roc30'] > 0) & 
    (btc_df['ema20'] > btc_df['ema50'])
).astype(int)

# Realized volatility
btc_df['rv30'] = c.pct_change().rolling(30).std() * np.sqrt(365)

# Load DVOL
dvol_df = pd.read_feather("user_data/research/data/dvol/btc_dvol_daily.feather")
dvol_df['date'] = pd.to_datetime(dvol_df['date'])
# If the time is 08:00 or something, normalize to midnight if needed, but OKX daily might be midnight UTC.
dvol_df.set_index('date', inplace=True)
if not dvol_df.index.tz:
    dvol_df.index = dvol_df.index.tz_localize('UTC')

# Merge
df = btc_df.join(dvol_df[['dvol']], how='left')

# Drop NA where DVOL is missing
df = df.dropna(subset=['dvol'])

# Calculate DVOL change
df['dvol_chg_5d'] = df['dvol'].pct_change(5)
df['rv30_chg_5d'] = df['rv30'].pct_change(5)

df['fwd_ret_10d'] = df['close'].shift(-10) / df['close'] - 1

test_start = pd.to_datetime('2025-08-17', utc=True)
test_end = pd.to_datetime('2026-05-27', utc=True)
df['is_test'] = (df.index >= test_start) & (df.index <= test_end)

# Try different thresholds for DVOL acceleration (e.g. 10%, 15%, 20%, 25%, 30%)
thresholds = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

for th in thresholds:
    print(f"\\n=== Testing Threshold: {th:.0%} ===")
    
    # Identify signal
    # DVOL accelerates rapidly
    df['signal'] = (df['dvol_chg_5d'] > th).astype(int)
    
    # Pre-Gate 1: Episode/Materiality Census
    # Must fire >= 6 times while in-market
    
    # Group into episodes (continuous blocks of signal==1). We can just count connected components
    in_market = df[df['core'] == 1].copy()
    
    if in_market.empty:
        print("No in-market days.")
        continue
        
    in_market['signal_change'] = in_market['signal'].diff()
    # Number of episodes is the number of times signal goes from 0 to 1 (or starts at 1)
    # Actually, if signal is 1 and previous day is 0, that's an episode start.
    in_market['episode_start'] = ((in_market['signal'] == 1) & (in_market['signal'].shift(1) != 1)).astype(int)
    
    if in_market.iloc[0]['signal'] == 1:
        in_market.iloc[0, in_market.columns.get_loc('episode_start')] = 1
        
    episodes = in_market['episode_start'].sum()
    
    # Fires in TEST split?
    test_market = in_market[in_market['is_test'] == True]
    test_episodes = test_market['episode_start'].sum()
    
    print(f"Pre-Gate 1:")
    print(f"  Episodes while in-market: {episodes} (Required: >= 6)")
    print(f"  Episodes in TEST split: {test_episodes} (Required: >= 1)")
    
    # Pre-Gate 2: Harm Census
    # Affected days must be demonstrably adverse (forward returns worse than unconditional).
    
    unconditional_fwd_ret = in_market['fwd_ret_10d'].dropna()
    affected_fwd_ret = in_market[in_market['signal'] == 1]['fwd_ret_10d'].dropna()
    
    if affected_fwd_ret.empty:
        print(f"  No affected days to calculate harm.")
    else:
        uncond_median = unconditional_fwd_ret.median()
        uncond_mean = unconditional_fwd_ret.mean()
        
        aff_median = affected_fwd_ret.median()
        aff_mean = affected_fwd_ret.mean()
        
        print(f"Pre-Gate 2:")
        print(f"  Affected Days: {len(affected_fwd_ret)}")
        print(f"  Unconditional 10d Fwd Ret: Median = {uncond_median:.2%}, Mean = {uncond_mean:.2%}")
        print(f"  Affected 10d Fwd Ret:     Median = {aff_median:.2%}, Mean = {aff_mean:.2%}")
        
        if aff_median > uncond_median or aff_mean > uncond_mean:
            print("  FAIL: Affected days are BETTER or equal to unconditional. No harm to avoid.")
        else:
            print("  PASS: Affected days are WORSE than unconditional.")
