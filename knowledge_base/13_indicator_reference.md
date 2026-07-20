# 13. Indicator Reference — Consolidated Encyclopedia

Merged from the `Indicators.md` files of all five source books:
- **Pardo** = Pardo, *Evaluation and Optimization of Trading Strategies*
- **Chan** = Chan, *Quantitative Trading*
- **Vince** = Vince, *Mathematics of Money Management*
- **Hilpisch** = Hilpisch, *Python for Algorithmic Trading*
- **Kaufman** = Kaufman, *Trading Systems and Methods*

Organized by family: **Trend** → **Momentum/Oscillator** → **Volatility** → **Volume/Breadth** → **Adaptive** → **Statistical, Cycle & Quantitative Methods**. Within each family, indicators covered by multiple books are presented once with each book's treatment attributed separately; single-source indicators carry one attributed treatment.

**Preservation policy (per project rules):** All "formula not recoverable from PDF extraction," "embedded-graphic gap," and "reconstructed from the standard published form" flags are preserved exactly as they appear in the source extractions. No formula, parameter, or claim below is invented — everything traces to a source file named in each entry. See `14_backtesting_and_validation.md` for testing/optimization methodology that uses these indicators as examples, and `16_research_hypotheses.md` (sibling file, written separately) for any downstream research use.

**Coverage-weight note:** Kaufman's *Indicators.md* (~569 lines, all 24 chapters) is overwhelmingly the largest and most technically detailed source and dominates this file's volume, as expected given the task brief. Pardo and Vince are explicitly thin (both books are about testing/money-management methodology, not indicator theory) — their entries are short by design, not by omission. Chan and Hilpisch sit in between: both use indicators instrumentally (as inputs to statistical-arbitrage or ML strategies) rather than surveying them broadly.

---

# I. TREND INDICATORS

## Simple Moving Average (SMA) — multi-book

