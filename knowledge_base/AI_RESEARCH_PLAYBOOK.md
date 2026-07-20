# AI Research Playbook — Operating Manual for This Project's Research Process

This file is the **process and navigation layer** for any AI (or human) researcher picking up this
project. It sits alongside `EDGE_FRAMEWORK.md` (the philosophy of what makes an edge durable),
`hypothesis_bank.md` (the catalog of candidate ideas), `implementation_patterns.md` (the composable
building blocks), the 18 numbered topic files (the raw synthesized book knowledge), and
`master_index.md` (the alphabetical lookup). **It does not restate any of their content** — it tells
you, step by step, how to actually use them to do research on this specific codebase.

It is also downstream of this repo's own operating documents at the repo root:
`research/research_index.md` (the live dashboard — read this first, every session), `research/strategy_iteration_log.md`
(the chronological experiment journal), `research/strategy_research_notes.md` (the synthesis of book knowledge
vs. this project's own empirical findings), `research/best_strategy_so_far.py` (the champion strategy's
maintained code copy), and `research/strategy_portfolio.md` (the current portfolio view). If anything in this
playbook appears to conflict with what those five files actually say, **the repo-root files are the
ground truth** — this playbook describes process, they record state.

---

## Table of Contents

1. [How to approach research — the research loop](#1-how-to-approach-research--the-research-loop)
2. [How to choose what to investigate](#2-how-to-choose-what-to-investigate)
3. [How to navigate the knowledge base](#3-how-to-navigate-the-knowledge-base)
4. [How to diagnose a failed strategy](#4-how-to-diagnose-a-failed-strategy)
5. [How to improve a promising strategy](#5-how-to-improve-a-promising-strategy)
6. [How to construct a new strategy](#6-how-to-construct-a-new-strategy)
7. [How to validate strategies correctly](#7-how-to-validate-strategies-correctly)
8. [How to recognize overfitting](#8-how-to-recognize-overfitting)
9. [How to prioritize robustness over backtest performance](#9-how-to-prioritize-robustness-over-backtest-performance)
10. [How to decide when an idea should be abandoned](#10-how-to-decide-when-an-idea-should-be-abandoned)
11. [How to log results](#11-how-to-log-results)
12. [Quick Start for a New Research Session](#quick-start-for-a-new-research-session)

---

## 1. How to approach research — the research loop

The loop this project follows, every time, no exceptions:

**hypothesis → implementation → validation → decision → logging.**

1. **Hypothesis**: pick one candidate from `hypothesis_bank.md`, filtered per §2 below. Do not start
   from a backtest and work backward to a story — `EDGE_FRAMEWORK.md` §6 point 1 and this project's own
   96-trial history (`research/research_index.md` hypothesis #8: an unconstrained sweep with no prior mechanism
   found nothing) both say mechanism-first, backtest-second.
2. **Implementation**: build the smallest version of the hypothesis that tests its mechanism, using
   `implementation_patterns.md` components. Do not over-build before the first validation pass.
3. **Validation**: run the mandatory pipeline in §7 below — no shortcuts, no partial runs used to
   decide whether to keep iterating.
4. **Decision**: REJECT, ADOPT, or (rare) PARTIAL/DEFENSIVE-VARIANT, per the stopping rules in §10.
5. **Logging**: update `research/strategy_iteration_log.md` and `research/research_index.md` regardless of outcome — see
   §11. A rejection recorded is as valuable as an adoption; an unrecorded trial is actively harmful
   because it breaks the cumulative `n_trials` count the DSR gate depends on.

**The standing constraint that should shape every decision in this loop right now**: per
`research/research_index.md`'s own "Open hypotheses" framing and its final priority-list item, *the marginal
value of testing another untested-paradigm-family construct is low*, because every additional
construct tested against this project's OHLCV dataset further deflates the Deflated Sharpe Ratio of
everything already found — including the current champion. `research/research_index.md` states this literally:
"more grinding on the same data is provably counterproductive" and "if any new hypothesis is proposed:
it must use a genuinely new data dimension or a structurally different mechanism — parameter
variations of tested families are banned." Treat that as a hard gate on step 1 of this loop, not a
suggestion — see §2.

---

## 2. How to choose what to investigate

Before opening `hypothesis_bank.md`, internalize the filter you must apply, because the bank itself
does not enforce it — you do:

1. **Skip anything flagged `**Already tested by this project**`.** Each hypothesis card that matches
   something this project has run names the `research/research_index.md` hypothesis number and status inline.
   Re-running a parameter variant of an already-rejected family is exactly the mistake
   `research/research_index.md` priority item 5 forbids.
2. **Prefer a genuinely new data axis or mechanism over a parameter variation of a tested family.**
   This is this project's own hard-won lesson (`research/strategy_research_notes.md` §2.1: "the pipeline is not
   broken; the edges aren't there" after 61 indicator/ensemble variants of already-tested trend/
   mean-reversion families produced nothing). Check `research/research_index.md`'s "Open hypotheses" section
   first — it already lists the two live, non-exhausted directions (forward dry-run accumulation, and
   the COT positioning data axis) and the five confirmed-blocked axes (funding-rate history, order
   book, liquidations, on-chain flow, sentiment) so you don't waste a cycle re-discovering that a door
   is closed.
3. **Run the candidate through `EDGE_FRAMEWORK.md` §6's priority checklist before spending a trial.**
   That section orders exactly what to check, in priority order: mechanism plausibility before backtest
   quality, cross-asset/cross-regime transfer, walk-forward/test-split positivity (not full-window),
   DSR at current cumulative n_trials, plateau/robustness behavior, sample-size adequacy, cost/fee
   realism, and — last but explicit — whether the idea is a genuinely new data axis or mechanism. If a
   candidate fails the "new axis or mechanism" test, it should not be built at all; if it fails
   "mechanism plausibility," fix the mechanism story before building; the rest are validated, not
   guessed at, during §7 below.
4. **If nothing in the bank passes filters 1-3**, the two highest-priority actions per
   `research/research_index.md`'s own ranked list are: (a) extend the TrendVolTarget forward dry-run (this grows
   genuine out-of-sample evidence at *zero* selection cost — it is not a new trial against the same
   historical window, it is new data arriving), and (b) exploit the COT data axis further, since it is
   the only new-data direction this project has confirmed reachable (`research/research_index.md` item 4).
   Both are lower-risk to the DSR budget than any new OHLCV construct.

---

## 3. How to navigate the knowledge base

A practical decision tree, given "I have a strategy idea, where do I look":

```
Do I have a hypothesis already? ──No──> hypothesis_bank.md (browse by theme; apply §2 filters above)
        │
       Yes
        │
        v
Do I know how to implement its pieces? ──No──> implementation_patterns.md
        │                                       (composable entry/exit/sizing/regime-filter blocks;
       Yes                                       "Common combinations" and "Common mistakes" fields
        │                                        per pattern are load-bearing, read them)
        v
Do I need the exact formula for an indicator it uses? ──Yes──> 13_indicator_reference.md
        │
       No / already have it
        v
Do I need the original author's full reasoning, a worked example,
or to check an extraction "Ambiguities" flag? ──Yes──> Knowledge/<Author>_<Book>/02_Chapter_NN_*.md
        │                                              (the topic file's (Book, Ch.N) tag tells you
       No                                               which chapter and folder)
        v
Proceed to implementation (§6) and validation (§7) below.
```

If you don't know which numbered topic file (01-18) covers a concept at all, **use
`master_index.md` as the fallback lookup** — it is a pure alphabetical index with no content of its
own, pointing you to the right file(s) so you can then use that file's own headers or Ctrl+F.

Two files are process/philosophy layers, not content lookups, and belong at a different point in the
workflow than the tree above: `EDGE_FRAMEWORK.md` (read before committing to a hypothesis — §2 above)
and this file (read once at the start of a session — see Quick Start).

---

## 4. How to diagnose a failed strategy

When a backtest disappoints — or, just as important, when it looks *too* good — work through
`18_common_failure_modes.md`'s taxonomy in the order this project has actually used historically
across its own iterations (`research/strategy_iteration_log.md`), not in the file's own section order:

1. **Lookahead bias, first, always.** This project found and fixed a genuine 1-bar lookahead bug in
   its own validator harness mid-session during iteration 5 (`research/strategy_iteration_log.md` Iteration 5) —
   discovered only because it was checked early, before any performance number was trusted. Check
   signal-to-execution lag (this project's `validator.py` enforces a 2-bar signal lag; confirm any new
   harness does the same) before looking at anything else. See `18_common_failure_modes.md` §1 and
   `14_backtesting_and_validation.md` §4.5 (Chan's look-ahead-bias detection procedure) for the
   diagnostic mechanics.
2. **Sample size adequacy, second.** Count trades before trusting a Sharpe. This project's overnight-
   breakout rejection (`research/research_index.md` hypothesis #6: 5-10 trades across 3-5 years) is the
   sharpest instance of this project killing an idea purely on N, before any deeper diagnosis was
   needed. See `18_common_failure_modes.md` §6 (small-sample traps) and
   `14_backtesting_and_validation.md` §3.1 for the standard-error arithmetic.
3. **Regime shift vs. genuine overfitting, third.** If in-sample and out-of-sample performance diverge,
   ask whether the OOS window's *market regime* differs structurally from the IS window (a regime-shift
   explanation, per `18_common_failure_modes.md` §4) before concluding the parameters were simply
   curve-fit to noise. This project's own RiskManagedBetaOverlay rejection
   (`research/strategy_iteration_log.md` Iteration 4) diagnosed both at once: the +362% full-window figure was
   almost entirely the 2020-21 bull regime (a regime-composition artifact), and the walk-forward
   IS-to-OOS decay (30.9%→2.77% CAGR) on top of that confirmed genuine overfitting, not just regime
   bad luck — both explanations were checked, not assumed.
4. **Fee/cost erosion, fourth** — the single most common way a *real* signal still isn't tradeable.
   This project's hours 21-22 UTC anomaly (`research/research_index.md` hypothesis #12) is the canonical
   internal example: a statistically genuine effect (t=2.4-3.0) killed 25:1 by fees. Always check this
   before discarding a signal as fake — it may be real but untradeable, which is a different, still
   loggable, conclusion. See `18_common_failure_modes.md` §5.
5. **Peak-parameter fragility, fifth** — if the strategy only works at one exact parameter setting,
   check the neighborhood (`18_common_failure_modes.md` §7; `14_backtesting_and_validation.md` §6.3,
   Pardo's plateau-over-peak framework). This project's TrendVolTarget was accepted partly *because*
   its parameter sweeps plateau (SMA 150-250, ROC 20-40, vol-target 30-50% all comparable —
   `research/strategy_iteration_log.md` Iteration 6); every rejected construct that showed a single spike
   rather than a plateau was treated as presumptively overfit.

This order — lookahead, sample size, regime-vs-overfit, fees, peak-fragility — is not arbitrary; it is
cheapest-check-first: lookahead and sample size can each be settled in minutes from the trade log
alone, before spending any effort on the harder regime/overfitting distinction.

---

## 5. How to improve a promising strategy

If a candidate clears initial validation (§7) and looks genuinely promising, improve it by swapping
**one** implementation-pattern component at a time, using `implementation_patterns.md`'s catalog of
interchangeable pieces — e.g., swap a fixed-percentage stop for a volatility-scaled one (ATR-based, see
`implementation_patterns.md`'s ATR Usage Patterns / stop-family entries, cross-referenced to
`09_exits.md` and `06_volatility.md` for the exact math), or swap fixed-fractional sizing for a
vol-target scheme (`10_position_sizing.md`) — the pattern this project's own champion already uses.

**The specific trap this project has already fallen into and recovered from: do not re-optimize on the
same data repeatedly.** Kaufman calls this the "Feedback" trap (`14_backtesting_and_validation.md` §4.3;
also `17_author_disagreements.md` §4) — re-running walk-forward or parameter search after every tweak
means there is, strictly, no true out-of-sample data left, because the "out-of-sample" window has been
looked at (directly or via the researcher's own adjusted intuition) on every prior pass. This project's
`freqtrade_dsr.py` DSR gate exists specifically to price this in mechanically: every additional trial
against the same dataset — including a "small tweak" to a strategy already tested — increments
cumulative `n_trials` and deflates the Deflated Sharpe Ratio of *every* candidate that has been
selected from that growing pool, past and present. Concretely:

- Each swap-and-retest of a component against this project's historical window is one more trial. Budget
  it accordingly — don't swap five components in a row and evaluate only the final combination; each
  swap that gets evaluated against the data counts, win or lose.
- Prefer improvements you can pre-register a rationale for (per §6's disagreement-check step) over
  improvements discovered by scanning results and picking whichever swap happened to score best this
  time — the latter is exactly the "Abuse of Hindsight" pattern in `18_common_failure_modes.md` §1 and
  `14_backtesting_and_validation.md` §9.2.
- A change should improve **both** the training/IS window and the test/OOS window, or be re-derived
  from a stated mechanism reason before being kept — Chan's explicit rule
  (`14_backtesting_and_validation.md` §4.2; restated in `EDGE_FRAMEWORK.md` §7) that an improvement
  which only helps the test set has turned the test set into a second training set.

---

## 6. How to construct a new strategy

Step-by-step synthesis workflow once a hypothesis has cleared §2's filters:

1. **Pick the hypothesis card** from `hypothesis_bank.md`. Read its "Supporting concepts,"
   "Suggested indicators," and "Related hypotheses" fields — they tell you which topic files and which
   implementation patterns are relevant before you write any code.
2. **Assemble implementation patterns.** Per Kaufman's three-part strategy definition that
   `implementation_patterns.md`'s own intro cites as its organizing assumption (entry + risk management
   + position sizing — independently converged on by Pardo too), you need at minimum one pattern from
   each of those three categories, not just an entry signal. Pull them from
   `implementation_patterns.md`'s catalog; do not invent a stop or sizing rule ad hoc when a cataloged
   pattern already covers the case.
3. **Check `17_author_disagreements.md` for any parameter choice that is genuinely contested** before
   picking a default value arbitrarily. E.g., if the strategy needs a volatility-target level, §2 of
   that file lays out the open Kaufman-6-8%-vs-this-project's-40% tension explicitly, so you make an
   informed choice (and document which side you're leaning on and why) rather than picking a number
   because it "felt right." If the strategy needs a Kelly/optimal-f-derived sizing choice, §1 of that
   file lays out the Vince/Chan/Kaufman three-way framing so you know none of them recommend trading at
   full Kelly. If it touches walk-forward-vs-average-of-tests validation philosophy, §4 tells you the
   three authors don't agree and this project's own pipeline (validator.py) hedges between Pardo's and
   Kaufman's positions rather than picking one.
4. **Implement.** Keep the first version minimal — the smallest construct that tests the hypothesis's
   actual mechanism, per §1 above.
5. **Validate** per §7, immediately — do not iterate informally against held-out data before the formal
   pipeline runs (that is exactly the Feedback trap in §5).

---

## 7. How to validate strategies correctly

This project's actual, mandatory validation sequence — not a book's abstract recommendation, but the
concrete pipeline that already exists and must be run, unmodified, for any new candidate:

1. **`user_data/research/validator.py`** — the harness. Confirms anti-lookahead execution (signal at
   close of bar *t*, position taken at open of *t+1*), then runs, in order: full-history backtest,
   year-by-year breakdown, a 70/15/15 chronological train/val/test split, a 4-window walk-forward, and
   a Monte Carlo stage (block-shuffled trades with slippage and commission and delayed execution). The
   file's own docstring states the pass bar explicitly (≥5 years of data, positive returns in ≥60% of
   years, no single year >40% of total profit, max DD <25%, Sharpe >1.5, profit factor >1.5, ≥200
   trades, test-Sharpe ≥0.5×train-Sharpe, walk-forward positive in ≥50% of windows, MC 5th-percentile
   Sharpe >0). Do not weaken these thresholds to make a candidate pass; do not skip a stage because an
   earlier stage looked good.
2. **`freqtrade_dsr.py`** — the DSR gate, run *after* validator.py, at the project's current honest
   cumulative `n_trials` (check `research/research_index.md`'s "Standing constraints" section for the current
   count — it is explicitly tracked and incremented with every trial, currently ≈95+ as of the last
   `research/research_index.md` update). A candidate must clear DSR ≥0.95 to be called a proven real edge; below
   that, report the actual DSR value and describe it honestly as "N% credible," exactly as
   `research/research_index.md` does for the current champion (0.64-0.67, described as "~64% probability of real
   edge," explicitly *not* claimed as proven).
3. **Cross-reference against `14_backtesting_and_validation.md`** for *why* each stage exists, if the
   rationale isn't obvious from the harness alone: §7 (Walk-Forward Analysis, Pardo's centerpiece,
   including Walk-Forward Efficiency and the four questions WFA is meant to answer) explains the
   walk-forward stage; §6 (Robustness: plateaus over peaks, Kaufman's parameter-neighborhood-averaging
   toolkit) explains why a single best-parameter result is not enough on its own; §9/§10 (the five
   causes of overfitting; costs and data-integrity checks) explain what the Monte Carlo and fee-modeling
   stages are guarding against. This file gives you the book-methodology *context* — it is not itself
   part of the pipeline you run.
4. **Never treat validator.py's stages as optional or partial.** A candidate that only ran the
   full-history backtest and looked good has not been validated — full-window Sharpe on this project's
   own data runs 2-4x inflated relative to the test-split number (see §9 below), which is precisely
   what the 70/15/15 split and walk-forward stages exist to catch.

---

## 8. How to recognize overfitting

`EDGE_FRAMEWORK.md` §7 gives the warning-signs checklist; here is how to make each one actionable
against this project's actual code and output, not just as an abstract principle:

- **Full-window Sharpe far exceeds walk-forward/test-split Sharpe.** Actionable rule: if full-window
  Sharpe is more than roughly 2x the walk-forward/test-split Sharpe, treat the full-window number as a
  red flag, not a result — do not report it as the headline number. This project's own best-validated
  strategy shows this pattern (TrendVolTarget: full-window 1.26 vs. test-split 0.41, a ~3x gap) and the
  project's own standing rule in response is to headline the *test* number, never the full-window one
  (`research/research_index.md`, "Standing constraints": "Judge on TEST-set / walk-forward numbers only.
  Full-window Sharpe runs 2-4x inflated here").
- **A single spectacular parameter surrounded by mediocre neighbors.** Actionable check: re-run the
  backtest at parameter values ±20-30% from the reported optimum (e.g., SMA period, vol-target level,
  lookback window) and confirm performance is comparable, not degraded, in that neighborhood. This
  project's parameter-sweep checks on TrendVolTarget (SMA 150-250, ROC 20-40, vol-target 30-50% all
  plateau) are the concrete template to reuse.
- **Trade count below the statistical floor.** Actionable check: count total trades in the *test* split
  specifically, not the full window. Below ~30 trades (Pardo's/Vince's converged-on floor,
  `EDGE_FRAMEWORK.md` §3), treat any Sharpe/DD figure from that split as noise, not signal — this
  project's overnight-breakout rejection (5-10 trades total) is the concrete precedent for killing an
  idea on this check alone.
- **The story only makes sense in hindsight.** Actionable check: could you have stated the mechanism
  and its expected market conditions *before* seeing this specific backtest result? If the rule was
  reverse-engineered from a pattern already visible in the exact data being tested, it fails this check
  regardless of how good the number looks.
- **A refinement improves test but not train, or vice versa, with no re-derived reason why.**
  Actionable check: log both numbers for every swap made per §5 above; if only one moved and you cannot
  articulate a new mechanism reason for why, revert the swap.
- **Kurtosis on trade returns exceeds ~6-8**, or **>50% of total profit comes from a handful of
  price-shock days.** Actionable check: pull the trade-return distribution and the daily P&L series for
  any candidate before trusting its Sharpe — these are exactly the two audit items `research/research_index.md`
  flags as still-open validator.py additions (Kaufman Ch.21 price-shock decomposition and the
  average-of-all-tests-not-peak reporting convention). If you build these checks while validating a new
  candidate, add them to `validator.py` itself so future researchers get them for free.
- **The hypothesis is a parameter variation of an already-tested family, not a new mechanism or data
  axis.** This is §2's filter restated as a red flag: if you find yourself here *after* building
  something, it should have been caught before you spent a trial — treat it as a process failure, not
  just a result to log.

---

## 9. How to prioritize robustness over backtest performance

This is an operating instruction, not a philosophical stance (that's `EDGE_FRAMEWORK.md`'s job — see
its §4's three-tier evidentiary framework and §6's priority list for the reasoning). The instruction
itself:

- **Judge every candidate on its TEST-set / walk-forward Sharpe, never on full-window Sharpe.** When
  writing up a result — in your own working notes, in `research/strategy_iteration_log.md`, or in any summary to
  the user — the number you lead with is the test-split number. If you report a full-window number at
  all, report it second, and label it explicitly as "full-window (inflated 2-4x on this dataset)."
- **When comparing a new candidate against the current champion for portfolio inclusion**
  (`research/strategy_portfolio.md`'s own stated evolution criteria), compare TEST-set/walk-forward performance
  and DSR at the *then-current* cumulative n_trials — not historical total return, not full-window
  Sharpe, not win rate. `research/strategy_portfolio.md` states this explicitly as one of its four portfolio-slot
  criteria: "positive TEST-set performance standalone" is required, full-window performance is not
  sufficient on its own.
- **A strategy with lower full-window returns but a smaller train-to-test decay gap is the more
  trustworthy candidate**, even if its headline number is less exciting. This project's own defensive
  variant (TVT 9-asset + portfolio-vol overlay: lower CAGR, DD -12.9% vs core's -16.6%, MC tail 1% vs
  28%) is kept in `research/strategy_portfolio.md` explicitly as a robustness-over-return tradeoff, not despite
  its lower returns.

---

## 10. How to decide when an idea should be abandoned

Concrete stopping rules — any one of these is sufficient to reject, per this project's own precedent
in `research/strategy_iteration_log.md`:

- **Trade count too small to distinguish skill from luck.** Below Pardo's/Vince's ~30-trade floor in the
  test split specifically. Precedent: overnight breakout, 5-10 trades in 3-5 years
  (`research/research_index.md` hypothesis #6) — rejected on this basis alone.
- **DSR doesn't clear the bar, even provisionally, and the shortfall is large.** The bar is 0.95; the
  current champion sits at 0.64-0.67 and is *not* rejected, but is explicitly labeled unproven rather
  than adopted-as-proven. A new candidate scoring materially below the champion's DSR, with no
  compensating strength (e.g., a genuinely new/uncorrelated mechanism), should be rejected outright
  rather than added to the portfolio to sit alongside the champion. Precedent: H-COT filter,
  `research/research_index.md` hypothesis #14, DSR 0.603 (below the champion's own 0.627 reference)  — rejected.
- **Walk-forward windows are wildly inconsistent** (best-performing window and worst-performing window
  diverge sharply, or fewer than half the windows are positive). Per validator.py's own pass bar
  (walk-forward positive in ≥50% of windows) and Kaufman's window-instability diagnostic
  (`research/strategy_research_notes.md` §1, "walk-forward window instability... = undersized window").
- **The mechanism doesn't survive cross-asset transfer.** If a construct only works on the asset(s) it
  was tuned on and fails on untuned assets, that is strong evidence of overfitting to that asset's
  idiosyncratic history rather than a real mechanism. This is precisely the test TrendVolTarget passed
  (positive Sharpe on 9/9 untuned assets) that every other rejected construct in this project's history
  either failed or was never subjected to.
- **In-sample effect is neutral-to-harmful and there is zero test-split activity.** Precedent: H-COT
  filter fired zero times in the TEST split (making TEST metrics identical by construction) while
  degrading full-window drawdown and one walk-forward window — rejected even though it "did nothing
  bad" in the sense of not corrupting the TEST number, because it added no evidence of benefit anywhere
  it could be checked.

**A rejection is a valuable, loggable result, not a failure to hide.** `research/strategy_iteration_log.md`'s own
header states "negative results are valuable," and its actual content is majority-rejections (11 of 14
tracked hypothesis families in `research/research_index.md`'s status table are FAIL, BLOCKED, or PARTIAL) —
this is the normal, expected shape of the log, not a sign the pipeline is broken. Every rejection must
still get a **Decision** and a **Lesson** line per the format in §11.

---

## 11. How to log results

Mandatory bookkeeping after every experiment, no exceptions, including negative results:

1. **`research/strategy_iteration_log.md`** — append a new numbered iteration entry, following the existing
   format (Hypothesis / Implementation / Validation-or-Result / Decision / Lesson). Include the exact
   metrics (Sharpe, DD, trade count, DSR, walk-forward window results) — this file is the project's
   evidentiary record, not a summary; future researchers rely on being able to see the actual numbers,
   not just the verdict.
2. **`research/research_index.md`** — update two things: the "Hypotheses tested — status table" (add a row with
   the hypothesis number continuing the existing sequence, session date, status, and primary
   failure/success reason in one line) and, if the trial changes the standing cumulative `n_trials`
   count, update the "Standing constraints" section's stated count so the DSR gate stays honest for the
   next researcher. If the trial closes or opens a line item in "Open hypotheses," update that list too.
3. **`research/strategy_portfolio.md` and `research/best_strategy_so_far.py` — only if a new strategy demonstrates
   superior ROBUSTNESS, not merely higher returns.** This is a hard rule already stated in both files'
   own headers (`research/best_strategy_so_far.py`: "Replace ONLY if a new strategy demonstrates superior
   ROBUSTNESS (not merely higher historical returns)"; `research/strategy_portfolio.md`'s own evolution criteria:
   structurally different mechanism, correlation with existing holdings <~0.4, full gate stack pass
   including DSR at current n_trials, standalone positive TEST-set performance — all four required, not
   any one). A strategy with a higher full-window return but a worse test-split Sharpe, larger DSR
   shortfall, or higher drawdown tail than the current champion does **not** qualify for promotion,
   regardless of how it compares on raw historical P&L. If a candidate does qualify, update
   `research/best_strategy_so_far.py`'s maintained code copy and status header, and add or revise the relevant
   slot in `research/strategy_portfolio.md` including its correlation with existing holdings.
4. **Do not skip logging a null/blocked result.** Data-access failures (e.g., a funding-rate API
   returning HTTP 451/403) are exactly as loggable as a completed-but-rejected backtest — see
   `research/research_index.md` hypothesis #4 ("BLOCKED") for the precedent — because future researchers need to
   know a door is closed without re-attempting it.

---

## Quick Start for a New Research Session

A fresh AI researcher picking up this project cold should do exactly this, in order:

1. **Read `research/research_index.md` in full.** It is the dashboard: standing constraints (dry-run only, DSR
   gate, current `n_trials`), the current champion and its honest metrics, the hypothesis status table,
   and the ranked list of open/highest-priority next steps.
2. **Skim `research/strategy_iteration_log.md`'s most recent 2-3 entries** to see exactly what was tried last and
   why it was accepted or rejected, in the researcher's own words at the time.
3. **Skim `research/strategy_research_notes.md` §3 ("Contradictions and tensions")** to see which questions are
   still explicitly open (e.g., the 40% vs. 6-8% vol-target reconciliation) versus resolved, so you
   don't re-litigate a settled question.
4. **Read this file's §2 ("How to choose what to investigate")** and apply its filters before opening
   `hypothesis_bank.md` — this prevents the single most common wasted cycle in this project's own
   history (re-testing a parameter variation of an already-rejected family).
5. **Open `hypothesis_bank.md`**, find a candidate that survives §2's filters, and read its full card
   (Supporting concepts / Suggested indicators / Related hypotheses / Already-tested flag).
6. **Run the candidate through `EDGE_FRAMEWORK.md` §6's priority checklist** before writing any code —
   if it fails "genuinely new data axis or mechanism," stop and pick a different candidate, or default
   to the two zero/low-selection-cost priorities `research/research_index.md` itself ranks highest: extending the
   TrendVolTarget forward dry-run, or the COT data axis.
7. **Build the smallest implementation** using `implementation_patterns.md` components (§6 above), and
   check `17_author_disagreements.md` for any contested parameter choice before defaulting it.
8. **Validate with the mandatory pipeline**: `user_data/research/validator.py` (70/15/15 + walk-forward
   + Monte Carlo) followed by `freqtrade_dsr.py` at the current cumulative `n_trials` (§7 above). Do not
   report or act on any partial-pipeline result.
9. **Decide** (ADOPT / REJECT / PARTIAL) using §10's concrete stopping rules, and **log the result
   immediately** in `research/strategy_iteration_log.md` and `research/research_index.md` per §11 — before moving on to
   anything else, including a follow-up experiment.
10. **Only update `research/strategy_portfolio.md` / `research/best_strategy_so_far.py`** if the result clears the
    robustness-over-returns bar in §11 point 3 — check this explicitly before touching either file.
