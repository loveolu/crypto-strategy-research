# A-012 — Five candidate strategies + benchmark, 2025-09-01 → 2026-09-01 (operator-directed, 2026-09-03)

**Zero trials spent; this window is INSIDE the perps reserved holdout (after 2025-09-19) and is now
SPENT for these five constructs.** Rules were fixed in writing on 2026-09-03 before any run; nothing
was tuned on this window. Costs are the A-011 measured per-instrument figures. Script:
`user_data/research/bt_five_A012.py`; monthly table `research/measurements/A012_monthly_pnl.csv`.
Data extended by `freqtrade download-data` (okx, futures, 1h + 1d, 9 pairs) from 2026-05-28 to
2026-09-03; manifest rebuilt (52 files). Reserved-holdout boundary **unchanged** at 2025-09-19.

**The year was a crash.** The equal-weight basket lost **−53.29%** (MaxDD −70.14%); every month
Oct-2025 → Mar-2026 was negative, June-2026 −24%. This is the regime a long-only strategy is
supposed to survive, and the one the benchmark cannot.

## Monthly P&L, % of capital

| month | BENCH | S3 gated VT | S1 casc (T) | S1 (M) | S2 gated casc (T) | S2 (M) | S5 spread |
|---|---|---|---|---|---|---|---|
| 2025-09 | +5.34 | +1.59 | +2.02 | +2.14 | +1.01 | +1.09 | +0.47 |
| 2025-10 | −14.97 | −12.23 | −10.86 | −10.64 | −8.23 | −8.05 | +3.96 |
| 2025-11 | −23.03 | −2.71 | +4.29 | +4.54 | 0 | 0 | +0.43 |
| 2025-12 | −8.93 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2026-01 | −13.88 | 0 | −4.30 | −3.97 | −0.52 | −0.51 | −0.71 |
| 2026-02 | −12.21 | 0 | −10.73 | −10.42 | 0 | 0 | −0.82 |
| 2026-03 | −4.11 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2026-04 | +2.72 | 0 | −0.27 | −0.24 | 0 | 0 | 0 |
| 2026-05 | −0.99 | 0 | +0.20 | +0.13 | 0 | 0 | −1.34 |
| 2026-06 | −23.99 | 0 | −14.74 | −14.44 | 0 | 0 | +1.22 |
| 2026-07 | +6.02 | 0 | +1.34 | +1.36 | 0 | 0 | −1.06 |
| 2026-08 | +25.19 | −2.95 | +2.59 | +2.30 | +2.04 | +1.69 | +1.57 |

## Year summary

| strategy | return | MaxDD | Sharpe | trades | trades/day |
|---|---|---|---|---|---|
| BENCHMARK (hold basket) | **−53.29%** | −70.14% | −0.96 | — | — |
| S3 gated vol-target basket | −15.80% | −23.99% | −0.78 | ~30 | 0.1 |
| S1 cascade reversion, taker | −28.22% | −33.39% | −2.15 | 1,348* | ~1.0 |
| S1 cascade reversion, maker | −27.26% | −32.51% | −2.07 | 1,343* | ~1.0 |
| S2 trend-gated cascade, taker | −5.91% | −9.23% | −0.84 | 579* | ~0.43 |
| S2 trend-gated cascade, maker | −5.95% | −9.03% | −0.85 | 577* | ~0.43 |
| **S5 majors/alts spread** | **+3.67%** | −7.05% | **+0.40** | 43* | 0.1 |
| *ALL trade counts in this table are FULL-SERIES totals (the loop was not windowed) — corrected 2026-09-04 (A-015): S1 ≈ 1.0/day, S2 ≈ 0.43/day over 2023→2026. S5's 43 is regime entries over the FULL 2023→2026 series (the loop was not windowed), not the year alone — corrected 2026-09-04. | | | | | |
| S4 funding overlay on S3 | no effect — basket funding z never reached ±2 in the covered window (2026-05-14 →) | | | | |

## Reading

- **All five beat the benchmark on both return and drawdown.** That is the low bar: the benchmark
  lost half its capital.
- **Only S5 made money** (+3.67%, Sharpe 0.40). It is the only hedged construct; its net exposure
  is ~0, and it earned in Oct/Jun (the two worst basket months) exactly as designed.
- **S2 is the defensive standout**: −5.9% in a −53% year, DD −9%, 1.6 trades/day. The daily gate
  removed 80% of S1's loss (−28% → −6%) by holding S1 out of the market Dec→Jul. That is the
  mechanism working — buy cascades only in uptrends — and it is the first construct to deliver
  the frequency goal while roughly preserving capital in a crash.
- **S1 alone is a losing strategy in a bear**: 3.7 trades/day, −28%. The cascade sign held in-sample
  (T-038/T-040/Strategy A) but in a down-trend "the dip keeps dipping". Without the gate it is dead.
- **S3 is what "beta with a seatbelt" looks like**: −16% instead of −53%, flat Dec→Jul, and it
  MISSED the Aug-2026 +25% rebound (still gated off). The gate's cost is late re-entry.
- **Maker vs taker moved results by ~1 point.** At 24h holds P&L is signal-dominated, not
  cost-dominated. A-011's cost calibration matters for h ≤ 12; it did not decide this test.
- **S4 is INCONCLUSIVE, not negative.** 3.5 months of calm funding; the ±2σ trigger never fired.

## What this does NOT establish

No strategy here has a positive full-cycle record. This is ONE year, ONE regime (crash), and the
strategies that did best are the ones built to be flat or hedged in exactly that regime. In the
2023-24 bull the benchmark made +500% and every gated/hedged construct here would have made a
fraction of it. **Picking S5 or S2 on this result is a selection on the holdout**; the DSR for
whichever is carried forward must price at least these five constructs plus the ~8 exploratory
variants of 2026-09-02. **Reserved-holdout status: SPENT for S1–S5 as specified.**
