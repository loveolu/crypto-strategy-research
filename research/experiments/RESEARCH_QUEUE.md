# Research queue — ranked by Potential Edge × Credibility × Information Gain ÷ Complexity (2026-09-04, post EXP-008)

**Standing rule: no further variants of S2 on the 2023→2026 data.** ~40 constructs have been examined
on it; the next in-sample "improvement" is noise by construction. Items 1–2 generate NEW evidence.

1. **Forward paper-trade S2-strict-9** (freqtrade IStrategy port; dry-run bot is up). Decides decay vs
   regime — the only question left that matters and the only one this data cannot answer. Record
   theoretical vs simulated fill, slippage, latency, forward expectancy vs TRAIN baseline (+149 bps).
   *Promotion gate: rolling 90d PF > 1 for two consecutive quarters.* Complexity: medium (port).
2. **Decay monitor** on S2-strict-9: rolling 90d PF, expectancy, win rate vs TRAIN; flag **Degraded**
   if PF < 1 two quarters running. Cheap; runs alongside 1.
3. **4h cascade variant** (goal timeframe survey): same mechanism at 4h resolution — untested, cheap,
   and h ≥ 12 is the cost-viable region anyway. Pre-register on TRAIN, evaluate OOS once.
4. **Funding as a regime feature** for the gate (6 months of 1h funding held, growing): does extreme
   funding predict the cascade-reversion hit rate? Forward-heavy; wait for 12 months of funding.
5. **Open-interest drop as the liquidation trigger** (OKX rubik; untested bank card) — replaces the
   dsd/mom proxy with the thing it proxies. Needs an A-XXX data fetch first.
6. **Walk-forward with re-fit** on the stable region (W 134–202, HOLD 16–32) — does per-window
   re-selection beat fixed params OOS? Medium; low expected gain given the region is flat.

Closed, do not re-queue without new reason: majors/alts rotation; regime-switch S2/V5; daily/weekly
rebalance; S2 short mirror; S2 gate-timing variants (EXP-008); S1 ungated; all T-038/039/040 families.
