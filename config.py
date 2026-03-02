import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
CLEANED_DATA_DIR = os.path.join(DATA_DIR, "cleaned")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Data Collection Parameters
# Target stock tickers representing major companies across different sectors
TARGET_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", 
    "TSLA", "NVDA", "JPM", "V", "JNJ",
    "WMT", "PG", "MA", "HD", "CVX",
    "PEP", "KO", "PFE", "ABBV", "BAC",
    "CSCO", "MCD", "DIS", "ADBE", "CRM"
]

# RSS feeds for financial news
RSS_FEEDS = {
    "CNBC_Top": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "CNBC_Investing": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "CNBC_Tech": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910",
    "CNBC_Finance": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000628",
    "WSJ_World": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "WSJ_Business": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
    "WSJ_Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "WSJ_Tech": "https://feeds.a.dj.com/rss/RSSWSJD.xml",
    "MarketWatch_Top": "http://feeds.marketwatch.com/marketwatch/topstories"
}

# Number of days of historical data to fetch when aligning market data
HISTORY_DAYS = 1825 # 5 years
