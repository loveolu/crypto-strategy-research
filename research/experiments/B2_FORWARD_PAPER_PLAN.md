# B2Cascade4h forward-paper plan

Pre-registered 2026-09-05. This is an execution/decay measurement of the frozen
CRYPTO-EXP-013 Candidate, not another optimization trial. It is dry-run only and
does not authorize real-money trading.

## Frozen rule

- Universe: BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT and LINK OKX USDT perpetuals.
- Resolution: 4h; long only; unleveraged intent; next available execution at the
  4h signal close using market orders.
- Entry: 42-bar downside-semideviation percentile over 180 bars is at least 0.80;
  24h return is at most -3.85%; BTC 24h return is below zero; the instrument's
  completed daily close is above SMA200 and EMA20 is above EMA50.
- Exit: dispersion percentile below 0.50 or the frozen harness's `HOLD6`
  time stop. Because a signal is acted on at the next 4h open, `HOLD6` maps to
  a maximum 28-hour open-to-open holding time (seven 4h intervals), not 24 hours.
- Execution proxy: taker, with the perp config's 9 bps all-in cost per side.
- Allocation: 500 USDT per position, at most nine simultaneous positions, in a
  dedicated 5,000 USDT simulated wallet.

Any rule, threshold, universe, timeframe, allocation or cost change creates a
new experiment and must not rewrite this forward record.

## Evidence and gates

The comparison baseline is fixed-split OOS expectancy +149 bps/trade and win
rate 63%. The monitor reports after-cost 30/90/180/365-day compounded return,
expectancy, win rate and profit factor from closed dry-run trades.

- `COLLECTING`: either 90-day quarter has fewer than 15 closed trades.
- `PF_GATE_PASSED_AWAITING_SIGNIFICANCE`: both profit-factor windows pass, but
  fewer than 100 total trades have accumulated since the frozen forward start.
- `PF_GATE_PASSED_SIGNIFICANCE_FAILED`: both profit-factor windows pass and at
  least 100 trades exist, but forward PSR(Sharpe > 0) is below .95.
- `READY_FOR_REVIEW`: profit factor is above 1.0 in each of two consecutive,
  non-overlapping 90-day windows with at least 15 trades each, at least 100 total
  forward trades exist, and forward PSR(Sharpe > 0) is at least .95. This permits
  human review only; it is not automatic live promotion.
- `DEGRADED`: profit factor is below 1.0 in both qualifying quarters.
- `MIXED`: populated quarters disagree.
- `RUNTIME_DOWN`: the evidence classification is retained separately, but the
  monitor cannot verify both a heartbeat no older than 180 seconds and the OS PID
  reported by that heartbeat. This overrides the displayed top-level status so a
  stale database can never masquerade as active collection.

Decision-time signal price, proposed simulated fill price and latency are logged
separately so execution drift is observable. Entry and exit decisions are reconciled
to the dedicated dry-run database by pair/time and trade ID; the monitor reports
matched-fill coverage, median decision-to-fill latency, adverse slippage versus the
proposed quote, and realized fees plus funding. Open positions are included for
immediate entry-fill reconciliation; only closed trades enter return statistics.
The bot uses a dedicated database,
log and scheduled keepalive and must not interact with the existing spot bot.

The significance requirement was added after CRYPTO-EXP-025 found selection-
deflated walk-forward DSR only .543 at 200 assumed trials. It does not change the
frozen trading rule or erase forward observations; it prevents a statistically
small pair of profitable windows from being mistaken for live-ready evidence.

Runtime verification added 2026-09-04 PDT: the monitor parses the latest Freqtrade
heartbeat, converts its America/Los_Angeles log timestamp to UTC, checks freshness,
and independently verifies that PID through the OS. At 2026-09-04 23:16:56 UTC it
reported `HEALTHY`: PID 38404 existed, bot state was `RUNNING`, and the latest
heartbeat was 53.3 seconds old. Forward evidence remained `COLLECTING` with zero
closed trades.

## Port-parity correction (2026-09-04 16:24 PDT)

An all-nine-coin, full-history parity audit found five deployment-port defects
that the prior formula-level tests missed:

1. Freqtrade's standard 1d→4h informative merge exposed the newly completed daily
   gate on the 20:00 candle, four hours earlier than the frozen harness's explicit
   `gate_shift=6` convention.
2. The entry callback compared the current 4h `close` with the daily `sma200_1d`;
   the harness compares the completed daily `close_1d` with its daily SMA.
3. The port labeled `HOLD6` as a 24-hour time stop. In the research ledger, the
   signal is evaluated on bar `k` and filled/exited at the next open; 367 of 377
   applicable trades span seven 4h open-to-open intervals. The faithful maximum
   time stop is therefore 28 hours.
4. Freqtrade could re-enter from a signal formed during the candle in which the
   prior trade exited. The harness advances to signal candle `k+2` after filling
   an exit at open `k+1`, deliberately skipping that exit candle. A one-candle
   Freqtrade `CooldownPeriod` reproduces this scheduling convention. Engine-level
   verification showed that its boundary rounding makes the correct setting one
   candle (a two-candle setting delayed valid entries by an additional 4h).
5. The intended 9 bps per-side backtest cost override was nested inside `exchange`,
   but Freqtrade reads this override only from the top level. The engine silently
   used its injected market's 5 bps taker fee. The key is now top-level and an
   engine rerun explicitly reports `Using fee 0.0900% from config`.

The strategy now offsets informative timestamps by four hours and compares
`close_1d > sma200_1d`, its time stop is now 28 hours (`time_stop_28h`), and it
uses the required post-exit cooldown. Both the end-to-end entry mask and complete
entry/exit timestamp ledger match the frozen harness across all nine instruments
and all available 4h history. The initial host-owned process predated the corrections
and was correctly classified `STALE_STRATEGY_CODE / RUNTIME_DOWN`; it produced zero
trades. PID 37452 subsequently loaded the corrected strategy and both configuration
files. An OS census shows it is the only actual B2 trade process, its heartbeat is
fresh, and current status is **`HEALTHY / COLLECTING`**. The dedicated keepalive
detects runtime files newer than the matched B2 process. It also sets PowerShell's error preference to
`Stop`, so a denied process census fails closed instead of falling through and
launching a duplicate. A managed-shell verification returned exit code 1 on the
denied CIM query and left the original single parent/child bot process pair intact.

## Real-engine parity evidence (2026-09-04 16:57 PDT)

The actual Freqtrade 2026.5 backtest engine was run with protections enabled on
temporary 4h feathers mechanically resampled from the canonical 1h files. Static
offline market metadata avoided network access; canonical candle files were not
modified. Across 2023-01-22 through 2026-09-02, all **368/368** engine trades match
the frozen research ledger on both entry and exit timestamp, for every coin. The
9 bps/side fixed-stake engine diagnostic returned +59.08%, 13.71% CAGR, Sharpe 1.45,
PF 2.22 and -5.95% maximum drawdown. These performance values are not substituted
for the walk-forward leaderboard because the engine run uses fixed 500 USDT stakes.
Replaying the same 368 engine profit ratios with the research portfolio convention
(1/9 fractional exposure) gives +88.35% and -10.49% drawdown, versus +92.03% and
-9.99% under the harness's measured coin-specific costs. Thus the apparent return
gap is capital sizing plus the deliberately conservative constant cost—not a signal
or fill-timing mismatch. Compact evidence and artifact SHA-256 are stored under
`research/measurements/B2_ENGINE_PARITY/summary.json`.
