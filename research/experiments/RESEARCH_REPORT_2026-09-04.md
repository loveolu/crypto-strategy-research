# Research report — cycle of 2026-09-04 (CRYPTO-EXP-005 → 010)

Autonomous research cycle under the goal framework. Full experiment rows: `EXPERIMENT_LOG.md`;
ranking: `LEADERBOARD.md`; queue: `RESEARCH_QUEUE.md`. Scripts under `user_data/research/`
(`s2_cascade.py` core; `a015_s2_robustness.py`, `a016_s2_strict.py`). All costs A-011 measured,
per-instrument, unleveraged. Data: OKX USDT perps, 1h, 2023-01-22 → 2026-09-01.

## Best strategies

| | **S2-strict-4h, 9 perps** | S2-strict, 9 perps (1h) | S5-V5 spread |
|---|---|---|---|
| status | **Promising** | Testing | Testing (hedge) |
| concept | buy the largest 24h drops (≤ −3.85%) during high downside dispersion on **4h bars**, only in a daily uptrend; hold 24h | same at 1h, ≤ −2.73% | long majors / short alts, beta-neutral, in cascade regimes |
| tf / hold | **4h / 24h** | 1h / 24h | 1h / multi-day |
| OOS period | 2024-11 → 2026-09 (21 mo) | same | 2025-04 → 2026-09 |
| OOS net / ann. | **+27.5% / ≈15%** | +12.8% / ~7% | +7.2% / ~5% |
| OOS Sharpe / PF | **1.31 / 1.87** | 0.83 / 1.32 | — |
| OOS DD | −10.4% | −12.6% | −20% |
| trades (OOS) / per day | 170 / 0.26 | 220 / 0.35 | 43 entries |
| last 365d | **−6.7%** | −11.6% | ≈ −6% |
| in-sample (TRAIN) Sh / PF | 1.78 / 2.26 | 3.11 / 2.33 | — |
| cost stress (2× / 3×) OOS Sh | **1.18 / 1.05** | 0.61 / — | — |
| drop top-5% trades (OOS) | **+10.8%** | −4.1% | — |
| robustness | params ✓ cost ✓ coins 7/9 ✓ concentration ✓ · **delay ✗ (act at 4h close) · recent ✗ · FWD ✗** | params ✓ delay ✓ cost ✓ · concentration ✗ recent ✗ | uncorrelated; OOS-positive |

Nothing reaches Candidate; the 4h construct is Promising. It is the first to sit inside the 10–20%
OOS band and the first that does not depend on a handful of trades. It has lost money over the last
year (all recent trades are the same nine from August 2026) and its edge is gone if execution slips
past ~8h. Promotion gate: forward paper-trading, rolling 90d PF > 1 for two consecutive quarters.

## Recent experiments

**EXP-005 — S2 robustness protocol.** *Why:* S2 was the leader and had never been stress-tested.
*What happened:* cost ✓ (Sh 1.00 at 2× taker), entry delay ✓ (Sh *rises* to 1.68 at 2 bars — the
signal fires early), parameters ✓ (all 25 one-at-a-time variations Sh ≥ 1.24; base is conservative
within a broad region), 8/12 rolling quarters positive. **Fails:** drop the top 5% of trades → negative;
two quarters carry all the return; last 365 days −5.9%. Short mirror −27% (crypto is asymmetric).
9-universe Sh 1.76 vs 5-universe 1.33. *Learned:* the strategy is robust to everything except the
removal of its rare large winners — which is either luck or the mechanism.

**EXP-006 — are the big winners systematic?** *Why:* decides whether EXP-005's concentration is fatal.
*What happened:* entry dsd-percentile (the primary conditioner) has **no** relation to outcome (ρ +0.06,
p 0.15). Prior-24h drop magnitude **does** (ρ +0.18, p < 0.001); the largest-drop quartile holds 11–12%
of the top-5% trades vs 2.5% base and is the only quartile with real expectancy. *Learned:* the edge is
systematic and lives in drop magnitude; the `mom_24 < 0` filter admits three losing trades for every
winning one.

