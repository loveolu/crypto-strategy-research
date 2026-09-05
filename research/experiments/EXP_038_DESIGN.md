# CRYPTO-EXP-038 — Awesome Oscillator saucer continuation

## Hypothesis and frozen construction

When Bill Williams' Awesome Oscillator remains on one side of zero, briefly turns against the
prevailing impulse, then resumes, the pullback may be shallow enough for the resumed 24h move to
clear realistic perpetual-futures friction.

- Universe: the same nine liquid OKX perpetuals and chronological partitions used by EXP-023–037.
- Timeframe: 4h. Compute midpoint `(high + low) / 2`; Awesome Oscillator (AO) is its causal 5-bar
  simple moving average minus its causal 34-bar simple moving average.
- Bullish saucer at completed bar *t*: AO[t], AO[t−1], and AO[t−2] are all strictly above zero,
  AO[t−1] < AO[t−2], and AO[t] > AO[t−1]. Bearish mirror: all three are below zero,
  AO[t−1] > AO[t−2], and AO[t] < AO[t−1]. No zero-cross entry is substituted.
- Enter at the next 4h open, hold six bars (24h), and exit at that later open. Ignore signals while
  a trade is active; exclude any unfinished final trade. Equal 1/9 sleeves, no leverage, measured
  instrument-specific taker friction on entry and exit.
- No trend, volatility, BTC, volume, funding, coin, stop, target, threshold, or regime filter. No
  parameter search and no Twin-Peaks/divergence variant in this experiment.

## TRAIN gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Keep held-out sealed unless there are at least 300
completed trades and 20 per coin; gross expectancy exceeds expected round-trip cost; at least six
coins are net-positive; long and short gross expectancy are independently positive; and the pooled
gross mean beats at least 97.5% of 999 shared circular-shift placebos (seed 38038, minimum shift 30
days). Placebos shift the complete direction stream within each coin using one shared offset.

## Held-out and robustness gates

If TRAIN passes, inspect 2024-11-23 through 2026-09-01 once. Require positive expected-cost return,
Sharpe and PF; six positive coins; both directions net-positive; two positive VAL/TEST/FWD segments;
and positive outcomes at 2× costs, one-bar delayed execution, and after removing the top 5% of
trades. Only then test the unchanged rule on Kraken. The Claude superiority hurdle remains >+61.7%
return with drawdown no worse than −5.5% under one consistent evidence stream.

Failure does not authorize selecting one direction, changing the 5/34 averages, hold, saucer
inequalities, filters, or coin set, or switching to Twin Peaks after inspecting TRAIN.

## Result

All cheap TRAIN gates passed. The rule produced **1,796 trades**, +33.23 gross and +19.53 net
bps/trade, **+43.19% net return** (21.58% annualized), Sharpe 1.16, Sortino 0.74, PF 1.16, and
−13.18% maximum drawdown. Eight of nine coins were net-positive. Longs earned +44.23 gross / +30.67
net bps across 924 trades; shorts earned +21.56 gross / +7.72 net bps across 872 trades.

The mandatory 999-draw shared circular-shift placebo narrowly failed: observed gross expectancy was
33.23 bps versus a 5.44 bps placebo mean, but one-sided **p=0.029** exceeded the frozen ≤0.025 gate.

**Verdict: REJECTED_TRAIN_GATE (placebo).** Held-out stayed sealed. The near miss does not authorize
a new random seed, relaxed significance threshold, direction/coin selection, or parameter search.
