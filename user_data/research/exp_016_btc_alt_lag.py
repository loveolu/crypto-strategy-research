"""CRYPTO-EXP-016: BTC shock/rebound leading lagging altcoins."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import numpy as np


def resample_ohlcv_4h(hourly: pd.DataFrame) -> pd.DataFrame:
    """Build UTC-anchored 4h candles from complete groups of four hourly bars."""
    bars = hourly.resample("4h", origin="epoch").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )
    counts = hourly["close"].resample("4h", origin="epoch").count()
    return bars.loc[counts == 4].dropna()


def complementary_boolean_masks(values: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Return explicitly typed regime masks, treating unavailable history as false."""
    above = values.fillna(False).astype(bool).to_numpy(dtype=bool)
    return above, np.logical_not(above)


def train_shock_threshold(
    btc: pd.DataFrame, train_end: pd.Timestamp, quantile: float = 0.10
) -> float:
    """Calculate the shock cutoff without allowing post-TRAIN observations."""
    returns = btc.loc[:train_end, "close"].pct_change().dropna()
    return float(returns.quantile(quantile))


def detect_events(
    btc: pd.DataFrame,
    alt: pd.DataFrame,
    shock_threshold: float,
    instrument: str,
    entry_delay_bars: int = 0,
) -> pd.DataFrame:
    """Generate next-open, one-full-bar trades from completed signal bars."""
    aligned = pd.DataFrame(
        {
            "btc_return": btc["close"].pct_change(),
            "alt_return": alt["close"].pct_change(),
            "entry_open": alt["open"].shift(-(1 + entry_delay_bars)),
            "exit_open": alt["open"].shift(-(2 + entry_delay_bars)),
        }
    ).dropna()
    signal = (
        (aligned["btc_return"].shift(1) <= shock_threshold)
        & (aligned["btc_return"] > 0.0)
        & (aligned["alt_return"] <= 0.0)
    )
    rows = []
    occupied_until = None
    for signal_time, row in aligned.loc[signal].iterrows():
        entry_time = alt.index[alt.index.get_loc(signal_time) + 1 + entry_delay_bars]
        exit_time = alt.index[alt.index.get_loc(signal_time) + 2 + entry_delay_bars]
        if occupied_until is not None and entry_time < occupied_until:
            continue
        gross = float(row["exit_open"] / row["entry_open"] - 1.0)
        rows.append(
            {
                "instrument": instrument,
                "signal_time": signal_time,
                "entry_time": entry_time,
                "exit_time": exit_time,
                "entry_open": float(row["entry_open"]),
                "exit_open": float(row["exit_open"]),
                "gross": gross,
            }
        )
        occupied_until = exit_time
    return pd.DataFrame(rows)


def pre_gate_summary(
    events: pd.DataFrame,
    placebo_p: float,
    round_trip_cost_bps: float,
    expected_instruments: int = 8,
) -> dict:
    """Evaluate the four frozen TRAIN-only advancement conditions."""
    grouped = events.groupby("instrument")["gross"]
    counts = grouped.size()
    means = grouped.mean()
    expectancy_bps = float(events["gross"].mean() * 10_000.0) if len(events) else 0.0
    positive = int((means > 0.0).sum())
    sample_ok = bool(
        len(events) >= 100
        and len(counts) == expected_instruments
        and (counts >= 10).all()
    )
    conditions = {
        "sample": sample_ok,
        "positive_pooled_mean": expectancy_bps > 0.0,
        "breadth": positive >= 5,
        "placebo": placebo_p < 0.05,
        "economic_size": expectancy_bps >= round_trip_cost_bps,
    }
    return {
        "trades": int(len(events)),
        "trades_by_instrument": {str(k): int(v) for k, v in counts.items()},
        "gross_expectancy_bps": expectancy_bps,
        "positive_instruments": positive,
        "placebo_p": float(placebo_p),
        "round_trip_cost_bps": float(round_trip_cost_bps),
        "conditions": conditions,
        "passes": bool(all(conditions.values())),
    }


