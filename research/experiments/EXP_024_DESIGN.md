# CRYPTO-EXP-024 design — volume-led close-strength continuation

Date frozen: 2026-09-04 PDT. Independent parent: none. EXP-023 tested lower-wick
absorption; this tests demand continuation and does not alter the failed hammer.

## Hypothesis

When exceptional 4h volume accompanies a green candle that closes near its high,
urgent buyer execution may be incomplete and continue over the next 12 hours.
Restricting longs to a completed BTC daily uptrend reduces ordinary bear-market beta.

## Frozen rule

- Nine liquid OKX USDT perpetuals, 4h bars resampled from canonical 1h data.
- Signal: current volume's trailing 180-bar percentile rank ≥.90, close > open,
  and close location `(close-low)/(high-low)` ≥.80.
- Regime: BTC's last fully completed daily close > SMA200; expose each daily value
  only after six subsequent 4h bars.
- Enter next 4h open and exit three bars later at the open. Equal 1/9 sleeves,
  one position per coin, long only, measured instrument-specific taker costs.
- No return-magnitude condition, alternative threshold, stop, target, coin removal,
  short mirror or holding-period search.

## Validation gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Held-out remains sealed unless
there are at least 200 trades and 20 per coin; gross expectancy exceeds expected
round-trip cost; at least six coins are net-positive; and observed mean gross return
beats at least 97.5% of 999 circular time-shift placebos (seed 24024; shifts ≥30d).

If TRAIN passes, inspect 2024-11-23 through 2026-09-01 once. Require positive net
return, Sharpe and PF; six positive coins; two positive VAL/TEST/FWD segments; and
positive results at 2× costs, one-bar delay and after top-5% trade removal. Then test
the exact rule on Kraken without refitting. Superiority additionally requires full
return above +61.7% with drawdown no worse than −5.5%.
