# T-039 / H-IntradayEdgeFloor-1h — Research Engineer report

**VERDICT: REJECT.** Of the 72 pre-registered cells, **0 satisfy G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5.** The
pre-registered falsification condition fired.

**Trial accounting: `n_trials` 0 → 0** (perps program, cap 30). **`research/trial_sharpe_ledger.csv`
0 data rows → 0 data rows.** No strategy variant was evaluated, no optimization was run, no candidate
was produced, no DSR was computed, nothing was appended to the ledger.

Produced by `user_data/research/phase_t039_census.py`, single deterministic run, seed 20260803.
All raw artifacts in `research/results/T-039_raw/`. Section 13 maps every figure below to its file.

---

## 1. Task ID and hypothesis

**Task ID**: T-039 · **Program**: `perps` · **Cycle type**: RESEARCH · **Hypothesis**:
H-IntradayEdgeFloor-1h

Copied verbatim from `research/NEXT_TASK.md`:

> **On the nine OKX USDT perpetual swaps at 1h, there exists at least one (state variable, horizon,
> tail) cell — drawn from a pre-registered family of 6 variables × 6 horizons × 2 tails = 72 cells,
> every variable computable causally from 1h OHLCV+volume at bar close — whose decile-conditional
> forward return, measured on TRAIN+VAL only, exceeds the unconditional forward return by at least
> 36.0 bps (2 × the 18.0 bps taker round trip), holds that sign in at least 5 of the 9 instruments
> individually, and exceeds the 95th percentile of a family-wise circular-shift placebo distribution.**

---

## 2. Zero-cost pre-gate result

**The entire cycle is the pre-gate. Result: FAIL → hypothesis REJECTED.**

| Gate | Threshold | Cells clearing | Note |
|---|---|---|---|
| **G0** Coverage | all 9 load, strictly increasing, no duplicates | **PASS** (9/9) | 338,933 pooled full-series bars |
| **G1** Non-degeneracy | ≥1,000 pooled ∧ ≥50 per instrument | **72 / 72** | smallest bucket 1,043.6 n_eff / 20,394-bar shortest census |
| **G2** Economic | `d·excess ≥ 36.0` **and** `d·mu_cell ≥ 18.0` bps | **1 / 72** | only `vol_ratio h=24 BOT` |
| **G3** Breadth | `d·excess_i > 0` for ≥5 of 9 | **66 / 72** | |
| **G4** Placebo | `abs(excess) > P95(M) = 47.2200` bps | **0 / 72** | largest real `abs(excess)` = **36.5176** bps |
| **G5** TEST presence | fires on ≥30 of 151 TEST dates | **66 / 72** | `illiq TOP` TEST-ABSENT at 19/151 |
| **PASS = G1∧G2∧G3∧G4∧G5** | all five | **0 / 72** | |

**The single most decision-relevant number in this cycle:** the largest conditional excess anywhere in
the 72-cell matrix is **36.5176 bps**, and the family-wise noise floor for a 72-cell scan on this data
is **47.2200 bps**. The scan's own selection noise is **larger than its best finding**, and larger
than the 36.0 bps economic bar it was asked to clear.

### The cost wall, quantified — the objective of the cycle

Cost is **fixed per round trip** (18.0 bps); conditional edge grows roughly with √h. That makes the
affordable holding period arithmetic. Best in-sample cell per horizon (`economics_by_horizon.csv`):

| h (bars) | max abs(excess) bps | best gross per-trade cell | best `d·mu_cell` bps | gross edge ÷ 18.0 bps | net per trade bps | round trips/yr | annual cost drag |
|---|---|---|---|---|---|---|---|
| 1 | 2.9081 | mom_24 BOT | 2.7756 | **0.15×** | −15.2244 | 8,760 | 1,576.8% |
| 2 | 5.1050 | mom_24 BOT | 4.8390 | **0.27×** | −13.1610 | 4,380 | 788.4% |
| 4 | 8.8795 | mom_24 BOT | 8.3511 | **0.46×** | −9.6489 | 2,190 | 394.2% |
| 8 | 17.1835 | mom_24 BOT | 16.1349 | **0.90×** | −1.8651 | 1,095 | 197.1% |
| 12 | 19.8521 | vol_ratio BOT | 21.4246 | **1.19×** | +3.4246 | 730 | 131.4% |
| 24 | 36.5176 | vol_ratio BOT | 39.8100 | **2.21×** | +21.8100 | 365 | 65.7% |

**The operator's stated goal is a bot trading multiple times per day, i.e. h ≤ 8.** Across that whole
region the best gross conditional return available from any of the six variables, on either tail, is
**below one round trip** — 0.15× to 0.90× of 18.0 bps. Not marginal: **negative before slippage
error, before adverse selection, before any implementation shortfall, and before pricing the fact
that these are the best of 72 in-sample cells.** The gross edge first exceeds one round trip only at
h = 12 (1.19×), and first exceeds the pre-registered 2× bar only at h = 24 — the one-round-trip-per-day
boundary case, which is not the target frequency.

These per-horizon figures are **upper bounds, not expectations**: each is the maximum over 12 cells
selected in-sample at that horizon, with no selection penalty applied. The placebo control (G4) is
what prices that selection, and it rejects the h=24 cell too.

---

## 3. Implementation notes

**Script**: `user_data/research/phase_t039_census.py` (one file, one entry point, no arguments).
Re-runnable unmodified; **verified byte-identical across three consecutive runs** for every CSV and
JSON artifact.

### Data access
- The nine 1h futures feathers are read with `pd.read_feather` at the exact paths in `NEXT_TASK.md`,
  then `.set_index("date").sort_index()`. `validator.load()` was **not** used — per the assignment's
  environment note it resolves against `DATA_DIR` with a flat filename convention and cannot find the
  futures tree.
- Nothing else was read. No 1d feather, no mark, no funding, no external axis. No axis was fetched;
  none was assigned.

### State variables (transcribed literally from the assignment's table)
All six are computed on each instrument's **full 1h series before any slicing** (directive 8,
"Warmup"), and all are causal — every window is backward-looking and the value at `t` uses only bars
`≤ t`.

| # | Variable | Implementation | Decisions made explicit |
|---|---|---|---|
| 1 | `mom_24` | `log(c).diff(24)` | — |
| 2 | `vol_ratio` | `r.rolling(24).std() / r.rolling(168).std()` | **pandas default `ddof=1`**; zero denominator → NaN |
| 3 | `volume_z` | `(log1p(v) − mean_168) / std_168` | `ddof=1`; zero std → NaN |
| 4 | `range_pos` | `(c − min(l,24)) / (max(h,24) − min(l,24))` | denominator 0 → NaN, as specified |
| 5 | `cs_mom_rank` | cross-sectional rank of `mom_24`, `(rank−1)/(n_present−1)`, NaN if `n_present < 6` | **ties = pandas default `method="average"`**; exact `mom_24` ties in the whole panel: **10** |
| 6 | `illiq` | `(abs(r)/(v·c)).rolling(24).mean() · 1e9` | `v·c == 0 → NaN`; `min_periods=24` makes the window NaN if any contributing bar is NaN, exactly as specified |

`min_periods` equals the window everywhere, so no rolling statistic is computed on a partial window.

### Forward returns
- **Executable (used by every gate)**: `fwd_h(t) = log(c_{t+1+h}) − log(c_{t+1})`, matching
  `validator.signal_to_returns`'s 2-bar anti-lookahead convention (`validator.py:505-536`).
- **Naive (diagnostic only, used by NO gate)**: `fwd_h(t) = log(c_{t+h}) − log(c_t)`. Reported in
  section 7; never entered a gate expression.

### Decile thresholds
Computed **per instrument on TRAIN+VAL only** and never re-estimated on TEST. `TOP = v ≥ q90`,
`BOT = v ≤ q10`.

