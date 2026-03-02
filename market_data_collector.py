import os
import yfinance as yf
import pandas as pd
from datetime import datetime
import config

def fetch_market_data(ticker, period="1y"):
    """
    Fetches historical OHLCV data using yfinance.
    """
    print(f"Fetching market data for {ticker} ({period})...")
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    
    if hist.empty:
        print(f"  -> Warning: No data found for {ticker}")
        return None
        
    # Reset index to make Date a column instead of index
    hist = hist.reset_index()
    hist['ticker'] = ticker
    
    # Rename columns for consistency
    hist = hist.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })
    
    # Drop columns we don't need (like Dividends, Stock Splits)
    cols_to_keep = ["date", "ticker", "open", "high", "low", "close", "volume"]
    hist = hist[cols_to_keep]
    
    return hist

def main():
    print("Starting market data collection...")
    all_dataframes = []
    
    for ticker in config.TARGET_TICKERS:
        try:
            df = fetch_market_data(ticker, period="1y")
            if df is not None:
                all_dataframes.append(df)
        except Exception as e:
            print(f"  -> Error fetching market data for {ticker}: {e}")
            
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Ensure raw data directory exists
        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(config.RAW_DATA_DIR, f"market_data_{timestamp_str}.csv")
        
        combined_df.to_csv(output_file, index=False)
        print(f"\nSuccessfully saved {len(combined_df)} market data rows to {output_file}")
    else:
        print("\nNo market data collected.")

if __name__ == "__main__":
    main()
