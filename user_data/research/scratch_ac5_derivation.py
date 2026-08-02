# RELOCATED from the repo root 2026-08-01, and RETAINED as a worked example for
# A-003 (golden-value regression suite for validator.py) in research/OPS_BACKLOG.md.
#
# A-003 requires that "every expected value [be] derived analytically or by hand,
# INDEPENDENTLY of the implementation" - a test whose expectation is copied from a
# previous run of the same function locks in whatever the bug was. This script is
# that pattern already executed: it computes what shock_log_share SHOULD be for the
# T-020 AC5 fixture by replicating the arithmetic by hand, WITHOUT calling
# compute_shock_share. Read it before writing that suite; a worked example is
# easier to copy correctly than a description of one.
#
"""
Hand derivation for AC5 (T-020) shock fixture.
This script computes exactly what shock_log_share should be for the AC5 fixture
WITHOUT calling compute_shock_share - it replicates the ARITHMETIC by hand.

Run: py -3.13 scratch_ac5_derivation.py
"""
import sys
sys.path.insert(0, 'user_data/research')
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade')

import numpy as np
import pandas as pd
from validator import shock_day_mask

WINDOW_START = pd.Timestamp("2026-07-08", tz="UTC")
n_days = 120
dates = pd.date_range("2026-07-08", periods=n_days, freq='D', tz='UTC')

# ===== BASE RETURNS (fixed seed) =====
np.random.seed(7)
btc_base = np.random.normal(0.0, 0.008, n_days)  # std ≈ 0.008

# ===== INJECTED SHOCK DAYS (hand-chosen) =====
# Day index 40 = 2026-08-17, day index 80 = 2026-09-26
# Return: +0.20 (20%) -- clearly > 3 * 0.008 = 0.024 threshold
SHOCK_IDX_A = 40
SHOCK_IDX_B = 80
SHOCK_RETURN_A = 0.20  # +20%
SHOCK_RETURN_B = -0.20  # -20%

btc_rets = btc_base.copy()
btc_rets[SHOCK_IDX_A] = SHOCK_RETURN_A
btc_rets[SHOCK_IDX_B] = SHOCK_RETURN_B

btc_series = pd.Series(btc_rets, index=dates)

print(f"Injected shock day A: index={SHOCK_IDX_A}, date={dates[SHOCK_IDX_A].date()}, return={SHOCK_RETURN_A}")
print(f"Injected shock day B: index={SHOCK_IDX_B}, date={dates[SHOCK_IDX_B].date()}, return={SHOCK_RETURN_B}")

# ===== CONFIRM WHICH DAYS FIRE AS SHOCKS (using the REAL shock_day_mask) =====
# Use ETH same as BTC for simplicity in this fixture
underlying_rets = pd.DataFrame({'BTC': btc_series, 'ETH': btc_series})

mask = shock_day_mask(underlying_rets, method="3sigma", sigma_mult=3.0, vol_lookback=30)

print(f"\nTotal shock days fired: {mask.sum()}")
print(f"Shock day dates: {dates[mask.values].strftime('%Y-%m-%d').tolist()}")

# Verify the injected days are in the shock set
assert mask.iloc[SHOCK_IDX_A], f"Day {SHOCK_IDX_A} should be a shock but is not"
assert mask.iloc[SHOCK_IDX_B], f"Day {SHOCK_IDX_B} should be a shock but is not"
n_shock = int(mask.sum())
print(f"\nVerified: both injected days are in the shock set. n_shock_days={n_shock}")

# ===== IN-MARKET DAYS =====
# Set the last 30 days as in-market (strategy return = 0.005 per day on those days)
# This gives 30 in-market days, well above the 20-day threshold
INMARKET_RETURN = 0.005  # small positive return
in_market_mask = np.zeros(n_days, dtype=bool)
in_market_mask[-30:] = True  # days 90-119

# Build strategy daily return series
# On in-market days, return = INMARKET_RETURN; flat otherwise
strat_rets = np.where(in_market_mask, INMARKET_RETURN, 0.0)
strat_series = pd.Series(strat_rets, index=dates)

print(f"\nIn-market days: {in_market_mask.sum()} (need >=20 ✓)")

