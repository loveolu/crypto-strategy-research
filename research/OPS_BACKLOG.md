# OPS BACKLOG — logged, not assigned

Operations and infrastructure work items in the `A-XXX` ID space. Nothing here is an active
assignment: `research/NEXT_TASK.md` remains the single active assignment. An item moves from here to
`NEXT_TASK.md` only when a Director explicitly assigns it.

**A-XXX tasks are not research.** They do not increment `n_trials` and do not advance the
meta-review cycle counter. (Rule established 2026-07-28, repair item 6.)

---

## A-001 — Reconcile missing research_index rows for T-017, T-018, T-019

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-07-28 (repair item 3 amendment).
**Class:** OPS / bookkeeping. Zero trials. Does not advance the meta-review counter.

### Problem

`research/research_index.md` carries 38 cycle rows, but three formally-numbered cycles have **no
index row at all**. They exist only as artifacts under `research/results/` and
`research/review_briefs/`:

| Task | Name | Artifacts known to exist |
|---|---|---|
| T-017 | H-ForwardParity-R1 | `research/results/T-017_report.md` |
| T-018 | A-ParityHardening | `research/results/T-018_report.md`; lessons in `strategy_research_notes.md` annotated "AUDITED 2026-07-15 — cycle REJECTED" |
| T-019 | A-S5Repair | `research/review_briefs/T-019_brief.md` |

This was discovered during the 2026-07-28 repair (item 3) while compacting the index. The gap was
**recorded rather than back-filled**: writing verdicts for these cycles without reading their
evidence would be exactly the kind of hand-typed, unsourced claim that T-019, T-023 and T-025
already cost this project.

### Scope

For each of T-017, T-018 and T-019:

1. Read the cycle's report and review brief in full.
2. Extract the verdict **as recorded by the Reviewer**, not as inferred from surrounding prose. If
   no Reviewer verdict exists, record `NO VERDICT ON RECORD` — do not synthesise one.
3. Extract the primary reason, compressed to one line in the index format
   (`Task ID | Hypothesis | Verdict | Primary reason`).
4. Cite the artifact path each row was derived from, in the commit message.
5. Add the three rows to `research/research_index.md` in Task-ID order, and delete the
   "Numbering note" paragraph that currently records the gap.
6. Re-run `python scripts/check_context_budget.py` — the added rows must not breach the 40 KB
   mandatory budget. If they do, compact elsewhere; do not raise the budget.

### Acceptance criteria

- Three rows added, each traceable to a named artifact file.
- No verdict invented. Any cycle whose verdict cannot be established from artifacts is recorded as
  `NO VERDICT ON RECORD` with a pointer to what was read.
- `n_trials` unchanged (these are ops cycles).
- Meta-review cycle counter unchanged.
- `scripts/check_context_budget.py` exits 0.

### Explicit non-goals

- Do not re-run any analysis from these cycles.
- Do not re-open T-036 — terminated by operator decision 2026-07-29 and already carrying an index row.
- Do not adjust `n_trials` or the meta-review counter.

---

## A-002 — Decide the binary data distribution strategy

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-07-29 (repair item 4 amendment).
**Class:** OPS / infrastructure. Zero trials. Does not advance the meta-review counter.
**Blocking:** this must be decided **before any sub-hourly data is downloaded.**

### Problem

`user_data/data/` is currently **29.6 MB across 52 files**, all daily/hourly feathers plus one CSV.
As of repair item 4 these binaries are committed to git and covered by
`user_data/data/MANIFEST.json`, so every data change writes a new blob into history.

That is tolerable at 29.6 MB. It stops being tolerable at 5m resolution. A 5m series carries roughly
12x the bars of 1h and ~288x the bars of 1d; across the 9 perp instruments in
`user_data/config_perp.json`, with futures OHLCV plus mark price, **5m data will be substantially
larger than the entire current data tree** — plausibly by more than an order of magnitude, and it
grows every time it is refreshed. Git stores each revision of a binary in full, so the repository
would grow by the full size of the dataset on every top-up, permanently and unprunably.

The decision cannot be deferred until after the download: once large binaries are committed, removing
them requires history rewriting, which invalidates every commit hash this project's records cite.

### Options to evaluate

1. **git-lfs** — binaries tracked as pointers. Keeps `git add`/`clone` workflows and the manifest
   unchanged. Costs: an LFS dependency for every clone, storage/bandwidth quotas, and LFS pointer
   files interact with the existing `user_data/*` gitignore and `git add -f` practice.
2. **Manifest-only, data not committed** — `MANIFEST.json` stays in git as the integrity record;
   the data itself is re-fetched from the exchange on a fresh clone. Costs: a documented, tested,
   reproducible re-fetch path becomes mandatory infrastructure, and exchange history limits become a
   hard constraint (OKX funding history was ~97 days in T-031; sub-hourly OHLCV retention must be
   checked before relying on this).
