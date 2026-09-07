# NEXT_TASK — A-021 / isolated Binance metrics sample acquisition

Assigned 2026-09-05 under the operator's autonomous research mandate. OPS only: zero strategy
evaluations and no changes to the frozen market-data tree. The previous T-040 assignment is
preserved below; its recorded disposition is REJECT on 2026-08-06 in `research_index.md`.

Scope: download the five BTCUSDT daily metrics ZIPs already probed in
`measurements/A021_binance_metrics_reachability.json`, plus their CHECKSUM files, to
`user_data/research/data/binance_metrics_a021/`. Use requests; save raw bytes before parsing;
refuse overwrites; record URL, fetch time, HTTP metadata and SHA-256; verify checksums and inspect
schema, timestamp gaps/duplicates and the last ten raw records. Run offline replay and guard tests.
Do not import strategy modules, compute outcome returns, change B2 or touch other recorders.
Continuous historical coverage and point-in-time validity remain unproven by five sample days.
Raw artifacts must enter a dedicated versioned record before acquisition is called complete.
No strategy trial or promotion is assigned here.

Extension assigned 2026-09-06: census all 1,096 calendar days in [2023-09-01, 2026-09-01)
for BTCUSDT metrics only, using a maximum of four concurrent downloads. Preserve each ZIP,
checksum and metadata before parsing in `binance_metrics_a021/history_20230901_20260901/`;
reuse existing verified sample files for overlapping dates. No date selection by returns and no
interpolation. Record every error/gap, field-null count, schema, and longest complete daily run.
The five-day samples are versioned in commit `f09e8d4ed`; the expanded census needs its own
versioned record after verification. Market timing, execution alignment and economic gates remain.

Derived-view extension 2026-09-06: the full raw census is now versioned in `b03e93705`.
Build an offline-only chronological OI view for the same full interval. Mark absent timestamps
explicitly; do not fill their measurements. Reject duplicate/off-grid/out-of-window timestamps.
Use a fixed 24-hour difference (288 five-minute steps), requiring 289 consecutive observations
with finite positive OI and OI value. Test invalid endpoints, bad interior observations, recovery,
sorting and future-data invariance. Preserve naive source timestamp labels; do not invent live
availability timestamps. No price returns, threshold search, trading decisions or strategy trials.
Save the derived view separately with source hashes and an eligibility report.

## Preserved prior assignment

# NEXT_TASK — T-040 / H-SemiVarSizing-1h

**Task ID**: T-040
**Program**: `perps`
**Cycle type**: RESEARCH
**Assigned**: 2026-08-05, Research Director
**n_trials before this cycle**: **0** (read from `research/research_metrics.md`, "Perps program — ACTIVE": `Perps n_trials | 0 of the 30-trial cap`)
**Trials this cycle will spend**: **at most 1.** Zero if any zero-cost pre-gate fails (P1–P3 below); exactly 1 if all pass and the single candidate variant is evaluated on TEST.

---

## Objective

Determine whether the volatility→exposure inversion that killed T-038 is a property of *volatility itself* on 1h perps, or an artifact of using a **total**-volatility estimator that sums an adverse (downside) and a favourable (upside) dispersion component.

---

## Hypothesis

**On 1h OKX perpetual bars, forward risk-adjusted returns of the nine-instrument equal-weight basket are DECREASING in trailing *downside* semideviation, even though T-038 measured them as INCREASING in trailing *total* volatility — and an exposure multiplier that cuts exposure as downside semideviation rises therefore improves the basket's risk-adjusted return net of its own turnover cost.**

The two claims are separable and are gated separately: P2/P2b test the sign and its significance; P3 tests whether the mechanism pays for the trading it requires.

---

## Scientific rationale

### The mechanism

For any window, the uncentered mean square of returns decomposes **exactly**:

```
(1/W)·Σ r_s²  =  (1/W)·Σ min(r_s,0)²  +  (1/W)·Σ max(r_s,0)²
              =        dsd²           +        usd²
```

A total-volatility conditioner therefore mixes two components. In a **long-only** book these have opposite economic signs: upside dispersion is mechanically co-incident with the rallies that generate the forward returns being measured, while downside dispersion is the component associated with forced deleveraging. On a leveraged perpetual venue the downside component is not merely "bad returns" — it is the observable signature of **liquidation cascades**, which are the defining structural feature of the instrument class (cascade begets cascade through forced margin liquidation, a mechanism with no spot analogue).

If the T-038 inversion is driven by upside contamination, then splitting the estimator restores the classic de-risking sign on the downside leg. If the inversion survives the split, volatility-conditioned de-risking is dead on 1h perps **for any trailing-dispersion estimator**, and the family can be closed on principle rather than on one estimator.

### Why T-038's own numbers implicate the estimator

T-038's harm census did not find a vol gradient. It found (Reviewer-confirmed, `research/review_briefs/T-038_brief.md`, "Observations"): quintile means **non-monotonic with Q3 the minimum**, realized quintile Sharpes Q1 **+0.6150** … Q5 **+2.8015**, and the Reviewer's summary "**Q4/Q5 carry everything**, not a vol gradient". A monotone conditioner that produces a non-monotone response is the signature of a conditioner mixing two signals. That is the claim under test.

### Grounding in the knowledge base

- `knowledge_base/12_portfolio_construction.md:72` — semivariance "doesn't need annualizing, and *has no agenda with respect to the profit patterns* — only penalizes drawdowns" (GASP objective function). This is precisely the property at issue: total volatility **does** have an agenda with respect to profit patterns in a long-only book.
- `knowledge_base/11_risk_management.md:184` — Sortino ratio; downside deviation as "the standard deviation of only the negative equity excursions" (Kaufman Ch.23).
- `knowledge_base/11_risk_management.md:185` — Ulcer Index, explicitly "a semi-variance-type measure" (Peter Martin 1987).
- **The counter-argument, cited because it argues against this hypothesis**: `knowledge_base/11_risk_management.md:106` — Kaufman's own caveat that "using only drawdowns discards the information that unusually large *profits* can also indicate elevated risk; with limited data, using the full (gain+loss) distribution is more robust". This cycle is a direct empirical test of that disagreement on 1h perps, and the 1h sample is not the "limited data" case Kaufman conditions the caveat on.

---

## Expected regime(s)

**Should work in**: drawdown and deleveraging regimes where dispersion is downside-dominated — 2022H2, the 2025H1 negative half-year (which is the VAL split), any liquidation-cascade episode.

**Should fail in**: sustained melt-ups where dispersion is upside-dominated. **State this plainly: the TEST split (2025-04-22 … 2025-09-19) is a rally — the manual records it as the 74.5th percentile of rolling 151-bar windows and second-best of six non-overlapping blocks** (`PROJECT_OPERATOR_MANUAL.md`, "Calibration for Directors"). A de-risking overlay gives up return in exactly that regime. **The candidate may therefore fail promotion criterion 3 while the mechanism is real.** The scientific content of this cycle is in the pre-gates, which run on TRAIN+VAL at 1h resolution; the TEST evaluation is the promotion formality and, per criterion 7 below, cannot exceed PARK regardless.

