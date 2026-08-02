# Independent Consistency Audit Report — 2026-07-30

**Execution Statement**: Shell and Python commands WERE actually executed against this repository during this audit to dynamically parse ASTs, run tests (`scripts/check_context_budget.py`, `scripts/data_manifest.py`, `scripts/test_data_manifest.py`), inspect git commit diffs, verify file tracking, and validate calculations. Findings in Sections A, F, and G are empirically verified by runtime execution rather than inferred solely from static code reading.

---

## Section A: Silent defaults that change reported numbers

Enumerate every function in `user_data/research/` and `scripts/` (plus `freqtrade_dsr.py`) with default parameters affecting reported numbers, verdicts, or logs.

### 1. `freqtrade_dsr.deflated_sharpe_ratio()`
- **File & Line**: `freqtrade_dsr.py:81` (`trial_sharpe_var: float | None = None`)
- **Default value**: `trial_sharpe_var = None`
- **What it does**: When `trial_sharpe_var` is `None`, the function falls back to the Lo (2002) estimator proxy: `v = max((1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * (sr_hat ** 2)) / (t - 1), 1e-9)`.
- **Which callers rely on it**: Direct callers invoking `freqtrade_dsr.deflated_sharpe_ratio()` without passing cross-trial variance (e.g. `phase18_cointpair.py:386`, `phase19_sizingband.py:291`, `phase20_tailalloc.py:312`, `phase21_ivgate.py:754`).
- **Is relying on it ever wrong?**: YES — ALWAYS for cross-frequency comparisons. The proxy scales inversely as `~1/(t-1)` in observation/trade count `t`. Between 92 trades and 10,000 trades, the benchmark selection hurdle `sr0` shrinks ~10x. High-frequency strategies receive a drastically lower selection bar than daily strategies purely due to trade count.
- **Severity**: BLOCKING

### 2. `validator.validate()`
- **File & Line**: `user_data/research/validator.py:914` (`n_trials: Optional[int] = None`)
- **Default value**: `n_trials = None`
- **What it does**: When `n_trials` is `None`, DSR evaluation is skipped entirely (`dsr_res = {}`), and `Verdict.dsr` is left empty.
- **Which callers rely on it**: Any caller invoking `validator.validate(name, df, signal_fn)` without explicitly supplying `n_trials`.
- **Is relying on it ever wrong?**: YES. Manual lines 720 and 760 declare DSR ≥ 0.95 a mandatory promotion gate. Omitting `n_trials` produces a `Verdict` that silent-bypasses DSR validation.
- **Severity**: BLOCKING

### 3. `validator.walk_forward()` and `split_70_15_15()`
- **File & Line**: `user_data/research/validator.py:581` (`windows: int = 4`), `user_data/research/validator.py:568`
- **Default value**: `windows = 4`, percentage-based row splitting (`0.70`, `0.15`, `0.15`).
- **What it does**: Computes split boundaries strictly as percentages of row indices of whatever DataFrame is passed.
- **Which callers rely on it**: `validator.validate()` and all phase scripts calling `walk_forward()` or `split_70_15_15()`.
- **Is relying on it ever wrong?**: YES. Manual line 610 explicitly mandates: *"Pin splits by DATE, not by fraction, while the holdout is reserved."* Passing series extending past 2026-05-27 causes test/OOS windows to slide silently into the reserved holdout period.
- **Severity**: BLOCKING

### 4. `validator.signal_to_returns()`
- **File & Line**: `user_data/research/validator.py:426` (`fee: Optional[float] = None`, `execution_mode: Optional[str] = None`)
- **Default value**: `fee = None`, `execution_mode = None`
- **What it does**: When `fee` is `None`, falls back to `per_side_cost(execution_mode)`. If `fee` is passed as a float (e.g. `0.0009`), it overrides venue cost resolution. `execution_mode = None` resolves to `COST_MODEL["fill_assumption"]` ("taker" = 9 bps/side).
- **Which callers rely on it**: `validate()`, `walk_forward()`, and custom backtest loops across `user_data/research/`.
- **Is relying on it ever wrong?**: Relying on default `execution_mode` is wrong when evaluating maker execution sensitivity. Passing an explicit `fee` float bypasses cost model accounting.
- **Severity**: DEGRADING