3. **Hybrid** — commit daily/hourly (small, stable, already committed), keep sub-hourly
   manifest-only.

### Required before a decision

- Measured size of one instrument-month of 5m futures OHLCV, extrapolated to 9 instruments over the
  intended window.
- OKX's actual retention limit for 5m OHLCV — determines whether option 2 is even available.
- Whether the reserved holdout (all bars after 2026-05-27) can be reconstructed by re-fetch; if not,
  that data must be committed regardless of the option chosen.

### Explicit non-goals

- Do not download any sub-hourly data as part of evaluating this.
- Do not rewrite git history.

---

## A-003 — Golden-value regression suite for validator.py

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-07-29 (repair closeout).
**Class:** OPS / test infrastructure. Zero trials. Does not advance the meta-review counter.
**BLOCKING:** blocks repair item 5 (`render_report_sections`) **and the first perps cycle (T-038).**

### Problem

`validator.py` is the single source of every performance number this project has ever reported, and
it has **no tests**. The 2026-07-28 repair changed its cost model, its path handling, its Monte Carlo
stress term, and added an import-time data gate — all verified only by smoke runs whose "correct"
answer was whatever the code produced. A smoke run confirms the code does not crash; it cannot
confirm the Sharpe is right.

This is the same class of gap that let T-019 report a hand-computed 13.0645% where the script value
was 2.2760%: no independent expected value existed to check against. `scripts/test_data_manifest.py`
(repair item 4) is the pattern to follow — and note that writing it immediately exposed a real
`relative_to(REPO_ROOT)` bug that had gone unnoticed because only the default path was ever exercised.

### Scope

A golden-value suite where every expected number is derived **analytically or by hand, independently
of the implementation**. A test whose expectation is copied from a previous run of the same function
is worthless — it locks in whatever the bug was.

1. **Analytically-known Sharpe.** Construct return series whose Sharpe is known in closed form
   (e.g. a constant-return series; a two-value alternating series; a series with known mean and
   standard deviation). Assert `metrics()` reproduces it, including the `sqrt(365)` annualisation.
   Include a zero-variance series and assert the documented 0.0 rather than a division error.
2. **Hand-checkable max drawdown.** A short equity path with a drawdown computable on paper
   (e.g. 100 → 120 → 60 → 90: max DD = −50%). Assert exactly. Include: no-drawdown monotonic series;
   drawdown at the final bar; and two separate drawdowns where the *deeper* one must win, not the
   later one.
3. **`round_trip_cost()` arithmetic, both fill assumptions.** Assert taker = 2 × (taker + slippage +
   spread/2) = 18.0 bps and maker = 2 × (maker + adverse_selection) with a set value — computed in
   the test from first principles, not by calling `per_side_cost()`. Assert the maker path **raises**
   while `adverse_selection_bps` is unset, that a value without a basis string raises, and that a
   negative value raises.
4. **Per-sub-run `execution_mode` propagation.** `validate()` currently threads `execution_mode`
   through **six** call sites, not five: full window (`validator.py:815`), train/val/test
   (`:827`–`:829`), walk-forward (`:831`, which re-enters `signal_to_returns` per window at `:483`),
   and Monte Carlo (`:832`). Assert per sub-run that the cost actually applied is the requested one —
   e.g. by running the same signal under `taker` and `maker_optimistic` and asserting **each** of
   `full`, `train`, `val`, `test`, every `wf` window, and `mc` differs in the expected direction.
   Asserting only the top-level result would pass even if four of the six silently used the default.

5. **DSR trial-variance sourcing** (added 2026-07-30). Two assertions:
   - **`trial_var_source` must not be `"estimator_proxy"` once the ledger holds ≥ 10 trials.**
     Build a temp ledger with 10+ rows, call `validator.deflated_sharpe()` against it, and assert
     the source is `"trials"`. This is the regression that matters: the proxy fallback is silent,
     and a DSR quoted from it is not comparable across trade frequencies
     (`research/trial_sharpe_ledger.csv` header explains why). Assert the converse too — at 9 rows
     the source IS the proxy and `PROXY_DSR_WARNING` appears in `Verdict.warnings`.
   - **A hand-checkable `expected_max_sharpe(trial_sharpe_var, n_trials)` value** for a known pair,
     computed by hand from the closed form and written in a comment — not copied from a run of the
     function. Assert `expected_max_sharpe` is monotone increasing in both arguments, and that it
     is INDEPENDENT of observation count (the whole point of the ledger: the proxy path moves
     sr0 from 0.2174 at 92 obs to 0.0207 at 10,000, the ledger path does not move at all).

### Worked example of the required pattern (added 2026-08-01)

