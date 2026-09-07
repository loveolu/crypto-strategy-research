# A-021: verified sample contents, not continuous historical coverage

Date: 2026-09-06. Operations evidence only; zero strategy configurations evaluated.

## What changed

The five HEAD-only samples now have preserved ZIP bodies, accompanying exchange CHECKSUM files,
and HTTP metadata. All five SHA-256 digests match their published checksums. The raw path is
`user_data/research/data/binance_metrics_a021/`; the derived `sample_inspection.json` includes
each archive/checksum hash, row count, schema and last ten raw records. Metadata sidecars retain
URLs, fetch times, status, complete response headers and raw-body hashes. Nothing was written to
`user_data/data/`, the OKX recorders or B2 strategy/configuration files.

The dates are 2023-01-01, 2024-01-01, 2025-01-01, 2025-08-01 and 2026-08-01. Each contains 288
records from 00:00 through 23:55 on a five-minute grid: 1,440 rows total. No missing five-minute
slots, duplicate timestamps, non-increasing steps or recognized null tokens occur in these samples.
An independent CSV/Decimal pass also checks 8,640 numeric values: all are finite and positive.
This is a sample-quality result, not a claim that every field is economically correct.

All five files have the same eight column names:

- `create_time`, `symbol`
- `sum_open_interest`, `sum_open_interest_value`
- `count_toptrader_long_short_ratio`, `sum_toptrader_long_short_ratio`
- `count_long_short_ratio`, `sum_taker_long_short_vol_ratio`

The columns confirm that the archive contains OI and positioning fields, not just price candles.
Units, population definitions and publication latency still need authoritative validation. Numeric
formatting differs across vintages; identical column names do not prove unchanged methodology.

## Reproduction and safety checks

Implementation: `user_data/research/a021_binance_metrics_probe.py`.
Tests: `user_data/research/test_a021_binance_metrics_probe.py`.

Eleven tests failed at the missing-implementation assertion before code was added; after
implementation all eleven passed. Coverage includes immutable cache reuse without network,
modified/orphan cache rejection, preservation of HTTP error bodies, checksum digest and filename,
timestamp gaps/duplicates/nulls, wrong symbol/day/grid/schema, and unsafe ZIP member rejection.
The ZIP is inspected in memory and never extracted to the filesystem.

Use a unique, nonexistent workspace `--basetemp` for pytest: the default external pytest temp
directory is inaccessible in this sandbox. Run with `-o addopts='' -p no:cacheprovider`; this
environment reports two pre-existing unknown asyncio-option warnings.

The network invocation succeeded after the required sandbox escalation. An offline invocation
through the actual CLI then exited 0, reproduced the saved report and left all 21 files byte-identical
under before/after SHA-256 checks. An earlier verification command piped stdout into
`Select-Object -First 5`, which terminated the producer early (exit -1); that was not counted as a
successful replay. Capturing all stdout before displaying its first five lines resolved it.

Reproduce without network:

```powershell
python user_data/research/a021_binance_metrics_probe.py --offline
```

## Unresolved gates and next action

Versioning follow-up: commit `f09e8d4ede694187df9ab627c813084ddd4a3ce2` preserves the sample
archives, checksums, metadata, inspection, probe and tests. All 22 files in the committed raw
directory (including its byte-preserving `.gitattributes`) were compared directly with Git blobs:
zero byte mismatches. The sample versioning requirement is discharged. This does not certify the
subsequent three-year acquisition, which needs its own versioned record.

Five separated days cannot prove a continuous year. The next data operation is a fixed recent
coverage census and immutable acquisition, not a strategy return calculation. Also unresolved:

- `create_time` is naive in the files. UTC, interval-end versus interval-start, and actual release
  latency require confirmation before joining execution quotes.
- Two sampled 2025 objects were last modified in 2026. Checksums authenticate today's download,
  not the historical real-time vintage; they cannot remove revision look-ahead risk.
- No historical execution/funding alignment, cross-venue transfer or untouched outcome split has
  been established. Do not treat OI changes as authenticated forced-liquidation events.
- The prior selection-count uncertainty, family closures, realistic costs and promotion gates
  remain unchanged. This evidence does not support a new leaderboard entry or benchmark victory.
