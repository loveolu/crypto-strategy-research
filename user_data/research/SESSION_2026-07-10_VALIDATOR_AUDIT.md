# Session 2026-07-10 — A-ValidatorAudit: Kaufman Ch.21 diagnostics + champion re-audit

**This is an AUDIT of the existing champion (TrendVolTarget), not a trial. Zero n_trials
cost — no new construct is selected, no parameter is changed, no new strategy is
backtested. Cumulative n_trials stays at 97.**

Script: `phase17_validator_audit.py`. Assignment: `research/NEXT_TASK.md` (2026-07-10,
Research Director cycles #3/#4 — the twice-displaced, reissued validator-audit
assignment). Deliverables: the three Kaufman Ch.21 diagnostics implemented as reusable
functions in `validator.py`, this audit run, and this report.

## 1. Pre-registration block (LOCKED before any results were produced)

Written and committed to this file before `phase17_validator_audit.py` was written or
produced any numbers. Everything below the end marker was filled in afterwards. The
interpretation rules (downgrade triggers) are copied verbatim in substance from the
NEXT_TASK assignment, which itself declared them before results.

### Champion stream construction (frozen, replication-gated)

The audited object is the champion's daily net-return stream, reconstructed with the
exact phase15/16 baseline convention: BTC+ETH 1d futures feathers (2020-01 → 2026-05),
core gate `close>SMA200 AND ROC30>0 AND EMA20>EMA50` per asset, sizing
`clip(0.40/rv30_cc, 0, 1)` quantized to 0.25 steps, weights/2 across the 2-pair basket,
2-bar signal lag, fees 0.15%/side. Before any diagnostic is computed, the stream must
replicate the recorded baseline (TEST Sharpe 0.35–0.45, full-window Sharpe 1.0–1.4,
MC P(DD<−25%) 25–40% at 1,000 monthly-block sims, seed 11) or the audit STOPS.

### Diagnostic 1 — price-shock P&L decomposition: definitions (declared BEFORE looking at which days qualify)

Shock days are defined on the UNDERLYING (BTC and ETH daily close-to-close returns on
the harness index), not on the strategy stream. Two definitions, both reported — they
bracket the concept:

- **Definition A (static 99th percentile)**: calendar day t is a shock day if
  |BTC return_t| exceeds the 99th percentile of |BTC daily returns| over the full
  harness window, OR the same holds for ETH (each asset measured against its own
  full-window percentile; union across the two assets).