**`user_data/research/scratch_ac5_derivation.py` is this suite's pattern already executed once.**
It computes what `shock_log_share` should be for the T-020 AC5 fixture by replicating the arithmetic
**by hand, without calling `compute_shock_share`** — exactly the independence this item demands.
Read it before writing the suite: a worked example is easier to copy correctly than a description of
one, and the failure mode here (quietly deriving the expectation from the implementation) is easy to
commit while believing you have not.

### Acceptance criteria

- Every expected value derived independently of `validator.py`, with the derivation in a comment.
- Runs standalone and under pytest (note: repo `pyproject.toml` sets `--dist`; use `-o addopts=""`).
- Fails loudly if any sub-run ignores `execution_mode`.
- Fails loudly if `trial_var_source` is `"estimator_proxy"` with a ≥10-row ledger.
- No test touches `user_data/data/`, the committed manifest, or the real
  `research/trial_sharpe_ledger.csv` — use temp ledgers.

### Explicit non-goals

- Do not change `validator.py` behaviour to make a test pass without first establishing, by hand,
  which of the two is wrong.
- Do not re-run or re-validate any historical strategy.

---

## A-005 — Compute and commit the perps program benchmark

**Status:** ✅ **COMPLETE, 2026-08-01.** **T-038 is unblocked.** Zero trials — perps `n_trials` stays
0; not appended to the trial ledger; meta-review counter unchanged.
Report: `research/results/A-005_report.md`. Benchmark record:
`research/benchmarks/perps_equal_weight_benchmark.md`. Script:
`user_data/research/perps_benchmark.py`. Headline in `research/research_index.md`.

**One deviation from the specification below, by operator instruction 2026-08-01: the basket is
MONTHLY REBALANCED, not buy-and-hold.** An unrebalanced basket stops being equal-weight almost
immediately (over this window SOL 20.2x vs DOT 0.97x leaves it ~46% SOL / ~2% DOT) and pays no
turnover, both of which flatter the benchmark. The drift variant is retained as a labelled
diagnostic and reconciles exactly. The "Entry cost applies once per instrument; buy-and-hold has no
rebalancing turnover" line below is superseded on that point only.

**Also delivered under this task**: `validator.sharpe_difference_se()` — promotion criterion 3 had
**no implementation anywhere in the repository**, so no candidate could ever have been promoted.

Do not re-execute — the benchmark is pre-registered and re-running it after a candidate exists is
exactly what the "not a number chosen to be beaten" rule forbids.
**Logged:** 2026-07-29 (manual gap closure 3).
**Class:** OPS / measurement. Zero trials for the *program*; the benchmark itself is priced at
`n_trials = 1`. Does not advance the meta-review counter.
**BLOCKING: blocks T-038.** No perps candidate can be evaluated without it.

### Problem

`PROJECT_OPERATOR_MANUAL.md`, "Promotion comparison": where no champion exists, a candidate is
compared against the pre-registered program benchmark — and a candidate that does not beat it cannot
be promoted regardless of its other metrics. The perps program has no champion, and the benchmark
does not yet exist.

It must be computed and committed **before T-038 runs**. A benchmark computed after a candidate's
results are known is not a benchmark; it is a number chosen to be beaten.

### Specification (pre-registered — do not vary)

- **Construction**: equal-weight buy-and-hold of the 9 instruments in `user_data/config_perp.json`
  (BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT, LINK — all `/USDT:USDT`).
- **Costs**: `validator.COST_MODEL` with `fill_assumption = "taker"`. Entry cost applies once per
  instrument; buy-and-hold has no rebalancing turnover.
- **Funding**: perps carry a funding-rate P&L term. State explicitly whether funding is included and
  from which series; if it is excluded, say so and justify it — do not leave it implicit.
- **DSR**: evaluated at `n_trials = 1`.
- **Window and splits**: pinned by DATE, honouring the reserved holdout. The benchmark is computed on
  the same window and split dates any candidate will be judged on, or the comparison is void.

### Deliverables

**A DSR figure alone is NOT sufficient.** The promotion rule
(`PROJECT_OPERATOR_MANUAL.md`, "Promotion rule") evaluates a candidate against this benchmark on
TEST-split Sharpe and MaxDD, and criterion 3 needs the benchmark's *per-bar returns* — not a summary
statistic — to compute the paired standard error. Confirmed required artifacts:

1. **Benchmark TEST-split Sharpe** — per-period and annualised, both stated, with the annualisation
   factor named. Criterion 3's formula takes per-period Sharpes; mixing conventions changes the
   verdict.
