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

### Acceptance criteria

- Every expected value derived independently of `validator.py`, with the derivation in a comment.
- Runs standalone and under pytest (note: repo `pyproject.toml` sets `--dist`; use `-o addopts=""`).
- Fails loudly if any sub-run ignores `execution_mode`.
- No test touches `user_data/data/` or the committed manifest.

### Explicit non-goals

- Do not change `validator.py` behaviour to make a test pass without first establishing, by hand,
  which of the two is wrong.
- Do not re-run or re-validate any historical strategy.
