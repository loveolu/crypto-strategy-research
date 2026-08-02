# Reviewer probe — results

**Probe run date: 2026-07-31.** Fixture: `SYNTHETIC_T-PROBE_report_DO_NOT_CITE.md`, five planted
defects, graded against `SYNTHETIC_T-PROBE_NEXT_TASK_DO_NOT_CITE.md`. See `README.md` for the
re-run procedure and `git show 4e8222a5c:research/probe/ANSWER_KEY.md` for the key.

**Not a research cycle. Zero trials. `n_trials` unaffected.**

## Scores

| Model | Planted (of 5) | Unplanted findings | Status |
|---|---|---|---|
| **Composer 2.5** | **5/5** | **3** — deliverable path, section count, first-3-record mismatch | **Strongest of the three. Current Reviewer B candidate.** |
| Gemini 3.6 Flash (High) | 5/5 | 1 | Complete run |
| Grok 4.6 | — | — | **ABORTED — contaminated. Requires a clean re-run before it can be ranked.** |

## Composer 2.5 — current Reviewer B candidate

Found all five planted defects **and** three the probe did not plant:

1. a deliverable-path discrepancy,
2. a section-count discrepancy,
3. the **first-3-record mismatch** between `research/results/T-035_report.md` §7 and the current
   `fng_raw.json`.

Finding (3) is the notable one: it is a **genuine defect in a real cycle**, surfaced incidentally
while auditing a synthetic fixture. Analysis is in the collateral finding below.

**Recorded as the current Reviewer B candidate, pending Grok 4.6's re-run.** The ranking is
provisional precisely because one of the three could not be scored.

## Gemini 3.6 Flash (High)

5/5 planted, 1 unplanted. Complete run, no contamination.

## Grok 4.6 — aborted, and correctly so

Ran a repo-wide `grep`, which surfaced `research/probe/ANSWER_KEY.md`, then **self-reported the
contamination and stopped rather than continuing with the answers in context.**

**This is the correct behaviour and is recorded as such.** A reviewer that notices it has been
handed the answers and says so is doing exactly what the role demands; continuing would have
produced a meaningless 5/5. **The abort reflects a probe design flaw, not a deficiency of the
model** — the key should never have been reachable from the fixture directory.

Grok 4.6 **cannot be ranked** on this run. A clean re-run is required, under the constraints in
`README.md` (no repo-wide grep, no git history — the key is still recoverable from commit
`4e8222a5c` and a history sweep would re-contaminate).

Remediation applied: the key is deleted from the working tree and gitignored. It remains in git
history and cannot be removed without a rewrite, which this project does not do.

## Collateral finding — a probe run modified a real research artifact

**During the probe runs, `user_data/research/data/fear_greed/fng_raw.json` was overwritten.**

| | |
|---|---|
| Before | 347,198 bytes, mtime 2026-07-21 02:28 (its original T-035 fetch) |
| After | 348,514 bytes, mtime 2026-08-01 20:39:53 |
| Change | +15 records **at the head** (newest-first ordering): coverage 2026-07-18 → 2026-08-02 |

Cause: `user_data/research/phase_feargreed.py:32` opens the raw artifact with `open(out_path, "w")`
and re-fetches unconditionally — no existence check, no immutability guard. Any reviewer following
`prompts/reviewer.md` Phase 1.C (*"Re-run the Engineer's scripts unmodified"*) destroys the raw
artifact the byte-match check depends on.

It was invisible to every tripwire: the file is gitignored (`.gitignore:7`, `user_data/*`), was
never committed, and sits outside `data_manifest.py`'s coverage (`user_data/data/` only). `git
status`, `git diff` and `data_manifest.py verify` were all clean throughout.

**This also explains the first-3-record mismatch** that Composer 2.5 and one other model reported
against T-035 — the mismatch was created by the re-fetch, not by anything the T-035 Engineer or
Reviewer did. Full analysis was reported to the operator separately; no file was modified in
response.
