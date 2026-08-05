# research_index.md — compressed project dashboard

> **Format: one line per completed cycle, no detailed analysis.** Pre-2026-07-28 narrative is in
> `research/archive/index_narrative_pre_2026-07-28.md`.

**Cycles since meta-review #1 (2026-07-18): 18 of 25** — not due.

## Standing constraints

- **Dry-run only. No real capital on backtest evidence.** All configs `dry_run: true`, empty keys.
- **DSR gate ≥0.95** at honest cumulative `n_trials` (spot program ended at **100**; perps starts at
  0). Standard is in `PROJECT_OPERATOR_MANUAL.md`, "DSR promotion threshold" — that is primary, this
  is a pointer. `research_metrics.md` is authoritative for the count.
- Judge on TEST-set / walk-forward numbers only. Full-window Sharpe runs 2-4x inflated here.
- Asset universe is not restricted to BTC/ETH — they are the default because most liquid/stable.
- **Costs**: `validator.COST_MODEL` only; pre-2026-07-28 results are not comparable. **Holdout is
  PROGRAM-SCOPED**: perps = after **2025-09-19**, spot = after 2026-05-27
  (`validator.HOLDOUT_BOUNDARIES`, operator decision 2026-08-01). `PROJECT_OPERATOR_MANUAL.md` is
  primary; "after 2026-05-27" for perps (older line here, and `T-037_PERPS_TRANSITION_brief.md`
  line 41) reserves zero perp bars and is superseded.
- **Perps split triple, frozen by A-005 and mandatory for every perps candidate**: `train_end
  2024-11-22 · val_end 2025-04-21 · test_end 2025-09-19`, date-pinned. Other dates void the
  benchmark comparison.

## Champion status

**The perps program has NO champion.** TrendVolTarget and the 80/20 stance are spot artifacts at the
pre-2026-07-28 cost model — void as perps evidence, not a promotion baseline. Until one exists on
perp data, candidates are compared against the pre-registered benchmark below. Historical spot
detail: `research/current_champion.md`, `research/strategy_portfolio.md`,
`research/review_briefs/T-037_PERPS_TRANSITION_brief.md`.

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
