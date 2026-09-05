# Strategy leaderboard — updated 2026-09-05 through CRYPTO-EXP-044

Current consolidated report: `RESEARCH_REPORT_2026-09-04_CURRENT.md`.

Composite per the goal (never raw return alone). **WF** = rolling walk-forward, 11 windows 2024-01→2026-09,
threshold re-fit per window. **Fixed OOS** = 2024-11→2026-09, threshold from TRAIN. A-011 measured
costs, taker, unleveraged, 9 OKX perps. All members of the top group are ONE mechanism (cascade
reversion in daily uptrends) at different settings — correlated, not three independent edges.

| # | strategy | status | tf | WF ann | WF Sh / So | WF DD | Calmar | 2024 / 2025 / 2026 | last 365d | fixed-OOS Sh | top-5% drop | 3× cost Sh | +win |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **B2: 4h cascade + BTC-drop condition** | **Paper Trading (statistically provisional)** | 4h | 13.9% | 1.23 / 3.54 | **−5.5%** | **2.55** | +37.3 / +1.9 / +0.5 | **+1.6%** | **1.42** | **+13.3%** | 1.17 | 6/11 |
| **1b** | **B2 + target exit** (same entry; exit at 50% of the entry drop or 24h) — CRYPTO-EXP-043 | **Candidate (backtest); not the live rule** | 4h | 12.8% | **1.61 / 3.80** | **−4.3%** | **3.00** | +30.7 / **+3.8** / +1.0 | +1.8% | **1.61** | +12.6% | **1.25** | 6/11 |
| **2** | **S2-strict 4h** | Promising | 4h | 15.7% | 1.30 / 2.93 | −7.4% | 2.12 | +42.3 / +2.1 / +0.6 | −4.1% | 1.31 | +10.8% | 1.05 | 5/11 |
| **3** | **S2-strict 8h** | Promising | 8h | 14.7% | 1.70 / **4.72** | −8.3% | 1.76 | +39.3 / +1.7 / +0.9 | **+4.3%** | 0.85 | +4.9% | — | 5/11 |
| 4 | S2-strict 2h | Testing | 2h | 17.0% | 1.56 / 3.81 | −8.4% | 2.02 | +49.4 / +0.4 / +0.5 | −7.6% | 1.02 | +0.4% | — | 6/11 |
| 5 | S2-strict 1h | Testing | 1h | 21.3% | 2.06 / 3.68 | −12.2% | 1.75 | +62.1 / +2.2 / −0.1 | −11.2% | 0.83 | −4.1% | 0.61 (2×) | 6/11 |
| — | B3 vol-expansion 4h | Rejected | 4h | 8.3% | 1.13 / 2.07 | −7.2% | 1.16 | +25.4 / −1.4 / −0.3 | −1.3% | — | — | — | 2/11 |
| — | V5 beta-neutral spread | Rejected as hedge | 1h | −3.2% | −0.35 | −20% | — | −8.9 / +7.2 / −5.9 | −1.1% | — | — | — | — |
| — | BTC shock/rebound → lagging-alt catch-up | Rejected | 4h | −6.9% OOS | −1.10 / −1.38 | −13.3% | −0.52 | OOS segments all negative | −5.6% | −1.10 | −20.2% | −1.67 | 0/3 |
| — | S3 gated vol-target basket | Testing (daily, out of scope) | 1d | — | 0.79 | −30% | — | +48 / −19 / −4 | — | — | — | — | — |
| — | S1, MAR, RS, rebal-freq, S2 short, S5 base, EXP-008 gate | Rejected | | | | | | | | | | | |

**Reference:** A-005 equal-weight monthly basket over the WF span: 2024 +84%, 2025 −34%, 2026 −22%; DD −71%.

**Ranking rationale.** #1 B2 leads on every risk metric, is the only construct positive in the crash
window, passes concentration / cost / delay / timeframe / coin / parameter tests, and its improvement
over #2 is in the direction its mechanism predicts on walk-forward OOS. EXP-025 subsequently made
that evidence statistically provisional rather than Candidate-grade. #2 vs #3 is a genuine trade-off:
4h has the better fixed-split Sharpe (1.31 vs 0.85), more trades
and better concentration; 8h has the better Sortino, the best recent year and the least bear damage.
1h has the highest headline numbers and the worst drawdown, recent, concentration and TRAIN→OOS
transfer — the profile the goal says to distrust.