### 5. `validator.monte_carlo()`
- **File & Line**: `user_data/research/validator.py:605` (`n_sims: int = 200`, `extra_cost: Optional[float] = None`, `execution_mode: Optional[str] = None`)
- **Default value**: `n_sims = 200`, `extra_cost = None`, `execution_mode = None`
- **What it does**: Runs 200 trade-order shuffling and block-bootstrap simulations without additional cost stress unless `extra_cost` is explicitly supplied.
- **Which callers rely on it**: `validator.validate()` line 955.
- **Is relying on it ever wrong?**: Relying on `extra_cost = None` omits cost-degradation stress testing required by Validation Requirement 10 (manual line 525).
- **Severity**: DEGRADING

### 6. Annualization Factor Audit Across Sharpe Paths
- **Paths checked**:
  - `user_data/research/validator.py:62,513,680`: `ANNUALIZATION_DAILY = 365`. Computes `_sharpe = ret.mean() / ret.std() * np.sqrt(365)` on daily strategy return series.
  - `freqtrade/data/metrics.py:339,470`: `calculate_sharpe` uses `annualization_factor = 365`, but divides mean daily profit by the standard deviation of PER-TRADE profits (`np.std(trades['profit_abs'])`).
  - `user_data/research/phase18_cointpair.py:63,118`, `phase19_sizingband.py:51,145`, `phase20_tailalloc.py:27,119`, `phase21_ivgate.py:46,159`: All use `ANN = 365` with `ret.mean() / ret.std() * np.sqrt(365)` on daily return series.
- **Agreement**: All research scripts and harness functions agree on constant `365` for daily crypto series (no 252 vs 365 conflict found in research code). However, Freqtrade's native `calculate_sharpe()` in `freqtrade/data/metrics.py:470` mixes cumulative daily mean return with per-trade standard deviation, distorting the annualized Sharpe compared to daily-return Sharpes in `validator.py`.
- **Severity**: DEGRADING

---

## Section B: Contradictions between standards

### 1. Data-acquisition ban vs. Reachability pre-gate external fetch
- **File & Line**: `PROJECT_OPERATOR_MANUAL.md:631` vs `PROJECT_OPERATOR_MANUAL.md:649,790`
- **Contradiction**: Line 631 states: *"A research cycle may not create, modify, delete or rebuild any file under user_data/data/..."* Pre-gate Step 1 (Reachability, line 790) requires confirming external data availability. Line 649 provides a carve-out for `user_data/research/data/<axis_name>/`, but if a candidate strategy requires new exchange market data under `user_data/data/`, the research cycle cannot fetch it and must block.
- **Severity**: DEGRADING

### 2. Reserved-holdout date rule vs. Walk-forward window construction
- **File & Line**: `PROJECT_OPERATOR_MANUAL.md:606` vs `user_data/research/validator.py:581,954`
- **Contradiction**: Line 606 states: *"All bars after 2026-05-27 are RESERVED HOLDOUT... Pin splits by DATE, not by fraction, while the holdout is reserved."* However, `validator.py`'s `walk_forward()` and `split_70_15_15()` are implemented using fixed fractional row slicing (`0.70/0.15/0.15` and 4 equal index quarters) with no date parameters. Running them on datasets extending past 2026-05-27 automatically evaluates test splits inside the reserved holdout.
- **Severity**: BLOCKING

### 3. Absolute DSR promotion gate vs. Relative DSR comparison in phase scripts
- **File & Line**: `PROJECT_OPERATOR_MANUAL.md:720` vs `PROJECT_OPERATOR_MANUAL.md:764` & `phase19_sizingband.py:291-292`
- **Contradiction**: Manual line 720 specifies DSR ≥ 0.95 as an absolute gate (not compared against benchmark DSR, because the benchmark is fixed at `n_trials=1`). However, line 764 and scripts `phase19_sizingband.py`, `phase20_tailalloc.py`, and `phase21_ivgate.py` evaluate candidate DSR relative to champion DSR at `n_trials=N_TRIALS`, penalizing the benchmark or comparing mismatched search debts.
- **Severity**: BLOCKING

