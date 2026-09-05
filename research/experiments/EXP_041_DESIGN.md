# CRYPTO-EXP-041 — Futures-to-mark tail dislocation reversion

## Audit correction and hypothesis

The legacy basis record measured the distribution of `(futures close − mark close) / mark close`
and its funding correlation, then called the axis noise. It did not test causal forward returns.
Feature amplitude being below cost is not an economic kill gate because a small dislocation may
forecast a larger liquidation/reversion move.

Hypothesis: an extreme positive hourly futures premium to OKX mark reflects aggressive leveraged
buying and predicts a four-hour reversal; an extreme negative premium reflects forced selling and
predicts a rebound.

## Frozen construction

- Data gate: TRAIN alignment is 100% for ETH, SOL, BNB, XRP, ADA, AVAX, DOT, and LINK. BTC is excluded
  before return inspection because only 3,200/16,104 TRAIN hours (19.9%) align and contain 31 gaps.
- At each completed 1h bar, premium is `futures_close / mark_close − 1`.
- Thresholds are the 1st and 99th percentiles of the **previous** 720 aligned premiums:
  `rolling(720, min_periods=720).quantile(...).shift(1)`.
- Premium ≤ prior p1 signals long; premium ≥ prior p99 signals short. Enter at the next futures open,
  hold four hours, and exit at that later open. Ignore signals while a position is active and exclude
  unfinished final trades.
- Eight equal 1/8 sleeves, no leverage. Use measured instrument-specific expected taker friction on
  entry and exit. No funding, BTC, trend, volume, volatility, coin, stop, target, or regime filter.
  No threshold/window/hold search.

## TRAIN gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Keep held-out sealed unless there are at least 300
completed trades and 30 per coin; combined gross expectancy exceeds expected round-trip cost; at
least six of eight coins are net-positive; long and short gross expectancy are independently
positive; and pooled gross expectancy beats at least 97.5% of 999 shared circular-shift placebos
(seed 41041, minimum shift 30 days). Shift the complete direction streams with one shared offset.

## Held-out and robustness gates

If TRAIN passes, inspect 2024-11-23 through 2026-09-01 once. Require positive expected-cost return,
Sharpe and PF; six positive coins; both directions net-positive; two positive VAL/TEST/FWD segments;
and positive outcomes at 2× costs, one-bar delay, and after removing the top 5% of trades. The Claude
superiority hurdle remains >+61.7% return with drawdown no worse than −5.5% in one evidence stream.

Failure does not authorize one-sided selection, alternative quantiles/windows/holds, coin selection,
or adding funding/trend filters after inspecting TRAIN.
