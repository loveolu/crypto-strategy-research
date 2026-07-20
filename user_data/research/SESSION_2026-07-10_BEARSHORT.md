# Session 2026-07-10 — H-BearShort: mirror-image trend gate as a short sleeve

Pre-registered experiment, **trial #98** in the project's cumulative DSR ledger.
Script: `phase16_bearshort.py`. Assignment: `research/NEXT_TASK.md` (2026-07-10
Research Director cycle #2, post-H-RangeVol). This is the first candidate for
`strategy_portfolio.md`'s second slot: a short sleeve active when the champion is
flat by design.

## 1. Pre-registration block (LOCKED before any results were produced)

Written and committed to this file before the pre-gates, baseline replication, or
the sleeve trial were run. Everything below this block's end marker was filled in
afterwards.

### Hypothesis

The champion (TrendVolTarget) detects bull regimes via a 3-of-3 gate
(close>SMA200 AND ROC30>0 AND EMA20>EMA50) and sizes positions with vol-target
sizing. It is flat through bear markets by design — this is its edge mechanism
(regime avoidance). The directional short side of this exact mechanism has never
been tested in 97 constructs.

**H-BearShort: a short sleeve gated on the mirrored 3-of-3 condition
(close<SMA200 AND ROC30<0 AND EMA20<EMA50), vol-target sized identically to the
champion, produces (a) a positive standalone return stream concentrated in bear
regimes, and (b) when run alongside the champion, a combined portfolio with
equal-or-better Sharpe and a thinner drawdown tail than the champion alone.**

The pre-registered primary prediction is (b) — the portfolio-level improvement —
because that is the decision this trial informs (does the project gain a second
portfolio slot?). Standalone sleeve profitability is necessary but not sufficient.

### Scientific rationale

1. The champion's edge is regime detection: its 3-of-3 gate reliably identifies
   sustained trends with a lag, and that detection transferred to 9/9 untuned
   assets. If the gate detects bull regimes, its mirror detects bear regimes.
2. Crypto bears trend hard (BTC 2018: -84%; 2022: -77%). The short side harvests
   exactly what the champion sits out.
3. The mechanism is inherited, not fitted: every parameter (SMA200, ROC30,
   EMA20/50, vol-target 0.40, quantization 0.25, caps) is frozen at the
   champion's values, mirrored. Nothing is optimized — selection-fishing stays
   near the theoretical minimum.
4. The two sleeves are active in disjoint regimes (bull gate vs bear gate), so
   return correlation should be near zero — far under the <0.4 portfolio bar.
5. The honest failure mode is informative: if crypto short-trend fails, it closes
   the entire short/TSMOM-symmetric direction and documents WHY crypto bears are
   or aren't harvestable.

### Variant (exact, no others)

- **Trial #98 (sole variant)**: short BTC+ETH, entry when
  `close < SMA200 AND ROC30 < 0 AND EMA20 < EMA50` (all three), exit when any
  condition breaks. Sizing: `clip(0.40 / rv30, 0, 1)` quantized to 0.25 steps,
  50% per-pair cap, weights/2 across the 2-pair basket. Fees 0.15%/side, 2-bar
  signal lag, -30% disaster brake (mirrored: on adverse move against the short).
  **No parameter changes, no tuning, no second variant.**

### Frozen (changing any = protocol violation)

VOL_TARGET 0.40, VOL_LOOKBACK 30, QUANT_STEP 0.25, PER_PAIR_CAP 0.50,
core signal (mirrored: close<SMA200 & ROC30<0 & EMA20<EMA50), exits
(any condition breaks), -30% disaster brake, fees 0.15%/side, 2-bar signal lag,
BTC+ETH 1d futures universe. No lookahead: all indicators use only completed
bars (same shift convention as the champion harness). Shorts are simulated as
negative weights in `net_from_weights`; turnover/fee accounting handles sign
changes (a long->short flip is 2x turnover, not 0).

### Carry cost (mandatory, pre-registered)

Funding history is a blocked data axis. Primary run charges the sleeve a
conservative **-10%/yr carry, pro-rated daily, on every in-market day**. Report
0%/yr and -20%/yr as sensitivity bounds. Promotion is judged at -10%/yr.
(Rationale: historical average funding would *pay* shorts, so -10% is deliberately
pessimistic; -20% brackets stressed-bear funding flips.)

### Zero-cost pre-gates (run BEFORE the trial; if either fails, zero trials spent)

1. **Activity census**: count mirrored-gate in-market days and round trips on
   BTC+ETH futures 2020-01->2026-05. If round trips < 15 full-window OR in-market
   days < 20 in the 70/15/15 TEST split: STOP — verdict UNTESTABLE, zero n_trials.
2. **Whipsaw census (descriptive gate)**: distribution of mirrored-gate episode
   lengths and per-episode gross returns. If the median episode is <= 3 bars,
   the gate is structurally a whipsaw detector, not a bear detector — STOP and
   report.

### Data

- **Primary window**: futures feathers 2020-01->2026-05 (phase13/14/15 harness
  conventions).
- **Extended window (regime-coverage check, reporting only)**: BTC-only sleeve on
  the longest available spot window (~2017->2026, includes the 2018 bear). Spot
  prices as perp proxy with the same carry assumption.

### Validation plan (in order)

1. Pre-gates above (zero trial cost; stop rules pre-declared).
2. **Baseline replication**: unmodified champion through the harness; require
   TEST Sharpe ~0.39-0.41 and MC P(DD<-25%) ~28-38% before evaluating the sleeve.
3. **Standalone sleeve gate stack**: full-window metrics, 70/15/15 TEST split,
   4-window walk-forward, Monte Carlo (1,000 monthly-block shuffles) with
   explicit P(MaxDD < -25%), slippage stress (2x), calendar-year table (2022 is
   the load-bearing year), DSR at n_trials=98. Cross-asset transfer of the
   mirrored gate on the 9-asset universe (unchanged parameters) — reporting, with
   a soft expectation of >=6/9 non-negative.
4. **Correlation analysis**: daily-return correlation sleeve-vs-champion (full
   window and TEST); overlap census (days both active — expected ~0 by
   construction; report it).
5. **Combined portfolio (the primary prediction)**: pre-register the exact
   combination BEFORE results — champion weights plus sleeve short weights in one
   account, per-pair net exposure capped at the champion's existing 50%. Full
   gate stack on the combined stream, side-by-side with same-session champion
   baseline.
6. **Average of all runs, not the best** (Kaufman convention) wherever anything
   is swept.

### Combined portfolio construction (pre-registered)

The combined portfolio is: `combined_W = champion_W - sleeve_W` where
`champion_W` is the champion's quantized vol-target weight matrix (long when
bull gate active) and `sleeve_W` is the mirrored quantized vol-target weight
matrix (short when bear gate active), both divided by len(SYMS) for the 2-pair
basket. Per-pair net exposure (combined) is capped at the champion's existing
50% (i.e., if the short sleeve is active for a pair while the champion is flat,
net is -sleeve_weight capped at -0.50; if both are somehow simultaneously active
— expected ~0 — they net out). The `net_from_weights` function handles this
naturally: negative positions are short, turnover is |delta| (a long->short flip
is 2x), and fees apply on all position changes.

