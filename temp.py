from MarketDataCollector import get_data

if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL"]
    sources = ["yahoo"]
    #ssources = ["alpha_vantage", "yahoo"]
    data = get_data(tickers, sources)
    print(data)

