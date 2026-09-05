# CRYPTO-EXP-032 — Market-structure archive readiness gate

## Hypothesis

The retained OKX daily open-interest, positioning, and taker-flow archive may now contain enough
complete, aligned history to support a chronological multi-regime feature test.

## Pre-registered zero-trial gate

- Required universe: nine currencies × three metrics = 27 series.
- Required history: at least 365 timestamps common to every series.
- Integrity: no missing series, duplicate timestamps, missing daily intervals, or non-daily spacing.
- This audit reads timestamps and identifiers only. It does **not** inspect feature values, returns,
  correlations, thresholds, or efficacy. Failure therefore spends zero research trials and preserves
  the future feature test.

## Result (2026-09-04)

- 27/27 series present.
- Every series has 179 unique daily observations.
- Common range: 2026-03-09 16:00 UTC through 2026-09-03 16:00 UTC.
- Zero duplicates, gaps, and non-daily intervals.
- Common complete days: **179 / 365 required**.

## Verdict

**STOPPED — DATA NOT READY.** The archive is structurally clean but 186 common days short of the
minimum. No feature values or forward returns were examined; zero trades and zero trials. Continue
immutable daily collection and rerun the same gate. Earliest eligibility is approximately 2027-03-08
if continuity is maintained; eligibility is based on the observed count, not that forecast date.

Machine-readable evidence: `research/measurements/EXP032/summary.json`.
Reproducible audit: `user_data/research/market_structure_readiness.py`.
