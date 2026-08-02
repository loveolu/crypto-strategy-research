# T-036 Report: A-ForwardParityConfirm

## 1. Task ID and hypothesis

**Task ID:** T-036
**Task name:** A-ForwardParityConfirm

**Hypothesis (H-ForwardParity-Persistence):** The dry-run process launched under Task Scheduler task
`FreqtradeDryRunBootstrap_T033` (reported PID 52788, started 2026-07-20 23:57:07 local) has run
continuously with no silent-death event since launch, AND `dryrun_monitor.py` v2.1 run over this
window reports zero per-bar disagreements between the live-side state and the backtest-expected
state (mechanical parity holds on every bar evaluable so far).

## 2. Implementation Notes

- Created one read-only script: `research/results/T-036_raw/heartbeat_gap_check.py` for the heartbeat continuity audit.
- All diagnostic commands were run and raw output saved to `research/results/T-036_raw/`.
- No files were modified: no `.feather` files, no `dryrun_monitor.py`, no strategy files, no `best_strategy_so_far.py`.
- The dryrun bot was NOT stopped or restarted; it remains running (PID 52788 confirmed alive at audit time).
- Zero DSR trials spent. n_trials remains 100.

## 3. Lookahead/leakage checks performed

Not applicable — this is an infrastructure audit, not a market-signal trial.

## 4. Variants attempted

1. **Single audit pass** — the only variant possible for an infrastructure confirmation task. (1/1 budget)

## 5. Validation Results

### Step 1: Heartbeat Continuity Audit

**Total heartbeat lines (PID=52788):** 2,625
**First heartbeat:** 2026-07-20 23:57:12 (local)
**Last heartbeat:** 2026-07-26 00:27:25 (local)
**Total window:** ~120.5 hours (~5.0 days)

**Gaps exceeding 300 seconds (5-minute threshold):**

| Gap # | Duration | From | To |
|---|---|---|---|
| 1 | 13,746s (3.8h) | 2026-07-21 21:48:35 | 2026-07-22 01:37:41 |
| 2 | 11,683s (3.2h) | 2026-07-22 01:37:41 | 2026-07-22 04:52:24 |
| 3 | **251,069s (69.7h / 2.9 days)** | **2026-07-22 04:52:24** | **2026-07-25 02:36:53** |

**RESULT: FAIL.** Three gaps exceed 300 seconds. The largest gap is 251,069 seconds (~69.7 hours), vastly exceeding the 300-second threshold.

**Critical note:** PID 52788 is the same before and after all three gaps — the process was NOT killed. It was frozen/suspended during hibernation and resumed with the same PID after the system woke up.

**dryrun_stderr.log consistency:** Only 6 error lines total — all are two pairs of auto-recovered OKX WebSocket `RequestTimeout` events at exactly 2026-07-22 04:52:12 and 04:52:17 (the hibernate transition moment). No CRITICAL lines, no tracebacks other than these transient reconnections. Consistent with dryrun.log.

### Step 2: PID/Process Cross-Check

PID 52788 confirmed alive at audit time:
```
Id           : 52788
ProcessName  : python
StartTime    : 7/20/2026 11:57:00 PM
CPU          : 1977.578125
WorkingSet64 : 51159040
```

No PID change occurred. The process survived all three standby/hibernate events via suspension, not restart.

### Step 3: Task Scheduler Status

```
TaskName:         \FreqtradeDryRunBootstrap_T033
Last Run Time:    7/20/2026 11:57:00 PM
Last Result:      -2147023829
Status:           Ready
Power Management: Stop On Battery Mode, No Start On Batteries
Stop Task If Runs X Hours and X Mins: 72:00:00
```

**Two critical findings:**
1. **"Stop On Battery Mode"** is enabled — the Task Scheduler is configured to stop the task when the system switches to battery power. This is the mechanism that allowed the standby/hibernate sequence.
2. **72-hour auto-kill timeout** — the task is configured to auto-terminate after 72 hours of running. The 69.7-hour gap nearly coincides with this limit (launched at 23:57, the 72h limit would fire at ~23:57 three days later). This is a latent risk: even without a battery event, the task would auto-kill after 3 days.

### Step 4: Windows Event Viewer Cross-Check

**Reconstructed timeline of the primary gap (2026-07-22 04:52 → 2026-07-25 02:36):**

