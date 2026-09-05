# CRYPTO-EXP-028 — one-minute volume-shock overshoot

Status: **Rejected at the frozen TRAIN economic gate. Validation and TEST were not examined.**

## Setup

The hypothesis was that the most extreme one-minute returns accompanied by high
quote volume contain temporary market impact that reverses over five minutes.
Signals used only the prior 1,440 bars for percentile thresholds, entered at the
next open, and paid instrument-specific taker fee, half-spread and measured $5k
book-walk costs. The 29 complete common days were split 15/7/7 chronologically.

## TRAIN result (2026-08-04 through 2026-08-18)

| Trades | Gross expectancy | Measured RT cost | Net expectancy | Net return | Max DD | PF | Positive coins |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 988 | **-1.46 bps** | 13.62 bps | -15.08 bps | -15.26% | -15.28% | 0.12 | 0/9 |

The signal is frequent (65.9 trades/day) and well distributed (91–128 trades per
coin), so lack of sample is not the issue. The required reversal is absent before
costs. Down shocks had only +0.14 gross bps of subsequent reversal; up shocks
continued rather than reversed, losing -3.31 gross bps when faded. Friction consumed
14.96% of sleeve capital in 15 days and was more than twice total gross winning P&L.

The annualized return and Sharpe fields in `summary.json` are mechanically reported
for completeness but are not economically interpretable on a 15-day TRAIN window.
The per-trade gross result is sufficient to reject the mechanism.

## Gate discipline and conclusion

The sample gates passed, but gross did not exceed cost, neither breadth nor the
short-direction sign passed, and 0/9 coins were net-positive. Therefore the placebo
was skipped and validation (2026-08-19–25) and TEST (2026-08-26–09-01) remain sealed.

Do not reverse the signal after seeing this outcome, tune the percentile/holding
period, or inspect direction subsets. The exact 1m impact-overshoot hypothesis is
closed. A different microstructure design requires order-flow/order-book history,
not another OHLCV threshold search.
