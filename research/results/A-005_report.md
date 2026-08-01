# A-005 — Perps program benchmark + promotion criterion 3

**Class:** OPS / measurement + harness. **Zero trials**; not appended to the trial ledger; does not
advance the meta-review counter. **Perps `n_trials` stays 0.**

**Status:** COMPLETE (2026-08-01). **T-038 is unblocked.**

Three deliverables: (1) the benchmark, (2) its committed artifacts, (3) an implementation of
promotion criterion 3, which did not exist anywhere in the repository.

> **Supersedes the first A-005 commit of the same date.** That commit used an unrebalanced
> buy-and-hold, per the backlog's original wording. Per operator instruction the benchmark is now
> **monthly-rebalanced**; the reasoning is in §1. The drift variant is retained as a labelled
> diagnostic and reconciles exactly, so the two commits are mutually checkable rather than
> contradictory. **Where they differ, this one governs.**

---

## 1. The benchmark

**Full detail, all caveats, and the reproduction recipe are in
`research/benchmarks/perps_equal_weight_benchmark.md`.** Headline only here.

| Figure | Value |
|---|---|
| **TEST Sharpe, per-period** | **+0.123321** — **POSITIVE** |
| **TEST Sharpe, annualised** | **+2.3560** (sqrt(365)) |
| **TEST MaxDD** | **−25.02%** → criterion-4 candidate cap −31.27% |
| **DSR, TEST, n_trials = 1** | **0.93914**, sr0 = 0.0, `trial_var_source = estimator_proxy` |
| Full window | +503.52% / Sharpe 1.3553 / MaxDD −51.33% |
| Walk-forward | **positive in 1 of 4** OOS windows |

Equal-weight long basket of the nine `config_perp.json` perps, 1d, `COST_MODEL` taker (9.0 bps/side),
window **2022-12-23 … 2025-09-19** (1002 bars), splits **2024-11-22 / 2025-04-21 / 2025-09-19**.

**Rebalancing: monthly**, weights reset to 1/9 at the close of the last trading bar of each calendar
month. 33 rebalances, mean turnover 10.05% of notional, total cost 0.388% over the window. Chosen
over the backlog's "buy-and-hold, no rebalancing turnover" because an unrebalanced basket stops being
equal-weight almost immediately — SOL returns 20.2× and DOT 0.97× over this window, so the drift
basket ends ~46% SOL and ~2% DOT, which is a hindsight-selected concentrated bet, and it pays no
turnover cost at all. Both effects flatter the benchmark.

**Splits chosen** as: window start = first bar all nine instruments exist (BNB inception); window end
= the perps reserved-holdout boundary; 70/15/15 (the method T-037 carries forward) applied once and
frozen as literal dates, with a self-check that raises if the data ever stops reproducing them.
**This triple is mandatory for every perps candidate** — criterion 3 needs date-identical TEST
overlap.

**Funding: EXCLUDED, forced.** Positive funding = contango = **longs pay**, so
`funding_pnl = −rate × notional` for this long-only basket and **excluding it flatters the
benchmark**. Two independent funding datasets are held — the feathers (2026-02-26 … 2026-05-28, all
nine) and the T-031 recorder CSVs (2026-04-14 … 2026-07-20, nine files but holding UNI and lacking
XRP). **The earliest datum held is 2026-02-26; the window ends 2025-09-19; zero overlap on any
instrument.** OKX retention is ~97 days, so it cannot be recovered, and A-005 may not touch
`user_data/data/`. No proxy or backfill was invented. Indicative magnitude on the window that *is*
held: **+0.720%/yr paid by longs**, equal-weight.

**Also stated**: the basket is survivorship-biased upward (2026-selected whitelist, backtested from
2022), and the >100% CAGR defect presumption was triggered on train and test and verified on all four
manual checks. The drift variant's terminal equity is reproduced in closed form to 1.155e-14.

## 2. Committed artifacts

| File | Role |
|---|---|
| `research/benchmarks/perps_equal_weight_benchmark.md` | the benchmark record |
| `research/benchmarks/perps_equal_weight_benchmark.json` | **machine-readable companion (JSON)** |
| `research/benchmarks/perps_equal_weight_benchmark_TEST_returns.csv` | **criterion-3 paired series**, 151 bars |
| `research/benchmarks/perps_equal_weight_benchmark_FULL_returns.csv` | full-window series, 1002 bars |
| `research/benchmarks/perps_equal_weight_benchmark_run_output.txt` | run stdout, verbatim |
| `user_data/research/perps_benchmark.py` | the script (`git add -f`; `user_data/*` is ignored) |

Both CSVs embed split dates, window, holdout boundary, instruments, cost model and funding treatment
as `#` header lines, so the series carries the window it was computed on. Read with
`pd.read_csv(..., comment="#", index_col=0, parse_dates=True)`.

The four `perps_benchmark_*` files from the first commit were removed — leaving two benchmark records
with different numbers in one directory is how a later comparison silently uses the wrong one. They
remain in git history.

