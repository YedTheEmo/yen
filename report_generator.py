import argparse
import yfinance as yf
import markdown
import json
import os
import time
import ollama

# Function to fetch stock data for given intervals
def fetch_data(ticker, start_date, end_date, intervals):
    data = {}
    for interval in intervals:
        data[interval] = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    return data

# Function to generate a prompt for the model based on interval data
def generate_prompt(interval, data):
    prompt = (
        f"You are a Volume Price Analysis expert. Analyze the following {interval} interval data for anomalies, confirmations, and volume-price relationships.\n"
        "Look for patterns such as volume spikes, price reversals, support/resistance levels, bear/bull traps, accumulation, distribution, stopping volume, "
        "and trend confirmations. Provide recommendations on entry and position.\n"
        "Provide your response in Markdown format with bullet points and headings.\n\n"
        f"{interval} Data:\n{data.to_string()}\n\n"
        "Provide a detailed analysis."
    )
    return prompt

# Function to generate a summary prompt based on multiple intervals
def generate_summary_prompt(intervals):
    prompt = (
        "You are a Volume Price Analysis expert. Based on the analyses of the following intervals, provide a consolidated summary:\n\n"
        f"Intervals analyzed: {', '.join(intervals)}\n\n"
        "Summarize the key insights, overarching patterns, and recommendations from all intervals. Provide your response in Markdown format."
    )
    return prompt

# Function to call the Ollama model and get a response
def call_ollama(prompt, model='llama3.2'):
    response = ollama.chat(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant and Volume Price Analysis expert.'},
            {'role': 'user', 'content': prompt}
        ],
#        temperature=temperature
    )
    return response['message']['content']

# Function to convert Markdown text to HTML
def markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)

# Function to save the HTML report to a file
def save_html_report(html_content, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html_content)

# Main function to orchestrate the data fetching, analysis, and report generation

def main():
    parser = argparse.ArgumentParser(description="Fetch VPA data and generate a prompt for analysis.")
    parser.add_argument("ticker", nargs="?", help="The stock ticker symbol (e.g., AAPL).")
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD).")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD).")
    parser.add_argument("--intervals", nargs="*", default=["1wk", "1d", "1h"],
                        help="Candlestick intervals (default: 1wk, 1d, 1h).")
    parser.add_argument("--file", type=argparse.FileType('r'),
                        help="File containing a list of ticker symbols, one per line.")

    args = parser.parse_args()

    if args.file:
        tickers = [line.strip() for line in args.file.readlines()]
    elif args.ticker:
        tickers = [args.ticker]
    else:
        print("Please provide either a ticker symbol or a file containing ticker symbols.")
        return

    for ticker in tickers:
        print(f"Processing {ticker}...")
        data = fetch_data(ticker, args.start_date, args.end_date, args.intervals)

        markdown_responses = []
        for interval in args.intervals:
            interval_data = data.get(interval)
            if interval_data is not None and not interval_data.empty:
                prompt = generate_prompt(interval, interval_data)
                analysis = call_ollama(prompt)
                markdown_responses.append(f"## Analysis for {interval} Interval\n\n{analysis}\n")
            else:
                print(f"No data found for interval {interval}. Skipping.")

        summary_prompt = generate_summary_prompt(args.intervals)
        summary = call_ollama(summary_prompt)
        markdown_responses.append(f"## Consolidated Summary\n\n{summary}\n")

        combined_markdown = f"# VPA Analysis for {ticker}\n\n" + "\n".join(markdown_responses)
        html_report = markdown_to_html(combined_markdown)

        output_file = f"reports/vpa_analysis_{ticker}_{args.start_date}_{args.end_date}_{'_'.join(args.intervals)}.html"
        save_html_report(html_report, output_file)

        print(f"HTML report saved as: {output_file}")

if __name__ == "__main__":
    main()
