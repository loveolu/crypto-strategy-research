# NEXT_TASK — T-039 / H-IntradayEdgeFloor-1h

**Task ID**: T-039
**Program**: `perps`
**Cycle type**: RESEARCH
**Assigned**: 2026-08-03, Research Director
**n_trials before this cycle**: **0** (read from `research/research_metrics.md`, "Perps program — ACTIVE")
**Trials this cycle will spend**: **0** — zero, whether the hypothesis passes or fails. This cycle
evaluates **no strategy variant**: it runs a conditional-mean census on held data and produces a
matrix plus a pass/fail verdict. Per `PROJECT_OPERATOR_MANUAL.md`, "Research budget": *"A cycle
killed at a pre-gate spends ZERO trials — no variant was evaluated, so none is counted."* No variant
is evaluated here on either branch, so `n_trials` stays **0** of the **30**-trial cap in either case.

---

## Objective

Measure, on the 338,933-bar 1h perp sample at the real 2026-07-28 cost model, whether **any**
entry-level conditional edge computable from 1h OHLCV+volume is large enough per trade to clear the
18.0 bps taker round-trip cost by a factor of two — and if none is, close the reopened intraday
family at real rates rather than on archived cost assumptions.

## Hypothesis

**On the nine OKX USDT perpetual swaps at 1h, there exists at least one (state variable, horizon,
tail) cell — drawn from a pre-registered family of 6 variables × 6 horizons × 2 tails = 72 cells,
every variable computable causally from 1h OHLCV+volume at bar close — whose decile-conditional
forward return, measured on TRAIN+VAL only, exceeds the unconditional forward return by at least
36.0 bps (2 × the 18.0 bps taker round trip), holds that sign in at least 5 of the 9 instruments
individually, and exceeds the 95th percentile of a family-wise circular-shift placebo distribution.**

This is a statement about the **existence of a cost-feasible intraday entry edge**, not about any
particular indicator. It is deliberately constructed so that its rejection carries family-level
information.

---

## Zero-cost pre-gate

**The entire cycle is the pre-gate.** There is no backtest, no optimization, no strategy object.
Everything below is arithmetic on held feathers.

### Definitions — transcribe these literally into code

All variables are computed **per instrument, on the full 1h series, before any slicing** (see
"Warmup" under Split specification). All are causal: the value at bar `t` uses only bars `<= t`.

Let `c_t` = close, `h_t` = high, `l_t` = low, `v_t` = base volume, and `r_t = log(c_t) - log(c_{t-1})`.

| # | Variable | Definition at bar `t` | Mechanism |
|---|---|---|---|
| 1 | `mom_24` | `log(c_t) - log(c_{t-24})` | Time-series momentum at intraday resolution. The one paradigm that survived the spot program (trend gate), never run at 1h or at real perp rates. |
| 2 | `vol_ratio` | `std(r, 24 bars ending t) / std(r, 168 bars ending t)` | Volatility expansion. Tests T-038's inversion at the **entry** level rather than the sizing level (see "Standing directive compliance"). |
| 3 | `volume_z` | `(log(1+v_t) - mean(log(1+v), 168 bars ending t)) / std(log(1+v), 168 bars ending t)` | Participation / liquidity shock. `research_metrics.md` records the 3.5x-SMA volume filter as "the one plausible genuine signal component" of this project's first construct; never isolated or tested at 1h. |
| 4 | `range_pos` | `(c_t - min(l, 24 bars ending t)) / (max(h, 24 bars ending t) - min(l, 24 bars ending t))`; NaN if the denominator is 0 | Channel/breakout position. Direct 1h instance of the archived "Opening Range Breakout Family" and "Volatility Breakout Based on the Open or Previous Close" cards (`knowledge_base/archive/closed_families.md`, lines 356-400). |
| 5 | `cs_mom_rank` | cross-sectional rank of `mom_24` across the instruments with a non-NaN value at timestamp `t`, scaled `(rank - 1)/(n_present - 1)` to `[0,1]`; NaN if `n_present < 6` | Cross-sectional structure across the 9-instrument panel — a portfolio mechanism, distinct from variable 1. |
| 6 | `illiq` | `mean over the 24 bars ending t of ( abs(r_s) / (v_s * c_s) )`, then * 1e9; a bar with `v_s == 0` contributes NaN and the window value is NaN if any contributing bar is NaN | Amihud (2002) illiquidity — price impact per unit of quote volume. The closest available proxy for the order-book axis, which `research_index.md` records as unreachable. Never tested in this project. |

**Horizons**: `h` in `{1, 2, 4, 8, 12, 24}` bars.

**Tails**: `TOP` = the instrument's 10th (highest) decile of the variable; `BOT` = the 1st (lowest)
decile. Decile thresholds are computed **per instrument on TRAIN+VAL only** and are never
re-estimated on TEST.

**Forward return — use the executable convention, not the naive one:**

```
fwd_h(t) = log(c_{t+1+h}) - log(c_{t+1})
```

