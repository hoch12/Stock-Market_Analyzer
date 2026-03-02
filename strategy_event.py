import pandas as pd
import numpy as np
import os
import pickle
import config
from risk_management import RiskManager

class StrategyEventReaction:
    """
    Simulates trading based entirely on the ML Model's predictions of abnormal movement.
    If a spike is predicted, we enter a volatility trade (simplified here as buying the underlying).
    """
    def __init__(self, initial_capital=10000.0):
        self.risk_manager = RiskManager(initial_capital)
        
        model_path = os.path.join(config.MODELS_DIR, "rf_model.pkl")
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            print("Model not found. Run ml_model.py first.")
            self.model = None

    def backtest(self):
        """
        Runs the exact dataset through a time-series simulation, executing trades
        when the model strongly predicts a >1.5% movement.
        """
        print("Starting Event Reaction Strategy Backtest...")
        data_path = os.path.join(config.PROCESSED_DATA_DIR, "ml_dataset.csv")
        
        if not os.path.exists(data_path) or self.model is None:
            return
            
        df = pd.read_csv(data_path)
        feature_cols = [
            'open', 'volume', 'daily_volatility',
            'macro_sentiment', 'macro_engagement', 'macro_news_count',
            'specific_sentiment', 'specific_engagement', 'specific_news_count'
        ]
        
        # Chronological sort is critical for backtesting
        df = df.sort_values(by='date').reset_index(drop=True)
        
        trade_count = 0
        winning_trades = 0
        
        for index, row in df.iterrows():
            if self.risk_manager.kill_switch_active:
                break
                
            X_current = row[feature_cols].to_frame().T.fillna(0)
            
            # Predict probability of a spike
            prob_spike = self.model.predict_proba(X_current)[0][1]
            
            # If high confidence (> 65%), we "take a position"
            if prob_spike > 0.65:
                current_price = row['open']
                # Assume stop loss at 2% below current open
                stop_loss = current_price * 0.98 
                
                shares_to_buy = self.risk_manager.calculate_position_size(current_price, stop_loss)
                
                if shares_to_buy > 0:
                    # In this simulation, we buy at Open, sell at Next Day Open (or Close).
                    # 'next_day_return' already holds this percentage change: (NextOpen - CurOpen)/NextOpen
                    
                    actual_return_pct = row['next_day_return'] / 100.0
                    
                    # Transaction costs and slippage simulation: 0.1% cost
                    actual_return_pct -= 0.001
                    
                    # If it hit our 2% stop loss intraday, we take the max loss instead
                    # Our daily volatility feature helps approximate this, but for simplicity:
                    if actual_return_pct < -0.02:
                        actual_return_pct = -0.02
                        
                    pnl = shares_to_buy * current_price * actual_return_pct
                    
                    # Calculate exit price based on pnl
                    exit_price = current_price * (1 + actual_return_pct)
                    
                    self.risk_manager.update_capital(pnl)
                    self.risk_manager.log_trade(
                        entry_date=row['date'],
                        ticker=row['ticker'],
                        entry_price=current_price,
                        exit_price=exit_price,
                        shares=shares_to_buy,
                        pnl=pnl,
                        strategy_name="Event Reaction"
                    )
                    
                    trade_count += 1
                    if pnl > 0:
                        winning_trades += 1

        print("\n=== Backtest Complete ===")
        metrics = self.risk_manager.get_performance_metrics()
        for k, v in metrics.items():
            if isinstance(v, float):
                print(f"{k}: {v:.2f}")
            else:
                print(f"{k}: {v}")

if __name__ == "__main__":
    strategy = StrategyEventReaction()
    strategy.backtest()
