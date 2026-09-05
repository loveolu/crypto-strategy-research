# CRYPTO-EXP-019 design — cross-venue B2 portfolio audit

Date frozen: 2026-09-04 PDT. Parents: CRYPTO-EXP-013 and CRYPTO-EXP-017.

## Hypothesis and construction

Venue-specific noise may make the frozen OKX and Kraken B2 implementations less
than perfectly correlated, allowing a 50/50 unleveraged venue allocation to reduce
drawdown while preserving return. Each venue keeps its frozen seven-coin equal-sleeve
implementation and existing expected costs. Returns are combined on a common 4h UTC
exit-bar ledger. The symmetric 50/50 allocation is the primary construction; 25/75
and 75/25 are sensitivity views only and may not be selected after inspection.

## Epistemic limit and success rule

Kraken's full B2 history was already inspected in CRYPTO-EXP-017. This is therefore a
retrospective diversification audit, not untouched OOS evidence, and cannot promote a
strategy. A useful result requires materially lower drawdown than both components and
must exceed the user's Claude hurdle jointly: return above +61.7% and drawdown no worse
than −5.5%. Otherwise the cross-venue portfolio is closed without weight optimization.
