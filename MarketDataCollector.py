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
    base_url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
    params = {
        "period1": "0",
        "period2": str(int(time.time())),
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true",
    }
    response = limited_request(base_url, params=params)

    if response.status_code != 200:
        raise DataCollectionError("Failed to fetch data from Yahoo Finance", "yahoo", ticker)

    data = response.text
    df = pd.read_csv(StringIO(data), index_col="Date", parse_dates=True)

    return df


def normalize_data(data: pd.DataFrame, source: str) -> pd.DataFrame:
    """
    Normalize the data according to the data source.

    Parameters:
    data (pandas.DataFrame): A dataframe containing the raw data.
    source (str): The data source name.

    Returns:
    pandas.DataFrame: A dataframe containing the normalized data.
    """
    # Implement data normalization steps based on the source
    pass


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
            futures = {executor.submit(
                get_data_from_source, ticker, source): source for source in sources}

            for future in as_completed(futures):
                try:
                    source = futures[future]
                    data = future.result()

                    # Normalize and merge data
                    data = normalize_data(data, source)
                    merged_data = merged_data.join(data, how="outer")
                except DataCollectionError as e:
                    logger.warning(
                        f"Failed to get data from {e.source} for {e.ticker}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    # Sort the merged data by date
                    merged_data.sort_index(inplace=True)
                    # Apply additional data processing steps if required
                    if config.get("additional_data_processing"):

                        merged_data = apply_additional_data_processing(
                            merged_data)
                        # Store the merged data in the DataStorageManager
                        store_data(merged_data)
                        logger.info(
                            f"Successfully collected data for {tickers}")
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
    print(data)


