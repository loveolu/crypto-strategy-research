# CRYPTO-EXP-029 — extreme-fear relief across the 2021–22 bear regime

Status: **Rejected at the discovery placebo gate. Retrospective transfer period not examined.**

## Purpose and evidence boundary

EXP-027 observed +112 net bps/trade across all nine perpetuals, but only 38 trades
during eight Extreme Fear days. EXP-029 transferred the exact frozen signal to
BTC/USDT spot and an earlier regime: 2021-05-25 through 2023-01-21. No threshold,
confirmation, or holding rule changed. Execution used next-open fills and a
conservative 22 bps spot round trip.

## Discovery result

| Trades | Gross expectancy | Net expectancy | Net return | Sharpe | Max DD | PF | Placebo p |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 145 | +28.62 bps | +6.58 bps | +5.25% | 0.25 | -25.10% | 1.08 | **0.250** |

The sample and gross-cost gates passed, but the 999-draw circular daily-sentiment
placebo decisively failed: shifted sentiment dates averaged +11.99 gross bps and
25% of null draws matched or exceeded the observed +28.62 bps. The result was also
regime-fragile: 2021 returned +17.85%, while 2022 lost -10.80% with -24.68% drawdown.
Friction consumed 31.96% of notional across the discovery record.

## Conclusion

The earlier, larger sample does not support Fear & Greed as a specific causal or
timing input. It appears to label price-stress periods in which generic relief
rallies sometimes occur, consistent with the prior finding that the index is
reactive. The 2023-01-22 through 2026-05-24 transfer period overlaps history already
seen by EXP-027; because the independent discovery gate failed, it remained sealed.

Close the exact sentiment-relief strategy. Do not search other fear thresholds,
holding periods, or candle confirmations. The immutable source price and sentiment
artifacts were not modified.
