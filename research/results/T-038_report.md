# T-038 — H-BasketVolTarget-1h — Research Engineer report

**Verdict: REJECT at pre-gate P2. Zero trials spent. Perps `n_trials` stays 0.**

The mechanism the construct depends on is not merely absent on this data — it is
**inverted**. High-trailing-volatility hours had *better* forward per-unit-risk returns
than low-volatility hours, in every robustness view tested, in every calendar year, on
8 of 9 instruments individually. De-risking into high 1h volatility would have removed
the bars on which essentially all of the basket's return was earned.

---

## 1. Task ID and hypothesis

**Task ID:** T-038 (first perps research cycle). **Program:** perps. **Cycle class:**
RESEARCH. **`n_trials` before this cycle:** 0. **Trials spent:** **0** (pre-gate stop).

Hypothesis, copied verbatim from `research/NEXT_TASK.md`:

> Scaling the equal-weight, monthly-rebalanced long basket of the 9
> `user_data/config_perp.json` perps by a single exposure multiplier
> `m_t = min(1, sigma_target / sigma_t)` — where `sigma_t` is an EWMA volatility of the
> basket's 1h returns with 48-hour half-life, `sigma_target` is the TRAIN-split median
> of `sigma_t`, and `m` is re-applied only when it drifts ≥ 0.10 from the currently-
> applied value — yields a **net TEST-split per-period (daily) Sharpe ≥ 0.135653**
> (1.10× the committed benchmark's, quoted from the manual) with **realized TEST MaxDD
> no worse than −31.27%**, because per-unit-risk basket returns decline as trailing
> volatility rises (volatility is persistent at the 1h horizon; returns do not scale
> proportionally with it).

The clause after "because" is the mechanism claim. Pre-gate P2 tests it directly, and
it is false with the sign reversed.

---

## 2. Zero-cost pre-gate result

Ladder run in the assigned order, stopping at the first failure.

| Gate | What it tests | Computed | Threshold | Result |
|---|---|---|---|---|
| **P0** | reachability (environment) | 9/9 feathers load; all cover ≥ 2025-09-19; 0 gaps > 24 h; 0 duplicate timestamps; 24,019 all-nine basket bars | must load & cover | **PASS** |
| **P1** | 1h volatility persistence | median Spearman ρ = **0.564373**; minimum **0.434160** (BTC) | median ≥ 0.30 **AND** every > 0.15 | **PASS** |
| **P2** | mechanism existence (harm census) | basket **Q1 − Q5 = −0.442905**; breadth **1 of 9** positive | KILL if Q1−Q5 ≤ 0; KILL if < 5 of 9 | **FAIL — both clauses** |
| **P3** | cost-free upper bound | — | — | **not reached** |
| **P4** | TEST activity floor | — | — | **not reached** |

Sections 7, 8 and 9 state "not reached" accordingly.

### P0 — reachability (PASS)

| instrument | raw bars | raw span | window bars | worst internal gap | gaps > 24 h | dup ts |
|---|---:|---|---:|---|---:|---|
| BTC/USDT:USDT | 38,587 | 2022-01-01 … 2026-05-27 | 24,025 | 1 h | 0 | no |
| ETH/USDT:USDT | 38,612 | 2022-01-01 … 2026-05-28 | 24,025 | 1 h | 0 | no |
| SOL/USDT:USDT | 38,612 | 2022-01-01 … 2026-05-28 | 24,025 | 1 h | 0 | no |
| BNB/USDT:USDT | 30,062 | 2022-12-23 … 2026-05-28 | 24,019 | 1 h | 0 | no |
| XRP/USDT:USDT | 38,612 | 2022-01-01 … 2026-05-28 | 24,025 | 1 h | 0 | no |
| ADA/USDT:USDT | 38,612 | 2022-01-01 … 2026-05-28 | 24,025 | 1 h | 0 | no |
| AVAX/USDT:USDT | 38,612 | 2022-01-01 … 2026-05-28 | 24,025 | 1 h | 0 | no |
| DOT/USDT:USDT | 38,612 | 2022-01-01 … 2026-05-28 | 24,025 | 1 h | 0 | no |
| LINK/USDT:USDT | 38,612 | 2022-01-01 … 2026-05-28 | 24,025 | 1 h | 0 | no |

BNB's 1h history begins **2022-12-23 06:00 UTC**, not 00:00. The other eight have bars
from 00:00 that day, so **6 union bars have a missing leg and were dropped**: a bar on
which one of the nine does not exist is not a bar of a nine-instrument basket. Basket
window **2022-12-23 06:00 → 2025-09-19 00:00, 24,019 bars**.

### P1 — volatility persistence (PASS)

TRAIN+VAL 1h log returns, per instrument. Spearman ρ between `sigma_t` (EWMA half-life
48, as specified) and realized vol over t+1…t+24. n = 20,369 per instrument (TRAIN+VAL
minus the last 24 bars, so no forward window reaches into TEST).

| instrument | ρ(sigma_t, forward rv) | ρ(trailing rv, sigma_{t+24}) — reversed census |
|---|---:|---:|
| BTC/USDT:USDT | 0.434160 | 0.705125 |
| ETH/USDT:USDT | 0.525241 | 0.743695 |
| SOL/USDT:USDT | 0.540947 | 0.759879 |
| BNB/USDT:USDT | 0.559363 | 0.768557 |
| XRP/USDT:USDT | 0.571900 | 0.773286 |
| ADA/USDT:USDT | 0.617874 | 0.791353 |
| AVAX/USDT:USDT | 0.612359 | 0.788018 |
| DOT/USDT:USDT | 0.638522 | 0.801384 |
| LINK/USDT:USDT | 0.564373 | 0.764974 |

**median 0.564373 ≥ 0.30 → PASS. minimum 0.434160 (BTC) > 0.15 → PASS.**

Both mandatory sanity checks were executed and are reported, not assumed:

- **(a) −k vs +k must differ.** The forward and reversed censuses differ on all nine
  (smallest gap 0.200 on LINK; largest 0.271 on BTC). The script **raises** if any pair
  matches to 1e-9. No exact k↔−k symmetry — the bug signature is absent.
- **(b) suspicious cleanliness.** No correlation is exact to 4 dp; the values are not
  monotone in any instrument ordering. Nothing flagged.

**1h volatility is strongly persistent on this data.** The construct's *forecasting*
premise is sound. What fails is the premise about what that forecast is worth.

### P2 — mechanism existence, harm census (FAIL — this is the verdict)

TRAIN+VAL, n = 20,370 basket bars. Bars bucketed into quintiles by `sigma_t` (edges
from TRAIN+VAL); per bar, forward 24-bar per-unit-risk return = (Σ log returns t+1…t+24)
/ (std of log returns t+1…t+24); averaged within quintile.

Sigma quintile edges, annualised: `0.003548 · 0.430994 · 0.527737 · 0.629592 · 0.794877 · 1.746258`

| quintile (by trailing sigma) | n | mean forward 24-bar per-unit-risk return |
|---|---:|---:|
| Q1 (lowest vol) | 4,074 | **+0.393508** |
| Q2 | 4,074 | +0.339667 |
| Q3 | 4,074 | +0.196651 |
| Q4 | 4,074 | +0.742229 |
| Q5 (highest vol) | 4,074 | **+0.836413** |

> **Q1 − Q5 = −0.442905.** Gate: **KILL if ≤ 0** → **KILLED**.

Moving-block bootstrap 90% CI on Q1 − Q5 (block 168 bars, 2,000 resamples, seed 7):
**[−1.210815, +0.344539]**, median −0.444336, share of resamples > 0 = **0.1705**.
**Reported, not gating** — the gate is on sign and breadth, as specified. The CI is wide
and straddles zero, which is the honest statement of how precisely the *magnitude* is
known; the *sign* is what the gate reads, and it is stable across every view in §5.

**1-bar-forward diagnostic** (per-unit-risk is undefined for a single bar — the standard
deviation of one observation — so two faithful analogues are reported):

| quintile | mean forward 1-bar log return | mean (forward 1-bar / sigma_t) |
|---|---:|---:|
| Q1 | −0.00001800 | −0.00017817 |
| Q2 | −0.00002678 | −0.00005134 |
| Q3 | −0.00003429 | −0.00005249 |
| Q4 | +0.00009026 | +0.00010857 |
| Q5 | +0.00030719 | +0.00027291 |

Q1 − Q5 raw = **−0.00032518**; scaled = **−0.00045108**. Same sign, same conclusion, on
a statistic that shares no forward-window construction with the gating one.

**Secondary, per instrument** (per-asset quintile edges, n = 20,369 each):

| instrument | Q1 mean | Q5 mean | Q1 − Q5 | sign |
|---|---:|---:|---:|:--:|
| BTC/USDT:USDT | +0.289797 | +0.808256 | −0.518459 | − |
| ETH/USDT:USDT | +0.253081 | +0.452708 | −0.199628 | − |
| SOL/USDT:USDT | −0.123524 | +0.526203 | −0.649727 | − |
| BNB/USDT:USDT | +0.169874 | +0.995932 | −0.826057 | − |
| XRP/USDT:USDT | +0.210813 | +0.389546 | −0.178733 | − |
| **ADA/USDT:USDT** | +0.154651 | −0.027134 | **+0.181785** | **+** |
| AVAX/USDT:USDT | −0.147845 | +0.501798 | −0.649644 | − |
| DOT/USDT:USDT | +0.044702 | +0.231704 | −0.187003 | − |
| LINK/USDT:USDT | −0.107197 | +0.144903 | −0.252100 | − |

> **1 of 9 positive.** Gate: **KILL if fewer than 5 of 9** → **KILLED**.

Both P2 KILL clauses fired independently. ADA is the lone instrument on the hypothesised
side, and it is the only one whose Q5 mean is negative at all.

---

## 3. Implementation notes

Every construction constant is pre-registered in `NEXT_TASK.md`; none was chosen here.
All three scripts print every intermediate number, because `NEXT_TASK.md` states that a
pre-gate stop is a verdict and will be independently rerun.

**Basket construction.** `build_basket()` in `phase_t038_bvt.py` is a direct
transcription of the committed benchmark's own loop
(`user_data/research/perps_benchmark.py:build_benchmark(rebalance=True)`): equal weight
1/9; weights drift between rebalances; reset to 1/9 at the **last bar of each calendar
month, final bar excluded**; each rebalance charges `per_side_cost × Σᵢ|w_target,ᵢ −
w_drift,ᵢ|`; entry at bar 0 is the same formula against `w_drift = 0`, i.e. exactly one
per-side cost. The only difference from the benchmark is resolution — "last trading bar
of the month" resolves to the month's final **hour** on 1h bars. Realized: **33
rebalances**, mean turnover **0.100571**, total basket cost **0.003887** of notional.
(The daily benchmark records 33 rebalances and mean turnover 10.05% — the 1h path
reproduces both, which is a useful cross-check that the mirrored convention is right.)

**Volatility estimate.** `ret.ewm(halflife=48, adjust=True).std() × sqrt(8760)`. pandas
maps `halflife=48` to `alpha = 1 − exp(−ln2/48)`, i.e. decay `λ = 2^(−1/48) =
0.985663199` — the constant `NEXT_TASK.md` pre-registers, matched exactly rather than
approximated. `adjust=True` makes the early values an expanding weighted estimate
converging to the EWMA, which is the "initialized as an expanding estimate over the
first 96 bars" the spec asks for. Computed **once over the full pre-holdout series, then
sliced** — never per split (Standing Directive 8). Two estimator details the spec does
not pin, stated for the record: pandas' `ewm.std()` takes deviations from the EWM mean
(not from zero, as RiskMetrics does) and applies the `bias=False` debiasing factor.
Both are ~1% uniform effects on `sigma_t` that **cancel in `sigma_target / sigma_t`**,
since `sigma_target` is the TRAIN median of the same series; and P1/P2 use `sigma_t`
only for rank ordering, which no monotone rescaling changes.

**Target.** `sigma_target` = median of `sigma_t` over TRAIN only, excluding the 96
burn-in bars: **0.540308** annualised, from **16,699** TRAIN observations. TRAIN sigma
range 0.206619 … 1.614508. Computed once; never revisited.

**Multiplier.** `m_raw = min(1.0, sigma_target/sigma_t)`, forced to 1.0 for the first 96
bars. No-trade band: the applied multiplier adopts `m_raw` only when
`|m_raw − m_applied| ≥ 0.10`; a single sequential pass, band = 0.10, no sweep.

**Lag.** `validator.signal_to_returns` clips its signal to {−1, 0, 1} and so cannot
carry a fractional weight. Its lag arithmetic was therefore **replicated manually**, as
`NEXT_TASK.md` construct item 6 anticipates: `position[t] = m_applied[t−2]`, the same
2-bar convention (`signal_to_returns` line 528: `position = signal.shift(2)`). This is
stated in the report as the spec requires.

**Costs.** `per_side = validator.per_side_cost("taker")` — never a literal. Resolved
value **0.0009** (9.00 bps/side, 18.00 bps round trip). Candidate stream (built, not
reached by a gate): `m_pos × ret_gross − m_pos × basket_rebalance_cost − |Δm_pos| ×
per_side`; the un-invested fraction earns zero.

**Deviation from `NEXT_TASK.md`, requested by it:** deliverable 4 directs the Engineer
**not** to write `research_index.md`, `research_metrics.md` or
`strategy_iteration_log.md` this cycle, assigning that maintenance to the Reviewer. The
standing Engineer prompt lists the latter two as Engineer bookkeeping. `NEXT_TASK.md` is
the cycle contract and is followed; **none of the three files was modified.** Flagged
here so the Reviewer knows the omission is instructed, not forgotten. (It is also nearly
moot: a pre-gate stop produces no headline performance numbers and advances no counter.)

**Material implementation decision — the date boundary on hourly bars.** See §5 and the
BLOCKING NOTE in §12. `validator.HOLDOUT_BOUNDARIES["perps"]` is
`Timestamp("2025-09-19", tz="UTC")` — **midnight**, not end-of-day — and
`assert_no_holdout()` rejects anything strictly after that instant while
`split_by_dates()` slices on `idx <= end`. Both were written for daily bars, where the
date label *is* the bar. On hourly bars they exclude the last 23 hours of each boundary
date. `NEXT_TASK.md` mandates calling `assert_no_holdout()` on every frame, so the
guard-compliant reading was taken: **the evaluation series ends at 2025-09-19 00:00
UTC**. Immaterial to P0–P2 (23 bars at an edge of a 20,370-bar census); **not**
immaterial to the criterion-3 daily pairing the trial would have needed. No assumption
was made about the trial step — it was never reached, and §12 records the conflict for
the Director rather than resolving it.

**Files created** (none modified; no frozen `phase*.py` touched):

- `user_data/research/phase_t038_bvt.py` — the ladder, P0 → P4.
- `user_data/research/phase_t038_diag_p2_verify.py` — independent P2 recomputation + 4 artifact probes.
- `user_data/research/phase_t038_diag_lookahead.py` — L1–L5 leakage verification.
- `research/results/T-038_raw/` — all stdout and JSON (§13).

---

## 4. Compliance attestations

**`user_data/data/` is untouched.**

```
$ git status --porcelain user_data/data/
(no output)
$ git diff --stat -- user_data/data/
(no output)
$ git diff --stat --cached -- user_data/data/
(no output)
```

No `freqtrade download-data`, no `scripts/data_manifest.py build`, no write of any kind
into that tree. No new external data axis was assigned and none was fetched.

**Data manifest verification — passed, not bypassed.**

```
$ python scripts/data_manifest.py verify
OK: 52 files match the manifest (built 2026-07-29T07:58:59Z).
```

`validator.DATA_INTEGRITY` at import time on every run:
`{'ok': True, 'built_utc': '2026-07-29T07:58:59Z', 'checked_count': 52,
'recorded_count': 52, 'modified': [], 'missing': [], 'extra': [], 'bypassed': False}`.
`FREQTRADE_SKIP_DATA_VERIFY` was never set; `bypassed` is `False` on all three runs.

**Resolved cost model** — from `validator.describe_cost_model("taker")`, printed by the
script, not typed from memory:

```
okx_usdt_perp / regular (non-VIP, no fee discounts) / fill=taker:
maker 2.0bps, taker 5.0bps, slippage 3.0bps/side, spread 2.0bps,
adverse selection unset -> 9.00bps/side, 18.00bps round trip
```

Venue `okx_usdt_perp`; fill assumption **`taker`**; per-side **0.0009**; round trip
**0.0018**. `maker_optimistic` appears nowhere in this cycle. Every cost in the code
resolves from `validator.per_side_cost()`; no fee, slippage or spread number is
hardcoded anywhere in the three scripts. Mandatory accompanying warning, verbatim:

> COST MODEL NOTE - slippage (3.0 bps/side) and spread (2.0 bps) are estimates, not
> calibrated against realized fills. Fee rates are published OKX regular (non-VIP, no
> fee discounts) rates for okx_usdt_perp as of 2026-07-28.

**Split dates and reserved holdout.** `validator.split_by_dates(df, "2024-11-22",
"2025-04-21", "2025-09-19")` — the frozen perps triple, date-pinned.
`split_70_15_15()` appears nowhere. `enforce_holdout=False` appears nowhere.
`validator.assert_no_holdout(..., program="perps")` was called on the full window and on
every train / val / test frame and on the sigma series, and passed every time.

| split | bars | span |
|---|---:|---|
| full | 24,019 | 2022-12-23 06:00 → 2025-09-19 00:00 |
| train | 16,795 | 2022-12-23 06:00 → 2024-11-22 00:00 |
| val | 3,600 | 2024-11-22 01:00 → 2025-04-21 00:00 |
| test | 3,624 | 2025-04-21 01:00 → 2025-09-19 00:00 |
| TRAIN+VAL (P1–P3 census) | 20,395 | — |

**Reserved holdout was untouched.** Bars after 2025-09-19 00:00 UTC (the series run on
to 2026-05-28) were sliced off as the first operation in `p0_reachability()`, before any
computation. TEST was used only by P4, which was never reached; **the P1 and P2 censuses
that produced this verdict ran on TRAIN+VAL alone**, and their forward windows were
truncated so that not one reaches into TEST (verified, §5 L3).

**DSR entry point.**

```
$ python scripts/check_dsr_entrypoint.py
VIOLATIONS: 0
OK: no research file imports freqtrade_dsr directly.
```

No DSR was computed: no trial was spent, so there is no TEST return stream to deflate
and nothing to append to `research/trial_sharpe_ledger.csv` (still 0 rows).

**Falsification conditions transcribed literally** (Reviewer duty — code lines given):

| spec text | code | reading |
|---|---|---|
| P1 "median … ≥ 0.30 **AND** every instrument > 0.15" | `phase_t038_bvt.py` `ok_med = med >= P1_MEDIAN_MIN` / `ok_all = (vals > P1_EVERY_MIN).all()` / `verdict = ok_med and ok_all` | `and`, `>=` and `>` exactly as written |
| P2 "**KILL if** (Q1 − Q5) ≤ 0" | `ok_primary = d > 0` | pass iff strictly > 0; kill on ≤ 0 |
| P2 "**KILL if** fewer than 5 of 9 … show Q1 − Q5 > 0" | `n_pos += int(c["q1_minus_q5"] > 0)`; `ok_breadth = n_pos >= 5` | strict `> 0` per instrument; `>= 5` breadth |
| P2 two KILL clauses combined | `verdict = ok_primary and ok_breadth` | either KILL clause firing kills the gate |

The last row is the only place a reading had to be chosen: the spec lists two
independent KILL conditions rather than one compound one, so the gate survives only if
neither fires — the `and` of the two pass-conditions. **Not outcome-determining here:
both clauses fired.** Recorded because the manual requires `and`/`or` choices to be
reported whether or not they changed the answer.

---

## 5. Lookahead / leakage checks performed

Run by `phase_t038_diag_lookahead.py`; full output in §13. These were **executed**, not
asserted.

**L1 — `sigma_t` uses only bars ≤ t. PASS.** The EWMA was recomputed on the series
*truncated at t* and its last value compared to the full-series value at t, at five
probe points spanning the window (i = 200, 1000, 8000, 19019, 24018). **Bit-identical at
every probe** (`atol=0, rtol=0`), e.g. i = 24018 → 0.461670174102 both ways. If sigma
had absorbed any future bar the truncated value would differ.

**L2 — the forward window covers t+1…t+24 and excludes t. PASS.** (a) The rolling
sum/std at t was compared against a hand-built sum over positions t+1…t+24 at three
probes; matched to 1e-12 on all six comparisons. (b) Bar t alone was perturbed by +0.5:
the forward window at t moved by **4.163e-17** (pandas' rolling accumulator carries
float noise into all later values), while an **independent numpy slice reference gave
exactly 0.0**; and the windows that *did* move were exactly the 24 at t−24…t−1, the ones
that legitimately contain bar t. *An earlier version of this probe used exact equality
and reported a failure on that 4e-17; the numpy reference is what settles it, and the
tolerance is now three orders of magnitude above the measured noise floor.*

**L3 — no censused forward window reaches into TEST. PASS.** The census index is
TRAIN+VAL minus its last 24 bars. Last censused bar 2025-04-20 00:00; its forward window
ends 2025-04-21 00:00 = the last TRAIN+VAL bar; first TEST bar 2025-04-21 01:00. Zero
overlap.

**L4 — indicators computed before splitting.** `sigma` is computed once on the full
pre-holdout series and sliced. Recomputing it per split instead would deviate by up to
**0.2365** annualised (and produce NaN on the split's first bar) — the warmup-truncation
defect quantified rather than merely avoided.

**L5 — holdout untouched. PASS.** `assert_no_holdout` on `closes`, `basket`, `sigma`,
`train`, `val`, `test`, all clean; last bar evaluated anywhere is 2025-09-19 00:00.

**Survivorship** is present and not removed: the nine are `config_perp.json`'s 2026
whitelist backtested from 2022. It biases the *benchmark* upward, and here it affects
the census only through which instruments are in the basket at all. Unchanged from the
benchmark record §6.

**>100% CAGR defect presumption — not triggered.** No backtest was run and no return or
CAGR figure is reported: the ladder stopped at a census over historical returns. The
only Sharpe-like numbers in §5's cross-check are diagnostic quintile statistics on the
*unmodified* basket, not on any strategy.

### Independent verification of the P2 stop

Because the entire verdict rests on one census, `phase_t038_diag_p2_verify.py`
recomputes it through a different code path — plain numpy `argsort` ranks and integer
bucketing, sharing no pandas `quantile`/`cut`/`groupby` code with the gating
implementation — and probes the four ways the stop could be an artifact.

| view | Q1 − Q5 | n | sign |
|---|---:|---:|:--:|
| **V1** independent recomputation (numpy ranks) | **−0.442905** | 20,370 | − |
| **V2** first 96 burn-in bars excluded | −0.434451 | 20,275 | − |
| **V3a** disjoint forward windows, offset 0 | −0.605279 | 848 | − |
| **V3b** disjoint forward windows, offset 8 | −0.384368 | 849 | − |
| **V3c** disjoint forward windows, offset 16 | −0.358513 | 849 | − |
| **V4** calendar 2023 only | −0.044174 | 8,760 | − |
| **V4** calendar 2024 only | −1.302706 | 8,784 | − |
| **V4** calendar 2025 only (to 04-21) | −1.094976 | 2,617 | − |

- **V1** reproduces the gating number to 6 dp through independent code. It is the number.
- **V2** answers whether the 96 expanding-EWMA burn-in bars (sigma as low as 0.0036
  annualised, all landing in Q1) manufacture the sign. They do not: −0.434 without them.
- **V3** answers the overlapping-window objection — the census evaluates a 24-bar
  forward window on *every* bar, so neighbours share 23/24 of their data. Taking every
  24th bar makes the windows disjoint. All three offsets are negative, two of them more
  strongly than the pooled figure.
- **V4** answers "is this one episode?". Negative in every calendar year with enough
  bars to report, including 2023 (a year of near-parity, −0.044) and 2024/2025 (strongly
  negative). It is not one episode.

**Direction cross-check using a different statistic entirely** — no forward window, no
per-unit-risk ratio. Realized basket returns restricted to the bars the construct would
actually have acted on (trailing sigma lagged 2 bars), TRAIN+VAL:

| quintile of trailing sigma | n | mean 1h return | sd | Sharpe (ann.) | total return |
|---|---:|---:|---:|---:|---:|
| Q1 (lowest vol) | 4,079 | +0.00003012 | 0.004584 | **+0.6150** | **+8.32%** |
| Q2 | 4,078 | −0.00003135 | 0.005713 | −0.5135 | −17.71% |
| Q3 | 4,078 | −0.00001690 | 0.006093 | −0.2596 | −13.49% |
| Q4 | 4,078 | +0.00016034 | 0.007893 | +1.9012 | +69.33% |
| Q5 (highest vol) | 4,079 | +0.00030795 | 0.010288 | **+2.8015** | **+182.77%** |

**The highest-volatility quintile has the highest risk-adjusted return, by a factor of
4.6 in Sharpe over Q1, and carries essentially all of the basket's TRAIN+VAL return.**
The construct would have systematically reduced exposure into exactly those bars. This
is the mechanism failing on merit, verified five independent ways.

---

## 6. Variants attempted

**Budget: 1 variant, 0 optimization runs. Used: 0 and 0.**

| # | run | outcome |
|---|---|---|
| — | (none) | The ladder stopped at P2, which precedes any variant being evaluated. No strategy variant was backtested, no parameter was swept, no seed re-drawn, no window re-selected. |

Every run performed is a pre-gate census or a verification of one, all on TRAIN+VAL, all
zero-cost by the manual's definition. HL 48, band 0.10, cap 1.0 and the TRAIN-median
target were used exactly once each, as pre-registered; no neighbour was evaluated.
Diagnostics in §5 (V1–V4, cross-check, L1–L5) re-measure the *same* pre-registered
construct's inputs — they are not variants and consume no budget.

**Trials spent: 0.** `research/trial_sharpe_ledger.csv` unchanged (0 rows). Perps
`n_trials` remains **0**, leaving 30 of the 30-trial program cap.

---

## 7. Backtest results

**Not reached.** The ladder stopped at P2 before any trial. No backtest was run, so no
headline metric, config, or return stream exists for this cycle.

Construct diagnostics computed on the way to the gate (descriptive, not performance):

| quantity | value |
|---|---:|
| `sigma_target` (TRAIN median, annualised) | 0.540308 |
| mean `m_raw` / mean `m_applied` (full window) | 0.8597 / 0.8288 |
| share of bars `m_raw < 1.0` / `m_applied < 1.0` | 0.5797 / 0.9698 |
| share of bars `m_raw < 0.9` / `m_applied < 0.9` | 0.4399 / 0.4567 |
| exposure changes over the full window | 249 |
| Σ\|Δm_applied\| over the full window | 30.207 |
| basket rebalances / mean turnover / total cost | 33 / 0.100571 / 0.003887 |

## 8. Walk-forward / out-of-sample results

**Not reached.** No walk-forward was run: it belongs to the trial, which the pre-gate
stop prevented. The P1/P2 censuses are TRAIN+VAL only; TEST was never scored.

## 9. DSR and other required statistics

**Not reached.** No DSR was computed — there is no candidate return stream, no trial was
spent, and `validator.deflated_sharpe()` was not called. `n_trials` stays 0 and the
ledger stays at 0 rows. `scripts/check_dsr_entrypoint.py` reports 0 violations.

For the record, had the trial run, criterion 7 would have capped the verdict at **PARK**
regardless of results (`trial_var_source` would be `estimator_proxy` at 0 ledger rows).
**PROMOTE was unreachable this cycle by construction**, and nothing here was worked
toward it.

The statistical-power quantities the task pre-registered (achieved ρ, `sharpe_difference_se`,
implied t on the 151-bar TEST pairing) are **not computable** without the trial and are
not reported. `NEXT_TASK.md` required them only "at trial".

---

## 10. Verdict vs. falsification statement

The pre-registered falsification statement lists five conditions, any of which rejects.

| # | condition | fired? | evidence |
|---|---|:--:|---|
| 1 | P1 fails — 1h volatility not persistent | **no** | median ρ 0.564373 ≥ 0.30; min 0.434160 > 0.15 |
| 2 | **P2 fails — high-trailing-vol hours do NOT have worse per-unit-risk forward returns (mechanism absent)** | **YES** | basket Q1 − Q5 = **−0.442905** (KILL if ≤ 0); breadth **1 of 9** (KILL if < 5) |
| 3 | P3 fails | n/a | not reached |
| 4 | P4 fails | n/a | not reached |
| 5 | trial-level bars missed | n/a | not reached; zero trials |

**Falsification condition 2 fired. The hypothesis is REJECTED at pre-gate P2, at zero
trials.** Per `NEXT_TASK.md` and the manual, a pre-gate stop spends no trial and is a
complete, successful research cycle.

The rejection is stronger than "mechanism absent": the mechanism is **present with the
opposite sign**. The hypothesis's stated causal clause — "per-unit-risk basket returns
decline as trailing volatility rises" — is contradicted by the data, in every year and
on 8 of 9 instruments.

---

## 11. Regime behavior

- **Where the construct's forecast works:** everywhere. Volatility clustering at 1h is
  strong and uniform — ρ 0.43–0.64 across all nine instruments, no weak leg. The risk
  *forecast* is not the problem.
- **Where the economics fail:** everywhere in this window, and worst in trending years.
  Q1−Q5 is −0.044 in 2023, −1.303 in 2024, −1.095 in 2025-to-April. 2023 (a
  broad-based, comparatively steady advance) is close to neutral; 2024 and early 2025,
  which contained the sharp legs, are strongly adverse. The construct's *predicted* good
  regime — vol-clustered drawdowns — is where the census says it would have hurt most.
- **Mechanically why:** in this sample high-volatility hours in the perp basket are
  predominantly high-volatility *rallies*, not cascading liquidations. `NEXT_TASK.md`
  named that as the expected failure mode ("the construct de-risks into upside vol; the
  cap at m ≤ 1 means it can never overweight calm rallies to compensate"), and the harm
  census confirms it before any money was modelled: Q5 alone carries +182.77% of the
  +8.32%/−17.71%/−13.49%/+69.33%/+182.77% quintile decomposition.
- **The one exception:** ADA is the only instrument whose Q5 forward per-unit-risk
  return is negative (−0.027) and the only positive Q1−Q5 (+0.182). Nine instruments is
  too few for that to be more than a note.

Funding P&L is excluded from candidate and benchmark alike — the earliest held funding
datum is 2026-02-26 and the evaluation window ends 2025-09-19, so there is zero overlap
and no series to include. No proxy, interpolation or backfill was invented. Direction of
the resulting bias: the candidate holds *less* long exposure on average (mean m ≈ 0.83),
and longs pay funding in contango, so the exclusion flatters the **benchmark** more than
the candidate — i.e. **anti-candidate**, conservative with respect to promotion. It has
no bearing on this verdict, which was decided by a gross-return census.

---

## 12. Lessons

1. **A vol-target overlay on a long-only crypto perp basket needs its harm census before
   anything else, and at 1h on this venue it fails with the sign reversed.** Volatility
   persistence (P1) and mechanism existence (P2) are genuinely orthogonal, exactly as
   the manual says: this construct passed P1 as decisively as it failed P2 (ρ 0.56
   median; Q1−Q5 −0.44). Passing a persistence test tells you the estimator works, not
   that the trade works.

2. **This is the H-IVSizing finding again, on a different axis, at a different
   resolution, on a different venue and cost model.** H-IVSizing (spot, 2026-07-12)
   found that days where implied vol exceeded realized had *better* forward returns.
   T-038 finds that hours with high *realized* vol have better forward per-unit-risk
   returns. Two independent constructs, two different volatility measures, two
   programs, same conclusion: **in this asset class, de-risking on a volatility signal
   selects out good bars.** That is now a pattern rather than a one-off, and the next
   volatility-conditioned de-risking proposal should be expected to fail P2 unless it
   carries a specific reason why its volatility measure separates crash vol from rally
   vol.

3. **Volatility-target sizing does not transfer from the spot program.** It was the
   spot program's single most durable component across ~97 constructs. On perps at 1h
   it does not survive its own zero-cost pre-gate. The T-037 transition brief's
   instruction to treat spot numbers as void was correct, and this cycle is a concrete
   instance of a "durable" spot mechanism failing immediately on the new venue and
   resolution — the carried-forward finding ("risk-management mechanisms survived") is
   weaker than it looked.

4. **BLOCKING NOTE for the Director — the holdout boundary is not hour-aware, and the
   next 1h cycle that reaches a trial will hit it.** `HOLDOUT_BOUNDARIES["perps"] =
   Timestamp("2025-09-19", tz="UTC")` is midnight. On daily bars the date label and the
   bar coincide, so the constant means "the 2025-09-19 daily bar is the last included".
   On 1h bars, `assert_no_holdout()` rejects every bar after 00:00 and `split_by_dates()`
   truncates at 00:00, so the last 23 hours of the boundary date are dropped. Consequence
   for criterion 3, concretely: the guard-compliant TEST slice is 2025-04-21 01:00 →
   2025-09-19 00:00, which daily-aggregates to **152** UTC dates with a 23-hour first day
   and a **1-hour last day**, against the benchmark's **151** complete days. The task
   requires N = 151 on identical dates or the comparison is VOID. The construction that
   *does* produce 151 complete days (2025-04-22 00:00 → 2025-09-19 23:00) is exactly the
   one `assert_no_holdout()` refuses. **This cycle did not have to resolve it — P2 stopped
   the ladder first — and it was not resolved here.** It needs a Director/operator
   decision before any 1h perps candidate can be scored against the benchmark: either an
   hour-aware boundary (`2025-09-19 23:00`) declared explicitly and recorded as such, or
   an equally explicit rule for aggregating partial boundary days. Note that changing the
   boundary is governed by "THE BOUNDARY IS FIXED … it may not be moved after any perps
   result has been measured against it" — the benchmark has been measured against it, so
   this is a declaration question, not an edit.

5. **Small data note, harmless but worth recording:** BNB's 1h series begins at
   **06:00** on 2022-12-23, not 00:00. Six union bars therefore lack a leg and were
   dropped, giving 24,019 basket bars rather than 24,025. Any future 1h basket work on
   the nine will meet the same six bars.

6. **The 0.10 no-trade band is stickier than it looks on a capped multiplier.** `m_raw`
   is below 1.0 on 58% of bars, but `m_applied` is below 1.0 on **97%** — once the
   applied value parks at, say, 0.94, a return to `m_raw = 1.0` is only a 0.06 drift and
   never triggers. Both are below 0.9 on ~44–46% of bars, so the *magnitude* of exposure
   reduction is similar; it is the "fully invested" state that the band effectively
   abolishes. Any future band-based rebalance rule against a **capped** signal should
   expect the cap to be almost never re-attained, and should say whether that is intended.

---

## 13. Raw output locations

Every figure in this report is traceable to one of these. All paths repo-relative.

| artifact | path |
|---|---|
| ladder script (P0→P4) | `user_data/research/phase_t038_bvt.py` |
| ladder stdout, verbatim | `research/results/T-038_raw/T-038_pregate_output.txt` |
| ladder machine-readable results | `research/results/T-038_raw/T-038_pregates.json` |
| P2 independent verification script | `user_data/research/phase_t038_diag_p2_verify.py` |
| P2 verification stdout | `research/results/T-038_raw/T-038_p2_verification_output.txt` |
| P2 verification JSON | `research/results/T-038_raw/T-038_p2_verification.json` |
| look-ahead verification script | `user_data/research/phase_t038_diag_lookahead.py` |
| look-ahead stdout | `research/results/T-038_raw/T-038_lookahead_output.txt` |
| look-ahead JSON | `research/results/T-038_raw/T-038_lookahead.json` |
| this report | `research/results/T-038_report.md` |
| inputs (read-only, unmodified) | `user_data/data/okx/futures/{BTC,ETH,SOL,BNB,XRP,ADA,AVAX,DOT,LINK}_USDT_USDT-1h-futures.feather` |
| benchmark record mirrored for conventions | `research/benchmarks/perps_equal_weight_benchmark.md`, `user_data/research/perps_benchmark.py` |

**Reproduction:** `python user_data/research/phase_t038_bvt.py`, then
`phase_t038_diag_p2_verify.py`, then `phase_t038_diag_lookahead.py`. All are
deterministic (seeds 7 for the bootstrap and the unreached P3 shuffle) and read only
committed, manifest-verified data. No script writes to `user_data/data/`. No script
fetches anything. **No streams CSV was written** — `T-038_basket_multiplier_full.csv` is
emitted only on the all-pre-gates-pass path, which was not taken; the multiplier series
is fully reconstructible from the script and the committed feathers.

---

## 14. Recommendations to the Director

Advisory only. I am not selecting the next hypothesis and have not begun any of this.

1. **Treat "volatility-conditioned de-risking" as a family at risk of closure, but do
   not close it on this cycle alone.** Two constructs on two programs now die on the
   same finding (§12 lesson 2). What has actually been falsified is *de-risking on a
   volatility LEVEL signal in a long-only crypto book*. What has **not** been tested is
   whether a measure that distinguishes downside vol from upside vol behaves
   differently — the whole failure here is that Q5 is dominated by high-volatility
   rallies. A semivariance / downside-deviation conditioning variable is a structurally
   different mechanism on the same axis, and its P2 census is cheap: the same script
   with the bucketing variable swapped. **I would consider that worth one pre-gate, and
   I would kill it fast if its Q1−Q5 also comes back negative** — that would be a third
   independent confirmation and would justify closing the family properly.

2. **The 1h sample is real and worth using, and this cycle is evidence for that, not
   against it.** 20,370 census bars resolved a mechanism question decisively, with a
   consistent sign across three disjoint-window subsamples and three calendar years. The
   151-bar daily TEST could not have distinguished any of this. The manual's designation
   of 1h as the preferred perps sample is well founded and the harness handles it fine.

3. **Fix the hourly boundary before assigning another 1h cycle** (§12 lesson 4). This is
   the single thing most likely to block the *next* 1h cycle rather than this one, and
   it is an operator decision, not something an Engineer can resolve inside a cycle. It
   is cheap to fix and expensive to hit at the trial step, after the pre-gates have been
   paid for.

4. **A side-observation the metrics do not show, offered without a claim attached:**
   the quintile decomposition in §5 is extreme — Q2 and Q3 are *negative* over TRAIN+VAL
   while Q4 and Q5 carry everything. That is a much stronger statement than "vol timing
   does not work"; it says returns in this basket are concentrated in high-volatility
   states to a degree that would make *any* exposure rule keyed on volatility level
   harmful in the de-risking direction, and would make the opposite sign (scale **up**
   in high vol) look attractive in-sample. **I would treat that inverted construct as a
   trap and not test it**: it is an unhedged leveraged long on a 2023–2025 crypto bull
   sample, its in-sample result is guaranteed by the same decomposition that killed this
   cycle, and the drawdown behaviour it implies in a real deleveraging episode is not
   present anywhere in this window. If it is ever tested, it should be pre-gated on a
   crash sample the current window does not contain.

5. **Cheap tightening for future harm censuses:** the moving-block bootstrap CI here was
   wide enough to straddle zero (share > 0 = 0.17) while the sign was stable across every
   subsample. That is a real tension and the gate's design — sign and breadth, CI
   reported — handled it correctly. But it means the CI adds little at these block
   lengths. If the Director wants an inferential statement rather than a sign, the
   per-year and disjoint-window views (§5 V3/V4) carried far more information per line
   of code, and I would put those in the spec rather than the bootstrap.
