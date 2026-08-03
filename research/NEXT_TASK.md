# NEXT_TASK — T-038 / H-BasketVolTarget-1h

- **Task ID**: T-038 (first perps research cycle; global monotonic sequence, spot ended T-036, transition brief T-037)
- **Program**: perps
- **Cycle class**: RESEARCH
- **n_trials before this cycle**: 0 (read from `research/research_metrics.md`, perps counter; cap is 30 per `PROJECT_OPERATOR_MANUAL.md`, "Program trial cap and terminal condition")
- **Trials this cycle will spend**: **0 if any pre-gate fails (the normal expectation); exactly 1 if all pre-gates pass and the full validation runs.** Failing a pre-gate does NOT spend a trial.

---

## Objective

Test whether intraday (1h) volatility-target scaling of the equal-weight 9-perp long basket — the risk-management mechanism that was the spot program's single most durable component — beats the frozen perps benchmark net of real taker costs.

## Hypothesis

Scaling the equal-weight, monthly-rebalanced long basket of the 9 `user_data/config_perp.json` perps by a single exposure multiplier `m_t = min(1, sigma_target / sigma_t)` — where `sigma_t` is an EWMA volatility of the basket's 1h returns with 48-hour half-life, `sigma_target` is the TRAIN-split median of `sigma_t`, and `m` is re-applied only when it drifts ≥ 0.10 from the currently-applied value — yields a **net TEST-split per-period (daily) Sharpe ≥ 0.135653** (1.10× the committed benchmark's, quoted from the manual) with **realized TEST MaxDD no worse than −31.27%**, because per-unit-risk basket returns decline as trailing volatility rises (volatility is persistent at the 1h horizon; returns do not scale proportionally with it).

This is a **structural / risk-management mechanism, not a predictive one** — it forecasts risk (which is forecastable) and never direction. It is the first cycle ever run on the 1h sample and the first re-test of the reopened intraday family at real rates.

## Falsification statement

**This hypothesis is REJECTED if any of the following holds:**

1. Pre-gate P1 fails (1h volatility is not persistent on this data at the declared thresholds), or
2. Pre-gate P2 fails (high-trailing-vol hours do NOT have worse per-unit-risk forward returns — mechanism absent), or
3. Pre-gate P3 fails (the fee-free timing benefit does not survive the 18 bps round-trip turnover drag, or timing adds nothing even fee-free), or
4. Pre-gate P4 fails (the mechanism barely fires in the TEST window — comparison uninformative), or
5. At trial: net TEST per-period daily Sharpe (daily-aggregated, identical dates to the benchmark CSV) **< 0.135653**, or realized TEST MaxDD (daily-aggregated equity) **worse than −31.27%**, or the Monte Carlo gate is FAIL, or any validation gate enumerated below fails.

Pre-gate stops 1–4 spend **zero trials**. Outcome 5 spends the one trial. **The best achievable verdict this cycle is PARK, not PROMOTE** — see "Promotion criteria".

## Scientific rationale

- **Program evidence (strongest cross-cycle finding, carried through the T-037 transition):** predictive constructs did not survive out-of-sample; risk-management and structural mechanisms did. Volatility-target sizing is the single component with a spotless record across ~97 spot constructs (`research_metrics.md`, indicator-usage table). Those *numbers* are void as perps evidence — this cycle re-establishes (or refutes) the mechanism on the new venue, cost model, and resolution.
- **Mechanism:** volatility-managed exposure raises Sharpe when (a) volatility is forecastable from its own past (clustering) and (b) expected return does not rise proportionally with volatility, so per-unit-risk return is worse in high-vol states. Both are empirical claims and both are pre-gated below rather than assumed. Grounding: `knowledge_base/hypothesis_bank.md` cards "Volatility-Stabilized Trend Portfolio (VF Rebalancing)" (Kaufman Ch.24 — portfolio-level vol factor with a drift-threshold rebalance rule, exactly the switching-cost-aware form used here), "Trend + Volatility-Target Sizing Combo", and "Equal-Risk (Volatility-Parity) Portfolio Weighting" (`06_volatility.md`, `12_portfolio_construction.md`).
- **Why 1h:** Standing Directive 9 requires preferring samples that can resolve the claimed effect. The pooled/basket 1h sample (~24k basket bars in TRAIN+VAL alone) powers the mechanism censuses; a 151-bar daily TEST cannot power a mechanism test by itself. The manual designates 1h "the preferred sample for the perps program"; no cycle has ever used it.
- **Known adverse precedent, addressed:** H-IVSizing (spot, 2026-07-12) found that days where *implied* vol exceeded *realized* had BETTER forward returns (VRP positive-carry). That was an IV-vs-RV gap on daily bars, not realized-vol level at 1h — but it is a standing warning that vol-conditioned de-risking can select good days. Pre-gate P2 exists precisely to test this instead of assuming it.

