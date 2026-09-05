# Research queue — ranked by Potential Edge × Credibility × Information Gain ÷ Complexity (2026-09-05, post EXP-044)

**Standing rule: no further variants of the cascade family on 2023→2026 data.** ≈ 50 constructs examined.

1. **Monitor the live B2 forward-paper stream** (launched 2026-09-04 13:55 PDT; isolated dry-run DB,
   log and keepalive verified). Compare theoretical vs simulated fill, slippage, latency and forward
   expectancy with the frozen backtest (+149 bps/trade, WR 63%). Authoritative status is now
   **HEALTHY / COLLECTING**: PID 37452 was created after the strategy and both config files,
   emits fresh heartbeats, and is the only actual B2 trade process.
   Review gate: rolling 90d PF > 1 for two consecutive quarters; **Degraded** if PF < 1 twice running.
   EXP-025 additionally failed selection-deflated WF significance (DSR .543 at N=200), so the strategy
   is not live-eligible on historical evidence even if the basic PF gate later passes.
2. **Monitor OI / long-short / taker-volume collection** (launched 2026-09-04; 27/27 OKX Rubik
   series, 179 finalized daily rows each, scheduled daily at 03:30). Do not inspect feature efficacy
   until at least 12 months are retained; the current ~6 months cannot support a multi-regime test.
   CRYPTO-EXP-032 made this a timestamp-only executable gate: 179/365 common days, with zero gaps,
   duplicates, or non-daily intervals. Rerun `market_structure_readiness.py`; do not substitute a
   forecast date for the observed common-day count.
3. **Activate the one-minute forward recorder in host context.** The append-safe, finalized-day
   collector and wrapper are implemented and tested, but the managed process blocks outbound sockets
   and cannot register its Task Scheduler entry. Current authoritative state: **NOT REGISTERED**, zero
   complete forward partitions. Do not use this lane for promotion until ≥365 common days exist.
4. **Funding as gate feature** — revisit at 12 months held (currently 6; the n=10 look was suggestive).
5. **B2 + target exit as the NEXT forward variant** (CRYPTO-EXP-043). Do not touch the live frozen
   rule. When the current forward window reaches its first 90-day review, register a second dry-run
   instance with `exit_mode="target"` (exit when price recovers 50% of the entry drop, else HOLD6) and
   run both side by side. Backtest: WF Sh 1.61 / Cal 3.00 / DD −4.3%; two-bar-late Sh 0.96.
6. **Bear-leg short with a STRICTER bear gate** (from CRYPTO-EXP-041). The squeeze-fade short earned
   +17.2% in 2025 and lost −18.0% in 2024 pullbacks: real in true bears, and the SMA200/EMA gate cannot
   separate a bear from a pullback. ONE pre-registered gate: price < SMA200 AND SMA200 falling (the
   mirror of EXP-008). Kill: WF Sh ≤ 0 or 2024 loss > 2025 gain. If it survives, the book has a second
   regime for the first time. Uses seen data — count it, and treat any pass as needing forward proof.
7. **Second, uncorrelated mechanism.** The non-cascade constructs tested (V5 spread, vol-expansion,
   S3 daily, and BTC-rebound/lagging-alt catch-up) are negative, bull-beta, or out of scope. The book
   remains one edge. Require a genuinely new hypothesis; intraday seasonality and simple OHLCV
   lead/lag are CLOSED, while funding / OI need forward data.
6. **Beat the explicit Claude hurdle honestly.** A challenger must exceed the displayed B2 #1
   (+61.7% total, −5.5% DD) after costs and survive equivalent OOS/recent/concentration/delay tests.
   Also compare against consistent fixed-rule B2 (+92.0%, −10.4% DD) and true WF B2 separately;
   do not compound the supplied hybrid 2023 in-sample + 2024–26 WF columns as one validation stream.