This matches `validator.signal_to_returns`'s anti-lookahead convention (`user_data/research/validator.py`
lines 505-536: `position[t] = signal[t-2]`, so a signal formed at close `t` is in position from close
`t+1` onward). Anchoring at `c_t` instead would grant one bar of lookahead and would inflate `h=1`
most of all. **Also report, as a diagnostic only, the naive `log(c_{t+h}) - log(c_t)` version**, so
the size of the execution-lag effect is on the record. The naive version may never be used in any
gate.

**Cell statistics.** For each of the 72 cells `(variable, h, tail)`, pooled across the nine
instruments over the census window:

```
mu_cell   = mean( fwd_h(t) )  over bars t in the cell's decile          [report in bps]
mu_uncond = mean( fwd_h(t) )  over ALL bars in the census window        [report in bps]
excess    = mu_cell - mu_uncond                                         [report in bps]
d         = +1 if excess > 0 else -1
```

**Census window**: each instrument's full available 1h history up to and including
**2025-04-21 23:00:00+00:00** (TRAIN+VAL), **minus its final 24 bars**, so that no forward return
reads a TEST bar. Eight instruments start 2022-01-01, BNB starts 2022-12-23; pooled TRAIN+VAL bars
before the 24-bar trim = **252,162** (Director-verified 2026-08-03).

### Gates

Compute the **full 72-cell matrix first** — it is cheap and it is the deliverable's most valuable
output — then apply the gates. Do **not** stop early: a map of where the cost wall bites is worth
more than a single verdict.

| Gate | Condition | Disposition |
|---|---|---|
| **G0 — Coverage** | Every one of the 9 instruments loads, and `date` is strictly increasing with no duplicate timestamps. Report per-instrument bar counts and first/last timestamps. | A missing or non-monotonic series is a **BLOCK**, not something to route around. |
| **G1 — Non-degeneracy** | The cell's decile bucket holds **>= 1,000** pooled bars **and >= 50** bars for each of the 9 instruments. | A cell failing G1 is marked **INELIGIBLE** and cannot pass, regardless of its statistics. |
| **G2 — Economic (C1)** | `d * excess >= 36.0` bps **AND** `d * mu_cell >= 18.0` bps | Both clauses required. **This is an `and`, not an `or`.** |
| **G3 — Breadth (C2)** | `d * excess_i > 0` for **>= 5 of the 9** instruments computed individually | Threshold adopted from T-038's pre-registered breadth rule (KILL if < 5 of 9). |
| **G4 — Placebo control (C3)** | `abs(excess) > P95(M)`, where `M` is the family-wise max-statistic control distribution defined below | Guards the "passes by arithmetic" failure mode. |
| **G5 — TEST presence** | Applying the **TRAIN+VAL** decile threshold to the variable over 2025-04-22 00:00 -> 2025-09-19 23:00 UTC, the cell fires on **>= 30 of the 151** TEST dates | A cell failing G5 is marked **TEST-ABSENT** and may not be carried forward. **Read the state variable only — no TEST forward returns may be computed for any purpose.** |

**A cell PASSES only if it clears G1 AND G2 AND G3 AND G4 AND G5 — all five, conjunctively.**

### The placebo control (G4) — construction is mandatory and specified here in full

Per `PROJECT_OPERATOR_MANUAL.md` and the Director's own pre-gate-design rule, a gate must be
**capable of failing for the reason the hypothesis is wrong**. State explicitly in the report what
would make G2 pass in the absence of a real mechanism, and why G4 prevents it.

*What would make G2 pass without a mechanism*: the top decile of a magnitude variable such as
`vol_ratio` or `volume_z` selects high-variance bars. The **mean** of a high-variance subsample is
itself a high-variance estimate, so with 72 cells scanned, the largest `abs(excess)` in the matrix is
expected to be materially above zero even under pure noise. This is exactly the T-038 pathology the
Engineer named a **trap** (T-038 brief, recommendation 4): the inverted construct looks good
in-sample for a decomposition reason rather than a causal one.

*Why G4 prevents it*: the control preserves each variable's marginal distribution, each return
series' autocorrelation and volatility clustering, and the panel's cross-sectional structure, while
destroying the **alignment** between variable and return. It then takes the **maximum over all 72
cells per draw**, so the threshold is a family-wise one and the 72-cell scan is priced in.

```
Repeat 1,000 times (seed 20260803, stated here so it is pre-registered):
  1. Draw one integer offset k ~ Uniform[720, N_min - 720], where N_min is the shortest
     instrument's census-window length. Use the SAME k for all nine instruments in a draw,
     so cs_mom_rank's cross-sectional alignment is preserved.
  2. Circularly shift each instrument's six state-variable series forward by k bars,
     leaving its return series in place.
  3. Recompute per-instrument decile thresholds on the shifted variables and recompute
     abs(excess) for all 72 cells.
  4. M_draw = max over the 72 cells of abs(excess).
Report: mean(M), sd(M), P50(M), P95(M), P99(M).
```

**Mandatory sanity assertions** (`research/strategy_research_notes.md`, lesson 20 — a suspiciously
clean diagnostic is a bug signal, and a census must assert that its two sides differ):

- `sd(M) > 0` and `P95(M) > 0`. If either is zero the control is degenerate — **BLOCK**, do not
  interpret.
