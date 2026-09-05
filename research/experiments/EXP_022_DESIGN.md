# CRYPTO-EXP-022 design — systemic-cascade conviction portfolio

Date frozen: 2026-09-04 PDT. Parent: CRYPTO-EXP-013; diagnostic source:
CRYPTO-EXP-021 TRAIN trades only.

## Evidence-derived hypothesis

Same-bar B2 concurrency was monotonically associated with TRAIN expectancy:
one coin +63.9 bps/trade, two coins +139.6 bps, and at least three coins
+365.2 bps (medians +52.8, +46.6 and +357.8 bps). A broad simultaneous signal
is therefore stronger evidence of a true systemic liquidation than an isolated
coin signal.

## Frozen construction

- Use the exact nine-coin OKX B2 signals, exits and measured taker costs.
- An event qualifies only when at least three executable coin signals share the
  exact same completed 4h signal timestamp.
- Enter only if the event portfolio is flat. Allocate 100% unleveraged capital
  equally across the qualifying event's triggered coins at their normal next-bar
  entries. Each leg keeps its original B2 exit; exited capital remains cash until
  every leg has exited. Ignore all signals while any event leg remains open.
- No alternative concurrency threshold, partial exposure, overlapping event,
  coin subset, timing tolerance or signal parameter is tested.

## Chronological gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Held-out 2024-11-23 through
2026-09-01 remains sealed unless there are at least 10 events, 40 legs and six
coins; net return and Sharpe both exceed ordinary equal-sleeve B2; maximum
drawdown is no worse than base; and return remains positive after removing the
single best event.

If TRAIN passes, evaluate held-out once. The event portfolio must beat base return,
Sharpe and drawdown, have at least six positive coins, and remain positive with
2× costs, one-bar entry delay and its best event removed. Its consistent full
record must exceed +61.7% total return with maximum drawdown no worse than −5.5%
to beat the user's Claude hurdle. Otherwise reject without further concurrency
or allocation experiments.
