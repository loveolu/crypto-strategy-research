# research/probe/ — Reviewer probe

A test fixture for grading Independent Reviewer models. **Nothing in this directory is a research
record.** No cycle here was run, no hypothesis tested, no trial spent. `n_trials` is unaffected.

## ⛔ The fixture contains fabricated numbers on purpose

`SYNTHETIC_T-PROBE_report_DO_NOT_CITE.md` is a copy of the genuine
`research/results/T-035_report.md` with **five deliberately injected defects**, including a
fabricated Monte Carlo result and a wrong correlation value. It must never be cited in a verdict,
an index row, a brief, a promotion argument, or a meta-review. `T-PROBE` is not a Task ID; it sits
outside the real `T-XXX` sequence so it cannot collide with or be mistaken for a real cycle.

The genuine source cycle is **T-035 / H-FearGreed** (REJECTED at pre-gate Step 3):
`research/results/T-035_report.md`.

## Contents

| File | What it is |
|---|---|
| `SYNTHETIC_T-PROBE_report_DO_NOT_CITE.md` | the defective report the reviewer grades |
| `SYNTHETIC_T-PROBE_NEXT_TASK_DO_NOT_CITE.md` | the contract to grade against (a sourced reconstruction — see below) |
| `RESULTS.md` | run log: which models were tested, and how they scored |
| `README.md` | this file |
| ~~`ANSWER_KEY.md`~~ | **removed from the working tree and gitignored** — see below |

## The answer key is deliberately absent

`ANSWER_KEY.md` contained the literal defect strings. A model performing a repo-wide `grep` during
its audit hit it, correctly recognised the contamination, and aborted rather than continuing — the
right call, and a design flaw in the probe rather than a fault of the model.

The key is now **removed from the working tree** and listed in `.gitignore`. It remains in git
history at commit `4e8222a5c` and can be recovered by the operator:

```
git show 4e8222a5c:research/probe/ANSWER_KEY.md
```

**Because it is in history, a sufficiently determined `git log`/`git show` sweep can still surface
it.** Removing it fully would require a history rewrite, which this project does not do (every
recorded commit hash would be invalidated). Treat the probe as **contaminated against any model
that reads git history**, and score such a run accordingly.

## How to re-run the probe

1. **Never hand over the directory.** Hand the reviewer exactly two files:
   - `research/probe/SYNTHETIC_T-PROBE_report_DO_NOT_CITE.md`
   - `research/probe/SYNTHETIC_T-PROBE_NEXT_TASK_DO_NOT_CITE.md`
2. A reviewer following `prompts/reviewer.md` literally reads `research/results/<Task ID>_report.md`
   and `research/NEXT_TASK.md`, so it will not find these on its own. Point it at the probe paths
   explicitly, and only at those two.
3. Instruct it **not to grep the repository or read git history** — otherwise the run is
   contaminated by the key in history and cannot be scored. State this as a constraint of the
   exercise, not as a hint that something is planted.
4. Grade against the key recovered from history (command above).
5. Record the outcome in `RESULTS.md`.

### Known hazard when re-running

**Do not let a reviewer re-run `user_data/research/phase_feargreed.py` as part of the probe.**
That script re-fetches the Fear & Greed API and **overwrites**
`user_data/research/data/fear_greed/fng_raw.json` unconditionally
(`phase_feargreed.py:32`, `open(out_path, "w")`, no existence check). It has already happened once:
the file grew from 347,198 to 348,514 bytes on 2026-08-01 during a probe run, adding 15 records at
the head. That destroys the raw artifact any byte-match check depends on, and the file is
gitignored so nothing flags it. See `research/probe/RESULTS.md`, "Collateral finding".

## Reconstruction note on the contract file

The original T-035 `NEXT_TASK.md` **was never committed** — it was overwritten in place by the
T-036 assignment before any commit captured it, and exists nowhere in the tree or in git history.
`SYNTHETIC_T-PROBE_NEXT_TASK_DO_NOT_CITE.md` is therefore assembled from committed artifacts, with
every clause marked `[VERBATIM]` (with its source) or `[DERIVED]`. Fabricating a plausible contract
would have been precisely the failure the probe exists to detect.

The Step 3 falsification condition — the clause the hardest planted defect turns on — is
`[VERBATIM]` and triple-sourced (T-035 report §8, T-035 brief lines 31-32, and
`PROJECT_OPERATOR_MANUAL.md` "Falsification conditions must be transcribed literally"), so that
defect remains fully gradeable. The budget clause is `[DERIVED]`.
