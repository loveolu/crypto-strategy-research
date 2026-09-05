# Research report — top 3 after walk-forward (2026-09-05, CRYPTO-EXP-012 → 015)

> **Note (2026-09-05):** a parallel session ran CRYPTO-EXP-016 → 040 the same day and launched the B2
> forward paper trade; its `RESEARCH_REPORT_2026-09-04_CURRENT.md` is the consolidated, authoritative
> report. This session's four follow-ups were renumbered EXP-041 → 044 (originally 016 → 019).


Operator asked for the top 3 after checking the leads and improving the best strategies, on ~3 years.
Data: OKX USDT perps, 9 instruments, 2023-01-22 → 2026-09-01 (3.6 y). Validation: rolling walk-forward
(12 m train / 3 m test / 3 m step, 11 windows, only the magnitude threshold re-fit) **and** the fixed
TRAIN→OOS split. A-011 measured per-instrument costs; unleveraged; taker.

## Top 3

| | **1. B2: 4h cascade + BTC-drop** | **2. S2-strict 4h** | **3. S2-strict 8h** |
|---|---|---|---|
| status | **Paper Trading (statistically provisional)** | Promising | Promising |
| rule | on 4h bars: downside-dispersion pct ≥ .80 **and** 24h drop ≤ −3.85% **and** BTC 24h drop < 0 **and** daily uptrend; `HOLD6` (28h maximum open-to-open) | same without the BTC condition | same mapping at 8h; drop ≤ −5.06% |
| WF ann / Sh / So | 13.9% / 1.23 / 3.54 | 15.7% / 1.30 / 2.93 | 14.7% / 1.70 / 4.72 |
| WF DD / Calmar | **−5.5% / 2.55** | −7.4% / 2.12 | −8.3% / 1.76 |
| WF by year 24/25/26 | +37.3 / +1.9 / +0.5 | +42.3 / +2.1 / +0.6 | +39.3 / +1.7 / +0.9 |
| last 365 d | **+1.6%** | −4.1% | **+4.3%** |
| fixed OOS (21 mo) net / Sh / PF | **+30.8% / 1.42 / 1.97** | +27.5% / 1.31 / 1.87 | +11.0% / 0.85 / 1.56 |
| OOS trades / WR / hold | 168 / 63% / 28 h | 170 / 55% / 25 h | 98 / — / — |
| drop top-5% trades | **+13.3%** | +10.8% | +4.9% |
| 3× taker cost Sh | 1.17 | 1.05 | — |
| delay 1 bar / 2 bars | 0.97 / 0.18 | 0.79 / 0.04 | — |
| high-vol / low-vol ann | +32% / −2% | +34% / 0% | +29% / +2% |
| bull / bear ann | +37% / −2% | +42% / −2% | +37% / −1% |

**These are one mechanism at three settings, not three independent edges.** Correlation among them is
high; the only uncorrelated construct found (V5) is negative-expectancy over the span.

## What improved, and what did not

- **BTC-drop condition (EXP-013): improved.** Mechanism: market-wide cascades are liquidation-driven and
  revert; single-coin drops are news-driven and do not. On walk-forward OOS it cut drawdown 26%, turned
  the crash window and the last year positive, and raised fixed-split Sharpe 1.31 → 1.42. It passed every
  robustness test the base passed. It is the first improvement whose effect landed exactly where the
  hypothesis said it would.
- **Walk-forward (EXP-012): confirmed.** All four resolutions positive across 11 rolling windows with
  per-window re-fit. The mechanism is not an artifact of one split.
- **Vol-expansion / opposite trade (EXP-014): rejected** — bull-beta only.
- **V5 hedge (EXP-015): rejected** — uncorrelated, but −3.2%/yr over the span; lowers Sharpe at any weight.
- **Leads:** OI history is 6 months deep on OKX → forward-record only. Funding at entry is suggestive in
  the crowding direction on n = 10 → not a test.

## What this book cannot do — stated plainly

