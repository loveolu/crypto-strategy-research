# Archive cost note — pre-2026-07-28 results are not comparable to current runs

**Status: binding. Read before quoting any number produced before 2026-07-28.**

On 2026-07-28 (repair item 1) this repository replaced its implicit execution-cost
assumptions with an explicit `COST_MODEL` in `user_data/research/validator.py`. Every
result produced *before* that date was generated under a different, materially more
expensive cost model. **The two are not comparable, and no ranking, Sharpe
comparison, or family-closure argument may mix them.**

---

## 1. The archived cost model

Every pre-2026-07-28 backtest in this repository charged **15 bps per side, with zero
spread**, expressed one of two equivalent ways:

| Source | Expression | Per side |
|---|---|---|
| `validator.py` (former module constants) | `COMMISSION = 0.001` + `SLIPPAGE = 0.0005` | 15 bps |
| All 34 `user_data/research/phase*.py` one-shot scripts | `FEE = 0.0015` | 15 bps |
| `user_data/research/scratch/test_baseline*.py` | `turn * 0.0015` | 15 bps |
| Real freqtrade engine artifact (`backtest-result-2026-06-11_01-06-44.zip`) | `fee_open = fee_close = 0.0015` | 15 bps |

Round trip: **30 bps**.

Three further properties of the archived model:

- **No bid-ask spread was modelled anywhere**, in the pandas harness or the real
  engine. Spread cost was implicitly assumed to be zero.
- **No maker/taker distinction existed.** A single blended number was applied to
  every fill regardless of order type. There was no `fill_assumption` concept and
  therefore no adverse-selection charge.
- **The venue and instrument were never stated.** The 0.10% commission figure
  corresponds to OKX *spot* taker, but the constant was applied uniformly, including
  to constructs a reader would reasonably assume were perpetuals.
- `monte_carlo()` additionally subtracted a flat `extra_slippage = 0.0005` per trade
  as its stress scenario, on top of the 15 bps/side already baked into the P&L.

## 2. The current cost model

`validator.COST_MODEL`, OKX regular tier (non-VIP), USDT-margined perpetual swap,
rates as of 2026-07-28:

| Component | Value |
|---|---|
| maker fee | 2.0 bps/side |
| taker fee | 5.0 bps/side |
| slippage | 3.0 bps/side (estimate, uncalibrated) |
| spread | 2.0 bps quoted; a taker crosses half = 1.0 bps/side (estimate, uncalibrated) |
| adverse selection | **required** on the maker path, no zero default (unset by default) |

- `fill_assumption = "taker"` → **9.0 bps/side, 18.0 bps round trip**
- `fill_assumption = "maker_optimistic"` → 2.0 bps fee + `adverse_selection_bps`,
  which must be set explicitly with a basis string before any maker run will execute.

## 3. Size of the discontinuity

| Comparison | Archived | Current | Ratio |
|---|---|---|---|
| Round-trip **all-in** (fees + slippage + spread), taker | 30.0 bps | 18.0 bps | archived is **1.67x** too expensive |
| Round-trip **fees only**, taker | 30.0 bps | 10.0 bps | archived is **3x** too expensive |
| Round-trip **fees only**, maker | 30.0 bps | 4.0 bps | archived is **7.5x** too expensive |

The 3x and 7.5x figures compare the archived *all-in* 15 bps/side against
*fee-only* perp rates, because the archived model never separated its fee component
from its slippage component. They are the correct figures for asking "was this
construct killed by a fee assumption that does not match the venue?" — which is why
they appear in the intraday/sub-daily family reopening note. The 1.67x figure is the
correct one for asking "what would this construct's net P&L actually be today?"

**Do not quote 3x or 7.5x as an expected P&L improvement.** They are fee-line
comparisons, not all-in ones.

## 4. Scope — what is affected

Every one of these was produced under the archived model:

- All 34 `user_data/research/phase*.py` scripts and everything they print.
- All 63 result JSONs in `user_data/research/results/`.
- All 18 `research/results/T-*_report.md` cycle reports and their review briefs.
- Every verdict, Sharpe, CAGR, profit factor, DSR figure, and family-closure
  argument recorded in `research/research_index.md`,
  `knowledge_base/hypothesis_bank.md`, `research/current_champion.md`, and
  `user_data/research/BEST_STRATEGY_REPORT.md`.
- The champion (`TrendVolTarget`) headline figures, including the Sharpe 1.26 /
  DD -16.6% / +458% numbers and the T-030 (H-TailAlloc) 80/20 promotion.

## 5. Rules

1. **The `phase*.py` scripts are frozen.** Their `FEE = 0.0015` constants are the
   reproduction record of runs already counted in the trial ledger. Do not re-point
   them at `COST_MODEL`; doing so would silently break reproduction of the archived
   numbers. This includes `phase4_deep_validation.py` and `phase5_2018_stress.py`,
   which formerly imported the deleted `COMMISSION`/`SLIPPAGE` constants and now
   carry a pinned literal with a frozen-cost comment.
2. **New work must use `validator.per_side_cost()` / `round_trip_cost()`.** No new
   script may hardcode a fee, slippage, or spread number.
3. **Never rank an archived result against a current one.** A post-2026-07-28 Sharpe
   is mechanically advantaged by roughly 12 bps of round-trip cost relief per trade.
   Turnover-heavy constructs benefit far more than low-turnover ones, so the bias is
   not a constant offset and cannot be corrected by eye.
4. **Re-testing is not free.** Any archived construct re-run at current costs
   consumes a fresh trial and must be recorded in the ledger. A cheaper cost model is
   not a licence to re-run rejected constructs until one passes — that is precisely
   the multiple-testing failure the DSR gate exists to catch.
5. **A family closed on cost grounds may be reopened; a family closed on other
   grounds may not.** The archived cost error is only a valid reason to revisit a
   construct whose rejection turned on fee drag. See the intraday/sub-daily family
   note in `knowledge_base/hypothesis_bank.md`. Finding #12 (21-22 UTC anomaly) was
   re-examined and **stays closed**: its fee-to-edge ratio improves from 25:1 to
   ~3.3:1 at real maker rates and is still losing.

---

*Created 2026-07-28 as an amendment to repair item 1. See
`research/audits/2026-07-28_repo_audit.md` §2 for the audit that established the
archived values, and `PROJECT_OPERATOR_MANUAL.md` "Execution and cost model" for the
governing rules.*
