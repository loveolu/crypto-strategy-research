# T-038 / H-BasketVolTarget-1h — Reviewer A brief

**VERDICT: REJECT at pre-gate P2. Zero trials. Perps `n_trials` stays 0** (cap 30).
First perps RESEARCH cycle; first on the 1h sample. Detail: `research/results/T-038_report.md`.

## Decisive facts
- **P1 PASSED**: Spearman ρ(sigma_t, fwd 24-bar realized vol) median **0.564373**, min **0.434160**
  (BTC); bars ≥0.30 / >0.15. Vol IS persistent at 1h.
- **P2 FAILED on both KILL clauses**: basket **Q1−Q5 = −0.442905** (KILL if ≤0); breadth **1 of 9**
  (KILL if <5). Mechanism **inverted**, not absent — high-vol hours had *better* forward per-unit-risk
  returns. Realized quintile Sharpes Q1 **+0.6150** … Q5 **+2.8015** (Q2/Q3 negative).
- **Falsification condition 2 fired.** The report accepts it rather than arguing around it. P3/P4
  correctly not reached.

## Reproduced / not reproduced
All three scripts re-run **unmodified** → **byte-identical** stdout and JSON on all six raw artifacts.
Every gating figure also re-derived to 6 dp by a Reviewer reimplementation sharing no code path (own
basket loop, `scipy.stats.spearmanr`, numpy `searchsorted` bucketing), incl. sigma_target 0.540308 and
24,019 basket bars. I resolved `per_side_cost("taker")` = **0.0009** myself; matches. **Not
reproduced:** nothing material — no DSR/MC/walk-forward existed, no trial spent.

**Clean:** data tree untouched before/after reruns; manifest OK (52 files); no bypass; DSR entry-point
0 violations; ledger 0 rows; splits date-pinned, `assert_no_holdout` clean; no census window reaches
TEST; boolean transcription exact — **no spec deviations**; 0 of 1 variants.

## Audit findings (none outcome-changing)
1. **Untraceable figures.** Five §7 diagnostics (mean m_raw/m_applied, two shares <0.9, 249 exposure
   changes, Σ|Δm| 30.207) appear in **no** raw artifact, contradicting §13's "every figure is
   traceable". I recomputed all five: **correct to the digit.** Documentation gap, not fabrication.
2. **Scripts gitignored/untracked** (`.gitignore:7 user_data/*`); prior cycles' were force-added. No
   git baseline for deliverable 2 — the gap class that lost `fng_raw.json`. **Operator action.**
3. **Engineer wrote `strategy_research_notes.md`** (Reviewer bookkeeping). Verified accurate; kept
   with Reviewer attribution.

## Observations
- P2 quintile means are **non-monotonic** (Q3 is the minimum): "Q4/Q5 carry everything", not a vol
  gradient.
- Bootstrap CI on Q1−Q5 **straddles zero** ([−1.210815, +0.344539], share>0 0.1705), correctly
  non-gating. **Sign** robust across burn-in exclusion, 3 disjoint offsets, 3 years and an independent
  cross-check; **magnitude** is not.
- **Harness issue I confirmed:** the guard-compliant 1h TEST slice spans **152** UTC dates vs the
  benchmark's **151** — criterion 3 VOID for the first 1h candidate at trial. Unresolved.

## Engineer's recommendations to the Director (carried forward)
1. Treat "volatility-conditioned de-risking" as **at risk of closure but do not close it on this cycle
   alone**; a semivariance/downside-deviation conditioning variable is structurally different and its
   P2 census is cheap (same script, bucketing swapped) — worth one pre-gate, killed fast if again
   negative.
2. The 1h sample is worth using: 20,370 census bars resolved this where 151 daily bars could not.
3. **Fix the hourly boundary before assigning another 1h cycle** — operator decision, cheap now.
4. Without a claim: the extreme decomposition means the **inverted** construct (scale UP in high vol)
   would look good in-sample for that same reason — the Engineer calls it **a trap**, untestable
   without a crash-sample pre-gate.
5. Per-year and disjoint-window views beat the bootstrap CI per line.

## Implications (factual)
De-risking on a volatility **level** signal in a long-only crypto book now fails on two independent
axes, programs, resolutions and cost models (H-IVSizing implied vol; T-038 realized 1h). Untested: any
measure separating downside from upside vol. **`n_trials` after: 0.** Meta-review 17 of 25 — not due.
Cap open.
