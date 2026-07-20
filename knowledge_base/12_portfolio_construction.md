# 12. Portfolio Construction

Diversification, allocation, and portfolio-level construction, as documented across Kaufman's *Trading Systems and Methods* (Ch.23-24), Vince's *The Mathematics of Money Management* (Ch.5-8), and Chan's *Quantitative Trading* (Ch.6-7). See `10_position_sizing.md` for single-instrument Optimal f/Kelly/vol-targeting and `11_risk_management.md` for risk-of-ruin/drawdown/VaR math — this file is scoped to the multi-asset/multi-strategy allocation layer sitting on top of those single-instrument techniques.

---

## 1. Kaufman Ch.24 — Diversification and Portfolio Allocation (in full)

### 1.1 Framing and core claims

Kaufman's final chapter treats risk from any single stock/ETF/future as substantially reducible via diversification and proper leverage. The explicit object of diversification is "to have the offsetting price movement reduce overall risk more than it reduces returns" (Kaufman Ch.24). A stated fact: trading more than one asset with similar volatility "will always reduce total risk" (Kaufman Ch.24). For most investors, the best portfolio yields the highest return-to-risk ratio in real trading. The chapter progresses from market selection, to Excel Solver mean-variance allocation, to Kaufman's own genetic-algorithm portfolio solution (GASP), which the author presents as superior for handling active-trading idiosyncrasies (non-continuous returns, disjoint holding periods) (Kaufman Ch.24).

### 1.2 Systematic risk vs. market risk

**Systematic risk** can be reduced by diversification; **market risk** (price shocks, catastrophic risk) cannot be eliminated — "not predictable, and can surprise even the most sophisticated investors" (Kaufman Ch.24). The 2008 subprime crisis "proved that diversification can disappear under stress." Even with a purely random up/down scenario, two independent markets move the same direction 50% of the time (Kaufman Ch.24).

### 1.3 Three steps to achieving diversification

1. **Selecting individual assets from unrelated groups** — trade markets with low covariance/correlation. Market groups by liquidity: fixed income, currencies, equities/equity index, energy, industrial/precious metals, grains, livestock, foods, miscellaneous. Diversification benefit among equity sub-groups is limited because most react to the same broad economic conditions. **Financials** (fixed income + currencies + index markets) have strong fundamental interrelationships despite short-term independence — worked causal chain: better-than-expected U.S. GDP → Treasury prices drop first (yields rise) → USD strengthens → stock market rises (unless rate-sensitive, then falls). 9/11 example: investors fled stocks into fixed income and away from USD. Outside financials, a weaker dollar raises oil/gold/grain prices. Key qualifier: outside news-driven periods, there is considerable independent daily movement among commodities/stocks — **"Money moves the market, not fundamentals, and money seeks safety when there is a price shock. There is no diversification during a crisis"** (Kaufman Ch.24).
2. **Multiple strategies** — under stress, markets correlate more, so varied *strategies* diversify better than varied markets alone. Warning: superficially different techniques (moving average, ARIMA, point-and-figure) can all be trend-following and thus highly correlated — "If all trend-following systems are profitable, then they must extract those profits from the same price moves and hold the same position at some time" (Kaufman Ch.24). Six named less-correlated strategy families: (a) trend-following (MAs, P&F, breakout); (b) countertrend/mean-reverting (stochastic, contrary opinion, Hilbert); (c) spreading (pairs, sector-neutral, interdelivery, intercommodity, arbitrage, product); (d) fundamental (value, supply/demand, P/E); (e) carry/convenience-yield/implied-yield; (f) patterns (divergence, charting). These can hold conflicting positions in the same market simultaneously, reducing overall portfolio risk.
3. **Balanced risk** — equalizing risk across assets/strategies is necessary for diversification to work. Naive equal-dollar allocation is warned against: two stocks at the same price can have very different volatilities (Bank of America dropped from $30-50 to $5 post-crisis, showing *more* volatility at the lower price; "companies in the news tend to be more volatile than those under the radar"). Three most popular equal-risk methods (cross-ref `10_position_sizing.md`): (a) equal dollar amounts; (b) equal risk via annualized standard deviation; (c) equal risk via ATR (best for futures when H/L/C available; dividing equal-dollar investment by closing price is easiest for stocks) (Kaufman Ch.24).

### 1.4 The downside of equal weighting

If assets are equally weighted, diversification gives you the *average* returns. Illustrative construct: System B has zero net return but negatively correlated performance to System A (high return) — the average of the two is half of System A's return, yet combined *risk* could drop by more than 50%. If the objective function is a return-to-risk ratio, the combined portfolio beats either single asset — "yet it may not be satisfying to the investor" (a return-ratio optimum is not necessarily return-maximizing or psychologically acceptable) (Kaufman Ch.24).

### 1.5 Changing correlations

Correlation is normally measured over a long period or rolling average, but averages hide short-period behavior. Worked example: 20-day rolling correlation of S&P futures to 30-year bonds, the euro, and gold during fall 2008 — the subprime crisis pushed gold and the euro to about −0.6 correlation with the S&P, bonds also about −0.60. A shorter calculation period would show even more extreme correlations. **General finding: "many of the statistics that we use to make decisions are good under normal market conditions. When a price shock occurs, they go to extremes, for which we are always unprepared"** (Kaufman Ch.24). Three stated ways to avoid this unexpected risk: (1) be out of the market as much as possible; (2) cap portfolio leverage; (3) use uncorrelated strategies.

### 1.6 Five portfolio models (cited to Narang, *Inside the Black Box*)

1. **Equal-Dollar Weighting** — each asset gets an equal account-value share; forecasting relative asset performance is "extremely unreliable," so unequal weighting concentrates risk.
2. **Equal-Risk Weighting ("volatility parity")** — equalizes risk via volatility/expected-drawdown; worked example: asset A (4% vol) gets 20%, asset B (1% vol) gets 80% (inverse-volatility weighting). Common for futures portfolios.
3. **Alpha-Driven Weighting** — assets ranked by expected alpha get larger (non-linearly scaled) allocations; favors past-best performers.
4. **Decision-Tree Models** — match each asset to a strategy-type/risk-level combination for net allocation.
5. **Optimization** — classic mean-variance: evaluates volatility/correlation to maximize return, minimize risk (elaborated below) (Kaufman Ch.24).

### 1.7 Too much diversification

Diversification benefit declines as assets increase — a second asset yields a huge risk reduction, a tenth or twentieth little (Figure 24.1). Adding assets can continually improve the reward-to-risk ratio, but average returns can drop to an undesirable level. Very large funds sometimes cannot find enough assets to absorb their full investment and must settle for lower-return or slightly-higher-risk assets to stay fully invested — either "reduces performance" (Kaufman Ch.24).

