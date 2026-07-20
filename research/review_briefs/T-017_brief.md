# Review Brief — T-017 / H-ForwardParity-R1

**Independent Reviewer, 2026-07-12.** Audit of the repaired forward-parity instrument
(reissue of the cycle-#16 INVALID task). Engineer report: `research/results/T-017_report.md`.
Session report: `user_data/research/SESSION_2026-07-12_FORWARDPARITY_R1.md`.

---

## 1. Verdict

**VALID CYCLE — INSTRUMENT ACCEPTED.**

The deliverable (`user_data/research/dryrun_monitor.py` v2) passes all seven acceptance
checks in NEXT_TASK.md on independent verification. The hypothesis H-ForwardParity itself is
**neither confirmed nor falsified** — it remains OPEN (classification: PARKED-OPEN, reopening
evidence = accrued forward data; the instrument keeps running). This task could not promote
or demote the champion by its own contract, and it did not. n_trials stays 98. Champion,
validator bars, and the 80/20 portfolio stance are all untouched (verified).

## 2. Evidence supporting the verdict

Every acceptance check was verified independently, not taken from the report:

1. **Step-0 refresh + freshness**: I read the feathers directly — BTC and ETH both end
   2026-07-11 (3104 / 2415 rows, matching the report exactly). The rerun printed
   `FRESHNESS CHECK PASSED` with candle last 07-11, realized last 07-12, window end 07-12.
2. **Hard-fail assertion in code**: present (`assert_freshness`, dryrun_monitor.py:113-132),
   invoked at line 375 BEFORE any verdict logic; failure path prints `STALE DATA -- NO
   VERDICT` and `sys.exit(1)`. Structurally sound.
3. **Coverage math**: I recounted heartbeats from the raw log — 1408 (07-10), 1440 (07-11),
   761 (07-12), zero on 07-08/07-09; log first line 2026-07-10 00:27:34. Coverage 3/5 = 60%,
   the 07-08/09 gap appears (the #16 "100%" defect is fixed). ERROR lines independently
   recounted: 411 total = 2 websocket + 409 market-load, matching the classification.
4. **Four required sections**: all present in the script output and DRYRUN_LOG.md entry —
   (a) dated daily return series (5 rows, all 0.0, correct for a 0-trade window);
   (b) expected-side window stats from fresh candles (0/4 in-market, 0 entries, 0 rebalances);
   (c) 80/20 stance line (0.0000 all days; 9-asset sleeve proxied by BTC+ETH — disclosed);
   (d) shock-share: evaluability precondition reported unmet with accrued counts (0 < 20),
   which satisfies the acceptance check's OR-clause.
5. **Locked-trigger block**: reproduced in session-report §1 before any results. Content
   matches NEXT_TASK.md; symbols are ASCII-transliterated (→ becomes ->), substance identical.
6. **M1 parity**: per-bar table printed, 4/4 AGREE. **Not vacuous**: I recomputed the 3-of-3
   gate from the raw feathers with my own code (not the Engineer's functions) — both pairs
   fail `close>SMA200` and `EMA20>EMA50` on every window bar; the last core-True bar for
   both pairs was 2025-10-09. The expected side is genuinely flat on genuinely fresh data.
7. **Protected files**: empty git diffs and pre-session mtimes for
   `research/best_strategy_so_far.py` (07-08), `user_data/strategies/TrendVolTarget.py`
   (06-11), `user_data/research/validator.py` (07-10), `research/strategy_portfolio.md`
   (07-11). DB independently read via sqlite3: trades 0 rows, orders 0 rows.

**Reviewer rerun**: `py -3.13 user_data/research/dryrun_monitor.py` — exit 0; output
reproduces every reported number (60% coverage, C1 FIRED, M1 4/4 AGREE, all NOT-YET-EVALUABLE
statuses with the same counts). The rerun appended a second dated entry to DRYRUN_LOG.md,
which is the instrument working as designed.

**Budget audit**: 0 backtested constructions, 0 optimization attempts — compliant. No hidden
experiments found (no new backtest result files; only the monitor rebuild and a scratch
`check_log.py`, disclosed in §11).

**Specification audit**: the assigned task was implemented exactly — no substitutions. The
one approximation (9-asset defensive sleeve proxied by BTC+ETH) is explicitly disclosed in
both the code comment and the report, and is immaterial for an all-flat window.

**Falsification audit**: no falsification condition triggered. M1 did not fire; S1/S3 did
not fire; S2/S4/S5 not yet evaluable (preconditions honestly reported with counts); C1 fired
but is by contract an ops escalation, not a parity verdict.

## 3. Audit findings (defects — none invalidate this window)

- **F1 (material, latent — must fix before the first trade)**: `mechanical_parity` and the
  M1 table derive the live side from the CURRENT open-positions snapshot and apply it to
  every historical bar. With a 0-row trades table this is exactly correct (live state was
  flat on every bar). But once any trade opens or closes, historical bars will be compared
  against *today's* positions — M1 and S2 verdicts on trade-bearing windows would be wrong.
  The live side must be reconstructed per-bar from trade `open_date`/`close_date`.
  (The daily-return section already reads close dates correctly; only the parity table has
  this defect.)
- **F2 (minor claim inaccuracy)**: report §2 and the notes lesson claim `shock_day_mask()`
  is "called (not just imported)". False for this run: `compute_shock_share()` returns at
  the <20-in-market-days precondition BEFORE the call (dryrun_monitor.py:313-314). The
  contract's OR-clause is satisfied, so the cycle stands, but the mask call path is
  unexercised until ≥20 in-market days accrue. Corrected in `strategy_research_notes.md`.
- **F3 (trivial)**: the monitor labels log timestamps as UTC, but `dryrun.log` is written
  in local time (UTC−7) — a ~7h skew on the realized-side freshness figure, well inside the
  1.5-bar tolerance. Would matter only if the tolerance is ever tightened.
- **F4 (accepted deviation)**: freshness tolerance implemented as 1.5 daily bars vs the
  contract's "within 1 daily bar" — necessary slack because a daily bar labeled 07-11 IS
  the freshest complete bar on 07-12; this cannot mask a #16-style staleness (which was 36+
  bars).

## 4. Reproducibility assessment

**YES.** Another researcher using only the repository can reproduce every conclusion: the
script is re-runnable with no arguments under `py -3.13`; data sources (feathers, sqlite DB,
log) are all in-repo; strategy filename, config, dataset, timeframe, pairs, and Python
version are recorded. No random seed is needed (fully deterministic computation). I did
reproduce it, plus an independent recomputation of the expected side from raw candles.
Caveat: coverage/freshness figures are time-anchored (`utcnow`), so later reruns will show
a longer window — the dated DRYRUN_LOG.md entries preserve each run's state.

## 5. Confidence

**HIGH.** Full independent rerun; raw-log recount; DB read via a separate path; expected
side recomputed with Reviewer-written code; protected-file mtimes and diffs checked. The
only untested code path is the shock-share computation beyond its precondition (F2) and the
stale-data exit path (verified by reading, not execution).

## 6. Failure classification

Not applicable — the experiment did not fail. (The prior cycle's failure, #16, was
Implementation Error + Protocol Violation; this reissue repaired it.)

## 7. Research debt (missing knowledge, not next-hypothesis proposals)

1. **M1 live-side per-bar reconstruction (F1)** — the instrument cannot yet render a valid
   parity verdict on any window containing a trade. This is the single highest-priority
   repair, and it is cheap while the trades table is still empty.
2. **The shock-share and stale-data code paths are unexercised** — nothing in the repo
   demonstrates they behave as written (a synthetic-input test would close this).
3. **The 9-asset defensive sleeve is proxied** — the true 80/20 stance line requires the
   9-asset universe in the periodic download.
4. **The 2026-06-11 → 2026-07-08 dry-run period is unrecorded** — the bot ran but no log
   survives; whether external evidence (exchange API history) can recover it is unknown.
5. **Coverage cannot reach 100% for the current 30-day window** — the 07-08/09 gap is
   permanent history; C1 will remain fired until enough covered days dilute it (earliest
   ~2026-07-18 for 80% of a trailing 10-day window; under the locked trailing-30d rule the
   gap stops binding 2026-08-07). The Task Scheduler registration (one-time operator
   action, block in `current_champion.md`) is the only guard against new gaps.

## 8. Engineer observations (carried forward unfiltered, from §12 of the report)

1. Task Scheduler registration is urgent — C1 fired; every unregistered day risks another
   48h coverage gap.
2. The flat regime will persist; the next informative event is either an entry signal
   (tests S2 immediately) or ~90 days elapsing without one. Neither needs code changes.
3. Add the 9-asset universe to the periodic data download to compute the true defensive
   sleeve rather than the BTC+ETH proxy.
4. The 409-line "Could not load markets" cluster (07-12 01:13–01:14) auto-recovered; if OKX
   rate-limiting recurs it could accumulate gaps that fire C1 even with the keepalive.
5. Consider extending the window start backward if external evidence of the 2026-06-11
   start period exists (exchange API history, alerts).
6. The instrument is a standing deliverable — future cycles should run it monthly and append
   to DRYRUN_LOG.md; consider formalizing as a scheduled task.

The Engineer also stated (§12.4 of the session report) that **S2 is the most informative
trigger** — the first expected entry signal is the highest-value single data point this
instrument can produce. Reviewer note: that moment is exactly when F1 must already be fixed.

## 9. Implications for nearby research directions (facts only)

- The forward-evidence lane is now open and valid for the first time: every day of coverage
  accrues selection-free evidence at zero n_trials cost, against locked, pre-registered
  triggers. All 98 backtest trials share one history; this is the only lane that doesn't.
- The current regime is the champion's documented weakest (3-of-3 gate unsatisfied since
  2025-10-09 per the recomputation — both pairs below SMA200 with EMA20<EMA50). Weeks of
  flat parity are the expected near-term output; per the contract, flat agreement is
  evidence, not absence of evidence.
- The structural map of the OHLCV dataset remains closed (index #16-#22); nothing in this
  cycle reopens any backtest direction.
- Meta-review counter stands at 24 completed cycles; the NEXT completed cycle reaches the
  25-cycle interval.

---

*Bookkeeping completed this session: iteration-log Reviewer entry appended (Iteration 19
verdict); research_index.md row #24 added and open-priority #1 updated; research_metrics.md
updated; strategy_research_notes.md lesson confirmed with one correction (F2);
current_champion.md Dry-Run History confirmation appended; hypothesis_bank.md H-ForwardParity
set to PARKED-OPEN / instrument ACCEPTED. All `(UNAUDITED — pending Reviewer)` tags resolved.
No promotion procedure was run (no PROMOTE verdict).*
