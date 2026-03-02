import subprocess
import sys
import time

def run():
    print("Testing News Crawler")
    subprocess.run([sys.executable, "data_collector.py"])
    print("Testing Market Data Crawler")
    subprocess.run([sys.executable, "market_data_collector.py"])

if __name__ == "__main__":
    run()