2. **Benchmark TEST-split MaxDD** — feeds criterion 4 (candidate MaxDD ≤ 1.25 × benchmark MaxDD).
3. **The benchmark's TEST-split return series, committed as a data artifact** (date-indexed, one row
   per bar). Criterion 3 computes `ρ` between candidate and benchmark returns and `N` from the
   overlapping bars; neither is recoverable from summary statistics. Without this series, criterion 3
   cannot be evaluated and **no candidate can ever be promoted.**
4. A committed script that reproduces all of the above from the committed data, and its output.
5. Full metric set on the same basis the harness reports for a candidate: Sharpe, CAGR, max DD,
   profit factor, MC tail, DSR — full window, train/val/test, walk-forward.
6. The benchmark's headline figures recorded in `research/research_index.md` standing constraints.

The return series must carry the exact split dates it was computed on, so a later candidate can be
checked for date-identical overlap ("Like-for-like or void").

### Acceptance criteria

- Reproducible from committed data with `scripts/data_manifest.py verify` clean.
- Costs resolved from `COST_MODEL`; no hardcoded fee anywhere.
- **Funding treatment stated explicitly**, including the source series, per the original spec above.
- TEST-split Sharpe (per-period and annualised), TEST-split MaxDD, and the TEST-split return series
  all committed — not just DSR.
- Committed BEFORE any T-038 work begins.

### Explicit non-goals

- Do not design, test, or imply a strategy. This measures the do-nothing alternative.
- Do not tune the benchmark. It is pre-registered; if the specification is wrong, change it here
  and say so before computing, never after.

---

## A-004 — Decide whether the untracked review briefs are records or scratch

**Status:** ✅ **RESOLVED, 2026-08-01. Decision: RECORDS.** All six briefs are committed, together
with the seven cycle reports, both raw-output directories, and the audits — 44 files, 18,621 lines.
Byte counts at commit time matched this item's table exactly (9,326 / 12,437 / 8,723 / 11,943 /
10,836 / 10,219), confirming no brief was altered between logging and resolution.

**The manifest question, answered explicitly as this item requires: briefs and reports are protected
by GIT HISTORY ALONE, and `scripts/data_manifest.py` remains DATA-ONLY BY DESIGN.** The manifest
exists to detect tampering with market data that a research cycle is forbidden to modify at all —
a tree where *any* change is a violation, so a hash mismatch is unambiguously a defect. Research
text is different: it is *supposed* to change, by append, and a SHA over it would fire on every
legitimate write. Git already gives these files what the manifest gives the data tree — an immutable
baseline and a reviewable diff — which is precisely what they lacked while untracked.

**Verdict record integrity is now enforced by commit history, not by hashes.** That is a weaker
guarantee than the manifest's and is stated as such: a force-push or history rewrite could still
alter them. This project does not rewrite history (see `research/probe/README.md`), which is what
makes the weaker guarantee sufficient.

**Logged:** 2026-07-29 (manual gap closure 5).
**Class:** OPS / records. Zero trials. Does not advance the meta-review counter.

### Problem

Six review briefs exist in the working tree but are **not tracked by git**:

| Brief | Bytes | Cited in `research_index.md` |
|---|---:|---|
| `T-029_brief.md` | 9,326 | yes |
| `T-030_brief.md` | 12,437 | yes |
| `T-031_brief.md` | 8,723 | yes (×2) |
| `T-032_brief.md` | 11,943 | yes |
| `T-034_brief.md` | 10,836 | yes |
| `T-035_brief.md` | 10,219 | yes (×2) |

Every one is cited by `research_index.md` as the evidence behind a recorded verdict, and **none would
survive a fresh clone.** A reader following those citations on a clean checkout finds nothing. This
is the same class of problem as an uncommitted manifest: a record that only exists on one machine is
not a record.

**`research/review_briefs/` is outside the data manifest's coverage** — `scripts/data_manifest.py`
hashes only `user_data/data/` (verified: the manifest's `root` is `user_data/data` and contains no
`review_briefs` entry). Nothing detects if these files change or vanish.

They were untracked before the 2026-07-28/29 repair and were deliberately left that way: committing
another agent's unreviewed work product without deciding what it *is* would be presumptuous, and one
`git add -A` during the repair swept them in accidentally and had to be undone.

### The decision

**Records** — commit them (`git add -f`, since `user_data/*`-style ignores do not apply here but the
files are currently untracked by choice). Then either extend the manifest to cover
`research/review_briefs/`, or state explicitly that briefs are protected by git history alone and
the manifest is data-only by design.

**Scratch** — then `research_index.md` must stop citing them as evidence, and the cited content must
be relocated into the cycle reports under `research/results/`, which are the durable artifacts.

**Mixed** is also a legitimate answer, but must be stated per file, not left ambiguous.

Note that whichever way this goes, the 4 KB Reviewer cap applies to future briefs only; these six
range 8.7–12.4 KB and predate it. Do not rewrite them to fit — they are someone else's verdict
records, and editing a verdict to satisfy a later formatting rule is not a bookkeeping fix.

