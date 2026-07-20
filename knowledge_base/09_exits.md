# 09 — Exit Techniques: Stops, Profit-Taking, and Trade Management

Consolidated exit-technique reference drawn from the five extracted source books under `Knowledge/`. Scope: stop-loss taxonomy, volatility-scaled stops (Kase DevStop, ATR stops, Parabolic/Chandelier-style trailing stops), profit-taking logic and the "cutting the right tail" warning, trend-break exits, day-trading time exits, Pardo's exit-design/trade-management machinery, and exit-vs-entry asymmetry. Every claim is tagged to its source book and chapter. Where a source explicitly flags an unrecoverable formula or an internal inconsistency, that flag is preserved rather than resolved.

Cross-references: see `06_volatility.md` for the underlying volatility measures (ATR, standard deviation, Efficiency Ratio) used throughout this file's stop constructions; `07_market_regimes.md` for the trending-vs-mean-reverting regime classification that governs which exit tool applies; `08_entries.md` for the entry-side counterparts to several rules described here (e.g., the same trend/breakout systems whose exits are detailed below).

---

## 1. Stop-Loss Taxonomy (Money/Volatility/Chart/Time)

Kaufman's Chapter 23 (Risk Control) is the book's dedicated risk chapter and gives the fullest single taxonomy of stop-loss construction methods in the entire knowledge base. It presents **5 stop-placement approaches that adapt to market conditions**, explicitly numbered (Kaufman Ch.23):

