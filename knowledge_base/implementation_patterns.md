# Implementation Patterns — A Composable Building-Blocks Reference

## Purpose and Scope

This file is a catalog of **reusable implementation patterns** extracted from the five source books
(Kaufman, Chan, Vince, Hilpisch, Pardo) — the composable pieces a strategy is *built from*, not the
strategies themselves. Full named strategies and concrete hypotheses live in the sibling file
`hypothesis_bank.md` (built in parallel); this file is the parts bin those hypotheses draw components
from. A future `EDGE_FRAMEWORK.md` will describe how to reason about whether a *combination* of these
patterns constitutes a genuine edge; a future `AI_RESEARCH_PLAYBOOK.md` will describe the research
process for testing them. This file, `README.md`, and `master_index.md` will need a pointer added once
those files exist.

**How to use this file**: each pattern entry gives the problem it solves, when it helps/hurts per the
sources, what it's commonly paired with (and why), common implementation mistakes, and where to find the
full formula. This file deliberately does **not** restate exact formulas — those live in
`13_indicator_reference.md` (indicator math), `10_position_sizing.md` (sizing math), `09_exits.md` (stop
math), and `06_volatility.md` (volatility math). Every claim is traceable to a specific book/chapter and,
where useful, to the knowledge_base file that documents the underlying math in full. Formula gaps flagged
as "embedded-graphic" or "reconstructed" in the source files are not re-litigated here; consult the
underlying file for those flags.

**A cross-cutting note on combination itself**: nearly every pattern below is explicitly documented, in at
least one source, as *dependent for its safety on being paired with something else* — a trend filter alone
is not a strategy, a stop alone is not risk management, a sizing rule alone does not define an edge. The
"Common combinations" field in each entry is not decorative; it reflects a real, source-documented
non-optionality. Kaufman's own three-part strategy definition (entry + risk management + position sizing,
independently converged upon by Pardo, Ch.5) is the organizing assumption behind why this file exists as a
separate layer from `hypothesis_bank.md` at all: a hypothesis is a *particular assembly* of these parts,
and the same parts recombine into many different hypotheses.

---

## Trend Filters

### Pattern: Moving-Average-Direction Filter

- **Purpose**: gate entries/exits so a strategy trades only in the direction the market is already
  moving, using the *direction of change* of a trendline (not price crossing it) as the signal.
- **Mechanism**: buy when the trendline (SMA/EMA/regression) turns up; sell short when it turns down —
  the lowest-frequency, highest-lag member of Kaufman's "three families of entry/exit rule" (Kaufman
  Ch.8; full mechanics in `02_trend_following.md`, `08_entries.md` §3).
- **When to use**: longer-term/position trading where fewer, more reliable signals are preferred over
  high signal count; markets/timeframes where noise dominates short calculation periods (Kaufman Ch.8).
  Table 8.2 (10-yr Amazon, 5 calc periods): trendline-direction signals produced 26-37% fewer trades and
  generally better Profit Factor than price-penetration variants.
- **When to avoid**: at very fast calculation periods (≤5 days in the Amazon test) the added lag costs
  more than the noise-filtering benefit — price-penetration variants performed better there. Also
  unsuitable in genuinely sideways/congested markets (see Confirmation Logic — sideways classification).
- **Common combinations**: paired with a second, faster trendline (see Multi-Timeframe Agreement below)
  to add entry timing on top of directional confirmation; paired with an Efficiency-Ratio or ADX filter
  to avoid trading a "direction change" that is really just noise reversing inside a non-trending regime.
- **Common mistakes**: choosing the calculation period is "the most important decision in the ultimate
  success of the trading system" per Kaufman — more consequential than which trend-identification method
  is used at all (Kaufman Ch.8). Testing calculation periods only at equally-spaced *day* counts (rather
  than equally-spaced smoothing constants) biases which "styles" of trend a parameter sweep actually
  samples (Kaufman Ch.7) — see `18_common_failure_modes.md` §7 (Peak-Parameter Fragility).
- **Source**: Kaufman Ch.7-8. Full formula/mechanics: `02_trend_following.md`, `08_entries.md` §3.

### Pattern: Efficiency Ratio (ER) Threshold Gate

- **Purpose**: distinguish a genuinely trending (low-noise) regime from a noisy/sideways one, using net
  price change over a period divided by the sum of absolute bar-to-bar changes over that period — a
  measure of how *directly* price travels, not how *far* or how *large* the swings are.
- **Mechanism**: ER near 1 = low noise (trend-suited); ER near 0 = high noise (mean-reversion-suited).
  Gate trend-following entries to fire only above an ER threshold (Kaufman Ch.1, Ch.17).
- **When to use**: as a pre-trade regime filter for any trend-following system, and as the live-adapting
  input to adaptive smoothing constants (see Adaptive Smoothing Patterns below). Explicitly NOT
  interchangeable with a volatility filter — a market can show large absolute swings and still have high
  ER if all those swings are part of one large net directional move (Kaufman Ch.1, Ch.20).
- **When to avoid**: ER is a fractal property — it applies "in the same way at all levels of detail," so
  a single ER reading at one timeframe does not resolve whether a *different* timeframe is trending
  (Kaufman Ch.1). Emerging/less-mature markets show artificially low noise from thin participation, not
  genuine trend cleanliness — liquidity, not the ER reading itself, may be the binding constraint there
  (Kaufman Ch.1).
- **Common combinations**: the direct regime-detection input for KAMA-style adaptive smoothing constants
  (Adaptive Smoothing Patterns); commonly paired with ADX as a second, independent trend-strength
  confirmation (see Confirmation Logic); Chan's independent mean-reversion-vs-momentum regime framing
  (Chan Ch.7) is a conceptual echo of the same trend/noise dichotomy from a different author, useful as a
  cross-check.
- **Common mistakes**: conflating noise with volatility is flagged explicitly as a recurring, easy-to-make
  error (Kaufman Ch.20; also flagged as a KAMA-specific common mistake in `13_indicator_reference.md`).
- **Source**: Kaufman Ch.1, Ch.17, Ch.20. Full formula: `13_indicator_reference.md` (Efficiency Ratio
  entry), regime framing in `07_market_regimes.md` §1.

### Pattern: ADX / Directional-Movement Regime Gate

- **Purpose**: use trend *strength* (as opposed to ER's trend *cleanliness*) to decide whether to take
  trend-following signals at all, and which direction to favor.
- **Mechanism**: ADX rising → take only longs; ADX falling → take only shorts; if ADX remains above both
  +DMI and −DMI (extreme price strength), hold the position using only a trailing stop to exit — the
  Directional Parabolic System's explicit regime-gate design (Kaufman Ch.9). Kestner's Oscillator Method
  with ADX Filter similarly gates an MA-difference oscillator's signals behind an ADX-based "no-trend"
  condition, only acting when both hold simultaneously (Kaufman Ch.9).
- **When to use**: as a companion filter to a fast oscillator/crossover system that would otherwise
  whipsaw heavily in a non-trending market — the point of the combination is that the oscillator supplies
  timing while ADX supplies the regime gate.
- **When to avoid**: exact inequality thresholds for the Kestner combination were not recoverable from the
  source (embedded-graphic gap) — thresholds must be independently derived/tested, not assumed.
- **Common combinations**: paired with Wilder's Parabolic SAR (ATR Usage Patterns — trailing-stop
  variant) in the Directional Parabolic System; conceptually parallel to (but a distinct measure from) the
  ER-threshold gate above — the two can be used together as independent confirmations (see 2-of-3
  Confirmation Logic).
- **Common mistakes**: treating ADX level as a directional signal by itself — it measures trend strength,
  not direction; direction still requires +DMI vs. −DMI or a separate directional indicator.
- **Source**: Kaufman Ch.9. Full formula: `13_indicator_reference.md` (ADX/DMI entries).

### Pattern: Multi-Timeframe Agreement (Elder Triple Screen style)

- **Purpose**: require a slower, higher-timeframe trend to be confirmed by a faster, lower-timeframe
  timing signal before acting — reduces whipsaw from taking a fast signal that contradicts the dominant
  trend.
- **Mechanism (generic two-trendline family, Kaufman Ch.8)**: three named rule-set variants —
  (1) simple crossover, always in market; (2) price-vs-both-MAs, creating a flat/neutral zone, entering
  only when price crosses *both* MAs; (3) both-trendlines-agree, entering only when the faster trendline's
  own direction agrees with the slower one, exiting when they conflict. A third, even-faster confirming
  trendline can be layered on top (the Modified 3-Crossover Model) specifically so a trade is never
  entered while price is actually moving opposite to the position about to be taken (Kaufman Ch.8).
  Ichimoku Cloud is a further hybrid: the cloud direction is the macro trend filter, while a separate
  Tenkan-sen/Kijun-sen cross times shorter-term re-entries strictly in the cloud's current direction
  (Kaufman Ch.8).
- **When to use**: whenever a fast signal generator (oscillator, short MA cross) is otherwise prone to
  false signals in choppy conditions; Rule Set 2/3's flat/neutral zone specifically adds "liquidity"
  (smaller order size at transitions) versus an always-reversing design (Kaufman Ch.8).
