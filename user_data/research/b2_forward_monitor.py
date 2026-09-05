"""Forward-paper monitoring for the frozen B2 cascade strategy."""

from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import psutil


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "tradesv3.b2_4h.dryrun.sqlite"
DEFAULT_LOG = ROOT / "user_data" / "logs" / "b2_4h_dryrun.log"
DEFAULT_STRATEGY = ROOT / "user_data" / "strategies" / "B2Cascade4h.py"
DEFAULT_EVENTS = ROOT / "user_data" / "logs" / "b2_4h_forward_events.jsonl"
DEFAULT_RUNTIME_CONFIGS = [ROOT / "user_data" / "config_b2_4h.json", ROOT / "user_data" / "config_perp.json"]
DEFAULT_OUT = Path(__file__).resolve().parent / "forward"
FORWARD_STARTED_AT = "2026-09-04T20:55:57+00:00"
HEARTBEAT_PATTERN = re.compile(
    r"^(?P<stamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+.*"
    r"Bot heartbeat\. PID=(?P<pid>\d+).*state='(?P<state>[^']+)'"
)


def _utc(value: pd.Timestamp | datetime | str) -> pd.Timestamp:
    stamp = pd.Timestamp(value)
    return stamp.tz_localize("UTC") if stamp.tzinfo is None else stamp.tz_convert("UTC")


