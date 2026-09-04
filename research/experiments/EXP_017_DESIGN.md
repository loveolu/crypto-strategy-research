# CRYPTO-EXP-017 design — B2 cross-exchange transfer to Kraken Futures

Date pre-registered: 2026-09-04 PDT. Parent: CRYPTO-EXP-013/B2Cascade4h.

## Hypothesis

B2 reflects market-wide liquidation/reversion rather than an OKX-specific artifact.
Therefore its exact frozen rule should retain positive after-cost expectancy on Kraken
USD perpetuals without any threshold refit.

## Data and frozen rule

- Source: public Kraken Futures chart API, native 4h trade candles and native 1d
  trade candles, 2023-01-22 through 2026-09-01 where listed.
- Common universe: BTC plus ETH, SOL, XRP, ADA, AVAX, DOT and LINK. BNB has no Kraken
  perpetual and is excluded before data is viewed.
- Exact B2: 42-bar downside-semideviation; 180-bar rolling percentile ≥0.80;
  24h return ≤−3.85%; BTC 24h return <0; prior completed daily close>SMA200 and
  adjusted EMA20>EMA50. Enter next 4h open; exit next open after percentile <0.50
  or six held bars. Long only, equal 1/7 alt sleeves, unleveraged.
- No Kraken parameter fitting, asset removal, alternative bar alignment or rule change.
- Cost scenarios: 0 bps gross, 18 bps expected round trip (the Candidate's conservative
  all-in proxy), 36 bps and 54 bps stress. This avoids crediting Kraken with better
  execution absent a local measurement.

## Advancement gates

External transfer passes only if expected-cost full-period return is positive, Sharpe
>0.5, profit factor >1, at least 5/7 alts have positive net expectancy, at least two
calendar years are positive, and return stays positive at 2x cost, after a one-bar
entry delay, and after removing the top 5% of trades. The 3x-cost and two-bar-delay
cases are diagnostics. A pass confirms exchange robustness but does not alter the
forward-paper promotion gate. A failure downgrades exchange robustness and is not a
license to tune on Kraken.

Data integrity requires monotonic unique candles, valid OHLC relationships, complete
4h spacing within each returned sequence, response-source provenance and SHA-256.
