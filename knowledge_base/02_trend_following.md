# Trend Following

This file is the largest of the knowledge base because trend following is the dominant subject of Kaufman's *Trading Systems and Methods* — it spans event-driven (price-extreme) methods, time-based (moving-average/regression) methods, adaptive methods, and multi-timeframe methods. Every claim below is tagged to its source chapter. Where a source explicitly flags a formula as unrecoverable from PDF extraction ("embedded graphic gap") or as a reconstruction from a standard published form (not verbatim from the book), that flag is preserved rather than silently resolved. See `01_market_structure.md` for background on the Efficiency Ratio and noise concepts referenced repeatedly below; see `04_breakouts.md` (if present) for pure breakout mechanics detail; see `05_momentum.md` for ROC/TRIX treated as momentum oscillators rather than trend filters; see the volatility knowledge base file for volatility-based position sizing and stops referenced throughout.

---

## Why Trend-Following Works: Fat Tails (Kaufman Ch.8)

Kaufman gives four explicit reasons trend systems work (Kaufman Ch.8):

1. **Long-term trends capture large price moves caused by fundamental factors.** Economic trends are most often rooted in government interest-rate policy, which is slow-developing and incremental; interest rates in turn affect FX, trade balance, mortgage rates, carrying charges, and the stock market.
2. **Persistence.** Some price moves defy valuation-based analysis and keep rising — only staying with the trend captures the gains of stocks like Apple, Amazon, Tesla, and **Bitcoin** ("In the case of Bitcoin, extreme trends have been both up and down.") — this is the book's first crypto mention, occurring specifically in the trend-following chapter.
3. **Prices are not normally distributed but have a fat tail** — an unusually large number of directional price moves are far longer than a random distribution would predict. Profits from the fat tail are described as essential to trend following's long-term success.
4. **Money moves the markets.** Most trends are supported by the flow of investor funds; this generates short-term noise but also delivers long-term trends, since as a trend becomes clearer more money flows in to extend it.

**Explicit caveat (Kaufman Ch.8)**: trend trading works only when the market is trending; it does not work in sideways markets, and there is no universally best trending technique — most trending methods have similar returns over time but different risk profiles and trading frequency.

### How Often Do Markets Trend?

There is no agreed measurement. One analyst's definition (10 consecutive closes in the same direction) is called arbitrary by the author. **Kaufman's own operational definition**: "A trend exists if you can profit from the price moves using a trending strategy" — trend is a relative concept depending on the trader's time horizon and the frequency/size of price swings the trader can accept (Kaufman Ch.8).

### The Fat Tail, Illustrated

Via coin-flip runs (random/binomial expectation for 100 tosses): 50 runs of length 1 (opposite-follows), 25 runs of 2, 12.5 runs of 3, ~6 runs of 4, ~3 runs of 5, 1-2 runs of 6. If price moves followed this random distribution (with up/down moves of equal size), a trend system could not profit. Because prices are *not* normally distributed, actual markets show more long runs (e.g., one run of 12, or three runs of 6) and correspondingly fewer short runs — the fat tail is created by "stealing" frequency from short runs, not by adding total moves (Kaufman Ch.8, Figure 8.1). Cross-referenced in the source to "Gambling Techniques: The Theory of Runs" (Ch.22).

### Distribution of Profits and Losses