- **When to avoid**: worked test of a 3-day timing trend added to an 80/20 Eurodollar crossover showed
  small improvement on longs but a decline on shorts (Kaufman Ch.8) — confirmation layers are not free;
  each must be tested per market/direction, not assumed symmetric.
- **Common combinations**: pairs naturally with any breakout confirmation pattern (below) — the
  higher-timeframe trend supplies direction, the breakout confirmation supplies entry timing on the lower
  timeframe. Also the direct trend-side analogue of oscillator-confirms-trend logic (Confirmation Logic).
- **Common mistakes**: the "4-9-18 Crossover" and "Ahead of the Crowd 8-18" case studies are explicit,
  source-documented warnings that a once-popular parameter combination can decay as the "crowd" using it
  changes — Kaufman's own modern out-of-sample retest of the 4-9-18 found only marginal profits, with the
  explicit caveat it likely worked better in an earlier, lower-noise market era (Kaufman Ch.8). Treat any
  specific period combination as a hypothesis to test, not a working default.
- **Source**: Kaufman Ch.8. Full formula/system detail: `02_trend_following.md`, `08_entries.md` §3.

---

## Volatility Filters

### Pattern: ATR-Based Regime Gate (Absolute Threshold)

- **Purpose**: exclude or delay trades when volatility is outside a "workable" range, since both very
  high and (for some strategy types) very low volatility change the risk/reward of a signal.
- **Mechanism**: compute annualized volatility (or ATR-based volatility) and compare to fixed thresholds.
  Kaufman's explicit worked finding: above ~45% annualized volatility on an individual market, returns
  decline and risk rises — exit and don't re-enter until volatility falls back to ~35% (Kaufman Ch.20).
  A 100-day trend system on QQQ using a 30%-exit/15%-re-entry volatility filter cut the standard deviation
  of daily returns by ~45% while returning slightly *more* profit than unfiltered (Kaufman Ch.20).
- **When to use**: works especially well for trend systems being run through extended high-volatility
  regimes (dot-com bust tail, 2008 crisis) — the QQQ test specifically avoided trading during both. Also
  usable at the portfolio level: deleverage above a target annualized volatility (commonly cited: 12% for
  futures fund managers), releverage below it (Kaufman Ch.20, Ch.23-24).
- **When to avoid**: thresholds are explicitly market-specific — "40% volatility" is only a rough average
  "good" threshold; interest-rate volatility differs greatly from crude oil, so thresholds must be tested
  per market (Kaufman Ch.20). Do not treat 45%/35% (or 12%) as universal constants.
- **Common combinations**: pairs with the Eliminate-vs-Delay decision rule (short-term trading can afford
  to eliminate a filtered trade outright; long-term trend trades should delay entry until volatility
  normalizes rather than miss a potentially large move, Kaufman Ch.20). Also pairs with Volatility-Target
  Position Sizing as the two halves of a single volatility-management approach (filter what to trade,
  size what you do trade).
- **Common mistakes**: applying a single global volatility threshold across a portfolio of unrelated
  markets, ignoring that "normal" volatility baselines differ structurally by market/sector (stock indices
  are naturally high-noise/high-vol, short-term interest-rate markets naturally low, Kaufman Ch.3, Ch.20).
- **Source**: Kaufman Ch.20, Ch.23-24. Full formula/detail: `06_volatility.md`.

### Pattern: Relative Volatility Ratio (Short/Long Period Ratio)

- **Purpose**: filter or size trades using *relative* rather than absolute volatility, which generalizes
  better across markets and regimes than a fixed absolute threshold.
- **Mechanism**: RV = v(n)/v(m), a short calculation period n over a longer "normal" period m, using any
  of the five volatility measures (Kaufman Ch.20; full list in `06_volatility.md`). The "bulge" problem —
  a volatile event stays inside the longer rolling window and keeps the ratio elevated long after the
  event has passed — is fixed by lagging the longer-period window so it ends *before* the shorter one
  begins (nonoverlapping windows), the same principle that fixes Bollinger Band "bulge" (Kaufman Ch.18,
  Ch.20).
- **When to use**: whenever an absolute volatility number would need re-tuning per market — relative
  volatility largely sidesteps the "avoid stocks under $5/$10" price-level distortion Kaufman documents
  for absolute volatility measures (Kaufman Ch.20).
- **When to avoid**: the unlagged version misdiagnoses two independent back-to-back volatile events as one
  continuous elevated-volatility period — always confirm the lagged-window fix is implemented before
  trusting the ratio as a regime signal.
- **Common combinations**: the same lagged-window fix generalizes directly to Bollinger Band width/squeeze
  (below) — document this as one fix serving two pattern families, not two separate fixes.
- **Common mistakes**: applying the ratio without the nonoverlapping-window fix and then being surprised
  that a rolling "regime" signal stays "on" long after the underlying event has genuinely passed.
- **Source**: Kaufman Ch.18, Ch.20. Full formula: `06_volatility.md`.

### Pattern: Bollinger Band Width / Squeeze

- **Purpose**: use band compression (low relative volatility) as a setup condition, then trade the
  eventual breakout through the bands, rather than trading band touches directly as overbought/oversold.
- **Mechanism**: standard bands = 20-day MA ± 2 SD of price changes over the same 20 days. The "squeeze"
  variant waits for the bands to compress to some percentage of their average width (e.g., 50%) before
  acting on a subsequent breakout; trading in the direction of the prevailing trend improves results
  further (Kaufman Ch.8, citing Kent Calhoun). Modified Bollinger Bands (McNicholl) address the same
  "bulge" problem as the Relative Volatility pattern above — bands widen quickly after a spike but shrink
  back slowly — via a faster-reverting center-line/multiplier construction (f=2.5 vs. standard 2.0).
- **When to use**: as a volatility-compression setup filter ahead of a breakout entry, ideally combined
  with a trend filter for directional bias (Kaufman Ch.8).
- **When to avoid**: because prices are not normally distributed, the nominal "2 SD" band captures only
  ~87% empirical confidence in practice versus the ~95.4% a true Normal distribution implies (Kaufman
  Ch.8) — do not treat the band as a calibrated probability interval. Also: Pardo's book treats "volatility
  bands" not as an endorsed indicator but as the *specific mechanism* of a documented overfitting failure —
  adding scanned volatility bands to an already-validated system took in-sample profit from $10,000 to
  $65,000 while the same added complexity lost $15,000 out-of-sample (Pardo Ch.13, per
  `18_common_failure_modes.md` §1). This stands in explicit contrast to Kaufman's much more favorable
  treatment of the same general band family — the disagreement is about confidence in a *specific
  historical parameter fit*, not about the band mechanism itself.
- **Common combinations**: the Rattlesnake Breakout Method combines a Bollinger squeeze, a Keltner
  Channel, and a Chaikin Oscillator (volume/fund-flow confirmation) as a 3-part confirmation stack
  (Kaufman Ch.8) — a concrete worked example of the 3-of-3 Confirmation Logic pattern below built entirely
  from volatility- and volume-based components.
- **Common mistakes**: scanning band-width percentage as a free optimizable parameter without
  out-of-sample validation — this is the exact overfitting mechanism Pardo documents. See
  `18_common_failure_modes.md` §1 (Overfitting) and §7 (Peak-Parameter Fragility).
- **Source**: Kaufman Ch.8, Ch.18; Pardo Ch.13. Full formula: `06_volatility.md`, `13_indicator_reference.md`.

### Pattern: Volatility Percentile / Empirical-Distribution Ranking

- **Purpose**: avoid the false-precision of a Normal-distribution volatility band (which can imply an
  impossible negative volatility lower bound) by ranking current volatility against its own empirical
  historical distribution instead.
- **Mechanism**: sort all historical rolling-volatility readings and read off percentile thresholds
  directly (e.g., SPY 1998-2018: 10% chance volatility exceeds 28.3%, 1% chance it exceeds 56.8%) rather
  than assuming ±2 SD around an average (Kaufman Ch.18).
- **When to use**: whenever a volatility-based filter/threshold is being calibrated and a short/recent
  sample is available — the empirical-percentile approach avoids the negative-lower-bound problem of a
  Normal assumption entirely.
- **When to avoid**: a short/recent sample understates tail risk relative to one spanning a genuine crisis
  period (Kaufman's own example: a recent-year-only sample showed a max of 27% vs. a much higher true tail
  once 2008 is included, Kaufman Ch.18) — the percentile approach is only as good as the historical window
  it draws from.
- **Common combinations**: this is the empirical-distribution analogue of the Volatility-Target Position
  Sizing pattern's normality assumption — the two can be combined by sizing off a percentile rank rather
  than a raw SD multiple.
- **Common mistakes**: using a convenient but short backtest window (e.g., "the last year") to set
  volatility percentile thresholds, silently excluding the tail events the filter most needs to survive.
- **Source**: Kaufman Ch.18. Full formula: `06_volatility.md`.

---

## Breakout Confirmation

