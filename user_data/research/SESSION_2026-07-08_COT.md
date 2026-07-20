# Session 2026-07-08 — H-COT: CFTC positioning crowding filter on TrendVolTarget

Pre-registered experiment, **trial #96** in the project's cumulative DSR ledger.
ONE feature, ONE rule, no variants tested. Script: `phase14_cot.py`.
New data axis: CFTC Traders-in-Financial-Futures (Futures Only) via Socrata
(`publicreporting.cftc.gov/resource/gpe5-46if.json`) — first non-blocked
external data source in the project.

## 1. Hypothesis and pre-registered spec

**H-COT**: asset-manager crowding in CME Bitcoin futures, used as a de-risking
filter on the champion TrendVolTarget, improves risk-adjusted OOS performance.

- Feature (one): `am_net_frac` = (asset_mgr_positions_long −
  asset_mgr_positions_short) / open_interest_all for BITCOIN - CHICAGO
  MERCANTILE EXCHANGE, z-scored over trailing 52 weekly reports
  (min 26 weeks; no filter before that).
- Rule (one): z > +2 → multiply the champion's quantized vt_scale by 0.5 on
  both legs (hypothesis names *Bitcoin* futures positioning as the crowding
  gauge for the whole champion). Never increases exposure; never touches
  entry/exit.
- Judged primarily on TEST-split Sharpe, TEST max DD, MC P(DD<−25%).
  DSR at n_trials=96.

## 2. Data acquired (deliverable, cached regardless of outcome)

`user_data/research/data/cot/`:

| File | Rows | Coverage |
|---|---|---|
| `BITCOIN_tff_futonly.csv` | 430 weekly reports | 2018-04-10 .. 2026-06-30 |
| `ETHER_CASH_SETTLED_tff_futonly.csv` | 274 weekly reports | 2021-04-06 .. 2026-06-30 |

Note: the CME ETH contract is named `ETHER CASH SETTLED` in the dataset
(plain `ETHER` returns 0 rows). ETH COT was cached but not used by the
pre-registered rule.

## 3. Timing hygiene (no lookahead)

COT `report_date` is the Tuesday the data is AS OF; public release is the
following Friday ~15:30 ET. Each report's z becomes usable only from
**report_date + 6 calendar days** (the following Monday), then forward-filled
daily until the next report's effective date. On top of that the harness
applies its standard 2-bar execution lag. **Each COT value is therefore 6–12
days stale when it first affects the signal, plus 2 more days to execution
(8–14 days total).** Verified: no z value is referenced before its effective
date.

## 4. Baseline replication check — PASSED

Harness (phase11/13 convention: BTC+ETH futures feathers, fees 0.15%/side,
2-bar lag, quantized vol-target weights / 2):

- TEST Sharpe **0.39** (recorded: 0.39–0.41) — exact match to SESSION_2026-07-02.
- MC P(DD<−25%) **28%** (recorded: 28%) — exact match.
- Full-window harness Sharpe 1.11 (the recorded 1.26 is the *real freqtrade
  engine* number; the harness has always printed ~1.1 for this construct —
  same as phase11's per-day series that produced the recorded DSR 0.64).

Baseline valid; filter evaluation proceeded.

## 5. Filter activity

- Weekly reports with z > +2: **28 of 430** (5 in 2019 before OHLCV data;
  Nov 2021–Feb 2022 top; one week Jul 2023; Jan–Apr 2024 ETF run-up;
  one report 2025-12-30).
- Daily bars active: 161 (6.9% of 2,339 bars).
- Active AND champion in-market: **51 of 977 in-market days (5.2%)** —
  above the pre-registered 5% thin-sample floor, but only barely.
  Distribution: 2021: 23d, 2023: 2d, 2024: 26d.
- **Filter-active in-market days inside the TEST split: 0.** The only TEST
  z>+2 episode (2026-01-05..11, from the 2025-12-30 report) fell entirely in
  a flat period (champion had no position). The entire realized effect of the
  filter is in-sample.

## 6. Results

| Metric | Baseline (champion) | + COT filter |
|---|---|---|
| TEST Sharpe | 0.391 | 0.391 (identical — filter never active in-market in TEST) |
| TEST max DD | −16.3% | −16.3% (identical) |
| TEST CAGR | +5.4% | +5.4% (identical) |
| MC P(DD<−25%) | 27.6% | 26.4% (Δ within MC noise, SE≈2% at 500 sims) |
| MC median DD | −22.4% | −22.3% |
| Full Sharpe | 1.11 | 1.09 |
| Full max DD | −16.9% | **−20.3% (worse)** |
| Full CAGR | +22.7% | +21.7% |
| Walk-forward Sharpes | +1.52 +1.06 +1.85 −0.60 (3/4 pos) | +1.53 **+0.57** +1.85 −0.60 (3/4 pos) |

Where the filter actually fired, it hurt: both variants' max DD is the
Mar→Oct 2024 episode, and the filter made it *deeper* (−20.3% vs −16.9%)
because the Jan–Apr 2024 crowding episode expired *before* the actual
drawdown — it halved exposure during the tail of the ETF rally, then restored
full exposure in time for the decline. WF window 2 (covering 2024) dropped
from 1.06 to 0.57 for the same reason. The Nov 2021 episode (where de-risking
should have helped) did not compensate.

## 7. Deflated Sharpe Ratio (per-day returns, n_trials=96)

| Series | DSR | Bar |
|---|---|---|
| Champion baseline (reference) | 0.627 | 0.95 |
| **Champion + COT filter (this trial)** | **0.603** | 0.95 |

The filtered variant is *further* from the bar than the unfiltered champion.

## 8. Verdict: **REJECT**

The pre-registered win condition (improved risk-adjusted TEST performance)
is not met and *cannot* be met by this rule on this data: the filter was
never active while in-market during the TEST split (0 days), so its OOS
evidence is nil — and its entire in-sample effect was negative (deeper
realized max DD, weaker 2024 walk-forward window, lower full Sharpe, lower
DSR). The one nominally favorable number (MC P(DD<−25%) 26.4% vs 27.6%) is
inside Monte Carlo noise. The champion remains unchanged.

Sub-caveat recorded honestly: overall in-market activity (5.2%) cleared the
pre-registered 5% floor, so this is a REJECT, not INCONCLUSIVE — but the
TEST-split activity being exactly zero means a future re-test after more
forward data accumulates would not be double-dipping on the same evidence.

## 9. Lessons

1. **CFTC COT is a working, cached, free data axis** (the first external
   source that isn't geo-blocked). 430 weeks of BTC, 274 of ETH now stored
   locally; future hypotheses can use it without re-download.
2. Asset-manager crowding at z>+2 is a *bull-market-top* phenomenon
   (Nov 2021, Jan–Apr 2024). The champion is already long in those periods
   by construction, so the filter mostly just taxes rallies; the crowding
   signal decayed before the actual 2024 drawdown arrived. Positioning
   extremes here were early by ~6 months.
3. Weekly data + 6-day release lag + trend-following holding periods leaves
   very few actionable overlaps: 51 affected days in 6.4 years. COT-based
   overlays on a slow trend system are structurally low-sample; any future
   COT hypothesis should target constructs where it can fire more often
   (or accept multi-year evidence accumulation).
4. n_trials is now **96**. The champion's DSR at 96 is 0.627.

Standing rule unchanged: **dry-run only, no real capital on backtest evidence.**
