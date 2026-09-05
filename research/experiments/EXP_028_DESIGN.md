# CRYPTO-EXP-028 design — one-minute volume-shock overshoot

Date frozen: 2026-09-04 PDT. Independent data axis: recent OKX 1m microstructure
archive. Status ceiling: Experimental; 30 days cannot establish a durable edge.

## Hypothesis

An unusually large one-minute return accompanied by unusually high quote volume
contains urgent market-order flow. At the most extreme tail, temporary price impact
may exceed information content, causing a five-minute reversal. The economic
question is whether that reversal exceeds measured taker friction.

## Frozen rule

- Nine liquid OKX USDT perpetuals, one-minute finalized candles.
- At each completed bar, rank absolute one-minute return and quote volume against
  the preceding 1,440 completed bars, excluding the current bar.
- Signal when absolute-return rank is at least .99 and quote-volume rank at least
  .95. Trade against the shock direction at the next minute open; exit at the open
  five bars later. One position per coin; equal 1/9 sleeves; no leverage.
- Expected taker execution uses the measured instrument-specific $5k book-walk
  estimate plus the sampled half-spread and 5 bps fee per side. No stop, target,
  regime gate, coin removal, direction filter, threshold search or hold search.

## Chronological gates

Use the first 15 complete common UTC days as TRAIN, the next 7 as validation, and
the remaining complete days as untouched TEST. Do not open validation or TEST unless
TRAIN has at least 200 trades and 15 per coin, mean gross expectancy exceeds the
mean measured round-trip taker cost, at least six coins are net-positive, both long
and short gross expectancy are positive, and the observed gross mean beats 97.5%
of 999 circular signal-state shifts (seed 28028, minimum one-day displacement).

If TRAIN passes, require each held-out segment to be net-positive with PF > 1,
at least six positive coins, and survival at 2x cost, a one-minute entry delay, and
top-5% trade removal. Regardless of outcome, do not promote beyond Experimental:
extend the immutable forward archive to at least one year before candidate-grade
walk-forward validation.
