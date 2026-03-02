# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-02
### Added
- Completed `strategy_mean_reversion.py` tracking post-panic normalization.
- Defined Risk Management Layer in `risk_management.py` (position sizing, risk-per-trade).
- Built paper-trading Backtesting Engine simulating transaction costs and slippage.
- Finalized Google Colab Notebook with visual metrics (ROC-AUC, Confusion Matrix, Feature Importance).

## [0.9.0] - 2026-03-02
### Changed
- Refactored Architecture completely to fully meet PV academic demands.
- Separated Preprocessing and Feature Engineering layers.
### Added
- Created `strategy_volatility.py` for modeling expansion patterns using True Range approximation.
- Replaced missing Yahoo RSS links with robust Reddit API parsing.

## [0.8.0] - 2026-03-01
### Added
- Began Strategy Simulation layer: `strategy_event.py` for direct market movement event-trading.
- Built initial Risk Management thresholds and drawdown tracking functions.

## [0.7.0] - 2026-02-28
### Added
- Introduced 5-Fold Cross-Validation logic to prove non-overfitting in Machine Learning model.
- Created `ml_model.py` generating `rf_model.pkl` Random Forest Classifier.

## [0.6.0] - 2026-02-25
### Changed
- Shifted historical data window from 1 year to 5 years (2020-2025) to map the vast news crawl payload.
### Added
- Written `feature_engineering.py` executing `merge_asof` temporal matching with 7-day tolerances.

## [0.5.0] - 2026-02-21
### Added
- Introduced NLTK VADER sentiment analysis models for scoring headline impact values (-1.0 to 1.0).
- Created `preprocessing.py` standardizing dates into localized UTC formatting.

## [0.4.0] - 2026-02-15
### Added
- Reached the required 1500+ records threshold by crawling general financial RSS feeds and subreddits.
- Merged news strings with volume data metrics effectively.

## [0.3.1] - 2026-02-05
### Fixed
- Addressed fatal timezone discrepancy between market data `open/close` values and news timestamp values, causing `Merge` crashes.

## [0.3.0] - 2026-01-28
### Added
- Introduced text cleanup logic removing HTML escape characters and redundant whitespace in crawled values. 

## [0.2.0] - 2026-01-15
### Added
- Implemented core Python API interactions using `yfinance` to establish historical `OHLCV` boundaries.
- Designed market alignment system (`market_data_collector.py`).

## [0.1.0] - 2026-01-05
### Added
- Established base directory structures (`data/`, `models/`, `docs/`).
- Wrote initial configuration parameters.
- Designed simplistic web scraper for news retrieval (initial data crawler).
