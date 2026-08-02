# Independent consistency audit — 2026-07-30

**Auditor:** independent agent, no involvement in the 2026-07-28/29/30 repair work.
**Branch:** `repo-repair-2026-07-28` @ `900635b0d`.
**Scope:** read-only. No file under `user_data/data/` was touched; no git command that
mutates the working tree or index was run.

## Execution statement

**I executed shell and Python commands against this repository.** Sections A, F and G are
**VERIFIED BY EXECUTION**, not inferred. Python 3.14.3 and 3.13.0 are both present;
`pandas 3.0.2 / numpy 2.4.4 / scipy 1.17.1` are importable. `validator.py` imports cleanly
and its data-integrity gate passes on this machine. Every empirical claim below was produced
by a command whose output I read; the probe scripts were written to the session scratchpad,
not into the repo.

Two disclosures:

1. **Output path collision.** I was told to write to `research/AUDIT_2026-07-30_gemini.md`.
   That file already existed (22,992 B) with an mtime of **17:53 today — during this
   session**, and was absent from the session-start `git status`. A concurrent audit is
   writing there. I did not read it and did not overwrite it; this report is at
   `research/AUDIT_2026-07-30_opus.md` instead, and the full text is emitted verbatim in
   chat as instructed.
2. **Incidental exposure.** Two repo-wide `grep` sweeps (for `40 KB|48 KB` and for
   meta-review cadence strings) matched inside that file and printed three of its lines
   before I could exclude the path. Both findings those lines touched had already been
   derived independently in the same command output, from `OPS_BACKLOG.md:47` and
   `scripts/check_context_budget.py:34`. No finding in this report originates from that file.

---

## A. Silent defaults that change reported numbers

**Method:** AST sweep of every function definition under `user_data/research/` and
`scripts/` (excluding `quarantine/`, `scratch/`, `archive/`, `__pycache__`), extracting every
non-trivial default. 197 defaults across 30 files. The great majority are strategy
hyperparameters inside individual phase scripts (`_rsi(n=14)`, `supertrend_4h(mult=3.0)` …) —
those are the hypothesis, not a hidden default, and are excluded below. What follows is the
complete set that sits in shared harness code and materially moves a number that reaches a
report, a Verdict or a log.

### A.1 The annualization constants do NOT agree

There is exactly one annualization constant, `ANNUALIZATION_DAILY = 365`
(`user_data/research/validator.py:62`), and `validate()` accepts `bars_per_year` to override
it (`:914`). **Two of the six sub-runs inside `validate()` ignore that override.**

| Path | Line | Annualization actually used |
|---|---|---|
| `metrics()` full / train / val / test | `:940`, `:950–952` | caller's `bars_per_year` ✅ |
| `walk_forward()` → `metrics(rets, trs)` | `:597` | **hardcoded 365** ❌ |
| `monte_carlo()` → `np.sqrt(len(shuffled) / (len(returns) / ANNUALIZATION_DAILY))` | `:628` | **hardcoded 365** ❌ |
| `_sharpe()` and every Kaufman diagnostic | `:680`, `:702`, `:742`, `:767`, `:803` | default 365 unless passed |

Verified on 4,000 synthetic **hourly** bars with `bars_per_year=8760`:

```
full   sharpe (8760): 2.565      full  sharpe (365): 0.5236   ratio 4.8988 = sqrt(24) ✅
wf window sharpes   : [0.7002, 1.4911, 2.0505, -0.646]   identical under both  ratio 1.0 ❌
mc  p50 sharpe      : 0.339                              identical under both  ratio 1.0 ❌
```

A single Verdict therefore reports a full-window Sharpe of 2.57 next to walk-forward window
Sharpes of 0.70–2.05 that are **4.9× smaller for no reason except which function computed
them**. `walk_forward()` takes no `bars_per_year` parameter at all, so a caller cannot fix
this without editing the harness. This is inert for the spot program (all daily) and becomes
live the moment the perps program touches 1h or 5m bars, which is its stated target.
**Severity: BLOCKING.**

`ANNUALIZATION_DAILY = 365` itself is correct for crypto and is used consistently by
`batch3/4/5.py` and `run_batch.py`, which all pass `bars_per_year=365` explicitly.
`PROJECT_OPERATOR_MANUAL.md:748` also hardcodes `sqrt(365)` into the promotion-criterion-3
formula, which will be wrong for any sub-daily candidate.

### A.2 Monte Carlo simulation counts and shock parameters

`monte_carlo(returns, trades, n_sims=200, extra_cost=None, execution_mode=None)`
(`validator.py:605`).

- `n_sims=200` — **not reachable from `validate()`**, which calls
  `monte_carlo(rets, trs, execution_mode=execution_mode)` at `:955` with no `n_sims`. Every
  Verdict's MC is 200 sims. Separately, `print_verdict()` at `:1041` hardcodes the string
  `"Monte Carlo (200 sims, +1 extra round trip of cost)"` — if a caller does pass `n_sims`,
  the printed label lies. `research_metrics.md` cites champion MC figures at **1,000 sims**,
  which cannot have come from this function.
- `rng = np.random.default_rng(42)` (`:623`) — a fixed seed. The pass/fail gate at `:973`
  (`mc_p5_sharpe < 0`) is decided on one seed, with no seed-robustness check. The project's
  own H-TailAlloc precedent (10 seeds) shows it knows better.
