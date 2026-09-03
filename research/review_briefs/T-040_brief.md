# T-040 / H-SemiVarSizing-1h — Reviewer A brief

**REJECT — pre-gate P2, F2 fired on BOTH clauses. Trials spent 0; perps `n_trials` stays 0 of 30.**

**Falsification: FIRED.** F1 no (ρ med 0.480280 / min 0.427458 vs 0.30 / >0.15). **F2 yes, both
clauses**: `D_bar` **−0.426586** (KILL ≤0), breadth **0/9** (KILL <5), 250,425 pooled TRAIN+VAL 1h
anchor bars. F3/P3 NOT REACHED — correctly recorded as *not reached*, not *not met*.

**The inversion is not an estimator artifact.** The decomposition reversed the prediction: `dsd`
−0.426586 (0/9) << `sd` −0.205060 (2/9) < `usd` −0.189939 (3/9). The leg predicted to flip positive
inverts hardest; total vol sits *between* its components, not below both. Negative in **14/14**
robustness cells and under medians/1%-trimming at 0/9 — not a tail artifact — but median
monotonicity is only **+0.30**, so not a gradient either.

**Reproduced.** All 8 raw artifacts byte-identical (SHA-256) on an unmodified re-run. Independently
reimplemented the census from the assignment text under two further binning conventions — qcut
−0.425994, rank-split −0.426376, **breadth 0/9 in all three**; P1 ρ and the anchor count matched
exactly. `per_side_cost("taker")`=0.0009 called directly. Manifest clean (52 files, not bypassed),
`user_data/data/` untouched, DSR entrypoint 0 violations, ledger 0 rows. Nothing gating went
unreproduced; no DSR/Sharpe/MC exists.

**Principal Reviewer finding — sign established, MAGNITUDE not.** P2b never ran, so I ran its own
pre-registered construction as an audit statistic. The null is well-formed (mean +0.0102, median
+0.0031, share>0 **0.502**, sd 0.3356) and `D_bar` sits at only its **10.2nd percentile** (z −1.30,
two-tailed p 0.236). The shared offset preserves cross-sectional alignment, so breadth is
near-uniform on 0…9: **P(B=0)=0.105**. **F2 fires on 53.5% of null draws.** REJECT is
unambiguous (pre-registered one-tailed p would be **0.898**), but no closure may rest on the
inversion's *size* or on the `dsd`/`sd`/`usd` ordering — its 0.237 spread is under one null sd.
Directive 10's "sign robust, magnitude NOT", measured.

**Audit.** Spec deviations **none**; F1/F2/F3 transcribed literally (`or` ×3). Budget 0 of 1
variants, 0 opt runs. One non-outcome-changing error: §7's "Q5 is the maximum for 8 of 9
(LINK's Q3 higher)" is **6 of 9** — BTC, ETH *and* LINK peak at Q3; it overstates the gradient,
against the report's own §12.4. Engineer disclosed a real tie discrepancy (qcut vs searchsorted
moves `D[i]` ≤3.7e-03) and asserted both KILL clauses under both conventions rather than smoothing
it; added a truncation-invariance leakage proof; script tracked; no Reviewer-owned file written.

**Engineer's recommendations, carried forward.** (1) Close the de-risking direction but bound it
tightly — untested: h≠24, non-per-unit-risk responses, daily bars, short/neutral books,
cross-sectional rank sizing; resist "volatility sizing doesn't work". (2) No further cycle on
another dispersion functional (Ulcer, downside EWMA, other windows) — re-parameterisations of the
most-inverted leg. (3) **The open question is the response, not the conditioner**: `fwd_pur` is
Sharpe-like attractiveness, not money; measure the same quintile difference on **raw** and
cost-adjusted `fwd_ret` before reading the inversion as tradeable — one column swap; would not
assign the scale-up construct first. (4) BTC/ETH cross-sectionally different — a lead, though "less
negative", not positive. (5) Three cycles bump into 1h reversal, none tested it directly; h≥24
given T-039's h≤8 cost wall. (6) Pin the quantile tie convention in census
assignments; make truncation invariance a standard directive-8 attestation. (7) Ledger empty after
3 perps cycles, criterion 7 needs 10 rows — structural; would not weaken a gate for it.

**Implications.** Ulcer / downside EWMA / Sortino denominators / other semivariance windows are
**inside** the bank-ledger closure, not escapes. Meta-review 19 of 25, not due. `n_trials` **0**,
cap not reached. Context budget 98.1%.