### 4. Research budget variant limit vs. Zero-trial pre-gate expenditure
- **File & Line**: `PROJECT_OPERATOR_MANUAL.md:680` vs `PROJECT_OPERATOR_MANUAL.md:776`
- **Contradiction**: Line 680 caps research cycles at 3 strategy variants and states *"Each variant counts as one trial against n_trials."* Line 776 states *"A hypothesis killed at a pre-gate spends ZERO trials."* Evaluating pre-gate Steps 4 (Episode floor), 5 (Harm census), and 6 (TEST concentration) requires implementing and running candidate strategy variants, which consumes the 3-variant per-cycle limit and spends trials against `n_trials`.
- **Severity**: DEGRADING

### 5. `A-XXX` ops task definition vs. RESEARCH:OPS ratio cycle definition
- **File & Line**: `PROJECT_OPERATOR_MANUAL.md:570` vs `PROJECT_OPERATOR_MANUAL.md:599`
- **Contradiction**: Line 570 specifies that `A-XXX` ops tasks never advance the meta-review cycle counter, but line 599 requires tracking the RESEARCH:OPS cycle ratio every cycle and halting if <2:1. Ops tasks count as cycles in the denominator of the ratio while being excluded as cycles for meta-review advancement.
- **Severity**: COSMETIC

---

## Section C: Paper-only rules

Categorization of all mandatory rules in `PROJECT_OPERATOR_MANUAL.md` (lines 448–931):

### 1. MECHANICALLY ENFORCED
- **Director context budget cap (48 KB)**: Enforced by `scripts/check_context_budget.py`.
- **Review brief file size cap (4 KB)**: Enforced by `scripts/check_context_budget.py`.
- **Latest review brief selection by Task ID**: Enforced by `scripts/check_context_budget.py`.
- **Data directory manifest integrity (`user_data/data/` SHA-256)**: Enforced by `scripts/data_manifest.py`.
- **Taker all-in cost requirement (9 bps/side)**: Enforced by `user_data/research/validator.py` (`set_venue` / `per_side_cost`).
- **Maker optimistic fill assumption requires `adverse_selection_bps` and `basis`**: Enforced by `user_data/research/validator.py` (`set_fill_assumption`).
- **CAGR > 100% presumed defective warning**: Enforced by `user_data/research/validator.py` (`cost_model_warnings`).
- **Robustness stage payload structural verification**: Enforced by `user_data/research/validator.py` (`validate_robustness_payload`).

### 2. REVIEWER-CHECKED
- **Falsification condition literal transcription (`and`/`or`) check** (manual line 841).
- **Git diff `user_data/data/` immutability check** (manual line 635).
- **External data axis carve-out verification** (raw response saved, endpoint logged, `requests` used) (manual line 655).
- **Like-for-like promotion comparison verification** (manual line 698).

### 3. PAPER ONLY (Explicit List of Unenforced Rules)
The following rules exist ONLY in manual text and have no enforcing code, script check, or automated validation:
1. **Per-cycle research budget cap (max 3 variants, 1 optimization run)**: No script checks or limits variant execution in `validator.py` or phase scripts.
2. **RESEARCH:OPS cycle ratio monitoring & stop-and-reassess signal (<2:1 ratio)**: Logged in `research_metrics.md`, but no script computes the ratio or triggers a stop signal.
3. **Reserved holdout date enforcement (post 2026-05-27)**: No code in `validator.py` checks bar dates against 2026-05-27.
4. **Date-pinned split construction vs percentage splitting**: `validator.py` implements percentage splitting without date pins.
5. **Zero-cost pre-gate 6-step ordering & zero-trial expenditure**: No harness enforces step sequence or prevents trial logging during pre-gate execution.
6. **Promotion comparison 5-criterion rule (Jobson-Korkie paired SE, MaxDD ≤ 1.25x benchmark, etc.)**: Unimplemented in `validator.py`.
7. **Perps benchmark pre-registration (`n_trials=1` equal-weight buy-and-hold)**: Benchmark not computed or committed (`A-005` in backlog).
8. **DSR absolute promotion gate (≥0.95) in `validator.validate()`**: `validate()` attaches `Verdict.dsr` but does not fail `Verdict.passed` if `dsr < 0.95`.

---

## Section D: Divergent sources of truth

Numeric thresholds, costs, and limits across manual, metrics, configs, validator, and scripts:

