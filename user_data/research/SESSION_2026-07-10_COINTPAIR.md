# Session 2026-07-10 — H-CointPair: formal BTC-ETH cointegration pairs trading

Pre-registered, single-shot, pre-gated experiment. Assignment: `research/NEXT_TASK.md`
(2026-07-10, Research Director cycle #6). Script: `phase18_cointpair.py`.
This is the last untested, structurally new, data-reachable mechanism in the hypothesis
bank (`knowledge_base/hypothesis_bank.md`, "BTC-ETH Cointegration Pairs Trading").
The two pre-gates cost ZERO n_trials; only if BOTH pass does the single pre-registered
construction run as **trial #98**. Otherwise n_trials stays at **97** and the
pairs/relative-value direction is closed.

## 1. Pre-registration block (LOCKED before any statistic was computed)

Written and saved BEFORE `phase18_cointpair.py` was written or executed, and before any
stationarity test, hedge ratio, half-life, or census number existed. Everything below
the end marker was filled in afterwards.

### Hypothesis

BTC and ETH log prices are cointegrated: a fitted linear combination (hedge-ratio
spread) is mean-reverting with a tradeable half-life, and a dollar-neutral two-leg
position taken at spread extremes earns positive expectancy after realistic two-leg
fees — in chop/range regimes where the champion (TrendVolTarget) is weakest.

### Why this is NOT a repeat of the rejected ETH/BTC z-score fade (#13, TEST Sharpe −1.45)

The z-fade used a raw 1:1 price ratio, an arbitrary z-window, no stationarity test, no
hedge ratio, and no reversion-timescale estimate — it bet on mean reversion without
first establishing that a mean-reverting object exists. This assignment INVERTS that
order: the statistical object (stationary spread, fitted hedge ratio, measured OU
half-life) must be demonstrated BEFORE any trading rule is evaluated; if it does not
exist, no rule is ever tested. Chan's KO/PEP warning (correlation ≠ cointegration;
KO/PEP correlate 0.4849 yet fail CADF) is precisely this distinction (Chan Ch.7;
Kaufman Ch.13; `knowledge_base/03_mean_reversion.md`).

### Distinction from the H-BearShort closure (required paragraph)

