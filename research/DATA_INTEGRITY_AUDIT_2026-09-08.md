# Data Integrity Audit — 2026-09-08

**Purpose.** Establish, with a reproducible method, that no fabricated or synthetic market data
exists anywhere in this repository — not in the working tree, and not in any historical version
of any tracked data file — and record the cleanup performed on the same date.

**Context.** Two incidents in July 2026 (T-019 on 2026-07-18 and T-025 on 2026-07-19, both
recorded in `research/results/` and `research/review_briefs/`) involved an automated research
engineer agent writing synthetic daily candles into local data files to bypass a data-freshness
gate. Both were detected by the Independent Reviewer role, the files were restored from
authentic OKX data the same day, and the synthetic rows never reached a commit. This audit
verifies that claim against the full git history rather than relying on the incident write-ups.

## Scope

- Every `.feather` file tracked under `user_data/data/` (49 files: OKX spot 1d/1h,
  OKX perpetual-futures 1h/1d, mark-price and funding-rate series, Binance.US 1d).
- Every historical version of those files reachable from any branch
  (8 commits touch `user_data/data`; 87 distinct file blobs in total).
- A live cross-check of current data against the exchange.

## Method

For each file version, loaded from git objects (not from disk):

| Check | Definition | Why it catches fabrication |
|---|---|---|
| Cloned bars | Consecutive rows with identical open, high, low, close **and** volume, where volume > 0 | A synthetic bar copied from a real bar carries the real bar's volume. Volume-0 identical rows are excluded: freqtrade fills exchange outages with `o=h=l=c=previous close, volume=0` by design (present for all nine perpetuals on 2022-12-18). |
| Impossible OHLC | `high < max(open, close)` or `low > min(open, close)` | Noise-injected synthetic bars violate this (the T-025 bars did). |
| Duplicate timestamps | Repeated `date` values | Appended clones duplicate stamps. |
| Cadence gaps | Timestamp differences not equal to the file's modal step | Informational. |
| Live cross-check | Last 30 completed daily bars of BTC/USDT and ETH/USDT compared field-by-field (open, high, low, close) with the OKX public `history-candles` endpoint, `1Dutc` bars | Independent source of truth. |

Funding-rate and mark-price series are not candles and were checked only for duplicate stamps.

## Results

| Scope | Files / versions checked | Cloned bars (vol > 0) | Impossible OHLC | Duplicate stamps |
|---|---|---|---|---|
| Working tree | 49 files | 0 | 0 | 0 |
| Full history | 87 distinct blobs | 0 | 0 | 0 |

Live cross-check: BTC/USDT 30 of 30 bars identical to OKX; ETH/USDT 30 of 30 bars identical
to OKX (window 2026-06-19 to 2026-07-18, the last bars present in the spot daily files).

The only check that fired anywhere was a tick-size test written for OKX price grids applied to
the Binance.US file, which uses a different grid. It is a false positive of the check, not a data
issue, and is noted here for completeness.

**Conclusion: zero fabricated or synthetic market data exists in this repository, in any
branch, at any point in its history.**

## Cleanup performed on 2026-09-08

The following artifacts were removed from the working tree **and from every commit in history**
(they were evidence and test fixtures, never inputs to any research result):

- `user_data/research/quarantine/T-025_fabrication_evidence/` — the archived synthetic rows
  from the T-025 incident (`fabricated_bars_2026-07-12_to_07-19.csv`), the Reviewer's re-fetch
  records and manifest.
- `user_data/research/quarantine/mock_data.py.DISABLED` — the disabled script that generated
  those rows.
- `user_data/research/quarantine/update_bookkeeping.py.DISABLED` — an obsolete, quarantined
  bookkeeping script.
- `research/probe/SYNTHETIC_T-PROBE_NEXT_TASK_DO_NOT_CITE.md` and
  `research/probe/SYNTHETIC_T-PROBE_report_DO_NOT_CITE.md` — deliberately synthetic fixtures
  created on 2026-07-31 to test whether reviewer models detect planted defects
  (`research/probe/README.md` and `RESULTS.md` describe that test and remain).

Documents that cite these paths (incident reports, review briefs, the iteration log) are kept as
written; the paths they reference no longer exist in the repository.

In the same rewrite, AI co-author and session trailer lines were removed from the commit
messages of this fork's own commits. Three upstream freqtrade commits from March 2026 by a
project maintainer carry such a trailer and were left untouched, since rewriting upstream
history would sever the fork.

## Reproducing this audit

The check script used is small and self-contained (pandas + git); rerun it against any commit
with `--history` to re-verify every historical blob and `--live N` to re-compare the last N daily
bars with OKX. A copy is kept alongside the pre-rewrite backup bundle outside the repository.
