# CRYPTO-EXP-CX-001 — dispersion-conditioned cross-sectional reversal

**Verdict: REJECT at the TRAIN-only zero-cost pre-gate. Zero trials spent.** The interaction had
the wrong sign before costs, so no validation, OOS inspection, parameter variation, or promotion
test was run.

## Pre-registration and implementation

The design was frozen in `research/experiments/EXP_CX_001_DESIGN.md` before the first data run.
Implementation: `user_data/research/exp_cx_001_dispersion_reversal.py`; behavior tests:
`user_data/research/test_exp_cx_001_dispersion_reversal.py`.

The single cell used all nine OKX USDT perps at 1h. At a causal high-dispersion onset (current
cross-sectional dispersion in 24h momentum above the 80th percentile of the prior 720 hours), it
went long the two worst and short the two best 24h performers, gross 1.0/net 0.0, entered two bars
after signal close, held 24 hours, and charged A-011 measured per-instrument taker costs both ways.
Signals were separated by a 24-bar cooldown.

## Data and boundary

- Common panel: 32,418 hourly bars, 2022-12-23 06:00 through 2026-09-03 23:00 UTC.
- Pre-gate: TRAIN only, signals through 2024-11-22 23:00 UTC.
- Fully executable TRAIN events: **237**, exceeding the pre-registered floor of 50.
- No market-data file was created, modified, downloaded, or rebuilt.
- The OOS and spent-forward portions were loaded to construct the common panel but were not used in
  any threshold, gate, result, or selection decision. The circular-shift null was confined to TRAIN.

## Pre-gate results

| gate | required | observed | result |
|---|---:|---:|---|
| Event count | >= 50 | **237** | PASS |
| Mean gross / realized round-trip cost | >= 2.0x | **-1.457x** | **FAIL** |
| Positive signed instrument contributions | >= 5 of 9 | **3 of 9** | **FAIL** |
| Circular-shift placebo, one-tailed | p <= 0.05 | **p = 0.9850** | **FAIL** |

Mean event return was **-0.19799% gross (-19.80 bps)** and **-0.33389% net (-33.39 bps)**.
Mean realized round-trip cost was **0.13589% (13.59 bps)**. The 1,000-draw placebo distribution
(seed 20260904) had a 95th-percentile mean gross return of **+0.14723% (+14.72 bps)**. Thus the real
alignment was worse than 98.5% of null alignments in the hypothesized reversal direction.

## Interpretation

High cross-sectional dispersion does not rescue the 24h momentum-reversal cell left open by T-039.
On TRAIN it selects continuation, not convergence: recent winners continued to beat recent losers.
This is stronger than an after-cost rejection because the direction is already wrong before fees.

The result closes only this exact interaction: 24h cross-sectional momentum, trailing-dispersion
top-quintile onset, two-versus-two reversal, and 24h holding on the nine-perp panel. It does not
close all variable interactions, alternative targets, or different horizons. Reversing the trade
direction after seeing this result would be a new selected hypothesis and is not performed here.

## Raw artifacts

- `research/results/EXP-CX-001_raw/pregate_summary.json`
- `research/results/EXP-CX-001_raw/train_trades.csv`
- `research/results/EXP-CX-001_raw/placebo_means.csv`
- `research/results/EXP-CX-001_raw/event_series.csv`
