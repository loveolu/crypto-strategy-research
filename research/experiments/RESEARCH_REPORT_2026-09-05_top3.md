# Research report — top 3 after walk-forward (2026-09-05, CRYPTO-EXP-012 → 015)

Operator asked for the top 3 after checking the leads and improving the best strategies, on ~3 years.
Data: OKX USDT perps, 9 instruments, 2023-01-22 → 2026-09-01 (3.6 y). Validation: rolling walk-forward
(12 m train / 3 m test / 3 m step, 11 windows, only the magnitude threshold re-fit) **and** the fixed
TRAIN→OOS split. A-011 measured per-instrument costs; unleveraged; taker.

## Top 3

| | **1. B2: 4h cascade + BTC-drop** | **2. S2-strict 4h** | **3. S2-strict 8h** |
|---|---|---|---|
| status | **Candidate** | Promising | Promising |
| rule | on 4h bars: downside-dispersion pct ≥ .80 **and** 24h drop ≤ −3.85% **and** BTC 24h drop < 0 **and** daily uptrend; hold 24h | same without the BTC condition | same mapping at 8h; drop ≤ −5.06% |
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
construct to put in front of it.

## Next
1. Port B2 to freqtrade; paper-trade; execute at the 4h close.
2. Decay monitor.
3. Start recording OI / long-short / taker-volume so the liquidation-trigger variant is testable in a year.
4. Find a second, uncorrelated mechanism — the book is currently one edge.
