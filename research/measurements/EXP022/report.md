# CRYPTO-EXP-022 — systemic-cascade conviction portfolio

**Verdict: REJECTED on TRAIN; held-out remained sealed.** Training diagnosis
showed a real monotonic relationship between same-bar signal breadth and per-trade
expectancy. The frozen implementation therefore traded only events with at least
three triggered coins, allocated 100% capital equally, and stayed flat between
events.

| TRAIN 2023-01-22→2024-11-22 | Equal-sleeve B2 | 3+ coin event portfolio |
|---|---:|---:|
| Events / legs | 129 / 200 | 16 / 65 |
| Net return | +46.86% | **+62.28%** |
| Sharpe | **1.82** | 1.47 |
| Maximum drawdown | **−5.25%** | −12.40% |
| Profit factor | 2.62 | **3.89** |
| Positive coins | 9/9 | 9/9 |

Removing the single best event still produced +44.63%, Sharpe 1.27 and PF 3.21,
so the return was not a one-event artifact. Nevertheless, concentrating all capital
in rare systemic events converted strong conditional expectancy into materially
worse portfolio risk. It failed the predeclared Sharpe and drawdown gates.

No held-out, cost, delay or full-record hurdle result was computed. The three-coin
threshold and full-allocation rule will not be adjusted after this result.
