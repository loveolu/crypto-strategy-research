# Gap Audit: Chan, *Quantitative Trading* vs. `knowledge_base/`

Audited by reading all 8 chapter files, the MATLAB appendix, and all cross-cutting topic files
(`Master_Summary.md`, `Strategies.md`, `Glossary.md`, `Concepts.md`, `Risk_Management.md`,
`Algorithmic_Trading.md`, `Research_Ideas.md`, `Crypto_Specific.md`, `Psychology.md`) in
`Knowledge\Chan_Quantitative_Trading\`, then cross-referencing against all 18 `knowledge_base\*.md`
topic files via targeted full-file reads and greps.

**Overall finding, stated up front:** this is the most faithfully and thoroughly consolidated of any
book's material I would expect to see in a topic-reorganization exercise. Kelly/half-Kelly/fat-tail
cap, cointegration/CADF/half-life, the full backtesting-bias taxonomy, both self-disclosed
overleveraging anecdotes, and both negative-result strategies (PCA −1.81%, Heston-Sadka seasonal
Sharpe −0.1055) are all present, correctly preserved as negative results, and reproduce exact source
numbers. The gaps below are real but narrow — mostly a handful of worked-example numbers dropped in
favor of the rule they illustrate, plus two genuinely absent conceptual threads (capacity/Ch.8 thesis,
and the Ch.7 high-frequency-trading section) that deserve a MODERATE-to-CRITICAL flag because of how
load-bearing they are in the source.

Chapters 1 and 4 (business case, retail-vs-proprietary account structure, brokerage/infrastructure
setup) are almost entirely absent from the knowledge_base. This is **not flagged as a gap** — per
`README.md`, the knowledge_base's explicit scope is strategy paradigms, signal design, and
risk/portfolio/validation mathematics, not business-setup mechanics. That is a deliberate, documented
scope decision, consistent with how the other four books' business/infrastructure chapters are also
absent.

---

## CRITICAL

### C1. Chan's Chapter 8 "capacity" thesis — the book's own central argument — is not represented anywhere

**Source:** Chan Ch.8 (`02_Chapter_08_Conclusion.md`), also foreshadowed in Ch.2's "flying under the
radar" section, and named explicitly in `Master_Summary.md` Author Insight #3 as "Chapter 8's central
thesis."

**What's missing:** The knowledge_base captures Chan's Ch.8 material on *agency risk* (Kerviel,
the rogue-trader anecdote — correctly placed in `18_common_failure_modes.md` §9) but not the chapter's
actual titular argument: **why capacity is the mechanism that explains independent-trader success**.
Specifically absent:
- The definition of **capacity** as "the amount of equity a strategy can generate good returns on,"
  and Chan's claim that low-capacity strategies are structurally unattractive to institutions and
  therefore "the niche for independent traders like us" (explicit quote, Ch.8).
- The **mechanism** for why large-capacity strategies are structurally disadvantaged: most
  low-capacity profitable strategies act as **market makers** (supplying short-term liquidity, taking
  quick profits when the liquidity need disappears); a trader managing billions instead becomes the
  party **demanding** liquidity and must pay for it, forcing long holding periods, which exposes the
  portfolio to macro regime shifts that can cause severe drawdowns even in a sound model.
- The cascade of institutional structural disadvantages Chan lists explicitly: intense inter-fund
  competition erodes shared-strategy profitability; lowered returns pressure managers to overleverage
  to hit targets; competitive pressure pushes toward complexity that "invites data-snooping bias";
  crowded/correlated positioning sets up contagion-driven stampedes.
- Institutional non-quantitative-constraint costs: "every institutional constraint imposed on a
  trading strategy tends to decrease its returns, if not its Sharpe ratio as well" — the explicit
  framing that any added optimization constraint can only decrease (never increase) the objective.
- The "next steps for growth" framework: once a strategy's realized capacity is exhausted, growth
  requires (1) higher-frequency strategies, (2) longer-holding-period/lower-Sharpe strategies that
  "enormously improve capacity," (3) branching into new asset classes (typically higher capacity than
  equities), or (4) further automation.

**Why this matters for this project:** the whole point of Chan's book, per his own framing, is that
low-capacity strategies are the correct target for a small/independent researcher — this is directly
relevant to how this project should be evaluating and prioritizing crypto strategy candidates (small
notional, infrequent institutional interest), yet the concept isn't in the knowledge_base at all.

**Where it should live:** `16_research_hypotheses.md` (as a named strategy-selection heuristic —
"prefer low-capacity/niche strategies") and/or a new subsection in `18_common_failure_modes.md` or
`01_market_structure.md` (liquidity-supplier-vs-demander dynamics as market structure). Cross-reference
from `17_author_disagreements.md` where institutional-vs-independent framing is discussed.

Note: `Master_Summary.md`'s own "Open Questions" §2 ("no formula for capacity is given") IS correctly
reflected in `16_research_hypotheses.md` line 95 — but that only captures the absence of a *formula*.
The qualitative concept and its supporting mechanism (which Chan does explain in full, formula or not)
is what's missing.

---

### C2. The High-Frequency Trading section (Chan Ch.7) is essentially absent as a topic

**Source:** Chan Ch.7, "High-Frequency Trading Strategies" (`02_Chapter_07_Special_Topics.md`, roughly
lines 227-244).

**What's missing:** A dedicated topic file treatment of:
- Chan's **operational definition of "high frequency"**: any strategy that does NOT hold a position
  overnight (explicitly broader/more "pedestrian" than specialist definitions reserving the term for
  sub-second holding periods).
- The **law-of-large-numbers argument** for why high frequency → high Sharpe: placing hundreds to
  thousands of independent bets per day minimizes percentage deviation from mean return (given a
  genuinely positive-mean-return strategy), which in turn permits much higher Kelly-implied leverage
  (Ch.6), boosting realized ROE to "often stratospheric levels."
- The explicit caveat that this argument explains why a high-frequency strategy with positive mean
  return has high Sharpe — it does **not** explain why any particular high-frequency strategy has
  positive mean return in the first place; Chan states this is "impossible to explain in general."
- The **risk-management advantage** specific to high-frequency strategies: small position sizes,
  fast de-leveraging, ability to go to cash entirely — sudden contagious losses are unlikely; "the
  worst that can happen" as such strategies crowd is slow return decay, not a blow-up (a genuinely
  useful contrast against the Ch.6 financial-contagion mechanism, which is well-covered elsewhere).
- **Backtesting/execution challenges specific to HFT**: transaction costs dominate at this frequency;
  last-price data is insufficient (bid/ask/last quote data needed, sometimes full order-book data);
  "quite often, the only true test... is to run it in real-time unless one has an extremely
  sophisticated simulator"; execution speed/co-location can account for a large share of actual P&L.

Only one sentence of this entire section survives in the knowledge_base, and only inside a
crypto-transferability inference in `15_crypto_specific.md` line 97 ("The 'law of large numbers...'
HFT rationale... is general; Chan's historical note... is suggestively applicable to crypto's own
liquid, 24/7 structure") — the underlying section itself is never given as source-faithful content in
any of files 01-14. `01_market_structure.md` (which would be the natural home, given the
liquidity-supplier framing) has zero coverage of market-making/liquidity-provision concepts at all
(confirmed via grep — no matches for "liquidity provi", "market maker", "bid.ask", "order book", "tick
data").

**Where it should live:** `01_market_structure.md` (liquidity provision/market-making framing) and/or
`05_momentum.md` or a new subsection near the Sharpe-ratio material in `14_backtesting_and_validation.md`
(the backtesting/execution-challenge half of the section).

---

## MODERATE

### M1. Order-sizing / market-impact minimization rules (Chan Ch.5) are entirely absent

**Source:** Chan Ch.5, "Minimizing Transaction Costs" (`02_Chapter_05_Execution_Systems.md`, lines
48-54).

**What's missing:**
- The **order-sizing rule of thumb**: limit each order to **≤1% of average daily volume**. Worked
  example given in source: IRN (S&P 600 SmallCap), 3-month average volume ~51,000 shares at $4.45/share
  → 1% of volume = 510 shares = $2,269 notional — illustrating this threshold is easy to hit even as
  an independent trader on small-cap names.
- The **capital-scaling-by-market-cap rule**: capital allocated per stock should scale with the
  **fourth root of market capitalization**, not linearly — because market caps span orders of
  magnitude (tens of millions to hundreds of billions), linear scaling would assign near-zero weight
  to small/microcap names, eliminating diversification. Fourth-root scaling keeps the
  largest-to-smallest weight ratio around 10 (vs. up to ~10,000 under linear scaling).
- The order-splitting/slippage tradeoff (breaking a large order into smaller pieces reduces market
  impact but increases slippage) — explicitly flagged by Chan as "not really suitable for retail
  traders whose order size is usually not big enough to require this remedy."
- Commission-reduction guidance: avoid stocks priced under $5 (institutional convention) — low-priced
  stocks require more shares for a fixed capital amount and tend to have proportionally wider spreads.

None of this appears in `10_position_sizing.md`, `12_portfolio_construction.md`, or
`14_backtesting_and_validation.md` (confirmed via grep for "fourth root", "1% of", "average daily
volume", "market impact", "order sizing" — zero matches in the knowledge_base aside from an unrelated
3%-ADV liquidity constraint sourced to Vince in `12_portfolio_construction.md` line 78).

**Why this matters:** this is directly connected to gap C1 (capacity) — the fourth-root market-cap
weighting rule is Chan's concrete operational answer to "how do you actually size a diversified,
capacity-constrained portfolio without either ignoring small-caps or concentrating dangerously in
them," which is exactly the kind of practical position-sizing detail this knowledge_base otherwise
excels at preserving (see how thoroughly Vince's and Kaufman's analogous sizing rules are captured in
`10_position_sizing.md`).

**Where it should live:** `10_position_sizing.md` (a new subsection alongside the existing
volatility-parity/ATR-sizing material) and/or `12_portfolio_construction.md`.

---

### M2. The "interesting puzzle" — geometric random walk, arithmetic vs. geometric mean — worked illustration is dropped

**Source:** Chan Ch.6, Sidebar/Example 6.1, "An Interesting Puzzle (or Why Risk Is Bad for You)"
(`02_Chapter_06_Money_and_Risk_Management.md`, lines 34-39).

**What's missing:** The specific worked illustration — a stock following a true geometric random walk
(50/50 chance of +1%/−1% each minute) — that a naive trader would guess is "flat" in the long run but
actually **loses money at 0.005% (0.5 basis point) per minute**, because compounded growth rate
`g = m − s²/2`, and since the arithmetic mean m = 0 here, the geometric mean (and thus long-term
growth) must be negative (geometric mean ≤ arithmetic mean, equal only when all values are identical).
The underlying formula and lesson ("risk always decreases long-term growth rate") **are** present in
`10_position_sizing.md` (the `g = r + f·m − s²·f²/2` derivation and the SPY 9.8% vs. 11.23% example are
both there) — but this specific, pedagogically vivid, distinct worked example (which Chan uses
precisely because it's counterintuitive even to sophisticated readers) is not reproduced anywhere. This
is a genuinely good "aha" illustration that's worth keeping distinct from the SPY example, since it
isolates the pure risk-decreases-growth point with m=0 (no confounding with an actual positive-return
asset).

**Where it should live:** `10_position_sizing.md` §2.1 (Chan's Kelly treatment), as a short addition
right after or before the SPY worked example.

---

### M3. Split/dividend price-adjustment mechanics and worked example (Chan Ch.3, Example 3.2) reduced to a one-line cross-reference

**Source:** Chan Ch.3 (`02_Chapter_03_Backtesting.md`, lines 57-64).

**What's missing:** `14_backtesting_and_validation.md` line 531 only says "verify split/dividend
adjustment via multiplier not subtraction (Chan Ch.3...)" — dropping:
- The actual **formulas**: split adjustment = multiply all prices before ex-date T by 1/N (for an N:1
  split); dividend adjustment = multiply all prices before ex-date T by
  `(Close(T-1) − d) / Close(T-1)` for a $d/share dividend.
- The explicit reasoning for why **multiplication** (not subtraction of $d) is correct: it preserves
  historical *daily returns* across the adjustment point, whereas subtraction would preserve daily
  *price changes* but not returns — and multiplication is how Yahoo! Finance (the most common
  convention) does it.
- The explicit warning that unadjusted data shows a spurious price "drop" at the ex-date's open beyond
  normal fluctuation, which can trigger erroneous trading signals.
- **Worked Example 3.2** (IGE ETF): a 2:1 split (multiplier 0.5) combined with 9 subsequent dividends
  (aggregate dividend multiplier 0.976773) yields a combined multiplier of 0.488386 applied to all
  pre-split prices — verified to match Yahoo!'s published adjusted closes to two decimal places.

**Where it should live:** `14_backtesting_and_validation.md`, expanding the existing one-line mention
into a short subsection (this file already has the analogous full worked-example treatment for other
Chan backtesting pitfalls in its §11, so this would be consistent with the file's existing structure).

---

### M4. Chan's Sharpe-ratio vs. absolute-return institutional-bias anecdote (SAC Capital pitch) is dropped

**Source:** Chan Ch.2 (`02_Chapter_02_Fishing_for_Ideas.md`, lines 86).

**What's missing:** Chan's anecdote about pitching a strategy to SAC Capital Advisors ($14B AUM),
whose head of risk management dismissed a high Sharpe ratio in favor of higher absolute returns ("we
can all go buy bigger houses with our bonuses!") — which Chan calls "quite wrong," reasoning that a
higher Sharpe ratio permits higher leverage, and it is the *leveraged* return that ultimately matters.
This is a vivid, specific illustration of the book's single most-repeated point (Sharpe over raw
return drives long-term growth) and is the kind of "Author Insight" the KB elsewhere preserves
carefully (e.g., the "$100k vs $100M account" framing is preserved for Ch.8's capacity thesis in the
Master_Summary but not carried into a topic file — see C1). The underlying *lesson* (Sharpe ratio
drives compounded growth via g=r+S²/2) is well represented in `10_position_sizing.md` and
`13_indicator_reference.md`; only this specific supporting anecdote is missing.

**Where it should live:** `13_indicator_reference.md`'s Sharpe Ratio entry (Chan Ch.2/3/6 section,
around line 448-460), as a one-sentence addition, or `17_author_disagreements.md` if framed as an
industry-practice disagreement (institutional raw-return bias vs. quant Sharpe-ratio preference).

---

## MINOR

### N1. PCA factor-model result reported inconsistently as "−1.81%" vs. "−181%" across two knowledge_base files

Not a source-fidelity gap exactly, but worth flagging for a future editing pass: `08_entries.md` line
333 states the PCA strategy's failure as "average annualized return ≈ **−181%**," while
`16_research_hypotheses.md` line 86 and `13_indicator_reference.md` both state "**−1.81%**." The
source itself (`02_Chapter_07_Special_Topics.md` line 131, `Strategies.md` line 229) is genuinely
ambiguous — Chan's own code comment says "−1.81" without a clear percent/decimal convention, and this
ambiguity is correctly flagged as unresolved in the Chan extraction's own `Strategies.md` ("It is not
stated whether... only the aggregate −1.81 average annualized return figure" is given). Since the
underlying source is ambiguous, this isn't a fidelity failure — but the two KB files should at least
state the same number, or both flag the ambiguity, rather than silently disagreeing with each other.

### N2. Chan's Sidebar "Artificial Intelligence and Stock Picking" (Ch.2) not represented as a distinct item

**Source:** Chan Ch.2 (`02_Chapter_02_Fishing_for_Ideas.md`, lines 135-141).

Chan's explicit skepticism of AI/neural-network/genetic-algorithm stock-picking — his experience that
every AI-based financial model he built "performed well in backtest but miserably going forward," and
his stated criteria for when AI methods HAVE worked for him (sound econometric basis, few parameters,
linear regression only, all optimization within a lookback window continuously validated on
unseen data) — is not captured as a standalone item anywhere. The general Occam's-razor/simplicity
theme is well represented (`17_author_disagreements.md` line 98), but this specific, more actionable
checklist for evaluating an ML-based trading idea is not. Given this project's own research history
includes ML-adjacent strategy attempts, this is a reasonably actionable omission, though minor in
scope relative to C1/C2.

**Where it should live:** `18_common_failure_modes.md` (overfitting section) or `16_research_hypotheses.md`.

### N3. Chan's seasonal-trade year-by-year P&L/drawdown tables (gasoline and natural gas sidebars) reduced to summary-only

**Source:** Chan Ch.7 sidebars (`02_Chapter_07_Special_Topics.md`, lines 211-225).

`07_market_regimes.md` §2.7 correctly preserves the qualitative claims (profitable every year since
1995 for gasoline, 14 consecutive years for natural gas, the "alive and well" framing, and the
data-snooping caveat) but drops the specific year-by-year P&L/max-drawdown figures that make the case
concrete — e.g., 2007 gasoline: +$2,286 P&L but a −$9,816 intra-trade max drawdown (a real
uncomfortable-to-hold-even-when-profitable illustration); natural gas 2003: +$2,000 P&L against
−$5,550 drawdown. Also dropped: the explicit **Amaranth Advisors ($6 billion loss) and Bank of Montreal
($450 million loss)** natural-gas risk warnings that accompany the NG sidebar specifically (Amaranth is
mentioned once elsewhere in the KB, in `06_volatility.md` line 459, in a different context — the
NG-sidebar-specific citation with its explicit "trade the reduced-size mini QG contract" recommendation
is not reproduced).

**Where it should live:** `07_market_regimes.md` §2.7, as a short addition (this file already has the
qualitative claims; adding 2-3 representative year rows plus the Amaranth/BMO warning would round this
out without much space).

### N4. Information Ratio's benchmark-selection guidance dropped

**Source:** Chan Ch.2 (`02_Chapter_02_Fishing_for_Ideas.md`, line 82).

The Information Ratio formula itself is present (`13_indicator_reference.md` line 449), but Chan's
explicit guidance that the benchmark should match the traded universe (Russell 2000/S&P SmallCap for
small-cap strategies, gold spot price for gold-futures strategies — "not always S&P 500") is dropped.
Minor, since the formula and general concept survive, but the practical guidance on *which* benchmark
to choose is exactly the kind of detail a future strategy evaluator would need.

**Where it should live:** `13_indicator_reference.md`, appended to the existing Sharpe/Information
Ratio entry.

---

## Summary

| Severity | Count |
|---|---|
| CRITICAL | 2 |
| MODERATE | 4 |
| MINOR | 4 |
| **Total** | **10** |

**Overall completeness assessment:** Very high fidelity. Of the areas flagged for special attention in
the audit brief — cointegration/CADF/half-life mechanics, the backtesting-bias taxonomy, Kelly/half-
Kelly and the fat-tail leverage cap, the two overleveraging anecdotes, the PCA and seasonal negative
results, and Chan's own Author Insights/Warnings/Open Questions — every single one is present in the
knowledge_base with correct source numbers and correctly preserved as negative results where
applicable (the PCA and Heston-Sadka failures are explicitly NOT presented as endorsements anywhere I
checked). The two CRITICAL gaps (Ch.8's capacity thesis, and the Ch.7 high-frequency-trading section)
are both genuinely load-bearing pieces of the book's own argument that didn't make the cut into any
topic file — not obscure asides. The MODERATE and MINOR findings are the kind of worked-example/detail
attrition that's expected and acceptable in a consolidation exercise of this scale, not evidence of
carelessness. Execution-systems and business-setup chapters (Ch.1, Ch.4, most of Ch.5) are correctly
and deliberately out of scope per the knowledge_base's own documented purpose.