## Expected regime(s)

- **Should work:** vol-clustered drawdown regimes — cascading liquidation episodes, 2022-style deleveraging legs, sharp corrections inside the window — where the multiplier is capped down while per-unit-risk returns are poor.
- **Should fail / lag:** high-volatility *rallies* (the construct de-risks into upside vol; the cap at m ≤ 1 means it can never overweight calm rallies to compensate) and any window dominated by a single vol regime (nothing to time). **Note honestly in the report:** the frozen TEST window (2025-04-22 → 2025-09-19) was a strong rally (74.5th percentile of rolling 151-bar windows per the manual); if its rally legs were high-vol, the candidate will trail the benchmark there — that is the hypothesis failing on merit, not a data defect.

## Statistical power statement (Standing Directive 9 — mandatory)

- Absolute TEST daily Sharpe, N = 151: **SE ≈ 1.555 annualised** — the absolute TEST Sharpe alone is nearly uninformative and is NOT this cycle's evidence.
- The promotion-relevant quantity is the **paired difference** vs the benchmark on identical dates. By the manual's Jobson–Korkie/Memmel formula, with candidate–benchmark daily correlation ρ (expected high — the candidate holds the benchmark scaled by m ≤ 1): SE(Δ per-period) ≈ sqrt(2(1−ρ)/151); at ρ = 0.95 → ≈ 0.026 per-period (≈ 0.49 annualised), at ρ = 0.99 → ≈ 0.0115 per-period (≈ 0.22 annualised). The criterion-3 margin is Δ = 0.012 per-period (0.236 annualised). **Report the achieved ρ and SE(Δ); state plainly in the report whether the TEST comparison resolved the effect at 1 SE or not.**
- The mechanism censuses (P1/P2) run on ~24,000 TRAIN+VAL basket 1h bars (and ~185,000 per-asset bars pooled as a diagnostic), where quintile-level effects of the size the vol-managed literature reports are resolvable. **The cycle's informational weight is deliberately on the pre-gates, not on the 151-bar TEST comparison.**
- **Pre-registered correlation problem:** the candidate is the benchmark scaled by m ≤ 1, so ρ is expected to be **0.98–0.99**. At ρ = 0.99, SE(Δ) ≈ 0.0115 per-period against a required criterion-3 margin of 0.012 — **the comparison sits within one standard error of the bar by construction.** The report must state the achieved ρ and SE(Δ) and say plainly whether the result resolved the effect, and **must not present a narrow pass or fail on criterion 3 as a resolved finding.**

## Prior-work check

