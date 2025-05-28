#!/usr/bin/env python3
"""
YEN - Unified Stock Analysis Workflow Manager

This script provides predefined workflows that chain together multiple analysis tools
to eliminate the complexity of managing individual scripts and their dependencies.
"""

import os
import sys
import argparse
import subprocess
import glob
from pathlib import Path
import tempfile
import shutil

class YenWorkflowManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent / "core"
        self.temp_files = []
        
    def run_script(self, script_name, args):
        """Execute a script in the yen subdirectory"""
        script_path = self.script_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        cmd = [sys.executable, str(script_path)] + args
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Script {script_name} failed with return code {result.returncode}")
        return result
    
    def find_exported_csv(self, ticker, start_date, end_date, interval="1d"):
        """Find the CSV file exported for a specific ticker"""
        pattern = f"data_exports/{ticker}_{start_date}_{end_date}_{interval}.csv"
        matches = glob.glob(pattern)
        if not matches:
            raise FileNotFoundError(f"No exported CSV found matching pattern: {pattern}")
        return matches[0]

    def find_latest_report(self, output_dir):
        pattern = Path(output_dir) / "report_*.json"
        reports = sorted(glob.glob(str(pattern)))
        return reports[-1] if reports else None

    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Cleaned up: {temp_file}")

    # ================================
    # WORKFLOW 1: VSA Analysis Pipeline
    # ================================
    def vsa_analysis(self, ticker, start_date, end_date, intervals=None, threshold=1.0, plot=False, days=5):
        """
        Complete VSA Analysis Pipeline:
        1. Export stock data
        2. Clean the CSV
        3. Run VSA analysis with visualization
        """
        print(f"🔄 Starting VSA Analysis for {ticker}")
        
        if intervals is None:
            intervals = ["1d"]
        
        try:
            # Step 1: Export data
            print("📊 Step 1: Exporting stock data...")
            self.run_script("data_exporter.py", [
                ticker, start_date, end_date,
                "--intervals"] + intervals)
            
            # Process each interval
            for interval in intervals:
                print(f"\n📈 Processing {interval} interval...")
                
                # Step 2: Find and clean CSV
                print("🧹 Step 2: Cleaning CSV data...")
                raw_csv = self.find_exported_csv(ticker, start_date, end_date, interval)
                cleaned_csv = f"cleaned_{ticker}_{interval}.csv"
                self.temp_files.append(cleaned_csv)
                
                self.run_script("clean_csv_data.py", [raw_csv, cleaned_csv])
                
                # Step 3: Run VSA analysis
                print("🔍 Step 3: Running VSA analysis...")
                vsa_args = ["-f", cleaned_csv, "-t", str(threshold)]
                if plot:
                    vsa_args.extend(["-p", "-d", str(days)])
                
                self.run_script("vsa.py", vsa_args)
            
            print(f"✅ VSA Analysis complete for {ticker}")
            
        except Exception as e:
            print(f"❌ VSA Analysis failed: {e}")
            raise
        finally:
            self.cleanup()

    # ======================================
    # WORKFLOW 2: Volume Anomaly Detection
    # ======================================
    def volume_anomalies(self, ticker, start_date, end_date, threshold=2.0):
        """
        Volume Anomaly Detection Pipeline:
        1. Export stock data
        2. Clean the CSV
        3. Detect volume anomalies
        """
        print(f"🔄 Starting Volume Anomaly Detection for {ticker}")
        
        try:
            # Step 1: Export data
            print("📊 Step 1: Exporting stock data...")
            self.run_script("data_exporter.py", [ticker, start_date, end_date])
            
            # Step 2: Clean CSV
            print("🧹 Step 2: Cleaning CSV data...")
            raw_csv = self.find_exported_csv(ticker, start_date, end_date)
            cleaned_csv = f"cleaned_{ticker}_anomalies.csv"
            self.temp_files.append(cleaned_csv)
            
            self.run_script("clean_csv_data.py", [raw_csv, cleaned_csv])
            
            # Step 3: Detect anomalies
            print("🚨 Step 3: Detecting volume anomalies...")
            anomaly_output = f"anomalies_{ticker}_{start_date}_{end_date}.csv"
            self.run_script("detect_volume_anomalies.py", [
                cleaned_csv, anomaly_output, "--threshold", str(threshold)
            ])
            
            print(f"✅ Volume Anomaly Detection complete for {ticker}")
            print(f"📄 Results saved to: {anomaly_output}")
            
        except Exception as e:
            print(f"❌ Volume Anomaly Detection failed: {e}")
            raise
        finally:
            self.cleanup()

    # ============================
    # WORKFLOW 3: AI Report Generation
    # ============================
    def ai_analysis(self, ticker, start_date, end_date, intervals=None):
        """
        AI-Powered Analysis Report:
        1. Generate analysis prompts
        2. Get AI analysis via OpenAI API
        3. Generate HTML report
        """
        print(f"🔄 Starting AI Analysis for {ticker}")
        
        if intervals is None:
            intervals = ["1wk", "1d", "1h"]
        
        try:
            # Run AI report generator (handles data fetching internally)
            print("🤖 Generating AI-powered analysis report...")
            self.run_script("report_generator.py", [
                ticker, start_date, end_date,
                "--intervals"] + intervals)
            
            print(f"✅ AI Analysis complete for {ticker}")
            
        except Exception as e:
            print(f"❌ AI Analysis failed: {e}")
            raise

    # ===========================
    # WORKFLOW 4: Complete Analysis
    # ===========================
    def full_analysis(self, ticker, start_date, end_date, vsa_threshold=1.0, anomaly_threshold=2.0):
        """
        Complete Analysis Pipeline:
        1. VSA Analysis
        2. Volume Anomaly Detection  
        3. AI Report Generation
        """
        print(f"🔄 Starting Full Analysis for {ticker}")
        
        try:
            # Run all analyses
            self.vsa_analysis(ticker, start_date, end_date, threshold=vsa_threshold, plot=True)
            self.volume_anomalies(ticker, start_date, end_date, threshold=anomaly_threshold)
            self.ai_analysis(ticker, start_date, end_date)
            
            print(f"✅ Full Analysis complete for {ticker}")
            
        except Exception as e:
            print(f"❌ Full Analysis failed: {e}")
            raise

    # ============================
    # WORKFLOW 5: Stock Screening
    # ============================
    def stock_screening(self, min_institutional, min_volatility, min_volume, 
                       ticker_file=None, output_file="filtered_stocks.txt", resume=False):
        """
        Stock Screening Workflow:
        Screen stocks based on institutional ownership, volatility, and volume
        """
        print("🔄 Starting Stock Screening...")
        
        try:
            args = [str(min_institutional), str(min_volatility), str(min_volume)]
            if ticker_file:
                args.extend(["--ticker-file", ticker_file])
            args.extend(["--output-file", output_file])
            if resume:
                args.append("--resume")
            
            self.run_script("stock_scanner.py", args)
            
            print("✅ Stock Screening complete")
            print(f"📄 Results saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Stock Screening failed: {e}")
            raise

    # ===============================
    # WORKFLOW 6: Batch Analysis
    # ===============================
    def batch_analysis(self, ticker_file, start_date, end_date, workflow="vsa", **kwargs):
        """
        Batch Analysis Workflow:
        Process multiple tickers from a file through any workflow
        """
        print(f"🔄 Starting Batch {workflow.upper()} Analysis...")
        
        try:
            # Read tickers from file
            with open(ticker_file, 'r') as f:
                tickers = [line.strip() for line in f if line.strip()]
            
            print(f"📋 Processing {len(tickers)} tickers...")
            
            for i, ticker in enumerate(tickers, 1):
                print(f"\n🔄 [{i}/{len(tickers)}] Processing {ticker}...")
                
                try:
                    if workflow == "vsa":
                        self.vsa_analysis(ticker, start_date, end_date, **kwargs)
                    elif workflow == "anomalies":
                        self.volume_anomalies(ticker, start_date, end_date, **kwargs)
                    elif workflow == "ai":
                        self.ai_analysis(ticker, start_date, end_date, **kwargs)
                    elif workflow == "full":
                        self.full_analysis(ticker, start_date, end_date, **kwargs)
                    else:
                        raise ValueError(f"Unknown workflow: {workflow}")
                        
                except Exception as e:
                    print(f"⚠️  Failed to process {ticker}: {e}")
                    continue
            
            print("✅ Batch Analysis complete")
            
        except Exception as e:
            print(f"❌ Batch Analysis failed: {e}")
            raise


    # =============================
    # WORKFLOW 7: KABU Snapshot Diff
    # =============================
    def kabu_analysis(self,
                       ticker_file=None,
                       compare=None,
                       snapshot_only=False,
                       output_dir=None,
                       snapshot_dir=None,
                       visualize_png=False,
                       visualize_html=False,
                       png_output="kabu_visualization.png",
                       html_output="kabu_report.html"):
        """
        Run KABU snapshot comparison and optional visualization.
        """
        print("🔄 Starting KABU snapshot analysis...")
        args = []
        if ticker_file:
            args.extend(["--tickers", ticker_file])
        if compare:
            args.extend(["--compare", compare])
        if snapshot_only:
            args.append("--snapshot-only")
        out_dir = output_dir or snapshot_dir or "kabu_snapshots"
        args.extend(["--output-dir", out_dir])
        # Run KABU
        try:
            self.run_script("kabu.py", args)
            print("✅ KABU execution complete")
            if not snapshot_only:
                report_path = self.find_latest_report(out_dir)
                if report_path:
                    print(f"🔍 Found report: {report_path}")
                    if visualize_png:
                        print("📈 Generating PNG visualization...")
                        self.run_script("kabu_visualizer.py", ["--report", report_path, "--output", png_output])
                    if visualize_html:
                        print("🌐 Generating HTML report...")
                        self.run_script("kabu_visualizer_html.py", ["--report", report_path, "--output", html_output])
                else:
                    print("⚠️  No report found for visualization.")
            return
        except Exception as e:
            print(f"❌ KABU analysis failed: {e}")
            raise
        finally:
            self.cleanup()
    # ============================
    # UTILITY: Data Conversion
    # ============================
    def convert_data(self, input_file, output_file=None):
        """Convert space-separated TXT to CSV"""
        if output_file is None:
            output_file = input_file.replace('.txt', '.csv')
        
        print(f"🔄 Converting {input_file} to {output_file}")
        
        try:
            self.run_script("txt_to_csv.py", [input_file, output_file])
            print(f"✅ Data conversion complete")
            
        except Exception as e:
            print(f"❌ Data conversion failed: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(
        description="YEN - Unified Stock Analysis Workflow Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Workflows:
  vsa-analysis      Complete VSA analysis pipeline (export → clean → analyze)
  volume-anomalies  Volume anomaly detection pipeline
  ai-analysis       AI-powered analysis report generation
  full-analysis     Complete analysis (VSA + anomalies + AI report)
  stock-screening   Screen stocks by institutional ownership/volatility/volume
  batch-analysis    Process multiple tickers through any workflow
  convert-data      Convert space-separated TXT to CSV
  kabu-analysis     Daily Stock Watchlist Roundup

Examples:
  python yen.py vsa-analysis AAPL 2024-01-01 2024-12-31 --plot
  python yen.py volume-anomalies TSLA 2024-01-01 2024-12-31 --threshold 1.5
  python yen.py full-analysis NVDA 2024-01-01 2024-12-31
  python yen.py stock-screening 10.0 0.3 1000000
  python yen.py batch-analysis tickers.txt 2024-01-01 2024-12-31 vsa --plot
        """)
    
    subparsers = parser.add_subparsers(dest='workflow', help='Available workflows')
    
    # VSA Analysis workflow
    vsa_parser = subparsers.add_parser('vsa-analysis', help='Complete VSA analysis pipeline')
    vsa_parser.add_argument('ticker', help='Stock ticker symbol')
    vsa_parser.add_argument('start_date', help='Start date (YYYY-MM-DD)')
    vsa_parser.add_argument('end_date', help='End date (YYYY-MM-DD)')
    vsa_parser.add_argument('--intervals', nargs='*', default=['1d'], help='Intervals to analyze')
    vsa_parser.add_argument('--threshold', type=float, default=1.0, help='VSA threshold')
    vsa_parser.add_argument('--plot', action='store_true', help='Generate plots')
    vsa_parser.add_argument('--days', type=int, default=5, help='Days around signal to plot')
    
    # Volume Anomalies workflow
    anom_parser = subparsers.add_parser('volume-anomalies', help='Volume anomaly detection')
    anom_parser.add_argument('ticker', help='Stock ticker symbol')
    anom_parser.add_argument('start_date', help='Start date (YYYY-MM-DD)')
    anom_parser.add_argument('end_date', help='End date (YYYY-MM-DD)')
    anom_parser.add_argument('--threshold', type=float, default=2.0, help='Anomaly threshold')
    
    # AI Analysis workflow
    ai_parser = subparsers.add_parser('ai-analysis', help='AI-powered analysis report')
    ai_parser.add_argument('ticker', help='Stock ticker symbol')
    ai_parser.add_argument('start_date', help='Start date (YYYY-MM-DD)')
    ai_parser.add_argument('end_date', help='End date (YYYY-MM-DD)')
    ai_parser.add_argument('--intervals', nargs='*', default=['1wk', '1d', '1h'], help='Intervals')
    
    # Full Analysis workflow
    full_parser = subparsers.add_parser('full-analysis', help='Complete analysis suite')
    full_parser.add_argument('ticker', help='Stock ticker symbol')
    full_parser.add_argument('start_date', help='Start date (YYYY-MM-DD)')
    full_parser.add_argument('end_date', help='End date (YYYY-MM-DD)')
    full_parser.add_argument('--vsa-threshold', type=float, default=1.0, help='VSA threshold')
    full_parser.add_argument('--anomaly-threshold', type=float, default=2.0, help='Anomaly threshold')
    
    # Stock Screening workflow
    screen_parser = subparsers.add_parser('stock-screening', help='Screen stocks by criteria')
    screen_parser.add_argument('min_institutional', type=float, help='Min institutional ownership %%')
    screen_parser.add_argument('min_volatility', type=float, help='Min annualized volatility')
    screen_parser.add_argument('min_volume', type=int, help='Min average daily volume')
    screen_parser.add_argument('--ticker-file', help='File with ticker symbols')
    screen_parser.add_argument('--output-file', default='filtered_stocks.txt', help='Output file')
    screen_parser.add_argument('--resume', action='store_true', help='Resume from last progress')
    
    # Batch Analysis workflow
    batch_parser = subparsers.add_parser('batch-analysis', help='Process multiple tickers')
    batch_parser.add_argument('ticker_file', help='File containing ticker symbols')
    batch_parser.add_argument('start_date', help='Start date (YYYY-MM-DD)')
    batch_parser.add_argument('end_date', help='End date (YYYY-MM-DD)')
    batch_parser.add_argument('workflow_type', choices=['vsa', 'anomalies', 'ai', 'full'], 
                            help='Type of analysis to run')
    batch_parser.add_argument('--threshold', type=float, default=1.0, help='Analysis threshold')
    batch_parser.add_argument('--plot', action='store_true', help='Generate plots (VSA only)')
    
    # KABU Snapshot Diff workflow with Visualization options
    kabu_parser = subparsers.add_parser('kabu-analysis', help='Compare and visualize KABU snapshot differences')
    kabu_parser.add_argument('--tickers', dest='ticker_file', help='Ticker list file (default: filtered_stocks.txt)')
    kabu_parser.add_argument('--compare', dest='compare', help='Path to previous snapshot JSON')
    kabu_parser.add_argument('--snapshot-only', dest='snapshot_only', action='store_true', help='Only create a snapshot')
    kabu_parser.add_argument('--output-dir', dest='output_dir', help='Output directory for snapshots/reports')
    kabu_parser.add_argument('--snapshot-dir', dest='snapshot_dir', help='Directory to store/load snapshots')
    kabu_parser.add_argument('--visualize-png', dest='visualize_png', action='store_true', help='Generate PNG visualization')
    kabu_parser.add_argument('--visualize-html', dest='visualize_html', action='store_true', help='Generate HTML report')
    kabu_parser.add_argument('--png-output', dest='png_output', default='kabu_visualization.png', help='PNG output filename')
    kabu_parser.add_argument('--html-output', dest='html_output', default='kabu_report.html', help='HTML output filename')


    # Data Conversion utility
    convert_parser = subparsers.add_parser('convert-data', help='Convert TXT to CSV')
    convert_parser.add_argument('input_file', help='Input TXT file')
    convert_parser.add_argument('--output-file', help='Output CSV file (optional)')
    
    args = parser.parse_args()
    
    if not args.workflow:
        parser.print_help()
        return
    
    manager = YenWorkflowManager()
    
    try:
        if args.workflow == 'vsa-analysis':
            manager.vsa_analysis(
                args.ticker, args.start_date, args.end_date,
                intervals=args.intervals, threshold=args.threshold,
                plot=args.plot, days=args.days
            )
        elif args.workflow == 'volume-anomalies':
            manager.volume_anomalies(
                args.ticker, args.start_date, args.end_date,
                threshold=args.threshold
            )
        elif args.workflow == 'ai-analysis':
            manager.ai_analysis(
                args.ticker, args.start_date, args.end_date,
                intervals=args.intervals
            )
        elif args.workflow == 'full-analysis':
            manager.full_analysis(
                args.ticker, args.start_date, args.end_date,
                vsa_threshold=args.vsa_threshold,
                anomaly_threshold=args.anomaly_threshold
            )
        elif args.workflow == 'stock-screening':
            manager.stock_screening(
                args.min_institutional, args.min_volatility, args.min_volume,
                ticker_file=args.ticker_file, output_file=args.output_file,
                resume=args.resume
            )
        elif args.workflow == 'batch-analysis':
            kwargs = {'threshold': args.threshold}
            if args.plot:
                kwargs['plot'] = True
            manager.batch_analysis(
                args.ticker_file, args.start_date, args.end_date,
                workflow=args.workflow_type, **kwargs
            )
        elif args.workflow == 'kabu-analysis':
            manager.kabu_analysis(
                ticker_file=args.ticker_file,
                compare=args.compare,
                snapshot_only=args.snapshot_only,
                output_dir=args.output_dir,
                snapshot_dir=args.snapshot_dir,
                visualize_png=args.visualize_png,
                visualize_html=args.visualize_html,
                png_output=args.png_output,
                html_output=args.html_output
            )
        elif args.workflow == 'convert-data':
            manager.convert_data(args.input_file, args.output_file)
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        manager.cleanup()
    except Exception as e:
        print(f"\n💥 Workflow failed: {e}")
        manager.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
