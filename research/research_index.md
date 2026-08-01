# research_index.md — compressed project dashboard

> **Format: one line per completed cycle, no detailed analysis.** Pre-2026-07-28 narrative is in
> `research/archive/index_narrative_pre_2026-07-28.md`.

**Cycles since meta-review #1 (2026-07-18): 16 of 25** — not due.

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

**The perps program has NO champion.** TrendVolTarget and the 80/20 portfolio stance are spot
artifacts computed at the pre-2026-07-28 cost model; their figures are void as perps evidence and are
not a promotion baseline. Until one is established on perp data, candidates are compared against the
pre-registered program benchmark. Spot detail, all historical:
`research/current_champion.md`, `research/strategy_portfolio.md`,
`research/review_briefs/T-037_PERPS_TRANSITION_brief.md`.

## Perps program benchmark (A-005, 2026-08-01) — a candidate must beat this to be promoted

Equal-weight buy-and-hold, 9 `config_perp.json` perps, 1d, taker, **2022-12-23…2025-09-19**.
**TEST Sharpe +0.122344 per-period / +2.3374 ann(√365) · TEST MaxDD −23.22% (criterion-4 cap
−29.03%) · N=151 · DSR 0.93713 @ n_trials=1** (sr0=0 — high by construction, not a quality signal).
Full window +504.34% / Sharpe 1.3370 / MaxDD −50.21%; WF positive in **1 of 4** windows. Funding
EXCLUDED and basket survivorship-biased — both bias the bar *upward*, i.e. harder to beat. Spent no
trial. Criterion-3 return series: `research/benchmarks/perps_benchmark_TEST_returns.csv`.
Detail and caveats: `research/results/A-005_report.md`.

## Cycles completed

| Task ID | Hypothesis | Verdict | Primary reason |
|---|---|---|---|
| T-037 | Perps program transition (not a cycle) | **PROGRAM BOUNDARY, 2026-07-29** | Venue, cost model and trial ledger changed; spot results void as perps evidence. See `research/review_briefs/T-037_PERPS_TRANSITION_brief.md` |

*(First perps research cycle is T-038. Rows append below as cycles complete.)*

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