### Acceptance criteria

- A stated decision per file, recorded in the commit message.
- If Records: files tracked, and the manifest question answered explicitly either way.
- If Scratch: no dangling citations left in `research_index.md`.
- No brief's *content* altered as part of this task.

### Explicit non-goals

- Do not rewrite, summarise, or truncate any brief to meet the 4 KB cap.
- Do not re-run or re-audit any cycle.

---

## A-006 — Determine whether phase21_ivgate.py's DSR print path ever executed

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-07-31 (validation-harness repair, item 0).
**Class:** OPS / forensics. Zero trials. Does not advance the meta-review counter.

### Problem

`user_data/research/phase21_ivgate.py:756-757` applies `:.4f` formatting to values returned by
`deflated_sharpe_ratio()`, which returns a **dict**, not a float:

```python
753  N_TRIALS_NEW = N_TRIALS_BASE + 1  # 99
754  dsr_veto     = deflated_sharpe_ratio(ret_veto,  n_trials=N_TRIALS_NEW)
755  dsr_champ_99 = deflated_sharpe_ratio(ret_champ, n_trials=N_TRIALS_NEW)
756  print(f'    IV-veto DSR  at n_trials={N_TRIALS_NEW}: {dsr_veto:.4f}')
757  print(f'    Champion DSR at n_trials={N_TRIALS_NEW}: {dsr_champ_99:.4f} (same-window baseline)')
```

`f"{dict:.4f}"` raises `TypeError: unsupported format string passed to dict.__format__`. As written
these lines cannot execute successfully.

**This matters because T-021's verdict rests on this script.** Either the block never ran — in which
case the DSR figures attributed to this cycle came from somewhere else, and that somewhere must be
identified — or it did run and the script differed from what is committed, in which case the
committed artifact is not the one that produced the record. Both readings have consequences for the
cycle's auditability.

Note the sibling call sites are correct: `phase19_sizingband.py:291-292` and
`phase20_tailalloc.py:312-313` subscript the dict (`dsr_t['dsr']`) before formatting. Only phase21
formats the dict directly, which suggests an edit that was never re-run.

### Scope

1. Determine whether lines 750-758 were ever reached: check the cycle's saved output
   (`user_data/research/SESSION_2026-07-11_IVGATE.md`, `research/results/`), and whether any DSR
   figure attributed to T-021/H-IVGate appears anywhere in the record.
2. If DSR figures exist for the cycle, establish which code produced them.
3. Record the finding. **Do not "fix" the line** — the phase scripts are frozen reproduction records
   (`user_data/research/ARCHIVE_COST_NOTE.md`, rule 1). If the committed script cannot reproduce the
   recorded numbers, that is the finding, not a bug to patch away.
4. If the record turns out to rest on numbers no committed script can produce, escalate: that is a
   provenance failure of the same class as T-019, not a formatting typo.

### Explicit non-goals

- Do not edit `phase21_ivgate.py`.
- Do not re-run the cycle or recompute its DSR.
- Do not revise T-021's recorded verdict as part of this task.

---

## A-008 — phase_feargreed.py overwrites its own raw artifact on every run

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-08-01 (step-5 finding, fix 3).
**Class:** OPS / data integrity. Zero trials. Does not advance the meta-review counter.

### Problem

`user_data/research/phase_feargreed.py:32` writes its raw artifact with:

```python
out_path = os.path.join(out_dir, "fng_raw.json")
with open(out_path, "w") as f:
    json.dump(fng_raw, f, indent=2)
```

There is **no existence check and no guard**. The script re-fetches the Fear & Greed API
unconditionally and overwrites `user_data/research/data/fear_greed/fng_raw.json` in place on every
run.

This collides directly with the Independent Reviewer standard, which requires re-running the
Engineer's scripts **unmodified**: performing the audit destroys the artifact the audit exists to
byte-match. **It has already happened.** On 2026-08-01 a reviewer-probe run overwrote the file
(347,198 B / mtime 2026-07-21 → 348,514 B / mtime 2026-08-01 20:39:53). The file had never been
committed, so no baseline existed, and **the T-035 state is permanently unrecoverable** —
reconstruction by truncation was tested and is arithmetically impossible (see the fix-4 report).

Three tripwires missed it simultaneously: the tree is gitignored (`user_data/*`), the file was
never committed, and `data_manifest.py` covers only `user_data/data/`.

### Why this is logged rather than fixed

`phase*.py` scripts are **frozen reproduction records** (`user_data/research/ARCHIVE_COST_NOTE.md`,
rule 1). Editing one to add a guard would change the artifact that reproduces a completed cycle.
The standard requiring the guard now applies to **all future fetch scripts** and is recorded in
`PROJECT_OPERATOR_MANUAL.md`, "Data acquisition is not research" → carve-out. This item records
that one frozen script predates it.

