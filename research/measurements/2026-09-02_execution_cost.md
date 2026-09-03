# Execution-cost measurement — OKX USDT perps, maker vs taker (A-011, 2026-09-02)

**Operator-directed measurement, zero trials, no signal tested.** Answers one question: what does a
retail order actually cost to execute on this venue, and does a resting (maker) order pay for its
adverse selection? Every number in `validator.COST_MODEL` for slippage and spread was labelled
"estimate, uncalibrated". This calibrates them.

**Scripts:** `user_data/research/fetch_okx_micro.py` (fetch; refuses to overwrite),
`user_data/research/adverse_selection_sim.py` (analysis). **Raw:** `user_data/research/data/okx_micro/`
— `book_samples.jsonl` (40 rounds × 9 books, 2026-09-02 ~23:30 UTC), `<inst>_1m_raw.jsonl` (43,300
1m candles each, 2026-08-03 → 2026-09-02, verbatim API responses), `fetch_log.json`, results CSV.
Endpoints: `/api/v5/market/books`, `/api/v5/market/history-candles`. `requests` only.

## Method

- **Spread**: median quoted (ask−bid)/mid over 40 snapshots per instrument.
- **Taker slippage**: walk the sampled ask side for a $1k / $5k / $20k order; VWAP vs mid.
- **Maker adverse selection** `a_k = E[drift_k | filled] − E[drift_k | all]`, drift_k =
  close[t+k]/close[t] − 1, k ∈ {1, 5, 15, 60} min. A bid posted at close×(1 − half_spread) is
  "filled" if the next bar's low trades strictly through it; symmetric on the ask; both sides
  averaged. Negative a_k = price kept moving against you after filling you.
- **All-in per side**: taker = half_spread + 5.0 fee + slippage; maker = 2.0 fee − half_spread − a_k.

## Results (bps; $5k order; a_k at 15 min)

| inst | spread | slip $5k | fill rate | a_15m | **TAKER/side** | **MAKER/side** |
|---|---|---|---|---|---|---|
| BTC | 0.013 | 0.006 | 81% | −0.56 | **5.01** | **2.55** |
| ETH | 0.042 | 0.021 | 85% | −0.55 | 5.04 | 2.53 |
| SOL | 1.001 | 0.500 | 79% | −1.27 | 6.00 | 2.77 |
| BNB | 1.456 | 0.728 | 63% | −1.74 | 6.46 | 3.01 |
| XRP | 0.743 | 0.371 | 80% | −1.29 | 5.74 | 2.92 |
| ADA | 4.989 | 2.494 | 63% | −3.85 | 9.99 | 3.36 |
| AVAX | 1.396 | 2.013 | 70% | −2.27 | 7.71 | 3.57 |
| DOT | 1.154 | 3.470 | 73% | −2.17 | 9.05 | 3.59 |
| LINK | 0.902 | 1.086 | 75% | −1.83 | 6.54 | 3.37 |
| **MEAN** | **1.300** | **1.188** | 74% | **−1.72** | **6.84** | **3.07** |

**Round trip: taker 13.67 bps ($5k) / 14.85 ($20k); maker 6.15 bps. Model assumed 18.0.**

Adverse selection is flat across 1→60 min for every instrument (a one-time hit, not a persistent
drift) and is under 1 bp on BTC/ETH. Depth splits the universe: BTC/ETH hold ~$300k at best; AVAX
$538, DOT $232, LINK $1,377 — thin-book alts pay 2–5 bps of book-walk on a $5k order.

## What it does to the T-039 cost wall (gross edges are T-039's in-sample maxima, unchanged)

| hold | gross | net @18.0 (model) | net @13.7 (taker, measured) | net @6.2 (maker) |
|---|---|---|---|---|
| 8h | 16.13 | −1.87 | **+2.5** | **+10.0** |
| 12h | 21.42 | +3.42 | +7.8 | +15.3 |
| 24h | 39.81 | +21.8 | +26.1 | +33.7 |

## Caveats — read before acting

1. **Fill rate is an UPPER bound.** "Next bar's low traded through the quote" means price touched
   it, not that a retail order at the back of a $300k BTC queue got its turn. True fill rate on
   deep books is materially lower; on thin alt books, touch ≈ fill. The maker figures above are
   therefore closer to reality on the alts than on BTC/ETH.
2. **Missed-trade cost is not included.** At ~74% fill, ~26% of signals are missed, and the missed
   ones are systematically those where price ran away favourably. This cost exists only relative to
   a signal and cannot be priced here.
3. **One regime.** 30 days (Aug–Sep 2026) of candles; book samples from a single quiet hour. Spreads
   and slippage widen in stress; this is a fair-weather floor, not a stress estimate.
4. **A lower wall does not create an edge.** The gross edges in the wall table failed their own
   family-wise placebo in T-039 (p = 0.221). Lower cost makes a real edge tradeable; it does not make
   a noise edge real. No signal is established by this document.

## Recommendation (operator decision — NOT applied)

`validator.COST_MODEL` slippage (3.0) and spread (2.0) are now measured at ~1.2 and ~1.3 bps
equal-weight. Updating them changes every future cycle's economics and is a standard change under
`PROJECT_OPERATOR_MANUAL.md` "Execution and cost model". Suggested form: **per-instrument**
half-spread + slippage from this table, taker fee 5.0, i.e. BTC/ETH ≈ 5.0 bps/side, thin alts
≈ 7–10. A single equal-weight number (6.8) would over-charge BTC and under-charge ADA/DOT.
`maker_optimistic` remains barred from promotion; the `adverse_selection_bps` it requires now has a
measured basis (~1.7 equal-weight, ~0.6 BTC/ETH, ~2–4 thin alts) but fill-rate uncertainty (caveat 1)
still makes the maker path a forward-evidence question.
