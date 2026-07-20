# Position Sizing and Money Management

This file is the complete position-sizing / money-management corpus assembled from five source extractions: Ralph Vince's *The Mathematics of Money Management* (the dominant source — this is literally what the book is about), Ernest Chan's *Quantitative Trading* (Kelly criterion, half-Kelly, fat-tail leverage caps), Perry Kaufman's *Trading Systems and Methods* (Kelly, volatility-parity, ATR sizing, stock sizing, VIX sizing, gambling-technique/Martingale warnings), Yves Hilpisch's *Python for Algorithmic Trading* (Kelly in code, leverage/margin mechanics), and Robert Pardo's *The Evaluation and Optimization of Trading Strategies* (position sizing as part of strategy-level risk control). Every claim below is tagged with its source book and chapter. Where a source extraction explicitly flags a formula as "not recoverable" or "reconstructed," that flag is preserved verbatim rather than silently repaired.

Sibling files: detailed stop-loss/exit technique taxonomy lives in `09_exits.md`; risk-of-ruin mathematics (classical gambler's-ruin formulas, Vince's parametric risk-of-ruin=1 argument, Kaufman's Vince-modified spreadsheet risk-of-ruin) lives in `11_risk_management.md`; portfolio-level optimal f, the geometric-optimal portfolio, and multi-asset Kelly/covariance allocation live in `12_portfolio_construction.md`. This file focuses on **single-position/single-system** sizing methodology.

---

## 1. Optimal f (Vince)

Optimal f is the organizing concept of Vince's entire book (Chapters 1-8). It answers "how many units/contracts/shares should I trade," which Vince argues is at least as important a decision as direction: "whether you are right or wrong on the direction of the market when you enter a trade does not dominate whether or not you have the right quantity on" (Vince Ch.1).

### 1.1 Definition and core mechanics

**f** is a number between 0 and 1: the divisor of the trader's perceived biggest loss. It is explicitly **not** "the percentage of the account to bet" — that is a common misconception Vince corrects directly (Vince Ch.1). The actual sizing chain is:

```
Dollar amount to finance 1 unit = Biggest Loss / -f
Number of units to trade = Account Equity / (Biggest Loss/-f)
```

Worked example (Vince Ch.1): $50,000 account, worst-case expected loss $5,000/contract, holding 5 contracts → `50,000/(5,000/f) = 5 → f = .5`. With 1 contract instead, f = .1.

Fractional contract counts are always **floored** (rounded down) — "the price extracted for being slightly below optimal is less than the price for being slightly beyond it" (Vince Ch.1). Margin requirements are explicitly **irrelevant** to the mathematically correct contract count — P&L per contract doesn't depend on margin size, and margin is "further made meaningless" because loss is not capped at the margin amount (Vince Ch.1). In practice, real-life capital-per-contract = the greater of (a) initial margin requirement and (b) the dollar amount dictated by optimal f (Vince Ch.1).

### 1.2 HPR and TWR machinery

The entire framework is built on the **Holding Period Return (HPR)**: 1 plus the fractional gain/loss on a trade. Vince's definition is explicitly non-standard — most texts omit the "+1"; in this book HPR always includes it (Vince, `Concepts.md`).

**General empirical optimal-f formulas** (Vince Ch.1):
```
HPR = 1 + f*(-Trade/Biggest Loss)                          (1.11)
TWR = Π[i=1,N] (1+f*(-Tradei/Biggest Loss))                (1.12)   [Terminal Wealth Relative]
G = TWR^(1/N)                                               (1.13)  [Geometric Mean]
```
where -Trade = that trade's P&L with sign reversed (losses become positive numbers), Biggest Loss = the single most negative P&L in the sample (always negative), N = number of trades.

Also foundational:
```
TWR = Π[i=1,N] HPRi                       (1.04)
Geometric Mean = TWR^(1/N)                (1.05)
TWR = Final Stake / Starting Stake        (1.06)
G = (Final Stake/Starting Stake)^(1/N)    (1.07)
```

**Why reinvestment (compounding) is the right frame, and why the geometric mean — not win rate, average trade, risk/reward, or lowest drawdown — is the correct criterion for judging a system under reinvestment (Vince Ch.1)**:

*Reinvestment can turn a "winning" system into a loser (but never the reverse)*. Two contrived 2-trade systems, each netting +10% on a non-reinvested basis: **System A** (+50%, -40%) reinvested ends at 90 (start 100) — a **-10%** result, despite being "profitable" non-reinvested. **System B** (+15%, -5%, same +10% non-reinvested) reinvested ends at 109.25 (+9.25%) — still profitable. Trade order doesn't affect the final cumulative result either way. Vince's own statement: **"reinvesting trading profits can turn a winning system into a losing system but not vice versa!"** — a system becomes a loser under reinvestment specifically when its returns carry too much dispersion relative to their average. Vince argues reinvestment is nonetheless the correct real-world frame, since real trading compounds rather than replenishing losses with fresh cash: "it is compounding that takes the linear function of account growth and makes it a geometric function."

*Worked demonstration that naive metrics pick the wrong system*: extending Systems A and B to 4 trades (System A: +50,-40,+1,+1; System B: +15,-5,-1,-1) and adding comparison **System C**, a "perfectly consistent" bank account (+1,+1,+1,+1 every trade) — System A has the highest win rate is false (C wins 100% of trades, A only 75%) and the highest average trade (3 vs. B's 2 vs. C's 1) and best risk/reward, yet:

| System | TWR (N=4) | Geometric Mean |
|---|---|---|
| A | .91809 | 0.978861 |
| B | 1.070759 | 1.017238 |
| C | 1.040604 | 1.009999 |

**System B — last on every naive metric (lowest win rate, lowest average trade, no #1 ranking on any single criterion) — has the highest geometric mean and is therefore the best system for reinvestment.** None of win %, total dollars, average trade, consistency (avg-trade/SD), risk/reward, or drawdown correctly identifies this; only the geometric mean captures the right combination of profitability and consistency. A geometric mean below 1 (System A) means the system loses money under reinvestment even though it is nominally profitable non-reinvested.

*How aggressively to reinvest*: 100% reinvestment of the entire stake on every single bet is reckless even in a favorable game — worked example: $1 stake, 50/50 coin toss paying $2 win/-$1 loss (ME=$.50/toss), betting the entire stake each time: win first toss (stake→$3), lose second toss → **wiped out completely**. Flat/constant $1 bets on the same sequence instead net +$1 (stake→$2). "Somewhere between these two scenarios lies the optimal betting approach for a positive expectation" — the fixed-fraction search this section develops. For a **negative-expectation** game, the best bet is no bet at all; if forced to bet, "maximum boldness" applies — bet on as FEW trials as possible (the opposite of the positive-expectation case), since more trials only increase the certainty that the negative edge will be realized (example: 49% win $1/51% lose $1 → best to bet on only 1 trial; probability of eventual loss → certainty as trials→∞). For a **positive-expectation** game with unknown win/loss sequencing, always betting an identical FIXED FRACTION of total stake is, long-run, the best staking system — the technique the rest of this section formalizes.

**Search procedure**: loop f from .01 to 1.0 in increments of .01 (or use a faster search such as **parabolic interpolation** — referenced repeatedly by Vince across Chapters 1, 3, 4, and 5 as "one of the fastest ways" to find optimal f, but its actual mechanics are **never given in this book**; readers are referred to Vince's predecessor book *Portfolio Management Formulas*, which the extraction does not have access to — this is a genuine, acknowledged gap in the source). The TWR/geometric-mean curve is smooth and single-peaked, so the f producing the highest TWR is optimal — both TWR and geometric mean peak at the same f (Vince Ch.1).

TWR is a **product**, not a sum. This multiplicative structure means an HPR of exactly 0 (a 100% loss on one trade) wipes the account out completely regardless of any other trade's outcome — "in trading you are only as smart as your dumbest mistake" (Vince Ch.1).

### 1.3 Worked numeric examples (why quantity dominates direction)

**50/50 game, win $2/lose $1** (Vince Ch.1, Figure 1-1): optimal f = .25, giving TWR = 10.55 after 40 bets (955% profit). At f=.1 or f=.4 (each only 15% away from optimal), TWR = 4.66 — less than half the optimal result despite the small deviation. **At f=.5 in this specific game you exactly break even; beyond f=.5 you are a guaranteed long-run loser despite a positive-expectation game.**

**50/50 game, win $5/lose $1** (Vince Ch.1, Figure 1-6): optimal f = .4. After 20 sequences of +5,-1 (40 bets) from a $2.50 stake: ending stake = $127,482. At f=.6 or f=.2 (each 20% off), profit is "not even a tenth" of the optimal result. Mathematical expectation of this game = 2 (strongly positive), yet **betting with f > .8 loses money outright** — expectation alone says nothing about correct bet size, and overbetting can turn even a strongly favorable game into a loser.

**Kelly-with-averages vs. true optimal f** (Vince Ch.1): sequence +9,+18,+7,+1,+10,-5,-3,-17,-7 (9 trades, 5 profitable). Naively averaging win/loss sizes into the Kelly ratio formula gives f≈.16 (explicitly identified as **"a mistake that traders commonly make"** — "here is where so many traders go wrong," because trade P&L is not Bernoulli-distributed). The true optimal f (found via the TWR-search method) is **.24**. Repeating the 9-trade sequence out to 999 trades: TWR at f=.24 = 25,451.045 vs. TWR at f=.16 = 8,563.302 — **f=.24 outperforms by 297%** despite the two f-values differing by only .08. "You must give the program time... and not expect miracles in the short run" (Vince Ch.1).

**Dispersion, not raw expectation, drives compounded growth — 28:1 vs. 1:1 payoff comparison** (Vince Ch.1): System A wins 10% of the time at 28:1 payoff, System B wins 70% of the time at 1:1 payoff. Mathematical expectation: ME(A)=1.9/unit bet vs. ME(B)=.4/unit bet — A's raw per-bet expectation is **4.75x** B's. Yet at each system's own optimal f (found by dividing ME by the win\loss ratio: f(A)=.0678, f(B)=.4), the geometric means are G(A)=1.044176755 (4.4177%/bet) vs. G(B)=1.0857629 (8.57629%/bet) — **System B, despite less than 1/4 the raw expectation, compounds almost twice as fast as System A.** Recovery-from-a-50%-drawdown comparison confirms the practical consequence: solving `1.044177^X=2.0` gives X≈16.5 trades for A vs. `1.0857629^X=2.0` giving X≈9 trades for B — B recovers roughly twice as fast. This directly corrects the common misconception that growth (TWR) equals `(1+R)^N` for a *constant* per-period return R (Eqs 1.17/1.18) — that shortcut is only valid if HPR never varies, which it never does in real trading; true growth is always the multiplicative product of the actually-varying HPRs.

### 1.4 Drawdown implications — why trading above or below optimal f is costly

**Core stated fact (Vince Ch.1, repeated in `Risk_Management.md` and `Concepts.md`)**: "the drawdown you can expect with fixed fractional trading, as a percentage retracement of your account equity, historically would have been at least as much as f percent." If f=.55, historical drawdown is guaranteed to be ≥55% of equity the instant the biggest historical loss recurs while trading at optimal f.

**The central paradox, stated directly**: "optimal f allows you to experience the greatest geometric growth, [but] it also gives you enough rope to hang yourself with." Vince's own analogy: **"Optimal f is like plutonium. It gives you a tremendous amount of power, yet it is dreadfully dangerous."** The better a system (the higher its optimal f), the higher its historical minimum drawdown will be (Vince Ch.1).

**Empirical claim (Vince's own stated experience, not formally derived)**: "you will have enormous difficulty finding a portfolio with at least 5 years of historical data... with any less than a 30% drawdown in terms of equity retracement" when every component is traded at true optimal f — "expect to be nailed for 30% to 95% equity retracements," requiring "enormous discipline" that "very few people can emotionally handle" (Vince Ch.1).

**Time-in-drawdown finding (Vince Ch.2, via the arc sine laws)**: at optimal f, the longest drawdown (elapsed trades between one equity peak and the point it is re-exceeded — distinct from the *deepest* drawdown) typically consumes **35% to 55% of the total elapsed time/trades** of a program, "no matter how long or short a time period you are looking at." This finding is explicitly time-invariant and holds for single systems or full portfolios traded at full or dynamic-fractional f.

**Why trading above optimal f is mathematically fatal, not just riskier**: this is not a matter of degree. Vince demonstrates (2:1 coin toss example, Ch.1) that at f=.5 you exactly break even despite positive expectation, and beyond f=.5 you are a *guaranteed long-run loser*. The mechanism is the Pythagorean-like **Fundamental Equation of Trading** (§1.5 below): geometric mean growth is a peaked function of bet size, not monotonic in risk. Overbetting doesn't just add variance — it can drive the geometric mean below 1, guaranteeing eventual ruin regardless of positive arithmetic expectation.

**Diluting below optimal f (static fractional f, e.g. trading f/2)**: drawdown reduces only **arithmetically**, while returns are reduced **geometrically** — an asymmetric, unfavorable trade-off. Vince's own rhetorical challenge: "why commit funds to futures trading that aren't necessary simply to flatten out the equity curve at the expense of your bottom-line profits? You can diversify cheaply somewhere else" (Vince Ch.1). Quantified in Ch.2: at full f (geometric mean 1.06066) doubling the stake takes ~11.77 trades; at half f (geometric mean 1.04582499) it takes ~15.47 trades — 31.44% longer. Over 100 trades, full f reaches 361.09x vs. half f's 88.29x. Vince's own conclusion: "anyone who claims that the only thing you sacrifice with trading at a fractional versus full f is time required to reach a specific goal is completely correct. Yet time is what it's all about" (Vince Ch.2).

### 1.5 The Fundamental Equation of Trading (geometric mean maximization vs. risk of ruin)

This is Vince's master lens for evaluating *any* change to sizing, stops, or system rules (Vince Ch.1, preserved with equation numbers):

```
G^2 = A^2 - V           (1.23)
G^2 = A^2 - SD^2        (1.24)
A^2 - G^2 - SD^2 = 0    (1.25)
G^2 = A^2 - SD^2        (1.26)
SD^2 = A^2 - G^2        (1.27)
A^2 = G^2 + SD^2        (1.28)
```
where A = arithmetic mean HPR, G = geometric mean HPR, SD = standard deviation of HPRs (V = SD²). Equation (1.28) is recognized as **the Pythagorean Theorem** — A is the hypotenuse, G and SD the two legs. When SD=0, A=G exactly.

**Formula (1.19c), explicitly named "The Fundamental Equation of Trading":**
```
Estimated TWR = (A^2 - SD^2)^(N/2)
```

**Key implications (IF/THEN, Vince Ch.1):**
- IF A ≤ 1 (non-positive expectation), THEN regardless of SD and N, TWR can never exceed 1, and as N→∞, TWR→0 — a non-positive-expectation system goes broke with certainty given enough trades, **no matter its variance**. This is the formal statement of why more risk is not monotonically more reward and why overbetting is fatal: pushing f beyond the optimum effectively degrades A relative to SD until this same asymptotic failure mode is reached.
- IF A > 1, THEN increasing N increases total profit; diversification's real benefit (per this equation) is letting you accumulate more N in the same calendar time.
- Reducing SD by more than you reduce A is beneficial (formalizes "cut losses short") — but only up to the point where tightening stops starts excluding trades that would have turned profitable (which reduces A faster than SD, an explicit stated limit).

**Worked demonstration — options overlay (Vince Ch.1)**: an OEX 20-day channel breakout system (7 trades, 1987) has geometric mean 1.12445 at optimal f trading the underlying. Converting the identical trade signals to theoretical option prices (via Black-Scholes) yields geometric mean **1.2166** — "an enormous difference." Raised to the 6th power: underlying TWR = 2.02 (+102%) vs. options TWR = 3.24 (+224%). Vince's own caveat: this is "an extreme case," and trading long options outright "may not always be superior to being long the underlying instrument" — it illustrates the fundamental equation as an evaluation lens, not a blanket recommendation.

### 1.6 "Not recoverable" / reconstructed formula flags (preserved verbatim)

The extraction of Vince's book is unusually clean and complete (per its own `Progress_Log.md`, the entire book was read sequentially with no skipped sections), but a small number of items are explicitly flagged as gaps by the extractor rather than reconstructed:
- The **parabolic interpolation search algorithm** (referenced Ch.1, 3, 4, 5 as a faster alternative to brute-force f search) is never actually given in the book — deferred to *Portfolio Management Formulas*, not available to this extraction.
- **Classical closed-form risk-of-ruin equations** are discussed conceptually (Ch.2 footnote, Ch.5) but never derived in the main text — see `11_risk_management.md`.
- Minor internal numerical inconsistencies in Vince's own worked examples are preserved as-is per extraction policy (not corrected): a Chapter 5 probability table summing to 1.30 instead of 1.00; a Chapter 8 margin-constraint example showing a $2,000 vs. $4,800/$4,600 discrepancy; the Bernoulli variance formula in Appendix B printed as `Q=P-1` (conventionally `Q=1-P`); Appendix C's phase-length formula with an ambiguous exponent ("D^2*3*D+1", most likely `D^2+3*D+1`).

### 1.7 Parametric Optimal f on the Normal Distribution (Vince Ch.3)

**Why this exists**: Kelly (§2.2 below) is itself a *parametric* technique — it derives optimal f from just two numbers (win probability, payoff ratio) — but is valid only for Bernoulli (2-outcome) processes. Vince Ch.3 generalizes the same idea to a full continuous outcome distribution (the Normal), needing only two estimated parameters: mean and SD of trade P&L. Unlike the empirical method (§1.1-1.6), this works even with **no trade history at all** — a discretionary trader can simply *estimate* the two parameters.

**Four stated advantages of parametric over empirical techniques (Vince Ch.3, explicit numbered list — this is why Chapters 3-5 exist at all)**:
1. **Inherently more accurate when the true distribution is known** — not diluted by finite-sample noise. **Worked illustrative example**: a coin known (long-run) to land heads 60% of the time, 1:1 payoff. Kelly (parametric) says bet f=.2. An *empirical* calculation from the last 20 tosses (11 heads, 9 tails = 55%) gives f=.1 — **half** the correct value, despite the sample being only 5 points off the true rate. The parametric answer (.2) is correct, the empirical answer (.1) is wrong. Critical proviso: this requires knowing the true long-run distribution — "the biggest drawback to using the parametric techniques."
2. **Doesn't require an extensive trade-history sample** (with 50 tosses the empirical estimate would be closer to .2; with 1,000, closer still, per the law of averages) — this has effectively restricted empirical optimal-f to mechanical systems with plenty of history.
3. **Usable by ANY trader, mechanical or discretionary** (e.g., Elliott Wave, Gann, a market guru) — since no trade-history sample is required, just estimated distribution parameters. Caveat: this assumes the FUTURE distribution resembles the estimated one — arguably a bigger assumption for discretionary traders. Discretionary practitioners are just as subject to optimal-f mathematics as mechanical traders: overbetting still dooms even the best analyst, underbetting still costs "geometrically lower profits than their expertise... should have made for them."
4. **"Perhaps the biggest advantage"**: enables **"What if" scenario modeling** — varying input parameters (e.g., simulating a hot system cooling down) to see the effect on optimal f in advance, something a fixed empirical history cannot do.

**Normal density and standardization (Vince Ch.3):**
```
N'(X) = 1/(S*(2*3.1415926536)^(1/2)) * EXP(-((X-U)^2)/(2*S^2))         (3.14)
N'(Z) = 1/((2*3.1415926536)^(1/2)) * EXP(-(Z^2/2)) = .398942*EXP(-(Z^2/2))   (3.15a)
Z = (X-U)/S                                                             (3.16)
```
where U = mean, S = population SD, X = observed data point. Peak of the standard Normal curve: N'(0)=.398942.

**Cumulative Normal probability approximation** (footnoted: the true integral has no closed form; this is a very close approximation — used throughout the rest of the book, including the Runs Test confidence lookup in `14_backtesting_and_validation.md` §13 and Appendix C's Fisher's Z below):
```
N(Z) = 1 - N'(Z) * ( (1.330274429*Y^5) - (1.821255978*Y^4) + (1.781477937*Y^3) - (.356563782*Y^2) + (.31938153*Y) )
IF Z<0 THEN N(Z) = 1 - N(Z)
where Y = 1/(1+.2316419*ABS(Z))                                         (3.21)
```
Upper-tail-only variant (drop the leading `1-` and the `IF Z<0` sign flip): gives P(event ≥ Z SD) directly — this is the variant used in the optimal-f search below, since each discretized point needs "probability of an event at or beyond this many SD," not a cumulative probability.

**"What if" Shrink/Stretch mechanism**: Shrink = multiplier on the mean (can be negative, even flip sign, to simulate the system's edge changing/reversing). Stretch = multiplier on the SD (must be positive; >1 simulates rising dispersion/volatility). Lowering stretch toward 0 makes results MORE optimistic; lowering shrink toward 0 makes them MORE pessimistic.
```
D = (U*Shrink) + (S*E*Stretch)                                          (3.28)
```
where D = the mapped P&L value, E = the standard-unit (Z) value. With Shrink=Stretch=1 this reduces to the base mapping D=U+(S*E) (Eq 3.27), i.e. no scenario adjustment.

**Full search procedure**: choose a sigma-bounding range (Vince recommends **3 to 5 sigma**; 3σ captures 99.73% of the mass) and a point count (≥10× the number of sigmas). For each equally-spaced standardized point, map to a dollar P&L via (3.28), get its associated upper-tail probability via (3.21), then:
```
HPR = (1 + (L/(W/(-f))))^P                                              (3.30)
TWR = Π[i=1,N] HPRi                                                     (3.31)
G = TWR^(1/Σ[i=1,N] Pi)                                                 (3.32)
GAT = (G(f) - 1) * (W/(-f))                                             (3.33)
K = E/Q                                                                 (3.34)
Q = W/(-f)                                                              (3.35)
```
where L = the associated P&L for a point, W = the worst-case associated P&L in the table (always negative — the point at the lower sigma bound), f = the f value being tested, P = the point's associated probability, K = contracts to trade, E = current account equity. Loop f from 0 to 1; the f maximizing G is optimal.

**Fully worked 232-trade example** (same dataset as the empirical method, §1.1-1.6; mean=.330129 pts=$330.13/pt, SD=1.743232 pts=$1,743.23/pt at $1,000/point, ±3σ range, 61 points): worst-case point (Z=-3) maps to `D = 330.129 + 1743.232*(-3) = -$4,899.57`. Search result: **optimal f = .744**, geometric mean = **1.0265**, GAT = **$174.45**, i.e. **1 contract per $6,585.44** (`Q = -4899.57/-.744`). Over the full 232-trade history, expected TWR = `1.0265^232 = 431.79` (+43,079%).

**"Slop" — the discrepancy between the theoretical and true empirical distribution**: on this exact dataset, the empirical optimal f (Chapter 1's method, same data) gives **1 contract per $7,918.04** — i.e. the Normal-parametric method here sits slightly to the right (more aggressive) of the true empirical optimum. This numeric gap IS the "slop" for this dataset. Vince's mitigating argument for using the Normal anyway: option pricing itself assumes the log of price changes is Normal, so "there is a lot to be said for expecting the future distribution of prices to be Normally distributed."

**Worked "What if" scenario** (shrink=.5, i.e. average trade halves; stretch=1.6, i.e. dispersion rises 60%): optimal f collapses from .744 to **.262** (1 contract per $31,305.92), geometric mean drops to 1.0027, 232-trade TWR drops from 431.79 to **1.869** — "not even close to what it presently would be." This is Vince's own worked demonstration of scenario stress-testing applied to his *own* parametric-Normal machinery (distinct from the Kaufman/Chan stress-testing discussed elsewhere in this file).

**Explicit warning on sensitivity**: "the optimal number of contracts to trade is [very sensitive] to the worst loss," which is entirely a function of the chosen sigma-bounding range. A loss beyond the chosen bound "can really hurt us... you should be very careful what value you choose for this range bounding parameter. **You'll have a lot riding on it.**"

**Applying to equalized data**: equalize raw P&L's to percentage terms (Eqs 2.10a-c, §3.5 above), multiply by the current price, then standardize on the equalized mean/SD. Optimal f, geometric mean, and TWR are invariant to which current price is used; GAT, arithmetic average trade, and threshold to geometric are NOT (they're denominated in current-price dollars and must be redone if price changes).

**Estimated Geometric Mean (EGM) — a related Ch.1 shortcut formula worth noting here**, since it uses the same A/SD inputs this section's technique estimates directly (Vince Ch.1):
```
EGM = (AHPR^2 - SD^2)^(1/2)                                             (1.16a)
EGM = (AHPR^2 - V)^(1/2)                                                (1.16b)   [V = SD^2]
Estimated TWR = ((AHPR^2 - SD^2)^(1/2))^N                               (1.19a)
```
This is a fast closed-form approximation to the geometric mean directly from the arithmetic mean and SD of HPRs — the same Pythagorean relationship as the Fundamental Equation of Trading (§1.5), applied here as a shortcut rather than a full TWR search.

### 1.8 Fitting a Custom Distribution and the Kolmogorov-Smirnov Test (Vince Ch.4)

**Motivation**: "the Normal is often regarded as a poor model for the distribution of trade profits and losses" (Vince, closing Ch.3). Chapter 4 generalizes §1.7's machinery to ANY distribution, whether or not its CDF is known in closed form, and builds a custom 4-parameter distribution shape-matched to real trade data.

**The Kolmogorov-Smirnov (K-S) test** — the preferred goodness-of-fit tool here (vs. the chi-square test, which needs binning; K-S works on unbinned distributions). D = the maximum absolute difference between two CDFs (empirical vs. theoretical), checking both just-before and just-after each empirical CDF jump (since divergence can occur on either side of the discontinuity). Lower D = more alike.
```
SIG = Σ[j=1,∞] (j%2)*4 - 2*EXP(-2*j^2*(N^(1/2)*D)^2)                    (4.01)
```
where SIG = significance level, N = number of trades, `%` = modulus. Series converges quickly. Worked (N=100, D=.04): SIG ≈ **.997** (99.7% confident the theoretical distribution represents the actual one — "a very good significance level").

**Vince's custom "characteristic distribution function"**, built up parameter by parameter from a base bell curve to a 4-parameter (location/scale/skewness/kurtosis) adjustable shape:
```
Y = 1/(X^2+1)                                                           (4.02, base bell curve)
Y = 1/((X-LOC)^2+1)                                                     (4.03, + location LOC)
Y = 1/(ABS(X-LOC)^KURT+1)                                               (4.04, + kurtosis KURT)
Y = 1/(ABS((X-LOC)*SCALE)^KURT+1)                                       (4.05, + scale SCALE)
Y = (1/(ABS((X-LOC)*SCALE)^KURT+1))^C                                   (4.06, + skewness exponent C)
C = (1 + (ABS(SKEW)^ABS(1/(X-LOC)) * sign(X) * -sign(SKEW)))^.5         (4.07)
```
Constraints:
```
-infinity < LOC < +infinity      (4.08)
SCALE > 0                        (4.09)
-1 <= SKEW <= +1                 (4.10)
KURT > 0                         (4.11)
```
When SKEW=+1, the entire right side of the distribution flattens to the peak height (and mirror for SKEW=-1). In practice SCALE and KURT typically fall in .5-3 (extreme cases .05-5). **Explicit caveat**: LOC/SCALE/SKEW/KURT are NOT the same values as the standard descriptive-statistics formulas from §1.7/Ch.3 (e.g. Pearson's skewness) — they are unique to this specific curve.

**Fitting procedure — "the twentieth-century brute force technique"**: grid search over KURT/SCALE (then LOC/SKEW) to minimize the K-S statistic D. Since this custom function's CDF generally has no closed form, build it numerically via "bar summation":
```
N(C) = ( Σ[i=1,C] N'(Xi) + Σ[i=1,C-1] N'(Xi) ) / 2 / Σ[i=1,M] N'(Xi)    (4.12)
```
where C = the current X index, M = total X-value count — average the running sum at the current and previous point, then normalize by the grand total.

**Worked 4-pass zoom on the 232-trade example** (coarse → fine grid search), converging to final best-fit parameters **LOC=.02, SCALE=2.76, SKEW=0, KURT=1.78** (K-S statistic .0835529, significance 7.8384% — a comparatively weak fit vs. the hypothetical example's 99.7%).

**Points of inflection — the explicit bias-variance argument for why this matters** (directly relevant to this project's own overfitting discussions, `14_backtesting_and_validation.md` §9/§13): a point of inflection is where concavity flips. The Normal (and Vince's characteristic function) has exactly 2. The raw, jagged, sparse-tailed empirical trade distribution effectively has MORE than 2. Vince's argument (Galton's-board analogy): the observed 232-trade distribution is itself a noisy, finite-sample realization of a smoother underlying generating process; as trade count→∞, the empirical distribution should converge toward the smooth theoretical shape. Therefore **"the optimal f derived from the theoretical will be more accurate over the future sequence of trades than the optimal f derived empirically over the past trades"** — provided the sample is a fair proxy for the future. Trade-off, explicit: you COULD build a distribution allowing arbitrarily many points of inflection to fit the data perfectly (converging to the empirical result), but "the more points of inflection we were to add... the less robust it would be" — a named bias-variance trade-off, predating that terminology.

**The Stable Paretian Distribution — why Ch.4 built a custom distribution instead of using it directly (Vince Appendix B)**: many researchers believe price changes follow this entire CLASS of distributions (not a single fixed form), on the theoretical basis of the "Generalized Central Limit Theorem" — the ordinary CLT converges to the Normal only under finite variance; the stable Paretian family is "invariant under addition" (the sum of independent stable variables with characteristic exponent A is itself stable with approximately the same A) and serves as the limiting distribution even under INFINITE variance (A<2), precisely where the ordinary CLT fails. Four parameters (A=characteristic exponent/kurtosis, B=skewness, V=scale, D=location) correspond respectively to the 4th/3rd/2nd/1st moments; A=2 recovers the Normal exactly, A=1 gives the Cauchy, A<2 implies fatter tails and infinite variance, and the mean exists only if A>1. **Practical difficulty, explicit**: the stable Paretian's CDF is NOT known in closed form, making parameter estimation difficult — this is explicitly WHY Chapter 4 built the custom "adjustable distribution" (§1.8 above) instead of using the stable Paretian directly for trade P&L. **Explicit, footnoted clarification (do not conflate the two)**: "Do not confuse the stable Paretian Distribution with our adjustable distribution discussed in Chapter 4. The stable Paretian is a REAL distribution because it models a probability PHENOMENON. Our adjustable distribution does NOT [model a specific phenomenon] — rather, it models OTHER probability distributions, such as the stable Paretian" (Vince Appendix B) — i.e., LOC/SCALE/SKEW/KURT (§1.8) is a flexible curve-fitting mechanism, not itself a theoretically-grounded probability model the way the stable Paretian is.

**Bounding-parameter sensitivity — quantified (cross-referenced in `14_backtesting_and_validation.md` §13.5)**: at ±3σ/100 points, optimal f=.206 ($23,783.17/contract) vs. the empirical $7,918.04 — a large discrepancy attributed to sparse empirical tails being "smoothed over" by the fitted curve. Pushing the upper bound out (lower fixed at -3σ) while holding the fitted parameters constant:

| Upper Bound | f | f$ |
|---|---|---|
| 3σ | .206 | $23,783.17 |
| 4σ | .588 | $8,332.51 |
| 5σ | .784 | $6,249.42 |
| 6σ | .887 | $5,523.73 |
| 8σ | .963 | $5,087.81 |
| 100σ | .999 | $4,904.46 |

Widening BOTH bounds symmetrically instead:

| Upper & Lower Bound | f | f$ |
|---|---|---|
| 3σ | .206 | $23,783.17 |
| 4σ | .158 | $42,040.42 |
| 5σ | .126 | $66,550.75 |
| 6σ | .104 | $97,387.87 |
| 10σ | .053 | $322,625.17 |

**Vince's own recommended, reasoned bounding choice for this example**: extend the observed worst case (-2.96σ) further to **-4σ** (anticipate a worse future loss than yet seen), but do NOT extend the observed best case (+6.94σ) beyond what was already observed — because (1) "trading systems notoriously do not trade as well into the future," and (2) erring left of the f-curve peak costs less than erring right (§1.4/Type I-II logic, `14_backtesting_and_validation.md` §13.2). Result at these bounds: optimal f=**.837**, 1 contract per **$7,936.41** — notably close to the empirical $7,918.04 despite the very different methodology. **Explicit blind-spot warning**: "so long as our selected bounding parameters are not violated, our model of reality is accurate in terms of the bounds selected... the possible divergence between our model and reality is our blind spot." Recommended structural defense: use instruments (e.g., long options) that cap liability to a known amount.

### 1.9 Scenario Planning (Vince Ch.4)

Vince's own explicitly recommended technique for **"someone not using a mechanical means of entering and exiting the markets"** — i.e., exactly the situation of a not-yet-backtested hypothesis. Described as "perhaps the best technique, and certainly the easiest to employ" for discretionary/pre-backtest position sizing — easier than estimating full LOC/SCALE/SKEW/KURT parameters (§1.8).

**Two forecasting pitfalls scenario planning addresses**: (1) people systematically assume overly optimistic futures; (2) people make single, straight-line, most-likely-outcome forecasts rather than considering the full outcome spectrum. Vince explicitly rejects the classic 3-scenario (optimistic/pessimistic/unchanged) approach as "too simple... too crude to be of any value" — comparable to finding optimal f from only 3 trades.

**Formal requirements, all mandatory**:
1. Define each unique scenario.
2. Assign each a probability in [0,1]; probability-0 scenarios can be dropped.
3. Probabilities are NOT cumulative — adjust for overlapping causes to avoid double-counting (e.g., "bankruptcy" .15 including a "bankruptcy via foreign competition" .07 subset → adjust bankruptcy-alone to .08).
4. **Sum of ALL probabilities must equal EXACTLY 1.**
5. Each scenario needs a numerical outcome (dollars or any consistent unit).
6. **At least one scenario must have a NEGATIVE outcome** — mandatory. Without a downside scenario the "correct" answer trivially becomes "commit 100%."
7. **Overall mathematical expectation (Eq 1.03) must be strictly positive.** If ME ≤ 0, this specific f-finding technique doesn't apply (though scenario planning itself remains useful).
8. Aim to cover ~99% of the outcome spectrum with as many scenarios as practically manageable.

**Core formulas:**
```
Geometric mean = TWR^(1/Σ[i=1,N] Pi)                                    (4.13)
TWR = Π[i=1,N] HPRi                                                     (4.14)
HPRi = (1+(Ai/(W/-f)))^Pi                                               (4.15)
Geometric mean = (Π[i=1,N] (1+(Ai/(W/-f)))^Pi)^(1/Σ[i=1,N] Pi)          (4.16)
TWR = Geometric Mean^X                                                  (4.17)
AHPR = (Σ[i=1,N] (1+(Ai/(W/-f))) * Pi) / Σ[i=1,N] Pi                    (4.18)
```
where N = number of scenarios, Ai = scenario i's outcome, Pi = its probability, W = the WORST outcome among ALL scenarios (regardless of its probability), f = tested f, X = number of times the scenario set is "repeated" for an extended TWR. Eq (4.18)'s AHPR is flagged as important later for the efficient frontier (expected return of a market system = AHPR-1, `12_portfolio_construction.md`).

**Worked example — XYZ Manufacturing Corporation** (5 scenarios, deciding whether to market a product in a remote country):

| Scenario | Probability | Result |
|---|---|---|
| War | .1 | -$500,000 |
| Trouble | .2 | -$200,000 |
| Stagnation | .2 | $0 |
| Peace | .45 | $500,000 |
| Prosperity | .05 | $1,000,000 |

Probabilities sum to 1.00 ✓, has a negative scenario ✓, ME = `(.1×-500000)+(.2×-200000)+(.2×0)+(.45×500000)+(.05×1000000) = $185,000` (positive) ✓. Naive most-likely-outcome planning would fixate on "Peace" (45% probability) — exactly the error scenario planning + optimal f corrects. Search result: **optimal f = .57**, geometric mean = **1.1106**, converting to a dollar commitment `-$500,000/-.57 = $877,192.35` — XYZ should optimally commit **$877,192.35** to the venture. Committing more = "too far beyond the peak" (overbet); less = "too few contracts on" (underbet).

**Generality, explicit**: the "quantity" need not be money — Vince explicitly extends this to % allocation to stocks vs. cash, bond position sizing, military strategy, underwriting participation, mortgage down payments — "any quantitative decision in an environment of favorable uncertainty." **Drawdown warning carries over unchanged**: whatever fraction is allocated should be expected, at some point, to be almost entirely depleted (near-100% drawdown of THAT allocated portion) as the price of maximizing long-run geometric growth.

**The White-vs-Black decision comparison — geometric mean vs. arithmetic expectation, proven**: naive decision rules (Hurwicz, maximax, minimax, minimax regret, greatest arithmetic ME) can give the WRONG answer whenever outcomes will be reinvested.

- **White**: scenarios A(.3,-20), B(.4,0), C(.3,+30) → ME=$3.00, optimal f=.17, geometric mean=1.0123.
- **Black**: scenarios A(.3,-10), B(.4,+5), C(.15,+6), D(.15,+20) → ME=$2.90, optimal f=.31, geometric mean=1.0453.

Naive ME-maximizing choice picks White ($3.00 > $2.90) — **wrong**. Black is correct because it has the higher geometric mean (1.0453 vs 1.0123): "the black decision makes more than three times as much, on average... as does the white decision" once reinvestment is considered (4.53% vs 1.23% per-play gain, ≈3.7×).

**Explicit rule for when arithmetic (not geometric) IS correct**: only when you do NOT plan to reinvest the money risked into future repetitions of similar decisions. Since "the money risked on an event today will be risked again on a different event in the future" in virtually all real situations, geometric-mean maximization is generally correct. **Generalized rule**: "whenever the outcome of an event has an effect on the outcome(s) of subsequent event(s) we are best off to maximize for greatest geometric expectation. In the rare cases where the outcome of an event has NO effect on subsequent events, we are then best off to maximize for greatest arithmetic expectation." Footnoted exception: an entity currently trading "constant-contract" deciding WHEN to switch to fixed-fractional should maximize arithmetic expectation, at the geometric-threshold transition point specifically.

**Additional property**: maximizing geometric mean at optimal f is inherently MORE conservative than maximizing arithmetic ME (since geometric mean ≤ arithmetic mean always, Eq 3.05, `H≤G≤A`) — a rare case of a technique being simultaneously mathematically superior (max long-run growth) AND more conservative than the naive alternative.

**Bridging empirical and parametric, explicit gray area**: this same machinery, applied to historical trades each treated as a scenario with equal probability 1/N, reduces exactly to the standard empirical optimal-f method (§1.1-1.6). "There is not a fine line that delineates the two schools [empirical vs parametric]... there is a gray area."

### 1.10 Optimal f on Binned Data (Vince Ch.4)

A hybrid empirical/parametric technique: treat each bin as a scenario (probability = trades-in-bin/total-trades, outcome = the bin's midpoint), then apply §1.9's scenario-planning machinery.

**Worked 3-bin example**: bins [-1000,-100] (2 trades, midpoint -550), [-100,100] (5 trades, midpoint 0), [100,1000] (3 trades, midpoint 550) → probabilities .2/.5/.3. Result: optimal f=**.2**, 1 contract per **$2,750** (worst-case loss = -$550, the worst bin's midpoint).

**Explicit binning-sensitivity warning, sharply quantified**: this technique assumes the biggest loss equals the *midpoint* of the worst bin — usually false. Isolating the true worst loss into its own narrow bin instead: adding a dedicated bin [-1000,-1000] (the exact $1,000 loss, isolated, prob=.1) plus [-999,-100] (prob=.1, midpoint -550), [-100,100] (prob=.5, midpoint 0), [100,1000] (prob=.3, midpoint 550) → result changes dramatically to optimal f=**.04**, 1 contract per **$25,000** — a huge shift from $2,750, purely from re-binning the same underlying data (directly relevant to `14_backtesting_and_validation.md`'s discussion of estimation error from coarse/binned data). Second weakness: the average element within a bin generally sits closer to the distribution's mode than the midpoint, so this technique tends to OVERSTATE dispersion. Exact only in the limit of infinite trades and infinite bins.

**Vince's own ranking of all optimal-f techniques (explicit, "in my opinion")**: for mechanical-system traders, the custom-adjustable-distribution parametric method (§1.8) is "most likely" the best estimate of the next trade's true distribution; for non-system (discretionary) traders, scenario planning (§1.9) is "the easiest to employ accurately."

### 1.11 Options, the Underlying, and Multi-Position Optimal f (Vince Ch.5)

A further parametric technique, specifically suited to non-mechanical-system traders: rather than a historical trade-P&L stream, enumerate ALL possible future outcomes for a position (options, the underlying, or simple multi-leg combinations) by a target date, weighted by probability, and find the f maximizing the geometric mean across that outcome distribution. Requires only (a) an estimate of the underlying's volatility and (b) a price forecast — both more readily available to discretionary traders than distributional trade-history parameters.

**Option pricing — Black-Scholes (stock) and Black (futures) models**, needed to compute the `Z(T,U-Y)` term used below:
```
C = U*EXP(-R*T)*N(H) - E*EXP(-R*T)*N(H - V*T^(1/2))                    (5.01, Black-Scholes call)
P = -U*EXP(-R*T)*N(-H) + E*EXP(-R*T)*N(V*T^(1/2) - H)                  (5.02, Black-Scholes put)
H = ln(U/(E*EXP(-R*T))) / (V*T^(1/2)) + (V*T^(1/2))/2                  (5.03)
```
where C/P = fair call/put value, U = underlying price, E = strike, T = decimal-fraction-of-year to expiration, V = annual volatility, R = risk-free rate, N() = Eq (3.21). Dividend adjustment (5.04): `U = U - Σ Di*EXP(-R*Wi)`. Deltas: `Call Delta = N(H)` (5.05), `Put Delta = -N(-H)` (5.06).

**Black futures-option variant** (identical except H):
```
H = ln(U/E)/(V*T^(1/2)) + (V*T^(1/2))/2                                 (5.07)
```
Futures-model deltas: `Call Delta = EXP(-R*T)*N(H)` (5.08), `Put Delta = -EXP(-R*T)*N(-H)` (5.09).

**Historical volatility estimation** (the V input above): compute daily log-returns (`ln(close_t/close_t-1)`), take a rolling N-day sample SD (divide by N-1), annualize by multiplying by √(trading days/year, e.g. √252=15.87450787). Worked (yen futures): 20-day sample SD=.009486832981 → annualized **15.06%**.

**"European Options Pricing Model for All Distributions"** — distribution-agnostic pricing, defining "theoretically fair" as the arithmetic mathematical expectation at expiration, present-valued, assuming NO directional bias:
```
C = Σ(pi*ai) / Σpi                                                      (5.10, raw)
C = (Σ(pi*ai)*EXP(-R*T)) / Σpi                                          (5.11, present-valued; works for puts too)
```
where pi = probability of the underlying at price i at expiration (from ANY distribution — Normal, Student's t, Vince's own adjustable distribution, etc.), ai = intrinsic value at price i. Practical truncation: sum until pi<.001 (≈"1,000 option trades in your lifetime" cutoff).

**Worked Student's t (5 df) example** (100 call/put, underlying=strike=100, 20% vol, 5% RFR): conventional Black (lognormal) model gives both call and put = **2.861**. Under Student's t (5 df, K-S-fitted): call=**3.842**, put=**2.562** — a substantial divergence, because (1) fatter tails push the fair call value higher, and (2) call/put values diverge (unlike the symmetric Black result).

**Put-call parity, Formula (5.13):**
```
P = C + (E-U)*EXP(-R*T)
```
**Consistency correction procedure (mandatory when a distribution implies an underlying expected value ≠ current price)**: compute the underlying's own modeled expected value at expiration via Eq (5.10) with ai=i (here: **101.288467**, not 100 — heavier tails skew it upward, analogous to inflation). Subtract this difference (1.288467) from EVERY intrinsic-value term before applying (5.11), flooring negatives to 0. Re-doing the Student's t example this way yields **both the call and put at 3.218** — consistent with put-call parity, no arbitrage.

**Single long option — HPR and optimal f:**
```
HPR(T,U) = (1 + f*(Z(T,U-Y)/S - 1))^P(T,U)                              (5.14)
```
where f = tested f, S = current option price, Z(T,U-Y) = theoretical option price at underlying=U-Y with T remaining, P(T,U) = 1-tailed probability of the underlying at U with T remaining, Y = the "no-bias" adjustment (underlying's Eq-5.10 expectation minus current price). **Key flexibility**: the distribution used for P(T,U) need not match the pricing model's own distributional assumption (e.g. price with Black-Scholes, weight with fat tails).
```
IF U<=Q: P(T,U) = N( ln(U/Q) / (V*L^(1/2)) )                            (5.15a)
IF U>Q:  P(T,U) = 1 - N( ln(U/Q) / (V*L^(1/2)) )                        (5.15b)
Std. Dev. = U*EXP(V*(T^(1/2)))                                          (5.16, 1 SD above U)
+X Std. Dev. = U*EXP(X*(V*T^(1/2)))                                     (5.17a)
-X Std. Dev. = U*EXP(-X*(V*T^(1/2)))                                    (5.17b)
G(f,T) = {Π[U=-3SD,+3SD] HPR(T,U)}^(1/Σ P(T,U))                         (5.18a/b)
K = INT(E / (S/f))                                                      (5.19, contracts; INT()=floor)
```
Repeat the whole f-search for every possible exit date; the (exit date, f) pair with the highest geometric mean is optimal.

**Single short option** — identical machinery, sign-flipped core term:
```
HPR(T,U) = (1 + f*(1 - Z(T,U-Y)/S))^P(T,U)                              (5.20)
```

**The underlying instrument as an option with infinite T**: `HPR(U) = (1 + (L/(W/(-f))))^P` (reusing Eq 3.30), with:
```
L (long) = U - S                                                        (5.21a)
L (short) = S - U                                                       (5.21b)
```
(S=current underlying price, U=hypothetical future price). Unlike option f's (bounded ≤1 by construction), **f on the underlying CAN exceed 1**. **Critical finding**: if the directional bias Y is properly subtracted from every outcome (removing directional bias, consistent with the put-call-parity-consistent framework), the underlying's modeled expectation equals its current price exactly — **zero expectation, hence NO optimal f exists** for a "blind" position in the underlying. An optimal f for the underlying can only exist given a genuine directional forecast (below).

**Why fairly-priced options can show POSITIVE geometric expectation before expiration (resolves an apparent paradox)**: a "fairly priced" option has zero arithmetic expectation *if held to expiration* — the missing caveat. Two competing dynamics: time-premium decays at the rate of the SQUARE ROOT of time remaining (slowest on day 1); the ±X-SD outcome window (Eqs 5.17a/b) expands with elapsed time but at a DECREASING rate (fastest on day 1). Because a long option's downside is fixed (premium paid) while upside isn't, a wider window favors positive expectation while faster decay hurts it — day 1 has both slowest decay AND fastest-expanding window, so **expectation is greatest the first instant and decays gradually thereafter**, eventually going negative. **Worked decay table** (100 call, 20% vol, 5% RFR, Black commodity model): AHPR/GHPR/f positive on 911105 (f=.0806) and 911106 (f=.0016), negative by 911107. Contract sizing swings enormously across this window: exiting 911105 = 1 contract per **$3,549.63**; holding to 911106 (last positive-expectation day) = 1 contract per **$178,812.50**. **SD-count convergence** (unlike the underlying-instrument bounding-parameter sensitivity of §1.7-1.8, this result is NOT sensitive to the SD-count choice): results converge by 5 SD, "hardly change at all" beyond 5, "seem to stop changing" beyond 8 — Vince's stated 8-SD rule-of-thumb default for single-leg work (strictly valid only under a Normal logs-of-price-changes assumption).

**Incorporating a directional bias**: let the base price U shift over time per a price forecast (e.g. straight-line advance toward a target) rather than holding it at the current price. A tiny .01-point/day upward bias (same 100-call example) raises optimal f to .1081663 (1 contract per $2,645.00) and extends the positive-expectation window an extra day — a sufficiently strong bias can push the positive-expectation window all the way to expiration. Vince recommends re-running the whole procedure daily on the option's current price (a "re-bet as odds shift" horse-race analogy), accepting "many inevitable losses along the way."

**Multi-leg positions and correlation structure — cross-reference**: the causal-relationship (same-underlying, e.g. straddles/spreads) and random-relationship (zero-correlation) multi-leg HPR/geometric-mean formulas (Eqs 5.22-5.27), plus the explicit nested-loop search pseudocode Vince gives for computing them, are developed in `12_portfolio_construction.md` §2.1 alongside the correlative (Ch.6, arbitrary-correlation) generalization those formulas feed into.

---

## 2. Kelly Criterion — Five Treatments

The Kelly criterion appears independently in Vince, Chan, Kaufman, Pardo, and Hilpisch. Each treats it differently. Vince (fractional f), Chan (half-Kelly), and Kaufman (citing the same practitioner convention) agree that Kelly/optimal-f is a **ceiling, not a target** — a maximum theoretical growth-optimal bet size that in practice should be diluted. Pardo does not explicitly state this "ceiling, not target" framing himself; his own caveat is narrower and input-focused (see §2.4) — noted here so the synthesis in §2.6 doesn't overstate agreement on this specific point. Hilpisch's own "half Kelly" recommendation (§2.5) independently converges with Vince/Chan/Kaufman's dilution consensus. They differ substantially in framing, mathematical form, and how central Kelly is to their overall system.

### 2.1 Chan's treatment (Chan Ch.6)

Chan follows Edward Thorp's exposition (Thorp, 1997) directly, adapted from a portfolio-of-securities framing to a portfolio-of-strategies framing.

**Assumption (explicitly flagged as an approximation)**: each strategy's returns are Gaussian with fixed mean mᵢ and standard deviation sᵢ (net of financing costs, i.e., excess returns). Chan explicitly warns this is potentially quite inaccurate since real-world large losses occur far more often than Gaussian tails allow.

**Multi-strategy Kelly formula:**
```
F* = C⁻¹M
```
where F* = (f₁*,...,fₙ*)ᵀ are optimal equity fractions per strategy, C = covariance matrix of strategy returns, M = vector of mean unlevered excess returns.

**Single-strategy (independent) Kelly formula** — the version most directly comparable to classical Kelly:
```
fᵢ = mᵢ / sᵢ²
```

**Derivation (Gaussian case, Chan Ch.6 appendix)**: from the general compounded, levered growth-rate formula `g(f) = r + f·m − s²·f²/2` (Chan notes this g(f) formula's own derivation is non-trivial and is not given, only its optimization), taking `dg/df = m - s²f = 0` gives `f = m/s²`.

**Maximum achievable growth rate at Kelly-optimal leverage:**
```
g = r + S²/2
```
where S is the portfolio Sharpe ratio — this is Chan's formal justification for his repeated claim (Ch.2, per this book's other extraction files) that Sharpe ratio, not raw return, drives long-term compounded wealth growth.

**Sidebar/Example 6.1 — "An Interesting Puzzle (or Why Risk Is Bad for You)" (Chan Ch.6)**: a distinct, deliberately vivid worked illustration Chan uses precisely because it is counterintuitive even to sophisticated readers — kept separate from the SPY example below since it isolates the pure risk-decreases-growth point with a zero arithmetic mean, uncontaminated by an actual positive-return asset. **Setup**: a stock follows a true geometric random walk — a 50/50 chance of +1% or −1% each minute. Q: buying and holding this stock, does one make money, lose money, or break even in the long run (ignoring financing costs)? **Common wrong answer**: "flat." **Correct answer**: you **lose money**, at a rate of **0.005% (0.5 basis point) per minute**. **Reasoning**: the compounded growth rate is `g = m − s²/2`, not the one-period arithmetic mean m (which is 0 here) — this mirrors the general fact that the geometric mean of a set of numbers is always ≤ the arithmetic mean (equal only if all numbers are identical), so since the arithmetic mean here is 0, the geometric mean (and hence compounded growth rate) must be negative. **Chan's stated takeaway**: "risk always decreases long-term growth rate — hence the importance of risk management!"

**Worked example (Chan Ch.6, SPY)**: mean annual return 11.23%, std dev 16.91%, risk-free rate 4% → mean excess return 7.231%, Sharpe 0.4275. Kelly leverage `f = 0.07231/0.16912 = 2.528` — a $100,000 account should hold $252,800 of SPY. Explicitly noted: **Kelly f is independent of time scale** (unlike the Sharpe ratio, which is time-scale dependent). Resulting levered compounded growth: 13.14%; the unlevered cash-only growth rate is only `g = r + m - s²/2 = 9.8%`, not the naive 11.23% arithmetic mean — again illustrating that arithmetic mean overstates true compounded growth (the same point Vince makes via the Fundamental Equation of Trading).

**Half-Kelly practice (Chan Ch.6)**: "traders commonly halve the Kelly-recommended leverage" for safety, given parameter-estimation uncertainty and non-Gaussian real returns. This is explicitly a practitioner convention, not a formula-derived optimum.

**Fat-tail leverage cap (Chan Ch.6)** — see §6 below for full treatment.

**Continuous rebalancing requirement**: Kelly-optimal allocation requires continuous adjustment as equity changes. Worked illustration continuing the SPY example: after a 10% loss (equity $74,720), Kelly dictates reducing the position to $188,892 (=2.528×$74,720) — **you must sell into a loss to stay Kelly-optimal**, not average down or hold. Practical cadence: update capital allocation at least once per trading day; re-estimate M/C periodically (rule of thumb: 6-month lookback for ~1-day-holding strategies).

**Retail leverage cap adjustment**: if Kelly-recommended total leverage exceeds a Reg T retail cap l (2x overnight/4x intraday), scale every fᵢ by `l / (|f₁|+|f₂|+...+|fₙ|)`.

### 2.2 Vince's treatment of Kelly, and how he relates it to optimal f (Vince Ch.1)

Vince presents Kelly as the historical precursor to his own more general optimal-f machinery, attributed to John L. Kelly, Jr. (1956, Bell System Technical Journal, "A New Interpretation of Information Rate") — developed for data-transmission noise problems, later applied to gambling because both are "environments of favorable uncertainty."

**Kelly growth function to maximize, Formula (1.08):**
```
G(f) = P*ln(1+B*f) + (1-P)*ln(1-f)
```
where f = fraction bet, P = win probability, B = ratio of win amount to loss amount.

**Closed-form Kelly solutions, valid ONLY for true Bernoulli (2-outcome, fixed-magnitude) distributions:**
```
f = 2P-1                    (1.09a, equal-magnitude win/loss)
f = P-Q                     (1.09b, Q=1-P)
```
Worked example (Eq 1.09, Vince Ch.1): sequence -1,+1,+1,-1,-1,+1,+1,+1,+1,-1 (10 bets, 6 wins) → `f = (.6*2)-1 = .2`.
```
f = ((B+1)*P-1)/B           (1.10a, fixed win:loss ratio B)
f = Mathematical Expectation/B   (1.10b)
f = P-Q/B                   (1.10c)
```

**Vince's critical, explicit warning**: applying these Kelly formulas to real (non-Bernoulli, variable-sized) trade data by averaging win/loss sizes is **"a mistake" that traders commonly make ("here is where so many traders go wrong")** and will not yield the true optimal f — demonstrated by the +9,+18,...,-7 sequence in §1.3 above (naive Kelly-with-averages f≈.16 vs. true optimal f=.24, a 297% performance gap after 999 trades).

**How Vince relates Kelly to optimal f**: Kelly is explicitly framed as a **special case** of Vince's general geometric-mean-maximization search — "when the underlying distribution truly IS Bernoulli, Kelly and Vince's general geometric-mean search method agree exactly" (Vince, `Concepts.md`). The rest of Vince's book (empirical search in Ch.1, parametric-Normal in Ch.3, custom-distribution/scenario-planning in Ch.4, options in Ch.5) generalizes Kelly far beyond the 2-outcome case to handle real trade-P&L distributions, which are "virtually never Bernoulli-distributed."

### 2.3 Kaufman's treatment (Kaufman Ch.23, "Probability of Success and Ruin")

Kaufman's Ch.23 discusses Kelly primarily through the lens of **risk of ruin** rather than as a standalone position-sizing formula (the ruin-focused derivation is detailed in `11_risk_management.md`). Kaufman explicitly cites "**Vince's Modified Risk-of-Ruin**" (via Peter Griffin's blackjack-theory "fair approximation," modified by Kaufman for spreadsheet use) as the connective bridge between Kelly/optimal-f and ruin probability, using AvgWin, AvgLoss, ProbWin, ProbLoss, Investment, and MaxRisk as inputs (Kaufman Ch.23). Kaufman does not present Kelly's classical f=2P-1 form independently of this ruin framework in the extracted material; instead his position-sizing chapter emphasizes **volatility-based sizing methods** (§4-5 below) as the practical alternative/complement to Kelly-style edge-based sizing.

### 2.4 Pardo's treatment (Pardo Ch.5)

Pardo gives Kelly/Optimal f as the fourth of his four named position-sizing methods (alongside volatility-adjusted sizing, Martingale, and Anti-Martingale — see §4.3 and §8 below), presented as a compact, self-contained named formula rather than as part of a larger geometric-growth apparatus.

**Attribution, explicit**: Pardo names "Optimal f (fixed fractional trading)" and attributes it to **Ralph Vince (1990)** — a direct, named cross-reference from one source book in this corpus to another — itself derived from the classical Kelly criterion via "Professor Edward Thorpe's" application of it to gambling and trading.

**Formula:**
```
Kelly % = (Win % − Loss %) / (Average Profit / Average Loss)
```

**Worked example (Pardo Ch.5)**: 55% win rate (45% loss rate), average win $1,750, average loss $1,250 → `Kelly% = (55−45)/(1,750/1,250) = 10/1.4 = 7.14%`. Applied to a $250,000 account at $1,000 risk/contract → 7.14% × $250,000 / $1,000 = 17.85 contracts, floored to **17 contracts**.

**Pardo's own caveat (distinct from, but thematically parallel to, Vince's/Chan's dilution warnings)**: the inputs to this formula — win rate, average win, average loss — are themselves statistically **"fuzzy"**: small-sample, high-variance quantities that inject meaningful inaccuracy into the resulting Kelly/Optimal-f percentage. Unlike Vince's "mistake traders commonly make" warning (§2.2, about wrongly averaging non-Bernoulli trade data into a closed-form Kelly equation) or Chan's Gaussian/fat-tail warning (§2.1, §6), Pardo's caveat is about **input-estimation noise** specifically, not about the formula's distributional assumptions — a third, independently-arrived-at instance of the broader "Kelly inputs are unreliable" theme, but not identical in mechanism to the other two.

Pardo does not present a fractional-Kelly or half-Kelly dilution recommendation of his own in the extracted material — his contribution to this section is the named formula, its worked example, and the input-fuzziness caveat, not a stated ceiling/target distinction.

### 2.5 Hilpisch's treatment (Hilpisch Ch.10) — the continuous/stock-market formulation, explicitly distinguished from Sharpe

Hilpisch derives Kelly independently via the same binomial-game starting point as Vince (§2.2), then generalizes it to continuous trading of a stock/index rather than to a portfolio-of-strategies (Chan, §2.1) or a trade-history search (Vince).

**Binomial derivation**: repeated bets on a biased coin, `P(heads)=p > 1/2 > q=1-p`. Naive expected-value maximization (a risk-neutral agent betting all available capital each round) causes near-certain eventual ruin from a single loss, so it does not maximize long-run wealth. Maximizing the long-term **geometric growth rate** instead (via `G(f) = p*log(1+f) + q*log(1-f)`) yields the closed-form optimal fraction **f\* = p − q** in the simple 50/50-stakes case — e.g., p=0.55 → f\*=0.10 (bet 10% of capital per round). A Python simulation (50 series × 100 coin-toss trials, capital compounding by `(1±f)` per win/loss) comparing f=0.05, 0.10(=f\*), 0.25, 0.50 shows lower f gives lower average growth, while higher-than-optimal f can give either higher average ending capital (f=0.25) *or* much lower (f=0.5) — with volatility increasing considerably in both higher-f cases — demonstrating the Kelly fraction as an interior optimum, not "more is always better."

**Continuous formulation for stocks/indices**: generalizing the binomial model to expected return `μ`, volatility `σ`, risk-free rate `r`, and deriving the growth-rate-maximizing formula for continuous trading yields:
```
G∞(f) = r + (μ-r)·f - (σ²/2)·f²
```
optimized at **f\* = (μ − r) / σ²** — excess return divided by **variance**. Hilpisch explicitly notes this formula "looks similar to the Sharpe ratio but is different": **Sharpe divides by volatility (σ) in the denominator, Kelly divides by variance (σ²)** — the identical structural distinction Chan makes independently via `f=m/s²` (§2.1), arrived at via a different derivation route and a different asset-class framing (single-instrument leverage vs. multi-strategy portfolio), an independent-convergence data point for this file's cross-book synthesis.

**Worked S&P 500 example**: `.SPX`, 2010–2019 EOD data — annualized mean return μ≈9.99%, annualized volatility σ≈14.76%, r=0. Optimal Kelly fraction/leverage **f\*≈4.59** — theoretically optimal to invest **4.59× available capital** (459% leveraged long) in a passive S&P 500 position given these historical statistics. Simulated equity curves at f\* and fractions thereof show substantially higher volatility of the equity path at full Kelly than the index itself, motivating the practitioner heuristic of using **"half Kelly"** (here ≈2.3) instead — presented explicitly as a recommendation/heuristic, not a formal derivation, trading some growth-rate optimality for materially reduced volatility/drawdown risk.

**Boxed warning (explicit)**: "Leverage increases risks associated with trading strategies significantly... A positive backtesting performance is also no guarantee whatsoever for future performances." Some jurisdictions (e.g., Germany) cap leverage ratios for retail traders by instrument class.

**Applied to a strategy's own returns, not just the raw instrument**: annualizing the *strategy's* (not the underlying instrument's) mean/variance and applying the same `mean/var` (full) or `×0.5` (half) formula gives the AdaBoost ML strategy of `14_backtesting_and_validation.md` §12.6 an optimal leverage **above 50** once transaction costs are included — noted as "feasible, even for retail traders" via CFD brokers offering such leverage.

### 2.6 Where the five treatments agree and differ

**Agreement:**
- Vince, Chan, Kaufman, and Hilpisch treat the raw Kelly/optimal-f output as a **theoretical ceiling that should be diluted in practice** — Vince via fractional f (static or dynamic, `12_portfolio_construction.md`/`11_risk_management.md`), Chan via half-Kelly, Kaufman by folding Kelly into a risk-of-ruin framework where a chosen fraction of full Kelly reduces ruin probability, and Hilpisch via his own explicit "half Kelly" recommendation (§2.5). Pardo does not make this specific ceiling/target claim (§2.4) — his caveat is about input reliability, not about how much of the computed % to actually bet.
- All five warn that the inputs/assumptions feeding a closed-form Kelly-style formula are **unreliable in some way**: Vince and Kaufman-via-Vince warn real trade data is not Bernoulli-distributed (so averaging into the classical Kelly formula misstates the optimum); Chan warns real returns are not Gaussian (fat tails understate risk); Pardo warns the win-rate/avg-win/avg-loss inputs themselves are statistically fuzzy from limited sample size; Hilpisch's own boxed warning stresses that a positive backtest is no guarantee of future performance and that jurisdictional leverage caps may override the formula's output regardless. These are distinct failure mechanisms behind a shared conclusion — naively plugging simple statistics into a closed-form Kelly-style equation understates or misstates the true, safe optimum.
- Vince, Chan, Pardo, and Hilpisch all connect position sizing directly to **compounded (geometric) growth or growth-optimal outcomes**, not one-period arithmetic expectation — this is the deepest point of agreement among the sources that address it, though Pardo's own formula is stated without an explicit geometric-growth derivation in the extracted material (unlike Vince's Fundamental Equation of Trading, Chan's `g=r+S²/2`, or Hilpisch's `G∞(f)=r+(μ-r)f-(σ²/2)f²`).
- **Chan's and Hilpisch's formulas are structurally identical** (`f=m/s²` vs. `f*=(μ-r)/σ²`, both "excess return over variance," both explicitly contrasted with Sharpe's "excess return over volatility") despite being derived independently in two different books for two different framings (multi-strategy portfolio allocation vs. single-instrument leverage sizing) — a clean independent-convergence data point.

**Differences in framing/formula:**
- Vince's f is a **divisor of the biggest loss** (a distribution-agnostic, trade-history-driven or scenario-driven quantity found by search); Chan's and Hilpisch's f is a **direct leverage multiplier** derived in closed form from mean/variance under a Gaussian assumption; the two families are mathematically related (both maximize geometric growth) but Vince explicitly builds his machinery to work on **any distribution** (Normal, custom-fitted, scenario-based, binned), which he considers necessary because "the Normal is often regarded as a poor model for the distribution of trade profits and losses" (Vince Ch.3). Pardo's `Kelly % = (Win % − Loss %) / (Average Profit / Average Loss)` is closest in surface form to Vince's Bernoulli closed-form solutions (§2.2's formulas 1.09a-1.10c) — both reduce Kelly to a simple win-rate/payoff-ratio ratio. Hilpisch's own binomial derivation (`f*=p-q`) is *also* structurally identical to Vince's Bernoulli formula 1.09b — a second independent-convergence point, this time between Vince and Hilpisch specifically.
- Chan's Kelly extends naturally to a **multi-strategy covariance-matrix formula** (`F*=C⁻¹M`) as the primary object of interest; Hilpisch's Kelly is applied only at the single-instrument or single-strategy level (raw S&P 500 exposure, or a single ML strategy's own return series) with no portfolio-level/covariance extension shown; Vince's portfolio-level extension of optimal f is a separate, more elaborate apparatus (dividing each component's dollar f by its geometric-optimal portfolio weighting — see `12_portfolio_construction.md`). Pardo gives no portfolio-level Kelly extension in the extracted material.
- Kaufman does not present a standalone closed-form Kelly sizing formula as the chapter's centerpiece; his practical toolkit for Ch.23 leans on volatility-parity/ATR/VIX sizing (below) with Kelly folded into the ruin-probability apparatus rather than treated as the primary sizing method.
- Pardo is the only one of the five to give a fully worked, contract-count-resolved numeric example (17 contracts on a $250,000 account) without any accompanying dilution step — the rawest, least-hedged presentation of a Kelly-style output among the five treatments. Hilpisch, by contrast, is the only one to give a fully worked *leverage-ratio* example on a real, named, broad-market index (S&P 500, f\*≈4.59) with an explicit half-Kelly figure (≈2.3) computed alongside it.

---

## 3. Fixed-Fractional Sizing (Vince Ch.2 and related)

Fixed-fractional trading — always trading a fixed fraction f of current equity, recalculated as equity changes — is the mechanism through which optimal f is actually implemented. Vince Ch.2 ("Characteristics of Fixed Fractional Trading and Salutary Techniques") develops its properties and refinements in depth.

### 3.1 Small accounts / traders just starting out (Vince Ch.2)

Problem: a small account trading 1 contract cannot simply use pure optimal-f dollar sizing from day one, because a single bad trade could impair the ability to meet margin on the next trade.

**Formula (2.01):**
```
A = MAX{ (Biggest Loss/-f), (Margin + ABS(Drawdown)) }
```
where A = dollars to allocate to the first contract, Margin = initial speculative margin, Drawdown = historic maximum drawdown.

Worked example: optimal f=.4, biggest loss=-$3,000, max drawdown=-$6,000, margin=$2,500 → `A = MAX{7500, 8500} = $8,500`. Given $22,500 equity, this method yields 2 contracts total vs. 3 under plain optimal-f sizing — converging to standard sizing as equity grows.

### 3.2 Threshold to Geometric (Vince Ch.2)

The equity level at which a small trader should step up from N to N+1 contracts (relevant because integer-only position sizing makes plain optimal-f sizing sub-optimal at low unit counts).

**Formula (2.02):**
```
T = AAT/GAT * Biggest Loss/-f
```
where AAT = arithmetic average trade, GAT = geometric average trade (see §3.4). Worked example (2:1 coin toss, optimal f=.25): naive doubling at $8.00 equity is premature; `T = .50/.2428 * 4 = $8.24` is the correct step-up point. **The trough of the threshold-to-geometric curve occurs exactly at optimal f** — trading at optimal f minimizes the equity level at which stepping up becomes worthwhile.

Explicit limitation: valid for stepping from 1→2 contracts, but **not valid** for N→N+1 generally unless the trader refuses to trim size back down during a drawdown while below threshold — trimming invalidates the derivation. If contracts are never trimmed below threshold, this comes at a cost of lower asymptotic TWR and higher drawdown/ruin risk than pure optimal f.

### 3.3 One combined bankroll vs. separate bankrolls (Vince Ch.2)

**Core claim**: trading multiple market systems from **one combined bankroll** (recalculated/"recapitalized" daily off total equity) asymptotically beats maintaining separate per-system bankrolls. Under positive correlation, both approaches net the same profit. Under **negative correlation**, the combined-bank approach produces dramatically better results (worked coin-toss example: $42.38 net profit either way with separate bankrolls, but $102.73 — more than double — with one combined bank under negative correlation). **"When using fixed fractional trading you are best off operating from a single combined bank"** (Vince Ch.2).

### 3.4 Geometric Average Trade (GAT) (Vince Ch.1)

**Formula (1.14):**
```
GAT = G * (Biggest Loss / -f)
```
where G = geometric mean minus 1. GAT is what a system actually earns per contract per trade on average under reinvestment (as opposed to the raw, naive "average trade" statistic, which Vince says most traders wrongly rely on) — it accounts for the fact that losses tend to occur when many contracts are held (after a winning streak has grown the position) and wins tend to occur when fewer contracts are held (post-loss).

### 3.5 Equalizing data for fixed-fractional sizing (Vince Ch.2)

When historical P&L was earned at different past prices than the current price, Vince recommends converting raw P&L to percentage terms before computing optimal f, then reconverting to dollars at the current price:

**Formulas (2.10a-c):**
```
P&L% = Exit Price/Entry Price - 1        (longs)
P&L% = Entry Price/Exit Price - 1        (shorts)
P&L% = P&L in Points / Entry Price
```
**Formula (2.11) — converting equalized f back to dollars at the current price:**
```
f$ = Biggest % Loss * Current Price * $ per Point / -f
```

Key property: optimal f itself does not change with price under equalization — only f$ (the dollar translation) changes continuously as price moves. Vince's own stated position (explicitly framed as opinion, not mathematical fact): "you are probably better off with the equalized data," with the heuristic that if equalized vs. non-equalized results differ a great deal, you are probably using too much (stale) historical data regardless of which method you pick.

### 3.6 Dollar/share averaging (Vince Ch.2)

A complementary technique for entering/exiting a *position in the trading program itself* (not sizing individual trades): entering with a fixed dollar amount per period (dollar averaging in) or exiting with a fixed share/unit count per period (share averaging out) yields a below-average entry cost or above-average exit price respectively, when lacking directional knowledge about near-term performance. Recommended only after checking for dependency (Ch.1's runs test/serial correlation) on monthly equity changes — if dependency is found at high confidence, a timed lump-sum entry may be preferable instead.

---

## 4. Volatility-Target / Volatility-Parity Sizing (Kaufman Ch.23)

### 4.1 Volatility parity for futures (Kaufman Ch.23, Table 23.3)

**Rationale, explicit**: futures require substantial reserves beyond margin to reduce inherent leverage — typically ~25% of investment used for margin+reserve; without reserves, leverage ranges 4:1 to 20:1 depending on market volatility, and using 25% cuts leverage by a factor of 4.

**Procedure:**
1. Divide the trading allocation equally across markets (e.g., $20,000 each of a $100,000 pool for 5 markets).
2. Compute each market's 20-day ATR.
3. Multiply ATR × conversion factor (big point value) × currency conversion = dollar volatility per contract.
4. Position size (contracts) = Allocation / Dollar Volatility.

**Effect**: equalizes volatility risk across positions, maximizing diversification. In Kaufman's worked example, crude oil and NASDAQ (the most volatile markets tested) receive the smallest contract counts. **Risk parity** (a more complex alternative using incremental price-change data) is noted but not endorsed: "it is not clear that the result is better" (Kaufman Ch.23).

### 4.2 Portfolio-level volatility targeting (Kaufman Ch.23, "Reserves and Targeted Risk Levels")

A 5-step procedure explicitly comparable to modern vol-target methodology:
1. Record daily P&L from a simulated trading history.
2. Compute the standard deviation of those daily P&L figures.
3. Choose a target annualized-volatility risk level (measured on **strategy returns**, not on underlying prices).
4. Worked interpretation: a 12% target risk implies 1 SD = 12% → a 16% chance of losing 12% over the sample period, 2.5% chance of losing 24%.
5. If actual computed risk exceeds the target, scale position size down by (target/actual) — e.g., 0.12/actual_risk.

**Stated practical range**: 6% is described as the lowest practical target (8% is more typical); 16%+ "can put an investor at risk." Kaufman forward-references this exact procedure as "volatility stabilization," developed fully at the portfolio level in his Chapter 24 (outside this extraction's scope; see `12_portfolio_construction.md` for any portfolio-level material captured elsewhere). **Explicit caveat preserved**: this is presented in a stock/futures-portfolio context and is **not validated for crypto** in the source.

### 4.3 Pardo's "volatility-adjusted sizing" (Pardo Ch.5) — the simplest of the four treatments

Pardo names this his first (of four) position-sizing methods, calling it **"volatility-adjusted sizing"** despite its formula being a fixed-fraction-of-equity risk rule rather than a volatility-measure-driven one — the label is Pardo's own, preserved as-stated rather than relabeled to match this file's Kaufman-driven §4/§5 terminology.

**Formula:**
```
Contracts = (fixed % of equity to risk) / (dollar risk per contract)
```

**Worked example (Pardo Ch.5)**: 3% risk on a $250,000 account = $7,500; dollar risk per contract = $1,000 → 7,500/1,000 = 7.5, floored to **7 contracts**.

This is Pardo's baseline sizing method — named first in his own Ch.5 taxonomy, ahead of Martingale, Anti-Martingale, and Kelly/Optimal f (§2.4 above; §8 below) — and is structurally the simplest version of the same underlying principle Kaufman's §4.1-4.2 volatility-parity/vol-targeting procedures also implement: size a position so that a fixed amount of account risk maps to a fixed dollar-per-unit risk, rather than sizing by a raw unit count. Unlike Kaufman's ATR-driven dollar-volatility-per-contract calculation (§4.1) or Kaufman's daily-P&L-standard-deviation-driven portfolio targeting (§4.2), Pardo's version takes "dollar risk per contract" as a given input (e.g., from a stop-loss distance, §9.1 of `09_exits.md`) rather than deriving it from a rolling volatility measure — making it the fourth, independently-stated, and notably simpler instance of the "size by fixed % equity risk ÷ per-unit dollar risk" family collected in this section.

### 4.4 Managing risk via size reduction instead of stops (Kaufman Ch.23)

An explicit alternative to stop-losses: reduce position size as volatility increases rather than exiting outright, allowing a trend-follower to remain in a trend while cutting risk. Rebalancing to volatility incurs added transaction costs. The full portfolio-level version of this ("volatility stabilization," scaling entire-portfolio leverage to hold constant risk) is deferred by Kaufman to his Chapter 24.

---

## 5. ATR-Based Sizing (Kaufman)

ATR appears as the core volatility proxy across several of Kaufman's Ch.23 sizing and stop-placement methods:

- **Volatility-parity futures sizing** (§4.1 above): position size = Allocation / (20-day ATR × conversion factor × FX conversion).
- **ATR-based stock sizing** (Table 23.4, Kaufman Ch.23): Allocation/ATR per stock, then rescale the whole vector so total dollar value matches the actual investment size (worked BAC/NFLX/XOM/V/AMZN example).
- **Volatility risk stops and profit targets** (cross-reference `09_exits.md` for full taxonomy): a sell stop/target distance set as a multiple of ATR (e.g., 3× the 10-day ATR), explicitly preferred over a fixed-dollar distance because it "automatically adapts as volatility expands/contracts" (this exact preference is echoed independently by Pardo — see §7.1 below — using an "N-day average daily range" rather than named-ATR, but the logic is identical).
- **Kase's Dev-Stop** (Cynthia Kase, 1993, cited in Kaufman Ch.23): a full standard-deviation-based stop procedure using rolling ATR of the 2-day True Range plus a multiplier (2.06-2.25 for tighter, 3.20-3.50 for wider/skew-corrected stops — the source's own exact multiplier-selection criterion did not extract cleanly and is flagged as a gap in the Kaufman extraction). **Position-sizing tie-in (Kaufman, Ch.23)**: because the Dev-Stop is built as 3 stop levels, positions are entered in multiples of 3 contracts/units, with one unit scaled out each time a stop level is crossed (scale-out risk reduction); the full position resets when the trend direction changes.
- **Kaufman's own judgment on stop types (Ch.23)**: "stops that adapt to volatility (e.g., the std-dev stop) are 'most likely to work,' more so than fixed-dollar or fixed-percentage stops." A heat-map test (US 30-yr bonds, 2000-2011, MA strategy) found average performance across all trailing-stop-factor tests beat no-stop, with the best results at longer trend periods combined with stop factors of 4-6× ATR.

### 5.1 Annualized-volatility-based stock sizing (Kaufman Ch.23, Table 23.5)

An alternative to ATR-based sizing: weight_i ∝ 1/AnnVol_i, normalized to sum to 1, then scaled to the total investment amount, further scaled down to a target portfolio volatility (e.g., 10%) if average 20-day volatility exceeds that target. **Explicit caveat**: annualized volatility, computed from closing prices only, "may underestimate the volatility" relative to ATR (which uses the full high-low-close range).

---

## 6. Fat-Tail Leverage Caps (Chan)

Chan Ch.6 gives an explicit, formula-based cap on Kelly leverage designed specifically to survive fat-tail/black-swan events that a Gaussian-return assumption underestimates:

```
Leverage to use = MIN( half-Kelly leverage , max-tolerable-drawdown-implied leverage )

where: max-tolerable-drawdown-implied leverage
     = (your max tolerable one-period equity drawdown) / (historical worst one-period loss)
```

**Worked example (S&P 500/SPY, Chan Ch.6)**: historical worst one-day loss ≈ 20.47% (October 19, 1987, "Black Monday"). If a trader's max tolerable one-day drawdown is 20%, the implied max leverage is ≈1. Since half-Kelly leverage in Chan's own SPY example was 1.264 (half of 2.528), **half-Kelly alone would NOT have been conservative enough to survive Black Monday** — the smaller, drawdown-implied cap should be used instead. This is Chan's explicit, direct demonstration that half-Kelly is "not automatically 'safe enough.'"

**Epistemic humility, explicitly quoted by Chan (citing Wittgenstein)**: "the truly scary scenario in risk management is the one that has not occurred in history before" — for genuinely unprecedented events, "theoretical models are appropriately silent" (Chan Ch.6).

**Practical remedy chain (Chan Ch.6)**: (1) backtest to estimate the historical maximum one-period loss (period = your rebalancing interval); (2) determine your own maximum tolerable one-period drawdown; (3) divide (2) by (1) to get an implied maximum leverage; (4) use the smaller of this and half-Kelly leverage.

This fat-tail cap sits alongside Chan's Gaussian-assumption warning (Ch.6): the Kelly formula's continuous-finance derivation assumes Gaussian returns, but actual returns exhibit **"fat tails"** (Chan cites Nassim Taleb's "black swan" terminology) — large losses occur far more often than a Gaussian bell curve predicts, which is the entire motivation for this additional cap beyond simple Kelly-halving.

---

## 7. Stock Sizing Methods and VIX-Based Sizing (Kaufman Ch.23)

### 7.1 Three stock-sizing methods compared (Kaufman Ch.23, Tables 23.4-23.6)

1. **ATR-based**: Allocation/ATR per stock, rescaled to total investment (see §5.1).
2. **Annualized-volatility-based**: weight ∝ 1/AnnVol, normalized and scaled to a target portfolio volatility (see §5.1).
3. **"The Easy Way"**: simply divide equal dollar allocation by share price, ignoring volatility entirely. **Stated distortion**: higher-priced stocks carry more absolute-dollar volatility but not necessarily more percentage volatility; mitigate by avoiding stocks under $5-10/share. **Author's finding, explicit**: this simple method's allocation shape closely matches the more complex annualized-volatility method once both are scaled to the same target, raising the question "Is the benefit of using the ATR or annualized volatility worth the effort?" Kaufman states this is "the most popular way of calculating position size" as far as he knows.

**Volatility-of-low-priced-stocks warning (Kaufman Ch.23)**: a Bank of America 1998-2018 worked example shows that when BAC dropped to $1.13/share (February 2009), a fixed-dollar-allocation/price sizing rule spiked the resulting share count sharply right as volatility also spiked, exposing the portfolio to elevated event risk. **Explicit recommendation to avoid low-priced stocks for this reason.**

### 7.2 VIX-based sizing (Kaufman Ch.23)

VIX (S&P options-implied volatility) was tested against SPY's 20-day annualized historic volatility, 1990-2018, specifically through the 2008 crisis. **Finding**: VIX runs "slightly higher" than realized volatility on most days but "jumps around more," and did **not** fully reflect the actual peak historic volatility during the 2008 crisis (the 20-day historic-volatility average is inherently smoother).

**Head-to-head test result (Kaufman Ch.23)**: a SPY multi-MA system sized by (1) investment/closing-price (the "easy way" from §7.1) vs. (2) inverse-VIX sizing gave "nearly the same" results. **Kaufman's own choice, explicit**: he adopted method (1), the simple price-based method, because it's simpler, applies to all equities (not just optioned names), and VIX's abrupt day-to-day swings could shift position sizes by up to **25% from one day to the next**, "introducing more chance into the process." This is a direct, explicit rejection of VIX-based sizing in favor of the simpler alternative, based on a head-to-head empirical test — not a theoretical preference.

---

## 8. Martingale / Anti-Martingale Warnings (Kaufman Ch.22)

**Chapter location note**: the task brief that generated this file speculated Martingale content might live in Kaufman Ch.4 or Ch.22. It was verified by direct search (grep for "Martingale" across the Kaufman extraction) to live in **Chapter 22, "Adding Reality"** — specifically the "Gambling Techniques: The Theory of Runs" section — not in Chapter 4 ("Charting Systems"), which does not mention Martingale at all in the extraction.

### 8.1 The gambling-theory framing (Kaufman Ch.22)

Kaufman applies roulette/gambling theory to trading because it satisfies two conditions: (1) it presumes no statistical edge in the occurrence of profits/losses, focusing on *pattern* probabilities (each daily up/down move treated like red/black in roulette); (2) it emphasizes money management under adverse conditions, requiring the same capital-allocation discipline a professional gambler needs.

### 8.2 Simple Martingale (Kaufman Ch.22)

**Definition**: double the bet after every loss; on a win, net one unit of gain and reset to the initial bet size.

**Sizing procedure**: decide the longest run the system must survive (e.g., a run of 8, from a 256-coup probability table), compute $1 doubled 8 times = $128, then divide total risk capital by 128 to get the initial bet size. Worked example: $1,000/128 = $7.8125, rounded down to $7 — meaning an 8th consecutive loss requires an $897 bet.

**Worked 256-coup simulation** (using $7 initial bet): 65 distinct runs, profit of $455 (45.5% return on capital), vs. a flat-equal-bet strategy on the same sequence *losing* $140 on a $7 bet. **Casino real-world limitation, explicitly stated**: house-imposed maximum table bets prevent doubling down past a run of 8, which is the real-world vulnerability of Martingale sizing — an occasional run of 9 would otherwise be catastrophic.

### 8.3 The core money-management warning (Kaufman Ch.4, cross-referencing Ch.22)

Kaufman Ch.4 (in its coverage of the historical Trident trading bulletins) contains the book's most direct, quotable warning: a Trident bulletin suggested a Martingale-style approach (increase position size after each loss, continue until a win occurs). **Kaufman's own direct warning, quoted verbatim in the extraction**: **"The idea of increasing your position size following each loss will eventually result in ruin."** This passage is explicitly cross-referenced by the source itself to Ch.22's "Martingales and Anti-Martingales" and "Theory of Runs" sections — confirming that Martingale content spans both Ch.4 (the warning/critique) and Ch.22 (the full mechanical/mathematical treatment).

### 8.4 Anti-Martingale (Kaufman Ch.22)

**Definition**: the opposite of simple Martingale — double the *winning* bet size (not the losing one) until a goal is reached, resetting to base size on any loss.

**Rationale**: exploits the same long-run statistics but wins only if a long run occurs *early* in the betting sequence. **Worked numeric outcomes from a 256-coup sequence**: waiting for a run of 6 on black lost $138 (no qualifying run occurred); waiting for a run of 6 on red won three times ($94 each) against a $118 loss; waiting for a run of 8 on red won $128 against a $117 loss. **General timing rule**: in 4,096 coups, a run of 11 occurs once (returning $1,024 on a $1 bet) against 2,048 losses — if the long run occurs in the *middle* of play the method roughly breaks even; sooner is better, later is worse.

### 8.5 Martingale applied to trading, with a trend filter (Kaufman Ch.22)

Kaufman develops a named 6-rule system combining Martingale-style doubling with a trend filter, motivated by an empirical finding: testing SPY, QQQ, IWM, DAX, Hang Seng and other markets (1998-2016) found "every market except gold showed a run of 13 or more" up/down days — **"price moves are not random," with "a clearly upward bias."**

**Rules:**
1. IF the trend has just turned up (per a moving average) THEN enter long with 1 unit.
2. IF the trend is still up and price closes lower THEN double the long position.
3. IF the trend is up and price closes higher THEN remove all positions in excess of the original 1 unit.
4. IF the trend turns down THEN exit all longs and sell short 1 unit.
5. IF the trend is down and prices close higher THEN double the short position.
6. IF the trend is down and prices close lower THEN cover all short positions in excess of the original 1 unit.

**Risk cap, explicit**: because prices can move against you longer than your capital lasts, the number of doublings must be capped (worked example: doubling up to 5 times, total cap $32,000 — the exact starting dollar amount before the cap did not extract cleanly from the source PDF and is flagged as a gap). Tested on SPY and QQQ, 1998-June 2018, 120-day MA, $1,000 initial investment, 5 doublings: the 2000-2002 QQQ 90% decline was mostly avoided because the trend filter kept the strategy out of the market; QQQ (having longer runs than SPY) outperformed SPY.

**Anti-Martingale applied test** (Kaufman Ch.22): adding to positions on profitable days, resetting to starting size on a losing day, tested on QQQ from 1999 (same 120-day MA filter, doubling capped at 4×). Doubling returned ~$10,000 on $16,000 invested (62.5%); adding equal amounts returned ~$5,000 on a $5,000 max investment (100%) — the equal-unit approach had the higher percentage return on committed capital, though neither approach uses all funds at all times.

### 8.6 Fractional Martingales and delayed entry (Kaufman Ch.22)

Full doubling requires deep pockets. Cited alternatives (not fully worked in the source): (1) for anti-Martingales, size by actual accumulated profits rather than a fixed doubling rule; (2) scale by 1.5× the previous position size instead of doubling, **attributed to Furguson** ("Martingales" and "Reverse Martingales," *Technical Analysis of Stocks & Commodities*, Feb/Mar 1990) — stated to give the same relative improvement over the base trend method with less absolute risk. A related refinement, "Delayed Countertrend Entry into a Run," suggests waiting for 2-3 consecutive lower closes before doubling (rather than doubling on the first down day), trading fewer opportunities for a lower chance of a further adverse move.

### 8.7 Pardo's brief mention (Pardo, `Risk_Management.md`)

Pardo names both Martingale ("double size after each loss, reset to 1 unit after each win") and Anti-Martingale ("double size after each win, reset to 1 unit after each loss") as gambling-derived position-sizing techniques in his strategy-level risk-control taxonomy, but does **not** endorse either — they are listed alongside volatility-adjusted sizing (§4.3 above, with its own formula and worked example) and Kelly/Optimal-f (§2.4 above, likewise with its own formula and worked example) as the remaining two of his four named position-sizing methods, without further elaboration or warning attached to the Martingale/Anti-Martingale pair specifically in the extracted material (Pardo Ch.5, via `Risk_Management.md`).

### 8.8 Synthesis: why every source treats Martingale as a warning, not a technique

Across Vince, Kaufman, and Pardo, Martingale-style sizing (increasing size after a loss) is uniformly treated as a **cautionary example**, not a recommended technique — in sharp contrast to optimal f / Kelly / volatility-target sizing, which are all presented as legitimate (if risk-laden) growth-optimal methods. The mathematical reason connects directly to §1.4 above: Martingale sizing increases size precisely when the trader has already sustained losses (the opposite of Vince's dynamic-fractional-f principle of scaling exposure with a cushion of accumulated profit — see `11_risk_management.md`), compounding the probability that a single sufficiently long adverse run exhausts capital before the doubling sequence can complete. Kaufman's own explicit statement of this mechanism: "will eventually result in ruin."

---

## 9. Order Sizing and Market-Impact Minimization (Chan Ch.5)

Distinct from the position-*sizing* methods above (which answer "how much capital should this strategy/position get"), this section covers Chan's order-*execution* sizing rules — how large a single order can be without moving the market against you, and how to scale capital across a diversified portfolio of names spanning wildly different market caps without either ignoring small-caps or concentrating dangerously in them. This connects directly to the capacity concept (`16_research_hypotheses.md`, `18_common_failure_modes.md`): these are Chan's own concrete operational answers to sizing within a low-capacity, diversified portfolio.

**Order-sizing rule of thumb**: limit each order to **≤1% of average daily volume** (lookback period for the average is the trader's choice). Chan notes this threshold is easy to hit even for an independent trader on small-cap names — **worked example**: IRN (S&P 600 SmallCap constituent), 3-month average volume ~51,000 shares at $4.45/share close → 1% of volume = 510 shares = just **$2,269 notional**.

**Capital-scaling-by-market-cap rule**: capital allocated per stock should scale with the **fourth root of market capitalization**, not linearly. Market caps span orders of magnitude (tens of millions to hundreds of billions), so linear scaling would assign near-zero weight to small/microcap names, eliminating diversification benefits. Fourth-root scaling keeps the largest-to-smallest weight ratio around **10** (vs. up to ~10,000 under pure linear scaling), subject also to the 1%-of-volume liquidity constraint above.

**Order-splitting/slippage tradeoff**: breaking a large order into smaller pieces reduces market impact but increases **slippage** (the difference between signal-trigger price and average execution price of the full order, growing as execution time lengthens). Chan explicitly flags this technique as "not really suitable for retail traders whose order size is usually not big enough to require this remedy" — a genuine institutional-vs-independent-trader distinction, not a universally-applicable refinement.

**Commission-reduction guidance**: avoid stocks priced under $5 (an institutional convention) — low-priced stocks require more shares for a fixed capital amount (raising commission cost) and tend to have proportionally wider bid-ask spreads (raising liquidity cost).

**Uncontrollable slippage sources** (noted alongside the above, not a sizing rule but a related execution-cost caveat): broker execution speed (software processing delay, risk-control checks against buying power before routing, or the broker's own pipeline speed to exchanges) and insufficient dark-pool liquidity access — factors to weigh in broker selection rather than order sizing per se (Chan Ch.5).

---

## Cross-References

- Full risk-of-ruin mathematics (classical gambler's-ruin formulas, Vince's parametric argument that risk of ruin = 1 for unlimited-liability instruments over an infinite horizon, and Kaufman's Vince-modified spreadsheet risk-of-ruin procedure with its worked Table 23.15) are developed in `11_risk_management.md`.
- Portfolio-level optimal f (the geometric-optimal portfolio, unconstrained efficient frontier, dividing each component's dollar optimal f by its portfolio weighting, Chan's multi-strategy Kelly matrix F*=C⁻¹M in its full covariance-matrix form) is developed in `12_portfolio_construction.md`.
- Stop-loss and profit-target technique taxonomy (risk stops, trailing stops, volatility-based stops, Kase's Dev-Stop, profit targets, scaling in/out) is developed in `09_exits.md`.