### Scope, if assigned

1. Decide whether the frozen-script exemption should yield here, given that the script is not merely
   inert history — it is executable and destructive, and the Reviewer standard actively instructs
   people to run it.
2. If the exemption holds: add a prominent DO-NOT-RUN warning where a Reviewer would see it before
   running (report section 13 convention, and/or a README in `user_data/research/`), rather than
   editing the script.
3. If the exemption yields: add an existence check that loads from disk, and record the edit in
   `ARCHIVE_COST_NOTE.md` as a deliberate exception with its reason.
4. Audit the other `phase*.py` scripts for the same pattern — any that fetch and write raw artifacts.

### Explicit non-goals

- Do not attempt to restore the lost `fng_raw.json` state. It is unrecoverable; this was determined,
  not assumed.
- Do not re-run `phase_feargreed.py` while investigating. That is the defect.

---

## A-007 — Give the live harness callers explicit split_dates

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-07-31 (validation-harness repair, item 3).
**Class:** OPS / harness maintenance. Zero trials. Does not advance the meta-review counter.

### Problem

Item 3 added a reserved-holdout guard to `validate()` and `walk_forward()`, and deprecated the
fractional `split_70_15_15()`. That changed the behaviour of files which are **live harness callers,
not frozen reproduction artifacts** — so the frozen-script exemption in
`user_data/research/ARCHIVE_COST_NOTE.md` rule 1 does **not** cover them.

**Now raise `HoldoutViolation`** on any series extending past `RESERVED_HOLDOUT_AFTER`:

| File | Calls |
|---|---|
| `user_data/research/batch3.py` | `validate()` |
| `user_data/research/batch4.py` | `validate()`, `split_70_15_15()` |
| `user_data/research/batch5.py` | `validate()` |
| `user_data/research/run_batch.py` | `validate()` |

**Now emit the `split_70_15_15()` deprecation warning:** `user_data/research/batch4.py`,
`user_data/research/multi_asset.py`.

On today's BTC 1d feather (52 bars past the boundary) every one of these raises.

### Scope

1. Give each `validate()` call an explicit `split_dates=(train_end, val_end, test_end)` tuple whose
   `test_end` is on or before the reserved-holdout boundary.
2. Migrate `split_70_15_15()` uses in `batch4.py` and `multi_asset.py` to `split_by_dates()`.
3. Decide the dates ONCE and use the same triple everywhere. Different split dates across callers
   makes their results mutually incomparable, which is the defect that
   "Like-for-like or void" (`PROJECT_OPERATOR_MANUAL.md`, "Promotion comparison") exists to prevent.
4. State the chosen dates in the commit message and in `research/research_index.md` standing
   constraints, so a later reader can tell which window any of these produced.

### Explicit non-goals — read before starting

- **Passing `enforce_holdout=False` is NOT an acceptable fix.** It silences the guard instead of
  fixing the caller, makes every metric in-sample, and marks the run as not-evidence. The guard is
  reporting a real condition: these scripts genuinely were evaluating on reserved holdout. Disabling
  it re-creates the defect and hides it. Any change that adds `enforce_holdout=False` to these files
  must be rejected in review.
- Do not re-point the frozen `phase*.py` scripts at anything. They are covered by the
  frozen-reproduction rule and are out of scope here.
- Do not re-run any historical batch and record its output as a current result. These scripts
  produced archived numbers under a different cost model, a degenerate Monte Carlo, and truncated
  warmup (`ARCHIVE_COST_NOTE.md` §1-4, §4b, §4c). Fixing the call signature does not make their
  output current.

### Acceptance criteria

- All four `validate()` callers run without `HoldoutViolation` on the current feathers.
- No `enforce_holdout=False` anywhere in the repository.
- No remaining `split_70_15_15()` calls outside `phase*.py`.
- The chosen split dates recorded in one place and identical across callers.

---

## A-009 — Establish whether funding-rate history is reachable back to 2022, or close the axis at the data layer

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-08-04 by Independent Reviewer A, as directed by `research/NEXT_TASK.md` (T-039,
"Environment notes"). The Director was explicitly barred from writing this file that cycle.
**Class:** OPS / data reachability. Zero trials. Does not advance the meta-review counter.

### Problem

Funding rate is the **natively-perp mechanism** — the one economic term that exists on this venue and
nowhere in the spot program — and it is currently unusable. All nine
`user_data/data/okx/futures/*-1h-funding_rate.feather` files span **2026-02-26/28 → 2026-05-28**
(266–273 rows each): entirely **after** the TEST window ends (2025-09-19) and entirely **inside** the
reserved holdout. Zero overlap with any evaluable window on the frozen split triple. A-005 excluded
funding from the perps benchmark for exactly this reason, and T-039's Director rejected a
funding/carry hypothesis at reachability rather than on its merits.