Closed, do not re-queue without new reason: V5 as hedge; vol-expansion ignition; majors/alts rotation;
regime-switch; rebalance-freq; S2 short mirror; S2 gate-timing variants; S1 ungated; T-038/039/040 families;
EXP-016 BTC-shock/rebound lagging-alt catch-up (TRAIN-positive, gross-negative in every held-out segment);
EXP-018 exact same-bar Kraken confirmation (failed TRAIN return, Sharpe, drawdown and expectancy gates;
heldout remained sealed); EXP-019 cross-venue B2 blending (OKX/Kraken daily correlation .970 and DD
≈−13.15% at every 25–75% venue weight). Do not tune timestamp tolerance, confirmation thresholds,
coin subsets or venue weights. EXP-020 static B2/TrendVolTarget blending confirmed low correlation
(.053) but failed risk gates (50/50 DD −11.51%; 75% B2 DD −10.23%). Do not select the latter post hoc.
EXP-021 inverse-vol B2 sizing failed TRAIN Sharpe/DD gates with heldout sealed; do not tune its 42-bar
window, normalization or clipping bounds. EXP-022 confirmed that 3+ coin events have high expectancy,
but full allocation doubled TRAIN drawdown and lowered Sharpe; do not tune concurrency or allocation.
EXP-023 high-volume hammer absorption was net-positive on TRAIN but failed sample and coin breadth;
do not loosen volume/wick thresholds or tune its holding period. EXP-024 volume-led continuation
passed TRAIN and raw OOS/cost/delay gates, but top-5% removal turned it negative; do not mine the
winning tails, alter close/volume thresholds, or test asset subsets.

Statistical audit note: EXP-025's B2 block bootstrap passed (P[Sh>0]=.975), but its primary WF DSR
gate failed (.543 vs .95 at 200 trials). Do not treat the Claude table or fixed-rule trade DSR as
proof of live readiness; require genuinely independent forward evidence.

EXP-026 cross-venue convergence is closed at 4h: 1,074 TRAIN trades earned only +6.25 gross bps
against 14.23 bps friction and only 2/7 coins were net-positive. Do not mine shorter holds, divergence
thresholds, direction subsets or timestamp tolerances without genuinely higher-frequency venue data.

EXP-027 prior-day Extreme Fear relief is closed as a strategy but retained as an uncertain finding:
38 TRAIN trades earned +112.45 net bps/trade with 9/9 positive coins, yet every coin had only 3–5
observations. The frozen sample gates failed, so placebo and heldout remained sealed. Do not loosen
the fear cutoff, confirmation, daily de-duplication or hold merely to manufacture more observations.

EXP-028 one-minute high-volume impact reversal is closed. Its 988-TRADE TRAIN sample was ample,
but fading shocks lost −1.46 gross bps/trade before 13.62 bps measured round-trip cost, with 0/9
coins net-positive. Validation and TEST remain sealed. Do not reverse direction post hoc or tune
return/volume percentiles and holding time; another microstructure design needs historical order
flow or book imbalance, not another OHLCV tail rule.

EXP-029 resolves EXP-027's sparse sentiment observation. The exact rule produced 145 earlier BTC
spot discovery trades and +28.62 gross bps against 22 bps friction, but its circular sentiment-date
placebo was p=.250 and 2022 lost −10.80% with −24.68% drawdown. The overlapping 2023–26 transfer
period remained sealed. Close the sentiment-relief family; do not search fear cutoffs, confirmations
or holds. Fear & Greed remains a reactive regime label, not demonstrated timing information.

EXP-030 found weak one-minute BTC→alt price discovery but no harvestable edge. Across 121 basket
events / 968 legs, both BTC shock signs predicted positive gross alt returns, yet the pooled edge
was only +0.72 bps against 14.13 bps measured friction (~20× too small); net was −15.00% and 0/8
coins were positive. Validation/TEST remained sealed. Do not mine horizons, thresholds, directions
or coins. Revisit only with true order-flow history and materially cheaper demonstrated execution.

EXP-031 audited the available true order-book sample before defining another microstructure rule.
All 360 unique snapshots are only 40 dense polls per coin spanning 260.295 seconds (six UTC minutes),
not a historical order-flow panel. The pre-signal data gate stopped the experiment with zero trades,
zero return inspection and zero trials. Revisit imbalance only after at least 30 complete days,
1,000 snapshots per coin and 20 distinct UTC days have been retained.

