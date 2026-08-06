# T-040 — H-SemiVarSizing-1h — Research Engineer report

**Task ID**: T-040 · **Program**: perps · **Cycle type**: RESEARCH · **Date**: 2026-08-05
**Verdict**: **REJECT at zero-cost pre-gate P2 (F2 fired on BOTH clauses).**
**Trials spent: 0. Perps `n_trials` stays 0.**

---

## 1. Task ID and hypothesis

**Task ID**: T-040 / H-SemiVarSizing-1h.

**Hypothesis** (copied verbatim from `research/NEXT_TASK.md`):

> **On 1h OKX perpetual bars, forward risk-adjusted returns of the nine-instrument
> equal-weight basket are DECREASING in trailing *downside* semideviation, even though
> T-038 measured them as INCREASING in trailing *total* volatility — and an exposure
> multiplier that cuts exposure as downside semideviation rises therefore improves the
> basket's risk-adjusted return net of its own turnover cost.**

**Objective** (verbatim):

> Determine whether the volatility→exposure inversion that killed T-038 is a property of
> *volatility itself* on 1h perps, or an artifact of using a **total**-volatility estimator
> that sums an adverse (downside) and a favourable (upside) dispersion component.

The answer this cycle produces is: **it is a property of the dispersion, not an artifact of
the estimator.** Splitting total volatility into its downside and upside components does not
restore the de-risking sign — the *downside* component carries the **strongest** inversion of
the three estimators tested.

---

## 2. Zero-cost pre-gate result

Ladder run in the assigned order, stopping at the first failure.

| Gate | Statistic | Computed | Threshold | Result |
|---|---|---|---|---|
| **P1** | median Spearman ρ(dsd, forward 24-bar downside semideviation) | **+0.480280** | KILL if `< 0.30` | pass |
| **P1** | min ρ across the nine (BTC) | **+0.427458** | KILL if `<= 0.15` | pass |
| **P2** | `D_bar` on the PRIMARY conditioner `dsd` | **−0.426586** | KILL if `<= 0` | **FAIL** |
| **P2** | breadth `B` = count of `D[i] > 0` | **0 of 9** | KILL if `< 5` | **FAIL** |
| **P2b** | one-tailed placebo p | — | KILL if `> 0.05` | **NOT REACHED** |
| **P3** | `Sharpe(o) > Sharpe(b)` on TRAIN+VAL | — | requirement to proceed | **NOT REACHED** |

**F2 fired, and both of its clauses fired independently.** The cycle stops here, spends zero
trials, and P2b, P3 and the trial stage were never run. Sections 7–9 state "not reached"
where that is the case.

**Sign of the result, stated plainly**: `D_bar = −0.426586` means the *lowest*-downside-
semideviation quintile has a forward per-unit-risk return **0.4266 lower** than the highest.
High trailing downside dispersion on 1h perps is followed by **better** risk-adjusted
returns, not worse — the T-038 inversion, reproduced on the downside leg alone.

---

## 3. Implementation notes

**Script**: `user_data/research/phase_t040_semivar.py` (single file, committed with
`git add -f`; `.gitignore:7` makes a plain `git add` a silent no-op).

**Every parameter came from `NEXT_TASK.md` and none was tuned**: `W = 168`, quintiles,
`h = 24`, `fwd_pur` response, 25-bar trim, `m ∈ [0.25, 1.00]` at a 0.25 quantizer,
`target` = TRAIN median, 1,000 placebo draws at seed `20260805`, MC `n_sims = 1000` at seeds
`[11, 20260805, 777]`, `n_trials = 1`. The last five were never used — the cycle stopped
before P2b.

**Basket construction rule** (needed only from P3 onward, so never exercised): the script
imports `perps_benchmark.build_benchmark` and `perps_benchmark.load_whitelist` directly
rather than reimplementing them, per the assignment's "read its header and reuse the rule; do
not invent a second construction". `month_end_bars()` marks the last bar of each calendar
month at whatever resolution it is handed, which at 1h is the last 1h bar of the month —
exactly the assigned rule.

**Order of operations (standing directive 8, warmup).** `dsd`, `usd`, `sd` and every forward
variable are computed by `conditioners()` over the **full 1h series from each instrument's
own first bar**; the TRAIN+VAL slice is taken afterwards. No indicator is recomputed inside a
split. Then, in order: slice to `≤ val_end` → drop the last 25 bars → drop warmup NaNs → drop
bars whose response is undefined.

**Forward-window trim.** The literal **25** bars (`max(h) + 1`) the assignment specifies,
not 24. It is one bar more conservative than strictly required, which is the point: the last
retained anchor is `2025-04-20 22:00` and its forward window ends `2025-04-21 22:00`, one bar
**before** `val_end` at the 1h resolution (`2025-04-21 23:00`). Asserted for all nine in
`_assert_forward_window_contained()`, not assumed.

**Falsification conditions were transcribed literally.** The top-level connective between
F1/F2/F3 is `or`; the connectives inside each clause are as written:

| Spec | Code | Line |
|---|---|---|
| F1: `median(rho) < 0.30` **OR** `min(rho) <= 0.15` | `fired = (med < P1_MEDIAN_FLOOR) or (mn <= P1_MIN_FLOOR)` | `p1_persistence()` |
| F2: `D_bar <= 0` **OR** `B < 5` | `fired = (d_bar <= 0.0) or (breadth < P2_BREADTH_FLOOR)` | `p2_harm_census()` |
| F3: `p > 0.05` | `fired = p_one > P2B_P_CEILING` | `p2b_placebo()` (not reached) |

