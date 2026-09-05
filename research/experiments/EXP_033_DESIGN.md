# CRYPTO-EXP-033 — 5-bar fractal breakout

Date frozen: 2026-09-04 PDT. Independent parent: none. This is the untested named system in
`knowledge_base/04_breakouts.md`, not a cascade-family modification.

## Hypothesis

After a confirmed five-bar pivot low, a later close above that pattern's highest high identifies
buyers overcoming a defended trough. The breakout should continue far enough to reach one pattern
range of profit within 24 hours, after realistic perpetual-futures costs.

## Frozen rule

- Nine liquid OKX USDT perpetuals; 4h bars resampled mechanically from canonical 1h bars.
- A down fractal is confirmed only after all five bars close: the center low is strictly below each
  of the two preceding and two following lows. The latest confirmed fractal replaces any older,
  untriggered one.
- Pattern low/high are the minimum low and maximum high of those five completed bars. A breakout is
  recognized only when a later completed bar closes strictly above the pattern high. This avoids an
  unknowable intrabar signal/fill ordering.
- Enter long at the next 4h open. Target = actual entry open + the frozen fractal's high-low range.
  If a later bar's high reaches the target, fill at the target; otherwise exit at the open exactly
  six bars (24h) after entry. No stop, matching the source's best reported variant.
- A coin holds at most one position; the triggering fractal is consumed. Equal 1/9 sleeves. Apply
  measured instrument-specific taker friction on both sides. No BTC trend gate, volume filter,
  threshold, short mirror, coin selection, alternative target, or holding-period search.

## Validation gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Held-out remains sealed unless TRAIN has at least
100 trades and 10 per coin; gross expectancy exceeds expected round-trip cost; at least six coins
are net-positive; and observed mean gross return beats at least 97.5% of 999 circularly shifted
signal placebos (seed 33033; minimum shift 30 days).

If TRAIN passes, inspect 2024-11-23 through 2026-09-01 once. Require positive net return, Sharpe,
and profit factor; six positive coins; two positive VAL/TEST/FWD segments; and positive results at
2× costs, one-bar entry delay, and after removing the top 5% of trades. A surviving rule must then
transfer unchanged to Kraken. Superiority additionally requires return above +61.7% with drawdown
no worse than −5.5%; the consistent B2 and true walk-forward comparisons remain separate.

One pre-registered construct is evaluated. Failure is recorded without reversing direction or
tuning the fractal definition, timeout, target, or asset subset.

## Result

TRAIN produced 1,587 trades (all coins had 164–194), so sample size was not the problem. Gross
expectancy was only **+5.81 bps/trade** against **13.71 bps** expected round-trip friction. After
costs the strategy returned **−14.92%**, with **−28.94%** maximum drawdown, **−0.49 Sharpe**,
**0.94 profit factor**, and only **3/9** positive coins. The economic and breadth gates failed, so
the circular placebo was unnecessary and the held-out period was not opened.

**Verdict: REJECTED_TRAIN_GATE.** The exact long-only 4h fractal breakout is too weak to pay taker
costs on liquid crypto perpetuals. Zero held-out trials were spent. Do not add a BTC gate, tune the
timeout/target, loosen the pivot, choose coins, or reverse it post hoc.

Full required diagnostics and cost-model boundaries: `EXP_033_035_FULL_DIAGNOSTICS.md` and the
machine-readable `research/measurements/EXP033/summary.json`.