Every return is 2024. In 2025–26 the strategies were flat because the gate kept them out; the goal's
10–20% band is met on the 32-month walk-forward and on the 21-month fixed OOS, and it is **not** met on
the last 12 months by any config except 8h (+4.3%). Whether dip-buying in confirmed uptrends returns
when the next bull does, or has decayed, is the question only forward data answers. B2 is the
construct to put in front of it. A later selection-bias audit (CRYPTO-EXP-025) found walk-forward
daily DSR only .543 at 200 assumed trials despite a positive block-bootstrap result; B2 is therefore
not live-eligible on historical evidence alone.

## Next
1. Port B2 to freqtrade; paper-trade; execute at the 4h close.
2. Decay monitor.
3. Start recording OI / long-short / taker-volume so the liquidation-trigger variant is testable in a year.
4. Find a second, uncorrelated mechanism — the book is currently one edge.

## Independent-challenger update through CRYPTO-EXP-030

The leaderboard remains unchanged. EXP-016, 018–024, and 026–028 tested distinct
cross-market, cross-exchange, sizing, concurrency, candle/volume and sentiment
mechanisms under frozen TRAIN gates. None qualified. EXP-024 had the strongest raw
held-out result (+24.18%, Sharpe 1.26) but failed top-5% trade removal; EXP-027 had
strong TRAIN expectancy (+112.45 net bps/trade, 9/9 positive coins) but only 38
trades, so its placebo and held-out period were not opened. EXP-025 also makes the
current B2 leader statistically provisional pending independent forward evidence.

EXP-028 also tested the recent one-minute microstructure archive. Its 988-TRADE
TRAIN sample lost −1.46 gross bps/trade before 13.62 bps measured round-trip cost
and had 0/9 net-positive coins. The later 7-day validation and 7-day TEST segments
remained sealed; this exact impact-reversal mechanism is closed.

EXP-029 resolved EXP-027's sparse but strong sentiment observation using 145 earlier
BTC spot trades. Its +28.62 gross bps only narrowly cleared 22 bps friction, had
−25.10% drawdown, and failed the 999-shift sentiment-date placebo (p=.250). Later
overlapping history remained sealed. Fear & Greed is still a reactive regime label,
not a validated timing edge.

EXP-030 found a weak one-minute BTC price-discovery lead into alts: +0.72 gross
bps/leg across 121 events, positive after both up and down shocks. The relationship
is roughly 20× smaller than 14.13 bps measured friction, yielding −15.00% net and
0/8 positive coins. Validation and TEST remained sealed; it is information, not a
tradeable challenger.

B2 evidence remains **COLLECTING** and runtime is now **HEALTHY** on PID 37452.
The process was created after the corrected strategy and both configuration files,
has a fresh heartbeat, and is the only actual B2 trade process. The initial stale
process produced zero trades, so the forward record is uncontaminated.
Promotion still requires two populated 90-day
windows with PF > 1, at least 100 total forward trades, and PSR(Sharpe > 0) ≥ .95.

The port audit compared the complete historical entry mask for all nine coins,
not only indicator formulas. It found and fixed five differences: the daily gate was
available four hours too early, and the current 4h close was compared with daily
SMA200 instead of the completed daily close. The port also used a 24h time stop,
while the frozen `HOLD6` next-open ledger implies a 28h maximum open-to-open stop.
Freqtrade also needed a one-candle post-exit cooldown (including its boundary rounding) to skip signals formed during
the exit candle exactly as the harness does. Finally, the 9 bps fee override had to
move from `exchange` to the top level where Freqtrade actually reads it. A real
protected engine run then matched all 368/368 entry and exit timestamps across 9/9
coins and explicitly loaded 9 bps/side. Exact entry-mask and ledger parity now pass;
collection resumes only after runtime freshness proves the corrected file is loaded.

EXP-031 then audited the only available actual order-book archive before attempting
another microstructure strategy. Its 360 unique snapshots are 40 polls per coin
compressed into 260.295 seconds (six UTC minutes). That is useful for spread and
book-walk cost measurement, but not independent predictive history. The frozen
data gate stopped before defining a signal or inspecting any forward return: zero
trades, zero trials, and no leaderboard change. Order-book imbalance remains an
untested hypothesis pending a genuine multi-day forward archive.
