import argparse
import yfinance as yf
import sys

def get_company_description(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    try:
        summary = ticker.info.get("longBusinessSummary")
        return summary if summary else "No description available."
    except Exception as e:
        return f"[ERROR] Could not fetch data for {ticker_symbol}: {e}"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch company descriptions from Yahoo Finance using yfinance."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ticker', type=str, help='Single ticker symbol (e.g., AAPL)')
    group.add_argument('--tickers', nargs='+', help='List of ticker symbols (e.g., AAPL MSFT GOOGL)')
    group.add_argument('--ticker-file', type=str, help='Path to a file with ticker symbols, one per line')
    parser.add_argument('--output', type=str, help='Path to save output as plain text')
    return parser.parse_args()

def load_tickers_from_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        sys.exit(f"[ERROR] Failed to read ticker file: {e}")

def main():
    args = parse_args()

    if args.ticker:
        tickers = [args.ticker]
    elif args.tickers:
        tickers = args.tickers
    elif args.ticker_file:
        tickers = load_tickers_from_file(args.ticker_file)
    else:
        sys.exit("[ERROR] No valid ticker input method provided.")

    output_lines = []
    for symbol in tickers:
        header = f"\n=== {symbol.upper()} ==="
        description = get_company_description(symbol)
        print(header)
        print(description)
        output_lines.append(header)
        output_lines.append(description)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write("\n".join(output_lines))
            print(f"\n[✔] Output saved to {args.output}")
        except Exception as e:
            sys.exit(f"[ERROR] Could not write to output file: {e}")

if __name__ == "__main__":
    main()

