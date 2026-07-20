# Task ID and hypothesis
**Task ID:** T-022
**Hypothesis:** A change-based implied volatility signal (e.g., Δ5d DVOL) leads realized volatility (Δ5d rv30) and can be used to dynamically adjust position sizing or gate entries, improving the Deflated Sharpe Ratio above the 0.95 threshold for the current champion.

## Implementation Notes
- Loaded champion strategy `TrendVolTarget` core signals and realized volatility.
- Loaded daily DVOL data from `user_data/research/data/dvol/btc_dvol_daily.feather`.
- Calculated 5-day percentage change in DVOL (`dvol_chg_5d`) to capture implied volatility acceleration.
- Tested multiple change thresholds (10%, 15%, 20%, 25%, 30%, 35%, 40%) as signal triggers.
- Evaluated Pre-Gate 1 (Episode/Materiality Census) by counting contiguous signal blocks while the champion is in-market, as well as checking presence in the TEST split (2025-08-17 to 2026-05-27).
- Evaluated Pre-Gate 2 (Harm Census) by comparing the 10-day forward returns of affected days vs. unconditional in-market days.
- No backtest was built because the hypothesis failed the pre-gates. `n_trials` was not incremented (remains at 98).
- Scratch evaluation script was placed at `research/scratch/t022_pregate.py`.

## Lookahead/leakage checks performed
- DVOL change was calculated over the past 5 days (e.g., `pct_change(5)`).
- Forward returns for the harm census were calculated exclusively using `shift(-10)` on future close prices, and correctly aligned with the signal day.

## Variants attempted
1/10 (Pre-gate evaluation) - Evaluated 5-day DVOL change thresholds from 10% to 40%. All thresholds failed both Pre-Gate 1 and Pre-Gate 2.

## Backtest results
N/A - Stopped at Pre-Gate.

## Walk-forward / out-of-sample results
N/A - Stopped at Pre-Gate.

## Deflated Sharpe Ratio (DSR)
N/A - Stopped at Pre-Gate. (Cumulative `n_trials` remains 98).

## Verdict vs. falsification statement
**Verdict: REJECTED**
The hypothesis triggered the pre-registered falsification conditions for both Pre-Gate 1 and Pre-Gate 2:
1. **Episode/Materiality Census (FAIL):** While lower thresholds (10%-20%) produced >= 6 episodes in-market, **no threshold fired in the TEST split (0 episodes)**. The signal is entirely absent in the most recent 9 months of data.
2. **Harm Census (FAIL):** Days affected by DVOL acceleration are demonstrably **favorable, not adverse**. For example, at a 15% threshold (42 affected days), the median 10d forward return was +6.71% (mean +6.30%), compared to the unconditional median of +0.70% (mean +1.20%). 

## Regime behavior
DVOL accelerates rapidly during the strongest bullish impulses (the "wall of worry"). The options market charges a high premium during these phases, but they consistently resolve higher. Avoiding or sizing down during DVOL acceleration would mean missing the most profitable days of the trend. During the choppy sideways regime (TEST split), DVOL never accelerated significantly while the champion was in-market.

## Lessons
- DVOL *change* (acceleration) suffers from the identical Variance Risk Premium (VRP) positive-carry dynamic as DVOL *levels*. Rapid increases in implied volatility during an uptrend are a bullish continuation signal, not an incoming crisis warning.
- The absence of any DVOL acceleration in the TEST split confirms the mid-2024 to 2026 regime is a structurally distinct, lower-volatility environment where historical IV patterns do not apply.

## Raw output locations
- Evaluation script output in execution logs.
- Evaluation script: `research/scratch/t022_pregate.py`

## Recommendations to the Director
- **Recommendation 1:** Abandon the DVOL/Implied Volatility axis entirely for daily trend-following strategies. Both level-based and change-based constructions fail because VRP is positive-carry; high or accelerating IV means the market is about to go up faster, not crash.
- **Recommendation 2:** The complete absence of DVOL acceleration in the TEST split while in-market suggests the market structure has fundamentally changed (likely ETF institutionalization dampening vol-of-vol). Strategies relying on volatility spikes will starve.
- **Recommendation 3:** Given that we have closed the structural OHLCV map and the IV map, future hypotheses should likely focus on portfolio-level allocations or execution timing (e.g., the intraday UTC anomaly), as individual sleeve mechanisms appear exhausted.
