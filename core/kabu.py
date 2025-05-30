#!/usr/bin/env python3
"""
KABU - Daily Stock Movement Monitor

This module handles monitoring and visualization of price movements of tracked stocks.
Tracks daily price changes, volume spikes, and generates comparison reports.
"""

import os
import json
import yfinance as yf
from datetime import datetime, timedelta
import argparse

# Configuration
SNAPSHOT_DIR = "kabu_snapshots"
DEFAULT_TICKER_FILE = "watchlist_stocks.txt"
PERCENT_MOVE_THRESHOLD = 5.0  # % movement threshold for significance
VOLUME_MULTIPLIER_THRESHOLD = 2.0  # Volume spike threshold

def load_tickers(path):
    """Load ticker symbols from file with validation"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ticker file not found: {path}")
    
    with open(path, 'r') as f:
        tickers = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
    
    if not tickers:
        raise ValueError(f"No valid tickers found in {path}")
    
    print(f"Loaded {len(tickers)} tickers from {path}")
    return tickers

def fetch_stock_data(ticker, days=30):
    """
    Fetch stock data with proper error handling
    Returns current day data plus historical averages
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{days}d")
        
        if hist.empty or len(hist) < 2:
            print(f"⚠️  Insufficient data for {ticker}")
            return None
        
        # Get the most recent complete trading day data
        current_data = hist.iloc[-1]
        previous_data = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
        
        # Calculate averages
        avg_volume_30d = float(hist['Volume'][-min(30, len(hist)):].mean())
        avg_volume_5d = float(hist['Volume'][-min(5, len(hist)):].mean())
        
        return {
            "ticker": ticker,
            "date": current_data.name.strftime("%Y-%m-%d"),
            "current_close": float(current_data['Close']),
            "previous_close": float(previous_data['Close']),
            "current_volume": int(current_data['Volume']),
            "high": float(current_data['High']),
            "low": float(current_data['Low']),
            "avg_volume_30d": avg_volume_30d,
            "avg_volume_5d": avg_volume_5d,
            "daily_change_pct": ((current_data['Close'] - previous_data['Close']) / previous_data['Close']) * 100,
            "volume_ratio_30d": current_data['Volume'] / avg_volume_30d if avg_volume_30d > 0 else 0,
            "volume_ratio_5d": current_data['Volume'] / avg_volume_5d if avg_volume_5d > 0 else 0
        }
        
    except Exception as e:
        print(f"❌ Error fetching data for {ticker}: {e}")
        return None

def create_snapshot(tickers, snapshot_date=None):
    """Create a snapshot of current stock data"""
    if snapshot_date is None:
        snapshot_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📸 Creating snapshot for {snapshot_date}...")
    
    snapshot_data = {
        "date": snapshot_date,
        "created_at": datetime.now().isoformat(),
        "tickers": {}
    }
    
    successful = 0
    failed = 0
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Fetching {ticker}...", end=" ")
        
        data = fetch_stock_data(ticker)
        if data:
            snapshot_data["tickers"][ticker] = data
            successful += 1
            print("✅")
        else:
            failed += 1
            print("❌")
    
    print(f"\n📊 Snapshot complete: {successful} successful, {failed} failed")
    return snapshot_data

def save_snapshot(snapshot_data, output_dir=SNAPSHOT_DIR):
    """Save snapshot to JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    
    date = snapshot_data["date"]
    filename = f"snapshot_{date}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(snapshot_data, f, indent=2, default=str)

    print(f"💾 Snapshot saved: {filepath}")
    return filepath

def load_snapshot(filepath):
    """Load snapshot from JSON file"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Snapshot file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        return json.load(f)

