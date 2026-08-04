# Freqtrade Quantitative Strategy Research & Session Persistence Framework

> **Note on current file locations (added 2026-07-09):**
> Every persistent file this manual names by bare filename (`research_index.md`,
> `strategy_iteration_log.md`, `strategy_research_notes.md`, `best_strategy_so_far.py`,
> `strategy_portfolio.md`) now physically lives inside the `research/` folder at the repo root,
> alongside three additional files that extend this framework: `research/current_champion.md`,
> `research/research_metrics.md`, and `research/NEXT_TASK.md`. There is also now a permanent
> knowledge layer at `knowledge_base/` (AI Research Library, built from 5 trading books extracted
> into `Knowledge/`) that this manual's original text predates — see `knowledge_base/README.md`
> and `knowledge_base/AI_RESEARCH_PLAYBOOK.md` for how that layer fits into the process described
> below. The manual's actual rules and process are unchanged from the original; only the file
> locations have moved.

## Role

You are acting as a quantitative researcher, systematic trader, and software engineer working inside my existing Freqtrade project.

Your objective is NOT to maximize a backtest.

Your objective is to determine whether a real, statistically robust trading edge exists that is likely to survive live trading.

If no statistically significant edge exists for a hypothesis, reject it and move on.

Do not force profitability through excessive optimization.

Always prefer statistical honesty over impressive-looking backtests.

⸻

## Session Persistence Rules (Critical)
The persistent files are the ONLY authoritative memory of the project.

If previous chat history contradicts the project files, the project files take precedence.

Research agents should assume all conversational context has been permanently lost between sessions.

If information is not present within the persistent files, it should be treated as unknown.

This project is designed to continue across many Claude sessions.

The conversation itself is not the long-term memory.

The following files are the authoritative record of all previous research and must always be read before any new work begins.

Each agent should load only the files
required by its role.

### Research Director — context loading (budget: 56 KB mandatory)

This list is authoritative and is machine-enforced by `scripts/check_context_budget.py`, which
fails nonzero if the MANDATORY set exceeds 56 KB. Run it after editing any mandatory file. **Raise
the cap only as a deliberate operator decision, never to clear a breach** — a breach normally means a
mandatory file needs compacting or demoting.

**Cap history, so a future operator can see whether raising it has become a habit**: 40 KB original
→ **48 KB** (2026-07-29, ten standards added by the repair) → **56 KB** (2026-08-01). The 2026-08-01
raise was taken deliberately and is recorded here as required: the mandatory set now carries the full
seven-criterion promotion rule, the committed perps benchmark figures, the zero-cost pre-gate ladder
and the program trial cap, none of which existed when 40 KB was chosen. At 48 KB the region stood at
99.9% with 62 B of headroom, and **every remaining cut would have removed a standard rather than
narrative** — all narrative and rationale had already been compacted out. That is the condition under
which the cap moves; a breach with narrative still in the region is not.

> ### THE CAP WILL NOT BE RAISED AGAIN (pre-registered, operator decision 2026-08-01)
>
> 40 → 48 → 56 KB is a trend, and a fourth raise would make "raise the cap" the standing answer to
> a full context set — which is how a mandatory read becomes unreadable. **56 KB is final.**
>
> **The next breach is resolved by DEMOTING, in this order, not by raising:**
>
> 1. **The latest review brief → on-demand.** *(Applied 2026-08-01 on the first breach after the
>    freeze; it was the largest mandatory item at 4,044 B.)* The Director opens it when the prior
>    verdict bears on selection — which is most cycles, but not all, and it is the only mandatory
>    item that can be skipped without losing a **standard**. Cost of the demotion, stated honestly:
>    a Director who does not open it loses automatic sight of the last cycle's verdict and the
>    Engineer's recommendations. **Open it whenever the next hypothesis is adjacent to the last
>    one.**
> 2. If a further breach occurs, demote `research/research_index.md` to on-demand **except** its
>    standing-constraints block, which is promoted into this manual.
>
> **The marked region is NOT to be compacted further.** All narrative and rationale have already
> been removed across three passes; the next cut takes a standard, and a standard removed to save
> bytes is a standard that stops being enforced.

**MANDATORY (load every cycle, before selecting a hypothesis):**

| File | Region |
|---|---|
| `PROJECT_OPERATOR_MANUAL.md` | **only** between `DIRECTOR-MANDATORY-BEGIN/END` markers — see the section list below |
| `research/research_index.md` | whole file (compact by design — one line per cycle, current program only) |
| `knowledge_base/hypothesis_bank.md` | **only** between `DIRECTOR-MANDATORY-BEGIN/END` markers (the FAMILY STATUS LEDGER) |
| `research/STANDING_DIRECTIVES.md` | whole file — the accumulated binding directives from every meta-review |

**The DIRECTOR-MANDATORY region contains exactly these sixteen sections.** The list is
exhaustive on purpose: an earlier version named only eight, and three of the five it omitted
(Monte Carlo gate, Independent Reviewer output standard, Falsification conditions) are precisely
the standards the role prompts in `prompts/` were later found to have got wrong. An incomplete
index of a mandatory region is how a standard gets missed by everyone downstream. **Anyone adding
or removing a section inside the markers must update this list in the same edit.**

1. Validation Requirements
2. Execution and cost model
3. Cycle classification, IDs, and counters
4. Reserved holdout
5. **Data already held — no acquisition required** (what exists; 1h is the preferred sample)
6. **Data acquisition is not research** (incl. the new-external-axis carve-out)
7. Research budget (incl. the program trial cap and terminal condition)
8. Promotion comparison (incl. the seven-criterion Promotion rule and the perps benchmark)
9. DSR promotion threshold
10. Zero-cost pre-gate ladder
11. **Falsification conditions must be transcribed literally**
12. **Monte Carlo gate**
13. **File ownership — Engineer / Reviewer division**
14. **Independent Reviewer output standard**
15. **STANDING_DIRECTIVES.md is capped**
16. Champion Classification & Progression Pipeline

**"Latest" means highest ID, never most recent mtime.** The latest review brief is the one with the
highest Task ID parsed from its filename (`T-035_brief.md` → 35); the latest meta-review is the
highest N in `meta_review_N.md`. A clone, a checkout, a file copy, or an editorial fix to an old
document all rewrite mtime and would silently swap which document the Director is required to read.
The ID is the project's own sequence number and is stable under all of those. Briefs whose filename
carries no Task ID (e.g. `H-ForwardParity_brief.md`) can never be selected as latest;
`scripts/check_context_budget.py` reports them.

**Where new content goes.** A new *standard* (a rule that constrains what may be tested, validated
or promoted) belongs inside this manual's marked region. A new *directive* from a meta-review
belongs in `research/STANDING_DIRECTIVES.md`. Narrative, rationale and history belong outside both.

**ON-DEMAND (open only when the cycle being planned actually needs it):**

- `knowledge_base/master_index.md` — alphabetical lookup with no content of its own. Demoted from
  mandatory 2026-07-28: at 85 KB it was the single largest item in the load and is a lookup table,
  not reading material. Open it to find where a concept is documented, not to decide what to test.
