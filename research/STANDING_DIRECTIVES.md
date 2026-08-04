# STANDING DIRECTIVES

**MANDATORY every cycle, Phase 0 (Director, Reviewer).** Capped at 4,096 B; the cap, three-sentence
limit, consolidation-not-raising, no-renumbering and retire-only-by-naming are in the manual,
"STANDING_DIRECTIVES.md is capped". Evidence: `strategy_research_notes.md`, "Evidence displaced…".
Compacted 2026-08-02 from 8,899 B — **no rule lost or altered**; missing 4 = source gap.

**1–7 Meta-Review #1 · 8 harness repair 07-31 · 9 power 08-01 · 10 T-038 08-02**

1. **Claim-must-cite-test.** Any claim that "X was executed / covered / passes through Y" must cite
   the specific test or run calling the REAL function with the REAL caller's argument convention;
   the Reviewer rejects the claim — not necessarily the cycle — if it is missing or the test
   replicates internals inline. "We call the underlying logic directly to avoid X" is an automatic
   red flag requiring a Reviewer rerun through the real path.
2. **Shock-share is unverified-by-default.** Any Engineer statement about `compute_shock_share` /
   `shock_day_mask` coverage is false until a Reviewer reruns it end-to-end through `main()`'s
   convention (false twice: T-017, T-018).
3. **Index row discipline.** New `research_index.md` rows are 1–3 lines (verdict, reason, pointer),
   detail going to the iteration log; iteration numbering counts existing entries, never the
   previous label.

5. **Closed families are closed.** An assignment touching one of §4's seven closures requires the
   specific reopening evidence named in its closure note (e.g. a passing forward cointegration
   census; sub-daily IV data), never a re-parameterization.
6. **Operator action: git commit of the research record.** **DISCHARGED 2026-08-02**, commit
   `20b02a96d`; retained per no-silent-deletion.
7. **Proposed, NOT adopted — binds no one:** that instrument code ship with its fixture suite in
   the same cycle, the Reviewer rerunning fixtures as acceptance.

8. **Any Director citing the OOS-collapse conclusion, the "~1.2–1.3 Sharpe ceiling", or the
   champion's TEST Sharpe 0.41 must cite alongside it that every archived TEST and walk-forward
   figure predating 2026-07-31 used truncated indicator warmup, systematically DEPRESSING val and
   test metrics** (BTC 1d SMA200: TEST Sharpe −1.2159 → +0.2129 after the fix). **Scope:**
   rejections stand *a fortiori* and pre-gate stops never used TEST metrics, so only the
   **magnitude** of the collapse is unestablished, not its direction; re-measuring costs trials.

9. **A Director must state the expected standard error of the primary metric in `NEXT_TASK.md`
   before assigning, and prefer samples large enough to resolve the claimed effect** — SE scales as
   `sqrt(bars_per_year / N)`, so a 151-bar daily TEST split carries SE **1.555** against criterion
   3's **0.24**: DSR ≥ 0.95 went uncleared in spot for an **arithmetic** reason. **Scope: this does
   NOT loosen any promotion criterion and no future directive may cite it to do so** — raise sample
   resolution, or accept a negative result at the trial cap.

10. **Volatility-conditioned de-risking is INVERTED on this market, not merely absent: any construct
    reducing exposure as trailing volatility rises must state why it escapes this finding before it
    may be assigned** — T-038 (perps, 1h): high trailing-vol hours had BETTER forward per-unit-risk
    returns, **Q1−Q5 = −0.442905**, **1 of 9** instruments on the hypothesised side; H-IVSizing
    (spot, daily, implied vol) confirms it on a different measure and venue. **Sign robust**
    (three disjoint subsamples, all three years) **but magnitude NOT** — CI straddles zero, quintile
    means non-monotonic, so the finding is "Q4/Q5 carry everything" and −0.44 is never an effect size.
    **Scope: cite the tension with spot**, which called vol-target sizing its most durable non-signal
    component across ~97 constructs and does not reproduce here, **and do NOT close the volatility
    family** — no downside-vol measure is tested; the bank entry is basket-exposure only.
