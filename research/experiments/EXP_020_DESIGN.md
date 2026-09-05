# CRYPTO-EXP-020 design — independent-mechanism portfolio

Date frozen: 2026-09-04 PDT. Parents: CRYPTO-EXP-013 B2 and the frozen
TrendVolTarget BTC+ETH strategy.

## Hypothesis

B2 earns episodic 4h liquidation-rebound returns, while TrendVolTarget earns slow
directional returns only during established daily uptrends. Their different holding
periods and return drivers may diversify drawdown better than combining two exchanges
running B2.

## Frozen construction

- Allocate 50% of initial capital to fixed-rule B2 on its nine OKX perps and 50% to
  the frozen BTC+ETH TrendVolTarget basket. Do not rebalance between strategy sleeves.
- B2 remains W42/PW180/pct .80/momentum −3.85%/BTC-down/exit .50/hold six 4h bars,
  equal 1/9 sleeves and measured instrument-specific taker costs.
- TrendVolTarget remains close>SMA200, ROC30>0 and EMA20>EMA50, 40% annual-vol target
  quantized to .25, equal BTC/ETH caps, two completed daily bars of execution lag,
  and 15 bps per-side turnover cost.
- Evaluate the common 2023-01-22 through 2026-09-01 period. Aggregate B2 returns to
  UTC days before combining sleeve equity. Report 25/75 and 75/25 initial allocations
  as sensitivity only; no weight is selected after inspection.

## Evidence status and gates

Both components' standalone histories were already viewed, so this is a retrospective
portfolio audit rather than untouched OOS evidence. It cannot promote a new live
strategy without forward validation. The primary 50/50 portfolio must have lower
maximum drawdown and higher Sharpe than each component, remain positive in every
calendar segment in which B2 is positive, and jointly beat the user's Claude hurdle:
total return above +61.7% with drawdown no worse than −5.5%. Failure closes static
B2/TrendVolTarget blending without optimizing weights.
