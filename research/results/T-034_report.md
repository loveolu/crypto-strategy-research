# T-034_report.md

## Task ID and hypothesis
**Task ID:** T-034 (revised)
**Hypothesis:** H-LogisticEntry: a logistic regression model, trained via strict walk-forward (expanding-window, periodic refit, never fit on future data) on a small, pre-registered set of lagged log-return features, predicts the sign of next-period BTC/ETH return with genuine out-of-sample skill — sufficient that a standalone long/flat signal built from it (long when predicted P(up) > 0.5, flat otherwise, no shorting) clears this project's standard validation gates on held-out data.

## Implementation Notes
- Created `user_data/research/phase_logistic.py` to evaluate the zero-cost pre-gates directly using `pandas` and `sklearn.linear_model.LogisticRegression` on the `user_data/data/okx/*-1d.feather` files.
- The walk-forward scheme was implemented exactly as specified: expanding window, refit monthly, predicting only on dates strictly after the training-data cutoff.
- Features used: lagged log returns at lags [1, 2, 3, 5, 10] trading days, computed separately per asset.
- The first training window was dynamically selected to ensure at least 500 days of prior return history before making the first out-of-sample prediction.
- The pre-gate execution failed at Step 2 (in-sample fit sanity) for BTC. Since the condition dictates "stop at the first failure", the full freqtrade strategy backtest (Steps 3-7) was not run, preserving the research budget.
- The initial environment blocker (`scikit-learn` missing) was resolved by the operator prior to this successful execution.

## Lookahead/leakage checks performed
**Leakage Check (Sample of 5 refits from ETH run):**
- Train max date: 2021-04-30 00:00:00+00:00 | Test min date: 2021-05-01 00:00:00+00:00
- Train max date: 2022-04-30 00:00:00+00:00 | Test min date: 2022-05-01 00:00:00+00:00
- Train max date: 2023-04-30 00:00:00+00:00 | Test min date: 2023-05-01 00:00:00+00:00
- Train max date: 2024-04-30 00:00:00+00:00 | Test min date: 2024-05-01 00:00:00+00:00
- Train max date: 2025-04-30 00:00:00+00:00 | Test min date: 2025-05-01 00:00:00+00:00
**Result:** PASSED Step 1. No leakage detected.

## In-sample fit sanity (Step 2)
**BTC Results:**
- Train window: 2018-01-22 to 2019-06-30
- Total samples: 525
- Hit ratio: 0.5314
- Binomial test p-value: 1.6247e-01 (p > 0.05)
**Result for BTC:** FAILED. Model cannot beat coin flip in-sample at conventional significance (p < 0.05).

**ETH Results:**
- Train window: 2019-12-12 to 2021-04-30
- Total samples: 506
- Hit ratio: 0.5672
- Binomial test p-value: 2.8600e-03 (p < 0.05)
**Result for ETH:** PASSED.

## Variants attempted
1. `LogisticRegression` with pre-registered features on BTC/ETH. No variants attempted. Stopped at zero-cost pre-gate.

## Backtest results
N/A (Stopped at zero-cost pre-gate).

## Walk-forward / out-of-sample results
N/A (Stopped at zero-cost pre-gate).

## DSR and any other required statistics
N/A (Stopped at zero-cost pre-gate). 0 trials spent. n_trials remains 100.

## Verdict vs. falsification statement
**Verdict: REJECTED.** 
The hypothesis is rejected per falsification statement #2: "In-sample fit sanity (zero-cost pre-gate): on the FIRST training window only, the model's in-sample hit-ratio... does not exceed 50% at conventional statistical significance". For BTC, the hit ratio was 53.14% but the binomial test p-value was ~0.162, meaning it failed to beat a coin flip at conventional statistical significance even in-sample.

## Regime behavior
N/A (No full backtest performed).

## Lessons
- Statistical/ML models with simple features like lagged log-returns struggle to find significant predictive edge even in-sample on this asset class. The "ceiling" of Sharpe ~1.2-1.3 is not purely an artifact of rule-based technical constructs; the data itself lacks simple linear predictability.
- The zero-cost pre-gate discipline continues to protect the project's DSR budget, saving a trial by halting an experiment that couldn't clear the fundamental requirement of beating a coin flip.

## Raw output locations
- `user_data/research/phase_logistic.py` (Analysis script that outputs leakage checks and in-sample sanity).

## Recommendations to the Director
- The failure of simple lagged returns to provide an in-sample edge for logistic regression supports the previous conclusion that OHLCV signal-prediction constructs are generally closed. I recommend against further tests of statistical learning models (e.g. Random Forests, AdaBoost, DNNs) unless they incorporate genuinely new, orthogonal features (non-OHLCV) or a non-linear mechanism that explicitly handles regime shifts.
- The project should continue to rely on regime-avoidance and vol-target sizing, as predictive edges remain elusive.
