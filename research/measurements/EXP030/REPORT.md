# CRYPTO-EXP-030 — one-minute BTC price-discovery lead

Status: **Rejected at the frozen TRAIN economic gate. Validation and TEST were not examined.**

## Hypothesis and execution

Extreme, high-volume BTC one-minute returns may carry information into liquid alts
with a short delay. The test followed the BTC direction in eight alt perpetuals at
the next minute open and exited five minutes later. Thresholds used only the prior
1,440 completed BTC bars. Each leg paid its measured $5k taker fee, half-spread and
book-walk cost; the mean round trip was 14.13 bps.

## TRAIN result (2026-08-04 through 2026-08-18)

| Basket events | Legs | Gross expectancy | Net expectancy | Gross return | Net return | Max DD | Positive coins |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 121 | 968 | **+0.72 bps** | -13.42 bps | +0.86% | -15.00% | -15.12% | 0/8 |

The directional mechanism exists weakly on both sides: +1.26 gross bps following
up-shocks and +0.11 gross bps following down-shocks. It is not remotely harvestable.
Measured friction is about 20 times the average gross edge, producing PF .15, only
17.4% winning legs, and 17.10% of sleeve capital paid in modeled friction over 15
days. Every alt was net-negative.

## Gate discipline and conclusion

Event and per-coin sample gates passed, as did the sign requirements. Gross
expectancy failed to exceed cost and coin breadth was 0/8. The placebo was therefore
skipped; validation (2026-08-19–25) and TEST (2026-08-26–09-01) remain sealed.

BTC does appear to lead alts by a tiny amount at one-minute resolution, but the
relationship is information, not a tradeable strategy under realistic execution.
Do not mine horizons, thresholds, directions or coin subsets. A future revisit
requires materially cheaper execution plus true order-flow history and at least one
year of forward data.
