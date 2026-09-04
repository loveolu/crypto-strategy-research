# Daily append-safe collector for public OKX OI/volume, long-short ratio and taker volume.
$projectRoot = 'C:\Users\Comec\Projects\freqtrade'
$logDir = Join-Path $projectRoot 'user_data\research\data\market_structure'
if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
Set-Location -LiteralPath $projectRoot
& py -3.13 user_data/research/market_structure_recorder.py *>> (Join-Path $logDir 'recorder_task.log')
exit $LASTEXITCODE