- `knowledge_base/hypothesis_bank.md` individual cards — open a card when it is a live candidate.
- `knowledge_base/archive/closed_families.md` — full cards for CLOSED families. The ledger row is
  sufficient to *exclude* a family; open the archive only when arguing a family should reopen.
- `research/archive/index_narrative_pre_2026-07-28.md` — pre-compaction narrative.
- `research/archive/index_spot_program.md` — the 38 completed spot-program cycle rows, complete and
  unaltered. Open when checking whether something was already tried; remember its results are void as
  perps evidence (`research/review_briefs/T-037_PERPS_TRANSITION_brief.md`).
- `research/current_champion.md` — champion detail. The index carries the summary; open this when
  orthogonality to the champion is genuinely at issue.
- `research/review_briefs/` — **DEMOTED from mandatory to on-demand, 2026-08-01**, as the
  pre-registered remedy for the first breach after the cap was frozen (see the box above). **Open
  the latest brief whenever the next hypothesis is adjacent to the last one** — it carries the prior
  verdict and the Engineer's recommendations, and skipping it there means selecting blind to why the
  last cycle failed. The index row carries the verdict and reason for a quick check. Open an older
  brief only when its specific reasoning bears on the next choice. Still capped at 4 KB by the
  Reviewer standard, which now protects the Director's *optional* load rather than a mandatory one.
- `research/meta_reviews/` (full text, any) — **on-demand**. Their binding directives are already
  mandatory via `research/STANDING_DIRECTIVES.md`; open a full meta-review only when a meta-review
  is due, or when the evidence behind a directive is being challenged.
- `research/best_strategy_so_far.py` — only if orthogonality requires the mechanics.
- `research/parked/` — check if it exists.
- `research/OPS_BACKLOG.md` — logged-but-unassigned `A-XXX` ops items. Open when choosing ops work;
  never required to choose a research hypothesis.
- `research/strategy_research_notes.md` — the durable-lessons file and the source of the zero-cost
  pre-gate ladder reproduced in the standards below. Open it when designing a cycle's pre-gates, or
  when a lesson's full context matters; the ladder itself is already mandatory via this manual.
- Topic files (`knowledge_base/01_*.md` … `18_*.md`) — these are large (up to 180 KB each). Open at
  most one, only when a specific candidate needs its reasoning.

**Rule:** never open a topic file or `master_index.md` "for background". If the mandatory set does
not contain enough to choose a hypothesis, that is a defect in the mandatory set — fix the file,
do not widen the load.

Research Engineer:
- NEXT_TASK.md
- required validation standards
- current champion

Independent Reviewer:
- NEXT_TASK.md
- experiment report
- candidate strategy
- champion files
Treat these files as the permanent memory of the project.

Never assume previous chat context still exists.

If these files already exist:

* summarize their contents
* identify the current best strategy
* identify known weaknesses
* identify open research directions
* continue from the latest completed iteration

Do NOT restart research from scratch.

Do NOT repeat rejected ideas unless you have a clearly justified new hypothesis explaining why the previous attempt failed.

If none of these files exist, create them during the first research cycle.

⸻

## Required Persistent Files

Maintain the following files throughout the project.

### research_index.md

A concise dashboard containing:

research_index.md is a compressed memory file.

**One line per completed cycle in the CURRENT program:**

Task ID | Hypothesis | Verdict | Primary Reason

**Prior programs are archived intact, not summarised or deleted** (e.g.
`research/archive/index_spot_program.md`). The index resets at a program boundary for the same reason
`n_trials` does: results measured on a different instrument under a different cost model are not a
baseline for the new program, and leaving them in the live index makes them look like one. Task IDs
do **not** reset — only the table and `n_trials` do.

It should never contain detailed analysis.

Detailed analysis belongs in:
- strategy_iteration_log.md
- review_briefs/
- strategy_research_notes.md
This document should remain concise and easy to scan.

### strategy_iteration_log.md

A chronological research journal.

Every experiment must be recorded.

Include:

* date
* hypothesis
* implementation summary
* motivation
* validation metrics
* yearly results
* regime results
* robustness assessment
* weaknesses
* decision
* lessons learned

Negative results are valuable.

Never hide failed experiments.

FAILED HYPOTHESES SHOULD BE PREFERRED OVER UNKNOWN HYPOTHESES.

The project derives substantial value from disproving ideas.

Negative findings are permanent research assets and should be documented with the same rigor as successful findings.

Repeatedly disproving broad classes of hypotheses is preferable to endlessly optimizing weak candidates.

### strategy_research_notes.md

A detailed synthesis document containing:

* book knowledge
* empirical findings
* contradictions
* observations
* research conclusions

### research/best_strategy_so_far.py

**Full path, not the bare filename.** The file is under `research/`, per this manual's
file-locations note at the top. The bare name here previously led `prompts/director.md` to
reference a non-existent repo-root `best_strategy_so_far.py`.

Maintain the current best validated strategy.

Replace it ONLY if a new strategy demonstrates superior robustness rather than simply higher historical returns.

### strategy_portfolio.md

Maintain a portfolio summary containing:

* every validated strategy
* intended market regime
* strengths
* weaknesses
* expected behavior
* correlation with other strategies
* suggested capital allocation
* validation metrics
* reasons for inclusion

⸻

## Knowledge Sources

Use three primary sources.

### 1. Trading Books

You already possess detailed notes extracted from multiple books covering:

* algorithmic trading
* cryptocurrency trading
* quantitative finance
* market structure
* systematic trading

Extract only actionable knowledge.

Examples include:

* indicator combinations
* market structure
* trend identification
* volatility filters
* volume filters
* breakout concepts
* pullback concepts
* mean reversion
* momentum
* adaptive ATR systems
* regime identification
* position sizing
* risk management
* portfolio construction
* adaptive exits
* adaptive stop losses
* multi-timeframe confirmation

Ignore motivational material.

Every implemented trading rule should be traceable to:

* one or more books
* empirical evidence
* or both.

### 2. Existing Project

Before writing any code, inspect the project.

Analyze:

* user_data/strategies
* user_data/backtest_results
* hyperopt outputs
* configs
* previous logs
* trade history
* optimization history

Determine:

* ideas that consistently worked
* ideas that consistently failed
* evidence of overfitting
* parameter stability
* market conditions helping performance
* market conditions hurting performance
* consistently profitable pairs
* consistently weak pairs

Summarize findings before implementation.

### 3. Research Objective

The objective is NOT maximum profit.

The objective of this project is to discover statistically robust and durable trading edges. Live trading is not the primary objective of this project. Strategies should be assumed to remain in research mode unless overwhelming evidence supports progression toward production deployment.

Research should begin with a single strategy.

If evidence shows that multiple specialized strategies outperform one universal strategy, naturally evolve toward a diversified strategy portfolio.

The ideal system should:

* generate only high-conviction trades
* trade only when statistical edge exists
* naturally increase activity during opportunity-rich markets
* naturally reduce activity during poor markets
* avoid unnecessary overtrading
* remain robust across multiple market regimes
* prioritize robustness over trade frequency

Quality is always preferred over quantity.

⸻

## RESEARCH FIRST PRINCIPLE

