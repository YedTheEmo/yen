import yfinance as yf
import numpy as np
import pandas as pd
import requests
import argparse
import time
import os
import json
import sys
from datetime import datetime, timedelta
import random

# Constants
CACHE_FILE = "cached_tickers.json"
PROGRESS_FILE = "progress.txt"
DATA_CACHE_FILE = "stock_data_cache.json"
DEFAULT_OUTPUT_FILE = "summary.txt"

# Rate limiting configuration
MIN_DELAY = 0.1  # Minimum delay between requests
MAX_DELAY = 2.0  # Maximum delay for exponential backoff
BATCH_SIZE = 10  # Process in batches
BATCH_DELAY = 5  # Delay between batches
CACHE_EXPIRY_HOURS = 24  # Cache data for 24 hours

class RateLimitedStockScanner:
    def __init__(self):
        self.request_count = 0
        self.last_request_time = 0
        self.consecutive_errors = 0
        self.data_cache = self.load_cache()
        
    def load_cache(self):
        """Load cached stock data"""
        if os.path.exists(DATA_CACHE_FILE):
            try:
                with open(DATA_CACHE_FILE, "r") as f:
                    cache = json.load(f)
                # Clean expired entries
                current_time = datetime.now().timestamp()
                cache = {k: v for k, v in cache.items() 
                        if current_time - v.get('timestamp', 0) < CACHE_EXPIRY_HOURS * 3600}
                return cache
            except:
                return {}
        return {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(DATA_CACHE_FILE, "w") as f:
                json.dump(self.data_cache, f)
        except Exception as e:
            print(f"Warning: Could not save cache - {e}")
    
    def smart_delay(self):
        """Implement smart delay with exponential backoff"""
        current_time = time.time()
        
        # Base delay increases with consecutive errors
        base_delay = MIN_DELAY * (1.5 ** min(self.consecutive_errors, 5))
        
        # Add randomization to avoid thundering herd
        delay = base_delay + random.uniform(0, base_delay * 0.5)
        
        # Ensure minimum time between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Longer pause every batch
        if self.request_count % BATCH_SIZE == 0:
            print(f"Processed {self.request_count} requests. Taking batch break...")
            time.sleep(BATCH_DELAY)
    
    def get_cached_or_fetch(self, ticker, data_type, fetch_func, *args, **kwargs):
        """Get data from cache or fetch if not available/expired"""
        cache_key = f"{ticker}_{data_type}"
        current_time = datetime.now().timestamp()
        
        # Check if we have valid cached data
        if cache_key in self.data_cache:
            cached_data = self.data_cache[cache_key]
            if current_time - cached_data['timestamp'] < CACHE_EXPIRY_HOURS * 3600:
                print(f"{ticker}: Using cached {data_type}")
                return cached_data['data']
        
        # Fetch new data
        self.smart_delay()
        try:
            data = fetch_func(ticker, *args, **kwargs)
            
            # Cache the result
            self.data_cache[cache_key] = {
                'data': data,
                'timestamp': current_time
            }
            
            # Reset error counter on success
            self.consecutive_errors = 0
            
            return data
            
        except Exception as e:
            self.consecutive_errors += 1
            print(f"{ticker}: Error fetching {data_type} - {e}")
            
            # For rate limit errors, implement exponential backoff
            if "rate limit" in str(e).lower() or self.consecutive_errors >= 3:
                backoff_time = min(MAX_DELAY * (2 ** self.consecutive_errors), 60)
                print(f"Rate limit detected. Backing off for {backoff_time:.1f} seconds...")
                time.sleep(backoff_time)
            
            return None

def get_tickers(file_path=None):
    if file_path:
        if not os.path.exists(file_path):
            print(f"Error: The file '{file_path}' does not exist.")
            return []
        with open(file_path, 'r') as file:
            tickers = [line.strip() for line in file.readlines() if line.strip()]
        return tickers
    else:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        
        # Rate limit the SEC API call too
        time.sleep(1)
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; StockScanner/1.0)'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tickers = [item['ticker'] for item in data.values()]
                with open(CACHE_FILE, "w") as f:
                    json.dump(tickers, f)
                return tickers
            else:
                print(f"Error fetching ticker symbols from SEC: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching ticker symbols: {e}")
            return []

def calculate_volatility_safe(ticker, period="1y"):
    """Rate-limited volatility calculation"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None
        daily_returns = hist['Close'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252)
        return float(volatility) if not np.isnan(volatility) else None
    except Exception as e:
        print(f"Volatility calculation error for {ticker}: {e}")
        return None

def get_average_volume_safe(ticker, period="1y"):
    """Rate-limited average volume calculation"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None
        avg_volume = hist['Volume'].mean()
        return float(avg_volume) if not np.isnan(avg_volume) else None
    except Exception as e:
        print(f"Volume calculation error for {ticker}: {e}")
        return None