Both F1 clauses and both F2 clauses are evaluated and reported separately
(`clause_a_*` / `clause_b_*` in `t040_results.json`) so a Reviewer can check each against its
threshold without re-deriving the `or`.

**Nothing was ambiguous enough to block.** One point needed a decision and was resolved by
**reporting both readings rather than choosing one**: the assignment's non-gating robustness
views say "`D_bar` recomputed per calendar year / on three sub-windows" without stating
whether the quintile edges are re-estimated inside the view. The script reports **both** —
`D_bar_refit_edges` (edges re-estimated in the view, the natural reading of "recomputed" and
how `D` is defined in P2) and `D_bar_fixed_edges` (edges held at the full TRAIN+VAL values).
Both are negative in every view, so the sign does not depend on the unstated choice. This is
a non-gating diagnostic and could not change F2, which had already been evaluated on the
pre-registered statistic.

**Zero-volume bars** (Environment notes, A-010): 9 in TRAIN+VAL for each of the eight
non-BNB instruments, 0 for BNB, 0 in TEST. They are **kept as ordinary bars and not
special-cased**. The construct reads `close` only, a zero-volume bar still carries a settled
close, and dropping bars would punch a hole in a contiguous hourly index that every rolling
window depends on. Counts are recorded per instrument in `anchor_census_shape.json`.

**Data-shape facts confirmed on load** (all nine, asserted in `load_closes_1h()`): no
duplicate timestamps, **no non-hourly gaps at all**, no NaN closes. BTC ends `2026-05-27
18:00` against the others' `2026-05-28 19:00` (the known A-010 25-bar shortfall) — far
outside the split window and with no effect here.

**Post-verdict diagnostics.** Three tail-insensitive views of the same census
(quintile medians, 1%-trimmed quintile means, and a monotonicity score) were computed
**after** F2 had been evaluated, are labelled as such in the artifact, gate nothing, and
could not change the verdict. They exist to answer the one question the assignment asks the
Engineer to judge in prose (T-038 Engineer recommendation 4: is the effect a gradient or a
few extreme bars?). See sections 7 and 12.

**Files modified / created**:

- created `user_data/research/phase_t040_semivar.py` (the script);
- created `research/results/T-040_raw/` (8 artifacts);
- created `research/results/T-040_report.md` (this file).

Nothing else. No Reviewer-owned file was touched, and no deviation from `NEXT_TASK.md` was
requested or taken.

---

## 4. Compliance attestations

**(a) `user_data/data/` is untouched.**

```
$ git status --porcelain -- user_data/data/
(no output)
$ git diff --stat -- user_data/data/
(no output)
```

Full working-tree status at the end of the cycle, before the Engineer's own commit:

```
 M research/NEXT_TASK.md          <- the Director's assignment, modified before this cycle began
?? research/results/T-040_raw/    <- this cycle's raw artifacts
?? research/results/T-040_report.md
```

`user_data/research/phase_t040_semivar.py` does not appear because `.gitignore:7`
(`user_data/*`) hides it; it is committed with `git add -f`. No `download-data`, no
`data_manifest.py build`, no write of any kind under `user_data/data/`.

**(b) Data manifest verification passed and was NOT bypassed.**

`validator.py` verifies on import and fails closed. Recorded on every artifact:

```
{'verified': True, 'bypassed': False, 'files_checked': 52,
 'manifest_built_utc': '2026-07-29T07:58:59Z'}
```

`FREQTRADE_SKIP_DATA_VERIFY` was never set. `bypassed` is `False`.

**(c) Resolved cost model** — read from `validator.py`, not typed from memory:

```
$ per_side_cost("taker")   -> 0.000900   (9.0 bps/side)
$ round_trip_cost("taker") -> 0.001800   (18.0 bps round trip)
okx_usdt_perp / regular (non-VIP, no fee discounts) / fill=taker:
maker 2.0bps, taker 5.0bps, slippage 3.0bps/side, spread 2.0bps,
adverse selection unset -> 9.00bps/side, 18.00bps round trip
```

Venue **okx_usdt_perp**, fill assumption **`taker`** as assigned. `maker_optimistic` was
never set, so no maker warning applies. **No cost number is hardcoded anywhere in the
script**; the only cost used, `per_side_cost("taker")`, is resolved at run time and was in
fact never consumed by a computation, because the cycle stopped before P3.

**Mandatory cost-model warning, reproduced verbatim:**

> COST MODEL NOTE - slippage (3.0 bps/side) and spread (2.0 bps) are estimates, not
> calibrated against realized fills. Fee rates are published OKX regular (non-VIP, no fee
> discounts) rates for okx_usdt_perp as of 2026-07-28.

**(d) Split dates and reserved holdout.**

Split triple used, pinned by literal date, exactly the frozen A-005 values:
`train_end 2024-11-22 · val_end 2025-04-21 · test_end 2025-09-19`. Sub-daily boundaries were
resolved through `validator.holdout_boundary(program, freq="1h")` rather than hand-rolled:
`val_end` = `2025-04-21 23:00 UTC`, holdout boundary = `2025-09-19 23:00 UTC`.
`split_70_15_15()` was never called; no boundary was computed as a fraction.

**Reserved holdout was untouched, and so was the entire TEST split.** This cycle never
reached a TEST evaluation. Stronger than an assertion, it is demonstrated empirically: the
whole census was recomputed on inputs **physically truncated at `val_end`**, and every
reported figure is **bit-identical** —

```
D_bar, full-series input        : -0.4265863378077064
D_bar, truncated at val_end     : -0.4265863378077064   (identical)
P1 median rho, full / truncated : 0.4802800066657192 / identical
anchor sets identical           : True
```

