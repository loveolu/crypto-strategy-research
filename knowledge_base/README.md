# Trading Knowledge Base — AI Research Library

## Purpose

This is a **permanent AI Research Library**: a self-contained system that lets any future AI researcher (Claude, DeepSeek, GPT, Gemini, or another model — as well as human researchers) conduct high-quality systematic/algorithmic trading research **without ever needing to re-read the five original source books**, and without needing to rediscover this project's own research process from scratch.

It has two distinct layers, built for two different purposes:

- **Knowledge layer** (files `01`-`18` plus `master_index.md`) — everything the five books say, reorganized by topic instead of by book, with full source traceability.
- **Research-operations layer** (`hypothesis_bank.md`, `implementation_patterns.md`, `EDGE_FRAMEWORK.md`, `AI_RESEARCH_PLAYBOOK.md`) — the reasoning and process layer built on top of the knowledge layer: what hypotheses are worth testing, what reusable building blocks exist, how to think about durable edges, and — most importantly — the operating manual for actually doing research with all of this.

Rather than requiring a reader to work through five separate books to find, say, "what do these authors say about position sizing," this knowledge base reorganizes their combined content into 18 topic files, each pulling together everything the five books say about a single subject — trend-following, mean reversion, position sizing, backtesting validation, and so on — with full source traceability back to the originating book and chapter. On top of that, the research-operations layer answers a different question: not "what do the books say," but "what should I, an AI researcher, actually DO next."

**This knowledge base is not a summary or a shortcut past the source material — it is a faithful, exhaustively cross-referenced reorganization of it.** Every substantive claim traces to a specific book and chapter. Nothing is invented. Where the books disagree, contradict themselves, or leave a gap, that disagreement or gap is preserved and flagged, not smoothed over. The research-operations layer is held to the same standard: it distinguishes explicitly between what the books claim, what all five books agree on, and what this project has actually confirmed or refuted on its own crypto data — these are three different tiers of evidence, never collapsed into one.

## The five source books

