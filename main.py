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
