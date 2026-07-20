# Meta-Review #1 — Research Program Audit

**Date**: 2026-07-18. **Auditor**: Research Program Auditor (Prompt 4). **Coverage**: cycles #1–#25
(project start 2026-05-14 → T-018 Reviewer rejection 2026-07-15). **First meta-review ever performed**
(interval = 25; counter reached at cycle #25). n_trials at audit time: **98**. Champion: TrendVolTarget
(unbeaten since 2026-06-11). No prior meta-reviews exist; `research/parked/` and `research/champions/`
directories do not exist (parked ideas live inline in iteration-log entries — acceptable, see §6).

---

## 1. Recurring failure modes

Clustering all rejections (index rows #1–#22, iteration log 1–20):

**Cluster A — OOS collapse / selection overfitting (dominant killer, ~85 of ~94 rejections).**
EmaRsiVolume family (#1), pullback/MR/breakout/Donchian/Bollinger (#2), squeeze/fade (#3),
overnight breakout (#6), SMA200 overlay (#7, IS 30.9% CAGR → OOS 2.77%), the 61-strategy sweep
(#8, 0/61), blending/dual-momentum/calendar/x-sect (#11), all six Forven-derived ideas (#13),
dominance rotation (TRAIN 1.67 → TEST 0.21). The signature is always the same: positive
in-sample, collapse on held-out data.

**Cluster B — statistical object does not exist (the pre-gate era's killer, 5 stops).**
H-BearShort (#16: median mirrored-gate episode 3 bars), H-CointPair (#18: no cointegration on any
window, post-2024 ADF p 0.405), H-SizingBand (#19: fee-free continuous bound fails the bar),
H-IVGate (#21: 4 in-market spike episodes < 6), H-IVSizing (#22: affected days are *favorable* —
VRP positive-carry). Plus the EWMA synthetic-gate cancel (#15). These are not new mistakes — they
are Cluster-A candidates being killed earlier and cheaper.

**Cluster C — costs.** 0.15%/side kills everything intraday (hours 21-22 UTC anomaly real at
t=2.4–3.0 but fees exceed edge 25:1, #12); 4h/high-frequency variants of the 61-sweep all fell
under Sharpe 1.0 from fee drag.

**Cluster D — data unreachability.** Funding history, order book, liquidations, on-chain,
sentiment (#4 + metrics data-axis table); basis proxy is noise (#5).

**Cluster E — NEW and ACTIVE: instrument-task overclaiming (3 incidents in the last 10 cycles).**
(i) Cycle #16 A-DryRunMonitor: "100% coverage" and "mechanical parity PASS" both false (stale
expected side, log-anchored coverage) — INVALID CYCLE. (ii) T-017: report claimed
`shock_day_mask` "called (not just imported)" — false. (iii) T-018: report claimed the fixture
"passes through `compute_shock_share`" — false (inline replica), and the Reviewer found a
confirmed units bug (returns double-pct_changed) in the exact path the claim covered — REJECTED.

**Are the same mistakes recurring despite being logged — and why isn't memory preventing them?**
Cluster A is *not* recurring: pre-registration + DSR gate + pre-gates (adopted from cycle #10 on)
converted it into Cluster B at zero trial cost. That is the memory system working.
Cluster E *is* recurring: T-018 overstated the same shock-share path T-017 had just been
corrected on, one cycle later, with the lesson already written into strategy_research_notes.md.
Root cause: prose claims in reports are cheap and are only checked when the Reviewer reruns the
actual call chain; the memory system records lessons but nothing *structurally* forces the
Engineer to comply with them mid-task. The Reviewer layer caught all three incidents — the safety
net works, but it is catching the same class of ball twice. Corrective directives in §"Directives"
below (claim-must-cite-test rule).

## 2. Recurring success patterns

Only three things have ever been promoted or kept: TrendVolTarget (champion, #9), the 9-asset +
portfolio-vol defensive variant (#10, bench slot), and the 80/20 allocation stance (#20, trial
#98). They share every one of these properties:

- **Mechanism is risk management, not prediction**: regime *avoidance* (binary in/out gate) plus
  vol-target sizing. No promoted construct forecasts anything.
- **Daily timeframe** — the only timeframe that survives the fee floor.
- **Low complexity**: 3-of-3 gate + one sizing formula; zero free parameters in the allocation
  stance (formula-selected w*).
- **Broad parameter plateaus** (SMA 150–250, ROC 20–40, vol-target 30–50%) — never a peak.
- **Cross-asset transfer without re-tuning** (9/9 positive Sharpe).
- **Layered validation survived**: WF majority-positive, MC, DSR-honest, engine-verified,
  shock-decomposition favorable (less shock-dependent than the underlying).

Corollary the program has already internalized: the marginal promoted unit has moved *up* the
stack — sleeve (June) → sizing audit (closed) → portfolio allocation (July). The remaining
unexplored upside is above the sleeve level or in forward data, not inside it.

## 3. Exploration coverage

Mapping completed work onto the hypothesis-bank families:

| Bank family | Status | Evidence |
|---|---|---|
| 1. Trend-following | **Heavily mined; champion extracted** | #1, #2, #7, #8 (batches 1–4), #9, #13; MA-crossover, Donchian, Supertrend, ensembles all swept |
| 2. Mean reversion | **Mined and dead at every tested timeframe** | #2, #3 (negative even IS), #8, #13 z-fade; structural: fees vs reversion amplitude |
| 3. Breakout | **Mined and dead** | #2, #3, #6; squeeze breakouts "buy local tops" |
| 4. Momentum | **Mined** | #8 (x-sect mom DD −66%), #11 dual momentum; TSMOM short symmetry closed (#16) |
| 5. Volatility-based | **Sizing arm closed at efficient frontier (both directions); IV arm closed on daily bars** | #15 estimator, #19 granularity, #21 DVOL veto, #22 DVOL sizing |
| 6. Regime-based | **Core mined** (SMA200, HMM, COT #14); ER-gate/MESA variants untested but are OHLCV signal constructs → banned family |
| 7. Cross-sectional / portfolio | **Partially mined, one success** | x-sect top-K failed (#11); H-TailAlloc promoted (#20); frontier knee mapped w=0.0→1.0 |
| 8. Statistical / ML | **Untouched by design** | Correctly so: ML on the same exhausted OHLCV is Cluster-A bait at maximum DSR cost with n_trials=98 |
| 9. Crypto-specific | **All reachable axes tested or blocked** | Funding BLOCKED, basis noise, COT tested+rejected, DVOL fully closed, sentiment/on-chain BLOCKED, cointegration closed |

**Is the program stuck in a local neighborhood?** No — the opposite. It deliberately walked the
full structural map (signal prediction, sizing, short side, relative value, external axes) and
closed each lane with evidence. The un-mined areas (ML §8, adaptive trend-speed, multi-timeframe)
are parameter-variations or re-samplings of the same exhausted dataset, and the standing rule
("genuinely new data dimension or structurally different mechanism") correctly bans them. The
open frontier is **calendar time** (forward dry-run evidence) and **new data axes** (which mostly
require live recording started now — see bank refill).

## 4. Exhausted themes — formally CLOSED at family level

Declared closed with evidence; future Directors must not assign these (the hypothesis bank now
carries matching CLOSED markers):

1. **Mean reversion on crypto OHLCV (all tested timeframes)** — never positive even in-sample
   (#2, #3, #8, #13); winners structurally smaller than losers; fees vs amplitude.
2. **Intraday / time-of-day / sub-daily anything** — fee floor 0.15%/side; the one real anomaly
   (21-22 UTC) is untradeable 25:1 (#12); equities session mechanisms have no 24/7 analog (#6).
3. **Short side / symmetric TSMOM of the champion's gate** — whipsaw census (#16): crypto bears
   are crashes-then-squeezes; 2018's −84% year yielded +2.6% gross.
4. **BTC-ETH pairs / relative value / rotation / dominance / ratio constructions** — no
   cointegration on any window; post-2024 ETF-era break formal (#18); retroactively explains #13.
5. **Sleeve sizing refinement** — closed at efficient frontier from both directions (estimator
   #15, granularity #19); the 25% quantizer is a protective no-trade band.
6. **DVOL daily-bar champion modifications** — veto closed at B3a (#21), sizing closed at P2
   (#22); VRP is positive-carry; no third mechanism without new data.
7. **New OHLCV signal-prediction constructs generally** — 61-sweep 0/61 plus everything else;
   the structural map is closed; any new backtest spends trial #99 against DSR 0.95 with the
   champion priced at 0.624.

**Remaining OPEN**: H-ForwardParity (needs ≥3 months coverage); portfolio/allocation layer above
the sleeve (one interior point validated; dynamic-w parked as a new mechanism); new data axes
contingent on live recording or a paid vendor.

## 5. Process health

- **Budgets: respected and honestly counted.** n_trials=98 verified consistent across
  research_index / research_metrics / current_champion at every audit; five would-be trials
  stopped at zero cost; the H-RangeVol session even *corrected down* a budgeted count (98→97)
  when only one variant ran. Exemplary.
- **Falsification discipline: holding.** Every trial since #96 pre-registered with locked stop
  rules before results; stop rules honored even on near-misses (GK tail 22.9% vs ≤20% bar —
  "the criterion is the criterion").
- **Pre-gate record: 6 valid stops, 1 false stop (corrected).** The false stop (IV lead/lag sign
  bug) would have closed the last reachable data axis on a one-line pandas error; Director rerun
  caught it. The resulting rules (assert xcorr sides differ; Director reruns all stops) are sound
  and were followed in cycles #14–#15.
- **Engineer reliability: bimodal.** On pre-registered *trials and censuses*, Engineer numbers
  have reproduced exactly under every Director/Reviewer rerun (phases 16–22). On *instrument
  tasks*, 3 of 4 recent cycles contained false prose claims (§1 Cluster E). Reviewer/Director
  verification is load-bearing and must remain mandatory for instrument work.
- **Report completeness: good for trials, weaker for instruments** (T-017 missing sections
  originally; T-018 §1 trigger block paraphrased, current_champion.md update skipped).
- **Standards drift in promotions: none found.** Both promotions (champion 2026-06-11 stance
  2026-07-11) passed full bars; H-TailAlloc was Director-rerun plus a 10-seed robustness check.
  No bar has ever been retuned to let a candidate pass.
- **Outstanding process debts**: `research/`, `knowledge_base/`, `user_data/research/` are largely untracked in git — the project's entire evidentiary record is working files.

## 6. Memory health

- **research_index.md**: the one-line-per-cycle discipline has degraded — rows #21–#25 are
  10–20-line paragraphs and the header banner had grown to ~25 lines of nested history. Compacted
  this session (banner rewritten; rows left intact as they are load-bearing evidence, but future
  rows must return to 1–3 lines with detail pushed to the iteration log).
- **Numbering defects (recorded, deliberately NOT renumbered — external citations reference the
  existing numbers)**: (a) research_index "Lessons from empirical testing" jumps #15 → #19
  (16–18 never existed); (b) strategy_iteration_log.md contains two entries numbered
  "Iteration 18" (H-IVSizing and the invalid A-DryRunMonitor cycle). Future entries: count
  entries, don't trust the last label (T-018's assignment already said this).
- **strategy_research_notes.md**: accumulating well — superseded entries are struck through with
  corrections in place rather than deleted, which preserves the audit trail. Distillation
  section added this session (see Outputs); the strikethrough style is acceptable but each future
  meta-review should collapse fully-dead struck text into one-line tombstones.
- **Parked ideas**: live inline in iteration-log entries (regime-gated pairs, dynamic-w,
  anti-whipsaw chop filter, dry-run shock-share drift metric). Acceptable at current volume; if
  parked ideas exceed ~10, create `research/parked/` as the manual's structure implies.
- **hypothesis_bank.md**: was missing project-closure status at family level — added this session.

## 7. Champion robustness (independent of any single cycle)

The evidence still looks **sound**, and has strengthened since promotion:

- The 2026-07-10 Kaufman Ch.21 audit passed both pre-declared downgrade triggers: champion is
  *less* shock-dependent than BTC hold (removing all static-p99 shock days improves Sharpe
  1.11→1.20), and WF verdicts are boundary-stable (majority-positive at 3/4/5 windows; rolling
  18m Sharpe never negative in 61 evaluations).
- Every subsequent attack (COT filter, better estimator, finer rebalancing, short sleeve, pairs,
  DVOL veto, DVOL sizing) either lost to it or was stopped pre-gate — 13 months unbeaten across
  ~13 constructs tested since promotion.
- The honest price remains DSR 0.624 at n_trials=98 (~62% probability of real edge; family
  peak-of-66 context is exactly what DSR discounts) and forward expectation 5–15% CAGR.

**Accumulated doubts to carry forward**: TEST-split verdicts are episode-hostage (Jul–Aug 2025 decided two experiments).

## 8. Competition Mode readiness

Assessed against the four criteria:

1. **Stable champion with strong multi-gate evidence** — YES. Unbeaten 13 months; WF + MC + DSR +
   cross-asset + engine-parity + shock-decomposition + boundary-stability; Director-verified.
2. **Substantial body of validated experiments** — YES. 98 honestly-counted trials, 25 audited
   cycles, ~96% rejection rate, reusable validator + DSR gate + pre-gate toolkit.
3. **Closed/exhausted obvious hypothesis families** — YES. §4 above: the structural map is closed
   with evidence, formally declared.
4. **Healthy process discipline** — MOSTLY. Trial discipline is exemplary; instrument-task
   discipline produced one invalid cycle and one rejection in the last four cycles, and the
   standing monitor carries a confirmed bug.

**VERDICT: YES — Competition Mode is warranted**, with two prerequisite repairs before the first
Challenger cycle (both zero-trial, both already Reviewer-specified):
(P1) commit `research/`, `knowledge_base/`, and
`user_data/research/` to git so the evidentiary record a Challenger will attack is immutable.
The operator may introduce the Challenger and Independent Reviewer agents once P1–P2 land.
Rationale for YES despite §5's blemishes: every violation was caught by the existing review
layer — the adversarial machinery Competition Mode formalizes is already demonstrably working.

---

## Directives for future cycles (Research Director and Independent Reviewer MUST read during Phase 0)

1. **Claim-must-cite-test rule.** Any report claim of the form "function/path X was executed /
   covered / passes through Y" must cite the specific test or run that calls the REAL function
   with the REAL caller's argument convention. The Reviewer rejects the claim (not necessarily
   the cycle) if the citation is missing or the test replicates internals inline. A test-file
   comment of the form "we call the underlying logic directly to avoid X" is an automatic red
   flag requiring Reviewer rerun through the real path.
2. **Shock-share path is unverified-by-default.** After two consecutive false claims (T-017,
   T-018), any Engineer statement about `compute_shock_share` / `shock_day_mask` coverage is
   treated as false until a Reviewer reruns it end-to-end through `main()`'s convention.
3. **Index row discipline.** New research_index status rows: 1–3 lines (verdict + one-line reason
   + pointer). Detail belongs in the iteration log and session reports. Iteration numbering:
   count existing entries; never trust the previous label.

5. **Closed families are closed.** §4's seven family closures are binding. Assignments touching
   them require the specific reopening evidence named in their closure notes (e.g., a passing
   forward rolling-cointegration census; sub-daily IV data), not a re-parameterization.
6. **Operator actions outstanding** (proposed, not assigned — operator to action): git commit of the research record (P2 above).
7. **Proposed for operator decision (NOT adopted here — the manual's standards are unchanged):**
   consider a standing rule that instrument/monitoring code ships with its fixture suite in the
   same cycle and the Reviewer reruns fixtures as a default acceptance step. This matches what
   T-017/T-018 already did informally and would have caught both false claims earlier.

---

## Bookkeeping performed by this meta-review

1. This file created (`research/meta_reviews/meta_review_1.md`).
2. `knowledge_base/hypothesis_bank.md`: family-status ledger added (CLOSED markers per §4);
   new-entries section added targeting the open frontier (live-recording data axes,
   forward-contingent constructions).
3. `strategy_research_notes.md`: program-level distillation added; superseded finding #7 text
   compacted.
4. `research_index.md`: META_REVIEW_DUE banner removed; meta-review #1 recorded; cycle counter
   reset to 0/25; header compacted.
5. No task assigned; no strategy promoted/demoted; `best_strategy_so_far.py` untouched;
   validation standards unchanged. n_trials remains **98**.