**One decision, made explicit and then measured rather than assumed.** The assignment says thresholds
are estimated "on TRAIN+VAL"; the census window is TRAIN+VAL minus each instrument's final 24 bars.
I estimated them on the **census window**, so that the real matrix and the placebo control — which
shifts and re-thresholds *within* the census window by construction — use the same estimation sample.
I then re-ran the entire matrix with thresholds estimated on the **untrimmed** TRAIN+VAL instead:
max relative threshold difference **2.017e-03**, max shift in any cell's excess **0.1620 bps**, and
**0 of 72 cells change G1–G4 status** (`matrix_sensitivity_trainval_thresholds.csv`). The choice is
immaterial to every gate outcome, and the alternative is on disk.

**Bucket sizes behave as expected for a decile** — realised TOP/BOT fractions are 0.100000–0.100044
of valid bars for five of the six variables (`decile_thresholds.csv`). **`cs_mom_rank` is the
exception at 0.1120–0.1797**, because with nine instruments it takes at most nine discrete values, so
a decile cut necessarily captures a whole rank level. This is a property of the variable, not a
defect; it is reported because it makes `cs_mom_rank` buckets 12–80% larger than a true decile.

### Placebo control (G4)
1,000 draws, seed 20260803, `k ~ Uniform[720, N_min − 720]` inclusive with `N_min = 20,394` (BNB's
census length) → `k ∈ [720, 19674]`. One `k` per draw, applied to all nine instruments. The six
state-variable series are circularly shifted forward by `k`; return series stay in place; thresholds
are recomputed on the shifted variables; `M_draw = max over the 72 cells of abs(excess)`.

**One optimization, proven rather than assumed.** A circular shift permutes a variable's values
without changing the multiset, so recomputed decile thresholds are *exactly* the unshifted ones and
the shifted mask is `roll(mask, k)`. The script **proves this on the real data before the loop runs**
(`assert_shift_thresholds_invariant`, k=1234): 108 (instrument × variable × quantile) pairs checked,
**max absolute threshold difference 0.0**, and the run aborts if it is nonzero. The loop then gathers
rows at `(idx + k) mod n` instead of re-sorting 54 arrays per draw. This is an optimization of the
specified computation, not a change to it.

### What I did NOT do
No strategy object, no signal series, no backtest, no equity curve, no hyperopt, no parameter search,
no DSR, no Monte Carlo, no walk-forward — none is applicable and none was assigned. No seventh
variable, no extra horizon, no extra tail, no extra draw. No file outside my ownership was written.

---

## 4. Compliance attestations

**a. `user_data/data/` is untouched.**
```
$ git status --porcelain -- user_data/data/
(no output)
```
Run before and after the work; empty both times. The script contains no write path into that tree; it
opens the nine feathers read-only and writes only to `research/results/T-039_raw/`.

**b. Data manifest verification — passed, not bypassed.**
```
BEFORE: OK: 52 files match the manifest (built 2026-07-29T07:58:59Z).
AFTER : OK: 52 files match the manifest (built 2026-07-29T07:58:59Z).
```
The import-time gate in `validator.py` also ran on every execution and is recorded in the run log:
`{"verified": true, "bypassed": false, "files_checked": 52, "manifest_built_utc": "2026-07-29T07:58:59Z"}`.
**`FREQTRADE_SKIP_DATA_VERIFY` was never set.** The script additionally aborts with exit code 2 if
`data_integrity_snapshot()["bypassed"]` is ever true. `scripts/data_manifest.py build` was not run.

**c. Cost model — resolved from `COST_MODEL`, nothing hardcoded.**
```
$ validator.describe_cost_model("taker")
okx_usdt_perp / regular (non-VIP, no fee discounts) / fill=taker: maker 2.0bps, taker 5.0bps,
slippage 3.0bps/side, spread 2.0bps, adverse selection unset -> 9.00bps/side, 18.00bps round trip

validator.per_side_cost("taker")   = 0.0009  ->  9.0000 bps/side
validator.round_trip_cost("taker") = 0.0018  -> 18.0000 bps round trip
```
Both G2 thresholds are **derived at runtime** from that return value:
`C1a = 2 × round_trip_cost("taker") × 1e4 = 36.0000 bps`,
`C1b = 1 × round_trip_cost("taker") × 1e4 = 18.0000 bps`. No fee, slippage or spread number is typed
anywhere in the script. Venue: OKX USDT perpetual swaps, regular tier. **Fill assumption: `taker`.**
`maker_optimistic` was not used anywhere, not even as a secondary comparison, and no
`maker_optimistic` warning applies to this cycle.

Mandatory cost-model warning, reproduced verbatim:
> COST MODEL NOTE - slippage (3.0 bps/side) and spread (2.0 bps) are estimates, not calibrated
> against realized fills. Fee rates are published OKX regular (non-VIP, no fee discounts) rates for
> okx_usdt_perp as of 2026-07-28.

**d. Split dates and holdout.**
`validator.split_by_dates(df, "2024-11-22", "2025-04-21", "2025-09-19")` per instrument.
`split_70_15_15()` was not called. No fractional split anywhere.

- Census window (G1–G4): each instrument's history through **2025-04-21 23:00:00+00:00**, minus its
  final 24 bars → ends **2025-04-20 23:00:00+00:00**.
- TEST window (G5 only): **2025-04-22 00:00 → 2025-09-19 23:00**, **151 UTC dates for all nine
  instruments** (verified: the set of per-instrument date counts is exactly `{151}`).
- **Reserved holdout (bars strictly after 2025-09-19) was untouched.**
  `validator.holdout_boundary("perps", freq="1h")` = **2025-09-19 23:00:00+00:00** — the
  resolution-aware reading; it was called, not hand-rolled.

`validator.assert_no_holdout(..., program="perps")` was called on **every frame built** — 9
instruments × (train, val, test, train+val, census) = **45 assertions, all OK**
(`holdout_assertions.txt`). The raw full series is deliberately *not* an evaluation window: the guard
is invoked on it and **correctly raises**, which is recorded in the log as evidence the guard is live.
Only backward-looking rolling windows are read from that frame, and every analysed frame is sliced
before use. `enforce_holdout=False` was never used; `validate()` was never called (no candidate).

**e. Budget compliance.** Strategy variants **0 of 0**. Optimization runs **0 of 0**. Hyperopt **0**.
Trials **0 of 0**, `n_trials` **0 → 0** against the 30-trial program cap. Placebo draws **1,000 of
1,000** at the pre-registered seed. Variables **6**, horizons **6**, tails **2** — the pre-registered
sets, unchanged. Nothing was re-run with a different seed, window, or pair set; the only re-runs were
identical-input determinism checks, which produced byte-identical output.

**f. DSR entry point.** `python scripts/check_dsr_entrypoint.py` → **`VIOLATIONS: 0`**. No DSR was
computed this cycle (no candidate exists), so there is no `trial_var_source` to report; the ledger
stays at **0 data rows** and promotion criterion 7 remains unsatisfiable program-wide.

---

## 5. Lookahead / leakage checks performed

