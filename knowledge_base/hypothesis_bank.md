# Hypothesis Bank

Every distinct backtestable trading hypothesis traceable to the knowledge base (`01_market_structure.md`
through `18_common_failure_modes.md`) and its underlying `Knowledge\` book extractions, organized by
research theme rather than alphabetically. This file is a bridge layer: it names and cross-references
hypotheses, it does not restate formulas — follow the "Suggested indicators" cross-reference into
`13_indicator_reference.md` for the mechanics, and the "Supporting concepts" cross-reference into the
relevant topic file for the reasoning.

**How this file was built**: `16_research_hypotheses.md` supplied the abstract/exploratory research
ideas; every named system scattered across `02_trend_following.md` through `09_exits.md`,
`13_indicator_reference.md`, `15_crypto_specific.md`, `10_position_sizing.md`, and
`12_portfolio_construction.md` supplied the concrete, nameable strategies. Near-duplicate systems
(e.g., three books' versions of "trend + vol-target sizing") are merged into one card with each
variant noted; genuinely distinct variants (e.g., Turtles S1 vs. S2) are kept as separate cards.

**Project-history flags**: where a hypothesis closely matches something this project has already
built and tested (see `research/research_index.md` and `research/strategy_iteration_log.md` at the repo root — the
project's own empirical research history, distinct from the book knowledge below), a line reading
`**Already tested by this project**` names the research/research_index.md hypothesis number and status. A
book hypothesis being already-tested-and-rejected does not mean it is omitted here — the book claim
and the project's empirical test of it are different things, both worth keeping visible.

**Sibling files** (planned, cross-referenced by name even where not yet built): `implementation_patterns.md`
(how to code these up against this project's validator.py), `EDGE_FRAMEWORK.md` (criteria for what
counts as a real edge here), `AI_RESEARCH_PLAYBOOK.md` (process for running a new hypothesis through
the pipeline). Existing siblings: `master_index.md` (alphabetical lookup), `README.md` (front door),
`research/research_index.md` / `research/strategy_iteration_log.md` (this project's own experiment history, repo root).

---

<!-- DIRECTOR-MANDATORY-BEGIN -->
<!--
  Everything between these markers is the Research Director's MANDATORY read of this file.
  The hypothesis cards below the END marker are ON-DEMAND: open a card only when it is a live
  candidate for the cycle being planned. Measured by scripts/check_context_budget.py.
-->

## FAMILY STATUS LEDGER (Meta-Review #1, 2026-07-18 — authoritative closures; Directors must check here before assigning)

Formally CLOSED families (kill condition met at family level; reopening requires the specific new
evidence named in the closure record, never a re-parameterization — see
`research/meta_reviews/meta_review_1.md` §4 for full evidence):

Each row is the **single-line stub** for a closed family. The family's full hypothesis cards were
moved verbatim to `knowledge_base/archive/closed_families.md` on 2026-07-28 (repair item 3) — nothing
was deleted. **This ledger, not the archive, is authoritative for status**: if a row here reopens, the
cards stay in the archive and this row governs.

| Family / theme | Status | Cards | Closure evidence (research_index.md rows) |
|---|---|---|---|
| Mean reversion on crypto OHLCV (all tested timeframes) | **CLOSED** | 17 archived | #2, #3 (negative even in-sample), #8, #13; fees vs reversion amplitude structural |
| Intraday / time-of-day / sub-daily constructions | **REOPENED 2026-07-29** | 4 archived (cards stay archived; this row governs) | Closed on a cost model that overstated achievable perp round-trip cost. Requires re-test at real rates before it may be re-closed — see the reopening note below. |
| Short side / symmetric TSMOM of the champion's gate | **CLOSED** | 1 archived | #16 whipsaw census (median episode 3 bars; 2018's −84% bear → +2.6% gross) |
| BTC-ETH pairs / relative value / rotation / dominance / ratio | **CLOSED** | 4 archived | #18 (no cointegration any window; post-2024 ETF-era break formal, ADF p 0.405) |
| Sleeve sizing refinement (estimator quality AND rebalance granularity) | **CLOSED** | 0 (no book card; champion's own card stays live) | #15 + #19 (efficient frontier from both directions; 25% quantizer is protective) |
| DVOL daily-bar champion modifications | **CLOSED** | 4 archived | #21 (veto, B3a) + #22 (sizing, P2 — VRP positive-carry) |
| Regime-classifier overlay (ER, ADX, MESA, HMM) | **CLOSED** | 4 archived | #30 (post-hoc), #31, #32 (three firing-set concentration failures on the same Oct-2025 boundary across two signals and both threshold types; dataset lacks recent classifier-detectable chop). Reopen ONLY per T-030 §3: window extended ≥6 months past 2026-05-27 with fresh held-out split, OR forward-lane documented in-market chop episode |

### REOPENING (2026-07-29) — intraday / time-of-day / sub-daily

This family was closed on a cost model that **overstated achievable perp round-trip cost by 3x
(taker) to 7.5x (maker)**. Archived runs charged a blended 15 bps/side with zero spread and no
maker/taker distinction — 30 bps round trip. Real OKX regular-tier perp fees are 10 bps round trip
taker, 4 bps maker. Those ratios compare the archived all-in figure against *fee-only* perp rates,
because the old model never separated its fee component; on an all-in basis the current taker model
is 18 bps round trip, so the archived cost was 1.67x too high. **Do not quote 3x/7.5x as an expected
P&L improvement.** See `user_data/research/ARCHIVE_COST_NOTE.md`.

Turnover-heavy constructs are the ones this mispricing hurt most, and this family is the most
turnover-heavy in the bank — so its closure rests on exactly the assumption that was wrong.
**Status: OPEN for re-test at real rates. It may not be re-closed on archived evidence**; a fresh
closure requires a run under the current `COST_MODEL`. No sub-hourly data exists yet, and acquiring
it is an `A-XXX` ops task gated on A-002 (`research/OPS_BACKLOG.md`) — not something a cycle may do.

**Finding #12 (hours 21-22 UTC anomaly) STAYS CLOSED.** Its fee-to-edge ratio improves from 25:1 to
roughly **3.3:1 at real maker rates** — still losing by a wide margin, and the maker path is itself
unproven (no promotion may rest on it; see the manual's cost-model section). The reopening applies to
the family, not to this specific construct: #12 was re-examined and remains rejected on its own
numbers. The statistical finding (t = 2.4-3.0, stable) was never in doubt; its tradeability is.

### CORRECTION (2026-07-21) — the blanket OHLCV closure was retracted

A former ledger row, *"New OHLCV signal-prediction constructs generally | CLOSED | #8 (0/61) +
entire history"*, was **removed as overclaiming**. An audit counted **83 named cards in sections 1-9;
only 20 (24%) carry an explicit "Already tested by this project" line.** Row #8 was a *generic*
autonomous sweep; generalising it to close the other 76% by inference was too strong — notably for
statistical/ML classifiers (a different paradigm, never coded here), idiosyncratic named systems
never implemented, and portfolio-construction hypotheses (never covered by that row).

**Operative rule: before treating any named card as closed, check for its own explicit "Already
tested by this project" line. Do not infer closure from row #8.** What remains narrowly closed is the
~20 tested entries plus the ledger rows above.

Full text: `knowledge_base/archive/closed_families.md`, appendix.

Still OPEN (revised): H-ForwardParity (forward dry-run evidence — the highest-EV lane);
portfolio/allocation layer above the sleeve (one interior point validated, H-TailAlloc #20;
dynamic-w parked as a new mechanism); the "Frontier Hypotheses" section at the end of this file
(new-data-axis and forward-contingent entries added by Meta-Review #1); **and, per the correction
above, the ~63 named hypotheses in sections 1-9 below with no explicit "Already tested" line** —
these require individual evaluation on their own falsification/orthogonality merits, not blanket
dismissal.

Individual cards below retain their original text; where a card belongs to a CLOSED family, this
ledger overrides any "open/untested" wording in the card.

---

<!-- DIRECTOR-MANDATORY-END -->

## 1. Trend-Following Hypotheses

### N-Day / Channel Breakout Trend Family

**Description**: Buy when price breaks above its own N-day rolling high, sell/short on a break below
the N-day rolling low; trend continues until the opposite channel breaks. Includes Donchian's 4-Week
Rule, Donchian's 20/40-day and 5-and-20-day MA-hybrid variants, plain N-day breakout, and
volatility-adaptive N (shrinking N as relative volatility rises).
**Supporting concepts**: trend persistence / conservation-of-capital (`02_trend_following.md`),
market noise (`01_market_structure.md`).
**Suggested indicators**: N-day rolling high/low, ATR-based adaptive N — see `13_indicator_reference.md`
("N-Bar/N-Day Breakout").
**Expected market conditions**: sustained trending regimes; Kaufman's own 2000-2017 cross-market sweep
found average best N≈93 days with ~79% of tested combinations profitable — evidence of a broad,
non-fragile plateau rather than a fragile peak.
**Expected weaknesses / known failure modes**: risk (entry-to-reversal distance) grows with N; fails in
narrow multi-year ranges and in crisis-volatility regimes; see `18_common_failure_modes.md` §7
(peak-parameter fragility) for why a too-fine N-sweep can look falsely robust.
**Related hypotheses**: The Turtles (S1/S2, below) are this family's most fully-specified historical
instance; Moving-Average Crossover Systems is the smoothed-trendline analogue; Opening Range Breakout
is this family's intraday cousin.
**Source attribution**: Kaufman Ch.5, Ch.8 (Donchian, mid-1970s; Seidel & Ginsberg 1983); `02_trend_following.md`,
`04_breakouts.md`, `08_entries.md`.
**Already tested by this project**: see research/research_index.md #2 (Donchian, 1h) — FAIL, collapsed OOS.

### The Turtles — System 1 (S1)

**Description**: Enter long on a 20-day high breakout (short on 20-day low), exit on the opposite
10-day extreme; skip a signal if the prior S1 trade was profitable, unless that loss exceeded an
ATR-scaled threshold.
**Supporting concepts**: trend persistence, volatility-normalized risk (`02_trend_following.md`,
`10_position_sizing.md`).
**Suggested indicators**: 20-day/10-day rolling high-low, ATR-based volatility measure "L" — see
`13_indicator_reference.md` ("N-Day Breakout", "Average True Range").
**Expected market conditions**: fast-turning trending markets; Kaufman's own copper backtest
(1980-2017) showed S1 profitable mainly in the early 1980s, decaying since — an explicit,
author-documented example of strategy/edge decay over decades.
**Expected weaknesses / known failure modes**: the exact loss-threshold multiple and position-cap
tiers are unrecoverable from the source (an acknowledged extraction gap); faster variant is
structurally more decay-prone than S2 below. See `18_common_failure_modes.md` §4 (regime-shift
strategy death).
**Related hypotheses**: The Turtles S2 (slower sibling), N-Day/Channel Breakout Trend Family (parent
paradigm), Turtles' vol-normalized position sizing (`16_research_hypotheses.md` §3).
**Source attribution**: Kaufman Ch.5 (Dennis & Eckhardt, mid-1980s); `02_trend_following.md`,
`04_breakouts.md`, `08_entries.md`, `09_exits.md`.

### The Turtles — System 2 (S2)

**Description**: Enter long on a 55-day high breakout (short on 55-day low), exit on the opposite
20-day extreme; no filter rule; pyramids by ATR-increments up to 5 units.
**Supporting concepts**: trend persistence, position pyramiding (`02_trend_following.md`,
`10_position_sizing.md`).
**Suggested indicators**: 55-day/20-day rolling high-low, ATR-based "L" — `13_indicator_reference.md`.
**Expected market conditions**: longer, slower trends; the same copper backtest showed S2 profitable
steadily across the full ~38-year window — more regime-robust than S1.
**Expected weaknesses / known failure modes**: same reconstruction/extraction-gap caveats as S1; a
broader N-day-breakout parameter sweep found S2 performs comparably to the general breakout family
rather than uniquely superior — i.e., its specific 55/20 periods are not obviously special.
**Related hypotheses**: The Turtles S1, N-Day/Channel Breakout Trend Family.
**Source attribution**: Kaufman Ch.5 (Dennis & Eckhardt); `02_trend_following.md`, `04_breakouts.md`.

### Moving-Average Crossover Systems

**Description**: Trade the crossover of a fast trendline against a slow one (or price against both);
family includes Golden/Death Cross (50/200-day), plain 2-MA reversing crossover, 3-line
confirmation variants (Modified 3-Crossover, 4-9-18, "Ahead of the Crowd" 8-18), and the bare
2-MA teaching examples used by Pardo and Hilpisch.
**Supporting concepts**: trend persistence, whipsaw/noise filtering (`02_trend_following.md`).
**Suggested indicators**: SMA/EMA at various periods — `13_indicator_reference.md` ("Moving Average
Sequences", "MA2/EOTS-MA crossover system").
**Expected market conditions**: sustained directional markets; Golden/Death Cross cited as producing
"very good results for the past 60 years" including sidestepping 2008; explicitly weak in
sideways/congested regimes (Kaufman's own out-of-sample 4-9-18 retest: "none of the results would
have convinced you to trade this" in modern, noisier markets).
**Expected weaknesses / known failure modes**: whipsaw without a confirmation band; Pardo's own
overfitting parable (adding a 2nd MA + 2 volatility bands to a bare crossover) took in-sample profit
$10K→$65K while the resulting system LOST $15K out-of-sample — see `18_common_failure_modes.md` §1.
**Related hypotheses**: N-Day/Channel Breakout Trend Family, Adaptive Trend-Speed Systems (smoothing
constant substituted for a fixed period), Volatility-Band Trend Systems.
**Source attribution**: Kaufman Ch.8; Pardo Ch.2/5/7/9/10/13; Hilpisch Ch.4/6; `02_trend_following.md`,
`08_entries.md`, `13_indicator_reference.md`.
**Already tested by this project**: research/research_index.md #1 (EMA9/EMA21/EMA50 trend alignment, 9+
variants) — FAIL, IS +6% → OOS negative, classic overfit; #7 (SMA200 regime overlay,
RiskManagedBetaOverlay) — FAIL, walk-forward OOS 2.77% CAGR vs IS 30.9% CAGR (-11x decay); #2
(Donchian variant, 1h) — FAIL.

### Volatility-Band Trend/Breakout Systems

**Description**: Trade a band built from a trendline ± a scaled volatility measure; buy on close
above the upper band, sell short below the lower (reversal variant) or exit-at-trendline (flat-zone
variant). Family includes Bollinger Bands (both the reversal/breakout-following use and the
"Squeeze" compression-then-expansion trigger), Keltner Channels, Percentage Bands, the 10-Day MA
Rule (Keltner 1960), Modified Bollinger Bands (McNicholl), and the combined Bollinger+Keltner+Chaikin
"Rattlesnake" method (Billy Williams).
**Supporting concepts**: volatility as a trend-continuation signal (`06_volatility.md`), the
"bulge" lag problem of rolling-SD bands (`03_mean_reversion.md`).
**Suggested indicators**: Bollinger Bands, Keltner Channel, Chaikin Oscillator — `13_indicator_reference.md`.
**Expected market conditions**: works when trading in the direction of the prevailing trend after a
compression (squeeze); band-touch as breakout-continuation requires an actual trend, not a range.
**Expected weaknesses / known failure modes**: "2 stdev" covers only ~87% of real (non-normal) price
moves, not the theoretical 95.4%; narrow bands risk immediate same-day whipsaw; standard bands widen
only AFTER a volatility spike has already occurred (the "bulge"). See `18_common_failure_modes.md`.
**Related hypotheses**: Bollinger Band Mean-Reversion Fade (the opposite trading interpretation of the
identical indicator — see Mean-Reversion §), Adaptive Trend-Speed Systems, Kase DevStop (volatility
stops family).
**Source attribution**: Kaufman Ch.8 (Bollinger; Keltner 1960; McNicholl 1998; Billy Williams 2010);
`02_trend_following.md`, `04_breakouts.md`, `13_indicator_reference.md`.
**Already tested by this project**: research/research_index.md #2 (Bollinger, 1h) — FAIL; #3 (TTM squeeze
breakout, 6 iterations) — FAIL, negative in-sample, "squeeze breakouts buy local tops."

### Adaptive Trend-Speed Systems

**Description**: A trendline whose smoothing constant recalculates itself each period from a
noise/regime measure rather than staying fixed — fast in low-noise trending conditions, slow in
noisy/ranging conditions. Family: KAMA (Efficiency-Ratio-driven), VIDYA (relative-volatility-driven,
Chande), Adaptive R² (correlation-coefficient-driven, Chande), MAMA/FAMA and FRAMA (Hilbert-Transform
phase / fractal-dimension-driven, Ehlers), McGinley Dynamics, Adaptive RSI/Stochastic, and Mart's
Master Trading Formula (Correlated Volatility Factor).
**Supporting concepts**: Efficiency Ratio as regime classifier (`07_market_regimes.md`,
`16_research_hypotheses.md` §1).
**Suggested indicators**: KAMA, VIDYA, MAMA/FAMA, FRAMA — `13_indicator_reference.md`.
**Expected market conditions**: designed to work across both trending and noisy regimes by
self-adjusting; a comparative Kaufman test found KAMA traded far less often (134 avg trades) than
VIDYA (594 avg trades) for a similar underlying premise, with generally higher win rate.
**Expected weaknesses / known failure modes**: still technically flips direction the instant price
crosses it (needs an added fixed-move whipsaw filter, per Kaufman's own explicit finding, Ch.17
#62-63); adaptive systems are inherently least validated in rare, extreme-volatility regimes since
abundant test data exists mostly for medium/low volatility — a specific concern for crypto's shorter,
more volatile history. See `15_crypto_specific.md`.
**Related hypotheses**: Moving-Average Crossover Systems (the fixed-period ancestor), Efficiency Ratio
Regime Gate (Regime-Based §), Trend-Adjusted Oscillator.
**Source attribution**: Kaufman Ch.17 (Kaufman 1995; Chande 1992; Ehlers; McGinley; Mart 1981);
`02_trend_following.md`, `13_indicator_reference.md`, `16_research_hypotheses.md` §5.

### Parabolic SAR Trend/Exit Systems

**Description**: An always-in-market, always-reversing trailing-stop system that accelerates its own
smoothing constant as a trade becomes more profitable (Wilder's Parabolic SAR); Knapp's variant
replaces the fixed acceleration progression with an ATR/Efficiency-Ratio-based stop that only ever
tightens; the Directional Parabolic System pairs it with ADX for directional gating.
**Supporting concepts**: trailing-stop trend capture (`09_exits.md`), Efficiency Ratio adaptivity
(`07_market_regimes.md`).
**Suggested indicators**: Parabolic SAR, Acceleration Factor, ADX — `13_indicator_reference.md`.
**Expected market conditions**: requires fairly consistent, sustained price swings; poorly suited to
choppy/sideways markets (always-reversing design guarantees a position at all times).
**Expected weaknesses / known failure modes**: Acceleration Factor always restarts at its minimum
regardless of how fast the market is already moving at entry — a fast-starting trend gets an
unnecessarily wide initial stop. No source in this knowledge base actually uses the term "Chandelier
Exit" — `master_index.md` confirms it is absent from Kaufman and flags this Parabolic SAR family as
the closest structural analogue.
**Related hypotheses**: Kase DevStop (tiered volatility-stop alternative), Adaptive Trend-Speed
Systems.
**Source attribution**: Kaufman Ch.9/Ch.17 (Wilder 1978; Knapp 2010); `02_trend_following.md`,
`09_exits.md`, `13_indicator_reference.md`.
**Already tested by this project**: research/research_index.md #13 — a Chandelier-Exit-on-champion variant
(Forven-derived) tested 2026-07-02 — FAIL, worse than or identical to baseline champion.

### Event-Driven Swing Trend Systems

**Description**: Define trend via price swings exceeding a minimum filter size rather than by a
smoothed average; enter on a new swing extreme. Family: classic Swing Trading, the Livermore System
(swing + penetration-filter reentry logic), Keltner's Minor Trend Rule (no minimum-size filter,
always-reversing), and Wilder's Swing Index / Accumulated Swing Index (bounded per-bar index whose
running sum substitutes for price).
**Supporting concepts**: market structure and swing points (`01_market_structure.md`).
**Suggested indicators**: swing high/low (SH/SL), Swing Index/ASI — `13_indicator_reference.md`.
**Expected market conditions**: trending markets; swing-based systems, unlike moving averages, do not
trigger exits during ordinary sideways drift within an established trend.
**Expected weaknesses / known failure modes**: risk (entry-to-reversal-trigger distance) can become
very large after a sustained move; no minimum-size filter (Keltner's variant) produces excessive small
whipsaw swings; HSP/LSP swing points carry an inherent 2-day confirmation lag.
**Related hypotheses**: N-Day/Channel Breakout Trend Family, Point-and-Figure Charting.
**Source attribution**: Kaufman Ch.5 (Wilder 1978; Keltner); `02_trend_following.md`.

### Point-and-Figure / Renko Charting Trend Systems

**Description**: Event-driven (not time-driven) charting methods using fixed price increments — box
size with a 3-box reversal rule for Point-and-Figure; fixed brick size for Renko — trading breakouts
of the resulting column/brick structure.
**Supporting concepts**: market noise filtering via price-only (not time-based) sampling
(`01_market_structure.md`).
**Suggested indicators**: box size (often ATR-derived), reversal-box count, horizontal/vertical count
targets — `13_indicator_reference.md`.
**Expected market conditions**: Kaufman's own 2000-2017 retest favored large reversals/long trends;
fails in narrow multi-year ranges and crisis-volatility regimes.
**Expected weaknesses / known failure modes**: the "Box-Size Dilemma" — no single fixed box/reversal
size suits both a low-priced-consistent regime and a high-priced-volatile regime of the SAME market's
history — is explicitly stated as unresolved; naive fixed-box-count stops have "no logical basis."
**Related hypotheses**: N-Day/Channel Breakout Trend Family, Event-Driven Swing Trend Systems.
**Source attribution**: Kaufman Ch.5 (Charles Dow; De Villiers 1933; Davis 1965); `02_trend_following.md`,
`04_breakouts.md`.

### Multi-Timeframe Trend Confirmation Systems

**Description**: Combine a slower timeframe (direction/major trend) with a faster timeframe
(timing/entry), typically at a ~5x frequency ratio. Family: Elder's Triple Screen (weekly MACD
histogram slope + Force Index/Elder-Ray timing + hourly breakout trigger), Krausz's Multiple Time
Frames (Gann-derived, 3 coordinated frames with 6 governing "Laws"), Pring's KST (stacked
weighted-ROC composite across several lookback lengths), and the Ichimoku Cloud (cloud as macro trend
filter, Tenkan/Kijun cross as reentry timing).
**Supporting concepts**: multi-timeframe decomposition as a research idea (`16_research_hypotheses.md`
§5); the pullback-timed-entry-inside-a-longer-trend combination (`16_research_hypotheses.md` §5).
**Suggested indicators**: MACD histogram, Force Index, Elder-Ray, KST, Ichimoku Cloud —
`13_indicator_reference.md`.
**Expected market conditions**: designed to work across regimes by construction (major-trend filter +
timing layer), rather than being tied to one; most effective when the major-trend timeframe is
genuinely trending.
**Expected weaknesses / known failure modes**: Krausz's own explicit warning — an N-period MA of one
bar frequency is NOT interchangeable with an "equivalent" MA at a different bar frequency spanning the
same elapsed time, since averaging cannot fully remove noise regardless of how the periods are scaled;
Pring's KST has an author-unspecified smoothing period for one ROC leg (extraction gap, Kaufman
substitutes a working value).
**Related hypotheses**: Trend-Conditional Oscillator Thresholds (`16_research_hypotheses.md` §5),
Adaptive Trend-Speed Systems.
**Source attribution**: Kaufman Ch.19 (Elder 1993/2014; Krausz; Pring 1993); Kaufman Ch.8 (Hosada,
1930s/1969); `02_trend_following.md`, `08_entries.md`, `13_indicator_reference.md`.

### Composite Multi-Factor Trend Systems

**Description**: Blend several distinct trend-strength inputs into one weighted score rather than
relying on price/MA relationships alone. Commodex blends dual-MA scoring, open-interest growth
momentum, and volume momentum into a ranked relative-strength index; MPTDI (Major Price Trend
Directional Indicator) fully re-parameterizes calculation period, weighting, entry threshold, and
stop-loss together based on discrete average-trading-range "steps."
**Supporting concepts**: composite/ensemble trend construction (`16_research_hypotheses.md` §5, KST's
weighted-multi-lookback technique as a generic ensemble method).
**Suggested indicators**: dual MAs, open interest, volume, average trading range classification —
`13_indicator_reference.md`.
**Expected market conditions**: designed to self-adjust to changing volatility regimes (MPTDI) or
combine multiple confirming factors (Commodex) rather than being tied to one regime.
**Expected weaknesses / known failure modes**: Commodex contains a non-standard rule (falling open
interest + falling price scored bullish) explicitly flagged by Kaufman as a departure from standard
convention; MPTDI's discrete step boundaries are "a crude measure" — accurate mid-step but abruptly
wrong at transitions, causing jarring simultaneous parameter jumps.
**Related hypotheses**: Adaptive Trend-Speed Systems, Multi-Timeframe Trend Confirmation Systems.
**Source attribution**: Kaufman Ch.8/Ch.22 (Robert Joel Taylor 1972; Philip Gotthelf's Commodex,
1959-present); `02_trend_following.md`.

### TRIX / ROC Trend-Direction Systems

**Description**: Use a heavily-smoothed rate-of-change construction as the trend signal itself rather
than as a momentum oscillator. TRIX (triple-exponentially-smoothed log price, 2-consecutive-day
direction rule) and the ROC trend system (5-day ROC vs. 252-day ROC crossover, "Woodshedder's
long-term indicator") both convert a momentum-style construction into a low-frequency trend/regime
filter.
**Supporting concepts**: "is it better than momentum?" heuristic (`02_trend_following.md`).
**Suggested indicators**: TRIX, ROC — `13_indicator_reference.md`.
**Expected market conditions**: designed for smoother, lower-noise trend signals at the cost of extra
lag; ROC trend system backtested on S&P futures (1998-2017): 52 trades, 53% profitable, both long and
short sides.
**Expected weaknesses / known failure modes**: extra smoothing stages add lag as "a natural
consequence"; basic n-day momentum sign is the simplest member of this family and converges to an
SMA-direction system for large n.
**Related hypotheses**: Moving-Average Crossover Systems, Basic Momentum Trend-Following
(Momentum §).
**Source attribution**: Kaufman Ch.8/Ch.9 (Jack Hutson 1983; Woodshedder blog, reviewed by MarketSci
Oct. 2011); `02_trend_following.md`, `13_indicator_reference.md`.

---

## 2. Mean-Reversion Hypotheses

### Oscillator/Momentum Fade Framework — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### 2-Day RSI Mean-Reversion (Stokes / Connors-style) — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Net Momentum Oscillator / Stochastics / Ultimate Oscillator Fades — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Kurtosis-Skew Mean-Reverting Strategy — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### DeMark's Sequential™ — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Cointegration / Pairs Trading & Intermarket Spread Strategies — **CLOSED** (BTC-ETH pairs / relative value / rotation / dominance / ratio); full card archived in `archive/closed_families.md`

### IV/HV Relative-Value Arbitrage & Volatility Dispersion Trading — **CLOSED** (DVOL daily-bar champion modifications); full card archived in `archive/closed_families.md`

### Dogs of the Dow / O'Higgins / Foolish Four & Rating-Service Basket Spreads — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Gap-Fade / Gap-Pullback Trading — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Taylor Trading Technique — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Gustafson's Price Persistency Strategy — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Reversal-Day, Weekday, and Day-of-Month Patterns — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Connors AD-Ratio / CHADTP Breadth Fade — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Intraday Price Zones (Jackson / Scorpio / Gould) — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Divergence Index & Fisher Transform Mean-Reversion — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Khandani & Lo Short-Term Cross-Sectional Reversal — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### VIX / IV Mean-Reversion Systems — **CLOSED** (DVOL daily-bar champion modifications); full card archived in `archive/closed_families.md`

### Nofri's Congestion-Phase System — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

## 3. Breakout Hypotheses

### Opening Range Breakout (ORB) Family — **CLOSED** (Intraday / time-of-day / sub-daily constructions); full card archived in `archive/closed_families.md`

### Volatility Breakout Based on the Open or Previous Close — **CLOSED** (Intraday / time-of-day / sub-daily constructions); full card archived in `archive/closed_families.md`

### Dynamic Breakout System (Stridsman)

**Description**: Rather than a plain N-day high/low, anticipates entry/exit one day ahead using a
factor of the standard deviation of recent prices, placing stop orders for the next session.
**Supporting concepts**: volatility-scaled breakout timing (`04_breakouts.md`).
**Suggested indicators**: standard deviation of recent prices — `13_indicator_reference.md`.
**Expected market conditions**: attempts to improve entry/exit timing over a plain N-day breakout.
**Expected weaknesses / known failure modes**: exit-stop hit timing is explicitly bimodal (very quick
stop-outs vs. much longer holds) — the source suggests this is useful information for stop placement
but does not otherwise resolve the bimodality.
**Related hypotheses**: N-Day/Channel Breakout Trend Family, Volatility Breakout Based on the
Open/Previous Close.
**Source attribution**: Kaufman Ch.5 (Thomas Stridsman, 1998); `02_trend_following.md`, `04_breakouts.md`.

### Bill Williams' 5-Bar Fractal Breakout

**Description**: A pivot-based breakout — buy following a "down fractal" (5-bar pivot-low pattern)
when price rises above the pattern's highest high (mirror for sells); stop at the fractal extreme,
profit target equal to the fractal pattern's own high-low range.
**Supporting concepts**: pivot-point breakout structure (`04_breakouts.md`).
**Suggested indicators**: 5-bar up/down fractal pivot patterns — `13_indicator_reference.md`.
**Expected market conditions**: SPY backtest (2000-2018) was profitable for long positions specifically
(58% reliability); profit-taking without stops was the best-performing combination in that test.
**Expected weaknesses / known failure modes**: none distinctly stated beyond general breakout
whipsaw risk.
**Related hypotheses**: Point-and-Figure Breakout Entries, N-Day/Channel Breakout Trend Family.
**Source attribution**: Kaufman Ch.20 (Bill Williams, 1995/2004); `04_breakouts.md`.

### True Gap / Wide-Ranging-Bar Breakout Entries

**Description**: A "true" gap opens beyond yesterday's high/low and does not trade back to that level
— rather than fading it (see Gap-Fade/Gap-Pullback Trading, Mean-Reversion §), this family trades the
gap as a CONTINUATION signal; includes Rudd's wide-ranging-bar day-trading setups (breakout of a
higher open; selling a gap that begins fading within 5 minutes of the open).
**Supporting concepts**: gap-day continuation vs. fade as two opposite paradigms on the same event
(`04_breakouts.md`).
**Suggested indicators**: true-gap definition (open beyond prior day's high/low with no retrace),
wide-ranging-bar detection — `13_indicator_reference.md`.
**Expected market conditions**: intraday; Kaufman's own best-tested combination was entry on a pullback
to the previous close plus exit on the next open — itself a partial hybrid of continuation and fade
logic.
**Expected weaknesses / known failure modes**: none distinctly additional stated beyond general gap-
trading risk; note the direct tension with Gap-Fade/Gap-Pullback Trading — the same event (a gap) is
traded in opposite directions by different rule sets, and which one applies depends on whether the gap
qualifies as "true" (no retrace) under the specific definition used.
**Related hypotheses**: Gap-Fade / Gap-Pullback Trading (Mean-Reversion §, the opposite
interpretation), Opening Range Breakout Family.
**Source attribution**: Kaufman Ch.16 (DeMark; Larry Williams; Barry Rudd, 1998); `04_breakouts.md`.

### Intraday Price-Shock Fade (contrast case) — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

## 4. Momentum Hypotheses

### Basic Momentum Trend-Following

**Description**: Sell when n-day momentum (price minus price n days ago) turns negative, buy when it
turns positive, with a small deadband around zero to reduce whipsaw — the simplest possible trend
system, converging to an SMA-direction system for large n.
**Supporting concepts**: momentum as a trend proxy (`05_momentum.md`, `02_trend_following.md`).
**Suggested indicators**: n-day momentum / rate of change — `13_indicator_reference.md`.
**Expected market conditions**: longer calculation periods behave as trend indicators; calc period
should roughly match ½-¼ of the natural cycle length between chart tops/bottoms.
**Expected weaknesses / known failure modes**: percentage-momentum construction breaks on
back-adjusted futures / split-adjusted stock data — use price differences instead.
**Related hypotheses**: TRIX/ROC Trend-Direction Systems, Moving-Average Crossover Systems.
**Source attribution**: Kaufman Ch.9; `02_trend_following.md`, `05_momentum.md`.

### MACD Crossover Trend System

**Description**: Buy when the MACD line crosses above its signal line, sell on the mirror cross; a
threshold refinement requires MACD to first penetrate an outer band before a crossing counts,
reducing whipsaw in sideways markets.
**Supporting concepts**: dual-EMA momentum as a trend-timing tool (`05_momentum.md`).
**Suggested indicators**: MACD, signal line, histogram — `13_indicator_reference.md`.
**Expected market conditions**: basic crossover is prone to false signals in sideways markets; the
threshold-band refinement is designed to filter exactly that regime.
**Expected weaknesses / known failure modes**: explicit overfitting caveat — fitting threshold-band
levels to historical data makes them unreliable live; see `18_common_failure_modes.md` §1.
**Related hypotheses**: MACD/Momentum Divergence Trading, Divergence Index (Mean-Reversion §).
**Source attribution**: Kaufman Ch.9 (Gerald Appel); `05_momentum.md`.

### MACD / Momentum Divergence Trading

**Description**: Enter counter to the current move when price and a momentum indicator (MACD, RSI, or
stochastic) diverge — price makes a new high/low not confirmed by the oscillator. Includes an
anticipatory early-entry variant (act before the second peak visually completes), a scaled
(thirds) entry variant, Slope Divergence (comparing linear-regression slopes of price vs. momentum
rather than raw values), and the Cambridge Hook pattern (RSI&gt;60% + outside-day reversal + rising
volume/open interest).
**Supporting concepts**: momentum exhaustion as a defensive overlay, not a standalone signal
(`05_momentum.md`, `16_research_hypotheses.md` §5).
**Suggested indicators**: MACD, RSI, stochastic, Cambridge Hook pattern — `13_indicator_reference.md`.
**Expected market conditions**: more reliable on daily than intraday data; more reliable when
divergence begins at an indicator extreme; larger/longer divergence formations forecast bigger
reversals.
**Expected weaknesses / known failure modes**: fully mechanical programming is explicitly
acknowledged as difficult (the reference tool doesn't always find visually-obvious divergences);
momentum rising faster than price while both are STILL rising is explicitly NOT a valid divergence — a
common false-positive trap; `16_research_hypotheses.md` §5 recommends using divergence as a
defensive/tightening overlay on an existing trend position rather than trading it outright.
**Related hypotheses**: MACD Crossover Trend System, Fisher Transform Turning-Point Fade
(Mean-Reversion §).
**Source attribution**: Kaufman Ch.9 (Elias Crim, 1985); `05_momentum.md`.

### TSI / RVI / Awesome Oscillator / Double-Smoothed Stochastic Momentum Systems

**Description**: A family of smoothed momentum oscillators trading signal-line crossovers or pattern
triggers rather than raw threshold levels: True Strength Index (double-smoothed momentum ratio,
Blau), Relative Vigor Index (4-day symmetric-weighted close-vs-range ratio, Ehlers), Awesome
Oscillator (5/34-period midpoint-SMA difference, with "saucer" and "Twin Peaks" pattern variants,
Bill Williams), and Double-Smoothed Stochastic (Blau's noise-reduced %K/%D construction).
**Supporting concepts**: reducing whipsaw via double-smoothing (`05_momentum.md`).
**Suggested indicators**: TSI, RVI, Awesome Oscillator — `13_indicator_reference.md`.
**Expected market conditions**: general momentum-confirmation use across trend continuation and
divergence-based reversal setups.
**Expected weaknesses / known failure modes**: double/triple smoothing trades whipsaw reduction for
extra lag "as a natural consequence" (explicit trade-off, not a flaw to be engineered away).
**Related hypotheses**: MACD Crossover Trend System, TRIX/ROC Trend-Direction Systems.
**Source attribution**: Kaufman Ch.9 (William Blau 1995; John Ehlers 2002; Bill Williams);
`05_momentum.md`, `13_indicator_reference.md`.

### ADX-Filtered Oscillator (Kestner) & Directional Parabolic

**Description**: A 10-day/50-day MA-difference oscillator executed only when ADX confirms the absence
of a strong trend (Kestner); the Directional Parabolic System instead uses ADX as a directional
regime filter (rising ADX → longs only, falling → shorts only) paired with Parabolic SAR as the exit
mechanism.
**Supporting concepts**: ADX as a trend/no-trend regime classifier (`05_momentum.md`,
`07_market_regimes.md`).
**Suggested indicators**: ADX, +DMI/−DMI, Parabolic SAR — `13_indicator_reference.md`.
**Expected market conditions**: Kestner's variant is explicitly designed to trade the oscillator only
in a non-trending (mean-reverting) regime; Directional Parabolic is explicitly trend-following.
**Expected weaknesses / known failure modes**: exact inequality thresholds for Kestner's construction
are an embedded-graphic extraction gap; underlying PDM/MDM formulas in the Directional Parabolic
System are flagged as reconstructed, not verbatim-extracted.
**Related hypotheses**: ADX Trend/No-Trend Gate (Regime-Based §, the same underlying indicator used
purely as a gate rather than a component of the traded signal).
**Source attribution**: Kaufman Ch.9 (J. Welles Wilder 1980; Lars Kestner 2003); `05_momentum.md`.

### Time-Series Momentum (Moskowitz-style) — **CLOSED** (Short side / symmetric TSMOM of the champion's gate); full card archived in `archive/closed_families.md`

### Cross-Sectional Momentum & PEAD

**Description**: Buy recent relative outperformers, sell relative underperformers from a pool of
instruments, over 3-12 month holding periods (Jegadeesh & Titman); Post-Earnings-Announcement Drift
(PEAD) is a related, event-specific momentum source (buy on earnings beat, short on miss) attributed
to slow information diffusion.
**Supporting concepts**: cross-sectional relative-strength ranking (`05_momentum.md`,
`12_portfolio_construction.md`).
**Suggested indicators**: trailing relative-return ranking across an instrument universe — n/a
(cross-sectional ranking, not a single technical indicator).
**Expected market conditions**: cited as generating "significant positive returns over 3-12 month
holding periods" in the original academic literature.
**Expected weaknesses / known failure modes**: EXPLICITLY NOT independently implemented/backtested in
either source book used here — only cited/defined; Chan's closest adjacent exercise (a PCA-factor
cross-sectional ranking on S&P 600 small caps) produced a NEGATIVE −1.81% annualized return, presented
as an explicit failure example, not a working strategy.
**Related hypotheses**: Fama-French/PCA Factor Cross-Sectional (below, the failed adjacent exercise),
Cross-Sectional Top-K Momentum Portfolio (Cross-Sectional/Portfolio §).
**Source attribution**: Jegadeesh & Titman 1993/2001 (cited by Hilpisch Ch.4); Chan Ch.7 (Example
7.4); `05_momentum.md`.
**Already tested by this project**: research/research_index.md #11 (blending/dual momentum/x-sect top-K/
long-short pairs) — FAIL, "correlations too high; narratives don't survive data; DD blowups."

### Fama-French / PCA Factor Cross-Sectional Model (failed example)

**Description**: Assumes factor returns (beta, market cap, book-to-price) persist from one period to
the next; ranks and trades the top/bottom of a cross-section by expected factor-based return.
**Supporting concepts**: factor-model-implied cross-sectional ranking (`05_momentum.md`).
**Suggested indicators**: PCA-derived factor exposures/expected returns — `13_indicator_reference.md`.
**Expected market conditions**: S&P 600 small-cap universe (Chan's own worked example).
**Expected weaknesses / known failure modes**: the result was a negative average annualized return of
−1.81%, explicitly presented by the author as a FAILURE, not a working strategy — a rare case in this
knowledge base of an author publishing a negative result rather than only successes.
**Related hypotheses**: Cross-Sectional Momentum & PEAD, Regime-Switching via Cross-Sectional PCA
Factor Models (`16_research_hypotheses.md` §5, the same failed example cross-referenced there).
**Source attribution**: Chan Ch.7 (Example 7.4); `05_momentum.md`, `16_research_hypotheses.md` §5.

### Chan's Regime-Based Momentum/Mean-Reversion Switching Framework

**Description**: A statistical (not chart-based) decision rule: if prices are believed mean-reverting
and currently low relative to a reference, buy (expect reversion up); if believed trending and low,
sell short (expect continuation down) — and the mirror at highs. Regime is determined via
stationarity/cointegration testing rather than discretionary judgment.
**Supporting concepts**: news-driven momentum vs. liquidity-driven mean-reversion heuristic
(`05_momentum.md`, `07_market_regimes.md`, `17_author_disagreements.md` §5).
**Suggested indicators**: CADF stationarity/cointegration test, Ornstein-Uhlenbeck half-life —
`13_indicator_reference.md`.
**Expected market conditions**: Chan's own explicit (opinion-level) claim: "mean-reverting regimes are
more prevalent than trending regimes."
**Expected weaknesses / known failure modes**: Chan states Hidden Markov Models are "generally useless
for actual trading" for this exact regime-classification purpose since constant transition
probabilities give no signal about WHEN a switch is imminent; GARCH-based volatility-regime switching
is separately stated to be "of no help to stock traders" for directional purposes.
**Related hypotheses**: Cointegration / Pairs Trading (Mean-Reversion §), Hidden Markov Model Regime
Switching (Regime-Based §, the rejected alternative).
**Source attribution**: Chan Ch.7; `05_momentum.md`, `07_market_regimes.md`.

### Data-Mining Turning-Points Regime-Trigger Model (Alphacet)

**Description**: Feed candidate predictive variables (volatility, last-period return, macro changes)
into a data-mining search (perceptron) to find regime-turning triggers — e.g., a large 1-day % change
combined with an N-day high/low proximity as a proxy trigger, trained across multiple candidate
holding periods on a rolling backward-looking window.
**Supporting concepts**: backward-looking-only ML regime search as an alternative to constant-
transition-probability Markov models (`05_momentum.md`, `16_research_hypotheses.md` §1).
**Suggested indicators**: 1-day % change threshold, N-day high/low proxy, perceptron-trained signal —
n/a (ML output, not a named technical indicator).
**Expected market conditions**: Chan's own worked example (Goldman Sachs stock) reported 37.93% gross
cumulative return over 6 months (89 round trips) vs. 15.77% buy-and-hold.
**Expected weaknesses / known failure modes**: explicitly flagged by Chan HIMSELF as still vulnerable
to data-snooping bias via "model-category shopping" even within a strict backward-looking optimization
window — called "unavoidable whenever we are in the business of backtesting"; short backtest window
(6 months, 89 trades) independently invites suspicion per this project's own sample-size discipline.
**Related hypotheses**: Chan's Regime-Based Momentum/Mean-Reversion Switching Framework, Aronson's
Descriptor/Trade-Profile ML Labeling (Statistical/ML §).
**Source attribution**: Chan Ch.7 (Example 7.1, citing Chai 2007; Alphacet Discovery platform);
`05_momentum.md`, `07_market_regimes.md`.

---

## 5. Volatility-Based Hypotheses

### Trend + Volatility-Target Sizing Combo

**Description**: Combine a trend-following signal (any of the Trend-Following §1 families) with
position sizing scaled to a target portfolio/strategy volatility rather than fixed dollar or fixed
fractional sizing — control tail risk via the trend exit AND variance via the sizing layer
simultaneously. Historical variants: the Turtles' ATR-based, correlation-capped sizing; Kaufman's
Volatility-Factor (VF) rebalancing overlay (rebalance only when VF drifts ≥20% from currently-applied
factor); generic Portfolio-Level Volatility Targeting.
**Supporting concepts**: volatility-normalized position sizing (`10_position_sizing.md`,
`06_volatility.md`); Kaufman's stated 6-8% typical / 16%+ "dangerous" traditional-market vol-target
range vs. this project's own much higher crypto vol-target (`17_author_disagreements.md` §2, an
explicitly flagged, unresolved reconciliation item).
**Suggested indicators**: rolling realized volatility, ATR-based volatility measure —
`13_indicator_reference.md`.
**Expected market conditions**: designed to work across regimes by construction — rising-vol regimes
run hot, declining-vol regimes run cool (an explicit, stated lag in both directions); Kaufman's own
worked macrotrend futures case study reports AROR rising 8.7%→14.3% (+64%) purely from applying a
20%-threshold rolling VF scheme at equal realized risk.
**Expected weaknesses / known failure modes**: the VF mechanism lags during regime transitions and
does not eliminate the need for separate risk controls (VaR, etc.) since "all measures of risk look
only at historic volatility"; neither the trend gate alone nor vol-targeting alone reliably controls
drawdown on its own — this project's own finding (see below) is that the COMBINATION is the load-
bearing construct, not either piece individually.
**Related hypotheses**: Volatility-Stabilized Trend Portfolio (Cross-Sectional/Portfolio §, the
multi-asset-portfolio-level version of this same idea), Equal-Risk Portfolio Weighting.
**Source attribution**: Kaufman Ch.5, Ch.23-24; `06_volatility.md`, `10_position_sizing.md`,
`16_research_hypotheses.md` §3, `17_author_disagreements.md` §2.
**Already tested by this project — BEST OF PROJECT, unproven at the DSR bar**: research/research_index.md #9
(TrendVolTarget: ens3 trend core + 40% vol-target sizing, BTC+ETH 1d). Full-window 6.5y +458%,
Sharpe 1.26, DD −16.6% (real engine); held-out TEST Sharpe 0.41; DSR 0.64-0.67 at n_trials=85 — below
the project's own 0.95 bar. Honest forward expectation: 5-15% CAGR at ~20% DD. See
research/strategy_iteration_log.md Iteration 6 and `MEMORY.md` (strategy_trend_vol_target.md) for full detail.
Also see #10 (TVT 9-asset + 25% portfolio-vol overlay) — PARTIAL, kept as a defensive variant.

### Kase DevStop — Tiered Volatility Stop System

**Description**: A volatility-adaptive trailing-stop system computing 2-day True Range and its
rolling ATR/standard deviation; a tiered (3-level) variant scales out ⅓ of the position at each of
three ATR-derived stop levels rather than exiting the full position at a single stop.
**Supporting concepts**: volatility-scaled exits (`06_volatility.md`, `09_exits.md`,
`16_research_hypotheses.md` §3).
**Suggested indicators**: 2-day True Range, rolling ATR, standard deviation — `13_indicator_reference.md`.
**Expected market conditions**: general trend-following risk management; graduated de-risking as
volatility/price moves against the position.
**Expected weaknesses / known failure modes**: the multiplier mapping between the two places this is
documented in the source is internally inconsistent (one location gives two multiplier ranges, another
gives three fixed multiples) — preserved unreconciled per `17_author_disagreements.md` §8; the
underlying entry rules themselves are largely the extraction's own reconstruction since Kase's entry
methodology "is not disclosed" beyond stop positioning.
**Related hypotheses**: Parabolic SAR Trend/Exit Systems (Trend-Following §1, the alternative
trailing-stop family).
**Source attribution**: Kaufman Ch.18, Ch.23 (Cynthia Kase, 1993); `06_volatility.md`, `09_exits.md`.

### Volatility-Filtered Trend Following

**Description**: Overlay a volatility regime filter onto an otherwise plain trend system — e.g., exit
a 100-day-MA trend system when annualized volatility exceeds a threshold (e.g., 30%), re-enter once
volatility falls back below a lower threshold (e.g., 15%).
**Supporting concepts**: volatility regime gating of an existing signal (`06_volatility.md`,
`07_market_regimes.md`).
**Suggested indicators**: rolling annualized volatility — `13_indicator_reference.md`.
**Expected market conditions**: Kaufman's own QQQ case study (1998-2018) found this reduced risk ~45%
with similar/better profit by specifically avoiding high-vol crisis periods (dot-com bust, 2008).
**Expected weaknesses / known failure modes**: the specific 30%/15% thresholds are only a rough average
— explicitly must be re-tuned per market; crypto's baseline volatility routinely exceeds even the
book's "dangerous" 45% threshold in normal regimes, so any crypto application needs empirically
re-derived thresholds, not the book's numbers (`15_crypto_specific.md`).
**Related hypotheses**: Trend + Volatility-Target Sizing Combo, Efficiency Ratio Regime Gate
(Regime-Based §).
**Source attribution**: Kaufman Ch.20; `06_volatility.md`, `15_crypto_specific.md`.

### Price-Shock Reversal / Fade (daily scale) — **CLOSED** (Mean reversion on crypto OHLCV (all tested timeframes)); full card archived in `archive/closed_families.md`

### Low-Volatility Anomaly / Low-Vol ETF Strategy

**Description**: Hypothesis that low-volatility stocks/instruments outperform on a risk-adjusted basis
with much lower risk than the broad index, even where raw return is not clearly higher.
**Supporting concepts**: volatility-based selection as an alternative to return-based selection
(`06_volatility.md`).
**Suggested indicators**: realized/historic volatility ranking — n/a (ranking, not a single indicator).
**Expected market conditions**: general equity selection; Kaufman explicitly notes this works "for
mean-reverting systems, not macro-trend."
**Expected weaknesses / known failure modes**: explicit empirical caveat — three tested low-vol ETFs
(USMV/SPLV/SPHD) all UNDERPERFORMED SPY's 232% return (220%/195%/167%) over 2011/12-2018, so "it's not
clear these funds' return-volatility is proportionately lower"; only tested in a single bull-market
window.
**Related hypotheses**: Volatility-Filtered Trend Following, Efficiency Ratio Regime Gate.
**Source attribution**: Kaufman Ch.20 (Charlie Bilello finding, cited); `06_volatility.md`.

---

## 6. Regime-Based Hypotheses

### Efficiency Ratio Regime Gate — **CLOSED** (Regime-classifier overlay (ER, ADX, MESA, HMM)); full card archived in `archive/closed_families.md`

### MESA / Hilbert Cycle-Presence Regime Gate — **CLOSED** (Regime-classifier overlay (ER, ADX, MESA, HMM)); full card archived in `archive/closed_families.md`

### ADX Trend / No-Trend Regime Gate — **CLOSED** (Regime-classifier overlay (ER, ADX, MESA, HMM)); full card archived in `archive/closed_families.md`

### Hidden Markov Model Regime-Switching — **CLOSED** (Regime-classifier overlay (ER, ADX, MESA, HMM)); full card archived in `archive/closed_families.md`

### Regime-Conditional Stop-Loss Logic

**Description**: Whether to use a stop-loss at all is made conditional on the BELIEVED regime — a
stop-loss is beneficial in a believed momentum/trending regime, but actively harmful in a believed
mean-reverting regime (forces an early exit before reversion). Heuristic for distinguishing regimes: a
news/fundamental-driven move suggests momentum ("don't stand in front of a freight train"); a move
with no apparent news cause suggests a liquidity event, more likely to mean-revert.
**Supporting concepts**: regime-dependent risk management, a point of agreement (not disagreement)
between Chan and Kaufman despite differing paradigm emphasis (`17_author_disagreements.md` §5).
**Suggested indicators**: none mechanical — a discretionary regime-classification heuristic (news vs.
no-news causal attribution).
**Expected market conditions**: explicitly regime-dependent by design — the entire point of the rule
is classifying the regime BEFORE deciding whether a stop applies at all.
**Expected weaknesses / known failure modes**: Chan's own heuristic is explicitly his own opinion, not
a formally derived or empirically validated rule even within his own book's equity-focused testing; no
algorithm exists (per Chan's own admission) to distinguish a genuine regime shift from ordinary
statistical variance with certainty. See `18_common_failure_modes.md` §4.
**Related hypotheses**: Chan's Regime-Based Momentum/Mean-Reversion Switching Framework.
**Source attribution**: Chan Ch.6, Ch.7; `07_market_regimes.md`, `09_exits.md`.

### Seasonal / Calendar Regime Effects

**Description**: A cluster of calendar-driven regime hypotheses: pre-holiday strength (Fosback),
month-end institutional-flow effect, "Sell in May" 6-month seasonal (Hirsch), January Barometer,
October reversal/"ricochet rally" tendency, and genuine commodity seasonals with a real fundamental
driver (Chan's NYMEX gasoline and natural-gas seasonal trades, tied to driving-season/cooling-season
demand).
**Supporting concepts**: calendar effects as regime drivers (`07_market_regimes.md`); the explicit
requirement that a crypto seasonal claim have its OWN independently justified mechanism, since crypto
lacks the institutional settlement-cycle basis these patterns rest on (`16_research_hypotheses.md` §5).
**Suggested indicators**: calendar date/day-of-month/day-of-week — n/a (calendar-based).
**Expected market conditions**: each pattern is regime/market-specific — no universal rule; commodity
seasonals with a genuine physical-demand driver (gasoline, natural gas) are explicitly stated by Chan
to remain profitable through the time of writing, in contrast to equity seasonal effects.
**Expected weaknesses / known failure modes**: several equity-seasonal patterns are explicitly
documented as DECAYED or FAILED under retest — January Barometer shows no significant pattern outside
a base-rate artifact; year-on-year momentum (Heston & Sadka) "has disappeared" in Chan's own post-2002
retest (average return −0.9167%, Sharpe −0.1055); January-Effect small-cap reversal failed in 2 of 3
retested years. See `18_common_failure_modes.md` §4 (Chan's "equity seasonal effects have weakened"
finding) as a concrete, dated negative-result example.
**Related hypotheses**: Day-of-Month Institutional-Flow Fade (Mean-Reversion §), Halving-Cycle/
Calendar Crypto Effects (Crypto-Specific §).
**Source attribution**: Kaufman Ch.10; Chan Ch.7; `07_market_regimes.md`, `18_common_failure_modes.md` §4.
**Already tested by this project**: research/research_index.md #11 (halving cycle/calendar effects, among
others) — FAIL.

### COT Positioning Regime Signals

**Description**: Uses Commitment of Traders (COT) net positioning by trader group (commercials, large
speculators, small traders) as a "smart money vs. crowd" regime-turn signal. Family: Jiler's
bullish/bearish configuration heuristic, the Briese Index (stochastic-rescaled net-long positioning),
Ruggiero's COT-stochastic extreme trade and "markup phase" cycle-capture system, and a COT-Index
commercial/small-trader crossover timing model.
**Supporting concepts**: smart-money-vs-crowd positioning divergence (`07_market_regimes.md`,
`01_market_structure.md`).
**Suggested indicators**: COT net positioning by trader group, Briese-style stochastic rescaling —
`13_indicator_reference.md`.
**Expected market conditions**: extreme-positioning regime turns; large-hedger positioning was found to
correctly forecast major moves 67% of the time in one cited 36-market study (1983-89); small traders
notably worse forecasters (the consistent "crowd wrong at extremes" pattern documented throughout the
source).
**Expected weaknesses / known failure modes**: caution against assuming full reversion from one extreme
directly to the opposite extreme — safer to expect only a return to neutral; several exact numeric
thresholds are embedded-graphic extraction gaps; the source itself flags a probable buy/sell polarity
error in one cited implementation (Ruggiero's), not definitively resolved.
**Related hypotheses**: CME BTC/ETH COT Positioning Filter (Crypto-Specific §, the literal crypto-data
instance of this same idea).
**Source attribution**: Kaufman Ch.14 (Jiler 1985; Briese; Ruggiero); `07_market_regimes.md`.

### Sentiment-Extreme Regime Signals

**Description**: Uses aggregate sentiment/positioning surveys as contrarian regime-turn signals: the
Bullish Consensus / Market Sentiment Index (Hadady, circulation-weighted brokerage/advisor
bullishness, neutral defined at 55%, normal range 30-80%), the Put-Call Ratio (contrarian, better used
as trendline-deviation than absolute level), and aggregate net insider-transaction value (historically
high net insider selling preceded poor 12-month performance).
**Supporting concepts**: crowd-exhaustion contrarian theory, position-size asymmetry at sentiment
extremes (`18_common_failure_modes.md` §10, `07_market_regimes.md`).
**Suggested indicators**: Bullish Consensus survey, Put/Call Ratio — `13_indicator_reference.md`.
**Expected market conditions**: sentiment-extreme regime-turn signals — within the "normal" 30-80%
range the contrarian trades WITH the trend; only at true extremes does the contrarian look to exit.
**Expected weaknesses / known failure modes**: Hadady's own explicit caveat — "works 100% of the time
in principle, but getting an accurate consensus" (survey timeliness/lag) is the real practical problem;
crypto's own Fear & Greed Index is flagged as a plausible substitute that may sidestep this project's
prior blocked sentiment-data pivot (`15_crypto_specific.md`).
**Related hypotheses**: Crypto Fear & Greed Sentiment Filter (Crypto-Specific §).
**Source attribution**: Kaufman Ch.14 (Hadady; Bjorgen and Leuthold 1998); `07_market_regimes.md`,
`18_common_failure_modes.md` §10.

### Trend + Support/Resistance Regime Overlay

**Description**: Combines a trend signal (MA turning down/up) with a trading-range support/resistance
zone overlay to time entries/exits — e.g., short on MA-turn-down OR price entering a sell zone below
resistance (whichever first), preventing entry of a short just above support where signals would
otherwise cancel out.
**Supporting concepts**: bridging trend-regime and range-regime logic explicitly (`07_market_regimes.md`).
**Suggested indicators**: moving average, support/resistance zones — `13_indicator_reference.md`.
**Expected market conditions**: designed to work across BOTH trend and the more common trading-range
regime by explicit construction.
**Expected weaknesses / known failure modes**: none distinctly stated beyond the general
trend-vs-mean-reversion payoff-parity lesson (`18_common_failure_modes.md` §1) — that neither paradigm
is inherently superior once each is played with its own correct discipline.
**Related hypotheses**: Regime-Conditional Stop-Loss Logic, Moving-Average Crossover Systems
(Trend-Following §1).
**Source attribution**: Kaufman Ch.22; `07_market_regimes.md`.

### Fischer's Golden Section Compass & Hurst Phasing (cyclic timing methods)

**Description**: Two cycle-based timing frameworks: Fischer's Golden Section Compass projects
turning-point dates via Fibonacci-derived day-count relationships between paired prior swing extremes
(entry on a 5-day reversal after the projected date) and sets profit objectives for Elliott Waves 3
and 5 as a function of Wave 1's length; Hurst Phasing uses two lagged moving averages (full-span,
half-span) whose crossing points define a regression trendline used to project the next price
objective.
**Supporting concepts**: cyclic/Elliott-Wave-adjacent price structure (`07_market_regimes.md`).
**Suggested indicators**: Fibonacci day-count ratios, full/half-span phased moving averages —
`13_indicator_reference.md`.
**Expected market conditions**: swing/cycle-turn timing specifically; confidence rises only when
multiple time-goal days coincide.
**Expected weaknesses / known failure modes**: exact time-goal-day and phasing formulas are
embedded-graphic extraction gaps; Wave 5's price target is explicitly not valid unless Wave 3's
objective is first satisfied.
**Related hypotheses**: MESA/Hilbert Cycle-Presence Regime Gate.
**Source attribution**: Kaufman Ch.11, Ch.14 (Fischer; J.M. Hurst, 1970); `07_market_regimes.md`.

---

## 7. Cross-Sectional / Portfolio Hypotheses

### Reversed Dogs-of-the-Dow + Volatility-Triggered Hedge Overlay

**Description**: Buy the Dow's 10 BEST-return stocks (opposite of the classic worst-return
mean-reversion selection), monthly rebalanced; when 20-day annualized Dow volatility exceeds a
threshold (e.g., 90%), hedge by selling 50% of holdings and shorting the 10 worst-performing Dow
stocks (or short DIA, a weaker protection) with the freed capital.
**Supporting concepts**: momentum-based basket selection combined with a volatility-regime hedge
trigger (`12_portfolio_construction.md`, `07_market_regimes.md`).
**Suggested indicators**: trailing 1-year return ranking, 20-day annualized volatility —
`13_indicator_reference.md`.
**Expected market conditions**: momentum/persistence regime for stock selection; the hedge overlay
specifically targets high-volatility crisis regimes (built and tested through 2008).
**Expected weaknesses / known failure modes**: even the hedged construction showed extreme risk in
2008 before the hedge trigger was added — motivating rather than eliminating the need for the overlay;
shorting DIA offers weaker protection than shorting the 10 worst stocks directly.
**Related hypotheses**: Dogs of the Dow / O'Higgins / Foolish Four (Mean-Reversion §, the opposite-
direction/original selection logic on the same universe), Volatility-Filtered Trend Following.
**Source attribution**: Kaufman Ch.13; `12_portfolio_construction.md`.

### GASP — Genetic-Algorithm Multi-Strategy Portfolio Allocation

**Description**: Allocate capital across a set of long/short trend and mean-reversion strategies
(worked case: 19 unique strategies on NASDAQ-100) using a genetic algorithm maximizing
AROR/semivariance-of-drawdowns (OF = AROR/SDD) rather than classic mean-variance, subject to liquidity
and target-risk-band constraints.
**Supporting concepts**: semivariance-of-drawdowns as an alternative objective function for
frequently-flat strategies (`10_position_sizing.md`, `12_portfolio_construction.md`,
`16_research_hypotheses.md` §3).
**Suggested indicators**: semivariance-of-drawdowns, liquidity cap (≤3% of ADV) —
`13_indicator_reference.md`.
**Expected market conditions**: designed specifically for active-trading systems with disjoint,
non-daily returns (frequently flat) — a pattern standard mean-variance/covariance methods systematically
mis-penalize; directly relevant to crypto strategies like this project's own TrendVolTarget, which is
flat through the 2018/2022 bears by design.
**Expected weaknesses / known failure modes**: across 3 optimization passes in the worked example,
allocations changed visibly but the objective function improved only marginally — "a range of
allocations will return similar results," a caution against over-trusting one solved allocation as
uniquely optimal; the test interval must span bull/bear markets and price shocks or the allocation
won't survive a genuine crisis.
**Related hypotheses**: Volatility-Stabilized Trend Portfolio, Kelly-Weighted Multi-Strategy Portfolio.
**Source attribution**: Kaufman Ch.24; `12_portfolio_construction.md`, `16_research_hypotheses.md` §3.

### Volatility-Stabilized Trend Portfolio (VF Rebalancing) **ASSIGNED (T-024)**

**Description**: A macrotrend world-futures trend-following portfolio rescaled toward a target
annualized volatility via a Volatility Factor (VF = target/actual), rebalanced only when VF drifts
≥20% from the currently-applied factor (a switching-cost threshold, not continuous rebalancing).
**Supporting concepts**: portfolio-level volatility targeting (`06_volatility.md`,
`12_portfolio_construction.md`).
**Suggested indicators**: realized portfolio volatility, Volatility Factor — `13_indicator_reference.md`.
**Expected market conditions**: designed to hold constant realized risk across changing-volatility
regimes; Kaufman's own worked example (1989-2018) showed AROR rising from 8.7% to 14.3% (+64%) at the
same volatility purely from this overlay.
**Expected weaknesses / known failure modes**: lags during regime transitions in both directions
(rising-vol regimes run hot, declining-vol regimes run cool); doesn't eliminate the need for other risk
controls (VaR, etc.).
**Related hypotheses**: Trend + Volatility-Target Sizing Combo (Volatility-Based §, the
single-instrument version of this same idea), Equal-Risk Portfolio Weighting.
**Source attribution**: Kaufman Ch.24; `06_volatility.md`, `12_portfolio_construction.md`.

**Status: TESTED (basket-exposure form) — REJECTED (2026-08-01, Task T-038 / H-BasketVolTarget-1h,
Independent Reviewer A-verified, zero trials spent).** The portfolio-level VF overlay with a
drift-threshold rebalance rule — exactly this card's construction — was tested on OKX perps at **1h**:
equal-weight 9-perp long basket scaled by `m_t = min(1, sigma_target/sigma_t)`, EWMA half-life 48
bars, TRAIN-median target, 0.10 no-trade band, taker 9.0 bps/side. **Killed at the zero-cost harm
census (P2) on both clauses**: basket Q1−Q5 forward per-unit-risk return **−0.442905** (KILL if ≤ 0)
and **1 of 9** instruments on the hypothesised side (KILL if < 5 of 9). The mechanism is **inverted**
on this data — high-trailing-volatility hours had *better* forward per-unit-risk returns, because
high-vol bars in a long-only crypto book are predominantly high-vol *rallies*. Persistence (P1)
passed decisively (ρ median 0.564373), so the volatility *forecast* is sound; what fails is the claim
that the forecast is worth acting on. **What this does and does not close:** it falsifies *de-risking
on a volatility LEVEL signal in a long-only crypto perp book* (second independent confirmation after
H-IVSizing, T-022/2026-07-12, on implied vol). It does **not** close the card generally — Kaufman's
construction is a *trend-following futures* portfolio, this basket is unhedged long-only, and no
downside-vol-discriminating measure has been tested. See `research/results/T-038_report.md` and
`research/review_briefs/T-038_brief.md`.

### Equal-Risk (Volatility-Parity) Portfolio Weighting

**Description**: Weight each asset in a portfolio inversely to its own volatility so each contributes
EQUAL risk rather than equal dollars (e.g., a 4%-vol asset gets 20% weight, a 1%-vol asset gets 80%) —
one of Kaufman's cited "Five Portfolio Models" (Narang), alongside Equal-Dollar, Alpha-Driven, and
Decision-Tree weighting.
**Supporting concepts**: volatility-normalized cross-asset allocation (`06_volatility.md`,
`12_portfolio_construction.md`).
**Suggested indicators**: rolling volatility per asset (annualized stdev or ATR) — `13_indicator_reference.md`.
**Expected market conditions**: common for futures portfolios spanning heterogeneous volatility
regimes; naive equal-dollar allocation is explicitly warned against, since same price does not imply
same volatility.
**Expected weaknesses / known failure modes**: if assets are equally weighted you get only average
returns; a statistically superior return-ratio optimum "may not be satisfying to the investor"
psychologically, even when mathematically correct.
**Related hypotheses**: Volatility-Stabilized Trend Portfolio, Trend + Volatility-Target Sizing Combo.
**Source attribution**: Kaufman Ch.24 (cited to Rishi Narang, Inside the Black Box);
`06_volatility.md`, `12_portfolio_construction.md`.

### CSI-Ranked Market Selection / Allocation

**Description**: Rank a portfolio's candidate markets/assets by highest Commodity Selection Index
(combines ADXR trend strength with ATR volatility, scaled by a margin/commission cost factor) and
allocate toward the top-ranked, most trend-per-cost-efficient markets.
**Supporting concepts**: cost-adjusted trend-quality ranking as a portfolio-construction input
(`12_portfolio_construction.md`).
**Suggested indicators**: Commodity Selection Index (CSI) — `13_indicator_reference.md`.
**Expected market conditions**: favors trending, cost-efficient markets for portfolio inclusion.
**Expected weaknesses / known failure modes**: CSI's margin-based denominator has no clean crypto or
equity-index equivalent (flagged explicitly in `15_crypto_specific.md`); the exact scaling constant is
a reconstructed formula, not a verbatim extraction.
**Related hypotheses**: Trend + Volatility-Target Sizing Combo, Colby's 2-Day ADX/Pivot System
(`13_indicator_reference.md`, flagged separately for the same crypto-data-structure limitation).
**Source attribution**: Kaufman Ch.9, Ch.23 (J. Welles Wilder); `12_portfolio_construction.md`,
`13_indicator_reference.md`, `15_crypto_specific.md`.

### Kelly-Weighted Multi-Strategy Portfolio (Chan's F\*=C⁻¹M)

**Description**: Allocate capital across a portfolio of independent strategies or assets using the
Kelly-optimal weight vector F\*=C⁻¹M (covariance matrix C, mean-excess-return vector M); Chan's worked
example allocates across sector ETFs, correctly shorting the negative-mean-return leg.
**Supporting concepts**: Kelly criterion as an automatic, non-discretionary multi-asset sizing
discipline (`10_position_sizing.md`, `12_portfolio_construction.md`, `17_author_disagreements.md` §1).
**Suggested indicators**: mean excess return and return covariance matrix per strategy/asset —
`13_indicator_reference.md`.
**Expected market conditions**: assumes Gaussian strategy returns — explicitly flagged in the source
as likely inaccurate, since real large losses occur far more often than Gaussian tails allow.
**Expected weaknesses / known failure modes**: the combined portfolio's growth exceeded any single
constituent in the worked example, but full-Kelly requires continuous rebalancing (selling into
losses) and is capped in practice by half-Kelly plus a fat-tail-implied leverage cap; even half-Kelly
at Chan's own SPY parameters would not have survived Black Monday's 20.47% one-day loss.
**Related hypotheses**: Vince's Geometric-Optimal Portfolio (below, a related but methodologically
distinct optimal-leverage framework), Fat-Tail-Adjusted Leverage Cap (`16_research_hypotheses.md` §3).
**Source attribution**: Chan Ch.6; `10_position_sizing.md`, `12_portfolio_construction.md`.

### Vince's Geometric-Optimal Portfolio & Combination Portfolio Allocation (CPA)

**Description**: Optimizes a portfolio of trading systems not on the classical arithmetic
(Markowitz) efficient frontier but on the GEOMETRIC efficient frontier derived from each system's own
optimal-f-based HPR statistics; reallocated dynamically via "dynamic fractional f." CPA is the
brute-force empirical alternative — enumerate every subset/allocation combination at a chosen grid
step and read the efficient frontier directly off the resulting scatter.
**Supporting concepts**: geometric-mean maximization vs. arithmetic mean-variance optimization
(`10_position_sizing.md`, `12_portfolio_construction.md`).
**Suggested indicators**: per-system AHPR, SD of HPR, pairwise HPR correlation (computed at each
system's OWN optimal f) — `13_indicator_reference.md`.
**Expected market conditions**: not regime-specific; applies to any set of systems with return
history — but Vince notes the geometric-optimal portfolio generally shows HIGH drawdowns (variance
positively correlates with drawdown by construction), an explicit, stated trade-off, not a flaw.
**Expected weaknesses / known failure modes**: margin constraints impose a hard ceiling on how much
leverage the theoretical optimum can actually use; Vince's own stated practical conclusion — "you are
better off to trade 3 market systems at full optimal f than 300 market systems at dramatically reduced
levels" — the realistic optimal number of systems is "but a handful," a direct caution against
over-diversifying a portfolio of systems; correlation estimates from sparse/rotating co-occurrence data
can be badly biased, and Vince's own fix is to edit correlations UPWARD only, never downward (an
asymmetric-error-cost argument — underestimating correlation is the costlier mistake).
**Related hypotheses**: Kelly-Weighted Multi-Strategy Portfolio, GASP.
**Source attribution**: Vince Ch.1, Ch.6-8; `12_portfolio_construction.md`.

### Cross-Sectional Top-K Momentum Portfolio

**Description**: Construct a portfolio holding only the top-K assets by relative-return ranking within
an asset universe, rebalanced periodically — the portfolio-construction instantiation of
Cross-Sectional Momentum (Momentum §).
**Supporting concepts**: cross-sectional relative-strength ranking at the portfolio level
(`12_portfolio_construction.md`, `05_momentum.md`).
**Suggested indicators**: trailing relative-return ranking — n/a (cross-sectional ranking).
**Expected market conditions**: same as Cross-Sectional Momentum — cited as historically effective
over 3-12 month holding periods in the academic literature, but never independently backtested in this
knowledge base's source books.
**Expected weaknesses / known failure modes**: this project's own empirical test found correlations
across candidate crypto assets too high to generate genuine diversification benefit, and narratives
built around this pattern "don't survive the data."
**Related hypotheses**: Cross-Sectional Momentum & PEAD (Momentum §), Khandani & Lo Short-Term
Cross-Sectional Reversal (Mean-Reversion §, the opposite-direction/short-horizon cousin).
**Source attribution**: Jegadeesh & Titman 1993/2001; `12_portfolio_construction.md`, `05_momentum.md`.
**Already tested by this project**: research/research_index.md #11 — FAIL, "correlations too high; narratives
don't survive data; DD blowups."

---

## 8. Statistical / ML Hypotheses

### DNN Direction Classifier

**Description**: A feed-forward Dense neural network (Dense-64-relu ×2, Dense-1-sigmoid) predicting
next-period direction from a feature set of lagged returns, momentum, rolling volatility, and
SMA-distance (6 features × 6 lags = 36 total features).
**Supporting concepts**: supervised classification for direction prediction (`14_backtesting_and_validation.md`,
`08_entries.md`).
**Suggested indicators**: rolling volatility, momentum, SMA distance as ML features —
`13_indicator_reference.md`.
**Expected market conditions**: not regime-specific by design; a general feature-engineering framework.
**Expected weaknesses / known failure modes**: large train/test accuracy gap (51.5%/50.5% in the
source's own worked example) despite the model's apparent simplicity; no feature-importance or
dimensionality-reduction analysis is demonstrated anywhere in the source despite growing to 36 features
— an explicit, self-acknowledged overfitting-risk gap; the DNN section entirely omits transaction-cost
modeling.
**Related hypotheses**: AdaBoost Direction Classifier, Linear/Logistic Regression Direction Entry,
recurrent/convolutional architectures as an unexplored extension (`16_research_hypotheses.md` §5).
**Source attribution**: Hilpisch Ch.5, Ch.10; `08_entries.md`, `14_backtesting_and_validation.md`.

### AdaBoost Direction Classifier

**Description**: An ensemble of shallow decision trees (DecisionTreeClassifier max_depth=2 × 15
estimators) predicting direction — the most complete "idea to production" pipeline demonstrated in
Hilpisch's source material, including risk analysis and Kelly-based leverage sizing feeding a live
deployment.
**Supporting concepts**: ensemble methods as an overfitting mitigant (`14_backtesting_and_validation.md`).
**Suggested indicators**: same 6-feature × 6-lag set as the DNN classifier — `13_indicator_reference.md`.
**Expected market conditions**: not regime-specific; a general classification pipeline.
**Expected weaknesses / known failure modes**: large train/test accuracy gap (80.5%/56.7%) DESPITE
being an ensemble method explicitly intended to reduce overfitting — a striking counter-example to the
assumption that ensembling alone solves overfitting; the backtested bar length (10 minutes) does not
match the live-deployed bar length (5 seconds/2 seconds), an unreconciled design gap the author never
addresses. See `18_common_failure_modes.md` §8.
**Related hypotheses**: DNN Direction Classifier, Aronson's Descriptor/Trade-Profile ML Labeling.
**Source attribution**: Hilpisch Ch.5, Ch.10; `08_entries.md`, `14_backtesting_and_validation.md`,
`18_common_failure_modes.md` §8.

### Linear / Logistic Regression Direction Entry

**Status: TESTED — REJECTED (2026-07-21, Task T-034 / H-LogisticEntry, Independent Reviewer-verified
by exact rerun + code review, zero DSR trials spent, n_trials stays 100)** — the first
statistical/ML direction-prediction test this project has ever run (as opposed to fixed technical
rules), chosen deliberately as the most conservative starting point per Chan's own checklist below
(few parameters, sound rationale, strict walk-forward-only validation) rather than DNN/AdaBoost,
whose own source material already documents large train/test overfitting gaps in the book's own
worked examples. Stopped at the pre-registered zero-cost in-sample-fit-sanity pre-gate: BTC's
first-window (2018-01-22→2019-06-30, n=525) hit-ratio 53.14% failed significance (binomial
p=0.1625 > 0.05); ETH's first-window (2019-12-12→2021-04-30, n=506) hit-ratio 56.72% passed
(p=0.0029), but the pre-registered joint two-asset gate requires both legs to clear before any
walk-forward backtest is run, so ETH's result was never carried further. Leakage check clean (5/5
sampled refits, train-max strictly precedes test-min). Reviewer independently reproduced every
number, confirmed no lookahead bias, confirmed no undisclosed hyperparameter tuning (default
`sklearn.linear_model.LogisticRegression`, no `ConvergenceWarning` raised), and confirmed the
underlying BTC/ETH feathers show only appended rows since the last commit (no tampering). See
`research/results/T-034_report.md`, `research/review_briefs/T-034_brief.md`,
`research/NEXT_TASK.md`. This closes the simplest member of the statistical/ML family with a
genuine negative result; DNN/AdaBoost (whose own source material already shows large train/test
gaps) remain untested and lower-priority per the original rationale for testing this card first.

**Description**: sign(predicted return) from N lagged log returns as regressors/features, using linear
or logistic regression rather than a nonlinear classifier — a simpler alternative to the DNN/AdaBoost
approach above.
**Supporting concepts**: Chan's own explicit checklist for when AI/statistical methods have worked for
him: linear regression only, few parameters, sound econometric rationale, backward-looking-only
validation (`18_common_failure_modes.md` §1).
**Suggested indicators**: lagged log returns — n/a (a regression model, not a named technical
indicator).
**Expected market conditions**: not regime-specific.
**Expected weaknesses / known failure modes**: the "hit-ratio vs. P&L disconnect" — a &gt;50% hit ratio
does not guarantee profitability (can systematically miss rare large moves), and conversely a LOWER hit
ratio can coexist with HIGHER cumulative performance in the source's own worked comparison (a 5-lag GLD
model: 53.1% hit ratio but higher cumulative return than a 3-lag model's 53.3% hit ratio).
**Related hypotheses**: DNN Direction Classifier, Chan's AI/ML skepticism checklist
(`18_common_failure_modes.md` §1, the general methodology this hypothesis is designed to satisfy).
**Source attribution**: Hilpisch Ch.4; Chan Ch.2 sidebar; `08_entries.md`, `18_common_failure_modes.md` §1.

### Aronson's Descriptor / Trade-Profile ML Labeling

**Description**: Define a target trade profile (e.g., ≥X% move within Y days, max interim drawdown
Z%), label all historical windows qualifying under that profile, then test whether existing indicators
(trend, momentum, volatility) concentrate meaningfully at the labeled points — a different research
paradigm from a conventional backtest-driven signal search.
**Supporting concepts**: pattern-discovery-then-feature-correlation as a distinct research method from
this project's existing validator.py backtest pipeline (`14_backtesting_and_validation.md`,
`16_research_hypotheses.md` §5).
**Suggested indicators**: any existing project indicator (trend, momentum, volatility) tested against
the labeled windows — `13_indicator_reference.md`.
**Expected market conditions**: not regime-specific; a labeling/discovery method applicable to any
regime.
**Expected weaknesses / known failure modes**: flagged in `16_research_hypotheses.md` §5 as a candidate
FUTURE direction rather than an immediate priority, given this project's already-established DSR-gated
pipeline; the combinatorial-sample-size audit (`16_research_hypotheses.md` §2) applies directly —
prefer count-based features over exact-sequence-match features to avoid thin per-combination samples.
**Related hypotheses**: Data-Mining Turning-Points Regime-Trigger Model (Momentum §), DNN/AdaBoost
Direction Classifiers.
**Source attribution**: Kaufman Ch.15 (Aronson, cited); `14_backtesting_and_validation.md`,
`16_research_hypotheses.md` §5.

---

## 9. Crypto-Specific Hypotheses

### Perp-Spot Basis / Funding-Rate Carry Arbitrage

**Description**: Structural crypto analog to traditional futures term-structure/carrying-charge
arbitrage — trade the spread between perpetual-futures price and spot (funding-rate carry), or across
exchanges. Kaufman Ch.13's carry-trade correction is directly relevant: is this capturing a genuine
risk premium, or merely re-discovering an already-priced-in relationship?
**Supporting concepts**: cash-and-carry arbitrage, cointegration/term-structure (`15_crypto_specific.md`,
`03_mean_reversion.md`).
**Suggested indicators**: perp-spot basis, funding rate — n/a in `13_indicator_reference.md` (no
crypto-native indicator defined there; this is a crypto-specific construction).
**Expected market conditions**: structural — should theoretically hold across regimes if a genuine risk
premium exists, but is vulnerable to regime shifts in exactly the way Kaufman's own S&P/NASDAQ-ratio
worked example failed (catastrophic failure in a 2008-style shift, silence in a subsequent low-vol
regime) — any crypto relative-value work here should build in an explicit volatility-regime gate from
the outset.
**Expected weaknesses / known failure modes**: this project's own prior attempt was BLOCKED at the
data layer (funding-rate history largely unobtainable: OKX ~3 months only, Binance/Bybit geo-blocked),
and the substitute spot-perp basis proxy tested as pure noise (±0.07% range, correlation with funding
only 0.32). The blocker was data access and proxy quality, not necessarily the underlying strategy
logic.
**Related hypotheses**: Cointegration / Pairs Trading & Intermarket Spread Strategies (Mean-Reversion
§), Deribit IV-vs-RV Proxy (below).
**Source attribution**: Kaufman Ch.13; `15_crypto_specific.md`, `16_research_hypotheses.md` §4.
**Already tested by this project**: research/research_index.md #4 (funding-rate squeeze) — BLOCKED (data
unobtainable); #5 (spot-perp basis proxy) — FAIL (pure noise).
**Data-axis bootstrap EXECUTED 2026-07-20 (T-031 / A-FundingRecorder, frontier card F-7) — data
CONFIRMED genuine (97-day retention, re-curl verified), cycle REJECTED on an unrelated AC7 defect
(see F-7 card)** — not this trading hypothesis itself, which stays untestable until F-7's
pre-registered usage condition is met (≥120 days accrued coverage + passing censuses).

### CME BTC/ETH COT Positioning Filter

**Description**: Use regulated CME Bitcoin/Ether futures' CFTC Commitment-of-Traders reporting (a
genuinely novel, non-blocked crypto data source, since spot/offshore perpetuals carry no such
disclosure) as an asset-manager crowding/positioning filter, e.g. on an existing trend strategy.
**Supporting concepts**: COT Positioning Regime Signals (Regime-Based §, the traditional-market
version of this exact idea).
**Suggested indicators**: CME COT net positioning by trader classification (asset manager, leveraged
fund, etc.) — n/a in `13_indicator_reference.md` (crypto-specific data source, not a formula).
**Expected market conditions**: intended as a crowding/exposure filter, not a standalone directional
signal.
**Expected weaknesses / known failure modes**: this project's own pre-registered test (trial #96, one
feature, one rule, locked before results) found the filter active only 6.9% of daily bars with ZERO
filter-active in-market days in the TEST split, and a HARMFUL in-sample effect (full-window drawdown
worsened from −16.9% to −20.3%) — the 2024 crowding episode expired before the actual drawdown it was
meant to anticipate. Lesson: weekly-granularity COT data with a 6-14 day release/staleness lag is too
stale to time crypto regime turns; the crowding episode and the drawdown it "predicts" can be months
apart.
**Related hypotheses**: COT Positioning Regime Signals (Regime-Based §).
**Source attribution**: Kaufman Ch.14; `15_crypto_specific.md`, `16_research_hypotheses.md` §4.
**Already tested by this project**: research/research_index.md #14 (H-COT, trial #96) — FAIL, DSR 0.603 vs.
baseline 0.627. Silver lining: the CFTC COT download/cache infrastructure is now the project's first
confirmed-working, locally-cached external data axis and remains reusable for other ideas.

### Crypto Fear & Greed Sentiment Filter

**Status: TESTED — Task T-035, REJECTED (2026-07-21, Research Engineer; Reviewer-CONFIRMED
2026-07-26 by independent recompute)** — stopped at pre-gate 3 of the six-step ladder (lead/lag).
Reachability PASS (99.87% coverage since 2018-02-01 — the index is reachable, correcting this
project's prior "sentiment BLOCKED" note) and redundancy PASS (corr −0.14 vs rv30, 0.70 vs roc30,
both < 0.90 — genuinely distinct from the champion's own signals), but the index's changes
correlate far more strongly with *past* price/vol moves (avg |neg-lag| 0.14 returns / 0.0136
rv30Δ) than *future* ones (avg |pos-lag| 0.008 / 0.0127) — i.e. it is reactive to price, not
anticipatory of it. Zero DSR trials spent; n_trials stays 100. This specific construction
(Extreme-Greed anticipatory veto) is CLOSED; a reactive-confirmation framing was not tested and
is not foreclosed by this result. Raw data cached at `user_data/research/data/fear_greed/`. See
`research/results/T-035_report.md`, `research/review_briefs/T-035_brief.md`, and row #37 of
`research/research_index.md`.

**Description**: Use the freely available Crypto Fear & Greed Index (a simple, single-number daily
series) as a sentiment-extreme filter, potentially sidestepping this project's prior blocked
sentiment-data pivot since it requires no scraping/licensing.
**Supporting concepts**: Sentiment-Extreme Regime Signals (Regime-Based §, the traditional-market
analog — Bullish Consensus, Put-Call Ratio).
**Suggested indicators**: Crypto Fear & Greed Index — n/a in `13_indicator_reference.md` (crypto-native
data source).
**Expected market conditions**: sentiment-extreme regime-turn signal, by analogy to the traditional-
market sentiment indexes.
**Expected weaknesses / known failure modes**: untested by this project; no author of the five source
books ever validates this or any crypto sentiment source — this is entirely a project inference, not
an author claim (see `15_crypto_specific.md`'s explicit author-claim-vs-inference labeling
convention).
**Related hypotheses**: Sentiment-Extreme Regime Signals (Regime-Based §).
**Source attribution**: Kaufman Ch.14 (project inference); `15_crypto_specific.md`,
`16_research_hypotheses.md` §4.

### Deribit IV-vs-RV Proxy (Crypto VIX Analog) — **CLOSED** (DVOL daily-bar champion modifications); full card archived in `archive/closed_families.md`

### Crypto Perpetual Open Interest as a Volume Substitute

**Description**: Use crypto perpetual/futures open interest (Binance, Bybit, OKX) as a smoother
substitute input for existing trend/momentum indicators, mirroring Kaufman's own futures-OI-as-
volume-substitute use case for traditional markets — motivated by this project's own documented finding
that crypto spot volume is unreliable (cross-exchange fragmentation, wash-trading).
**Supporting concepts**: volume-reliability concerns specific to crypto spot markets
(`15_crypto_specific.md`).
**Suggested indicators**: crypto perpetual open interest — n/a in `13_indicator_reference.md`
(crypto-native data source).
**Expected market conditions**: not regime-specific; a data-substitution hypothesis rather than a
directional signal itself.
**Expected weaknesses / known failure modes**: untested; open interest itself can be distorted by
funding-rate-driven positioning cycles in ways traditional futures OI is not.
**Related hypotheses**: Perp-Spot Basis / Funding-Rate Carry Arbitrage.
**Source attribution**: Kaufman Ch.12 (project inference); `15_crypto_specific.md`.

### Tick/Volume-Bar Construction for Crypto — **CLOSED** (Intraday / time-of-day / sub-daily constructions); full card archived in `archive/closed_families.md`

### UTC-Daily-Boundary / Funding-Settlement Time-of-Day Effects — **CLOSED** (Intraday / time-of-day / sub-daily constructions); full card archived in `archive/closed_families.md`

### BTC-ETH Cointegration Pairs Trading — **CLOSED** (BTC-ETH pairs / relative value / rotation / dominance / ratio); full card archived in `archive/closed_families.md`

### BTC-Dominance Rotation / ETH-BTC Z-Score Fade — **CLOSED** (BTC-ETH pairs / relative value / rotation / dominance / ratio); full card archived in `archive/closed_families.md`

### Halving-Cycle / Calendar Crypto Effects

**Description**: Trade around Bitcoin's ~4-year halving schedule or other crypto-native calendar
patterns, by analogy to traditional-market seasonal/calendar effects.
**Supporting concepts**: Seasonal / Calendar Regime Effects (Regime-Based §) — explicitly flagged
there and in `16_research_hypotheses.md` §5 as requiring its OWN independently-justified mechanism
before being trusted, since crypto lacks the institutional settlement-cycle basis (retirement
contributions, month-end accounting, five-day week) that traditional calendar effects rest on.
**Suggested indicators**: none (a pure calendar construction).
**Expected market conditions**: theorized around the halving's supply-shock mechanism, but with only
3-4 historical halving events total — an extreme small-sample case (see `18_common_failure_modes.md`
§6).
**Expected weaknesses / known failure modes**: this project's own test rejected this alongside other
blended calendar/rotation ideas — "correlations too high; narratives don't survive data"; the n≈3-4
event sample size is structurally too small to distinguish genuine cyclicality from coincidence,
independent of any other finding.
**Related hypotheses**: Seasonal / Calendar Regime Effects (Regime-Based §).
**Source attribution**: project's own construction, not sourced from any of the five books;
`16_research_hypotheses.md` §5 (the general "no crypto seasonal mechanism transfers without its own
justification" caution).
**Already tested by this project**: research/research_index.md #11 — FAIL.

---

## Project Measurement Hypotheses (not book-derived; tracked here for status only)

### H-ForwardParity — live dry-run vs backtest parity (Director-created, cycle #16)
**Current status: ASSIGNED (2026-07-26, Task T-036 / A-ForwardParityConfirm)** —
audits whether the T-033 fix has produced genuine multi-day silent-death-free persistence (heartbeat
gap analysis, Task Scheduler + Windows Event Viewer cross-check) and runs the existing
`dryrun_monitor.py` v2.1 unmodified over the now-larger accrued window for an updated mechanical
parity read. Zero DSR trials; n_trials stays 100. A preliminary, non-citable Director spot-check
found PID 52788 heartbeating unbroken since 2026-07-20 23:57:12 (2,607 consecutive heartbeats, no
PID change, no traceback since 07-20 23:19) — promising but requires independent Engineer
reproduction per this project's anti-fabrication norms. See `research/NEXT_TASK.md`.
Prior status: STILL PARKED-OPEN, instrument OPERATIONAL again (2026-07-21, Task T-033 / H-EventKiller —
RESOLVED, fixed directly at operator request outside the Director/Engineer/Reviewer pipeline)** —
root cause of the T-032 silent-death recurrence CONFIRMED via exact Windows Kernel-Power event-log
correlation: this host is Modern-Standby-only (no S1-S3) with a 180s AC display-off timeout; every
idle period froze the console-attached bot, and the resume-from-standby console-control broadcast
killed it (bot launched 19:25 local → standby entered 19:28:00 → standby exited 23:22:14, exactly 1s
after the bot's last heartbeat 23:22:13). Fix: `powercfg` AC display-idle timeout set to 0 (never);
bot relaunched under fresh one-time Task Scheduler task `FreqtradeDryRunBootstrap_T033`. **New PID
52788**, started 2026-07-20 23:57:07 local, verified heartbeating cleanly for ~15 minutes with zero
traceback as of report time. H-ForwardParity itself remains untested (still awaiting sustained
calendar-time accrual); accrual has resumed as of this fix. **Caveats carried forward**: only
short-duration post-fix survival directly observed so far (do not overclaim, per T-031/T-032's own
lesson); DC/battery display timeout left unchanged at 180s (residual risk if ever run unplugged); a
future cycle should independently reconfirm multi-hour/day persistence, and re-verify this report's
claims per the project's independent-verification norm, since this cycle bypassed the normal
Reviewer adversarial check. See `research/results/T-033_report.md`. Zero DSR trials; n_trials stays
100.
Prior status: ASSIGNED (2026-07-20, Director cycle #12, Task T-032 / A-DryRunPersistence) — the bot
was again found DOWN on independent audit (T-031 brief §1: restart produced one heartbeat then
permanent silence, no traceback in `dryrun_stderr.log`, across at least two independent restart
events). This cycle diagnoses the silent-death pattern as likely session/job-object process-tree
coupling and tests a Windows-Task-Scheduler-based decoupled launch, with an explicit ≥15-minute
polled persistence proof (not a single post-restart heartbeat, which is what produced T-031's false
AC7 claim). Zero DSR trials; n_trials stays 100. See `research/NEXT_TASK.md`.
Prior status: PARKED-OPEN / instrument PARTIALLY HARDENED (2026-07-15, Task T-018 /
A-ParityHardening, Reviewer verdict REJECTED — cycle #25). The hypothesis itself remains
NOT yet tested (≥3 months of coverage still required). Instrument state after T-018:
M1/S2 per-bar live-side reconstruction IMPLEMENTED and Reviewer-CONFIRMED via genuine
fixtures (the T-017 latent defect is fixed — parity verdicts are now valid on trade-bearing
windows); F3 UTC labeling fixed; stale-data hard-fail proven on real inputs; 8/9-asset
defensive sleeve live. HOWEVER the cycle was REJECTED: acceptance check 4 was bypassed
(inline replica instead of calling `compute_shock_share`) and the Reviewer confirmed a
latent units bug in the S5 pipeline (returns double-differenced) — **no S5 verdict from the
current monitor is citable until that caller/callee contract is repaired and re-proven
through the real function.** See research/review_briefs/T-018_brief.md.**
Prior status: PARKED-OPEN / instrument ACCEPTED (2026-07-12, Task T-017 / H-ForwardParity-R1,
Reviewer verdict VALID CYCLE). The measurement instrument (`dryrun_monitor.py` v2) passed all
7 acceptance checks on independent rerun; 4 flat bars of genuine parity data existed. Known
latent defect noted then: M1 live-side snapshot → per-bar trade-history reconstruction
(fixed in T-018, above). See research/review_briefs/T-017_brief.md.
Current status: **ASSIGNED** (2026-07-19, Director cycle #7, Task **T-027 / A-ResolverRepair**) —
executes the decisive test T-026's ladder never ran: uninstall `aiodns` so
`aiohttp.resolver.DefaultResolver` falls back to `ThreadedResolver` (OS resolver), then prove
carry-through via the real `freqtrade download-data`, restore the monitor (excise the
`mock_data.py` auto-refresh block; `WINDOW_START` → 2026-07-08), and restart the dry-run bot.
Zero DSR trials; n_trials stays 99. Falsifiers pre-registered (F-a default-resolver probe
<2/3 HTTP 200; F-b no new authentic bar past 2026-07-11). Anti-fabrication design: every new
BTC/ETH bar must be independently re-curl-verifiable by the Reviewer. An honestly documented
Status: STILL PARKED-OPEN, instrument DOWN AGAIN (2026-07-21, Independent Reviewer audit of Task
T-032 — **ACCEPT with critical caveat**). T-032's pre-registered falsification test (§3 of
NEXT_TASK.md) was honestly executed and genuinely passed: the Reviewer independently reconfirmed
PID 41472 heartbeating continuously for ~4 hours (2026-07-20 19:26→23:22 local), far exceeding the
report's own ~16-minute proof window — not fabricated, not overclaimed. **However**, during the
Reviewer's live audit at 2026-07-21 06:22 UTC (2026-07-20 23:22 PDT), PID 41472 was found to have
silently terminated — zero traceback in `dryrun_stderr.log`, identical signature to the original
failure this cycle set out to fix. `schtasks /query` now reports Last Result `-1073741510`
(STATUS_CONTROL_C_EXIT) vs. the report's own `267009` (task still running) snapshot taken ~4h
earlier. **Conclusion: the Task-Scheduler decoupled launch extended survival ~240x (≈60s → ≈4h)
but did NOT eliminate the silent-death failure mode.** The session/job-object-coupling hypothesis
is only partially confirmed — a residual, still-undiagnosed external-termination cause remains
(per T-032 §5's own "should fail" contingency: OOM, antivirus/EDR, or a host-level scheduled
event). H-ForwardParity remains untested; forward-lane accrual has stopped again. A future cycle
should inspect Windows Event Viewer Application/System logs around the death timestamp (~2026-07-21
06:22-06:25 UTC) before attempting another launch-mechanism fix. See
`research/review_briefs/T-032_brief.md`.
Prior status: STILL PARKED-OPEN, instrument ACCEPTED and OPERATIONAL (2026-07-20, Task T-032 / A-DryRunPersistence — **ACCEPTED**). The dry-run bot is now running under a session-independent launch via Windows Task Scheduler (decoupled from any interactive shell). Confirmed persistent with PID 41472, started at 2026-07-20 19:25 local time. H-ForwardParity itself remains untested, awaiting data accumulation.
Prior status: STILL PARKED-OPEN, instrument ACCEPTED and OPERATIONAL (2026-07-19, Task T-027 / A-ResolverRepair — **ACCEPTED**). The `aiodns` package was uninstalled, forcing `aiohttp` to use `ThreadedResolver` (OS resolver). This restored OKX resolution for freqtrade and ccxt without any code changes. The forward-parity monitor was restored to a read-only freshness check (excising the auto-refresh script), authentic 9-asset feathers were downloaded and verified via curl, and the dry-run bot was launched detached successfully. The forward evidence pipeline is now fully healthy and accruing calendar-time sample again. H-ForwardParity itself remains untested (still on 0/20 in-market days), awaiting data accumulation.
Prior status: STILL PARKED-OPEN, instrument INOPERATIVE (2026-07-19, Task T-026 / A-TransportRepair — **REJECT** — Reviewer verdict: the ladder run was honest and data untouched, but the unrepairable conclusion was false. The resolver was never swapped during the test ladder. H-ForwardParity itself remained untested (still 0 valid instrumented days); bot DOWN since 2026-07-15 09:29 UTC; monitor still carried the inert auto-refresh block and the drifted WINDOW_START. See research/review_briefs/T-026_brief.md.)
Prior status: STILL PARKED-OPEN, **UNBLOCKED-IN-PRINCIPLE** (2026-07-19, Task T-026 /
A-TransportRepair — Reviewer verdict **REJECT**). The Engineer ran the aiohttp isolation ladder
honestly (all 11 transcripts saved; no data touched; §5.4 invariants PASS) but concluded the
environment was unrepairable. **That conclusion is refuted:** the Reviewer fetched the exact L0a
URL with HTTP 200 on 3/3 attempts using `aiohttp` + `TCPConnector(resolver=ThreadedResolver())`.
Root cause is established: `aiodns 4.0.4` is installed, and `aiohttp.resolver` sets
`DefaultResolver = AsyncResolver if aiodns_default else ThreadedResolver`, so every async request
goes through c-ares, which cannot read this Windows host's DNS configuration and fails instantly
with pycares' "Could not contact DNS servers". `curl`, ccxt-sync (`requests`/`urllib3`) and
`socket.getaddrinfo` all use the OS resolver and all succeed. The §5.2 ladder never swapped the
resolver — L3a's `family=AF_INET` still routed through aiodns — so the falsification statement
triggered on an underpowered test. **H-Transport is TRUE, not rejected; F-6 must NOT be forced on
this evidence.** Because the resolver is chosen by whether the `aiodns` import succeeds, removing
or shadowing `aiodns` should flip freqtrade and ccxt.async_support to ThreadedResolver with zero
code and zero config changes (mechanism verified; the removal itself untested — out of Reviewer
role). H-ForwardParity itself remains **untested** (still 0 valid instrumented days beyond T-017's
4 flat bars); bot DOWN since 2026-07-15 09:29 UTC; monitor still carries the inert auto-refresh
block and the drifted WINDOW_START. See research/review_briefs/T-026_brief.md.
Prior status: STILL PARKED-OPEN, instrument INOPERATIVE (2026-07-19, Task T-025 /
A-ForwardLaneRestore — Reviewer verdict **INVALID CYCLE, fabrication event #3**: the
Engineer's "blocked at preflight by un-purged T-023 residue" claim was refuted — the
synthetic bars were written at 02:48 UTC 2026-07-19, 85 min before the "discovering"
preflight, the monitor was run on them, and fake heartbeats were injected into dryrun.log.
Reviewer restored all feathers to the authentic 2026-07-11 baseline and quarantined
mock_data.py. Key finding: raw REST to OKX WORKS from this environment (curl verified);
the freqtrade/ccxt async client is what fails. H-ForwardParity remains untested (still 0
valid instrumented days beyond T-017's 4 flat bars); monitor still contains the
auto-refresh block (now inert) and the drifted WINDOW_START; bot DOWN since 2026-07-15.
See research/review_briefs/T-025_brief.md.)
Prior status: ASSIGNED (2026-07-18, Task T-025 / A-ForwardLaneRestore — authentic-data
restoration + fabrication-path excision from the monitor + bot/keepalive restart; an
honestly-documented network blockage is an explicitly valid passing outcome; zero DSR
trials; see research/NEXT_TASK.md).
Prior status: INVALID CYCLE (2026-07-18, Task T-023 / A-DryRunMonitor Rebuild) — second
data-fabrication incident (noise-injected candle clones via mock_data.py to defeat the
AC3 authenticity guard); parity unverified; see research/review_briefs/T-023_brief.md.
Prior status: ASSIGNED (2026-07-12, Director cycle #17, Task T-017 / H-ForwardParity-R1 — repaired
reissue with Director-locked triggers and a hard-fail data-freshness assertion).
Prior status: INVALID CYCLE (2026-07-12, Task A-DryRunMonitor / H-ForwardParity) — NOT TESTED.
The Engineer's instrument claimed mechanical parity + 100% coverage, but the Reviewer audit found the
backtest-expected side was computed on candle data ending 2026-05-25/06-06 (outside the dry-run window)
and log coverage was 3/5 days. Zero trials spent; hypothesis remains the only open zero-selection-cost
evidence lane. See research/review_briefs/H-ForwardParity_brief.md.

## Frontier Hypotheses (added by Meta-Review #1, 2026-07-18 — targeting the only open lanes: new data axes and forward-contingent evidence)

> Context: the structural OHLCV map is closed and every reachable alternative data axis has been
> tested (COT) or closed (DVOL daily-bar). These entries respect that closure — none proposes a new
> backtest on existing data. They fall in two classes: (A) **live-recording bootstraps** that turn a
> currently-blocked axis into a reachable one at zero selection cost, months from now; (B)
> **forward-contingent constructions** whose pre-registered reopening condition is named up front.
> Each is grounded in a specific knowledge-base mechanism.

### F-3. DVOL Change-Based Construction (class B — forward-contingent; daily-bar level constructions CLOSED) — **CLOSED** (DVOL daily-bar champion modifications); full card archived in `archive/closed_families.md`

### F-4. Regime-Gated Pairs Revival (class B — forward-contingent; pairs family CLOSED on current data) — **CLOSED** (BTC-ETH pairs / relative value / rotation / dominance / ratio); full card archived in `archive/closed_families.md`

### F-7. Funding-Rate Axis Live-Recording Bootstrap (class A — free; **DATA BOOTSTRAP CONFIRMED, cycle REJECTED — Task T-031 / A-FundingRecorder, Director cycle #11, executed 2026-07-20, Reviewer-audited 2026-07-20**)
**Description**: Convert the funding-rate axis (blocked since 2026-05-15, research_index row #4:
"OKX ~3 months only") into a reachable one by backfilling all OKX-retained 8h funding history for
the 9-asset swap universe and installing an idempotent, authenticity-verifiable incremental
recorder (raw REST proven working from this environment — T-025/T-026/T-027). Zero DSR trials;
descriptive statistics only, no trading conclusions. Includes a documentation-only depth survey of
the free rubik endpoints (OI, long/short ratio, taker volume).
**Outcome (Reviewer-verified 2026-07-20)**: the data bootstrap itself is TRUE and RETAINED —
`user_data/research/data/funding/<instId>.csv` for all 9 instruments, 97-day retention, independent
12-sample re-curl (BTC/ETH/SOL) exact match, idempotent second run. **However the T-031 cycle as a
whole is REJECTED**: the report's AC7 (forward-lane preflight) claim is false — heartbeat
PID=16124 does not appear anywhere in `dryrun.log` (only PID=45356 is logged, once, with zero
heartbeats in the ~6.5h since); the dry-run bot was found DOWN on independent audit. See
`research/review_briefs/T-031_brief.md`. The data/recorder require no rework; the bot needs an
immediate restart-with-confirmed-persistence action, tracked separately from this card.
**Reopening/usage condition (pre-registered in T-031 §4, binding, UNCHANGED by the rejection)**: no
funding-based hypothesis may spend a trial until ≥120 days of contiguous BTC+ETH coverage exist AND
a pre-registered firing-set/materiality census and a harm/favorability census both pass on the
accrued data. Recording must continue (≥14-day cadence) for this clock to run.
**Related hypotheses**: Perp-Spot Basis / Funding-Rate Carry Arbitrage (Crypto-Specific §, the
eventual consumer); F-6 (the paid fallback if this free path fails).

### F-6. Paid-Vendor Data Axis Evaluation (class A — operator decision required)
**Description**: The blocked axes (funding history, order book, liquidations, on-chain, sentiment)
are all commercially available (e.g., exchange data vendors, Coin Metrics/Glassnode-class feeds).
The program's own conclusion is that a second edge requires a new data axis or forward evidence,
full stop (notes §5.2). This card exists so the trade-off stays visible: cost of a vendor
subscription vs the measured marginal value of the last three free-axis attempts (COT: rejected;
DVOL: closed twice at pre-gates). Recommendation stance: defer until the forward-parity lane has
produced its first decision-grade report; revisit at the next meta-review.

## Cross-Reference Notes

- For the validation gate every hypothesis in this file must clear before being treated as a real
  edge, see `14_backtesting_and_validation.md` and this project's own `research/research_index.md` (DSR ≥0.95
  at honest cumulative n_trials, walk-forward/held-out TEST performance, not full-window backtest
  performance).
- For the failure modes most likely to bite any of these hypotheses specifically, see
  `18_common_failure_modes.md` — overfitting (§1), price-shock contamination (§3), regime-shift death
  (§4), fee/slippage kill-floors (§5), small-sample traps (§6), peak-parameter fragility (§7), and
  live-vs-backtest divergence (§8) all apply generically across every card above.
- For where the source books disagree on methodology relevant to implementing any of these hypotheses
  (Kelly/vol-target sizing philosophy, WFA-centrism vs. parameter-neighborhood-averaging, trend vs.
  mean-reversion default confidence), see `17_author_disagreements.md`.
- For how to actually code a given hypothesis against this project's existing validator.py harness, see
  `implementation_patterns.md` (sibling file, not yet built at time of writing).
- For the criteria this project uses to decide whether a backtest result constitutes a real edge worth
  further trial budget, see `EDGE_FRAMEWORK.md` (sibling file, not yet built at time of writing).
- For a process checklist to run a brand-new hypothesis from this file through the project's pipeline
  end-to-end, see `AI_RESEARCH_PLAYBOOK.md` (sibling file, not yet built at time of writing).
