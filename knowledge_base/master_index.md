# Master Index

This is a master alphabetical index of the trading knowledge base at `knowledge_base\` (README.md
plus files `01_market_structure.md` through `18_common_failure_modes.md`, which itself consolidates
five trading books — Pardo, Chan, Vince, Hilpisch, Kaufman — plus four bridge/foundation files built on
top of that base: `hypothesis_bank.md` (83 named, backtestable hypothesis cards), `implementation_patterns.md`
(31 composable strategy building-block patterns), `EDGE_FRAMEWORK.md` (the philosophical foundation —
what makes an edge durable, why strategies fail), and `AI_RESEARCH_PLAYBOOK.md` (the process/workflow
manual for running a new hypothesis through this project's own research pipeline)). **This index
contains no content of its own** — it is a pure lookup tool. Every entry points to the file(s) where
the concept, indicator, strategy, technique, or idea actually lives; the formulas, worked examples,
source-book attributions, and full explanations remain in those files, not here.

**How to use this file**: find the term you're looking for (alphabetically), note which file(s) it
appears in, then open that file and use its own section headers (or Ctrl+F the term) to navigate to
the relevant passage. If a term appears in multiple files, each occurrence generally reflects a
different angle on the same concept (e.g., Kelly criterion is introduced in `10_position_sizing.md`,
disputed across authors in `17_author_disagreements.md`, and cross-referenced for its crypto
leverage-cap implications in `15_crypto_specific.md` and `16_research_hypotheses.md`).

File key: `01`=market_structure, `02`=trend_following, `03`=mean_reversion, `04`=breakouts,
`05`=momentum, `06`=volatility, `07`=market_regimes, `08`=entries, `09`=exits,
`10`=position_sizing, `11`=risk_management, `12`=portfolio_construction, `13`=indicator_reference,
`14`=backtesting_and_validation, `15`=crypto_specific, `16`=research_hypotheses,
`17`=author_disagreements, `18`=common_failure_modes. Plus four bridge/foundation files, cited by
full name (not a number) throughout this index: `hypothesis_bank.md` (83 hypothesis cards, organized
by research theme), `implementation_patterns.md` (31 composable building-block patterns),
`EDGE_FRAMEWORK.md` (durable-edge philosophy), `AI_RESEARCH_PLAYBOOK.md` (research process/workflow).

---

## A

**AAII Survey** — 07_market_regimes.md
**Abuse of Hindsight** — 14_backtesting_and_validation.md, 18_common_failure_modes.md — Pardo's three cautionary narratives
**Accumulated Swing Index (ASI)** — 02_trend_following.md, 13_indicator_reference.md
**Accumulation/Distribution** — 05_momentum.md, 13_indicator_reference.md
**Accumulative Average (moving average)** — 02_trend_following.md, 13_indicator_reference.md
**Acceleration (momentum of momentum)** — 05_momentum.md
**Acceleration Factor (AF)** — 02_trend_following.md, 09_exits.md, 13_indicator_reference.md — Parabolic SAR parameter
**Action and Reaction** — 08_entries.md — Kaufman's behavioral price-movement framing
**AdaBoost** — 08_entries.md, 14_backtesting_and_validation.md, hypothesis_bank.md ("AdaBoost Direction Classifier") — Hilpisch ensemble-method strategy
**AdaBoost Direction Classifier** — see AdaBoost
**Adaptive Momentum Transformations** — 13_indicator_reference.md
**Adaptive Price Zone (APZ)** — 04_breakouts.md, 02_trend_following.md, 08_entries.md, 13_indicator_reference.md
**Adaptive RSI / Adaptive Stochastic** — 07_market_regimes.md, 02_trend_following.md, 13_indicator_reference.md, implementation_patterns.md ("Efficiency-Adaptive Smoothing Constant" pattern)
**Adaptive Trend-Speed Systems** — hypothesis_bank.md — KAMA/VIDYA/Adaptive-R²/MAMA-FAMA/FRAMA/Mart's Master Trading Formula family, umbrella hypothesis card
**Adaptivity as a Re-Optimization Process** — implementation_patterns.md — periodic re-test/re-optimize vs. a continuous adaptive-smoothing formula
**ADX (Average Directional Movement/Index)** — 05_momentum.md, 07_market_regimes.md, 08_entries.md, 12_portfolio_construction.md, 13_indicator_reference.md, hypothesis_bank.md, implementation_patterns.md
**ADX / Directional-Movement Regime Gate** — implementation_patterns.md — trend-strength (not cleanliness) regime filter
**ADX-Filtered Oscillator (Kestner) & Directional Parabolic** — hypothesis_bank.md — see also Oscillator Method with ADX Filter (Kestner)
**ADX Trend / No-Trend Regime Gate** — hypothesis_bank.md
**ADXR** — 13_indicator_reference.md
**Advance-Decline Index** — 01_market_structure.md, 13_indicator_reference.md
**Ahead of the Crowd 8-18 Day Crossover** — 02_trend_following.md, 08_entries.md
**Alexander Elder** — 02_trend_following.md — see Elder's Triple Screen Trading System
**Alpha generation (Hilpisch definition)** — 01_market_structure.md
**Alpha-Driven Weighting (portfolio)** — 06_volatility.md, 12_portfolio_construction.md
**Alphacet Discovery (Chan Example 7.1)** — 05_momentum.md, hypothesis_bank.md ("Data-Mining Turning-Points Regime-Trigger Model (Alphacet)")
**Alphier Expectation** — 13_indicator_reference.md
**Alternating Peaks (divergence)** — 05_momentum.md
**Alternating Random/Test Periods (validation)** — 14_backtesting_and_validation.md
**Amaranth Advisors** — 07_market_regimes.md, 11_risk_management.md, 12_portfolio_construction.md, 18_common_failure_modes.md — natural-gas loss cited as blowup example
**Anti-Martingale sizing** — 08_entries.md, 10_position_sizing.md, 18_common_failure_modes.md
**Apophenia** — 18_common_failure_modes.md — Fibonacci-Lucas overfitting warning
**AI_RESEARCH_PLAYBOOK.md** — bridge/foundation file — the operating manual/process layer for this project's own research loop, session quick-start, and validation pipeline; see header key
**Arbitrage (Kaufman's definition)** — 03_mean_reversion.md
**ARIMA (Autoregressive Integrated Moving Average)** — 13_indicator_reference.md
**Arithmetic Average HPR (AHPR)** — 12_portfolio_construction.md
**Arms Index / TRIN** — 01_market_structure.md, 13_indicator_reference.md
**Aronson's Descriptor/Trade-Profile Pattern-Discovery Method** — 14_backtesting_and_validation.md, 16_research_hypotheses.md, hypothesis_bank.md ("Aronson's Descriptor / Trade-Profile ML Labeling")
**Asymmetric-error-cost framing (Type I vs Type II)** — 18_common_failure_modes.md
**Asymmetric-scrutiny debiasing rule** — 18_common_failure_modes.md — "surprisingly good results are as suspect as bad ones"
**Aspray's Demand Oscillator (DO)** — 13_indicator_reference.md
**ATR-Based Regime Gate (Absolute Threshold)** — implementation_patterns.md
**ATR-Based Unit Sizing** — implementation_patterns.md — Turtles' L-based sizing; see also Average True Range (ATR)
**ATR Usage Patterns (Stop Distance / Sizing Denominator / Regime Filter / Trailing-Stop)** — implementation_patterns.md — four distinct, source-documented jobs sharing one indicator
**Auction Theory** — 01_market_structure.md
**Autocorrelation / Durbin-Watson d-statistic** — 13_indicator_reference.md
**Automatic Gain Control (AGC)** — 02_trend_following.md
**Autoregressive functions (trend forecasting)** — 02_trend_following.md
**Average Directional Movement** — see ADX
**Average Maximum Retracement (AMR)** — 11_risk_management.md
**Average True Range (ATR)** — 06_volatility.md, 13_indicator_reference.md, implementation_patterns.md (ATR Usage Patterns)
**Average Volume** — 13_indicator_reference.md
**Average-Modified / Average-Off Method** — 02_trend_following.md, 13_indicator_reference.md
**Average-of-all-tests reporting convention** — 16_research_hypotheses.md — vs. peak-test reporting
**Awesome Oscillator (AO)** — 05_momentum.md, 13_indicator_reference.md

## B

**Back-Adjusted / Front-Adjusted Continuous Contract** — 14_backtesting_and_validation.md, 15_crypto_specific.md
**Backwardation / Contango** — 07_market_regimes.md, 03_mean_reversion.md, 15_crypto_specific.md
**Balanced Risk Allocation** — 12_portfolio_construction.md
**Basic Momentum Trend-Following** — hypothesis_bank.md — n-day momentum sign as the simplest trend system
**Bear Trap / Bull Trap** — 04_breakouts.md
**BTC-Dominance Rotation / ETH-BTC Z-Score Fade** — hypothesis_bank.md — project's own construction, not sourced from the five books
**BTC-ETH Cointegration Pairs Trading** — hypothesis_bank.md — see also Cointegration
**Bearish/Bullish Divergence** — 05_momentum.md
**Benoit Mandelbrot's fractal-distribution finding** — 01_market_structure.md, 11_risk_management.md, 16_research_hypotheses.md
**Bernoulli-utility risk-preference framing** — 16_research_hypotheses.md, 11_risk_management.md — Utility Theory, 1738
**Big Fish in a Small Pond Syndrome** — 14_backtesting_and_validation.md, 16_research_hypotheses.md, 18_common_failure_modes.md
**Bill Williams' 5-Bar Fractal Breakout** — 04_breakouts.md, hypothesis_bank.md
**Billy Williams' Rattlesnake Breakout Method** — 04_breakouts.md, 02_trend_following.md, implementation_patterns.md (worked 3-of-3 Confirmation Logic example)
**Binomial Probability of a Run of Losses** — 11_risk_management.md, 14_backtesting_and_validation.md
**Bjorgen and Leuthold Study (insider selling)** — 01_market_structure.md, 07_market_regimes.md
**Black-Scholes Option Pricing Model** — 06_volatility.md, 10_position_sizing.md
**Black futures-option model** — 10_position_sizing.md
**Blau's Double Smoothing of Price Changes** — 02_trend_following.md, 13_indicator_reference.md
**Bolton-Tremblay Indicator** — 01_market_structure.md, 13_indicator_reference.md
**Bollinger Bands** — 02_trend_following.md, 03_mean_reversion.md, 04_breakouts.md, 08_entries.md, 13_indicator_reference.md, implementation_patterns.md
**Bollinger Band Width / Squeeze (pattern)** — see Bollinger Squeeze
**Bollinger Squeeze** — 02_trend_following.md, 04_breakouts.md, 06_volatility.md, 08_entries.md, 13_indicator_reference.md, hypothesis_bank.md, implementation_patterns.md
**Bond-Utility Arbitrage (Murray Ruggiero)** — 03_mean_reversion.md
**Bookstaber's Ratio Volatility Measures** — 06_volatility.md, 13_indicator_reference.md
**Box Size / Reversal Value (point-and-figure)** — 02_trend_following.md, 04_breakouts.md, 08_entries.md, 13_indicator_reference.md
**Box-Jenkins Method** — 13_indicator_reference.md
**Breadth (advance/decline)** — 01_market_structure.md
**Breakaway / Exhaustion / Runaway / Common Gap** — 04_breakouts.md
**Briese Index / Briese COT Index** — 07_market_regimes.md, 13_indicator_reference.md
**British Election 1992 Shock** — 07_market_regimes.md
**Broken Fractal** — 04_breakouts.md
**Bruce Gould / Gould's Long-Term Price Zones** — 03_mean_reversion.md, hypothesis_bank.md ("Intraday Price Zones")
**Bulge Problem (rolling volatility lag)** — 06_volatility.md, 03_mean_reversion.md ("Avoiding the Bulge")
**Bulkowski's Gap-Closure / Candlestick-Performance Statistics** — 04_breakouts.md, 08_entries.md
**Bull/Bear Hooks** — 04_breakouts.md
**Bull/Bear Market Phases (Dow Theory)** — 01_market_structure.md
**Bull/Bear/Cyclic/Congested Market Taxonomy (Pardo)** — 07_market_regimes.md, 14_backtesting_and_validation.md
**Bullish Consensus / Market Sentiment Index (Hadady)** — 01_market_structure.md, 07_market_regimes.md, 13_indicator_reference.md, 18_common_failure_modes.md, hypothesis_bank.md ("Sentiment-Extreme Regime Signals")
**Bullish Review Study (COT)** — 01_market_structure.md
**Business Cycle (Armstrong Economics)** — 07_market_regimes.md
**Butterfly Spread (futures term structure)** — 03_mean_reversion.md
**Buy the Rumor, Sell the Fact** — 01_market_structure.md
**Buyer's and Seller's Curves** — 01_market_structure.md
**Buying Power (BP) / Selling Power (SP)** — 05_momentum.md

## C

**Calendar-Quarter-Based N** — 04_breakouts.md
**Calmar Ratio** — 11_risk_management.md
**Cambridge Hook** — 05_momentum.md, 08_entries.md, 13_indicator_reference.md
**Capacity (strategy capital ceiling)** — 16_research_hypotheses.md — Chan's central book concept
**Capital Market Line (CML)** — 12_portfolio_construction.md
**Cash-and-Carry Arbitrage** — 15_crypto_specific.md
**Cattle Cycle** — 07_market_regimes.md, 13_indicator_reference.md
**Causal / Correlative / Random Relationships (Vince)** — 12_portfolio_construction.md
**CCI (Commodity Channel Index)** — 13_indicator_reference.md
**CFD/Leverage Risk** — 11_risk_management.md
**CHADTP (Conners-Hayward Advance-Decline Trading Patterns)** — 03_mean_reversion.md, hypothesis_bank.md ("Connors AD-Ratio / CHADTP Breadth Fade")
**Chaiken's Proportional-Volume Approach** — 01_market_structure.md
**Chan's Regime-Based Momentum/Mean-Reversion Switching Framework** — hypothesis_bank.md
**Chandelier Exit** — 09_exits.md — confirmed absent from Kaufman source, flagged as such
**Chande &amp; Kroll Volatility-Scaled Forecast Zones** — 06_volatility.md, 13_indicator_reference.md
**Chande's Trend Strength Ranking (St)** — 08_entries.md, 12_portfolio_construction.md, 13_indicator_reference.md
**Chande's VIDYA (Variable Index Dynamic Average)** — 02_trend_following.md, 07_market_regimes.md, 13_indicator_reference.md
**Channel Breakout / Channel Construction** — 04_breakouts.md
**Charles H. Dow** — 01_market_structure.md
**Chasing Volatility** — 06_volatility.md
**Chess-Computer Analogy** — 16_research_hypotheses.md — Pardo's systematic-vs-discretionary framing
**Chi-Square (χ²) Significance Test** — 11_risk_management.md, 14_backtesting_and_validation.md
**Choosing the Calculation Period** — 02_trend_following.md, 05_momentum.md
**Classifications of Trends (Primary/Secondary/Minor)** — 01_market_structure.md
**CME BTC/ETH Futures COT Data** — 15_crypto_specific.md, 16_research_hypotheses.md, hypothesis_bank.md ("CME BTC/ETH COT Positioning Filter")
**CNNMoney Fear &amp; Greed Index** — 07_market_regimes.md
**Cointegration** — 03_mean_reversion.md, 05_momentum.md, 08_entries.md, 12_portfolio_construction.md, 15_crypto_specific.md, hypothesis_bank.md ("Cointegration / Pairs Trading & Intermarket Spread Strategies", "BTC-ETH Cointegration Pairs Trading")
**Cointegrating Augmented Dickey-Fuller Test (CADF)** — 03_mean_reversion.md, 05_momentum.md, 13_indicator_reference.md
**Colby's 2-Day ADX/Pivot System** — 08_entries.md, 12_portfolio_construction.md, 15_crypto_specific.md
**Combinatorial-Sample-Size Audit** — 16_research_hypotheses.md
**Combination Portfolio Allocation (CPA)** — 12_portfolio_construction.md, hypothesis_bank.md ("Vince's Geometric-Optimal Portfolio & Combination Portfolio Allocation (CPA)")
**Commercial-vs-Speculator Positioning** — 15_crypto_specific.md
**Commission / Slippage (backtesting costs)** — 14_backtesting_and_validation.md
**Commitment of Traders (COT) Report** — 01_market_structure.md, 07_market_regimes.md, 15_crypto_specific.md
**Commodex** — 02_trend_following.md, hypothesis_bank.md ("Composite Multi-Factor Trend Systems")
**Commodity Selection Index (CSI)** — 12_portfolio_construction.md, 13_indicator_reference.md, 16_research_hypotheses.md, hypothesis_bank.md ("CSI-Ranked Market Selection / Allocation")
**Common Sense Management of Risk (Kaufman's 8-point checklist)** — 11_risk_management.md
**Competitive Decay of Edges** — 18_common_failure_modes.md — Kaufman's crowd-imitation framing
**Complexity Tolerance — Author Disagreement** — 17_author_disagreements.md
**Composite Multi-Factor Trend Systems** — hypothesis_bank.md — Commodex, MPTDI
**Conditional Entropy** — 13_indicator_reference.md
**Confirmation Logic (N-of-M Signal Agreement / Oscillator-Confirms-Trend / Volume-Confirms-Price)** — implementation_patterns.md
**Congestion Pattern / Delayed Consolidation Pattern** — 04_breakouts.md
**Conners RSI-Timed VIX Mean-Reversion Strategy** — 06_volatility.md, hypothesis_bank.md ("VIX / IV Mean-Reversion Systems")
**Conners VIX Reversal 9 (CVR9)** — 06_volatility.md, hypothesis_bank.md ("VIX / IV Mean-Reversion Systems")
**Connors AD-Ratio System (Larry Connors)** — 03_mean_reversion.md, hypothesis_bank.md ("Connors AD-Ratio / CHADTP Breadth Fade")
**Conservation of Capital** — 02_trend_following.md, 09_exits.md
**Consistency and Profit-Distribution Cases** — 14_backtesting_and_validation.md
**Consolidated Pre-Trade Checklist** — 14_backtesting_and_validation.md
**Contagion-Style Trading** — 01_market_structure.md
**Continuous / Perpetual Contract** — 14_backtesting_and_validation.md, 15_crypto_specific.md
**Continuous Moving-Window Re-Optimization** — 17_author_disagreements.md — Chan's safeguard
**Contingent-Entry Risk** — 04_breakouts.md
**Contrary Opinion / Contrarian** — 01_market_structure.md, 07_market_regimes.md, 15_crypto_specific.md
**Corporate Insider Activity** — 01_market_structure.md
**Correlation Between Equity Curve and Perfect Profit (CECPP)** — 14_backtesting_and_validation.md, 15_crypto_specific.md
**Correlation Breakdown During a Shock** — 07_market_regimes.md, 11_risk_management.md, 12_portfolio_construction.md
**Correlation Coefficient (r²) as Smoothing Constant** — 02_trend_following.md, 07_market_regimes.md, 13_indicator_reference.md
**Correlation vs. Cointegration Distinction** — 03_mean_reversion.md, 13_indicator_reference.md
**Countertrend/Mean-Reverting Strategy Family (portfolio)** — 12_portfolio_construction.md
**Covariance from Correlation Formula** — 12_portfolio_construction.md
**Crisis Management Three-Rule Proposal** — 07_market_regimes.md
**Cross-Market Consistency Test ("loose pants fit everyone")** — 14_backtesting_and_validation.md, 16_research_hypotheses.md
**Cross-Sectional Momentum** — 05_momentum.md, 16_research_hypotheses.md, hypothesis_bank.md ("Cross-Sectional Momentum & PEAD")
**Cross-Sectional PCA Factor-Model Regime-Switching** — 16_research_hypotheses.md — Chan's failed S&amp;P 600 example; see also Fama-French / PCA Factor Cross-Sectional Model (hypothesis_bank.md)
**Cross-Sectional Top-K Momentum Portfolio** — hypothesis_bank.md
**Crossover Price (CP2)** — 02_trend_following.md, 13_indicator_reference.md
**Crowd Behavior and Market Structure** — 01_market_structure.md
**Crowd-Exhaustion Contrarian Theory** — 18_common_failure_modes.md
**Crypto Fear &amp; Greed Index** — 15_crypto_specific.md, 16_research_hypotheses.md, hypothesis_bank.md ("Crypto Fear & Greed Sentiment Filter")
**Crypto Perpetual-Futures Open Interest** — 15_crypto_specific.md, 16_research_hypotheses.md, 01_market_structure.md, hypothesis_bank.md ("Crypto Perpetual Open Interest as a Volume Substitute")
**CSI-Ranked Market Selection / Allocation** — see Commodity Selection Index (CSI)
**CTA (Commodity Trading Advisor) AUM** — 02_trend_following.md
**Cumulative-Trials Multiple-Comparisons Arithmetic** — 16_research_hypotheses.md, 18_common_failure_modes.md, 14_backtesting_and_validation.md (Multiple-Comparisons Problem)
**Cup and Cap Pattern** — 08_entries.md
**Customer Trade Indicator (CTI) Trader Classification** — 01_market_structure.md
**Cycle Analysis** — 07_market_regimes.md
**Cyclic (Trading-Range) Market** — 14_backtesting_and_validation.md, 07_market_regimes.md

## D

**Daily Pivot Range** — 04_breakouts.md
**Daily Raw Figure (DRF)** — 05_momentum.md
**Data Errors / Fictitious Quotes (backtest inflation)** — 03_mean_reversion.md
**Data Integrity Checks / Pre-Flight Checklist** — 14_backtesting_and_validation.md, 16_research_hypotheses.md
**Data-Mining Turning-Points Regime-Trigger Model (Alphacet)** — hypothesis_bank.md — see also Alphacet Discovery, Turning-Points / Data-Mining Approach
**Data-Snooping Bias** — 14_backtesting_and_validation.md, 18_common_failure_modes.md
**Day-of-Month Institutional-Flow Patterns** — 03_mean_reversion.md, 16_research_hypotheses.md, hypothesis_bank.md ("Reversal-Day, Weekday, and Day-of-Month Patterns")
**Death Cross / Golden Cross** — 02_trend_following.md, 08_entries.md
**Decaying Performance Diagnostic** — 11_risk_management.md
**Decimalization (2001)** — 07_market_regimes.md
**Decision-Tree Models (portfolio allocation)** — 06_volatility.md, 12_portfolio_construction.md
**Deflated Sharpe Ratio (DSR)** — 14_backtesting_and_validation.md, EDGE_FRAMEWORK.md, AI_RESEARCH_PLAYBOOK.md — mandatory ≥0.95 gate per this project's own pipeline
**DeMark's Sequential** — 03_mean_reversion.md, 09_exits.md, hypothesis_bank.md
**Dennis Meyers' Adaptive Range Breakout** — 02_trend_following.md, 09_exits.md, 13_indicator_reference.md (Normalized High/Low Range)
**Deployment Checklist (Oanda-based)** — 18_common_failure_modes.md
**Deribit Implied-vs-Realized Volatility** — 15_crypto_specific.md, 16_research_hypotheses.md, hypothesis_bank.md ("Deribit IV-vs-RV Proxy (Crypto VIX Analog)")
**Despair and Greed (psychological failure modes)** — 11_risk_management.md, 18_common_failure_modes.md
**Detrending (correlation coefficient / two-trendline)** — 12_portfolio_construction.md, 13_indicator_reference.md
**Diagnosing Live-Trading Underperformance (Chan's checklist)** — 14_backtesting_and_validation.md
**Dickey-Fuller (DF) Test** — 03_mean_reversion.md
**Dip and Rally Pattern** — 04_breakouts.md
**Directional Movement (+DMI/−DMI)** — 05_momentum.md, 08_entries.md, 12_portfolio_construction.md, 13_indicator_reference.md
**Directional Parabolic Stop (DPS)** — 05_momentum.md, 09_exits.md, 13_indicator_reference.md, hypothesis_bank.md ("ADX-Filtered Oscillator (Kestner) & Directional Parabolic")
**Distribution of the Optimization Profile** — 14_backtesting_and_validation.md
**Divergence Index (DI)** — 05_momentum.md, 03_mean_reversion.md, 13_indicator_reference.md, hypothesis_bank.md ("Divergence Index & Fisher Transform Mean-Reversion")
**Diversification** — 12_portfolio_construction.md
**Dividend / Split Adjustment** — 14_backtesting_and_validation.md
**DNN (Deep Neural Network) Classification** — 08_entries.md, 14_backtesting_and_validation.md, hypothesis_bank.md ("DNN Direction Classifier") — Hilpisch/Keras
**Dogs of the Dow** — 03_mean_reversion.md, 12_portfolio_construction.md, hypothesis_bank.md ("Dogs of the Dow / O'Higgins / Foolish Four & Rating-Service Basket Spreads", "Reversed Dogs-of-the-Dow + Volatility-Triggered Hedge Overlay")
**Dollar Risk Stop / Dollar Profit Target** — 09_exits.md
**Donald Jones' Value-Area Overlay Method** — 01_market_structure.md
**Donchian Channels (40/20 Channel Breakout)** — 02_trend_following.md, 04_breakouts.md, 08_entries.md
**Donchian's 4-Week Rule** — 04_breakouts.md, 02_trend_following.md, 08_entries.md
**Donchian's 5- and 20-Day Moving Average System** — 02_trend_following.md, 08_entries.md
**Donchian's 20- and 40-Day Breakout** — 02_trend_following.md, 08_entries.md
**Double Smoothing (moving average)** — 02_trend_following.md, 13_indicator_reference.md
**Double-Blind Testing** — 14_backtesting_and_validation.md
**Double-Smoothed Stochastics** — 05_momentum.md, 13_indicator_reference.md
**Dow Theory** — 01_market_structure.md
**Down Fractal / Up Fractal** — 04_breakouts.md
**Downstream KAMA Cross-Reference** — see KAMA
**Drawdown Mathematics** — 11_risk_management.md, 15_crypto_specific.md
**Drawdown Ratio (DR)** — 11_risk_management.md
**Drawdown-Response Dilemma** — 16_research_hypotheses.md — Kaufman's de-risk-vs-hold question
**Drawdown-Triggered Re-Leveraging** — 12_portfolio_construction.md
**Drop-Off Effect (moving average)** — 02_trend_following.md
**Dunnigan's One-Way Formula / Square Root Theory / Thrust Method** — 08_entries.md, implementation_patterns.md (2-of-4-then-confirm example, N-of-M Confirmation Logic)
**Dynamic Breakout System (DBS, Stridsman)** — 04_breakouts.md, 02_trend_following.md, hypothesis_bank.md
**Dynamic Fractional f** — 10_position_sizing.md — split-equity technique
**Dynamic Hedging / Static Hedging** — 01_market_structure.md
**Dynamic Momentum Index (DMI, Chande/Kroll)** — 07_market_regimes.md, 02_trend_following.md, 13_indicator_reference.md, implementation_patterns.md ("Efficiency-Adaptive Smoothing Constant" pattern)

## E

**Early Breakout Pattern / Early Onset Trend (Ehlers)** — 04_breakouts.md, 02_trend_following.md, 13_indicator_reference.md
**Early Exits from a Trend** — 02_trend_following.md
**EDGE_FRAMEWORK.md** — bridge/foundation file — durable-edge philosophy, three-tier evidence framework, warning-sign checklist; see header key
**Effective vs. Nominal Sample Size** — 16_research_hypotheses.md, 18_common_failure_modes.md
**Efficiency Ratio (ER) / Fractal Efficiency** — 01_market_structure.md, 06_volatility.md, 07_market_regimes.md, 09_exits.md, 12_portfolio_construction.md, 13_indicator_reference.md, 15_crypto_specific.md, 16_research_hypotheses.md, hypothesis_bank.md ("Efficiency Ratio Regime Gate"), implementation_patterns.md ("Efficiency Ratio (ER) Threshold Gate")
**Efficiency-Adaptive Smoothing Constant** — see KAMA / VIDYA / FRAMA / MAMA-FAMA
**Efficient Frontier** — 11_risk_management.md, 12_portfolio_construction.md, 15_crypto_specific.md
**Efficient Market Hypothesis (EMH)** — 01_market_structure.md
**Eight-Repetition Rule (cycle validity)** — 07_market_regimes.md
**Eight-Stage Trading Strategy Development Process (Pardo)** — 14_backtesting_and_validation.md
**Elastic Volume-Weighted Moving Average (eVWMA)** — 13_indicator_reference.md
**Elder's Triple Screen Trading System** — 02_trend_following.md, 08_entries.md, 09_exits.md, 13_indicator_reference.md, hypothesis_bank.md ("Multi-Timeframe Trend Confirmation Systems"), implementation_patterns.md ("Multi-Timeframe Agreement")
**Elder-Ray (Bull Power / Bear Power)** — 02_trend_following.md, 08_entries.md, 13_indicator_reference.md
**Elliott Wave Theory** — 01_market_structure.md, 07_market_regimes.md, 13_indicator_reference.md
**Elliott Wave Oscillator (EWO)** — 09_exits.md, 13_indicator_reference.md
**Empirical Frequency Distribution (volatility percentiles)** — 06_volatility.md, 15_crypto_specific.md, implementation_patterns.md ("Volatility Percentile / Empirical-Distribution Ranking")
**Equal-Dollar Weighting** — 06_volatility.md, 12_portfolio_construction.md
**Equal-Risk (Volatility-Parity) Portfolio Weighting** — 06_volatility.md, 12_portfolio_construction.md, hypothesis_bank.md, implementation_patterns.md
**Equilibrium (price)** — 01_market_structure.md
**Err-Conservatively-When-Uncertain Principle** — 18_common_failure_modes.md — Vince
**Estimated Geometric Mean (EGM)** — 10_position_sizing.md
**Eugene Fama** — 01_market_structure.md
**Euclidean Distance** — 13_indicator_reference.md
**European Options Pricing Model for All Distributions** — 10_position_sizing.md
**Event Trading and Price Shocks** — 01_market_structure.md, 07_market_regimes.md, 14_backtesting_and_validation.md
**Event-Driven Swing Trend Systems** — hypothesis_bank.md — swing trading, Livermore System, Keltner's Minor Trend Rule, Swing/Accumulated Swing Index
**Evaluation-Profile vs. Trade-Profile Comparison** — 11_risk_management.md, 17_author_disagreements.md
**E-V Theory (Markowitz)** — 12_portfolio_construction.md
**Excel Solver Portfolio Optimization** — 12_portfolio_construction.md
**Excess Kurtosis** — 01_market_structure.md, 13_indicator_reference.md
**Exhaustion Gap** — 04_breakouts.md
**Exit Structures (Trend-Break / Fixed-Volatility-Scaled Stop / Trailing Stop / Time-Based Exit / Volatility-Scaled Profit Target)** — implementation_patterns.md — composable, strategy-type-matched exit modules
**Expected Portfolio Return / Portfolio Variance** — 12_portfolio_construction.md, 13_indicator_reference.md
**Exponential Smoothing / EMA** — 02_trend_following.md, 13_indicator_reference.md
**Extreme-Years Distortion Test (seasonality)** — 07_market_regimes.md
**Extreme Spread Ratios (failure mode)** — 03_mean_reversion.md

## F

**Failed Breakout (bar-chart definition)** — 04_breakouts.md
**Failure Swing (RSI)** — 05_momentum.md, 03_mean_reversion.md
**Fallacy of Filters** — 12_portfolio_construction.md
**FAMA / MAMA (Ehlers)** — 07_market_regimes.md, 02_trend_following.md, 13_indicator_reference.md, implementation_patterns.md ("Efficiency-Adaptive Smoothing Constant" pattern)
**Fama-French Three-Factor Model** — 05_momentum.md, 13_indicator_reference.md, hypothesis_bank.md ("Fama-French / PCA Factor Cross-Sectional Model (failed example)")
**Fat Tails / Non-Normality of Price Distributions** — 01_market_structure.md, 09_exits.md
**Fat-Tail Leverage Cap** — 10_position_sizing.md, 15_crypto_specific.md, 16_research_hypotheses.md
**Fear (psychological failure mode)** — 18_common_failure_modes.md
**Fee/Slippage Kill-Floors** — 18_common_failure_modes.md, EDGE_FRAMEWORK.md, AI_RESEARCH_PLAYBOOK.md — hours 21-22 UTC anomaly, real signal killed 25:1 by fees
**Feedback Trap (Kaufman)** — 14_backtesting_and_validation.md, AI_RESEARCH_PLAYBOOK.md
**Fibonacci Ratios / Retracement** — 01_market_structure.md, 07_market_regimes.md, 08_entries.md, 13_indicator_reference.md
**Financial Contagion** — 12_portfolio_construction.md
**First/Second Differences (momentum)** — 05_momentum.md
**Fisher's Z Transformation** — 14_backtesting_and_validation.md
**Fisher Transform** — 05_momentum.md, 03_mean_reversion.md, 07_market_regimes.md, 13_indicator_reference.md, 16_research_hypotheses.md, hypothesis_bank.md ("Divergence Index & Fisher Transform Mean-Reversion") — includes Inverse Fisher Transform
**Fischer's Golden Section Compass (GSC) System** — 07_market_regimes.md, hypothesis_bank.md ("Fischer's Golden Section Compass & Hurst Phasing")
**Fixed-Fractional Sizing** — 10_position_sizing.md, implementation_patterns.md
**Fixed/Volatility-Scaled Stop (pattern)** — see Exit Structures
**Flat Production Scenario (Pardo)** — 18_common_failure_modes.md
**Foolish Four Variant (Dogs of the Dow)** — 03_mean_reversion.md
**Force Index (Elder)** — 02_trend_following.md, 08_entries.md, 13_indicator_reference.md
**Forecast Oscillator (Chande)** — 05_momentum.md
**Forecasting vs. Following (trend systems)** — 02_trend_following.md
**Four or Fewer Variables Rule (Futures Truth)** — 14_backtesting_and_validation.md
**Fourier / Spectral Analysis** — 07_market_regimes.md, 13_indicator_reference.md
**Fractal Dimension** — 01_market_structure.md, 07_market_regimes.md, 13_indicator_reference.md
**Fractional f** — 12_portfolio_construction.md, 17_author_disagreements.md
**Fractional Martingales / Delayed Entry** — 10_position_sizing.md
**Frank Tubbs' Law of Proportion** — 08_entries.md
**FRAMA (Fractal Adaptive Moving Average, Ehlers)** — 07_market_regimes.md, 13_indicator_reference.md, implementation_patterns.md ("Efficiency-Adaptive Smoothing Constant" pattern)
**Front-Loaded WMA** — 13_indicator_reference.md
**Full Kelly Formula (F* = C⁻¹M)** — 16_research_hypotheses.md, 10_position_sizing.md, hypothesis_bank.md ("Kelly-Weighted Multi-Strategy Portfolio (Chan's F*=C⁻¹M)")
**Fundamental Equation of Trading** — 12_portfolio_construction.md, 10_position_sizing.md, implementation_patterns.md
**Fundamental Strategy Family (portfolio)** — 12_portfolio_construction.md

## G

**Gambler's Ruin Formula** — 11_risk_management.md
**Gann's Rule of Ten** — 09_exits.md
**Gap-Fade / Gap-Pullback Trading** — see Gap Trading Rules / Gap-Fill Folklore
**Gap Trading Rules / Gap-Fill Folklore** — 04_breakouts.md, 03_mean_reversion.md, 16_research_hypotheses.md, hypothesis_bank.md ("Gap-Fade / Gap-Pullback Trading", "True Gap / Wide-Ranging-Bar Breakout Entries")
**GARCH** — 06_volatility.md, 13_indicator_reference.md
**GASP (Genetic Algorithm Portfolio Solution)** — 12_portfolio_construction.md, 13_indicator_reference.md, 15_crypto_specific.md, 16_research_hypotheses.md, hypothesis_bank.md ("GASP — Genetic-Algorithm Multi-Strategy Portfolio Allocation")
**Gauss-Jordan Elimination** — 12_portfolio_construction.md
**Gaussian Filter (smoothing)** — 02_trend_following.md, 13_indicator_reference.md
**Generalized Central Limit Theorem** — 10_position_sizing.md
**Genetic Algorithms** — 12_portfolio_construction.md, 13_indicator_reference.md, 14_backtesting_and_validation.md, 17_author_disagreements.md
**Geometric Average Trade (GAT)** — 10_position_sizing.md
**Geometric Efficient Frontier** — 12_portfolio_construction.md, hypothesis_bank.md ("Vince's Geometric-Optimal Portfolio & Combination Portfolio Allocation (CPA)")
**Geometric Mean (growth criterion) / GHPR** — 10_position_sizing.md, 12_portfolio_construction.md, 15_crypto_specific.md
**Geometric Moving Average (GA)** — 02_trend_following.md, 13_indicator_reference.md
**Geometric Ratio (GR)** — 11_risk_management.md
**Globalization and Noise** — 01_market_structure.md
**Goichi Hosada / Ichimoku Cloud** — 02_trend_following.md, 08_entries.md, 13_indicator_reference.md
**Golden Cross / Death Cross** — 02_trend_following.md, 08_entries.md
**Gorbachev's Abduction (1991 Shock)** — 07_market_regimes.md
**GTWR/ATWR (Terminal Wealth over N Trades)** — 12_portfolio_construction.md
**Grid Search (Brute Force) Optimization** — 14_backtesting_and_validation.md
**Group Weighting (moving average)** — 13_indicator_reference.md
**Gulf War / Kuwait Invasion Shock** — 07_market_regimes.md
**Gulf-Stream Cautionary Tale** — 18_common_failure_modes.md — Kaufman's qualifying-the-market rule
**Gustafson's Price Persistency Strategy** — 03_mean_reversion.md, hypothesis_bank.md

## H

**Hadady's Bullish Consensus** — see Bullish Consensus
**Half-Kelly** — 10_position_sizing.md, 12_portfolio_construction.md, 15_crypto_specific.md, 16_research_hypotheses.md, 17_author_disagreements.md
**Halving-Cycle / Calendar Crypto Effects** — hypothesis_bank.md
**Hard to Borrow (persistent friction)** — 07_market_regimes.md
**Heat Maps and 3-D Surface Plots (optimization)** — 14_backtesting_and_validation.md
**Hedge Fund Replication** — 12_portfolio_construction.md
**Hedge Ratio (H = f·A/E)** — 12_portfolio_construction.md, 03_mean_reversion.md
**Herrick Payoff Index (HPI)** — 05_momentum.md, 13_indicator_reference.md
**Hidden Markov Models (regime switching)** — 07_market_regimes.md, 13_indicator_reference.md, 16_research_hypotheses.md, hypothesis_bank.md ("Hidden Markov Model Regime-Switching")
**High Swing Point (HSP) / Low Swing Point (LSP)** — 02_trend_following.md, 13_indicator_reference.md
**High Watermark** — 13_indicator_reference.md
**High-Frequency Trading (HFT)** — 01_market_structure.md, 14_backtesting_and_validation.md, 15_crypto_specific.md
**High-Low Data Reliability** — 14_backtesting_and_validation.md
**High-Low Index (HLX) / High-Low Ratio (HLR)** — 01_market_structure.md, 13_indicator_reference.md
**Hilbert Transform** — 02_trend_following.md, 07_market_regimes.md, 13_indicator_reference.md
**Hill Climbing / Multipoint Hill Climbing** — 14_backtesting_and_validation.md
**Hindenburg Omen** — 15_crypto_specific.md
**Hindsight Bias** — 18_common_failure_modes.md
**Hinge (stochastic pattern)** — 05_momentum.md
**Hirsch's "Sell in May" 6-Month Strategy** — 07_market_regimes.md
**Historic / Historical Volatility (HV)** — 06_volatility.md, 10_position_sizing.md, 13_indicator_reference.md
**Hit Ratio (ML) vs. P&amp;L Disconnect** — 08_entries.md, 14_backtesting_and_validation.md
**Holding Period Return (HPR)** — 10_position_sizing.md, 12_portfolio_construction.md, 15_crypto_specific.md
**Holiday Effect** — 07_market_regimes.md
**Horizontal / Vertical Count (point-and-figure)** — 13_indicator_reference.md
**Hull Moving Average (HMA)** — 02_trend_following.md, 13_indicator_reference.md, README.md
**Hurst's Five Principles of Periodic Motion** — 07_market_regimes.md
**Hurst Phasing / Hurst Exponent** — 07_market_regimes.md, 13_indicator_reference.md
**Hutson Day-to-Smoothing-Constant Conversion** — 02_trend_following.md, 13_indicator_reference.md

## I

**Ichimoku Cloud** — 02_trend_following.md, 08_entries.md, 13_indicator_reference.md
**Implied Volatility (IV)** — 06_volatility.md
**In-Sample / Out-of-Sample Discipline** — 14_backtesting_and_validation.md
**Inadequate Data and Trade Sample** — 14_backtesting_and_validation.md, 18_common_failure_modes.md
**Index Arbitrage** — 01_market_structure.md
**Information Ratio** — 11_risk_management.md, 12_portfolio_construction.md, 13_indicator_reference.md
**Inside Day Filter** — 04_breakouts.md, 08_entries.md — Toby Crabel
**Insider/Big-Block Activity as Sentiment Signal** — 07_market_regimes.md, 01_market_structure.md
**Instantaneous Trendline (Ehlers)** — 07_market_regimes.md, 02_trend_following.md
**Institutional Agency-Risk Overleveraging** — 18_common_failure_modes.md — Chan Ch.8
**Institutional Capacity-Driven Structural Disadvantage** — 18_common_failure_modes.md
**Intermarket Index Ratio Mean Reversion** — 03_mean_reversion.md
**Intraday Intensity** — 13_indicator_reference.md
**Intraday Momentum (Hilpisch)** — 05_momentum.md
**Intraday Price Zones (Jackson / Scorpio / Gould)** — hypothesis_bank.md — see also J. T. Jackson, Scorpio's ATR-Based Daily Zones, Bruce Gould
**Intraday Price-Shock Detector** — 06_volatility.md, 16_research_hypotheses.md
**Intraday Price-Shock Fade (contrast case)** — hypothesis_bank.md — mean-reversion fade despite "volatility breakout" source placement
**Intraday Volatility U-Shape/W-Shape** — 06_volatility.md
**Inverse Fisher Transform** — 13_indicator_reference.md
**IV/HV Arbitrage (Relative Value)** — 06_volatility.md, 03_mean_reversion.md, hypothesis_bank.md ("IV/HV Relative-Value Arbitrage & Volatility Dispersion Trading")

## J

**J-Curve Effect** — 03_mean_reversion.md
**J. Peter Steidlmayer** — 01_market_structure.md
**J. T. Jackson / Jackson's Intraday Zones** — 03_mean_reversion.md, 09_exits.md, 13_indicator_reference.md, hypothesis_bank.md ("Intraday Price Zones")
**Jack Hutson** — 02_trend_following.md
**Jérôme Kerviel** — 18_common_failure_modes.md — Société Générale $7.1B loss example
**January Barometer** — 07_market_regimes.md
**January Effect (small-cap reversal)** — 07_market_regimes.md, 08_entries.md, 18_common_failure_modes.md
**Jesse Livermore / Livermore System** — 02_trend_following.md
**Jiler's Guidelines (COT)** — 01_market_structure.md, 07_market_regimes.md
**Johansen Test** — 03_mean_reversion.md
**John Bollinger** — 02_trend_following.md
**John Ehlers** — 02_trend_following.md
**John McGinley / McGinley Dynamics** — 02_trend_following.md, 13_indicator_reference.md

## K

**Kalman Filter** — 13_indicator_reference.md
**KAMA (Kaufman's Adaptive Moving Average)** — 01_market_structure.md, 02_trend_following.md, 07_market_regimes.md, 09_exits.md, 13_indicator_reference.md, 15_crypto_specific.md, 16_research_hypotheses.md
**Kase DevStop — Tiered Volatility Stop System** — see Kase's DevStop
**Kase's DevStop** — 06_volatility.md, 09_exits.md, 13_indicator_reference.md, 16_research_hypotheses.md, hypothesis_bank.md, implementation_patterns.md
**Kelly / Optimal-f-Derived Fractional Sizing (pattern)** — see Kelly Criterion / Kelly Formula, Optimal f
**Kelly Criterion / Kelly Formula** — 10_position_sizing.md, 11_risk_management.md (implicit via Optimal f), 12_portfolio_construction.md, 13_indicator_reference.md, 15_crypto_specific.md, 16_research_hypotheses.md, 17_author_disagreements.md, README.md, hypothesis_bank.md ("Kelly-Weighted Multi-Strategy Portfolio"), implementation_patterns.md
**Keltner Channel** — 04_breakouts.md, 02_trend_following.md, 06_volatility.md, 13_indicator_reference.md
**Keltner's Minor Trend Rule** — 04_breakouts.md, 02_trend_following.md
**Key Reversal Day** — 06_volatility.md, 08_entries.md
**Khandani &amp; Lo Short-Term Mean-Reversal Model** — 05_momentum.md, 03_mean_reversion.md, hypothesis_bank.md ("Khandani & Lo Short-Term Cross-Sectional Reversal")
**K-Means** — 13_indicator_reference.md
**K-Nearest Neighbor (k-NN)** — 13_indicator_reference.md
**Klein and Prestbo Study** — 01_market_structure.md
**Knapp's ER-Based Parabolic Variant (Volker Knapp)** — 02_trend_following.md, 09_exits.md
**Kolmogorov-Smirnov (K-S) Test** — 01_market_structure.md, 10_position_sizing.md, 15_crypto_specific.md
**Kondratieff Wave (K-Wave)** — 07_market_regimes.md
**KST (Know Sure Thing) System, Martin Pring** — 02_trend_following.md, 08_entries.md, 13_indicator_reference.md, 16_research_hypotheses.md, hypothesis_bank.md ("Multi-Timeframe Trend Confirmation Systems")
**Kurtosis (statistical moment)** — 01_market_structure.md, 13_indicator_reference.md, 14_backtesting_and_validation.md, 16_research_hypotheses.md, 18_common_failure_modes.md
**Kurtosis as Overfitting Diagnostic** — 01_market_structure.md, 14_backtesting_and_validation.md, 16_research_hypotheses.md, 18_common_failure_modes.md
**Kurtosis-Skew Strategy** — 06_volatility.md, 03_mean_reversion.md, 16_research_hypotheses.md, hypothesis_bank.md ("Kurtosis-Skew Mean-Reverting Strategy")

## L

**Lag (moving average)** — 02_trend_following.md
**Lag-Construction Technique (ML)** — 14_backtesting_and_validation.md
**Lagged Linear-Regression Direction Entry (Hilpisch)** — 08_entries.md, hypothesis_bank.md ("Linear / Logistic Regression Direction Entry")
**Larry Connors** — 03_mean_reversion.md
**Larry Williams' Filtered Opening Range Breakout** — 04_breakouts.md, 08_entries.md
**Law of Large Numbers (HFT Sharpe argument)** — 01_market_structure.md, 15_crypto_specific.md
**Laws of Multiple Time Frames (Krausz)** — 02_trend_following.md, 08_entries.md
**LBR/RSI (Raschke and Conners)** — 04_breakouts.md, 08_entries.md, 13_indicator_reference.md
**Lee Leibfarth** — 02_trend_following.md
**Left/Right Crossover (stochastic pattern, Lane)** — 05_momentum.md
**Lengthen-Calculation-Period-First Rule** — 16_research_hypotheses.md — Kaufman's trend-before-mean-reversion sequencing
**Leptokurtic / Platykurtic / Mesokurtic** — 01_market_structure.md
**Limit Moves (locked-limit day)** — 14_backtesting_and_validation.md, 15_crypto_specific.md
**Limit-Order Fill Realism** — 18_common_failure_modes.md, 14_backtesting_and_validation.md
**Linear Regression (Least-Squares)** — 13_indicator_reference.md, 02_trend_following.md (LRS trend system)
**Live Chi-Square Monitoring** — 16_research_hypotheses.md
**Live-vs-Backtest Divergence** — 18_common_failure_modes.md
**Lo, Mamaysky, Wang (2000) Chart Pattern Study** — 08_entries.md
**Local vs. Global Maximum (optimization)** — 14_backtesting_and_validation.md
**Logging and Remote Monitoring Architecture** — 18_common_failure_modes.md — ZeroMQ PUB-SUB
**Logical Information Machines (LIM)** — 14_backtesting_and_validation.md
**Logistic-Regression Direction Entry (Hilpisch)** — 08_entries.md, hypothesis_bank.md ("Linear / Logistic Regression Direction Entry")
**Long-Term Capital Management (LTCM)** — 01_market_structure.md, 07_market_regimes.md, 11_risk_management.md, 12_portfolio_construction.md, 18_common_failure_modes.md
**Look-Ahead Bias** — 05_momentum.md, 14_backtesting_and_validation.md, AI_RESEARCH_PLAYBOOK.md — "check first, always" diagnostic priority
**Loose Pants Fit Everyone (Ken Tropin)** — 14_backtesting_and_validation.md, 16_research_hypotheses.md
**Low-Volatility Anomaly / Low-Vol ETF Strategy** — see Low-Volatility ETFs
**Low-Volatility ETFs** — 06_volatility.md, hypothesis_bank.md ("Low-Volatility Anomaly / Low-Vol ETF Strategy")
**Lukac, Brorsen, and Irvin Study** — 07_market_regimes.md

## M

**MACD (Moving Average Convergence-Divergence)** — 05_momentum.md, 13_indicator_reference.md, hypothesis_bank.md ("MACD Crossover Trend System", "MACD / Momentum Divergence Trading")
**MACD Histogram / Signal Line** — 05_momentum.md
**MAMA/FAMA (Ehlers)** — 07_market_regimes.md, 13_indicator_reference.md, implementation_patterns.md ("Efficiency-Adaptive Smoothing Constant" pattern)
**Mandatory Pre-Reading Exercise (Vince catastrophic-loss visualization)** — 18_common_failure_modes.md
**Margin Constraint (Vince Ch.8)** — 12_portfolio_construction.md
**Margin-Call-as-Objective-Signal Reframe** — 18_common_failure_modes.md
**Mark Fisher's Opening Range Breakout** — 04_breakouts.md, 08_entries.md
**Market Direction Indicator (MDI)** — 02_trend_following.md, 13_indicator_reference.md
**Market Facilitation Index** — 13_indicator_reference.md
**Market Maker vs. Liquidity Demander Mechanism** — 16_research_hypotheses.md
**Market Making** — 01_market_structure.md
**Market Maturity and Liquidity** — 01_market_structure.md
**Market Noise** — 01_market_structure.md, 07_market_regimes.md
**Market Personalities (per-market regime character)** — 07_market_regimes.md
**Market Profile (Steidlmayer)** — 01_market_structure.md, 13_indicator_reference.md
**Market Risk / Systematic Risk** — 12_portfolio_construction.md
**Martin J. Pring** — 02_trend_following.md
**Martingale Sizing** — 08_entries.md, 10_position_sizing.md, 18_common_failure_modes.md
**Mart's Master Trading Formula (Donald Mart)** — 02_trend_following.md
**Maturing Markets and Globalization** — 01_market_structure.md
**Maximum Adverse Excursion (MAE)** — 06_volatility.md, 09_exits.md
**Maximum Drawdown (MDD)** — 01_market_structure.md, 11_risk_management.md, 14_backtesting_and_validation.md
**Maximum Entropy Spectral Analysis (MESA)** — 07_market_regimes.md, 13_indicator_reference.md, 16_research_hypotheses.md
**Maximum Run-Up (MRU)** — 11_risk_management.md, 14_backtesting_and_validation.md
**McClellan Oscillator** — 01_market_structure.md, 13_indicator_reference.md
**McGinley Dynamics** — 02_trend_following.md, 13_indicator_reference.md
**Mean Reversion vs. Momentum Regime Viability (Chan)** — 05_momentum.md, 07_market_regimes.md, 15_crypto_specific.md, 17_author_disagreements.md
**Mean-Variance Optimization** — 06_volatility.md, 12_portfolio_construction.md (E-V Theory)
**Media Indicators (Grant Noble)** — 01_market_structure.md
**Medians vs. Means for Skewed Distributions** — 01_market_structure.md
**Merloti's Fuzzy Expert System** — 14_backtesting_and_validation.md
**MESA / Hilbert Cycle-Presence Regime Gate** — see MESA / Hilbert Transform (Ehlers)
**MESA / Hilbert Transform (Ehlers)** — 07_market_regimes.md, 13_indicator_reference.md, hypothesis_bank.md ("MESA / Hilbert Cycle-Presence Regime Gate")
**Method of Lagrange Multipliers** — 12_portfolio_construction.md
**Method of Link Relatives / Yearly Averages (seasonality)** — 07_market_regimes.md
**Meyers' Adaptive Range Breakout** — 02_trend_following.md, 09_exits.md, 13_indicator_reference.md
**Minimal (Manual) Walk-Forward** — 14_backtesting_and_validation.md
**Minimarkets Perspective** — 07_market_regimes.md, 16_research_hypotheses.md
**Mini QG Contract** — 07_market_regimes.md
**Minor Trend** — 01_market_structure.md
**Mistaking Luck for Skill** — 18_common_failure_modes.md — cited to Taleb
**Model Efficiency (ME)** — 11_risk_management.md, 14_backtesting_and_validation.md
**Model Risk** — 11_risk_management.md, 12_portfolio_construction.md
**Model-Category Shopping** — 18_common_failure_modes.md
**Modified 3-Crossover Model** — 02_trend_following.md, 08_entries.md, implementation_patterns.md ("Multi-Timeframe Agreement", N-of-M Confirmation Logic example)
**Modified Bollinger Bands (McNicholl)** — 04_breakouts.md, 02_trend_following.md, 13_indicator_reference.md
**Momentum (n-day) / Rate of Change (ROC)** — 05_momentum.md, 02_trend_following.md, 13_indicator_reference.md, hypothesis_bank.md ("Basic Momentum Trend-Following", "TRIX / ROC Trend-Direction Systems")
**Momentum Divergence** — 05_momentum.md, 16_research_hypotheses.md, hypothesis_bank.md ("MACD / Momentum Divergence Trading")
**Momentum Pinball (Raschke and Conners)** — 04_breakouts.md, 08_entries.md
**Momentum Surge Strategy (Pardo)** — 13_indicator_reference.md
**Momentum-Volume (MV)** — 05_momentum.md, 13_indicator_reference.md
**MomVectorBacktester Class** — 05_momentum.md
**Money Flow Index (MFI)** — 05_momentum.md, 13_indicator_reference.md
**Monte Carlo Sampling / Test Data** — 14_backtesting_and_validation.md
**Month-End Effect** — 07_market_regimes.md
**Morning Star / Evening Star** — 08_entries.md
**Moskowitz et al. (2012) Time-Series Momentum Study** — 02_trend_following.md, hypothesis_bank.md ("Time-Series Momentum (Moskowitz-style)")
**Moving-Average-Direction Filter (pattern)** — implementation_patterns.md — direction-of-change (not price-crossing) trend signal, Kaufman's lowest-frequency entry/exit family
**Moving-Average Crossover Systems** — hypothesis_bank.md — umbrella hypothesis card for Golden/Death Cross, 2-MA reversing crossover, 3-line confirmation variants; see also Modified 3-Crossover Model
**Moving Average Sequences (signal progression)** — 02_trend_following.md, 09_exits.md
**Moving Channel** — 04_breakouts.md, 13_indicator_reference.md
**Moving Median** — 02_trend_following.md, 13_indicator_reference.md
**Moving Skewness (McNicholl)** — 06_volatility.md, 13_indicator_reference.md
**MPTDI (Major Price Trend Directional Indicator)** — 02_trend_following.md, 08_entries.md, hypothesis_bank.md ("Composite Multi-Factor Trend Systems")
**Multi-Timeframe Agreement (pattern, Elder Triple Screen style)** — implementation_patterns.md
**Multi-Timeframe Trend Confirmation Systems** — hypothesis_bank.md — Elder's Triple Screen, Krausz's Multiple Time Frames, Pring's KST, Ichimoku Cloud
**Multimarket/Multiperiod Test and Optimization** — 14_backtesting_and_validation.md
**Multiple Strategies Diversification** — 12_portfolio_construction.md
**Multiple Time Frame Trend Methods** — 02_trend_following.md
**Multiple-Comparisons Problem** — 14_backtesting_and_validation.md, 18_common_failure_modes.md
**Murray Ruggiero** — 03_mean_reversion.md
**Myron Scholes / LTCM Anecdote** — 01_market_structure.md

## N

**N-Bar / N-Day Breakout** — 04_breakouts.md, 02_trend_following.md, 08_entries.md, 13_indicator_reference.md, 15_crypto_specific.md, hypothesis_bank.md ("N-Day / Channel Breakout Trend Family"), implementation_patterns.md ("N-Bar / Multi-Bar Confirmation")
**N-Day Average Daily Range (Pardo volatility proxy)** — 06_volatility.md
**N-Day High/Low (Moving High/Low)** — 13_indicator_reference.md
**N-of-M Independent Signal Agreement (2-of-3, 3-of-3)** — implementation_patterns.md — Confirmation Logic umbrella pattern
**NAAIM Exposure Index** — 07_market_regimes.md
**Natural Gas (NG) Seasonal Trade** — 07_market_regimes.md
**Negative Volume Index (NVI)** — 13_indicator_reference.md
**Neighbor-Averaging/Smoothing of Objective Functions** — 14_backtesting_and_validation.md, 16_research_hypotheses.md
**Net Momentum Oscillator (Chande &amp; Kroll)** — 05_momentum.md, 03_mean_reversion.md, 13_indicator_reference.md, hypothesis_bank.md ("Net Momentum Oscillator / Stochastics / Ultimate Oscillator Fades")
**Newton's South Sea Bubble Quote** — 01_market_structure.md
**NIC Device (Non-Interest-Bearing Cash)** — 12_portfolio_construction.md
**No Diversification During a Crisis** — 07_market_regimes.md, 15_crypto_specific.md, 18_common_failure_modes.md
**Noise vs. Volatility Distinction** — 01_market_structure.md, 06_volatility.md
**Nofri's Congestion-Phase System** — 08_entries.md, hypothesis_bank.md
**Nominality / Proportionality / Summation / Commonality / Variation Principles (Hurst)** — 07_market_regimes.md
**Nonstationarity of Financial Time Series** — 07_market_regimes.md
**Normal Carry (forward-curve structure)** — 07_market_regimes.md
**Normalized High Range / Normalized Low Range (NHR/NLR)** — 02_trend_following.md, 13_indicator_reference.md
**NR4 Pattern (Raschke's Range-Contraction Breakout)** — 04_breakouts.md, 08_entries.md

## O

**O'Higgins Strategy** — 03_mean_reversion.md, hypothesis_bank.md ("Dogs of the Dow / O'Higgins / Foolish Four & Rating-Service Basket Spreads")
**Objective Function (Fitness Function)** — 14_backtesting_and_validation.md, 13_indicator_reference.md (GASP)
**On-Balance True Range (Bierovic)** — 06_volatility.md, implementation_patterns.md ("Volume-Confirms-Price")
**On-Balance Volume (OBV)** — 13_indicator_reference.md
**Online Algorithm Pattern (offline vs. online)** — 14_backtesting_and_validation.md, 18_common_failure_modes.md
**Open Interest** — 01_market_structure.md, 13_indicator_reference.md, 15_crypto_specific.md
**Opening Range Breakout (ORB)** — 04_breakouts.md, 08_entries.md, 16_research_hypotheses.md, hypothesis_bank.md ("Opening Range Breakout (ORB) Family")
**Optimal f** — 10_position_sizing.md, 11_risk_management.md, 12_portfolio_construction.md, 13_indicator_reference.md, 15_crypto_specific.md, 16_research_hypotheses.md, 17_author_disagreements.md, README.md, hypothesis_bank.md, implementation_patterns.md
**Optimal Leverage Multiplier q** — 12_portfolio_construction.md
**Optimization Framework — Four Setup Decisions** — 14_backtesting_and_validation.md
**Order Sizing and Market-Impact Minimization** — 10_position_sizing.md
**Ornstein-Uhlenbeck Half-Life of Mean Reversion** — 03_mean_reversion.md, 05_momentum.md, 08_entries.md, 13_indicator_reference.md
**Oscillator (normalized/bounded momentum)** — 05_momentum.md, 13_indicator_reference.md, hypothesis_bank.md ("Oscillator/Momentum Fade Framework")
**Oscillator-Confirms-Trend (pattern)** — implementation_patterns.md
**Oscillator Fades / Contrarian Rules** — 03_mean_reversion.md
**Oscillator Method with ADX Filter (Kestner)** — 05_momentum.md, 07_market_regimes.md, 08_entries.md, 13_indicator_reference.md, hypothesis_bank.md ("ADX-Filtered Oscillator (Kestner) & Directional Parabolic"), implementation_patterns.md
**Outside Day with Outside Close (Arnold)** — 08_entries.md, 03_mean_reversion.md, implementation_patterns.md ("Time-Based Exit")
**Overbought/Oversold** — 05_momentum.md, 03_mean_reversion.md
**Overfit Forecasting-Model / Trading-Model Parable** — 04_breakouts.md, 14_backtesting_and_validation.md, 18_common_failure_modes.md
**Overfitting (general)** — 04_breakouts.md, 08_entries.md, 14_backtesting_and_validation.md, 16_research_hypotheses.md, 18_common_failure_modes.md, README.md
**Overleveraging Blowups** — 18_common_failure_modes.md
**Overnight Gap Risk** — 15_crypto_specific.md
**Overoptimization / Curve-Fitting / Data Mining** — 14_backtesting_and_validation.md
**Overparameterization** — 14_backtesting_and_validation.md, 18_common_failure_modes.md
**Overscanning** — 14_backtesting_and_validation.md, 16_research_hypotheses.md, 18_common_failure_modes.md

## P

**Pairs Trading** — 03_mean_reversion.md
**Palagi Ratio** — 11_risk_management.md
**Parabolic Interpolation Search** — 10_position_sizing.md, 16_research_hypotheses.md
**Parabolic SAR Trend/Exit Systems** — see Parabolic Time/Price System (Wilder's Parabolic SAR)
**Parabolic Time/Price System (Wilder's Parabolic SAR)** — 02_trend_following.md, 05_momentum.md, 09_exits.md, 13_indicator_reference.md, hypothesis_bank.md ("Parabolic SAR Trend/Exit Systems")
**Parameter Averaging** — 16_research_hypotheses.md
**Parameter-Grid Shape Bias** — 16_research_hypotheses.md, 18_common_failure_modes.md
**Parameterless Trading Models** — 14_backtesting_and_validation.md, 16_research_hypotheses.md
**Particle Swarm Optimization** — 14_backtesting_and_validation.md, 17_author_disagreements.md
**Parzen / Tukey Window (spectral analysis)** — 13_indicator_reference.md
**Peak Performance vs. Statistical Rigor Trade-Off** — 14_backtesting_and_validation.md
**Peak-Parameter Fragility** — 18_common_failure_modes.md
**Percentage Bands** — 04_breakouts.md, 02_trend_following.md, 13_indicator_reference.md
**Percentage Momentum (%M) / with Volume (%MV)** — 05_momentum.md, 13_indicator_reference.md
**Percentage-of-Price-Change Stop (Parabolic-style)** — 09_exits.md
**Perceptron (Neural Network) Regime-Switching** — 13_indicator_reference.md
**Perfect Profit (PP)** — 13_indicator_reference.md, 14_backtesting_and_validation.md
**Performance Evaluation as an Investment Decision** — 14_backtesting_and_validation.md
**Perp-Spot Basis / Funding-Rate Carry Arbitrage** — hypothesis_bank.md
**Perpetual/Continuous Contract** — see Continuous Contract
**Persistence Assumption (trend forecasting)** — 02_trend_following.md
**Pessimistic Return on Margin (PROM)** — 14_backtesting_and_validation.md, 15_crypto_specific.md
**Phase Length Test** — 14_backtesting_and_validation.md
**Phantom Trades / Tracking Errors (backtesting)** — 14_backtesting_and_validation.md
**Philip Gotthelf** — 02_trend_following.md
**Pivot Points** — 02_trend_following.md
**Pivot-Point Weighting (moving average)** — 02_trend_following.md, 13_indicator_reference.md
**Platykurtic / Leptokurtic / Mesokurtic** — 01_market_structure.md
**Point-and-Figure Charting** — 02_trend_following.md, 04_breakouts.md, 08_entries.md, 13_indicator_reference.md, hypothesis_bank.md ("Point-and-Figure / Renko Charting Trend Systems"), implementation_patterns.md ("Multi-Box (Point-and-Figure) Confirmation")
**Portfolio Insurance** — 12_portfolio_construction.md
**Portfolio Risk (Pardo taxonomy)** — 12_portfolio_construction.md, 11_risk_management.md
**Portfolio-Level Volatility Targeting** — 06_volatility.md, 10_position_sizing.md, hypothesis_bank.md ("Trend + Volatility-Target Sizing Combo", "Volatility-Stabilized Trend Portfolio"), implementation_patterns.md ("Volatility-Target / Vol-Parity Sizing")
**Position-Flip Order Sizing Formula** — 11_risk_management.md
**Position-Size Asymmetry (Hadady)** — 18_common_failure_modes.md
**Positive Volume Index (PVI)** — 13_indicator_reference.md
**Post-Earnings-Announcement Drift (PEAD)** — 05_momentum.md, hypothesis_bank.md ("Cross-Sectional Momentum & PEAD")
**Presidential Election Cycle** — 07_market_regimes.md
**Price and Volume Trend (PVT)** — 13_indicator_reference.md
**Price Density** — 01_market_structure.md, 07_market_regimes.md, 13_indicator_reference.md
**Price Manipulation as Source of Structural Change** — 01_market_structure.md
**Price Shock** — see Event Trading and Price Shocks
**Price Slippage / Trade Slippage** — 14_backtesting_and_validation.md
**Price Trend vs. Value Trend** — 01_market_structure.md
**Price-Shock P&amp;L Decomposition** — 16_research_hypotheses.md, 14_backtesting_and_validation.md, hypothesis_bank.md ("Price-Shock Reversal / Fade (daily scale)")
**Prathap's 3-Bar Inside Day Pattern** — 08_entries.md
**Primary / Secondary Trend (Dow Theory)** — 01_market_structure.md
**Principal Component Analysis (PCA)** — 13_indicator_reference.md, 16_research_hypotheses.md
**Principle of Confirmation (Dow Theory)** — 01_market_structure.md
**Prioritized Step Search (optimization)** — 14_backtesting_and_validation.md
**Probability of Backtest Overfitting (PBO)** — 16_research_hypotheses.md
**Probability of Drawdown (DP)** — 11_risk_management.md
**Profit Target via k×ATR** — 06_volatility.md, 09_exits.md
**Program-Trading Co-Movement** — 01_market_structure.md
**Projecting Moving Average Crossovers** — 02_trend_following.md
**Put-Call Parity** — 10_position_sizing.md
**Put-Call Ratio** — 07_market_regimes.md, 13_indicator_reference.md, hypothesis_bank.md ("Sentiment-Extreme Regime Signals")
**Pyramid-with-Profits Temptation** — 18_common_failure_modes.md — 1974 silver "always buy" system
**Pyramiding / Scaling Rules (pattern)** — implementation_patterns.md — see also Scaling In / Scaling Out

## Q

**Qualitative Data-Snooping** — 16_research_hypotheses.md, 18_common_failure_modes.md
**Quantified Spike Detection Rule** — 06_volatility.md, 08_entries.md

## R

**Random-Walk Baseline for Stop Rules** — 11_risk_management.md
**Ranking Based on Volatility (Appel mutual-fund selection)** — 06_volatility.md
**Rate of Change (ROC)** — see Momentum
**Rating-Service Basket Spread** — 03_mean_reversion.md
**Rearranging Data (Monte Carlo)** — 14_backtesting_and_validation.md
**Reg T Leverage Cap** — 10_position_sizing.md, 12_portfolio_construction.md
**Regime Shift (Chan definition)** — 07_market_regimes.md
**Regime-Conditional Stop-Loss Logic (Chan)** — 07_market_regimes.md, hypothesis_bank.md
**Regime-Switching (Markov approach)** — 05_momentum.md, 16_research_hypotheses.md
**Regime-Switching Between Two Sub-Strategies (pattern)** — implementation_patterns.md
**Regression-Based (Programmed) Channel Breakout** — 04_breakouts.md, 08_entries.md, 13_indicator_reference.md
**Regularization (Mills) / Exponential Regularization** — 02_trend_following.md, 13_indicator_reference.md
**Relative Strength (price minus trend)** — 05_momentum.md
**Relative Value Arbitrage** — 03_mean_reversion.md
**Relative Vigor Index (RVI)** — 05_momentum.md, 13_indicator_reference.md
**Relative Volatility (RV)** — 06_volatility.md, 13_indicator_reference.md, 16_research_hypotheses.md, implementation_patterns.md ("Relative Volatility Ratio")
**Renko Bricks** — 04_breakouts.md, 02_trend_following.md, hypothesis_bank.md ("Point-and-Figure / Renko Charting Trend Systems")
**Representativeness Bias** — 12_portfolio_construction.md, 11_risk_management.md
**Required Capital (RC)** — 09_exits.md, 11_risk_management.md, 14_backtesting_and_validation.md
**Reserve-Capital Sizing Check** — 11_risk_management.md, 18_common_failure_modes.md
**Reset Accumulative Average** — 02_trend_following.md, 13_indicator_reference.md
**Residual Impact (RI)** — 02_trend_following.md, 13_indicator_reference.md
**Retest-Before-Entry (pattern)** — implementation_patterns.md
**Retracement Theory** — 08_entries.md
**Returns Adjusted for Sample Error** — 14_backtesting_and_validation.md
**Reversal Day / Outside Reversal Day** — 08_entries.md, 03_mean_reversion.md, hypothesis_bank.md ("Reversal-Day, Weekday, and Day-of-Month Patterns")
**Reversal Rule** — 08_entries.md
**Reversed Dogs-of-the-Dow + Volatility-Triggered Hedge Overlay** — hypothesis_bank.md
**Reversing After a False Breakout** — 04_breakouts.md
**Reward-to-Risk Ratio (RRR)** — 11_risk_management.md, 14_backtesting_and_validation.md
**Richard Arms' Equivolume** — 13_indicator_reference.md
**Richard Bookstaber / Volatility System** — 02_trend_following.md, 04_breakouts.md, 08_entries.md
**Richard Dennis / Bill Eckhardt / The Turtles** — 02_trend_following.md
**Richard Donchian** — 02_trend_following.md
**Risk of Ruin** — 07_market_regimes.md (Optimal f/Kelly limitation), 11_risk_management.md, 12_portfolio_construction.md, 16_research_hypotheses.md
**Risk Preference Formula** — 11_risk_management.md
**Robert Bookstaber** — see Richard Bookstaber (Volatility System)
**Robert E. Davis Point-and-Figure Formations** — 02_trend_following.md
**Robert Joel Taylor / MPTDI** — 02_trend_following.md
**Robert Krausz's Multiple Time Frames** — 02_trend_following.md, 08_entries.md
**Robust Statistics (small-sample)** — 01_market_structure.md, 16_research_hypotheses.md
**Robustness (optimization profile) / Robustness Over Peak Optimization** — 14_backtesting_and_validation.md, 16_research_hypotheses.md, 18_common_failure_modes.md
**Role Reversal (support/resistance)** — 04_breakouts.md
**Rolling Correlation** — 12_portfolio_construction.md
**Roofing Filter (Ehlers)** — 02_trend_following.md
**Rudd's Special Set-Up Patterns** — 04_breakouts.md, 08_entries.md
**Ruggiero's ADX Trending/Consolidating Rules** — 08_entries.md, 13_indicator_reference.md
**Ruggiero's COT Stochastic Extreme Trade** — 07_market_regimes.md
**Ruin as Mathematically Certain** — 18_common_failure_modes.md — Vince unlimited-liability argument
**Runaway Gap** — 04_breakouts.md
**Runs Test / Serial Correlation Test** — 14_backtesting_and_validation.md

## S

**S&amp;P-Bond (High-Yield Timing) Arbitrage** — 03_mean_reversion.md
**Sample-Size Rule of Thumb (252 × parameters)** — 14_backtesting_and_validation.md, 16_research_hypotheses.md, 18_common_failure_modes.md
**Saucer Formation (Awesome Oscillator)** — 05_momentum.md
**Scaling In / Scaling Out** — 09_exits.md, implementation_patterns.md ("Pyramiding / Scaling Rules")
**Scan Range / Overscanning Risk** — 14_backtesting_and_validation.md
**Scenario Planning** — 10_position_sizing.md, 12_portfolio_construction.md, 16_research_hypotheses.md
**Schabacker's End-of-Bull/Bear-Market Signals** — 01_market_structure.md
**scikit-learn Three-Step API Pattern** — 14_backtesting_and_validation.md
**Scorpio's ATR-Based Daily Zones** — 06_volatility.md, 03_mean_reversion.md, 13_indicator_reference.md, hypothesis_bank.md ("Intraday Price Zones")
**Seasonal / Calendar Regime Effects** — see Seasonality
**Seasonality** — 07_market_regimes.md, hypothesis_bank.md ("Seasonal / Calendar Regime Effects")
**Seasonality Overfitting Warning (coffee/wheat case)** — 07_market_regimes.md
**Secondary Trend** — 01_market_structure.md
**Selective/Discretionary Override Bias** — 18_common_failure_modes.md
**Selling a Gap Open** — 04_breakouts.md
**Semivariance (SV) / Semivariance of Drawdowns (SDD)** — 11_risk_management.md, 12_portfolio_construction.md, 16_research_hypotheses.md, hypothesis_bank.md ("GASP — Genetic-Algorithm Multi-Strategy Portfolio Allocation")
**Sensitivity Analysis / Testing (parameter)** — 14_backtesting_and_validation.md
**Separation Theorem (Tobin)** — 12_portfolio_construction.md
**September 11 2001 Shock** — 07_market_regimes.md
**Setup/Intersection/Countdown (DeMark stages)** — 03_mean_reversion.md
**Shannon Entropy** — 13_indicator_reference.md, README.md
**Shape of the Optimization Profile (plateaus over peaks)** — 14_backtesting_and_validation.md
**Share Averaging Reallocation** — 12_portfolio_construction.md
**Sharpe Ratio** — 06_volatility.md, 11_risk_management.md, 12_portfolio_construction.md, 13_indicator_reference.md, 14_backtesting_and_validation.md
**Shifting Markets / Sources of Condition Variation** — 14_backtesting_and_validation.md
**Shoddy Inductive Reasoning** — 18_common_failure_modes.md
**Short Cycle Indicator ("LX")** — 13_indicator_reference.md
**Short-Term Bias** — 14_backtesting_and_validation.md
**Sibbett's Demand Index** — 01_market_structure.md, 13_indicator_reference.md
**Similarity of Systematic Signals (systemic-risk amplifier)** — 07_market_regimes.md
**Simple Moving Average (SMA)** — 02_trend_following.md, 13_indicator_reference.md
**Simplification Test** — 14_backtesting_and_validation.md
**Simulated Annealing** — 14_backtesting_and_validation.md, 17_author_disagreements.md
**Skewness (statistical moment)** — 01_market_structure.md
**Slippage Due to Size** — 14_backtesting_and_validation.md, 10_position_sizing.md
**Slope Divergence** — 05_momentum.md
**Small Dogs Variant (Dogs of the Dow)** — 03_mean_reversion.md
**Software Risk** — 12_portfolio_construction.md
**Sortino Ratio** — 11_risk_management.md
**Spectral Analysis / Periodogram / Spectral Density** — 13_indicator_reference.md
**Spike Detection Rule (True Range based)** — 06_volatility.md
**Split Adjustment** — 14_backtesting_and_validation.md
**Spread or Straddle** — 03_mean_reversion.md
**Stable Paretian Distribution** — 01_market_structure.md, 10_position_sizing.md
**Standard Deviation Moving Average (StdAvg)** — 02_trend_following.md, 13_indicator_reference.md
**Standard Error / Standard Error % (degrees of freedom)** — 14_backtesting_and_validation.md, 18_common_failure_modes.md
**Start-Up Overhead (Bias)** — 14_backtesting_and_validation.md, 16_research_hypotheses.md, 18_common_failure_modes.md
**Static Hedging / Dynamic Hedging** — 01_market_structure.md
**Stationarity (test)** — 05_momentum.md, 03_mean_reversion.md
**Statistical Significance of the Optimization Profile** — 14_backtesting_and_validation.md
**Status Quo Bias / Endowment Effect** — 12_portfolio_construction.md
**Step-Forward (Walk-Forward) Testing (Kaufman)** — 14_backtesting_and_validation.md
**Step-Weighting (moving average)** — 02_trend_following.md, 13_indicator_reference.md
**Stochastic Oscillator (%K/%D)** — 05_momentum.md, 13_indicator_reference.md
**Stochastic Fade (George Lane)** — 03_mean_reversion.md
**Stop and Reverse (SAR)** — 02_trend_following.md
**Stop-Loss Philosophy (strategy-type fit)** — 11_risk_management.md
**Stop-Loss Taxonomy (5 adaptive approaches)** — 09_exits.md
**Strategy Growth Avenues After Capacity Exhaustion** — 16_research_hypotheses.md — Chan's four-avenue framework
**Strategy Refinement Discipline** — 14_backtesting_and_validation.md
**Strategy Stop (SSL)** — 09_exits.md, 11_risk_management.md
**Stress Indicator Pairs Trade** — 03_mean_reversion.md
**Summary Table: Stop/Profit-Tool Fit by Strategy Type** — 09_exits.md
**Survivorship Bias** — 03_mean_reversion.md, 14_backtesting_and_validation.md
**Swing Trading / Swing Filter** — 02_trend_following.md, hypothesis_bank.md ("Event-Driven Swing Trend Systems")
**Swiss Franc Cycle** — 07_market_regimes.md
**SwamiChart** — 13_indicator_reference.md
**Symmetrical vs. Asymmetrical Strategies** — 08_entries.md, implementation_patterns.md ("Symmetrical vs. Asymmetrical Strategy Construction")
**Synthetic and Monte Carlo Test Data** — 14_backtesting_and_validation.md
**System Disconnect Failure Mode** — 18_common_failure_modes.md — 1987 crash case study
**Systematic Overreaction/Reversal Effect (post-shock)** — 07_market_regimes.md

## T

**Tangent Portfolio** — 11_risk_management.md, 12_portfolio_construction.md
**Taylor Trading Technique (George Douglass Taylor)** — 03_mean_reversion.md, 08_entries.md, hypothesis_bank.md
**TD Ameritrade Investor Movement Index** — 07_market_regimes.md
**Techno-Fundamental Trading** — 02_trend_following.md, 09_exits.md
**Terminal Wealth Relative (TWR)** — 10_position_sizing.md
**The Averages Discount Everything** — 01_market_structure.md
**The Losing Run Scenario (Pardo)** — 18_common_failure_modes.md
**The Risk of October (ricochet rallies)** — 07_market_regimes.md
**The Trend Persists (Dow Theory)** — 01_market_structure.md
**The Windfall Profit Scenario (Pardo)** — 18_common_failure_modes.md, 09_exits.md
**Theory of Relevant Data (Pardo)** — 07_market_regimes.md, 14_backtesting_and_validation.md
**Theory of Runs** — 10_position_sizing.md, 16_research_hypotheses.md, 18_common_failure_modes.md
**Thomas DeMark** — 03_mean_reversion.md
**Thomas Stridsman** — 02_trend_following.md
**Threshold to Geometric** — 10_position_sizing.md
**Thrust Oscillator** — 01_market_structure.md, 13_indicator_reference.md
**Tick Volume Indicator (TVI)** — 13_indicator_reference.md
**Tick-Bar/Volume-Bar Construction** — 15_crypto_specific.md, 16_research_hypotheses.md, hypothesis_bank.md ("Tick/Volume-Bar Construction for Crypto")
**Time-Based Exit (pattern)** — implementation_patterns.md
**Time Series Momentum (Hilpisch)** — 05_momentum.md, 08_entries.md, 13_indicator_reference.md, 02_trend_following.md (Moskowitz study), hypothesis_bank.md ("Time-Series Momentum (Moskowitz-style)")
**Time to Recovery** — 11_risk_management.md
**Time/Price Opportunities (TPO)** — 01_market_structure.md, 13_indicator_reference.md
**Timing the Order** — 02_trend_following.md
**Toby Crabel's Opening Range Breakout** — 04_breakouts.md, 08_entries.md
**Total Volume Convention** — 01_market_structure.md
**Trade List Report / Equity Curve Report (backtesting outputs)** — 14_backtesting_and_validation.md
**Trade Risk / Strategy Risk / Portfolio Risk (Pardo's three-tier taxonomy)** — 11_risk_management.md
**Trader Interference** — 18_common_failure_modes.md
**Trading Motives Taxonomy (Dorn et al.)** — 01_market_structure.md
**Trading Range** — 04_breakouts.md
**Trading-Day Annualization Convention** — 15_crypto_specific.md, 06_volatility.md
**Trailing Stop (pattern)** — implementation_patterns.md — see also ATR Usage Patterns, Trailing Volatility Profit Stop
**Trailing Volatility Profit Stop (Pardo)** — 06_volatility.md, 09_exits.md
**Trend + Support/Resistance Regime Overlay** — hypothesis_bank.md
**Trend + Volatility-Target Sizing Combo** — hypothesis_bank.md — this project's BEST-OF-PROJECT champion (TrendVolTarget); see also Volatility-Target / Vol-Parity Sizing
**Trend-Adjusted Oscillator (TAO)** — 07_market_regimes.md, 02_trend_following.md, 13_indicator_reference.md, implementation_patterns.md ("Oscillator-Confirms-Trend")
**Trend-Break Exit (pattern)** — implementation_patterns.md
**Trend-Following vs. Mean-Reversion Comparison Table (Kaufman)** — 07_market_regimes.md, 17_author_disagreements.md
**Trending vs. Sideways Oscillator** — 05_momentum.md
**Trendline Delay Techniques** — 04_breakouts.md
**Trendline-Direction Signal** — 02_trend_following.md, 09_exits.md
**Triangular Weighting / Triangular Moving Average (TMA)** — 02_trend_following.md, 13_indicator_reference.md
**Trident System (1975)** — 08_entries.md
**Trigonometric Regression (cycle detection)** — 07_market_regimes.md, 13_indicator_reference.md
**Triple Screen Concept (Barbara Diamond)** — 02_trend_following.md
**TRIX (Triple Exponential Smoothing)** — 05_momentum.md, 02_trend_following.md, 13_indicator_reference.md, hypothesis_bank.md ("TRIX / ROC Trend-Direction Systems")
**TRMV** — 05_momentum.md
**True Gap (DeMark/Larry Williams)** — 04_breakouts.md, 08_entries.md, hypothesis_bank.md ("True Gap / Wide-Ranging-Bar Breakout Entries")
**True Range** — 06_volatility.md, 13_indicator_reference.md
**True Strength Index (TSI)** — 05_momentum.md, 13_indicator_reference.md, hypothesis_bank.md ("TSI / RVI / Awesome Oscillator / Double-Smoothed Stochastic Momentum Systems")
**TSM Divergence / TSM Dunnigan / TSM Flexible Intraday Breakout / TSM Gap Study / TSM Intraday Gaps / TSM Intraday Shocks 2 / TSM Midday Support and Resistance** — 04_breakouts.md, 05_momentum.md, 08_entries.md
**Tukey Window** — 13_indicator_reference.md
**Turning-Points / Data-Mining Approach (regime detection)** — 05_momentum.md, 07_market_regimes.md, 16_research_hypotheses.md, hypothesis_bank.md ("Data-Mining Turning-Points Regime-Trigger Model (Alphacet)")
**Turning Points Test (validation)** — 14_backtesting_and_validation.md
**Turtles (The Turtles, Richard Dennis, Bill Eckhardt)** — 02_trend_following.md
**Turtles System 1 (S1) / System 2 (S2)** — 02_trend_following.md, 04_breakouts.md, 08_entries.md, hypothesis_bank.md ("The Turtles — System 1 (S1)", "The Turtles — System 2 (S2)")
**Turtles' Volatility-Normalized / Correlation-Capped Position Sizing** — 15_crypto_specific.md, 16_research_hypotheses.md, 09_exits.md, 12_portfolio_construction.md (De-leveraging rule), implementation_patterns.md ("ATR-Based Unit Sizing", "Pyramiding / Scaling Rules")
**Turtle Trading Strategy (TTS, Pardo's illustrative version)** — 04_breakouts.md, 02_trend_following.md, 08_entries.md
**Twin Peaks (AO bullish divergence)** — 05_momentum.md
**Two-Day RSI (Michael Stokes)** — 05_momentum.md, 03_mean_reversion.md, 13_indicator_reference.md
**Two-Moving-Average Crossover System (MA2/EOTS-MA)** — 04_breakouts.md, 02_trend_following.md, 08_entries.md
**Two-Trendline Detrending (Johnson/Ehlers)** — 13_indicator_reference.md, 02_trend_following.md, 09_exits.md
**Type I Error / Type II Error** — 14_backtesting_and_validation.md, 18_common_failure_modes.md

## U

**Ulcer Index (UI)** — 11_risk_management.md, 12_portfolio_construction.md
**Ultimate Oscillator (Larry Williams)** — 05_momentum.md, 03_mean_reversion.md, 13_indicator_reference.md
**Unables (missed fills around scheduled news)** — 09_exits.md
**Upside/Downside Ratio** — 01_market_structure.md, 13_indicator_reference.md
**Uptick Rule Elimination (2007)** — 07_market_regimes.md
**US 2016 Presidential Election Shock** — 07_market_regimes.md
**UTC Daily-Candle Boundaries** — 15_crypto_specific.md, 16_research_hypotheses.md, hypothesis_bank.md ("UTC-Daily-Boundary / Funding-Settlement Time-of-Day Effects")
**Utility Theory (Bernoulli, 1738)** — 11_risk_management.md, 16_research_hypotheses.md

## V

**Value at Risk (VaR)** — 11_risk_management.md, 12_portfolio_construction.md, 13_indicator_reference.md, 15_crypto_specific.md, README.md
**Value Area** — 01_market_structure.md
**Variance-Covariance VaR / Historical VaR / Kritzman-Rich Probability-of-Loss VaR** — 11_risk_management.md
**Vectorized Backtesting / Event-Based Backtesting** — 14_backtesting_and_validation.md, 18_common_failure_modes.md
**Velocity and Acceleration (trend/sideways classification)** — 07_market_regimes.md, 13_indicator_reference.md
**Victor De Villiers** — 02_trend_following.md
**VIDYA (Chande's Variable Index Dynamic Average)** — 07_market_regimes.md, 02_trend_following.md, 13_indicator_reference.md, implementation_patterns.md ("Efficiency-Adaptive Smoothing Constant" pattern)
**VIX (CBOE Implied Volatility Index)** — 06_volatility.md, 13_indicator_reference.md, hypothesis_bank.md ("VIX / IV Mean-Reversion Systems")
**Vince's Geometric-Optimal Portfolio & Combination Portfolio Allocation (CPA)** — hypothesis_bank.md — see also Combination Portfolio Allocation (CPA), Geometric Efficient Frontier
**Volatility-Band Trend/Breakout Systems** — hypothesis_bank.md — Bollinger, Keltner, Percentage Bands, 10-Day MA Rule, Modified Bollinger Bands, Rattlesnake method
**Volatility Bands** — 04_breakouts.md, 02_trend_following.md, 13_indicator_reference.md
**Volatility Breakout Based on Open or Previous Close** — 04_breakouts.md, 08_entries.md, hypothesis_bank.md ("Volatility Breakout Based on the Open or Previous Close")
**Volatility Dispersion Trading** — 06_volatility.md, hypothesis_bank.md ("IV/HV Relative-Value Arbitrage & Volatility Dispersion Trading")
**Volatility Expansion/Contraction Trade Selection** — 06_volatility.md
**Volatility Factor (VF)** — 06_volatility.md, 12_portfolio_construction.md, 13_indicator_reference.md, 16_research_hypotheses.md, hypothesis_bank.md ("Volatility-Stabilized Trend Portfolio (VF Rebalancing)"), implementation_patterns.md ("Volatility-Target / Vol-Parity Sizing")
**Volatility-Filtered Trend Following** — hypothesis_bank.md
**Volatility Parity Method (position sizing)** — 03_mean_reversion.md, 10_position_sizing.md, implementation_patterns.md ("Volatility-Target / Vol-Parity Sizing")
**Volatility Percentile / Empirical-Distribution Ranking (pattern)** — see Empirical Frequency Distribution (volatility percentiles)
**Volatility Profit Target (Pardo)** — 06_volatility.md
**Volatility Ratio (event measurement)** — 01_market_structure.md, 07_market_regimes.md
**Volatility Regime Switching** — 05_momentum.md
**Volatility Risk Stop (Pardo)** — 06_volatility.md, 09_exits.md
**Volatility-Stabilized Trend Portfolio (VF Rebalancing)** — hypothesis_bank.md — see also Volatility Factor (VF)
**Volatility System (Bookstaber)** — 04_breakouts.md, 02_trend_following.md, 06_volatility.md, 08_entries.md
**Volatility-Adaptive N (Seidel and Ginsberg)** — 04_breakouts.md, 02_trend_following.md, 13_indicator_reference.md
**Volatility-Adjusted Sizing (Pardo)** — 10_position_sizing.md, implementation_patterns.md ("ATR-Based Unit Sizing")
**Volatility-Target / Vol-Parity Sizing (pattern)** — see Portfolio-Level Volatility Targeting, Volatility Factor (VF)
**Volatility-Targeting Procedure (5-step)** — 06_volatility.md
**Volker Knapp** — 02_trend_following.md
**Volume Accumulator (VA)** — 13_indicator_reference.md
**Volume Count Indicator (VCI)** — 13_indicator_reference.md
**Volume Goes with the Trend (Dow Theory)** — 01_market_structure.md
**Volume Momentum / Volume % Change** — 13_indicator_reference.md
**Volume Oscillator** — 13_indicator_reference.md
**Volume Spike** — 01_market_structure.md
**Volume-Spike Mean-Reversion / Pseudo-Volume Strategy** — 16_research_hypotheses.md, 08_entries.md
**Volume-Weighted MACD (VWMACD)** — 13_indicator_reference.md
**VWAP (Volume-Weighted Average Price)** — 13_indicator_reference.md

## W

**W Intraday Volume Pattern** — 01_market_structure.md
**Walk of Empirical Development / Data Mining** — 14_backtesting_and_validation.md
**Walk-Forward Analysis (WFA)** — 07_market_regimes.md, 14_backtesting_and_validation.md, 15_crypto_specific.md, 17_author_disagreements.md, 18_common_failure_modes.md, README.md, EDGE_FRAMEWORK.md, AI_RESEARCH_PLAYBOOK.md, implementation_patterns.md ("Walk-Forward-Friendly Parameterization")
**Walk-Forward Efficiency (WFE)** — 14_backtesting_and_validation.md, 17_author_disagreements.md
**Walk-Forward-Friendly Parameterization (pattern)** — see Walk-Forward Analysis (WFA)
**Walk-Forward Window-Ratio Inconsistency** — 16_research_hypotheses.md, 17_author_disagreements.md, README.md
**Weekday/Weekend Reversal Patterns** — 03_mean_reversion.md
**Weekly Breakout Rule** — 04_breakouts.md, 02_trend_following.md
**Weighted Moving Average (WMA)** — 02_trend_following.md, 13_indicator_reference.md
**Wheeler Index of War** — 07_market_regimes.md
**Whipsaw Mitigation Techniques** — 04_breakouts.md, 09_exits.md (KAMA whipsaw-control filters)
**Wilder's Swing Index (SI)** — 02_trend_following.md, 13_indicator_reference.md
**William Blau** — 02_trend_following.md
**William P. Hamilton** — 01_market_structure.md
**Williams' A/D Oscillator (Waters-Williams)** — 05_momentum.md, 03_mean_reversion.md
**Williams %R** — 04_breakouts.md, 05_momentum.md, 13_indicator_reference.md
**Window Size and Model Life** — 14_backtesting_and_validation.md
**Winter's Self-Correcting Recursive Method (seasonality)** — 07_market_regimes.md
**Wyckoff's "Effort and Results"** — 04_breakouts.md

## X

**X-11/X-12-ARIMA** — 07_market_regimes.md

## Y

**Yates Correction** — 11_risk_management.md, 16_research_hypotheses.md
**Year-on-Year Momentum Strategy (Heston &amp; Sadka)** — 07_market_regimes.md, 02_trend_following.md

## Z

(no distinct entries beginning with Z were found in the 19 files)

---

## Scope and completeness note

This index was originally built by systematically reading all 19 files in `knowledge_base\` (README.md
plus `01_market_structure.md` through `18_common_failure_modes.md`) as they stood on 2026-07-09, after the
knowledge base's own two completeness-audit passes. It was then updated on 2026-07-09 to integrate four
newly-added bridge/foundation files — `hypothesis_bank.md` (83 hypothesis cards), `implementation_patterns.md`
(31 composable patterns), `EDGE_FRAMEWORK.md`, and `AI_RESEARCH_PLAYBOOK.md` — bringing the file's total
coverage to **23 files**. It indexes roughly **1000-1050 distinct entries** (before cross-file merging;
the alphabetized, merged list above runs to several hundred consolidated headword entries once recurring
terms — e.g. Bollinger Bands, Kelly criterion, Optimal f, KAMA, ADX, Walk-Forward Analysis — are collapsed
into single entries listing every file they appear in).

The 2026-07-09 update added new alphabetized entries for hypothesis cards and implementation patterns that
had no prior headword in this index (e.g. named hypothesis-bank cards like "Trend + Volatility-Target
Sizing Combo" or "BTC-ETH Cointegration Pairs Trading", and named implementation patterns like "ATR Usage
Patterns" or "N-of-M Independent Signal Agreement"), and added `hypothesis_bank.md` / `implementation_patterns.md`
/ `EDGE_FRAMEWORK.md` / `AI_RESEARCH_PLAYBOOK.md` citations to dozens of pre-existing entries (e.g. Kelly
Criterion, ADX, Bollinger Squeeze, KAMA/VIDYA/FRAMA, Kase's DevStop, Walk-Forward Analysis, Deflated Sharpe
Ratio) that also recur in the four new files. Existing entries and their original file citations were
preserved unchanged except where a new citation was appended.

This index does **not** cover the deeper per-book `Knowledge\<Author>_<Short_Title>\` folders except
insofar as their content has already been consolidated into the 19 numbered `knowledge_base\` files — per
the knowledge base's own README, those folders are the "deeper, rawer layer" and are not separately
indexed here. Research-hypothesis entries from `16_research_hypotheses.md` and `hypothesis_bank.md` are
indexed at the granularity the source file itself uses (individual hypotheses/cards where the file names
them individually; coarser thematic groupings — noted as such — where the file's own treatment is
thematic). No entry below was invented; every term traces to actual content encountered in the 23 files
during extraction. If a term you expect to find is missing, it may be discussed in the source files only
as part of a longer passage without being given a distinct named-concept treatment — consult the relevant
topic file directly (see the File Map in README.md) rather than assuming the concept is absent from the
knowledge base.
