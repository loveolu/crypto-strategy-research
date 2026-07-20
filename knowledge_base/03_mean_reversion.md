# Mean Reversion

This file consolidates everything the source knowledge bases say about mean-reversion trading: Chan's statistical framework (stationarity, cointegration, half-life), Kaufman's contrarian oscillator-fade rules, Kaufman's pairs/arbitrage mean-reversion methodology, Kaufman's short-term fade patterns, and band/channel-fade concepts scattered across Kaufman's chapters on momentum, short-term patterns, and price distribution. A brief Hilpisch worked example is included where it illustrates the same paradigm. Every claim below is traced to its source book and chapter. Where two books cover overlapping ground with genuinely different methodologies (Chan's statistical cointegration vs. Kaufman's more discretionary/technical pairs trading), both are presented side by side rather than merged.

Cross-references: see `01_market_structure.md` for the Efficiency Ratio / noise framework that determines when a market favors mean-reversion over trend-following; see `05_momentum.md` for the underlying mechanics of momentum, RSI, stochastics, MACD, and other oscillators (this file only covers their *contrarian/fade* trading use); see `04_breakouts.md` for false-breakout fade overlap; and see the volatility file for band-width-based (Bollinger squeeze, ATR-scaled) construction details not specific to fading.

---

## Stationarity, Cointegration, and Half-Life (Chan Ch.2-3, Ch.7)

### The foundational claim

Chan states plainly that trading strategies can only be profitable if security prices are either mean-reverting or trending; "if prices random-walk, trading will be futile" (Chan Ch.7). Academic research is cited as showing stock prices are, on average, very close to a random walk — but under certain special conditions and time horizons, genuine mean-reverting or trending behavior can emerge, and the *same* price series can be mean-reverting at one horizon while trending at another (a "fractal" characterization some traders use, per Chan) (Chan Ch.7, Concepts.md).

Chan's own heuristic, explicitly labeled as his personal opinion, not an empirical finding: "unless the expected earnings of a company have changed, stock prices will be mean reverting" (Chan Ch.2, Ch.7). He cites Khandani & Lo's (2007) simple short-term mean-reversal model as empirically profitable before transaction costs over many years, but flags that whether it remains profitable after transaction costs is left to the trader to determine.

### Stationarity

**Definition** (citing Alexander, 2001): a time series is "stationary" (formally, "integrated of order zero," I(0)) if it never drifts progressively farther and farther away from its initial value (Chan Concepts.md, Ch.7).

Most individual stock **price** series are *not* stationary — they follow a geometric random walk, drifting from their IPO value over time. But appropriately-weighted **linear combinations** of two or more non-stationary series (i.e., spreads) *can* be stationary. When this holds, the constituent series are called **cointegrated** (Chan Ch.7).

Chan's central IF/THEN claim: "IF a price series (or spread) is stationary, THEN a mean-reverting strategy is guaranteed to be profitable, AS LONG AS the stationarity persists into the future (which is by no means guaranteed)" (Chan Concepts.md). He explicitly flags the converse as false: "you don't necessarily need a stationary price series in order to have a successful mean-reverting strategy," since even nonstationary series can exhibit exploitable short-term reversal opportunities (Chan Concepts.md).

**Important uncertainty flag, preserved verbatim in spirit**: persistence of stationarity into the future is explicitly *not guaranteed* — a currently-stationary spread could stop being so if the underlying economic relationship between the two securities breaks down. Chan does not give a specific detection method for this beyond implying periodic re-testing (Chan Concepts.md).

### Cointegration

**Definition**: two (or more) individually non-stationary price series are "cointegrated" if a specific linear combination of them (e.g., long one, short the other in a fitted ratio) *is* stationary (Chan Ch.7).

Cointegrating pairs typically arise between securities from the same industry group (an economic-linkage argument) — but Chan is explicit that same-industry membership is **neither necessary nor sufficient**. The book's own worked counterexample: KO (Coca-Cola) and PEP (Pepsi), same industry, do *not* cointegrate (Chan Ch.7).

**Worked example (GLD vs. GDX, Example 7.2)**: long 1 share of GLD (gold ETF), short 1.6766 shares of GDX (gold miners ETF) forms a stationary spread. The hedge ratio (1.6766) was determined by OLS regression of GLD against GDX. Tested via the **cointegrating augmented Dickey-Fuller test (CADF)**, using a free MATLAB package from spatial-econometrics.com (James LeSage): CADF t-statistic = −3.35698533 (1 lag, AR(1) estimate −0.060892), versus critical values −3.819 (1%), −3.343 (5%), −3.042 (10%). Because the t-stat falls between the 1% and 5% critical values, there is "better than 95% probability" the two series are cointegrated (Chan Ch.7, Indicators.md).

**Counterexample (KO vs. PEP, same industry, NOT cointegrated)**: CADF t-statistic = −2.14, less negative than the 10% critical value of −3.038 → less than 90% probability of cointegration. The regression-fit spread visibly drifts over time rather than mean-reverting (Chan Ch.7).

The CADF test is treated by Chan largely as a "black box" — the underlying Dickey-Fuller regression mechanics are not derived in the source; only how to run and interpret the test via the referenced package is given (Chan Indicators.md). Like any hypothesis test, a valid CADF result at one point in time does not guarantee the cointegration relationship will persist — an explicit, unresolved caveat (Chan Indicators.md).

**Other asset classes mentioned as exhibiting stationarity/cointegration** (mentioned by Chan, not elaborated with backtests): certain currency cross-rates, e.g. CAD/AUD, "noted as stationary since both are commodities currencies"; futures calendar spreads (long/short the same underlying commodity, different expiration months) — "the simplest examples of cointegrating futures pairs"; and fixed-income instruments, e.g. long/short bonds by the same issuer with different maturities (Chan Ch.7).

### Cointegration vs. Correlation — an explicit, heavily emphasized distinction

Chan treats this as one of the most important conceptual traps in the entire mean-reversion framework: "Many pair traders are unfamiliar with the concepts of stationarity and cointegration. But most of them are familiar with correlation, which superficially seems to mean the same thing as cointegration. Actually, they are quite different" (Chan Ch.7, Concepts.md).

- **Correlation** measures co-movement of *returns* over a chosen (typically short) horizon. It says nothing about long-run price-level behavior.
- **Cointegration** measures whether a linear combination of *price levels* remains bounded (stationary) over the long run.

Two stocks can be significantly correlated in daily returns while their price levels drift arbitrarily far apart over years. Conversely, a synthetic example in the book (two stocks A and B, Figure 7.6) shows a pair that is cointegrated (the A−B spread always reverts to ~$1) while showing essentially no daily return correlation (Chan Ch.7).

**Concrete real-world proof point**: KO/PEP daily-return correlation = 0.4849 (p = 0, i.e., statistically significant) — yet the same pair fails the CADF cointegration test (Chan Ch.7, Indicators.md). Chan's explicit practical rule: when screening candidate pairs for a mean-reversion pair-trading strategy, use a cointegration test (CADF), *not* a correlation test, as the primary screening criterion (Chan Concepts.md).

### The Ornstein-Uhlenbeck half-life of mean reversion

**Model** (Chan Ch.7, Indicators.md):

```
dz(t) = -θ(z(t) - μ)dt + dW
```

where z(t) is the spread/price series, μ is its long-run mean, θ is the mean-reversion speed parameter, and dW is Gaussian random noise.

**Purpose**: provides a statistically robust, whole-time-series-based method for estimating the optimal holding period of a mean-reverting position — more robust than counting actual historical trade durations (which may be a small, noisy sample), because it uses the *entire* time series (not just trade-triggering days) to estimate θ (Chan Ch.7).

**Estimation method**: θ (and μ) are estimated via a linear regression of the daily *change* in the spread (dz) against the spread level itself: `dz = -θ·(z - mean(z)) + noise`, i.e., regress dz on (prevz − mean(prevz)) to get θ = −(regression beta). The exact MATLAB formula given: `theta = results.beta` from `ols(dz, prevz - mean(prevz))`, then `halflife = -log(2)/theta` (Chan Indicators.md).

**Half-life** = ln(2)/θ = the expected time for the deviation from the mean to shrink by half.

**Worked result (GLD/GDX, Example 7.5)**: half-life ≈ **10.0037 days**, i.e., approximately how long one should expect to hold the GLD-GDX spread trade before it becomes profitable (Chan Ch.7).

**Strengths/weaknesses**: more statistically robust than a naive trade-based holding-period estimate, and directly interpretable as "expected time to revert halfway." Weakness: assumes the O-U process form is a good approximation of the actual mean-reversion dynamics — this is not separately validated in the source beyond the single GLD/GDX example; and like all backward-looking parameter estimates, θ can change if the underlying mean-reversion dynamics shift (Chan Indicators.md). Applicable specifically to spreads/series already identified as mean-reverting (e.g., via a prior cointegration test) — not meaningful for trending/momentum series.

### Exit-strategy logic specific to mean reversion (a core IF/THEN framework)

Chan categorizes all exit logic into exactly four types: (1) a fixed holding period, (2) a target price or profit cap, (3) the latest entry signal used as an exit trigger, and (4) a stop price (Chan Ch.7, Concepts.md).

