"""Behavior tests for CRYPTO-EXP-016's anti-lookahead event engine."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp_016_btc_alt_lag import (
    circular_shift_placebo,
    complementary_boolean_masks,
    detect_events,
    pre_gate_summary,
    resample_ohlcv_4h,
    train_shock_threshold,
)


def _bars(closes: list[float], opens: list[float] | None = None) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=len(closes), freq="4h", tz="UTC")
    return pd.DataFrame({"open": opens or closes, "close": closes}, index=index)


def test_threshold_is_derived_only_from_bars_through_train_end() -> None:
    btc = _bars([100, 90, 99, 98, 9800])
    train_end = btc.index[3]

    got = train_shock_threshold(btc, train_end, quantile=0.10)
    expected = btc.loc[:train_end, "close"].pct_change().dropna().quantile(0.10)

    assert np.isclose(got, expected)


def test_signal_enters_next_open_and_exits_one_full_bar_later() -> None:
    # At t=2 BTC rebounds after a -10% shock while the alt is still down.
    btc = _bars([100, 90, 91, 92, 93], [100, 90, 91, 92, 93])
    alt = _bars([100, 99, 98, 97, 96], [100, 99, 98, 100, 102])

    events = detect_events(btc, alt, shock_threshold=-0.09, instrument="ALT")

    assert len(events) == 1
    event = events.iloc[0]
    assert event.signal_time == btc.index[2]
    assert event.entry_time == btc.index[3]
    assert event.exit_time == btc.index[4]
    assert np.isclose(event.gross, 0.02)


def test_same_bar_alt_rebound_is_not_a_lagging_signal() -> None:
    btc = _bars([100, 90, 91, 92])
    alt = _bars([100, 95, 96, 97])

    events = detect_events(btc, alt, shock_threshold=-0.09, instrument="ALT")

    assert events.empty


def test_entry_delay_moves_both_entry_and_exit_without_changing_signal() -> None:
    btc = _bars([100, 90, 91, 92, 93, 94])
    alt = _bars([100, 99, 98, 97, 96, 95], [100, 99, 98, 100, 90, 99])

    events = detect_events(
        btc, alt, shock_threshold=-0.09, instrument="ALT", entry_delay_bars=1
    )

    event = events.iloc[0]
    assert event.signal_time == btc.index[2]
    assert event.entry_time == btc.index[4]
    assert event.exit_time == btc.index[5]
    assert np.isclose(event.gross, 0.10)


def test_pre_gate_requires_sample_breadth_significance_and_economic_size() -> None:
    instruments = [f"A{i}" for i in range(8)]
    rows = [
        {"instrument": instrument, "gross": 0.002 if i < 6 else -0.001}
        for i, instrument in enumerate(instruments)
        for _ in range(12)
    ]
    events = pd.DataFrame(rows)

    got = pre_gate_summary(events, placebo_p=0.02, round_trip_cost_bps=5.0)

    assert got["trades"] == 96
    assert got["positive_instruments"] == 6
    assert got["passes"] is False  # pooled sample is below the frozen 100-trade floor


def test_circular_shift_placebo_is_deterministic_and_two_sided() -> None:
    rng = np.random.default_rng(7)
    n = 300
    trigger = np.zeros(n, dtype=bool)
    trigger[20::20] = True
    lag_condition = np.ones(n, dtype=bool)
    forward = rng.normal(0.0, 0.001, n)
    forward[trigger] = 0.01

    first = circular_shift_placebo(trigger, {"ALT": (lag_condition, forward)}, 199, seed=13)
    second = circular_shift_placebo(trigger, {"ALT": (lag_condition, forward)}, 199, seed=13)

    assert first == second
    assert 0.0 < first < 0.05


def test_resample_uses_utc_aligned_complete_four_hour_bars() -> None:
    index = pd.date_range("2024-01-01", periods=8, freq="1h", tz="UTC")
    hourly = pd.DataFrame(
        {
            "open": np.arange(8.0),
            "high": np.arange(8.0) + 2,
            "low": np.arange(8.0) - 2,
            "close": np.arange(8.0) + 1,
            "volume": np.ones(8),
        },
        index=index,
    )

    got = resample_ohlcv_4h(hourly)

    assert list(got.index) == [index[0], index[4]]
    assert got.iloc[0].to_dict() == {
        "open": 0.0,
        "high": 5.0,
        "low": -2.0,
        "close": 4.0,
        "volume": 4.0,
    }


def test_regime_masks_are_boolean_and_complementary() -> None:
    above, below = complementary_boolean_masks(pd.Series([True, None, False], dtype=object))

    assert above.dtype == np.dtype("bool")
    assert below.dtype == np.dtype("bool")
    assert above.tolist() == [True, False, False]
    assert below.tolist() == [False, True, True]
