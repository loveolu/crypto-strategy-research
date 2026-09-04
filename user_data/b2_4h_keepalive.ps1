# Dedicated keepalive for the isolated B2Cascade4h forward-paper bot.
# This deliberately matches only B2, so it neither suppresses nor stops the
# existing TrendVolTarget spot bot. DRY-RUN ONLY; config contains empty keys.

$projectRoot = 'C:\Users\Comec\Projects\freqtrade'
$running = Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" |
    Where-Object {
        $_.CommandLine -match 'freqtrade\s+trade' -and
        $_.CommandLine -match '(--strategy\s+B2Cascade4h|config_b2_4h\.json)'
    }
if ($running) { exit 0 }

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
