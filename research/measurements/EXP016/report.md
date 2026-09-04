# CRYPTO-EXP-016 — BTC reversal leads lagging alts

**Final status: REJECTED_HELD_OUT.** The TRAIN pre-gate passed and the held-out data
was opened once under the frozen advancement rule.

## TRAIN pre-gate

- Trades: 386; gross expectancy 17.04 bps
- Expected round-trip cost: 14.34 bps
- Breadth: 6/8; circular-shift p=0.019

## Expected-cost chronological results

| Segment | Trades | Return | Annualized | Sharpe | PF | Net expectancy bps |
|---|---:|---:|---:|---:|---:|---:|
| TRAIN | 386 | +1.08% | +0.58% | 0.14 | 1.06 | 2.70 |
| VAL | 129 | -5.81% | -13.57% | -1.36 | 0.64 | -35.77 |
| TEST | 52 | -0.74% | -1.78% | -0.85 | 0.71 | -11.30 |
| FWD | 203 | -5.77% | -6.08% | -1.18 | 0.64 | -22.91 |
| OOS | 384 | -11.90% | -6.90% | -1.10 | 0.64 | -25.66 |

## Frozen advancement gates

- FAIL — oos_return_positive
- FAIL — oos_sharpe_above_0_5
- FAIL — oos_profit_factor_above_1
- FAIL — two_of_three_segments_positive
- FAIL — five_of_eight_alts_positive
- FAIL — two_x_cost_positive
- FAIL — one_bar_delay_positive
- FAIL — top_five_pct_removed_positive

## Stress diagnostics

Cost scenarios (0x is gross; 1x measured expected):

- 0.0x: return -5.63%, Sharpe -0.49, expectancy -11.35 bps
- 1.0x: return -11.90%, Sharpe -1.10, expectancy -25.66 bps
- 2.0x: return -17.77%, Sharpe -1.67, expectancy -39.97 bps
- 3.0x: return -23.25%, Sharpe -2.20, expectancy -54.29 bps

Entry delay at expected costs:

- +1 bar: return -10.69%, Sharpe -0.91
- +2 bar: return -3.02%, Sharpe -0.29

Top 5% of OOS trades removed: return
-20.22%, Sharpe
-2.35. Positive OOS coin breadth:
1/8. Positive VAL/TEST/FWD segments:
0/3.

Recent expected-cost windows:

- 30d: 2 trades, return +0.34%, expectancy 135.38 bps
- 90d: 28 trades, return -3.75%, expectancy -108.24 bps
- 180d: 72 trades, return -5.61%, expectancy -63.60 bps
- 365d: 212 trades, return -5.61%, expectancy -21.29 bps

BTC trend regimes (using only the prior completed daily close/SMA200):

- btc_above_sma200: 185 trades, expectancy -35.05 bps, win rate 40.0%
- btc_below_sma200: 199 trades, expectancy -16.93 bps, win rate 38.2%

The machine-readable summary additionally records monthly returns, drawdown, Sortino,
Calmar, winner/loser distributions, fees/slippage, turnover, exposure, streaks,
recovery time and worst day/week/month for every chronological segment.

## Conclusion

The verdict follows the preregistered gates, not headline return. This mechanism is
tracked separately from B2 and no reverse direction, parameter variant, or alternate
holding period was selected after seeing held-out results.