**Perfect vs. real-world diversification**: with perfect (fully independent) diversification, 2 assets → risk falls to 50% of initial; 3 → 33.3%; 4 → 25% (1/n scaling). Real-world caveat: a fully diversified real-world portfolio might reduce initial risk by only ~50% (far short of the 1/n curve, since real assets aren't fully independent). "More assets always offer better diversification than fewer assets" — but marginal risk-reduction drops sharply above ~4 assets (Kaufman Ch.24).

**Case study — equal weighting improves ETF sector returns**: cap-weighted Sector SPDR ETFs vs. Guggenheim's equally-weighted equivalents — equally-weighted performed slightly better (and by information ratio). A narrower 9-stock comparison: cap-weighted top-9 returned 15.2%, full index 19.4%, equally-weighted 9 stocks 28.5% — largest allocations (by cap weight) did not perform best (Kaufman Ch.24).

### 1.8 Classic portfolio allocation calculations (MPT/Markowitz)

Kaufman's formulas (embedded-graphic extraction gaps, reconstructed as standard MPT forms and flagged as such):
- **Expected portfolio return**: E(R) = Σ wᵢ·E(Rᵢ)
- **Portfolio variance (n-asset)**: σp² = Σᵢ Σⱼ wᵢwⱼ·Covᵢⱼ, where Covᵢᵢ = σᵢ²
- **Covariance from correlation**: Covᵢⱼ = σᵢ·σⱼ·ρᵢⱼ
- **Decision rule**: given equal returns, prefer lower variance; given equal variance, prefer higher return (cross-ref efficient frontier, §4 below).

**Caveat on long-interval correlation stats**: a single catastrophic high-correlation event can be statistically "lost" among many normal-period observations — look explicitly at maximum portfolio loss and assume "the largest historic loss will be exceeded sometime in the future," partly by chance, partly because "the probability of a run increases as the amount of data increases." Recommendation: also run VaR on the final portfolio — "an excessive number of risk spikes is a sign of too much leverage" (Kaufman Ch.24, cross-ref Ch.23 VaR).

**Worked spreadsheet example**: monthly returns, SPY and Vanguard bond ETF BND, April 2007–July 2018, 60% SPY / 40% BND. Results: SPY return 5.8%, BND 3.6%, combined 5.2%; SPY risk 14.6%, combined risk 8.9%. Given 2008's ~50% equity loss, 5.2% AROR "seems good" — the bond allocation "saved a large part of the drawdown in SPY" in 2008 (Kaufman Ch.24).

### 1.9 Finding optimal allocation via Excel Solver

Worked example: S&P 500 futures, gold futures, Apple, Microsoft, Nov 2010–Oct 2011. Procedure: align price data, compute returns, index prices to 100, initial equal weights, sum-of-allocations = 1.0 constraint, SUMPRODUCT weighted returns, portfolio NAV, annualized std dev and AROR, information ratio (AROR/annualized-risk) as the Solver objective. Solver settings: maximize the information-ratio cell; change the weighting cells; constrain weight sum = 1.0, each weight ≥ 0 (or between −1/+1 if shorting is allowed). **Result**: 9.1% S&P futures, 55% gold futures, 35.9% Apple, 0% Microsoft — information ratio 1.97 ("high") (Kaufman Ch.24).

### 1.10 GASP — Kaufman's genetic-algorithm portfolio allocator

**Motivation**: Solver/classic mean-variance doesn't incorporate cross-correlations well, market liquidity, or professional considerations — and critically, **standard deviation and covariance calculations break down for active trading systems with disjoint (non-daily) returns** (Kaufman Ch.24).

**The core problem**: a systematic 2-MA-crossover system on S&P and bonds may be in the market only ~50% of the time (zero returns on flat days). Worked example: if bonds' passive daily std dev is 0.5% and the system is in the market 50% of the time, the *measured* std dev of the trading-return series drops to ~0.25% purely from the zero-return days — making a less-frequently-in-market method appear both lower-risk AND lower-return, even if returns are larger on active days. Kaufman's rebuttal to the standard counterargument (zero returns should count): "Perhaps they should use their allocations to trade their own portfolio" (Kaufman Ch.24, explicit opinion).

**Three risk-measure alternatives considered**:
1. Annualized volatility (traditional).
2. Residuals of a linear regression fit to returns — drawback: penalizes upside deviation from trend, not just drawdowns.
3. **Semivariance of daily drawdowns — the measure GASP actually uses.** Advantage: doesn't need annualizing, and "has no agenda with respect to the profit patterns" — only penalizes drawdowns.

**GASP objective function**: OF = AROR / SDD, where SDD = sqrt[Σ(Hᵢ − Eᵢ)² / n] over days where Hᵢ ≠ Eᵢ (Hᵢ = peak cumulative equity, Eᵢ = current equity). Structurally identical to the Ulcer Index (Kaufman Ch.23).

**Target risk level**: user-specified probability of a specific loss size over a specific period (e.g., "0.1% chance of losing 10% during 10 years"). Both max and min target risk must be specified — the minimum prevents trivially minimizing risk via tiny capital use.

**Constraints**: liquidity (don't exceed 3% of average daily volume; specify in absolute units, not percentages); negative-allocation restriction (most investors prefer positive-only, though the optimizer might otherwise suggest short positions as implicit arbitrage, e.g. 5% long euros/−3% gold).

**Subportfolio approach**: choice between one large pool vs. sector/group subportfolios optimized first, then re-optimized as a group-return series — the two-stage approach is much faster (GA compute expands exponentially with combinations) and lets human judgment about correlated-stress-period behavior be imposed where limited price history doesn't capture it — **"there should always be enough data and it should be selected to include high-risk events"** (Kaufman Ch.24).

**Six-step GA process**: (1) Initialization; (2) Calculation of the objective function; (3) Test for completion; (4) Propagation; (5) Mating; (6) Mutating (loop back to 2).

1. **Initialization**: return series per asset; pool of random portfolios ("strings"), recommended ~5,000 for <25 assets (combinatorial framing: a 5-asset portfolio in whole-percent increments has 100^5 = 10 billion combinations). Random-portfolio generation: uniform random number per asset, sum to T, divide each by T to normalize weights to 1.0. Constraints applied during initialization: individual-asset caps (reject violators), group liquidity constraints (rescale via a further random factor), min/max absolute risk bands (reject portfolios outside 8-20% in a worked example).
2. **Evaluation**: portfolio return per day via SUMPRODUCT(weights, returns); build NAV, compute AROR/AStd, OF = AROR/AStd (worked example: AROR 29.33%, vol 19.15%, OF 1.53). **Rescaling to target volatility**: multiply all allocations by (target/actual) ratio if below target; individual portfolios allowed ±5% variance from target; rescaling doesn't change the information ratio itself — only satisfies absolute-risk/liquidity constraints (must re-check liquidity after rescaling).
3. **Test for completion**: convergence (best OF stable for 2-3 cycles) OR fixed iteration count. Author recommends fixed iterations, preferring 3-5 fresh reruns to confirm a global (not local) maximum over one very long run.
4. **Propagation** (survival of the fittest): rank by OF; draw a uniform random number between the pool's lowest/highest OF; find the closest-OF portfolio and copy it into the new pool; repeat until the new pool is full. Warning: shortcuts (multiplying copy counts, using OF's integer value directly) over-concentrate the gene pool and risk converging on a local maximum. Target removal rate: ~10% of worst performers per cycle.
5. **Mating**: select two distinct portfolios, draw a random split point among assets, swap assets on one side of the split between the two, normalize resulting weights, correct group-liquidity constraints if the split falls inside a constrained group. Mate 10-20% of the pool per cycle (too little limits new combinations; too much risks losing the best existing results).
6. **Mutating**: select a random portfolio and random asset, assign a new random weight, adjust for constraints, normalize. Mutate 5-15% of the pool (too much loses best results; too little causes premature convergence).

**Optimal subsets**: for large universes (50-100 assets), restrict to a subset (e.g., 15) via zero-weighting inactive assets during initialization, maintaining subset size through mating (split-matched active-asset counts) and mutation (swap-in/swap-out). Subset solutions are much faster and "only slightly" worse than a full-universe optimum.

**Solution-quality guidance**: for small asset counts GASP finds the true optimum; for 20-50 assets, "very likely" optimal; for very large counts, close to optimal even exploring only a fraction of combinations. Limiting allocation precision (whole-percent vs. 0.0001) drastically shrinks the search space without materially changing the resulting allocation shape.

**Verifying the global maximum**: run GASP multiple times from fresh random pools; consistent allocations across runs indicate a likely global maximum. Recommendation: 5 runs of 50-100 cycles rather than 1 run of 500 cycles (convergence typically by ~50 cycles at a 10-15% mating/mutation rate).

**Worked 19-strategy NASDAQ-100 case study**: 19 unique long/short trend/mean-reversion strategy combinations, 7.16-year history, target subset of 12 of 19, $10M investment, pool 5,000, mutation 10%, risk measure = semivariance of drawdowns, target risk 16.7% at 99.74% confidence, 100 cycles/pass, 3 passes. Best solution (case 59, OF 17.315) achieved 80% of total improvement in the first 15 cases. Across 3 passes, OF improved 17.315 → 17.801 → 17.894 while AROR improved only 49.46% → 50.95% ("showing that returns are very similar") — **key robustness finding: despite visually different allocations between passes, the *same* strategies received allocations with a similar distribution shape** — "there are clearly a range of allocations that will return similar results." Total runtime: 85 minutes for 3×100 cycles on 2004-era hardware.

**Test interval recommendation**: short intervals track current conditions but miss full bull/bear balance and extreme-risk periods. "No one has yet shown that an allocation based on short intervals is better than one based on a longer period." Recommendation: ensure the test period spans bull and bear markets plus price shocks, and specifically "be sure that the portfolio will survive the financial crisis of 2008" (Kaufman Ch.24).

### 1.10a Hedge Fund Replication (Ch.20 static/dynamic methods)

*(Distinct from the portfolio-copying/allocation-matching flavor of "replication" — this is Kaufman's Ch.20 "Advanced Techniques" treatment of reverse-engineering a THIRD PARTY's fund returns, not the Ch.24 Excel Solver/GASP asset-allocation machinery covered in §1.9-1.10 above, though it reuses the same Solver tool.)*

**Concept**: technology enables mathematically replicating hedge fund performance without paying hedge fund fees — any replication inaccuracy (tracking error) is offset by the lower cost of replicating vs. paying fund fees. Replication can target a single fund, a fund of funds, or a hedge fund index; marketed as "a conservative and algorithmic approach to investing" (Kaufman Ch.20).

**Static method**: given a fund investing only long in, e.g., 10 mining-sector stocks, use Excel's Solver on the fund's historic returns to solve for the % allocation to each of the 10 stocks needed to reproduce those returns (assumes constant allocations over the analysis window). If the target fund rebalances (e.g., monthly), the regression must be re-run more often — possibly with constraints limiting how much each stock's solved weight can change per re-run.

**Dynamic/daily method**: each day, ask "what allocation would have reproduced yesterday's return?", then trade to align the replicator's own portfolio with that solved allocation; repeat daily. If the target fund doesn't change positions often, the replicator's positions converge toward the fund's own — described as analogous to a Monte Carlo approach converging on the correct distribution. This approach carries tracking error while converging, which "may be better or worse than the actual hedge fund" (Kaufman Ch.20).

**Rebalancing trade-off**: early replication practice rebalanced monthly, which allowed large tracking errors to accumulate; a better method rebalances whenever tracking error exceeds a threshold, trading off tracking-error size against rebalancing cost — the same threshold-rebalancing logic as the Volatility Factor 20% band in §1.11 below.

**Cited benchmark**: the Hedge Fund Replication Index (hedgefundreplication.com) is said to replicate **85%** of hedge fund returns, leaving a **15%** tracking error — still described as less costly than the fee load of an actual fund-of-hedge-funds (Kaufman Ch.20).

### 1.11 Volatility stabilization

**Motivation**: a portfolio engineered for a stated volatility (e.g., 12% annualized) implies a 16% chance of exceeding that drawdown and 2.5% chance of exceeding 2× it — but these are long-run averages; realized volatility can swing between quiet years (8%) and volatile spikes (18-25%). No volatility-stabilization method eliminates the need for additional risk controls like VaR — "all measures of risk look only at historic volatility; using multiple measures is always better" (Kaufman Ch.24).

**Volatility Factor formula**: VF = Target Volatility / Actual (measured) Volatility. VF > 1 → scale up; VF < 1 → scale down. Worked example: target 12%, measured 8.78% → VF ≈ 1.408.

**Threshold-based rebalancing**: the applied VF only updates when it differs by ≥20% from the currently-applied factor — avoids excessive position churn. When the factor does change, all positions are scaled by the ratio of new/old factor.

**Real-world case study**: macrotrend world-futures portfolio, 1989–June 2018 (29 years), unadjusted AROR 8.7%. Applying volatility stabilization (target 12%, 20% rebalancing threshold) produced AROR 14.3% at the same volatility level — a stated **64% improvement**. Lag caveat: in rising-volatility regimes, stabilization lags (realized vol runs above target, e.g., ~13% vs. 12%); in declining-volatility regimes it lags below (10-11%).

**Switching-cost mitigations**: (1) use a longer calculation period for the volatility estimate; (2) use a volatility-change threshold before altering positions. Choosing/combining these requires strategy-specific testing.

**Capping exposure (regulatory)**: European UCITS caps: total exposure ≤ 2.5× current account equity; commodity exposure ≤ 20% of current account equity (stricter, driven by fear of physical delivery). Capping must be applied LAST, after all other adjustments. Exposure = face value of assets held. If exposure E exceeds cap C, scale ALL positions (including new ones causing the breach) by C/E. Capping reduces total returns but may have minimal effect on the information ratio, "because high leverage tends to coincide with low volatility/low price direction" — "Given regulations, most portfolio managers have no choice" (Kaufman Ch.24).

### 1.12 Business risk and drawdown/re-leveraging rules

Allocator-imposed constraints example: don't risk more than 4% on any one day (via VaR); don't lose more than 15% of the investment. At 12% target volatility, there's a 16% chance of a 12%-or-greater loss at some point.

**Drawdown response dilemma** (not resolved with a single rule): reducing exposure by 25% after a 10% drawdown lowers risk of ruin but slows recovery — "a difficult business decision." If exposure is kept unchanged: "You will recover the losses or go out of business." If cutting toward a hard 15% floor, the author proposes cutting positions 20% each additional 1% lost, stabilizing around a 12% loss after two such cuts.

**Kaufman's proposed systematic re-leveraging process** (5 steps, author's own, not attributed to an external source): (1) track performance as though still at full target volatility (a "shadow" system); (2) wait until the shadow system recovers 3% of a 12% loss (25% of the loss); (3) wait for a subsequent 1% pullback in the shadow system's profit (confirmation); (4) add back 25% of the original position size; (5) repeat from step 2. Reset rule: if the full 3% shadow profit is given back, cut position size another 25% and restart.

