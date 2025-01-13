# YEN | VPA (Volume Price Analysis) Llama Integration

This repository provides a tool for fetching stock data, generating analysis prompts, and using the Ollama model to perform Volume Price Analysis (VPA). It can analyze stock data over different time intervals (1-hour, 1-day, 1-week), generate detailed VPA reports, and convert them into HTML format for easy sharing and documentation.

## Features
- **Stock Data Fetching**: Retrieves stock data for given ticker symbols and intervals from Yahoo Finance.
- **VPA Prompt Generation**: Generates detailed prompts for Volume Price Analysis based on stock data, focusing on patterns such as volume spikes, price reversals, support/resistance levels, etc.
- **Ollama Model Integration**: Sends the generated prompts to the Ollama model (Llama 3.2) to get detailed analysis and recommendations.
- **Report Generation**: Converts the analysis from Ollama into a Markdown report, which is then converted to HTML for easy use and sharing.

## Installation Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/HawtStrokes/yen.git
   cd yen
   ```

2. **Create a Virtual Environment (Optional, but Recommended)**
   If you prefer to work with a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```

3. **Install the Dependencies**
   Make sure you have `pip` installed, and then run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama**
   Ollama is a local AI model that powers the analysis. You can install it by following the instructions on the [Ollama website](https://ollama.com/). After installation, ensure that the `ollama` command is accessible in your system's PATH.

## Usage Instructions

1. **Run the Script to Fetch Data and Generate Reports**

   You can run the script using the following command:
   ```bash
   python main.py <TICKER> <START_DATE> <END_DATE> --intervals <INTERVALS>
   ```

   - `<TICKER>`: The stock ticker symbol (e.g., `AAPL`).
   - `<START_DATE>`: The start date for the data (format: `YYYY-MM-DD`).
   - `<END_DATE>`: The end date for the data (format: `YYYY-MM-DD`).
   - `--intervals`: Optional. List of candlestick intervals. Default is `1wk 1d 1h`.

   Example:
   ```bash
   python main.py AAPL 2023-01-01 2023-12-31 --intervals 1h 1d 1wk
   ```

2. **Using a File with Multiple Tickers**

   You can also provide a file containing a list of ticker symbols, one per line:
   ```bash
   python main.py --file tickers.txt 2023-01-01 2023-12-31 --intervals 1h 1d 1wk
   ```

3. **Output**
   After running the script, the tool will generate an HTML report with the analysis for each interval. The HTML file will be saved in the `reports/` directory with the following naming convention:
   ```
   vpa_analysis_<TICKER>_<START_DATE>_<END_DATE>_<INTERVALS>.html
   ```

   This file can be opened in any browser, and the contents can be copied and pasted into Word or other document formats.

## Token Limitations and Considerations

- This integration uses the Ollama Llama 3.2 model, which may have its own token and usage limits.
- The script will handle large data sets by splitting the analysis into smaller chunks for each interval.
- Ensure that the `ollama` command is accessible in your system's PATH.
