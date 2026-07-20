# Momentum, Oscillators, and Time-Series Momentum

This file covers the momentum/rate-of-change family of indicators and the oscillator family built on them (Kaufman Ch.9), Chan's statistical/regime framing of momentum versus mean reversion (Chan Ch.2, Ch.7), and Hilpisch's vectorized time-series-momentum implementations (Hilpisch Ch.4). It focuses on indicator mechanics, formulas, standard parameters, and the native trading rules attached to each indicator. Many of these same oscillators are also the engines behind dedicated contrarian/fade systems — see 03_mean_reversion.md for those. Where ROC/TRIX or momentum crossovers are used purely as trend filters rather than overbought/oversold tools, see 02_trend_following.md. For Kaufman's Efficiency Ratio and related "is this market trending or noisy" diagnostics, see 01_market_structure.md.

## Framing: What Momentum Is (Kaufman Ch.9)

Momentum and oscillators analyze price *changes* rather than price *levels*. Momentum is the speed/rate of price movement — conceptually the slope of a least-squares regression fit to price. Kaufman frames this with a loose restatement of Newton's First Law: "once started, prices tend to remain in motion at about the same speed and in more-or-less the same direction." Momentum and oscillators serve as **leading indicators** of price direction: they can show a trend losing strength (still rising, but at a slower rate) before the trend actually reverses, giving an early-liquidation opportunity (Kaufman Ch.9).

Shorter calculation periods make momentum more sensitive to small price changes, and short-period momentum is then typically used as a **countertrend/mean-reversion** tool to flag overbought/oversold conditions (see 03_mean_reversion.md for the systems built on this). The change in momentum — acceleration — is even more sensitive and anticipates change sooner than momentum itself. First differences (today's price minus yesterday's) and second differences can substitute for momentum and acceleration respectively (Kaufman Ch.9).

A single price level (e.g., gold at $1,400) has no implied direction; speed requires a stated time interval — this is what a momentum value expresses (Kaufman Ch.9).

## Basic Momentum and Its Properties (Kaufman Ch.9)

