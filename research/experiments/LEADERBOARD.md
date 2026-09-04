# Strategy leaderboard (goal framework) — updated 2026-09-04 after CRYPTO-EXP-010

Composite ranking per the goal: net ann. return, Sharpe/Sortino, DD, PF, **recent**, OOS, robustness,
parameter stability, cost sensitivity, sample size — never raw return alone. A-011 measured costs,
unleveraged. **OOS = VAL+TEST+FWD (2024-11-23 → 2026-09-01, 21 months), thresholds set on TRAIN only.**

| # | strategy | status | tf | OOS net | OOS ann. | OOS Sh | OOS DD | OOS PF | OOS n | /day | last 365d | robustness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **S2-strict-4h, 9 perps** (W42 PW180 HOLD6, mom_24h ≤ −3.85%) | **Promising** | **4h** | **+27.5%** | **~15%** | **1.31** | −10.4% | **1.87** | 170 | 0.26 | **−6.7%** | cost ✓ (Sh 1.05 @3×) · params ✓ (all +, THR peaks at base ⚑) · **top-5% ✓ (+10.8%)** · coins 7/9 · **delay ✗ (must act at 4h close)** · recent ✗ · FWD ✗ |
| 2 | S2-strict, 9 perps (mom_24 ≤ −2.73%) | Testing | 1h | **+12.8%** | ~7.1% | 0.83 | −12.6% | 1.32 | 220 | 0.35 | **−11.6%** | cost ✓ (Sh 0.61 @2×) · params ✓ · delay ✓ · **recent ✗ · top-5% ✗ · FWD ✗** |
| 3 | S2-strict, 5 perps (≤ −2.37%) | Testing | 1h | +9.6% | ~5.4% | 0.71 | −8.7% | 1.28 | 133 | 0.21 | −7.2% | same profile, lower DD |
| 4 | S5-V5 beta-neutral spread | Testing | 1h | +7.2% (TEST+FWD) | ~5% | — | −20% | — | 43 entries | 0.03 | — | only construct positive in FWD; a hedge |
| 5 | S2 loose, 9 perps | Testing | 1h | +4.2% | ~2.4% | 0.31 | −15.0% | 1.09 | 315 | 0.50 | −9.9% | superseded by strict |
| 6 | S3 gated vol-target basket | Testing (daily — outside 1m–4h scope) | 1d | −6.7% (TEST+FWD) | — | — | −30% | — | ~30 | 0.03 | — | beats A-005 full-cycle; vol-target helps at daily |
| — | S2 loose, 5 perps (original) | Superseded | 1h | −3.1% | — | −0.17 | −10.8% | 0.96 | 197 | 0.30 | −5.9% | in-sample Sh 1.33 did not transfer |
| — | S2-strict + SMA200-rising gate | **Rejected** (EXP-008) | 1h | +9.5% | — | 0.72 | −10.0% | 1.32 | 152 | — | −9.5% | cuts TEST, barely helps FWD |
| — | S1 ungated · S2 short mirror · MAR rotation · RS switch · rebal-freq · S5 base | **Rejected** | — | — | — | — | — | — | — | — | — | EXP-004/005 |

**Reference:** A-005 equal-weight monthly basket — OOS (same 21 months) ≈ −45%, DD −71%.

**No strategy is Candidate; one is Promising.** S2-strict-4h-9 clears cost, parameters, coin breadth
and — unlike the 1h version — top-trade removal, and annualises ≈15% OOS, inside the goal band. It
fails recent performance (−6.7% last 365d, all recent trades from one month) and requires execution at
the 4h close (edge gone by 8h). **Promotion gate to Candidate: positive rolling 90-day PF on forward
paper data for two consecutive quarters.** ≈ 45 constructs examined on the 2023→2026 data; no
further variants of this family on seen data.
