import os
import pandas as pd
import numpy as np
from datetime import timedelta
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ssl
import config

# Fix for Mac SSL cert issues when downloading NLTK datasets
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
    
# Download vader lexicon if not already present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

def engineer_features():
    """
    Takes the cleaned news and market data, aligns them chronologically, 
    calculates text sentiment, and generates target labels (price movements).
    """
    print("Starting Feature Engineering...")
    
    news_path = os.path.join(config.CLEANED_DATA_DIR, "clean_news.csv")
    market_path = os.path.join(config.CLEANED_DATA_DIR, "clean_market.csv")
    
    if not os.path.exists(news_path) or not os.path.exists(market_path):
        print("Cleaned data not found. Run preprocessing.py first.")
        return
        
    df_news = pd.read_csv(news_path)
    df_market = pd.read_csv(market_path)
    
    # Convert dates back to timezone aware UTC
    df_news['timestamp'] = pd.to_datetime(df_news['timestamp'], utc=True)
    df_market['date'] = pd.to_datetime(df_market['date'], utc=True)
    
    # Init Sentiment Analyzer
    sia = SentimentIntensityAnalyzer()
    
    print("Calculating Sentiment Scores...")
    # Apply VADER sentiment
    df_news['sentiment'] = df_news['clean_text'].apply(lambda x: sia.polarity_scores(str(x))['compound'])
    
    # Create an engagement metric
    # Reddit posts have score and comments. We normalize to give a generic "impact" weight
    max_score = df_news['score'].max() if df_news['score'].max() > 0 else 1
    max_cmts = df_news['num_comments'].max() if df_news['num_comments'].max() > 0 else 1
    
    df_news['engagement_index'] = (df_news['score'] / max_score) + (df_news['num_comments'] / max_cmts)
    
    # We will aggregate news by date so we have 1 sentiment score per ticker per day
    # We map news to the NEXT trading day because if a news comes out at 3PM today, 
    # the market reaction is mostly felt tomorrow.
    
    # Floor timestamp to just getting the date
    df_news['news_date'] = df_news['timestamp'].dt.floor('d')
    
    # Group by ticker and date to get average daily sentiment and total engagement
    daily_news = df_news.groupby(['ticker', 'news_date']).agg({
        'sentiment': 'mean',
        'engagement_index': 'sum',
        'clean_text': 'count' # Number of articles/posts
    }).reset_index()
    daily_news.rename(columns={'clean_text': 'news_count'}, inplace=True)
    
    print("Aligning News with Market Data...")
    
    # Create target variables in Market Data
    # 1-day percentage return (Close to Close)
    # We shift so that the current row represents the return generated TOMORROW
    
    master_df_list = []
    
    # Process per ticker to align dates correctly
    for ticker, group in df_market.groupby('ticker'):
        group = group.copy()
        
        # Next day open vs next day close (the market reaction to overnight news)
        group['next_day_return'] = (group['close'].shift(-1) - group['open'].shift(-1)) / group['open'].shift(-1) * 100
        
        # Volatility metric (True Range approximation)
        group['daily_volatility'] = (group['high'] - group['low']) / group['open'] * 100
        
        # Target: Did the price move more than 1.5% the next day? (Classification)
        group['abnormal_movement'] = (group['next_day_return'].abs() > 1.5).astype(int)
        
        master_df_list.append(group)
        
    df_market_targets = pd.concat(master_df_list)
    df_market_targets.dropna(subset=['next_day_return'], inplace=True)
    
    # Now merge. For news on Day T, we map it to Market Date T+1 (or closest next trading day)
    # Pandas merge_asof is perfect for this (merge to the nearest future date)
    
    # We need both dfs sorted by date
    daily_news.sort_values('news_date', inplace=True)
    df_market_targets.sort_values('date', inplace=True)
    
    merged_data = pd.DataFrame()
    
    # Process GENERAL macro news explicitly
    t_news_general = daily_news[daily_news['ticker'] == 'GENERAL'].copy()
    if not t_news_general.empty:
        t_news_general.rename(columns={'sentiment': 'macro_sentiment', 'engagement_index': 'macro_engagement', 'news_count': 'macro_news_count'}, inplace=True)
        t_news_general.drop(columns=['ticker'], inplace=True)
        t_news_general.sort_values('news_date', inplace=True)
    
    for ticker in config.TARGET_TICKERS:
        # Get specific news, if any, for this ticker
        t_news = daily_news[daily_news['ticker'] == ticker].copy()
        t_market = df_market_targets[df_market_targets['ticker'] == ticker].copy()
        
        if t_market.empty:
            continue
            
        # We need to map dates. We will use the market dates as the master index
        # and left merge both specific news and macro news.
        # This guarantees we get all valid market records, and attach whatever news was available recently.
        
        # Merge macro news using merge_asof (backward looking to find the *latest* news BEFORE this market open)
        merged = pd.merge_asof(
            t_market,
            t_news_general,
            left_on='date',
            right_on='news_date',
            direction='backward',
            tolerance=pd.Timedelta(days=7) # News is valid for up to 7 days
        )
        
        # If there is specific news, merge it too
        if not t_news.empty:
            t_news.rename(columns={'sentiment': 'specific_sentiment', 'engagement_index': 'specific_engagement', 'news_count': 'specific_news_count'}, inplace=True)
            t_news.drop(columns=['ticker'], inplace=True)
            t_news.sort_values('news_date', inplace=True)
            
            merged = pd.merge_asof(
                merged,
                t_news,
                left_on='date',
                right_on='news_date',
                direction='backward',
                tolerance=pd.Timedelta(days=7)
            )
        else:
            merged['specific_sentiment'] = 0.0
            merged['specific_engagement'] = 0.0
            merged['specific_news_count'] = 0.0
            
        merged_data = pd.concat([merged_data, merged])
        
    # Fill missing gaps where there was no news
    for col in ['macro_sentiment', 'macro_engagement', 'macro_news_count', 'specific_sentiment', 'specific_engagement', 'specific_news_count']:
        if col in merged_data.columns:
            merged_data[col] = merged_data[col].fillna(0)
            
    # Drop rows where we have absolutely NO news at all (either macro or specific)
    merged_data = merged_data[(merged_data['macro_news_count'] > 0) | (merged_data['specific_news_count'] > 0)]
    
    print(f"Final ML Dataset contains {len(merged_data)} samples.")
    
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    output_path = os.path.join(config.PROCESSED_DATA_DIR, "ml_dataset.csv")
    merged_data.to_csv(output_path, index=False)
    
    print(f"  -> Engineered Features saved to {output_path}")

if __name__ == "__main__":
    engineer_features()