# ===== HAND DERIVATION OF shock_log_share =====
# Formula: shock_log_share = sum(log1p(strat[shock_days])) / sum(log1p(strat[all_in_mkt]))
# 
# STEP 1: log returns of the strategy for every day in underlying_rets.index
#         aligned to underlying_rets (drops day 0 since pct_change loses it)
# Note: compute_shock_share does:
#   underlying_rets = closes.pct_change().dropna()
#   window_ret = underlying_rets[>= WINDOW_START]
# But we're feeding pct_change of prices INTO compute_shock_share -- let's
# build a matching price series so pct_change gives back our intended returns.
# Actually: price[0]=100, price[t] = price[t-1] * (1 + return[t])
btc_prices = (1 + btc_series).cumprod() * 100

# The prices -> pct_change in compute_shock_share gives back (approx) btc_rets
# BUT the returned underlying_rets will have the same index shifted by 1 (dropna)
underlying_from_prices = btc_prices.pct_change().dropna()
print(f"\nunderlying_from_prices start: {underlying_from_prices.index[0].date()}")
print(f"underlying_from_prices end: {underlying_from_prices.index[-1].date()}")
print(f"Length: {len(underlying_from_prices)}")

# The mask is applied over this index
# shock_day_mask will use underlying_from_prices as input -> same index (119 days not 120)
underlying_from_prices_df = pd.DataFrame({'BTC': underlying_from_prices, 'ETH': underlying_from_prices})
mask_from_prices = shock_day_mask(underlying_from_prices_df, method="3sigma", sigma_mult=3.0, vol_lookback=30)

print(f"\nShock mask from prices: n_shock={mask_from_prices.sum()}")

# Now align strat returns to this index
strat_aligned = strat_series.reindex(underlying_from_prices.index).fillna(0.0)
log_ret = np.log1p(strat_aligned)

total_log = log_ret.sum()
shock_mask_aligned = mask_from_prices.reindex(log_ret.index).fillna(False)
shock_log = log_ret[shock_mask_aligned].sum()

print(f"\n=== HAND DERIVATION (arithmetic) ===")
print(f"In-market days (strat_ret != 0): {(strat_aligned != 0).sum()}")
print(f"Total log-PnL: {total_log:.8f}")
print(f"  = sum of log1p({INMARKET_RETURN}) * 30 days (approx)")
print(f"  = {np.log1p(INMARKET_RETURN):.8f} * 30 = {np.log1p(INMARKET_RETURN)*30:.8f}")

# Which shock days overlap with in-market days?
shock_inmarket_days = strat_aligned[shock_mask_aligned]
print(f"\nShock days in in-market window: {shock_mask_aligned[strat_aligned != 0].sum()}")
print(f"  strat_ret on shock days: {shock_inmarket_days[shock_inmarket_days != 0].values}")
shock_log_from_inmarket = log_ret[shock_mask_aligned & (strat_aligned != 0)].sum()
shock_log_from_flat = log_ret[shock_mask_aligned & (strat_aligned == 0)].sum()
print(f"  shock_log from in-market days: {shock_log_from_inmarket:.8f}")
print(f"  shock_log from flat days: {shock_log_from_flat:.8f}")
print(f"  total shock_log: {shock_log:.8f}")

if abs(total_log) > 1e-12:
    shock_share_pct = float(shock_log / total_log) * 100.0
    print(f"\nshock_log_share = {shock_log:.8f} / {total_log:.8f} = {shock_share_pct:.6f}%")
else:
    shock_share_pct = float('nan')
    print("ZERO total log-PnL -- cannot compute share")

print(f"\nSHOCK DAYS IN MASK:")
for i, (dt, in_mkt) in enumerate(zip(underlying_from_prices.index, strat_aligned)):
    if mask_from_prices.iloc[i] if i < len(mask_from_prices) else False:
        print(f"  {dt.date()}: strat_ret={strat_aligned.iloc[i]:.4f}, log1p={np.log1p(strat_aligned.iloc[i]):.8f}, in_market={in_mkt != 0}")

print(f"\n=== RESULT FOR AC5 FIXTURE ===")
print(f"n_shock_days expected = {int(mask_from_prices.sum())}")
print(f"shock_log_share expected = {shock_share_pct:.4f}%")
print(f"Tolerance: +-0.05pp -> [{shock_share_pct-0.05:.4f}%, {shock_share_pct+0.05:.4f}%]")
