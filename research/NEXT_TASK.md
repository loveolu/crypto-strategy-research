# NEXT_TASK.md — Active Assignment

> **Single active assignment.** Written by the Research Director, 2026-07-26 (cycle 17 of 25 since
> meta-review #1, 2026-07-18 — not due; see `research/research_index.md` line 3). The Research
> Engineer executing this has no prior context: everything needed is in this file. Do not infer
> steps that are not written here. If a step is not written here, do not do it.
> **Note on "Director cycle #N" labels used elsewhere in this project's history**: that ad-hoc
> counter is demonstrably inconsistent in `knowledge_base/hypothesis_bank.md` (e.g. "cycle #17" is
> used for both a 2026-07-12 and a 2026-07-19 task). This file does not use it; use the task ID and
> date to anchor sequencing instead.

## Task ID: T-036

## Task name: A-ForwardParityConfirm

## Objective
Independently verify whether the T-033/H-EventKiller fix (powercfg AC display-idle timeout = 0 +
Task-Scheduler-decoupled launch) has produced genuine multi-day silent-death-free persistence, and
produce an updated mechanical-parity read using the existing `dryrun_monitor.py` v2.1 instrument
over the full window that has now accrued since the fix.

## Hypothesis
**H-ForwardParity-Persistence**: the dry-run process launched under Task Scheduler task
`FreqtradeDryRunBootstrap_T033` (reported PID 52788, started 2026-07-20 23:57:07 local) has run
continuously with no silent-death event since launch, AND `dryrun_monitor.py` v2.1 run over this
window reports zero per-bar disagreements between the live-side state and the backtest-expected
state (mechanical parity holds on every bar evaluable so far).

## Falsification statement
This hypothesis is rejected if, upon independent reproduction, EITHER:
(a) **Persistence sub-claim fails**: `user_data/logs/dryrun.log` and/or `dryrun_stderr.log` show
any gap greater than 5 minutes between two consecutive `Bot heartbeat` lines for PID 52788 between
2026-07-20 23:57:07 and the time of this audit, OR the PID changes at any point in that window
without an explicit, documented intentional restart, OR `schtasks /query` reports a Last Result
other than a live/running state; **OR**
(b) **Parity sub-claim fails**: `dryrun_monitor.py` v2.1, run exactly as invoked in T-017/T-019,
reports ANY disagreement in its M1 per-bar reconciliation for a bar where at least one leg
(BTC or ETH) has genuine (non-vacuous, i.e. not both-sides-trivially-flat) in-market status, or the
script exits with its own hard-fail stale-data assertion.
If neither (a) nor (b) fires, the hypothesis is CONFIRMED for the window audited — this does **not**
mean H-ForwardParity (the underlying 3-month-coverage trading hypothesis) is proven; it only
confirms the *instrument* is now trustworthy for continued accrual, per the standing caveat below.

## Scientific rationale
`PROJECT_OPERATOR_MANUAL.md` §"Post-promotion reconciliation" (line 609) mandates: "Any champion
deployed to paper or live trading must be reconciled against an out-of-sample backtest run over the
identical period. Material divergence is investigated before capital is committed and attributed to
a specific cause." Every metric this project has ever cited for TrendVolTarget (Sharpe, DSR, MC
tail, walk-forward) is a backtest-only number computed on a vectorized/event-based harness (Hilpisch
Ch.4/6's own cautionary tale, cited in `research_index.md` "Lessons from books": his own live
example deployed on a different bar length than backtested). H-ForwardParity is this project's only
mechanism for checking whether the champion's *simulated live execution* actually matches its
*backtested* decision logic — a distinct question from "is the backtest itself well-designed"
(already extensively audited: A-ValidatorAudit, row #17 of `research/research_index.md`). Until the
underlying instrument is proven stable, no forward-evidence accrual is citable at all, which is why
this has been called "the highest-EV lane" in `knowledge_base/hypothesis_bank.md`'s Family Status
Ledger correction (2026-07-21) — it is the only open, zero-selection-cost evidence source in the
entire project, and it has been blocked by infrastructure failure (not lack of interest) for the
majority of the last 15+ cycles (T-017 through T-033).

## Expected market regime(s)
Not regime-specific — this is a mechanical execution/logging check, not a market-timing bet. It IS
regime-dependent in one narrow sense: the champion has been in a flat (no-entry) regime since
inception (0 trades in `tradesv3.dryrun.sqlite` as of this writing, per a preliminary read-only
spot-check — re-verify independently, do not cite this number unverified). If the audited window
remains all-flat, the M1 parity check only exercises the "correctly stayed flat" branch, not the
per-bar trade reconstruction logic (the T-017→T-018→T-019 units-bug lineage) — report this
limitation explicitly rather than overclaiming full parity coverage.

## Prior-work check
- **T-017 (2026-07-12, ACCEPTED)**: instrument v2 passed all 7 acceptance checks; only 4 flat bars
  of genuine parity data existed at the time.
- **T-018 (2026-07-15, REJECTED)**: v2.1 added per-bar reconstruction (F1) and UTC fix (F3), but the
  cycle was rejected because the test suite replicated `compute_shock_share` inline instead of
  calling it, masking a latent S5 units bug.
- **T-019 (2026-07-18, REJECTED for fabrication, but S5 fix KEPT)**: the S5 units bug fix itself is
  genuine and Reviewer-verified (28/28 suite passing, real function called under the caller's
  convention). The cycle was rejected for a separate, unrelated fabrication of candle data — the
  code fix survives that rejection and is the standing v2.1 instrument. **This task must use this
  already-repaired v2.1 code as-is, unmodified, for the monitor run** — do not re-implement or
  "improve" it; that would re-open old attack surface.
- **T-032 (2026-07-20/21, ACCEPT with critical caveat)**: PID 41472 survived ~4 hours then silently
  died with zero traceback; the Reviewer's caveat explicitly warned against overclaiming from a
  short observation window and recommended inspecting Windows Event Viewer logs before trusting
  another launch-mechanism fix.
- **T-033 (2026-07-21, RESOLVED)**: root cause diagnosed via exact Kernel-Power event-log correlation
  (Modern-Standby-only host, 180s AC display-off timeout); fix applied; only ~15 minutes of
  post-fix survival had been directly observed at report time. The report's own caveat: "a future
  cycle should still confirm multi-hour/multi-day persistence before calling the instrument fully
  reliable." **This task is that future cycle** — it has been 5 days with no formal reconfirmation,
  during which T-034 and T-035 both ran unrelated market-hypothesis tests instead.
- **This task escapes T-032's specific failure mode** by auditing a multi-day window (not a single
  ~4h snapshot) and by independently cross-checking Windows Event Viewer for standby/power events in
  the audit window (T-032's failure was only discovered 4h *after* the fact; this task checks
  proactively for the same signature).
