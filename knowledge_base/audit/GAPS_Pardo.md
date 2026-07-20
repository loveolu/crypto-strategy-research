# Gap Audit: Pardo, *The Evaluation and Optimization of Trading Strategies* vs. `knowledge_base/`

Audited by reading the full Pardo extraction (`Knowledge/Pardo_Evaluation_and_Optimization_of_Trading_Strategies/` — all 14 chapter files plus Strategies/Indicators/Concepts/Risk_Management/Research_Ideas/Algorithmic_Trading/Crypto_Specific/Psychology/Glossary/Master_Summary) as ground truth, then checking coverage across all 18 `knowledge_base/*.md` topic files plus README.md.

**Headline finding**: coverage is unusually strong. `14_backtesting_and_validation.md` in particular reproduces Pardo's WFA chapter (Ch.11), overfitting chapter (Ch.13), and optimization chapters (Ch.9-10) at near-full fidelity, including exact worked numbers, formulas, and the Ch.6/Ch.11 walk-forward-ratio inconsistency (explicitly preserved, not resolved). `Risk_Management.md`'s capital formulas, `Psychology.md`'s System X/Y example, and the Glossary's ~80 terms are also well distributed across the relevant topic files. The gaps below are the genuine exceptions found after checking every chapter and every cross-cutting file against the 18 topic files.

---

## CRITICAL

### C1. Pardo's Kelly / Optimal-f formula and worked example are absent from `10_position_sizing.md`
- **Source**: Pardo Ch.5 (`02_Chapter_05_The_Elements_of_Strategy_Design.md`, "Advanced Strategies"), also `Risk_Management.md` and `Concepts.md`.
- **Target**: `knowledge_base/10_position_sizing.md`, §2 ("Kelly Criterion — Three Treatments").
- **Gap**: §2 opens "The Kelly criterion appears independently in Vince, Chan, and Kaufman" — Pardo is not mentioned anywhere in the Kelly section, despite Pardo giving his own named formula and worked example:
  - `Kelly % = (Win % − Loss %) / (Average Profit / Average Loss)`
  - Worked example: 55% win rate, avg win $1,750, avg loss $1,250 → Kelly% = (55−45)/(1750/1250) = 10/1.4 = **7.14%**; applied to a $250,000 account at $1,000 risk/contract → **17 contracts**.
  - Pardo explicitly attributes "Optimal f (fixed fractional trading)" to **Ralph Vince (1990)**, itself derived from the Kelly criterion via Edward Thorpe's gambling application — a genuine cross-book connection (Pardo citing Vince, the other source book in this same knowledge base) that is currently invisible to a reader of `10_position_sizing.md`.
  - Pardo's explicit caveat (also missing): because win rate/avg win/avg loss are themselves statistically "fuzzy" (small-sample, high-variance inputs), the resulting Kelly/Optimal-f percentage inherits meaningful inaccuracy — this is a distinct, source-specific framing of the general "Kelly inputs are noisy" theme already present for Vince/Chan and should be added as a third, independently-arrived-at instance of the same warning.