def circular_shift_placebo(
    btc_trigger: np.ndarray,
    alt_streams: dict[str, tuple[np.ndarray, np.ndarray]],
    permutations: int = 999,
    seed: int = 16,
) -> float:
    """Two-sided timing placebo, shifting each alt's condition/outcome jointly."""
    trigger = np.asarray(btc_trigger, dtype=bool)

    def statistic(shifts: dict[str, int]) -> float:
        samples = []
        for instrument, (lag_condition, forward_return) in alt_streams.items():
            condition = np.roll(np.asarray(lag_condition, dtype=bool), shifts.get(instrument, 0))
            outcome = np.roll(np.asarray(forward_return, dtype=float), shifts.get(instrument, 0))
            valid = trigger & condition & np.isfinite(outcome)
            samples.extend(outcome[valid].tolist())
        return float(np.mean(samples)) if samples else 0.0

    zero = {instrument: 0 for instrument in alt_streams}
    observed = statistic(zero)
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(permutations):
        shifts = {
            instrument: int(rng.integers(1, len(trigger))) for instrument in alt_streams
        }
        null.append(statistic(shifts))
    extreme = int(np.sum(np.abs(null) >= abs(observed)))
    return float((extreme + 1) / (permutations + 1))


ROOT = Path(__file__).resolve().parents[2]
FUTURES = ROOT / "user_data" / "data" / "okx" / "futures"
OUTPUT = ROOT / "research" / "measurements" / "EXP016"
ALTS = ["ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK"]
TRAIN_START = pd.Timestamp("2023-01-22", tz="UTC")
TRAIN_END = pd.Timestamp("2024-11-22 23:00", tz="UTC")
DATA_END = pd.Timestamp("2026-09-01", tz="UTC")
SPLITS = {
    "TRAIN": (TRAIN_START, TRAIN_END),
    "VAL": (pd.Timestamp("2024-11-23", tz="UTC"), pd.Timestamp("2025-04-21 23:00", tz="UTC")),
    "TEST": (pd.Timestamp("2025-04-22", tz="UTC"), pd.Timestamp("2025-09-19 23:00", tz="UTC")),
    "FWD": (pd.Timestamp("2025-09-20", tz="UTC"), DATA_END),
    "OOS": (pd.Timestamp("2024-11-23", tz="UTC"), DATA_END),
}


def _load(instrument: str) -> pd.DataFrame:
    path = FUTURES / f"{instrument}_USDT_USDT-1h-futures.feather"
    frame = pd.read_feather(path).set_index("date").sort_index()
    return resample_ohlcv_4h(frame.loc[~frame.index.duplicated()])


def _round_trip_cost_bps(events: pd.DataFrame) -> float:
    costs = pd.read_csv(
        ROOT / "user_data" / "research" / "data" / "okx_micro" / "adverse_selection_results.csv"
    ).set_index("inst")
    per_instrument = 2.0 * (costs["half"] + 5.0 + costs["slip_$5k"])
    weights = events["instrument"].value_counts(normalize=True)
    return float(sum(weights.get(name, 0.0) * per_instrument.loc[name] for name in ALTS))