Directive 8 requires indicators be computed on the full series so warmup is not truncated,
which does mean the loader *reads* post-`val_end` bars; this check demonstrates that **none
of them reaches a reported number**. Artifact: `lookahead_checks.json`.

**(e) DSR entry-point check.**

```
$ python scripts/check_dsr_entrypoint.py
  VIOLATIONS: 0
  OK: no research file imports freqtrade_dsr directly.
```

No DSR was computed this cycle — no trial was spent, so there is no candidate return series
to deflate. `validator.deflated_sharpe()` was not called and `validator.append_trial()` was
not called; both would have been wrong here. Consequently **`research/trial_sharpe_ledger.csv`
still holds 0 data rows** and criterion 7 remains unsatisfiable for the next cycle.

---

## 5. Lookahead / leakage checks performed

All four are executed inside the script (`leakage_and_arithmetic_checks()`), raise on
failure, and are recorded in `lookahead_checks.json`.

**1. Truncation invariance — the decisive leakage test.** Recomputing the entire census on
inputs truncated at `val_end` returns bit-identical anchor sets, `D_bar` and `P1` median ρ
(figures in 4(d)). No bar after `2025-04-21 22:00` influences any number in this report.

**2. Forward-window containment.** Every retained anchor's 24-bar forward window ends at or
before `2025-04-21 22:00`, strictly before `val_end` `2025-04-21 23:00`, for all nine
instruments. Asserted per instrument in `build_anchor_frame()`.

**3. Causality of the conditioners, checked by hand arithmetic.** At a fixed timestamp chosen
before any result was seen (SOL, `2024-06-05 07:00`), `dsd`, `usd`, `sd`, `fwd_ret`,
`fwd_vol` and `fwd_pur` were recomputed by explicit slice arithmetic and agree with the
vectorised implementation to `rtol = 1e-9`. `dsd[t]` reads exactly `r[t-167 … t]` — bars at
or before `t` only. `sd` uses the population std (`ddof=0`) as specified.

**4. The decomposition identity holds exactly.** `dsd² + usd² == mean(r²)` over the same
168-bar window, to `rtol = 1e-12`. This is the algebraic claim the hypothesis rests on, so it
is verified rather than assumed.

**5. Indicators computed before splitting** — yes, by construction (section 3), and that is
also what makes check 1 meaningful.

**6. Independent code-path check, and the one discrepancy it found.** `D[i]` was recomputed
for all nine instruments with `pandas.qcut` + `groupby` instead of
`np.quantile` + `np.searchsorted`. They **do not agree bit-for-bit**, and the check is
reported rather than buried:

- max |difference| **3.731e-03** (BTC: −0.103755 vs −0.100024);
- cause: `dsd` carries thousands of exactly-repeated values (5,544–7,796 duplicates per
  instrument — a 168-bar RMS of the negative returns repeats whenever the window's negative
  set repeats). Where a quintile edge lands on a tied value, pandas' right-closed interval
  `(a, b]` assigns the ties to the **lower** bin while `searchsorted(side="right")` assigns
  them to the **upper** one. It moves **0–6 bars per instrument out of ~28,775**;
- it is a tie-handling convention, not an arithmetic error, and neither convention is
  "correct". The pre-registered implementation (`searchsorted`) is primary because it was
  fixed before any result was seen;
- **the KILL clauses do not turn on it**: `D_bar` −0.426586 (breadth 0/9) under
  `searchsorted` versus −0.425994 (breadth 0/9) under `qcut`. Both clauses of F2 fire under
  both conventions. The script asserts this agreement and would raise a STOP condition if the
  verdict depended on the convention.

**No leakage was found, and no construct was rejected on leakage grounds.** F2 fired on the
data.

---

## 6. Variants attempted — numbered against budget

**Assigned budget: 1 strategy variant, 0 optimization runs. Used: 0 variants, 0 optimization
runs. Trials spent: 0.**

No variant was ever constructed, because a pre-gate killed the hypothesis first. For
completeness, every computation run in this cycle is logged, with its budget status:

| # | Run | Budget status | Outcome |
|---|---|---|---|
| 1 | Data load + integrity gate, all nine 1h series | not a variant | clean; 250,425 pooled anchor bars |
| 2 | Lookahead / leakage / arithmetic verification | not a variant | passed; one reported binning discrepancy (§5.6) |
| 3 | **P1** persistence census | zero-cost pre-gate, no trial | PASS (median ρ +0.480280, min +0.427458) |
| 4 | **P2** harm census on `dsd` (PRIMARY, gating) | zero-cost pre-gate, no trial | **FAIL — F2 fired on both clauses** |
| 5 | P2 diagnostic census on `sd` | non-gating diagnostic, mandated | `D_bar` −0.205060, breadth 2/9 |
| 6 | P2 diagnostic census on `usd` | non-gating diagnostic, mandated | `D_bar` −0.189939, breadth 3/9 |
| 7 | P2 robustness: 4 calendar years × 2 edge conventions | non-gating, mandated | all 8 negative |
| 8 | P2 robustness: 3 disjoint sub-windows × 2 edge conventions | non-gating, mandated | all 6 negative |
| 9 | Post-verdict tail diagnostics (median / trimmed / monotonicity) | non-gating, post-verdict | sign unchanged, breadth 0/9 in all three |