- **Why CRITICAL**: this is a named formula with a full worked numeric example from a primary source chapter (Ch.5) on a topic (position sizing) that has its own dedicated knowledge_base file — the exact kind of content this audit was asked to check for, and it is not a subtle omission (the section's own topic sentence enumerates three authors and skips a fourth who is directly on-topic).

### C2. Pardo's volatility-adjusted position-sizing formula is absent from `10_position_sizing.md`
- **Source**: Pardo Ch.5, `Risk_Management.md`.
- **Target**: `knowledge_base/10_position_sizing.md`.
- **Gap**: Formula `contracts = (fixed % of equity to risk) / (dollar risk per contract)`, worked example: 3% risk on $250,000 = $7,500; risk/contract = $1,000 → **7 contracts** (7.5 rounded down). This is Pardo's baseline sizing method (named ahead of Martingale/Anti-Martingale/Kelly in his own Ch.5 taxonomy) and is not reproduced anywhere in the position-sizing file, even though the file's §8 does cover Pardo's Martingale/Anti-Martingale mentions in detail (§8.7). Add alongside the existing volatility-based-sizing material (which currently draws only from Vince/Kaufman/Chan) as a fourth, simpler, independently-stated version of the same "size by fixed % equity risk ÷ per-unit dollar risk" principle.

### C3. Scaling into / out of a position (Pardo Ch.5) is absent from both `09_exits.md` and `10_position_sizing.md`
- **Source**: Pardo Ch.5, `Risk_Management.md`, `Glossary.md`.
- **Target**: `knowledge_base/09_exits.md` (§8, "Pardo's Exit Design and Trade Management") or `10_position_sizing.md`.
- **Gap**: Two named, defined techniques with worked examples are missing entirely:
  - **Scaling into a position**: "adds incrementally to an existing position as the market moves in the profitable direction of the trade" — example: add 1 unit per additional $1,000 of open profit.
  - **Scaling out of a position**: "incrementally decreases an existing position [as it moves favorably]" — example: remove 1 unit per additional $1,000 of open profit.
  - **Combined worked example**: scale in +1 unit per $1,000 gained up to a $5,000 cap on the oldest lot, then scale out −1 unit per additional $1,000 gained thereafter.
  - Pardo notes this is more commonly a discretionary-trader technique but states it is equally implementable in an automated strategy — a nuance worth preserving.
  - Note: `10_position_sizing.md`'s own cross-reference footer (final section) points to `09_exits.md` for "scaling in/out," but `09_exits.md` does not actually contain this content — a genuine hole between the two files' mutual cross-references, not just a missing topic.

---

## MODERATE

### M1. Pardo's dollar/volatility trailing-stop and profit-target worked numeric examples are claimed as "reproduced" but are not actually present in `09_exits.md`
- **Source**: Pardo Ch.5, `Risk_Management.md`.
- **Target**: `knowledge_base/09_exits.md`, §8 (line ~263): "Trailing stops and profit targets, both given full definitions and worked numeric examples reproduced in §1 and §4 above."
- **Gap**: This sentence overstates what §1 (Stop-Loss Taxonomy) and §4 (ATR Stops) actually contain. Checked both sections directly — they contain Pardo's *risk-stop* worked examples (dollar/volatility/percent-of-equity — correctly present) but NOT the profit-management-side worked examples:
  - **Trailing dollar profit stop**: $1,000 (2 pts) trail; long at 350, high reaches 356 → trailing stop = 354, locking ~$2,000.
  - **Trailing volatility profit stop**: 50% of a 3-day avg range (5.50 pts) = 2.75 pts trail; long at 350, high 356 → stop 353.25, locking ~$1,625.
  - **Dollar profit target**: $1,000 (2 pts) target; short at 350.00 → buy target at 348.00.
  - **Volatility profit target**: 150% of a 3-day avg range (5.50 pts) = 8.25 pts; long at 350.00 → sell target 358.25 (~$4,125 gross).
  - Fix: either add these four worked examples where the cross-reference claims they live, or correct the cross-reference sentence to not claim numeric examples that aren't there.

### M2. Chapter 8's worked multimarket/multiperiod TEST comparison (MA 5×20 vs. RSIct vs. XTct) is referenced only abstractly, without its actual numbers
- **Source**: Pardo Ch.8 (`02_Chapter_08_Preliminary_Testing.md`, "The Test / Results"), also `Strategies.md`.
- **Target**: `knowledge_base/14_backtesting_and_validation.md`, §8 opening line ("By this point a strategy is presumed to have passed the multimarket/multiperiod test...").
- **Gap**: This is Pardo's single clearest illustrative example of the multimarket/multiperiod screening philosophy — 5 markets (coffee, crude oil, S&P, T-bonds, yen) × 5 two-year segments (1997–2006) × one fixed parameter set = 25 simulations, run for three strategies:
  - MA 5×20 crossover: total **+$66,301** but with large losses in individual cells (e.g., −$57,175 on S&P 2001–2002) — "questionable results."
  - RSIct: total **+$333,489**, positive in nearly every cell — "typical to good results."
  - XTct: total **+$865,688**, strongly positive nearly everywhere — "excellent results."
  - This worked comparison is the concrete anchor for the abstract "excellent/deplorable/mixed" decision framework that the topic files do state, but the numbers themselves (and the three-tier qualitative labels attached to them) are not reproduced anywhere in the knowledge base. This is exactly the kind of "worked numeric example" the audit brief flagged as high-priority (Pardo's book is full of these). Suggested target: a new subsection in `14_backtesting_and_validation.md` §2 or a new §2.x ("The Multimarket/Multiperiod Test, Worked") alongside the existing multimarket/multiperiod *optimization* worked example (§5.6, which IS present with its own numbers).

### M3. Pardo's Efficient Market Hypothesis discussion (Ch.6) is entirely absent
- **Source**: Pardo Ch.6, `Concepts.md` (EMH entry).
- **Target**: `knowledge_base/01_market_structure.md` or `07_market_regimes.md` (both already carry Kaufman's separate, unrelated EMH mention re: price-shock reactions).
- **Gap**: Pardo's own EMH discussion is a distinct, unreproduced strand: EMH attributed to Eugene Fama; Pardo's stated position that EMH "is no longer accepted as an accurate theory of market action" by "many" (his own characterization, not a citation); his own nuanced view that markets ARE efficient to a meaningful degree but not perfectly/omnisciently so, with inefficiencies continuously discovered, exploited, and erased in an ongoing cycle; and the **Myron Scholes/LTCM anecdote** ("The fund will succeed... because of fools like you," re: LTCM) used as a cautionary tale about overconfidence in exploiting perceived market inefficiency. This is a different EMH treatment from Kaufman's (which the knowledge base does capture, re: price-shock reaction lag) and should be added as its own tagged entry, not merged into Kaufman's.

### M4. Kelly-formula chapter-comparison table implicitly undercounts sources
- **Source**: Cross-cutting (Pardo Ch.5 + Vince + Chan + Kaufman).
- **Target**: `knowledge_base/10_position_sizing.md`, §2's synthesis paragraphs (e.g., "All three agree that Kelly/optimal-f is a ceiling, not a target").
- **Gap**: Once C1 above is fixed, the "all three... Vince's fractional f, Chan's half-Kelly, Kaufman's citation" synthesis language should be revisited to state whether Pardo's Kelly treatment agrees with the same "ceiling, not target" framing (Pardo does not explicitly say this — he only flags the input-fuzziness caveat) — a small follow-on correction once C1 is addressed, noted here so it isn't dropped in a future edit pass.

---

## MINOR

### N1. Chapter 4 (The Strategy Development Platform) content is not represented in any topic file
- **Source**: Pardo Ch.4 — platform feature requirements (scripting, diagnostics, reporting, optimization tooling, speed, automation, WFA-as-a-platform-feature, portfolio analysis).
- **Target**: Arguably out of scope for this knowledge base (it's about software/tooling requirements, not trading methodology per se), but `Algorithmic_Trading.md`'s own "Automation" section (Ch.4) is partially reflected in `14_backtesting_and_validation.md` §5 (automation is mentioned in passing under WFA workflow) — the fuller platform-feature checklist (diagnostics tools like PaintBars/Show Me studies, reporting-format standards, the "objective function" cross-reference) is not reproduced. Likely a deliberate, reasonable scope decision (this is a trading-knowledge base, not a software-selection guide) — flagged as MINOR/optional rather than a real gap.

### N2. Chapter 7's Joe Trader/Alex Programmer dialogue and the 4-form MA specification example are not represented
- **Source**: Pardo Ch.7 (`02_Chapter_07_Formulation_and_Specification.md`).
- **Target**: None of the 18 topic files cover strategy-specification/scripting pedagogy.
- **Gap**: The illustrative "vague idea → precise pseudocode → formal IF/THEN → C code → EasyLanguage/Metastock/TradersStudio" pipeline, and the fictional interview technique for surfacing hidden inconsistency in a trader's mental model of their own strategy, are absent. This is process/pedagogy content (how to specify a strategy precisely) rather than trading-methodology content, so its absence is a reasonable, low-priority scope decision — but if a future "strategy specification discipline" angle is ever added to the knowledge base (e.g., as part of `14_backtesting_and_validation.md`'s pipeline stage list), this dialogue is the source's most concrete illustration of "incomplete specification is one of the most common mistakes."

### N3. PTIx trade-list/report-format example (Ch.6) not reproduced
- **Source**: Pardo Ch.6, `Strategies.md`.
- **Gap**: The specific PTIx report walkthrough (S&P 1989–2006, net profit $338,625, MDD $149,100, 218 trades, 66.9% win rate, PF 1.62, plus a sample trade-list line) is used by Pardo purely to illustrate report *format*, not strategy content. `14_backtesting_and_validation.md` §2.1 already reproduces the PTIx headline numbers correctly. The individual trade-list line items are not reproduced, which is appropriate — low value, correctly triaged as omittable.

### N4. The Turtle Trading Strategy secondhand-failure anecdote (Richard Dennis via Art Collins) is present but the two separate citations of it (Ch.2 and Ch.6) are merged into one mention
- **Source**: Pardo Ch.2 and Ch.6 both reference "the Turtle Trading system no longer works" (Dennis, reported by Art Collins), with Ch.6 adding the point that Turtle-derived variants reportedly produced "hundreds of millions of dollars" during the years the method did work.
- **Target**: `knowledge_base/02_trend_following.md` (line ~776, confirmed present) and `14_backtesting_and_validation.md` §3.3 (Window Size and Model Life, which references the Dennis comment in the "operating assumption" paragraph — confirmed present).
- **Gap**: Both mentions independently exist and are each individually adequate; the "hundreds of millions of dollars during the years it worked" clause specifically (from Ch.6) is not present in either location. Trivial, noted for completeness only.

### N5. A handful of Glossary terms have no direct entry anywhere in the 18 topic files (spot-checked)
- **Source**: `Glossary.md`.
- **Terms checked and found unreproduced verbatim, though the underlying concept is present**: *Individual (in a genetic algorithm)*, *Postoptimization performance* (as a distinct synonym label — the concept "out-of-sample = postoptimization" is present but the glossary-style synonym note is not), *Window* (as a general umbrella term covering Test/Optimization/Walk-forward/Step windows — each specific window type IS covered, just not the umbrella glossary note tying them together).
- **Assessment**: these are genuinely minor — glossary-style terminological completeness, not missing substantive content. Not worth a dedicated editing pass on their own; would only be worth fixing if a future pass adds a consolidated cross-book glossary file to the knowledge base (none currently exists at the topic-file layer).

---

## Areas checked and found ADEQUATE (no material gap — noted briefly per the "don't invent gaps" instruction)

- **Walk-Forward Analysis (Ch.11)**: full mechanics, WFE formula and benchmarks, the RSI CT single-walk-forward example (WFE 341%), the full 30-window WFA case study (19/30 profitable, WFE 135%, all worked numbers), Theory of Relevant Data, and — importantly — the Ch.6-vs-Ch.11 window-ratio inconsistency is explicitly preserved (not silently resolved) in `14_backtesting_and_validation.md` §7.3 exactly as the audit brief asked to verify.
- **The Many Faces of Overfitting (Ch.13)**: all five causes, both parables (forecasting-model and trading-model, including the escalating $10K→$25K→$65K→−$15K trading-model narrative), DoF/start-up-overhead worked math, and the abuse-of-hindsight framework are all present in `14_backtesting_and_validation.md` §9 at high fidelity.
- **PROM, CECPP, Perfect Profit, Model Efficiency**: all four formulas and their worked examples are present in `14_backtesting_and_validation.md` §5.2 and §6.4.
- **Risk-stop taxonomy (dollar/volatility/percent-of-equity) incl. Gann's "Rule of Ten"**: present with full worked numbers in `09_exits.md` §1 and cross-referenced correctly.
- **Required Capital / RAR / RRR / Strategy Stop-Loss formulas**: present with worked numbers across `11_risk_management.md` §3.2, §6.2, §9.1.
- **Psychology (System X/Y worked example, fear/greed/self-doubt mechanics, trader interference)**: present in `18_common_failure_modes.md` §10 at high fidelity.
- **Four market types (bull/bear/cyclic/congested) with regression-slope heuristics**: present in `14_backtesting_and_validation.md` §3.2.
- **Search methods (grid/step/hill-climbing/GA/SA/PSO)**: present in full in `14_backtesting_and_validation.md` §5.1, cross-corroborated against Kaufman.
- **Degrees of freedom, standard error, start-up overhead**: present with all worked numeric examples in `14_backtesting_and_validation.md` §3.1 and §9.5.1.
- **Big Fish in a Small Pond Syndrome**: present in `14_backtesting_and_validation.md` §9.5.4.
- **Mandelbrot/fractal MDD caveat**: present in `11_risk_management.md` §3.2 exactly as the audit brief flagged it should be verified.
- **Robustness — statistical significance / distribution / shape of the optimization profile, incl. the neighbor-averaging worked example**: present in full in `14_backtesting_and_validation.md` §6.1–6.3.
- **Crypto-Specific scope decision**: `15_crypto_specific.md` correctly documents Pardo as pre-crypto with no crypto content — per the task instructions, this is a documented deliberate scope decision, not a gap.

---

## Summary

**Total findings**: 3 CRITICAL, 4 MODERATE, 5 MINOR (12 total).

**Overall completeness assessment**: the knowledge_base captures Pardo's book at very high fidelity overall — genuinely one of the most thoroughly reproduced sources in this knowledge base by volume and by preservation of exact wording, formulas, and worked numbers. The book's two centerpiece chapters (Ch.11 Walk-Forward Analysis, Ch.13 The Many Faces of Overfitting) are reproduced at effectively ~95%+ depth in `14_backtesting_and_validation.md`, including the deliberately-preserved Ch.6/Ch.11 walk-forward-ratio inconsistency. The gaps that do exist cluster almost entirely in one place: **Chapter 5's position-sizing and profit-management formulas** (Kelly/Optimal-f, volatility-adjusted sizing, scaling in/out, and the trailing-stop/profit-target dollar examples) did not make it into `10_position_sizing.md` or `09_exits.md` even though those are exactly the two files built to hold this content, and even though the risk-stop half of the same Ch.5 material (dollar/volatility/percent-of-equity risk stops) DID make it into `09_exits.md` correctly — suggesting an uneven extraction pass through Ch.5 rather than a systemic problem. Estimated depth: ~90% of Pardo's Ch.5 (Elements of Strategy Design) content made it into the knowledge base, with the missing ~10% concentrated specifically in position-sizing/scaling formulas; ~97%+ of Ch.9-13 (the optimization/WFA/overfitting core) made it in; Ch.4 and Ch.7 (platform/specification pedagogy, ~0% represented) are reasonable, low-priority scope exclusions rather than true gaps.
