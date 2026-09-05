# Session-B experiments, 2026-09-05 — CRYPTO-EXP-B01 … B04 (separate namespace, no collision)

**Why this file exists.** Two sessions worked this tree on 2026-09-04/05 without a channel between
them. Session A ran CRYPTO-EXP-016 → 041+ and rewrote the shared `EXPERIMENT_LOG.md`; Session B's
four rows (first numbered 016 → 019, then 041 → 044) were dropped by that rewrite and collide with
A's numbering either way. They are recorded here under **B01 → B04** and are NOT in the shared log.
Whoever consolidates should merge these rows into `EXPERIMENT_LOG.md` under fresh numbers.

Harness: `user_data/research/s2_cascade.py` (params `squeeze`, `btc_bounce`, `exit_mode` added by
Session B) and `wf_cascade.py`; runner `user_data/research/a020_new_axes.py`; results
`research/measurements/A020_new_axes.pkl`. Walk-forward = 11 windows, 12 m train / 3 m test / 3 m
step, 2024-01 → 2026-09, only the magnitude threshold re-fit. Fixed OOS = 2024-11-23 → 2026-09-01,
threshold from TRAIN. A-011 measured per-instrument taker costs; unleveraged; 9 OKX perps; 4h.

| ID | hypothesis | construction | result | verdict |
|---|---|---|---|---|
| **B01** (was 016/041) | Bear rallies are squeezes that fade: short upside spikes in downtrends | 4h; upside-dispersion pct ≥ .80; up-move ≥ TRAIN 75th pct; daily gate OFF; BTC also up; short 24h | WF −2.7%, ann −1.0%, DD −20.9%, Sh −0.08, So −0.11; **2024 −18.0%, 2025 +17.2%, 2026 +1.3%**; 4/11 windows; 301 trades | **KILLED by rule** (Sh ≤ 0). Earns in the true bear, loses in bull pullbacks: the SMA200/EMA gate cannot tell them apart. **Lead** → stricter bear gate (price < SMA200 AND SMA200 falling). The loose 1h mirror had already died in EXP-005 (−27%). |
| **B02** (was 017/042) | BTC leads alts: wait one bar, enter only if BTC closed green | B2 + forced 1-bar delay + BTC bar return > 0 | WF 14.4% / Sh 0.74 / DD −5.6% / Cal 0.94, n 118 — vs B2 plain 1-bar delay WF 18.3% / Sh 0.85 / DD −8.7% / Cal 0.77, n 157 | **KILLED** (Sh). Better DD, worse Sharpe, fewer trades. BTC works as a FILTER (B2), not as a TIMING signal. **Independently reproduces Session A's EXP-016 rejection.** |
| **B03** (was 018/043) | Exit research: fixed 24h vs target (50% of entry drop) vs stop (entry-bar low) vs both | B2 with `exit_mode` ∈ {time, target, stop, both} | WF: time 40.6% / Sh 1.23 / DD −5.5 / Cal 2.55 · **target 36.9% / Sh 1.61 / DD −4.3 / Cal 3.00 / So 3.80** · stop 30.5% / Sh 0.99 / Cal 1.72 · both 21.8% / Sh 1.03. Target by year 2024 +30.7 / 2025 **+3.8** / 2026 +1.0; last 365d +1.8%. Fixed OOS target: **+27.6%, Sh 1.61, So 3.39, PF 2.14, WR 70%**, 179 trades, hold 18h, 54% close on target; 2× / 3× cost Sh 1.41 / 1.25; **delay 1 / 2 bars Sh 1.81 / 0.96** (time-exit: 0.97 / 0.18); drop top-5% → +12.6%, top-10% → +5.7% | **SURVIVES — Candidate VARIANT.** Beats fixed 24h on Sharpe, Sortino, DD, Calmar, PF, WR, both hard years and cost stress, for ~10% less total return, and **relaxes the execution-timing constraint**. Stops HURT. Not the live paper-trade rule (frozen at HOLD6 per `B2_FORWARD_PAPER_PLAN.md`); pre-registered as the next forward variant. Not selection-deflated — treat DSR ≤ B2's .543 (Session A EXP-025). |
| **B04** (was 019/044) | Within a market-wide cascade the hardest-hit coins bounce most | fixed OOS; bars with ≥ 4 of 9 simultaneous B2 triggers; take the 3 most-negative mom_24h | all B2 OOS: n 168, 149 bps, WR 63%, PF 1.97 · wide bars: n 15, **603 bps, WR 87%** (3 bars) · hardest-3: n 9, 663 bps · rest: n 3, 458 bps | n = 9 is not evidence. Market-WIDE cascade bars carry ~4× expectancy — a sizing lead, not a strategy. **Independently reproduces Session A's EXP-022** (breadth = mechanism insight, allocation rejected). |

## Leads for the queue (not yet in the shared queue — Session A rewrote it)

1. **B2 + target exit as the next forward variant.** Do not alter the running frozen rule. At the first
   90-day review of the live paper trade, register a second dry-run instance with
   `exit_mode="target"` and run both side by side.
2. **Bear-leg short with a stricter bear gate** (from B01): ONE pre-registered gate, price < SMA200
   AND SMA200 falling (the mirror of EXP-008). Kill: WF Sh ≤ 0 or 2024 loss > 2025 gain. If it
   survives, the book has a second regime. Seen data — count it; a pass needs forward proof.

## Process note

Session B's earlier reconciliation appended addenda to `LEADERBOARD.md`, `RESEARCH_QUEUE.md` and
`RESEARCH_REPORT_2026-09-04_CURRENT.md` under the label CRYPTO-EXP-041 → 044; those labels collide
with Session A's EXP-041 (mark-premium reversion) and may have been overwritten. **This file is the
authoritative record of Session B's four experiments.** Rule going forward: one session per working
tree, or separate git worktrees — two agents rewriting shared ledgers concurrently loses work.