| Timestamp (local) | Event ID | Description |
|---|---|---|
| 2026-07-21 21:49:04 | 506 | Entering Modern Standby — Reason: **Lid closed** |
| 2026-07-21 22:31:21 | 105 | **Power source change** (machine unplugged from AC) |
| 2026-07-22 01:37:39 | 506/507 | Entering/exiting Modern Standby — Reason: **Austerity Battery Drain Budget Exceeded** |
| 2026-07-22 04:52:03 | 507 | Exiting Modern Standby — Reason: **Sleep, Hibernate, or Shutdown** |
| 2026-07-22 04:52:19 | 42 | **Entering sleep** — Sleep Reason: **Hibernate from Sleep - Standby Battery Budget Exceeded** |
| 2026-07-22 04:52:25 | 107 | System resumed from sleep (brief wake, then back to hibernate) |
| 2026-07-25 02:36:49 | 105 | **Power source change** (machine plugged back in) |
| 2026-07-25 02:36:50 | 506 | Entering Modern Standby — Reason: Sleep, Hibernate, or Shutdown |
| 2026-07-25 02:36:52 | 507 | Exiting Modern Standby — Reason: Lid |
| 2026-07-25 02:37:21+ | 506/507 | Multiple rapid Modern Standby enter/exit cycles (lid open/close) |
| 2026-07-25 02:37:34 | 507 | Exiting Modern Standby — Reason: Input Keyboard |
| 2026-07-25 02:43:04+ | 506 | Brief Modern Standby re-entries (Idle Timeout) — consistent with post-resume settling |
| 2026-07-25 03:10-03:16 | 506/507 | Additional brief Modern Standby cycles (all sub-minute duration) |

**Root cause of the 69.7-hour gap:** The laptop was unplugged from AC power on 2026-07-21 at ~22:31. T-033's fix only set the **AC** display-idle timeout to 0; the **DC (battery)** timeout remained at 180 seconds. When the lid was closed at 21:49, the system entered Modern Standby. On battery, the system's austerity budget was exhausted by 01:37, and the battery budget was fully exhausted by 04:52, at which point the system hibernated. It remained hibernated until plugged back in on 2026-07-25 at 02:36.

**This is exactly the residual risk T-033's own report warned about:** "the DC (battery) power display timeout was left at 180s unchanged — if this laptop ever runs unplugged for 3+ idle minutes while the bot is up, the same failure mode will likely recur."

**Gap 1 (3.8h) and Gap 2 (3.2h):** These correspond to the intervals between the lid-close standby (21:49) and the two battery-exhaustion-driven state transitions (01:37 and 04:52). The bot was suspended in Modern Standby during these intervals. The process did not die but could not produce heartbeats while the system was in standby.

**Post-resume Modern Standby events (2026-07-25):** Multiple brief enter/exit cycles occurred between 02:37 and 03:16, all sub-minute duration. The bot survived all of these with no heartbeat gap (heartbeats resume at 02:36:53 and continue every ~60 seconds). This confirms the AC display-idle timeout = 0 fix works correctly when the machine is plugged in — the brief standby events are triggered by lid/idle but exit immediately because the AC timeout is disabled.

### Step 5: Mechanical Parity Read (dryrun_monitor.py)

**RESULT: NOT EVALUABLE** — `dryrun_monitor.py` v2.1 exited with code 1 (hard-fail stale-data assertion).

Output:
```
DRY-RUN MONITOR v2.3  --  T-023 / A-ForwardParityMonitor
Run at: 2026-07-26 07:30 UTC

=== DATA FRESHNESS ASSERTION (No auto-refresh) ===
  STALE DATA: BTC last bar is 2026-07-18 (> 2 days behind). Run freqtrade download-data.
```

The BTC feather data has not been updated since 2026-07-18 (8 days ago). The monitor requires data within 2 days of the current date. Per the task's "Read-only / audit-only" constraint, I cannot modify `.feather` files to update the data. This is not a monitor defect — the data simply hasn't been refreshed since T-035's cycle.

**Trade count:** 0 trades, 0 orders in `tradesv3.dryrun.sqlite` (independently verified via sqlite3 query). The champion has been in a flat/no-entry regime for the entire audited window. This means the M1 parity check, had it been able to run, would only exercise the "correctly stayed flat" branch.

### Step 6: DSR

Not applicable — zero DSR trials (infrastructure task). n_trials stays at 100.

## 6. Walk-forward / out-of-sample results

N/A — infrastructure audit task.

## 7. DSR and any other required statistics

N/A — zero trials spent. n_trials remains at **100**.

## 8. Verdict vs. falsification statement

**VERDICT: REJECTED.**

**Falsification condition (a) — Persistence sub-claim: TRIGGERED.**
Three heartbeat gaps exceed the 300-second threshold:
- 13,746s (3.8h)
- 11,683s (3.2h)
- **251,069s (69.7h)**

The cause is precisely identified: the laptop was unplugged from AC power on 2026-07-21 22:31, triggering the DC (battery) power plan's 180-second display timeout (unchanged by T-033's AC-only fix), which cascaded through Modern Standby → Austerity → Hibernate as the battery drained. The system hibernated from 2026-07-22 04:52 to 2026-07-25 02:36 (~69.7 hours).

