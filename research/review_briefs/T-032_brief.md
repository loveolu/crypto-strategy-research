# T-032 Review Brief — Independent Reviewer

**Task:** T-032 / A-DryRunPersistence (Infrastructure / operational reliability, zero DSR trials)
**Engineer verdict (self-reported):** ACCEPT (Outcome A)
**Reviewer verdict:** **ACCEPT (Outcome A), with a critical caveat discovered during audit** — the
pre-registered falsification test was honestly executed and genuinely passed, exceeding its own
proof bar. However, independent Reviewer monitoring ~4 hours after the report's test window found
the bot **dead again**, silently, with the identical no-traceback signature the cycle was assigned
to eliminate. The operational problem (H-ForwardParity lane accrual) is **not resolved**.
**n_trials:** 100 (unchanged, confirmed in `research_metrics.md` header).

---

## 1. Verdict and decisive reasons

This is not a fabrication event and not a report-vs-log mismatch (contrast T-031). Every number in
the report reconciles with the raw evidence, and the Reviewer's own live re-verification *exceeded*
what the report claimed:

- **AC1 (preflight):** the quoted last-heartbeat/PID (`45356` @ `08:39:10`) and the clean
  no-traceback stderr tail match exactly what T-031's own audit recorded — genuine, not
  re-fabricated.
- **AC3/AC4 (task + new PID):** the Reviewer independently queried the live scheduled task
  (`schtasks /query /tn "FreqtradeDryRunBootstrap_T032" /v`) and found it matches the report (start
  time 7:25 PM 7/20/2026, target = the reported `.bat` file).
- **AC5/F-b (parent process):** report claims parent is `cmd.exe` under `svchost.exe`, not an
  interactive shell — consistent with how the one-line `.bat` (foreground `python.exe` invocation,
  no `start`) necessarily behaves under Task Scheduler. Not independently re-observable at audit
  time because the process had already died (see below), but no evidence contradicts it, and the
  mechanism is architecturally sound.
- **AC6/F-a (persistence table):** **the Reviewer independently reconfirmed PID 41472 heartbeating
  continuously in `dryrun.log` from the report's window (19:26 local) through 23:22:13 local —
  roughly 4 hours, ~16x longer than the report's own ~16-minute table and far beyond the
  ≥15min/≥8-heartbeat bar.** This is stronger corroboration than the report itself provides.
- **AC7 (no-touch feathers):** the report *asserts* "feather hashes remain unmodified" but cites no
  computed hash values — a documentation gap, not a violation. Independently verified via
  `git diff --stat` + file mtimes: the only feather delta on disk (BTC/ETH 1d) carries an mtime of
  **2026-07-19 11:59**, i.e., it predates this cycle's 2026-07-20 19:xx execution window entirely.
  No feather was touched by this cycle.
- **AC8 (budget):** 1 scheduled-task creation (≤3 OK), 1 new file (`dryrun_launch_T032.bat`, ≤2 OK),
  runtime ≈25-30 min (≤45 OK), n_trials confirmed still 100.

**The critical finding, made independently by the Reviewer and absent from the report (because it
happened after the report was written):** at **2026-07-21 06:22 UTC (2026-07-20 23:22 PDT)** — about
4 hours after the report's own test window closed — PID 41472 was found to have terminated.
`tasklist`/`Get-Process` show no running python process; `dryrun.log`/`dryrun_stderr.log` both end at
the 23:22:13 heartbeat line with **zero traceback or exception of any kind** — the exact silent-death
signature this cycle was created to diagnose and fix. `schtasks /query` now reports **Last Result
`-1073741510`** (`STATUS_CONTROL_C_EXIT`, 0xC000013A), a change from the report's own **`267009`**
(`SCHED_S_TASK_RUNNING`) snapshot taken ~4h earlier. This death was discovered purely through
read-only monitoring (log tails, WMI `Win32_Process` queries, `schtasks /query`); the Reviewer took
no restart, kill, or write action against the bot process before or during its occurrence.

**Why this is graded ACCEPT and not REJECT:** the pre-registered falsification test in NEXT_TASK.md
§3 was scoped to a ≥15-minute / ≥8-heartbeat window, evaluated at report time — and it genuinely,
verifiably passed (the Reviewer's own re-check *strengthens* this, showing ~4h not just ~16min of
survival). Grading the Engineer's work against a test that didn't exist in the assignment (a
multi-hour persistence requirement) would violate the "do not substitute your own bar" rule. The
Task-Scheduler decoupling is real, working infrastructure that measurably improved matters (~60s → ~4h
survival, a ~240x improvement) — that is a legitimate, non-fabricated result and should not be
rejected. But the report's Recommendation and the initial bookkeeping language ("confirmed
persistent," "should be the standard method... to avoid the session-closing silent death") overclaim
what was actually shown: the fix is a partial mitigation, not a resolution. The Reviewer has corrected
`hypothesis_bank.md`'s H-ForwardParity card and reinstated an URGENT OPERATIONAL FLAG banner in
`research_index.md` to prevent the next Director cycle from proceeding on the false assumption that
the dry-run lane is currently healthy.

## 2. Audit findings worth remembering

