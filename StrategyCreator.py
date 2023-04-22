# StrategyCreator.py

import logging
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Tuple, Callable, Union
import talib
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Indicator(ABC):

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        pass

class MovingAverage(Indicator):

    def __init__(self, window: int, column: str = "close"):
        self.window = window
        self.column = column

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data[self.column].rolling(window=self.window).mean()

class MACD(Indicator):

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        macd, signal, hist = talib.MACD(data["close"], fastperiod=self.fast_period, slowperiod=self.slow_period, signalperiod=self.signal_period)
        return macd, signal, hist

class BollingerBands(Indicator):

    def __init__(self, window: int = 20, nbdevup: float = 2, nbdevdn: float = 2):
        self.window = window
        self.nbdevup = nbdevup
        self.nbdevdn = nbdevdn

    def calculate(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        upper, middle, lower = talib.BBANDS(data["close"], timeperiod=self.window, nbdevup=self.nbdevup, nbdevdn=self.nbdevdn)
        return upper, middle, lower

class ATR(Indicator):

    def __init__(self, window: int = 14):
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return talib.ATR(data["high"], data["low"], data["close"], timeperiod=self.window)

class Strategy:

    def __init__(self, entry_condition: Callable, exit_condition: Callable, stop_loss: float = None, take_profit: float = None):
        self.entry_condition = entry_condition
        self.exit_condition = exit_condition
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        entry_signals = self.entry_condition(data)
        exit_signals = self.exit_condition(data)
        return entry_signals, exit_signals

def simple_moving_average_strategy(data: pd.DataFrame) -> Strategy:
    ma_short = MovingAverage(window=50)
    ma_long = MovingAverage(window=200)

    def entry_condition(data: pd.DataFrame) -> pd.Series:
        short_ma = ma_short.calculate(data)
        long_ma = ma_long.calculate(data)
        return (short_ma > long_ma).shift(1).fillna(False)

    def exit_condition(data: pd.DataFrame) -> pd.Series:
        short_ma = ma_short.calculate(data)
        long_ma = ma_long.calculate(data)
        return (short_ma < long_ma).shift(1).fillna(False)

    r    return Strategy(entry_condition, exit_condition)

def backtest_strategy(strategy: Strategy, data: pd.DataFrame, initial_capital: float = 10000) -> pd.DataFrame:
    entry_signals, exit_signals = strategy.generate_signals(data)

    positions = pd.Series(np.zeros(len(data)), index=data.index, name="positions")
    entry_price = pd.Series(np.zeros(len(data)), index=data.index, name="entry_price")

    open_position = False
    for i in range(len(data)):
        if not open_position and entry_signals[i]:
            positions[i] = 1
            entry_price[i] = data["close"][i]
            open_position = True
        elif open_position and exit_signals[i]:
            positions[i] = -1
            entry_price[i] = 0
            open_position = False

    capital = (positions * (data["close"] - entry_price)).cumsum() + initial_capital

    results = pd.concat([data, positions, entry_price, capital], axis=1)
    results.rename(columns={0: "capital"}, inplace=True)

    return results

def plot_backtest_results(backtest_results: pd.DataFrame):
    fig, ax1 = plt.subplots()
    ax1.plot(backtest_results["close"], label="Close Price")
    ax1.set_ylabel("Price")

    ax2 = ax1.twinx()
    ax2.plot(backtest_results["capital"], color="orange", label="Capital")
    ax2.set_ylabel("Capital")

    plt.title("Backtest Results")
    plt.show()

if __name__ == "__main__":
    data = pd.read_csv("sample_data.csv", index_col="date", parse_dates=True)
    strategy = simple_moving_average_strategy(data)
    backtest_results = backtest_strategy(strategy, data)
    plot_backtest_results(backtest_results)

