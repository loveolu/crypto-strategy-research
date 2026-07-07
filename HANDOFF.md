# Project Handoff — Freqtrade Strategy Research

Written 2026-07-07 for a Windows → MacBook migration. This is a research
project on top of a freqtrade fork, not a running trading bot. Read this
before doing anything else.

## 0. Standing constraint (read first)

**Do not deploy real money based on this backtest research.** Every config
in this repo must stay `dry_run: true` with empty `key`/`secret`. This rule
has held across the whole project and should not change without a deliberate,
separate decision.

## 1. What this project is

An autonomous search for a profitable crypto trading strategy, backtested on
freqtrade against BTC/ETH (and a wider 9-asset universe for some tests) OKX
futures 1-day OHLCV data. After 95+ tested constructs across many sessions,
**no strategy has cleared a rigorous statistical bar for "real edge."** The
current state is a documented negative/marginal result, not a deployable
system. That is the honest and complete finding — see §4.

## 2. Repo layout (what matters)

- `user_data/research/` — the actual research code, phase-numbered scripts
  (`phaseN_*.py`) each testing a batch of strategy ideas against a standard
  validation pipeline. Session reports are `SESSION_*.md` files in the same
  directory — read these for narrative context, they're better than the code
  alone.
- `user_data/research/validator.py` — reusable harness: 70/15/15 chronological
  split + walk-forward + Monte Carlo block-shuffle. Use this for any new
  candidate rather than re-deriving the pipeline.
- `freqtrade_dsr.py` (repo root) — Deflated Sharpe Ratio module (Bailey &
  López de Prado 2014), ported from github.com/judder659/Forven under
  AGPL-3.0. **Keep the license header if you keep or redistribute this file.**
  This is now a mandatory final gate: report DSR before calling anything an
  edge.
- `user_data/data/okx/` — cached OHLCV data (spot in root, futures in
  `futures/`), feather format. This is what all the research scripts read.
- `user_data/config.json` — dry-run config, tracked in git (verified safe:
  `dry_run: true`, empty API keys).
- `user_data/strategies/` — freqtrade Strategy classes. The champion is
  `TrendVolTarget.py`; the rest are earlier eliminated candidates kept for
  reference (`EmaRsiVolumeStrategy.py`, `OvernightVolSizedBreakout.py`,
  `RiskManagedBetaOverlay.py`, etc. — all superseded, see memory/session
  reports for why each failed).
- `user_data/backtest_results/` — freqtrade's native backtest output zips.

Note: `.gitignore` excludes `user_data/*` by default (freqtrade's default),
so tracked files under `user_data/` were force-added (`git add -f`). If you
add new files there and want them tracked, you'll need `-f` too.

A `books/` folder (reference PDFs) exists locally but is gitignored and was
never pushed — re-source your own reference material if you want it on the
new machine, don't expect it to come over from this repo.

## 3. Validation pipeline (apply to any new idea)

1. Fees: 0.15%/side.
2. Anti-lookahead: signal computed on bar close, position = `signal.shift(2)`
   (2-bar lag).
3. Split 70% train / 15% validation / 15% test, chronological (no shuffling
   across time).
4. 4-window walk-forward over the back half of the series.
5. Monte Carlo: monthly-block shuffle, 500 iterations, seed 11 — reports
   median drawdown and P(drawdown < -25%).
6. **Deflated Sharpe Ratio** (`freqtrade_dsr.py`) at the current cumulative
   `n_trials` (see below) — must clear ≥0.95 to be called a real edge.

Judge everything on TEST-set and walk-forward numbers, never on the full-
window backtest — full-window Sharpe is consistently ~2-4x inflated by
in-sample fitting across this whole project.

## 4. Where the research landed

- **~95 total constructs tested** (cumulative `n_trials` for DSR — this
  number does not reset per session; every new test further deflates future
  picks' credibility, so grinding more variants on the same OHLCV is now
  provably counterproductive).
- **Best candidate: TrendVolTarget** (BTC+ETH, 1d) — core signal
  `close>SMA200 AND ROC30>0 AND EMA20>EMA50`, position sized by
  `clip(0.40/realized_vol_30d_annualized, 0, 1)` quantized to 0.25 steps,
  50% equity per pair.
  - Full-window (6.5y): Sharpe 1.26, max DD -16.6%, +458% cumulative.
  - Held-out TEST split: Sharpe 0.41 (real engine trades) / 0.39 (harness).
  - **DSR = 0.64-0.67 at n_trials=85** (0.50 at 300, 0.35 at 1000) — well
    short of the 0.95 bar. Roughly half the backtest Sharpe is selection
    luck, not edge.
  - BTC buy-and-hold over the same window: DSR = 0.988 (n_trials=1, never
    selection-fished) — included as a sobering baseline.
  - **Honest forward expectation: ~5-15% CAGR**, not the headline +458%.
- **Everything else tested has been eliminated**, including a large batch of
  ideas mined from github.com/judder659/Forven (Supertrend, Chandelier exit,
  BTC-dominance rotation, ETH/BTC z-score fade, and blends) — all
  underperformed the champion or failed walk-forward/MC gates. Full
  elimination table: `user_data/research/SESSION_2026-07-02_FORVEN_DSR.md`.
- **Bottom line:** the project's live open question is no longer "can we
  find something better" (95 attempts say: unlikely, and each new attempt
  makes any future pick less credible) — it's "is the existing 64%-credible
  edge real," which only forward dry-run evidence or genuinely new data
  (not another parameter sweep) can resolve.

