# T-029 / H-ERScale — Independent Reviewer Brief

**Verdict: REJECT — valid pre-gate stop at F-P2 (episode dispersion). Zero trials spent; n_trials = 100.**
**Champion `TrendVolTarget` stands unchanged. Regime-classifier-overlay family stays OPEN** (binding
per NEXT_TASK §4.3: F-P1/F-P2 stops do not close the family).

Reviewer: fresh-context session, 2026-07-19. Graded against `research/NEXT_TASK.md` (T-029) and
`research/results/T-029_report.md`; independently verified by full end-to-end rerun of
`user_data/research/phase24_erscale.py` (Python 3.13, `PYTHONIOENCODING=utf-8`).

---

## 1. Verdict and decisive reasons

- **F-P2 triggered exactly as pre-registered.** Materially-affected TEST-split days span 5 distinct
  calendar months (passes the ≥3 clause), but the last materially-affected day is **2025-10-09** and
  **230 of 351 TEST days (65.5%) postdate it** — over the 50% limit. The mechanism sat inert for
  two-thirds of the held-out window. Stop honored; `sys.exit` fires before Steps 5–7; trial #101
  never constructed.
- **F-P0 and F-P1 passed first, so the stop is meaningful.** Replication landed *identically* on the
  T-028 Reviewer baseline (FULL Sharpe 1.154 / TEST 0.391 / MC tail 33.6%). F-P1: 187
  materially-affected days = 19.1% of in-market days (vs 5% floor), 39 in TEST (vs 20 floor), across
  62 episodes, mean |Δw| 0.248 / max 0.727 — the multiplier is *not* swallowed by the quantizer.
  The T-015/T-019-style inertness failure did not recur; the mechanism fired and was still unusable.
- **Every reported number reproduced exactly on Reviewer rerun** — replication triple, ER summary
  stats, m_t distribution, correlations, harm census, F-P1 counts, F-P2 counts. No discrepancies.

## 2. Audit findings worth remembering

- **Integrity CLEAN — fifth consecutive clean cycle.** Research feathers at the frozen 2026-06-10
  baseline; forward-lane feathers at exactly the T-027 refresh timestamp (2026-07-19 11:59), not
  touched during this cycle; all protected files (`best_strategy_so_far.py`, `TrendVolTarget.py`,
  `validator.py`, `freqtrade_dsr.py`, `dryrun_monitor.py`) predate the cycle. No `dryrun.log`
  interference. Budget: 0 optimization runs, 0 trials, no undisclosed variants, no stray results
  files.
