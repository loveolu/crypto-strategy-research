# CRYPTO-EXP-040 — Turn-of-the-candle replication feasibility

## Primary-source hypothesis

Shanaev, Vasenin, and Stepanov (2023), *Turn-of-the-candle effect in bitcoin returns*, report that
Bitcoin returns average approximately +0.58 bps in minutes 0, 15, 30, and 45. Their strategy buys
for each boundary minute. Its favorable implementation depends on accumulating enough Bitfinex
rolling volume to reach a zero-fee tier; the paper explicitly describes initial fees as prohibitive.
Primary open-access source: https://pmc.ncbi.nlm.nih.gov/articles/PMC10015199/

The mechanism is exact and OHLCV-representable: enter before each quarter-hour boundary minute and
exit after that minute. It is distinct from EXP-039's first-10-second signed-order-flow predictor.

## Frozen pre-backtest gates

Before inspecting the local boundary-minute returns, require both:

1. at least 365 complete days of authentic one-minute BTC data, with a later chronological holdout;
2. the paper's +0.58 bps gross effect must exceed this project's measured executable round-trip
   friction, or an authenticated maker/fee-tier execution plan must close the gap without assuming
   fills or volume tiers the account does not have.

## Feasibility result

- Local archive: only 28 complete common one-minute days (2026-08-04 through 2026-09-01), below the
  365-day minimum.
- Measured project friction: approximately 13.7 bps per taker round trip.
- Published gross effect: approximately 0.58 bps per boundary minute.
- Cost/effect ratio: **23.6×**. Even before spread variation and latency, the published mean is about
  13.1 bps/trade below the project's realistic execution hurdle.

**Verdict: REJECTED_PRE_BACKTEST_COST_AND_DATA_GATES.** Local minute returns were not inspected;
zero trades and zero trial. Do not assume Bitfinex zero fees, apply leverage, aggregate only winning
dates, or use the 28-day sample to rescue the idea. Reopen only with ≥365 days and authenticated
execution economics whose complete round trip is below the prespecified gross edge.