| Threshold / Cost / Limit | Location 1 (Value) | Location 2 (Value) | Location 3 (Value) | Disagreement / Status |
|---|---|---|---|---|
| **DSR threshold** | `PROJECT_OPERATOR_MANUAL.md:720,760` (`≥0.95`) | `freqtrade_dsr.py:208` (`0.95`) | `validator.py:762` (`0.95`) | Numeric values match (0.95). Implementation diverges: manual mandates absolute gate for promotion, `validator.validate()` omits DSR from `passed`, phase scripts used relative DSR comparison. |
| **Per-side taker cost** | `PROJECT_OPERATOR_MANUAL.md:544` (`9.0 bps / 0.0009`) | `validator.py:280-305` (`0.0009`) | `user_data/config_perp.json:112` (`0.0009`) | Values match for perps (9 bps/side). `user_data/config.json` lacks `"fee"` key entirely (falls back to 15 bps spot default). |
| **Fee key in configs** | `user_data/config_perp.json:112` (`"fee": 0.0009`) | `user_data/config.json` (**MISSING KEY**) | N/A | `config.json` missing `"fee"` key; backtests using `config.json` fall back to Freqtrade exchange defaults (0.0015). |
| **max_open_trades** | `user_data/config.json:2` (`2`) | `user_data/config_perp.json:24` (`9`) | N/A | `config.json` caps trades at 2; `config_perp.json` caps trades at 9. |
| **n_trials counter** | `PROJECT_OPERATOR_MANUAL.md:588` (Resets to 0 for perps) | `research/research_metrics.md:82` (`100` spot trials) | `validator.py:918` (`n_trials = None`) | Spot total is 100; perps starts at 0; `validator.py` defaults to `None` (omits DSR calculation). |
| **Research budget** | `PROJECT_OPERATOR_MANUAL.md:680` (3 variants / cycle) | `NEXT_TASK.md:188` (0 DSR trials for T-036) | N/A | Task-specific budget overrides global default; no code enforcement. |
| **Context budget cap** | `PROJECT_OPERATOR_MANUAL.md:49` (`48 KB`) | `scripts/check_context_budget.py:34` (`48 KB`) | N/A | PERFECT AGREEMENT (48 KB / 49,152 B). |
| **Review-brief cap** | `PROJECT_OPERATOR_MANUAL.md:848` (`4 KB`) | `scripts/check_context_budget.py:47` (`4,096 B`) | N/A | PERFECT AGREEMENT (4 KB / 4,096 B). |
| **Reserved holdout date** | `PROJECT_OPERATOR_MANUAL.md:606` (`2026-05-27`) | `research/research_index.md` (`2026-05-27`) | `validator.py` (**MISSING**) | Date documented in manual and index, but omitted from `validator.py` code. |
| **Meta-review cadence** | `PROJECT_OPERATOR_MANUAL.md:993` (`every 25-50 cycles`) | `research/research_index.md:3` (`25 research cycles`) | `STANDING_DIRECTIVES.md` (`25 research cycles`) | Manual allows 25-50 range; index and directives specify fixed 25. |

---

## Section E: Dead and dangling references

### 1. Six untracked review briefs cited by `research_index.md`
- **Files**: `research/review_briefs/T-029_brief.md`, `T-030_brief.md`, `T-031_brief.md`, `T-032_brief.md`, `T-034_brief.md`, `T-035_brief.md`
- **What is wrong**: `research/research_index.md` cites these six files as primary evidence for cycle verdicts. All six files are untracked (`??`) in git. On a clean clone, these files are missing. (Logged in backlog as item `A-004`).
- **Severity**: DEGRADING

