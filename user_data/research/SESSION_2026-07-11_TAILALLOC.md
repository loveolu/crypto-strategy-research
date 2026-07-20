# Session 2026-07-11 — H-TailAlloc: portfolio-level allocation between champion and defensive variant

Pre-registered, single-shot, pre-gated experiment (**would-have-been trial #98**; pre-gates
cost zero n_trials). Script: `phase20_tailalloc.py`. Assignment: `research/NEXT_TASK.md`
(2026-07-10, Research Director cycle #9). No new signal, no new parameters — convex
combinations of two ALREADY-VALIDATED daily return streams.

## 1. Pre-registration block (LOCKED before any results were produced)

Written and saved to this file before any number existed. Everything below the end marker
was filled in afterwards.

### Hypothesis

The champion's residual MC tail (~30%) is structural to concentrated long-only BTC+ETH
exposure. The defensive variant carries the same core mechanism with a radically thinner
tail (MC P(DD<−25%) = 1%) via 9-asset breadth plus a portfolio-vol cap. Because the two
streams' DRAWDOWN profiles differ far more than their return correlation suggests, an
interior allocation (majority champion) inherits enough defensive tail protection to clear
the ≤20% bar while retaining most of the champion's return — a dominating point neither
endpoint offers.

### Harness conventions (identical to phase15/16/18/19 for the champion stream)

- **CHAMPION**: BTC+ETH futures 1d feathers (2020-01→2026-05), fees 0.15%/side on
  |Δposition|, 2-bar lag, per-asset weight = `quantize(core × clip(0.40/rv30,0,1)) / 2`.
- **DEFENSIVE** (frozen spec from 2026-06-11, NOT re-tuned): same TVT construct across
  BTC, ETH, SOL, XRP, ADA, AVAX, DOT, LINK, BNB — equal weight 1/9 each, plus second
  vol-target layer at portfolio level (25% target, 25%-step quantized scale on portfolio
  weights). Same fees, lag, signal, sizing parameters as champion per asset.
- Calendar master index: **BTC futures calendar** (2020-01-01 → 2026-05-27).
- 70/15/15 chronological split judged on TEST; MC = 1,000 monthly-block shuffles, seed 11;
  DSR via `freqtrade_dsr.py`.

### Locked free constant — pre-listing asset handling (DEFENSIVE stream)

**Rule: zero-weight pre-listing (frozen before any computation).**

On any day before an asset's feather data begins, that asset's target weight is **0**
(the core gate and scale are treated as 0; NaN closes produce 0 exposure). The equal-weight
divisor remains **9** (the full frozen asset set) — weights are NOT renormalized across
only-listed assets. Rationale: matches the original phase7/phase9 implementation that
produced the recorded defensive-variant metrics; renormalization would inflate pre-2021
alt exposure and change the validated stream.

Documented listing starts on this calendar (for audit):
BTC 2020-01-01; ETH/XRP/ADA/AVAX/DOT/LINK 2020-10-01; SOL 2021-01-23; BNB 2022-12-23.

### Pre-gate A — stream replication (both endpoints; ZERO n_trials)

**CHAMPION replication gate** (phase15/16/18/19 conventions):
- Full Sharpe 1.0–1.4, TEST Sharpe 0.30–0.50, MC P(DD<−25%) 20–45% at 1,000 sims seed 11.
- Recorded reference: 1.11 / 0.39 / 30.5%.

**DEFENSIVE replication gate** (same harness conventions, same calendar):
- CAGR 10–18%, Sharpe 0.9–1.3, MaxDD −10% to −17%, TEST Sharpe 0.13–0.33,
  MC P(DD<−25%) ≤ 5% at 1,000 sims seed 11.
- Recorded reference (2026-06-11): 14.0% / 1.10 / −12.9% / 0.23 / 1%.

**STOP RULE**: either stream out of band → STOP everything; file as data-integrity finding.

### Pre-gate B — frontier census (only if A passes; ZERO n_trials)

1. Report return correlation between streams: full window and TEST split; all-days and
   in-market-days-only (in-market = either stream's gross exposure > 0).
2. For w ∈ {0.0, 0.1, …, 1.0} (w = champion capital fraction; grid LOCKED):
   - **(i)** Daily-rebalanced arithmetic blend: `r = w·r_champ + (1−w)·r_def` (reference).
   - **(ii)** Fixed capital slices compounded separately; rebalanced to (w, 1−w) **MONTHLY**
     on completed month-end dates; incremental reallocation fee = `|w_actual − w| × 2 × 0.0015`
     (both legs, fraction of total portfolio value — consistent with harness turnover accounting).
3. Judge everything on **(ii)**; report (i) once to show implementation gap.
4. For each w on (ii): full Sharpe, TEST Sharpe, CAGR, MaxDD, MC P(DD<−25%) (1,000 sims seed 11).
5. **Candidate selection (locked)**: w* = the **LARGEST** w with MC P(DD<−25%) ≤ 20%.

**STOP RULE**: FAIL unless ALL of:
- w* ≥ 0.5 (if champion must be diluted below half, direction closes),
- TEST Sharpe(w*) ≥ champion TEST Sharpe − 0.05,
- CAGR(w*) ≥ defensive-variant CAGR + 2pp.

If no w satisfies tail bar, or w* fails other conditions → portfolio-tail direction CLOSED.

### The trial (ONLY if both pre-gates pass — consumes trial #98)

ONE construction: w* fixed-slice monthly-rebalanced portfolio (stream ii). Full stack:
70/15/15 judged on TEST; `wf_window_stability` at 3/4/5/6; MC 1,000 seed 11; DSR at
n_trials=98; champion baseline recomputed at 98; `family_context`; look-ahead audit on
rebalance dates (month-end uses only completed-month data); per-year fee accounting.

### Required validation bars (pre-declared; ALL must hold to promote)

- MC P(DD<−25%) ≤ 20% at w*, AND
- TEST Sharpe(w*) ≥ champion TEST − 0.05, AND full Sharpe(w*) ≥ champion full − 0.05, AND
- WF majority-positive at ≥ 3 of 4 window configs (3/4/5/6), AND
- DSR at n_trials=98 ≥ champion baseline recomputed at n_trials=98, AND
- CAGR(w*) ≥ defensive CAGR + 2pp, with per-year turnover/fee accounting.

### Promotion criteria

- ALL bars pass → PORTFOLIO promotion (not champion replacement): `best_strategy_so_far.py`
  untouched; `strategy_portfolio.md` gains w* stance; `current_champion.md` portfolio note.
- Any bar fails → REJECT, document fully, nothing changes.
- Pre-gate B fails → explicit "portfolio-tail direction CLOSED" entry.

### Budget

Maximum backtested constructions: **1** (formula-selected w* only). Weight grid 0.1 steps;
rebalance cadence monthly; defensive spec FROZEN. n_trials advances 97 → 98 ONLY if both
pre-gates pass and trial runs.

**— END OF PRE-REGISTRATION BLOCK —**

## 2. Pre-gate A — endpoint stream replication: **PASSED**

Both streams reproduced the recorded bands on the BTC master calendar (2020-01→2026-05),
1,000 MC sims seed 11:

| Stream | FULL Sharpe | TEST Sharpe | CAGR | MaxDD | MC P(DD<−25%) |
|---|---|---|---|---|---|
| CHAMPION (recorded) | 1.11 | 0.39 | +22.7% | −16.9% | 30.5% |
| CHAMPION (this run) | 1.11 | 0.39 | +22.7% | −16.9% | 30.5% |
| DEFENSIVE (recorded) | 1.10 | 0.23 | +14.0% | −12.9% | 1% |
| DEFENSIVE (this run) | 1.10 | 0.23 | +14.0% | −12.9% | 0.7% |

Pre-listing rule applied: zero-weight, divisor=9 (see §1). Defensive MC tail 0.7% vs recorded
1% — inside band (≤5%), not a mismatch.

## 3. Pre-gate B — frontier census: **PASSED**

### Return correlation (reported before frontier numbers)

| Pair | Pearson r |
|---|---|
| Full window | +0.797 |
| TEST split | +0.861 |
| In-market days only (full) | +0.800 |
| TEST in-market only | +0.861 |

High correlation confirmed (honest failure mode (a) from the assignment) — but the frontier is
**not** degenerate: drawdown profiles differ enough that an interior point exists.

### Frontier — monthly-rebalanced fixed slices (stream ii; the implementable version)

| w (champ %) | FULL Sh | TEST Sh | CAGR | MaxDD | MC tail |
|---|---|---|---|---|---|
| 0.0 | 1.10 | 0.23 | +14.0% | −12.9% | 0.7% |
| 0.1 | 1.13 | 0.26 | +14.9% | −13.3% | 1.1% |
| 0.2 | 1.15 | 0.28 | +15.8% | −13.6% | 1.2% |
| 0.3 | 1.16 | 0.30 | +16.7% | −13.9% | 2.0% |
| 0.4 | 1.17 | 0.32 | +17.6% | −14.2% | 3.5% |
| 0.5 | 1.16 | 0.34 | +18.5% | −14.6% | 5.0% |
| 0.6 | 1.16 | 0.35 | +19.4% | −15.0% | 7.1% |
| 0.7 | 1.15 | 0.36 | +20.2% | −15.4% | 10.7% |
| **0.8 (w\*)** | **1.14** | **0.38** | **+21.1%** | **−15.9%** | **16.5%** |
| 0.9 | 1.12 | 0.38 | +21.9% | −16.4% | 22.1% |
| 1.0 | 1.11 | 0.39 | +22.7% | −16.9% | 30.5% |

Reference only — daily-rebalanced blend at w=0.5 (stream i): MC tail 5.0% vs 5.0% monthly
(gap negligible at this weight; implementable version is not materially worse here).

**Formula-selected w\* = 0.8** (largest w with MC tail ≤ 20%).

Pre-gate B conditions: w\* ≥ 0.5 **PASS** (0.8); TEST Sh ≥ champ−0.05 **PASS** (0.38 vs 0.34
bar); CAGR ≥ def+2pp **PASS** (21.1% vs 16.0% bar).

## 4. Trial #98 — w\*=0.8 portfolio: **ALL VALIDATION BARS PASSED → PORTFOLIO PROMOTION**

Full stack on the w\*=0.8 monthly-rebalanced portfolio (80% champion sleeve / 20% defensive
sleeve, rebalanced to target weights at each completed month-end, 0.15%/side on traded fraction):

| Metric | Champion | w\*=0.8 portfolio | Bar | Verdict |
|---|---|---|---|---|
| MC P(DD<−25%) | 30.5% | **16.5%** | ≤ 20% | PASS |
| TEST Sharpe | 0.39 | **0.38** | ≥ 0.34 | PASS |
| FULL Sharpe | 1.11 | **1.14** | ≥ 1.06 | PASS |
| CAGR | +22.7% | **+21.1%** | ≥ +16.0% | PASS |
| WF majority-positive | 3/4 configs | **3/4** | ≥ 3/4 | PASS |
| DSR @ n_trials=98 | 0.6245 | **0.6423** | ≥ baseline | PASS |
| Look-ahead | — | prefix-stable (max diff 1.4e−5) | causal | PASS |

70/15/15: TRAIN 1.35 | VAL 0.76 | TEST 0.38. Family context: TEST Sharpe rank 13/64 (80th
pctile), same neighborhood as the champion.

Per-year returns vs champion standalone show the expected cost of the 20% defensive dilution in
strong trend years (2020 −8.4pp, 2023 −1.5pp) with identical bear-year behavior (2022 −3.9%).

## 5. Verdict

**H-TailAlloc: PORTFOLIO PROMOTION at w\*=0.8.** The hypothesis is **confirmed**: an interior
allocation fixes the champion's MC tail (30.5%→16.5%) while retaining most of its return and
TEST Sharpe — a point neither endpoint offers. The champion code (`best_strategy_so_far.py`,
`TrendVolTarget.py`) is **unchanged**; the recommended deployment stance is now an **80/20
monthly-rebalanced portfolio** documented in `strategy_portfolio.md`.

**n_trials: 97 → 98** (one trial consumed). Deterministic re-run reproduced every number.

## 6. Lessons

1. **Return correlation ≠ frontier degeneracy.** r≈0.80 on daily returns, yet MC tail drops
   from 30.5% to 16.5% at w=0.8 because the defensive sleeve's *drawdown path* diversifies
   the portfolio's block-shuffle tail — a Kaufman/Vince portfolio-construction effect, not a
   second signal.
2. **The tail-fix window is narrow.** w=0.8 clears the ≤20% bar (16.5%); w=0.9 fails (22.1%).
   There is no slack — this is the efficient frontier knee, not a broad plateau.
3. **Lesson #14 answered:** portfolio-level allocation CAN reduce the champion's structural MC
   tail without becoming the defensive variant. The sizing layer was closed; the allocation
   layer was open — and now has a validated interior point.
4. **Monthly rebalancing is sufficient.** At w=0.5 the daily vs monthly implementable streams
   match on MC tail (both 5.0%); no need for daily reallocation in practice.
5. **Honest caveat:** TEST Sharpe 0.38 vs champion 0.39 is essentially tied — the portfolio
   buys tail relief (+14pp on MC) for ~0.01 TEST Sharpe and ~1.6pp CAGR vs champion alone.
   Forward expectation for the portfolio stance: re-derive as ~8–18% CAGR at ~18% DD (between
   the two endpoints, closer to champion).

Standing rule unchanged: **dry-run only, no real capital on backtest evidence.**
