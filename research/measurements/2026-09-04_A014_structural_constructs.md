# A-014 — Five structural constructs, pre-registered and run once (2026-09-04)

**Operator-directed. Zero trials.** Script `user_data/research/a014_structural.py`. Kill conditions were
written into the script header before the run. Costs: A-011 measured per-instrument taker. Window
2023-01-22 → 2026-09-01 (consistent for every row; A-013's by-year figures used series ends of
09-03, so the reference rows differ by a few points — ordering unchanged). "OOS" = TEST + FWD,
2025-04-22 → 2026-09-01.

| construct | full | DD | Sharpe | 2023 | 2024 | 2025 | 2026 | OOS | kill check |
|---|---|---|---|---|---|---|---|---|---|
| BENCHMARK (monthly rebal) | +75.4% | −71.2% | 0.56 | +95.5 | +83.9 | −33.9 | −26.2 | −32.2 | — |
| S3 gated vol-target | +88.4% | −30.4% | 0.79 | +48.1 | +61.8 | −18.5 | −3.6 | −6.7 | — |
| **S2 trend-gated cascade** | +64.1% | **−10.8%** | **1.33** | +7.6 | +58.2 | −5.0 | +1.5 | −5.9 | — |
| V5-beta spread | +1.8% | −20.4% | 0.10 | +6.3 | −4.9 | +7.2 | −6.0 | +7.2 | — |
| C  MAR momentum rotation 90d | −12.8% | −30.8% | −0.20 | +9.6 | **−16.8** | −5.6 | +1.4 | +6.7 | **KILLED** (Sh −0.20 ≤ V5 0.10) |
| A  RS switch S2 / V5 | +69.6% | −18.0% | 1.28 | +25.9 | +54.1 | −5.7 | −7.2 | −11.1 | **KILLED** (Sh 1.28 ≤ S2 1.33) |
| E  PF 50/50 S3 + V5 | +43.7% | −15.6% | 0.82 | +26.4 | +26.2 | −5.2 | −5.0 | +0.8 | survives (0.82 > 0.79) — marginal |
| J  S3 gate-only (no vol-target) | +78.1% | −48.2% | 0.60 | +62.9 | +63.8 | −29.9 | −4.8 | −11.7 | diagnostic |
| K  basket rebal DAILY | +68.1% | −70.8% | 0.54 | +93.6 | +76.2 | −33.2 | −26.3 | −32.6 | **KILLED** (< monthly) |
| K  basket rebal WEEKLY | +74.8% | −70.9% | 0.56 | +96.1 | +80.6 | −33.3 | −26.1 | −32.3 | (< monthly) |

## Findings

1. **The majors/alts rotation does not exist as a tradeable 90-day trend.** MAR flipped **43 times**
   and lost −16.8% in 2024 — the year it was designed to win. The 2024→2025 flip visible in
   hindsight is not a clean momentum series in real time; it whipsaws. This *strengthens* the
   "relative value / rotation / dominance" closure with a momentum test to sit beside the
   cointegration one. Its OOS +6.7% ≈ V5's +7.2% — no rotation value added there either.
2. **Regime-switching S2 and V5 adds return and adds drawdown; Sharpe does not improve.** The V5
   sleeve during gate-off periods lost in 2026 (−7.2%) and pushed OOS from −5.9% to −11.1%.
3. **The S3+V5 portfolio survives, barely.** Sharpe 0.79 → 0.82; DD halved (−30 → −16); return
   halved (+88 → +44). First diversified construct with non-negative OOS (+0.8%). Real but modest.
4. **Vol-target sizing HELPS on daily perps** — J vs S3: removing it costs 10 points of return and
   *adds* 18 points of drawdown (−30 → −48). The 1h inversion (T-038/T-040) does not hold at daily.
   This is direct evidence for T-040's "daily bars" reopening path and confirms the spot champion's
   mechanism transfers to perps at daily resolution.
5. **Rebalance-frequency harvesting is dead at measured costs.** Daily < weekly < monthly. The
   diversification return is smaller than the turnover cost even at 13.7 bps RT. The hypothesis
   T-040's assignment parked is closed.
6. **S2 remains the best risk-adjusted construct the program has produced**: Sharpe 1.33, DD −10.8%,
   positive 3 of 4 years, ~0.43 trades/day (corrected A-015). Nothing designed here beat it.

**Construct count 2026-09-02 → 09-04: ≈ 33.** Every window seen. No held-out data remains.
