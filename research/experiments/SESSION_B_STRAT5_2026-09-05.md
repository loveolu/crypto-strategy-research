# Session B — five strategies not previously tested, walk-forward (branch `session-b-research`, 2026-09-05)

**Ask:** top 5 strategies the program has not used, targeting ≥ 20%/yr. **Method:** five pre-registered
constructs with kill conditions fixed before running; rolling walk-forward (11 windows, 12 m train /
3 m test / 3 m step, 2024-01 → 2026-09); A-011 measured per-instrument taker costs; unleveraged;
9 OKX USDT perps at 4h. Module `user_data/research/strat5.py` (self-contained, reads this worktree's
data); runner `a022_strat5_wf.py`; sanity `a021_sanity.py`; results `research/measurements/SESSION_B_strat5_wf.pkl`.
Sanity: the module's B2 long leg reproduces the main harness exactly on the fixed split (+30.8%, Sh 1.42, 168 trades).

## Result

| # | strategy | mechanism | WF net | ann | DD | Sh / So | Cal | 2024 / 2025 / 2026 | 365d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| — | B2 (reference, this harness) | cascade long in daily uptrend + BTC-drop | +44.3% | 15.1% | −3.9% | 1.30 / 3.89 | 3.90 | +41.3 / +2.0 / +0.1 | +1.1% | Candidate (paper-trading, Session A) |
| 1 | **LS-Cascade** | B2 long + squeeze-fade SHORT with strict bear gate (price < SMA200, SMA200 falling, EMA20 < EMA50) | +38.6% | 13.3% | −13.3% | 1.07 / 2.36 | 1.00 | +28.2 / +3.8 / +4.2 | +3.2% | **KILLED** — Sh 1.07 < B2 1.30; short leg 2024 **−9.3%** (rule: < −5%) |
| 2 | **TSMOM-4h** | 15-day time-series momentum, vol-target, L/S | −6.3% | −2.5% | −32.8% | 0.07 / 0.10 | — | +16.8 / −18.0 / −2.1 | −13.4% | **KILLED** — long-only +1.8%, short-only −10.9%; **shorts lost −7.5% in the 2025 bear** they exist for |
| 3 | **AltBTC-MR** | alt/BTC ratio z-score reversion (30 d, ±2σ in, 0.5σ out), dollar-neutral | −5.1% | −2.0% | −17.6% | −0.13 / −0.18 | — | −7.1 / −1.2 / +3.4 | +1.6% | **KILLED** — Sh ≤ 0.3 |
| 4 | **CascadeSpread** | on systemic-cascade bars, long 3 hardest-hit / short 3 least-hit, dollar-neutral, 24h | **+35.5%** | **12.3%** | **−6.1%** | **1.21 / 2.74** | 2.01 | **+32.0 / +7.4 / −4.4** | −1.7% | **SURVIVES** (Sh > 0.3). 131 spreads, 24 bps net each, WR 53%, PF 1.74. **Cost-fragile at 6 legs**: ×2 Sh 0.53, ×3 Sh −0.16 |
| 5 | **GBM-Cascade** | HistGB (depth 3, 100 iters) on 7 causal features, WF re-fit, enter at P ≥ .60 | +61.0% | 20.0% | −30.5% | 0.99 / 1.59 | 0.66 | **+81.3 / +19.3 / −25.5** | −29.3% | **KILLED** — Sh < B2; last 365 d −29%. Diagnosis below |
| **P** | **B2 + CascadeSpread 50/50** | long cascade + neutral cascade; ρ = **+0.004** | +40.8% | 14.0% | **−3.8%** | **1.77 / 4.60** | 3.74 | +37.4 / +4.8 / −2.2 | — | **SURVIVES** (Sh 1.77 > max 1.30). Best risk-adjusted book found |

Sensitivity rows (reported, not selected): TSMOM LB 42 → Sh 0.36 (+18.5%); LB 168 → −0.41. GBM P ≥ .55 →
Sh 0.53; P ≥ .65 → Sh 0.99 with 2025 +35% / 2026 −22%. Portfolio 70/30 B2/S4 → Sh 1.64, ann 14.5%.

