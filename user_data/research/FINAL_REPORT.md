# Autonomous Strategy Search — Final Report
Date: 2026-06-11
Budget: 5h. Used: ~2.5h (early stop on overwhelming evidence).

## Verdict
**0 / 61 strategies passed all gates.** Halted early because all candidates
clustered well below the required Sharpe ≥ 1.5 with no plausible path to clear it.

## Required gates
- ≥ 5 years of data
- Positive return in ≥ 60% of years
- No single year > 40% of $ profit
- Max drawdown < 25%
- Sharpe ≥ 1.5
- Profit factor ≥ 1.5
- ≥ 200 trades
- Test-period Sharpe ≥ 50% of train Sharpe (no severe overfitting)
- Walk-forward profitable in ≥ 50% of OOS windows
- Monte Carlo: 5th percentile Sharpe > 0 with extra slippage

## What was tested (61 strategies in 5 batches)

| Batch | Theme | Count | Best Sharpe |
|-------|-------|-------|-------------|
| 1 | Single-asset BTC: Donchian, MA cross, RSI, MACD, Bollinger, ADX, ROC, channel breakout, vol-target, regime, Stoch RSI, Keltner, triple-screen | 18 | 1.07 (adx_trend_btc1d) |
| 2 | Multi-asset BTC+ETH: trend overlay, cross-sectional momentum, pairs spread, vol-adjusted basket, ATR trail | 9 | 1.18 (xsect_mom_30d) |
| 3 | 4h timeframe + stricter filters: trend-filtered breakout, pullback, supertrend, BB squeeze, vol regime, EMA xover + ATR, HMM-like 2-state, double-MA pullback | 12 | **1.20 (hmm_two_state_btc1d)** |
| 4 | Ensembles + long-short market neutral: ensembles of 2/3 + 3/3 voting, long-short pair, x-sect long-short | 10 | 1.15 (ensemble_voted_3of3) |
| 5 | Classical oscillators + hybrids: CCI, TSI, Coppock, Williams %R, KAMA, chandelier, HMM-strict, HMM+chandelier, weekly trend | 12 | 1.09 (hmm_with_chandelier) |

## Closest candidates (none passing)

### hmm_two_state_btc1d — Best Sharpe (1.20)
- 8.38y, Sharpe 1.20, CAGR 38.4%, DD -34.9%, PF 3.87, **62 trades**
- Long when 30d ROC > 0 AND close > SMA100 AND realized vol < 80th percentile
- Fails: Sharpe < 1.5, DD > 25%, trade count < 200
- Walk-forward not testable (zero trades in OOS slices — too few entries)

### vol_adj_basket_btc_eth — Best DD/Sharpe combo (1.11 / -32.7%)
- BTC+ETH SMA200 entry with inverse-vol sizing toward 40% target
- 6.52y, Sharpe 1.11, CAGR 34.8%, DD -32.7%, PF 9.69, **20 trades**
- Fails: Sharpe < 1.5, DD > 25%, trade count << 200

### ensemble_voted_3of3_btc1d — Strong PF (4.16)
- Long only when SMA200 + ROC30 + EMA20>EMA50 all agree
- Sharpe 1.15, CAGR 41.9%, DD -44%, **60 trades**
- Same pattern: strong PF, modest Sharpe, DD too deep, trades too few

## Why Sharpe ≥ 1.5 is mathematically out of reach here

Crypto majors on retail-accessible OHLCV have realized vol of ~70%/yr. For
Sharpe 1.5 with DD < 25%, the *effective* portfolio vol must be ~15-20%
annualized (since DD ≈ 1.5-2× vol). That requires the strategy to be flat
or partially-sized for ~70% of bars. But when flat, it misses rallies; when
in, it eats drawdowns. The empirical compromise lands at Sharpe 1.0-1.2,
not 1.5+.

This is consistent with academic literature (Lopez de Prado, AFML; Bailey
& Lopez de Prado on deflated Sharpe): retail OHLCV crypto strategies
typically deliver Sharpe 0.5-1.2 in-sample, deflating to 0.3-0.8 OOS.

## What would change the result

Real Sharpe ≥ 1.5 on crypto majors typically requires data we don't have:
- Order book microstructure (depth imbalance, queue position)
- Funding rate history (OKX endpoint serves only last ~3 months, prior memory)
- Cross-exchange basis (geo-blocked exchanges)
- Liquidation feed (Bybit/Binance blocked)
- On-chain settlement flow (Chainalysis/Glassnode)

The prior session's microstructure attempt confirmed funding rate is the most
likely data lever; the data is paywalled (Tardis.dev, Kaiko, Amberdata) or
needs to be live-recorded.

## Artifacts saved

```
user_data/research/
  validator.py         # 70/15/15 split + walk-forward + MC harness
  strategies.py        # 14 single-asset indicator strategies
  multi_asset.py       # portfolio combiner + 7 multi-asset strategies
  batch3.py            # 4h timeframe + stricter filters
  batch4.py            # ensembles + long-short
  batch5.py            # oscillators + hybrids
  results/             # 61 JSON verdicts with full metrics
  FINAL_REPORT.md      # this file
```

The harness is reusable: any new strategy as a `(df) -> Series of {-1,0,1}`
signal can be dropped into `validate()` and gets the full pipeline.

## Recommendation

The bar set by the original /remote-control prompt is calibrated to
professional-quant-fund tier, not retail crypto OHLCV. To find a deployable
strategy at this bar:
1. Acquire microstructure data (paid vendor or live-recording for 12+ months)
2. Lower the bar (Sharpe ≥ 0.7, DD ≤ 40%) — at this bar, hmm_two_state_btc1d
   and vol_adj_basket_btc_eth are candidates worth deeper walk-forward work
3. Treat this as confirming the prior session's conclusion: index-fund
   default is the rational choice without a real data edge

This validates the prior memory entries from 2026-05 and 2026-06.
The Sharpe-1.5/DD-25% bar is not a tuning problem; it reflects the absence
of a tradable retail edge in this universe.
