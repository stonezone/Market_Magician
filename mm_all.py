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
                    return signalsimport pymongo
from pymongo import MongoClient
import logging
import os
import shutil

class DataStorageManager:
    def __init__(self, database_name):
        self.database_name = database_name
        self.backup_path = "database_backup"
        self.logger = self.setup_logger()
        self.setup_backup_folder()

        try:
            self.client = MongoClient()
            self.db = self.client[self.database_name]
            self.logger.info(f"Connected to database: {self.database_name}")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {self.database_name}. Error: {e}")
            raise

    def setup_logger(self):
        logger = logging.getLogger("DataStorageManager")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Set up file handler for logging
        file_handler = logging.FileHandler("data_storage_manager.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Set up console handler for logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def setup_backup_folder(self):
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
            self.logger.info(f"Created backup folder at {self.backup_path}")

    def insert_data(self, collection_name, data):
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(data)
            self.logger.info(f"Inserted data into {collection_name}: {result.inserted_id}")
        except Exception as e:
            self.logger.error(f"Failed to insert data into {collection_name}. Error: {e}")
            raise

    def update_data(self, collection_name, query, new_data):
        try:
            collection = self.db[collection_name]
            result = collection.update_one(query, {"$set": new_data})
            self.logger.info(f"Updated data in {collection_name}: {result.modified_count} document(s) modified")
        except Exception as e:
            self.logger.error(f"Failed to update data in {collection_name}. Error: {e}")
            raise

    def query_data(self, collection_name, query, projection=None):
        try:
            collection = self.db[collection_name]
            result = collection.find(query, projection)
            self.logger.info(f"Queried data from {collection_name}: {result.count()} document(s) returned")
            return list(result)
        except Exception as e:
            self.logger.error(f"Failed to query data from {collection_name}. Error: {e}")
            raise
    def backup_database(self):
        backup_folder = os.path.join(self.backup_path, self.database_name)
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        try:
            os.system(f"mongodump --db {self.database_name} --out {self.backup_path}")
            self.logger.info(f"Successfully backed up {self.database_name} to {self.backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to backup database {self.database_name}. Error: {e}")
            raise
    def delete_data(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(query)
            self.logger.info(f"Deleted data from {collection_name}: {result.deleted_count} document(s) deleted")
        except Exception as e:
            self.logger.error(f"Failed to delete data from {collection_name}. Error: {e}")
            raise

    def restore_database(self):
        backup_folder = os.path.join(self.backup_path, self.database_name)
        if os.path.exists(backup_folder):
            try:
                os.system(f"mongorestore --db {self.database_name} {backup_folder}")
                self.logger.info(f"Successfully restored {self.database_name} from {self.backup_path}")
            except Exception as e:
                self.logger.error(f"Failed to restore database {self.database_name}. Error: {e}")
                self.logger.error(f"Failed to restore database {self.database_name}. Error: {e}")
            raise
        else:
            self.logger.error(f"Backup folder for {self.database_name} not found in {self.backup_path}")

    def drop_collection(self, collection_name):
        try:
            collection = self.db[collection_name]
            collection.drop()
            self.logger.info(f"Dropped collection {collection_name} from {self.database_name}")
        except Exception as e:
            self.logger.error(f"Failed to drop collection {collection_name} from {self.database_name}. Error: {e}")
            raise

if __name__ == "__main__":
    data_storage_manager = DataStorageManager("test_db")

    # Insert data
    data_storage_manager.insert_data("test_collection", {"symbol": "AAPL", "price": 100})

    # Update data
    data_storage_manager.update_data("test_collection", {"symbol": "AAPL"}, {"price": 101})

    # Query data
    data = data_storage_manager.query_data("test_collection", {"symbol": "AAPL"})
    print(data)

    # Delete data
    data_storage_manager.delete_data("test_collection", {"symbol": "AAPL"})

    # Backup database
    data_storage_manager.backup_database()

    # Restore database
    data_storage_manager.restore_database()

    # Drop collection
    data_storage_manager.drop_collection("test_collection")
                # MarketDataCollector.py

"""
MarketDataCollector.py

This module manages data collection from various sources. It is further divided
into sub-modules for each data source to improve modularity and maintainability.
It also provides a unified interface for accessing the data from any source.
"""

import logging
import time
import json
from io import StringIO
from typing import Optional, List
import pandas as pd
import yfinance as yf
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
try:
    from ratelimit import limits, sleep_and_retry
except ImportError:
    print("ratelimit module not found. Please install it using 'pip install ratelimiter'")


# Set up logging
logging.basicConfig(
    filename="market_data_collector.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

# Load the config file
with open("config.json", "r") as f:
    config = json.load(f)

# Define a custom exception class for data collection errors


class DataCollectionError(Exception):
    """An exception raised when data collection fails."""

    def __init__(self, message: str, source: str, ticker: str) -> None:
        """Initialize the exception with a message, a source, and a ticker."""
        super().__init__(message)
        self.source = source
        self.ticker = ticker
        # Apply a rate limit of 5 requests per minute


@sleep_and_retry
@limits(calls=5, period=60)
def limited_request(url: str, **kwargs) -> requests.Response:
    return requests.get(url, **kwargs)


@lru_cache(maxsize=None)
def get_data_from_alpha_vantage(ticker: str) -> pd.DataFrame:
    api_key = config["data_sources"]["alpha_vantage"]["api_key"]
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "outputsize": "full",
        "apikey": api_key,
        "datatype": "json",
    }
    response = limited_request(base_url, params=params)

    if response.status_code != 200:
        raise DataCollectionError("Failed to fetch data from Alpha Vantage", "alpha_vantage", ticker)

    data = response.json()
    if "Error Message" in data:
        raise DataCollectionError(data["Error Message"], "alpha_vantage", ticker)

    df = pd.DataFrame(data["Time Series (Daily)"]).T
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns=lambda x: x.strip().replace(" ", "_").lower())

    return df


@lru_cache(maxsize=None)
def get_data_from_yahoo(ticker: str) -> pd.DataFrame:
    stock_data = yf.download(ticker, start="1900-01-01")

    if stock_data.empty:
        raise DataCollectionError("Failed to fetch data from Yahoo Finance", "yahoo", ticker)

    return stock_data



def normalize_data(data: pd.DataFrame, source: str) -> pd.DataFrame:
    # Rename columns based on the source
    if source == "yahoo":
        column_mapping = {"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
    elif source == "alpha_vantage":
        column_mapping = {
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. adjusted close": "adjusted_close",
            "6. volume": "volume",
            "7. dividend amount": "dividend_amount",
            "8. split coefficient": "split_coefficient",
        }
    else:
        raise NotImplementedError(f"Column normalization not implemented for source: {source}")

    data = data.rename(columns=column_mapping)

    # Add a print statement to check the data after renaming columns
    print(f"Data after renaming columns ({source}):", data)

    # Drop unnecessary columns
    # ...

    return data



def get_data_from_source(ticker: str, source: str) -> pd.DataFrame:
    if source == "alpha_vantage":
        return get_data_from_alpha_vantage(ticker)
    elif source == "yahoo":
        return get_data_from_yahoo(ticker)
    else:
        raise ValueError(f"Invalid or unsupported source: {source}")


def get_data(tickers: List[str], sources: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Get historical stock data from multiple sources and merge them into one dataframe.

    Parameters:
    tickers (list[str]): A list of stock symbols to query.
    sources (list[str]): A list of data sources to use. If None, use all available sources.

    Returns:
    pandas.DataFrame: A dataframe containing the historical stock data from all sources.

    Raises:
    ValueError: If the sources list is empty or contains invalid sources.
    """
    logger.info(f"Getting data from multiple sources for {tickers}")
    # Define the default list of sources
    default_sources = list(config["data_sources"].keys())
    # Validate the sources list
    if sources is None:
        # Use all available sources
        sources = default_sources
    elif not sources:
        # Raise an error if the list is empty
        logger.error(f"No sources specified")
        raise ValueError(f"No sources specified")
    else:
        # Check if the list contains valid sources
        for source in sources:
            if source not in default_sources:
                logger.error(f"Invalid or unsupported source: {source}")
                raise ValueError(f"Invalid or unsupported source: {source}")

    # Initialize an empty dataframe to store the merged data
    merged_data = pd.DataFrame()

    # Loop through the tickers
    for ticker in tickers:
        # Fetch data for each ticker using ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(get_data_from_source, ticker, source): source for source in sources}

            for future in as_completed(futures):
                try:
                    source = futures[future]
                    data = future.result()

                    # Add a print statement to check the data before normalization
                    print(f"Data before normalization ({ticker}, {source}):", data)

                    # Normalize and merge data
                    data = normalize_data(data, source)
                    
                    # Add a print statement to check the data after normalization
                    print(f"Data after normalization ({ticker}, {source}):", data)

                    merged_data = merged_data.join(data, how="outer")
                except DataCollectionError as e:
                    logger.warning(f"Failed to get data from {e.source} for {e.ticker}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")

    # Sort the merged data by date
    merged_data.sort_index(inplace=True)

    # Apply additional data processing steps if required
    if config.get("additional_data_processing"):
        merged_data = apply_additional_data_processing(merged_data)

    # Store the merged data in the DataStorageManager
    store_data(merged_data)
    logger.info(f"Successfully collected data for {tickers}")

    return merged_data
def store_data(data: pd.DataFrame) -> None:
                        """
    Store the collected data in the DataStorageManager.

    Parameters:
    data (pandas.DataFrame): A dataframe containing the collected data.

    Returns:
    None
    """
    # Implement the logic to store the data using your preferred DataStorageManager.
pass


def apply_additional_data_processing(data: pd.DataFrame) -> pd.DataFrame:
    """
    Apply additional data processing steps to the collected data.

    Parameters:
    data (pandas.DataFrame): A dataframe containing the collected data.

    Returns:
    pandas.DataFrame: A dataframe containing the processed data.
    """
    # Implement the logic to apply additional data processing steps.
    pass


if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL"]
    sources = ["alpha_vantage", "yahoo"]
    data = get_data(tickers, sources)
    print(data)# SecurityManager.py

import sqlite3
import logging
import os
import smtplib
import email.message
from cryptography.fernet import Fernet
from hashlib import pbkdf2_hmac
from base64 import b64encode, b64decode
import secrets

DB_NAME = "security_manager.db"
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587

# Configure logging
logging.basicConfig(filename="security_manager.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def generate_salt():
    return secrets.token_bytes(16)

def hash_password(password, salt):
    password_hash = pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt, b64encode(password_hash)

def verify_password(password, salt, password_hash):
    salt = b64decode(salt)
    stored_hash = b64decode(password_hash)
    password_hash = pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return password_hash == stored_hash

def generate_token():
    return secrets.randbelow(1000000)

def register_user(username, password, email):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            raise Exception("User already exists")
        else:
            salt, password_hash = hash_password(password, generate_salt())
            token = generate_token()
            cursor.execute("INSERT INTO users (username, salt, password, token, email, timestamp, role) VALUES (?, ?, ?, ?, ?, datetime('now'), 'user')", (username, salt, password_hash, token, email))
            conn.commit()
            return token

def authenticate_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            salt = user[1]
            password_hash = user[2]
            if verify_password(password, salt, password_hash):
                return user[4], user[6]  # Return email and role
            else:
                raise Exception("Wrong password")
        else:
            raise Exception("User not found")

def revoke_or_renew_token(username, password, action):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            salt = user[1]
            password_hash = user[2]
            if verify_password(password, salt, password_hash):
                if action == "revoke":
                    cursor.execute("UPDATE users SET token = 0 WHERE username = ?", (username,))
                    conn.commit()
                    return "Token revoked successfully"
                elif action == "renew":
                    new_token = generate_token()
                    cursor.execute("UPDATE users SET token = ?, timestamp = datetime('now') WHERE username = ?", (new_token, username))
                    conn.commit()
                    return new_token
                else:
                    raise Exception("Invalid action")
            else:
                raise Exception("Wrong password")
        else:
            raise Exception("User not found")

def change_password(username, old_password, new_password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            old_salt = user[1]
            old_password_hash = user[2]
            if verify_password(old_password, old_salt, old_password_hash):
                new_salt, new_password_hash = hash_password(new_password)
                cursor.execute("UPDATE users SET salt = ?, password = ?, timestamp = datetime('now') WHERE username = ?", (new_salt, new_password_hash, username))
                conn.commit()
                return "Password changed successfully"
            else:
                raise Exception("Wrong old password")
        else:
            raise Exception("User not found")

def reset_password(username, reset_code, new_password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            with open("reset_codes.txt", "r") as f:
                for line in f:
                    user_code, stored_reset_code = line.split()
                    if user_code == username and reset_code == stored_reset_code:
                        salt, password_hash = hash_password(new_password)
                        cursor.execute("UPDATE users SET salt = ?, password = ?, timestamp = datetime('now') WHERE username = ?", (salt, password_hash, username))
                        conn.commit()
                        return "Password reset successfully"
                else:
                    raise Exception("Invalid reset code")
        else:
            raise Exception("User not found")

def delete_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            salt = user[1]
            password_hash = user[2]
            if verify_password(password, salt, password_hash):
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                return "User deleted successfully"
            else:
                raise Exception("Wrong password")
        else:
            raise Exception("User not found")

def assign_role(username, role):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
            conn.commit()
            return "Role assigned successfully"
        else:
            raise Exception("User not found")

def encrypt_data(data, key):
    fernet = Fernet(key)
    data_bytes = data.encode()
    encrypted_data = fernet.encrypt(data_bytes)
    return encrypted_data

def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    data_bytes = fernet.decrypt(encrypted_data)
    data = data_bytes.decode()
    return data

def audit_action(username, action, status):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit (username, action, status, timestamp) VALUES (?, ?, ?, datetime('now'))", (username, action, status))
        conn.commit()
        logging.info(f"{username} {action} {status}")

def notify_event(username, event, email):
    message = email.message.EmailMessage()
    message["Subject"] = "Security Event Notification"
    message["From"] = EMAIL_USER
    message["To"] = email
    message.set_content(f"Hello {username},\n\nWe detected a security event on your account. The event details are as follows:\n\n{event}\n\nIf you recognize this event, please ignore this email. Otherwise, please take the following actions to secure your account:\n\n- Change your password immediately.\n- Revoke or renew your token.\n- Contact the administrator for further assistance.\n\nThank you,\nSecurityManager.py Team")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(message)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt BLOB NOT NULL, password BLOB NOT NULL, token INTEGER NOT NULL, email TEXT NOT NULL, timestamp INTEGER NOT NULL, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, username TEXT NOT NULL, action TEXT NOT NULL, status TEXT NOT NULL, timestamp INTEGER NOT NULL)")

    conn.close()
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
    def create_model(self, input_dim, output_dim, hidden_layers, activation, dropout_rate, learning_rate):
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
            Dense(hidden_layers[0], input_dim=input_dim, activation=activation))

        # add dropout layer if dropout_rate is positive
        if dropout_rate > 0:
            self.model.add(Dropout(dropout_rate))

        # add the remaining hidden layers with dropout layers if needed
        for i in range(1, len(hidden_layers)):
            self.model.add(Dense(hidden_layers[i], activation=activation))
            if dropout_rate > 0:
                self.model.add(Dropout(dropout_rate))

        # add the output layer with softmax activation
        self.model.add(Dense(output_dim, activation='softmax'))

        # compile the model with Adam optimizer and categorical crossentropy loss
        self.model.compile(optimizer=Adam(learning_rate=learning_rate),
                           loss='categorical_crossentropy', metrics=['accuracy'])

    # define a method to train the machine learning model on historical data
    def train_model(self, train_start_date, train_end_date, window_size, batch_size, epochs):
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
            X.append(indicators_scaled[i-window_size:i])

            # get the price change for the next day as output label (1 for positive change, 0 for negative change or no change)
            price_change = train_data['Close'].iloc[i] - \
                train_data['Close'].iloc[i-1]
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
        self.model.save('model.h5')
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
                X.append(indicators_scaled[i-window_size:i])

                # get the price change for the next day as output label (1 for positive change, 0 for negative change or no change)
                price_change = test_data['Close'].iloc[i] - \
                    test_data['Close'].iloc[i-1]
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
            self.model = keras.models.load_model('model.h5')
            #
            # predict the output labels for X using the model
            y_pred = self.model.predict(X)
            # get the predicted signals as a list of integers (0 for buy, 1 for sell, or 2 for hold)
            signals = np.argmax(y_pred, axis=1)

            # create a new column in the test data to store the signals
            test_data['Signal'] = signals

            # create a new column in the test data to store the positions (1 for long, -1 for short, or 0 for flat)
            test_data['Position'] = test_data['Signal'].diff()

            # create a new column in the test data to store the returns (percentage change in price)
            test_data['Return'] = test_data['Close'].pct_change()

            # create a new column in the test data to store the strategy returns (returns multiplied by positions)
            test_data['Strategy_Return'] = test_data['Return'] * \
                test_data['Position']

            # create a new column in the test data to store the cumulative returns
            test_data['Cumulative_Return'] = (
                test_data['Return'] + 1).cumprod()

            # create a new column in the test data to store the cumulative strategy returns
            test_data['Cumulative_Strategy_Return'] = (
                test_data['Strategy_Return'] + 1).cumprod()

            # plot the cumulative returns and cumulative strategy returns
            plt.figure(figsize=(12, 8))
            plt.plot(test_data['Cumulative_Return'], label='Buy and Hold')
            plt.plot(test_data['Cumulative_Strategy_Return'],
                     label='Machine Learning Strategy')
            plt.title('Backtesting Results')
            plt.xlabel('Date')
            plt.ylabel('Cumulative Return')
            plt.legend()
            plt.show()

            # define a method to optimize the strategy parameters using grid search
            def optimize_strategy(self, train_start_date, train_end_date, window_size_range, batch_size_range, epochs_range):
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
                            self.create_model(input_dim=window_size*len(self.adp.indicator_list), output_dim=3,
                                              hidden_layers=[32, 16], activation='relu', dropout_rate=0.2,
                                              learning_rate=0.01)

                            # train the model on historical data with the given parameters
                            self.train_model(train_start_date=train_start_date,
                                             train_end_date=train_end_date,
                                             window_size=window_size,
                                             batch_size=batch_size,
                                             epochs=epochs)

                            # backtest the strategy on historical data with the given parameters
                            self.backtest_strategy(test_start_date=train_start_date,
                                                   test_end_date=train_end_date,
                                                   window_size=window_size)

                            # calculate and print the performance metrics
                            sharpe_ratio = self.calculate_sharpe_ratio()

                            max_drawdown = self.calculate_max_drawdown()
                            profit_factor = self.calculate_profit_factor()
                            print(
                                f'Window Size: {window_size}, Batch Size: {batch_size}, Epochs: {epochs}')
                            print(
                                f'Sharpe Ratio: {sharpe_ratio}, Max Drawdown: {max_drawdown}, Profit Factor: {profit_factor}')

                            # append the parameters and metrics to the results list
                            results.append(
                                [window_size, batch_size, epochs, sharpe_ratio, max_drawdown, profit_factor])

                            # convert the results list to a pandas DataFrame
                            results_df = pd.DataFrame(results, columns=[
                                                      'Window Size', 'Batch Size', 'Epochs', 'Sharpe Ratio', 'Max Drawdown', 'Profit Factor'])

                            # sort the results by Sharpe Ratio in descending order
                            results_df = results_df.sort_values(
                                by='Sharpe Ratio', ascending=False)

                            # return the results DataFrame
                            return results_df

                            # define a method to evaluate the strategy on unseen data
                            def evaluate_strategy(self, eval_start_date, eval_end_date, window_size):
                                # eval_start_date: the start date of the evaluation period as a string in YYYY-MM-DD format
                                # eval_end_date: the end date of the evaluation period as a string in YYYY-MM-DD format
                                # window_size: the number of previous days to use as input features

                                # load the model saved from the optimization
                                self.model = keras.models.load_model(
                                    'model.h5')

                                # backtest the strategy on unseen data with the given parameters
                                self.backtest_strategy(test_start_date=eval_start_date,
                                                       test_end_date=eval_end_date,
                                                       window_size=window_size)

                                # calculate and print the performance metrics
                                sharpe_ratio = self.calculate_sharpe_ratio()
                                max_drawdown = self.calculate_max_drawdown()
                                profit_factor = self.calculate_profit_factor()
                                print(f'Window Size: {window_size}')
                                print(
                                    f'Sharpe Ratio: {sharpe_ratio}, Max Drawdown: {max_drawdown}, Profit Factor: {profit_factor}')

                            # define a method to calculate the Sharpe Ratio
                            def calculate_sharpe_ratio(self):
                                # calculate the annualized return
                                annualized_return = (
                                    self.data['Cumulative_Strategy_Return'].iloc[-1] - 1) * 252 / len(self.data)

                                # calculate the annualized volatility
                                annualized_volatility = self.data['Strategy_Return'].std(
                                ) * np.sqrt(252)

                                # calculate the risk-free rate (assuming 0% for simplicity)
                                risk_free_rate = 0

                                # calculate the Sharpe Ratio
                                sharpe_ratio = (
                                    annualized_return - risk_free_rate) / annualized_volatility

                                # return the Sharpe Ratio
                                return sharpe_ratio

                            # define a method to calculate the Maximum Drawdown
                            def calculate_max_drawdown(self):
                                # calculate the cumulative peak
                                cumulative_peak = self.data['Cumulative_Strategy_Return'].cummax(
                                )

                                # calculate the cumulative drawdown
                                cumulative_drawdown = 1 - \
                                    self.data['Cumulative_Strategy_Return'] / \
                                    cumulative_peak

                                # calculate the maximum drawdown
                                max_drawdown = cumulative_drawdown.max()

                                # return the maximum drawdown
                                return max_drawdown

                            # define a method to calculate the Profit Factor
                            def calculate_profit_factor(self):
                                # calculate the gross profit (sum of positive strategy returns)
                                gross_profit = self.data[self.data['Strategy_Return'] > 0]['Strategy_Return'].sum(
                                )

                                # calculate the gross loss (sum of negative strategy returns)
                                gross_loss = self.data[self.data['Strategy_Return'] < 0]['Strategy_Return'].sum(
                                )

                                # calculate the profit factor (ratio of gross profit to gross loss)
                                profit_factor = gross_profit / abs(gross_loss)

                                # return the profit factor
                                return profit_factor
[part 1 of 9] # import needed libraries
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
    def create_model(self, input_dim, output_dim, hidden_layers, activation, dropout_rate, learning_rate):
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
            Dense(hidden_layers[0], input_dim=input_dim, activation=activation))

        # add dropout layer if dropout_rate is positive
        if dropout_rate > 0:
            self.model.add(Dropout(dropout_rate))

        # add the remaining hidden layers with dropout layers if needed
        for i in range(1, len(hidden_layers)):
            self.model.add(Dense(hidden_laye
[part 2 of 9] rs[i], activation=activation))
            if dropout_rate > 0:
                self.model.add(Dropout(dropout_rate))

        # add the output layer with softmax activation
        self.model.add(Dense(output_dim, activation='softmax'))

        # compile the model with Adam optimizer and categorical crossentropy loss
        self.model.compile(optimizer=Adam(learning_rate=learning_rate),
                           loss='categorical_crossentropy', metrics=['accuracy'])

    # define a method to train the machine learning model on historical data
    def train_model(self, train_start_date, train_end_date, window_size, batch_size, epochs):
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
            X.append(indicators_scaled[i-window_size:i])

            # get the price change for the next day as output label (1 for positive change, 0 for negative change or no change)
            price_change = train_data['Close'].iloc[i] - 
[part 3 of 9] \
                train_data['Close'].iloc[i-1]
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
        self.model.save('model.h5')
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
                X.append(indicators_scaled[i-window_size:i])

                # get the price change for the next day as output label (1 for positive change, 0 for negative change or no change)
 
[part 4 of 9]                price_change = test_data['Close'].iloc[i] - \
                    test_data['Close'].iloc[i-1]
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
            self.model = keras.models.load_model('model.h5')
            #
            # predict the output labels for X using the model
            y_pred = self.model.predict(X)
            # get the predicted signals as a list of integers (0 for buy, 1 for sell, or 2 for hold)
            signals = np.argmax(y_pred, axis=1)

            # create a new column in the test data to store the signals
            test_data['Signal'] = signals

            # create a new column in the test data to store the positions (1 for long, -1 for short, or 0 for flat)
            test_data['Position'] = test_data['Signal'].diff()

            # create a new column in the test data to store the returns (percentage change in price)
            test_data['Return'] = test_data['Close'].pct_change()

            # create a new column in the test data to store the strategy returns (returns multiplied by positions)
            test_data['Strategy_Return'] = test_data['Return'] * \
                test_data['Position']

            # create a new column in the test data to store the cumulative returns
            test_data['Cumulative_Return'] = (
                test_data['Return'] + 1).cumprod()

            # create a new column in the test data to store the cumulative strategy returns
            test_data['Cumulative_Strategy_Return'] = (
                test_data['Strategy_Return'] + 1).cumprod()

            # plot the cumulative returns and cumulative strategy returns
            plt.figure(figsize=
[part 5 of 9] (12, 8))
            plt.plot(test_data['Cumulative_Return'], label='Buy and Hold')
            plt.plot(test_data['Cumulative_Strategy_Return'],
                     label='Machine Learning Strategy')
            plt.title('Backtesting Results')
            plt.xlabel('Date')
            plt.ylabel('Cumulative Return')
            plt.legend()
            plt.show()

            # define a method to optimize the strategy parameters using grid search
            def optimize_strategy(self, train_start_date, train_end_date, window_size_range, batch_size_range, epochs_range):
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
                            self.create_model(input_dim=window_size*len(self.adp.indicator_list), output_dim=3,
                                              hidden_layers=[32, 16], activation='relu', dropout_rate=0.2,
                                              learning_rate=0.01)

                            # train the model on historical data with the given parameters
                            self.train_model(train_start_date=train_start_date,
                                             train_end_date=train_end_date,
                       
[part 6 of 9]                       window_size=window_size,
                                             batch_size=batch_size,
                                             epochs=epochs)

                            # backtest the strategy on historical data with the given parameters
                            self.backtest_strategy(test_start_date=train_start_date,
                                                   test_end_date=train_end_date,
                                                   window_size=window_size)

                            # calculate and print the performance metrics
                            sharpe_ratio = self.calculate_sharpe_ratio()

                            max_drawdown = self.calculate_max_drawdown()
                            profit_factor = self.calculate_profit_factor()
                            print(
                                f'Window Size: {window_size}, Batch Size: {batch_size}, Epochs: {epochs}')
                            print(
                                f'Sharpe Ratio: {sharpe_ratio}, Max Drawdown: {max_drawdown}, Profit Factor: {profit_factor}')

                            # append the parameters and metrics to the results list
                            results.append(
                                [window_size, batch_size, epochs, sharpe_ratio, max_drawdown, profit_factor])

                            # convert the results list to a pandas DataFrame
                            results_df = pd.DataFrame(results, columns=[
                                                      'Window Size', 'Batch Size', 'Epochs', 'Sharpe Ratio', 'Max Drawdown', 'Profit Factor'])

                            # sort the results by Sharpe Ratio in descending order
                            results_df = results_df.sort_values(
                                by='Sharpe Ratio', ascending=False)

                            # return the results DataFrame
                            return results_df

                            # define a method to evaluate th
[part 7 of 9] e strategy on unseen data
                            def evaluate_strategy(self, eval_start_date, eval_end_date, window_size):
                                # eval_start_date: the start date of the evaluation period as a string in YYYY-MM-DD format
                                # eval_end_date: the end date of the evaluation period as a string in YYYY-MM-DD format
                                # window_size: the number of previous days to use as input features

                                # load the model saved from the optimization
                                self.model = keras.models.load_model(
                                    'model.h5')

                                # backtest the strategy on unseen data with the given parameters
                                self.backtest_strategy(test_start_date=eval_start_date,
                                                       test_end_date=eval_end_date,
                                                       window_size=window_size)

                                # calculate and print the performance metrics
                                sharpe_ratio = self.calculate_sharpe_ratio()
                                max_drawdown = self.calculate_max_drawdown()
                                profit_factor = self.calculate_profit_factor()
                                print(f'Window Size: {window_size}')
                                print(
                                    f'Sharpe Ratio: {sharpe_ratio}, Max Drawdown: {max_drawdown}, Profit Factor: {profit_factor}')

                            # define a method to calculate the Sharpe Ratio
                            def calculate_sharpe_ratio(self):
                                # calculate the annualized return
                                annualized_return = (
                                    self.data['Cumulative_Strategy_Return'].iloc[-1] - 1) * 252 / len(self.data)

                                # calculate the annualized volatility
                     
[part 8 of 9]            annualized_volatility = self.data['Strategy_Return'].std(
                                ) * np.sqrt(252)

                                # calculate the risk-free rate (assuming 0% for simplicity)
                                risk_free_rate = 0

                                # calculate the Sharpe Ratio
                                sharpe_ratio = (
                                    annualized_return - risk_free_rate) / annualized_volatility

                                # return the Sharpe Ratio
                                return sharpe_ratio

                            # define a method to calculate the Maximum Drawdown
                            def calculate_max_drawdown(self):
                                # calculate the cumulative peak
                                cumulative_peak = self.data['Cumulative_Strategy_Return'].cummax(
                                )

                                # calculate the cumulative drawdown
                                cumulative_drawdown = 1 - \
                                    self.data['Cumulative_Strategy_Return'] / \
                                    cumulative_peak

                                # calculate the maximum drawdown
                                max_drawdown = cumulative_drawdown.max()

                                # return the maximum drawdown
                                return max_drawdown

                            # define a method to calculate the Profit Factor
                            def calculate_profit_factor(self):
                                # calculate the gross profit (sum of positive strategy returns)
                                gross_profit = self.data[self.data['Strategy_Return'] > 0]['Strategy_Return'].sum(
                                )

                                # calculate the gross loss (sum of negative strategy returns)
                                gross_loss = self.data[self.data['Strategy_Return'] < 0]['Strategy_Return'].sum(
     
[part 9 of 9]                            )

                                # calculate the profit factor (ratio of gross profit to gross loss)
                                profit_factor = gross_profit / abs(gross_loss)

                                # return the profit factor
                                return profit_factor

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
        # config.py

# API keys and other sensitive information can be stored in environment variables or a separate .env file.
# For demonstration purposes, placeholders are used here.

# MarketDataCollector settings
API_KEY_FINANCIAL_PLATFORM = 'your_financial_platform_api_key'
API_KEY_NEWS_SOURCE = 'your_news_source_api_key'
API_KEY_ALTERNATIVE_DATA = 'your_alternative_data_api_key'

# DataStorageManager settings
DATABASE_URL = 'your_database_url'
DATABASE_USERNAME = 'your_database_username'
DATABASE_PASSWORD = 'your_database_password'

# AdvancedDataProcessor settings
ML_MODEL_PATH = 'path/to/your/machine_learning_model'

# StrategyCreator settings
RISK_PROFILE = 'conservative'  # Options: 'conservative', 'moderate', 'aggressive'

# SecurityManager settings
SECRET_KEY = 'your_secret_key'

# TradeManager settings
TRADING_PLATFORM_API_KEY = 'your_trading_platform_api_key'
TRADING_PLATFORM_SECRET_KEY = 'your_trading_platform_secret_key'
# debug.py

import MarketDataCollector
import DataStorageManager
import AdvancedDataProcessor
import StrategyCreator
import SecurityManager
import TradeManager

from unittest.mock import MagicMock
import logging
import os
import sys

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mock the components' test methods
MarketDataCollector.test = MagicMock()
DataStorageManager.test = MagicMock()
AdvancedDataProcessor.test = MagicMock()
StrategyCreator.test = MagicMock()
SecurityManager.test = MagicMock()
TradeManager.test = MagicMock()

def main_menu():
    print("Select a component to test:")
    print("1. MarketDataCollector")
    print("2. DataStorageManager")
    print("3. AdvancedDataProcessor")
    print("4. StrategyCreator")
    print("5. SecurityManager")
    print("6. TradeManager")
    print("7. Exit")

def get_input():
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if choice in range(1, 8):
                return choice
            else:
                raise ValueError
        except ValueError:
            print("Invalid choice. Please enter a number between 1 and 7.")

def test_component(component):
    try:
        component.test()
    except Exception as e:
        logging.error(f"Error testing component: {e}")
    else:
        logging.info("Component tested successfully.")

def main():
    while True:
        main_menu()
        choice = get_input()

        if choice == 1:
            test_component(MarketDataCollector)
        elif choice == 2:
            test_component(DataStorageManager)
        elif choice == 3:
            test_component(AdvancedDataProcessor)
        elif choice == 4:
            test_component(StrategyCreator)
        elif choice == 5:
            test_component(SecurityManager)
        elif choice == 6:
            test_component(TradeManager)
        elif choice == 7:
            print("Exiting...")
            sys.exit()

if __name__ == "__main__":
    main()
# main.py

import MarketDataCollector
import DataStorageManager
import AdvancedDataProcessor
import StrategyCreator
import SecurityManager
import TradeManager
import config

def main():
    # Initialize components
    market_data_collector = MarketDataCollector.MarketDataCollector(config)
    data_storage_manager = DataStorageManager.DataStorageManager(config)
    advanced_data_processor = AdvancedDataProcessor.AdvancedDataProcessor(config)
    strategy_creator = StrategyCreator.StrategyCreator(config)
    security_manager = SecurityManager.SecurityManager(config)
    trade_manager = TradeManager.TradeManager(config)

    # Collect market data
    market_data = market_data_collector.collect_data()

    # Store collected data
    data_storage_manager.store_data(market_data)

    # Process and analyze data
    processed_data = advanced_data_processor.process_data(market_data)

    # Create trading strategies
    strategies = strategy_creator.create_strategies(processed_data)

    # Execute trades based on strategies
    trade_manager.execute_trades(strategies)

if __name__ == "__main__":
    main()
import pandas as pd
from MarketDataCollector import get_data

def test_get_data():
    tickers = ["AAPL", "GOOG"]
    sources = ["yahoo", "alpha_vantage"]
    data = get_data(tickers, sources)

    print("Data type:", type(data))  # Add this print statement
    print("Data content:", data)  # Add this print statement

    assert isinstance(data, pd.DataFrame), "Expected data to be a pandas DataFrame"
    assert not data.empty, "Expected data to be non-empty"

    assert data.shape[1] == len(tickers) * len(sources), "Expected data to have columns for all tickers and sources"

    print("All tests passed.")


if __name__ == "__main__":
    test_get_data()

