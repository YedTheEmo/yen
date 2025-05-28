import yfinance as yf
import argparse
import os
import pandas as pd

def fetch_data(ticker, start_date, end_date, intervals):
    data = {}
    for interval in intervals:
        data[interval] = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    return data

def save_data_to_csv(data, ticker, start_date, end_date, intervals):
    os.makedirs("data_exports", exist_ok=True)
    
    for interval in intervals:
        df = data.get(interval)
        if df is not None and not df.empty:
            filename = f"data_exports/{ticker}_{start_date}_{end_date}_{interval}.csv"
            df.to_csv(filename)
            print(f"Data saved for {interval} interval: {filename}")
        else:
            print(f"No data for {interval} interval. Skipping.")

def main():
    parser = argparse.ArgumentParser(description="Fetch stock data and export to CSV.")
    parser.add_argument("ticker", help="The stock ticker symbol (e.g., AAPL).")
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD).")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD).")
    parser.add_argument("--intervals", nargs="*", default=["1wk", "1d", "1h"], 
                        help="Candlestick intervals (default: 1wk, 1d, 1h).")
    
    args = parser.parse_args()

    # Fetch stock data
    data = fetch_data(args.ticker, args.start_date, args.end_date, args.intervals)
    
    # Save data to CSV
    save_data_to_csv(data, args.ticker, args.start_date, args.end_date, args.intervals)

if __name__ == "__main__":
    main()

