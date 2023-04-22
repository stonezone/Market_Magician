# MarketDataCollector.py

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

# ... (Include other get_data_from_* functions as before)

def get_data_from_source(ticker: str, source: str) -> pd.DataFrame:
    # ... (Same as before)

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

                    # Normalize and merge data
                    data = normalize_data(data, source)
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
                    from DataStorageManager import DataStorageManager

                    data_storage_manager = DataStorageManager()
                    data_storage_manager.store(data)

                def apply_additional_data_processing(data: pd.DataFrame) -> pd.DataFrame:
                    """
                    Apply additional data processing steps to the merged data, if required.

                    Parameters:
                    data (pandas.DataFrame): A dataframe containing the merged data.

                    Returns:
                    pandas.DataFrame: A dataframe containing the processed data.
                    """
                    # Implement additional data processing steps here, e.g., adding technical indicators, etc.
                    # This function can also call other scripts or modules, such as the AdvancedDataProcessor, if needed.
                    pass

                if __name__ == "__main__":
                    tickers = ["AAPL", "GOOG", "MSFT"]
                    sources = ["yahoo", "alpha_vantage"]
                    data = get_data(tickers, sources)
                    print(data)
                
