# Session 2026-07-02 — DSR audit + Forven-derived strategies

Inputs: user-provided `freqtrade_dsr.py` (Deflated Sharpe Ratio, ported from
Forven) and the Forven repo (github.com/judder659/Forven) as an idea source.

## 1. Deflated Sharpe Ratio audit of the champion (phase11_dsr.py)

DSR = P(edge is real | we picked the best of n_trials attempts). Bar: >= 0.95.

| Series | n_trials=85 | n_trials=300 | n_trials=1000 |
|---|---|---|---|
| Per-trade (92 trades, real engine) | 0.67 | 0.50 | 0.36 |
| Per-day (2339 days, harness) | 0.64 | 0.48 | 0.34 |
| BTC buy-and-hold (n_trials=1) | 0.988 | — | — |

**Verdict: TrendVolTarget does NOT clear the DSR bar.** After correcting for
having selected it as best-of-~85 constructs, the probability its edge is real
is ~64% — a favorable coin flip, not statistical proof. BTC HODL ironically
scores 0.988 because it was never selection-fished. This quantifies what the
70/15/15 splits kept showing (train 1.59 → test 0.41).

Corollary: every additional construct we test *further deflates* whatever we
eventually pick. Grinding more variants on the same daily OHLCV is now
provably counterproductive without new data or a longer OOS window.

## 2. Forven repo review

Forven is an autonomous strategy-lab (hypotheses → gauntlet → paper → live)
for Hyperliquid. Its "Gauntlet" mirrors our pipeline (walk-forward, MC,
parameter-jitter, cost-stress) and adds the DSR gate we just adopted.
~75 builtin strategies; most overlap constructs we already eliminated, and its
funding/liquidation/taker-flow strategies need data we've confirmed we can't
get. Four genuinely new axes were tested (phase12, phase13):

| Idea (Forven source) | Result vs champion (TEST Sharpe 0.39, MC P(DD<-25%) 28%) |
|---|---|
| Supertrend(10,3) state machine | ELIMINATED — TEST -0.92, DD -41%, MC 100% |
| Supertrend + SMA200 gate | ELIMINATED — TEST -0.09, dominated everywhere |
| Chandelier ATR exit on TVT core | ELIMINATED — exit-only worse (TEST -0.20); OR-core identical to champion (chandelier never fires first) |
| BTC-dominance rotation proxy (lb 7/14/30d) | ELIMINATED — full Sharpe 1.30 is train artifact (TRAIN 1.67, TEST 0.21-0.24), MC tail worse |
| ETH/BTC z-score fade (long-only) | ELIMINATED — TEST -1.45 raw / -1.46 gated; regime-unstable (VAL +1.7) |
| 75% champion + 25% gated z-fade | MARGINAL — MC tail better (10%) but TEST lower (0.30) and sleeve is OOS-negative; not defensible |

## 3. What we adopted from this session

- `freqtrade_dsr.py` stays at repo root as a permanent pipeline stage: any
  future candidate must report DSR with honest cumulative n_trials (now ~95).
- `validate_robustness_payload()` legitimacy gates available for the harness.
- The champion TrendVolTarget remains unbeaten. Its honest status is now
  sharper: ~64% probability of real edge, forward expectation 5-15% CAGR.

Standing rule unchanged: **dry-run only, no real capital on backtest evidence.**
