"""Parity and safety tests for the B2 forward-paper strategy."""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "user_data" / "strategies"))
sys.path.insert(0, str(ROOT / "user_data" / "research"))

from B2Cascade4h import (
    B2Cascade4h,
    append_jsonl_once,
    calculate_b2_indicators,
    calculate_daily_gate_indicators,
)
import s2_cascade


def _ohlcv(n: int = 240) -> pd.DataFrame:
    date = pd.date_range("2025-01-01", periods=n, freq="4h", tz="UTC")
    close = pd.Series(100 * np.exp(np.linspace(0, 0.2, n) + 0.03 * np.sin(np.arange(n))), index=date)
    return pd.DataFrame(
        {
            "date": date,
            "open": close.to_numpy(),
            "high": (close * 1.01).to_numpy(),
            "low": (close * 0.99).to_numpy(),
            "close": close.to_numpy(),
            "volume": 1000.0,
        }
    )


def _strategy() -> B2Cascade4h:
    """Construct for pure callback tests without starting exchange-facing state."""
    return object.__new__(B2Cascade4h)


def test_indicator_formula_matches_research_harness() -> None:
    """Catches drift in W42/PW180/momentum-6 calculations used by the live port."""
    source = s2_cascade.load("ETH", "1h").resample("4h").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    ).dropna()
    live = calculate_b2_indicators(source.reset_index())
    research = s2_cascade.cond("ETH", 42, 180, "4h", 6)

    assert np.allclose(live["dsd_pct"].tail(100), research["pct"].tail(100), equal_nan=True)
    assert np.allclose(live["mom_24h"].tail(100), research["mom"].tail(100), equal_nan=True)


def test_daily_gate_formula_matches_research_harness() -> None:
    """Catches use of a different EMA convention in the paper strategy."""
    source = s2_cascade.load("ETH", "1d").reset_index()
    live = calculate_daily_gate_indicators(source)
    close = source["close"]

    assert np.allclose(live["sma200"], close.rolling(200).mean(), equal_nan=True)
    assert np.allclose(live["ema20"], close.ewm(span=20).mean(), equal_nan=True)
    assert np.allclose(live["ema50"], close.ewm(span=50).mean(), equal_nan=True)


def test_entry_requires_cascade_btc_drop_and_completed_daily_uptrend() -> None:
    """Catches omission of any of B2's four entry clauses."""
    strategy = _strategy()
    frame = _ohlcv(4)
    frame["dsd_pct"] = [0.9, 0.9, 0.9, 0.9]
    frame["mom_24h"] = [-0.05, -0.05, -0.05, -0.05]
    frame["btc_mom_24h"] = [-0.01, 0.01, -0.01, -0.01]
    frame["sma200_1d"] = 90.0
    frame["ema20_1d"] = [95.0, 95.0, 85.0, 95.0]
    frame["ema50_1d"] = 90.0

    got = strategy.populate_entry_trend(frame, {"pair": "ETH/USDT:USDT"})

    assert got["enter_long"].fillna(0).astype(int).tolist() == [1, 0, 0, 1]


def test_exit_signal_fires_when_dispersion_percentile_recovers() -> None:
    """Catches reversing the research harness's pct-below-0.50 exit."""
    strategy = _strategy()
    frame = _ohlcv(3)
    frame["dsd_pct"] = [0.49, 0.50, 0.80]

    got = strategy.populate_exit_trend(frame, {"pair": "ETH/USDT:USDT"})

    assert got["exit_long"].fillna(0).astype(int).tolist() == [1, 0, 0]


def test_custom_exit_enforces_six_bar_time_stop() -> None:
    """Catches holding beyond the pre-registered 24-hour maximum."""
    strategy = _strategy()
    now = pd.Timestamp("2026-09-05 00:00", tz="UTC").to_pydatetime()
    young = SimpleNamespace(open_date_utc=now - timedelta(hours=23, minutes=59))
    old = SimpleNamespace(open_date_utc=now - timedelta(hours=24))

    assert strategy.custom_exit("BTC/USDT:USDT", young, now, 100.0, 0.0) is None
    assert strategy.custom_exit("BTC/USDT:USDT", old, now, 100.0, 0.0) == "time_stop_24h"


def test_paper_config_is_dry_run_and_uses_isolated_database() -> None:
    """Catches credentials, live mode, or reuse of the running spot bot database."""
    from freqtrade.configuration.load_config import load_from_files

    config = load_from_files([str(ROOT / "user_data" / "config_b2_4h.json")])

    assert config["dry_run"] is True
    assert config["exchange"]["key"] == ""
    assert config["exchange"]["secret"] == ""
    assert config["db_url"] == "sqlite:///tradesv3.b2_4h.dryrun.sqlite"
    assert config["strategy"] == "B2Cascade4h"
    assert config["timeframe"] == "4h"


def test_append_jsonl_once_deduplicates_callback_retries(tmp_path: Path) -> None:
    """Catches duplicate forward events when Freqtrade retries one order callback."""
    path = tmp_path / "events.jsonl"
    record = {"event_id": "BTC|2026-09-05T00:00:00Z|entry", "rate": 100.0}

    assert append_jsonl_once(path, record) is True
    assert append_jsonl_once(path, {**record, "rate": 101.0}) is False

    assert path.read_text(encoding="utf-8").splitlines() == [
        '{"event_id":"BTC|2026-09-05T00:00:00Z|entry","rate":100.0}'
    ]


def test_confirm_trade_entry_records_forward_signal_once(tmp_path: Path) -> None:
    """Catches a paper entry that has no auditable theoretical-vs-proposed record."""
    strategy = _strategy()
    strategy.forward_event_log = tmp_path / "events.jsonl"
    candle_time = pd.Timestamp("2026-09-05 00:00", tz="UTC")
    analyzed = pd.DataFrame(
        [{"date": candle_time, "close": 100.0, "dsd_pct": 0.91, "mom_24h": -0.05, "btc_mom_24h": -0.02}]
    )
    strategy.dp = SimpleNamespace(get_analyzed_dataframe=lambda **_: (analyzed, None))
    now = (candle_time + timedelta(hours=4, seconds=7)).to_pydatetime()

    args = dict(
        pair="ETH/USDT:USDT",
        order_type="market",
        amount=5.0,
        rate=101.0,
        time_in_force="GTC",
        current_time=now,
        entry_tag="b2_cascade",
        side="long",
    )
    assert strategy.confirm_trade_entry(**args) is True
    assert strategy.confirm_trade_entry(**args) is True

    records = [__import__("json").loads(line) for line in strategy.forward_event_log.read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["signal_close"] == 100.0
    assert records[0]["proposed_rate"] == 101.0
    assert records[0]["decision_latency_seconds"] == 7.0
