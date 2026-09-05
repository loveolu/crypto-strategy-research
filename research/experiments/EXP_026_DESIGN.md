# CRYPTO-EXP-026 design — cross-venue return convergence

Date frozen: 2026-09-04 PDT. Independent parent: none. Data: aligned OKX and
Kraken Futures 4h candles for seven common liquid alt perpetuals.

## Hypothesis

Kraken and OKX incorporate information at slightly different speeds. When their
same-coin completed 4h returns diverge unusually far, the lagging OKX price should
converge toward Kraken during the next bar. Using returns rather than price levels
avoids contract-denomination and basis-level differences.

## Frozen rule

- Common universe: ETH, SOL, XRP, ADA, AVAX, DOT and LINK.
- At each exact common UTC 4h close, compute `d = Kraken 4h return − OKX 4h return`.
  Compute the percentile rank of `abs(d)` over the trailing 180 completed bars.
- If rank ≥.95, enter OKX at the next 4h open in `sign(d)`: long when Kraken was
  stronger, short when OKX was stronger. Exit at the following 4h open.
- One position per coin, equal 1/7 sleeves, unleveraged gross notional, measured
  OKX instrument-specific taker costs on both sides. No BTC/trend/volume filter,
  tolerance alignment, threshold alternative or holding-period search.

## Chronological gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Held-out 2024-11-23 through
2026-09-01 remains sealed unless there are at least 500 trades and 50 per coin;
gross expectancy exceeds expected round-trip cost; both long and short gross
expectancy are positive; at least five coins are net-positive; and observed gross
expectancy beats 97.5% of 999 independent circular Kraken-return shifts (seed 26026,
minimum 30-day displacement).

If TRAIN passes, open held-out once. Require positive net return, Sharpe and PF,
both directions and five coins net-positive, and survival at 2× costs, one-bar delay
and top-5% trade removal. A superior claim additionally requires full consistent
return above +61.7% with drawdown no worse than −5.5%.
