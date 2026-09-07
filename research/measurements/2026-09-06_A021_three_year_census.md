# A-021: three-year BTCUSDT positioning archive census

Date: 2026-09-06. Fixed interval: [2023-09-01, 2026-09-01). Data operations only.

## Result

All 1,096 daily ZIPs and their exchange checksums were retrieved or reused from the frozen sample
set. Every checksum matched and every CSV parsed: 315,512 observed records out of 315,648 expected
five-minute timestamps. No duplicate timestamps were found. There are 136 missing slots:

| Date | Missing five-minute slots |
|---|---:|
| 2023-09-12 | 3 |
| 2024-02-16 | 125 |
| 2024-10-28 | 2 |
| 2025-08-29 | 3 |
| 2026-08-12 | 3 |

107 files have non-increasing physical row order. Twelve have recognized nulls in ratio fields:
72 `count_toptrader_long_short_ratio`, 46 `sum_toptrader_long_short_ratio`, and 37
`count_long_short_ratio` values. OI, OI value and taker ratio have no recognized null tokens.
All files have the same eight column names as the initial samples.

The saved scanner reports 973 days satisfying its combined grid/null/physical-order check and a
236-day longest run under that strict definition. **This is not a claim that the other 123 days
have no usable data.** Ignoring physical row order, the longest complete timestamp-grid/all-fields
run is 347 days, 2025-08-30 through 2026-08-11. Sorting a separate derived table is legitimate;
silently filling missing observations or modifying the raw CSV is not.

## Critical numeric hazard

An independent pass through the raw ZIPs using CSV and Decimal reproduced 315,512 rows. It found
no negative numeric values or nonfinite values beyond the null tokens above, **but 341 rows have
zero OI and zero OI value**. These occur on 18 days:

| Date | Zero-OI rows |
|---|---:|
| 2023-11-11 | 1 |
| 2023-11-20 | 6 |
| 2023-11-23 | 2 |
| 2023-11-26 | 2 |
| 2024-07-09 | 6 |
| 2024-07-10 | 41 |
| 2024-07-11 | 46 |
| 2024-07-12 | 43 |
| 2024-07-13 | 52 |
| 2024-07-14 | 85 |
| 2024-07-15 | 26 |
| 2024-08-12 | 6 |
| 2025-01-08 | 4 |
| 2025-01-28 | 1 |
| 2025-03-06 | 1 |
| 2025-04-11 | 4 |
| 2025-04-15 | 5 |
| 2025-07-21 | 10 |

These zeros are not certified economic observations. A naive percentage-change feature would read
them as total position collapse and can create false liquidation signals. Before any OI hypothesis,
require positive finite OI at both endpoints and valid observations throughout its required lookback;
explicitly mask affected windows in a derived view. Do not substitute tiny positive values,
interpolate, forward-fill across outages, or call the zeros actual forced selling. The scanner's
`complete_days` is a timestamp/null/order measure and does not test this numeric hazard.

## Timing and external context

870 objects have Last-Modified dates more than seven days after their nominal archive date. This
does not prove which numeric values changed, but it prevents treating current checksums as proof
of the historical real-time vintage. Raw `create_time` timezone, interval semantics and publication
latency remain unresolved. No execution/funding join or outcome calculation was performed.

A firsthand [data-quality report in Binance's issue tracker](https://github.com/binance/binance-public-data/issues/484)
describes missing/duplicate records in earlier downloaded vintages. It is a user's report, not a
Binance-maintainer confirmation. Two of its reported missing intervals match the present local
checks; other reported defects are not copied into this census because current local evidence
governs. The [older OI-frequency issue](https://github.com/binance/binance-public-data/issues/211)
does not provide authoritative release-latency semantics in the retrieved text.

## Reproducibility and scope

`user_data/research/a021_binance_metrics_census.py` uses the tested raw-preservation/checksum
helpers. It records every requested day, including failures, and uses at most four workers.
The first five census tests failed before implementation; the corrupt-ZIP regression failed before
its exception handler was added. All 17 combined probe/census tests now pass (two existing
environment asyncio-option warnings). No strategy modules are imported.

Raw new artifacts and `census_inspection.json` are in
`user_data/research/data/binance_metrics_a021/history_20230901_20260901/`. Four overlapping days
reuse the already committed sample directory. The derived report preserves per-day schemas,
hashes, quality measures and last ten raw records. A full actual-CLI offline replay exited 0 and
left all 4,369 files in the history directory byte-identical under before/after SHA-256 checks.

```powershell
python user_data/research/a021_binance_metrics_census.py --offline
```

The original sample evidence is in `f09e8d4ed`; the three-year extension needs its own scoped
versioning operation. No frozen OKX market data, other-agent recorder, strategy or B2 setting was
changed. Zero strategy configurations were evaluated and no return or leaderboard claim follows.

## Next decision

Historical availability is substantially improved: the full fixed three-year archive is now held.
It is not gap-free, and demanding an entirely pristine year would discard a mostly present dataset.
Proceed to a tested chronological derived view with explicit missing/zero-OI validity masks and
source timing validation. Preserve all raw data and all calendar periods; do not choose a favorable
subset after seeing returns. Only then preregister a narrow OI hypothesis and its costed validation.
Existing selection accounting and promotion gates remain in force.