### Pattern: N-Bar / Multi-Bar Confirmation

- **Purpose**: reduce false breakout signals by requiring the breakout to persist for more than one bar
  before acting, at the cost of later entry.
- **Mechanism**: the conservative (close-based) N-day breakout variant — buy only when today's *close* (not
  just the intraday high) is above the N-day high — is the simplest form (Kaufman Ch.5). Point-and-figure's
  analogous fix raises the required confirming breakout from 1 box to 2-4 boxes as volatility increases
  (Kaufman Ch.5).
- **When to use**: in noisier/higher-volatility conditions, where a single-bar intraday breakout is prone
  to immediate reversal.
- **When to avoid**: the always-in-market intraday-high/low variant produces the most (and most
  whipsaw-prone) signals but also the earliest entry — conservative confirmation trades signal frequency
  and entry price directly against each other; there's no free improvement.
- **Common combinations**: pairs directly with Volume Confirmation and Retest-Before-Entry as alternative
  or additive ways to filter the same false-breakout problem — a system can use one, two, or all three
  simultaneously (see 2-of-3 Confirmation Logic).
- **Common mistakes**: the Box-Size Dilemma (below, shared with ATR-as-regime-filter) shows that any fixed
  confirmation threshold that works in one volatility regime performs poorly in another — Kaufman
  explicitly calls this "a problem yet to be solved," not a solved one (Kaufman Ch.5).
- **Source**: Kaufman Ch.5. Full formula: `04_breakouts.md`, `08_entries.md` §2.

### Pattern: Volume Confirmation

- **Purpose**: use volume behavior as an independent confirming signal that a breakout reflects genuine
  participation rather than a thin, easily-reversed move.
- **Mechanism**: the Rattlesnake Breakout combines a Bollinger squeeze + Keltner Channel with a Chaikin
  Oscillator (fund-flow/volume-based) crossing zero as the final confirming trigger (Kaufman Ch.8).
  Crabel's opening-range breakout work found that preceding-pattern volume/volatility filters (inside
  days, NR4-style narrow-range bars) meaningfully improved the profitable-trade percentage of an
  intraday breakout (e.g., bonds 60%→76%, soybeans 60%→70%, Kaufman Ch.16).
- **When to use**: as an additive filter layered on a breakout or trend signal, particularly for
  intraday/day-trading breakout systems where Crabel's evidence is strongest.
- **When to avoid**: no source in this knowledge base gives a generalized, market-agnostic volume
  threshold — every worked example is specific to the market/system tested; treat volume-confirmation
  thresholds as needing per-market calibration, same as breakout-confirmation counts.
- **Common combinations**: forms one leg of the classic 2-of-3 or 3-of-3 confirmation stack alongside
  price-breakout and trend-direction legs (see Confirmation Logic below).
- **Common mistakes**: Kaufman's own price-volatility relationship material warns that volume and
  volatility tend to rise *together* around genuine equilibrium shifts ("chasing volatility," Kaufman
  Ch.18) — a volume spike alone, without a coincident volatility/price move, is a weaker signal than the
  combination.
- **Source**: Kaufman Ch.8, Ch.16, Ch.18. Full formula: `08_entries.md` §2, `13_indicator_reference.md`.

### Pattern: Multi-Box (Point-and-Figure) Confirmation

- **Purpose**: the point-and-figure-specific version of N-bar confirmation — raise the number of boxes
  required to confirm a breakout as volatility rises, since P&F's fixed box size otherwise becomes
  miscalibrated across volatility regimes.
- **Mechanism**: standard signal = 1 box beyond the prior column's extreme; raise to 2, 3, or 4 boxes as
  volatility increases to filter false starts (Kaufman Ch.5). The 3-box reversal convention itself is the
  base case of this same idea — a reversal must fill 3 boxes (a net move of box-size × reversal-boxes)
  before a new column starts at all.
- **When to use**: any P&F-based signal generation, and — as a general principle — any fixed-increment
  breakout method (Renko shares the identical weakness).
- **When to avoid**: the Box-Size Dilemma is explicit and unresolved in the source — a box size tuned for
  one volatility/price regime performs poorly in another, and Kaufman states plainly this is "a problem
  yet to be solved" even with ATR-based dynamic sizing as a partial fix (a position opened during high
  volatility might reverse if volatility later drops, Kaufman Ch.5).
- **Common combinations**: the three risk-limited P&F entry alternatives (pullback-then-standard-stop,
  second-reversal entry, raised confirmation count) are explicitly presented as *alternatives*, not a
  stack — pick one deliberately rather than combining all three (Kaufman Ch.5).
- **Common mistakes**: entering on the original 1-box signal with an arbitrary stop "3 boxes below the
  highs" — Kaufman explicitly states this "has no logical basis and can quickly result in a losing trade"
  (Kaufman Ch.5).
- **Source**: Kaufman Ch.5. Full formula: `04_breakouts.md`.

### Pattern: Retest-Before-Entry

- **Purpose**: avoid entering directly on the breakout bar (often the highest-slippage, worst-fill moment)
  by waiting for price to pull back toward the broken level before entering.
- **Mechanism**: P&F's second risk-limiting alternative — skip the first pullback opportunity and enter on
  the *second* reversal in the trend direction via a trailing order placed a fixed number of boxes above/
  below the reversal extreme (Kaufman Ch.5). The generalized gap-trading version: for an upward gap, wait
  for the empirically-typical ~40% retracement of the gap before entering long into the pullback rather
  than chasing the open (Kaufman Ch.15).
- **When to use**: whenever slippage/fill-quality at the breakout bar itself is a material cost — day
  trading in particular, per Kaufman Ch.16's "Not So Fast" finding that trend/directional entries face
  materially higher slippage than mean-reversion-style entries that wait for a pullback.
- **When to avoid**: a retest-based entry can miss the trade entirely if price never pulls back — this is
  the direct trade-off against the N-bar/multi-box confirmation patterns above, which also delay entry but
  do not require an actual retracement.
- **Common combinations**: pairs with time-in-market reduction as a risk-control side effect — waiting for
  a retest inherently reduces exposure to the highest-noise moment of a move.
- **Common mistakes**: none specifically flagged beyond the generic missed-trade risk above; this is one
  of the more source-uniform patterns in this file (P&F, day-trading, and gap-trading material all
  converge on the same logic independently).
- **Source**: Kaufman Ch.5, Ch.15, Ch.16. Full formula: `04_breakouts.md`, `08_entries.md` §2, §5.

---

## Position Sizing Patterns

### Pattern: Fixed-Fractional Sizing