def _slice(trades: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    closed = trades.copy()
    closed["close_date"] = pd.to_datetime(closed["close_date"], utc=True)
    return closed.loc[(closed["close_date"] >= start) & (closed["close_date"] < end)]


def runtime_health(
    log_path: Path,
    as_of: pd.Timestamp,
    *,
    pid_exists: Callable[[int], bool] = psutil.pid_exists,
    maximum_age_seconds: float = 180.0,
    strategy_path: Path | None = None,
    configuration_paths: list[Path] | None = None,
    process_create_time: Callable[[int], float] | None = None,
) -> dict:
    """Verify a current heartbeat and its reported OS process independently."""
    if not log_path.exists():
        return {"status": "LOG_MISSING", "log": str(log_path), "healthy": False}
    latest = None
    for line in reversed(log_path.read_text(encoding="utf-8", errors="replace").splitlines()):
        match = HEARTBEAT_PATTERN.search(line)
        if match:
            latest = match
            break
    if latest is None:
        return {"status": "HEARTBEAT_MISSING", "log": str(log_path), "healthy": False}
    local_stamp = pd.Timestamp(datetime.strptime(latest.group("stamp"), "%Y-%m-%d %H:%M:%S"))
    heartbeat = local_stamp.tz_localize(ZoneInfo("America/Los_Angeles")).tz_convert("UTC")
    age = float((_utc(as_of) - heartbeat).total_seconds())
    pid = int(latest.group("pid"))
    state = latest.group("state")
    alive = bool(pid_exists(pid))
    strategy_loaded = None
    process_started = None
    strategy_modified = None
    stale_runtime_files: list[str] = []
    if alive and strategy_path is not None and strategy_path.exists():
        get_create_time = process_create_time or (lambda value: psutil.Process(value).create_time())
        process_epoch = float(get_create_time(pid))
        strategy_epoch = float(strategy_path.stat().st_mtime)
        process_started = pd.Timestamp(process_epoch, unit="s", tz="UTC")
        strategy_modified = pd.Timestamp(strategy_epoch, unit="s", tz="UTC")
        strategy_loaded = process_epoch >= strategy_epoch
        runtime_files = [strategy_path, *(configuration_paths or [])]
        stale_runtime_files = [
            str(path) for path in runtime_files
            if path.exists() and process_epoch < float(path.stat().st_mtime)
        ]
        strategy_loaded = not stale_runtime_files
    status = "HEALTHY"
    if not alive:
        status = "PROCESS_MISSING"
    elif age < -5.0:
        status = "HEARTBEAT_FROM_FUTURE"
    elif age > maximum_age_seconds:
        status = "STALE_HEARTBEAT"
    elif state != "RUNNING":
        status = "BOT_NOT_RUNNING"
    elif strategy_loaded is False:
        status = "STALE_STRATEGY_CODE"
    return {
        "status": status,
        "healthy": status == "HEALTHY",
        "log": str(log_path),
        "pid": pid,
        "process_exists": alive,
        "bot_state": state,
        "last_heartbeat_utc": heartbeat.isoformat(),
        "heartbeat_age_seconds": age,
        "maximum_age_seconds": maximum_age_seconds,
        "strategy": str(strategy_path) if strategy_path is not None else None,
        "strategy_loaded": strategy_loaded,
        "process_started_utc": process_started.isoformat() if process_started is not None else None,
        "strategy_modified_utc": strategy_modified.isoformat() if strategy_modified is not None else None,
        "stale_runtime_files": stale_runtime_files,
    }


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


def load_events(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return pd.DataFrame(rows)


def execution_quality(trades: pd.DataFrame, events: pd.DataFrame) -> dict:
    """Reconcile decision quotes with dry-run fills and realized costs."""
    result = {
        "entry_decisions": 0, "matched_entries": 0,
        "entry_fill_latency_seconds_median": None, "entry_slippage_bps_median": None,
        "exit_decisions": 0, "matched_exits": 0,
        "exit_fill_latency_seconds_median": None, "exit_slippage_bps_median": None,
        "realized_cost_bps_median": None,
    }
    if events.empty:
        return result
    entries = events.loc[events.get("kind", pd.Series(index=events.index, dtype=str)).eq("entry_decision")]
    exits = events.loc[events.get("kind", pd.Series(index=events.index, dtype=str)).eq("exit_decision")]
    result["entry_decisions"] = int(len(entries))
    result["exit_decisions"] = int(len(exits))
    if trades.empty:
        return result

    frame = trades.copy()
    frame["open_date"] = pd.to_datetime(frame["open_date"], utc=True)
    frame["close_date"] = pd.to_datetime(frame.get("close_date"), utc=True)
    entry_latency, entry_slippage = [], []
    for _, event in entries.iterrows():
        decision = _utc(event["decision_time"])
        candidates = frame.loc[frame["pair"].eq(event["pair"])].copy()
        if candidates.empty:
            continue
        candidates["distance"] = (candidates["open_date"] - decision).abs()
        match = candidates.sort_values("distance").iloc[0]
        if match["distance"] > pd.Timedelta(minutes=10):
            continue
        entry_latency.append((match["open_date"] - decision).total_seconds())
        entry_slippage.append((float(match["open_rate"]) / float(event["proposed_rate"]) - 1.0) * 10_000.0)
    result["matched_entries"] = len(entry_latency)
    if entry_latency:
        result["entry_fill_latency_seconds_median"] = float(np.median(entry_latency))
        result["entry_slippage_bps_median"] = float(np.median(entry_slippage))

    exit_latency, exit_slippage = [], []
    for _, event in exits.iterrows():
        candidates = frame.loc[frame["id"].eq(int(event["trade_id"]))]
        if candidates.empty or pd.isna(candidates.iloc[0]["close_date"]):
            continue
        match = candidates.iloc[0]
        decision = _utc(event["decision_time"])
        exit_latency.append((match["close_date"] - decision).total_seconds())
        # Long exits are sells: execution below the proposed quote is adverse.
        exit_slippage.append((float(event["proposed_rate"]) / float(match["close_rate"]) - 1.0) * 10_000.0)
    result["matched_exits"] = len(exit_latency)
    if exit_latency:
        result["exit_fill_latency_seconds_median"] = float(np.median(exit_latency))
        result["exit_slippage_bps_median"] = float(np.median(exit_slippage))

    closed = frame.loc[frame["close_date"].notna() & frame["stake_amount"].gt(0)].copy()
    if not closed.empty:
        paid = closed["fee_open_cost"].fillna(0) + closed["fee_close_cost"].fillna(0)
        paid = paid - closed["funding_fees"].fillna(0)
        result["realized_cost_bps_median"] = float(np.median(paid / closed["stake_amount"] * 10_000.0))
    return result


def _forward_significance(trades: pd.DataFrame, as_of: pd.Timestamp) -> dict:
    """Probabilistic Sharpe Ratio versus zero on genuinely forward trades."""
    end = _utc(as_of) + pd.Timedelta(microseconds=1)
    returns = pd.to_numeric(
        _slice(trades, _utc(FORWARD_STARTED_AT), end).get(
            "close_profit", pd.Series(dtype=float)
        ),
        errors="coerce",
    ).dropna().to_numpy(dtype=float)
    n = len(returns)
    result = {"trades": int(n), "minimum_trades": 100, "psr_positive": None}
    if n < 2:
        return result
    mean = float(returns.mean())
    std = float(returns.std(ddof=0))
    if std <= 1e-12:
        result["psr_positive"] = 1.0 if mean > 0 else 0.0
        return result
    centered = returns - mean
    skew = float(np.mean(centered**3) / std**3)
    kurtosis = float(np.mean(centered**4) / std**4)
    sharpe = mean / std
    denominator = 1.0 - skew * sharpe + ((kurtosis - 1.0) / 4.0) * sharpe**2
    psr = 0.0 if denominator <= 0 else 0.5 * (
        1.0 + math.erf(sharpe * math.sqrt(n - 1) / math.sqrt(2.0 * denominator))
    )
    result.update(
        {
            "psr_positive": float(psr),
            "sharpe_per_trade": float(sharpe),
            "skew": skew,
            "kurtosis": kurtosis,
        }
    )
    return result


def classify_forward_status(
    trades: pd.DataFrame, as_of: pd.Timestamp, min_trades_per_quarter: int = 15
) -> dict:
    """Apply the pre-registered two-consecutive-quarter profit-factor gate."""
    end = _utc(as_of) + pd.Timedelta(microseconds=1)
    boundary = end - pd.Timedelta(days=90)
    older = _metrics(_slice(trades, end - pd.Timedelta(days=180), boundary))
    recent = _metrics(_slice(trades, boundary, end))
    significance = _forward_significance(trades, as_of)
    result = {
        "status": "COLLECTING",
        "older_90d": older,
        "recent_90d": recent,
        "forward_significance": significance,
    }
    if min(older["trades"], recent["trades"]) < min_trades_per_quarter:
        return result
    factors = (older["profit_factor"], recent["profit_factor"])
    if all(value is not None and value > 1.0 for value in factors):
        if significance["trades"] < significance["minimum_trades"]:
            result["status"] = "PF_GATE_PASSED_AWAITING_SIGNIFICANCE"
        elif (significance["psr_positive"] or 0.0) >= 0.95:
            result["status"] = "READY_FOR_REVIEW"
        else:
            result["status"] = "PF_GATE_PASSED_SIGNIFICANCE_FAILED"
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
        selected = [
            name for name in (
                "id", "pair", "open_date", "open_rate", "close_date", "close_rate",
                "close_profit", "stake_amount", "fee_open_cost", "fee_close_cost", "funding_fees",
            ) if name in columns
        ]
        # Keep open positions so entry decisions can be reconciled immediately.
        # Return windows still exclude them naturally because close_date/profit are null.
        closed = pd.read_sql_query(f"SELECT {', '.join(selected)} FROM trades", connection)
        open_count = int(connection.execute("SELECT COUNT(*) FROM trades WHERE is_open = 1").fetchone()[0])
    return closed, open_count


def build_report(
    db_path: Path,
    as_of: pd.Timestamp,
    log_path: Path = DEFAULT_LOG,
    event_path: Path = DEFAULT_EVENTS,
) -> dict:
    trades, open_count = load_trades(db_path)
    classification = classify_forward_status(trades, as_of)
    runtime = runtime_health(
        log_path,
        as_of,
        strategy_path=DEFAULT_STRATEGY,
        configuration_paths=DEFAULT_RUNTIME_CONFIGS,
    )
    return {
        "strategy": "B2Cascade4h",
        "mode": "dry_run",
        "as_of": _utc(as_of).isoformat(),
        "forward_started_at": FORWARD_STARTED_AT,
        "database": str(db_path),
        "database_exists": db_path.exists(),
        "status": classification["status"] if runtime["healthy"] else "RUNTIME_DOWN",
        "evidence_status": classification["status"],
        "runtime": runtime,
        "gate": (
            "PF > 1.0 in each of two consecutive 90-day windows with at least "
            "15 trades/window, plus >=100 total forward trades and PSR(Sharpe>0) >= 0.95"
        ),
        "backtest_baseline": {"expectancy_bps_per_trade": 149.0, "win_rate_pct": 63.0},
        "open_trades": open_count,
        "windows": {str(days): window_metrics(trades, as_of, days) for days in (30, 90, 180, 365)},
        "quarter_gate": classification,
        "execution_quality": execution_quality(trades, load_events(event_path)),
    }


def write_report(report: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "b2_4h_status.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    rows = [
        "# B2 4h forward-paper status",
        "",
        f"- Status: **{report['status']}**",
        f"- Runtime: **{report['runtime']['status']}**",
        f"- Runtime PID: {report['runtime'].get('pid', 'n/a')}",
        f"- Last heartbeat UTC: {report['runtime'].get('last_heartbeat_utc', 'n/a')}",
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
    quality = report["execution_quality"]
    rows.extend(
        [
            "",
            "## Execution quality",
            "",
            f"- Entry decisions / matched fills: {quality['entry_decisions']} / {quality['matched_entries']}",
            f"- Median entry decision-to-fill latency: {display(quality['entry_fill_latency_seconds_median'], ' s')}",
            f"- Median adverse entry slippage: {display(quality['entry_slippage_bps_median'], ' bps')}",
            f"- Exit decisions / matched fills: {quality['exit_decisions']} / {quality['matched_exits']}",
            f"- Median exit decision-to-fill latency: {display(quality['exit_fill_latency_seconds_median'], ' s')}",
            f"- Median adverse exit slippage: {display(quality['exit_slippage_bps_median'], ' bps')}",
            f"- Median realized fees plus funding: {display(quality['realized_cost_bps_median'], ' bps')}",
        ]
    )
    (output_dir / "b2_4h_status.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--as-of", default=datetime.now(timezone.utc).isoformat())
    args = parser.parse_args()
    report = build_report(
        args.db.resolve(), _utc(args.as_of), args.log.resolve(), args.events.resolve()
    )
    write_report(report, args.output_dir.resolve())
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
