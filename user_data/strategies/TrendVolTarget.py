# TrendVolTarget.py
# Best risk-adjusted construct from the 2026-06-11 autonomous research session.
#
# Design (all components individually plateau-robust, see user_data/research/):
#   Core entry (3-of-3 trend agreement, per asset):
#     close > SMA200  AND  ROC30 > 0  AND  EMA20 > EMA50
#   Exit: any core condition breaks.
#   Sizing: vol-targeted — stake scaled by clip(40% / realized_vol_30d, 0, 1),
#     quantized to 25% steps, max 50% of equity per pair (BTC + ETH basket).
#
# Validation summary (pandas harness, fees 0.1% + slippage 0.05% per side):
#   BTC+ETH 2019-12..2026-05 (6.5y): CAGR +32.4%, Sharpe 1.33, MaxDD -17.1%
#   BTC-only 2018-01..2026-05 (8.4y): CAGR +30.7%, Sharpe 1.20, MaxDD -23.6%
#   ZERO days in market during 2018 and 2022 bear years.
#   Walk-forward: 3/4 windows positive; 4th (2025-08..2026-05) flat at -2.4%.
#   Monte Carlo (1000 block-shuffles + extra slippage): P(Sharpe<0) = 0%,
#     median DD -23.5%, P(DD < -25%) = 38%.
#   HONEST CAVEATS:
#     - Held-out test period (mid-2024..2026) Sharpe only 0.41 (train 1.59).
#       Forward expectation: high-single-digit CAGR at ~20% DD, NOT +32%.
#     - Most absolute return came from 2020-2021. Edge is regime-avoidance
#       (sit out bears), not alpha generation.
#     - DO NOT deploy real money on the basis of this backtest.
#
# Freqtrade 2026.x | OKX spot | dry-run only.

from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy


class TrendVolTarget(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = "1d"
    startup_candle_count: int = 250

    # Trend exit is the primary risk control; stop is a disaster brake only.
    stoploss = -0.30
    use_custom_stoploss = False
    trailing_stop = False

    # Exits handled by signal, not ROI.
    minimal_roi = {"0": 100.0}
    use_exit_signal = True
    exit_profit_only = False

    # Allow rebalancing as vol scale changes
    position_adjustment_enable = True
    max_entry_position_adjustment = 8

    # Vol-target parameters (plateau-robust 30-50%; 40% chosen mid-plateau)
    VOL_TARGET = 0.40
    VOL_LOOKBACK = 30
    QUANT_STEP = 0.25
    PER_PAIR_CAP = 0.50  # max fraction of total equity per pair (2-pair basket)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        c = dataframe["close"]
        dataframe["sma200"] = c.rolling(200).mean()
        dataframe["roc30"] = c.pct_change(30)
        dataframe["ema20"] = c.ewm(span=20, adjust=False).mean()
        dataframe["ema50"] = c.ewm(span=50, adjust=False).mean()
        rv = c.pct_change().rolling(self.VOL_LOOKBACK).std() * np.sqrt(365)
        scale = (self.VOL_TARGET / rv).clip(0, 1)
        # quantize to 25% steps
        dataframe["vt_scale"] = (scale / self.QUANT_STEP).round() * self.QUANT_STEP
        dataframe["core"] = (
            (c > dataframe["sma200"])
            & (dataframe["roc30"] > 0)
            & (dataframe["ema20"] > dataframe["ema50"])
        ).astype(int)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["core"] == 1) & (dataframe["vt_scale"] > 0) & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe["core"] == 0, "exit_long"] = 1
        return dataframe

    # ---- vol-targeted stake sizing ----

    def _desired_fraction(self, pair: str, current_time: datetime) -> float:
        """Target fraction of total equity for this pair right now."""
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return 0.0
        row = df.iloc[-1]
        if row.get("core", 0) != 1:
            return 0.0
        scale = float(row.get("vt_scale", 0.0))
        return max(0.0, min(1.0, scale)) * self.PER_PAIR_CAP

    def custom_stake_amount(
        self, pair: str, current_time: datetime, current_rate: float,
        proposed_stake: float, min_stake: Optional[float], max_stake: float,
        leverage: float, entry_tag: Optional[str], side: str, **kwargs,
    ) -> float:
        frac = self._desired_fraction(pair, current_time)
        if frac <= 0:
            return 0.0
        total = self.wallets.get_total_stake_amount()
        stake = total * frac
        return max(min_stake or 0.0, min(stake, max_stake))

    def adjust_trade_position(
        self, trade: Trade, current_time: datetime, current_rate: float,
        current_profit: float, min_stake: Optional[float], max_stake: float,
        current_entry_rate: float, current_exit_rate: float,
        current_entry_profit: float, current_exit_profit: float, **kwargs,
    ) -> Optional[float]:
        """Rebalance stake toward the vol-target as the scale changes (25% steps)."""
        frac = self._desired_fraction(trade.pair, current_time)
        total = self.wallets.get_total_stake_amount()
        desired = total * frac
        current = trade.stake_amount
        # only act when drift exceeds half a quantization step of per-pair equity
        threshold = total * self.PER_PAIR_CAP * self.QUANT_STEP / 2
        diff = desired - current
        if abs(diff) < threshold:
            return None
        if diff > 0:
            return min(diff, max_stake - current)
        # negative = partial exit
        return max(diff, -current * 0.9)
