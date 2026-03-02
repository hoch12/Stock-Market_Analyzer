import sys
import subprocess
import time
import os

def run_script(script_name, description):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {description} ({script_name})")
    print(f"{'='*60}")
    time.sleep(1)
    
    # We will pass the parent directory into PYTHONPATH so relative imports work down the tree
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    try:
        subprocess.run([sys.executable, script_name], env=env, check=True)
        print(f"✅ SUCCESS: {script_name} completed.")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {script_name} failed with exit code {e.returncode}.")
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find '{script_name}'. Are you in the right directory?")

def main():
    print("""
    =========================================================
     EVENT-DRIVEN MARKET REACTION & VOLATILITY ANALYSIS
     Academic Python Project (PV)
    =========================================================
    """)
    
    while True:
        print("\nMain Menu:")
        print("  1. Run Phase 1: Data Collection (Crawlers)")
        print("  2. Run Phase 2: Feature Engineering & Preprocessing")
        print("  3. Run Phase 3: Train Machine Learning Model (Random Forest)")
        print("  4. Run Phase 4: Strategy Simulations (Backtesting)")
        print("  5. 🚀 RUN ENTIRE PIPLELINE (CLI Only)")
        print("  6. 🖥️  SPUSTIT APLIKACI / LAUNCH GUI")
        print("  0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '1':
            run_script("src/data_collection/market_data_collector.py", "Market Data Collector")
            run_script("src/data_collection/reddit_finance_crawler.py", "Reddit News Crawler")
        elif choice == '2':
            run_script("src/features/preprocessing.py", "Data Preprocessing")
            run_script("src/features/feature_engineering.py", "Feature Engineering (NLTK Sentiment)")
        elif choice == '3':
            run_script("src/models/ml_model.py", "Machine Learning Training")
        elif choice == '4':
            run_script("src/trading/strategy_event.py", "Event Reaction Strategy")
            run_script("src/trading/strategy_volatility.py", "Volatility Expansion Strategy")
            run_script("src/trading/strategy_mean_reversion.py", "Mean Reversion Strategy")
        elif choice == '5':
            print("\nStarting full pipeline execution...")
            run_script("src/data_collection/market_data_collector.py", "Market Data Collector")
            run_script("src/data_collection/reddit_finance_crawler.py", "Reddit News Crawler")
            run_script("src/features/preprocessing.py", "Data Preprocessing")
            run_script("src/features/feature_engineering.py", "Feature Engineering")
            run_script("src/models/ml_model.py", "Machine Learning Training")
            run_script("src/trading/strategy_event.py", "Event Reaction Strategy")
            run_script("src/trading/strategy_volatility.py", "Volatility Expansion Strategy")
            run_script("src/trading/strategy_mean_reversion.py", "Mean Reversion Strategy")
            print("\n🎉 FULL PIPELINE COMPLETED SUCCESSFULLY!")
        elif choice == '6':
            print("\nSpouštím grafické rozhraní...")
            run_script("src/gui/app.py", "Tkinter Desktop Application")
        elif choice == '0':
            print("Exiting program. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a number between 0 and 6.")

if __name__ == "__main__":
    main()
