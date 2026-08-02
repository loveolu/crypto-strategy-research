# Freqtrade Research Repo Audit — 2026-07-28

Facts and file paths only. No recommendations.

---

## 1. Scope read

`PROJECT_OPERATOR_MANUAL.md`, all files under `research/` (top-level `.md` files, `results/`,
`review_briefs/`, `meta_reviews/`, `scratch/`), all files under `knowledge_base/`, plus (as needed
to answer Q2/Q6) `user_data/config.json`, `user_data/research/validator.py`, `freqtrade_dsr.py`,
`user_data/research/dryrun_monitor.py`, `user_data/strategies/*.py`, `user_data/research/phase*.py`,
`user_data/data/okx/`, and the embedded contents of
`user_data/backtest_results/backtest-result-2026-06-11_01-06-44.zip` (the latest real-engine
backtest artifact, per `.last_result.json`).

---

## 2. Fee, slippage, and spread assumptions — exact values and locations

**A. Research harness (`user_data/research/validator.py`, lines 56–58):**
```
COMMISSION = 0.001          # 0.1% per side (OKX taker)
SLIPPAGE = 0.0005           # 0.05% per side
```
`monte_carlo()` (validator.py, line 241) additionally subtracts a per-trade
`extra_slippage: float = 0.0005` (0.05%) from `trades["pnl"]` before its 200-simulation shuffle, on
top of whatever `COMMISSION+SLIPPAGE` was already baked into the trade P&L series passed in.

**B. Strategy-file comments corroborate the same combined figure:**
- `user_data/strategies/TrendVolTarget.py:11`: `# Validation summary (pandas harness, fees 0.1% + slippage 0.05% per side):`
- `user_data/research/BEST_STRATEGY_REPORT.md:30`: `Fees modeled: 0.10% commission + 0.05% slippage/side.`
- `user_data/research/phase15_rangevol.py:18` and `phase19_sizingband.py:25`: `fees 0.15%/side` (= 0.001+0.0005, same total, expressed as one number rather than split).
- `user_data/research/phase10_intraday.py:55`: `fees 0.15%/side` used for the hours-21-22 UTC intraday test.

**C. `freqtrade_dsr.py`** (repo root): grepped for `fee|slippage|commission|spread` — **zero
matches**. The DSR/legitimacy-gate module contains no cost model; it consumes pre-computed
return/Sharpe series only.

**D. `user_data/research/dryrun_monitor.py`**: grepped for `fee|slippage|commission|spread` —
**zero matches**. The forward-parity instrument does not model or check costs; it reconciles
positions/returns only.

**E. `user_data/config.json`** (the live dry-run trading config): contains **no `"fee"` key
anywhere** (confirmed via `grep -rn '"fee"' user_data/ research/` → no hits in any JSON). No
slippage or spread configuration block exists in this file at all.

**F. Real freqtrade engine run** (`user_data/backtest_results/backtest-result-2026-06-11_01-06-44.zip`,
the latest real-engine artifact per `.last_result.json`): the embedded
`backtest-result-2026-06-11_01-06-44_config.json` has no `"fee"` key. The embedded results file
`backtest-result-2026-06-11_01-06-44.json` (strategy `TrendVolTarget`, 92 trades) shows, on every
trade record:
```
"fee_open": 0.0015, "fee_close": 0.0015, "funding_fees": 0.0
```
i.e., the real engine applied a **single 0.15%-per-side fee** (source: freqtrade's own
default/exchange-fetched value — no override is set anywhere in the repo). No separate slippage or
spread line item exists in this result file.

**G. Spread**: grepped `validator.py`, `dryrun_monitor.py`, `config.json`, `TrendVolTarget.py`,
`best_strategy_so_far.py` for `spread` — the only match is `"sharpe_spread"` in `validator.py:420`,
an unrelated statistic (max-minus-min Sharpe across walk-forward windows). No bid-ask spread cost is
modeled anywhere in the repository, in either the harness or the real engine.

**Summary table:**

