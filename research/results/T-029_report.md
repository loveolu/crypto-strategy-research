# T-029_report.md

## 1. Task ID and hypothesis
**Task ID:** T-029 (Codename: H-ERScale)

**Hypothesis:** Replacing T-028's binary ER veto with a continuous multiplier on the champion's final position weight — full exposure when 30-day Efficiency Ratio sits at or above its causal expanding bottom tercile, ramping linearly to zero as ER approaches the bottom of its own historical distribution — improves the champion's risk profile on held-out data without the single-episode fragility that rejected the binary form.

## 2. Implementation Notes
- Loaded futures data up to 2026-05-27, with overlap window starting 2020-10-01.
- Split dates: TEST started 2025-06-11 and ended 2026-05-27.
- Causal expanding percentile rank (`r_t`) computed manually for each day by evaluating the fraction of strictly past values (up to `t-1`) that are strictly less than `ER_t`. This exactly matches the T-028 veto behavior and preserves the affected day-set constraints.
- Modifying files: `phase24_erscale.py` and `SESSION_2026-07-19_ERSCALE.md` created. No strategy files modified. No fabricated data used.
- Assumptions: Continuous `m_t` applied directly to final quantized champion weights as explicitly instructed.
- All pre-gates and diagnostic verifications correctly ran on the overlap window.

## 3. Lookahead/leakage checks performed
- **ER computation:** Uses `close t` and `close t-30`, available at bar `t` close.
- **Rank (`r_t`) computation:** Uses history strictly up to `t-1`, therefore causal at `t`.
- **Volatility estimator (`rv30`):** Uses history up to `t`.
- **Positions:** Shifted by 2, meaning weights generated at `t` execute at `t+2`. No lookahead bias is present.

## 4. Variants attempted
1. Variant 1/2: H-ERScale pre-gate execution (fee-loaded `final_w` check for materiality and dispersion). Failed at F-P2.

## 5. Backtest results
- Pre-gate STOP. The fee-loaded candidate reached F-P1 (Materiality) and F-P2 (Episode dispersion).
- F-P1 passed with 19.1% materially-affected in-market days (187 full-window, 39 in TEST split).
- **F-P2 failed**: Although the affected TEST days spanned 5 distinct calendar months, the last affected day occurred on 2025-10-09. As a result, 230 TEST days (65.5% of the total 351 TEST days) postdated the last materially-affected day, exceeding the maximum permitted 50.0%.

## 6. Walk-forward / out-of-sample results
Not computed (Stopped at F-P2).

## 7. DSR and any other required statistics
Not computed (Stopped at F-P2). The trial was unspent. `n_trials` remains at **100**.

## 8. Verdict vs. falsification statement
**REJECTED**. The cycle triggered **F-P2 (episode dispersion)**. The continuous action failed precisely where the binary form failed: the materially-affected days are highly concentrated around a specific episode ending in mid-October 2025, leaving 65.5% of the TEST split without any action. Per the pre-registered rules, a stop at F-P2 means the mechanism was not given a statistically meaningful out-of-sample period. 

**The regime-classifier-overlay family stays OPEN.** (Do not close it).

## 9. Regime behavior
The continuous action activated on 187 days (19.1% of in-market days), reducing the total turnover slightly (-0.1692 vs champion). The multiplier effectively dampened exposure during the low-efficiency chop but left over 65% of the recent TEST period (2025-10-10 to 2026-05-27) entirely untouched because ER remained above the causal expanding bottom tercile.

## 10. Lessons
The single-episode dependence (N≈1) pathology observed in T-028 is a property of the *signal threshold* relative to the specific TEST split market regime, not just the *action shape*. The efficiency ratio did not dip below its causal 33.33rd percentile after mid-October 2025, meaning neither a binary veto nor a continuous ramp can provide any protection for the remainder of the TEST period. Zero-cost pre-gates correctly saved trial #101.

## 11. Raw output locations
- Analysis script: `user_data/research/phase24_erscale.py`
- Session log: `user_data/research/SESSION_2026-07-19_ERSCALE.md`

## 12. Recommendations to the Director
- The Efficiency Ratio did not breach the 33.33rd percentile after October 2025. This suggests that either the 2025-2026 period has been historically "efficient" relative to 2020-2024, or the expanding threshold is too slow to adapt to structural regime shifts.
- The regime-classifier family is still open. Since ER's failure here was due to threshold staleness rather than signal invalidity, consider using a rolling window for the percentile rank rather than an expanding window (which becomes sluggish), or explore ADX/MESA which might be more adaptive.
- `n_trials` is still exactly 100.
