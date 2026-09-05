# Hypothesis-ledger audit — oscillator duplicate prevention

## Trigger

The post-EXP-035 screen selected the standard MACD crossover as apparently open because its card in
`knowledge_base/hypothesis_bank.md` had no `Already tested by this project` line. Before assigning an
experiment, the construct-usage census in `research/research_metrics.md` showed that MACD had already
been evaluated in Iteration 5's oscillator/hybrid batch.

## Authoritative evidence

`research/research_metrics.md`, “Common indicator / technique usage across all 97 tested constructs,”
records MACD, CCI, TSI, Coppock, Williams %R, Stochastic RSI, KAMA, and Chandelier Exit at roughly
one or two constructs each, with the batch conclusion that none cleared Sharpe 1.2. The same census
records ADX at roughly three constructs, with `adx_trend` showing a narrow parameter ridge rather
than a stable plateau. Chandelier already had an explicit project-test marker; MACD and the grouped
TSI/RVI/Awesome-Oscillator card did not.

## Repair

- Added an explicit prior-test marker to the MACD crossover card.
- Added an explicit batch-evidence marker to the grouped smoothed-momentum card, carefully limiting
  the claim to the named implementations actually recorded by the census; it does not claim every
  RVI/Awesome-Oscillator pattern was exhaustively tested.
- Cancelled the proposed MACD cycle before design or backtest. No experiment ID, trial, held-out
  access, or parameter search was spent.

## Research consequence

Do not rerun a standard MACD crossover or the previously evaluated oscillator implementations merely
because a card lacks a detailed row in the newer CRYPTO-EXP log. Reopening requires new evidence,
new data, or a mechanistically distinct rule—not a fresh experiment number. Continue screening cards
against both the hypothesis ledger and the 97-construct usage census.
