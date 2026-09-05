# CRYPTO-EXP-023 — high-volume hammer absorption

**Verdict: REJECTED on TRAIN before placebo; held-out remained sealed.**

The independent 4h signal required trailing-180-bar volume rank ≥.95, a lower
wick at least half the candle range, a green close, and BTC above its completed
daily SMA200. Entries used the next open, exits the open 12 hours later, and
measured instrument-level OKX taker costs.

TRAIN produced 82 trades, +56.12 gross bps/trade and +42.12 net bps/trade against
13.92 bps expected round-trip friction. Portfolio return was +3.78%, Sharpe 0.56,
PF 1.37 and maximum drawdown −3.55%.

The rule failed its sample and breadth gates: fewer than 100 trades, only five of
nine coins had positive net expectancy, and BTC had only three trades. Coin net
expectancy ranged from −164 bps (LINK) to +241 bps (ETH), which is too unstable
to treat the pooled positive average as transferable.

Because prerequisite gates failed, the 999-draw circular-shift placebo was not
run and held-out data was not opened. No volume percentile, wick fraction, trend
gate or holding-period alternative will be tried on this dataset.
