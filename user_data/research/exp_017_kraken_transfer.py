"""CRYPTO-EXP-017: frozen B2 transfer to Kraken Futures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def align_completed_daily_gate(
    daily_gate: pd.Series, four_hour_index: pd.DatetimeIndex
) -> pd.Series:
    """Expose a daily value only after its six constituent 4h bars completed."""
    return (
        daily_gate.astype(float)
        .reindex(four_hour_index, method="ffill")
        .shift(6)
        .fillna(0.0)
        .astype(bool)
    )


def simulate_trades(
    frame: pd.DataFrame,
    instrument: str,
    entry_delay_bars: int = 0,
    max_hold_bars: int = 6,
) -> pd.DataFrame:
    """Execute the exact B2 entry/exit timing on precomputed causal features."""
    rows = []
    t = 0
    n = len(frame)
    while t < n - entry_delay_bars - 2:
        row = frame.iloc[t]
        trigger = (
            row["pct"] >= 0.80
            and row["mom"] <= -0.0385
            and row["btc_mom"] < 0.0
            and bool(row["gate"])
        )
        if not trigger:
            t += 1
            continue
        entry_position = t + 1 + entry_delay_bars
        exit_signal_position = entry_position
        last_signal_position = min(entry_position + max_hold_bars, n - 2)
        while (
            exit_signal_position < last_signal_position
            and frame.iloc[exit_signal_position]["pct"] >= 0.50
        ):
            exit_signal_position += 1
        if (
            entry_position + max_hold_bars > n - 2
            and exit_signal_position == n - 2
            and frame.iloc[exit_signal_position]["pct"] >= 0.50
        ):
            break
        exit_position = exit_signal_position + 1
        entry_price = float(frame.iloc[entry_position]["open"])
        exit_price = float(frame.iloc[exit_position]["open"])
        rows.append(
            {
                "instrument": instrument,
                "signal_time": frame.index[t],
                "entry_time": frame.index[entry_position],
                "exit_time": frame.index[exit_position],
                "gross": exit_price / entry_price - 1.0,
                "bars_held": exit_position - entry_position,
                "entry_pct": float(row["pct"]),
                "entry_mom": float(row["mom"]),
            }
        )
        t = exit_position + 1
    return pd.DataFrame(rows)


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "user_data" / "research" / "data" / "kraken_futures"
OUTPUT_DIR = ROOT / "research" / "measurements" / "EXP017"
INSTRUMENTS = ["ETH", "SOL", "XRP", "ADA", "AVAX", "DOT", "LINK"]
START = pd.Timestamp("2023-01-22", tz="UTC")
END = pd.Timestamp("2026-09-01", tz="UTC")
EXPECTED_ROUND_TRIP = 0.0018


def _load(instrument: str, timeframe: str) -> pd.DataFrame:
    matches = list(DATA_DIR.glob(f"{instrument}-*-{timeframe}.feather"))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one {instrument}/{timeframe} file, found {len(matches)}")
    return pd.read_feather(matches[0]).set_index("date").sort_index().loc[START:END]


def _features(instrument: str, btc_momentum: pd.Series) -> pd.DataFrame:
    bars = _load(instrument, "4h")
    returns = bars["close"].pct_change()
    downside = np.sqrt(np.minimum(returns, 0.0).pow(2).rolling(42).mean())
    daily = _load(instrument, "1d")["close"]
    daily_gate = (
        (daily > daily.rolling(200).mean())
        & (daily.ewm(span=20).mean() > daily.ewm(span=50).mean())
    )
    return pd.DataFrame(
        {
            "open": bars["open"],
            "pct": downside.rolling(180).rank(pct=True),
            "mom": bars["close"].pct_change(6),
            "btc_mom": btc_momentum.reindex(bars.index),
            "gate": align_completed_daily_gate(daily_gate, bars.index),
        }
    )


def _all_trades(delay: int = 0) -> pd.DataFrame:
    btc = _load("BTC", "4h")
    btc_momentum = btc["close"].pct_change(6)
    batches = [
        simulate_trades(_features(instrument, btc_momentum), instrument, entry_delay_bars=delay)
        for instrument in INSTRUMENTS
    ]
    return pd.concat(batches, ignore_index=True).sort_values(["entry_time", "instrument"])


def _return_stream(trades: pd.DataFrame, cost_multiple: float = 1.0) -> pd.Series:
    index = _load("BTC", "4h").index
    stream = pd.Series(0.0, index=index)
    net = trades["gross"] - EXPECTED_ROUND_TRIP * cost_multiple
    for exit_time, value in net.groupby(trades["exit_time"]).sum().items():
        if exit_time in stream.index:
            stream.loc[exit_time] += float(value) / len(INSTRUMENTS)
    return stream


def _metrics(trades: pd.DataFrame, cost_multiple: float = 1.0) -> dict:
    stream = _return_stream(trades, cost_multiple)
    equity = (1.0 + stream).cumprod()
    years = (stream.index[-1] - stream.index[0]).total_seconds() / (365.25 * 86400)
    total = float(equity.iloc[-1] - 1.0)
    annualized = float(equity.iloc[-1] ** (1.0 / years) - 1.0)
    drawdown = equity / equity.cummax() - 1.0
    net = trades["gross"] - EXPECTED_ROUND_TRIP * cost_multiple
    winners, losers = net[net > 0], net[net < 0]
    daily = (1.0 + stream).resample("1D").prod() - 1.0
    weekly = (1.0 + stream).resample("W").prod() - 1.0
    monthly = (1.0 + stream).resample("ME").prod() - 1.0
    downside = np.sqrt(np.mean(np.minimum(stream.to_numpy(), 0.0) ** 2))
    losing = longest_losing = 0
    for value in net:
        losing = losing + 1 if value < 0 else 0
        longest_losing = max(longest_losing, losing)
    underwater = longest_underwater = 0
    for value in drawdown < 0:
        underwater = underwater + 1 if value else 0
        longest_underwater = max(longest_underwater, underwater)
    annual = {str(year): float(value * 100.0) for year, value in ((1 + stream).groupby(stream.index.year).prod() - 1).items()}
    return {
        "trades": int(len(trades)),
        "return_pct": total * 100.0,
        "annualized_pct": annualized * 100.0,
        "annual_returns_pct": annual,
        "max_drawdown_pct": float(drawdown.min() * 100.0),
        "sharpe": float(stream.mean() / stream.std() * np.sqrt(6 * 365.25)) if stream.std() else 0.0,
        "sortino": float(stream.mean() / downside * np.sqrt(6 * 365.25)) if downside else 0.0,
        "calmar": float(annualized / abs(drawdown.min())) if drawdown.min() < 0 else None,
        "profit_factor": float(winners.sum() / -losers.sum()) if len(losers) else None,
        "win_rate_pct": float((net > 0).mean() * 100.0) if len(net) else None,
        "gross_expectancy_bps": float(trades["gross"].mean() * 10_000.0) if len(trades) else None,
        "net_expectancy_bps": float(net.mean() * 10_000.0) if len(net) else None,
        "average_winner_bps": float(winners.mean() * 10_000.0) if len(winners) else None,
        "average_loser_bps": float(losers.mean() * 10_000.0) if len(losers) else None,
        "median_trade_bps": float(net.median() * 10_000.0) if len(net) else None,
        "trades_per_day": float(len(trades) / ((END - START).total_seconds() / 86400)),
        "average_hold_hours": float(trades["bars_held"].mean() * 4.0) if len(trades) else None,
        "fees_slippage_pct_of_sleeved_equity": float(len(trades) * EXPECTED_ROUND_TRIP * cost_multiple / len(INSTRUMENTS) * 100.0),
        "turnover_x_equity": float(len(trades) * 2 / len(INSTRUMENTS)),
        "long_exposure_pct": float(trades["bars_held"].sum() * 4 / len(INSTRUMENTS) / ((END - START).total_seconds() / 3600) * 100.0),
        "short_exposure_pct": 0.0,
        "profitable_active_days_pct": float((daily[daily != 0] > 0).mean() * 100.0) if (daily != 0).any() else None,
        "max_intraday_drawdown_pct": float(stream.min() * 100.0),
        "longest_losing_streak": int(longest_losing),
        "recovery_time_hours": int(longest_underwater * 4),
        "worst_day_pct": float(daily.min() * 100.0),
        "worst_week_pct": float(weekly.min() * 100.0),
        "worst_month_pct": float(monthly.min() * 100.0),
        "monthly_returns_pct": {str(k.date()): float(v * 100.0) for k, v in monthly.items()},
    }


def run() -> tuple[pd.DataFrame, dict]:
    trades = _all_trades()
    scenarios = {str(mult): _metrics(trades, mult) for mult in (0.0, 1.0, 2.0, 3.0)}
    delays = {str(delay): _metrics(_all_trades(delay), 1.0) for delay in (1, 2)}
    expected_net = trades["gross"] - EXPECTED_ROUND_TRIP
    cutoff = expected_net.quantile(0.95)
    top_removed = _metrics(trades.loc[expected_net < cutoff].copy(), 1.0)
    coin = {}
    for instrument, group in trades.groupby("instrument"):
        coin[instrument] = {
            "trades": int(len(group)),
            "net_expectancy_bps": float((group["gross"].mean() - EXPECTED_ROUND_TRIP) * 10_000.0),
        }
    positive_coins = sum(value["net_expectancy_bps"] > 0 for value in coin.values())
    positive_years = sum(value > 0 for value in scenarios["1.0"]["annual_returns_pct"].values())
    conditions = {
        "expected_return_positive": scenarios["1.0"]["return_pct"] > 0,
        "sharpe_above_0_5": scenarios["1.0"]["sharpe"] > 0.5,
        "profit_factor_above_1": (scenarios["1.0"]["profit_factor"] or 0.0) > 1.0,
        "five_of_seven_coins_positive": positive_coins >= 5,
        "two_calendar_years_positive": positive_years >= 2,
        "two_x_cost_positive": scenarios["2.0"]["return_pct"] > 0,
        "one_bar_delay_positive": delays["1"]["return_pct"] > 0,
        "top_five_pct_removed_positive": top_removed["return_pct"] > 0,
    }
    recent = {}
    stream = _return_stream(trades, 1.0)
    for days in (30, 90, 180, 365):
        window = stream.loc[stream.index >= END - pd.Timedelta(days=days)]
        recent[str(days)] = {
            "return_pct": float(((1 + window).prod() - 1) * 100.0),
            "trades": int((trades["exit_time"] >= END - pd.Timedelta(days=days)).sum()),
        }
    summary = {
        "experiment_id": "CRYPTO-EXP-017",
        "status": "EXCHANGE_TRANSFER_CONFIRMED" if all(conditions.values()) else "EXCHANGE_TRANSFER_FAILED",
        "source": "Kraken Futures public chart API",
        "period": f"{START.isoformat()}..{END.isoformat()}",
        "universe": INSTRUMENTS,
        "expected_round_trip_cost_bps": EXPECTED_ROUND_TRIP * 10_000.0,
        "conditions": conditions,
        "cost_scenarios": scenarios,
        "entry_delay": delays,
        "top_five_pct_removed": top_removed,
        "coin_results": coin,
        "positive_coins": positive_coins,
        "positive_years": positive_years,
        "recent": recent,
        "benchmark_to_beat": {"name": "OKX B2 4h + BTC condition", "three_year_total_pct": 61.7, "max_drawdown_pct": -5.5},
    }
    return trades, summary


def _report(summary: dict) -> str:
    expected = summary["cost_scenarios"]["1.0"]
    rows = "\n".join(
        f"| {mult}x | {metric['return_pct']:+.2f}% | {metric['annualized_pct']:+.2f}% | {metric['sharpe']:.2f} | {metric['max_drawdown_pct']:.2f}% | {metric['net_expectancy_bps']:.2f} |"
        for mult, metric in summary["cost_scenarios"].items()
    )
    gates = "\n".join(f"- {'PASS' if value else 'FAIL'} — {key}" for key, value in summary["conditions"].items())
    coins = "\n".join(f"- {key}: {value['trades']} trades, {value['net_expectancy_bps']:+.2f} bps/trade" for key, value in summary["coin_results"].items())
    annual = ", ".join(f"{year} {value:+.2f}%" for year, value in expected["annual_returns_pct"].items())
    delay = summary["entry_delay"]
    return f"""# CRYPTO-EXP-017 — B2 transfer to Kraken Futures

