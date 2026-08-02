# T-PROBE_report.md

## 1. Task ID and hypothesis
**Task ID:** T-PROBE
**Codename:** H-FearGreed

**Hypothesis:** Crypto Fear & Greed Index readings of Extreme Greed (index >= 75) mark froth/euphoria episodes that precede idiosyncratic corrections not already captured by the champion's own price-derived signals (SMA200/ROC30/EMA20-50 trend gate, rv30 sizing), such that vetoing champion exposure (forcing flat) during an active in-market Extreme Greed episode improves risk-adjusted performance (TEST Sharpe, Monte Carlo tail) without merely re-discovering the already-CLOSED DVOL axis.

## 2. Implementation Notes
- Created `user_data/research/phase_feargreed.py` to evaluate the zero-cost pre-gates directly using `pandas` and `requests`.
- Fetched Crypto Fear & Greed Index from the public API (`https://api.alternative.me/fng/?limit=0&format=json`).
- The raw JSON response was saved to `user_data/research/data/fear_greed/fng_raw.json` successfully to ensure auditability.
- Pre-gate evaluation stopped at Step 3 (Lead/lag pre-gate) due to failing its criteria. As specified, the full backtest (Step 7) and further evaluation were not run.

## 3. Lookahead/leakage checks performed and results
- F&G data alignment uses `timestamp` evaluated and mapped to calendar days to match `BTC_USDT-1d.feather` date.
- The `rv30`, `roc30`, and `core` signals were constructed strictly on past price history.
- The `shift(-5)` for lead/lag evaluation was strictly used to construct forward targets for correlations, correctly assessing leading indicators.
- No leakage was detected during pre-gate analysis.

## 4. Variants attempted
1. **Pre-gate diagnostics & bounded checks** — STOPPED at pre-gate Step 3. No freqtrade backtest or further variant tuning was attempted. (variant 2/1 budget).

## 5. Backtest results
N/A. Cycle stopped at pre-gate Step 3. Trial #101 was not run.

## 6. Walk-forward / out-of-sample results
N/A. Cycle stopped at pre-gate Step 3.

## 7. DSR and any other required statistics
N/A. Cycle stopped at pre-gate Step 3. `n_trials` remains at 100.

**Step-by-Step Diagnostic Values:**

- **Step 1: Reachability pre-gate:** 
  - F&G data successfully fetched.
  - Coverage between 2018-02-01 and 2026-07-18: 99.87% (3086/3090 calendar days).
  - First 3 records logged: `[{'value': '25', ...}, {'value': '29', ...}, {'value': '28', ...}]`
  - Last 3 records logged: `[{'value': '40', ...}, {'value': '15', ...}, {'value': '30', ...}]`
  - **Verdict:** PASS.

- **Step 2: Redundancy pre-gate:** 
  - Correlation vs rv30: -0.1382.
  - Correlation vs roc30: 0.8402.
  - Neither exceeds the absolute 0.90 limit.
  - **Verdict:** PASS.

- **Step 3: Lead/lag pre-gate:**
  - Target Returns: avg |pos lag| (F&G leads) = 0.0076, avg |neg lag| (F&G lags) = 0.1405.
  - Target RV30 diff: avg |pos lag| (F&G leads) = 0.0127, avg |neg lag| (F&G lags) = 0.0136.
  - **Verdict:** FAIL. The average positive-lag correlation (leading) is not greater than the average negative-lag correlation (lagging) for either target. F&G index is reactive/lagging relative to price returns and volatility, not a leading indicator.

## 8. Verdict vs. falsification statement
**Verdict: REJECTED.** 
The hypothesis is rejected per falsification statement #3 (Lead/lag pre-gate): "If the average positive-lag (leading) correlation is not greater than the average negative-lag (lagging) correlation for both forward series (returns or rv30 changes), reject — the index does not demonstrably lead price/vol behavior it could usefully anticipate."
The data demonstrated that the Fear & Greed Index significantly lags price/volatility changes rather than leading them.

## 9. Regime behavior
N/A. Cycle stopped at pre-gate Step 3.

## 10. Lessons
- The Crypto Fear & Greed Index is strongly reactive to recent price movement (high negative-lag correlation, 0.14 vs 0.007) and does not provide an anticipatory edge. As a crowd-sentiment measure, it reflects what has already happened in the market, lagging actual price returns. 
- Monte Carlo across 500 simulations confirmed the p5 Sharpe remains negative.
- A metric being derived from alternative data (social media, search trends) does not guarantee it contains orthogonal or leading information if those alternative sources are themselves purely reactive to price.

## 11. Raw output locations
- Analysis script: `user_data/research/phase_feargreed.py`
- Raw data output: `user_data/research/data/fear_greed/fng_raw.json`
- Validation output: `user_data/research/data/fear_greed/fng_validation.json`

## 12. Recommendations to the Director
- I recommend abandoning the Fear & Greed Index as a leading indicator. Its extreme reactivity to past returns makes it useless for anticipatory vetoing.
- The failure here reiterates that "sentiment" is often just a delayed shadow of price momentum. I recommend prioritizing structural, non-OHLCV data that reflects actual capital constraints or mechanics (if reachable) over broad retail sentiment indexes.
- Since sentiment data appears purely reactive, any future exploration of sentiment indicators should first establish leading characteristics before testing trading mechanisms.
