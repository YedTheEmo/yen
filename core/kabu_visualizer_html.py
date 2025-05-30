# core/kabu_visualizer_html.py

import json
import argparse
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kabu Report – {report_date}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
        h1  {{ text-align: center; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }}
        .tile {{ background: white; border-radius: 12px; padding: 15px;
                  box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: flex;
                  flex-direction: column; justify-content: space-between; }}
        .ticker {{ font-weight: bold; font-size: 1.2em; }}
        .positive {{ color: green; }}
        .negative {{ color: red; }}
        .neutral  {{ color: #999; }}
        .meta     {{ margin-top: 8px; font-size: 0.9em; }}
        .status   {{ margin-top: 10px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Kabu Report – {report_date}</h1>
    <div class="grid">
        {tiles}
    </div>
</body>
</html>
"""

def generate_tile(entry):
    ticker       = entry['ticker']
    status       = entry['status']
    type_        = entry.get('type', 'tracked')
    pct_change   = entry.get('pct_change', 0.0)
    volume_ratio = entry.get('volume_ratio', 0.0)
    significant  = entry.get('significant', False)

    if type_ == 'added':
        color_class = "neutral"
        content = f"""
            <div class="ticker">🆕 {ticker}</div>
            <div class="status">{status}</div>
        """
    elif type_ == 'removed':
        color_class = "neutral"
        content = f"""
            <div class="ticker">❌ {ticker}</div>
            <div class="status">{status}</div>
        """
    else:
        color_class = "positive" if pct_change > 0 else "negative"
        sig_marker  = "📈" if significant else "〰️"
        content = f"""
            <div class="ticker {color_class}">{sig_marker} {ticker}</div>
            <div class="meta {color_class}">{pct_change:+.2f}% | Vol x{volume_ratio:.2f}</div>
            <div class="status">{status}</div>
        """

    return f'<div class="tile">{content}</div>'

def generate_html(report, entries, output_file):
    report_date = report.get("comparison_date", 
                     datetime.now().strftime("%Y-%m-%d"))
    tiles = "\n".join(generate_tile(e) for e in entries)
    html  = HTML_TEMPLATE.format(report_date=report_date, tiles=tiles)

    with open(output_file, 'w') as f:
        f.write(html)
    print(f"✅ HTML report written to {output_file}")

def kabu_visualizer_html(report_file, output_file):
    # 1. Load the full report dict
    with open(report_file, 'r') as f:
        report = json.load(f)

    entries = []

    # 2. Added tickers
    for t in report.get("added_tickers", []):
        entries.append({
            "ticker": t,
            "status": "Added to watchlist",
            "type":   "added"
        })

    # 3. Movements for tracked tickers
    for m in report.get("movements", []):
        entries.append({
            "ticker":       m["ticker"],
            "status":       m["status"],
            "type":         "tracked",
            "pct_change":   m["daily_change_pct"],
            "volume_ratio": m["volume_ratio_30d"],
            "significant":  m.get("significant", False)
        })

    # 4. Removed tickers
    for t in report.get("removed_tickers", []):
        entries.append({
            "ticker": t,
            "status": "Removed from watchlist",
            "type":   "removed"
        })

    # 5. Render HTML
    generate_html(report, entries, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kabu HTML visualizer")
    parser.add_argument("--report", required=True, help="Path to JSON report file")
    parser.add_argument("--output", required=True, help="Output HTML file")
    args = parser.parse_args()

    kabu_visualizer_html(report_file=args.report, output_file=args.output)

