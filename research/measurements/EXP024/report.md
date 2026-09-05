# CRYPTO-EXP-024 — volume-led close-strength continuation

**Verdict: REJECTED on held-out concentration robustness.** This independent
4h demand-continuation hypothesis passed every TRAIN pre-gate, then remained
profitable OOS—but all economic profit depended on the best 5% of trades.

## Chronological evidence

| Period | Trades | Net return | Sharpe | PF | Max DD |
|---|---:|---:|---:|---:|---:|
| TRAIN, 2023-01-22→2024-11-22 | 491 | +13.91% | 0.80 | 1.22 | −8.10% |
| Held-out, 2024-11-23→2026-09-01 | 351 | **+24.18%** | **1.26** | **1.54** | −6.54% |

TRAIN gross expectancy was 39.19 bps against 13.78 bps expected round-trip
cost, seven of nine coins were positive, and the circular-shift test placed the
observed mean above 99.30% of 999 placebos (one-sided p=.008).

Held-out expectancy was +57.81 net bps/trade with seven positive coins. The
rule survived 2× cost (+17.82%, Sharpe .98) and a one-bar delay (+18.73%,
Sharpe .97). VAL returned +25.94%; TEST returned −2.17%; FWD returned +0.78%
on only 21 trades.

## Disqualifying failure

Removing the top 5% of held-out trades produced **−1.95%, Sharpe −0.12 and
PF .96**, with only three positive coins. The strong pooled result is therefore
tail-dependent rather than a stable frequent-trading edge. No threshold, exit,
asset subset or top-trade characteristic will be optimized after inspection.
Kraken transfer and the full Claude hurdle were not tested because the frozen
held-out robustness sequence had already failed.
