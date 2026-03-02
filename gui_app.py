import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import os
import random
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import config

class StockAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Market Analyzer - Machine Learning Dashboard")
        self.root.geometry("900x800")
        self.root.configure(bg="#1E1E2E")
        self.root.resizable(True, True)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colors
        self.bg_color = "#1E1E2E"
        self.panel_color = "#282A36"
        self.text_color = "#F8F8F2"
        self.accent_color = "#BD93F9"
        self.success_color = "#50FA7B"
        self.danger_color = "#FF5555"

        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Panel.TFrame", background=self.panel_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground=self.accent_color)
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 12), foreground="#8BE9FD")
        self.style.configure("TButton", font=("Segoe UI", 11, "bold"), background=self.accent_color, foreground="#282A36")
        self.style.map("TButton", background=[("active", "#FF79C6")])
        self.style.configure("Action.TButton", font=("Segoe UI", 12, "bold"), background=self.success_color, foreground="#282A36")
        self.style.map("Action.TButton", background=[("active", "#8BE9FD")])

        # Load Data
        self.tickers = config.TARGET_TICKERS
        self.df_market = None
        self.df_ml = None
        self.model = None
        self.load_data()

        self.create_widgets()

    def load_data(self):
        """Loads required datasets and the trained ML model."""
        try:
            market_path = os.path.join(config.CLEANED_DATA_DIR, "clean_market.csv")
            if os.path.exists(market_path):
                self.df_market = pd.read_csv(market_path)
                self.df_market['date'] = pd.to_datetime(self.df_market['date'])
                
            ml_path = os.path.join(config.PROCESSED_DATA_DIR, "ml_dataset.csv")
            if os.path.exists(ml_path):
                self.df_ml = pd.read_csv(ml_path)
                self.df_ml['date'] = pd.to_datetime(self.df_ml['date'])

            model_path = os.path.join(config.MODELS_DIR, "rf_model.pkl")
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
        except Exception as e:
            messagebox.showerror("Error Loading Data", f"Ensure all phases of the pipeline are complete.\n{e}")

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root, padding=(20, 20))
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="Event-Driven Market Analyzer", style="Header.TLabel").pack()
        ttk.Label(header_frame, text="AI-Powered Day Trading Recommendations", style="SubHeader.TLabel").pack()

        # Control Panel
        control_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=(20, 20))
        control_frame.pack(fill=tk.X, padx=20, pady=10)

        # Controls Inner Container
        inner_ctrl = ttk.Frame(control_frame, style="Panel.TFrame")
        inner_ctrl.pack(anchor=tk.CENTER)

        ttk.Label(inner_ctrl, text="Select Stock Ticker:", style="TLabel", background=self.panel_color).grid(row=0, column=0, padx=10)
        
        self.ticker_var = tk.StringVar()
        self.ticker_cb = ttk.Combobox(inner_ctrl, textvariable=self.ticker_var, values=self.tickers, state="readonly", width=15)
        self.ticker_cb.grid(row=0, column=1, padx=10)
        if self.tickers:
            self.ticker_cb.current(0)

        random_btn = ttk.Button(inner_ctrl, text="🎲 Random Pick", command=self.pick_random)
        random_btn.grid(row=0, column=2, padx=10)

        analyze_btn = ttk.Button(inner_ctrl, text="⚡ ANALYZE CURRENT CONDITIONS", style="Action.TButton", command=self.analyze_ticker)
        analyze_btn.grid(row=1, column=0, columnspan=3, pady=20, ipadx=20, ipady=5)

        # Output View
        self.output_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=(20, 20))
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Setup split layout in output
        self.text_frame = tk.Frame(self.output_frame, bg=self.panel_color)
        self.text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.graph_frame = tk.Frame(self.output_frame, bg=self.panel_color)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Text Results
        self.lbl_title = tk.Label(self.text_frame, text="Awaiting Analysis...", font=("Segoe UI", 16, "bold"), fg=self.accent_color, bg=self.panel_color)
        self.lbl_title.pack(anchor=tk.W, pady=(0, 10))

        self.lbl_sentiment = tk.Label(self.text_frame, text="", font=("Segoe UI", 12), fg=self.text_color, bg=self.panel_color, justify=tk.LEFT)
        self.lbl_sentiment.pack(anchor=tk.W, pady=5)

        self.lbl_prediction = tk.Label(self.text_frame, text="", font=("Segoe UI", 12), fg=self.text_color, bg=self.panel_color, justify=tk.LEFT)
        self.lbl_prediction.pack(anchor=tk.W, pady=5)

        self.lbl_recommendation = tk.Label(self.text_frame, text="", font=("Segoe UI", 14, "bold"), fg=self.success_color, bg=self.panel_color, justify=tk.LEFT)
        self.lbl_recommendation.pack(anchor=tk.W, pady=20)

    def pick_random(self):
        if self.tickers:
            choice = random.choice(self.tickers)
            self.ticker_cb.set(choice)
            self.analyze_ticker()

    def analyze_ticker(self):
        if self.model is None or self.df_ml is None or self.df_market is None:
            messagebox.showerror("Missing Data", "Cannot analyze. ML Model or Dataset files are missing.")
            return

        ticker = self.ticker_var.get()
        if not ticker: return

        # Get the most recent data row for this ticker
        ticker_data = self.df_ml[self.df_ml['ticker'] == ticker]
        if ticker_data.empty:
            messagebox.showinfo("No Data", f"No ML features generated for {ticker} yet.")
            return
            
        latest_row = ticker_data.iloc[-1]
        
        feature_cols = [
            'open', 'volume', 'daily_volatility',
            'macro_sentiment', 'macro_engagement', 'macro_news_count',
            'specific_sentiment', 'specific_engagement', 'specific_news_count'
        ]
        
        features = latest_row[feature_cols].to_frame().T.fillna(0)
        
        # Predict
        prob_spike = self.model.predict_proba(features)[0][1]
        
        # Extract meaningful data for UI
        current_price = latest_row['open']
        macro_sent = latest_row['macro_sentiment']
        daily_vol = latest_row['daily_volatility']

        self.lbl_title.config(text=f"Analysis for {ticker} (Last Close: ${current_price:.2f})")
        
        sent_text = "Bullish 📈" if macro_sent > 0 else "Bearish 📉" if macro_sent < 0 else "Neutral ⚖️"
        self.lbl_sentiment.config(text=f"Macro News Sentiment: {sent_text} (Score: {macro_sent:.2f})\nDaily Volatility Baseline: {daily_vol:.2f}%")
        
        pred_text = "YES" if prob_spike > 0.5 else "NO"
        pred_color = self.danger_color if prob_spike > 0.5 else self.text_color
        self.lbl_prediction.config(text=f"Abnormal Market Spike Expected: {pred_text} ({prob_spike*100:.1f}%)", fg=pred_color)

        # Logic for determining the trade plan
        trade_plan = "HOLD / DO NOT TRADE"
        plan_desc = "Market conditions are ordinary. Risk/reward is not favorable."
        plan_color = self.text_color

        if prob_spike > 0.65:
            trade_plan = "EXECUTE: VOLATILITY EXPANSION"
            plan_desc = "High probability of severe move. Enter breakout straddle or directional swing."
            plan_color = self.accent_color
        elif prob_spike > 0.5 and macro_sent < -0.3:
            trade_plan = "EXECUTE: MEAN REVERSION"
            plan_desc = "Market overreacting to negative news. Look to buy the dip below 20MA."
            plan_color = self.success_color
        elif prob_spike < 0.2:
            trade_plan = "EXECUTE: SHORT OPTIONS (IRON CONDOR)"
            plan_desc = "Extremely low probability of movement. Market will likely range-bound today."
            plan_color = "#F1FA8C" # Yellow

        self.lbl_recommendation.config(text=f"💡 RECOMMENDED PLAN:\n{trade_plan}\n\n{plan_desc}", fg=plan_color)

        # Update Chart
        self.plot_chart(ticker)

    def plot_chart(self, ticker):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Get last 60 days of market data
        t_market = self.df_market[self.df_market['ticker'] == ticker].tail(60)
        
        if t_market.empty:
            return

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor(self.panel_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.panel_color)

        dates = t_market['date']
        closes = t_market['close']
        
        ax.plot(dates, closes, color=self.success_color, linewidth=2)
        
        # 20 Day MA
        ma20 = closes.rolling(window=20).mean()
        ax.plot(dates, ma20, color=self.accent_color, linestyle="--", linewidth=1, label="20 MA")

        ax.set_title(f"{ticker} - 60 Day Price Action", color=self.text_color, fontsize=10)
        
        # Format axes
        for spine in ax.spines.values():
            spine.set_color(self.text_color)
            
        ax.tick_params(colors=self.text_color, labelsize=8)
        ax.grid(True, linestyle=':', alpha=0.3, color=self.text_color)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        fig.autofmt_xdate(rotation=30)
        ax.legend(loc="upper left", frameon=False, labelcolor=self.text_color)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerGUI(root)
    root.mainloop()
