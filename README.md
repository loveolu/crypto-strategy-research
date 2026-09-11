# Crypto strategy research: a validation gate that says no

Four months (May to September 2026) of systematic strategy research on OKX spot and
USDT-perpetual data, run through a pre-registered validation pipeline. The headline result
is negative and documented: after roughly 100 statistical trials across 40 numbered research
tasks and a further 44 experiment cycles, **no strategy has cleared the bar for real edge**.
The one candidate that came closest is in forward paper trading, with its deflated Sharpe
ratio recorded as below the live-eligibility threshold.

Everything here is dry-run. No real capital was ever deployed on this research, every bot
config is `dry_run: true` with empty exchange keys, and that constraint is written into the
operator manual as standing policy.

## What the framework does

Every candidate goes through the same gates, in order, and the order is fixed before the
candidate is built:

1. **Chronological 70/15/15 split with walk-forward re-fitting** (`user_data/research/validator.py`).
   Later work uses 12-month train, 3-month test, 3-month step windows and re-fits only the
   pre-declared free parameter.
2. **Monte Carlo block-shuffle** of trade sequences for drawdown and tail estimates.
3. **Deflated Sharpe Ratio** (`freqtrade_dsr.py`, Bailey and Lopez de Prado 2014) with a
   cumulative trial counter. The counter is never reset inside a research line, so each new
   idea is charged for every idea tried before it. The project champion on daily bars has a
   raw Sharpe of 1.26 and a deflated Sharpe of 0.64 against a 0.95 bar. That gap is the
   selection luck, and it is why the champion is labelled "not edge".
4. **Measured execution costs**, not assumed ones. Order-book snapshots on OKX gave a
   taker round trip of 13.67 bps at $5k notional (maker 6.15), with per-instrument half-spread
   plus book-walk slippage. Every stress test then reruns at 2x and 3x cost and with 1 to 2
   bars of entry delay.
5. **Data integrity manifest**. Every OHLCV file is SHA-256 hashed (`scripts/data_manifest.py`)
   and verified before a cycle runs. A cycle that skips verification is invalid by rule.
   `research/DATA_INTEGRITY_AUDIT_2026-09-08.md` re-verifies every tracked file and all 87
   historical versions against the exchange.

Kill rules are pre-registered per experiment (`research/experiments/EXP_*_DESIGN.md`), and the
reviewer is required to reproduce every figure a finding rests on before signing off.

## How the research was run

The cycles were executed by an agent loop with three roles and persistent memory:
Director (chooses the next hypothesis and writes the pre-gate), Engineer (builds and runs it),
Reviewer (independently reruns and can reject). The prompts are in `prompts/`. A periodic
meta-review audits the loop itself.

The design question was whether a framework can be rigorous enough that agents running inside
it still produce honest rejections rather than curve-fit wins. Two outcomes are worth stating
plainly:

- The gate rejected the large majority of what went through it, including a 61-strategy
  autonomous search in June that passed zero candidates.
- The review layer caught three separate incidents where an engineer agent fabricated candles
  to pass a data-freshness check. The fabricated data was purged from git history, the tooling
  quarantined, and the full-history audit above was added as a permanent check.

## What was found

- **Regime, not signal, dominates crypto returns.** Trend-gated and dollar-neutral designs
  preserved capital through the 2022 bear (buy-and-hold was -75%); the only thing that made
  money that year was a trend-following short, which is bear beta rather than edge. In the
  choppy 2025-26 bear the same short lost.
- **Intraday cost wall.** A 72-cell census of 1h momentum on perpetuals found the best gross
  edge at 0.9x of one round trip, below the census's own noise floor.
- **Cascade reversion at 4h** (buy the hardest-hit perps after a large 24h drop, only inside a
  daily uptrend) is the only construct that survived walk-forward, top-5% trade removal, and
  3x cost. Its returns are concentrated in 2024 and flat since. It is in forward paper trading
  under a frozen rule set, not live.
- **A dollar-neutral cascade spread** is the first mechanism found to be uncorrelated with it
  (correlation 0.004). The 50/50 book has the best risk-adjusted profile in the project and
  still does not earn 20% a year across bear years. Nothing here does.

Full narrative in `HANDOFF.md`, `PROJECT_OPERATOR_MANUAL.md`, and the dated reports under
`research/`.

## Layout

| Path | What it is |
| --- | --- |
| `freqtrade_dsr.py` | Deflated Sharpe gate (AGPL-3.0 port, license header retained) |
| `user_data/research/` | Research scripts, phase-numbered, plus session reports |
| `user_data/research/validator.py` | Reusable split / walk-forward / Monte Carlo harness |
| `user_data/strategies/` | freqtrade strategy classes, champion and eliminated candidates |
| `user_data/data/` | Cached OKX OHLCV (feather), hashed in the manifest |
| `research/experiments/` | Experiment designs, log, leaderboard, queue, reports |
| `research/measurements/` | Cost calibration, walk-forward pickles, structural tests |
| `research/` | Iteration log, metrics, audits, standing directives |
| `knowledge_base/` | Hypothesis bank, closed families, edge framework, failure modes |
| `prompts/` | Director / Engineer / Reviewer / meta-reviewer prompts |
| `scripts/` | Data manifest, DSR entrypoint check, context budget, tests |

This repository was extracted from a fork of [freqtrade](https://github.com/freqtrade/freqtrade)
with `git filter-repo`, keeping only the research paths and their original commit history.
Upstream freqtrade code is not included; install it separately to run the strategies.

## Reading order

1. `HANDOFF.md` for the project in one page.
2. `research/experiments/RESEARCH_REPORT_2026-09-04_CURRENT.md` for the current state.
3. `research/experiments/SESSION_B_STRAT5_2026-09-05.md` for the latest five-strategy
   walk-forward and the 2022 out-of-sample test.
4. `knowledge_base/archive/closed_families.md` for what has been ruled out and why.
