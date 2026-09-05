# CRYPTO-EXP-034 — Simplified Morning/Evening Star continuation

Date frozen: 2026-09-04 PDT. Independent parent: none. This is the named three-candle pattern in
`knowledge_base/08_entries.md`; it is not an NR4/opening-range variant and not a B2 modification.

## Hypothesis

A large directional candle, a smaller counter-direction candle, and renewed large movement in the
original direction represent a pause followed by continuation. On liquid crypto perpetuals, the
next 4h return in that direction should exceed realistic round-trip friction.

## Frozen rule

- Nine liquid OKX USDT perpetuals; mechanical 4h bars from canonical 1h data.
- Body size is `abs(close-open)`. “Large” means strictly above that completed candle's trailing
  20-bar mean body; “small” means strictly below it. No percentile or fitted threshold.
- Morning pattern: large bearish bar, small bullish bar, large bullish bar. Go long at the next open.
- Evening pattern: large bullish bar, small bearish bar, large bearish bar. Go short at the next open.
- Exit exactly one 4h bar later at its open. One position per coin, equal 1/9 sleeves. Both entry and
  exit pay measured instrument-specific taker friction. Long and short results are reported
  separately, while the pre-registered primary rule contains both directions.
- No trend, BTC, volume, gap, wick, target, stop, asset-selection, or alternative-hold filter.

## Validation gates

TRAIN: 2023-01-22 through 2024-11-22 23:00 UTC. Keep held-out sealed unless the combined rule has
at least 300 trades and 20 per coin; gross expectancy exceeds expected round-trip cost; at least six
coins are net-positive; both long and short gross expectancy are positive; and observed combined
gross expectancy beats at least 97.5% of 999 common circular-shift placebos (seed 34034, shifts of
at least 30 days). These direction gates prevent one side hiding a failed mirror.

If TRAIN passes, open 2024-11-23 through 2026-09-01 once and require positive net return, Sharpe,
profit factor, six positive coins, both directions net-positive, two positive VAL/TEST/FWD segments,
and positive performance at 2× costs, one-bar delay, and after top-5% removal. Then transfer the
unchanged rule to Kraken. Superiority requires +61.7% return and drawdown no worse than −5.5%, with
consistent fixed-rule and true walk-forward B2 comparisons kept separate.

One construct is evaluated. Failure will not be followed by body-window, direction, hold, filter,
or coin searches on the seen data.

## Result

TRAIN produced **751 trades** (69–104 per coin). Combined gross expectancy was **−0.36 bps/trade**
before **13.64 bps** expected round-trip friction. Longs earned +9.88 gross bps but still failed the
cost hurdle; shorts lost −8.51 gross bps before costs. Combined after-cost return was **−11.20%**,
maximum drawdown **−12.97%**, Sharpe **−1.34**, profit factor **0.78**, and only **3/9** coins were
positive. The economic, breadth, and short-direction gates failed, so no placebo was required and
held-out data stayed sealed.

**Verdict: REJECTED_TRAIN_GATE.** The exact symmetric 4h pattern has no tradeable continuation edge.
The mildly positive long gross mean is below friction and was observed inside a pre-registered
two-direction test; it is not permission to create a post-hoc long-only variant.

Full required diagnostics and cost-model boundaries: `EXP_033_035_FULL_DIAGNOSTICS.md` and the
machine-readable `research/measurements/EXP034/summary.json`.
