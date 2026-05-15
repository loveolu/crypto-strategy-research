# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
from typing import Optional, Union

from freqtrade.strategy import (
    IStrategy, Trade, Order, PairLocks, informative,
    timeframe_to_minutes, merge_informative_pair,
    stoploss_from_absolute, stoploss_from_open,
)
import talib.abstract as ta
from technical import qtpylib


class MeanReversionStrategy(IStrategy):
    """
    MR3: Mean reversion in a bullish daily regime.
    Entry:  RSI crossed above 45 from below AND lower Bollinger Band was touched
            on the prior candle AND close > EMA50 AND daily regime bullish.
    Exit:   6% ROI cap OR trailing stop (3% trail activates after 5% gain).
    Stoploss: -4%.
    """

    INTERFACE_VERSION = 3
    can_short: bool = False

    minimal_roi = {"0": 0.06}

    stoploss = -0.04
    trailing_stop = True
    trailing_stop_positive = 0.03
    trailing_stop_positive_offset = 0.05
    trailing_only_offset_is_reached = True
    use_custom_stoploss = False

    timeframe = "1h"
    startup_candle_count: int = 100
    process_only_new_candles = True
    use_exit_signal = False
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    order_types = {
        "entry": "limit", "exit": "limit",
        "stoploss": "market", "stoploss_on_exchange": False,
    }
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    @informative('1d')
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema50"]      = ta.EMA(dataframe, timeperiod=50)
        dataframe["rsi"]        = ta.RSI(dataframe, timeperiod=14)
        dataframe["rsi_prev"]   = dataframe["rsi"].shift(1)
        dataframe["adx"]        = ta.ADX(dataframe, timeperiod=14)
        dataframe["volume_sma"] = ta.SMA(dataframe["volume"], timeperiod=20)
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe["bb_lower"]   = bb["lowerband"]
        dataframe["bb_mid"]     = bb["middleband"]
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] > 45)                                    # RSI crossed above 45
                & (dataframe["rsi_prev"] <= 45)                            # from below
                & (dataframe["close"].shift(1) <= dataframe["bb_lower"].shift(1))  # prior candle touched lower BB
                & (dataframe["close"] > dataframe["ema50"])                # above structural support
                & (dataframe["adx"] < 40)                                  # not in a hard directional trend
                & (dataframe["volume"] > dataframe["volume_sma"] * 0.8)
                & (dataframe["ema20_1d"] > dataframe["ema50_1d"])          # daily regime bullish
                & (dataframe["close"] > dataframe["ema50_1d"])
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe
