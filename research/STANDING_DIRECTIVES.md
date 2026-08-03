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

---

## Directives from the 2026-07-31 validation-harness repair

Not a meta-review, but binding on the same terms. Numbering continues the global
sequence (Meta-Review #1 ended at 7).

8. **The spot program's headline conclusions carry a measurement caveat, and it must be cited
   with them.** Every archived TEST-split and walk-forward figure predating 2026-07-31 was computed
   with **truncated indicator warmup**: `validate()` recomputed `signal_fn` on each split slice and
   `walk_forward()` on each OOS window, restarting every indicator inside the window. This
   **systematically DEPRESSED val and test metrics** — train is long enough to absorb its own warmup,
   the later splits are not. Measured on BTC 1d with an SMA200, the champion's own core: TEST Sharpe
   **−1.2159 → +0.2129** and val **−0.1302 → +0.6345** after the fix, same data, same strategy. Where
   warmup exceeded the split length the affected split reported **0 trades and Sharpe 0.0000
   regardless of merit**.

   The champion's recorded **TEST Sharpe 0.41** is one of these figures. So is the
   *"no signal-prediction edge survives OOS, only regime avoidance transfers"* conclusion and the
   *"~1.2-1.3 Sharpe ceiling"*, both of which rest on comparing strong train numbers against weak
   test numbers — and the test side was biased downward by an unknown amount.

   **What this does and does not overturn.** Rejections stand *a fortiori*: a construct that failed
   on a pessimistically-biased TEST would also have failed on an unbiased one, and the pre-gate stops
   never used TEST metrics at all. What is not established is the **magnitude** of the OOS collapse,
   and therefore how much of the train→test decay was overfitting versus warmup truncation.

   **Any Director citing the OOS-collapse conclusion, the Sharpe ceiling, or the champion's TEST
   Sharpe must cite this caveat alongside it.** Quoting the number without the caveat is a
   misstatement of the evidence. Re-measuring any of it costs fresh trials under the current cost
   model and is a pre-registered cycle, not a free correction.

---

## Directives from the 2026-08-01 statistical-power finding

Not a meta-review, but binding on the same terms. Numbering continues the global sequence
(the 2026-07-31 validation-harness repair ended at 8).

9. **A Director must state the expected standard error of the primary metric in `NEXT_TASK.md`
   before assigning, and must prefer hypotheses on samples large enough to resolve the effect they
   claim.**

   Standard error on an annualised Sharpe scales as approximately `sqrt(bars_per_year / N)`.
   Measured on this repository's actual data:

   | sample | N | SE(annualised Sharpe) |
   |---|---:|---:|
   | TEST split, daily | 151 | **1.555** |
   | full window, daily | 1,002 | 0.604 |
   | BTC daily, all history | 2,339 | 0.395 |
   | **1h pooled across the 9 perps** | **338,933** | **0.161** |

   **The perps benchmark's TEST Sharpe of 2.356 carries an SE of 1.555.** The do-nothing baseline's
   own headline number is not distinguishable from zero on this sample. Promotion criterion 3 asks a
   candidate to resolve a difference of **0.24** with an instrument whose resolution is **1.55**.

   **Consequence, binding on Directors: DSR ≥ 0.95 was never cleared in the spot program for an
   ARITHMETIC reason, not a discipline one.** A 151-bar daily TEST split cannot supply the evidence
   the promotion rule requires, from any construct, however good. Reaching SE 0.25 on daily bars
   would need roughly 16 years of history; crypto perps began in 2020.

   **This directive does NOT loosen any promotion criterion, and no future directive may cite it to
   do so.** The gates are individually defensible and remain in force. The sample was the problem.
   The two honest responses are to raise sample resolution or to accept that a daily-bar programme
   terminates at its trial cap with a negative result — not to lower a bar because the data cannot
   clear it.

---

## Directives from the 2026-08-02 T-038 family-level finding

Not a meta-review, but binding on the same terms. Numbering continues the global sequence
(the 2026-08-01 statistical-power finding ended at 9).

10. **Volatility-conditioned de-risking is INVERTED on this market, not merely absent. Any
    construct that reduces exposure as trailing volatility rises must state why it escapes this
    finding before it may be assigned.**

    T-038 (perps, 1h, basket EWMA-sigma quintiles, TRAIN+VAL, 20,370 bars): high trailing-vol
    hours had **BETTER** forward per-unit-risk returns — **Q1−Q5 = −0.442905**, **1 of 9**
    instruments on the hypothesised side, realized Sharpe by quintile **+0.62 / −0.51 / −0.26 /
    +1.90 / +2.80** with Q5's bars alone compounding **+182.8%**; H-IVSizing (spot, daily,
    implied-vs-realized vol) is a second confirmation on a different measure/resolution/venue.

    **Sign robust, magnitude NOT — cite both:** the sign holds across three disjoint subsamples and
    all three calendar years, but the bootstrap CI straddles zero ([−1.21, +0.34]) and the quintile
    means are **non-monotonic** (Q3 is the minimum), so the finding is **"Q4/Q5 carry everything"**,
    not a smooth gradient — never quote −0.44 as an effect size.

    **Scope:** cite alongside this the tension with spot, which called vol-target sizing its most
    durable non-signal component across ~97 constructs and does **not** reproduce here (either a
    pre-repair-harness artifact, directive 8, or regime-specific — both open); and **do NOT close
    the volatility family**, since no downside-vol/semivariance measure has been tested and the
    failure mechanism (high-vol bars here are predominantly *rallies*) is what such a measure might
    separate — the `hypothesis_bank.md` entry is scoped to the **basket-exposure form only**.
    Evidence and the inverted-construct trap: `strategy_research_notes.md`, "FAMILY-LEVEL FINDING".
