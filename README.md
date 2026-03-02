# Event-Driven Market Reaction & Volatility Analysis System
**Academic Python Project (PV) v1.0.0**

## Abstract
This project is an end-to-end Machine Learning and Algorithmic Trading simulation system. It analyzes how financial markets react to real-world news events by dynamically crawling external text APIs (Reddit) and Market structures (Yahoo Finance), mapping them using NLTK Sentiment Analysis, and training a Random Forest Model to predict abnormal volatility movements.

## Features
- **Data Crawler (`data_collector.py`, `market_data_collector.py`)**: Fetches 5 years of historical OHLCV market data alongside over 4,500 real financial news strings.
- **Preprocessing (`preprocessing.py`)**: Normalizes timestamps into timezone-aware UTC frames to accurately overlay text datasets onto trading market hours.
- **Feature Engineering (`feature_engineering.py`)**: Quantifies unstructured text using NLTK (VADER) `sentiment` and `engagement_index` scoring mechanisms. Calculates historical True Range (`daily_volatility`).
- **Machine Learning Pipeline (`ml_model.py`)**: Trains an ensemble Random Forest model to ~79% accuracy with an ROC-AUC of 0.71. Incorporates native 5-Fold Cross Validation.
- **Algorithmic Strategies (`strategy_*.py`)**: Simulates Event-Driven, Volatility Expansion, and Mean-Reversion execution strategies against historical unseen data.
- **Risk Management (`risk_management.py`)**: Integrates Position Sizing formulas and a Max-Drawdown kill switch to prevent catastrophic ruin on backtests.

## Prerequisites
This software runs purely on standard Python without the need for an IDE.

1. Ensure Python 3.9+ is installed.
2. Install external requirements:
```bash
pip install -r requirements.txt
```

*(Note for Mac users executing on system Python: if you encounter SSL certificate errors during the `requirements.txt` execution, they are natively bypassed in the script architecture.)*

## How to Execute the Platform

### Phase 1: Data Acquisition
If you wish to re-pull live external data, run:
```bash
python3 market_data_collector.py
python3 reddit_finance_crawler.py
```
*Datasets will be deposited into `data/raw/`.*

### Phase 2: Feature Engineering & Preprocessing
To merge texts with stock price behaviors and generate ML features:
```bash
python3 preprocessing.py
python3 feature_engineering.py
```
*The synthesized ML matrix drops into `data/processed/ml_dataset.csv`.*

### Phase 3: Machine Learning Model Training
Train the Random Forest model independently:
```bash
python3 ml_model.py
```
*Creates `models/rf_model.pkl` and outputs Cross-Validation logs to the console.*

### Phase 4: Strategy Simulation
Backtest the models over chronological datasets:
```bash
python3 strategy_event.py
python3 strategy_volatility.py
python3 strategy_mean_reversion.py
```
*Prints Net PNL, Trade Amount, Stop-Loss triggers, and Win-Rate percentages.*

## Colab Notebook (Defense Artifact)
Required educational artifacts outlining the feature importance weights and Confusion Matrix plots are located in:
`notebooks/colab_training.ipynb`

Load this explicitly into Google Colab if presenting visual outcomes.
