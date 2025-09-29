#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sys

def setup_api_keys():
    """
    Interactive script to set up API keys for financial data providers
    """
    print("Financial Analytics Hub API Key Setup")
    print("=====================================")
    print("\nThis script will help you set up API keys for various financial data providers.")
    print("You can get free API keys from the following sources:")
    print("\n1. Alpha Vantage: https://www.alphavantage.co/support/#api-key")
    print("2. Twelve Data: https://twelvedata.com/")
    print("3. Polygon.io: https://polygon.io/")
    print("4. Finnhub: https://finnhub.io/")
    print("5. IEX Cloud: https://iexcloud.io/")
    print("6. MarketStack: https://marketstack.com/")
    print("7. CoinGecko: https://www.coingecko.com/en/api")
    print("8. Financial Modeling Prep: https://financialmodelingprep.com/developer")
    print("9. Trading Economics: https://tradingeconomics.com/api/")
    
    # Load existing .env file if it exists
    load_dotenv()
    
    # Dictionary to store API keys
    api_keys = {}
    
    # Get API keys
    providers = {
        "ALPHA_VANTAGE_API_KEY": "Alpha Vantage",
        "TWELVE_DATA_API_KEY": "Twelve Data",
        "POLYGON_API_KEY": "Polygon.io",
        "FINNHUB_API_KEY": "Finnhub",
        "IEX_CLOUD_API_KEY": "IEX Cloud",
        "MARKETSTACK_API_KEY": "MarketStack",
        "COINGECKO_API_KEY": "CoinGecko",
        "FMP_API_KEY": "Financial Modeling Prep",
        "TRADING_ECONOMICS_API_KEY": "Trading Economics"
    }
    
    for key, provider in providers.items():
        current_key = os.getenv(key, "")
        if current_key and current_key != "demo":
            print(f"\nCurrent {provider} API key: {current_key[:4]}...{current_key[-4:]}")
            change = input("Would you like to change this key? (y/N): ").lower()
            if change != 'y':
                api_keys[key] = current_key
                continue
        
        new_key = input(f"\nEnter your {provider} API key: ").strip()
        if new_key:
            api_keys[key] = new_key
    
    # Write to .env file
    with open(".env", "w") as f:
        f.write("# Financial Analytics Hub API Keys\n\n")
        for key, value in api_keys.items():
            f.write(f"{key}={value}\n")
        f.write("\n# Cache Settings\n")
        f.write("CACHE_EXPIRY=300  # 5 minutes in seconds\n")
    
    print("\nAPI keys have been saved to .env file.")
    print("You can now start the Financial Analytics Hub with real-time data!")

if __name__ == "__main__":
    try:
        setup_api_keys()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        sys.exit(1) 