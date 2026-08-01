"""
A-005 — the pre-registered PERPS PROGRAM BENCHMARK.

Computes the do-nothing alternative every perps candidate must beat: an
equal-weight, MONTHLY-REBALANCED long basket of the nine USDT-perpetual
instruments in user_data/config_perp.json, under validator.COST_MODEL taker
costs, on date-pinned splits that honour the reserved holdout.

WHY THIS FILE EXISTS
--------------------
PROJECT_OPERATOR_MANUAL.md, "Promotion comparison": where no champion exists a
candidate is compared against the pre-registered program benchmark, and a
candidate that does not beat it cannot be promoted regardless of its other
metrics. The perps program has no champion. Promotion criterion 3 needs the
benchmark's PER-BAR TEST returns (not a summary statistic) to compute the paired
Jobson-Korkie standard error, so this script emits the return series as a
committed data artifact.

A benchmark computed after a candidate's results are known is not a benchmark.
This runs BEFORE T-038.

REBALANCING RULE — monthly, and why it is not the backlog's buy-and-hold
-----------------------------------------------------------------------
research/OPS_BACKLOG.md A-005 as originally written said "buy-and-hold ... no
rebalancing turnover". Operator instruction of 2026-08-01 specifies MONTHLY
REBALANCING, and it is the better construction on the merits:

  * An unrebalanced basket stops being equal-weight almost immediately. Over
    2022-12-23..2025-09-19 SOL returns 20.2x while DOT returns 0.97x, so a
    never-rebalanced basket ends ~46% SOL and ~2% DOT. That is not "equal
    weight"; it is a concentrated bet on whichever instrument won, chosen with
    hindsight. It flatters the benchmark, and a flattered benchmark raises the
    promotion bar for reasons that have nothing to do with the candidate.
  * Rebalancing charges real turnover, so the benchmark pays costs on the same
    footing as a candidate rather than being a zero-cost idealisation.

The drift (never-rebalanced) variant is still computed and reported as a labelled
diagnostic, because the first A-005 commit used it and the two must be
reconcilable. THE MONTHLY-REBALANCED SERIES IS THE BENCHMARK.

Rule, stated precisely: weights are reset to 1/9 at the CLOSE of the last trading
bar of each calendar month (never on the final bar of the window, where no return
follows). Turnover cost on a rebalance is per_side_cost x sum_i |w_target,i -
w_drift,i| — every leg pays one side, buys and sells alike. The initial entry is
the same formula with w_drift = 0, i.e. exactly one per-side cost.

SPECIFICATION — otherwise pre-registered in research/OPS_BACKLOG.md, A-005.
--------------------------------------------------------------------------
Costs          validator.COST_MODEL, fill_assumption="taker".
Funding        EXCLUDED. Justified in FUNDING_NOTE; no held series overlaps the
               window. Sign convention stated there regardless.
DSR            evaluated at n_trials = 1, on the TEST split.
Window/splits  pinned by DATE, honouring the reserved holdout.

Everything printed is reproducible from committed data with
`python scripts/data_manifest.py verify` clean — importing validator enforces
that gate before any number is computed.

Run:  python user_data/research/perps_benchmark.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "user_data" / "research"))

import validator as V  # noqa: E402  (import-time data-integrity gate runs here)

CONFIG_PERP = REPO_ROOT / "user_data" / "config_perp.json"
FUTURES_DIR = REPO_ROOT / "user_data" / "data" / "okx" / "futures"
T031_FUNDING_DIR = REPO_ROOT / "user_data" / "research" / "data" / "funding"
OUT_DIR = REPO_ROOT / "research" / "benchmarks"
STEM = "perps_equal_weight_benchmark"

TIMEFRAME = "1d"
PROGRAM = "perps"
N_TRIALS = 1                      # pre-registered: the benchmark is never searched over
BARS_PER_YEAR = V.ANNUALIZATION_DAILY          # 365 — crypto trades every day
ANNUALIZATION_NAME = "sqrt(365) — daily bars, crypto trades 365 days/year"
EXECUTION_MODE = "taker"
MC_SIMS_PER_SEED = 200
REBALANCE = "monthly (last trading bar of each calendar month)"

# --------------------------------------------------------------------------- #
#  FROZEN SPLIT DATES — the perps program's single split triple.
#
#  Derived ONCE by the project's carried-forward 70/15/15 method
#  (research/review_briefs/T-037_PERPS_TRANSITION_brief.md, "Carries forward")
#  applied to the benchmark window, then FROZEN as literal dates. _check_splits()
#  re-derives them from the data on every run and RAISES if they no longer match,
#  so a data change surfaces as an error instead of silently sliding the windows
#  (PROJECT_OPERATOR_MANUAL.md, "Reserved holdout": pin splits by DATE).
#
#  These dates are the triple every perps candidate must use. Criterion 3
#  requires date-identical TEST overlap; a candidate on a longer series (BTC
#  starts 2020-01-01) uses the SAME triple and gets a longer TRAIN with an
#  identical TEST. Different dates make the comparison void.
# --------------------------------------------------------------------------- #
SPLIT_DATES = ("2024-11-22", "2025-04-21", "2025-09-19")

#: First bar on which all nine instruments have data — BNB's inception, the
#: binding constraint. Before it, an "equal-weight basket of the nine" does not
#: exist; entering the nine on different dates is not a basket of the nine.
WINDOW_START = "2022-12-23"

FUNDING_NOTE = """\
FUNDING IS EXCLUDED, and the exclusion is forced by data availability, not chosen.

