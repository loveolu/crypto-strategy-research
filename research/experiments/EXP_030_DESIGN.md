# CRYPTO-EXP-030 design — one-minute BTC price-discovery lead

Date frozen: 2026-09-04 PDT. Independent mechanism: cross-market price discovery
on the recent OKX 1m archive. Status ceiling: Experimental because only 29 complete
common days are available.

## Hypothesis

Urgent information reaches BTC first because it is the deepest crypto market. An
extreme BTC one-minute return with extreme quote volume should therefore predict
same-direction returns in liquid alt perpetuals during the next five minutes.
Unlike EXP-016, this does not wait for a BTC rebound or select already-lagging alts;
it tests pure sub-minute-to-minute information propagation.

## Frozen rule

- BTC plus ETH, SOL, BNB, XRP, ADA, AVAX, DOT and LINK OKX USDT perpetuals.
- On completed BTC 1m bars, compare absolute return and quote volume with the prior
  1,440 completed bars, excluding the current bar. Require return percentile ≥.99
  and quote-volume percentile ≥.95.
- At the next minute open, take the BTC shock direction in all eight alts; exit at
  the open five bars later. Equal 1/8 sleeves, one basket at a time, no leverage.
- Charge each alt's measured $5k taker fee + half-spread + book-walk cost on entry
  and exit. No lagging-alt filter, regime gate, threshold/hold search, stop, target,
  direction subset or coin removal.

## Chronological gates

First 15 complete common UTC days are TRAIN; next 7 validation; final 7 TEST. Keep
both later segments sealed unless TRAIN has ≥100 basket events, ≥100 legs per coin,
mean gross expectancy above mean measured round-trip cost, ≥6/8 positive coins,
positive gross expectancy after both up and down BTC shocks, and a 999-draw circular
BTC-signal shift placebo p≤.025 (seed 30030, minimum one-day displacement).

If all TRAIN gates pass, require validation and TEST separately positive after
costs and survival at 2x cost, one-minute delay and top-5% removal. No result from
29 days can be promoted beyond Experimental; candidate-grade evidence requires at
least one year of forward history and rolling walk-forward validation.
