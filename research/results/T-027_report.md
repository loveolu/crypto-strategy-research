# T-027 / A-ResolverRepair Report

## Objective
Execute the `aiodns` uninstall repair to allow `aiohttp` to use `ThreadedResolver` (OS resolver) so the freqtrade pipeline and bot can reach OKX. Restore the forward-parity monitor to an honest configuration and restart the dry-run bot to continue collecting forward evidence.

## What Was Run
1. Pre-flight state capture (manifest, env, git status).
2. Probes: R1 (control default, failed), R2 (control threaded, succeeded).
3. Repair: uninstalled `aiodns`, verified `ThreadedResolver` is now the default.
4. Decisive Test: R3 (default probe post-repair, succeeded 3/3).
5. Pipeline test: `freqtrade download-data` for BTC/ETH, then all 9 assets.
6. Authenticity proof: Python script using `curl` to independently fetch daily OKX candles and assert exact OHLCV matches against the local feather data.
7. Monitor restoration: Excised `mock_data.py` auto-refresh; added read-only freshness assertion; restored `WINDOW_START` to `2026-07-08`; modified `test_dryrun_monitor.py` to pass under pytest.
8. Bot restart: Launched detached bot (`Start-Process`), verified PID and heartbeats.
9. Final monitor run: `dryrun_monitor.py` passed freshness and authenticity checks on the real log and fresh data.

## Hypothesis & Falsifier Status
**H-Transport-R1:** Uninstalling `aiodns` changes the default resolver to `ThreadedResolver` and fixes async network resolution for freqtrade.
**Falsifier:** NOT FIRED. The decisive probe R3 returned HTTP 200 on 3/3 attempts (F-a avoided). Freqtrade appended real bars post-2026-07-11 (F-b avoided).

## Transcript Index
- `R0_manifest_before.txt`
- `R0_env.txt`
- `R0_git_status.txt`
- `R1_default_before.txt`
- `R2_threaded_before.txt`
- `R2b_uninstall.txt`
- `R2c_dispatch_after.txt`
- `R3_default_after.txt`
- `R4_download_data.txt`
- `R4_manifest_after.txt`
- `R5_download_all.txt`
- `R5_manifest_after.txt`
- `R6_authenticity.txt`
- `R7_pytest.txt`
- `R8_dryrun_confirm.txt`
- `R8_bot_alive.txt`
- `R9_monitor_run.txt`

## Manifest Diff
Files changed:
- `ADA_USDT-1d.feather`
- `AVAX_USDT-1d.feather`
- `BNB_USDT-1d.feather`
- `BTC_USDT-1d.feather`
- `DOT_USDT-1d.feather`
- `ETH_USDT-1d.feather`
- `LINK_USDT-1d.feather`
- `SOL_USDT-1d.feather`
- `UNI_USDT-1d.feather`

Files strictly unchanged (identical SHA-256):
- `BTC_USDT-1h.feather`
- `BTC_USDT-4h.feather`

## Acceptance Criteria (Outcome A)
- **AC1 [PASS]:** R2 control succeeded and R3 returned HTTP 200 3/3 (`R3_default_after.txt`).
- **AC2 [PASS]:** `download-data` appended new authentic bars past 2026-07-11 (`R4_download_data.txt`).
- **AC3 [PASS]:** New bars independently cross-checked via `curl` and matched perfectly (`R6_authenticity.txt`).
- **AC4 [PASS]:** `mock_data.py` remains quarantined; no data file written by custom scripts; manifest fully reported.
- **AC5 [PASS]:** Monitor auto-refresh excised; freshness hard-fail installed; `WINDOW_START` restored; pytest suite passing (`R7_pytest.txt`).
- **AC6 [PASS]:** Bot running detached (PID=32344), genuine heartbeats captured (`R8_bot_alive.txt`); `dry_run: true` confirmed (`R8_dryrun_confirm.txt`).
- **AC7 [PASS]:** Monitor executed cleanly against refreshed data (`R9_monitor_run.txt`).
- **AC8 [PASS]:** `n_trials` unchanged at 99.

## Budget Usage
- DSR trials: 0 (limit: 0)
- Strategy variants: 0 (limit: 0)
- Optimization runs: 0 (limit: 0)
- Repair variants: 1 (limit: ≤3)
- Network attempts: 22 (limit: ≤30)

## Recommendations to the Director
1. The forward-evidence lane is fully restored. The dry-run bot is accruing valid out-of-sample data on OKX.
2. The `pytest` execution for `test_dryrun_monitor.py` was structurally incompatible out-of-the-box because it relied on top-level `sys.exit(0)` calls that broke test collection. This was repaired, but future pytest checks should ensure test scripts are valid pytest functions, not just imperative execution scripts.
3. The C1 Coverage Trigger is firing (10% coverage) because the bot was down between 2026-07-09 and 2026-07-19. This will naturally resolve as new days accrue, but the current monitor recommendation is to "register Task Scheduler keepalive to prevent recurrence". We should consider doing this so future gaps are minimized.
