# T-019 / S5 Repair + Run — Research Engineer Report

**Task ID**: T-019 / S5 Repair  
**Date**: 2026-07-18  
**n_trials used this session**: 0 (infrastructure task; cumulative n_trials = 98 unchanged)

---

## §1 — AC1: S5 Units Bug Repair

The units bug identified during the T-018 rejection was repaired by implementing Option A: passing the raw `closes` price frame to `compute_shock_share`, which maintains its internal `pct_change()` computation.

### Before/After Diff (`dryrun_monitor.py`)

```diff
-    underlying_rets = closes.pct_change()
-    window_underlying = underlying_rets[underlying_rets.index >= WINDOW_START]
-    shock_result, s5_evaluable, n_inmarket = compute_shock_share(window_underlying, daily_ret)
+    shock_result, s5_evaluable, n_inmarket = compute_shock_share(closes, daily_ret)
```

---

## §2 — AC2: Evaluable-Branch Fixture & Hand-Computation

The inline replica block was removed from `test_dryrun_monitor.py` (AC3) and replaced with an AC2-compliant fixture that passes raw price `closes_synth` to the real `compute_shock_share`.

**Hand-Computation for AC2 Fixture**:
- **Setup**: 120 days of synthetic returns for BTC/ETH (all >= `WINDOW_START`). Last 30 days are set as in-market (daily return ≠ 0). 
- **Method**: The underlying returns are passed through `shock_day_mask(method="3sigma", ...)`, which yielded 3 `True` mask days (shock days).
- **Log P&L**: The total log-return of the 30 in-market days was computed. The sum of log-returns on the 3 shock days was computed.
- **Ratio**: The quotient (shock_log / total_log) was computed by hand.
- **Result**: Hand-computed ratio: 13.0645%. 
- **Assertion**: `compute_shock_share` yielded exactly 3 shock days and 13.0645% share, matching hand-computation perfectly.

---

## §3 — AC8: Claims-to-Tests Table

Every claim of code behavior in this report is supported by a test that invokes the REAL function. No inline logic bypasses are present in the test suite.

| Claim | Cited Test in `test_dryrun_monitor.py` | Function Invoked |
|-------|----------------------------------------|------------------|
| S5 branch evaluates successfully at >= 20 in-market days | `ACCEPTANCE CHECK 4: Shock-share path with >=20 in-market days` | `compute_shock_share` |
| S5 computes correct log-share matching hand computation | `ACCEPTANCE CHECK 4: Shock-share path with >=20 in-market days` (AC2-3) | `compute_shock_share` |
| S5 computes exact matching number of shock days | `ACCEPTANCE CHECK 4: Shock-share path with >=20 in-market days` (AC2-4) | `compute_shock_share` |
| S5 returns `not-evaluable` when 0 in-market days | `ACCEPTANCE CHECK 4: Shock-share path with >=20 in-market days` (AC4-4) | `compute_shock_share` |

---

## §4 — AC4: Full Suite Green

Run command and counts:
```bash
py -3.13 user_data/research/test_dryrun_monitor.py
```

```text
  Total checks: 27
  PASS: 27
  FAIL: 0

  ALL CHECKS PASSED -- fixture suite ACCEPTED
  Acceptance checks 2, 3, 4 satisfied.
```

---

## §5 — AC5: Monitor Run Output Excerpt

The 1d candles were updated to `2026-07-18`. The monitor correctly passed the freshness assertion and reached the S5 evaluation.

**S5 Excerpt:**
```text
  S5 (shock-day log-share: 44.6% +/- 5pp, evaluable at >=20 in-market days):
    In-market days: 0 (need >=20)
    S5: NOT YET EVALUABLE (precondition unmet: 0 in-market days < 20)
```

---

## §6 — AC9: POL/USDT Attempt

Attempted to download POL/USDT using `freqtrade download-data` against OKX.

**Outcome**: FAILED. The command aborted immediately with `aiodns.error.DNSError: (11, 'Could not contact DNS servers')` causing `ExchangeNotAvailable`. OKX DNS resolution was completely unavailable in the environment. Per instructions, POL/USDT was left out and the 8-asset defensive proxy was retained as-is.

---

## §7 — AC10: Bookkeeping Integrity

| Item | Value | Note |
|------|-------|------|
| **Backtests** | 0 | No backtests run |
| **Hyperopts** | 0 | No hyperopt run |
| **Hypothesis trials** | 0 | Total remains 98 |
| **n_trials consistency** | 98 | Consistent across index, metrics, and champion |

**Protected File mtimes:**
(Unchanged. Files `best_strategy_so_far.py`, `TrendVolTarget.py`, `validator.py`, `strategy_portfolio.md`, and `freqtrade_dsr.py` were not modified).

---

## Recommendations to the Director

1. **Keepalive Registration**: The C1 trigger remains fired due to earlier downtime (bot session-kill fragility). Registering the Task Scheduler keepalive is critical to prevent further downtime on the current champion dry-run.
2. **POL/USDT Data Addition**: Once OKX DNS availability is restored in the operational environment, a single `download-data` invocation for `POL/USDT` should be executed to expand the defensive sleeve from 8 to 9 assets.
3. **Patience on Parity Data**: The M1 flat parity check confirmed matching state (flat) up to 2026-07-18. S5 accurately reported "NOT YET EVALUABLE" due to zero in-market days. The parity experiment continues to act as designed; it is simply awaiting trend triggers.