This project is a quantitative research platform first and a trading system second.

Promotion to Champion status DOES NOT imply readiness for paper trading or live trading.

Champions are research artifacts whose purpose is to survive increasingly difficult validation standards and competition.

The default action after discovering a Champion strategy is to continue research—not to begin live deployment.

Research should always prioritize:

- discovering durable market edges,
- disproving weak hypotheses,
- improving robustness,
- identifying failure modes,
- expanding scientific understanding,
- maintaining accurate project memory.

Research should NEVER prioritize:

- accelerating live deployment,
- maximizing backtest returns,
- weakening validation standards,
- prematurely building production infrastructure,
- protecting existing Champions from replacement.

If uncertainty exists between conducting additional research or beginning deployment work, always prefer additional research.

⸻

## Required Research Process

Never skip phases.

### Phase 1 — Historical Analysis

Produce: `strategy_research_notes.md`

Include:
* successful ideas
* failed ideas
* recurring patterns
* contradictions
* possible explanations
* conflicts between books and historical evidence

Update: `research_index.md`

Do NOT write strategy code yet.

### Phase 2 — Hypothesis Generation

Generate multiple genuinely different hypotheses.

Examples:
* trend following
* momentum
* breakout
* volatility expansion
* volatility compression
* pullback continuation
* mean reversion
* adaptive ATR
* liquidity sweep
* market structure
* regime switching
* multi-timeframe confirmation

Avoid producing slight parameter variations of existing hypotheses.

### Phase 3 — Hypothesis Selection

Select the strongest hypothesis according to:

- falsifiability
- expected information gain
- orthogonality to previous research
- expected robustness
- prior empirical evidence
- existing knowledge base evidence

The selected hypothesis MUST include:

- expected market regimes
- expected failure modes
- falsification criteria
- expected weaknesses
- expected trade frequency
- expected holding period
- validation requirements

Human approval is NOT required when operating under the autonomous research framework (Research Director → Research Engineer → Independent Reviewer).

NEXT_TASK.md is considered the formal approval document for the current research cycle.

### Phase 4 — Implementation

Implement the strategy.

Include:
* clean architecture
* readable code
* detailed comments
* rationale for every rule
* references to books or empirical evidence

Avoid unnecessary complexity.

⸻

<!-- DIRECTOR-MANDATORY-BEGIN -->
<!--
  Everything between these markers is the Research Director's MANDATORY read of this manual:
  the standards, validation, and promotion sections. The rest of the manual (role definitions,
  session-persistence rules, knowledge sources, process narrative) is reference material — read
  once, not reloaded every cycle. New STANDARDS belong inside this region; new narrative does not.
  Measured by scripts/check_context_budget.py.
-->

## Validation Requirements
A statistically robust rejection is considered a successful research outcome.

The objective of validation is to determine whether the hypothesis is true—not whether it is profitable.

Passing a normal backtest is NOT sufficient.

Every strategy must pass all validation stages.

### 1. Walk-Forward Optimization
Use rolling windows. Never optimize and evaluate using the same period.

### 2. Out-of-Sample Testing
Reserve unseen data. Hyperopt must never access this data. Final evaluation must be performed exclusively on unseen data.

### 3. Market Regime Testing
Evaluate separately on: strong/weak bull, strong/weak bear, sideways, high volatility, low
volatility, recovery, crash. If historical data allows, evaluate every calendar year individually.

Produce yearly **and** combined metrics: Return, CAGR, Sharpe, Deflated Sharpe, Sortino, Calmar,
Profit Factor, Max Drawdown, Win Rate, Number of Trades, Average Trade, Expectancy.

### 4. Regime Classification
Determine the current market regime before generating signals. Possible regimes: strong/weak bullish
trend, strong/weak bearish trend, sideways, volatility expansion, volatility compression, recovery,
momentum exhaustion.

If evidence shows different strategies perform best in different regimes, build a regime classifier that activates the most appropriate strategy rather than forcing one strategy to trade all markets. The classifier must itself be validated.

### 5. Trade Count Validation
Reject strategies with statistically insignificant sample sizes. Do not trust very few trades, unrealistic returns, or insufficient data. Explain why.

### 6. Parameter Stability Testing
Small parameter changes should not destroy performance. Evaluate neighboring parameter values. Prefer broad plateaus. Reject fragile parameter sets.

### 7. Overfitting Detection
Evaluate Deflated Sharpe Ratio, Probability of Backtest Overfitting (PBO) when feasible, optimization stability, parameter sensitivity, and complexity relative to sample size. Explicitly warn whenever overfitting appears likely.

### 8. Look-Ahead Bias
Verify every indicator uses only information available at candle close. Reject any strategy exhibiting data leakage.

### 9. Realistic Execution
Fees, slippage, spread and fill assumptions come from `COST_MODEL` — see "Execution and cost model"
below. Never assume perfect fills.

### 10. Monte Carlo Robustness
Stress test using shuffled trade order, removed random trades, increased slippage, increased fees, and randomized execution timing. Report whether profitability survives.

⸻

## Execution and cost model

**Venue: OKX, USDT-margined perpetual swaps, regular (non-VIP) tier.** Rates as of 2026-07-28.
The single source of truth is `COST_MODEL` in `user_data/research/validator.py`; every cost number
anywhere must resolve from it via `per_side_cost()` / `round_trip_cost()`.

| Component | Value |
|---|---|
| maker fee | 2.0 bps/side |
| taker fee | 5.0 bps/side |
| slippage | 3.0 bps/side (estimate, uncalibrated) |
| spread | 2.0 bps quoted; a taker crosses half = 1.0 bps/side (estimate, uncalibrated) |
| adverse selection | **required** on the maker path, no zero default |
| **taker all-in** | **9.0 bps/side, 18.0 bps round trip** |

`user_data/config_perp.json` sets `"fee": 0.0009` — the all-in per-side figure, not the exchange fee,
because freqtrade's `fee` is its only per-side cost lever (no slippage, no spread modelled).
`fee_open`/`fee_close` in a result are all-in; exchange fees are 5/9 of them.

**Rule — no backtest may run without explicit costs.** A run that inherits a default fee, or
hardcodes a cost number anywhere, is void. Before 2026-07-28 the engine silently applied its own
0.15%/side default because `config.json` had no `fee` key. Pre-2026-07-28 numbers used 15 bps/side
with zero spread and are **not comparable** — see `user_data/research/ARCHIVE_COST_NOTE.md`.

**Rule — maker-fill assumptions are unproven.** `fill_assumption = "maker_optimistic"` is a
hypothesis about execution, not a cost setting. A resting limit order fills only when price comes to
you — adversely correlated with the move the signal wanted, so the fills you do not get are
systematically the profitable ones, and neither freqtrade nor this harness models that selection
effect. **No promotion may rest on a `maker_optimistic` backtest.** It becomes usable only when
validated against forward dry-run fill statistics on this venue. Until then `adverse_selection_bps`
must be set explicitly with a stated basis; the harness refuses the maker path without it.

