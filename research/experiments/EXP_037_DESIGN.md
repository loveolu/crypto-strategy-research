# CRYPTO-EXP-037 — Volatility-scaled next-bar dynamic breakout

## Hypothesis and frozen construction

Crypto volatility clusters. A stop entry placed far enough beyond the latest completed 4h close,
scaled by recent realized volatility, may isolate genuine expansion rather than ordinary noise and
produce six-bar continuation large enough to clear perpetual-futures friction.

- Universe: the same nine liquid OKX perpetuals and chronological partitions used by EXP-023–036.
- At each completed 4h bar, calculate the sample standard deviation of the prior 12 log returns,
  including that completed bar and no later value (`rolling(12, min_periods=12).std(ddof=1)`).
- Freeze multiplier 1.5. The next bar's long stop is `close * exp(1.5*sigma)` and short stop is
  `close * exp(-1.5*sigma)`. These are stop-market triggers, not assumed limit fills.
- Only the immediately following 4h bar can trigger. If its high reaches only the upper stop, enter
  long; if its low reaches only the lower stop, enter short. If both stops are touched, skip the
  ambiguous bar because OHLCV cannot identify which trigger occurred first.
- A gap beyond a stop fills adversely at the next bar open; otherwise fill at the stop. Hold for six
  complete bars and exit at the following open. Signals occurring while a trade is active are
  ignored. Any trade without its scheduled exit is excluded.
- One position per coin, equal 1/9 sleeves, no leverage. Apply measured instrument-specific taker
  friction at entry and exit. No trend, BTC, volume, funding, coin, direction, stop, target, or
  regime filter and no parameter search.

## TRAIN gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Keep held-out sealed unless there are at least 300
completed trades and 20 per coin; gross expectancy exceeds expected round-trip cost; at least six
coins are net-positive; long and short gross expectancy are independently positive; and the pooled
gross mean beats at least 97.5% of 999 shared circular-shift placebos (seed 37037, minimum shift 30
days). Placebos shift the complete dimensionless upper/lower distances together within coin, then
re-anchor those distances to the contemporaneous close; this avoids nonsensical absolute-price
levels while preserving the frozen volatility-width sequence.

## Held-out and robustness gates

If TRAIN passes, inspect 2024-11-23 through 2026-09-01 once. Require positive expected-cost return,
Sharpe and PF; six positive coins; both directions net-positive; two positive VAL/TEST/FWD segments;
and positive results at 2× costs, one-bar delayed entry eligibility, and after removing the top 5%
of trades. Only then test the unchanged construction on Kraken. Superiority requires >+61.7% return
with drawdown no worse than −5.5%, with fixed and walk-forward evidence kept separate.

Failure does not authorize changing the 12-bar window, 1.5 multiplier, six-bar hold, direction,
ambiguity policy, filters, or coin set after inspecting TRAIN.

## Result

TRAIN produced **3,319 trades** and passed the sample, per-coin, aggregate economics, and breadth
gates. Gross expectancy was +18.80 bps/trade against 13.70 bps expected round-trip cost; net return
was +12.95% (6.85% annualized), Sharpe 0.38, Sortino 0.30, PF 1.04, and maximum drawdown **−45.48%**.
Six of nine coins were net-positive. Turnover was 737.56× and the median trade was −25.24 bps.

The frozen direction gate failed. Longs earned +49.03 gross / +35.30 net bps across 1,532 trades,
while shorts lost **−7.12 gross / −20.83 net bps** across 1,787 trades. Because every cheap gate had
to pass before the expensive placebo, the placebo was not run.

**Verdict: REJECTED_TRAIN_GATE (short gross expectancy).** Held-out stayed sealed. The favorable
long split does not authorize a post-hoc long-only test or parameter/filter search.