T-031 separately established OKX serves roughly **97 days** of funding history. If that is the real
ceiling across reachable venues, the axis is not "not yet fetched" — it is **permanently unavailable
to this program**, and it should be recorded as closed at the data layer instead of being
re-proposed, re-investigated and re-rejected by every future Director.

### Scope

1. Determine OKX's actual funding-history retention limit from the API, not from memory. Record the
   endpoint, the parameters, and the oldest timestamp actually returned.
2. Check whether any other reachable venue serves funding history back to 2022 for these nine
   instruments. T-025's forensics established that **raw REST/curl to OKX works from this environment
   while the ccxt-async client fails** — test the raw path before concluding a venue is unreachable.
   Binance/Bybit were geo-blocked as of T-031; re-confirm rather than assume, and record which.
3. If a source exists: state the exact coverage and cost, and stop. **Do not download anything under
   this task** — acquisition is a separate assignment and is gated on A-002.
4. If no source exists: record the funding axis as **CLOSED AT THE DATA LAYER** in
   `research_metrics.md`'s data-axis table with the evidence, so it stops consuming Director cycles.

### Acceptance criteria

- A stated retention figure per venue tried, each traceable to a saved raw response.
- A yes/no answer on 2022-back availability, with the evidence, not an impression.
- `user_data/data/` untouched; nothing downloaded.
- Whichever way it resolves, the data-axis table is updated so the question is not re-asked.

### Explicit non-goals

- Do not fetch, backfill, or extend any funding series under this task.
- Do not re-run or revise A-005's benchmark — its funding exclusion is correct either way.

---

## A-010 — Two 1h data-coverage facts recorded by T-039, unresolved

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-08-04 by Independent Reviewer A, from the T-039 Engineer's recommendations 6(b)
and 7. Both are Reviewer-verified from `research/results/T-039_raw/g0_coverage.csv`.
**Class:** OPS / data hygiene. Zero trials. Does not advance the meta-review counter.

### Problem

Neither item affects any recorded result — both sit inside the reserved holdout or are handled
correctly by current code. They are logged so the next cycle does not rediscover them as bugs in its
own code.

1. **BTC's 1h series is 25 bars short of the other eight.** BTC ends **2026-05-27 18:00** with 38,587
   bars; the other seven full-history instruments end **2026-05-28 19:00** with 38,612 (BNB 30,062
   from its later start). Entirely inside the reserved holdout, so it affects nothing measured to
   date — but it will matter the first time a cycle evaluates on the holdout, and a ragged panel edge
   is the kind of thing that silently changes a pooled statistic.
2. **Eight of the nine instruments carry exactly 9 zero-volume 1h bars each; BNB carries 0.** The
   count being *identical* across eight instruments points to a venue-wide outage rather than
   per-instrument gaps. T-039 handled them correctly by construction (`illiq` treats a zero-quote-
   volume bar as NaN and the affected 24-bar windows drop out), and no project file records them.

### Scope

1. Identify the timestamps of the 9 zero-volume bars and confirm the venue-outage reading by checking
   whether they share timestamps across the eight instruments.
2. Establish whether BTC's 25-bar shortfall is a fetch gap or genuine venue absence.
3. Record both in `research/research_index.md`'s standing constraints — this is the cheap outcome and
   probably the right one.
4. **Only if a repair is proposed:** it touches `user_data/data/`, so it is an operator-authorised
   data action, never a research cycle. `PROJECT_OPERATOR_MANUAL.md`, "Data acquisition is not
   research" governs; the manifest must be rebuilt deliberately and the change recorded.

### Explicit non-goals

- Do not modify, backfill, interpolate or rebuild any feather while merely investigating. A cycle
  whose diff touches `user_data/data/` is INVALID.
- Do not treat the zero-volume bars as a defect to patch. They are a real property of the venue's
  history; the correct outcome may well be to document them and change nothing.

---

## A-011 — Execution-cost calibration (maker vs taker) + infrastructure restart — **EXECUTED 2026-09-02**

**Status:** DONE, operator-directed (session of 2026-09-02). Zero trials. Does not advance the
meta-review counter.

**Measurement:** `research/measurements/2026-09-02_execution_cost.md`. Equal-weight round trip
measured at **13.67 bps taker ($5k) / 6.15 bps maker** vs the model's 18.0; BTC/ETH taker ≈ 5.0
bps/side; maker adverse selection ≈ −1.7 bps equal-weight, flat 1→60 min. **`COST_MODEL` NOT
changed** — that is an operator decision on a manual standard; recommendation recorded in the file.

