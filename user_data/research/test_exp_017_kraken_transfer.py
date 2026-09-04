"""Behavior tests for the frozen B2 Kraken transfer harness."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp_017_kraken_transfer import align_completed_daily_gate, simulate_trades


def test_daily_gate_becomes_available_only_after_six_four_hour_bars() -> None:
    daily_index = pd.date_range("2024-01-01", periods=2, freq="1D", tz="UTC")
    four_hour_index = pd.date_range("2024-01-01", periods=12, freq="4h", tz="UTC")
    daily_gate = pd.Series([True, False], index=daily_index)

    got = align_completed_daily_gate(daily_gate, four_hour_index)

    assert got.iloc[:6].eq(False).all()
    assert got.iloc[6:].eq(True).all()


def test_trade_uses_next_open_and_exits_after_recovery_signal() -> None:
    index = pd.date_range("2024-01-01", periods=7, freq="4h", tz="UTC")
    frame = pd.DataFrame(
        {
            "open": [100, 100, 100, 101, 103, 104, 105],
            "pct": [0.1, 0.9, 0.9, 0.4, 0.4, 0.4, 0.4],
            "mom": [0.0, -0.04, -0.04, -0.03, 0.0, 0.0, 0.0],
            "btc_mom": [-0.01] * 7,
            "gate": [True] * 7,
        },
        index=index,
    )

    trades = simulate_trades(frame, instrument="ALT")

    assert len(trades) == 1
    trade = trades.iloc[0]
    assert trade.signal_time == index[1]
    assert trade.entry_time == index[2]
    assert trade.exit_time == index[4]
    assert np.isclose(trade.gross, 0.03)


def test_trade_timestamps_match_original_okx_b2_harness() -> None:
    """Guards against declaring exchange transfer with a mechanically different rule."""
    import s2_cascade as original

    instrument = "ETH"
    indicators = original.cond(instrument, 42, 180, "4h", 6)
    gate = original.gate(instrument).reindex(indicators.index, method="ffill").shift(6).fillna(0).astype(bool)
    frame = pd.DataFrame(
        {
            "open": indicators["o"],
            "pct": indicators["pct"],
            "mom": indicators["mom"],
            "btc_mom": original.cond("BTC", 42, 180, "4h", 6)["mom"].reindex(indicators.index),
            "gate": gate,
        }
    )

    got = simulate_trades(frame, instrument)
    expected, _ = original.trades(
        instrument,
        W=42,
        PW=180,
        HOLD=6,
        mom_bars=6,
        gate_shift=6,
        tf="4h",
        mom_thr=0.0385,
        btc_cond=True,
    )

    assert got["entry_time"].tolist() == expected["entry"].tolist()
    assert got["exit_time"].tolist() == expected["exit"].tolist()