**EXP-007 — magnitude filter, threshold set on TRAIN only.** *Why:* mechanistic fix from EXP-006.
*What happened:* OOS improves from −3.1% → **+9.6%** (5u) and +4.2% → **+12.7%** (9u); VAL Sh 0.70 →
3.24, TEST −0.05 → 1.12; survives 2× cost. FWD still −7% / −12%. *Learned:* the diagnosis transfers
out-of-sample. The remaining failure is the crash year, in both loose and strict.

**EXP-008 — SMA200-rising gate.** *Why:* hypothesis that FWD losses come from bear-market rallies
passing the gate. *What happened:* FWD barely improves, TEST collapses (+4.0 → +0.9), total OOS falls.
**Killed.** *Learned:* the losing FWD trades fired in *confirmed* uptrends. Dip-buying stopped paying
in 2025–26 regardless of gate quality. Decay vs regime cannot be resolved on this data.

**EXP-009 — 4h resolution.** *Why:* the goal's timeframe survey; h ≥ 12 is the cost-viable region.
*What happened:* mechanical mapping (7d/30d/24h/24h in 4h bars), TRAIN-set threshold −3.85%. OOS
+27.5%, Sh 1.31, PF 1.87, DD −10.4%; **drop top-5% → +10.8%** (1h: negative); 2× cost Sh 1.18.
*Learned:* smoother bars cut false triggers; the 4h construct does not depend on rare trades.

**EXP-010 — 4h robustness.** *What happened:* grid all positive (Sh 0.78–1.57), cost to 3× (Sh 1.05),
7/9 coins positive OOS. **Delay kills it**: 1 bar (4h) Sh 0.79, 2 bars (8h) 0.04. *Learned:* combined
with the 1h delay result, the reversion window opens ~1–3h after the cascade and closes within ~8h.

## Failed experiments (this cycle)
S2 short mirror (−27%, PF 0.82) · SMA200-rising gate (EXP-008) · gate-timing as the FWD explanation.
Prior cycle: majors/alts rotation (43 flips, 2024 −17%), regime switch S2/V5, daily/weekly rebalance.

## New market insights
1. **Cascade reversion is a drop-magnitude effect, not a dispersion effect.** Confirmed OOS. The T-038/
   T-040 finding that dispersion → forward return was real but was proxying for this.
2. **Speed does not matter at this horizon.** Entry delay *improves* S2; the reversion unfolds over hours.
3. **The edge is concentrated in high-vol regimes** (Sh 1.84 vs 0.59) and in bursts (2024-Q1, Q4).
4. **Crypto is not symmetric**: the mirrored short construct loses at every window.
5. **More instruments help** — 9 perps beat 5 on Sharpe and OOS; cascade events are partly independent.
6. **The reversion has a window.** 1h entries improve with 1–2h delay; 4h entries collapse with 4–8h
   delay. The relief rally starts ~1–3h after the cascade peak and is spent within ~8h.
7. **Something changed after 2025-09.** Every long-only construct is negative over the last year even
   in confirmed uptrends. Whether the dip-buying edge decayed or the regime is temporarily hostile is
   the open question, and only forward data answers it.

## Next experiments (ranked)
1. Forward paper-trade **S2-strict-4h-9** (execute at 4h close); promotion gate = rolling 90d PF > 1
   for two consecutive quarters.
2. Decay monitor alongside it.
3. 2h and 8h resolutions as the timeframe bracket, one pre-registered OOS run each.
4. Funding as a gate feature once 12 months are held.
5. OI-drop as the liquidation trigger (needs data fetch).

**Construct count this program, 2026-09-02 → 09-04: ≈ 45.** No held-out data remains for the S2
family. The standing rule is now: no further S2 variants on seen data.
