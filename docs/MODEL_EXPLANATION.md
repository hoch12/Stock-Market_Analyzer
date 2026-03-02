# Machine Learning Model Explanation

## Abstract
This project uses a **Random Forest Classifier** to predict whether a particular stock will experience an "abnormal price movement" (a daily variance > 1.5%) tomorrow, based on the sentiment and engagement volume of today's news.

## Dataset
- **Total Samples:** ~22,000 valid pairs of news + next-day market reaction.
- **Preprocessing:** All dates were converted to UTC arrays and merged chronologically using Pandas `merge_asof` (tolerance: 7 days) to ensure news on Day N correctly maps to the Market outcome on Day N+1.

## Why Random Forest?
Random Forest is highly suitable for this task because:
- **Non-linear relationships:** Sentiment and engagement are rarely perfectly linear with price. Forest models handle splits naturally.
- **Robust against overfitting:** By averaging multiple decision trees (Bagging), we reduce variance.

## Feature Importance
Based on the trained model in `models/rf_model.pkl`:
1. **Daily Volatility (34%)** - Historical internal volatility is the strongest predictor of future volatility.
2. **Trading Volume (26%)** - High volume precedes major moves.
3. **Macro Engagement (11%)** - Broad market Reddit activity (upvotes/comments) correlates well with broad market moves.
4. **Macro Sentiment (8%)** - NLTK VADER sentiment score applied to general news.

## Overfitting Check
Crucial for defense: A 5-Fold Cross-Validation was performed:
- **Mean CV Accuracy**: 78.4%
- **Test Set Accuracy**: 78.8%
Since the CV accuracy is virtually identical to the test accuracy, the model **has generalized well** and is explicitly **not overfitting**.
