# NEXT TASK — Research Assignment

> **Single active assignment.** Written by the Research Director, cycle #9 since meta-review #1,
> 2026-07-19. The Research Engineer executing this has no prior context: everything needed is in
> this file. Do not infer steps that are not written here.

**Task ID:** T-029
**Codename:** H-ERScale
**Type:** Hypothesis cycle (may spend at most one DSR trial, #101)
**n_trials at start of cycle:** **100** (`research/research_metrics.md` is authoritative)

---

## 1. Objective

Determine whether the Efficiency-Ratio chop signal — already proven real, orthogonal to volatility,
and abundantly harvestable by T-028 — can be converted into durable held-out performance when its
**action** is changed from an all-or-nothing veto to a continuous, proportional exposure ramp.

---

## 2. Hypothesis

Replacing T-028's binary ER veto with a continuous multiplier on the champion's final position
weight — full exposure when 30-day Efficiency Ratio sits at or above its causal expanding bottom
tercile, ramping linearly to zero as ER approaches the bottom of its own historical distribution —
improves the champion's risk profile on held-out data without the single-episode fragility that
rejected the binary form.

**This cycle changes exactly one variable versus T-028: the action shape.** The signal, the lookback,
the threshold fraction, the causal-threshold construction, and the affected day-set are identical and
are inherited verbatim, not re-fitted. Any change to the signal side is an automatic rejection of the
cycle, because it would confound the one variable under test.

---

## 3. Falsification statement

This hypothesis is rejected if **any** of the following triggers. Falsifiers F-P1 through F-P4 are
zero-trial pre-gates evaluated in order; the trial is constructed only if all four pass.

- **F-P0 (replication).** The replicated champion baseline falls outside its documented band
  (§7.3 Step 1). → STOP, report harness drift, spend no trial.
- **F-P1 (materiality).** After the continuous multiplier is applied to the champion's final
  quantized weight, fewer than **5.0%** of in-market days show `|final_w − champion_w| ≥ 0.05`,
  OR fewer than **20** such days fall inside the TEST split. → STOP. This means the mechanism is
  inert or statistically uninformative and the T-015/T-019 quantizer-swallow result has recurred.
- **F-P2 (episode dispersion).** The materially-affected TEST-split days fall in fewer than
  **3 distinct calendar months**, OR more than **50%** of TEST-split days postdate the last
  materially-affected day. → STOP. This is the pre-registered fix for the N≈1 macro-period
  pathology that sank H-IVGate (index row #21) and T-028 (row #30).
- **F-P3 (idealized upper bound).** Simulated with **zero** transaction cost and perfect execution —
  a mathematical ceiling no fee-loaded implementation can beat — the construction delivers an
  MC-tail improvement of **< 5.0pp**, OR degrades TEST Sharpe by **> 0.05** versus the replicated
  champion. → STOP.
- **F-P4 (single-episode robustness).** On that same idealized bound, recomputing TEST Sharpe with
  the single largest-contributing affected episode removed leaves candidate TEST Sharpe **below**
  the replicated champion's TEST Sharpe. → STOP. T-028 fails this decisively (0.617 → −0.096); it is
  promoted here from a post-hoc Reviewer probe to a pre-registered zero-cost gate.
- **F-T (trial).** The fee-loaded locked construction fails **any** of the eleven gates in §8.

If the cycle is rejected, the ER card's declared family implication in §4 takes effect.

---

## 4. Scientific rationale

### 4.1 The mechanism, and what T-028 established

The Kaufman Efficiency Ratio (`knowledge_base/07_market_regimes.md`; `13_indicator_reference.md`;
Kaufman Ch.17, Ch.30) measures directional efficiency: net displacement over a window divided by the
sum of absolute per-bar moves. It is scale-free and path-shape-based — a noise measure, not a
volatility-level measure.

T-028 (`research/review_briefs/T-028_brief.md`) tested this signal as a binary veto on the champion
and produced three durable, Reviewer-verified findings:

1. **The signal is real.** Low-ER in-market days have forward-10d median **−0.49%** / mean **−0.36%**
   (n=271) against an unconditional in-market baseline of **+0.77%** / **+1.49%** (n=936). The harm
   census (F-B) passed decisively.
2. **The signal is orthogonal to volatility.** ρ(ER30, rv30) = **+0.071** (BTC) / **+0.069** (ETH)
   full-window. This is far below the |ρ|>0.7 alarm and confirms the rejection is *not* another
   instance of the positive-carry-VRP result that killed T-022 and T-024.
3. **The action failed, not the signal.** Within the TEST split the binary veto avoided one −13.75%
   episode while suppressing three strongly positive ones (+9.13%, +5.18%, +2.30%). The Reviewer's
   summary is explicit: *"a binary, all-or-nothing veto driven by a slow noise measure cannot convert
   the chop signal into durable held-out performance... Any successor in this family inherits that
   constraint on its **action**, not on its **signal**."*

### 4.2 Why a continuous action is the correct next test, not a variation

The binary veto's failure has a specific structural cause. ER is a *slow* measure; a step function
applied to a slow measure produces late, total, and irreversible exposure changes. The observed
asymmetry — one large loss avoided, three large gains forgone — is the signature of an action that
cannot express partial conviction. A proportional ramp keeps exposure monotonically related to signal
strength: marginal chop produces a marginal de-risk rather than a full exit, so the cost of being
wrong about a mild reading is bounded by the reading's own magnitude.

This is Kaufman's own prescription for the same family: adaptive-trend systems (KAMA and the wider
Adaptive Trend-Speed family, `knowledge_base/hypothesis_bank.md` §1) use the Efficiency Ratio as a
**continuous smoothing-constant modulator**, never as a binary switch. T-028 tested the construction
Kaufman does not use; this cycle tests the one he does.

### 4.3 Why the outcome is informative either way

- **If it passes**, the program gains its first mechanism improvement since H-TailAlloc, from a signal
  whose reality is already independently established.
- **If it fails**, the regime-classifier-overlay family closes as a whole — the ER card plus the
  **ADX Trend/No-Trend**, **MESA/Hilbert Cycle-Presence** and **Hidden Markov Regime-Switching** cards
  in `knowledge_base/hypothesis_bank.md` §6. All four partition the same in-market days by the same
  underlying noise/trend property. With the signal proven real and orthogonal (T-028) and *both*
  action shapes failed (binary T-028, continuous T-029), the family's failure would be established at
  the level of harvestability rather than of any particular classifier, and swapping ADX or MESA in
  for ER would be a re-parameterization, not a new test.

**Declared family implication (binding):** an F-T or F-P3/F-P4 rejection of this cycle CLOSES the
regime-classifier-overlay family. An F-P1 or F-P2 stop does **not** close it — those indicate the
*mechanism was never given a fair test*, and the family stays open.

### 4.4 A permanent pipeline improvement, independent of the verdict

Single-episode dependence has now sunk two candidates through unrelated mechanisms (H-IVGate at B3a,
T-028 at Gate 7), each time discovered only by a post-hoc Reviewer probe. The T-028 Reviewer proposed
a standing check and left adoption to the Director. **It is adopted here**, as F-P2 and F-P4, and
promoted to pre-registered zero-cost pre-gates. Even a rejected cycle therefore leaves the validation
pipeline permanently stronger.

---

## 5. Expected market regime(s)

**Should work:** choppy, low-efficiency sideways regimes where the champion's trend gate remains
nominally True but price makes no net progress — specifically the 2024-04→10 chop and the 2025 range,
which `research/current_champion.md` limitations #4 and #7 identify as the champion's weakest stretches.

**Should fail:** sustained high-efficiency trends (2020-21, 2023 legs), where the multiplier should sit
at exactly 1.0 and the candidate should be numerically identical to the champion — verify this. It
should also underperform in sharp V-shaped reversals, where ER is mechanically low at the bottom and the
ramp will hold reduced exposure into the recovery. **This is the known structural risk of the
hypothesis and must be reported explicitly**, not discovered by the Reviewer.

**Where the binary form specifically failed and this one might not:** shallow, brief efficiency dips
inside an intact trend. The veto exited entirely; the ramp should trim only slightly.

---

## 6. Prior-work check

| Task ID | Relationship | How this escapes its failure mode |
|---|---|---|
| **T-028 / H-EffRatio** (row #30) | Direct predecessor; same signal | T-028 failed Gate 7 (cliff) and on single-episode dependence, both properties of the *binary* action. The continuous ramp has no threshold cell to sit on a cliff — exposure is a continuous function of the signal — and F-P4 tests episode-dependence *before* a trial is spent rather than after. |
| **H-IVGate** (row #21) | Same N≈1 pathology, different signal | F-P2 pre-registers the dispersion requirement that B3a discovered only after the fact. |
| **H-RangeVol** (row #15) | Sizing-input precision discarded by the 25% quantizer | The multiplier is applied **after** quantization and is itself **not** re-quantized (§7.2), so it cannot be swallowed. F-P1 tests this empirically at zero cost rather than assuming it. |
| **H-SizingBand** (row #19) | Sleeve sizing layer CLOSED at its efficient frontier | **This is not a sizing-layer task.** Rows #15/#19 closed the *volatility* sizing input — estimator quality and rebalance granularity of the rv30-driven vol-target. This cycle leaves the entire vol-target layer byte-identical and applies a multiplier driven by a **different, measured-orthogonal input** (ρ(ER30,rv30) = +0.07). The Engineer must not modify the vol-target layer in any way. |
| **T-022 / T-024** (rows #24, #26) | Killed by positive-carry VRP | T-028 measured ρ(ER,rv30) ≈ +0.07 directly. ER is not a volatility proxy; that failure mode does not apply. §7.3 Step 2c re-verifies this rather than assuming it. |

**Engineer recommendations from the last brief:** none exist. The T-028 Engineer wrote no
`T-029`-facing recommendations because **`research/results/T-028_report.md` was never written**
(brief §3). Nothing has been filtered out; there was nothing to carry forward. Note for this cycle:
the report is Deliverable 1 and is not optional.

**Reviewer observation adopted:** the standing single-episode check proposed in brief §5 — adopted in
full as F-P2 and F-P4 (§3), and as Gate 11 (§8).

**Reviewer observation rejected as stated:** brief §4's data-staleness flag ("feathers end 2026-05-27,
seven weeks stale, despite T-027 appending fresh bars"). The Director verified this directly: it
conflates two distinct datasets. See §12.

---

## 7. Constraints and exact procedure

### 7.0 Hard constraints

- **Dry-run only.** Never place live orders. Never modify any `config*.json` `dry_run` field.
- **Do NOT modify** `research/best_strategy_so_far.py`, `user_data/strategies/TrendVolTarget.py`,
  `user_data/research/validator.py`, or `freqtrade_dsr.py`. Read them; do not edit them.
- **Do NOT touch the forward-evidence lane.** Specifically: do not run, edit, or import
  `user_data/research/dryrun_monitor.py`; do not write to `user_data/research/DRYRUN_LOG.md` or
  `user_data/logs/dryrun.log`; do not stop or restart the dry-run bot; do not modify, append to, or
  regenerate **any** file under `user_data/data/okx/`. That lane is accruing evidence in parallel,
  was restored at real cost in T-027, and is **not displaceable**.
- **ABSOLUTE PROHIBITION ON SYNTHETIC DATA.** Three cycles in this project were ruled invalid for
  fabricating candles (T-019, T-023, T-025). Do not create, clone, extrapolate, interpolate, or
  "top up" any price bar under any circumstance or justification. `mock_data.py` is quarantined and
  must stay quarantined. If data you need is missing or stale, **stop and report it as a blocker** —
  an honestly reported blocker is a fully acceptable outcome of this cycle; a fabricated bar is a
  rejected cycle. The Reviewer will verify feather mtimes and SHA-256 against the pre-cycle baseline.
- **This task requires no network access and no data download.** It reads cached feathers read-only.
- **Pre-registration.** Before running anything that produces a number, write §7.2's locked constants
  verbatim into the header of `user_data/research/phase24_erscale.py` and into
  `user_data/research/SESSION_2026-07-19_ERSCALE.md` §1. Constants may not change afterwards.
- **No optimization.** No hyperopt. No grid search over ER lookback, breakpoint fraction, or ramp
  shape. There is exactly one construction (§7.2) and it has **zero fitted free parameters**.
  Searching for a better ramp is an automatic rejection of the cycle.
- **Do not update bookkeeping optimistically.** Per the T-028 Engineer-behaviour note: write index,
  iteration-log and metrics entries only after the report exists, and phrase them conservatively.
  Never self-declare ACCEPTED — the verdict is the Reviewer's.

### 7.1 Data and evaluation window

- **Pairs:** `BTC/USDT:USDT` and `ETH/USDT:USDT`, timeframe `1d`.
- **Files:** `user_data/data/okx/futures/BTC_USDT_USDT-1d-futures.feather` and
  `.../ETH_USDT_USDT-1d-futures.feather`. Load read-only, exactly as
  `user_data/research/phase22_ivsizing.py::load_fut` does.
- **Window:** the full common history of the two feathers. Report the exact first and last dates.
  (Expected last date **2026-05-27**; see §12 — this is correct and intended, not staleness.)
- **Split:** chronological 70/15/15 by row count, identical to the project convention —
  `train_end = int(n*0.70)`, `val_end = int(n*0.85)`, TEST = the final 15%. Report the TEST split's
  start and end dates explicitly.
- **Execution model:** fee = **0.0015** (0.15% per side) applied to `|Δ position|`; 2-bar lag
  (`pos = W.shift(2)`); annualization 365. Copy `net_from_weights` from `phase22_ivsizing.py`
  verbatim.

### 7.2 LOCKED construction — zero fitted parameters

```
ER lookback         : n = 30 bars            (inherited verbatim from T-028; introduces NO
                                              new parameter)
ER definition       : ER_t = |C_t - C_{t-30}| / sum_{i=t-29..t} |C_i - C_{i-1}|
Rank                : r_t = causal EXPANDING percentile rank of ER_t within ER_1..ER_{t-1},
                      then .shift(1).  r_t in [0, 1].
                      Minimum history before the ramp may act: 365 observations.
                      Bars with insufficient history: m_t = 1.0 (multiplier INACTIVE).
Breakpoint          : b = 1/3            (inherited verbatim from T-028's bottom-tercile rule.
                                          FIXED A PRIORI. Do not tune it. It is not re-fitted
                                          here and this cycle claims no credit for choosing it.)
ACTION (the single
changed variable)   : m_t = min(1.0, r_t / b)
                      i.e.  r_t >= 1/3  ->  m_t = 1.0  (champion weight EXACTLY unchanged)
                            r_t <  1/3  ->  m_t ramps linearly 0.0 -> 1.0 across the
                                            bottom tercile
Application         : final_w_i(t) = champion_w_i(t) * m_t(i)
                      Applied AFTER the champion's 25% quantizer and AFTER the per-pair cap.
                      The result is NOT re-quantized.  (This is deliberate: rows #15/#19
                      showed the quantizer discards sizing precision; applying the multiplier
                      downstream is what keeps the mechanism from being swallowed. F-P1 tests
                      that this worked.)
Per-asset           : each pair uses its OWN close series for ER, rank and multiplier
Sizing layer        : UNTOUCHED. 40%/rv30, clip(0,1), 25% quantizer, /2 per-pair cap.
                      Do not modify it in any way.
Hysteresis / confirmation bars / smoothing of m_t / floors on m_t : FORBIDDEN
MC                  : 1,000 monthly-block-shuffle sims, seed 11
WF configs          : 3 / 4 / 5 / 6 windows via validator.wf_window_stability
DSR                 : n_trials = 101 (trial step only)
Forward-return horizon for the harm-census replication : 10 days, net, champion returns
"Materially affected day" (used throughout) : an in-market day where
                      |final_w_i(t) - champion_w_i(t)| >= 0.05 for at least one pair
"Affected episode"  : a maximal contiguous run of materially-affected days
```

Reference implementations to copy rather than reinvent — `user_data/research/phase22_ivsizing.py`:
`load_fut`, `core_series`, `rv30_series`, `scale_series_rv30`, `quantize_scale`,
`champion_weights`, `net_from_weights`, `perf`, `mc_tail`, `split_indices`.
`user_data/research/phase23_effratio.py` contains a correct causal ER implementation — reuse it.
**Note:** `phase23_effratio.py` crashes under the default cp1252 console on its box-drawing
characters. Run with `PYTHONIOENCODING=utf-8`, or use plain ASCII in your own script's output.

### 7.3 Step-by-step

**Step 1 — Replication (mandatory gate, F-P0).** Rebuild the champion baseline from
`champion_weights` + `net_from_weights` over the §7.1 window. Report FULL Sharpe, TEST Sharpe,
MaxDD, CAGR, MC tail P(MaxDD < −25%). **Assert** the baseline lands in the documented band:
FULL Sharpe in **[1.05, 1.35]**, TEST Sharpe in **[0.30, 0.50]**, MC tail in **[25%, 36%]**.
T-028's own replication produced FULL 1.154 / TEST 0.391 / MC tail 33.6% — you should land very
close to these. If any assertion fails, **STOP** and report harness drift. All later comparisons use
**your replicated values**, not the numbers quoted in this document.

**Step 2 — Diagnostics and T-028 replication (no gate, but all must be reported).**
- **2a** ER30 summary statistics per pair: min / p25 / median / p75 / max, and the level of `r_t` at
  the start of the TEST split.
- **2b** Distribution of `m_t` on in-market days: the fraction at exactly 1.0, and the min / p25 /
  median of the remainder.
- **2c** **Volatility-proxy check (required):** Pearson correlation between ER30 and rv30, per pair,
  full window and TEST split separately. Report all four numbers. T-028 measured +0.071 / +0.069
  full-window; if you do not reproduce these within ±0.03, something is wrong with your ER or rv30
  construction — stop and investigate before proceeding.
- **2d** **T-028 harm-census replication (integrity check).** For the bottom-tercile in-market days
  (`r_t < 1/3`), recompute the champion's forward-10d net return. T-028 reported median **−0.49%**,
  mean **−0.36%**, n=**271**, against an unconditional in-market baseline of **+0.77%** / **+1.49%**,
  n=**936**. Report your figures alongside these. Material disagreement (n off by more than 5%, or a
  sign flip on median or mean) means you are not on the same data or the same signal — **STOP** and
  report. Do not proceed to a trial on a signal you could not reproduce. This census is **not**
  re-gated — it already passed in T-028 — it is a replication check only.

**Step 3 — PRE-GATE 1 (materiality, F-P1).** Compute `final_w` per §7.2. Report: the count and
percentage of in-market days that are materially affected (full window), the same inside the TEST
split, the number of affected episodes, mean and max `|Δw|`, and the change in total turnover.
**STOP if F-P1 triggers** (< 5.0% of in-market days affected, OR < 20 materially-affected TEST-split
days).

**Step 4 — PRE-GATE 2 (episode dispersion, F-P2).** For the materially-affected TEST-split days,
report: the distinct calendar months they fall in, the date of the last affected day, and the number
and percentage of TEST-split days that postdate it. **STOP if F-P2 triggers** (< 3 distinct calendar
months, OR > 50% of TEST days postdate the last affected day). For calibration: T-028's binary veto
produced 50 TEST veto-days confined to 2025-06-12 → 2025-10-11, with **65%** of TEST days postdating
the last firing — it fails this gate. State explicitly in the report whether the continuous form
passes where the binary form failed.

**Step 5 — PRE-GATE 3 (idealized upper bound, F-P3).** Simulate the construction with **zero**
transaction cost and perfect execution — the mathematical ceiling no fee-loaded implementation can
beat. Report FULL Sharpe, TEST Sharpe, MaxDD, MC tail. **STOP if F-P3 triggers** (MC-tail
improvement < 5.0pp versus your replicated champion, OR TEST Sharpe degradation > 0.05). This is the
pre-gate class that killed H-SizingBand (#19) for zero cost; apply it honestly and do not soften the
bound in the candidate's favour.

**Step 6 — PRE-GATE 4 (single-episode robustness, F-P4).** On the Step 5 idealized bound, rank the
affected episodes by their contribution to the TEST-split Sharpe improvement. Report the full ranked
list with dates. Then recompute TEST Sharpe with the **single largest-contributing episode** disabled
(multiplier forced to 1.0 across those dates, nothing else changed). **STOP if F-P4 triggers**
(candidate TEST Sharpe with that episode removed < your replicated champion's TEST Sharpe). For
calibration: T-028 scores 0.617 with its single Oct-2025 episode and **−0.096** without it — it fails
this gate badly. Report your equivalent pair of numbers whatever the outcome.

**Step 7 — TRIAL #101 (only if Steps 1, 3, 4, 5 and 6 all pass).** Run the single locked, fee-loaded
construction through the full gate stack in §8. Recompute the **champion's own** DSR at
`n_trials=101` alongside the candidate's, so the comparison is like-for-like. Increment the counter
to **n_trials = 101** in `research/research_metrics.md` and in the `research_index.md` standing
constraints line. If any pre-gate stopped the cycle, **n_trials stays 100** and you must say so
explicitly in every deliverable.

---

## 8. Required validation (trial step only — every bar quoted in full)

Applies only if Step 7 is reached. All comparisons are against the **Step 1 replicated** champion.

| # | Gate | Pass threshold |
|---|---|---|
| 1 | **Held-out TEST Sharpe** | candidate TEST Sharpe **≥ replicated champion TEST Sharpe − 0.05** |
| 2 | **Full-window Sharpe** | candidate FULL Sharpe **≥ replicated champion FULL Sharpe − 0.05** |
| 3 | **Monte Carlo tail** | P(MaxDD < −25%) **≤ 20.0%**, from 1,000 monthly-block-shuffle sims at seed 11, AND an improvement of **≥ 5.0pp** versus the replicated champion |
| 4 | **Max drawdown** | candidate full-window MaxDD **≤ 25.0%** |
| 5 | **Walk-forward** | majority-positive OOS windows (**≥ 3 of 4**) at the 4-window config, AND majority-positive at **≥ 3 of the 4** configs {3, 4, 5, 6} via `validator.wf_window_stability` |
| 6 | **Deflated Sharpe Ratio** | computed with `freqtrade_dsr.py::deflated_sharpe_ratio` at **n_trials = 101**; candidate DSR **≥ champion DSR recomputed at the same n_trials = 101**. Report both. Separately state whether the absolute **≥ 0.95** proven-edge bar is met (it almost certainly is not — report it honestly either way) |
| 7 | **Parameter stability** | report candidate metrics across ER lookback **20 / 30 / 40** × breakpoint **b ∈ {0.25, 1/3, 0.40}** as a **reporting-only sensitivity surface**. This is NOT a search: the locked (30, 1/3) cell remains the candidate regardless of which cell scores best. **A cell adjacent to the locked cell scoring below the replicated champion's TEST Sharpe is a Gate 7 FAILURE** — this is exactly the cliff that rejected T-028 (adjacent cell 0.186 vs champion 0.391). Report the full 3×3 grid and the min/max spread |
| 8 | **Activity count** | report in-market days, materially-affected days, number of position changes, and turnover — full window and TEST split separately. Fewer than **20** materially-affected TEST-split days makes the TEST verdict statistically uninformative (F-P1 should already have caught this) |
| 9 | **Look-ahead audit** | state, line by line, that ER, `r_t` and rv30 use only information available at bar close, that `r_t` is computed on an expanding window of ER₁..ER_{t−1} and `.shift(1)`-lagged, and that positions are `.shift(2)`-lagged. Any leak = automatic rejection |
| 10 | **Regime breakdown** | per-calendar-year return, Sharpe, MaxDD and materially-affected-day count for champion vs candidate. Explicitly flag any year where the candidate's **return** is worse (T-028 was worse in 2024 and 2025 while showing a better TEST Sharpe) |
| 11 | **Single-episode robustness (fee-loaded)** | repeat Step 6's leave-one-episode-out computation on the **fee-loaded** candidate. Candidate TEST Sharpe with the largest-contributing episode removed must remain **≥ replicated champion TEST Sharpe**. Also report what fraction of TEST-split days postdate the last materially-affected day |

---

## 9. Promotion criteria

To replace the champion, the candidate must satisfy **all eleven** gates in §8, with every number
reproducible by a reviewer who runs `user_data/research/phase24_erscale.py` and reads nothing else.
In particular:

- **Gates 1, 2 and 3 are jointly necessary.** A tail improvement bought with TEST Sharpe is exactly
  the trade that rejected T-024; it will reject this too.
- **Gate 6 is necessary.** A candidate DSR below the champion's at the same `n_trials` means the
  construction has not paid for its own selection cost.
- **Gate 7 must show a plateau, not a peak** — and specifically no adjacent cell below the champion.
- **Gate 11 is necessary and is the point of this cycle.** A candidate whose held-out advantage rests
  on one episode is rejected regardless of how the other ten gates score.

Anything short of all eleven = the champion stands unchanged. A candidate that passes some gates and
fails others is a **REJECTED** verdict, not a partial promotion. If the candidate is rejected but the
pre-gate diagnostics produced a durable finding, record the finding — that is the cycle's real output.

If promoted, the champion changes at the *sleeve* level, which invalidates the 80/20 portfolio stance
in `strategy_portfolio.md`. **Do not attempt to re-derive the portfolio stance in this cycle** — flag
it for the Director as follow-on work.

---

## 10. Research budget (hard limits — may not be exceeded)

- **Strategy variants:** **2** total — (i) the idealized fee-free construction (Step 5), (ii) the
  locked fee-loaded construction (Step 7). No third variant.
- **Optimization runs:** **0**. No hyperopt, no grid search, no tuning of lookback, breakpoint, or
  ramp shape.
- **DSR trials:** **1** maximum (trial #101), and only if Steps 1 and 3–6 all pass. Pre-gates cost
  zero trials.
- **Sensitivity surface (§8 Gate 7):** reporting only, run **once**, after the verdict is fixed. It
  may not change the candidate. Running it earlier is permitted only if you can demonstrate it could
  not have influenced the locked construction; running it *instead of* locking first is a cycle
  violation.
- Exceeding any limit invalidates the cycle.

---

## 11. Deliverables

1. **`research/results/T-029_report.md`** — the standard 12-section report format (Task ID and
   hypothesis; implementation notes; lookahead/leakage checks; variants attempted; backtest results;
   walk-forward / OOS results; DSR and other statistics; verdict vs. falsification statement; regime
   behavior; lessons; raw output locations; recommendations to the Director). State the verdict
   against §3 by naming the specific falsifier (F-P0 / F-P1 / F-P2 / F-P3 / F-P4 / F-T) or
   "none triggered". **This deliverable is mandatory and was skipped in T-028 — do not skip it.**
   The "recommendations to the Director" section is how your ground-level observations reach the next
   cycle; write it even if the verdict is negative.
2. `user_data/research/phase24_erscale.py` — the analysis script, with §7.2's locked constants
   verbatim in the module docstring header. It must run end-to-end and reproduce every number in the
   report. Use ASCII-only output or set `PYTHONIOENCODING=utf-8`. If any result is produced by a
   second execution path (e.g. a `validator.py` harness call), that path must be named in the report —
   T-028 left a results JSON with unexplained provenance.
3. `user_data/research/SESSION_2026-07-19_ERSCALE.md` — session narrative; §1 must contain the
   pre-registration written *before* any numbers exist, and the file must carry a real narrative, not
   only the pre-registration.
4. `research/strategy_iteration_log.md` — one appended entry. Count the existing entries to get the
   iteration number; do not trust the previous label.
5. `research/research_index.md` — one new status-table row, **1–3 lines** (verdict + one-line reason
   + pointer), per meta-review directive #3. Update the cycle counter (this is cycle **#9 of 25**
   since meta-review #1). Update the `n_trials` line in "Standing constraints" **only** if trial #101
   was actually spent.
6. `research/research_metrics.md` — update `n_trials` only if the trial was spent; the two counts
   must always match.
7. `knowledge_base/hypothesis_bank.md` — update the "Efficiency Ratio Regime Gate" card's
   **continuous-action successor** sub-entry from ASSIGNED to the outcome. **If the cycle is rejected
   at F-P3, F-P4 or F-T**, also add the family-closure note to the ADX Trend/No-Trend, MESA/Hilbert
   Cycle-Presence and Hidden Markov Regime-Switching cards and add a row to the FAMILY STATUS LEDGER,
   per §4.3. **If the cycle stops at F-P1 or F-P2**, the family stays OPEN — say so explicitly and do
   not close it.
8. If and only if trial #101 is spent and the candidate is promoted: update
   `research/current_champion.md`, `research/best_strategy_so_far.py`, and
   `user_data/strategies/TrendVolTarget.py`. Otherwise leave all three untouched.

**Reporting honesty requirements.** Per meta-review directive #1 (claim-must-cite-test), any claim
that a function was executed must cite the specific run that called the **real** function with the
real caller's argument convention. Report every number you computed, including ones that undermine
the hypothesis. A cycle that reports an honest negative is a successful cycle; a cycle that reports a
flattering number it cannot reproduce is a rejected cycle. An honestly reported blocker is an
acceptable outcome; a fabricated data point is not.

---

## 12. Environment notes

- **Python:** use **Python 3.13**, not the PATH default 3.14 (3.14 lacks `python-rapidjson` and
  freqtrade imports will fail).
- **Network:** OKX access was repaired in T-027 by uninstalling `aiodns` (which forced `aiohttp` onto
  `ThreadedResolver`). **Do not reinstall `aiodns`.** This task needs no network access at all.
- **The two datasets are distinct — do not conflate them.** The T-028 review brief §4 flagged the
  research feathers as "seven weeks stale despite T-027 appending fresh bars." The Director verified
  this directly on 2026-07-19 and it is a conflation of two separate datasets:
  - `user_data/data/okx/futures/*.feather` — the **research** lane. Frozen at mtime 2026-06-10,
    data ending **2026-05-27**. This is correct and desirable: a frozen window keeps every cycle's
    results mutually comparable and reproducible. **This is the data T-029 uses.**
  - `user_data/data/okx/*_USDT-1d.feather` — the **forward/dry-run** lane. Refreshed 2026-07-19
    11:59, exactly as T-027 reported. The bot is live (`user_data/logs/dryrun.log` written 12:08).
  T-027's acceptance stands and there is no staleness problem. **Do not "fix" either dataset.**
- **`n_trials` is 100** at the start of this cycle (T-028 spent #100). `research_metrics.md` is
  authoritative; if it disagrees with `research_index.md`, report the discrepancy rather than
  silently picking one.
- **Champion baseline reference values** (for the Step 1 assertion band only — always use your own
  replicated values downstream): FULL Sharpe **1.154**, TEST Sharpe **0.391**, MC tail
  P(DD<−25%) **33.6%**, DSR **0.5949** @ n_trials=100 (all from the T-028 Reviewer's verified rerun).
- **`research/current_champion.md` staleness flag:** champion DSR is recorded there at n_trials=98.
  The T-028 brief supplies the refreshed figure (0.5949 @ 100). Update that file's DSR row **only**
  if Step 7 is reached; a cycle that stops at a pre-gate leaves the flag standing.
- **Files confirmed present:** `user_data/research/phase22_ivsizing.py`,
  `user_data/research/phase23_effratio.py`, `user_data/research/validator.py`, `freqtrade_dsr.py`,
  both futures feathers.
- **Files confirmed ABSENT — do not cite them as if they exist:** `research/parked/` (no such
  directory), `research/results/T-028_report.md` (never written),
  `knowledge_base/implementation_patterns.md`, `EDGE_FRAMEWORK.md` and `AI_RESEARCH_PLAYBOOK.md` are
  referenced by `hypothesis_bank.md` but may be stubs — verify before relying on them.
- **Meta-review status:** 8 of 25 cycles completed since meta-review #1; this is cycle #9. Not due.
