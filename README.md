# YEN | VPA Prompt and Report Generator

A tool for fetching Volume Price Analysis (VPA) data, generating prompts for analysis, and producing reports with the help of OpenAI’s GPT models. It allows you to analyze stock data over different time intervals (1-hour, 1-day, 1-week) and generate reports that are formatted in Markdown and HTML.

## Features
- **Prompt Generator**: Fetches stock data from Yahoo Finance and creates a prompt for GPT to analyze the data based on volume-price relationships and other VPA criteria.
- **Report Generator**: Converts the GPT-generated analysis into a Markdown report and then converts it into HTML for easy copy-paste into Word or other document formats.

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

   Make sure you have pip installed, and then run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a config.json File**

   Create a `config.json` file in the root directory of this repository with your OpenAI API key:
   ```json
   {
       "openai_api_key": "<YOUR API KEY>"
   }
   ```
   Note: Replace `<YOUR API KEY>` with your actual OpenAI API key. This is required to interact with the OpenAI API.

## Usage Instructions

Run the Script to Fetch Data and Generate Reports

The script can be run with the following command:
```bash
python main.py <TICKER> <START_DATE> <END_DATE> --intervals <INTERVALS>
```
- `<TICKER>`: The stock ticker symbol (e.g., AAPL).
- `<START_DATE>`: The start date for the data (format: YYYY-MM-DD).
- `<END_DATE>`: The end date for the data (format: YYYY-MM-DD).
- `--intervals`: Optional. List of candlestick intervals. Default is `1h 1d 1wk`.

Example:
```bash
python main.py AAPL 2023-01-01 2023-12-31 --intervals 1h 1d 1wk
```

## Output

The script will generate a report in HTML format and save it with the following naming convention:
```php
vpa_analysis_<TICKER>_<START_DATE>_<END_DATE>.html
```
This file can be opened in any browser, and you can copy and paste the contents into a Word document.

## Token Limit and Considerations

The OpenAI models used have token limits, which may affect the amount of data you can process in one request.
- **GPT-3.5 (4096 tokens)**: The model has a token limit of 4096 tokens (input + output). If the token limit is exceeded, the input will need to be shortened.
- **GPT-4**: You can use GPT-4 models with token limits up to 32K tokens, but ensure you are using the correct model version and that your OpenAI API key supports this.

Important: This project uses the OpenAI API, so ensure that you have an active API key in your `config.json` file.
