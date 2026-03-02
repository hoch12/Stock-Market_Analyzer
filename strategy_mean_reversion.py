import pandas as pd
import numpy as np
import os
import config
from risk_management import RiskManager

class StrategyMeanReversion:
    """
    Simulates Mean Reversion.
    If a stock drops significantly relative to its recent average because of a bad news event, 
    we buy the dip expecting it to normalize.
    """
    def __init__(self, initial_capital=10000.0):
        self.risk_manager = RiskManager(initial_capital)

    def backtest(self):
        print("Starting Mean Reversion Strategy Backtest...")
        data_path = os.path.join(config.PROCESSED_DATA_DIR, "ml_dataset.csv")
        
        if not os.path.exists(data_path):
            return
            
        df = pd.read_csv(data_path)
        df = df.sort_values(by='date').reset_index(drop=True)
        
        # 20-day Moving Average of the Open price as our "Mean"
        df['open_ma_20'] = df.groupby('ticker')['open'].transform(lambda x: x.rolling(window=20, min_periods=1).mean())
        
        for index, row in df.iterrows():
            if self.risk_manager.kill_switch_active:
                break
                
            current_price = row['open']
            mean_price = row['open_ma_20']
            
            # If the stock opens 5% BELOW its 20-day Moving Average AND there was heavily negative news
            # (We use macro_sentiment < -0.3 as a proxy for bad news days)
            if current_price < (mean_price * 0.95) and row['macro_sentiment'] < -0.3:
                
                # Stop loss tighter for mean reversion since falling knives are dangerous
                stop_loss = current_price * 0.95 
                
                shares_to_buy = self.risk_manager.calculate_position_size(current_price, stop_loss)
                
                if shares_to_buy > 0:
                    # Target is returning to the mean
                    target_price = mean_price
                    target_pct = (target_price - current_price) / current_price
                    
                    # We look at exactly what happened next_day_return
                    actual_return_pct = row['next_day_return'] / 100.0
                    actual_return_pct -= 0.001 # slippage
                    
                    pnl = shares_to_buy * current_price * actual_return_pct
                    exit_price = current_price * (1 + actual_return_pct)
                    
                    self.risk_manager.update_capital(pnl)
                    self.risk_manager.log_trade(
                        entry_date=row['date'],
                        ticker=row['ticker'],
                        entry_price=current_price,
                        exit_price=exit_price,
                        shares=shares_to_buy,
                        pnl=pnl,
                        strategy_name="Mean Reversion"
                    )

        print("\n=== Backtest Complete ===")
        metrics = self.risk_manager.get_performance_metrics()
        for k, v in metrics.items():
            if isinstance(v, float):
                print(f"{k}: {v:.2f}")
            else:
                print(f"{k}: {v}")

if __name__ == "__main__":
    strategy = StrategyMeanReversion()
    strategy.backtest()
