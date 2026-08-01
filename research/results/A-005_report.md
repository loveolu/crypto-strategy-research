# A-005 — Perps program benchmark: computed and committed

**Class:** OPS / measurement. **Zero trials for the program**; the benchmark itself is priced at
`n_trials = 1` by construction. Does not advance the meta-review counter. **Perps `n_trials` stays 0.**

**Status:** COMPLETE. **T-038 is unblocked.**

Assigned from `research/OPS_BACKLOG.md`, A-005. Executed 2026-08-01 against the specification there
verbatim; nothing in the specification was varied. No research task was assigned, `validator.py` was
not modified, and `user_data/data/` was not touched.

---

## 1. Headline — the numbers the promotion rule consumes

| Figure | Value | Consumed by |
|---|---|---|
| **TEST Sharpe, per-period** | **+0.122344** | promotion criterion 3 (Jobson–Korkie SE) |
| **TEST Sharpe, annualised** | **+2.3374** | reporting; factor = **sqrt(365)**, daily bars |
| **TEST MaxDD (realized)** | **−23.22%** | criterion 4 → candidate cap **−29.03%** (1.25×) |
| **TEST bars, N** | **151** (2025-04-22 … 2025-09-19) | criterion 3's `N` |
| **DSR, TEST split, n_trials = 1** | **0.93713** (sr0 = 0.0) | criterion 1 is an *absolute* gate on the candidate, not a comparison against this |

Both Sharpe conventions are stated because criterion 3's formula takes **per-period** Sharpes and
mixing conventions changes the verdict. Annualising both sides by the same sqrt(365) scales Δ and
SE(Δ) identically and leaves the verdict unchanged — but only if both sides are annualised.

**The DSR is mechanically high and is not a quality signal.** At `n_trials = 1`,
`expected_max_sharpe()` returns exactly 0.0, so sr0 = 0 and DSR collapses to P(true Sharpe > 0).
This is precisely the "high by construction" property the manual cites as the reason criterion 1 is
absolute rather than a comparison. A candidate does **not** need to beat 0.93713; it needs ≥ 0.95 at
its own honest `n_trials`.

## 2. Specification compliance

| Spec line (OPS_BACKLOG A-005) | How it was met |
|---|---|
| Equal-weight buy-and-hold of the 9 `config_perp.json` instruments | Whitelist read from `config_perp.json` at runtime (rapidjson, PM_COMMENTS), never hardcoded; run raises if it is not 9 pairs |
| `COST_MODEL`, `fill_assumption = "taker"` | `validator.per_side_cost("taker")` = 9.0 bps/side. No cost number appears anywhere in the script |
| Entry cost once per instrument; no rebalancing turnover | Bar 0's net return is exactly −9.0 bps; nothing is charged again. Weights **drift** thereafter — that is what buy-and-hold means |
| Funding: state explicitly, justify if excluded | **EXCLUDED.** §5 below |
| DSR at `n_trials = 1` | Via `validator.deflated_sharpe(...)`, TEST split, `basis = per_bar` |
| Splits pinned by DATE, honouring the reserved holdout | §3 below. `assert_no_holdout` runs on the window and on every train/val/test/WF slice |

## 3. Window and splits — the perps program's single split triple

```
window       2022-12-23 .. 2025-09-19        1002 daily bars
train_end    2024-11-22                       701 bars
val_end      2025-04-21                       150 bars
test_end     2025-09-19                       151 bars   <- = reserved-holdout boundary
```

**Window start (2022-12-23)** is the first bar on which all nine instruments have data — BNB's
inception, the binding constraint. Before it an equal-weight basket of the nine does not exist, and
entering the nine on staggered dates is not buy-and-hold of the nine.

**Window end (2025-09-19)** is the perps reserved-holdout boundary (`validator.HOLDOUT_BOUNDARIES`,
operator decision 2026-08-01). No bar past it enters any window.

**Split method**: 70/15/15 — the method carried forward explicitly by
`research/review_briefs/T-037_PERPS_TRANSITION_brief.md` — applied once to the benchmark window and
then **frozen as literal dates** in `perps_benchmark.py:SPLIT_DATES`. The script re-derives them from
the committed data on every run and **raises** if they no longer match, so a data change surfaces as
an error instead of silently sliding the windows.

**This triple is the perps program's split triple, and every candidate must use it.** Criterion 3
requires date-identical TEST overlap. A candidate on a longer series (BTC starts 2020-01-01) passes
the *same* triple to `split_by_dates()` and gets a longer TRAIN with a byte-identical TEST window. A
candidate that uses different dates is void against this benchmark — not weaker evidence, void.

*(This also answers, for perps, the question A-007 raises for the legacy harness callers. A-007
remains unassigned and untouched here.)*

## 4. Full metric set

