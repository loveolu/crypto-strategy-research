# OPS BACKLOG — logged, not assigned

Operations and infrastructure work items in the `A-XXX` ID space. Nothing here is an active
assignment: `research/NEXT_TASK.md` remains the single active assignment. An item moves from here to
`NEXT_TASK.md` only when a Director explicitly assigns it.

**A-XXX tasks are not research.** They do not increment `n_trials` and do not advance the
meta-review cycle counter. (Rule established 2026-07-28, repair item 6.)

---

## A-001 — Reconcile missing research_index rows for T-017, T-018, T-019, T-036

**Status:** LOGGED, NOT ASSIGNED. Do not execute without explicit assignment.
**Logged:** 2026-07-28 (repair item 3 amendment).
**Class:** OPS / bookkeeping. Zero trials. Does not advance the meta-review counter.

### Problem

`research/research_index.md` carries 37 cycle rows, but four formally-numbered cycles have **no
index row at all**. They exist only as artifacts under `research/results/` and
`research/review_briefs/`:

| Task | Name | Artifacts known to exist |
|---|---|---|
| T-017 | H-ForwardParity-R1 | `research/results/T-017_report.md` |
| T-018 | A-ParityHardening | `research/results/T-018_report.md`; lessons in `strategy_research_notes.md` annotated "AUDITED 2026-07-15 — cycle REJECTED" |
| T-019 | A-S5Repair | `research/review_briefs/T-019_brief.md` |
| T-036 | A-ForwardParityConfirm | `research/results/T-036_report.md` (terminated by operator decision — repair item 7) |

This was discovered during the 2026-07-28 repair (item 3) while compacting the index. The gap was
**recorded rather than back-filled**: writing verdicts for four cycles without reading their
evidence would be exactly the kind of hand-typed, unsourced claim that T-019, T-023 and T-025
already cost this project.

### Scope

For each of T-017, T-018, T-019, T-036:

1. Read the cycle's report and review brief in full.
2. Extract the verdict **as recorded by the Reviewer**, not as inferred from surrounding prose. If
   no Reviewer verdict exists, record `NO VERDICT ON RECORD` — do not synthesise one.
3. Extract the primary reason, compressed to one line in the index format
   (`Task ID | Hypothesis | Verdict | Primary reason`).
4. Cite the artifact path each row was derived from, in the commit message.
5. Add the four rows to `research/research_index.md` in Task-ID order, and delete the
   "Numbering note" paragraph that currently records the gap.
6. Re-run `python scripts/check_context_budget.py` — four added rows must not breach the 40 KB
   mandatory budget. If they do, compact elsewhere; do not raise the budget.

### Acceptance criteria

- Four rows added, each traceable to a named artifact file.
- No verdict invented. Any cycle whose verdict cannot be established from artifacts is recorded as
  `NO VERDICT ON RECORD` with a pointer to what was read.
- `n_trials` unchanged (these are ops cycles and one already-terminated instrument cycle).
- Meta-review cycle counter unchanged.
- `scripts/check_context_budget.py` exits 0.

### Explicit non-goals

- Do not re-run any analysis from these cycles.
- Do not re-open T-036 (terminated by operator decision, repair item 7).
- Do not adjust `n_trials` or the meta-review counter.
