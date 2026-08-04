# T-038 / H-BasketVolTarget-1h — Reviewer A brief

**VERDICT: REJECT at pre-gate P2. Zero trials. Perps `n_trials` stays 0** (cap 30). First perps
RESEARCH cycle; first on the 1h sample. Detail: `research/results/T-038_report.md`.

## Decisive facts
- **P1 PASSED**: Spearman ρ(sigma_t, fwd 24-bar realized vol) median **0.564373**, min **0.434160**
  (BTC), against bars ≥0.30 / >0.15. Vol IS persistent at 1h.
- **P2 FAILED on both KILL clauses**: **Q1−Q5 = −0.442905** (KILL if ≤0), breadth **1 of 9** (KILL
  if <5). Mechanism **inverted**, not absent — high-vol hours had *better* forward per-unit-risk
  returns; realized quintile Sharpes Q1 **+0.6150** … Q5 **+2.8015** (Q2/Q3 negative).
- **Falsification condition 2 fired**; the report accepts it rather than arguing around it. P3/P4
  correctly not reached.

## Reproduced / not reproduced
All three scripts re-run **unmodified** → **byte-identical** stdout and JSON on all six raw
artifacts; every gating figure also re-derived to 6 dp by a Reviewer reimplementation sharing no
code path with theirs. **Not reproduced:** nothing
material — no DSR/MC/walk-forward existed, no trial spent. **Clean:** data tree untouched before and
after reruns; manifest OK (52 files); no bypass; DSR entry-point 0 violations; ledger 0 rows; splits
date-pinned; no census window reaches TEST; `per_side_cost("taker")` = 0.0009 as reported; boolean
transcription exact — **no spec deviations**; 0 of 1 variants.

## Audit findings (none outcome-changing)
1. **Untraceable figures.** Five §7 diagnostics (mean m_raw/m_applied, two shares <0.9, 249 exposure
   changes, Σ|Δm| 30.207) appear in **no** raw artifact, against §13's "every figure is traceable";
   I recomputed all five **correct to the digit**. Documentation gap, not fabrication.
2. **Scripts gitignored/untracked** (`.gitignore:7 user_data/*`) — the gap that lost `fng_raw.json`.
   Resolved 2026-08-02, force-added in `f2a303a72`.
3. **Engineer wrote `strategy_research_notes.md`** (Reviewer bookkeeping); verified, kept with
   attribution.

## Observations
- Quintile means **non-monotonic** (Q3 is the minimum): "Q4/Q5 carry everything", not a vol
  gradient. Bootstrap CI on Q1−Q5 **straddles zero** ([−1.21, +0.34], share>0 0.1705), correctly
  non-gating: **sign** robust across burn-in exclusion, 3 disjoint offsets, 3 years and a
  cross-check, **magnitude** not.
- **Harness issue I confirmed:** the 1h TEST slice spans **152** UTC dates vs the benchmark's
  **151** — criterion 3 VOID for any 1h candidate at trial. Fixed 2026-08-02; see note.

## Engineer's recommendations (carried forward)
1. Treat "volatility-conditioned de-risking" as **at risk of closure but not closable on this cycle
   alone**; a semivariance/downside-deviation variable is structurally different and its P2 census
   is cheap (same script, bucketing swapped) — worth one pre-gate, killed fast if negative.
2. The 1h sample is worth using: 20,370 census bars resolved this where 151 daily could not.
3. **Fix the hourly boundary before assigning another 1h cycle** — operator decision, cheap now.
4. Without a claim: the extreme decomposition makes the **inverted** construct (scale UP in high
   vol) look good in-sample for the same reason — the Engineer calls it **a trap**, untestable
   without a crash-sample pre-gate.
5. Per-year and disjoint-window views beat the bootstrap CI.

## Implications (factual)
De-risking on a volatility **level** signal in a long-only crypto book now fails on two independent
axes, programs, resolutions and cost models (H-IVSizing implied vol; T-038 realized 1h) — now
**standing directive 10**. **`n_trials` after: 0.** Meta-review 17 of 25.

## Post-cycle note (2026-08-02) — resolution-aware boundary
T-038 ran under the old midnight-valued holdout boundary, made resolution-aware afterwards
(`5cbd7617a`). Re-run under the fix: **Q1−Q5 = −0.438872**, **P1 ρ = 0.564232**, **breadth 1 of 9
unchanged**, both KILL clauses fire, **verdict unchanged**. The committed raw artifacts remain the
record of what was run.
