import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os

PERCENT_MOVE_THRESHOLD = 5.0  # or whatever threshold value you are using in kabu.py

def load_report(report_file):
    with open(report_file, 'r') as f:
        return json.load(f)

def plot_report(report_data, output_file="kabu_visualization.png"):
    tickers = [r['ticker'] for r in report_data]
    pct_changes = [r['pct_change'] if 'pct_change' in r else 0 for r in report_data]
    volume_ratios = [r['volume_ratio'] if 'volume_ratio' in r else 0 for r in report_data]
    statuses = [r['status'] for r in report_data]

    # Create a color map for the percentage changes
    cmap = mcolors.ListedColormap(['#ff3333', '#f7b800', '#33ff33'])  # Red, Yellow, Green
    norm = mcolors.BoundaryNorm(boundaries=[-100, -PERCENT_MOVE_THRESHOLD, PERCENT_MOVE_THRESHOLD, 100], ncolors=3)

    fig, ax = plt.subplots(figsize=(12, 8))

    scatter = ax.scatter(tickers, pct_changes, c=pct_changes, cmap=cmap, norm=norm, s=100)
    
    for i, txt in enumerate(statuses):
        ax.annotate(txt, (tickers[i], pct_changes[i]), fontsize=8, ha='center', color='black')

    ax.set_xlabel('Ticker')
    ax.set_ylabel('% Change in Price')
    ax.set_title('Kabu Daily Roundup - Price Movement')
    
    cbar = fig.colorbar(scatter, ax=ax, orientation='vertical')
    cbar.set_label('% Price Change')

    ax.set_xticklabels(tickers, rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"Visualization saved to {output_file}")

def kabu_visualizer(report_file="snapshots/report_2025-04-30.json", output_file="kabu_visualization.png"):
    report_data = load_report(report_file)
    plot_report(report_data, output_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Visualize Kabu Daily Roundup Report as PNG.")
    parser.add_argument("--report", help="Path to the report JSON file", default="snapshots/report_2025-04-30.json")
    parser.add_argument("--output", help="Path to save the output PNG", default="kabu_visualization.png")
    args = parser.parse_args()

    kabu_visualizer(report_file=args.report, output_file=args.output)