- For at least one cell, the shifted `abs(excess)` must differ from the unshifted `abs(excess)`.
  Exact equality across all cells is a bug signature (the shift did not take effect), not a result.
- Report the pairwise Spearman correlation matrix of the six variables, pooled. **Not gating.**
  Correlated variables reduce the **effective** number of independent tests in the family, which
  **lowers** `P95(M)` — the max of fewer independent draws is smaller — and therefore makes G4
  **EASIER to clear, not harder**. Report the effective number of independent cells implied by the
  correlation structure alongside the raw 72. If any pair exceeds `abs(0.90)`, state in the report
  that **G4's protection is weaker than the 72-cell framing suggests**, and name which cells are
  affected.

### Falsification statement

**This hypothesis is REJECTED if, after computing all 72 cells, no cell satisfies G1 AND G2 AND G3
AND G4 AND G5 simultaneously.**

**It is CONFIRMED (pre-gate PASS) if at least one cell satisfies all five.** A confirmed cell is a
*result*, not a strategy: it is handed to a future cycle, which builds and backtests the construct
and spends the trial. **This cycle spends no trial on either branch and produces no promotion
candidate.**

**On the boolean operators** (`PROJECT_OPERATOR_MANUAL.md`, "Falsification conditions must be
transcribed literally"): every conjunction above is `and`, written as `and`. "at least one of" does
not appear anywhere in this specification. **If any condition in this file reads as genuinely
ambiguous to you, do NOT choose an interpretation and do NOT pick the conservative one — write
`research/BLOCKED.md` quoting the exact sentence and stop.**

### Required robustness outputs for any PASSING cell

Adopted from the T-038 Engineer's recommendation 5 (per-year and disjoint-window views beat a
bootstrap CI):

1. **Per-year** `excess` for each calendar year in the census window (2022, 2023, 2024, 2025-partial).
2. **Three disjoint sub-windows** of roughly equal bar count, each with its own `excess` and breadth.
3. **Common-window re-run**: census restricted to 2022-12-23 00:00 -> 2025-04-21 23:00 for all nine
   instruments, so the pooled statistic is not driven by BNB's absence from the first year.
4. Whether the cell implies a **long** construct (`d = +1` on a TOP tail, or `d = -1` on a BOT tail
   interpreted as an avoidance filter) or a **short** construct. **Flag any short-implying cell
   explicitly**: the "Short side / symmetric TSMOM" family is CLOSED in the
   `knowledge_base/hypothesis_bank.md` FAMILY STATUS LEDGER, and standing directive 5 requires the
   Reviewer to rule on whether a follow-on short construct is admissible before any cycle builds one.
   Reporting the cell is correct; assuming it is buildable is not.
5. **Selection debt.** Any passing cell was chosen from a **72-cell census**. The report must state
   prominently, and the Reviewer must carry into the brief, that a follow-on construct built on this
   cell **inherits 72 tests of selection debt**. The Director of that cycle must set `n_trials` to
   reflect it — **not 1** — and must state the value used and its derivation in `NEXT_TASK.md`. **A
   construct built on a censused cell and evaluated at `n_trials = 1` is a multiple-testing
   violation, not a promotion candidate.**

If **no** cell passes, items 1-3 are not required; report the full matrix and stop.

---

## Scientific rationale

**The mechanism under test is the cost wall itself.** `PROJECT_OPERATOR_MANUAL.md`, "Execution and
cost model" fixes the taker path at **9.0 bps/side, 18.0 bps round trip**. The operator's stated goal
is a bot that trades multiple times per day. At one round trip per day that is 18.0 x 365 = 6,570 bps
= **65.7% per year of cost drag**; at three round trips per day it is **197% per year**. No project
file records an estimate of the gross per-trade edge available at 1h on this venue, so no Director
can currently tell whether that goal is reachable — and **`n_trials` is capped at 30**, which is not
enough budget to discover it by backtesting constructs one at a time.

The family this tests was **REOPENED on 2026-07-29** precisely because its closure rested on the
wrong cost assumption. The hypothesis bank states the condition for closing it again
(`knowledge_base/hypothesis_bank.md`, "REOPENING (2026-07-29)"):

> **Status: OPEN for re-test at real rates. It may not be re-closed on archived evidence**; a fresh
> closure requires a run under the current `COST_MODEL`.

This cycle is that run. Its rejection would supply the evidence the ledger explicitly demands, and
would do so at zero trial cost.

The six variables are not arbitrary. Each names a distinct structural mechanism with a cited source:
momentum and channel position instantiate the archived ORB and volatility-breakout cards
(`knowledge_base/archive/closed_families.md` lines 356-400, Kaufman Ch.16 — Crabel, Fisher, Raschke);
volume participation is the one component `research_metrics.md` flags as plausibly genuine from this
project's own first construct; Amihud illiquidity is the standard price-impact measure and the
nearest reachable proxy to the order-book axis `research_index.md` records as blocked; cross-sectional
rank is a portfolio mechanism the 9-instrument panel makes available and which no perps cycle has
touched. Volatility expansion is included because T-038 measured the **opposite** of the expected
sign at 1h and that lead should be tested where it was not tested — at entry, with a placebo control.

