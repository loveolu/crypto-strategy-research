# CRYPTO-EXP-029 design — extreme-fear relief across the 2021–22 bear regime

Date frozen: 2026-09-04 PDT. Parent observation: CRYPTO-EXP-027. This is an
exact-rule BTC spot transfer audit, not a parameter variation.

## Hypothesis

EXP-027's prior-day Extreme Fear relief signal had strong TRAIN economics but only
38 trades because 2023–24 contained eight qualifying sentiment days. If the effect
reflects capitulation rather than that isolated episode, the identical rule should
also exist during the independent 2021–22 fear regime on BTC spot.

## Frozen rule and data

- OKX BTC/USDT spot, canonical 4h candles. Use the most recent five years available:
  2021-05-25 through 2026-05-24.
- Exact EXP-027 signal: Fear & Greed shifted one full UTC day, value ≤25, completed
  24h return <0, green 4h candle, first qualifying signal per UTC day.
- Enter next 4h open and exit three bars later. One unleveraged BTC position at a
  time, full notional. Charge a conservative 11 bps per side (10 bps regular spot
  taker fee plus 1 bp spread/slippage); expected round trip 22 bps.
- No fear threshold, candle, holding, stop, direction, or date optimization.

## Evidence boundaries and gates

Discovery/TRAIN is 2021-05-25 through 2023-01-21, ending before EXP-027's perpetual
history. Require at least 60 trades, gross expectancy above 22 bps, and a 999-draw
circular daily-sentiment placebo p≤.025 (seed 29029, minimum 30-day displacement).

Only if all discovery gates pass, inspect 2023-01-22 through 2026-05-24 as a
**retrospective transfer audit**. This period overlaps market history already seen
in EXP-027 and is not untouched OOS. Report 2x cost, one-bar delay, top-5% removal,
calendar years and two chronological subsegments. Even a pass remains Experimental
until new forward data supplies independent evidence.
