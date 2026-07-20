# Keepalive launcher for the TrendVolTarget dry-run bot.
# Registered with Windows Task Scheduler (task: FreqtradeDryRun-TrendVolTarget)
# to run at logon and every 30 minutes: starts the bot only if it isn't
# already running, so the forward dry-run evidence stream survives Claude
# session ends and machine reboots (see research/current_champion.md,
# "Dry-run history" — the session-bound process was killed twice, 2026-07-09/10).
#
# DRY-RUN ONLY: user_data/config.json has dry_run: true and empty API keys.
# To stop permanently: Unregister-ScheduledTask -TaskName 'FreqtradeDryRun-TrendVolTarget'
# and kill the python process.

$proj = 'C:\Users\Comec\Projects\freqtrade'

$running = Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" |
    Where-Object { $_.CommandLine -match 'freqtrade\s+trade' }
if ($running) { exit 0 }

$logDir = Join-Path $proj 'user_data\logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

Start-Process -FilePath 'py' `
    -ArgumentList '-3.13', '-m', 'freqtrade', 'trade',
        '--config', 'user_data/config.json',
        '--strategy', 'TrendVolTarget',
        '--logfile', 'user_data/logs/dryrun.log' `
    -WorkingDirectory $proj `
    -WindowStyle Hidden
