import yfinance as yf
import numpy as np
import pandas as pd
import requests
import argparse
import time
import os
import json
import sys

# Constants
CACHE_FILE = "cached_tickers.json"
PROGRESS_FILE = "progress.txt"
DEFAULT_OUTPUT_FILE = "summary.txt"


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
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            tickers = [item['ticker'] for item in data.values()]
            with open(CACHE_FILE, "w") as f:
                json.dump(tickers, f)
            return tickers
        else:
            print("Error fetching ticker symbols from SEC.")
            return []


def calculate_volatility(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        return None
    daily_returns = hist['Close'].pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252)
    return volatility


def get_average_volume(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        return None
    avg_volume = hist['Volume'].mean()
    return avg_volume


def get_institutional_ownership(ticker):
    stock = yf.Ticker(ticker)
    holders = stock.institutional_holders
    if holders is None or holders.empty:
        return None
    total_shares_held = holders['Shares'].sum()
    info = stock.info
    shares_outstanding = info.get('sharesOutstanding')
    if shares_outstanding is None:
        return None
    institutional_ownership = (total_shares_held / shares_outstanding) * 100
    return institutional_ownership


def write_result(output_file, ticker, inst_ownership, volatility, avg_volume):
    write_header = not os.path.exists(output_file)
    with open(output_file, "a") as f:
        if write_header:
            f.write("Ticker\tInstitutional Ownership (%)\tVolatility\tAverage Daily Volume\n")
        f.write(f"{ticker}\t{inst_ownership:.2f}\t{volatility:.5f}\t{avg_volume:.0f}\n")


def main(min_institutional, min_volatility, min_volume, ticker_file=None, output_file=DEFAULT_OUTPUT_FILE, resume=False):
    tickers = get_tickers(ticker_file)
    if not tickers:
        print("No tickers retrieved. Exiting.")
        return

    # Determine starting index
    start_index = 0
    if resume and os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            start_index = int(f.read().strip())

    for idx in range(start_index, len(tickers)):
        ticker = tickers[idx]
        print(f"Processing {ticker} ({idx + 1}/{len(tickers)})...")
        try:
            inst_ownership = get_institutional_ownership(ticker)
            if inst_ownership is None or inst_ownership < min_institutional:
                print(f"{ticker}: Institutional ownership below threshold or data unavailable.")
                continue

            volatility = calculate_volatility(ticker)
            if volatility is None or volatility < min_volatility:
                print(f"{ticker}: Volatility below threshold or data unavailable.")
                continue

            avg_volume = get_average_volume(ticker)
            if avg_volume is None or avg_volume < min_volume:
                print(f"{ticker}: Average trading volume below threshold or data unavailable.")
                continue

            write_result(output_file, ticker, inst_ownership, volatility, avg_volume)
            print(f"{ticker}: Passed all filters. Written to {output_file}.")
            time.sleep(0.05)

        except yf.YFRateLimitError:
            print("Rate limit hit. Saving progress and exiting...")
            with open(PROGRESS_FILE, "w") as f:
                f.write(str(idx))
            sys.exit(0)

        except Exception as e:
            print(f"{ticker}: Error occurred - {e}")
            continue

        # Save progress index
        with open(PROGRESS_FILE, "w") as f:
            f.write(str(idx + 1))

    print("\nScan complete.")


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
