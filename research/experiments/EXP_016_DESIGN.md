# CRYPTO-EXP-016 design — BTC reversal leads lagging alts

Date pre-registered: 2026-09-04 PDT. Parent: none (independent mechanism).

## Hypothesis

After an unusually negative BTC 4h bar, BTC's first positive 4h close marks partial
market stabilization. An altcoin that is still non-positive during that rebound is
temporarily lagging the market and should catch up over the next completed 4h bar.
The expected edge is delayed cross-asset information diffusion, not the cascade
strategy's own-volatility percentile or daily trend gate.

## Frozen primary rule

- Data: existing OKX 1h perpetual OHLCV resampled to UTC-aligned 4h bars; BTC plus
  ETH, SOL, BNB, XRP, ADA, AVAX, DOT and LINK.
- TRAIN: 2023-01-22 through 2024-11-22 23:00 UTC. VAL, TEST and FWD retain the
  existing project boundaries and remain unopened unless the TRAIN pre-gate passes.
- Shock threshold: the 10th percentile of BTC 4h close-to-close return on TRAIN,
  calculated once. This is the experiment's only data-derived parameter.
- Signal at completed bar `t`: BTC return at `t-1` is at or below the threshold;
  BTC return at `t` is positive; alt return at `t` is at or below zero.
- Execution: long the alt at `open[t+1]`; exit at `open[t+2]`. Signals while the
  position is occupied are ignored. No leverage, stop, target, or regime filter.
- Expected cost: measured instrument-specific taker all-in cost on entry and exit.
  Gross/zero-cost is the pre-gate; expected, 2x and 3x costs are reported only after
  it passes.

## TRAIN-only pre-gate and multiplicity

This is one primary construct and one trial. It advances only if all conditions hold:

1. At least 100 pooled TRAIN trades and at least 10 trades for every alt.
2. Positive pooled mean gross return and positive mean gross return in at least 5/8
   alts.
3. A two-sided, event-block circular-shift placebo p-value below 0.05 using 999
   deterministic shifts. BTC signal dates are preserved and each alt return stream
   is shifted, which breaks predictive timing without inventing observations.
4. Gross expectancy is at least the pooled measured round-trip expected cost. This
   is an economic-size screen, not an after-cost backtest.

Failure stops the experiment without viewing VAL/TEST/FWD. A pass opens the held-out
segments exactly once, followed by cost, one/two-bar delay, top-5%-trade removal,
coin breadth, calendar/regime and recent-window diagnostics. No alternative shock
quantile, return cutoff, holding period or direction will be tried in this experiment.

Before opening held-out data, the advancement rule is frozen as: expected-cost net
return, Sharpe and profit factor must all be positive/above 0.5/above 1.0 across all
OOS; at least two of VAL, TEST and FWD must have positive expected-cost return; at
least 5/8 alts must have positive OOS expectancy; and all-OOS return must remain
positive at 2x cost, with a one-bar entry delay at expected cost, and after removing
the top 5% of trades. The 3x-cost and two-bar-delay cases are reported as stress
diagnostics but are not promotion gates. Passing means `Promising`, not `Candidate`.

## Falsification and interpretation

Reject if any pre-gate fails. A negative result closes this exact BTC-shock/rebound
catch-up rule, not all BTC-to-alt lead/lag mechanisms. Any reverse-direction result is
diagnostic only and cannot be promoted without a new preregistered experiment.
