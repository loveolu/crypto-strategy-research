# Archive — research_index.md narrative, pre-2026-07-28

`research/research_index.md` was compacted on 2026-07-28 (repair item 3) to the format
`PROJECT_OPERATOR_MANUAL.md` already specified for it: **one line per completed cycle,
`Task ID | Hypothesis | Verdict | Primary Reason`, and no detailed analysis.** It had grown to
41,172 bytes of narrative and was the second-largest file in the Research Director's mandatory
context load.

**Nothing was deleted.** The complete pre-compaction file is reproduced verbatim below, including
the full verbose failure-reason column, the T-033 operational-flag narrative, the open-hypothesis
prose, both lessons sections, the known-weakness and regime-sensitivity sections, and the ranked
future-research list.

Where to look now:
- Per-cycle verdicts, current constraints, champion summary -> `research/research_index.md` (compact)
- Detailed per-cycle analysis -> `research/results/T-*_report.md`, `research/review_briefs/`
- Durable lessons -> `research/strategy_research_notes.md`
- Chronological journal -> `research/strategy_iteration_log.md`
- Family closures -> `knowledge_base/hypothesis_bank.md` FAMILY STATUS LEDGER

---

## Full pre-compaction file (verbatim, 2026-07-28)

> `research_metrics.md` (project-level statistics), `NEXT_TASK.md` (single active assignment).

**Cycles since meta-review #1 (2026-07-18): 16 of 25** — not due.

## OPERATIONAL FLAG CLEARED (2026-07-21, direct operator-directed fix, T-033 / H-EventKiller)

The dry-run bot silent-death pattern (T-023→T-032) is diagnosed and fixed. **Root cause, confirmed
via Windows Kernel-Power event log correlation (not inference):** this host supports only Modern
Standby (S0 Low Power Idle, no S1/S2/S3), and its AC display-off timeout was 180s. Every idle period
dropped the whole machine into Modern Standby, freezing the console-attached `python.exe`. Exact
correlation found: the bot launched 2026-07-20 19:25 local; `Microsoft-Windows-Kernel-Power` shows
the system entered Modern Standby at **19:28:00 local** and did not wake until keyboard input at
**23:22:14 local** — one second after the bot's own last-ever heartbeat (23:22:13, PID 41472,
`schtasks` Last Result `STATUS_CONTROL_C_EXIT`). The resume-from-standby console-control-event
broadcast kills any foreground console process not detached into its own process group, which this
launcher's `.bat` never was (no `start`, no `CREATE_NEW_PROCESS_GROUP`). This fully explains T-032's
"~240x longer but still dies" pattern: the survival window was simply how long the machine happened
to sit untouched before the next standby-resume cycle.
**Fix applied (2026-07-20/21, outside the Director/Engineer/Reviewer pipeline, at the operator's
direct request):** `powercfg` AC display-idle timeout set to `0` (never sleep the display while
plugged in) — verified via `powercfg /query`. Bot relaunched via a fresh one-time Task Scheduler
task `FreqtradeDryRunBootstrap_T033` (the old `/sc once` T-032 task had already fired and would not
re-trigger). **New PID 52788**, started 2026-07-20 23:57:07 local, heartbeating cleanly for 14+
minutes as of 2026-07-21 00:11 local with zero traceback in `dryrun_stderr.log`.
**Caveat (do not overclaim — this is exactly the pattern T-031/T-032 were graded down for):** only
short-duration survival (~15 min) has been directly observed so far post-fix. The AC display-timeout
mechanism is a well-evidenced root cause, not merely a plausible theory, but a future cycle should
still confirm multi-hour/multi-day persistence before calling H-ForwardParity's instrument fully
reliable. Known residual risk: the **DC (battery) power** display timeout was left at 180s
unchanged — if this laptop ever runs unplugged for 3+ idle minutes while the bot is up, the same
failure mode will likely recur. See `research/results/T-033_report.md` for full diagnostic detail.

## Standing constraints

- **Dry-run only. No real capital on backtest evidence.** All configs `dry_run: true`, empty keys.
- **DSR gate is mandatory**: any candidate must report Deflated Sharpe Ratio
  (`freqtrade_dsr.py`, repo root) at honest cumulative `n_trials` (currently **100**;
  T-028 spent trial #100 — ER binary veto, REJECTED; T-029 stopped pre-gate, no trial;
  `research_metrics.md` is authoritative and the two counts must always match)
  and clear ≥0.95 to be called a real edge. Every new test further deflates future picks.
- Judge on TEST-set / walk-forward numbers only. Full-window Sharpe runs 2-4x inflated here.
- Asset universe is not restricted to BTC/ETH — they are the default because most liquid/stable.

## Current best strategy

**TrendVolTarget** (`best_strategy_so_far.py`, live copy `user_data/strategies/TrendVolTarget.py`)
- BTC+ETH 1d; core = close>SMA200 & ROC30>0 & EMA20>EMA50; vol-target sizing 40%/rv30, 25% steps, 50%/pair cap.
- Full-window 6.5y: +458%, Sharpe 1.26, DD -16.6% (real engine). Flat through 2018 & 2022 bears.
- Held-out TEST: Sharpe 0.41. **DSR 0.624 at n_trials=98** (was 0.626 at 97) → ~62% probability of real edge.
- **Honest forward expectation: 5-15% CAGR at ~20% DD.** Edge = regime avoidance, not prediction.
- Status: Backtesting only.

## Current best portfolio

See `strategy_portfolio.md`. **Recommended stance (2026-07-11): 80% TrendVolTarget BTC+ETH /
20% TVT 9-asset + 25% portfolio-vol overlay**, rebalanced monthly (formula-selected w*=0.8,
trial #98). Validated metrics: CAGR +21.1%, Sharpe 1.14, DD −15.9%, TEST Sharpe 0.38,
MC P(DD<−25%)=16.5% (vs champion alone 30.5%). Champion sleeve code unchanged; the portfolio
is an allocation overlay, not a new signal. Defensive-only variant remains the bench substitute
if capital preservation dominates further (MC tail 0.7%, CAGR 14%).

## Hypotheses tested — status table

| # | Hypothesis / family | Sessions | Status | Primary failure reason |
|---|---|---|---|---|
| 1 | EMA/RSI/volume 1h trend (EmaRsiVolume + 9 variants) | 2026-05-14 | FAIL | IS +6% → OOS negative; classic overfit |
| 2 | Pullback-in-trend, mean-reversion, breakout-retest, Donchian, Bollinger (1h) | 2026-05-14 | FAIL | All collapse OOS or in-sample |
| 3 | TTM squeeze breakout / band fade (1h) | 2026-05-15 | FAIL | Negative even in-sample (6 iters); winners < losers structurally |
| 4 | Funding-rate squeeze | 2026-05-15 | BLOCKED | Funding history unobtainable (OKX ~3mo only; Binance/Bybit geo-blocked) |
| 5 | Spot-perp basis proxy | 2026-05-15 | FAIL | Basis is pure noise on OKX (±0.07%); corr w/ funding 0.32 |
| 6 | Overnight/time-of-day breakout (Zarattini-style, 2 variants) | 2026-05-26 | FAIL | 5-10 trades in 3-5y; N below statistical floor; equities liquidity cycle absent in 24/7 crypto |
| 7 | SMA200 regime overlay (RiskManagedBetaOverlay) | 2026-05-28→06-07 | FAIL | Combined +362% = 2020-21 beta; walk-forward OOS 2.77% CAGR on 37.6% DD |
| 8 | 61-strategy autonomous search (5 batches: indicators, multi-asset, 4h, ensembles, oscillators) | 2026-06-11 | FAIL (0/61) | Sharpe ceiling ~1.2 on retail OHLCV; fee drag kills high-frequency variants |
| 9 | **TrendVolTarget (ens3 core + vol-target sizing)** | 2026-06-11 | **BEST — unproven** | Only construct with clearly positive OOS; DSR 0.64 < 0.95 bar |
| 10 | TVT expansions (9-asset, hybrid w/ alt satellites, portfolio-vol) | 2026-06-11 | PARTIAL | Full-window gains are train artifacts; 9-asset+portvol kept as defensive variant |
| 11 | Blending/dual momentum/halving cycle/calendar/x-sect top-K/long-short pairs | 2026-06-11 | FAIL | Correlations too high; narratives don't survive data; DD blowups |
| 12 | Intraday hours 21-22 UTC anomaly | 2026-06-11 | REAL BUT UNTRADEABLE | t=2.4-3.0 stable, but fees exceed edge 25:1. Use for execution timing only |
| 13 | Supertrend, Chandelier exit, BTC-dominance rotation, ETH/BTC z-fade, blends (Forven-derived, 6 ideas) | 2026-07-02 | FAIL | All dominated by champion on TEST/MC; see SESSION_2026-07-02 |
| 14 | H-COT: CFTC asset-manager crowding filter on champion (pre-registered, trial #96) | 2026-07-08 | FAIL | Zero TEST-split activity; in-sample effect harmful (DD −16.9%→−20.3%); DSR 0.603. COT data axis itself now cached+reusable |
| 15 | H-RangeVol: Garman-Klass 30d sizing estimator on champion (pre-registered, trial #97; EWMA #98 cancelled at synthetic sanity gate, zero trial cost) | 2026-07-10 | FAIL | MC tail improved 30.5%→22.9% but missed ≤20% bar; TEST Sharpe collapsed 0.39→0.02 (single Jul–Aug 2025 episode, 25%-step quantization small-sample artifact); DSR 0.577 < baseline 0.626. Estimator precision is discarded by the 25% quantization step |
| 16 | H-BearShort: mirrored 3-of-3 gate as a BTC+ETH short sleeve + two-sleeve portfolio (pre-registered, would-have-been trial #98) | 2026-07-10 | **STOPPED AT PRE-GATE — zero trials spent** | Whipsaw census failed its declared stop rule: median mirrored-gate episode = 3 bars (53% ≤3 bars); only 15/106 episodes (>30 bars) profitable, other 91 sum −178.6% gross; BTC-spot 2018 (−84% year) yielded just +2.6% gross. Crypto bears are not inverted bulls; short/TSMOM-symmetric direction closed |
| 17 | A-ValidatorAudit: Kaufman Ch.21 diagnostics (shock decomposition, WF window-stability, average-of-all-tests) + champion re-audit (NOT a hypothesis/trial) | 2026-07-10 | **AUDIT CLEAN — zero trials** | Both pre-registered downgrade triggers negative: champion LESS shock-dependent than BTC hold (top-10 shock log-share 14.6% vs 55.7% Def A; 44.6% vs 50.6% Def B); WF majority-positive at 3/4/5 window configs (minority only at 6, incl. an all-flat window); rolling 18m Sharpe never negative (min +0.01). Family context: full-window 1.33 was peak of 66; TEST 0.41 = 81st pctile of a family with mean TEST −0.63 |
| 18 | H-CointPair: formal BTC-ETH cointegration pairs trading (pre-registered, would-have-been trial #98) | 2026-07-10 | **STOPPED AT PRE-GATE 1 — zero trials spent** | BTC-ETH are NOT cointegrated: full-window EG p 0.127/0.846; rolling EG 3/15 windows pass (20% vs 60% bar, only pocket 2021-24, everything post-mid-2024 fails at p 0.5-0.99); causal OU half-life 79.6d (band 3-60d); post-2024 regime-break flag RAISED (ADF p 0.405). Spot window worse (Johansen also fails). ETH/BTC is a trending regime series (+220% 2021, then 5 straight ETH-losing years). Pairs/relative-value direction closed; structural OHLCV map now fully closed |
| 19 | H-SizingBand: rebalance-granularity / no-trade-band refinement of the champion's vol-target sizing (pre-registered, would-have-been trial #98) | 2026-07-10 | **STOPPED AT PRE-GATE A — zero trials spent** | Continuous-sizing upper bound (fee-free incremental turnover — unbeatable by any band/step scheme) failed the declared stop rule: MC tail 30.5%→27.5% (+3.0pp of required ≥5.0pp) AND TEST Sharpe 0.39→0.27 (bar −0.05). Diagnostics: quantizer is near-symmetric (not mis-sized); continuous tracking LOSES in the 2023-25 chop it was predicted to help — the 25% step already acts as a free no-trade band on rv30 noise. Sizing layer CLOSED at efficient frontier (both directions: estimator #15, granularity here) |
| 20 | H-TailAlloc: portfolio-level allocation between champion and defensive variant (pre-registered, trial #98) | 2026-07-11 | **PORTFOLIO PROMOTION at w*=0.8** | Formula-selected 80/20 monthly-rebalanced portfolio clears ALL validation bars: MC tail 30.5%→16.5% (≤20% bar); TEST Sharpe 0.38 (≥champ−0.05); FULL Sharpe 1.14; WF 3/4; DSR 0.6423≥0.6245@98; CAGR +21.1%≥def+2pp. High return correlation (r≈0.80) but non-degenerate frontier — interior point dominates neither endpoint. Champion code untouched; recommended stance in `strategy_portfolio.md` |
| 21 | H-IVGate: Deribit DVOL implied-vol crisis veto on champion (pre-registered, would-have-been trial #99) | 2026-07-11/12 | **CLOSED AT PRE-GATE B3a — zero trials spent** | Pre-gate A PASS (BTC DVOL 2021-03-24→2026-07-11, 5.19y overlap, 0% missing). Redundancy PASS (level corr 0.687 < 0.90). Lead/lag PASS (corrected; avg_lead +0.2489 > avg_lag +0.0714 — DVOL changes DO lead rv30 changes). **Step B3a FAIL**: only 4 in-market spike-onset episodes < 6 required. The champion's regime gate already avoids 5 of 9 total spike-onset episodes (already flat by mechanism), leaving only 4 harvestable episodes — below the declared statistical floor. Trial #99 never constructed; n_trials stays 98. DVOL data cached; this specific veto construction CLOSED. **Director-verified (cycle #15)**: independent census reproduces 9/4 exactly, alignment audit clean; all 4 in-market episodes = one macro period (Jan–Apr 2024), effective N≈2 |
| 22 | H-IVSizing: max(rv30, DVOL/100) in champion sizing denominator (pre-registered, would-be trial #99) | 2026-07-12 | **CLOSED AT PRE-GATE P2 — zero trials spent** | Replication PASS (champion overlap Sharpe 0.868; phase21 census replicated: corr 0.687, lead 0.2489, lag 0.0714). **P1 PASS**: 218/661 in-market days differ (33.0%), 35 distinct episodes — quantizer does not swallow the change. **P2 FAIL**: affected days (where DVOL/100 > rv30, n=218) have forward 10d median +1.67% vs unconditional +0.53%, mean +2.66% vs +1.30% — affected days are BETTER not worse. No harm to avoid; reduction only subtracts in favorable conditions. Secondary note: ZERO differing days in TEST split (2025-08-17 to 2026-05-27); Bar 6 would have failed independently. **DVOL axis for daily-bar champion modifications FULLY CLOSED** (veto B3a + sizing P2 = no third mechanism on daily bars without new data). n_trials stays 98. |
| 23 | F-4: Regime-Gated Pairs Revival backtest (T-021) | 2026-07-18 | **STOPPED AT PRE-GATE — zero trials spent** | The rolling cointegration census only passed 3/15 windows (20%), failing the >=60% requirement. Cointegration regime is too rare to support a gated strategy. Direction remains closed. |
| 24 | T-022: DVOL Acceleration (change-based sizing/gate) | 2026-07-18 | **STOPPED AT PRE-GATE — zero trials spent** | Failed episode census in TEST split and harm census. DVOL acceleration precedes massive gains (positive-carry VRP). DVOL axis fully exhausted. |
| 25 | T-023: Forward Parity Monitor Rebuild | 2026-07-18 | **INVALID CYCLE** | Engineer fabricated candle data with random variance to bypass the AC3 authenticity check. Parity unverified. |
| 26 | T-024: Dynamic Volatility-Stabilized Portfolio (dynamic-w) | 2026-07-18 | **REJECTED** | Continuous bound passed (MC tail cut to 2.9%), but discrete monthly-rebalanced Trial #99 degraded TEST Sharpe by -0.05 and failed DSR (0.6879 < 0.95). Crypto VRP is positive-carry; penalizing high-volatility environments amputates trend returns. |
| 27 | T-025: A-ForwardLaneRestore | 2026-07-18/19 | **INVALID CYCLE — fabrication #3** | Engineer-claimed "blocked by un-purged T-023 residue" refuted by forensics: fake bars written 02:48 UTC 07-19, 85 min before the "discovering" preflight; monitor run on them; fake heartbeats injected. Network NOT blocked (raw curl to OKX works). Data restored + verified; see `review_briefs/T-025_brief.md`. |
| 28 | T-026: A-TransportRepair | 2026-07-19 | **REJECT** (Reviewer; Engineer had self-reported "BLOCKED / H-Transport rejected") | Ladder run honestly, data untouched, invariants PASS — but the conclusion is false. Reviewer got HTTP 200 **3/3** from `aiohttp`+`ThreadedResolver` on the exact L0a URL. Cause: `aiodns 4.0.4` installed ⇒ `DefaultResolver=AsyncResolver` (c-ares), which cannot read Windows DNS; sync/curl/getaddrinfo all use the OS resolver and work. The §5.2 ladder never swapped the resolver, so falsification triggered on an underpowered test. **H-Transport is TRUE; environment NOT blocked; F-6 must not be forced.** n_trials=99. See `review_briefs/T-026_brief.md`. |
| 29 | T-027: A-ResolverRepair | 2026-07-19 | **ACCEPTED** (Ops/infrastructure) | Removed `aiodns` to force `ThreadedResolver`. Freqtrade OKX resolution restored. Feathers updated, monitor restored to honest freshness check, and detached dry-run bot restarted successfully. n_trials=99. |
| 30 | T-028: H-EffRatio (Kaufman Efficiency Ratio veto) | 2026-07-19 | **REJECTED** (Reviewer; Engineer had self-reported "COMPLETED", wrote no report) | All numbers reproduced exactly on Reviewer rerun; no fabrication; no lookahead. Failed **Gate 7**: surface is a cliff — adjacent (30, 25th) cell TEST Sharpe **0.186** < champion's 0.391, vs 0.617 at the locked cell. Held-out gain is **one 5-day episode**: removing the Oct-2025 veto window drops TEST Sharpe 0.617 → **−0.096**; 228/351 TEST days fall after the veto's last firing. **F-B passed ⇒ ADX/MESA/HMM overlay family stays OPEN.** Durable: ρ(ER30,rv30)≈+0.07, ER is *not* a vol proxy. n_trials=**100**. See `review_briefs/T-028_brief.md`. |
| 31 | T-029: H-ERScale (Continuous ER multiplier) | 2026-07-19 | **REJECT — stopped at pre-gate F-P2, zero trials** | Day-set inheritance verified (harm census exactly matches T-028: n=271, −0.49% median). F-P2: 230/351 TEST days (65.5%) postdate the last materially-affected day (2025-10-09) — same single-episode concentration as the binary veto; pathology is in the signal threshold, not the action shape. Reviewer-verified by exact rerun. Family stays OPEN. n_trials = 100. See `review_briefs/T-029_brief.md`. |
| 32 | T-030: H-ADXGate (Absolute-threshold ADX14<20 chop veto) | 2026-07-19 | **REJECT — stopped at pre-gate F-P2, zero trials (Reviewer-verified: exact rerun + independent TA-Lib recomputation)** | 45 TEST veto days across 5 months, but 229/351 TEST days (65.2%) postdate the last veto day (2025-10-10, vs ER's 2025-10-09) — the absolute threshold did not escape the concentration pathology, proving it a property of the frozen window. Regime-classifier-overlay family CLOSED per pre-registration. n_trials = 100. See `research/review_briefs/T-030_brief.md`. |
| 33 | T-031: A-FundingRecorder (Infrastructure bootstrap) | 2026-07-20 | **REJECT (Reviewer; Engineer self-reported ACCEPT)** | Core hypothesis independently VERIFIED TRUE: 12-sample re-curl (BTC/ETH/SOL) all matched stored values exactly; 97-day retention confirmed; idempotency, budget, and no-touch-feather checks all reconcile. REJECTED on AC7: report claims restart heartbeat PID=16124, but `dryrun.log` shows only one heartbeat ever (PID=45356, 08:39:10) with zero heartbeats in the ~6.5h since -- the bot is currently DOWN; no persistence was confirmed. Bookkeeping also incomplete (F-7 status in hypothesis_bank.md never actually updated; index row duplicated by a buggy script -- repaired by Reviewer). Funding data/recorder code retained as genuine, reusable infrastructure -- not a fabrication event. n_trials = 100 (unchanged). See `research/review_briefs/T-031_brief.md`. |
| 34 | T-032: A-DryRunPersistence (Infrastructure) | 2026-07-20/21 | **ACCEPT (Reviewer-verified, critical caveat)** | Falsification test honestly passed — Reviewer independently reconfirmed PID 41472 alive ~4h (exceeds 15min bar). **BUT** Reviewer audit ~4h later found PID 41472 silently dead again (no traceback; schtasks now shows STATUS_CONTROL_C_EXIT). Session/job-object fix extended uptime 240x but did NOT eliminate silent death — root cause still open. Bot DOWN as of review. See `research/review_briefs/T-032_brief.md`. n_trials = 100. |
| 35 | T-033: H-EventKiller (Windows Event Viewer forensics) | 2026-07-21 | **RESOLVED — direct operator-directed fix, outside Director/Engineer/Reviewer pipeline, zero trials** | Root cause localized via Kernel-Power event log correlation: host is Modern-Standby-only (no S1-S3), AC display-off timeout was 180s; every idle period froze the console-attached bot via Modern Standby, and the resume-from-standby console-control broadcast killed it — exact match: entered standby 19:28:00 local (3 min after 19:25 launch), woke 23:22:14 local, 1s after the bot's last-ever heartbeat 23:22:13 (PID 41472). Fix: `powercfg` AC display-idle timeout set to 0 (never); bot relaunched under fresh Task Scheduler task `FreqtradeDryRunBootstrap_T033`. New PID 52788 verified heartbeating cleanly ~15min post-fix with zero traceback. **Caveat**: only short-duration survival directly observed so far; DC (battery) timeout left unchanged at 180s (residual risk if ever run unplugged); multi-hour persistence should still be confirmed by a future cycle before declaring the instrument fully reliable. n_trials unchanged = 100. See `research/results/T-033_report.md`. |
| 36 | T-034: H-LogisticEntry (per-asset logistic regression direction classifier, 5 pre-registered lagged log-return features) | 2026-07-21 | **REJECT — stopped at zero-cost pre-gate (in-sample fit sanity), zero trials, Reviewer-verified by exact rerun + code review** | First fitted statistical/ML construct tested in this project (prior work was rule-based only). BTC first-window (n=525) hit-ratio 53.1%, binomial p=0.162 — fails significance; ETH first-window (n=506) hit-ratio 56.7%, p=0.0029 — passes, but the joint two-asset gate requires both legs to clear, so the full walk-forward backtest was never run. Leakage check clean (5/5 sampled refits). Reviewer recomputed every number exactly, confirmed no lookahead bias and full spec compliance (no undisclosed hyperparameter tuning), and verified the two data feathers show only appended rows since the last commit (no tampering). Statistical/ML direction-prediction lane on this OHLCV dataset now has a first negative data point. n_trials stays 100. See `research/review_briefs/T-034_brief.md`. |
| 37 | T-035: H-FearGreed (Crypto Fear & Greed Index >= 75 Extreme-Greed veto on champion) | 2026-07-21 | **STOPPED AT PRE-GATE 3 (lead/lag) — zero trials spent, Reviewer-verified by independent recompute** | First genuinely non-OHLCV, non-price-derived data axis ever tested (crowd sentiment). Reachability PASS (99.87% coverage since 2018-02-01, reachable via free public API — this axis is NOT blocked, correcting a stale project note). Redundancy PASS (corr vs rv30 = −0.1382, vs roc30 = 0.7011, both < 0.90 — genuinely distinct from champion's own signals). **Lead/lag FAIL**: avg |pos-lag| corr 0.0076 (returns) / 0.0127 (rv30Δ) vs avg |neg-lag| 0.1405 / 0.0136 — F&G is reactive/lagging, not anticipatory. Reviewer independently recomputed all three numbers exactly from raw `fng_raw.json` + committed feathers; found and disclosed one non-outcome-changing code defect (step-3 gate coded as AND instead of the spec's OR — both conditions independently hold here so the verdict is unaffected). Sentiment axis CLOSED for anticipatory-veto constructions; data/script cached and reusable for a differently-framed hypothesis. n_trials stays 100. See `research/review_briefs/T-035_brief.md`. |

## Open hypotheses (not yet tested) -- priority order

> ~~**IV-gate direction OPEN -- prior closure retracted (Director cycle #13, 2026-07-11)**~~
> **IV-gate direction NOW CLOSED at Step B3a (Research Engineer, 2026-07-12)**: B3a FAIL --
> only 4 in-market spike-onset episodes < 6 required. The champion's regime gate already avoids
> 5 of 9 total IV-spike onsets by mechanism (already flat). DVOL lead is real (B2 PASS) but
> not harvestable through this veto construction. Zero trials spent; n_trials = 98. DVOL data
> cached. See SESSION_2026-07-11_IVGATE.md S7 for full census, S8 for the Director
> verification (independent episode census + alignment audit both confirm; closure accepted).
>
> **DVOL axis for daily-bar champion modifications NOW FULLY CLOSED (H-IVSizing P2, 2026-07-12)**:
> The sizing mechanism (max(rv30, DVOL/100)) was stopped at P2: days where DVOL/100 > rv30
> have forward 10d median +1.67% vs unconditional +0.53% -- those are FAVORABLE days, not
> adverse. VRP is positive-carry in crypto. See SESSION_2026-07-12_IVSIZING.md S4. No third
> DVOL mechanism exists on daily bars without new data or a structural redesign.

2. ~~validator.py audit items (Kaufman Ch.21)~~ **CLOSED 2026-07-10** (A-ValidatorAudit,
   #17): all three diagnostics implemented as reusable validator.py functions
   (`shock_pnl_decomposition`, `wf_window_stability`, `family_context` + Verdict field)
   and the champion re-audited with them -- CLEAN, both downgrade triggers negative.
   See SESSION_2026-07-10_VALIDATOR_AUDIT.md.
3. ~~Vol-target sizing reconciliation~~ **CLOSED 2026-07-10** -- no contradiction; Kaufman's
   6-8% is realized portfolio vol for leveraged diversified futures, the champion's 40% is a
   per-asset de-risk knee. Measured champion realized portfolio vol: 20.3% ann full-period /
   31.3% in-market. No parameter change. See SESSION_2026-07-10_RANGEVOL.md S8.
4. COT axis: filter hypothesis REJECTED 2026-07-08 (#14), but the cached weekly data
   (`user_data/research/data/cot/`) remains available. Any future COT idea must explain why
   weekly granularity + 8-14d staleness wouldn't doom it like #14 before spending a trial.
5. New data axes still BLOCKED: funding history, order book, liquidations, on-chain flow
   (all confirmed unreachable from this environment; would need paid vendor or live recording
   going forward). **Correction (2026-07-26, T-035):** sentiment is NOT blocked — the Crypto
   Fear & Greed Index is freely reachable (99.87% coverage since 2018-02-01) and was tested;
   it failed on lead/lag grounds (reactive not anticipatory), not reachability. Data cached at
   `user_data/research/data/fear_greed/`.
6. ~~Short side / symmetric TSMOM of the champion's gate~~ **CLOSED 2026-07-10**
   (H-BearShort, #16): stopped at the whipsaw pre-gate for zero trial cost. Any future
   short-side idea must first explain how it defeats the documented crash-then-squeeze
   structure (see SESSION_2026-07-10_BEARSHORT.md S5), not re-parameterize the mirror.
7. ~~BTC-ETH cointegration pairs / relative value~~ **CLOSED 2026-07-10** (H-CointPair,
   #18): stopped at the stationarity pre-gate for zero trial cost -- no cointegration on
   any tested window, post-2024 regime break formally documented (ADF p 0.405). This was
   the last untested structural OHLCV mechanism: **the structural map of this dataset is
   closed.** Any future spread idea must first show live/forward evidence that a rolling
   cointegration census passes again (see SESSION_2026-07-10_COINTPAIR.md S8), not re-run
   the census on the same window.
8. ~~Sizing-layer refinement (rebalance granularity / no-trade band)~~ **CLOSED
   2026-07-10 -- SIZING LAYER AT ITS EFFICIENT FRONTIER** (H-SizingBand, #19): stopped
   at the continuous-bound pre-gate for zero trial cost. The fee-free unquantized bound
   -- a hard ceiling for ANY discretization scheme -- delivered only +3.0pp of the
   required >=5.0pp MC-tail improvement and degraded TEST Sharpe by 0.12. Combined with
   #15 (better estimator -- discarded by the quantizer), the sizing layer is closed from
   both directions. The champion's residual MC tail (~30%) is structural to long-only
   crypto trend exposure; future tail-reduction ideas must operate at the
   portfolio/allocation level (cf. the defensive variant), not inside the sleeve's
   sizing (see SESSION_2026-07-10_SIZINGBAND.md S4-6). **Portfolio-level allocation
   tested 2026-07-11 (H-TailAlloc, #20): CONFIRMED at w*=0.8 -- see open-hypothesis closure below.**
9. ~~DVOL axis for daily-bar champion modifications~~ **CLOSED 2026-07-12** (H-IVGate B3a
   + H-IVSizing P2): episode-veto closed because champion is already flat during 5/9
   IV-spike onsets; continuous-sizing closed because high-DVOL days have better-than-average
   forward returns (VRP is positive-carry). No third mechanism on daily bars without new data.
   Future DVOL ideas would require a change-based (not level-based) construction AND a new
   pre-registration AND a new data axis or mechanism rationale.

## Lessons from books (Knowledge/ folder, 5 books extracted 2026-07-07/08)

- **Pardo**: WFA is the core anti-overfit tool; robustness = broad contiguous parameter
  plateaus, not peaks; net profit is a dangerous objective function. Project independently
  converged on all of this.
- **Chan**: Kelly + half-Kelly practice; backtest bias taxonomy; capacity/regime-shift
  vigilance; "gradual scale-up" as psychological and statistical protection.
- **Vince**: Optimal f math in full; drawdown is proportional to f; treat optimal f as an
  UPPER BOUND, not a target (Kaufman concurs).
- **Hilpisch**: vectorized + event-based backtesting patterns; his own live example deploys
  on a different bar length than backtested — a cautionary tale, not a template.
- **Kaufman**: Efficiency Ratio/noise as regime diagnostic; trend-following persists because
  of fat tails; "average of all tests, not the peak test"; one-shot walk-forward (re-running
  destroys OOS validity); full stop/sizing/risk-control taxonomy. Most actionable:
  Research_Ideas.md #84-112 in `Knowledge/Kaufman_Trading_Systems_and_Methods/`.

## Lessons from empirical testing (what this project has proven on its own data)

1. **No signal-prediction edge survives OOS** on retail OHLCV (95+ constructs, 6+ sessions).
2. **Regime avoidance is the only transferable edge** (positive Sharpe 9/9 assets untouched).
3. **Vol-target sizing is the only overlay that improves risk without hurting Sharpe.**
4. **The data's Sharpe ceiling ≈ 1.2-1.3** for risk-managed constructs on daily OHLCV.
5. **Fees kill everything intraday** (0.15%/side); real anomalies exist (hours 21-22 UTC) but are untradeable.
6. **Multiple-testing debt is real and cumulative**: DSR at n_trials=97 prices the champion
   at 0.626. More grinding on the same data is provably counterproductive.
7. 2024-2026 regime is hostile to all trend variants (test Sharpes 0.1-0.4 everywhere).
8. **Sizing-input precision is discarded by the 25% quantization step** (H-RangeVol, #97):
   a 7x-more-efficient vol estimator moved MC tail only 30.5%→22.9% and couldn't beat the
   champion. ~~Improving the sizing layer now requires changing rebalance granularity (a
   fee-loaded, different hypothesis), not a better estimator.~~ **Superseded 2026-07-10
   (H-SizingBand, #19): the granularity lever is ALSO closed** — the fee-free continuous
   bound fails the tail bar and hurts TEST Sharpe. Corrected reading: the quantizer is a
   FEATURE (a free no-trade band that filters rv30 estimator noise), and the discarding
   is protective. The sizing layer is at its efficient frontier.
9. **Synthetic sanity gates work**: EWMA trial #98 was cancelled at zero n_trials cost when
   simulation showed its mechanism (noise reduction) is absent on daily bars.
10. **Crypto bears are not inverted bulls** (H-BearShort, 2026-07-10): the champion's gate
   mirrored short is a whipsaw detector (median episode 3 bars; 2018's −84% bear yielded
   +2.6% gross). Regime *avoidance* is lag-tolerant; regime *harvesting* is lag-punished —
   the flat-in-bear design is not leaving money on the table for this mechanism.
11. **Zero-cost pre-gates have now stopped four doomed trials in a row** (EWMA sanity
   gate; BearShort whipsaw census; CointPair stationarity census; SizingBand continuous
   bound). Activity/whipsaw/stationarity censuses are mandatory before any future
   gate-style or spread-style trial; a mathematical upper-bound counterfactual (evaluate
   the idealized, cost-free version of the mechanism first) is the cheapest and most
   decisive pre-gate class where one exists.
12. **The champion is LESS shock-dependent than its underlying** (A-ValidatorAudit, #17):
   removing all static-p99 shock days IMPROVES its Sharpe (1.11→1.20); its 3σ-shock
   exposure is asymmetric-favorable by mechanism (in-market only in confirmed uptrends).
   Its WF verdict is boundary-stable (3/4/5-window configs majority-positive; rolling
   18m Sharpe never negative), with weakness localized to two episodes (2024-04→10 chop,
   ~2025-10→11 gate exit). Peak-of-family context: full-window 1.33 was rank 1 of 66;
   the family's mean TEST Sharpe was negative — this is what DSR 0.626 prices.
13. **BTC-ETH are not cointegrated; the ETF-era relative-pricing break is formal**
   (H-CointPair, #18): return correlation ≈0.8 yet no stationary spread on any tested
   window (Chan's correlation≠cointegration warning replicated on crypto's core pair);
   post-2024 the ETH/BTC relationship is a unit-root drift (ADF p 0.405). All
   rotation/dominance/ratio/spread constructions on this pair are statistically
   groundless on current data — this retroactively explains #13's z-fade failure.
14. **The champion's MC drawdown tail (~30%) is structural, not implementational**
   (H-SizingBand, #19, with #15): both sizing-refinement routes — estimator quality
   and rebalance granularity — fail to reach the ≤20% bar even under idealized
   assumptions. The tail is carried by what the strategy IS (long-only crypto trend,
   ρ≈0.8 pair). ~~The only validated tail-cutter remains the portfolio-level vol overlay
   (defensive variant, P(DD<−25%)=1%), which pays for it in return.~~ **Updated
   2026-07-11 (H-TailAlloc, #20): an 80/20 champion/defensive monthly-rebalanced
   portfolio cuts MC tail to 16.5% while retaining TEST Sharpe 0.38 and CAGR +21.1%
   — an interior dominating point. Full defensive (w=0) still thinnest tail (0.7%) at
   return cost; champion alone (w=1) still highest return at tail cost.**
15. **Return correlation ≠ portfolio frontier degeneracy** (H-TailAlloc, #20): BTC+ETH
   champion and 9-asset defensive streams correlate r≈0.80 on daily returns (same
   mechanism), yet MC tail falls from 30.5% to 16.5% at w=0.8 because drawdown *paths*
   diversify under block-shuffle — a Vince/Kaufman portfolio-construction effect. The
   knee is narrow (w=0.9 fails the ≤20% bar at 22.1%); there is no broad plateau of
   equivalent allocations.
19. ~~Crypto IV is reactive, not anticipatory, at daily granularity~~ **RETRACTED (Director
    cycle #13, 2026-07-11)**: the H-IVGate lead/lag table was symmetric by construction (sign
    bug — both branches computed the IV-leading correlation). Corrected census shows the
    OPPOSITE: Δ5d DVOL changes LEAD Δ5d rv30 changes (avg_lead +0.2489 vs avg_lag +0.0714;
    lag −1 corr +0.3335 exceeds contemporaneous +0.2883; lagging side decays to ~0 by +4).
    DVOL is also non-redundant with rv30 in levels (corr 0.687). Durable infrastructure:
    BTC+ETH DVOL cached at `user_data/research/data/dvol/` (2021-03-24 onward).
20. **Pre-gate discipline is 5-for-6 valid; the false stop was corrected** (amended 2026-07-12):
    EWMA sanity gate, BearShort whipsaw census, CointPair stationarity census, SizingBand
    continuous-sizing bound, and **IV B3a episode-count census** each correctly stopped a doomed
    trial at zero n_trials cost. The IV lead/lag census (initially the "5th") was a false stop
    from a code bug, corrected on Director review; B3a is the genuine 5th valid stop. Mandatory
    sanity check for lead/lag: **assert the −k and +k sides differ before the verdict line runs**
    — exact symmetry between two distinct series is a bug signature, not a market fact.
21. **DVOL lead is real but not harvestable through the z_iv > 2.0 veto construction**
    (H-IVGate B3a, 2026-07-12): DVOL carries independent level information (0.687) AND leading
    change information (+0.2489 vs +0.0714) — BUT only 4 in-market spike-onset episodes exist
    in 5.19y of data (< 6 required). The champion's regime gate achieves regime-orthogonality
    with IV spikes by mechanism: already flat during 5 of 9 spike onsets. The leading DVOL
    information is real; this specific veto construction cannot be validated. Any future DVOL
    hypothesis must address the structural overlap problem before spending a trial.
22. **Episode-count pre-gating is mandatory for crisis-veto ideas on gated strategies**
    (H-IVGate B3a, 2026-07-12 -- new process lesson): before any hypothesis that adds a
    crisis filter to a gated strategy, compute how many crisis events the strategy is IN-MARKET
    for. A strategy that already avoids crises by mechanism faces structurally narrow
    harvestability -- the crises the veto targets are often ones the gate already caught. B3a
    stopped this trial at zero n_trials cost.
23. **The VRP (variance risk premium) is positive-carry in crypto; DVOL > rv30 days are
    favorable, not adverse** (H-IVSizing P2, 2026-07-12): days when DVOL/100 > rv30 have
    forward 10d median +1.67% vs unconditional +0.53% -- materially BETTER. The options market
    charges an IV premium precisely in the "wall of worry" trending phases when the champion is
    in-market. Reducing exposure there harms, not helps. **Consequence: a lead in CHANGES
    (what the phase21 census measured) is a distinct property from worse returns on high-LEVEL
    days (what P2 measured). Both must be verified before any IV-based sizing modification.**
24. **P1 and P2 pre-gates for sizing modifications are complementary and non-redundant**
    (H-IVSizing, 2026-07-12): P1 confirmed the max() construction fires on 33% of in-market
    days (not a quantizer-absorbs-it failure). P2 found those days are the wrong target. Had
    only P1 been evaluated, the trial would have run and produced a rejected result at n_trials
    cost. Both gates are mandatory: one passing tells you nothing about the other.
25. **A fired-but-never-active-in-TEST construction is a design defect** (H-IVSizing, 2026-07-12):
    the TEST split (2025-08-17 to 2026-05-27) contains zero differing days between IVSizing
    and champion -- the most recent ~9 months show rv30 >= DVOL/100 consistently. Bar 6 (>0
    diff days in TEST) would have independently rejected the trial. Any future construction
    must verify it fires in the evaluation period before spending a trial.
26. **The "no signal-prediction edge survives OOS" finding now extends to fitted statistical/ML
    models, not just hand-specified technical rules** (H-LogisticEntry, T-034, 2026-07-21): a
    logistic regression on 5 pre-registered lagged log-return features failed BTC's in-sample
    hit-ratio significance test (53.1%, p=0.162) before any OOS step was even reached -- the
    ceiling appears to be a property of this data's (lack of) simple linear predictability, not
    an artifact of only ever testing rule-based constructions. ETH's own model passed the same
    in-sample bar (56.7%, p=0.0029), but the pre-registered joint two-asset gate (both legs must
    clear) meant it was never carried into a full backtest -- a genuinely significant single-asset
    result can be shelved by design under a joint multi-asset construction; this is a property of
    the gate design, not evidence the ETH result is spurious.
27. **The first genuinely non-OHLCV data axis tested (crowd sentiment) is reachable but reactive,
    not anticipatory** (H-FearGreed, T-035, 2026-07-21/26): the Crypto Fear & Greed Index passed
    reachability (99.87% coverage since 2018) and redundancy (corr 0.14/0.70 vs rv30/roc30, both
    < 0.90 — genuinely distinct information) but failed lead/lag: F&G changes correlate far more
    strongly with *past* price/vol moves (avg |neg-lag| 0.14 returns / 0.0136 rv30Δ) than with
    *future* ones (avg |pos-lag| 0.008 / 0.0127) — it is a mirror of price, not a predictor of it.
    This closes the sentiment axis for anticipatory-veto constructions specifically; a reactive-
    confirmation framing (using F&G to confirm a move already underway, not to anticipate one)
    was not tested and is not foreclosed by this result. Process note: the pre-registered step-3
    gate code used AND where the spec specified OR — a defect that happened not to change this
    verdict (both legs independently fail) but is a reminder to literally transcribe boolean gate
    logic from the spec, not paraphrase it.

## Known weaknesses of current best

- DSR 0.626 at n_trials=97 (2026-07-10 recompute) → roughly a favorable coin flip, not statistical proof.
- Train Sharpe 1.59 → test 0.41 decay; forward expectation must use the test number.
- Underperforms HODL in raging bulls by design; most historical return came from 2020-21.
- MC tail: P(DD<-25%) ≈ 28-38% for champion alone; **reducible to ~16.5% via validated 80/20 portfolio stance** (H-TailAlloc #20).
- Trend-following decay risk in ETF-era crypto already visible in 2024-26 segment.
- Full-window headline Sharpe was the PEAK of its 66-member search family (family mean
  TEST Sharpe negative) — Kaufman average-of-all-tests context, audited 2026-07-10;
  the DSR number is the honest single-figure correction for this.
- P&L is top-day concentrated (top-10 own days = 44.6% of log-P&L; top-20 = 79.6%) —
  structural to trend following and MILDER than BTC hold's own concentration, but it
  means forward results hinge on catching the few big days (audited 2026-07-10).

## Known regime sensitivities

- TVT: excellent in sustained trends (2020-21, 2023-24), flat in bears (by design),
  weak/whipsawed in choppy sideways regimes (2024-26).
- Mean reversion: never worked on this data at any timeframe (trending asset class + fees).
- Alt satellites: dead since 2024 (no alt season); 9-asset diversification helps tail only.

## Highest-priority future research (ranked by expected value)

1. ~~Pull CFTC COT data for CME BTC/ETH; test positioning-based regime filter~~ DONE and
   REJECTED 2026-07-08 (H-COT, #14) — kept here only as the historical rank; the cached
   data axis remains available under the conditions in open-hypothesis item 4.
2. ~~Implement Kaufman Ch.21 audit items in validator.py; re-audit champion with them~~
   DONE 2026-07-10 (A-ValidatorAudit, #17 — audit clean; see
   SESSION_2026-07-10_VALIDATOR_AUDIT.md).
3. ~~Reconcile 40% vol-target vs Kaufman's 6-8% guidance~~ DONE 2026-07-10 (see
   SESSION_2026-07-10_RANGEVOL.md §8; no contradiction, no parameter change).
4. If any new hypothesis is proposed: it must use a genuinely new data dimension or a
   structurally different mechanism — parameter variations of tested families are banned.
