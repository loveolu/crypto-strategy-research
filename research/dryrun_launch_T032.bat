@echo off
REM ============================================================================
REM CURRENT INFRASTRUCTURE - NOT a historical T-032 artifact, despite the name.
REM
REM THIS EXACT PATH IS REGISTERED IN TWO LIVE WINDOWS SCHEDULED TASKS:
REM     FreqtradeDryRunBootstrap_T032
REM     FreqtradeDryRunBootstrap_T033
REM Both were State=Ready when verified on 2026-08-01, and both invoke
REM     C:\Users\Comec\Projects\freqtrade\research\dryrun_launch_T032.bat
REM
REM MOVING, RENAMING OR DELETING THIS FILE BREAKS THE DRY-RUN BOT LAUNCHER.
REM If it must move, re-register both scheduled tasks in the same change.
REM
REM The T-032 name records the cycle that created it (Task Scheduler decoupling,
REM to fix the silent-death failure mode); it does not mean the file is retired.
REM Launch must use Python 3.13 - see the ops notes on the Modern Standby
REM resume-kill root cause fixed under T-033.
REM ============================================================================
cd /d C:\Users\Comec\Projects\freqtrade
"C:\Users\Comec\AppData\Local\Programs\Python\Python313\python.exe" -m freqtrade trade --config user_data\config.json --strategy TrendVolTarget --logfile user_data\logs\dryrun.log 1> user_data\logs\dryrun_stdout.log 2> user_data\logs\dryrun_stderr.log
