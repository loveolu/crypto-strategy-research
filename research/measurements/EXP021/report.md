# CRYPTO-EXP-021 — volatility-budgeted B2 sleeves

**Verdict: REJECTED on TRAIN; held-out data remained sealed.** The exact B2
signals, exits and measured execution costs were unchanged. Only entry weights
were changed using completed 42-bar realized volatility.

| TRAIN 2023-01-22→2024-11-22 | Equal 1/9 sleeves | Volatility-budgeted |
|---|---:|---:|
| Trades / coins | 200 / 9 | 200 / 9 |
| Net return | +46.86% | +38.15% |
| Sharpe | 1.82 | 1.73 |
| Maximum drawdown | −5.25% | −4.65% |
| Mean trade weight | 11.11% | 9.52% |
| Largest coin share of absolute P&L | 17.87% | 15.87% |

Four of six gates passed: sample size, breadth, retention of at least 75% of
return, and lower worst-coin concentration. It failed the decisive risk-adjusted
gates. Sharpe declined, and drawdown remained 88.6% of base rather than at most
75%. The sizing rule reduced exposure, but systemic cascades caused coins to lose
together; cross-sectional rescaling could not isolate that common risk.

No held-out, doubled-cost, delayed-entry or full-record benchmark result was
computed. The 42-bar window, clipping bounds and normalization will not be tuned.
