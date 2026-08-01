# Perps program benchmark — equal-weight, monthly-rebalanced long basket

**Pre-registered under A-005. Computed 2026-08-01, before any T-038 work exists.**

`PROJECT_OPERATOR_MANUAL.md`, "Promotion comparison": where no champion exists a candidate is
compared against the pre-registered program benchmark, and **a candidate that does not beat this
cannot be promoted regardless of its other metrics.** The perps program has no champion.

**A-XXX ops task.** Perps `n_trials` stays **0**; not appended to `research/trial_sharpe_ledger.csv`;
meta-review counter unchanged. The benchmark is priced at `n_trials = 1` by construction because it
is pre-registered and never searched over.

| Artifact | Path |
|---|---|
| this document | `research/benchmarks/perps_equal_weight_benchmark.md` |
| **machine-readable companion — JSON** | `research/benchmarks/perps_equal_weight_benchmark.json` |
| **criterion-3 paired series — CSV** | `research/benchmarks/perps_equal_weight_benchmark_TEST_returns.csv` |
| full-window series — CSV | `research/benchmarks/perps_equal_weight_benchmark_FULL_returns.csv` |
| run stdout, verbatim | `research/benchmarks/perps_equal_weight_benchmark_run_output.txt` |
| script | `user_data/research/perps_benchmark.py` |

**Companion format: JSON** for the record (nested metric sets, cost snapshot, funding inventory,
worked criterion-3 examples), **CSV** for the return series, because criterion 3 consumes a per-bar
series and CSV is the form a Reviewer can diff and re-read without a parser.

---

## 1. Headline

| Figure | Value |
|---|---|
| **TEST Sharpe, per-period** | **+0.123321** — **POSITIVE** |
| **TEST Sharpe, annualised** | **+2.3560** (factor **sqrt(365)**, daily bars) |
| **TEST MaxDD (realized)** | **−25.02%** → criterion-4 candidate cap **−31.27%** |
| **TEST bars, N** | **151** (2025-04-22 … 2025-09-19) |
| **DSR, TEST split, n_trials = 1** | **0.93914**, sr0 = 0.0, `trial_var_source = estimator_proxy` |

**The benchmark's own TEST Sharpe is positive (+0.123321 per-period).** Criterion 3 is therefore the
binding constraint, not criterion 2: a candidate must not merely be profitable on TEST, it must beat
a benchmark that was itself strongly profitable there. Had the benchmark's TEST Sharpe been negative,
criterion 2 (candidate TEST Sharpe > 0 in absolute terms) would have become binding instead, because
any positive-Sharpe candidate would clear a negative benchmark almost automatically. That is not the
situation here — the TEST window (2025-04-22 … 2025-09-19) was a strong crypto rally, +66.28% on the
basket, and any candidate is being asked to beat that.

**The DSR is mechanically high and is not a quality signal.** At `n_trials = 1`
`expected_max_sharpe()` returns exactly 0.0, so sr0 = 0 and DSR reduces to P(true Sharpe > 0). This
is exactly why manual criterion 1 is an **absolute ≥ 0.95 gate on the candidate**, not a comparison
against this figure. `trial_var_source` is `estimator_proxy` because the perps trial ledger is empty
by design (0 rows, 10 needed); **for this artifact that has no numerical effect at all**, since
`trial_sharpe_var` enters only through sr0 and sr0 is 0 at one trial. It will matter for candidates.

## 2. Construction