The H-BearShort closure (2026-07-10, iteration 12) applies to *directional* shorting of
trend regimes with a lagging confirmation gate — it documented that crypto bear price
action (crash-then-squeeze) punishes lagging directional shorts. A market-neutral
spread short leg is a different claim: the short leg is hedged by an equal-dollar long
leg, so the position's P&L depends on RELATIVE BTC-ETH pricing, not on market
direction. The BearShort closure therefore does not cover this construction. It is,
however, honestly noted that violent common crashes where both legs gap and the spread
widens (Kaufman's 2008 S&P/NASDAQ pairs failure mode) remain a named risk for this
construction — that risk is regime-break risk, not directional-lag risk.

### Data (pre-declared)

- **Harness window (primary)**: OKX futures 1d feathers, BTC and ETH, inner join on
  common dates. BTC futures start 2020-01-01, ETH futures 2020-10-01 → common window
  ≈ 2020-10-01 → 2026-05-27 (~2,065 bars). All trial statistics and the trial itself
  (if reached) use this window (short leg must be realistic → futures).
- **Secondary longer window (spot, reporting + regime coverage)**: OKX spot 1d
  feathers. **Honest data note recorded up front**: the assignment hoped for
  ~2017-18 spot coverage; the actual earliest COMMON BTC+ETH spot coverage in this
  environment is 2019-12-01 (ETH spot feather starts then; BTC alone reaches back to
  2018-01-11). The secondary window is therefore 2019-12-01 → 2026-05-25 (~2,360
  bars), which adds the pre-COVID regime and the March-2020 crash to the census but
  does NOT reach the 2018 bear. This limitation is reported, not hidden.
- Daily log closes throughout. No other timeframe, no other assets.

### Pre-declared statistical constructions

- **Hedge ratio (strictly causal)**: rolling OLS of log(ETH) on log(BTC), window
  **365 completed bars**, refit every bar, coefficients shifted 1 bar so the value
  used at bar t is fitted on bars t−366 … t−1 only. Causal spread:
  `z_raw[t] = log(ETH[t]) − α[t] − β[t]·log(BTC[t])`.
  Primary normalization direction: ETH regressed on BTC (BTC is the dominant/driver
  asset). Both normalization directions are still tested in the EG census.
- **Full-window (non-causal, DIAGNOSTIC ONLY) spread**: single OLS over the whole
  window — used ONLY inside the stationarity tests of pre-gate 1 (that is what
  EG/CADF is), never for any trading decision. The census (pre-gate 2) and the trial
  (if reached) use exclusively the causal spread. This is the look-ahead firewall.
- **OU half-life**: on the causal spread over the harness window, regress
  Δz[t] on (z[t−1] − mean(z)) → θ = −slope, HL = ln(2)/θ. If slope ≥ 0, HL = ∞
  (automatic band failure). Reported for the full-window-fit spread too (diagnostic).
- **z-score (causal)**: `z[t] = (z_raw[t] − μ_L[t]) / σ_L[t]` with μ_L, σ_L rolling
  over **L_z** bars, shifted 1 bar (only completed bars). **Formula, pre-declared**:
  `L_z = clip(round(3 × HL_causal), 20, 180)` bars. No other window will be examined.

### Pre-gate 1 — stationarity / cointegration census (zero n_trials)

Tests, all pre-declared:

1. Engle-Granger (`statsmodels coint`, trend='c', autolag='aic') on the full harness
   window, BOTH normalization directions (ETH~BTC and BTC~ETH).
2. Johansen (`coint_johansen`, det_order=0, k_ar_diff=1) on the full harness window:
   trace statistic for r=0 vs its 95% critical value.
3. Rolling EG: windows of **730 bars**, stepped **91 bars**, across the harness
   window; a window PASSES if EG p < 0.05 in EITHER direction.
4. Same battery (1-3) on the secondary spot window, REPORTING ONLY (more regimes,
   more honest; does not enter the stop rule).
5. Post-2024 sub-window check: EG both directions on 2024-01-01 → end of harness
   window. If min p ≥ 0.05 → **regime-break flag** must be reported even if the full
   window passes.
6. OU half-life of the causal spread (harness window).

**STOP RULE (exact, declared now)**: pre-gate 1 FAILS unless ALL of:

- (1a) Full harness window: EG p < 0.05 in at least one direction, AND
- (1b) Johansen trace statistic for r=0 > its 95% critical value, AND
- (1c) ≥ 60% of rolling 730-bar windows pass (EG p < 0.05, either direction) —
  "clear majority" per the assignment, quantified as 60%, AND
- (1d) OU half-life of the causal spread in **[3, 60] days** (too fast is fee-eaten
  at daily bars; too slow is indistinguishable from drift on this sample).

If pre-gate 1 fails → STOP. Zero trials spent. Direction closed.

### Pre-gate 2 — fee-hurdle amplitude census (zero n_trials; only if pre-gate 1 passes)

On the CAUSAL spread z-score (window L_z as declared above), census all excursion
episodes over the harness window:

- **Episode definition**: entry at the first bar t where |z| crosses from ≤2 to >2;
  direction s = −sign(z[t]) applied to the ETH leg (s=+1: long ETH / short BTC).
  Exit at the first bar u > t where |z[u]| < 0.5, or time-stop at
  `ceil(3 × HL_causal)` bars after entry, whichever first.
- **Execution reference (census convention, same as the H-BearShort census)**: 1-bar
  lag — entry priced at close[t+1], exit at close[u+1]. Conservative relative to the
  harness's 2-bar convention.
- **Position (dollar-neutral, per assignment)**: $1 long one asset, $1 short the
  other (2× gross notional). Per-episode gross capture = Σ over held bars of
  `s·(r_ETH − r_BTC)` (compounded), in return terms on the $1-per-leg convention.
- **Fee hurdle**: round trip = 4 legs × 0.15%/leg = **0.60%** on the same $1-per-leg
  convention. The established 0.15%/side figure already bundles fee + slippage
  (validator.py: 0.10% commission + 0.05% slippage; phase13-16 convention).

**STOP RULE (exact, declared now)**: pre-gate 2 FAILS unless ALL of:

- (2a) Median per-episode gross capture ≥ **1.80%** (= 3 × 0.60% round-trip cost), AND
- (2b) Episode count over the harness window ≥ **40**, AND
- (2c) Aggregate gross across all episodes minus (0.60% × episode count) > 0.

If pre-gate 2 fails → STOP. Zero trials spent. Direction closed.

### The trial (ONLY if both pre-gates pass — this and only this consumes trial #98)

ONE pre-registered construction, all numbers already fixed above or derived by the
declared formulas — no sweeps, no variants:

- Dollar-neutral spread position, causal hedge ratio (365d rolling OLS as declared):
  weights ±0.5/∓0.5 of equity on ETH/BTC futures (implementable without leverage;
  exactly half the census's $1-per-leg convention — scale-invariant for Sharpe).
- z lookback L_z (formula above). Entry |z| > 2; exit |z| < 0.5 or time-stop
  ceil(3×HL); hard stop if |z| > 4 (spread blowout = regime-break protection),
  after which flat until |z| re-enters the |z| < 2 band.
- 2-bar signal lag, fees 0.15%/side per leg (turnover accounting: entry = 1.0 total
  turnover at 0.5/leg), futures closes.
- Validation: 70-15-15 split judged on TEST (if TEST episodes < 10 →
  INCONCLUSIVE-BY-SAMPLE, not a pass); `wf_window_stability` at 3/4/5/6 windows;
  Monte Carlo 1,000 monthly-block sims, seed 11, reporting P(Sharpe<0) and
  P(DD<−25%) vs champion context; DSR at n_trials=98 via `freqtrade_dsr.py`;
  `family_context` populated from the results dir; daily-return correlation with the
  same-session recomputed champion stream (bar: < 0.4, the portfolio-slot criterion).
- Look-ahead audit: hedge ratio (365d OLS, shift 1), μ_L/σ_L (rolling L_z, shift 1),
  HL (measured once on the causal spread, used only as a time-stop/lookback constant
  derived from pre-gate statistics), signal execution shift(2). No full-sample
  statistic feeds any trading decision.

### Promotion criteria (pre-declared)

- Candidate competes ONLY for portfolio slot 3 (structurally different mechanism,
  corr < 0.4, full gate stack, positive TEST standalone). It does NOT compete with
  TrendVolTarget for champion. `best_strategy_so_far.py` is NOT replaced under any
  outcome. DSR ≥ 0.95 remains the bar for "real edge"; passing everything except DSR
  = candidate sleeve pending forward evidence, Director decision, not automatic.

### Budget

Maximum backtested constructions: **1**. n_trials 97 → 98 ONLY if both pre-gates pass
and the trial runs. Zero parameter optimization: no sweeps of entry z, exit z,
lookbacks, or hedge windows. If a result is close to a bar and a variation "would
probably pass," it goes into "ideas parked" and the session STOPS.

**— END OF PRE-REGISTRATION BLOCK —**

---

# RESULTS (filled in after the pre-registration block was locked)

## 2. Outcome summary

**STOPPED AT PRE-GATE 1 (stationarity/cointegration census). Trial #98 was NEVER
RUN. Pre-gate 2 was never reached. Zero n_trials spent — the cumulative trial count
stays at 97.**

Three of the four pre-declared stop-rule conditions FAILED, and the pre-declared
post-2024 regime-break flag was RAISED. There is no demonstrated mean-reverting
object between BTC and ETH on this data; per the locked protocol, no trading rule
was ever evaluated. This is the third consecutive pre-registered experiment stopped
by a zero-cost gate (H-RangeVol EWMA sanity gate; H-BearShort whipsaw census; now
H-CointPair stationarity census).

Scripts: `phase18_cointpair.py` (the full pre-registered pipeline; exits at the
pre-gate — reproducible end to end, exit code 1 with the stop-rule message) and
`phase18_diag_spread_drift.py` (descriptive drift diagnostic only — no strategy
returns computed anywhere this session).

## 3. Pre-gate 1 — census results (FAIL on 3 of 4 conditions)

Harness window: BTC+ETH futures inner join, 2020-10-01 → 2026-05-27 (2,065 bars).
Secondary spot window: 2019-12-01 → 2026-05-25 (2,368 bars; the pre-registered
honesty note stands — common spot coverage begins 2019-12, so the 2018 bear was
unreachable, less regime coverage than the assignment hoped).

| Stop-rule condition (pre-declared) | Result | Value |
|---|---|---|
| (1a) Full-window EG p < 0.05, either direction | **FAIL** | p(ETH~BTC) 0.1269, p(BTC~ETH) 0.8456 |
| (1b) Johansen trace(r=0) > 95% cv | PASS | 25.99 vs 15.49 |
| (1c) ≥ 60% of rolling 730-bar/91-step windows EG p<0.05 | **FAIL** | 3/15 = 20% |
| (1d) Causal-spread OU half-life in [3, 60] days | **FAIL** | 79.6 days |
| Post-2024 sub-window EG (flag, not a condition) | **FLAG RAISED** | p 0.7039 / 0.5528 (878 bars) |

Supporting census detail:

- **Rolling EG**: the only passing windows are 2021-04→2023-03 (p 0.001),
  2022-03→2024-03 (p 0.008), 2022-06→2024-06 (p 0.002) — all three lie inside the
  2021-04→2024-06 span (and even within it they are not contiguous: the 2021-07,
  2021-09, 2021-12 windows fail). Every window ending after mid-2024 fails badly
  (best p among the last four windows: 0.52). The relationship did not merely
  weaken; it left.
- **Causal hedge ratio** (365d rolling OLS, shift 1): β wandered across
  [0.01, 2.13] over the window (last value 1.19) — a stable cointegrating relation
  would hold a roughly constant β; this range is itself evidence of structural
  instability.
- **Full-window-fit spread half-life (diagnostic)**: 125.5 days — even with the
  look-ahead advantage of a full-sample hedge fit, the "reversion" is a
  four-month timescale, indistinguishable from drift on a 5.6-year sample.
- **Secondary spot window (reporting)**: worse on every measure — EG p 0.64/0.90,
  Johansen trace 10.42 < 15.49 (fails even the one test the futures window
  passed), rolling 3/19 windows pass. The longer window does not rescue the
  hypothesis; it strengthens the rejection.

### Why Johansen (1b) passed while everything else failed

The Johansen trace test rejects "no cointegrating vector exists" at 95% on the
full futures window, but the object it certifies reverts with a ~126-day
half-life around a relationship whose fitted hedge ratio is unstable year to
year. A statistically detectable long-run relation that reverts on a 4-month
timescale with a drifting β is not a tradeable spread at daily bars with 0.60%
round-trip costs — which is exactly why the pre-registered stop rule required all
four conditions jointly rather than any single test. One test passing out of four
is what a borderline/spurious relation looks like, not a robust one.

## 4. Drift diagnostic (descriptive only — documents WHY the census failed)

`phase18_diag_spread_drift.py`, ETH/BTC log ratio on the futures window:

| Year | ETH vs BTC relative move |
|---|---|
| 2020 (from Oct) | −23.4% |
| 2021 | +220.2% |
| 2022 | −8.3% |
| 2023 | −25.3% |
| 2024 | **−33.0%** |
| 2025 | −4.5% |
| 2026 (to May) | −19.6% |

- Net over the window: ETH lost 18% against BTC — but through one +220% year
  followed by five consecutive down years. That is a trending, regime-shifting
  relative price, not oscillation around an equilibrium.
- ADF on the causal spread: pre-2024 p = 0.073 (marginal, not even then < 0.05),
  post-2024 p = **0.405** (unambiguous unit root). The assignment's stated failure
  mode (b) — "persistent post-2024 structural drift (ETF-era BTC dominance) that
  may have broken any earlier cointegration" — is precisely what the data shows,
  with the added finding that even the pre-2024 period was only marginal.

## 5. Verdict per pre-registered criteria

| Item | Result |
|---|---|
| Pre-gate 1 (stationarity census) | **FAIL (3 of 4 conditions) → STOP** |
| Post-2024 regime-break flag | RAISED |
| Pre-gate 2 (fee-hurdle amplitude census) | NOT REACHED |
| Trial #98 (pre-registered construction) | NOT RUN |
| Promotion / portfolio-slot evaluation | NOT EVALUATED |
| n_trials | **UNCHANGED at 97** |
| Champion / best_strategy_so_far.py | UNTOUCHED |

**H-CointPair is REJECTED at the statistical-object level.** The hypothesis's own
first clause — "BTC and ETH log prices are cointegrated" — is contradicted by the
census on both available windows. The z-fade-vs-cointegration inversion did its
job: by demanding the mean-reverting object be demonstrated before any rule was
written, the project closed this direction for zero selection cost instead of
discovering the same drift through another failed backtest (as #13's z-fade did,
TEST Sharpe −1.45, for one full trial's cost).

Per NEXT_TASK: **the pairs/relative-value direction is now CLOSED alongside
short/TSMOM. This was the last untested structural OHLCV mechanism — the
structural map of this dataset is closed.** Any future spread hypothesis must
first present evidence that the BTC-ETH (or other pair) relationship has
re-stabilized (e.g., a future rolling-EG census passing again on live data), not
re-run this census on the same window.

## 6. Required distinction paragraphs (per assignment)

**vs the rejected z-fade (#13)**: the z-fade traded first and asked questions
never; this session asked first and consequently never traded. Both now agree
from opposite directions: there is no exploitable BTC-ETH relative-value
reversion on this data — #13 showed the trade loses, #18 shows the statistical
premise (a stationary spread) does not hold, and adds the sharper structural fact
that the relationship's stationarity pocket (2021-24) has since dissolved.

**vs the H-BearShort closure**: that closure covered directional shorting of trend
regimes with a lagging gate (crash-then-squeeze punishes lag). This closure is
independent and different in kind: it is not about lag or direction at all — the
hedged object this strategy needed simply does not exist as a stationary series.
The two closures together now cover both remaining "second edge from OHLCV"
archetypes: directional harvesting of the champion's off-regime, and
market-neutral relative value.

## 7. Lessons

1. **Correlation ≠ cointegration, confirmed on this project's own core pair.**
   BTC-ETH daily returns are highly correlated (ρ≈0.8, long noted in
   strategy_research_notes), yet the pair fails formal cointegration on every
   window tested. Chan's KO/PEP warning replicates exactly on crypto's two most
   liquid assets.
2. **The ETF-era regime break is now formally documented, not just suspected.**
   Post-2024 the ETH-BTC relationship is a unit-root drift (ADF p 0.40; five
   consecutive ETH-losing years save 2021). Anything premised on BTC-ETH
   relative-pricing equilibrium — rotation, dominance, spread, ratio-fade — is
   statistically groundless on current data. This retroactively explains #13's
   failure mechanism.
3. **A single passing test out of a battery is a warning, not a signal.** Johansen
   said yes; EG (both directions), the rolling census, the half-life band, and
   the sub-window check all said no. Requiring joint passage in the
   pre-registered stop rule is what kept the one positive result from becoming a
   rationalization to proceed.
4. **The pre-gate discipline is now 3-for-3** (EWMA sanity gate, BearShort whipsaw
   census, CointPair stationarity census): three consecutive doomed trials
   stopped at zero selection cost. The census numbers are the deliverable.
5. **The structural map of this dataset is closed.** Every OHLCV-reachable
   mechanism class (signal prediction, sizing refinement, directional short,
   market-neutral relative value) is now tested-and-rejected or closed at
   pre-gate. The standing conclusion of strategy_portfolio.md is upgraded from
   "will most likely require a new data axis" to "requires a new data axis or
   forward evidence, full stop."

## 8. Ideas parked (NOT tested, recorded per protocol)

- A regime-gated pairs construction (trade the spread only inside windows where a
  trailing rolling-EG test currently passes) would have been the obvious next
  variation — parked, because it is a second-order construction on a first-order
  relationship that currently does not exist, and the 2021-24 stationarity pocket
  is a single episode (n=1 regime) — any backtest of it would be one long
  in-sample fit. Revisit only if live/forward data re-establishes a passing
  rolling census for a sustained period.
- Cross-exchange or spot-perp same-asset spreads are the only other formally
  cointegrated-by-construction candidates, but the spot-perp basis was already
  measured as pure noise on OKX (#5) and cross-exchange data is a blocked axis.

