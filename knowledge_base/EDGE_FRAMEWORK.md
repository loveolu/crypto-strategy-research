# EDGE_FRAMEWORK — The Philosophical Foundation of This Research System

This file is not another topic reference. It sits alongside `01_market_structure.md` through
`18_common_failure_modes.md` (which catalog *what the books say*, indicator by indicator, failure
mode by failure mode) and alongside `hypothesis_bank.md` / `implementation_patterns.md` (which
catalog *specific tradable ideas* and *how to implement them*), but this file answers a different
question: **how should a researcher — human or AI — think about the problem of finding a trading
edge at all?**

It is deliberately short relative to the other 19 files. Every claim here is either tagged to a
specific book/chapter or tagged to this project's own empirical record
(`research/research_index.md`, `research/strategy_research_notes.md`). Where the two disagree, or where the project's
own results complicate a book's claim, that tension is stated explicitly rather than resolved by
picking a side.

---

## 1. What creates a durable trading edge

The five books do not agree on *where* edge comes from, but they converge, from independent
starting points, on what a durable edge is *not*: it is not superior prediction of short-term price
direction. Each book locates durability somewhere else:

- **Kaufman**: edge is *regime-avoidance*, not prediction. Trend-following works "because of fat
  tails" — a few large outlier moves pay for many small losses (Kaufman Ch.8) — and the discipline
  of staying out of the wrong regime, not forecasting the next bar, is what a trend system actually
  buys you. His stronger, more explicit claim: mechanical rules survive precisely because they are
  not trying to predict, only to avoid holding through the type of move the system is not built for
  (Kaufman Ch.9, Ch.22).
- **Pardo**: durability is a property of *robustness*, not peak performance. A strategy profitable
  across a broad, contiguous range of parameters/markets/conditions is preferred over one with a
  single spectacular but isolated result (Pardo Ch.10, Ch.13) — edge that only appears at one exact
  parameter setting is evidence of curve-fitting, not of a real, durable mechanism.
- **Chan**: durability is a *structural/capacity* argument, not a skill argument. Chan's Chapter 8
  central thesis is that the retail-scale trader's edge is being small enough to trade strategies too
  low-capacity for institutional money to bother with — the edge is a market-structure gap, not
  superior insight into price.
- **Vince**: durability is contingent on *survival*. His entire book's premise is that a system with
  even a marginal, real positive expectation is worthless if position sizing produces ruin before the
  edge can compound (Vince Ch.1-2) — an edge is not durable unless the money-management layer keeps
  the trader in the game long enough for it to express itself.

**This project's own empirical history is a direct test of the Kaufman thesis, run on crypto data
that none of the five books ever touched.** Across 96 tested constructs (`research/research_index.md`
hypotheses #1-14; `research/strategy_research_notes.md` §2), every signal-*prediction* family — EMA/RSI/volume
trend, pullback-in-trend, mean reversion, breakout-retest, TTM squeeze, funding-rate/basis proxies,
overnight/time-of-day breakout, 61 further indicator/ensemble/oscillator variants, Supertrend/
Chandelier/dominance-rotation/z-fade blends, and a CFTC positioning filter — failed out-of-sample.
The **only** construct that produced positive Sharpe on 9 of 9 untuned assets was a regime-avoidance
gate (close>SMA200 & ROC30>0 & EMA20>EMA50), stacked with volatility-target position sizing
(TrendVolTarget; `research/research_index.md` hypothesis #9-10). That is Kaufman's thesis confirmed
independently, on an asset class and data source his book never saw.

But the project's own numbers immediately complicate any triumphant reading of that confirmation.
TrendVolTarget's Deflated Sharpe Ratio, computed at the project's own honest cumulative trial count
(n_trials≈95), is **0.64-0.67** — meaning roughly a 64% probability the edge is real rather than
selection artifact, against this project's own required bar of 0.95 (`research/research_index.md`, "Current
best strategy"; DSR audit, MEMORY.md 2026-07-02). **An edge durable in KIND (regime avoidance, not
prediction) is not automatically durable — or even established — in STRENGTH.** The mechanism
Kaufman, Pardo, Chan, and Vince converge on philosophically is the only mechanism that survived this
project's own gauntlet, which is a real and non-trivial corroboration of the books' shared instinct.
It is simultaneously true that this project has not yet cleared its own statistical bar for calling
that survival "proven." Both statements hold at once; this file will not soften either one to make
the other sound better.

---

## 2. Why most strategies fail

At the level of mechanism (not the exhaustive list — see `18_common_failure_modes.md` for that), the
five books describe the same handful of failure modes wearing different names:

1. **Overfitting** — fitting parameters to noise rather than to a real, economically-grounded
   pattern. Pardo's taxonomy (insufficient degrees of freedom, inadequate sample, overparameterization/
   overscanning, "big fish in a small pond," absence of walk-forward testing — Pardo Ch.13) is the
   most systematic version of this; Kaufman's kurtosis>6-8 alarm and Chan's data-snooping-management
   framework describe the identical underlying failure from different angles.