| Check | How it was verified | Result |
|---|---|---|
| **Indicators computed before splitting** | All six variables are built on the full series in `per_instrument_variables()` / `add_cs_mom_rank()`, then `.loc[census_idx]` slices them. Splitting happens strictly after. | **PASS** — directive 8 satisfied; no warmup truncation at any split edge |
| **Every state variable is causal** | Every window is a pandas `rolling(...)` (backward-looking) or a `diff(k)` (backward-looking). No `shift(-k)`, no `rolling(...).shift(-k)`, no centered window appears in any variable expression. `cs_mom_rank` ranks *within a single timestamp* across instruments — a cross-section, not a time shift. | **PASS** |
| **Signal-to-execution lag** | Forward returns anchor at `c_{t+1}`, not `c_t`, matching `signal_to_returns`'s `position[t] = signal[t-2]`. The naive `c_t` anchor was computed **only** as a labelled diagnostic and appears in no gate expression. | **PASS** — and the size of the effect is measured, see §7 |
| **Decile thresholds are a selection statistic** | Estimated on TRAIN+VAL only; never re-estimated on TEST. G5 applies the *TRAIN+VAL* threshold to TEST. | **PASS** |
| **No TEST forward return** | The G5 frame carries the state-variable matrix only — no forward-return column is built for it anywhere in the code. | **PASS**, with one measured exception below |
| **Holdout untouched** | 45 `assert_no_holdout` calls, all OK. Latest bar any executable forward return reads: **2025-04-22 00:00:00+00:00**, ~5 months before the 2025-09-19 boundary. | **PASS** |
| **Forward-return NaNs in census** | Counted per instrument: `{BTC:0, ETH:0, SOL:0, BNB:0, XRP:0, ADA:0, AVAX:0, DOT:0, LINK:0}`. No cell mean is contaminated by a partially-available window. | **PASS** |
| **>100% CAGR check** | Not applicable — this cycle produces no equity curve and no return stream. Stated rather than silently omitted. | n/a |

### The one measured exception, stated plainly

The assignment defines the census window as TRAIN+VAL **"minus its final 24 bars, so that no forward
return reads a TEST bar."** With the executable anchor, `fwd_24` at the last census bar reads
`c_{t+25}`. A 24-bar trim therefore leaves **exactly one bar of overlap**: for each instrument, the
h=24 family's last census observation reads the close of **2025-04-22 00:00 — the first TEST bar.**
The trim needed to achieve the stated purpose under this anchor is 25, not 24. This is an off-by-one
in the assignment's stated rationale, not an ambiguity in its instruction, so **I executed the literal
pre-registered number (24)** and measured the alternative rather than silently substituting it:

> Re-running the full matrix with a **25-bar trim** (no forward return reads any TEST bar at any
> horizon): **0 of 72 cells change G1–G4 status**, max shift in any cell's excess **0.0546 bps**,
> cells clearing G1–G4 still **0**. → `matrix_sensitivity_trim25.csv`

Magnitude of the leak: **9 bars out of 251,946**, in 6 of 72 cells, worth ≤0.0546 bps. It is
outcome-irrelevant here, but it is a real defect in the spec text and the next 1h census should trim
`max(h) + 1`. See §12.

---

## 6. Variants attempted

**0 of 0 assigned.** No strategy variant, no parameter set, no optimization run, no hyperopt was
attempted, abandoned, or completed. Nothing was tried and discarded — there is no unlogged run
because there was no run to log. The census is a single deterministic pass over held data.

For completeness, the non-variant computations performed (none consumes budget, all are pre-registered
or explicitly labelled diagnostics):

| # | Computation | Status |
|---|---|---|
| 1 | 72-cell matrix, executable anchor | pre-registered, gating |
| 2 | 1,000-draw placebo control, seed 20260803 | pre-registered, gating |
| 3 | G5 TEST-presence scan (state variable only) | pre-registered, gating |
| 4 | 72-cell matrix, naive anchor | pre-registered as a **diagnostic**, gates nothing |
| 5 | Spearman matrix + effective test count | pre-registered as **not gating** |
| 6 | Sensitivity: thresholds on untrimmed TRAIN+VAL | Engineer diagnostic, gates nothing |
| 7 | Sensitivity: 25-bar trim | Engineer diagnostic, gates nothing |
| 8 | Placebo argmax attribution by horizon/variable | Engineer diagnostic, gates nothing |

---

## 7. Backtest results

**None. No backtest was run and none was assigned.** This section is the census matrix instead.

**Exact configuration**: 9 OKX USDT perps, 1h futures feathers, taker fill, `COST_MODEL` as resolved
in §4c, census window 2022-01-01 (BNB 2022-12-23 06:00) → 2025-04-20 23:00, **251,946 pooled census
bars** (252,162 pooled TRAIN+VAL before the 24-bar trim — **exactly matching the Director's verified
figure**).

### Unconditional forward return, pooled over the census window

| h | 1 | 2 | 4 | 8 | 12 | 24 |
|---|---|---|---|---|---|---|
| `mu_uncond` (bps) | −0.1325 | −0.2659 | −0.5284 | −1.0486 | −1.5725 | −3.2924 |

The census window's unconditional 1h drift is **negative at every horizon**. This is why the design
measures `excess` against `mu_uncond` rather than against zero.

### Full 72-cell matrix (executable anchor — this is what the gates ran on)

`mu_cell`, `excess`, `SE` in bps. `SE` is by non-overlapping subsampling, `n_eff = n_bucket / h`,
`SE = sd_bucket / √n_eff`, **recomputed per cell from the actual data** as required — not quoted from
the Director's power table. `br` = breadth count (of 9). Status: FAIL / INELIGIBLE (G1) /
TEST-ABSENT (G5) / PASS.

