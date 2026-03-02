import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import os
import pandas as pd
import glob
from datetime import datetime
import config

def get_latest_file(pattern):
    """Finds the most recent file matching a given pattern."""
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def clean_news_data():
    """
    Loads raw news data (from Reddit, RSS, API), cleans it, standardizes timestamps,
    and saves to the cleaned/ directory.
    """
    print("Preprocessing News Data...")
    
    # We will combine broad news, specific API news, and Reddit API news into one dataset
    dfs = []
    
    # 1. Reddit News
    reddit_file = get_latest_file(os.path.join(config.RAW_DATA_DIR, "news_reddit_*.csv"))
    if reddit_file:
        df_reddit = pd.read_csv(reddit_file)
        # Convert timestamp to Pandas datetime, timezone aware if possible, then to UTC
        df_reddit['timestamp'] = pd.to_datetime(df_reddit['timestamp'], utc=True)
        dfs.append(df_reddit)
        
    # 2. Broad RSS News
    broad_file = get_latest_file(os.path.join(config.RAW_DATA_DIR, "news_broad_data_*.csv"))
    if broad_file:
        df_broad = pd.read_csv(broad_file)
        df_broad['timestamp'] = pd.to_datetime(df_broad['timestamp'], utc=True, format="mixed")
        dfs.append(df_broad)
        
    if not dfs:
        print("No raw news data found to preprocess.")
        return None
        
    # Combine all news
    df_combined = pd.concat(dfs, ignore_index=True)
    
    # Drop items with missing critical data
    df_combined.dropna(subset=['headline_text', 'timestamp'], inplace=True)
    
    # Deduplicate strictly based on headline to avoid double counting
    df_combined.drop_duplicates(subset=['headline_text'], inplace=True)
    
    # Clean text (remove extra spaces, newlines, etc.)
    df_combined['clean_text'] = df_combined['headline_text'].str.replace(r'\n|\r', ' ', regex=True)
    df_combined['clean_text'] = df_combined['clean_text'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # Keep only relevant columns for the ML model
    cols_to_keep = ['ticker', 'timestamp', 'clean_text', 'source', 'score', 'num_comments']
    
    # Ensure columns exist even if some sources didn't provide them (like RSS missing score)
    for col in cols_to_keep:
        if col not in df_combined.columns:
            df_combined[col] = 0
            
    df_final = df_combined[cols_to_keep].copy()
    
    # Sort chronologically
    df_final.sort_values(by='timestamp', inplace=True)
    
    # Save cleaned
    os.makedirs(config.CLEANED_DATA_DIR, exist_ok=True)
    output_path = os.path.join(config.CLEANED_DATA_DIR, "clean_news.csv")
    df_final.to_csv(output_path, index=False)
    
    print(f"  -> Cleaned {len(df_final)} news records saved to {output_path}")
    return df_final

def clean_market_data():
    """
    Loads raw market data, standardizes dates, and saves to cleaned/.
    """
    print("Preprocessing Market Data...")
    
    market_file = get_latest_file(os.path.join(config.RAW_DATA_DIR, "market_data_*.csv"))
    if not market_file:
        print("No raw market data found.")
        return None
        
    df_market = pd.read_csv(market_file)
    
    # Timestamps are often naive or non-UTC from yfinance, ensure UTC matching
    df_market['date'] = pd.to_datetime(df_market['date'], utc=True)
    
    # Drop any nulls (yfinance sometimes gives rows with NaNs on holidays)
    df_market.dropna(inplace=True)
    
    # Sort
    df_market.sort_values(by=['ticker', 'date'], inplace=True)
    
    os.makedirs(config.CLEANED_DATA_DIR, exist_ok=True)
    output_path = os.path.join(config.CLEANED_DATA_DIR, "clean_market.csv")
    df_market.to_csv(output_path, index=False)
    
    print(f"  -> Cleaned {len(df_market)} market records saved to {output_path}")
    return df_market

def main():
    clean_news_data()
    clean_market_data()

if __name__ == "__main__":
    main()