- **Purpose**: the simplest sizing rule — commit a fixed percentage of current equity (or a fixed
  fraction f of the "biggest loss" divisor, in Vince's specific formal sense) per trade, rather than a
  fixed dollar/share/contract count.
- **Mechanism**: Vince's f is the divisor of the perceived biggest loss — dollar amount to finance 1 unit
  = Biggest Loss / −f; NOT simply "percentage of account to bet," a distinction Vince corrects directly
  (Vince Ch.1). Percent-of-equity risk stops (Pardo Ch.5) are the simpler, stop-distance-denominated
  cousin of the same idea: risk a fixed % of equity per trade, translated into a stop distance via
  position size.
- **When to use**: as the baseline sizing method for any system without a validated volatility-target or
  Kelly-derived alternative; explicitly requires pairing with an equity-scaling rule (position size grows
  with account equity) — otherwise risk-per-trade silently drifts as equity grows while position size
  stays fixed (Pardo Ch.5).
- **When to avoid**: fixed-fractional sizing at *optimal* f (Vince's specific sense) guarantees a
  historical drawdown of at least f% of equity — trading anywhere near true optimal f without deliberately
  diluting it is explicitly warned against for any real account (Vince Ch.1, "optimal f is like
  plutonium").
- **Common combinations**: pairs with Volatility-Target Sizing and ATR-Based Unit Sizing as three
  competing ways to answer the same "how much" question — a strategy typically picks one primary method
  and may use a second as a cap/floor.
- **Common mistakes**: conflating Vince's f with "percent of account" is explicitly named as a common
  trader error (Vince Ch.1); using a naive Kelly-from-averages estimate instead of the true optimal-f
  search is a second explicitly named, costly error (Vince Ch.1, §1.3 example: f=.16 from averages vs.
  true optimal f=.24 — a 297% TWR difference over 999 trades).
- **Source**: Vince Ch.1; Pardo Ch.5. Full formula: `10_position_sizing.md` §1.

### Pattern: Volatility-Target / Vol-Parity Sizing

- **Purpose**: size positions (or portfolio-level leverage) so that realized volatility tracks a chosen
  target, rather than letting volatility float with whatever the market happens to be doing.
- **Mechanism**: Volatility Factor (VF) = Target Volatility / Actual (measured) Volatility; scale positions
  up when VF>1 (actual below target), down when VF<1 — applied at the portfolio level with a threshold
  rule (only rebalance when VF differs ≥20% from the currently-applied factor, to avoid churn) (Kaufman
  Ch.24). At the multi-asset level, Equal-Risk/"volatility parity" weighting allocates inversely to each
  asset's volatility (a 4%-vol asset gets 20% weight, a 1%-vol asset gets 80%, in Kaufman's worked
  example) (Kaufman Ch.24).
- **When to use**: portfolio-level engineering is documented as a genuine, distinct source of return
  separate from signal quality — a real 29-year world-futures-portfolio case study improved AROR from
  8.7% to 14.3% (a 64% improvement) at equal risk purely by adding volatility stabilization, with no
  change to the underlying trading signals (Kaufman Ch.24).
- **When to avoid**: stabilization lags in a fast-changing volatility regime — realized volatility runs
  above target during a rising-volatility regime and below target during a declining one (Kaufman Ch.24).
  Kaufman's stated practical target range for stock/futures portfolios is 6-8% typical, with 16%+
  considered dangerous — explicitly NOT validated for crypto in the source (Kaufman Ch.23). This project's
  own champion strategy (TrendVolTarget, see MEMORY.md) uses a 40% target, far outside this range; the
  source material does not resolve whether that is proportionally reasonable given crypto's higher
  baseline volatility or genuinely far more aggressive — an explicitly unresolved gap, not a validated
  choice.
- **Common combinations**: pairs directly with the ATR-Based Volatility Regime Filter (Volatility Filters,
  above) as the sizing-side counterpart to the same filtering-side idea; also pairs with Equal-Risk
  portfolio weighting for multi-asset books.
- **Common mistakes**: rebalancing on every small VF fluctuation instead of using a threshold — this is
  the specific switching-cost problem Kaufman's 20%-threshold rule is designed to solve (Kaufman Ch.24).
  Applying a regulatory exposure cap (e.g., UCITS 2.5x equity) *before* volatility stabilization rather
  than after — the correct order is stabilize-then-cap (Kaufman Ch.24).
- **Source**: Kaufman Ch.23-24. Full formula: `10_position_sizing.md`, `06_volatility.md`
  (Position Sizing and Leverage via Volatility section).

### Pattern: ATR-Based Unit Sizing

- **Purpose**: size a position so that a fixed dollar/percentage risk corresponds to a volatility-scaled
  price distance, rather than a fixed number of shares/contracts.
- **Mechanism**: the Turtles' canonical version — L = a 20-day ATR-based volatility measure converted to
  dollars via the market's big-point-value; risk is calibrated so that 2L corresponds to a fixed 2% of
  portfolio, with position size set to equalize dollar-volatility exposure across markets (Kaufman Ch.5).
  Pardo's simpler version: stop distance = a multiple of N-day average daily range, e.g., 3-day avg range
  5.55 pts → stop at entry − 5.55 (Pardo Ch.5).
- **When to use**: whenever cross-market or cross-instrument comparability of risk matters — ATR-based
  unit sizing is explicitly the mechanism the Turtles used to make position sizes comparable in risk
  terms across very different markets (currencies, metals, grains) simultaneously (Kaufman Ch.5).
- **When to avoid**: Pardo's stated rationale ("it will adjust as volatility expands and contracts,"
  Pardo Ch.5) is also its risk — a volatility spike immediately before entry can produce an oversized
  stop distance and correspondingly undersized position if not bounded.
- **Common combinations**: this is the entry-side twin of ATR-as-stop-distance (ATR Usage Patterns below)
  — the same ATR reading typically drives both the stop placement and the position size in one calculation,
  which is precisely why they must be documented as related-but-distinct uses of one indicator.
  Also combines with the Turtles' pyramiding rule (below) for compounding.
- **Common mistakes**: the exact Turtles loss-threshold multiple and 4-tier position-cap structure are
  explicitly not recoverable from the source (embedded-graphic gap) — do not assume a specific numeric
  value not independently derived and tested.
- **Source**: Kaufman Ch.5; Pardo Ch.5. Full formula: `10_position_sizing.md`, `06_volatility.md`.

### Pattern: Kelly / Optimal-f-Derived Fractional Sizing

- **Purpose**: derive a theoretically growth-maximizing bet size from a strategy's return distribution
  (mean/variance, or full empirical trade distribution), then deliberately dilute it for practical use.
- **Mechanism**: five independent treatments converge on the same "ceiling, not target" conclusion.
  Vince's empirical optimal-f search maximizes the geometric mean (TWR) over the actual trade-P&L
  sequence (Vince Ch.1); Chan's single-strategy Kelly fraction f=m/s² (mean over variance, not mean over
  volatility — an explicitly flagged point of confusion, Hilpisch also notes this distinction) derives
  from a Gaussian-return assumption (Chan Ch.6); Chan explicitly recommends half-Kelly in practice.
  Hilpisch's own worked code recommends half-Kelly independently. Pardo names Kelly/Optimal-f among four
  position-sizing methods without the same explicit "ceiling not target" framing as the other three —
  noted so as not to overstate cross-book agreement.
- **When to use**: whenever a strategy has enough trade history (or a confidently-estimated mean/variance)
  to compute a Kelly fraction, as an upper bound to check ad hoc sizing against — not as the sizing rule
  itself.
- **When to avoid**: trading at or near true optimal f, per Vince's own explicit empirical claim, produces
  historical drawdowns in the 30-95% equity-retracement range and requires "enormous discipline" most
  traders cannot emotionally sustain (Vince Ch.1). A negative-expectation game has no viable Kelly fraction
  at all — the best bet is no bet (Vince Ch.1). Naively averaging win/loss sizes into the classic Kelly
  ratio formula (rather than running the true TWR-maximizing search) is explicitly named as a common,
  costly trader mistake (Vince Ch.1).
- **Common combinations**: pairs with Fixed-Fractional Sizing as the "compute Kelly, then trade a fraction
  of it" workflow; the Fundamental Equation of Trading (G² = A² − SD², Vince Ch.1) is the general lens for
  evaluating whether any sizing/stop change is a genuine improvement or just added variance.
- **Common mistakes**: see `18_common_failure_modes.md` §2 (Martingale/anti-Martingale sizing failure) and
  §9 (Overleveraging blowups) for the source-documented failure modes of over-aggressive Kelly-adjacent
  sizing.
- **Source**: Vince Ch.1, Ch.3-5; Chan Ch.6; Hilpisch (Risk_Management.md); Pardo Ch.5. Full formula:
  `10_position_sizing.md` §1-2.

### Pattern: Pyramiding / Scaling Rules

- **Purpose**: add to (scale in) or reduce (scale out) an existing position as it moves favorably, rather
  than committing full size at entry and holding a fixed size until exit.
- **Mechanism**: the Turtles' compounding rule — add another unit (or ½ unit) per additional L of
  favorable movement from entry, up to 5 units, with stops recalculated to 2L from the *most recent*
  entry once a second unit is added, so total trade risk stays constant regardless of how many units are
  held (Kaufman Ch.5). Pardo's generic scale-in/scale-out: add 1 unit per $1,000 of open profit gained (up
  to a cap on the oldest lot), then scale out 1 unit per additional $1,000 gained thereafter (Pardo Ch.5).
  Kase's DevStop ties a graduated 3-unit position to 3 stop levels, removing one unit per level crossed —
  a scale-out-on-adversity variant rather than scale-in-on-strength (Kaufman Ch.18).
- **When to use**: trend-following systems specifically designed to capture a fat right tail (a small
  number of very large winners) benefit from adding to winners, since the goal is maximizing exposure to
  the rare large move, not just holding a static initial size.
- **When to avoid**: Pardo notes scaling in/out is more commonly a discretionary technique, though equally
  implementable mechanically (Pardo Ch.5) — a system without disciplined stop recalculation at each add-on
  risks silently growing total trade risk beyond the intended level.
- **Common combinations**: pairs directly with ATR-Based Unit Sizing (the L-unit is itself an ATR-derived
  measure) and with Trend-Break/Trailing-Stop exit structures (the stop must ratchet with each add-on to
  keep total risk constant).
- **Common mistakes**: failing to recalculate the stop distance from the *most recent* entry after each
  add — the Turtles' explicit design point is that total risk stays constant at each pyramiding stage;
  omitting this recalculation lets risk compound silently alongside position size.
- **Source**: Kaufman Ch.5, Ch.18; Pardo Ch.5. Full formula: `10_position_sizing.md`, `09_exits.md` §2.

---

## ATR Usage Patterns

ATR (Average True Range) recurs across four **distinct** uses in the source material — distinct enough
that conflating them is itself a documented failure mode. They are separated explicitly here even though
they share one underlying indicator.

### Sub-pattern: ATR as Stop Distance

- **Purpose**: place a stop a volatility-scaled distance from entry, so the stop naturally widens in
  volatile conditions and tightens in quiet ones, rather than using a fixed dollar/point distance.
- **Mechanism**: stop = entry ± k×ATR(n); the Turtles use k=2 (as "2L"); Bookstaber's construction uses
  k≈2-3 (the two Kaufman chapter citations of the same system differ, 2.0 vs. 3.0, and are preserved
  unreconciled in the source, Kaufman Ch.8 vs. Ch.20); Pardo's volatility risk stop uses an N-day average
  range multiple directly (Pardo Ch.5).
