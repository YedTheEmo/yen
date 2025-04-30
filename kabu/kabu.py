import os
import json
import yfinance as yf
from datetime import datetime

SNAPSHOT_DIR = "snapshots"
DEFAULT_TICKER_FILE = "tickers.txt"

PERCENT_MOVE_THRESHOLD = 5.0  # % movement threshold
VOLUME_MULTIPLIER_THRESHOLD = 1.5  # Volume spike threshold

def load_tickers(path):
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def fetch_latest_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty:
            return None
        return {
            "last_close": float(hist['Close'].iloc[-1]),
            "prev_close": float(hist['Close'].iloc[0]),
            "volume": int(hist['Volume'].iloc[-1]),
            "avg_volume": float(hist['Volume'].mean())
        }
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return None

def save_snapshot(ticker_list, path):
    snapshot = {}
    for ticker in ticker_list:
        data = fetch_latest_data(ticker)
        if data:
            snapshot[ticker] = data
    with open(path, 'w') as f:
        json.dump(snapshot, f, indent=2)
    print(f"Saved snapshot: {path}")

def save_report(report, path):
    with open(path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Saved report: {path}")

def compare_snapshots(prev_data, curr_data, tickers):
    report = []
    prev_tickers = set(prev_data.keys())
    curr_tickers = set(tickers)

    removed = prev_tickers - curr_tickers
    added = curr_tickers - prev_tickers
    common = prev_tickers & curr_tickers

    for ticker in common:
        old = prev_data[ticker]
        new = curr_data.get(ticker)
        if not new: continue

        pct_change = ((new['last_close'] - old['last_close']) / old['last_close']) * 100
        volume_ratio = new['volume'] / old['avg_volume'] if old['avg_volume'] else 0
        significant = abs(pct_change) >= PERCENT_MOVE_THRESHOLD or volume_ratio >= VOLUME_MULTIPLIER_THRESHOLD

        report.append({
            "ticker": ticker,
            "type": "tracked",
            "pct_change": round(pct_change, 2),
            "volume_ratio": round(volume_ratio, 2),
            "significant": significant,
            "status": "📈 Significant move!" if significant else "No major change"
        })

    for ticker in added:
        report.append({
            "ticker": ticker,
            "type": "added",
            "status": "🆕 Newly added to watchlist"
        })

    for ticker in removed:
        report.append({
            "ticker": ticker,
            "type": "removed",
            "status": "❌ Removed from watchlist"
        })

    return report

def kabu_main(ticker_file=None, compare_path=None, snapshot_only=False):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    ticker_path = ticker_file or DEFAULT_TICKER_FILE
    tickers = load_tickers(ticker_path)

    now = datetime.now().strftime("%Y-%m-%d")
    curr_snapshot_path = os.path.join(SNAPSHOT_DIR, f"{now}.json")
    report_path = os.path.join(SNAPSHOT_DIR, f"report_{now}.json")  # Save report separately

    # Fetch current data
    current_data = {}
    for ticker in tickers:
        data = fetch_latest_data(ticker)
        if data:
            current_data[ticker] = data

    if snapshot_only:
        save_snapshot(tickers, curr_snapshot_path)
        return

    if not compare_path or not os.path.exists(compare_path):
        print("Error: Previous snapshot not found.")
        return

    with open(compare_path, 'r') as f:
        previous_data = json.load(f)

    report = compare_snapshots(previous_data, current_data, tickers)

    # Save the structured report as JSON
    save_report(report, report_path)

    # Display results
    print("\n📊 Kabu Daily Roundup Report:")
    for r in report:
        line = f"{r['ticker']}: {r['status']}"
        if r.get("pct_change") is not None:
            line += f" | %Change: {r['pct_change']}% | Volume Ratio: {r['volume_ratio']}"
        print(line)

    save_snapshot(tickers, curr_snapshot_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Kabu: Daily price/volume movement roundup tool.")
    parser.add_argument("--tickers", help="Path to ticker list", default=DEFAULT_TICKER_FILE)
    parser.add_argument("--compare", help="Path to previous snapshot JSON")
    parser.add_argument("--snapshot-only", action="store_true", help="Only create a snapshot")
    args = parser.parse_args()

    kabu_main(ticker_file=args.tickers, compare_path=args.compare, snapshot_only=args.snapshot_only)

