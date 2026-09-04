# Research queue — ranked by Potential Edge × Credibility × Information Gain ÷ Complexity (2026-09-05, post EXP-015)

**Standing rule: no further variants of the cascade family on 2023→2026 data.** ≈ 50 constructs examined.

1. **Monitor the live B2 forward-paper stream** (launched 2026-09-04 13:55 PDT; isolated dry-run DB,
   log and keepalive verified). Compare theoretical vs simulated fill, slippage, latency and forward
   expectancy with the frozen backtest (+149 bps/trade, WR 63%). Current status: **COLLECTING**.
   Review gate: rolling 90d PF > 1 for two consecutive quarters; **Degraded** if PF < 1 twice running.
2. **Monitor OI / long-short / taker-volume collection** (launched 2026-09-04; 27/27 OKX Rubik
   series, 179 finalized daily rows each, scheduled daily at 03:30). Do not inspect feature efficacy
   until at least 12 months are retained; the current ~6 months cannot support a multi-regime test.
3. **Funding as gate feature** — revisit at 12 months held (currently 6; the n=10 look was suggestive).
4. **Second, uncorrelated mechanism.** The non-cascade constructs tested (V5 spread, vol-expansion,
   S3 daily, and BTC-rebound/lagging-alt catch-up) are negative, bull-beta, or out of scope. The book
   remains one edge. Require a genuinely new hypothesis; intraday seasonality and simple OHLCV
   lead/lag are CLOSED, while funding / OI need forward data.

Closed, do not re-queue without new reason: V5 as hedge; vol-expansion ignition; majors/alts rotation;
regime-switch; rebalance-freq; S2 short mirror; S2 gate-timing variants; S1 ungated; T-038/039/040 families;
EXP-016 BTC-shock/rebound lagging-alt catch-up (TRAIN-positive, gross-negative in every held-out segment).
