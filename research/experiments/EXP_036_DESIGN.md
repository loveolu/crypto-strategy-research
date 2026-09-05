# CRYPTO-EXP-036 — Standard TRIX trend-direction system

Date frozen: 2026-09-04 PDT. Independent parent: none. The project census records MACD/TSI and
several ROC/momentum constructs, but no TRIX implementation. This tests the complete standard rule
in `knowledge_base/13_indicator_reference.md`, not another MACD cycle.

## Hypothesis

Triple exponential smoothing suppresses enough 4h crypto noise that two consecutive changes in the
same direction identify persistent trends. Longer reversal-to-reversal holds should allow the edge
to clear realistic round-trip friction where one-to-six-bar candle patterns could not.

## Frozen rule

- Nine liquid OKX USDT perpetuals; 4h bars mechanically resampled from canonical 1h data.
- Compute `log(close)`, then three causal EMAs with `span=6`, `adjust=False`, and `min_periods=6` at
  every stage. TRIX direction is the one-bar difference of the third EMA.
- Desired long state requires TRIX direction >0 on both the current and prior completed bars.
  Desired short state requires <0 on both. Zero/undefined leaves the prior position unchanged.
- On a state change, execute at the next 4h open. Reverse at the same next open when the opposite
  state appears. Unfinished final positions are excluded rather than assigned an invented terminal
  fill. One position per coin, equal 1/9 sleeves, measured instrument-specific taker friction on
  each entry and exit. No leverage.
- Report long and short separately. No deadband, signal line, trend/volatility/BTC/volume filter,
  stop, target, coin selection, or alternative EMA span/confirmation count.

## TRAIN gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Keep held-out sealed unless there are at least 100
completed trades and 8 per coin; combined gross expectancy exceeds expected round-trip cost; at
least six coins are net-positive; long and short gross expectancy are independently positive; and
the combined gross mean beats at least 97.5% of 999 shared circular-shift placebos (seed 36036,
minimum shift 30 days). The placebo shifts desired-state streams while preserving cross-coin time.

## Held-out and robustness gates

If TRAIN passes, inspect 2024-11-23 through 2026-09-01 once. Require positive expected-cost return,
Sharpe and PF; six positive coins; both directions net-positive; two positive VAL/TEST/FWD segments;
and positive outcomes at 2× costs, one-bar delayed state execution, and after removing the top 5%
of trades. Then test the unchanged rule on Kraken. Superiority requires >+61.7% return with drawdown
no worse than −5.5%, while fixed-rule and walk-forward comparisons remain separate.

This is one pre-registered construct. Failure does not authorize selecting one direction, changing
span or confirmation length, adding a deadband/filter, or substituting a signal-line crossover on
the seen data.

## Result

The cheap TRAIN gates all passed: **2,108 trades**, 9/9 positive coins, +49.34 gross and +35.63 net
bps/trade, **+110.91% net return**, 50.12% annualized, Sharpe 1.45, Sortino 1.42, PF 1.20, and
−23.20% maximum drawdown. Longs earned +92.76 gross / +79.00 net bps; shorts earned only +5.91 gross
and **−7.75 net bps**. Turnover was 468.44× and the median trade was −96.38 bps, so large winners
carried a low 34.91% win-rate distribution.

The mandatory 999-draw shared circular-shift placebo then failed: observed gross mean **49.34 bps**,
placebo mean **17.88 bps**, one-sided **p=0.107** versus the frozen ≤0.025 gate. The apparent TRAIN
edge is not exceptional enough relative to persistence obtainable by displaced state sequences.

**Verdict: REJECTED_TRAIN_GATE (placebo).** Held-out stayed sealed. The economically attractive
in-sample result is not promotion evidence, and the observed long/short split does not authorize a
post-hoc long-only test.