def run_train() -> tuple[pd.DataFrame, dict]:
    frames = {name: _load(name) for name in ["BTC", *ALTS]}
    common = frames["BTC"].index
    for frame in frames.values():
        common = common.intersection(frame.index)
    common = common[(common >= TRAIN_START) & (common <= TRAIN_END)]
    frames = {name: frame.loc[common] for name, frame in frames.items()}
    btc = frames["BTC"]
    threshold = train_shock_threshold(btc, TRAIN_END)

    events = []
    btc_return = btc["close"].pct_change()
    trigger = ((btc_return.shift(1) <= threshold) & (btc_return > 0.0)).to_numpy()
    streams = {}
    for instrument in ALTS:
        alt = frames[instrument]
        event = detect_events(btc, alt, threshold, instrument)
        event = event[event["exit_time"] <= TRAIN_END]
        events.append(event)
        streams[instrument] = (
            (alt["close"].pct_change() <= 0.0).fillna(False).to_numpy(),
            (alt["open"].shift(-2) / alt["open"].shift(-1) - 1.0).to_numpy(),
        )
    trades = pd.concat(events, ignore_index=True).sort_values(["signal_time", "instrument"])
    placebo_p = circular_shift_placebo(trigger, streams, permutations=999, seed=16)
    cost_bps = _round_trip_cost_bps(trades)
    summary = pre_gate_summary(trades, placebo_p, cost_bps)
    summary.update(
        {
            "experiment_id": "CRYPTO-EXP-016",
            "status": "TRAIN_PRE_GATE_PASS" if summary["passes"] else "REJECTED_TRAIN_PRE_GATE",
            "train_start": TRAIN_START.isoformat(),
            "train_end": TRAIN_END.isoformat(),
            "btc_shock_quantile": 0.10,
            "btc_shock_threshold_pct": threshold * 100.0,
            "permutations": 999,
            "held_out_opened": bool(summary["passes"]),
        }
    )
    return trades, summary


def _cost_map() -> dict[str, float]:
    costs = pd.read_csv(
        ROOT / "user_data" / "research" / "data" / "okx_micro" / "adverse_selection_results.csv"
    ).set_index("inst")
    return {name: float(2.0 * (costs.loc[name, "half"] + 5.0 + costs.loc[name, "slip_$5k"])) for name in ALTS}


def _performance(
    trades: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, cost_mult: float = 1.0
) -> dict:
    selected = trades[(trades["entry_time"] >= start) & (trades["exit_time"] <= end)].copy()
    costs = _cost_map()
    selected["net"] = selected["gross"] - selected["instrument"].map(costs) * cost_mult / 10_000.0
    index = pd.date_range(start.floor("4h"), end.floor("4h"), freq="4h", tz="UTC")
    returns = pd.Series(0.0, index=index)
    for exit_time, value in selected.groupby("exit_time")["net"].sum().items():
        if exit_time in returns.index:
            returns.loc[exit_time] += float(value) / len(ALTS)
    equity = (1.0 + returns).cumprod()
    years = max((end - start).total_seconds() / (365.25 * 86400), 1 / 365.25)
    total = float(equity.iloc[-1] - 1.0) if len(equity) else 0.0
    annual = float(equity.iloc[-1] ** (1.0 / years) - 1.0) if len(equity) else 0.0
    drawdown = float((equity / equity.cummax() - 1.0).min()) if len(equity) else 0.0
    downside = np.sqrt(np.mean(np.minimum(returns.to_numpy(), 0.0) ** 2))
    std = float(returns.std())
    trade_net = selected["net"]
    winning_trades = trade_net[trade_net > 0]
    losing_trades = trade_net[trade_net < 0]
    wins = winning_trades.sum()
    losses = -losing_trades.sum()
    losing_streak = longest_losing_streak = 0
    for value in trade_net:
        losing_streak = losing_streak + 1 if value < 0 else 0
        longest_losing_streak = max(longest_losing_streak, losing_streak)
    daily = (1.0 + returns).resample("1D").prod() - 1.0
    weekly = (1.0 + returns).resample("W").prod() - 1.0
    monthly = (1.0 + returns).resample("ME").prod() - 1.0
    drawdown_series = equity / equity.cummax() - 1.0
    underwater = drawdown_series < 0
    recovery = longest_recovery = 0
    for value in underwater:
        recovery = recovery + 1 if value else 0
        longest_recovery = max(longest_recovery, recovery)
    return {
        "trades": int(len(selected)),
        "return_pct": total * 100.0,
        "annualized_pct": annual * 100.0,
        "max_drawdown_pct": drawdown * 100.0,
        "sharpe": float(returns.mean() / std * np.sqrt(6 * 365.25)) if std > 0 else 0.0,
        "sortino": float(returns.mean() / downside * np.sqrt(6 * 365.25)) if downside > 0 else 0.0,
        "calmar": float(annual / abs(drawdown)) if drawdown < 0 else None,
        "profit_factor": float(wins / losses) if losses > 0 else None,
        "win_rate_pct": float((trade_net > 0).mean() * 100.0) if len(selected) else None,
        "average_winner_bps": float(winning_trades.mean() * 10_000.0) if len(winning_trades) else None,
        "average_loser_bps": float(losing_trades.mean() * 10_000.0) if len(losing_trades) else None,
        "median_trade_bps": float(trade_net.median() * 10_000.0) if len(selected) else None,
        "gross_expectancy_bps": float(selected["gross"].mean() * 10_000.0) if len(selected) else None,
        "net_expectancy_bps": float(trade_net.mean() * 10_000.0) if len(selected) else None,
        "fees_slippage_pct_of_sleeved_equity": float(
            selected["instrument"].map(costs).sum() * cost_mult / 10_000.0 / len(ALTS) * 100.0
        ),
        "trades_per_day": float(len(selected) / max((end - start).total_seconds() / 86400, 1.0)),
        "average_hold_hours": 4.0,
        "long_exposure_pct": float(len(selected) * 4 / len(ALTS) / max((end - start).total_seconds() / 3600, 1) * 100),
        "short_exposure_pct": 0.0,
        "turnover_x_equity": float(len(selected) * 2 / len(ALTS)),
        "profitable_active_days_pct": float((daily[daily != 0] > 0).mean() * 100.0) if (daily != 0).any() else None,
        "max_intraday_drawdown_pct": float(returns.min() * 100.0),
        "longest_losing_streak": int(longest_losing_streak),
        "recovery_time_hours": int(longest_recovery * 4),
        "worst_day_pct": float(daily.min() * 100.0),
        "worst_week_pct": float(weekly.min() * 100.0),
        "worst_month_pct": float(monthly.min() * 100.0),
        "monthly_returns_pct": {str(k.date()): float(v * 100.0) for k, v in monthly.items()},
    }


