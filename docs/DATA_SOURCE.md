# Data Source Documentation

## Overview
This project relies on real, publicly available financial market data and news headlines to train a model to predict abnormal market reactions. There are two primary sources of data.

## 1. Market Data
- **Source**: Yahoo Finance API (accessed via the `yfinance` Python library).
- **Data Extracted**: Daily historical prices (Open, High, Low, Close) and trading Volume (OHLCV).
- **Resolution**: Daily.
- **Proof of Real Data**: Data is pulled directly from the public Yahoo Finance servers via an open-source library widely used in academia and industry.

## 2. News Data
- **Source**: Yahoo Finance RSS Feeds (`https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US`).
- **Data Extracted**: News headlines, timestamps, source name, and category.
- **Proof of Real Data**: Feed parses real-time RSS XML data provided by Yahoo Finance, containing links to actual published financial news articles.
