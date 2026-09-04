# A-013 — Operator reference bar (S5) + improvement variants + full-cycle record for all candidates (2026-09-04)

**Operator-directed. Zero trials.** Instruction: designate S5's +3.67% as the bar to beat, then improve it
or find better. Scripts: `user_data/research/s5_spread.py` (S5 core, variants as parameters),
`user_data/research/a013_variants.py` (in-sample runner). Costs: A-011 measured per-instrument taker.
Windows: TRAIN 2023-01-22 → 2024-11-22 (all nine present + 720-bar warmup), VAL → 2025-04-21,
TEST → 2025-09-19, FWD 2025-09-20 → 2026-09-01 (the A-012 spent year).

## 1. S5 base — full record (the designated bar)

| window | return | ann. | MaxDD | Sharpe |
|---|---|---|---|---|
| TRAIN | **−22.42%** | −12.9% | −32.0% | −1.01 |
| VAL | **−15.52%** | −33.7% | −16.7% | −2.25 |
| TEST | +8.49% | +21.8% | −2.6% | +2.63 |
| FWD | +3.46% | +3.7% | −7.1% | +0.39 |

By year: 2023 −3.8% · **2024 −25.0%** · 2025 +3.5% · 2026 −2.7% → **≈ −27% full cycle.** The +3.67%
was best-of-five on one crash year. Unconditionally ("always on") the spread is −26.6% on TRAIN+VAL:
it is a pure timing bet on cascades and loses in alt-season.

## 2. Pre-registered variants, TRAIN+VAL only (in-sample development; TEST withheld)

| variant | TRAIN ret / DD / Sh | VAL ret / DD / Sh | T+V ret / DD / Sh | 2023 | 2024 |
|---|---|---|---|---|---|
| base | −22.4 / −32.0 / −1.01 | −15.5 / −16.7 / −2.25 | −34.5 / −43.1 / −1.29 | −3.8 | −25.1 |
| always (diagnostic) | −15.4 / −31.4 / −0.42 | −13.2 / −13.7 / −1.21 | −26.6 / −39.6 / −0.60 | −14.5 | −5.7 |
| V6 trend-gate (bear only) | −10.7 / −16.6 / −0.73 | −11.4 / −12.6 / −2.39 | −20.8 / −21.9 / −1.13 | −9.5 | −1.2 |
| V2 drop ADA, DOT (cost) | −22.0 / −30.8 / −0.98 | −15.8 / −17.8 / −2.54 | −34.3 / −42.2 / −1.31 | −6.6 | −22.1 |
| V3 hysteresis .90/.40 | −29.9 / −38.9 / −1.41 | −13.2 / −13.0 / −2.09 | −39.1 / −47.0 / −1.55 | −8.5 | −26.7 |
| **V5 beta-neutral** | **+1.3 / −14.5 / +0.12** | −6.2 / −7.9 / −1.54 | **−5.0 / −20.4 / −0.19** | **+6.3** | −4.9 |
| V1 drop BNB (holdout-informed) | −26.9 / −36.4 / −1.13 | −16.3 / −17.7 / −2.08 | −38.8 / −47.5 / −1.34 | −6.0 | −28.5 |
| combo V6+V2+V5 | −12.5 / −17.0 / −1.05 | −8.0 / −9.0 / −2.50 | −19.6 / −20.4 / −1.35 | −9.7 | −3.2 |

**Winner by the pre-registered rule (TRAIN+VAL Sharpe): V5 beta-neutral.** The base construct
carried an unintended short-beta tilt (alts ~1.5–2× major vol); sizing the alt leg by the causal
trailing vol ratio removes it. Mechanical fix, not fished. Everything else is noise or harmful; the
3-way combo is worse than V5 alone because the trend gate switches off the periods V5 earns in.

## 3. V5 one-shot TEST, and the full-cycle record of every candidate

| strategy | TRAIN | VAL | TEST | FWD | 2023 | 2024 | 2025 | 2026 | **full cycle** | worst DD |
|---|---|---|---|---|---|---|---|---|---|---|
| **BENCHMARK hold basket** | +251% | −26% | +66% | −59% | +95.5 | +83.9 | −33.9 | −22.1 | **+85%** | **−70%** |
| **S3 gated vol-target basket** | +135% | −14% | +19% | −22% | +48.1 | +61.8 | −18.5 | +0.5 | **+96%** | **−25%** |
| S1 ungated cascade (3.7/day) | +106% | +28% | +8% | −28% | +1.3 | +102.6 | +32.4 | −24.1 | +106% | −33% |
| S2 trend-gated cascade (1.6/day) | +69% | +3% | −0.3% | −5.6% | +7.6 | +58.2 | −5.0 | +1.7 | +64% | **−10%** |
| S5-V5 beta-neutral spread | +1.3% | −6.2% | +8.5% | −1.2% | +6.3 | −4.9 | +7.2 | −6.7 | +1% | −15% |
| S5 base (the designated bar) | −22% | −16% | +8.5% | +3.5% | −3.8 | −25.0 | +3.5 | −2.7 | −27% | −32% |

**Out-of-sample only (TEST + FWD, the 17 months nothing was developed on):** V5 **+7%** · S2 −6% ·
S3 −7% · S1 −22% · benchmark **−32%**.

## 4. Reading

- **S3 beats the A-005 benchmark on a full cycle**: +96% vs +85%, at a third of the drawdown
  (−25% vs −70%). That is the "beta with a seatbelt" thesis confirmed on this data. It loses to the
  benchmark in every rally (TEST +19% vs +66%) and wins by being flat in every crash.
- **S1 has the highest raw return (+106%)** — from 2024's +103%, alt-season dip-buying — and the
  worst behaviour in the crash (−28%, DD −33%). Sharpe collapses from +2.5 in-sample to −2.2 forward.
- **S2 is the most robust**: positive 3 of 4 years, DD under 10% everywhere, 1.6 trades/day. It gave
  up most of 2024 and was flat-to-slightly-negative in 2025–26. Full cycle +64%.
- **S5 in its best form (V5) is a hedge, not a return engine**: ~flat over the cycle, +7% in the
  OOS 17 months, the only construct positive there.
- **The designated +3.67% bar is the wrong object to optimise.** Its family is a cascade-timed hedge;
  improving it means making it flatter and safer, not more profitable.

## 5. What is spent, and what this does NOT establish

**Every window is now seen for S1, S2, S3, S5 and the eight S5 variants.** There is no held-out data
left for any of them. Roughly 21 constructs have been examined across 2026-09-02 → 09-04 (8 exploratory,
5 A-012, 8 A-013 variants); any trial on S3 or S2 must carry `n_trials ≈ 21`, at which the 0.95 DSR
bar is unlikely to clear. S1/S2/S3's TRAIN+VAL figures are **not out-of-sample** — Strategy A was
developed on TRAIN+VAL, S2 = Strategy A + gate, and S3 is the spot champion's mechanism. The honest
OOS record is the TEST+FWD column: everything beat holding; only V5 was positive. **No construct here
has a demonstrated positive OOS return except a market-neutral hedge at +7% over 17 months.**