| window | return | CAGR | Sharpe (ann.) | Sharpe (per-period) | Sortino | MaxDD | bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| full | +504.34% | +92.57% | +1.3370 | +0.069981 | +2.0401 | −50.21% | 1002 |
| train | +444.28% | +141.62% | +1.7508 | +0.091641 | +2.7904 | −40.35% | 701 |
| val | −31.55% | −60.24% | −0.6705 | −0.035097 | −0.9357 | −50.21% | 150 |
| **test** | **+62.21%** | +221.94% | **+2.3374** | **+0.122344** | +4.2191 | **−23.22%** | 151 |

Yearly: 2022 −5.1% (9 bars) · 2023 +203.6% · 2024 +70.6% · 2025 +23.0% (to 09-19).
Max single-year share of $ profit **0.4032**. Years 2.75.

**Profit factor 1679.75, win rate 88.9%, 9 trades — FULL WINDOW ONLY.** These are trade-derived and
buy-and-hold holds exactly one position per instrument across the entire window, so there is no
per-window trade log. They are blanked (`None`) on the train/val/test/WF rows rather than repeated,
which would have printed full-window figures as if they were TEST figures. PF does not enter any
promotion criterion.

**Walk-forward** — `validator.walk_forward()`'s own anchored window arithmetic (50% + 10%·k), so the
windows are identical to a candidate's:

| W | span | return | Sharpe (ann.) | MaxDD | bars |
|---|---|---:|---:|---:|---:|
| 1 | 2024-05-07 … 2024-08-14 | −14.59% | −0.5025 | −32.78% | 100 |
| 2 | 2024-08-15 … 2024-11-22 | +78.85% | +4.0192 | −20.19% | 100 |
| 3 | 2024-11-23 … 2025-03-02 | −9.70% | −0.0565 | −37.90% | 100 |
| 4 | 2025-03-03 … 2025-06-10 | −8.82% | −0.0706 | −26.93% | 100 |

**Positive in 1 of 4 OOS windows.** The do-nothing alternative is not a smooth ride: it loses money
in three of four walk-forward windows and its entire full-window result rests on 2023 and on W2.
`walk_forward()` was not called directly because it re-derives returns through `signal_to_returns()`,
which would charge a fresh entry cost at the start of every window; a buy-and-hold is already in
position and pays nothing there. The window boundaries are copied from it exactly.

**Monte Carlo tail.**

- **Harness trade-level gate (`validator.monte_carlo`, called for real): INSUFFICIENT — "fewer than
  30 trades".** This is structural, not a defect: buy-and-hold holds nine positions and closes none,
  so the trade log can never reach the 30-trade floor. It is reported rather than asserted so the
  unavailability is on the record.
- **Bar-level diagnostic** (explicitly labelled as such; same two resampling schemes, same 5 seeds,
  1000 sims, one extra round trip of portfolio notional spread across the bars): **GATE PASS**,
  per-seed p5 Sharpe [0.2672, 0.4088, 0.3338, 0.4480, 0.2536], spread 0.1944. Sharpe p5 +0.3628 /
  p50 +1.3198 / p95 +2.2531. Return p5 +7.93% / p50 +485.69%. MaxDD p50 −50.92%, p95 (worst tail)
  −67.83%, worst −84.33%.

The permuted-order MaxDD **must not** feed criterion 4 — that uses the realized TEST MaxDD (−23.22%),
per `validator.monte_carlo`'s own documented limit.

## 5. Funding — EXCLUDED, and the exclusion is forced

The project holds `user_data/data/okx/futures/<PAIR>-1h-funding_rate.feather` for all nine
instruments. **Every one covers only 2026-02-26 … 2026-05-28** (266–273 eight-hourly settlements) —
a ~91-day window lying entirely *after* the benchmark window's end (2025-09-19) and after the
reserved-holdout boundary. **There is zero overlap with the window being measured.** OKX's public
funding endpoint is retention-limited (~97 days, measured in T-031), so the missing history cannot be
recovered from the venue; acquiring it is an `A-XXX` data task and A-005 may not touch
`user_data/data/`.

Magnitude, measured on the only window the project holds:

| | BTC | ETH | SOL | BNB | XRP | ADA | AVAX | DOT | LINK |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| annualised | +1.47% | +2.42% | −0.43% | +3.29% | +1.90% | +1.94% | +2.16% | −9.27% | +3.01% |
| share positive | 60.8% | 64.3% | 49.6% | 68.2% | 61.1% | 66.7% | 66.7% | 55.1% | 69.4% |

Equal-weight: **+0.720%/yr paid by longs.** Excluding funding therefore **overstates** the
benchmark's return by roughly that order, which makes the promotion bar **harder**, not easier. The
bias is conservative with respect to promotion: a candidate beating this benchmark would also beat a
funding-charged one.

## 6. Survivorship — present, unremoved, stated

The nine instruments are `config_perp.json`'s whitelist, selected in 2026 for having complete cached
history. A basket chosen in 2026 and backtested from 2022 never holds the perps that delisted or went
illiquid in between. Removing this needs a point-in-time OKX listing history the project does not
hold. **Direction: upward** — like the funding exclusion it makes the benchmark harder to beat.