**The Turtles' de-leveraging rule** (restated): for every 10% portfolio drawdown from peak equity, cut position size by 20%; for every 6⅔% recovery, add back 10% (costs included). Contextual note: at the time, most futures managers considered 50% (not 15%) the maximum tolerable loss. Kaufman's closing caveat: "These may not be the best plans for all investors, but business risk is real, and a clear plan is needed before it is necessary" (Kaufman Ch.24).

### 1.13 Dogs of the Dow / Best-Return Dow Rebalance with Volatility Hedge (Ch.13)

*(A distinct, Ch.13-specific system — not the classic O'Higgins "Dogs of the Dow" value strategy (Ch.22, covered as a mean-reversion/value entry in `03_mean_reversion.md`). This Ch.13 variant inverts the classic theory's stock selection and adds a portfolio-level volatility-triggered hedge overlay, which is why it belongs here rather than in the mean-reversion file.)*

**Reversed selection logic**: the classic Dogs-of-the-Dow theory (buy the Dow's 10 worst-return stocks each Dec 31, expecting dividend-driven mean reversion) tested poorly in Kaufman's own worked test. A **reversed test** — buying the 10 *best*-return Dow stocks, held one year — produced results similar to the S&P. Switching from yearly to **monthly rebalancing** of the best-return basket "greatly improved returns." **Author's conclusion**: "success is persistent and poor performance is also persistent" — i.e., stock performance shows autocorrelation/momentum at the basket level, directly contradicting the classic Dogs-of-the-Dow "worst performers reverse" premise (Kaufman Ch.13).

**Volatility hedge overlay**: despite its outperformance, the monthly-rebalanced best-stocks portfolio still showed extreme risk in 2008. Because risk correlates with volatility, the system hedges long positions when **20-day annualized Dow Index volatility exceeds 90%**:
1. Sell 50% of each stock currently held in the portfolio, freeing half the invested capital and reducing risk.
2. Use the freed funds to short the 10 *worst*-performing Dow stocks, equal investment (1/10 of freed funds) per stock.
3. **Alternative**: short the Dow ETF (DIA) instead of the 10 worst stocks — noted as offering weaker protection than the direct 10-worst-stock short (Kaufman Ch.13).

This is functionally a regime-triggered partial-hedge/de-leveraging rule (cross-ref the Turtles' de-leveraging rule and Volatility Factor threshold rebalancing above), but keyed to an absolute volatility threshold on the underlying index rather than to the portfolio's own drawdown or a target-volatility ratio.

---

## 2. Vince's portfolio-level optimal f and correlation effects (Ch.5-8)

### 2.1 Chapter 5 — causal and random multi-position relationships (background to portfolio theory)

Vince Ch.5 is chiefly an options-optimal-f chapter, but it establishes the vocabulary and directional applicability rules later used for full portfolio construction:

- **Causal relationship**: correlation with a factual, logical, connective explanation (e.g., IBM puts vs. IBM calls, correlation ≈ −1). Practical rule of thumb: "a causal relationship almost always consists of any two tradeable items... that have the same underlying instrument" (Vince Ch.5).
- **Correlative relationship**: correlation exists without a clear causal explanation (typically weaker, e.g., IBM calls vs. Digital Equipment calls — both "computer group" but not deterministically linked). Vince's own caveat: "there is not a fine line that differentiates causal and correlative relationships" (Vince Ch.5).
- **Random relationship**: pairwise correlation coefficient is exactly 0 (or asymptotically expected to be 0).
- **Directional applicability rule (explicit, repeated for both causal and random cases)**: Chapter 6's correlative techniques (handling ANY correlation from −1 to +1) can always substitute for the causal- or random-relationship formulas in Ch.5, but NOT vice versa — applying causal/random-case formulas to a genuinely correlated (nonzero, non-causal) pair is erroneous (Vince Ch.5).
- For multi-leg causal positions (all options on the same underlying, no correlation-matrix machinery needed): HPR(T,U) = (1 + Σ Ci(T,U))^P(T,U), same shared probability across all legs. Simple case: legs put on entirely at a debit use Eq (5.14)'s form directly (S, Z(T,U-Y) redefined as the NET price/value of ALL legs combined); if put on at a credit, use Eq (5.20)'s form similarly. Worked conceptual example: a long straddle (long put + long call, same strike/expiration) with optimal f of 1 contract-pair per $2,000 equity means, for every $2,000 in equity, buy 1 full straddle unit — "the optimal f returned by this technique pertains to financing 1 unit of the ENTIRE position, no matter how large that position is" (Vince Ch.5).
- For random-relationship (zero-correlation) multi-leg positions: HPR(T,U) = (1 + Σ Ci(T,U))^(Π Pi(T,U)) — the exponent becomes the PRODUCT of each leg's individual probability, reflecting independence, rather than one shared probability.

**Generalized multi-leg causal formula, Eq (5.22), and its per-leg contribution terms:**
```
HPR(T,U) = (1 + Σ[i=1,N] Ci(T,U))^P(T,U)                                (5.22)
Ci(T,U) = f*(Z(T,U-Y)/S - 1)          (5.23a, debit leg / long underlying)
Ci(T,U) = f*(1 - Z(T,U-Y)/S)          (5.23b, credit leg / short underlying)
```
where N = number of legs; same f, S, Z, P, Y definitions as Ch.5's single-position formulas (`10_position_sizing.md` §1.11), applied per leg. Geometric mean reuses Eq (5.18a) with the range extended to **±8 SD** (Vince's stated general-purpose default for multi-leg work, vs. ±3 SD for a single leg): `G(f,T) = {Π[U=-8SD,8SD] HPR(T,U)}^(1/Σ P(T,U))`.

**Random-relationship (zero-correlation) multi-leg geometric mean, Eq (5.24)/(5.25):**
```
HPR(T,U) = (1 + Σ[i=1,N] Ci(T,U)) ^ Π[i=1,N] Pi(T,U)                    (5.24)
G(f,T) = { Π[U1] ... Π[UN] { (1+Σ Ci(T,U))^(Π Pi(T,U)) } } ^ (1 / (Σ[U1]...Σ[UN] Π Pi(T,U)))   (5.25)
```
(each Ui range spans ±8 SD; Ci(T,U) per Eqs 5.23a/b). Structural difference from the causal case: the exponent is the PRODUCT of each leg's individual probability rather than one shared probability.

**Explicit nested-loop pseudocode for the full multi-leg, multi-exit-date search** — one of the few places Vince gives literal algorithmic structure rather than just a formula (Vince Ch.5):

Shared exit date across all legs:
```
For each mandated exit date (weekday) between now and expiration
  For each value of f (until optimal is found)
    For each market system [i.e., leg]
      For each tick between +8 and -8 std. devs.
        Determine the HPR
```
Independent per-leg exit dates (explicit compute-cost warning: this "compounds the number of computations geometrically" vs. the shared-exit-date version):
```
For each market system [i.e., leg]
  For each mandated exit date (weekday) between now and expiration
    For each value of f (until optimal is found)
      For each market system
        For each tick between +8 and -8 std. devs.
          Determine the HPR
```

**Arithmetic average HPR (AHPR) for options, and the SD identity derived from it:**
```
AHPR = {Σ[U=-8SD,+8SD] ((1+f*(Z(T,U-Y)/S-1))*P(T,U))} / Σ[U=-8SD,+8SD] P(T,U)     (5.26a, long/debit)
AHPR = {Σ[U=-8SD,+8SD] ((1+f*(1-Z(T,U-Y)/S))*P(T,U))} / Σ[U=-8SD,+8SD] P(T,U)     (5.26b, short/credit)
SD = (A^2 - G^2)^(1/2)                                                  (5.27)
```
where A=AHPR, G=geometric mean HPR — the same Pythagorean relationship as Ch.1's Fundamental Equation of Trading (Eq 1.27, `SD^2=A^2-G^2`, `10_position_sizing.md` §1.5), applied here specifically to options HPR statistics.

- **Explicit acknowledged limitation of Ch.5's machinery**: it does not address the general case of a nonzero, non-±1 linear correlation coefficient between components — deferred entirely to Chapter 6, which generalizes to ANY correlation structure using each position's correlation coefficient (of its 1-contract daily HPR) to every other position, plus each position's arithmetic average HPR and standard deviation of HPRs (Vince Ch.5).

### 2.2 Chapter 6 — the Efficient Frontier / E-V Theory derivation (Vince's full treatment)

Vince Ch.6 generalizes portfolio construction to handle ANY linear correlation coefficient between −1 and +1, presented as the professional/institutional Markowitz Modern Portfolio Theory technique ("E-V Theory" — Expected return/Variance of return), for a portfolio of stocks in a cash account (fully paid, no margin), from first principles with full worked matrix algebra.

**Stated assumption**: the generating return distributions have FINITE variance (footnoted exception: Fama 1965 for stable-Paretian/infinite-variance cases, not covered in this book) (Vince Ch.6).

**Inputs**: expected return (%) and expected variance of return per component, over a CONSISTENT holding period, applied to a worked 4-investment example (Toxico, Incubeast, LA Garb, Savings Account).

**Correlation-coefficient methodology**: must be computed on RETURNS data (not raw prices), at the SAME time-frame/granularity as the return/variance inputs.

**Formulas**:
- Covariance (6.01): COVₐ,ᵦ = Rₐ,ᵦ·Sₐ·Sᵦ
- Correlation from covariance (6.02): Rₐ,ᵦ = COVₐ,ᵦ/(Sₐ·Sᵦ)
- Self-covariance identity (6.03): COV(X,X) = Sx² = Vx
- Full investment constraint (6.04): Σ Xᵢ = 1, each Xᵢ ≥ 0
- Expected portfolio return (6.05): Σ Uᵢ·Xᵢ = E
- Portfolio variance, 4 equivalent forms (6.06a-d), e.g. V = Σᵢ Σⱼ Xᵢ·Xⱼ·COVᵢ,ⱼ

**Optimization goal**: find the Xᵢ's (summing to 1) minimizing V for a given target E — solved via the **Method of Lagrange Multipliers** (general background given, Eq 6.07-6.08), producing a system of N+2 equations in N+2 unknowns (N weights + 2 Lagrangians L1, L2) for N securities (Eq 6.09-6.12). Solved via **row-equivalent matrices / Gauss-Jordan procedure** (three allowed row operations: swap rows, scale a row, add a scaled row to another).

**Worked 4-investment result at E=.14**: X1(Toxico)=.12391, X2(Incubeast)=.12787, X3(LA Garb)=.38407, X4(Savings)=.36424, L1=−2.6394, L2=.22434. Minimum variance V=.0725872809.

**Interpreting the Lagrangians**: L1 = −δV/δE ("the marginal variance in expected returns"); L2 (restating the constraint as ΣXᵢ=M) = δV/δM ("the marginal risk of increased or decreased investment").

**Real-world "slop" from share indivisibility**: at $50,000 total, rounding to a lot deviates from the theoretical optimum by ~6.5%; at $5 million the same rounding deviates by only ~0.2% — larger capital bases track the theoretical optimum more closely (Vince Ch.6).

**Handling negative weights**: if any of the first N solution rows is ≤0 (an infeasible short position under the ΣXᵢ=1, Xᵢ≥0 setup), drop that variable's row+column and re-solve the reduced system from scratch; multiple simultaneous negative weights require dropping multiple rows/columns together. Negative Lagrangian values (L1/L2) require NO correction — they're allowed to be negative.

**Matrix inversion alternative**: derive C⁻¹ once (per the same security set), then solve for ANY target E by simple multiplication rather than re-running Gauss-Jordan each time — confirmed to reproduce identical results.

**Incorporating short positions**: a short position's "return" = expected price-decline gain minus owed dividends (margin interest not modeled — cash-account assumption). **Sign-flip rule**: for every pairwise correlation involving a shorted security, multiply by −1; if BOTH legs of a pair are shorted, the double sign-flip cancels and the correlation is unchanged from the long-long case.

### 2.3 Chapter 7 — The Geometry of Portfolios: marrying the Efficient Frontier with Optimal f

This is Vince's central synthesis chapter, extending Ch.6's efficient frontier to ANY tradeable instrument while incorporating optimal f and mechanical trading systems, to obtain "a truly efficient portfolio for which geometric growth is maximized" (Vince Ch.7).

**Capital Market Lines (CML)**: mixing the risk-free asset (point A) with the tangent portfolio (point B — the ONE efficient-frontier portfolio a line from A is tangent to) DOMINATES any efficient-frontier portfolio at the same risk level. To the right of B, the CML represents borrowed leverage into B, which also dominates. **Separation theorem** (footnoted, Tobin 1958): all rational investors want the SAME portfolio (B), differing only in leverage/deleverage degree. The tangent portfolio is usually well-diversified; portfolios far along the frontier tend to have few components.

**Formula (7.01a) — locating the tangent portfolio**: Tangent Portfolio = MAX{(AHPR−(1+RFR))/SD} — this bracketed expression is explicitly the **Sharpe ratio**. Multiplying the Sharpe ratio by √(number of periods) yields the t-statistic for confidence that AHPR exceeds RFR by more than chance.

**Positioning a target point on the CML (Vince Ch.7, Eq 7.02-7.04)**: `P = SX/ST` (7.02) — the % of assets that must sit in the tangent portfolio to reach a target CML risk coordinate SX, where ST = the tangent portfolio's own SD coordinate (P>1 implies borrowing to leverage into the tangent portfolio beyond 100%). `ACML = (AT·P) + ((1+RFR)·(1−P))` (7.03) — the CML's AHPR at that point, where AT = the tangent portfolio's own AHPR. `SD = P·ST` (7.04) — the inverse, finding the risk coordinate for a given target AHPR via P. Worked (Vince Ch.7): at SX=.08296 (beyond the tangent point at ST=.02986), P=.08296/.02986=2.7782 → **277.82%** in the tangent portfolio, i.e., fully invested plus borrowing $1.7782 for every $1 already committed.

**Geometric Efficient Frontier**: everything above uses the ARITHMETIC average HPR, but reinvesting profits requires the GEOMETRIC average HPR — "this changes things considerably." GHPR = (AHPR² − V)^(1/2) (Eq 7.05, same relationship as Ch.1's fundamental equation of trading). The geometric-optimal portfolio satisfies AHPR = V + 1 (Eq 7.06a-d) — i.e., **arithmetic mathematical expectation exactly equals variance**.

**Central paradox, explicit and important**: variance is generally positively correlated with drawdown. Since the geometric-optimal portfolio is defined by E=V, **the geometric-optimal portfolio will generally show HIGH drawdowns**, and "the greater the GHPR of the geometric optimal portfolio... the greater will be its drawdown." Vince states this explicitly: **"when we perform the exercise of diversification, we should view it as an exercise to obtain the highest geometric mean rather than the lowest drawdown, as the two tend to pull in opposite directions!"** (Vince Ch.7) — this directly cross-references and reinforces Vince Ch.1's flagged claim that "diversification's primary benefit is improving the geometric mean, not reducing worst-case drawdown," which Vince calls "absolutely contrary to the popular notion."

**Terminal wealth over N trades, Formula (7.07)**: `GTWR = GHPR^N` (compounded; worked GHPR=1.0154 over 50 trades → 2.15x) vs. the **arithmetic (non-reinvested) equivalent, Formula (7.08)**: `ATWR = 1+N·(AHPR−1)` (worked AHPR=1.03 over 50 trades → 1+50×.03=2.5x). Initially ATWR > GTWR, but GTWR eventually overtakes ATWR and "would continue to outpace the arithmetic... eventually infinitely greater." **Crossover point N, four equivalent forms, Formula (7.10a-d)**: `GHPR^N = 1+N·(AHPR−1)` (7.10a, exact crossover condition) ≡ `1+N·(AHPR−1)−GHPR^N=0` (7.10b) ≡ `1+N·AHPR−N−GHPR^N=0` (7.10c) ≡ `N=(GHPR^N−1)/(AHPR−1)` (7.10d) — must be solved by iteration since N appears on both sides (restating the general inequality/question form, Eq 7.09: `GHPR^N ≥ 1+N·(AHPR−1)`). Worked example (GHPR=1.01542, AHPR=1.031) gives a crossover at N≈83.49894 elapsed trades.

**Unconstrained portfolios — the NIC device**: to lift the ΣXᵢ=1 constraint (enabling explicit leverage within the matrix framework), Vince adds an artificial security **NIC** (Non-Interest-bearing Cash: AHPR=1.0, zero variance/covariance to everything) and sets the sum-of-weights constraint arbitrarily high (suggested: 3× the number of real market systems). **Explicit warning**: a real component with zero variance and AHPR>1 (e.g., a savings account) will cause the solver to converge on a degenerate all-in-that-component, arbitrarily-levered solution — such components must be excluded before solving. **Diagnostic rule**: if NIC does not appear with a positive weight in the solution, the sum-of-weights constraint was not set high enough — raise it and re-solve. Weights >100% are legitimate leverage, not an error.

**How optimal f fits with optimal portfolios — Vince's central critique of standard practice**: conventional portfolio management derives expected return/variance from the CURRENT PRICE, computes weights, and converts to shares via current price. Vince: "That generally is how portfolio strategies are currently practiced. But it is not optimal. Here lies one of this book's many hearts" (Vince Ch.7). **The correct approach**: derive expected return and variance from the **optimal f, in dollars, for each component**, using fixed-interval HPRs (Eq 1.15/2.12) computed consistently across all components — "Portfolios whose parameters... are selected based on the current price of the component will NOT yield truly optimal portfolios... you must derive the input parameters based on trading 1 unit AT THE OPTIMAL F for each component" (Vince Ch.7).

**Reconciling >100% weights with optimal f — the "weight ≠ quantity" insight**: divide each component's dollar optimal f by its portfolio weighting to get the adjusted f actually traded (per unit of TOTAL equity, not a sub-allocation). Worked: Toxico f=$2,500, weight 1.025982 → adjusted f=$2,436.69. **Central thesis, explicit**: "In a nonleveraged situation, such as a portfolio of stocks that are not on margin, weighting and quantity are synonymous. Yet in a leveraged situation, such as a portfolio of futures market systems, weighting and quantity are different indeed" (Vince Ch.7).

**Correlation coefficient caveat — detrending**: correlating HPRs of two positive-expectation systems shows a spurious "slight tendency toward positive correlation" purely from both equity curves trending upward (a shared-trend artifact, not genuine co-movement). Suggested fix: fit a least-squares regression to each equity curve, take residuals, convert to non-cumulative daily changes, THEN correlate. **Restriction**: valid ONLY for daily equity changes, never raw prices. **Explicit failure mode**: for infrequently-trading systems, detrending can artificially produce SPURIOUSLY HIGH positive correlation (regression lines rise slightly every day while actual daily change is zero on most non-trading days for both systems, mechanically creating false positive correlation) — "This detrending technique must always be used with caution" (Vince Ch.7). AHPR/SD inputs themselves must always use non-detrended data.

**GHPR-CML and the tangent/geometric-optimal coincidence condition (Vince Ch.7)**: the GHPR-based CML is derived from the AHPR-CML via `CMLG = (CMLA² − VT·P)^(1/2)` (Eq 7.11), where CMLA = the AHPR-CML's E-coordinate at the same risk level, VT = the tangent portfolio's variance coordinate, P = % in the tangent portfolio (Eq 7.02). An equivalent, direct way to locate the tangent portfolio using GHPR instead of AHPR: `Tangent Portfolio = MAX{(GHPR−(1+RFR))/SD}` (Eq 7.01b, substituting GHPR for AHPR in 7.01a). The AHPR-CML and GHPR-CML tangency points always share the SAME SD coordinate. **The tangent (Sharpe-maximizing) portfolio and the geometric-optimal (E=V) portfolio are generally NOT the same portfolio** — they coincide only under the special condition `RFR = GHPROPT − 1` (Eq 7.12, where GHPROPT = the GHPR of the geometric-optimal portfolio). IF RFR > GHPROPT−1, the geometric-optimal portfolio sits to the LEFT of (less variance than) the tangent portfolio; IF RFR < GHPROPT−1, the tangent portfolio sits to the left of the geometric-optimal portfolio. In all cases the tangent portfolio can never have a HIGHER GHPR than the true geometric-optimal one, by definition.

**Nominal-to-effective annual rate conversion (Vince Ch.7, Eq 7.14)**, needed to derive a daily RFR input for the CML/tangent-portfolio formulas above: `E (effective annual rate) = (1+R/M)^M − 1`, where R = nominal annual rate, M = compounding periods/year. Worked: 9% nominal compounded monthly → `(1+.09/12)^12−1 = .093806898` ≈ **9.38%** effective annual — then divided by 260.8875 (the weekday-year convention) to get a daily RFR of ≈.00035957/day.

**Completing the loop — the canonical unconstrained portfolio**: for any target E, the unconstrained optimal portfolio is THE SAME PORTFOLIO, just levered up or down differently — the ratios between component weightings are IDENTICAL at every point along the unconstrained frontier (contrasted with CONSTRAINED frontiers, where ratios change along the frontier). This canonical portfolio is characterized as the constrained (ΣXᵢ=1) portfolio with L2=0, equivalently the unconstrained portfolio with L1=−2 (Eq 7.06e) — and is exactly the tangent portfolio for RFR=0. **Optimal leverage multiplier**: q = (E−RFR)/V (Eq 7.13, cited to Latane & Tuttle 1967), "a very close approximation" converting the constrained tangent portfolio into the unconstrained geometric-optimal portfolio.

**RFR practical guidance**: always assume RFR=0 for futures (margin trading isn't literal borrowing/lending); for stocks, RFR should reflect the actual leverage cost (margin interest).

### 2.4 Chapter 8 — Risk Management: reallocation, portfolio insurance, margin constraints, rotating markets

*(Not explicitly in the assigned reading list, but directly continues Ch.7's machinery into practical portfolio-construction constraints and is the source of Vince's correlation-editing rule and market-rotation guidance requested under §5-7 below; included for completeness.)*

### 2.5 Chapter 1 — Combination Portfolio Allocation (CPA): the empirical precursor to the Lagrange method

Before Ch.6's full matrix-algebra efficient frontier (§2.2 above), Vince's Ch.1 gives a brute-force, empirical, non-parametric bridging technique for a researcher who wants a first-pass portfolio construction without solving a Lagrangian system: **Combination Portfolio Allocation (CPA)**.

**Procedure (Vince Ch.1/Introduction)**: enumerate every SUBSET of the available market systems (every combination of 1, 2, 3, ... up to all N systems), and for each subset, enumerate every percentage-allocation combination at a chosen increment (e.g. 10% steps: 100/0, 90/10, 80/20, ... for a 2-system subset; finer grids for larger subsets). For each (subset, allocation) combination, compute:
1. The average **daily net HPR** of the combined portfolio at that allocation.
2. The population **standard deviation of daily net HPRs** of the combined portfolio at that allocation.

Plotting every combination's (SD, average HPR) pair produces a scatter from which the empirical efficient frontier can be identified directly — the set of combinations offering the highest average HPR for a given SD (or lowest SD for a given average HPR), read straight off the scatter rather than solved for analytically.

**Relationship to the later machinery**: CPA is the direct empirical precursor to Ch.6's Lagrange-multiplier/Gauss-Jordan efficient frontier (§2.2 above) — the same underlying goal (maximize return for a given risk, or minimize risk for a given return, across a set of components) approached by exhaustive enumeration instead of constrained optimization. It requires no covariance-matrix algebra and no distributional assumptions, at the cost of being combinatorially expensive as the number of systems and the allocation-grid fineness grow (the same brute-force-vs-directed-search trade-off documented for Pardo's grid-search optimization method, `14_backtesting_and_validation.md` §5.1). For a small number of systems or a coarse allocation grid, CPA is a practical first-pass tool before committing to the full Lagrangian solve.

**Static vs. dynamic fractional f**: static = trade a constant fraction of full optimal f permanently (constant dispersion). **Dynamic fractional f ("split-equity" technique)**: split equity into active/inactive subaccounts; always use the FULL (undiluted) optimal f but apply it only to the active portion; the inactive dollar amount stays CONSTANT. Dynamic's effective fraction of optimal f rises toward 1 as equity→∞ and falls toward 0 as equity approaches the fixed inactive floor — "equivalent to a form of portfolio insurance." Dynamic asymptotically dominates static, but for SHORT horizons static can actually reach a goal faster — reallocating every trade/day degenerates dynamic into static exactly (Vince Ch.8).

**Four reallocation methods**: (1) **Investor Utility** — set initial active% equal to your max-drawdown tolerance (with the explicit warning that the initial active-equity fraction is NOT a hard cap on total possible loss, since active equity grows with the account); (2) **Scenario Planning** — apply Ch.4's scenario-planning machinery to active-equity % change per period; (3) **Share Averaging** — pull a fixed % of TOTAL equity from active to inactive each period, automatically taking profits from winners and automatically draining a losing program to zero over time (Eq 8.01: valid-period condition `FG^N ≤ G^N·FRAC + 1−FRAC`, where FG = the fractional-f geometric mean at the active FRAC being used, G = the full optimal-f geometric mean); (4) **Portfolio Insurance** — inherent in ANY dynamic fractional f strategy (the hedge ratio H = f·A/E, Eq 8.04a, is mathematically the delta of an implicitly replicated deep-out-of-the-money call / deep-in-the-money put on the portfolio) and can also be used as a standalone active reallocation technique (though Vince calls this "steering a tanker with a rowboat oar").

**Share-averaging termination-rate formulas (Vince Ch.8)**: the periodic pull-out % (P) needed so that active equity hits exactly zero after N periods of pure stagnation: `P = 1 − INACTIVE^(1/N)` (Eq 8.02), where INACTIVE = the inactive fraction of equity. Worked (80% inactive, target termination in 10 quarters): `P = 1−.8^.1 = .0220672315` → pull **2.20672315%** of total equity per quarter. The inverse — given a fixed periodic pull-out %, how many periods until termination under stagnation — is `N = ln(INACTIVE)/ln(1−P)` (Eq 8.03; round-trips to N=10 on the same inputs).

**The "buffer" demand-deposit account technique (Vince Ch.8)** — Vince's recommended fix for the fact that most traders/managers withdraw a CONSTANT DOLLAR amount for living expenses, which (he shows) is the worst possible withdrawal pattern (it withdraws a larger % when the account is smaller, exactly backward from optimal — the mirror image of share-averaging-out done wrong): withdraw a CONSTANT PERCENTAGE of total equity each period into a separate, simple demand-deposit "buffer" account (the buffer can literally BE the inactive subaccount); then withdraw a CONSTANT DOLLAR amount from THIS buffer (never directly from the trading account) to meet living expenses. **Sizing constraint**: the constant buffer withdrawal must be LESS than the SMALLEST expected transfer INTO the buffer. Worked: $500,000 account, 1%/month pull rate, 20% initial active (80% inactive) → smallest expected transfer = `.01×500,000×.8 = $4,000` → steady monthly withdrawal capped at ≤$4,000. This reconciles the mathematically superior dynamic-fractional-f growth path with a trader's need for smooth, steady cash flow — resolving what would otherwise be a direct conflict between optimal growth and psychological/practical smoothness needs (cross-ref `Psychology.md`'s living-expense-withdrawal critique).

**Blended portfolio f and the static/dynamic hedge-ratio pair (Vince Ch.8)**: the portfolio-wide blended f used in the hedge-ratio formulas is the portfolio-WEIGHTED sum of each component's own optimal f: `f = Σ[i=1,N] fi·Wi` (Eq 8.05, fi = component i's own optimal f in [0,1], Wi = its portfolio weighting from the identity-matrix solve). Under **dynamic** fractional f, hedge ratio `H = f·A/E` (Eq 8.04a, A = active funds, E = total equity — restated from above); under **static** fractional f, hedge ratio `H = f·FRAC` (Eq 8.04b, since A/E≡1 and f is instead scaled directly by the static FRAC used). Using portfolio insurance itself AS an active reallocation trigger (rather than merely the passive-consequence framing above) requires solving Eq 8.04a for the active-equity fraction that matches a target replicated-option delta D: `D/f = A/E` when D<f, otherwise A/E is capped at 1 (Eq 8.06) — Vince's explicit caveat: doing this implies near-constant reallocation, which degrades dynamic fractional f toward static-like behavior, so he concludes "trying to steer performance by way of portfolio insurance as a dynamic fractional f reallocation strategy probably isn't such a good idea," even though portfolio insurance is always PRESENT implicitly whenever dynamic fractional f is used at all.

**The margin constraint**: adding market systems with correlation <1 always improves the geometric mean in theory, but margin requirements impose a hard ceiling — a portfolio with weight-sum 3 is roughly 3× as margin-call-prone as trading a single market alone. **Formula (8.08)**: U = Σfᵢ$ / (Σmarginᵢ$ × N), capped at 1 — the maximum active-equity fraction avoiding an initial margin call. **Explicit trade-off**: "you are better off to trade 3 market systems at the full optimal f levels than to trade 300 market systems at dramatically reduced levels" — the practical optimal number of market systems, factoring in execution-mistake risk, is usually "but a handful" (Vince Ch.8).

**Rotating markets**: when a market is added/dropped from the active set, simply RE-SOLVE the unconstrained geometric-optimal portfolio over the current component set and adjust positions — "It is alright to have a constantly changing portfolio in terms of components," provided the inactive equity amount stays constant.

**The "Fallacy of Filters"**: if a filter genuinely reduces 1-unit drawdown, the post-filter optimal f will be HIGHER (f$ correspondingly lower) than the pre-filter optimal f. A trader who keeps applying the OLD pre-filter f after adding a filter is unknowingly trading at a fraction of the new true optimal f — the "improvement" is an accident of dilution, not genuine edge. If she correctly re-derives the post-filter optimal f, she faces the same impending large drawdowns optimal f always implies — "she seems to have defeated the purpose of her filter... this illustrates the fallacy of filters from a money-management standpoint" (Vince Ch.8).

---

## 3. Chan's capital allocation across strategies (Ch.06-07)

### 3.1 The Kelly formula as the central capital-allocation tool

Chan explicitly follows Thorp's (1997) exposition, adapted from a portfolio-of-securities framing to a portfolio-of-strategies framing ("the mathematics are almost identical") (Chan Ch.6). Objective: maximize long-term compounded growth rate g — which implicitly requires avoiding ruin, since ruin makes long-term wealth (and g) surely zero.

**Multi-strategy Kelly formula**: **F\* = C⁻¹M**, where C = covariance matrix of strategy returns, M = vector of mean one-period simple excess returns (Chan Ch.6). **Independent-strategies special case**: if strategies are statistically independent, C is diagonal and the formula reduces to fᵢ = mᵢ/sᵢ² per strategy.

**Assumption flagged as an approximation**: returns are assumed Gaussian with fixed mean/std dev — Chan explicitly warns this may be inaccurate, since real large losses occur far more often than Gaussian predicts (fat tails, "black swans," citing Taleb 2007).

**Worked multi-strategy example (OIH/RKH/RTH sector ETFs)**: M = [0.1396, 0.0294, −0.0073]ᵀ, F* = [1.2919, 1.1723, −1.4882]ᵀ — since RTH's mean excess return is negative, Kelly correctly recommends SHORTING it. Combined portfolio g(F*) = 15.29%, exceeding the max growth rate achievable by ANY single one of the three ETFs alone (OIH alone achieves only 12.78%) — **illustrating the diversification/allocation benefit of the multi-strategy Kelly framework** (Chan Ch.6).

### 3.2 Practical allocation discipline

- **Half-Kelly betting**: because of parameter-estimation uncertainty and non-Gaussian real returns, traders commonly halve Kelly-recommended leverage.
- **Retail leverage cap adjustment**: if Kelly's unrestricted total leverage (Σ|fᵢ|) exceeds a regulatory cap l (e.g., Reg T's 2 or 4), scale every fᵢ down by l/Σ|fᵢ| (caveat: ignores potential offsetting-position effects).
- **Continuous rebalancing requirement**: Kelly-optimal allocation must be continuously adjusted as equity changes — worked illustration shows a Kelly-sized SPY position must be SOLD INTO a 10% loss to stay Kelly-optimal, not held or averaged down. Practical cadence: update allocation at least once/day; recompute F* itself periodically using trailing mean/std — rule of thumb for ~1-day-holding strategies: a **6-month lookback**, chosen because it gradually reduces exposure to deteriorating strategies.
- **Worst-case-loss override**: because of fat tails, Chan recommends estimating the historical maximum one-period loss via backtest, dividing your personal max-tolerable one-period drawdown by that worst-case loss to get an implied maximum leverage, and using the SMALLER of (a) half-Kelly leverage and (b) this worst-historical-loss-derived maximum. **Worked S&P 500 example**: worst one-day loss ≈20.47% (Black Monday 1987); at a 20% max-tolerable one-day drawdown, implied max leverage ≈1 — even half-Kelly (1.26 in the chapter's SPY example) would NOT have been conservative enough to survive Black Monday (Chan Ch.6).

### 3.3 Financial contagion and the risk-reduction feedback loop

Chan's Kelly-driven position-reduction-after-loss discipline is explicitly linked to a systemic risk mechanism: **financial contagion**. Example cited: August 2007 "quant meltdown" (Khandani & Lo) — Goldman Sachs's Global Alpha fund fell 22.5% in one week; even Renaissance Technologies lost 8.7% in the first half of August 2007, despite few of the affected funds holding the mortgage-backed securities that were the ostensible root cause. **Mechanism**: a fund with a large loss sells liquid (possibly unrelated) stock positions to manage risk; this selling depresses those stocks; other funds holding similar positions suffer losses too, triggering further selling — converting a sector-specific shock into a broad sell-off. Because strict full-Kelly rebalancing implies large, frequent loss-realization trades, most traders prefer half-Kelly, which implies smaller risk-driven sell sizes (Chan Ch.6).

### 3.4 Risk categories beyond position risk (portfolio-level)

Chan ranks these in decreasing order of likelihood: (1) **model risk** (data-snooping/survivorship bias, increased competition, or genuine regime shift eliminating the edge — mitigated for competition/regime-shift by letting Kelly leverage automatically decay toward zero as trailing mean return decreases, rather than abruptly shutting the model down); (2) **software risk** (bugs causing ATS to diverge from the backtested model); (3) **physical/natural disaster risk** (Chan Ch.6).

### 3.5 Psychological preparedness as a portfolio-allocation discipline

Chan frames psychological discipline as inseparable from capital allocation: even fully automated quant traders will override their systems on abnormal-P&L days. Named biases: **status quo bias/endowment effect** (holding losers too long), **loss aversion** (exiting winners too early), **representativeness bias** (overweighting recent experience, prompting unwise post-hoc parameter changes that should instead be tested over a long backtest window), **despair** (pressure to shut down a model, or reckless doubling-down — both irrational; the Kelly-disciplined response is to gradually LOWER allocation), and **greed** (rapid leverage increases after a good run). **Chan's "one golden rule": keep portfolio size under control at all times.** Historical overleveraging failures cited: LTCM (2000), Amaranth Advisors (2006, a single trader's natural-gas calendar-spread position lost $6 billion, "comfortably wiping out the fund's equity"). Chan discloses two of his own overleveraging mistakes (a $100M addition to a 6-month-old strategy losing >$1M; a mean-reverting XLE/CL spread trade increased to ~$500K that reverted only after he exited at a near-six-figure loss) as explicit cautionary lessons (Chan Ch.6).

---

## 4. The Efficient Frontier — side-by-side treatments

### 4.1 Kaufman (Ch.23)

Every strategy/portfolio is described by AROR and ASTD. Rational-investor rule: given equal risk, prefer higher return; given equal return, prefer lower risk — "a rational investor will always choose the one that is higher and to the left" on a risk/return plot. **The efficient frontier is the curve of investments offering max return per given risk (or min risk per given return).** The **optimal point** is where AROR/ASTD is maximized — geometrically, where a line from the risk-free rate R on the vertical axis is tangent to the frontier. Explicit caveat: not all investors choose this tangent point — personal risk tolerance and absolute levels matter; full portfolio-selection treatment is deferred to Ch.24 (Kaufman Ch.23). Kaufman's Ch.24 later restates the efficient-frontier concept while (per its own internal citation, preserved as an inconsistency) attributing its introduction to "Chapter 22" rather than Ch.23 — flagged in the source extraction as an apparent citation error.

### 4.2 Vince (Ch.6-7)

Vince derives the SAME classical Markowitz E-V efficient frontier from first principles via Lagrange multipliers and Gauss-Jordan matrix solving (Ch.6, full worked 4-asset numeric example), then in Ch.7 explicitly distinguishes:
- The **AHPR-based (arithmetic) efficient frontier and its Capital Market Line**, whose tangent point maximizes the Sharpe ratio (Eq 7.01a) — this is the CLASSICAL, textbook Markowitz/tangent-portfolio result.
- The **GHPR-based (geometric) efficient frontier**, obtained by converting each AHPR/V point via GHPR=(AHPR²−V)^(1/2) — the portfolio Vince argues actually matters for a reinvesting trader, since arithmetic averages overstate real compounded growth.
- The **unconstrained efficient frontier** (via the NIC device), which for any level of E is literally the SAME portfolio at different leverage, and on which "you cannot put a CML line" since CML lines are only meaningful on constrained (ΣXᵢ=1) frontiers.

**Vince's explicit critique of the traditional/Kaufman-style efficient frontier**: "The current generally accepted procedure for determining the efficient frontier will not really yield the efficient frontier, much less the portfolio that is geometric optimal... This can be derived only by incorporating the optimal f. Further, the generally accepted procedure yields a portfolio that gets traded on a static f basis rather than on a dynamic basis, the latter being asymptotically infinitely more powerful" (Vince Ch.8, restating Ch.7's core argument).