**On the program's strongest cross-cycle finding**
(`research/review_briefs/T-037_PERPS_TRANSITION_brief.md`): *predictive constructs did not survive
out-of-sample; risk-management and structural mechanisms did.* This cycle does not contradict that
finding — it prices it. If the census fails, the reason predictive constructs did not survive at this
venue is quantified as an **execution-cost** fact rather than an inference from ~100 spot rejections,
and future cycles can stop paying for it. If it passes, the surviving cell is the only place a
predictive intraday construct is worth a trial at all.

### Standing directive compliance (`research/STANDING_DIRECTIVES.md`)

- **Directive 10** (volatility-conditioned de-risking is INVERTED; any construct reducing exposure as
  trailing volatility rises must say why it escapes): **this cycle assigns no such construct.** It is
  a census, and `vol_ratio` is measured symmetrically on both tails with a placebo control. Directive
  10's own scope clause states the volatility family is **not** closed and that the T-038 bank entry
  was basket-exposure-sizing only; an entry-level conditional-mean measurement is a different object.
  Note also directive 10's caveat that `-0.442905` is a **sign**, never an effect size — do not
  quote it as one.
- **Directive 9** (state the expected SE of the primary metric before assigning): done below.
- **Directive 8** (pre-2026-07-31 metrics used truncated indicator warmup, systematically depressing
  val and test figures): binding on how you compute the variables — see "Warmup" below. No archived
  TEST or walk-forward figure is cited in this assignment.
- **Directive 5** (closed families are closed): the only closed family this cycle can touch is the
  short side, and only if a BOT-tail cell passes; handling is specified above (flag, do not build).
- **Directive 1** (claim-must-cite-test): every number in your report must cite the raw artifact and
  the script line that produced it. See "Deliverables".

### Expected standard error of the primary metric (directive 9)

Director-computed on the real feathers, 2026-08-03, pooled TRAIN+VAL, top-decile bucket = 25,216
bars, using non-overlapping subsampling (`n_eff = n_bucket / h`) to account for overlapping forward
windows:

| h | sd of `fwd_h` | `n_eff` | SE of `mu_cell` | SEs to the 36.0 bps threshold |
|---|---|---|---|---|
| 1 | 92.7 bps | 25,216 | **0.58 bps** | 62 |
| 4 | 182.1 bps | 6,304 | **2.29 bps** | 16 |
| 24 | 442.2 bps | 1,051 | **13.64 bps** | 2.6 |

`SE(excess)` is approximately `1.05 x SE(mu_cell)`, since `mu_uncond` is estimated on roughly ten
times the data. **The worst case, `h = 24`, resolves the 36.0 bps threshold at about 2.6 SE** —
adequate, not lavish; `h <= 12` is comfortable. This is the resolution directive 9 exists to require,
and it is available only because the sample is 1h: the same census on the 151-bar daily TEST split
could not resolve it at all. **You must recompute and report these SEs per cell from the actual
data** rather than quoting this table — it is a Director's power calculation, not your result.

## Expected regime(s)

- **Where it should work**: trending, high-participation regimes where directional follow-through
  persists for several hours — 2023H2 and 2024Q4 in this sample. Longer horizons (`h = 12, 24`) are
  where a 36.0 bps excess is physically plausible, because the 24-bar return has a 442 bps standard
  deviation to draw from.
- **Where it should fail**: `h = 1` and `h = 2` almost certainly fail G2 on magnitude alone — a
  92.7 bps-sd one-hour return does not support a 36.0 bps conditional mean — and that failure is a
  *finding*, not a defect in the design. Chop and low-participation regimes (2025H1, the only
  negative calendar half-year in the series, which sits in VAL) should show the smallest excess.
- **Where the design could mislead**: a bull-heavy census window inflates `mu_uncond`, which the
  `excess` construction subtracts out by design; and a single 2024Q4-type episode could carry a cell,
  which is why per-year and disjoint-window views are mandatory for any passing cell.

---

## Prior-work check

| Adjacent work | Why this escapes its failure mode |
|---|---|
| **T-038 / H-BasketVolTarget-1h** (REJECT at pre-gate P2, 2026-08-01) — same nine perps, same 1h sample. | T-038 tested one **sizing overlay** on a fixed basket; this tests **entry-level** conditional means across six variables. Decisively, T-038's headline statistic (`Q1-Q5 = -0.442905`) had **no placebo control** — its bootstrap CI straddled zero and its quintile means were non-monotonic, which is why the Reviewer recorded the sign as robust and the magnitude as not. G4 here is the control that census lacked. |
| **#6 — overnight/time-of-day breakout, Zarattini-style** (FAIL: N below any statistical floor, 2-10 trades in 3-5 years). | That construct was daily and event-sparse. This census has **252,162 pooled TRAIN+VAL bars** and a 25,216-bar decile bucket; the failure mode was sample size, and it does not recur. |
| **#12 — hours 21-22 UTC anomaly** (REAL but untradeable; fee-to-edge ~25:1, ~3.3:1 at maker rates). | **Stays closed and is not retested**: no variable here is a clock. The hypothesis-bank reopening note is explicit that the family reopened but #12 did not. Its lesson — that a statistically real intraday effect can be economically dead — is the reason G2 is denominated in cost multiples rather than t-statistics. |
| **#8 — 61-strategy autonomous sweep** (0/61, found a ceiling and no edge). | That was a sweep that selected a backtest winner. This is a pre-registered census with a **family-wise max-statistic control** over all 72 cells and **zero** backtests, so the multiple comparison is priced rather than exploited. The 2026-07-21 ledger correction also warns against generalising row #8; this assignment does not rely on it. |
| **H-IVSizing (spot, daily, implied vol)** and standing directive 10. | Handled above under directive compliance — no de-risking construct is assigned. |

