import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import os
import time
import pandas as pd
from datetime import datetime
import config
import feedparser
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def fetch_rss_news():
    """
    Fetches news headlines from general financial RSS feeds configured in config.py.
    Returns a list of dictionaries.
    """
    news_items = []
    
    for feed_name, url in config.RSS_FEEDS.items():
        print(f"Fetching RSS feed: {feed_name}...")
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                # Find publication date
                pub_date = entry.get('published', '')
                if not pub_date:
                    pub_date = entry.get('updated', str(datetime.now()))
                
                # Check if it mentions any target tickers
                headline = entry.get('title', '')
                summary = entry.get('summary', '')
                
                mentioned_tickers = []
                for ticker in config.TARGET_TICKERS:
                    if ticker in headline or ticker in summary:
                        mentioned_tickers.append(ticker)
                
                # If no specific ticker mentioned, map it to 'GENERAL'
                if not mentioned_tickers:
                    mentioned_tickers = ['GENERAL']
                
                for t in mentioned_tickers:
                    news_items.append({
                        "ticker": t,
                        "headline_text": headline,
                        "summary_text": summary[:200], # store a snippet
                        "timestamp": pub_date,
                        "source": feed_name,
                        "category": "Market News",
                        "language": "en"
                    })
        except Exception as e:
            print(f"  -> Error parsing {feed_name}: {e}")
            
    return news_items

def main():
    print("Starting broad news data collection...")
    all_news = fetch_rss_news()
            
    if all_news:
        df = pd.DataFrame(all_news)
        
        # Deduplicate based on headline to avoid exact same news multiple times
        df = df.drop_duplicates(subset=['headline_text', 'ticker'])
        
        # Ensure raw data directory exists
        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(config.RAW_DATA_DIR, f"news_broad_data_{timestamp_str}.csv")
        
        df.to_csv(output_file, index=False)
        print(f"\nSuccessfully saved {len(df)} news articles to {output_file}")
    else:
        print("\nNo news data collected.")

if __name__ == "__main__":
    main()
