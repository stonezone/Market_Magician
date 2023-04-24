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

