# T-030 Report: H-ADXGate

## 1. Task ID and hypothesis

**Task ID:** T-030
**Codename:** H-ADXGate

**Hypothesis:** Vetoing the champion's position (weight → 0) on in-market days where the pair's own 14-bar Wilder ADX, lagged one bar, sits below the absolute no-trend threshold of 20 improves the champion's held-out risk profile — because low-ADX in-market days are genuinely adverse (as low-ER days were proven to be in T-028) AND an absolute-level threshold keeps firing in the 2025–26 regime where the ER expanding-percentile threshold went silent.

## 2. Implementation Notes

- Script created at `user_data/research/phase25_adxgate.py`.
- No deviations from the locked constants were made.
- ADX calculation implemented exactly as specified, cross-checked against TA-Lib (BTC mean abs diff = 0.0022, ETH mean abs diff = 0.0055).
- Pre-registered constants written to `user_data/research/SESSION_2026-07-19_ADXGATE.md` and script docstring before execution.
- Evaluated on the frozen 2026-05-27 futures datasets.
- Stopped at pre-gate F-P2. Trial #101 was NOT constructed or evaluated.

## 3. Lookahead/leakage checks performed and results

- TR, +DM, -DM, and ADX use only OHLC data available at the bar's close.
- Wilder smoothing implemented with `ewm` without future peeking.
- The veto mask uses `.shift(1)` to ensure the ADX value from bar `t-1` is applied to weight at bar `t`.
- The `net_from_weights` harness uses `.shift(2)` on positions.
- No leakage was detected.

## 4. Variants attempted

1. **Pre-gate diagnostics & bounded checks** — STOPPED at pre-gate F-P2. The idealized fee-free construction and locked fee-loaded trial were not reached. (0/2 budget).

## 5. Backtest results

N/A. Cycle stopped at pre-gate F-P2. Trial #101 was not run.

## 6. Walk-forward / out-of-sample results

N/A. Cycle stopped at pre-gate F-P2.

## 7. DSR and any other required statistics

N/A. Cycle stopped at pre-gate F-P2. `n_trials` remains at 100.

**Step 2 Diagnostic Values:**

- **2a. ADX14 summary statistics:**
  - BTC FULL: Min 0.0000, p25 20.4678, Median 26.0870, p75 35.2754, Max 71.2543
  - BTC TEST: Min 9.4266, p25 17.9141, Median 24.3534, p75 30.6159, Max 58.3083
    - TEST split start ADX: 17.8895
    - Fraction ADX < 20 (ALL): full=22.1%, TEST=35.0%
    - Fraction ADX < 20 (IN-MARKET): full=14.6%, TEST=47.1%
  - ETH FULL: Min 0.0000, p25 21.8212, Median 27.6225, p75 36.2329, Max 62.8317
  - ETH TEST: Min 10.7755, p25 20.6802, Median 24.6224, p75 37.9369, Max 56.3420
    - TEST split start ADX: 24.0609
    - Fraction ADX < 20 (ALL): full=18.5%, TEST=23.1%
    - Fraction ADX < 20 (IN-MARKET): full=21.1%, TEST=25.0%

- **2b. Veto-day census:**
  - BTC Veto days: 127 (15.0% of in-market)
  - ETH Veto days: 120 (20.7% of in-market)
  - Combined Veto days: 224 (22.9% of in-market)
  - Combined Veto episodes: 45
  - Episode lengths: min 1, median 3.0, max 16

- **2c. GATE F-H1 (vol proxy):**
  - BTC |ρ| FULL=0.2473 (TEST=0.7085)
  - ETH |ρ| FULL=0.1809 (TEST=0.4200)
  - Gate passed (|ρ| < 0.70 on FULL window).

- **2d. GATE F-H2 (harm census):**
  - Affected days (n=222): median=-0.13%, mean=+0.78%
  - Unconditional in-market (n=936): median=+0.77%, mean=+1.49%
  - Gate passed (affected median and mean strictly below unconditional).

- **2e. Day-set overlap diagnostic (ADX vs ER):**
  - Jaccard overlap (in-market days): FULL=0.3525, TEST=0.6379

## 8. Verdict vs. falsification statement

**VERDICT: REJECTED (Stopped at pre-gate F-P2).**
The cycle triggered F-P2 (episode dispersion): "The TEST-split veto days fall in fewer than 3 distinct calendar months, OR more than 50% of TEST-split days postdate the last veto day."
- Distinct calendar months with vetoes in TEST: 5
- Last veto day in TEST: 2025-10-10
- Days postdating last veto in TEST: 229 (65.2%).
Because > 50% of TEST days postdate the last veto day, F-P2 is triggered.

Per `NEXT_TASK.md`, this CLOSES the regime-classifier-overlay family on the frozen research dataset.

## 9. Regime behavior

N/A. Cycle stopped at pre-gate F-P2.

## 10. Lessons

- **Absolute thresholds succumb to the same concentration pathology as expanding relative thresholds.** Despite ADX < 20 being a fixed literature constant, the absolute threshold signal still failed F-P2 at exactly the same date range as T-029 (last veto day 2025-10-10 for ADX, 2025-10-09 for ER).
- The absence of recent classifier-detectable chop is a property of the frozen evaluation window itself, not just an artifact of the indicator's threshold construction. The market simply hasn't produced the required chop signature in the last ~8 months of the TEST window.

## 11. Raw output locations

- Analysis script: `user_data/research/phase25_adxgate.py`
- Session narrative: `user_data/research/SESSION_2026-07-19_ADXGATE.md`

## 12. Recommendations to the Director

- **Regime Classifier Family is Closed:** As pre-registered, the F-P2 failure closes the regime-classifier-overlay family (ER, ADX, MESA/Hilbert, HMM) on the frozen dataset. The reopening condition is strict: the frozen research window must be extended ≥ 6 months beyond 2026-05-27 with a freshly cut held-out split, or the forward dry-run lane must document a completed in-market chop episode. Do not attempt further chop-classifier variations on this dataset.
- **Harm is Real but Unharvestable:** The F-H2 census confirmed again that low-directionality days (measured by ADX < 20) are genuinely adverse (median -0.13% vs unconditional +0.77%). The problem is not the theory of chop harm, but the concentration of these days in the TEST window.
- **Dataset staleness:** We have repeatedly hit the limits of the TEST split (2025-06 to 2026-05). The recent 8-month period lacks the specific signatures needed to validate regime classifiers. We should prioritize hypotheses that do not rely on recent chop episodes to demonstrate out-of-sample edge.
