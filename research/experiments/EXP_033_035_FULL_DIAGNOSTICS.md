# Full rejection diagnostics — CRYPTO-EXP-033 through 035

All values are frozen TRAIN results (2023-01-22 through 2024-11-22). Gross and net streams use
equal 1/9 sleeves and compound at each 4h exit timestamp. The detailed monthly series and per-coin
results are stored in each experiment's `summary.json`.

| Metric | EXP-033 Fractal | EXP-034 Stars | EXP-035 Outside close |
|---|---:|---:|---:|
| Trades / trades per day | 1,587 / 2.37 | 751 / 1.12 | 1,934 / 2.88 |
| Gross return | +8.37% | −0.50% | +12.56% |
| Net return / annualized | −14.92% / −8.42% | −11.20% / −6.26% | −16.09% / −9.11% |
| Sharpe / Sortino / Calmar | −0.49 / −0.21 / −0.29 | −1.34 / −0.51 / −0.48 | −0.70 / −0.49 / −0.33 |
| Maximum drawdown | −28.94% | −12.97% | −28.01% |
| Profit factor / win rate | 0.94 / 49.09% | 0.78 / 42.08% | 0.92 / 41.16% |
| Gross / net expectancy | +5.81 / −7.90 bps | −0.36 / −13.99 bps | +6.18 / −7.50 bps |
| Average winner / loser | +246.47 / −253.14 bps | +115.66 / −108.17 bps | +202.91 / −154.67 bps |
| Median trade | −8.90 bps | −26.40 bps | −39.76 bps |
| Average holding time | 19.53 h | 4.00 h | 9.64 h |
| Turnover | 352.67× | 166.89× | 429.78× |
| Long / short exposure | 21.39% / 0% | 0.92% / 1.15% | 6.09% / 6.78% |
| Longest losing streak | 22 | 13 | 18 |
| Longest recovery | 9,620 h | 16,040 h | 15,484 h |
| Worst day / week / month | −5.36 / −6.26 / −11.96% | −1.56 / −2.02 / −3.54% | −2.99 / −4.43 / −6.08% |
| Profitable active days | 47.82% | 40.59% | 38.96% |
| Maximum intraday drawdown | −5.36% | −1.58% | −2.51% |
| Positive coins | 3/9 | 3/9 | 2/9 |

## Cost-model boundaries

The net results include the measured per-instrument taker fee/spread/slippage aggregate used by the
project. Its components cannot be separated from the historical bar data, so standalone slippage is
reported as unavailable rather than relabeling aggregate friction. Partial fills and execution
latency cannot be reconstructed from OHLCV. Perpetual borrowing cost is inapplicable. Synchronized
historical funding is unavailable across the full TRAIN span, so funding is explicitly not included;
this is a limitation, not a zero-cost assumption. Each rule already fails because gross expectancy
is below the measured non-funding round-trip friction, so none advances while this limitation remains.

All three held-out periods remained sealed and all three statuses remain `REJECTED_TRAIN_GATE`.