def get_institutional_ownership_safe(ticker):
    """Rate-limited institutional ownership calculation"""
    try:
        stock = yf.Ticker(ticker)
        holders = stock.institutional_holders
        if holders is None or holders.empty:
            return None
        
        total_shares_held = holders['Shares'].sum()
        info = stock.info
        shares_outstanding = info.get('sharesOutstanding')
        if shares_outstanding is None or shares_outstanding == 0:
            return None
        
        institutional_ownership = (total_shares_held / shares_outstanding) * 100
        return float(institutional_ownership) if not np.isnan(institutional_ownership) else None
    except Exception as e:
        print(f"Institutional ownership error for {ticker}: {e}")
        return None

def write_result(output_file, ticker, inst_ownership, volatility, avg_volume):
    write_header = not os.path.exists(output_file)
    with open(output_file, "a") as f:
        if write_header:
            f.write("Ticker\tInstitutional Ownership (%)\tVolatility\tAverage Daily Volume\n")
        f.write(f"{ticker}\t{inst_ownership:.2f}\t{volatility:.5f}\t{avg_volume:.0f}\n")

def main(min_institutional, min_volatility, min_volume, ticker_file=None, output_file=DEFAULT_OUTPUT_FILE, resume=False):
    scanner = RateLimitedStockScanner()
    
    tickers = get_tickers(ticker_file)
    if not tickers:
        print("No tickers retrieved. Exiting.")
        return

    print(f"Starting scan of {len(tickers)} tickers...")
    print(f"Filters: Institutional >= {min_institutional}%, Volatility >= {min_volatility}, Volume >= {min_volume:,}")
    print(f"Using cache expiry: {CACHE_EXPIRY_HOURS} hours")
    
    # Determine starting index
    start_index = 0
    if resume and os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            start_index = int(f.read().strip())
        print(f"Resuming from ticker {start_index + 1}")

    successful_scans = 0
    passed_filters = 0
    
    try:
        for idx in range(start_index, len(tickers)):
            ticker = tickers[idx].upper()
            print(f"\n[{idx + 1}/{len(tickers)}] Processing {ticker}...")
            
            # Get institutional ownership
            inst_ownership = scanner.get_cached_or_fetch(
                ticker, "institutional", get_institutional_ownership_safe
            )
            
            if inst_ownership is None or inst_ownership < min_institutional:
                print(f"{ticker}: Institutional ownership insufficient ({inst_ownership})")
                continue

            # Get volatility
            volatility = scanner.get_cached_or_fetch(
                ticker, "volatility", calculate_volatility_safe
            )
            
            if volatility is None or volatility < min_volatility:
                print(f"{ticker}: Volatility insufficient ({volatility})")
                continue

            # Get average volume
            avg_volume = scanner.get_cached_or_fetch(
                ticker, "volume", get_average_volume_safe
            )
            
            if avg_volume is None or avg_volume < min_volume:
                print(f"{ticker}: Volume insufficient ({avg_volume:,.0f})")
                continue

            # Ticker passed all filters
            write_result(output_file, ticker, inst_ownership, volatility, avg_volume)
            passed_filters += 1
            print(f"✅ {ticker}: PASSED all filters! ({inst_ownership:.1f}%, {volatility:.3f}, {avg_volume:,.0f})")

            successful_scans += 1
            
            # Save progress and cache periodically
            if idx % 10 == 0:
                scanner.save_cache()
                with open(PROGRESS_FILE, "w") as f:
                    f.write(str(idx + 1))
                print(f"Progress saved. Processed: {successful_scans}, Passed: {passed_filters}")

    except KeyboardInterrupt:
        print("\n🛑 Scan interrupted by user. Saving progress...")
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        
    finally:
        # Save final state
        scanner.save_cache()
        if 'idx' in locals():
            with open(PROGRESS_FILE, "w") as f:
                f.write(str(idx + 1))
        
        print(f"\n📊 Scan Summary:")
        print(f"Total processed: {successful_scans}")
        print(f"Passed all filters: {passed_filters}")
        print(f"Cache entries: {len(scanner.data_cache)}")
        print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock scanner with progress tracking and resume support.")
    parser.add_argument("min_institutional", type=float, help="Minimum institutional ownership percentage.")
    parser.add_argument("min_volatility", type=float, help="Minimum annualized volatility.")
    parser.add_argument("min_volume", type=int, help="Minimum average daily trading volume.")
    parser.add_argument("--ticker-file", type=str, help="Path to a text file containing ticker symbols.", default=None)
    parser.add_argument("--output-file", type=str, help="Path to the output file.", default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--resume", action="store_true", help="Resume scanning from last progress point.")
    args = parser.parse_args()

    main(args.min_institutional, args.min_volatility, args.min_volume, args.ticker_file, args.output_file, args.resume)