| variable | h | tail | mu_cell | mu_uncond | excess | d | SE | n_bucket | n_eff | br | G1 | G2 | G3 | G4 | G5 | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom_24 | 1 | TOP | −0.5727 | −0.1325 | −0.4401 | −1 | 0.7467 | 25173 | 25173.0 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 2 | TOP | −0.7396 | −0.2659 | −0.4737 | −1 | 1.4585 | 25173 | 12586.5 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 4 | TOP | −2.0818 | −0.5284 | −1.5534 | −1 | 2.8477 | 25173 | 6293.3 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 8 | TOP | −6.1859 | −1.0486 | −5.1373 | −1 | 5.4900 | 25173 | 3146.6 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 12 | TOP | −11.1399 | −1.5725 | −9.5674 | −1 | 8.1302 | 25173 | 2097.8 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 24 | TOP | −9.6689 | −3.2924 | −6.3765 | −1 | 15.9744 | 25173 | 1048.9 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 1 | BOT | 2.7756 | −0.1325 | **2.9081** | +1 | 0.9210 | 25173 | 25173.0 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 2 | BOT | 4.8390 | −0.2659 | **5.1050** | +1 | 1.8141 | 25173 | 12586.5 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 4 | BOT | 8.3511 | −0.5284 | **8.8795** | +1 | 3.5387 | 25173 | 6293.3 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 8 | BOT | 16.1349 | −1.0486 | **17.1835** | +1 | 6.7253 | 25173 | 3146.6 | 9 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 12 | BOT | 16.2021 | −1.5725 | 17.7746 | +1 | 10.0195 | 25173 | 2097.8 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| mom_24 | 24 | BOT | 15.8988 | −3.2924 | 19.1912 | +1 | 19.2230 | 25173 | 1048.9 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 1 | TOP | 1.5302 | −0.1325 | 1.6627 | +1 | 0.9084 | 25047 | 25047.0 | 9 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 2 | TOP | 2.3001 | −0.2659 | 2.5661 | +1 | 1.7612 | 25047 | 12523.5 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 4 | TOP | 3.5483 | −0.5284 | 4.0767 | +1 | 3.3970 | 25047 | 6261.8 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 8 | TOP | 3.1152 | −1.0486 | 4.1638 | +1 | 6.4920 | 25047 | 3130.9 | 5 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 12 | TOP | 3.4300 | −1.5725 | 5.0025 | +1 | 9.5885 | 25047 | 2087.3 | 5 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 24 | TOP | −4.2220 | −3.2924 | −0.9296 | −1 | 18.9959 | 25047 | 1043.6 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 1 | BOT | −1.7926 | −0.1325 | −1.6601 | −1 | 0.4373 | 25047 | 25047.0 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 2 | BOT | −3.8066 | −0.2659 | −3.5407 | −1 | 0.8738 | 25047 | 12523.5 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 4 | BOT | −7.3867 | −0.5284 | −6.8582 | −1 | 1.7461 | 25047 | 6261.8 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 8 | BOT | −13.6126 | −1.0486 | −12.5639 | −1 | 3.5939 | 25047 | 3130.9 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| vol_ratio | 12 | BOT | −21.4246 | −1.5725 | −19.8521 | −1 | 5.4441 | 25047 | 2087.3 | 9 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| **vol_ratio** | **24** | **BOT** | **−39.8100** | −3.2924 | **−36.5176** | **−1** | **11.0915** | 25047 | 1043.6 | **9** | ✓ | **✓** | ✓ | **✗** | ✓ | **FAIL** |
| volume_z | 1 | TOP | −0.2717 | −0.1325 | −0.1391 | −1 | 0.8627 | 25047 | 25047.0 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 2 | TOP | 0.4730 | −0.2659 | 0.7389 | +1 | 1.6518 | 25047 | 12523.5 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 4 | TOP | 1.3414 | −0.5284 | 1.8698 | +1 | 3.1548 | 25047 | 6261.8 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 8 | TOP | 3.5172 | −1.0486 | 4.5659 | +1 | 5.9655 | 25047 | 3130.9 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 12 | TOP | 7.2841 | −1.5725 | 8.8566 | +1 | 8.7660 | 25047 | 2087.3 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 24 | TOP | 7.3121 | −3.2924 | 10.6045 | +1 | 16.8023 | 25047 | 1043.6 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 1 | BOT | −1.2853 | −0.1325 | −1.1527 | −1 | 0.4175 | 25047 | 25047.0 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 2 | BOT | −3.2275 | −0.2659 | −2.9616 | −1 | 0.8653 | 25047 | 12523.5 | 9 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 4 | BOT | −4.6201 | −0.5284 | −4.0917 | −1 | 1.7719 | 25047 | 6261.8 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 8 | BOT | −1.6631 | −1.0486 | −0.6145 | −1 | 3.5676 | 25047 | 3130.9 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 12 | BOT | −2.1423 | −1.5725 | −0.5698 | −1 | 5.4625 | 25047 | 2087.3 | 5 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| volume_z | 24 | BOT | −14.8006 | −3.2924 | −11.5082 | −1 | 11.5474 | 25047 | 1043.6 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 1 | TOP | 0.4072 | −0.1325 | 0.5397 | +1 | 0.5991 | 25182 | 25182.0 | 5 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 2 | TOP | 0.5620 | −0.2659 | 0.8280 | +1 | 1.1747 | 25182 | 12591.0 | 5 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 4 | TOP | 1.3224 | −0.5284 | 1.8508 | +1 | 2.3607 | 25182 | 6295.5 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 8 | TOP | 0.2767 | −1.0486 | 1.3253 | +1 | 4.5675 | 25182 | 3147.8 | **4** | ✓ | ✗ | **✗** | ✗ | ✓ | FAIL |
| range_pos | 12 | TOP | 1.9987 | −1.5725 | 3.5712 | +1 | 6.7009 | 25182 | 2098.5 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 24 | TOP | −8.7011 | −3.2924 | −5.4087 | −1 | 13.5056 | 25182 | 1049.3 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 1 | BOT | 1.5471 | −0.1325 | 1.6796 | +1 | 0.6795 | 25182 | 25182.0 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 2 | BOT | 2.1036 | −0.2659 | 2.3695 | +1 | 1.3089 | 25182 | 12591.0 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 4 | BOT | 3.0860 | −0.5284 | 3.6145 | +1 | 2.4987 | 25182 | 6295.5 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 8 | BOT | −0.3494 | −1.0486 | 0.6993 | +1 | 5.0203 | 25182 | 3147.8 | **4** | ✓ | ✗ | **✗** | ✗ | ✓ | FAIL |
| range_pos | 12 | BOT | −0.0956 | −1.5725 | 1.4768 | +1 | 7.5036 | 25182 | 2098.5 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| range_pos | 24 | BOT | 8.0866 | −3.2924 | 11.3790 | +1 | 15.0365 | 25182 | 1049.3 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 1 | TOP | 0.3862 | −0.1325 | 0.5188 | +1 | 0.5577 | 35315 | 35315.0 | 5 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 2 | TOP | 0.9457 | −0.2659 | 1.2116 | +1 | 1.1063 | 35315 | 17657.5 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 4 | TOP | 1.7246 | −0.5284 | 2.2530 | +1 | 2.1855 | 35315 | 8828.8 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 8 | TOP | 2.4384 | −1.0486 | 3.4870 | +1 | 4.2981 | 35315 | 4414.4 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 12 | TOP | 1.3191 | −1.5725 | 2.8916 | +1 | 6.3283 | 35315 | 2942.9 | **4** | ✓ | ✗ | **✗** | ✗ | ✓ | FAIL |
| cs_mom_rank | 24 | TOP | 0.0226 | −3.2924 | 3.3150 | +1 | 12.3343 | 35315 | 1471.5 | 5 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 1 | BOT | −0.4689 | −0.1325 | −0.3363 | −1 | 0.5139 | 37153 | 37153.0 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 2 | BOT | −0.9468 | −0.2659 | −0.6809 | −1 | 1.0139 | 37153 | 18576.5 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 4 | BOT | −2.3883 | −0.5284 | −1.8598 | −1 | 1.9968 | 37153 | 9288.3 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 8 | BOT | −4.7504 | −1.0486 | −3.7018 | −1 | 3.9091 | 37153 | 4644.1 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 12 | BOT | −6.7283 | −1.5725 | −5.1558 | −1 | 5.8852 | 37153 | 3096.1 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| cs_mom_rank | 24 | BOT | −14.8614 | −3.2924 | −11.5690 | −1 | 11.8497 | 37153 | 1548.0 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| illiq | 1 | TOP | −0.0228 | −0.1325 | 0.1098 | +1 | 0.5315 | 25149 | 25149.0 | 5 | ✓ | ✗ | ✓ | ✗ | **✗** | TEST-ABSENT |
| illiq | 2 | TOP | −0.0984 | −0.2659 | 0.1675 | +1 | 1.0548 | 25149 | 12574.5 | **4** | ✓ | ✗ | **✗** | ✗ | **✗** | TEST-ABSENT |
| illiq | 4 | TOP | 0.2071 | −0.5284 | 0.7355 | +1 | 2.0937 | 25149 | 6287.3 | **4** | ✓ | ✗ | **✗** | ✗ | **✗** | TEST-ABSENT |
| illiq | 8 | TOP | 0.6043 | −1.0486 | 1.6529 | +1 | 4.1789 | 25149 | 3143.6 | 5 | ✓ | ✗ | ✓ | ✗ | **✗** | TEST-ABSENT |
| illiq | 12 | TOP | −1.4513 | −1.5725 | 0.1212 | +1 | 6.2337 | 25149 | 2095.8 | **4** | ✓ | ✗ | **✗** | ✗ | **✗** | TEST-ABSENT |
| illiq | 24 | TOP | −6.8144 | −3.2924 | −3.5220 | −1 | 12.2425 | 25149 | 1047.9 | 5 | ✓ | ✗ | ✓ | ✗ | **✗** | TEST-ABSENT |
| illiq | 1 | BOT | −1.0197 | −0.1325 | −0.8871 | −1 | 0.7265 | 25149 | 25149.0 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| illiq | 2 | BOT | −1.9963 | −0.2659 | −1.7303 | −1 | 1.4091 | 25149 | 12574.5 | 7 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| illiq | 4 | BOT | −3.8882 | −0.5284 | −3.3597 | −1 | 2.7569 | 25149 | 6287.3 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| illiq | 8 | BOT | −7.5031 | −1.0486 | −6.4545 | −1 | 5.3447 | 25149 | 3143.6 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| illiq | 12 | BOT | −12.7711 | −1.5725 | −11.1986 | −1 | 7.7946 | 25149 | 2095.8 | 6 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |
| illiq | 24 | BOT | −29.0469 | −3.2924 | −25.7545 | −1 | 15.1551 | 25149 | 1047.9 | 8 | ✓ | ✗ | ✓ | ✗ | ✓ | FAIL |