## Diagnoses

**LS-Cascade.** The strict bear gate (price below a *falling* SMA200 with EMA20 < EMA50) still admits
2024 pullbacks — it was ON 19% of 2024 bars — and shorting rallies inside a bull cost −9.3%. The short
leg does earn in the bear (+1.7% 2025, +4.1% 2026) but not enough. Adding it to B2 raised drawdown from
−3.9% to −13.3%. The daily-bar gate family cannot separate a bear from a deep pullback; the short side
needs a different regime sensor, not a stricter version of this one.

**TSMOM-4h.** Trend-following at 4h with 7–30-day lookbacks does not work on these perps in any
direction. The shorts lost in the crash year: bear rallies (squeezes) whipsaw them — H-BearShort's
"crashes + squeezes" finding, now confirmed at 4h. This closes the *intraday-resolution* trend question
that T-039 opened at 1h.

**GBM.** 99% of its signals fire with the daily trend gate OFF. In the last four windows, gate-ON
signals were +237 bps / WR 80% (n = 5); gate-OFF were −102 bps / WR 41% (n = 684). Trained on 2024–25,
where ungated cascade-buying paid, it learned the ungated-S1 profile (S1: 2025 +32%, 2026 −24%) and
reproduced it: +19% in 2025, −25% in 2026. The hand-built gate is the single most valuable feature and
the model under-weights it. A model constrained to gate-ON bars would be B2 with extra noise.

**CascadeSpread — the survivor, and its one weakness.** A dollar-neutral cascade bet: the coin hit
hardest in a systemic cascade bounces more than the coin hit least. It is uncorrelated with B2 (+0.004),
earns in the 2025 bear (+7.4%), and has DD −6.1%. The weakness is cost: 12 side-costs per spread
against 24 bps net edge. Leg-count sensitivity (post-hoc — k=3 was pre-registered, so this is a
diagnosis, not a selection):

| legs per side | ×1 cost | ×2 | ×3 |
|---|---|---|---|
| k=3 (pre-registered) | Sh 1.21, +35.5%, DD −6.1% | Sh 0.53 | Sh −0.16 |
| k=2 | Sh 1.23, +46.1%, DD −9.7% | Sh 0.69 | Sh 0.13 |
| **k=1 (extremes only)** | **Sh 1.66, +113%, DD −13.5%** | **Sh 1.30** | **Sh 0.93** |

The edge lives in the extremes (consistent with B04: hardest-hit bounce most) and cost falls with
legs, so fewer legs wins on both counts. **k=1 survives 3× cost, which k=3 does not.** If CascadeSpread
goes forward it should go at k=1 or k=2, and that choice must be priced as a selection (n ≥ 3
configurations seen). DD rises with concentration.

## Against the 20%/yr target — stated plainly

No construct, old or new, earns 20% in every year of 2024 → 2026. The bear years are the wall:

| | 2024 | 2025 | 2026 (to Sep) |
|---|---|---|---|
| best book (B2 + CascadeSpread 50/50) | +37.4% | +4.8% | −2.2% |
| CascadeSpread k=1 (post-hoc) | — | earns in 2025 | — |
| GBM (killed) | +81% | +19% | −25% |
| hold basket | +77% | −33% | −26% |

What the day established: (1) a **second, uncorrelated mechanism exists** (neutral cascade spread) and
the combined book is Sharpe 1.77 at −3.8% drawdown — roughly 14%/yr on walk-forward with a fraction of
the risk of anything before it; (2) **trend-following, ratio mean-reversion and a gated short all fail
at 4h** — three families closed at this resolution with walk-forward evidence; (3) the ML model finds
the same edge the hand-built rule found and then over-reaches into the regime where it fails.

## Status and queue

