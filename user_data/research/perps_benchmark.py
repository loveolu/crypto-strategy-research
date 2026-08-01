"""
A-005 — the pre-registered PERPS PROGRAM BENCHMARK.

Computes the do-nothing alternative every perps candidate must beat:
an equal-weight buy-and-hold of the nine USDT-perpetual instruments in
user_data/config_perp.json, under validator.COST_MODEL taker costs, on
date-pinned splits that honour the reserved holdout.

WHY THIS FILE EXISTS
--------------------
PROJECT_OPERATOR_MANUAL.md, "Promotion comparison": where no champion exists a
candidate is compared against the pre-registered program benchmark, and a
candidate that does not beat it cannot be promoted regardless of its other
metrics. The perps program has no champion. Promotion criterion 3 needs the
benchmark's PER-BAR TEST returns (not a summary statistic) to compute the paired
Jobson-Korkie standard error, so this script emits the return series as a
committed data artifact, not just the headline numbers.

A benchmark computed after a candidate's results are known is not a benchmark.
This runs BEFORE T-038.

SPECIFICATION — pre-registered in research/OPS_BACKLOG.md, A-005. Do not vary.
-----------------------------------------------------------------------------
Construction   equal-weight buy-and-hold of the 9 config_perp.json instruments.
Costs          validator.COST_MODEL, fill_assumption="taker". Entry cost applies
               ONCE per instrument; buy-and-hold has no rebalancing turnover.
Funding        EXCLUDED. Justified in FUNDING_NOTE below; the project holds no
               funding series covering this window.
DSR            evaluated at n_trials = 1.
Window/splits  pinned by DATE, honouring the reserved holdout.

Everything this script prints is reproducible from committed data with
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
OUT_DIR = REPO_ROOT / "research" / "benchmarks"

TIMEFRAME = "1d"
PROGRAM = "perps"
N_TRIALS = 1                      # pre-registered: the benchmark is never searched over
BARS_PER_YEAR = V.ANNUALIZATION_DAILY          # 365 — crypto trades every day
ANNUALIZATION_NAME = "sqrt(365) — daily bars, crypto trades 365 days/year"
EXECUTION_MODE = "taker"
MC_SIMS_PER_SEED = 200

# --------------------------------------------------------------------------- #
#  FROZEN SPLIT DATES — the perps program's single split triple.
#
#  Derived ONCE, here, by the project's carried-forward 70/15/15 method
#  (research/review_briefs/T-037_PERPS_TRANSITION_brief.md, "Carries forward")
#  applied to the benchmark window, then FROZEN as literal dates. _check_splits()
#  re-derives them from the data on every run and RAISES if they no longer match,
#  so a data change surfaces as an error instead of silently sliding the windows
#  (PROJECT_OPERATOR_MANUAL.md, "Reserved holdout": pin splits by DATE).
#
#  These dates are the triple every perps candidate must use. Criterion 3 requires
#  date-identical TEST overlap; a candidate on a longer series (BTC starts
#  2020-01-01) uses the SAME triple and gets a longer TRAIN with an identical
#  TEST. A candidate that uses different dates is void against this benchmark.
# --------------------------------------------------------------------------- #
SPLIT_DATES = ("2024-11-22", "2025-04-21", "2025-09-19")

#: First bar on which all nine instruments have data — BNB's inception, the
#: binding constraint. Before it, an "equal-weight basket of the nine" does not
#: exist; entering the nine on different dates is not buy-and-hold of the nine.
WINDOW_START = "2022-12-23"

FUNDING_NOTE = """\
FUNDING IS EXCLUDED FROM THIS BENCHMARK, and the exclusion is forced, not chosen.

Source series held: user_data/data/okx/futures/<PAIR>-1h-funding_rate.feather,
one per instrument. Every one of them covers only 2026-02-26 .. 2026-05-28
(266-273 8-hourly settlements each) — a ~91-day window that lies entirely AFTER
the benchmark window's end (2025-09-19) and after the reserved-holdout boundary.
There is ZERO overlap with the window being measured. OKX's public funding
endpoint is retention-limited (~97 days observed in T-031), so the missing
history cannot be recovered from the venue; acquiring it is an A-XXX data task,
and this task may not touch user_data/data/.