### 2. Hardcoded Windows absolute paths across `user_data/research/` scripts
- **Files**:
  - `user_data/research/phase18_cointpair.py:50,51` (`C:/Users/Comec/Projects/freqtrade/...`)
  - `user_data/research/phase18_diag_spread_drift.py:12`
  - `user_data/research/phase19_diag_bound.py:14`
  - `user_data/research/phase19_sizingband.py:29,30,41`
  - `user_data/research/phase1_blend.py:12`
  - `user_data/research/phase20_tailalloc.py:14,15,26`
  - `user_data/research/phase21_diag_b3a_verify.py:18`
  - `user_data/research/phase21_diag_leadlag_fix.py:36,37`
  - `user_data/research/phase21_ivgate.py:33,34,59,60`
  - `user_data/research/phase22_diag_p2_verify.py:23,24`
  - `user_data/research/phase22_ivsizing.py:32,33,59,60`
  - `user_data/research/phase23_effratio.py:28,29,54`
  - `user_data/research/phase24_erscale.py:6,7,31`
  - `user_data/research/phase25_adxgate.py:50,51,82`
  - `user_data/research/phase2_robustness.py:11`, `phase3_new_paradigms.py:11`, `phase4_deep_validation.py:20`, `phase5_2018_stress.py:3`, `phase6_cross_asset.py:10,16,85`, `phase7_universe_portfolios.py:11,17,126`, `phase8_portfolio_vol.py:10,16`, `phase9_finalists.py:9,15`, `phase_logistic.py:7`, `run_batch.py:4`, `test_dryrun_monitor.py:50,51,52,367,368,394,395,421,422,539,540,587,588`
  - `research/scratch/t024_pregate.py:2,3,13`, `research/scratch/t024_trial.py:2,3,13`
- **What is wrong**: Over 30 research scripts contain hardcoded Windows paths (`C:/Users/Comec/Projects/freqtrade`). Execution fails on any other directory path, username, or non-Windows OS.
- **Severity**: BLOCKING

### 3. Untracked research scripts under `user_data/research/` due to `.gitignore`
- **Files**: `user_data/research/phase23_effratio.py`, `phase24_erscale.py`, `phase25_adxgate.py`, `phase_feargreed.py`, `phase_logistic.py`, `test_dryrun_monitor.py`, `user_data/research/data/`
- **What is wrong**: `.gitignore` contains `user_data/*`, causing new files under `user_data/research/` to be ignored by git unless force-added (`git add -f`). These research scripts exist locally but are uncommitted and will not exist on a clean clone.
- **Severity**: DEGRADING

### 4. Task T-038 citation in `research_index.md` without brief
- **File**: `research/research_index.md`
- **What is wrong**: `research_index.md` cites `T-038`, but `research/review_briefs/T-038_brief.md` does not exist.
- **Severity**: COSMETIC

---

## Section F: Untested surface

### 1. DSR Trial-Variance Ledger Module in `validator.py` (Last 5 Commits)
- **Functions Added/Modified**:
  - `read_trial_ledger(path: Optional[Path] = None)` (`validator.py:153`)
  - `trial_sharpe_variance(path: Optional[Path] = None)` (`validator.py:172`)
  - `_load_dsr_module()` (`validator.py:190`)
  - `deflated_sharpe(returns, n_trials, ledger_path=None)` (`validator.py:200`)
  - `dsr_warnings(dsr_result: dict)` (`validator.py:220`)
  - `validate(..., n_trials=None)` (`validator.py:914`)
- **Automated Test Coverage**: **0%**. None of these functions are tested by automated unit or integration tests anywhere in the repository. (Logged in backlog as item `A-003`).
- **Severity**: BLOCKING

### 2. Execution Mode Propagation Across 6 Distinct Call Sites in `validate()`
- **File & Lines**: `user_data/research/validator.py:938,950,951,952,954,955`
- **Distinct Call Sites**:
  1. Line 938: `signal_to_returns(df, sig, execution_mode=execution_mode)` (Full dataset)
  2. Line 950: `signal_to_returns(df_tr, sig_tr, execution_mode=execution_mode)` (Train split)
  3. Line 951: `signal_to_returns(df_vl, sig_vl, execution_mode=execution_mode)` (Val split)
  4. Line 952: `signal_to_returns(df_te, sig_te, execution_mode=execution_mode)` (Test split)
  5. Line 954: `walk_forward(df, signal_fn, execution_mode=execution_mode)` (Walk-forward sub-runs)
  6. Line 955: `monte_carlo(rets, trs, execution_mode=execution_mode)` (Monte Carlo sub-runs)
- **Test Gap**: A top-level-only test checking `Verdict.cost_model` or full-window returns would pass even if sub-runs (train/val/test/wf/mc) omitted `execution_mode` and silently defaulted to `"taker"`.
- **Severity**: DEGRADING

---

## Section G: Reproducibility from a clean clone

