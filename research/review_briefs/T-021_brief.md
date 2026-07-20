# Review Brief: T-021 (F-4: Regime-Gated Pairs Revival)

## 1. Verdict
**REJECTED AT PRE-GATE 1 (Stationarity/Cointegration Census)**

## 2. Audit Findings
- **Hypothesis Tested Correctly?** Yes. The falsification condition required the rolling cointegration census to establish >=60% passing 730d windows.
- **Falsification Status:** **Triggered.** The census was re-run using `user_data/research/phase18_cointpair.py`. The rolling census only passed 3 out of 15 windows (20%), failing the 60% requirement.
- **Overfitting / Budget Discipline:** **Exemplary.** The falsification condition was applied BEFORE constructing a backtest. No trading rule code was written. Zero trials were spent. `n_trials` remains 98.
- **Ledger Consistency:** `research_index.md`, `research_metrics.md`, and `hypothesis_bank.md` all reflect n_trials = 98 and document the closure of the BTC-ETH pairs/relative-value lane.

## 3. Durable Lessons
- **BTC-ETH Cointegration is Historically Sparse:** The 20% passing rate confirms that cointegration between these assets is not a persistent feature that can be exploited by a rolling window regime selection.
- **Post-2024 ETF-Era Regime Break:** The cointegration relationship is fundamentally broken in the ETF era. Trading the spread on this pair is no longer viable.
- **Structural Map Closure:** The structural map of this dataset regarding OHLCV signal prediction, sizing, short-side, and pairs/relative-value is now considered fully closed.

## 4. Director Action Required
The Independent Reviewer phase for T-021 is complete.
The Research Director must now determine the next research assignment and document it in `research/NEXT_TASK.md`.