def _all_events(frames: dict[str, pd.DataFrame], threshold: float, delay: int = 0) -> pd.DataFrame:
    events = [
        detect_events(frames["BTC"], frames[name], threshold, name, entry_delay_bars=delay)
        for name in ALTS
    ]
    return pd.concat(events, ignore_index=True).sort_values(["signal_time", "instrument"])


def run_held_out(threshold_pct: float) -> tuple[pd.DataFrame, dict]:
    frames = {name: _load(name) for name in ["BTC", *ALTS]}
    common = frames["BTC"].index
    for frame in frames.values():
        common = common.intersection(frame.index)
    common = common[(common >= TRAIN_START) & (common <= DATA_END)]
    frames = {name: frame.loc[common] for name, frame in frames.items()}
    threshold = threshold_pct / 100.0
    events = _all_events(frames, threshold)
    expected = {name: _performance(events, *bounds) for name, bounds in SPLITS.items()}
    oos_start, oos_end = SPLITS["OOS"]
    cost_stress = {
        str(mult): _performance(events, oos_start, oos_end, cost_mult=mult)
        for mult in (0.0, 1.0, 2.0, 3.0)
    }
    delay = {
        str(bars): _performance(_all_events(frames, threshold, delay=bars), oos_start, oos_end)
        for bars in (1, 2)
    }
    oos = events[(events["entry_time"] >= oos_start) & (events["exit_time"] <= oos_end)].copy()
    costs = _cost_map()
    oos["net"] = oos["gross"] - oos["instrument"].map(costs) / 10_000.0
    cutoff = oos["net"].quantile(0.95)
    trimmed = events.drop(index=oos[oos["net"] >= cutoff].index)
    top_removed = _performance(trimmed, oos_start, oos_end)
    coin = {
        name: {
            "trades": int(len(group)),
            "net_expectancy_bps": float(
                (group["gross"] - costs[name] / 10_000.0).mean() * 10_000.0
            ),
        }
        for name, group in oos.groupby("instrument")
    }
    segment_positive = sum(expected[name]["return_pct"] > 0 for name in ("VAL", "TEST", "FWD"))
    coin_positive = sum(value["net_expectancy_bps"] > 0 for value in coin.values())
    recent = {
        str(days): _performance(events, max(oos_start, oos_end - pd.Timedelta(days=days)), oos_end)
        for days in (30, 90, 180, 365)
    }
    daily_btc = frames["BTC"]["close"].resample("1D").last().dropna()
    prior_daily_trend = (daily_btc > daily_btc.rolling(200).mean()).shift(1)
    trend_at_signal, inverse_trend = complementary_boolean_masks(
        prior_daily_trend.reindex(oos["signal_time"], method="ffill")
    )
    regime = {}
    for label, mask in {
        "btc_above_sma200": trend_at_signal,
        "btc_below_sma200": inverse_trend,
    }.items():
        subset = oos.loc[mask]
        net = subset["gross"] - subset["instrument"].map(costs) / 10_000.0
        regime[label] = {
            "trades": int(len(subset)),
            "net_expectancy_bps": float(net.mean() * 10_000.0) if len(net) else None,
            "win_rate_pct": float((net > 0).mean() * 100.0) if len(net) else None,
        }
    conditions = {
        "oos_return_positive": expected["OOS"]["return_pct"] > 0,
        "oos_sharpe_above_0_5": expected["OOS"]["sharpe"] > 0.5,
        "oos_profit_factor_above_1": (expected["OOS"]["profit_factor"] or 0) > 1.0,
        "two_of_three_segments_positive": segment_positive >= 2,
        "five_of_eight_alts_positive": coin_positive >= 5,
        "two_x_cost_positive": cost_stress["2.0"]["return_pct"] > 0,
        "one_bar_delay_positive": delay["1"]["return_pct"] > 0,
        "top_five_pct_removed_positive": top_removed["return_pct"] > 0,
    }
    summary = {
        "status": "PROMISING" if all(conditions.values()) else "REJECTED_HELD_OUT",
        "conditions": conditions,
        "segments": expected,
        "cost_stress_oos": cost_stress,
        "entry_delay_oos": delay,
        "top_five_pct_removed_oos": top_removed,
        "coin_oos": coin,
        "recent_windows": recent,
        "btc_trend_regime_oos": regime,
        "positive_oos_coins": coin_positive,
        "positive_held_out_segments": segment_positive,
    }
    return events, summary