Direction and magnitude of the resulting bias, measured on the only window the
project holds (printed by this script): longs PAY funding on average across the
nine, an equal-weight ~+0.7%/yr. Excluding it therefore OVERSTATES the
benchmark's return by roughly that order, which makes the promotion bar HARDER,
not easier. The bias is conservative with respect to promotion — a candidate
beating this benchmark would also beat a funding-charged one. That is why the
exclusion is acceptable; it is not acceptable to leave it implicit.
"""

SURVIVORSHIP_NOTE = """\
THE BASKET IS SURVIVORSHIP-BIASED, and the bias cannot be removed here.

The nine instruments are config_perp.json's whitelist, selected in 2026 as the
perps with complete cached history (that file's own comment: "verified
2026-07-28"). All nine were still listed and liquid in 2026. A basket chosen in
2026 and then backtested from 2022 never holds the perps that delisted, died, or
went illiquid in between, so its measured return is the return of the winners
plus the losers that merely fell — not of the universe as it stood in 2022.

Removing the bias needs a point-in-time OKX perp listing history the project does
not hold; obtaining one is an A-XXX data task, not something a benchmark
computation may improvise.

Direction: upward. Like the funding exclusion, it makes this benchmark HARDER to
beat, so it is conservative with respect to promotion. It is stated because
criterion 3 compares a candidate against these numbers and a reader must know
they are an optimistic estimate of the do-nothing alternative.
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


def feather_path(pair: str) -> Path:
    """'BTC/USDT:USDT' -> BTC_USDT_USDT-1d-futures.feather"""
    stem = pair.replace("/", "_").replace(":", "_")
    return FUTURES_DIR / f"{stem}-{TIMEFRAME}-futures.feather"


def load_closes(pairs: list[str]) -> pd.DataFrame:
    """Close price of every instrument on one UTC daily index."""
    cols = {}
    for p in pairs:
        fp = feather_path(p)
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


# --------------------------------------------------------------------------- #
#  Splits
# --------------------------------------------------------------------------- #
def _check_splits(index: pd.DatetimeIndex) -> dict:
    """Re-derive 70/15/15 over the benchmark window; RAISE if it moved.

    The frozen SPLIT_DATES above are the authority. This proves they are still
    the 70/15/15 boundaries of the committed data rather than stale literals.
    """
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
def build_benchmark(closes: pd.DataFrame, per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Equal-weight buy-and-hold with DRIFTING weights. Returns (bars, trades).

    Definition, stated so it cannot be reconstructed differently later:

      * On the first bar of the window each instrument is bought at that bar's
        close with 1/9 of capital. The one-off entry cost is charged on that bar,
        so bar 0's net return is exactly -per_side_cost.
      * From bar 1 onward the portfolio's gross return is the weight-weighted
        mean of the instruments' close-to-close returns, and each weight then
        drifts by its own instrument's return. This is buy-and-hold: nothing is
        rebalanced, so no turnover cost is ever charged again.
      * The position is never closed. Terminal value is MARK-TO-MARKET; an actual
        exit would cost a further per_side_cost, which is NOT charged here
        because the pre-registered spec charges entry only.

    The returned frame matches the shape validator.metrics() expects, so the
    benchmark's numbers come out of the same code that scores every candidate.
    """
    idx = closes.index
    rets = closes.pct_change()                      # bar 0 is NaN by construction
    n_assets = closes.shape[1]

    w = np.full(n_assets, 1.0 / n_assets)
    gross = np.zeros(len(idx))
    for t in range(1, len(idx)):
        r = rets.iloc[t].to_numpy()
        g = float(w @ r)
        gross[t] = g
        w = w * (1.0 + r) / (1.0 + g)               # drift; still sums to 1

    net = gross.copy()
    net[0] -= per_side                              # entry, once, on bar 0

    bars = pd.DataFrame(
        {"position": 1.0,
         "ret_gross": gross,
         "ret_net": net,
         "equity": np.cumprod(1.0 + net)},
        index=idx)

    # One "trade" per instrument: entered on bar 0, still open at the last bar.
    # pnl is that instrument's own buy-and-hold return net of its entry cost.
    trades = pd.DataFrame([
        {"entry": idx[0], "exit": idx[-1], "side": 1, "bars": len(idx) - 1,
         "pnl": float(closes[p].iloc[-1] / closes[p].iloc[0] - 1.0) - per_side}
        for p in closes.columns])
    return bars, trades


def assert_closed_form(bars: pd.DataFrame, closes: pd.DataFrame, per_side: float) -> dict:
    """Independent closed-form check of the drifting-weight loop. RAISES on mismatch.

    An equal-weight buy-and-hold that is never rebalanced ends at the ARITHMETIC
    MEAN of the instruments' wealth relatives — the money in each sleeve compounds
    on its own and the sleeves are simply added up:

        equity(T) = (1/N) * SUM_i [ close_i(T) / close_i(0) ] * (1 - entry_cost)

    That is derived from the definition of buy-and-hold, not from the loop above,
    so it is a genuine cross-check rather than the implementation grading itself
    (the defect class A-003 exists to prevent). If the iterative weight-drift
    construction is wrong in any way, these disagree.
    """
    wealth_relatives = (closes.iloc[-1] / closes.iloc[0]).to_numpy(dtype=float)
    expected = float(np.mean(wealth_relatives)) * (1.0 - per_side)
    actual = float(bars["equity"].iloc[-1])
    if not np.isclose(expected, actual, rtol=1e-10, atol=1e-12):
        raise RuntimeError(
            f"benchmark construction FAILED its closed-form check: iterative "
            f"drifting-weight equity {actual!r} != mean-of-wealth-relatives "
            f"{expected!r}. The portfolio is not the buy-and-hold it claims to be.")
    return {"closed_form_terminal_equity": expected,
            "constructed_terminal_equity": actual,
            "abs_error": abs(expected - actual),
            "identity": "equity(T) = mean_i(close_i(T)/close_i(0)) * (1 - entry_cost)"}


def defect_presumption_check(m_full: dict, splits: dict, per_side: float) -> dict:
    """PROJECT_OPERATOR_MANUAL.md: >100% CAGR is PRESUMED DEFECTIVE until verified.

    "A result surviving all four is reported WITH that verification; one unchecked
    is not reportable." The four checks, answered for this construct:
    """
    flagged = sorted(k for k in ("full", "train", "val", "test")
                     if abs(splits[k]["cagr"]) > 1.0)
    return {
        "triggered": bool(flagged) or m_full["cagr"] > 1.0,
        "windows_over_100pct_cagr": flagged,
        "costs_applied": (
            f"VERIFIED. per_side_cost('taker') resolved from validator.COST_MODEL = "
            f"{per_side * 1e4:.1f} bps, charged once per instrument on bar 0; bar 0's "
            f"net return equals exactly -{per_side * 1e4:.1f} bps. Nothing is "
            f"hardcoded and no default is inherited."),
        "signal_lag": (
            "NOT APPLICABLE, and that is the point: there is no signal. Position is "
            "the constant 1 from bar 0, so signal_to_returns()'s 2-bar lag has nothing "
            "to protect against. Returns are close-to-close, close_i(t)/close_i(t-1); "
            "no bar uses information from a later bar."),
        "indicator_warmup": (
            "NOT APPLICABLE — no indicators. The full-series-then-slice rule exists "
            "so a split does not restart an indicator's warmup; buy-and-hold has no "
            "state to warm up. Splits are pure slices of one continuous series."),
        "survivorship": (
            "PRESENT AND NOT REMOVED — see SURVIVORSHIP_NOTE. The nine instruments "
            "were selected in 2026 for having complete history; delisted perps are "
            "absent. The bias is upward, i.e. it makes this benchmark harder to beat."),
        "conclusion": (
            f"The high CAGRs are NOT a cost, lag, or warmup defect. They are (a) the "
            f"2023-2025 crypto bull measured on an unhedged long basket, (b) short-window "
            f"annualisation — the {splits['test']['cagr'] * 100:+.2f}% TEST CAGR annualises "
            f"a {splits['test']['n_bars']}-bar {splits['test']['total_return'] * 100:+.2f}% "
            f"move and must not be read as a sustainable rate, and (c) an upward "
            f"survivorship bias that is real and unremoved. The closed-form check above "
            f"independently reproduces the terminal equity."),
    }


def slice_bars(bars: pd.DataFrame) -> pd.DataFrame:
    """Re-base a slice so equity starts at 1.0, exactly as validate() does.

    validate() recomputes signal_to_returns() per split, so every split's equity
    (and therefore its max drawdown) restarts at 1.0 inside the window. A
    benchmark measured any other way would not be like-for-like.
    """
    out = bars.copy()
    out["equity"] = np.cumprod(1.0 + out["ret_net"].to_numpy())
    return out


# --------------------------------------------------------------------------- #
#  Metrics
# --------------------------------------------------------------------------- #
def sharpe_pair(ret: pd.Series) -> dict:
    """Per-period AND annualised Sharpe, both stated.

    Promotion criterion 3's Jobson-Korkie formula takes PER-PERIOD Sharpes.
    Mixing conventions changes the verdict, so both are reported and labelled.
    """
    sd = float(ret.std())
    per = float(ret.mean() / sd) if sd > 0 else 0.0
    return {"sharpe_per_period": round(per, 6),
            "sharpe_annualised": round(per * np.sqrt(BARS_PER_YEAR), 4),
            "annualisation": ANNUALIZATION_NAME,
            "n_bars": int(len(ret))}


#: Why the sub-window trade stats are blanked. metrics() derives profit factor,
#: win rate and trade count from the trade log it is handed. Buy-and-hold has ONE
#: position per instrument spanning the entire window, so there is no per-window
#: trade log at all — handing metrics() the full-window log for a 151-bar slice
#: would print the full-window PF/win-rate/count as if they were TEST figures.
#: They are reported for the full window only and blanked everywhere else.
_TRADE_DERIVED = ("profit_factor", "win_rate", "n_trades")
_TRADE_STATS_NA = ("n/a - one buy-and-hold position per instrument spans the whole "
                   "window; there is no per-window trade log to derive these from")


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

    The boundaries are copied from validator.walk_forward (is_end/oos_end at
    50%+10%k) so the windows are identical to a candidate's. The function itself
    is not called because it re-derives returns through signal_to_returns(),
    which would charge a fresh entry cost at the start of every window — a
    buy-and-hold is already in position and pays nothing there.
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
                  "warmup_mode": "n/a — buy-and-hold has no indicator"})
        out.append(m)
    return out


def bar_level_mc(bars: pd.DataFrame, extra_cost: float) -> dict:
    """Bar-level MC — a DIAGNOSTIC, not the harness trade-level gate.

    validator.monte_carlo() resamples the TRADE log and short-circuits below 30
    trades. Buy-and-hold has nine trades and never will have more, so the harness
    gate is structurally unavailable here and returns INSUFFICIENT (that honest
    result is reported alongside this). This diagnostic applies the same two
    resampling schemes to the DAILY return series instead — bootstrap for Sharpe
    and terminal return, permutation for max drawdown — with the same seeds and
    the same per-seed sign-agreement rule (validator.mc_gate_status).

    Execution stress: validator.monte_carlo charges one extra round trip per
    trade. Nine instruments at 1/9 weight each is one extra round trip of
    portfolio notional in total, spread evenly across the bars of the window.
    """
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
        "mc_basis": "BAR-LEVEL DIAGNOSTIC — not validator.monte_carlo()'s trade-level gate",
        "mc_p5_sharpe": float(np.percentile(sharpes, 5)),
        "mc_p50_sharpe": float(np.percentile(sharpes, 50)),
        "mc_p95_sharpe": float(np.percentile(sharpes, 95)),
        "mc_p5_return": float(np.percentile(finals, 5)),
        "mc_p50_return": float(np.percentile(finals, 50)),
        "mc_p50_maxdd": float(np.percentile(dds, 50)),
        "mc_p95_maxdd": float(np.percentile(dds, 5)),
        "mc_worst_maxdd": float(np.min(dds)),
        "mc_seeds": list(V.MC_SEEDS),
        "mc_sims_per_seed": MC_SIMS_PER_SEED,
        "mc_n_sims": MC_SIMS_PER_SEED * len(V.MC_SEEDS),
        "mc_p5_sharpe_per_seed": [round(x, 4) for x in per_seed_p5],
        "mc_seed_spread_p5_sharpe": float(max(per_seed_p5) - min(per_seed_p5)),
        "mc_gate": V.mc_gate_status(per_seed_p5),
        "mc_extra_cost_note": (f"one extra round trip of portfolio notional "
                               f"({extra_cost * 1e4:.1f} bps) spread across {n} bars"),
    }


def funding_magnitude(pairs: list[str]) -> dict:
    """Measure the funding series the project DOES hold, to size the exclusion."""
    per, spans = {}, []
    for p in pairs:
        stem = p.replace("/", "_").replace(":", "_")
        fp = FUTURES_DIR / f"{stem}-1h-funding_rate.feather"
        if not fp.exists():
            continue
        df = pd.read_feather(fp).set_index("date").sort_index()
        rate = df["open"].astype(float)
        per[p] = {"n_settlements": int(len(rate)),
                  "first": str(rate.index.min().date()),
                  "last": str(rate.index.max().date()),
                  "mean_rate": round(float(rate.mean()), 8),
                  "annualised_pct": round(float(rate.mean()) * 3 * 365 * 100, 3),
                  "share_positive": round(float((rate > 0).mean()), 4)}
        spans += [rate.index.min(), rate.index.max()]
    eq = round(float(np.mean([v["annualised_pct"] for v in per.values()])), 3) if per else None
    return {"included_in_benchmark": False,
            "reason": "no funding series overlaps the benchmark window",
            "coverage_first": str(min(spans).date()) if spans else None,
            "coverage_last": str(max(spans).date()) if spans else None,
            "equal_weight_annualised_pct_paid_by_longs": eq,
            "per_instrument": per}


def _write_series(fp: Path, seg: pd.DataFrame, label: str, closes: pd.DataFrame,
                  per_side: float, boundary: pd.Timestamp) -> None:
    """Write a return series with its split dates embedded in the file itself.

    A-005: "The return series must carry the exact split dates it was computed
    on, so a later candidate can be checked for date-identical overlap." A bare
    CSV does not carry them, and a series whose window has to be looked up
    elsewhere is one that can be silently compared against the wrong window.

    Read with: pd.read_csv(fp, comment="#", index_col=0, parse_dates=True)
    """
    hdr = [
        f"# A-005 perps program benchmark - {label} split return series",
        f"# equal-weight buy-and-hold, 9 OKX USDT perps, {TIMEFRAME} bars",
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
        f"#        entry charged once per instrument on "
        f"{closes.index.min().date()} at {per_side * 1e4:.1f} bps/side; no other cost.",
        f"#        A TEST slice therefore carries NO cost - buy-and-hold was already in",
        f"#        position when TEST began. That is the correct do-nothing baseline.",
        f"# funding: EXCLUDED (no series overlaps this window - see perps_benchmark.json)",
        f"#",
        f"# equity is re-based to 1.0 at the FIRST BAR OF THIS FILE, matching how",
        f"# validate() re-bases each split, so max drawdown here is within-window.",
        f"# ret_net is the series promotion criterion 3 consumes (pair with the",
        f"# candidate's TEST returns on identical dates, or the comparison is void).",
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
    observed_start = closes_all.dropna().index.min()
    if observed_start != start:
        raise RuntimeError(
            f"WINDOW_START {start.date()} is no longer the first bar on which all "
            f"nine instruments have data ({observed_start.date()}). The window is "
            f"pre-registered; resolve deliberately.")

    closes = closes_all.loc[(closes_all.index >= start) & (closes_all.index <= boundary)]
    if closes.isna().any().any():
        raise RuntimeError("NaN close inside the benchmark window")
    V.assert_no_holdout(closes, label="benchmark window", program=PROGRAM)
    split_shape = _check_splits(closes.index)

    bars, trades = build_benchmark(closes, per_side)
    closed_form = assert_closed_form(bars, closes, per_side)

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

    # Harness trade-level MC, called for real so its structural unavailability is
    # on the record rather than asserted, plus the bar-level diagnostic.
    mc_harness = V.monte_carlo(bars, trades, n_sims=MC_SIMS_PER_SEED,
                               execution_mode=EXECUTION_MODE, bars_per_year=BARS_PER_YEAR)
    mc_bar = bar_level_mc(bars, round_trip)

    # DSR on the TEST split — validate()'s own convention (validator.py:1387).
    # At n_trials=1, expected_max_sharpe() returns exactly 0.0, so the hurdle sr0
    # is 0 and DSR reduces to P(true Sharpe > 0). The estimator-proxy warning
    # still fires (the ledger is empty by design) but CANNOT affect this number:
    # trial_sharpe_var only enters through sr0, which is 0 at one trial.
    dsr_test = V.deflated_sharpe(te_bars["ret_net"].dropna().tolist(), N_TRIALS)
    dsr_test["window"] = "test_split"
    dsr_test["basis"] = "per_bar"
    dsr_full = V.deflated_sharpe(bars["ret_net"].dropna().tolist(), N_TRIALS)
    dsr_test["dsr_full_window_diagnostic"] = dsr_full.get("dsr")

    funding = funding_magnitude(pairs)

    # ---- artifacts -------------------------------------------------------- #
    test_csv = OUT_DIR / "perps_benchmark_TEST_returns.csv"
    full_csv = OUT_DIR / "perps_benchmark_FULL_returns.csv"
    _write_series(test_csv, te_bars, "TEST", closes, per_side, boundary)
    _write_series(full_csv, bars, "FULL", closes, per_side, boundary)

    record = {
        "task": "A-005",
        "artifact": "perps program benchmark — equal-weight buy-and-hold, 9 OKX USDT perps",
        "generated_by": "user_data/research/perps_benchmark.py",
        "program": PROGRAM,
        "instruments": pairs,
        "timeframe": TIMEFRAME,
        "window": {"start": str(closes.index.min().date()),
                   "end": str(closes.index.max().date()),
                   "holdout_boundary": str(boundary.date()),
                   "start_rationale": "first bar on which all nine instruments exist (BNB inception)",
                   **split_shape},
        "split_dates": {"train_end": SPLIT_DATES[0], "val_end": SPLIT_DATES[1],
                        "test_end": SPLIT_DATES[2], "mode": "date_pinned",
                        "method": "70/15/15 of the benchmark window, then frozen as dates"},
        "cost_model": V.cost_model_snapshot(EXECUTION_MODE),
        "cost_application": (f"entry charged ONCE per instrument at "
                             f"{per_side * 1e4:.1f} bps/side on {SPLIT_DATES and closes.index.min().date()}; "
                             f"no rebalancing turnover; terminal value is mark-to-market "
                             f"(an exit would cost a further {per_side * 1e4:.1f} bps)"),
        "n_trials": N_TRIALS,
        "funding": funding,
        "survivorship": SURVIVORSHIP_NOTE,
        "construction_check": closed_form,
        "full": {**m_full, "max_year_share": conc.get("max_year_share")},
        "train": m_tr, "val": m_vl, "test": m_te,
        "yearly": yearly,
        "wf": wf,
        "mc_trade_level_harness": mc_harness,
        "mc_bar_level_diagnostic": mc_bar,
        "dsr": dsr_test,
        "data_manifest": V.data_integrity_snapshot(),
        "warnings": (V.data_integrity_warnings() + V.dsr_warnings(dsr_test)
                     + V.cost_model_warnings(EXECUTION_MODE)),
        "artifacts": {"test_returns_csv": str(test_csv.relative_to(REPO_ROOT)).replace("\\", "/"),
                      "full_returns_csv": str(full_csv.relative_to(REPO_ROOT)).replace("\\", "/")},
    }
    record["defect_presumption_check"] = defect_presumption_check(
        m_full, {"full": record["full"], "train": m_tr, "val": m_vl, "test": m_te}, per_side)
    json_fp = OUT_DIR / "perps_benchmark.json"
    json_fp.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")

    _print(record, funding)
    print(f"\nWrote:\n  {test_csv.relative_to(REPO_ROOT)}"
          f"\n  {full_csv.relative_to(REPO_ROOT)}"
          f"\n  {json_fp.relative_to(REPO_ROOT)}")
    return record


def _print(r: dict, funding: dict) -> None:
    w, s = r["window"], r["split_dates"]
    line = "=" * 78
    print(f"\n{line}\nPERPS PROGRAM BENCHMARK (A-005) — equal-weight buy-and-hold, 9 OKX USDT perps\n{line}")
    print(f"Instruments : {', '.join(p.split('/')[0] for p in r['instruments'])}  ({r['timeframe']})")
    print(f"Window      : {w['start']} .. {w['end']}  ({w['n_bars']} bars)  "
          f"holdout after {w['holdout_boundary']}")
    print(f"Splits      : {s['mode']}  train<={s['train_end']} ({w['train_bars']})  "
          f"val<={s['val_end']} ({w['val_bars']})  test<={s['test_end']} ({w['test_bars']})")
    dm = r["data_manifest"]
    print(f"Data        : {'VERIFIED' if dm['verified'] else 'NOT VERIFIED'} "
          f"({dm['files_checked']} files, manifest {dm['manifest_built_utc']})")
    print(f"Costs       : {r['cost_model']['summary']}")
    print(f"              {r['cost_application']}")

    print(f"\n{'-'*78}\nFUNDING — EXCLUDED\n{'-'*78}")
    print(FUNDING_NOTE)
    print(f"  measured coverage {funding['coverage_first']} .. {funding['coverage_last']} "
          f"(benchmark window ends {w['end']} — NO OVERLAP)")
    for p, v in funding["per_instrument"].items():
        print(f"    {p.split('/')[0]:5s} n={v['n_settlements']:4d}  mean {v['mean_rate']:+.8f}  "
              f"ann {v['annualised_pct']:+6.2f}%  positive {v['share_positive']:.1%}")
    print(f"  equal-weight annualised funding paid by longs: "
          f"{funding['equal_weight_annualised_pct_paid_by_longs']:+.3f}%/yr")

    print(f"\n{'-'*78}\nSURVIVORSHIP\n{'-'*78}")
    print(SURVIVORSHIP_NOTE)

    cf = r["construction_check"]
    print(f"{'-'*78}\nCONSTRUCTION CHECK — closed form, independent of the implementation\n{'-'*78}")
    print(f"  {cf['identity']}")
    print(f"  closed form {cf['closed_form_terminal_equity']:.12f}   "
          f"constructed {cf['constructed_terminal_equity']:.12f}   "
          f"abs error {cf['abs_error']:.3e}  -> PASS (raises otherwise)")

    dp = r["defect_presumption_check"]
    print(f"\n{'-'*78}\n>100% CAGR DEFECT PRESUMPTION — mandatory verification\n{'-'*78}")
    print(f"  Triggered on: {', '.join(dp['windows_over_100pct_cagr']) or 'none'}")
    for k in ("costs_applied", "signal_lag", "indicator_warmup", "survivorship"):
        print(f"  - {k}: {dp[k]}")
    print(f"  => {dp['conclusion']}")

    print(f"\n{'-'*78}\nHEADLINE — the numbers the promotion rule consumes\n{'-'*78}")
    t = r["test"]
    print(f"  TEST Sharpe (per-period) : {t['sharpe_per_period']:+.6f}   <- criterion 3 input")
    print(f"  TEST Sharpe (annualised) : {t['sharpe_annualised']:+.4f}   [{t['annualisation']}]")
    print(f"  TEST MaxDD               : {t['max_dd']*100:+.2f}%   -> criterion 4 cap "
          f"{t['max_dd']*1.25*100:+.2f}%")
    print(f"  TEST bars (N)            : {t['n_bars']}")
    print(f"  DSR (TEST, n_trials=1)   : {r['dsr'].get('dsr')}   sr0 {r['dsr'].get('sr0_benchmark')}")

    print(f"\n{'-'*78}\nFULL METRIC SET\n{'-'*78}")
    print(f"{'window':8s} {'return':>9s} {'CAGR':>9s} {'Sharpe':>9s} {'per-per':>10s} "
          f"{'Sortino':>9s} {'MaxDD':>9s} {'bars':>5s}")
    for lbl in ("full", "train", "val", "test"):
        m = r[lbl]
        print(f"{lbl:8s} {m['total_return']*100:+8.2f}% {m['cagr']*100:+8.2f}% "
              f"{m['sharpe_annualised']:+9.4f} {m['sharpe_per_period']:+10.6f} "
              f"{m['sortino']:+9.4f} {m['max_dd']*100:+8.2f}% {m['n_bars']:>5d}")
    print(f"\n  Profit factor / win rate / trade count are FULL-WINDOW ONLY: "
          f"PF {r['full']['profit_factor']}, win rate {r['full']['win_rate']:.1%}, "
          f"{r['full']['n_trades']} trades")
    print(f"    ({_TRADE_STATS_NA}) — they are blanked on train/val/test/WF rows above.")
    print(f"  years {r['full']['years']}   max single-year share of $ profit "
          f"{r['full']['max_year_share']:.4f}")
    print("  yearly: " + "  ".join(f"{y}:{v*100:+.1f}%" for y, v in r["yearly"].items()))

    print("\n  walk-forward (validator.walk_forward window arithmetic, anchored, 4 OOS windows):")
    for x in r["wf"]:
        print(f"    W{x['window']}  {x['is_end']} .. {x['oos_end']}  "
              f"ret {x['total_return']*100:+7.2f}%  Sharpe {x['sharpe_annualised']:+7.4f}  "
              f"MaxDD {x['max_dd']*100:+7.2f}%  bars {x['n_bars']}")
    wf_pos = sum(1 for x in r["wf"] if x["total_return"] > 0)
    print(f"    positive in {wf_pos}/{len(r['wf'])} OOS windows")

    mh, mb = r["mc_trade_level_harness"], r["mc_bar_level_diagnostic"]
    print(f"\n  Monte Carlo — harness trade-level gate: {mh.get('mc_gate')} "
          f"({mh.get('mc_note', 'n/a')})")
    print("    Structural, not a defect: buy-and-hold holds nine positions and closes none, so the")
    print("    trade log can never reach validator.monte_carlo()'s 30-trade floor. The bar-level")
    print("    diagnostic below is the substitute and is labelled as such.")
    print(f"  Monte Carlo — bar-level diagnostic ({mb['mc_n_sims']} sims, {len(mb['mc_seeds'])} seeds, "
          f"{mb['mc_extra_cost_note']}):")
    print(f"    GATE {mb['mc_gate']}   per-seed p5 Sharpe {mb['mc_p5_sharpe_per_seed']}   "
          f"spread {mb['mc_seed_spread_p5_sharpe']:.4f}")
    print(f"    Sharpe p5 {mb['mc_p5_sharpe']:+.4f}  p50 {mb['mc_p50_sharpe']:+.4f}  "
          f"p95 {mb['mc_p95_sharpe']:+.4f}")
    print(f"    Return p5 {mb['mc_p5_return']*100:+.2f}%  p50 {mb['mc_p50_return']*100:+.2f}%")
    print(f"    MaxDD  p50 {mb['mc_p50_maxdd']*100:+.2f}%  p95(worst tail) "
          f"{mb['mc_p95_maxdd']*100:+.2f}%  worst {mb['mc_worst_maxdd']*100:+.2f}%")
    print("    NOTE: permuted-order MaxDD overstates dispersion and MUST NOT feed promotion")
    print("          criterion 4 — that uses the realized TEST MaxDD above.")

    d = r["dsr"]
    print(f"\n  DSR (TEST split, per_bar, n_trials={d.get('n_trials')}): {d.get('dsr')}   "
          f"sr_hat {d.get('sr_hat_per_trade')}  sr0 {d.get('sr0_benchmark')}  n_obs {d.get('n_obs')}")
    print(f"    trial_var_source={d.get('trial_var_source')} (ledger rows {d.get('n_trials_recorded')})"
          f"   full-window DSR (diagnostic only): {d.get('dsr_full_window_diagnostic')}")
    print("    At n_trials=1 expected_max_sharpe() returns exactly 0.0, so sr0=0 and DSR reduces to")
    print("    P(true Sharpe > 0). The estimator-proxy warning below cannot affect this figure:")
    print("    trial_sharpe_var enters only through sr0. This is the 'mechanically high by")
    print("    construction' DSR the manual describes — it is NOT a quality signal.")

    print(f"\n{'-'*78}\nWARNINGS — reproduce verbatim in any report quoting these numbers\n{'-'*78}")
    for x in r["warnings"]:
        print(f"  !! {x}\n")


if __name__ == "__main__":
    main()
