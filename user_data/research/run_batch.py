"""Run the strategy battery through the validator and print verdicts."""
import sys
import time
sys.path.insert(0, 'C:/Users/Comec/Projects/freqtrade/user_data/research')
from validator import load, validate, print_verdict, save_verdict
import strategies as S

df_btc1d = load('BTC/USDT', '1d')
df_btc1h = load('BTC/USDT', '1h')
df_eth1d = load('ETH/USDT', '1d')

BARS_PER_YEAR_1H = 24 * 365

TESTS = [
    # (name, df, signal_fn, bars_per_year)
    ("donchian_20_10_btc1d", df_btc1d, lambda d: S.donchian_breakout_vec(d, 20, 10), 365),
    ("donchian_55_20_btc1d", df_btc1d, lambda d: S.donchian_breakout_vec(d, 55, 20), 365),
    ("ma_cross_50_200_btc1d", df_btc1d, lambda d: S.ma_cross(d, 50, 200), 365),
    ("ma_cross_20_50_btc1d", df_btc1d, lambda d: S.ma_cross(d, 20, 50), 365),
    ("rsi2_revert_btc1d", df_btc1d, lambda d: S.rsi_mean_reversion(d, 2, 10, 50), 365),
    ("rsi2_revert_btc1h", df_btc1h, lambda d: S.rsi_mean_reversion(d, 2, 10, 50), BARS_PER_YEAR_1H),
    ("macd_trend_btc1d", df_btc1d, S.macd_trend, 365),
    ("bollinger_revert_btc1d", df_btc1d, S.bollinger_revert, 365),
    ("adx_trend_btc1d", df_btc1d, S.adx_trend, 365),
    ("adx_trend_btc1h", df_btc1h, S.adx_trend, BARS_PER_YEAR_1H),
    ("roc30_btc1d", df_btc1d, lambda d: S.roc_momentum(d, 30, 5), 365),
    ("channel_atr_btc1d", df_btc1d, lambda d: S.channel_breakout_atr(d, 50, 2.0), 365),
    ("vol_target_btc1d", df_btc1d, lambda d: S.vol_target_btc(d, 0.40), 365),
    ("regime_trend_btc1d", df_btc1d, S.regime_trend, 365),
    ("stoch_rsi_btc1d", df_btc1d, S.stoch_rsi_revert, 365),
    ("keltner_btc1d", df_btc1d, S.keltner_breakout, 365),
    ("triple_screen_btc1d", df_btc1d, S.triple_screen, 365),
    ("triple_screen_btc1h", df_btc1h, S.triple_screen, BARS_PER_YEAR_1H),
]

passed = []
for name, df, fn, bpy in TESTS:
    t0 = time.time()
    try:
        v = validate(name, df, fn, bars_per_year=bpy)
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
        continue
    elapsed = time.time() - t0
    save_verdict(v)
    print_verdict(v)
    print(f"  (took {elapsed:.1f}s)")
    if v.passed:
        passed.append(name)

print("\n" + "="*70)
print(f"BATTERY COMPLETE: {len(passed)}/{len(TESTS)} passed")
print("="*70)
for p in passed:
    print(f"  PASS: {p}")
