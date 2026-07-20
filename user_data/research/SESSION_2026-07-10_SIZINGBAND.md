# Session 2026-07-10 — H-SizingBand: rebalance-granularity / no-trade-band refinement of the champion's vol-target sizing layer

Pre-registered, single-shot, pre-gated experiment (**would-have-been trial #98**; the two
pre-gates cost zero n_trials). Script: `phase19_sizingband.py`. Assignment:
`research/NEXT_TASK.md` (2026-07-10, Research Director cycle #8). The trading signal
(SMA200 / ROC30 / EMA20>EMA50 gate) is NOT touched; only HOW the vol-target weights are
discretized changes. This is the dual of H-RangeVol (#97): #97 proved a better estimator
is discarded by the 25% quantizer; this asks whether the quantizer itself costs.

## 1. Pre-registration block (LOCKED before any results were produced)

Written and saved to this file before any number existed — before the baseline
replication, before pre-gate A, before anything. Everything below the end marker was
filled in afterwards. All thresholds below are copied verbatim from NEXT_TASK.md; the
subsection "Locked free constants" fixes the definitions NEXT_TASK left open, and was
also written before any computation.

### Hypothesis

The champion's 25%-step weight quantization is a material source of avoidable risk: it
discards sizing precision (proven by #15/H-RangeVol) AND forces whipsaw rebalances in
chop. A continuous-or-banded discretization tracks the vol target closely enough to cut
the MC drawdown tail below 20%, and its extra fee drag (if any) is smaller than the gross
benefit — net, it improves robustness without hurting the return stream.

### Harness conventions (identical to phase15/16/18 — the recorded champion stream)

BTC+ETH futures 1d feathers (2020-01→2026-05), fees 0.15%/side charged on |Δposition|,
2-bar lag (signal close[t] → exec open[t+1] → held close[t+1]; implemented as shift(2) on
signal-time weights vs close-to-close returns), per-asset weight =
`quantize_or_scheme(core × clip(0.40 / rv30, 0, 1)) / 2` (2-pair basket, 50%/pair cap),
rv30 = 30d close-to-close std × √365. Frozen: VOL_TARGET 0.40, VOL_LOOKBACK 30,
PER_PAIR_CAP 0.50, core signal, exits, fees, lag, universe. 70/15/15 chronological split
judged on TEST; MC = 1,000 monthly-block shuffles, seed 11; DSR via `freqtrade_dsr.py`.

### Pre-gate A — continuous-sizing upper bound (zero n_trials)

1. **Replication gate first**: BASELINE = current 25%-step quantizer must reproduce the
   recorded band — full-window harness Sharpe ≈ 1.11 (accept 1.0–1.4 per phase15 band),
   TEST Sharpe ≈ 0.39 (accept 0.30–0.50), MC P(DD<−25%) ≈ 30.5% (accept 20–45%).
   Mismatch → STOP everything.
2. CONTINUOUS-BOUND = identical formula with NO quantization, with fees charged ONLY on
   the baseline's fee events: `ret_bound = gross_continuous − baseline_turnover × fee`.
   Deliberately unrealistic (fee-free incremental turnover) — it is a hard UPPER BOUND on
   what ANY discretization scheme can achieve.
3. Report ΔSharpe (full + TEST), ΔmaxDD, ΔMC tail (1,000 monthly-block sims, seed 11) for
   the bound vs baseline.
4. **STOP RULE (verbatim from NEXT_TASK)**: FAIL unless the continuous bound improves MC
   P(DD<−25%) by ≥ 5 percentage points (e.g. 30.5% → ≤ 25.5%) AND does not degrade
   full-window Sharpe by more than 0.05 or TEST Sharpe by more than 0.05. If the bound
   fails, the sizing layer is declared **CLOSED at its efficient frontier** — zero trials
   spent.

### Pre-gate B — turnover / fee-drag census (only if A passes; zero n_trials)

Fixed scheme set (locked, no others, no width/step sweeps):

- `continuous` — no quantization, real fees;
- `step10` — 10%-step quantization: `round(scale / 0.10) × 0.10`;
- `step25` — the baseline (reference);
- `band10` — no-trade band: hold the previous weight unless |held − continuous target| >
  10% of equity, then rebalance exactly TO the continuous target.

For each: annualized turnover and fee drag computed mechanically from the weight series
(cost accounting only — no performance numbers at this stage), plus tracking error to the
continuous target.

**STOP RULE (verbatim)**: FAIL unless at least one non-baseline scheme has (annualized
incremental fee drag vs baseline) < (annualized gross benefit implied by pre-gate A's
bound, prorated by that scheme's tracking-capture fraction). The qualifying scheme with
the LOWEST fee drag among those capturing ≥ 80% of the continuous scheme's tracking
improvement is THE trial candidate — selected by this formula, not by inspection of
returns.

### Locked free constants (fixed here, before any computation, where NEXT_TASK left a definition open)

1. **Turnover**: `turnover_ann(s) = mean_daily( Σ_assets |Δpos_s| ) × 365`, where `pos_s`
   is the scheme's held (2-bar-lagged) weight series. First day's turnover = initial
   position size. **Fee drag**: `fee_ann(s) = turnover_ann(s) × 0.0015`.
   **Incremental fee drag** = `fee_ann(s) − fee_ann(step25)`.
2. **Tracking error**: `TE(s) = mean_daily( Σ_assets |pos_s − pos_continuous| )` with
   `pos_continuous` = the lagged unquantized target. By definition TE(continuous) = 0.
3. **Tracking-capture fraction**: `capture(s) = (TE(step25) − TE(s)) / TE(step25)`;
   continuous = 1.0 by construction.
4. **Annualized gross benefit from pre-gate A**: `B_ann = (mean_daily_ret(bound) −
   mean_daily_ret(baseline)) × 365` (arithmetic, same-index daily streams).
5. **Qualification test**: scheme s qualifies iff
   `incremental_fee_drag(s) < B_ann × capture(s)`.
6. **Strict reading of the selection rule** (ambiguity resolved now): pre-gate B passes
   only if at least one scheme BOTH qualifies under (5) AND has capture(s) ≥ 0.80. The
   trial candidate = the lowest-incremental-fee-drag scheme among that intersection. If
   qualifiers exist but none reaches 80% capture → pre-gate B FAILS (no trial).
7. **Band gate-exit rule** (preserves the signal layer byte-identical): when core = 0 the
   target is 0 and the exit ALWAYS executes regardless of the band (the band applies to
   sizing adjustments only, never to gate entries/exits). Without this rule a residual
   ≤10% position could ride through a bear market, which would change the signal layer —
   out of scope for a sizing-layer hypothesis. Entries from flat likewise always execute
   at the full target (from 0 to target > 0 the difference exceeds 10% in practice for
   any quantized entry; for continuous targets ≤ 10% the entry still executes — flat→long
   is a gate event, not a sizing adjustment).
8. **Band causality**: band state at signal-time t depends only on the band's own
   signal-time state at t−1 and the target computed from data through close[t]; execution
   uses the same shift(2) as every other scheme. (Look-ahead audit in the trial verifies
   this.)
9. **MC seed 11**, 1,000 monthly-block sims, for every MC number in this session.
10. **DSR n_trials**: 98 for the trial candidate (and the baseline recomputed at 98 for
    like-for-like), per NEXT_TASK. If the session stops at a pre-gate, n_trials stays 97.

### The trial (ONLY if both pre-gates pass — this and only this consumes trial #98)

ONE construction: the champion with the pre-gate-B-selected discretization, all other
parameters byte-identical. Full stack: 70/15/15 judged on TEST; `wf_window_stability` at
3/4/5/6 windows (validator.py); MC 1,000 monthly-block sims seed 11; DSR at n_trials=98
via `freqtrade_dsr.py`; `family_context` from the results dir; look-ahead audit of the
band logic (band state must depend only on completed bars).

### Required validation bars (pre-declared; ALL must hold to promote)

1. MC P(DD<−25%) ≤ **20%** (the project bar #15 missed), AND
2. TEST Sharpe ≥ baseline − 0.05 AND full-window Sharpe ≥ baseline − 0.05, AND
3. WF majority-positive at ≥ 3 of the 4 window configs (3/4/5/6), AND
4. DSR at n_trials=98 ≥ baseline 0.626, AND
5. Turnover/fee accounting reported per year (no silent fee increases).

### Promotion / rejection

- ALL bars pass → the discretization change is promoted INTO the champion
  (`best_strategy_so_far.py`, `user_data/strategies/TrendVolTarget.py`,
  `current_champion.md`, `strategy_portfolio.md`) as a sizing-layer amendment.
- Any bar fails → REJECT, document in full, champion untouched. Close-but-failing →
  "ideas parked"; no second construction, no threshold nudging.
- Pre-gate A fails → explicit "sizing layer CLOSED at efficient frontier" entry in the
  open-hypotheses list.

### Budget

Maximum backtested constructions: **1** (the pre-gate-B-selected scheme only). Scheme set
fixed at the four listed; band width (10%) and step (10%) locked; no sweeps of anything.
n_trials advances 97 → 98 ONLY if both pre-gates pass and the trial runs.

**— END OF PRE-REGISTRATION BLOCK —**

## 2. Baseline replication — PASSED

Harness (phase15/16/18 convention: BTC+ETH futures feathers 2020-01→2026-05, fees
0.15%/side, 2-bar lag, quantized vol-target weights / 2):

- TEST Sharpe **0.39** (accept band 0.30–0.50; recorded 0.39–0.41) — matches phase15.
- Full-window harness Sharpe **1.11** (accept 1.0–1.4; recorded ~1.11).
- MC P(DD<−25%) **30.5%** at 1,000 sims seed 11 (accept 20–45%; recorded 30.5%) —
  bit-identical to the phase15 baseline.

Baseline valid; pre-gate A proceeded. Re-run of the full pipeline reproduced every
number exactly (deterministic; seed 11).

## 3. Pre-gate A — continuous-sizing upper bound: **FAIL on 2 of 3 conditions. STOPPED.**

The bound (continuous, unquantized weights; fees charged only on the baseline's fee
events — deliberately fee-free incremental turnover, the hard ceiling for any
discretization scheme):

| Metric | BASELINE step25 | BOUND continuous (fee-free incr.) | Stop-rule requirement | Verdict |
|---|---|---|---|---|
| MC P(DD<−25%), 1,000 sims seed 11 | 30.5% | 27.5% | improve ≥ 5.0pp (→ ≤ 25.5%) | **FAIL** (+3.0pp only) |
| TEST Sharpe | 0.39 | 0.27 | ≥ baseline − 0.05 | **FAIL** (−0.122) |
| Full-window Sharpe | 1.11 | 1.08 | ≥ baseline − 0.05 | PASS (−0.033) |
| Full-window MaxDD | −16.9% | −17.9% | (reported) | worse by 1.0pp |
| MC median DD | −22.7% | −22.2% | (reported) | +0.4pp |
| Full CAGR | +22.7% | +21.8% | (reported) | worse |

**The stop rule triggered.** Even with zero incremental fees — an unreachable best
case — perfectly continuous tracking of the vol target delivers only +3.0pp of the
required ≥5.0pp tail improvement, and it BUYS that with a 0.12 TEST-Sharpe degradation
and a slightly worse realized max drawdown. Since every scheme in the fixed set
(10%-step, 10% no-trade band) can only approximate this target while paying real
incremental fees, none can beat the bound. Per the pre-registered rule:

**THE SIZING LAYER IS DECLARED CLOSED AT ITS EFFICIENT FRONTIER. Zero trials spent;
n_trials remains 97.** Pre-gate B and the trial were never reached.

## 4. Diagnostics — why the hypothesis is wrong (reporting-only, `phase19_diag_bound.py`)

The hypothesis asserted the 25% quantizer "discards sizing precision AND forces whipsaw
rebalances in chop." The decomposition shows the opposite mechanism:

1. **The quantizer is not systematically mis-sized.** Mean exposure is essentially
   identical (0.222 vs 0.221 full-window; 0.178 vs 0.176 TEST). The quantizer rounds UP
   (holds more than the continuous target) on 20.9% of days and DOWN on 15.4% —
   near-symmetric, tiny net (+0.003 in-market). There is no material precision being
   "discarded"; with 2 assets × 4 non-zero levels the quantizer already tracks the
   target closely — exactly the honest failure mode (a) named in the assignment.
2. **Continuous tracking LOSES in chop — the regime it was predicted to help.** Yearly
   difference (bound − baseline): 2020 +2.1%, 2021 −0.6%, 2022 +0.1% (flat by gate),
   2023 −2.4%, 2024 −2.4%, 2025 −1.8%. The chop years 2023–2025 are precisely where
   the hypothesis predicted the band/continuous scheme would help; instead, following
   every wiggle of rv30 through those rotations sized the book slightly wrong at each
   turn, while the 25% steps acted as a hysteresis filter that ignored estimator noise.
   The quantizer IS the no-trade band, effectively — a coarse one that already does the
   band's job for free.
3. **The TEST degradation is the same episode-hostage pattern as #97**: −1.47% in
   2025-08 and −1.09% in 2025-07 dominate the TEST delta (TEST span 2025-06→2026-05,
   ~100 in-market days). Same two months that decided H-RangeVol. On this small a
   sample the sign is not deeply meaningful — but the stop rule is the stop rule, and
   unlike #97 the failure here is TWO-sided: the tail bound ALSO missed, independently
   of the TEST episode.
4. **Cross-check with #97's arithmetic**: H-RangeVol moved MC tail 30.5→22.9% by
   changing the estimator WITHIN the quantizer. The unquantized bound here only reaches
   27.5% with the cc30 estimator. Both routes fall short of ≤20% — consistent evidence
   that the residual tail is carried by the champion's structural exposure pattern
   (long crypto in confirmed uptrends), not by sizing implementation error.

## 5. Verdict

**H-SizingBand: REJECT at pre-gate A (upper-bound kill switch). Zero trials spent.
n_trials unchanged at 97. Champion untouched** (`best_strategy_so_far.py` /
`TrendVolTarget.py` byte-identical; verified nothing was modified).

Combined with H-RangeVol (#97, better estimator — rejected) this closes the sizing
layer from BOTH directions: better inputs are discarded by the quantizer, and removing
the quantizer is worthless even fee-free. **The champion's 25%-step vol-target sizing
implementation is at its efficient frontier.** Per NEXT_TASK deliverable 4, the
open-hypotheses list gains an explicit closure entry mirroring BearShort/CointPair.

## 6. Lessons

1. **The 25% quantization step is a feature, not a defect.** It functions as a free
   no-trade band/hysteresis filter on a noisy vol estimate: rv30's day-to-day
   fluctuation is mostly estimator noise (established in #97's synthetic work), and
   tracking that noise continuously is slightly harmful gross of fees, before any fee
   argument. Lesson #8's phrasing ("precision is discarded by the quantizer") was
   technically right but wrongly valenced — the discarding is protective.
2. **The mathematical-upper-bound pre-gate is the cheapest kill switch yet**: one
   fee-free counterfactual closed an entire hypothesis family in one computation, at
   zero trial cost, with no possibility of "maybe a different band width" — any
   band/step scheme is dominated by the bound by construction. Pre-gate discipline is
   now 4-for-4 (EWMA sanity gate, BearShort whipsaw census, CointPair stationarity
   census, SizingBand continuous bound).
3. **The champion's MC tail (~30%) is structural, not implementational.** Two
   independent sizing-layer refinement routes (estimator quality #97, rebalance
   granularity #98-candidate) both failed to reach ≤20%. The tail lives in what the
   strategy IS (long-only crypto trend with ~0.8 asset correlation), and the only
   validated instrument that actually cuts it remains the portfolio-level overlay
   (defensive variant: P(DD<−25%)=1%) — at return cost. Future tail-reduction ideas
   must operate at the portfolio/allocation level, not inside the sleeve's sizing.
4. **Jul–Aug 2025 decides every sizing experiment on this TEST split** (#97 and this
   session). Any future sizing-adjacent evaluation should report that episode's
   contribution explicitly before interpreting a TEST delta — and the honest fix is
   still calendar time (the dry-run), not another backtest.

Standing rule unchanged: **dry-run only, no real capital on backtest evidence.**

