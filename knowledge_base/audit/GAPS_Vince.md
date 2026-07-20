# Gap Audit: Vince, *The Mathematics of Money Management* — vs. `knowledge_base/`

Audited against the full Vince extraction (`Knowledge/Vince_Mathematics_of_Money_Management/`: 8 chapter files, Appendices A/B/C, and all 10 topic files) read cover-to-cover. Compared against `knowledge_base/10_position_sizing.md`, `11_risk_management.md`, `12_portfolio_construction.md`, and `14_backtesting_and_validation.md` (with spot checks of `06_volatility.md`, `16_research_hypotheses.md`, `17_author_disagreements.md`).

**Headline finding**: Vince's *empirical* techniques (Ch.1-2: HPR/TWR/geometric mean, Kelly, Fundamental Equation of Trading, threshold-to-geometric, arc sine laws) and his *portfolio-level* techniques (Ch.6-8: Lagrange/Gauss-Jordan efficient frontier, unconstrained/geometric-optimal portfolio, dynamic fractional f, margin constraint, reallocation methods) are exhaustively and faithfully represented, formula-for-formula, in `10_position_sizing.md`, `11_risk_management.md`, and `12_portfolio_construction.md`. By contrast, Vince's entire middle third — the **parametric optimal-f machinery of Chapters 3, 4, and most of Chapter 5** — is almost completely absent from the knowledge base. This is not a scope decision documented anywhere (no README or scope note excludes it); it is a genuine extraction gap.

---

## CRITICAL

### C1. Chapter 3's full parametric-Normal optimal-f procedure is entirely absent
**Source**: Vince Ch.3, Eq (3.14)-(3.35), plus the fully worked 232-trade example.
**Target**: `10_position_sizing.md` (should sit alongside §1 "Optimal f (Vince)" as a new subsection, e.g. §1.7).

Nothing in the knowledge base documents Vince's method for deriving optimal f from just two estimated parameters (mean, SD) under a Normal-distribution assumption — the technique Vince presents as usable by traders who have *no* trade history at all (discretionary traders), and which he frames as one of the four advantages of parametric over empirical methods. None of the following made it into any topic file:

- The Normal density and its standardized form:
  ```
  N'(X) = 1/(S*(2*3.1415926536)^(1/2)) * EXP(-((X-U)^2)/(2*S^2))        (3.14)
  N'(Z) = 1/((2*3.1415926536)^(1/2)) * EXP(-(Z^2/2)) = .398942*EXP(-(Z^2/2))   (3.15a)
  Z = (X-U)/S                                                            (3.16)
  ```
- The cumulative Normal probability approximation (the closed-form-approximation Vince uses throughout the rest of the book, including the runs-test confidence-limit lookup and Appendix C's Fisher's Z):
  ```
  N(Z) = 1 - N'(Z) * ( (1.330274429*Y^5) - (1.821255978*Y^4) + (1.781477937*Y^3) - (.356563782*Y^2) + (.31938153*Y) )
  IF Z<0 THEN N(Z) = 1 - N(Z)
  where Y = 1/(1+.2316419*ABS(Z))                                        (3.21)
  ```
- The "What if" Shrink/Stretch mechanism (a multiplier on the mean and on the SD respectively) and its price-mapping formula:
  ```
  D = (U*Shrink) + (S*E*Stretch)                                         (3.28)
  ```
- The full search procedure: converting each standardized point to a dollar P&L via (3.28), an associated probability via the upper-tail Normal CDF, then:
  ```
  HPR = (1 + (L/(W/(-f))))^P                                             (3.30)
  TWR = Π[i=1,N] HPRi                                                    (3.31)
  G = TWR^(1/Σ Pi)                                                       (3.32)
  GAT = (G(f) - 1) * (W/(-f))                                            (3.33)
  K = E/Q ;  Q = W/(-f)                                                  (3.34)/(3.35)
  ```
- The fully worked 232-trade example: optimal f = **.744**, geometric mean = **1.0265**, 1 contract per **$6,585.44** — explicitly compared against the empirical optimal f on the same data (1 contract per **$7,918.04**) to introduce the "slop" concept (the gap between a theoretical distribution and the true empirical one).
- The worked "what-if" scenario (shrink=.5, stretch=1.6) showing optimal f collapsing from .744 to .262 — Vince's own worked demonstration of scenario stress-testing that `10_position_sizing.md` currently only describes for Kaufman/Chan, not for Vince.
- The explicit warning that the resulting optimal f is *extremely* sensitive to the chosen sigma-bounding range ("You'll have a lot riding on it").