**Regime profile (all configs):** high-vol +29–40%/yr, bull +37–60%/yr; low-vol and bear ≈ −3% to
+5%. The gate keeps bear losses small; it cannot create returns there. **Returns are 2024.**

**Forward status:** B2 entered isolated Freqtrade dry-run paper trading on 2026-09-04 13:55 PDT,
executing at the 4h close. The basic forward gate remains rolling 90d PF > 1 for two consecutive
quarters, but EXP-025's failed DSR gate also requires independent forward statistical confirmation
before any live consideration; the initial monitor state is **COLLECTING** (zero trades).

**Forward-port audit correction:** An end-to-end all-nine-coin parity audit found that the
initial Freqtrade port exposed the daily gate four hours earlier than the frozen harness and used
the current 4h close instead of completed daily close against SMA200. It also translated frozen
`HOLD6` into 24 hours, although next-open ledger execution makes the faithful maximum open-to-open
time stop 28 hours. It also allowed a re-entry signal formed during the exit candle, which the
frozen harness skips, and placed the 9 bps fee override where Freqtrade ignored it. All five code
defects are fixed. A real protected Freqtrade engine run confirms exact 368/368 entry and exit
timestamps across all nine coins and explicitly loads 9 bps/side. The benchmark metrics already used the
original frozen ledger and therefore do not change.
PID 37452 has now loaded the corrected strategy and both config files; a fresh heartbeat and an
independent OS process census establish authoritative runtime status **HEALTHY / COLLECTING**.
There are zero trades, so no forward observation was contaminated and rankings are unchanged.

**Independent-mechanism update:** CRYPTO-EXP-016's BTC-rebound/lagging-alt rule passed its TRAIN-only
existence screen but reversed sign gross OOS (−5.6%; −11.9% after measured costs), with every held-out
segment negative. It is rejected and does not diversify the cascade family.

**Exchange-transfer update:** The exact B2 signal transferred without refitting to seven Kraken alt
perpetuals (259 trades, +82.1% after an 18 bps round trip, Sharpe 1.35, PF 2.09, all seven coins
positive). It survived 3× costs, two-bar delay and top-5% removal, materially strengthening the
mechanism claim. Kraken drawdown was −13.2% and last-365d return −9.8%, so it does not beat the
user/Claude +61.7% / −5.5% benchmark on the joint return-risk hurdle.

**Cross-exchange-filter update:** CRYPTO-EXP-018 required exact same-bar Kraken confirmation before
trading OKX. It was rejected on TRAIN alone: +36.9% versus +53.0% base, Sharpe 1.45 versus 1.83 and
drawdown −5.64% versus −5.79%. The 107-trade sample had full coin breadth, but the filter discarded
too much return without materially reducing risk. Held-out data was not examined; rankings are unchanged.

**Venue-portfolio update:** A fixed 50/50 OKX/Kraken B2 blend returned +93.8% with Sharpe 1.48,
but maximum drawdown remained −13.15%. Daily return correlation was .970 and 25/75 through 75/25
venue weights had effectively identical drawdown. It clears Claude's return number but fails the
joint −5.5% drawdown hurdle, is retrospective rather than untouched OOS, and does not change rankings.

**Independent-portfolio update:** Frozen B2 and BTC/ETH TrendVolTarget returns were nearly
uncorrelated (.053 daily), but the static 50/50 portfolio still drew down −11.51% (+93.86%, Sharpe
1.47). A 75% B2 sensitivity improved Sharpe to 1.75 but DD remained −10.23%; selecting it after
inspection would be weight optimization. The Claude joint hurdle fails and rankings remain unchanged.

**Sizing update:** CRYPTO-EXP-021 applied causal inverse-volatility weights without changing B2
signals. On TRAIN it reduced drawdown from −5.25% to −4.65% and worst-coin absolute-P&L share from
17.87% to 15.87%, but return fell from +46.86% to +38.15% and Sharpe from 1.82 to 1.73. It failed
the frozen risk gates, held-out remained sealed, and the equal-sleeve leaderboard is unchanged.