Per-instrument bucket counts and per-instrument excess for all 72 cells (9 columns each) are in
`matrix_executable.csv`; they are omitted here only for width.

### Naive-anchor diagnostic matrix — **NOT USED IN ANY GATE**

Full matrix at `matrix_naive_DIAGNOSTIC_ONLY.csv`. The execution-lag effect on `excess`
(naive − executable) is **mean +0.352 bps, median +0.257 bps, max abs 3.492 bps** (at
`mom_24 h=24 BOT`). Naive `mu_uncond` runs −0.1355 / −0.2681 / −0.5344 / −1.0552 / −1.5742 / −3.2770
bps against the executable −0.1325 / −0.2659 / −0.5284 / −1.0486 / −1.5725 / −3.2924.

**One sentence on the size of the effect, as required:** the naive anchor inflates the largest
abs(excess) in the matrix from 36.5176 to 37.6360 bps (+3.1%) and biases `excess` upward by ~0.26 bps
at the median — small relative to the 36.0 bps bar and far too small to change this cycle's verdict,
but systematically *favourable* and concentrated in the short-horizon momentum cells the naive anchor
mechanically flatters, which is exactly why the executable convention is mandatory rather than
optional.

---

## 8. Walk-forward / out-of-sample results

**Not applicable, and not run.** This cycle evaluates no strategy, so there is no return stream to
walk forward. The out-of-sample discipline that *does* apply here is threefold and was enforced:

1. All 72 cell statistics are measured on **TRAIN+VAL only** (251,946 pooled bars).
2. Decile thresholds are estimated on **TRAIN+VAL only** and never re-estimated on TEST.
3. **G5** is the only computation touching TEST, and it reads the **state variable only** — no TEST
   forward return exists anywhere in the code.

### G5 — TEST presence (151 TEST dates, 2025-04-22 → 2025-09-19)

Threshold applied to TEST is the TRAIN+VAL threshold. "Pooled dates" counts a date as fired if any
instrument's variable is in its own decile on any bar of that date; per-instrument counts are given
alongside because the pooled reading is the more permissive one and the gate should be auditable
under both.

| variable | tail | pooled fired dates | min instrument | median instrument | G5 (≥30) |
|---|---|---|---|---|---|
| mom_24 | TOP | 95 | 23 | 46 | ✓ |
| mom_24 | BOT | 72 | 17 | 37 | ✓ |
| vol_ratio | TOP | 75 | 24 | 26 | ✓ |
| vol_ratio | BOT | 60 | 19 | 22 | ✓ |
| volume_z | TOP | 147 | 103 | 109 | ✓ |
| volume_z | BOT | 145 | 82 | 97 | ✓ |
| range_pos | TOP | 138 | 95 | 99 | ✓ |
| range_pos | BOT | 130 | 84 | 92 | ✓ |
| cs_mom_rank | TOP | 151 | 50 | 69 | ✓ |
| cs_mom_rank | BOT | 151 | 63 | 73 | ✓ |
| **illiq** | **TOP** | **19** | **0** | **0** | **✗ TEST-ABSENT** |
| illiq | BOT | 151 | 4 | 128 | ✓ |

**`illiq TOP` is TEST-ABSENT and this is a substantive finding, not a bookkeeping note.** The
*median* instrument fires on **zero** of 151 TEST dates. The Amihud illiquidity level that defined
the top decile in 2022–2024 is essentially never reached in mid-2025: quote volumes on these nine
perps rose enough that the in-sample "most illiquid" state stopped occurring. A construct trained on
that state would have had nothing to trade in TEST. It also means **any future cycle using a
level-based liquidity threshold on this panel must re-express it as a rolling percentile**, or it
will silently stop firing.

Under the stricter per-instrument reading, `vol_ratio BOT` (min 19) and `mom_24 BOT` (min 17) would
also fall below 30 for their weakest instrument. Neither changes the verdict — both fail G2 and G4
anyway — but the Reviewer should know the pooled reading was the one applied.

---

## 9. DSR and other required statistics

**DSR: not computed, correctly.** No trial was spent, no candidate exists, and
`NEXT_TASK.md` explicitly lists DSR among the gates that do not apply this cycle. Nothing was
appended to `research/trial_sharpe_ledger.csv`, which holds **0 data rows before and 0 after** (51
physical lines, all comments plus one CSV header).

> **Discrepancy worth the Reviewer's attention, resolved in favour of the assignment:** a naive line
> count of `trial_sharpe_ledger.csv` returns 50, because the file's 51 physical lines are **50 comment
> lines plus one CSV header and zero data rows**. The **data-row count, which is what the 10-row DSR variance threshold actually
> counts, is 0**, exactly as `NEXT_TASK.md` states. My first run of the script printed the naive
> figure; the script was corrected to parse the file properly and re-run before this report was
> written. No number in this report derives from the wrong count.

`scripts/check_dsr_entrypoint.py` → **VIOLATIONS: 0**. No file imports `freqtrade_dsr` directly;
12 frozen `phase*.py` artifacts are exempt as designed.

Also not computed, and not applicable, stated rather than silently omitted: Monte Carlo gate,
`validator.sharpe_difference_se()`, walk-forward, parameter stability, trade-count validation. Each
is a property of a strategy; none exists.

### The placebo control distribution (G4)

1,000 draws, seed **20260803**, `k ∈ [720, 19674]`, `N_min = 20,394`.

| statistic | value (bps) |
|---|---|
| mean(M) | **29.9228** |
| sd(M) | **9.8972** |
| P50(M) | **28.7884** |
| **P95(M)** | **47.2200** ← the G4 threshold |
| P99(M) | 57.2635 |
| min(M) | 7.9825 |
| max(M) | 80.1789 |

**Mandatory sanity assertions — both required, both checked, both passed:**

1. **`sd(M) > 0` and `P95(M) > 0`** → **TRUE** (sd 9.8972 bps, P95 47.2200 bps). The control is not
   degenerate; no BLOCK condition.
2. **At least one cell's shifted abs(excess) differs from the unshifted value** → **TRUE**. On draw 1,
   **72 of 72 cells differ**, max difference **24.4153 bps**. The shift demonstrably took effect. (Had
   all 72 matched, that would have been the bug signature lesson 20 warns about, not a result.)

The script hard-aborts with a distinct exit code if either assertion fails, so a degenerate control
could not have been silently interpreted.

**Where the family-wise max comes from** (`placebo_argmax_by_draw.csv`, Engineer diagnostic): the
maximising cell is at **h=24 in 985 of 1,000 draws** and h=12 in the other 15; never at h ≤ 8. By
variable: vol_ratio 370, illiq 308, mom_24 250, range_pos 53, volume_z 16, cs_mom_rank 3. The control
is therefore dominated by exactly the long-horizon, heavy-tailed cells where the real matrix's only
G2-clearing candidate sits — which is the correct behaviour for a control designed to price this
scan, and it is why a 36.5 bps in-sample result is not evidence of a mechanism.

### What would make G2 pass without a mechanism, and why G4 prevents it

Required by the assignment, stated explicitly. **The failure mode:** the top (or bottom) decile of a
magnitude variable such as `vol_ratio`, `volume_z` or `illiq` selects high-variance bars by
construction. The mean of a high-variance subsample is itself a high-variance estimate, so scanning
72 cells and reporting the largest abs(excess) yields a materially non-zero maximum **under pure
noise**. This is the T-038 pathology the previous Engineer named a trap: the inverted construct looks
good in-sample for a decomposition reason, not a causal one.

**Why G4 prevents it:** the circular shift preserves each variable's marginal distribution (proven
exactly — thresholds are bit-identical after shifting), each return series' autocorrelation and
volatility clustering (returns are never touched), and the panel's cross-sectional structure (one `k`
for all nine instruments), while destroying only the **alignment** between variable and return. Taking
the **maximum over all 72 cells per draw** makes the threshold family-wise, so the 72-cell scan is
priced in rather than exploited.

