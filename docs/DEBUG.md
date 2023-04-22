debug.py - README.md

Overview

debug.py is a powerful interactive testing and debugging script that allows users to test and troubleshoot various components of the MarketMagician trading bot. It provides an easy-to-use interface for testing individual components, checking for issues, and validating the functionality of each component.

Prerequisites

Before using debug.py, ensure that all required dependencies are installed by running:

pip install -r requirements.txt


Additionally, make sure you have set up all the required accounts and API keys, as described in the main README.md file.

Usage

To use debug.py, simply run the script using Python:

python debug.py

This will launch an interactive menu where you can select the component you'd like to test. The available components are:

MarketDataCollector
DataStorageManager
AdvancedDataProcessor
StrategyCreator
SecurityManager
TradeManager
Example Usage Scenarios
Scenario 1: Testing the MarketDataCollector

Suppose you want to test the MarketDataCollector component to ensure that it can correctly fetch market data from various sources. To do this, run debug.py, then enter 1 when prompted to select a component:

python debug.py
Select a component to test:
1. MarketDataCollector
2. DataStorageManager
3. AdvancedDataProcessor
4. StrategyCreator
5. SecurityManager
6. TradeManager
7. Exit

Enter your choice: 1

The script will then run the test method for the MarketDataCollector component and log the results.

Scenario 2: Testing the TradeManager

If you want to test the TradeManager component to ensure that it can successfully execute trades and interact with various trading platforms, run debug.py and enter 6 when prompted:

python debug.py
Select a component to test:
1. MarketDataCollector
2. DataStorageManager
3. AdvancedDataProcessor
4. StrategyCreator
5. SecurityManager
6. TradeManager
7. Exit

Enter your choice: 6

The script will run the test method for the TradeManager component and log the results.

Customization

debug.py is designed to be customizable to suit your specific testing needs. If you want to add or modify test cases, edit the respective component's test method. To add more components to the testing menu, simply update the main_menu() function and add the corresponding logic in the main() function.

Logging

debug.py uses Python's built-in logging module to log test results and errors. By default, the log level is set to INFO, but you can change this by modifying the logging.basicConfig() call in the script. Logs are printed to the console, but you can also configure the logging module to save logs to a file if desired.

Limitations

debug.py does not cover every possible edge case or scenario, and it is up to the user to ensure that the components work as expected in their specific use cases. Additionally, the script is dependent on the accuracy of the mocked data and simulated API responses.