**Concurrency update:** TRAIN expectancy rose from 64 bps for singleton signals to 140 bps for
pairs and 365 bps for 3+ coin events. CRYPTO-EXP-022 concentrated 100% capital in those broad events:
return rose to +62.28% and PF 3.89, but DD worsened from −5.25% to −12.40% and Sharpe fell from 1.82
to 1.47. Best-event removal stayed profitable; the mechanism insight is real, but the portfolio fails.
Held-out remained sealed and rankings are unchanged.

**Independent-signal update:** CRYPTO-EXP-023's high-volume 4h hammer earned +42.1 net bps/trade
on TRAIN, but produced only 82 trades, five positive coins and as few as three trades on BTC. The
pooled +3.78%, Sharpe 0.56 result failed prerequisite breadth/sample gates; placebo and held-out were
not opened. It is rejected and does not enter the leaderboard.

**Volume-continuation update:** CRYPTO-EXP-024 passed all TRAIN gates including a 999-shift placebo
(p=.008), then returned +24.18% OOS with Sharpe 1.26, PF 1.54, seven positive coins, 2×-cost and
delay robustness. It is still rejected: removing the best 5% of trades yields −1.95%, Sharpe −.12
and only three positive coins; TEST was −2.17% and FWD had just 21 trades. No ranking change.

**Selection-bias update:** CRYPTO-EXP-025 found that fixed-rule per-trade DSR passes (.991 at 200
trials), but the preferred stitched walk-forward daily DSR is only .543 (.351 at 1,000 trials) because
returns are extremely skewed and fat-tailed. A 10,000-draw 30d block bootstrap gives P(Sh>0)=.975,
so evidence is mixed rather than disproven. B2 stays #1 and in Paper Trading, but is statistically
provisional and not live-eligible on historical evidence alone.

**Cross-venue price-discovery update:** CRYPTO-EXP-026 found small gross convergence in both directions
(long +8.45, short +4.12 bps/trade), but measured round-trip cost was 14.23 bps. Across 1,074 TRAIN
trades the strategy lost −12.13%, Sharpe −.77, PF .88, with only 2/7 positive coins. Held-out remained
sealed; the rule is rejected and does not enter the leaderboard.

**Sentiment-confirmation update:** CRYPTO-EXP-027 conservatively delayed each Fear & Greed reading by
one UTC day and bought the first green 4h candle after a negative 24h return during Extreme Fear.
TRAIN economics were strong (+112.45 net bps/trade, PF 5.84, 9/9 positive coins), but there were only
38 trades and 3–5 per coin. It failed both frozen sample gates; placebo and heldout remained sealed.
The result is uncertain rather than leaderboard-eligible.

**One-minute microstructure update:** CRYPTO-EXP-028 tested whether extreme high-volume one-minute
price shocks overshoot and reverse over five minutes. Across 988 TRAIN trades the fade lost −1.46
gross bps/trade before a measured 13.62 bps round trip, producing −15.26% net, −15.28% drawdown,
PF .12 and 0/9 positive coins. Its sample was ample; the mechanism was absent. Placebo and held-out
segments were not opened, and the leaderboard is unchanged.

**Sentiment regime-transfer update:** CRYPTO-EXP-029 applied EXP-027's exact rule to an earlier
BTC/USDT spot regime. The larger 145-trade discovery sample earned +28.62 gross bps versus 22 bps
friction, but only +6.58 net bps, Sharpe .25 and −25.10% DD. A 999-shift daily-sentiment placebo
gave p=.250, and 2022 lost −10.80%. The discovery gate failed, later overlapping history remained
sealed, and the sentiment-relief family is now closed without a ranking change.

**One-minute BTC-lead update:** CRYPTO-EXP-030 measured +0.72 gross bps/leg of same-direction alt
follow-through after extreme high-volume BTC shocks (+1.26 after up-shocks, +0.11 after down-shocks).
That weak price-discovery relationship is about 20× smaller than the measured 14.13 bps round trip.
Across 121 events / 968 legs it produced −15.00% net, PF .15 and 0/8 positive coins. Later segments
remained sealed; the relationship is informative but untradeable and does not change rankings.