**Failure scenario if this gap is not filled**: a researcher wanting to size a position from *estimated* return/volatility parameters alone (no trade history — exactly this project's situation for many hypothesis-only strategies) has no formula to reach for in the knowledge base, despite this being Vince's own stated best method for exactly that situation.

### C2. Chapter 4's entire content — K-S test, custom adjustable distribution, and Scenario Planning — is absent
**Source**: Vince Ch.4, Eq (4.01)-(4.18), plus three fully worked examples (232-trade curve-fitting, XYZ Corporation scenario planning, White-vs-Black decision comparison).
**Target**: `10_position_sizing.md` (new subsection).

This is the single largest gap in the audit. Scenario Planning in particular is explicitly Vince's own recommended technique for "someone not using a mechanical means of entering and exiting the markets" (Vince's closing ranking, Ch.4) — i.e., exactly the situation of a researcher evaluating a not-yet-backtested hypothesis — and it is completely missing from `10_position_sizing.md`, `16_research_hypotheses.md`, and everywhere else. None of the following appear anywhere in the knowledge base:

- The Kolmogorov-Smirnov statistic and its significance-level conversion:
  ```
  SIG = Σ[j=1,∞] (j%2)*4 - 2*EXP(-2*j^2*(N^(1/2)*D)^2)                   (4.01)
  ```
- Vince's custom 4-parameter "characteristic distribution function" (location/scale/skewness/kurtosis), built up step by step:
  ```
  Y = 1/(X^2+1)                                                          (4.02, base bell curve)
  Y = 1/((X-LOC)^2+1)                                                    (4.03, + location)
  Y = 1/(ABS(X-LOC)^KURT+1)                                              (4.04, + kurtosis)
  Y = 1/(ABS((X-LOC)*SCALE)^KURT+1)                                      (4.05, + scale)
  Y = (1/(ABS((X-LOC)*SCALE)^KURT+1))^C                                  (4.06, + skewness exponent C)
  C = (1 + (ABS(SKEW)^ABS(1/(X-LOC)) * sign(X) * -sign(SKEW)))^.5        (4.07)
  ```
  with parameter constraints `-∞<LOC<∞`, `SCALE>0`, `-1≤SKEW≤1`, `KURT>0` (4.08-4.11).
- The grid-search ("twentieth-century brute force") fitting procedure and its 4-pass worked example on the 232-trade dataset, converging to LOC=.02, SCALE=2.76, SKEW=0, KURT=1.78.
- The numerical-integration ("bar summation") technique for building a CDF when none is known in closed form:
  ```
  N(C) = ( Σ[i=1,C] N'(Xi) + Σ[i=1,C-1] N'(Xi) ) / 2 / Σ[i=1,M] N'(Xi)   (4.12)
  ```
- The "points of inflection" argument for why the theoretical (smooth) fit is expected to be *more* accurate for future trades than the raw empirical distribution — an explicit, named bias-variance trade-off ("the more points of inflection we were to add... the less robust it would be") that is directly relevant to `16_research_hypotheses.md`'s and `14_backtesting_and_validation.md`'s overfitting discussions but is not cross-referenced there.
- The bounding-parameter sensitivity tables showing optimal f swinging from .053 to .999 purely as a function of where the sigma bounds are set — this exact sensitivity is asserted qualitatively in `10_position_sizing.md`'s discussion of §2.3 but the actual worked numbers and tables are gone.
- **Scenario Planning in full**, including all six formal requirements (probabilities must sum to exactly 1, at least one scenario must be negative, overall ME must be positive, etc.), the core formulas:
  ```
  Geometric mean = TWR^(1/Σ Pi)                                          (4.13)
  TWR = Π HPRi                                                           (4.14)
  HPRi = (1+(Ai/(W/-f)))^Pi                                              (4.15)
  AHPR = (Σ(1+(Ai/(W/-f)))*Pi) / Σ Pi                                    (4.18)
  ```
  the fully worked XYZ Manufacturing Corporation 5-scenario example (optimal f=.57, $877,192.35 optimal commitment), and the White-vs-Black decision comparison (explicit proof that maximizing geometric mean, not arithmetic expectation, is the correct decision rule whenever outcomes will be reinvested — "the black decision makes more than three times as much... as does the white decision" despite White having the higher arithmetic expectation).