| Path | Component | Value |
|---|---|---|
| `user_data/research/validator.py:56` | Commission | `0.001` (0.1%/side) |
| `user_data/research/validator.py:57` | Slippage | `0.0005` (0.05%/side) |
| `user_data/research/validator.py:241` | MC extra slippage | `0.0005` default arg |
| `user_data/backtest_results/…_01-06-44.zip` → `*.json` trade records | Real-engine fee | `fee_open=0.0015`, `fee_close=0.0015` |
| `user_data/config.json` | Fee/slippage/spread config keys | absent |
| `freqtrade_dsr.py` | Fee/slippage/spread | absent (not a cost-model file) |
| `user_data/research/dryrun_monitor.py` | Fee/slippage/spread | absent (not a cost-model file) |
| any file in repo | Bid-ask spread cost | not found |

---

## 3. Validation computed by script vs. written by hand into markdown

**A. Computed by script (deterministic, reproducible, source cited):**

- `user_data/research/validator.py`:
  - `metrics()` — Sharpe, CAGR/total return, MaxDD, trade count, profit factor
  - `yearly_breakdown()`, `yearly_pnl_dollar_concentration()`
  - `split_70_15_15()` — train/val/test split
  - `walk_forward()` — 4-window OOS split
  - `monte_carlo()` — 200-sim shuffle, P5/P50/P95 Sharpe and return
  - `shock_day_mask()`, `shock_pnl_decomposition()` — Kaufman Ch.21 shock-day P&L decomposition
  - `top_day_concentration()` — top-5/10/20-day P&L share
  - `wf_window_stability()` — 3/4/5/6-window boundary-sensitivity
  - `rolling_sharpe_series()` — trailing 18-month Sharpe
  - `family_context()` / `family_from_results_dir()` — average-of-all-tests ranking
  - `validate()` / `save_verdict()` — assembles the above into a `Verdict` object
- `freqtrade_dsr.py`: `probabilistic_sharpe_ratio()`, `expected_max_sharpe()`,
  `deflated_sharpe_ratio()`, `returns_from_freqtrade()`, `evaluate_freqtrade()`,
  `validate_robustness_payload()` — the sole source of every quoted DSR number.
- `user_data/research/dryrun_monitor.py`: `core_signal()`, `vol_scale()`, `expected_positions()`,
  `assert_freshness()`, `assert_data_authenticity()`, `parse_log()`, `coverage_report()`,
  `reconstruct_live_positions_per_bar()`, `compute_8020_stance()`, `realized_daily_returns()`,
  `compute_shock_share()` — source of M1/S2/S4/S5/coverage-% figures cited in dry-run reports.
- Per-hypothesis one-off `user_data/research/phase*.py` scripts (e.g. `phase21_ivgate.py`,
  `phase_feargreed.py`, `phase18_cointpair.py`) — source of pre-gate numbers: reachability %,
  redundancy correlations, lead/lag cross-correlations, episode counts, harm-census forward returns,
  TEST-split concentration stats, ADF/EG cointegration statistics, half-life estimates. These are
  script-generated but are one-shot scripts, not part of the reusable `validator.py` suite.

**B. Written by hand directly into markdown (prose/narrative, or a number typed without a backing
script run):**
- Every "Scientific rationale," "Expected market regime(s)," "Lessons," and "Recommendations to the
  Director" section in `research/NEXT_TASK.md` and `research/results/T-*_report.md` — free-text
  interpretation, not script output.
- Verdict labels themselves (CONFIRMED / REJECTED / ACCEPTED / PROMOTED) — a human/agent judgment
  applied on top of script numbers, not computed.
- The narrative rows in `research/research_index.md`'s "Hypotheses tested" table and the status
  blocks in `knowledge_base/hypothesis_bank.md` — hand-composed prose summarizing script output,
  authored by the Director/Reviewer, not themselves script-generated.