| Book | Author | Edition | Published |
|---|---|---|---|
| *The Evaluation and Optimization of Trading Strategies* | Robert Pardo | 2nd edition | 2008 |
| *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* | Ernest P. Chan | 1st edition | 2009 |
| *The Mathematics of Money Management: Risk Analysis Techniques for Traders* | Ralph Vince | 1st edition | 1992 |
| *Python for Algorithmic Trading: From Idea to Cloud Deployment* | Yves Hilpisch | 1st edition (O'Reilly) | 2020 |
| *Trading Systems and Methods* | Perry J. Kaufman | 6th edition (Wiley) | 2019/2020 |

## How this knowledge base was built

Construction happened in two stages:

**Stage 1 — Verbatim per-book extraction.** Each book was read in full (every chapter, cover to cover) and extracted into a dedicated per-book folder under `Knowledge\<Author>_<Short_Title>\`. Each folder contains:
- `01_Overview.md` — bibliographic info, table of contents, core philosophy
- `02_Chapter_NN_*.md` — one file per chapter, with the chapter's full content, formulas, worked examples, and an "Ambiguities" section flagging any extraction gaps (e.g., formulas rendered as un-extractable embedded graphics in the source PDF)
- `Master_Summary.md` — the book's own navigation index, author insights, warnings/limitations, and open questions
- `Strategies.md`, `Indicators.md`, `Concepts.md`, `Risk_Management.md`, `Algorithmic_Trading.md`, `Research_Ideas.md`, `Crypto_Specific.md`, `Psychology.md`, `Glossary.md` — cross-cutting reference files consolidating that book's content by theme
- `Progress_Log.md` — the extraction session's own completeness log

These per-book folders are the **deeper, rawer layer** of this knowledge base. They remain in place at `Knowledge\` and are the correct place to drill into a book's own original chapter-by-chapter treatment, worked examples, and exact wording.

**Stage 2 — Topic consolidation.** The 18 numbered files in this folder cut across all five books' extractions by *topic* rather than by book, so a reader interested in (say) volatility can read one file that synthesizes what Vince, Chan, Pardo, Hilpisch, and Kaufman each say about volatility, rather than reading five books' worth of scattered volatility mentions. Every claim in these topic files is tagged with its source `(Book, Ch.N)` so a reader can trace back to the deeper per-book layer for full context, exact wording, or a worked example. This stage was followed by two exhaustive completeness-audit passes (one book-by-book targeted audit, one fully exhaustive re-read including previously under-visited cross-cutting source files) — see `master_index.md`'s scope note and the `audit/` subfolder for that record.

**Stage 3 — Research-operations layer (`master_index.md`, `hypothesis_bank.md`, `implementation_patterns.md`, `EDGE_FRAMEWORK.md`, `AI_RESEARCH_PLAYBOOK.md`).** The 18 topic files answer "what do the books say." This layer answers "what should a researcher actually do with that." `hypothesis_bank.md` extracts every distinct backtestable hypothesis into structured cards (and cross-checks each against this project's own prior empirical tests, flagging any already-rejected paradigm rather than letting a future researcher re-derive a known dead end). `implementation_patterns.md` catalogs the reusable, composable building blocks (trend filters, sizing patterns, exit structures, etc.) that strategies get assembled from. `EDGE_FRAMEWORK.md` is the philosophical foundation — what makes an edge durable, why strategies fail, where the five books agree or disagree, explicitly separated from what this project has actually confirmed on its own crypto data. `AI_RESEARCH_PLAYBOOK.md` is the operating manual that ties all of this together into a concrete research workflow.

## File map

| # | File | Scope |
|---|---|---|
| — | **`AI_RESEARCH_PLAYBOOK.md`** | **Start here for process.** The operating manual: how to choose what to investigate, navigate the library, diagnose failures, validate correctly, and log results. A literal "Quick Start" checklist for a fresh research session is at the bottom. |
| — | **`EDGE_FRAMEWORK.md`** | **Start here for philosophy.** What creates a durable edge, why most strategies fail, which ideas have real cross-book/empirical support vs. single-book claims, warning signs of overfitting. |
| — | `hypothesis_bank.md` | Every distinct backtestable hypothesis from the five books, as structured cards (description, supporting concepts, indicators, expected conditions/weaknesses, related hypotheses, source attribution) — cross-checked against this project's own tested/rejected paradigms. |
| — | `implementation_patterns.md` | Reusable, composable strategy building blocks — trend/volatility filters, breakout confirmation, position-sizing patterns, ATR usage patterns, adaptive smoothing, confirmation logic, exit structures — with when-to-use/avoid and common mistakes. |
| — | `master_index.md` | Alphabetical A-Z lookup of every concept/indicator/strategy/technique in the whole library, with the file(s) each appears in. Use this when you know the term but not which file covers it. |
| 01 | `01_market_structure.md` | Market structure fundamentals: how prices move, market types, efficiency, liquidity, order flow |
| 02 | `02_trend_following.md` | Trend-following systems: moving averages, breakout trends, channel/band systems, why trend-following works |
| 03 | `03_mean_reversion.md` | Mean-reversion and statistical-arbitrage strategies: cointegration, pairs trading, oscillator-based reversion |
| 04 | `04_breakouts.md` | Breakout systems: range breakouts, N-day breakouts, volatility breakouts, opening-range breakouts |
| 05 | `05_momentum.md` | Momentum and oscillator-based strategies: RSI, MACD, stochastics, divergence, momentum persistence |
| 06 | `06_volatility.md` | Volatility measurement and volatility-based strategies: ATR, historical/implied vol, volatility regimes |
| 07 | `07_market_regimes.md` | Regime detection and classification: noise measures, cycle analysis, trend-vs-choppy classification |
| 08 | `08_entries.md` | Entry-signal design and timing across all strategy families |
| 09 | `09_exits.md` | Exit-signal design: stops, targets, trailing exits, time-based exits |
| 10 | `10_position_sizing.md` | Position-sizing mathematics: Kelly criterion, optimal f, volatility-based sizing |
| 11 | `11_risk_management.md` | Risk control: stop-loss taxonomy, drawdown management, risk of ruin, VaR |
| 12 | `12_portfolio_construction.md` | Portfolio-level construction: diversification, correlation, efficient frontier, multi-strategy allocation |
| 13 | `13_indicator_reference.md` | Consolidated indicator reference: every named indicator across all five books, with formulas |
| 14 | `14_backtesting_and_validation.md` | Backtesting methodology and validation: walk-forward analysis, overfitting detection, degrees of freedom, in/out-of-sample discipline |
| 15 | `15_crypto_specific.md` | Every crypto/Bitcoin mention across all five books (all incidental — none of the books is crypto-focused), plus clearly-labeled project inferences about crypto transferability |
| 16 | `16_research_hypotheses.md` | Every future-research idea, open question, and author-flagged gap across all five books, organized by theme |
| 17 | `17_author_disagreements.md` | Every place the five books disagree, diverge in emphasis, or contradict themselves internally |
| 18 | `18_common_failure_modes.md` | Every documented way a strategy or trader can fail: overfitting, overleveraging, regime shifts, psychological failure modes |
| — | `README.md` (this file) | Front door: purpose, sources, construction method, file map, reliability notes, usage guidance |
| — | `audit/` | Completeness-audit reports (one per book) from the two remediation passes — a record of what was checked and fixed, not a reference file itself |

Files 01-13 cover strategy paradigms, signal design, and risk/portfolio mathematics. File 14 covers the validation methodology that should gate any strategy built from files 01-13 before it is trusted. Files 15-18 are cross-cutting: crypto applicability, research directions, where the sources disagree, and how things go wrong — each pulls from all 18 topic areas and all five books rather than covering a single strategy paradigm. The five research-operations files sit above all of this and are where a researcher should actually start (see "Recommended reading order" below).

## Recommended reading order

This library is large (20+ files, well over 1.5MB of consolidated content). A fresh AI researcher should NOT read it front to back. Recommended path:

1. **This README** (you're here) — orientation.
2. **`AI_RESEARCH_PLAYBOOK.md`** — the operating manual. This is the single most important file for actually doing research; read it before anything else in this folder.
3. **`EDGE_FRAMEWORK.md`** — the philosophy that the playbook's decisions rest on.
4. **`hypothesis_bank.md`** — skim the thematic section relevant to whatever you're currently investigating; don't read it cover to cover.
5. **`implementation_patterns.md`** and the relevant numbered topic file(s) (01-14) — only once you've picked a specific hypothesis and need the building blocks/exact formulas to implement it.
6. **`master_index.md`** — use as a lookup tool throughout, not a reading target.
7. **`Knowledge\<Author>_<Short_Title>\`** — drill into the original book's chapter file only when a topic file's citation isn't enough (e.g., you need the author's full worked example or exact wording).
8. This project's own **`research/` folder** (`research/research_index.md`, `research/strategy_iteration_log.md`, `research/strategy_research_notes.md`, `research/best_strategy_so_far.py`, `research/strategy_portfolio.md`, plus `research/current_champion.md`, `research/research_metrics.md`, `research/NEXT_TASK.md`) is NOT part of this knowledge base — it's the project's own live research state, referenced throughout `AI_RESEARCH_PLAYBOOK.md` and `hypothesis_bank.md`, and must be read before starting any new research cycle regardless of what this library says.

## Reliability notes

**Traceability convention.** Every substantive claim in every topic file is tagged `(Book, Ch.N)` — e.g., `(Kaufman Ch.21)`, `(Vince Ch.4)`. This tag means: consult that book's `02_Chapter_NN_*.md` file in `Knowledge\<Author>_<Short_Title>\` for the full original treatment, exact wording, and any worked example the topic file only summarizes.

**Author-claim vs. project-inference labeling is preserved exactly, never collapsed.** Several source extractions (most extensively Kaufman's `Crypto_Specific.md` and `Research_Ideas.md`) distinguish between what an author actually states and what this project's own research process inferred or extrapolated from the author's general principles. That distinction is preserved verbatim in files 15 and 16 of this knowledge base — a labeled "project inference" is never presented as if it were an author's claim, and vice versa. Where you see "project inference, not sourced" or similar language, that means: this project extrapolated the idea from the author's general methodology, but the author never said it, tested it, or validated it.

**Formula-gap flags are preserved, not silently filled in.** The source PDFs (particularly Kaufman's 2,285-page book) render many inline equations as embedded graphics that did not survive text extraction, and no PDF page-rendering tool was available during extraction. Every such gap is flagged in the relevant chapter file's "Ambiguities" section rather than guessed at. A small number of genuinely standard, unambiguous published formulas (e.g., Hull Moving Average, Shannon entropy, Wilder's ADX chain, standard Markowitz mean-variance forms) were reconstructed from well-known published definitions and explicitly labeled as reconstructions, not as directly extracted from the source text.

**Internal source inconsistencies are preserved, not corrected.** Where a book contradicts itself — Kaufman has six documented internal inconsistencies across chapters (Ch.14, 17, 18, 22, 23, 24); Pardo has an unreconciled walk-forward-window-ratio discrepancy between Ch.6 and Ch.11; Vince has several minor numerical table errors; Hilpisch has an unreconciled bar-length mismatch between backtested and live-deployed code — these are documented in full in `17_author_disagreements.md` §8, not silently fixed anywhere in this knowledge base. If a formula or rule as printed in the source looks internally inconsistent, that inconsistency is the source's own, and is called out rather than resolved by guesswork.

**All five books are pre-crypto or nearly so.** Vince (1992) and Pardo (2008) predate Bitcoin entirely. Chan (2009) was published essentially concurrently with Bitcoin's genesis block and contains zero mentions. Kaufman (2019) contains exactly 3 incidental Bitcoin mentions in 2,285 pages, none of which describe a crypto trading system. Hilpisch (2020) is the only book with any deliberate crypto engagement, and even there it is limited to data-plumbing demonstrations (a Quandl BTC/USD retrieval demo, an FXCM crypto-CFD instrument-list printout) — never a backtested crypto strategy. See `15_crypto_specific.md` for the full, exhaustive catalog of every direct mention plus the clearly-labeled project inferences about what methodology plausibly transfers to crypto markets. Treat any crypto-specific claim elsewhere in this knowledge base as a labeled inference unless it appears in file 15's verbatim-mentions section.

**Commercial and personal disclosure notes.** Pardo's book repeatedly references his own firm's Walk-Forward Analysis software products (Walk-Forward Analyst, TradeProfiler) alongside his methodological claims about WFA's near-indispensability — a disclosed commercial interest worth weighing when reading his WFA-centric recommendations (see `17_author_disagreements.md` §4). Several of Chan's claims rest on personal anecdote, private conversation, or a single unpublished source rather than peer-reviewed literature (e.g., the decimalization-hurts-stat-arb claim, the risk-parity 23/77 recommendation, an unverified rumor about a rogue trader) — these are flagged in the underlying Chan extraction and are not treated as more authoritative than their actual evidentiary basis warrants.

## Guidance for future researchers

0. **Read `AI_RESEARCH_PLAYBOOK.md` first, before anything else in this folder.** It is the operating manual — how to choose what to investigate, navigate this library, diagnose a failed strategy, validate correctly, and log results — and ends with a concrete "Quick Start for a New Research Session" checklist. Everything below is knowledge-layer guidance that the playbook already points to at the right moments; you shouldn't need to reason through this list manually once you've read the playbook.
1. **Start with the topic file, not the book.** If you have a specific question ("what do these books say about volatility targeting," "how should I validate a new strategy before trusting it"), go to the relevant numbered topic file (01-18) first, or `master_index.md` if you're not sure which one. It synthesizes all five books' treatment of that topic in one place, with source tags.
2. **Drill into the per-book chapter file for depth.** Once a topic file's `(Book, Ch.N)` tag identifies which chapter has the fuller treatment, open `Knowledge\<Author>_<Short_Title>\02_Chapter_NN_*.md` for the original wording, the full worked example, and that chapter's own "Ambiguities" section.
3. **Check `15_crypto_specific.md` before assuming anything crypto-relevant.** None of the five books validates a crypto strategy. Any crypto application of this knowledge base's content is this project's own hypothesis, to be tested with the same rigor `14_backtesting_and_validation.md` and `18_common_failure_modes.md` describe — not assumed to work merely because a traditional-market analog is described here.
4. **Read `17_author_disagreements.md` before adopting a single author's framing as "the" answer.** Several of the most load-bearing methodological questions in this field (how to size positions relative to Kelly/optimal f, how much validation machinery a strategy needs before being trusted, whether trend-following or mean-reversion deserves more default confidence) are genuinely disputed across these five books. This knowledge base does not adjudicate those disputes — it presents each author's position, reasoning, and evidence side by side so a researcher can make an informed choice for their own context.
5. **Use `18_common_failure_modes.md` as a pre-mortem checklist** before trusting any new strategy result — most of the failure modes catalogued there (overfitting via insufficient degrees of freedom, price-shock contamination, peak-parameter fragility, live-vs-backtest divergence) are cheap to check for and expensive to discover only after real capital is committed.
6. **Use `hypothesis_bank.md`, not `16_research_hypotheses.md`, as your starting point for picking a next experiment.** `16_research_hypotheses.md` is the raw author-suggested/open-question material; `hypothesis_bank.md` is the researcher-facing distillation of it (plus every named strategy in the knowledge base) into structured, testable cards, already cross-checked against this project's own prior experiments. Prefer a hypothesis NOT already flagged "already tested" there, and prefer a genuinely new mechanism or data axis over a parameter variation of something already tried — this project's own history (`research/research_index.md`) shows parameter variations of tested paradigm families reliably fail.
7. **Assemble, don't invent, when constructing a new strategy.** Use `implementation_patterns.md` for the composable building blocks (a trend filter, a sizing pattern, an exit structure) rather than designing a novel mechanism from scratch — novelty for its own sake is not what this library's evidence supports as valuable; recombination of well-understood, individually-validated components is.
8. **Every new experiment must clear this project's own validation pipeline, not just "sound reasonable" against this knowledge base.** `14_backtesting_and_validation.md` explains WHY each validation stage exists; `user_data/research/validator.py` and `freqtrade_dsr.py` at the repo root are what ACTUALLY runs. Passing the walk-forward/Monte Carlo/DSR gate is mandatory regardless of how well-supported a hypothesis looks in `hypothesis_bank.md` or `EDGE_FRAMEWORK.md`.
