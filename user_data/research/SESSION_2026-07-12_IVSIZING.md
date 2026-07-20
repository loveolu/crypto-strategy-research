# SESSION 2026-07-12 -- H-IVSizing: max(rv30, DVOL/100) in the champion''s sizing denominator

> **Experiment type**: Pre-registered, single-shot, pre-gated. Would-be trial #99.
> Pre-gates cost ZERO n_trials. n_trials stays at 98 (P2 stop before trial runs).
> **Final status**: CLOSED AT PRE-GATE P2 -- IV-sizing direction and DVOL axis CLOSED.
> **Assignment source**: NEXT_TASK.md, Director cycle #15, 2026-07-12.

---

## S1 PRE-REGISTRATION BLOCK
*(Written before phase22_ivsizing.py was executed or any number computed.
 Locked constants copied verbatim from NEXT_TASK.md before any run.)*

### S1.1 Hypothesis

The champion sizes with backward-looking rv30 (30d realized vol), which lags vol
expansions by construction. The corrected cycle-#13 census proved Delta5d DVOL changes
lead Delta5d rv30 changes (lead corr +0.33 at -1 day vs +0.29 contemporaneous, lagging
side decaying to 0 by +4). Taking the elementwise MAX of realized and implied vol in the
sizing denominator uses implied vol exactly when it exceeds realized -- i.e., when the
options market prices MORE risk than has yet been realized (the forward-looking case) --
and leaves the champion bit-identical otherwise. If the lead is economically real, the
modified sleeve steps down exposure days earlier at vol-expansion onsets, improving the
in-market drawdown tail at modest cost.

### S1.2 Locked constants (ALL fixed here; no deviations permitted)

| Constant | Value | Rationale |
|---|---|---|
| Sizing formula | rv_eff_i(t) = max(rv30_i(t), DVOL_BTC(t)/100) | Zero free parameters |
| Weight formula | w_i = quantize_25%( core_i x clip(0.40 / rv_eff_i, 0, 1) ) / 2 | Same 2-bar lag, same 0.15%/side fees |
| DVOL driver | BTC DVOL only (ETH DVOL cached but unused) | Consistent with H-IVGate lock |
| DVOL alignment | ffill(limit=2) to champion calendar | Same as phase21 |
| Free parameters | ZERO | No z-scores, no thresholds, no blend weights, no VRP haircut |
| Evaluation window | DVOL-champion overlap only (2021-03-24 to 2026-05-31) | Same as phase21 |
| Champion baseline | Recomputed on the IDENTICAL overlap window | Replication band: overlap FULL Sharpe 0.65-1.20 |
| Split dates | 70/15/15 chronological on the overlap window | Flag short TEST split as episode-hostage |
| MC | 1,000 monthly-block-shuffle sims, seed 11 | Identical to all prior phases |
| WF configs | 3/4/5/6 windows | Same as phase21 |
| DSR | n_trials = 99 via freqtrade_dsr.py | Champion baseline recomputed at 99 on the same window |
| n_trials budget | 98 -> 99 only if the trial runs; pre-gate stops cost zero | |
| Fee | 0.15%/side on |Delta position| | Same as champion |

### S1.3 Pre-gates (EACH evaluated before the trial)

**P1 -- Materiality census**: count in-market days where the QUANTIZED weight differs
and distinct difference episodes.
STOP if < 5% differing in-market days OR < 20 episodes.

**P2 -- Harm census on affected days**: on days where W_ivsizing < W_champ, compare
the CHAMPION forward 10d net return vs unconditional in-market forward 10d distribution.
STOP if NOT worse (nothing to avoid).

### S1.4 Pre-registered validation bars (ALL must hold to adopt)

1. MC P(DD < -25%) improved by >= 5pp, OR TEST Sharpe improved by >= +0.05 -- at least one
2. TEST Sharpe not degraded by more than 0.02
3. Full-window (overlap) Sharpe not degraded by more than 0.05
4. WF majority-positive at >= 3 of 4 window configs
5. DSR at n_trials=99 >= same-window champion baseline DSR at n_trials=99
6. Activity where judged: > 0 quantized-weight-difference days inside the TEST split
7. Per-year accounting: no year where the construction fee + exposure drag exceeds gross avoided loss

