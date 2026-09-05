# CRYPTO-EXP-027 — lagged extreme-fear relief reversal

Status: **Rejected at the frozen TRAIN sample gate. Held-out data was not examined.**

The rule used the prior UTC day's Fear & Greed reading (a conservative one-day
availability lag), then required a negative completed 24-hour return and the first
green 4-hour candle of the day. Trades entered at the next open, exited 12 hours
later, used equal 1/9 sleeves, and paid measured OKX taker friction.

## TRAIN result (2023-01-22 through 2024-11-22)

| Trades | Net return | Sharpe | Max DD | PF | Gross expectancy | Net expectancy | Positive coins |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 38 | +4.82% | 1.28 | -0.72% | 5.84 | +126.14 bps | +112.45 bps | 9/9 |

The economic observation is unusually clean but too sparse: every coin was
positive, while individual samples ranged from only three to five trades. The
pre-registered requirements were at least 100 total and eight per coin. Because
both sample gates failed, the 999-shift placebo was not run and the 2024-11-23 to
2026-08-01 held-out period remains sealed.

## Conclusion

Extreme-fear relief is an interesting **uncertain finding**, not a validated
strategy. Loosening the fear cutoff, weakening confirmation, changing the hold,
or opening the held-out period would convert a sparse observation into parameter
mining. Close this exact rule and wait for genuinely new sentiment history or an
independently motivated design.

Authoritative machine-readable results: `summary.json`; TRAIN ledger:
`train_trades.csv`.
