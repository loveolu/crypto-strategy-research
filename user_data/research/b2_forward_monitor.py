"""Forward-paper monitoring for the frozen B2 cascade strategy."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "tradesv3.b2_4h.dryrun.sqlite"
DEFAULT_OUT = Path(__file__).resolve().parent / "forward"
FORWARD_STARTED_AT = "2026-09-04T20:55:57+00:00"


def _utc(value: pd.Timestamp | datetime | str) -> pd.Timestamp:
    stamp = pd.Timestamp(value)
    return stamp.tz_localize("UTC") if stamp.tzinfo is None else stamp.tz_convert("UTC")


def _slice(trades: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    closed = trades.copy()
    closed["close_date"] = pd.to_datetime(closed["close_date"], utc=True)
    return closed.loc[(closed["close_date"] >= start) & (closed["close_date"] < end)]


def _metrics(frame: pd.DataFrame) -> dict:
    returns = pd.to_numeric(frame.get("close_profit", pd.Series(dtype=float)), errors="coerce").dropna()
    wins = returns[returns > 0].sum()
    losses = -returns[returns < 0].sum()
    profit_factor = float(wins / losses) if losses > 0 else (float("inf") if wins > 0 else None)
    return {
        "trades": int(len(returns)),
        "net_return_pct": float(((1.0 + returns).prod() - 1.0) * 100.0) if len(returns) else 0.0,
        "expectancy_bps": float(returns.mean() * 10_000.0) if len(returns) else None,
        "win_rate_pct": float((returns > 0).mean() * 100.0) if len(returns) else None,
        "profit_factor": profit_factor,
    }


def window_metrics(trades: pd.DataFrame, as_of: pd.Timestamp, days: int) -> dict:
    """Return after-cost closed-trade metrics for the trailing calendar window."""
    end = _utc(as_of) + pd.Timedelta(microseconds=1)
    return _metrics(_slice(trades, end - pd.Timedelta(days=days), end))


def classify_forward_status(
    trades: pd.DataFrame, as_of: pd.Timestamp, min_trades_per_quarter: int = 15
) -> dict:
    """Apply the pre-registered two-consecutive-quarter profit-factor gate."""
    end = _utc(as_of) + pd.Timedelta(microseconds=1)
    boundary = end - pd.Timedelta(days=90)
    older = _metrics(_slice(trades, end - pd.Timedelta(days=180), boundary))
    recent = _metrics(_slice(trades, boundary, end))
    result = {"status": "COLLECTING", "older_90d": older, "recent_90d": recent}
    if min(older["trades"], recent["trades"]) < min_trades_per_quarter:
        return result
    factors = (older["profit_factor"], recent["profit_factor"])
    if all(value is not None and value > 1.0 for value in factors):
        result["status"] = "READY_FOR_REVIEW"
    elif all(value is not None and value < 1.0 for value in factors):
        result["status"] = "DEGRADED"
    else:
        result["status"] = "MIXED"
    return result


def load_trades(db_path: Path) -> tuple[pd.DataFrame, int]:
    if not db_path.exists():
        return pd.DataFrame(columns=["close_date", "close_profit"]), 0
    with sqlite3.connect(db_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(trades)")}
        if not columns:
            return pd.DataFrame(columns=["close_date", "close_profit"]), 0
        closed = pd.read_sql_query(
            "SELECT close_date, close_profit FROM trades WHERE is_open = 0", connection
        )
        open_count = int(connection.execute("SELECT COUNT(*) FROM trades WHERE is_open = 1").fetchone()[0])
    return closed, open_count


def build_report(db_path: Path, as_of: pd.Timestamp) -> dict:
    trades, open_count = load_trades(db_path)
    classification = classify_forward_status(trades, as_of)
    return {
        "strategy": "B2Cascade4h",
        "mode": "dry_run",
        "as_of": _utc(as_of).isoformat(),
        "forward_started_at": FORWARD_STARTED_AT,
        "database": str(db_path),
        "database_exists": db_path.exists(),
        "status": classification["status"],
        "gate": "PF > 1.0 in each of two consecutive 90-day windows, at least 15 trades/window",
        "backtest_baseline": {"expectancy_bps_per_trade": 149.0, "win_rate_pct": 63.0},
        "open_trades": open_count,
        "windows": {str(days): window_metrics(trades, as_of, days) for days in (30, 90, 180, 365)},
        "quarter_gate": classification,
    }


def write_report(report: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "b2_4h_status.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    rows = [
        "# B2 4h forward-paper status",
        "",
        f"- Status: **{report['status']}**",
        f"- As of: {report['as_of']}",
        f"- Open trades: {report['open_trades']}",
        f"- Gate: {report['gate']}",
        "",
        "| Window | Trades | Net return | Expectancy | Win rate | Profit factor |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for window, metric in report["windows"].items():
        def display(value: object, suffix: str = "") -> str:
            if value is None:
                return "n/a"
            if isinstance(value, float) and np.isinf(value):
                return "inf"
            return f"{value:.2f}{suffix}" if isinstance(value, float) else str(value)
        rows.append(
            f"| {window}d | {metric['trades']} | {display(metric['net_return_pct'], '%')} | "
            f"{display(metric['expectancy_bps'], ' bps')} | {display(metric['win_rate_pct'], '%')} | "
            f"{display(metric['profit_factor'])} |"
        )
    (output_dir / "b2_4h_status.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--as-of", default=datetime.now(timezone.utc).isoformat())
    args = parser.parse_args()
    report = build_report(args.db.resolve(), _utc(args.as_of))
    write_report(report, args.output_dir.resolve())
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