- **Specific documented cases where a hand-typed number was later found false by the Reviewer**
  (i.e., "validation" that was never actually script-derived, presented as if it were):
  - `research/review_briefs/T-019_brief.md`: the AC2 fixture's "hand computation" was a programmatic
    mirror of the function body rather than an independent value — report claimed `13.0645%`, actual
    (script) value was `2.2760%`.
  - `research/review_briefs/T-031_brief.md`: report claimed restart heartbeat `PID=16124`; that PID
    does not appear anywhere in `dryrun.log` — a hand-typed, unverified claim.
  - `research/review_briefs/T-025_brief.md`: 8 synthetic OHLC bars per feather were hand-written
    (not fetched) into all 9 feathers, plus fake `PID=12345` heartbeat lines hand-inserted into
    `dryrun.log`.
  - `research/review_briefs/T-023_brief.md` / `research_index.md` row #25: candle data fabricated
    with injected random variance, hand-written into feathers.

---

## 4. Timeframe and pair universe of every construct tested

Source: `research/research_index.md` rows 1–37 (+ T-036, unreviewed), `user_data/strategies/*.py`
`timeframe` attributes, `user_data/data/okx/` cached feathers, `user_data/research/phase*.py`.

| Research_index row(s) | Construct family | Timeframe | Pairs/universe |
|---|---|---|---|
| #1 | EMA/RSI/volume trend (`EmaRsiVolumeStrategy.py`) | `1h` | BTC/USDT, ETH/USDT (config.json whitelist) |
| #2 | Pullback/mean-rev/breakout-retest/Donchian/Bollinger | `1h` (`PullbackStrategy.py`, `BollingerBreakoutStrategy.py`, `BreakoutRetestStrategy.py`, `DonchianBTC1h.py` all declare `timeframe = "1h"`) | BTC (Donchian variant explicitly BTC-only per `DonchianBTC1h.py`/`.json`); others per config whitelist |
| #3 | TTM squeeze / band fade (`SqueezeBreakoutStrategy.py`, `BandFadeStrategy.py`) | `1h` | BTC/ETH per config |
| #4 | Funding-rate squeeze | n/a (BLOCKED — never backtested) | n/a |
| #5 | Spot-perp basis proxy | n/a (OKX data, no strategy file/timeframe attr found) | BTC/ETH |
| #6 | Overnight/time-of-day breakout (`OvernightVolSizedBreakout.py`, `BTCOvernightVolTarget.py`) | `1h` | BTC only |
| #7 | SMA200 regime overlay (`RiskManagedBetaOverlay.py`) | `1d` | BTC + ETH |
| #8 | 61-strategy autonomous search | Mixed `1d`/`1h`/`4h` — `user_data/research/results/` contains 63 result JSONs; filename convention confirms `*_btc1d.json`, `*_btc4h.json`, `*_btc1h.json` variants (61 `btc`-tagged files, 13 `eth`-tagged, 5 `xsect`-tagged) | Primarily BTC-only; some ETH; 5 cross-sectional files |
| #9–#10 | TrendVolTarget core + 9-asset/hybrid expansions | `1d` (`TrendVolTarget.py:41`) | Core: BTC+ETH. 9-asset universe = the 9 feathers in `user_data/data/okx/`: BTC, ETH, ADA, AVAX, BNB, DOT, LINK, SOL, UNI (all `-1d.feather`) |
| #11 | Cross-sectional/dual-momentum/halving/calendar/long-short pairs | `1d` (`XSectMomMajors1d.py:77`) | 9-asset universe |
| #12 | Intraday hours 21-22 UTC anomaly | `1h` (`user_data/research/phase10_intraday.py:2,13`: "BTC 1h, 2020-10..2026-05") | BTC only |
| #13 | Supertrend/Chandelier/BTC-dominance/ETH-BTC z-fade (Forven-derived) | `1d` | BTC + ETH |
| #14 | H-COT (CFTC crowding filter) | `1d` | BTC + ETH (CME COT data overlaid on champion) |
| #15, #19 | H-RangeVol, H-SizingBand (sizing-layer) | `1d` (`phase15_rangevol.py:18`, `phase19_sizingband.py:25`: "BTC+ETH 1d universe") | BTC + ETH |
| #16 | H-BearShort (mirrored short sleeve) | `1d` | BTC + ETH |
| #17 | A-ValidatorAudit | `1d` | BTC + ETH (champion re-audit) |
| #18, T-021 | H-CointPair / F-4 Regime-Gated Pairs Revival | `1d` | BTC + ETH |
| #20 | H-TailAlloc (portfolio allocation) | `1d` | BTC+ETH sleeve vs. 9-asset defensive sleeve |
| #21, #22, T-022 (F-3) | H-IVGate, H-IVSizing, DVOL acceleration | `1d` (DVOL is a daily index) | BTC + ETH (Deribit BTC/ETH DVOL, `user_data/research/data/dvol/`) |
| T-024 | Dynamic Volatility-Stabilized Portfolio | `1d` | BTC+ETH champion sleeve + 9-asset defensive sleeve |
| #28 (T-028), #29 (T-029) | H-EffRatio, H-ERScale | `1d` | BTC + ETH |
| #30 (T-030) | H-ADXGate | `1d` | BTC + ETH |
| T-031 | A-FundingRecorder | n/a (data bootstrap, `1h` funding settlement cadence per `user_data/data/okx/futures/*-1h-funding_rate.feather`) | 9 perpetual-swap instruments (`user_data/research/data/funding/*.csv`: includes XRP alongside the 9-asset spot set per futures feathers, e.g. `XRP_USDT_USDT-1h-funding_rate.feather`) |
| T-032, T-033, T-036 | Dry-run persistence / forward parity | `1d` (live dry-run bot timeframe matches champion) | BTC + ETH |
| T-034 | H-LogisticEntry | `1d` (per-asset, lagged log-returns) | BTC, ETH (separate per-asset models) |
| T-035 | H-FearGreed | `1d` (Fear & Greed Index is daily) | BTC + ETH |