### Engineer recommendations from `research/review_briefs/T-038_brief.md` — the brief WAS opened

1. **Semivariance / downside-deviation variant of the P2 census** — **REJECTED as this cycle's
   object.** Reason (one line, as required): it re-enters the sizing layer immediately after a
   decisive inversion there, whereas the prior question — whether *any* intraday entry edge clears
   18.0 bps — determines whether the sizing layer is worth refining at all; the idea stays live and
   uncosted for a later cycle.
2. **The 1h sample is worth using** — **ADOPTED.** It is the whole basis of this cycle's power.
3. **Fix the hourly boundary before assigning another 1h cycle** — **ADOPTED, already satisfied.**
   Resolution-aware `holdout_boundary(program, freq=...)` landed 2026-08-02 (`5cbd7617a`); the manual
   records 1h -> 23:00. Use it; do not hand-roll a boundary.
4. **The inverted construct is a trap, untestable without a crash-sample pre-gate** — **ADOPTED as
   the design's central constraint.** G4 is that pre-gate in generalised form: `vol_ratio`'s top
   decile must beat a placebo that preserves its distribution and destroys its alignment.
5. **Per-year and disjoint-window views beat the bootstrap CI** — **ADOPTED**, mandatory for any
   passing cell.

### Alternatives the Director considered and rejected this cycle (recorded so they are not re-derived)

- **Funding-rate carry / crowding.** The natively-perp mechanism, and dead for the frozen split
  triple: all nine `*-1h-funding_rate.feather` files start **2026-02-26 / 2026-02-28** and end
  2026-05-28 — **zero overlap** with a TEST window ending 2025-09-19, and entirely inside the
  reserved holdout. Consistent with A-005's note that funding had to be excluded from the benchmark.
  See "Environment notes".
- **Mark-vs-last basis as an order-flow / liquidation-pressure proxy.** Rejected at reachability:
  `BTC_USDT_USDT-1h-mark.feather` holds **7,810** rows against 38,587 OHLCV bars (~20% coverage), and
  the basis itself is ~1-3 bps with 8-29% exact zeros from tick quantization on the cheaper alts.
  Not worth a cycle in that state.

---

## Deployment envelope

Quoted for you because you cannot see the Director's prompt. Every figure below is transcribed from
`PROJECT_OPERATOR_MANUAL.md` or `user_data/config_perp.json`.