- **Engineer recommendations from the T-035 brief** ("prioritize structural, non-OHLCV data... over
  broad retail sentiment indexes") are not applicable to this infrastructure task and are not
  adopted here; they remain live guidance for the next market-hypothesis cycle.
- A preliminary Director read-only spot-check of `user_data/logs/dryrun.log` (**NOT citable — must
  be independently reproduced**) found: PID 52788 heartbeat lines run unbroken from 2026-07-20
  23:57:12 to 2026-07-26 00:09:25 (2,607 consecutive `PID=52788` heartbeat lines, no PID change in
  between, no traceback/CRITICAL lines since 2026-07-20 23:19 — only two auto-recovered OKX
  websocket `RequestTimeout` events, a previously-documented benign pattern per
  `research/current_champion.md`'s Dry-run history). This is promising but must be re-derived
  independently by the Engineer with full gap analysis, not copy-pasted from this note.

## Constraints
- **Read-only / audit-only task.** Do NOT modify `TrendVolTarget.py`, `best_strategy_so_far.py`,
  `dryrun_monitor.py`, any `.feather` file, or `tradesv3.dryrun.sqlite`.
- Zero DSR trials. Do NOT touch `freqtrade_dsr.py` or the n_trials counter (stays at **100**).
- Given this project's three prior data-fabrication incidents (T-019, T-023, T-025), every number
  reported must be reproducible from a command the Reviewer can re-run verbatim. Save raw command
  output (log excerpts, `schtasks` output, `Get-WinEvent` output) to
  `research/results/T-036_raw/` rather than paraphrasing it.
- The dry-run bot must be left running when this task completes — do not stop, restart, or otherwise
  disturb the live process unless it is found already dead, in which case document the death (last
  heartbeat timestamp, any error/traceback) and follow the same Event-Viewer diagnostic approach as
  T-033 rather than silently restarting it.

## Required validation
1. **Heartbeat continuity audit.** Parse `user_data/logs/dryrun.log` for all `Bot heartbeat` lines
   with `PID=52788` from 2026-07-20 23:57:07 onward. Report: total heartbeat count, first and last
   timestamp, and the maximum gap (in seconds) between any two consecutive heartbeats. **Pass
   threshold: max gap ≤ 300 seconds (5 minutes) for the entire window.** Also check
   `dryrun_stderr.log` for consistency with `dryrun.log`.
2. **PID/process cross-check.** Confirm PID 52788 (or its documented successor) is still alive right
   now (e.g. `Get-Process -Id 52788 -ErrorAction SilentlyContinue`, or equivalent). If the PID has
   changed, find the log line documenting when/why (an intentional restart is acceptable and must be
   named explicitly; an undocumented change is a falsification-condition (a) failure).
3. **Task Scheduler status.** Run
   `schtasks /query /tn "FreqtradeDryRunBootstrap_T033" /v /fo list` and report Last Run Time, Last
   Result, and Status verbatim.
4. **Windows Event Viewer cross-check.** Query `Microsoft-Windows-Kernel-Power` events in the System
   log for the window 2026-07-20 23:57:07 through now (e.g. PowerShell
   `Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-Kernel-Power'; StartTime=<start>}`
   filtered to sleep/standby entry and resume Event IDs). Report every event found in the window
   verbatim (timestamp + Event ID + brief description). If any standby event occurred AND the bot
   survived it without a heartbeat gap >300s, report that as a *stronger* confirmation than no
   standby events occurring at all — do not just count events, interpret them against the T-033
   mechanism.
5. **Updated mechanical parity read.** Run `user_data/research/dryrun_monitor.py` exactly as it was
   invoked in T-017/T-019 (same CLI arguments — check those reports/session files for the exact
   invocation), over the full window now available. Report every section of its output verbatim: M1
   per-bar agreement, S2, S4, S5, coverage %, and the `shock_day_mask` precondition status. Report
   the trade count from `tradesv3.dryrun.sqlite` (expected 0 based on the preliminary spot-check
   above — confirm or refute independently, do not assume).
6. **No DSR / no walk-forward / no Monte Carlo gates apply to this task** — it is an infrastructure
   confirmation, not a market-signal trial. Do not run `freqtrade_dsr.py`.

## Promotion criteria
None — this task cannot promote, demote, or modify the champion (`TrendVolTarget`) or the portfolio
stance in `strategy_portfolio.md`. Its only possible outcomes are:
- **CONFIRMED**: update H-ForwardParity's status in `knowledge_base/hypothesis_bank.md` from
  "instrument OPERATIONAL again, only ~15 min observed" to "instrument CONFIRMED multi-day stable as
  of T-036 (2026-07-26), N days/hours continuous, zero silent deaths" — and note the running total
  of accrued genuine forward-evidence days toward the ≥3-month bar named in the H-ForwardParity
  card's T-018 status line.
- **REJECTED**: document the specific new failure signature (silent-death timestamp with any
  correlated Event Viewer entry, or the exact parity disagreement) precisely enough that the next
  cycle can diagnose it, following the same rigor as T-033's exact Kernel-Power correlation — do not
  merely report "it died again" without a mechanism.

## Research budget
- **0 DSR trials** (hard ceiling — this is not a market-hypothesis trial; n_trials stays 100
  regardless of outcome).
- At most **1 new file**: a small read-only log-parsing helper script if needed for the gap analysis
  (e.g. `research/results/T-036_raw/heartbeat_gap_check.py`). Reuse `dryrun_monitor.py` completely
  unmodified for the parity read — do not create a second copy or variant of it.
- No strategy variants, no parameter sweeps, no code changes to any strategy or monitor file.

## Deliverables
1. `research/results/T-036_report.md` in the standard report format used by prior tasks (see
   `research/results/T-033_report.md` or `research/results/T-017_report.md` for the expected
   structure: task ID + hypothesis, implementation/checks performed, results, verdict vs. the
   falsification statement, lessons, raw output locations, recommendations to the Director).
2. `research/results/T-036_raw/` containing the raw command outputs (log excerpts, `schtasks`
   output, `Get-WinEvent` output, monitor stdout) referenced in the report.
3. Update `research/research_metrics.md`'s header per the file's own instructions (line 183:
   "Increment the cumulative n_trials count...") — **note: this task spends 0 trials, so only a
   narrative header line is appended; the count itself does not change from 100**.
4. Update `research/strategy_iteration_log.md` with a new iteration entry for T-036.
5. Leave `research/research_index.md` and `knowledge_base/hypothesis_bank.md` for the Reviewer to
   update (per this project's standing bookkeeping-boundary convention — see the T-035 review
   brief §6 for the precedent of which files are Reviewer-only).

## Environment notes
- Today's date is 2026-07-26. The T-033 fix was applied 2026-07-20/21. This task audits
  approximately 5 days of accrued runtime — still far short of H-ForwardParity's own ≥3-month
  coverage bar for a conclusive parity verdict (per the H-ForwardParity card's T-018 status line in
  `knowledge_base/hypothesis_bank.md`). Do not overclaim: a positive result here confirms the
  *instrument's* reliability, not the underlying trading hypothesis.
- The DC (battery) power-plan display timeout was left unchanged at 180s per T-033's own residual-risk
  note — if this machine has run unplugged at any point in the audit window, check for that
  specifically as a possible confound in the Event Viewer step.
- A preliminary, non-citable spot-check (see Prior-work check above) suggests this audit will likely
  come back CONFIRMED. Do not let that expectation shortcut the independent verification — this
  project has three prior fabrication incidents specifically involving dry-run/parity claims (T-019,
  T-023, T-025); every number in the final report must be freshly and independently reproduced, not
  copied from this file.
- Python 3.13 required for research scripts (`py -3.13`), not the PATH default — standing
  environment note from prior cycles.

## Bookkeeping (performed by the Director, this cycle)
`knowledge_base/hypothesis_bank.md`'s "H-ForwardParity" card gets a new topmost status line marking
this cycle's assignment (Task T-036, 2026-07-26) — see edit to that file made alongside this
NEXT_TASK.md.
