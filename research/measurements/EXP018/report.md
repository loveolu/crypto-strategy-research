# CRYPTO-EXP-018 — dual-exchange cascade confirmation

**Verdict: REJECTED at the TRAIN gate. Held-out data was not examined.**

The frozen rule required each OKX B2 cascade to be independently confirmed by the
same completed 4h Kraken coin and BTC bar. The common universe was ETH, SOL, XRP,
ADA, AVAX, DOT and LINK. Trades used OKX opens and measured instrument-specific
taker friction.

| TRAIN result | OKX B2 base | Dual-exchange confirmation |
|---|---:|---:|
| Trades | 161 | 107 |
| Net return | +53.01% | +36.92% |
| Sharpe | 1.83 | 1.45 |
| Maximum drawdown | −5.79% | −5.64% |
| Net expectancy | 191.46 bps | 214.21 bps |

The variation passed sample size (107 trades, at least 11 for every coin), but
failed four frozen requirements: expectancy improved by 22.75 rather than at
least 25 bps/trade; Sharpe fell; drawdown remained 97.4% of the base rather than
at most 85%; and it retained only 69.6% rather than at least 90% of base return.

The causal interpretation is useful but insufficient: Kraken agreement removes
some weaker events, yet it also discards profitable OKX cascades without isolating
drawdown. The exact rule is closed. No threshold, timestamp tolerance or asset
subset will be tuned after seeing this result.
