# T-034 Review Brief — Independent Reviewer

**Task:** T-034 (revised) / H-LogisticEntry (per-asset logistic regression direction classifier,
pre-registered zero-cost pre-gates, would-have-been DSR trial #101)
**Engineer verdict:** REJECTED (Step 2 zero-cost pre-gate — in-sample fit sanity)
**Reviewer verdict:** **REJECT CONFIRMED.** Every headline number independently reproduced; code
reviewed for lookahead bias and spec compliance with no defects found; budget and bookkeeping
compliant; underlying data feathers verified untampered.
**n_trials:** 100 (unchanged, zero DSR trials spent — confirmed in `research_metrics.md` header).

---

## 1. Verdict and decisive reasons

The Engineer's REJECT verdict is upheld on independent audit with no material findings against it.

- **Recomputation.** Reran `user_data/research/phase_logistic.py` unmodified (`py -3.13`,
  sklearn 1.9.0). Output matched the report exactly: BTC first-window (2018-01-22→2019-06-30,
  n=525) hit-ratio 0.5314, binomial p=1.6247e-01 (FAIL, threshold p<0.05); ETH first-window
  (2019-12-12→2021-04-30, n=506) hit-ratio 0.5672, p=2.8600e-03 (PASS); all 5 sampled ETH
  leakage checkpoints (train-max/test-min date pairs, 2021-2025) reproduced exactly, with
  train-max strictly preceding test-min in every case.
- **No lookahead bias.** Feature construction (`log_ret.shift(lag)`) uses only strictly-past
  information relative to each row's date; the target (`log_ret.shift(-1) > 0`) is a next-period
  label used only for supervised training, never as a feature. The expanding-window train/test
  split (`year_month < month`) is a clean walk-forward scheme with no boundary contamination.
- **No undisclosed hyperparameter tuning.** Reran both fits with sklearn's `ConvergenceWarning`
  promoted to a raised exception — neither model raised it, confirming default-regularization
  `LogisticRegression()` converged cleanly as specified, with no adjustment needed or made.
- **Full spec adherence.** Exactly the 5 pre-registered lagged-log-return features (lags 1/2/3/5/10),
  computed per-asset with no cross-asset leakage; exactly 1 new file created
  (`phase_logistic.py`, ≤2 allowed); zero DSR trials spent (correct, since the pre-gate failed);
  the standalone strategy file, full backtest, walk-forward, Monte Carlo, and DSR steps (3-7) were
  correctly never run, since the falsification statement requires stopping at the first failure.
  No silent deviation from `NEXT_TASK.md` found anywhere in the implementation.
- **Bookkeeping boundary respected.** The Engineer updated `research_metrics.md` and
  `strategy_iteration_log.md` as required, and correctly left `research_index.md` and
  `hypothesis_bank.md` untouched (Reviewer-only bookkeeping per deliverable 5) — confirmed by
  `git diff` showing no T-034 content in either file prior to this review.
- **Data integrity.** Given this project's history of data-fabrication incidents (T-019, T-023,
  T-025), the working-copy `BTC_USDT-1d.feather`/`ETH_USDT-1d.feather` (3111/2422 rows, through
  2026-07-18) were diffed against the last committed versions (3057/2422→2422 rows through
  2026-05-25): zero non-1-day gaps in either file, and zero differing `close` values across all
  overlapping historical dates — the working copy strictly appends new rows. No tampering found.

## 2. Audit findings worth remembering

- **A joint two-asset pre-gate (`btc_pass AND eth_pass`) was used to decide whether to proceed,
  and this is the reading the Reviewer endorses as conservative-but-defensible, not a spec
  violation.** `NEXT_TASK.md`'s falsification Step 2 is phrased in the singular ("the model")
  despite two independent per-asset models being in scope. The Engineer's script requires both to
  clear the in-sample bar before any walk-forward backtest runs. Under this Reviewer's standing
  default-to-conservative mandate, this is the correct call given genuine textual ambiguity — but
  it is worth flagging explicitly for future assignment-writing: **a multi-asset joint hypothesis
  should state up front whether a single-leg pass is meant to be investigated on its own or is
  intentionally foreclosed by the joint gate**, rather than leaving that implicit in an `and`.
- **ETH's own model showed genuine in-sample statistical significance** (56.7% hit-ratio,
  p=0.0029) and was never carried into a walk-forward backtest, purely because of the joint-gate
  design above. This is a factual observation about what was and wasn't tested — not a basis to
  overturn the REJECT verdict, and not a recommendation to test it further (that is the Director's
  call).
- **This is the cleanest-executing cycle in recent memory.** Unlike the last several
  instrument/infrastructure cycles (T-025, T-026, T-031, T-032 all surfaced report-vs-reality gaps
  requiring Reviewer correction), this pre-registered statistical pre-gate cycle reproduced
  exactly on rerun with no corrections needed — consistent with the pattern noted in
  `strategy_research_notes.md` that this project's false-claim incidents (Cluster E,
  Meta-Review #1) have so far clustered in instrument/infrastructure cycles with prose claims
  about external/live state, not in self-contained statistical trial/pre-gate scripts.
