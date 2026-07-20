# Strategy Portfolio — validated strategies and allocation view

> Per PROJECT_OPERATOR_MANUAL.md. Last updated 2026-07-11 (H-TailAlloc portfolio promotion).
> Reality check: this project has ONE partially-validated strategy mechanism (regime avoidance)
> deployed two ways (concentrated champion + defensive variant), plus ONE validated **allocation
> stance** combining them. There is still no genuinely uncorrelated second edge.

## Portfolio slot 1 — TrendVolTarget (BTC+ETH) — CORE

- **Code**: `best_strategy_so_far.py` / `user_data/strategies/TrendVolTarget.py`
- **Intended regime**: sustained bull trends; flat (cash) in bear regimes by design.
- **Validation metrics**: full-window Sharpe 1.26 / DD -16.6% / +458% (6.5y, real engine);
  TEST Sharpe 0.41; walk-forward 3/4 positive; MC P(Sharpe<0)=0%, P(DD<-25%)≈28-38%;
  DSR 0.64 at n_trials=85. Parameter plateaus throughout.
- **Strengths**: only construct with positive OOS; transfers to 9/9 untuned assets;
  zero market days in 2018/2022 bears; engine-verified; simple and explainable.
- **Weaknesses**: DSR below 0.95 bar (edge ~64% credible); weak in choppy regimes
  (2024-26 test Sharpe 0.41); underperforms HODL in raging bulls; concentrated in one
  mechanism (regime avoidance).
- **Expected behavior**: long stretches flat; ~7 entries + ~22 rebalances/yr; most return
  arrives in a few sustained trend legs. Forward expectation 5-15% CAGR at ~20% DD.
- **Correlation**: n/a (only core holding).
- **Suggested capital allocation**: 100% of *risk budget* IF the single-strategy stance is
  kept — but per standing rule, currently **0% real capital; dry-run only.** See **Recommended
  portfolio stance** below for the validated 80/20 alternative.
- **Reason for inclusion**: best survivor of 95+ constructs under the full gate stack.

## Recommended portfolio stance — 80% Champion / 20% Defensive (validated 2026-07-11)

> **This is the project's current recommended deployment configuration**, per H-TailAlloc
> trial #98. It is an ALLOCATION between two validated streams of the same mechanism — not
> a new strategy and not a second independent edge.

- **Spec**: 80% capital to Portfolio slot 1 (TVT BTC+ETH) + 20% to Portfolio slot 2
  (TVT 9-asset + 25% portfolio-vol overlay), rebalanced back to (0.80, 0.20) **monthly**
  on completed month-end dates; inter-slice reallocation charged at 0.15%/side on the
  traded fraction (both legs).
- **Formula selection**: w* = largest w ∈ {0.0…1.0 step 0.1} with MC P(DD<−25%) ≤ 20%
  on the monthly-rebalanced implementable blend (pre-registered in SESSION_2026-07-11_TAILALLOC.md).
- **Validation metrics** (2020-01→2026-05, harness): CAGR +21.1%, Sharpe 1.14, MaxDD −15.9%;
  TEST Sharpe 0.38; MC P(DD<−25%)=**16.5%** (vs champion 30.5%, defensive 0.7%); DSR 0.6423
  at n_trials=98 (≥ champion 0.6245); WF 3/4 majority-positive.
- **Why w*=0.8 and not higher**: w=0.9 fails the MC tail bar (22.1%); the frontier knee is
  narrow — there is no slack above 80% champion weight.
- **Strengths vs champion alone**: MC tail −14pp (30.5%→16.5%) with TEST Sharpe essentially
  unchanged (0.38 vs 0.39) and +7pp CAGR vs defensive alone.
- **Weaknesses vs champion alone**: ~1.6pp lower CAGR (+21.1% vs +22.7%); dilution in strong
  BTC/ETH trend legs (2020 −8.4pp, 2023 −1.5pp vs champion); still a single-mechanism book
  (return correlation r≈0.80 between sleeves).
- **Expected behavior**: same regime-avoidance mechanism as the champion; slightly lower
  exposure in concentrated trend legs; measurably thinner MC drawdown tail. Forward expectation
  ~8–18% CAGR at ~18% MaxDD (between the two endpoints, closer to champion).
- **Implementation note**: freqtrade dry-run currently runs the champion sleeve only; deploying
  this stance live would require two parallel strategy instances or a custom allocator — not
  yet built. Backtest evidence supports the allocation; implementation is an engineering task.
- **When to use defensive-only (slot 2 at 100%) instead**: if MC tail ≤1% dominates and
  ~14% CAGR is acceptable (capital preservation first).

## Portfolio slot 2 — TVT 9-Asset + 25% Portfolio-Vol Overlay — DEFENSIVE VARIANT (bench)

- **Spec**: same TVT construct across BTC, ETH, SOL, XRP, ADA, AVAX, DOT, LINK, BNB, equal
  weight, plus second vol-target layer (25%) at portfolio level.
- **Validation metrics**: 5.6y CAGR +14.0%, Sharpe 1.10, DD -12.9%; TEST Sharpe 0.23;
  MC P(DD<-25%)=1% (vs core's 28%).
- **Strengths**: drastically thinner tail; mean pairwise correlation of the 9 TVT streams
  only 0.33 — the diversification is real at the risk level.
- **Weaknesses**: lower return; alts have dragged OOS since 2024; more moving parts.
- **Correlation with slot 1**: high (same signal, overlapping assets) — this is a RISK-PROFILE
  alternative to slot 1, not a diversifying addition. Do not run both.
- **Suggested role**: substitute for slot 1 if capital preservation dominates.

## Explicitly NOT in the portfolio (and why)

- Hybrid BTC-core + alt momentum satellites: TEST Sharpe 0.12; satellites added nothing OOS.
  Revisit only if a genuine alt regime returns.
- hmm_two_state, ensemble_3of3, vol_adj_basket, xsect momentum: dominated by/absorbed into
  TVT; DDs -33% to -66%.
- All mean-reversion, squeeze, overnight, calendar, pairs, dominance-rotation, z-fade
  constructs: failed validation (see `strategy_iteration_log.md`).

## Portfolio evolution criteria (from the manual + project evidence)

A second strategy earns a slot only if: (1) mechanism is structurally different from regime
avoidance, (2) return-stream correlation with TVT < ~0.4, (3) passes the full gate stack
including DSR at the then-current n_trials, (4) positive TEST-set performance standalone.
Six sessions of evidence say this will most likely require a NEW DATA AXIS (COT positioning
is the only reachable candidate) rather than another OHLCV construct.