def compare_snapshots(current_snapshot, previous_snapshot):
    """
    Compare two snapshots and generate a detailed report
    """
    current_tickers = set(current_snapshot["tickers"].keys())
    previous_tickers = set(previous_snapshot["tickers"].keys())
    
    # Find ticker changes
    added_tickers = current_tickers - previous_tickers
    removed_tickers = previous_tickers - current_tickers
    common_tickers = current_tickers & previous_tickers
    
    report = {
        "comparison_date": current_snapshot["date"],
        "previous_date": previous_snapshot["date"],
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_current": len(current_tickers),
            "total_previous": len(previous_tickers),
            "added": len(added_tickers),
            "removed": len(removed_tickers),
            "tracked": len(common_tickers)
        },
        "movements": [],
        "added_tickers": list(added_tickers),
        "removed_tickers": list(removed_tickers)
    }
    
    print(f"\n📈 Analyzing movements between {previous_snapshot['date']} and {current_snapshot['date']}...")
    
    # Analyze common tickers
    significant_moves = 0
    for ticker in sorted(common_tickers):
        current_data = current_snapshot["tickers"][ticker]
        previous_data = previous_snapshot["tickers"][ticker]
        
        # Calculate period change (snapshot to snapshot)
        period_change_pct = ((current_data["current_close"] - previous_data["current_close"]) / 
                            previous_data["current_close"]) * 100
        
        # Use current daily change
        daily_change_pct = current_data["daily_change_pct"]
        volume_ratio = current_data["volume_ratio_30d"]
        
        # Determine significance
        significant_daily = abs(daily_change_pct) >= PERCENT_MOVE_THRESHOLD
        significant_volume = volume_ratio >= VOLUME_MULTIPLIER_THRESHOLD
        significant_period = abs(period_change_pct) >= PERCENT_MOVE_THRESHOLD
        
        is_significant = significant_daily or significant_volume or significant_period
        
        if is_significant:
            significant_moves += 1
        
        movement = {
            "ticker": ticker,
            "daily_change_pct": round(daily_change_pct, 2),
            "period_change_pct": round(period_change_pct, 2),
            "volume_ratio_30d": round(volume_ratio, 2),
            "current_price": round(current_data["current_close"], 2),
            "previous_price": round(previous_data["current_close"], 2),
            "current_volume": current_data["current_volume"],
            "avg_volume_30d": round(current_data["avg_volume_30d"], 0),
            "significant": is_significant,
            "significant_daily": significant_daily,
            "significant_volume": significant_volume,
            "significant_period": significant_period,
            "status": generate_status_message(daily_change_pct, period_change_pct, volume_ratio, is_significant)
        }
        
        report["movements"].append(movement)
    
    report["summary"]["significant_moves"] = significant_moves
    return report

def generate_status_message(daily_pct, period_pct, volume_ratio, significant):
    """Generate human-readable status message"""
    if not significant:
        return "No major movement"
    
    messages = []
    
    if abs(daily_pct) >= PERCENT_MOVE_THRESHOLD:
        direction = "📈 Up" if daily_pct > 0 else "📉 Down"
        messages.append(f"{direction} {abs(daily_pct):.1f}% today")
    
    if volume_ratio >= VOLUME_MULTIPLIER_THRESHOLD:
        messages.append(f"🔊 Volume spike {volume_ratio:.1f}x")
    
    if abs(period_pct) >= PERCENT_MOVE_THRESHOLD:
        direction = "🚀 Strong rise" if period_pct > 0 else "💥 Sharp drop"
        messages.append(f"{direction} {abs(period_pct):.1f}% period")
    
    return " | ".join(messages) if messages else "Significant movement detected"