**Verdict: {summary['status']}.** Exact frozen B2 signal and exits on the
pre-registered common-alt universe; no Kraken refit.

Kraken common universe: {', '.join(summary['universe'])}. Period: {summary['period']}.
Expected cost is 18 bps round trip, retained from the conservative Candidate proxy.

| Cost | Total return | Annualized | Sharpe | Max DD | Net expectancy bps |
|---|---:|---:|---:|---:|---:|
{rows}

Expected-cost calendar returns: {annual}. Trades: {expected['trades']}; PF
{expected['profit_factor']:.2f}; Sortino {expected['sortino']:.2f}; average hold
{expected['average_hold_hours']:.1f} hours.

## Frozen gates

{gates}

## Breadth and stress

{coins}

- One-bar delay: {delay['1']['return_pct']:+.2f}%, Sharpe {delay['1']['sharpe']:.2f}
- Two-bar delay: {delay['2']['return_pct']:+.2f}%, Sharpe {delay['2']['sharpe']:.2f}
- Top 5% removed: {summary['top_five_pct_removed']['return_pct']:+.2f}%, Sharpe {summary['top_five_pct_removed']['sharpe']:.2f}

The machine-readable artifact includes monthly/recent returns, costs, exposure,
turnover, drawdown, streak and recovery diagnostics. This experiment evaluates
exchange transfer; it is not a new challenger to the +61.7% / −5.5% OKX B2
benchmark and does not alter the live-promotion gate.
"""


def main() -> int:
    trades, summary = run()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    trades.to_csv(OUTPUT_DIR / "trades.csv", index=False)
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "report.md").write_text(_report(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
