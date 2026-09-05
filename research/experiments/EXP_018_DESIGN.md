# CRYPTO-EXP-018 design — dual-exchange cascade confirmation

Date pre-registered: 2026-09-04 PDT. Parent: B2 / CRYPTO-EXP-013 and exchange
transfer evidence CRYPTO-EXP-017. This is one new variant justified by genuinely new
Kraken data despite the standing prohibition on further same-data cascade variants.

## Hypothesis

A forced-liquidation cascade is market-wide. An OKX B2 signal confirmed independently
by the same coin and BTC on Kraken should remove venue-specific noise, improve trade
expectancy and reduce drawdown enough to challenge the current B2 leader.

## Frozen construction

- Trade on OKX using its measured per-instrument expected taker costs.
- Common alt universe fixed before testing: ETH, SOL, XRP, ADA, AVAX, DOT, LINK.
- Base OKX B2 is unchanged. Confirmation at the same completed UTC 4h bar requires
  Kraken coin downside-dispersion percentile ≥.80, 24h return ≤−3.85%, completed-
  daily uptrend true, and Kraken BTC 24h return <0.
- Enter at the next OKX open; use the normal OKX B2 exit (<.50 dispersion or six
  held bars). Equal 1/7 sleeves, long only, unleveraged. No tolerance window, asset
  removal, parameter refit or alternative confirmation definition.

## TRAIN pre-gate

TRAIN is 2023-01-22→2024-11-22 23:00 UTC. Held-out data remains unopened unless
consensus has at least 80 trades and at least five per coin; expected-cost expectancy
exceeds same-universe base B2 by at least 25 bps/trade; Sharpe is higher; maximum
drawdown is at most 85% of base; and total return retains at least 90% of base. Failure
closes the exact consensus rule with zero held-out inspection.

## Held-out and benchmark gates

If TRAIN passes, evaluate 2024-11-23→2026-09-01 once. Consensus must beat same-universe
base OOS return and Sharpe with lower drawdown, have ≥5/7 positive coins, and remain
positive at 2× cost, after one-bar delay and after top-5% trade removal. For the user's
explicit Claude hurdle, the full 2023→2026 record must additionally exceed +61.7%
with drawdown no worse than −5.5%. Failure of that final joint hurdle means it is not
declared superior even if it improves some B2 metrics.