### S1.5 Known honest failure modes (stated before results)

(a) VRP drag: DVOL > rv30 on most days (variance risk premium) -- chronic average
    exposure reduction -- CAGR/Sharpe cost even when the lead is real.
(b) Quantizer may discard the max() difference, as it discarded the GK precision in #15.
    P1 measures this explicitly.
(c) Short TEST split (~0.78 years): episode-hostage risk (finding #9).
(d) Vol-spike-then-rip episodes: IV rises, sizing drops, price rips -- the
    construction misses the rally.

---

## S2 STEP 1 -- REPLICATION BASELINE

Script: phase22_ivsizing.py, run 2026-07-12.

| Metric | Value | Gate | Result |
|---|---|---|---|
| Overlap window | 2021-03-24 to 2026-05-27 | -- | 1,891 days |
| Futures data loaded | 2021-03-24 to 2026-05-27 | -- | OK |
| BTC DVOL cache | 2021-03-24 to 2026-07-11 | -- | 1,936 days, loaded from feather |
| DVOL NaN after ffill(2) | 0 | -- | OK |
| Champion FULL Sharpe on overlap | 0.868 | [0.65, 1.20] | PASS |
| Level corr z_iv / z_rv | +0.6870 | ref +0.6870 | REPLICATED |
| avg_lead IV-leading (-5..-1) | +0.2489 | ref +0.2489 | REPLICATED |
| avg_lag IV-lagging (+1..+5) | +0.0714 | ref +0.0714 | REPLICATED |

**REPLICATION GATE: PASS.** Phase21 census numbers reproduced exactly.

---

## S3 PRE-GATE P1 -- MATERIALITY CENSUS

| Metric | Value | Stop rule | Result |
|---|---|---|---|
| Total in-market days (champion, 2-bar lag) | 661 | -- | -- |
| Days where QUANTIZED weight differs (any asset) | 232 | -- | -- |
| Of which in-market days | 218 | < 5% -> STOP | 33.0% of in-market days -- PASS |
| Distinct difference episodes | 35 | < 20 -> STOP | PASS |

**Differing days by year:**

| Year | Total diff days | In-market diff days |
|---|---|---|
| 2021 | 16 | 16 |
| 2022 | 0 | 0 |
| 2023 | 98 | 96 |
| 2024 | 81 | 74 |
| 2025 | 37 | 32 |
| 2026 | 0 | 0 |

**70/15/15 split dates:**
- TRAIN ends: 2024-11-05
- VAL ends: 2025-08-16
- TEST starts: 2025-08-17
- TEST ends: 2026-05-27

**Differing days in TEST split: 0 (0 in-market)** -- this would have tripped Bar 6
if the trial reached it (no activity where judged). Pre-registered Bar 6: > 0 diff
days in TEST required. TEST split falls entirely in 2025-08-17 to 2026-05-27, and
all differing days are in 2021-2025 with 2026 showing 0 diff days. The TEST split
window has zero differing days regardless.

All 232 differing days have IVSizing < Champion (DVOL > rv30 -- exposure reduced). Zero
days where IVSizing > Champion (impossible by construction: max() can only increase the
denominator, reducing the scale factor).

**PRE-GATE P1: PASS (33.0% differing in-market days, 35 episodes)**

---

## S4 PRE-GATE P2 -- HARM CENSUS ON AFFECTED DAYS

Affected days = in-market AND W_ivs < W_champ = 218 days.

| Metric | Value | Stop rule | Result |
|---|---|---|---|
| Affected days (n=218): forward 10d median | +1.67% | < unconditional -> PASS | WORSE? NO |
| Affected days (n=218): forward 10d mean | +2.66% | < unconditional -> PASS | WORSE? NO |
| Unconditional in-market (n=661): forward 10d median | +0.53% | -- | -- |
| Unconditional in-market (n=661): forward 10d mean | +1.30% | -- | -- |

**PRE-GATE P2: FAIL**

The days where DVOL/100 > rv30 (i.e., the days the max() construction would reduce
exposure) have BETTER forward 10d returns than unconditional in-market days:
- Affected median +1.67% vs unconditional +0.53% -- affected is BETTER
- Affected mean +2.66% vs unconditional +1.30% -- affected is BETTER

**STOP. Zero trials spent. n_trials stays at 98.**

### Interpretation of the P2 failure

This is the decisive finding. The VRP mechanism (failure mode (a) from S1.5) is
confirmed empirically:

- The variance risk premium (DVOL > rv30) is a chronic condition in crypto. When DVOL
  exceeds rv30, it does not signal imminent price decline -- it signals that the options
  market is pricing more risk than has been realized, which is the normal state in a
  risk-premium-paying asset.
- The days where DVOL > rv30 (implied > realized) are, if anything, **favorable** for
  the champion's strategy: those are days when the market is in an uptrend (which is
  why the champion is in-market at all) AND implied vol is elevated, suggesting that
  market participants are paying up for crash protection. In a trending bull market, this
  is a common profile of the "wall of worry" regime.