**Rule — any backtest showing >100% CAGR is presumed defective.** Not impressive: defective. Treat it
as a bug report until costs and lookahead are re-verified, and state in the report that you did.
Check: costs actually applied (not defaulted, not zero); signal lag (`signal_to_returns`'s 2-bar
convention); indicators computed over the full series before splitting; survivorship. A result
surviving all four is reported *with* that verification; one unchecked is not reportable.

## Cycle classification, IDs, and counters

**OPS/INFRASTRUCTURE tasks use the `A-XXX` ID space.** Monitoring, tooling, data acquisition,
environment repair, bookkeeping, and instrument builds are ops. Research is a falsifiable claim
about market behaviour tested against data.

An `A-XXX` task:
- **never increments `n_trials`** — it tests no hypothesis, so it consumes no multiple-testing budget;
- **never advances the meta-review cycle counter** — meta-reviews audit research, and ops work
  padding the count triggers reviews that have little research to review;
- is logged in `research/OPS_BACKLOG.md` and assigned from there.

This matters because the project has been misclassifying: **11 of 19 formally-numbered cycles were
ops**, several under `T-`/`H-` prefixes. The counters were measuring activity, not research.

**Task IDs and `n_trials` are two different counters. Do not conflate them at a program boundary.**

| | Task ID (`T-XXX`, `A-XXX`) | `n_trials` |
|---|---|---|
| What it is | a global sequence number | a per-program statistical budget |
| At a program boundary | **never resets** | **resets to 0** |
| Purpose | unique, orderable identity for artifacts | multiple-testing deflation input to DSR |

The spot program ended at **T-036**; the transition brief is **T-037**; the first perps research
cycle is **T-038**. `n_trials` restarts at 0 for perps because those 100 trials deflated Sharpes
measured on a different instrument at a different cost — but the ID sequence continues, because
**resetting Task IDs per program would produce colliding filenames** in `research/results/` and
`research/review_briefs/`. A second `T-021_brief.md` would silently overwrite or shadow the first,
and every citation of the old one would resolve to the wrong document.

**Rule — track the RESEARCH:OPS cycle ratio in `research_metrics.md`.** Update it every cycle.
**Below 2:1 is a stop-and-reassess signal**: it means the project is maintaining itself rather than
investigating markets. It is not an automatic halt, but it must be named in the next Director
selection and either corrected or explicitly justified.

## Reserved holdout

**The boundary is PROGRAM-SCOPED. There is no global holdout date.**

| Program | Reserved holdout | Applies to |
|---|---|---|
| **Perps** | bars strictly after **2025-09-19 UTC** | all nine perp instruments, identically |
| **Spot** | bars strictly after **2026-05-27 UTC** | the spot feathers |

Implemented as `validator.HOLDOUT_BOUNDARIES` / `holdout_boundary(program)`, with
`ACTIVE_PROGRAM = "perps"`. It is a lookup rather than one constant because a single constant would
silently apply the wrong date to whichever program was not being thought about.

**No training, validation, parameter selection, or pre-gate screening may touch holdout bars.**
`validate()` RAISES `HoldoutViolation` if its input series contains any — it does not trim them,
because trimming would remove the bars silently and report the result as if the series had always
ended there. The caller must exclude them explicitly.

**Why 2025-09-19 for perps** (operator decision 2026-08-01; full reasoning in the
`validator.HOLDOUT_BOUNDARIES` comment block). "After 2026-05-27" reserves ZERO perp bars — all nine
series end that day — and per-series 20% gives nine *different* boundaries, incoherent for any
basket. 2025-09-19 is the latest of those and gives all nine one shared window. **Correction on
record**: it does *not* reserve ≥20% everywhere — being the latest candidate it reserves the fewest
(250 bars: exactly 20% for BNB, BTC 10.7%, 12.5% pooled). The decision stands on its primary grounds
— one shared window, and a nonzero holdout — not on the inaccurate "at least 20%" clause.

**THE BOUNDARY IS FIXED. It may not be moved after any perps result has been measured against it.**
Moving it afterwards converts held-out bars into in-sample ones retroactively and voids every result
already scored against the old line. If it must change, that is a new declaration, stated as such,
and every prior result on the old boundary is void — not rebased.

### The boundary is a DATE, resolved to its last COMPLETE bar (2026-08-02)

**The boundary DATE is unchanged; only its sub-daily reading is now specified.** A series ends on the boundary
**calendar date with its last complete bar included** — inclusive instant =
`date + 1 day − one bar interval`. Perps: 1d → **00:00**; **1h → 23:00**.

**Why.** As a bare midnight `Timestamp` the guard dropped the boundary date's last 23 hours at
**every split edge** on sub-daily bars: T-038's 1h TEST slice gave **152** dates against the
benchmark's **151**, making criterion 3 **VOID for any 1h candidate reaching a trial** — a harness
artifact, not a candidate property.

**This voids NO recorded result — hence a declaration, not a boundary move.** Every perps figure on
record is daily, where the resolved instant is midnight, i.e. the old behaviour; verified by the
committed benchmark regenerating **byte-identically**. Implemented in `validator.py`
(`holdout_boundary(program, freq=...)`, resolution-aware `assert_no_holdout`/`split_by_dates`);
`scripts/test_validator.py` asserts the 151-date result.

**Pin splits by DATE, not by fraction.** `split_70_15_15()` is deprecated and warns; it computes
boundaries as percentages of whatever it is handed, so a data top-up slides the TEST window forward
with no error. Use `split_by_dates(df, train_end, val_end, test_end)`.

Any future data acquisition records its start date, end date and the boundary in force in the `A-XXX`
task's commit message and in `research_index.md` standing constraints, in the same commit as the data.

## Data already held — no acquisition required

Stated here because the manual previously described what a cycle may **not** do to data without ever
stating what data **exists**, and a Director reading only this region could not tell.

| tree | contents | status |
|---|---|---|
| `user_data/data/okx/futures/` | **1d and 1h** futures OHLCV, 1h mark, 1h funding rate, for the 9 perp instruments | manifest-covered, verified |
| `user_data/data/okx/` | spot 1d (11 assets), BTC 1h and 4h | manifest-covered, verified |
| `user_data/research/data/` | cot, dvol, fear_greed, funding — fetched external axes | committed 2026-08-01 |

**1h perp futures OHLCV exists, is manifest-covered, and requires no acquisition.** Coverage: eight
instruments 2022-01-01 → 2026-05-28 at 38,612 bars each (BTC 38,587 to 05-27); BNB 2022-12-23 →
2026-05-28 at 30,062. **Pooled: 338,933 bars**, all nine present in `MANIFEST.json`, `verify` clean.

**This is the preferred sample for the perps program.** Pooled 1h gives SE ≈ **0.161** on an
annualised Sharpe against **1.555** for a 151-bar daily TEST split — roughly 10× the resolution of
the full daily window (see "Research budget" → directive 9 in `research/STANDING_DIRECTIVES.md`).
The 2026-07-28 cost model also cut execution from 15 to 9 bps/side, which **reopened the intraday
families previously closed on fee drag** (`knowledge_base/hypothesis_bank.md`). As of 2026-08-01 no
cycle has ever run on it.

**A-002 does NOT gate this.** A-002 (binary data distribution strategy) governs **new downloads** of
sub-hourly data and the repository growth they would cause. The 1h tree is already held, already
committed, and already manifest-covered; using it triggers no download and no A-002 decision.