### Promotion criteria (ALL must hold for the sleeve to earn portfolio slot 2)

1. **Primary**: combined portfolio Sharpe >= same-session champion baseline
   Sharpe AND combined MC P(MaxDD < -25%) <= champion baseline's, both at -10%/yr
   carry.
2. Standalone sleeve: full-window Sharpe >= 0.5; TEST-split Sharpe > 0.20;
   calendar-2022 return positive; no calendar year worse than -15%; >= 15 round
   trips full-window.
3. Correlation with champion daily returns < 0.4 on both full window and TEST
   split.
4. Combined walk-forward: >= 3/4 windows positive, and no window the champion had
   positive flipping below -5% combined.
5. DSR: combined-portfolio DSR at n_trials=98 >= champion baseline DSR recomputed
   at 98.
6. Robustness to carry: criteria 1-2 must also hold directionally at -20%/yr
   carry (small degradation allowed; a sign flip of the sleeve's full-window
   return is a FAIL).

### Budget

Maximum 1 backtested variant (trial #98). Hard cap. Pre-gates, baseline
replication, carry sensitivity re-pricing of the SAME weight stream, the
extended-window BTC report, and the combined-portfolio evaluation (derived from
the two streams) do not count as additional trials. No tuning of any inherited
parameter. If a "small tweak" looks tempting mid-session, write it in the
session report's "ideas parked" section and stop.

If either pre-gate fails: zero trials spent; report why; n_trials stays 97.

**— END OF PRE-REGISTRATION BLOCK —**

---

# RESULTS (filled in after the pre-registration block was locked)

## 2. Outcome summary

**STOPPED AT PRE-GATE 2 (whipsaw census). Trial #98 was NEVER RUN. Zero n_trials
spent — the project's cumulative trial count stays at 97.**

- Pre-gate 1 (activity census): **PASS** — abundant activity.
- Pre-gate 2 (whipsaw census): **FAIL** — median mirrored-gate episode length is
  exactly **3 bars**, hitting the pre-registered stop rule ("if the median episode
  is <= 3 bars, the gate is structurally a whipsaw detector, not a bear detector —
  STOP and report").

Per the locked protocol, no backtest of the sleeve, no baseline replication
consumption, no combined portfolio, no DSR ledger change. The champion is unchanged.
This is the second time a zero-cost gate has stopped a pre-registered trial before
it spent selection budget (first: H-RangeVol's EWMA variant at the synthetic sanity
gate, 2026-07-10 earlier session).

Scripts: `phase16_bearshort.py` (the full pre-registered pipeline; exits at the
pre-gate), `phase16_diag_gate_census.py` and `phase16_diag_spot_census.py`
(descriptive diagnostics only — no strategy returns were computed anywhere).

## 3. Pre-gate 1 — activity census (PASS)

Mirrored gate on BTC+ETH futures, 2020-01 → 2026-05 (BTC 2,339 bars from
2020-01-01; ETH 2,065 bars from 2020-10-01):

| Pair | Round trips (gate episodes) | In-market (weight>0) days |
|---|---|---|
| BTC | 62 | 529 |
| ETH | 44 | 571 |
| **Total** | **106** (bar: >=15) | basket 692 days full-window |

TEST split (last 15% of the harness index, from 2025-06-11): **130 basket
in-market days** (bar: >=20). Both thresholds passed by an order of magnitude —
unlike H-COT, activity was never the issue.

## 4. Pre-gate 2 — whipsaw census (FAIL, stop rule triggered)

All 106 mirrored-gate episodes, both pairs, with the 1-bar execution-lag reference
convention (gross = short return close[entry+1] → close[exit+1], before fees and
carry):

| Statistic | Value |
|---|---|
| Episode length: median / q25 / q75 / max | **3 bars** / 1 / 10 / 89 |
| Share of episodes <= 3 bars | **53%** |
| Per-episode gross short return: median / mean | -0.0% / +0.6% |
| Episodes with positive gross | **21%** |
| Best / worst episode | +53.1% / -18.3% |

**Stop rule: median <= 3 bars → the gate is structurally a whipsaw detector on the
short side.** More than half of all bear-gate activations last three days or less;
they are noise crossings of the 3-of-3 boundary, not detected bear regimes.

## 5. Why the mirror is not symmetric (diagnostics, descriptive only)

Side-by-side census of the champion's bull gate vs the mirrored bear gate on the
identical window and construction (`phase16_diag_gate_census.py`):

| Gate | Episodes | Median len | q75 len | Max len | Share <=3 bars | Mean gross/episode | % positive |
|---|---|---|---|---|---|---|---|
| BULL (champion) | 81 | 5 | 29 | 119 | 41% | **+6.0%** | 32% |
| BEAR (mirror) | 106 | 3 | 10 | 89 | 53% | **+0.6%** | 21% |

The mirrored gate fires ~30% more often, holds for a third as long (q75: 10 vs 29
bars), and earns one **tenth** the gross per episode. The same 3-of-3 lagging
confirmation logic that rides long, slow bull trends gets chopped to pieces on the
short side, because crypto bear price action is structurally different from
inverted bull action: declines arrive as sharp crashes (which the lagging gate
confirms only near the local bottom) followed by violent bear rallies (short
squeezes) that immediately break EMA20<EMA50 and eject the position.

Gross short return by episode length (bear gate):

| Length bucket | n | Mean gross | % positive | Sum gross |
|---|---|---|---|---|
| 1-3 bars | 56 | -0.9% | 5% | **-52.5%** |
| 4-10 bars | 25 | -3.4% | 16% | **-84.8%** |
| 11-30 bars | 10 | -4.1% | 30% | -41.3% |
| >30 bars | 15 | **+16.3%** | 80% | **+244.9%** |

Only the 15 longest episodes (14% of activations) make money; the other 91
episodes sum to **-178.6% gross** before a single basis point of fees or carry.
And the profitable tail is itself concentrated: the top 3 episodes (ETH 2022-04
+53%, ETH 2025-02 +36%, ETH 2026-01 +27%) sum to +116.4% — the entire remaining
103 episodes sum to **-50.2%**. Add the cost side this stream would have carried —
106 round trips at 0.30%/RT in fees plus the pre-registered -10%/yr carry on ~700
in-market basket days (≈ -19% cumulative) — and the structural hopelessness is
plain without running the trial.

Calendar distribution (bear gate, gross): 2021 -18.5%, **2022 +69.4%** (but +53pp
of that is the single ETH April episode), 2023 -10.3%, **2024 -50.6%**, 2025
+42.8%, 2026 +33.4%. Even the load-bearing 2022 bear year is one episode, not a
harvestable regime.

## 6. Extended-window check — BTC spot 2018→2026 (reporting only, as pre-registered)

`phase16_diag_spot_census.py`, BTC spot 2018-01-11 → 2026-05-25 (3,057 bars,
includes the full 2018 bear, the one regime the futures window lacks):

- 81 episodes, median length 3 bars, share <=3 bars 52% — same whipsaw signature.
- **Sum of all episode gross short returns over 8.4 years: +3.7%** — before fees
  (81 RTs ≈ -24%) and before carry. The direction is economically dead on the
  longest available window.
- **2018 itself — an -84% bear year — yielded just +2.6% gross** across 12
  episodes (median 4 bars). This is the single most informative number of the
  session: even the best conceivable bear regime was not harvestable by this gate,
  because 2018's decline was a staircase of crashes and +30-50% dead-cat rallies,
  each rally ejecting the short at the worst price.
- 2022: +27.0% gross (18 episodes); 2024: **-23.0%**; 2021: -10.1%.

## 7. Verdict per pre-registered criteria

| Criterion | Result |
|---|---|
| Pre-gate 1 (activity: >=15 RTs full, >=20 TEST in-market days) | PASS (106 RTs; 130 TEST days) |
| Pre-gate 2 (whipsaw: median episode > 3 bars) | **FAIL (median = 3) → STOP** |
| Trial #98 (standalone sleeve gate stack) | NOT RUN (per stop rule) |
| Combined portfolio (primary prediction) | NOT RUN (per stop rule) |
| Promotion criteria 1-6 | NOT EVALUATED (per stop rule) |
| n_trials | **UNCHANGED at 97** |

**H-BearShort is REJECTED at the structural level.** The hypothesis's own logic is
what failed: it assumed "if the gate detects bull regimes, its mirror detects bear
regimes." The census shows the mirror detects mostly noise (53% of episodes <= 3
bars), and the descriptive gross — before any costs — depends on 3 of 106 episodes.
The pre-registered prediction (a) "a positive standalone return stream concentrated
in bear regimes" is contradicted descriptively: the stream's gross is negative
outside its top-3 episodes and near-zero (+3.7%/8.4y) on the longest window.
Prediction (b) was never reached.

Per NEXT_TASK: **the short/TSMOM-symmetric direction is now closed for this
dataset.** Any future short-side hypothesis must first explain how it defeats the
squeeze/whipsaw structure documented here (e.g., a structurally different
short-entry trigger), not merely re-parameterize the mirror.

## 8. Lessons

1. **Crypto bears are not inverted bulls.** The champion's lagging 3-of-3
   confirmation is fit-for-purpose long (slow trends reward late entry) and
   structurally wrong short (crashes are over by confirmation time; squeezes eject
   the position). Time-series-momentum symmetry (Moskowitz-Ooi-Pedersen) does not
   hold for this gate on this asset class — the champion's flat-in-bear design is
   not "leaving money on the table"; the money mostly isn't there for this
   mechanism.
2. **2018 is the decisive regime witness**: an -84% year produced +2.6% gross for
   the mirrored gate. "Bears trend hard" is true of price but not of what a lagging
   confirmation gate can extract from it.
3. **The zero-cost pre-gate discipline paid for itself a second time** (after
   H-RangeVol's EWMA cancellation): a structurally doomed trial was identified and
   stopped for zero selection cost. The whipsaw census (episode-length + gross
   distribution) is cheap and should be a standard pre-gate for any future
   gate-style hypothesis.
4. **Regime avoidance and regime harvesting are different claims.** Evidence that
   a gate marks a regime well enough to stand aside (binary, lag-tolerant) is not
   evidence it marks the regime well enough to trade it directionally
   (lag-punished). This sharpens the interpretation of the champion's edge:
   detection quality is asymmetric in the cost of lag.
5. Ideas parked (NOT tested, recorded per protocol): a short trigger based on
   bear-rally exhaustion (enter on failed rallies rather than post-crash
   confirmation) would attack the documented squeeze structure directly — but it
   is a new signal-prediction construct on OHLCV, the family with 95+ failures,
   and would need extraordinary justification before spending a trial.