1. **Chart-based / support-resistance stop** — placed at the previous support or resistance level.
2. **Volatility-based stop** — a multiple of current volatility, e.g., 3× the 10-day ATR.
3. **Percentage-of-price-change stop (Parabolic-style)** — advances the stop by a percentage of the price change since entry (Wilder's approach; see §3 below).
4. **Swing-based stop** — the recent swing high/low, defined by a minimum % swing filter.
5. **Channel/extreme stop** — the highest-high or lowest-low of the most recent n periods.

Kaufman separately enumerates **3 trailing-stop constructions** (Kaufman Ch.23):
1. **Fixed-percentage trailing stop** — trails below the highest closing price reached during the trade (e.g., a 3% trail); never retreats; exits on either a trend-change signal or the percentage breach, whichever comes first.
2. **Volatility-based trailing stop** — closer when volatility is low, farther when volatility is high; positioned from the best high/close (e.g., highest price − 5×10-day ATR); some traders withhold activating the stop until a minimum profit level is reached.
3. **Breakeven lock-in** — reposition the stop to the entry price once a profit threshold is reached ("don't let a profit turn into a loss"); **explicit risk flagged**: done too soon, ordinary market noise triggers it prematurely.

And a distinct category, the **Risk Control Overlay — 3 named alternatives to price/volatility-based stops**, each with a stated weakness (Kaufman Ch.23):
1. **Percentage of initial margin** (e.g., 50-70%) — "loosely related to long-term volatility but lags considerably."
2. **Percentage of portfolio/account value** (e.g., 1.0-2.5%) — the popular "equalized risk" approach, but insensitive to individual-market volatility divergence (too tight in some markets, too loose in others).
3. **Maximum Adverse Excursion (MAE)**, cited to Sweeney — stop placed just beyond the historic MAE per trade, or 2.5% of price, whichever is smaller.

**Money-based stops** appear across the book as the simplest, most naive baseline: Kaufman contrasts a beginning trader's "no trade should lose more than $500" rule against the more experienced "never lose more than 3% of total investment on a single trade" rule, explicitly stating that risk *magnitude* should be handled via leverage adjustment rather than an arbitrary fixed-dollar stop (Kaufman Ch.23). Pardo independently defines and gives a worked example of a **dollar risk stop**: a fixed $ amount from entry (e.g., $1,000 = 4.00 pts risk on a long entered at 350 → stop at 346) (Pardo Ch.5).

**Volatility-based stops** are treated as the generally preferred adaptive method by both books. Pardo's **volatility risk stop** sizes the stop distance as a function of a volatility measure such as the 3-day average daily range (e.g., 3-day avg range = 5.55 pts → stop on a long at 350.00 is 344.45); Pardo states this is **explicitly preferred over a fixed dollar amount because it automatically adapts as volatility expands/contracts** (Pardo Ch.5).

**Pardo's dollar-based profit-management constructs** (the profit-side counterparts to the dollar risk stop above, Pardo Ch.5): a **trailing dollar profit stop** trails a fixed $ distance from the running high/low — example: $1,000 (2 pts) trail; long at 350, high reaches 356 → trailing stop = 354, exit locks in ~$2,000 (minus costs). A **dollar profit target** is a fixed $ distance limit order from entry — example: $1,000 (2 pts) target on a short entered at 350.00 → buy target at 348.00. Both carry the same overnight-gap caveat as every other Pardo stop/target construction (§8 below).

**Percent-of-equity risk stops** (Pardo Ch.5): risk is sized as a fixed % of account equity, divided across position size — e.g., $100,000 account, 2 contracts, 1% equity risk → $1,000/2 = $500/contract = 2.00 pts/contract; stop on a long at 350 → 348.00. Pardo cites W. D. Gann's historical "Rule of Ten" ("never risk more than ten percent of your trading capital on any trade") as a precedent, noting contemporary practice favors much smaller (~1%) risk fractions, and explicitly notes this method **only makes sense paired with an equity-scaling position-sizing rule** — otherwise risk-per-trade silently grows as account equity grows while position size stays fixed.

**Time-based stops** are documented mainly as named-system rules rather than as a generalized taxonomy category (see §7 for the day-trading-specific treatment). Two concrete instances from Kaufman's Chapter 4 named-systems survey (Kaufman Ch.4, cross-referenced in Risk_Management.md):
- **Outside Day with Outside Close (Arnold)**: a stop-loss just below the outside day's low (long) or above its high (short), combined with a fixed timed exit 3 days after entry (tested range 1-5 days) regardless of whether the stop has been hit.
- **Nofri's Congestion-Phase System**: the author's own test used **no stop-loss at all**, since trades were held only 1 day — an explicit example of a pure time exit substituting entirely for a price-based stop.

**Chart-based stops** recur throughout the named-system material: e.g., the **Cambridge Hook** places a protective stop above the high of the signal day for a short entry (mirror below the low for a long) — "stop beyond the pattern's defining extreme" (Kaufman Ch.9). **DeMark's Sequential™** gives two chart-based stop variants: (a) subtract the true range of the lowest-range day (within the combined setup+countdown period) from that day's low, or (b) subtract the close-to-low distance of the lowest day from that day's low for a tighter stop (Kaufman Ch.4). **Elder's Triple-Screen 3-step stop-loss progression**, described as a "general-purpose, reusable risk template," combines chart-based and profit-lock elements: (1) initial stop at the lower of the entry-day low or previous-day low; (2) move to breakeven as soon as practically possible, with an explicit caution that room must remain between the stop and current price or it will trigger immediately; (3) thereafter trail the stop to protect 50% of the highest achieved open profit (Kaufman Ch.19).

### Kaufman's explicit strategy-type/tool-fit rule (a load-bearing summary claim)
> "Stop-loss: works for trending systems in trending markets; bad for non-trending markets or mean-reversion systems. Profit-taking: works for mean-reversion/short-term strategies; bad for trending markets or long-term trend strategies." (Kaufman Ch.23)

This is stated as a **non-interchangeable** pairing — the two risk tools are not substitutes for each other, they are matched to opposite strategy types.

### The random-walk baseline for judging whether a stop rule adds value
Kaufman gives an explicit diagnostic: using random numbers, **(number of times a stop is triggered) × (distance of the stop) is roughly constant** — a stop rule must beat this random-baseline relationship to be considered genuinely informative rather than an artifact of placement distance (Kaufman Ch.23). Tight stops get hit often; farther stops less often — "the pattern is very similar to random price moves."

### Kaufman's own judgment on which stops "work"
Explicitly framed as unclear/debated: stops sometimes execute at the worst price of the day, sometimes save a trader from disaster. **Author's judgment**: stops that adapt to volatility (e.g., the std-dev/Kase stop) are "most likely to work," more so than fixed-dollar or fixed-percentage stops; support/resistance-based stops are "also good"; trailing stops are "the most practical" (Kaufman Ch.23). A worked heat-map test (Table 23.7, US 30-yr bonds 2000-2011, MA strategy) found the average of all tests using a trailing stop beat no-stop, with the best results combining longer trend periods with stop factors of 4-6 ATR.

### Noise-timing asymmetry in stop execution
Because of market noise, Kaufman states stop-losses are usually based on the **closing price**; but for intraday systems (higher noise), a triggered stop should still wait for the close (to allow a pullback), while **profit-taking should exit at the intraday spike rather than waiting for the close** — an explicit asymmetric-timing recommendation between how stops and profit targets should each be evaluated intraday (Kaufman Ch.23).

### A contrasting view: is stop-loss even good risk management?
Chan directly challenges the "stops prevent catastrophic losses" premise as a common fallacy, presenting the **opposite conditional logic** to Kaufman/Pardo's largely stop-favorable framing (Chan Ch.6, "Is Stop Loss Good Risk Management?"):
- **Reasoning against blanket stop-loss use**: during a genuine catastrophic/discontinuous price event, stop orders fill at prices far worse than pre-event levels — exiting via a stop *realizes* the catastrophic loss rather than avoiding it.
- **Conditional rule, explicit**: IF the trader believes they are in a momentum/trending regime (price likely to continue worsening within the trade's expected lifetime) → a stop loss is beneficial. IF the trader believes they are in a mean-reverting regime within that lifetime → a stop loss is **harmful** (it forces an early, unnecessary exit right before the position would otherwise have recovered via reversion).
- **Chan's own heuristic for distinguishing the two regimes** (explicitly labeled as his own observation, not a formally derived rule): a price move driven by news/fundamentals (e.g., deteriorating revenue) is likely a momentum regime ("don't stand in front of a freight train") because the move to a new equilibrium is irreversible absent a fundamental reversal; a price move with no apparent news/fundamental cause is likely a liquidity event (forced liquidation, short-covering), typically short-duration with a likely mean-reversion back to prior levels.

This is presented in this knowledge base as a genuinely different position from Kaufman's strategy-type/tool-fit rule above: Kaufman's rule is stated as a property of the *strategy type* (trend vs. mean-reversion), while Chan's rule is a property of the *believed cause of the specific price move* — the two are not strictly contradictory but use different diagnostic axes and neither source reconciles them explicitly.

A further gap, noted rather than filled: Hilpisch's book documents that broker APIs (`tpqoa.create_order`, FXCM order methods) **support** stop-loss distance, trailing stop-loss distance, and take-profit price parameters, but **none of the book's worked strategy examples actually use them** — every live/backtested example relies solely on the model's own signal reversal to exit a position, with no independent protective stop (Hilpisch, Risk_Management.md). This is flagged in the source extraction as an explicit gap in the book's own coverage, not a stated recommendation against stops.

---

## 2. Kase DevStop

Cynthia Kase's Dev-Stop (1993) is documented twice in the Kaufman extraction — once as a named indicator entry (Ch.18) and once with the full worked stop-placement procedure (Ch.23) — and the two entries give **slightly different multiplier figures**, both preserved here verbatim per the traceability rule rather than merged.

### Ch.23's full procedure (Kaufman Ch.23)
1. Compute the True Range (TR) of the past 2 trading days (highest high, lowest low over the 2-bar window).
2. Compute the rolling ATR of that 2-day TR series (30 bars for intraday charts, 20 days for daily charts — each "period" spans 2 underlying days).
3. Compute the standard deviation (STDEV) of the TR series over the same 20-day/30-bar window.
4. **Stop-loss formula**: `DDEV = ATR + (multiplier) × STDEV`, where the multiplier ranges **"2.06 to 2.25, and 3.20 to 3.50"** — flagged by the extraction as an embedded-graphic gap: the source's own exact mapping of which multiplier-pair applies under which condition did not survive PDF extraction. The larger values of each pair are stated to "correct for skew and allow for greater risk."
5. Dev-stop for longs = Trade High − DDEV; for shorts = Trade Low + DDEV (Trade High/Low = the price of greatest favorable excursion during the trade).

A worked chart example is cited: 30-year bond, 80-day MA with an 80-period window, factor-of-8 std-dev stop band (Kaufman Ch.23).

### Ch.18's indicator-entry description (Kaufman Ch.18, Indicators.md)
- **Construction**: three stop levels, each = (2-day ATR) − (1.0, 2.2, or 3.6 standard deviations of that ATR, taken over 20 days), subtracted from the closing price (not from a trendline). The 2-day ATR smooths the stop so it does not jump around with the raw daily close.
- **Entry rules** are the extraction's own reconstruction, since "other than the positioning of the stops, Kase's rules are not disclosed": buy when the fast 5-day trend crosses above the slower 21-day trend; sell when the fast 5-day trend crosses below the slower 21-day trend.
- **Position sizing tied to the three risk levels**: because there are 3 stop levels, positions are entered in multiples of 3 contracts/units; each time a stop level is crossed, one unit is removed (scale-out risk reduction) — described in Risk_Management.md as "an explicit example of graduated (not binary) risk reduction as a trade moves against a position" (Kaufman Ch.18). Full position resets when the trend changes direction.
- **Result cited**: "still good" on crude oil futures (Figure 18.4) — no numeric performance table given in the extracted text.
- **Ambiguity flagged**: the exact combining formula/arithmetic for the "first stop" calculation is an embedded-graphic gap; only the verbal description (2-day ATR minus a multiple of its 20-day SD) and the three stated SD multiples (1.0, 2.2, 3.6) survived as clean text.

**Note on the discrepancy**: Ch.23 gives multiplier pairs 2.06-2.25 and 3.20-3.50 with an unresolved mapping rule; Ch.18 gives three specific multiples (1.0, 2.2, 3.6) with no mapping rule given either, applied instead to three separate simultaneous stop *levels* (tiered scale-out) rather than a single selected stop distance. Both are preserved as-extracted; the source material does not reconcile which version is authoritative or whether they describe the same or different published versions of Kase's method.

Kase's DevStop is cross-referenced in Risk_Management.md as "an explicit tiered position-reduction risk model" (Kaufman Ch.18) — distinguished from a single binary stop by removing one-third of the position at each of the three crossed levels.

---

## 3. Chandelier and Parabolic Trailing Stops

**A direct terminology note**: the Kaufman extraction contains no occurrence of the term "Chandelier" or "Chandelier Exit" anywhere in the book (confirmed by search across all chapter files). The book's equivalent adaptive-trailing-stop content is **Wilder's Parabolic Time/Price System**, documented fully in Chapter 17 (Adaptive Techniques), which functions as this book's closest analog to a chandelier-style trailing stop (a stop that trails price using a volatility/range-derived offset from the extreme favorable price reached).

### The Parabolic Time/Price System (Wilder, *New Concepts in Technical Trading Systems*, 1978) — Kaufman Ch.17
- **Philosophy**: "time is an enemy" — once entered, a position must continue to be profitable or it will be liquidated. The system is always in the market; every exit is also a reversal (Stop and Reverse, SAR).
- **SAR calculation**: an exponential-smoothing-style formula using the high price while long (or low price while short), with an Acceleration Factor (AF) as the smoothing constant.
- **AF progression**: starts at 0.02 at the beginning of each trade, increases by 0.02 after any day making a new extreme (new high while long / new low while short), capped at a maximum of 0.20 (a 9-day-MA equivalent; AF=0.02 initially is roughly a 99-day-MA equivalent).
- **SAR initial point (SIP)**: the lowest point of the prior move (for a new long) or the highest point of the prior move (for a new short).
- **Noise-protection rule (explicit anti-whipsaw design)**: the SAR may never be closer to price than the most recent 2-day high/low range — for longs, SAR may never exceed the low of today or the prior day (reset to that low if the formula would place it higher); for shorts, SAR may never be below the high of today or the prior day. Risk_Management.md frames this as "a concrete worked example of building noise-tolerance directly into a stop/reversal mechanism" (Kaufman Ch.17).
- **Reversal condition**: occurs when a new intraday extreme (low while long, high while short) penetrates the SAR.
- **Author's stated strengths and weaknesses (Kaufman Ch.17)**: strong point — the initial SAR is a genuine market-extreme price (not a statistically derived point), and the 2-day floor/ceiling prevents noise-driven reversals during a strong move. Weak point, explicitly flagged as a live-trading risk elsewhere in Risk_Management.md — **AF always restarts at 0.02 regardless of how fast the market is already moving at entry**, meaning a fast-starting trend gets an unnecessarily wide initial stop; "a market moving quickly at entry might be better served starting with a faster AF." The method also "requires fairly consistent price swings to be profitable."
- Cross-referenced elsewhere in the book: combined with Directional Movement to form the **Directional Parabolic System (DPS)** (Kaufman Ch.9), which uses ATR-based initialization (ATR length 3, factor 1.5) with the same 0.02-start/0.20-cap acceleration structure — the 0.20 cap is described as "an explicit ceiling on how fast the trailing stop can ratchet in, preventing an overly tight stop during strong trends" (Kaufman Ch.9).

### Knapp's ER-based Parabolic variant (Kaufman Ch.17)
Volker Knapp (*Active Trader*, September 2010) proposes replacing Wilder's fixed AF progression with a 10-day ATR/10-day ER-based stop adjustment. The IF/THEN structure is preserved even though the specific numeric thresholds are an embedded-graphic gap:
1. Set the initial stop at an ATR-based distance from entry (exact multiple not recoverable).
2. IF ER is at one threshold level, THEN leave the stop unchanged.
3. IF ER is at a higher threshold, THEN reduce the stop's distance by an ATR-based amount (not recoverable).
4. IF ER is at a further threshold, THEN reduce the stop distance by a different (larger) ATR-based amount (not recoverable).
5. The trailing stop only ever advances (higher for longs, lower for shorts) — never retreats.
6. The stop applies to trading on the next day.
Explicitly noted: the rules are **not symmetric between longs and shorts**.

### Adaptive whipsaw-control filters (applicable to any exponential-smoothing-based adaptive trailing method, e.g., KAMA)
Because KAMA and related adaptive smoothing methods technically flip direction on any price penetration — even during a near-zero-smoothing-constant "sideways" phase — Kaufman gives **two filter choices** to prevent structural, avoidable whipsaw losses (Kaufman Ch.17):
1. A factor f (suggested small, e.g., f = 0.01) times the 20-day standard deviation of the trendline's own period-to-period changes, added/subtracted as a band that must be penetrated before a direction change counts.
2. Track the most recent trendline low (after an up-turn) or high (after a down-turn); require the trendline to move away from that extreme by a fixed amount F before signaling.
Kaufman's own testing finding: **option 2 (fixed-amount move filter) is the better choice** and is what the chapter's own results use.

**Explicit gap flagged for this section**: no source in this knowledge base uses the specific term "Chandelier Exit" (the widely-known Chuck LeBeau construction of highest-high-minus-N×ATR). The functionally closest documented technique is Wilder's Parabolic SAR (above) and the general "volatility-based trailing stop" category in §1 (highest price − k×ATR). Readers seeking the specific named Chandelier Exit formula will not find it verbatim in this knowledge base; only its structural cousins are present.

---

## 4. ATR Stops

ATR-based stop and profit-target construction recurs across multiple chapters as the book's default volatility-scaling tool.

### Profit-Taking via ATR (Kaufman Ch.23)
Two explicit volatility-based profit-taking methods:
1. **Fixed target at entry**: profit target = entry point ± f × ATR (typical f = 3-4 using a 20-day ATR). Kaufman notes "most analysts data mine to find the best factor" — a self-flagged overfitting risk in this specific technique.
2. **Momentum-triggered exit**: any single-day (or cumulative) favorable move of f × ATR triggers the exit, on the assumption that any sufficiently large move will mean-revert even mid-trend.

**Scaling Out as an anti-data-mining technique** (Kaufman Ch.23): rather than committing to one "best" ATR factor, use 3+ profit targets simultaneously — e.g., a "best" factor of 3.0 bracketed by 2.0/4.0 or 1.5/4.5 — so the average of the targets approximates the single best-fit factor while partial exits reduce exposure without needing the exact best factor. Risk_Management.md explicitly cross-references this to "this project's own ensemble-averaging discipline."

### The Bookstaber k×ATR formula for both stops and targets (Kaufman Ch.20)
An identical volatility-based formula (cited to Bookstaber) can define **both** a profit target and a stop-loss using k×ATR with **k≈3**, but the two constructs are used differently by design:
- **Profit targets**: triggered on the intraday high/low, but exited on the close after a stop trigger — to capture noise-driven price recovery.
- **Stop-loss levels**: must be kept far enough from price to avoid noise-triggering.
**Structural warning shared by both** (Kaufman Ch.20): for long-term trend systems, taking profits or being stopped out while the underlying trend remains intact requires deliberate re-entry logic, or the system risks systematically missing the rare large "fat tail" trades that justify trend-following in the first place.

### ATR-based volatility risk stop (Pardo Ch.5)
As given in §1: risk distance = a multiple of a volatility measure (e.g., N-day average daily range); example: 3-day avg range = 5.55 pts → sell stop on a long at 350.00 → stop at 344.45. Pardo's parallel construction on the profit side is the **trailing volatility profit stop**: distance = a % of a volatility measure, e.g., 50% of a 3-day avg range of 5.50 pts = 2.75 pts; long at 350, high reaches 356 → stop 353.25, locking ~$1,625 (Pardo Ch.5). And the **volatility profit target**: distance = a larger % of the volatility measure, e.g., 150% of a 3-day avg range of 5.50 pts = 8.25 pts; long at 350 → sell target 358.25 (~$4,125 gross) (Pardo Ch.5).

### The Turtles' ATR-based stop (a fully worked historical example, Kaufman Ch.5)
- **Per-trade stop**: 2L from entry, where L is a 20-day ATR-based volatility measure converted to dollars via the market's big point value.
- **Exit priority, explicit**: first of (a) the 2L stop-loss, (b) an opposite breakout signal, (c) a 2%-of-portfolio loss (calibrated so 2L = 2% of portfolio at entry).
- **Compounding mechanic**: additional units added per L of favorable movement (up to 5 units); once a 2nd unit is added, **all stops for the whole position move to 2L from the most recent entry** — engineered so total trade risk stays constant regardless of how many units are held.

### A quantified high-volatility exit/re-entry threshold (Kaufman Ch.20)
Distinct from a per-trade ATR stop, this is a regime-level volatility overlay: **annualized volatility above ~45%** is associated with declining returns and rising risk on individual markets; the recommended response is to exit and wait for volatility to fall to **~35%** before re-entering — explicitly framed as a risk-management overlay independent of the underlying trading signal, applicable to a trend or any other system. A portfolio-level analog uses a 12% annualized daily-return target (typical for futures fund managers): deleverage above 12%, increase leverage below it.

### Kaufman's Directional Parabolic System ATR initialization (Kaufman Ch.9)
ATR-based initialization uses ATR length 3, factor 1.5, combined with the Wilder acceleration factor structure (start 0.02, cap 0.20) described in §3.

---

## 5. Profit-Taking and Cutting the Right Tail

### The core trade-off, stated explicitly and repeatedly
Kaufman's Chapter 8 (Trend Systems) states the book's central warning about profit-taking and stops applied to trend systems:
> "Adding stop-losses or profit-taking to a basic trend system reduces or eliminates the ability to capture the fat-tailed windfall trades that make classic trend-following profitable overall" — stated as a direct, unavoidable trade-off, not a free improvement. Traders who dislike giving back large unrealized profits when a major trend reverses must accept this cost consciously. (Kaufman Ch.8)

This is grounded in the **fat-tail** finding documented earlier in the same chapter: a 40-day SMA strategy applied to five diverse futures markets (30-yr bonds, S&P, euro, crude oil, gold) produces trade profit/loss histograms extended far to the right (fat tail of large wins) with a much shorter left tail (small, frequent losses) — e.g., in the S&P results, one $18,750-bin profit offset 15 losses in the highest-frequency −$1,250 bin. **Key stated principle: a pure trend strategy needs this asymmetric distribution shape to be profitable** (Kaufman Ch.8).

Kaufman's **generalized moving-average trend-following profile** (Kaufman Ch.8), drawn from a NASDAQ futures full-history test (1998-June 2018, 80-day trendline system, Table 8.4):
- Percentage of profitable trades is low, about 35%.
- Average winning trade must be significantly larger than the average losing trade — given only 35% wins, the win:loss ratio must exceed ~2.86:1 just to break even.
- Average winning trades are held much longer than losing trades (in the worked table: 47.3 bars average for winners vs. 10.09 bars for losers).
- High frequency of losing trades produces long losing-trade sequences.
- This risk/return shape is called **conservation of capital** (cut losses quickly, let profits run).

### "Cut your losses and let your profits run" formalized, and its inversion warned against
Risk_Management.md's Ch.8 summary states the risk explicitly: adding stops/profit-taking risks **flipping the intended asymmetry into "take your profits and let your losses run"** if done carelessly — an explicit author caution to be "very careful when making exceptions" to the basic trend-following risk shape (Kaufman Ch.8).

### Kaufman's own direct framing subsection on stops and profit-taking (Kaufman Ch.23)
> "Profit targets are essential for short-term/mean-reversion trading (price noise reverses fast), but more difficult to incorporate into a longer-term trend-following system because they risk missing the bigger profit (the fat tail)" — trend followers who take profits need a re-entry plan to avoid missing rare large moves.

### Windfall-profit risk management (a related but distinct caution, Kaufman Ch.5 and Ch.22)
An unusually large unrealized profit from a price shock should **not** be assumed to persist. Explicit suggestions: wait for a standard reversal-size retracement before exiting all/part of the position (preserves re-entry potential), or reduce position size during extreme volatility ("volatility stabilization"). **Explicit warning**: "A trading system should not depend on a single, very large profit to prove its success" — treat outsized shock-driven gains as a risk-management event, not validation of the strategy (Kaufman Ch.5). Chapter 22's crisis-management rule extends this: **exit immediately on a windfall profit from a price shock**; by contrast, **hold (do not panic-exit) a large loss from a price shock**, expecting a same-direction reversal within days — an explicit asymmetric prescription for windfall gains vs. windfall losses (Kaufman Ch.22).

### Pardo's parallel framing of profit targets (Pardo Ch.5)
Profit targets are defined as "an unconditional exit of a trade with a locked-in profit at some predetermined price or profit level," placed as a price/limit order. **Trade-off, explicit**: profit targets lock in gains immediately (can't be given back) but cap upside if the market keeps running past the target; targets tend to raise win % and smooth the equity curve but can reduce total captured profit. **Pardo's general guidance, explicitly stated as general, not universal**: active/countertrend strategies from overbought/oversold conditions benefit most from profit targets, while slower trend-following strategies benefit least — directly consistent with Kaufman's strategy-type/tool-fit rule (§1) even though the two books never cross-reference each other.

A fill-risk caveat unique to profit-target orders (Pardo Ch.5): unlike stop orders, limit-order profit targets carry the risk of **never filling at all** — Perry Kaufman is cited elsewhere (by Pardo) as estimating up to **30% of limit orders go unfilled**. Overnight gaps can also work *in favor of* a resting profit target: a favorable gap-through fills at the better open price (example: a 10-point favorable gap adds $5,000 beyond the nominal target).

### Pardo's windfall-profit anecdote (a real-time psychology parallel to Kaufman's warning, Pardo Ch.14)
Pardo recounts a Chicago trading firm reportedly making "over one billion dollars" on S&P/T-bond positions in the days after the 1987 crash, paying large bonuses and closing operations for a month-long paid vacation. Pardo poses this rhetorically ("Good idea or bad?") without resolving it definitively — presented as an open anecdote, not a settled recommendation. **Core lesson, stated directly**: a windfall should be enjoyed but not treated as a repeatable baseline, nor as proof of the strategist's brilliance — "It was more a matter of being in the right place at the right time. A good trader knows the difference between luck and skill." This directly parallels Kaufman's "mistaking luck for skill" framing in Ch.23 (see also `01_...` risk-of-ruin material and Psychology cross-cutting files).

### Bollinger's own risk-reduction view on mean-reversion profit-taking (Kaufman Ch.8)
Bollinger's own recommended usage of his bands is typically mean-reverting/counter-trend, which Kaufman's extraction calls "risky, especially when prices are volatile." Bollinger's own mitigation: confirm a downside penetration using other indicators (primarily volume- and market-breadth-based) before treating a band touch as a profit-taking or reversal trigger.

---

## 6. Trend-Break Exits

### The trendline-direction exit family (Kaufman Ch.8)
Kaufman's "three families of entry/exit rule" ranks trend-break exit signals by lag:
1. **Price-crossing (intraday)** — exits the moment price crosses the trendline intraday; most (and most whipsaw-prone) signals.
2. **Price-crossing (close-based)** — exits only on a close beyond the trendline; reduces signal count.
3. **High/Low/Close-average crossing** — uses (H+L)/2 or (H+L+C)/3 crossing the trendline.
4. **Trendline-direction signal** (lowest frequency, most lag) — exits only after the trendline's own direction itself turns. Benefit: far fewer false signals (higher win rate, lower cost); penalty: signal generated later than a price cross.

**Worked comparison (Table 8.2, 10 years of Amazon, five calculation periods)**: trendline-direction exits had 26%-37% fewer trades than price-penetration exits and, for the most part, better performance (Profit Factor) — better in all but the fastest (5-day) calculation period, where the lag becomes too costly relative to price-penetration timing. **General conclusion**: trendline-based exits suit longer-term trading; price-penetration suits shorter-term/day trading (Kaufman Ch.8, cross-ref §7 below).

### Techno-fundamental early exits (a discretionary override on a systematic trend-break rule, Kaufman Ch.8)
Kaufman documents an explicit hybrid approach for slow trend systems tracking fundamentally-driven trends (illustrated via the 1981-2015 U.S. interest-rate decline): a very slow trend (e.g., 200-day MA, ~100-day lag) can lag a genuine policy reversal significantly, giving back a large unrealized gain before the trendline itself signals the reversal. **Rationale for overriding the mechanical trend-break rule**: if the fundamental driver (e.g., government policy) visibly changes, the fundamental basis for the trend is over even before the trendline reverses — exiting on the policy-change signal rather than waiting for the mechanical trend-break is framed as a safer way to lock in profit and reduce market risk. **Explicit warning ("caveat emptor")**: this only works when a reliable government policy is genuinely driving the trend, and policy shifts are often clear only in hindsight (the source cites a 2010 case where an expected Fed policy change did not materialize, and bonds instead posted a strong upward trend into 2011's record-low yields). **Guidance given: wait for an actual statement of policy** before acting on this override. Kaufman names this hybrid approach **techno-fundamental trading**.

### Two-trendline exit constructions (Kaufman Ch.8)
Where a slower trendline sets the dominant trend direction and a faster trendline times entries/exits, three rule variants determine the trend-break exit behavior:
1. **Simple crossover (always in market)**: exit/reverse when the faster MA crosses the slower MA.
2. **Price-vs-both-MAs**: exit longs when price crosses below either MA (creates a flat/neutral zone rather than an immediate reversal).
3. **Both-trendlines-agree**: exit when the two trendlines conflict (requires mutual confirmation to remain in a position).
Exiting to flat (variants 2 and 3) rather than always reversing (variant 1) adds liquidity (smaller order size) and allows re-entering in the same direction on the next signal rather than a forced reversal.

### Elliott Wave Oscillator (EWO) trend-break exit (Kaufman Ch.14)
A clean, unambiguous mechanical stop condition contrasted with the otherwise highly subjective, interpretive nature of manual Elliott wave counting: **close any long position when EWO falls below zero** (Kaufman Ch.14).

### Moving-average sequence consistency checks before trusting a trend-break signal (Kaufman Ch.8)
Comparing the trend direction across a range of calculation periods (e.g., 1 through 18+ days) around the traded period reveals whether a new trend-break signal is reliable or spurious. **Rule of thumb**: an erratic short-end sequence (very short calc periods flipping direction easily on single-day data changes) should not be trusted as a real trend change — only a genuinely smooth, progressive sequence change across the range of calculation periods is considered reliable (Kaufman Ch.8).

### Time-in-market as an implicit trend-break-adjacent risk lever (Kaufman Ch.21, Ch.23)
Kaufman explicitly frames time-in-market reduction (achieved via profit-taking, multiple trend speeds, or a trend-break exit that goes flat rather than reversing) as "the only defense against price shocks," since shocks are by definition unpredictable — a 40%-in-market strategy avoids 60% of shocks by construction (Kaufman Ch.23, restated Ch.21).

---

## 7. Time Exits for Day Trading

Kaufman's Chapter 16 (Day Trading) documents time-based exits primarily as concrete rules embedded in specific named intraday systems rather than as a single generalized taxonomy, and states a general principle about holding-period floors for trend techniques.

### General holding-period guidance (Kaufman Ch.16)
> "Traditional trend-following technical analysis is generally not used for holding periods under 3 days, and probably not under 20 days — trends serve mainly as a directional filter for short-term trading."

For day trading specifically, both trend and fundamental analysis are described as serving only as filters, **except** trading the reaction to scheduled economic reports, which is treated as a legitimate day-trading strategy in its own right (cross-ref Ch.14 "Event Trading").

### Named systems with explicit time-based exit rules
- **Meyers' Adaptive Range Breakout** (intraday stock/stock-index): "**Close all trades 5 minutes before the close of trading**" — a hard session-end time exit regardless of P&L (Kaufman Ch.17, an intraday breakout system covered in the Adaptive Techniques chapter).
- **Walt Bressert's chart** (1970s intraday key-level system, Kaufman Ch.16): maps time-of-day + developing-range + previous-day-range combinations to specific buy/sell trigger levels that tighten as the day progresses. Worked example: at 30 minutes after the open, buy/sell triggers are set at the previous day's high/low; by midday the short-sale trigger tightens to today's low; **35 minutes before the close**, if price is between today's open and high, the buy trigger lowers to today's high and the short trigger lowers to today's open — a time-of-day-conditioned tightening of exit/entry logic rather than a single fixed clock-time exit.
- **Afternoon breakouts and midday reversals** (Kaufman Ch.16): a post-midday breakout still indicates likely directional continuation for the rest of the session, but with half the remaining time to profit — making an **overnight hold** important to capture the full potential move (i.e., the time-of-day at which a signal fires determines whether a same-day time exit or an overnight hold is the appropriate management choice).
- **TSM Flexible Intraday Breakout** (Companion-Website testing tool, Kaufman Ch.16): its configurable parameter set explicitly includes session start/end/last-entry times and an optional overnight-hold toggle — confirming time-of-day exit boundaries as a standard, tunable parameter class for this family of systems.
- **Outside Day with Outside Close (Arnold)** (Kaufman Ch.4): position closed on a fixed timed exit **3 days after entry** (tested range 1-5 days) regardless of whether the stop has been hit — a multi-day (not intraday) time exit, included here for completeness since it is one of the book's few purely time-triggered (non-price-conditional) exits.

### Rationale for time-based exits around scheduled news (Kaufman Ch.14)
Stop orders placed around a scheduled news event are explicitly criticized as unsafe: a surprise report can cause price to jump past a resting stop and fill at a price "you will later regret." The chapter's recommendation is to **exit positions ahead of scheduled reports** rather than relying on stops to manage the event-day gap risk — a time-based (calendar-scheduled) exit trigger used specifically as a substitute for a price-based stop in known-event windows. **Unables** (missed fills when price has already jumped past an intended entry/exit around such releases) are documented as a **one-sided risk**: skipping the trade removes upside without removing downside, meaning live performance will structurally underperform a backtest using idealized fills around events like the API energy stocks report (Tuesday 10:30am ET), FOMC announcements (2:15pm ET), and similar scheduled releases (Kaufman Ch.16).

### No explicit generalized "time stop" taxonomy entry in Ch.23
It is worth noting explicitly: Kaufman's Chapter 23 stop-loss taxonomy (§1 above) does **not** include a distinct "time-based stop" as one of its 5 numbered adaptive stop-placement methods or its 3 trailing-stop constructions — time exits appear only as system-specific rules scattered across Ch.4, Ch.16, and Ch.17, not as a named category alongside money/volatility/chart stops in the book's own central risk chapter. This is flagged here as a structural observation about the source, not an inferred claim.

---

## 8. Pardo's Exit Design and Trade Management

### The three principal components of a strategy (Pardo Ch.5)
Pardo frames exit design as one of three universal components of any strategy: (1) entry and exit, (2) risk management, (3) position sizing. Definitions given:
- **Exit rule**: "closes out a current long or short position." Can only occur from an open position.
- **Reversal rule**: "closes out a position and initiates a new and opposite position" in one action.
- Strategies can be **symmetrical** (buy/sell/exit conditions mirror each other) or **asymmetrical** (unrelated entry vs. exit logic — Pardo's own example: a 5-day-high breakout entry paired with a 5-day/20-day MA-cross exit).
- A strategy can be **reversing** (always in the market, flips position on new signal) or **nonreversing** (exits to flat, waits for a fresh signal to re-enter) — directly paralleling Kaufman's reversal-vs.-flat distinction in §6 above, though the two books use different terminology for the same underlying design choice.

### The Management of Profit — Pardo's two mechanisms (Pardo Ch.5)
Trailing stops and profit targets, both given full definitions and worked numeric examples reproduced in §1 (dollar variants) and §4 (volatility variants) above. Pardo's summary trade-off, restated here for completeness: trailing stops preserve a "predetermined proportion of open trade profit" and never retreat once advanced; profit targets are an "unconditional exit... at some predetermined price or profit level," which locks gains immediately but caps upside.

### Overnight-gap risk as a cross-cutting caveat on ALL of Pardo's exit constructions (Pardo Ch.5)
Every stop and target type Pardo defines (risk stop, trailing stop, profit target) carries the same explicit caveat: a GTC (good-till-cancelled) order can only fill at the next tradable price, so a large adverse overnight gap can blow through a stop by many multiples of its intended distance, or (favorably, for a profit target) fill at a better price than the nominal target if the gap runs through it in the trader's favor. Worked example: a 2.00-point risk stop exceeded by a 10.00-point adverse open results in a fill 8.00 points worse than intended.

### Strategy-level and portfolio-level exit-adjacent risk controls (Pardo Ch.5, Ch.12, Ch.14)
Beyond the single-trade exit, Pardo defines a **strategy stop** — the point at which trading of an entire strategy is abandoned, not just a single trade:
- **Strategy stop formula**: `Strategy Stop = Maximum Drawdown (MDD) × Safety Factor`. Example: MDD $40,000, safety factor 1.5 → $60,000.
- **Required Capital formula (basic)**: `RC = Margin + (MDD × Safety Factor)`. Example: MDD $40,000, safety factor 1.5, margin $15,000 → RC = $75,000.
- A worked stress-test shows this basic formula can still be insufficient against **back-to-back drawdowns**: an account capitalized at $75,000 can be wiped out by a $50,000 drawdown, a partial +$15,000 recovery, then another $40,000 drawdown. Pardo's proposed remedy is a more conservative formula: `RC = Margin + (MDD × Safety Factor × 2)`, e.g., ((40,000×1.5)×2)+15,000 = $135,000 — shown to survive the same two-hit stress scenario with $60,000 remaining.

### The Strategy Stop-Loss (SSL) — Pardo's live-trading exit-from-trading-a-strategy-altogether rule (Pardo Ch.14)
This is Pardo's dedicated framework for deciding **when to stop trading a live strategy entirely** — an exit at the strategy level, distinct from any single-trade exit:
- **Basic formula**: `SSL = MDD × Drawdown Safety Factor`. Example: MDD $5,000, DSF 2 → SSL $10,000.
- **Combined formula**: `Required Capital = Margin + (MDD × Safety Factor)`. Example: margin $5,000, MDD $6,000, factor 3 → RC = $23,000.
- **SSL-as-%-of-capital formula**: `Required Capital = SSL / Capital Loss %`. Example: SSL = $6,000×3 = $18,000; if this should represent a 40% max-loss threshold → RC = $18,000/40% = $45,000.
- **Two usage philosophies, both presented as legitimate (explicit)**: (a) a strict mechanical stop — trading halts the instant the SSL is reached/exceeded, no exceptions; (b) a heightened-vigilance qualitative trigger — assess whether the equity curve looks like it's "in free fall" (stop early) or "finding support" (allow some extra latitude even slightly past the nominal SSL).
- **Statistical monitoring guideline**: "If statistics in the trade profile are less than 50 percent or more than 150 percent of the corresponding evaluation profile statistic, whether profitable or not, then a rational explanation must be found." Drawdown must be constantly monitored against both the SSL and the evaluation profile.

### Trade-profile comparison as an implicit exit-timing discipline (Pardo Ch.14)
Pardo gives a worked contrast illustrating how the SSL/evaluation-profile framework should be applied in practice: (a) real-time producing 9 consecutive losses totaling $10,000 under similar volatility to the backtest — this exceeds both the dollar and trade-count expected bounds by a wide margin and is judged a likely genuine strategy failure warranting suspension; (b) real-time producing 3 losses totaling $8,000 (same trade-count as expected) but under volatility roughly double the evaluation baseline — judged "unpleasant, but not an entirely unexpected performance," because loss size alone, without controlling for volatility regime, can be a misleading comparison (Pardo Ch.14). This is presented as a direct decision procedure for whether an observed live drawdown should trigger the SSL exit or be tolerated as normal variance.

### Position sizing as exit-adjacent risk control (Pardo Ch.5)
Four named position-sizing methods are given (volatility-adjusted sizing, Martingale, Anti-Martingale, Kelly/Optimal f — full formulas and worked examples in `10_position_sizing.md` §2.4 and §4.3), and Pardo's own **scaling-out** definition is directly exit-relevant: "incrementally decreases an existing position" as it moves favorably — e.g., remove 1 unit per additional $1,000 of open profit gained, contrasted with **scaling in** (add 1 unit per $1,000 of open profit gained). A combined example: scale in +1 unit per $1,000 gained up to a $5,000 cap on the oldest lot, then scale out −1 unit per additional $1,000 gained thereafter (Pardo Ch.5). **Explicit note on who uses this**: Pardo states scaling in/out is more commonly a discretionary trader's technique, but is equally implementable in an automated, mechanical strategy (Pardo Ch.5) — a nuance worth preserving since it distinguishes this from the purely-mechanical stop/target constructions documented elsewhere in this file.

---

## 9. Exit-vs-Entry Asymmetry

This theme recurs across all three books that address it in depth (Kaufman, Pardo, Chan), though each frames the asymmetry differently, and the framings are presented separately here rather than merged.

### Kaufman: asymmetric attention and asymmetric signal reliability
- **Entry uncertainty is structurally higher than exit certainty for trend systems**: "entry timing is the point of greatest uncertainty" for trend systems — lag in the trend calculation can trigger a buy on a day prices actually drop (or vice versa), and most trend systems have a low win rate, so the chance of an initial loss is high (Kaufman Ch.23). By contrast, **breakout strategies start each trade at high risk by construction** (risk = the calculation period's full high-low range) — a different asymmetry: breakout entries carry known, quantifiable risk at inception, while trend-crossover entries carry unknown, lag-dependent risk.
- **Mean-reversion systems invert this asymmetry**: they have a higher win rate but "take larger risks" because they buy into falling prices / sell into rising prices, betting moves are overextended and unsustainable (Kaufman Ch.23) — i.e., for mean reversion the *entry* is the source of asymmetric tail risk (a strong sustained trend can keep price outside a mean-reversion channel for weeks), while for trend-following the *exit* (holding through the full move) is the source of the asymmetric payoff.
- **Timing asymmetry between stops and profit-taking, explicitly recommended (Kaufman Ch.23)**: for intraday systems, a triggered stop should wait for the close (allowing a noise-driven pullback to potentially save the trade), while profit-taking should exit at the intraday spike rather than waiting for the close — the two exit types are deliberately timed asymmetrically relative to each other, even within the same system.
- **The entering-sooner vs. entering-later asymmetry** (Kaufman Ch.23, "Waiting for a Better Price" and momentum-filtered entry tests): empirical tests (Table 23.9, Table 23.10) found that adding a wait/pullback filter to entries generally improved profit factor, % winning trades, and average profit per trade, even in markets the author expected to be poor candidates (Apple, Amazon) — but delaying entry from a signal close to the next open, tested separately (Kaufman Ch.8), *reduced* overall total profits despite improving the average entry price 75% of the time, because fast breakouts that never retrace are missed entirely. This is flagged as a direct empirical tension: patience helps some entry-timing designs and hurts others, with no single rule given.
- **Exit design for trend systems must specifically preserve entry-side risk tolerance**: since a trend system's entire profitability rests on capturing a fat right tail from a small number of large winners against many small losers (§5), any exit-side addition (a stop or profit target) that is not carefully matched to this asymmetric distribution risks inverting it. This is the book's single most repeated instance of exit design being asymmetrically more consequential than entry design for trend systems specifically — Kaufman's Ch.8 ranking states the calculation-period choice (which shapes both entry lag and exit lag together) is "the most important decision in the ultimate success of the trading system," more important than entry rules, profit-taking, or volatility filters individually.

### Pardo: entry and exit as formally distinct but structurally parallel rule types, with asymmetric fill risk
- Pardo's formal definitions draw a clean structural line: an **entry rule** "initiates a new long or short position" and can only occur when flat; an **exit rule** "closes out a current long or short position" and can only occur from an open position (Pardo Ch.5) — the two rule types are mechanically asymmetric by construction (mutually exclusive preconditions), regardless of strategy design philosophy.
- **Fill-risk asymmetry between stop and target orders**: a risk stop, once touched, executes as a market order (subject to slippage, but reliably fills); a profit-target limit order carries a **distinct, opposite risk of never filling at all** — up to 30% of limit orders, per the Kaufman estimate cited by Pardo, go unfilled (Pardo Ch.5). This means the two "management of profit" tools carry structurally different execution-risk profiles even when calibrated to the same dollar/volatility distance.
- **Gap risk is directionally asymmetric depending on order type**: an adverse overnight gap harms a resting stop (fills far worse than intended) but a *favorable* overnight gap-through helps a resting profit target (fills at a better price than the nominal target, adding extra realized profit) — the same market event (a large overnight gap) has opposite consequences depending on whether it is evaluated against an exit-side stop or an exit-side target (Pardo Ch.5).
- **Strategy-type asymmetry in what benefits from profit targets**: Pardo's general (explicitly non-universal) guidance is that active/countertrend strategies from overbought/oversold conditions benefit most from profit targets, while slower trend-following strategies benefit least — an asymmetry in which exit tool suits which entry philosophy, directly paralleling Kaufman's strategy-type/tool-fit rule in §1 despite being independently stated.

### Chan: the regime-dependent asymmetry of whether an exit tool helps or hurts at all
As detailed fully in §1, Chan's "Is Stop Loss Good Risk Management?" section presents the sharpest asymmetry claim in this file's source set: the *same* stop-loss exit mechanism is described as **beneficial in a momentum/trending regime and actively harmful in a mean-reverting regime** — not merely more or less useful, but sign-reversing in its effect on expected outcome depending on the believed cause of the price move (Chan Ch.6). This is a different kind of asymmetry from Kaufman's and Pardo's (which concern differential fill/timing/tool-fit), since Chan's claim is about the causal *direction* of the exit tool's effect on P&L, not just its magnitude or reliability.

### A structural observation not explicitly stated by any single source, but implied across all three
No single book explicitly states a unified "exits are harder than entries" or "entries are harder than exits" conclusion — Kaufman's material leans toward exits (particularly avoiding the temptation to cut winners short) being the more consequential design decision for trend systems specifically, while Pardo's material treats entry and exit as formally symmetric-but-mechanically-exclusive rule types whose main asymmetry is in execution risk (fill risk, gap risk) rather than design difficulty, and Chan's material locates the asymmetry in regime uncertainty rather than in entry vs. exit at all. This divergence across sources is preserved here explicitly rather than resolved into a single synthesized claim, per the traceability and non-merging rules governing this file.

---

## Summary Table: Stop/Profit-Tool Fit by Strategy Type (Kaufman Ch.23, restated as the file's most load-bearing single rule)

| Tool | Works well for | Works poorly for |
|---|---|---|
| Stop-loss | Trending systems in trending markets | Non-trending markets or mean-reversion systems |
| Profit-taking | Mean-reversion/short-term strategies | Trending markets or long-term trend strategies |

Pardo's independent, non-cross-referenced guidance in Ch.5 ("active/countertrend strategies... benefit most [from profit targets]... slower trend-following strategies benefit least") is consistent with this table without either book citing the other.

---

## Explicitly Flagged Gaps in Source Coverage

1. **"Chandelier Exit" as a named technique does not appear anywhere in the Kaufman extraction** (confirmed by full-book search). The task's expectation that this material sits in Kaufman Ch.17 is not borne out by the source; the closest available material is Wilder's Parabolic SAR (§3), which is structurally similar (a volatility/range-derived trailing offset from the extreme favorable price) but is not the same named construction.
2. **Kase's DevStop multiplier mapping is internally ambiguous across the two places it appears in Kaufman** (Ch.18's indicator entry gives three fixed multiples 1.0/2.2/3.6 for three tiered stop levels; Ch.23's procedure gives two multiplier *ranges* — 2.06-2.25 and 3.20-3.50 — for a single stop, with the source's own mapping of which range applies left unrecoverable). Both are preserved verbatim in §2 without being reconciled.
3. **Kaufman's own Ch.23 stop-loss taxonomy has no distinct "time-based stop" category** alongside its money/volatility/chart entries — time exits exist only as scattered system-specific rules (§7). This may reflect a genuine gap in the source's own organizational treatment, not an extraction failure.
4. **Several formula gaps within the Kase DevStop, ATR-target, and Bollinger-band constructions are embedded-graphic gaps in the original Kaufman PDF** (e.g., the exact "first stop" combining arithmetic for DevStop, the exact Modified Bollinger Band center-line/band formulas) — flagged in the original extraction and preserved as flagged here rather than reconstructed.
5. **Hilpisch's book documents broker-API support for stop-loss/trailing-stop/take-profit order parameters but never demonstrates their use in any worked strategy** — every example relies solely on signal-reversal exits. This is a genuine gap in that book's own coverage of exit techniques, not merely thin material to summarize.
6. **Vince's book contains essentially no exit-technique material** — it is a position-sizing and risk-of-ruin framework (Kelly/Optimal f, drawdown dilution via fractional f, portfolio-level leverage) and does not address stop-loss placement, profit-taking, or trade-management mechanics at all. It is cited in this file only tangentially (via its foundational axiom that no money-management scheme rescues a negative-expectation game, relevant background to §9's asymmetry discussion) but contributes no exit-specific content.
7. **Trend-break exits are well documented for slow/trend systems (Ch.8) but the Chapter 17 material the task specifically flagged as a likely source for Chandelier/parabolic content is, per confirmed search, Parabolic-SAR-only** — no separate "chandelier" trend-break exit construction exists in that chapter beyond what is captured in §3.
