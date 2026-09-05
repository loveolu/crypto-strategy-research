# CRYPTO-EXP-031 design — order-book imbalance data-sufficiency gate

Date: 2026-09-04 PDT. This is a zero-trial data audit, not a parameter search.

## Hypothesis

Persistent imbalance between bid and ask depth in a liquid perpetual order book
may predict the next few minutes of returns strongly enough to clear taker costs.
Unlike EXP-028 and EXP-030, this mechanism requires actual order-book state rather
than inferring order flow from OHLCV.

## Gate before any signal or return calculation

- Source: immutable `okx_micro/book_samples.jsonl`, nine OKX USDT perpetuals.
- Each observation must have a unique instrument/sequence identifier and both bid
  and ask depth.
- Require at least 30 complete UTC days and at least 1,000 snapshots per instrument.
- Require observations spanning at least 20 distinct UTC days. Dense polling over
  a few minutes does not count as independent history.
- If any condition fails, stop without defining an imbalance threshold, horizon,
  direction, trade, or examining forward returns. The hypothesis remains untested.

If this gate eventually passes on forward data, a new experiment must freeze its
TRAIN/validation/TEST split and economic gates before calculating returns. This
audit cannot be retroactively converted into a trading trial.