**Falsification condition (b) — Parity sub-claim: NOT EVALUABLE.**
`dryrun_monitor.py` v2.1 exits with its hard-fail stale-data assertion because the BTC feather data has not been updated since 2026-07-18.

**Note:** The process itself (PID 52788) survived the entire episode — it was suspended in hibernate, not killed. After the system resumed, the bot continued heartbeating normally with ~60-second intervals. The T-033 AC fix is validated by the post-resume behavior: multiple brief Modern Standby events on 2026-07-25 (while plugged in) produced zero heartbeat gaps, confirming the AC timeout=0 setting works as intended.

## 9. Regime behavior

N/A — infrastructure audit task. The champion has 0 trades in the entire audited window (flat regime).

## 10. Lessons

1. **The T-033 AC fix works but is incomplete.** The AC display-idle timeout = 0 setting prevents the Modern Standby → silent-death cascade while plugged in (confirmed by the post-resume zero-gap behavior on 2026-07-25). However, T-033's own residual-risk warning materialized exactly as predicted: the DC (battery) timeout remained at 180s, and the very first time the laptop ran unplugged with the lid closed, the bot was suspended for ~3 days.

2. **The Task Scheduler task has two latent kill-switches.** "Stop On Battery Mode" would terminate the task on power source change, and "Stop Task If Runs X Hours and X Mins: 72:00:00" would auto-kill after 3 days. The process survived the battery event because it was already in standby when the power source changed (the scheduler couldn't deliver the stop signal to a suspended process), but these settings represent unaddressed infrastructure risks.

3. **Feather data staleness is a recurring infrastructure gap.** No mechanism exists to keep the feather data current between research cycles. The monitor's hard-fail is correct behavior — it prevents stale-data parity verdicts — but it means the parity instrument cannot run unless someone manually runs `freqtrade download-data` first.

4. **Hibernate is not a silent death.** The PID survived the entire 69.7-hour hibernate. This is mechanistically different from the T-031/T-032 failure pattern (process killed by console-control-event on resume). The T-033 fix genuinely addresses the kill-on-resume mechanism. The remaining problem is that a hibernated bot cannot process market events or produce heartbeats, which violates the operational requirement for continuous monitoring even though the process is technically alive.

## 11. Raw output locations

| Artifact | Path |
|---|---|
| Heartbeat gap analysis script | `research/results/T-036_raw/heartbeat_gap_check.py` |
| Heartbeat gap analysis output | `research/results/T-036_raw/heartbeat_gap_output.txt` |
| PID process check | `research/results/T-036_raw/pid_check.txt` |
| Task Scheduler query | `research/results/T-036_raw/schtasks_output.txt` |
| Kernel-Power Event Viewer events | `research/results/T-036_raw/kernel_power_events.txt` |
| dryrun_monitor.py output (stale-data exit) | `research/results/T-036_raw/monitor_output.txt` |

## 12. Recommendations to the Director

1. **Fix the DC (battery) power timeout immediately.** Run `powercfg /change standby-timeout-dc 0` (or equivalent) to disable the battery-mode display/sleep timeout. This is the exact same fix as T-033 applied to the AC plan, and it's the #1 residual risk that just materialized. This should be a 30-second operator action, not a full research cycle.

2. **Fix the Task Scheduler settings.** The `FreqtradeDryRunBootstrap_T033` task has "Stop On Battery Mode" enabled and a 72-hour auto-kill. Both should be disabled for a continuous-running bot. Consider creating a new task with `Stop On Battery Mode = No`, `Stop Task If Runs Longer Than = Disabled`, and a periodic restart schedule (e.g., daily) to pick up any feather data updates.

3. **Establish a data freshness mechanism.** The monitor cannot run without current feather data, and no automated download exists. Options: (a) add `freqtrade download-data` to the bot's startup batch file, (b) create a daily scheduled task to update feathers, or (c) accept that the monitor only runs during research cycles and have the Engineer update data as a standard pre-step.

4. **Once fixes 1-2 are applied, re-run this exact audit (T-036 spec) as the next infrastructure cycle.** The current 5-day window is contaminated by the battery event. A clean 5+ day window with no standby gaps would genuinely confirm the instrument's reliability. The task spec, falsification criteria, and validation steps are all reusable — only the expected timeline changes.

5. **Do not overclaim from the positive signal.** The post-resume period (2026-07-25 02:37 through 2026-07-26 00:29, ~22 hours) shows zero heartbeat gaps despite multiple brief Modern Standby events. This confirms the AC fix works. But 22 hours of clean operation is still insufficient to declare the instrument fully reliable — it's exactly the T-031/T-032 lesson ("passed-test ≠ problem-solved").
