"""Behavior tests for the append-safe OKX market-structure recorder."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parent))

from market_structure_recorder import finalized_daily_rows, merge_rows, parse_rows


def test_parse_rows_applies_metric_schema_and_provenance() -> None:
    got = parse_rows(
        "open_interest_volume",
        "BTC",
        [["1704067200000", "123.5", "456.7"]],
        "2026-09-04T20:00:00Z",
        "https://example.test/source",
    )

    assert got.to_dict("records") == [
        {
            "timestamp_ms": 1704067200000,
            "timestamp_utc": "2024-01-01T00:00:00+00:00",
            "currency": "BTC",
            "open_interest_usd": 123.5,
            "volume_usd": 456.7,
            "fetched_at_utc": "2026-09-04T20:00:00Z",
            "source_url": "https://example.test/source",
        }
    ]


def test_merge_is_sorted_idempotent_and_keeps_original_provenance() -> None:
    old = pd.DataFrame(
        [{"timestamp_ms": 2, "value": 20.0, "fetched_at_utc": "old"}]
    )
    new = pd.DataFrame(
        [
            {"timestamp_ms": 2, "value": 20.0, "fetched_at_utc": "new"},
            {"timestamp_ms": 1, "value": 10.0, "fetched_at_utc": "new"},
        ]
    )

    got = merge_rows(old, new, value_columns=["value"])

    assert got["timestamp_ms"].tolist() == [1, 2]
    assert got.loc[got["timestamp_ms"] == 2, "fetched_at_utc"].item() == "old"


def test_merge_rejects_changed_historical_overlap() -> None:
    old = pd.DataFrame([{"timestamp_ms": 2, "value": 20.0}])
    changed = pd.DataFrame([{"timestamp_ms": 2, "value": 21.0}])

    with pytest.raises(ValueError, match="immutable overlap"):
        merge_rows(old, changed, value_columns=["value"])


def test_only_completed_daily_rows_are_persisted() -> None:
    rows = pd.DataFrame(
        {
            "timestamp_ms": [1788393600000, 1788480000000, 1788566400000],
            "value": [1.0, 2.0, 3.0],
        }
    )

    got = finalized_daily_rows(rows, "2026-09-04T20:00:00Z")

    assert got["timestamp_ms"].tolist() == [1788393600000]
