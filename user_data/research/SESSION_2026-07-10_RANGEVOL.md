# Session 2026-07-10 — H-RangeVol: range-based volatility estimator in the champion's sizing layer

Pre-registered experiment, **trials #97 and #98** in the project's cumulative DSR ledger.
Script: `phase15_rangevol.py`. Assignment: `research/NEXT_TASK.md` (2026-07-09 Research
Director cycle). Trading signal untouched; only the vol-target sizing layer's volatility
input changes.

## 1. Pre-registration block (LOCKED before any results were produced)

Written and committed to this file before the sanity checks, baseline replication, or
either trial was run. Everything below this block's end marker was filled in afterwards.

### Hypothesis

The champion (TrendVolTarget) sizes positions as `clip(0.40 / rv30, 0, 1)` where `rv30` is
the 30-day close-to-close return std, annualized ×√365. Range-based estimators
(Parkinson 1980; Garman-Klass 1980; Rogers-Satchell 1991) are 5–8x more statistically
efficient per observation because they use the intrabar high/low range — a data dimension
no construct in this project's 96-trial history has ever used.

**H-RangeVol: a range-based (or faster exponentially-weighted) volatility estimate reacts
faster and with less noise to volatility regime shifts, so the vol-target sizing de-risks
earlier when volatility expands (thinner drawdown tail) and re-risks sooner when it
compresses, with no degradation of the signal layer.**

**Primary pre-registered prediction: reduction in Monte Carlo P(MaxDD < −25%)** — the
champion's single weakest documented metric (28–38% across recorded runs). Sharpe is only
required not to degrade (non-inferiority). We are predicting a specific tail-risk
mechanism, not hunting a higher headline number.

### Variants (exact, no others)

- **Trial #97 (primary) — Garman-Klass 30d**: per-bar variance
  `gk_t = 0.5*ln(H_t/L_t)^2 − (2 ln 2 − 1)*ln(C_t/O_t)^2`;
  `rv_gk = sqrt(rolling_mean_30(gk) * 365)`. Drop-in replacement for `rv`.
  Crypto trades 24/7 (open ≈ prior close, no overnight gap), so GK's no-opening-jump
  assumption is valid here; Yang-Zhang's overnight decomposition would be degenerate.
- **Trial #98 (secondary, run regardless of #97's outcome) — EWMA close-to-close**:
  RiskMetrics standard, λ = 0.94: `var_t = λ*var_{t−1} + (1−λ)*r_t²`;
  `rv_ewma = sqrt(var * 365)`.
- No third variant. No λ tuning. No lookback tuning beyond the reporting-only plateau
  sweep. If neither passes, REJECT and log; do not iterate.

### Frozen (changing any = protocol violation)

VOL_TARGET 0.40, VOL_LOOKBACK 30 (where applicable), QUANT_STEP 0.25, PER_PAIR_CAP 0.50,
core signal (close>SMA200 & ROC30>0 & EMA20>EMA50), exits, −30% brake, fees 0.15%/side,
2-bar signal lag, BTC+ETH 1d universe. No lookahead: estimators use only completed bars
(same shift convention as the existing `rv`).

### Validation plan (in order)

1. **Estimator sanity checks on synthetic data (zero trial cost; gate)**:
   (a) constant-vol GBM — GK/EWMA/CC agree in expectation within sampling error;
   (b) vol-jump series (σ doubles at a known date) — GK/EWMA converge to the new level in
   fewer bars than CC30. If the mechanism is absent, stop and report; spend zero trials.
2. **Baseline replication**: unmodified TrendVolTarget through the harness; require TEST
   Sharpe ≈ 0.39–0.41 and MC tail ≈ 28–38% before running variants.
3. **Full gate stack per variant**: full-window BTC+ETH metrics, 70/15/15 TEST split,
   4-window walk-forward, Monte Carlo (1,000 monthly-block shuffles + slippage stress)
   with explicit P(MaxDD < −25%), cross-asset transfer on the 9-asset universe (unchanged
   parameters), DSR at n_trials=98 (baseline recomputed at 98 for like-for-like).
4. **Plateau check (reporting-only)**: GK lookback swept 20–40; must be a contiguous
   plateau. The reported variant stays at the pre-registered 30d regardless.
5. Report the average of all runs, not the best (Kaufman convention).

### Promotion criteria (ALL must hold for a variant to replace the champion's estimator)

