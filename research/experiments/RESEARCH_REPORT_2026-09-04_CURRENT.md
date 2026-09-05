# Current crypto research report — through CRYPTO-EXP-040

As of 2026-09-04 PDT. Expected-cost results are primary. The Claude table is a hybrid comparison,
not a single valid validation stream; fixed-rule, walk-forward, real-engine, exchange-transfer, and
forward-paper evidence are therefore shown separately.

## Best strategies

| Strategy | Status | Market / timeframe | Trades | Net return / annualized | Sharpe / Sortino | Max DD / PF | Recent 30d / 90d / 365d | OOS evidence | Robustness |
|---|---|---|---:|---:|---:|---:|---:|---|---:|
| **B2 cascade + BTC-drop** | **Paper Trading; statistically provisional** | 9 OKX perps / 4h | 368 fixed; 11 WF windows | WF +40.6% / 13.9% | 1.23 / 3.54 | **−5.5% / —** | historical +0.47% / +0.47% / +1.62%; forward 0/0/0 | True rolling WF; 6/11 windows positive | **8/10** |
| S2-strict cascade | Promising, not forward-promoted | 9 OKX perps / 4h | 170 fixed OOS | +27.5% / ≈15% fixed OOS | 1.31 / 2.93 | −10.4% / 1.87 | historical +0.55% / +0.55% / −4.05% | Positive at 1h/2h/4h/8h; no untouched family data remains | **7/10** |

The robustness score is a transparent gate count, not a fitted optimizer: positive OOS, cost stress,
parameter neighborhood, timeframe neighborhood, coin breadth, delay, top-trade removal, recent
profitability, exchange transfer, and statistical correction (one point each). B2 loses recent and
selection-deflated-significance points. S2's conservative score reflects no external transfer plus
its recent and execution-delay weaknesses.

Historical 30/90/365-day returns are recomputed directly from the stitched walk-forward return
series ending 2026-08-31 20:00 UTC (`research/measurements/A019_wf.pkl`), not inferred from calendar
year totals. Forward windows come from the isolated dry-run database.

### B2 evidence layers — do not combine these totals

- **True rolling walk-forward (leaderboard basis):** +40.6%, 13.9% annualized, Sharpe 1.23,
  Sortino 3.54, maximum drawdown −5.5%, six of eleven windows positive. Returns are concentrated in
  2024; three windows have zero trades.
- **Consistent fixed research harness:** +92.03%, daily maximum drawdown −9.99%. This is not WF.
- **Real Freqtrade engine:** exact 368/368 entry and exit timestamp parity. Fixed $500 stakes returned
  +59.08%, CAGR 13.71%, Sharpe 1.45, Sortino 2.07, PF 2.22, DD −5.95%. Replaying the engine trades at
  the research 1/9 capital model returned +88.35%, DD −10.49%.
- **Independent Kraken transfer:** 259 trades, +82.06% net, 18.06% annualized, Sharpe 1.35,
  Sortino 2.98, PF 2.09, DD −13.16%, 7/7 coins positive; 3× costs, delay, and top-5% removal survive.
- **Selection audit:** WF daily DSR is only .543 at 200 trials, below the .95 gate, although a
  10,000-draw block bootstrap gives P(Sharpe>0)=.975. Historical evidence is mixed and insufficient
  for live capital.
- **Forward paper:** runtime HEALTHY/COLLECTING; zero trades. Promotion requires ≥100 trades,
  PSR(Sharpe>0) ≥.95, and PF>1 in two consecutive 90-day windows with ≥15 trades each.

### Claude hurdle

B2's valid WF drawdown matches the supplied −5.5% hurdle but its +40.6% WF total does not beat
+61.7%. The consistent fixed rule beats +61.7% return but fails the −5.5% drawdown hurdle. Kraken
transfer beats the return hurdle but also fails drawdown. **No strategy clears both return and
drawdown honestly under one consistent evidence stream.**

## Recent experiments

| ID | Hypothesis | Result | Held-out |
|---|---|---|---|
| EXP-031 | Book imbalance predicts short-horizon returns | Data gate stopped: 360 snapshots span only 260 seconds | Not examined |
| EXP-032 | OI/positioning/taker-flow archive is research-ready | 27/27 clean series, but only 179/365 common days | Not examined |
| EXP-033 | Five-bar fractal breakout | 1,587 TRAIN trades; +5.81 gross bps vs 13.71 cost; −14.92% net | Sealed |
| EXP-034 | Morning/Evening Star continuation | 751 TRAIN; −0.36 gross bps; −11.20% net | Sealed |
| EXP-035 | Outside-close range expansion continues | 1,934 TRAIN; +6.18 gross bps vs 13.68 cost; −16.09% net | Sealed |
| EXP-036 | Triple-smoothed TRIX direction persists | +110.91% TRAIN and 9/9 positive, but shared-shift placebo p=.107 failed | Sealed |
| EXP-037 | Volatility-scaled next-bar dynamic breakout | 3,319 TRAIN; +18.80 gross bps, but short gross −7.12 bps and DD −45.48% | Sealed |
| EXP-038 | Awesome Oscillator saucer continuation | +43.19% TRAIN, 8/9 positive and both sides profitable; placebo p=.029 >.025 | Sealed |
| EXP-039 | Quarter-hour signed-order-flow effect | Data gate stopped: 28 complete days and no sub-minute aggressor-side tape | Not examined |
| EXP-040 | BTC turn-of-the-candle boundary minute | Published +0.58 bps edge is 23.6× below measured cost; only 28 local days | Not examined |

## Failed and uncertain findings

- EXP-024 volume continuation was raw-OOS positive (+24.18%, Sharpe 1.26) but becomes negative after
  removing the best 5% of trades; rejected for concentration.
