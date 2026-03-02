import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import pandas as pd
import numpy as np

class RiskManager:
    """
    Handles position sizing, drawdown limits, and basic capital allocation.
    """
    def __init__(self, initial_capital=10000.0, risk_per_trade_pct=0.02, max_drawdown_pct=0.15):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.peak_capital = initial_capital
        
        self.trade_history = []
        self.active_position = None
        self.kill_switch_active = False

    def update_capital(self, pnl):
        """Updates account balance and tracking peak capital."""
        self.capital += pnl
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital
            
        current_drawdown = (self.peak_capital - self.capital) / self.peak_capital
        if current_drawdown >= self.max_drawdown_pct:
            print("KILL SWITCH ENGAGED: Max Drawdown threshold breached.")
            self.kill_switch_active = True

    def calculate_position_size(self, current_price, stop_loss_price):
        """
        Calculates how many shares to buy based on risk limits.
        """
        if self.kill_switch_active:
            return 0
            
        risk_amount = self.capital * self.risk_per_trade_pct
        risk_per_share = abs(current_price - stop_loss_price)
        
        if risk_per_share <= 0:
            return 0
            
        shares = int(risk_amount / risk_per_share)
        
        # Ensure we don't buy more than we can afford (leverage check)
        max_shares_affordable = int(self.capital / current_price)
        return min(shares, max_shares_affordable)

    def log_trade(self, entry_date, ticker, entry_price, exit_price, shares, pnl, strategy_name):
        self.trade_history.append({
            'date': entry_date,
            'ticker': ticker,
            'strategy': strategy_name,
            'entry': entry_price,
            'exit': exit_price,
            'shares': shares,
            'pnl': pnl,
            'balance': self.capital
        })

    def get_performance_metrics(self):
        if not self.trade_history:
            return {"Total Trades": 0, "Net Profit": 0}
            
        df = pd.DataFrame(self.trade_history)
        wins = df[df['pnl'] > 0]
        losses = df[df['pnl'] <= 0]
        
        win_rate = len(wins) / len(df) * 100 if len(df) > 0 else 0
        net_profit = self.capital - self.initial_capital
        
        return {
            "Initial Capital": self.initial_capital,
            "Final Capital": self.capital,
            "Net Profit": net_profit,
            "Total Trades": len(df),
            "Win Rate (%)": win_rate,
            "Max Drawdown (%)": ((self.peak_capital - self.capital) / self.peak_capital) * 100
        }
