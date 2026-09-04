# research_index.md — compressed project dashboard

> **ON-DEMAND since 2026-08-06** — demoted from the Director's mandatory set under escalation step 2
> of the frozen-cap box in `PROJECT_OPERATOR_MANUAL.md`. **Open this file before selecting any
> hypothesis adjacent to recent work**: the cycles table below is the project's only compact record
> of what has already been rejected and why, and the counter below decides when a meta-review is due.
>
> **Format: one line per completed cycle, no detailed analysis.** Pre-2026-07-28 narrative is in
> `research/archive/index_narrative_pre_2026-07-28.md`.

**Cycles since meta-review #1 (2026-07-18): 19 of 25** — not due.

## Standing constraints — MOVED

**Promoted into `PROJECT_OPERATOR_MANUAL.md` as section 17 of the `DIRECTOR-MANDATORY` region on
2026-08-06, in the same edit that demoted this file to on-demand. That manual section is now the
primary and only location** — no constraint was dropped in the move, and it is deliberately not
duplicated here, because a standard held in two places is a standard that can silently disagree
with itself.

## Champion status

**The perps program has NO champion.** TrendVolTarget and the 80/20 stance are spot artifacts at the
pre-2026-07-28 cost model — void as perps evidence, not a promotion baseline. Until one exists on
perp data, candidates are compared against the pre-registered benchmark below. Historical spot
detail: `research/current_champion.md`, `research/strategy_portfolio.md`,
`research/review_briefs/T-037_PERPS_TRANSITION_brief.md`.

## Operator reference bar (designated 2026-09-04) — S5 majors/alts cascade spread

**Operator instruction (2026-09-04): treat S5's +3.67% as the bar to beat.** Recorded as an
**operator-designated reference**, NOT as a replacement for the A-005 program benchmark — criterion 3
still pairs against A-005's frozen TEST series, because S5's +3.67% is on the holdout year
(2025-09 → 2026-09), not the frozen split, and it was the best of five constructs on that year.
**Full record, computed 2026-09-04** (`user_data/research/s5_spread.py`): TRAIN **−22.42%**
(2023-01 → 2024-11), VAL **−15.52%**, TEST +8.49% (Sharpe 2.63), FWD +3.46%; by year 2023 −3.8%,
**2024 −25.0%**, 2025 +3.5%, 2026 −2.7% — **≈ −27% over the full cycle.** It loses in alt-season and
earns in cascades; the dispersion gate does not tell the two apart. Improvement work: A-013.

## Perps program benchmark (A-005, 2026-08-01)

Committed; T-038 unblocked. **`PROJECT_OPERATOR_MANUAL.md` "Promotion comparison" is primary for its
figures and for the 7-criterion promotion rule** — this is a pointer, not a second copy. Equal-weight
monthly-rebalanced long basket, 9 perps, 1d, taker, 2022-12-23…2025-09-19; full window +503.52% /
Sharpe 1.3553 / MaxDD −51.33%; WF positive in **1 of 4** windows. Funding excluded and basket
survivorship-biased — both bias the bar upward. Spent no trial. Record:
`research/benchmarks/perps_equal_weight_benchmark.md`, `research/results/A-005_report.md`.

## Cycles completed

| Task ID | Hypothesis | Verdict | Primary reason |
|---|---|---|---|
| T-037 | Perps program transition (not a cycle) | **PROGRAM BOUNDARY, 2026-07-29** | Venue, cost model and trial ledger changed; spot results void as perps evidence. See `research/review_briefs/T-037_PERPS_TRANSITION_brief.md` |
| T-038 | H-BasketVolTarget-1h — EWMA vol-target exposure scaling of the 9-perp basket | **REJECT (pre-gate P2), 2026-08-01** | Harm census inverted: basket Q1−Q5 = −0.442905 (KILL if ≤0), breadth 1/9 (KILL if <5). High-vol 1h bars have BETTER forward per-unit-risk returns. P1 passed (ρ median 0.564). Zero trials; **perps n_trials stays 0** |
| T-039 | H-IntradayEdgeFloor-1h — 72-cell conditional-mean census for any 1h entry edge clearing 2× the taker round trip | **REJECT (pre-gate), 2026-08-04** | Falsification fired: **0 of 72** cells clear G1∧G2∧G3∧G4∧G5 (G1 72 · G2 1 · G3 66 · **G4 0** · G5 66). At h ≤ 8 the best gross conditional edge is **16.13 bps vs an 18.0 bps round trip (0.90×)**; the one G2-clearing cell (`vol_ratio` h=24 BOT, 36.5176 bps, 9/9 breadth) sits inside the 72-cell family-wise null (**P95(M) 47.2200 bps**; 22.1% of draws reach it). Zero trials; **perps n_trials stays 0** |
| T-040 | H-SemiVarSizing-1h — is T-038's vol→exposure inversion an artifact of a TOTAL-vol estimator mixing downside and upside dispersion? | **REJECT (pre-gate P2), 2026-08-06** | No: F2 fired on **both** clauses — `D_bar` **−0.426586** (KILL ≤0), breadth **0/9** (KILL <5), 250,425 pooled 1h anchor bars. The decomposition reverses the prediction: `dsd` −0.4266 (0/9) << `sd` −0.2051 (2/9) < `usd` −0.1899 (3/9). P1 passed (ρ med 0.4803); negative in all 14 view/convention cells. **Reviewer caveat — sign established, MAGNITUDE not**: `D_bar` at the 10.2nd pct of its own null (z −1.30), B=0/9 null P 0.105. Zero trials; **perps n_trials stays 0** |

> **T-035 raw artifact permanently lost; verdict stands. Do not attempt restoration.** Full note:
> `research/review_briefs/T-035_brief.md`, "T-035 audit-status note".

**Prior program.** The 38 completed cycles of the spot program (2026-05-14 → 2026-07-29) are archived
complete and unaltered in `research/archive/index_spot_program.md`. The index resets at a program
boundary for the same reason `n_trials` does — those results were measured on a different instrument
at a different cost model. Task IDs do not reset.

## Open / closed directions

Family status is governed by the `knowledge_base/hypothesis_bank.md` FAMILY STATUS LEDGER, itself
mandatory context — read it there, not summarised here.

- **Data axes**: COT cached, filter rejected (#14). Sentiment reachable, cached, reactive (T-035).
  Funding recorded going forward (T-031). Order book, liquidations, on-chain flow unreachable
  without a paid vendor.
- Any new hypothesis must use a genuinely new data dimension or a structurally different mechanism.
  Parameter variations of tested families are banned.

## Where detail lives

Detail does not belong in this file. Per-cycle reports: `research/results/`. Reviewer audits:
`research/review_briefs/`. Durable lessons (incl. the 27 empirical-testing lessons and book summaries
formerly inline here): `research/strategy_research_notes.md`,
`research/archive/index_narrative_pre_2026-07-28.md`. Champion detail: `research/current_champion.md`.
Binding directives: `research/STANDING_DIRECTIVES.md`.
