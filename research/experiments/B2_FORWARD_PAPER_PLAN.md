# B2Cascade4h forward-paper plan

Pre-registered 2026-09-05. This is an execution/decay measurement of the frozen
CRYPTO-EXP-013 Candidate, not another optimization trial. It is dry-run only and
does not authorize real-money trading.

## Frozen rule

- Universe: BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOT and LINK OKX USDT perpetuals.
- Resolution: 4h; long only; unleveraged intent; next available execution at the
  4h signal close using market orders.
- Entry: 42-bar downside-semideviation percentile over 180 bars is at least 0.80;
  24h return is at most -3.85%; BTC 24h return is below zero; the instrument's
  completed daily close is above SMA200 and EMA20 is above EMA50.
- Exit: dispersion percentile below 0.50 or 24 hours after entry.
- Execution proxy: taker, with the perp config's 9 bps all-in cost per side.
- Allocation: 500 USDT per position, at most nine simultaneous positions, in a
  dedicated 5,000 USDT simulated wallet.

Any rule, threshold, universe, timeframe, allocation or cost change creates a
new experiment and must not rewrite this forward record.

## Evidence and gates

The comparison baseline is fixed-split OOS expectancy +149 bps/trade and win
rate 63%. The monitor reports after-cost 30/90/180/365-day compounded return,
expectancy, win rate and profit factor from closed dry-run trades.

- `COLLECTING`: either 90-day quarter has fewer than 15 closed trades.
- `READY_FOR_REVIEW`: profit factor is above 1.0 in each of two consecutive,
  non-overlapping 90-day windows, with at least 15 trades in each. This permits
  human review only; it is not automatic live promotion.
- `DEGRADED`: profit factor is below 1.0 in both qualifying quarters.
- `MIXED`: populated quarters disagree.

Decision-time signal price, proposed simulated fill price and latency are logged
separately so execution drift is observable. The bot uses a dedicated database,
log and scheduled keepalive and must not interact with the existing spot bot.
