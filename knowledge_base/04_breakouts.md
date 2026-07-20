# Breakout Systems: N-Day/Channel, Opening Range, and Volatility Breakouts

Scope note: this file documents breakout **mechanics** — how N-day/channel breakout thresholds are constructed, how opening-range breakout (ORB) systems define and confirm a breakout, how volatility-scaled breakout bands are built, what gap statistics are documented in the sources, and what the sources say about false breakouts/whipsaws. The same underlying Kaufman Ch.5/Ch.8 material (Donchian channels, the Turtles, the six-system comparison) is also covered from a trend-following organizing angle in `02_trend_following.md` — see that file for the trend-following framing, position-sizing/compounding rules, and the cross-system performance comparison tables. See `03_mean_reversion.md` for the false-breakout-fade angle (fading failed breakouts as a mean-reversion trade) and `05_momentum.md` for momentum/RSI-type confirmation filters layered onto breakout entries (e.g., Momentum Pinball's LBR/RSI filter, below). All claims are tagged to their source book/chapter; every place the extraction flagged a formula as an embedded PDF graphic that did not survive text extraction is preserved as an explicit gap rather than filled in from outside knowledge.

---

## N-Day and Channel Breakouts (Kaufman Ch.5, Ch.8)

### Basic Construction

The N-Day Breakout is described as sharing the buy-new-highs/sell-new-lows behavior of true event-driven methods (like swing trading and point-and-figure charting), even though it is not purely event-driven since a fixed N-day window still involves time (Kaufman Ch.5). It is called "one of the most popular trend-following techniques" (Kaufman Ch.5).

- **Basic rules (always-in-market, intraday-trigger variant)**: Buy when today's high crosses above the high of the past N days; sell when today's low crosses below the low of the past N days (Kaufman Ch.5).
- **Conservative variant (close-based)**: Buy when today's close is above the high of the past N days; sell when today's close is below the low of the past N days — this confirms direction at the cost of a later entry (Kaufman Ch.5).
- **Risk characteristic**: risk = the difference between the entry price and the point at which an opposite N-day high/low would reverse the signal; a larger N produces larger risk. This is explicitly what distinguishes event-driven methods from time-driven methods such as moving averages generally (Kaufman Ch.5).

### Donchian's 4-Week Rule

Richard Donchian, mid-1970s; described by *Playboy's Investment Guide* as "childishly simple ... recently discovered to rank premiere among a dozen widely followed mechanical techniques" (Kaufman Ch.5).

- **Rules**: (1) go long (cover shorts) when current price exceeds the highs of the previous 4 calendar weeks; (2) sell short (liquidate longs) when current price falls below the lows of the previous 4 calendar weeks; (3) for futures, roll to the next contract on the last day of the month preceding expiration (Kaufman Ch.5).
- **Historical validation cited**: *The Traders Note Book* (1970, Dunn and Hargitt) rated it the best of the era's popular systems over 16 years of history (Kaufman Ch.5).
- **Relationship to Keltner**: closely resembles Keltner's Minor-Trend Rule (an always-reversing rule with no minimum size requirement — see below), but modified via the 4-week window to trade less frequently (Kaufman Ch.5).

### Keltner's Minor Trend Rule (event-driven precursor)

From Keltner, *How to Make Money in Commodities* — historically influential among agricultural traders for its simplicity (Kaufman Ch.5).

- **Trend definition**: an uptrend = failure to make new lows (today's low vs. prior day's low); a downtrend = absence of new highs.
- **Trading rule**: the minor trend turns up when price trades above its most recent high, and turns down when price trades below its most recent low; always reverse position on a trend-turn signal (always in the market).
- **Character**: a simple, short-term, always-reversing tool; unlike the filtered swing method, it has **no minimum size requirement for a reversal**, so it produces many more (smaller) swings; risk varies with volatility rather than a fixed filter (Kaufman Ch.5).

### Channel Construction Rules (bar-chart channels)

Kaufman Ch.3 defines a **channel** as a trendline plus a second line drawn parallel to it, enclosing the price move; the channel's width reflects the move's volatility and defines entry/exit zones (Kaufman Ch.3).

- **Construction**: requires at least 2 (preferably 3+) major low points in an uptrend to draw the primary trendline; the parallel (upper) line is then drawn through the highest high reached during that trend (Kaufman Ch.3).
- **Trading rule**: buy near the support (lower) line, sell near the resistance (upper) line; the buy/sell zones are defined as approximately the bottom/top 20% of the channel width (Kaufman Ch.3).
- **Reversal handling**: if price breaks the lower trendline, the long trade is exited and a new bearish (downward) channel must be redrawn from the most recent swing high/low pair; in a downward channel, sell short in the upper zone and cover in the lower zone. **Buying in the lower zone of a downward channel is explicitly not recommended** — "trades are safest when entered in the direction of the trend" (Kaufman Ch.3).
- **Trading-range special case**: a near-horizontal channel is a **trading range** with no directional bias, so both new longs (at support) and new shorts (at resistance) are acceptable; a break of either boundary forces liquidation and signals a new trend direction (Kaufman Ch.3).
- **Caveat**: trendlines/channels drawn on very little data are essentially "analyzing noise and have limited value" (Kaufman Ch.3).
- **Automated trendline construction**: run a linear regression from the day of the lowest price to the most recent day; find the point(s) furthest below (or above, for a downtrend) that regression line; draw a parallel line through that point — a break of that parallel line signals a trend reversal (Kaufman Ch.3).
- **Channel profit targets**: conceptually identical to the horizontal-consolidation target (breakout point + range height), but measured *perpendicular* to the angled channel boundaries and projected from the breakout point; channel length does not affect target size; the target may be trimmed slightly below the raw channel width for conservatism. As a channel evolves through a trend, a new channel — and hence a new price objective — must be redrawn from the most recent reversal/reaction points each time (Kaufman Ch.3).
- **Regression-based programmed channel (secondary source)**: Chan's material describes a computable version of the same visual trend channel — a linear regression channel with bands set to the most extreme historical residuals, projected one bar ahead; parameters are the regression window length and a choice of testing close vs. low/high for the breakout signal (close = more conservative/later, low/high = earlier) (Chan, Indicators.md). A near-zero regression slope indicates a sideways channel, to which the same breakout logic applies. A related "moving channel" variant uses a dynamically updating (non-regression) moving midpoint and moving range as the channel basis, with the author (in that source) suggesting the profit-objective distance be rescaled to current ATR rather than kept fixed, for volatility-adaptivity (Chan, Indicators.md).

### Point-and-Figure as a Channel/Breakout-Adjacent Method

Point-and-figure charting (Kaufman Ch.5) shares the "buy on box-defined new high, sell on box-defined new low" breakout logic, but is coarser and more delayed than a swing chart because a P&F signal requires filling a discrete box rather than reacting to any move beyond the previous extreme. Basic P&F signals: buy when the X-column rises one box above the previous X-column's high; sell when the O-column falls one box below the previous O-column's low (Kaufman Ch.5). Three risk-limiting entry alternatives to reduce the entry-to-stop distance are given: (1) wait for a pullback to an acceptable risk level, then enter with a logical (support-based) stop rather than an arbitrary fixed-box stop; (2) enter on the second reversal in the direction of the original signal (skip the first pullback, wait for a full 3-box reversal down, then place a trailing buy 4 boxes above the O-column low); (3) require a confirming new high beyond the basic 1-box breakout (raise the confirmation threshold to 2, 3, or 4 boxes as volatility increases) to filter false breakouts during erratic sideways or expanding-after-low-volatility patterns (Kaufman Ch.5).

### Modifying the N-Day Rule

- **Volatility-adaptive N (cited, Seidel and Ginsberg, 1983)**: N for today's calculation can be derived from the ratio of normal (longer-period) volatility to current (shorter-period, typically less than ¼ the longer period) volatility — as current volatility rises relative to normal, N decreases. **Gap flagged**: the exact combining formula is embedded as a graphic in the source PDF and did not survive text extraction; the inverse volatility-ratio relationship and the parameter definitions (normal vs. current volatility, ¼-period ratio) are explicit and preserved (Kaufman Ch.5).
- **Calendar-quarter-based N for stocks**: N can be set as a multiple/fraction of a calendar quarter to relate trend length to earnings-announcement cycles — a multiple of 3 months smooths quarterly reactions; a shorter period tries to capture the pre-announcement trend (Kaufman Ch.5).

### Testing the N-Day Rule (Kaufman's own study, 2000–Nov. 2017)

Same market set as the point-and-figure box-size study; N tested from 10 to 120 days in steps of 10 (23 tests/market) (Kaufman Ch.5).

- **Results**: average best calculation period ≈ 93 days (a macrotrend-style N); 7 of the tested markets were profitable across *all* tested N values; average 79% of tests profitable across all markets (vs. 63% for point-and-figure in the equivalent study); net profits for the breakout system were **more than 15× greater** than point-and-figure's over the same test window (Kaufman Ch.5). Author's interpretation: the consistency across N values adds confidence to the method's robustness.

### Weekly Breakouts

Originated with Donchian's 4-Week Rule. The classic form evaluates prices only on Friday, since the Friday close is treated as the week's most important "evening up" price (analogous to the daily close's primacy in Dow Theory) — this evening-up process is expected to filter out midweek/midday low-liquidity false signals; weekly data is also inherently smoother than daily (Kaufman Ch.5).

- **Typical rules**: buy (close shorts) if Friday's close exceeds the highest closing price of the past N weeks; sell short (close longs) if Friday's close is below the lowest closing price of the past N weeks (Kaufman Ch.5).
- **Main drawback — high risk**: initial risk on a new long = the difference between the highest and lowest closing prices of the past N weeks; the position is not liquidated until Friday's close (or even Monday's open, depending on calculation timing), which can amplify realized losses relative to a same-day model — offset somewhat by weekly data's smoothing benefit (Kaufman Ch.5). **Explicit warning**: this is called out as a genuine risk trade-off, not merely a theoretical concern.
- **Programming caveat**: a "Friday" close should actually mean "the last close of the week" to correctly handle holiday-shortened weeks; best practice is to use native weekly data feeds (correctly converted from daily) rather than deriving week-end closes from daily data directly, to avoid look-ahead/holiday bugs (Kaufman Ch.5).

### Dynamic Breakout System (DBS) — Stridsman

Thomas Stridsman ("Revelation Trading," *Futures*, Feb. 1998) (Kaufman Ch.5).

- **Core idea**: rather than a plain N-day high/low, anticipate entry/exit points one day ahead using a factor of the standard deviation of recent prices, placing stop orders for the next trading day — an attempt to improve timing over the plain N-day breakout, which reacts to price moves and volatility only after the fact.
- **Study finding**: exit-stop hit timing falls into two distinct groups — trades stopped out very quickly, and trades held for a much longer time; this bimodal pattern is used to suggest traders can position stops more deliberately depending on which regime is likely to apply.

### Donchian's 40/20 Channel Breakout and the Turtles

Donchian's 40/20 Channel Breakout (Hayden Stone, 1960s) is described as the earliest recorded N-day breakout to use **different periods for entry (longer, 40 days) and exit (shorter, 20 days)** — the direct conceptual predecessor of the Turtles' method (Kaufman Ch.5). The full Turtles System 1/System 2 rule set, risk-control/position-sizing/compounding rules, and the six-system trend comparison are documented in `02_trend_following.md`; the breakout-threshold mechanics specifically are: System 1 enters long on a 20-day high / short on a 20-day low, exits on a 10-day opposite extreme; System 2 enters long on a 55-day high / short on a 55-day low, exits on a 20-day opposite extreme (Kaufman Ch.5). Both systems place the initial stop-loss at a distance of 2L from entry, where L is a 20-day-ATR-based volatility measure converted to dollar terms via the market's "big point value" (Kaufman Ch.5).

### The Six-System Comparison — Breakout's Place in It (Kaufman Ch.8)

Kaufman Ch.8 compares six single-trend systems head-to-head on the same markets/calculation periods with no stops or profit-taking, to isolate each method's natural risk/return profile: momentum (M), simple moving average (MA), exponential smoothing (EXP), N-day breakout (BO), swing breakout (SWG), and linear regression slope (LRS). The **BO (breakout)** rule as tested: buy when close > highest(high, t−1, n); sell when close < lowest(low, t−1, n) (Kaufman Ch.8). Full comparative results are covered in `02_trend_following.md`; the risk-profile finding specific to breakout mechanics is that the breakout system carries **higher per-trade risk than a moving average** (risk = the full high-low range of the calculation period) but achieves a **higher win rate, roughly 50-70%**, because it tolerates price movement without reversing the way a moving-average crossover does (Kaufman Ch.8). This is contrasted with the MA system's typical <35% win rate and much larger win:loss ratio requirement. **Author's synthesis**: breakouts "may suit intraday trading" specifically, among the family of trend techniques, though "you can't really go wrong, whichever method you choose" for genuinely trending markets (Kaufman Ch.8).

### The Adaptive Price Zone (APZ) as a Channel-Breakout Contrast Case

Not a trend-breakout system but included here because it uses the same "band touches highs/lows" construction logic in the opposite (mean-reverting) direction: Leibfarth's APZ (2006) builds a band from a double-smoothed exponential trendline, with volatility measured via an "adaptive range" = the 5-day EMA of the 5-day EMA of (daily high − daily low). When the bands touch the day's highs/lows, that is read as a mean-reversion opportunity rather than a trend-continuation breakout signal (Kaufman Ch.8). **Gap flagged**: the exact band-width combining formula is an embedded graphic not recoverable from the extraction; the double-smoothed-EMA volatility construction and the mean-reversion interpretation are explicit. See `03_mean_reversion.md` for further mean-reversion band material.

### Bill Williams' 5-Bar Fractal Breakout (Kaufman, Ch.20)

A pivot-based breakout system distinct from Bill Williams' Awesome Oscillator (covered in `05_momentum.md` and `13_indicator_reference.md` — not duplicated here). Source: Bill Williams, *Trading Chaos* (1995; new edition by Justine Gregory-Williams and Bill M. Williams, 2004) (Kaufman, Ch.20).

- **Definitions**:
  - **Up fractal**: a 5-bar pivot pattern — the two bars to the left of the center bar have lower highs, and the two bars to the right have lower highs (i.e., the center bar's high is a local peak over the 5-bar window). Indicates the market is struggling to go higher.
  - **Down fractal**: the mirror image — the two bars to the left have higher lows, the two bars to the right have higher lows (the center bar's low is a local trough). Indicates the market resists going lower.
  - If the center bar is an outside bar, the same 5-bar pattern can simultaneously qualify as both an up fractal and a down fractal.
  - A trade cannot be made until the fifth (final) bar of the pattern is complete.
  - **Broken fractal**: when a subsequent high/low goes above/below the previous fractal's extreme.
- **Entry Rules**: buy following a down fractal when price rises above the highest high of the down-fractal pattern; sell following an up fractal when price falls below the low of the up-fractal pattern.
- **Risk Rules**: place a sell stop at the low of the fractal pattern (for longs) or a buy stop at the high of the fractal pattern (for shorts).
- **Exit Rules (added by Kaufman)**: take profit equal to the high-low range of the fractal pattern, measured from the trade entry point.
- **Backtest Result**: SPY, 2000-2018 — profitable for long positions, 58% reliability. Using profit-taking without stops was the best combination — noted by the author as "a result that is common for most short-term trading."
- **Algorithmic Trading**: `TSM Fractal Indicator` (pattern detection) and `TSM Fractal Strategy` (full trading rule test) on the Companion Website.

---

## Opening Range Breakout Systems (Kaufman Ch.16)

### Framing

Kaufman Ch.16 identifies the 1990s as the peak era for intraday breakout systems, as computer speed, software, and cheap electronic data made the daily N-day breakout evolve into the **N-bar breakout** — new highs/lows of the previous N *bars* rather than N *days*. A discovered risk of this evolution: intraday reversals (new high, then new low, then new high again within a session) can produce shockingly large losses; trades held overnight continue the N-bar count across days (Kaufman Ch.16).

Three general ways to define an intraday breakout are given: (1) the high-low range formed in the first n minutes/bars after the open; (2) a percentage of daily volatility measured from the open; (3) the same volatility measure but from the previous close. All three types can be filtered by trend, minimum/maximum volatility, compression, or other qualifying patterns, and can be held overnight or exited on the close (Kaufman Ch.16).

### 1st Hour Breakout (Opening Range Breakout Using Time)

The classic time-based opening range breakout (Kaufman Ch.16).

- **Entry Rules**: wait 1 hour after the open; fix the breakout levels as that period's high/low; buy above the high, sell below the low; reverse if price crosses the opposite threshold (some traders take only the first signal of the day).
- **Exit Rules**: exit at the end of the day.
- **Filters/Optimization**: optional 1-ATR (14-day) profit target; cancel the trade if no signal occurs within 2 hours of the open.

### N-Bar Breakout

A bar-count variant of the 1st Hour Breakout, fixing the high-low range after the first N bars of trading rather than after a fixed time (Kaufman Ch.16).

- **Entry Rules**: buy/sell stop at the N-bar range high/low.
- **Example**: S&P 30-minute bars, 2-bar breakout, exit on close — worked through 5 days of signals and outcomes in the source.
- **Filters**: trade only with the daily trend; require a preceding inside bar; enter longs after an upside reversal pattern on a smaller bar size.
- **Important Warnings**: breakouts occurring near the close offer little profit opportunity; new trades are typically not entered within 1 hour of the close.

### Raschke and Conners' Momentum Pinball (LBR/RSI™ + 1st-Hour Breakout)

An improvement on plain opening-range-breakout trade selection using a fast, low-lag momentum/RSI hybrid (Kaufman Ch.16). Source: Conners & Raschke, *Street Smarts* (1995).

- **Indicator**: LBR/RSI™ = a 3-day RSI applied to a 1-day rate of change (the rate-of-change pre-transform reduces the normal lag of a plain RSI). Ties conceptually to Taylor's 3-day cycle (Kaufman Ch.15).
- **Entry Rules (buy)**: IF the previous day's LBR/RSI < 30, THEN place a buy stop above the first hour's trading-range high on the current day; once filled, place a sell stop at the first hour's low; IF stopped out, THEN re-enter if prices reverse and penetrate the original buy threshold again.
- **Sell signals**: mirror image, triggered when LBR/RSI > 70.
- **Exit Rules**: IF profitable at day's end, THEN carry the position overnight; IF the next open extends the profitable direction, THEN exit on that open.
- **Reported test result**: emini S&P, 2000–May 2011: $703/contract average gain over 1,734 trades, **no transaction costs applied** in this figure. Author notes more strongly trending markets than the S&P should be expected to perform better.
- **Full parameter set captured?** Yes for the core rule (30/70 LBR/RSI thresholds, 1st-hour range, re-entry logic) — this is one of the more completely specified named ORB systems in the extraction.

### Toby Crabel's Opening Range Breakout Using Volatility

Replaces a fixed-tick opening-range breakout with per-market volatility-calibrated thresholds, filtered by preceding-pattern compression (Kaufman Ch.16). Source: Toby Crabel, *Day Trading with Short Term Price Patterns and Opening Range Breakout* (1990); "Opening Range Breakout, Part 4" (1989).

- **Entry Rules**: buy when price moves up from the open by a market-specific fixed value (Table 16.4 gives examples such as a specific tick-value in bonds, 25 basis points in cattle — see gap note below); reverse to short if price then declines a further specified amount below the open (an 8-tick reversal is the example given for bonds specifically).
- **Exit Rules**: exit all trades on the close of the day.
- **Filters/Confirmation**: preceding inside days, low volatility, and "bull/bear hooks" are all reported to improve trade selection. Table 16.4 compares "Any Day" vs. "Inside Day" percentage-profitable across bonds, S&P 500, soybeans, and cattle — inside-day filtering raises the win rate in every market shown (e.g., bonds 60%→76%, soybeans 60%→70%, per the day-trading knowledge base file's Ch.16 read of the same table).
- **Important Warning**: despite dating to 1990, compression as a filter "seems to remain a good filter" per the author's more recent commentary.
- **Gap flagged — parameters only partially captured**: Table 16.4's exact per-market breakout threshold values and the precise row/column alignment of the percentage-profitable figures are described in the source as **partially degraded by PDF column-extraction artifacts**; only the illustrative examples above (a tick-value in bonds, 25bp in cattle, an 8-tick reversal in bonds) and the qualitative inside-day-filter benefit are reliably preserved. The full numeric threshold table for all four markets (bonds, S&P 500, soybeans, cattle) across both "Any Day" and "Inside Day" conditions is **not** confidently recoverable from this extraction — flagged as a genuine gap rather than reconstructed.

### Raschke's NR4 Range-Contraction Breakout

Linda Raschke's variation on Crabel's range-contraction concept, using a 4-day "narrowest range" pattern (Kaufman Ch.16). Source: Conners & Raschke, *Street Smarts* (1995).

- **Required Conditions — exact NR4 definition**: NR4 = a 4-day window in which the **4th day's** high-low range is smaller than each of the preceding 3 days. Note the source explicitly clarifies that the 4th day's range **need not fall entirely within** the prior 3 days' range — only its span (high minus low) must be numerically the smallest of the four.
- **Entry Rules**: on the day following an NR4 day, place a buy stop 1 tick above the NR4 day's high and a sell stop 1 tick below its low.
- **Exit Rules**: IF a new signal triggers (e.g., a buy) AND price reverses through the sell-stop level the same day, THEN close the long and go short; use a trailing stop to protect gains; IF the trade is not profitable within 2 days, THEN exit on the close of the second day.
- **Gap flagged**: the trailing-stop mechanism itself is explicitly noted by the source author as the "only missing feature" of the published rule set — it is not defined in the source and is not reconstructed here.
- **Full parameter set captured?** Yes for the core setup (4-day lookback, 1-tick stop placement, 2-day time-stop) — the NR4 lookback of exactly 4 days is explicit and exact, unlike some of the other named ORB systems in this chapter.

### Mark Fisher's Opening Range Breakout (from *The Logical Trader*)

An in-depth, professionally-derived ORB method with layered confirmation, fade, and bias rules; some components target very small profits suited only to very-low-cost professional execution (Kaufman Ch.16). Source: Mark B. Fisher, *The Logical Trader* (2002).

- **Timeframes**: stocks typically use a 20-minute opening range (OR); futures 5-30 minutes depending on the market; no more than 5-minute bars are recommended for constructing the OR.
- **Indicators/levels**: ORH/ORL = opening range high/low; **±A levels** = a percentage (illustrative example given: 100%) of the OR range added above ORH / subtracted below ORL; **±C levels** = a larger percentage (illustrative example given: 150%) further beyond ±A; a separate daily pivot range is computed from the prior day's movement.
- **Entry Rules**:
  1. Buy when price moves above +A and remains above it for a time equal to (a fraction/multiple of) the OR duration.
  2. Sell short if price falls below −C and remains below it for the equivalent confirmation time.
  3. IF price falls one tick below ORL while long, THEN close the long (a separate condition from the reversal-to-short rule).
  4. Once reversed to short, place a stop-loss one tick above ORH.
  5. IF price does not prove profitable within a time interval (a multiple of OR), THEN exit.
- **Confirmation Signals**: the "remain outside the threshold for ½ the OR time" rule exists specifically because a short OR window otherwise produces too many false signals — for a 20-minute OR, price must hold above ORH for 10 minutes before buying.
- **Filters**: the separate daily pivot range sets a bullish/bearish bias for the day — IF the previous close is above today's pivot-range high, THEN bullish bias (expect support to hold at the pivot low); IF below the pivot low, THEN bearish bias; a break of the pivot range itself is treated as a stronger, more significant signal than an ordinary support/resistance break.
- **Alternate/Fade Rules**: a separate rule set fades a failed penetration of a support level (ORL, −A, −C, or the pivot low) — a failed downward break is likely followed by a minor rally, potentially back to ORL; this is explicitly flagged as offering frequent but sometimes small opportunities, depending on the day's volatility and the trader's cost structure (see `03_mean_reversion.md` for the general false-breakout-fade framing).
- **Profit-Taking**: targets can be set as a multiple of the OR range; after a profitable exit, a long position can be "reset" if price falls back below +A and then breaks back above it, with a stop 1 tick below ORL.
- **Gap flagged — parameters only qualitatively captured**: the exact default percentage values for the A/C multipliers beyond the illustrative 100%/150% examples, and the exact time-multiplier defaults for the confirmation and exit rules, are **embedded-graphic gaps** — the symbols did not survive PDF extraction. The qualitative rule *structure* (ORH/ORL, ±A/±C bands, time-based confirmation, pivot-range bias, fade variant) is fully preserved, but the full numeric parameter set as originally published is **not** recoverable from this extraction.

### Larry Williams' Filtered Opening Range Breakout (S&P and bonds)

Two distinct filtered ORB variants for the S&P 500, adaptable to bonds/interest-rate markets (Kaufman Ch.16).

- **Indicator**: a 10-day raw stochastic/%R, with numerator = Highest(High,10) − current close — Williams' own variant, explicitly distinguished by the source author from a related %R formula attributed to James T. Holter (*Futures*, Aug. 2001).
- **Entry Rules — Method 1 (S&P)**: IF %R < 20% AND today's close < the close 7 days ago AND today's close > the previous close (or the close 2 days ago) AND today is not an inside day, THEN the buy setup is active. For bonds/interest-rate markets, additionally require today's close > the close 4 days ago (Williams wants more trend confirmation in that market).
- **Entry Rules — Method 2 (S&P, Monday/Tuesday rally tendency)**: IF the previous day is not an inside day with a close greater than the low 2 or 3 days ago AND today's close < the close 6 days ago (bonds: close 15 days ago), THEN the buy signal triggers when price penetrates a band formed by adding 20% of the previous day's trading range to today's open.
- **Filters**: Williams also recommends traditional seasonality as an additional filter, with the explicit caveat that seasonal patterns "do not work all the time" but still provide a useful risk-awareness edge.
- **Gap flagged**: the full normalized %R formula's denominator/scaling term is an embedded-graphic gap; only the numerator definition is captured as clean text.
- **Full parameter set captured?** Method 1 and Method 2 both have fully specified, exact numeric lookback values (7, 2, 4, 6, 15 days; 20% band; 20%/80% %R thresholds) — one of the more completely parameterized named systems in this chapter, in contrast to Fisher's ORB above.

### Volatility Breakout Based on the Open or the Previous Close (general framework)

Distinct from the named/attributed systems above, this is Kaufman's own generalized volatility-breakout construction, tested via the `TSM Flexible Intraday Breakout` companion tool (Kaufman Ch.16). See also the "Volatility Breakouts" section below for the shared ATR-band mechanics.

- Volatility is measured as an n-day ATR (5-20 days); a percentage (the "breakout factor," typically <1.0 since ATR is a daily-scale value) of that ATR is added/subtracted from either the day's open or the previous close to form the breakout bands.
- Centering on the **previous close** embeds some trend information into the band and can generate a signal on the very first bar of the day; centering on the **open** is trend-neutral. **No a priori answer is given** as to which is better — the source states this requires testing; trending markets are expected to favor the previous-close method, which also tends to generate more signals.

**Parameter-selection case study (S&P 30-minute, 2010–Apr. 2017, $8/contract/side cost)** — one-parameter-at-a-time testing is explicitly recommended over simultaneous multi-parameter optimization, to keep each parameter's contribution interpretable (Kaufman Ch.16):

1. Breakout factor from the open: profitable factors cluster 0.5-1.0, peaking at 0.6 (~$450,000 total) — smaller breakouts react to noise, larger ones leave too little time in the day.
2. Breakout factor from the previous close: similarly clustered, peaking near $800,000 — better overall than the open-based version.
3. Adding a trend filter: the open-based version improved only slightly (fast trend lengths 20-40 days; win rate rose from 55%/471 trades/$979 avg to 56%/440 trades/$1,100 avg — "a real but modest improvement," at the cost of higher correlation with other trend-following systems for a portfolio manager). The previous-close version improved more clearly (no-filter baseline $801,912/347 trades/61% win rate; with a 50-70 day trend filter, ~$816,000/319 trades/62% win rate).
4. **General lesson stated**: neither the open- nor close-based breakout showed a decisive case for a trend filter; the recommended process is to test options individually, record results, then combine only the previously-selected best parameters in pairs — judging visually by equity-curve smoothness, not just net-profit tables.
5. **Mean-reversion variant** (reverse the breakout logic; open-based, current-day-only): breakout factor optimization again clusters 0.5-1.0; overall profit was only 14% less than the directional open-based breakout, but with a much smoother equity curve, average profit per trade of $1,973 (about double the directional breakout) on only 219 trades, 64% profitable.

The full configurable parameter set for the underlying `TSM Flexible Intraday Breakout` tool includes: choice of open-basis vs. previous-close basis; the breakout factor f and lookback n; an optional mean-reversion factor mf on the same ATR; session start/end/last-entry times; an ATR-based profit-target factor m; an optional trend filter; a c-day compression filter; an inside-day filter; a long-only option; an overnight-hold option; and separate stock ($10,000/trade) vs. futures ($25,000/trade) position-sizing defaults (Kaufman Ch.16).

### Other Day-Trading Breakout/Reversal Patterns (briefly, for completeness)

Several further named patterns in Kaufman Ch.16 use breakout or breakout-failure logic on stock intraday data (Barry Rudd, *Stock Patterns for Day Trading and Swing Trading*, 1998, and DeMark/Larry Williams "true gap" material) — these are documented in full under "Strategies.md, Chapter 16 additions" and summarized here only briefly since they are day-trading-specific pattern catalogs rather than core breakout-mechanics content (see the day-trading knowledge base file, if one exists, for full treatment):

- **Rudd's Special Set-Up Patterns (5-min data)**: five buy setups — Dip and Rally, Consolidation, Delayed Consolidation, Early Breakout, Reversing After a False Breakout (this last one is explicitly a false-breakout-fade rule: IF a breakout of the Consolidation pattern fails and price falls back into the original range, THEN close the long and sell short, expecting a support breakdown) (Kaufman Ch.16).
- **Day Trades Following a Wide-Ranging Bar (Rudd)**: Breakout of a Higher Open (buy the current day's high breakout if the next day opens above the prior wide-ranging bar's high and then tests that high before rallying) and Selling a Gap Open (sell if a substantial gap open begins to fade within the first 5 minutes) (Kaufman Ch.16).
- **Short-Term "True Gap" Patterns (DeMark/Larry Williams)**: a "true" gap opens beyond yesterday's high/low and does not trade back to that level; Williams' method enters a new short on a stop when price pulls back to the previous high after a true upward gap (mirror for downward gaps). The `TSM Intraday Gaps` tool found the best entry/exit combination to be entry on pullback-to-previous-close plus exit-on-next-open (Kaufman Ch.16). See "Gap Statistics" below for related gap-fill data.

---

## Volatility Breakouts (Kaufman Ch.5, Ch.8, Ch.16)

Volatility-scaled breakout construction recurs across three chapters with a shared underlying logic: scale the breakout/band threshold by a volatility measure (ATR, standard deviation, or a percentage of price) rather than a fixed point/tick value, so sensitivity stays roughly constant across changing volatility regimes.

### Volatility Bands (Kaufman Ch.8, trend-following framing)

**General construction**: band width = a scaling factor s × a volatility measure; the trendline can be a moving average, exponential smoothing, or regression, and can be substituted freely. The prose explicitly notes "when [the scaling parameter is set to a stated value], the full band equals 2×ATR" as one calibration case (Kaufman Ch.8). **Gap flagged**: the exact combining formula is an embedded graphic and did not survive text extraction; only the concept and the 2×ATR special case are preserved as prose.

**Comparison of four 20-day-MA-centered bands, same scaling factor of 2 (S&P, Figure 8.5)**: (a) 2% of trendline, (b) 2% of price, (c) 2×ATR, (d) annualized 20-day volatility (standard deviation). Observed shapes: the two percentage-based bands are almost identical, very smooth, and farthest from the center; the ATR band is next-closest and widens slightly more in volatile periods; the standard-deviation band is closest to the trendline and most sensitive to price volatility. Because a shared scaling factor produces very different absolute band widths across the four methods, direct comparison requires adjusting scaling factors per method (Kaufman Ch.8).

**Keltner Channels**: cited as one of the original band calculations (Chester Keltner, *How to Make Money in Commodities*, 1960). **Gap flagged**: the exact formula is an embedded graphic and did not extract as clean text. Author's own note: it would be best to substitute true range for the high-low range as a better volatility measure (Kaufman Ch.8).

**Percentage Bands**: a band formed by adding/subtracting a fixed percentage c of price from a closing-price-based trendline. Worked example: MA for Merck (MRK) = $33, band = 3% → upper band = $33.99, lower band = $32.01. A more sensitive variant uses the *current price* (rather than the MA) to compute band width while still centering on the MA trendline for stability. **Explicit warning**: percentage bands cannot be used with back-adjusted futures data (their absolute price levels are artificial); avoid a fixed-dollar-value band since it would be overly sensitive at high prices and insensitive at low prices (Kaufman Ch.8). **Gap flagged**: exact band arithmetic formulas are embedded graphics not recoverable as clean text; the worked example and the two variants are preserved.

**Rules for using any band type**:
- **Reversal-strategy variant (always in the market)**: buy (close shorts, go long) when price closes above the upper band; sell short (close longs, go short) when price closes below the lower band. Maximum risk per trade = the current band width (which changes daily) (Kaufman Ch.8).
- **Trendline-exit variant (reduces order size, adds a flat/no-position period)**: buy when price closes above the upper band; exit when price reverses and closes below the trendline (band center). Sell short when price closes below the lower band; cover when price closes above the trendline. If price fails to penetrate the opposite band the same day, the trade closes but does not reverse; the next day, penetration of either band signals a fresh long or short. **Benefit noted**: allows re-entry in the same direction after a false trend change if price pulls back, at a possibly better price, and halves order size (improving execution/liquidity for large traders). For a genuinely trending market, using the intraday high (longs) / low (shorts) as trigger rather than the close "should produce some extra profits." **Risk note**: using the trendline as exit limits risk to half the full band width, but if bands are narrow, an intraday-high entry might be exited below the trendline on the same day's close (Kaufman Ch.8).

**Bollinger Bands** (Kaufman Ch.8): most common construction = 20-day MA ± 2 standard deviations of price changes over the same 20-day period (popularized by John Bollinger). Because prices are not normally distributed, 2 standard deviations equates to only an ~87% confidence band (vs. the 95.4% a true normal distribution would give). **Definitional note**: "if it's not a 20-day average and 2 standard deviations, it's not a Bollinger band" — the specific parameters are part of the named indicator's definition, not just an example. A characteristic behavior: once price moves outside a band, it tends to remain outside for several consecutive days (a momentum-like pattern); band width varies with volatility and shows a "bubble" (temporary widening) that persists past the point where volatility itself has declined.

- **The "Squeeze"**: a Bollinger-band variation on price compression — wait until the band compresses to some percentage of its average width (e.g., 50%), then buy or sell the breakout through the bands. **Cited as historically successful as a filter**, with trading in the direction of the prevailing trend improving performance further (cited to Kent Calhoun, 2016) (Kaufman Ch.8).
- **Modified Bollinger Bands (Dennis McNicholl correction)**: addresses the problem that standard Bollinger bands expand quickly after a volatility spike but are slow to narrow back down as volatility declines (the "bulge" effect). Center line D uses an exponential-smoothing-style formula with smoothing constant α = 0.15 (chosen to approximate a 20-day MA); the band-width multiplier f is suggested at **2.5** (vs. Bollinger's standard 2.0). Result (gold futures, first half of 2009): the modified bands don't eliminate the volatility bulge, but correct/narrow faster and envelop prices more uniformly than the original. **Gap flagged**: the exact center-line and upper/lower-band combining formulas are embedded graphics not recoverable as clean text; the α=0.15 and f=2.5 parameters are preserved (Kaufman Ch.8, citing Dennis McNicholl, "Better Bollinger Bands," *Futures*, Oct. 1998).
- **Combining Bollinger with other indicators (Williams' method)**: cited to Billy Williams, "Biting off Profits with the Rattlesnake Breakout Method," *Futures*, Oct. 2010. Combines (1) a standard 20-day/2-stdev Bollinger band, (2) a 20-day Keltner Channel, (3) a 21-day Chaikin Oscillator. **Long entry (all required)**: Bollinger bands narrow to fully inside the Keltner Channel AND the Chaikin Oscillator is below zero; THEN the Chaikin Oscillator crosses above zero. **Short entry**: mirror image (Kaufman Ch.8).

### Volatility System (Bookstaber) and the 10-Day Moving Average Rule

Two named ATR-based always-reversing breakout systems appear in the Kaufman Ch.8 indicator inventory:

- **Volatility System** (Bookstaber, cited 1984): trend defined by an unusually large single-day move relative to the n-day ATR. Sell if close falls more than k×ATR from the prior close; buy if close rises more than k×ATR from the prior close; k ≈ 2.0 (Kaufman Ch.8, Indicators.md).
- **10-Day Moving Average Rule** (Keltner, 1960): a 10-day MA of (H+L+C)/3, with a band equal to the 10-day MA of the high-low range (approximately a 10-day ATR); an always-reversing breakout system. Historically, the required division was a simple decimal shift, a convenience feature for the pre-calculator era (Kaufman Ch.8, Indicators.md).

### Volatility Breakout in Day Trading (Kaufman Ch.16)

The day-trading volatility-breakout construction (open-basis or previous-close-basis bands scaled by a percentage of n-day ATR) is documented in full under "Opening Range Breakout Systems" above; the shared mechanic — band = anchor price ± breakout factor × n-day ATR, breakout factor typically <1.0 — is the same volatility-breakout logic applied at intraday granularity rather than daily. A secondary-source restatement of this same mechanic appears verbatim in the Indicators.md cross-reference: "Volatility-adjusted opening-range breakout bands: bands = open (or previous close) ± factor × n-day ATR, factor typically <1.0 since ATR is a daily-scale value; factor and n (5-20 days) are both tunable" (Kaufman Ch.16, Indicators.md).

### Intraday Price Shocks as a Volatility-Breakout Trigger (fade variant)

Kaufman Ch.16 also documents a volatility-triggered *fade* (mean-reversion) system rather than a trend-following breakout: **TSM Intraday Shocks 2** defines a shock as an intraday bar with volatility at least a specified multiple of the 20-day average bar volatility (general shock definition: at least 2x the average of previous bars; this specific strategy's own default factor is 2.2, calibrated for gold). Entry: place a short-sale limit order at the current bar's close + factor × 20-day average bar volatility; place a buy limit order at the current bar's close − factor × 20-day average bar volatility. Exit when the current bar's volatility falls back below the 20-day average, or on the second-to-last bar of the day. Backtested on gold, 2010–April 2017 — profitable overall with >50% winning trades (Kaufman Ch.16). See `03_mean_reversion.md` for the general mean-reversion framing of volatility-spike fades.

### Renko Bricks — a Volatility-Adjacent Fixed-Increment Method

Renko bricks (from the Japanese "renga") assign a fixed price range to each "brick"; each higher brick is recorded one box up and one to the right, each lower brick one box down and one to the right, always at a 45° angle — larger brick size smooths price movement more (Kaufman Ch.5). **Shared weakness with point-and-figure**: as a fixed-increment method, Renko becomes more sensitive as price rises and less sensitive as price falls — the same asymmetry problem discussed for P&F box sizing. A percentage-based increment is suggested (untested in the source text) as a possible fix; a constant-sensitivity system is generally preferred (Kaufman Ch.5).

---

## Gap Statistics (Kaufman Ch.3 / Bulkowski)

### Gap Types

Kaufman Ch.3 defines an upward gap as today's low exceeding yesterday's high (meaningfully possible mainly for markets with a closed session — e.g., equities at the open, or futures over a weekend/Globex reopen; economic releases at 7:30am Central can cause SPY gaps up to an hour before the cash open since the S&P E-mini trades continuously). **Four gap types** (illustrated on Amazon.com in the source, Figure 3.13):

1. **Common gap** — no particular significance, not tied to a specific chart level.
2. **Breakaway gap** — occurs at a clear support/resistance level from a cluster of orders; the term is applied *retrospectively* — only called "breakaway" if followed by a sustained move. Trading it requires an order placed *in advance* as price approaches the level. If a long position gaps up, that is "free exposure" (profit with no execution cost); if it doesn't gap, price often drifts lower and the trade should be exited for a small loss and potentially re-entered.
3. **Exhaustion gap** — occurs at the end of a sustained, volatile move; confirms the reversal; typically occurs the day after (occasionally later) the extreme price.
4. **Runaway gap** — occurs mid-trend and confirms the trend; has "no practical use" as a standalone signal since the trend could reverse right after it (in which case it becomes an island top in hindsight); still, holding a long through an upward runaway gap adds profit but signifies "extreme risk."

**Gap-fill folklore, per the source**: nearly all gaps eventually fill given enough time, but the most important (breakaway) gaps are not filled for a long time — they mark a genuine regime shift (Kaufman Ch.3).

### Bulkowski's Gap-Closure Statistics (Table 3.1) — CONFIRMED PRESENT

The extraction does contain a Bulkowski gap-statistics table. Table 3.1, "% of gaps closed within 1 week," sample of 100 stocks (Kaufman Ch.3, citing Thomas N. Bulkowski, *Encyclopedia of Chart Patterns*, 2nd ed., Wiley, 2005, and *Encyclopedia of Candlestick Charts*, Wiley, 2008):

| Gap Type | Uptrend | Downtrend |
|---|---|---|
| Breakaway | 1% | 6% |
| Continuation | 11% | 10% |
| Exhaustion | 58% | 72% |

**Conclusion drawn from the table**: breakaway gaps rarely fill and thus favor trend-continuation strategies (N-day breakout, swing trading, pivot-point breakouts) — but the source explicitly qualifies this "only when the observation period exceeds 40 days, the minimum considered to be a macrotrend" (Kaufman Ch.3).

### Kaufman's Own Gap Study (275 stocks, 2012–2017)

A separate, non-Bulkowski gap study conducted by the author himself (Kaufman Ch.3):

- **Upward gaps > 1%** consistently pulled back intraday (~40% average pullback from the high) yet still tended to close near the day's high. Table 3.2 example figure: a 1-3% higher open shows ~31.26% frequency of occurrence, ~-1.45% average pullback, and ~+0.01% average close vs. prior close.
- **Downward gaps** behaved differently, reflecting stocks' general upward bias — pullbacks from the low were larger and the close was consistently *higher* than the gap open. Table 3.3 example figure: a 1-3% lower open shows ~27.50% frequency, ~+1.53% pullback, ~+0.11% close.
- **Practical implication stated**: most trading opportunity from a gap occurs early in the session (Kaufman Ch.3).

### Bulkowski's Candlestick-Performance Findings (adjacent, not gap-specific, but same author/source)

Also present in Kaufman Ch.3, cited to Bulkowski's own research summary — not a gap-fill statistic but a related candle-performance finding worth flagging alongside the gap tables since it comes from the same cited author and methodology:

- Best-performing candles have closing prices within ⅓ of the bar's low, then the middle third, then the high third (in descending order of performance).
- Candle patterns perform better in a bear market than other market types, regardless of breakout direction.
- Most candles perform best on higher-volume days.
- Candles with unusually long wicks (shadows) outperform.
- Unusually tall candles outperform.

(Kaufman Ch.3, citing Thomas Bulkowski, "What You Don't Know About Candlesticks," *Technical Analysis of Stocks & Commodities*, March 2011.)

### Gap Trading Rules (Kaufman Ch.3)

- **Common gap**: take a position counter to the gap direction, expecting a fill; exit with profit at fill or liquidate if unfilled after a few days.
- **Breakaway gap**: place a buy order just under resistance ahead of a clear sideways pattern to capture the "free exposure" jump.
- **Runaway gap**: a good point to *add* to an existing position, confirming the move.
- **Exhaustion gap**: highly risky to trade as it occurs; sell into the move with a stop above the prior high — if wrong, price could explode higher, but if right, profits can be large.

### Ch.16 Gap Material (Intraday "True Gaps")

Kaufman Ch.16 defines a "true" gap (DeMark/Larry Williams terminology) as a market opening above yesterday's high (or below yesterday's low) that does **not** trade back to that level — a stronger form of gap than the general Ch.3 definitions above. See "Opening Range Breakout Systems" above for the full True Gap Patterns entry rules and the finding that entry on pullback-to-previous-close plus exit-on-next-open tested best on 15-30 minute data (Kaufman Ch.16).

---

## False Breakouts and Breakout Failure (Kaufman / Chan / Pardo)

### Failed Breakouts as Chart Events (Kaufman Ch.3)

- **Failed breakout (bar-chart definition)**: a bar whose high penetrates resistance but which closes back below it (or the symmetric case at support) confirms the opposite (failed) move. Most chartists leave the resistance/support line at its original level rather than raising/lowering it to the failed bar's extreme (Kaufman Ch.3).
- **Role reversal**: once broken, resistance tends to become the new support (and vice versa) — the market treats the break as new information causing a durable shift; if price falls back below a broken resistance line, that itself is a failed breakout (Kaufman Ch.3).
- **Bull and bear traps**: a **bear trap** = a failed downside breakout (price falls below support, generating sells, then reverses back above, often accelerating upward); a **bull trap** is the mirrored failed upside breakout. **Explicit statement: no general method is given to avoid traps** — the guidance is only to recognize the failed reversal as quickly as possible and reverse the position; traps "often precede significant price reversals." Confirmation of a trap/failed-pattern is complete once price retraces the entire original pattern and clears the next resistance/support level beyond it (Kaufman Ch.3).
- **Markets move sideways an estimated 80% of the time** — sustained directional breakouts are relatively rare, or (implicitly) many apparent breakouts are false (Kaufman Ch.3, "Consolidation vs. Directional Patterns"). This statistic is presented as a stated fact about market behavior, not a specific breakout-failure-rate measurement.
- **Volatility-regime caveat on breakout reliability**: every market has a baseline noise level (e.g., stock indices show the most irregular movement due to broad participation and anticipation-driven pricing; Eurodollars show large participation but little anticipation, hence less noise). A volatility increase back up to the market's *normal* noise level should not be mistaken for a genuine breakout. This directly affects triangle/consolidation interpretation: if a pattern's apex compresses to *below* the market's normal noise floor, the eventual "breakout" may just be a reversion to normal noise rather than a meaningful directional signal — such breakouts "are not reliable buy/sell signals" (Kaufman Ch.3).
- **Two opposing, explicitly unresolved camps on volatility and breakout reliability**: the source states plainly that some analysts believe breakouts after *low* volatility are more reliable, while others believe breakouts associated with *high* volatility are more reliable — the author does not resolve this disagreement (Kaufman Ch.3).
- **Tighter/narrower support-resistance lines drawn during low-volatility consolidations produce less reliable breakout signals** — they may just represent noise inside a larger, quieter regime (Kaufman Ch.3).
- **Wyckoff's "effort and results"** (cited by Kaufman): a pattern's *failure* to hold is itself an important, tradeable signal — e.g., a clean break of a support line that traders expected to hold should trigger short entries and abandonment of the bullish thesis, not stubborn adherence to the "expected" reversal; if the market's effort (a chart pattern's implied setup) is not followed by the expected result, trade the opposite direction (Kaufman Ch.3).

### Whipsaw Mitigation Techniques (Kaufman Ch.3, Ch.5, Ch.8)

- **Trendline delay techniques** (Kaufman Ch.3): (1) wait one or two days to confirm price remains on the new side of the trendline; (2) wait for a reversal after the initial penetration, then enter in the new-trend direction even if that reversal re-crosses the trendline; (3) create a small safety band/channel around the trendline, requiring price to clear both the trendline and the band before entering. **Explicit trade-off**: delay usually gives a better entry price, but if price moves quickly through the trendline without reversing, delay produces a worse entry — and "most of the biggest profits result from breakouts that never pull back," so waiting-for-better-price traders can systematically miss the largest moves (Kaufman Ch.3).
- **Small band around a moving-average crossover** (Kaufman Ch.8): if too many losses come from short-held trades in a two-trendline crossover system, a small band placed around each trendline (requiring a clear penetration through the upper/lower band before flipping) can filter out marginal whipsaw crossovers (Kaufman Ch.8).
- **Point-and-figure confirmation thresholds** (Kaufman Ch.5): raising the P&F confirmation requirement from a basic 1-box breakout to 2, 3, or 4 boxes as volatility increases filters out false breakouts occurring during erratic sideways or expanding-after-low-volatility patterns — effectively demanding accelerating momentum before committing (Kaufman Ch.5).
- **Contingent-entry risk (explicit caveat, Kaufman Ch.8)**: a contingent entry rule conditioned on further price action (e.g., waiting for a pullback before entering a breakout) risks never entering at all — "a contingent order that is missed is guaranteed to be a profitable trade" (i.e., survivorship bias in evaluating skipped trades). **Empirical finding cited from multi-year tests of trend-following systems**: delaying execution from the signal close to the next open improved the entry price about 75% of the time, but *reduced* overall total profits — because fast breakouts that never retrace are missed entirely, and those missed profitable breakouts outweighed the 75%-of-time small price improvements (Kaufman Ch.8).
- **"Not All Entries Should Be Anticipated" (Kaufman Ch.8)**: a 10-year Eurodollar vs. S&P comparison across five calculation periods found that for the low-noise Eurodollar, entering sooner was more profitable in all but one case; for the high-noise S&P, waiting until the next close was favored and short-term trends were unprofitable — attributed to higher market noise in the S&P. This is presented as evidence that whipsaw-avoidance tactics (delay, confirmation) should be calibrated to the specific market's noise level, not applied uniformly.

### False-Breakout Filtering in Named ORB Systems (Kaufman Ch.16)

Several of the day-trading ORB systems documented above build false-breakout filtering directly into their rule sets, rather than treating it as a separate topic:

- **Crabel's ORB**: inside-day, low-volatility, and "bull/bear hook" preceding-pattern filters are reported to raise the percentage of profitable trades relative to unfiltered ("Any Day") signals across every market shown in Table 16.4 (Kaufman Ch.16).
- **Fisher's ORB**: the required "hold beyond the threshold for ½ the OR time" rule exists specifically because a short opening-range window otherwise produces too many false signals (Kaufman Ch.16).
- **Williams' Filtered ORB**: both entry methods require the prior day not be an inside day and impose specific multi-day close-comparison conditions, explicitly built to filter out setups without genuine trend confirmation, particularly for the more trend-sensitive bond/interest-rate variant (Kaufman Ch.16).
- **Rudd's "Reversing After a False Breakout" pattern**: an explicit false-breakout-fade rule — IF a breakout of the Consolidation pattern fails and price falls back into the original range, THEN close the long and sell short, expecting a support breakdown (Kaufman Ch.16). See `03_mean_reversion.md` for the general fade-the-failed-breakout framing.

### False-Signal / Overfitting Risk in Breakout-System Design (Pardo, secondary source)

Pardo's book is explicitly about testing/optimization methodology rather than a strategy catalog, and it uses the **Turtle Trading Strategy (TTS)** — an N-day-high/low channel breakout attributed to Richard Dennis, based on Richard Donchian's range-breakout work — as its illustrative example of an "information-poor" systematic strategy (Pardo, Strategies.md). Pardo's own entry/exit description: "Goes long when an x-day high has been penetrated and goes short when an x-day low has been broken," exiting "on opposite signals from a shorter y-day high or low" — a bare two-parameter channel-breakout structure with **no additional filters disclosed** ("Pardo emphasizes TTS in this simplified form uses NO additional information beyond the breakout levels themselves").

- **Failure/decay note, secondhand**: Pardo reports (via Art Collins, unverified in-text beyond this citation) that Richard Dennis himself said "the Turtle Trading Strategy doesn't work anymore." Pardo separately states in his "Life Cycle of a Trading Strategy" discussion that "the principal driver of the Turtle Trading system no longer works," while also noting that variants reportedly produced "hundreds of millions of dollars" in profits during the years the system did work (Pardo, Strategies.md). This is presented as an example of strategy decay/regime dependence for a channel-breakout system specifically, not a general claim about all breakout systems.
- **Gap flagged**: Pardo's TTS description does not specify market conditions, timeframes, assets, position sizing, or risk rules beyond the bare breakout rule — the book states "there are other variations" of the historical Turtle rules but does not detail them, explicitly calling them "ignored for the sake of this illustration." (Contrast with Kaufman Ch.5's own more detailed Turtles System 1/System 2 reconstruction, covered in `02_trend_following.md`, which likewise self-describes as "a simplified reconstruction ... not a claim of complete original fidelity.")
- **Relevance to false breakouts/whipsaws specifically**: Pardo's broader methodological point (illustrated elsewhere via the Two-Moving-Average Crossover teaching example, not a breakout system per se) is that adding filter parameters to suppress whipsaws/false signals can inflate in-sample performance while degrading out-of-sample robustness — the Ch.13 "overfit trading model" parable shows an MA-crossover-plus-volatility-band variant whose in-sample profit is progressively inflated from $10,000 to $65,000 by adding parameters, only for the final over-parameterized version to **lose $15,000 out-of-sample** (Pardo, Strategies.md). This is a general overfitting warning rather than breakout-specific, but it is directly applicable to the temptation to add ever more false-breakout filters (inside-day filters, compression filters, trend filters, band buffers) to a channel-breakout or ORB system, as Kaufman Ch.16's own parameter-selection case study also cautions against testing filters simultaneously rather than one at a time.

### Chan (secondary source) — No Direct Match

A targeted search of the Chan Quantitative Trading extraction's Strategies.md file for "breakout," "whipsaw," or "false signal" content returned no matches. **Gap flagged**: the extraction of Chan's book, as captured, does not appear to contain a dedicated breakout-system or false-breakout-failure discussion in Strategies.md; the only Chan-sourced breakout-adjacent material located in this research was the regression-based "Programmed Channel Breakout Bands" entry in Chan's Indicators.md file (cited above under "Channel Construction Rules"), which is a channel-construction mechanic rather than a false-breakout discussion.

---

## Summary Cross-References

- For the trend-following framing of N-day/Donchian/Turtles breakout mechanics (full six-system comparison tables, position sizing, compounding, portfolio drawdown rules), see `02_trend_following.md`.
- For fading failed breakouts and volatility-spike mean reversion as trading strategies in their own right, see `03_mean_reversion.md`.
- For momentum/RSI-style confirmation filters layered onto breakout entries (e.g., Momentum Pinball's LBR/RSI, Williams' %R filter), see `05_momentum.md`.
- For the day-trading-specific material this file draws breakout content from (transaction costs, slippage, HFT, intraday volume/volatility patterns), see the day-trading-focused knowledge base file, if one exists as a separate numbered file in this knowledge base.
