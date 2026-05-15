# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these imports ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
from typing import Optional, Union

from freqtrade.strategy import (
    IStrategy,
    Trade,
    Order,
    PairLocks,
    informative,
    timeframe_to_minutes,
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
)

# --------------------------------
import talib.abstract as ta
from technical import qtpylib


class EmaRsiVolumeStrategy(IStrategy):
    """
    Entry:  EMA9 > EMA21, close > EMA50 (1h), ADX > 25, RSI > 52,
            volume > 3.5x 20-period SMA,
            daily EMA20 > daily EMA50, daily close > daily EMA50 (regime filter)
    Exit:   trailing stop (3% trail, activates after 4% gain)
    """

    INTERFACE_VERSION = 3
    can_short: bool = False

    minimal_roi = {
        "0": 1.0,
    }

    stoploss = -0.03
    trailing_stop = True
    trailing_stop_positive = 0.03
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True
    use_custom_stoploss = False

    timeframe = "1h"
    startup_candle_count: int = 100

    process_only_new_candles = True
    use_exit_signal = False
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    order_types = {
        "entry":                "limit",
        "exit":                 "limit",
        "stoploss":             "market",
        "stoploss_on_exchange":  False,
    }

    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    plot_config = {
        "main_plot": {
            "ema9":  {"color": "blue"},
            "ema21": {"color": "orange"},
            "ema50": {"color": "red"},
        },
        "subplots": {
            "RSI": {"rsi": {"color": "purple"}},
            "ADX": {"adx": {"color": "green"}},
            "Volume": {
                "volume":     {"color": "rgba(0,150,255,0.3)"},
                "volume_sma": {"color": "red"},
            },
        },
    }

    @informative('1d')
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema9"]       = ta.EMA(dataframe, timeperiod=9)
        dataframe["ema21"]      = ta.EMA(dataframe, timeperiod=21)
        dataframe["ema50"]      = ta.EMA(dataframe, timeperiod=50)
        dataframe["rsi"]        = ta.RSI(dataframe, timeperiod=14)
        dataframe["adx"]        = ta.ADX(dataframe, timeperiod=14)
        dataframe["volume_sma"] = ta.SMA(dataframe["volume"], timeperiod=20)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema9"] > dataframe["ema21"])           # 1h short-term uptrend
                & (dataframe["close"] > dataframe["ema50"])        # 1h broad uptrend
                & (dataframe["adx"] > 25)                          # trending market only
                & (dataframe["rsi"] > 52)                          # bullish momentum
                & (dataframe["volume"] > dataframe["volume_sma"] * 3.5)  # high-conviction volume
                & (dataframe["volume"] > 0)
                & (dataframe["ema20_1d"] > dataframe["ema50_1d"])  # daily regime: EMA20 > EMA50
                & (dataframe["close"] > dataframe["ema50_1d"])     # daily regime: close > EMA50
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe
