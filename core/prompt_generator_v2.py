import argparse
import yfinance as yf
import markdown
import tiktoken
import json
import os

def fetch_data(ticker, start_date, end_date, intervals):
    data = {}
    for interval in intervals:
        data[interval] = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    return data

def generate_prompt(interval, data):
    prompt = (
        f"You are a Volume Price Analysis expert. Analyze the following {interval} interval data for anomalies, confirmations, and volume-price relationships.\n"
        "Look for patterns such as volume spikes, price reversals, support/resistance levels, bear/bull traps, accumulation, distribution, stopping volume, "
        "and trend confirmations. Provide recommendations on entry and position.\n\n"
        f"{interval} Data:\n{data.to_string()}\n\n"
        "Make the analysis as detailed as possible."
    )
    return prompt

def generate_summary_prompt(intervals):
    prompt = (
        "You are a Volume Price Analysis expert. Based on the analyses of the following intervals, provide a consolidated summary:\n\n"
        f"Intervals analyzed: {', '.join(intervals)}\n\n"
        "Summarize the key insights, overarching patterns, and recommendations from all intervals."
    )
    return prompt

def get_token_count(prompt):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(prompt))

def markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)

def save_html_report(html_content, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html_content)

def process_ticker(ticker, start_date, end_date, intervals):
    data = fetch_data(ticker, start_date, end_date, intervals)
    
    # Generate and collect prompts for each interval
    markdown_responses = []
    for interval in intervals:
        interval_data = data.get(interval)
        if interval_data is not None and not interval_data.empty:
            prompt = generate_prompt(interval, interval_data)
            markdown_responses.append(f"## Prompt for {interval} Interval\n\n{prompt}\n")
        else:
            print(f"No data found for interval {interval}. Skipping.")
    
    # Generate summary prompt
    summary_prompt = generate_summary_prompt(intervals)
    markdown_responses.append(f"## Consolidated Summary Prompt\n\n{summary_prompt}\n")
    
    # Combine all Markdown responses
    combined_markdown = f"# VPA Analysis Prompts for {ticker}\n\n" + "\n".join(markdown_responses)
    
    # Convert to HTML
    html_report = markdown_to_html(combined_markdown)
    
    # Save HTML report
    output_file = f"prompts/vpa_analysis_prompts_{ticker}_{start_date}_{end_date}_{'_'.join(intervals)}.html"
    save_html_report(html_report, output_file)
    
    print(f"\nHTML prompts saved as: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Fetch VPA data and generate a prompt for analysis.")
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD).")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD).")
    parser.add_argument("--intervals", nargs="*", default=["1wk", "1d", "1h"], 
                        help="Candlestick intervals (default: 1wk, 1d, 1h).")
    parser.add_argument("--tickers_file", help="File containing a list of tickers (one per line).")
    parser.add_argument("--tickers", nargs="*", help="A list of ticker symbols (e.g., AAPL, GOOG).")

    args = parser.parse_args()

    tickers = []

    if args.tickers_file:
        # Read tickers from file
        with open(args.tickers_file, 'r') as f:
            tickers = [line.strip() for line in f.readlines()]
    
    if args.tickers:
        tickers.extend(args.tickers)

    if not tickers:
        print("No tickers provided. Exiting.")
        return
    
    # Process each ticker
    for ticker in tickers:
        process_ticker(ticker, args.start_date, args.end_date, args.intervals)

if __name__ == "__main__":
    main()
import argparse
import yfinance as yf
import markdown
import tiktoken
import json
import os

def fetch_data(ticker, start_date, end_date, intervals):
    data = {}
    for interval in intervals:
        data[interval] = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    return data

def generate_prompt(interval, data):
    prompt = (
        f"You are a Volume Price Analysis expert. Analyze the following {interval} interval data for anomalies, confirmations, and volume-price relationships.\n"
        "Look for patterns such as volume spikes, price reversals, support/resistance levels, bear/bull traps, accumulation, distribution, stopping volume, "
        "and trend confirmations. Provide recommendations on entry and position.\n\n"
        f"{interval} Data:\n{data.to_string()}\n\n"
        "Make the analysis as detailed as possible."
    )
    return prompt

def generate_summary_prompt(intervals):
    prompt = (
        "You are a Volume Price Analysis expert. Based on the analyses of the following intervals, provide a consolidated summary:\n\n"
        f"Intervals analyzed: {', '.join(intervals)}\n\n"
        "Summarize the key insights, overarching patterns, and recommendations from all intervals."
    )
    return prompt

def get_token_count(prompt):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(prompt))

def markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)

def save_html_report(html_content, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html_content)

def process_ticker(ticker, start_date, end_date, intervals):
    data = fetch_data(ticker, start_date, end_date, intervals)
    
    # Generate and collect prompts for each interval
    markdown_responses = []
    for interval in intervals:
        interval_data = data.get(interval)
        if interval_data is not None and not interval_data.empty:
            prompt = generate_prompt(interval, interval_data)
            markdown_responses.append(f"## Prompt for {interval} Interval\n\n{prompt}\n")
        else:
            print(f"No data found for interval {interval}. Skipping.")
    
    # Generate summary prompt
    summary_prompt = generate_summary_prompt(intervals)
    markdown_responses.append(f"## Consolidated Summary Prompt\n\n{summary_prompt}\n")
    
    # Combine all Markdown responses
    combined_markdown = f"# VPA Analysis Prompts for {ticker}\n\n" + "\n".join(markdown_responses)
    
    # Convert to HTML
    html_report = markdown_to_html(combined_markdown)
    
    # Save HTML report
    output_file = f"prompts/vpa_analysis_prompts_{ticker}_{start_date}_{end_date}_{'_'.join(intervals)}.html"
    save_html_report(html_report, output_file)
    
    print(f"\nHTML prompts saved as: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Fetch VPA data and generate a prompt for analysis.")
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD).")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD).")
    parser.add_argument("--intervals", nargs="*", default=["1wk", "1d", "1h"], 
                        help="Candlestick intervals (default: 1wk, 1d, 1h).")
    parser.add_argument("--tickers_file", help="File containing a list of tickers (one per line).")
    parser.add_argument("--tickers", nargs="*", help="A list of ticker symbols (e.g., AAPL, GOOG).")

    args = parser.parse_args()

    tickers = []

    if args.tickers_file:
        # Read tickers from file
        with open(args.tickers_file, 'r') as f:
            tickers = [line.strip() for line in f.readlines()]
    
    if args.tickers:
        tickers.extend(args.tickers)

    if not tickers:
        print("No tickers provided. Exiting.")
        return
    
    # Process each ticker
    for ticker in tickers:
        process_ticker(ticker, args.start_date, args.end_date, args.intervals)

if __name__ == "__main__":
    main()

