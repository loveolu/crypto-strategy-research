# CRYPTO-EXP-039 — Quarter-hour order-flow feasibility gate

## Primary-source hypothesis

Kim and Hansen (2026), *The Quarter-Hour Effect: Periodic Algorithmic Trading and Return
Predictability in Cryptocurrency Futures* (arXiv:2607.09426v2), report that perpetual-futures
activity and phase-specific dependence concentrate in the first 10 seconds after quarter-hour
boundaries. Their quarter-hour opening order imbalance predicts returns over four to twelve hours,
with weaker effects at finer clock frequencies. Primary source:
https://arxiv.org/abs/2607.09426

This is structurally distinct from the project's generic intraday-seasonality and one-minute OHLCV
shock tests: it requires trade-level aggressor direction at a precise clock phase.

## Frozen pre-signal data gate

Before defining a trading rule or inspecting forward returns, require:

- at least 365 complete common UTC days across at least six liquid perpetual contracts;
- trade-event timestamps fine enough to isolate the first 10 seconds after each 00/15/30/45 minute;
- aggressor/taker side and executed size for every retained trade;
- duplicate and gap audit plus an immutable raw-data manifest;
- a venue-transfer plan, because the paper studies Binance while this project executes on OKX.

OHLCV candles, quote volume, or candle direction are not accepted as substitutes for signed order
flow. A one-minute candle cannot establish the paper's first-10-second mechanism.

## Readiness result

The local OKX archive has nine contracts and 43,300 unique one-minute candles per contract. Their
common intersection contains 43,258 minutes from 2026-08-03 22:34 through 2026-09-02 23:32 UTC,
covering 31 touched days but only **28 complete 1,440-minute days**. Each source candle has nine OKX
OHLCV fields; there are no trade-event timestamps, aggressor-side labels, or individual sizes.

**Verdict: STOPPED_DATA_GATE.** Zero trades, zero return inspection, and zero strategy trial. Do not
test candle direction or one-minute volume as an order-imbalance proxy under this experiment ID.
Reopen only with the exact trade-tape schema and minimum history above.
