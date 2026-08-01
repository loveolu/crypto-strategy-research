# Measurement — TrendVolTarget through the repaired validator (2026-07-30)

**This is a MEASUREMENT, not a cycle.** No trial was spent, nothing was appended to
`research/trial_sharpe_ledger.csv`, no counter advanced, and `research/current_champion.md` was NOT
modified. No promotion or rejection is implied.

## Setup

| | |
|---|---|
| Construct | `research/best_strategy_so_far.py` (TrendVolTarget), reimplemented exactly: 3-of-3 core gate (close>SMA200, ROC30>0, EMA20>EMA50), vol-target `clip(0.40/rv30, 0, 1)` quantized to 25% steps, 50% per-pair cap |
| Data | spot BTC/USDT + ETH/USDT 1d, common window **2019-12-01 → 2026-05-27** (2370 bars) |
| Splits | date-pinned: train ≤ **2024-06-15**, val ≤ **2025-06-05**, test ≤ **2026-05-27** (calendar 70/15/15 on the common window, test pinned to the SPOT holdout boundary) |
| Holdout | enforced, spot boundary 2026-05-27 |
| Costs | `okx_usdt_perp` taker — 9.0 bps/side, 18.0 bps round trip |
| n_trials | 100 (spot program's final count), `record_trial=False` |

## Per-asset sleeves

| | BTC | ETH |
|---|---|---|
| full Sharpe / trades | +1.2519 / 105 | +1.1650 / 81 |
| train Sharpe / trades | +1.5688 / 80 | +1.3317 / 70 |
| val Sharpe / trades | +0.6077 / 20 | +0.1975 / 3 |
| test Sharpe / trades | **−0.2879** / 5 | **+0.9752** / 9 |
| full return / MaxDD | +165.39% / −9.94% | +159.75% / −11.35% |
| walk-forward Sharpes | [0.3314, 2.4308, 0.5006, 1.0682] | [−0.0049, 1.7287, 0.2415, 2.1199] |
| MC Sharpe p5/p50/p95 | +0.3137 / +0.9141 / +1.4443 | +0.2509 / +0.8163 / +1.3112 |
| MC per-seed p5 | [0.2995, 0.3267, 0.3525, 0.3135, 0.2243], spread 0.1283 | [0.2282, 0.2791, 0.3194, 0.2305, 0.2129], spread 0.1065 |
| MC gate | PASS | PASS |
| MC MaxDD p50/p95 | −13.74% / −21.02% | −16.38% / −25.26% |
| DSR (TEST) | **0.00241**, n_obs 356, sr0 0.13275 | **0.05879**, n_obs 356, sr0 0.13396 |
| trial_var_source | estimator_proxy (ledger 0 rows) | estimator_proxy (ledger 0 rows) |
| DSR full-window diagnostic | 0.7733 | 0.70319 |
| Harness verdict | FAIL (Sharpe<1.5; 105 trades<200; test < 0.5×train) | FAIL (Sharpe<1.5; 81 trades<200) |

## Portfolio (both sleeves combined, as the champion trades)

| metric | value |
|---|---|
| FULL | Sharpe **+1.3648**, CAGR +33.34%, return +547.68%, MaxDD **−16.69%**, 209 trades, PF 2.0397, 6.49y |
| train 2019-12-01→2024-06-15 | Sharpe +1.6154, 170 trades, +448.00%, MaxDD −16.27% |
| val 2024-06-16→2025-06-05 | Sharpe +0.5104, 25 trades, +7.21%, MaxDD −14.19% |
| test 2025-06-06→2026-05-27 | Sharpe **+0.6594**, 15 trades, +10.24%, MaxDD −16.02% |
| walk-forward (4 windows) | Sharpes [1.485, 1.011, 1.65, −0.075]; returns [+32.46, +20.35, +29.90, −1.91]%; 3/4 positive |
| MC Sharpe p5/p50/p95 | **+0.4318** / +1.0350 / +1.6030 |
| MC per-seed p5 | [0.4223, 0.5154, 0.5061, 0.3868, 0.4489], spread 0.1286 |
| MC gate | **PASS** (all five seeds > 0) |
| MC MaxDD p50/p95 | −25.83% / −37.85% |
| DSR (TEST) | **0.02891**, n_obs 356, sr0 0.13806, estimator_proxy |
| DSR full-window diagnostic | **0.8356**, n_obs 2370 |

On the record's own stated TEST window (mid-2024 → 2026-05-27, 711 bars): Sharpe **+0.5869**,
39 trades, +18.19%, MaxDD −16.02%, DSR **0.04304**.

## Versus `current_champion.md`

| | recorded | remeasured |
|---|---|---|
| Full-window Sharpe | 1.26 (real engine) | **1.3648** |
| Full-window MaxDD | −16.6% | **−16.69%** |
| Held-out TEST Sharpe | 0.41 | **+0.6594** (or +0.5869 on the record's window) |
| DSR | 0.624 @ n_trials=98 | **0.02891 on TEST** @ 100 — full-window diagnostic 0.8356 |
| MC | "P(Sharpe<0) = 0%" | PASS, but the archived figure was computed on a degenerate distribution |

Return and drawdown reproduce closely. TEST Sharpe comes in **higher** than recorded, consistent with
directive 8 (archived val/test figures were depressed by warmup truncation). The Monte Carlo gate
passes for the first time meaningfully — all five seeds positive.

**The DSR is where the picture changes.** On the TEST split at n_trials=100 the portfolio scores
**0.02891** against a 0.95 bar, where the recorded 0.624 was computed on full-window returns; the
full-window diagnostic here reproduces the flattering regime at **0.8356**. The gap is the WINDOW,
not the data. Both per-asset sleeves still fail the harness outright on Sharpe and trade count, and
BTC's TEST Sharpe is negative on 5 trades.

## Caveats on this measurement

1. **Costs are not like-for-like with the archive.** The perp taker model (9.0 bps/side) was applied
   to SPOT data, as instructed. The archive used 15 bps/side. This measurement is therefore CHEAPER
   than the archived runs and flatters returns relative to them. It is also not the correct cost
   model for spot, which would be 10 bps/side taker plus slippage and spread.
2. **Every DSR here is `estimator_proxy`-sourced**, because `research/trial_sharpe_ledger.csv` is
   empty by design. Those figures are not comparable across trade frequencies.
3. **Split dates are not the archive's.** The record describes TEST as "mid-2024→2026", which spans
   this measurement's val+test. The row for that window is given above.
4. The champion is a two-sleeve portfolio; `validate()` is single-asset. Per-asset figures come from
   `validate()` end-to-end; portfolio figures come from the same repaired primitives
   (`metrics`, `extract_trades`, `monte_carlo`, `wf_window_stability`, `deflated_sharpe`) applied to
   the combined stream.