| | |
|---|---|
| Instruments | the 9 in `user_data/config_perp.json` — BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT, LINK (all `/USDT:USDT`), read from the config at runtime, never hardcoded |
| Timeframe | 1d futures OHLCV (`user_data/data/okx/futures/`) |
| Position | long-only, equal weight 1/9 |
| **Rebalance** | **monthly — weights reset to 1/9 at the close of the last trading bar of each calendar month** (never on the window's final bar, where no return follows) |
| Costs | `validator.COST_MODEL`, `fill_assumption = "taker"` → **9.0 bps/side**. Entry = 1 × per-side. Each rebalance = per-side × Σᵢ\|w_target,ᵢ − w_drift,ᵢ\| — every leg pays one side, buys and sells alike |
| Realized turnover | **33 rebalances**, mean turnover **10.05%** of notional, **total cost 0.388%** of notional over the window |
| Funding | **EXCLUDED** — §5 |

### Why monthly rebalancing, when the backlog said buy-and-hold

`research/OPS_BACKLOG.md` A-005 as written said "buy-and-hold … no rebalancing turnover". The
operator instruction of 2026-08-01 specifies monthly rebalancing, and it is the better construction
on the merits:

- **An unrebalanced basket stops being equal-weight almost immediately.** Over this window SOL
  returns **20.2×** and DOT **0.97×**, so a never-rebalanced basket ends roughly **46% SOL and 2%
  DOT**. That is not "equal weight" — it is a concentrated position in whichever instrument won,
  selected with hindsight. It flatters the benchmark, and a flattered benchmark raises the promotion
  bar for reasons unrelated to any candidate.
- **Rebalancing charges real turnover**, so the benchmark pays costs on the same footing as a
  candidate instead of being a zero-cost idealisation.

The drift (never-rebalanced) variant is still computed and reported in §7 for reconciliation with the
superseded first A-005 commit. **The monthly-rebalanced series is the benchmark.**

## 3. Window and splits — the perps program's single split triple

```
window       2022-12-23 .. 2025-09-19        1002 daily bars
train_end    2024-11-22                       701 bars
val_end      2025-04-21                       150 bars
test_end     2025-09-19                       151 bars   <- = reserved-holdout boundary
```

**How they were chosen.**

- **Window start 2022-12-23** is the first bar on which all nine instruments have data — BNB's
  inception, the binding constraint. Earlier, an equal-weight basket of the nine does not exist, and
  entering the nine on staggered dates is not a basket of the nine.
- **Window end 2025-09-19** is the perps reserved-holdout boundary
  (`validator.HOLDOUT_BOUNDARIES["perps"]`, operator decision 2026-08-01). `assert_no_holdout()` runs
  on the window and on every train / val / test / walk-forward slice; no bar past the boundary enters
  any window.
- **70/15/15** — the split method carried forward explicitly by
  `research/review_briefs/T-037_PERPS_TRANSITION_brief.md` — applied once to that window, then
  **frozen as literal dates** in `perps_benchmark.py:SPLIT_DATES`. The script re-derives them from
  committed data on every run and **raises** if they no longer match, so a data change surfaces as an
  error rather than silently sliding the windows.

**This triple is mandatory for every perps candidate.** Criterion 3 requires date-identical TEST
overlap. A candidate on a longer series (BTC starts 2020-01-01) passes the *same* triple to
`split_by_dates()` and gets a longer TRAIN with an identical TEST. Different dates make the
comparison **void**, not merely weaker.

## 4. Full metric set

| window | return | CAGR | Sharpe (ann.) | Sharpe (per-period) | Sortino | MaxDD | bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| full | +503.52% | +92.48% | +1.3553 | +0.070938 | +2.0601 | −51.33% | 1002 |
| train | +393.32% | +129.56% | +1.7184 | +0.089945 | +2.7270 | −43.08% | 701 |
| val | −26.42% | −52.61% | −0.4792 | −0.025081 | −0.6621 | −51.33% | 150 |
| **test** | **+66.28%** | +241.82% | **+2.3560** | **+0.123321** | +4.3451 | **−25.02%** | 151 |

Yearly: 2022 −5.1% (9 bars) · 2023 +189.5% · 2024 +83.8% · 2025 +19.5% (to 09-19).
Max single-year share of $ profit **0.4572**. Years 2.75.
PF **2.405**, win rate **53.6%**, **306 instrument-month positions** — full window only; blanked on
sub-window rows, because the trade log is whole-window and repeating it per split would print
full-window figures as if they were TEST figures.

**Walk-forward** (`validator.walk_forward()`'s own anchored arithmetic, 50% + 10%·k, so the windows
are identical to a candidate's):

| W | span | return | Sharpe (ann.) | MaxDD |
|---|---|---:|---:|---:|
| 1 | 2024-05-07 … 2024-08-14 | −18.89% | −0.9609 | −33.58% |
| 2 | 2024-08-15 … 2024-11-22 | +89.10% | +4.1688 | −19.31% |
| 3 | 2024-11-23 … 2025-03-02 | −0.85% | +0.3636 | −38.26% |
| 4 | 2025-03-03 … 2025-06-10 | −9.09% | −0.0920 | −27.78% |

**Positive in 1 of 4 OOS windows.** The do-nothing alternative is not a smooth ride: it loses money
in three of four walk-forward windows and its full-window result rests on 2023 and on W2.

**Monte Carlo.**

- **Harness trade-level gate (`validator.monte_carlo`): PASS** — per-seed p5 Sharpe
  [1.8068, 1.7008, 1.8765, 1.7741, 1.7521], 1000 sims, Sharpe p5 +1.7567 / p50 +2.4785.
- **Bar-level diagnostic: PASS** — per-seed p5 [0.2890, 0.4389, 0.3675, 0.5303, 0.2412].

**Caveat on the trade-level figures.** `validator.monte_carlo()` assumes one position at a time. This
basket holds nine sleeves in **parallel** at 1/9 weight, so treating each instrument-month as a
sequential full-notional trade inflates both the annualisation factor (`sqrt(n_trades/years)`) and
the compounded max drawdown (p95 tail −94.23% is an artifact of that, not a plausible path). **The
bar-level diagnostic is the faithful one for a basket.** Both gate PASS, so the conclusion does not
turn on the distinction. The permuted-order MaxDD also overstates dispersion and **must not** feed
criterion 4 — that uses the realized TEST MaxDD (−25.02%), per `monte_carlo`'s own documented limit.

## 5. Funding — excluded, forced, and the sign convention stated

**Sign convention** (stated even though the term is excluded, so the next task to revisit this need
not re-derive it): OKX USDT perps settle funding every 8 hours, three times daily. **A positive
funding rate means contango and LONGS PAY SHORTS.** For this long-only basket

```
funding_pnl(t) = − rate(t) × position_notional(t)     [summed over settlements]
```

so a positive rate is a **cost**. Including funding would **lower** the benchmark's return; excluding
it **flatters** the benchmark and makes every future candidate look *worse* by comparison, not
better. The omission is therefore conservative with respect to promotion.

**What the project holds — two independent datasets, neither overlapping the window:**

| Dataset | Coverage | Instruments |
|---|---|---|
| `user_data/data/okx/futures/<PAIR>-1h-funding_rate.feather` | 2026-02-26 … 2026-05-28, 266–273 settlements each | all nine |
| `user_data/research/data/funding/<PAIR>-USDT-SWAP.csv` (T-031 recorder) | 2026-04-14 … 2026-07-20, 292 settlements each | nine files, but holds **UNI** and lacks **XRP** |

**The earliest funding datum the project holds is 2026-02-26. The benchmark window ends 2025-09-19.
The gap exceeds five months and there is zero overlap on any instrument.** OKX's public funding
endpoint is retention-limited (~97 days, measured in T-031), so the history cannot be recovered from
the venue; acquiring it is an `A-XXX` data task and A-005 may not touch `user_data/data/`.

**What was done:** funding was excluded entirely. **No proxy, interpolation or backfill was
invented** — extrapolating a 2026 rate onto 2023 would be a fabricated series, the failure mode this
project has already had three times (T-019, T-023, T-025).

**Magnitude**, measured on the only window held, annualised, paid by longs:

| BTC | ETH | SOL | BNB | XRP | ADA | AVAX | DOT | LINK | equal-weight |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| +1.47% | +2.42% | −0.43% | +3.29% | +1.90% | +1.94% | +2.16% | −9.27% | +3.01% | **+0.720%/yr** |

If that magnitude carried over, the benchmark's ~+92%/yr full-window CAGR would be overstated by well
under a percentage point a year — immaterial to any verdict. **But the estimate rests on a
non-overlapping window and is indicative only**; it is not evidence about 2022–2025 funding.

## 6. Survivorship — present, unremoved, stated

The nine instruments are `config_perp.json`'s whitelist, selected in 2026 for having complete cached
history. A basket chosen in 2026 and backtested from 2022 never holds the perps that delisted or went
illiquid in between. Removing this needs a point-in-time OKX listing history the project does not
hold. **Direction: upward** — like the funding exclusion, it makes the benchmark harder to beat.

## 7. Verification

**>100% CAGR defect presumption** (`PROJECT_OPERATOR_MANUAL.md`) — triggered on **train (+129.56%)**
and **test (+241.82%)**:

1. **Costs applied** — VERIFIED. `per_side_cost("taker")` from `COST_MODEL` = 9.0 bps. Entry charges
   exactly that once; each of the 33 rebalances charges it on realised turnover (mean 10.05%). Total
   0.388% of notional over the window. Nothing hardcoded, no default inherited.
2. **Signal lag** — NOT APPLICABLE: there is no signal. Position is constant long from bar 0 and
   rebalance dates are calendar-determined, not data-determined. Returns are close-to-close; no bar
   uses information from a later bar.
3. **Indicator warmup** — NOT APPLICABLE: no indicators, no state to warm up. Splits are pure slices
   of one continuous series.
4. **Survivorship** — PRESENT AND NOT REMOVED (§6), upward.

**Conclusion**: not a cost, lag or warmup defect. (a) 2023–2025 crypto bull on an unhedged long
basket; (b) short-window annualisation — the +241.82% TEST CAGR annualises a 151-bar +66.28% move and
is not a sustainable rate; (c) real, unremoved upward survivorship bias.

**Independent construction check.** A never-rebalanced equal-weight basket must terminate at the
arithmetic mean of the instruments' wealth relatives,
`equity(T) = mean_i(close_i(T)/close_i(0)) × (1 − entry_cost)` — derived from the definition, not the
implementation, so it is a genuine cross-check rather than the code grading itself. Closed form
**6.043410410539**, constructed **6.043410410539**, abs error **1.155e-14**; the script raises on
mismatch. This validates the weight-drift arithmetic the rebalanced path uses between rebalances.

**Drift variant (diagnostic only, NOT the benchmark)** — reconciles exactly with the superseded first
A-005 commit: full +504.34% / Sharpe 1.3370 / MaxDD −50.21%; TEST +62.21% / Sharpe +2.3374
(per-period +0.122344) / MaxDD −23.22%.

`python scripts/data_manifest.py verify` → `OK: 52 files match the manifest`. The check also runs at
import time inside `validator.py`, before any number is computed.

## 8. How to use this for criterion 3

```python
import pandas as pd, validator as V

bench = pd.read_csv("research/benchmarks/perps_equal_weight_benchmark_TEST_returns.csv",
                    comment="#", index_col=0, parse_dates=True)["ret_net"]
# candidate TEST returns must be on IDENTICAL dates, or the comparison is void
res = V.sharpe_difference_se(candidate_test_returns, bench, bars_per_year=365)
res["criterion_3_pass"]     # delta >= se
```

`sharpe_difference_se()` **raises** rather than guessing on mismatched lengths or non-identical
indexes — a silent reindex is exactly how a void comparison would slip through.

**Worked examples, run against this artifact** (so the wiring is demonstrated, not asserted):

| comparison | Sa | Sb | ρ | N | Δ | SE | pass |
|---|---:|---:|---:|---:|---:|---:|---|
| benchmark vs itself | +0.123321 | +0.123321 | +1.000000 | 151 | 0.000000 | 0.000000 | True |
| drift variant vs benchmark | +0.122344 | +0.123321 | +0.986648 | 151 | −0.000977 | 0.013349 | **False** |

**Degenerate edge case, recorded not patched**: a series compared against itself gives Δ = 0 and
SE = 0, and the manual's rule `Δ ≥ SE` is then satisfied. This cannot arise for a real candidate
(SE = 0 requires ρ = 1 *and* identical Sharpes, i.e. the identical series), and the formula is
transcribed literally from the manual as required. Flagged here rather than silently changed to a
strict inequality — that would be a standards change, which is an operator decision.

The second row is the informative one: the drift variant is 98.7% correlated with the benchmark and
its Sharpe is *lower*, so it fails criterion 3 — as it must.

## 9. Warnings that must accompany these numbers

- **DSR WARNING — `trial_var_source='estimator_proxy'`**: the perps trial ledger holds 0 rows (10
  required), so the hurdle falls back to the Lo (2002) estimator proxy, which is **not comparable
  across trade frequencies**. For this benchmark the warning has no numerical effect (sr0 = 0 at
  `n_trials = 1`); it will matter for candidates.
- **COST MODEL NOTE**: slippage (3.0 bps/side) and spread (2.0 bps) are **estimates**, not calibrated
  against realized fills. Fee rates are published OKX regular-tier rates for `okx_usdt_perp` as of
  2026-07-28.