**It did exactly its job.** `vol_ratio h=24 BOT` cleared the economic gate (`d·excess` 36.52 ≥ 36.0,
`d·mu_cell` 39.81 ≥ 18.0) and had perfect breadth (9/9). Under a design without G4 it would have been
reported as a passing cell and handed to a follow-on cycle to build and backtest. **G4 says a
72-cell scan of this data produces a 36.5 bps maximum more than 5% of the time under the null
(P95 = 47.22 bps), so that cell is inside the noise.** One trial, and probably a cycle, was saved.

### Spearman correlation of the six variables (pooled, **NOT gating**)

|  | mom_24 | vol_ratio | volume_z | range_pos | cs_mom_rank | illiq |
|---|---|---|---|---|---|---|
| **mom_24** | 1.0000 | −0.0265 | 0.0192 | **0.7700** | 0.4284 | −0.0306 |
| **vol_ratio** | −0.0265 | 1.0000 | 0.4031 | 0.0089 | 0.1089 | −0.0167 |
| **volume_z** | 0.0192 | 0.4031 | 1.0000 | 0.0115 | 0.1188 | −0.0384 |
| **range_pos** | **0.7700** | 0.0089 | 0.0115 | 1.0000 | 0.3310 | −0.0074 |
| **cs_mom_rank** | 0.4284 | 0.1089 | 0.1188 | 0.3310 | 1.0000 | −0.0745 |
| **illiq** | −0.0306 | −0.0167 | −0.0384 | −0.0074 | −0.0745 | 1.0000 |

**Max abs(off-diagonal) = 0.7700 (mom_24 ↔ range_pos). No pair exceeds abs(0.90), so the assignment's
"G4's protection is weaker than the 72-cell framing suggests" warning is NOT triggered.**

Effective number of independent tests (`effective_tests.json`): eigenvalues
[0.2198, 0.5970, 0.6972, 1.0004, 1.4253, 2.0603]; **M_eff = 5.0000 (Li & Ji 2005)**, 5.6387
(Cheverud–Nyholt). The Li & Ji figure lands on exactly 5.0000; per lesson 20 I checked rather than
assumed, and it is exact arithmetic, not a bug — the eigenvalues of a correlation matrix sum to its
trace (6), `sum(floor(λ)) = 4` and three eigenvalues are ≥1, so `M_eff = (6 − 4) + 3 = 5` exactly.
On the variable axis alone that implies **≈60 effective cells against a raw 72**
(×12 for horizons and tails). Reported as required; note this counts only the variable axis — the six
horizons are nested windows on the same returns and are strongly dependent, so the true effective
count is materially below 60. Per the assignment's own reasoning this makes G4 **easier** to clear
than the raw 72-cell framing implies, and it was still not cleared by any cell.

### Per-cell standard errors — recomputed from the data, as required

Recomputed per cell by non-overlapping subsampling (`n_eff = n_bucket / h`), not quoted from the
Director's power table. Comparison at the top decile:

| h | Director's power calc (SE of mu_cell) | Realised SE, this data (median over the 12 cells at that h) |
|---|---|---|
| 1 | 0.58 bps | 0.6393 bps |
| 4 | 2.29 bps | 2.4297 bps |
| 24 | 13.64 bps | 14.2711 bps |

(Full per-horizon medians: 0.6393 / 1.2418 / 2.4297 / 4.7939 / 7.1022 / 14.2711 bps at
h = 1/2/4/8/12/24.)

The realised SEs are close to the Director's estimate and slightly larger at short horizons. **The
design was adequately powered**: at h=24 the 36.0 bps bar sits at ~2.6 SE of a single cell, and the
rejection is not an artifact of insufficient resolution — the largest effect found was 3.29 SE from
zero *per cell*, and still inside the family-wise null.

---

## 10. Verdict vs. falsification statement

**The pre-registered falsification condition:**

> This hypothesis is REJECTED if, after computing all 72 cells, no cell satisfies G1 AND G2 AND G3
> AND G4 AND G5 simultaneously.

**Did it trigger? YES. Verdict: REJECT.**

Evidence: `matrix_executable.csv` carries a `PASS` column computed as
`G1 & G2 & G3 & G4 & G5` — five conjunctions, coded as `&`, in one expression, with no intermediate
reinterpretation. `PASS.sum() = 0`. Per-gate counts: G1 72/72, G2 **1**/72, G3 66/72, G4 **0**/72,
G5 66/72.

**Boolean transcription — checked line by line against the spec, as this project has failed twice:**

| Spec text | Code | Operator |
|---|---|---|
| "`d * excess >= 36.0` bps **AND** `d * mu_cell >= 18.0` bps … **This is an `and`, not an `or`**" | `mat["G2"] = mat["G2a…"] & mat["G2b…"]` | `and` ✓ |
| "`d * excess_i > 0` for **>= 5 of the 9**" | `mat["G3"] = mat["breadth_count"] >= 5` | ✓ |
| "cell's decile bucket holds **>= 1,000** pooled bars **and >= 50** bars for each of the 9" | `G1_pooled_ok & G1_per_instrument_ok` | `and` ✓ |
| "`abs(excess) > P95(M)`" | `mat["excess_bps"].abs() > p95` | strict `>` ✓ |
| "fires on **>= 30 of the 151** TEST dates" | `mat["g5_fired_dates"] >= 30` | ✓ |
| "A cell PASSES only if it clears G1 AND G2 AND G3 AND G4 AND G5 — all five, conjunctively" | `G1 & G2 & G3 & G4 & G5` | `and` ✓ |

The phrase "at least one of" does not appear in the assignment and no `or` appears in any gate
expression in the script. `d = +1 if excess > 0 else -1` is coded exactly as written.

**The near-miss, stated precisely so it is not lost.** Exactly one cell — `vol_ratio h=24 BOT` —
cleared G1, G2 and G3 with 9/9 breadth, and failed **only** G4 (abs(excess) 36.5176 vs P95 47.2200).
It is the reason the placebo control was mandated, and it is the reason this cycle's REJECT is
informative rather than vacuous: the hypothesis did not fail for lack of any measurable structure. It
failed because the one structure large enough to pay 2× the round trip is not distinguishable from
the noise floor of the scan that found it.

Under the assignment's own definitions (item 4), that cell is `d = −1` on a **BOT** tail, i.e.
**LONG-implying read as an avoidance filter** ("do not hold through the lowest-vol_ratio decile"),
**not** a short construct. **No short-implying cell passed any gate, so no ruling on the CLOSED short
family is required from the Reviewer this cycle.** Item 5 (selection debt) likewise has no subject:
**no cell passed, so nothing is handed forward and no follow-on cycle inherits 72 tests of selection
debt from a passing cell.** Were the Director to revive the `vol_ratio` cell despite G4, the debt
would be 72 tests and `n_trials = 1` would be a multiple-testing violation.

---

## 11. Regime behavior

The assignment requires per-year and disjoint-window views **only for a passing cell**; none passed,
so items 1–3 of "Required robustness outputs" are not required and were not computed. What the matrix
itself shows about regime and structure:

- **Where the design predicted failure, it failed, and for the predicted reason.** h=1 and h=2 were
  expected to fail G2 on magnitude alone. They did, by more than an order of magnitude: the largest
  abs(excess) at h=1 is **2.9081 bps** against a 36.0 bps bar. A 92.7 bps-sd one-hour return does not
  support a 36 bps conditional mean, and the data says so.
