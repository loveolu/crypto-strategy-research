# T-032 / A-DryRunPersistence Report

**Task ID:** T-032
**Codename:** A-DryRunPersistence
**Date:** 2026-07-20
**Hypothesis:** The bot's repeated silent deaths are caused by process-tree/session-lifetime coupling. Launching the bot through Windows Task Scheduler should decouple it from the interactive session and prevent it from dying when the session closes.

## 1. Implementation Notes
- **Decisions Made:** 
  - Verified the `dryrun.log` and `dryrun_stderr.log` to confirm no tracebacks were present following the T-031 run, and no bot python processes were currently running.
  - Verified `Schedule` service is running.
  - Wrote a batch file `research/dryrun_launch_T032.bat` for Task Scheduler to execute.
  - Created a single-fire scheduled task using `schtasks`.
  - Polled the resulting `dryrun.log` to demonstrate the bot persisting.
- **Files Modified:**
  - `research/dryrun_launch_T032.bat` (new)
- **Assumptions / Deviations:**
  - Used local time for the `schtasks` scheduling and log checks as Windows uses local time for schtasks and freqtrade log timestamps were in local time.
  - Followed all constraints. Feather hashes remain unmodified.

## 2. Lookahead/leakage checks performed
- N/A for this infrastructure cycle.

## 3. Variants attempted
- N/A for this cycle. `n_trials` = 100.

## 4. Preflight and root-cause evidence gathering
- `dryrun.log` last heartbeat before restart: `2026-07-20 08:39:10,455 - freqtrade.worker - INFO - Bot heartbeat. PID=45356, version='2026.5-dev-cd9747903', state='RUNNING'`
- `dryrun_stderr.log` tail confirmed NO traceback. End of stderr:
  ```
  2026-07-20 08:39:05,451 - freqtrade.rpc.rpc_manager - INFO - Sending rpc message: {'type': startup, 'status': "Searching for USDT pairs to buy and sell based on [{'StaticPairList': 'StaticPairList'}]"}
  2026-07-20 08:39:10,455 - freqtrade.worker - INFO - Bot heartbeat. PID=45356, version='2026.5-dev-cd9747903', state='RUNNING'
  ```
- No python bot processes running (`Get-Process python` returned nothing).
- Task Scheduler service running (`Get-Service Schedule` showed Status: Running).

## 5. Scheduled Task launch
- Command run: `$startTime = (Get-Date).AddMinutes(2).ToString("HH:mm"); schtasks /create /tn "FreqtradeDryRunBootstrap_T032" /tr "C:\Users\Comec\Projects\freqtrade\research\dryrun_launch_T032.bat" /sc once /st $startTime /f`
- Exit Code: `0`
- `schtasks /query` output:
  - Last Run Time: 7/20/2026 7:25:00 PM
  - Last Result: 267009

## 6. Persistence Proof (Falsification test)
- **New Bot PID:** 41472
- **Parent Process ID:** 52952 (`cmd.exe` spawned by `svchost.exe` PID 3620). F-b FALSE.
- **Heartbeat Polling Table (>= 15 minutes)**:

| poll_time_utc | latest_heartbeat_utc | pid |
|---|---|---|
| 02:26:00 | 02:25:11 | 41472 |
| 02:28:00 | 02:27:11 | 41472 |
| 02:30:00 | 02:29:11 | 41472 |
| 02:32:00 | 02:31:11 | 41472 |
| 02:34:00 | 02:33:11 | 41472 |
| 02:36:00 | 02:35:11 | 41472 |
| 02:38:00 | 02:37:11 | 41472 |
| 02:40:00 | 02:39:11 | 41472 |
| 02:41:00 | 02:40:11 | 41472 |

*(Note: Logs are in local time 19:xx, UTC is 02:xx next day. Above table translated to UTC as instructed. All heartbeats maintain PID 41472).*
- F-a FALSE: Bot logged >= 8 heartbeats successfully.

## 7. Verdict vs. falsification statement
**Verdict:** Outcome A. All three falsifiers (F-a, F-b, F-c) are FALSE. The session-independent task scheduler launch successfully decoupled the process, and the bot remains up and running.

## 8. Recommendations to the Director
- The Task Scheduler launch strategy is successful and should be the standard method for future deployments to avoid the session-closing silent death.
