# T-037 — Perps program transition brief

**Not a cycle verdict.** Records the boundary between the spot program (2026-05-14 → 2026-07-29,
38 index rows, `n_trials` 100) and the perps program. No hypothesis is assigned or implied here.

**Task IDs are a single monotonic global sequence and never reset.** This is **T-037**; the spot
program ended at T-036. **The first perps research cycle is T-038.** `n_trials` is a separate,
per-program counter and does reset — see below.

Carrying the highest Task ID, this resolves as the Director's mandatory brief until T-038's exists —
deliberately, since the last spot brief describes a program whose results this document voids.

## What changed

**Venue.** OKX spot → OKX USDT-margined perps (`user_data/config_perp.json`, 9 instruments). Perps
carry a **funding-rate P&L term absent from spot**. No spot result contains it.

**Cost model.** Implicit 15 bps/side, zero spread, no maker/taker split → explicit
`validator.COST_MODEL`: taker 9.0 bps/side, 18.0 bps round trip; maker path requires an explicit
`adverse_selection_bps`. Detail: `user_data/research/ARCHIVE_COST_NOTE.md`.

**Trial counter.** `n_trials` **resets to 0** — and only `n_trials`. Task IDs continue at T-038. The
spot program's 100 trials deflated Sharpes measured on a different instrument at a different cost.
Carrying the count forward would penalise perp results for spot selection, and carrying spot
*results* forward under a fresh count would launder them. Neither is acceptable, so the trial ledger
starts clean and no spot result may be quoted as a perps baseline.

## Carries forward

Findings independent of venue, cost and fill assumption:

- **Method.** 70/15/15 + walk-forward + Monte Carlo; DSR as a mandatory gate; Kaufman
  average-of-all-tests reporting; zero-cost pre-gates before spending a trial.
- **Process directives** in `research/STANDING_DIRECTIVES.md`, in full.
- **Data-integrity requirements.** The three fabrication events (T-019, T-023, T-025) are program
  history, not spot history.
- **Cost-free statistical facts**, measured on price series rather than net P&L: BTC-ETH show no
  cointegration on any tested window with a formal post-2024 break; Fear & Greed is reactive not
  anticipatory; DVOL changes lead rv30 changes while high-DVOL days carry better-than-average forward
  returns; a 5-feature logistic classifier fails in-sample significance on BTC.
- **Reserved holdout: all bars after 2026-05-27.** Unchanged and still binding.

## Void

Nothing below may be quoted as evidence in the perps program without being re-established.

- **Every performance number ever recorded**: Sharpe, CAGR, max DD, profit factor, win rate, MC
  tail, DSR — all computed at the old cost model on spot, including the champion's
  1.26 / −16.6% / +458% headline and its 0.41 held-out TEST Sharpe.
- **Champion status itself.** TrendVolTarget is a spot artifact at stale costs. The perps program has
  **no champion** until one is established on perp data; `current_champion.md` and
  `strategy_portfolio.md` are historical.
- **The 80/20 portfolio stance** (trial #98) — an allocation selected on those voided numbers.
- **Family closures that turned on fee drag**, principally intraday / sub-daily — reopened in
  `knowledge_base/hypothesis_bank.md`. Closures resting on non-cost evidence remain closed but were
  established on spot OHLCV, and are **not automatically binding on perps** where funding carry
  materially changes the construct.
- **All Engineer recommendations.** "Recommendations to the Director" sections in every
  `research/results/T-*_report.md` are void. They were written against spot economics, a champion that
  no longer holds status, and a trial counter that no longer applies. A prior recommendation is not a
  reason to test anything.

## Standing

The perps program selects its first hypothesis — **T-038** — under the normal Director process from
the mandatory context set. Nothing here is an assignment, a ranking, or a hint at where to start.
