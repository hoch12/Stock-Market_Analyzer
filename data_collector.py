import os
import time
import feedparser
import pandas as pd
from datetime import datetime
import config

def fetch_yahoo_finance_news(ticker):
    """
    Fetches news headlines for a specific ticker using Yahoo Finance RSS feed.
    """
    url = config.YAHOO_FINANCE_RSS_URL.format(ticker=ticker)
    feed = feedparser.parse(url)
    
    news_items = []
    for entry in feed.entries:
        # Extract desired fields
        try:
            # RSS dates are usually in format: 'Wed, 21 Feb 2024 15:30:00 +0000'
            dt = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            iso_date = dt.isoformat()
        except Exception:
            iso_date = datetime.now().isoformat()
            
        news_items.append({
            "ticker": ticker,
            "headline_text": entry.title,
            "timestamp": iso_date,
            "source": "Yahoo Finance",
            "category": "Market News",
            "language": "en"
        })
        
    return news_items

def main():
    print("Starting news data collection...")
    all_news = []
    
    for ticker in config.TARGET_TICKERS:
        print(f"Fetching news for {ticker}...")
        try:
            news = fetch_yahoo_finance_news(ticker)
            all_news.extend(news)
            print(f"  -> Found {len(news)} articles.")
            # Be polite to the server
            time.sleep(1)
        except Exception as e:
            print(f"  -> Error fetching news for {ticker}: {e}")
            
    if all_news:
        df = pd.DataFrame(all_news)
        
        # Ensure raw data directory exists
        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(config.RAW_DATA_DIR, f"news_data_{timestamp_str}.csv")
        
        df.to_csv(output_file, index=False)
        print(f"\nSuccessfully saved {len(df)} news articles to {output_file}")
    else:
        print("\nNo news data collected.")

if __name__ == "__main__":
    main()
