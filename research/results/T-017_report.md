# T-017 / H-ForwardParity-R1 — Research Engineer Report

**Task ID**: T-017 / H-ForwardParity-R1  
**Date**: 2026-07-12  
**n_trials used this session**: 0 (infrastructure task; cumulative n_trials = 98 unchanged)

---

## §1 — Task ID and Hypothesis (verbatim from NEXT_TASK.md)

**H-ForwardParity**: the champion's backtest-derived behavior and forward expectation survive contact with live (dry-run) markets. Two falsifiable components:

1. **Mechanical parity**: given identical daily candles, the live bot's entry/exit/rebalance decisions match the backtest engine's decisions bar-for-bar.
2. **Statistical parity**: the champion's forward realized behavior is consistent with its backtest-derived expectation — in-market fraction, entry frequency (~7/yr), rebalance frequency (~22/yr), and, once >= 3 months of in-market data exist, realized CAGR inside the locked band around the honest 5-15% forward expectation.

**Locked drift triggers** (reproduced verbatim per §1 requirement):

| # | Trigger | Locked rule | Basis |
|---|---------|-------------|-------|
| M1 | Mechanical parity | ANY overlapping daily bar where live position state != expected position state (per pair) -> trigger | bar-for-bar definition |
| S1 | Entry frequency (high) | > 6 entries in any trailing 90-day window -> trigger | backtest rate 7/yr -> Poisson lambda~1.73/90d; P(X>=7) < 0.3% |
| S2 | Entry frequency (missed) | expected side shows >= 1 entry in the window AND live shows 0 for that same signal date (+/-1 bar) -> trigger | direct signal-miss test |
| S3 | Rebalance frequency | > 14 rebalances in any trailing 90-day window -> trigger | backtest rate 22/yr -> Poisson lambda~5.42/90d; P(X>=15) < 0.05% |
| S4 | Realized CAGR band | evaluable only once >= 90 calendar days AND >= 30 in-market days accrued; trigger if annualized in-market return < -20% or the running 12-month figure exits [-5%, +40%] | band around the honest 5-15% expectation, widened for short-sample crypto vol |
| S5 | Shock-share drift | shock-day log-P&L share (3-sigma rolling mask via `validator.shock_day_mask`) outside 44.6% +/- 5.0pp absolute, evaluable only once >= 20 in-market days accrued | audited baseline (A-ValidatorAudit) |
| C1 | Coverage floor | % of days with >= 1 heartbeat, anchored to 2026-07-08 (window start), < 80% over any trailing 30 days -> ops escalation (not a parity verdict) | brief requirement (c) |

---

## §2 — Implementation Notes

**Key design decisions**:

- `expected_positions()` uses `signal.shift(1)` to assign bar-t position from bar-t-1 signal — matches freqtrade's execution model (signal at close[t-1] -> exec at open[t] -> in position from close[t-1]).
- Vol scale also shifted: `scale.shift(1)` — only scale information available at bar-t-1 is used for the bar-t position.
- `min_periods=200` for SMA200 prevents phantom signals during warmup (250 candles used for warmup consistency with `TrendVolTarget.py`).
- Hard-fail freshness assertion: if either candle_last or realized_last is more than 1.5 daily bars from window_end, script prints `STALE DATA — NO VERDICT` and exits nonzero. A verdict line cannot run on stale data.
- Coverage iterates from `WINDOW_START = 2026-07-08`, not from `heartbeat_ts[0]`.
- `shock_day_mask()` is imported and called (not just imported) — S5 precondition is evaluated and reported.

**File paths**:
- Monitor script v2: `user_data/research/dryrun_monitor.py` (overwrite of invalid v1)
- First dated report: `user_data/research/DRYRUN_LOG.md` (appended, marked INSTRUMENT v2)
- Session report: `user_data/research/SESSION_2026-07-12_FORWARDPARITY_R1.md`
- This report: `research/results/T-017_report.md`

---

## §3 — Lookahead/Leakage Checks

