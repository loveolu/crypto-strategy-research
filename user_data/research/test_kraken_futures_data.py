"""Behavior tests for paginated Kraken Futures candle acquisition."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parent))

from kraken_futures_data import merge_candle_pages, parse_candles, validate_candles


def test_parse_candles_normalizes_numeric_values_and_timestamp() -> None:
    got = parse_candles(
        [{"time": 1672531200000, "open": "10", "high": "12", "low": "9", "close": "11", "volume": "3"}]
    )

    assert got.index.tolist() == [pd.Timestamp("2023-01-01", tz="UTC")]
    assert got.iloc[0].to_dict() == {"open": 10.0, "high": 12.0, "low": 9.0, "close": 11.0, "volume": 3.0}


def test_merge_pages_deduplicates_boundary_and_sorts() -> None:
    first = parse_candles([
        {"time": 2000, "open": "2", "high": "3", "low": "1", "close": "2", "volume": "1"}
    ])
    second = parse_candles([
        {"time": 1000, "open": "1", "high": "2", "low": "0", "close": "1", "volume": "1"},
        {"time": 2000, "open": "2", "high": "3", "low": "1", "close": "2", "volume": "1"},
    ])

    got = merge_candle_pages([first, second])

    assert got.index.is_monotonic_increasing
    assert got.index.is_unique
    assert len(got) == 2


def test_validation_rejects_missing_candle_spacing() -> None:
    frame = pd.DataFrame(
        {"open": [1, 1], "high": [1, 1], "low": [1, 1], "close": [1, 1], "volume": [1, 1]},
        index=pd.DatetimeIndex(["2024-01-01T00:00Z", "2024-01-01T08:00Z"]),
    )

    with pytest.raises(ValueError, match="spacing"):
        validate_candles(frame, expected_frequency="4h")