def _report(summary: dict) -> str:
    verdict = "PASS" if summary["passes"] else "REJECT"
    conditions = "\n".join(
        f"- {'PASS' if passed else 'FAIL'} — {name}" for name, passed in summary["conditions"].items()
    )
    breadth = ", ".join(
        f"{name} {count}" for name, count in summary["trades_by_instrument"].items()
    )
    holdout = (
        "The TRAIN gate passed; held-out evaluation is authorized next."
        if summary["passes"]
        else "The gate failed, so VAL, TEST and FWD were not opened."
    )
    return f"""# CRYPTO-EXP-016 — BTC reversal leads lagging alts

**Verdict: {verdict} at the TRAIN-only pre-gate.** {holdout}

## Frozen setup

- TRAIN: {summary['train_start']} through {summary['train_end']}
- BTC shock: TRAIN 10th-percentile 4h return = {summary['btc_shock_threshold_pct']:.3f}%
- Trades: {summary['trades']} ({breadth})
- Gross expectancy: {summary['gross_expectancy_bps']:.2f} bps/trade
- Measured expected round-trip cost: {summary['round_trip_cost_bps']:.2f} bps/trade
- Positive-instrument breadth: {summary['positive_instruments']}/8
- Circular-shift placebo: p={summary['placebo_p']:.3f}, 999 deterministic shifts

## Gate

{conditions}

## Interpretation

This tests one preregistered delayed-information rule. Gross expectancy is evaluated
before costs for statistical existence, while the separate economic-size condition
requires it to cover measured expected friction. No reverse direction or alternative
threshold was selected after seeing the result.
"""


