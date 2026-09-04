"""Behavior tests for B2 forward-paper decay classification."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parent))

from b2_forward_monitor import classify_forward_status, window_metrics


def _quarter_trades(as_of: pd.Timestamp, values: list[float]) -> pd.DataFrame:
    first = pd.date_range(as_of - pd.Timedelta(days=175), periods=len(values), freq="5D", tz="UTC")
    second = pd.date_range(as_of - pd.Timedelta(days=85), periods=len(values), freq="5D", tz="UTC")
    return pd.DataFrame(
        {
            "close_date": first.append(second),
            "close_profit": values + values,
        }
    )


def test_window_metrics_reports_after_cost_trade_statistics() -> None:
    """Catches using gross values or omitting losing trades from profit factor."""
    as_of = pd.Timestamp("2026-09-05", tz="UTC")
    trades = pd.DataFrame(
        {
            "close_date": [as_of - pd.Timedelta(days=3), as_of - pd.Timedelta(days=2)],
            "close_profit": [0.02, -0.01],
        }
    )

    got = window_metrics(trades, as_of, days=30)

    assert got["trades"] == 2
    assert np.isclose(got["net_return_pct"], 0.98)
    assert np.isclose(got["expectancy_bps"], 50.0)
    assert np.isclose(got["win_rate_pct"], 50.0)
    assert np.isclose(got["profit_factor"], 2.0)


def test_status_requires_two_populated_profitable_quarters() -> None:
    """Catches promotion from one quarter or statistically empty windows."""
    as_of = pd.Timestamp("2026-09-05", tz="UTC")
    profitable = _quarter_trades(as_of, [0.02, -0.01] * 8)

    ready = classify_forward_status(profitable, as_of, min_trades_per_quarter=15)
    sparse = classify_forward_status(profitable.iloc[::4], as_of, min_trades_per_quarter=15)

    assert ready["status"] == "READY_FOR_REVIEW"
    assert sparse["status"] == "COLLECTING"


def test_status_marks_two_losing_quarters_degraded() -> None:
    """Catches retaining Candidate confidence after persistent forward PF below one."""
    as_of = pd.Timestamp("2026-09-05", tz="UTC")
    losing = _quarter_trades(as_of, [0.01, -0.02] * 8)

    got = classify_forward_status(losing, as_of, min_trades_per_quarter=15)

    assert got["status"] == "DEGRADED"
    assert got["older_90d"]["profit_factor"] < 1.0
    assert got["recent_90d"]["profit_factor"] < 1.0