- **When to use**: as the default stop-distance method whenever a fixed-dollar stop would need per-market
  or per-regime re-tuning; explicitly preferred by both Kaufman and Pardo over fixed-dollar stops for this
  reason.
- **When to avoid**: a stop must be far enough from price to avoid triggering on ordinary noise — an
  ATR-derived stop that is too tight (small k) suffers the identical problem a fixed-dollar stop would.
- **Source**: Kaufman Ch.5, Ch.8, Ch.20, Ch.23; Pardo Ch.5. Full formula: `09_exits.md` §4.

### Sub-pattern: ATR as a Sizing Denominator

- **Purpose**: convert a volatility measure directly into a position-size divisor, so dollar risk per
  trade is held constant across markets/instruments with very different price scales and volatility.
- **Mechanism**: this is the same L-based calculation as ATR-Based Unit Sizing above — ATR (converted to
  dollars via big-point-value) is the denominator that determines how many units a fixed risk budget
  buys.
- **When to use / avoid**: see ATR-Based Unit Sizing above — this sub-pattern IS that pattern, listed here
  again only to make explicit that "ATR as stop distance" and "ATR as sizing denominator" are two
  different jobs the same number does simultaneously in most worked systems (Kaufman Ch.5's Turtles
  system uses the identical L both ways at once).
- **Source**: Kaufman Ch.5. Full formula: `10_position_sizing.md`.

### Sub-pattern: ATR as a Volatility Regime Filter

- **Purpose**: use the *level* (not the direction) of ATR to gate whether a trade should be taken at all —
  a distinct job from either stop-placement or sizing.
- **Mechanism**: the quantified spike-detection rule and volatility-filtered key-reversal-day rule both
  gate a pattern-based entry behind an ATR-multiple threshold (k>0.75 recommended for spike detection,
  1.5× the 20-day ATR for the key-reversal filter) — adding this filter "markedly improved" a basic
  key-reversal test on heating oil in Kaufman's own spreadsheet test (Kaufman Ch.3). See also the
  Absolute/Relative Volatility Filter patterns above, which are the generalized form of this same idea.
- **When to use / avoid**: see Volatility Filters section above.
- **Source**: Kaufman Ch.3. Full formula: `06_volatility.md`.

### Sub-pattern: ATR as a Trailing-Stop Mechanism

- **Purpose**: ratchet a stop upward (for longs) using ATR as the offset from the best price reached
  during the trade, rather than a fixed percentage trail.
- **Mechanism**: volatility-based trailing stop = highest price reached − k×ATR (Kaufman Ch.23); closer
  when volatility is low, farther when high. Kase's DevStop is a more elaborate tiered version: three
  stop levels each built from a 2-day ATR minus a multiple of that ATR's own standard deviation, with
  position reduced by one unit per level crossed (Kaufman Ch.18). Wilder's Parabolic SAR is the closest
  documented analogue to a "Chandelier Exit" in this source material, though the specific named
  "Chandelier Exit" construction (highest-high minus N×ATR, Chuck LeBeau) does not appear verbatim
  anywhere in the extraction — flagged explicitly as absent, not merely thin, in `09_exits.md` §3.