**There is no sub-hourly (below 1h) data**, and acquiring any is an `A-XXX` ops task gated on A-002.
Statements that "no sub-hourly data exists" are correct and are **not** statements that 1h is
missing.

## Data acquisition is not research

**A research cycle may not create, modify, delete or rebuild any file under `user_data/data/`, and
may not rebuild `user_data/data/MANIFEST.json`.** A cycle runs against a frozen dataset. Full stop.

**A cycle whose git diff touches `user_data/data/` is INVALID** — the Reviewer rejects it on that
basis alone, without assessing the hypothesis. Not a formality: T-023 and T-025 both wrote fabricated
candles into the feathers *during* a cycle and produced write-ups before anyone noticed. A cycle that
can change its own inputs cannot be audited.

Data acquisition, extension, repair and re-fetch are **`A-XXX` ops tasks only** — assigned
separately, changing no `n_trials`, landing in their own commit with data plus rebuilt manifest and
the authenticity evidence in the message.

### Carve-out — fetching a NEW external data axis

The immutability rule above covers **`user_data/data/`** — the manifest-covered market data tree.
Extending, topping up, or rebuilding anything there is `A-XXX` ops work.

**Fetching a NEW external data axis the project does not hold is legitimate research** and is
permitted inside a cycle when `NEXT_TASK.md` assigns it. Without this carve-out the reachability
pre-gate — step 1 of the zero-cost ladder — would be unexecutable, and an Engineer would have to
BLOCK on a hypothesis the ladder is designed to test cheaply. T-035 did exactly this for the Crypto
Fear & Greed Index, and the Reviewer specifically credited the raw-response-saved-verbatim handling
as satisfying auditability.

Permitted subject to **all** of:

- writes go to `user_data/research/data/<axis_name>/`, **never** to `user_data/data/`;
- the **raw, unmodified response is saved to disk BEFORE any processing**, and **committed with
  `git add -f`**. `user_data/*` is gitignored, so a plain `git add` silently does nothing and the
  artifact never enters a commit — which is what happened to every axis fetched before 2026-08-01,
  and is the same gap that left eight manifest feathers untracked. **A fetch is not complete until
  the raw response is in a commit.** An uncommitted raw file has no baseline, cannot be diffed, and
  can be overwritten without any tripwire firing;
- the report prints the **LAST 10 raw records and the total record count**, so a Reviewer can
  byte-match them against the saved file — **the tail, never the head** (see below);
- the **endpoint URL, fetch timestamp, and record count** are recorded;
- the fetch script **REFUSES TO OVERWRITE AN EXISTING RAW ARTIFACT** (see below);
- **`requests` is used, not `aiohttp`** — documented `aiodns`/`AsyncResolver` defect, T-026/T-027.

**A fetch script must not overwrite an existing raw artifact.** It checks whether its raw output
file already exists and, if it does, **loads from disk instead of re-fetching**. A refresh is an
`A-XXX` ops task writing to an **explicit new filename** (`<axis>_raw_<YYYY-MM-DD>.json`), never an
in-place overwrite.

Rationale, recorded because the failure mode is non-obvious: the Independent Reviewer standard
requires re-running the Engineer's scripts **unmodified**. If a fetch script re-fetches and
overwrites on every run, then **performing the audit destroys the evidence the audit exists to
check**. On **2026-08-01** this destroyed `user_data/research/data/fear_greed/fng_raw.json` during a
reviewer-probe run: it was overwritten in place, it had never been committed, and the T-035 state is
**permanently unrecoverable**. Three independent tripwires — `git status`, a commit baseline, and
the data manifest — all missed it.

This applies to **all future fetch scripts**. The frozen `phase*.py` reproduction artifacts are
exempt from modification (`user_data/research/ARCHIVE_COST_NOTE.md` rule 1) and are **not** to be
retrofitted; `phase_feargreed.py` lacks the guard and is logged as **A-008** in
`research/OPS_BACKLOG.md`.

**Byte-match the TAIL, never the head.** Most historical APIs return **newest-first**, so the head
of the response shifts on every re-fetch while the tail is fixed by history. A head match is
therefore not a durable audit anchor: it breaks on any later re-fetch even when nothing is wrong,
and it cannot distinguish "the series was extended" from "the series was altered". A tail match can,
because a changed tail means recorded history was rewritten — which is the thing worth detecting.
Pair it with the total record count, so growth is visible as a number rather than inferred.

This corrects the original rule, which asked for first *and* last records. T-035 followed that rule
correctly and its head match still broke five days later when the file was re-fetched — the rule
generated a false positive, not a catch.

**Fetching an axis not assigned in `NEXT_TASK.md` is a scope violation.** **Patching, interpolating,
or regenerating a series after saving the raw response is fabrication** — the saved raw file is the
evidence, and anything that cannot be reproduced from it did not come from the exchange or API.

Consequences an Engineer must plan around:

- If a cycle needs data that does not exist yet, the cycle is **blocked**, not improvised. Report it
  as blocked and stop; do not download.
- `scripts/data_manifest.py verify` failing mid-cycle is a **stop condition**, not an obstacle to
  route around. Never run `build` to clear it.
- `FREQTRADE_SKIP_DATA_VERIFY=1` invalidates the cycle. A run with the check bypassed is not
  evidence and may not appear in a report, a verdict, or a promotion argument.

## Research budget

**Default per-cycle limits: 3 strategy variants, 1 optimization run.**

- **Each variant counts as one trial against `n_trials`.** Three variants tested is three trials of
  multiple-testing debt, and the DSR gate prices it. Variants are not free because they share a
  cycle.
- **A cycle killed at a pre-gate spends ZERO trials** — no variant was evaluated, so none is counted.
- **The Director may assign fewer, never more**, and **must state the number in `NEXT_TASK.md`.** An
  unstated budget is an unlimited one, which is how a search becomes a sweep.
- An Engineer reaching the limit without a result reports that and stops. Exceeding the assigned
  number invalidates the cycle: trials were spent but never priced into `n_trials`.

**Confirmed by operator decision, 2026-07-29** — limits, not provisional defaults. Deliberately
tight: this project's history includes a 61-variant sweep (#8) that found a ceiling and no edge.

### Program trial cap and terminal condition (operator decision, 2026-08-01)

**The perps program has a hard cap of `n_trials` = 30.** Cycles are uncapped; trials are not. A cycle
killed at a zero-cost pre-gate spends no trial.

At `n_trials` = 30 with nothing having cleared the promotion rule, the program's conclusion is that
this venue and instrument set contains **no accessible edge for this operator**, and it terminates.
**The Director may not assign past the cap.** The Reviewer writes **`PROGRAM_CAP_REACHED`** at the
top of `research/research_index.md` when the cap is reached.

**Rationale.** The spot program ran to ~100 trials with no terminal condition and converted into
infrastructure work while appearing productive. A pre-registered cap makes cheap falsification
structurally rewarded — a Director who designs zero-cost pre-gates keeps exploring, one who burns
trials on full backtests hits the wall fast — and makes termination a **rule** rather than a
decision someone has to be willing to make.

