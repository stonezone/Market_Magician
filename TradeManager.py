# TradeManager.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Parameters
stop_loss = 0.02
take_profit = 0.04

# Load test data with predictions
test_data = pd.read_csv("test_data.csv")
test_data['Date'] = pd.to_datetime(test_data['Date'])
test_data.set_index('Date', inplace=True)

# Define trading logic
test_data['Entry_Price'] = 0 # Price at which trade is entered
test_data['Exit_Price'] = 0 # Price at which trade is exited
test_data['Stop_Loss'] = 0 # Price at which trade is stopped out
test_data['Take_Profit'] = 0 # Price at which trade is taken profit
test_data['Trade_Duration'] = 0 # Number of days trade is held
test_data['Trade_Return'] = 0 # Percentage return of trade
test_data['Cum_Return'] = 1 # Cumulative return of strategy

position = 0 # Current position: 0 for no position, 1 for long position, -1 for short position

for i in range(len(test_data)):
    if position == 0: # No position
        if test_data['Pred_Signal'].iloc[i] == 1: # Predicted buy signal
            position = 1 # Enter long position
            test_data['Entry_Price'].iloc[i] = test_data['Open'].iloc[i+1] # Enter at next open price
            test_data['Stop_Loss'].iloc[i] = test_data['Entry_Price'].iloc[i] * (1 - stop_loss) # Set stop loss price
            test_data['Take_Profit'].iloc[i] = test_data['Entry_Price'].iloc[i] * (1 + take_profit) # Set take profit price
        elif test_data['Pred_Signal'].iloc[i] == -1: # Predicted sell signal
            position = -1 # Enter short position
            test_data['Entry_Price'].iloc[i] = test_data['Open'].iloc[i+1] # Enter at next open price
            test_data['Stop_Loss'].iloc[i] = test_data['Entry_Price'].iloc[i] * (1 + stop_loss) # Set stop loss price
            test_data['Take_Profit'].iloc[i] = test_data['Entry_Price'].iloc[i] * (1 - take_profit) # Set take profit price
        elif position == 1: # Long position
         if test_data['Low'].iloc[i+1] <= test_data['Stop_Loss'].iloc[i]: # Next low price hits stop loss
            position = 0 # Exit long position
            test_data['Exit_Price'].iloc[i] = test_data['Stop_Loss'].iloc[i] # Exit at stop loss price
            test_data['Trade_Duration'].iloc[i] = i - test_data[test_data['Entry_Price'] > 0].index[-2] + 1 # Calculate trade duration
            test_data['Trade_Return'].iloc[i] = (test_data['Exit_Price'].iloc[i] / test_data['Entry_Price'].iloc[i]) - 1 # Calculate trade return
            test_data['Cum_Return'].iloc[i] = test_data['Cum_Return'].iloc[i-1] * (1 + test_data['Trade_Return'].iloc[i]) # Calculate cumulative return
        elif test_data['High'].iloc[i+1] >= test_data['Take_Profit'].iloc[i]: # Next high price hits take profit
            position = 0 # Exit long position
            test_data['Exit_Price'].iloc[i] = test_data['Take_Profit'].iloc[i] # Exit at take profit price
            test_data['Trade_Duration'].iloc[i] = i - test_data[test_data['Entry_Price'] > 0].index[-2] + 1 # Calculate trade duration
            test_data['Trade_Return'].iloc[i] = (test_data['Exit_Price'].iloc[i] / test_data['Entry_Price'].iloc[i]) - 1 # Calculate trade return
            test_data['Cum_Return'].iloc[i] = test_data['Cum_Return'].iloc[i-1] * (1 + test_data['Trade_Return'].iloc[i]) # Calculate cumulative return
        elif test_data['Pred_Signal'].iloc[i] == -1: # Predicted sell signal
            position = 0 # Exit long position
            test_data['Exit_Price'].iloc[i] = test_data['Open'].iloc[i+1] # Exit at next open price
            test_data['Trade_Duration'].iloc[i] = i - test_data[test_data['Entry_Price'] > 0].index[-2] + 1 # Calculate trade duration
            test_data['Trade_Return'].iloc[i] = (test_data['Exit_Price'].iloc[i] / test_data['Entry_Price'].iloc[i]) - 1 # Calculate trade return
            test_data['Cum_Return'].iloc[i] = test_data['Cum_Return'].iloc[i-1] * (1 + test_data['Trade_Return'].iloc[i]) # Calculate cumulative return
        elif position == -1: # Short position
         if test_data['High'].iloc[i+1] >= test_data['Stop_Loss'].iloc[i]: # Next high price hits stop loss
            position = 0 # Exit short position
            test_data['Exit_Price'].iloc[i] = test_data['Stop_Loss'].iloc[i] # Exit at stop loss price
            test_data['Trade_Duration'].iloc[i] = i - test_data[test_data['Entry_Price'] > 0].index[-2] + 1 # Calculate trade duration
            test_data['Trade_Return'].iloc[i] = (test_data['Entry_Price'].iloc[i] / test_data['Exit_Price'].iloc[i]) - 1 # Calculate trade return
            test_data['Cum_Return'].iloc[i] = test_data['Cum_Return'].iloc[i-1] * (1 + test_data['Trade_Return'].iloc[i]) # Calculate cumulative return
        elif test_data['Low'].iloc[i+1] <= test_data['Take_Profit'].iloc[i]: # Next low price hits take profit
            position = 0 # Exit short position
            test_data['Exit_Price'].iloc[i] = test_data['Take_Profit'].iloc[i] # Exit at take profit price
            test_data['Trade_Duration'].iloc[i] = i - test_data[test_data['Entry_Price'] > 0].index[-2] + 1 # Calculate trade duration
            test_data['Trade_Return'].iloc[i] = (test_data['Entry_Price'].iloc[i] / test_data['Exit_Price'].iloc[i]) - 1 # Calculate trade return
            test_data['Cum_Return'].iloc[i] = test_data['Cum_Return'].iloc[i-1] * (1 + test_data['Trade_Return'].iloc[i]) # Calculate cumulative return
        elif test_data['Pred_Signal'].iloc[i] == 1: # Predicted buy signal
                            position = 0 # Exit short position
                            test_data['Exit_Price'].iloc[i] = test_data['Open'].iloc[i+1] # Exit at next open price
                            test_data['Trade_Duration'].iloc[i] = i - test_data[test_data['Entry_Price'] > 0].index[-2] + 1 # Calculate trade duration
                            test_data['Trade_Return'].iloc[i] = (test_data['Entry_Price'].iloc[i] / test_data['Exit_Price'].iloc[i]) - 1 # Calculate trade return
                            test_data['Cum_Return'].iloc[i] = test_data['Cum_Return'].iloc[i-1] * (1 + test_data['Trade_Return'].iloc[i]) # Calculate cumulative return
            
                # Print performance metrics
        total_trades = len(test_data[test_data['Trade_Return'] != 0]) # Total number of trades
        winning_trades = len(test_data[test_data['Trade_Return'] > 0]) # Number of winning trades
        losing_trades = len(test_data[test_data['Trade_Return'] < 0]) # Number of losing trades
        win_rate = winning_trades / total_trades # Percentage of winning trades
        avg_win = test_data[test_data['Trade_Return'] > 0]['Trade_Return'].mean() # Average percentage return of winning trades
        avg_loss = test_data[test_data['Trade_Return'] < 0]['Trade_Return'].mean() # Average percentage return of losing trades
        profit_factor = -avg_win * winning_trades / (avg_loss * losing_trades) # Ratio of gross profit to gross loss
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss) # Average percentage return per trade
        max_drawdown = (test_data['Cum_Return'].cummax() - test_data['Cum_Return']).max() # Maximum peak-to-trough decline of cumulative return
        sharpe_ratio = test_data['Trade_Return'].mean() / test_data['Trade_Return'].std() * np.sqrt(252) # Risk-adjusted return per unit of volatility

        print("Total Trades:", total_trades)
        print("Winning Trades:", winning_trades)
        print("Losing Trades:", losing_trades)
        print("Win Rate:", win_rate)
        print("Average Win:", avg_win)
        print("Average Loss:", avg_loss)
        print("Profit Factor:", profit_factor)
        print("Expectancy:", expectancy)
        print("Max Drawdown:", max_drawdown)
        print("Sharpe Ratio:", sharpe_ratio)

        # Plot cumulative return
        test_data['Cum_Return'].plot()
        plt.title('Cumulative Return')
        plt.xlabel('Date')
        plt.ylabel('Return')
        plt.show()
        