**Cached data universe (all timeframe/pair combinations that exist as feather files,
`user_data/data/okx/`):** BTC/USDT (`1d`, `1h`, `4h`), ETH/USDT (`1d`), ADA/AVAX/BNB/DOT/LINK/SOL/UNI
(`1d` only). Futures/funding data (`user_data/data/okx/futures/`) additionally covers BTC, ETH, ADA,
AVAX, BNB, DOT, LINK, SOL, XRP at `1h` (futures OHLCV, mark price, funding rate) and `1d` (futures
OHLCV).

---

## 5. Every research cycle T-001 onward — RESEARCH vs. OPS/INFRASTRUCTURE

`grep -ohE "T-0[0-9][0-9]"` across `research/research_index.md`, `research/research_metrics.md`,
`research/strategy_iteration_log.md`, `knowledge_base/hypothesis_bank.md` returns exactly these IDs
— **no `T-001` through `T-016` exist anywhere in the repository, and `T-020` does not exist** (a
second independent grep for `T-020`/`T-20[^0-9]`/`Task 020` returned zero hits). The formal `T-XXX`
numbering scheme begins at `T-017` (2026-07-12). Hypothesis-bank rows #1–#20 (dated 2026-05-14
through 2026-07-11) predate this scheme and are tracked only by row number/date/hypothesis name in
`research/research_index.md`, never as `T-XXX`.