| Dimension | Constraint |
|---|---|
| Venue | OKX USDT perpetual swaps, regular (non-VIP) fee tier |
| Config | `user_data/config_perp.json` — `"trading_mode": "futures"`, `"margin_mode": "isolated"`, `"fee": 0.0009` |
| Instruments | Exactly the 9 in that config's `pair_whitelist`: BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT, LINK — all `/USDT:USDT`. **No others.** |
| Timeframe | **1h** (this cycle's whole point). The 1d feathers are not used. |
| Fill assumption | **`taker`**. `maker_optimistic` may not be used anywhere in this cycle, not even as a secondary comparison — there is no promotion argument here for it to contaminate, and the manual forbids resting any promotion on it. |
| Cost — exact figures | maker fee **2.0 bps/side**; **taker fee 5.0 bps/side**; slippage **3.0 bps/side** (estimate, uncalibrated); spread **2.0 bps quoted, a taker crosses half = 1.0 bps/side** (estimate, uncalibrated); **taker all-in 9.0 bps/side, 18.0 bps round trip**. `validator.per_side_cost("taker")` returns **0.0009**. The single source of truth is `COST_MODEL` in `user_data/research/validator.py`; resolve every cost number through `per_side_cost()` / `round_trip_cost()` and **hardcode none**. |
| Return envelope | Not applicable — this cycle produces no equity curve. Stated for completeness: any backtest above **100% CAGR is presumed defective**, and the manual's check order is (1) costs actually applied, not defaulted or zero; (2) signal lag — `signal_to_returns`'s 2-bar convention; (3) indicators computed over the full series before splitting; (4) survivorship. |
| Target frequency | The operator's goal is a bot trading **multiple times per day**. This cycle exists to measure whether that is affordable; `h = 24` is included as the one-round-trip-per-day boundary case, not as a target. |

---

## Data

**Read-only. Exact paths, all verified present by the Director on 2026-08-03:**

```
user_data/data/okx/futures/BTC_USDT_USDT-1h-futures.feather
user_data/data/okx/futures/ETH_USDT_USDT-1h-futures.feather
user_data/data/okx/futures/SOL_USDT_USDT-1h-futures.feather
user_data/data/okx/futures/BNB_USDT_USDT-1h-futures.feather
user_data/data/okx/futures/XRP_USDT_USDT-1h-futures.feather
user_data/data/okx/futures/ADA_USDT_USDT-1h-futures.feather
user_data/data/okx/futures/AVAX_USDT_USDT-1h-futures.feather
user_data/data/okx/futures/DOT_USDT_USDT-1h-futures.feather
user_data/data/okx/futures/LINK_USDT_USDT-1h-futures.feather
```

Columns: `date, open, high, low, close, volume`, `date` tz-aware UTC. `volume` is **base** volume —
`illiq` requires quote volume, so use `v_s * c_s` as specified. Coverage: eight instruments
2022-01-01 -> 2026-05-28 at 38,612 bars (BTC 38,587 to 05-27); BNB 2022-12-23 -> 2026-05-28 at
30,062; **pooled 338,933**. All nine are in `MANIFEST.json` and `verify` is clean.

**No other data file may be read** — not the 1d feathers, not mark, not funding, not any external
axis. No new data axis is assigned this cycle, so fetching one would be a scope violation.

**Data must not be created, modified, deleted, downloaded or rebuilt.** From
`PROJECT_OPERATOR_MANUAL.md`, "Data acquisition is not research": *"A cycle whose git diff touches
`user_data/data/` is INVALID — the Reviewer rejects it on that basis alone, without assessing the
hypothesis."* Run `python scripts/data_manifest.py verify` before and after your work and paste both
outputs into the report. **A failing verify is a stop condition; never run `build` to clear it, and
`FREQTRADE_SKIP_DATA_VERIFY=1` invalidates the cycle.**

---

## Split specification

**The perps split triple is FROZEN. It is not yours and not the Director's to choose.** Pin as
literal dates, never as fractions — `validator.split_70_15_15()` is deprecated and warns.

```
train_end 2024-11-22    val_end 2025-04-21    test_end 2025-09-19
```

Use `validator.split_by_dates(df, "2024-11-22", "2025-04-21", "2025-09-19")`.

- **Census window (G1-G4)**: TRAIN + VAL only, i.e. bars up to and including
  **2025-04-21 23:00:00+00:00**, minus each instrument's final 24 bars so no forward return reads a
  TEST bar. Instruments with longer history keep it — BTC/ETH/etc. from 2022-01-01, BNB from
  2022-12-23 — giving a longer TRAIN with an identical TEST, as the manual specifies.
- **TEST window (G5 only)**: 2025-04-22 00:00 -> 2025-09-19 23:00 UTC, **151 UTC dates**. Only the
  state variable is read here. **No TEST forward return may be computed, for any purpose, including
  a diagnostic.**
- **Reserved holdout (perps): bars strictly after 2025-09-19.** The boundary is a **date resolved to
  its last complete bar**: at 1h the inclusive instant is **23:00**, not midnight — this was fixed on
  2026-08-02 after it silently cost T-038's 1h slice a date (152 vs the benchmark's 151). Call
  `validator.assert_no_holdout(obj, label=..., program="perps", freq="1h")` on every frame you build
  and paste the result. `validate()` **raises `HoldoutViolation`** rather than trimming, by design.
- A candidate evaluated on different split dates is **VOID against the program benchmark**, not
  weaker evidence.

### Warmup (directive 8)