### 4.3 Agreement and disagreement between the two treatments

**Where they agree**: both use AROR/return and ASTD/variance as the two axes; both define the frontier as return-maximizing-per-risk; both explicitly flag that variance-based risk measures don't capture tail/catastrophic risk or higher moments (Kaufman's VaR-supplementation recommendation and Vince's explicit citation of Markowitz's own caveat about E-V theory's limits are functionally the same point, independently stated).

**Where they diverge**: Kaufman's treatment (Ch.23-24) stops at the classical tangent-portfolio/Solver-style optimization and layers GASP (a genetic-algorithm alternative optimizer) on top for active-trading return streams — Kaufman never distinguishes an "arithmetic" vs. "geometric" efficient frontier as separate objects, and does not address the weighting-vs-quantity distinction. Vince's treatment (Ch.6-8) explicitly argues the classical constrained/arithmetic frontier is NOT the frontier that matters for a compounding trader, constructs the geometric and unconstrained frontiers as objects distinct from the classical one, and derives a formal (if approximate) leverage multiplier (q, Eq 7.13) connecting the classical tangent portfolio to his own geometric-optimal portfolio. Kaufman's book does not engage with this arithmetic/geometric distinction at all — the two books' efficient-frontier concepts are compatible (same underlying MPT machinery) but Vince's is a strict superset in ambition, explicitly built to correct what Vince considers a flaw in how the classical frontier (i.e., Kaufman's version) is normally applied in practice.