1. **Primary**: MC P(MaxDD < −25%) ≤ 20% (vs same-session baseline 28–38%).
2. **Non-inferiority OOS**: TEST-split Sharpe ≥ 0.35.
3. Full-window Sharpe within 0.10 of same-session baseline; no walk-forward window
   flipping from positive to materially negative (< −5%).
4. Cross-asset: positive Sharpe on ≥ 8 of 9 untuned assets (baseline: 9/9).
5. DSR at n_trials=98 ≥ baseline champion's DSR recomputed at n_trials=98.
6. Lookback plateau confirmed.

### Budget

Maximum 2 backtested variants (trials #97, #98). Hard cap. Sanity checks, baseline
replication, plateau sweep (reporting-only) and the vol-target reconciliation write-up do
not count against n_trials.

**— END OF PRE-REGISTRATION BLOCK —**

## 2. Sanity checks (results)

### 2.0 Methodological note — first implementation was inadequate and was revised BEFORE
### any strategy data was touched (documented for transparency)

The first implementation of sanity check (b) used a **single random seed** and measured
each estimator's first crossing of a threshold derived from the **true** volatility level.
It printed: CC30 12 bars, GK30 19 bars, EWMA 12 bars → "faster-convergence FAIL".
That implementation is statistically invalid for two reasons, both identifiable from
theory alone (no strategy data was involved):

1. **Single realization.** Crossing times are noisy; analytically the expected crossing
   of the midpoint after a σ→2σ jump is ~12.5 bars for a 30d rolling estimator and
   ~8.7 bars for EWMA λ=0.94, yet the single seed showed 12 vs 12.
2. **Bias-confounded threshold.** With 100 intrabar steps the synthetic bar's observed
   high/low understates the continuous range (discrete-monitoring bias), so GK reads
   ~9% low. Measuring GK against a true-vol-derived threshold makes its crossing target
   relatively harder than CC's. Crossing must be measured against each estimator's OWN
   pre/post asymptotic levels.

**Refined check spec (declared before running it):**

- (a) Constant-vol GBM, 100 seeds × 1,000 bars: CC/EWMA mean within ±10% of true;
  GK mean within ±10% of its own discretization-adjusted asymptote, AND the GK bias must
  shrink as intrabar steps increase 100 → 1,000 (proves it is a discretization artifact,
  not an implementation bug). Also report each estimator's std around its own mean —
  the efficiency claim itself (GK std expected ≈ 0.4–0.5× CC std).
- (b) Vol-jump series (σ doubles at a known bar), ≥200 seeds, two measures per estimator,
  both against the estimator's OWN pre/post levels:
  - **first-touch**: median bars to first cross the midpoint of own pre/post levels;
  - **sustained convergence**: median bars until the estimate enters ±15% of its own
    post-jump level and stays there through the 60-bar measurement window (the
    decision-relevant reading of "converge" for a sizing layer, since spurious flips
    re-risk during expansions).
- **Gate (pre-declared)**: an estimator passes (b) if its median sustained-convergence
  time is strictly smaller than CC30's AND its median first-touch is ≤ CC30's + 2 bars
  (integer-bar noise tolerance). If an estimator fails, its
  trial is NOT run (zero-trial stop per NEXT_TASK); the other variant proceeds
  independently (NEXT_TASK specifies #98 runs regardless of #97's outcome and vice versa).
- Honest theoretical expectation recorded up front: GK30 at the same 30d equal-weight
  lookback has the SAME mean response speed as CC30 by construction — its 5–8x efficiency
  appears as lower estimator variance (earlier reliable settling), not a faster mean
  path. The assignment's "reacts faster" phrasing conflates speed and noise for GK
  (it is accurate for EWMA). The refined measures separate these.

### 2.1 Refined check results

**(a) Constant-vol GBM (100 seeds × 1,000 bars, true annualized vol 0.60):**

| Estimator | Mean level | vs true | Estimator std (noise) | vs CC30 |
|---|---|---|---|---|
| CC30 | 0.5937 | −1.0% | 0.0758 | 1.00x |
| GK30 | 0.5456 | −9.1% | **0.0278** | **0.37x** |
| EWMA(0.94) | 0.5945 | −0.9% | 0.0717 | 0.95x |

GK's −9.1% bias shrinks to −3.1% at 1,000 intrabar steps — confirmed a
discrete-monitoring artifact of the synthetic bars (observed high/low understates the
continuous range), not an implementation bug. The headline efficiency claim is CONFIRMED:
GK's estimator noise is 0.37x CC's (≈7x variance efficiency, in the literature's 5–8x
band). EWMA at λ=0.94 has essentially NO efficiency gain over CC30 (0.95x) — its
effective sample size (~33 bars) is nearly identical to the 30-bar rolling window.

**(b) Vol jump 0.60 → 1.20 annualized (200 seeds), measured against each estimator's OWN
pre/post levels:**

| Estimator | Median first-touch (bars) | Median sustained ±15% convergence (bars) | Gate |
|---|---|---|---|
| CC30 | 12.0 | 47.0 | (reference) |
| GK30 | 13.0 | **19.0** | **PASS** |
| EWMA(0.94) | **8.0** | 51.0 | **FAIL** |

- **GK30 PASSES**: same mean response speed as CC30 (13 vs 12 bars first-touch — as
  theory predicts for the same equal-weight lookback), but 2.5x faster *reliable*
  convergence (19 vs 47 bars) because its low noise stops it from repeatedly whipsawing
  out of the ±15% band. The mechanism the hypothesis needs (earlier *reliable* de-risk /
  re-risk levels) is present.
- **EWMA FAILS**: it first-touches faster (8 bars — the λ=0.94 half-life is ~11 bars vs
  an effective ~15 for the rolling window), but its noise is as large as CC30's, so its
  *sustained* convergence (51 bars) is no better than CC30 (47). The pre-registered
  mechanism ("faster AND less noisy") is absent for EWMA on daily data: faster mean
  response was bought entirely with equal noise.

**Consequence (per the pre-declared zero-trial-stop rule): trial #98 (EWMA) was NOT run.**
NEXT_TASK's own contingency ("if either sanity check fails, spend zero trials and report
why") applies per-variant here; #97 (GK) proceeded alone. **Honest cumulative trial count
is therefore 97, not 98.** DSR is reported at n_trials=97 (primary) and n_trials=98
(pre-registered reference; difference is negligible — 4th decimal).

## 3. Baseline replication — PASSED

Harness (phase13/14 convention: BTC+ETH futures feathers 2020-01→2026-05, fees
0.15%/side, 2-bar lag, quantized vol-target weights / 2):

- TEST Sharpe **0.39** (recorded 0.39–0.41) — matches SESSION_2026-07-02 and -07-08.
- MC P(DD<−25%) **30.5%** at 1,000 sims (recorded 28–38%) — in band.
- Full-window harness Sharpe 1.11, DD −16.9% (recorded harness ~1.11; engine 1.26).

Baseline valid; trial #97 proceeded.

## 4. Trial results

Trial #97 (GK30) vs same-session baseline. All numbers same harness, same seeds.

| Metric | Baseline cc30 | GK30 (#97) | Promotion bar |
|---|---|---|---|
| **MC P(MaxDD<−25%), 1,000 sims (PRIMARY)** | 30.5% | **22.9%** | ≤ 20% → **FAIL (near miss)** |
| MC median DD | −22.7% | −21.5% | — |
| **TEST Sharpe (non-inferiority)** | 0.39 | **0.02** | ≥ 0.35 → **FAIL (collapse)** |
| TEST CAGR / DD | +5.4% / −16.3% | −0.9% / −16.8% | — |
| Full Sharpe | 1.11 | 1.07 | within 0.10 → PASS |
| Full DD / CAGR | −16.9% / +22.7% | −16.8% / +19.7% | — |
| Walk-forward Sharpes | +1.52 +1.06 +1.85 −0.60 (3/4) | +1.61 +1.01 +1.98 −0.86 (3/4) | no pos→<−5% flip → PASS |
| WF window returns | +33.5 +20.8 +35.2 −7.6% | +33.7 +17.2 +36.5 −10.3% | — |
| Slippage stress (2x, 0.25%/side) | FULL 1.06 / TEST 0.34 | FULL 1.01 / TEST −0.03 | — |
| Cross-asset (9 untuned) | 9/9 pos, median 0.65 | 9/9 pos, median 0.66 | ≥8/9 → PASS |
| DSR | 0.626 @97 | 0.577 @97 | ≥ baseline → **FAIL** |

Where the TEST collapse comes from (diagnostics, `results/phase15_diag.py`): mean TEST
exposure is nearly identical (0.171 vs 0.178; identical 101 in-market days — the signal
layer is untouched by construction), and turnover is the same (8.0 vs 7.8). The entire
TEST-split difference is concentrated in **July–August 2025** (−3.9% and −2.9% relative):
GK's lower vol reading sized differently through that specific rally/decline sequence, on
quantized steps that differ from cc30's on 27.5% of bars. With only ~101 in-market TEST
days, a two-month sizing accident of ±25%-step granularity dominates the whole split —
the TEST delta is a small-sample artifact of step quantization, not a systematic defect
of GK. But the pre-registered criterion is the criterion; it fails.

## 5. DSR table

| Series | DSR @ n_trials=97 (honest) | DSR @ n_trials=98 (pre-registered ref) | Bar |
|---|---|---|---|
| Champion baseline (cc30) | 0.6259 | 0.6245 | 0.95 |
| GK30 (trial #97) | 0.5774 | 0.5760 | 0.95 |
| EWMA (trial #98) | NOT RUN (sanity-gate stop) | — | — |

## 6. GK lookback plateau sweep 20–40 (reporting-only; reported variant stays 30d)

| Lookback | Full Sharpe | TEST Sharpe | Full DD | MC tail |
|---|---|---|---|---|
| 20 | 1.13 | 0.29 | −17.3% | 15.0% |
| 25 | 1.08 | 0.18 | −15.4% | 20.4% |
| 30 | 1.07 | 0.02 | −16.8% | 22.9% |
| 35 | 1.13 | 0.04 | −16.5% | 20.9% |
| 40 | 1.15 | 0.20 | −16.8% | 18.1% |
| **Average of all runs (Kaufman convention)** | **1.11** | **0.15** | — | **19.5%** |

Full-window Sharpe and MC tail are proper contiguous plateaus (1.07–1.15; 15–23%). TEST
Sharpe is NOT a plateau — it is a noise-dominated valley with the pre-registered 30d
sitting at its bottom (0.29 / 0.18 / 0.02 / 0.04 / 0.20). Read honestly, this says the
TEST-split ranking of GK lookbacks is statistical noise on ~101 in-market days — which
cuts both ways: the 30d TEST collapse is likely unlucky, but by the same token no GK
lookback shows a *reliable* TEST improvement either. The sweep average TEST Sharpe (0.15)
is still well under the baseline's 0.39. Per the pre-registration this sweep is
reporting-only and cannot rescue the verdict.

## 7. Cross-asset transfer (single sleeve per asset, unchanged parameters)

| | BTC | ETH | SOL | XRP | ADA | AVAX | DOT | LINK | BNB | pos | median |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cc30 | +1.24 | +0.65 | +0.97 | +0.43 | +0.80 | +0.61 | +0.17 | +0.59 | +1.13 | 9/9 | 0.65 |
| GK30 | +1.34 | +0.44 | +0.89 | +0.40 | +0.83 | +0.60 | +0.32 | +0.66 | +1.15 | 9/9 | 0.66 |

GK30 transfers exactly as well as cc30 — consistent with the estimators being 0.925
correlated and the mechanism (trend gate) being untouched.

## 8. Vol-target reconciliation: 40% here vs Kaufman's 6–8% (open priority #4 — CLOSED)

Kaufman (Ch.23) states 6–8% *annualized portfolio volatility* as the practical target
range for institutional, leveraged, diversified multi-asset futures portfolios. This
project uses `VOL_TARGET = 0.40` — but these two numbers are not the same quantity, and
the measured record shows the champion never ran anywhere near 40% portfolio vol:

- **The 40% is a per-asset scaling numerator, not a realized-vol target.**
  `scale = clip(0.40 / rv30, 0, 1)` with the clip at 1 (never leveraged), 25%
  quantization, and a 50% per-pair cap means 40% acts as a *de-risking knee*: full size
  whenever the asset's 30d vol is under 40%, scaled down proportionally above it. In a
  67%-median-vol asset class this is a volatility *cap*, not a volatility *goal*.
- **Measured portfolio-level realized vol of the champion** (from this session's baseline
  daily stream, 2020-01→2026-05): **20.3% annualized over the full period** (including
  flat days — the trend gate is out of the market 58% of days), **31.3% on in-market days
  only**; rolling 30d vol median 12.0%, 90th percentile 34.7%, max 60.3%.
- **Why not target 6–8% here**: Kaufman's portfolios reach 6–8% by (a) diversifying
  across dozens of low-correlation futures markets and (b) *leveraging* low-vol assets up
  toward target. This sleeve is long-only, unleveraged, in a single ~0.8-correlated
  crypto pair. Hitting 8% portfolio vol on assets with ~70% native vol would require
  holding ~10–12% exposure — below the 25% quantization step (it would round to 0 or 25%)
  and would shrink the expected 5–15% CAGR to roughly fee-level noise. The defensive
  variant already documented in `strategy_portfolio.md` (9-asset + 25% *portfolio-level*
  overlay) is the correct instrument for a lower-vol mandate, and it targets 25%, the
  practical floor for this asset class and step size.
- **Conclusion**: no contradiction and **no parameter change**. Kaufman's 6–8% is
  portfolio-realized-vol for leveraged diversified futures; this project's 40% is a
  per-asset de-risk knee whose realized portfolio outcome (20% full-period / 31%
  in-market) sits sensibly between crypto's native ~70% and institutional targets, given
  no leverage and a 2-asset universe. Documented here; priority #4 closed.

## 9. Verdict

**Trial #97 (Garman-Klass 30d): REJECT.** Promotion scorecard (all six had to hold):

1. MC P(MaxDD<−25%) ≤ 20%: **FAIL** — 22.9% (baseline 30.5%; directionally as predicted,
   ~25% relative tail reduction, but short of the pre-registered bar).
2. TEST Sharpe ≥ 0.35: **FAIL** — 0.02 (collapse concentrated in Jul–Aug 2025;
   quantization small-sample artifact, but the criterion is the criterion).
3. Full Sharpe within 0.10, no WF flip: PASS (−0.05; windows 3/4 both).
4. Cross-asset ≥ 8/9: PASS (9/9).
5. DSR ≥ baseline: **FAIL** (0.577 vs 0.626).
6. Plateau: PASS for full-window/MC-tail; TEST-split not plateau (noise valley).

**Trial #98 (EWMA λ=0.94): NOT RUN — zero-trial stop.** The refined sanity check showed
the hypothesis's mechanism (faster AND less noisy) is absent for EWMA at daily
granularity: it is faster in the mean but exactly as noisy as CC30 (0.95x std), with
*worse* sustained convergence (51 vs 47 bars). Spending the trial would have tested a
mechanism already known to be absent.

**Champion unchanged.** `best_strategy_so_far.py` / `TrendVolTarget.py` untouched.
Cumulative n_trials: **97**.

## 10. Lessons

1. **The estimator-efficiency literature claim is real and was reproduced** (GK noise
   0.37x CC at equal lookback), and it *did* translate into the predicted direction of
   tail improvement (MC tail 30.5% → 22.9%, median DD −22.7% → −21.5%). What it could
   not do is overcome the sizing layer's 25% quantization: most of the extra estimator
   precision is thrown away at the `round(scale/0.25)` step. The informative conclusion
   pre-registered for this outcome stands: **daily-bar sizing-latency/precision doesn't
   matter at this rebalance granularity.** The "improve the sizing input" direction is
   now closed cheaply — any future attempt must change the *granularity* (finer steps),
   which is a different (and fee-loaded) hypothesis, not an estimator swap.
2. **EWMA λ=0.94 on daily bars is not a noise-reduction device** — it only trades window
   shape for response speed at equal variance. RiskMetrics' λ was tuned for forecasting
   1-day-ahead vol, not for stable sizing levels. Measured, not assumed, before spending
   a trial: this is exactly what the sanity-check gate is for. First time in the project
   a pre-registered trial was cancelled by a synthetic-data gate at zero n_trials cost.
3. **TEST-split verdicts on ~100 in-market days are hostage to single episodes** (here
   Jul–Aug 2025, exactly as H-COT's verdict was hostage to a zero-overlap TEST split).
   With slow trend systems, the honest OOS sample grows only with calendar time — one
   more argument for the dry-run being the project's highest-value activity.
4. **Sanity-check design is itself failure-prone**: the first implementation (single
   seed, true-vol threshold) produced a wrong FAIL for the whole hypothesis. Multi-seed
   + own-asymptote measurement reversed it for GK and confirmed it for EWMA. Synthetic
   gates need the same statistical care as backtests, and both versions are documented
   in section 2.0 rather than silently replaced.
5. **Priority #4 (Kaufman vol-target reconciliation) is closed**: no contradiction; the
   champion's realized portfolio vol is 20.3% full-period / 31.3% in-market, and the 40%
   knob is a de-risk knee, not a realized-vol target (section 8).

Standing rule unchanged: **dry-run only, no real capital on backtest evidence.**