SIGN CONVENTION (stated even though the term is excluded, because the next task
to revisit this must not have to re-derive it). OKX USDT perps settle funding
every 8 hours, three times a day. When the funding rate is POSITIVE the market is
in contango and LONGS PAY SHORTS. This benchmark is long-only, so its funding
P&L would be:

    funding_pnl(t) = - rate(t) * position_notional(t)      [summed over settlements]

i.e. a positive rate is a COST to this benchmark. Including funding would
therefore LOWER the benchmark's return; excluding it FLATTERS the benchmark and
makes every future candidate look worse by comparison, not better.

WHAT IS HELD. The project holds two independent funding datasets, and NEITHER
overlaps the benchmark window (2022-12-23 .. 2025-09-19):

  1. user_data/data/okx/futures/<PAIR>-1h-funding_rate.feather — all nine
     instruments, 266-273 settlements each, covering 2026-02-26 .. 2026-05-28.
  2. user_data/research/data/funding/<PAIR>-USDT-SWAP.csv — the T-031 recorder's
     output, 292 settlements each, covering 2026-04-14 .. 2026-07-20. Nine files,
     but the set is not the whitelist: it holds UNI and lacks XRP.

The earliest funding datum the project has is 2026-02-26. The benchmark window
ends 2025-09-19. The gap is over five months and there is ZERO overlap on any
instrument. OKX's public funding endpoint is retention-limited (~97 days,
measured in T-031), so the missing history cannot be recovered from the venue.
Acquiring it is an A-XXX data task, and A-005 may not touch user_data/data/.

WHAT WAS DONE. Funding is excluded from the benchmark entirely, and no proxy,
interpolation or backfill was invented for it — extrapolating a 2026 funding rate
onto 2023 would be a fabricated series, which is the failure mode this project
has already had three times.

MAGNITUDE, so the size of the omission is known rather than merely acknowledged:
on the only window the project holds, the equal-weight mean rate annualises to
roughly +0.7%/yr paid by longs (per-instrument table printed below; DOT is a
-9.3%/yr outlier, the other eight are -0.4% to +3.3%). If that magnitude carried
over to the benchmark window, the benchmark's ~+50%/yr would be overstated by
under one percentage point a year - immaterial to the verdict, but the estimate
rests on a non-overlapping window and is therefore indicative only.

DIRECTION: the exclusion makes the benchmark HARDER to beat. It is conservative
with respect to promotion.
"""

SURVIVORSHIP_NOTE = """\
THE BASKET IS SURVIVORSHIP-BIASED, and the bias cannot be removed here.

