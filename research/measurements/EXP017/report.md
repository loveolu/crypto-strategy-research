# CRYPTO-EXP-017 — B2 transfer to Kraken Futures

**Verdict: EXCHANGE_TRANSFER_CONFIRMED.** Exact frozen B2 signal and exits on the
pre-registered common-alt universe; no Kraken refit.

Kraken common universe: ETH, SOL, XRP, ADA, AVAX, DOT, LINK. Period: 2023-01-22T00:00:00+00:00..2026-09-01T00:00:00+00:00.
Expected cost is 18 bps round trip, retained from the conservative Candidate proxy.

| Cost | Total return | Annualized | Sharpe | Max DD | Net expectancy bps |
|---|---:|---:|---:|---:|---:|
| 0.0x | +94.49% | +20.24% | 1.48 | -12.82% | 187.74 |
| 1.0x | +82.06% | +18.06% | 1.35 | -13.16% | 169.74 |
| 2.0x | +70.41% | +15.92% | 1.22 | -13.50% | 151.74 |
| 3.0x | +59.51% | +13.81% | 1.09 | -13.84% | 133.74 |

Expected-cost calendar returns: 2023 +8.34%, 2024 +59.48%, 2025 +4.73%, 2026 +0.62%. Trades: 259; PF
2.09; Sortino 2.98; average hold
27.8 hours.

## Frozen gates

- PASS — expected_return_positive
- PASS — sharpe_above_0_5
- PASS — profit_factor_above_1
- PASS — five_of_seven_coins_positive
- PASS — two_calendar_years_positive
- PASS — two_x_cost_positive
- PASS — one_bar_delay_positive
- PASS — top_five_pct_removed_positive

## Breadth and stress

- ADA: 39 trades, +315.41 bps/trade
- AVAX: 31 trades, +153.36 bps/trade
- DOT: 24 trades, +222.88 bps/trade
- ETH: 27 trades, +123.65 bps/trade
- LINK: 47 trades, +96.12 bps/trade
- SOL: 52 trades, +124.68 bps/trade
- XRP: 39 trades, +185.10 bps/trade

- One-bar delay: +50.50%, Sharpe 1.20
- Two-bar delay: +18.45%, Sharpe 0.57
- Top 5% removed: +34.63%, Sharpe 0.97

The machine-readable artifact includes monthly/recent returns, costs, exposure,
turnover, drawdown, streak and recovery diagnostics. This experiment evaluates
exchange transfer; it is not a new challenger to the +61.7% / −5.5% OKX B2
benchmark and does not alter the live-promotion gate.