**For mean-reverting strategies specifically**:
- The historical mean price (μ from the O-U model) is a natural **target price**, usable in combination with the half-life as dual exit criteria — exit on whichever triggers first (Chan Ch.7).
- **Stop losses are explicitly argued to be harmful, not helpful, for reversal-model exits.** Chan's reasoning: re-running a reversal (mean-reversion) model after an existing position has lost money will simply generate *another* signal of the same sign (since the position is now further from the mean, if anything a stronger reversal signal). Therefore, "a reversal model for entry signals will never recommend a stop loss." A stop-loss in this context "often means you are exiting at the worst possible time" (Chan Ch.7, Concepts.md).
- **The sole stated exception**: IF you believe you have suddenly entered a momentum regime due to fresh news, THEN even an originally mean-reversion-motivated position may warrant a stop-loss-like exit (Chan Ch.7, Concepts.md).
- By contrast, stop-loss exits and "latest-signal-reversal" exits are conceptually appropriate for **momentum** regimes, not mean-reversion ones — this asymmetry (mean-reversion ≠ momentum in exit-rule design) is treated as close to universally applicable by Chan.

### Backtesting perils specific to mean-reverting strategies (Chan Ch.7)

Chan flags two backtesting pitfalls as *disproportionately* damaging to mean-reversion strategies specifically:

1. **Data errors artificially inflate mean-reversion backtests.** A mean-reverting strategy will buy on a fictitiously-low quote and sell on the next (correct) quote near the moving average, generating a "profit" from pure data error. Recommendation: thoroughly cleanse data of fictitious quotes before trusting mean-reversion backtest results.
2. **Survivorship bias disproportionately affects mean-reversion backtests.** Stocks with extreme price moves are disproportionately likely to have been acquired (price spiked) or gone bankrupt (price → 0). A mean-reverting strategy would short the former and buy the latter — losing money on both in reality — but survivorship-biased data may exclude these stocks entirely, artificially inflating backtested performance.

### Competition's effect on mean-reversion opportunities

Chan explicitly contrasts the two regimes: for **mean-reverting strategies**, competition gradually eliminates the arbitrage opportunity, diminishing returns toward zero. As true arbitrage opportunities shrink, an increasing proportion of remaining trading signals reflect real fundamental valuation changes rather than transient mispricing — i.e., signals become less reliably "mean-reverting" and more often value-trap-like (Chan Ch.7). This is the opposite dynamic from momentum strategies, where competition instead shrinks the optimal holding period rather than eliminating the opportunity outright.

### Worked example: the transaction-cost fragility of mean reversion (Chan Ch.2-3)

Chan's own illustrative Bollinger Band mean-reversion strategy on ES (E-mini S&P 500 futures), 5-minute bars, entering at ±2 moving standard deviations and exiting within 1 standard deviation, had a Sharpe ratio ≈ **3** with no transaction costs — but Sharpe ≈ **−3** after subtracting just 1 basis point of transaction cost (Chan Ch.2, Ch.3). This is presented explicitly as a cautionary illustration, not an endorsed strategy, of how easily high-frequency mean-reversion strategies can flip from excellent to ruinous once realistic costs are applied.