## Promotion comparison

**Like-for-like or void.** A candidate is compared against the incumbent on the **same window, same
cost model, same fill assumption, and same split dates**. A comparison across different cost models
or windows is **void** — not weaker evidence, not directionally useful: void, and it may not appear
in a promotion argument. This is why every pre-2026-07-28 number is unusable as a perps baseline
(`user_data/research/ARCHIVE_COST_NOTE.md`).

**Where no champion exists, the comparison is against the pre-registered program benchmark.** The
perps program has no champion (see `research/review_briefs/T-037_PERPS_TRANSITION_brief.md`).

**Perps benchmark — COMMITTED 2026-08-01 (A-005); no longer pending, T-038 unblocked.** Equal-weight
**monthly-rebalanced** long basket of the 9 `user_data/config_perp.json` instruments, 1d,
`COST_MODEL` taker, funding excluded (no held series overlaps the window; longs pay funding, so the
exclusion flatters the benchmark). **Window 2022-12-23…2025-09-19, splits 2024-11-22 / 2025-04-21 /
2025-09-19. TEST Sharpe 0.123321 per-period (+2.3560 ann. √365), TEST MaxDD −25.02%, N = 151, DSR
0.93914 at `n_trials = 1` (sr0 = 0.0).** Record + paired series:
`research/benchmarks/perps_equal_weight_benchmark.md` / `..._TEST_returns.csv`. Benchmark **and**
split triple are **frozen**; a candidate on different split dates is void, not weaker evidence.

**A candidate that does not beat the benchmark cannot be promoted, regardless of its other metrics.**
A good Sharpe, a clean walk-forward and a passing DSR do not substitute for beating the thing you
could have held instead.

### Promotion rule — FINAL (operator decision, 2026-08-01; supersedes 2026-07-29)

**Primary metric for the benchmark comparison is TEST-split Sharpe.** A candidate is **PROMOTED only
if ALL SEVEN hold**. Failing any one is **REJECT or PARK**. There is **no discretion** — a Director
or Reviewer may not weigh a strong result on one criterion against a failure on another.

1. **DSR ≥ 0.95 on the TEST split at the current `n_trials`.** **Absolute gate, not a comparison
   against the benchmark**, which is computed at `n_trials = 1` by construction (sr0 = 0.0, DSR
   0.93914). A DSR-vs-DSR comparison would be unclearable by design: the candidate is penalised for
   having been searched for while the benchmark is rewarded for never having been. DSR measures
   selection luck, not skill relative to holding.
2. **Candidate TEST-split Sharpe > 0** in absolute terms.
3. **Candidate TEST-split Sharpe ≥ 1.10 × the benchmark's** — same window, cost model and fill
   assumption; against the committed benchmark, **≥ 0.135653 per-period (+2.5916 annualised)**.
   Compare per-period Sharpes; annualising both sides leaves the ratio unchanged, mixing conventions
   does not. **The paired-difference SE and t-statistic from `validator.sharpe_difference_se()` MUST
   be computed and reported on every candidate but do NOT gate.** A series compared against itself
   gives Δ = 0 and **does not pass** — 1.00 × is not 1.10 ×.
4. **Candidate REALIZED MaxDD ≤ 1.25 × the benchmark's realized TEST MaxDD** — benchmark −25.02%, so
   the cap is **−31.27%**. **Realized only, never the Monte Carlo MaxDD distribution**, which is
   computed on permuted order and overstates dispersion (`validator.monte_carlo` says so itself).
5. **Every validation gate in `NEXT_TASK.md` passed.**
6. **Monte Carlo gate is PASS, not INSUFFICIENT.** A construct whose survival depends on which seeds
   were drawn has not demonstrated survival; **INSUFFICIENT maps to PARK** (see "Monte Carlo gate").
7. **DSR `trial_var_source` is not `"estimator_proxy"`.** Below 10 rows in
   `research/trial_sharpe_ledger.csv` the hurdle falls back to the Lo (2002) proxy, which scales as
   ~1/(n_obs−1) and is not comparable across trade counts. **Until the ledger is populated the
   maximum available verdict is PARK.**

**Why criterion 3 is a ratio and NOT a standard-error gate — do not reintroduce the SE gate without
reading this.** The 2026-07-29 draft required the candidate's TEST Sharpe to beat the benchmark's by
≥ 1 SE of the paired difference. Against the actual benchmark that demands an annualised TEST Sharpe
of **3.06 (ρ = 0.9) to 4.57 (ρ = 0.0)** — **+112% to +208% over the 151-bar TEST window**, versus the
benchmark's +66.28%. It is unclearable, and **the cause is arithmetic, not a property of any
candidate**: SE scales as 1/√N, so at N = 151 one SE is **≈ 2.22 annualised, comparable to the
benchmark's entire annualised Sharpe of 2.36**. A gate whose threshold is the size of the quantity
being measured cannot discriminate. **Statistical separation from the benchmark is a forward-evidence
question; 151 bars cannot establish it** — hence reported, not gating. Reinstating it needs a
materially longer TEST window or an explicit operator decision recorded here.

**Formula for the reported SE.** `r_c`, `r_b` over the `N` **overlapping** TEST bars (identical
dates — per "Like-for-like or void"; `N` is bars, not trades); `S_c`, `S_b` **per-period** Sharpes,
`ρ` their correlation. Jobson–Korkie with Memmel's (2003) correction:

```
SE(Δ) = sqrt( (1/N) · [ 2(1 − ρ) + ½(S_c² + S_b²) − (S_c·S_b/2)(1 + ρ²) ] ),   t = Δ / SE(Δ)
```

**Corrected 2026-08-01**: this manual previously wrote that last term as `−ρ·S_c·S_b`, which is not
Memmel's correction. The forms agree at `ρ = 1` and whenever either Sharpe is zero, and differ
elsewhere by ~0.4% of SE here. `validator.sharpe_difference_se()` was updated to match; **no recorded
result changed**, since by the same decision the SE no longer gates. Series that do not overlap on
identical dates make the comparison void and promotion fails.

**Calibration for Directors — the bars are high on purpose.**

- **TrendVolTarget, the spot program's champion and strongest of ~100 trials, scores DSR 0.02891 on
  TEST at `n_trials = 100`** (`research/measurements/2026-07-30_champion_remeasurement.md`). The 0.95
  bar is retained **knowingly**: most constructs will not approach it, and that is the gate working.
- **The benchmark's TEST window (2025-04-22 … 2025-09-19) is the 74.5th percentile of rolling 151-bar
  windows and second-best of six non-overlapping blocks — a good window, not an extraordinary one.**
  The unusual split is **val**, containing 2025H1, the only negative calendar half-year in the
  series. Splits were reviewed against this evidence and **retained**.

## DSR promotion threshold

Quoted verbatim from `research/research_index.md` standing constraints:

> **DSR gate mandatory**: any candidate reports Deflated Sharpe Ratio (`freqtrade_dsr.py`) at honest
> cumulative `n_trials` and must clear **≥0.95** to be called a real edge. `research_metrics.md` is
> authoritative; the two counts must always match.