**Infrastructure restored in the same session, all durable:**
- Dry-run bot back up (PID 53360, heartbeating). Death of 2026-08-02 21:20 confirmed as Modern
  Standby (Kernel-Power 507 at 21:20:42, 22 s after the last heartbeat); the 07-21 power fix had
  reverted (AC display-off 180 s) — re-applied, plus AC sleep → Never. **DC timeout untouched**: an
  unplugged idle > 3 min still kills it. Keepalive task `FreqtradeDryRun-TrendVolTarget` registered
  (every 30 min) — it had never been registered, which is why every prior death was permanent.
- Funding recorder caught up 07-20 → 09-02 (133 rows × 9, 0 gaps); daily 03:00 task
  `FreqtradeFundingRecorder` registered. **BTC+ETH coverage now 141 contiguous days — the F-7
  120-day unlock is MET.** A funding hypothesis may be assigned, subject to the F-7 census conditions.
- Leftover inert tasks `FreqtradeDryRunBootstrap_T032/_T033` (`/sc once`, no next run) not removed.

**Closes:** A-009's question (funding reachability) is answered for the recorder path — 141 days
held and growing. A-010 unaffected.

---

## A-012 — Data extension to 2026-09-03 + five-strategy holdout evaluation — **EXECUTED 2026-09-03**

**Status:** DONE, operator-directed. Zero trials. Does not advance the meta-review counter.

**Data:** `freqtrade download-data` (okx, futures, `--timeframes 1h 1d`, 9 whitelist pairs,
`--timerange 20260525-20260901`; ccxt-async worked) extended `user_data/data/okx/futures/*-1h-*`,
`*-1d-*`, and the auto-fetched `*-1h-mark.feather` / `*-1h-funding_rate.feather` to
**2026-09-03 23:00 UTC**. Zero duplicate timestamps. `MANIFEST.json` rebuilt (52 files, verify OK).
**Reserved-holdout boundary UNCHANGED at 2025-09-19.** Log: `user_data/logs/A012_download.log`.

**Evaluation:** `research/measurements/2026-09-03_A012_five_strategies.md`. Benchmark −53.29% in a
crash year; S5 (hedged majors/alts spread) the only positive at +3.67%; S2 (trend-gated cascade)
−5.9% at 1.6 trades/day; S1 ungated −28%; S3 −15.8%; S4 inconclusive (funding z never hit ±2).
**Holdout SPENT for S1–S5 as specified**; any carry-forward is a selection step and must be priced.

---

## A-013 — Operator reference bar (S5) + pre-registered improvement variants + full-cycle record — **EXECUTED 2026-09-04**

**Status:** DONE, operator-directed. Zero trials. Record:
`research/measurements/2026-09-04_A013_reference_bar_and_variants.md`.

S5 designated as operator reference bar per instruction (recorded in `research_index.md` and manual
§17 — NOT a replacement for A-005). Its full record is **≈ −27%** over 2023→2026 (2024 −25%). Eight
pre-registered variants on TRAIN+VAL: **V5 beta-neutral** is the only material fix (−34.5% → −5.0%
T+V; 2023 +6.3%); one-shot TEST +8.48% (Sh 3.91); full cycle ≈ +1%, OOS (TEST+FWD) **+7%** — a hedge.
Full-cycle record for all candidates: **S3 gated vol-target basket +96% at DD −25% beats the A-005
benchmark (+85%, DD −70%)**; S1 +106% / DD −33%; S2 +64% / DD −10%. OOS-only: V5 +7%, S2 −6%,
S3 −7%, S1 −22%, benchmark −32%. **All windows now SEEN for S1/S2/S3/S5 and variants; ~21 constructs
examined 09-02→09-04 — no held-out data remains for any of them.**

---

## A-014 — Five structural constructs (rotation, regime-switch, portfolio, gate-only, rebalance freq) — **EXECUTED 2026-09-04**

**Status:** DONE, operator-directed, zero trials. `research/measurements/2026-09-04_A014_structural_constructs.md`.
**3 killed by pre-registered condition** (MAR momentum rotation: 43 flips, −16.8% in 2024; RS
switch: Sharpe 1.28 < S2 1.33; daily/weekly rebalance < monthly at measured costs). **1 survives
marginally** (50/50 S3+V5: Sh 0.82 vs 0.79, DD halved, return halved, OOS +0.8%). **Diagnostic:**
vol-target HELPS at daily on perps (S3 vs gate-only: +10 pts return, −18 pts DD) — evidence for
T-040's daily reopening path. **S2 (Sh 1.33, DD −10.8%, 1.6/day) remains the best risk-adjusted
construct found.** A-005 benchmark and S5 reference bar retained as instructed. ~33 constructs seen.