- EXP-027 Extreme-Fear relief had strong TRAIN economics but only 38 trades; its earlier BTC transfer
  (EXP-029) failed the circular-date placebo. Sentiment timing is closed.
- EXP-026 cross-venue convergence and EXP-028/030 one-minute shock rules have gross edges below cost.
- EXP-033 through 035 show a repeated structural result: recognizable 4h candle patterns may have
  small gross continuation, but not enough to clear 13–14 bps round-trip friction with coin breadth.
- EXP-036 shows why economic gates alone are insufficient: a broad, profitable TRAIN result can
  still be ordinary under an autocorrelation-preserving null. Its attractive long side is not a
  post-hoc license to discard the losing short side or open held-out data.
- EXP-037 found 24h continuation after upside volatility-scaled breaks but not downside symmetry.
  The frozen combined rule is rejected; the observed split is not permission to select long-only.
- EXP-038 was economically broad but missed its multiplicity-aware timing gate by four placebo
  exceedances per thousand (p=.029 vs ≤.025). Treat it as rejected, not as rounded significance.
- EXP-039 identifies a genuinely distinct recent mechanism, but the available one-minute OHLCV
  archive cannot represent its first-10-second signed-order-flow signal. No proxy test was run.
- EXP-040 shows that a statistically documented anomaly can still be unusable: the paper's economics
  depend on a zero-fee tier, while its gross mean is far below this project's executable friction.

## New market insights

1. B2 remains the only replicated mechanism, but its evidence is 2024-heavy and statistically
   provisional after selection correction.
2. Exchange transfer supports liquidation/reversion as a mechanism, not OKX-specific data mining;
   it does not solve synchronized drawdown or recent decay.
3. Ordinary pattern continuation is economically weak: ample samples in EXP-033/035 show gross
   effects below half the required cost, while EXP-034 is gross-negative.
4. Volatility-scaled expansion is directionally asymmetric on TRAIN: EXP-037's upside breaks carried
   continuation, but downside breaks did not. This is diagnostic only because direction was frozen.
5. AO saucer resumption is the strongest independent TRAIN mechanism after the cascade family, but
   its timing evidence did not clear the frozen placebo gate and therefore supplies no OOS claim.
6. New-data lanes are cleanly gated: daily market structure needs 186 more common days; true book
   imbalance needs genuine multi-day capture; the quarter-hour effect needs authenticated trade tape.
7. Boundary-minute seasonality is not a taker strategy at current costs: published gross expectancy
   is 0.58 bps against approximately 13.7 bps measured round-trip friction.
8. A prior hourly futures-to-mark census found 1.13–3.43 bps feature dispersion, but that alone does
   not bound the future return it might predict. EXP-041 addresses the previously missing causal test.

## Prioritized next work

1. Continue B2 paper monitoring without changing the frozen strategy.
2. Continue immutable OI/positioning/taker-flow collection; rerun the timestamp-only 365-day gate.
3. Activate one-minute forward capture only from a queryable host process; require 365 common days.
4. Seek an independent mechanism with a pre-registered gross edge plausibly larger than costs;
   avoid further cascade variants and already-closed univariate OHLCV scans.
5. Reassess funding/OI features only after the minimum history gate, not on the current six months.

Detailed records: `EXPERIMENT_LOG.md`, `LEADERBOARD.md`, `RESEARCH_QUEUE.md`, and each experiment's
machine-readable `research/measurements/.../summary.json`.

---

## Addendum — CRYPTO-EXP-041 → 044 (second session, 2026-09-05; axes other than the entry filter)

These four ran concurrently with EXP-016 → 040 in a separate session and were initially mis-numbered
016 → 019; renumbered here. Same harness (`s2_cascade.py`, `wf_cascade.py`), same walk-forward.

| experiment | result | verdict |
|---|---|---|
| **043 exit research on B2** | target exit (50% of the drop): WF Sh 1.23 → **1.61**, So 3.54 → 3.80, DD −5.5 → **−4.3%**, Cal 2.55 → **3.00**, 2025 +1.9 → **+3.8%**; fixed OOS +27.6% Sh 1.61 PF 2.14 WR 70% hold 18h; 3× cost Sh 1.25; **delay 1 / 2 bars Sh 1.81 / 0.96** (fixed exit: 0.97 / 0.18); stops at entry-bar low: Sh 0.99 | **SURVIVES — Candidate variant (1b).** Not the live rule; next forward variant. Not yet selection-deflated. |
| 041 squeeze-fade short (4h, strict, BTC-up, gate OFF) | WF Sh −0.08; **2024 −18.0%, 2025 +17.2%, 2026 +1.3%**; 4/11 windows | killed by rule; the mechanism is real in true bears and the gate admits pullbacks → queued with a stricter bear gate |
| 042 BTC-bounce timing (wait one bar, BTC green) | Sh 0.74 vs 0.85 plain-delay reference | killed; **reproduces EXP-016's rejection** — BTC is a filter, not a timing signal |
| 044 hardest-hit concentration in wide cascades | wide bars 603 bps/trade WR 87% vs 149 all-B2; 3 bars / 15 trades | n too small; **reproduces EXP-022** — breadth is a mechanism insight, not an allocation |

**Reading against the consolidated evidence above.** The target exit is the only backtest improvement
in either session that raised every risk metric at once and relaxed the execution-timing constraint;
it does not change the EXP-025 conclusion (DSR .543) and does not make anything live-eligible. The
squeeze short is the first construct in the program to earn in the 2025 bear on walk-forward, and the
first that could give the book a second regime — if a bear gate that excludes bull pullbacks exists.

