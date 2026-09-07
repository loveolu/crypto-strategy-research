# A-021: historical Binance metrics archive reachability

Date: 2026-09-05. Status: five HEAD probes succeeded; acquisition and schema/coverage validation remain pending.
This is an operations evidence note, not a strategy experiment or completed data acquisition.

## Finding

Five exact BTCUSDT daily metrics ZIP paths returned HTTP 200 from this machine: 2023-01-01,
2024-01-01, 2025-01-01, 2025-08-01 and 2026-08-01. Reported byte lengths are respectively
14,337 / 11,521 / 11,213 / 11,353 / 11,044. Selected headers and the probe timestamp are preserved
in `A021_binance_metrics_reachability.json`. No ZIP body was requested or processed.
The initial sandbox socket error was local access denial, not an exchange geoblock; the required
network-escalated retry succeeded. This does not establish trading-API access or trading eligibility.

This changes the next action: investigate the archive before treating limited REST history or
the short local OKX record as proof that historical positioning data cannot be obtained. It does
not prove that the ZIPs contain open interest, that intervening dates exist, or that measurements
are comparable to OKX.

## Primary-source context and timing risks

Binance's [public-data repository](https://github.com/binance/binance-public-data) links the archive,
describes daily/monthly publishing, provides checksum verification, and warns that archived files
can be revised. Its README does not document the metrics ZIP schema. The
[collection directory](https://data.binance.vision/?prefix=data/futures/um/daily/metrics/BTCUSDT/)
exposed no listing rows in the web reader; the successful evidence is the terminal HEAD requests.
Web-reader attempts to open two CHECKSUM URLs failed; no checksum contents were verified.

The [Open Interest Statistics API documentation](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data)
limits that REST endpoint to the latest month and describes total OI, total OI value, and an
end-of-period timestamp. These are API definitions, not a verified archive-column mapping.

The 2025-01-01 file reports Last-Modified 2026-07-24, and the 2025-08-01 file reports 2026-08-04.
These show later object modification, not what changed or whether numeric values changed.
Any eventual historical test must disclose retrospective data vintages; current checksums cannot
prove today's contents were available at the original trading time.

## Next evidence required

1. Assign an isolated A-021 acquisition scope before downloading bodies. Keep frozen
   `user_data/data/`, the other agent's recorders and active strategy files untouched.
2. Preserve raw ZIPs and checksums under a new research-axis directory before parsing; refuse
   overwrite, record URLs/fetch times/hashes, and retain raw artifacts in the project-required
   versioned record. This HEAD-only note does not discharge acquisition requirements.
3. Inspect real columns, units, nulls, timestamp grid, symbol identity, last ten raw records,
   and row counts. Check old and recent files for schema changes.
4. Census daily availability and common coverage with execution/funding inputs over a fixed recent
   two-to-three-year span. Require at least one usable year; do not interpolate gaps. Binance
   predictors with OKX execution require an explicit cross-venue design, not silent substitution.
5. Resolve release latency and revision risk before a point-in-time claim. OI changes alone are
   not authenticated liquidation flow and do not reopen closed cascade pre-filter hypotheses.
6. Only after the data gate, preregister a narrow hypothesis, chronological splits and cost/delay
   cases before opening outcome returns. Selection-count uncertainty and promotion gates remain.

No new return, Sharpe, ranking, strategy selection or deployment claim was produced. Existing B2
settings and all raw market-data files were unchanged by this check.
