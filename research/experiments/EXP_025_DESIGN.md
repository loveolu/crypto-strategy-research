# CRYPTO-EXP-025 design — B2 selection-bias audit

Date frozen: 2026-09-04 PDT. Subject: CRYPTO-EXP-013 B2.

## Question

Does B2 remain statistically credible after accounting for the many strategy and
parameter variants examined in this project, non-Gaussian returns and serial
dependence? This is an evidence audit, not a strategy modification.

## Frozen analyses

- Recompute the exact fixed-rule nine-coin B2 stream and the stitched 12m-train /
  3m-test rolling walk-forward B2 stream from canonical data.
- Compute Deflated Sharpe Ratio on: fixed-rule individual trade returns; fixed-rule
  daily portfolio returns; walk-forward daily portfolio returns; and active days
  for both daily streams.
- Report conservative selection counts N={50,100,200,1000}. The perps trial ledger
  has no data rows, so use the documented skew/kurtosis-adjusted Sharpe-estimator
  variance proxy and label this limitation; do not mix the incompatible spot ledger.
- Independently run 10,000 circular 30-day block bootstraps of walk-forward daily
  returns with seed 25025. Report the probability of positive annualized Sharpe and
  its 5th/50th/95th percentiles. Blocks preserve within-month dependence.

## Decision rule

B2 retains Candidate/Paper Trading status only if walk-forward all-day DSR is at
least .95 at N=200 and the block-bootstrap probability of positive Sharpe is at
least .95. N=1000 is a reported sensitivity, not the primary gate. Failure downgrades
the historical evidence; passing does not prove future profitability and does not
replace the live forward gate.
