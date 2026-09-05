# CRYPTO-EXP-021 design — volatility-budgeted B2 sleeves

Date frozen: 2026-09-04 PDT. Parent: CRYPTO-EXP-013. This tests position sizing
only; B2 entries, exits, universe and execution costs remain unchanged.

## Hypothesis

The cross-venue audit showed that cascade returns synchronize. Equal 1/9 coin
sleeves therefore allocate the same capital to a high-volatility alt as to a lower-
volatility one exactly when systemic risk is elevated. Causal inverse-volatility
sizing may reduce clustered losses while retaining enough of B2's return to improve
the return/drawdown frontier.

## Frozen sizing rule

- Universe: the original nine OKX perps. Signal and exit: exact B2 4h rule.
- At each completed signal bar, calculate each coin's 42-bar (seven-day) realized
  volatility from completed 4h close-to-close returns and the cross-sectional median
  across all nine coins.
- Trade weight = `(1/9) × median_vol / coin_vol`, clipped to `[0.25/9, 1/9]`.
  Thus no trade exceeds its original sleeve and sizing never uses future volatility.
- Freeze the entry weight until exit. No leverage, portfolio renormalization, overlap
  reallocation, volatility-window changes or cap alternatives.

## Chronological gate

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Held-out 2024-11-23 through
2026-09-01 remains unopened unless the sized version has at least 150 trades and
seven coins represented; retains at least 75% of base return; has higher Sharpe;
maximum drawdown is at most 75% of base; and its worst coin's share of absolute
weighted P&L is lower than base.

If TRAIN passes, open held-out once. It must improve both Sharpe and drawdown over
base, retain at least 75% of base return, remain positive under 2× costs and one-bar
delay, and show at least six positive coins. The full consistent fixed-rule record
must jointly exceed +61.7% total return with drawdown no worse than −5.5% to beat the
user's Claude hurdle. Otherwise reject without sizing-rule optimization.
