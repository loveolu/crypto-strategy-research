"""Behavior tests for the EXP-CX-001 dispersion-conditioned reversal engine."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


RESEARCH_DIR = Path(__file__).resolve().parents[2] / "user_data" / "research"
sys.path.insert(0, str(RESEARCH_DIR))

from exp_cx_001_dispersion_reversal import (
    build_entry_weights,
    build_trade_table,
    dispersion_event_mask,
    event_onsets,
    trade_returns,
)


def test_build_entry_weights_reverses_two_extreme_momentum_names() -> None:
    """Catches sorting the legs in the momentum, rather than reversal, direction."""
    momentum = pd.Series({"BTC": -0.08, "ETH": -0.03, "SOL": 0.01, "XRP": 0.05, "ADA": 0.09})

    weights = build_entry_weights(momentum, names_per_leg=2)

    assert weights.to_dict() == {
        "BTC": 0.25,
        "ETH": 0.25,
        "SOL": 0.0,
        "XRP": -0.25,
        "ADA": -0.25,
    }
    assert np.isclose(weights.abs().sum(), 1.0)
    assert np.isclose(weights.sum(), 0.0)


def test_event_onsets_requires_crossing_and_enforces_cooldown() -> None:
    """Catches repeated entries on every bar of one high-dispersion episode."""
    high = pd.Series(
        [False, True, True, False, True, False, True, False],
        index=pd.date_range("2026-01-01", periods=8, freq="h", tz="UTC"),
    )

    got = event_onsets(high, cooldown_bars=4)

    assert got.tolist() == [False, True, False, False, False, False, True, False]


def test_trade_returns_uses_delayed_entry_and_charges_all_four_legs() -> None:
    """Catches same-bar execution and undercharging a four-leg round trip."""
    idx = pd.date_range("2026-01-01", periods=6, freq="h", tz="UTC")
    opens = pd.DataFrame(
        {
            "A": [100, 100, 100, 110, 110, 110],
            "B": [100, 100, 100, 110, 110, 110],
            "C": [100, 100, 100, 90, 90, 90],
            "D": [100, 100, 100, 90, 90, 90],
        },
        index=idx,
    )
    weights = pd.Series({"A": 0.25, "B": 0.25, "C": -0.25, "D": -0.25})
    per_side_bps = pd.Series({"A": 5.0, "B": 5.0, "C": 5.0, "D": 5.0})

    gross, net, entry_time, exit_time = trade_returns(
        opens,
        signal_position=0,
        weights=weights,
        hold_bars=1,
        delay_bars=2,
        per_side_bps=per_side_bps,
    )

    # Signal at t0 enters at t2 open and exits at t3 open: +10% long and +10% short.
    assert entry_time == idx[2]
    assert exit_time == idx[3]
    assert np.isclose(gross, 0.10)
    # Gross-one exposure pays 5 bps on entry and again on exit.
    assert np.isclose(net, 0.10 - 0.001)


def test_dispersion_event_mask_uses_only_prior_bars_for_threshold() -> None:
    """Catches leakage from including the current cross-section in its own threshold."""
    idx = pd.date_range("2026-01-01", periods=8, freq="h", tz="UTC")
    momentum = pd.DataFrame(
        {
            "A": [0, 0, 0, 0, -4, 0, 0, 0],
            "B": [0, 1, 2, 0, 4, 0, 0, 0],
            "C": [0, -1, -2, 0, 0, 0, 0, 0],
            "D": [0, 0, 0, 0, 0, 0, 0, 0],
        },
        index=idx,
    )

    events, threshold = dispersion_event_mask(momentum, lookback=3, quantile=0.5, cooldown_bars=2)

    # At t4, the prior dispersions come from t1:t3; t3 is deliberately low so t4
    # is a fresh crossing rather than a continuation of the prior episode.
    assert np.isclose(threshold.iloc[4], momentum.iloc[1:4].std(axis=1, ddof=0).median())
    assert bool(events.iloc[4])


def test_build_trade_table_records_only_executable_events() -> None:
    """Catches silently truncating a trade whose exit lies beyond the data."""
    idx = pd.date_range("2026-01-01", periods=7, freq="h", tz="UTC")
    opens = pd.DataFrame(
        {
            "A": [100, 100, 100, 110, 110, 110, 110],
            "B": [100, 100, 100, 110, 110, 110, 110],
            "C": [100, 100, 100, 90, 90, 90, 90],
            "D": [100, 100, 100, 90, 90, 90, 90],
        },
        index=idx,
    )
    momentum = pd.DataFrame(
        [[-4, -3, 3, 4]] * len(idx), columns=opens.columns, index=idx, dtype=float
    )
    events = pd.Series(False, index=idx)
    events.iloc[[0, 4]] = True

    trades = build_trade_table(
        opens,
        momentum,
        events,
        pd.Series(5.0, index=opens.columns),
        hold_bars=1,
        delay_bars=2,
    )

    assert len(trades) == 1
    assert trades.iloc[0]["signal_time"] == idx[0]
    assert np.isclose(trades.iloc[0]["net_return"], 0.099)
