import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os

# must match the threshold used in kabu.py
PERCENT_MOVE_THRESHOLD = 5.0  

def load_report(report_file):
    """Load the JSON report and return the 'movements' list."""
    with open(report_file, 'r') as f:
        report = json.load(f)
    return report.get("movements", [])

def plot_report(movements, output_file="kabu_visualization.png"):
    """Scatter-plot tickers by daily % change, color-coded by magnitude."""
    if not movements:
        print("No movement data to plot.")
        return

    tickers       = [m['ticker']                    for m in movements]
    pct_changes   = [m['daily_change_pct']          for m in movements]
    volume_ratios = [m['volume_ratio_30d']          for m in movements]
    statuses      = [m['status']                    for m in movements]

    # Color map: down (red), flat (yellow), up (green)
    cmap = mcolors.ListedColormap(['#ff3333', '#f7b800', '#33ff33'])
    norm = mcolors.BoundaryNorm(
        boundaries=[-100,
                    -PERCENT_MOVE_THRESHOLD,
                     PERCENT_MOVE_THRESHOLD,
                     100],
        ncolors=cmap.N
    )

    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(
        tickers,
        pct_changes,
        c=pct_changes,
        cmap=cmap,
        norm=norm,
        s=100
    )

    # Annotate each point with its status
    for i, txt in enumerate(statuses):
        ax.annotate(
            txt,
            (tickers[i], pct_changes[i]),
            fontsize=8,
            ha='center',
            va='bottom'
        )

    ax.set_xlabel('Ticker')
    ax.set_ylabel('% Change in Price (Daily)')
    ax.set_title('Kabu Daily Roundup – Price Movement')

    cbar = fig.colorbar(scatter, ax=ax, orientation='vertical')
    cbar.set_label('% Price Change')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    plt.savefig(output_file)
    plt.close()

    print(f"✅ Visualization saved to {output_file}")

def kabu_visualizer(report_file, output_file="kabu_visualization.png"):
    movements = load_report(report_file)
    plot_report(movements, output_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Visualize Kabu Daily Roundup Report as PNG."
    )
    parser.add_argument(
        "--report",
        help="Path to the report JSON file",
        default="snapshots/report_2025-04-30.json"
    )
    parser.add_argument(
        "--output",
        help="Path to save the output PNG",
        default="kabu_visualization.png"
    )
    args = parser.parse_args()

    kabu_visualizer(report_file=args.report, output_file=args.output)

