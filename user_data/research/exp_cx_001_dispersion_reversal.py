"""EXP-CX-001: high-dispersion cross-sectional 24-hour momentum reversal.

The experiment is intentionally a single pre-registered cell.  Signals observed at
bar close execute two hourly bars later; a high-dispersion episode can create only
one trade during the 24-hour holding/cooldown interval.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_entry_weights(momentum: pd.Series, names_per_leg: int = 2) -> pd.Series:
    """Return gross-one, dollar-neutral reversal weights for momentum extremes."""
    if names_per_leg < 1 or len(momentum.dropna()) < 2 * names_per_leg:
        raise ValueError("not enough valid instruments for both legs")
    ordered = momentum.dropna().sort_values()
    weights = pd.Series(0.0, index=momentum.index, dtype=float)
    weights.loc[ordered.index[:names_per_leg]] = 0.5 / names_per_leg
    weights.loc[ordered.index[-names_per_leg:]] = -0.5 / names_per_leg
    return weights


def event_onsets(high_dispersion: pd.Series, cooldown_bars: int) -> pd.Series:
    """Select low-to-high transitions separated by at least ``cooldown_bars``."""
    if cooldown_bars < 1:
        raise ValueError("cooldown_bars must be positive")
    crossings = high_dispersion.fillna(False) & ~high_dispersion.shift(1, fill_value=False)
    selected = pd.Series(False, index=high_dispersion.index)
    last = -cooldown_bars
    for pos in np.flatnonzero(crossings.to_numpy()):
        if pos - last >= cooldown_bars:
            selected.iloc[pos] = True
            last = int(pos)
    return selected


def dispersion_event_mask(
    momentum: pd.DataFrame,
    lookback: int = 720,
    quantile: float = 0.80,
    cooldown_bars: int = 24,
) -> tuple[pd.Series, pd.Series]:
    """Return causal high-dispersion onsets and their trailing thresholds."""
    dispersion = momentum.std(axis=1, ddof=0)
    threshold = dispersion.shift(1).rolling(lookback, min_periods=lookback).quantile(quantile)
    high = dispersion > threshold
    return event_onsets(high, cooldown_bars), threshold


def trade_returns(
    opens: pd.DataFrame,
    signal_position: int,
    weights: pd.Series,
    hold_bars: int,
    delay_bars: int,
    per_side_bps: pd.Series,
) -> tuple[float, float, pd.Timestamp, pd.Timestamp]:
    """Calculate one delayed open-to-open trade with weighted round-trip costs."""
    entry_pos = signal_position + delay_bars
    exit_pos = entry_pos + hold_bars
    if entry_pos < 0 or exit_pos >= len(opens):
        raise IndexError("trade extends beyond available bars")
    aligned_weights = weights.reindex(opens.columns).fillna(0.0)
    entry = opens.iloc[entry_pos]
    exit_ = opens.iloc[exit_pos]
    gross = float((aligned_weights * (exit_ / entry - 1.0)).sum())
    costs = per_side_bps.reindex(opens.columns).fillna(0.0) / 10_000.0
    round_trip = float((aligned_weights.abs() * costs * 2.0).sum())
    return gross, gross - round_trip, opens.index[entry_pos], opens.index[exit_pos]


def build_trade_table(
    opens: pd.DataFrame,
    momentum: pd.DataFrame,
    events: pd.Series,
    per_side_bps: pd.Series,
    hold_bars: int = 24,
    delay_bars: int = 2,
) -> pd.DataFrame:
    """Build one row per fully executable event trade."""
    rows: list[dict[str, object]] = []
    for signal_pos in np.flatnonzero(events.reindex(opens.index, fill_value=False).to_numpy()):
        if signal_pos + delay_bars + hold_bars >= len(opens):
            continue
        weights = build_entry_weights(momentum.iloc[signal_pos])
        gross, net, entry_time, exit_time = trade_returns(
            opens,
            int(signal_pos),
            weights,
            hold_bars,
            delay_bars,
            per_side_bps,
        )
        row: dict[str, object] = {
            "signal_time": opens.index[signal_pos],
            "entry_time": entry_time,
            "exit_time": exit_time,
            "gross_return": gross,
            "net_return": net,
            "round_trip_cost": gross - net,
        }
        row.update({f"weight_{name}": float(value) for name, value in weights.items()})
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    futures = root / "user_data" / "data" / "okx" / "futures"
    raw_dir = root / "research" / "results" / "EXP-CX-001_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    instruments = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK"]

    frames = {}
    for instrument in instruments:
        path = futures / f"{instrument}_USDT_USDT-1h-futures.feather"
        frame = pd.read_feather(path).set_index("date").sort_index()
        frames[instrument] = frame[~frame.index.duplicated(keep="last")]
    common = frames[instruments[0]].index
    for instrument in instruments[1:]:
        common = common.intersection(frames[instrument].index)
    common = common.sort_values()
    close = pd.DataFrame({i: frames[i]["close"].reindex(common) for i in instruments})
    opens = pd.DataFrame({i: frames[i]["open"].reindex(common) for i in instruments})

    cost_path = root / "user_data" / "research" / "data" / "okx_micro" / "adverse_selection_results.csv"
    cost_frame = pd.read_csv(cost_path).set_index("inst")
    per_side_bps = pd.Series(
        {i: float(cost_frame.loc[i, "half"] + 5.0 + cost_frame.loc[i, "slip_$5k"]) for i in instruments}
    )

    momentum = close.pct_change(24)
    events, threshold = dispersion_event_mask(momentum, lookback=720, quantile=0.80, cooldown_bars=24)
    trades = build_trade_table(opens, momentum, events, per_side_bps, hold_bars=24, delay_bars=2)
    train_end = pd.Timestamp("2024-11-22 23:00", tz="UTC")
    train = trades[trades["signal_time"] <= train_end].copy()

    weight_cols = [f"weight_{i}" for i in instruments]
    signal_positions = common.get_indexer(pd.DatetimeIndex(train["signal_time"]))
    weights = train[weight_cols].to_numpy(dtype=float)
    entry_positions = signal_positions + 2
    exit_positions = entry_positions + 24
    realized = opens.to_numpy()[exit_positions] / opens.to_numpy()[entry_positions] - 1.0
    contributions = weights * realized
    breadth = int((np.nanmean(contributions, axis=0) > 0).sum()) if len(train) else 0

    rng = np.random.default_rng(20260904)
    fwd = opens.shift(-26).to_numpy() / opens.shift(-2).to_numpy() - 1.0
    null_means = np.empty(1000, dtype=float)
    if len(train):
        train_limit = int(common.searchsorted(train_end, side="right"))
        null_start = 720
        null_span = train_limit - 26 - null_start
        for draw in range(1000):
            shift = int(rng.integers(1, null_span))
            shifted_rows = (signal_positions - null_start + shift) % null_span + null_start
            null_means[draw] = np.nanmean(np.sum(weights * fwd[shifted_rows], axis=1))
    else:
        null_means.fill(np.nan)

    mean_gross = float(train["gross_return"].mean()) if len(train) else float("nan")
    mean_net = float(train["net_return"].mean()) if len(train) else float("nan")
    mean_cost = float(train["round_trip_cost"].mean()) if len(train) else float("nan")
    empirical_p = float((1 + np.sum(null_means >= mean_gross)) / 1001) if len(train) else float("nan")
    gates = {
        "n_events_at_least_50": bool(len(train) >= 50),
        "gross_at_least_2x_cost": bool(mean_gross >= 2 * mean_cost),
        "breadth_at_least_5_of_9": bool(breadth >= 5),
        "placebo_p_at_most_0_05": bool(empirical_p <= 0.05),
    }
    passed = all(gates.values())
    summary = {
        "experiment": "CRYPTO-EXP-CX-001",
        "pre_registered_cell": "dispersion_p80_x_mom24_reversal_2v2_hold24_delay2",
        "common_bars": int(len(common)),
        "data_start": str(common.min()),
        "data_end": str(common.max()),
        "train_end": str(train_end),
        "train_events": int(len(train)),
        "mean_gross_return": mean_gross,
        "mean_net_return": mean_net,
        "mean_round_trip_cost": mean_cost,
        "gross_to_cost": float(mean_gross / mean_cost) if mean_cost else float("nan"),
        "positive_instrument_breadth": breadth,
        "placebo_draws": 1000,
        "placebo_seed": 20260904,
        "placebo_p95_mean_gross": float(np.nanquantile(null_means, 0.95)),
        "placebo_empirical_p_one_tailed": empirical_p,
        "gates": gates,
        "pre_gate_passed": passed,
        "trials_spent": 0,
        "verdict": "CONTINUE_TO_VALIDATION" if passed else "REJECT_PRE_GATE",
    }
    train.to_csv(raw_dir / "train_trades.csv", index=False)
    pd.DataFrame({"null_mean_gross": null_means}).to_csv(raw_dir / "placebo_means.csv", index=False)
    pd.DataFrame({"dispersion_threshold": threshold, "event": events.astype(int)}).to_csv(
        raw_dir / "event_series.csv"
    )
    (raw_dir / "pregate_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not passed:
        raise SystemExit(2)