def _held_out_report(train: dict, held: dict) -> str:
    segment_rows = []
    for name, metric in held["segments"].items():
        profit_factor = metric["profit_factor"]
        segment_rows.append(
            f"| {name} | {metric['trades']} | {metric['return_pct']:+.2f}% | "
            f"{metric['annualized_pct']:+.2f}% | {metric['sharpe']:.2f} | "
            f"{profit_factor:.2f} | {metric['net_expectancy_bps']:.2f} |"
        )
    gates = "\n".join(
        f"- {'PASS' if passed else 'FAIL'} — {name}" for name, passed in held["conditions"].items()
    )
    costs = "\n".join(
        f"- {mult}x: return {metric['return_pct']:+.2f}%, Sharpe {metric['sharpe']:.2f}, "
        f"expectancy {metric['net_expectancy_bps']:.2f} bps"
        for mult, metric in held["cost_stress_oos"].items()
    )
    delays = "\n".join(
        f"- +{bars} bar: return {metric['return_pct']:+.2f}%, Sharpe {metric['sharpe']:.2f}"
        for bars, metric in held["entry_delay_oos"].items()
    )
    recent = "\n".join(
        f"- {days}d: {metric['trades']} trades, return {metric['return_pct']:+.2f}%, "
        f"expectancy {metric['net_expectancy_bps'] if metric['net_expectancy_bps'] is not None else 0:.2f} bps"
        for days, metric in held["recent_windows"].items()
    )
    regimes = "\n".join(
        f"- {name}: {metric['trades']} trades, expectancy {metric['net_expectancy_bps']:.2f} bps, "
        f"win rate {metric['win_rate_pct']:.1f}%"
        for name, metric in held["btc_trend_regime_oos"].items()
    )
    return f"""# CRYPTO-EXP-016 — BTC reversal leads lagging alts

**Final status: {held['status']}.** The TRAIN pre-gate passed and the held-out data
was opened once under the frozen advancement rule.

## TRAIN pre-gate

- Trades: {train['trades']}; gross expectancy {train['gross_expectancy_bps']:.2f} bps
- Expected round-trip cost: {train['round_trip_cost_bps']:.2f} bps
- Breadth: {train['positive_instruments']}/8; circular-shift p={train['placebo_p']:.3f}

## Expected-cost chronological results

| Segment | Trades | Return | Annualized | Sharpe | PF | Net expectancy bps |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(segment_rows)}

## Frozen advancement gates

{gates}

## Stress diagnostics

Cost scenarios (0x is gross; 1x measured expected):

{costs}

Entry delay at expected costs:

{delays}

Top 5% of OOS trades removed: return
{held['top_five_pct_removed_oos']['return_pct']:+.2f}%, Sharpe
{held['top_five_pct_removed_oos']['sharpe']:.2f}. Positive OOS coin breadth:
{held['positive_oos_coins']}/8. Positive VAL/TEST/FWD segments:
{held['positive_held_out_segments']}/3.

Recent expected-cost windows:

{recent}

BTC trend regimes (using only the prior completed daily close/SMA200):

{regimes}

The machine-readable summary additionally records monthly returns, drawdown, Sortino,
Calmar, winner/loser distributions, fees/slippage, turnover, exposure, streaks,
recovery time and worst day/week/month for every chronological segment.

## Conclusion

The verdict follows the preregistered gates, not headline return. This mechanism is
tracked separately from B2 and no reverse direction, parameter variant, or alternate
holding period was selected after seeing held-out results.
"""


def main() -> int:
    trades, summary = run_train()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    trades.to_csv(OUTPUT / "train_trades.csv", index=False)
    if summary["passes"]:
        full_events, held = run_held_out(summary["btc_shock_threshold_pct"])
        full_events.to_csv(OUTPUT / "all_events.csv", index=False)
        summary["held_out"] = held
        summary["status"] = held["status"]
        report = _held_out_report(summary, held)
    else:
        report = _report(summary)
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