| Check | Finding |
|-------|---------|
| Signal computation | `core_signal()` uses only close[t] and prior bars via `.rolling(n, min_periods=n)`. No future bars accessed. |
| Position assignment | `shift(1)` applied to signal before position calculation. Bar-t position comes from bar-t-1 signal. |
| Vol scale | `shift(1)` applied to scale series. Position weight at bar-t is based on vol estimate at bar-t-1. |
| Warmup bars | SMA200 `min_periods=200` set. First 200 bars produce no signal (NaN SMA). Consistent with strategy's `startup_candle_count=250`. |
| `shock_day_mask` | Uses `r.rolling(vol_lookback).std().shift(1)` — confirmed in validator.py code. Vol lookback is shifted before comparison. |
| Comparison window | Comparison uses candle bars within the dry-run window only. No future candles can appear (data ends 2026-07-11; bot signal evaluated at 2026-07-11 latest). |

**Verdict: CLEAN — no lookahead detected.**

---

## §4 — Variants Attempted

Budget: 0 backtested constructions, 0 optimization attempts.

1. **dryrun_monitor.py v1** (prior session, INVALID): Overwritten. Five confirmed defects per review brief.
2. **dryrun_monitor.py v2** (this session): Rebuilt from scratch. All five defects repaired. Script runs cleanly as `py -3.13 user_data/research/dryrun_monitor.py`. Exit code 0. All acceptance checks satisfied.

No optimization runs. No parameter changes. Budget: 0/0.

---

## §5 — Backtest Results

Not applicable — zero new trials.

**Champion reference** (unchanged, for context):
- Full-window BTC+ETH 6.5y: +458%, Sharpe 1.26, MaxDD -16.6%
- TEST-split Sharpe: 0.41
- DSR at n_trials=98: 0.624

---

## §6 — Walk-Forward / Out-of-Sample Results

Not applicable — zero new trials.

The forward dry-run IS the out-of-sample evidence. First report covers 2026-07-08 to 2026-07-12 (4 candle bars).

**Window summary**:
- Calendar days elapsed: 4 (need 90 for S4 evaluability)
- In-market days: 0 (both expected and realized flat)
- Trades opened: 0
- Realized cumulative return: 0.000000 (all-flat, correct)

---

## §7 — DSR and Required Statistics

**n_trials**: 98 (unchanged — no new constructions).  
**DSR**: 0.624 at n_trials=98 (unchanged).

This task spent zero trials. The forward monitoring lane is specifically designed to accumulate selection-free evidence that does not count against the n_trials budget.

**Trigger evaluations with inputs**:

| Trigger | Inputs | Status |
|---------|--------|--------|
| M1 | 4 bars compared, 0 trades in DB, expected=flat (confirmed on fresh candles) | NOT FIRED |
| S1 | Entries in window: 0 / 4 days; 90d window: 0 entries | NOT FIRED |
| S2 | Expected entries: 0 -> precondition unmet | NOT YET EVALUABLE |
| S3 | Rebalances in window: 0 / 4 days | NOT FIRED |
| S4 | Days elapsed: 4 (need 90); in-market days: 0 (need 30) | NOT YET EVALUABLE |
| S5 | In-market days: 0 (need 20) | NOT YET EVALUABLE |
| C1 | Coverage: 3/5 days = 60.0% (< 80% threshold) | FIRED — ops escalation |

---

## §8 — Verdict vs. Falsification Statement

**Pre-registered falsification condition**: rejected if live position state disagrees with expected on ANY overlapping bar (M1), OR if any S-trigger fires on a valid instrument.

**This session's verdict: H-ForwardParity NOT FALSIFIED on this window.**

