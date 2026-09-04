# Research queue — ranked by Potential Edge × Credibility × Information Gain ÷ Complexity (2026-09-05, post EXP-015)

**Standing rule: no further variants of the cascade family on 2023→2026 data.** ≈ 50 constructs examined.

1. **Port B2 to a freqtrade IStrategy and paper-trade it** (Candidate → Paper Trading). Execute at the
   4h close (edge gone by 8h). Log theoretical vs simulated fill, slippage, latency, forward expectancy
   vs backtest (+149 bps/trade, WR 63%). Gate to next stage: rolling 90d PF > 1, two consecutive quarters.
2. **Decay monitor** on B2 forward: rolling 90d PF / expectancy / WR vs backtest; **Degraded** if PF < 1
   two quarters running.
3. **Record OI, long-short ratio and taker-volume daily** (A-XXX ops; OKX rubik, ~6 mo retention) so a
   liquidation-trigger variant is testable in a year. Same pattern as the funding recorder.
4. **Funding as gate feature** — revisit at 12 months held (currently 6; the n=10 look was suggestive).
5. **Second, uncorrelated mechanism.** The only non-cascade constructs tested (V5 spread, vol-expansion,
   S3 daily) are negative, bull-beta, or out of scope. The book is one edge. Candidates with a real
   hypothesis and a 3-year backtest available: BTC-leads-alts *lag* trade (alt reversion after BTC
   reversion, cross-asset, untested). Intraday seasonality is CLOSED; funding / OI need data.

Closed, do not re-queue without new reason: V5 as hedge; vol-expansion ignition; majors/alts rotation;
regime-switch; rebalance-freq; S2 short mirror; S2 gate-timing variants; S1 ungated; T-038/039/040 families.
