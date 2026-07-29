# T-000-PERPS — Program transition brief

**Not a cycle verdict.** This records the boundary between the spot research program (2026-05-14 →
2026-07-28, 37 index rows, `n_trials` 100) and the perps program that follows. Written 2026-07-28
during the repo repair. No hypothesis is assigned or implied here.

## What changed

**Venue and instrument.** OKX spot → OKX USDT-margined perpetual swaps
(`user_data/config_perp.json`, 9 instruments). Perps carry a **funding-rate P&L term that does not
exist in spot**. No spot result contains it.

**Cost model.** Implicit 15 bps/side with zero spread and no maker/taker distinction → explicit
`validator.COST_MODEL`: taker 9.0 bps/side / 18.0 bps round trip, maker path requiring an explicit
`adverse_selection_bps`. Detail: `user_data/research/ARCHIVE_COST_NOTE.md`.

**Trial counter.** `n_trials` **resets to 0.** The spot program's 100 trials deflated Sharpes
measured on a different instrument at a different cost. Carrying the count forward would penalise
perp results for spot selection, and carrying spot *results* forward under a fresh count would
launder them. Neither is acceptable, so the ledger starts clean and no spot result may be quoted as
a perps baseline.

## Carries forward

Findings independent of venue, cost and fill assumption:

- **Method.** 70/15/15 + walk-forward + Monte Carlo architecture; DSR as a mandatory gate;
  Kaufman average-of-all-tests reporting; zero-cost pre-gates before spending a trial.
- **Process directives** in `research/STANDING_DIRECTIVES.md`, in full — including the
  claim-must-cite-test rule and the shock-share unverified-by-default rule.
- **Data-integrity requirements.** Three fabrication events (T-019, T-023, T-025) are program
  history, not spot history.
- **Cost-free statistical facts** about the underlying assets, which were measured on price series
  and not on net P&L: BTC-ETH show no cointegration on any tested window with a formal post-2024
  break; Fear & Greed is reactive rather than anticipatory; DVOL changes lead rv30 changes while
  high-DVOL days carry better-than-average forward returns; a 5-feature logistic direction
  classifier fails in-sample significance on BTC.
- **Reserved holdout: all bars after 2026-05-27.** Unchanged and still binding.

## Void

Nothing below may be quoted as evidence in the perps program without being re-established.

- **Every performance number ever recorded**: Sharpe, CAGR, max DD, profit factor, win rate, MC
  tail, DSR. All were computed at the old cost model on spot. This includes the champion's
  1.26 / −16.6% / +458% headline and its 0.41 held-out TEST Sharpe.
- **Champion status itself.** TrendVolTarget is a spot artifact evaluated at stale costs. The perps
  program has **no champion** until one is established on perp data. `current_champion.md` and
  `strategy_portfolio.md` describe the spot program and are historical.
- **The 80/20 portfolio stance** (trial #98) — an allocation selected on those voided numbers.
- **Family closures that turned on fee drag**, principally intraday / time-of-day / sub-daily. The
  old cost model overstated achievable perp round-trip cost; that family is reopened for re-test in
  `knowledge_base/hypothesis_bank.md`. Closures resting on non-cost evidence remain closed, but were
  established on spot OHLCV and are **not automatically binding on perp instruments** where funding
  carry materially changes the construct.
- **All Engineer recommendations.** "Recommendations to the Director" sections in every
  `research/results/T-*_report.md` are void and carry no weight. They were written against spot
  economics, a live champion that no longer holds status, and a trial counter that no longer
  applies. A prior recommendation is not a reason to test anything.

## Standing

The perps program selects its first hypothesis under the normal Director process from the mandatory
context set. Nothing in this brief constitutes an assignment, a ranking, or a suggestion of where to
start.
