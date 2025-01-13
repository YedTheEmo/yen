import argparse
import yfinance as yf
import markdown
import tiktoken
import json
import os

# Load OpenAI API key from config file (no longer needed for this version)
with open("config.json", "r") as f:
    config = json.load(f)

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

def main():
    parser = argparse.ArgumentParser(description="Fetch VPA data and generate a prompt for analysis.")
    parser.add_argument("ticker", help="The stock ticker symbol (e.g., AAPL).")
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD).")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD).")
    parser.add_argument("--intervals", nargs="*", default=["1wk", "1d", "1h"], 
                        help="Candlestick intervals (default: 1wk, 1d, 1h).")

    args = parser.parse_args()
    
    # Fetch data
    data = fetch_data(args.ticker, args.start_date, args.end_date, args.intervals)
    
    # Generate and collect prompts for each interval
    markdown_responses = []
    for interval in args.intervals:
        interval_data = data.get(interval)
        if interval_data is not None and not interval_data.empty:
            prompt = generate_prompt(interval, interval_data)
            markdown_responses.append(f"## Prompt for {interval} Interval\n\n{prompt}\n")
        else:
            print(f"No data found for interval {interval}. Skipping.")
    
    # Generate summary prompt
    summary_prompt = generate_summary_prompt(args.intervals)
    markdown_responses.append(f"## Consolidated Summary Prompt\n\n{summary_prompt}\n")
    
    # Combine all Markdown responses
    combined_markdown = f"# VPA Analysis Prompts for {args.ticker}\n\n" + "\n".join(markdown_responses)
    
    # Convert to HTML
    html_report = markdown_to_html(combined_markdown)
    
    # Save HTML report
    output_file = f"prompts/vpa_analysis_prompts_{args.ticker}_{args.start_date}_{args.end_date}_{'_'.join(args.intervals)}.html"
    save_html_report(html_report, output_file)
    
    print(f"\nHTML prompts saved as: {output_file}")

if __name__ == "__main__":
    main()
