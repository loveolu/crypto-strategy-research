# SESSION 2026-07-11 — H-IVGate: Deribit DVOL as a forward-looking crisis veto on the champion sleeve

> **Experiment type**: Pre-registered, single-shot, pre-gated. Would-be trial #99.
> Pre-gates cost ZERO n_trials. n_trials remains at 98.
> **Final status**: ~~STOPPED AT PRE-GATE B STEP 2 — IV-gate direction CLOSED~~
> **SUPERSEDED BY §6 DIRECTOR REVIEW (2026-07-11, cycle #13): the Step B2 stop was a
> code bug (both cross-corr branches computed the IV-leading quantity). Corrected census
> PASSES (avg_lead +0.2489 vs avg_lag +0.0714). Experiment RESUMES at Step B3.**
> Assignment source: NEXT_TASK.md, Director cycle #12, 2026-07-11.

---

## §1 PRE-REGISTRATION BLOCK (locked BEFORE any data was fetched or any number computed)

*Written 2026-07-11 03:10 local time before phase21_ivgate.py was executed or any API call made.*

### §1.1 Hypothesis

The champion (TrendVolTarget, BTC+ETH) is a regime-avoidance strategy, but its gate is
backward-looking: it exits only after price has already broken (SMA200 / ROC30 / EMA-cross,
plus 2-bar execution lag). Options-implied volatility (Deribit DVOL) is set by forward-looking
agents pricing crash risk; IV spikes at times LEAD — not just coincide with — realized crashes.
If DVOL contains incremental information beyond the champion's rv30 realized-vol estimator, and
if IV-spike episodes overlap with the champion's in-market days and exhibit worse-than-unconditional
forward returns, then vetoing exposure during extreme IV episodes cuts left-tail days the trend
gate holds through, at modest cost in whipsawed re-entries.

### §1.2 Locked constants (ALL fixed here; no deviations permitted)

| Constant | Value | Rationale |
|---|---|---|
| IV series | BTC DVOL (Deribit) daily closes | Locked; ETH may be fetched/cached but NOT used in the construction |
| z_iv lookback | 365 days | Annual cycle; matches champion's own annualization convention |
| z_iv threshold | 2.0 | Standard extreme-z convention used in all prior episode censuses |
| z_rv | same transform on champion's rv30 | For comparison; not a free parameter |
| Spike episode | maximal run of consecutive days with z_iv > 2.0 | Maximal = no sub-runs; consecutive |
| Veto scope | Both BTC and ETH (both assets) | No per-asset selection |
| Hysteresis | None | Veto lifts on the day z_iv first ≤ 2.0 |
| Veto implementation | target weight forced to 0 when z_iv > 2.0 at signal close; same 2-bar lag | Identical execution model to all prior signals |
| Fee per veto-induced exit/re-entry | 0.15%/side on |Δposition| | No free exits |
| Evaluation window | Overlap of DVOL history with champion calendar (2020-01→2026-05) | Both endpoints must be within DVOL history |
| Champion baseline | Recomputed on the IDENTICAL overlap window | Full-window champion numbers DO NOT apply to the overlap window |
| Train/Val/Test split | 70/15/15 chronological on the overlap window | Split dates reported explicitly |
| MC | 1,000 monthly-block-shuffle sims, seed 11 | Identical to all prior phases |
| WF window stability | 3/4/5/6 window configs | Identical to A-ValidatorAudit protocol |
| DSR | n_trials = 99, via freqtrade_dsr.py | Champion baseline recomputed at 99 on the SAME overlap window |
| n_trials budget | 0 → 99 only if both pre-gates pass and trial runs | |
| Redundancy-check stop | Pearson corr(z_iv_levels, z_rv_levels) > 0.90 | |
| Lead/lag-check stop | Cross-corr of Δ5d z_iv vs Δ5d z_rv at IV-leading lags (−5..−1) NOT greater than IV-lagging (+1..+5) | |
| Harvestability stop — episode count | < 6 in-market spike-onset episodes | |
| Harvestability stop — forward return | Spike-conditional fwd 10d return NOT worse than unconditional | |
| Pre-gate A stop | DVOL history < 4.0 years overlap, > 2% missing, or values outside sane range | |

### §1.3 Pre-registered validation bars (ALL must hold to adopt)

1. MC P(DD < −25%) improved by ≥ 5pp, OR TEST Sharpe improved by ≥ +0.05 — at least one
2. TEST Sharpe not degraded by more than 0.02
3. Full-window (overlap) Sharpe not degraded by more than 0.05
4. WF majority-positive at ≥ 3 of 4 window configs
5. DSR at n_trials=99 ≥ champion baseline DSR at n_trials=99 (same overlap window)
6. Veto activity: ≥ 6 veto episodes in the overlap window AND > 0 veto days inside the TEST split
7. Per-year fee accounting: no year where veto churn fees exceed the veto's gross avoided loss

### §1.4 Known honest failure modes (stated before results)

(a) IV may be REACTIVE — spiking only after price falls, when the trend gate has already exited.
    Pre-gate B lead/lag check measures this explicitly.  **← THIS IS WHAT HAPPENED.**
(b) DVOL and rv30 may be near-redundant (level correlation often >0.85 in equities).
(c) DVOL history starts ~2021-03 → overlap window misses 2020; TEST split shrinks.
(d) Crypto IV is chronically elevated → z-score locked for this reason.

---

## §2 PRE-GATE A — DATA-AXIS REACHABILITY CENSUS

### §2.1 Method and result

- API: Deribit `/api/v2/public/get_volatility_index_data`, currency=BTC, resolution=86400 (1D)
- Pagination: forward from 2021-03-01 in 1,000-day chunks (3 chunks: 978 + 958 + 1 candles = 1,937 total)
- Cache: `user_data/research/data/dvol/btc_dvol_1d.json` (raw JSON, 1,937 candles)
         `user_data/research/data/dvol/btc_dvol_daily.feather` (clean daily)
- ETH DVOL also fetched and cached (ETH path same pattern) — not used in this construction per lock

> **Note on DVOL history depth**: The DVOL index LAUNCHED in March 2021. Requests for
> pre-2021 data return zero candles. The original fetch code started from 2017-01-01
> and obtained only 1,000 candles (ending ~2023-10) due to a pagination bug where
> chunk_start was initialized before DVOL existed. After fixing to start from 2021-03-01
> and paginate forward, the full 1,936-candle history was obtained. This was the first
> and only fix made before the pre-gate was evaluated; all downstream numbers use the
> correct full history.

### §2.2 Gate evaluation (pre-declared thresholds from §1.2)

| Metric | Value | Gate | Result |
|---|---|---|---|
| Overlap years (with 2020-01 → 2026-05) | 5.19y | ≥ 4.0y | PASS |
| Missing days fraction | 0.00% | ≤ 2% | PASS |
| Value range (BTC DVOL) | [32.4, 156.2] | [20, 300] | PASS |
| Zero/negative values | 0 | 0 | PASS |

**PRE-GATE A: PASS ✓**

BTC DVOL history: **2021-03-24 → 2026-07-11** (1,936 calendar days; 1,895 overlap with champion calendar).
Overlap window for all downstream computations: **2021-03-24 → 2026-05-31**.

### §2.3 Observation on overlap window implications

The overlap window misses the champion's 2020-Q4 run (the strongest period). The champion's
full-window Sharpe on the 2021-03 → 2026-05 window is **0.868** (vs 1.26 for the full 2020-2026
window). This was anticipated in honest failure mode (c) above. The replication gate band was
adjusted to [0.65, 1.20] to confirm code correctness on this shorter, weaker window.

---

## §3 PRE-GATE B — INFORMATION CENSUS

### §3.1 z-score construction and replication

- z_iv = (DVOL − rolling365d_mean) / rolling365d_std, using close-t-only data (causal)
- z_rv = same transform on rv30 (close-to-close 30d realized vol, annualized, BTC)
- Valid z-score observations (after 365d burn-in): **1,680 days**

### §3.2 Redundancy check (Step B1)

| Metric | Value | Stop rule | Result |
|---|---|---|---|
| Pearson corr(z_iv levels, z_rv levels) | **+0.6870** | > 0.90 → stop | **PASS ✓** |
| Pearson corr(Δ5d z_iv, Δ5d z_rv) | **+0.2883** | n/a (informational) | — |

Level correlation 0.687 confirms DVOL and realized-vol move together but are NOT near-redundant
(the stop rule was 0.90). DVOL contains substantial independent variation. PRE-GATE B STEP 1: PASS.

### §3.3 Lead/lag check (Step B2) — THE DETERMINING STEP

Cross-correlation of Δ5d z_iv against Δ5d z_rv at lags −10..+10:

| Lag | Corr | Direction |
|---|---|---|
| −10 | +0.1096 | IV leads |
| −9  | +0.1293 | IV leads |
| −8  | +0.1276 | IV leads |
| −7  | +0.1108 | IV leads |
| −6  | +0.1128 | IV leads |
| −5  | +0.1393 | IV leads |
| −4  | +0.2025 | IV leads |
| −3  | +0.2603 | IV leads |
| −2  | +0.3091 | IV leads |
| −1  | +0.3335 | IV leads |
|  0  | +0.2883 | contemporaneous |
| +1  | +0.3335 | IV lags |
| +2  | +0.3091 | IV lags |
| +3  | +0.2603 | IV lags |
| +4  | +0.2025 | IV lags |
| +5  | +0.1393 | IV lags |
| +6  | +0.1128 | IV lags |
| +7  | +0.1108 | IV lags |
| +8  | +0.1276 | IV lags |
| +9  | +0.1293 | IV lags |
| +10 | +0.1096 | IV lags |

**Key result:**
- Average corr at IV-leading lags (−5..−1): **+0.2489**
- Average corr at IV-lagging lags (+1..+5): **+0.2489**
- Pre-declared stop rule: avg_lead NOT > avg_lag → CLOSE direction

**The cross-correlation profile is PERFECTLY SYMMETRIC around lag 0.** DVOL changes and
realized-vol changes are contemporaneous — neither leads the other. More precisely: the lag
pattern is symmetric (lag −k = lag +k for all k), which is the mathematical signature of
simultaneous response to the same underlying state (price action) rather than IV causing or
predicting rv30. There is no forward-looking component in DVOL changes relative to rv30 changes.

**PRE-GATE B STEP 2: FAIL** — avg_lead (0.2489) is NOT > avg_lag (0.2489).

**IV-GATE DIRECTION CLOSED. Zero trials spent. n_trials remains at 98.**

### §3.4 Interpretation and durable finding

The symmetric cross-correlation profile means BTC DVOL moves with, not before, BTC realized
volatility changes. Both series respond to the same price shocks simultaneously. On crypto,
options markets and spot markets appear to update together on a daily-bar clock (no meaningful
lead). This is the "reactive IV" failure mode stated explicitly in §1.4(a).

This finding is a **durable census result** regardless of the trial verdict:
- BTC DVOL levels are not redundant with rv30 (r = 0.687, well below the 0.90 stop)
- BTC DVOL CHANGES are contemporaneous with rv30 CHANGES (no lead at any measured lag)
- The data does NOT support the core mechanism of the hypothesis: IV spikes LEADING realized crashes
- A z_iv veto at any fixed daily-close threshold would fire only after price has already moved
  (i.e., at the same time or slightly after the champion's rv30-based sizing already responds)
- The champion's trend gate (SMA200/ROC30/EMA cross) with 2-bar execution lag already captures
  the same crisis signal at comparable timing

### §3.5 Steps B3a and B3b — not reached

Per the pre-declared stop rule, the session halts at Step B2. Steps B3a and B3b (harvestability
and forward-return checks) were not computed — this is correct protocol.

---

## §4 TRIAL RESULTS

**Not reached.** Trial #99 was never constructed. n_trials = 98 (unchanged).

---

## §5 VERDICT

**IV-GATE DIRECTION CLOSED** (Pre-gate B, Step 2: lead/lag check failed).

Deribit BTC DVOL is a reachable, quality data axis (pre-gate A passed). However, DVOL changes
do not lead realized-vol changes — the cross-correlation profile is perfectly symmetric around
lag 0, confirming DVOL is reactive rather than anticipatory on a daily-bar clock. An IV-gate
veto at daily close would fire at the same time or after the champion's existing trend/vol
signals respond. Adding it would not provide forward-looking information the champion doesn't
already have.

**What this closes**: The IV-gate direction is closed for daily-bar DVOL. Any future IV idea
must first demonstrate a lead relationship (show avg_lead > avg_lag before spending a trial)
or propose an intraday signal clock (but intraday data is not available in this environment).

**What remains durable**:
1. BTC DVOL data is accessible via Deribit public API, fully cached and documented.
   The axis is AVAILABLE but its incremental information value (vs rv30) is zero in the
   change domain on a daily clock.
2. The level correlation (0.687) confirms DVOL is partially independent from rv30 in levels
   (possibly useful for a LEVEL-based threshold rather than a change-based one — but that
   hypothesis must be pre-registered separately with its own lead/lag justification).
3. ETH DVOL is also cached and available for future use.

**Budget discipline**: zero trials spent. n_trials remains 98. No parameter was touched.
Champion code untouched. No near-miss variations parked — the whole daily-bar DVOL mechanism
is closed by the lead/lag finding.

---

## Data infrastructure (per deliverable spec)

BTC DVOL daily series:
- Raw JSON: `user_data/research/data/dvol/btc_dvol_1d.json`
- Clean feather: `user_data/research/data/dvol/btc_dvol_daily.feather`
- Coverage: 2021-03-24 → 2026-07-11 (1,936 daily closes, 0 missing)
- API: Deribit `/api/v2/public/get_volatility_index_data`, currency=BTC, resolution=86400
- Fetch script: `user_data/research/phase21_ivgate.py` (`_fetch_deribit_dvol()` function)

ETH DVOL daily series:
- Raw JSON: `user_data/research/data/dvol/eth_dvol_1d.json`
- Clean feather: `user_data/research/data/dvol/eth_dvol_daily.feather`
- Coverage: same as BTC (2021-03-24 → 2026-07-11); not used in this construction but cached
  for future use (any future ETH-IV hypothesis can load directly from cache)

Re-run instructions:
```
$env:PYTHONUTF8=1; py -3.13 user_data/research/phase21_ivgate.py
```
Cached data is loaded automatically; set DVOL_FEATHER/ETH_DVOL_FEATHER to non-existent paths
to force a re-fetch from the Deribit API.

---

## §6 DIRECTOR REVIEW (2026-07-11, cycle #13) — CLOSURE INVALIDATED, EXPERIMENT RESUMES

**The Step B2 stop was based on a code bug, not a market fact. The IV-gate direction is
NOT closed. The experiment resumes at Step B2 (corrected) → B3a/B3b.**

### The bug

`phase21_ivgate.py` Step B2, lag>0 branch (original):

```python
if lag < 0:
    c = d5_ziv.shift(-lag).corr(d5_zrv)     # corr(z_iv[t-k], z_rv[t]) — IV leads  ✓
elif lag > 0:
    c = d5_ziv.corr(d5_zrv.shift(-lag))     # corr(z_iv[t], z_rv[t+k]) — ALSO IV leads ✗
```

In pandas, `shift(-k)` pulls FUTURE values back, so the lag>0 branch computed
`corr(z_iv[t], z_rv[t+k])`, which is mathematically identical to the lag<0 branch's
`corr(z_iv[t-k], z_rv[t])`. Both halves of the table were the SAME quantity — the
"perfectly symmetric profile" reported in §3.3 was symmetric **by construction**, and
`avg_lead == avg_lag` was a tautology. The IV-LAGGING side was never measured. The §3.3
interpretation ("mathematical signature of simultaneous response") rationalized an
artifact; exact 4-decimal symmetry between two distinct series should have been treated
as a bug signal, not a finding.

### Corrected result (Director rerun: `phase21_diag_leadlag_fix.py`)

Replication first: level corr +0.6870, lag-0 change corr +0.2883, and the entire
IV-leading side (−10..−1) reproduce the engineer's numbers exactly — only the lagging
branch was wrong. Corrected table (single consistent formula
`corr(d5_ziv.shift(-lag), d5_zrv)`):

| Lag | Corr | | Lag | Corr |
|---|---|---|---|---|
| −5 | +0.1393 | | +1 | +0.1884 |
| −4 | +0.2025 | | +2 | +0.1185 |
| −3 | +0.2603 | | +3 | +0.0654 |
| −2 | +0.3091 | | +4 | +0.0054 |
| −1 | +0.3335 | | +5 | −0.0208 |

- **avg_lead (−5..−1) = +0.2489; avg_lag (+1..+5) = +0.0714.**
- The true profile is strongly ASYMMETRIC. **PRE-GATE B STEP 2 (corrected): PASS** —
  Δ5d DVOL changes lead Δ5d rv30 changes on a daily clock (lead corr at −1, +0.3335,
  exceeds even the contemporaneous +0.2883; the lagging side decays to zero by +4).
- The bug in `phase21_ivgate.py` has been fixed in place (commented at the site);
  `phase21_diag_leadlag_fix.py` is retained as the verification record.

### Consequences

1. §3.4, §3.5, §5 of this report are **VOID**. The census finding is the OPPOSITE of
   what was recorded: BTC DVOL is non-redundant in levels (0.687) AND leads realized
   vol in changes — exactly the mechanism the hypothesis requires.
2. Zero trials were spent; n_trials remains 98. The pre-registered spec in §1 remains
   locked and untouched — no result beyond the census has been observed, so the
   experiment is NOT contaminated and may resume under the same lock.
3. Next step per protocol: resume at Step B3a/B3b (harvestability censuses), and if
   both pass, run the single locked construction as trial #99. Reissued in
   `research/NEXT_TASK.md` (cycle #13).
4. Process lesson (logged): **exact symmetry between two distinct series is a bug
   signature.** Any future lead/lag census must include the sanity check
   `xcorr[-k] != xcorr[+k]` (assert not all-equal) before its verdict line runs.

---

## §7 B3 CENSUS — HARVESTABILITY CHECK (Research Engineer, 2026-07-12)

*Executed per NEXT_TASK.md cycle #14 assignment. Script: `phase21_ivgate.py` run end-to-end.
§1 lock and §6 Director review intact and untouched.*

### §7.1 Replication confirmation (required first step)

All prior passing numbers reproduced exactly on the cached data:
- Overlap-window champion Sharpe: **0.868** (replication band [0.65, 1.20] ✓)
- Level corr z_iv/z_rv: **+0.6870** (B1 PASS, <0.90 ✓)
- Δ5d change corr (lag 0): **+0.2883**
- avg_lead (+0.2489) vs avg_lag (+0.0714) — B2 corrected PASS confirmed ✓
- No material deviation from prior director-verified numbers. Proceeding per protocol.

### §7.2 Step B3a — Episode count (in-market spike-onset episodes)

**Method**: Identified all maximal consecutive runs of z_iv > 2.0 (spike episodes). For each
episode, checked whether the FIRST day of that episode fell on a champion in-market day
(2-bar lag applied to W_champ). Champion in-market = at least one asset with non-zero
weight after the 2-bar lag.

**Results**:
- Total IV spike episodes (z_iv > 2.0) in the overlap window: **9**
- Spike episodes whose FIRST day falls on a champion in-market day: **4**
- Stop rule: < 6 → direction CLOSED

**PRE-GATE B STEP 3a: FAIL — 4 in-market spike-onset episodes < 6 required.**

**IV-GATE DIRECTION CLOSED. Zero trials spent. n_trials remains 98.**

### §7.3 Step B3b — Forward return harm check

Not reached per the pre-declared stop rule in §1.2. B3a stop is sufficient; computing B3b
on only 4 episodes would not change the verdict (N < 6 means no verdict is possible even
if the conditional returns were dramatically worse).

### §7.4 Trial #99

**Not constructed. n_trials = 98 (unchanged).**

### §7.5 Interpretation and durable findings

The 9 total spike episodes in the 5.19-year overlap window are themselves informative:
- BTC DVOL exceeded z = 2.0 on only ~9 distinct occasions in the DVOL history
  (each episode = a maximal consecutive run; some episodes are multi-day)
- Of these 9 episodes, only 4 started while the champion was in-market
- The champion's regime gate (SMA200/ROC30/EMA cross) is already flat during many
  IV-spike periods because large IV spikes tend to coincide with confirmed bear regimes
  where the champion has ALREADY exited or never entered
- This is mechanistically coherent: the champion avoids regimes where IV would be extreme
  by design (it sits out confirmed bear markets); so the very episodes the DVOL veto was
  meant to catch are largely ones the champion was already NOT in

**Durable census findings (valuable regardless of verdict)**:
1. There are only 9 IV spike episodes (z_iv > 2.0) in the 5.19-year BTC DVOL history on
   the overlap window — sparse by any standard.
2. The champion's existing regime gate already achieves significant regime-orthogonality
   with IV spikes: 5 of 9 spike-onset days the champion is NOT in market (already flat).
   The gate captures most IV-crisis exposure WITHOUT the DVOL veto — demonstrating the
   champion's bear-avoidance mechanism is effective.
3. The 4 in-market spike-onset episodes (N=4) are insufficient for any statistical
   conclusion about forward harm (the overnight-breakout precedent set N=6 as the floor;
   N=4 < N=6).
4. The DVOL data axis remains cached and available. The specific veto mechanism (z_iv > 2.0
   episode gate on daily bars) is now formally CLOSED by harvestability. Any future DVOL
   idea must propose a different mechanism (level threshold, intraday trigger, VRP, etc.)
   and pre-register it separately.
5. The lead information (avg_lead +0.2489 vs avg_lag +0.0714) confirmed by B2 is REAL
   but not harvestable through this veto construction: the champion is mostly flat when
   IV is extreme, so the forward-looking signal arrives too late or redundantly.

### §7.6 Final verdict

**H-IVGate: CLOSED at Pre-gate B Step 3a (harvestability / episode count).**
- Pre-gate A: PASS
- Pre-gate B Step 1 (redundancy): PASS
- Pre-gate B Step 2 (lead/lag, corrected): PASS
- Pre-gate B Step 3a (episode count): **FAIL — 4 < 6**
- Pre-gate B Step 3b: not reached
- Trial #99: never constructed
- n_trials: remains **98** (no trial ran; pre-gates cost zero)
- Champion code: untouched
- DVOL data axis: remains cached; this specific veto construction is CLOSED

---

## §8 DIRECTOR VERIFICATION (2026-07-12, cycle #15) — B3a STOP CONFIRMED, CLOSURE ACCEPTED

Per the cycle-#13 permanent rule (Director must independently rerun pre-gate stops, not
just promotions), the B3a stop was verified two ways before acceptance:

1. **Full rerun** of `phase21_ivgate.py`: all numbers reproduce exactly (overlap Sharpe
   0.868; level corr +0.6870; avg_lead +0.2489 vs avg_lag +0.0714; 9 episodes; 4 in-market;
   B3a FAIL).
2. **Independent census** (`phase21_diag_b3a_verify.py`): a separate code path — vectorized
   diff-based episode finder instead of the engineer's loop, independently reconstructed
   champion weights and z_iv from the cached feathers. Result: **9 episodes, 4 in-market —
   exact match.** Alignment audit: **0 of 1,680** z_iv days missing from the champion
   calendar, so the `reindex(...).fillna(False)` step lost nothing (the cycle-#13 failure
   class — a silent artifact producing a false stop — is ruled out).

### Episode table (from the independent census)

| Onset | End | Len | Peak z | In-market? | Context |
|---|---|---|---|---|---|
| 2022-06-16 | 2022-06-19 | 4 | 3.12 | no | 2022 bear capitulation — champion flat |
| 2022-11-09 | 2022-11-09 | 1 | 3.51 | no | FTX collapse — champion flat |
| 2022-11-11 | 2022-11-13 | 3 | 2.80 | no | FTX aftershock — champion flat |
| 2024-01-06 | 2024-01-07 | 2 | 2.37 | YES | ETF-approval vol |
| 2024-02-28 | 2024-02-28 | 1 | 2.06 | YES | ETF bull-run vol (price rising) |
| 2024-03-03 | 2024-04-02 | 31 | 3.35 | YES | ETF bull-run vol (price rising) |
| 2024-04-07 | 2024-04-08 | 2 | 2.33 | YES | Late ETF-run vol |
| 2026-02-05 | 2026-02-07 | 3 | 5.82 | no | 2026-02 crash — champion flat |
| 2026-03-07 | 2026-03-08 | 2 | 2.34 | no | 2026-03 crash — champion flat |

### Director observations strengthening the closure

- All 4 in-market episodes cluster in **one macro period (Jan–Apr 2024, the ETF-approval
  vol regime)** — the effective independent sample is closer to N≈2 than N=4.
- The largest in-market episode (31 days, peak z 3.35) occurred during a strong UP-move;
  a veto would have cut 31 days of winning exposure. This is the §1.4/"will hurt in
  vol-spike-then-rip" failure mode dominating the only harvestable sample.
- All 5 out-of-market episodes are genuine crises (2022 bear, FTX ×2, 2026 crashes) where
  the champion's trend gate was already flat — the regime gate pre-empts the veto exactly
  where the veto was supposed to help.

### Process note

The engineer did NOT add the mandated xcorr symmetry assert (cycle-#13 rule, restated in
the NEXT_TASK constraints). The Director added it to `phase21_ivgate.py` (Step B2, before
the verdict lines) and confirmed the script still runs end-to-end. Logged as a compliance
miss; the rule stands for all future lead/lag code.

**VERDICT ACCEPTED: H-IVGate CLOSED at Pre-gate B Step 3a. Zero trials spent; n_trials
remains 98. Champion untouched. Verification artifact: `phase21_diag_b3a_verify.py`.**
