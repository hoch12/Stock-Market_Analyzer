import sys
import subprocess
import time

def run_script(script_name, description):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {description} ({script_name})")
    print(f"{'='*60}")
    time.sleep(1)
    
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"✅ SUCCESS: {script_name} completed.")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {script_name} failed with exit code {e.returncode}.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find '{script_name}'. Are you in the right directory?")
        sys.exit(1)

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
        print("  5. 🚀 RUN ENTIRE PIPELINE (1 -> 4)")
        print("  0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == '1':
            run_script("market_data_collector.py", "Market Data Collector")
            run_script("reddit_finance_crawler.py", "Reddit News Crawler")
        elif choice == '2':
            run_script("preprocessing.py", "Data Preprocessing")
            run_script("feature_engineering.py", "Feature Engineering (NLTK Sentiment)")
        elif choice == '3':
            run_script("ml_model.py", "Machine Learning Training")
        elif choice == '4':
            run_script("strategy_event.py", "Event Reaction Strategy")
            run_script("strategy_volatility.py", "Volatility Expansion Strategy")
            run_script("strategy_mean_reversion.py", "Mean Reversion Strategy")
        elif choice == '5':
            print("\nStarting full pipeline execution...")
            run_script("market_data_collector.py", "Market Data Collector")
            run_script("reddit_finance_crawler.py", "Reddit News Crawler")
            run_script("preprocessing.py", "Data Preprocessing")
            run_script("feature_engineering.py", "Feature Engineering (NLTK Sentiment)")
            run_script("ml_model.py", "Machine Learning Training")
            run_script("strategy_event.py", "Event Reaction Strategy")
            run_script("strategy_volatility.py", "Volatility Expansion Strategy")
            run_script("strategy_mean_reversion.py", "Mean Reversion Strategy")
            print("\n🎉 FULL PIPELINE COMPLETED SUCCESSFULLY!")
        elif choice == '0':
            print("Exiting program. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a number between 0 and 5.")

if __name__ == "__main__":
    main()
