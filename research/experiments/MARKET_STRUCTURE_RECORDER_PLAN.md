# OKX market-structure forward recorder plan

Created 2026-09-04 PDT to support a future liquidation-trigger experiment. This is
data collection, not a trading experiment and not evidence of an edge.

## Scope

Collect once daily for BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT and LINK from three
public OKX Rubik endpoints at `period=1D`:

- contracts/open-interest-volume: timestamp, open-interest USD, volume USD;
- contracts/long-short-account-ratio: timestamp, account long/short ratio;
- taker-volume with `instType=CONTRACTS`: timestamp, taker-buy and taker-sell USD.

The initial run stores all currently returned history (approximately 180 days). Later
runs merge by metric/currency/timestamp. Existing values are immutable: a changed
overlap fails loudly rather than silently rewriting history. Every row records fetch
time and source URL, and every request adds an audit-log record with HTTP/API status,
row count and response SHA-256. Writes use a same-directory temporary file followed
by atomic replacement.

## Operations and acceptance

The recorder is isolated under `user_data/research/data/market_structure/` and a new
Windows scheduled task runs it daily. It does not modify the funding recorder or any
trading bot. Acceptance requires parser/merge tests, a successful live collection for
all 27 currency/metric combinations, unique sorted timestamps, non-empty numeric
fields, source provenance, a clean immediate idempotence rerun, and a successful
scheduled-task invocation. Retention depth is measured rather than assumed.
