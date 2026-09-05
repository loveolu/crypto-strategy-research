# Dedicated keepalive for the isolated B2Cascade4h forward-paper bot.
# This deliberately matches only B2, so it neither suppresses nor stops the
# existing TrendVolTarget spot bot. DRY-RUN ONLY; config contains empty keys.

# Fail closed: if the process census is unavailable, never fall through and
# launch a second instance against the same strategy/database.
$ErrorActionPreference = 'Stop'

$projectRoot = 'C:\Users\Comec\Projects\freqtrade'
$strategyPath = Join-Path $projectRoot 'user_data\strategies\B2Cascade4h.py'
$running = Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" |
    Where-Object {
        $_.CommandLine -match 'freqtrade\s+trade' -and
        $_.CommandLine -match '(--strategy\s+B2Cascade4h|config_b2_4h\.json)'
    }

# Reload code changes safely: only the isolated B2 process is eligible, and only
# when its creation time predates the strategy file.  This never matches the
# separate TrendVolTarget spot process.
$strategyWriteUtc = (Get-Item -LiteralPath $strategyPath).LastWriteTimeUtc
$stale = @($running | Where-Object { $_.CreationDate.ToUniversalTime() -lt $strategyWriteUtc })
if ($running -and -not $stale) { exit 0 }
if ($stale) {
    foreach ($process in $stale) {
        Stop-Process -Id $process.ProcessId -ErrorAction Stop
    }
    Start-Sleep -Seconds 2
}

$logDir = Join-Path $projectRoot 'user_data\logs'
if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

Start-Process -FilePath 'py' `
    -ArgumentList '-3.13', '-m', 'freqtrade', 'trade',
        '--config', 'user_data/config_b2_4h.json',
        '--strategy', 'B2Cascade4h',
        '--db-url', 'sqlite:///tradesv3.b2_4h.dryrun.sqlite',
        '--logfile', 'user_data/logs/b2_4h_dryrun.log' `
    -WorkingDirectory $projectRoot `
    -WindowStyle Hidden
