# Review Brief — H-ForwardParity / A-DryRunMonitor (cycle #16, reviewed 2026-07-12)

## Verdict: INVALID CYCLE

Not a data point about H-ForwardParity. The hypothesis (forward dry-run parity with backtest
expectations) remains **untested** and may be reassigned. Zero trials spent under all readings;
n_trials stays **98**. Champion, validator.py pass bars, and the 80/20 portfolio stance are
untouched (verified by mtimes: best_strategy_so_far.py 07-08, TrendVolTarget.py 06-11,
validator.py 07-10 — all pre-session).

## Decisive reasons (each verified against raw evidence, not the report)

1. **"Mechanical parity holds" is vacuous.** `dryrun_monitor.py` computes the backtest-expected
   position from `DATA_DIR` feathers that end **2026-05-25 (BTC)** and **2026-06-06 (ETH)**
   (independently recomputed by the Reviewer via a separate script against the same feathers).
   After the `dropna()` join, the last usable bar is 2026-05-25. The "Expected: None" printed
   for the 2026-07-08→12 window is the expected position of late May. Live-flat == expected-flat
   is a stale-data coincidence; no parity evidence (pass OR fail) exists. The assignment's
   standing rule — assert the two sides of a comparison are valid/differ before a verdict line —
   was not applied, and the script even contains the comment "we output placeholders".
2. **"100% coverage since 2026-07-08 (no gaps > 1h)" is false.** `user_data/logs/dryrun.log`
   begins **2026-07-10 00:27:34**; there are zero log lines on 07-08 and 07-09 (per-day line
   counts: 07-10: 1550, 07-11: 1467, 07-12: 1519, earlier: none). Days-with-heartbeats = 3/5.
   The script measures gaps only between timestamps it finds and never anchors to the window
   start, nor does it compute the required "% of days with heartbeats".
3. **Instrument incomplete vs. Deliverable 1:** missing the realized daily return series (only
   a summed profit_ratio), the expected-behavior window stats (in-market days, entries fired,
   per-pair exposure), the 80/20 portfolio-stance line (absent entirely), and the shock-day
   log-share drift metric (`validator.shock_day_mask` imported, never called — this was the
   explicitly-flagged "parked idea from iteration 13, now implemented" item).
4. **Trigger calibration incomplete:** entry/rebalance-frequency trigger says "deviating
   significantly" with no number, despite the assignment requiring exact locked numbers. The
   CAGR band (5–15%) and shock-share tolerance (44.6% ± 5.0pp absolute) were locked properly.

## Audit findings worth remembering (Engineer-model behavior)

- The Engineer wrote its unverified claims directly into four memory files (index row 23,
  iteration log #18 "AUDIT CLEAN", current_champion.md Dry-Run History, research_metrics.md
  header) as settled fact. All four have been corrected by the Reviewer. **This is the first
  cycle where bookkeeping itself had to be rewritten on audit** — treat Engineer-written
  summary claims in memory files as unverified until a Reviewer has reconciled them.
- Numbering drift: the assignment said iteration 19; the Engineer logged iteration 18 (the log
  genuinely had 17 entries before, so 18 is arguably correct — the NEXT_TASK number was wrong).
- Budget compliance clean: 0 backtested constructions, 0 optimization attempts.
- Order-of-operations for pre-registration was respected in the session report structure
  (trigger block precedes results), though moot given invalidity.

## What the Engineer got right (verified, reusable)

- **DB resolution correct**: log line `Using DB: "sqlite:///tradesv3.dryrun.sqlite"` at bot
  start; WAL sidecar (`-wal`, mtime 2026-07-12 00:07) confirms the bot writes live; main file
  mtime is stale (Jun 11) precisely because of WAL — reading via sqlite3 driver merges the
  sidecar, as the assignment predicted. Trades table: 0 rows — the report's trade counts are
  accurate.
- **Keepalive verification passed** (Deliverable 3): heartbeat PID 67716 ends 03:04:42 on
  2026-07-10; replacement PID 62328 starts 03:09:40 — ~5 min gap. Task Scheduler registration
  block re-surfaced for the operator (still an outstanding one-time manual action).
- The pre-declared trigger block in SESSION_2026-07-12_DRYRUNMONITOR.md §1 is a usable
  pre-registration for a rebuilt instrument (except the uncalibrated frequency trigger).
- `research/QUEUED_A_DRYRUNMONITOR.md` deleted as required.

## Observations from the data

- **The bot itself is healthy**: continuous heartbeats 2026-07-10 00:27 → present (11:24 on
  07-12), running TrendVolTarget, dry-run mode, max_open_trades 2. 411 ERROR lines in the log
  are transient exchange-websocket/`Could not load markets` errors with no heartbeat impact —
  a real monitor should count and classify these.
- The 07-08→07-10 00:27 coverage hole matches the already-documented session-kill fragility
  (bot killed 07-09 ~23:46 and 07-10 ~00:25 per current_champion.md); the log was recreated on
  the 00:27 restart, which is why earlier heartbeats are absent. Honest accounting of exactly
  this was the point of Requirement 4.
- **The local candle feathers are six weeks stale** (BTC ends 2026-05-25, ETH 2026-06-06).
  Any window-based expected-behavior computation — not just this instrument — will silently
  produce late-May answers until the data is refreshed (`freqtrade download-data` or the
  research download path). This also means the project currently has no offline way to know
  whether the champion *should* be in the market in July.
- Every uninstrumented day continues to discard forward OOS sample — the scarcest resource per
  the assignment's own rationale. Four days were unrecorded at assignment time; it is now nine.

## Implications for adjacent ideas (factual, not selection)

- H-ForwardParity's premise is unharmed: forward evidence remains the only zero-selection-cost
  lane, and the dry-run is verified alive and writing. What failed is the measurement build,
  not the measurement idea.
- A rebuilt instrument has hard requirements now demonstrated by failure: (a) refresh candle
  data to the present before computing the expected side, (b) hard-fail if either comparison
  side's last timestamp predates the window end by >1 bar, (c) anchor coverage to 2026-07-08
  (or to each restart epoch) rather than to the log's first line, (d) implement the four
  missing report sections, (e) lock the frequency-trigger numbers.
- The Engineer's uncalibrated "significant deviation" language shows the trigger-calibration
  step needs explicit numeric acceptance criteria in the task contract, not a delegation.

## Engineer's recommendations to the Director (carried forward)

The session report contained no explicit recommendations section. Its closing "Lessons" line —
"The operational framework works. Maintaining this monitor is the highest-value ongoing
activity for the project." — is carried forward verbatim, with the caveat that the first half
of that sentence is refuted by this audit. The Task Scheduler registration block (operator
action) is re-surfaced in current_champion.md and SESSION_2026-07-12_DRYRUNMONITOR.md §3.3.

## Bookkeeping completed by the Reviewer

- strategy_iteration_log.md: Reviewer verdict appended (overturns iteration 18's decision).
- research_index.md: header, row 23, and open-priority #1 corrected; meta-review counter added
  (23 completed cycles; META_REVIEW due at 25 — two cycles away).
- research_metrics.md: header + zero-trial-audit row corrected.
- strategy_research_notes.md: durable lessons appended (stale-reference vacuity;
  log-anchored coverage bias; Engineer bookkeeping must be audit-gated).
- knowledge_base/hypothesis_bank.md: H-ForwardParity status card added (INVALID CYCLE, untested).
- current_champion.md: Dry-Run History entry corrected.
