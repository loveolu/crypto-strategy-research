# CRYPTO-EXP-CX-001 — dispersion-conditioned cross-sectional reversal

Pre-registered 2026-09-04 before the first data run. Program: OKX USDT perpetuals. This is a new
interaction test, not another S2 variant.

## Hypothesis

When cross-sectional dispersion in 24-hour returns enters its trailing top quintile, the two worst
performers will outperform the two best performers over the next 24 hours after realistic costs.
The mechanism is forced-liquidation overshoot followed by market-neutral convergence.

## Fixed construction

- Nine perps: BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT, LINK; 1h candles.
- `mom_24 = close.pct_change(24)` and cross-sectional population standard deviation each hour.
- High dispersion means above the 80th percentile of the prior 720 hourly observations. The current
  observation is excluded from its own threshold.
- Enter only on a low-to-high transition, with a 24-bar cooldown. Long the bottom two `mom_24`
  names and short the top two; 0.25 absolute weight each, gross 1.0 and net 0.0.
- Signal at candle close; execution at the open two bars later; exit at the open 24 bars after
  entry. No leverage. Charge A-011 measured per-instrument taker costs on entry and exit.
- One cell only. No parameter search and no optimization.

## Zero-cost pre-gate

Use TRAIN only, through 2024-11-22 23:00 UTC. Stop and reject with zero trials if any condition
fails:

1. At least 50 fully executable event trades.
2. Mean gross return is at least twice the mean realized round-trip cost.
3. Mean signed contribution is positive for at least five of nine instruments.
4. A 1,000-draw circular-shift placebo, seed 20260904, gives one-tailed empirical `p <= 0.05` for
   mean gross trade return. The shift preserves each instrument's return dependence while breaking
   alignment with the selected events and ranks.

The placebo is the multiple-testing control for the single pre-registered cell. Robustness variants
are not inspected unless all four gates pass. A pre-gate failure spends no DSR trial.

## If and only if the pre-gate passes

Evaluate the fixed rule on VAL, TEST, and the already-spent forward window separately. Report gross,
expected-cost, and 2x-cost stress results; 1/2-bar delay; ±20% lookback/threshold/hold sensitivity;
coin leave-one-out; removal of top 5% trades; rolling 30/90/180/365-day performance; long/short leg
metrics; DSR, Monte Carlo, and all seven project promotion criteria. Because the historical windows
have been viewed repeatedly, these outputs are diagnostic and carry the existing selection debt;
they are not described as untouched evidence.
