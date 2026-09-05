# CRYPTO-EXP-020 — independent-mechanism portfolio

**Verdict: REJECTED at the portfolio gate.** The frozen B2 and TrendVolTarget
daily returns were only 0.053 correlated, confirming that the mechanisms are
meaningfully different. Their fixed 50/50 initial-capital portfolio nevertheless
did not deliver enough drawdown reduction.

| Common 2023-01-22→2026-09-01 record | Return | Sharpe | Maximum DD |
|---|---:|---:|---:|
| B2 | +92.03% | 1.56 | −9.99% daily |
| TrendVolTarget BTC+ETH | +95.69% | 0.95 | −16.93% |
| **50/50 initial capital** | **+93.86%** | **1.47** | **−11.51%** |

The primary portfolio returned +22.13% in 2023, +45.77% in 2024, +8.31% in
2025 and +0.54% through 2026-09-01. It was positive in every calendar segment,
but neither beat both components' Sharpe nor drawdown. It exceeds Claude's
+61.7% return but fails the joint hurdle because drawdown is worse than −5.5%.

The predeclared weight views do not rescue it: 25% B2 / 75% TVT drew down
−14.16%; 75% B2 / 25% TVT drew down −10.23%. The latter Sharpe of 1.75 is an
interesting allocation property, but selecting it now would be retrospective
weight optimization and its drawdown still fails decisively. Static blending is
closed; any future portfolio allocation requires new forward data.