- **CascadeSpread**: Promising (survives kill; cost-fragile at k=3; k=1 needs pre-registration).
- **B2 + CascadeSpread portfolio**: Promising — the deployable shape; forward-test both sleeves.
- **Queue**: (1) pre-register CascadeSpread at k=1 vs k=2 as ONE test and forward-test the winner beside
  B2; (2) a bear-regime sensor that is not a daily moving-average gate (funding/OI when 12 months are
  held) — the short side is real in true bears and dead in pullbacks; (3) constrain the GBM to gate-ON
  bars only as a diagnostic of whether ML adds anything inside the regime.

**Construct count, both sessions, 2026-09-02 → 09-05: ≈ 90.** Every window is seen for every
construct here; forward paper data is the only unspent evidence.

## Addendum — 2022, a genuinely out-of-sample bear (`a023_2022_oos.py`)

No threshold was fit on 2022 (TRAIN = 2023-01 → 2024-11). BNB starts 2022-12-23 → 8 perps. The daily
SMA200 gate needs 200 days → gated rules trade from 2022-07-19; gate-free (neutral, TSMOM) rules from
2022-02-08. Thresholds carried from TRAIN: long ≤ −4.95%, short ≥ +5.76%. 2022-H2 gate state: uptrend
gate ON 4% of bars, strict-bear gate ON 81%.

| strategy | window | return | Sh | DD | trades | read |
|---|---|---|---|---|---|---|
| HOLD basket (8) | Feb–Dec | **−74.7%** | −1.44 | −77% | — | the bear |
| B2 long (gated) | H2 | −3.2% | — | −3.5% | 4 | flat: gate held it out; 3 of 4 trades were FTX-week dip-buys |
| short leg, strict bear gate | H2 | **+6.4%** | 1.76 | −2.4% | 43 | earns in a true bear (also +1.7% 2025, +4.1% 2026; −9.3% 2024) |
| LS-Cascade combined | H2 | +3.0% | 0.78 | −4.9% | — | positive |
| CascadeSpread k=3 (neutral) | Feb–Dec | +1.8% | 0.21 | −6.5% | 48 | break-even; H2 +2.9% |
| CascadeSpread k=1 (post-hoc) | Feb–Dec | −0.0% | 0.12 | **−16.1%** | 48 | **worse than k=3 out of sample** — evidence against the post-hoc k=1 pick |
| **TSMOM-4h SHORT only** | Feb–Dec | **+50.1%** | **1.74** | −9.9% | — | killed on 2024–26 WF (2025 −7.5%); in a TRENDING bear it is the best thing in the table |
| TSMOM-4h L/S | Feb–Dec | +25.4% | 0.95 | −18.4% | — | |
| AltBTC-MR (neutral) | Feb–Dec | +1.2% | 0.16 | −13.2% | — | flat |
| B2 + CascadeSpread 50/50 | H2 | −0.1% | 0.03 | −4.9% | — | capital preserved |

**Answer to "did anything profit or break even in 2022":** everything except holding. Profit: TSMOM
short (+50%), TSMOM L/S (+25%), the bear-gate short leg (+6.4%), LS-Cascade (+3.0%), CascadeSpread
(+1.8%), AltBTC-MR (+1.2%). Break-even: B2 (−3.2% on 4 trades), the 50/50 book (−0.1%). Holding lost
three quarters of its value.

**What 2022 changes.** The 2024–26 walk-forward killed TSMOM because its shorts lost −7.5% in the 2025
bear. In 2022 the same rule made +50%. **Bears are not one regime**: 2022 trended down (Luna → FTX) and
rewarded trend shorts; 2025–26 chopped with squeezes and punished them. The squeeze-fade short earned
in BOTH bear types (+6.4% / +1.7% / +4.1%) and lost only in the bull pullbacks of 2024. The TSMOM kill
stands on its pre-registered window — un-killing it because a different window looks good would be
window-picking — but the mechanism is recorded as **regime-dependent, not dead**: it needs a trending
bear, and 2 of the 3 bear years in the data were not. The k=1 CascadeSpread pick does NOT generalise
to 2022 (DD −16% vs −6.5%); k=3 stays.