- **Spec inconsistency, resolved correctly and disclosed.** The §7.2 rank definition ("rank of ER_t
  within ER₁..ER_{t−1}, **then .shift(1)**") carried over T-028's phrasing, where `.shift(1)`
  applies to the expanding-quantile *threshold* series — equivalent to ranking ER_t against
  strictly-past values. A literal extra shift on the rank would have lagged the day-set one bar and
  broken the binding "day-set inherited verbatim" requirement. The Engineer implemented the
  day-set-preserving reading and disclosed it (report §2). **Empirically proven correct:** the 2d
  harm census matches T-028 *exactly* (affected n=271, median −0.49%, mean −0.36%; unconditional
  n=936, +0.77%/+1.49%), and ρ(ER30,rv30) reproduces at +0.0709/+0.0694 (spec tolerance ±0.03).
  Directors should note: locked-constant blocks copied between cycles can carry construction-specific
  phrasing that becomes self-contradictory in the new context.
- **Engineer behaviour this cycle: honest and compliant.** Unlike T-028, the mandatory report was
  written, bookkeeping was done conservatively (n_trials left at 100; index/log/bank entries phrase
  the verdict as a stop, family explicitly kept open; no self-declared ACCEPTED). The full remaining
  gate-stack code (Steps 5–7) sits unreached in the script — correct structure.
- **Report deficiencies (non-fatal):** Step 2a/2b/2c diagnostic values and Step 3's mean/max |Δw|
  are required to be *reported* but appear only in script output, not in `T-029_report.md`
  (all verified by rerun). §5's "fee-loaded candidate reached F-P1" is imprecise — F-P1/F-P2 are
  weight-based and fee-independent. `test_sh.py` (a champion-only TEST-start-date diagnostic) was
  left at repo root instead of a scratch area.
- **Split convention documented:** the 70/15/15 split is computed on the raw union window (2,339
  rows from 2020-01-01), giving TEST = 2025-06-11 → 2026-05-27 (351 days), with returns evaluated on
  the common window from 2020-10-01. This is inherited from T-028 (its 351-day TEST and the
  Director's own calibration numbers presuppose it) — consistent, but it is *not* literally
  "the full common history" as §7.1 words it. Worth normalizing in future assignment text.
- **Pre-existing index defect fixed by this Reviewer:** `research_index.md`'s standing-constraints
  line still said n_trials=99 (stale from T-024); corrected to 100 to match authoritative
  `research_metrics.md`. Index banner also compacted per meta-review directive #3.

## 3. Engineer's "Recommendations to the Director" (carried forward verbatim in substance)

1. ER never breached its causal expanding 33.33rd percentile after October 2025 — either 2025–26 is
   historically "efficient" relative to 2020–24, or the expanding threshold is too slow to adapt to
   structural regime shifts.
2. The regime-classifier family is still open. Since ER's failure was threshold staleness rather
   than signal invalidity, consider (a) a **rolling window** for the percentile rank instead of the
   expanding window, or (b) **ADX/MESA**, which might be more adaptive.
3. n_trials is still exactly 100.

*(Reviewer note on #2, fact not recommendation: a rolling-rank variant introduces a lookback
parameter — a fitting degree of freedom the expanding construction was explicitly chosen to avoid,
and both prior ER cycles claimed zero fitted parameters as a virtue. Any such assignment would need
to confront that trade-off in its pre-registration.)*

## 4. Observations from the data

- **The concentration pathology is upstream of the action.** Changing the action from step to ramp
  moved the last-affected TEST day by only two days (2025-10-11 → 2025-10-09) and the postdating
  fraction not at all (65% → 65.5%). Whatever the action, the signal defines *when* anything can
  happen, and this signal's bottom tercile has been empty since Oct-2025.
- **The ramp fired broadly in-sample:** 187 affected days over 62 episodes full-window (vs the
  binary veto's behaviour), 22.6%/23.1% of in-market days at m_t<1.0 (BTC/ETH), median sub-1.0
  multiplier ≈0.42/0.47. Turnover *fell* slightly (72.25 → 72.08). The mechanism is well-behaved;
  the evaluation window is what starves it.
- **ER–rv30 correlation is regime-dependent:** full-window +0.071/+0.069 (BTC/ETH) but **+0.317 /
  +0.151 in the TEST split**. Still far below the 0.7 alarm, but the orthogonality claim is
  materially weaker in the recent regime — worth knowing if the family is ever revisited.
- **r_t at TEST start was 0.360 (BTC) / 0.425 (ETH)** — just above the tercile boundary. The TEST
  period began near the activation edge and then drifted away from it.

## 5. What this verdict implies for adjacent ideas

- **The regime-classifier-overlay family (ADX, MESA/Hilbert, HMM cards) remains OPEN** — the
  pre-declared closure conditions (F-P3/F-P4/F-T) never evaluated. However, both ER cycles now show
  the *harvestability* constraint concretely: any overlay driven by a slow noise/trend classifier
  with a distribution-relative threshold faces the same risk that its firing set is concentrated in
  one macro-episode of the TEST window. F-P1+F-P2-style day-set censuses are cheap, pre-trial, and
  now twice-proven — any successor in this family should expect them as pre-gates.
- **The expanding-vs-rolling threshold question is now a documented open question**, not a free fix
  (see §3 note). It applies equally to any future distribution-relative rule, not just ER.
- **The T-028 durable findings stand unchanged:** the low-ER chop signal is real (harm census
  re-replicated exactly here) and orthogonal-to-volatility at full-window scale. Nothing in T-029
  contradicts them; T-029 adds that neither tested action shape can reach the signal in the current
  regime.
- **TEST-split episode-hostage risk (meta-review §7 doubt) recurred for the third time** (H-IVGate,
  T-028, T-029): verdicts on this dataset's held-out window keep being decided by whether a
  mechanism touches the mid-2025→Oct-2025 stretch. This is a property of the frozen evaluation
  window itself; forward evidence (the dry-run lane) is the only axis that dilutes it.

## 6. Bookkeeping performed by this Reviewer

- `strategy_iteration_log.md`: Reviewer audit appended under Iteration 31 (T-029).
- `research_index.md`: banner compacted (duplicate fabrication banners merged into an integrity
  ledger; orphaned fragment removed); row #31 tightened and marked Reviewer-verified;
  standing-constraints n_trials corrected 99 → 100.
- `research_metrics.md`: header updated for T-029 (n_trials unchanged at 100).
- `strategy_research_notes.md`: four durable lessons appended (signal-vs-action concentration;
  expanding-threshold staleness; autopsy-to-pre-gate pipeline win; spec-conflict resolution pattern).
- `knowledge_base/hypothesis_bank.md`: verified — Engineer's update is accurate (ER card TESTED /
  REJECTED at F-P2, family explicitly NOT closed); no change needed.
- Meta-review counter: 9 of 25 — not due.