---

## Zero-cost pre-gate ladder

**All three pre-gates run on TRAIN+VAL 1h bars ONLY. No pre-gate may read a bar dated after `2025-04-21 23:00 UTC`. Failing any pre-gate STOPS the cycle with a rejection and spends ZERO trials** (`PROJECT_OPERATOR_MANUAL.md`, "Research budget": "A cycle killed at a pre-gate spends ZERO trials — no variant was evaluated, so none is counted").

Run in order. Stop at the first failure.

### Definitions (all causal; every quantity at bar `t` uses only bars `≤ t`)

Per instrument `i`, on 1h futures bars:

```
r[i,t]    = close[i,t] / close[i,t-1] - 1
W         = 168                                   # 7 days, pre-registered, not tuned
dsd[i,t]  = sqrt( (1/W) * sum_{s=t-W+1..t} min(r[i,s], 0)^2 )        # PRIMARY conditioner
usd[i,t]  = sqrt( (1/W) * sum_{s=t-W+1..t} max(r[i,s], 0)^2 )        # diagnostic only
sd [i,t]  = sqrt( (1/W) * sum_{s=t-W+1..t} (r[i,s] - rbar[i,t])^2 )  # diagnostic only, population std
```

Forward 24-bar per-unit-risk return (the P2 response variable):

```
fwd_ret[i,t] = close[i,t+24] / close[i,t] - 1
fwd_vol[i,t] = population std of { r[i,s] : s = t+1 .. t+24 }
fwd_pur[i,t] = fwd_ret[i,t] / fwd_vol[i,t]     # undefined if fwd_vol == 0 -> drop the bar, report the count
```

**Warmup rule (binding — standing directive 8).** `dsd`, `usd`, `sd` and the forward variables are computed over the **FULL 1h series from each instrument's first available bar**, and the TRAIN/VAL slice is taken **afterwards**. Do NOT recompute indicators inside a split. Every archived TEST/walk-forward figure in this project predating 2026-07-31 used truncated warmup and was thereby depressed (BTC 1d SMA200 TEST Sharpe −1.2159 → +0.2129 once fixed); this is the same defect.

**Forward-window trim (binding — adopted from the T-039 Reviewer audit).** Trim the last **25** bars (`max(h) + 1 = 24 + 1`) from the TRAIN+VAL slice before selecting census anchors, so that no `fwd_*` window can read a bar at or beyond `val_end`. T-039 used a literal 24 and its `fwd_24` read one TEST bar per instrument; the Reviewer's instruction was "Next census: trim `max(h)+1`". Use 25.

---

### P1 — Persistence of the conditioner

Downside semideviation must be forecastable at 1h, or no causal multiplier built on it can work.

- Compute, per instrument, the Spearman rank correlation `rho[i] = spearman( dsd[i,t] , forward 24-bar realized downside semideviation )`, where the forward quantity is `sqrt( (1/24) * sum_{s=t+1..t+24} min(r[i,s],0)^2 )`.
- Report all nine `rho[i]`, their median and their minimum.