A second worked example (Khandani & Lo-style cross-sectional 1-day mean-reversal, buying the worst-performing stocks and shorting the best-performing stocks daily): pre-cost Sharpe on the S&P 500 large-cap universe was only 0.25 (versus the original authors' reported 4.47, attributed by Chan to their result being driven mainly by small/microcap stocks); after a 5bp one-way transaction cost, Sharpe collapsed to **−3.19** ("very unprofitable"). A refinement — simply rebalancing at the market open instead of the close — raised the pre-cost Sharpe to 4.43 and the post-cost Sharpe to a profitable 0.78 (Chan Ch.3). See `02_backtesting_methodology.md`-equivalent material for the full transaction-cost discussion if such a file exists in this knowledge base; the load-bearing point for mean-reversion specifically is that this strategy family is unusually transaction-cost-sensitive due to high rebalancing frequency.

### Survivorship bias and mean reversion — a deeper compounding relationship

Beyond the general database-bias discussion, Chan explicitly cross-references that mean-reversion strategy backtests are hit doubly hard: a mean-reverting strategy would short extreme winners (later acquired, price spikes) and buy extreme losers (later bankrupt, price to zero) — both cases likely to be *excluded* from a biased dataset, hiding the real losses those trades would have incurred in live trading (Chan Concepts.md, cross-referencing Ch.3's worked toy example where survivorship-biased data flipped a true −42% return into a fictitious +388%).

---

## Oscillator Fades and Contrarian Rules (Kaufman Ch.9)

**Important scope note for this section**: Kaufman's Chapter 9 is titled "Momentum and Oscillators" and is predominantly about the *mechanics and construction* of momentum indicators, oscillators, MACD, RSI, stochastics, and their divergence-based trend-confirmation uses — that underlying indicator mechanics content belongs in `05_momentum.md`, not here. This section extracts only the material that is explicitly framed by Kaufman as *contrarian/countertrend/fade* trading logic — i.e., trading *against* an oscillator's current direction rather than using it to confirm a trend. Kaufman's chapter genuinely does contain a substantial fade-specific subsection ("Identifying and Fading Price Extremes"), so this is not a thin/absent topic — but it is a smaller fraction of the chapter than the indicator-mechanics content, which the momentum-file agent should be the primary owner of.

### The core framing: momentum as both trend and countertrend tool

Kaufman states that shorter momentum calculation periods make the indicator more sensitive to small price changes, and it is then "often used as a countertrend/mean-reversion tool to indicate overbought/oversold" conditions — as distinct from longer calculation periods, which behave more like a trend indicator (Kaufman Ch.9). This calculation-period-dependent duality is the structural basis for everything in this section: the *same* indicator family can be used either way depending on period length and rule design.

### Identifying and Fading Price Extremes

Momentum's positive/negative peaks are bounded by the maximum possible price move over the calculation period N. Kaufman defines:
- **Overbought** = a sustained upward trend at a fast rate for most of N days → expect a downward reaction, or at least a slowdown.
- **Oversold** = the mirror condition.

Faster momentum periods fluctuate frequently above/below zero (small price changes); longer periods behave like a trend and stay on one side of zero for the trend's duration (Kaufman Ch.9).

#### Setting the fade thresholds

Kaufman gives three explicit ways to select the horizontal threshold lines used to flag tops/bottoms for fading:
1. Visually, from prior extreme values, so a penetration tends to precede a reversal.
2. As a percentage of the maximum possible momentum value.
3. As a multiple of the standard deviation of momentum values (2 standard deviations → only ~5% of values penetrate above/below the two lines) (Kaufman Ch.9).

#### Entry rule variants, aggressive → most confirmed (Kaufman Ch.9)

- **Aggressive**: enter long when momentum crosses the *lower* bound; enter short when it crosses the *upper* bound (i.e., fade the extreme immediately on penetration, no confirmation).
- **Minor confirmation**: enter short on the first day momentum *turns down* after crossing the upper bound (mirror for longs).
- **Major confirmation**: enter short when momentum crosses back *below* the upper bound while moving lower (mirror for longs).
- **Timing variant**: enter short after momentum has remained above the upper bound for n days, or after a confirmation has occurred (mirror for longs).

#### Exit rule variants, symmetric long/short (Kaufman Ch.9)

- **Most demanding**: exit when momentum crosses the *opposite* threshold used for entry (e.g., entered short at +50, cover at −50).
- **Moderately demanding**: cover when momentum crosses zero minus one standard deviation (or another interim target between zero and the entry bound); the standard deviation here is computed on the *changes in* momentum, not the momentum values themselves.
- **Basic exit**: cover when momentum crosses zero.
- **Allowing an extended move**: cover when momentum crosses zero moving up after having penetrated it moving down (this effectively uses momentum as a short-term trend rather than a pure fade).

#### Risk protection for fade entries — an explicit warning

"A protective stop-loss should be used whenever trading opposite to current momentum (fading)." This is most important for the **aggressive entry** variant (selling as momentum rises above the upper threshold regardless of price speed) — Kaufman states there is *no natural stop-placement logic* for this variant; the trader must set risk based on historic momentum/volatility. For the more-confirmed entry variants, since price is no longer at an extreme when entered, stops can be placed above/below the most extreme high/low momentum value, as a trailing stop based on momentum points or price volatility, or via equal-spaced "zones" acting as interim profit levels that disallow reverse penetration once a new zone is entered (Kaufman Ch.9). **Key caution, stated explicitly**: both profit targets and risk on extreme-entry (fade) trades must scale up with rising volatility/price levels — a fixed-dollar or fixed-point fade threshold will become miscalibrated as volatility changes (see also "Changing Volatility" below).

#### A cautionary empirical finding against naive aggressive fading

Kaufman reports an accidental test result: a computer test of the aggressive fade entry was coded backward by mistake (it ended up buying on upper-bound crossing with a stop *below* entry — i.e., trend-following, not fading) — and this *still* produced "outstanding, consistent profits." Kaufman's own interpretation: this incidentally proved that high-momentum periods persist long enough to capture small consistent profits, and that an aggressive countertrend entry anticipating an early reversal at that same threshold would, by implication, be a comparatively weaker approach. His explicit reminder: "declining momentum while still above zero does not mean prices are falling — only that they are rising more slowly" (Kaufman Ch.9). This is presented as empirical evidence urging caution about naive aggressive fading, not a blanket condemnation of fading generally.

#### Exiting countertrend (fade) trades — the core mean-reversion exit logic

For pure mean-reversion trades (short entered at a momentum high, long at a low), Kaufman states the most reasonable exit is when momentum returns to *near zero* (the midpoint) — the extreme is expected to return to normal, though this does not guarantee profitability if price kept moving against the position while momentum "returns to neutral" (Kaufman Ch.9).

- **Win-rate vs. profit-size trade-off, explicit**: targeting a more conservative exit (e.g., 5-10% short of zero, based on the distance from the entry threshold to zero) gives a smaller average profit but a higher win rate; conversely, targeting the *opposite* side of zero (past neutral, into the opposite extreme zone) increases average profit per trade but at a lower win rate.
- Effectiveness of early vs. late profit-taking depends on the noise level in the momentum series; trending markets keep momentum on one side of zero for a long time, making an opposite-side exit target a long wait.

### RSI-specific contrarian/fade material (Wilder, 1978; Kaufman Ch.9)

- **Standard thresholds**: 30 (oversold, imminent upturn) and 70 (overbought, pending downturn), on Wilder's preferred 14-day calculation period.
- **Wilder's own top/bottom formations ("failure swing")**: buy signal when a second RSI low is higher than the first low, then RSI moves above the peak of the rally between the two lows; mirror sell signal (second high lower than first, RSI breaks below the low between the two highs).
- **Calculation-period trade-off**: too short a period causes RSI to stay outside the 70/30 zone for extended stretches rather than giving a timely reversal signal — the goal is to pick a period for which sustained moves rarely exceed the period length. Shorter periods (e.g., 10) paired with wider zones (80/20) give more frequent fade signals.
- **RSI Countertrend jump-trigger variant**: instead of only using the absolute RSI threshold, trigger on a large 1-day RSI jump — sell when `RSI_t − RSI_[t-1] > D` (some threshold), or buy on the mirror condition, regardless of RSI's absolute level. This increases trade frequency when combined with standard threshold entries. Exits at momentum returning to near zero, or after n days (Kaufman Ch.9, reference tool `TSM RSI Countertrend`).
- **2-Day RSI** (Michael Stokes, MarketSci Blog, Dec. 9, 2008): replaces each 1-day closing-price change with a 2-day change before running the standard RSI calculation — smoother than a straight 1-day RSI but with higher overall RSI volatility. **Stokes's simple rules (S&P)**: buy on next close when the 2-day RSI penetrates 10 moving lower; sell short on next close when it penetrates 90 moving higher; exit one day later on the close. **Historical regime-shift finding, explicitly noted**: 2-day RSI (S&P) behaved as a good *trend* indicator from 1970-1998 (RSI above 90 → S&P continued up) but reversed into a *mean-reverting* indicator after ~1998 — an explicit example of the same indicator flipping regime interpretation over time.
- **Scaling-in variant** (same MarketSci source): a graduated position-sizing table, symmetric long/short —

  | RSI condition | Buy % | RSI condition | Sell-short % |
  |---|---|---|---|
  | <5 | 100% | >95 | 100% |
  | <10 | 75% | >90 | 75% |
  | <15 | 50% | >85 | 50% |
  | <20 | 25% | >80 | 25% |

  Exit rule (Stokes's, considered safer than waiting for RSI to cross 50, since 2-day RSI can stay pinned above/below 50 for long stretches): exit one day later on the close. Kaufman flags an explicit ambiguity in the source itself: it is unclear whether adding to a position on a further RSI extreme the next day implies an unwinding logic if no further add occurs — the book states it assumes exit if no add occurs on the next day. **Explicit warning**: 1-day-holding-period trades of this kind are highly sensitive to commissions/slippage; per-share/per-contract returns must be checked to confirm they cover costs.
- **Net Momentum Oscillator** (Chande & Kroll, 1994): AU − AD (difference, not ratio, of up-day and down-day sums) — recovers extremes that RSI's ratio-based smoothing removes; an equivalent effect can be had simply by shortening RSI's calculation period.

### Stochastics-specific contrarian material (George Lane; Kaufman Ch.9)

- **Trading the stochastic (fade framing)**: buy below 10, sell above 90 (thresholds depend on calculation period); Kaufman notes this is typically filtered by trend direction (buy dips within an uptrend, i.e., fade only in the direction of the larger trend rather than fading unconditionally).
- **Extremes**: reaching 0 or 100 requires 7 consecutive closes at the highs/lows; the subsequent test of these extremes following a pullback is described as "an excellent entry point."
- **Caveat, explicitly stated as dangerous**: "if price does not retrace after a trend signal, a confirming stochastic signal may never occur, or occur very late — it is particularly dangerous to use a timing rule for exiting a position. Delays in entering are lost opportunities, but delays exiting are real trading losses" (Kaufman Ch.9).
- **Stochastic-from-any-indicator generalization**: any indicator (including an unbounded one like raw momentum) can be converted to a bounded %K-style stochastic by substituting the indicator's own value for closing price in the standard stochastic formula — this normalization technique underlies several of the pairs-trading and volatility-arbitrage fade systems described later in this file (Kaufman Ch.9, also used in Kaufman Ch.13).

### Williams' A/D Oscillator — an explicit fade-risk warning

Kaufman's treatment of the Waters-Williams A/D Oscillator (Daily Raw Figure, DRF) includes a direct, general statement about the risk asymmetry of fading: **"countertrend/overbought-fade trading is exciting and profitable, but at considerably greater risk than trading in the direction of the trend"** — losses on a fading long position entered while price keeps falling fast can be substantial even with a quick exit (Kaufman Ch.9). This is one of the clearest single-sentence risk statements about oscillator fading in the source material and applies conceptually to the whole fade-trading category, not just the A/D Oscillator.

### Ultimate Oscillator (Larry Williams, 1985) — fade/reversal rule set

Combines the A/D Oscillator concept with Wilder's RSI across three concurrent time periods (7, 14, 28 days) to reduce whipsaw. **Trading rules** (Kaufman Ch.9):
1. Sell setup: oscillator rises above 50%, peaks, declines, then rallies again; if it fails to exceed the prior peak on this second rally, a short sale is placed when the oscillator fails at the "right shoulder" (a classic top-confirmation/fade pattern).
2. Cover shorts when a long signal occurs, when the 30% level is reached, or if the oscillator rises above 65% (stop-loss) after having been below 50%.
3. Buy signal: the mirror pattern of rule 1 (bottom formation).
4. Close longs when a short signal occurs, when the 70% level is reached, or if the oscillator falls below 30% (stop-loss) after having been above 50%.

### Changing volatility — the core structural problem with fixed-band oscillator/momentum fades

Kaufman gives a detailed empirical illustration (S&P 20-day and 3-day momentum, 2005-2011) of why fixed fade thresholds fail over time: entry bands appropriate in a low-volatility year (e.g., ±30 for the 20-day momentum in 2006) become far too tight once volatility rises (2007-2008), producing large open losses if the bands aren't widened; after volatility subsides, static wide bands then produce too few signals. **General finding, stated explicitly**: "the scale of a fixed-band momentum system is unpredictable" — it needs dynamic adjustment (see the volatility file for volatility-band cross-references) or a genuinely bounded/self-normalizing oscillator construction instead of raw momentum (Kaufman Ch.9). This is the direct rationale motivating the oscillator-normalization principle described above (dividing raw momentum by its own rolling maximum).

### Kurtosis-Skew Strategy — an explicit mean-reverting variant contrasted with a trend-following variant (Kaufman Ch.18)

Although this strategy lives in Kaufman's price-distribution chapter rather than Ch.9, it is directly relevant here because Kaufman presents *both* a trend-following and a mean-reverting rule set built on the same underlying indicators (excess kurtosis, skew, and ATR as a volatility filter), making the trend-vs-fade distinction explicit:

- **Trend-following entry rules**: Buy when excess kurtosis crosses below 0, skew > 0, AND volatility > a minimum level. Sell when excess kurtosis crosses below 0, skew < 0, AND volatility > minimum.
- **Mean-reverting entry rules** (fading the move flagged by a kurtosis cross above zero): Buy when excess kurtosis crosses *above* 0, skew < 0, AND volatility > minimum. (The source's stated mean-reversion "Sell" rule appears, verbatim, to duplicate the trend-following sell condition rather than mirror the mean-reversion buy rule — this is flagged in the source itself as a likely internal inconsistency/transcription error, preserved here rather than silently corrected.)
- **Author's suggested enhancement, explicitly noted as not in the base rule set**: mean-reverting trades in this system performed better at *higher* volatility, implying the trend-following variant might do better by excluding high-volatility entries (i.e., add a maximum-volatility filter to the trend variant) — an explicit empirical note that volatility regime differentially favors fade vs. trend variants of the same underlying indicator.

### DeMark's Sequential™ (Thomas DeMark) — a 3-stage countertrend exhaustion system

A fully mechanical, named countertrend system built specifically to identify a severely overextended move likely to reverse — one of the best-known named mean-reversion systems in the technical-analysis literature and notable among this book's systems for having **no adjustable "dial"** for robustness testing (Kaufman Ch.4; cross-ref `14_backtesting_and_validation.md` and `Concepts.md` for the robustness-testability implication).

- **Buy signal — 3 sequential stages (daily data)**:
  1. **Setup**: ≥9 consecutive closes strictly lower than the close 4 days earlier; any day failing the condition restarts the count from zero.
  2. **Intersection**: the high of any day on or after the 8th setup day must exceed the low of any day 3+ days earlier (confirms an orderly decline rather than a plunge; may occur with some delay after the setup completes).
  3. **Countdown**: count (non-consecutive days allowed) days where the close is below the close 2 days ago; the buy signal fires once the count reaches 13, UNLESS: (a) a close exceeds the highest intraday high recorded during the setup stage; (b) a *sell* setup occurs (9 consecutive closes above the close 4 days earlier); or (c) another buy setup occurs first — any of these triggers "recycling," restarting the process at step 2.
- **Sell signal**: the exact mirror of the buy signal (9 consecutive higher closes vs. 4 days earlier, intersection test, countdown to 13 on closes above the close 2 days ago).
- **Typical formation duration**: 21+ days, typically 24-39 days from setup start to countdown completion — a genuinely multi-week pattern despite the "short-term reversal" framing.
- **Entry timing options (trade-off between price and recycling risk)**: (1) enter on the close of the countdown-completion day itself (best price, but exposed to a new competing setup forming immediately); (2) wait for confirmation — a close above the close 4 days ago (avoids recycling risk, but a later/worse entry); (3) a close above the high 2 days earlier (a compromise between the two).
- **Exit rule**: if the current setup's price extreme does not exceed the prior opposite setup's extreme, exit on setup completion; if it does exceed that prior extreme, hold for a reverse (opposite) signal instead.
- **Stop-loss (two variants)**: (a) the true range of the lowest-range day within the setup+countdown window, subtracted from that day's low; (b) the close-to-low distance of that same lowest day, subtracted from its low (a tighter stop than variant a).
- **Important Warning — robustness-testability caveat (Kaufman's own methodological point, cross-ref `Concepts.md`)**: unlike a breakout system whose lookback period can be swept to check for smooth, interpretable robustness, Sequential is a single fixed rule set (the countdown always targets exactly 13) with no comparable adjustable parameter — Kaufman states its future reliability is therefore unverifiable by his own standard parameter-sweep method ("only time will decide"). **Project inference**: when screening candidate crypto strategies, prefer ideas with at least one continuously-tunable parameter over single fixed "magic number" rules like this one, precisely because the latter cannot be robustness-tested the same way (Kaufman Ch.4, Algorithmic_Trading.md, Research_Ideas.md #7).

---

## Pairs Trading and Arbitrage Mean Reversion (Kaufman Ch.13)

### Kaufman's framing vs. Chan's framing — an explicit methodological contrast

Both books cover pair trading as a mean-reversion strategy, but their approaches differ substantially in rigor and philosophy, and this difference is worth stating explicitly per the task's instruction not to silently merge them:

- **Chan (Ch.7)** treats cointegration testing (CADF) as the primary, near-mandatory screening tool, explicitly rejecting correlation and same-industry heuristics as insufficient, and builds the entire holding-period/exit framework around the statistically-estimated Ornstein-Uhlenbeck half-life.
- **Kaufman (Ch.13)** presents cointegration as the most *rigorous* of three methods but treats it as one option among several, explicitly validating simpler, more discretionary approaches: "traders have been successful at pairs trading long before cointegration was known" (Kaufman Ch.13). Kaufman's own worked pairs examples (ICBC/BOC, LEN/KBH) use simple standard-deviation bands on price differences or momentum differences, not a full CADF/O-U pipeline, and he states cointegration's "exact implementation is closely held and requires a strong math background" — implying it is less accessible than his own simpler methods, not necessarily superior in practice.

### Kaufman's terminology distinctions (Ch.13)

- **Spread or straddle**: opposing positions in related markets, contracts, options, or shares generally.
- **Pairs trading**: a spread specifically between two related stocks, entered simultaneously long/short.
- **Arbitrage**: when the dynamics of the spread can be *definitively calculated* (e.g., two bonds of the same maturity/grade); academic usage implies risk-free, "although nothing is risk-free" (Kaufman's explicit qualifier).
- **Relative value arbitrage**: an arbitrage between two similar-but-not-identical companies/products that diverge, where there is a history of similar price movement.

### Three methods to qualify pair candidates, in order of simplicity (Kaufman Ch.13)

1. **Correlations between 0.4 and 0.7** — indicates short-term co-movement without being overly tight; the simplest, most popular method. (Note: this directly contrasts with Chan's explicit rejection of correlation as a screening tool — Kaufman treats correlation in this band as a legitimate, if less rigorous, first-pass filter, not an error.)
2. **A high z-score or 2-sample t-test** — indicates similar mean and distribution of prices between the two series. Worked example: LEN/KBH, using an online 2-sample t-statistic calculator with n=1,310 data items, showed ≥95% confidence for each of three tested pairs.
3. **Cointegration** — identifies whether the *long-term trend* of the two series is the same; if so, variations around the trend are trading opportunities.

**Kaufman's own summarized cointegration procedure** (Ch.13), presented as less formally rigorous than Chan's CADF pipeline but structurally similar:
1. Find two candidate markets, A and B.
2. Each market must be **stationary** (no underlying trend) — tested via 1st differences summing near zero, or the more rigorous **Dickey-Fuller (DF) test**: regress the series against itself lagged by one day; if the regression slope < 1, the series is stationary. If 1st differences fail, try 2nd differences ("order 2"), though it's best if 1st differences work.
3. If both series are stationary, solve a regression between them (doable in Excel's Data Analysis tool); a specific condition on the regression result (exact threshold notation lost to PDF extraction) indicates the pair satisfies cointegration conditions.
4. Even a stationary series can have differing volatility — the ratio of the two series' annualized volatilities (standard deviation of 1st differences × √252 for daily data) gives the **position-size ratio needed for equal-risk legs**. Very high annualized volatility in either series may argue for avoiding that pair.
5. The **Johansen Test** is also cited as usable for cointegration (source code available online).
6. **Verification tip**: test the ETF SPY against its inverse SDS — the regression should always be stationary (near-zero X) though price swings vary by period; the SDS/SPY volatility ratio ≈ 2.5 (because SDS is leveraged).

Kaufman's worked LEN/KBH correlation results: full-period correlation = 0.797 (very high); rolling correlations were extremely high 2002-2008 but more erratic afterward; even restricting to a 2012-March 2018 divergence period, correlation remained 0.752 — "by any criterion, these two markets are candidates" (Kaufman Ch.13).

### Worked pairs-trading strategy: Pairs Mean-Reversion via Price-Difference Bands (ICBC-BOC) (Kaufman Ch.13)

- **Purpose**: mean-reversion pairs trade using a standard-deviation band around the raw price *difference* of two correlated stocks.
- **Assets**: Industrial and Commercial Bank of China (ICBC) and Bank of China (BOC), both traded in Shanghai, 2007-2017 history.
- **Indicators**: rolling 15-day standard deviation of the price difference (ICBC − BOC), ±2.0 SD bands around that difference.
- **Entry rules**: buy ICBC / sell BOC when the difference is below the 15-day average minus 2.0 standard deviations; sell ICBC / buy BOC when the difference is above the 15-day average plus 2.0 standard deviations.
- **Exit rules**: exit when the current difference crosses back above (long case) or below (short case) the 15-day average of the difference.
- **Position sizing**: equal-dollar investment (e.g., $1,000) divided by the current price of each leg.
- **Optimization note, explicit**: a smaller standard-deviation threshold generates more trades and higher risk. Calculation periods for pairs trades are kept intentionally short (here 15 days) because adapting quickly to volatility is critical to risk control — this also results in short (few-day) holding periods, which Kaufman describes as fitting the nature of pairs trading generally.
- **Ambiguity/limitation**: no explicit stop-loss beyond the exit-at-mean rule; profitability was shown for 2011 specifically (a "quiet period," per the source) as the illustrative example, with total profits for the full 2007-2017 window shown only in a source figure not reproduced in text.

### Worked pairs-trading strategy: Momentum-Difference Pairs Trade (Kaufman Ch.13, Lennar/KB Home)

- **Purpose**: treat a pairs trade as relative-value arbitrage using the *difference* between two identical momentum indicators applied to each leg, rather than a price-level difference.
- **Indicators**: 6-day raw stochastic applied separately to each stock; the difference between the two stochastic values (Kaufman notes RSI or MACD would give similar results).
- **Entry rules, two variants**:
  1. Sell the stronger stock when it is overbought (stochastic ≈90) and the momentum difference exceeds a threshold (e.g., 70); says nothing about the other leg. Exit when the overbought stock corrects to neutral or the momentum difference narrows to neutral.
  2. (Preferred/easiest to implement) Buy the weaker stock when the momentum difference is below −20; sell when the difference is the mirror-positive threshold. Exit when the difference crosses zero.
- **Result**: profits shown for LEN-KBH using variant 2 from 1998 through Q1 2018 (aggregate figure only, no numeric Sharpe/return given in extractable text).

### Worked pairs-trading strategy: Stress Indicator Pairs Trade (Kaufman Ch.13)

A refinement of the Momentum-Difference approach: a **Stress Indicator** = a second stochastic calculation applied to D_t, the day-t difference between the two legs' 6-day raw stochastics, with a 10-day calculation period in the worked example. Buy leg 1 / sell leg 2 when the Stress Indicator is below its low threshold; sell leg 1 / buy leg 2 when above its high threshold; exit at the opposite-side threshold. Kaufman notes that because the short (10-day) calculation period can pin the stochastic at 0 or 100 for several days, some traders instead enter on the *first day the momentum reverses from the extreme* — success of this technique depends on how strongly the market trends. A minimum-volatility filter is recommended in quiet markets, where the momentum fluctuation range may be too small to trade profitably. **Result comparison**: over 1998-Q1 2018, the raw Momentum-Difference approach was "slightly better" than the Stress Indicator refinement, though Kaufman cautions this is a single test.

### Other Kaufman pairs/intermarket mean-reversion systems

- **Bond-Utility Arbitrage** (cited to Murray Ruggiero): 30-year Treasury bond futures vs. utility ETF XLU (substituted for the original Philadelphia Utility Index). Entry: buy bonds if US < 6-day MA(US) AND XLU > 20-day MA(XLU); sell short bonds on the mirror condition. Stated as consistently profitable long and short over the prior 20 years, per the source (Kaufman Ch.13).
- **S&P-Bond (High-Yield Timing) Arbitrage** (adapted from Hector Landazabal): times SPY entries using the S&P/high-yield-bond intermarket relationship, motivated explicitly by the fact that the S&P's reaction to rate changes lags too much (the "J-curve" effect) for a classic simultaneous arbitrage. Buy SPY when the 20-day rolling correlation of SPY with HYG/JNK is sufficiently below the 252-day rolling correlation AND SPY's 5-day return trails the combined HYG/JNK 5-day return by ≥0.5% (Kaufman Ch.13).
- **Intermarket Index Ratio Mean Reversion** (S&P/DJIA, S&P/Russell 2000): "in the short term, differences between related index markets are mean reverting (buy the lower ratio, sell the higher, expect reversion to the midpoint); however, a longer-term trend can also exist in the ratio" — an explicit dual-regime caveat, since the same ratio series can be traded as either mean-reverting or trending depending on horizon (Kaufman Ch.13, directly echoing Chan's fractal mean-reversion/momentum duality claim).
- **IV/HV Relative Value Arbitrage (UVXY/SPY)**: sell IV, buy HV when implied volatility (via UVXY/VIX) spikes relative to historic volatility (calculated from SPY); since there is no tradeable HV instrument, the trade is executed entirely through SPY. Net stochastic (UVXY stochastic minus SPY-HV stochastic) ranges −100 to +100; sell SPY when net stochastic > 20 (loosened from a stricter symmetric level to capture more trades), buy SPY when net stochastic < −80; exit at net stochastic = 0. Kaufman's explicit warning: never assume an overbought reading will flip directly into oversold — once normalized, there is no directional edge in predicting what comes next. Both directions were profitable over a ~5-year test, with short trades (selling SPY on UVXY overbought) more reliable; combining both directions added roughly 20% to total returns versus either alone. **Explicitly stated to be "not a true arbitrage but a timing method"** (Kaufman Ch.13). **Cited alternative construction (Ernest Chan, *Machine Trading*, 2017, not independently developed by Kaufman beyond the summary rule)**: using a contract ratio of 0.39:1, buy VX (volatility futures) and buy ES (S&P futures) when VX is in backwardation with a roll return ≤ −10%, or in contango with a roll return ≥ +10% — a differently-constructed relative-value volatility trade than the UVXY/SPY net-stochastic system, sharing the same IV/HV convergence premise (Kaufman Ch.13).
- **Trend of Ratio (Crude/Gold)**: contrasted explicitly as a *trend*, not mean-reversion, application of a spread/ratio series — included here only to make the trending-vs-reverting decision framework clear (see "Trending or Mean Reverting?" below).
- **Butterfly Spread**: exploits fund-roll-driven term-structure distortions rather than relative-value divergence between two distinct markets — a sibling arbitrage technique to the ratio/pairs systems above, but built entirely within one market's delivery-month term structure. Best in highly volatile markets where concentrated trading in one or two delivery months (often fund managers rolling from nearby to next delivery in the week before expiration) pushes those contracts out of their normal term-structure relationship. **Worked example (soybeans)**: sell 2 July contracts, buy 1 May + 1 August contract — equivalent to two simultaneous spreads (long May/short July, short July/long August). Described as "essentially risk-free" once entered, because the middle (July) contract cannot remain out of line with both surrounding deliveries — a trader could take delivery of May and redeliver in July at a profit exceeding the cost of carry. **Caveat**: the opportunity window is short, both legs are hard to execute simultaneously, and a lack of trading in deferred months can create a false apparent distortion if only stale last-traded prices (not live bid/ask) are visible (Kaufman Ch.13).
- **Trend Following Using Bull and Bear Spreads**: substitutes a lower-risk intramarket (interdelivery) spread for an outright directional trend position, applied to grain/food commodity markets where nearby-month prices move faster than deferred-month prices in the direction of the trend. **Bull spread** (bull market expected): long the nearby delivery, short a deferred delivery — both risk and reward are reduced versus an outright position, though the spread itself becomes more volatile as the gap between the two months widens. **Bear spread**: the mirror, short nearby / long deferred. **Entry confirmation**: many traders require the spread series itself (not just the nearby contract) to confirm the trend, via a medium-speed moving average on the spread or a 1- to 3-day spread-direction change for faster traders — a bullish nearby-contract signal paired with a bearish spread signal is read as a short-term supply disruption, not a good trending-spread entry. **Exit**: once the underlying trend peaks, the spread must be reversed, since the nearby delivery declines faster than the deferred month (Kaufman Ch.13).

### Named value/basket mean-reversion systems: Dogs of the Dow, Small Dogs, Foolish Four (Kaufman Ch.22)

A different flavor of basket mean reversion from the pairs/spread systems above: instead of fading a price or momentum difference between two related instruments, this family fades a *ranking* (dividend yield) across a fixed basket of stocks, rebalanced annually.

- **Dogs of the Dow (O'Higgins)**: on January 1 each year, buy the 10 Dow stocks with the highest dividend yield; hold one year; rebalance. Theory: the Dow's lowest-return/highest-yield components will attract buyers as dividends rise, allowing outperformance. **Cited backtest**: 10.8%/yr, 1992-2011, versus the S&P's 9.6%/yr over the same period.
- **Small Dogs variant**: from the same 10 Dogs, buy only the lowest-priced ones (the "puppies") — a further value/mean-reversion tilt within the already-selected high-yield basket.
- **Foolish Four variant (Sheard's refinement)**: sort the Small Dogs by price and the 10 Dogs by dividend yield (both ascending); eliminate whichever stock tops both lists; take the top 4 remaining names from the Small Dogs list.
- **Contrast with Kaufman's own empirical test of the classic theory**: elsewhere in Ch.13 ("Dogging the Dow"), Kaufman tests the standard worst-return-basket version of this same idea directly (not the O'Higgins yield-based selection) and finds it performs *poorly*, while a monthly-rebalanced *best*-return basket outperforms instead — an explicit empirical tension between O'Higgins's yield-based Dogs-of-the-Dow (cited above as beating the S&P) and Kaufman's own return-based test of the same "buy the laggards" premise, which the source does not reconcile (Kaufman Ch.13, Ch.22).

### "Trending or Mean Reverting?" — Kaufman's explicit decision framework for spreads (Ch.13)

Kaufman states directly: market noise is most visible short-term while trends dominate over the long term — a mean-reverting approach exploits noise and works best with short holding periods; a longer-term trend captures sustained divergence. **"Pairs trading, by nature, seeks short-term price distortions and thus succeeds via mean reversion."** A gradual, longer sentiment shift (e.g., investors rotating from small caps to dividend-paying stocks) is better captured via a trend, not a fade (Kaufman Ch.13). This is Kaufman's most explicit general statement on when to apply a mean-reversion vs. trend-following lens to any spread/ratio series.

### Changing volatility in spreads — a mean-reversion-specific risk warning

Kaufman's worked example (emini S&P vs. NASDAQ futures ratio, 2006-2011): a mean-reversion strategy buying at ratio 0.05 and selling at 0.15 worked well in the first half of the period, but during the 2008 crisis, selling at 0.15 would have meant "suffering catastrophic risk"; from July 2009 onward, volatility fell and the ratio no longer even touched 0.15, meaning the strategy would generate signals in a low-volatility regime that may not clear trading costs. **Conclusion, explicit**: relative-value timing needs a companion **low-volatility filter** to reduce trade count and select only trades with sufficient profit potential — and even then, sudden regime jumps will produce losses regardless of method (Kaufman Ch.13).

### Rating-Service Basket Spread — a generalizable ranking-to-spread methodology (Kaufman Ch.13)

A distinct, more general technique from the named pairs/spread systems above: rather than pairing two specific instruments, this converts *any* stock-ranking service — fundamental (e.g., Starmine, which weights valuation, momentum, earnings, and analyst-accuracy-weighted "economic intuition") or a self-built technical ranking (raw/information-ratio returns, or the output of a long-term trend system) — into a systematic long/short basket spread.

- **Basket construction**: use at least 5 stocks (10 preferred) from the top and bottom of the ranking; the combined basket should be no more than 20% of the total ranked universe.
- **Validation step, explicit and prior to trading**: the ranking must first be checked for whether it is genuinely predictive. **IF** the ranking is validated as predictive **THEN** treat it as trend-confirming — buy the top basket, sell the bottom basket. **IF** the ranking is validated as poor or anti-predictive **THEN** treat it as mean-reverting — sell the top basket, buy the bottom basket. This validation is described only as a monitoring/record-keeping discipline (recording rankings weekly and tracking actual outcomes), not a formal statistical test, in the source.
- **Position sizing**: volatility-adjust top and bottom selections using the same dollar-ATR-based, equal-investment-per-stock method as standard pairs trading (see above); only re-adjust the top vs. bottom baskets relative to each other if their volatility diverges by more than 20% — otherwise each new position self-adjusts via its own current volatility.
- **Rebalancing rule**: if a marginal stock (the Nth-best of the top basket, or Nth-worst of the bottom basket) moves out of its basket by 2 or more rank positions, replace it — this avoids overly frequent switching.
- **Filter**: verify the bottom-basket stocks have volatility similar to the top-basket stocks — some low-ranked stocks are ranked low simply because they aren't moving, offering no risk-offsetting hedge value.
- **Ambiguity**: no explicit numeric stop-loss or holding-period rule is given; the entire strategy's viability is conditional on first empirically confirming whether the specific ranking source is predictive, mean-reverting, or pure noise for the instruments being traded (Kaufman Ch.13).

### Position sizing for pairs trades — the volatility-parity method (Kaufman Ch.13)

Equalizing risk between legs is described as critical: trading equal shares of a $5 stock and a $25 stock effectively makes returns depend almost entirely on the $25 leg. **Volatility parity method**: divide a fixed investment (e.g., $1,000) by the dollar value of each leg's 20-day average true range. Worked example: a $5 stock with a $0.25 average range → buy/short 4,000 shares; a $25 stock with a $1 average range → buy/short 1,000 shares — giving both legs an equal chance to contribute to P&L. A simpler, less accurate alternative commonly used by traders: divide the fixed investment by the current stock price (works reasonably well as long as the stock is not trading below $10). Kaufman notes both methods are difficult to improve upon even at the more sophisticated portfolio-allocation level.

### Extreme spread ratios — an explicit failure mode

When the two legs of a spread are badly volatility-mismatched, the spread behaves like an outright position in the more volatile leg and "can actually carry higher risk than an outright position" if both legs move adversely — this defeats the entire purpose of a spread trade (Kaufman Ch.13, explicit closing warning of the chapter's spread-risk discussion).

---

## Short-Term Fade Patterns (Kaufman Ch.15)

Kaufman's Chapter 15 frames pattern trading broadly: "some patterns documented here are best traded as mean-reversion (faded), others as trend-following (joined), and some are ambiguous, left to the reader/trader to classify per market and regime" (Kaufman Ch.15). The chapter is explicitly empirical/statistical (frequency tables across multiple markets and eras) rather than purely rule-based, but several patterns are stated as consistent, tradeable fade signatures.

### Gap fades — the chapter's single most consistent cross-market mean-reversion finding

**Downward-gap mean reversion in futures**: across every one of four futures markets tested (S&P, bonds, crude oil, euro), downward gaps showed a very strong (98-100%) tendency to cross back above the previous close at some point during the session — described by Kaufman as "a systematic intraday mean-reversion signature after gap-downs," more consistent and stronger than the corresponding upward-gap reversal tendency (Kaufman Ch.15). Specific figures: S&P eMini (2009-Apr.2018) — of 118 downward-gap cases, 100% crossed back above the previous close, and none closed lower than the open or between the open and prior close. Bonds (1999-2017) — 100% of downward gaps crossed back above the previous close. Crude oil (Sep.2014-Apr.2017) — 98% of downward gaps crossed back above the previous close ("many commodities resist lower prices," per Kaufman). Euro (Apr.2001-Apr.2017) — 100% of downward gaps crossed back above the prior close.

**Generalized 275-stock study (2000-2017, stocks under $5 excluded)**: upward gaps pull back (retrace from the open) by an average of roughly 40% of the gap size, larger for bigger initial gaps, with the average close ending up very near the opening price. Downward gaps are less frequent than upward gaps (confirming a general upward equity bias), with slightly larger pullbacks, and the average close across all downward-gap sizes is consistently *higher* than the open.

**Gap-Fade/Pullback Trading Rules, derived by Kaufman from the above findings (Ch.15)**:
- For an existing long facing an upward gap: take profit into the gap, wait for the ~40% pullback, then re-enter long.
- For a flat trader wanting long exposure: enter on the pullback to capture roughly 40% of the gap.
- For a downward gap, day trader: buy shortly after the open once volume begins dropping (a sign the sell-off is exhausting); target a rally of about half the gap-down size.
- For an existing long facing a downward gap: exit into a rally of about half the gap, resetting at the close to trim the loss.
- **Filters**: exclude stocks trading under $5 (unusually volatile, distorts results). Because gaps tend to run with the prevailing trend, gap day-trading is suggested as a complement to (not a replacement for) a trend-following core portfolio.
- **Explicit warning against overgeneralizing**: single extreme events can dominate a bucket's statistics — one 9-11% downward Netflix gap rallied 15.32% before closing 16.68% *lower* than the open on the same day. Individual names vary enormously: Micron and Boeing showed some next-day follow-through rather than reversal; Tesla showed "no percentages high or low enough to create trading confidence" despite its dramatic price history — Kaufman's explicit caveat: "not all markets present opportunities."

### The Taylor Trading Technique — an explicitly mean-reverting 3-day cycle (George Douglass Taylor, 1950)

Kaufman categorizes this as "a short-term mean-reverting technique," best combined with a good trend-following method (Kaufman Ch.15). Core mechanism: in an uptrend, prices are expected to cycle through a **Buying Day** (decline to an objective, typically the prior day's or 3-day cycle's low — buy on the test/penetration), a **Selling Day** (close the long at an objective, typically the prior high), and a **Short Sale Day** (prices meet resistance — sell short before an expected reversal), after which the cycle restarts. Order-of-occurrence (whether the day's high or low forms first) is central to Taylor's original method and requires continuous, full-time monitoring.

Taylor's explicit rule that fading against a countertrend requires *faster* reactions: "IF prices rally sharply on the entry day [during a downtrend], THEN close the position at a profit immediately, since time is working against you when countertrend" — an explicit statement that fade trades carry a different risk profile from trend-aligned trades and must be managed with tighter discipline (Kaufman Ch.15).

**Taylor's 3-Day Trading Method** (simplified, computer-programmable version, author's own reduction): buy on the third consecutive lower close, sell short on the third consecutive higher close; exit on the close after a fixed 2-day hold. A 100-day moving-average trend filter was added by the author (restricting fade trades to the direction of the longer-term trend). Backtest on SPY, 2000-Apr.2018: without the trend filter, returns were higher but with much more risk; with the 100-day MA filter, fewer trades but greatly reduced risk. Kaufman explicitly flags this reduction as "unreasonably simple" relative to Taylor's original order-of-occurrence method — most likely to work well on equity index markets and highly liquid futures (e.g., U.S. bonds), and "explicitly flagged as likely to disappoint on individual stocks" (Kaufman Ch.15).

### Named System: Gustafson's Price Persistency Strategy — a consecutive-lower-close Martingale-style fade (Kaufman Ch.22)

A close relative of Taylor's consecutive-close counting logic above, but explicitly long-only and framed by Kaufman within his gambling-theory/Martingale discussion rather than the short-term-pattern chapter. Attribution: Gordon Gustafson, "Price Persistency," *Technical Analysis of Stocks & Commodities* (January 2002); studied on the S&P, 1988-1995.

- **Rules**: enter long after prices close lower 4 days in a row (buy on next open); exit longs after an upward run of 5 days (exit on next open); exit longs unconditionally after 8 days have elapsed since entry, regardless of the run count. The system **only ever takes long positions** — Gustafson's own rationale is that it exploits the stock market's persistent upward bias, which the source notes was "particularly strong in the mid- and late-1990s."
- **In-sample result (1988-1995)**: 78% of trades profitable, $35,030 net profit, $5,847 maximum drawdown.
- **Out-of-sample extension (1982-mid-2001)**: 76% reliability, $348,460 profit, $56,370 drawdown.
- **Explicit author caveat**: the extended test period, despite spanning nearly 20 years, still fell entirely within the same secular bull market — i.e., the strategy has never been validated against a genuine multi-year bear-market regime, a direct instance of the single-regime validation trap this file flags elsewhere (Kaufman Ch.22).

### Weekday/weekend reversal patterns — mixed trend/fade evidence, market-dependent

Kaufman's weekday-pattern study (Jan.2000-Apr.2018, ~823 weeks) found some markets favor *continuation* (heating oil: 5 of 8 high-probability Friday patterns favored continuing Monday's direction) and others favor *reversal* (bonds and S&P: most high-probability patterns favored reversing Monday's direction) — an explicit demonstration that the trend-vs-fade classification is market-specific, not universal (Kaufman Ch.15). The clearest single trend-filter finding: for the S&P across three moving-average filter lengths (30/60/120-day), "Friday is very favorable to the Monday (trend) direction," averaging 55-58% same-direction-as-Monday outcomes.

Weekend-pattern study (six markets, Jan.2000-Apr.2018): all markets except the euro tended to **open Monday in the opposite direction from Friday's move** (a reversal-on-open bias, i.e., an overnight fade), but then **closed Monday in the same direction as the (reversed) open** — meaning the Monday-open reversal persists through the close rather than fully round-tripping. This is a genuinely nuanced fade pattern: the open fades Friday, but the intraday direction from that faded open then trends through the close.

### Reversal-day patterns (classic chart patterns, tested empirically)

Kaufman tests three formations across 8 markets, comparing an older (2000-2011) sample to a newer (2009-2018) one: (1) trend-continuation days, (2) classic **reversal days** (higher high but lower close in an uptrend, or the mirror), and (3) **outside reversal days** (a more extreme version — yesterday's high exceeded the prior high AND yesterday's close was below the prior low, or the mirror). The newer sample shows bull-market persistence pulling several markets' continuation rates up (S&P, Amazon, Exxon) — but **10-year T-notes showed a strong tendency (well into the 50s%) to follow through on downward reversals in both tested periods**, an unexpected, genuinely contrarian finding given the underlying multi-decade bond bull market, interpreted by Kaufman as evidence that "even in a bull market not every day is up" (Kaufman Ch.15).

### Day-of-month institutional-flow patterns — a fade/reset dynamic at month boundaries

Kaufman's day-of-month study (2010-2018) found bonds show the chapter's "most reliable" monthly pattern: clear selling at the start of the month (a fade opportunity against that early weakness for buyers) and clear buying concentrated in the last five trading days, peaking on the third-from-last day at roughly 50% above-average volume — attributed to well-defined, non-discretionary institutional rebalancing flows (Kaufman Ch.15).

### Breadth as a contrarian/fade indicator (Connors AD-Ratio System — cross-referenced from Ch.12, directly relevant to the fade paradigm)

Larry Connors ("Fade the Breadth," *Futures*, January 2005), cited by Kaufman: most literature treats market breadth (the advance/decline ratio) as trend-*confirming*, but Connors trades the AD ratio as a **mean-reversion** signal, arguing equity indexes — and breadth itself, as an aggregate of many individual stock moves — tend to be mean-reverting due to a large amount of price noise (Kaufman Ch.12, cross-referenced in Concepts.md as "a direct methodological disagreement within the chapter rather than a settled consensus"). Rules: sell the index when the AD ratio exceeds a high threshold, buy when it falls below a low threshold (exact numeric thresholds are an extraction gap); exit after 5 days unless a reverse signal occurs first. Supporting statistical findings, all from the same Connors source (1996-2003 sample, spanning extreme bull and bear conditions): if declining NYSE stocks exceeded advancing NYSE stocks for ≥3 consecutive days, the S&P averaged a +0.50% gain the following week; the *opposite* condition in all tested cases showed essentially no gain the following week.

### CHADTP (Conners-Hayward Advance-Decline Trading Patterns) — a related but distinct breadth-reversal system (Kaufman Ch.12)

Attributed to Laurence A. Conners and Blake E. Hayward, *Investment Secrets of a Hedge Fund Manager* (1995). CHADTP is a *separate, more mechanically complete* pattern-reversal system from the Connors AD-Ratio System above — both trade NYSE breadth as a mean-reversion signal, but CHADTP builds its own smoothed indicator and pairs it with an explicit S&P price-penetration trigger rather than trading the raw AD ratio directly.

- **Construction**: (1) sum the past 5 days of NYSE advancing issues; (2) sum the past 5 days of NYSE declining issues; (3) subtract (2) from (1); (4) divide by 5 for the average daily value — this is CHADTP.
- **Extreme thresholds**: the original 1995 rule used fixed levels of **±400**. Kaufman's own modernization instead scales the threshold to a number of standard deviations of CHADTP computed over the trailing 60 days (exact SD multiplier is an extraction gap in the source).
- **S&P point-penetration trigger**: entry additionally requires the S&P futures to trade a threshold number of points (T_SP) beyond the previous day's high/low, where T_SP itself must scale with the index level — originally 10 points when the S&P was at 460, with Kaufman estimating roughly 25 points once the S&P reached 2800 (a rounded estimate, not a precisely derived ratio).
- **Entry rules**: sell short when CHADTP exceeds its positive extreme threshold **AND** S&P futures trade T_SP points below the previous day's low; buy when CHADTP is below its negative extreme threshold **AND** S&P futures trade T_SP points above the previous day's high. The oscillator itself does not need to make a new extreme on the actual signal day.
- **Confirmation**: signal quality is considered best when it coincides with news commentary describing "depressed volume," or actual volume meaningfully below its 3-month average — interpreted as sideline cash ready to re-enter the market.
- **Exit rules**: targets a 5- to 7-day holding horizon; a drop of the oscillator back into its midrange is treated as an exit opportunity, a standard price oscillator can supply its own overbought/oversold exit within that window, and an opposite entry signal reverses the position.
- **Ambiguities**: the exact standard-deviation multiplier for the modernized threshold and the precise T_SP-to-index-level scaling relationship are not given as an exact formula in the source — only the two anchor data points (10 pts @ S&P 460, ~25 pts @ S&P 2800) are preserved (Kaufman Ch.12).

---

## Band and Channel Fades (Kaufman Ch.8/9/15/18)

### Bollinger Bands — both a trend-confirmation and a mean-reversion tool, explicitly dual-use

Kaufman is explicit that Bollinger Bands are used in genuinely opposite ways depending on the trader and context, and does not present one as more "correct" than the other:

- **Reversal (fade) variant, always in market** (Kaufman Ch.8): buy (close shorts, go long) when price closes *above* the upper band; sell short (close longs, go short) when price closes *below* the lower band. This is a breakout-following, trend-confirming interpretation — note this is the *opposite* of what "fading a band" might naively suggest; it treats a band penetration as continuation, not reversal.
- **Trendline-exit variant**: same entry logic, but exit when price closes back below/above the trendline (band center) rather than reversing directly into the opposite side. Kaufman notes this variant risks "a same-day entry-then-exit" if bands are narrow, and using intraday high (longs)/low (shorts) as the trigger in a trending market "should produce extra profits."
- **Bollinger's own counter-trend usage, explicitly attributed to John Bollinger himself**: "standard use is mean-reverting (counter to price direction), which is risky in volatile conditions." Bollinger recommends confirming a downside penetration with volume/breadth indicators — if price falls but volume isn't rising and negative breadth doesn't confirm, a buy (fade) is realistic (Kaufman Ch.8, Strategies.md). Bollinger treats volatility as cyclic without a regular period ("extreme seeking" — low volatility forecasts high volatility and vice versa) and recommends selling a major rally once bandwidth (which expanded during the rally) begins to narrow — stated by Kaufman as applying only to upward moves.
- **The "Squeeze" variant**: wait for band compression to some percentage of average width (e.g., 50%) then trade the *breakout* through the bands — explicitly a trend/breakout play, not a fade, and Kaufman notes trading with the prevailing trend improves results here (see also `04_breakouts.md` and the volatility file for band-squeeze construction).
- **Statistical caveat**: because prices are not normally distributed, the standard "2 standard deviation" Bollinger Band equates to only ~87% empirical confidence, not the ~95.4% a true normal distribution would imply (Kaufman Ch.8, Ch.18).

### Bollinger Bands as a price-distribution / overbought-oversold framework (Kaufman Ch.18)

Kaufman's price-distribution chapter reiterates that a 2-SD Bollinger Band "should normally enclose ~95% of data, so a penetration signals strength/weakness/outlier — traded either as directional confirmation or as a mean-reversion setup" — again explicitly presenting both interpretations side by side without declaring one superior (Kaufman Ch.18). A 21-period vs. 65-period Bollinger Band comparison (relative 1-month vs. 3-month volatility) is suggested: the thicker (65-period) band crossing the shorter-term band flags relative overbought/oversold conditions, usable as a fade signal at a longer horizon.

**"Avoiding the Bulge" — a structural lag problem in any band-based fade system** (Kaufman Ch.18): any rolling n-bar standard-deviation band lags in both directions — it widens only *after* a volatility spike has already occurred, and narrows only slowly as high-volatility days age out of the window. Kaufman's proposed fix: lag the *data* used in the standard-deviation calculation (compute the n-day SD from an *offset* window, excluding the most recent days) so that a current high-volatility day is more likely to be correctly flagged as "unusual" against a band that has not yet absorbed it. **General principle stated**: to identify genuinely unusual volatility (and thus a genuine fade opportunity vs. a band that has already widened to accommodate the move), compare current volatility to a longer-term measure, a lagged measure, or both.

### Adaptive Price Zone (APZ) — an explicitly mean-reversion-labeled band (Leibfarth, 2006; Kaufman Ch.8)

Contrasted directly against trend-following bands in the same chapter section: APZ uses a double-smoothed exponential trendline with an "adaptive range" volatility measure (5-day EMA of the 5-day EMA of the daily high-low range). **Entry signal**: bands touching/expanding to meet the day's highs and lows as volatility increases is read as a mean-reversion opportunity — the band's expansion itself, rather than a fixed penetration threshold, is the fade trigger (Kaufman Ch.8).

### Jackson's Intraday Zones and related zone systems — explicit mean-reversion-within-noise framing (Kaufman Ch.18)

J. T. Jackson's 6-zone intraday system (relative to yesterday's daily High/Low/Close) is applied by Kaufman with an explicitly mean-reversion-within-noise entry logic: "sell short when price moves into Zone 4 (mildly up) with a stop if price enters Zone 5"; treating the middle zones (3-4-5) as largely noise, "sell at the top of Zone 4 and cover near the Zone 4 average (or buy near the bottom of Zone 3 and exit near the average) to capture the majority of price moves that have no direction" (Kaufman Ch.18) — an explicit statement that this is a fade-the-noise, not fade-the-trend, strategy. Kaufman notes the strategy works best when the actual zone-frequency distribution deviates from a theoretical random baseline (a perfectly random 7%-14%-28%-28%-14%-7% distribution implies no profit potential); higher central clustering than the random baseline favors the fade approach with more frequent (if not necessarily larger) wins.

The related **Scorpio ATR-based Zones** system (Kaufman Ch.18) uses the same "mean-reverting on intraday data or absent a clear trend; trend-following on daily data or with a well-defined trend" rule — i.e., Kaufman applies the same zone-fade logic across multiple zone-construction methods (Jackson's H/L/C-based zones, the Chande & Kroll volatility-projected zones, and the ATR-based Scorpio zones), treating "trade the middle zones as reverting noise" as a general-purpose template rather than a single named system.

### Gould's Long-Term Price Zones — a slow, multi-year fade framework (Bruce Gould; Kaufman Ch.18)

Divides historic prices into 5 zones, each 20% of the 3-year price range. **Rule**: selling in Zone 1 (lowest) or buying in Zone 5 (highest) offers little profit opportunity; selling in a higher zone or buying in a lower zone increases opportunity while reducing risk, "especially given the likelihood of eventual sideways/reverting behavior" (Kaufman Ch.18) — an explicitly long-horizon, investor-oriented fade framework, contrasted with the intraday zone systems above.

### Divergence Index (DI) — a self-adjusting alternative to MACD's fixed threshold (Kaufman Ch.9)

A MACD-like indicator that is the volatility-adjusted difference between two moving averages (e.g., 10- and 40-day). Unlike MACD's fixed threshold levels (which Kaufman flags as prone to overfitting when hand-tuned to historical data), the DI's band = k × standard deviation of DI itself, self-adjusting to volatility changes. Trading rules: buy when DI moves below the lower band while the slow average is in an uptrend; sell when DI moves above the upper band while the slow average is in a downtrend; exit on a DI crossing of zero. This is presented by Kaufman as a structurally superior alternative to MACD's fixed-threshold-band problem, directly relevant to the same "changing volatility breaks fixed fade thresholds" theme raised in the oscillator-fade section above.

### Fisher Transform — designed specifically to avoid the "stuck at extremes" fade-timing problem (Ehlers, cited in Kaufman Ch.13/Indicators.md)

Structurally similar to a stochastic but designed to avoid getting "stuck" at extremes for extended periods (a known problem for fade-timing tools generally, since a fade entered too early into a still-extending extreme can suffer large losses). Full range +1 to −1 (or +100 to −100), with recommended overbought/oversold thresholds of about +80 and −80. **Worked application** (platinum/gold ratio, 1 year from March 2010): when the Fisher-transformed ratio peaks above 80, sell platinum/buy gold; close out when the ratio nears zero (return to normal). Kaufman notes the Fisher Transform "is noted to move quickly between overbought/oversold levels" in this application, i.e., it resolves faster than a raw stochastic would — directly addressing the "plateau and hold" weakness that plain oscillators exhibit during strong trends per the source's own commentary elsewhere (Kaufman Ch.13, cross-referencing Ehlers' Hilbert Transform commentary on sharp cyclic peaks being "advantageous for mean-reversion-style entries").

---

## Hilpisch: A Worked Vectorized Mean-Reversion Example (Brief Cross-Reference)

Hilpisch's *Python for Algorithmic Trading* includes a simple SMA-distance mean-reversion strategy, included here briefly because it illustrates the same core paradigm (fade deviation from a rolling mean) in a different, code-first idiom, with an explicit transaction-cost failure case worth noting alongside Chan's parallel warning above.

- **Mechanism**: `distance = price - SMA`; go long when `distance < -threshold` (price too far below trend), go short when `distance > threshold` (long-short version only); close to neutral when `distance` crosses back through zero (price re-crosses its own SMA) (Hilpisch Ch.4/Ch.6).
- **Assets**: GDX and GLD (gold-linked ETFs), chosen because the author expected "significant mean reversion" for gold-related instruments — an explicitly stated but not independently validated rationale.
- **Parameters used**: SMA=25/threshold=3.5 for GDX; SMA=43/threshold=7.5 for GLD — described as hand-picked/illustrative, with no formal grid-search optimization shown for this strategy (in contrast to Hilpisch's SMA-crossover strategy, which does use `optimize_parameters()`).
- **Transaction-cost fragility, directly echoing Chan's warning**: in a Ch.6 event-based AAPL comparison, the mean-reversion strategy's no-cost performance (+439.08%) collapsed hardest of three compared strategies under transaction costs, down to +53.75% (with $10 fixed + 1% proportional costs) — the largest relative cost erosion of the three tested strategies.
- **A distinct, more severe failure mode noted**: the long-short version, combined with wrong-direction shorts and margin dynamics, produced a debt/negative-equity outcome (−151.11%) in one shown configuration — used by Hilpisch as a real-world CFD-margin cautionary tale, not merely a return-erosion example.
- **A genuine success case, also noted**: the GLD example (Ch.4) outperformed even after 0.1% transaction costs (ending $13,542 vs. a benchmark, +$646.21 outperformance) — the only one of Hilpisch's three core strategies (SMA, momentum, mean-reversion) shown to survive transaction costs positively in its highlighted example.
- **Explicit limitation**: threshold units are absolute price-distance, not normalized (not in standard deviations or percentage terms), which Hilpisch does not address — this makes cross-instrument comparison and out-of-sample robustness unclear, a much less rigorous calibration approach than either Chan's O-U/CADF pipeline or Kaufman's ATR/standard-deviation-based band constructions above.

---

## Synthesis: Where the Sources Agree and Disagree

- **All three books agree** that mean reversion is a real, exploitable phenomenon under the right conditions, but each flags it as fragile: Chan emphasizes that stationarity/cointegration can silently break down; Kaufman emphasizes that fixed thresholds break down as volatility regimes shift and that fading intrinsically carries higher risk than trend-following; Hilpisch's own worked examples show the mean-reversion strategy suffering the single worst transaction-cost erosion among the strategies he tested.
- **Chan and Kaufman diverge sharply on rigor vs. accessibility.** Chan treats cointegration testing (CADF) as close to mandatory before trading a pair, and builds a formal statistical exit-timing model (O-U half-life) around it. Kaufman validates simpler correlation-band and momentum-difference approaches as historically successful in their own right, and presents cointegration as the most rigorous but least accessible of three valid methods — "traders have been successful at pairs trading long before cointegration was known" (Kaufman Ch.13).
- **Both books agree, independently, on the "never fully trust a fixed threshold" lesson**, arrived at via different routes: Chan via the transaction-cost collapse of the Bollinger Band ES example (Sharpe 3 → −3) and via warning that cointegration itself is not guaranteed to persist; Kaufman via the "changing volatility" critique of fixed momentum/oscillator bands and via the explicit low-volatility-filter requirement for relative-value spread trades.
- **Both books agree that stop-losses interact awkwardly with mean-reversion logic**, though for related but distinct reasons: Chan argues a reversal model will *never itself recommend* a stop-loss because a further adverse move only strengthens the same signal; Kaufman states more generally that fading carries "considerably greater risk than trading in the direction of the trend" and that any aggressive (unconfirmed) fade entry has no natural stop-placement logic at all, requiring the trader to impose one externally.
- **A genuine open question, left unresolved across all sources**: none of the books give a systematic, validated method for detecting *in advance* when a cointegrated pair, a fade threshold, or a mean-reverting regime is about to break down structurally — Chan explicitly defers this to "periodic re-testing" without a specified cadence; Kaufman defers to volatility filters and regime-dependent judgment; Hilpisch does not address it at all.
