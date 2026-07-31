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

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
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

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
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
