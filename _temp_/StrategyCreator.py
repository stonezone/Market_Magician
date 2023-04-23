# import needed libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from AdvancedDataProcessor import AdvancedDataProcessor

# define the StrategyCreator class


class StrategyCreator:
    # initialize the class with the data and parameters
    def __init__(self, data, initial_capital=100000, commission=0.001):
        self.data = data  # the market data as a pandas DataFrame
        self.initial_capital = initial_capital  # the initial capital for trading
        self.commission = commission  # the commission rate for each trade
        # an instance of the AdvancedDataProcessor class
        self.adp = AdvancedDataProcessor()
        self.model = None  # the machine learning model for trading signals

    # define a method to create the machine learning model
    def create_model(
        self,
        input_dim,
        output_dim,
        hidden_layers,
        activation,
        dropout_rate,
        learning_rate,
    ):
        # input_dim: the number of input features (technical indicators)
        # output_dim: the number of output classes (buy, sell, or hold)
        # hidden_layers: a list of integers indicating the number of neurons in each hidden layer
        # activation: the activation function for the hidden layers
        # dropout_rate: the dropout rate for regularization
        # learning_rate: the learning rate for the optimizer

        # create a sequential model
        self.model = Sequential()

        # add the first hidden layer with input dimension
        self.model.add(
            Dense(hidden_layers[0], input_dim=input_dim, activation=activation)
        )

        # add dropout layer if dropout_rate is positive
        if dropout_rate > 0:
            self.model.add(Dropout(dropout_rate))

        # add the remaining hidden layers with dropout layers if needed
        for i in range(1, len(hidden_layers)):
            self.model.add(Dense(hidden_layers[i], activation=activation))
            if dropout_rate > 0:
                self.model.add(Dropout(dropout_rate))

        # add the output layer with softmax activation
        self.model.add(Dense(output_dim, activation="softmax"))

        # compile the model with Adam optimizer and categorical crossentropy loss
        self.model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

    # define a method to train the machine learning model on historical data
    def train_model(
        self, train_start_date, train_end_date, window_size, batch_size, epochs
    ):
        # train_start_date: the start date of the training period as a string in YYYY-MM-DD format
        # train_end_date: the end date of the training period as a string in YYYY-MM-DD format
        # window_size: the number of previous days to use as input features
        # batch_size: the batch size for training
        # epochs: the number of epochs for training

        # filter the data by the training period
        train_data = self.data.loc[train_start_date:train_end_date]

        # get the technical indicators from the AdvancedDataProcessor class
        indicators = self.adp.get_indicators(train_data)

        # scale the indicators to be between 0 and 1 using MinMaxScaler
        scaler = MinMaxScaler()
        indicators_scaled = scaler.fit_transform(indicators)

        # create empty lists to store the input features (X) and output labels (y)
        X = []
        y = []

        # loop through the indicators and create X and y by using a sliding window of size window_size
        for i in range(window_size, len(indicators_scaled)):
            # get the indicators for the current window as input features
            X.append(indicators_scaled[i - window_size : i])

            # get the price change for the next day as output label (1 for positive change, 0 for negative change or no change)
            price_change = train_data["Close"].iloc[i] - train_data["Close"].iloc[i - 1]
            if price_change > 0:
                y.append(1)
            else:
                y.append(0)

        # convert X and y to numpy arrays
        X = np.array(X)
        y = np.array(y)

        # one-hot encode y to have three classes: buy (1, 0, 0), sell (0, 1, 0), or hold (0, 0, 1)
        y = np.eye(3)[y]

        # train the model on X and y using batch_size and epochs
        self.model.fit(X, y, batch_size=batch_size, epochs=epochs)
        # save the scaler and the model for later use

        self.scaler = scaler
        self.model.save("model.h5")
        # define a method to backtest the strategy on historical data

        def backtest_strategy(self, test_start_date, test_end_date, window_size):
            # test_start_date: the start date of the testing period as a string in YYYY-MM-DD format
            # test_end_date: the end date of the testing period as a string in YYYY-MM-DD format
            # window_size: the number of previous days to use as input features

            # filter the data by the testing period
            test_data = self.data.loc[test_start_date:test_end_date]

            # get the technical indicators from the AdvancedDataProcessor class
            indicators = self.adp.get_indicators(test_data)

            # scale the indicators using the scaler saved from the training
            indicators_scaled = self.scaler.transform(indicators)

            # create empty lists to store the input features (X) and output labels (y)
            X = []
            y = []

            # loop through the indicators and create X and y by using a sliding window of size window_size
            for i in range(window_size, len(indicators_scaled)):
                # get the indicators for the current window as input features
                X.append(indicators_scaled[i - window_size : i])

                # get the price change for the next day as output label (1 for positive change, 0 for negative change or no change)
                price_change = (
                    test_data["Close"].iloc[i] - test_data["Close"].iloc[i - 1]
                )
                if price_change > 0:
                    y.append(1)
                else:
                    y.append(0)

            # convert X and y to numpy arrays
            X = np.array(X)
            y = np.array(y)

            # one-hot encode y to have three classes: buy (1, 0, 0), sell (0, 1, 0), or hold (0, 0, 1)
            y = np.eye(3)[y]

            # load the model saved from the training
            self.model = keras.models.load_model("model.h5")
            #
            # predict the output labels for X using the model
            y_pred = self.model.predict(X)
            # get the predicted signals as a list of integers (0 for buy, 1 for sell, or 2 for hold)
            signals = np.argmax(y_pred, axis=1)

            # create a new column in the test data to store the signals
            test_data["Signal"] = signals

            # create a new column in the test data to store the positions (1 for long, -1 for short, or 0 for flat)
            test_data["Position"] = test_data["Signal"].diff()

            # create a new column in the test data to store the returns (percentage change in price)
            test_data["Return"] = test_data["Close"].pct_change()

            # create a new column in the test data to store the strategy returns (returns multiplied by positions)
            test_data["Strategy_Return"] = test_data["Return"] * test_data["Position"]

            # create a new column in the test data to store the cumulative returns
            test_data["Cumulative_Return"] = (test_data["Return"] + 1).cumprod()

            # create a new column in the test data to store the cumulative strategy returns
            test_data["Cumulative_Strategy_Return"] = (
                test_data["Strategy_Return"] + 1
            ).cumprod()

            # plot the cumulative returns and cumulative strategy returns
            plt.figure(figsize=(12, 8))
            plt.plot(test_data["Cumulative_Return"], label="Buy and Hold")
            plt.plot(
                test_data["Cumulative_Strategy_Return"],
                label="Machine Learning Strategy",
            )
            plt.title("Backtesting Results")
            plt.xlabel("Date")
            plt.ylabel("Cumulative Return")
            plt.legend()
            plt.show()

            # define a method to optimize the strategy parameters using grid search
            def optimize_strategy(
                self,
                train_start_date,
                train_end_date,
                window_size_range,
                batch_size_range,
                epochs_range,
            ):
                # train_start_date: the start date of the training period as a string in YYYY-MM-DD format
                # train_end_date: the end date of the training period as a string in YYYY-MM-DD format
                # window_size_range: a list of integers indicating the range of window sizes to try
                # batch_size_range: a list of integers indicating the range of batch sizes to try
                # epochs_range: a list of integers indicating the range of epochs to try

                # create an empty list to store the results
                results = []

                # loop through all possible combinations of parameters
                for window_size in window_size_range:
                    for batch_size in batch_size_range:
                        for epochs in epochs_range:
                            # create a new model with the given parameters
                            self.create_model(
                                input_dim=window_size * len(self.adp.indicator_list),
                                output_dim=3,
                                hidden_layers=[32, 16],
                                activation="relu",
                                dropout_rate=0.2,
                                learning_rate=0.01,
                            )

                            # train the model on historical data with the given parameters
                            self.train_model(
                                train_start_date=train_start_date,
                                train_end_date=train_end_date,
                                window_size=window_size,
                                batch_size=batch_size,
                                epochs=epochs,
                            )

                            # backtest the strategy on historical data with the given parameters
                            self.backtest_strategy(
                                test_start_date=train_start_date,
                                test_end_date=train_end_date,
                                window_size=window_size,
                            )

                            # calculate and print the performance metrics
                            sharpe_ratio = self.calculate_sharpe_ratio()

                            max_drawdown = self.calculate_max_drawdown()
                            profit_factor = self.calculate_profit_factor()
                            print(
                                f"Window Size: {window_size}, Batch Size: {batch_size}, Epochs: {epochs}"
                            )
                            print(
                                f"Sharpe Ratio: {sharpe_ratio}, Max Drawdown: {max_drawdown}, Profit Factor: {profit_factor}"
                            )

                            # append the parameters and metrics to the results list
                            results.append(
                                [
                                    window_size,
                                    batch_size,
                                    epochs,
                                    sharpe_ratio,
                                    max_drawdown,
                                    profit_factor,
                                ]
                            )

                            # convert the results list to a pandas DataFrame
                            results_df = pd.DataFrame(
                                results,
                                columns=[
                                    "Window Size",
                                    "Batch Size",
                                    "Epochs",
                                    "Sharpe Ratio",
                                    "Max Drawdown",
                                    "Profit Factor",
                                ],
                            )

                            # sort the results by Sharpe Ratio in descending order
                            results_df = results_df.sort_values(
                                by="Sharpe Ratio", ascending=False
                            )

                            # return the results DataFrame
                            return results_df

                            # define a method to evaluate the strategy on unseen data
                            def evaluate_strategy(
                                self, eval_start_date, eval_end_date, window_size
                            ):
                                # eval_start_date: the start date of the evaluation period as a string in YYYY-MM-DD format
                                # eval_end_date: the end date of the evaluation period as a string in YYYY-MM-DD format
                                # window_size: the number of previous days to use as input features

                                # load the model saved from the optimization
                                self.model = keras.models.load_model("model.h5")

                                # backtest the strategy on unseen data with the given parameters
                                self.backtest_strategy(
                                    test_start_date=eval_start_date,
                                    test_end_date=eval_end_date,
                                    window_size=window_size,
                                )

                                # calculate and print the performance metrics
                                sharpe_ratio = self.calculate_sharpe_ratio()
                                max_drawdown = self.calculate_max_drawdown()
                                profit_factor = self.calculate_profit_factor()
                                print(f"Window Size: {window_size}")
                                print(
                                    f"Sharpe Ratio: {sharpe_ratio}, Max Drawdown: {max_drawdown}, Profit Factor: {profit_factor}"
                                )

                            # define a method to calculate the Sharpe Ratio
                            def calculate_sharpe_ratio(self):
                                # calculate the annualized return
                                annualized_return = (
                                    (
                                        self.data["Cumulative_Strategy_Return"].iloc[-1]
                                        - 1
                                    )
                                    * 252
                                    / len(self.data)
                                )

                                # calculate the annualized volatility
                                annualized_volatility = self.data[
                                    "Strategy_Return"
                                ].std() * np.sqrt(252)

                                # calculate the risk-free rate (assuming 0% for simplicity)
                                risk_free_rate = 0

                                # calculate the Sharpe Ratio
                                sharpe_ratio = (
                                    annualized_return - risk_free_rate
                                ) / annualized_volatility

                                # return the Sharpe Ratio
                                return sharpe_ratio

                            # define a method to calculate the Maximum Drawdown
                            def calculate_max_drawdown(self):
                                # calculate the cumulative peak
                                cumulative_peak = self.data[
                                    "Cumulative_Strategy_Return"
                                ].cummax()

                                # calculate the cumulative drawdown
                                cumulative_drawdown = (
                                    1
                                    - self.data["Cumulative_Strategy_Return"]
                                    / cumulative_peak
                                )

                                # calculate the maximum drawdown
                                max_drawdown = cumulative_drawdown.max()

                                # return the maximum drawdown
                                return max_drawdown

                            # define a method to calculate the Profit Factor
                            def calculate_profit_factor(self):
                                # calculate the gross profit (sum of positive strategy returns)
                                gross_profit = self.data[
                                    self.data["Strategy_Return"] > 0
                                ]["Strategy_Return"].sum()

                                # calculate the gross loss (sum of negative strategy returns)
                                gross_loss = self.data[
                                    self.data["Strategy_Return"] < 0
                                ]["Strategy_Return"].sum()

                                # calculate the profit factor (ratio of gross profit to gross loss)
                                profit_factor = gross_profit / abs(gross_loss)

                                # return the profit factor
                                return profit_factor