- Reducing exposure on those days would subtract from returns in favorable conditions,
  not protect against adverse ones.
- The max() construction has zero free parameters, but it is the WRONG construction for
  this data: the forward-looking property of DVOL (its lead over rv30 CHANGES) does NOT
  translate into worse in-market forward RETURNS on days when DVOL exceeds rv30 LEVELS.
  Lead in changes and worse returns on high-DVOL days are different properties.

### Connection to the DVOL lead finding

The DVOL lead finding (avg_lead +0.2489 > avg_lag +0.0714) means: when DVOL rises
(relative to its recent level), rv30 tends to rise over the next few days. This is a
lead in CHANGES. It does NOT mean that days when DVOL > rv30 in absolute levels have
worse forward returns. The P2 census measured the relevant quantity: absolute-level
comparison, and found no harm to avoid.

### Why this closes the DVOL axis

Per the pre-registration (S1.6) and NEXT_TASK.md: "A P1/P2 stop also formally closes
the DVOL axis for daily-bar champion improvements (veto closed at B3a, sizing closed
here -- no third mechanism exists on daily bars without new data)."

- The IV-veto mechanism was closed at H-IVGate B3a (2026-07-12, cycle #14): only 4
  in-market spike-onset episodes -- no harvestable tail.
- The IV-sizing mechanism is now closed at P2 (2026-07-12, cycle #15): DVOL > rv30
  days have BETTER not worse forward returns -- reducing exposure harms not helps.
- Both mechanisms that could translate the DVOL lead into champion improvement have
  been evaluated and found not harvestable. The DVOL lead is a real statistical
  property (confirmed three separate ways: level non-redundancy, lead in changes, and
  symmetry assert passing), but it does not translate to a practical trading improvement
  through either the episode-veto or continuous-sizing route on daily bars.
- The only remaining route would be a fundamentally new data axis or mechanism. That
  requires a new pre-registration.

---

## S5 TRIAL #99 RESULTS

**NOT REACHED.** P2 stop fired before the trial. Zero trials constructed. n_trials
remains at 98.

---

## S6 VALIDATION BAR CHECK

**NOT EVALUATED.** Pre-gate P2 stopped the experiment. The trial never ran.

Note: even if P2 had passed, the materiality census revealed a second issue: Bar 6
(>0 differing days in TEST split) would have failed, since the TEST split
(2025-08-17 to 2026-05-27) contains ZERO differing days. The construction would have
produced no measurable activity in the evaluation period. The P2 failure is the primary
and dispositive stop.

---

## S7 VERDICT AND DURABLE FINDINGS

**VERDICT: CLOSED AT PRE-GATE P2. IV-sizing direction CLOSED. DVOL axis for
daily-bar champion improvements CLOSED. Zero trials spent; n_trials stays at 98.**

### Durable findings (to record in strategy_research_notes.md)

1. **DVOL lead in changes does NOT imply worse returns on high-DVOL-level days.**
   These are distinct properties. A lead in 5d changes (what the phase21 census
   measured) means DVOL anticipates rv30 MOVEMENTS. It does not mean that days when
   DVOL/100 > rv30 are bad for the in-market strategy. The P2 census confirms the
   opposite: those days have median +1.67% vs +0.53% unconditional forward 10d return.

2. **The VRP (variance risk premium) in crypto is pervasive and positive-carry.**
   When DVOL > rv30, it reflects a chronic state where option buyers pay a risk
   premium. In a trending bull market (which is when the champion is in-market), that
   premium is collected, not a warning signal.

3. **Pre-gate P2 is a necessary check distinct from P1.** P1 (materiality) confirmed
   the max() construction fires 33% of in-market days -- not a quantizer-swallows-it
   failure. P2 (harm) found that the fired days are the WRONG target. Both pre-gates
   are necessary for different failure modes.

4. **The DVOL axis is now exhausted for daily-bar champion modifications** (per
   NEXT_TASK.md standing rule). Two mechanisms tested: episode-veto (H-IVGate, closed
   B3a), continuous sizing (H-IVSizing, closed P2). No third mechanism remains on daily
   bars without new data or a structural redesign.

5. **The champion's existing rv30 sizing is appropriate despite the DVOL lead.** The
   lead means DVOL anticipates rv30 changes, but the max() substitution would act on
   ALL high-DVOL days -- the majority of which are favorable. A targeted use of the
   DVOL CHANGE signal (not level) might be a future route, but it would require a
   fundamentally different design (not a max() construction) and would need its own
   pre-registration.

### Near-miss observations (parked in writing, NOT to be run)

- A DVOL-change-based construction (sizing on rv30 + delta_DVOL_5d * k) might target
  the actual leading signal. This would have a free parameter (k), would need a
  separate pre-registration, and is NOT being run here.
- The TEST split zero-activity finding (Bar 6 would fail) is independently informative:
  even if P2 had passed, the construction has no activity in the most recent ~9 months.
  This is consistent with 2026 showing 0 differing days -- the most recent regime may
  have rv30 persistently elevated above DVOL, making the max() inactive.

---

## S8 DIRECTOR VERIFICATION (cycle #16 review, 2026-07-12)

Per the standing rule (Director reruns stops; cycle-#13 false-stop precedent), the P2
stop was independently verified with a separate code path:
`phase22_diag_p2_verify.py` (does not import phase22_ivsizing.py; rebuilds champion
weights, the max() variant, and the census from scratch).

**V1 — count replication (exact match):** in-market 661, diff days 232, affected
(diff & in-market) 218, episodes 35.

**V2–V4 — harm census under three views**, including two the engineer did not run
(lag-consistent measurement from t+2, when the weight change would actually take
effect through the 2-bar lag; and raw equal-weight BTC/ETH asset returns, removing
the strategy's own sizing from the measurement):

| View | Affected med/mean | Uncond med/mean | Affected worse? |
|---|---|---|---|
| V2 engineer-style (champ net, from t) | +1.11% / +2.43% | +0.54% / +1.19% | NO |
| V3 lag-consistent (champ net, from t+2) | +1.04% / +2.21% | +0.36% / +1.13% | NO |
| V4 raw-asset (EW BTC/ETH, from t+2) | +1.72% / +2.41% | +0.98% / +1.65% | NO |

(V2 magnitudes differ slightly from S4 due to window-inclusivity conventions; the
direction and roughly 2x margin are identical.) No view shows harm on affected days
under any timing or measurement convention — this is not a cycle-#13-class false stop.

**P2 STOP VERIFIED. Closure accepted: IV-sizing direction CLOSED; DVOL axis for
daily-bar champion improvements CLOSED. n_trials = 98. Champion untouched.**

---

## Appendix: Raw script output (key sections)

```
==============================================================================
PHASE 22 - H-IVSizing: max(rv30, DVOL/100) in champion sizing denominator
==============================================================================

STEP 1 -- Replication gate: PASS (Sharpe 0.868, band [0.65, 1.20])
Phase21 census numbers REPLICATED (corr 0.6870, lead 0.2489, lag 0.0714)

PRE-GATE P1:
  Total in-market days: 661
  Days where QUANTIZED weight differs: 232
  Of which in-market: 218 (33.0%)
  Distinct difference episodes: 35
  Differing days in TEST split: 0
  -> PASS (33.0% >= 5%, 35 episodes >= 20)

PRE-GATE P2:
  Affected days (n=218): median=+1.67%  mean=+2.66%
  Unconditional in-market (n=661): median=+0.53%  mean=+1.30%
  -> FAIL: affected-day forward returns NOT worse than unconditional

VERDICT: CLOSED AT PRE-GATE P2. Zero trials spent. n_trials stays 98.
```