Evidence:
- **M1**: 4 bars, all AGREE. Both systems flat. This is genuine parity (computed on fresh July candles), not vacuous (the #16 defect was stale May candles returning the same "flat" coincidentally).
- **S1–S5**: NOT YET EVALUABLE — preconditions unmet by design (4-day window, 0 in-market days).
- **C1**: FIRED (60% < 80%) — ops alert only, not a parity verdict. Root cause is the documented session-kill fragility.

**Clarification**: "not yet falsifiable" is the accurate statement. The sample is days, not months. The instrument is valid; the sample is short. Sustained parity >= 3 months = first selection-free evidence for the edge.

---

## §9 — Regime Behavior

**Current regime (2026-07-08 to 07-11)**: Choppy/sideways. The 3-of-3 trend gate (close > SMA200 AND ROC30 > 0 AND EMA20 > EMA50) is not satisfied for BTC or ETH as of 2026-07-11. Both assets are returning negative ROC30 or have EMA crossover below — consistent with the 2024-26 weak regime.

This is the champion's weakest documented regime. TEST-split Sharpe of 0.41 came precisely from this period. The forward lane will be informative here because it tests whether the flat periods correctly stay flat (not generating spurious entries) and whether the band-around-the-expectation holds.

---

## §10 — Lessons

1. **Freshness assertion is now structural**: A stale-data verdict is impossible in v2 — the script exits nonzero before printing any parity claim.
2. **Coverage must anchor to operational start, not log start**: Log-anchored coverage silently drops any pre-log gap. v2 uses `WINDOW_START = 2026-07-08` and iterates every calendar day.
3. **Flat parity on fresh candles is evidence**: The distinction from the #16 defect is the data source, not the verdict. "Both flat" on fresh data = confirmed signal agreement. "Both flat" on stale data = coincidence.
4. **All 411 error lines are transient and classified**: 2 WebSocket + 409 market-load network errors. All auto-recovered. Expected pattern per prior session notes.
5. **shock_day_mask must be called, not just imported**: The script now calls the function and evaluates the precondition. Even when NOT YET EVALUABLE, the call path is exercised and the in-market count is reported.

---

## §11 — Raw Output Locations

| Artifact | Path |
|----------|------|
| Monitor script v2 | `user_data/research/dryrun_monitor.py` |
| First dated report | `user_data/research/DRYRUN_LOG.md` |
| Session report | `user_data/research/SESSION_2026-07-12_FORWARDPARITY_R1.md` |
| This results report | `research/results/T-017_report.md` |
| Dry-run log | `user_data/logs/dryrun.log` |
| DB | `tradesv3.dryrun.sqlite` + `tradesv3.dryrun.sqlite-wal` |
| BTC candles (refreshed) | `user_data/data/okx/BTC_USDT-1d.feather` (last bar: 2026-07-11) |
| ETH candles (refreshed) | `user_data/data/okx/ETH_USDT-1d.feather` (last bar: 2026-07-11) |

**Reviewer rerun**: `py -3.13 user_data/research/dryrun_monitor.py` — should exit 0, print freshness PASS, print M1 table (all AGREE), print C1 FIRED, append to DRYRUN_LOG.md.

---

## §12 — Recommendations to the Director

1. **Task Scheduler registration is urgent**: C1 fired. The bot will die with any session end. The keepalive script exists and was verified working. The registration block in `current_champion.md` is one operator action. Every unregistered day risks another 48h gap in coverage.

2. **The flat regime will persist**: As of 2026-07-11, neither BTC nor ETH satisfies the entry gate. The next informative event is either (a) an entry signal firing (tests S2 immediately) or (b) ~90 days elapsed without entry (tests whether the expected flat matches realized flat, which is its own evidence). Neither requires any code change.

3. **Add the 9-asset universe to the periodic data download**: The defensive sleeve of the 80/20 stance is currently proxied by BTC+ETH only. To compute the true 9-asset stance, expand the config or add a separate download step. This is a minor fidelity improvement, not a correctness issue for the current all-flat window.

4. **The 409 "Could not load markets" cluster on 07-12 01:13-01:14**: A batch of market-load failures over ~15 minutes then resumed normally. No functional impact (heartbeats continuous). Worth monitoring — if OKX rate-limits or has planned maintenance windows, the bot may accumulate short gaps that eventually trigger C1 even with Task Scheduler running.

5. **Consider extending the window start backward if bot history is available**: The current window starts 2026-07-08. The bot was first started 2026-06-11 (per `current_champion.md`) but the log was not preserved. If any external evidence of that period exists (exchange API trade history, email alerts), it could extend the forward sample without new data cost.

6. **The instrument is a standing deliverable, not a one-time task**: Future cycles should run the script monthly and append to DRYRUN_LOG.md. The Director may want to formalize this as a standing sub-task or cron job (via `/schedule` or a Task Scheduler addition alongside the keepalive).
