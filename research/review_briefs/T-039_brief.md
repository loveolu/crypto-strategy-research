# T-039 / H-IntradayEdgeFloor-1h — Reviewer A brief

**REJECT** (failed pre-gate). **Falsification FIRED**: 0/72 cells clear G1∧G2∧G3∧G4∧G5. G1 72 · G2
**1** · G3 66 · **G4 0** · G5 66. **n_trials 0 → 0** of 30; ledger 0 rows; no DSR/MC. Reviewer B:
REJECT, same figures.

## Decisive numbers (Reviewer-reproduced)

- **Objective met.** At h ≤ 8 the best gross edge from any of the 6 variables, either tail, over
  251,946 pooled bars: **16.1349 bps vs an 18.0 bps round trip = 0.90×**. Edge/cost by horizon
  **0.15/0.27/0.46/0.90/1.19/2.21×** at h=1/2/4/8/12/24; edge scales ~√h, cost does not.
- **G4 changed the verdict.** `vol_ratio` h=24 BOT cleared G2 (d·excess 36.5176≥36.0; d·mu_cell
  39.8100≥18.0) at **9/9** breadth, failing only the placebo: **P95(M)=47.2200** > both the largest
  real |excess| (36.5176) and the 36.0 bar. Both sanity assertions passed; without G4 a construct
  goes forward and a trial is spent.

## Reproduction

(1) Re-ran `phase_t039_census.py` **unmodified**: all **20** artifacts **byte-identical**.
(2) **Reimplemented from the spec text**, their module not imported: matrix to **max diff 7.1e-15
bps**, 0 breadth/n_bucket mismatches; placebo rebuilt with **true `np.roll` + re-estimated
thresholds** — first 60 draws match to 1e-10 bps, proving the mask-roll shortcut equivalent.
Also verified: costs, bar counts, TEST dates, DSR entrypoint, tree/manifest, no bypass, gates.

## Audit findings (none outcome-changing)

- **Assignment defect, not Engineer deviation:** the 24-bar trim under the executable anchor lets
  `fwd_24` read one TEST bar/instrument. He ran the **literal** 24, disclosed it, shipped the 25-bar
  matrix (**0/72** changes, ≤0.0546 bps) — I confirmed both. Next census: trim `max(h)+1`.
- **G5 pooled-vs-per-instrument unspecified**; the permissive pooled reading was used, all nine
  counts reported. Strict reading also makes `vol_ratio`/`mom_24` BOT TEST-ABSENT —
  no cell passes either way.
- **Reviewer-only statistic, no Engineer counterpart (hence not in the verdict's paired fields):** **221 of the 1,000 placebo draws reach the best cell's 36.5176 bps — empirical
  family-wise p = 0.221.** The report gave only the P95 comparison, which reads as a near miss; the
  percentile shows an ordinary null draw.
- **T-038's two findings did not recur**: figures traceable, script committed, no Reviewer file
  written.

## Engineer's recommendations (unfiltered)

1. Close intraday-entry at real rates **recording the per-horizon edge/cost table**: at h=8 a
   round trip must cost **under ~8 bps** to clear 2×.
2. **State the closure boundary** — NOT closed: interactions, non-decile forms, conditional
   vol/skew targets, unheld data.
3. `vol_ratio BOT` warrants a bank paragraph as **measured-but-not-harvestable**: he **would not
   fund a construct on it**, but would record that two measurements agree on the sign.
4. **Kill early: any construct at h ≤ 4** (8.88 vs 18.0 bps).
5. If intraday stays live: **rolling-percentile conditioners and interaction cells at h=12–24**;
   maker re-test only if the fill assumption is validated.
6/7. Ops — **A-009** (funding history to 2022, else close that axis) and **A-010** (BTC 1h short
   25 bars; 9 zero-volume bars ×8 instruments), both filed.

## Observations

`vol_ratio BOT` is the only coherent structure — monotone in h, breadth 8–9/9, **all nine
instruments negative at h=24**: **directive 10's inversion now has a second, controlled measurement,
at entry level** — a sign, not an effect size, not harvestable. **1h `mom_24` is reversal, not
trend** (TOP negative at all six horizons). `illiq TOP` is TEST-ABSENT (19/151, **0** at the
median): **level cuts expire — use rolling percentiles.** **Width is unaffordable here**: the scan's
noise floor exceeds its own bar. No cell passed, so **no selection debt is handed forward**;
reviving one inherits **72 tests**, so `n_trials=1` is a multiple-testing violation. No
short-implying cell passed — **no CLOSED-short-family ruling was required.**