- **Environment blocker handling was correct.** The prior sub-cycle (Iteration 37) correctly
  refused to hand-roll a logistic regression substitute when `scikit-learn` was missing, and
  correctly filed it as an environment blocker rather than silently substituting a different
  implementation — consistent with the manual's standard-tooling-for-reproducibility principle.

## 3. Engineer's "Recommendations to the Director" (carried forward verbatim)

> The failure of simple lagged returns to provide an in-sample edge for logistic regression
> supports the previous conclusion that OHLCV signal-prediction constructs are generally closed.
> I recommend against further tests of statistical learning models (e.g. Random Forests, AdaBoost,
> DNNs) unless they incorporate genuinely new, orthogonal features (non-OHLCV) or a non-linear
> mechanism that explicitly handles regime shifts.
>
> The project should continue to rely on regime-avoidance and vol-target sizing, as predictive
> edges remain elusive.

The Reviewer notes the first paragraph goes further than this single cycle's evidence supports:
one linear model, five features, two assets is a narrow test, and `hypothesis_bank.md`'s own
correction ledger (written this same cycle, prior to this trial) explicitly flagged that
generalizing a single test's negative result into a blanket family closure was exactly the
overclaiming pattern that prompted this task's assignment in the first place. The Director should
weigh this recommendation with that caution in mind rather than adopting it as a closure.

## 4. Observations from the data / open questions

- BTC's in-sample hit-ratio (53.1%) is directionally above chance but not significant at n=525;
  ETH's (56.7%) is both higher and significant at a similar sample size (n=506) on the same
  feature set and model class, applied to a different asset. This asset-level asymmetry (also
  seen elsewhere in this project, e.g. DVOL/COT findings differing by mechanism, not by asset) is
  a recurring pattern worth the Director's attention: BTC and ETH do not always respond
  identically to the same construction on this dataset.
- The pre-gate's zero-cost design worked exactly as intended — it stopped a doomed(-by-design)
  joint hypothesis before any of the 5 subsequent validation stages (full backtest, TEST-split,
  walk-forward, Monte Carlo, DSR) consumed time or trial budget, consistent with 8 prior pre-gate
  stops in this project's history (EWMA, BearShort, CointPair, SizingBand, IVGate, IVSizing,
  ERScale, ADXGate).
- No walk-forward monthly-refit predictions were ever actually generated (the script only fits
  once, at the first window, then exits or logs date boundaries for the leakage check) — this is
  appropriate given the design (steps 3+ were never reached), not a defect, but a future cycle
  that *does* clear this pre-gate will need to verify the refit-cadence logic actually refits
  monthly during the full backtest, since this script never exercised that code path.

## 5. What this verdict implies for adjacent ideas

- **The statistical/ML family (hypothesis_bank.md Section 8) has its first tested member, with a
  negative result, but is not closed.** DNN and AdaBoost — both flagged in the same section as
  having documented large train/test overfitting gaps in their own source material — remain
  untested and are a mechanistically different (nonlinear/ensemble) approach; this cycle's result
  does not extend to them by inference, per the same overclaiming caution the Director's own
  cycle-#16 self-audit raised about the prior blanket-closure error.
- **The project's "no signal-prediction edge survives OOS" finding now has one data point
  extending it to fitted models, at the in-sample stage** — BTC's model failed before OOS
  collapse was even possible, suggesting (not proving) the ~1.2-1.3 Sharpe ceiling reflects a
  property of this data's linear predictability rather than being an artifact of only testing
  rule-based constructions. This is weak evidence (one model class) and should not be
  over-generalized.
- **The Crypto Fear & Greed hypothesis remains DEFERRED**, unaffected by this cycle's outcome —
  it is a different data axis (sentiment, not OHLCV-derived) and was not touched this cycle.

## 6. Bookkeeping performed by this review

- `research/strategy_iteration_log.md`: Independent Reviewer audit block appended under the
  existing Iteration 38 heading (no renumbering needed).
- `research/research_metrics.md`: Reviewer update header added above the Engineer's self-reported
  entry (same pattern as prior Reviewer corrections); new row added to the Common
  Indicator/Technique Usage table for logistic regression.
- `research/research_index.md`: new row #36 added to the hypotheses-tested table; new item #26
  added to "Lessons from empirical testing"; cycles-since-meta-review counter advanced to 15 of 25
  (not due).
- `knowledge_base/hypothesis_bank.md`: Linear/Logistic Regression Direction Entry card status
  updated from ASSIGNED to TESTED — REJECTED, with full verdict detail and citations.
- `research/strategy_research_notes.md`: three durable process lessons added (statistical/ML
  ceiling generalization is weak-but-real evidence; joint multi-asset pre-gates can shelve a
  significant single-leg result by design; pre-registered self-contained pre-gate scripts continue
  to reconcile exactly on rerun, unlike instrument/infrastructure cycles).
- **Meta-review check:** cycle counter is 15 of 25 since meta-review #1 — not due (threshold 25).