The nine instruments are config_perp.json's whitelist, selected in 2026 as the
perps with complete cached history (that file's own comment: "verified
2026-07-28"). All nine were still listed and liquid in 2026. A basket chosen in
2026 and then backtested from 2022 never holds the perps that delisted, died, or
went illiquid in between.

Removing the bias needs a point-in-time OKX perp listing history the project does
not hold; obtaining one is an A-XXX data task, not something a benchmark
computation may improvise.

Direction: upward. Like the funding exclusion, it makes this benchmark HARDER to
beat, so it is conservative with respect to promotion.
"""


# --------------------------------------------------------------------------- #
#  Loading
# --------------------------------------------------------------------------- #
def load_whitelist() -> list[str]:
    """The nine instruments, read from config_perp.json — never hardcoded.

    config_perp.json carries comments, so json.load() cannot read it; rapidjson
    with PM_COMMENTS is the documented loader (see the file's own header).
    """
    import rapidjson
    cfg = rapidjson.loads(
        CONFIG_PERP.read_text(encoding="utf-8"),
        parse_mode=rapidjson.PM_COMMENTS | rapidjson.PM_TRAILING_COMMAS)
    pairs = cfg["exchange"]["pair_whitelist"]
    if len(pairs) != 9:
        raise RuntimeError(
            f"config_perp.json whitelist has {len(pairs)} pairs, expected the 9 the "
            f"A-005 specification names. The benchmark construction is pre-registered "
            f"against that whitelist and may not be varied silently.")
    return pairs


def load_closes(pairs: list[str]) -> pd.DataFrame:
    """Close price of every instrument on one UTC daily index."""
    cols = {}
    for p in pairs:
        stem = p.replace("/", "_").replace(":", "_")
        fp = FUTURES_DIR / f"{stem}-{TIMEFRAME}-futures.feather"
        if not fp.exists():
            raise FileNotFoundError(f"missing futures feather for {p}: {fp}")
        df = pd.read_feather(fp).set_index("date").sort_index()
        if df.index.has_duplicates:
            raise RuntimeError(f"{fp.name}: duplicate timestamps")
        gaps = df.index.to_series().diff().dropna()
        bad = gaps[gaps != pd.Timedelta("1D")]
        if len(bad):
            raise RuntimeError(f"{fp.name}: {len(bad)} non-daily gap(s); first at {bad.index[0]}")
        cols[p] = df["close"].astype(float)
    return pd.DataFrame(cols)


def _check_splits(index: pd.DatetimeIndex) -> dict:
    """Re-derive 70/15/15 over the benchmark window; RAISE if it moved."""
    n = len(index)
    i1, i2 = int(n * 0.70), int(n * 0.85)
    derived = (str(index[i1 - 1].date()), str(index[i2 - 1].date()), str(index[-1].date()))
    if derived != SPLIT_DATES:
        raise RuntimeError(
            f"SPLIT_DATES {SPLIT_DATES} no longer equal the 70/15/15 boundaries of the "
            f"benchmark window, which now derive as {derived} over {n} bars. The split "
            f"triple is FROZEN and pre-registered; the data underneath it changed. "
            f"Resolve deliberately — do not update the constant to make this pass.")
    return {"n_bars": n, "train_bars": i1, "val_bars": i2 - i1, "test_bars": n - i2}


# --------------------------------------------------------------------------- #
#  Benchmark construction
# --------------------------------------------------------------------------- #
def month_end_bars(index: pd.DatetimeIndex) -> np.ndarray:
    """Boolean mask: last trading bar of each calendar month, final bar excluded.

    The final bar is excluded because no return follows it, so rebalancing there
    charges turnover for a position that is never held.
    """
    per = index.to_period("M")
    mask = np.zeros(len(index), dtype=bool)
    mask[:-1] = per[:-1] != per[1:]
    return mask


def build_benchmark(closes: pd.DataFrame, per_side: float,
                    rebalance: bool = True) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Equal-weight long basket. Returns (bars, trades, turnover_record).

    rebalance=True  -> weights reset to 1/9 at each month-end close (THE BENCHMARK)
    rebalance=False -> never reset; weights drift (the diagnostic variant)

    Cost model: every rebalance leg pays ONE side, buys and sells alike, so the
    charge is per_side_cost x sum_i |w_target,i - w_drift,i|. The initial entry is
    that same formula against w_drift = 0, which gives exactly one per_side_cost.

    The returned bars frame matches the shape validator.metrics() expects, so the
    benchmark's numbers come out of the same code that scores every candidate.
    """
    idx = closes.index
    rets = closes.pct_change()
    n_assets = closes.shape[1]
    equal = np.full(n_assets, 1.0 / n_assets)
    reb_mask = month_end_bars(idx) if rebalance else np.zeros(len(idx), dtype=bool)

    w = equal.copy()
    gross = np.zeros(len(idx))
    cost = np.zeros(len(idx))
    cost[0] = per_side * float(np.abs(equal).sum())      # entry: turnover 1.0
    # Instrument-month positions: a position runs from one rebalance to the next.
    # Between rebalances the holding is fixed, so this is a genuine held position
    # rather than an arbitrary slicing of a continuous exposure.
    seg_start = 0
    segments: list[tuple[int, int]] = []
    turnovers = [1.0]

    for t in range(1, len(idx)):
        r = rets.iloc[t].to_numpy()
        g = float(w @ r)
        gross[t] = g
        w = w * (1.0 + r) / (1.0 + g)                    # drift; still sums to 1
        if reb_mask[t]:
            turnover = float(np.abs(equal - w).sum())
            cost[t] = per_side * turnover
            turnovers.append(turnover)
            w = equal.copy()
            segments.append((seg_start, t))
            seg_start = t
    segments.append((seg_start, len(idx) - 1))

    net = gross - cost
    bars = pd.DataFrame(
        {"position": 1.0, "ret_gross": gross, "ret_net": net,
         "equity": np.cumprod(1.0 + net)},
        index=idx)

    # One trade per (instrument, holding period). pnl is that instrument's return
    # over the period MINUS a full round trip of cost on the position — a
    # deliberate over-charge, since actual rebalancing turnover is partial. The
    # exact net accounting lives in the bar series above; this log exists so the
    # Monte Carlo gate has per-position outcomes to resample.
    round_trip = 2.0 * per_side
    rows = []
    for a, b in segments:
        if b <= a:
            continue
        for p in closes.columns:
            rows.append({"entry": idx[a], "exit": idx[b], "side": 1, "bars": b - a,
                         "pnl": float(closes[p].iloc[b] / closes[p].iloc[a] - 1.0) - round_trip})
    trades = pd.DataFrame(rows)

    rec = {"rebalance": REBALANCE if rebalance else "none (drift buy-and-hold)",
           "n_rebalances": int(reb_mask.sum()),
           "n_positions": int(len(trades)),
           "total_cost_fraction": float(cost.sum()),
           "mean_rebalance_turnover": float(np.mean(turnovers[1:])) if len(turnovers) > 1 else 0.0,
           "entry_cost_bps": round(per_side * 1e4, 4)}
    return bars, trades, rec


def assert_closed_form_drift(bars: pd.DataFrame, closes: pd.DataFrame,
                             per_side: float) -> dict:
    """Closed-form check of the DRIFT variant. RAISES on mismatch.

    A never-rebalanced equal-weight basket must end at the arithmetic mean of the
    instruments' wealth relatives — each sleeve compounds alone and the sleeves
    are added up:

        equity(T) = (1/N) * SUM_i [close_i(T)/close_i(0)] * (1 - entry_cost)

    Derived from the definition, not from the loop, so it is a genuine
    cross-check rather than the implementation grading itself (the defect class
    A-003 exists to prevent). It validates the weight-drift arithmetic that the
    monthly-rebalanced path uses between rebalances.
    """
    expected = float(np.mean((closes.iloc[-1] / closes.iloc[0]).to_numpy(dtype=float)))
    expected *= (1.0 - per_side)
    actual = float(bars["equity"].iloc[-1])
    if not np.isclose(expected, actual, rtol=1e-10, atol=1e-12):
        raise RuntimeError(
            f"drift-variant construction FAILED its closed-form check: {actual!r} != "
            f"{expected!r}. The weight-drift arithmetic is wrong, which would also "
            f"corrupt the monthly-rebalanced benchmark.")
    return {"closed_form_terminal_equity": expected, "constructed_terminal_equity": actual,
            "abs_error": abs(expected - actual),
            "identity": "equity(T) = mean_i(close_i(T)/close_i(0)) * (1 - entry_cost)",
            "applies_to": "drift variant; validates the shared weight-drift arithmetic"}


def slice_bars(bars: pd.DataFrame) -> pd.DataFrame:
    """Re-base a slice so equity starts at 1.0, exactly as validate() does."""
    out = bars.copy()
    out["equity"] = np.cumprod(1.0 + out["ret_net"].to_numpy())
    return out


# --------------------------------------------------------------------------- #
#  Metrics
# --------------------------------------------------------------------------- #
_TRADE_DERIVED = ("profit_factor", "win_rate", "n_trades")
_TRADE_STATS_NA = ("n/a for a sub-window - the trade log is whole-window; "
                   "per-window trade stats would repeat full-window figures")


def sharpe_pair(ret: pd.Series) -> dict:
    """Per-period AND annualised Sharpe, both stated.

    Criterion 3's Jobson-Korkie formula takes PER-PERIOD Sharpes; mixing
    conventions changes the verdict. ddof=1 to match validator.metrics().
    """
    sd = float(ret.std())
    per = float(ret.mean() / sd) if sd > 0 else 0.0
    return {"sharpe_per_period": round(per, 6),
            "sharpe_annualised": round(per * np.sqrt(BARS_PER_YEAR), 4),
            "annualisation": ANNUALIZATION_NAME,
            "n_bars": int(len(ret))}


def window_metrics(bars: pd.DataFrame, trades: pd.DataFrame,
                   trade_stats: bool = True) -> dict:
    m = V.metrics(bars, trades, BARS_PER_YEAR)
    m.update(sharpe_pair(bars["ret_net"]))
    if not trade_stats:
        for k in _TRADE_DERIVED:
            m[k] = None
        m["trade_stats"] = _TRADE_STATS_NA
    return m


def walk_forward_windows(bars: pd.DataFrame, trades: pd.DataFrame) -> list[dict]:
    """Anchored walk-forward on validator.walk_forward()'s own window arithmetic.

    Boundaries copied from validator.walk_forward (is_end/oos_end at 50%+10%k) so
    the windows are identical to a candidate's. The function itself is not called
    because it re-derives returns through signal_to_returns(), which would charge
    a fresh entry cost at the start of every window; this basket is already in
    position and its real costs are already in ret_net.
    """
    n = len(bars)
    out = []
    for k in range(1, 5):
        is_end = int(n * (0.5 + (k - 1) * 0.10))
        oos_end = min(int(n * (0.5 + k * 0.10)), n)
        seg = bars.iloc[is_end:oos_end]
        if len(seg) < 30:
            continue
        V.assert_no_holdout(seg, label=f"walk-forward window {k}", program=PROGRAM)
        seg = slice_bars(seg)
        m = window_metrics(seg, trades, trade_stats=False)
        m.update({"window": k, "is_end": str(bars.index[is_end].date()),
                  "oos_end": str(bars.index[oos_end - 1].date()),
                  "warmup_mode": "n/a — no indicator"})
        out.append(m)
    return out


def funding_inventory(pairs: list[str]) -> dict:
    """Inventory BOTH held funding datasets and prove the non-overlap."""
    per, spans = {}, []

    for p in pairs:
        stem = p.replace("/", "_").replace(":", "_")
        fp = FUTURES_DIR / f"{stem}-1h-funding_rate.feather"
        if not fp.exists():
            continue
        rate = pd.read_feather(fp).set_index("date").sort_index()["open"].astype(float)
        per[p.split("/")[0]] = {
            "source": "feather", "n_settlements": int(len(rate)),
            "first": str(rate.index.min().date()), "last": str(rate.index.max().date()),
            "mean_rate": round(float(rate.mean()), 9),
            "annualised_pct_paid_by_longs": round(float(rate.mean()) * 3 * 365 * 100, 3),
            "share_positive": round(float((rate > 0).mean()), 4)}
        spans += [rate.index.min(), rate.index.max()]

    t031 = {}
    for fp in sorted(T031_FUNDING_DIR.glob("*-USDT-SWAP.csv")):
        df = pd.read_csv(fp)
        ts = pd.to_datetime(df["funding_time_utc"], utc=True)
        t031[fp.stem.split("-")[0]] = {
            "n_settlements": int(len(df)),
            "first": str(ts.min().date()), "last": str(ts.max().date()),
            "annualised_pct_paid_by_longs": round(
                float(df["funding_rate"].mean()) * 3 * 365 * 100, 3)}
        spans += [ts.min(), ts.max()]

    eq = round(float(np.mean([v["annualised_pct_paid_by_longs"] for v in per.values()])), 3) \
        if per else None
    return {
        "included_in_benchmark": False,
        "reason": "no held funding series overlaps the benchmark window",
        "sign_convention": ("OKX settles every 8h; positive rate = contango = LONGS PAY. "
                            "funding_pnl = -rate * notional for this long-only basket, "
                            "so excluding it FLATTERS the benchmark."),
        "earliest_funding_datum_held": str(min(spans).date()) if spans else None,
        "latest_funding_datum_held": str(max(spans).date()) if spans else None,
        "equal_weight_annualised_pct_paid_by_longs": eq,
        "feather_series": per,
        "t031_recorder_series": t031,
        "t031_note": "nine files but not the whitelist: holds UNI, lacks XRP",
    }


def bar_level_mc(bars: pd.DataFrame, extra_cost: float) -> dict:
    """Bar-level MC — a supplementary DIAGNOSTIC, not the harness trade-level gate."""
    r = bars["ret_net"].to_numpy(dtype=float) - extra_cost / len(bars)
    n = len(r)
    ann = np.sqrt(BARS_PER_YEAR)
    sharpes, finals, dds, per_seed_p5 = [], [], [], []
    for seed in V.MC_SEEDS:
        rng = np.random.default_rng(seed)
        seed_sharpes = []
        for _ in range(MC_SIMS_PER_SEED):
            boot = rng.choice(r, size=n, replace=True)
            sd = boot.std(ddof=1)
            seed_sharpes.append(float(boot.mean() / sd * ann) if sd > 0 else 0.0)
            finals.append(float(np.cumprod(1.0 + boot)[-1] - 1.0))
            eq = np.cumprod(1.0 + rng.permutation(r))
            dds.append(float((eq / np.maximum.accumulate(eq) - 1.0).min()))
        sharpes.extend(seed_sharpes)
        per_seed_p5.append(float(np.percentile(seed_sharpes, 5)))
    return {
        "mc_basis": "BAR-LEVEL DIAGNOSTIC — supplements validator.monte_carlo()",
        "mc_p5_sharpe": float(np.percentile(sharpes, 5)),
        "mc_p50_sharpe": float(np.percentile(sharpes, 50)),
        "mc_p95_sharpe": float(np.percentile(sharpes, 95)),
        "mc_p5_return": float(np.percentile(finals, 5)),
        "mc_p50_return": float(np.percentile(finals, 50)),
        "mc_p95_maxdd": float(np.percentile(dds, 5)),
        "mc_worst_maxdd": float(np.min(dds)),
        "mc_p5_sharpe_per_seed": [round(x, 4) for x in per_seed_p5],
        "mc_gate": V.mc_gate_status(per_seed_p5),
        "mc_n_sims": MC_SIMS_PER_SEED * len(V.MC_SEEDS),
    }


def defect_presumption_check(splits: dict, per_side: float, turnover: dict) -> dict:
    """PROJECT_OPERATOR_MANUAL.md: >100% CAGR is PRESUMED DEFECTIVE until verified."""
    flagged = sorted(k for k in ("full", "train", "val", "test")
                     if abs(splits[k]["cagr"]) > 1.0)
    return {
        "triggered": bool(flagged),
        "windows_over_100pct_cagr": flagged,
        "costs_applied": (
            f"VERIFIED. per_side_cost('taker') from validator.COST_MODEL = "
            f"{per_side * 1e4:.1f} bps. Entry charges exactly that once; each of the "
            f"{turnover['n_rebalances']} monthly rebalances charges it on realised "
            f"turnover (mean {turnover['mean_rebalance_turnover']:.4f} of notional). "
            f"Total cost over the window = {turnover['total_cost_fraction'] * 100:.3f}% "
            f"of notional. Nothing hardcoded, no default inherited."),
        "signal_lag": (
            "NOT APPLICABLE — there is no signal. Position is constant long from bar 0 "
            "and rebalance dates are calendar-determined, not data-determined. Returns "
            "are close-to-close; no bar uses information from a later bar."),
        "indicator_warmup": (
            "NOT APPLICABLE — no indicators, no state to warm up. Splits are pure "
            "slices of one continuous series."),
        "survivorship": (
            "PRESENT AND NOT REMOVED — see survivorship note. Upward bias, i.e. it "
            "makes the benchmark harder to beat."),
        "conclusion": (
            f"Not a cost, lag or warmup defect. (a) 2023-2025 crypto bull on an "
            f"unhedged long basket; (b) short-window annualisation — the TEST CAGR "
            f"{splits['test']['cagr'] * 100:+.2f}% annualises a {splits['test']['n_bars']}-bar "
            f"{splits['test']['total_return'] * 100:+.2f}% move and is not a sustainable "
            f"rate; (c) real, unremoved upward survivorship bias. The drift variant's "
            f"terminal equity is independently reproduced in closed form."),
    }


# --------------------------------------------------------------------------- #
#  Artifacts
# --------------------------------------------------------------------------- #
def _write_series(fp: Path, seg: pd.DataFrame, label: str, closes: pd.DataFrame,
                  per_side: float, boundary: pd.Timestamp) -> None:
    """Write a return series with its split dates embedded in the file itself.

    A-005: "The return series must carry the exact split dates it was computed
    on, so a later candidate can be checked for date-identical overlap." A series
    whose window must be looked up elsewhere is one that can be silently compared
    against the wrong window.

    Read with: pd.read_csv(fp, comment="#", index_col=0, parse_dates=True)
    """
    hdr = [
        f"# A-005 perps program benchmark - {label} return series",
        f"# equal-weight LONG basket, 9 OKX USDT perps, {TIMEFRAME} bars",
        f"# rebalance: {REBALANCE}",
        f"# generated by user_data/research/perps_benchmark.py",
        f"#",
        f"# SPLIT DATES (date-pinned, frozen): train_end={SPLIT_DATES[0]} "
        f"val_end={SPLIT_DATES[1]} test_end={SPLIT_DATES[2]}",
        f"# benchmark window: {closes.index.min().date()} .. {closes.index.max().date()}",
        f"# reserved holdout: bars strictly after {boundary.date()} (program={PROGRAM})",
        f"# this file covers:  {seg.index.min().date()} .. {seg.index.max().date()} "
        f"({len(seg)} bars)",
        f"# instruments: {', '.join(closes.columns)}",
        f"# costs: {V.describe_cost_model(EXECUTION_MODE)}",
        f"#        entry = 1 x per-side on {closes.index.min().date()}; each month-end",
        f"#        rebalance charges per-side x realised turnover. Both are IN ret_net.",
        f"# funding: EXCLUDED - no held series overlaps this window; positive rate means",
        f"#          longs pay, so excluding it FLATTERS this benchmark. See the .md.",
        f"#",
        f"# equity is re-based to 1.0 at the FIRST BAR OF THIS FILE, matching how",
        f"# validate() re-bases each split, so max drawdown here is within-window.",
        f"# ret_net is the series promotion criterion 3 consumes: pair it with the",
        f"# candidate's TEST returns on IDENTICAL dates and pass both to",
        f"# validator.sharpe_difference_se(candidate, benchmark).",
        f"#",
        f"# read with: pd.read_csv(fp, comment='#', index_col=0, parse_dates=True)",
    ]
    out = seg[["ret_gross", "ret_net", "equity"]].copy()
    out.index.name = "date"
    body = out.to_csv(float_format="%.10f", lineterminator="\n")
    fp.write_text("\n".join(hdr) + "\n" + body, encoding="utf-8")


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    boundary = V.holdout_boundary(PROGRAM)
    per_side = V.per_side_cost(EXECUTION_MODE)
    round_trip = V.round_trip_cost(EXECUTION_MODE)

    pairs = load_whitelist()
    closes_all = load_closes(pairs)

    start = pd.Timestamp(WINDOW_START, tz="UTC")
    observed = closes_all.dropna().index.min()
    if observed != start:
        raise RuntimeError(
            f"WINDOW_START {start.date()} is no longer the first bar on which all nine "
            f"instruments have data ({observed.date()}). Pre-registered; resolve "
            f"deliberately.")

    closes = closes_all.loc[(closes_all.index >= start) & (closes_all.index <= boundary)]
    if closes.isna().any().any():
        raise RuntimeError("NaN close inside the benchmark window")
    V.assert_no_holdout(closes, label="benchmark window", program=PROGRAM)
    split_shape = _check_splits(closes.index)

    bars, trades, turnover = build_benchmark(closes, per_side, rebalance=True)
    drift_bars, _, _ = build_benchmark(closes, per_side, rebalance=False)
    closed_form = assert_closed_form_drift(drift_bars, closes, per_side)

    df_tr, df_vl, df_te = V.split_by_dates(bars, *SPLIT_DATES)
    for lbl, seg in (("train", df_tr), ("val", df_vl), ("test", df_te)):
        V.assert_no_holdout(seg, label=lbl, program=PROGRAM)

    m_full = window_metrics(bars, trades)
    m_tr = window_metrics(slice_bars(df_tr), trades, trade_stats=False)
    m_vl = window_metrics(slice_bars(df_vl), trades, trade_stats=False)
    te_bars = slice_bars(df_te)
    m_te = window_metrics(te_bars, trades, trade_stats=False)

    yearly = {int(y): round(float(v), 6) for y, v in V.yearly_breakdown(bars).items()}
    conc = V.yearly_pnl_dollar_concentration(bars)
    wf = walk_forward_windows(bars, trades)

    mc = V.monte_carlo(bars, trades, n_sims=MC_SIMS_PER_SEED,
                       execution_mode=EXECUTION_MODE, bars_per_year=BARS_PER_YEAR)
    mc_bar = bar_level_mc(bars, round_trip)

    # DSR on the TEST split — validate()'s own convention.
    dsr = V.deflated_sharpe(te_bars["ret_net"].dropna().tolist(), N_TRIALS)
    dsr["window"] = "test_split"
    dsr["basis"] = "per_bar"
    dsr["dsr_full_window_diagnostic"] = V.deflated_sharpe(
        bars["ret_net"].dropna().tolist(), N_TRIALS).get("dsr")

    # Criterion 3, exercised on the real artifact so a Reviewer sees the wiring
    # work rather than taking it on trust. Self-comparison must give delta 0.
    _, _, dte = V.split_by_dates(drift_bars, *SPLIT_DATES)
    c3 = {
        "self": V.sharpe_difference_se(te_bars["ret_net"], te_bars["ret_net"],
                                       bars_per_year=BARS_PER_YEAR),
        "drift_variant_vs_benchmark": V.sharpe_difference_se(
            slice_bars(dte)["ret_net"], te_bars["ret_net"], bars_per_year=BARS_PER_YEAR),
    }

    drift_full = window_metrics(drift_bars, trades)
    _, _, drift_te = V.split_by_dates(drift_bars, *SPLIT_DATES)
    drift_te_m = window_metrics(slice_bars(drift_te), trades, trade_stats=False)

    test_csv = OUT_DIR / f"{STEM}_TEST_returns.csv"
    full_csv = OUT_DIR / f"{STEM}_FULL_returns.csv"
    _write_series(test_csv, te_bars, "TEST split", closes, per_side, boundary)
    _write_series(full_csv, bars, "FULL window", closes, per_side, boundary)

    record = {
        "task": "A-005",
        "artifact": "perps program benchmark — equal-weight monthly-rebalanced long basket",
        "generated_by": "user_data/research/perps_benchmark.py",
        "machine_readable_companion": f"research/benchmarks/{STEM}.json (this file)",
        "human_readable": f"research/benchmarks/{STEM}.md",
        "program": PROGRAM,
        "instruments": pairs,
        "timeframe": TIMEFRAME,
        "rebalance_rule": REBALANCE,
        "turnover": turnover,
        "window": {"start": str(closes.index.min().date()),
                   "end": str(closes.index.max().date()),
                   "holdout_boundary": str(boundary.date()),
                   "start_rationale": "first bar on which all nine instruments exist (BNB inception)",
                   **split_shape},
        "split_dates": {"train_end": SPLIT_DATES[0], "val_end": SPLIT_DATES[1],
                        "test_end": SPLIT_DATES[2], "mode": "date_pinned",
                        "method": "70/15/15 of the benchmark window, then frozen as dates"},
        "cost_model": V.cost_model_snapshot(EXECUTION_MODE),
        "n_trials": N_TRIALS,
        "funding": funding_inventory(pairs),
        "survivorship": SURVIVORSHIP_NOTE,
        "construction_check": closed_form,
        "full": {**m_full, "max_year_share": conc.get("max_year_share")},
        "train": m_tr, "val": m_vl, "test": m_te,
        "yearly": yearly,
        "wf": wf,
        "mc_trade_level_harness": mc,
        "mc_bar_level_diagnostic": mc_bar,
        "dsr": dsr,
        "criterion_3_worked_examples": c3,
        "drift_variant_diagnostic": {
            "note": ("never-rebalanced buy-and-hold, the construction used in the "
                     "superseded first A-005 commit; reported for reconciliation only"),
            "full": drift_full, "test": drift_te_m},
        "data_manifest": V.data_integrity_snapshot(),
        "warnings": (V.data_integrity_warnings() + V.dsr_warnings(dsr)
                     + V.cost_model_warnings(EXECUTION_MODE)),
        "artifacts": {"test_returns_csv": f"research/benchmarks/{test_csv.name}",
                      "full_returns_csv": f"research/benchmarks/{full_csv.name}"},
    }
    record["defect_presumption_check"] = defect_presumption_check(
        {"full": record["full"], "train": m_tr, "val": m_vl, "test": m_te},
        per_side, turnover)

    (OUT_DIR / f"{STEM}.json").write_text(
        json.dumps(record, indent=2, default=str), encoding="utf-8")

    _print(record)
    print(f"\nWrote:\n  research/benchmarks/{STEM}.json"
          f"\n  research/benchmarks/{test_csv.name}"
          f"\n  research/benchmarks/{full_csv.name}")
    return record


def _print(r: dict) -> None:
    w, s, t = r["window"], r["split_dates"], r["test"]
    line = "=" * 78
    print(f"\n{line}\nPERPS PROGRAM BENCHMARK (A-005)\n"
          f"equal-weight LONG basket of 9 OKX USDT perps, {r['rebalance_rule']}\n{line}")
    print(f"Instruments : {', '.join(p.split('/')[0] for p in r['instruments'])}  ({r['timeframe']})")
    print(f"Window      : {w['start']} .. {w['end']}  ({w['n_bars']} bars)  "
          f"holdout after {w['holdout_boundary']}")
    print(f"Splits      : {s['mode']}  train<={s['train_end']} ({w['train_bars']})  "
          f"val<={s['val_end']} ({w['val_bars']})  test<={s['test_end']} ({w['test_bars']})")
    dm = r["data_manifest"]
    print(f"Data        : {'VERIFIED' if dm['verified'] else 'NOT VERIFIED'} "
          f"({dm['files_checked']} files, manifest {dm['manifest_built_utc']})")
    print(f"Costs       : {r['cost_model']['summary']}")
    tn = r["turnover"]
    print(f"Turnover    : {tn['n_rebalances']} monthly rebalances, mean turnover "
          f"{tn['mean_rebalance_turnover']:.4f} of notional; total cost paid "
          f"{tn['total_cost_fraction'] * 100:.3f}% of notional over the window")

    print(f"\n{'-'*78}\nHEADLINE — the numbers the promotion rule consumes\n{'-'*78}")
    print(f"  TEST Sharpe (per-period) : {t['sharpe_per_period']:+.6f}   <- criterion 3 input")
    print(f"  TEST Sharpe (annualised) : {t['sharpe_annualised']:+.4f}   [{t['annualisation']}]")
    print(f"  TEST Sharpe SIGN         : {'POSITIVE' if t['sharpe_per_period'] > 0 else 'NEGATIVE'}")
    print(f"  TEST MaxDD               : {t['max_dd']*100:+.2f}%   -> criterion-4 cap "
          f"{t['max_dd']*1.25*100:+.2f}%")
    print(f"  TEST bars (N)            : {t['n_bars']}")
    print(f"  DSR (TEST, n_trials=1)   : {r['dsr'].get('dsr')}   sr0 {r['dsr'].get('sr0_benchmark')}"
          f"   trial_var_source={r['dsr'].get('trial_var_source')}")

    print(f"\n{'-'*78}\nFULL METRIC SET\n{'-'*78}")
    print(f"{'window':8s} {'return':>9s} {'CAGR':>9s} {'Sharpe':>9s} {'per-per':>10s} "
          f"{'Sortino':>9s} {'MaxDD':>9s} {'bars':>5s}")
    for lbl in ("full", "train", "val", "test"):
        m = r[lbl]
        print(f"{lbl:8s} {m['total_return']*100:+8.2f}% {m['cagr']*100:+8.2f}% "
              f"{m['sharpe_annualised']:+9.4f} {m['sharpe_per_period']:+10.6f} "
              f"{m['sortino']:+9.4f} {m['max_dd']*100:+8.2f}% {m['n_bars']:>5d}")
    print(f"\n  PF {r['full']['profit_factor']}, win rate {r['full']['win_rate']:.1%}, "
          f"{r['full']['n_trades']} instrument-month positions (full window only; "
          f"blanked on sub-windows)")
    print(f"  years {r['full']['years']}   max single-year share of $ profit "
          f"{r['full']['max_year_share']:.4f}")
    print("  yearly: " + "  ".join(f"{y}:{v*100:+.1f}%" for y, v in r["yearly"].items()))

    print("\n  walk-forward (validator.walk_forward window arithmetic, 4 anchored OOS windows):")
    for x in r["wf"]:
        print(f"    W{x['window']}  {x['is_end']} .. {x['oos_end']}  "
              f"ret {x['total_return']*100:+7.2f}%  Sharpe {x['sharpe_annualised']:+7.4f}  "
              f"MaxDD {x['max_dd']*100:+7.2f}%")
    print(f"    positive in {sum(1 for x in r['wf'] if x['total_return'] > 0)}/{len(r['wf'])} windows")

    mh, mb = r["mc_trade_level_harness"], r["mc_bar_level_diagnostic"]
    print(f"\n  Monte Carlo — harness trade-level gate: {mh.get('mc_gate')}   "
          f"per-seed p5 Sharpe {mh.get('mc_p5_sharpe_per_seed')}")
    print(f"    {mh.get('mc_n_sims')} sims, Sharpe p5 {mh.get('mc_p5_sharpe', float('nan')):+.4f} "
          f"p50 {mh.get('mc_p50_sharpe', float('nan')):+.4f}; MaxDD p95(worst tail) "
          f"{mh.get('mc_p95_maxdd', float('nan'))*100:+.2f}%")
    print(f"  Monte Carlo — bar-level diagnostic: {mb['mc_gate']}   "
          f"per-seed p5 {mb['mc_p5_sharpe_per_seed']}")
    print("    CAVEAT on the trade-level figures: validator.monte_carlo() assumes ONE")
    print("    position at a time. This basket holds nine sleeves in PARALLEL at 1/9")
    print("    weight, so treating each instrument-month as a sequential full-notional")
    print("    trade inflates both the annualisation factor and the compounded MaxDD.")
    print("    The bar-level diagnostic is the faithful one for a basket; both gate the")
    print("    same way, so the conclusion does not turn on the distinction.")
    print("    permuted-order MaxDD also overstates dispersion and must NOT feed")
    print("    criterion 4 — that uses the realized TEST MaxDD above.")

    print(f"\n{'-'*78}\nCRITERION 3 — validator.sharpe_difference_se(), worked on this artifact\n{'-'*78}")
    for k, c in r["criterion_3_worked_examples"].items():
        print(f"  {k}:")
        print(f"    Sa {c['sharpe_a']:+.6f}  Sb {c['sharpe_b']:+.6f}  rho {c['rho']:+.6f}  "
              f"N {c['n_obs']}")
        print(f"    delta {c['delta']:+.6f}  SE {c['se']:.6f}  -> criterion_3_pass "
              f"{c['criterion_3_pass']}")

    d = r["drift_variant_diagnostic"]
    print(f"\n{'-'*78}\nDRIFT VARIANT (never rebalanced) — diagnostic only, NOT the benchmark\n{'-'*78}")
    print(f"  full  return {d['full']['total_return']*100:+.2f}%  Sharpe "
          f"{d['full']['sharpe_annualised']:+.4f}  MaxDD {d['full']['max_dd']*100:+.2f}%")
    print(f"  test  return {d['test']['total_return']*100:+.2f}%  Sharpe "
          f"{d['test']['sharpe_annualised']:+.4f} (per-period "
          f"{d['test']['sharpe_per_period']:+.6f})  MaxDD {d['test']['max_dd']*100:+.2f}%")
    cf = r["construction_check"]
    print(f"  closed-form check: {cf['closed_form_terminal_equity']:.12f} vs "
          f"{cf['constructed_terminal_equity']:.12f}  (abs err {cf['abs_error']:.3e}) PASS")

    print(f"\n{'-'*78}\nFUNDING\n{'-'*78}")
    print(FUNDING_NOTE)
    f = r["funding"]
    print(f"  earliest funding datum held: {f['earliest_funding_datum_held']}   "
          f"benchmark window ends {w['end']}   ->  NO OVERLAP")
    for k, v in f["feather_series"].items():
        print(f"    {k:5s} n={v['n_settlements']:4d}  {v['first']}..{v['last']}  "
              f"ann {v['annualised_pct_paid_by_longs']:+6.2f}%  positive {v['share_positive']:.1%}")
    print(f"  equal-weight annualised funding paid by longs: "
          f"{f['equal_weight_annualised_pct_paid_by_longs']:+.3f}%/yr (indicative only)")

    print(f"\n{'-'*78}\nSURVIVORSHIP\n{'-'*78}")
    print(SURVIVORSHIP_NOTE)

    dp = r["defect_presumption_check"]
    print(f"{'-'*78}\n>100% CAGR DEFECT PRESUMPTION — mandatory verification\n{'-'*78}")
    print(f"  Triggered on: {', '.join(dp['windows_over_100pct_cagr']) or 'none'}")
    for k in ("costs_applied", "signal_lag", "indicator_warmup", "survivorship"):
        print(f"  - {k}: {dp[k]}")
    print(f"  => {dp['conclusion']}")

    print(f"\n{'-'*78}\nWARNINGS — reproduce verbatim in any report quoting these numbers\n{'-'*78}")
    for x in r["warnings"]:
        print(f"  !! {x}\n")


if __name__ == "__main__":
    main()
