# OKX market-structure recorder launch — 2026-09-04

Status: **ACTIVE / DATA COLLECTION ONLY**. No trading hypothesis was evaluated.

- Universe: BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT, LINK.
- Metrics: daily aggregate open interest + contract volume, account long/short
  ratio, and taker buy/sell volume from public OKX Rubik endpoints.
- Initial collection: 27/27 series successful, 0 failures, 179 finalized rows per
  series (4,833 rows total).
- Retained range: 2026-03-09 16:00 UTC through 2026-09-03 16:00 UTC. The 16:00 UTC
  alignment is supplied by OKX's daily bars; it was measured, not relabeled.
- Incomplete-bar policy: timestamps on or after the current UTC day are withheld.
- Integrity: timestamps sorted/unique, numeric metric fields finite, currency and
  source URL populated, overlap values immutable, response SHA-256 logged.
- Immediate manual rerun: 27/27 successful, zero new rows, all 27 CSV hashes
  unchanged.
- Scheduled task: `FreqtradeMarketStructureRecorder`, daily 03:30 local time;
  forced verification run completed with result 0 and zero duplicate rows.

The approximately six-month history is insufficient for a credible multi-regime
liquidation-trigger backtest. Accumulate forward without inspecting feature efficacy;
revisit at 12 months minimum, preferably after the sample includes materially different
volatility regimes. This recorder is separate from and did not modify the existing
funding recorder or either dry-run trading bot.
