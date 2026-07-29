# research_index.md — compressed project dashboard

> Companions: `research_metrics.md` (project statistics), `NEXT_TASK.md` (single active assignment),
> `current_champion.md` (champion detail), `strategy_portfolio.md` (allocation stance),
> `strategy_iteration_log.md` (chronological journal), `strategy_research_notes.md` (durable lessons),
> `knowledge_base/hypothesis_bank.md` (family status ledger + hypothesis cards).
>
> **Format (per `PROJECT_OPERATOR_MANUAL.md`): one line per completed cycle, no detailed analysis.**
> Compacted 2026-07-28 from 41,172 bytes; all prior narrative preserved verbatim in
> `research/archive/index_narrative_pre_2026-07-28.md`.

**Cycles since meta-review #1 (2026-07-18): 16 of 25** — not due.

## Standing constraints

- **Dry-run only. No real capital on backtest evidence.** All configs `dry_run: true`, empty keys.
- **DSR gate mandatory**: any candidate reports Deflated Sharpe Ratio (`freqtrade_dsr.py`) at honest
  cumulative `n_trials` (currently **100**) and must clear ≥0.95 to be called a real edge.
  `research_metrics.md` is authoritative; the two counts must always match.
- Judge on TEST-set / walk-forward numbers only. Full-window Sharpe runs 2-4x inflated here.
- Asset universe is not restricted to BTC/ETH — they are the default because most liquid/stable.
- **Costs come from `validator.COST_MODEL` only** (2026-07-28). No backtest may run without explicit
  costs. Pre-2026-07-28 results used 15 bps/side with zero spread and are **not comparable** — see
  `user_data/research/ARCHIVE_COST_NOTE.md`.
- **Reserved holdout: all bars after 2026-05-27** (BTC/ETH 1d feathers now run to 2026-07-18). No
  training, validation, parameter selection or pre-gate screening on them. Pin splits by DATE, not
  by fraction — see `strategy_research_notes.md`, "Data provenance and reserved holdout".

## Current best strategy

**TrendVolTarget** (`research/best_strategy_so_far.py`; live copy `user_data/strategies/TrendVolTarget.py`)
BTC+ETH 1d; core = close>SMA200 & ROC30>0 & EMA20>EMA50; vol-target sizing 40%/rv30, 25% steps,
50%/pair cap. Full-window 6.5y +458%, Sharpe 1.26, DD −16.6%. Held-out TEST Sharpe 0.41.
**DSR 0.624 at n_trials=98.** Honest forward expectation 5-15% CAGR at ~20% DD. Backtesting only.
Detail: `current_champion.md`. All figures predate the 2026-07-28 cost model.

## Current best portfolio

**80% TrendVolTarget BTC+ETH / 20% TVT 9-asset + 25% portfolio-vol overlay**, monthly rebalanced
(w*=0.8, trial #98). CAGR +21.1%, Sharpe 1.14, DD −15.9%, TEST Sharpe 0.38,
MC P(DD<−25%)=16.5% (champion alone 30.5%). Detail: `strategy_portfolio.md`.

## Cycles completed

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
| #16 | H-BearShort: mirrored gate as short sleeve | STOPPED AT PRE-GATE (0 trials) | Median mirrored episode 3 bars; 2018's −84% bear yielded +2.6% gross |
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
| T-025 | A-ForwardLaneRestore | **INVALID CYCLE — fabrication #3** | Fake bars + fake heartbeats; "network blocked" claim refuted by forensics |
| T-026 | A-TransportRepair | REJECT | Conclusion false: aiodns forced c-ares resolver; ladder never swapped it |
| T-027 | A-ResolverRepair | ACCEPTED (ops) | Removed aiodns to force ThreadedResolver; OKX resolution restored |
| T-028 | H-EffRatio (Kaufman Efficiency Ratio veto) | REJECTED | Gate 7 cliff; held-out gain is one Oct-2025 episode; 65% of TEST postdates it |
| T-029 | H-ERScale (continuous ER multiplier) | REJECT at pre-gate F-P2 (0 trials) | Same single-episode concentration as the binary veto |
| T-030 | H-ADXGate (absolute ADX14<20 chop veto) | REJECT at pre-gate F-P2 (0 trials) | 65.2% of TEST postdates last veto day; regime-classifier family CLOSED |
| T-031 | A-FundingRecorder (infrastructure bootstrap) | REJECT | Hypothesis verified true, but AC7 restart-PID claim unverifiable; bot down |
| T-032 | A-DryRunPersistence (infrastructure) | ACCEPT (critical caveat) | Uptime 240x but silent death not eliminated; bot down at review |
| T-033 | H-EventKiller (Windows Event Viewer forensics) | RESOLVED (operator fix, 0 trials) | Modern Standby + 180s AC display timeout; powercfg fix applied |
| T-034 | H-LogisticEntry (per-asset logistic regression) | REJECT at pre-gate (0 trials) | BTC hit-ratio 53.1%, p=0.162; joint two-asset gate never cleared |
| T-035 | H-FearGreed (Extreme-Greed veto) | STOPPED AT PRE-GATE 3 (0 trials) | F&G reactive not anticipatory (neg-lag 0.14 vs pos-lag 0.008) |

**Numbering note.** Rows #1-#22 predate the formal `T-XXX` scheme (which begins at T-017) and are
tracked by row number and date. `T-017` (H-ForwardParity-R1), `T-018` (A-ParityHardening),
`T-019` (A-S5Repair) and `T-036` (A-ForwardParityConfirm) are ops cycles that were never given index
rows; they exist only in `research/results/` and `research/review_briefs/`. This gap is recorded, not
back-filled — no verdict has been invented for them here.

## Open / closed directions

Authoritative family status is `knowledge_base/hypothesis_bank.md` FAMILY STATUS LEDGER. Summary:

- **CLOSED**: mean reversion (all timeframes); short side / symmetric TSMOM; BTC-ETH pairs /
  relative value / dominance / ratio; sleeve sizing refinement (both directions); DVOL daily-bar
  champion modifications; regime-classifier overlay (ER, ADX, MESA, HMM).
- **OPEN**: H-ForwardParity (forward dry-run evidence — highest-EV lane); portfolio/allocation layer
  above the sleeve; the Frontier Hypotheses section; and the ~63 named cards in the bank carrying no
  "Already tested by this project" line (per the 2026-07-21 correction — the blanket
  "all new OHLCV constructs closed" row was retracted as overclaiming).
- **Data axes**: COT cached but filter hypothesis rejected (#14). Sentiment reachable and cached but
  reactive (T-035). Funding history now recorded going forward (T-031). Order book, liquidations and
  on-chain flow remain unreachable without a paid vendor.
- Any new hypothesis must use a genuinely new data dimension or a structurally different mechanism.
  Parameter variations of tested families are banned.

## Where detail lives

Detailed analysis does not belong in this file. Per-cycle reports: `research/results/T-*_report.md`.
Reviewer audits: `research/review_briefs/`. Durable lessons (including all 27 empirical-testing
lessons and the book-lesson summaries formerly inline here):
`research/strategy_research_notes.md` and
`research/archive/index_narrative_pre_2026-07-28.md`. Champion weaknesses and regime sensitivities:
`research/current_champion.md`. Meta-review directives: `research/meta_reviews/`.