---

## 5. Correlation constraints — cross-book comparison

**Kaufman (Ch.24)**: correlation used mainly as a *risk-flagging* input — market-group classification by liquidity/covariance for asset selection (§1.3 above), and an explicit warning that correlation statistics are least reliable exactly when most needed (they go to extremes during price shocks, which historic/rolling averages systematically understate). No formal correlation-adjustment procedure is given beyond the general "use uncorrelated strategies" principle and GASP's raw pairwise-correlation inputs to its risk/liquidity constraints.

**Vince (Ch.6)**: correlation enters directly as a matrix input (COVᵢⱼ = ρᵢⱼ·σᵢ·σⱼ) to the Lagrangian optimization; sign-flip rule for shorted legs (multiply the correlation by −1 per shorted leg; double-short pairs cancel back to the original sign).

**Vince (Ch.7)**: flags a **detrending artifact** — two positive-expectation systems show spurious positive correlation purely from shared equity-curve uptrend; recommends detrending via regression residuals, but only for *daily equity changes*, never raw prices, and warns detrending itself can produce spuriously HIGH correlation for infrequently-trading systems.

**Vince (Ch.8)**: gives the most operationally concrete correlation-constraint guidance in either book — an explicit, directional bias-correction rule for correlation estimation under sparse/infrequent co-occurrence data: **"don't be afraid to edit the correlation coefficients UPWARD. However, be wary of moving them LOWER"** — because underestimating correlation pushes the optimizer to increase position sizes, moving the portfolio to the (costlier) RIGHT of the true f-curve peak, whereas overestimating correlation only moves it to the (safer) LEFT. This is presented as a direct application of Vince's broader Type-I/Type-II error asymmetry (erring conservative is cheaper than erring aggressive) to the specific case of correlation-matrix estimation for rotating/infrequently-co-occurring markets (e.g., gold and silver that have never historically traded simultaneously may show ≈0 measured correlation despite a true strongly-positive relationship).