- **Effect size scales with horizon, cost does not.** Max abs(excess) by h: 2.91 / 5.11 / 8.88 /
  17.18 / 19.85 / 36.52 — close to √h scaling (√24 ≈ 4.9× from h=1 gives ~14 bps; the realised 36.5
  is above that, consistent with the h=24 cells' fatter tails). Cost stays 18.0 bps whatever h is.
  **That divergence is the whole finding.**
- **The census window's unconditional drift is negative at every horizon** (−0.13 to −3.29 bps).
  Because `excess` subtracts `mu_uncond`, the design is not flattered by a bull window — and in this
  window it was not exposed to one.
- **The single coherent structure in the matrix is `vol_ratio BOT`, and it is monotone in h**: excess
  −1.66 / −3.54 / −6.86 / −12.56 / −19.85 / −36.52 bps at h = 1/2/4/8/12/24, breadth 8–9 of 9 at every
  horizon, and **six of the seven highest abs(excess)/SE ratios in the entire matrix (3.29–4.05)**.
  **Low trailing
  relative volatility predicts materially worse forward returns across the panel.** Per-instrument at
  h=24: BTC −19.3, ETH −31.9, SOL −61.7, BNB −22.1, XRP −43.3, ADA −75.8, AVAX −25.5, DOT −25.7,
  LINK −19.0 bps — all nine negative, no instrument carrying the pooled figure.
- **That direction corroborates T-038 and standing directive 10 independently, at the entry level.**
  T-038 found high-vol 1h bars have *better* forward per-unit-risk returns as a **sizing** result with
  no placebo control. This census finds the same sign at **entry**, on both tails, with a control —
  low-vol bars are the bad ones. Two different measurements, same direction. Directive 10's inversion
  is now supported by a second, methodologically stronger observation. **It remains a sign, not an
  effect size, and it is still not harvestable**: G4 rejects it and every horizon below 24 is far
  under the cost wall.
- **`mom_24 BOT` is the mirror-image structure**: excess +2.91 / +5.11 / +8.88 / +17.18 / +17.77 /
  +19.19, positive at every horizon with breadth 7–9. Short-term *reversal* after 24-bar declines,
  not continuation. Note `mom_24 TOP` is negative at every horizon (−0.44 to −9.57) — the same
  reversal seen from the other side. **Intraday 1h momentum on these perps is a reversal effect, not
  a trend effect** — the one paradigm that survived the spot program does not survive a change of
  resolution with its sign intact.
- **`illiq TOP` is a regime casualty**, described in §8: the in-sample illiquid state effectively
  ceases to exist in TEST (19 of 151 pooled dates, median instrument 0).
- **Breadth is not the binding constraint anywhere.** 66 of 72 cells clear G3; the 6 failures
  (breadth 4) all have abs(excess) below 3.6 bps and are noise regardless. Consistency across
  instruments is cheap on this panel because the nine instruments are highly correlated; **breadth
  should not be read as independent confirmation.**

---

## 12. Lessons

1. **The cost wall is now measured, not assumed, and it binds hard below h=12.** At the operator's
   stated target frequency (multiple round trips per day, h ≤ 8) the best gross conditional per-trade
   return available from any of six causal 1h OHLCV+volume variables, on either tail, over 251,946
   pooled bars, is **16.13 bps against an 18.0 bps round trip — 0.90×, and that is the best of 72
   in-sample cells with no selection penalty applied.** This is the evidence the hypothesis-bank
   reopening note demanded: a run under the current `COST_MODEL`, at real rates, on the real sample.
2. **A 72-cell scan on this data has a family-wise noise floor of 47.22 bps, which is above the
   36.0 bps economic bar.** Any future census of comparable width on this panel should be designed
   knowing that its own selection noise exceeds 2× the round trip — i.e. **width is expensive here**,
   and a narrow pre-registered test of one cell would face a far lower bar than the same cell found
   by scanning. Narrower future censuses, or pre-registration of a single cell, buy real power.
3. **The placebo control changed the verdict.** Without G4 this cycle would have reported
   `vol_ratio h=24 BOT` as a passing cell and handed a construct to a follow-on cycle. Control
   distributions on decile-conditional means are not ceremony on this data; they are the difference
   between REJECT and a spent trial. Every future census of this shape should carry one.
4. **The census-window trim must be `max(h) + 1`, not `max(h)`, under the executable anchor.** T-039's
   spec said 24 and its stated rationale required 25. Measured impact here: 9 bars of 251,946, ≤0.0546
   bps, zero status changes. Free to fix, and the next 1h census should fix it.
5. **Level-based thresholds silently expire.** `illiq TOP` fired on 19 of 151 TEST dates and on
   **zero** dates for the median instrument, because liquidity on these perps improved between the
   TRAIN+VAL window and TEST. Any variable whose decile cut is a *level* rather than a *rolling
   percentile* can stop existing out-of-sample without any error being raised. G5 caught this; a
   design without a TEST-presence gate would not have.
6. **1h momentum on these perps is a reversal, not a trend.** `mom_24 TOP` excess is negative at all
   six horizons and `mom_24 BOT` positive at all six. Trend-following intuitions carried down from the
   daily spot program invert at this resolution. Whatever the next intraday hypothesis is, it should
   not assume continuation.
7. **Breadth across these nine instruments is nearly free** (66/72 cells clear 5-of-9) and should not
   be treated as independent corroboration. A breadth gate is a useful floor against single-instrument
   artifacts, but on a panel this correlated it disqualifies almost nothing.
8. **Reading a CSV's line count is not reading its row count.** `trial_sharpe_ledger.csv` has 51 lines
   and 0 data rows. My first run printed 50 and it would have gone into this report as a contradiction
   of `NEXT_TASK.md` had I not checked the file. Parse, don't count.

---

## 13. Raw output locations

Everything below is under `research/results/T-039_raw/`. Produced by
`user_data/research/phase_t039_census.py` in a single run; the function that writes each file is
named. Re-running the script unmodified regenerates all of them byte-identically (verified).

| Artifact | Contents | Produced by |
|---|---|---|
| `run_log.txt` | Complete stdout of the run — every number in this report appears here in context | `Tee` / `_run()` |
| `matrix_executable.csv` | **The 72-cell matrix.** mu_cell, mu_uncond, excess, d, SE, n_eff, bucket counts, per-instrument n and excess (9 cols each), G1–G5, PASS, status | `compute_matrix()` + gate block in `_run()` |
| `matrix_naive_DIAGNOSTIC_ONLY.csv` | Same 72 cells on the naive anchor. **Gates nothing** | `compute_matrix(..., "Fn")` |
| `economics_by_horizon.csv` | §2 cost-wall table: max abs(excess), best `d·mu_cell`, edge÷cost, net per trade, round trips/yr, annual cost drag | `_run()` economics block |
| `best_cell_per_horizon.csv` | Largest abs(excess) cell at each horizon | `_run()` headline block |
| `summary_stats.json` | Verdict, gate counts, status counts, max abs(excess) and its cell, G2-clearing cells, C1a/C1b, P95(M), binding constraint, lag effect, bar counts, TEST-ABSENT list, both sensitivity results | `_run()` headline block |
| `placebo_summary.json` | mean/sd/P50/P95/P99/min/max of M, seed, N_min, k range, both sanity assertions and their outcomes | `placebo_control()` + `_run()` |
| `placebo_draws.csv` | All 1,000 M values in draw order | `placebo_control()` |
| `placebo_argmax_by_draw.csv` | Per draw: k, M, and which (variable, tail, h) supplied the max | `placebo_control()` |
| `spearman_variables.csv` | 6×6 pooled Spearman matrix | `spearman_pooled()` |
| `effective_tests.json` | Eigenvalues, M_eff (Li & Ji and Cheverud–Nyholt), max abs off-diagonal rho, pairs over abs(0.90), implied effective cells | `spearman_pooled()` |
| `g0_coverage.csv` | Per instrument: bars, first/last timestamp, monotonicity, duplicate count, tz, NaN closes, zero-volume bars | `g0_coverage()` |
| `split_report.csv` | Per instrument: train/val/test/train+val/census bar counts, census and TEST first/last, TEST date count, latest bar read by fwd_24 | `_run()` split block |
| `holdout_assertions.txt` | All 45 `assert_no_holdout` results plus the deliberate raise on the raw full series | `_run()` split block |
| `decile_thresholds.csv` | Per instrument × variable: q10, q90, valid count, TOP/BOT bucket counts and fractions | `decile_thresholds()` + `_run()` |
| `g5_test_presence.csv` | Per variable × tail: pooled and all nine per-instrument TEST fired-date counts | `g5_test_presence()` |
| `mu_uncond_executable.csv` | Pooled unconditional forward return per horizon | `_run()` |
| `matrix_sensitivity_trainval_thresholds.csv` | Full matrix with thresholds from untrimmed TRAIN+VAL | `_run()` sensitivity block |
| `matrix_sensitivity_trim25.csv` | Full matrix with a 25-bar trim (no TEST bar read at any h) | `_run()` sensitivity block |
| `cost_model.txt` | `describe_cost_model("taker")`, resolved per-side and round-trip costs, both G2 thresholds | `_run()` |

**Script**: `user_data/research/phase_t039_census.py`. Committed with **`git add -f`** —
`user_data/*` is gitignored (`.gitignore:7`) and a plain `git add` is a silent no-op.

---

## 14. Recommendations to the Director

Advisory only. I did not act on any of these and did not begin any of them.

1. **Close the intraday-entry family at real rates, and record the number, not just the verdict.**
   The reopening note requires "a fresh closure … under the current `COST_MODEL`". This is it, and
   the closure is stronger than a verdict: **at h ≤ 8 the best of 72 in-sample cells returns 0.90× of
   one round trip gross.** I'd record the per-horizon edge-to-cost table in the bank entry, because
   it tells a future Director exactly which horizons are worth revisiting if costs ever fall — and
   how far they'd have to fall. At h=8 a round trip would need to cost under ~8 bps for the best
   in-sample cell to clear 2×; that is roughly half the current all-in taker cost and below the
   exchange fee plus spread alone.

2. **The scope of this closure is narrower than "intraday is dead", and I'd write the boundary
   explicitly.** What was tested: six *univariate decile* conditioners on 1h OHLCV+volume, measured
   as *unconditional-mean differences*. What was **not** tested and is not closed by this cycle:
   variable *interactions* (e.g. `volume_z` high **and** `range_pos` extreme), non-decile
   functional forms, conditional *volatility* or *skew* targets rather than mean returns, and
   anything using data this panel does not hold. A future Director should not cite T-039 as closing
   more than it measured — the 2026-07-21 ledger correction exists because that happened before.

3. **`vol_ratio BOT` deserves one paragraph in the bank, flagged as measured-but-not-harvestable.**
   It is the most coherent structure in the matrix — monotone in h across six horizons, 8–9 of 9
   breadth at every horizon, all nine instruments negative at h=24, and the highest abs(excess)/SE
   ratios present. It also independently corroborates directive 10 and T-038 at the entry level with
   a control neither had (six of the seven highest abs(excess)/SE ratios in the matrix). And it fails
   G4. **I would not fund a construct on it**, but I would record
   that two independent measurements now agree on the sign, so a third cycle does not have to
   rediscover it. If it is ever revisited it must be as a **single pre-registered cell** — a narrow
   test faces a far lower bar than a 72-cell max-statistic — and at `n_trials` reflecting 72 tests of
   debt if the census is what motivated it.

4. **The idea I'd kill early: any construct at h ≤ 4.** Max abs(excess) there is 8.88 bps against
   18.0 bps of cost. That is not a near miss to be closed with better execution or a smarter filter;
   it is a factor of two, measured on a quarter-million bars, before slippage error and before
   selection is priced. Any proposal to trade this panel more than ~6 times a day should be required
   to say which of these numbers it thinks is wrong.

5. **The one place I'd spend the next cycle, if intraday stays on the table: rolling-percentile
   conditioners and interaction cells at h = 12–24, or a re-test at maker rates *if and only if* the
   fill assumption is ever validated.** h=12 already shows 1.19× gross edge-to-cost and h=24 shows
   2.21×; both are below the family-wise noise floor of *this* scan but would not be below the bar of
   a narrow, pre-registered test. That is the cheapest remaining place a real intraday edge could
   still be hiding. I note the manual forbids resting any promotion on `maker_optimistic`, so the
   maker path is only worth naming as a data-collection goal for the dry-run bot, not as a research
   direction now.

6. **Two data-hygiene items for `OPS_BACKLOG.md`** (Reviewer to file; I did not write that file):
   (a) the census-trim off-by-one should be fixed in the *next assignment's* wording, not in this
   script, so T-039's artifacts stay reproducible as run; (b) **BTC's 1h series ends 2026-05-27 18:00
   while the other eight end 2026-05-28 19:00**, a 25-bar shortfall visible in `g0_coverage.csv`. It
   is entirely inside the reserved holdout and affects nothing here, but it will matter the first
   time a cycle uses the holdout, and it is better discovered now than then.

7. **Nine of the instruments carry 9 zero-volume 1h bars each (BNB has 0).** They are handled
   correctly — `illiq` treats them as NaN by design and the affected windows drop out — but they are
   a real data property, they are pooled-identical across eight instruments (suggesting a venue-wide
   outage rather than per-instrument gaps), and no project file records them. Worth a line in the
   standing constraints so the next cycle doesn't treat them as a bug in its own code.

---

## Statement on ambiguity (required item 13)

**One condition in the assignment was internally inconsistent; none was ambiguous in a way that
required a BLOCK, and I resolved nothing by choosing between competing readings of a gate.**

- **The inconsistency**: the census window is specified as TRAIN+VAL *"minus its final 24 bars, so
  that no forward return reads a TEST bar."* Under the mandated executable anchor, `fwd_24` at the
  last census bar reads `c_{t+25}`, so a 24-bar trim leaves exactly one bar of overlap — the first
  TEST bar, 2025-04-22 00:00. The **instruction** (24) is unambiguous; its **stated rationale**
  (no TEST bar read) is off by one. Because the number itself is not ambiguous, and because the
  manual's rule is to transcribe literally, I **executed the literal 24** rather than substituting my
  own reading of the intent, and then **measured the alternative** (25-bar trim: 0 of 72 status
  changes, ≤0.0546 bps, still 0 passing cells — `matrix_sensitivity_trim25.csv`). Both are on disk;
  the verdict is identical under either. Flagged in §5, §12 and §14.
- **No gate condition was ambiguous.** Every conjunction in the assignment is written as `and` and is
  coded as `&`; "at least one of" appears nowhere in the specification and no `or` appears in any gate
  expression. The transcription is checked line-by-line in §10.
- **Two implementation choices were under-specified rather than ambiguous, and I measured both
  instead of assuming**: (a) the decile-threshold estimation sample (census window vs untrimmed
  TRAIN+VAL) — 0 of 72 status changes; (b) the reading of "fires on ≥30 of the 151 TEST dates" as
  pooled-across-instruments vs per-instrument — I applied the pooled reading and reported all nine
  per-instrument counts so the stricter reading is fully auditable; under either reading no cell
  passes, because no cell clears G4.
- **Nothing was assumed because information was missing.** The one factual conflict I found — the
  assignment stating the trial ledger holds 0 rows, against a naive line count of 50 — resolved in the
  assignment's favour on inspection (0 data rows; 50 comment lines plus a header) and is recorded in
  §9 rather than silently reconciled.

---

*Engineer deliverables complete: this report, the raw artifacts under `research/results/T-039_raw/`,
and `user_data/research/phase_t039_census.py`. No Reviewer-owned file was written — not
`research_index.md`, `research_metrics.md`, `strategy_iteration_log.md`,
`strategy_research_notes.md`, `knowledge_base/hypothesis_bank.md`, nor anything under
`research/review_briefs/`. `research/BLOCKED.md` was not created; the cycle completed as assigned.*