- **When to use / avoid**: see ATR Stops section of `09_exits.md` §4 for the full taxonomy including the
  documented "which stops work" ranking (Kaufman's own judgment: volatility-adaptive stops are "most
  likely to work," more so than fixed-dollar/percentage stops; trailing stops generally are "the most
  practical," Kaufman Ch.23).
- **Common combinations across all four ATR sub-patterns**: a single system frequently uses ATR for two or
  three of these jobs simultaneously (the Turtles use it for sizing AND stop distance; the Directional
  Parabolic System uses it for both regime filtering, via ADX, AND trailing-stop initialization) — the
  point of separating them explicitly in this file is that a strategy author must decide, for *each* ATR
  reference in a system, which of these four jobs it is doing, since the right parameterization (lookback,
  multiplier) differs by job even when the underlying ATR calculation is shared.
- **Common mistakes**: reusing one ATR calculation/parameter set across multiple jobs (sizing, stop,
  regime filter) without checking whether the same lookback/multiplier is actually appropriate for each —
  the sources use different multipliers for different jobs even within the same named system (e.g., the
  Directional Parabolic System's ATR-based SAR initialization (length 3, factor 1.5) is a different
  parameterization from the ADX regime-gate it's paired with, Kaufman Ch.9).
- **Source**: Kaufman Ch.9, Ch.17, Ch.18, Ch.23. Full formula: `09_exits.md` §2-4.

---

## Adaptive Smoothing Patterns

### Pattern: Efficiency-Adaptive Smoothing Constant (KAMA/VIDYA/FRAMA-style)

- **Purpose**: the general pattern of letting a moving average's own responsiveness (smoothing constant)
  adjust automatically to how "trending vs. noisy" the market currently is, rather than fixing a single
  calculation period for all conditions.
- **Mechanism (generic skeleton shared by all named variants)**: `Trendt = Trendt-1 + SC × (Ct −
  Trendt-1)`, where SC is recomputed every bar from some 0-1 (or rescaled) noise/efficiency measure, using
  a fast/slow-end interpolation: `SC = [measure × (fastest SC − slowest SC) + slowest SC]²` (KAMA's
  specific form, Kaufman Ch.17). What differs across named variants is only **which noise/efficiency proxy
  drives SC**:
  - **KAMA** (Kaufman): the Efficiency Ratio (net change / sum of absolute changes) — squaring the SC
    components pushes the slow end to an extremely unresponsive ~900-period-equivalent and the fast end to
    a ~4-period equivalent (Kaufman Ch.17).
  - **VIDYA** (Chande): relative volatility — ratio of short-term (9-day) to long-term (30-day) standard
    deviation of closing prices scales a base 0.20 smoothing constant; higher relative volatility → slower
    trend (Kaufman Ch.17).
  - **Correlation-Coefficient-driven** (Chande): r² of price against a linear time index used directly as
    SC — near 1 in a strong trend, near 0 in a non-trending regime.
  - **MAMA/FAMA** (Ehlers): phase-rate-of-change based adaptive speed; FAMA is the slowest/fewest-
    false-signal variant of six adaptive methods compared, MAMA the fastest (~2x FAMA's speed).
  - **FRAMA** (Ehlers): fractal dimension of price (self-similar "roughness," the coastline-measurement
    analogy) as the adaptivity proxy.
  - **Adaptive RSI/Adaptive Stochastic**: rescale any bounded oscillator (0-1, ±1, 0-100, ±100) into a
    valid SC using the same KAMA-style fast/slow-end mechanism — a generalization showing this is a
    reusable *skeleton*, not a fixed indicator.
  - **Dynamic Momentum Index** (Chande/Kroll): a variable-length RSI whose period lengthens as volatility
    declines and shortens as volatility rises around a 14-day pivotal period — an internal inconsistency
    in the source's stated formula direction is flagged and preserved verbatim in `13_indicator_reference.md`
    rather than silently corrected.
- **When to use**: any situation where a single fixed calculation period is a compromise between fast
  response (whipsaw-prone) and slow reliability (laggy) — the adaptive skeleton lets the same trendline
  serve both roles depending on conditions, without manual regime detection.
- **When to avoid**: Kaufman's own explicit caveat — "adaptive techniques can improve on standard trend
  calculations but cannot solve all problems" (Kaufman Ch.17). Adaptive systems are built on abundant
  medium/low-volatility test data but comparatively little very-high-volatility data (which occurs less
  often and for shorter durations) — behavior in rare extreme regimes is inherently less validated
  (Kaufman Ch.17). KAMA outperformed VIDYA and Correlation-Coefficient-driven variants in Kaufman's own
  comparative test (fewer whipsaws, higher win rate); VIDYA in particular traded far more often (594 avg
  trades vs. KAMA's 134), diluting per-trade edge once costs are applied — the choice of which noise proxy
  drives the adaptivity is not interchangeable in practice even though the skeleton is shared.
- **Common combinations**: because any exponential-smoothing-based adaptive trend technically can flip
  direction on any price penetration even during a near-zero-SC "sideways" phase, Kaufman gives two
  explicit whipsaw-control filters that should be paired with any adaptive smoothing pattern: (1) a small
  band (e.g., f=0.01 × the 20-day SD of the trendline's own period-to-period changes) that must be
  penetrated before a direction change counts; (2) require the trendline to move away from its most recent
  extreme by a fixed amount F before signaling — Kaufman's own testing found option (2) the better choice
  (Kaufman Ch.17). Adaptivity-as-a-process (periodic walk-forward re-optimization rather than a
  continuously-varying constant) is presented as a related but distinct implementation of the same
  underlying idea (Kaufman Ch.17) — see `14_backtesting_and_validation.md` for the walk-forward-friendly
  parameterization pattern under Other Composable Patterns below.
- **Common mistakes**: conflating noise (the ER/efficiency proxy) with volatility (VIDYA's proxy) as
  though they measure the same thing — they are explicitly different, and the choice of proxy changes the
  resulting adaptive trend's behavior materially (Kaufman Ch.1, Ch.20). Omitting the whipsaw filter
  entirely and trading the raw adaptive-trend cross, an explicitly named common mistake for KAMA
  specifically (`13_indicator_reference.md`).
- **Source**: Kaufman Ch.17 (KAMA, VIDYA, Correlation-Coefficient SC, Adaptive RSI/Stochastic, DMI);
  citing Chande and Ehlers. Full formula: `13_indicator_reference.md` (KAMA/VIDYA/FRAMA/MAMA-FAMA entries),
  regime framing in `07_market_regimes.md` §1.4.

### Pattern: Adaptivity as a Re-Optimization Process (not a formula)

- **Purpose**: achieve the same "adjust to current conditions" goal as a continuously-varying smoothing
  constant, but via periodic re-testing/re-optimization on recent data rather than an embedded formula.
- **Mechanism**: the re-test window can be fixed (e.g., rolling N-day walk-forward) or triggered visually/
  by rule (when the market changes pattern, becomes more volatile, undergoes a price shock, or reaches new
  highs/lows) (Kaufman Ch.17).
- **When to use**: whenever a strategy's parameters are believed to need periodic refreshing but a
  continuous adaptive-smoothing-constant formula is either unavailable or judged too reactive.
- **When to avoid**: faster reaction (a shorter re-test window) means less data to validate the
  re-optimization decision — an explicit data-sufficiency-vs-responsiveness trade-off with no universal
  answer given (Kaufman Ch.17).
- **Common combinations**: this is the conceptual bridge between the Adaptive Smoothing patterns above and
  the walk-forward-friendly parameterization pattern in Other Composable Patterns below — the same
  "adapt over time" goal, addressed either continuously (a formula) or discretely (a re-optimization
  schedule).
- **Source**: Kaufman Ch.17. Cross-ref `14_backtesting_and_validation.md`.

---

## Confirmation Logic

### Pattern: N-of-M Independent Signal Agreement (2-of-3, 3-of-3)

- **Purpose**: require multiple, ideally independent, signal types to agree before acting, trading signal
  frequency for reliability.
- **Mechanism (worked concrete examples across sources)**:
  - **Dunnigan's Thrust Method**: requires 2 of 4 named swing-pattern conditions, confirmed the next day by
    a volatility-scaled "thrust" — an explicit 2-of-4-then-confirm structure (Kaufman Ch.4).
  - **Rattlesnake Breakout**: 3-of-3 — Bollinger squeeze inside a Keltner Channel AND Chaikin Oscillator
    below zero, THEN Chaikin crosses above zero (Kaufman Ch.8).
  - **Cambridge Hook**: outside reversal day + RSI>60% + rising volume AND open interest — a 4-condition
    stack for a high-probability reversal call (Kaufman, Indicators.md).
  - **Modified 3-Crossover Model**: a third, faster confirming trendline must agree with the direction
    about to be traded before entry (Kaufman Ch.8).
  - **Kestner's Oscillator + ADX Filter**: an MA-difference oscillator signal is only acted on when an
    independent ADX-based no-trend condition also holds (Kaufman Ch.9).
- **When to use**: whenever a single indicator's false-signal rate is judged too high on its own — adding
  independent (not redundant) confirmations reduces false positives at the cost of missed true positives
  and later entries.
- **When to avoid**: Pardo's explicit overfitting warning applies directly here — "as the number and
  complexity of trading filters increases, so does the difficulty of coding/testing... the likelihood of
  overfitting also rises with the number of filters," to the absurd limiting case of a unique filter per
  historical bar (a perfect historical fit with zero forward-looking value) (Pardo Ch.5). Kaufman
  independently gives the same warning in different words (Ch.1, Trading System Development Guidelines):
  excessive filtering causes either overfitting or a system that generates no trades at all.
- **Common combinations**: this pattern is the umbrella under which Multi-Timeframe Agreement, Volume
  Confirmation, and Breakout Confirmation (N-bar, multi-box) all sit as specific instances — a strategy
  author choosing "how many confirmations" is making one decision that manifests differently depending on
  which pattern families are being combined.
- **Common mistakes**: adding filters that are not actually independent (e.g., two indicators both
  derived from the same underlying price series in similar ways) provides the *appearance* of confirmation
  without the actual variance-reduction benefit of a genuinely independent second opinion. Adding filters
  purely because they improve an in-sample backtest, without an ex-ante rationale for each one — the
  Pardo/Kaufman overfitting warnings above apply directly. See `18_common_failure_modes.md` §1
  (Overfitting) and §7 (Peak-Parameter Fragility).
- **Source**: Kaufman Ch.4, Ch.8, Ch.9; Pardo Ch.5. Full formula/system detail: `08_entries.md` §4, §6.

### Pattern: Oscillator-Confirms-Trend

- **Purpose**: use a bounded oscillator (RSI, stochastic, momentum) as a secondary confirmation that a
  trend signal is not occurring against exhausted/overextended conditions, rather than trading the trend
  signal alone.
- **Mechanism**: in a trending market, oscillators tend to "stay pinned at the top or bottom of their
  range" (Kaufman Ch.9) — the Trend-Adjusted Oscillator (TAO) explicitly corrects for this bias by
  shifting the oscillator's value by the amount its own moving average deviates from the theoretical
  midpoint, at the stated cost of losing some smaller overbought/oversold signals (Kaufman Ch.9, Ch.17).
- **When to use**: whenever a trend signal's timing (not direction) benefits from an independent
  overbought/oversold read, e.g., waiting for a pullback-driven oscillator reset before adding to a trend
  position.
- **When to avoid**: an oscillator pinned at an extreme in a genuine strong trend is not a reversal signal
  — treating it as one is a direct, named misuse the TAO construction exists specifically to correct.
- **Common combinations**: pairs with Multi-Timeframe Agreement (oscillator on the fast timeframe, trend
  filter on the slow one) and with the Fisher Transform's stated use as a mean-reversion-specific
  signal (sharp peaks in the transformed series are "particularly good for mean-reversion trading,"
  contrasted with indicators that plateau at extremes while price continues in the same direction —
  Ehlers, Kaufman Ch.11).
- **Common mistakes**: applying an oscillator confirmation with no minimum volatility threshold — Kaufman
  explicitly recommends a minimum price-volatility threshold before trusting Hilbert/Fisher-Transform
  signals, since during low-volatility periods the indicator still shows relative highs/lows without
  adequate underlying profit opportunity (Kaufman Ch.11).
- **Source**: Kaufman Ch.9, Ch.11, Ch.17. Full formula: `13_indicator_reference.md`, `05_momentum.md`.

### Pattern: Volume-Confirms-Price

- **Purpose**: use volume (or a volume-derived oscillator) as an independent confirmation axis for a
  price-based signal, on the premise that genuine directional moves are usually accompanied by
  participation, while thin/false moves are not.
- **Mechanism**: see Volume Confirmation under Breakout Confirmation above (Rattlesnake Breakout's Chaikin
  Oscillator leg; Crabel's opening-range-breakout preceding-pattern filters). On-Balance True Range
  (Bierovic) is a related volume-analogue construction that substitutes True Range for volume inside OBV's
  cumulative up/down-day logic, then smooths and compares via crossover — explicitly framed as helping
  separate high- and low-volatility conditions rather than as a pure volume-confirmation tool per se
  (Kaufman Ch.20).
- **When to use / avoid / mistakes**: identical considerations to Volume Confirmation above — this entry
  exists to make explicit that "volume confirms price" and "volume confirms breakout" are the same
  underlying pattern applied at different signal-generation stages (setup vs. trigger).
- **Source**: Kaufman Ch.8, Ch.16, Ch.20. Full formula: `13_indicator_reference.md`.

---

## Exit Structures

Framed here explicitly as **composable, swappable modules** — Kaufman's load-bearing rule (Ch.23) states
these are matched to *strategy type*, not freely interchangeable: "Stop-loss: works for trending systems
in trending markets; bad for non-trending markets or mean-reversion systems. Profit-taking: works for
mean-reversion/short-term strategies; bad for trending markets or long-term trend strategies." Chan
provides a second, independent (non-strategy-type-based) axis for the same question: a stop-loss is
beneficial in a *believed* momentum regime and actively harmful in a *believed* mean-reverting regime,
regardless of the strategy's formal type label (Chan Ch.6-7) — the two axes are not reconciled in the
source material and are preserved here as distinct, both load-bearing considerations.

### Pattern: Trend-Break Exit

- **Purpose**: exit (or reverse) purely on the trend indicator's own direction change, without a separate
  price-based or volatility-based stop.
- **Mechanism**: the lowest-frequency, highest-lag member of the same three/four-family ranking used for
  entries (Kaufman Ch.8) — exits only once the trendline's own direction reverses. Two-trendline exit
  variants determine whether this reverses immediately (Rule Set 1) or exits to flat first (Rule Sets 2-3,
  requiring price/trend agreement before re-entering) (Kaufman Ch.8).
- **When to use**: pure trend-following systems whose profitability depends on capturing the fat right
  tail of trade outcomes — Kaufman's explicit, repeated warning is that adding a stop-loss or profit
  target to a basic trend-cross system reduces or eliminates its ability to capture that fat tail (Kaufman
  Ch.8).
- **When to avoid**: a very slow trendline (e.g., 200-day MA) can lag a genuine fundamental reversal
  significantly, giving back a large unrealized gain before the mechanical trend-break fires — Kaufman's
  "techno-fundamental" hybrid explicitly overrides the mechanical rule when a clear fundamental/policy
  driver visibly reverses, with the explicit caveat that this only works when the fundamental driver is
  genuinely clear (not usually knowable in real time) (Kaufman Ch.8).
- **Common combinations**: pairs naturally with Pyramiding (the same trend-break signal that would exit a
  static position also determines when to stop adding units) and is the natural default exit for any
  system built primarily on the Trend Filters section above.
- **Common mistakes**: comparing trend direction across a sequence of calculation periods (e.g., 1 through
  18+ days) before trusting a break signal — an erratic short-end sequence (very short calc periods
  flipping on single-day noise) should not be trusted as a genuine trend change; only a smooth, progressive
  sequence change across the range is reliable (Kaufman Ch.8).
- **Source**: Kaufman Ch.8, Ch.14. Full formula: `09_exits.md` §6.

### Pattern: Fixed/Volatility-Scaled Stop

- **Purpose**: cap the loss on an individual trade at a predetermined distance, independent of the
  trend/signal itself.
- **Mechanism**: see the full stop-loss taxonomy — chart-based, volatility-based (ATR/Dev-Stop), percentage-
  of-price-change (Parabolic-style), swing-based, channel/extreme-based (Kaufman Ch.23's five numbered
  approaches). Kaufman's own explicit ranking: volatility-adaptive stops (std-dev/Kase) are "most likely to
  work," support/resistance-based stops "also good," trailing stops "the most practical" (Kaufman Ch.23).
- **When to use / avoid**: see Kaufman's strategy-type/tool-fit rule above the section header — stop-losses
  are documented as working well for trending systems in trending markets, poorly for non-trending markets
  or mean-reversion systems.
- **Common combinations**: pairs with ATR-Based Unit Sizing (the same ATR reading often drives both);
  pairs with Windfall-Profit Management (a large unrealized profit from a shock is a distinct, asymmetric
  case — exit immediately on a shock-driven windfall, but hold through a shock-driven loss expecting
  reversal, Kaufman Ch.22).
- **Common mistakes**: the random-walk baseline diagnostic — (number of times a stop triggers) ×
  (stop distance) is roughly constant for random price data — is Kaufman's explicit test for whether a
  stop rule adds genuine information versus being an artifact of placement distance (Kaufman Ch.23). A
  stop rule that doesn't beat this baseline isn't earning its keep.
- **Source**: Kaufman Ch.23; Pardo Ch.5. Full formula: `09_exits.md` §1-4.

### Pattern: Trailing Stop

- **Purpose**: lock in progressively more of an open profit as a trade moves favorably, without a fixed
  predetermined exit price.
- **Mechanism**: fixed-percentage trailing stop (e.g., 3% below the highest close reached); volatility-
  based trailing stop (highest price − k×ATR, closer in low vol, farther in high vol); breakeven lock-in
  (move stop to entry once a profit threshold is reached, with the explicit risk that doing so too soon
  lets ordinary noise trigger it prematurely) (Kaufman Ch.23). Elder's Triple-Screen 3-step progression —
  initial chart-based stop, then breakeven, then trail to protect 50% of peak open profit — is
  specifically framed as "a general-purpose, reusable risk template" (Kaufman Ch.19).
- **When to use / avoid**: see Fixed/Volatility-Scaled Stop above — same strategy-type-fit rule applies.
- **Common combinations**: pairs with Pyramiding (stop recalculated from the most recent entry each time a
  unit is added, keeping total trade risk constant); the Kase DevStop's tiered 3-level version pairs
  directly with 3-unit position construction (scale out one unit per level crossed) — see Pyramiding /
  Scaling Rules above.
- **Common mistakes**: activating a breakeven-lock too early, letting ordinary noise stop out a position
  that would otherwise have continued favorably (Kaufman Ch.23) — an explicitly named risk of the
  breakeven-lock sub-pattern specifically.
- **Source**: Kaufman Ch.19, Ch.23. Full formula: `09_exits.md` §1, §3.

### Pattern: Time-Based Exit

- **Purpose**: exit after a fixed holding period (or by a fixed clock time, for intraday systems)
  regardless of price/indicator state.
- **Mechanism**: Nofri's Congestion-Phase System uses a pure 1-day hold with no stop-loss at all — the
  time exit substitutes entirely for a price-based stop (Kaufman Ch.4). Arnold's Outside Day with Outside
  Close closes 3 days after entry (tested range 1-5 days) regardless of whether a stop has fired (Kaufman
  Ch.4). Intraday systems commonly close all positions a fixed interval before session end (Meyers'
  Adaptive Range Breakout: 5 minutes before close) (Kaufman Ch.17). Kaufman's explicit recommendation is
  to exit ahead of scheduled news events entirely rather than rely on a stop to manage the event-day gap
  risk (Kaufman Ch.14, Ch.16).
- **When to use**: short-holding-period mean-reversion systems where the edge is expected to resolve
  within a known, short window; around known scheduled-news events, as a substitute for a price-based
  stop that could be jumped past by the surprise itself.
- **When to avoid**: Kaufman notes Ch.23's own stop-loss taxonomy does NOT include a distinct time-based
  stop as one of its five numbered adaptive stop-placement categories — time exits appear only as
  system-specific rules scattered across other chapters, which is flagged in the source as a structural
  gap in the book's own organizational treatment, not evidence time exits are unimportant (Kaufman Ch.23,
  per `09_exits.md` §7).
- **Common combinations**: pairs naturally with Mean-Reversion entries (Confirmation Logic / Pullback
  patterns in `08_entries.md`) where the expected reversion has a known short time horizon; pairs with
  news-event avoidance as a category of its own.
- **Common mistakes**: relying on a stop-loss instead of a time-based exit around a scheduled news release
  — a surprise report can jump price past a resting stop and fill at a much worse price than intended
  (Kaufman Ch.14).
- **Source**: Kaufman Ch.4, Ch.14, Ch.16-17. Full formula: `09_exits.md` §7.

### Pattern: Volatility-Scaled Profit Target

- **Purpose**: take profit at a volatility-scaled distance from entry, symmetric in construction to a
  volatility-scaled stop but applied on the favorable side.
- **Mechanism**: profit target = entry ± f×ATR (typical f=3-4 using a 20-day ATR); triggered on the
  intraday high/low but the position is exited on the close after a stop trigger, to allow noise-driven
  recovery (Kaufman Ch.20, Ch.23). Scaling Out (using 3+ targets simultaneously, e.g., 2.0/3.0/4.0×ATR
  bracketing a "best" 3.0 factor) is explicitly framed as an anti-data-mining technique — the average of
  several targets approximates the single best-fit factor without needing to identify it exactly, while
  partial exits reduce exposure (Kaufman Ch.23).
- **When to use**: short-term/mean-reversion strategies, per the strategy-type/tool-fit rule — Kaufman
  states profit targets are essential for short-term trading (price noise reverses fast) but more
  difficult to incorporate into longer-term trend-following without risking the fat tail (Kaufman Ch.23).
- **When to avoid**: long-term trend systems — taking profit at a fixed volatility multiple works directly
  against the goal of capturing the rare, very large winning trade that justifies trend-following's
  asymmetric win/loss shape in the first place (Kaufman Ch.8, Ch.20).
- **Common combinations**: pairs with Scaling-Out (multiple simultaneous targets) as an explicit,
  source-named defense against picking one over-fit "best" factor; pairs with the asymmetric
  windfall-profit rule (exit fully, immediately, on a shock-driven windfall regardless of the normal target
  logic, Kaufman Ch.22).
- **Common mistakes**: "most analysts data mine to find the best [ATR] factor" — Kaufman flags this as a
  self-aware, named overfitting risk specific to single-factor ATR profit targets (Kaufman Ch.23); the
  Scaling-Out technique above is presented as the direct mitigation.
- **Source**: Kaufman Ch.20, Ch.22-23. Full formula: `09_exits.md` §4-5.

---

## Other Composable Patterns

### Pattern: Regime-Switching Between Two Sub-Strategies

- **Purpose**: run two different strategy types (typically trend-following and mean-reversion) and switch
  which is active based on a detected regime, rather than committing to one paradigm across all
  conditions.
- **Mechanism**: the same Efficiency Ratio / noise measure that gates trend-following entries (Trend
  Filters, above) is explicitly framed by Kaufman as also indicating when to switch paradigms — "if
  lengthening the calculation period is not enough to overcome noise, switch to mean reversion, emphasizing
  the shorter holding periods... noise is dominant in the short term and trends in the long term" (Kaufman
  Ch.20). Chan's independent framing arrives at a structurally similar idea from the opposite direction:
  the *same* stop-loss exit mechanism should be applied or withheld depending on the believed regime
  (momentum vs. mean-reverting) of the specific price move in question, not the strategy's nominal label
  (Chan Ch.6-7) — a regime-conditional *rule*, even without formally switching the entire strategy.
- **When to use**: markets/instruments that plausibly cycle between trending and mean-reverting character
  over time (Kaufman's explicit example: emerging markets show clean trends early on, then deteriorate into
  noisier, less trend-following-friendly character as they mature, Kaufman Ch.1).
- **When to avoid**: Chan's explicit, strongly-worded rejection of formal Markov/hidden-Markov
  regime-switching models for actual trading — these assume *constant* transition probabilities at all
  times, giving no actionable signal about *when* a transition is imminent, which Chan calls "generally
  useless for actual trading purposes" (Chan Ch.7). The data-mining/turning-points alternative Chan does
  present (a machine-learning model on candidate predictive variables) carries its own explicit
  data-snooping caveat, admitted by the author as "unavoidable" via "model-category shopping" (Chan Ch.7).
- **Common combinations**: pairs directly with the ER Threshold Gate (Trend Filters) as the specific
  trigger mechanism, and with the regime-conditional stop-loss logic (Exit Structures header note) as a
  lighter-weight, rule-level (rather than whole-strategy-level) version of the same idea.
- **Common mistakes**: assuming a formal statistical regime-detection model provides forward-looking
  warning of an imminent regime change — per Chan's explicit critique, most such models (constant-
  transition-probability Markov models specifically) do not.
- **Source**: Kaufman Ch.1, Ch.20; Chan Ch.6-7. Full detail: `07_market_regimes.md` §1, §5.

### Pattern: Walk-Forward-Friendly Parameterization

- **Purpose**: design a strategy's parameter space so that re-optimization on a rolling/recent window is
  a legitimate, low-risk maintenance process rather than a fresh overfitting exercise each time.
- **Mechanism**: Kaufman's "adaptivity as a process" framing (Adaptive Smoothing Patterns, above) is the
  general version of this idea — a fixed or rule-triggered re-test window, explicitly trading responsiveness
  against the amount of data available to validate each re-optimization decision (Kaufman Ch.17). Pardo's
  parallel material names volatility regime shifts as one of several sources of market-behavior variation
  (alongside seasonality, bull/bear/business cycles, trending-vs-mean-reverting "personalities,"
  multi-timeframe effects, liquidity contraction/expansion) that motivate periodic re-optimization and
  Walk-Forward Analysis specifically as a formal methodology (Pardo Ch.6, Ch.11). Chan's independent,
  non-cross-referenced observation converges on a related point from a data-length angle: because
  financial time series are "famously nonstationary," more historical data does not straightforwardly mean
  a more robust result — only the last ~10 years is generally considered suitable for building predictive
  models, regardless of how much longer history exists (Chan Ch.3).
- **When to use**: any strategy expected to be traded live over a period long enough that market character
  may shift — which is essentially all strategies intended for real deployment, per the regime-shift
  material in `07_market_regimes.md`.
- **When to avoid**: robustness-across-a-parameter-sweep (Kaufman's own preferred diagnostic — e.g., the
  N-day breakout study's finding that 7 of 13 markets were profitable across *all* tested N values, Kaufman
  Ch.5) is a different and complementary check from walk-forward re-optimization; neither substitutes for
  the other, and relying on only one is a documented source of false confidence — see
  `14_backtesting_and_validation.md` and `18_common_failure_modes.md` §7 (Peak-Parameter Fragility).
- **Common combinations**: pairs with the ER-threshold regime gate and with Adaptivity-as-a-Process as
  three different mechanisms addressing the same underlying "markets change over time" problem at
  different levels (continuous formula, discrete re-optimization schedule, and parameter-space design,
  respectively) — a mature strategy design should be explicit about which of the three (or which
  combination) it is relying on.
- **Common mistakes**: treating a single historical parameter-sweep optimum as permanently valid without
  any re-optimization or regime-monitoring process at all — directly contradicted by both Kaufman's and
  Pardo's independent emphasis on periodic re-testing, and by the documented regime-shift case studies in
  `07_market_regimes.md` (decimalization, uptick-rule elimination, seasonal-pattern structural breaks).
- **Source**: Kaufman Ch.17; Pardo Ch.6, Ch.11; Chan Ch.3. Full detail: `07_market_regimes.md`,
  `14_backtesting_and_validation.md`.

### Pattern: Symmetrical vs. Asymmetrical Strategy Construction

- **Purpose**: a design-level choice about whether a strategy's long and short logic (or entry and exit
  logic) mirror each other, independent of which specific patterns above are used for each side.
- **Mechanism**: Pardo's formal definitions — a symmetrical strategy's buy/sell conditions mirror each
  other (e.g., an N-day-high breakout to buy, N-day-low breakout to sell); an asymmetrical strategy uses
  unrelated logic per side (e.g., an N-day-high breakout entry paired with an MA-cross exit) (Pardo Ch.5).
  Most Kaufman named systems (N-day breakout, Donchian channels, two-trendline crossovers) are
  symmetrical/mirror-image by construction; Kaufman explicitly calls out the exceptions when they occur
  (Kaufman Ch.5, Ch.8).
- **When to use**: symmetry simplifies testing and reduces the number of independently-fitted parameters
  (fewer things to overfit); asymmetry can better exploit a genuinely asymmetric market characteristic
  (e.g., a documented upward bias in equity gap behavior, Kaufman Ch.15) that a mirrored rule set would
  miss.
- **When to avoid**: asymmetric designs implicitly double the parameter-fitting surface (long-side and
  short-side logic must each be separately validated) — a design choice that interacts directly with the
  overfitting warnings elsewhere in this file (Confirmation Logic, ATR-target Scaling-Out).
- **Common combinations**: this is an orthogonal design axis to every other pattern in this file — any
  entry pattern, exit structure, or sizing rule can be applied symmetrically or asymmetrically; it is
  listed here as its own pattern because the choice is a distinct, explicit design decision documented
  independently in the sources, not a byproduct of any single other pattern.
- **Common mistakes**: none specifically flagged beyond the general overfitting-surface argument above.
- **Source**: Pardo Ch.5; Kaufman Ch.5, Ch.8. Full detail: `08_entries.md` §1.

---

## Cross-Reference Index (by knowledge_base file)

- `02_trend_following.md` — MA-direction filters, trend systems, Turtles, Donchian family, N-day breakout.
- `04_breakouts.md` — N-bar/multi-box confirmation, point-and-figure mechanics, Renko.
- `06_volatility.md` — all five Kaufman volatility measures, ATR/AV comparison, Bollinger bulge fix,
  volatility-targeting math, VIX systems.
- `07_market_regimes.md` — Efficiency Ratio, KAMA/VIDYA/adaptive-technique regime framing, seasonality,
  cycle analysis, price-shock regimes, Chan's regime-shift vigilance.
- `08_entries.md` — full entry-technique taxonomy: breakout, MA-cross, pullback/retracement, pattern,
  day-trading, multi-timeframe confirmation.
- `09_exits.md` — full stop-loss taxonomy, Kase DevStop, Parabolic SAR, ATR stops, profit-taking,
  trend-break exits, time exits, Pardo's exit/trade-management machinery.
- `10_position_sizing.md` — Optimal f (Vince), Kelly (five treatments), fixed-fractional, ATR-based
  sizing, scenario planning.
- `11_risk_management.md` — risk-of-ruin mathematics, drawdown response.
- `12_portfolio_construction.md` — multi-asset Kelly/covariance allocation, equal-risk weighting.
- `13_indicator_reference.md` — full indicator formula reference (ER, ADX, KAMA/VIDYA/FRAMA/MAMA-FAMA,
  Bollinger, Kase DevStop, etc.).
- `14_backtesting_and_validation.md` — walk-forward methodology, parameter-sweep robustness diagnostics.
- `18_common_failure_modes.md` — overfitting, Martingale sizing failure, price-shock backtest
  contamination, regime-shift strategy death, peak-parameter fragility, overleveraging blowups.

## Notes on Coverage

All eight requested pattern families (Trend Filters, Volatility Filters, Breakout Confirmation, Position
Sizing, ATR Usage, Adaptive Smoothing, Confirmation Logic, Exit Structures) are documented with multiple
distinct patterns each, plus two additional families (Regime-Switching, Walk-Forward-Friendly
Parameterization / Symmetrical-vs-Asymmetrical Construction) added under Other Composable Patterns because
the source material supported them as genuinely separate, reusable design decisions rather than sub-cases
of the requested eight. Breakout Confirmation was, on inspection, somewhat thinner than the other families
in terms of distinct sourced sub-patterns (three clear variants — N-bar, volume, multi-box — plus
retest-before-entry) compared to the richer ATR Usage and Position Sizing families, which each drew on
several independent, fully-worked book treatments (Vince's book in particular is almost entirely about
position sizing, giving that family the deepest source base in this file).