**Thresholds (carried over verbatim from T-038's P1, which passed at median 0.564373 / min 0.434160):**

**KILL if** `median(rho) < 0.30` **OR** `min(rho) <= 0.15`.

**What would make P1 pass without the mechanism**: any autocorrelated series passes a persistence test. **P1 is a necessary condition, not evidence of the hypothesis, and may not be cited as support for it.** It exists only to kill the cycle cheaply if the conditioner is unforecastable.

---

### P2 — Harm census on the PRIMARY conditioner (this is where the science is)

- Restrict to TRAIN+VAL bars (after warmup and the 25-bar trim).
- **Within each instrument**, assign every bar to a quintile of `dsd[i,t]`, with the quintile thresholds estimated **on that instrument's TRAIN+VAL bars only**. Q1 = lowest `dsd`, Q5 = highest.
- Per instrument, compute `D[i] = mean(fwd_pur | Q1) - mean(fwd_pur | Q5)`.
- **Primary statistic**: `D_bar = (1/9) * sum_i D[i]` — an equal weight across instruments, so that an instrument with more bars cannot dominate.
- **Breadth**: `B = count of i where D[i] > 0`, out of 9.

**KILL if** `D_bar <= 0` **OR** `B < 5`.

These are the **same two KILL clauses T-038 used**, unchanged in form, so the two cycles are directly comparable on sign and breadth. T-038 measured `Q1-Q5 = -0.442905` (`-0.438872` under the resolution-aware boundary re-run) with breadth **1 of 9**, and both clauses fired.

**Note on comparability, stated so it is not overclaimed**: T-038 used an **EWMA** estimator and this cycle uses a **168-bar rolling window**, and this assignment specifies `fwd_pur` explicitly rather than inheriting T-038's formula. The KILL clauses are therefore carried over as **sign and breadth conditions**, which are estimator-independent; T-038's numeric `-0.442905` is quoted as context, **not** as a value this cycle's statistic is numerically comparable to.

**Mandatory diagnostics, REPORTED and NON-GATING** (they are the decomposition that makes the cycle informative whichever way it goes). Recompute `D_bar` and `B` identically for:

- **(a)** `sd[i,t]` — total volatility on the matched 168-bar window. **Expected sign: negative** (this is T-038's finding on a matched window). If it comes out positive, the two cycles disagree on the same data and the Engineer must say so loudly in the report rather than proceeding quietly.
- **(b)** `usd[i,t]` — upside semideviation. **Expected sign: strongly negative** if the contamination hypothesis is right.

**Only `dsd` gates.** (a) and (b) are diagnostics, so there is no multiplicity to correct at this step.

**Robustness views on the primary statistic (reported, non-gating)** — adopted from T-038 Engineer recommendation 5, which found these more informative than a bootstrap CI: `D_bar` recomputed per calendar year, and on three disjoint sub-windows of TRAIN+VAL of equal bar count. Report the sign in each. A statistic that flips sign across years is a warning even when the pooled figure passes, and must be stated as such.

**What would make P2 pass without the mechanism?** Three candidate artifacts, and why each is excluded as specified:

1. *Volatility clustering raising Sharpe mechanically.* Excluded: the response variable `fwd_pur` is **already normalised by realised forward volatility**, so a change in forward dispersion divides out. This is why T-038 chose a per-unit-risk response, and it is why T-038 was able to detect an **inversion** rather than a construction artifact.
2. *In-sample quintile thresholds.* Excluded from gating: thresholds are estimated per instrument on TRAIN+VAL and the response is a **forward** quantity, so threshold estimation cannot see the response.
3. *Selection across variables/horizons.* Excluded by construction: **one** pre-registered conditioner, **one** pre-registered horizon, **one** pre-registered response. There is no scan. P2b prices what remains.

---

### P2b — Circular-shift null control (single pre-registered statistic — **NOT a family-wise correction**)

Standing directive 12 requires that "any census-style scan must carry a family-wise control built the same way; a max cell reported without one is not evidence." T-039's placebo **changed that cycle's verdict**, and this pre-gate exists so that P2's `D_bar` is reported against its own null rather than against zero.

**What this control is and is not — read this before coding it, and transcribe the distinction into the report.** P2 tests **one** pre-registered conditioner, **one** horizon, **one** response (see "What would make P2 pass without the mechanism", point 3). **There is no family here**, so a max-statistic over a family of one is simply the statistic itself, and no multiplicity correction is occurring. Calling this control "family-wise" would imply a correction that is not being applied.

What it genuinely does is price the **autocorrelation and volatility-clustering structure that the circular roll preserves**: `D_bar` is a difference of conditional means on a strongly autocorrelated conditioner over overlapping forward windows, so its null distribution is **not** the textbook one and cannot be assumed centred with a known variance. That is the value of this control, and it is sufficient reason to run it.

**Consequences that must be stated explicitly in the report:**

- **This cycle carries NO multiple-testing protection beyond its single pre-registration.** The protection is that the conditioner, horizon, response, thresholds and seeds were all fixed in this file before any of them was computed — nothing more.
- **A follow-on construct built on this cell inherits ONE test, not 72.** This is the material difference from T-039's cells, where the T-039 Reviewer recorded that "reviving one inherits 72 tests, so `n_trials=1` is a multiple-testing violation." No such debt attaches here. A future Director may build on a passing `dsd` result at `n_trials` incremented by 1.

- **1,000 draws. Pre-registered seed: `20260805`.** `n_draws` and the seed may NOT be changed after seeing a result.
- Per draw: sample **one shared integer offset `k`**, uniform on `[168, N_min - 168]` where `N_min` is the smallest per-instrument TRAIN+VAL bar count. Apply the **same `k` to all nine instruments** (T-039's construction — it preserves cross-sectional alignment, which an independent per-instrument shuffle would destroy).
- **Circularly roll the conditioner series `dsd[i,·]` by `k` and leave the forward-return series in place.** Then **re-estimate the quintile thresholds on the rolled series** and recompute `D[i]` and `D_bar` exactly as in P2. Call the result `M_draw`.
- Report `mean(M)`, `sd(M)`, `P95(M)`, `P99(M)`, and the **empirical one-tailed p-value** `p = share of draws with M_draw >= D_bar`.

**KILL if** `p > 0.05`. **The kill is one-tailed by design — the hypothesis is directional** (it predicts `D_bar > 0`, that low-downside-dispersion bars have better forward per-unit-risk returns). A large negative `D_bar` is not a pass; it is the T-038 inversion recurring, and F2 catches it first.

Report the P95 comparison **and** the empirical p-value. T-039's report gave only the P95 comparison, which read as a near miss, while the percentile showed an ordinary null draw (p = 0.221) — the Reviewer had to add it. Give both.

**Additionally REPORT, NON-GATING** (so the Reviewer can confirm the null behaves as it should rather than taking the one-tailed number on trust):

- the **two-tailed empirical p-value**, `share of draws with |M_draw| >= |D_bar|`;
- the **full distribution of `M_draw`** — minimum, P1, P5, P25, median, P75, P95, P99, maximum, plus the raw draw vector saved as a raw artifact;
- an explicit **sign-symmetry check**: the share of draws with `M_draw > 0`, and the median of `M_draw`. **The null is expected to be centred near zero**; a null centred materially away from zero means the roll is not destroying the association it is supposed to destroy, and the Engineer must say so rather than reporting the one-tailed p as if it were interpretable.

**Two mandatory sanity assertions** (`PROJECT_OPERATOR_MANUAL.md`, "Zero-cost pre-gate ladder", lesson 20 — a suspiciously clean diagnostic is a bug signal):

- assert `sd(M) > 0` — a degenerate null means the roll is not doing anything;
- assert that on draw 1 the rolled conditioner differs from the unrolled conditioner for **all nine** instruments, and that `M_draw != D_bar`.

A failed assertion is a **stop condition**, not a warning to route around.

---

### P3 — Cost-admissibility REQUIREMENT (a gate on proceeding — **NOT a falsification condition**)

The mechanism must pay for its own turnover at 18.0 bps per round trip.

**Status of this gate, stated up front because it governs how the result may be written up.** P3 is a **requirement for proceeding to the trial**, not a test of the hypothesis. Failing it stops the cycle at **zero trials**, exactly as a falsification would — but it is **not** one of the falsification conditions and it produces **no evidence about the hypothesis in either direction**. The reason is in "What would make P3 pass without the mechanism?" below: a de-risking multiplier raises Sharpe on any volatility-clustered series whether or not the hypothesised relationship exists, so listing it alongside the real conditions would present a hurdle that a mechanism-free construct clears almost automatically. The falsification statement is **F1 OR F2 OR F3** and P3 appears in none of them.

**Basket construction (must match the committed benchmark's rule, at 1h):** equal-weight LONG basket of the nine instruments; weights reset to `1/9` at the close of the **last 1h bar of each calendar month** (never on the final bar of the window); turnover cost on a rebalance is `per_side_cost("taker") * sum_i |w_target,i - w_drift,i|`; the initial entry is the same formula with `w_drift = 0`. This rule is stated in the header of `user_data/research/perps_benchmark.py` — read it there and reuse it; do not invent a second construction. Call the resulting 1h net return series `b[t]`.

**Multiplier:**

```
dsd_basket[t] = sqrt( (1/168) * sum_{s=t-167..t} min(b[s], 0)^2 )
target        = median( dsd_basket[t] ) over TRAIN ONLY (bars <= 2024-11-22 23:00 UTC)
m_raw[t]      = clip( target / dsd_basket[t], 0.25, 1.00 )
m[t]          = m_raw[t] quantized to the nearest of {0.25, 0.50, 0.75, 1.00}
```

- **Upper bound 1.00 is binding: this construct takes NO leverage.** It de-risks only.
- **`target` is calibrated on TRAIN only** — not TRAIN+VAL, not full-sample. A median over a window that includes VAL would leak.
- The 0.25 quantizer is **not a parameter under test**. It is the project's established setting; the sleeve-sizing-refinement family is CLOSED in both directions (`knowledge_base/hypothesis_bank.md` FAMILY STATUS LEDGER: "Sleeve sizing refinement (estimator quality AND rebalance granularity) | CLOSED"), with the finding that the 25% step functions as a protective no-trade band. Do not tune it.

**Application and cost (2-bar lag, matching `validator.signal_to_returns`'s documented convention):**

```
o[t] = m[t-2] * b[t]  -  |m[t-2] - m[t-3]| * per_side_cost("taker")
```

**REQUIREMENT TO PROCEED: `Sharpe(o) > Sharpe(b)` over TRAIN+VAL** (both per-period on 1h bars; annualise with `bars_per_year = 8760` if reporting annualised, and say which you are quoting). **If `Sharpe(o) <= Sharpe(b)`, STOP the cycle at zero trials** — the overlay does not pay for its own turnover, so there is nothing to evaluate on TEST. Record this in the verdict as **"cost-admissibility requirement NOT met"**, and **not** as a falsification of the hypothesis: P1/P2/P2b may well have passed, and if they did, that finding stands on its own and must be reported as such.

**Report** (non-gating): `sum |Δm|`, the count of multiplier changes, implied total turnover cost in bps over the window, mean `m`, and the share of bars at `m = 1.00`. For scale, T-038's overlay produced **249 exposure changes** and `Σ|Δm| = 30.207` on its census window.

**What would make P3 pass without the mechanism?** **This one genuinely can pass without the mechanism, and that is why it does not gate the science.** A de-risking multiplier holds less exposure in high-dispersion bars, which lowers realised volatility more than mean return on any volatility-clustered series, and therefore raises Sharpe **whether or not the hypothesised relationship exists**. **P3 is a cost-admissibility check ONLY. It may not be cited anywhere in the report as evidence that the mechanism exists.** The evidence is P2 and P2b. Write that sentence into the report.

**Frequency diagnostic (reported, NON-GATING, NOT a variant, NOT evaluated on TEST):** recompute the P3 quantities with the quantizer removed (continuous `m_raw`), reporting turnover, change count, and TRAIN+VAL net Sharpe. This exists solely to tell the next Director whether the mechanism extends to a higher-frequency implementation. It may not be promoted, may not be evaluated on TEST, and does not count against the variant budget.

---

## Falsification statement

**This hypothesis is REJECTED if AT LEAST ONE of F1, F2, F3 fires.** Transcribe each into code literally: the top-level connective is **OR**; the connectives inside each clause are as written. (`PROJECT_OPERATOR_MANUAL.md`, "Falsification conditions must be transcribed literally": "at least one of" is `or`, "both" is `and`; substituting one for the other is a spec deviation **even when the verdict is unchanged**.)

- **F1** — `median(rho) < 0.30` **OR** `min(rho) <= 0.15`.
- **F2** — `D_bar <= 0` **OR** `B < 5`.
- **F3** — `p > 0.05`, where `p` is the one-tailed empirical share of the 1,000 null draws with `M_draw >= D_bar`.

**There is no F4.** P3's cost-admissibility requirement is deliberately **not** a falsification condition — it can be satisfied by a mechanism-free construct (see P3), so including it as an OR clause would manufacture the appearance of a fourth hurdle. It gates proceeding to the trial; it does not bear on whether the hypothesis is true.

If F1, F2 and F3 all fail to fire **and** the P3 cost-admissibility requirement is met, proceed to the trial. **Stopping at F1, F2, F3, or at the P3 requirement, spends ZERO trials and `n_trials` stays 0.**

**Verdict-section requirement.** The report's verdict section must state, as two separate items:

1. **which of F1, F2, F3 fired** (naming each by number, with its computed value against its threshold), or that none did; and
2. **separately, whether the P3 cost-admissibility requirement was met**, with `Sharpe(o)` and `Sharpe(b)`.

Do not merge them into a single pass/fail line. A cycle that passes F1–F3 and then stops at P3 has produced a **positive finding about the mechanism together with a negative finding about its tradeability**, and collapsing the two would lose the more valuable half.

**If any falsification condition above is ambiguous when you go to code it: BLOCK, quote the exact sentence, and stop.** Do not choose an interpretation, do not pick the conservative one, do not note it and proceed (`PROJECT_OPERATOR_MANUAL.md`, "Where a condition is genuinely ambiguous, the Engineer BLOCKS and quotes the sentence").

---

## Prior-work check

### Adjacency and escape

**T-038 / H-BasketVolTarget-1h (REJECT at pre-gate P2, 2026-08-01) — the direct parent.** Same layer (exposure sizing on the nine-perp basket), same sample, same KILL-clause structure. This cycle escapes T-038's failure mode by changing the **functional form** of the conditioner on the exact axis T-038's own decomposition implicates — not its window, not its decay parameter. **Standing directive 10 requires this statement explicitly** ("any construct reducing exposure as trailing volatility rises must state why it escapes this before being assigned"), and here it is:

> T-038 conditioned on **total** realised volatility, which is exactly `sqrt(dsd² + usd²)`. In a long-only crypto book the `usd` component is mechanically co-incident with the rallies that produce the forward returns being measured, so a total-vol conditioner mixes an adverse component with a favourable one. T-038's own result is consistent with that reading and not with a vol gradient: quintile means non-monotonic, Q3 the minimum, "Q4/Q5 carry everything". Conditioning on `dsd` alone is a **different functional**, not a re-parameterisation. **And the escape is falsifiable in this cycle**: if `dsd` also inverts, the construct dies at F2 and directive 10 generalises from "total volatility" to "any trailing-dispersion estimator on 1h perps", which closes the family on principle.

**T-039 / H-IntradayEdgeFloor-1h (REJECT at pre-gate, 2026-08-04) — adjacent, and deliberately not built upon.** The family T-039 closed is "**Intraday 1h univariate decile-conditioned ENTRY on OHLCV+volume**, measured as conditional-mean differences". This cycle is outside it on all three counts: it is an **exposure/sizing overlay with no entry signal**, its response is **forward per-unit-risk return** rather than a conditional mean return, and its conditioner is not one of T-039's six variables.

**Critically — this cycle does NOT build on T-039's `vol_ratio` h=24 BOT cell, and must not be reported as doing so.** The T-039 Reviewer's warning is binding: "reviving one inherits **72 tests**, so `n_trials=1` is a multiple-testing violation." The lineage of this hypothesis is **T-038's single pre-registered construct plus its Engineer's recommendation 1**, both of which predate T-039's census. T-039's `vol_ratio` finding may be cited in the report as **corroborating context only**, explicitly labelled as such, and may not appear in any selection or threshold argument.

### Engineer recommendations — every one dispositioned

**From `research/review_briefs/T-038_brief.md`:**

1. *"A semivariance/downside-deviation variable is structurally different and its P2 census is cheap (same script, bucketing swapped) — worth one pre-gate, killed fast if negative."* — **ADOPTED IN FULL. This recommendation is the cycle.**
2. *"The 1h sample is worth using: 20,370 census bars resolved this where 151 daily could not."* — **ADOPTED**; the decisive measurement is at 1h.
3. *"Fix the hourly boundary before assigning another 1h cycle."* — **ALREADY DISCHARGED** (resolution-aware boundary, 2026-08-02, `5cbd7617a`). This assignment depends on it and requires the 151-date assertion at the trial step.
4. *"The inverted construct (scale UP in high vol) looks good in-sample for the same reason — a trap, untestable without a crash-sample pre-gate."* — **ADAPTED, not rejected. The naive sign-flip is NOT being assigned.** The Engineer's trap is that the apparent edge lives in a few extreme bars rather than in a gradient; the `dsd`/`usd`/`sd` decomposition diagnoses exactly that, and P2b prices it against a null. If the Engineer still judges the trap unaddressed after seeing P2's diagnostics, say so in the report.
5. *"Per-year and disjoint-window views beat the bootstrap CI."* — **ADOPTED** as P2's mandatory robustness reporting; no bootstrap CI is requested.

**From `research/review_briefs/T-039_brief.md`:**

1. *Close intraday entry at real rates recording the per-horizon edge/cost table.* — Reviewer bookkeeping, already in `research_metrics.md`. No action.
2. *State the closure boundary.* — Done by the Reviewer in the family ledger; this assignment respects it (see above).
3. *`vol_ratio BOT` as a measured-but-not-harvestable bank paragraph.* — Reviewer bookkeeping. Not mine to write.
4. *"Kill early: any construct at h ≤ 4."* — **ADOPTED**; see the directive-11 statement below. This construct holds continuous exposure and its multiplier changes on a multi-day cadence, so h ≤ 4 does not arise.
5. *"Rolling-percentile conditioners rather than level cuts; level cuts expire."* — **PARTIALLY ADOPTED.** `target` is a TRAIN **median** of the conditioner (a distributional anchor) rather than an absolute level, which is the remedy for the `illiq TOP` TEST-absence pathology T-039 found. It is not a rolling percentile — a rolling anchor would make the multiplier's calibration drift through the split and is not assigned.
6. / 7. *A-009 (funding history) and A-010 (1h coverage).* — Ops tasks, **already filed** in `research/OPS_BACKLOG.md`. Not re-filed. See Environment notes for the Director's confirmation that funding is unusable this cycle.

### Alternatives considered and set aside this cycle

- **Funding-rate carry / crowding** — the perp-native axis, and it would have been the first choice. **Dead on data**: the held funding series cover **2026-02-26/28 → 2026-05-28** only (266–273 records per instrument), which has **zero overlap** with the frozen window ending 2025-09-19. A-005 recorded the same fact. Blocked pending A-009; assigning it would require data acquisition, which a research cycle may not do.
- **Mark-price premium `(close − mark)/mark` as a 1h microstructure conditioner** — set aside under selection rubric 2 (cost-aware). Director read-only measurement this session over TRAIN bars: per-bar premium standard deviation **1.13–3.43 bps** across six instruments, p5–p95 span roughly **±1 to ±3.4 bps**. The entire dispersion of the axis is under one fifth of a single 18.0 bps round trip. Recorded here so a future Director need not re-derive it; see Environment notes for provenance.
- **Rebalancing-frequency / diversification-return harvesting on the benchmark basket** — a genuine structural mechanism and a good fit for the frequency goal, but criterion 3 requires a ~10% improvement in TEST Sharpe, and changing rebalance cadence alters the portfolio's drift term only marginally while adding turnover that scales with frequency. Parked as a candidate for a later cycle rather than assigned.

---

## Standing-directive compliance statements

- **Directive 8 (warmup).** This assignment does not cite the OOS-collapse conclusion, the 1.2–1.3 Sharpe ceiling, or the champion's TEST Sharpe 0.41 as evidence. The warmup rule itself is imposed as binding above.
- **Directive 9 (state the primary metric's expected SE before assigning).**
  - **Pre-gate metric (where this cycle's science is):** the P2 census runs on pooled 1h TRAIN+VAL bars. T-039 measured **251,946** pooled TRAIN+VAL 1h bars on these same nine instruments and this same window; this census will be marginally smaller after the 168-bar warmup and 25-bar trim, and the Engineer must report the exact count. The manual records pooled 1h as giving **SE ≈ 0.161** on an annualised Sharpe (338,933 bars, full series). This sample **can** resolve the claimed effect.
  - **Trial metric:** TEST-split Sharpe on **151 daily bars**, which carries **SE 1.555** annualised (directive 9, quoting the manual). Per-period, one SE is ≈ `1/sqrt(151)` ≈ **0.081**, while criterion 3's margin over the benchmark is `0.135653 − 0.123321 = 0.012332` — about **0.15 of one SE**. **The TEST split cannot statistically separate this candidate from the benchmark, and is not being asked to**: criterion 3 is a **ratio** bar, not an SE gate, precisely for this arithmetic reason (`PROJECT_OPERATOR_MANUAL.md`, "Why criterion 3 is a ratio and NOT a standard-error gate"). Report the SE and t; do not gate on them.
- **Directive 10 (volatility inversion).** Escape statement given in full in the prior-work check above. The construct **does** reduce exposure as a trailing dispersion measure rises, and the escape is falsifiable within this cycle at F2.
- **Directive 11 (state expected per-trade gross edge vs round-trip cost before assigning any construct holding under 8 hours).** **This construct does not hold positions under 8 hours.** It holds continuous long exposure in the basket and modulates its size; the quantized multiplier changed **249 times** in T-038's comparable census window, a multi-day cadence. The relevant cost is therefore **turnover cost, not per-trade entry edge**, and it is gated explicitly at P3 against `per_side_cost("taker") = 9.0 bps/side`. T-039's h ≤ 8 cost wall (best gross edge 16.1349 bps vs an 18.0 bps round trip, **0.90×**) does not bind on a construct with no entry signal — but if the Engineer finds the multiplier changing more often than daily, P3's turnover figure is the number that decides it, and that must be stated in the report.
- **Directive 12 (census-style scans must price their own width).** **This cycle is not a census-style scan** — one conditioner, one horizon, one response — so the directive's family-wise requirement has no family to correct over. It is nonetheless honoured in substance by P2b: 1,000 draws, shared offset, thresholds re-estimated per draw, empirical p reported alongside P95, plus the two-tailed p and the null's sign symmetry. **P2b is explicitly NOT a family-wise correction and must not be described as one** (see P2b). The width this cycle has to price is one.
- **Directive 13 (do not carry a daily-bar finding to 1h without re-testing it).** Nothing daily is carried. The Kaufman/Sortino grounding is a *mechanism* citation, not a transferred empirical result, and it is being tested at 1h from scratch — including the counter-argument at `11_risk_management.md:106`.

### Target frequency — stated honestly

The operator's goal is a bot that trades multiple times per day. **The primary construct does not meet that goal**: on T-038's comparable window the quantized multiplier changed 249 times, a multi-day cadence. It is assigned under the envelope's explicit exception — *"constructs trading less often are acceptable only when they test a mechanism that plausibly extends to higher frequency"* — because the conditioner is defined at **every 1h bar** and it is the 0.25 quantizer, not the mechanism, that suppresses turnover. The continuous-multiplier diagnostic in P3 measures exactly that extension and hands the number to the next Director. This construct is **not** proposed as an end state.

---

## Deployment envelope

| Dimension | Constraint |
|---|---|
| Venue | OKX USDT perpetual swaps, regular (non-VIP) fee tier |
| Config | `user_data/config_perp.json` — `"trading_mode": "futures"`, `"margin_mode": "isolated"`, `"dry_run": true`, `"fee": 0.0009` |
| Instruments | Exactly the nine in that config's `pair_whitelist`: `BTC/USDT:USDT`, `ETH/USDT:USDT`, `SOL/USDT:USDT`, `BNB/USDT:USDT`, `XRP/USDT:USDT`, `ADA/USDT:USDT`, `AVAX/USDT:USDT`, `DOT/USDT:USDT`, `LINK/USDT:USDT`. **No others.** |
| Timeframe | **1h** for the construct and all pre-gates; the TEST return series is aggregated to daily for the criterion-3 pairing (see Split specification) |
| Fill assumption | **`taker`.** `maker_optimistic` is permitted only as a clearly-labelled secondary comparison and **may NEVER be the basis of a promotion** |
| Leverage | **None. The multiplier is capped at 1.00.** |

**Cost model — quoted from `PROJECT_OPERATOR_MANUAL.md`, "Execution and cost model". The single source of truth is `COST_MODEL` in `user_data/research/validator.py`; resolve every cost through `per_side_cost()` / `round_trip_cost()` and never hardcode one:**

| Component | Value |
|---|---|
| maker fee | 2.0 bps/side |
| taker fee | 5.0 bps/side |
| slippage | 3.0 bps/side (estimate, uncalibrated) |
| spread | 2.0 bps quoted; a taker crosses half = 1.0 bps/side (estimate, uncalibrated) |
| **taker all-in** | **9.0 bps/side, 18.0 bps round trip** |

**No backtest may run without explicit costs.** A run that inherits a default fee, or hardcodes a cost number anywhere, is void.

**Return envelope — any result above 100% CAGR is presumed defective, not impressive.** Treat it as a bug report until re-verified, and state in the report that you did, in this order: (1) costs actually applied — not defaulted, not zero; (2) signal lag — `validator.signal_to_returns`'s 2-bar convention; (3) indicators computed over the full series before splitting; (4) survivorship. A result surviving all four is reported *with* that verification; one unchecked is not reportable. **No target return or drawdown band is stated here because no project file defines one.**

---

## Data

**All inputs exist and are manifest-covered. This cycle may NOT create, modify, delete, download or rebuild anything under `user_data/data/`, and may NOT rebuild `user_data/data/MANIFEST.json`. A cycle whose git diff touches `user_data/data/` is INVALID and the Reviewer rejects it on that basis alone without assessing the hypothesis.**

| Path | Contents | Confirmed |
|---|---|---|
| `user_data/data/okx/futures/{BTC,ETH,SOL,BNB,XRP,ADA,AVAX,DOT,LINK}_USDT_USDT-1h-futures.feather` | 1h futures OHLCV — the sole input to every pre-gate and to the candidate | Yes — verified present 2026-08-05; 38,612 bars each for seven instruments, BTC 38,587, BNB 30,062 (starts 2022-12-23) |
| `user_data/config_perp.json` | whitelist, futures/isolated, `fee` 0.0009 | Yes |
| `research/benchmarks/perps_equal_weight_benchmark_TEST_returns.csv` | the benchmark's per-bar TEST return series, for criterion 3 pairing | Yes — 175 physical lines including comment header |
| `research/benchmarks/perps_equal_weight_benchmark.md` | full benchmark record | Yes |
| `user_data/research/perps_benchmark.py` | the **authoritative basket-construction rule** — read its header and reuse the rule | Yes |
| `user_data/research/validator.py` | `COST_MODEL`, `per_side_cost`, `round_trip_cost`, `split_by_dates`, `assert_no_holdout`, `holdout_boundary`, `signal_to_returns`, `metrics`, `extract_trades`, `monte_carlo`, `mc_gate_status`, `deflated_sharpe`, `sharpe_difference_se`, `append_trial`, `walk_forward`, `yearly_breakdown` | Yes |
| `research/trial_sharpe_ledger.csv` | **0 data rows** (1 header + 50 comment lines) | Yes |

**Not to be used this cycle**: `*-1h-funding_rate.feather` (coverage 2026-02-26 → 2026-05-28, zero overlap with the window — see Environment notes) and `*-1h-mark.feather` (set aside on magnitude grounds; BTC mark is in any case only 7,810 bars against 38,587 OHLCV bars).

**`scripts/data_manifest.py verify` failing mid-cycle is a STOP condition, not an obstacle to route around. Never run `build` to clear it. `FREQTRADE_SKIP_DATA_VERIFY=1` invalidates the cycle** — a run with the check bypassed is not evidence and may not appear in a report, a verdict, or a promotion argument.

---

## Split specification

**The perps split triple is FROZEN and is not yours to change. Pin by literal date, never by fraction** (`split_70_15_15()` is deprecated and warns — use `validator.split_by_dates`):

```
train_end  2024-11-22
val_end    2025-04-21
test_end   2025-09-19
```

**A candidate evaluated on different split dates is VOID against the program benchmark — not weaker evidence, VOID** — because criterion 3 requires date-identical TEST overlap.

**Reserved holdout (program-scoped): bars strictly after `2025-09-19` UTC.** No training, validation, parameter selection, or pre-gate screening may touch a holdout bar. `validate()` RAISES `HoldoutViolation` if its input contains any; it does not trim them. Exclude them explicitly.

**Sub-daily boundary resolution (binding, 2026-08-02).** A series ends on the boundary **calendar date with its last complete bar included**: inclusive instant = `date + 1 day − one bar interval`. For perps, **1d → 00:00, 1h → 23:00**. Use `validator.holdout_boundary(program, freq=...)` and the resolution-aware `assert_no_holdout` / `split_by_dates`; do not hand-roll a midnight `Timestamp`. Under the old midnight reading T-038's 1h TEST slice spanned **152** UTC dates against the benchmark's **151**, which made criterion 3 **VOID for any 1h candidate** — a harness artifact, and the reason this paragraph exists.

**Criterion-3 pairing procedure (mandatory, and assert it):**

1. Produce the candidate's **1h** net return series on the TEST split.
2. Compound within each UTC calendar date to a **daily** net return series.
3. **Assert the daily series has exactly `N = 151` bars and that its dates are element-wise identical to those in `research/benchmarks/perps_equal_weight_benchmark_TEST_returns.csv`.** A mismatch is a **stop condition** — report it and BLOCK; do not reindex, do not trim, do not fill.
4. Pair against the benchmark series for criterion 3 and for `validator.sharpe_difference_se()`.

**Harness reconciliation check, run BEFORE the trial** (Director-set threshold — the manual defines none; recorded in Environment notes): aggregate the **un-overlaid** 1h basket `b[t]` to daily over TEST and compare against the committed 1d benchmark series. Report the Pearson correlation and the difference in TEST Sharpe. **If the correlation is below 0.99, STOP and BLOCK** — the 1h basket construction does not reproduce the committed benchmark and no candidate figure built on it would be interpretable.

---

## Required validation (only if all pre-gates pass)

Every gate below is mandatory on the single candidate variant. Thresholds are quoted from `PROJECT_OPERATOR_MANUAL.md`.

1. **Walk-forward** — `validator.walk_forward`, rolling windows over the TRAIN+VAL region. Never optimize and evaluate on the same period. Report per-window Sharpe and the count of positive windows. *(Benchmark context: the committed benchmark is WF-positive in **1 of 4** windows.)*
2. **Out-of-sample** — final evaluation exclusively on the TEST split. Hyperopt must never touch it; no hyperopt is assigned this cycle.
3. **Market-regime testing** — `validator.yearly_breakdown`; report per calendar year and combined: Return, CAGR, Sharpe, Deflated Sharpe, Sortino, Calmar, Profit Factor, Max Drawdown, Win Rate, Number of Trades, Average Trade, Expectancy.
4. **Trade-count validation** — report the number of multiplier changes and the number of distinct exposure episodes on TEST. **State explicitly whether the count is statistically meaningful and why.** Do not trust very few trades, unrealistic returns, or insufficient data.
5. **Parameter stability** — evaluate neighbouring values and prefer broad plateaus. **Run the neighbourhood on TRAIN+VAL ONLY, never on TEST**: `W ∈ {120, 168, 240}` and `m_min ∈ {0.00, 0.25, 0.50}`. **Because these are never evaluated on TEST they are diagnostics, not variants, and do not count against the trial budget** — state that in the report. A cliff rather than a plateau is a reportable robustness failure.
6. **Overfitting detection** — Deflated Sharpe Ratio via the `freqtrade_dsr.py` entry point (`validator.deflated_sharpe`), on the TEST split, at `n_trials = 1` (0 before this cycle + 1 for this variant). **Bar: DSR ≥ 0.95.** Report `trial_var_source` verbatim.
7. **Look-ahead bias** — verify every quantity uses only information available at candle close. Use `validator.signal_to_returns`'s 2-bar convention rather than hand-rolling a shift; if the overlay is applied outside that function, state the lag explicitly and justify that it matches. **Reject the construct on any leakage.**
8. **Realistic execution** — `COST_MODEL` taker, resolved through `per_side_cost()`. Never assume perfect fills.
9. **Monte Carlo** — `validator.monte_carlo` + `validator.mc_gate_status`. **Pre-registered: `n_sims = 1000`, seeds `[11, 20260805, 777]`.** These are fixed now and **may not be raised or changed after seeing a straddling result — doing so invalidates the cycle.** Three outcomes, not two:

   | Outcome | Condition | Disposition |
   |---|---|---|
   | **PASS** | **every** seed's p5 Sharpe > 0 | eligible to continue |
   | **FAIL** | **every** seed's p5 Sharpe ≤ 0 | REJECT |
   | **INSUFFICIENT** | seeds disagree in sign | **PARK, never PROMOTE** |

   **INSUFFICIENT is the absence of a result, not a soft FAIL and not a near-PASS.** Report every per-seed p5 value.
10. **`validator.sharpe_difference_se()` — MANDATORY on the candidate.** Compute and report the paired-difference standard error and the implied t-statistic against the benchmark's TEST return series over the 151 overlapping dates. **These do NOT gate** — criterion 3 is the 1.10× ratio — but **omitting them is a spec violation.**
11. **Ledger** — call `validator.append_trial(...)` once for the variant so `research/trial_sharpe_ledger.csv` gains its first data row. See Environment notes on ownership.

---

## Promotion criteria — all SEVEN, quoted from `PROJECT_OPERATOR_MANUAL.md`, "Promotion rule — FINAL"

A candidate is **PROMOTED only if ALL SEVEN hold**. Failing any one is **REJECT or PARK**. **There is no discretion** — neither Engineer nor Reviewer may weigh a strong result on one criterion against a failure on another.

1. **DSR ≥ 0.95** on the TEST split at the current `n_trials`. Absolute gate, not a comparison against the benchmark.
2. **Candidate TEST-split Sharpe > 0** in absolute terms.
3. **Candidate TEST-split Sharpe ≥ 1.10 × the benchmark's** — same window, cost model and fill assumption: **≥ 0.135653 per-period (+2.5916 annualised)**, against the benchmark's 0.123321 per-period (+2.3560 annualised). Compare **per-period** Sharpes. A series compared against itself gives Δ = 0 and **does not pass** — 1.00× is not 1.10×.
4. **Candidate REALIZED MaxDD ≤ 1.25 × the benchmark's realized TEST MaxDD** — benchmark −25.02%, so the cap is **−31.27%**. **Realized only, never the Monte Carlo MaxDD distribution.**
5. **Every validation gate in this file passed.**
6. **Monte Carlo gate is PASS, not INSUFFICIENT.**
7. **DSR `trial_var_source` is not `"estimator_proxy"`.**

### PROMOTE IS CURRENTLY UNREACHABLE — do not design or report as though it were

`research/trial_sharpe_ledger.csv` holds **0 data rows**. The harness needs **10** before cross-trial variance is estimable, so every DSR computed this cycle will return `trial_var_source = "estimator_proxy"`, and **criterion 7 caps the maximum available verdict at PARK.** This is stated so that neither Engineer nor Reviewer works toward an outcome that cannot be reached this cycle. The ledger fills one row per variant per cycle; this cycle contributes its first, if it reaches a trial.

**The correct dispositions this cycle are: REJECT (a pre-gate fired, or a validation gate failed), or PARK (everything passed but criterion 7 binds).** Report the other six criteria honestly regardless — they are what a future cycle will read.

---

## Research budget

Quoted from `PROJECT_OPERATOR_MANUAL.md`, "Research budget" — default per-cycle limits are **3 strategy variants, 1 optimization run**. The Director may assign fewer, never more.

| Item | Assigned |
|---|---|
| Strategy variants (each = 1 trial against `n_trials`) | **1** |
| Optimization / hyperopt runs | **0** |
| Monte Carlo sims / seeds | 1000 / `[11, 20260805, 777]` — pre-registered above |
| Placebo draws / seed | 1000 / `20260805` — pre-registered above |
| Trials spent | **0** if any of F1, F2, F3 fires **or** the P3 cost-admissibility requirement is not met; **1** otherwise |

**Every parameter is pre-registered in this file and none may be tuned**: `W = 168`, quintiles, `h = 24`, `m ∈ [0.25, 1.00]`, the 0.25 quantizer, `target` = TRAIN median. The parameter-stability neighbourhood in gate 5 and the continuous-multiplier frequency diagnostic in P3 are evaluated on **TRAIN+VAL only**, are never scored on TEST, and therefore are **not variants**. **Exceeding the assigned variant count invalidates the cycle** — trials would be spent without being priced into `n_trials`.

**Program cap**: `n_trials` may not exceed **30** for the perps program. At 0 before this cycle, spending 1 is within the cap.

---

## Deliverables

**Engineer writes these and nothing else** (`PROJECT_OPERATOR_MANUAL.md`, "File ownership"):

1. `research/results/T-040_report.md` — the standard report format. It must contain, at minimum: every gating figure with its raw-artifact provenance; the P2 `dsd`/`sd`/`usd` decomposition table; the per-year and disjoint-window sign views; the P2b null summary **with P95, the one-tailed empirical p-value, the two-tailed p, the full `M_draw` distribution and the sign-symmetry check**; the explicit statement that P2b is **not** a family-wise correction, that this cycle carries no multiple-testing protection beyond its single pre-registration, and that a follow-on construct inherits **1 test, not 72**; P3's turnover figures and the continuous-multiplier diagnostic; the sentence that P3 is a cost check and not evidence of the mechanism; the verdict section's two separate items (which of F1/F2/F3 fired, and separately whether the cost-admissibility requirement was met); the four-item >100%-CAGR verification; and, if a trial was spent, all seven promotion criteria evaluated individually.
2. `research/results/T-040_raw/` — every raw artifact behind every number. **Every figure in the report must be traceable to one of these.** T-038's audit found five section-7 diagnostics traceable to no artifact; they recomputed correct, but it was recorded as a documentation gap. Do not repeat it.
3. `user_data/research/phase_t040_semivar.py` — the script. **Commit it with `git add -f`** — `.gitignore:7` (`user_data/*`) means a plain `git add` silently does nothing, which is the gap that permanently lost `fng_raw.json`. A script not in a commit is not reproducible.

**Do NOT write** `research_index.md`, `research_metrics.md`, `strategy_iteration_log.md`, `strategy_research_notes.md`, `knowledge_base/hypothesis_bank.md`, or anything in `research/review_briefs/`. Those are Reviewer-owned; an Engineer writing one is a recorded spec deviation. This assignment does not widen that division (it may narrow but never widen it), with the single exception noted for the trial ledger in Environment notes.

**Reproducibility standard**: the Reviewer will re-run your script **unmodified** and expects byte-identical artifacts. Seed every stochastic step with the pre-registered seeds. Do not write a script that overwrites its own outputs on re-run in a way that would destroy the evidence the audit exists to check.

---

## Environment notes

- **Meta-review counter**: 18 of 25 at assignment time — not due. This is perps RESEARCH cycle 3.
- **RESEARCH:OPS ratio** (perps): 2 RESEARCH : 1 OPS before this cycle. The 2:1 floor is **not yet in force** — it begins at cycle 7. This is a RESEARCH cycle, so the ratio improves regardless.
- **Trial ledger ownership is a manual gap.** `PROJECT_OPERATOR_MANUAL.md`'s "File ownership" section names neither role as the owner of `research/trial_sharpe_ledger.csv`, while the promotion section says "the ledger fills one row per variant per cycle". This assignment instructs the **Engineer** to call `validator.append_trial(...)` because the function exists for that purpose and the row must be written when the variant is evaluated. **Reviewer: please treat this as an assignment-authorised action rather than an ownership violation, and flag the manual gap for the operator.**
- **Funding-rate data is unusable this cycle, confirmed by direct inspection on 2026-08-05.** All nine `*-1h-funding_rate.feather` files span **2026-02-26/28 → 2026-05-28** (266–273 records each) — **zero overlap** with the window ending 2025-09-19. This matches A-005's finding. **A-009 is already filed** to establish whether history back to 2022 is reachable; not re-filed here. Acquisition is forbidden inside a research cycle.
- **Provenance of the mark-premium figures** quoted under "Alternatives considered": the Director ran a **read-only** one-line inspection this session over TRAIN bars only (`(close − mark)/mark` in bps, per instrument, bars ≤ 2024-11-22 23:00 UTC), reading `*-1h-mark.feather` and `*-1h-futures.feather`. **No file was created or modified and no project artifact records these numbers** — they are a Director dead-on-arrival check under selection rubric 2, not a cycle result, and should not be cited as one.
- **Known 1h data-coverage facts (A-010, already filed, unresolved)**: BTC 1h is short 25 bars relative to the other instruments at the series end, and there are 9 zero-volume bars across 8 instruments. Neither falls inside the split window, but **report how your code handles zero-volume bars** if any are encountered.
- **BNB starts 2022-12-23**, later than the other eight. Its TRAIN split is correspondingly shorter. This is expected, not a defect — but state the per-instrument bar counts entering P2 so the breadth statistic can be read against them.
- **Director-set thresholds, recorded because the manual does not define them**: the 0.99 basket-reconciliation correlation floor; the `p > 0.05` placebo kill in F3; the `W ∈ {120,168,240}` / `m_min ∈ {0.00,0.25,0.50}` stability neighbourhood. Every other threshold in this file is quoted from a project file.
- **`research/champions/` does not exist.** That is expected — it is created by the Reviewer on the first PROMOTE. Its absence is not a missing file.
- **`research/BLOCKED.md` does not exist** at assignment time. If you must block, create it and state the exact blocking sentence.
- **Hypothesis bank**: this hypothesis was **not drawn from the bank ledger**, so no bank entry has been marked ASSIGNED and the bank was not modified. The nearest existing cards are "Volatility-Filtered Trend Following" (§5, untested, regime-gate framing) and "Trend + Volatility-Target Sizing Combo" (§5, tested in the spot program as TrendVolTarget); neither specifies a downside-only estimator. The construct is grounded in `11_risk_management.md` / `12_portfolio_construction.md` as cited above and in T-038's own carried-forward Engineer recommendation.
- **Both prior perps research cycles died at zero-cost pre-gates, and that is the discipline working** — but it also means the trial ledger is still empty and criterion 7 is unsatisfiable. This cycle is designed so that a genuine pass reaches a trial rather than stopping short. It is **not** designed to reach a trial regardless: F1, F2 and F3 are real, and F2 in particular is a coin-flip on the program's own evidence. Note that the P3 cost-admissibility requirement can also stop the cycle, but it is not one of the three and is not evidence about the hypothesis.
