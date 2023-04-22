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
