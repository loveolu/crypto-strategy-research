# Archive — spot program cycle rows (2026-05-14 → 2026-07-29)

The 38 completed cycles of the **OHLCV / spot program**, moved out of
`research/research_index.md` on 2026-07-29 by operator decision. **The rows below are the complete,
unaltered originals** — verified byte-for-byte against the live index at the time of the move.

The index resets at a program boundary for the same reason `n_trials` does: these results were
measured on a different instrument at a different cost model, and none of them is a perps baseline.
See `research/review_briefs/T-037_PERPS_TRANSITION_brief.md` for what carries forward and what is
void, and `user_data/research/ARCHIVE_COST_NOTE.md` for the cost discontinuity.

Task IDs do **not** reset — the sequence continues at T-038. Only the index table and `n_trials`
reset.

**Numbering note.** Rows #1-#22 predate the `T-XXX` scheme (which begins at T-017). T-017, T-018 and
T-019 are ops cycles that were never given index rows; that gap is recorded, not back-filled, and no
verdict was invented for them — see A-001 in `research/OPS_BACKLOG.md`.

Final spot-program RESEARCH:OPS ratio was **0.73 : 1** (8 research / 11 ops) — see
`research/research_metrics.md`.

---

## Cycles completed — spot program (final, frozen)

| Task ID | Hypothesis | Verdict | Primary reason |
|---|---|---|---|
| #1 | EMA/RSI/volume 1h trend (+9 variants) | FAIL | IS +6% → OOS negative; classic overfit |
| #2 | Pullback / mean-rev / breakout-retest / Donchian / Bollinger (1h) | FAIL | All collapse OOS or in-sample |
| #3 | TTM squeeze breakout / band fade (1h) | FAIL | Negative even in-sample; winners < losers structurally |
| #4 | Funding-rate squeeze | BLOCKED | Funding history unobtainable then (OKX ~3mo; others geo-blocked) |
| #5 | Spot-perp basis proxy | FAIL | Basis is noise on OKX (±0.07%) |
| #6 | Overnight / time-of-day breakout (Zarattini-style) | FAIL | 5-10 trades in 3-5y; N below statistical floor |
| #7 | SMA200 regime overlay (RiskManagedBetaOverlay) | FAIL | +362% was 2020-21 beta; WF OOS 2.77% CAGR on 37.6% DD |
| #8 | 61-strategy autonomous search (5 batches) | FAIL (0/61) | Sharpe ceiling ~1.2 on retail OHLCV; fee drag kills HF variants |
| #9 | **TrendVolTarget (ens3 core + vol-target sizing)** | **BEST — unproven** | Only construct with clearly positive OOS; DSR 0.64 < 0.95 bar |
| #10 | TVT expansions (9-asset, hybrid, portfolio-vol) | PARTIAL | Full-window gains are train artifacts; 9-asset kept as defensive variant |
| #11 | Blending / dual momentum / halving / calendar / x-sect / long-short | FAIL | Correlations too high; narratives don't survive data; DD blowups |
| #12 | Intraday hours 21-22 UTC anomaly | REAL BUT UNTRADEABLE | t=2.4-3.0 stable; fees exceeded edge 25:1 at the old cost model |
| #13 | Supertrend / Chandelier / BTC-dominance / ETH-BTC z-fade (6 Forven ideas) | FAIL | All dominated by champion on TEST/MC |
| #14 | H-COT: CFTC asset-manager crowding filter (trial #96) | FAIL | Zero TEST-split activity; in-sample harmful; DSR 0.603 |
| #15 | H-RangeVol: Garman-Klass 30d sizing estimator (trial #97) | FAIL | MC tail 30.5→22.9% missed ≤20% bar; TEST Sharpe 0.39→0.02 |
| #16 | H-BearShort: mirrored gate as short sleeve | STOPPED AT PRE-GATE (0 trials) | Median episode 3 bars; 2018's −84% bear yielded +2.6% gross |
| #17 | A-ValidatorAudit: Kaufman Ch.21 diagnostics + champion re-audit | AUDIT CLEAN (0 trials) | Both downgrade triggers negative; WF boundary-stable |
| #18 | H-CointPair: BTC-ETH cointegration pairs | STOPPED AT PRE-GATE 1 (0 trials) | Not cointegrated on any window; post-2024 break formal (ADF p 0.405) |
| #19 | H-SizingBand: rebalance granularity / no-trade band | STOPPED AT PRE-GATE A (0 trials) | Continuous bound gave +3.0pp of required ≥5.0pp; TEST Sharpe −0.12 |
| #20 | H-TailAlloc: champion/defensive allocation (trial #98) | **PORTFOLIO PROMOTION at w\*=0.8** | MC tail 30.5→16.5%; TEST Sharpe 0.38; DSR 0.6423 ≥ 0.6245@98 |
| #21 | H-IVGate: Deribit DVOL crisis veto | CLOSED AT PRE-GATE B3a (0 trials) | Only 4 in-market spike episodes < 6 floor; all one macro period |
| #22 | H-IVSizing: max(rv30, DVOL/100) sizing | CLOSED AT PRE-GATE P2 (0 trials) | High-DVOL days are BETTER (VRP positive-carry); zero TEST diff days |
| T-021 | F-4: Regime-Gated Pairs Revival | STOPPED AT PRE-GATE (0 trials) | Rolling cointegration passed 3/15 windows vs ≥60% bar |
| T-022 | DVOL Acceleration (change-based sizing/gate) | STOPPED AT PRE-GATE (0 trials) | Failed TEST episode + harm census; DVOL axis exhausted |
| T-023 | Forward Parity Monitor Rebuild | **INVALID CYCLE** | Engineer fabricated candle data to bypass the AC3 authenticity check |
| T-024 | Dynamic Volatility-Stabilized Portfolio (dynamic-w) | REJECTED | Discrete trial #99 degraded TEST Sharpe −0.05; DSR 0.6879 < 0.95 |
| T-025 | A-ForwardLaneRestore | **INVALID CYCLE — fabrication #3** | Fake bars + heartbeats; "network blocked" claim refuted by forensics |
| T-026 | A-TransportRepair | REJECT | Conclusion false: aiodns forced c-ares resolver; ladder never swapped it |
| T-027 | A-ResolverRepair | ACCEPTED (ops) | Removed aiodns to force ThreadedResolver; OKX resolution restored |
| T-028 | H-EffRatio (Kaufman Efficiency Ratio veto) | REJECTED | Gate 7 cliff; held-out gain is one Oct-2025 episode; 65% of TEST postdates it |
| T-029 | H-ERScale (continuous ER multiplier) | REJECT at pre-gate F-P2 (0 trials) | Same single-episode concentration as the binary veto |
| T-030 | H-ADXGate (absolute ADX14<20 chop veto) | REJECT at pre-gate F-P2 (0 trials) | 65.2% of TEST postdates last veto day; regime-classifier family CLOSED |
| T-031 | A-FundingRecorder (infrastructure) | REJECT | Hypothesis verified true; AC7 restart-PID claim unverifiable, bot down |
| T-032 | A-DryRunPersistence (infrastructure) | ACCEPT (critical caveat) | Uptime 240x but silent death not eliminated; bot down at review |
| T-033 | H-EventKiller (Windows Event Viewer forensics) | RESOLVED (operator fix, 0 trials) | Modern Standby + 180s AC display timeout; powercfg fix applied |
| T-034 | H-LogisticEntry (per-asset logistic regression) | REJECT at pre-gate (0 trials) | BTC hit-ratio 53.1%, p=0.162; joint two-asset gate never cleared |
| T-035 | H-FearGreed (Extreme-Greed veto) | STOPPED AT PRE-GATE 3 (0 trials) | F&G reactive not anticipatory (neg-lag 0.14 vs pos-lag 0.008) |
| T-036 | A-ForwardParityConfirm (ops) | **TERMINATED BY OPERATOR, 2026-07-29** (0 trials) | Champion took zero trades in dry run; parity reconciles trivially every bar, so the instrument cannot produce evidence |
