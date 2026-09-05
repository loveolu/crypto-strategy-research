# CRYPTO-EXP-023 design — high-volume hammer absorption

Date frozen: 2026-09-04 PDT. Independent parent: none. Archive search found no
prior wick/close-location plus volume-climax strategy in this project.

## Hypothesis

A completed 4h candle with exceptional volume, a long lower wick and a close above
its open represents aggressive forced selling that was absorbed by buyers. During
a broad BTC uptrend, that absorption should predict positive returns over the next
12 hours. Unlike B2, this identifies intrabar rejection and volume, not trailing
downside-volatility rank or a 24h momentum threshold.

## Frozen rule

- Universe: nine liquid OKX USDT perpetuals; 4h candles resampled from canonical 1h
  data. Long only, one equal 1/9 sleeve per coin, at most one open trade per coin.
- A signal requires current 4h volume's trailing 180-bar percentile rank ≥.95,
  lower wick `(min(open,close)-low)/(high-low)` ≥.50, and close > open.
- Regime requires BTC's last fully completed daily close > its 200-day SMA. The
  daily value is exposed only after six subsequent 4h bars.
- Enter at next 4h open, exit three bars later at the open. Use measured OKX
  instrument-specific expected taker spread, slippage and fees on both sides.
- No parameter alternatives, profit target, stop, coin removal or direction reversal.

## TRAIN pre-gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Held-out 2024-11-23 through
2026-09-01 stays sealed unless there are at least 100 trades and ten per coin;
gross expectancy exceeds the universe-weighted expected round-trip cost; at least
six coins have positive net expectancy; and the mean gross trade return beats at
least 97.5% of 999 circular time-shift placebos (fixed RNG seed 23023, shifts at
least 30 days).

If TRAIN passes, open held-out once. Net return, Sharpe and PF must be positive;
at least six coins and two of VAL/TEST/FWD must be positive; and the result must
survive 2× costs, one-bar delay and top-5% trade removal. Only then test the same
frozen rule on Kraken. A superior claim additionally requires a consistent full
record above +61.7% with drawdown no worse than −5.5%.
