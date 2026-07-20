# T-021 / F-4: Regime-Gated Pairs Revival backtest — Research Report

## 1. Task ID and hypothesis
**Task ID:** T-021
**Objective:** Implement F-4: Regime-Gated Pairs Revival backtest.
**Hypothesis:** We can harvest BTC-ETH pair edge by restricting trading strictly to trailing windows that pass cointegration gates.
**Falsification statement:** This hypothesis is rejected if the forward rolling cointegration census fails to establish >=60% passing 730d windows, or if the resulting backtest fails the DSR 0.95 gate.

## 2. Implementation Notes
- Evaluated the forward rolling cointegration census using the exact pre-registered implementation (`user_data/research/phase18_cointpair.py`) which computes the rolling Engle-Granger p-values over 730d windows.
- No strategy code or variants were written because the task hit the pre-gate falsification condition immediately.
- The assignment specified "Forward rolling cointegration census must be re-run and pass."

## 3. Lookahead/leakage checks performed and results
N/A — Stopped at pre-gate.

## 4. Variants attempted
1/1. Baseline census evaluation — zero n_trials cost, STOPPED AT PRE-GATE.

## 5. Backtest results
N/A — Stopped at pre-gate.

## 6. Walk-forward / out-of-sample results
N/A

## 7. DSR and any other required statistics
N/A — Zero trials spent, n_trials remains 98.

## 8. Verdict vs. falsification statement
**REJECTED.** The falsification statement requires the hypothesis to be rejected if "the forward rolling cointegration census fails to establish >=60% passing 730d windows". The census execution confirmed that only 3 of 15 rolling windows (20%) passed the `p < 0.05` threshold. The first falsification condition was triggered.

## 9. Regime behavior
The cointegration regime is isolated to a specific historical pocket (2021-2024). It is fundamentally too rare (20% incidence) to support a gated trading strategy that requires a 60% baseline presence.

## 10. Lessons
Gating a strategy to operate only within a specific structural regime (like cointegration) still requires that regime to exist for a significant fraction of the dataset. A 20% regime incidence provides insufficient sample size and tradeable opportunity, confirming the prior closure of the pairs/relative-value direction.

## 11. Raw output locations
- Used the deterministic output of `user_data/research/phase18_cointpair.py`.

## 12. Recommendations to the Director
The failure of this gate reinforces that BTC-ETH cointegration is not just broken post-2024, but historically sparse. Restricting trading to valid trailing windows results in being out of the market 80% of the time, which would likely starve any strategy of the returns needed to clear the fee hurdle. I strongly recommend leaving the pairs/relative-value direction closed, as the structural map of this dataset does not support it.
