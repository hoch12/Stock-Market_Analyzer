import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pickle
import config

def train_model():
    """
    Trains a Random Forest classifier to predict abnormal market movement
    based on news sentiment and engagement metrics.
    """
    print("Loading ML dataset...")
    data_path = os.path.join(config.PROCESSED_DATA_DIR, "ml_dataset.csv")
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return
        
    df = pd.read_csv(data_path)
    print(f"Dataset shape: {df.shape}")
    
    # Define features and target
    # features = sentiment (macro + specific), engagement (macro + specific), daily volatility
    # target = abnormal_movement (0 or 1)
    
    feature_cols = [
        'open', 'volume', 'daily_volatility',
        'macro_sentiment', 'macro_engagement', 'macro_news_count',
        'specific_sentiment', 'specific_engagement', 'specific_news_count'
    ]
    
    X = df[feature_cols]
    y = df['abnormal_movement']
    
    # Handle any remaining NaNs
    X = X.fillna(0)
    
    # Train/Test Split (80% train, 20% test)
    # Since this is time-series-ish, a chronological split is better for realism, 
    # but for a basic academic project, random split is usually accepted.
    # We will do a random split here for standard metrics.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")
    
    # Initialize Model - Random Forest avoids severe overfitting if tuned, handles non-linearities
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    
    print("Training Random Forest Classifier...")
    model.fit(X_train, y_train)
    
    # Evaluation
    print("\n--- Model Evaluation ---")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    try:
        roc_auc = roc_auc_score(y_test, y_prob)
        print(f"ROC-AUC Score: {roc_auc:.4f}")
    except ValueError:
        pass
        
    # Feature Importance
    importances = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nFeature Importances:")
    print(importances)
    
    # Save the model
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    model_path = os.path.join(config.MODELS_DIR, "rf_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    print(f"\nModel saved to {model_path}")
    
    # Check for overfitting using cross-validation on the training set
    print("\nChecking for overfitting (5-Fold Cross Validation on Train Set):")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"CV Accuracy Scores: {cv_scores}")
    print(f"Mean CV Accuracy: {cv_scores.mean():.4f}")
    print(f"Test Set Accuracy: {model.score(X_test, y_test):.4f}")
    
    if (model.score(X_train, y_train) - model.score(X_test, y_test)) > 0.15:
        print("WARNING: Model might be overfitting (Train accuracy >15% higher than Test).")
    else:
        print("Model generalization looks acceptable.")

if __name__ == "__main__":
    train_model()