| Task ID | Name | Classification | Basis (file) |
|---|---|---|---|
| T-017 | H-ForwardParity-R1 | OPS/INFRASTRUCTURE | `research/results/T-017_report.md` — dry-run monitor instrument build |
| T-018 | A-ParityHardening | OPS/INFRASTRUCTURE | `research/results/T-018_report.md` |
| T-019 | A-S5Repair | OPS/INFRASTRUCTURE | `research/review_briefs/T-019_brief.md` |
| T-021 | F-4 Regime-Gated Pairs Revival | RESEARCH | `research/results/T-021_report.md` |
| T-022 | DVOL Acceleration | RESEARCH | `research/results/T-022_report.md` |
| T-023 | A-DryRunMonitor/ForwardParityMonitor Rebuild | OPS/INFRASTRUCTURE | `research/results/T-023_report.md` |
| T-024 | Dynamic Volatility-Stabilized Portfolio | RESEARCH | `research/results/T-024_report.md` |
| T-025 | A-ForwardLaneRestore | OPS/INFRASTRUCTURE | `research/results/T-025_report.md` |
| T-026 | A-TransportRepair | OPS/INFRASTRUCTURE | `research/results/T-026_report.md` |
| T-027 | A-ResolverRepair | OPS/INFRASTRUCTURE | `research/results/T-027_report.md` |
| T-028 | H-EffRatio | RESEARCH | `research/research_index.md` row 30 |
| T-029 | H-ERScale | RESEARCH | `research/results/T-029_report.md` |
| T-030 | H-ADXGate | RESEARCH | `research/results/T-030_report.md` |
| T-031 | A-FundingRecorder | OPS/INFRASTRUCTURE | `research/results/T-031_report.md` |
| T-032 | A-DryRunPersistence | OPS/INFRASTRUCTURE | `research/results/T-032_report.md` |
| T-033 | H-EventKiller | OPS/INFRASTRUCTURE | `research/results/T-033_report.md` (Windows Event Viewer forensics/powercfg fix, despite "H-" prefix) |
| T-034 | H-LogisticEntry | RESEARCH | `research/results/T-034_report.md` |
| T-035 | H-FearGreed | RESEARCH | `research/results/T-035_report.md` |
| T-036 | A-ForwardParityConfirm | OPS/INFRASTRUCTURE | `research/results/T-036_report.md` (unreviewed as of this audit — no `T-036_brief.md` exists yet) |

**Counts: RESEARCH = 8** (T-021, T-022, T-024, T-028, T-029, T-030, T-034, T-035).
**OPS/INFRASTRUCTURE = 11** (T-017, T-018, T-019, T-023, T-025, T-026, T-027, T-031, T-032, T-033,
T-036). Total formally-numbered cycles = 19.

---

## 6. Byte size of every file the Director prompt loads

Per the Director prompt's "Context loading" section, in its stated order:

| # | File | Bytes | Status |
|---|---|---|---|
| 1 | `PROJECT_OPERATOR_MANUAL.md` | 18,185 | mandatory |
| 2 | `research/research_index.md` | 41,172 | mandatory |
| 3 | Latest file in `research/review_briefs/` — `T-035_brief.md` (newest by mtime, 2026-07-26 00:03; `T-036` has no brief yet) | 10,219 | mandatory |
| 4 | Latest file in `research/meta_reviews/` — `meta_review_1.md` (only file present) | 17,395 | mandatory |
| 5a | `knowledge_base/master_index.md` | 85,527 | mandatory |
| 5b | `knowledge_base/hypothesis_bank.md` | 164,820 | mandatory |
| 6a | `research/current_champion.md` | 23,057 | mandatory |
| 6b | `best_strategy_so_far.py` (actual path: `research/best_strategy_so_far.py`) | 5,813 | conditional ("only if orthogonality requires understanding its mechanics") |
| 7 | `research/parked/` | 0 (directory does not exist) | mandatory to check, contributes 0 bytes |

**Mandatory-only subtotal (rows 1–6a, 7): 360,375 bytes.**
**With conditional file 6b included: 366,188 bytes.**

**Conditionally-opened topic files** (prompt: "Open topic files... only where relevant to
selection"), sizes for the two files the prompt names as examples:

| File | Bytes |
|---|---|
| `knowledge_base/02_trend_following.md` | 134,610 |
| `knowledge_base/14_backtesting_and_validation.md` | 179,902 |

If both example topic files are opened in a given cycle: **680,700 bytes** total before a selection
decision.

**Token estimate**: using a conservative ~4 bytes/token approximation for English/markdown text (no
tokenizer run against these specific files — this is an approximation, not a measured count):
- Mandatory-only (360,375 bytes): **≈ 90,000 tokens**
- Mandatory + best_strategy_so_far.py (366,188 bytes): **≈ 91,500 tokens**
- Mandatory + both example topic files (360,375 + 314,512 = 680,700 bytes total): **≈ 168,700 tokens**
