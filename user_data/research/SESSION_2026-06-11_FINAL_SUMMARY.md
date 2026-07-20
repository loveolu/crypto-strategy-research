# Strategy Research — Final Rankings (2026-06-11, extended session)

Cumulative scope: **~85 strategy constructs tested** across 6 research sessions,
all under a uniform pipeline (fees 0.15%/side, anti-lookahead 2-bar lag,
70/15/15 chronological split, walk-forward, Monte Carlo).

---

## THE RANKING

### #1 — TrendVolTarget (BTC+ETH) — THE CHAMPION
*The strategy currently dry-running.*

```
core  = close > SMA200  AND  ROC30 > 0  AND  EMA20 > EMA50   (per asset, 1d)
size  = clip(40% / realized_vol_30d, 0, 1) in 25% steps, 50% equity cap/pair
exit  = any core condition breaks
```

| Validation | Result |
|---|---|
| Real Freqtrade engine, 6.5y spot | **+458% total, Sharpe 1.26, DD -16.6%** |
| BTC-only 8.4y (incl. 2018) | +30.7% CAGR, Sharpe 1.20, DD -23.6% |
| Bear years 2018 / 2022 / 2026-now | Flat / flat / flat — by design |
| Held-out test (2024-2026) | Sharpe 0.39, +5.4% CAGR — **only construct with clearly positive OOS** |
| Cross-asset transfer | **Positive Sharpe on 9/9 assets never tuned on** (median 0.65) |
| Monte Carlo | P(Sharpe<0)=0%; median DD -22%, P(DD<-25%)≈28% |
| Parameter sweeps | Plateaus everywhere (SMA 150-250, ROC 20-40, vol-target 30-50%) |

**Forward expectation (honest):** ~5-15% CAGR at ~20% max DD. Its edge is
sitting out bear markets, not predicting prices.

### #2 — TVT 9-Asset + Portfolio-Vol Overlay — THE DEFENSIVE VARIANT
Same construct across BTC, ETH, SOL, XRP, ADA, AVAX, DOT, LINK, BNB, equal
weight, plus a second vol-target layer (25%) on the whole portfolio.

| Metric | Result |
|---|---|
| Full window 5.6y | CAGR +14.0%, Sharpe 1.10, **DD -12.9%** |
| Held-out test | Sharpe 0.23, +2.3% CAGR (second best OOS) |
| Monte Carlo | **P(DD<-25%) = 1%** (vs champion's 28%) |

Lower return, drastically lower tail risk. The right choice if capital
preservation dominates. Diversification across 9 TVT streams (mean pairwise
correlation only 0.33) is what buys the thin tail.

### #3 — Hybrid: BTC Core + Top-2 Momentum Alts (15% satellites)
BTC TVT at 50% + the 2 strongest in-regime alts by risk-adjusted momentum.
Full-window Sharpe 1.28 (best of all), DD -21.8% — **but test Sharpe only
0.12**. The alt satellite added nothing OOS (no alt season since 2024).
Hold as a candidate to revisit IF alt regimes return; not for deployment.

### Superseded (good but dominated): hmm_two_state (Sharpe 1.20),
ensemble_voted_3of3 (1.15), xsect_mom_30d (1.18, DD -66%), vol_adj_basket (1.11).
All absorbed into or beaten by the TVT construct.

---

## ELIMINATED THIS SESSION (with reasons)

| Idea | Verdict |
|---|---|
| Return-stream blending of top strategies | Correlations 0.5-0.8 — never beats best component |
| Expanded-universe Sharpe boost | Full-window gains are train-period artifacts; alts drag OOS |
| Cross-sectional top-K momentum (9 assets) | Sharpe ≤1.17, DD -29..-51%, worse than champion |
| Long-short BTC-ETH pairs | Net negative across all parameterizations |
| Dual momentum (Antonacci) | Re-derives xsect mom: DD -66% |
| Halving-cycle regime | Q11 spikes as hard as Q2 — narrative doesn't survive data |
| Day-of-week / turn-of-month | t≈2 but too weak vs multiple-testing + fees |
| Intraday hours 21-22 UTC | REAL anomaly (t=2.4-3.0, stable) but fees kill it 25:1 |
| adx_trend | Parameter ridge (lucky peak), penalized on robustness |
| All 61 batch-1..5 single-asset constructs | Ceiling Sharpe 1.2, none pass gates |

## STRUCTURAL CONCLUSIONS (six sessions of evidence)

1. **The data's Sharpe ceiling is ~1.3** for anything risk-managed on retail
   OHLCV. Institutional gates (Sharpe ≥1.5) need data we cannot access
   (order book, funding history, on-chain flow).
2. **Regime avoidance is the only edge that survives every test** — and it
   transfers across all 9 assets. Signal prediction does not survive.
3. **Vol targeting is the only overlay that reliably improves risk** without
   hurting Sharpe. Drawdown control, calendar filters, satellites: no.
4. **Recent regime (2024-2026) is hostile** to all trend variants: test-period
   Sharpes 0.1-0.4 everywhere. Whatever deploys must expect this, not 2020-21.

## CURRENT STATE

- TrendVolTarget **dry-running live** (correctly flat — BTC $61.5k < SMA200 $78.2k)
- All research code in `user_data/research/` (phases 1-10 + validator harness)
- 9-asset daily data through 2026-05 in `user_data/data/okx/futures/`
- Standing rule: **dry-run only; no real capital on backtest evidence**