For the full narrative, read the memory files under
`C:\Users\Comec\.claude\projects\...\memory\` on the old machine (or ask
Claude to summarize — it should carry over if you're continuing with Claude
Code) or the `SESSION_*.md` files in `user_data/research/` in commit order.

## 5. Setting up on macOS

1. Python: use 3.11-3.13 (this project was run on 3.13 on Windows;
   freqtrade officially supports 3.10-3.13). `python3 -m venv .venv && source
   .venv/bin/activate`.
2. Install freqtrade dependencies: `pip install -e .` from repo root, or
   follow freqtrade's own docs (`docs/installation.md`) for the standard
   setup script. TA-Lib C library is normally required by freqtrade's
   built-in indicators, but the champion strategy and all research scripts
   here are pure pandas/numpy — you can skip the TA-Lib C-extension install
   if you only intend to run the research scripts, but install it if you
   want to run `freqtrade backtesting` on the strategy classes in
   `user_data/strategies/`.
3. `pip install scipy` — required by `freqtrade_dsr.py`.
4. Data: `user_data/data/okx/` (spot) and `user_data/data/okx/futures/`
   (futures, used by most research scripts) should already be present in
   the repo (tracked via `git add -f`, feather format, no re-download
   needed). Verify with:
   ```
   ls user_data/data/okx/futures/*.feather
   ```
   If a script references a symbol/timeframe not present, re-download via
   `freqtrade download-data` (needs exchange API reachability, not keys).
5. Run a research script directly, e.g.:
   ```
   python user_data/research/phase11_dsr.py
   ```
   Note: scripts currently have Windows-style absolute paths hardcoded
   (`C:/Users/Comec/Projects/freqtrade/...`) at the top via `sys.path.insert`
   and `Path(...)` — **update these to the new repo path on macOS** before
   running. Search for `C:/Users/Comec` across `user_data/research/*.py`.
6. To run freqtrade itself (backtest or dry-run), use `user_data/config.json`
   as-is — it's already dry-run-safe. Never populate `key`/`secret` with
   real exchange credentials without a separate, explicit decision.

## 6. Notes on `freqtrade_dsr.py` licensing

This file is a faithful port of DSR math from Forven
(github.com/judder659/Forven, AGPL-3.0), with attribution header intact. It
is fine to keep and use, including in this public fork, as long as the
header stays. Do not strip the header, and if you ever build a derivative
service around it, be aware AGPL's network-use clause may apply (it doesn't
for local backtesting scripts like this).

## 7. Immediate next steps if you want to keep going

- Nothing about the strategy needs more parameter grinding — that's proven
  counterproductive (see §4). The productive next steps are either (a) let
  the existing champion run in dry-run for a meaningful stretch to get
  genuine out-of-selection evidence, or (b) bring in a new data source
  (the project has repeatedly hit walls trying to get funding rates,
  liquidations, or sentiment data — if you have access to any of those on
  the new machine, that's the highest-value unexplored axis).
- If restarting dry-run, it was previously stopped; nothing is currently
  running. Use `freqtrade trade --config user_data/config.json --strategy
  TrendVolTarget` and consider a durable runner (launchd on macOS,
  analogous to Task Scheduler on Windows) if you want it to survive reboots.
