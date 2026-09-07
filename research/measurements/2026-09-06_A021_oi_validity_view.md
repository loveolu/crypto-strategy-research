# A-021: chronological OI validity view

Date: 2026-09-06. Offline data preparation only; zero strategy configurations evaluated.

The fixed three-year archive now has a separate chronological view for a 24-hour OI difference.
It uses all calendar timestamps in [2023-09-01, 2026-09-01), not a selected favorable interval.
Each valid window requires 289 consecutive five-minute observations (both endpoints plus the
288-step interval), with finite positive OI and OI value throughout. The computed change is in
**open interest**, not price, equity or profit.

## Observed eligibility

| Calendar block | Grid rows | Valid 24h windows | Invalid or warm-up |
|---|---:|---:|---:|
| 2023 September-December | 35,136 | 33,394 | 1,742 |
| 2024 | 105,408 | 102,489 | 2,919 |
| 2025 | 105,120 | 103,063 | 2,057 |
| 2026 January-August | 69,984 | 69,693 | 291 |
| Total | 315,648 | 308,639 | 7,009 |

There are 315,512 source rows, 136 absent timestamps and 341 present rows with invalid OI.
Absent timestamps have explicit `record_present=False` and missing measurements. Zero/negative/
nonfinite OI or OI value invalidates the full lookback, not merely its endpoints. Missing windows
have a missing `oi_change`, never a synthetic zero return. No measurement was interpolated or
forward/backward-filled. Source archive and original row number are retained for present records.
The previously unsorted source files remain byte-identical; only the derived view is sorted.

Source timestamps remain naive labels. **No live availability timestamp is supplied.** The output
is not approved for execution-time joins until timezone, interval labeling, publication delay and
historical revision risk are resolved. A focused public-source search did not resolve those archive
semantics; third-party conventions are not promoted to authoritative exchange specifications.

## Verification

Implementation: `user_data/research/a021_oi_validity_view.py`.
Tests: `user_data/research/test_a021_oi_validity_view.py`.

Thirteen new tests failed before implementation and passed afterward. They cover full warm-up,
invalid interior observations/endpoints, zero OI value, missing timestamps, recovery only after the
whole lookback is valid, sorting invariance, future-data invariance, duplicate/off-grid/out-of-range/
timezone-aware timestamp rejection, and entirely missing input. All 30 combined A-021 tests pass;
two pre-existing unknown asyncio-option warnings remain in the local pytest environment.

An independent prefix-sum calculation, using the saved Parquet without importing the implementation,
reproduced the complete validity mask. Every valid OI change matches endpoint arithmetic exactly;
all 7,009 excluded changes remain missing. A second actual CLI run reproduced the result with no
derived-file hash changes. All 4,391 raw-directory files still match their committed Git blob IDs.

The loader reads the census manifest directly from source commit `b03e93705` and validates every
archive SHA-256 against that manifest before parsing. Census SHA-256:
`4ed6030f0f80930e00b173b7f38bcc67067ff58d390a9ce8b54846a520c4c3a6`.

Outputs are isolated in `user_data/research/data/binance_metrics_a021_derived/`:

- `oi_24h_validity.parquet`, SHA-256
  `ac6d494c86417a28678f6e0af4114a026f433cfe7ee1150a603eb5370ee739f5`.
- `eligibility_report.json`: scope, source identity, quality counts and unresolved timing flags.

Reproduce without network or raw-data modification:

```powershell
python user_data/research/a021_oi_validity_view.py
```

The existing output is compared, not overwritten. This data-preparation result is not a strategy
promotion, evidence of profitability, or resolution of historical selection-count uncertainty.
Next: establish the timing contract for an executable OI predictor, then preregister one narrow
market hypothesis, chronological validation and full cost/delay assumptions before reading outcomes.