- `extra_cost=None` → `round_trip_cost(execution_mode)` = 18.0 bps. Correct and documented.
- `shock_day_mask(method="p99", pctile=0.99, sigma_mult=3.0, vol_lookback=30)` (`:651`) —
  these four defaults *are* the two headline numbers in `research_metrics.md:173` ("14.6%
  static p99 def / 44.6% 3σ-rolling def"). Relying on them is fine only because the report
  states which definition it used; a report that omits the method is uninterpretable.
- `wf_window_stability(window_counts=(3,4,5,6), oos_start_frac=0.5)` (`:764`) — the
  "downgrade trigger (≥2 minority configs)" recorded in `research_metrics.md:174` is defined
  against exactly these defaults. Changing `window_counts` changes the trigger silently.
- `rolling_sharpe_series(window_days=548)` (`:801`) — the "rolling 18-month Sharpe" row.

### A.3 The Monte Carlo stage computes the same number 200 times

`monte_carlo()` shuffles the per-trade P&L vector and then computes, per simulation:

```python
shuffled = rng.permutation(pnl)
eq   = np.cumprod(1 + shuffled)
rets = pd.Series(shuffled)
s    = rets.mean() / rets.std() * sqrt(...)
finals.append(eq[-1] - 1)
```

`mean`, `std` and `∏(1+xᵢ)` are **all invariant under permutation**. Every simulation
produces the identical Sharpe and the identical final equity. Verified on 120 synthetic
trades at 500 sims:

```
mc_p5_sharpe   -1.7761090156430683
mc_p50_sharpe  -1.7761090156430681
mc_p95_sharpe  -1.7761090156430674
mc_p5_return   -0.6822815008840506
mc_p50_return  -0.6822815008840504
```

The spread is float round-off at the 15th decimal. **`mc_p5_sharpe` is not a 5th percentile
— it is the point estimate, relabelled.** The MC gate in `validate()` (`:973`) is therefore
just "cost-stressed Sharpe < 0", and every reported "MC p5" figure is a distributional claim
about a degenerate distribution.

`PROJECT_OPERATOR_MANUAL.md:526` requires MC over "shuffled trade order, removed random
trades, increased slippage, increased fees, and randomized execution timing". Of those five,
the harness implements increased cost (real), shuffled order (mathematically inert), and
none of the other three. **Severity: BLOCKING.**

### A.4 Cost resolution — clean

This is the one area that holds up. `per_side_cost(execution_mode=None)` (`:355`) falls back
to `COST_MODEL["fill_assumption"]`; `round_trip_cost()` (`:379`) delegates to it;
`signal_to_returns(fee=None)` (`:426`) resolves from `per_side_cost()` at `:447`. Verified:
taker 9.0 bps/side, 18.0 bps round trip, matching `PROJECT_OPERATOR_MANUAL.md:543` and
`config_perp.json:111` (`"fee": 0.0009`) exactly.

`adverse_selection_bps = None` is a **deliberate** no-default that raises on the maker path
(`:373–375`, `:346–347`) — the correct pattern, and the counter-example the rest of this
section should have followed.

`execution_mode` threading was tested end-to-end by running the same signal under `taker`
(9 bps) and `maker_optimistic` (42 bps) and comparing every sub-run. All six differ:

```
full  0.9283 → 0.1686   train 0.9552 → 0.2149   val 1.9715 → 1.1744   test −0.3907 → −1.1723
wf[0] −0.3419 → −1.1496  wf[1] 1.0394 → 0.1047   wf[2] 1.3153 → 0.4410  wf[3] 2.0802 → 1.4207
mc    0.7175 → −0.2118
```

**No sub-run silently uses the default.** A-003's concern here is unfounded on current code.

### A.5 DSR inputs

`deflated_sharpe(returns, n_trials, ledger_path=None)` (`:200`) →
`trial_sharpe_variance()` → `read_trial_ledger()`. The ledger currently holds **zero data
rows**, so `variance` is `None` and `freqtrade_dsr.deflated_sharpe_ratio()` takes the Lo-2002
proxy. Verified live: `{'variance': None, 'n_trials_recorded': 0, 'source': 'estimator_proxy'}`.

`freqtrade_dsr.deflated_sharpe_ratio(returns, n_trials, trial_sharpe_var=None)`
(`freqtrade_dsr.py:81`) — the archetype defect, unchanged. Reproduced at `n_trials=30`:

| n_obs | proxy sr0 | proxy DSR | ledger (var=0.01) sr0 | ledger DSR |
|---|---|---|---|---|
| 92 | 0.2169 | 0.0143 | 0.2073 | 0.0516 |
| 500 | 0.0928 | 0.0251 | 0.2073 | 0.0000 |
| 2,000 | 0.0464 | 0.4609 | 0.2073 | 0.0000 |
| 10,000 | 0.0207 | **0.8558** | 0.2073 | **0.0000** |

Same generating process, same search intensity: the proxy path swings DSR from 0.01 to 0.86
purely on observation count. `evaluate_freqtrade(dsr_threshold=0.95)` (`freqtrade_dsr.py:209`)
calls `deflated_sharpe_ratio(returns, n_hyperopt_epochs)` **without** `trial_sharpe_var` — so
the module's own public one-call API, which the manual names as *the* DSR tool
(`PROJECT_OPERATOR_MANUAL.md:760`), is permanently on the defective path.

One further design point on the fix itself. `validate()` feeds **per-bar** returns to
`deflated_sharpe()` (`:982`, `rets["ret_net"]`), so the resulting field — named
`sr_hat_per_trade` by `freqtrade_dsr.py:133` — is a per-*bar* Sharpe. The ledger column that
is meant to receive it (`research/trial_sharpe_ledger.csv:40`) is documented as "per-trade".
`freqtrade_dsr.returns_from_freqtrade()` produces genuinely per-trade `profit_ratio` values.
If the ledger is populated from both paths, its cross-trial variance mixes per-bar and
per-trade Sharpes — reintroducing exactly the frequency contamination the ledger exists to
remove. Nothing in the CSV header, the writer (there is none), or the reader distinguishes
them.

### A.6 Walk-forward window construction

`walk_forward(df, signal_fn, windows=4)` (`:581`): `is_end = n·(0.5 + (k−1)·0.10)`,
`oos_end = n·(0.5 + k·0.10)` for k=1..4.

- OOS windows are `[0.50,0.60] [0.60,0.70] [0.70,0.80] [0.80,0.90]`. **The last 10% of the
  series is never evaluated** — 312 bars on BTC 1d, i.e. everything after 2025-09-09.
- The docstring says "prior 60%+ is IS"; the code uses 50%. Cosmetic but misleading.
- OOS windows 1–2 lie entirely inside the 70/15/15 **TRAIN** region `[0, 0.70]`. There is no
  re-fitting anywhere in `walk_forward()` — `signal_fn` is simply applied to the slice — so
  "walk-forward" here is segmented evaluation, not walk-forward optimization. Manual
  Validation Requirement 1 ("Never optimize and evaluate using the same period") is not
  tested by this function.

### A.7 Split construction

`split_70_15_15(df)` (`:574`) — pure fractions of whatever it is handed. See B.2 / D.9; this
is the single highest-consequence default in the file.

### A.8 Risk-free rate

**There is none, anywhere.** `metrics()` (`:522`) computes `ret.mean()/ret.std()·sqrt(bpy)`;
`_sharpe()` (`:683`) the same; `freqtrade_dsr.deflated_sharpe_ratio()` (`:108`) computes
`sr_hat = mean_r / sd_r`. Every Sharpe in this project is excess-of-zero. That is a defensible
convention for crypto, but it is stated in no document I could find, and the perps program
introduces a funding-rate carry term that makes "excess of zero" a live modelling choice
rather than a formality. `research/OPS_BACKLOG.md:219` already flags funding treatment as
must-be-stated for A-005; the same should hold for the risk-free rate.

### A.9 `family_from_results_dir(results_dir=RESULTS_DIR)` (`:852`)

Default reads **every** `*.json` in `user_data/research/results/`. Verified: **63 verdict
files, 63 of which carry no `cost_model` snapshot** — i.e. all are pre-2026-07-28, computed
at 15 bps/side with zero spread on spot. A perps cycle that passes
`family=family_from_results_dir()` gets a Kaufman rank/percentile computed against a
population the manual declares **void** ("Like-for-like or void",
`PROJECT_OPERATOR_MANUAL.md:696`), and that number lands on the Verdict and in the report.
**Severity: DEGRADING.**

---

## B. Contradictions between standards

Read as a single document, the DIRECTOR-MANDATORY region (`:439`–`:931`) contains the
following pairs that cannot both be satisfied.

### B.1 The pre-gate ladder mandates screening on the TEST split; OOS testing forbids it

- Validation Requirement 2 (`:461`): "Reserve unseen data. … Final evaluation must be
  performed exclusively on unseen data."
- Promotion rule criteria 2 and 3 (`:730`, `:731`): the primary metric is **TEST-split
  Sharpe**.
- Pre-gate ladder gate 6 (`:799`): "**TEST concentration** — Share of TEST postdating the
  last materially-affected day, plus a >0-affected-days check", run **"before any trial is
  spent"** (`:776`).

Gate 6 requires computing where in the TEST split the construct fires, and *killing the
hypothesis on the answer*, before any trial exists. T-029 and T-030 were both rejected on
exactly this gate. Any hypothesis that survives gate 6 has been selected in part on its TEST
behaviour, and is then judged on TEST-split Sharpe by criteria 2–3. The TEST split is not
out-of-sample for anything that reaches promotion. **Severity: BLOCKING.**

### B.2 Reserved holdout vs. the splits the harness actually computes

`PROJECT_OPERATOR_MANUAL.md:606–613` states the problem correctly — "`split_70_15_15()` and
`walk_forward()` compute boundaries as percentages … a data top-up slides the TEST window
forward into the holdout silently — no error, no warning" — and then mandates "**Pin splits
by DATE, not by fraction**". **No date-pinned split function exists.** `validate()`
unconditionally calls `split_70_15_15(df)` at `:946` and `walk_forward(df, …)` at `:954`;
a caller cannot substitute date-pinned splits without rewriting `validate()`.

Verified against the committed feathers:

```
BTC_USDT-1d.feather   3111 bars  2018-01-11 .. 2026-07-18
   split_70_15_15 -> TEST = 2025-04-08 .. 2026-07-18
   RESERVED HOLDOUT bars (> 2026-05-27) in file: 52   of which inside TEST split: 52
ETH_USDT-1d.feather   2422 bars  2019-12-01 .. 2026-07-18
   split_70_15_15 -> TEST = 2025-07-20 .. 2026-07-18
   RESERVED HOLDOUT bars (> 2026-05-27) in file: 52   of which inside TEST split: 52
```

**Every reserved-holdout bar is already inside the TEST split for both 1d spot feathers.**
Anyone who calls `validator.validate()` on `load('BTC/USDT','1d')` today evaluates on the
holdout, and nothing raises, warns, or records it. The rule and the harness are in direct
contradiction, and the harness wins because it is the thing that runs.
**Severity: BLOCKING.**

### B.3 The perps holdout declaration selects zero bars

`:606` declares "**All bars after 2026-05-27 are RESERVED HOLDOUT**". `:619–621` declares the
perps mechanism: "the holdout is the most recent 20% of the series by CALENDAR DATE, computed
from the download end date … `end − 0.20 × S`".

The committed perp futures data ends **exactly at 2026-05-27**
(`BTC_USDT_USDT-1d-futures.feather`, 2,339 bars, 2020-01-01 .. 2026-05-27). Applying the
blanket date: **0 holdout bars**. Applying the declared mechanism: span 2,338 days, 20% =
467.6 days, boundary **2025-02-13** — 15 months of holdout. The two rules disagree by the
entire holdout. A Director reading the region top-to-bottom gets whichever answer they read
last, and `:626` says a boundary chosen after looking at data "is not a holdout, and every
result measured against it is in-sample". **Severity: BLOCKING.**

### B.4 The pre-gate ladder requires an incumbent the perps program does not have

Gate 2 (`:795`): "Is the signal distinct from what the strategy already uses? →
**Correlation vs the incumbent's own signals**". Gate 4 (`:797`): "enough events the strategy
is **in-market** for". Gate 6 (`:799`): affected days relative to an existing construct. All
six numeric precedents cited are champion overlays.

`research/research_index.md:21`: "**The perps program has NO champion.**" Gates 2, 4 and 6 are
unevaluable for the first perps cycle, yet the ladder is mandatory and is to be evaluated "in
that order, stopping at the first failure". The manual gives no rule for a gate that cannot be
computed. **Severity: DEGRADING** (it will produce a blocked or improvised first cycle, not a
wrong number).

### B.5 Research budget vs. the pre-gate ladder — no conflict, but an unstated boundary

`:680` sets 3 variants / 1 optimization run and `:683` prices each variant as one trial;
`:684` exempts pre-gate kills. The six ladder gates are not variants and do not consume
budget — these two are consistent. What is **unstated** is whether constructing the object a
gate needs (gate 5's harm census and gate 6's TEST-concentration check both require a
concrete construct with concrete parameters) counts as a variant. Under the letter of `:686`
("The Director may assign fewer, never more"), an Engineer who tries two parameterisations
inside a pre-gate has either spent two of three variants or zero, and the manual does not say
which. **Severity: DEGRADING.**

### B.6 Promotion comparison vs. the DSR gate — the DSR is computed on the wrong window

Criterion 1 (`:723`) is an absolute DSR ≥ 0.95 gate. Criteria 2–4 are all TEST-split.
`validate()` computes DSR from `rets["ret_net"]` — the **full window** (`:982`) — not from
`rets_te`. Meanwhile `research/research_index.md:14` is unambiguous: "**Judge on TEST-set /
walk-forward numbers only. Full-window Sharpe runs 2-4× inflated here.**"

So criterion 1 is evaluated on the one series the project's own standing constraint says
never to judge on, and it is the criterion the manual calls "an **absolute gate**".
**Severity: BLOCKING.**

Criterion 3's Jobson–Korkie/Memmel formula (`:743`) has **no implementation anywhere** —
`grep -ri "jobson|memmel|se_delta"` across every `.py` in the repo returns nothing, and
`metrics()` returns only an annualised Sharpe rounded to 4 dp, not the per-period Sharpe and
correlation the formula requires. A-005 correctly identifies that the benchmark return series
must be committed for this reason, but the computation itself does not exist.

### B.7 A-XXX ops rule vs. the RESEARCH:OPS ratio's definition of a cycle

`PROJECT_OPERATOR_MANUAL.md:574–577`: an `A-XXX` task "**never advances the meta-review cycle
counter**"; `:599`: "**track the RESEARCH:OPS cycle ratio** … **Below 2:1 is a
stop-and-reassess signal**".

`research/research_metrics.md:134`: "`A-XXX` tasks do **not** advance the meta-review counter
and **are not cycles for any other purpose** — but they DO count here, in the OPS column."

Two problems:

1. **Self-defeating metric.** The manual defines the ratio over *cycles* and defines A-XXX as
   not-a-cycle. Strictly applied, the OPS column has zero entries by construction and the
   ratio can never breach — which is precisely the metric that was created to catch the
   0.73:1 breach. That breach was only measurable because the eleven ops cycles carried `T-`
   prefixes; under the new ID rule they would all be `A-XXX` and therefore invisible.
   `research_metrics.md` patches this by fiat, in a file the manual does not designate as a
   standards location.
2. **An invented suspension.** `research_metrics.md:129` declares "**The 2:1 floor applies
   only after 6 completed perps cycles**" and marks the floor "Not yet in force". That
   carve-out appears nowhere in the manual. The manual's own rule at `:74–76` — "A new
   *standard* … belongs inside this manual's marked region" — is violated by the very file
   the standard delegates measurement to.

**Severity: DEGRADING.**

### B.8 Data-acquisition ban vs. the reachability pre-gate — partially resolved, residue remains

The carve-out at `:644–667` (commit `03cd428d0`) does resolve the headline conflict for a
**new** axis. Two residues:

- The carve-out mandates writes to `user_data/research/data/<axis_name>/` and that the raw
  response be "**committed**". `user_data/*` is gitignored (`.gitignore:7`), and
  `git ls-files user_data/research/data` returns **nothing** — `cot/`, `dvol/`,
  `fear_greed/`, `funding/` are all untracked. `research_metrics.md:233` cites
  `user_data/research/data/fear_greed/fng_raw.json` as the auditability evidence for T-035;
  on a fresh clone it does not exist. The carve-out never says `git add -f`.
- `scripts/data_manifest.py` covers **only** `user_data/data/` (`data_manifest.py:53`). The
  directory the carve-out now mandates as the destination for all new research data is
  outside the integrity gate that exists because of three fabrication events. Nothing detects
  a post-hoc edit to a saved raw response — which is exactly the fabrication mode `:666`
  warns about.

**Severity: DEGRADING.**

### B.9 The manual's "quoted verbatim" DSR block quotes text that no longer exists

`PROJECT_OPERATOR_MANUAL.md:758` — "Quoted verbatim from `research/research_index.md`
standing constraints:" — followed by:

> **DSR gate mandatory**: any candidate reports Deflated Sharpe Ratio (`freqtrade_dsr.py`) at
> honest cumulative `n_trials` and must clear **≥0.95** … `research_metrics.md` is
> authoritative; the two counts must always match.

The string "DSR gate mandatory" occurs **nowhere except this manual**. The actual text at
`research/research_index.md:11–13` reads "**DSR gate ≥0.95** at honest cumulative `n_trials`
(spot program ended at **100**; perps starts at 0). Standard is in
`PROJECT_OPERATOR_MANUAL.md` … `research_metrics.md` is authoritative for the count."

Commit `900635b0d` ("fix 5: DSR threshold precedence across its three copies") edited the
paragraph directly beneath this quote and did not check the quote itself. This is the
same class of defect as the rule added one commit earlier — "falsification conditions must be
transcribed literally" (`:816`) — applied to the manual's own attributions.

*(For contrast, I checked the other four quoted blocks. `:782` against
`strategy_research_notes.md:16–18`, `:788` against `:714–715`, `:803` against `:224–227`, and
`:810` against lesson 4 — **all four are literal**. Only the DSR block has drifted.)*

**Severity: DEGRADING.**

---

## C. Paper-only rules

Every rule in the DIRECTOR-MANDATORY region (`:439`–`:931`), classified.

### MECHANICALLY ENFORCED (a script exits nonzero on violation)

| Rule | Enforcer |
|---|---|
| Data tree must match the committed SHA-256 manifest | `scripts/data_manifest.py verify` (exit 1/2) **and** import-time in `validator.py:102` — raises before the module binds |
| Bypass must be recorded, not hidden | `validator.py:227` → `Verdict.warnings`, `Verdict.data_manifest["bypassed"]` |
| Director mandatory context ≤ 48 KB | `scripts/check_context_budget.py` (exit 1) |
| A mandatory file or marker missing = failure | same, exit 2 |
| "Latest" brief = highest Task ID, not mtime | `check_context_budget.latest_brief()` |
| Costs must resolve from `COST_MODEL` | `signal_to_returns(fee=None)` → `per_side_cost()`; no module-level `COMMISSION`/`SLIPPAGE` remain |
| `adverse_selection_bps` required on the maker path, with a basis | `per_side_cost()` raises (`:375`); `set_fill_assumption()` raises (`:347`, `:339`) |
| Every Verdict carries its cost model and warnings | `validate()` `:994–996` |
| DSR must state its variance source | `Verdict.dsr["trial_var_source"]`, `PROXY_DSR_WARNING` onto `Verdict.warnings` |

### REVIEWER-CHECKED (a document instructs an agent to check it)

- Falsification conditions transcribed literally; `and`/`or` audited line-by-line, with
  outcome-changing status stated (`:841–844`).
- Engineer BLOCKS on an ambiguous condition rather than choosing (`:834`).
- A cycle whose git diff touches `user_data/data/` is INVALID (`:635`).
- Pre-gate stops get Director reruns (`:810`).
- Lead/lag census must assert ±k sides differ; suspiciously clean results are bug signals (`:803`).
- Any backtest >100% CAGR is presumed defective until four checks are re-verified (`:562`).
- Claim-must-cite-test (`STANDING_DIRECTIVES.md` #1).
- Closed families stay closed (`STANDING_DIRECTIVES.md` #5).

### PAPER ONLY (stated nowhere else — nothing checks it, no prompt names it)

This is the set that will be violated first.

1. **"Pin splits by DATE, not by fraction, while the holdout is reserved"** (`:610`). No
   date-pinned split function exists; `validate()` hardcodes the fractional ones. Already
   violated today — see B.2.
2. **"No training, validation, parameter selection, or pre-gate screening may touch"
   post-2026-05-27 bars** (`:608`). No guard. All 52 holdout bars are inside TEST.
3. **DSR ≥ 0.95 as an absolute promotion gate** (`:723`). `validate()` computes DSR but
   `Verdict.passed` (`:976`) is decided before it and does not include it. No script fails on
   DSR < 0.95.
4. **Nothing forbids promoting on an `estimator_proxy` DSR.** `PROXY_DSR_WARNING` is emitted;
   criterion 1 has no clause about the variance source. The ledger cannot reach 10 rows until
   10 perps trials are spent, so the entire opening stretch of the program runs on the
   defective hurdle with only a warning between it and a promotion.
5. **Promotion criteria 2–5** (`:730`–`:734`). No code evaluates any of them; criterion 3's
   formula has no implementation at all.
6. **"A candidate that does not beat the benchmark cannot be promoted"** (`:711`). The
   benchmark does not exist (A-005, unassigned).
7. **The 4 KB review-brief cap** (`:848`), explicitly claimed at `:859` to be "Enforced by
   `scripts/check_context_budget.py`". **It is not.** A cap breach appends to `warnings`
   (`check_context_budget.py:178`); the exit code depends only on `errors` and total
   over-budget (`:246–256`). Measured: current total 41,876 B of 49,152 B, latest brief
   4,044 B → **a brief may reach 11,320 B (2.8× the cap) before the script exits nonzero.**
   All six untracked briefs (8.7–12.4 KB) would pass silently.
8. **"Every cost number anywhere must resolve from `COST_MODEL`"** (`:533`) and "a run that …
   hardcodes a cost number anywhere is void" (`:550`). Twelve phase scripts hardcode
   `FEE = 0.0015` (`phase10`, `phase11:46`, `phase12:21`, `phase13:22`, `phase14:48`,
   `phase15:36`, `phase16:45`, `phase17`, `phase19`, `phase4`, `phase6`, `phase16_diag`).
   Nothing detects it, and every recent cycle used a `phaseNN` script as its template.
9. **"Update the RESEARCH:OPS ratio every cycle"** (`:599`) — manual bookkeeping.
10. **"An unstated budget is an unlimited one … must state the number in `NEXT_TASK.md`"**
    (`:686`) — nothing parses `NEXT_TASK.md`.
11. **`n_trials` in `research_index.md` and `research_metrics.md` must always match**
    (`:762`) — nothing compares them. They currently disagree (D.5).
12. **`validator.deflated_sharpe()` is "the ONLY entry point research code should use"**
    (`validator.py:203`). It has **zero callers**. All eight existing DSR call sites
    (`phase11`, `phase14:253`, `phase15:368`, `phase16:436`, `phase18`, `research/scratch/t024_*`)
    import `freqtrade_dsr.deflated_sharpe_ratio` directly — the path the docstring says
    "silently takes the estimator proxy". Nothing prevents the next script from doing the same.
13. **`render_report_sections(verdict)`** — referenced at `validator.py:390` as the mechanism
    by which warnings reach a report "without an agent retyping them". It does not exist.
    Every warning is currently retyped by hand.

---

## D. Divergent sources of truth

| # | Quantity | Locations | Verdict |
|---|---|---|---|
| D.1 | **DSR threshold 0.95** | `PROJECT_OPERATOR_MANUAL.md:723,760`; `research/research_index.md:11`; `freqtrade_dsr.py:208` (`dsr_threshold=0.95`); `research_metrics.md:161` | **AGREE** on the value. But the manual's block claims to be a *verbatim quote* of index text that no longer exists (B.9), and the manual is silent on the fact that `evaluate_freqtrade()` — the function it names — never receives the ledger variance. |
| D.2 | **Per-side / round-trip cost** | `PROJECT_OPERATOR_MANUAL.md:543` (9.0 / 18.0 bps); `validator.COST_MODEL` (`:261–277`, computed 9.0/18.0 — verified by execution); `config_perp.json:111` (`0.0009`) | **AGREE.** Cleanest area in the repo. |
| D.3 | **`fee` key** | `config_perp.json:111` = `0.0009` ✅ ; **`user_data/config.json` — NO `fee` KEY AT ALL** | **DISAGREE / RULE VIOLATED.** `:549` states the rule and names this exact file as the historical cause ("Before 2026-07-28 the engine silently applied its own 0.15%/side default because `config.json` had no `fee` key"). It still has no `fee` key, and `research/dryrun_launch_T032.bat` launches the live dry-run with `--config user_data\config.json`. The running bot is on an inherited default fee. **BLOCKING.** |
| D.4 | **`max_open_trades`** | `config.json:2` = 2; `config_perp.json:24` = 9 | Intentional and documented at `config_perp.json:19–23`. **AGREE.** |
| D.5 | **`n_trials`** | `research_index.md:11` — "spot program ended at **100**; **perps starts at 0**"; `research_metrics.md:82` Experiment-counts table — "**100**", no perps row; `research_metrics.md:239` — "these two numbers must always match"; `PROJECT_OPERATOR_MANUAL.md:762` — "`research_metrics.md` is authoritative" | **DISAGREE.** The file designated authoritative has no perps `n_trials`; its only number is the spot final. An Engineer asked for "current `n_trials`" reads 100 from the authority and 0 from the index. Since `n_trials` is a direct DSR input, this changes a gate. **BLOCKING.** |
| D.6 | **Research budget (3 variants / 1 opt run)** | `PROJECT_OPERATOR_MANUAL.md:680`; `research/trial_sharpe_ledger.csv:43–44` | **AGREE.** |
| D.7 | **Context budget cap** | `PROJECT_OPERATOR_MANUAL.md:49,52` = 48 KB; `check_context_budget.py:34` = 48 | **AGREE** — but `research/OPS_BACKLOG.md:47` (A-001 step 6) still says "**the 40 KB mandatory budget**". Stale by one operator decision. |
| D.8 | **Review-brief cap 4 KB** | `PROJECT_OPERATOR_MANUAL.md:848`; `check_context_budget.py:47` (`REVIEW_BRIEF_CAP = 4*1024`) | Values **AGREE**; the manual's claim at `:859` that it is *enforced* is **false** (C.7). |
| D.9 | **Reserved-holdout date** | `PROJECT_OPERATOR_MANUAL.md:606` = "all bars after 2026-05-27"; `research_index.md:16` = same; `PROJECT_OPERATOR_MANUAL.md:619` = "most recent 20% by calendar date" → **2025-02-13** for the perps futures series | **DISAGREE** — B.3. No code anywhere encodes either date. |
| D.10 | **Meta-review cadence** | `PROJECT_OPERATOR_MANUAL.md:993` = "every 25-50 cycles"; `research_index.md:6` = "16 of 25"; `NEXT_TASK.md:28` = "cycle 17 of 25" | **DISAGREE** on the count *and* on what is counted. `:575` says A-XXX tasks never advance the counter, yet the 16 includes T-023, T-025, T-026, T-027, T-031, T-032, T-033, T-036 — all classified OPS by `research_metrics.md:107`. Research-only, the count is ~6, not 16. The counter measures activity, which is the exact failure `:582` says it was fixed to stop. Also note `research_index.md:6` and `NEXT_TASK.md:28` disagree with each other (16 vs 17). |
| D.11 | **Verdict PASS bar vs. promotion rule** | `validator.py:958–974` (≥5y, ≥60% positive years, ≤40% one-year concentration, DD > −25%, **full-window** Sharpe > 1.5, PF > 1.5, ≥200 trades, test ≥ 0.5×train, WF ≥50%, MC p5 > 0) vs `PROJECT_OPERATOR_MANUAL.md:715–734` (DSR, **TEST** Sharpe > 0, TEST Sharpe > benchmark + 1 SE, MaxDD ≤ 1.25× benchmark, all `NEXT_TASK` gates) | **DISAGREE — disjoint criteria sets.** They share not one condition. A Verdict printing `VERDICT: PASS` says nothing about promotability, and a construct that satisfies all five promotion criteria will usually print `FAIL` (full-window Sharpe 1.5 is far above the project's own ~1.2–1.3 observed ceiling). **DEGRADING**, trending BLOCKING the first time someone quotes `passed` as a promotion signal. |
| D.12 | **Construct count** | `research_metrics.md:82,140` = 100; `:179,211` = "all 97 tested constructs" | Cosmetic. |
| D.13 | **Spot-program cycle count** | `research_index.md:36` = "38 completed cycles"; `PROJECT_OPERATOR_MANUAL.md:592` = "spot program ended at **T-036**"; `research_metrics.md:106–107` = 8 research + 11 ops = 19 | Three different counts of the same thing. Cosmetic, but it is the denominator of the RESEARCH:OPS ratio. |

---

## E. Dead and dangling references

### Cited but missing

1. **`research/parked/`** — `PROJECT_OPERATOR_MANUAL.md:98` lists it as on-demand context
   with the instruction "check if it exists". It does not. COSMETIC.
2. **`research/results/T-028_report.md`** — cited by `research_metrics.md:72`, which itself
   notes the Engineer never wrote it. Self-documenting; COSMETIC.
3. **`render_report_sections(verdict)`** — `validator.py:390`. Never written. DEGRADING (C.13).
4. **A-003's line numbers into `validator.py`** — `OPS_BACKLOG.md:158–162` cites `:815`,
   `:827–829`, `:831`, `:832`, `:483`. Current lines are `:938`, `:950–952`, `:954`, `:955`,
   `:595`. The *count* (six call sites) is correct and I verified all six thread
   `execution_mode` correctly; the anchors are stale. COSMETIC.
5. **A-001 describes a file state that no longer exists** — `OPS_BACKLOG.md:20` says
   "`research/research_index.md` carries 38 cycle rows"; it now carries **one** (T-037).
   Step 5 (`:45`) instructs deletion of "the 'Numbering note' paragraph that currently records
   the gap" — no such paragraph exists. Step 6 (`:47`) cites the superseded 40 KB budget. The
   task as written cannot be executed. DEGRADING.
6. **A-004's premise is stale** — `OPS_BACKLOG.md:275–282` tabulates six briefs as "Cited in
   `research_index.md`". Verified: `research_index.md` cites **none** of them; the citations
   moved to `research/archive/index_spot_program.md` during the compaction. The task's
   "Scratch" branch ("`research_index.md` must stop citing them") is now a no-op. DEGRADING.
7. **`user_data/research/data/fear_greed/fng_raw.json`** — cited by `research_metrics.md:233`
   as T-035's auditability evidence. Untracked; absent from a fresh clone. DEGRADING.
8. **`PROJECT_OPERATOR_MANUAL.md` §"Post-promotion reconciliation" (line 609)** — cited by
   `NEXT_TASK.md:70`; that section is now at `:1020`. `NEXT_TASK.md:203` likewise cites
   `research_metrics.md` "line 183" for the update protocol, which is now at `:237`. Both are
   inside a block explicitly marked HISTORICAL RECORD. COSMETIC.

### The six untracked review briefs (verified)

`research/review_briefs/` holds 18 files. `git ls-files` returns 12. Untracked:
**T-029, T-030, T-031, T-032, T-034, T-035** — exactly the six A-004 names. They exist on
this machine only. Note that on a fresh clone `check_context_budget.latest_brief()` still
resolves correctly to `T-037_PERPS_TRANSITION_brief.md` (tracked), so the budget check does
not detect their absence.

### Scripts named in the manual / OPS_BACKLOG — all exist and all run

Executed: `scripts/data_manifest.py verify --json` → `{"ok": true, "checked_count": 52}`;
`scripts/check_context_budget.py` → exit 0, 41,876 B / 49,152 B. `freqtrade_dsr.py`,
`user_data/research/validator.py`, `user_data/research/ARCHIVE_COST_NOTE.md`,
`research/review_briefs/T-037_PERPS_TRANSITION_brief.md`,
`research/archive/index_spot_program.md`, `research/archive/index_narrative_pre_2026-07-28.md`,
`knowledge_base/hypothesis_bank.md` (markers present at `:32`/`:110`),
`research/audits/2026-07-28_repo_audit.md` — all present. Clean.

### Present but cited nowhere

- `research/review_briefs/H-ForwardParity_brief.md` — carries no Task ID, so it can never be
  selected as latest. Correctly surfaced as a warning by `check_context_budget.py`. Working
  as designed; noted only for completeness.
- `user_data/research/tvt_streams.parquet`, `t026_l1.py`…`t026_l3g.py`,
  `user_data/research/quarantine/` — orphaned artifacts of closed cycles. No citation, no
  harm. COSMETIC.

---

## F. Untested surface

**No test file in this repository imports `validator`.** Verified: the only importers of
`validator` are 20 phase/batch scripts and `dryrun_monitor.py`. The test files that exist
(`scripts/test_data_manifest.py`, `user_data/research/test_dryrun_monitor.py`,
`research/test_pagination.py`, `ft_client/test_client/test_rest_client.py`) cover the manifest
checker, the dry-run monitor, and the REST client. **`validator.py` — the single source of
every performance number this project reports — has zero automated coverage.** A-003 exists to
fix this and is LOGGED, NOT ASSIGNED.

### Functions added or materially changed in `user_data/research/` in the last 5 commits

Only `8f1a2bc03` touched `user_data/research/`; only `validator.py` changed (+141 lines).

| Function | Line | Tested? |
|---|---|---|
| `read_trial_ledger(path=None)` | `:153` | **NO** |
| `trial_sharpe_variance(path=None)` | `:172` | **NO** |
| `_load_dsr_module()` | `:188` | **NO** |
| `deflated_sharpe(returns, n_trials, ledger_path=None)` | `:200` | **NO** |
| `dsr_warnings(dsr_result)` | `:218` | **NO** |
| `validate(..., n_trials=None)` — new parameter and DSR block | `:914`, `:979–983` | **NO** |
| `Verdict.dsr` field | `:899` | **NO** |
| `print_verdict()` — new DSR block | `:1017–1023` | **NO** |

**The untested set is all of it.** Worth flagging specifically: `read_trial_ledger()` swallows
every malformed row via `except (TypeError, ValueError, KeyError): continue` (`:166–167`). A
ledger with a typo'd header, a renamed column, or a stray quote silently yields zero rows —
which is indistinguishable from an empty ledger, which silently reverts to the estimator
proxy. The failure mode of the fix is the bug it fixes, and nothing tests it.

I exercised the new code by execution (Section A.5) and it behaves as documented on the happy
path. That is a smoke run, not a test, and the distinction is the one A-003 itself makes.

### `execution_mode` call sites — the specific question asked

**Six distinct call sites** inside `validate()`:

| # | Site | Line |
|---|---|---|
| 1 | full window → `signal_to_returns` | `:938` |
| 2–4 | train / val / test → `signal_to_returns` | `:950`, `:951`, `:952` |
| 5 | `walk_forward(...)` → re-enters `signal_to_returns` per window | `:954` → `:595` |
| 6 | `monte_carlo(...)` → `round_trip_cost(execution_mode)` | `:955` → `:619` |

Plus `cost_model_snapshot(execution_mode)` at `:994` and `cost_model_warnings(execution_mode)`
at `:995`, which record rather than compute.

**Would a top-level-only assertion pass while a subset used a default?** It would, and A-003
is right to demand per-sub-run assertions — but on the code as it stands **all six sites do
thread it correctly**. Verified by running the same signal under `taker` (9.0 bps/side) and
`maker_optimistic` (42.0 bps/side) and asserting every sub-run moved: full, train, val, test,
wf[0..3] and mc all differ in the expected direction (numbers in A.4). This defect does not
exist today; the regression test to keep it that way does not exist either.

---

## G. Reproducibility from a clean clone

Assume `git clone` to `/home/x/freqtrade` on Linux, `pip install -r requirements.txt`.

### G.1 `scripts/data_manifest.py verify` would **FAIL**

Verified by set arithmetic against `git ls-files`, not by guessing:

```
manifest entries:                 52
git-tracked under user_data/data: 45  (of which MANIFEST.json is not itself hashed)
IN MANIFEST BUT NOT TRACKED IN GIT (8):
    okx/ADA_USDT-1d.feather   okx/AVAX_USDT-1d.feather  okx/BNB_USDT-1d.feather
    okx/BTC_USDT-4h.feather   okx/DOT_USDT-1d.feather   okx/LINK_USDT-1d.feather
    okx/SOL_USDT-1d.feather   okx/UNI_USDT-1d.feather
```

`verify` reports 8 MISSING → `format_failure()` → **exit 1**. And because `validator.py:102`
runs `data_manifest.verify()` at **import time** with `raise_on_mismatch=True`, **the entire
research harness is unimportable on a fresh clone** — every phase script dies on
`import validator`. The only escape is `FREQTRADE_SKIP_DATA_VERIFY=1`, which
`PROJECT_OPERATOR_MANUAL.md:675` declares invalidates the cycle. On a fresh clone there is no
legal way to run anything. **Severity: BLOCKING for reproducibility.**

Root cause: `user_data/*` is gitignored (`.gitignore:7`), tracked data files were added with
`git add -f`, and eight of them were missed. A-002 (binary distribution strategy) is the right
place to resolve this and is unassigned.

### G.2 Absolute Windows paths — 40+ occurrences

Every `phaseNN_*.py`, `batchN.py`, `multi_asset.py`, `run_batch.py` and
`dryrun_monitor.py:66` hardcodes `C:/Users/Comec/Projects/freqtrade`, both as
`sys.path.insert(...)` and as data roots (`FUT_DIR`, `SPOT_DIR`, `COT_DIR`, `RESULTS_DIR`,
`ZIP`). Not one uses `Path(__file__).resolve().parents[n]`. On Linux at a different path, all
of them fail — including `phase25_adxgate.py`, the script the most recent research verdict
(T-030) rests on, and therefore any attempt to re-verify that verdict.

`validator.py:57`, `data_manifest.py:52` and `check_context_budget.py:32` all derive
`REPO_ROOT` correctly from `__file__`. The three repaired files are portable; the forty they
serve are not. **Severity: DEGRADING.**

### G.3 Windows-specific assumptions beyond paths

- `research/dryrun_launch_T032.bat` — `.bat`, `cd /d`, hardcoded
  `C:\Users\Comec\AppData\Local\Programs\Python\Python313\python.exe`.
- `NEXT_TASK.md:153–165` mandates `schtasks /query` and
  `Get-WinEvent -FilterHashtable @{ProviderName='Microsoft-Windows-Kernel-Power'}` as
  *required validation steps*. The entire dry-run persistence lane is Windows-only.
- `NEXT_TASK.md:225` requires `py -3.13`; `py` does not exist on Linux, and the system default
  here is 3.14.3, so the launcher and the interpreter policy disagree with each other on this
  machine too.

### G.4 mtime dependence

**None found in enforcement code, deliberately and correctly.** `latest_brief()`
(`check_context_budget.py:82`) and `latest_meta_review()` (`:113`) both resolve by parsed ID
with a filename tie-break and document why. `data_manifest.py` hashes content and records
`bytes`, never mtime. This is the one place the repair anticipated the clone problem and
solved it properly.

*(mtime is used forensically in the narrative record — `research_metrics.md:90` describes
T-025's fabrication being caught by mtime — but nothing depends on it to run.)*

### G.5 Uncommitted-but-required files

| File / dir | Status | Consequence on fresh clone |
|---|---|---|
| 8 `.feather` files (G.1) | untracked | manifest verify fails → harness unimportable |
| `research/review_briefs/T-029,30,31,32,34,35` | untracked | six cited verdict records vanish |
| `user_data/research/data/{cot,dvol,fear_greed,funding}/` | untracked | every cached alternative-data axis vanishes, including the T-035 raw-response evidence the carve-out rule mandates be committed |
| `research/results/T-030,31,32,33,34,35,36*` | untracked | the reports the briefs cite |
| `research/audits/2026-07-28_repo_audit.md` | untracked | cited as the source of the RESEARCH:OPS numbers (`research_metrics.md:117`) |
| `research/trial_sharpe_ledger.csv` | **tracked** ✅ | fine |

### G.6 Unpinned / missing dependencies

- **`scipy` is not in `requirements.txt`.** It is pinned only in `requirements-hyperopt.txt:5`
  — an optional extra. `freqtrade_dsr._norm_ppf()` does `from scipy.stats import norm`, so on
  a base install **the DSR gate cannot be computed at all**. DEGRADING.
- **`statsmodels` is in no requirements file.** `phase18_cointpair.py` imports `adfuller`,
  `coint`, `coint_johansen`; `phase_logistic.py` imports `binomtest` (scipy). The
  cointegration family closure is not reproducible from a clean install.
- **`scikit-learn`** is pinned at `1.8.0` (`requirements-freqai.txt:6`,
  `requirements-hyperopt.txt:6`), but `research_metrics.md:20` records the T-034 Reviewer
  reproduction as having been done with **sklearn 1.9.0** — a version pinned nowhere.
- `numpy==2.4.4`, `pandas==3.0.2`, `pyarrow==24.0.0` are properly pinned. `requires-python
  = ">=3.11"` (`pyproject.toml:16`) conflicts with the standing "Python 3.13 required"
  environment note.
- No `requirements` file exists for the research harness specifically.

---

## Findings that could change a research conclusion if left unfixed

1. `validator.py:605–637` — `monte_carlo()` returns a degenerate distribution; mean, std and
   `∏(1+xᵢ)` are permutation-invariant, so all 200 sims are identical and `mc_p5_sharpe` is a
   point estimate mislabelled as a 5th percentile. Manual Validation Requirement 10 is not
   satisfied by this function.
2. `validator.py:574–578` + `:946` — `split_70_15_15()` places **all 52 reserved-holdout bars
   (post-2026-05-27) inside the TEST split** for both BTC and ETH 1d, with no guard, warning
   or record. The manual's date-pinning rule (`PROJECT_OPERATOR_MANUAL.md:610`) has no
   implementation.
3. `validator.py:597` and `:628` — `walk_forward()` and `monte_carlo()` ignore the caller's
   `bars_per_year` and hardcode 365, producing Sharpes 4.9× inconsistent with the
   full/train/val/test figures in the same Verdict on hourly data. Live the moment the perps
   program leaves daily bars.
4. `validator.py:947–952` — `validate()` recomputes `signal_fn` **per split**, so indicator
   warmup truncates the TEST window. Measured on a 200-day SMA gate: TEST Sharpe 1.64 vs 1.29
   and trade count 1 vs 4 depending only on where warmup falls. TEST-split Sharpe is the
   manual's primary promotion metric.
5. `validator.py:982` — DSR is computed on **full-window** returns while promotion criteria
   2–4 are TEST-split, directly against `research_index.md:14` ("Judge on TEST-set /
   walk-forward numbers only. Full-window Sharpe runs 2-4× inflated here").
6. `freqtrade_dsr.py:121–129` + empty `research/trial_sharpe_ledger.csv` — the estimator-proxy
   hurdle is still the live path (DSR 0.86 vs 0.00 for identical data at 10,000 obs), the
   ledger cannot reach 10 rows until 10 perps trials are spent, and **nothing gates promotion
   on `trial_var_source`** — the fix emits a warning, not a bar.
7. `freqtrade_dsr.py:216` — `evaluate_freqtrade()` calls `deflated_sharpe_ratio()` without
   `trial_sharpe_var`, so the module the manual names as *the* DSR tool
   (`PROJECT_OPERATOR_MANUAL.md:760`) is permanently on the defective path;
   `validator.deflated_sharpe()`, the corrected entry point, has zero callers while eight
   existing call sites bypass it.
8. `PROJECT_OPERATOR_MANUAL.md:606` vs `:619` — the perps holdout is declared twice with
   incompatible mechanisms: the blanket 2026-05-27 date selects **zero** bars of the committed
   perp futures series (which ends 2026-05-27), while the declared 20%-of-calendar-span rule
   gives 2025-02-13. Fifteen months of data are either holdout or not depending on which
   sentence is read.
9. `PROJECT_OPERATOR_MANUAL.md:799` (pre-gate 6, "TEST concentration") vs `:461` and
   `:730–731` — the mandatory pre-gate ladder requires screening on, and killing hypotheses
   with, the TEST split before any trial is spent; the promotion rule then judges survivors on
   TEST-split Sharpe. TEST is not out-of-sample for anything that reaches promotion.
10. `user_data/config.json` — still has **no `fee` key**, and
    `research/dryrun_launch_T032.bat` launches the live dry-run against it. The manual names
    this exact omission as the cause of every void pre-2026-07-28 number (`:549–552`) and
    declares such runs void; the dry-run evidence lane is running under the condition the rule
    forbids.
11. `research_metrics.md:82` vs `research_index.md:11` — the file designated authoritative for
    `n_trials` records **100** and has no perps row; the index says perps starts at **0**.
    `n_trials` is a direct DSR input, so the disagreement changes a gate value.
12. `validator.py:958–974` vs `PROJECT_OPERATOR_MANUAL.md:715–734` — `Verdict.passed` and the
    five-criterion promotion rule share **no** condition. `VERDICT: PASS` is not evidence of
    promotability and `FAIL` is not evidence against it.
13. `validator.py:852` — `family_from_results_dir()` defaults to all 63 saved verdicts, every
    one of which predates the 2026-07-28 cost model and is declared **void** by "Like-for-like
    or void" (`:696`). Any Kaufman family rank or percentile it produces is computed against a
    void population and lands on the Verdict.
14. Twelve phase scripts hardcode `FEE = 0.0015` against `:533`/`:550`, with no mechanical
    check — and they are the templates every recent cycle copied.
15. `scipy` absent from base `requirements.txt` and eight manifest-listed feathers absent from
    git: on a clean clone the DSR gate cannot be computed and `import validator` raises, so no
    recorded result is independently reproducible by anyone but this machine.
