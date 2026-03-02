import os
import requests
import pandas as pd
import time
from datetime import datetime
import config

def fetch_reddit_financial_news():
    """
    Crawls financial subreddits using Reddit's public JSON API.
    This safely bypasses the need for an API key while gathering >1500 
    real-world, timestamped records with multiple attributes.
    """
    subreddits = ['investing', 'StockMarket', 'wallstreetbets', 'Economics', 'Finance']
    all_posts = []
    
    headers = {
        'User-Agent': 'MarketAnalyzer Academic Project/1.0 (Coursework PV)'
    }
    
    print("Starting Reddit financial data collection...")
    
    for sub in subreddits:
        print(f"Crawling r/{sub}...")
        after = None
        # Try to get 10 pages of 100 items each per subreddit (up to 1000 max provided by reddit API)
        for page in range(10):
            url = f"https://www.reddit.com/r/{sub}/new.json?limit=100"
            if after:
                url += f"&after={after}"
                
            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"  -> Error {response.status_code} on page {page+1}")
                    break
                    
                data = response.json()
                children = data.get('data', {}).get('children', [])
                
                if not children:
                    break
                    
                count = 0
                for child in children:
                    post = child['data']
                    
                    # Extract features
                    title = post.get('title', '')
                    selftext = post.get('selftext', '')
                    score = post.get('score', 0)
                    upvote_ratio = post.get('upvote_ratio', 0.0)
                    num_comments = post.get('num_comments', 0)
                    created_utc = post.get('created_utc', 0)
                    
                    # Skip completely non-descriptive titles
                    if len(title) < 15:
                        continue
                        
                    # Map to a ticker if one is mentioned, else 'GENERAL'
                    identified_ticker = 'GENERAL'
                    for t in config.TARGET_TICKERS:
                        # Simple keyword based assignment
                        if t in title.split():
                            identified_ticker = t
                            break
                            
                    iso_date = datetime.fromtimestamp(created_utc).isoformat()
                    
                    all_posts.append({
                        "ticker": identified_ticker,
                        "headline_text": title,
                        "timestamp": iso_date,
                        "source": f"Reddit r/{sub}",
                        "category": "Social Sentiment & News",
                        "score": score,
                        "upvote_ratio": upvote_ratio,
                        "num_comments": num_comments,
                        "language": "en"
                    })
                    count += 1
                
                print(f"  -> Page {page+1}: Fetched {count} posts.")
                after = data.get('data', {}).get('after')
                
                if not after:
                    print(f"  -> Reached end of available feed for r/{sub}.")
                    break
                    
            except Exception as e:
                print(f"  -> Request failed: {e}")
                break
                
            # Sleep to respect rate limits (Reddit allows 60 req/min for unauthenticated scripts in theory, sometimes 10 req/min)
            time.sleep(2)
            
    return all_posts

def main():
    posts = fetch_reddit_financial_news()
    
    if posts:
        df = pd.DataFrame(posts)
        # Drop identical headlines to ensure clean data
        df = df.drop_duplicates(subset=['headline_text'])
        
        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(config.RAW_DATA_DIR, f"news_reddit_{timestamp_str}.csv")
        
        df.to_csv(output_file, index=False)
        print(f"\nSuccessfully saved {len(df)} financial news and sentiment records to {output_file}")
        
        # Verify the 1500 limit for PV requirements
        if len(df) >= 1500:
            print("SUCCESS: 1500+ record requirement met!")
        else:
            print(f"WARNING: Only collected {len(df)} records. Run again or add more subreddits.")
    else:
        print("\nNo data collected.")

if __name__ == "__main__":
    main()