A 40-day simple-moving-average strategy (buy when the trendline turns up, sell short when it turns down) applied to five diverse futures markets (30-yr bonds, S&P, euro, crude oil, gold) produces trade profit/loss histograms extended far to the right (a fat tail of large wins) with a much shorter left tail (small, frequent losses). Example: in the S&P results, one $18,750-bin profit offset 15 losses in the highest-frequency −$1,250 bin. **Key stated principle**: a pure trend strategy needs this asymmetric distribution shape to be profitable (Kaufman Ch.8, Table 8.1 — the full cross-market numeric bin table was not cleanly recoverable from PDF extraction and is flagged as a gap; the S&P's specific numbers and the general fat-right/short-left shape are reliable).

### Market Character and Trend Clarity

- Trends are clearest on long-term/weekly charts; stepping back in time frame clarifies the trend (daily→weekly clearer; daily→hourly is mostly noise). Lower-frequency data produces better performance with longer-term trends; fast trends that show backtest profits tend to be less stable (Kaufman Ch.8).
- **Sector differences**: interest-rate futures, money markets, and utility stocks are closely tied to government rate policy and can trend for years. FX is more complex (subject to central-bank intervention) and generally shows clearer but shorter trends than interest rates. Equities are driven by many idiosyncratic factors that often don't net into a clear trend; index-arbitrage flows can drag individual shares contrary to their own fundamentals. Emerging markets trend strongly while lightly traded/dominated by commercials, then require longer time frames as public participation and noise increase (Kaufman Ch.8).
- **General guidance**: match calculation period, data frequency, and market choice together — longer periods, lower-frequency data, and fundamentally-driven markets all favor trend following (Kaufman Ch.8).

---

## Event-Driven Trend Systems (Kaufman Ch.5)

**Framing**: event-driven methods ignore time entirely — a trend is defined purely by the extent of price movement (new highs/lows by a minimum amount), not by how long it takes, in contrast to the time-driven methods (moving averages, etc.) covered later. Kaufman's explicit challenge to the reader: as later chapters introduce more mathematically intricate methods, continually ask how much genuine improvement they offer over these older, simpler event-driven approaches (Kaufman Ch.5).

### Swing Trading

**Core definition**: a **price swing** is a price movement up or down by a preset minimum size (the **swing filter**). A new upward swing starts when price reverses from the lows by the filter size; new highs are recorded until price turns down from the swing high by the filter amount, then the reverse. The distance from any swing high to the next swing low is never smaller than the swing filter. The filter can be expressed in cents, dollars, or as a percentage of current price.

- **Percentage swings preferred for robustness**: a fixed dollar/point filter is insensitive at low prices and overly sensitive at high prices; a percentage filter keeps sensitivity consistent across a long price history — important for backtesting and consistent signals. The filter recalculates only at each new swing high/low, not continuously (Kaufman Ch.5).

**Constructing a classic swing chart (algorithm, Kaufman Ch.5)**:
1. Start at any point (the very first swing's accuracy may be off). Record the high of the starting bar as the last swing high (SH); the following period is treated as a downswing. Record that bar's low as the current swing low (CL).
2. Next bar: if Low < CL, then CL = Low (downswing continues).
3. Test reversal: if High − CL > swing filter, a new upswing begins. Set new swing low SL = CL and CH (current swing high) = High.
4. Next bar: if High > CH, then CH = High (upswing continues).
5. Test reversal: if CH − Low > swing filter, a new downswing begins.
6. Return to step 2.

The reference implementation (TSM Swing) tests for a reversal *before* testing for trend continuation. These rules are noted as very similar to point-and-figure construction rules (below).

**Entry rules (two rule sets, Kaufman Ch.5 and Strategies.md)**:
1. **Conservative**: Buy when the high of the current upswing exceeds the high of the *previous* upswing (two columns back); sell when the low of the current downswing falls below the low of the previous downswing.
2. **Aggressive**: Buy as soon as a new upswing is recognized; sell as soon as a new downswing is recognized (i.e., on the first reversal greater than the swing filter, in either direction) — always in the market.

**Strengths (Kaufman's swing philosophy, Ch.5)**:
- **No action during sideways markets**: unlike a moving average (which "has an agenda" — price must keep advancing to maintain trend status), a swing/event-driven approach lets price move sideways or stand still within a trend without triggering an exit, as long as prior swing highs/lows in the relevant direction are not violated.
- **Robustness at the cost of higher risk**: risk = the difference between entry price (where the old swing high/low was penetrated) and the exit/reverse trigger price — can be as small as the swing filter or much larger after a sustained move.
- **No-lag response to genuine news events**: because the method is purely price-extreme-based, it reacts immediately to a genuine surprise that pushes price to new highs/lows, unlike moving-average-based trend systems, which inherently lag.

#### The Livermore System

Jesse Livermore (active 1910-1940). Developed pattern recognition from marking prices on exchange slate boards; tracked prices in columns headed Secondary Rally, Natural Rally, Up Trend, Down Trend, Natural Reaction, Secondary Reaction — believed a basis for later systematic charting methods (Kaufman Ch.5).

- **Two filters**: a larger **swing filter** and a **penetration filter** believed to be ½ the swing filter's size (though Kaufman notes this is not entirely clear from Livermore's own materials — could be as small as 20% of the current swing size).
- **Pivot points**: defined retrospectively as the top/bottom of each new swing.
- **Trend definition**: a major uptrend = confirmed higher highs and higher lows, with the penetration filter not broken in the reverse direction (mirror logic for downtrends).
- **Entry/position building**: positions are added each time a new penetration occurs confirming the trend direction; a stop-loss is placed at the point of penetration beyond the prior pivot point.
- **Failed Reversal rule**: the *first* penetration of the stop-loss (a new swing high for a short, or swing low for a long) triggers liquidation of the current position, but a *second* penetration is required to confirm a genuine new trend. If that second penetration fails, it is treated as a secondary reaction within the old trend (not a reversal) — the old trend may be reentered at a distance of one swing filter below/above the failed reversal point, and again on the next swing at the next penetration level. **Explicit rationale**: it is easier to reenter an established trend than to establish a position in a brand-new one (Kaufman Ch.5).

#### Keltner's Minor Trend Rule

From Chester Keltner, *How to Make Money in Commodities* — historically influential among agricultural traders for its simplicity.

- **Trend definition**: an uptrend = failure to make new lows (today's low vs. prior day's low); a downtrend = absence of new highs.
- **Trading rule**: the minor trend turns up when price trades above its most recent high, down when price trades below its most recent low; always reverse on a trend-turn signal (always in the market).
- **Character**: a simple, short-term, always-reversing tool with **no minimum size requirement for a reversal**, so it produces many more (smaller) swings; risk varies with volatility rather than a fixed filter (Kaufman Ch.5).

#### Wilder's Swing Index (SI) and Accumulated Swing Index (ASI)

J. Welles Wilder Jr., *New Concepts in Technical Trading Systems* (1978). Combines daily range measurements with pivot-point-based trading signals — an event-driven method despite using a daily calculation (Kaufman Ch.5).

- **Five positive uptrend patterns** (reversed for downtrend): (1) today's close > prior close; (2) today's close > today's open; (3) today's high > prior close; (4) today's low > prior close; (5) prior close was above prior open.
- **Swing Index (SI)**: combines these five factors, scaled into a range of +1 to −1, using K (the largest of certain range-based terms), M (the "limit move" value, below), and TR (a weighted true range computed via a two-step largest-of-three process). **Gap flagged in source**: the exact combining arithmetic for K, TR-step-1, and TR-step-2 is embedded as a graphic in the original PDF and did not survive text extraction.
- **Updating M for modern (non-limit-move) markets**: since M only rescales SI into ±1 and the trading rules use only relative highs/lows of ASI (not fixed thresholds), an arbitrary M larger than the normal daily move works fine — the book's own examples use M=100 (TSM Wilder Swing Index).
- **Accumulated Swing Index (ASI)**: the running sum of daily SI values, substituted for price to generate trading signals.
- **Key ASI-derived terms**: **HSP** (High Swing Point) = a day where ASI is higher than both neighboring days; **LSP** (Low Swing Point) = a day where ASI is lower than both neighbors (both have an inherent 2-day confirmation lag). **SAR (Stop and Reverse)** — three types: Index SAR, SAR applied to a specific price, and Trailing Index SAR (lags 60 ASI points behind the best ASI value reached during the trade).
- **Trading rules**: (1) go long when ASI crosses above the most recent HSP; go short when ASI crosses below the most recent LSP. (2) SAR placement (long) = most recent LSP, reset to first LSP after each new HSP; trailing SAR = lowest daily low between the highest HSP and the day ASI drops ≥60 points. (3) SAR placement (short) mirrors the long rules.
- Reference implementations: TSM Wilder Swing Index and TSM Accumulated Swing Index; note that the TradeStation library version requires a preset limit-move value per market, unlike the book's own version.

#### Pivot Points (cross-reference)

A pivot point is the high or low point of a reversal — a much weaker condition than a swing high/low, with no minimum size requirement. A 5-day pivot point (2 days each side) has an inherent 2-day confirmation lag (Kaufman Ch.5, cross-referencing Ch.3/Ch.7).

### Point-and-Figure Charting

Credited to Charles Dow (used just prior to 1900); earliest documented source *The Game in Wall Street* by "Hoyle" (1898); first definitive treatment by Victor De Villiers (1933), working with Owen Taylor (Kaufman Ch.5).

- **Three defining characteristics**: (1) simple, well-defined trading rules; (2) ignores reversals below the minimum move set by the box size; (3) no time factor — purely event-driven.
- **De Villiers' three philosophical premises**: (1) a stock's price at any instant is its correct valuation per the consensus of all buyers/sellers and the forces of supply/demand; (2) the last price reflects/crystallizes everything known about the stock up to that point; (3) even insiders with superior knowledge cannot conceal their future intentions — their plans reveal themselves through subsequent price action.
- **Chart mechanics**: an upswing column is a series of boxes marked X; a downswing column is a series marked O. A new mark requires price to reach the box's minimum increment (the **box size**).

**Plotting rules**:
- **Box size selection**: as a starting point, use the **20-day average true range** as the box size (2017 examples: S&P 15 points, gold $4, crude oil $1.10, Apple $2.75, Walmart $1.50). Larger box = less sensitive/longer-term view; smaller box = more sensitive.
- **Continuation preference**: if trend is up (column of Xs), test the new high price first; if down, test the new low first. A reversal is only checked if the new price fails to extend the current column.
- **3-box reversal (traditional standard)**: price must reverse enough to fill 3 boxes from the extreme box of the last column before a new column starts (a 4th box must actually be filled since the extreme box itself is left blank). The **net reversal amount** (box size × number of reversal boxes) functions analogously to a swing filter. Example: a 25-point box with 3-box reversal on NASDAQ 100 futures requires a 75-point reversal to flip trend; a 3-point box with 25-box reversal produces the same 75-point threshold but captures more of intermediate moves.
- **Trendlines**: bullish/bearish 45° diagonal trendlines drawn from the corner of a top/bottom formation's blank extreme box, used to filter basic P&F signals (trade only long when the 45° trendline is up, only short when down).

**Point-and-figure formations**: Robert E. Davis (1965, *Profit and Profitability*) examined 2 stocks (1914-1964) and 1,100 stocks (1954-1964) to find the most reliable of 8 buy/sell formations. **Best buy signal**: ascending triple top. **Best sell signal**: breakout of a triple bottom. For futures (fewer unique formations), the basic approach dominates: buy = an X one box above the highest X of the last X-column; sell = an O one box below the lowest O of the last O-column.

**Finding the box size**: box size (given a fixed 3-box reversal) is the single most important variable, analogous to a moving average's calculation period.
- Historical studies: Thiel & Davis (1970) found 53% of trades profitable in a strong-trend period; Zieg & Kaufman (1974, 22 commodities, 6-month extremely active period) found only 40% of 375 signals profitable, average duration 12.4 days (vs. 50 days in the Davis/Thiel tests) — evidence that price moves were accelerating.
- Chartcraft's fixed-grid method kept the number of vertical boxes on a page constant and adjusted the box size so the period's full price range fit — effectively auto-adjusting box size for volatility, at the cost of signals changing periodically.
- Kaufman's own 2000-2017 re-test (futures + stocks) found best-performing box sizes, given a 3-box reversal, generally favored **large reversals** → long trends, fewer trades; long positions were profitable across nearly all tested markets; Bank of America (2008 crisis) and Walmart (narrow multi-year range) failed the robustness test.
- **The Box Size Dilemma (explicit, unresolved problem, Kaufman Ch.5)**: a small reversal size suits low-priced, consistent trends; a large reversal size suits high-priced, volatile moves. A single market spanning both regimes over its history is unlikely to be profitably tradeable with one fixed reversal criterion across the whole period. Proposed (imperfect) solutions: (1) Chartcraft's fixed-grid approach; (2) Zieg & Kaufman's variable-size box (larger at higher prices); (3) ATR-based dynamic box sizing (same issue — a position opened during high volatility might reverse if volatility later drops). **Kaufman's own assessment**: "consider this a problem yet to be solved."

**Trading techniques and risk**:
- **Basic signals**: buy when the X-column rises one box above the previous X-column's high; sell when the O-column falls one box below the previous O-column's low.
- **Difference from swing charting**: a P&F signal requires filling a discrete box, whereas any move above a previous swing high triggers a swing-chart signal immediately — P&F is inherently coarser/more delayed.
- **Three risk-limiting entry alternatives**: (1) wait for a pullback to an acceptable risk level, then enter with the standard P&F stop — **explicit caution**: it is *not* advisable to enter on the original signal with an arbitrary stop 3 boxes below the highs, since such a stop "has no logical basis and can quickly result in a losing trade"; (2) enter on the second reversal in the direction of the original signal (skip the first pullback, place a trailing buy order 4 boxes above the low of the O-column) — reduces risk to 4 boxes and can avoid a whipsaw, but may miss the trade entirely if price never pulls back; (3) require a confirming new high (raise confirmation from a 1-box breakout to 2, 3, or 4 boxes as volatility increases) to filter false breakouts.
- **Stop placement**: quoting Jesse Livermore to Richard Wyckoff — "I go long or short as close as I can to the danger point, and if the danger becomes real I close out and take a small loss." A stop-loss is typically placed below the resistance line penetrated to enter.
- **A windfall profit**: a very large unrealized profit from a price shock is "an opportunity to take profits" (though noted to go "beyond the area of technical analysis"). **Explicit system-design warning**: "A trading system should not depend on a single, very large profit to prove its success" — an exceptional profit often reflects luck (a price shock), not skill. **General profit-taking caution**: taking small profits broadly "does not improve overall profitability because it most often misses the biggest moves" — the windfall guidance is an explicit narrow exception for extreme/shock moves only.
- **Alternative treatment of reversals**: on a highly volatile outside day, both a trend-continuation box-fill *and* a 3-box reversal can occur simultaneously; traditional rules record only the continuation. Kaufman's own tested alternative — record the reversal first — generally produces an earlier stop-loss/trend change and was confirmed by testing to work to the trader's benefit, except when the reversal value is small.
- Some analysts favor P&F specifically because both profit objective and risk are known at entry; some traders require a return-to-risk ratio > 2.0.

**Price objectives**:
- **Horizontal count**: upside H_U = P_L + (W × R); downside H_D = P_H − (W × R), where P_L/P_H = price of the lowest/highest box of the base/top formation, W = width of the formation in columns (excluding the breakout column), R = the reversal value (boxes × box value). Worked example (London Cocoa, £4 box, £12 reversal): a 19-column base added to a £570 base low gives an upside objective of £798; a wider-base alternative gives £870. Downside: a 9-column top gives £632; a narrower 5-column top gives £680 (the farther £632 target coincided with genuine intermediate support, illustrating that the "harder to reach" target can still be the more reasonable pick when it aligns with independent support/resistance). The same logic applies to a head-and-shoulders neckline-penetration distance or a triangle's widest point.
- **Vertical count**: uses the size of the first reversal column following an established bottom, multiplied by the market's minimum reversal size, added to the bottom's low (mirror for downside). Worked QQQ example: October 2002 low at $20.00, first reversal = 13 boxes × $0.25/box = $3.25; ×3 (minimum reversal boxes) = $9.75; + $20.00 = **$29.75 target**, reached May 2003. A secondary February 2003 low confirmed via convergence at $28.75. **Character**: essentially a volatility-based measure that can be quite accurate but tends to **understate** the expected move when inaccurate.

### Renko Bricks

From the Japanese "renga" (brick). Assigns a fixed price range to each "brick"; each higher brick is recorded one box up and one to the right, each lower brick one box down and one to the right, always at a 45° angle. Larger brick size smooths price movement more (Kaufman Ch.5).

- **Shared weakness with point-and-figure**: as a fixed-increment method, it becomes more sensitive as price rises and less sensitive as price falls. A percentage-based increment is suggested (untested in the text) as a possible fix; a constant-sensitivity system is generally preferred.

### N-Day Breakout

Described as "close on the heels of" swing and P&F methods, though not purely event-driven (time still plays a role in the fixed N-day window) — but shares the buy-new-highs/sell-new-lows behavior of true event-driven systems. One of the most popular trend-following techniques (Kaufman Ch.5).

- **Basic rules (always-in-market)**: Buy when today's high crosses above the high of the past N days; sell when today's low crosses below the low of the past N days.
- **Conservative variant (close-based)**: Buy when today's close is above the high of the past N days; sell when today's close is below the low of the past N days — confirms direction at the cost of a later entry.
- **Risk characteristic**: risk = difference between entry price and the point where an opposite N-day high/low would reverse the signal; larger N = larger risk.

#### Donchian's 4-Week Rule

Richard Donchian, mid-1970s; described by *Playboy's Investment Guide* as "childishly simple... recently discovered to rank premiere among a dozen widely followed mechanical techniques" (Kaufman Ch.5).

- **Rules**: (1) go long (cover shorts) when current price exceeds the highs of the previous 4 calendar weeks; (2) sell short (liquidate longs) when current price falls below the lows of the previous 4 calendar weeks; (3) for futures, roll to the next contract on the last day of the month preceding expiration.
- Historical validation: *The Traders Note Book* (1970, Dunn and Hargitt) rated it the best of the era's popular systems over 16 years of history.
- Closely resembles Keltner's Minor-Trend Rule, but modified (via the 4-week window) to trade less frequently.

#### Modifying the N-Day Rule

- **Volatility-adaptive N** (cited, Seidel and Ginsberg, 1983): N for today's calculation can be derived from the ratio of normal (longer-period) volatility to current (shorter-period, typically <¼ the longer period) volatility — as current volatility rises relative to normal, N decreases. **Gap flagged**: exact formula embedded as a graphic, not recoverable; the inverse volatility-ratio relationship is explicit (cross-reference: the adaptive-technique detail is deferred to Ch.17, below).
- **Calendar-quarter-based N for stocks**: N can be set as a multiple/fraction of a calendar quarter to relate trend length to earnings-announcement cycles.

#### Testing the N-Day Rule (Kaufman's own study, 2000-Nov. 2017)

Same market set as the P&F box-size study; tested N from 10 to 120 days in steps of 10 (23 tests/market). **Results**: average best calculation period ≈93 days; 7 of the markets were profitable across *all* tested N values; average 79% of tests profitable across all markets (vs. 63% for point-and-figure in the equivalent study); net profits for the breakout system were **more than 15× greater** than point-and-figure's. Kaufman's interpretation: this consistency across N adds confidence to the method's robustness.

#### Weekly Breakouts

Originated with Donchian's 4-Week Rule; the classic form only evaluates prices on Friday, since the Friday close is treated as the week's most important "evening up" price. **Typical rules**: buy (close shorts) if Friday's close exceeds the highest closing price of the past N weeks; sell short (close longs) if Friday's close is below the lowest closing price of the past N weeks.

- **Main drawback — high risk**: initial risk on a new long = the difference between the highest and lowest closing prices of the past N weeks; the position isn't liquidated until Friday's close (or Monday's open), which can amplify realized losses — offset somewhat by weekly data's smoothing benefit.
- **Programming caveat**: a "Friday" close should actually mean "the last close of the week" to correctly handle holiday-shortened weeks — best practice is native weekly data feeds rather than deriving week-end closes from daily data (avoids look-ahead/holiday bugs).

#### Dynamic Breakout System (DBS) — Stridsman

Thomas Stridsman ("Revelation Trading," *Futures*, Feb. 1998). **Core idea**: rather than a plain N-day high/low, anticipate entry/exit points one day ahead using a factor of the standard deviation of recent prices, and place stop orders for the next trading day. Study finding: exit-stop hit timing falls into two distinct groups (trades stopped out very quickly vs. held much longer) — a bimodal pattern suggested to help traders position stops more deliberately (Kaufman Ch.5).

#### N-Day Breakout: Stocks vs. Futures

Key structural differences: futures are generally less correlated across markets and offer much higher leverage; futures trading costs are close to negligible relative to contract face value (worked example: one S&P e-mini contract ≈ $5 commission on a $125,000 notional position, ≈ 0.00004% of notional), whereas stock trading runs closer to ~2.6 basis points for a typical <$30 stock. **Practical implication**: returns must be expressed per-contract (dollars) or per-share (cents) to fairly compare futures vs. stock breakout performance net of costs (Kaufman Ch.5).

### Donchian Channels (40/20 Channel Breakout)

Richard Donchian (Hayden Stone, 1960s) — credited as an early pioneer of both moving-average and breakout trend-following systems. The 40/20 Channel Breakout is the earliest recorded N-day breakout using **different periods for entry (longer, 40) and exit (shorter, 20)** — the direct conceptual predecessor of the Turtles' method (Kaufman Ch.5). See also "Donchian's 20- and 40-Day Breakout" under Ch.8 below, which is the same system framed as a trend-system example: entry = today's high > highest high of the past 40 days (long) / today's low < lowest low of the past 40 days (short); exit = today's low < lowest low of past 20 days (long) / today's high > highest high of past 20 days (short).

### The Turtles

Group founded by Richard Dennis and Bill Eckhardt, mid-1980s — among the most famous trading groups of the era (compared to Monroe Trout and Jim Simons' Renaissance in later decades); maintained high secrecy, rules made public later via Michael Covel and Curtis Faith's writings. Kaufman's presented summary is explicitly stated to be a simplified reconstruction sufficient for testing the core concepts, not a claim of complete original fidelity — some subtle original rules/variations are explicitly omitted. Underlying design imperative: "you can't miss the trade" (Kaufman Ch.5).

**System 1 (S1)**:
1. Enter long when intraday high exceeds the highest high of the previous 20 days; exit long when intraday low falls below the lowest low of the previous 10 days.
2. Enter short when intraday low falls below the lowest low of the previous 20 days; exit short when intraday high exceeds the highest high of the previous 10 days.
3. **Filter Rule**: ignore an S1 entry signal if the previous S1 entry (in either direction) was profitable — whether or not that prior signal was actually traded — UNLESS the prior S1 trade was a loss of at least a specified multiple of **L** (a 20-day ATR-based volatility measure, converted to dollars via the market's "big point value," BPV). **Gap flagged**: the exact loss-threshold multiple is embedded as a graphic in the source and not recoverable; the ATR-based L/BPV structure is explicit.

**System 2 (S2)**:
1. Enter long when intraday high exceeds the highest high of the previous 55 days (traders had discretion to shorten this slightly); exit long when intraday low falls below the lowest low of the previous 20 days.
2. Enter short when intraday low falls below the lowest low of the previous 55 days; exit short when intraday high exceeds the highest high of the previous 20 days.
3. **No filter rule** for S2 (unlike S1).

**Risk control (shared)**:
1. Stop-loss placed at a distance of **2L** from the initial entry.
2. Exit triggers on the *first* of: (a) the stop-loss; (b) an S1/S2 reversal signal; (c) a loss of 2% of portfolio value (calibrated so that 2L corresponds to 2% of the portfolio).
3. **Position sizing**: set to equalize dollar-volatility (2L-based) exposure across all traded markets.
4. **Position limits (unit caps)**, four-tier structure: a single market has its own unit cap; closely correlated markets (energy complex, precious metals, currencies, short-term rates) share a tighter group cap; less-correlated-but-related markets (linked via inflation/other macro factors) share a looser group cap; and there is an overall net-long/net-short cap across the portfolio. **Gap flagged**: exact numeric unit-cap values embedded as graphics, not recoverable; the four-tier structure itself is explicit.
5. **Compounding (position building)**: add another unit (or ½ unit) for every additional profitable move of size L from the actual entry price, up to a maximum of 5 units. Stop-loss starts at ½L on day 1 and moves to 2L thereafter (an alternate-stop variant keeps it at ½L, with the option to re-enter at the original entry price if stopped out); once a second unit is added, all stops move to 2L measured from the most recent entry, so **total trade risk stays constant** at each stage of compounding.
6. **Portfolio-level drawdown risk management**: for every 10% drawdown from peak equity, cut position size by 20%; for every 6⅔% recovery, add back 10% of the size reduction (at the time, most futures managers considered 50% drawdown the practical maximum tolerable loss). Trading costs were included in these calculations.

**Kaufman's own assessment**: Richard Dennis was reportedly one of the most successful floor traders of the late 1970s/early 1980s; it is not established whether his prior success came from this breakout method or something similar. The reference implementation (TSM Turtle) reproduces only the basic breakout + initial sizing/stop-loss, not the full rule set — sufficient to show the underlying method is profitable, with "subtle additions" potentially adding further value.

- **Worked copper example (1980-2017/18, closed trades only)**: the slower system (55/20) showed steady profits across the full ~38-year period, typical of a long-term trend-follower; the faster system (20/10) showed profits mainly in the early 1980s (the period that led Dennis to found the Turtles) and less thereafter. **Explicit caution**: this is only one market with an incomplete rule implementation — not sufficient to generalize.
- **Comparative N-Day Breakout test on the same copper data**: nearly all tested calculation periods (except the two shortest) were profitable over the full 38 years; the slower (55/20) Turtles-style result performed comparably to the broader N-day breakout sweep — Kaufman credits Dennis with the foresight to use breakout systems "ahead of the crowd," given markets trended more strongly in that earlier era.

**Secondary-source cross-check (Pardo, *Evaluation and Optimization of Trading Strategies*)**: Pardo's book treats the "Turtle Trading Strategy" (TTS) as a simplified illustrative example, not a full reconstruction — entry: "goes long when an x-day high has been penetrated and goes short when an x-day low has been broken"; exit: "exits positions on opposite signals from a shorter y-day high or low." Pardo explicitly notes "there are other variations" not detailed, and cites (secondhand, via Art Collins) that Richard Dennis himself reportedly said "the Turtle Trading Strategy doesn't work anymore," while noting variants reportedly produced "hundreds of millions of dollars" during the years the approach did work. This is a much thinner treatment than Kaufman's — Pardo uses TTS purely to illustrate methodology (systematic vs. discretionary contrast, strategy life-cycle decay), not to give a trading rule set of its own.

---

## Moving Averages and Exponential Smoothing (Kaufman Ch.7)

**Framing**: trends are time-horizon-dependent — more than one trend can coexist in the same market at the same time, and there is "no right or wrong trend"; the appropriate technique depends on what is known about *why* a market trends. This chapter adds the *time* dimension to Ch.5's event-driven (time-ignoring) methods and Ch.6's regression-based methods: moving averages and their variants try to hold onto a developing trend continuously, rather than waiting for a support/resistance event.

### Forecasting vs. Following

- **Forecasting** (predicting future price) is distinguished from **recognizing the current trend**; forecasts carry a confidence level that declines the further into the future they are projected.
- **Autoregressive functions** determine trend direction from past prices only, typically classifying only up/down/sideways with no confidence level or persistence estimate.
- **Core assumption — persistence**: the direction of prices today is most likely to be the same as the direction of prices tomorrow. This assumption "has proved to be true" for the most part but requires introducing a **lag** (a delay in identifying the trend) — explicitly framed as both "the best and worst part of moving average methods," since it is the zone of uncertainty that lets the technique ignore most market noise.
- **No universal best method**: the best historic results "often come from overfitting the data, and is a poor choice for trading" — an explicit overfitting warning specifically framed around choosing among trend methods (Kaufman Ch.7).

### Error Analysis and the Case for 1-Day-Ahead Forecasts

Using General Electric prices, a rolling 20-day least-squares regression's forecast error (projected price − actual price) grows as the forecast horizon lengthens:

| Days ahead | 1 | 2 | 3 | 5 | 10 |
|---|---|---|---|---|---|
| Stdev of errors | 1.137 | 1.336 | 1.519 | 1.860 | 2.672 |

This is described as "typical...regardless of the method," used to argue the smallest forecast interval is the best. **Explicit design conclusion: any forecasts used in the book's strategies will be 1-day-ahead** (Kaufman Ch.7).

**Defining expectations for profitability** — only ONE of the following two conditions needs to hold: (1) correct >50% of days predicting up/down direction, AND the average up move equals the average down move; OR (2) forecast accuracy is <50%, BUT the size of profitable moves exceeds the size of losing moves. **Kaufman's heuristic for robustness**: "the most robust trending method is the one that has been profitable over most markets and most calculation periods" — short calculation periods are excluded from this heuristic because they have no reliable trend.

### Momentum / Rate of Change as the Simplest Trend Indicator

**Momentum (M)** = pₜ − pₜ₋ₙ (t = today, n = days back); positive → uptrend, negative → downtrend. Some call this **rate of change (ROC)**, though Kaufman notes true ROC refers to change *over a unit of time* (normalized by n), distinguishing it from raw momentum. If n is large enough, momentum's trend read converges toward what a simple moving average would show. **Explicit heuristic**: "the simplest method can often be the most robust" — the author advises continually asking "Is it better than momentum?" (Kaufman Ch.7). See `05_momentum.md` for ROC/momentum treated as an oscillator rather than a trend filter.

### The Moving Average — Mechanics

A moving average at time t over the most recent n prices is their arithmetic mean; the number of elements averaged stays fixed while the window rolls forward. **Key mechanical property**: today's new value depends only on how the new incoming data point compares to the oldest outgoing one — if the new price exceeds the dropped price, the average rises, and vice versa (Kaufman Ch.7).

**Choosing the calculation period**: driven by predictive quality/profitability or the need to track specific time periods (e.g., a season). **General tradeoff**: slower trends (longer periods) are usually better direction indicators but carry larger risk — the stock market's benchmark 200-day MA is "much too slow" for traders' timing needs. Period-to-purpose examples: a 63-day MA (¼ of 252 trading days/year) reflects quarterly changes; a 252-day MA ignores seasonality, emphasizing annual growth/inflation. **Cycle-avoidance rule**: any periodic cycle equal in length to the MA's calculation period is cancelled out by the averaging — choose an MA length *out of phase with*, not equal to, any known cyclic/seasonal pattern. **Commercial-use example**: a jeweler buying silver weekly can tolerate delay on a downtrend but wants to buy immediately on an upturn — a 6-month trend is useless for this decision horizon, a 5-day MA matches it. General lesson: match calculation period to the actual decision horizon, not to whatever period "feels standard" (Kaufman Ch.7).

**What can you average?** Closing/settlement price is most common; alternatives: (H+L+C)/3 or (H+L)/2. Averaging other averages (e.g., a 3-day MA of a 3-day MA) produces a **double-smoothed moving average**, giving added weight to the center points; smoothing highs and lows independently creates a volatility band (used in Ch.8).

### Types of Moving Averages (Kaufman Ch.7)

- **Simple Moving Average** (also "truncated moving average"): plain arithmetic mean of the most recent n days. Main objection: an abrupt value change when an important old data point drops off, especially with few days in the calculation.
- **Average-Modified / Average-Off Method**: each new data point drops off the *previous average itself* (not the raw oldest price), which is computationally convenient (only the prior average value needs retaining) and dampens the drop-off/"end-off" impact.
- **Weighted Moving Average (WMA)**: weights need not be percentages summing to 1. **Front-loaded WMA** (most popular): more weight on recent data. **Step-weighting**: successive weights differ by a fixed increment — the most common 5-day form uses weights 5,4,3,2,1 (most-recent to oldest, normalized by their sum). TradeStation function name: `waverage`. **Percentage-relationship weighting**: uses a ratio a between successive weights (e.g., a=0.90 means each older item's weight is 90% of the next-more-recent weight) — noted as similar in effect to exponential smoothing.
- **Weighting by Group**: prices weighted in groups (e.g., every two consecutive elements sharing a weight), using an even period n with n/2 distinct weights.
- **Triangular Weighting (Triangular Filtering)**: reduces noise at *both* front and back of the window by weighting in a triangular/pyramid shape — for a 21-day window, the 11th (middle) day gets the greatest weight, days 1 and 21 the least. An odd number of days is recommended. A **Gaussian filter** is a related alternative weighting in a bell-curve shape. Often used for cycle analysis (Hilbert/Fischer transforms, Ch.11).
- **Pivot-Point Weighting**: uses reverse linear weights that start positive and continue declining into negative territory (e.g., 5, 4, 3, ... 0, −1, −2), an unusual feature since most weighted averages assume all-positive weights. The "pivot point" (weight = 0) occurs about ⅔ through the interval; for an 11-value MA, the 8th data point gets weight 0. Intent: reduce lag by front-loading prices; the divisor is smaller than a standard linear-weighted average's because negative values reduce the sum, and the negative weights on the oldest points actually **reverse** (not just diminish) their price-move impact. **Explicit caution**: for a short interval this can put the trendline out of phase with prices; works best for longer-term cyclic markets. Reference tool: `TSM Pivot Point Average`.
- **Standard Deviation Moving Average (StdAvg)**: modifies a moving-average value with a percentage of the price standard deviation. Example formula given: `SD = StdDev(close, 30); SDV = (SD − SD[1]) / SD; StdAvg = Average(close, 15) + 0.05 × SDV`.

### The Moving Median

The middle value of the sorted most-recent-N prices; ignores extremes and shows a "typical" value. Slower to compute (requires sorting each day). **Key weakness**: the median stays constant through a sideways range and a sharp turn, only moving once nearly half the window has been replaced by new values on the new side — it appears to "go sideways" even while prices move quickly. Reference tool: `TSM Median` (Kaufman Ch.7).

### Geometric Moving Average (GA)

The geometric mean applied on a rolling n-point basis; well-suited to long-term price movement and index-component calculation. Can be computed via natural log: `GA = average(ln(price), n)`. Gives more effective weight to lower values without an explicit discrete weighting scheme; most useful over long intervals with a wide price range. Example: for {10, 1000}, arithmetic mean = 505, geometric mean = 100 (large divergence); for three sequential nearby prices (56.20, 58.30, 57.15), arithmetic mean (57.2166) and geometric mean (57.1871) are nearly identical — for 5-/10-/20-day MAs of recent stock prices the difference is negligible; the geometric average's advantage shows up only over long-term historic data with wide variance (Kaufman Ch.7).

### Accumulative Average

The long-term average of *all* data — explicitly **not practical for trend following**, since the final value depends heavily on the start date; a **Reset Accumulative Average** restarts whenever a new trend begins, a significant event occurs, or at a specified interval (Kaufman Ch.7).

### Drop-Off Effect

The abrupt change in a rolling trend calculation's current value when a significant older value is dropped from the window. For an n-period MA:

**Drop-off impact = (new incoming price − oldest outgoing price) / n**

A front-weighted average reduces this effect since the transition is gradual rather than abrupt. Exponential smoothing and the average-off method both inherently minimize drop-off effect by being front-loaded (Kaufman Ch.7).

### Exponential Smoothing

Framed as "only another form of a weighted average" (more accurately, "percentage smoothing") — needs only the current price, the last smoothed value, and a smoothing constant to update. Developed during WWII for tracking aircraft/missile positions. Weights decline by the *same percentage* each prior day; because all past data retains *some* nonzero weight indefinitely, exponential smoothing is slower than a "comparable" simple moving average (Kaufman Ch.7).

**Common form**: **Eₜ = Eₜ₋₁ + sc × (pₜ − Eₜ₋₁)**, where sc = smoothing constant, 0 ≤ sc ≤ 1. Initialization: E₁ = p₁, then iterate. Even though initialized with the closing price, a smaller sc requires more data before the smoothed line stabilizes.

**The smoothing constant expressed in days (Hutson conversion)**: **sc = 2 / (n + 1)**, cited to Hutson. For n=1 through 5: sc = 1.0, 0.667, 0.50, 0.40, 0.333 — Kaufman flags this as leaving "large gaps in the test possibilities." **Explicit warning**: the Hutson conversion does NOT give a true lag-equivalent between a moving average and exponential smoothing — a 10% smoothing is actually **slower** than a 10-day MA, and a 5% smoothing slower than a 20-day MA.

**2nd/3rd-order exponential smoothing** (weighting the past 2 or 3 days — the exponential analogue of step-weighting):

| MA Days (n) | 1st-Order | 2nd-Order | 3rd-Order |
|---|---|---|---|
| 3 | 0.500 | 0.293 | 0.206 |
| 5 | 0.333 | 0.184 | 0.126 |
| 7 | 0.250 | 0.134 | 0.091 |
| 9 | 0.200 | 0.106 | 0.072 |
| 11 | 0.167 | 0.087 | 0.059 |
| 13 | 0.143 | 0.074 | 0.050 |
| 15 | 0.125 | 0.065 | 0.044 |
| 17 | 0.111 | 0.057 | 0.039 |
| 19 | 0.100 | 0.051 | 0.035 |
| 21 | 0.091 | 0.047 | 0.031 |

**Residual Impact (RI)**: exponential smoothing retains all past prices indefinitely (diminishing but nonzero weight) vs. a standard MA's hard cutoff. **Gap flagged**: the general RI-to-smoothing-constant formula is an embedded graphic, not recoverable. The standard sc=2/(n+1) approximation corresponds to a consistent residual impact of roughly 13-14% regardless of n:

| n | 2/(n+1) | RI (%) | 10% RI sc | 5% RI sc |
|---|---|---|---|---|
| 5 | 0.333 | 13.17 | 0.369 | 0.451 |
| 10 | 0.182 | 13.44 | 0.206 | 0.259 |
| 15 | 0.125 | 13.49 | 0.142 | 0.181 |
| 20 | 0.095 | 13.51 | 0.109 | 0.139 |

**Relating exponential and standard averages**: comparing a 10-day MA to "10%" exponential smoothing is not intuitive because the simple MA is equally weighted while the exponential is front-weighted. Because exponential smoothing never fully discards old data, a 10% smoothing is slower than a 10-day MA, and a 5% smoothing is slower than a 20-day MA.

| Smoothing constant | 0.10 | 0.20 | 0.30 | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 |
|---|---|---|---|---|---|---|---|---|
| Equivalent n-day MA | 20 | 10 | 6 | 4 | 3 | 2.25 | 1.75 | 1.40 |

| n-day MA | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 |
|---|---|---|---|---|---|---|---|---|
| Smoothing constant | 0.65 | 0.40 | 0.30 | 0.235 | 0.20 | 0.165 | 0.14 | 0.125 |

**Explicit methodological caution (cross-referenced to Ch.21)**: if smoothing constants are tested at *equally spaced* intervals, sensitivity clusters at the low-day end (half the tests would effectively analyze MAs of 3 days or fewer); testing equally spaced *day* counts produces a very different, more front-loaded distribution of implied smoothing constants (nearly logarithmic). **This means the choice of parameter grid materially biases which "styles" of trend a robustness/optimization sweep actually samples.**

**Double smoothing**: rather than lengthening the MA period or lowering sc, the trend values themselves can be smoothed again, slowing the trendline while weighting previous values in a possibly unexpected way. A double-smoothed 3-day MA (MA of an MA) concentrates weight on the *center* values, algebraically producing the same effective shape as triangular weighting; for longer windows, only the endpoints have reduced/declining weight while interior points share equal weight. For **exponential** double smoothing, because the most recent value already carries the full weight of sc in the first pass, double-smoothing causes the near-term value to effectively be smoothed by sc² — e.g., a nominal 0.20 constant produces, in double-smoothed form, a net effect close to sc² ≈ 0.031. **Error correction**: adding the exponentially smoothed *forecast error* series back to the single-smoothed trendline positions the trendline in the middle of the price move — Kaufman notes this "may be a good candidate for mean reversion trading."

**Double smoothing of price changes (Blau's method)**: William Blau substitutes price changes (Δp, momentum) for the price itself before double smoothing, making the input more sensitive; the first smoothing pass on this already-accelerated series effectively has no lag, so only the *second* pass contributes lag — the same net lag as one ordinary moving average despite two smoothing passes. Blau found this a successful long-term-trend proxy, using first-smoothing periods as long as 250 days and second-smoothing periods as short as 5 days. **Limitation**: the output is on a momentum/price-change scale, not price, so it cannot be plotted in the same chart window as price. **Trading rule**: buy when the double-smoothed trendline turns up, sell when it turns down (deferred to Ch.8 under "TRIX," below).

**Regularization (Mills)**: an alternative double-smoothing form ("exponential regularization," cited to Mark Mills), using a smoothing constant a, weighting factor w, and price p, nominally both a and w set to 9. **Gap flagged**: exact combining formula is embedded as a graphic, not recoverable; the nominal parameterization and its qualitative comparison ("much smoother but also shows more lag" vs. plain 9-day exponential smoothing) are preserved. Reference tool: `TSM Exponential Regularization`.

**Hull Moving Average (HMA)**: a double-smoothed method using linearly weighted averages (WMA) with modified calculation periods, designed to shorten net lag, using the original period p, √p, and p/2. **Gap flagged, with a labeled reconstruction**: the book's own inline equation graphic did not survive extraction; the standard published Hull construction is given as: HMA = WAVG( 2×WAVG(close, INT(p/2)) − WAVG(close, p), INT(SQRT(p)) ), explicitly flagged as reconstructed from the standard published form since the book's own notation did not extract, though the component names/roles in the source text are consistent with this construction. Comparison (16-week HMA vs. a traditional double smoothing of 20-week exponential smoothing followed by 5-week smoothing): "very similar," with HMA being the *slower* of the two; a double-smoothed 16-week *simple* MA is much more sensitive. Reference tool: `TSM Hull Moving Average`.

### Plotting Lags and Leads

Any trend calculation can be plotted forward (**lead**) or backward (**lag**) relative to the last price used. Conventional plots place the MA value directly above/below the last price (all averaging/smoothing is inherently lagging). Leading plots treat the MA as an n-day-ahead forecast; lagging plots (used for finding seasonal patterns) place the value in the middle of the actual price data used. **Note**: the Ichimoku Clouds technique (below) uses multiple lead plots simultaneously (Kaufman Ch.7).

---

## Trend Systems: MA and Breakout Combinations (Kaufman Ch.8)

**Framing**: turning trend calculations into a trading system requires trading rules and specific parameters defining trend speed and acceptable risk. Kaufman's explicit goal: find trends that are robust — working across many markets and varied economic conditions — while satisfying an investor's risk tolerance, calling this "a difficult balance." Trend systems are the preferred choice of CTAs and many hedge funds; CTA AUM reached a record $343 billion in 2017 (a small part of the $3.37 trillion managed by all hedge funds), cited as evidence of trend following's long-term success (Kaufman Ch.8).

### Basic Buy and Sell Signal Families

All trends lag price movement — an advantage (lets you stay in a trade) and a disadvantage. As calculation period grows, lag grows; the moving average's value is closest to the price from half the calculation period ago (e.g., a 40-day MA lags ~20 days) but is plotted under today's price. **Three families of entry/exit rule, in increasing lag order**:

1. **Price-crossing (intraday)**: Buy when prices cross above the trendline intraday; sell short when below. Produces the most (and most whipsaw-prone) signals.
2. **Price-crossing (close-based)**: Buy when prices *close* above the trendline; sell short when close below — reduces signal count.
3. **High/Low/Close-average crossing**: use (H+L)/2 or (H+L+C)/3 crossing the trendline.
4. **Trendline-direction signal** (lowest frequency, most lag): Buy when the trendline's own change is up; sell short when down. Fewer false signals (higher win rate, lower cost) but later than a price cross.

**Table 8.2 (10 years of Amazon, five calculation periods 5/10/20/40/80 days)**: trendline-direction signals had 26%-37% fewer trades and generally better Profit Factor than price-penetration signals, except at the fastest (5-day) period where the lag becomes too costly. **General conclusion**: trendline-based signals suit longer-term trading; price-penetration suits shorter-term/day trading.

### Anticipating the Trend Signal

**Consistency principle**: the system tested and the system traded must be identical. Two solutions: (1) capture prices shortly before the close, generate signals, and place orders for execution on the close (general rule: entering sooner is better); (2) calculate in advance the exact price that would trigger a signal — e.g., for an n-day MA, if the oldest price in a 40-day average was 30.25, any price above 30.25 today causes the trendline to turn up, so a stop order to buy at 30.26 can be placed before the close.

**Not all entries should be anticipated**: for Eurodollars (low noise), entering sooner was more profitable in all but one tested case, and longer trend periods were generally more profitable; for the S&P (high noise), waiting until the next close was favored, and short-term trends were unprofitable — attributed to higher market noise (Table 8.3).

### Profile of a Simple Moving Average System

Worked example: 80-day MA trendline-direction system on NASDAQ 100 futures, 1998-June 2018:

| Metric | All Trades | Long | Short |
|---|---|---|---|
| Total Net Profit | $1,584,665 | $1,868,520 | ($283,855) |
| Profit Factor | 1.47 | 2.22 | 0.85 |
| Total # Trades | 201 | 101 | 100 |
| % Profitable | 36.32% | 46.53% | 26.00% |
| Avg Trade Net Profit | $7,884 | $18,500 | ($2,839) |
| Avg Winning Trade | $67,844 | $72,226 | $59,921 |
| Avg Losing Trade | ($26,312) | ($28,261) | ($24,889) |
| Ratio Avg Win:Avg Loss | 2.58 | 2.56 | 2.41 |
| Max Consecutive Wins | 5 | 5 | 3 |
| Max Consecutive Losses | 11 | 5 | 12 |
| Avg Bars in Winning Trade | 47.3 | 54.11 | 35 |
| Avg Bars in Losing Trade | 10.09 | 11.06 | 9.38 |

**Generalized moving-average trend-following profile (Kaufman's explicit summary)**: percentage of profitable trades is low (~35%); average winning trades must be significantly larger than average losing trades, requiring a win:loss ratio > ~2.86:1 just to break even at that hit rate; winning trades are held much longer than losing trades; high frequency of losing trades produces long losing-trade sequences. This risk/return shape is called **conservation of capital** (cut losses quickly, let profits run). **Explicit warning**: adding profit-taking or stop-losses to improve these statistics reduces or eliminates the ability to capture the fat tail necessary for the strategy's long-term profitability — a direct trade-off, not a free improvement.

### Timing the Order

A change-of-trend signal is inherently a point of high uncertainty — entering exactly at the signal often places the trader at an immediate loss, especially in noisy markets. Listed options: wait until the close if triggered intraday; buy/sell on the next day's open; delay entry by 1-3 days; buy/sell on a 50% retracement of the daily range following the signal; buy/sell when price moves to within a specified risk level of a reversal/exit point. **Explicit caveat**: "a contingent order that is missed is guaranteed to be a profitable trade" (survivorship bias in evaluating skipped trades). **Empirical finding**: delaying execution from the signal close to the next open improved the entry price about 75% of the time in multi-year tests, but *reduced* overall total profits — fast breakouts that never retrace get missed, and those missed profits outweigh the 75%-of-time small price improvements.

### Bands and Channels

A band/channel around the trendline improves signal reliability without materially altering the overall trend profile — slows trading down without sacrificing the biggest profits, giving the trend time to develop.

- **Bands formed by highs and lows**: apply the n-day MA separately to highs and lows; long entries on today's high crossing the MA-of-highs, short entries on today's low crossing the MA-of-lows. For the highly trending Eurodollar, entering later via high/low crossing underperformed simple close-crossing; for the noisy S&P, waiting longer noticeably improved results, in one case turning a loss into a profit. **General conclusion**: a band can be a profitable variation but is not universally better — depends on market noise level.
- **Keltner Channels** (Chester Keltner, 1960): one of the original band calculations. **Gap flagged**: the exact formula is an embedded graphic and did not extract. Kaufman's own note: it would be best to substitute true range for the high-low range as a better volatility measure.
- **Percentage Bands**: a band formed by adding/subtracting a fixed percentage c of price from a closing-price-based trendline. Example: MA=$33, band=3% → upper $33.99, lower $32.01. A more sensitive variant uses the current price rather than the MA to compute band width, while still centering on the MA for stability. **Explicit warning**: percentage bands cannot be used with back-adjusted futures data (artificial absolute price levels); avoid a fixed-dollar band (over-sensitive at high prices, insensitive at low prices). **Gap flagged**: exact band arithmetic formulas are embedded graphics, not recoverable.
- **Volatility Bands**: scale band width using a scaling factor s and a volatility measure so signal sensitivity stays roughly constant across regimes. **Gap flagged**: exact combining formulas embedded as graphics; the "2×ATR" special case is stated in prose. Figure 8.5 (S&P, scaling factor 2 for all four): the two percentage-based bands are almost identical, smoothest, and widest; the ATR band is next-closest and widens slightly more in volatile periods; the standard-deviation band is closest to the trendline and most sensitive to volatility. **Practical note**: asymmetric entry/exit bands can be useful — entries less sensitive (wider) than exits (narrower); or entries triggered by band penetration while exits use the trendline, avoiding a direct long-to-short reversal (halves order size, improves slippage/liquidity). **Execution discipline reminder**: always use yesterday's trend calculation with today's price to generate a signal (avoid look-ahead).
- **Adaptive Price Zone (APZ)** (Lee Leibfarth, 2006): identifies mean-reversion opportunities (contrasts with trend-following bands). Built from a double-smoothed exponential trendline; volatility measured via an "adaptive range" = the 5-day EMA of the 5-day EMA of (daily high − daily low). The bands touch the highs/lows when volatility increases, read as an opportunity for a mean-reversion trade. **Gap flagged**: exact band-width formula is an embedded graphic.

#### Bollinger Bands

Most common construction: 20-day MA ± 2 standard deviations of price changes over the same 20-day period (popularized by John Bollinger). Because prices are not normally distributed, 2 standard deviations equates to only an ~87% confidence band (vs. 95.4% under a true normal distribution). **Definitional note**: "if it's not a 20-day average and 2 standard deviations, it's not a Bollinger band." Once price moves outside a band, it tends to remain outside for several consecutive days (momentum-like); band width varies with volatility and shows a "bubble" (temporary widening) that persists past the point where volatility itself has declined. Can be applied across multiple time frames simultaneously (e.g., combined daily + weekly bands).

**Modified Bollinger Bands (Dennis McNicholl correction)**: addresses the standard bands' tendency to expand quickly on a volatility spike but narrow back down too slowly. Center line D uses an exponential-smoothing-style formula with smoothing constant α = 0.15 (approximates a 20-day MA); band-width multiplier f suggested at **2.5** (vs. Bollinger's standard 2.0). **Gap flagged**: exact center-line and upper/lower-band combining formulas are embedded graphics. Result (gold futures, H1 2009): doesn't eliminate the volatility bulge, but corrects/narrows faster and envelops prices more uniformly than the original. Reference tools: `TSM Bollinger bands`, `TSM Bollinger Modified`.

**Rules for using bands (general, applies to any band type)**:
- **Reversal-strategy variant (always in market)**: buy (close shorts, go long) when price closes above the upper band; sell short (close longs, go short) when price closes below the lower band. Maximum risk per trade = the current band width.
- **Trendline-exit variant (reduces order size, adds a flat period)**: buy on close above the upper band, exit on close back below the trendline (band center); sell short on close below the lower band, cover on close above the trendline. If price fails to penetrate the opposite band the same day, the trade closes flat (not reversed); the next day, penetration of either band opens a fresh trade. Using the intraday high (longs) / low (shorts) as trigger in a genuinely trending market "should produce some extra profits." **Risk note**: using the trendline as exit limits risk to half the full band width, but narrow bands can cause a same-day entry-then-exit.

**The "Squeeze"**: wait until the band compresses to some percentage of its average width (e.g., 50%), then buy or sell the breakout through the bands — cited as historically successful as a filter, with trading in the direction of the prevailing trend improving performance further (cited to Kent Calhoun, 2016).

**Bollinger on Bollinger Bands**: Bollinger's own recommended usage is typically mean-reverting/counter-trend, which the source calls "risky, especially when prices are volatile." Bollinger's own risk-reduction recommendation: confirm a downside penetration using volume/breadth indicators — if price falls but volume isn't rising and negative breadth doesn't confirm, a buy is realistic. Bollinger treats volatility as cyclic without a regular period ("extreme seeking"): very low volatility forecasts high volatility and vice versa; a major rally with dramatically expanding bandwidth should be sold once the bandwidth begins to narrow — **this rule is stated as applying only to upward price moves.**

**Combining Bollinger with other indicators (Billy Williams' method, cited *Futures*, Oct. 2010)**: combines (1) standard 20-day/2-stdev Bollinger band; (2) a 20-day Keltner Channel; (3) a 21-day Chaikin Oscillator. **Long entry (all required)**: Bollinger bands narrow to fully inside the Keltner Channel AND Chaikin Oscillator < 0; THEN Chaikin Oscillator crosses above 0. **Short entry (mirror)**: Bollinger bands narrow to fully inside the Keltner Channel AND Chaikin Oscillator > 0; THEN Chaikin Oscillator crosses below 0.

**The compromise between reliability and smaller profits**: wider bands → fewer, more reliable signals, delayed entries, smaller average profit, greater risk per trade; narrower bands → more signals/lower reliability but faster entries. No universal answer — depends on the trader's risk preference.

### Choosing the Calculation Period

**Kaufman's explicit ranking of design decisions**: the calculation-period choice is "the most important decision in the ultimate success of the trading system" — more important than the trend-identification method itself (SMA vs. regression vs. breakout) and more important than entry rules, profit-taking, or volatility filters, which "will rarely change a losing trend into a profitable one" (Kaufman Ch.8).

- Long-term trend tracks government interest-rate policy/economic growth (favors longer periods); trends are clearer on weekly vs. daily charts; intraday charts show no clear persistent trend — yet most traders find long time frames' risk unacceptable and prefer smaller, faster trades.
- **Optimization caveat**: "the power of the computer is not always as good as human reasoning and common sense. The computer is best for validating an idea, not for discovering one."
- **Traditional calendar-based periods (pre-1980, historically successful)**: 3 days, 5 days (trading week), 20-23 days (trading month), 63 days (calendar quarter), 252 days (calendar year); implied volatility traditionally uses 20 days. The stock market's 200-day MA benchmark origin is explicitly stated as unclear.

### A Few Classic Single-Trend Systems (Kaufman Ch.8)

#### MPTDI — Major Price Trend Directional Indicator (Robert Joel Taylor, 1972)

A "step-weighted moving average" system — fully volatility-adaptive: calculation period, weighting, entry-penetration threshold, and stop-loss all change together based on discrete average-trading-range "steps" (Types A-E).

- **Entry**: classify current average trading range into one of 5 discrete steps (gold example: 50-150/150-250/250-350/350-450/450+ points → Types A-E, each with its own calc period 2-5/20/15/10/5 days and step-weighted factor progression); entry signal = penetration of the moving average by the step's assigned point threshold (e.g., Type C = 250-point penetration), triggered intraday off values calculated after the prior close.
- **Risk**: a stop-loss fixed at entry, sized to the same volatility-step's assigned value; a new signal in the opposite direction serves as both exit and new entry.
- **Strengths**: individualized per market, self-adjusting to changing volatility, favors recent data, fixed (not backing-away) risk per trade.
- **Weaknesses**: the discrete step boundaries are a "crude measure" — reasonably accurate mid-step but abruptly wrong at the extremes/transition points, where volatility can cause a jarring jump in all parameters at once. Kaufman frames MPTDI as groundwork for the later *continuous* (not discrete) adaptive methods of Ch.17.

#### Volatility System (cited to Richard Bookstaber, 1984)

An early ATR-based system: defines trend by an unusually large single-day move (a "price shock"), on the premise that the move following a shock continues in the shock's direction.

- **Entry**: Sell if close drops by more than k×ATR(n) from the previous close; Buy if close rises by more than k×ATR(n) from the previous close. k typically ≈ 2.0.
- **Strengths**: few trades but high reliability, per the source. Reference tool: `TSM Volatility System`.

#### The 10-Day Moving Average Rule (Keltner, 1960)

An early, computationally simple volatility-band system intended to capture minor rather than medium/long-term trends. Uses a 10-day MA of (H+L+C)/3, with a band formed from the 10-day MA of the high-low range (similar to a 10-day ATR). Buy when price crosses above the upper band; sell when price crosses below the lower band; always reversed (always in market). The 10-day period made the required division a simple decimal-place shift — likely a pre-calculator-era convenience. Kaufman notes shorter calc periods generally underperform on current, noisier markets, but the volatility-band concept "has held up well over time."

#### TRIX (Triple Exponential Smoothing)

First described by Jack Hutson (*Technical Analysis of Stocks & Commodities*, July 1983). A low-lag trend-direction signal built by applying exponential smoothing three times to the natural log of price.

- **Calculation**: take ln(price); apply exponential smoothing with the same smoothing constant three times in sequence; a common variant replaces the natural-log step with a percentage-change final step (speeds up the process).
- **Parameters**: smoothing constant should represent a short period, "between 3 and 20 days but recommended as 6 days," converted via sc = 2/(n+1).
- **Entry rules (original)**: buy when the triple-smoothed trendline rises for 2 consecutive days; sell when it falls for 2 consecutive days.
- **Signal-line variant**: a 3-day MA of TRIX values forms a signal line; buy when TRIX crosses above the signal line, sell when it crosses below (the same technique later reused for MACD).
- **Example**: 9-day TRIX on euro currency futures, 2013 — the final differencing step removes much of the expected lag, keeping price peaks and TRIX peaks nearly aligned while remaining reasonably smooth. Related methods cited: Blau's True Strength Index and True Directional Movement.
- **Note on classification**: Kaufman presents TRIX here as a trend-direction system (buy/sell on 2-consecutive-day trendline direction), distinct from its more common use as a momentum oscillator — see `05_momentum.md` for that alternate framing.

#### The ROC Method as a Trend System ("Woodshedder's long-term indicator")

Cited to the Woodshedder blog, reviewed by MarketSci blog (Oct. 4, 2011). Uses **5-day ROC** and **252-day ROC** (rate of change, defined the same as momentum).

- **Entry**: buy when the 5-day ROC is below the 252-day ROC for two consecutive days; exit the long when the 5-day ROC is above the 252-day ROC for two consecutive days.
- **Cash management rule**: when flat, earn one-half of the cash 3-month T-bill rate.
- **Backtest**: S&P futures, 1998-2017 (20 years) — 52 trades, 53% profitable, profits on both long and short positions. Reference tool: `TSM ROC`.
- **Note**: this is ROC deployed explicitly as a trend/regime filter (comparing a fast ROC to a slow ROC), distinct from ROC used as a momentum oscillator — see `05_momentum.md` for the oscillator framing and for TRIX's momentum-indicator lineage.

#### A Simple Momentum System

The most basic trend system: buy when n-day momentum is positive, sell when negative. For large n, results converge closely to a simple MA system with the same entry/exit rules. **Explicit reminder**: momentum can be effective even though it is very simple — reinforces the "is it better than momentum?" heuristic (Kaufman Ch.8, extending Ch.7).

#### Commodex — Multi-Factor Composite Trend System (Kaufman, Ch.22)

First presented in 1959 and still commercially operated (Commodex.com), now run by second-generation operator Philip Gotthelf — one of the longest continuously-run named trading systems. Unlike the single-trend systems above, Commodex deliberately blends several factor families — moving averages, price momentum, open interest, and volume — into one weighted trend index that is ranked to produce a relative-strength value, rather than relying on trend direction alone.

- **Three MA-derived scoring components** (10-day and 20-day MAs), combined with an explicit weighting priority: (1) the long-term (20-day) MA signal, most important; (2) the short-term (10-day) MA signal, second; (3) the fast/slow MA crossover (the dual-MA relative position), least important.
- **Strongest bullish configuration**: current price above both MAs, with the faster MA below the slower MA. **Strongest bearish configuration**: the mirror opposite. **Neutral**: when the most important element (the long-term MA) conflicts with the other two factors.
- **Open-interest rule (futures)**: "growth momentum" = the difference between open interest's rate-of-increase and its own 20-day moving average. IF open-interest growth momentum is rising together with rising prices THEN bullish — a "classic concept of charting," per Kaufman. IF open interest rises with falling prices THEN bearish. **Distinctive non-standard rule, explicitly flagged by Kaufman as departing from standard charting convention**: falling open interest together with falling prices is ALSO treated as bullish by Commodex. Volume momentum is scored identically to open-interest momentum for trend confirmation (rising volume momentum + rising prices = bullish support; other combinations = bearish).
- **Signal output**: the combined index is ranked from strong buy to strong sell and also functions as an overbought/oversold indicator, specifying profit-taking levels and permitting position reversal in extreme situations. Stops are placed using the 20-day MA with predetermined band penetrations.
- **Money-management overlay (tiered profit-taking)**: a 50% profit triggers a protective stop on part of the position; a 100% profit requires liquidating half the position.
- **Kaufman's assessment**: credits Commodex for "quantifying and balancing" elements normally treated as purely interpretive charting technique, and notes that its money-management rules "round out" the system.

### The Golden Cross / Death Cross

**Definition**: Golden Cross = 50-day MA crosses above the 200-day MA (bullish); Death Cross = 50-day MA crosses below the 200-day MA (bearish). Kaufman notes it is unclear how these specific periods began, but doubling periods (50/100/200) is a simple way to keep percentage changes constant and get a good result distribution over time.

- **Track record cited**: "very good results for the past 60 years," including avoiding the 2008 decline.
- **Variant comparison**: combined Golden+Death Cross (long/short) vs. Golden-Cross-only (long-only) — the combined version's advantage is concentrated mainly in the 2000 NASDAQ collapse and subsequent bear market; largest drawdown for the combined version occurred in 2014, not during the 2008 financial crisis; the long-only version would also earn interest income while flat. Reference tool: `TSM Golden Cross`.

### Ichimoku Cloud

Developed by Goichi Hosada, published 1969 (developed in the 1930s). A visual, cloud-based projected-trend system combining five moving-average-derived lines:

- **T1 Tenkan-sen (Conversion Line)** = (9-day MA of highs + 9-day MA of lows) / 2
- **T2 Kijun-sen (Base Line)** = (26-day MA of highs + 26-day MA of lows) / 2
- **T3 Senkou A** = (T1 + T2) / 2, plotted 26 periods forward (leading)
- **T4 Senkou B** = (52-day MA of highs + 52-day MA of lows) / 2, plotted 26 periods forward (leading)
- **T5 Chikou (Lagging Span)** = closing price plotted 26 days in the past (lagging)
- Senkou A and B together form the outline of "the cloud"; colored green when rising, red when falling.

**Entry rules — macrotrend**: buy when the cloud turns from red to green, or when price moves above a green cloud (bullish); sell short when the cloud turns from green to red, or when price moves below a red cloud (bearish). **Entry rules — shorter-term momentum/reentry** (only in the direction of the cloud): buy when T1 moves above T2; sell short when T1 moves below T2. **Filter**: the cloud serves as a long-term trend filter — trades taken only in the cloud's current direction (Kaufman Ch.8).

### Techniques Using Two Trendlines

**Rationale**: a dominant long-term trend (often policy-driven) can persist for years, but few traders will hold a single trade through the full move's drawdowns; a 2-trend combination lets traders take repeated smaller, lower-risk trades in the direction of the dominant trend. The slower trendline identifies the primary trend direction; the faster trendline (which need not itself be a trend indicator — could be pattern recognition or RSI) is used for entry/exit timing (Kaufman Ch.8).

**Three rule sets**:
1. **Simple crossover (always in market)**: Buy when the faster MA crosses above the slower MA; sell short when it crosses below.
2. **Price-vs-both-MAs (creates a flat/neutral zone)**: Buy when price crosses above both MAs; exit longs when price crosses below either MA. Sell short when price crosses below both MAs; cover when price crosses above either MA.
3. **Both-trendlines-agree (creates a flat/neutral zone)**: Buy when the faster trendline turns up AND the slower trendline is up; sell short when the faster turns down AND the slower is down; exit when the two trendlines conflict.

Exiting to flat (rules 2 and 3) rather than always reversing (rule 1) adds liquidity and allows re-entering in the same direction on the next signal.

**Worked example (euro futures, 1990-2018)**: a 100-day/30-day MA crossover (Rule 1, selected with the benefit of hindsight) outperformed a single 120-day MA on total profit, profit factor (2.0 vs. 1.62), and trade count — total PL $3,441,223 (crossover) vs. $2,658,518 (single MA) — cited as demonstrating that "a trend crossover system is a viable choice." **Refinement**: if too many losses come from short-held trades, a small band placed around each trendline (requiring clear penetration before flipping) can filter out marginal whipsaw crossovers.

#### Modified 3-Crossover Model (3-trend confirmation filter)

Adds a third, fast confirming trendline to a 2-trend crossover to avoid entering a trade at a moment when price is actually moving opposite to the new position. **Filter rule**: do not enter a trade unless the confirming (fast) moving average is moving in the same direction as the position about to be entered. Adding a 3-day timing trend to the Eurodollar 80-20 crossover produced a small improvement in long profits, a decline in short profits, and slightly better overall returns — more beneficial trading from the long side. Reference tool: `TSM Modified 3MA Cross`.

#### 4-9-18 Crossover Model

Popular during the late 1970s — a 3-trend crossover using periods slightly faster than the 5/10/20-day periods popular at the time (an early "ahead of the crowd" design, each period roughly double the faster one). Kaufman's own test on a sample of futures markets produced only marginal profits ("better than losses" but "none of the results would have convinced you to trade this") given the high level of price noise relative to three fast trends; likely would have been profitable in the earlier, lower-noise Donchian-era markets.

#### "Ahead of the Crowd" 8-18 Day Crossover

Deliberately uses calculation periods slightly faster than the most popular/crowded periods (e.g., 8 and 18 days vs. the popular 10 and 20) to get a small execution edge from following order flow ahead of the crowd — cited as a real system used during the 1980s-1990s. **Gap flagged**: exact TrendDifference/DifferenceAverage construction formulas are embedded graphics; the qualitative crossover-of-a-difference-vs-its-own-average structure is preserved. **Important warning**: Kaufman notes these specific calculation periods "may not be profitable in today's markets" — the value is the general principle, not the specific 8/18 parameters.

### Donchian's 5- and 20-Day Moving Average System

Richard Donchian, cited *Commodities Magazine*, Dec. 1974 — one of the longest continuously recorded trading histories (from Jan. 1, 1961). An early self-adjusting/volatility-penetration trend system, roughly equivalent to a 1-week/4-week MA combination.

- **Indicators**: 5-day MA (exit trigger, further modified by prior penetration and volatility) and 20-day MA (primary trend), plus a volatility-penetration criterion (originally the largest prior 1-day penetration of the 20-day MA; modernized in Kaufman's reference implementation using ATR over the 20-day period).
- **Modernized reference rules** (`TSM Donchian Moving Average System`): if not long and price condition + volatility-penetration condition met → buy; if not short and mirrored conditions met → sell short; if long and price falls back through the 5-day MA condition → exit long; if short and price rises back through the 5-day MA condition → cover short. **Gap flagged**: exact inequality thresholds are embedded graphics; the qualitative rule structure is preserved.
- **Position sizing**: volatility-adjusted using ATR over the 20-day period and each market's Big Point Value — explicitly justified because price levels/volatility have shifted dramatically since 1960.
- **Backtest**: applied to corn futures 1960-2018 with $8/contract/side costs — consistently profitable for 60 years, though the rate of return has slowed in recent decades (no parameters tuned in this example run).

### Donchian's 20- and 40-Day Breakout

Noted explicitly as "the basis for the Turtles' trading method." A slower, simpler version of the 5-&-20 system using pure price breakouts (no volatility bands). **Entry**: buy when today's high > highest high of the past 40 days; sell short when today's low < lowest low of the past 40 days. **Exit**: exit longs when today's low < lowest low of the past 20 days; exit shorts when today's high > highest high of the past 20 days (Kaufman Ch.8).

### Six-System Comparison Study (Kaufman Ch.8)

Six systems compared head-to-head using only basic buy/sell rules (no stops, no profit-taking, always in the market, entries/exits at the current close) to isolate each method's natural risk/return profile:

1. **M** — N-day momentum: Buy when M(t,n) > 0; Sell when M(t,n) < 0.
2. **MA** — simple moving average: Buy when MA trendline direction turns up; Sell when it turns down.
3. **EXP** — exponential smoothing: Buy/Sell analogous to MA, using exponential-smoothing trendline direction.
4. **BO** — N-day breakout: Buy when close > highest(high, t−1, n); Sell when close < lowest(low, t−1, n).
5. **SWG** — swing breakout: Buy when current swing high > previous swing high; Sell when current swing low < previous swing low.
6. **LRS** — linear regression slope: Buy when Slope(close, t, n) > 0; Sell when Slope(close, t, n) < 0.

**Test setup**: markets = IBM, Ford, Bank of America (equities), Eurodollar interest rates, emini S&P, euro currency, crude oil (futures); data 1991-2018 (futures) / 2000-2018 (stocks); $25,000 (futures) / $10,000 (stocks) notional per position; costs $8/trade (stocks) or $8/side/contract (futures); all entries/exits at the current close (justified for futures since near-24-hour trading makes "next open" execution impractical to compute and place in time).

**Results for futures**: Eurodollars show by far the highest profit and profit/max-drawdown ratio (strongest trend); the S&P shows the lowest ratio (highest noise). The euro shows balanced long/short gains; the S&P strongly favors longs; crude oil does better long but is profitable on shorts too. **Exponential smoothing consistently underperforms the simple moving average** (a repeat of the Ch.7 lag-related finding). **Momentum results are nearly identical to the moving average** (as Ch.7 predicted for large n). The swing system's optimal filter size varies by market. **Overall best three**: moving average, breakout, and linear regression slope. MA has by far the most trades and the lowest win rate but the highest PL/drawdown ratio for Eurodollars specifically; LRS has "the best overall profile" and performs well across all sampled markets generally. **Author's conclusion: "You can't really go wrong, whichever method you choose"** — results track closely across methods except around discrete regime shifts. **Stated takeaway: selecting trending markets matters more than picking the "best" system.**

**Results for stocks** (1998-July 2018, $10,000 account): short sales are broadly unprofitable except for GE (in a multi-year decline). Exponential smoothing again does poorly (exception: AAPL); the swing method is erratic; MA, BO, and LRS all perform well, with the single best method varying by stock.

**Observations (Kaufman's explicit bullet list)**:
- Long-term trend following can be profitable; all basic trending strategies are profitable if the market trends.
- Exponential smoothing has the poorest performance (repeat finding).
- Momentum ≈ moving average, but MA is the better choice of the two.
- Any of the top-tier systems (MA/BO/LRS/SWG) could be the best performer for a given market — no fixed ranking.
- A larger percentage of profitable trades is associated with fewer trades and higher risk (a recurring trade-off theme).
- Short sales in equities are not generally profitable.
- **Explicit methodological rule**: "When adding other features to a system, it needs to be proved that those features improve the results, because the simple approach seems to be very good."

**Calculation-period sweep results**: net profits generally improve as calculation period increases for interest rates (ED) and the S&P; commodities are expected to have shorter useful trend periods due to seasonality. Amazon and Boeing favor longer trends; Ford is the opposite, favoring shorter/mid trends across all three tested methods — a "problem" for a trend-follower seeking robustness because Ford lacks a persistent long-term trend. Averaging net profit across systems and markets, LRS was generally the best system, but was the weakest specifically for Ford.

**Making a decision (Kaufman's explicit synthesis)**: no universal "right" system — breakouts may suit intraday trading, MAs long-term trends, regression arbitrage/ranking; each system has "a preferred application." Risk-profile trade-off: MA has many small losses and fewer larger profits (typically <35% win rate); the breakout system has higher per-trade risk (risk = the full high-low range of the calc period) but a higher win rate (50-70%, since it tolerates price movement without reversing); LRS falls in between on both risk and win rate.

### Selecting the Trend Speed to Fit the Problem

**Institutional/commercial use case**: a mutual fund receiving periodic new investment inflows, or a cattle feedlot pricing new inventory once a month, wants a trend calculation period producing roughly one or two signals per month, so as to beat that month's average price. **Trader's goal is different**: find the parameter combination producing the best overall performance profile over the trader's own investment horizon. **Seasonality caveat**: a dominant seasonal factor (e.g., travel/leisure stocks) can be masked in any given year by a strong overall market trend, but the seasonal pattern persists underneath — a 12-month MA on a seasonal market eliminates the seasonal signal entirely; capturing the seasonal move requires a trend no longer than one calendar quarter (64 days), possibly half that (Kaufman Ch.8).

### Moving Average Sequences: Signal Progression

**Core idea**: comparing trend direction across a *range* of calculation periods (e.g., 1 through 18+ days) around the one actually being traded reveals whether a new signal is reliable or spurious. A moving average is "simply a consensus of direction... most fallible when prices are changing direction or going sideways."

- **Orderly trend change**: calculation periods 1-19 flip to uptrend together while period 20+ remains in downtrend — a smooth, left-to-right progression, described as trustworthy.
- **Erratic short-period trend change**: very short calc periods (2-9 days) flip up/down/up erratically because changing a single day of data can flip a short MA's direction easily; this instability diminishes at longer intervals. **Rule of thumb: an erratic short-end sequence should not be trusted as a real trend change** — only a genuinely smooth, progressive sequence change is reliable.
- **Alternative consistency check**: count the number of up-trending vs. down-trending calculation periods from the shortest up to the target period; whichever direction has the larger count is taken as the current trend (Kaufman Ch.8).

### Early Exits from a Trend

**Context**: U.S. interest rates declined for most of 1981-2015 (35 years). A very slow trend (e.g., 200-day MA, ~100-day lag) tracking bond futures would reflect prices from the midpoint of its window; if yields dropped 2% over a year, the trendline could lag current yields by roughly 1%, and a policy reversal could produce a large unrealized-gain giveback before the trendline itself signals the reversal.

**Rationale for a discretionary/techno-fundamental override**: if the fundamental basis for a long-term trend (sustained economic policy) visibly changes, the trend may be effectively over even before the trendline reverses — exiting on the policy-change signal rather than waiting for the trendline is a safer way to lock in profit. **Explicit warning ("Caveat emptor")**: this only works when a reliable government policy is genuinely driving the trend, and policy shifts are often clear only in hindsight — in 2010 it "seemed" Fed policy would change, yet 2011 instead posted a strong upward bond trend with record-low yields. **Guidance: wait for an actual statement of policy** before acting on this override. This hybrid discretionary/systematic approach is named **techno-fundamental** trading (Kaufman Ch.8).

### Projecting Moving Average Crossovers

For a single N-day MA, tomorrow's direction can be projected today: it will rise if today's close exceeds the price N days back (about to be dropped), and fall otherwise. For **two moving averages** crossing each other, a **crossover price (CP2)** — the future price level at which the two MAs would cross — can be calculated and updated daily, converging toward the eventual actual crossover as it nears (cited to Alexander Solodukhin, Mizuho Alternative Investments). **Gap flagged**: the exact CP2 formula is an embedded graphic, not recoverable. Donald Lambert used the *change* in the projected crossover to build the **Market Direction Indicator (MDI)** — buy when MDI crosses the zero line moving higher, sell when it crosses moving lower. **Gap flagged**: exact MDI formula is likewise an embedded graphic (Kaufman Ch.8).

### Early Identification of a Trend Change (Ehlers)

John Ehlers uses a "quotient transformation" to get an early trend indication and estimate trend duration: (1) rescale any bounded oscillator to [−1, +1]; (2) apply Ehlers' "roofing filter" to remove spectral dilation; (3) apply an "automatic gain control" (AGC) step to normalize the output without disturbing its pattern. Result: the **Early Onset Trend** indicator. Kaufman dryly notes "Only Ehlers can do this," signaling the technique's idiosyncratic/proprietary complexity. Cross-reference: the ADX (Ch.23) is another indicator attempting to recognize trend presence. **Gap flagged**: the underlying transform/filter mathematical definitions are not given in extractable text — only the high-level procedure survived (Kaufman Ch.8).

---

## Adaptive Trend Techniques (Kaufman Ch.17)

**Framing**: an adaptive technique changes with market conditions without manual intervention — true adaptivity means the calculation itself (e.g., the calculation period) changes automatically, unlike a simple % stop-loss or ATR-based stop. **Underlying premise**: a longer/slower trend calculation is better in sideways, low-volatility, or high-relative-noise conditions, while a faster calculation is better in trending/low-noise conditions — but identifying "sideways" is genuinely difficult (worked illustration: a price unchanged over 5 days that actually rose sharply for 3 days then reversed sharply is not truly "sideways" in character even though its net change is zero). **Kaufman's explicit caveat, stated up front**: adaptive techniques can improve on standard trend calculations but cannot solve all problems (Kaufman Ch.17).

### KAMA — Kaufman's Adaptive Moving Average

See also `01_market_structure.md` for the Efficiency Ratio (ER) background — KAMA is its direct downstream application. Began taking form in 1972 (Kaufman, *Smarter Trading*, 1995).

- **Core premise**: a noisy market requires a slower trend than a low-noise market; noise is NOT volatility (worked illustration: a 100-point weekly Dow range built from steady +20/day moves has far less noise than the same net range built from +100/-100/+100 alternating swings — "noise" is about the *pattern* of the move, not its magnitude). Metaphor: a very noisy move is like "a drunken sailor's walk, staggering from side to side (never backward) yet still moving forward."
- KAMA is technically an exponentially smoothed value, not a "moving average" despite the name, because the smoothing constant itself changes every period based on the Efficiency Ratio.
- **Formula**: KAMAt = KAMAt-1 + SC × (Ct − KAMAt-1), where SC (smoothing constant) is recalculated each period from the Efficiency Ratio: SC = [ER × (fastest SC − slowest SC) + slowest SC]², where fastest/slowest SC are the exponential-smoothing equivalents of the fastest and slowest allowed calculation periods (nominally 2 and 30, or 3 and 30 days). **Gap flagged, with a labeled reconstruction**: the book's own inline equation graphics for the SC-from-ER combining step and the fastest/slowest SC sub-formulas did not survive PDF extraction; the equation above is reconstructed from the standard published KAMA formula (Kaufman, *Smarter Trading*, 1995) and explicitly labeled as such, consistent with the chapter's own prose description and worked TradeStation code.
- Squaring the smoothing constant components means the slow end becomes an extremely unresponsive ~900-period-equivalent trend (the exact squared expression is an embedded-graphic gap, but the ~900-period magnitude is stated explicitly in the source); the fast end can reach a 4-period equivalent during a sustained directional move.
- **ER (Efficiency Ratio / "fractal efficiency")**: = 1 when price moves in the same direction for the full n periods; = 0 when price is unchanged over n periods; approaches 0 as swings widen relative to net change. Smaller ER → smaller SC → slower trend.
- **Verbatim TradeStation code from the source** (ER based on 10 periods; note a likely OCR artifact "0.O645" which should read "0.0645"):
  ```
  KAMA = KAMA[1] + ((absvalue(C-C[10])/
         summation(absvalue(C-C[1]),10)*0.6022) +
  0.0645)*2*(C - KAMA[1])
  ```
- **Alternate time periods for ER**: n only affects the ER calculation and is meant to be kept small (users may begin testing at n=8-10 days) so trend speed shifts quickly. A longer n centers the adaptive range closer to that period (still speeds up/slows down, but less extremely). Worked example: a 60-day KAMA vs. 60-day MA on S&P futures through April 2018 — KAMA tracks closer to price during the bull market and turns down faster at the early-February selloff, then stays in a downtrend as its smoothing constant drops and remains low.
- **Extra rules needed for trading (whipsaw fix)**: because KAMA still uses exponential smoothing, the trendline always technically changes direction the instant price crosses it, even when the smoothing constant is near zero and the line is meant to be moving "sideways." Two filter choices: (1) a factor f (suggested small, e.g. f=0.01) times the 20-day standard deviation of KAMA's own period-to-period changes, added/subtracted as a band that must be penetrated before a direction change counts; (2) track the most recent KAMA low (after an up-turn) or high (after a down-turn); require KAMA to move away from that extreme by a fixed amount F before signaling. **Kaufman's finding: option 2 (fixed-amount move filter) is the better choice**, and is what the chapter's own results use.
- **Trading rules**: buy when the trendline turns up and penetrates the small (fixed-F) threshold; sell when it turns down through the lower threshold. Faster trading: calculation period ~8-10 days. Longer-term trends: 35-60 days. Leave the upper bound fixed at 30 days; to make the trendline less sensitive, raise the *lower* bound above 2 (e.g., to 3 or 4). Always use the fixed-threshold entry filter to avoid unnecessary whipsaws. Cited result: an 8-period KAMA with a fixed filter of 0.017 on S&P futures, June 2010-April 2018 (chart-only reference, no numeric summary extracted).

### Chande's Variable Index Dynamic Average (VIDYA)

Tushar Chande, *Technical Analysis of Stocks & Commodities*, March 1992. Uses exponential smoothing with a fixed base smoothing constant of 0.20 (a 9-day equivalent), scaled up or down by the ratio of short-term to long-term standard deviation of closing prices (9-day vs. 30-day suggested): VIDYAt = VIDYAt-1 + SC × (Ct − VIDYAt-1), where SC = s × k, s = 0.20 (fixed base), k = relative volatility = stdev(C, n)/stdev(C, m), n=9, m=30 nominal.

- Higher relative volatility → larger smoothing constant → slower trend; lower relative volatility → faster trend.
- Chande recommends applying the standard deviation to price *changes* (returns) rather than raw prices, since raw prices introduce trend into what should be a pure volatility measure.
- **Weakness**: traded far more often than KAMA/MAMA in Kaufman's comparative test (594 avg trades vs. KAMA's 134), diluting per-trade edge once costs are applied.
- Available as `TSM VIDYA` (indicator and strategy, price-vs-price-change toggle).

### Correlation Coefficient (r²) as Smoothing Constant

Chande's second suggestion: use the correlation coefficient r² between closing prices and a simple sequence (1,2,3,...) from a linear regression as the smoothing constant directly — r² close to 1 when the trend fit is strong, close to 0 when there is no apparent direction. Also underperformed KAMA/MAMA in the comparative test. Available as `TSM Adaptive R2`.

### Ehlers' Adaptive Moving Averages: MAMA, FAMA, FRAMA

John Ehlers bases much of his adaptive work on the phase rate of change of price cycles (cross-reference Ch.11, Hilbert Transform); calculations not fully repeated in the source chapter, referenced to MesaSoftware.com and Ehlers' *Rocket Science for Traders*.

- **MAMA** ("fondly called the Mother of Adaptive Moving Averages"): phase rate of change = 360° per cycle, so a 36-bar cycle has a phase rate of 10°/bar (fewer bars per cycle → faster phase rate). A Hilbert-Transform-like solution finds the phase rate of change, used to set α (the smoothing constant) in classic exponential smoothing form. Ehlers restricts α to between 0.05 and 0.50 (equivalent to a 2-day to 19-day moving average).
- **FAMA**: applies the MAMA technique to the MAMA line itself (double smoothing), using a smoothing constant that is ½ of the MAMA smoothing constant at each point. Result: a smoother, less volatile signal line, analogous to the MACD signal line or %D in stochastics. The MAMA/FAMA crossover is used as the trend signal.
- **FRAMA**: based on fractal dimension. Ehlers' rationale: prices are "fractal" because they show the same "roughness" at every time frame (most traders cannot distinguish a 5-minute chart from a weekly chart once the time scale is removed). Classic coastline-measurement analogy: measuring an island's coastline with a shorter "ruler" reveals more jagged detail and yields a longer total measured length; an infinitely small ruler yields an infinite coastline length. Fractal dimension describes the shape/sparseness of a series at all levels of detail, calculated by covering the pattern with N objects (boxes) of various sizes s, where the relationship between the number of objects at two different sizes follows a power-law relationship. **Gap flagged**: the source's own inline power-law equation is an embedded-graphic gap; a worked toy example (a 10-foot line: 1-foot boxes fit N1=10, 0.1-foot boxes fit N2=100) is given, but the exact combining formula and final numeric fractal-dimension result are not recoverable. Ehlers' FRAMA adds upper/lower bands, a trailing stop, and profit-taking rules; available (modified) as `TSM FRAMA`.

**Comparison of adaptive methods** (Figure 17.5, daily S&P futures, Aug 2015-Mar 2016): FAMA is the slowest with the fewest false signals; MAMA (roughly 2x FAMA's speed) is the fastest; KAMA and Adaptive R² have similar shape and often cluster together.

**Table 17.1 (comparative returns, KAMA/VIDYA/Adaptive R²/MAMA on 15 futures markets, Jan 2000-Apr 2018, recommended parameters, no costs, longs-only on equity indices)**: KAMA (10-day ER, 3-to-30 range) averaged Profit Factor 1.41, 134 trades, 37.1% profitable — noticeably fewer trades than VIDYA (9/30-day), which averaged Profit Factor 1.08 and 594 trades. **General finding**: KAMA and MAMA trade far less often than VIDYA and Adaptive R² (increasingly important once commissions/slippage are applied); win-rate is highest with fewer trades and lowest with the most trades. Kaufman notes slowing all four systems down (longer calculation periods) might improve results, since slower trends generally track underlying economic moves better.

### McGinley Dynamics

John McGinley's "New McGinley Dynamic": MDt = MDt-1 + (p − MDt-1) / (k × n × (p/MDt-1)^4), where k = 0.60 (constant, 60% of a selected MA period n), n = the moving-average period, p = closing price. **Gap flagged, with a labeled reconstruction**: the exact exponent/denominator combining structure is the standard published McGinley Dynamic formula reconstructed here; the book's own inline equation graphic did not survive extraction, so this is labeled as reconstructed-from-the-standard-published-form rather than verbatim.

### Making Momentum Calculations Adaptive

To use any bounded momentum/oscillator value (e.g., RSI) as a smoothing constant, it must first be rescaled to the 0-1 range expected of an SC, where 0 = less trend and 1 = more trend:

| Momentum range | Transformation |
|---|---|
| 0 to 1 | SC = M |
| −1 to +1 | SC = \|M\| |
| 0 to 100 | SC = M/100 |
| −100 to +100 | SC = \|M/100\| |

where M = the current momentum/indicator value. Taking the absolute value for the ±ranges reflects negative (strong-down-trend) readings into the same "more trend → faster" pattern as strong positive readings.

**Worked comparison**: adaptive RSI vs. KAMA vs. 10-day MA on Eurodollar futures, Feb-Jul 2011 — during sideways periods, the adaptive RSI is the most sensitive, the plain MA is intermediate, KAMA is the least sensitive. Suggested fix for over-sensitivity: square the smoothing constant (e.g., 0.75 → 0.56) so any value below 1.0 is pulled toward a slower trend. Available as `TSM Adaptive RSI`.

**Adaptive stochastic** — verbatim pseudocode varying the stochastic look-back (`stochper`) using the same ER-based fast/slow-end mechanism as KAMA:
```
efratio = effratiofreq(period)/100;
stochper = intportion(slowend - efratio*(slowend - fastend));
raw = (close - lowest(low,stochper))*100 /
        (highest(high,stochper) - lowest(low,stochper));
astoch = average(raw,3);
```
Available as `TSM Adaptive Stochastic`.

### The Parabolic Time/Price System (Wilder's Parabolic SAR)

The first well-known adaptive technique (J. Welles Wilder Jr., *New Concepts in Technical Trading Systems*, 1978) — reduces trend lag by accelerating the smoothing constant (the Acceleration Factor, AF) as a trade becomes more profitable. Philosophy: "time is an enemy" — once entered, a position must continue to be profitable or it will be liquidated. Always in the market; every exit is also a reversal (Stop and Reverse, SAR).

- **SAR calculation**: an exponential-smoothing-style formula using the high price while long (or low price while short), with AF as the smoothing constant. AF starts at 0.02 at the beginning of each trade and increases by 0.02 after any day making a new extreme (new high while long / new low while short), capped at a maximum of 0.20 (a 9-day-MA equivalent; AF=0.02 initially is roughly a 99-day-MA equivalent).
- **SAR initial point (SIP)**: the lowest point of the prior move (for a new long) or the highest point of the prior move (for a new short).
- **Noise-protection rule**: the SAR may never be closer to price than the most recent 2-day high/low range — for longs, SAR may never exceed the low of today or the prior day (reset to that low if the formula would place it higher); for shorts, SAR may never be below the high of today or the prior day.
- A reversal occurs when a new intraday extreme (low while long, high while short) penetrates the SAR.
- **Kaufman's assessment**: a strong point is that the initial SAR is a market-extreme price (not a statistically derived point) and the 2-day floor/ceiling prevents noise-driven reversals during a strong move; a weak point is that AF always restarts at 0.02 regardless of how fast the market is already moving — a market moving quickly at entry might be better served starting with a faster AF. The method also requires fairly consistent price swings to be profitable. Cross-referenced: combined with Directional Movement (Ch.23) to form the Directional Parabolic System (Ch.9). TradeStation function `TSMParabolic` exposes starting AF, increment, and max AF as configurable parameters; optimizing these has "been reported to produce good results."

**Alternative Acceleration Factor — Knapp's ER-based Parabolic variant**: Volker Knapp (*Active Trader*, Sept. 2010) proposes replacing Wilder's fixed AF progression with a 10-day ATR/10-day ER-based stop adjustment. **Gap flagged**: the source's own inline threshold values are embedded-graphic gaps, but the IF/THEN logical structure is preserved: (1) set the initial stop at an ATR-based distance from entry; (2) IF ER is at one threshold level, THEN leave the stop unchanged; (3) IF ER is at a second (presumably higher) threshold, THEN reduce the stop's distance by an ATR-based amount; (4) IF ER is at a further threshold, THEN reduce the stop distance by a different (larger) ATR-based amount; (5) the trailing stop only ever advances (higher for longs, lower for shorts) — never retreats; (6) the stop applies to trading on the next day. Explicitly noted: rules are NOT symmetric between longs and shorts.

### Mart's Master Trading Formula

Donald Mart, *The Master Trading Formula* (1981). Another exponential-smoothing-based variable-speed method, but the smoothing constant and a surrounding band are both recalculated daily from market volatility, not from ER.

- Combines the 15-day ATR with the 15-day net change; each is ranked 1-21 (a defined maximum value divided into 20 equal zones, 21st zone = "anything higher"), and the two rankings are averaged into a Correlated Volatility Factor (CVF).
- CVF itself is then re-ranked into 21 zones and applied *linearly* to a smoothing-constant range of 0.084 to 0.330 (≈23-day to 5-day exponential equivalents).
- A trendline is formed daily from HLCt (average of today's high/low/close) using the resulting smoothing constant.
- A band is placed around the trendline with an *inverse* relationship to CVF: widest in low volatility (slow trend), narrowest in high volatility (fast trend) — the system is always in the market, going long on upper-band penetration and short on lower-band penetration.
- **Kaufman's critique (explicit, three points)**: (1) Mart's trend speed range (5-23 days) is much faster than KAMA's (≈2-900 days); (2) the band narrows precisely as the trend slows, an apparent attempt to allow earlier entry even while the trendline itself lags — best suited to short-term/intraday trading; (3) the linear 20-zone division ignores that sensitivity to calculation-period changes decreases as the period lengthens — Kaufman suggests a nonlinear (widening) zone structure would be more appropriate as the trend slows.

### Other Adaptive Momentum Calculations

- **Trend-Adjusted Oscillator (TAO)** (E. Marshall Wall, *Futures*, July 1996): corrects the tendency of oscillators to cluster in the lower half of their range during downtrends and the upper half during uptrends by shifting the oscillator's value by the amount its own moving average deviates from the theoretical midpoint. Worked example: a 10-day oscillator with a 5-day MA reading 40 (10 below the 50 midpoint) has its current value raised by +10. **Trade-off**: corrects sustained overbought/oversold bias at the cost of losing many smaller overbought/oversold signals.
- **Dynamic Momentum Index (DMI, Chande/Kroll)** — not Wilder's Directional Movement Indicator: a variable-length RSI whose calculation period increases as volatility declines and decreases as volatility rises, oscillating around a "pivotal period" (nominally 14 days). Formula: DMIt = INT(P/Vt), where Vt = today's volatility = σt(C,n)/[average σ over m days] (n nominally 5, m nominally 10). **Ambiguity flagged verbatim**: the source text states DMI becomes "larger than 14" when volatility increases, which appears internally inconsistent with the DMIt=INT(P/Vt) formula's implication that DMI should shrink as Vt rises — preserved as stated rather than silently corrected (possible OCR/extraction artifact).
- **Ehlers' Instantaneous Trend** (John Ehlers, Traders.com, May 2000): built on the Hilbert Transform. An adaptive trend line (AT) paired with a "Trigger" line. Entry: IF Trigger crosses above AT, THEN buy tomorrow at a limit; IF Trigger crosses below AT, THEN sell short tomorrow at a limit. **Gap flagged**: exact AT/Trigger formulas and the specific limit-price reference are embedded-graphic gaps. Tested on euro futures 2000-April 2018, described as giving "excellent results" — but the strategy is explicitly characterized in the source as **mean-reverting despite being framed as a "trend" method.**

### Meyers' Adaptive Range Breakout (Adaptive Intraday System)

Dennis Meyers, "Range Roving," *Active Trader*, March 2003. Based on the classic price-volatility relationship that the expected n-bar range is proportional to √n. Key mechanical distinction: the "high range" and "low range" at lag n use the actual high/low of the single bar located n bars ago (not the highest-high/lowest-low over the past n bars). These raw ranges are normalized by the n-period ATR and by a power function n^a (correcting for the range ratio's natural growth with n), producing Normalized High Range (NHR) and Normalized Low Range (NLR). The maximum NHR/NLR over the most recent n periods form threshold levels.

- **Buy** when NHR > threshold-high AND NLR < threshold-low.
- **Sell** when NLR > threshold-low AND NHR < threshold-high.
- Close all trades 5 minutes before the close of trading.
- Four optimized variables: n (lookback, suggested max 25), a (power function), and the two threshold values. **Gap flagged**: the cited QQQ-optimized numeric parameter values did not survive extraction (shown as blank/unrecoverable placeholders in the source). Kaufman's conditional endorsement: "if this method can be shown to be consistent over a reasonably long test period, producing about one trade per day, it is worth pursuing" — explicitly framed as tentative, not proven.

### An Adaptive Process (Concept, Not a Formula)

An adaptive method need not be a formula — it can be a *process*: periodically re-testing/re-optimizing a system on more recent data (walk-forward testing, Ch.21) rather than continuously varying a smoothing constant. **Core trade-off stated explicitly**: the faster you react (shorter re-test/adaptation window), the less data you have to validate the decision.

- A single robust trend-period selection (from testing a long history spanning many regimes) can be profitable across bull/bear/sideways/shock conditions but will carry large drawdowns; adaptive speed-changing attempts to reduce those drawdowns and raise the percentage of profitable trades, not to increase raw profit per se.
- **Closing caution (explicit author warning)**: adaptive systems must be built carefully around infrequent conditions — there is abundant test data for medium/low volatility but comparatively little for very high volatility, so an adaptive system's behavior in rare extreme conditions is inherently less validated. Two competing adaptive philosophies are named: (1) slow the trend down and simply hold the existing position until volatility subsides (what KAMA does), or (2) speed the trend up to try to capture the faster/shorter price swings directly (Kaufman suggests this "may be a better solution, if it can be done," without asserting it has been done successfully).

---

## Multiple Time Frame Trend Methods (Kaufman Ch.19)

**Framing**: Chapters 8-9 combined two trend or momentum periods using a single data frequency (daily); this chapter covers systems that deliberately mix intraday, daily, and/or weekly data to improve both timing and results. **History**: the first Triple Screen-style approach is attributed to Barbara Diamond (1981, CME floor trader), developed after CQG's charting system first made multiple time frames technically possible.

**Standard 3-tier structure that has "solidified"**: very short bars for timing, medium bars for the primary trading signal, longer bars for the overall trend/big picture. **Core rationale**: trends are best identified over longer periods, but entries require a faster response — combining two or three frequencies, each targeting a specific purpose, lets a trader filter/select short-term entries with a better-than-average chance of becoming winners. **Named single-timeframe problems this design solves**: very short-term data has high noise that obscures direction; weekly-only charts show clear direction but present higher risk and little opportunity for a good entry point (Kaufman Ch.19).

### Tuning Two Time Frames to Work Together

An indicator alone is rarely profitable as a standalone system — its primary value is timing. When combining a longer-term trend indicator (e.g., a moving average) with a faster timing indicator (e.g., RSI or stochastic), the two must be explicitly "tuned" to work together — the timing indicator is no longer evaluated as its own system but purely for its speed/responsiveness relative to the trend's holding period.

**Key reframing of overbought/oversold signals**: once a trend signal has fired, only the *first* subsequent oversold reading of the timing oscillator matters for entry — and "oversold" in an uptrend context may be a much higher-than-classic value (worked example: 50 on a 0-100 scale can function as the effective oversold threshold within an established uptrend). **Cross-reference**: this is explicitly identified as the same technique used by Linda Raschke in her First Cross system (Ch.9) — see the entry for Raschke's First Cross in the momentum knowledge base file for the full rule set.

**Sizing the timing oscillator's speed to the trend's holding period**: if a trend system's typical holding period is ~2 months (~45 business days), the timing oscillator should have a good chance of an improved entry within the first 3 days; for a ~1-week average holding period, use a 30-minute or 1-hour chart for the momentum timing.

### Elder's Triple Screen Trading System

Dr. Alexander Elder, *Trading for a Living* (1993, updated 2014). **Purpose**: combine trend-following (direction) and oscillators (timing) across exactly three time frames, each with a specific role.

- **Time-frame ratio rule**: each time frame relates to the adjacent one by a factor of ~5 (Elder's own observed ratio). If daily is the middle period, the short interval is ~1-2 hours and the long interval is ~1 week. If the middle interval is 10 minutes, short-term = 2 minutes, long-term = 1 hour.
- **Display convention**: original method used three physical screens; can be shown as stacked panels instead, with the highest-frequency data on top.
- **Screen 1 — The Major Move (lowest-frequency data, e.g., weekly)**: identifies the market's overall "tide"/major trend (or lack thereof). Elder's tool: the slope of the weekly MACD histogram, roughly equivalent to a 13-week/1-quarter exponential smoothing. **Rule**: trend is up when this week's value is higher than last week's; down when lower.
- **Screen 2 — The Intermediate Move (middle-frequency data, e.g., daily — the actual trading timeframe)**: the specific oscillator choice is secondary to correctly matching the time frame. Elder suggests two named oscillators (a stochastic can substitute):
  - **Force Index**: smoothed with a 2-day exponential (smoothing constant = 0.333). **Long-entry logic (all steps required)**: (1) Screen 1's major move must be up; (2) confirm the long when the 2-day-exponential Force Index falls below its center line but does NOT fall below its own recent multi-week low (a stochastic substitute buys when the stochastic falls below 30).
  - **Elder-Ray**: separates bullish ("bull power") from bearish ("bear power") price movement. **Buy logic**: (1) Screen 1's major move must be up; (2) bear power is negative but rising, and must not turn positive. **Two additional optional filters**: (3) the most recent bull-power peak is not significantly lower than the previous peak; (4) bear power is rising from a bullish divergence. (Sell rules mirror the buy rules.)
- **Screen 3 — Timing (highest-frequency data, e.g., 60-minute bars in the worked example)**: fastest-response screen, primarily for intraday breakout entries — mechanically a simple Buy Stop at the shortest bar's breakout level (worked example: buy when the current hourly bar's high exceeds the highest high of the prior day's hourly bars); no separate calculation needed.
- **Risk Rules (3-step stop-loss process for a long position)**: (1) initial stop below the entry day's low OR the previous day's low, whichever is lower; (2) move the stop to breakeven as soon as practical (must leave room between the stop and current price); (3) thereafter trail the stop to protect 50% of the highest achieved open profit; optionally also consider taking profits when the stochastic/Force Index rises above the 70% level.
- **Terminology note preserved verbatim**: the source describes the screens in reverse numbering relative to display order in one description ("Screen 1 (or panel 3) holds the longest time frame while Screen 3 (panel 1) shows the shortest") — preserved exactly as stated to avoid introducing an ambiguity not present, or present, in the original.

### Robert Krausz's Multiple Time Frames (The Fibonacci Trader)

Robert Krausz, *W. D. Gann Treasure Discovered*. Described by Kaufman as "the most robust and fully automated approach to multiple time frames," combining Gann-derived geometric/fractal market theory with three coordinated time frames.

- **Underlying theoretical premise**: as a trend-following calculation period increases (e.g., 50 days → 100 days), expect larger profit per trade, greater reliability, larger interim (drawdown) risk, and proportionally fewer trades — and the reverse as the period shortens; very short periods suffer disproportionately from noise and cost drag, very long periods suffer from large equity swings. **Test-quality heuristic explicitly stated**: results across a range of calculation periods should form "a flowing picture, with a clear, profitable pattern and continuity" — an implicit warning against choosing an isolated "best" period that doesn't fit this smooth pattern (an overfitting red flag).
- **Three time frames, fractal framing**: shortest = the actual trading time frame; two longer frames add confirming context. Patterns are explicitly compared to fractals — "you cannot have an hourly chart without a 15-minute chart, because the longer time period is composed of shorter periods." Price-level/profit-target relationships are woven from Fibonacci ratios and Gann principles.
- **Six "Laws of Multiple Time Frames"** (Krausz, copyrighted): (1) every time frame has its own structure; (2) higher time frames overrule lower time frames; (3) prices in the lower time frame tend to respect the "energy points" of the higher time frame's structure; (4) energy points of support/resistance created by the higher time frame's "vibration" can be validated by the action of the lower time periods; (5) the trend created by the *next* (higher) time period defines the tradable trend; (6) what appears as chaos in one time period can be order in another.
- **Worked example (U.S. Bonds June 1998, daily + 10-minute + 50-minute frames)**: the Daily HiLo Activator (a stepped moving average of daily highs) and the 50-minute HiLo Activator (MA of 50-minute highs used as a Buy Stop, or of 50-minute lows used as a Sell Stop) combined with 10-minute Gann swings — the 10-minute Gann swing signaled a trend change well before the daily Gann swing signaled the same change; since the dominant (daily) trend slope was down, short entries were taken in that direction using the faster 10-minute signal for timing, with each subsequent 10-minute swing low offering an opportunity to add to the position.
- **Practical time-frame selection warning (explicit, non-substitutable point)**: a 10-period MA of 1-hour bars is NOT interchangeable with a 40-period MA of 15-minute bars, even though both nominally span the same total elapsed time — nor is a 10-week MA interchangeable with a 50-day MA. **Reason given**: averaging cannot fully remove noise, and fewer, larger data points over the same span always produce a smoother result than more, smaller data points — genuinely different bar frequencies give a materially different market picture than "equivalent"-length moving averages built from a single frequency.

### Martin Pring's KST (Know Sure Thing) System

Martin J. Pring, *Martin Pring on Market Momentum* (1993). **Purpose**: multiple-time-frame confirmation system built entirely from stacked rate-of-change (ROC) indicators at different calculation periods, each with its own "unique cycle" — alignment across cycles flags major/intermediate tops and bottoms.

- **ROC formula used for KST**: ROC = [(Close_t / Close_(t-n)) − 1] × 100 (net percent price change from t-n to t). The source explicitly distinguishes this from the "true" calculus rate-of-change (change per unit time, i.e., slope), noting the KST convention uses the simpler percent-change version with a unit time step. **Gap flagged, with a labeled reconstruction**: the book's own inline notation for both formulas is an embedded-graphic gap; the ROC formula above is reconstructed from the standard published percent rate-of-change definition, consistent with the surrounding prose. See `05_momentum.md` for ROC as a standalone momentum oscillator.
- **Preferred calculation periods**: Pring prefers a long-term view — 6-, 12-, and 24-month ROC. The chapter's own worked example instead uses 6-, 12-, and 24-**week** ROC on S&P 500 futures to illustrate the alignment concept at a shorter horizon.
- **Basic trading logic (from the 3 raw ROC lines, before building the composite KST)**: (1) a trendline based on roughly half the longest ROC period sets the trade direction; (2) the longer (24-period) ROC identifies the major move; (3) strongest price moves occur when all three ROC values move in the same direction; (4) if the 24-period ROC peaks while the other two are still rising, any resulting sell-off is expected to be minor (likewise if the 12- and 6-period ROC peak while the 24-period is still rising); (5) a significant sell-off is expected only when all three ROC values peak together, then all three decline together.
- **Smoothing step**: the raw 6-, 12-, and 24-month ROC values are smoothed — 6- and 12-month with a 6-period MA, 24-month with a 9-period MA. Because the ROC calculation itself effectively speeds up price movement (rather than lagging it), this modest smoothing introduces very little lag.
- **Composite KST indicator construction**: a weighted sum of four smoothed ROC calculation periods, step-weighted in proportion to their length: (1) 24-period ROC, weight 4; (2) 18-period ROC, weight 3; (3) 12-period ROC, weight 2; (4) 9-period ROC, weight 1. **Author's own noted gap**: Pring's original description does not specify the smoothing/averaging period applied to the 18-period ROC component; the chapter uses 9 as its own working assumption for that missing value.
- **Trading signal generation** (weekly S&P 500 futures, Jan 2000-Dec 2003): plot the smoothed ROC alongside the KST indicator and a 12-period MA trendline; trade in the direction of the MA trendline, timed by the KST crossing the ROC line following the trendline's first turn; can be exited on the opposite-direction KST/ROC crossover, given a suitable choice of ROC periods. **Speed trade-off noted**: an ROC that is too fast makes it difficult to capture larger trend profits — a slower ROC calculation is generally preferable.
- **Timeframe generality**: results are described as clearer/more reliable on monthly data, but the method generalizes to any data frequency; a faster daily-data version can be built to filter trades or improve timing, but KST signals must always be used in combination with a trendline (not as a standalone system).
- **Additional uses**: because KST is described as an exceptionally smooth, low-lag indicator, it can also be used like an RSI or stochastic — with divergence and its own trendlines drawn directly on the KST line.

---

## Cross-Book Notes on Trend Following

### Hilpisch, *Python for Algorithmic Trading* — SMA Crossover (secondary source)

Hilpisch's book demonstrates an **SMA Crossover** strategy purely as a pedagogical illustration of Python implementation technique, not as a vetted alpha source (the book explicitly and repeatedly warns about data snooping/overfitting). Entry: IF SMA1 (short window) > SMA2 (long window) THEN go/stay long; IF SMA1 < SMA2 THEN go/stay short (or neutral in the long-only event-based version). No risk rules or stop-loss are built into the base implementation. `SMAVectorBacktester.optimize_parameters()` performs a brute-force grid search over (SMA1, SMA2) via `scipy.optimize.brute`; example: EUR/USD 2010-2019, brute force over SMA1∈[30,50] and SMA2∈[200,300] found an optimum SMA1=48, SMA2=238 (gross performance 1.5×) vs. 1.29× for the default (42,252) — the book itself flags this specific optimized parameterization as "a textbook overfitting risk" per its own Ch.4 "Data Snooping and Overfitting" discussion, with no out-of-sample validation shown for this strategy. A separate event-based backtest on AAPL.O (2010-2019) showed SMA net performance dropping from +462.05% (no costs) to +419.60% (with $10 fixed + 1% proportional costs) — described as more cost-resilient than the book's momentum variant because of its lower trade count.

**Difference from Kaufman's treatment**: Hilpisch's SMA crossover is presented with no risk rules, no bands/channels, and no discussion of the calculation-period-choice-as-primary-decision framing that dominates Kaufman Ch.8 — it is a bare vectorized crossover used to teach backtesting code, not a fully specified trading system in Kaufman's sense. Where Kaufman explicitly separates "noise" from "volatility" and builds an entire chapter (Ch.17) of adaptive techniques around that distinction, Hilpisch's book does not address adaptivity in its trend-following example at all.

### Chan, *Quantitative Trading* — momentum/trend mentions (secondary source, brief)

Chan's book focuses primarily on mean-reversion and factor-based strategies; explicit trend-following content is limited. It cites Moskowitz et al. (2012) for the claim that time-series momentum exists "in virtually every instrument examined" (an external finding, not independently re-validated by the author beyond illustrative examples), and separately describes a "Year-on-Year Seasonal Trending Strategy" (Heston & Sadka style) that hypothesizes a stock's performance in a given calendar month repeats in the same calendar month one year later — explicitly framed by Chan as momentum/trending rather than mean-reversion, despite the "seasonal" label.

### Pardo, *Evaluation and Optimization of Trading Strategies* — trend systems as methodology vehicles (secondary source)

Pardo's book is explicitly about the *methodology* of testing/optimizing/validating strategies, not a catalog of trading systems, and uses trend systems only as illustrative vehicles:

- **Turtle Trading Strategy (TTS)**: see the cross-check note under "The Turtles" above — Pardo's version is a bare-bones illustration (x-day-high/low entry, shorter-y-day-high/low exit) used to contrast systematic vs. discretionary trading knowledge, not a full rule reconstruction.
- **Two-Moving-Average Crossover System ("MA2"/"EOTS-MA")**: Pardo's primary running teaching example across multiple chapters for scripting, optimization, degrees-of-freedom, and overfitting illustrations. Entry: go long when MA1 (fast) crosses from below to above MA2 (slow); go short on the mirror-image cross (reversing, always in the market). **Required condition**: the slow MA period must be at least double the fast MA period ("Y is never less than 2 times X"). Used in Ch.10's worked 100-candidate optimization (MA1 scanned 1-10 step 1, MA2 scanned 15-60 step 5) and in Ch.13's overfitting parable, where adding a second MA plus two volatility bands to chase higher in-sample profit (from $10,000 to $65,000 across escalating parameter additions) produces a system that **loses $15,000 out-of-sample** — a direct illustration of the overfitting risk inherent in over-parameterizing a trend-crossover system. A bare 5×20 crossover version, tested by Pardo across a 5-market/5-period grid, produced "questionable" (inconsistent, sometimes deeply negative) results, used as an explicit example of a marginal/weak trend strategy.

**Difference from Kaufman's treatment**: Pardo never asserts the MA2 crossover is intended as a real trading system — it exists purely to demonstrate testing pitfalls, in direct contrast to Kaufman's extensive six-system comparison study (Ch.8) and two-trendline crossover treatment, which are presented as genuine candidate trading systems with real backtested performance figures (e.g., the euro futures 100/30-day crossover result).

---

## Summary of Explicit Warnings and Caveats Carried Through This File

- Trend trading works only when the market is trending; there is no universally best trending technique (Kaufman Ch.8).
- Adding stops or profit-taking to a basic trend system reduces or eliminates the ability to capture the fat tail necessary for long-term profitability — an explicit trade-off, not a free improvement (Kaufman Ch.8).
- The best historic backtest results "often come from overfitting the data, and is a poor choice for trading" (Kaufman Ch.7); Pardo's MA2 overfitting parable is a worked illustration of the same principle from a different book.
- The Hutson sc=2/(n+1) conversion does NOT produce a true lag-equivalent between exponential smoothing and a same-"n" moving average (Kaufman Ch.7).
- The Box Size Dilemma for point-and-figure and Renko is presented as an explicitly unresolved problem — no fully satisfying fixed-increment solution exists for a market spanning very different price/volatility regimes (Kaufman Ch.5).
- The Turtles' System 1 filter rule and the copper backtest are both explicitly flagged by Kaufman as simplified/incomplete reconstructions, not full-fidelity originals (Kaufman Ch.5).
- A contingent entry rule (waiting for a pullback) risks never entering at all — delaying execution to the next open improved entry price ~75% of the time in cited tests but reduced total profits because missed fast breakouts outweighed the improvements (Kaufman Ch.8).
- Adaptive systems are inherently less validated in rare, extreme-volatility conditions, since abundant test data exists for medium/low volatility but comparatively little for high volatility (Kaufman Ch.17).
- Ehlers' Instantaneous Trend is explicitly characterized as behaving like a mean-reversion strategy despite being framed as a "trend" method (Kaufman Ch.17) — a naming/behavior mismatch worth flagging for implementers.
- Numerous exact formulas throughout this file (Wilder's Swing Index K/TR sub-formulas, the Turtles' loss-threshold multiple and unit-cap values, Keltner Channel's original formula, percentage/volatility band arithmetic, Modified Bollinger Band center-line/band formulas, KAMA's SC-from-ER sub-formula, McGinley Dynamics, Hull Moving Average, Ehlers' fractal-dimension power law and Instantaneous Trend AT/Trigger formulas, Knapp's Parabolic threshold values, Meyers' optimized parameter values, the CP2 and MDI crossover-projection formulas, and Pring's KST/ROC inline notation) were embedded as graphics in the original PDFs and did not survive text extraction. Each is flagged at its point of use above; where a standard, widely-published (non-proprietary) form exists, it is given as an explicitly labeled reconstruction rather than presented as verbatim book content.
