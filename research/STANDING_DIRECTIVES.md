# STANDING DIRECTIVES

**MANDATORY for the Research Director and Independent Reviewer, every cycle, during Phase 0.** The
accumulated still-binding directives from every meta-review. Full meta-reviews are ON-DEMAND
(`research/meta_reviews/`); their directives live here.

**Every future meta-review APPENDS here** under a new `## Directives from Meta-Review #N (<date>)`
heading and does not rewrite earlier ones. A directive is retired only by an explicit superseding
directive naming it — never by silent deletion; where they conflict the later governs and must say so.

Content below is **verbatim** from the source, including its numbering. (Meta-Review #1's list skips
number 4; that gap is in the source, preserved rather than silently renumbered.)

---

## Directives from Meta-Review #1 (2026-07-18)

Source: `research/meta_reviews/meta_review_1.md` §"Directives for future cycles". Verbatim.

1. **Claim-must-cite-test rule.** Any report claim of the form "function/path X was executed /
   covered / passes through Y" must cite the specific test or run that calls the REAL function
   with the REAL caller's argument convention. The Reviewer rejects the claim (not necessarily
   the cycle) if the citation is missing or the test replicates internals inline. A test-file
   comment of the form "we call the underlying logic directly to avoid X" is an automatic red
   flag requiring Reviewer rerun through the real path.
2. **Shock-share path is unverified-by-default.** After two consecutive false claims (T-017,
   T-018), any Engineer statement about `compute_shock_share` / `shock_day_mask` coverage is
   treated as false until a Reviewer reruns it end-to-end through `main()`'s convention.
3. **Index row discipline.** New research_index status rows: 1–3 lines (verdict + one-line reason
   + pointer). Detail belongs in the iteration log and session reports. Iteration numbering:
   count existing entries; never trust the previous label.

5. **Closed families are closed.** §4's seven family closures are binding. Assignments touching
   them require the specific reopening evidence named in their closure notes (e.g., a passing
   forward rolling-cointegration census; sub-daily IV data), not a re-parameterization.
6. **Operator actions outstanding** (proposed, not assigned — operator to action): git commit of the research record (P2 above).
7. **Proposed for operator decision (NOT adopted here — the manual's standards are unchanged):**
   consider a standing rule that instrument/monitoring code ships with its fixture suite in the
   same cycle and the Reviewer reruns fixtures as a default acceptance step. This matches what
   T-017/T-018 already did informally and would have caught both false claims earlier.

---