**This manual is primary.** The threshold also appears as `freqtrade_dsr.evaluate_freqtrade()`'s
`dsr_threshold` default and in `research/research_index.md` standing constraints; **both are
secondary copies. If any two disagree, this manual governs and the others are the defect** — fix
them, do not re-derive the standard. A dashboard rewritten every cycle and a function default are
not where a permanent standard belongs.

`n_trials` is per-program and resets at a program boundary (see counters above); the **0.95 bar does
not**. The perps program starts at `n_trials = 0` and clears the same threshold.

## Zero-cost pre-gate ladder

**Run before any trial is spent. A hypothesis killed at a pre-gate spends ZERO trials** — `n_trials`
does not advance and the cycle is a successful negative result. Six consecutive hypotheses were
stopped this way before any DSR trial was spent.

Governing principle, quoted from `research/strategy_research_notes.md` (Standing lessons, item 3):

> **Zero-cost pre-gates before any trial** — demonstrate the object the strategy needs EXISTS
> (harvestable regime, stationary spread, adverse target days). Record: 6 valid stops, 1 false
> stop (corrected). Strongest sub-class: a cost-free mathematical upper bound.

The ladder, quoted from the same file (T-035 entry, 2026-07-26):

> reachability → redundancy → lead/lag → episode floor → harm census → TEST concentration

Evaluate in that order and stop at the first failure — the point is to fail cheaply. Per gate:

| # | Gate | What it tests | How it is evaluated |
|---|---|---|---|
| 1 | **Reachability** | Does the data exist and cover the window? | Coverage % over the span. Precedent PASS: F&G 99.87% since 2018-02-01 via free public API. A blocked or short axis stops here. |
| 2 | **Redundancy** | Is the signal distinct from what the strategy already uses? | Correlation vs the incumbent's own signals; **< 0.90** in precedent (F&G −0.1382/0.7011; DVOL level 0.687). |
| 3 | **Lead/lag** | Does the series lead price/vol, or merely react to it? | Cross-correlation at ±k lags. F&G FAIL: avg \|pos-lag\| 0.0076/0.0127 vs avg \|neg-lag\| 0.1405/0.0136 — reactive, not anticipatory. |
| 4 | **Episode floor** | Are there enough events the strategy is in-market for? | In-market episode count vs a **pre-declared floor**. H-IVGate FAIL: 4 spike-onset episodes < 6 required; the gate already avoided 5 of 9 by mechanism. |
| 5 | **Harm census** | Are the days the construct would act on genuinely adverse? | Forward returns on affected days vs unconditional — "are the affected days adverse?". H-IVSizing FAIL: affected days were *better*. |
| 6 | **TEST concentration** | Is the effect one episode, and does it fire in TEST at all? | Share of TEST postdating the last materially-affected day, plus a >0-affected-days check. T-029/T-030 FAIL: ~65%. |

Two mandatory sanity checks, quoted from `strategy_research_notes.md` (lesson 20):

> (a) any lead/lag census must ASSERT that the −k and +k sides differ before its verdict — exact
> k↔−k symmetry between two distinct series is a bug signature; (b) when a diagnostic produces a
> suspiciously clean result (equal to 4 decimals, perfectly monotonic), treat cleanliness as a bug
> signal and verify before interpretation.

Gates are **complementary, not substitutes** — "P1 and P2 pre-gates are complementary and
non-redundant… H-IVSizing passed P1 comfortably but failed P2 decisively." Per lesson 4, **pre-gate
stops get Director reruns**: a stop is a verdict — one sign bug nearly closed the last reachable axis.

Sources: `research/strategy_research_notes.md` (principle, ladder, sanity checks, complementarity);
numeric precedents from `research/archive/index_narrative_pre_2026-07-28.md` rows 21, 22, 37. Both
files unchanged — this is a copy, not a move.

## Falsification conditions must be transcribed literally

**A falsification condition is transcribed into code literally, not paraphrased.**
**"at least one of" is `or`. "both" is `and`.** Substituting one for the other is a **spec deviation
even when the verdict is unchanged** — the code no longer tests the hypothesis that was
pre-registered, and the next case where only one leg fires will be decided by the substitution rather
than by the data.

This failed in two consecutive cycles, both times harmlessly *on that data*: **T-035** (spec said
"at least one of", `phase_feargreed.py:116` coded `and`; both series satisfied the condition anyway)
and **T-034** (singular phrasing, code used a joint two-asset `and`, shelving a significant ETH
result — 56.7%, p=0.0029 — by design). "It didn't change the answer" is not a defence; it is luck.

**Where a condition is genuinely ambiguous, the Engineer BLOCKS and quotes the sentence.** Singular
phrasing applied to a multi-asset hypothesis is the archetype: *"the hit ratio must be significant"*
across two assets does not say whether one leg or both must clear. Do not choose an interpretation,
do not pick the conservative one, do not note it and proceed. Block, quote the exact sentence, and
let the Director disambiguate — a blocked cycle costs a day, an unstated interpretation costs the
result's meaning.

**Reviewer duty: check every falsification condition against its corresponding code line.** Record
any `and`/`or` mismatch as a spec deviation, and state explicitly whether it was outcome-changing.
Both are required — an outcome-changing mismatch invalidates the cycle, a non-outcome-changing one is
still a deviation and is still reported.

## Monte Carlo gate

The MC gate has three outcomes, not two. **PASS requires the 5th-percentile Sharpe to be > 0 for
EVERY seed individually** — not merely for the pooled distribution.

| Outcome | Condition | Disposition |
|---|---|---|
| **PASS** | every seed's p5 Sharpe > 0 | eligible to continue |
| **FAIL** | every seed's p5 Sharpe ≤ 0 | REJECT |
| **INSUFFICIENT** | seeds disagree in sign | **PARK, never PROMOTE** |

**An INSUFFICIENT result maps to PARK. A construct whose survival depends on which seeds were drawn
has not demonstrated survival** — the pooled figure's sign is an accident of the draw, and reporting
it as PASS or FAIL asserts something the run did not establish. INSUFFICIENT is not a soft FAIL and
not a near-PASS; it is the absence of a result.

**`n_sims` may be raised to tighten the estimate, but only as a PRE-REGISTERED choice in
`NEXT_TASK.md`.** Raising it after seeing a straddling result is choosing the seed set that gives the
answer you want, and it invalidates the cycle. If a construct comes back INSUFFICIENT, it parks; the
re-run is a new, pre-registered cycle.

Per-seed values are carried on `Verdict.warnings`, so INSUFFICIENT cannot be reported otherwise.

## File ownership — Engineer / Reviewer division (2026-08-02)

**This manual is primary**; the same division appears verbatim in `prompts/engineer.md` and
`prompts/reviewer.md`, which are the defect if they disagree.

- **Engineer writes:** `research/results/<Task ID>_report.md`, the raw artifacts under
  `research/results/<Task ID>_raw/`, the scripts under `user_data/research/`. **Nothing else.**
- **Reviewer writes:** `research_index.md`, `research_metrics.md`, `strategy_iteration_log.md`,
  `strategy_research_notes.md`, `hypothesis_bank.md`, both `review_briefs/` files.