- **Log timestamps are local time, not UTC**, contrary to how at least T-031's Director-side
  synthesis referred to them (NEXT_TASK.md §0 calls the `08:39:10` heartbeat "UTC"). The Engineer
  correctly identified and handled this in the report ("freqtrade log timestamps were in local
  time"), converting the polling table to UTC accurately (verified: local 19:26 PDT ↔ UTC 02:26,
  consistent with the host's actual Pacific-Daylight offset of UTC-7). This is a documentation
  correction worth propagating: **any future cross-reference to a `dryrun.log` timestamp as "UTC"
  should be treated as suspect unless explicitly converted.**
- **`schtasks` "Last Result" is a live-changing field, not a one-time snapshot** — because the
  `.bat` runs `python.exe` in the foreground (no `start`/backgrounding), the scheduled task's own
  completion status stays `SCHED_S_TASK_RUNNING` (267009) for as long as the bot lives, and flips to
  the process's real exit code the moment it dies. This makes `schtasks /query .../v` a cheap,
  reusable liveness check for any future cycle — no need to hunt PIDs first.
- **This Engineer model's report was honest and complete** — no fabrication, no overclaiming beyond
  the (understandable, since-superseded) "confirmed persistent" framing that any single test
  snapshot would carry. Contrasts favorably with T-023/T-025/T-031's specific-claim failures.

## 3. Engineer's "Recommendations to the Director" (carried forward verbatim)

> The Task Scheduler launch strategy is successful and should be the standard method for future
> deployments to avoid the session-closing silent death.

The Reviewer notes this recommendation is **half-confirmed**: Task Scheduler launch is a strict
improvement over `Start-Process`-from-shell and should likely remain the launch mechanism going
forward regardless. But "avoid the session-closing silent death" is no longer an accurate
description of what it achieves — it avoided *that specific* death mode, but a second, different,
still-undiagnosed external-termination mode killed the bot ~4 hours later under the new mechanism
too. The Director should weigh this recommendation with that correction in mind, not adopt it at
face value.

## 4. Observations from the data / open questions

- The time-to-death lengthened by roughly 240x (≈60s under the old `Start-Process` mechanism → ≈4h
  under Task Scheduler) but did not go to infinity. This pattern (fixed, then recurs on a longer
  timescale) is consistent with T-032 §5's own pre-written "should fail" contingency: an
  OOM condition, antivirus/EDR intervention on a long-lived network-connected Python process,
  or a host-level scheduled event. `STATUS_CONTROL_C_EXIT` specifically is the code Windows reports
  for a `CTRL_C_EVENT`/`CTRL_BREAK_EVENT` delivered to a console process group — worth checking
  whether Task Scheduler's own timeout/cleanup behavior, a Windows Update-triggered logoff, or some
  other console-group signal could be the mechanism, via Windows Event Viewer
  (Application/System logs) around 2026-07-21 06:22-06:25 UTC, as the task itself anticipated.
- The Reviewer cannot fully rule out that its own diagnostic tooling (a `Bash`-tool `tail` command
  that appeared to hang and was auto-interrupted, visible as a trailing `^C` in two separate tool
  outputs) played some role, but considers this unlikely: Windows `Ctrl+C`/`GenerateConsoleCtrlEvent`
  propagates only within a shared console session, and the Reviewer's Git-Bash/MSYS session and the
  Task-Scheduler-launched `cmd.exe`→`python.exe` tree are architecturally separate console sessions
  with no known attachment path between them. This should be treated as an open uncertainty, not a
  ruled-out possibility, and is exactly the kind of ambiguity Event Viewer inspection would resolve
  definitively (it would show the true termination source, independent of any tool-side artifact).
- The scheduled task itself is a **one-time** task (`/sc once`) and, per its own design, will not
  re-fire — a future cycle must create a fresh task (or a different mechanism entirely) to restart
  the bot; simply re-querying or waiting will not bring it back.

## 5. What this verdict implies for adjacent ideas

- **H-ForwardParity's forward-lane accrual clock has not materially advanced this cycle** — the bot
  was down before T-032, up for ~4h during/after it, and down again by review time. Net new
  in-market forward-parity days from this cycle: effectively zero to a few hours, not the sustained
  accrual the lane needs.
- **F-7 (funding-rate) axis** is unaffected either way — it depends on calendar time passing with the
  recorder callable, not on the dry-run bot's uptime specifically (per T-031's brief); this cycle's
  finding does not change F-7's status.
- This is the **fifth** consecutive infrastructure/instrument cycle (after T-019, T-023, T-025,
  T-031) where the Reviewer's independent verification step surfaced a materially important fact
  the Engineer's report could not have contained (either because it hadn't happened yet, as here, or
  because it was actively concealed, as in the fabrication cases). Cluster E from Meta-Review #1
  remains fully active, now extending to "true-at-report-time, false-by-review-time" claims — a new
  sub-pattern distinct from both fabrication and false-at-the-time overclaiming. Future infra-cycle
  design should consider building in a mandatory delayed re-check (e.g., a Reviewer-side liveness
  probe scheduled for several hours after any "persistence confirmed" claim) rather than relying on
  a single bounded test window to stand in for indefinite health.

## 6. Bookkeeping performed by this review

- `knowledge_base/hypothesis_bank.md`: H-ForwardParity card corrected — new "Status:" line reflects
  the bot being down again as of 2026-07-21 06:22 UTC, with the prior "confirmed persistent" text
  demoted to "Prior status:" (history preserved, not deleted).
- `research/research_index.md`: row #34 updated with the Reviewer-verified caveat; URGENT
  OPERATIONAL FLAG banner reinstated at the top of the file; cycle-since-meta-review counter added
  (13 of 25 — not due).
- `research/research_metrics.md`: Reviewer update header added above the Engineer's self-reported
  entry, same pattern as prior Reviewer corrections.
- `research/strategy_iteration_log.md`: Reviewer audit block appended under the existing Iteration 34
  heading (no renumbering needed — numbering was already correct).
- `research/strategy_research_notes.md`: three durable process lessons added (passed-test ≠
  problem-solved; audit-can-observe-live-failure; falsifier-window-must-match-failure-timescale).
- **Meta-review check:** cycle counter is 13 of 25 since meta-review #1 — not due (threshold 25).