2. **Regime shift** — a strategy validated in one market environment silently stops working when the
   environment changes, with no reliable way to *prove* the cause was regime shift versus ordinary
   variance (Chan Ch.5, Ch.8 — decimalization 2001, uptick-rule elimination 2007; explicitly stated
   as an unresolved detection gap).
3. **Fee/cost erosion** — transaction costs reversing a strategy's sign, not merely shrinking its
   magnitude. This is the single most repeated *empirical* finding across the books that model costs
   explicitly (Hilpisch Ch.4/6/10; Chan Ch.3 Examples 3.7-3.8; Pardo Ch.6's 200-trade/1-year contrast
   flipping to a net loss) — four independent datasets, the same structural result
   (`14_backtesting_and_validation.md` §14.6).
4. **Small-sample illusion** — mistaking a handful of trades, or a handful of outsized winners, for a
   statistically established edge (Pardo's standard-error tables; Chan's effective-vs-nominal sample
   size trap; Vince's asymmetric Type-I/Type-II framing).
5. **Peak-parameter fragility** — trusting the single best-scoring backtest instead of the average
   performance across a neighborhood of similar parameters (Pardo's neighbor-averaging technique;
   Kaufman's "average of all tests, not the peak test" — the single most repeated conclusion in his
   Ch.21).

**This project's own 85+ rejected constructs are a real-world demonstration of every one of these
failure modes, not a hypothetical illustration.** The 61-strategy autonomous search
(`research/research_index.md` hypothesis #8) found a Sharpe ceiling of ~1.2 on retail daily OHLCV and zero
survivors — not because the search was poorly executed, but because (per the project's own
diagnosis) "the pipeline is not broken; the edges aren't there" (`research/strategy_research_notes.md` §2.1).
The intraday hours 21-22 UTC anomaly (`research/research_index.md` hypothesis #12) is a rare case where a
*real, statistically stable* effect (t=2.4-3.0) was found and still rejected — fees exceeded the edge
25:1. That single result is worth dwelling on: it demonstrates failure mode #3 (fee erosion) in its
purest form, isolated from any question of whether the underlying signal was genuine. The signal was
genuine. It still could not be traded.

---

## 3. Principles that appear consistently across multiple books

Per `17_author_disagreements.md`'s "where they agree" framing and
`14_backtesting_and_validation.md` §14, these convergences are treated as load-bearing precisely
*because* the five books were written across a 28-year span by authors in different corners of the
industry with essentially no cross-citation:

1. **Plateaus over peaks.** Pardo's smooth-hilltop-vs-spiky-peak framework and Kaufman's
   "average of all tests... better than... average of all tests" restatement independently conclude
   the same thing: trust a broad, contiguous profitable region, not an isolated best result
   (Pardo Ch.10; Kaufman Ch.21).
2. **One-shot validation discipline.** Both Pardo and Kaufman independently warn against re-running
   walk-forward/step-forward analysis iteratively during development — Kaufman names this failure
   mode "Feedback": re-running the whole process after any tweak means there is, strictly, no true
   out-of-sample data left (Pardo Ch.11, Ch.13; Kaufman Ch.21).
3. **A ~30-trade minimum sample, converged on independently.** Pardo's standard-error arithmetic,
   Chan's `252×parameters` rule, and Vince's 30-trade Runs Test floor are three differently-derived
   numeric thresholds pointing at the same underlying statistical-power concern.
4. **Degrees of freedom / parameter count as a front-loaded, performance-independent overfitting
   check.** Pardo's `Rdf%` formula, Chan's ≤5-parameter rule, and Vince's "don't restrict degrees of
   freedom" guiding principle all treat parameter count as testable *before* looking at any backtest
   number at all.
5. **A sample-size-aware objective function**, converged on without a shared formula: Pardo's PROM
   (which shrinks its own "pessimism penalty" as trade count grows) and Kaufman's "returns adjusted
   for sample error" independently reject raw net profit as a ranking criterion.
6. **Optimal-f (or Kelly) as a ceiling, not a target.** Vince derives the mathematically optimal
   sizing fraction and treats deviation from it as an explicit *psychological* concession
   (fractional-f); Chan caps at half-Kelly plus a fat-tail correction; Kaufman treats the whole
   optimal-f apparatus as a sanity-check ceiling to stay well below, citing Elder's "never trade full
   optimal f." All three treat the underlying mathematics as valid and diverge only on how much
   safety margin to build in by default (`17_author_disagreements.md` §1).
7. **Transaction costs can flip a strategy's sign**, independently demonstrated with four unrelated
   datasets and methodologies (see §2.3 above).

This project's own validator.py pipeline (70/15/15 split + walk-forward + Monte Carlo + DSR gate) was
built *before* this book-extraction project began and independently converged on the same structure
as Kaufman's 60/20/20 in-sample/validation/out-of-sample convention and Pardo's WFA-as-final-gate
philosophy (`research/strategy_research_notes.md` §1, §5.4). That convergence is itself a small piece of
evidence for principle #1-2 above: multiple independent design processes (five authors, one
project's own methodology built from first principles) landed on structurally the same validation
discipline.

---

## 4. Which ideas have the strongest empirical support — three tiers of evidence

Future researchers using this knowledge base should keep three tiers of evidentiary strength
explicit, because collapsing them is the single easiest way to overstate what is actually known:

**Tier 1 — All five books converge on independently.** These are the strongest claims *in the
literature*: plateau-over-peak reporting, one-shot walk-forward discipline, a ~30-trade sample
floor, parameter-count as a front-loaded check, sample-size-aware objective functions, transaction
costs as sign-reversing, and optimal-f/Kelly as an upper bound (§3 above). No book here validates
these on crypto data — all five predate or ignore crypto almost entirely (Pardo 2008, Chan 2009,
Kaufman's 2019 edition has exactly three incidental Bitcoin mentions in 2,285 pages, Hilpisch's crypto
touchpoints are four incidental CFD-instrument mentions, Vince predates crypto by decades). **"Five
books agree" is evidence about testing methodology in general, not evidence that any specific
strategy works on crypto.**

**Tier 2 — A single book's claim, unconfirmed elsewhere.** E.g., Chan's specific ≤5-parameter rule of
thumb, Kaufman's 6-8% volatility-target range, Pardo's exact PROM formula. These carry the authority
of one author's experience and stated reasoning, not independent corroboration. Treat them as
informed opinion worth testing, not as established fact.

**Tier 3 — Empirically confirmed or refuted on THIS project's own crypto data.** This is the only
tier with direct evidentiary weight for crypto trading decisions made in this repository, and it is
sparse:
- *Confirmed*: regime-avoidance (not prediction) is the only strategy family with any OOS
  survival (`research/research_index.md` hypothesis #9-10) — directly testing Tier-1-adjacent Kaufman claims
  and finding them to hold, at least in kind.
  Volatility-target sizing is the only overlay found to improve risk without hurting Sharpe
  (`research/strategy_research_notes.md` §2.3) — directly testing the Vince/Kaufman/Chan sizing-matters thesis
  and finding it to hold.
  Fees reliably kill intraday/high-frequency variants on this data (`research/strategy_research_notes.md`
  §2.4) — directly confirming Tier-1 finding #7 above on crypto specifically.
- *Refuted or unconfirmed*: mean reversion has never worked on this project's crypto data at any
  timeframe tested (`research/strategy_research_notes.md` §4) — a genuine tension with Chan's stat-arb-centered
  book (see §5 below). Equities-style overnight/calendar anomalies (Zarattini-style) do not transfer
  to 24/7 crypto (`research/research_index.md` hypothesis #6, `research/strategy_research_notes.md` §3, "RESOLVED —
  closed"). Kaufman's 6-8% vol-target guidance has not been reconciled with this project's 40% target
  — flagged open, not resolved (see §5).

A claim appearing in a book is a hypothesis worth testing on this project's own data. A claim
confirmed in Tier 3 is the only kind of claim this project can currently act on with any confidence,
and even the strongest Tier-3 confirmation (regime avoidance) carries a DSR of only 0.64 — Tier 3
membership is necessary, not sufficient, for confidence.

---

## 5. Which ideas are controversial or unresolved

Documented in full in `17_author_disagreements.md`; the ones with direct bearing on this project's
own decisions:

- **Kelly/Optimal-f framing.** Vince presents the mathematically optimal fraction and treats
  deviation as a psychological concession; Chan caps at half-Kelly with an explicit fat-tail
  correction (a mathematical, not merely psychological, adjustment); Kaufman treats the whole
  apparatus as a ceiling to stay well below by default. All three agree on the underlying math and
  disagree only on how much margin to build in and why (`17_author_disagreements.md` §1). This
  project's position sizing (vol-target, not Kelly-derived) sits far below any of the three authors'
  practical recommendations — consensus, not controversy, on this specific point
  (`research/strategy_research_notes.md` §3, "RESOLVED").
- **Volatility-target level: 40% vs. 6-8%, genuinely unresolved.** Kaufman's stated practical range
  (6% minimum, 8% typical, 16%+ "dangerous") is drawn entirely from traditional futures/equities/FX
  and sits dramatically below TrendVolTarget's 40% crypto vol-target. Neither this project nor
  Kaufman's book resolves whether crypto's structurally higher baseline volatility genuinely
  justifies a proportionally higher target, or whether the crypto-side figure should be re-examined
  against the traditional-market benchmark as a sanity check (`17_author_disagreements.md` §2;
  `research/research_index.md`, open hypothesis #3). **This is flagged, not resolved, in both the book
  extraction and the project's own notes — any future researcher treating 40% as self-evidently
  correct because "crypto is more volatile" is going beyond what either source has actually
  established.**
- **Walk-forward-as-near-silver-bullet (Pardo) vs. average-of-tests-as-primary-signal (Kaufman) vs.
  no-WFA-at-all (Hilpisch).** Three genuinely different postures toward the same underlying problem,
  not a resolved consensus (`17_author_disagreements.md` §4). This project's own pipeline uses both
  a walk-forward split and average/DSR-style statistical correction, effectively hedging between
  Pardo's and Kaufman's positions rather than adjudicating between them.
- **Discretion vs. full automation.** Chan and Pardo respect discretionary trading's ceiling
  ("no systematic strategy has yet matched" the best discretionary traders, per Chan) while still
  building systematic frameworks on the premise that automation outperforms manual override for the
  target reader; Kaufman scopes psychology/discretion out entirely; Vince explicitly disclaims any
  ability to improve trading judgment at all, treating it as a separate, non-substitutable
  competency (`17_author_disagreements.md` §7). This project is fully systematic/backtest-driven by
  construction — it has not tested, and cannot speak to, whether a disciplined discretionary overlay
  would outperform.
- **Trend-following's "always recovers" claim, in live tension with 2024-26 project data.** Kaufman's
  long-horizon futures evidence treats trend-following as durable across decades; this project's own
  2024-2026 crypto segment shows all tested trend variants at test-split Sharpe 0.1-0.4
  (`research/strategy_research_notes.md` §3, "OPEN"). The project's own honest assessment: this could be an
  ordinary trend drought (consistent with Kaufman) or a structural regime change (ETF-era crypto
  market microstructure) that Kaufman's traditional-market evidence has no way to speak to. This is
  explicitly unresolved, and only forward (not backtested) data can resolve it.

---

## 6. What future researchers should prioritize when evaluating a new hypothesis

In rough priority order, synthesizing the Tier-1 book convergences (§3-4) with what this project's
own 96-trial history shows actually discriminated a survivor from a failure:

1. **Mechanism plausibility over pure curve fit.** Ask "why would this be true" before "does this
   backtest well" — Kaufman's "testing is misguided when it is used to discover a trading method"
   (Ch.1) and this project's own experience that indicator/ensemble sweeps with no prior mechanism
   found nothing (`research/research_index.md` hypothesis #8) both point here first.
2. **Cross-asset / cross-regime transfer.** Does it hold on untuned assets it wasn't fit to?
   TrendVolTarget's positive Sharpe on 9/9 untuned assets is this project's own clearest positive
   signal to date; every rejected construct failed this test, this project's OOS split, or both.
3. **Walk-forward / test-split positivity, not full-window performance.** This project's own
   standing rule: "judge on TEST-set / walk-forward numbers only. Full-window Sharpe runs 2-4x
   inflated here" (`research/research_index.md`, "Standing constraints") — a rule this file's own citations
   above (TrendVolTarget: full-window Sharpe 1.26 vs. test-split 0.41) demonstrate is not academic.
4. **DSR at current cumulative n_trials, not in isolation.** A hypothesis's own backtest Sharpe means
   little without discounting for how many prior hypotheses were tested against the same data
   (`research/research_index.md`: n_trials≈95 and rising with every new test — "more grinding on the same
   data is provably counterproductive").
5. **Robustness / plateau behavior**, not peak-parameter performance — per §3 above, check whether
   nearby parameter settings perform similarly before trusting the reported optimum.
6. **Sample size adequacy** for the strategy's own trading frequency — Pardo's standard-error
   arithmetic and this project's own N-too-small rejections (overnight breakout: 5-10 trades in 3-5
   years, `research/research_index.md` hypothesis #6) both apply directly.
7. **Cost/fee realism**, checked before any other judgment is made — this project's own hours
   21-22 UTC finding (real signal, 25:1 fee-to-edge ratio, untradeable) is the sharpest demonstration
   in this project's history that a statistically genuine effect and a tradeable strategy are not the
   same thing.
8. **A genuinely new data axis or mechanism**, not a parameter variation of an already-tested family.
   This project's own standing rule as of its most recent research-index update: "if any new
   hypothesis is proposed: it must use a genuinely new data dimension or a structurally different
   mechanism — parameter variations of tested families are banned" (`research/research_index.md`, priority
   list item 5) — a direct, hard-won consequence of watching 61 indicator/ensemble variants of
   already-tested families add nothing but DSR deflation.

---

## 7. Warning signs of overfitting or weak research

A scannable checklist; see `18_common_failure_modes.md` for full mechanism-level detail on each.

- **Full-window Sharpe far exceeds walk-forward/test-split Sharpe.** (TrendVolTarget itself: 1.26
  full-window vs. 0.41 test-split — even this project's own best result shows this pattern, which is
  exactly why the project's standing rule is to headline the test number, not the full-window one.)
- **A single spectacular parameter surrounded by mediocre neighbors** (a "spike," not a "plateau") —
  Pardo's and Kaufman's independently-converged-on primary red flag (§3 above).
- **Trade count too small to distinguish skill from luck** — below Pardo's ~30-trade floor, or
  Chan's `252×parameters` effective-sample floor; this project's own overnight-breakout rejection
  (5-10 trades across 3-5 years) is a direct instance.
- **The story only makes sense in hindsight.** Pardo's "Abuse of Hindsight" parables (Ch.13) —
  a strategist notices a pattern in the data already examined and builds a rule to capture exactly
  that pattern, without re-testing across the full range of markets/periods the rule wasn't
  inspired by.
- **A refinement improves the test set but not the training set (or vice versa without re-derivation
  of why).** Chan's explicit rule: a change must improve BOTH, or the test set has become a second
  training set (Chan Ch.2-3, Ch.7).
- **Kurtosis on trade returns exceeds ~6-8.** Kaufman's mechanical overfitting alarm — too many
  similarly-sized wins clustered together is unrealistic for live trading (Kaufman Ch.2, Ch.21).
- **More than roughly half of total backtest profit comes from price-shock days.** Kaufman's
  diagnostic for simultaneously overstated return and understated risk (Kaufman Ch.21-22).
- **"Surprisingly good" results were not scrutinized as hard as bad ones.** Kaufman's
  asymmetric-scrutiny debiasing rule, restated three times across his book — a genuinely good result
  deserves the same suspicion as a bad one, not less.
- **The hypothesis is a parameter variation of an already-tested family**, not a new mechanism or
  data axis — this project's own hard-earned standing rule after 96 trials (§6 above), because every
  additional test against the same data deflates the DSR of everything that came before it,
  including past successes.
- **No accounting for cumulative multiple-comparisons debt.** Kaufman: "finding 1 profitable strategy
  in 100 should not be comforting" (Ch.21) — the number that matters is not this hypothesis's own
  p-value, but how many hypotheses have been tried against the same dataset in total.

---

## Cross-references

- `hypothesis_bank.md` — the catalog of specific tradable ideas this framework's principles should be
  applied to before spending a trial.
- `implementation_patterns.md` — how to actually build and validate a candidate once it clears the
  §6 checklist.
- `14_backtesting_and_validation.md` — full mechanics of WFA, Walk-Forward Efficiency, PROM/CECPP,
  the 60/20/20 and 70/15/15 conventions, and the full pre-trade checklist (§15) this file's §6
  distills the philosophy of.
- `16_research_hypotheses.md` — the books' own flagged research ideas, cross-referenced against this
  project's validator.py pipeline.
- `17_author_disagreements.md` / `18_common_failure_modes.md` — full detail behind every claim
  compressed in §2-3, §5, and §7 above.
- `research/research_index.md` / `research/strategy_research_notes.md` (repo root) — this project's own live,
  updated empirical record; the ground truth §1, §4, §5, and §6-7 of this file are anchored to.
