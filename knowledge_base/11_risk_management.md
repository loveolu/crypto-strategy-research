# Risk Management

Portfolio- and system-level risk management, synthesized from five extracted knowledge bases: Vince (*The Mathematics of Money Management*), Kaufman (*Trading Systems and Methods*), Pardo (*Evaluation and Optimization of Trading Strategies*), Chan (*Quantitative Trading*), and Hilpisch (*Python for Algorithmic Trading* — broker execution/account-mechanics material, §10). This file covers risk **frameworks** — ruin, drawdown, required capital, VaR, risk-adjusted return ratios, event/price-shock risk, utility theory, live-performance monitoring, and broker-level execution/account-mechanics risk. For detailed stop-loss/exit **technique** taxonomy (trailing-stop constructions, volatility stops, profit targets, etc.), see `09_exits.md`. For Kelly/optimal-f/vol-targeting **position-sizing derivations**, see `10_position_sizing.md` (this file references those results only insofar as they bear on ruin/drawdown/leverage risk). For correlation/diversification at the multi-asset **portfolio-construction** level, see `12_portfolio_construction.md`.

---

## 1. Stop-Loss Philosophy at the Risk-Management Level

This section addresses *why* stops exist as a risk-control device and how each author frames that rationale — not the technique taxonomy itself (see `09_exits.md` for the full inventory of stop constructions: fixed-percentage, volatility-multiple, support/resistance, Kase Dev-Stop, etc.).

**Kaufman's framing**: a stop-loss is one of several tools for controlling *individual trade risk*, but its value is explicitly strategy-type-dependent, not universal. Kaufman's stated summary rule: "stop-losses work for trending systems in trending markets; [they are] bad for non-trending markets or mean-reversion systems," while the mirror-image tool, profit-taking, "works for mean-reversion/short-term strategies; bad for trending markets or long-term trend strategies" (Kaufman, Ch.23). The two tools are explicitly **not interchangeable** across strategy types. Kaufman also gives a random-walk baseline test for whether a stop rule has genuine value at all: using random numbers, `(number of times a stop is hit) × (distance of the stop)` is roughly constant — a real stop rule must beat this random baseline to be considered informative rather than an artifact of placement distance (Kaufman, Ch.23). Kaufman is explicit that whether stops "work" at all is unclear/debated in the literature — "stops sometimes execute at the worst price of the day, sometimes save a trader from disaster" — but his own judgment is that volatility-adaptive stops are "most likely to work" (Kaufman, Ch.23).

**Chan's framing — the stop-loss-as-fallacy sidebar**: Chan explicitly challenges the common belief that imposing a stop-loss on every trade prevents catastrophic portfolio losses. His reasoning: during a genuine catastrophic/discontinuous event, prices gap; a stop-loss order fills at a price far worse than pre-event levels, so exiting at that point **realizes** the catastrophic loss rather than avoiding it. Chan gives an explicit conditional rule: a stop-loss is beneficial **only if** you believe you are in a momentum/trending regime (price will likely continue worsening); if instead you believe you are in a mean-reverting regime, a stop-loss is **harmful** because it crystallizes a loss that would otherwise have reverted. His own heuristic for distinguishing the two regimes: price moves driven by news/fundamentals imply momentum ("don't stand in front of a freight train" — the move to a new equilibrium is irreversible absent a fundamental reversal); price moves with no apparent fundamental cause imply a liquidity event (forced liquidation, short-covering) where mean-reversion to prior levels is likely (Chan, Ch.6).

**Vince's framing — stops as an unstated position-sizing decision, not developed as technique**: Vince's book does not treat the stop-loss as a primary risk tool at all; instead, the entire apparatus of optimal f is presented as *the* risk-control mechanism — position size, not stop placement, is what determines the "amount of rope." Vince does note in a footnote that a **known, capped worst-case loss** (e.g., via a fixed day-trading stop, or via long options as a structurally capped-liability instrument) is "extremely handy from a money-management, particularly an optimal-f, standpoint," because it lets f-in-dollars be computed exactly as `dollars at risk per unit / optimal f`, and — per a further footnote — helps keep a trader closer to the true peak of the f-curve by eliminating the risk of tail losses beyond the assumed worst case (Vince, Ch.2). Vince's three stated *structural* defenses against the "unlimited liability + infinite horizon = certain ruin" axiom are: (1) trade only limited-liability (capped-loss) vehicles, such as long options; (2) don't trade forever; (3) pre-commit, in writing, to a profit level at which you permanently stop trading unlimited-liability instruments (Vince, Introduction/Ch.1). These are risk-*philosophy* statements, not stop-placement technique.

**Pardo's framing — the stop as the first of three defined risk levels**: Pardo formally defines a three-tier risk taxonomy (Pardo, Ch.5), each level given its own explicit definition:
- **Trade risk**: "the possibility of financial loss from an individual market position."
- **Strategy risk**: "the possibility of financial loss from the use of a trading strategy."
- **Portfolio risk**: "the possibility of financial loss at the portfolio level (potentially multistrategy, multiple time frame, and multimarket) from the sum total of all trading therein."

Pardo situates the "risk stop" as the trade-level control within this taxonomy: "a stop order that is entered at inception and is maintained through the life of the position... if the price of the risk stop is touched or exceeded, the position is unconditionally liquidated" (Pardo, Ch.5). Pardo's guiding principle for the whole risk framework: "the essence of good risk management is to risk as little trading capital as necessary so as to maximize profit" (Pardo, Ch.5). Pardo explicitly flags two reasons realized loss can exceed the nominal stop distance — slippage, and overnight/gap risk, where a GTC stop becomes a market order at the next tradable price if the open gaps through it (Pardo, Ch.5) — this is the trade-level seed of the event/price-shock risk discussed in §7 below. The strategy-risk tier is elaborated via the Strategy Stop-Loss (§9.1 below); the portfolio-risk tier is elaborated via Portfolio Maximum Drawdown (`12_portfolio_construction.md`).