### Pardo's treatment (Ch. 7, Ch. 9, Ch. 10, Ch. 13)
- **Definition:** Arithmetic mean of closing (or other) prices over a specified lookback period.
- **Purpose:** Trend identification; crossover of a fast and slow MA used as the book's primary running example of a trend-following entry/exit signal.
- **Calculation:** `MA1 = [C(t) + C(t+1) + ... + C(t+X−1)] / X` where C(t) is the close on day t (t=1 = present day) and X is the MA length (Ch. 7). An illustrative C-language implementation (`SMA()` function, Ch. 7): loop over `period` days summing `get_price_data(type, day-i)`, divide by `period`.
- **Parameters:** Length (period); price field (close, open, high, low, median — Ch. 10 notes testing showed price-field choice made little practical difference for the illustrated MA2 system, so it was fixed rather than optimized).
- **Recommended Settings:** None prescribed generically; illustrated variously as 10/30-day (Ch. 7), 3–15-day and 10–100-day ranges in optimization examples (Ch. 9/13), 5/20-day (Ch. 8's weaker example test), 1–10/15–60-day scan ranges (Ch. 10).
- **Strengths:** Simple, transparent, easy to script/verify — explicitly why the book uses it as its default teaching example.
- **Weaknesses:** Consumes degrees of freedom proportional to its length (a longer MA "costs" more of the sample); creates start-up overhead equal to its length before the first valid signal can occur (Ch. 6/13); a bare 5×20 MA crossover tested "questionable" (inconsistent, occasionally strongly negative) results in the book's own Ch. 8 multimarket example.
- **Best/Poor Conditions:** Not explicitly analyzed for MA specifically; the book's general market-type discussion (Ch. 6) implies trend-following approaches (which MA crossovers exemplify) do best in bull/bear trending markets, worst in congested markets.
- **Combinations:** Two MAs combined via crossover is the book's standard illustration; also shown combined with volatility bands and a 2-day time filter (Ch. 8, Ch. 13) as illustrations of adding filters/confirmation.
- **Common Mistakes:** Scanning a long-period MA at too fine a step size (overscanning, Ch. 10/13); adding a second/third MA plus volatility bands purely to chase higher in-sample profit without out-of-sample validation (the Ch. 13 overfitting parable — see `14_backtesting_and_validation.md`).
- **Examples:** See Pardo `Strategies.md` entry #3 (MA2 / EOTS-MA).

### Hilpisch's treatment (Ch. 4, Ch. 6)
- **Calculation:** `data['SMA'] = data['price'].rolling(N).mean()` (pandas `.rolling()` window function).
- **Parameters:** Window length `N`. Book examples: 42 & 252 days (classic "medium/long" pairing, ~2 months / ~1 year of trading days); 25 days (GDX mean reversion); 43 days (GLD mean reversion); 30 & 100 hourly bars (FXCM EUR/USD); 5 & 10 ticks (Ch. 7 streaming demo).
- **Recommended Settings:** Not prescriptively stated beyond the examples used; brute-force grid search shown once (Ch. 4) with an explicit overfitting caveat attached.
- **Strengths:** Trivial to compute (`.rolling().mean()`); crossover logic reduces to a one-line vectorized `np.where()` comparison; cites Brock, Lakonishok & LeBaron (1992) finding that MA rules "help to predict stock changes" (cited, not independently re-verified by the author beyond illustrative backtests).
- **Weaknesses:** Lagging by construction; the vectorized crossover strategy is "always fully invested" with no neutral state, so it cannot avoid whipsaws in range-bound markets (implied, not explicitly flagged).
- **Combinations:** Used as (a) sole crossover-signal engine (SMA1 vs SMA2), and (b) "trend proxy" for mean-reversion (`distance = price - SMA`, single SMA + threshold).
- **Common Mistakes:** Overly tight brute-force-optimized SMA windows risk overfitting to the backtest period (explicit Ch. 4 "Data Snooping and Overfitting" warning).
- **Examples:** EUR/USD 42/252-day SMA (Ch. 4); GDX 25-day SMA + 3.5 threshold (Ch. 4 mean reversion); GLD 43-day SMA + 7.5 threshold; AAPL.O 42/252-day event-based (Ch. 6).

### Kaufman's treatment (Ch. 2, Ch. 7 — "truncated moving average")
- **Definition:** Arithmetic mean of most recent n prices.
- **Weakness:** Abrupt value change ("drop-off effect") when an important old value exits the window, especially with small n. Drop-off impact = (new incoming price − oldest outgoing price) / n.
- **Related constructions in the same chapter:** Average-Modified/Average-Off Method (substitutes the previous average itself for the oldest raw price — smoother, dampens drop-off, needs only the last average stored); Weighted Moving Average (WMA, arbitrary per-lag weights); front-loaded WMA; step-weighting; percentage-relationship weighting (each older weight = a × next-more-recent weight, e.g. a=0.90, "similar in effect to exponential smoothing"); Group Weighting (shared weights across pairs/groups); Triangular Weighting (peaks at window midpoint, odd window length recommended, e.g. 21-day peaks at day 11 — often used for cycle analysis); Gaussian Filter (bell-curve weighting, formula an embedded-graphic gap); Pivot-Point Moving Average (reverse linear weights turning negative in the tail — reduces lag but can reverse rather than discount old data, best suited to longer-term cyclic markets); Standard Deviation Moving Average (`SD=StdDev(close,30); SDV=(SD−SD[1])/SD; StdAvg=Average(close,15)+0.05×SDV`); Moving Median (ignores extremes, "goes sideways" through sharp turns, slower — requires sorting); Geometric Moving Average (`GA = average(ln(price), n)`, best for long-term wide-range data); Accumulative Average (long-run average of all data, impractical for trend-following — overly dependent on start date); Reset Accumulative Average (resets on new trend/event/calendar interval).
- **Source:** Kaufman `Indicators.md` Ch. 2 / Ch. 7.

**Cross-book note:** All three books agree the SMA is simple, lagging, and consumes degrees of freedom / sample length proportional to its window. Pardo and Hilpisch both flag overfitting risk from brute-force/fine-grained window optimization specifically for the SMA parameter (see `14_backtesting_and_validation.md` for the general degrees-of-freedom and overfitting framework). Kaufman is alone in cataloguing the wide family of weighting variants (WMA, triangular, Gaussian, pivot-point, geometric, accumulative).

---

## Exponential Smoothing / EMA family (Kaufman Ch. 7, Ch. 17)
- **Definition:** `Eₜ = Eₜ₋₁ + sc×(pₜ − Eₜ₋₁)`, 0≤sc≤1, initialized E₁=p₁. Equivalent to moving the trendline sc% of the distance from the prior trendline value toward the current price.
- **Hutson day-to-smoothing-constant conversion:** sc = 2/(n+1). **Explicit warning:** this does NOT give a true lag-equivalent MA/EMA pairing — a 10% smoothing constant is actually slower than a 10-day MA; 5% is slower than a 20-day MA.
- **Higher-order variants:** 2nd-/3rd-order exponential smoothing (exponential analogue of step-weighting); Residual Impact (RI) formula approximates the smoothing constant for a target % of never-fully-discarded weight (sc=2/(n+1) corresponds to a consistent ~13–14% RI regardless of n; exact RI-to-sc formula is an embedded-graphic gap).
- **Double Smoothing:** Smoothing the trend values themselves (MA of an MA, or EMA of an EMA). A double-smoothed 3-day MA concentrates weight on center values (≈ triangular weighting shape); exponential double smoothing at nominal sc behaves closer to sc² (e.g., nominal 0.20 behaves like ≈0.031). Error correction: adding the smoothed forecast-error series back to a single-smoothed trendline centers the trendline within the price move — "a good candidate for mean reversion trading."
- **Blau's Double Smoothing of Price Changes:** substitutes price changes (momentum, Δp) for price before the first smoothing pass; the first pass then has effectively no lag, so the compounded 2-pass lag equals only one ordinary MA's worth of lag. Typical parameterization: first-pass period as long as 250 days, second-pass as short as 5 days (e.g., 5-day momentum → 1st smoothing at 5-day-equivalent sc → 2nd smoothing at 20-day-equivalent sc=0.0555). Signal off trendline direction changes only. Basis for TRIX (Ch. 8) and Double Smoothing (Ch. 9).
- **Exponential Regularization (Mills):** alternative double-smoothing form with smoothing constant a and weighting factor w, nominally a=w=9; smoother than plain exponential smoothing of the same nominal period but with more lag (exact combining formula an embedded-graphic gap).
- **Hull Moving Average (HMA):** double-smoothed WMA-based method combining weighted averages over period p, √p, and p/2 to cut net lag. **Reconstructed from the well-known published formula** (the book's own inline equation didn't extract cleanly, but its stated components match): `HMA = WAVG( 2×WAVG(close, INT(p/2)) − WAVG(close, p), INT(SQRT(p)) )`. Example period p=16 weeks; compared similar in speed to a 20-week EMA followed by a 5-week EMA (traditional double smoothing), both markedly slower than a double-smoothed 16-week simple MA.
- **Source:** Kaufman `Indicators.md` Ch. 7.

---

## Trend Channels, Bands, and Named Trend Indicators (Kaufman Ch. 4, Ch. 8)

- **Programmed Channel Breakout Bands (regression-based):** Computable version of the visual trend channel. (1) linear regression of closing price (Y) against a sequential bar index (X, not calendar date) → slope a, intercept b, ŷ = a·X + b; (2) residual per bar = actual close − ŷ; (3) Rmax = largest residual, Rmin = smallest (most negative); (4) upper band = ŷ + Rmax, lower band = ŷ + Rmin; (5) project both bands one period ahead using slope a. Parameters: regression window length; close-vs-low/high test choice (close = more conservative/later). Near-zero slope ≈ sideways channel. Basis for the Programmed Channel Breakout strategy and its countertrend scale-in variant.
- **Moving Channel (M/R construction):** Midpoint M = n-day MA of typical price (avg of H/L/C); Range R = n-day MA of daily true range; bands = M ± ½R. Next-day forecast projects M's path forward, scales projected range by multiplier f (exact projection arithmetic is an embedded-graphic gap). Alternative (footnote 12): forecast via regression slope, band width = stdev of price changes × scaling factor.
- **Keltner Channel** (Keltner, 1960): earliest cited volatility-band construction around a trendline; exact formula an embedded-graphic gap; author recommends substituting true range for the high-low range.
- **Percentage Band:** trendline ± fixed % of price (e.g. 3%); cannot be used on back-adjusted futures (percentages meaningless on shifted price levels); avoid fixed-dollar bands (mis-scale across price levels).
- **Volatility Band (generic scaled-band family):** band width = scaling factor s × a volatility measure (ATR, stdev, or % of price/trendline); MA/EMA/regression substitutable as center line. Empirical shape ranking (S&P, scaling factor 2 for all): % of trendline ≈ % of price (widest, smoothest) > 2×ATR > stdev-based (narrowest, most volatility-reactive). *See also Pardo's Volatility Bands entry below (Volatility family) — a distinct, thinner treatment used as a cautionary overfitting example.*
- **10-Day Moving Average Rule** (Keltner, 1960): 10-day MA of (H+L+C)/3 with a band = 10-day MA of the high-low range (≈10-day ATR); always-reversing breakout system.
- **Crossover Price (CP2)** (Solodukhin): the future price level at which two moving averages (periods m, n) would cross, recalculated daily and converging as price approaches it; formula an embedded-graphic gap.
- **Market Direction Indicator (MDI)** (Lambert, 1983): built from the change in the projected crossover price (CP2); buy when MDI crosses zero upward, sell downward; formula an embedded-graphic gap.
- **Ehlers' Early Onset Trend indicator** (2014): rescale a bounded oscillator (RSI, stochastic) to [-1,+1]; apply Ehlers' "roofing filter" to remove spectral dilation; apply automatic gain control (AGC) to renormalize without disturbing pattern shape. Underlying transform math not given in extractable text.
- **Ichimoku Cloud** (Hosada, developed 1930s, published 1969): five-line system — Tenkan-sen (9-day (H+L)/2 avg), Kijun-sen (26-day (H+L)/2 avg), Senkou A ((Tenkan+Kijun)/2, plotted 26 periods forward), Senkou B (52-day (H+L)/2 avg, plotted 26 periods forward), Chikou (close plotted 26 days back). Senkou A/B form the projected "cloud" (green=rising, red=falling), used as a long-term trend filter; Tenkan/Kijun crossover used for shorter-term timing within the cloud's direction.
- **Source:** Kaufman `Indicators.md` Ch. 4, Ch. 8.

---

## Directional Movement / ADX System (Wilder, 1980) — Kaufman Ch. 9, Ch. 23
- **PDM (Plus DM)** = today's high − yesterday's high; **MDM (Minus DM)** = yesterday's low − today's low. Daily DM = whichever is larger (other set to 0; both 0 on an inside day). TR1 = today's true range.
- **PDM14/TR14, MDM14/TR14:** after an initial 14-day sum, each successive value updates via Wilder's "average-off" running-total technique; equivalent smoothing constant ≈0.133 (exact recursive notation an embedded-graphic gap).
- **PDI14 = 100×(PDM14/TR14); MDI14 = 100×(MDM14/TR14)** — reconstructed standard Wilder form, consistent with the chapter's stated 0-100 normalization.
- **DX = 100×|PDI14−MDI14|/(PDI14+MDI14)** — reconstructed standard Wilder DX formula.
- **ADX** = DX smoothed with the same ≈0.133 (14-day-equivalent) constant.
- **ADXR (ADX Rating) = (ADX_today + ADX_14-days-ago) / 2** — variance-reducing adjustment.
- **Directional Parabolic System (DPS)** = SAR mechanic used only as an exit (ATR length 3, ATR factor 1.5 initialization; AF starts 0.02, capped 0.20). PDM/MDM exact inequality conditions **reconstructed from the standard published Wilder DM formula** (not verbatim), flagged as such.
- **Ruggiero's ADX trending/consolidating rules:** ADX crossing above 25 → trending; below 20 → consolidating; below 45 after being higher → consolidating; rising above 10 on 3-of-4 days after being lower → trend starting (in effect until 5-day ADX difference < 0). Additional levels: >40 strong trend, >50 extremely strong, >70 "power" trend.
- **Commodity Selection Index (CSI)** = `[ADXR × ATR14 × K] / (Margin × Commission)` — **reconstructed shape** from the chapter's own prose description; K = big-point-value conversion factor (equities: K=1, "Margin" = equity investment). Precompute the bracketed constant term once; rank/allocate a portfolio by highest daily/weekly CSI.
- **Oscillator Method with ADX Filter** (Lars Kestner, 2003): 10-day/50-day MA-difference oscillator gated by an ADX no-trend filter; exact inequality thresholds an embedded-graphic gap.

---

## TRIX (Triple Exponential Smoothing) (Hutson, 1983) — Kaufman Ch. 8, Ch. 9
- **Definition:** ln(price) smoothed exponentially three times with the same smoothing constant (recommended equivalent ≈6 days, sc=2/(n+1)); buy on 2 consecutive up days of the triple-smoothed line, sell on 2 consecutive down days. A 3-day-MA "signal line" variant prefigures MACD's construction. Common variant substitutes a percentage-change final step for the log.
- **Blau's TRIX variant:** (optional) ln(close) → 3 successive exponential smoothings (same constant each stage, p/q/r periods) → 1-period (or s-period) difference of the triple-smoothed line → optional ×10,000 scaling. Smoother but slightly more lag than TSI (difference taken at the end rather than the start).

---

# II. MOMENTUM / OSCILLATOR INDICATORS

## Momentum / Rate of Change — multi-book

### Pardo's treatment (informal, Ch. 3 "Momentum Surge Strategy")
- Not formally defined; "a bigger-than-usual momentum surge" relative to the 3-day average daily range. Entry triggers stated as percentages of the 3-day average daily range from the previous close (55% for longs, 75% for shorts) — no separate "momentum indicator" formula given; the trigger IS effectively a range-breakout expressed as a percentage of recent volatility. See Pardo `Strategies.md` entry #2.

### Kaufman's treatment (Ch. 7, Ch. 9, Ch. 19)
- **Basic Momentum (M):** `M(n)_t = p_t − p_[t-n]`. Positive → uptrend, negative → downtrend. Author notes true ROC should normalize by n (change per unit time), distinguishing it from raw momentum, though terms are often used interchangeably. Explicit heuristic: "the simplest method can often be the most robust" — benchmark more complex trend tools against plain momentum. Not the same as volatility (can be zero while range/volatility is high).
- **Percentage form (stocks):** `%M(n) = (p_t − p_[t-n])/p_[t-n]` — **NOT valid on back-adjusted futures/split-adjusted stock data** (use price differences instead there).
- **Momentum as price-minus-trend ("relative strength"):** price minus its own MA value; smaller range and less apparent lag than standard n-day momentum since the MA itself already lags. Not to be confused with Wilder's RSI.
- **ROC — KST convention** (reconstructed from the standard published percent rate-of-change definition, not verbatim from the source's embedded-graphic notation): `ROC = [(Close_t / Close_(t-n)) − 1] × 100`. The source distinguishes this from the calculus-style "true" rate-of-change (a slope/derivative).
- **Velocity & Acceleration:** velocity = 1st difference of price (or derivative dp/dt); acceleration = 2nd difference (or d²p/dt²). Only 2nd-order-or-higher trend equations (e.g., curvilinear) have nonzero/changing acceleration; straight lines, simple/weighted MAs, and exponential smoothing all have constant velocity (zero acceleration). Sideways-market detection requires BOTH velocity and acceleration to be small.

### Hilpisch's treatment (Ch. 5, Ch. 8, Ch. 10 — "Time Series Momentum")
- **Definition:** `momentum_signal = sign(returns.rolling(N).mean())` — direction implied by the average of the last N periods' returns. Cites Moskowitz et al. (2012) for the persistence hypothesis (cited, not independently proven).
- **Parameters:** Lookback window N — tested N=1 (badly underperforms), N=2,3 (gold, divergent results), up to N=9 (intraday AAPL/S&P500), N=6 (Oanda live), N=60 (event-based AAPL).
- **Weaknesses:** **Highly sensitive to N** — 2-day vs 3-day windows on the same gold data produce very different, non-monotonic performance. Extremely transaction-cost sensitive at short lookback windows due to high trade frequency: the book's clearest before/after-costs reversal example is gold N=3, +$7,395 gross outperformance → **−$2,653 net loss** with just 0.1% costs.
- **Combinations:** Embedded as the `mom` feature in the Ch. 10 6-feature ML set (mom/sma/min/max/vol/return).
- **Examples:** Gold (XAU=) 1/2/3-day windows; AAPL/S&P500 1/3/5/7/9-period intraday; Oanda EUR_USD 15/30/60/120-minute; live `MomentumTrader`/`MLTrader` real-time momentum feature (5s/10s bars).

**Cross-book note:** Kaufman and Hilpisch converge on treating naive short-window momentum as fragile — Kaufman via the general velocity/acceleration/noise framework, Hilpisch via a direct, quantified gross-vs-net cost demonstration. Both flag that raw momentum is not itself a volatility measure.

---

## RSI (Relative Strength Index) — multi-book

### Kaufman's treatment (Ch. 9, full definition; Wilder, 1978)
- **Calculation:** `RSI = 100 − 100/(1+RS)`, `RS = AU/AD` (14-day sums of up/down closes, updated via the average-off method).
- **Thresholds:** 30/70 standard; shorter periods (10) pair with wider zones (80/20). Wilder's top/bottom formation = "failure swing."
- **2-day RSI variant** (Stokes/MarketSci): apply RSI to 2-day-overlapping price differences instead of 1-day; more volatile/smoother; thresholds 10/90, exit 1 day later; scaling-in table (RSI<5→100% position ... RSI<20→25%) mirrored on both sides.
- **Net Momentum Oscillator** (Chande & Kroll, 1994): AU − AD (difference, not ratio) — recovers extremes RSI's smoothing removes.
- **LBR/RSI™** (Raschke and Conners, Ch. 16): a 3-day RSI applied to a 1-day rate of change (rather than raw price) — the ROC pre-transform makes the series more sensitive, reducing standard RSI's usual lag. Used in the Momentum Pinball system.
- **Adaptive RSI** (Ch. 17): RSI rescaled to a 0-1 smoothing constant via the Adaptive Momentum Transformation table (below), driving a KAMA-style adaptive trend.
- **Inverse Fisher Transform** (Ehlers, Ch. 11) wraps around RSI: TradeStation EasyLanguage `series = close - close[mom]; x1 = 0.1*(RSI(series,RSIper)-50); x2 = WAVERAGE(x1,waper); invfisher = 100*(EXPVALUE(2*x2)-1.0)/(EXPVALUE(2*x2)+1);` — produces a bipolar distribution clustering near ±1. Numeric defaults for mom/RSIper/waper not given (gap).
- **Dynamic Momentum Index (DMI, Chande/Kroll)** — distinct from Wilder's Directional Movement Indicator: variable-length RSI whose period lengthens as volatility falls, shortens as volatility rises, centered on pivotal period P (nominally 14). `DMIt = INT(P / Vt)`, where `Vt = σt(C,n) / [average σ over m days]`, n nominal 5, m nominal 10 (m=2n). At Vt=1, DMI=P=14. **Ambiguity flagged verbatim in the source:** the text states DMI becomes "larger than 14" when volatility increases, which appears inconsistent with `DMIt=INT(P/Vt)` (which implies DMI should shrink as Vt rises) — preserved as stated rather than silently corrected; possibly an extraction artifact or inverted convention not recoverable from the extracted text.

### Pardo's treatment (Ch. 5, Ch. 8, Ch. 11)
- **Definition/Calculation:** Not mathematically defined in the source — the book does not give RSI's calculation formula, assuming reader familiarity.
- **Purpose:** Countertrend/overbought-oversold signal generation in the "RSIct"/"RSI CT" example systems; briefly used as a filter example in Ch. 5 ("RSI closes below 20"; "RSI was below 30 on the previous bar and is now above 30 and rising higher").
- **Parameters:** RSI period; OB level; OS level. In the Ch. 11 Walk-Forward Analysis worked example: RSI period scanned 2–50 step 2; OB level scanned 0–80 step 20; OS level scanned 0–80 step 20.
- **Strengths:** In Ch. 8's multimarket/multiperiod comparison test, "RSIct" produced consistently positive ("typical to good") results across nearly all market/period cells.
- **Examples:** See Pardo `Strategies.md` entry #4 (RSIct / RSI CT), including the full worked Ch. 11 Walk-Forward Analysis case study — see also `14_backtesting_and_validation.md` for the WFA methodology itself.

**Cross-book note:** Kaufman supplies the formula and mechanics Pardo's book deliberately omits (Pardo treats RSI purely as an example vehicle for testing/optimization methodology, not as a technical-analysis subject). Both books use RSI's OB/OS thresholds as tunable parameters subject to overfitting risk if scanned too finely (Pardo Ch. 11 WFA case study; Kaufman's general warning about hand-fit thresholds under MACD, below, applies analogously).

---

## MACD (Moving Average Convergence-Divergence) — Kaufman Ch. 9 (Gerald Appel)
- **Calculation:** MACD line = fastEMA − slowEMA (standard 12/26-day; worked example uses 20/40); signal line = 9-day EMA of MACD line (worked example: 0.10 smoothing constant); histogram = MACD − signal.
- **Trading rule:** Buy/sell on MACD crossing signal line; threshold-band refinement (e.g., ±2.00) requires MACD to first penetrate an extreme before a crossing counts.
- **Common Mistake (explicit):** hand-fit threshold levels risk overfitting — explicit warning in the source.
- **Related constructions:** Volume-Weighted MACD (VWMACD) — standard 12/26-day MACD with closes × volume, each MA normalized by average volume over the same period, 0.20-constant (~9-day) signal line, same crossover rule (Ch. 12). Triangular MACD (Ch. 11) — difference of two Triangular Moving Averages, one at half the period of the other (e.g. 20-10 on IBM; 252-126 on corn using a ~63-day quarterly-earnings period).

---

## CCI (Commodity Channel Index) — Kaufman Ch. 4 (Donald Lambert, 1980)
- **Definition:** A deviation-from-average oscillator (not commodity-specific despite the name, and only loosely a "channel"); best suited to mean-reversion trading rather than trend-following.
- **Calculation:** (1) typical price M = average of daily high/low/close; (2) ADP = n-day average of M; (3) AvgDev = n-day average absolute deviation of M from ADP (mean absolute deviation, not standard deviation); (4) CCI = (today's deviation of M from ADP) ÷ (a fraction of AvgDev) — the classic scaling constant (0.015 in the standard published formula) is referenced only as "a fraction of the average deviation" in extractable text; the exact constant is embedded as a graphic and not recoverable here (**flagged gap**).
- **Interpretation:** values move well outside a nominal ±100 "channel" band during strong trends.
- **Weaknesses (explicit, important):** during a strong sustained uptrend, price/CCI can remain "overbought" for weeks; naive overbought/oversold buy/sell rules on CCI will "give frequent small profits and an occasional very large loss" — an explicit risk-asymmetry warning against using CCI as a pure mean-reversion trigger in trending regimes.

---

## Stochastic Oscillator Family — Kaufman Ch. 9 (George Lane)
- **%K/%D/%D-slow:** `%K = 100×(Close−Min(Low,10))/(Max(High,10)−Min(Low,10))`; `%D` = 3-day avg of %K; `%D-slow` = 3-day avg of %D. No inherent smoothing lag in raw %K (unlike RSI/MACD).
- **Lane's pattern vocabulary:** Left/Right Crossover, Hinge, Warning, Extremes (7 consecutive closes at highs/lows), Setup (bear/bull), Failure.
- **Generalization principle (explicit):** any bounded/unbounded indicator can be converted to a %K-style stochastic by substituting it for the closing price in the standard formula.
- **%R Method (Larry Williams):** today's close position within the past-n high-low range, inverted vs. stochastic convention (stronger close → smaller %R); author suggests using 1.0−%R for intuitive reading.
- **Williams' 10-day raw stochastic / %R variant (Ch. 16):** numerator = Highest(High,10) − current close; explicitly noted to differ from the %R formula attributed to Holter's 2001 article — full normalized denominator/scaling is an embedded-graphic gap.
- **Double-Smoothed Stochastic (Blau):** Lane's raw-stochastic numerator and denominator each double-exponentially smoothed (r then s periods) before dividing.
- **Adaptive Stochastic (Ch. 17):** verbatim source pseudocode varies the stochastic lookback (`stochper`) using the same ER-driven fast/slow-end interpolation as KAMA, then smooths raw %K over 3 days. Available as `TSM Adaptive Stochastic`.
- **1-day raw stochastic (Ch. 14):** `(close − low)/(high − low)` — used by Ruggiero as a simple report-day overreaction gauge for Treasuries.

---

## Other Named Oscillators — Kaufman Ch. 9
- **Oscillator normalization principle:** divide raw momentum by its own rolling maximum (positive or negative) to bound it — self-adjusts to changing volatility/price level; the basis for essentially all named oscillators in this section.
- **Momentum-Volume (MV):** `MV = (close − close[n]) × average(volume,n)`. Percentage variant `%MV = average(volume,n)×(close−close[n])/close[n]`. True-range-scaled variant `TRMV = average(volume,n)×(close−close[n])/avgtruerange(p)`.
- **Money Flow** (Quong & Soudack, 1989): day is "up" if avg(H,L,C) > previous day's avg(H,L,C); each day's avg × volume = daily money flow; 14-day ratio → money ratio → Money Flow Index (ratio/index formula an embedded-graphic gap).
- **Herrick Payoff Index (HPI):** combines volume AND open interest via change in underlying contract value; unbounded (not 0-100). Full programming-notation formula recovered: `HP = BigPointValue*volume*((high-low)/2 - (high[1]-low[1])/2)*(1 + (((high-low)/2 - (high[1]-low[1])/2)/absvalue((high-low)/2 - (high[1]-low[1])/2))*2*(absvalue(opint-opint[1])/lowest(opint,2))); HPI = smoothedaverage(HP,19)`. Smoothing constant s=0.10 (~19 days); typically scaled down by ÷100,000 or more. Larger HPI values cluster ahead of price turning points.
- **Divergence Index (DI):** volatility-adjusted difference between two MAs (e.g., 10/40-day); band = k×stdev(DI), self-adjusting to volatility (unlike MACD's fixed threshold). Buy when DI < lower band and slow MA up-trending; sell when DI > upper band and slow MA down-trending; exit on DI crossing zero.
- **SwamiChart** (Ehlers & Way): heat-map visualization of momentum across multiple calculation periods simultaneously; no discrete trading signals — a development aid ("Swami Predict"/"Swami Volume," generalizable to RSI/stochastics).
- **Relative Vigor Index (RVI)** (Ehlers, 2002): basic form ≈ (close−open)/(high−low); final version uses 4-day symmetric (triangular) weighting of numerator/denominator separately, targeting a nominal n=10 price cycle and removing the 2-bar cycle. Exact weighting formula an embedded-graphic gap. Signal line used exactly like MACD's.
- **Awesome Oscillator (AO)** (Bill Williams): 5-day SMA of (H+L)/2 minus 34-day SMA of (H+L)/2. Buy signal = "saucer" (cross above zero, turn down, turn back up). "Twin Peaks" bullish-divergence variant while AO is below zero.
- **True Strength Index (TSI)** (William Blau, 1995): double-exponential-smooth the 1-day price differences (numerator) and their absolute values (denominator), each first over period r then over period s; TSI = Num/Denom. Much smoother than raw n-day momentum with only slight added lag. Improvement noted: substitute n-day differences for 1-day differences as TSI's input for further smoothing at small lag cost (e.g., "10-20-20 TSI").
- **Ultimate Oscillator** (Larry Williams, 1985): BP = close − true low; TR = true range; sum BP and TR separately over 7/14/28-day windows; scale 7-day ratio ×4, 14-day ×2, 28-day ×1 (implied weighting 7:3:1). Rules use 50%/30%/65%/70% thresholds with "right shoulder failure" top/bottom confirmation.
- **Cambridge Hook** (Elias Crim, 1985, Ch. 9): outside reversal day + RSI > 60% + rising volume AND open interest → high-probability downward trend reversal (mirror for upward). Stop placed above the hook day's high.

---

## Elder's Triple-Screen Tools — Kaufman Ch. 19
- **Weekly MACD Histogram Slope / 13-Week Exponential** (Screen 1 — major trend): slope of the weekly MACD histogram, roughly equivalent to a 13-week (1 calendar quarter) exponential smoothing. Trend up when this week's value exceeds last week's, down otherwise.
- **Force Index (Elder)** (Screen 2 — timing): daily price change × daily volume. Short-term signal via 2-day EMA (constant 0.667, buy low/sell high — mean-reversion use); long-term signal via 13-day EMA (constant 0.1428, buy/sell on zero-line crosses — trend use). Elder's Triple-Screen Screen-2 variant smoothed with a 2-day exponential (constant 0.333); buy when it falls below its own center line without breaking its recent multi-week low.
- **Elder-Ray (Bull Power / Bear Power):** separates bullish and bearish price movement into two component series.
- **Source (Force Index, also):** Ch. 12 — see Volume/Breadth family below.

---

# III. VOLATILITY INDICATORS

## True Range / Average True Range (ATR) — Kaufman Ch. 3, Ch. 20
- **True Range (TR):** greatest of three measures of a bar's trading range, accounting for gaps from the previous close. Excel form: `TRn = Max(Hn-Ln, Hn-Cn-1, Cn-1-Ln)`.
- **ATR:** the most popular daily volatility measure (Wilder's True Range, averaged); extendable to 2+ day spans by substituting C_(t-2) etc. and using the multi-day highest-high/lowest-low.
- **Five Practical Volatility Measures (Kaufman, Ch. 20):**
  1. Change in price over n days: `v_t = P_t − P_(t−n)`. Ignores intervening activity; always understates true volatility vs. high/low methods.
  2. Maximum price fluctuation over n days: `v_t = Max(High,n) − Min(Low,n)`. Corrects the two-point dependency; usable for stop-loss/profit-target sizing to the average holding period; ignores frequency of directional changes.
  3. **ATR** — see above; most popular.
  4. Sum of absolute price changes over n days: includes both frequency and magnitude; large/hard-to-use values; same summation used in the Efficiency Ratio's denominator (Ch. 1, see Adaptive family below).
  5. Annualized Volatility (AV) (**reconstructed from the standard published form**): `AV = σ(r) × √P`, σ(r) = stdev of returns over n periods, P = periods per year. Cannot be applied to back-adjusted futures or some split-adjusted stocks.
  - **Finding:** ATR and AV are the two most commonly used; ATR (uses highs/lows) is generally the first choice for short-term thresholds, AV (uses only closes) is better for risk comparison across markets/time.
- **Bookstaber's Ratio Volatility Measures:** close-to-close volatility (SD of closing-price ratios, said to follow a known statistical distribution — name is an embedded-graphic gap), high-low volatility, high-low-close volatility (combines all three) — exact inline formulas are embedded-graphic gaps; variable definitions (C_t, H_t, L_t, v_t) preserved.
- **Relative Volatility (RV) and Lagged Relative Volatility:** `RV = v(n)/v(m)`, short-period volatility ÷ longer "normal" period's measure, used to filter trades by relative (not absolute) volatility. Lagged version: the longer-period calculation is shifted to end before the shorter period begins (nonoverlapping windows) — fixes the "bulge" problem (a prolonged hump after a volatile event delays recognition of a second volatile event; same principle as the Bollinger "bulge" fix below).

## Daily Range / Average Daily Range (Pardo Ch. 5)
- **Definition:** High minus low of a given bar, averaged over N bars (e.g., 3-day average daily range) — Pardo's chosen simple volatility measure for worked risk-stop/trailing-stop/profit-target examples throughout Ch. 5.
- **Calculation:** `Daily Range = High − Low`; N-day average = simple average of the last N daily ranges.
- **Parameters:** Lookback length (3-day in most examples); multiplier percentage applied to the average range (e.g., 50% trailing stop, 150% profit target).
- **Strengths:** Explicitly preferred by Pardo over a fixed-dollar risk/stop amount because "it will adjust as volatility expands and contracts."
- **Examples:** See Pardo `Risk_Management.md` for the full worked dollar-vs-volatility risk-stop, trailing-stop, and profit-target examples from Ch. 5.

## Bollinger Bands — multi-book

### Kaufman's treatment (Ch. 8, Ch. 18)
- **Definition:** Fixed definition = 20-day MA ± 2 stdev of price changes over the same 20 days. Because prices aren't normal, "2 stdev" is only ~87% empirical confidence (vs. 95.4% under a true normal).
- **Squeeze variant:** trade the breakout after bands compress to some % (e.g., 50%) of their average width.
- **Modified Bollinger Bands** (McNicholl, 1998): fixes the standard bands' slow-to-narrow "bulge" after a volatility spike; center-line smoothing constant α=0.15 (≈20-day MA), band multiplier f=2.5 (vs. standard 2.0); exact combining formulas an embedded-graphic gap.
- **"Avoiding the Bulge" lag problem (Ch. 18):** rolling-window SD bands widen only after a volatility spike has already happened and narrow only slowly as high-volatility days age out. Proposed fix: lag the input data window itself (compute SD from data offset t-n to t-m rather than up to today), making the band responsive to genuinely new spikes.
- **As distribution measure (Ch. 18):** comparing two periods (e.g., 21-day vs. 65-day bands) reveals relative short-term vs. longer-term volatility (crossings of the shorter band by the longer band flag relative overbought/oversold conditions).
- **Adaptive Price Zone (APZ)** (Leibfarth, 2006): mean-reversion band; volatility measure = 5-day EMA of the 5-day EMA of (H−L) ("adaptive range"); bands touching the highs/lows as volatility rises flags a mean-reversion opportunity. Band-width formula is an embedded-graphic gap.

### Chan's treatment (Ch. 3, mean-reversion example)
- **Definition:** A moving average plus/minus a multiple of the moving standard deviation of price, used to define statistical "overbought"/"oversold" bands.
- **Purpose:** trigger mechanism for a mean-reversion strategy: enter when price crosses outside the bands, exit when price reverts back inside a tighter inner band.
- **Calculation:** MA of price ± k × moving stdev of price, k typically 2 for entry bands (illustrative ES example), tighter multiple (e.g., 1) for the exit band.
- **Weaknesses (explicit, cautionary):** in the book's own illustrative example, this exact strategy at 5-minute frequency had **Sharpe ≈ 3 pre-cost but Sharpe ≈ −3 post-cost** (1bp transaction cost) — used explicitly as a cautionary illustration of transaction-cost sensitivity at high rebalancing frequency, NOT as a strategy endorsement.
- **Examples:** ES (E-mini S&P 500 futures) 5-minute mean-reversion example.

**Cross-book note:** Kaufman and Chan agree Bollinger Bands are simple and well-known; Chan's contribution is a stark quantified illustration of how transaction costs alone can flip a high-frequency mean-reversion Bollinger strategy from strongly profitable to strongly unprofitable — directly relevant to the transaction-cost discussion in `14_backtesting_and_validation.md`.

## Volatility Bands (generic, around a moving average) — Pardo Ch. 13
- **Definition:** Not mathematically defined; bands set some distance (dollar or percentage) around a moving average, used as buy/sell trigger levels.
- **Purpose (explicit cautionary framing):** used in the Ch. 13 "overfit trading model" parable as one of the added parameters (buy volatility band, sell volatility band, each scanned 0–5% step 0.25%) that, combined with a second moving average, took an already-validated simple system's in-sample profit from $10,000 to $65,000 while causing it to **LOSE $15,000 out-of-sample** — presented specifically as a cautionary example of overparameterization/overscanning, not as a recommended indicator. No positive endorsement of volatility bands is given anywhere in the Pardo source. See `14_backtesting_and_validation.md` §"Five Causes of Overfitting."

## Historical / Annualized Volatility — Vince Ch. 5
- Full worked procedure for computing 20-day annualized historical volatility (log price-change standard deviation, annualized by multiplying by √(trading days/year)) — Japanese yen futures example (Vince `02_Chapter_5_Multiple_Simultaneous_Positions_Parametric.md`). Used exclusively as an INPUT PARAMETER to option pricing models (Black-Scholes, Black futures option model) for computing optimal f on options positions — **not** used as a trading/timing indicator (not used to signal entries based on volatility breakouts or regime filters).
- Vince also mentions (without developing as a trading tool) that some unnamed practitioners adjust a system's "biggest loss" input to optimal f based on current market volatility (Ch. 2, "Too Much Sensitivity to the Biggest Loss") — described as an approach OTHER traders use, which Vince explicitly cautions against relying on.

## Historic Volatility / Standard Deviation of Price Distribution — Kaufman Ch. 18
- **Standard rule:** average ± 1 SD contains ~68% of data, ±2 SD ~95%, ±3 SD ~99.7% (normally distributed data).
- **Key limitation flagged:** this normal-distribution framework breaks down for volatility itself (cannot go negative) — a ±2 SD band around average annualized volatility produced a negative lower bound in the SPY worked example, "which doesn't work." **Fix:** use an empirical frequency distribution (sort all historical values, read percentile thresholds) instead of assuming normality.

## VIX (CBOE Implied Volatility Index) — Kaufman Ch. 20
- Reflects implied volatility of S&P options; introduced 1993; futures valued at 1,000× the index price, constructed from forward 3-day S&P 500 volatilities (vs. the cash index's original OEX 8-put/call weighted-implied-volatility construction).
- **Calculation procedure:** select options across two consecutive 23-37-day expirations (N options total) → calculate/weight each option's variance → sum weighted variances per expiration → interpolate to a 30-day variance → √variance = volatility (SD) → VIX = volatility × 100. Worked example: VIX=16%, S&P=2000 → implies ±$92.37 (1 SD, 68% confidence) over the next 30 calendar days (21 trading days).
- **Historic Volatility (HV) contrasted with VIX:** HV rises/falls more slowly around price spikes (20-day rolling window dilutes/retains the spike's effect); VIX spikes and declines immediately with price. VIX is better for identifying spikes (like volume); HV is more practical for trading filters and position sizing.

## Value-at-Risk (VaR) — Hilpisch Ch. 10; Kaufman Ch. 23 (as risk measure, cross-ref)
- **Hilpisch's treatment: Definition:** maximum expected loss (currency amount) over a given time horizon at a given confidence level.
- **Calculation:** `scipy.stats.scoreatpercentile(equity * returns, percentile)` for percentiles [0.01, 0.1, 1, 2.5, 5, 10] → confidence levels [99.99%, 99.9%, 99%, 97.5%, 95%, 90%].
- **Parameters:** confidence level, time horizon (bar resampling frequency — 10-minute native vs. 1-hour resampled shown, demonstrating VaR scaling with horizon).
- **Weaknesses:** historical/empirical VaR (as computed here) reflects only the realized sample period and provides no forward guarantee — not explicitly caveated by the author in this section, though this is a generally understood limitation of empirical VaR.
- **Examples:** Ch. 10 EUR_USD 30x-leverage ML strategy risk analysis — this VaR calculation is not a standalone illustration but one stage of Hilpisch's full backtest→risk-analysis→Kelly-leverage→persistence→live-deployment AdaBoost pipeline; see `14_backtesting_and_validation.md` §12.6 for the complete pipeline this VaR figure was computed within (max drawdown 511.38 EUR, VaR ranging ~63–163 EUR across confidence levels at the native 10-minute horizon, rising at every confidence level when resampled to 1 hour).
- **Kaufman's Ch. 23 treatment** (3 forms of VaR, Sharpe/Sortino/Calmar/Ulcer/Drawdown ratios) is logged in full in `Risk_Management.md` per the source's own cross-reference note, to avoid duplicate maintenance.

## Maximum Drawdown / Drawdown Duration — multi-book (see also `14_backtesting_and_validation.md` for use as a validation/robustness statistic)

### Chan's treatment (Ch. 3, Example 3.5)
- **Definition:** Drawdown at time t = difference between the global maximum of the equity curve occurring on or before t and the current equity value. Maximum drawdown = difference between the global maximum and the global minimum occurring AFTER that maximum (chronological order required). High watermark = running global maximum equity. Maximum drawdown duration = longest time for the equity curve to recover from a loss back to a new high watermark.
- **Calculation (algorithmic, `calculateMaxDD.m`):**
```
For each time t (starting from t=2):
  highwatermark(t) = max(highwatermark(t-1), cumret(t))
  drawdown(t) = (1 + highwatermark(t)) / (1 + cumret(t)) - 1
  IF drawdown(t) == 0: drawdownduration(t) = 0
  ELSE: drawdownduration(t) = drawdownduration(t-1) + 1
maxDD = max(drawdown)
maxDDD = max(drawdownduration)
```
- **Weaknesses:** purely historical — cannot bound future worst-case losses; a short backtest history may simply not have sampled the worst possible drawdown yet (explicit example: pre-1987 backtests would have missed Black Monday's ~20.47% one-day S&P loss).
- **Combinations:** directly informs the fat-tail leverage cap (Ch. 6): `implied max leverage = (max tolerable one-period drawdown) / (historical worst one-period loss)`; the smaller of this and half-Kelly leverage should be used.
- **Examples:** IGE/SPY hedge: max DD ≈10.53%, max DD duration ≈497 trading days. S&P 500 historical worst one-day loss ≈20.47% (Black Monday, Oct 19, 1987).

### Hilpisch's treatment (Ch. 4, Ch. 10, Appendix)
- **Calculation:** `cummax = equity.cummax(); drawdown = cummax - equity; drawdown.max()`. Period: identify timestamps where `drawdown==0` (new highs), compute consecutive timedeltas, take the max.
- **Strengths:** simple, robust, standard; the exact vectorized recipe is reused identically across three different chapters/contexts.
- **Examples:** EUR/USD SMA strategy: max DD ≈17.8pp, longest DD period 596 days (Ch. 4). ML strategy at 30x leverage: max DD ≈511 EUR (~15% of 3,333 EUR equity), longest DD period ≈7.33 hours (Ch. 10). S&P 500 raw index (Appendix): max DD ≈579.65 points (≈19.78% relative), longest DD period 417 days.

**Cross-book note:** Chan and Hilpisch use structurally identical drawdown mechanics (running high-watermark, drop from peak). Chan links it explicitly to a leverage-sizing rule (fat-tail cap); Hilpisch treats it purely as a reporting statistic. Both flag the backward-looking limitation.

## Kase's DevStop — Kaufman Ch. 18, Ch. 23
- 3-level trailing stop = (2-day ATR) − (1.0 / 2.2 / 3.6 × 20-day SD of the ATR), subtracted from the close. Full 5-step worked procedure in Kaufman `Strategies.md`: True Range → rolling ATR/STDEV of a 2-day TR series → DDEV = ATR + multiplier×STDEV, multiplier 2.06-2.25 or 3.20-3.50 → stop = Trade High/Low ∓ DDEV.

## Other Distribution/Zone Volatility Tools — Kaufman Ch. 18
- **Jackson's Intraday Zones:** 6-level relative-strength classification of the next 10-minute bar vs. yesterday's daily H/L/C.
- **Chande & Kroll Volatility-Scaled Forecast Zones:** built from the 10-day MA of the absolute value of daily price changes; five zones (H2/H1/L1/L2 boundaries) scale in proportion to this volatility measure.
- **Scorpio's ATR-Based Daily Zones:** six zones built from the 10-day ATR relative to today's high/low/(H+L)/2.
- **Moving Skewness (McNicholl):** 4-step leading trend-change indicator from closing prices only: (1) double-smooth closes (constant a=0.10) to get moving mean M; (2) moving deviation of (close−M); (3) moving stdev of that deviation; (4) moving skewness G. Steps 1's constant is the only numeric parameter that survived extraction; steps 3-4 formulas/constants are embedded-graphic gaps. Large skewness spikes tend to coincide with (or shortly precede/follow) trend changes.
- **Excess Kurtosis and Skew as Trading Signals:** Excess kurtosis = 3 − kurtosis (3="normal"). Rising excess kurtosis = strong/persistent clustering near the mode; skew direction indicates which side the tail leans. Joint interpretation: both moving up = persistence with upside tail; opposite directions = downside tail; simultaneous sharp peaks in both = likely turning/critical point.
- **Steidlmayer's Market Profile / TPO Count:** frequency distribution of intraday price by time (Time/Price Opportunities, half-hour letter-coded intervals), not volume; value area = ~70% of TPO-weighted activity, centered at the modal TPO price. Jones' overlay: value area = range within ±2 SD of the TPO-count center.

---

# IV. VOLUME / BREADTH INDICATORS
**Source (all entries this section unless noted): Kaufman Ch. 12, Ch. 14.**

- **Average Volume:** simplest volume indicator; commonly 50-day for equities, or matched to whatever price-MA period is in use (e.g. 200-day). Periods under 50 days are unlikely to be smooth.
- **Normalized Volume:** volume as a % of its N-day average (N=50 or 200 typical), or rescaled 0-100 via a stochastic-style construction (formula gap).
- **Volume Momentum / Volume % Change:** momentum/ROC-style calculations applied to *average* volume (not raw, too erratic) over rolling period N with indicator period n.
- **Force Index** (Alex Elder): daily price change × daily volume; short-term signal via 2-day EMA (constant 0.667, mean-reversion use); long-term via 13-day EMA (constant 0.1428, trend use). (Cross-ref Elder Triple-Screen, Momentum family above.)
- **Volume Oscillator:** two-step smoothing of volume, e.g. 14- and 34-day periods. Method 1 = difference of short/long average volume (MACD-style); Method 2 = ratio of short/long summed volume.
- **On-Balance Volume (OBV)** (Joseph Granville): cumulative running total; add full day's volume on up-close days, subtract on down-close days (±1/0 sign-decision formula an embedded-graphic gap). Best used with a long-term MA trend overlay or directly substituted for price in a trend system; divergence from price is a key signal. Interest-rate markets showed improvement using OBV as a price substitute in the author's own testing.
- **Money Flow Index (MFI):** OBV variant using average of high/low/close instead of close alone; compared to RSI (formula gap).
- **Volume Count Indicator (VCI):** running total, +1 if today's volume > yesterday's, else −1.
- **Volume Accumulator (VA)** (Mark Chaiken): OBV refinement — assigns a proportional share of volume to buyers/sellers based on where the close falls within the day's high-low range (all volume at extremes, none at midrange), rather than OBV's all-or-nothing assignment (formula gap).
- **Accumulation Distribution** (Chaiken): compares close-vs-open strength, divided by the day's range ("money flow" in some references); previous close substitutes for open if unavailable (formula gap).
- **Intraday Intensity:** increases when the close sits nearer the day's high than its low (formula gap).
- **Alphier Expectation:** a variation on Intraday Intensity (credited by John Bollinger to Alphier; formula gap).
- **Price and Volume Trend (PVT):** applies volume to the daily percentage price change; NOT valid on back-adjusted futures (cash markets/stocks/indexes only). Positive Volume Index (PVI) and Negative Volume Index (NVI) are its two-series variants; trend found via 127-day (6-month) or 255-day (1-year) MA of the index. **Fosback (1941-1975 study):** PVI-up → 79% bull-market odds; PVI-down → 67% bear-market odds; NVI-up → 96% bull-market odds; NVI-down → only 50% bear-market odds (coin-flip).
- **Aspray's Demand Oscillator (DO)** (Thomas Aspray): nets separately-computed Buying Pressure/Selling Pressure series (branch formulas a gap); uses volatility scaling factor K = 3 × close ÷ (10-day MA of max 2-day H-L range), typically well over 100 (worked example: S&P 2000, 30-pt avg volatility → K=200).
- **Tick Volume Indicator (TVI)** (William Blau): RSI-style construction on tick volume with double-exponential smoothing of up/down ticks (r-bar then s-bar smoothing); range −100 to +100; formula gap.
- **Volume-Weighted MACD (VWMACD):** see Momentum family above.
- **Elastic Volume-Weighted Moving Average (eVWMA)** (Christian Fries): weighting factor from the relationship between outstanding shares (OS), price, and next-period volume — prior trend value weighted more heavily on low-volume days, less on high-volume days (formula gap; OS chosen slightly above observed max daily volume in the worked Merck example).
- **Open Interest as a Volume Substitute (Futures):** total open interest is more stable than volume and reflects the same underlying fundamentals — preferable substitute for volume in many of the above indicators specifically for futures markets (use *total* volume, not single-contract volume, for the same reason).
- **VWAP / TWAP:** execution benchmarks, not signal indicators — VWAP avoids price impact from large orders; TWAP uses equally-spaced orders ignoring liquidity.
- **Advance-Decline Index:** cumulative sum of daily net advancing-minus-declining stock counts (unchanged issues ignored) — the most basic breadth technique.
- **Sibbett's Demand Index** (James Sibbett): RSI-style ratio of summed upside volume to summed downside volume, neutral at 1.0; Sibbett used 10 days, Merrill suggested an alternate period (gap).
- **McClellan Oscillator:** MACD-style difference of two smoothed Net Advances (NA) trends, 19- and 39-day periods (converted to EMA smoothing constants; exact resulting constants a gap).
- **Bolton-Tremblay:** net-advancing-stocks-vs-unchanged-stocks ratio with geometric weighting; uses |BT| to avoid a negative square root; produces large spikes when the unchanged-stock denominator is small.
- **Schultz:** advancing stocks as % of total stocks traded, bounded 0-100 (formula gap).
- **Upside/Downside Ratio (UDR):** unsmoothed version of Sibbett's ratio — unbounded upside (e.g. 4.0 if declining volume is 20% of total), bounded downside (0-1). High values expected to precede a bull market.
- **Arms Index (TRIN)** (Richard Arms): (advancing/declining stock ratio) ÷ (advancing/declining volume ratio); countertrend reading (below 1.0 bullish, above bearish, neutral at 1.0); as a trend indicator, buy above 2.0, sell below 0.50.
- **Thrust Oscillator (TO)** (Tushar Chande): (adv. stocks × adv. volume − decl. stocks × decl. volume) ÷ sum of the two products; overbought/oversold bands ±30 (or ±40 for more selectivity); author's suggested refinement — express all inputs as percentages of totals before combining, to avoid low-relative-volume distortion.
- **High-Low Index (HLX) / High-Low Ratio (HLR):** functions of new 52-week highs (NH) and lows (NL) — HLX combines them directly (formula gap); HLR = NH ÷ (NH+NL) over n days, smoothed 10 days per Gerald Appel, buy above a 0.80-0.90 threshold, sell below.
- **Market Facilitation Index:** compares tick volume to price range to gauge the market's "willingness" to move price; 2×2 tick-volume/index-direction interpretation table (up/up = confirmation; down/down = false direction, no trade; down/up = poor entry timing; up/down = potential new trend/end of old trend). Source: Bill Williams, *Trading Chaos* (1995).
- **Richard Arms' Equivolume** (charting method, not a scalar indicator): substitutes volume for time on the x-axis — high-volume moves render as taller *and* wider boxes; algorithmic version assigns time-units proportional to volume/normal-volume ratio.
- **Briese COT Index (Ch. 14):** a stochastic-style ranking (structurally identical to a %K calculation) of a trader group's net long position (NL) within its own n-period (1.5-4 year) historical range, expressed as a bullish percentage (via Commodity Systems, Inc.). Formula an embedded-graphic gap.
- **Commitment of Traders Sentiment Index (Curtis Arnold method, Ch. 14):** stochastic-style ranking of Net (commercial net position minus combined large-speculator + small-trader net position) within its historic Max/Min range — a bullish measure premised on commercials being the "correct" directional group. Formula an embedded-graphic gap.
- **Bullish Consensus / Market Sentiment Index (Hadady, Ch. 14):** circulation-weighted poll of brokerage/advisor market letters, 0-100% bullishness scale; neutral level 55% (novice-trader bullish bias + long-term equity upward drift), normal range 30-80%. Not a scalar formula but a survey-construction methodology.
- **Put-Call Ratio (Ch. 14):** put option volume ÷ call option volume; >1.0 theoretically bearish, <1.0 bullish, though the author recommends tracking deviation from the ratio's own trendline/average rather than the absolute level.

---

# V. ADAPTIVE INDICATORS
**Source (all entries this section: Kaufman Ch. 1, Ch. 17, unless noted).**

## Efficiency Ratio (ER) / Fractal Efficiency — Ch. 1
- **Definition:** A measure of price "noise" (erratic movement) relative to net directional price change over n bars/days. Also called fractal efficiency.
- **Purpose:** distinguishes trend-favorable (low-noise) markets from mean-reversion/arbitrage-favorable (high-noise) markets. Explicitly **NOT** a volatility measure — the author stresses noise and volatility are distinct and must not be conflated.
- **Calculation:** ER = (net price change from point A to point B over n periods) ÷ (sum of the absolute values of each individual bar-to-bar price change over the same n periods). n = calculation period, chosen by the user. ER is always ≤1.
- **Interpretation:** ER near 1.0 = low noise (strongly trending); ER near 0 = high noise.
- **Worked example (Table 1.1, 8-day windows):** "High noise" case — net change 35, sum of absolute daily changes 595 → ER=0.06. "Low noise" case — net change 310, sum of absolute daily changes 554 (similar total movement) → ER=0.56. Lesson: absolute daily swing size alone does not determine noise; noise is only meaningful relative to the net move achieved.
- **Common Mistake:** confusing noise (ER) with volatility — a market can have large absolute price swings and still show high ER (low noise) if those swings are all part of a large net directional move.
- **Combinations:** forms the adaptive-speed input for KAMA (below).

## Price Density and Fractal Dimension (estimate) — Ch. 1
- **Price Density:** "the extent to which prices fill a box" drawn around the highest high and lowest low over an n-day period. **Calculation not explicitly recoverable — embedded equation graphic did not extract as readable text (flagged gap).** Structurally similar to fractal dimension per the book.
- **Fractal Dimension (estimate):** "cannot be measured exactly but can be estimated" over n days. Calculation partial: (1) Max = highest high over n days, (2) Min = lowest low over n days, (3) Range = Max−Min, (4-6) **equation graphics not recoverable from PDF text extraction — flagged gap.** Book states "a strong relationship between fractal dimension and the efficiency ratio."

## Kaufman's Adaptive Moving Average (KAMA) — Ch. 17
- **Source:** Kaufman, *Smarter Trading* (1995).
- **Definition:** an adaptive exponential smoothing (not a true moving average) whose smoothing constant is recalculated every period from the Efficiency Ratio (ER, above).
- **Calculation:** `KAMAt = KAMAt-1 + SC × (Ct − KAMAt-1)`, where `SC = [ER × (fastest SC − slowest SC) + slowest SC]²` **[core form reconstructed from the standard published KAMA formula, not verbatim from this source — the book's own inline SC-from-ER and fastest/slowest-SC equations are embedded-graphic gaps]**. Fastest/slowest bounds nominally correspond to 2- and 30-day, or 3- and 30-day, calculation periods.
- **Verbatim TradeStation code recovered from the source** (10-day ER version): `KAMA = KAMA[1] + ((absvalue(C-C[10])/summation(absvalue(C-C[1]),10)*0.6022) + 0.0645)*2*(C - KAMA[1])` (source shows "0.O645," almost certainly an OCR artifact for 0.0645).
- **Parameters:** n (ER lookback, small — 8-10 days typical, up to 35-60 for longer-term use), fast/slow SC bounds (nominally 2/30 or 3/30 days), fixed threshold F for the required whipsaw filter.
- **Recommended Settings:** leave the 30-day slow bound fixed; raise the fast bound above 2 (e.g. 3-4) to reduce sensitivity rather than changing the slow bound. Cited working example: 8-period ER with fixed filter of 0.017 on S&P futures.
- **Strengths:** adapts calculation speed to genuine noise/efficiency conditions (not just volatility); fewer whipsaws and higher win rate than VIDYA/Adaptive R² in the book's own comparative test.
- **Weaknesses:** the underlying exponential-smoothing form technically reverses on every price penetration, requiring a mandatory added whipsaw filter (fixed-move-away-from-extreme filter tested as the better of two options) to be tradeable; extreme slow-end behavior (~900-period equivalent) can effectively freeze the line for long stretches during high noise.
- **Best/Poor Conditions:** works across regimes by design, but underperformed on some individual markets in the 2000-2018 test (e.g. gold Profit Factor 0.90).
- **Common Mistakes:** conflating noise (ER) with volatility; omitting the whipsaw filter and trading the raw KAMA cross.

## Chande's VIDYA (Variable Index Dynamic Average) — Ch. 17
- **Source:** Tushar Chande, *TASC*, March 1992.
- **Calculation:** `VIDYAt = VIDYAt-1 + SC × (Ct − VIDYAt-1)`, where `SC = s × k`, s = fixed base smoothing constant (0.20, a 9-day equivalent), k = relative volatility = `stdev(C, n) / stdev(C, m)`, n=9, m=30 nominal (m>n). **[Book's own inline k-formula partially recovered; general structure preserved, exact combining notation flagged as noted in the chapter file.]**
- **Interpretation:** k>1 → current volatility exceeds historic volatility → larger SC → slower trend; k<1 → faster trend.
- **Recommended Settings:** apply stdev to price changes/returns, not raw prices, to avoid injecting trend bias into the volatility measure.
- **Weaknesses:** traded far more often than KAMA/MAMA in the book's comparative test (594 avg trades vs. KAMA's 134), diluting per-trade edge once costs are applied.

## Correlation Coefficient (r²) as an Adaptive Smoothing Constant — Ch. 17
- **Calculation:** r² from a linear regression of closing price against the sequence (1,2,3,...); used directly as SC in the same exponential-smoothing skeleton as KAMA/VIDYA.
- **Interpretation:** r² near 1 (strong linear trend fit) → fast trend; near 0 (no direction) → slow trend.
- **Weaknesses:** also underperformed KAMA/MAMA in the comparative test.

## Ehlers' MAMA / FAMA — Ch. 17
- **Definition:** MESA Adaptive Moving Average (MAMA) uses the phase rate of change of the dominant price cycle (360°/cycle length) as the driver of α in classic exponential smoothing (`Pt = α×Price + (1−α)×Pt-1` form); a Hilbert-Transform-like method computes the phase rate (cross-ref Cycle Analysis, Statistical family below).
- **Parameters:** α restricted to 0.05-0.50 (≈2- to 19-day MA equivalents) for MAMA.
- **FAMA:** applies the MAMA technique to the MAMA line itself (double smoothing) using α_FAMA = ½ × α_MAMA — produces a smoother signal line for crossover-based signals, analogous to MACD's signal line or %D in stochastics.
- **Strengths:** FAMA is the slowest/fewest-false-signals of six adaptive methods compared in Figure 17.5; MAMA is the fastest (~2x FAMA's speed).

## Ehlers' Fractal Adaptive Moving Average (FRAMA) — Ch. 17
- **Source:** Ehlers, *TASC* (Oct. 2005).
- **Definition:** adaptive trend keyed to the fractal dimension of price (self-similar "roughness" across time frames — the classic coastline-measurement analogy: a shorter measuring "ruler" reveals more jagged detail, yields a longer measured length).
- **Calculation:** fractal dimension estimated by covering the price pattern with N objects (boxes) of size s at two different scales; power-law relationship between object counts at different scales. **[Exact power-law formula and the worked 10-foot-line toy example's numeric result are embedded-graphic gaps — only the box-count setup (N1=10 at s=1ft, N2=100 at s=0.1ft) survived extraction; cross-reference the related but distinct Ch.1 Fractal Dimension entry above, which uses n-day high/low range rather than Ehlers' box-covering method.]**
- **Additional features (Companion Website version):** upper/lower bands, trailing stop, profit-taking rules.

## McGinley Dynamics (New McGinley Dynamic) — Ch. 17
- **Source:** John McGinley, *Technical Trends* newsletter.
- **Calculation [reconstructed from the standard published form, not verbatim from this source]:** `MDt = MDt-1 + (p − MDt-1) / (k × n × (p/MDt-1)⁴)`, k=0.60 (constant), n = selected MA period, p = closing price.

## Adaptive Momentum Transformations — Ch. 17
Rescaling any bounded indicator to a 0-1 smoothing constant:

| Momentum range | Transformation to SC |
|---|---|
| 0 to 1 | SC = M |
| −1 to +1 | SC = \|M\| |
| 0 to 100 | SC = M/100 |
| −100 to +100 | SC = \|M/100\| |

- **Purpose:** allows RSI or any other bounded oscillator to drive an adaptive exponential-smoothing trend using the same KAMA-style skeleton.
- **Worked example:** adaptive RSI vs. KAMA vs. 10-day MA on Eurodollar futures (Feb-Jul 2011) — adaptive RSI was most sensitive during sideways stretches; suggested correction is squaring SC (e.g. 0.75 → 0.56) to pull intermediate values toward a slower trend.

## Trend-Adjusted Oscillator (TAO) — Ch. 17
- **Source:** E. Marshall Wall, *Futures* (July 1996).
- **Definition:** shifts an oscillator's current reading by the amount its own moving average deviates from the oscillator's theoretical midpoint (50 for a 0-100 oscillator, 0 for a ±100 oscillator), correcting the tendency of oscillators to cluster in the lower half during downtrends / upper half during uptrends.
- **Worked example:** a 10-day oscillator whose 5-day MA reads 40 (10 below the 50 midpoint) has its current value raised by +10.
- **Weaknesses:** corrects sustained overbought/oversold bias but loses many smaller overbought/oversold signals; a scaling multiplier (source used ×3, suggests 4-5 could work better) may be needed to avoid the adjusted value hugging the midpoint too tightly.

## Ehlers' Instantaneous Trend (Adaptive Trend + Trigger) — Ch. 17
- **Source:** Ehlers, Traders.com (May 2000).
- **Definition:** pairs an adaptive trend line (AT) with a derived "Trigger" line, built on the Hilbert Transform.
- **Entry logic:** buy tomorrow at a limit when Trigger crosses above AT; sell short tomorrow at a limit when Trigger crosses below AT. **Exact AT/Trigger formulas and the specific limit-price reference are embedded-graphic gaps.**
- **Note:** despite the "trend" name, the source explicitly characterizes the resulting strategy behavior as **mean-reverting**.

## Meyers' Normalized Range Breakout Indicators (NHR / NLR) — Ch. 17
- **Source:** Dennis Meyers, *Active Trader* (March 2003).
- **Definition:** normalized high-range/low-range measures for intraday breakout detection, using the single bar's H/L exactly n bars back (not a rolling extreme) as the raw range, normalized by n-period ATR and by a power function n^a to make different lookback periods comparable (correcting for the range ratio's natural growth with n, following the √n price-volatility relationship).
- **Parameters:** n (lookback, suggested max 25), a (power exponent) — both optimized along with two threshold values.

## The Parabolic Time/Price SAR (Wilder, 1978) — Ch. 17
- **Calculation:** exponential smoothing of the high (long) or low (short) using the Acceleration Factor (AF) as the smoothing constant; AF starts at 0.02/trade, +0.02 on each new profit extreme, capped at 0.20 (9-day-MA equivalent; 0.02 ≈ 99-day-MA equivalent).
- **Noise floor/ceiling:** SAR may never be closer than the most recent 2-day high/low range to price.
- Cross-listed here as the book's first adaptive smoothing-constant technique; full rule set in Kaufman `Strategies.md`.

## N-Day Breakout Adaptive Period (Seidel and Ginsberg volatility ratio) — Ch. 5
- **Source:** Andrew D. Seidel and Philip M. Ginsberg, 1983.
- **Definition:** an adaptive lookback period N for a breakout system, shrinking as current volatility rises relative to "normal" (longer-period) historical volatility. Exact formula embedded as a graphic in the source, not recoverable as clean text (flagged gap); inverse relationship (higher current-vs-normal volatility ratio → smaller N) is explicit.

## Volatility Factor (VF) — Ch. 24
- `VF = Target Volatility / Actual (measured) Volatility.` Used to rescale position sizes toward a stated target annualized volatility; applied only when it differs from the currently-in-force VF by ≥20% (a switching-cost-reducing threshold rule), not on every daily fluctuation. Full worked example (8.7% → 14.3% AROR at equal risk, macrotrend world-futures portfolio, 1989-2018) in `Risk_Management.md`'s Ch. 24 section and Kaufman `Strategies.md`'s "Volatility Stabilization Procedure."

---

# VI. STATISTICAL, CYCLE & QUANTITATIVE METHODS

## Sharpe Ratio (and Information Ratio) — Chan Ch. 2/3/6
- **Definition:** A risk-adjusted performance measure. Information ratio = Average(Excess Returns) / StdDev(Excess Returns), Excess Returns = Portfolio Returns − Benchmark Returns. Sharpe ratio = the special case where the benchmark is the risk-free rate, appropriate for dollar-neutral strategies; in practice most traders use "Sharpe ratio" terminology even for directional strategies.
- **Calculation:** `Sharpe = √NT × Average(Excess Returns over period T) / StdDev(Excess Returns over period T)`, NT = number of periods T in a year (annualization factor).
- **Rules of thumb (Ch. 2):** Sharpe < 1 → not suitable as a standalone strategy. Profitable almost every month → annualized Sharpe typically > 2. Profitable almost every day → annualized Sharpe typically > 3.
- **Common mistakes (explicit):**
  - Do **NOT** subtract the risk-free rate when computing excess returns for a dollar-neutral, self-financing strategy (financing cost is negligible; margin balance earns credit interest ≈ risk-free rate, cancels algebraically) — similarly not needed for long-only day-trading strategies with no overnight financing cost. Subtract risk-free rate ONLY when the strategy genuinely incurs financing cost.
  - **Common annualization mistake:** for an intraday hourly strategy, NT should be (trading days/year) × (trading hours/day) = 252×6.5=1,638, **NOT** 252×24=6,048.
  - Assumes returns are serially uncorrelated for the √NT annualization scaling to be valid (per Sharpe, 1994).
  - Does not by itself capture drawdown depth/duration or tail risk (fat tails) — must be paired with drawdown analysis and separate fat-tail-aware risk limits.
- **Best/Poor Conditions:** least informative in isolation for strategies with few trades/year (small sample noise; Ch. 2 explicitly notes low-trade-frequency strategies are unlikely to show high Sharpe even if genuinely sound).
- **Institutional-bias anecdote (Chan Ch.2)**: Chan recounts pitching a strategy to SAC Capital Advisors (AUM $14 billion); their head of risk management dismissed a high Sharpe ratio in favor of higher absolute returns ("we can all go buy bigger houses with our bonuses!"). Chan calls this reasoning "quite wrong," since a higher Sharpe ratio permits higher leverage, and it is the **leveraged** return that ultimately matters (formalized via g=r+S²/2, below) — a vivid, concrete illustration of the book's single most-repeated point (Sharpe over raw return drives long-term growth). The SAC pitch was unsuccessful, for unrelated reasons.
- **Information Ratio benchmark-selection guidance (Chan Ch.2)**: the benchmark used in the excess-returns calculation should match the traded universe — e.g., Russell 2000 or S&P SmallCap for a small-cap stock strategy, the gold spot price for a gold-futures strategy — **"not always S&P 500."**
- **Combinations:** feeds the Kelly formula (fᵢ=mᵢ/sᵢ²) and the maximum-growth-rate formula (g=r+S²/2, at Kelly-optimal leverage).
- **Examples:** Buy-and-hold IGE (Nov 2001–Nov 2007): Sharpe≈0.7893. Long IGE/short SPY hedge: Sharpe≈0.7837. GLD/GDX pair trade: training-set Sharpe 2.3–2.9, test-set Sharpe 1.5–2.1 depending on threshold tuning. S&P 500 cross-sectional mean-reversal (Khandani-Lo replication): 0.25 (pre-cost, close-based) / −3.19 (post-cost, close-based) / 4.43 (pre-cost, open-based) / 0.78 (post-cost, open-based).
- **Kaufman's cross-reference (Ch. 23):** Sharpe alongside Information/Geometric/Treynor/Palagi/Sortino/Calmar ratios, Ulcer Index, Drawdown Ratio, and 3 forms of VaR are logged in full in `Risk_Management.md` per Kaufman's own cross-reference (avoiding duplicate maintenance).

## Kelly Formula (Kelly Criterion) — Chan Ch. 6 (see also Vince, whole-book treatment in `Risk_Management.md`)
- **Definition:** A capital-allocation/leverage-sizing formula that maximizes long-term compounded wealth growth, derived under a Gaussian return-distribution assumption. Single-strategy form: `f = m/s²`. Multi-strategy form: `F* = C⁻¹M`.
- **Calculation:** single-asset SPY example: `f = 0.07231/0.16912² ...` note — actual worked value in the source text is `f=0.07231/0.16912=2.528`, treating 0.16912 as effectively s² in the specific units used, **reproduced exactly as given in the source**. Multi-strategy: `F* = C⁻¹M`; portfolio growth rate `g(F*) = r + F*ᵀCF*/2`; portfolio Sharpe `S = √(F*ᵀCF*)`.
- **Recommended Settings:** **"Half-Kelly" betting** is the standard practical convention (halving raw Kelly leverage) to compensate for parameter-estimation uncertainty and the falseness of the Gaussian assumption. Lookback period for parameter estimation: ~6 months for strategies holding positions ~1 day. Rebalancing cadence: at least once per trading day. **Leverage should further be capped at the SMALLER of half-Kelly and a fat-tail-implied maximum.**
- **Weaknesses:** relies on a Gaussian assumption that is empirically false (fat tails); full Kelly can be catastrophically oversized relative to real tail risk (half-Kelly leverage of 1.26 for SPY would NOT have survived Black Monday's ~20.47% one-day loss at only ~1x tolerable leverage). Requires continuous rebalancing (mechanically requires selling into losses). Sensitive to parameter estimation error.
- **Examples:** SPY: Kelly leverage 2.528, half-Kelly 1.264, compounded growth 13.14% (full Kelly) vs. 9.8% (unlevered). OIH/RKH/RTH three-ETF example: F*=[1.2919, 1.1723, −1.4882]ᵀ, portfolio g=15.29%, portfolio Sharpe=0.4751 (exceeds best single-asset achievable growth, OIH alone: 12.78%).
- **Vince's book-length treatment** (optimal f, fixed fractional trading, parametric optimal f on normal/other distributions, multi-asset optimal f, geometry of portfolios) is the primary source for Kelly-family position sizing and is logged in full in `Risk_Management.md` — not duplicated here since it is not indicator-signal content.

## Ornstein-Uhlenbeck (O-U) Half-Life of Mean Reversion — Chan Ch. 7
- **Definition:** stochastic-process model for mean-reverting series: `dz(t) = −θ(z(t) − μ)dt + dW`. Half-life = `ln(2)/θ`.
- **Calculation:** linear regression of the daily change in the spread (dz) against the spread level itself (`dz = θ·(z − mean(z))·(−1) + noise`, regress dz on (prevz − mean(prevz)) to get θ = −(regression beta)); `halflife = -log(2)/theta`.
- **Best/Poor Conditions:** applicable specifically to spreads/series already identified as mean-reverting (e.g. via cointegration test); not meaningful for trending/momentum series.
- **Combinations:** naturally paired with CADF cointegration testing (below) and target-price exit logic (μ = natural target price).
- **Examples:** GLD/GDX spread half-life ≈10.0037 days (Example 7.5).

## Cointegrating Augmented Dickey-Fuller (CADF) Test — Chan Ch. 7
- **Definition:** statistical hypothesis test for whether a linear combination of two (or more) non-stationary price series is itself stationary (cointegrated). Implemented via the `cadf` function in a free MATLAB econometrics package (spatial-econometrics.com, James LeSage).
- **Calculation:** treated as a "black box" statistical test in the source; output is a t-statistic compared against tabulated critical values at 1%/5%/10%.
- **Interpretation:** t-statistic more negative than a given critical value → cointegration supported at that confidence level.
- **Weaknesses:** a valid CADF result at one point in time does not guarantee validity persists into the future ("as long as the stationarity persists into the future (which is by no means guaranteed)").
- **Examples:** GLD/GDX: t-stat = −3.35698533 (1 lag) vs. critical values −3.819 (1%)/−3.343 (5%)/−3.042 (10%) → >95% probability of cointegration. KO/PEP: t-stat = −2.14, weaker than −3.038 (10%) → <90% probability (test FAILS despite same-industry intuition).

## Correlation Coefficient (returns) vs. Cointegration — Chan Ch. 7
- **Central lesson (explicit):** high correlation of RETURNS does NOT imply price LEVELS will not drift arbitrarily far apart — correlation does not guarantee (or even meaningfully suggest) a pair-trade spread will mean-revert. KO/PEP: return correlation=0.4849, p=0 (statistically significant) YET fails the CADF cointegration test.
- Chan's linear regression / correlation content (Ch. 6) recommends inputs be returns/price differences, not raw price levels, to avoid trend-driven distortion.
- **Kaufman's parallel treatment (Ch. 6):** `r = covariance(x,y)/(σx×σy)`, Excel `CORREL(x,y)` returns r². **Practical threshold: R² < ~0.20 → the regression has no practical value.** Best conditions: use returns/price differences, not raw levels. Arbitrage-specific interpretation: high correlation = little arbitrage opportunity; moderate positive correlation = more useful for arbitrage pair selection. Alternative: Spearman's Correlation (rank-based, less weight to outliers, more complex).

## Principal Component Analysis (PCA) as Factor-Model Construction — Chan Ch. 7
- **Definition:** decomposes a return covariance matrix into orthogonal eigenvector "factors," ranked by variance (eigenvalue) explained.
- **Calculation:** eigen-decomposition of `⟨RRᵀ⟩` (rolling window, e.g. 252 days); top-K eigenvectors form factor-exposure matrix X; eigenvalues = variances of the (mutually uncorrelated) factor returns b.
- **Required assumption (explicit):** requires factor EXPOSURES to be constant over the estimation window — explicitly RULES OUT using this exact method for inherently time-varying exposures like mean-reversion or momentum.
- **Weaknesses:** in the book's own S&P 600 small-cap worked example, resulting strategy had a strongly negative average annualized return (−1.81), attributed to either the "factor returns have momentum" assumption being wrong, or idiosyncratic returns being too large relative to the factor-driven component.
- **Examples:** Example 7.4 — a documented **failure case**, not a working method.

## Fama-French Three-Factor Model — Chan Ch. 7
- **Definition:** postulates a stock's excess return depends linearly on three factor exposures: beta, market capitalization, book-to-price ratio (Fama and French, 1992).
- **Calculation:** multivariate linear regression of excess stock returns against the three exposures; factor exposures typically normalized (mean 0, std 1 within the universe).
- **Weaknesses:** requires assuming factor returns have MOMENTUM to be usable predictively — vulnerable to periods when valuation methodology shifts (explicit examples: late-1990s Internet bubble; Aug/Dec 2007, when growth outperformed value, reversing the model's typical positive book-to-price factor return).
- **Best/Poor Conditions (typical signs):** market-cap factor return usually negative (small-caps outperform large-caps); book-to-price factor return usually positive (value outperforms growth) EXCEPT growth-favoring regimes; beta factor return usually positive.
- Chan cites Grinold & Kahn (1999): a good factor model with monthly returns on 1,000 stocks and 50 factors typically achieves R² of 30%–40%.

## GARCH — Chan Ch. 7 (mentioned only)
- Classical econometric model for time-varying volatility; cited (Klaassen, 2002) not derived. Explicitly noted as having "a long history of success" for volatility specifically, but "of no help to stock [directional] traders" — best suited to options/volatility-focused trading. Contrasted with (and presented as more established than) Markov regime-switching / hidden Markov models for price-level regime detection.

## Perceptron (Neural Network) in Regime-Switching — Chan Ch. 7
- Used in Example 7.1 to find optimal linear weights combining several technical trading rules (each with a different holding period) to maximize backtest profit within a moving training window (50-day window best-performing variant). "Black box" platform presentation (Alphacet Discovery); author acknowledges residual data-snooping risk from trying different rule "categories" until one works. Demonstrated on a 6-month backtest window for a single stock (GS) — author flags this short window as a genuine limitation.

## N-Day High/Low (Moving High/Low) — Chan Ch. 7
- Rolling max/min over an N-day window (N=10 in Example 7.1); used as a confirmation condition alongside a large percent-change threshold; not independently ablated in the book.

## Autocorrelation / Durbin-Watson d-statistic — Kaufman Ch. 6
- **Definition:** autocorrelation (serial correlation) measures whether a series' own future values can be predicted from its own past values — evidence of trend or cyclicality.
- **Calculation (simple method):** shift a copy of the series down 1+ rows and correlate with the original. **Formal test:** Durbin-Watson d-statistic, based on the change in regression errors across N points; ranges 0-4. d≈2 = no autocorrelation; d<2 = positive autocorrelation; d>2 = negative autocorrelation (more extreme further above 2).
- **Use:** diagnostic for regression/ARIMA model adequacy (a correlogram — plot of autocorrelation coefficients across lags — checks whether trend/periodic structure remains after differencing).

## ARIMA (Autoregressive Integrated Moving Average) / Box-Jenkins — Kaufman Ch. 6
- **Definition:** rolling regression combining an autoregressive component with a moving-average error-correction component, applied to a differenced (stationary) price series.
- **Calculation:** 1st-order AR: `pₜ = a·pₜ₋₁ + e`; 2nd-order: `pₜ = a₁pₜ₋₁ + a₂pₜ₋₂ + e`. MA error term (1st/2nd order): `Eₜ = b₁eₜ₋₁ (+b₂eₜ₋₂)`, functionally similar to exponential smoothing. Final forecast = AR estimate + smoothed MA error term, iterated until error variance stabilizes.
- **Notation:** ARIMA(p,d,q) — p=AR terms, d=differences, q=MA terms. ARIMA(0,1,1) = simple exponential smoothing.
- **Procedure:** (1) Specification — stabilize variance, detrend via differencing, choose minimal AR/MA orders using a correlogram; (2) Estimation — minimize forecast errors iteratively; (3) Testing for completion — coefficient stability, small/stable squared error, iteration cap.
- **Weaknesses:** forecast accuracy highest for the immediate next period, degrades further out; failure to converge usually indicates the data isn't yet stationary (needs further differencing) or the window spans too heterogeneous/volatile a regime.
- **Combinations:** basis for 3 named ARIMA trading strategies (see Kaufman `Strategies.md`).

## Kalman Filter — Kaufman Ch. 6; Chan (mentioned only)
- **Kaufman's treatment:** an alternative to ARIMA combining an underlying forecast ("message") model (any trading strategy/MA/regression approach) with a separate "observation" model (timely information such as specialist/floor-broker calls, liquidity, related-market activity). Message model `pₜ = a·pₜ₋₁ + message-error`; observation model has its own observation error; combined forecast adjusts the message-model result by a weighting factor K applied to the observation error (exact K-combining formula an embedded-graphic gap). Source: R.E. Kalman, 1960; commodities application via Seidel & Ginsberg, 1983.
- **Chan's treatment:** mentioned once, in a list of ML/AI techniques (alongside hidden Markov models and neural networks) that "still others" use to try to determine mean-reverting vs. trending regime; **not elaborated, derived, or demonstrated anywhere in this book** despite being named — no formula, worked example, or further discussion given.

## Linear Regression (Least-Squares Straight-Line Fit) — Kaufman Ch. 6
- **Definition:** `Y = a + bX`, best-fit line minimizing sum of squared deviations.
- **Calculation:** solved via simultaneous equations using N, ΣX, ΣY, ΣXY, ΣX² (or Excel's Slope/Intercept, TradeStation LinearRegSlope/LinearRegValue/LinRegIntercept). For trend-following, X = sequential bar index (not calendar date, avoiding weekend/holiday distortion).
- **Parameters:** calculation window length — full-year multiples deseasonalize; ≤3 months preserves seasonal signal; shorter/rolling windows generally track recent trend changes better than one long static fit.
- **Combinations:** basis for linear regression trading signals, the regression-slope trend system, confidence bands, the Forecast Oscillator, and cross-market ranking.

## Cycle Analysis Toolkit — Kaufman Ch. 11
- **Cattle Cycle / general cycle-length-by-tabulation method:** mark peaks/valleys on a long-term chart, tabulate dates, average days-between-peaks and days-between-valleys separately, average those two averages, convert to months. Rule of thumb: at least 8 cycle repetitions needed before concluding a cycle is valid. Worked example: cattle cycle = 10.2 months, cross-checked against the 4-6 month weaning + 6-10 month fattening fundamental cycle.
- **Triangular Moving Average (TMA) / Triangular MACD:** triangular (center-weighted, symmetric) weighting; calculation period should be odd. "Triangular MACD" = difference of two TMAs, one at half the period of the other (e.g. 20-10 on IBM; 252-126 on corn using a ~63-day quarterly-earnings period). Behaves like a momentum indicator but its smoothness aids anticipating major turns.
- **Two-Trendline Detrending (Johnson/Ehlers):** longer EMA/SMA set to half the dominant-cycle period, shorter set to half the longer one; MACD-style difference forms a smoother synthetic trend for detrending (author's refinement: lag this difference series by half the longer period before subtracting from price).
- **Cycle terminology:** Amplitude (a) = wave height from midpoint; Period (T) = time units per wavelength; Frequency (ω)=1/T; Phase = starting-point offset; Phase angle = clock-style position (0°=3 o'clock); Left/right translation = peak skew relative to cycle center.
- **Trigonometric sine-wave regression:** `y = a·sin(ω·φ + b)` for a single wave; compound wave = sum of multiple such terms at the same φ. Extrema via 1st derivative=0, 2nd derivative sign distinguishes max/min. Single/2-frequency trigonometric regression solvable via Excel Solver (worked corn example: minimized error 34.7).
- **Fourier Analysis / FFT:** expresses a (detrended, stationary) series as a sum of sine/cosine waves; requires ≥256 data points and ≥16 consistent 16-bar cycles for reliable use. Excel's Data Analysis add-in performs it directly (input must be power-of-2 count, max 4096); output complex-valued, use `IMABS` for magnitude. Worked on Southwest Airlines and cash corn monthly data.
- **Spectral Analysis / Periodogram / Spectral Density:** isolates/measures cyclic components (typically via Fourier series); periodogram → weighted → spectral density diagram (density = amplitude² net of noise). Requires ≥1 full cycle of data at minimum, more for robustness. Tukey window and Parzen window (lag-window functions with truncation point M) — exact formulas an embedded-graphic gap.
- **Shannon Entropy** (reconstructed from the standard published formula, not verbatim): `H = −Σ p_i·log(p_i)`, p_i = probability of character i — information-theory disorder measure, basis for Ehlers' MESA concept. (Also appears in Ch. 20 with base-2 log and normalization — see below.)
- **Maximum Entropy Spectral Analysis (MESA)** (John Ehlers): filters noise from a time series to expose useful cycles from very small amounts of data (vs. Fourier's ≥256-point requirement); useful cycles found only ~20% of the time by Ehlers' own account. Companion concept: phase angle sawtooth pattern — a uniform sawtooth signals an intact cycle, erratic phase signals cycle breakdown.
- **Hilbert Transform** (Ehlers): separates cycle phase into Quadrature and InPhase components using as little as 4 bars of data; phase angle θ = arctan(Quadrature/InPhase). Worked example: soybean monthly data, alpha=0.07, sharp peaks/valleys good for mean-reversion timing (vs. plateau-then-hold behavior of standard oscillators at extremes). Needs a minimum price-volatility threshold filter since it still shows relative highs/lows during low-volatility periods. Reduced Quadrature/InPhase formulas an embedded-graphic gap.
- **Fisher Transform** (Ehlers): `Fisher = 0.5·ln[(1+x)/(1−x)]` (reconstructed from the standard published form), x = normalized price position within a MaxH/MinL channel (bounded −1 to +1; channel-position normalizing formula an embedded-graphic gap). Output range ±1.0. Signal via a 3-day-MA trigger line, MACD-style; best signals occur just after an extreme high/low, not near a zero-crossing.
- **Inverse Fisher Transform** (Ehlers): see RSI entry above (Momentum family).
- **Ehlers' Universal Oscillator:** super-smoother-filter + Automatic Gain Control (AGC) construction designed to track price with near-zero lag; demonstrated on heating oil futures. Filter coefficients, initialization thresholds, and AGC combining formula are embedded-graphic gaps.
- **Short Cycle Indicator / "LX"** (Francisco Lorca-Susino): squared difference of two EMAs (XF faster, XS slower) combined with a stochastic-style relationship to the slower period's high/low extremes; term (XF−XS)/XF addresses convergence; SF (scaling factor) formula a gap. Applied to intraday bars across multiple timeframes; the indicator's turns often precede price turns.
- **Hurst Phasing:** lag a moving average by half its own calculation period ("phasing") so it appears centered on price; full-span MA (period estimated from average distance between chart tops) and half-span MA (half the full-span's period) both phased; their crossing points feed a linear regression trendline used to project price objectives — full 10-step rule set in Kaufman `Strategies.md`.
- **Note (Chan's book):** the **Hurst exponent is not mentioned anywhere in the Chan book** — flagged explicitly since it is a commonly expected mean-reversion/trending diagnostic in the broader quant literature; its absence there is a genuine gap relative to the field, not an extraction oversight. Kaufman's "Hurst Phasing" (above) is a distinct technique (moving-average phase lag) and NOT the same concept as the Hurst exponent.

## Shannon Entropy / Conditional Entropy — Kaufman Ch. 20
- **Shannon Entropy (reconstructed from the standard published formula, explicitly labeled as such — the source's own inline notation is an embedded-graphic gap):** `H(x) = −Σ p_i × log₂(p_i)`, p_i = probability of the ith of n possible outcomes. H=0 when fully predictable (p_i=1 for one outcome); H maximized at log₂(n) when all outcomes equally likely. Normalized by dividing by log₂(n). Used to assess how predictable a next-day price-move distribution is following a given chart-pattern setup.
- **Conditional Entropy:** measures the probability that two patterns (a past setup X and a subsequent outcome Y) are similar/related. Conditional probability `P(Y_j|X_i) = f(X_i,Y_j)/f(X_i)` (joint frequency over marginal frequency); conditional entropy H(Y|X) = probability-weighted average of the entropies across each state of X (exact inline summation formula an embedded-graphic gap). Higher H = greater predictive value. **Caveat:** cells built from very small samples (e.g. 1 observation) can show high-looking values that are not reliable.

## Genetic Algorithm Fitness Criterion — Kaufman Ch. 20
- `rank = f(profit/trade, number of trades N, GP/GL)` — combines profit magnitude, sample-size adequacy, and consistency (gross-profit/gross-loss ratio, or alternatively the information ratio AROR/ASD). Worked comparison: a high-per-trade/low-trade-count/low-P&L-ratio system (170.75) ranked below a lower-per-trade/high-trade-count/high-P&L-ratio system (315.00) — the criterion favors consistency and sample size over raw per-trade profit. (See `14_backtesting_and_validation.md` for the broader objective-function/search discussion including Pardo's PROM.)

## K-Nearest Neighbor / K-Means Distance Measures — Kaufman Ch. 20
- k-NN classifies/values a new data point by majority vote or weighted average (weight ∝ 1/distance) of its nearest known neighbors. **Euclidean distance (reconstructed from the standard published form):** `d = √((x−x_i)² + (y−y_i)²)`, extended with a third term for 3D. K-Means iteratively re-centers a point's estimated value at the mean of its neighborhood until convergence.

## Chande's Trend Strength Ranking — Kaufman Ch. 23 (cited to Chande, 1997)
- `St = (net return over n days) / f(σ)`, σ = stdev of 1-period returns over n periods (structurally similar to the Efficiency Ratio/noise concept). St's sign gives trend direction.
- **Author-flagged internal critique:** applying this with a log transform to stocks implicitly assumes volatility rises with price, which Kaufman states is "not correct" (cross-ref Ch. 22's volatility-scale discussion, see `14_backtesting_and_validation.md`) — Kaufman critiquing Chande's own published method, not endorsing it.

## Expected Portfolio Return / Variance / Covariance (MPT forms) — Kaufman Ch. 24
- `E(R) = Σ wᵢ·E(Rᵎ)` (weighted average of asset expected returns); portfolio variance `σp² = ΣᵢΣⱼ wᵢwⱼ·Covᵢⱼ`; `Covᵢⱼ = σᵢ·σⱼ·ρᵢⱼ`. **The book's own inline notation for these three did not survive PDF extraction; reconstructed in standard, widely-published Markowitz mean-variance form and flagged as such** (fully consistent with the chapter's own surrounding prose description).

## GASP Objective Function — Kaufman Ch. 24
- `OF = AROR / SDD`, SDD (semivariance of daily drawdowns) = `sqrt[ Σ(Hᵢ−Eᵢ)² / n ]` over all days i where Hᵢ≠Eᵢ (Hᵢ=peak/high cumulative equity as of day i, Eᵢ=current equity, n=count of drawdown days). Structurally identical to the Ulcer Index formula (Ch. 23, see `Risk_Management.md`) — same semivariance-of-drawdowns construction, repurposed as a portfolio-allocation objective function.

## Perfect Profit (PP) — Pardo Ch. 2/9/12 (benchmark, not a tradable indicator)
- **Definition:** "The sum total of all of the potential profit that could be realized by buying every bottom and selling every top... the sum of the absolute value of every price swing formed between a price peak and a subsequent price valley."
- **Purpose:** a theoretical ceiling used to measure a market's total available "opportunity" over a given window/time-degree; denominator for Model Efficiency (Ch. 12) and for the Correlation between Equity Curve and Perfect Profit (CECPP) objective function (Ch. 9, see `14_backtesting_and_validation.md`).
- **Calculation:** sum of absolute peak-to-valley swings; monotonically, cumulatively increasing over time by construction.
- **Parameters:** time degree matters enormously — Table 12.1 shows PP across 5-min/30-min/daily/weekly/monthly time degrees for 5 markets over 2002–2006 (e.g., S&P PP ranges from $432,400 monthly to $18,498,100 at 5-minute granularity over the same 5 years).
- **Weaknesses:** explicitly "an idealized and unobtainable goal" / "obviously an unachievable ideal measure" — not a tradable indicator, purely an analytical benchmark.
- **Examples:** see Pardo `02_Chapter_12_The_Evaluation_of_Performance.md` — worked Model Efficiency example (net profit $25,000 / PP $300,000 = 8.33% ME).

## Point-and-Figure Constructs — Kaufman Ch. 5
- **Box Size / Reversal Value:** box size = minimum price increment per mark; reversal value = box size × number of boxes required (traditionally 3) to start a new column. Practical starting box size = the market's 20-day ATR. **The Box Size Dilemma:** a fixed box size that works well at one price/volatility regime performs poorly at another — explicitly flagged as "a problem yet to be solved" (Chartcraft's fixed-grid rescaling, Zieg & Kaufman's variable-size box, ATR-based dynamic box size surveyed as imperfect partial solutions).
- **Horizontal Count:** `H_U = P_L + (W × R)` [upside]; `H_D = P_H − (W × R)` [downside], P_L/P_H = extreme price of the base/top formation, W = formation width in columns (excluding breakout column), R = reversal value.
- **Vertical Count:** upside objective = low of a bottom formation + (3 × size of the first reversal column following the bottom, 3 = boxes in a minimum reversal); downside mirror. Worked QQQ example: Oct 2002 low $20.00 + (3×$3.25 first-reversal) = $29.75 target, reached May 2003.

## Wilder's Swing Index (SI) / Accumulated Swing Index (ASI) — Kaufman Ch. 5 (Wilder, 1978)
- **Definition:** SI combines 5 daily open/high/low/close relationship factors plus a weighted true-range term into a single value scaled −1 to +1; ASI = running cumulative sum of daily SI, substituted for price to derive trading signals.
- **Calculation:** exact combining sub-formulas for K and the two-step TR calculation are embedded-graphic gaps; the 5-factor structure is explicit.
- **Modernization:** M (scaling constant, originally the market's exchange-set limit-move value) can be any arbitrary value larger than the normal daily move (example M=100) since derived trading rules use only ASI's relative highs/lows (HSP/LSP), not fixed numeric thresholds.
- **Derived terms:** HSP (High Swing Point, confirmed 2 days late), LSP (mirror); SAR (3 types: Index SAR, price-applied SAR, Trailing Index SAR lagging 60 ASI points behind the trade's best ASI value).

## Fibonacci Retracement Ratios — Kaufman Ch. 4, Ch. 14
- **Definition:** ratios from the Fibonacci sequence (1,1,2,3,5,8,13,21,...), used as candidate price-retracement/extension targets.
- **Calculation:** the ratio of consecutive terms approaches 1.618 as n grows; inverse is 0.618; a secondary, less-used ratio ≈0.382 (reciprocal-of-reciprocal form) also cited.
- **Ch. 14 clarification:** 0.618 = limiting ratio of consecutive Fibonacci numbers; 1.618 its reciprocal; 2.618 = ratio 2 positions apart; **0.382 is explicitly noted by the author as NOT itself a Fibonacci ratio**, despite being a very commonly used retracement level (it is the complement of 0.618).
- **DeMark's refinement (cited):** additionally uses 0.382, 0.50, 1.382, 2.236, and 2.618 as "alternative" ratios, applied to a move measured from the highest point reached since price last traded at the current low (rather than from the most recent swing high).
- **Combined Fibonacci-Lucas (FL) series** (Harahus extension): Lucas numbers (1,3,4,7,11,18,29,47,76,123,199,...) combined with Fibonacci, duplicates removed, to fill gaps between large Fibonacci terms for day-count/retracement-percentage projections. Successive-ratio convergence to 0.618 shown oscillating: 1.000, 0.500, 0.667, 0.625, 0.615, 0.619,...
- **Practical caveat:** exact hits are unrealistic — use a tolerance band or multiple targets rather than a single price.

---

# Indicators Named But Not Elaborated (explicit gaps, preserved verbatim from sources)

- **Elliott wave theory** (Chan) — mentioned as a technical-analysis framework some chartists use for the "fractal" mean-reverting/trending duality of prices; not elaborated or endorsed. (Kaufman's book, by contrast, DOES give a worked Elliott Wave Oscillator and full rule set — see Momentum family above and `Strategies.md`.)
- **Hidden Markov models** (Chan) — mentioned as an academic regime-detection technique, critiqued generally as "generally useless for actual trading purposes" due to the constant-transition-probability assumption, but not derived mathematically.
- **Kalman filter** (Chan) — mentioned once in a list of ML/AI regime-detection techniques; not elaborated, derived, or demonstrated. (Kaufman's book DOES derive it structurally — see above.)
- **Hurst exponent** — not mentioned anywhere in the Chan book (explicit gap flag, not an oversight in extraction).
- **Kaufman's own several "formula not recoverable"/"embedded-graphic gap" indicators** are individually flagged throughout this file at their point of use (Price Density, Fractal Dimension steps 4-6, Candle Body Directional Momentum's combining formula, Shadow Trend, Qstick's threshold logic, Pivot Point Levels' level arithmetic, Moving Channel's projection arithmetic, CCI's 0.015 constant, Wilder's SI/ASI sub-formulas, N-Day Breakout adaptive-N formula, Kalman filter's K-weighting, Money Flow's ratio/index formula, HPI already recovered in full, Divergence Index already recovered, SwamiChart, RVI's weighting formula, Oscillator O, Ultimate Oscillator fully recovered, TSI fully recovered, Blau's TRIX fully recovered, DMI's ambiguous inversion, ADX chain's smoothing-constant notation, CSI's exact shape, KAMA's SC-from-ER sub-formula, VIDYA's k-formula, FRAMA's power-law formula, McGinley Dynamic reconstructed, Instantaneous Trend's AT/Trigger formulas, various volume-indicator "formula gap" items in Section IV, Hilbert/Fisher Transform sub-formulas, Tukey/Parzen window formulas, Gann's astrological sub-equations, DeMark's Projected Range combining formula, Greer-Brorsen slippage model formula, Ginter-Richie execution-cost formula). These are preserved individually at each entry above rather than repeated here; this paragraph is a navigation aid only.

---

*End of file 13. Cross-references: `14_backtesting_and_validation.md` (testing/optimization methodology that treats many of these indicators as example vehicles), `Risk_Management.md` in each book's own Knowledge folder (position-sizing/Kelly/VaR/Sharpe-family content not duplicated here), `16_research_hypotheses.md` (sibling file, written separately by another agent).*
