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


class BollingerBreakoutStrategy(IStrategy):
    """
    Bollinger Band squeeze breakout strategy (user spec).
    Entry: BB width < 20-period avg BB width × 0.7 (squeeze),
           close breaks above upper BB,
           daily EMA20 > daily EMA50,
           volume > volume_sma × 1.5
    Exit: trailing stop (3% trail, activates after 4% gain), -3% stoploss
    """

    INTERFACE_VERSION = 3
    can_short: bool = False

    minimal_roi = {"0": 1.0}

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
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe["bb_upper"]   = bb["upperband"]
        dataframe["bb_lower"]   = bb["lowerband"]
        dataframe["bb_mid"]     = bb["middleband"]

        # BB width as fraction of mid
        dataframe["bb_width"]     = (dataframe["bb_upper"] - dataframe["bb_lower"]) / dataframe["bb_mid"]
        dataframe["bb_width_sma"] = ta.SMA(dataframe["bb_width"], timeperiod=20)

        dataframe["volume_sma"]   = ta.SMA(dataframe["volume"], timeperiod=20)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["bb_width"] < dataframe["bb_width_sma"] * 0.7)  # squeeze
                & (dataframe["close"] > dataframe["bb_upper"])              # breakout above upper BB
                & (dataframe["volume"] > dataframe["volume_sma"] * 1.5)    # volume confirmation
                & (dataframe["ema20_1d"] > dataframe["ema50_1d"])           # daily regime
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe
