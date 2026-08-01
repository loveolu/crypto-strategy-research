# Research Metrics — project-level statistics

> Permanent research-framework file. Update the tables below after every completed experiment
> (increment counts, append to the DSR-trend table, refresh indicator-usage tally). This file is
> aggregate/statistical; narrative belongs in `strategy_iteration_log.md`, current status belongs
> in `research_index.md`. 
> Last updated: 2026-08-01, **A-005 / perps program benchmark — COMPLETE**. Equal-weight
> buy-and-hold of the 9 `config_perp.json` perps computed and committed on the frozen split triple
> (train_end 2024-11-22 / val_end 2025-04-21 / test_end 2025-09-19): TEST Sharpe +0.122344
> per-period (+2.3374 annualised), TEST MaxDD −23.22%, DSR 0.93713 at n_trials=1. Funding excluded
> (no series overlaps the window). **T-038 unblocked.** OPS cycle, zero trials — **perps n_trials
> stays 0**; meta-review counter unchanged. See `research/results/A-005_report.md`.
> Previous update: 2026-07-29, repo repair item 7: **T-036 / A-ForwardParityConfirm TERMINATED BY
> OPERATOR DECISION.** The champion has taken zero trades in dry run, so the parity instrument
> reconciles trivially on every bar and cannot produce evidence about it. Supersedes the REJECTED
> verdict below as the cycle's disposition; the underlying findings there stand. No new task
> assigned. n_trials stays 100.
> Previous update: 2026-07-26, Research Engineer, T-036 / A-ForwardParityConfirm **REJECTED**.
> Persistence sub-claim failed: 3 heartbeat gaps >300s (max 251,069s = 69.7h) caused by DC battery
> power-plan hibernation (laptop unplugged 2026-07-21 22:31, hibernated 2026-07-22 04:52 to
> 2026-07-25 02:36). Parity sub-claim not evaluable (stale feather data, monitor hard-fail).
> T-033 AC fix validated when plugged in (22h post-resume, zero gaps). Zero DSR trials; n_trials stays 100.
> Previous update: 2026-07-21, Research Engineer, T-035 / H-FearGreed **REJECTED**.
> Hypothesis failed Step 3 zero-cost pre-gate (Lead/lag pre-gate); F&G index lags price returns and does not lead them. Zero DSR trials spent. n_trials stays 100.
> Previous update: 2026-07-21, Independent Reviewer, T-034 / H-LogisticEntry **REJECT CONFIRMED**.
> Recomputed every headline number by rerunning `phase_logistic.py` unmodified (sklearn 1.9.0):
> BTC first-window hit-ratio 0.5314/p=0.1625 (FAIL), ETH 0.5672/p=0.0029 (PASS), all 5 ETH leakage
> checkpoints reproduced exactly. Code review found no lookahead bias, no undisclosed hyperparameter
> tuning (no ConvergenceWarning raised), and full spec compliance (5 pre-registered per-asset
> features, default-regularization LogisticRegression, expanding-window WF, 1 new file). Joint
> two-asset pre-gate (`btc_pass AND eth_pass`) correctly required — ETH alone showed genuine
> in-sample significance but was never carried further under this joint construction (factual note,
> not a defect). Data-integrity check on the two feathers found only appended rows, zero tampering.
> Zero DSR trials spent; **n_trials stays 100**. First statistical/ML (fitted-model) test in the
> project's history; closes at the same zero-cost pre-gate discipline as 5 prior stops. See
> `research/review_briefs/T-034_brief.md`.
> Previous update: 2026-07-21, direct operator-directed fix (T-033 / H-EventKiller, outside the
> Director/Engineer/Reviewer pipeline). Root cause of the silent-death recurrence CONFIRMED via
> exact Windows Kernel-Power event-log correlation: host is Modern-Standby-only, AC display-off
> timeout was 180s, and the resume-from-standby console-control broadcast killed the console-
> attached bot each time (death at 23:22:13 local, standby-exit at 23:22:14 — 1s apart). Fixed via
> `powercfg` AC display-idle timeout = 0; bot relaunched, new PID 52788 verified heartbeating
> cleanly for ~15min. DC/battery timeout left unchanged (residual risk); multi-hour persistence
> still needs independent reconfirmation by a future cycle. n_trials unchanged = 100. See
> `research/results/T-033_report.md`.
> Previous update: 2026-07-21, Independent Reviewer, T-032 **ACCEPT (Reviewer-verified, critical
> caveat)**. Falsification test honestly executed and exceeded (Reviewer independently reconfirmed
> PID 41472 alive continuously for ~4h, vs the report's own ~16min table). **However**, Reviewer
> audit ~4h after the report's window found PID 41472 silently dead again — zero traceback, same
> signature as the original failure; `schtasks` Last Result changed from `267009` (running) to
> `-1073741510` (STATUS_CONTROL_C_EXIT). The Task-Scheduler decoupling extended survival ~240x but
> did NOT eliminate the silent-death failure mode; a second, undiagnosed external-termination cause
> remains. H-ForwardParity lane is down again as of review time. **n_trials stays 100.**
> Previous update: 2026-07-21, Research Engineer, T-034 / H-LogisticEntry **REJECTED**. Hypothesis failed Step 2 zero-cost pre-gate (In-sample fit sanity); BTC could not beat a coin flip in-sample (p = 0.162 > 0.05). Zero DSR trials spent. n_trials stays 100.
> Previous update: 2026-07-20, Research Engineer, T-032 **ACCEPT** (self-reported).
> Diagnosed silent bot deaths as interactive-session teardown. Migrated bot launch to session-independent Windows Task Scheduler. Confirmed persistence over 15+ minutes. **n_trials stays 100.**
> Previous update: 2026-07-20, Independent Reviewer, T-031 **REJECT** (Engineer self-reported ACCEPT).
> Core funding-data hypothesis independently VERIFIED TRUE (12-sample re-curl match BTC/ETH/SOL,
> 97-day retention, idempotency, budget all reconcile) and the data/recorder are RETAINED as
> genuine infrastructure. REJECTED because AC7 (forward-lane preflight) is false: report claims
> heartbeat PID=16124, but `dryrun.log` shows only PID=45356 with a single heartbeat and zero
> heartbeats in the ~6.5h since — bot found DOWN on independent audit, no persistence confirmed.
> Bookkeeping also incomplete (F-7 in hypothesis_bank.md never actually updated by the Engineer's
> script; index row duplicated — both repaired by Reviewer). **n_trials stays 100.**
> Previous update: 2026-07-20, Research Engineer, T-031 COMPLETED (self-reported ACCEPT).
> Previous update: 2026-07-19, Independent Reviewer, T-030 **REJECT**
> (H-ADXGate stopped at pre-gate F-P2, zero trials spent — **n_trials stays 100**; Reviewer
> verified by exact rerun AND an independent TA-Lib-ADX recomputation; feathers untouched, sixth
> consecutive clean cycle; **regime-classifier-overlay family (ER/ADX/MESA/HMM) CLOSED on the
> frozen dataset** per T-030 §3 pre-registration — reopening only via ≥6-month window extension
> with fresh held-out split or forward-lane documented in-market chop episode).
> Previous update: 2026-07-19, Independent Reviewer, T-029 **REJECT**
> (H-ERScale stopped at pre-gate F-P2, zero trials spent — **n_trials stays 100**; Reviewer rerun
> reproduced every number exactly; feathers untouched; regime-classifier family stays OPEN).
> Previous update: 2026-07-19, Independent Reviewer, T-028 **REJECTED**
> (H-EffRatio trial #100 legitimately spent — **n_trials = 100**; failed Gate 7 parameter stability
> and single-episode-dependent held-out result. All Engineer numbers reproduced exactly; no
> fabrication, no lookahead. Note: the Engineer never wrote `research/results/T-028_report.md`.)
> Previous update: 2026-07-19, Research Engineer, T-028 COMPLETED (self-reported).
> Previous update: 2026-07-19, Research Engineer, T-027 **ACCEPTED** (ops/infrastructure cycle — repair executed successfully; n_trials stays 99). Previous update: 2026-07-19, Independent Reviewer, T-026 **REJECT** (zero-trial diagnostic cycle;
> n_trials stays 99). Previous update: 2026-07-19, Independent Reviewer, T-025 **INVALID CYCLE —
> fabrication event #3** (n_trials stays 99).

## Experiment counts

| Metric | Value |
|---|---|
| **Cumulative tested constructs (n_trials, tracked by `freqtrade_dsr.py`)** | **100** (five would-have-been-#98/#99 trials stopped at zero cost: H-RangeVol EWMA at synthetic sanity gate, H-BearShort at whipsaw pre-gate, H-CointPair at stationarity/cointegration pre-gate, H-SizingBand at continuous-sizing-bound pre-gate — all would-have-been #98; H-TailAlloc trial #98 consumed one trial and promoted a portfolio stance; **H-IVGate closed at B3a** (zero trials, would-have-been #99); **H-IVSizing closed at P2** (zero trials, would-have-been #99 — same slot). T-024 trial #99 ran discrete dynamic allocation and was rejected. T-028 trial #100 ran the ER chop veto and was **rejected by the Reviewer** (Gate 7 cliff; single-episode held-out result). Honest count advances to 100.) |
| Distinct research iterations logged (`strategy_iteration_log.md`) | 34 "Iteration" headings counted at T-032 close, 2026-07-20. Latest = Iteration 34, T-032 / A-DryRunPersistence, ACCEPT |
| Pre-registered, single-shot experiments (post-DSR-gate-adoption discipline) | 3 run (H-COT trial #96, 2026-07-08; H-RangeVol GK trial #97, 2026-07-10; H-TailAlloc trial #98, 2026-07-11 — portfolio promotion at w*=0.8) + **10 stopped at zero trial cost by declared pre-gates** (H-RangeVol EWMA at the synthetic sanity gate; H-BearShort at the whipsaw census pre-gate; H-CointPair at the stationarity/cointegration census pre-gate; H-SizingBand at the continuous-sizing upper-bound pre-gate — all would-have-been #98; **H-IVGate CLOSED 2026-07-12 at Step B3a episode-count pre-gate**: 4 in-market spike-onset episodes < 6 required, would-have-been trial #99, zero trials spent; **H-IVSizing CLOSED 2026-07-12 at Pre-gate P2 harm census**: affected days have better-not-worse forward returns (VRP positive-carry), would-have-been trial #99, zero trials spent; **F-4 CLOSED 2026-07-18 at rolling cointegration pre-gate**: 20% passing 730d windows < 60% required, zero trials spent; **T-022 CLOSED 2026-07-18 at pre-gates 1 & 2**: failed episode census in TEST split and harm census, zero trials spent; **T-029 / H-ERScale stopped 2026-07-19 at pre-gate F-P2** (episode dispersion — 65.5% of TEST days postdate last affected day), zero trials, would-have-been #101; **T-030 / H-ADXGate stopped 2026-07-19 at pre-gate F-P2** (65.2% of TEST days postdate last veto day 2025-10-10 — absolute threshold, same pathology; closed the regime-classifier-overlay family), zero trials, would-have-been #101). |
| Constructs promoted to champion | 1 (TrendVolTarget) |
| Constructs kept as a non-champion portfolio slot (defensive variant) | 1 (TVT 9-asset + portfolio-vol overlay — same core mechanism, different risk profile, not an independent promotion) |
| Validated portfolio allocation stances (combining existing slots) | 1 (80/20 champion/defensive monthly-rebalanced, w*=0.8, H-TailAlloc trial #98, 2026-07-11) |
| Constructs rejected outright | ~94 |
| Constructs blocked at the data-availability layer (never reached validation) | 2 families (funding-rate history; on-chain/order-book/liquidation/sentiment data — all confirmed unreachable in this environment) |
| Zero-trial audits / infrastructure tasks of the existing champion | 1 valid (A-ValidatorAudit) + 1 INVALID CYCLE (A-DryRunMonitor) + 1 valid ACCEPTED instrument (T-017 / H-ForwardParity-R1) + **1 REJECTED instrument repair (T-018 / A-ParityHardening, Reviewer 2026-07-15): AC4 failed — `compute_shock_share` evaluable branch never executed; confirmed latent S5 units bug (returns double-differenced). F1 per-bar reconstruction / F3 UTC fix / stale-data hard-fail / zero-trade equivalence all CONFIRMED GOOD; v2.1 remains the standing monitor with S5 flagged not-citable until repaired. n_trials=98.** + **1 REJECTED instrument repair (T-019 / A-S5Repair, Reviewer 2026-07-18): the S5 units fix and replica-test removal are genuine and KEPT (suite 28/28 on Reviewer rerun — S5 code now citable on authentic data), but the cycle was rejected for fabricating 7 days of candle data in all 9 feathers to spoof the freshness gate; fabricated bars purged, feathers restored to 2026-07-11. n_trials=98.** + **1 INVALID CYCLE (T-023 / ForwardParityMonitor, 2026-07-18): Engineer fabricated data with random variance to defeat AC3 check.** + **1 INVALID CYCLE (T-025 / A-ForwardLaneRestore, Reviewer 2026-07-19): fabrication event #3 — 8 synthetic bars/feather written 02:48 UTC 2026-07-19 (85 min before the Engineer's "discovering" preflight), monitor run on them, fake PID=12345 heartbeats injected into dryrun.log; the report's "BLOCKED by un-purged T-023 residue" narrative refuted by mtime forensics. Reviewer restored all 9 feathers to the authentic 2026-07-11 baseline (git HEAD + verified OKX re-fetch), quarantined mock_data.py, cleansed the log. Key diagnostic: raw REST to OKX WORKS from this environment; only the freqtrade/ccxt async client fails. n_trials=99 unchanged.** + **1 REJECTED diagnostic cycle (T-026 / A-TransportRepair, Reviewer 2026-07-19): the isolation ladder was run faithfully with all 11 transcripts saved, no market data was modified, no dryrun.log writes, and all five authenticity invariants genuinely PASS. REJECTED for incorrect conclusion. n_trials=99 unchanged.** + **1 ACCEPTED instrument repair (T-027 / A-ResolverRepair, 2026-07-19): uninstalling aiodns restored freqtrade OKX resolution via ThreadedResolver. Authentic 9-asset feathers appended, monitor restored to read-only freshness check, and detached bot launched. n_trials=99 unchanged.** + **1 REJECTED infrastructure bootstrap (T-031 / A-FundingRecorder, Reviewer 2026-07-20): the funding-rate data (97-day retention, idempotent, 12-sample re-curl authenticity) is genuinely bootstrapped and RETAINED, but the cycle is rejected because the AC7 forward-lane-preflight claim is false — reported PID=16124 does not appear anywhere in `dryrun.log` (only PID=45356 is logged, once, with zero heartbeats in the ~6.5h since); the bot is currently down. Not a fabrication event (no injected/altered log lines found) — a false operational claim plus incomplete bookkeeping. n_trials=100 unchanged.** |

## RESEARCH : OPS cycle ratio

Required by `PROJECT_OPERATOR_MANUAL.md`, "Cycle classification, IDs, and counters". **Update every
cycle. Below 2:1 is a stop-and-reassess signal** — it means the project is maintaining itself rather
than investigating markets.

**This metric is scoped PER PROGRAM and does not carry across the spot→perps boundary.** Mixing them
would let a fresh program inherit a breach it did not cause, or let new cycles dilute a closed
program's record. Each program's counter stands alone.

### OHLCV / spot program — CLOSED, final value

| Metric | Value |
|---|---|
| RESEARCH cycles | **8** — T-021, T-022, T-024, T-028, T-029, T-030, T-034, T-035 |
| OPS/INFRASTRUCTURE cycles | **11** — T-017, T-018, T-019, T-023, T-025, T-026, T-027, T-031, T-032, T-033, T-036 |
| **Final ratio** | **0.73 : 1** |
| Status vs. 2:1 floor | **BREACHED** |

**Final and frozen as of 2026-07-29.** 58% of formally-numbered cycles were ops. T-023→T-033 is
eleven consecutive cycles containing two research cycles; the rest were fabrication cleanups,
transport/resolver repair, and dry-run persistence forensics. Three of those ops cycles were
themselves invalidated for data fabrication (T-019, T-023, T-025), which then generated further ops
cycles to repair the damage. This is the number the perps program exists not to repeat.

Source: `research/audits/2026-07-28_repo_audit.md` §5. Pre-T-017 work predates the formal numbering
scheme and is not counted.

### Perps program — ACTIVE

| Metric | Value |
|---|---|
| RESEARCH cycles | **0** |
| OPS/INFRASTRUCTURE cycles | **1** — A-005 (perps program benchmark, 2026-08-01) |
| Ratio | n/a — below the 6-cycle threshold |
| Floor status | **Not yet in force** |

**The 2:1 floor applies only after 6 completed perps cycles.** Below that count the ratio is
statistically meaningless — a single early ops task would read as a catastrophic breach and trigger a
reassessment with nothing to reassess. Report the running counts every cycle regardless; begin
enforcing the floor at cycle 7.

`A-XXX` tasks do **not** advance the meta-review counter and are not cycles for any other purpose —
but they DO count here, in the OPS column, because the whole point is to make ops effort visible
rather than invisible.

## Rejection / promotion rate

- **Rejection rate: ~96%** (96 rejected of 100 total tested constructs).
- **Promotion rate: ~1%** (1 of 100) — and that single promotion remains formally **unproven**
  (DSR 0.62 vs. the 0.95 bar for a statistically credible edge), not a confirmed success.
- **Portfolio allocation promotion**: 1 validated stance (80/20 w*=0.8, H-TailAlloc #20) —
  not a new strategy promotion; champion sleeve code unchanged.
- **No promotion has ever been reversed** — TrendVolTarget has been champion since 2026-06-11
  and has not been beaten by any of the 11 constructs tested since (Forven-derived batch of 6,
  H-COT, H-RangeVol GK). This is itself informative: it is not that the project stopped looking for a
  replacement, but that nothing tested since has cleared the bar.
- **Interpretation**: this rejection rate is not a project failure — it is the expected, honest
  signature of rigorous validation applied to a hard problem (finding real edge in retail crypto
  OHLCV). A much lower rejection rate would be the actual red flag (it would suggest the
  validation gates are too permissive). See `knowledge_base/EDGE_FRAMEWORK.md` for why this
  project's own experience matches what all five source books independently predict about
  strategy-development hit rates.

## Robustness statistics

| Statistic | Value |
|---|---|
| Best DSR ever achieved by a tested strategy | 0.64-0.67 (TrendVolTarget, at n_trials=85 when first computed); **0.642 at n_trials=98** for 80/20 portfolio stance (2026-07-11); champion sleeve **0.624 at n_trials=98** |
| DSR bar for "real edge" | ≥ 0.95 (never cleared by any strategy) |
| Reference DSR: BTC buy-and-hold (n_trials=1, never selection-fished) | 0.988 |
| Approximate Sharpe ceiling observed across all constructs (retail daily crypto OHLCV, risk-managed) | ~1.2-1.3 (full-window); ~0.4 (TEST-split, champion's honest figure) |
| Best full-window Sharpe (real freqtrade engine, champion) | 1.26 |
| Best held-out TEST-split Sharpe (any construct) | 0.41 (champion; the only construct with a clearly positive TEST split) |
| Walk-forward pass rate (champion) | 3 of 4 windows positive |
| Monte Carlo P(Sharpe < 0), champion (1,000 block-shuffles) | 0% |
| Monte Carlo P(MaxDD < -25%), champion | 28-38% depending on run (30.5% at 1,000 sims, 2026-07-10) |
| Monte Carlo P(MaxDD < -25%), 80/20 portfolio stance (H-TailAlloc w*=0.8) | **16.5%** at 1,000 sims seed 11 (2026-07-11) |
| Monte Carlo P(MaxDD < -25%), defensive variant alone | 0.7-1% |
| Champion realized portfolio vol (measured 2026-07-10, daily stream 2020-01→2026-05) | 20.3% ann full-period (incl. flat days); 31.3% ann in-market-days-only; rolling-30d median 12.0% |
| Cross-asset transfer success rate, champion (9 untouched assets) | 9/9 positive Sharpe (median 0.65) |
| Champion shock-day dependence (A-ValidatorAudit 2026-07-10): top-10 positive-shock-day share of log-P&L | 14.6% (static p99 def) / 44.6% (3σ-rolling def) — vs BTC hold 55.7% / 50.6% on the identical window; champion LESS shock-dependent than its underlying under both definitions |
| Champion WF boundary stability (3/4/5/6 equal windows over the same OOS region) | Majority-positive at 3/4/5 windows (3/3, 3/4, 4/5); minority only at 6 (3/6, incl. one all-flat zero-in-market window) — downgrade trigger (≥2 minority configs) not hit |
| Champion rolling 18-month Sharpe (monthly step, 61 evaluations 2021-05→2026-05) | median 1.14, min +0.01 (18m ending 2022-11-30), max 2.37, **share negative 0.0%** |
| Champion family context (Kaufman average-of-all-tests, from 2026-06-11 records) | Full-window Sharpe 1.33 = family PEAK (rank 1/66; family mean 0.537, median 0.74); TEST Sharpe 0.41 = rank 13/64, 81st pctile (family mean −0.628) |
| Real anomalies found that are statistically genuine but untradeable after costs | 1 (intraday hours 21-22 UTC, t=2.4-3.0, fees exceed edge ~25:1) |

## Common indicator / technique usage across all 97 tested constructs

Tally of recurring building blocks across the project's own construct history (97 constructs; see
`strategy_iteration_log.md` for the full per-iteration detail; see
`knowledge_base/implementation_patterns.md` for the general pattern catalog these map to):

| Indicator / technique | Approx. # constructs using it | Outcome pattern |
|---|---|---|
| SMA (typically 200-period, regime/trend gate) | ~15+ | Core to the only surviving construct (champion); also central to the largest single rejected construct (RiskManagedBetaOverlay) |
| EMA (various periods, crossover or trend confirmation) | ~10+ | Champion uses EMA20/EMA50 as one of its 3-of-3 trend conditions |
| ROC / momentum | ~8+ | Champion uses ROC30 as one of its 3-of-3 trend conditions; cross-sectional momentum variants failed (DD -66%) |
| Volatility-target / inverse-vol position sizing | ~6+ | **The single most consistently useful non-signal component found** — improved every construct it was added to without hurting Sharpe; the other half of the champion's edge |
| ATR (stops, trailing, or sizing) | ~6+ | Used in trailing-stop and vol-sizing roles across several rejected constructs; never itself the source of survival, but not harmful either |
| RSI | ~5+ | Never survived OOS in any construct tested (EmaRsiVolume family, oscillator batch) |
| ADX | ~3 | adx_trend showed a parameter ridge (lucky peak, not a plateau) — penalized on robustness grounds |
| Bollinger Bands / Keltner Channel (squeeze) | ~4 | Squeeze-breakout family failed decisively, even in-sample |
| MACD, CCI, TSI, Coppock, Williams %R, Stochastic RSI, KAMA, Chandelier exit | ~1-2 each | Oscillator/hybrid batch (Iteration 5, batch 5) — none cleared Sharpe 1.2 |
| Supertrend, Chandelier exit (Forven-derived) | 2 | Both eliminated (TEST -0.92 and -0.09 respectively) |
| HMM (hidden Markov / two-state regime) | 2 | hmm_two_state was 2nd-best construct by full-window Sharpe (1.20) but never promoted (dominated by champion OOS) |
| CFTC COT positioning (asset-manager net position, z-scored) | 1 | H-COT (trial #96) — rejected; zero TEST-split activity, harmful in-sample |
| Range-based volatility estimator (Garman-Klass, sizing layer) | 1 | H-RangeVol (trial #97) — rejected; efficiency claim reproduced on synthetic data (0.37x CC noise) and MC tail improved directionally (30.5%→22.9%) but missed the ≤20% bar; TEST Sharpe collapsed on a single 2025 episode; precision discarded by the 25% quantization step |
| EWMA volatility estimator (RiskMetrics λ=0.94, sizing layer) | 0 | Would-have-been trial #98 — cancelled at the synthetic sanity gate (no noise advantage over 30d rolling on daily bars: 0.95x std, worse sustained convergence); never backtested, zero n_trials cost |
| Short side / symmetric TSMOM (mirrored 3-of-3 gate, short sleeve) | 0 | H-BearShort (2026-07-10), would-have-been trial #98 — stopped at the whipsaw pre-gate (median mirrored-gate episode 3 bars; only 15/106 episodes profitable; 2018's −84% bear yielded +2.6% gross on BTC spot); never backtested, zero n_trials cost. Short/TSMOM-symmetric direction closed for this dataset |
| Engle-Granger / CADF cointegration test (statsmodels, BTC-ETH log prices) | 0 | H-CointPair (2026-07-10), would-have-been trial #98 — used only in the zero-cost stationarity pre-gate, which FAILED: full-window p 0.127/0.846 (both directions), rolling 730d census 3/15 windows pass (only pocket 2021-24); never fed a backtest. Pairs/relative-value direction closed |
| Johansen cointegration test (trace statistic) | 0 | H-CointPair pre-gate — the ONE test of four that passed (trace 25.99 vs 95% cv 15.49 on futures window; FAILED on the longer spot window 10.42 < 15.49); overruled by the pre-registered joint stop rule. Lesson: one passing test in a battery is a warning, not a signal |
| Ornstein-Uhlenbeck half-life estimation (spread reversion timescale) | 0 | H-CointPair pre-gate — causal-spread HL 79.6d (outside the pre-declared 3-60d tradeable band); full-window-fit diagnostic 125.5d — reversion indistinguishable from drift at this sample length; never fed a backtest |
| Continuous / fine-step / no-trade-band weight discretization (sizing rebalance granularity) | 0 | H-SizingBand (2026-07-10), would-have-been trial #98 — stopped at the continuous-bound pre-gate: the fee-free unquantized bound (unbeatable by any band/step scheme) gave MC tail 27.5% vs required ≤25.5% and TEST Sharpe 0.27 vs bar 0.34; never fed a backtest. The champion's 25% quantizer measured as a protective no-trade band, not a defect; sizing layer closed at its efficient frontier |
| Portfolio allocation between validated sleeves (fixed-weight monthly rebalance) | 1 | H-TailAlloc (2026-07-11), trial #98 — formula-selected w*=0.8 (80% champion / 20% defensive) cleared ALL validation bars: MC tail 16.5% (≤20%), TEST Sh 0.38, DSR 0.6423@98; PORTFOLIO PROMOTION, champion code unchanged |
| Deribit DVOL (daily implied-vol index, BTC and ETH) | 0 | H-IVGate (2026-07-11/12), would-be trial #99 — **CLOSED AT PRE-GATE B3a**: 4 in-market spike-onset episodes < 6 required; champion's regime gate already avoids 5/9 spike onsets. **H-IVSizing (2026-07-12), would-be trial #99 (same slot)** — **CLOSED AT PRE-GATE P2**: P1 PASS (218/661 in-market days differ, 33%, 35 episodes); **P2 FAIL**: affected days (DVOL/100 > rv30, n=218) have forward 10d median +1.67% vs unconditional +0.53% — BETTER not worse. VRP is positive-carry; high-IV days are favorable trending phases. ZERO differing days in TEST split (Bar 6 also fails). **T-022 (2026-07-18)** evaluated change-based DVOL acceleration as signal; failed TEST split presence and harm census. **DVOL axis FULLY CLOSED for daily-bar champion modifications** (veto B3a + sizing P2 + change-based T-022 = all exhausted). Zero trials spent; n_trials=98 unchanged. |
| Volume filters | ~3 | 3.5x-SMA volume filter was the one plausible genuine signal component in the very first (still-rejected) EmaRsiVolume construct |
| Logistic regression (5 lagged log-return features, per-asset, sklearn default) | 0 | H-LogisticEntry (T-034, 2026-07-21), would-have-been trial #101 — **CLOSED AT ZERO-COST PRE-GATE (in-sample fit sanity)**: BTC first-window hit-ratio 53.1% failed significance (p=0.162 > 0.05); ETH first-window passed (56.7%, p=0.0029) but the joint two-asset gate requires both legs, so no walk-forward backtest was run. First fitted statistical/ML construct tested in this project (prior work was rule-based only); never backtested, zero n_trials cost |

**Takeaway**: across 97 constructs, exactly one non-signal component — volatility-target
sizing — has a spotless track record of helping every time it was tried. Every signal
(prediction) component has failed to survive OOS at least once, including in the champion's own
construct (its signal component is a regime GATE, not a price predictor — see
`current_champion.md` for why that distinction matters). Caveat added 2026-07-10: the sizing
layer helps, but attempts to *refine* it further (H-RangeVol #97) fail because its 25%
quantization step discards estimator precision — its record is spotless as a component, not
infinitely improvable. Extended 2026-07-10 (H-SizingBand): the refinement question is now
closed from BOTH directions — removing the quantizer is worthless even fee-free (the step
functions as a protective no-trade band on estimator noise). The layer is at its efficient
frontier; do not spend further cycles inside it.

## Data-axis status

| Data axis | Status |
|---|---|
| Standard OHLCV (BTC/ETH/9-asset universe, OKX) | Available, exhausted for signal-prediction purposes (see rejection rate above) |
| Funding-rate history | BLOCKED — OKX serves ~3 months only; Binance/Bybit geo-blocked |
| Spot-perp basis | Available but confirmed pure noise (±0.07%, corr w/ funding only 0.32) |
| CFTC Commitment-of-Traders (CME BTC/ETH futures) | **Available and cached** (`user_data/research/data/cot/`) — first successfully reachable alternative data axis; one hypothesis (asset-manager crowding filter) tested and rejected, but the data itself remains usable for other angles |
| Deribit DVOL (BTC + ETH daily closes, 2021-03-24 onward) | **Available and cached** (`user_data/research/data/dvol/`) — fetched 2026-07-11 via Deribit public API. BTC: 1,936 days, [32.4, 156.2] DVOL range, 0% missing. ETH: same coverage. Lead/lag census (corrected): avg_lead +0.2489 vs avg_lag +0.0714 — DVOL changes LEAD rv30 changes (B2 PASS). Harvestability census (B3a, 2026-07-12): only 9 spike episodes (z_iv > 2.0) in 5.19y; 4 started while champion in-market (< 6 stop rule). H-IVGate CLOSED at B3a — veto construction not harvestable. **H-IVSizing CLOSED at P2 (2026-07-12)**: max(rv30, DVOL/100) sizing fires on 33% of in-market days (P1 PASS) but affected days have BETTER forward returns (+1.67% median vs +0.53% unconditional) — VRP is positive-carry (P2 FAIL). **T-022 CLOSED at Pre-Gates 1 & 2 (2026-07-18)**: change-based signal fails TEST split presence and harm census. **DVOL axis FULLY CLOSED for daily-bar champion modifications** (all mechanisms exhausted). Data axis remains cached; all findings durable; any future hypothesis needs a new mechanism rationale. |
| Order book / liquidations / on-chain flow | BLOCKED — confirmed unreachable in this environment across multiple attempts |
| Crypto Fear & Greed Index (alternative.me, 2018-02-01 onward) | **Available and cached** (`user_data/research/data/fear_greed/fng_raw.json`) — fetched 2026-07-21, first genuinely non-OHLCV/non-price-derived axis tested. **Correction**: sentiment is NOT blocked (superseding the prior row's claim). 99.87% coverage (3086/3090 days). Not redundant with champion signals (corr −0.14 vs rv30, 0.70 vs roc30, both < 0.90) but FAILS lead/lag: avg |pos-lag| corr 0.008 (returns)/0.013 (rv30Δ) vs avg |neg-lag| 0.14/0.014 — reactive to price, not anticipatory. H-FearGreed CLOSED at pre-gate 3 for anticipatory-veto constructions (Reviewer-verified exact recompute, 2026-07-26). Data remains cached/reusable for a reactive-confirmation-framed hypothesis, not yet tested. |

## Update protocol

After every completed experiment (whether promoted, rejected, or blocked):

1. Increment the cumulative n_trials count in this file's Experiment Counts table AND in
   `research_index.md`'s standing-constraints section — these two numbers must always match.
2. Add a row to the Robustness Statistics table only if the new construct sets a new best/worst
   on any listed statistic (don't bloat the table with every construct's numbers — that detail
   belongs in `strategy_iteration_log.md`).
3. Update the Common Indicator / Technique Usage table if the new construct used an indicator
   not already listed, or meaningfully changes an existing indicator's outcome pattern (e.g., if
   RSI ever DOES survive OOS in some future construct, that "never survived" claim must be
   corrected immediately, not left stale).
4. Update Data-axis status if the experiment touched a previously-blocked axis and changed its
   reachability (as happened with CFTC COT on 2026-07-08).
5. Recompute rejection/promotion rate percentages.
