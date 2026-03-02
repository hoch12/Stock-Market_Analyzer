import sys
import os

# Append the project root to sys.path so 'import config' works
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import random
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import config

class StockAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 DayTrading AI Asistent (Osobní Rádce)")
        self.root.geometry("1100x900")
        self.root.configure(bg="#F4F6F8")
        self.root.resizable(True, True)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Modern Light/Clean Theme inspired by Apartment Analyzer
        self.bg_color = "#F4F6F8"
        self.panel_color = "#FFFFFF"
        self.text_main = "#2C3E50"
        self.text_muted = "#7F8C8D"
        self.accent_color = "#3498DB"
        self.action_buy = "#27AE60"
        self.action_sell = "#E74C3C"
        self.action_hold = "#F39C12"

        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Panel.TFrame", background=self.panel_color)
        self.style.configure("TLabel", background=self.panel_color, foreground=self.text_main, font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground=self.text_main, background=self.bg_color)
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 12), foreground=self.text_muted, background=self.bg_color)
        
        self.style.configure("TButton", font=("Segoe UI", 11, "bold"), background=self.accent_color, foreground="white")
        self.style.map("TButton", background=[("active", "#2980B9")])
        self.style.configure("Action.TButton", font=("Segoe UI", 14, "bold"), background=self.action_buy, foreground="white")
        self.style.map("Action.TButton", background=[("active", "#2ecc71")])

        self.tickers = config.TARGET_TICKERS
        self.df_market = None
        self.df_ml = None
        self.model = None
        self.load_data()

        self.create_widgets()

    def load_data(self):
        try:
            market_path = os.path.join(project_root, config.CLEANED_DATA_DIR, "clean_market.csv")
            if os.path.exists(market_path):
                self.df_market = pd.read_csv(market_path)
                self.df_market['date'] = pd.to_datetime(self.df_market['date'])
                
            ml_path = os.path.join(project_root, config.PROCESSED_DATA_DIR, "ml_dataset.csv")
            if os.path.exists(ml_path):
                self.df_ml = pd.read_csv(ml_path)
                self.df_ml['date'] = pd.to_datetime(self.df_ml['date'])

            model_path = os.path.join(project_root, config.MODELS_DIR, "rf_model.pkl")
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
        except Exception as e:
            messagebox.showerror("Chyba načítání", f"Nepodařilo se načíst data či model.\n{e}")

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root, padding=(20, 20))
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="📈 Osobní Rádce pro Obchodování Akcií", style="Header.TLabel").pack()
        ttk.Label(header_frame, text="Nevíte co na burze dělat? Naše umělá inteligence vám poradí krok za krokem.", style="SubHeader.TLabel").pack()

        # Input Form
        form_frame = tk.Frame(self.root, bg=self.panel_color, bd=1, relief="ridge")
        form_frame.pack(fill=tk.X, padx=40, pady=10)
        
        inner_form = tk.Frame(form_frame, bg=self.panel_color, pady=20)
        inner_form.pack(anchor=tk.CENTER)

        tk.Label(inner_form, text="Vyberte akcii, kterou chcete prozkoumat:", font=("Segoe UI", 12), bg=self.panel_color, fg=self.text_muted).grid(row=0, column=0, padx=10)
        
        self.ticker_var = tk.StringVar()
        self.ticker_cb = ttk.Combobox(inner_form, textvariable=self.ticker_var, values=self.tickers, state="readonly", width=15, font=("Segoe UI", 12))
        self.ticker_cb.grid(row=0, column=1, padx=10)
        if self.tickers:
            self.ticker_cb.current(0)

        random_btn = ttk.Button(inner_form, text="🎲 Nevím, vyberte za mě", command=self.pick_random)
        random_btn.grid(row=0, column=2, padx=10)

        analyze_btn = ttk.Button(inner_form, text="ZAČÍT ANALÝZU", style="Action.TButton", command=self.analyze_ticker)
        analyze_btn.grid(row=1, column=0, columnspan=3, pady=20, ipadx=40, ipady=10)

        # Output Layout
        self.output_frame = tk.Frame(self.root, bg=self.bg_color)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        # Left Column for Text Advice
        self.text_frame = tk.Frame(self.output_frame, bg=self.panel_color, bd=1, relief="ridge", padx=20, pady=20)
        self.text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right Column for Chart
        self.graph_frame = tk.Frame(self.output_frame, bg=self.panel_color, bd=1, relief="ridge", padx=10, pady=10)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # --- Text Frame Elements ---
        self.lbl_action_title = tk.Label(self.text_frame, text="", font=("Segoe UI", 13, "bold"), fg=self.text_muted, bg=self.panel_color, justify=tk.LEFT)
        self.lbl_action_title.pack(anchor=tk.W)

        self.lbl_action_main = tk.Label(self.text_frame, text="Zatím žádná analýza...", font=("Segoe UI", 24, "bold"), fg=self.text_main, bg=self.panel_color, justify=tk.LEFT)
        self.lbl_action_main.pack(anchor=tk.W, pady=(0, 15))

        # Step by step box
        self.steps_box = tk.LabelFrame(self.text_frame, text=" Krok za krokem: Co přesně máte udělat ", font=("Segoe UI", 12, "bold"), bg=self.panel_color, fg=self.accent_color, padx=15, pady=10)
        self.steps_box.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        self.lbl_steps = tk.Label(self.steps_box, text="Zvolte akcii nahoře a klikněte na Začít analýzu.", font=("Segoe UI", 12), fg=self.text_main, bg=self.panel_color, justify=tk.LEFT)
        self.lbl_steps.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        self.steps_box.bind('<Configure>', lambda e: self.lbl_steps.config(wraplength=max(100, e.width - 40)))

        # Reasoning box
        self.reason_box = tk.LabelFrame(self.text_frame, text=" Proč vám to radíme? (Vysvětlení od AI) ", font=("Segoe UI", 12, "bold"), bg=self.panel_color, fg=self.text_muted, padx=15, pady=10)
        self.reason_box.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        self.lbl_reason = tk.Label(self.reason_box, text="", font=("Segoe UI", 11, "italic"), fg=self.text_main, bg=self.panel_color, justify=tk.LEFT)
        self.lbl_reason.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        self.reason_box.bind('<Configure>', lambda e: self.lbl_reason.config(wraplength=max(100, e.width - 40)))

    def pick_random(self):
        if self.tickers:
            choice = random.choice(self.tickers)
            self.ticker_cb.set(choice)
            self.analyze_ticker()

    def analyze_ticker(self):
        if self.model is None or self.df_ml is None or self.df_market is None:
            messagebox.showerror("Chyba", "Chybí data! Spusťte nejprve všechny kroky v hlavním menu.")
            return

        ticker = self.ticker_var.get()
        if not ticker: return

        ticker_data = self.df_ml[self.df_ml['ticker'] == ticker]
        if ticker_data.empty:
            messagebox.showinfo("Chybí data", f"Pro akcii {ticker} zatím nemáme zpracovaná data.")
            return
            
        latest_row = ticker_data.iloc[-1]
        
        feature_cols = [
            'open', 'volume', 'daily_volatility',
            'macro_sentiment', 'macro_engagement', 'macro_news_count',
            'specific_sentiment', 'specific_engagement', 'specific_news_count'
        ]
        
        features = latest_row[feature_cols].to_frame().T.fillna(0)
        prob_spike = self.model.predict_proba(features)[0][1]
        
        current_price = latest_row['open']
        macro_sent = latest_row['macro_sentiment']

        self.lbl_action_title.config(text=f"Doporučení pro vaši akcii: {ticker} (Cena: ${current_price:.2f})")

        # Core logic translated into Layman Czech instructions
        if prob_spike > 0.65:
            # AGRESSIVE DAYTRADE
            self.lbl_action_main.config(text="🔥 AGRESIVNÍ NÁKUP", fg=self.action_buy)
            steps = (
                "1) Hned po otevření burzy v 15:30 nakupte tyto akcie.\n\n"
                "2) Trh bude velmi divoký. Okamžitě si nastavte pojistku proti ztrátě (Stop-Loss) na -2 %.\n\n"
                "3) Jakmile budete v zisku alespoň +3 %, prodejte polovinu, abyste měli jistý výdělek."
            )
            reason = (
                f"Naše umělá inteligence zanalyzovala tisíce zpráv z Redditu a porovnala je s 5 lety historie trhu.\n\n"
                f"Zjistila, že dnešní zprávy (Sentiment skóre: {macro_sent:.2f}) se blízce podobají dnům, "
                f"kdy akcie během pár hodin narostla o více než 1.5 % (Šance podle AI: {prob_spike*100:.1f} %).\n"
                f"Očekáváme obrovský obrat, a proto se vyplatí riskovat i za cenu mírného propadu (Stop-Loss zařídí bezpečnost)."
            )
        elif prob_spike > 0.5 and macro_sent < -0.3:
            # MEAN REVERSION
            self.lbl_action_main.config(text="📉 NÁKUP V PANICE (PROTI PROUDU)", fg=self.action_buy)
            steps = (
                "1) Počkejte 30 minut po otevření trhu. Nechte akcii chvíli padat a krvácet.\n\n"
                "2) Jakmile se propad zastaví, nakupte tuto akcii ve 'slevě'.\n\n"
                "3) Nastavte si velmi těsný Stop-Loss (-1 %) pro případ, že tvrdý pád bude pokračovat. Pokud cena začne růst, nechte ji růst až do večera."
            )
            reason = (
                f"Sociální sítě jsou momentálně v silné panice (Sentiment: {macro_sent:.2f}). Lidé masivně prodávají.\n\n"
                f"Náš model nicméně ví z historických dat, že taková panika bývá přehnaná a jakmile strach opadne, "
                f"cena rychle ustřelí zpět nahoru. Chceme tedy nakoupit ve slevě těsně před tím návratem nahoru."
            )
        elif prob_spike < 0.2:
            # HOLD / DO NOTHING
            self.lbl_action_main.config(text="🤝 NEDĚLEJTE NIC (VYČKÁVEJTE)", fg=self.text_muted)
            steps = (
                "1) Dnes s touto akcií určitě neobchodujte.\n\n"
                "2) Běžte ven obdivovat přírodu nebo si uvařte kávu.\n\n"
                "3) Pokuste se nenechat strhnout nudou k tomu, abyste nakupovali nesmysly. Nechte peníze ležet."
            )
            reason = (
                f"Kolem této akcie se dnes neděje vůbec nic zjímavého. Zprávy jsou průměrné, aktivita i na sociálních "
                f"sítích je nízká (Šance na velký pohyb podle AI: jen {prob_spike*100:.1f} %).\n\n"
                f"Snažit se z toho dnes vytěžit peníze by znamenalo jen riskovat poplatky za velmi malý a nejistý zisk."
            )
        else:
            # LIGHT SWING TRADE
            self.lbl_action_main.config(text="🛒 LEHKÝ NÁKUP (NA DELŠÍ DOBU)", fg=self.action_buy)
            steps = (
                "1) Nakupte tuto akcii, ale použijte jen maximálně zhruba čtvrtinu vašeho účtu.\n\n"
                "2) Dnes nepoužívejte žádný úzký Stop-Loss, netlačte na pilu. Klidně nechte akcii dýchat.\n\n"
                "3) Nechte ji ležet pár týdnů, nejde o žádný rychlý zisk za jeden den."
            )
            reason = (
                f"Ačkoliv je celkový postoj trhu lehce pozitivní, náš model nevidí žádné zásadní signály pro obrovský výbuch "
                f"ceny směrem nahoru, jako to dělává u vysoce rizikových obchodů.\n\n"
                f"Tato akcie je aktuálně spíše bezpečným uložením peněz na delší vzdálenost."
            )

        self.lbl_steps.config(text=steps)
        self.lbl_reason.config(text=reason)

        self.plot_chart(ticker)

    def plot_chart(self, ticker):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        t_market = self.df_market[self.df_market['ticker'] == ticker].tail(60)
        
        if t_market.empty:
            return

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor(self.panel_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.panel_color)

        dates = t_market['date']
        closes = t_market['close']
        
        ax.plot(dates, closes, color=self.action_hold, linewidth=2, label="Denní Hodnota Akcie")
        
        ma20 = closes.rolling(window=20).mean()
        ax.plot(dates, ma20, color=self.text_muted, linestyle="--", linewidth=1, label="Střední hodnota (20 Dní)")

        ax.set_title(f"Historie hodnoty akcie {ticker} pro kontext", color=self.text_main, fontsize=12, pad=10)
        
        for spine in ax.spines.values():
            spine.set_color("#E0E0E0")
            
        ax.tick_params(colors=self.text_muted, labelsize=9)
        ax.grid(True, linestyle=':', alpha=0.5, color=self.text_muted)
        
        fig.autofmt_xdate(rotation=30)
        ax.legend(loc="upper left", frameon=False, labelcolor=self.text_main, fontsize=9)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerGUI(root)
    root.mainloop()