**Order-book readiness update:** CRYPTO-EXP-031 found only 360 authentic snapshots (40 per coin)
covering 260 seconds. The 30-day/1,000-snapshot-per-coin gate failed before any return rule was
defined. No trial or ranking change.

**Market-structure readiness update:** CRYPTO-EXP-032 verified all 27 OI, account-ratio, and taker-flow
series are daily, aligned, gap-free, and duplicate-free, but only 179 of the required 365 common days
exist. No feature values or future returns were inspected; collection continues without a trial.

**Fractal-breakout update:** CRYPTO-EXP-033 generated 1,587 TRAIN trades but only +5.81 gross bps per
trade against 13.71 bps friction, −14.92% net, and 3/9 positive coins. Held-out stayed sealed and the
rule is rejected without a ranking change.

**Star-pattern update:** CRYPTO-EXP-034 generated 751 TRAIN trades with −0.36 gross bps expectancy,
−11.20% net, and 3/9 positive coins. Held-out stayed sealed and the rule is rejected.

**Outside-close update:** CRYPTO-EXP-035 generated 1,934 TRAIN trades with +6.18 gross bps against
13.68 bps friction, −16.09% net, and 2/9 positive coins. Held-out stayed sealed and the rule is
rejected.

**TRIX update:** CRYPTO-EXP-036 was economically strong on TRAIN (+110.91% net, 2,108 trades, 9/9
positive), but the preregistered 999-draw shared-shift placebo failed at p=.107 versus ≤.025. Held-out
stayed sealed; the apparent edge is not eligible for ranking.

**Dynamic-breakout update:** CRYPTO-EXP-037 produced 3,319 TRAIN trades and +18.80 gross bps against
13.70 bps friction, but shorts were gross-negative and drawdown reached −45.48%. The frozen side gate
failed, placebo was not run, and held-out stayed sealed.

**Awesome-Oscillator update:** CRYPTO-EXP-038 produced broad TRAIN economics (+43.19% net, 1,796
trades, 8/9 positive, both directions profitable), but narrowly failed the frozen shared-shift gate
at p=.029 versus ≤.025. The threshold was not rounded or retried, held-out stayed sealed, and the
strategy is rejected without entering the leaderboard.

**Quarter-hour research update:** CRYPTO-EXP-039 screened the July 2026 signed-order-flow result from
Kim and Hansen before defining a strategy. The local archive has only 28 complete common days and
one-minute OHLCV rather than first-10-second aggressor-side trade events. It stopped with zero return
inspection and zero trial; rankings are unchanged.

**Boundary-minute economics update:** CRYPTO-EXP-040 screened the published Bitcoin
turn-of-the-candle anomaly before local return inspection. Its +0.58 bps gross mean is 23.6× below
measured project taker friction, the paper's favorable economics require a zero-fee volume tier, and
only 28 complete local days exist. Zero trial was spent and rankings are unchanged.

**Addendum 2026-09-05 (this session, CRYPTO-EXP-041..044).** Exit research on B2: a profit target at
half the entry drop beats the fixed 24h exit on walk-forward Sharpe (1.23 → 1.61), Sortino, drawdown
(−5.5 → −4.3%), Calmar (2.55 → 3.00), PF, win rate (63 → 70%) and both hard years, for ~10% less total
return; **delay tolerance improves from Sh 0.18 → 0.96 at two bars late** (fixed OOS). Stops at the
entry-bar low hurt (Sh 0.99). Listed as **1b** because the running paper trade is frozen at HOLD6 and
must not be altered mid-record; the target exit is the pre-registered next forward variant. It has
NOT been through the EXP-025 selection-deflation audit; treat its DSR as ≤ B2's .543.
Squeeze-fade short in downtrends (EXP-041) was killed by its rule (WF Sh −0.08) but earned **+17.2% in
2025** and lost −18% in 2024 pullbacks — the daily gate cannot tell a bear from a pullback; queued with
a stricter bear gate. EXP-042 (BTC-bounce timing) and EXP-044 (hardest-hit concentration) independently
reproduce the parallel session's EXP-016 and EXP-022 rejections.