## 3. Promotion criterion 3 — implemented

**The gap.** `PROJECT_OPERATOR_MANUAL.md` has required criterion 3 since 2026-07-29 and **nothing in
the repository implemented it** — no `jobson`, no `memmel`, no paired standard error anywhere.
Criterion 3 was unevaluable, and since the promotion rule says failing any one criterion is
REJECT/PARK with no discretion, **no candidate could ever have been promoted.**

**Added**: `validator.sharpe_difference_se(returns_a, returns_b, bars_per_year)` — the only change to
`validator.py`. Takes raw per-period return series (the rounded annualised Sharpe from `metrics()`
cannot be used: the formula needs ρ between the two series, which no summary statistic carries).
Returns `sharpe_a`, `sharpe_b`, `delta`, `se`, `rho`, `n_obs`, `criterion_3_pass`, plus annualised
mirrors.

Formula transcribed literally from the manual:
`SE = sqrt((1/N)[2(1−ρ) + ½(Sa² + Sb²) − ρ·Sa·Sb])`, pass iff `Δ ≥ SE`.

Three decisions recorded rather than made silently:

- **`ddof = 1`** (sample sd), matching `validator.metrics()`. Every TEST Sharpe this project
  publishes comes from `metrics()`; a criterion that used the population sd would judge a slightly
  different statistic from the one in the report.
- **The verdict is computed once, from the per-period pair.** Annualised fields are reported for
  readability only. Scaling both sides by the same `sqrt(365)` cannot change the verdict; mixing
  conventions can.
- **Formula discrepancy, flagged not fixed.** Canonical Memmel (2003) carries `−(Sa·Sb/2)(1+ρ²)`
  where the manual writes `−ρ·Sa·Sb`. They agree at ρ = 1 and differ elsewhere; at this project's
  per-period Sharpe magnitudes (|S| ≈ 0.1) the gap is ~0.4% of SE, far below the resolution at which
  criterion 3 decides anything. **The manual governs and is implemented literally.** Changing it is
  an operator decision, not a code fix.

It **raises** rather than guessing on: mismatched lengths, non-identical pandas indexes
("Like-for-like or void" requires date-identical overlap, and a silent reindex is how a void
comparison slips through), fewer than 3 bars, NaN/inf, or a constant series.

**TDD, as instructed.** Ten tests were written first in `scripts/test_validator.py` and **confirmed
failing against absent code** — all ten `AttributeError: module 'validator_under_test' has no
attribute 'sharpe_difference_se'`, with the 34 pre-existing tests passing. Then implemented.
Final: **44/44 pass**, standalone and under `pytest -o addopts=""`.

Coverage: positive SE on correlated series; identical series → Δ = 0 **and** SE = 0; a hand-computed
closed-form value derived in the test's own docstring (not copied from a run — A-003's rule);
1/√N scaling; Δ antisymmetric and SE symmetric; the worse-Sharpe direction never passes; annualisation
verdict-invariance; and the four raise-paths.

**Degenerate edge case, recorded**: a series against itself gives Δ = 0, SE = 0, and `Δ ≥ SE` is
satisfied. It cannot arise for a real candidate (SE = 0 requires ρ = 1 *and* equal Sharpes) and the
manual's inequality is transcribed as written; flagged rather than silently tightened to `>`.

## 4. The question the operator asked

**Is the benchmark's own TEST Sharpe positive?** **Yes: +0.123321 per-period (+2.3560 annualised).**

So **criterion 3 is the binding constraint, not criterion 2.** A candidate must not merely be
profitable on TEST — it must beat a benchmark that was itself strongly profitable there (+66.28% over
151 bars; the TEST window was a crypto rally). Had the benchmark's TEST Sharpe been negative,
criterion 2 (candidate TEST Sharpe > 0 absolute) would have become binding instead, since any
positive-Sharpe candidate clears a negative benchmark almost automatically. That is not the situation.

Worked example proving the wiring: the drift variant (ρ = 0.9866 with the benchmark, Sharpe
+0.122344 vs +0.123321) gives Δ = −0.000977 against SE = 0.013349 → `criterion_3_pass False`, as it
must.

## 5. Bookkeeping

- Perps `n_trials` **stays 0**; **not** appended to `research/trial_sharpe_ledger.csv` — that ledger
  records the cross-trial variance of *searched* trials, and a never-searched construct would corrupt
  the statistic it exists to supply.
- Meta-review counter unchanged. `research_metrics.md`: perps OPS count 1 (A-005).
- `research/research_index.md`: benchmark headline + frozen split triple recorded; the stale
  "Holdout: all bars after 2026-05-27" line corrected to the manual's resolved perps boundary
  (2025-09-19). The manual is primary; the index was the defect.
  `research/review_briefs/T-037_PERPS_TRANSITION_brief.md` line 41 carries the same superseded date
  and was **not** edited — it is a historical verdict record; flagged here instead.
- `validator.py` modified **only** by the addition in §3. `user_data/data/` untouched. No research
  task assigned.
