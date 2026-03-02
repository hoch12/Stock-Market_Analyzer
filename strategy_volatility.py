import pandas as pd
import numpy as np
import os
import config
from risk_management import RiskManager

class StrategyVolatilityExpansion:
    """
    Simulates trading based on Volatility Expansion.
    Instead of predicting direction, it buys straddles (or proxies) when True Range exceeds Historical Average.
    """
    def __init__(self, initial_capital=10000.0):
        self.risk_manager = RiskManager(initial_capital)

    def backtest(self):
        print("Starting Volatility Expansion Strategy Backtest...")
        data_path = os.path.join(config.PROCESSED_DATA_DIR, "ml_dataset.csv")
        
        if not os.path.exists(data_path):
            return
            
        df = pd.read_csv(data_path)
        df = df.sort_values(by='date').reset_index(drop=True)
        
        # Calculate a 10-day moving average of volatility for baseline comparison.
        # Since the dataset is sparse on consecutive dates per ticker, we do our best approx.
        df['vol_ma_10'] = df.groupby('ticker')['daily_volatility'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())
        
        for index, row in df.iterrows():
            if self.risk_manager.kill_switch_active:
                break
                
            # If current volatility is 50% larger than 10-period average, it's a breakout
            if row['daily_volatility'] > (row['vol_ma_10'] * 1.5):
                current_price = row['open']
                stop_loss = current_price * 0.97 # 3% stop loss on absolute stock for simplicity
                
                shares_to_buy = self.risk_manager.calculate_position_size(current_price, stop_loss)
                
                if shares_to_buy > 0:
                    # In a real volatility expansion trade, you profit roughly off the absolute move
                    actual_return_pct = abs(row['next_day_return']) / 100.0
                    actual_return_pct -= 0.002 # Higher slippage for vol trades
                    
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
                        strategy_name="Volatility Expansion"
                    )

        print("\n=== Backtest Complete ===")
        metrics = self.risk_manager.get_performance_metrics()
        for k, v in metrics.items():
            if isinstance(v, float):
                print(f"{k}: {v:.2f}")
            else:
                print(f"{k}: {v}")

if __name__ == "__main__":
    strategy = StrategyVolatilityExpansion()
    strategy.backtest()