- Optimal f on binned data (treating each bin as a scenario), including the explicit, sharp worked demonstration that isolating the true worst loss into its own narrow bin changes optimal f from .2 to .04 — a striking, quotable illustration of binning sensitivity that would strengthen `14_backtesting_and_validation.md`'s discussion of estimation error from coarse data.

**Failure scenario if this gap is not filled**: any future researcher trying to size a discretionary or hypothesis-stage position (no mechanical backtest yet) has zero formula to reach for — despite this being exactly the situation Vince designed Scenario Planning to solve, and despite this project's own memory file (`MEMORY.md`) recording exactly this kind of pre-backtest hypothesis evaluation as a recurring need.

### C3. Chapter 5's option-pricing formulas (Black-Scholes / Black futures / distribution-free) are absent
**Source**: Vince Ch.5, Eq (5.01)-(5.13).
**Target**: `10_position_sizing.md` §2.7 (which currently jumps straight to the options-*optimal-f* HPR formulas 5.14/5.20 without ever presenting the pricing model those formulas price *against*) or `13_indicator_reference.md`.

`10_position_sizing.md` §2.7 correctly preserves the options-optimal-f HPR machinery (Eq 5.14, 5.18a/b, 5.19, 5.20, 5.21a/b) but never presents the option-pricing formulas that feed the `Z(T,U-Y)` term in those equations:
```
C = U*EXP(-R*T)*N(H) - E*EXP(-R*T)*N(H - V*T^(1/2))                    (5.01, Black-Scholes call)
P = -U*EXP(-R*T)*N(-H) + E*EXP(-R*T)*N(V*T^(1/2) - H)                  (5.02, Black-Scholes put)
H = ln(U/(E*EXP(-R*T))) / (V*T^(1/2)) + (V*T^(1/2))/2                  (5.03)
H = ln(U/E)/(V*T^(1/2)) + (V*T^(1/2))/2                                 (5.07, Black futures variant)
Call Delta = N(H) ; Put Delta = -N(-H)                                  (5.05)/(5.06)
```
Also missing: the distribution-agnostic ("European Options Pricing Model for All Distributions") formulas (5.10)-(5.13), which Vince uses to demonstrate a genuinely striking result — under a Student's t (5 df) assumption for log price changes, a 100-strike call/put on a security priced at 100 comes out to $3.842/$2.562 respectively (vs. $2.861/$2.861 under the standard lognormal Black model) — and the put-call-parity consistency correction procedure (subtracting the underlying's own modeled directional bias from every intrinsic value before pricing). None of this appears in `06_volatility.md` (which only borrows Vince's historical-volatility-annualization *procedure*, not his option-pricing formulas) or anywhere else.

**Failure scenario if this gap is not filled**: a researcher wanting to reproduce or adapt Vince's options-optimal-f technique (§2.7 of `10_position_sizing.md`) cannot actually price the options in the first place — the formula that computes `Z(T,U-Y)` is missing from the very file that uses it as an input.

---

## MODERATE

### M1. The Estimated Geometric Mean (EGM) formula and Chapter 1's Combination Portfolio Allocation (CPA) procedure are missing
**Source**: Vince Ch.1, Eq (1.16a)/(1.16b), and the CPA enumeration procedure (Introduction/Ch.1).
**Target**: `12_portfolio_construction.md` §2 (Vince's portfolio-level material) or `10_position_sizing.md` §1.

The knowledge base narrates several downstream consequences of this formula (the coin-toss correlation worked examples appear in `11_risk_management.md` §3.1; Eq 1.15's Daily HPR is cited in `12_portfolio_construction.md` §2.3) but the formula itself, and the procedure that produces the inputs to it, are never stated:
```
EGM = (AHPR^2 - SD^2)^(1/2)                                             (1.16a)
EGM = (AHPR^2 - V)^(1/2)                                                (1.16b)
Estimated TWR = ((AHPR^2 - SD^2)^(1/2))^N                               (1.19a)
```
Also missing is the **Combination Portfolio Allocation (CPA) enumeration procedure** — Vince's Ch.1, pre-Lagrange method of finding a near-optimal portfolio by brute-force enumerating every subset of market systems and every percentage-allocation combination at (e.g.) 10% increments, computing each combination's average daily net HPR and population SD of daily net HPRs, and identifying the empirical efficient frontier from the resulting scatter. This is the empirical precursor to Ch.6's Lagrange-multiplier method, and its absence means the knowledge base jumps straight from Vince's single-system optimal f to the full matrix-algebra portfolio machinery with no bridging technique for a researcher who wants a first-pass, non-parametric portfolio construction without solving a Lagrangian system.

### M2. Chapter 5's causal/random multi-leg HPR and geometric-mean formulas are only partially preserved
**Source**: Vince Ch.5, Eq (5.22)-(5.27).
**Target**: `12_portfolio_construction.md` §2.1.

`12_portfolio_construction.md` §2.1 correctly narrates the *concept* of causal vs. random multi-leg relationships and gives the HPR formulas in prose form, but drops:
```
Ci(T,U) = f*(Z(T,U-Y)/S - 1)          (5.23a, debit leg)
Ci(T,U) = f*(1 - Z(T,U-Y)/S)          (5.23b, credit leg)
SD = (A^2 - G^2)^(1/2)                (5.27, options AHPR/GHPR-derived SD)
```
and the explicit nested-loop pseudocode Vince gives for the full multi-leg, multi-exit-date search (both the shared-exit-date and independent-per-leg-exit-date variants) — a genuinely useful piece of the source for anyone implementing this computationally, since it's one of the few places Vince gives literal algorithmic structure rather than just a formula.

### M3. Chapter 3's "slop" and bounding-parameter sensitivity findings are asserted but not quantified
**Source**: Vince Ch.3-4, multiple worked sensitivity tables.
**Target**: `14_backtesting_and_validation.md` (estimation-error / small-sample caveats section).

`14_backtesting_and_validation.md` §13 captures Vince's Ch.1 dependency-testing statistical caveats in detail, but does not carry over the Ch.3-4 "bounding parameter choice is the single most consequential and most arbitrary decision in the whole parametric framework" finding — quantified by Vince's own worked tables (optimal f ranging from .053 to .999, or f$ ranging from $23,783 to $322,625, purely as a function of where the sigma bounds are set, holding the fitted distribution parameters constant). Since C1/C2 above recommend adding the Ch.3-4 machinery itself, this specific caveat (a load-bearing "estimation-error" warning of exactly the kind `14_backtesting_and_validation.md`'s scope is built around) should be added alongside it, cross-referenced from both files.

### M4. Vince's four "advantages of parametric over empirical techniques" argument is not preserved as a standalone methodological point
**Source**: Vince Ch.3, explicit numbered list.
**Target**: `10_position_sizing.md` or `16_research_hypotheses.md`.

Vince gives an explicit, numbered four-point argument for why parametric techniques are *generally more accurate* than empirical ones when the assumed distribution is a good model (not diluted by small-sample noise; don't require an extensive trade history; usable by discretionary as well as mechanical traders; enable "what if" scenario modeling) — including the striking illustrative example of a 60%-true-probability biased coin where a 20-toss empirical sample (55% observed) gives f=.1 (half the correct Kelly value of f=.2). `Master_Summary.md`'s Author Insights §7 captures a one-line summary of this claim, but the worked coin example and the full four-point argument (which is a genuinely load-bearing piece of Vince's overall epistemology — it's the reason Chapters 3-5 exist at all) doesn't appear anywhere in the knowledge base topic files, making the total absence of Chapters 3-5 (C1/C2 above) even more consequential, since the knowledge base doesn't even flag *why* that material would matter to a reader who doesn't already know the book.

---

## MINOR

### m1. The geometric mean's relationship to Sharpe/Treynor/Jensen/Vami is dropped to a single clause
**Source**: Vince Ch.1 (`Concepts.md` entry on Geometric Mean).
**Target**: `11_risk_management.md` §6.3.

`11_risk_management.md` §6.3 preserves the core sentence ("geometric mean... unique among them in measuring performance 'in the same mathematical form (multiplicative) as how account equity is actually affected'") but drops the explicit list of comparison measures Vince names (Sharpe ratio, Treynor measure, Jensen measure, Vami) — a small nuance, since none of the four is developed further by Vince either, but the framing (geometric mean as a member of a family of dispersion-adjusted measures, not a wholly separate concept) is slightly flattened.

### m2. The "why fairly-priced options can show positive geometric expectation before expiration" reasoning is absent
**Source**: Vince Ch.5, explicit reasoning section.
**Target**: `10_position_sizing.md` §2.7.

`10_position_sizing.md` §2.7 states the *conclusion* ("a 'theoretically fair' option... can nonetheless show a POSITIVE geometric expectation for early exit dates, because time-decay... is slowest on day 1 while the ±X-SD outcome window expands fastest on day 1") but drops the worked decay-of-expectation table (AHPR/GHPR/f by exit date, showing the crossover to negative expectation) and the SD-count convergence table (2/3/5/8/10 SD) that demonstrates this isn't sensitive to the sigma-bounding choice the way Ch.3-4's underlying-instrument optimal f is.

### m3. Appendix A (Chi-Square Test) worked example and Appendix C (Turning Points / Phase Length tests) are not cross-referenced from `14_backtesting_and_validation.md`
**Source**: Appendix A (full worked 232-trade chi-square test, X²=37.5336, confirming non-Normality at significance .000002419), Appendix C (Turning Points Test Eq C.01/C.02, Phase Length Test Eq C.03, Fisher's Z transformation Eq C.04-C.06).
**Target**: `14_backtesting_and_validation.md` §13 (Vince's dependency-testing section) and/or `10_position_sizing.md`.

`14_backtesting_and_validation.md` §13 covers the Runs Test and serial correlation from Ch.1 in detail but never mentions Vince's two *additional* dependency tests from Appendix C (Turning Points, which distinguishes "like begets like" from "like begets unlike" dependency by direction; Phase Length, which detects dependency without indicating its direction) or Fisher's Z transformation (converting a correlation coefficient to a confidence level, including the explicit small-sample caveat: N≤30 requires the Student's t rather than the Normal approximation). Given `14_backtesting_and_validation.md`'s scope is explicitly about validation methodology, these appendix-level statistical tools are on-topic and their absence is a minor completeness gap. Similarly, Appendix A's own worked confirmation that the 232-trade dataset is *not* Normally distributed (chi-square X²=37.5336, 7 df, significance .000002419) — the empirical confirmation of the very "slop" concept discussed in C1/C3 above — is not referenced anywhere.

---

## Verified as ADEQUATE (checked explicitly per the task's exhaustive-check list)

- **Full empirical Optimal f derivation and TWR/HPR machinery (Ch.1)**: complete and faithful in `10_position_sizing.md` §1, including Eq (1.11)-(1.13), the Kelly-vs-true-optimal-f worked sequence (f=.16 vs f=.24, 297% gap), and the flooring-to-integer rule with its stated rationale.
- **The geometric mean maximization argument / Fundamental Equation of Trading**: complete in `10_position_sizing.md` §1.5, all six forms of Eq (1.23)-(1.28) plus (1.19c), the OEX options-overlay worked example, and the IF/THEN implications (A≤1 → certain ruin; A>1 → N drives growth).
- **Why trading above optimal f is mathematically fatal**: complete — the f=.5 breakeven / f>.5 guaranteed-loser 2:1 coin-toss demonstration is preserved verbatim in `10_position_sizing.md` §1.3-1.4, tied explicitly back to the Fundamental Equation.
- **Risk-of-ruin, both philosophical treatment and closed forms**: complete. Vince's own philosophical "unlimited liability + infinite horizon = certain ruin" argument (including the explicit statement that this book does *not* derive classical closed-form risk-of-ruin equations) is faithfully preserved in `11_risk_management.md` §2.1, correctly distinguished from Kaufman's closed-form supplementary treatment in §2.2. This is a case where the knowledge base is *more* complete than a naive reading of Vince alone, since it correctly notes Vince's own acknowledged gap rather than silently filling it with another author's formula and blurring attribution.
- **The drawdown-as-function-of-f relationship**: complete in both `10_position_sizing.md` §1.4 and `11_risk_management.md` §3.1, including the "plutonium" quote, the 30-95% empirical range, and the 35-55% time-in-drawdown finding with its arc-sine-law derivation.
- **Portfolio-level optimal f and correlation effects (Ch.6-8)**: complete and unusually thorough in `12_portfolio_construction.md` §2 — the full Lagrange/Gauss-Jordan worked 4-asset example, the NIC unconstrained-portfolio device, the geometric-optimal-portfolio condition (AHPR-1=V), the weight-vs-quantity distinction, the detrending caveat (including its own explicit failure mode for infrequently-trading systems), dynamic/static fractional f, the four reallocation methods, the margin constraint (Eq 8.08), and the correlation-editing-direction rule ("edit upward, not downward") are all present with equation numbers intact.
- **All four flagged internal source inconsistencies preserved as flagged, not silently corrected**:
  1. Ch.5 probability table summing to 1.30 — preserved in `10_position_sizing.md` §1.6.
  2. Appendix C phase-length formula's ambiguous exponent (D^2*3*D+1 vs. D^2+3*D+1) — preserved in `10_position_sizing.md` §1.6.
  3. Appendix B's Q=P-1 (vs. conventional Q=1-P) typo — preserved in `10_position_sizing.md` §1.6.
  4. Ch.8 margin-constraint $2,000/$4,800/$4,600 table discrepancy — preserved in `10_position_sizing.md` §1.6.
- **The parabolic interpolation search algorithm gap**: correctly preserved as an acknowledged gap, not filled in with invented content. `10_position_sizing.md` §1.2 and §1.6 both explicitly state the algorithm is referenced across Chapters 1/3/4/5 but never given in this book, deferred to the unavailable predecessor title *Portfolio Management Formulas*.
- **Vince's Author Insights/Warnings/Open Questions**: `Master_Summary.md` in the per-book extraction folder is the dedicated file (per the task's expectation), and its contents (13 numbered Author Insights, 8 Warnings/Limitations, 6 Open Questions/Ambiguities) are substantively reflected across `10_position_sizing.md`, `11_risk_management.md`, and `12_portfolio_construction.md` — with the one exception noted at M4 above (the parametric-vs-empirical four-point argument), which is present in `Master_Summary.md` but not carried into the topic files.

---

## Summary

| Severity | Count |
|---|---|
| CRITICAL | 3 |
| MODERATE | 4 |
| MINOR | 3 |
| **Total findings** | **10** |

**Overall completeness assessment**: Vince's empirical techniques (Ch.1-2) and portfolio-construction techniques (Ch.6-8) are represented in the knowledge base with unusual fidelity — equation numbers, worked numeric examples, and even the book's own internal inconsistencies are all preserved exactly, and cross-file consistency (e.g., the risk-of-ruin split between Vince's philosophical treatment and Kaufman's closed forms) is handled correctly. However, **Vince's parametric optimal-f machinery — Chapters 3, 4, and the option-pricing half of Chapter 5, representing roughly a third of the book's technical content and the entirety of what Vince calls the more powerful, more broadly applicable half of his method — did not make it into the knowledge base at all**, beyond a compressed, formula-free summary of the options-optimal-f HPR mechanics in `10_position_sizing.md` §2.7. This is the dominant finding of this audit (C1-C3).

**Did all of Vince's numbered equations make it into the knowledge base?** No. A rough count: Vince's extraction carries approximately 140 numbered equations across the 8 chapters and 3 appendices (Ch.1: ~30 [1.01-1.29 plus lettered sub-variants]; Ch.2: ~13 [2.01-2.14]; Ch.3: ~22 [3.01-3.35]; Ch.4: ~18 [4.01-4.18]; Ch.5: ~27 [5.01-5.27]; Ch.6: ~12 [6.01-6.12]; Ch.7: ~14 [7.01-7.14]; Ch.8: ~8 [8.01-8.08]; Appendices: ~10 [A.01-A.02, B.01-B.31, C.01-C.06]). Of these, essentially all of Ch.1, Ch.2, Ch.6, Ch.7, and Ch.8's equations made it into the knowledge base (the near-total transfer this audit would expect from the source's own stated "unusually clean and complete" extraction). By contrast, only 6 of Ch.3's ~22 equations (3.02/3.05 implicitly via Concepts, and the options-adjacent 3.30-derived form) and roughly 8 of Ch.4's ~18 and Ch.5's ~27 equations made it through — the large majority of Ch.3-5's formula content (C1-C3 above) was not carried into any topic file. The single most important gap is **Scenario Planning (Ch.4)** specifically: it is Vince's own explicitly recommended technique for discretionary/pre-backtest position sizing, directly relevant to this project's own hypothesis-stage research workflow, and it is entirely missing from the knowledge base.