- **T-037 transition brief (opened by the Director this cycle):** voids every spot performance number and *all* prior Engineer recommendations ("A prior recommendation is not a reason to test anything"). There are therefore no Engineer recommendations to adopt or reject for T-038; the brief contains no hint or ranking. This cycle relies only on the venue-independent finding it carries forward (risk-management mechanisms survived; predictive ones did not).
- **Closed family "Sleeve sizing refinement (estimator quality AND rebalance granularity)"** (H-RangeVol #97, H-SizingBand — ledger row in `knowledge_base/hypothesis_bank.md`): this cycle does NOT touch it. That closure covered refining the *spot champion's existing daily sizing layer* — swapping estimators and sweeping rebalance granularity at its efficient frontier. Here there is no champion and no existing sleeve: this is the perps program's *first candidate construct*, on a resolution (1h) the closed tests never touched, at a different venue and cost model. No estimator comparison is run (one pre-registered EWMA) and no granularity sweep is run (one pre-registered band). The ledger row remains closed and untouched.
- **Intraday / time-of-day / sub-daily family — REOPENED 2026-07-29** on cost-model grounds. This is the first re-test at real rates the reopening note calls for. Finding #12 (hours 21–22 UTC) stays closed and is not touched.
- **T-024 (VF rebalancing, spot):** rejected — but it tested discrete dynamic allocation between spot sleeves under the old cost model; void as perps evidence and structurally different (sleeve allocation vs. basket exposure scaling).
- **H-IVSizing P2 precedent:** handled via pre-gate P2 (see rationale).
- **Hypothesis bank:** no untested card matches this construct exactly (the closest, "Volatility-Stabilized Trend Portfolio (VF Rebalancing)", is already marked ASSIGNED (T-024); "Equal-Risk" is a *cross-sectional* reweighting — a different mechanism, left available). Invented under selection rubric item 7, grounded in the three cards cited above. **No bank card is marked ASSIGNED for T-038.**
- **Index standing constraint** ("new hypothesis must use a genuinely new data dimension or structurally different mechanism"): satisfied — the 1h sample has never been used by any cycle, and no vol-timing overlay has ever been tested on perps.

---

## Deployment envelope (binding)

| Dimension | Value |
|---|---|
| Venue | OKX USDT perpetual swaps, regular (non-VIP) fee tier |
| Config | `user_data/config_perp.json` — futures, isolated margin, `dry_run: true` |
| Instruments | Exactly the 9 whitelist pairs: BTC/USDT:USDT, ETH/USDT:USDT, SOL/USDT:USDT, BNB/USDT:USDT, XRP/USDT:USDT, ADA/USDT:USDT, AVAX/USDT:USDT, DOT/USDT:USDT, LINK/USDT:USDT. No others. |
| Timeframe | 1h (candidate construction and evidence); daily aggregation only for the benchmark pairing |
| Fill assumption | `taker` only. `maker_optimistic` must not appear anywhere in this cycle. |
| Costs (quoted from `PROJECT_OPERATOR_MANUAL.md`, "Execution and cost model") | maker fee 2.0 bps/side; taker fee 5.0 bps/side; slippage 3.0 bps/side; spread 2.0 bps quoted, taker crosses half = 1.0 bps/side; **taker all-in 9.0 bps/side, 18.0 bps round trip**. Single source of truth is `validator.COST_MODEL` via `per_side_cost()` / `round_trip_cost()` — never hardcode these numbers in analysis code. |
| Leverage | None. `m_t ∈ [0, 1]` — the candidate only de-risks; it never exceeds equal-weight exposure. Un-invested fraction sits in USDT at zero yield. |
| Position count | Long-only basket; no shorts. |
| Return envelope | **Any result above 100% CAGR is presumed defective.** Manual check order, quoted: "costs actually applied (not defaulted, not zero); signal lag (`signal_to_returns`'s 2-bar convention); indicators computed over the full series before splitting; survivorship." A result surviving all four is reported *with* that verification; one unchecked is not reportable. |

**Funding P&L is excluded from both candidate and benchmark** — the held funding series starts 2026-02-26 and has zero overlap with the evaluation window (see Environment notes). The candidate holds *less* long exposure on average than the benchmark, so the exclusion flatters the candidate **less** than it flatters the benchmark (conservative direction). State this in the report.

## Data (all held; confirm each exists before starting; **must not be created, modified, or downloaded**)

- 1h futures OHLCV, one file per instrument:
  `user_data/data/okx/futures/<PAIR>_USDT_USDT-1h-futures.feather` for PAIR ∈ {BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT, LINK}. (All 27 futures/mark/funding 1h feathers exist; only the 9 `-1h-futures` files are inputs here.)
- Benchmark record (read it; replicate its monthly-rebalance convention and its 4-window walk-forward construction exactly): `research/benchmarks/perps_equal_weight_benchmark.md`
- Benchmark paired TEST series (read-only): `research/benchmarks/perps_equal_weight_benchmark_TEST_returns.csv`
- Harness: `user_data/research/validator.py` (COST_MODEL, `per_side_cost`, `round_trip_cost`, `split_by_dates`, `assert_no_holdout`, `walk_forward`, `monte_carlo`, `mc_gate_status`, `deflated_sharpe`, `sharpe_difference_se`, `metrics`, `yearly_breakdown`, `append_trial`)
- Trial ledger (append exactly one row ONLY if the trial is spent): `research/trial_sharpe_ledger.csv`

Rules, quoted from the manual: a cycle whose git diff touches `user_data/data/` is INVALID; `scripts/data_manifest.py verify` failing mid-cycle is a stop condition, never run `build`; `FREQTRADE_SKIP_DATA_VERIFY=1` invalidates the cycle. No new external axis is assigned — fetching one would be a scope violation.

## Split specification (FROZEN — not yours to choose)

```
train_end 2024-11-22   val_end 2025-04-21   test_end 2025-09-19
```

- Use `validator.split_by_dates(df, "2024-11-22", "2025-04-21", "2025-09-19")`. Never fractions; `split_70_15_15()` is deprecated and must not appear.
- **Reserved holdout: bars strictly after 2025-09-19 UTC** (program-scoped, perps). The 1h feathers extend to 2026-05-28 — **slice off everything after 2025-09-19 as the very first step**, and call `validator.assert_no_holdout(...)` on every frame before any computation. `validate()` raises `HoldoutViolation` rather than trimming; the caller must exclude explicitly.
- Evaluation window: **2022-12-23 → 2025-09-19** (the benchmark's committed window; BNB's 1h history begins 2022-12-23, so this is also the earliest date with all 9 instruments).
- A candidate evaluated on any other split dates is **VOID against the program benchmark, not weaker evidence** — criterion 3 requires date-identical TEST overlap.

## Construct specification (fully pre-registered — no free parameters, no optimization)

1. **Base basket**: equal-weight (1/9) long basket of the 9 instruments, monthly-rebalanced with **exactly the same rebalance-date convention as the committed benchmark** (read it from `research/benchmarks/perps_equal_weight_benchmark.md` and mirror it). Basket 1h simple-return series `r_t` built from the 1h feather closes, with the benchmark's own rebalance turnover costed at 9.0 bps/side on traded notional.
2. **Volatility estimate**: EWMA variance of `r_t` with half-life **48 bars** (λ = 2^(−1/48) ≈ 0.985663), initialized as an expanding estimate over the first 96 bars (2× half-life). `sigma_t` = sqrt(EWMA var), annualised with **bars_per_year = 8760**. Compute over the **full pre-holdout series once, then split** — never recompute per split (the warmup-truncation defect of Standing Directive 8).
3. **Target**: `sigma_target` = median of `sigma_t` over the TRAIN split only (2022-12-23 → 2024-11-22), excluding the 96 burn-in bars. Computed once; fixed for VAL and TEST. A plug-in, not a tuned parameter.
4. **Multiplier**: `m_raw_t = min(1.0, sigma_target / sigma_t)`; during the 96 burn-in bars `m = 1.0`.
5. **No-trade band**: the *applied* multiplier changes to `m_raw_t` only when `|m_raw_t − m_applied| ≥ 0.10`; otherwise hold `m_applied`. One band value; no sweep.
6. **Lag**: the multiplier computed at the close of bar t takes effect with the same lag convention as `validator.signal_to_returns` (the project's 2-bar convention). If that function cannot carry fractional weights directly, replicate its exact lag arithmetic manually and state so in the report.
7. **Costs**: every change of applied exposure trades `|Δ(m_applied)|` of equity at **9.0 bps per side** (from `per_side_cost()`), in addition to the scaled monthly-rebalance turnover of the underlying basket.
8. **Net candidate return**: `m_applied(t, lagged) × r_t − costs_t`. The fraction `1 − m` earns zero.

**Variant budget: exactly 1 variant (the spec above). 0 optimization runs.** (Manual default is 3 variants / 1 optimization run; the Director assigns fewer, as permitted.) Changing HL, band, cap, target percentile, or estimator = a new variant = exceeding the budget = the cycle is invalidated.

## Zero-cost pre-gate ladder (run in order; STOP at first failure; a stop = REJECT at zero trials)

All pre-gates use only bars ≤ 2025-09-19; P1–P3 use TRAIN+VAL only (2022-12-23 → 2025-04-21); P4 examines the TEST window per the ladder's gate-6 precedent. Pure pandas arithmetic — no backtest engine, no freqtrade run.

**P0 — Reachability (environment check, not a hypothesis verdict).** All 9 `-1h-futures` feathers load; coverage runs through ≥ 2025-09-19 with no internal gap > 24 h inside 2022-12-23 → 2025-09-19. Failure here = report BLOCKED (environment), not a rejection. Do not repair data.

**P1 — Volatility persistence (lead/lag analog).** Per instrument, on TRAIN+VAL 1h log returns: Spearman correlation between `sigma_t` (EWMA as specified, per-asset) and forward realized vol over the next 24 bars (std of log returns t+1…t+24). **PASS requires: median correlation across the 9 instruments ≥ 0.30 AND every instrument > 0.15.** Mandatory sanity checks, quoted from the manual: "any lead/lag census must ASSERT that the −k and +k sides differ before its verdict — exact k↔−k symmetry between two distinct series is a bug signature" — here: also compute the *reversed* pairing (trailing realized vol vs forward EWMA displacement) and assert the two censuses are not identical; "when a diagnostic produces a suspiciously clean result (equal to 4 decimals, perfectly monotonic), treat cleanliness as a bug signal and verify before interpretation."

**P2 — Mechanism existence (harm census; the H-IVSizing lesson applied).** On TRAIN+VAL:
- Primary, basket level: bucket basket bars into quintiles by `sigma_t` (quintile edges from TRAIN+VAL). Per quintile, compute forward 24-bar per-unit-risk return: per bar, (sum of log returns t+1…t+24) / (std of log returns t+1…t+24), averaged within quintile. **KILL if (Q1 per-unit-risk return − Q5 per-unit-risk return) ≤ 0** — i.e., high-vol hours are not worse per unit risk; the mechanism does not exist on this data.
- Secondary, per-asset: same census per instrument (per-asset quintile edges). **KILL if fewer than 5 of 9 instruments show Q1 − Q5 > 0.**
- Report a moving-block-bootstrap 90% CI on the basket Q1−Q5 difference (block length 168 bars, 2,000 resamples — overlapping forward windows make naive t-stats invalid). The CI is REPORTED, not gating: the gate is on sign and breadth; the trial is the real test. Also report the 1-bar-forward version of the same census as a diagnostic.

**P3 — Cost-free upper bound (turnover viability; strongest pre-gate sub-class).** Build the full candidate multiplier and weight series on TRAIN+VAL exactly per the construct spec. Compute:
- (a) **gross** (fee-free) annualised Sharpe of the vol-timed basket vs a **SHUFFLE CONTROL**: rebuild the multiplier from a block-shuffled `sigma` series (block length 168 bars, 200 shuffles, seed pre-registered at **7**), preserving the multiplier's distribution while destroying its timing. **KILL if the real vol-timed gross Sharpe does not exceed the 90th percentile of the shuffled distribution.** Report the real value, the shuffle p5/p50/p90, and the percentile rank of the real value. (Rationale: because `sigma_target` is the TRAIN median, m < 1 roughly half the time, so the construct systematically holds less exposure in high-vol bars; on any volatility-clustered series that lowers realized vol more than mean return and raises Sharpe MECHANICALLY, independent of whether the P2 mechanism exists — a plain-basket comparison would pass by construction.)
- (a2) Retain the plain equal-weight-basket gross-Sharpe comparison as a **REPORTED diagnostic, not a gate**, with a note that it cannot distinguish timing from mechanical variance reduction.
- (b) **net** Sharpe of the vol-timed basket (gross minus per-bar turnover drag: Σ|Δm_applied| × 0.0009, plus scaled monthly-rebalance costs) vs **net** Sharpe of the equal-weight monthly-rebalanced basket at the same cost model, same bars. **KILL if net(vol-timed) ≤ net(equal-weight)** — the mechanism cannot pay its own turnover even in-sample.
- Report total TRAIN+VAL turnover (Σ|Δm_applied|), implied trades per day, and annualised cost drag in bps.

**P4 — TEST activity floor (episode floor + TEST concentration).** On the TEST window (2025-04-22 → 2025-09-19): count distinct de-risking episodes — a maximal run of ≥ 12 consecutive bars with `m_raw_t < 0.9`, separated from the next by ≥ 24 bars at `m_raw ≥ 0.9`. **KILL if fewer than 6 episodes** (H-IVGate floor precedent) **or if fewer than 20% of TEST bars have `m_raw_t < 1.0`.** A mechanism that barely fires in TEST cannot produce an informative benchmark comparison there.

Every pre-gate stop is a verdict and, per the manual ("pre-gate stops get Director reruns"), will be independently rerun — save every script and print every intermediate number into the report.

## Required validation (only if all pre-gates pass; this spends the 1 trial)

1. **Full-window candidate build** on 2022-12-23 → 2025-09-19; `assert_no_holdout` on every frame; splits via `split_by_dates` at the frozen dates.
2. **TEST benchmark comparison (promotion criterion 3 accounting):** aggregate the candidate's net 1h returns to UTC-daily returns over TEST; pair with `research/benchmarks/perps_equal_weight_benchmark_TEST_returns.csv` on **identical dates** (N must be 151; any mismatch → the comparison is VOID — stop and report). Compute per-period daily Sharpes on both sides. Bar, quoted from the manual: candidate TEST per-period Sharpe **≥ 0.135653** (= 1.10 × benchmark's 0.123321; annualised equivalent +2.5916 at √365). "A series compared against itself gives Δ = 0 and does not pass — 1.00× is not 1.10×."
3. **`validator.sharpe_difference_se()` — MANDATORY reporting, non-gating:** paired-difference SE and implied t vs the benchmark TEST series, plus the achieved correlation ρ. Omitting this is a spec violation.
4. **MaxDD (criterion 4):** realized TEST MaxDD on the daily-aggregated equity, cap **−31.27%** (= 1.25 × benchmark's −25.02%). Realized only — never the Monte Carlo MaxDD distribution. Also report the 1h-resolution MaxDD (deeper by construction; informational).
5. **Walk-forward:** the same 4-window construction as the benchmark record (`perps_equal_weight_benchmark.md`); report per-window candidate Sharpe next to the benchmark's per-window figures.
6. **Monte Carlo — pre-registered: PRIMARY on the candidate's net 1h TEST stream (~3,650 bars), bars_per_year = 8760, n_sims = 1000 per seed, seeds = {11, 23, 47}. Criterion 6 is evaluated on the 1h result.** The daily-aggregated TEST MC is retained as a **reported diagnostic** (the benchmark's own TEST Sharpe carries SE 1.555 on the 151-bar daily sample, so daily bootstrap percentiles are wide and the seed-agreement rule would produce INSUFFICIENT for reasons of sample size rather than strategy quality). State both results in the report. The gate has THREE outcomes, quoted from the manual: **PASS** = every seed's p5 Sharpe > 0; **FAIL** = every seed's p5 Sharpe ≤ 0; **INSUFFICIENT** = seeds disagree in sign → **PARK, never PROMOTE**. "INSUFFICIENT is the absence of a result, not a soft FAIL." `n_sims` may NOT be raised after seeing a straddling result — that invalidates the cycle. Use `mc_gate_status`; per-seed p5 values go in the report.
7. **DSR:** `validator.deflated_sharpe` on the TEST stream at **n_trials = 1** (this trial). Threshold ≥ 0.95 (criterion 1). The ledger holds 0 rows, so `trial_var_source` WILL be `"estimator_proxy"` — record it; see promotion criteria.
8. **Regime/yearly breakdown:** `yearly_breakdown` per calendar year of the window plus per-split metrics (Return, CAGR, Sharpe, DSR, Sortino, Calmar, Profit Factor, MaxDD, Win Rate, N trades, Avg trade, Expectancy — manual Validation §3). Annualisation: 8760 for 1h streams, 365 for daily-aggregated.
9. **Parameter-stability statement (manual Validation §6):** no sweep is authorized. Report the pre-registered values (HL 48, band 0.10, TRAIN-median target, cap 1.0) and state that neighbors were NOT evaluated by design (budget: 0 optimization runs); stability assessment is deferred to any future cycle that would pre-register it.
10. **Ledger row (only if the trial ran):** `validator.append_trial(task_id="T-038", construct="BVT-EW-HL48-B10", ...)` with the DSR output's `sr_hat_per_trade`, its `n_obs`, `basis="per_bar"`, date — one row, same commit as the report.
11. **Look-ahead check (manual Validation §8):** confirm sigma and m at bar t use only bars ≤ t; confirm the lag convention; state both in the report.

## Promotion criteria (quoted in full from `PROJECT_OPERATOR_MANUAL.md`, "Promotion rule — FINAL"; ALL SEVEN must hold; no discretion)

1. **DSR ≥ 0.95 on the TEST split at the current `n_trials`.** Absolute gate, not a comparison against the benchmark.
2. **Candidate TEST-split Sharpe > 0** in absolute terms.
3. **Candidate TEST-split Sharpe ≥ 1.10 × the benchmark's** — same window, cost model and fill assumption; against the committed benchmark, **≥ 0.135653 per-period (+2.5916 annualised)**. Paired-difference SE and t from `sharpe_difference_se()` reported, non-gating.
4. **Candidate REALIZED MaxDD ≤ 1.25 × the benchmark's realized TEST MaxDD** — benchmark −25.02%, so the cap is **−31.27%**. Realized only, never the Monte Carlo MaxDD distribution.
5. **Every validation gate in `NEXT_TASK.md` passed.**
6. **Monte Carlo gate is PASS, not INSUFFICIENT.** INSUFFICIENT maps to PARK.
7. **DSR `trial_var_source` is not `"estimator_proxy"`.** Below 10 rows in `research/trial_sharpe_ledger.csv` the hurdle falls back to the Lo (2002) proxy; **until the ledger is populated the maximum available verdict is PARK.**

**PROMOTE IS CURRENTLY UNREACHABLE THIS CYCLE.** `research/trial_sharpe_ledger.csv` holds 0 rows; 10 are needed before cross-trial variance is estimable, so criterion 7 caps this cycle's best outcome at **PARK** regardless of results. Engineer and Reviewer must not work toward, or claim, a promotion. A full pass on criteria 1–6 is recorded as PARK with criterion 7 cited.

## Research budget

- **Maximum strategy variants: 1** (the pre-registered construct). Each variant tested = 1 trial against `n_trials`.
- **Maximum optimization runs: 0.**
- Manual default is 3 variants / 1 optimization run ("Research budget"); the Director assigns fewer, as the manual permits. Reaching a limit without a result = report that and stop. Exceeding it invalidates the cycle.

## Deliverables

1. `research/results/T-038_report.md` — standard format: verdict (REJECT at pre-gate / REJECT / PARK), every pre-gate's numbers, all validation outputs, the SE/ρ statement from the power section, the funding-exclusion statement, the look-ahead confirmation, and paths to all scripts.
2. Analysis scripts under `user_data/research/` (a new `phase_t038_*.py` or similar; do NOT modify frozen `phase*.py` reproduction artifacts per `user_data/research/ARCHIVE_COST_NOTE.md`).
3. One row appended to `research/trial_sharpe_ledger.csv` **only** if the trial was spent.
4. Do NOT write to `research_index.md`, `research_metrics.md`, or `strategy_iteration_log.md` — memory maintenance belongs to the Reviewer.

## Environment notes

- **Funding data has zero overlap with the evaluation window** (earliest held funding datum 2026-02-26 vs window end 2025-09-19, per the A-005 record). Funding P&L is excluded from candidate and benchmark alike; the direction of the resulting bias is anti-candidate (it holds less long exposure), as stated in the envelope section.
- **The 1h feathers extend past the holdout boundary** (to 2026-05-28). Slice to ≤ 2025-09-19 before anything else; `validate()` raises `HoldoutViolation` otherwise.
- `research/champions/` does not exist — expected; it is created by the Reviewer on the first PROMOTE.
- The latest review brief is the T-037 transition brief (highest Task ID). It was opened by the Director; it voids all prior Engineer recommendations, so none were available to weigh for this assignment.
- BNB's 1h history begins 2022-12-23 — identical to the window start; the other eight begin 2022-01-01. No pre-window bars are used.
- The manual defines the variant/optimization budget defaults; no manual gap required Director-invented numbers this cycle.
- `n_trials` cap is 30 (manual, "Program trial cap and terminal condition"); this cycle spends at most 1, leaving ≥ 29.
- RESEARCH:OPS (perps): 0 research / 1 ops before this cycle; this RESEARCH assignment is the ratio-correct choice (floor not yet in force below 6 completed cycles).
- The prior contents of this file (the terminated T-036 record, "NO ACTIVE ASSIGNMENT") are preserved in git history and in `research_metrics.md`'s 2026-07-29 entry; this file is create-or-overwrite per the Director prompt.
