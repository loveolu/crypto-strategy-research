# Strategy leaderboard — updated 2026-09-05 after CRYPTO-EXP-015

Composite per the goal (never raw return alone). **WF** = rolling walk-forward, 11 windows 2024-01→2026-09,
threshold re-fit per window. **Fixed OOS** = 2024-11→2026-09, threshold from TRAIN. A-011 measured
costs, taker, unleveraged, 9 OKX perps. All members of the top group are ONE mechanism (cascade
reversion in daily uptrends) at different settings — correlated, not three independent edges.

| # | strategy | status | tf | WF ann | WF Sh / So | WF DD | Calmar | 2024 / 2025 / 2026 | last 365d | fixed-OOS Sh | top-5% drop | 3× cost Sh | +win |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **B2: 4h cascade + BTC-drop condition** | **Paper Trading (COLLECTING)** | 4h | 13.9% | 1.23 / 3.54 | **−5.5%** | **2.55** | +37.3 / +1.9 / +0.5 | **+1.6%** | **1.42** | **+13.3%** | 1.17 | 6/11 |
| **2** | **S2-strict 4h** | Promising | 4h | 15.7% | 1.30 / 2.93 | −7.4% | 2.12 | +42.3 / +2.1 / +0.6 | −4.1% | 1.31 | +10.8% | 1.05 | 5/11 |
| **3** | **S2-strict 8h** | Promising | 8h | 14.7% | 1.70 / **4.72** | −8.3% | 1.76 | +39.3 / +1.7 / +0.9 | **+4.3%** | 0.85 | +4.9% | — | 5/11 |
| 4 | S2-strict 2h | Testing | 2h | 17.0% | 1.56 / 3.81 | −8.4% | 2.02 | +49.4 / +0.4 / +0.5 | −7.6% | 1.02 | +0.4% | — | 6/11 |
| 5 | S2-strict 1h | Testing | 1h | 21.3% | 2.06 / 3.68 | −12.2% | 1.75 | +62.1 / +2.2 / −0.1 | −11.2% | 0.83 | −4.1% | 0.61 (2×) | 6/11 |
| — | B3 vol-expansion 4h | Rejected | 4h | 8.3% | 1.13 / 2.07 | −7.2% | 1.16 | +25.4 / −1.4 / −0.3 | −1.3% | — | — | — | 2/11 |
| — | V5 beta-neutral spread | Rejected as hedge | 1h | −3.2% | −0.35 | −20% | — | −8.9 / +7.2 / −5.9 | −1.1% | — | — | — | — |
| — | S3 gated vol-target basket | Testing (daily, out of scope) | 1d | — | 0.79 | −30% | — | +48 / −19 / −4 | — | — | — | — | — |
| — | S1, MAR, RS, rebal-freq, S2 short, S5 base, EXP-008 gate | Rejected | | | | | | | | | | | |

**Reference:** A-005 equal-weight monthly basket over the WF span: 2024 +84%, 2025 −34%, 2026 −22%; DD −71%.

**Ranking rationale.** #1 B2 leads on every risk metric, is the only construct positive in the crash
window, passes concentration / cost / delay / timeframe / coin / parameter tests, and its improvement
over #2 is in the direction its mechanism predicts on walk-forward OOS — that is what Candidate means
here. #2 vs #3 is a genuine trade-off: 4h has the better fixed-split Sharpe (1.31 vs 0.85), more trades
and better concentration; 8h has the better Sortino, the best recent year and the least bear damage.
1h has the highest headline numbers and the worst drawdown, recent, concentration and TRAIN→OOS
transfer — the profile the goal says to distrust.

**Regime profile (all configs):** high-vol +29–40%/yr, bull +37–60%/yr; low-vol and bear ≈ −3% to
+5%. The gate keeps bear losses small; it cannot create returns there. **Returns are 2024.**

**Forward status:** B2 entered isolated Freqtrade dry-run paper trading on 2026-09-04 13:55 PDT,
executing at the 4h close. Paper Trading → live consideration requires rolling 90d PF > 1 for two
consecutive quarters on forward data; the initial monitor state is **COLLECTING** (zero trades).
