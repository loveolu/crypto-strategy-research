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

> **Superseded 2026-08-01**: criterion 3 is now a **1.10× Sharpe ratio**, and the paired SE is
> mandatory *reporting* that does not gate. The function below is still required on every candidate;
> it simply no longer decides. §3b records the formula correction, and the manual records why the SE
> gate was removed. The diagnostic that prompted it: at N = 151 the SE gate demanded an annualised
> TEST Sharpe of 3.06–4.57 (+112% to +208% over TEST) — unclearable by arithmetic.

**Added**: `validator.sharpe_difference_se(returns_a, returns_b, bars_per_year)` — the only change to
`validator.py`. Takes raw per-period return series (the rounded annualised Sharpe from `metrics()`
cannot be used: the formula needs ρ between the two series, which no summary statistic carries).
Returns `sharpe_a`, `sharpe_b`, `delta`, `se`, `rho`, `n_obs`, `criterion_3_pass`, plus annualised
mirrors.

Canonical Jobson–Korkie with Memmel (2003):
`SE = sqrt((1/N)[2(1−ρ) + ½(Sa² + Sb²) − (Sa·Sb/2)(1+ρ²)])`, `t = Δ/SE`.

Decisions recorded rather than made silently:

- **`ddof = 1`** (sample sd), matching `validator.metrics()`. Every TEST Sharpe this project
  publishes comes from `metrics()`; using the population sd would report a slightly different
  statistic from the one criterion 3's ratio is applied to.
- **Per-period Sharpes.** Annualised fields are readability mirrors; `t_stat` is invariant because
  it is a ratio of two identically-scaled quantities.
- **No pass/fail field is exposed.** A `criterion_3_pass` would let a caller believe it had
  evaluated criterion 3 when it had evaluated the superseded SE gate.
- **Zero SE is snapped to exactly 0.** For identical series the bracket is 0 mathematically, but
  `np.corrcoef` returns ρ = 1 − 1e-16 and cancellation left SE ≈ 9.4e-10 with a t of 0/9.4e-10 that
  looked like a real number. Clamped on a relative tolerance; `t_stat` is `None` at SE = 0.

It **raises** rather than guessing on: mismatched lengths, non-identical pandas indexes
("Like-for-like or void" requires date-identical overlap, and a silent reindex is how a void
comparison slips through), fewer than 3 bars, NaN/inf, or a constant series.

**TDD, as instructed.** Ten tests written first and **confirmed failing against absent code** — all
ten `AttributeError: module 'validator_under_test' has no attribute 'sharpe_difference_se'`, with the
34 pre-existing tests passing — then implemented. **47/47 pass** after the 2026-08-01 formula
correction, standalone and under `pytest -o addopts=""`.

Coverage: positive SE on correlated series; identical series → Δ = 0 **and** SE exactly 0;
hand-computed closed forms derived in the tests' own docstrings (never copied from a run — A-003's
rule); **a discriminator test that fails against the superseded formula**; 1/√N scaling; Δ
antisymmetric / SE symmetric; `t = Δ/SE` and `t < 0` in the worse-Sharpe direction; annualisation
invariance; absence of any gate field; and the four raise-paths.

### 3b. Formula correction (2026-08-01)

The manual carried `−ρ·Sa·Sb` where canonical Memmel (2003) has `−(Sa·Sb/2)(1+ρ²)`. **Both the manual
and `sharpe_difference_se()` are now canonical.**

The discriminator test uses ρ = −1 with both Sharpes nonzero, where the forms differ most: canonical
gives SE **exactly 1.0**, the superseded form 1.1726039399558574. It was confirmed failing with
*exactly* that superseded value before the fix. The pre-existing hand-computed case could not have
caught this — it has Sb = 0, where both forms coincide.

**Nothing reported changed.** On the only real comparison in the artifacts, SE moved 0.013349 →
0.013348 (0.008%, smaller than the ~0.4% general estimate because ρ = 0.9866 is near where the forms
agree). Benchmark Sharpe, MaxDD, DSR and every metric are byte-identical. And by the same operator
decision the SE no longer gates anything.

## 4. The question the operator asked

**Is the benchmark's own TEST Sharpe positive?** **Yes: +0.123321 per-period (+2.3560 annualised).**

So **criterion 3 is the binding constraint, not criterion 2.** A candidate must not merely be
profitable on TEST — it must reach **≥ 0.135653 per-period (+2.5916 annualised)**, 1.10× a benchmark
that was itself strongly profitable there (+66.28% over 151 bars; the TEST window was a crypto
rally). Had the benchmark's TEST Sharpe been negative, criterion 2 (candidate TEST Sharpe > 0
absolute) would have become binding instead, since any positive-Sharpe candidate clears a negative
benchmark almost automatically. That is not the situation.

**Note for a future program boundary**: a ratio rule is degenerate against a non-positive benchmark
Sharpe (1.10 × a negative number is *easier* to beat). It is well-defined here because the benchmark
Sharpe is positive, and criterion 2 covers the candidate side. Recorded as a known edge case, not a
proposed change.

Worked example proving the wiring: the drift variant (ρ = 0.9866, Sharpe +0.122344 vs +0.123321)
gives Δ = −0.000977, SE = 0.013348, t = −0.0732 — and fails the ratio gate, as it must.

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
