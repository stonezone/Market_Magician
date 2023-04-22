#!/bin/bash

# MarketMagician setup script

# Introduction
echo "Welcome to the MarketMagician setup script!"
echo "This script will guide you through the process of configuring your trading bot"
echo "with the required API keys, database credentials, and other necessary information."
echo "Please make sure you have all the required information before proceeding."
echo ""

# Prompt user for API keys
echo "Please enter your financial platform API key:"
read FINANCIAL_API_KEY
echo "Please enter your news source API key:"
read NEWS_API_KEY
echo "Please enter your alternative data source API key:"
read ALT_DATA_API_KEY
echo "Please enter your trading platform API key:"
read TRADING_API_KEY

# Prompt user for database credentials
echo "Please enter your database URL (e.g., 'postgresql://localhost/marketmagician'):"
read DATABASE_URL
echo "Please enter your database username:"
read DATABASE_USERNAME
echo "Please enter your database password:"
read DATABASE_PASSWORD

# Write the configuration to config.py
echo "Creating the config.py file..."
cat > config.py << EOF
# API keys
FINANCIAL_API_KEY = "${FINANCIAL_API_KEY}"
NEWS_API_KEY = "${NEWS_API_KEY}"
ALT_DATA_API_KEY = "${ALT_DATA_API_KEY}"
TRADING_API_KEY = "${TRADING_API_KEY}"

# Database configuration
DATABASE_URL = "${DATABASE_URL}"
DATABASE_USERNAME = "${DATABASE_USERNAME}"
DATABASE_PASSWORD = "${DATABASE_PASSWORD}"
EOF

echo "Configuration complete! You can now run 'python main.py' to start the trading bot."

# Exit script
exit 0