**Formula**: n-day momentum, `M(n)_t = p_t − p_[t-n]` (today's price minus the price n days ago).

- Ranges from the maximum possible upward move to the maximum possible downward move over n days; zero if price is unchanged over the period.
- **Momentum is not the same as volatility.** Example given: gold moves $1200→$1250 in two days then back to $1200 over the next three days — momentum over the 5-day window is zero, but volatility (range of movement) was high. When prices continue moving in one direction, momentum and volatility become the same thing (Kaufman Ch.9).
- **Direct crypto mention (verbatim from source, also logged to Crypto_Specific.md by the extraction):** "In cases such as Enron, or even Bitcoin, prices could collapse to zero in short order" — raised in the context of stocks/futures with no price floor.
- Higher-priced instruments generally show proportionally larger absolute price moves: gold's 5-day momentum reached $200/oz when gold was at $2,000 (Sept 2011) vs. only $3/5-days when gold was at $250 (Aug 1996) (Kaufman Ch.9).

### Pattern of Change and Leading-Indicator Behavior

On a smooth synthetic 15-day price cycle, momentum peaks (largest positive change) occur where price is rising fastest — not at the price peak itself — and momentum crosses zero when the n-day price change is zero, which typically precedes the actual price peak/trough. If prices moved in perfectly smooth cycles, momentum would be a perfect leading indicator; real price movement is irregular, so momentum values are irregular too. Double smoothing (TSI, TRIX — see below) makes anticipating direction changes more practical (Kaufman Ch.9).

Momentum does not carry a moving average's inherent lag — it can peak at about the same time as price (e.g., 40-day momentum vs. 40-day MA on Raytheon), while a faster momentum (20-day) can lead the price peak. The cost of this leading property is more noise/erratic pattern versus a smooth trendline. Momentum divergence (price makes new highs, momentum does not) is the basis for the dedicated Divergence Analysis section below (Kaufman Ch.9).

### Momentum as a Trend Indicator

Basic rule: sell when momentum turns negative, buy when it turns positive, with a small band around zero to reduce noise-driven whipsaws (sell below the lower band, buy above the upper band). **Momentum crossing zero is functionally identical to an n-day moving average of the same period turning up/down**, since today's price compared to price n days ago is exactly what an n-day MA turn represents. Kaufman notes his own Ch.8 testing found trend and momentum systems of the same calculation period gave very similar performance (Kaufman Ch.9).

Longer calculation periods make momentum smoother and more trend-like, since net change over n days ignores intermediate fluctuations; buy when momentum turns from negative to positive, sell on the opposite. **Calculation-period selection heuristic**: identify significant chart tops/bottoms, measure the average number of days between cycles (peak-to-peak or valley-to-valley), then use ½ or ¼ of that cycle length as the momentum calculation period — "these natural cycles will often be the best choice" (Kaufman Ch.9).

### Momentum of Returns (Percentage Momentum)

`%M = (p_t − p_[t-1]) / p_[t-1]` for one day, generalized to n-day: `%M(n) = (p_t − p_[t-n]) / p_[t-n]`. **Warning**: percentage momentum does not work correctly for back-adjusted continuous futures data (the adjustment distorts old prices) or for split-adjusted stock data with the same problem — use price differences instead for those series (Kaufman Ch.9).

### Momentum as Price Minus Trend ("Relative Strength")

"Momentum" is also commonly used to mean price minus a corresponding moving-average value (rather than price minus price n days ago) — larger values mean price is diverging from the MA, values toward zero mean converging. Kaufman notes this is also called **relative strength** (measured relative to a previous price or to a trendline) — explicitly **not to be confused with Wilder's RSI** discussed below. On a three-panel comparison (20-period MA / momentum / price-minus-MA, Intel), the price-minus-trendline version has a smaller value range and appears to have less lag than standard momentum, because the trendline itself already lags price (Kaufman Ch.9).

### Timing an Entry Within a Longer Trend

Momentum is convenient for timing entries within a longer trend: use a much shorter momentum period (e.g., 6 days) alongside a longer trend (30-50 days) to catch frequent overbought/oversold pullbacks within the trend. **Rule**: on a new trend buy signal, wait for the short momentum to turn negative before entering — the greater the negative momentum, the better the entry (but waiting risks missing the trade entirely). This is cross-referenced by Kaufman to his Ch.19 and to Raschke's First Cross (covered below) (Kaufman Ch.9).

### Identifying and Fading Price Extremes — Threshold Bands

Momentum's positive/negative peaks are bounded by the maximum possible price move over the calculation period N. **Overbought** = a sustained upward trend at a fast rate for most of N days (expect a downward reaction or at least a slowdown); **oversold** is the mirror condition. Faster momentum periods fluctuate frequently above/below zero (small price changes); longer periods behave like a trend and stay on one side of zero for the trend's duration. Note: an n-day momentum's range does **not** scale linearly with n (a 3-day momentum is not 3/20ths of a 20-day momentum), because volatility itself does not increase linearly over time (Kaufman Ch.9). This overbought/oversold fading logic overlaps directly with the contrarian systems in 03_mean_reversion.md.

Two horizontal lines are drawn above/below zero to isolate tops/bottoms of major moves, selected by one of three methods (Kaufman Ch.9):
1. Visually, from prior values, so penetration tends to precede a reversal.
2. As a percentage of the maximum possible momentum value.
3. A multiple of the standard deviation of momentum values (2 std devs → only ~5% of values penetrate above/below the two lines).

**Entry rule variants**, aggressive to most confirmed (Kaufman Ch.9):
- **Aggressive**: enter long when momentum crosses the lower bound; short when it crosses the upper bound.
- **Minor confirmation**: enter short on the first day momentum turns down after crossing the upper bound (mirror for longs).
- **Major confirmation**: enter short when momentum crosses back below the upper bound while moving lower (mirror for longs).
- **Timing**: enter short after momentum has remained above the upper bound for n days, or after a confirmation has occurred (mirror for longs).

**Exit rule variants**, symmetric long/short (Kaufman Ch.9):
- **Most demanding**: exit when momentum crosses the opposite threshold used for entry (e.g., entered short at +50, cover at −50).
- **Moderately demanding**: cover when momentum crosses zero minus one standard deviation (std dev computed on the *changes in* momentum, not momentum values themselves).
- **Basic exit**: cover when momentum crosses zero.
- **Allowing an extended move**: cover when momentum crosses zero moving up after having penetrated it moving down (effectively using momentum as a short-term trend).

### The Changing-Volatility Problem With Fixed Momentum Bands

Kaufman illustrates via S&P 20-day and 3-day momentum (2005-2011) that momentum's scale is unstable over time: bands appropriate in a low-volatility year (e.g., ±30 for 20-day momentum in 2006) become far too tight once volatility rises (2007-2008), producing large open losses if bands aren't widened (e.g., needing ±75, then ±100/±50); after volatility subsides, static wide bands then produce too few signals. **General finding: the scale of a fixed-band momentum system is unpredictable** — it needs dynamic adjustment (cross-referenced to Ch.8 volatility bands) or a bounded way of measuring momentum, i.e., an oscillator (Kaufman Ch.9). This is the direct motivation for normalizing momentum into oscillators (see below).

### Risk Protection on Momentum Trades

A protective stop-loss should be used whenever trading opposite to current momentum (fading), especially for the **aggressive entry** variant, which has no natural stop-placement logic — the trader must set risk based on historic momentum/volatility. For more-confirmed entry variants (price is no longer at an extreme when entered), stops can be placed above/below the most extreme high/low momentum value, as a trailing stop on momentum points or price volatility, or via equal-spaced "zones" acting as interim profit levels that disallow reverse penetration once a new zone is entered. **Key caution**: both profit targets and risk on extreme-entry trades must scale up with rising volatility/price levels (Kaufman Ch.9).

**Empirical test result (aggressive entry)**: a computer test accidentally coded backward (bought on upper-bound crossing with a stop below entry — trend-following, not fading) still produced outstanding, consistent profits. Kaufman reads this as incidental proof that high-momentum periods persist long enough to capture small consistent profits, and that an aggressive countertrend entry anticipating an early reversal would be a losing strategy. Reminder: declining momentum while still above zero does not mean prices are falling — only that they are rising more slowly (Kaufman Ch.9).

**The Trend Provides Protection**: when momentum is used only as an entry/exit timing tool within a trend-following strategy (not as the strategy itself), a new trend signal is not entered immediately — the strategy waits for a short momentum (e.g., 3-day) to penetrate the opposite band. If price continues adverse instead, the trend itself flips and the position exits via the trend signal — a separate stop-loss should not be necessary in this configuration (Kaufman Ch.9).

**Exiting countertrend trades**: for pure mean-reversion trades (short entered at a momentum high, long at a low), the most reasonable exit is when momentum returns to near zero. Win rate can be increased by targeting a more conservative exit (5-10% short of zero) at the cost of smaller average profit; targeting the opposite side of zero increases average profit per trade at a lower win rate. Effectiveness of early vs. late profit-taking depends on the noise level in the momentum series (Kaufman Ch.9) — see 03_mean_reversion.md for the fuller contrarian-system treatment.

**High-momentum trading**: some professional traders trade purely in the direction of a fast price move once momentum exceeds a high threshold, rather than anticipating reversal — a small, fast (minutes-to-hours, occasionally a few days) window requiring wide-market scanning tools and continuous screen-watching, called "a full-time commitment," attributed partly to the rise of day trading (Kaufman Ch.9).

## MACD — Moving Average Convergence/Divergence (Kaufman Ch.9)

**Source**: developed by Gerald Appel; standard parameters are 12-day and 26-day exponential smoothing plus a 9-day smoothing of the MACD line for the signal line, though the book's worked illustrative example uses 20/40/9.

**Construction** (worked steps, illustrative 20/40 example):
1. Choose two trend calculation periods (e.g., 20 and 40 days); convert to exponential smoothing constants via `α = 2/(n+1)`.
2. Slow trendline E40, smoothing value 0.0243 (≈2/(40+1)).
3. Fast trendline E20, smoothing value 0.0476 (≈2/(20+1)).
4. MACD line = E20 − E40 (positive when the market is moving up quickly).
5. Signal line = 9-day EMA of the MACD line (smoothing constant 0.10); this lags the MACD line.
6. Histogram = MACD line − signal line; histogram above zero confirms the uptrend.

**Trading the MACD**:
- Basic trend rule: buy when MACD crosses above the signal line; sell when it crosses below.
- **Problem**: many crossings are false/whipsaw signals in a sideways market.
- **Threshold refinement**: require MACD to first penetrate an outer band (book's AOL example uses ±2.00) before a crossing counts as valid — sell signals only after MACD has been above +2.00, buys only after it has fallen below −2.00. **Explicit caveat**: fitting these threshold lines to historical data makes them unreliable for live trading (overfitting risk); Kaufman offers "An RSI Version of MACD" as an alternative.
- Appel preferred 19- and 39-day periods for the NASDAQ composite.
- MACD is also central to divergence analysis (see Divergence Analysis section below).

### Volume-Adjusted Momentum Variants (Kaufman Ch.9)

Kaufman also documents several ways of adding volume to raw momentum, distinct from the pure oscillator family but conceptually adjacent:
- **Momentum-Volume (MV)**: `MV = (close − close[n]) × average(volume, n)`.
- **Percentage Momentum with Volume**: `%MV = average(volume,n) × (close − close[n]) / close[n]`.
- **TRMV** (scaled by true range): `TRMV = average(volume,n) × (close − close[n]) / avgtruerange(p)`; a longer 20-65 day calculation period is recommended for stability given volatility's own cyclicality.
- **Money Flow** (cited to Gene Quong and Avrum Soudack, "Volume-Weighted RSI: Money Flow," 1989): a positive/upward day is one where today's average of (high, low, close) exceeds the previous day's average; each day's average multiplied by volume gives daily money flow, and a 14-day ratio of these produces the Money Flow Index. **Flagged gap**: the exact combining formula beyond this description is not recoverable from the extraction (an embedded graphic that did not extract).
- **Herrick Payoff Index (HPI)** (from the CompuTrac manual): combines volume AND open interest to produce an unbounded (not 0-100) indicator. Formula as given in source:
  ```
  HP = BigPointValue*volume*((high-low)/2 - (high[1]-low[1])/2)*
       (1 + (((high-low)/2 - (high[1]-low[1])/2) /
       absvalue((high-low)/2 - (high[1]-low[1])/2))*2*
       (absvalue(opint - opint[1])/lowest(opint,2)))
  HPI = smoothedaverage(HP,19)
  ```
  Smoothing factor s = 0.10 (≈19-day smoothed average); most analysts scale HPI down by dividing by 100,000. Larger positive/negative HPI clusters tend to appear ahead of price turning points.
- **Divergence Index (DI)**: a MACD-like, volatility-adjusted difference between two moving averages (example: 10- and 40-day), with `band = k × stdev(DI)` self-adjusting to volatility (unlike MACD's fixed threshold). Rules: buy when DI moves below the lower band while the slow average is in an uptrend; sell when DI moves above the upper band while the slow average is in a downtrend; exit on DI crossing zero.

## Oscillators — the Normalized/Bounded Momentum Family (Kaufman Ch.9)

Oscillators are distinguished from raw momentum by being **normalized/bounded** (e.g., −1 to +1, 0 to 1, or 0 to 100). To transform standard momentum into a bounded oscillator, divide by its own maximum possible value (positive or negative, taken as positive) over the same rolling period — this makes the oscillator self-adjust to changing price/volatility levels. Example: Amazon's 10-day range was $16.63 in Feb 2011 vs. $140.73 in July 2018 — a raw $5 move meant 30% of the 2011 range but would need $42.21 to represent the same 30% of the 2018 range. Normalization is the basis for most of the oscillators below (Kaufman Ch.9).

## RSI — Relative Strength Index (Kaufman Ch.9)

**Source**: J. Welles Wilder, Jr., *New Concepts in Technical Trading Systems* (1978).

- **Purpose**: overbought/oversold indicator, more stable than raw momentum since it uses *all* values across the calculation period, not just first/last.
- **Formula (as given in source)**: `RSI = 100 − 100/(1+RS)`, where `RS = AU/AD`; AU = total of upward price changes over the past 14 days, AD = total of downward price changes (as positive numbers) over the past 14 days. Daily updates use an average-off method (subtract the average value, add the new value — cross-referenced by Kaufman to his Ch.7 "Average-Modified/Average-Off Method").
- **Calculation period**: Wilder favored 14 days (half of a natural monthly cycle). **Thresholds**: 30 (oversold, imminent upturn) and 70 (overbought, pending downturn).
- **Wilder's own top/bottom formations**: buy signal when a second RSI low is higher than the first low, then RSI moves above the peak of the rally between the two lows; mirror sell signal. Also called a **failure swing** or divergence.
- **Calculation-period trade-off**: too short a period → RSI stays outside the 70/30 zone for extended stretches rather than giving a timely turn signal; the goal is a period for which sustained moves rarely exceed the period length. Shorter periods (e.g., 10) paired with wider zones (80/20) give more frequent signals.
- Wilder also created ADX (Average Directional Movement) as a byproduct of Directional Movement — full treatment deferred by Kaufman to Ch.23 (see 02_trend_following.md for trend-filter material).

### RSI Countertrend Trading (Jump-Trigger Variant) (Kaufman Ch.9)

Instead of only using the absolute RSI threshold, trigger on a large 1-day RSI jump: sell when `RSI_t − RSI_[t-1] > D` (some threshold), or buy on the mirror condition, regardless of RSI's absolute level — similar in spirit to a gap-opening signal but can occur at any time. Increases trade frequency when combined with standard threshold entries. Exits at momentum returning to near zero, or after n days. This is a mean-reversion-flavored variant — see 03_mean_reversion.md.

### Net Momentum Oscillator (Kaufman Ch.9)

**Source**: cited to Tushar Chande and Stanley Kroll, *The New Technical Trader* (1994). A variation on RSI using the **difference** (not ratio) between the sum of up-day changes and down-day changes: `NetMomentum = AU − AD` (unsmoothed). Recovers extremes lost to RSI's smoothing; an equivalent effect can be had by shortening RSI's calculation period.

### Forecast Oscillator (Chande) (Kaufman Ch.6)

**Source**: Tushar Chande. A regression-residual momentum oscillator built directly on the chapter's linear-regression machinery (cross-ref `13_indicator_reference.md` Linear Regression entry) rather than on price differences.
- **Calculation**: using a 5-day linear regression of closing price, compute %F = today's residual (actual close minus the regression-forecast value) expressed as a percentage variation from the regression line; %F₃ = a 3-day moving average of %F.
- **Entry Rules**: buy when %F crosses above %F₃; sell short when %F crosses below %F₃.
- **Underlying assumption**: the residuals themselves trend — i.e., a residual-momentum premise, distinct from Chapter 6's other regression-based systems (which trade the *forecast* directly rather than the *forecast error*).

### 2-Day RSI (Kaufman Ch.9)

**Source**: Michael Stokes, MarketSci Blog (Dec. 9, 2008 posting). Replace each 1-day closing-price change with a 2-day change (`q_t = close_t − close_[t-2]`, overlapping 2-day data), then run standard RSI on the q series. Result: smoother than a straight 1-day RSI, but with higher overall volatility of the RSI series itself, since 2-day price moves are naturally larger.

- **Stokes's simple rules (S&P)**: buy on next close when the 2-day RSI penetrates 10 moving lower; sell short on next close when it penetrates 90 moving higher; exit one day later on the close.
- **Historical finding cited**: RSI(2-day, S&P) behaved as a good *trend* indicator from 1970-1998 (RSI above 90 → S&P continued up) but reversed into a *mean-reverting* indicator after ~1998.
- **Scaling-in variant** (from the same blog):

  | RSI condition | Buy % | RSI condition | Sell-short % |
  |---|---|---|---|
  | <5 | 100% | >95 | 100% |
  | <10 | 75% | >90 | 75% |
  | <15 | 50% | >85 | 50% |
  | <20 | 25% | >80 | 25% |

  Exit rule (Stokes's, considered safer than waiting for RSI to cross 50, since 2-day RSI can stay pinned above/below 50 for long stretches): exit one day later on the close. **Ambiguity flagged in the source itself**: unclear whether adding to a position on a further RSI extreme the next day (e.g., 50%→75% add) implies unwinding logic if no further add occurs the next day — the book states it assumes exit if no add occurs on the next day.
- Book's own caution: 1-day-holding-period trades are highly sensitive to commissions/slippage — check per-share/per-contract returns cover costs.

This entire 2-Day RSI system is explicitly contrarian/fade in character and overlaps heavily with 03_mean_reversion.md.

## Stochastics (Kaufman Ch.9)

**Source**: George Lane.

- **Concept**: measures the relative position of the close within the recent high-low range, on the premise that closes resist penetrating recent highs/lows (support/resistance) and that a breakout of those levels predicts continuation. Conceptually distinct from MACD (difference of two trends) and RSI (uses only closes, weighting up/down moves) — stochastics use the full high-low range and require no inherent smoothing lag, though a smoothed version is commonly used.
- **Three lines**: %K (raw stochastic, unsmoothed), %D (3-day smoothing of %K), %D-slow (3-day smoothing of %D, also called %K-slow).
- **Formula (10-day example, from source)**: `%K = 100 × (Close_t − Min(Low,10)) / (Max(High,10) − Min(Low,10))`; %D = 3-day average of %K; %D-slow = 3-day average of %D.
- **Comparison to momentum/RSI**: on the same 14-day calculation period, momentum and RSI track closely; the unsmoothed stochastic moves faster and exaggerates swings due to lacking inherent smoothing.
- **Trading the Stochastic**: buy below 10, sell above 90 (thresholds depend on calc period); typically filtered by trend direction (buy dips within an uptrend). Faster/slower pair (%D crossing %D-slow) used the same way as MACD/signal-line crossings — sell after %D exceeds 90 then crosses %D-slow moving down (mirror for buys). Fastest raw %K is rarely used directly (too volatile).
  - Enter short on the first stochastic sell signal (crossing down) after the trend turns down; enter long on the first buy signal after the trend turns up.
  - **Caveat, quoted**: "it is particularly dangerous to use a timing rule for exiting a position. Delays in entering are lost opportunities, but delays exiting are real trading losses."

### Left and Right Crossovers / Lane's Patterns (10-day calc period, %K-slow vs. %D-slow) (Kaufman Ch.9)

- Faster line (%K-slow) usually turns first — a "left crossover"; when %D-slow turns first instead, it signals a slower/more stable trend change ("right crossover," more favorable).
- **Hinge**: a flattening in either line indicates a reversal is likely the next day.
- **Warning**: an extreme, fast turn in %K-slow (e.g., 2%→12%) indicates at most two days remaining in the old trend.
- **Extremes**: reaching 0 or 100 requires 7 consecutive closes at the highs/lows; the subsequent test of these extremes following a pullback is described as an excellent entry point.
- **Setup**: price makes higher highs/lows on the chart but %D-slow makes a lower low → bear-market setup; look for a selling opportunity on the next rally (mirror for bull setup).
- **Failure**: %K-slow crosses %D-slow after penetrating an extreme, pulls back toward %D-slow but fails to cross it again — an excellent confirmation of direction change.

**Stochastic from RSI**: any indicator, including an unbounded one like raw momentum, can be converted to a bounded %K-style stochastic by substituting the indicator's own value for closing price in the standard stochastic formula — normalizes any unbounded series to 0-100 (Kaufman Ch.9).

## Williams' Oscillators: A/D Oscillator and %R (Kaufman Ch.9)

Larry Williams has published on these since 1972.

### A/D Oscillator (Waters-Williams)

**Source**: Jim Waters and Larry Williams.
- **Buying Power (BP)** measured relative to the open; **Selling Power (SP)** measured relative to the close. **Flagged gap**: the exact per-term BP/SP arithmetic is an embedded-graphic formula in the source, not recoverable as clean text. The combined output, the **Daily Raw Figure (DRF)**, is a normalized ratio bounded 0 to 1.
- Max DRF = 1 when the market opens at the low and closes at the high; DRF = 0 when it opens at the high and closes at the low. DRF fully self-adjusts to the day's own range, solving the volatility/limit-move scaling problem raw momentum has; each day is calculated independently (no memory of yesterday).
- **Trading Rules**: DRF is very volatile unsmoothed; can be smoothed (book's soybeans example uses a 0.30 smoothing constant, with entry bands narrowed from 80/20 raw to 70/30 smoothed).
  - Sell (close longs, go short on next day's open) when DRF (or smoothed DRF) penetrates the overbought zone; buy on the opposite condition. All positions entered on the next open after signal.
  - Optional risk control: exit if DRF fails to post a further extreme value within 1-2 days.
  - More conservative exit: exit when DRF crosses the neutral 0.50 level (book warns this could mean a long wait for a short position in a bull market).
  - **Worked example (soybeans, Jan-Mar 2011)**: raw DRF with 80/20 trigger produced 9 trades, 6 profitable; smoothed DRF (0.30) with 70/30 trigger produced only 2 trades, both profitable.
- **Known problem — gap openings**: an entire day's range occurring above or below the previous close distorts the DRF. **Fix**: replace the current day's high or low with the prior closing price (as in the True Range calculation) whenever that prior close falls outside the current day's range.
- **Explicit warning**: countertrend/overbought-fade trading is "exciting and profitable, but at considerably greater risk than trading in the direction of the trend."

### %R Method

**Source**: popularized after Williams' *How I Made One Million Dollars … Last Year … Trading Commodities*. Formula (10-day example): measures where today's close sits in the recent high-low range, similar to stochastics but conceptually "upside down" — as the close gets stronger, %R gets *smaller* (Kaufman notes it may be more intuitive to use `1.0 − %R`). Williams used it as a within-trend timing/add-on device, trading only in the direction of the major trend.

### Accumulation/Distribution — Note on Naming

Kaufman's source material treats "Accumulation/Distribution" in Ch.9 principally through the **A/D Oscillator (Waters-Williams)** documented above (a volume/price-range-based measure of buying vs. selling pressure), rather than as a separately named, differently-formulated indicator. No separate Accumulation/Distribution Line formula distinct from the A/D Oscillator above appears in the extracted Ch.9 text.

## The Ultimate Oscillator (Kaufman Ch.9)

**Source**: Larry Williams, "The Ultimate Oscillator," *Technical Analysis of Stocks & Commodities* (Aug. 1985) — described in the source as combining the A/D Oscillator concept with Wilder's RSI, adding three concurrent time periods to offset the whipsaw-proneness of a single short period without slowing the system too much.

**Construction (steps as given)**:
1. Today's buying pressure `BP = close − true low`, where true low = `min(low, prior close)`.
2. Today's true range `TR = max(high, prior close) − min(low, prior close)`.
3. Sum BP separately over three intervals: 7, 14, and 28 days.
4. Sum TR over the same three intervals.
5. Divide each period's summed BP by its summed TR; scale the 7-day ratio ×4 and the 14-day ratio ×2 (28-day ratio unscaled, ×1) so all three sit on a common scale. This produces a step-weighted momentum with relative weights 7:3:1 for the first-7-days : second-7-days : last-14-days segments — the last 14 days account for only 10% of the total weighting.

**Trading rules (as given)**:
1. Sell setup: oscillator rises above 50%, peaks, declines, then rallies again; if it fails to exceed the prior peak on this second rally, a short sale is placed when the oscillator fails at the "right shoulder" (a classic top-confirmation pattern).
2. Cover shorts when a long signal occurs, when the 30% level is reached, or if the oscillator rises above 65% (stop-loss) after having been below 50%.
3. Buy signal: the mirror pattern of rule 1 (bottom formation).
4. Close longs when a short signal occurs, when the 70% level is reached, or if the oscillator falls below 30% (stop-loss) after having been above 50%.

## Other Named Oscillators in Kaufman Ch.9

### Relative Vigor Index (RVI)
**Source**: John Ehlers, "Relative Vigor Index," *Technical Analysis of Stocks & Commodities* (Jan. 2002). Basic form: a ratio-style momentum comparing (close − open) to (high − low), conceptually similar to the A/D Oscillator. The final RVI applies a 4-day symmetric (triangular-like) weighting to numerator and denominator separately, designed to target a specific price cycle and eliminate the 2-bar cycle and its unwanted frequencies; Ehlers suggests a nominal cycle period of 10 if the series' dominant cycle hasn't been separately analyzed. **Flagged gap**: the exact weighted-summation formula is an embedded graphic not recoverable as clean text — the input variables (open/high/low/close, n≈10) and the 4-day symmetric weighting concept are preserved. Signal use: an RVI signal line is used exactly like the MACD signal line — sell the first time RVI crosses the signal line moving lower after an overbought peak.

### Awesome Oscillator (AO)
Attributed to Bill Williams (distinct from Larry Williams). Construction: a 5-day SMA of the midpoint price `(H+L)/2` minus a 34-day SMA of the same midpoint price.
- **Buy signal ("saucer" formation)**: AO crosses above zero, then turns down, then turns back up again (the saucer) — initial buy, pullback, confirming second move above zero.
- **Twin Peaks (bullish divergence variant, AO below zero)**: AO forms a low below zero, then a second, higher low (still below zero); buy when AO crosses back above zero. Multiple buy signals possible on each new higher AO peak after two rising lows, as long as no lower low breaks the pattern.

### Linking the Current Day With the Prior Day (Oscillator O)
An oscillator constructed from the high and low relative to the prior close, measuring the ratio of the high price (relative to prior close) against the total range for the day (extended by the prior close if it falls outside today's range, giving boundary values of exactly 1 or 0 in extreme cases). Can be smoothed like the A/D Oscillator. **Flagged gap**: exact combining formula is an embedded graphic, not recoverable — the conceptual construction and boundary-value logic are preserved.

### Oscillator to Distinguish Trending vs. Sideways Markets
Concept: the trend component is stronger when price is farther from "fair value," and noise (sideways movement) dominates when price is near value — so an oscillator comparing the net closing-price change over n days to the high-low range over the same n days can indicate trend strength (larger closing change relative to range = stronger trend; both shrinking together = sideways market). Can be smoothed using price change over 2-3 days rather than the most recent day. **Flagged gap**: exact combining formula is an embedded graphic; concept and smoothing method preserved. See 01_market_structure.md for related trend-vs-noise diagnostics (Efficiency Ratio).

## Double-Smoothed Momentum: True Strength Index (TSI) (Kaufman Ch.9)

**Source**: William Blau, *Momentum, Direction and Divergence* (1995); relates to Blau's double-smoothing work in Kaufman Ch.7.

- **Concept**: double-smooth the 1-day price differences (first differences) rather than smoothing price directly — "using momentum as a proxy for price." Because the first-differenced series is faster/more sensitive than price itself, then slowed by two rounds of smoothing, the net TSI result has surprisingly little lag despite substantial smoothing, and a much smoother line than a standard moving average.
- **Formula (from source, TradeStation-notation variable definitions)**:
  - `r` = calculation period of the first momentum smoothing; `s` = calculation period of the second momentum smoothing.
  - `close − close[1]` = 1-day momentum (numerator input).
  - Numerator: two-stage exponential smoothing of `(close − close[1])` — first over r, then that result smoothed over s: `XAverage(XAverage(close-close[1], r), s)`.
  - Denominator: same two-stage smoothing applied to the **absolute value** of the 1-day differences: `XAverage(XAverage(AbsValue(close-close[1]), r), s)` — this guarantees the denominator is always ≥ the numerator.
  - `TSI = Numerator / Denominator` (scaled, e.g., ×100).
  - Smoothing constants derived from the calculation periods via the standard `2/(n+1)` relationship.
- **Worked example**: Table 9.3 (crude oil, two 20-day smoothing periods) — spreadsheet columns for close, 1-day diff, first smoothing, second smoothing, full sample data preserved in the source for Jan 3-13, 2011.
- **Comparison**: vs. a standard 20-day momentum on Intel, TSI is much smoother, with peaks/valleys lagging price only slightly — Kaufman judges the noise reduction worth the slight added lag.
- **Signal line variant**: smooth the TSI with a 3-period MA as a signal line; buy when TSI crosses above the signal line after a low value.

### Additional Smoothing Without Adding Lag

Kaufman's own suggested improvement to Blau's TSI: substitute n-day differences (e.g., 10-day) for 1-day differences before the two rounds of smoothing — further smooths the trendline at the cost of only a slight additional lag. Example: TSI with 10-day difference + two 20-day exponential smoothings ("10-20-20 TSI"). **Anticipating the turn**: rather than waiting for a smooth trendline (like 10-20-20 TSI) to fully reverse, sell when it reaches a "near-zero slope" and continues to flatten — reduces lag at the cost of occasional false signals (Kaufman Ch.9).

### Double-Smoothed Stochastics (Kaufman Ch.9)

**Source**: William Blau's general form. `DoubleSmoothedStochastic = XAverage(XAverage(Close − Lowest(Low,q), r), s) / XAverage(XAverage(Highest(High,q) − Lowest(Low,q), r), s)` — i.e., Lane's raw stochastic numerator and denominator are each separately double-exponentially-smoothed (first over r periods, then over s periods) before dividing.

### TRIX (Kaufman Ch.9)

**Source**: introduced by Jack Hutson (cited in Colby's *Encyclopedia of Technical Market Indicators* as "Good Trix").
**Construction**:
1. (Optional, often omitted) Take the natural log of closing prices — corrects for price-level volatility, but commonly skipped because back-adjusted futures / split-adjusted stock data can cause errors.
2. p-period exponential smoothing of closing prices (or their log) → trend #1.
3. q-period exponential smoothing of trend #1 → trend #2.
4. r-period exponential smoothing of trend #2 → trend #3 (typically the same smoothing constant/period is used for all three stages).
5. Take the 1-period difference of trend #3 (can be replaced by an s-period difference, as with TSI's added smoothing).
6. (Optional) scale by ×10,000 for chart-friendly integer-like values.
- **Use as trend indicator**: buy when TRIX crosses above zero, sell when it crosses below; can be made faster by requiring 2-3 consecutive bars of rise/fall. See 02_trend_following.md for this usage mode.
- **TRIX vs. TSI comparison**: TRIX (triple-smoothed, differenced at the end) is smoother than TSI (double-smoothed, differenced at the start) but has slightly more lag — a "natural consequence of getting a smoother curve."

## Hybrid Momentum Techniques (Kaufman Ch.9)

A few named systems combine a trend filter with an oscillator; documented here for completeness since they are momentum/oscillator hybrids, though full standalone treatment of their trend components (Directional Movement, Parabolic SAR) is deferred by Kaufman to later chapters (see 02_trend_following.md).

- **Directional Parabolic System** (J. Welles Wilder, *Chart Trading Workshop* 1980): combines Directional Movement (+DMI/−DMI, ADX) with the Parabolic SAR, using ADX as a directional filter (ADX rising → longs only; falling → shorts only) and the Directional Parabolic Stop (DPS) as an exit-only mechanism. **Flagged gap**: the book's own inline PDM/MDM conditional definitions did not extract cleanly; the PDM/MDM logic presented in the source is explicitly flagged as "reconstructed from the standard published Wilder DM formula, not verbatim from this source."
- **Oscillator Method with ADX Filter** (Lars Kestner, *Quantitative Trading Strategies*, 2003): a 10-day/50-day moving-average-difference oscillator, filtered by ADX to detect lack of trend, executed on the next day's open. **Flagged gap**: exact inequality thresholds are embedded-graphic content not recoverable.
- **Cambridge Hook** (cited to Elias Crim, *Futures*, June 1985): combines Wilder's RSI (must exceed 60%) with an outside reversal day and rising volume/open interest to flag an early trend reversal; protective stop placed above/below the "hook" day's extreme.

## Momentum Divergence (Kaufman Ch.9)

### Concept

Divergence means two series moving in opposite directions. For a price series versus its own momentum/MACD indicator, price direction is expected to eventually follow momentum's direction, not the reverse — visualized as the rising-but-slowing portion of a rounded top (Kaufman Ch.9).

### Bearish vs. Bullish Divergence

- **Bearish divergence**: price rising, momentum falling — anticipates a downturn.
- **Bullish divergence**: price falling, momentum rising — anticipates an upturn.

Measured most often by comparing peak-to-peak (and valley-to-valley) direction of price vs. the corresponding momentum indicator; values between the peaks are not considered important for the comparison (Kaufman Ch.9).

### Key Principles (Kaufman Ch.9)

- Price and momentum must be moving in genuinely **opposite** directions — momentum rising faster than price (both still rising) is NOT a bullish divergence.
- **Larger divergence → higher likelihood of a near-term direction change.** During bearish divergence, each successive price peak advances by a smaller amount and takes longer to form (a rounded top).
- Divergence formed over a longer time period (months) forecasts a larger price reversal than one formed over days.
- Divergence measured on daily data is more reliable than intraday data (more noise/randomness intraday).
- Divergence is most reliable when the momentum indicator begins at an extreme high/low, particularly if the divergence forms while momentum is still well past the midpoint (50 or 0), ensuring room for a price correction before momentum even returns to neutral.

### Worked Example (Amazon.com, MACD-based) (Kaufman Ch.9)

Steps: identify swing highs on the price chart; connect the two most significant swing-high peaks; connect the corresponding two MACD peaks directly below; if the price-peak line rises while the MACD-peak line falls, that is bearish divergence. In the book's example, price then dropped from 110 to below 70 within two weeks, later below 50. An unmarked bullish divergence (rising MACD lows vs. price lows around June-August) preceded a subsequent rally.

### Trading Rules for Divergence (Kaufman Ch.9)

1. Enter short when the divergence is identified (provided price hasn't already reached a correction level or profit target); the neutral momentum value (0 or 50, depending on indicator) is the normal profit target, since an overbought reading is expected to correct to neutral, not necessarily flip to an oversold extreme.
2. Enter short when the MACD line crosses the signal line after the divergence pattern is recognized (a clearer, mechanically defined trigger than #1) — best when the *first* momentum peak was itself an extreme.
3. Exit the short if momentum moves above the last momentum peak (invalidates the divergence pattern — can be calculated one day in advance for most momentum indicators).
4. Exit when momentum reaches its neutral midpoint (50 for RSI/stochastic, 0 for MACD/simple momentum), OR when a separate price objective (volatility-based or support-level-based) is reached.
5. Exit an MACD-based short divergence when MACD crosses back above its signal line (can extend the hold well past a simple neutral-momentum exit, adding "considerable profit" in the book's Amazon example).
6. If, at the point of the "normal" divergence exit, the divergence-based trade happens to align with the direction of a separate/underlying trend, hold the position and use the trend reversal (rather than the divergence exit) to close out — converts the divergence trade into a trend trade.

### Anticipating the Divergence (Kaufman Ch.9)

Because a fully-formed second momentum peak is often recognized only after momentum has already fallen back near neutral, an anticipatory approach can be used: once price breaks above its previous resistance level, if the *current* momentum value is already lower than the momentum value at the previous price peak, a divergence sell signal exists immediately (before the second peak visually completes) — hold the short as long as current momentum stays below the last peak's momentum value; exit if momentum exceeds that peak. **Risk trade-off**: higher risk, but captures the full downward reversal.

**Less risky, scaled-entry alternative** (divide capital into thirds): (1) sell 1/3 when price makes a new high while MACD is much lower than its prior peak; (2) sell 1/3 more when MACD moves to within 15-20% of its previous high; (3) sell the final 1/3 when MACD crosses its signal line moving down. **Author's explicit ranking**: if only one entry point can be taken, prefer #2; if two, take #1 and #2; taking only #3 means price will have already dropped significantly, producing a disappointing entry.

### Single, Double, and Triple Divergences; Alternating Peaks (Kaufman Ch.9)

A double bearish divergence = three declining momentum peaks against three rising price peaks (the second momentum peak typically only slightly lower than the first, with the third dropping off noticeably — signals an imminent, more reliable reversal). Multiple divergences are considered more reliable than single divergences. When a lower momentum peak falls between two otherwise-declining peaks (e.g., peaks of 90, 60, 75), most analysts ignore the middle peak and evaluate only the outer (90→75) divergence.

### Programming Divergence and Slope Divergence (Kaufman Ch.9)

Full mechanical programming of divergence is acknowledged as difficult ("what we can see on a chart is not always easy to program into a computer"). The `TSM Divergence` reference tool uses a stochastic (not MACD) as its momentum measure, with parameters for swing percentage (typically 2-5%), minimum strength of decline (typically 5%), stochastic length (typically 5-10 days), and separate entry/exit stochastic lines (SlowK for entry, FastK for exit, to minimize lag). **Acknowledged limitation**: the program does not always find divergences that appear visually obvious, particularly when price rises steadily without forming clear swing highs even as momentum steadily declines.

**Slope Divergence** is offered as an alternative: calculate the slope of price and of the momentum indicator over the same interval (spreadsheet SLOPE function or `LinearRegSlope`); if one slope is positive and the other negative, a divergence exists. **Caution**: the momentum-calculation period should not be too long, or momentum's own slope will trend toward zero (since momentum is itself already a detrending transform). Classic analysis restricts the combinations considered to price-rising/momentum-falling (bearish) and price-falling/momentum-rising (bullish). Applying slope divergence to a heavily triple-smoothed momentum series (TRIX or TSI, e.g., 20-20-20) gives a clearer but slower, more lagged signal.

## Some Final Comments on Momentum and Oscillators (Kaufman Ch.9)

Momentum/oscillators, being fundamentally different from charting or moving averages, are important tools, but become highly unstable (rapid oscillation between overbought/oversold) at short calculation periods. **Any strategy using a momentum indicator to enter trades counter to price direction carries elevated risk.**

**Reminders about oscillators** (cited to John Ehlers, "Measuring Market Cycles," 2016):
- If an indicator gets stuck at its top/bottom value, the calculation period is too short.
- If an indicator never reaches its top/bottom value, the calculation period is too long.
- A shorter period tends to lead the market; a longer period lags it.
- Anticipating the indicator's turn is better than waiting for it to actually turn.
- In a trending market, indicators stay pinned at the top or bottom of their range.

**Practical application guidance**: momentum indicators are most often used as a *timing tool* within a longer-term strategy (e.g., a macrotrend), with the calculation period tuned to produce extremes at a frequency useful for entry timing. Worked example: for a trend strategy averaging 20-day holds, willing to wait up to 2 days for entry after a trend signal, construct either a 10-period oscillator of 1-hour bars or a 3-period oscillator of daily bars, and test that it produces at least one (preferably two) oversold signals per 2-day window (Kaufman Ch.9).

## Momentum vs. Mean-Reversion Regimes (Chan Ch.7)

Chan's framing is explicitly statistical/regime-based rather than indicator-mechanical: **trading strategies can only be profitable if security prices are either mean-reverting or trending; if prices random-walk, "trading will be futile"** (Chan Ch.7). His decision logic:
- IF prices are believed mean-reverting AND currently low relative to a reference price → buy now, plan to sell higher later.
- IF prices are believed trending AND currently low → sell (short) now, plan to buy lower later.
- The opposite logic applies symmetrically when prices are high.

**Empirical caveat**: academic research indicates stock prices are on average very close to a random walk, but under certain special conditions and time horizons, mean reversion or trending behavior can emerge — the same price series can be simultaneously mean-reverting at one horizon and trending at another (a "fractal" nature, a term Chan attributes to some traders). He mentions Elliott wave theory, hidden Markov models, Kalman filters, and neural networks as approaches others use to determine regime, but states he "personally [has] not found such general theories of mean reversion or momentum particularly useful," except in the specific regime-switching data-mining example discussed below (Chan Ch.7).

**Chan's own heuristic (explicitly his personal opinion)**: "unless the expected earnings of a company have changed, stock prices will be mean reverting." He cites Khandani & Lo (2007)'s simple short-term mean-reversal model as empirically profitable (before transaction costs) over many years, but flags that whether it remains profitable after transaction costs is left to the trader to determine (Chan Ch.7).

Chan's **Chapter Summary explicitly states**: "Mean-reverting regimes are more prevalent than trending regimes" (per his assessment) — a direct, opinionated contrast to a purely momentum-centric view of markets (Chan Ch.7).

### Sources of Momentum, per Chan (Chan Ch.7)

1. **Slow diffusion of information** — as more investors become aware of news, more buy/sell decisions accumulate in the same direction. Named example: **post-earnings-announcement drift (PEAD)** — buy on earnings-beat, short on earnings-miss.
2. **Incremental execution of a large order** (institutional liquidity needs or private investment decisions) — Chan states this "probably accounts for more instances of short-term momentum than any other cause," though increasingly sophisticated broker execution algorithms make it harder to detect whether a given move reflects a large hidden order.
3. **Herding behavior** — investors interpret others' (possibly random/meaningless) trading decisions as informative, in the absence of complete information of their own (citing Yale economist Robert Shiller).

**Practical limitation flagged for causes 2 and 3**: momentum from private liquidity needs or herding has "highly unpredictable time horizons" — you cannot generally estimate how large an institutional order is or when a "herd" reaches its tipping point, making these momentum sources hard to time profitably (Chan Ch.7).

### Effect of Competition — Contrast Between the Two Regimes (Chan Ch.7)

- **Mean-reverting strategies**: competition gradually eliminates the arbitrage opportunity, diminishing returns toward zero; as true arbitrage opportunities shrink, an increasing proportion of remaining trading signals reflect real fundamental valuation changes rather than transient mispricing.
- **Momentum strategies**: competition shrinks the time horizon over which a trend persists, since faster information dissemination and more traders acting earlier causes the new equilibrium price to be reached sooner — any trade entered after equilibrium is reached is unprofitable.

### Chan's Regime-Testing Framework (as distinct from Kaufman's discretionary/chart-based framing)

Where Kaufman's momentum/oscillator material is discretionary and chart-pattern-based (bands, thresholds, visual divergence, hinge patterns), Chan's approach to determining regime is statistical and test-driven:

- **Stationarity test**: a stationary time series ("integrated of order zero") never drifts progressively farther from its initial value; it is the ideal mean-reversion candidate. Most individual stock price series are NOT stationary (Chan Ch.7).
- **Cointegration test (CADF — cointegrating augmented Dickey-Fuller)**: even though individual non-stationary series may not be stationary, a specific linear combination of two (or more) of them can be — this is a formal, quantitative alternative to Kaufman's chart-based divergence/trend-vs-noise heuristics. Chan explicitly distinguishes cointegration (long-run price-LEVEL behavior) from correlation (short-run RETURN co-movement) — these are genuinely distinct properties, demonstrated via KO/PEP (correlated returns, 0.4849 correlation, but NOT cointegrated per CADF) (Chan Ch.7).
- **Ornstein-Uhlenbeck half-life**: for a series already established as mean-reverting, `dz(t) = −θ(z(t) − μ)dt + dW`; half-life = `ln(2)/θ`, estimated via linear regression of the daily change in the spread against the spread level — used to set the optimal holding period for a mean-reverting position (Chan Ch.7). See 03_mean_reversion.md for full treatment of this and the cointegration/pair-trading material.
- **Regime switching (academic Markov approach)**: propose 2+ regimes with different price-distribution parameters, assume a transition-probability structure, fit via maximum likelihood, forecast next-period regime. **Chan's explicit critical opinion**: "such Markov regime-switching models are generally useless for actual trading purposes," because they assume constant transition probabilities at all times, which is not actionable (Chan Ch.7).
- **Turning-points / data-mining approach** (contrasted with the Markov approach): feed many candidate predictive variables (current volatility, last-period return, macro changes) into a data-mining search for predictive relationships (citing Chai, 2007). Chan's own **Example 7.1** (Alphacet Discovery, Goldman Sachs stock) used a large one-day percent-change threshold combined with the stock being at an N-day high/low as a proxy for regime-turning triggers, trained via a perceptron across multiple holding periods (1/5/10/20/40/60 days) within a moving optimization window; best result: 37.93% gross cumulative return over a 6-month backtest with 89 round-trip trades, versus 15.77% buy-and-hold. Chan flags this as still vulnerable to data-snooping bias via "model-category shopping" even though the optimization window is strictly backward-looking.
- **Volatility regime switching**: noted as the type most amenable to classical econometric tools (GARCH), but explicitly "of no help to stock traders" per se — more relevant to options traders (Chan Ch.7).

### Stop-Loss Logic Differs by Regime (Chan Ch.6/Ch.7)

Chan's regime framework has a direct, load-bearing practical consequence for risk management, explicitly distinguishing it from a purely mechanical momentum/oscillator system:

- **Momentum models**: if a newer entry signal opposes an existing position, this indicates the momentum direction has genuinely reversed, and the resulting exit is "almost akin to" a stop loss — but Chan frames this as preferable to an arbitrary fixed stop-loss price, which adds an extra tunable parameter and invites data-snooping bias.
- **Reversal (mean-reverting) models**: running the model again after an existing position has lost money will simply generate ANOTHER signal of the SAME sign (the position is now further from the mean, if anything a stronger reversal signal) — therefore, **"a reversal model for entry signals will never recommend a stop loss."** Instead, it may recommend a target price/profit cap once the reversal has proceeded far enough. **Explicit conclusion**: it is "much more reasonable" to exit a mean-reversion position based on holding period or profit cap than stop loss, since a stop loss in this context "often means you are exiting at the worst possible time." **Sole stated exception**: if you believe you have suddenly entered a momentum regime due to recent news, a stop-loss-like exit may then be appropriate even for what was originally a mean-reversion trade.
- Chan's Ch.6 Money and Risk Management chapter states the same principle as a general rule: "Stop losses are conditionally, not universally, good risk management. Beneficial in a momentum/trending regime; actively harmful in a mean-reverting regime, where they force an unnecessary exit before the position would otherwise recoup its loss."

This is a direct point of contrast with Kaufman's momentum-trading material above, where stop-losses on aggressive countertrend (fading) entries are treated as mandatory regardless of regime, because Kaufman's oscillator-fade systems do not have Chan's formal regime classification — they simply assume a bounded, mean-reverting-like behavior for the oscillator itself even when trading an instrument that may be in a trending regime. See 03_mean_reversion.md for the fuller mean-reversion side of this contrast.

### Chan's Momentum Exit-Strategy Guidance (Chan Ch.7)

Exit signals generally fall into four categories: fixed holding period, target price/profit cap, latest entry signal (used as exit trigger), or a stop price. For **momentum strategies** specifically:
- Fixed holding period is the default exit method, since information-diffusion-driven momentum has a finite lifetime; optimal holding period ≈ average length of that lifetime, typically discovered via backtest.
- **Warning**: the optimal holding period for a momentum strategy tends to SHRINK over time as information diffuses faster and more traders exploit the same opportunity earlier — a strategy that historically worked with a 1-week holding period may now only work with a 1-day holding period, and could become entirely unprofitable within a year.
- Determining optimal holding period from backtest trade counts is itself prone to data-snooping bias when historical trade counts are limited — for news/event-driven momentum strategies, Chan states "there are no other alternatives" to this imprecise method (contrast with mean reversion's more statistically robust O-U half-life method, which does not suffer this limitation).
- Target prices CAN be used for momentum models if a fundamental valuation model exists, but Chan cautions fundamental valuation is "at best an inexact science," so target prices are "not as easily justified" here than for mean-reversion.

## Time-Series Momentum Implementation (Hilpisch Ch.4)

Hilpisch's treatment is explicitly code/vectorized-backtest-framed, in contrast to Kaufman's discretionary/chart-pattern framing and Chan's statistical/regime-testing framing. Hilpisch distinguishes two momentum types up front, citing literature but not independently validating the cross-sectional type (see the dedicated Cross-Sectional Momentum section below):

- **Cross-sectional momentum** — buy recent relative outperformers, sell relative underperformers, from a pool of instruments (cited: Jegadeesh & Titman 1993/2001; Chan, Jegadeesh & Lakonishok 1996). Cited finding, quoted directly from Jegadeesh & Titman (1993): "strategies which buy stocks that have performed well in the past and sell stocks that have performed poorly... generate significant positive returns over 3- to 12-month holding periods."
- **Time series momentum** — an instrument's own past returns predict its own future returns (cited: Moskowitz, Ooi & Pedersen 2012, quoted: "time series momentum focuses purely on a security's own past return... challeng[ing] the 'random walk' hypothesis"). **This is the type Hilpisch actually implements** in the book's vectorized-backtesting code.

### Basic Implementation (Hilpisch Ch.4)

- Simplest form: `data['position'] = np.sign(data['returns'])` — long if yesterday's return was positive, short if negative. Applied to gold (XAU=) EOD data, this simplest version **significantly underperforms** the benchmark.
- Generalized to a rolling window: `data['position'] = np.sign(data['returns'].rolling(3).mean())` — using the mean of the last 3 returns performs much better (both in absolute terms and relative to benchmark) than either the 1-day version or a 2-day version. The 2-day version is explicitly shown to perform much worse than the 3-day version on the same dataset.
- **Explicit warning**: the strategy's performance "is quite sensitive to the time window parameter" — flagged by Hilpisch as a first hint at overfitting risk baked into a simple-seeming momentum rule.

### Intraday Momentum (Hilpisch Ch.4)

Tested on AAPL and S&P 500, 1-minute bars, single day (2020-05-05): five momentum windows (1, 3, 5, 7, 9-period rolling mean of 1-minute returns) tested simultaneously via a loop generating `position_%d`/`strategy_%d` columns for each window `m`. Result: **all five configurations outperformed the underlying instrument** intraday for both AAPL and the S&P 500 (before transaction costs) in the example shown — presented by Hilpisch as support for the idea that time-series momentum "might be expected... to be more pronounced intraday than interday," though explicitly framed as a single-day, no-cost example, not statistically validated.

### `MomVectorBacktester` Class (Hilpisch Ch.4)

Adds a fixed initial `amount` and proportional transaction costs `tc` to the basic momentum logic:
- `run_strategy(momentum=1)`: computes `position = sign(returns.rolling(momentum).mean())`, `strategy = position.shift(1) * returns` (the `.shift(1)` is critical to avoid look-ahead — the position decided using information known at the end of day t is applied to the return realized on day t+1); identifies bars where a trade occurs via `trades = position.diff().fillna(0) != 0`; subtracts `tc` from the strategy return only on trade bars (`data['strategy'][trades] -= self.tc`); tracks cumulative returns (`creturns`/`cstrategy`) in absolute currency terms via `amount * cumsum().apply(exp)`.

**Worked example (gold XAU=, 2010-2019, momentum=3, $10,000 initial)**:
- No transaction costs: ending value $20,797.87 vs. benchmark → outperformance of $7,395.53.
- With 0.1% proportional transaction costs: ending value drops to $10,749.40, an **underperformance of −$2,652.93** — i.e., a mere 10 basis points per trade completely erases the outperformance and turns it into a loss relative to benchmark, because time-series momentum with short lookbacks trades frequently.

**Key lesson (explicit, load-bearing for real deployment, per Hilpisch)**: transaction costs matter enormously for higher-turnover strategies like short-window momentum; a strategy that looks excellent gross can be a net loser after realistic costs. This is echoed in Hilpisch's Ch.6 AAPL comparison, where momentum(60) achieved +1267% gross of costs (vs. SMA's +462% and mean-reversion's +439%), making it the highest-gross-return but also highest-turnover and most cost-sensitive of the three core strategy types documented for that book.

### Momentum as an ML Feature (Hilpisch, cross-reference)

Beyond the pure momentum strategy, Hilpisch also uses a rolling-mean-of-returns momentum term (`returns.rolling(5).mean().shift(1)`) as one of three engineered features (alongside volatility and distance-from-SMA) added to a DNN classifier's lagged-returns feature set in later chapters — adding these features markedly improved both classification accuracy and cumulative strategy performance in the book's worked example, though the improvement was noted as larger in-sample than out-of-sample (a caution flag for overfitting that Hilpisch does not explicitly call out in that specific subsection). This is a supporting/feature-engineering use of momentum, not a standalone trading rule, and is documented in more depth in a dedicated machine-learning file if one exists in this knowledge base.

## Cross-Sectional Momentum

**Status: cited but explicitly NOT implemented in either Hilpisch or Chan's source material — flagged here as a gap rather than invented.**

- Hilpisch's Ch.4 explicitly names and defines cross-sectional momentum (buying recent relative outperformers and selling relative underperformers from a pool of instruments, citing Jegadeesh & Titman 1993/2001 and Chan, Jegadeesh & Lakonishok 1996) as one of two momentum types, but states plainly that **time series momentum is "the type implemented in the book"** — cross-sectional momentum receives only the citation and definition, with no formula, code, or worked example (Hilpisch Ch.4).
- Hilpisch's own consolidated knowledge-base summary states this explicitly: "The book states cross-sectional momentum and pair/basket trading are out of scope, but does not explain why beyond keeping the book's scope 'concise.'"
- Chan's material does not use the term "cross-sectional momentum" either. His closest adjacent concept is the **factor-model framework** (Chan Ch.7, Fama-French three-factor model), where factor returns are sometimes assumed to have "momentum" (persistence from one period to the next) for predictive purposes — but this is a cross-sectional ranking of stocks by *factor exposure* (beta, market cap, book-to-price), not a ranking by trailing *return* in the Jegadeesh-Titman relative-strength sense. Chan's own worked PCA-factor example (Example 7.4, S&P 600 small-cap universe) explicitly assumes factor returns persist from one period to the next and ranks/trades the top and bottom 50 stocks by expected return — structurally similar in mechanism (rank a cross-section, go long top, short bottom) to cross-sectional momentum, but Chan frames it as a factor-model exercise, not as a momentum strategy per se, and the result was a **negative average annualized return of −1.81%**, explicitly presented as a failure example, not a working strategy (Chan Ch.7).
- **Conclusion**: true relative-strength cross-sectional momentum (rank a universe of instruments by trailing return, go long the top decile/quantile, short the bottom) is not built, backtested, or given trading rules anywhere in the Chan or Hilpisch source material available to this knowledge base. Any cross-sectional momentum system for crypto research would need to be constructed from first principles or from a source outside this knowledge base's five books.