EXP-033 tested the previously open Bill Williams 5-bar fractal breakout as one frozen 4h long/no-stop
cell. Its 1,587-TRADE TRAIN sample earned only +5.81 gross bps against 13.71 bps round-trip cost,
lost −14.92% net, and had only 3/9 positive coins. Held-out remained sealed. Close this exact rule;
do not rescue it with trend/volume filters, target/timeout searches, coin selection, or reversal.

EXP-034 tested the simplified Morning/Evening Star continuation pattern as a frozen symmetric 4h
rule. Across 751 TRAIN trades, combined gross expectancy was −0.36 bps; longs earned +9.88 gross bps
(still below 13.64 bps cost) and shorts lost −8.51 gross bps. Net return was −11.20% with 3/9 positive
coins. Held-out stayed sealed. Close the exact next-bar rule; the direction split is not a license to
select longs post hoc or add filters.

EXP-035 tested Outside Day with Outside Close as a frozen 4h continuation rule. Its 1,934 TRAIN
trades had +6.18 gross bps expectancy against 13.68 bps cost; both directions were gross-positive,
but only 2/9 coins survived costs and net return was −16.09%. Held-out stayed sealed. Close the exact
rule; do not mine BTC/ETH, select direction, reverse post hoc, or tune stops/holds/filters.

Duplicate-prevention audit: a proposed standard MACD cycle was cancelled before assignment because
the 97-construct census proves it was already tested in Iteration 5's oscillator batch. The MACD and
grouped smoothed-momentum cards now carry explicit prior-test markers. Screen future “open” cards
against `research/research_metrics.md` as well as the newer CRYPTO-EXP log before spending a trial.

CRYPTO-EXP-036 tested standard 6-span triple-EMA TRIX with two-bar direction confirmation. TRAIN
economics were unusually strong (2,108 trades, +110.91% net, Sharpe 1.45, 9/9 positive), but the
pre-registered 999 shared-shift placebo failed (p=.107 vs ≤.025), and shorts were net-negative.
Held-out stayed sealed. Reject the exact rule; do not select longs or tune span, confirmation,
deadband, filters, or coins after seeing this result.

CRYPTO-EXP-037 tested a volatility-scaled next-bar dynamic breakout. Its 3,319 TRAIN trades earned
+18.80 gross bps against 13.70 bps cost, but only the long side worked: long gross expectancy was
+49.03 bps while short gross expectancy was −7.12 bps. Net annualized return was 6.85% with −45.48%
drawdown. The frozen side gate failed before placebo, and held-out stayed sealed. Close the exact
rule; do not select longs or tune window, width, hold, ambiguity policy, filters, or coins.

CRYPTO-EXP-038 tested the fully specified Awesome Oscillator saucer pattern. TRAIN economics were
broad (+43.19% net, 21.58% annualized, 1,796 trades, 8/9 positive, both directions profitable), but
the preregistered shared-shift placebo narrowly failed at p=.029 versus ≤.025. Held-out stayed sealed.
Close the exact saucer rule; do not rerun a seed, relax alpha, select directions/coins, tune the 5/34
averages or hold, or pivot to Twin Peaks based on the seen near miss.

CRYPTO-EXP-039 translated recent quarter-hour-effect research into a strict data gate. The claimed
mechanism needs first-10-second trade events and aggressor-side size; the local archive has only 28
complete common days of one-minute OHLCV candles and none of those fields. Zero returns were viewed
and zero trial was spent. Preserve this as a high-value data-contingent lane; reopen only at ≥365
complete common days of authenticated trade tape, never through candle-direction/volume proxies.

CRYPTO-EXP-040 screened the separate Bitcoin turn-of-the-candle anomaly before return inspection.
Its published +0.58 bps boundary-minute mean is 23.6× smaller than the project's ≈13.7 bps taker
round trip, while the paper's profitable simulation relies on attaining a zero-fee Bitfinex tier.
Only 28 complete local days exist. Close under current execution; reopen only with ≥365 days and
authenticated all-in cost below 0.58 bps, never via leverage or assumed fee status.

Audit correction: the prior hourly futures-to-mark premium census measured only feature dispersion
(1.13–3.43 bps); feature magnitude below cost is not proof that subsequent predicted return is below
cost. No causal predictive ledger was found. CRYPTO-EXP-041 reopens this narrow missing test with a
frozen contrarian tail rule; it is not a carry/funding retest.
