# CRYPTO-EXP-035 — Outside Day with Outside Close

Date frozen: 2026-09-04 PDT. Independent parent: none. This is Arnold's named range-expansion
continuation rule recorded in `knowledge_base/08_entries.md`, not a cascade or volume-tail variant.

## Hypothesis

When a completed 4h candle expands beyond both sides of the preceding range and closes beyond the
preceding extreme, the directional auction is unresolved and continues over the next three bars.

## Frozen rule

- Nine liquid OKX USDT perpetuals; 4h bars mechanically resampled from canonical 1h data.
- Bullish signal: current high > prior high, current low < prior low, and close > prior high.
- Bearish signal: the same outside-range condition and close < prior low.
- Enter in the signal direction at the next 4h open. Stop at the signal candle's opposite extreme.
  A gap beyond the stop fills at the next bar's open; otherwise a touched stop fills at the stop.
  This deliberately prevents favorable impossible fills.
- If unstopped, exit at the open three 4h bars after entry. One position per coin; equal 1/9 sleeves;
  measured instrument-specific taker friction on entry and exit.
- Long and short results are reported separately. No volatility, trend, volume, BTC, wick, target,
  gap-size, asset-selection, or alternative-hold filter.

## Validation gates

TRAIN is 2023-01-22 through 2024-11-22 23:00 UTC. Held-out remains sealed unless the combined rule
has at least 300 trades and 20 per coin; gross expectancy exceeds expected round-trip cost; at least
six coins are net-positive; both long and short gross expectancy are positive; and combined gross
expectancy beats at least 97.5% of 999 shared circular-shift placebos (seed 35035, ≥30-day shifts).

If TRAIN passes, inspect 2024-11-23 through 2026-09-01 once. Require positive net return, Sharpe,
profit factor, six positive coins, both directions net-positive, two positive VAL/TEST/FWD segments,
and positive performance under 2× costs, one-bar delay, and top-5% trade removal. Then transfer the
unchanged rule to Kraken. The explicit superiority hurdle remains >+61.7% return with drawdown no
worse than −5.5%; consistent fixed-rule and walk-forward B2 remain separate comparisons.

One construct is evaluated. Failure does not authorize reversing the rule (which the source itself
suggests post hoc), selecting a direction, or tuning stop, hold, filters, or coins.

## Result

TRAIN produced **1,934 trades** (185–233 per coin). Both directions were positive before costs, but
weakly: longs +11.79 gross bps/trade and shorts +1.03 bps. Combined gross expectancy was only
**+6.18 bps** against **13.68 bps** expected round-trip friction. Net return was **−16.09%**, maximum
drawdown **−28.01%**, Sharpe **−0.70**, profit factor **0.92**, and only **2/9** coins were positive.
The economic and breadth gates failed, so the placebo was unnecessary and held-out stayed sealed.

**Verdict: REJECTED_TRAIN_GATE.** Range expansion has a small directional continuation tendency,
but less than half the edge needed to trade this rule at observed costs and without cross-coin
breadth. Do not mine BTC/ETH, select longs, reverse the setup, or tune stops/holding periods.

Full required diagnostics and cost-model boundaries: `EXP_033_035_FULL_DIAGNOSTICS.md` and the
machine-readable `research/measurements/EXP035/summary.json`.