**Chan (Ch.6)**: correlation enters through the full covariance matrix C in the multi-strategy Kelly formula F*=C⁻¹M — the worked OIH/RKH/RTH example shows the covariance structure directly driving a short recommendation on the negative-mean-return leg. Chan does not discuss correlation-estimation bias-direction (unlike Vince) but does flag the broader Gaussian-assumption risk (fat tails) that indirectly bears on correlation estimates during stress periods (echoing Kaufman's "correlations go to extremes during shocks" point, though Chan frames it via the Gaussian/fat-tail lens rather than a rolling-correlation lens).

**Cross-book agreement**: all three books agree correlation estimates are least trustworthy during the stress periods when they matter most (Kaufman's rolling-correlation shock example, Vince's sparse-co-occurrence example, Chan's fat-tail/Gaussian-assumption critique) — this is a point of genuine convergence across independently-derived frameworks, not merely restated from a shared source.

---

## 6. Strategy-portfolio thinking / multiple uncorrelated edges

**Kaufman (Ch.24)**: explicitly ranks multi-strategy diversification ABOVE multi-market diversification for stress-period robustness: "under stress, markets correlate more, so varied *strategies* diversify better than varied markets alone during uncertainty." The six named less-correlated strategy families (trend, countertrend/mean-reversion, spreading, fundamental, carry, patterns) are presented as the basic building blocks of strategy-level diversification (§1.3 above), with the explicit warning that superficially-different techniques within the SAME family (e.g., three different trend-following systems) are not genuinely diversifying, since "if all trend-following systems are profitable, then they must extract those profits from the same price moves and hold the same position at some time" (Kaufman Ch.24).

**Vince (implicit, via Ch.5-8)**: does not name "strategy families" the way Kaufman does, but the entire Ch.5-8 machinery treats "market systems" (which may be different strategies on the same or different underlyings) symmetrically with "assets" — the correlation-matrix/optimal-f framework applies identically whether the correlated positions are different instruments or different strategies on the same instrument. Vince's diminishing-returns/efficiency-loss finding (Ch.1-2, restated in Concepts.md) — that there is an optimal, FINITE number of market systems to combine, with marginally decreasing diversification benefit and marginally increasing simultaneous-betting efficiency loss as more systems are added — is the closest Vince analogue to Kaufman's "too much diversification" point (§1.7 above), independently derived from the opposite (parametric optimal-f) direction.

**Chan (Ch.6-7)**: the multi-strategy Kelly framework (F*=C⁻¹M) IS Chan's formal treatment of "multiple uncorrelated edges" — the OIH/RKH/RTH worked example is presented specifically to demonstrate that a correctly-allocated multi-strategy portfolio's compounded growth rate (15.29%) exceeds the maximum achievable by ANY single constituent strategy alone (12.78% for the best individual ETF), which Chan states illustrates "the diversification/allocation benefit of the multi-strategy Kelly framework" (Chan Ch.6). Chan's Ch.7 "high-frequency → high Sharpe" argument (via the law of large numbers: more independent bets → smaller % deviation from mean return → higher Sharpe → more permissible leverage → higher compounded growth) is a related but distinct point about *time-diversification within a single strategy* rather than cross-strategy diversification, though Chan explicitly ties it back to the same underlying Sharpe-ratio-drives-growth logic from Ch.6 (g = r + S²/2).

---

## 7. Market selection for portfolios (Kaufman Ch.23)

Kaufman's Ch.23 "Selecting the Best Markets" section (confirmed present in Ch.23, not Ch.24) gives five candidate ranking measurements for choosing which markets to include in a portfolio, each computable over 5/10/20/40-day windows: (1) correlation coefficient (only above a 0.25 threshold considered meaningful); (2) sum of net dollar moves over n days; (3) slope of an n-day dollar-terms regression; (4) Wilder's ADX (only above 0.20 threshold); (5) average absolute price change (caveat: conflates profit potential with risk for trend systems, needs smoothness analysis before blind use) (Kaufman Ch.23).

### 7.1 Commodity Selection Index (CSI) — J. Welles Wilder

Confirmed present in Kaufman Ch.23 (not Ch.24, as the task brief anticipated it might be misfiled — it is correctly in the Risk Control chapter's "Selecting the Best Markets" section). Full Directional Movement → ADX → CSI derivation chain:

- **Directional Movement**: PDM = today's high − yesterday's high; MDM = yesterday's low − today's low; DM = whichever of PDM/MDM is larger (other set to zero; both zero on an inside day). TR1 = today's true range.
- **DM14/TR14 smoothing**: Wilder-style running-total "average-off" smoothing, smoothing constant **0.133** (≈1/7.5, Wilder's standard 14-day approximation) — exact recursive notation is an embedded-graphic extraction gap.
- **Directional Indicators**: PDI14 = 100×(PDM14/TR14); MDI14 = 100×(MDM14/TR14) (reconstructed standard Wilder form).
- **DX**: DX = 100×|PDI14−MDI14|/(PDI14+MDI14) (reconstructed).
- **ADX**: DX smoothed with the same 0.133 constant.
- **ADXR**: ADXR = (ADX_today + ADX_14-days-ago)/2 — reduces ADX's extreme variance.
- **CSI formula**: CSI = [ADXR × ATR14 × K] / (Margin × Commission) (reconstructed shape; K = big-point-value conversion factor, or 1 for equities with "Margin" becoming the equity investment amount). Since the bracketed term is constant for a given market, K can be precomputed once, letting CSI be efficiently recalculated for a whole portfolio-ranking/allocation process — **select or weight-allocate positions by highest CSI** (Kaufman Ch.23).

**Related named system using the same DM/ADX machinery**: Colby's 2-Day System (long entry: 2-day PDI > 2-day MDI OR 2-day ADX > its own 2-day smoothing; mirrored for shorts; all orders on the close) — backtested on the DJIA 1928-2000, a $100 investment compounding to $9,988, beating buy-and-hold over the period, with no further risk/sizing rules given in the source (Kaufman Ch.23, cited to Robert Colby).

### 7.2 Efficiency Ratio market-selection framework — Kaufman's Strategy Selection Indicator

Confirmed present in Kaufman Ch.23 (Kaufman's own named "Strategy Selection Indicator" section). Restates the Efficiency Ratio (ER) from Ch.1/Ch.17: **ER = |net price change| / Σ(|individual price changes|)** over the same window, using closing prices. ER → noise increases as ER → 0; ER is explicitly NOT the same as volatility.

**Market-maturity link**: ranking equity markets' noise level indicates market maturity — emerging markets tend to show LESS noise/more trend (fewer participants with more uniform directional views, or illiquidity amplifying one-directional moves); "equity index markets could be a special case" (Kaufman Ch.23).

**Empirical scatter test**: 80-day MA trend-system profit factor vs. 10-day ER, 30 world futures markets, 1998–July 2018 (6 interest rate, 13 equity index, 3 currency, 6 metals, 4 energy, 4 agricultural). **Findings**: Eurodollars and Short Sterling (shortest-maturity rates, most policy-driven) sit at the high-ER/high-trend extreme; FTSE, EuroStoxx, and especially Russell 2000 sit at the low-ER/noisy extreme among equity index markets. **Conclusion**: ER is "a valuable tool for selecting the right market for a specific strategy," though exact scatter positions shift with different trend-speed/ER-period choices while the qualitative pattern (short-maturity rates trendiest, active equity indices noisiest) is described as robust (Kaufman Ch.23).

### 7.3 Ranking Trends Using Prices — Chande's Trend Strength (a related, Kaufman-critiqued measure)

Also in Ch.23: St = (net return over n days) / f(σ), cited to Chande (1997), structurally similar to the noise/ER concept. **Explicit flagged caveat**: when applied to stocks using a natural-log transform, the formula implicitly assumes volatility increases with price — which Kaufman states is "not correct," per the volatility-scale discussion in Ch.22. This is Kaufman's own critique of a published method he otherwise catalogs, not an endorsed Kaufman technique (Kaufman Ch.23).

### 7.4 No portfolio-market-selection content found in Vince or Chan

Neither Vince nor Chan's assigned chapters contain a market-selection-for-portfolio-inclusion framework comparable to Kaufman's CSI/ER treatment — Vince's Ch.5-8 machinery takes the candidate asset/strategy universe as given and optimizes weights across it, and Chan's Ch.6-7 likewise assumes the strategy set is already chosen (Chan's cointegration-screening in Ch.7 is a PAIR-selection tool for a single stat-arb strategy, not a portfolio-level market-selection ranking).

---

## 8. Pardo's Portfolio-Risk Tier (Pardo Ch.5)

Pardo's own portfolio-construction content is thin (the book's real subject is single-strategy testing/optimization methodology), but he does define the top tier of his three-level risk taxonomy (trade/strategy/portfolio risk — full taxonomy in `11_risk_management.md` §1) directly at the portfolio level:

- **Portfolio risk (definition)**: "the possibility of financial loss at the portfolio level (potentially multistrategy, multiple time frame, and multimarket) from the sum total of all trading therein" (Pardo Ch.5).
- **Portfolio maximum drawdown (definition)**: "the largest drop in portfolio equity measured from the portfolio equity high to a succeeding portfolio equity low" (Pardo Ch.5) — the direct portfolio-level analog of single-strategy MDD (`11_risk_management.md` §3.2).
- **Claimed diversification benefit, explicit**: portfolio MDD is claimed to be statistically more reliable (less variable across samples) than single-strategy MDD as diversification rises (uncorrelated strategies/markets/time-frames combined) — and this greater reliability is said by Pardo to justify **higher leverage with more confidence at the portfolio level** than would be prudent for any single component strategy alone (Pardo Ch.5). This is a qualitative claim, not accompanied by a worked formula or numeric example in the extracted material, and is directionally consistent with (though independently stated from) Kaufman's §1.1-1.2 diversification-reduces-risk framing and Vince's Ch.6-8 portfolio-optimal-f machinery above.

---

## Summary Table — Where Each Book Sits in the Portfolio-Construction Pipeline

| Stage | Kaufman | Vince | Chan |
|---|---|---|---|
| Market/strategy selection | CSI, Efficiency Ratio (Ch.23) | Not addressed (Ch.5-8 assumes given universe) | Cointegration screening (pair-level, Ch.7) |
| Diversification rationale | 3-step framework, strategy > market diversification (Ch.24) | Diminishing-returns/efficiency-loss finding (Ch.1-2, restated Ch.7) | Multi-strategy Kelly beats best single strategy (Ch.6) |
| Weighting/allocation method | Excel Solver (classic MPT) or GASP (genetic algorithm) (Ch.24) | Lagrange-multiplier E-V matrix solve, arithmetic + geometric + unconstrained frontiers (Ch.6-7) | Kelly formula F*=C⁻¹M (Ch.6) |
| Correlation handling | Risk-flagging input; "goes to extremes in shocks" (Ch.23-24) | Full covariance-matrix input; detrending caveat; edit-upward-not-downward rule (Ch.6-8) | Covariance matrix C in Kelly formula; Gaussian-assumption caveat (Ch.6) |
| Position-sizing linkage | Volatility parity / ATR sizing (Ch.23), Volatility Stabilization (Ch.24) | Optimal f divided by portfolio weighting = adjusted f (Ch.7) | Continuous Kelly rebalancing, half-Kelly (Ch.6) |
| Rebalancing/reallocation | Volatility Factor threshold rebalancing (20% band, Ch.24); Turtles' de-leveraging rule | 4 reallocation methods: Investor Utility, Scenario Planning, Share Averaging, Portfolio Insurance (Ch.8) | Daily/6-month-lookback Kelly recompute; worst-case-loss override (Ch.6) |
| Regulatory/practical caps | UCITS 2.5×/20% caps (Ch.24) | Margin-constraint formula (Eq 8.08, Ch.8) | Reg T leverage cap rescaling (Ch.6) |

---

## Notable Gaps and Extraction Weaknesses

- **GASP**: fully documented in the source (all 6 GA steps, worked 19-strategy case study) — not thin. The one genuine gap is the exact combining notation for several embedded-graphic formulas (portfolio-return SUMPRODUCT symbolic form, exposure-capping ratio) — preserved as flagged reconstructions, not invented.
- **CSI / Efficiency-Ratio-for-selection**: both are fully present in Kaufman Ch.23 (not thin at all) — the CSI's exact DM14/TR14 recursive smoothing notation and the final CSI bracket-arithmetic are embedded-graphic gaps, reconstructed from the standard published Wilder ADX formula and flagged as such in the source extraction; the qualitative selection logic (rank/weight by highest CSI or by ER against a strategy-type threshold) is completely intact.
- **Vince Ch.5**: mostly options-pricing/options-optimal-f content with only indirect portfolio relevance (the causal/random relationship taxonomy and directional-applicability rules) — thinner on direct "portfolio construction" content than Ch.6-7, as expected given its chapter title.
- **Kaufman's internal chapter-citation inconsistencies** ("Chapter 21" vs. "Chapter 23" for risk measures; "Chapter 22" vs. "Chapter 23" for the efficient frontier's introduction) are preserved verbatim per the source extraction's own flagging, not silently resolved.
- **Vince's Eq 7.13 (optimal leverage multiplier q)** is explicitly flagged by Vince himself as "a very close approximation," not exact — preserved as such.
- No cryptocurrency-specific portfolio-construction content was found in any of the three books' assigned chapters (confirmed via the source extractions' own full-text search notes for Kaufman Ch.23-24); all worked examples use equities, futures, ETFs, or options on traditional underlyings.
