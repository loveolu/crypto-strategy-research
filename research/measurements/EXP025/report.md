# CRYPTO-EXP-025 — B2 selection-bias audit

**Verdict: STATISTICAL GATE FAILED.** B2 remains the best observed strategy and
continues paper trading, but its historical record does not support Candidate-grade
confidence after conservative selection adjustment.

The perps trial ledger contains no data rows, so cross-trial Sharpe variance cannot
be estimated. This audit uses the documented skew/kurtosis-adjusted estimator proxy
and reports several trial-count assumptions rather than mixing the incompatible spot
research ledger.

| Return basis | Observations | DSR N=50 | N=100 | **N=200** | N=1000 |
|---|---:|---:|---:|---:|---:|
| Fixed-rule trades | 368 | .998 | .995 | **.991** | .970 |
| Fixed-rule daily | 1,319 | .949 | .916 | **.874** | .744 |
| Walk-forward daily | 953 | .725 | .634 | **.543** | .351 |
| Walk-forward active days | 72 | .685 | .590 | **.497** | .310 |

The fixed per-trade result passes, but it includes the selected strategy's in-sample
history and treats trades as independent. The preferred stitched walk-forward daily
stream has Sharpe 1.18 but extreme skew 12.74 and kurtosis 238.56; its N=200 DSR of
.543 is far below the frozen .95 gate.

A separate 10,000-draw circular 30-day block bootstrap is encouraging: 97.5% of
resamples had positive annualized Sharpe, with 5th/50th/95th percentiles of
.257/1.166/1.880. That says positive expectancy is plausible, but the joint rule
required both bootstrap and DSR evidence.

B2 therefore remains **Paper Trading**, not live-eligible. Forward results must
provide independent confirmation; the historical +61.7%/−5.5% hurdle alone is not
sufficient evidence of a deployable edge.