**Cross-reference**: the full stop-construction inventory (trailing stops, volatility-multiple stops, Kase's Dev-Stop, profit targets, scaling in/out) is documented in `09_exits.md`. This section preserves only the risk-framework-level rationale for *why* a stop exists and *when* the philosophy argues for or against using one.

---

## 2. Risk of Ruin

Ruin is treated fundamentally differently across sources: Vince treats it as a philosophical/structural certainty under specific conditions rather than deriving closed-form gambler's-ruin equations; Kaufman gives the classical closed-form equations directly.

### 2.1 Vince's treatment (philosophical, not closed-form)

Vince's central axiom: **"unlimited liability + infinite time horizon = certain ruin"** (probability of ruin → 1), where unlimited liability is defined precisely (Ch.5) as a distribution of outcomes with the left (adverse) tail unbounded to -∞. This holds even for a positive- or zero-expectation game, absent an upper absorbing barrier (a pre-committed stop-and-quit target) or a single, non-repeated play (Vince, Ch.1). Vince's three stated defenses are given in §1 above.

**Explicit gap, flagged by Vince's own extraction**: "this book does not derive or present classical closed-form risk-of-ruin equations in the main text, despite discussing risk of ruin extensively conceptually." Classical closed-form risk-of-ruin equations are referenced conceptually (Ch.2 footnote, Ch.5) but never derived — Vince develops only his own "parametric risk of ruin = 1 for unlimited liability + infinite horizon" argument, not the standard finite-sample gambling-theory formulas (Vince, Master_Summary — Open Questions #2). This gap is filled by Kaufman below.

**Vince's related, quantified claim — drawdown as a proxy for ruin risk**: "the drawdown you can expect with fixed fractional trading, as a percentage retracement of your account equity, historically would have been at least as much as f percent" — i.e., if f = .55, expect historical drawdown ≥ 55% of equity, because hitting the single biggest loss while trading at optimal f produces exactly that percentage loss by construction (Vince, Ch.1). Vince's own analogy: "Optimal f is like plutonium. It gives you a tremendous amount of power, yet it is dreadfully dangerous" (Vince, Ch.1). See §3 for the full drawdown treatment.

### 2.2 Kaufman's treatment (closed-form gambler's-ruin, plus extensions)

**Equal win/loss case** (standard gambler's-ruin form):
```
Z = [(1−P)/P]^c
```
where Z = risk of ruin (0 to 1), P = proportion of winning trades ("trader's advantage"), c = initial investment expressed in units (fractional units allowed for smaller bet sizing) (Kaufman, Ch.23).

**Worked example**: P=0.60 (60% win rate), $10,000 capital as 1 unit → risk of ruin ≈ 66%. Doubling capital to $20,000 (c=2 units, same P) → risk of ruin ≈ 43%. **Stated relationship**: greater trader's advantage OR greater capital → smaller risk of ruin (Kaufman, Ch.23).

A **goal-adjusted version** incorporates a profit goal G (in units of trading capital) at which trading would stop — risk of ruin decreases as the goal G is set closer to current capital (Kaufman, Ch.23; exact combining notation for this variant was not recoverable from the extraction — flagged as a gap).

**Unequal wins/losses (cited to Fred Gehm)**: because trading — especially conservation-of-capital/trend systems — typically has more losing trades than winning ones and must win much bigger on average than it loses, the equal-payout formula does not apply directly. Defined terms: CT = total capital available; CR = cutoff/ruin capital level (CR < CT); L = CT − CR = capital available to be risked; M₁ = expected mean return per trade = Σ(PLi × pi); M₂ = expected squared mean return per trade = Σ(PLi² × pi). Risk of ruin is computed from M₁, M₂, and L; qualitatively, **risk of ruin increases as a target objective/goal level L increases**, mirroring the equal-payout case. **Flagged gap**: "the chapter's own exact combining equation for this step did not extract cleanly" — preserved as a gap rather than invented (Kaufman, Ch.23).

**Vince's modified risk-of-ruin (spreadsheet form, cited by Kaufman to Ralph Vince via Peter Griffin's blackjack-theory approximation)** — note this is Kaufman's own extraction of a *different*, spreadsheet-oriented Vince formula than the empirical-optimal-f apparatus documented in `10_position_sizing.md`. Defined terms, in calculation order: AvgWin/AvgLoss (average winning/losing trade, $); Investment; ProbWin/ProbLoss (sum to 1); MaxRisk (max fraction of investment that can be lost, e.g., 0.25); AvgWin% = |AvgWin/Investment|, AvgLoss% analogous; `Z = ProbWin×AvgWin% − ProbLoss×AvgLoss%`; `A = sqrt[ProbWin×(AvgWin%)² + ProbLoss×(AvgLoss%)²]`; P = a function of Z/A (mapped through a probability transform not fully recoverable — one worked correspondence: Z/A=0.13484 → P=0.56742); final Risk of Ruin = a function of P and MaxRisk (final combining formula **not recoverable from extraction** — flagged as a gap; full worked table preserved instead) (Kaufman, Ch.23).

**Worked Table 23.15 (6 cases)**, the authoritative record of this method's behavior:
- Case 1 (benchmark: $10,000 investment, $400 avg win, $200 avg loss, 40%/60% win/loss, 25% max risk) → Risk of Ruin ≈ 10.16%.
- Case 2 (investment halved to $5,000) → 31.88%.
- Case 3 (investment halved again to $2,500) → 56.46%. **Finding**: halving investment size roughly triples-to-quadruples risk of ruin.
- Case 4 (AvgWin reduced $400→$350) → 25.35%.
- Case 5 (AvgWin further reduced to $325) → 47.00%.
- Case 6 (AvgWin held at $325, MaxRisk tightened 25%→15%) → 63%. **Counterintuitive finding, explicitly flagged by Kaufman**: tightening the allowed max-risk threshold, holding everything else constant, *increased* computed risk of ruin — interpreted as: a tighter ceiling combined with an already-weakened edge leaves less room to survive the same-sized adverse swings, rather than more protection (Kaufman, Ch.23).

**Accuracy vs. sample size (Table 23.16, Monte-Carlo, credited to Moritz Seibert)**: even a strategy with a genuinely strong long-term Information Ratio of 3.0 still has a **34% chance of showing a net loss after only 10 trades** (48% at IR=0.50/10 trades); this probability falls toward 0% only as trade count grows into the hundreds. Explicit caveat: this table used an idealized random process and does not capture real trading's characteristic long streaks or price shocks — its purpose is illustrating small-sample uncertainty, not precise forecasting (Kaufman, Ch.23).

### 2.3 Cross-reference

Kelly-formula-derived leverage (Vince's optimal f, Chan's `f = m/s²`) is the primary *preventive* lever against ruin in both books' frameworks, but the formal Kelly derivations themselves are documented in `10_position_sizing.md`. This section covers only the ruin-probability math directly.

---

## 3. Drawdown Mathematics

### 3.1 Vince's treatment

**Core empirical fact, stated repeatedly**: minimum historical drawdown ≥ f (as a % of equity) when trading at optimal f, because hitting the single biggest historical loss while at optimal f produces exactly that percentage loss by construction (Vince, Ch.1). **Stated paradox**: the better a system (the higher its optimal f), the higher its minimum historical drawdown will be.

**Empirical range, stated as near-universal from Vince's own experience**: "you will have enormous difficulty finding a portfolio with at least 5 years of historical data... with any less than a 30% drawdown in terms of equity retracement" when trading optimal f across all components — "expect to be nailed for 30% to 95% equity retracements," requiring "enormous discipline" that "very few people can emotionally handle" (Vince, Ch.1).

**Diversification does NOT fix worst-case drawdown**: an explicit, repeated correction of what Vince calls a "prevalent misconception." Diversification can *buffer* drawdowns (more trials/plays in the same time, raising total profit) but **cannot eliminate worst-case drawdown**, and "in some instances, may actually increase [it]" (Vince, Ch.1). His headline worked example: two coin-toss games combined at correlation −1.0 produce optimal f = .44 and geometric mean 1.67 (roughly 10x the standalone game's growth rate) — but worst-case historical drawdown for the combo is ≥44%, *higher* than the standalone game's ≥25%. **"Diversification, if done properly, is a technique that increases returns. It does not necessarily reduce worst-case drawdowns. This is absolutely contrary to the popular notion"** (Vince, Ch.1). The geometric-optimal portfolio (Ch.7), by its own defining condition (`AHPR−1 = Variance`), is explicitly stated to "tend to have HIGH drawdowns" — "when we perform the exercise of diversification, we should view it as an exercise to obtain the highest geometric mean rather than the lowest drawdown, as the two tend to pull in opposite directions!" (Vince, Ch.7/Ch.8).

**Diluting f trades drawdown asymmetrically against you**: trading a fraction of optimal f reduces drawdown only **arithmetically**, while returns are reduced **geometrically** — an unfavorable, asymmetric trade-off (Vince, Ch.1). Static fractional f keeps dispersion (and thus drawdown character) constant; dynamic fractional f (the split-equity technique) instead makes the *effective* fraction of full f rise toward 1 as equity grows and fall toward 0 as equity approaches a fixed inactive floor — an approach Vince frames as inherent portfolio insurance (Vince, Ch.8; full mechanics belong to `10_position_sizing.md`, but the risk-shape implication — dispersion that shrinks automatically in drawdowns — is a risk-management property worth noting here).

**Drawdown *duration*, not just depth**: Vince's empirical claim (Ch.2), stated as a general finding: "if you are trading at the optimal f level... the time [of] the longest drawdown... takes to elapse is usually **35 to 55% of the total time** you are looking at. This seems to be true no matter how long or short a time period you are looking at!" Applies to both single systems and full portfolios. Practical recommendation: expect to be within the maximum (longest) drawdown for roughly 35-55% of a program's life — "knowing this before the fact allows us to be mentally prepared to trade through it" (Vince, Ch.2). This connects to the arc-sine laws (Ch.2): for an idealized 50/50 equal-payoff zero-expectation game, the equity curve is *least* likely to spend equal time on both sides of breakeven, and *most* likely to spend nearly all its time on one side — a finding Vince argues applies "in spirit" (not exactly) to real trading once the zero-expectation reference line is replaced by a sloping (arithmetic-mean, constant-contract) or curving (geometric-mean, fixed-fractional) expectation line.

### 3.2 Pardo's treatment — MDD deep-dive and the Mandelbrot/fractal caveat

**Definition**: Maximum Drawdown (MDD) = "the dollar value of the largest decline from equity high to a subsequent equity low." Called **"the single most important measure of risk for a trading strategy"** — larger and more consequential than either per-trade risk or overnight risk in aggregate, because of its potential to wipe out an account entirely if undercapitalized (Pardo, Ch.12).

**Two named sources of MDD estimation error, explicit**:
1. **Volatility mismatch**: if historical-simulation volatility was *lower* than subsequent real-time volatility, real drawdowns will likely exceed the historical MDD estimate, risking undercapitalization. If historical volatility was *higher*, real drawdowns will likely be smaller than the historical MDD, producing safer-but-capital-inefficient overcapitalization. Pardo's stated preference: **"Overcapitalization and underperformance... is a better situation than undercapitalization and the consequent risk of ruin. It is best to avoid both conditions, however"** (Pardo, Ch.12).
2. **Statistical/mathematical limitations — the Mandelbrot/fractal caveat, explicit**: Pardo cites the field of "robust statistics" — small-sample statistics (as most trading-strategy simulations necessarily are) are inherently "fuzzier"/higher-variance than large-sample statistics. More significantly, Pardo cites **Benoit Mandelbrot's finding (fractal geometry) that financial time series follow a fractal, not Gaussian/normal, distribution** — meaning the standard statistical assumptions embedded in most performance/risk calculations, *including MDD itself*, are "in error to some degree or another," at a level Pardo characterizes as potentially more serious than simple sample-size fuzziness. Pardo's own stated epistemic conclusion, not resolved further in the book: **"the most accurate measure of maximum drawdown that we can derive with current statistical measures is likely to remain to some extent inaccurate"** (Pardo, Ch.12).

**MDD in context — diagnostic framing (explicit)**: compare MDD to average/minimum drawdown — tighter clustering suggests a more robust model; an MDD that is, say, 3x the average drawdown is not automatically disqualifying, but its cause should be understood. It is a **positive/expected** sign if MDD occurred during genuinely adverse conditions (extended congestion or extended volatile/choppy activity — cited as the typical settings for max drawdown across most strategies). It is a **warning sign** if MDD occurred under conditions indistinguishable from the strategy's own best-performing conditions (e.g., mid-strong-trend for a trend strategy) — potentially grounds for redesign or abandonment if unexplainable (Pardo, Ch.12).

**Maximum run-up (MRU)** — the positive mirror of MDD: "the largest improvement in trading equity between an equity low and a subsequent equity high." Periods of MRU define the strategy's *optimal* operating conditions (typically strong trend + high volatility + clean swings — the same conditions favorable to MDD-avoidance). Psychological warning: a big run-up can breed "damaging euphoria and a false sense of confidence," just as damaging to discipline as a big drawdown's fear (Pardo, Ch.12).

**Consistency framework**: the more consistent a strategy across profit/loss, wins/losses, long/short trades, and winning/losing runs, the more robust it is likely to be. Pardo gives three evaluation techniques: (1) avg/StDev/max/min per category; (2) remove the single maximum value from a category and recompute the average — a sharp drop (1-2 StDev) signals excessive reliance on one outlier; (3) check even distribution across the full historical timeline (concentration is a red flag unless explainable by an identifiable market-condition shift) (Pardo, Ch.12).

### 3.3 Kaufman's treatment

Kaufman treats drawdown primarily as an input to risk-adjusted return ratios (§6) and as a diagnostic of overfitting rather than developing separate drawdown mathematics. Key points:
- **Understated risk from optimized backtests**: an optimized system's apparent low risk is frequently an artifact of favorable price-shock exposure or overfitting rather than genuine low risk; "the erroneously low risk estimate is fatal to trading because it allows overleveraging and overconfidence" — risk *understatement*, not return overstatement, is explicitly framed as the more dangerous consequence of overfitting (Kaufman, Ch.21).
- **Maximum drawdown as a capitalization metric**: "can be very erratic and is not likely to be the largest risk seen in the future," but gives a rough minimum-capital estimate; an *unusually small* max drawdown is itself flagged as a possible sign of overfitting or too-short a test period. Recommendation: use the *average* maximum drawdown across a range of parameter tests, not the single best result. **Stated capitalization rule of thumb: capitalize a futures account at roughly 3x the maximum drawdown** (Kaufman, Ch.21) — directly consistent with Pardo's 2-3x rule in §4 below.
- **Time-in-market as risk reduction**: less market exposure reduces exposure to unpredictable price shocks; Kaufman states plainly that being out of the market is "the only defense against price shocks," and recommends preferring, between similarly-performing parameter sets, the one that spends less time in the market (Kaufman, Ch.21).
- **Drawdown-based downside risk (Ch.2)**: the standard deviation of daily equity drops below the prior peak gives a probability of a given drawdown size, but Kaufman flags a caveat — using only drawdowns discards the information that unusually large *profits* can also indicate elevated risk; with limited data, using the full (gain+loss) distribution is more robust (Kaufman, Ch.2).
- **The "50% gain doesn't recover a 50% loss" compounding trap**: a system with a 100% gain phase followed by a 50% loss phase, repeated twice a year on a fully compounded account, ends the year back at the starting value — "a lot of work for no return" (Kaufman, Ch.23).

---

## 4. Required Capital

Pardo's Ch.12 (extending Ch.5, reused again in Ch.14) gives an explicit, escalating-conservatism formula family for required capital, all keyed to a multiple of MDD.

**Base formula**: `RC = Margin + Risk`, where Risk = MDD. Worked example: margin $10,000, MDD $15,000 → RC = $25,000 — described as the **bare minimum**, since the account can survive one more max-size drawdown but the *next* trade after that must be a winner or the account cannot continue (Pardo, Ch.12).

**More conservative (2x MDD)**: `RC = Margin + (MDD × 2)`. Example: → RC = $40,000 — survives a $15,000 drawdown with $25,000 left, buying room for further losing trades without requiring an immediate win (Pardo, Ch.12).

**Even more conservative (3x MDD)**: `RC = Margin + (MDD × 3)`. Example: → RC = $55,000 (Pardo, Ch.12).

**Reasoning given in the text for choosing the multiplier, explicit**: the degree of MDD multiplication is a function of (a) personal risk tolerance/preference and (b) confidence in the accuracy of the original MDD estimate — given the acknowledged Mandelbrot/fractal statistical uncertainty in the MDD figure itself (§3.2 above). Pardo's single strongest, most explicit warning in this domain: **"Undercapitalization has been observed to be one of the primary causes of trading failure"** — erring conservative (i.e., toward the higher multiplier) is explicitly recommended (Pardo, Ch.12).

**Alternate framing from Pardo's Chapter 5** (as consolidated in `Risk_Management.md`), using a "Safety Factor" rather than a bare multiple, and demonstrating why even a single safety factor can be inadequate: `Strategy Stop = MDD × Safety Factor`; `Required Capital = Margin + (MDD × Safety Factor)`. A worked **stress-test example** shows an account capitalized with a single 1.5x safety factor (margin $15,000, MDD $40,000, factor 1.5 → RC = $75,000) can still be wiped out by a $50,000 drawdown, followed by a partial +$15,000 recovery, followed by another $40,000 drawdown — i.e., back-to-back drawdowns can exceed even a seemingly conservative single-multiple buffer. The **doubled-conservatism formula**, `RC = Margin + (MDD × Safety Factor × 2)`, is shown to survive the identical stress scenario with $60,000 remaining after both hits (Pardo, Ch.5/Ch.12 consolidated).

**Risk-Adjusted Return (RAR), built directly on the required-capital denominator**: `Annualized RAR = Annualized Profit / (Margin + Risk)`. Pardo's central principle: **"Profit can not be correctly assessed without reference to its cost. The primary cost of profit in trading is its risk."** RAR can be improved two ways — raising profit at constant risk, or lowering risk at constant profit — both equally valid. Worked contrast: Strategy A ($10,000 profit / $200,000 risk → RAR 5%) vs. Strategy B ($5,000 profit / $2,500 risk → RAR 200%) — B is dramatically superior despite smaller absolute profit (Pardo, Ch.12).

**Reward-to-Risk Ratio (RRR)**: `RRR = Net Profit / Maximum Drawdown`. Worked example: $25,000/$5,000 = 5.0. **Rule of thumb: RRR should be 3 or better** (Pardo, Ch.12).

**Model Efficiency (ME)**, a distinctive Pardo measure built on "Perfect Profit" (PP — the theoretical sum of every price swing captured by buying every bottom and selling every top, an unachievable ceiling): `Model Efficiency = Net Profit / Perfect Profit`. Worked example: $25,000/$300,000 → 8.33%, characterized as "actually quite good." **Stated rule of thumb: MEs of 5% and better are considered very good.** A *stable* ME across years — even while raw dollar profit varies — is a positive robustness signal, since PP itself scales with actual market opportunity (Pardo, Ch.12).

**Kaufman's convergent rule of thumb**: capitalize a futures account at roughly **3x the maximum drawdown** (Kaufman, Ch.21) — directly consistent with Pardo's most conservative multiplier, arrived at independently.

---

## 5. Value at Risk (VaR)

Source: Kaufman, Ch.23. **Three named VaR methodologies, explicit**: variance-covariance, historical, and Monte Carlo (Kaufman does not develop the Monte Carlo form in detail in the extraction; the historical and variance-covariance forms are given in full).

**Definition/use case**: the probability that current portfolio positions will produce an unacceptably large loss over the next few days, computed from historical data — illustrated via a worked bank scenario ("Bank Two") holding large short fixed-income futures positions plus 50%-hedged FX exposure, subject to a policy capping daily loss at 0.5% of cash value. **Inputs**: cross-correlations between exposed markets, position sizes, market volatilities, forecast time horizon, and a confidence interval (Kaufman, Ch.23).

### 5.1 Variance-Covariance VaR (2-asset form, cited to Longerstaey/RiskMetrics)

```
VaR = sqrt[ (σ₁X₁)² + (σ₂X₂)² + 2ρ₁₂(σ₁X₁)(σ₂X₂) ]
```
(reconstructed shape from the worked numeric example — the book's own inline notation did not extract cleanly), where σᵢ = std dev of the return series for market i, ρ₁₂ = cross-correlation between the two return series, Xᵢ embeds position size/market-value exposure.

**Worked example**: EURUSD position (USD 1.25mm market value, daily σ=0.565%) and a EUR 1mm 10-yr Eurobund position (USD 1.25mm market value, daily σ=0.605%); at 1.65 std devs (95% confidence, assuming normality): EURUSD 1-day risk ≈ USD 11,646; Eurobund 1-day risk ≈ USD 12,478. **Combined VaR is explicitly less than the simple sum** of the two individual risks because the two markets' correlation is −0.27 (a "noticeable offsetting effect") (Kaufman, Ch.23).

### 5.2 Generalized Multi-Asset VaR (n-asset form)

For n assets: VaR combines Z (confidence interval, e.g., 1.65 std devs for 5% one-tailed probability), T (VaR horizon in days, e.g., T=5), Wᵢ (weighting/relative position size), Pᵢ (current price of asset i on day t), σᵢ (annualized volatility), and ρᵢⱼ (cross-correlation between markets i and j). **Flagged gap**: "the chapter's own inline equation for combining terms across 3 assets did not extract cleanly" — variable list preserved, combining formula not recoverable. Annualized volatility is reconstructed from the standard published form (consistent with the chapter's own statement): `σ = StdDev(price changes over n days) × sqrt(252)` (252 trading days used for annualization). **Practical implementation note, explicit**: VaR should be calculated before the close; if it exceeds a threshold, exposure should be reduced the same day (Kaufman, Ch.23).

### 5.3 Generalized (probability-of-loss) VaR form (cited to Kritzman and Rich, 2002)

Probability of loss at horizon T is a function of the cumulative percentage loss threshold, cumulative expected return, and cumulative standard deviation, passed through the cumulative normal distribution function (Excel's NORMDIST). **Key methodological point, explicit**: compounding of periodic returns produces a *lognormal* distribution, while the continuous returns/std-dev used inside the calculation are *normally* distributed. Given a chosen probability Z (e.g., 5% → 1.65 std devs), the calculation solves for the threshold loss size instead of the probability. **Explicit caveat**: the resulting loss-at-horizon figure ignores any larger losses that might occur *within* the period if T>1 day — "losses during the period will always be at least as large as the loss at the end of the period" (Kaufman, Ch.23). (The source's own formula references natural-log base "e = 2.7128" — an apparent typo for 2.71828, preserved verbatim per the extraction's own flag.)

### 5.4 Historical VaR (Kaufman's recommended practical method)

**Author's practical recommendation, explicit**: the historical method is easier, more intuitive, and spreadsheet-implementable, with the caveat that "the result is only accurate when the past data represents what is likely to happen in the future" (Kaufman, Ch.23). Worked procedure (Table 23.2, 7-market futures portfolio):
1. List markets, current position sizes (signed, negative=short), conversion factors, FX values, current prices, and ~99+ days of historical prices.
2. Compute each market's daily return using the *current* position size against historical price changes.
3. Average the per-market returns into a single portfolio-return column for each day.
4. Sort the portfolio-return column smallest to largest.
5. **The Nth-percentile row IS the VaR** — with 100 days of data, the 5th-smallest entry is the 5% VaR (worked result: −0.0473, i.e., a stated 5% chance of losing 4.73% "today").

**Mathematical restatement, 5 steps (explicit)**: (1) given n assets/positions x₁...xₙ; (2) compute each asset's return over the past k days; (3) compute total portfolio return per day (converting FX/futures conversion factors to a single currency); (4) find the mean and std dev s of the return series R over the k days; (5) given a confidence level in std devs (e.g., Z=1.65), `VaR for day t = R̄ − Z·s` (VaR is always expressed as a negative number) (Kaufman, Ch.23).

**No VaR treatment was found in Vince, Pardo, or Chan's extractions** — VaR as a named framework is a Kaufman-specific contribution among these five sources.

---

## 6. Risk-Adjusted Return Ratio Family

### 6.1 Kaufman's full ratio catalog (Ch.23)

- **Sharpe Ratio**: `SR = (AROR − RF) / ASTD`, where AROR = annualized rate of return, RF = risk-free rate (usually 3-month), ASTD = annualized standard deviation of returns. RF is often omitted for simplicity (yielding the Information Ratio below) unless interest income on idle capital has been included in returns; for system-comparison purposes, since RF subtracts equally from all systems, omitting it doesn't change relative rankings (Kaufman, Ch.23).
- **Information Ratio**: `IR = AROR / ASTD` (Sharpe without the risk-free adjustment). **Stated limitation, explicit**: satisfies "higher profit is better, all else equal" but cannot distinguish (1) consecutive small losses vs. alternating small losses (the alternating pattern is preferable but the ratio can't tell), or (2) large profit surges vs. evenly-distributed losses — the ratio is blind to *sequencing* (Kaufman, Ch.23).
- **Geometric Ratio (GR)**: uses the geometric ratio of daily returns rather than arithmetic AROR, "since ratios are similar to percentages" (cited to Siligardos 2016). Exact notation not recoverable from extraction.
- **Treynor Ratio**: `TR = (AROR − RF) / β`, where β = portfolio beta (weighted sum of individual stock betas) — isolates excess return relative to systematic/benchmark risk rather than total volatility (Kaufman, Ch.23).
- **Palagi Ratio** (cited to Alessandro Palagi): `PR = Sharpe Ratio / (Max % Drawdown × Deviation from a straight line [linear regression residuals])`, both computed over the same interval as Sharpe. **Purpose**: favors returns with smaller drawdowns and smaller deviation from the annualized trend line — an overall smoother profile (Kaufman, Ch.23).
- **Average Maximum Retracement (AMR)** — Schwager's measure: average of (maximum closed-out equity prior to day i minus total equity on day i), over all days i, excluding new-equity-high days. Schwager's practical shortcut: use only the low-equity day of each month for a rough approximation. **Rationale, explicit**: conceptually similar to semi-variance; standard deviation "does not express [risk] correctly" and biases results in favor of profitable days if those are less volatile — "gives you an understated picture of risk" (Kaufman, Ch.23).
- **Calmar Ratio**: `CR = AROR / Max Drawdown(t)`, where max drawdown as of day t is the largest historic peak-to-valley drawdown from the start of data through today. **Explicit caveat, cross-referencing overfitting**: parameters chosen from an apparently robust test surface may look good only because their timing happened to avoid a bad price shock, understating true maximum drawdown — and "the future always brings larger profits and especially larger drawdowns" (Kaufman, Ch.23).
- **Sortino Ratio**: `Sortino = (Return − MAR) / DownsideDeviation`, where MAR = minimum acceptable return (may be the risk-free rate or any investor-set threshold), and the denominator is the standard deviation of only the negative equity excursions (peak equity − current equity, where nonzero) over the period (Kaufman, Ch.23).
- **Ulcer Index (UI)** — Peter Martin, 1987: `UI = sqrt[ Σ(Dᵢ²) / n ]`, where Dᵢ = (peak equity as of day i) − (actual equity on day i), using only days where D≠0, and n = number of such days. **Interpretation, explicit**: a semi-variance-type measure; as UI increases, investors are presumed more anxious about performance (Kaufman, Ch.23).
- **Time to Recovery**: given two systems with equal max drawdown, prefer the one that recovers sooner. Recovery speed doesn't change max drawdown but does change measured annualized volatility (Kaufman, Ch.23).
- **Potential Risk — Probability of Drawdown (DP) and Semivariance (SV)**: DP = std dev of daily drawdowns dᵢ (measured from the most-recent equity high to today's equity, dᵢ=0 on new-high days), computed only over days with a drawdown. SV = fit a linear regression to the equity/NAV stream, then take the std dev of only the *negative* residuals below the fitted line. **Stated relationship**: SV < DP typically, because fitted-line values sit below the peak-equity values used in DP. Both represent 1 standard deviation, giving a 16% chance of exceeding that value over the next n days, and 2.5% chance of exceeding 2× that value.
- **Drawdown Ratio (DR)**: `DR = Return / (DP or SV)`. **Explicit claim**: DR satisfies all 3 criteria the Sharpe ratio failed at — favors higher profit, reflects the order of profits/losses (drawdown size depends on sequencing), and doesn't penalize large gains (only drawdowns count as risk).
- **4 stated conditions under which these ratios understate true risk, explicit**: (1) small test samples; (2) few historic equity drops (also a poor-sample symptom); (3) concentration in fewer product groups (poor diversification); (4) compounding positions (Kaufman, Ch.23).
- **Decaying Performance diagnostic**: fitting a slope through cumulative (not average) annualized returns can reveal a "slight tendency for returns to decline" even when the simple arithmetic average of the same years looks fine — worked illustration: 5 years averaging 19.2% arithmetically show a cumulative-slope-derived rate of only 17.9% (Kaufman, Ch.23).

### 6.2 Pardo's ratio contributions (Ch.12)

Pardo's ratio family is built specifically on the required-capital denominator rather than on standard deviation:
- **Risk-Adjusted Return (RAR)** = Annualized Profit / (Margin + Risk) — see §4.
- **Reward-to-Risk Ratio (RRR)** = Net Profit / Maximum Drawdown — rule of thumb ≥3 — see §4.
- **Model Efficiency (ME)** = Net Profit / Perfect Profit — rule of thumb ≥5% — see §4.

Pardo does not present Sharpe/Sortino/Calmar-style ratios in the extracted chapters; his ratio family is drawdown-and-perfect-profit centric rather than standard-deviation centric, a structurally different (though philosophically related) approach to the same "reward per unit of risk" question that Kaufman's ratio family addresses.

### 6.3 Vince's contribution — the geometric mean as an implicit risk-adjusted measure, and the Sharpe/Tangent Portfolio

Vince positions the **geometric mean** itself as a dispersion-adjusted performance measure "alongside other dispersion-adjusted performance measures (Sharpe ratio, Treynor measure, Jensen measure, Vami)," but notes it is unique among them in measuring performance "in the same mathematical form (multiplicative) as how account equity is actually affected" (Vince, Ch.1). Vince's own Sharpe-ratio formulation, in the Capital Market Line context: `Tangent Portfolio = MAX{ (AHPR−(1+RFR))/SD }` (Vince, Ch.7, Eq 7.01a) — the tangent (highest-Sharpe) portfolio is explicitly noted to generally be a *different* portfolio from the geometric-optimal one, coinciding only when `RFR = GHPROPT − 1` (Vince, Ch.7). This is consistent with Kaufman's later, independently-stated efficient-frontier framing (§6.4).

### 6.4 Kaufman's utility/efficient-frontier framing (cross-referenced to §8)

Kaufman frames every strategy/portfolio by AROR and ASTD (annualized standard deviation of returns): "a rational investor will always choose the one that is higher and to the left" on a risk/return plot; the efficient frontier is the curve of investments offering max return per given risk. **Optimal point definition**: where AROR/ASTD is maximized — geometrically, where a line from the risk-free rate R on the vertical axis is tangent to the frontier. **Explicit caveat**: not all investors choose this tangent point — personal risk tolerance and absolute return/risk levels matter (full portfolio-selection treatment deferred by Kaufman to his Ch.24, i.e., `12_portfolio_construction.md`'s domain) (Kaufman, Ch.23).

---

## 7. Event / Price-Shock Risk

**Kaufman's core position, stated as an axiom**: systematic risks can be controlled/reduced, but market risk from a genuine price shock "can never be eliminated." Kaufman quotes Andrew Lo (*Adaptive Markets*): "Risk is measurable but uncertainty is not," and "Opportunity lies in uncertainty because everyone that understands risk can squeeze out every bit of marginal return" (Kaufman, Ch.23). **Restated even more bluntly elsewhere**: "risk cannot be eliminated — you can move the losses around, make them bigger or smaller, but you cannot eliminate them, and they will always add up to (almost) the same amount" (Kaufman, Ch.23). Kaufman's explicit "risk is immutable" axiom (Ch.22): risk can be reshaped (frequent-small vs. rare-large losses) or relocated in time, never eliminated; a system showing no losses, or claimed "risk-free" arbitrage, should be treated as a red flag rather than a genuine finding.

**Two practical rules to reduce price-shock exposure, explicit and numbered (Kaufman, Ch.23)**:
1. Choose a strategy that is not always in the market (via profit-taking or multiple trends). **Stated arithmetic**: a method in the market 40% of the time has a 60% chance of avoiding a given price shock; a method always in the market is exposed to all of them.
2. Earn as much as possible while investing as little as possible — seek high per-trade returns even at low market-time exposure, since less invested = less at risk. Kaufman frames "a reduction in returns for a larger reduction in exposure" as "a good trade-off."

**Explicit LTCM callback** (Kaufman, Ch.23, cross-referencing Ch.22): LTCM "believed they could engineer the risk out of each trade by explaining away and removing all of the previous large price shocks. They failed to survive the next price shock."

**Correlation collapse during shocks**: correlation statistics are explicitly flagged as unreliable exactly when needed most — they go to extremes (toward ±1) during price shocks, which historic averages/rolling windows systematically understate (Kaufman, Ch.24). "No amount of correlation analysis or diversification will protect an investment from a price shock" (Kaufman, Ch.22, "It's Not the Markets, It's the Money" — cross-referencing the negative-interest-rate 2011-2012 episode as an example no correlation model could have anticipated).

**Kaufman's Ch.21 price-shock correction rule for backtests**: assume roughly one >5-ATR shock every two years (10 shocks over a 20-year test); if a backtest shows more than 50% of embedded shocks were favorable, manually reverse enough of them to bring the favorable share to ≤30% (treating shocks as inherently close to a coin flip) — explicitly stated to mainly correct the *risk* estimate, not the return estimate (Kaufman, Ch.21).

**Kaufman's Ch.22 reserve-capital and crisis-response framework**:
- **Reserve-capital requirement, with concrete historical loss figures**: most leveraged futures traders would not have survived a $7,500 single-event loss (crude oil, Gulf War) or a $4,337 loss (euro, Gorbachev shock) — explicit recommendation to hold sufficient reserves to withstand *most* price shocks, since holding through a shock showed a 71% historical chance of substantial-to-full recovery within 2-8 days in the book's own 7-event sample, "if you weren't wiped out by the price shock" first (Kaufman, Ch.22).
- **Windfall-profit/large-loss asymmetric crisis rule**: (1) exit immediately on a windfall profit from a price shock; (2) hold (do not panic-exit) a large loss from a price shock, expecting a same-direction reversal within days, accepting the risk may increase in the interim; (3) only add to a position on a post-spike volume surge after volatility has begun to decline, and only with adequate reserves — explicitly framed as a temporary, still-systematic regime change, not ad hoc discretion (Kaufman, Ch.22).
- **System disconnect risk**: after a price shock, a lagging trend indicator can remain positioned in the pre-shock direction long after price has substantially reversed (the 1987 crash case: 22-30% of the recovery had already occurred by the time 50/100/200-day MAs individually turned) — mechanical adherence to a lagging trendline during exactly this post-shock window is itself a source of risk distinct from the shock's initial impact (Kaufman, Ch.22).
- **Data-integrity as a price-shock-adjacent risk**: outliers (>4% jump from prior data), missing dates, and open/close prices outside the high-low range are named as basic daily-data risk checks — undetected bad data can silently corrupt both backtest results and live signals in ways that masquerade as shock events (Kaufman, Ch.22).

**Kaufman's Ch.20 high-volatility exit/re-entry threshold**: annualized volatility above ~45% on an individual market is associated with declining returns and rising risk; the recommended response is to exit and wait for volatility to fall to ~35% before re-entering, framed as a risk-management overlay independent of the underlying trading signal (Kaufman, Ch.20).

**Pardo's convergent treatment**: price shocks are defined as "an unusually large price change," typically from major unexpected events (war, corporate collapse, major discovery, terrorist attack, assassination) — by nature rare/unpredictable statistical outliers that can produce windfall profit or extreme loss. A strategy needs risk-management/design that can survive an unexpected shock even though it cannot be predicted (Pardo, Ch.12). Pardo's named example: the ~20-point overnight S&P 500 drop around October 19, 1987 cost overnight longs ~$10,000/contract on the open — cited as a genuine "black swan" statistical outlier that "must be factored into the risk profile" (Pardo, Ch.12). General guidance: evaluate simulation performance both with and without rare, event-driven trades, to separate genuine repeatable edge from one-off windfalls/disasters (Pardo, Ch.6, consolidated in Pardo's Risk_Management.md).

**Chan's contribution — fat tails and the fat-tail-adjusted leverage cap**: Chan cites Nassim Taleb's "black swan" terminology for highly improbable, high-impact events, and gives an explicit remedy distinct from Kaufman's or Pardo's: use a simple backtest to estimate the historical *maximum one-period loss* (period = whatever rebalancing interval you commit to), determine your own maximum tolerable one-period equity drawdown, and take **the smaller of (a) half-Kelly leverage and (b) (max tolerable drawdown / historical worst one-period loss)** (Chan, Ch.6). Worked example: S&P 500 historical worst one-day loss ≈ 20.47% (Black Monday, Oct 19 1987); if max tolerable one-day drawdown = 20%, implied max leverage ≈ 1 — and since half-Kelly leverage in Chan's own SPY worked example was 1.264, **even half-Kelly would not have been conservative enough to survive Black Monday**, demonstrating that half-Kelly is not automatically "safe enough" against fat-tail/shock risk (Chan, Ch.6). Chan's explicit epistemic humility, quoting Wittgenstein: "the truly scary scenario in risk management is the one that has not occurred in history before" — for genuinely unprecedented events, "theoretical models are appropriately silent" (Chan, Ch.6).

---

## 8. Utility / Risk-Preference Theory

Source: Kaufman, Ch.23. **Bernoulli's utility theory** (Daniel Bernoulli, 1738, cited via Peter Bernstein's *The Portable MBA in Investment*): distinguishes price (same for everyone) from value/utility (personal). **Diminishing marginal utility**: as wealth grows, the preference for more wealth diminishes. Bernoulli's utility-vs-wealth curve is described as beginning at zero, moving up-and-right as "a perfect quarter-circle," ending horizontally where risk is no longer attractive — implying all people become risk-averse past some point.

**Observed behavioral patterns, stated as fact by Kaufman**: most people reject an even-money bet of equal gain/loss but will accept a small chance of a large win (state lotteries); young people with little savings take more risk because "a small amount of savings is not significant for their future" (Kaufman, Ch.23). Two other unattributed theories are mentioned without endorsement or rejection: "the market maximizes the amount of money lost" and "the market maximizes the number of losing participants" — Kaufman states both "appear to be true," without further defense (Kaufman, Ch.23).

**Risk Preference formula** (reconstructed from the source's own worked example, since the chapter's own inline formula did not extract cleanly): `P = Σ Wi·Ui`, where ΣWi = 1, Wi = weighting/probability of outcome i, Ui = utility of outcome i. Weighting factors may be personal-bias-based or calculated probabilities. **Worked example**: a gold trade with likely profit $4,000 and risk $1,500; at 60% probability of success, utility scales roughly linearly with probability (e.g., 0.6×4 − 0.4×1.5 = 1.8, in thousands). **Key behavioral finding, explicit**: investors do NOT feel proportionally about different reward sizes — a 60%-chance-of-$4,000 vs. 40%-chance-of-$1,500-loss trade might be rated 65 on a 0-100 preference scale by an investor; doubling the reward to $8,000 (same risk, same probabilities) might raise their preference rating only to 80, "although the utility would be 4.2, more than twice as large" — stated utility and subjective preference **diverge** (Kaufman, Ch.23).

**Figure 23.2 — 5 risk-preference curve archetypes, explicit**: (1) extreme risk-averse — less likely to take a trade as risk rises; (3) equal chance of taking the trade regardless of risk level; (5) risk-seeking — more likely to take a trade with higher risk (Kaufman, Ch.23).

**Common Sense Management of Risk, Kaufman's own 8-point checklist (explicit, numbered)**, presented as a practical distillation of the utility/risk-preference discussion:
1. Risk only a small amount of total capital per trade — "No trade should ever risk more than 5% of the invested capital."
2. Know exit conditions in advance for every trade, even if exact loss size isn't knowable ahead of time.
3. Large profits imply large risk — if average profit/loss is too large relative to investment, reduce position size.
4. Exit a trade quickly once you recognize something is wrong — don't try to manage the loss ("many floor traders believe that the smartest trader is the first one out").
5. Don't meet margin calls — a margin call is "an objective statement of a trade that's gone wrong, or a system that is not meeting expectations," a signal to review, not add capital.
6. When lightening up, liquidate the worst position first — profitable trades have proven themselves; losers haven't.
7. Be consistent with trading philosophy — a trend follower must keep losses small and let profits run; "You cannot be a trend follower by taking the first profit that you see."
8. Plan for contingencies (e.g., a price shock) — "Nothing ever goes as planned... Do not be undercapitalized" (Kaufman, Ch.23).

**No formal utility-function treatment was found in Vince, Pardo, or Chan's extractions.** Chan's closest analog is behavioral/psychological rather than formal-utility-theoretic: his treatment of loss aversion, the endowment effect, representativeness bias, despair, and greed (Chan, Ch.6) describes *why* traders systematically deviate from a rational risk-preference curve, but does not construct a formal utility function. Chan's "golden rule" — "keep portfolio size under control at all times" — and his explicit warning that both despair (adding capital to recoup losses) and greed (adding capital too fast after success) lead to overleveraging via different mechanisms, are the closest functional analog to Kaufman's risk-preference archetypes, presented as a psychological rather than mathematical framework.

---

## 9. Live-Performance Monitoring and When to Stop Trading a System

### 9.1 Pardo's framework — the Strategy Stop-Loss (SSL) and the evaluation-vs-trade-profile comparison

**Three ways real-time performance should be monitored, explicit (Pardo, Ch.14)**: (1) return on investment; (2) maximum risk; (3) real-time performance compared to test/evaluation performance.

**Three named reasons real-time ROI can decline, explicit**:
1. **Poor strategy** — the evaluation process itself missed a flaw (stated as unlikely if evaluation was done properly, but possible; treated as a last-resort explanation).
2. **Market contraction** — favorable conditions give way to unfavorable ones (a common, expected, non-alarming occurrence, provided it stays within the range of historically-observed behavior for that instrument).
3. **Unseen market conditions** — even a rigorously tested strategy can encounter genuinely novel conditions (data limitations, biased historical sample, or a true structural shift). Pardo's real historical illustration: the T-bill futures market's 1980 rally followed by the market going essentially "untradable" (flatlined) after hitting its high — "no matter what the style of trading strategy" (Pardo, Ch.14).

**The Strategy Stop-Loss (SSL)** — a predetermined loss threshold at which trading of the strategy is abandoned:
- Three inputs: (1) minimum capital needed to keep financing margin at the current commitment level; (2) a chosen max % of trading capital the trader is willing to lose before stopping; (3) MDD (or a multiple thereof).
- **Basic formula + example**: `SSL = MDD × Drawdown Safety Factor`. MDD $5,000, DSF 2 → SSL = $10,000.
- **Combined with required capital**: `Required Capital = Margin + (MDD × Safety Factor)`. Margin $5,000, MDD $6,000, factor 3 → RC = $23,000.
- **SSL as a % of required capital**: if SSL should represent a chosen max capital-loss % (e.g., 40%), then `Required Capital = SSL / Capital Loss %` = $18,000/40% = $45,000 — the SSL dollar amount and the capital-loss-percentage threshold become "one and the same" when solved this way (Pardo, Ch.14).
- **Two usage philosophies, both presented as legitimate**: (a) a hard, mechanical stop — trading ceases the instant losses reach/exceed the SSL, no exceptions; (b) a heightened-vigilance trigger — as drawdown approaches the SSL, the trader qualitatively assesses whether the equity curve looks like it's "in free fall" (stop early, even before hitting the literal SSL) vs. "finding support" (allow some additional latitude even slightly past the nominal SSL). Pardo notes some traders use it as strictly as a per-trade stop order (Pardo, Ch.14).

**The evaluation-profile vs. trade-profile comparison — the core live-monitoring mechanism**: "A trading strategy is said to be functioning properly or normally if its real-time trading performance is in line with or equivalent to its evaluation performance." A strategy performing *worse or better* than its evaluation profile both require explanation — not just losses (Pardo, Ch.14). A **25-item list of statistical measures** should be tracked and compared for both profiles: annualized profit; trades/year; % winning trades; largest/average win (and duration); largest/average loss (and duration); average/largest winning and losing runs (and durations); maximum equity drawdown (dollar size, duration, start/end dates); maximum equity run-up (same); standard deviations of each average (Pardo, Ch.14).

**Worked comparison example, explicit**: Evaluation profile shows MDD $4,000 over 3 trades (StDev $2,000/2 trades) under average-volatility conditions.
- (a) Real-time produces 9 consecutive losses totaling $10,000 under *similar* volatility → exceeds both the dollar ($4,000+$2,000=$6,000) and trade-count (3+2=5) expected bounds by a wide margin → judged a likely genuine strategy failure warranting suspension absent a very good explanation.
- (b) Real-time instead produces 3 losses totaling $8,000 (same trade-count as expected) but under volatility roughly *double* the evaluation baseline → judged "unpleasant, but not an entirely unexpected performance," because wins should also be proportionally larger under doubled volatility — loss size alone, without controlling for volatility regime, can be a misleading comparison (Pardo, Ch.14).

**The final, explicit statistical-comparison guideline**: **"If statistics in the trade profile are less than 50 percent or more than 150 percent of the corresponding evaluation profile statistic, whether profitable or not, then a rational explanation must be found."** Equity drawdowns specifically must be constantly monitored against both the SSL and the evaluation profile (Pardo, Ch.14).

**Common trader errors and performance quirks (explicit)**: a big early win risks emotionally destabilizing overconfidence/greed and may cause a trader to disregard subsequent normal losses or over-leverage without proper justification; unusually large wins are often volatility-driven, and "the sword of volatility cuts both ways" — an outsized win can be a leading indicator of an outsized loss to come. A big early loss fans fear and risks premature abandonment right before a "typical big win" the profile would have predicted. A flat/boring period can bore a trader into premature abandonment or unauthorized size increases (Pardo, Ch.14). The remedy in every case is the same: check whether the observed behavior is normal per the evaluation profile before reacting.

**Two-level remedy for building the evaluation profile, explicit (Pardo, Ch.14)**: (1) **macroscopic** — study of the full statistical evaluation profile, illustrated with a worked example (Table 14.1, strategy "XT99AP2dumo" on S&P, 1990–2005): net P&L $1,643,688, annualized $102,731, 119 trades, with win/loss/run/equity-swing statistics broken down by mean, StDev, +1SD, and −1SD; (2) **microscopic** — bar-by-bar, trade-by-trade review of the actual chart and tabular trade list, illustrated with a trade-efficiency table format showing entry/exit efficiency percentages (Table 14.2). Pardo's own framing: "a full operating knowledge of the performance of the trading strategy can only come through the acquisition of information from the microscopic, signal-by-signal and day-by-day behavior" — the macroscopic statistical profile alone is not sufficient.

**Pardo's closing governing rule**: **"trade the strategy as long as it performs in real time according to the expectations produced by its evaluation profile, thereby producing a steadily growing equity, which remains above the strategy stop-loss"** (Pardo, Ch.14).

### 9.2 Kaufman's framework — chi-square monitoring

**Chi-Square (χ²) Significance Test** (standard Pearson's chi-square form): `χ² = Σ [(O−E)² / E]`, summed across categories, where O = observed result, E = expected/theoretical result (Kaufman, Ch.23).

**Worked example**: actual reliability 20% (1-in-5 win rate) vs. expected 35% reliability → the computed χ² falls in the "0.1% to 1.0%" significance band per the source's own chi-square reference table (1 degree of freedom for this 2-category test) — interpreted as: only about a 1% chance the true system reliability is 35% given the observed 20%, i.e., "there is a problem with the system, most likely overfitting" (Kaufman, Ch.23). **3-tier significance classification, explicit**: "highly significant" > "significant" > "probably significant" (the exact numeric cutoffs for each tier did not extract cleanly from the source table — flagged as a gap; the qualitative ordering is preserved).

**Applied to price-run analysis (Table 23.19, cross-referencing the Theory of Runs)**: expected-vs-actual run-length counts compared via χ² — aggregate result ≈55% probability of occurring by chance ("not significant," i.e., the overall pattern matched random-walk expectation in this test). Individual run-length pairs showed more deviation but still not statistically significant on their own — an explicit caution that the aggregate test used is a "conservative/blunt instrument" (Kaufman, Ch.23).

**Yates Correction** (cited to Frank Yates): for small samples (under 5 data points), subtract 0.5 from each |O−E| difference before squaring in the chi-square calculation, to correct chi-square's tendency to overestimate significance at small sample sizes. **Explicit caveat**: "using a small number of data points is unreliable at best" regardless of the correction (Kaufman, Ch.23).

**"Is the Model Broken?" diagnostic framework, explicit**: causes of model decay include an exploited economic pattern occurring less often or becoming overpublicized, or an arbitrage strategy degrading as its components become too highly correlated. **Recommended diagnostic**: compare live drawdown size/duration against the tested historical profile, accounting for the expectation that more data naturally brings both larger profits AND larger losses over time; a chi-square test can also be applied. **Red flag, explicit**: if a newly-live system posts steady losses until it reaches the previous backtested maximum drawdown right out of the gate, "chances are that something is wrong" — **"systems should not systematically decay from the first day of trading"** (Kaufman, Ch.23). This finding directly parallels Pardo's SSL/evaluation-profile framework in §9.1, arrived at via a different (statistical-test-based) methodology.

**Binomial Probability of a Run of Losses** (standard Bernoulli/Pascal-triangle form), given by Kaufman as a companion diagnostic for judging whether an observed losing streak is statistically unremarkable: `B(l,n,p) = [n!/(l!×(n−l)!)] × p^l × (1−p)^(n−l)`. Worked table (5/10/15-trade horizons) gives mean and std dev of expected loss counts, e.g., a 15-trade sequence shows an 8% chance of ≥13 losses, used as an operational "something may be wrong" threshold (>12 losses in 15 trades) (Kaufman, Ch.23). **Distribution-shape caveat, explicit**: the symmetric binomial distribution is noted as *less* appropriate for real trading performance than a Poisson or other skewed distribution, since price returns are known to be skewed with a fat tail — flagged as a known simplification, not a claim that trading losses are truly binomially distributed.

### 9.3 Chan's framework — the regime-failure question

Chan's treatment of "when to stop" is explicitly framed around distinguishing genuine model/regime failure from ordinary statistical variance — a question he states plainly **"can only [be] believe[d]," not proven** (Chan, Ch.6, per the extraction's own flagged ambiguity).

**Model risk as the most likely non-position risk category, explicit ranking (Chan, Ch.6)**: (1) model risk — losses stemming from the model itself being wrong (data-snooping/survivorship bias, increased competition from other institutions running the same strategy, or a genuine regime shift eliminating the edge); (2) software risk — the automated trading system not faithfully reflecting the backtested model, due to bugs; (3) physical/natural disaster risk (infrastructure failures).

**Mitigation for the bias/error sub-case of model risk**: have a collaborator/consultant independently duplicate the backtest results — "routinely done in scientific research and no less essential in financial research" (Chan, Ch.6).

**Mitigation for the competition/regime-shift sub-case — no direct fix, only gradual de-risking**: Chan states explicitly there is no direct fix available for competition-driven or regime-shift-driven edge decay except gradually lowering leverage as losses accumulate. His stated preference: this should be accomplished *automatically and systematically* by continuously updating Kelly leverage from the trailing mean return/std dev — as the trailing mean decreases toward zero, Kelly leverage is automatically driven toward zero. Chan explicitly prefers this gradual, formula-driven approach over abruptly shutting down a model after a large drawdown, because of the psychological-pressure risks (despair-driven premature shutdown, or greed-driven doubling-down) discussed in his behavioral-finance section (Chan, Ch.6).

**Representativeness bias as an explicit warning against over-reacting to a single loss**: after a big loss, traders (even quant traders) tend to immediately modify strategy parameters to retroactively "avoid" that specific loss. Chan calls this "unwise," because such modification may (a) invite some other, not-yet-seen big loss, or (b) eliminate profit opportunities that previously existed — "we are operating in a probabilistic regime: No system can avoid all the market vagaries that can result in losses." **If a genuine deficiency is suspected**, Chan's explicit remedy is to always backtest the modified version over a *sufficiently long* period, not just the recent weeks that prompted the change (Chan, Ch.6).

**Despair and greed as the two irrational failure modes at drawdown decision points, explicit**: **Despair** (during major, prolonged drawdowns) produces two irrational responses — (a) pressure for complete, immediate model shutdown, or (b) overconfident, reckless doubling of bets on losing models hoping to recoup losses. **Neither is rational**; a Kelly-disciplined trader instead *gradually lowers* capital allocation to the losing model. **Greed** (during a good run) produces the temptation to rapidly increase leverage; a disciplined trader keeps leverage bounded by the Kelly formula and fat-tail-event caution, not by exuberance. Chan's stated "one golden rule" of risk management: **keep portfolio size under control at all times** — "easier said than done" (Chan, Ch.6).

**Historical failure examples Chan cites as consequences of failing to apply this discipline**: Long-Term Capital Management (2000) and Amaranth Advisors (2006) — in the latter case, a single trader (Brian Hunter) built such a large leveraged position in one strategy (natural gas calendar spreads) that a $6 billion loss wiped out the fund's equity, "a textbook case of risk mismanagement" (Chan, Ch.6). Chan also discloses two of his own overleveraging mistakes as cautionary lessons — adding over $100 million to a six-month-old institutional strategy "in a fit of greed" (losing investors over $1 million, before he learned the Kelly criterion), and stubbornly increasing a mean-reverting spread position to nearly $500,000 as an independent trader when the spread failed to revert as expected, exiting near a six-figure loss shortly before the spread reverted (Chan, Ch.6).

### 9.4 Synthesis across the three frameworks

All three approaches to "when to stop" are presented in full, without adjudication, since they operate at different levels and via different mechanisms:
- **Pardo** gives a hard, pre-committed dollar/percentage threshold (SSL) plus a systematic statistical comparison of live vs. backtested performance profiles (the 50%-150% band rule) — a rules-based, threshold-triggered framework.
- **Kaufman** gives a formal statistical hypothesis test (chi-square on reliability/run-length) to determine whether an observed live-performance deviation is likely to be genuine model failure (as opposed to noise), plus the "no day-one systematic decay" red flag.
- **Chan** frames the decision as inherently unprovable in real time ("can only be believed"), and instead advocates a continuous, automatic, formula-driven de-risking mechanism (trailing-mean-updated Kelly leverage) specifically designed to avoid the abrupt, psychologically-fraught binary "keep trading / stop trading" decision that both despair and greed corrupt.

No single source in this extraction set offers a definitive, universally-agreed answer to "when exactly to stop trading a system" — all three converge on the same underlying principle (compare live behavior against a pre-specified expectation, and act *before* a threshold/red-flag is breached rather than reactively), but differ sharply on mechanism: discrete threshold (Pardo), statistical significance test (Kaufman), or continuous automatic de-risking (Chan).

---

## 10. Broker Execution Architecture and Account Mechanics (Hilpisch Ch.8-9)

This is a Hilpisch-unique contribution among the five source books: concrete, code-level broker-integration mechanics (as opposed to narrative risk framing) that determine how a backtested strategy's risk actually manifests once it places real orders. Absent from Vince, Kaufman, Pardo, and Chan's extractions.

### 10.1 Broker/platform selection — the 5-criteria framework (reused identically for Oanda Ch.8 and FXCM Ch.9)
1. **Instruments** — stocks, ETFs, bonds, currencies, commodities, options, futures, etc.
2. **Strategies** — long-only vs. long-short capability; single- vs. multi-instrument support.
3. **Costs** — fixed and variable transaction costs, which "might even decide whether a certain strategy is profitable or not" (explicit cross-reference to the cost-sensitivity findings in `18_common_failure_modes.md` §5).
4. **Technology** — desktop/tablet/mobile trading tools plus programmatic APIs.
5. **Jurisdiction** — regulatory/legal frameworks vary by country/region and may restrict available platforms/instruments.

Oanda profile against these 5 criteria: CFDs (leveraged, e.g. 10:1/50:1, margin-traded, losses can exceed initial capital); both long and short with market/limit orders plus optional profit targets and (trailing) stop losses; no fixed transaction costs, variable cost via bid-ask spread only; RESTful + streaming v20 API with the official `tpqoa` Python wrapper and free practice/demo accounts easing paper→live transition; FX CFDs broadly available, index CFDs may be jurisdiction-restricted.

### 10.2 Net vs. hedge accounts — a materially important, non-obvious cross-broker portability risk

**Oanda defaults to net accounts; FXCM demo defaults to hedge accounts.** This is a behavioral difference in how the broker nets offsetting positions in the *same* instrument, and it directly affects whether strategy code that assumes one account type will behave correctly ported to a broker/account defaulting to the other — a portability risk that is not otherwise addressed anywhere in this book's own worked examples, but is significant enough that strategy code moved between brokers (or between demo and live accounts of different types) should not be assumed to produce identical position/P&L behavior without explicit verification of account type.

### 10.3 Leverage and margin mechanics — worked numeric example (Oanda Ch.8)
- Baseline (no leverage): buying 10,000 EUR_USD units at 1.10, rate rises to 1.105 → profit = 10,000 × 0.005 = **50** (+0.5%).
- **20:1 leverage** (5% margin): only 500 (10,000 × 5%) posted upfront; the same 50-unit profit now represents a **10% return on margin** — leverage amplifies relative returns by the leverage factor when a trade goes well.
- **Downside**: price drops to 1.08 → loss = 10,000 × (1.08−1.10) = **−200**; relative to the 500 margin, that's **−40%**. If equity falls below 200, the position must be force-closed since margin requirements can no longer be met.
- **Boxed warning (explicit, load-bearing)**: "With leveraged trading based on a 10:1 factor (10% margin), a 10% adverse move in the base instrument already wipes out the complete margin. In other words, a 10% move leads to a 100% loss." Cross-reference the CFD-margin debt-position finding in `14_backtesting_and_validation.md` §12.3 (short/long CFD positions can flip to a literal position of debt once leveraged transaction costs are included).

### 10.4 Streaming order-flow architecture — the callback pattern and position-flip sizing formula

**Callback-function pattern (FXCM, Ch.9)**: `api.subscribe_market_data(instrument, (output,))` — the broker's streaming machinery invokes a registered callback on every new tick, an event-driven (not polling) architecture.

**`MomentumTrader` class (Oanda, Ch.8) — the trading class *is* the API client**, an architecturally distinctive choice: it inherits directly from `tpqoa.tpqoa`, so a single object handles both data streaming and order placement. Its `on_success(self, time, bid, ask)` callback implements the online-algorithm pattern documented in `14_backtesting_and_validation.md` §12.5 (append tick → resample → drop incomplete last bar → compute signal), then applies:

**Position-flip order sizing formula**: `(1 - position) * units` — elegantly handles enter/hold/flip in one expression without separate branches: 1 unit sized if currently flat, 2 units if flipping from the opposite side (closing the existing position and opening the new one in a single order). Reused identically in the Ch.10 `MLTrader` live-deployment class.

**Manual final close-out required**: the class does not auto-close on stream termination — after streaming stops, the script must explicitly flatten any remaining position (`api.create_order(instrument, units=-mt.position * mt.units, ...)`).

### 10.5 Order-type support beyond market orders (unused in the book's own worked examples)

`create_order(instrument, units, price=None, sl_distance=None, tsl_distance=None, tp_price=None, comment=None, touch=False, ...)` supports stop-loss distance, trailing stop-loss distance, take-profit price, and market-if-touched orders — **but no worked example in the book actually uses any of these risk-limiting parameters**; every live/backtested example relies solely on the model's own signal reversal to exit a position (this gap is also logged in `14_backtesting_and_validation.md` §12.4's self-disclosed pipeline gaps).

### 10.6 CFD/leverage risk — cited real-world illustration

Contracts for Difference (CFDs) are derivative products whose payoff derives from another instrument's price but are themselves separate products issued/quoted/supported by the broker. **Cited risk example (not the author's own analysis)**: the 2015 Swiss Franc ("SNB") event caused multiple online forex broker insolvencies — used as a real-world illustration of CFD/leverage risk materializing at the broker-counterparty level, not just the position level.

---

## Summary Table — Where Each Book's Risk Framework Concentrates

| Topic | Vince | Kaufman | Pardo | Chan |
|---|---|---|---|---|
| Stop-loss philosophy | Not a primary tool; capped-loss framing only | Full technique taxonomy + strategy-type fit rule | Trade-risk tier, risk-stop definition | Explicit "stop-loss fallacy" critique |
| Risk of ruin | Philosophical/structural (no closed form) | Full closed-form equations (equal + unequal payout) | Not directly addressed | Ruin avoidance as the Kelly objective's implicit constraint |
| Drawdown math | Extensive (f-as-drawdown-proxy, duration, diversification myth) | Diagnostic/overfitting angle, 3x MDD capitalization rule | MDD deep-dive + Mandelbrot/fractal caveat | Not a separate treatment |
| Required capital | Not formulated as such | 3x MDD rule of thumb (convergent) | Full 1x/2x/3x MDD formula family | Not formulated as such |
| VaR | Absent | Full treatment (3 forms) | Absent | Absent |
| Risk-adjusted ratios | Geometric mean, Sharpe/CML | Full catalog (Sharpe, Sortino, Calmar, Ulcer, Treynor, Palagi, etc.) | RAR, RRR, Model Efficiency | Sharpe-driven growth-rate formula (g=r+S²/2) |
| Event/price-shock risk | Not directly addressed | Extensive (Ch.20-23), LTCM callback | Named, black-swan example | Fat-tail leverage cap (Black Monday example) |
| Utility/risk-preference theory | Absent (formal) | Full Bernoulli treatment + 8-point checklist | Absent (formal) | Behavioral/psychological analog only |
| Live monitoring / when to stop | Absent (this book ends at strategy design) | Chi-square significance testing | SSL + evaluation-vs-trade-profile comparison | Regime-failure "can only be believed" + automatic de-risking |
| Broker execution/account mechanics | Absent | Absent | Absent | Absent |

*Note: the table above retains its original four-book scope (Vince/Kaufman/Pardo/Chan); Hilpisch is documented separately in §10 rather than as a fifth table column, since his contribution (broker-API execution mechanics: 5-criteria selection framework, net/hedge account risk, leverage/margin worked example, position-flip sizing formula) does not map onto any of the table's existing rows for the other four books — it is a Hilpisch-exclusive category among the five sources, not a point of comparison.*

---

## Notes on Source Thinness and Chapter-Number Corrections

- The task brief's chapter-number guesses were confirmed largely correct: Kaufman Ch.23 ("Risk Control") is indeed the single chapter containing risk of ruin, VaR (all forms), the full risk-adjusted-ratio family, utility/risk-preference theory, and chi-square monitoring — no correction needed. Kaufman's own Ch.24 material explicitly (and, per its own extraction, mistakenly) cross-references "Chapter 21" for VaR/other-risk-measurement content in one place, when the material actually lives in Ch.23 — this internal citation inconsistency is Kaufman's own extraction's flagged error, preserved here rather than silently corrected.
- Event/price-shock risk in Kaufman is **not concentrated in Ch.21-22 alone** as the brief guessed — it is genuinely distributed across Ch.14 (behavioral framing), Ch.16 (day-trading-specific), Ch.20 (volatility threshold), Ch.21 (backtest-correction rule), Ch.22 ("Adding Reality" — reserve capital, crisis response, data integrity), and Ch.23 (the two numbered practical rules, LTCM callback). This file cites each specific chapter for each specific claim rather than treating Ch.21-22 as a single monolithic source.
- Pardo Ch.12 and Ch.14 matched the brief's chapter numbers exactly.
- **Thinnest area across all sources: Value at Risk.** Only Kaufman treats VaR at all; Vince, Pardo, and Chan's extractions contain no VaR content whatsoever. This is noted rather than papered over — do not infer that Vince/Pardo/Chan implicitly endorse or reject VaR; the topic is simply absent from their books.
- **Thinnest area within Kaufman: the exact combining formulas for several named techniques** (Generalized Multi-Asset VaR, Kritzman-Rich probability-of-loss VaR, Gehm's unequal-payout risk of ruin, Vince's spreadsheet risk-of-ruin transform, the chi-square 3-tier significance cutoffs) did not survive the source's own extraction process due to embedded-graphic/notation-rendering gaps. These are flagged inline above exactly as the source knowledge base flags them — variable definitions and worked numeric results are preserved as the authoritative record where the exact formula could not be recovered, per the extraction's own "don't fabricate" discipline.
- **Utility theory** is a Kaufman-exclusive formal treatment among these four books; Chan's behavioral-finance material (loss aversion, despair/greed) is a substantively different, non-formal lens on the same underlying risk-preference question and is presented here as a distinct, non-overlapping contribution rather than forced into the same framework.