- **Definition B (3σ of rolling 30d vol)**: day t is a shock day if |BTC return_t| > 3 ×
  (BTC's trailing 30-day daily-return std as of t−1), OR the same for ETH. The rolling
  std is shifted one day so the threshold uses only information available before day t.
  First 30 days of each asset's history are unclassifiable and treated as non-shock.

Both definitions include shocks of BOTH signs (up-shocks and down-shocks).

**P&L attribution conventions (declared now):**

- "Excluding" a set of days = dropping those days from the daily return series entirely
  (Kaufman's removal convention), then recomputing total return (compounded) and Sharpe
  (√365 annualization) on the remaining days.
- "Share of total P&L attributable to a set of days" = sum of log(1+r) over those days
  ÷ sum of log(1+r) over all days (log decomposition is exactly additive under
  compounding). Reported alongside the recomputed ex-days total return.
- Top-k single days (k = 5, 10, 20) are ranked on the STRATEGY's own daily returns:
  best-k removed, worst-k removed, and both removed — reported for the champion and for
  the baseline.
- **Baseline**: BTC buy-and-hold daily close-to-close returns on the identical calendar
  window, no fees (fee-free hold biases the comparison AGAINST the champion, which pays
  fees — conservative direction for an audit).
- Champion shock-day P&L is only nonzero where the champion was in the market (its
  position was already sized before the shock day; no hindsight is involved in the
  attribution).

**Downgrade trigger A (copied from NEXT_TASK, operationalized):** fires if BOTH hold —

1. removing the top-10 positive-P&L shock days (per Definition A; Definition B reported
   as corroboration) erases >50% of the champion's full-window log-P&L, AND
2. the champion is materially more shock-dependent than BTC hold under the identical
   definition — operationalized as: the champion's top-10-positive-shock-day log-P&L
   share exceeds BTC hold's same share by more than 10 percentage points (absolute).

If trigger A fires: `current_champion.md` Known Limitations gains a "shock-dependent
returns" entry and the 5–15% CAGR forward band must be re-argued or lowered in writing.

### Diagnostic 2 — walk-forward window-stability: spec

- The existing WF machinery (phase15/16 convention: OOS region = second half of the
  daily stream) re-run at k = 3, 4, 5, 6 equal contiguous windows spanning that same
  region. Same total data, same frozen signal, no re-fitting (the champion has no
  fitted parameters). Windows positive/total judged on window TOTAL RETURN (the
  existing convention); also report per-window Sharpe, worst window Sharpe, and the
  spread (max−min) of window Sharpes per configuration.
- Rolling 18-month Sharpe series: trailing 548-calendar-day window (18 × 30.44 days),
  evaluated at each month end (monthly step), on the champion's daily stream. Flag the
  worst 18-month period (lowest Sharpe) and report the share of month-end evaluations
  with negative trailing Sharpe.

**Downgrade trigger B (copied from NEXT_TASK):** fires if the walk-forward verdict
(majority-positive windows) flips to minority-positive (positive windows < half) at 2
or more of the 4 window-count configurations. If it fires, the champion's "passed
walk-forward" claim is rewritten as boundary-sensitive.

### Diagnostic 3 — average-of-all-tests family context: spec

- Sources (existing records ONLY, nothing re-run): the 61-strategy search's JSON
  verdicts in `user_data/research/results/*.json` (full-window and TEST Sharpes as
  recorded on 2026-06-11), plus the extended-session TVT-family variants whose numbers
  were recorded in `BEST_STRATEGY_REPORT.md` / `SESSION_2026-06-11_FINAL_SUMMARY.md`
  (tabulated as documented constants with citations; the phase1-10 scripts' stdout was
  not persisted, so the session reports are the record).
- Report: family mean / median / max of full-window Sharpe and TEST Sharpe, and where
  the champion sits (rank, percentile). This is the honest context for the champion's
  0.41 TEST Sharpe, complementing DSR.
- `validator.py` gains a `family_context` reporting hook (field on `Verdict` + helper
  to build it from the results directory or an explicit list), so every future
  validation run can carry it. Existing API/behavior unchanged.

### Interpretation rules (verbatim substance from NEXT_TASK)

- This audit CANNOT promote anything and does not change n_trials. It can only adjust
  the champion's documented confidence.
- Neither trigger dethrones the champion (there is no challenger); they change what we
  honestly say about it. If neither fires, that is recorded plainly — a clean audit is
  also a result.

### Constraints

- No new strategies, no parameter changes, no tuning, no new backtested variants.
- If a diagnostic suggests a promising modification: "ideas parked" section, STOP.
- Python 3.13. Dry-run bot untouched.

**— END OF PRE-REGISTRATION BLOCK —**

---

# RESULTS (filled in after the pre-registration block was locked)

## 2. Outcome summary

**Both downgrade triggers came back NEGATIVE — the audit is clean.** Per the
pre-registered interpretation rules, a clean audit is itself a result worth recording:

- **Trigger A (shock dependence): does NOT fire.** The champion is materially LESS
  shock-dependent than BTC buy-and-hold under both pre-declared definitions (top-10
  positive-shock log-P&L share: 14.6% vs 55.7% under Definition A; 44.6% vs 50.6%
  under Definition B). Under Definition A the champion's shock days are net NEGATIVE
  (removing all of them improves Sharpe 1.11 → 1.20).
- **Trigger B (walk-forward boundary sensitivity): does NOT fire.** Majority-positive
  holds at 3, 4, and 5 windows; only the 6-window configuration goes minority-positive
  (3/6), and one of its three non-positive windows is an all-flat 0.0% window (gate out
  of the market the entire period — by-design bear behavior, not a loss). The rolling
  18-month Sharpe was never negative in 61 monthly evaluations (min +0.01).
- **Diagnostic 3 (average-of-all-tests)** adds the honest context Kaufman demands: the
  champion's full-window Sharpe was the PEAK of its 65-variant recorded search family
  (family mean 0.54, median 0.74), while its TEST Sharpe 0.41 ranks 13th of 64 (81st
  percentile; family mean −0.63). The convention is now a permanent `family_context`
  hook in `validator.py`.

Baseline replication gate passed before any diagnostic ran: TEST Sharpe 0.39, full
Sharpe 1.11, MC P(DD<−25%) 30.5% at 1,000 sims — all inside recorded bands, and the
4-window walk-forward numbers reproduce the phase15/16 record exactly
(+33.5/+20.8/+35.2/−7.6%, Sharpes +1.52/+1.06/+1.85/−0.60).

**n_trials unchanged at 97.** Nothing was promoted, tuned, or newly backtested.

## 3. Diagnostic 1 — price-shock P&L decomposition

Shock-day counts on the harness window (2,339 days, 2020-01 → 2026-05):
Definition A (static p99 per asset, union BTC/ETH): **36 shock days** (1.5%), champion
in-market on 12. Definition B (3σ of trailing 30d vol, shifted): **78 shock days**
(3.3%), champion in-market on 34.

### Definition A (static 99th percentile)

| Series | Total ret | Sharpe | ex ALL shock | ex-top10-best shock | top-10-best log-share |
|---|---|---|---|---|---|
| Champion | +271.8% | 1.11 | +290.7% / Sh 1.20 | +207.1% / Sh 0.98 | **+14.6%** |
| BTC hold | +933.2% | 0.91 | +1416.9% / Sh 1.08 | +181.6% / Sh 0.58 | **+55.7%** |

Full top-k table (champion / hold, ex-best / ex-worst / ex-both):

| k | Champion ex-best | ex-worst | ex-both | Hold ex-best | ex-worst | ex-both |
|---|---|---|---|---|---|---|
| 5 | +210.1% | +364.2% | +287.1% | +393.6% | +3154.6% | +1454.8% |
| 10 | +207.1% | +373.2% | +290.7% | +181.6% | +6027.8% | +1570.2% |
| 20 | +207.1% | +373.2% | +290.7% | +40.7% | +9599.8% | +1416.9% |

(Per-cell Sharpes in `results/phase17_output.txt`.) Champion top-20 rows equal top-10
rows because the champion was in-market on only 12 Definition-A shock days; ranks
beyond that are flat days.

### Definition B (3σ of rolling 30d vol)

| Series | Total ret | Sharpe | ex ALL shock | ex-top10-best shock | top-10-best log-share |
|---|---|---|---|---|---|
| Champion | +271.8% | 1.11 | +139.5% / Sh 0.90 | +107.1% / Sh 0.70 | **+44.6%** |
| BTC hold | +933.2% | 0.91 | +799.6% / Sh 0.94 | +216.7% / Sh 0.61 | **+50.6%** |

### Strategy-own top-day concentration (any day, not just shock days)

| k best days removed | Champion total (log-share of best-k) | BTC hold total (log-share) |
|---|---|---|
| 5 | +167.6% (25.0%) | +393.6% (31.6%) |
| 10 | +107.1% (44.6%) | +181.6% (55.7%) |
| 20 | +30.7% (79.6%) | +3.6% (98.5%) |

### Interpretation

1. **Trigger A does not fire, decisively.** Under both definitions the champion is
   LESS dependent on positive shock days than its own underlying — under the static
   Definition A the gap is 41pp in the champion's favor, and its shock days are net
   negative in aggregate (log-share −3.8%). Shock concentration here is a property of
   the asset class, and the champion carries less of it than the asset.
2. **The Definition-B number (44.6% from top-10 positive shocks; 33.5% of log-P&L from
   all 78 shock days) deserves honest framing rather than alarm.** It sits just under
   the 50% warning line and reflects two structural facts: (a) trend-following P&L is
   fat-tail-concentrated by design (Kaufman's own explanation of why trend following
   works — the edge IS the few large winners); (b) the champion is only ever in the
   market during confirmed uptrends, where 3σ days skew positive, and is flat in
   crash regimes — so its shock exposure is asymmetric in the favorable direction.
   That is the regime-avoidance mechanism operating as documented, not an
   unrepeatable-event artifact. The comparison baseline confirms it: BTC hold gets
   MORE of its P&L from fewer shock days while also eating the negative ones
   (hold ex-worst-10 = +6028% vs its actual +933%).
3. **The 25%/44.6%/79.6% own-top-day concentration ladder is the quantitative version
   of an already-documented limitation** ("most return arrives in a few sustained
   trend legs") and is milder than the underlying's own ladder (31.6%/55.7%/98.5%).
4. The forward-expectation band (5–15% CAGR at ~20% DD) is NOT re-argued or lowered —
   the trigger condition for that action did not occur.

## 4. Diagnostic 2 — walk-forward window-stability

OOS region = second half of the daily stream (2023-03-15 → 2026-05-27), same region
the recorded 4-window walk-forward used. No re-fitting (nothing to re-fit).

| Config | Windows positive | Window Sharpes | Worst Sh | Spread | Verdict |
|---|---|---|---|---|---|
| 3 windows | **3/3** | +1.91 +0.21 +0.67 | +0.21 | 1.70 | majority-pos |
| 4 windows (recorded) | **3/4** | +1.52 +1.06 +1.85 −0.60 | −0.60 | 2.45 | majority-pos |
| 5 windows | **4/5** | +0.78 +2.23 +0.43 +2.11 −1.56 | −1.56 | 3.79 | majority-pos |
| 6 windows | **3/6** | +0.10 +3.07 −1.69 +1.15 +0.94 +0.00 | −1.69 | 4.76 | MINORITY-pos |

Trigger B fires at ≥2 minority-positive configurations; observed: **1 of 4 → does NOT
fire.** The single minority configuration (6 windows) merits a footnote rather than a
downgrade: its last window (2025-11-14 → 2026-05-27) has **zero in-market days**
(return exactly 0.0%) — the gate was out of the market the whole period, which is the
strategy's designed bear behavior, not a loss; counted as flat-not-positive, the
6-window verdict is 3 positive / 2 negative / 1 flat.

Where the losses actually live (window spans in
`results/phase17_validator_audit.json`): two distinct weak stretches, both already
regime-documented, neither an artifact of one boundary choice —

- **The 2024-04 → 2024-10 chop**: −8.9% when isolated (k=6); drags the k=3 middle
  window (2024-04 → 2025-05) to near-flat +2.3%; absorbed into positive windows at
  k=4/5.
- **The late-2025 trend break (~2025-10 → 2025-11)**: the k=4 (−7.6%, 2025-08 →
  2026-05) and k=5 (−11.7%, 2025-10 → 2026-05) negative windows are the same episode
  — the k=6 split shows the loss is concentrated before 2025-11-14 (2025-05 → 2025-11
  window +11.3%, then zero in-market days after). This is the recorded 4th-window
  walk-forward weakness, now localized to a single gate-exit episode rather than a
  general recent decay.

Rolling 18-month Sharpe (monthly step, 61 evaluations, first ending 2021-05-31):

- median **1.14**, max 2.37, min **+0.01** (18 months ending **2022-11-30** — the 2022
  bear year plus the mid-2021 chop, where the gate spent most days flat).
- **Share of evaluations with negative trailing Sharpe: 0.0%.** The champion's daily
  stream has never had a negative trailing 18-month Sharpe on this window — the
  continuous version of the walk-forward question agrees with the windowed one.

## 5. Diagnostic 3 — average-of-all-tests family context

Sources: 61 recorded verdict JSONs (`results/*.json`, 2026-06-11 search — read, not
re-run) + 4 extended-session TVT-family variants whose numbers are documented in
`BEST_STRATEGY_REPORT.md` / `SESSION_2026-06-11_FINAL_SUMMARY.md` (trend-only 1.25,
vol-target-only 0.97, 9-asset+portvol 1.10/0.23, hybrid-satellites 1.28/0.12).
Champion recorded figures used: full-window (harness) 1.33, TEST 0.41.

| Metric | n family | mean | median | max | min | champion | rank / pctile |
|---|---|---|---|---|---|---|---|
| Full-window Sharpe | 65 | **0.537** | 0.74 | 1.28 | −3.86 | 1.33 | **1 / 100.0** |
| TEST Sharpe | 63 | **−0.628** | −0.372 | 1.72 | −6.88 | 0.41 | **13 / 81.0** |

Recorded-as-ranges only (individual cells not persisted, so not includable as rows):
SMA150-250 × ROC20-40 sweep Sharpe 0.81–1.33; EMA-pair sweep 1.15–1.17; vol-target
30–50% sweep 1.24–1.33 (`BEST_STRATEGY_REPORT.md`). All of these would widen the
family below its recorded mean.

### Interpretation

1. **The champion's headline full-window Sharpe is literally the peak of its search
   family** — rank 1 of 66. This is precisely the situation Kaufman's
   average-of-all-tests convention exists to flag, and it retroactively justifies the
   project's two existing guardrails: the DSR gate (0.626 at n_trials=97 — the peak
   deflated for selection) and the standing rule to headline TEST numbers only.
2. **On TEST Sharpe the champion is NOT the family peak** — 12 of 63 recorded variants
   scored higher. Every one of those 12 was examined (see `results/*.json`): all fail
   the gate stack catastrophically elsewhere (full-window Sharpe 0.00–1.18, max DD
   −32% to −80%, TEST trade counts 0–26 — several "high TEST Sharpe" values ride on
   near-zero-activity splits). The champion was selected on the joint criteria, not on
   the TEST peak — which is the correct selection direction and slightly strengthens
   the case that its TEST 0.41 wasn't itself cherry-picked.
3. **The honest average-of-all-tests summary for the record**: the family the champion
   came from averaged NEGATIVE out-of-sample (mean TEST Sharpe −0.63, median −0.37).
   The champion sits at the 81st percentile of a family whose central tendency is
   "no edge." This is exactly what the DSR already prices (63% probability of real
   edge), now stated in Kaufman's preferred form.
4. **Comparability caveat (recorded honestly)**: the 61 JSON verdicts are single-asset
   BTC spot constructs on an 8.4y window with full-size {−1,0,1} positions; the
   champion figures are BTC+ETH vol-sized basket numbers. Family statistics mix these
   conventions because that is what the historical record contains. The ranking
   statement (peak full-window / 81st-pctile TEST) is robust to this; the exact
   percentile is not precision-grade.

## 6. validator.py changes (deliverable 1)

Added, all reusable and reporting-only (the pass bar is unchanged):

- `shock_day_mask(underlying_returns, method="p99"|"3sigma", ...)` — pre-declared
  shock-day definitions on underlying returns.
- `shock_pnl_decomposition(strategy_returns, shock_mask, top_ks=(5,10,20))` — full
  Kaufman removal-convention decomposition with exact log-P&L shares.
- `top_day_concentration(strategy_returns, ...)` — strategy-own top-day ladder.
- `wf_window_stability(strategy_returns, window_counts=(3,4,5,6), oos_start_frac=0.5)`
  — boundary-sensitivity diagnostic.
- `rolling_sharpe_series(strategy_returns, window_days=548)` — trailing 18-month
  Sharpe at monthly steps.
- `family_context(...)` + `family_from_results_dir(...)` + new
  `Verdict.family_context` field; `validate()` accepts an optional `family` argument
  (default None — existing API and behavior unchanged). `print_verdict` prints the
  family line when present.

No bug in existing validator.py behavior was revealed by the diagnostics (the
4-window walk-forward reproduction matched the recorded numbers exactly). One piece
of pre-existing dead code (`m_tr = ... if False else None` in `validate()`) was noted
but not touched — it is inert, and this assignment changes behavior only for bugs.

## 7. Verdict against the pre-registered interpretation rules

| Rule | Outcome |
|---|---|
| Downgrade trigger A (shock dependence >50% AND more than hold by >10pp) | **Does NOT fire** (14.6% vs 55.7% Def A; 44.6% vs 50.6% Def B) |
| Downgrade trigger B (minority-positive at ≥2 of 4 WF configs) | **Does NOT fire** (1 of 4; that one includes an all-flat window) |
| Forward-expectation band 5–15% CAGR | Unchanged (trigger condition absent) |
| "Passed walk-forward" claim | Stands, now with boundary-stability evidence attached |
| n_trials | **97, unchanged** |
| Champion / best_strategy_so_far.py | **Untouched** |

The champion's documented confidence is ADJUSTED UPWARD in two specific, bounded ways
(recorded in `current_champion.md`): (a) it is less shock-dependent than its
underlying, with shock-day exposure asymmetric in the favorable direction by
mechanism; (b) its walk-forward conclusion is boundary-stable and its trailing
18-month Sharpe never went negative. And it is CONTEXTUALIZED DOWNWARD in one way:
its full-window headline was the peak of a 65-variant family whose mean OOS
performance was negative — the DSR number (0.626) remains the honest single-figure
summary of what that implies.

## 8. Ideas parked (NOT tested, recorded per protocol)

1. The 2024-04→2024-10 whipsaw window is negative when isolated (k=6) and drags the
   k=3 middle window to near-flat. Any future anti-whipsaw filter idea (e.g., a chop
   detector suppressing entries)
   would be a new OHLCV signal construct — the family with 95+ failures — and would
   need to survive the mandatory whipsaw/activity pre-gates before spending a trial.
   Parked, not endorsed.
2. Definition-B shock share (44.6%) suggests a cheap future MONITORING metric for the
   dry-run: track the live stream's shock-day log-share against the backtest's as a
   drift indicator. This is instrumentation, not a strategy change; it could be added
   to the monthly dry-run-vs-backtest comparison at zero trial cost.

## 9. Lessons

1. **The champion's shock profile is the opposite of the failure mode Kaufman warns
   about**: shock days hurt it slightly (Definition A) or feed it asymmetrically
   through its designed bear-avoidance (Definition B), and in both cases less than
   buy-and-hold. "Profit concentrated in a few outlier days" describes the ASSET here
   more than the strategy.
2. **Walk-forward verdicts on this stream are boundary-stable**, and the continuous
   (rolling-Sharpe) formulation agrees with the windowed one. The window-stability
   lens also LOCALIZED the recent weakness: it is two specific episodes (the 2024-04→10
   chop and a single gate-exit loss around 2025-10→11) rather than a general recent
   decay — real and regime-shaped, not an artifact of one window boundary.
3. **Counting all-flat windows as "not positive" can flip a window-majority verdict**
   for a strategy whose design includes long flat periods (k=6 here). Future WF
   reporting should distinguish flat-by-design windows from losing windows; the new
   `wf_window_stability` output includes per-window returns so this is visible.
4. **Average-of-all-tests reporting is now permanent** (`Verdict.family_context`).
   The audit confirmed why it matters: the full-window headline was the family peak,
   and the family's mean OOS was negative. Peak-reporting without this context (or
   without DSR) would have materially overstated the evidence.

Standing rule unchanged: **dry-run only, no real capital on backtest evidence.**
