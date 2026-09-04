# Research queue — ranked by Potential Edge × Credibility × Information Gain ÷ Complexity (2026-09-04, post EXP-011)

**Standing rule: no further variants of S2 on the 2023→2026 data.** ~40 constructs have been examined
on it; the next in-sample "improvement" is noise by construction. Items 1–2 generate NEW evidence.

1. **Forward paper-trade S2-strict-4h-9** (freqtrade IStrategy port; dry-run bot is up). The leader
   after EXP-009/010. Decides decay vs regime — the only open question this data cannot answer.
   **Execution requirement from EXP-010: act at the 4h candle close; the edge is gone by 8h.** Record
   theoretical vs simulated fill, slippage, latency, forward expectancy vs TRAIN (+150 bps/trade).
   *Promotion gate: rolling 90d PF > 1 for two consecutive quarters.* Complexity: medium (port).
2. **Decay monitor** on S2-strict-4h-9: rolling 90d PF, expectancy, win rate vs TRAIN; flag
   **Degraded** if PF < 1 two quarters running. Cheap; runs alongside 1.
3. ~~2h and 8h bracket~~ **DONE — EXP-011**: all four resolutions OOS-positive (Sh 0.83/1.02/1.31/0.85);
   4h is a stable region with the smallest TRAIN→OOS gap.
4. **Funding as a regime feature** for the gate (6 months of 1h funding held, growing): does extreme
   funding predict the cascade-reversion hit rate? Forward-heavy; wait for 12 months of funding.
5. **Open-interest drop as the liquidation trigger** (OKX rubik; untested bank card) — replaces the
   dsd/mom proxy with the thing it proxies. Needs an A-XXX data fetch first.
6. **Walk-forward with re-fit** on the stable region (W 134–202, HOLD 16–32) — does per-window
   re-selection beat fixed params OOS? Medium; low expected gain given the region is flat.

Closed, do not re-queue without new reason: majors/alts rotation; regime-switch S2/V5; daily/weekly
rebalance; S2 short mirror; S2 gate-timing variants (EXP-008); S1 ungated; all T-038/039/040 families.
