# STANDING DIRECTIVES

**MANDATORY every cycle, Phase 0 (Director, Reviewer).** Capped at 4,096 B; each entry is rule +
one evidence clause + scope, evidence in `strategy_research_notes.md`, "Evidence displaced…".
Compacted 2026-08-02 and 08-04 — **no rule lost**; missing 4 = source gap.

**1–7 Meta-Review #1 · 8 warmup · 9 power · 10 T-038 · 11–13 T-039**

1. **Claim-must-cite-test.** Any "X was executed / covered / passes through Y" claim must cite the
   run calling the REAL function with the REAL caller's convention; the Reviewer rejects it
   if missing or replicating internals inline. "We call the underlying logic
   directly" is an automatic red flag requiring a Reviewer rerun through the real path.
2. **Shock-share is unverified-by-default.** Any Engineer statement about `compute_shock_share` /
   `shock_day_mask` coverage is false until a Reviewer reruns it end-to-end through `main()`'s
   convention (false twice: T-017/T-018).
3. **Index row discipline.** New `research_index.md` rows are 1–3 lines (verdict, reason, pointer);
   numbering counts entries, never the previous label.
5. **Closed families are closed.** An assignment touching one of §4's seven closures requires the
   reopening evidence named in its closure note, never a re-parameterization.
6. **Git commit of the research record — DISCHARGED 2026-08-02**, `20b02a96d`.
7. **Proposed, NOT adopted, binds no one:** instrument code shipping with its fixture suite in the
   same cycle.

8. **Any Director citing the OOS-collapse conclusion, the ~1.2–1.3 Sharpe ceiling, or the champion's
   TEST Sharpe 0.41 must also cite that every archived TEST/walk-forward figure predating 2026-07-31
   used truncated warmup, DEPRESSING val/test metrics** (BTC 1d SMA200 TEST
   Sharpe −1.2159 → +0.2129). **Scope:** rejections stand *a fortiori*; only the
   **magnitude** is unestablished, not the direction.
9. **A Director must state the primary metric's expected SE in `NEXT_TASK.md` before assigning, and
   prefer samples able to resolve the claimed effect** — a 151-bar daily TEST split
   carries SE **1.555** against criterion 3's **0.24**: DSR ≥ 0.95 went uncleared in spot for an
   **arithmetic** reason. **Scope: does NOT loosen any promotion criterion.**
10. **Volatility-conditioned de-risking is INVERTED here, not merely absent: any construct reducing
    exposure as trailing volatility rises must state why it escapes this before being assigned** —
    T-038 (perps 1h) **Q1−Q5 −0.442905**, **1/9**. **Sign robust, magnitude NOT — −0.44 is never an
    effect size. Scope: cite the spot tension; do NOT close the volatility family.**

11. **The 1h cost wall is measured, not assumed.** At h ≤ 8 the best in-sample gross edge from six
    causal 1h variables, either tail, is **0.90x of one 18.0 bps taker round trip** — below
    cost before any selection penalty (T-039). **A Director must
    state the expected per-trade gross edge against round-trip cost before assigning any construct
    holding positions under 8 hours.** **Scope:** six variables, nine perps, 1h — NOT "intraday is dead".
12. **A census-style scan must price its own width.** T-039's 72-cell scan has a family-wise null of
    **P95 47.22 bps**; its best cell (`vol_ratio` h=24 BOT, 36.52 bps, 9/9) sits at **empirical
    p = 0.221** — ordinary, not marginal. **Any census-style scan must carry a
    family-wise control built the same way; a max cell reported without one is not evidence.**
