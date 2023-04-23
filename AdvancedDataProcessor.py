# Importing the libraries
import numpy as np
import pandas as pd
import talib as ta
from sklearn.model_selection import ParameterGrid

# Defining the class
class AdvancedDataProcessor:

    # Initializing the class
    def __init__(self):
        # Defining the parameters for the indicators
        self.params = {
            'sma': {'timeperiod': [5, 10, 20, 50, 100, 200]},
            'ema': {'timeperiod': [5, 10, 20, 50, 100, 200]},
            'rsi': {'timeperiod': [6, 12, 24]},
            'macd': {'fastperiod': [12], 'slowperiod': [26], 'signalperiod': [9]},
            'stoch': {'fastk_period': [14], 'slowk_period': [3], 'slowd_period': [3]},
            'adx': {'timeperiod': [14]},
            'atr': {'timeperiod': [14]}
        }
        # Defining the thresholds for the entry and exit signals
        self.thresholds = {
            'rsi_buy': 30,
            'rsi_sell': 70,
            'macd_buy': 0,
            'macd_sell': 0,
            'stoch_buy': 20,
            'stoch_sell': 80,
            'adx_trend': 25
        }
        # Initializing an empty dataframe for the processed data
        self.data = pd.DataFrame()

    # Defining a helper function to generate column names for the indicators
    def generateColName(self, indicator, params):
        # Creating a column name with the indicator and the parameter values
        col = indicator + '_' + '_'.join([str(v) for v in params.values()])
        # Returning the column name
        return col

    # Defining the method to process the data and generate the indicators
    def processData(self, data):
        # Creating a copy of the data
        data = data.copy()
        # Looping through the indicators
        for indicator in self.params:
            # Getting the parameters for the indicator
            params = self.params[indicator]
            # Creating a grid of possible parameter combinations
            grid = ParameterGrid(params)
            # Looping through the parameter combinations
            for p in grid:
                # Generating the indicator values using TA-Lib
                values = getattr(ta, indicator.upper())(data['Close'], **p)
                # Handling indicators with multiple outputs (such as MACD or STOCH)
                if isinstance(values, tuple):
                    # Looping through the outputs
                    for i in range(len(values)):
                        # Generating a column name with the indicator and the parameter values using the helper function
                        col = self.generateColName(indicator, p)
                        # Adding a suffix for the output index
                        col += '_' + str(i)
                        # Adding the column to the data
                        data[col] = values[i]
                else:
                    # Generating a column name with the indicator and the parameter values using the helper function
                    col = self.generateColName(indicator, p)
                    # Adding the column to the data
                    data[col] = values
        
        # Storing the processed data as a class attribute
        self.data = data

    # Defining the method to generate the entry and exit signals based on the indicators
    def generateSignals(self):
        # Initializing an empty list for the signals
        signals = []
        # Looping through the rows of the processed data (using self.data instead of passing it as an argument)
        for i in range(len(self.data)):
            # Getting the current row as a dictionary
            row = self.data.iloc[i].to_dict()
    # Initializing an empty dictionary for the signal
            signal = {}
                # Setting the date and price of the signal
            signal['Date'] = row['Date']
            signal['Price'] = row['Close']
                # Initializing a list for the buy reasons and sell reasons
            buy_reasons = []
            sell_reasons = []
            
                ### SMA and EMA ###
            
                # Getting all the columns that start with sma or ema
            sma_cols = [col for col in row if col.startswith('sma')]
            ema_cols = [col for col in row if col.startswith('ema')]
            
                # Looping through all possible combinations of sma and ema columns (crosses)
            for sma_col in sma_cols:
                    for ema_col in ema_cols:
                        # Getting the current and previous values of sma and ema
                        curr_sma = row[sma_col]
                        prev_sma = self.data.iloc[i-1][sma_col]
                        curr_ema = row[ema_col]
                        prev_ema = self.data.iloc[i-1][ema_col]
                        # Checking if there is a bullish cross (sma crosses above ema)
                        if curr_sma > curr_ema and prev_sma < prev_ema:
                            # Adding a buy reason with the sma and ema parameters
                            buy_reasons.append(f'SMA {sma_col.split("_")[1]} crossed above EMA {ema_col.split("_")[1]}')
                        # Checking if there is a bearish cross (sma crosses below ema)
                        if curr_sma < curr_ema and prev_sma > prev_ema:
                            # Adding a sell reason with the sma and ema parameters
                            sell_reasons.append(f'SMA {sma_col.split("_")[1]} crossed below EMA {ema_col.split("_")[1]}')
            
                ### RSI ###
            
                # Getting all the columns that start with rsi
            rsi_cols = [col for col in row if col.startswith('rsi')]
            
                # Looping through all the rsi columns
            for rsi_col in rsi_cols:
                    # Getting the current value of rsi
                    curr_rsi = row[rsi_col]
                    # Checking if the rsi is below the buy threshold
                    if curr_rsi < self.thresholds['rsi_buy']:
                        # Adding a buy reason with the rsi parameter
                        buy_reasons.append(f'RSI {rsi_col.split("_")[1]} below {self.thresholds["rsi_buy"]}')
                    # Checking if the rsi is above the sell threshold
                    if curr_rsi > self.thresholds['rsi_sell']:
                        # Adding a sell reason with the rsi parameter
                        sell_reasons.append(f'RSI {rsi_col.split("_")[1]} above {self.thresholds["rsi_sell"]}')
            
                ### MACD ###
            
                # Getting all the columns that start with macd and end with 0 (macd line)
            macd_cols = [col for col in row if col.startswith('macd') and col.endswith('0')]
            
                # Looping through all the macd columns
            for macd_col in macd_cols:
                    # Getting the corresponding signal line column (ending with 1)
                    signal_col = macd_col[:-1] + '1'
                    # Getting the current and previous values of macd and signal lines
                    curr_macd = row[macd_col]
                    prev_macd = self.data.iloc[i-1][macd_col]
                    curr_signal = row[signal_col]
                    prev_signal = self.data.iloc[i-1][signal_col]
                    # Checking if there is a bullish cross (macd crosses above signal line)
                    if curr_macd > curr_signal and prev_macd < prev_signal:
                        # Adding a buy reason with the macd parameters
                        buy_reasons.append(f'MACD {macd_col.split("_")[1:4]} crossed above signal line')
                    # Checking if there is a bearish cross (macd crosses below signal line)
                    if curr_macd < curr_signal and prev_macd > prev_signal:
                        # Adding a sell reason with the macd parameters
                        sell_reasons.append(f'MACD {macd_col.split("_")[1:4]} crossed below signal line')
            
                ### STOCH ###
                
                # Getting all the columns that start with stoch and end with 0 (slowk line)
                    stoch_cols = [col for col in row if col.startswith('stoch') and col.endswith('0')]
            
                            # Looping through all the stoch columns
                    for stoch_col in stoch_cols:
                                # Getting the corresponding slowd line column (ending with 1)
                                slowd_col = stoch_col[:-1] + '1'
                                # Getting the current values of slowk and slowd lines
                                curr_slowk = row[stoch_col]
                                curr_slowd = row[slowd_col]
                                # Checking if both lines are below the buy threshold
                                if curr_slowk < self.thresholds['stoch_buy'] and curr_slowd < self.thresholds['stoch_buy']:
                                    # Adding a buy reason with the stoch parameters
                                    buy_reasons.append(f'STOCH {stoch_col.split("_")[1:4]} below {self.thresholds["stoch_buy"]}')
                                # Checking if both lines are above the sell threshold
                                if curr_slowk > self.thresholds['stoch_sell'] and curr_slowd > self.thresholds['stoch_sell']:
                                    # Adding a sell reason with the stoch parameters
                                    sell_reasons.append(f'STOCH {stoch_col.split("_")[1:4]} above {self.thresholds["stoch_sell"]}')
            
                            ### ADX ###
            
                            # Getting all the columns that start with adx
                    adx_cols = [col for col in row if col.startswith('adx')]
            
                            # Looping through all the adx columns
                    for adx_col in adx_cols:
                                # Getting the current value of adx
                                curr_adx = row[adx_col]
                                # Checking if the adx is above the trend threshold
                                if curr_adx > self.thresholds['adx_trend']:
                                    # Adding a trend reason with the adx parameter
                                    trend_reason = f'ADX {adx_col.split("_")[1]} above {self.thresholds["adx_trend"]}'
                                else:
                                    # Setting the trend reason to None
                                    trend_reason = None
            
                            ### ATR ###
            
                            # Getting all the columns that start with atr
                    atr_cols = [col for col in row if col.startswith('atr')]
            
                            # Looping through all the atr columns
                    for atr_col in atr_cols:
                                # Getting the current value of atr
                                curr_atr = row[atr_col]
                                # Calculating the stop loss price based on the atr value and a multiplier
                                stop_loss = row['Close'] - curr_atr * 2
                                # Adding a stop loss reason with the atr parameter and the stop loss price
                                stop_loss_reason = f'ATR {atr_col.split("_")[1]} stop loss at {stop_loss:.2f}'
            
                            # Checking if there are any buy reasons and no sell reasons
                    if buy_reasons and not sell_reasons:
                                # Setting the signal type to buy
                                signal['Type'] = 'Buy'
                                # Joining all the buy reasons with commas
                                signal['Reason'] = ', '.join(buy_reasons)
                                # Adding the trend reason if any
                                if trend_reason:
                                    signal['Reason'] += ', ' + trend_reason
                                # Adding the stop loss reason
                                signal['Reason'] += ', ' + stop_loss_reason
            
                            # Checking if there are any sell reasons and no buy reasons
                    elif sell_reasons and not buy_reasons:
                                # Setting the signal type to sell
                                signal['Type'] = 'Sell'
                                # Joining all the sell reasons with commas
                                signal['Reason'] = ', '.join(sell_reasons)
                                # Adding the trend reason if any
                                if trend_reason:
                                    signal['Reason'] += ', ' + trend_reason
                                # Adding the stop loss reason
                                signal['Reason'] += ', ' + stop_loss_reason
            
                            # Otherwise, setting the signal type to hold
                    else:
                                signal['Type'] = 'Hold'
                                signal['Reason'] = 'No clear signal'
            
                            # Appending the signal to the list of signals
                    signals.append(signal)
        
                        # Converting the list of signals to a dataframe
                    signals = pd.DataFrame(signals)
                        # Returning the signals dataframe
                    return signals