Runs 5–8 are explicitly mandated as non-gating reporting by `NEXT_TASK.md`. Run 9 was
computed after the verdict was determined and cannot change it. **None of these is a strategy
variant**: none produces a return series, none is evaluated on TEST, and none was selected
over an alternative. There was no parameter search of any kind — every parameter was fixed in
`NEXT_TASK.md` before the first computation.

**Not run, because the ladder stopped**: P2b (1,000 placebo draws), P3
(cost-admissibility + continuous-multiplier frequency diagnostic), the parameter-stability
neighbourhood (`W ∈ {120,168,240}`, `m_min ∈ {0.00,0.25,0.50}`), walk-forward, Monte Carlo,
DSR, `sharpe_difference_se`, `append_trial`, and the criterion-3 pairing.

---

## 7. Backtest results

**Not reached.** No candidate was constructed, so there is no backtest, no return series and
no headline metric. The `>100% CAGR` defect presumption does not arise — no CAGR was computed
at all, and there is no number in this report that a return envelope could apply to.

What exists instead is the census. The gating table:

### P1 — persistence of the conditioner (`p1_persistence.csv`)

Spearman ρ between `dsd[t]` and the forward 24-bar realized downside semideviation.

| Instrument | ρ | n anchors |
|---|---|---|
| BTC | +0.427458 | 28,775 |
| ETH | +0.513487 | 28,775 |
| SOL | +0.462938 | 28,775 |
| BNB | +0.441343 | 20,225 |
| XRP | +0.480280 | 28,775 |
| ADA | +0.505624 | 28,775 |
| AVAX | +0.520576 | 28,775 |
| DOT | +0.529232 | 28,775 |
| LINK | +0.478164 | 28,775 |
| **median** | **+0.480280** | floor 0.30 |
| **min** | **+0.427458** | floor > 0.15 |

**F1 did not fire.** Downside semideviation is comfortably forecastable at 1h — comparable to
T-038's total-volatility P1 (median 0.564373 / min 0.434160), slightly lower on the median
and essentially the same on the minimum.

**This is a necessary condition and is NOT evidence for the hypothesis.** Any autocorrelated
series passes a persistence test; P1 exists only to kill the cycle cheaply if the conditioner
were unforecastable, and it is not cited in support anywhere in this report.

### P2 — harm census (`p2_census.csv`) — the gating result

Response: `fwd_pur = fwd_ret / fwd_vol`, h = 24 bars. `D[i] = mean(fwd_pur | Q1) −
mean(fwd_pur | Q5)`, quintiles of the conditioner estimated per instrument on that
instrument's TRAIN+VAL anchors. `D_bar` is the equal-weight mean across the nine.

| Instrument | `D[i]` on **dsd** (PRIMARY) | `D[i]` on `sd` (diag) | `D[i]` on `usd` (diag) |
|---|---|---|---|
| BTC | −0.103755 | **+0.122912** | **+0.203311** |
| ETH | −0.055524 | **+0.041169** | **+0.316765** |
| SOL | −0.393464 | −0.381057 | −0.535430 |
| BNB | −1.051296 | −0.758062 | −0.982215 |
| XRP | −0.550458 | −0.478643 | −0.300409 |
| ADA | −0.428267 | −0.009335 | **+0.003809** |
| AVAX | −0.489468 | −0.085517 | −0.214589 |
| DOT | −0.434831 | −0.272336 | −0.095581 |
| LINK | −0.332214 | −0.024674 | −0.105109 |
| **`D_bar`** | **−0.426586** | **−0.205060** | **−0.189939** |
| **breadth `B`** | **0 / 9** | 2 / 9 | 3 / 9 |

**KILL clause `D_bar <= 0` OR `B < 5`: both clauses fire. F2 fired.**

- `D_bar = −0.426586 ≤ 0` → clause (a) fires;
- `B = 0 < 5` → clause (b) fires. **Not one instrument of nine** has the hypothesised sign.

**Quintile means, `dsd`, Q1 → Q5** (from `p2_census.csv`):

| | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|
| BTC | +0.2140 | +0.1681 | +0.3459 | +0.1004 | +0.3177 |
| ETH | +0.0752 | +0.0370 | +0.3098 | +0.0602 | +0.1307 |
| SOL | −0.0501 | +0.2925 | −0.3754 | +0.0629 | +0.3433 |
| BNB | +0.0138 | +0.0765 | +0.1184 | +0.4039 | +1.0651 |
| XRP | +0.1069 | −0.3015 | −0.1910 | +0.1179 | +0.6574 |
| ADA | −0.0773 | −0.0871 | +0.1104 | −0.2533 | +0.3510 |
| AVAX | −0.1411 | −0.0709 | −0.3965 | −0.0423 | +0.3484 |
| DOT | +0.0171 | +0.0188 | −0.3018 | −0.1235 | +0.4519 |
| LINK | −0.0519 | −0.0028 | +0.5204 | −0.2215 | +0.2803 |

**Q5 is the maximum for 8 of 9 instruments** (LINK's Q3 is higher). The interior quintiles
are non-monotonic almost everywhere — the same "not a vol gradient" character the T-038
Reviewer recorded, now reproduced on the downside-only estimator.

### Diagnostics — sign expectations from `NEXT_TASK.md`, and what happened

**(a) `sd` — expected NEGATIVE.** Measured **−0.205060**, breadth 2/9. **Expectation met.**
The two cycles agree on the same data: T-038 found total-volatility `Q1−Q5 = −0.442905`
(−0.438872 under the resolution-aware boundary re-run) with breadth **1/9** using an EWMA
estimator; this cycle finds −0.205060 with breadth **2/9** using the matched 168-bar rolling
window. Same sign, same near-zero breadth. **The assignment's "if it comes out positive the
two cycles disagree and the Engineer must say so loudly" clause does not trigger.** The
numeric values are not comparable (different estimator, different response formula); the sign
and breadth are, and they match.

**(b) `usd` — expected STRONGLY NEGATIVE if the contamination hypothesis is right.**
Measured **−0.189939**, breadth 3/9. It is negative, but it is the **weakest** of the three
and **weaker than `sd`**, while `dsd` — the leg predicted to flip **positive** — is more than
**twice as negative** as either.

**This ordering is the substantive result of the cycle, and it is the reverse of what the
contamination hypothesis predicts.** The prediction was: `usd` carries the inversion, `dsd`
does not, and total volatility inverts only because it mixes them. The measurement is:

```
dsd (−0.4266)  <<  sd (−0.2051)  <  usd (−0.1899)      more negative  ->  <<
```

The **adverse** component is where the inversion is concentrated. Splitting the estimator did
not isolate an adverse leg and a favourable leg — it isolated the leg that inverts *hardest*.
Note also that `D_bar(sd) = −0.2051` sits **between** its two components rather than below
both, which is what an averaging-of-two-effects picture predicts and is inconsistent with
"total volatility inverts because upside contaminates it".

### Robustness views (`p2_robustness_views.json`) — reported, non-gating

`D_bar` recomputed per calendar year and on three disjoint equal-bar-count sub-windows, under
**both** edge conventions (§3).

| View | bars/instrument | `D_bar` refit edges | breadth | `D_bar` fixed edges |
|---|---|---|---|---|
| year 2022 | 8,592 (BNB 42) | −1.452418 | 1/9 | −0.827844 |
| year 2023 | 8,760 | −0.337993 | 3/9 | −0.185046 |
| year 2024 | 8,784 | −0.631020 | 1/9 | −0.767184 |
| year 2025 (to 04-20) | 2,639 | −0.835599 | 1/9 | −6.372216 † |
| sub-window 1: 2022-01-08 … 2023-02-11 | — | −0.081812 | 3/9 | −0.197952 |
| sub-window 2: 2023-02-11 … 2024-03-17 | — | −0.376236 | 2/9 | −0.470891 |
| sub-window 3: 2024-03-17 … 2025-04-20 | — | −0.904028 | 0/9 | −1.236465 |

**`D_bar` is negative in all 14 view/convention cells. `sign_flips_across_views: false`.**
There is no year and no sub-window in which the hypothesised sign appears.

Two honest caveats on this table:

- **†** the 2025 fixed-edges figure is a **convention artifact, not a finding**. 2025's `dsd`
  distribution sits far to the right of the pooled one, so the full-window Q1 edge leaves
  ADA and DOT with **zero** Q1 bars (undefined `D`, dropped — the cell averages 7 of 9) and
  XRP/LINK with 13, ETH with 22. That is exactly why the refit convention is the primary
  reading and why both are reported.
- the 2022 view includes BNB on **42 bars** (~8 per quintile), just over the 25-bar
  evaluability floor. The other eight carry 8,592 bars each, so the view is not driven by it,
  but a 42-bar `D` estimate should not be read as an instrument-level result.

### Post-verdict tail diagnostics (`p2_post_verdict_diagnostics.json`) — non-gating

Computed **after** F2 was evaluated; changes no gate. Answers whether the sign is a gradient
or a few extreme bars (T-038 Engineer recommendation 4).

| `D_bar` computed from | value | breadth |
|---|---|---|
| quintile **means** (pre-registered) | −0.426586 | 0/9 |
| quintile **medians** | −0.473918 | 0/9 |
| 1 %-symmetrically-**trimmed** means | −0.426874 | 0/9 |

Median monotonicity ρ (quintile index 1…5 vs quintile mean): **+0.30**. Per instrument: BNB
+1.0, XRP +0.7, AVAX +0.7, SOL +0.5, ETH +0.3, ADA +0.3, DOT +0.2, LINK +0.2, BTC +0.1.

**Two distinct conclusions, and they point in different directions:**

1. **The sign is not a tail artifact.** Removing the tails makes it *more* negative, not
   less. The T-038 Engineer's trap — "the apparent edge lives in a few extreme bars" —
   **does not apply to the sign of this census**. Q5's advantage survives medians and
   trimming.
2. **But it is not a clean gradient either.** A median monotonicity of +0.30 across five
   ordered buckets is weak; only BNB is monotone. The relationship is closer to "the top
   bucket is different" than to "response increases smoothly with the conditioner". So the
   trap is **half-addressed**: the effect is not a handful of outliers, but neither is it the
   ordered dose-response a sizing curve would need.

---

## 8. Walk-forward / out-of-sample results

**Not reached.** Walk-forward, the TEST evaluation, the criterion-3 daily pairing (151-date
assertion), the 0.99 basket-reconciliation check and `validator.sharpe_difference_se()` all
belong to the trial stage, which was never entered. **No TEST or holdout bar was evaluated,
and none was read into any figure** (demonstrated in §4(d) and §5.1).

The pre-gate itself carries the cycle's out-of-sample content in a different form: P2 is a
TRAIN+VAL census whose response variable is strictly forward-looking, and its sign is stable
across three disjoint sub-windows and four calendar years (§7).

---

## 9. DSR and other required statistics

**Not reached, and deliberately not computed.** No trial was spent, so there is no candidate
return series to deflate. `validator.deflated_sharpe()` was not called; `n_trials` was never
consumed; `validator.append_trial()` was not called.

State of the inputs a future cycle will need, for the record:

- `research/trial_sharpe_ledger.csv`: **0 data rows** (unchanged by this cycle).
- Perps `n_trials`: **0 before this cycle, 0 after.** A cycle killed at a pre-gate spends
  zero trials (`PROJECT_OPERATOR_MANUAL.md`, "Research budget").
- `trial_var_source` would still be `estimator_proxy` — the ledger needs 10 rows and has 0,
  so promotion criterion 7 remains unsatisfiable and the maximum available verdict for the
  next cycle that reaches a trial is still **PARK**.
- `scripts/check_dsr_entrypoint.py`: **0 violations**. Nothing in this cycle calls
  `freqtrade_dsr` directly, and nothing calls it at all.

The one statistic this cycle *does* have a standard error worth stating: the P2 census ran on
**250,425 pooled TRAIN+VAL 1h anchor bars** (28,775 × 8 instruments + 20,225 for BNB). The
assignment's directive-9 statement predicted "marginally smaller than 251,946", and 250,425
is 0.6 % below it — the difference is the 168-bar warmup plus the 25-bar trim on nine series.
This sample is far larger than anything needed to resolve a `D_bar` of ±0.43; the census does
not fail for want of power, and the placebo control that would have priced its null
(P2b) was not reached because the sign was wrong, not because the magnitude was marginal.

---

## 10. Verdict vs. falsification statement

The assignment requires these as **two separate items**. They are.

### Item 1 — which of F1, F2, F3 fired

| Condition | Clause | Computed | Threshold | Fired? |
|---|---|---|---|---|
| **F1** | `median(rho) < 0.30` | +0.480280 | 0.30 | no |
| **F1** | `min(rho) <= 0.15` | +0.427458 | 0.15 | no |
| **F1** | (a) **OR** (b) | — | — | **NO** |
| **F2** | `D_bar <= 0` | **−0.426586** | 0 | **YES** |
| **F2** | `B < 5` | **0 of 9** | 5 | **YES** |
| **F2** | (a) **OR** (b) | — | — | **FIRED** |
| **F3** | `p > 0.05` | not computed | 0.05 | **NOT REACHED** |

**The pre-registered rejection condition triggered. The hypothesis is REJECTED.** F2 fired,
and uniquely among this project's recent census cycles it fired on **both** clauses at once:
the sign is wrong *and* not a single instrument of nine dissents.

### Item 2 — separately, whether the P3 cost-admissibility requirement was met

**NOT EVALUATED. The cycle stopped at F2, before P3 ran.**

This is stated as **not reached**, explicitly **not** as "not met". `Sharpe(o)` and
`Sharpe(b)` were never computed; the multiplier series was never built; no turnover figure
exists. Recording a requirement as failed when it was never tested would put a number in the
record that nobody computed.

The distinction matters in the direction the assignment anticipated, and it happens to be
moot here: the assignment reserved the "positive finding about the mechanism together with a
negative finding about its tradeability" split for a cycle that passes F1–F3 and then stops
at P3. **This cycle is the opposite case** — it failed on the mechanism itself, so there is
no positive half to preserve, and P3 would have been measuring the cost of trading a
relationship that runs the wrong way.

### What this does and does not license

- **The escape from directive 10 was falsifiable within this cycle, and it failed.** The
  assignment pre-registered the consequence: *"if `dsd` also inverts, the construct dies at
  F2 and directive 10 generalises from 'total volatility' to 'any trailing-dispersion
  estimator on 1h perps', which closes the family on principle."* `dsd` inverted — harder
  than `sd` did. **The evidence for that generalisation is now on the record; the decision to
  adopt it is the Director's and the Reviewer's, not mine.** The bounds it should carry are
  in §12.
- **This cycle carries no multiple-testing protection beyond its single pre-registration**,
  and it never needed any: the conditioner, horizon, response, thresholds and seeds were all
  fixed in `NEXT_TASK.md` before anything was computed, and no scan was run. P2b — which
  would have priced `D_bar` against its own autocorrelation-preserving null — **was not
  reached**. It is **not** a family-wise correction and must not be described as one in any
  downstream document.
- **A follow-on construct built on this result inherits ONE test, not 72.** No T-039 cell was
  used, cited in a threshold, or built upon.

---

## 11. Regime behavior

**Where the hypothesised effect worked: nowhere.** Zero of nine instruments, zero of four
calendar years, zero of three disjoint sub-windows, under both edge conventions and under
mean, median and trimmed-mean aggregation.

**Where it failed hardest, and what that says:**

- **BNB, `D = −1.051296`, monotonicity ρ = +1.0** — the only cleanly monotone instrument, and
  it is monotone in the *wrong* direction: forward per-unit-risk return rises smoothly from
  +0.0138 in Q1 to +1.0651 in Q5. The one instrument where the conditioner produces an
  orderly dose-response is the one that most decisively contradicts the hypothesis. BNB also
  has the shortest history (20,225 anchors, starting 2022-12-30) and no zero-volume bars.
- **BTC (−0.1038) and ETH (−0.0555) are the mildest** — and are the only two instruments
  whose `sd` and `usd` diagnostics come out *positive*. The two most liquid, most
  institutionally-traded instruments behave least like the other seven on every conditioner.
  That is a cross-sectional pattern worth a Director's attention (§14).
- **2022 is the most negative calendar year (−1.452418 refit).** 2022 is the bear leg of the
  sample. High-downside-dispersion 1h windows in a bear market were followed by the *best*
  forward per-unit-risk returns — i.e. by violent relief rallies. This is consistent with
  the project's own prior finding that crypto bears are "crashes + squeezes, not inverted
  bulls" (H-BearShort, 2026-07-10) and with T-039's "1h momentum is reversal, not trend".
  Three independent cycles now point at the same 1h mechanism.
- **The most recent sub-window is the most negative of the three (−0.904028) and the only one
  at breadth 0/9.** The effect is not decaying out of the sample; if anything the inversion
  strengthens toward `val_end`. Whatever else is true, this is not an expiring artifact of
  old data — which also means a future Director cannot expect it to have faded.

**Regime in which the *construct* would have been expected to work** (assignment: "drawdown
and deleveraging regimes… 2022H2, the 2025H1 negative half-year"): the census covers both.
2022 and 2025-to-April are the two most negative views in the table. **The construct's own
best-case regimes are where the conditioner is most inverted.**

---

## 12. Lessons

1. **The T-038 inversion is a property of trailing dispersion at 1h, not of the total-
   volatility estimator.** Three estimators over a matched 168-bar window on 250,425 pooled
   anchor bars: `dsd` −0.4266 (0/9), `sd` −0.2051 (2/9), `usd` −0.1899 (3/9). Decomposing the
   estimator did not recover the classic de-risking sign; it located the inversion in the
   **downside** leg specifically.
2. **The contamination hypothesis is not merely unsupported — it is contradicted in an
   informative direction.** It predicted `usd` would carry the negative and `dsd` would come
   out positive. The measurement is the exact reverse ordering. A future Director should not
   retry this mechanism with a different dispersion functional (Ulcer index, downside
   EWMA, semivariance over a different window): the axis on which the split was supposed to
   help is the axis on which the effect is strongest.
3. **Kaufman's caveat (`11_risk_management.md:106`) was cited in the assignment as the
   counter-argument, and the data sides with it — for a reason he did not state.** He argued
   that using only drawdowns discards the information in unusually large profits, and that
   with limited data the full distribution is more robust. Here the sample is not limited
   (250,425 bars) and the full-distribution estimator is still the *milder* of the two. The
   operative fact is not robustness under small samples; it is that on a long-only 1h perp
   book the downside component is **positively** associated with forward per-unit-risk
   return, so removing the upside component removes the only part that was damping the
   inversion.
4. **The sign is not an outlier artifact, but it is also not a gradient.** Medians (−0.4739)
   and 1 %-trimmed means (−0.4269) reproduce the pre-registered figure (−0.4266) with breadth
   0/9 throughout, so the T-038 "few extreme bars" trap does not explain the sign. Yet median
   monotonicity across the five quintiles is only **+0.30**. Any future construct that needs
   an *ordered* response to the conditioner — which every continuous sizing curve does — is
   building on an ordering the data barely supports, in either direction.
5. **Ties in a rolling RMS conditioner are common enough to move a census figure, and the
   binning convention must be pinned.** `dsd` had 5,544–7,796 exactly-repeated values per
   instrument. `pd.qcut` and `np.searchsorted(side="right")` disagree on 0–6 bars per
   instrument and moved `D[i]` by up to 3.7e-03 (BTC −0.1038 vs −0.1000). It changed nothing
   here because the margins were large, but a cycle whose `D_bar` lands near zero could have
   its verdict decided by which library function was reached for. **Future census cycles
   should state the tie convention in `NEXT_TASK.md`, and Engineers should verify the KILL
   clauses under both.**
6. **Truncation invariance is a cheap, decisive leakage proof and should be standard on any
   cycle that follows directive 8.** Directive 8 mandates full-series indicator computation,
   which *does* read holdout bars into memory; asserting bit-identity against a physically
   truncated re-run converts "we sliced afterwards, trust us" into evidence. It costs one
   extra pass over the data.
7. **The 25-bar trim did its job and should stay at `max(h)+1`.** The last retained anchor's
   forward window ends exactly one bar before `val_end`. T-039's literal-24 trim read one
   TEST bar per instrument; 25 leaves a one-bar margin that is visible in the artifact
   (`last_bar_read_by_forward_window: 2025-04-21 22:00` vs `val_end 2025-04-21 23:00`).
8. **A pooled 1h census answers in one cycle what daily bars could not.** 250,425 anchor bars
   made a 0/9 breadth result unambiguous. Both perps research cycles that have died at P2 died
   on 1h evidence, and neither verdict is close enough to be sample-size-limited.

---

## 13. Raw output locations

All under `research/results/T-040_raw/`. **Every figure in this report is traceable to one of
these files.**

| Artifact | Contents | Figures it backs |
|---|---|---|
| `t040_results.json` | complete machine-readable record: cost model, data-manifest snapshot, splits, pre-registered parameters, anchor shape, lookahead checks, P1, P2, robustness, post-verdict diagnostics, verdict | every number in this report |
| `lookahead_checks.json` | truncation invariance, independent code path (per instrument), hand arithmetic, decomposition identity, forward-window containment | §4(d), §5 |
| `anchor_census_shape.json` | per-instrument bar counts at each filtering stage, first/last anchor, last bar read by any forward window, full data inventory incl. zero-volume counts | §3, §7 anchor counts, §9 pooled 250,425 |
| `p1_persistence.csv` | per-instrument Spearman ρ, p-value, n | §7 P1 table |
| `p2_census.csv` | per-instrument `D`, n, Q1/Q5 counts, all five quintile means and counts, for `dsd`, `sd` and `usd` | §7 P2 tables, §2 |
| `p2_robustness_views.json` | per-calendar-year and three-sub-window `D_bar` under both edge conventions, per-instrument bar counts, sign-flip flag | §7 robustness table, §11 |
| `p2_post_verdict_diagnostics.json` | per-instrument quintile means / medians / trimmed means, `D` under each, monotonicity ρ, pooled summaries | §7 post-verdict table, §12.4 |
| `console_output.txt` | captured stdout of the run that produced the above | reproduction cross-check |

**Script**: `user_data/research/phase_t040_semivar.py` — committed with `git add -f`.

**Reproducibility**: the executed path contains no stochastic step (P2b, the only seeded
stage, was not reached), and the run was confirmed **byte-identical across three consecutive
executions** (SHA-256 over all JSON and CSV artifacts). A Reviewer re-running the script
unmodified will reproduce every figure exactly. The script writes only into
`research/results/T-040_raw/` and never overwrites an input.

**One note for the re-runner**: if a re-run ever passes all four gates, the script **raises**
rather than proceeding — the trial stage was never written, because the cycle terminated at
F2 and shipping an unexercised full-validation path would put numbers in a report that nobody
computed. Reaching that line means the census no longer reproduces, which is a stop condition
and a finding in itself.

---

## 14. Recommendations to the Director

Advisory only. I am not selecting the next hypothesis and have not begun any follow-up.

1. **Close the de-risking direction on 1h perps, and state the boundary tightly.** The
   evidence supports the generalisation the assignment pre-registered, but it should be
   recorded with its scope visible: *trailing-dispersion-conditioned exposure REDUCTION on
   the nine-perp long basket, at 1h, over 2022-01…2025-04 TRAIN+VAL, measured as a quintile
   difference in forward 24-bar per-unit-risk return* — tested now with an EWMA total-vol
   estimator (T-038) and with 168-bar rolling downside, upside and total estimators (T-040).
   What is **not** established: any horizon other than 24 bars, any response other than
   per-unit-risk, daily resolution, short or market-neutral books, and cross-sectional
   (rank-within-basket) sizing rather than basket-level sizing. I would resist a closure
   phrased as "volatility sizing doesn't work" — three of those five escape hatches are cheap
   to test and one of them is the interesting one (see 3).
2. **Do not spend another cycle on a different dispersion functional.** Ulcer index, downside
   EWMA, semivariance at another window, Sortino-style denominators — these are all
   re-parameterisations of the leg that just measured *most* inverted. The `dsd` < `sd` <
   `usd` ordering is the reason: there is no remaining decomposition that isolates a
   favourable component, because the unfavourable component is the one carrying the sign.
3. **The genuinely open question is the response variable, not the conditioner.** `fwd_pur`
   normalises by *realised forward* volatility. That was the right choice for detecting an
   inversion, and it is why this census is not a volatility-clustering artifact — but it
   means the census measures **Sharpe-like** attractiveness, not money. A construct that
   scales *up* into high `dsd` would earn raw returns, and this census does not say those are
   positive; it says the return-per-unit-of-forward-risk is. Before anyone reads the
   inversion as a tradeable long signal, someone should measure the same quintile difference
   on **raw `fwd_ret`** and on **cost-adjusted raw return**. That is a cheap census on the
   existing script (one column swap) and it would settle whether §11's "relief rally" reading
   has any money in it. **I would not assign the scale-up construct before that measurement**
   — it is exactly the trap the T-038 Engineer flagged, and my diagnostics only cleared half
   of it (the sign is not a tail artifact; the ordering is still weak at ρ = +0.30).
4. **Flag BTC and ETH as cross-sectionally different, and consider that a lead rather than
   noise.** They are the two mildest on `dsd` (−0.10, −0.06) and the only two that come out
   **positive** on both `sd` and `usd`. The other seven behave alike. If a dispersion-sizing
   idea is ever revisited, a BTC/ETH-only book is where the sign is least hostile — though on
   these magnitudes it is "less negative", not positive, so I would treat this as a
   description of the cross-section rather than a hypothesis with a live edge.
5. **Three cycles now agree that 1h crypto is a reversal environment, and no cycle has tested
   that claim directly.** T-039: 1h momentum is reversal not trend. H-BearShort: crypto bears
   are crashes plus squeezes. T-040: the highest-downside-dispersion 1h windows are followed
   by the best forward per-unit-risk returns, most strongly in the bear year. The project has
   been repeatedly *bumping into* mean reversion while testing other things. A pre-registered
   1h reversal hypothesis with a proper cost gate looks better-motivated than anything left
   in the sizing family — with the obvious caveat that T-039 already measured the cost wall at
   h ≤ 8 (best gross edge 0.90× a round trip), so the horizon would have to be h ≥ 24 where
   this census's own conditioner lives.
6. **Two process items worth a line in the standards.** (a) Pin the **quantile tie
   convention** in any future census assignment (§12.5) — it moved a `D[i]` by 3.7e-03 here
   and would decide a marginal cycle. (b) Make **truncation invariance** a standard
   attestation for cycles under directive 8 (§12.6) — it is one extra pass over the data and
   it turns the warmup rule's unavoidable "read the full series" into positive evidence of no
   leakage rather than a thing the Reviewer has to take on trust.
7. **The trial ledger is still empty after three perps cycles, and criterion 7 is still
   unsatisfiable.** T-038, T-039 and T-040 all died at zero-cost pre-gates — which is the
   discipline working, and I would not weaken a gate to fix it. But it is worth naming that
   the ledger needs **10** rows before any cycle can exceed PARK, and at the current rate
   the perps program will hit its meta-review and its RESEARCH:OPS checkpoints long before
   its DSR machinery becomes usable. That is a Director/operator structural question, not
   something a cycle can resolve.
