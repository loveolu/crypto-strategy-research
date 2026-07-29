# Archive — CLOSED family hypothesis cards

Moved out of `knowledge_base/hypothesis_bank.md` on 2026-07-28 (repair item 3) to bring the
Research Director's mandatory context load under budget. **Nothing here was deleted or edited** —
every card is reproduced verbatim, including any `Already tested by this project` lines.

**The ledger, not this file, is authoritative for status.** A family appearing here is closed *as of
the move*; if `knowledge_base/hypothesis_bank.md`'s FAMILY STATUS LEDGER later reopens a family, the
cards stay here and the ledger row governs. Reopening does not require moving cards back.

Reopening any family requires the specific new evidence named in its closure record
(`research/meta_reviews/meta_review_1.md` §4) — never a re-parameterization.

---

## Contents

- [Mean reversion on crypto OHLCV (all tested timeframes)](#mean-reversion-on-crypto-ohlcv-all-tested-timeframes)
- [Intraday / time-of-day / sub-daily constructions](#intraday--time-of-day--sub-daily-constructions)
- [Short side / symmetric TSMOM of the champion's gate](#short-side--symmetric-tsmom-of-the-champions-gate)
- [BTC-ETH pairs / relative value / rotation / dominance / ratio](#btc-eth-pairs--relative-value--rotation--dominance--ratio)
- [DVOL daily-bar champion modifications](#dvol-daily-bar-champion-modifications)
- [Regime-classifier overlay (ER, ADX, MESA, HMM)](#regime-classifier-overlay-er-adx-mesa-hmm)

---

## Mean reversion on crypto OHLCV (all tested timeframes)

### Oscillator/Momentum Fade Framework

**Description**: Fade a momentum/oscillator reading once it reaches a statistically or visually
defined extreme, betting on reversion toward zero/neutral. Umbrella covering: Kaufman's generic
fade taxonomy (aggressive/minor-confirmation/major-confirmation/timing variants), RSI 30/70 fade with
Wilder's failure-swing divergence confirmation, and the RSI 1-day-jump trigger variant.
**Supporting concepts**: bounded-oscillator behavior in ranging markets (`05_momentum.md`).
**Suggested indicators**: RSI (14-day, Wilder) — `13_indicator_reference.md`.
**Expected market conditions**: best in genuinely ranging/noisy (not trending) regimes; fixed
thresholds miscalibrate as the volatility regime changes.
**Expected weaknesses / known failure modes**: an accidentally-reversed (i.e., trend-following)
backtest of the "aggressive fade" variant still produced "outstanding, consistent profits" in
Kaufman's own test — casting doubt on naive fading generally; too-short RSI periods keep the
oscillator pinned outside 70/30 for extended stretches, giving false persistence signals.
**Related hypotheses**: 2-Day RSI Mean-Reversion, Bollinger Band Mean-Reversion Fade, Divergence
Index/Fisher Transform Mean-Reversion.
**Source attribution**: Kaufman Ch.9 (Wilder 1978); `03_mean_reversion.md`.

### 2-Day RSI Mean-Reversion (Stokes / Connors-style)

**Description**: Replace 1-day price differences with 2-day-overlapping differences before computing
RSI; buy when 2-day RSI penetrates 10 moving lower, short when it penetrates 90 moving higher, exit
one day later. A graduated scaling-in variant sizes position by how deep the RSI extreme is (e.g.,
&lt;5 → 100%, &lt;10 → 75%, ...).
**Supporting concepts**: oscillator-fade framework, regime-dependence of a single indicator's behavior
(`03_mean_reversion.md`).
**Suggested indicators**: 2-day RSI — `13_indicator_reference.md`.
**Expected market conditions**: explicit, documented regime-shift finding — this exact construction
behaved as a TREND indicator on the S&P 1970-1998, then reversed into MEAN-REVERTING after ~1998 —
a rare, explicitly author-documented case of an indicator's regime-fit flipping over time.
**Expected weaknesses / known failure modes**: 1-day holding period is highly sensitive to
commissions/slippage; scaling-in add/unwind logic is ambiguous in the source. See
`18_common_failure_modes.md` §5 (fee/slippage kill-floors).
**Related hypotheses**: Oscillator/Momentum Fade Framework, Divergence Index/Fisher Transform
Mean-Reversion.
**Source attribution**: Kaufman Ch.9 (Michael Stokes, MarketSci Blog, Dec. 2008); `03_mean_reversion.md`.

### Net Momentum Oscillator / Stochastics / Ultimate Oscillator Fades

**Description**: Three related bounded-oscillator fade variants using different underlying
constructions: Net Momentum Oscillator (AU−AD difference rather than ratio, Chande & Kroll);
Stochastics Fade (%K/%D below 10 / above 90, Lane, best filtered to fade only in the direction of a
larger trend); Ultimate Oscillator (7/14/28-day weighted blend designed to reduce whipsaw vs.
single-period oscillators, Larry Williams).
**Supporting concepts**: oscillator-fade framework (`03_mean_reversion.md`).
**Suggested indicators**: Net Momentum Oscillator, Stochastic Oscillator, Ultimate Oscillator —
`13_indicator_reference.md`.
**Expected market conditions**: ranging/non-trending regimes; Stochastics Fade explicitly performs
better when filtered by a larger prevailing trend (buy dips within an uptrend rather than fading
blind).
**Expected weaknesses / known failure modes**: Stochastics used as an EXIT timing rule is explicitly
flagged as dangerous — if price never retraces, the confirming signal may never occur or arrive very
late, and delayed exits are real losses, not theoretical ones.
**Related hypotheses**: Oscillator/Momentum Fade Framework, Divergence Index/Fisher Transform
Mean-Reversion.
**Source attribution**: Kaufman Ch.9 (Chande & Kroll 1994; George Lane; Larry Williams 1985);
`03_mean_reversion.md`.

### Kurtosis-Skew Mean-Reverting Strategy

**Description**: Buy when excess kurtosis crosses above 0, skew is negative, and volatility is above
a minimum threshold (mirror for shorts) — a distinct fade variant of the same indicator set used
trend-confirmingly elsewhere.
**Supporting concepts**: statistical-moment-based regime gating (`06_volatility.md`).
**Suggested indicators**: excess kurtosis, skew, ATR-based volatility filter — `13_indicator_reference.md`.
**Expected market conditions**: performed better at HIGHER volatility in Kaufman's own comparison — the
opposite of the trend-following variant built on the same indicators.
**Expected weaknesses / known failure modes**: the source's own printed mean-reversion "sell" rule is
flagged as an internal inconsistency (appears to duplicate the trend-following sell condition rather
than mirror the buy) — see `17_author_disagreements.md` §8; any implementation should use the
corrected/mirrored rule, not the rule as verbatim printed.
**Related hypotheses**: Volatility Regime Filters (Volatility-Based §), the trend-following
Kurtosis-Skew variant noted in Adaptive Trend-Speed Systems.
**Source attribution**: Kaufman Ch.18; `03_mean_reversion.md`, `16_research_hypotheses.md` §5.

### DeMark's Sequential™

**Description**: A fully mechanical 3-stage (Setup, Intersection, Countdown) countertrend exhaustion
system flagging severely overextended moves as reversal candidates, with a typical 24-39-day
formation duration.
**Supporting concepts**: exhaustion/overextension detection (`03_mean_reversion.md`).
**Suggested indicators**: consecutive close-vs-4-days-ago comparisons, high/low intersection test,
countdown sequence — `13_indicator_reference.md`.
**Expected market conditions**: countertrend/exhaustion detection after extended directional moves.
**Expected weaknesses / known failure modes**: no adjustable "dial"/parameter exists for robustness
testing (a single fixed rule set) — Kaufman states reliability is therefore unverifiable by his own
standard parameter-sweep method; recycling risk (competing setups) complicates entry timing.
**Related hypotheses**: Taylor Trading Technique, Nofri's Congestion-Phase System.
**Source attribution**: Kaufman Ch.4 (Thomas DeMark); `03_mean_reversion.md`, `09_exits.md`.

### Dogs of the Dow / O'Higgins / Foolish Four & Rating-Service Basket Spreads

**Description**: Annual-rebalance value/mean-reversion basket buying the highest-dividend-yield Dow
stocks (Dogs), optionally narrowed by price (Small Dogs/puppies) or a further elimination rule
(Foolish Four); generalized as a "Rating-Service Basket Spread" — converting any validated
fundamental/technical ranking service into a systematic long/short basket.
**Supporting concepts**: value/mean-reversion at the portfolio-construction level
(`03_mean_reversion.md`, `12_portfolio_construction.md`).
**Suggested indicators**: dividend-yield ranking, stock-price ranking — n/a (fundamental screen, not a
technical indicator).
**Expected market conditions**: long-only, annual-rebalance value tilt; O'Higgins cites 10.8%/yr
(1992-2011) vs. S&P 9.6%/yr.
**Expected weaknesses / known failure modes**: Kaufman's own separate test of the RETURN-based (rather
than yield-based) "buy the laggards" version performs poorly — an unreconciled tension with the cited
O'Higgins result, flagged rather than resolved.
**Related hypotheses**: Reversed Dogs-of-the-Dow + Vol-Hedge Overlay (Cross-Sectional/Portfolio §, the
opposite-direction/momentum variant of this same universe).
**Source attribution**: Kaufman Ch.13/Ch.22 (O'Higgins; Sheard); `03_mean_reversion.md`.

### Gap-Fade / Gap-Pullback Trading

**Description**: Fade intraday price gaps — futures downward gaps have a documented 98-100% tendency
to cross back above the prior close intraday; stock upward gaps retrace ~40% of the gap on average.
Includes specific entry rules for pullback/re-entry timing around the gap.
**Supporting concepts**: overreaction and reversion (`03_mean_reversion.md`); UTC-daily-open as a
crypto-native gap-proxy (`15_crypto_specific.md`, `16_research_hypotheses.md` §5).
**Suggested indicators**: gap size relative to prior close, volume (drop-off signals exhaustion) —
`13_indicator_reference.md`.
**Expected market conditions**: strongest and most consistent in futures (S&P, bonds, crude, euro);
gaps tend to run WITH the prevailing trend, so this is a day-trading complement, not a trend
replacement.
**Expected weaknesses / known failure modes**: explicit overgeneralization warning — single extreme
events dominate bucket statistics (a large Netflix gap example distorted the aggregate); individual
names vary enormously (Tesla showed no tradeable confidence despite dramatic price history).
**Related hypotheses**: UTC-Daily-Boundary Gap Proxy (Crypto-Specific §), True Gap Breakout Entry
(Breakout §, the opposite/continuation interpretation of a "true" gap).
**Source attribution**: Kaufman Ch.15; `03_mean_reversion.md`, `16_research_hypotheses.md` §5.
**Already tested by this project**: no direct crypto gap-fade test yet run; flagged in
`16_research_hypotheses.md` as a weaker analog for crypto since continuous trading produces no
overnight order backlog to generate a true discontinuity.

### Taylor Trading Technique

**Description**: A short-term mean-reverting 3-day cycle (Buying Day → Selling Day → Short Sale Day)
exploiting an uptrend's rhythmic pullback/rally/resistance pattern; a simplified, computer-programmable
reduction buys on the third consecutive lower close and sells short on the third consecutive higher
close.
**Supporting concepts**: cyclical/rhythmic price behavior within a broader trend (`03_mean_reversion.md`).
**Suggested indicators**: consecutive-close counting, optional 100-day MA trend filter —
`13_indicator_reference.md`.
**Expected market conditions**: best combined with an underlying trend-following method; best suited
to the equity index/liquid futures Taylor originally studied.
**Expected weaknesses / known failure modes**: the original method requires continuous full-time
monitoring; Kaufman explicitly flags the simplified/computerized reduction as "unreasonably simple"
and likely to disappoint on individual stocks.
**Related hypotheses**: Gustafson's Price Persistency Strategy, Nofri's Congestion-Phase System.
**Source attribution**: Kaufman Ch.15 (George Douglass Taylor, 1950); `03_mean_reversion.md`.

### Gustafson's Price Persistency Strategy

**Description**: Long-only Martingale-style consecutive-close fade — buy after 4 consecutive lower
closes, exit after a 5-day up run or unconditionally after 8 days — exploiting persistent equity
upward bias.
**Supporting concepts**: secular-trend-biased mean reversion (`03_mean_reversion.md`).
**Suggested indicators**: consecutive daily close-direction count — `13_indicator_reference.md`.
**Expected market conditions**: designed for/tested on a secular bull market (S&P).
**Expected weaknesses / known failure modes**: explicit author-acknowledged single-regime validation
trap — never validated against a genuine multi-year bear market despite a ~20-year out-of-sample test
window. See `18_common_failure_modes.md` §6 (small-sample traps).
**Related hypotheses**: Taylor Trading Technique, Reversal-Day/Outside-Reversal-Day Patterns.
**Source attribution**: Kaufman Ch.22 (Gordon Gustafson, 2002); `03_mean_reversion.md`.

### Reversal-Day, Weekday, and Day-of-Month Patterns

**Description**: A cluster of chart-pattern and calendar mean-reversion rules: weekday/weekend
reversal tendencies (market-dependent — bonds/S&P favor a Monday reversal of Friday's direction);
Reversal-Day and Outside-Reversal-Day patterns (higher high/lower close in an uptrend or the mirror);
and a day-of-month institutional-flow fade specific to bonds (early-month weakness ahead of reliable
late-month buying).
**Supporting concepts**: institutional flow timing, calendar effects (`03_mean_reversion.md`,
`07_market_regimes.md`).
**Suggested indicators**: day-of-week/day-of-month calendar position, daily high/low/close pattern
classification — n/a (calendar-based, not a technical indicator).
**Expected market conditions**: explicitly market-dependent — no universal rule; 10-year T-notes
showed a contrarian ~50%+ tendency to follow through on downward reversals even against the bond bull
market backdrop of the test window.
**Expected weaknesses / known failure modes**: classification (trend-continuation vs. fade) is
explicitly market-dependent, not generalizable; day-of-month patterns are attributed specifically to
retirement-account contribution schedules and month-end accounting closes — mechanisms with no clear
crypto-native equivalent (`16_research_hypotheses.md` §5, explicitly flagged as a poor crypto fit).
**Related hypotheses**: Seasonal/Calendar Regime Effects (Regime-Based §).
**Source attribution**: Kaufman Ch.15; `03_mean_reversion.md`.
**Already tested by this project**: research/research_index.md #6 (overnight/time-of-day breakout,
Zarattini-style) — FAIL, N=5-10 trades below statistical floor, "equities liquidity cycle absent in
24/7 crypto"; research/research_index.md #12 (intraday hours 21-22 UTC anomaly) — REAL but untradeable, fees
exceed edge 25:1.

### Connors AD-Ratio / CHADTP Breadth Fade

**Description**: Trades the NYSE advance/decline ratio as a MEAN-REVERSION signal (contrary to most
trend-confirming breadth literature) — sell the index when the AD ratio is extremely high, buy when
extremely low, exit after 5 days unless reversed. CHADTP (Conners-Hayward) adds a smoothed 5-day
AD-difference plus an S&P point-penetration trigger for a more mechanically complete version.
**Supporting concepts**: breadth as noise vs. signal, methodological disagreement over breadth's
regime-fit (`03_mean_reversion.md`, `17_author_disagreements.md`).
**Suggested indicators**: NYSE advance/decline ratio, CHADTP — `13_indicator_reference.md`.
**Expected market conditions**: equity indexes specifically; argued to be mean-reverting due to large
aggregate price noise; best confirmed by depressed/below-average volume (sideline cash ready to
re-enter).
**Expected weaknesses / known failure modes**: exact numeric thresholds are an extraction gap; this is
presented as a genuine methodological disagreement (breadth as trend-confirming vs. mean-reverting),
not settled consensus — see `17_author_disagreements.md`.
**Related hypotheses**: Crypto "Breadth" via a Basket Advance/Decline Line (Crypto-Specific §).
**Source attribution**: Kaufman Ch.12 (Larry Connors, 2005; Conners & Hayward, 1995);
`03_mean_reversion.md`.

### Intraday Price Zones (Jackson / Scorpio / Gould)

**Description**: Divide a reference price range into discrete zones and fade the "noise" middle zones
back toward the average. J.T. Jackson's Intraday Zones use prior-day H/L/C to build 6 zones; the
Scorpio variant substitutes ATR for a volatility-relative construction; Gould's Long-Term Price Zones
apply the same template over a multi-year horizon (5 zones of a 3-year range).
**Supporting concepts**: mean-reversion band construction (`03_mean_reversion.md`).
**Suggested indicators**: prior-day H/L/C zone boundaries, ATR-based zones — `13_indicator_reference.md`.
**Expected market conditions**: works best when the actual zone-frequency distribution deviates from
the theoretical random baseline (higher central clustering favors the fade); a perfectly random zone
distribution implies no profit potential — an explicit, falsifiable pre-condition.
**Expected weaknesses / known failure modes**: selling in the lowest zone or buying in the highest
offers little profit opportunity by construction; Scorpio's variant is trend-following (not
mean-reverting) specifically on daily/clear-trend data — an explicit regime-dependent flip of the same
template.
**Related hypotheses**: Divergence Index/Fisher Transform Mean-Reversion.
**Source attribution**: Kaufman Ch.18 (J.T. Jackson; Bruce Gould); `03_mean_reversion.md`.

### Divergence Index & Fisher Transform Mean-Reversion

**Description**: Divergence Index (DI) is a volatility-adjusted MA-difference oscillator with a
self-adjusting SD-based band (rather than MACD's fixed threshold), fading into the trend at band
extremes; the Fisher Transform reshapes price's channel-position distribution toward a sine-wave-like
density, producing sharper, less-laggy turning-point signals for fading at cycle extremes.
**Supporting concepts**: adapting oscillator bands to changing volatility (`03_mean_reversion.md`,
`16_research_hypotheses.md` §1).
**Suggested indicators**: Divergence Index, Fisher Transform — `13_indicator_reference.md`.
**Expected market conditions**: cycling/mean-reverting regimes; Fisher Transform recommends a minimum
volatility floor filter, since low-vol periods produce false relative highs/lows without real profit
opportunity.
**Expected weaknesses / known failure modes**: contrasted with plateauing oscillators that instead
signal a soft TRENDING regime — using the wrong one for the active regime is a direct source of error.
**Related hypotheses**: MESA/Hilbert Cycle-Presence Regime Gate (Regime-Based §, the "is there a cycle
at all" question this hypothesis assumes has already been answered "yes").
**Source attribution**: Kaufman Ch.9/Ch.11 (Ehlers, cited); `03_mean_reversion.md`,
`16_research_hypotheses.md` §1.

### Khandani & Lo Short-Term Cross-Sectional Reversal

**Description**: Daily-rebalanced strategy buying the worst-performing stocks and shorting the
best-performing stocks (1-day reversal) within a large universe.
**Supporting concepts**: liquidity-driven (not fundamentals-driven) mean reversion
(`03_mean_reversion.md`, `05_momentum.md`).
**Suggested indicators**: daily relative-return ranking — n/a (cross-sectional ranking, not a
technical indicator).
**Expected market conditions**: originally reported more profitable in small/microcap names than
large-cap.
**Expected weaknesses / known failure modes**: Chan's own replication found pre-cost Sharpe only 0.25
(vs. the original authors' claimed 4.47), collapsing to −3.19 post 5bp transaction cost — an extreme
transaction-cost sensitivity from high turnover; switching rebalance timing from close to open
materially changed viability (pre-cost Sharpe 0.25→4.43, post-cost −3.19→+0.78), showing execution
timing itself is as load-bearing as the signal.
**Related hypotheses**: Cointegration / Pairs Trading & Intermarket Spread Strategies, Cross-Sectional
Top-K Momentum Portfolio (the opposite-direction long-horizon cousin).
**Source attribution**: Chan Ch.2-3 (citing Khandani & Lo 2007); `03_mean_reversion.md`.

### Nofri's Congestion-Phase System

**Description**: A pure congestion/pullback mean-reversion system usable only WITHIN a defined
sideways range: if price closes in the same direction for 2 consecutive days, take the opposite
position at the close of day 2, take profit at the close of day 3 (a 3-day reversal system).
**Supporting concepts**: range-bound/congestion-phase trading (`03_mean_reversion.md`,
`08_entries.md`).
**Suggested indicators**: consecutive-close direction counting, congestion-range top/bottom —
`13_indicator_reference.md`.
**Expected market conditions**: explicitly ONLY within a defined congestion/sideways range; a new
high/low outside the range invalidates it.
**Expected weaknesses / known failure modes**: backtested well historically but showed large losses in
SOME markets during the 2008 financial crisis — Kaufman himself suggests a high-volatility filter may
be needed; the author's own operationalization used no stop-loss (relying entirely on the 1-day hold).
**Related hypotheses**: Taylor Trading Technique, DeMark's Sequential™.
**Source attribution**: Kaufman Ch.4; `08_entries.md`, `09_exits.md`.

---

### Price-Shock Reversal / Fade (daily scale)

**Description**: A True-Range-vs-lagged-average-True-Range shock ratio exceeding a threshold (e.g.,
&gt;3.0) tends to be followed by a next-day reversal, tested across bonds/crude/S&P over a 28-year
window — distinct from the (unforecastable) initial shock reaction itself.
**Supporting concepts**: price-shock backtest contamination and detection (`06_volatility.md`,
`18_common_failure_modes.md` §3).
**Suggested indicators**: True Range vs. lagged average ATR shock ratio — `13_indicator_reference.md`.
**Expected market conditions**: post-shock regime specifically; only the reversal-DAY pattern is
systematic — the shock day itself is not tradeable in advance ("no one can profit from a price shock
by clever planning, only by luck").
**Expected weaknesses / known failure modes**: backtests systematically overstate shock-trade win
rates; if more than roughly half a candidate strategy's favorable trades are shock-driven, this is
diagnostic of BOTH overstated return AND understated risk at once — see
`18_common_failure_modes.md` §3. Crypto's own documented shock history (COVID crash, FTX collapse,
2021 China mining-ban crash) makes this arguably more urgent for crypto than for the book's
traditional-market examples.
**Related hypotheses**: Intraday Price-Shock Fade (Breakout §, the intraday-resolution companion),
Price-Shock P&L Decomposition (a validator/audit method, not itself a hypothesis — see
`16_research_hypotheses.md` §2 and research/research_index.md's open-hypotheses priority list item #2).
**Source attribution**: Kaufman Ch.14, Ch.21-22; `06_volatility.md`, `18_common_failure_modes.md` §3.

### Intraday Price-Shock Fade (contrast case)

**Description**: Defines a "shock" bar as intraday volatility ≥ some multiple (e.g., 2.2x for gold) of
the 20-day average bar volatility, then places FADE (not continuation) limit orders at close ± a
factor × average bar volatility, exiting when volatility reverts to average or at session end.
**Supporting concepts**: price-shock detection at intraday resolution (`06_volatility.md`,
`16_research_hypotheses.md` §5).
**Suggested indicators**: 20-day average bar volatility, shock multiplier factor —
`13_indicator_reference.md`.
**Expected market conditions**: backtested profitable on gold (2010-2017), &gt;50% winning trades.
**Expected weaknesses / known failure modes**: this is explicitly a MEAN-REVERSION system despite being
documented in the source's "volatility breakout" section — included here as an explicit contrast case,
not a trend-continuation hypothesis, so as not to be confused with the Volatility Breakout family
above.
**Related hypotheses**: Price-Shock Reversal/Fade (Volatility-Based §, the daily-scale analog),
Volatility Breakout Based on the Open/Previous Close.
**Source attribution**: Kaufman Ch.16 (TSM Intraday Shocks 2); `04_breakouts.md`, `06_volatility.md`.

---

---

## Intraday / time-of-day / sub-daily constructions

### Opening Range Breakout (ORB) Family

**Description**: Fix a breakout threshold from the first period of trading (time-based or bar-count
based), then trade the breakout through that range. Family: 1st Hour Breakout, N-Bar Breakout,
Crabel's volatility-calibrated ORB (per-market thresholds, filtered by preceding-pattern compression
such as inside days), Mark Fisher's ACD method (layered A/C bands + time confirmation + pivot bias),
Larry Williams' filtered ORB variants (with a %R-style or multi-day-close filter), Raschke's NR4
range-contraction breakout, and Raschke & Conners' Momentum Pinball (LBR/RSI filter gating the 1st-hour
breakout).
**Supporting concepts**: intraday volatility structure, opening-range statistics (`04_breakouts.md`).
**Suggested indicators**: opening-range high/low, %R, NR4 narrow-range detection — see
`13_indicator_reference.md` ("Opening Range Breakout").
**Expected market conditions**: intraday, works best with genuine directional follow-through after the
opening period; Crabel's inside-day filter raised win rate in every tested market (e.g., bonds
60%→76%).
**Expected weaknesses / known failure modes**: intraday reversals (new high, new low, new high within
one session) can produce shockingly large losses in the N-Bar variant; breakouts near the close offer
little profit opportunity; the trailing-stop mechanism is the "only missing feature" of Raschke's
published NR4 rule set — not resolvable from the source.
**Related hypotheses**: N-Day/Channel Breakout Trend Family (the daily-bar parent paradigm),
Volatility Breakout Based on the Open/Previous Close, UTC-Daily-Boundary substitute (Crypto-Specific §
— crypto has no true "session open").
**Source attribution**: Kaufman Ch.16 (Toby Crabel 1989/1990; Mark Fisher 2002; Larry Williams; Linda
Raschke; Conners & Raschke 1995); `04_breakouts.md`, `08_entries.md`, `16_research_hypotheses.md` §5.
**Already tested by this project**: research/research_index.md #6 (overnight/time-of-day breakout,
Zarattini-style, 2 variants) — FAIL, N below statistical floor.

### Volatility Breakout Based on the Open or Previous Close

**Description**: Band = anchor price (day's open or previous close) ± a breakout factor (typically
&lt;1.0) × n-day ATR; centering on previous close embeds trend information, centering on open is
trend-neutral. A mean-reversion FADE variant (reversing the same directional logic, same-day only) is
explicitly documented as a distinct, smoother-equity-curve alternative.
**Supporting concepts**: volatility as the breakout-scaling unit (`04_breakouts.md`, `06_volatility.md`).
**Suggested indicators**: n-day ATR, breakout factor — `13_indicator_reference.md`.
**Expected market conditions**: S&P 30-minute case study (2010-2017) found profitable breakout factors
clustered 0.5-1.0; previous-close centering outperformed open-based centering.
**Expected weaknesses / known failure modes**: no a priori answer exists for open-vs-previous-close
centering — Kaufman's own explicit recommendation is one-parameter-at-a-time testing per market rather
than simultaneous multi-parameter optimization; the mean-reversion fade variant performed only 14%
worse in total profit while roughly DOUBLING average profit per trade on far fewer trades — a genuine,
documented case where the same mechanical construction supports two opposite paradigms with similar
edge.
**Related hypotheses**: Opening Range Breakout Family, Dynamic Breakout System.
**Source attribution**: Kaufman Ch.16 (TSM Flexible Intraday Breakout); `04_breakouts.md`.

### UTC-Daily-Boundary / Funding-Settlement Time-of-Day Effects

**Description**: Bucket bars by time-since-UTC-00:00 (common daily-candle boundary) and 8-hour
perpetual-funding settlement times, substituting for the book's exchange-session open/close and
day-of-week findings, since crypto has no true "session" and the boundary choice is itself an
assumption to test, not a given.
**Supporting concepts**: time-of-day/gap patterns adapted to a 24/7 market (`15_crypto_specific.md`,
`16_research_hypotheses.md` §5).
**Suggested indicators**: time-since-UTC-midnight, funding-settlement proximity — n/a (calendar/time
construction, not a technical indicator).
**Expected market conditions**: not regime-specific; a structural/timing hypothesis.
**Expected weaknesses / known failure modes**: this project's own overnight/time-of-day breakout test
(Zarattini-style, substituting Mon/Tue/Fri UTC timing for the equities overnight-drift mechanism)
FAILED with only 2-10 trades in 3-5 years — well below any statistical floor — because the underlying
equities overnight-liquidity-cycle mechanism has no real analog in a 24/7 market. Separately, this
project DID find a real, statistically stable intraday anomaly (hours 21-22 UTC, t=2.4-3.0 across
multiple tests) — but fees exceed the edge by roughly 25:1, making it real but untradeable at this
project's cost structure; useful only for execution timing, not as a standalone signal.
**Related hypotheses**: Opening Range Breakout Family (Breakout §), Gap-Fade/Gap-Pullback Trading
(Mean-Reversion §), Day-of-Month Institutional-Flow Fade.
**Source attribution**: Kaufman Ch.15-16 (project inference); `15_crypto_specific.md`,
`16_research_hypotheses.md` §5.
**Already tested by this project**: research/research_index.md #6 — FAIL (overnight breakout, N too small);
#12 — REAL but untradeable (hours 21-22 UTC anomaly, fees exceed edge 25:1).

### Tick/Volume-Bar Construction for Crypto

**Description**: Accumulate crypto trade data into tick-count or volume-threshold bars rather than
fixed-time (1m/5m/1h) candles, testing whether this reduces false trend signals — crypto genuinely
provides trade-level tick data, often more completely/cheaply than traditional feeds, unlike the
book's own single (non-generalized) worked FX example.
**Supporting concepts**: bar-construction methodology as a distinct axis from signal logic
(`16_research_hypotheses.md` §4).
**Suggested indicators**: none (a data-representation change, not an indicator).
**Expected market conditions**: not regime-specific; a low-effort comparative test against this
project's existing fixed-time OHLCV pipeline.
**Expected weaknesses / known failure modes**: untested; the book's own single worked example is
explicitly flagged as illustrative, not a broad statistical claim — any crypto adaptation needs its own
multi-asset, multi-period validation before being trusted.
**Related hypotheses**: none directly, though this is a prerequisite/infrastructure change that could
in principle be applied under any hypothesis in this file.
**Source attribution**: Kaufman Ch.16 (project inference); `15_crypto_specific.md`,
`16_research_hypotheses.md` §5.

---

## Short side / symmetric TSMOM of the champion's gate

### Time-Series Momentum (Moskowitz-style)

**Description**: An instrument's own past returns predict its own future returns; simplest form goes
long/short based on the sign of yesterday's return, generalized to the sign of a rolling-window mean
of recent returns.
**Supporting concepts**: return persistence / autocorrelation (`05_momentum.md`).
**Suggested indicators**: sign of rolling mean return over a lookback window — `13_indicator_reference.md`.
**Expected market conditions**: Hilpisch's gold (XAU=) EOD test found a 3-day rolling mean
substantially outperformed 1-day or 2-day windows; an intraday version outperformed the underlying
instrument on AAPL/S&P 1-minute bars in a single-day example.
**Expected weaknesses / known failure modes**: explicitly "quite sensitive to the time-window
parameter" (an overfitting-risk flag Hilpisch states himself); at 0.1% transaction costs on the gold
2010-2019 example, the momentum=3 variant's ending value flipped from +$7,395.53 outperformance
(no costs) to −$2,652.93 underperformance — transaction costs completely erase the edge at short
lookbacks/high turnover. See `18_common_failure_modes.md` §5.
**Related hypotheses**: Basic Momentum Trend-Following, Cross-Sectional Momentum.
**Source attribution**: Moskowitz, Ooi & Pedersen 2012 (cited); Hilpisch Ch.4/8/10; `05_momentum.md`.
**Already tested by this project**: research/research_index.md #8 (61-strategy autonomous search, incl. multiple
momentum/ensemble variants) — 0/61 passed; Sharpe ceiling ~1.2 on retail OHLCV; fee drag kills
high-frequency variants specifically.

---

## BTC-ETH pairs / relative value / rotation / dominance / ratio

### Cointegration / Pairs Trading & Intermarket Spread Strategies

**Description**: Trade the stationary spread between two related, individually non-stationary price
series via a fitted hedge ratio, betting on reversion to the long-run mean; holding period informed by
the Ornstein-Uhlenbeck half-life. Umbrella covering Chan's formal cointegration methodology plus a
family of Kaufman-documented intermarket spread trades: Bond-Utility Arbitrage, S&P/High-Yield-Bond
timing, Intermarket Index Ratio (S&P/DJIA, S&P/Russell 2000), Momentum-Difference and Stress-Indicator
pairs trades (Lennar/KB Home), price-difference-band pairs (ICBC-BOC), and Butterfly Spreads
(term-structure calendar arbitrage).
**Supporting concepts**: stationarity/cointegration testing, statistical arbitrage
(`03_mean_reversion.md`).
**Suggested indicators**: CADF test, Ornstein-Uhlenbeck half-life, rolling correlation of price
difference — `13_indicator_reference.md` ("Cointegrating Augmented Dickey-Fuller Test").
**Expected market conditions**: requires a genuinely stationary spread; correlation alone is NOT a
valid substitute screening tool (Chan's own KO/PEP example: correlated 0.4849 but fails cointegration).
**Expected weaknesses / known failure modes**: disproportionately vulnerable to data errors and
survivorship bias; Chan's own worked ES Bollinger-Band spread example collapsed from Sharpe≈3
pre-cost to Sharpe≈−3 with just 1bp transaction cost — the single most load-bearing transaction-cost
warning in the whole knowledge base, see `18_common_failure_modes.md` §5; Kaufman's own S&P/NASDAQ
ratio worked example failed catastrophically in a 2008-style regime shift, then went silent in a
subsequent low-vol regime.
**Related hypotheses**: Chan's Regime-Based Momentum/Mean-Reversion Switching Framework (Momentum §),
Cross-Sectional Top-K Momentum Portfolio.
**Source attribution**: Chan Ch.2-3, Ch.7; Kaufman Ch.13; `03_mean_reversion.md`, `15_crypto_specific.md`.
**Already tested by this project**: `research_index.md` row 23 (T-021) — **REJECTED at pre-gate**. A genuine BTC-ETH cointegration test (F-4: Regime-Gated Pairs Revival) hit its falsification condition before any trials were spent. The pre-gate census proved the rolling cointegration relationship passed in only 20% of windows, and broke down completely in the post-2024 ETF era. The pairs/relative-value direction is definitively CLOSED. (Prior related test: ETH/BTC z-score fade, row 13 — FAIL, TEST Sharpe -1.45).

### BTC-ETH Cointegration Pairs Trading

**Description**: A genuinely new, formally-tested cointegrated spread strategy between BTC and ETH
(distinct from a raw correlation screen or a simple z-score fade) — this project's history to date has
been entirely single-asset trend/mean-reversion or a BTC+ETH directional OVERLAY, never a true
cointegration-tested spread.
**Supporting concepts**: Cointegration / Pairs Trading & Intermarket Spread Strategies (Mean-Reversion
§) — the exact statistical methodology (CADF test, half-life estimation) this hypothesis requires
before being trusted.
**Suggested indicators**: CADF test, Ornstein-Uhlenbeck half-life — `13_indicator_reference.md`.
**Expected market conditions**: requires a genuinely stationary BTC-ETH spread, not merely a high
correlation — this is the exact distinction Chan's own KO/PEP example is meant to warn against.
**Expected weaknesses / known failure modes**: this project's ETH/BTC z-score fade (a related but
methodologically distinct construction that skipped formal cointegration testing in favor of a raw
z-score) already FAILED (TEST Sharpe −1.45) — any future attempt at a genuine cointegration test should
explain why a formally-tested spread would behave differently from the z-score fade before spending a
trial, per this project's own multiple-comparisons discipline.
**Related hypotheses**: Cointegration / Pairs Trading & Intermarket Spread Strategies (Mean-Reversion
§), BTC-Dominance Rotation / ETH-BTC Z-Score Fade (below).
**Source attribution**: Kaufman Ch.13; Chan Ch.7 (project inference for crypto application);
`15_crypto_specific.md`.
**Already tested by this project**: a related but distinct construction (ETH/BTC z-score fade,
research/research_index.md #13) — FAIL. The formally-cointegration-tested version remains an open, untested
hypothesis.

### BTC-Dominance Rotation / ETH-BTC Z-Score Fade

**Description**: Trade rotations in BTC's share of total crypto market capitalization ("dominance") or
fade z-score extremes in the ETH/BTC ratio, on the theory that capital rotates between BTC and
alt/large-cap ETH in cycles.
**Supporting concepts**: cross-sectional relative-strength rotation applied within the crypto asset
class (`12_portfolio_construction.md`, `05_momentum.md`).
**Suggested indicators**: BTC dominance ratio, ETH/BTC price ratio z-score — n/a in
`13_indicator_reference.md` (crypto-native constructions).
**Expected market conditions**: theorized to work during "alt season" rotations; this project's own
finding is that alt satellites have been dead since 2024 (no alt season observed).
**Expected weaknesses / known failure modes**: this project's own test found the BTC-dominance rotation
proxy was a pure train artifact (TRAIN Sharpe 1.67 → TEST Sharpe 0.21) and the ETH/BTC z-score fade
outright failed (TEST Sharpe −1.45); a 75/25 champion+z-fade blend was marginal with an OOS-negative
sleeve, "not defensible."
**Related hypotheses**: BTC-ETH Cointegration Pairs Trading (above, the more rigorously-tested
alternative approach to the same underlying asset pair).
**Source attribution**: project's own construction, not sourced from any of the five books;
`15_crypto_specific.md` (crypto-transferability framing of cross-sectional rotation generally).
**Already tested by this project**: research/research_index.md #13 (Forven-derived, 2026-07-02) — FAIL on both
constructions; DSR-gate now mandatory as of this same session (cumulative n_trials≈95).

### F-4. Regime-Gated Pairs Revival (class B — forward-contingent; pairs family CLOSED on current data)
**Description**: Parked in iteration 14: trade the BTC-ETH spread only inside trailing rolling-EG-
passing windows. The 2021-24 stationarity pocket is n=1 regime, so any backtest on current data is
in-sample by construction.
**Reopening condition**: a *forward* rolling cointegration census (computed on data accrued after
2026-07, never refit on the closed window) re-establishes ≥60% passing 730d windows. Until then the
family stays CLOSED per the ledger.

---

## DVOL daily-bar champion modifications

### IV/HV Relative-Value Arbitrage & Volatility Dispersion Trading

**Description**: Sell implied-volatility exposure / buy historic-volatility exposure (or vice versa)
when the two diverge, using a normalized (stochastic-style) spread indicator as the entry/exit
trigger; a related options-based variant (volatility dispersion) exploits IV differences between an
index and its components.
**Supporting concepts**: mean-reversion in volatility itself, not price (`06_volatility.md`).
**Suggested indicators**: stochastic-normalized IV and HV spread — `13_indicator_reference.md`.
**Expected market conditions**: IV/HV divergence regimes; explicitly NOT a directional edge once
normalized — "never assume overbought flips directly to oversold."
**Expected weaknesses / known failure modes**: no tradeable HV instrument exists (workarounds use a
correlated proxy, e.g. SPY for HV vs. UVXY for IV); described by the source itself as "not a true
arbitrage but a timing method."
**Related hypotheses**: Deribit IV-vs-RV Proxy (Crypto-Specific §), VIX/IV Mean-Reversion Systems
(Volatility-Based §).
**Source attribution**: Kaufman Ch.13 (alternative construction cited to Ernest Chan, Machine Trading,
2017); `03_mean_reversion.md`, `06_volatility.md`.

### VIX / IV Mean-Reversion Systems

**Description**: Treats implied-volatility indexes as themselves mean-reverting and tradeable.
Conners VIX Reversal 9 (CVR9) buys S&P futures after a VIX range-expansion-then-reversal pattern;
Conners RSI-Timed VIX strategy buys when the broad market is in an established uptrend AND VIX shows
an extreme short-term RSI spike; a MarketSci variant trades VIX itself via a 10-day EMA/SMA crossover.
**Supporting concepts**: volatility mean-reversion (`06_volatility.md`).
**Suggested indicators**: VIX (via a tradeable proxy such as UVXY/VX futures), 2-day RSI of VIX, 10-day
EMA/SMA of VIX — `13_indicator_reference.md`.
**Expected market conditions**: VIX spike-and-reversal events; the RSI-timed variant specifically
requires an established broad-market uptrend as context.
**Expected weaknesses / known failure modes**: the underlying cash VIX index is not directly
tradeable — all variants require a proxy (UVXY, VX futures) whose own basis/roll dynamics introduce
additional noise not present in the original signal.
**Related hypotheses**: IV/HV Relative-Value Arbitrage, Deribit IV-vs-RV Proxy (Crypto-Specific §, the
crypto analog — flagged as having no comparably liquid crypto VIX equivalent).
**Source attribution**: Kaufman Ch.20 (Larry Conners; MarketSci Blog, March 2011); `06_volatility.md`.

### Deribit IV-vs-RV Proxy (Crypto VIX Analog)

**Description**: Use Deribit BTC/ETH options-implied volatility vs. realized volatility as a crypto
substitute for the traditional VIX/HV framework — a genuinely novel angle distinct from this project's
prior blocked funding-rate/basis pivots.
**Supporting concepts**: IV/HV Relative-Value Arbitrage, VIX/IV Mean-Reversion Systems (both
Mean-Reversion/Volatility-Based §).
**Suggested indicators**: Deribit implied volatility, realized volatility — n/a in
`13_indicator_reference.md` (crypto-native data source).
**Expected market conditions**: IV/HV divergence regimes, by analogy to the traditional-market version;
no comparably liquid crypto VIX-equivalent instrument currently exists, which is precisely why this
angle is flagged as worth exploring rather than assumed solved.
**Expected weaknesses / known failure modes**: untested; the traditional-market version's own explicit
warning applies directly — "never assume overbought flips directly to oversold" once normalized; no
tradeable crypto HV instrument exists, so any implementation needs a correlated proxy.
**Related hypotheses**: IV/HV Relative-Value Arbitrage (Mean-Reversion §), Perp-Spot Basis /
Funding-Rate Carry Arbitrage.
**Source attribution**: Kaufman Ch.20 (project inference); `15_crypto_specific.md`,
`16_research_hypotheses.md` §4.

### F-3. DVOL Change-Based Construction (class B — forward-contingent; daily-bar level constructions CLOSED)
**Status: REJECTED (Task T-022, 2026-07-18)**
**Description**: The Director-verified durable finding is that Δ5d DVOL *leads* Δ5d rv30
(avg_lead +0.2489 vs avg_lag +0.0714) — but both closed mechanisms consumed the LEVEL comparison
(z_iv spike veto; DVOL/100 vs rv30 max()). A change-based construction (e.g., sizing responds to
DVOL *acceleration*, not level) targets the actual leading signal. Explicitly named as the only
surviving DVOL shape in index open-hypothesis #9.
**Reopening condition (pre-registered here)**: must first pass (1) a fresh episode/materiality
census showing the change-signal fires ≥6 times while in-market AND fires in the TEST split; and
(2) a harm census showing affected days are actually adverse (the P2 lesson: VRP is
positive-carry — a change-trigger must demonstrate it selects different days than the level
trigger did). Without both, no trial.

---

## Regime-classifier overlay (ER, ADX, MESA, HMM)

### Efficiency Ratio Regime Gate

**Description**: Kaufman's net-move-over-sum-of-absolute-moves noise measure used as a simple,
computable filter for "trend-favorable" (high ER) vs. "mean-reversion-favorable" (low ER) markets —
a regime gate that can sit alongside (not replace) an existing trading signal.
**Supporting concepts**: market noise as a regime driver (`01_market_structure.md`,
`07_market_regimes.md`).
**Suggested indicators**: Efficiency Ratio (ER) — `13_indicator_reference.md`.
**Expected market conditions**: high ER favors trend-following, low ER favors mean-reversion —
Kaufman's own explicit design premise, not merely an empirical correlation.
**Expected weaknesses / known failure modes**: "noise is not the sole determinant of success";
market noise baselines differ structurally BY market — don't mistake a return-to-normal-noise-level
for a genuine regime breakout.
**Related hypotheses**: Adaptive Trend-Speed Systems (Trend-Following §1, ER used as the smoothing-
constant driver rather than a standalone gate), MESA/Hilbert Cycle-Presence Regime Gate.
**Source attribution**: Kaufman Ch.1; `07_market_regimes.md`, `16_research_hypotheses.md` §1.
**Already tested by this project**: not yet directly tested as a standalone regime gate; flagged as an
open, untested hypothesis in `16_research_hypotheses.md` §1 and `15_crypto_specific.md`.
**Status: TESTED — REJECTED (2026-07-19, T-028 / H-EffRatio, trial #100).** All three pre-gates
PASSED: F-A harvestability (74 episodes, 27.7% of in-market days, 50 in TEST), F-B harm (low-ER
in-market days genuinely adverse — forward-10d median −0.49% / mean −0.36% vs unconditional +0.77% /
+1.49%), F-C idealized bound (+32.2pp MC-tail improvement). Trial #100 then failed on **Gate 7
(parameter stability)**: the surface is a cliff, not a plateau — the adjacent (lb=30, 25th-pct) cell
scores TEST Sharpe 0.186, *below the champion's own 0.391*, against 0.617 at the locked (30, 33rd)
cell; nine cells span 0.186–0.933. Reviewer probe additionally established that the entire held-out
gain is **a single 5-day episode** (Oct-2025 crash): disabling that one veto window collapses
candidate TEST Sharpe 0.617 → **−0.096**, and 228 of 351 TEST days fall after the veto's last firing.
Reproducibility, data integrity and lookahead all audited clean.

**Status: TESTED — REJECTED (2026-07-19, T-029 / H-ERScale, zero trials).** Stopped at pre-gate F-P2 (Episode dispersion). A continuous multiplier variant (`min(1.0, r_t / b)`) successfully tracked the materially-affected days (19.1%), passing F-P1, but failed F-P2 precisely where the binary veto failed: 65.5% of TEST days (230 days) postdated the last materially-affected day. The continuous ramp suffers the exact same single-episode concentration pathology.

**Status: TESTED — REJECTED (2026-07-19, T-030 / H-ADXGate, zero trials).** Stopped at pre-gate F-P2. The absolute-threshold ADX construction suffered the exact same single-episode concentration pathology as the distribution-relative ER constructs: 65.2% of TEST days postdate the last veto day (2025-10-10). The problem is not threshold staleness; the market simply has no recent classifier-detectable chop on this dataset.

**FAMILY CLOSED.** As pre-registered in T-030, the third F-P2 failure spanning two structurally different signals (ER and ADX) and both threshold constructions formally establishes the single-episode concentration as a property of the frozen dataset itself. This CLOSES the regime-classifier-overlay family: this card plus ADX Trend/No-Trend, MESA/Hilbert Cycle-Presence, and Hidden Markov Regime-Switching. Reopening requires the research window extended ≥ 6 months past 2026-05-27 with a fresh held-out split, or a forward-lane-documented in-market chop episode.
**Durable finding:** ρ(ER30, rv30) = +0.071 (BTC) / +0.069 (ETH) full-window, 0.317 / 0.151 on TEST.
ER is confirmed **orthogonal to volatility level**, so this rejection is a genuinely distinct failure
mode from the positive-carry-VRP result that killed T-022 and T-024 — not a repeat of it.

**CONTINUOUS-ACTION SUCCESSOR — ASSIGNED (Task T-029 / H-ERScale, Director cycle #9, 2026-07-19).**
Same signal, same lookback (30), same breakpoint (bottom tercile, inherited verbatim — not re-fitted);
the **single changed variable is the action**: the binary veto `w→0` is replaced by a continuous ramp
`m_t = min(1, r_t / (1/3))` applied to the champion's final weight *after* quantization and *not*
re-quantized. Grounded in the T-028 Reviewer's own conclusion that the constraint successors inherit
is on the *action*, not the *signal*, and in Kaufman's use of ER as a continuous smoothing-constant
modulator (Adaptive Trend-Speed family, §1) rather than a switch. Four zero-trial pre-gates:
F-P1 materiality (≥5% of in-market days with |Δw|≥0.05, ≥20 in TEST — tests whether the 25% quantizer
swallows the mechanism, per rows #15/#19), F-P2 episode dispersion (≥3 distinct TEST calendar months,
≤50% of TEST days postdating the last firing), F-P3 idealized fee-free bound (≥5.0pp MC-tail
improvement, TEST Sharpe degradation ≤0.05), F-P4 leave-one-episode-out (TEST Sharpe minus the
largest-contributing episode must still beat the champion). F-P2 and F-P4 are the T-028 Reviewer's
proposed standing single-episode checks, adopted by the Director and promoted to pre-registered
zero-cost gates. Would be trial #101 only if all pass.
**Declared family implication (revised for T-029)**: rejection at **F-P3, F-P4 or the trial gate
stack** CLOSES the regime-classifier-overlay family — this card plus the ADX Trend/No-Trend,
MESA/Hilbert Cycle-Presence and Hidden Markov Regime-Switching cards below — because the signal would
then be proven real and orthogonal (T-028) with *both* action shapes failed, making an ADX/MESA/HMM
substitution a re-parameterization rather than a new test. A stop at **F-P1 or F-P2 does NOT close
the family** (the mechanism would never have received a fair test). See `research/NEXT_TASK.md` §4.3.

*Original assignment text follows.* — ER30 bottom-tercile
(causal expanding threshold, zero fitted parameters) as a binary chop veto on the champion's core
gate; sizing layer untouched. Three zero-trial pre-gates precede any trial: F-A harvestability
census (≥6 in-market episodes, ≥5% of in-market days, ≥1 in TEST), F-B harm census (low-ER in-market
days must be adverse on forward-10d median AND mean), F-C idealized fee-free upper bound (≥5.0pp MC
tail improvement, TEST Sharpe degradation ≤0.05). Would be trial #100 only if all three pass.
Selected as the direct adoption of the T-024 Engineer recommendation to separate "good volatility"
(trend) from "bad volatility" (whipsaw) — ER is scale-free and path-shape-based, not a volatility
level measure, which is the specific mechanism that killed T-022 and T-024.
**Declared family implication**: an F-B failure closes the regime-classifier-overlay family as a
whole — this card plus the ADX Trend/No-Trend, MESA/Hilbert Cycle-Presence, and Hidden Markov
Regime-Switching cards below — because all four partition the same in-market days by the same
underlying noise/trend property. See `research/NEXT_TASK.md` §4.

### MESA / Hilbert Cycle-Presence Regime Gate

**Description**: Uses the presence/absence of a detectable clean short-term price cycle (found ~20% of
the time, per Ehlers) as a trend-vs-sideways classifier — a genuinely trending market cannot
simultaneously show a clean short-term cycle. Builds an instantaneous trendline vs. smoothed price
trendline; trend is deemed to exist if the two haven't crossed within the last half-dominant-cycle.
**Supporting concepts**: Ehlers' "lateral shift in thinking" — use cycle presence as a binary regime
gate rather than trying to trade the cycle's phase directly (`07_market_regimes.md`,
`16_research_hypotheses.md` §1).
**Suggested indicators**: MESA, Hilbert Transform, dominant cycle period — `13_indicator_reference.md`.
**Expected market conditions**: explicit trend-vs-cycle (sideways) classifier by design.
**Expected weaknesses / known failure modes**: cycle detection is meant to be USED as regime
information, not traded directly; Ehlers' related Instantaneous Trend construction is explicitly noted
elsewhere in the source to behave like a mean-reversion strategy despite its "trend" name — an
explicit naming/behavior mismatch worth flagging to any implementer.
**Related hypotheses**: Efficiency Ratio Regime Gate, Fisher Transform Mean-Reversion (Mean-Reversion
§).
**Source attribution**: Kaufman Ch.11 (John Ehlers); `07_market_regimes.md`, `16_research_hypotheses.md` §1.
**Status: CLOSED WITHOUT TESTING (2026-07-19, family closure via T-030 / H-ADXGate F-P2).** Member
of the regime-classifier-overlay family closed by T-030's pre-registered F-P2 rejection: three
firing-set concentration failures (T-028, T-029, T-030) spanning two structurally different signals
(ER, ADX) and both threshold constructions (distribution-relative, absolute) establish that the
frozen research window contains no recent classifier-detectable chop — a pathology no MESA/Hilbert
substitution can escape. **Reopening condition (pre-registered, T-030 §3):** frozen research window
extended ≥ 6 months beyond 2026-05-27 with a freshly cut held-out split, OR a forward-dry-run-lane
documented completed in-market chop episode. Not a re-parameterization.

### ADX Trend / No-Trend Regime Gate

**Description**: Uses ADX level and/or slope thresholds (e.g., rising above 25, falling below 20) to
classify a market as trending vs. consolidating, gating which family of system (trend vs.
mean-reversion oscillator) should be active.
**Supporting concepts**: directional-movement-based regime classification (`07_market_regimes.md`,
`05_momentum.md`).
**Suggested indicators**: ADX, +DMI/−DMI — `13_indicator_reference.md`.
**Expected market conditions**: explicitly a trend/range classifier, not a directional signal itself.
**Expected weaknesses / known failure modes**: exact threshold values across the several cited variants
(Ruggiero's rules, Kestner's oscillator-with-ADX-filter) are partly embedded-graphic extraction gaps.
**Related hypotheses**: ADX-Filtered Oscillator (Momentum §), Parabolic SAR Trend/Exit Systems
(Trend-Following §1).
**Source attribution**: Kaufman Ch.9 (Ruggiero; Lars Kestner 2003); `07_market_regimes.md`.
**Status: ASSIGNED (Task T-030 / H-ADXGate, Director cycle #10, 2026-07-19).** Binary chop veto
(the T-028 action) driven by ADX14 < 20 — an **absolute literature threshold**, chosen precisely
because both ER cycles (T-028 trial #100; T-029 pre-gate stop) died on distribution-relative
expanding-threshold staleness (ER never breached its expanding tercile after Oct-2025). Single
changed variable vs T-028 is the **signal**; zero fitted parameters (14 and 20 are Wilder/Kestner
constants). Gated pre-trial stack: F-P0 replication, F-H1 vol-proxy (|ρ(ADX,rv30)| ≤ 0.70),
F-H2 fresh harm census on the ADX day-set, F-P1 materiality (≥5% in-market days, ≥20 TEST veto
days), F-P2 episode dispersion (≥3 TEST months, ≤50% of TEST days postdating last firing),
F-P3 idealized fee-free bound, F-P4 leave-one-episode-out. Would be trial #101 only if all pass.
**Declared family implication (binding, `research/NEXT_TASK.md` §3):** rejection at F-P2, F-P3,
F-P4 or F-T CLOSES the regime-classifier-overlay family (this card + ER + MESA/Hilbert + HMM) on
the frozen research dataset — F-P2 because a third firing-set concentration failure spanning two
signals and both threshold constructions establishes the pathology as a property of the frozen
TEST window itself; reopening requires the research window extended ≥6 months past 2026-05-27
with a fresh held-out split, or a forward-lane-documented in-market chop episode. A stop at
F-H1/F-H2/F-P1 closes at most this card; the family stays OPEN.

**Status: TESTED — REJECTED (2026-07-19, T-030 / H-ADXGate, zero trials; Reviewer-verified by
exact rerun plus an independent TA-Lib-ADX recomputation of the decisive census).** F-P0/F-H1/
F-H2/F-P1 all passed (replication landed exactly on the 1.154/0.391/33.6% baseline; ρ(ADX14,rv30)
full-window +0.247 BTC / +0.181 ETH; harm census median −0.13% / mean +0.78% vs unconditional
+0.77% / +1.49%, both strictly below; 224 veto days = 22.9% of in-market, 45 in TEST). Stopped at
**F-P2**: TEST veto days span 5 months (Jun–Oct 2025) but the last veto day is **2025-10-10** and
229/351 TEST days (65.2%) postdate it — one day off T-029's ER result (2025-10-09, 65.5%). The
absolute literature threshold did NOT escape the concentration pathology, proving it is a property
of the frozen evaluation window, not of threshold construction. **Family closure triggered as
pre-registered** (see FAMILY CLOSED note on the Efficiency-Ratio card and the family-status
ledger). Caveats recorded for any future reopening: ρ(ADX14, rv30) on the TEST split alone was
**+0.709 (BTC)** — above the 0.70 alarm that the full-window gate measures — so in the recent
regime ADX is borderline a volatility proxy on BTC; and the ADX harm census is weaker than ER's
(mean +0.78% is below baseline but positive, vs ER's outright-negative −0.36%).

### Hidden Markov Model Regime-Switching

**Description**: Academic approach proposing 2+ regimes with different price-distribution parameters
and constant transition probabilities, fit via maximum likelihood, forecasting the next-period regime.
**Supporting concepts**: formal statistical regime-switching (`07_market_regimes.md`).
**Suggested indicators**: fitted regime-transition probabilities, regime-specific distribution
parameters — n/a (a statistical model, not a technical indicator).
**Expected market conditions**: intended generically for bull/bear, high/low-vol, or
trending/mean-reverting classification.
**Expected weaknesses / known failure modes**: Chan's own explicit, strongly-worded rejection —
"generally useless for actual trading purposes" because constant transition probabilities cannot say
WHEN a switch is imminent. Included here as a documented negative finding, not a recommendation.
**Related hypotheses**: Chan's Regime-Based Momentum/Mean-Reversion Switching Framework (Momentum §,
Chan's own preferred alternative), Data-Mining Turning-Points Regime-Trigger Model.
**Source attribution**: Chan Ch.7 (surveyed and rejected); `07_market_regimes.md`,
`16_research_hypotheses.md` §1.
**Status: CLOSED WITHOUT TESTING (2026-07-19, family closure via T-030 / H-ADXGate F-P2).** Member
of the regime-classifier-overlay family closed by T-030's pre-registered F-P2 rejection (see the
Efficiency-Ratio and MESA/Hilbert cards for the full rationale: three concentration failures across
two signals and both threshold constructions; the frozen window lacks recent classifier-detectable
chop). **Reopening condition (pre-registered, T-030 §3):** frozen research window extended ≥ 6
months beyond 2026-05-27 with a freshly cut held-out split, OR a forward-dry-run-lane documented
completed in-market chop episode. Not a re-parameterization. Chan's own "generally useless for
actual trading purposes" verdict stands as the independent prior.

---
