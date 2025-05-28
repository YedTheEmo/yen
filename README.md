# YEN | Unified Stock Analysis Workflow Manager

A comprehensive Python-based stock analysis suite that combines Volume Spread Analysis (VSA), volume anomaly detection, AI-powered reporting, and stock screening into unified workflows. YEN eliminates the complexity of managing individual analysis scripts by providing predefined workflows that chain together multiple analysis tools.

## Features

### Core Workflows
- **VSA Analysis Pipeline**: Complete Volume Spread Analysis with data export, cleaning, and visualization
- **Volume Anomaly Detection**: Statistical analysis to identify unusual volume patterns
- **AI-Powered Analysis**: Generate comprehensive analysis reports using OpenAI's GPT models
- **Stock Screening**: Filter stocks by institutional ownership, volatility, and volume criteria
- **Batch Processing**: Process multiple tickers through any workflow
- **Daily Market Roundup**: Real-time price/volume movement tracking with Kabu

### Analysis Tools
- **Volume Spread Analysis (VSA)**: Detect high-probability trading signals based on volume-price relationships
- **Statistical Anomaly Detection**: Z-score based volume anomaly identification
- **Technical Data Export**: Multi-timeframe OHLCV data extraction from Yahoo Finance
- **Data Cleaning & Preprocessing**: Automated CSV cleaning and formatting
- **Interactive Visualizations**: Plot generation for signals and anomalies

## Project Structure

```
yen/
├── yen.py                     # Main workflow manager
├── core/                       # Core analysis scripts
│   ├── data_exporter.py       # OHLCV data fetching from Yahoo Finance
│   ├── clean_csv_data.py      # CSV data cleaning and preprocessing
│   ├── vsa.py                 # Volume Spread Analysis engine
│   ├── detect_volume_anomalies.py  # Statistical volume anomaly detection
│   ├── report_generator.py    # AI-powered analysis report generation
│   ├── stock_scanner.py       # Stock screening by fundamental criteria
│   ├── prompt_generator.py    # VPA analysis prompt generation
│   ├── prompt_generator_v2.py # Multi-ticker prompt generation
│   ├── txt_to_csv.py         # Data format conversion utility
│   ├── kabu.py               # Daily price/volume movement tracker
│   ├── kabu_visualizer.py    # PNG visualization generator
│   └── kabu_visualizer_html.py # HTML report generator
├── data_exports/             # Exported CSV data storage
├── vsa_outputs/             # VSA analysis results
└── requirements.txt         # Python dependencies
```

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://www.github.com/YedTheEmo/yen.git
   cd yen
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure OpenAI API (Optional)**
   For AI-powered analysis, create `config.json`:
   ```json
   {
       "openai_api_key": "your-openai-api-key-here"
   }
   ```

## Usage Examples

### VSA Analysis Pipeline
Complete Volume Spread Analysis with visualization:
```bash
python yen.py vsa-analysis AAPL 2024-01-01 2024-12-31 --plot --threshold 1.0
```

### Volume Anomaly Detection
Detect unusual volume patterns:
```bash
python yen.py volume-anomalies TSLA 2024-01-01 2024-12-31 --threshold 2.0
```

### AI-Powered Analysis Report
Generate comprehensive AI analysis:
```bash
python yen.py ai-analysis NVDA 2024-01-01 2024-12-31 --intervals 1wk 1d 1h
```

### Complete Analysis Suite
Run all analyses in sequence:
```bash
python yen.py full-analysis MSFT 2024-01-01 2024-12-31
```

### Stock Screening
Filter stocks by criteria:
```bash
python yen.py stock-screening 10.0 0.3 1000000 --output-file filtered_stocks.txt
```

### Batch Processing
Process multiple tickers from file:
```bash
python yen.py batch-analysis tickers.txt 2024-01-01 2024-12-31 vsa --plot
```

### Daily Market Roundup (Kabu)
Generate daily price/volume summary:
```bash
python kabu/kabu.py --tickers tickers.txt
python kabu/kabu_visualizer_html.py --report daily_report.json --output daily_report.html
```

## 🔧 Individual Script Usage

### Data Export
```bash
python yen/data_exporter.py AAPL 2024-01-01 2024-12-31 --intervals 1d 1h
```

### VSA Analysis
```bash
python yen/vsa.py -f data.csv -t 1.0 0.5 -p -d 5
```

### Volume Anomaly Detection
```bash
python yen/detect_volume_anomalies.py input.csv output.csv --threshold 2.0
```

### Stock Screening
```bash
python yen/stock_scanner.py 10.0 0.3 1000000 --ticker-file sp500.txt --resume
```

## Workflow Details

### VSA Analysis Pipeline
1. **Data Export**: Fetch OHLCV data from Yahoo Finance
2. **Data Cleaning**: Remove headers and handle missing data
3. **VSA Analysis**: Apply Volume Spread Analysis algorithms
4. **Visualization**: Generate signal plots and charts

### Volume Anomaly Detection
1. **Data Export & Cleaning**: Prepare clean OHLCV dataset
2. **Statistical Analysis**: Calculate volume z-scores
3. **Anomaly Identification**: Flag volumes exceeding threshold
4. **Report Generation**: Export anomaly summary to CSV

### AI Analysis Workflow
1. **Data Collection**: Multi-timeframe data aggregation
2. **Prompt Generation**: Create structured analysis prompts
3. **AI Processing**: Send to OpenAI API for analysis
4. **Report Formatting**: Generate HTML/Markdown reports

## Requirements

- Python 3.7+
- pandas
- numpy
- yfinance
- matplotlib
- requests
- openai (for AI analysis)

## Use Cases

- **Day Trading**: VSA signal detection for intraday opportunities
- **Swing Trading**: Multi-timeframe analysis for position entries
- **Risk Management**: Volume anomaly alerts for unusual market activity
- **Portfolio Screening**: Filter stocks by fundamental and technical criteria
- **Market Research**: AI-powered analysis of market trends and patterns
- **Daily Monitoring**: Automated daily market roundup and alerts

## Important Notes

- **API Limits**: OpenAI API usage incurs costs based on token consumption
- **Data Sources**: Uses Yahoo Finance via yfinance library
- **File Management**: Temporary files are automatically cleaned up
- **Error Handling**: Graceful failure recovery with detailed error messages
- **Resume Support**: Stock screening supports resume functionality for large datasets

## Troubleshooting

### Argument Order Issues
Always place optional arguments after positional arguments:
```bash
# Correct
python yen.py vsa-analysis AAPL 2024-01-01 2024-12-31 --intervals 1d

# Incorrect
python yen.py vsa-analysis --intervals 1d AAPL 2024-01-01 2024-12-31
```

### Missing Config File
If `report_generator.py` fails, ensure `config.json` exists with your OpenAI API key.

### Data Export Issues
Check internet connectivity and verify ticker symbols are valid.

---

**YEN** - Your comprehensive toolkit for professional stock market analysis and trading signal generation.
