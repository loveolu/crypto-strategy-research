# CRYPTO-EXP-027 design — lagged extreme-fear relief reversal

Date frozen: 2026-09-04 PDT. Independent parent: none. T-035 established that
Fear & Greed is reactive rather than leading; this tests the still-open reactive-
confirmation mechanism identified in the durable research metrics.

## Hypothesis

An Extreme Fear reading summarizes broad capitulation that has already occurred.
If a coin then prints fresh intraday buying after a negative 24 hours, the first
reversal may mark the start of a relief move lasting several hours. The sentiment
state is confirmation, not an anticipatory signal.

## Frozen rule

- Nine liquid OKX USDT perpetuals on canonical 4h bars, long only.
- Map each Fear & Greed value to its UTC calendar day, then shift it by one full
  day before exposing it to 4h bars. This conservative lag avoids assuming the
  index was tradable at its nominal midnight timestamp.
- State requires prior-day Fear & Greed ≤25. Price confirmation requires current
  4h close > open and completed 24h close-to-close return <0.
- Take only the first qualifying signal per coin per UTC day. Enter next 4h open,
  exit three bars later at the open. Equal 1/9 sleeves, one position per coin,
  measured instrument-specific OKX taker costs.
- No BTC trend gate, alternative fear cutoff, candle-strength threshold, stop,
  target, coin removal, short mirror or holding-period search.

## Chronological gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Held-out remains sealed unless
there are at least 100 trades and eight per coin; gross expectancy exceeds expected
round-trip cost; at least six coins are net-positive; and mean gross return beats
97.5% of 999 circular shifts of the daily sentiment state relative to price (seed
27027, minimum 30-day displacement).

If TRAIN passes, inspect 2024-11-23 through 2026-08-01 once (the last completed day
covered by the immutable sentiment artifact). Require positive net return, Sharpe
and PF, six positive coins, two positive chronological subsegments, and survival
at 2× costs, one-bar delay and top-5% trade removal. Superiority additionally needs
a consistent full return above +61.7% with drawdown no worse than −5.5%.
