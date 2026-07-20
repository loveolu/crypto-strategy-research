# Session 2026-07-12: A-DryRunMonitor (Forward Evidence Parity Check)

## 1. Pre-Declared Drift Triggers (Locked Before Inspecting P&L)

This task checks whether the champion strategy (`TrendVolTarget`) exhibits mechanical and statistical parity between its backtested expectations and its live dry-run forward behavior (running since 2026-07-08).

### 1.1 Mechanical Parity Trigger
- **Condition:** Divergence in entry, exit, or sizing decisions bar-for-bar between the live dry-run behavior and the backtest engine re-run over the identical calendar window.
- **Threshold:** 0 divergence. Any mechanical difference is a bug or fundamental backtest/live divergence.
- **Action on Trigger:** Immediate bug investigation. If real and irreducible, the backtest evidence base is compromised; Director review of champion status.

### 1.2 Statistical Parity Triggers
- **Realized CAGR:** Once >= 3 months of in-market data exist, realized CAGR falling outside the pre-declared 5-15% expected band.
- **Shock-day Log-share Drift:** Dry-run P&L share on 3-sigma rolling shock days drifting beyond a ±5.0% absolute tolerance from the backtest-era baseline (44.6%). Stop rule triggers if > 49.6% or < 39.6%.
- **Entry/Rebalance Frequency:** Entry frequency deviating significantly from ~7/yr, or rebalance frequency from ~22/yr (adjusted pro-rata for the sample window).
- **Action on Trigger:** Champion forward expectation formally downgraded in `current_champion.md`; real-capital consideration pushed further out.

### 1.3 Parity Sustained
- **Condition:** No triggers hit after >= 3 months of in-market data.
- **Action:** DSR-external confirmation recorded in `research_metrics.md`.

## 2. Dry-run Script and Operations

- Script: `user_data/research/dryrun_monitor.py`
- Database: `sqlite:///tradesv3.dryrun.sqlite` (WAL mode)
- Log file: `user_data/logs/dryrun.log`

---
*(End of pre-registration block. Analysis follows below after script execution.)*

## 3. Execution Results

### 3.1 Initial Monitor Run
The `dryrun_monitor.py` script was executed on 2026-07-12 09:47 UTC.
- **Coverage since 2026-07-08**: 100% (No gaps > 1h found in `dryrun.log`).
- **Trades Opened/Closed**: 0 opened, 0 closed.
- **Current Position (Live)**: None.
- **Current Position (Expected)**: None.
- **Realized PnL**: N/A (insufficient data).

**Conclusion**: Mechanical parity holds. Both the live dry-run and the backtest engine correctly expect a flat portfolio (0 open trades) for the period 2026-07-08 to 2026-07-12.

### 3.2 Ops Closure: Keepalive Verification
A review of `user_data/logs/dryrun.log` confirms the scheduled restart:
- `2026-07-10 03:04:42,095` - Bot heartbeat (PID=67716) stops.
- `2026-07-10 03:09:40,199` - Bot restarts and enables colorized output (PID=62328).
The `user_data/dryrun_keepalive.ps1` script successfully fired at 03:09 UTC.

### 3.3 Task Scheduler Registration Block
To formally bind the keepalive script to run persistently across reboots, run the following in an Administrator PowerShell prompt:

```powershell
$action = New-ScheduledTaskAction -Execute "Powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File C:\Users\Comec\Projects\freqtrade\user_data\dryrun_keepalive.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "03:09"
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "FreqtradeDryRunKeepalive" -Description "Daily 03:09 restart for Freqtrade champion dry-run" -RunLevel Highest
```