The per-field split of `research_metrics.md` is **RETIRED** — a file two roles edit in one cycle
cannot be audited; the Reviewer transcribes the report's headline numbers after reconciling them
against its own reproduction, and disagreement is an **INVALID CYCLE** finding, never a silent fix.
**`NEXT_TASK.md` may NARROW this per cycle but may NOT widen it.** An Engineer writing a
Reviewer-owned file is a **spec deviation**, recorded as such.

## Independent Reviewer output standard

**A review brief must not exceed 4 KB (4,096 bytes).** The cap stands even though the latest brief
was demoted to on-demand on 2026-08-01: the Director should be able to open it *without* budget
anxiety, and a brief that is cheap to read is one that actually gets read. The cap now protects an
optional load rather than rationing a mandatory one.

A brief contains: the verdict; the falsification condition and whether it fired; what the Reviewer
independently reproduced and what they could not; any defect found, with its outcome-changing status
stated explicitly; and the resulting `n_trials`. Nothing else.

Everything longer belongs in the cycle's own report (`research/results/T-*_report.md`), which is
unbounded and on-demand. The brief is a verdict record, not a narrative. If a brief cannot be written
in 4 KB, the excess is analysis — put it in the report and cite it from the brief.

Enforced by `scripts/check_context_budget.py`, which counts the highest-Task-ID file in
`research/review_briefs/` against the mandatory budget.

## STANDING_DIRECTIVES.md is capped

**`research/STANDING_DIRECTIVES.md` is capped at 4,096 bytes.** Each directive is at most **three
sentences**: the binding rule, the decisive evidence in one clause, and the scope limit. Evidence,
derivations and caveats live in `research/strategy_research_notes.md`, which is off-budget and
unbounded; the directive carries a pointer.

**When the cap is reached, the Meta-Reviewer consolidates** — merging directives that express one
rule, and retiring any superseded by an explicit naming directive. **Directives are never renumbered
and gaps are preserved.** **Raising the cap is not an available remedy:** a directives file too long
to be read every cycle is not binding on anyone.

**Why this exists.** The file is fully mandatory, grows monotonically, and every meta-review adds to
it. It reached 8,899 B at ten directives and was the second-largest mandatory item — on track to
consume the Director's context budget by itself, which is the fourth budget crisis this project has
had. It was compacted to the cap on 2026-08-02 with no rule text lost; the displaced evidence is in
`strategy_research_notes.md`, "Evidence displaced from STANDING_DIRECTIVES.md".

## Champion Classification & Progression Pipeline

**Classification Hierarchy**: Research Candidate → Research Champion → Production Candidate →
Production Champion

**Definitions**
*   **Research Champion:** Strongest validated strategy currently known. NOT production ready. Expected to be challenged continuously. Remains in research mode.
*   **Production Candidate:** Requires multiple successful Meta Reviews, extensive challenger testing, competition mode completion, cross-regime robustness, parameter stability, extensive Monte Carlo validation, and satisfactory validation metrics.
*   **Production Champion:** Requires successful paper trading, successful production validation, and continued robustness requirements. Only Production Champions are eligible for live deployment.

**Progression Pipeline**: Research Champion → additional experiments → multiple successful Meta
Reviews → Competition Mode → Champion Improvement → Champion Challenging → cross-regime validation
→ additional robustness testing → **Production Candidate** → paper trading → production validation
→ **Production Champion** → live deployment

⸻

<!-- DIRECTOR-MANDATORY-END -->

## Performance Objective

Never optimize solely for profit.

Rank strategies using a balanced score including:
* robustness
* consistency
* Sharpe
* Deflated Sharpe
* Sortino
* Calmar
* Profit Factor
* Expectancy
* Max Drawdown
* stability across years
* stability across market regimes
* parameter robustness
* trade count
* simplicity
* capital efficiency
* consistency across coins
* consistency across timeframes
* live-trading realism
* correlation with existing validated strategies

A lower-return strategy that is substantially more robust should rank above a fragile high-return strategy.

⸻

## Strategy Portfolio Evolution

As research progresses, determine whether multiple complementary strategies outperform a single universal strategy.

Possible categories include:
* Trend Following
* Mean Reversion
* Breakout
* Momentum
* Pullback Continuation
* Volatility Expansion
* Volatility Compression
* Range Trading

Measure correlation between strategy returns. Prefer independent sources of edge. Avoid maintaining multiple highly correlated strategies. Maintain `strategy_portfolio.md` accordingly.

⸻

## Continuous Research Mode
Research cycles are executed through:

Research Director
→ selects hypothesis

Research Engineer
→ implements and validates

Independent Reviewer
→ audits and renders verdict

Meta Review
→ every 25-50 cycles

The default action after promotion of a Champion strategy is to continue research. Promotion does not imply readiness for paper trading or live deployment.

⸻

## Research Principles

Never manipulate validation criteria.
Never optimize for one coin.
Never optimize for one market cycle.
Never optimize for one year.
Never optimize solely for CAGR.
Never hide weaknesses.
Never exaggerate confidence.
Never prioritize appearance over statistical validity.
Always report negative findings.
Always explain uncertainty.

Prefer simple, explainable systems over unnecessarily complex ones when performance is comparable.

The ultimate goal is not to find the highest historical return.

The ultimate goal is to build a continuously improving quantitative research platform capable of discovering, validating, maintaining, retiring, and replacing statistically robust trading edges over many years.

If evidence shows that a diversified portfolio of strategies is more robust than a single strategy, prefer the portfolio.

Post-promotion reconciliation. Any champion deployed to paper or live trading must be reconciled against an out-of-sample backtest run over the identical period. Material divergence is investigated before capital is committed and attributed to a specific cause: fill assumptions, fees/slippage, data differences, or overfitting. Unexplained divergence demotes the champion.

⸻

## Initial Task

Before writing any strategy code:

1. Read:
   * `research/research_index.md`
   * `research/strategy_iteration_log.md`
   * `research/strategy_research_notes.md`
   * `research/best_strategy_so_far.py`
   * `research/strategy_portfolio.md` (if it exists)
2. Summarize the current research state.
3. Identify the strongest validated edge.
4. Identify unresolved weaknesses.
5. Identify the highest-priority unexplored hypothesis.
6. Proceed to Phase 1 of the research process.

Under the autonomous research framework,
research proceeds through:

Research Director
→ Research Engineer
→ Independent Reviewer

NEXT_TASK.md serves as the formal authorization
for a research cycle.

⸻

## OPERATOR PRINCIPLE

The purpose of this project is continuous scientific discovery.

The project should assume:

- most hypotheses will fail,
- most strategies will be rejected,
- most Champions will eventually be replaced,
- negative findings are valuable,
- statistical honesty is preferable to profitability,
- durability is preferable to short-term performance.

A strategy surviving hundreds of research cycles without deployment is preferable to a fragile strategy deployed prematurely.

Live trading is a possible consequence of successful research—not the goal of the research itself.

Research effort should be divided between:

- Novel hypothesis generation
- Champion improvement
- Champion challenge
- Portfolio diversification

The Director should not exclusively
assign novel hypotheses if evidence suggests
the current Champion can be materially improved.