def save_report(report, output_dir=SNAPSHOT_DIR):
    """Save comparison report to JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"report_{report['comparison_date']}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"📋 Report saved: {filepath}")
    return filepath

def print_report_summary(report):
    """Print a formatted summary of the report"""
    print(f"\n🎯 KABU REPORT SUMMARY")
    print("=" * 50)
    print(f"Period: {report['previous_date']} → {report['comparison_date']}")
    print(f"Tracked: {report['summary']['tracked']} stocks")
    print(f"Significant moves: {report['summary']['significant_moves']}")
    
    if report['summary']['added']:
        print(f"Added: {report['summary']['added']} stocks")
    if report['summary']['removed']:
        print(f"Removed: {report['summary']['removed']} stocks")
    
    print("\n📊 SIGNIFICANT MOVEMENTS:")
    print("-" * 50)
    
    significant_movements = [m for m in report["movements"] if m["significant"]]
    
    if not significant_movements:
        print("No significant movements detected.")
        return
    
    # Sort by absolute daily change
    significant_movements.sort(key=lambda x: abs(x["daily_change_pct"]), reverse=True)
    
    for movement in significant_movements[:10]:  # Show top 10
        ticker = movement["ticker"]
        daily_pct = movement["daily_change_pct"]
        volume_ratio = movement["volume_ratio_30d"]
        price = movement["current_price"]
        status = movement["status"]
        
        print(f"{ticker:6} | ${price:8.2f} | {daily_pct:+6.2f}% | Vol:{volume_ratio:5.1f}x | {status}")

def find_latest_snapshot(output_dir=SNAPSHOT_DIR):
    """Find the most recent snapshot file"""
    if not os.path.exists(output_dir):
        return None
    
    snapshot_files = [f for f in os.listdir(output_dir) if f.startswith("snapshot_") and f.endswith(".json")]
    
    if not snapshot_files:
        return None
    
    # Sort by date in filename
    snapshot_files.sort(reverse=True)
    return os.path.join(output_dir, snapshot_files[0])

def kabu_main(ticker_file=None, compare_with=None, snapshot_only=False, output_dir=None):
    """Main execution function"""
    
    # Setup paths
    ticker_path = ticker_file or DEFAULT_TICKER_FILE
    output_directory = output_dir or SNAPSHOT_DIR
    
    try:
        # Load tickers
        tickers = load_tickers(ticker_path)
        
        # Create current snapshot
        current_snapshot = create_snapshot(tickers)
        snapshot_path = save_snapshot(current_snapshot, output_directory)
        
        if snapshot_only:
            print("✅ Snapshot-only mode complete")
            return snapshot_path, None
        
        # Find comparison snapshot
        if compare_with:
            if not os.path.exists(compare_with):
                raise FileNotFoundError(f"Comparison snapshot not found: {compare_with}")
            previous_snapshot_path = compare_with
        else:
            # Find the most recent snapshot (excluding the one we just created)
            previous_snapshot_path = find_latest_snapshot(output_directory)
            if previous_snapshot_path and previous_snapshot_path == snapshot_path:
                # If we found the snapshot we just created, look for the second most recent
                snapshot_files = [f for f in os.listdir(output_directory) 
                                if f.startswith("snapshot_") and f.endswith(".json")]
                snapshot_files.sort(reverse=True)
                if len(snapshot_files) > 1:
                    previous_snapshot_path = os.path.join(output_directory, snapshot_files[1])
                else:
                    previous_snapshot_path = None
        
        if not previous_snapshot_path:
            print("⚠️  No previous snapshot found for comparison. Run again tomorrow to generate comparisons.")
            return snapshot_path, None
        
        # Load and compare snapshots
        print(f"📊 Comparing with: {previous_snapshot_path}")
        previous_snapshot = load_snapshot(previous_snapshot_path)
        
        # Generate comparison report
        report = compare_snapshots(current_snapshot, previous_snapshot)
        report_path = save_report(report, output_directory)
        
        # Display summary
        print_report_summary(report)
        
        return snapshot_path, report_path
        
    except Exception as e:
        print(f"💥 Kabu execution failed: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Kabu: Daily stock movement monitor and comparison tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python kabu.py                                    # Use default ticker file
  python kabu.py --tickers my_stocks.txt           # Use custom ticker file
  python kabu.py --snapshot-only                   # Only create snapshot
  python kabu.py --compare snapshots/old.json      # Compare with specific snapshot
  python kabu.py --output-dir my_snapshots         # Use custom output directory
        """)
    
    parser.add_argument("--tickers", 
                       help=f"Path to ticker list file (default: {DEFAULT_TICKER_FILE})")
    parser.add_argument("--compare", 
                       help="Path to previous snapshot JSON for comparison")
    parser.add_argument("--snapshot-only", 
                       action="store_true", 
                       help="Only create a snapshot without comparison")
    parser.add_argument("--output-dir", 
                       help=f"Output directory for snapshots and reports (default: {SNAPSHOT_DIR})")
    parser.add_argument(
    "--snapshot-dir",
    type=str,
    default="kabu_snapshots",
    help="Directory to store/load snapshots"
    )
    args = parser.parse_args()
    
    try:
        kabu_main(
            ticker_file=args.tickers,
            compare_with=args.compare,
            snapshot_only=args.snapshot_only,
            output_dir=args.output_dir
        )
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        exit(1)