Compute **all six state variables on each instrument's full 1h series first, then slice.** The
longest lookback is 720 bars (the normalisation windows and the control's minimum offset).
Truncating warmup at a split edge is the defect that systematically depressed every archived val and
test metric before 2026-07-31 (BTC 1d SMA200: TEST Sharpe -1.2159 -> +0.2129 after the fix). Rolling
windows are backward-looking, so computing them on the full series is causal and safe — **but decile
thresholds are a selection statistic and must be estimated on TRAIN+VAL only.**

---

## Required validation

**Applicable gates**: G0-G5 above, plus the sanity assertions, plus the manifest checks. That is the
complete list for this cycle.

**Gates that do NOT apply, stated explicitly rather than silently omitted** — this cycle evaluates no
strategy variant, produces no return series and no candidate:

- **Deflated Sharpe Ratio.** Not computed. No trial is spent, so nothing is appended to
  `research/trial_sharpe_ledger.csv`, which stays at **0 rows**.
- **Monte Carlo gate.** Not run. For the record, and because it is routinely misreported: it has
  **three** outcomes — **PASS** = every seed's p5 Sharpe > 0; **FAIL** = every seed's p5 Sharpe <= 0;
  **INSUFFICIENT** = the seeds disagree in sign, which maps to **PARK, never PROMOTE**. INSUFFICIENT
  is the absence of a result, not a soft FAIL. `n_sims` may be raised only as a **pre-registered**
  choice; raising it after seeing a straddling result invalidates the cycle.
- **`validator.sharpe_difference_se()`.** Mandatory on **every candidate**, and there is no candidate
  here. Do not fabricate one to satisfy the rule. When a follow-on cycle builds a construct from a
  passing cell, it must compute and report the paired-difference SE and implied t-statistic against
  `research/benchmarks/perps_equal_weight_benchmark_TEST_returns.csv` on the 151 identical TEST
  dates; those figures are reported and do **not** gate.
- **Walk-forward, parameter stability, regime breakdown, trade-count validation.** All are
  properties of a strategy; none exists this cycle.

The **1,000-draw placebo control at seed 20260803 is pre-registered here** and may not be enlarged,
re-seeded, or re-run with a different offset rule after seeing the result. If the control comes back
degenerate under the sanity assertions, BLOCK — do not re-draw.

---

## Promotion criteria

**PROMOTE IS CURRENTLY UNREACHABLE, AND THIS CYCLE CANNOT REACH IT FOR A SECOND, INDEPENDENT REASON.**

First reason (program-wide): `research/trial_sharpe_ledger.csv` holds **0 rows**. The harness needs
**10** before cross-trial variance is estimable, so every DSR presently returns
`trial_var_source = "estimator_proxy"` and **criterion 7 caps the maximum available verdict at
PARK**. Do not design or argue toward an outcome that cannot be reached. Second reason (this cycle):
no candidate is produced at all.

All seven are quoted in full from `PROJECT_OPERATOR_MANUAL.md`, "Promotion rule — FINAL", so that
they are on the record and so a follow-on cycle inherits them. **A candidate is PROMOTED only if ALL
SEVEN hold. Failing any one is REJECT or PARK. There is no discretion** — you may not weigh a strong
result on one criterion against a failure on another.

1. **DSR >= 0.95 on the TEST split at the current `n_trials`.** An absolute gate, not a comparison
   against the benchmark (which is computed at `n_trials = 1` by construction, sr0 = 0.0, DSR
   0.93914). DSR measures selection luck, not skill relative to holding.
2. **Candidate TEST-split Sharpe > 0** in absolute terms.
3. **Candidate TEST-split Sharpe >= 1.10 x the benchmark's** — same window, cost model and fill
   assumption; against the committed benchmark, **>= 0.135653 per-period (+2.5916 annualised)**.
   Compare per-period Sharpes. The paired-difference SE and t-statistic must be computed and reported
   but do **not** gate. A series compared against itself gives delta = 0 and does not pass — 1.00x is
   not 1.10x.
4. **Candidate REALIZED MaxDD <= 1.25 x the benchmark's realized TEST MaxDD** — benchmark -25.02%, so
   the cap is **-31.27%**. Realized only, never the Monte Carlo MaxDD distribution.
5. **Every validation gate in `NEXT_TASK.md` passed.**
6. **Monte Carlo gate is PASS, not INSUFFICIENT.**
7. **DSR `trial_var_source` is not `"estimator_proxy"`.**

**Benchmark of record** (`PROJECT_OPERATOR_MANUAL.md`, "Promotion comparison"; full record at
`research/benchmarks/perps_equal_weight_benchmark.md`): equal-weight, **monthly-rebalanced** long
basket of the 9 config instruments, 1d, `COST_MODEL` taker, funding excluded. Window
2022-12-23...2025-09-19, splits 2024-11-22 / 2025-04-21 / 2025-09-19. **TEST Sharpe 0.123321
per-period (+2.3560 annualised), TEST MaxDD -25.02%, N = 151, DSR 0.93914 at `n_trials = 1`.**
Because the benchmark's own TEST Sharpe is **positive**, criterion 3 binds rather than criterion 2 —
a merely profitable candidate does not clear it.

**Note for the follow-on cycle, recorded here because it is easy to get wrong**: a 1h construct's
**per-period Sharpe is hourly** and is not comparable to the benchmark's **daily** per-period Sharpe.
Criterion 3 requires date-identical overlap, so a 1h candidate must have its net return stream
aggregated to the **151 daily TEST buckets** and its daily per-period Sharpe compared against
0.135653. Do not annualise one side and not the other, and do not compare an hourly Sharpe to a daily
one.

---

## Research budget

`PROJECT_OPERATOR_MANUAL.md`, "Research budget" sets the default per-cycle limits at **3 strategy
variants, 1 optimization run**, each variant counting as one trial. **The Director may assign fewer,
never more.** For T-039:

| Item | Assigned |
|---|---|
| Strategy variants | **0** |
| Optimization runs | **0** |
| Trials against `n_trials` | **0** |
| Hyperopt / parameter search of any kind | **0 — forbidden this cycle** |
| Placebo control draws | **1,000**, seed **20260803**, pre-registered above |
| State variables | **6**, exactly as defined — do not add a seventh, do not substitute |
| Horizons | **6**, exactly `{1, 2, 4, 8, 12, 24}` |
| Tails | **2** (`TOP`, `BOT`) |

The variable set, horizon set and tail set are **pre-registered and closed**. Adding a variable after
seeing the matrix is the multiple-testing failure this design exists to prevent, and it would
invalidate the family-wise control. If you believe a seventh variable is essential, that is a finding
for the report and an input to the next Director — not a change you make.

**Exceeding any assigned number invalidates the cycle.** If you reach a limit without a result,
report that and stop.

---

## Deliverables

**File ownership** (`PROJECT_OPERATOR_MANUAL.md`, "File ownership — Engineer / Reviewer division",
2026-08-02). This assignment does **not** narrow or widen it:

- **You write:** `research/results/T-039_report.md`, raw artifacts under `research/results/T-039_raw/`,
  and your scripts under `user_data/research/`. **Nothing else.**
- **You do not write:** `research_index.md`, `research_metrics.md`, `strategy_iteration_log.md`,
  `strategy_research_notes.md`, `hypothesis_bank.md`, or anything in `review_briefs/`. Those are the
  Reviewer's. An Engineer writing a Reviewer-owned file is a recorded **spec deviation** — T-038's
  Engineer did exactly this and it is in the brief.

**Required contents of `research/results/T-039_report.md`:**

1. Verdict: **pre-gate PASS** (>=1 cell clears G1-G5) or **REJECT** (none does), stated in the first
   line.
2. `n_trials` before and after: **0 -> 0**. Trial ledger row count before and after: **0 -> 0**.
3. The **full 72-cell matrix**: for each `(variable, h, tail)` — `mu_cell`, `mu_uncond`, `excess`,
   `d`, per-cell SE by non-overlapping subsampling, bucket bar count, per-instrument breadth count,
   and G1-G5 status. Present it as a readable table **and** dump it as CSV to
   `research/results/T-039_raw/`.
4. The naive-anchor diagnostic matrix (`log(c_{t+h}) - log(c_t)`), clearly labelled as **not used in
   any gate**, with one sentence on the size of the execution-lag effect.
5. Control distribution summary: `mean(M)`, `sd(M)`, `P50/P95/P99(M)`, plus both sanity assertions
   and their outcomes.
6. The pairwise Spearman correlation matrix of the six variables, with the `abs(0.90)` note if
   triggered.
7. G0 coverage table: per-instrument bar counts, first/last timestamp, monotonicity check.
8. `assert_no_holdout` output for every frame built, and both `data_manifest.py verify` outputs.
9. `validator.describe_cost_model("taker")` output, showing 9.00 bps/side and 18.00 bps round trip
   resolved from `COST_MODEL` rather than hardcoded.
10. For any passing cell: the four robustness outputs (per-year, three disjoint sub-windows,
    common-window re-run, long/short flag).
11. **Traceability**: every figure in the report must be traceable to a named raw artifact and the
    script that produced it. T-038's audit found five diagnostics that appeared in no raw artifact —
    they recomputed correct, but the gap is on the record and is not to be repeated.
12. **Your recommendations to the next Director** — what you saw that the matrix does not show.
13. An explicit statement of whether any condition in this assignment was ambiguous and how you
    resolved it (or that none was).

**Scripts**: name them `phase_t039_*.py` under `user_data/research/`. **`user_data/*` is gitignored
(`.gitignore:7`), so a plain `git add` silently does nothing** — commit them with **`git add -f`**.
This is the same gap that lost `fng_raw.json` permanently and left T-038's three scripts untracked
until 2026-08-02. Your scripts must be re-runnable **unmodified** by the Reviewer and must produce
byte-identical output; seed every random draw.

---

## Environment notes

- **`research/BLOCKED.md` does not exist** — there is no outstanding blocker to repair. If you create
  one, quote the exact ambiguous sentence and stop.
- **`research/champions/` does not exist.** Expected: it is created by the Reviewer on the first
  PROMOTE. Not a missing file.
- **The perps program has no champion.** TrendVolTarget and the 80/20 stance are spot artifacts at
  the pre-2026-07-28 cost model — **void as perps evidence**, not a baseline. The benchmark above is
  the comparison object.
- **Funding data cannot support any hypothesis on the frozen split triple.** All nine
  `user_data/data/okx/futures/*-1h-funding_rate.feather` files span **2026-02-26/28 -> 2026-05-28**
  (266-273 rows each) — entirely after the TEST window and inside the reserved holdout. A-005
  excluded funding from the benchmark for the same reason. **Proposed ops task for
  `research/OPS_BACKLOG.md` (Reviewer to file; the Director may not write that file this cycle):
  investigate whether OKX or any reachable venue serves funding history back to 2022 — if not, the
  funding axis is permanently unavailable to this program and should be recorded as closed at the
  data layer rather than re-proposed each cycle.**
- **`BTC_USDT_USDT-1h-mark.feather` holds only 7,810 rows against 38,587 OHLCV bars (~20% coverage).**
  The other instruments' mark series are complete. Recorded so no future cycle rediscovers it; not
  used this cycle.
- **`validator.load(symbol, timeframe)` resolves against `DATA_DIR` with a flat filename convention
  and will not find the futures tree.** Read the feathers directly with `pd.read_feather` at the
  exact paths listed above, then `set_index("date").sort_index()`.
- **RESEARCH:OPS ratio, perps program**: currently **1:1** (T-038 research, A-005 ops), below the
  6-cycle threshold at which the 2:1 floor begins to bind. T-039 is a RESEARCH cycle and takes it to
  **2:1**. No exception is being claimed.
- **Meta-review counter**: 17 of 25 before this cycle; not due. The Reviewer advances it.
- **The T-038 review brief was opened and read by the Director** (2026-08-03). All five Engineer
  recommendations are dispositioned above.
- If any file this assignment names is missing, **do not invent its contents** — record it and
  proceed, or BLOCK if it is load-bearing.