1. **Absolute Windows Path Failure**: All 30+ phase scripts in `user_data/research/` break immediately on Linux or any different path due to hardcoded `C:/Users/Comec/Projects/freqtrade` strings in `sys.path` and data directory constants (`FUT_DIR`, `SPOT_DIR`, `DATA_DIR`).
2. **Windows OS Dependencies**: `user_data/dryrun_keepalive.ps1` and `NEXT_TASK.md` instructions depend on Windows Task Scheduler (`schtasks`), PowerShell (`Get-WinEvent`, `Get-Process`), and Windows Event Log providers (`Kernel-Power`). These cannot execute on Linux.
3. **Missing Uncommitted Briefs and Research Scripts**: 6 review briefs (`T-029`..`T-035`) and research scripts (`phase23`..`phase25`, `phase_feargreed`, `test_dryrun_monitor`) are uncommitted/ignored by `.gitignore` and will be absent on a fresh clone.
4. **Data Manifest Verification Status**: `python scripts/data_manifest.py verify` **PASSES**. All 52 data files under `user_data/data/` and `user_data/data/MANIFEST.json` are committed to git and match their SHA-256 hashes.

---

## OUTPUT — Findings That Could Change a Research Conclusion If Left Unfixed

The following single list contains EVERY finding from this audit that could change a research conclusion if left unfixed:

1. **`freqtrade_dsr.deflated_sharpe_ratio()` silent fallback to Lo-2002 estimator proxy when `trial_sharpe_var=None`** (`freqtrade_dsr.py:81,121-128`): The proxy scales selection hurdle `sr0` as `~1/(t-1)` in trade count `t`, shrinking the DSR hurdle ~10x between 92 and 10,000 trades. High-frequency strategies clear a drastically lower bar than low-frequency ones purely due to trade count. (Severity: **BLOCKING**)

2. **`validator.validate()` `n_trials` defaults to `None`, silently skipping DSR calculation** (`user_data/research/validator.py:914,979`): When `n_trials` is omitted, `Verdict.dsr` is empty and DSR warnings are bypassed, allowing candidates to pass validation without evaluating the mandatory DSR promotion gate (manual lines 720, 760). (Severity: **BLOCKING**)

3. **`validator.walk_forward()` and `split_70_15_15()` use percentage row slicing without date pins** (`user_data/research/validator.py:568,581,954`): Operating on row index fractions rather than pinned dates causes OOS/TEST windows to slide into the reserved holdout period (post 2026-05-27) whenever datasets are extended. (Severity: **BLOCKING**)

4. **Reserved holdout boundary (2026-05-27) missing from validation code** (`PROJECT_OPERATOR_MANUAL.md:606` vs `user_data/research/validator.py`): The mandatory holdout date is defined in manual text but unreferenced in code, allowing backtests and walk-forward evaluations to evaluate post-2026-05-27 bars without warning. (Severity: **BLOCKING**)

5. **Relative DSR comparison against champion in phase scripts vs absolute benchmark DSR gate** (`PROJECT_OPERATOR_MANUAL.md:720` vs `phase19_sizingband.py:291-292`, `phase20_tailalloc.py:312-313`): Scripts evaluate candidate DSR relative to champion DSR at `N_TRIALS`, penalizing the benchmark or comparing mismatched search debts rather than enforcing the absolute ≥0.95 DSR promotion gate at `n_trials=1`. (Severity: **BLOCKING**)

6. **100% untested DSR trial-variance ledger module in `validator.py`** (`user_data/research/validator.py:153-240,979`): All 5 functions managing DSR trial ledger parsing, cross-trial variance calculation, and DSR warning generation have zero automated unit/integration tests, risking silent failures or fallback to the frequency-dependent Lo-2002 proxy. (Severity: **BLOCKING**)

7. **Hardcoded Windows absolute paths in research scripts** (`user_data/research/phase18_cointpair.py:50`, `phase19_sizingband.py:29`, `phase20_tailalloc.py:14`, `phase21_ivgate.py:33`, `phase22_ivsizing.py:32`, etc.): Hardcoded `C:/Users/Comec/Projects/freqtrade` paths prevent execution and verification on fresh clones, different paths, or non-Windows environments. (Severity: **BLOCKING**)