## 7. Mandatory verification — the >100% CAGR defect presumption

The manual presumes any >100% CAGR **defective** until four checks are stated. Triggered on **train
(+141.62%)** and **test (+221.94%)**.

1. **Costs applied** — VERIFIED. Resolved from `COST_MODEL` via `per_side_cost("taker")` = 9.0 bps;
   bar 0's net return equals exactly −9.0 bps. Nothing hardcoded, no default inherited.
2. **Signal lag** — NOT APPLICABLE, and that is the point: there is no signal. Position is the
   constant 1 from bar 0, returns are close-to-close. No bar uses information from a later bar.
3. **Indicator warmup** — NOT APPLICABLE; no indicators, no state to warm up. Splits are pure slices
   of one continuous series.
4. **Survivorship** — PRESENT AND NOT REMOVED (§6). Upward bias.

**Conclusion**: the high CAGRs are not a cost, lag or warmup defect. They are (a) the 2023–2025
crypto bull on an unhedged long basket, (b) short-window annualisation — the +221.94% TEST CAGR
annualises a 151-bar +62.21% move and must not be read as a sustainable rate — and (c) a real,
unremoved upward survivorship bias.

**Independent construction check.** An equal-weight buy-and-hold that is never rebalanced must end at
the arithmetic mean of the instruments' wealth relatives:
`equity(T) = mean_i(close_i(T)/close_i(0)) × (1 − entry_cost)`. That identity is derived from the
definition of buy-and-hold, not from the implementation, so it is a genuine cross-check rather than
the code grading itself. Closed form **6.043410410539**, constructed **6.043410410539**, abs error
**1.155e-14**. The script **raises** on mismatch, so this cannot silently regress.

## 8. Artifacts

| File | What it is |
|---|---|
| `user_data/research/perps_benchmark.py` | the script; reproduces everything below from committed data |
| `research/benchmarks/perps_benchmark_TEST_returns.csv` | **the criterion-3 input** — 151 date-indexed TEST bars, `ret_gross`/`ret_net`/`equity` |
| `research/benchmarks/perps_benchmark_FULL_returns.csv` | full-window series, 1002 bars |
| `research/benchmarks/perps_benchmark.json` | complete machine-readable record incl. cost snapshot, funding, DSR, MC, WF |
| `research/benchmarks/perps_benchmark_run_output.txt` | the run's stdout, verbatim |

Both CSVs carry the **split dates, window, holdout boundary, instrument list and cost model as `#`
header lines inside the file**, per A-005's requirement that the series carry the split dates it was
computed on. A series whose window must be looked up elsewhere is one that can be silently compared
against the wrong window. Read with `pd.read_csv(fp, comment="#", index_col=0, parse_dates=True)`.

`python scripts/data_manifest.py verify` → `OK: 52 files match the manifest (built
2026-07-29T07:58:59Z)`. The check also runs at import time inside `validator.py`, before any number
is computed.

## 9. Warnings that must accompany these numbers

- **DSR WARNING — `trial_var_source='estimator_proxy'`**: the perps trial ledger holds 0 rows (10
  required), so the hurdle falls back to the Lo (2002) estimator proxy, which is not comparable
  across trade frequencies. **For this benchmark specifically the warning has no numerical effect**:
  `trial_sharpe_var` enters only through `sr0`, and `sr0 = 0` at `n_trials = 1`. It will matter for
  candidates and is reproduced here in full because the harness emits it.
- **COST MODEL NOTE**: slippage (3.0 bps/side) and spread (2.0 bps) are estimates, not calibrated
  against realized fills. Fee rates are published OKX regular-tier rates for `okx_usdt_perp` as of
  2026-07-28.

## 10. Bookkeeping

- **Perps `n_trials` stays 0.** The benchmark is pre-registered and never searched over; it is priced
  at `n_trials = 1` by construction. It was **deliberately not appended to
  `research/trial_sharpe_ledger.csv`** — that ledger records the cross-trial variance of *searched*
  trials, and inserting a never-searched construct would corrupt exactly the statistic it exists to
  supply.
- Meta-review cycle counter unchanged.
- `research/research_metrics.md`: perps OPS cycle count 0 → 1.
- `research/research_index.md` standing constraints: benchmark headline recorded; the stale
  "Holdout: all bars after 2026-05-27" line corrected to the manual's resolved perps boundary
  (2025-09-19). The manual is primary and the index is a secondary copy, so the index was the defect.
  `research/review_briefs/T-037_PERPS_TRANSITION_brief.md` line 41 carries the same superseded date;
  it is a historical verdict record and was **not** edited — flagged here instead.

## 11. Explicit non-goals, honoured

- No strategy designed, tested, or implied. This measures the do-nothing alternative.
- The benchmark was not tuned. The specification was executed as written; the only judgements it
  left open (window start, split triple) are documented above with their reasoning, made **before**
  any candidate exists, and frozen with a self-check.
- `validator.py` unmodified. `user_data/data/` untouched. No research task assigned.
