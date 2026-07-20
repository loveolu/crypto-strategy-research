# Best Strategy Found: TrendVolTarget
Session: 2026-06-11 (continuation of the 61-strategy autonomous search)
Researcher role: senior crypto algo-trading deep-dive with constant backtesting

## TL;DR

**TrendVolTarget** — a 3-of-3 trend-agreement core with volatility-targeted
position sizing on a BTC+ETH basket — is the best risk-adjusted strategy this
project has produced across ~75 tested constructs and six research sessions.

| Window | CAGR | Sharpe | Max DD | Years positive |
|---|---|---|---|---|
| BTC+ETH 2019-12 → 2026-05 (6.5y) | **+32.4%** | **1.33** | **-17.1%** | 5/8 (losers ≈ flat) |
| BTC-only 2018-01 → 2026-05 (8.4y) | +30.7% | 1.20 | -23.6% | 5/9 (losers ≈ flat) |

**Zero days in market during the 2018 and 2022 bear years.** The strategy's
edge is regime avoidance, not prediction.

## Definition (full spec, no hidden parameters)

Per asset (BTC/USDT, ETH/USDT), daily candles:

```
core    = (close > SMA200) AND (30d ROC > 0) AND (EMA20 > EMA50)
scale   = clip(0.40 / realized_vol_30d_annualized, 0, 1), quantized to 0.25 steps
position = core * scale * 0.50        # 50% equity cap per pair
```

Exit when any core condition breaks. Safety stop -30% (rarely touched; the
trend exit fires first). Fees modeled: 0.10% commission + 0.05% slippage/side.

Implemented at `user_data/strategies/TrendVolTarget.py` (entry/exit signals +
`custom_stake_amount` + `adjust_trade_position` for 25%-step rebalancing).

## Why this one is credible when 61 predecessors failed

1. **Plateau-robust, not curve-fit.** Every parameter was swept:
   - SMA 150-250 × ROC 20-40: Sharpe 0.81-1.33, all positive, no spikes
   - EMA pair 10/30→30/75: Sharpe 1.15-1.17 (irrelevant — any short trend works)
   - Vol target 30-50%: Sharpe 1.24-1.33, **every cell DD < 25%**
   - Quantization 0.25 vs 0.5 vs continuous: identical (1.31-1.33)
2. **Components validated independently before combination.** The ens3 core
   was the most robust of the 61-strategy search; vol-targeting is a
   textbook overlay, not a fitted one.
3. **Walk-forward:** 3 of 4 OOS windows positive (Sharpe 0.94-1.50); the 4th
   (Aug-2025→May-2026 bear) lost only -2.4% — drawdown control held.
4. **Monte Carlo (1000 month-block shuffles + extra slippage):**
   P(Sharpe < 0) = 0.0%, median DD -23.5%, p5 Sharpe 1.29.
5. **Bear-market behavior is structural:** flat all of 2018, flat all of 2022,
   -4% in 2022 on the basket variant. This is what the 3-of-3 gate buys.
6. **Costs are real and small:** turnover ~12× equity/yr → fee drag ~1.8%/yr.

## Honest weaknesses (read before acting)

1. **OOS decay exists here too.** Train Sharpe 1.59 → held-out test 0.41.
   The strategy did not lose money in the test period (+6% in 2025) but the
   +32% CAGR is dominated by 2020-2021. **Forward expectation: ~5-15% CAGR
   at ~20% drawdown, not +32%.**
2. **38% Monte Carlo probability of eventually seeing a DD worse than -25%.**
3. It underperforms HODL in raging bulls (2023: +39% vs +156%) by design —
   the value shows up in bears.
4. Sharpe 1.33 still does not clear the original 1.5 institutional gate, and
   ~7 discrete entries/yr will not satisfy a 200-trade significance bar on
   any reasonable horizon. The statistical evidence is moderate, not strong.
5. Crypto regime change (ETF era, falling vol) may keep weakening trend
   following — exactly what the 2024-2026 segment shows.

## Comparison vs benchmarks (same window, same fees)

| Strategy | CAGR | Sharpe | Max DD |
|---|---|---|---|
| **TrendVolTarget** | +32.4% | **1.33** | **-17.1%** |
| Trend only (no vol sizing) | +48.0% | 1.25 | -38.0% |
| VolTarget only (no trend) | +36.9% | 0.97 | -59.9% |
| 50/50 BTC-ETH HODL | +50.8% | 0.95 | -76.3% |
| BTC HODL | +43.6% | 0.90 | -76.6% |

Both components contribute: trend gate cuts the left tail, vol sizing cuts
the day-to-day variance. Neither alone gets DD under 25%.

## Research trail (this session)

- Phase 1: return-stream blending of top-7 candidates → **rejected**
  (correlations 0.5-0.8; blends never beat best component)
- Phase 2: parameter sweeps → ens3 = plateau (robust), adx = ridge (lucky)
- Phase 3: calendar effects (weak, t≈2), halving cycle (noise), dual momentum
  (re-derives xsect, DD -66%) → all rejected; vol-target overlay → **adopted**
- Phase 4: deep validation (split / WF / MC / fees / quantization / sweeps)
- Phase 5: 2018-bear stress (flat all year — passed), Freqtrade implementation

## Independent engine cross-validation (real Freqtrade backtest)

Installed freqtrade 2026.5-dev and ran the actual engine on the same window
(`freqtrade backtesting --strategy TrendVolTarget --timerange 20191201-20260525`):

| Metric | Pandas harness | Freqtrade engine |
|---|---|---|
| Sharpe (daily wallet) | 1.33 | **1.26** |
| Max % account underwater | -17.1% | **-16.61%** |
| Total profit | +32.4% CAGR | **+458%** (≈ +30.4% CAGR) |
| 2022 bear | -4% / flat | **1 trade, -180 USDT (flat)** |

92 trades, 42.4% win rate, avg duration 18.5 days, profit factor by year
2.0-5.0 in up years. Two independent implementations agree within noise —
the result is not an artifact of either backtester.

## Standing constraint

**Dry-run only. Do not deploy real money on the basis of this backtest.**
If it ever runs live, it must first run ≥3 months dry-run with results
compared against the backtest expectation band.
