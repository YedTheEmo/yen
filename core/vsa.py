import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import argparse
import warnings
import os

warnings.filterwarnings('ignore')


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.ewm(span=length, adjust=False).mean()
    return atr


def vsa_indicator(data: pd.DataFrame, norm_lookback: int = 168) -> pd.Series:
    atr = calculate_atr(data['high'], data['low'], data['close'], length=norm_lookback)
    vol_med = data['volume'].rolling(norm_lookback).median()
    norm_range = (data['high'] - data['low']) / atr
    norm_volume = data['volume'] / vol_med
    range_dev = np.full(len(data), np.nan)

    start_idx = norm_lookback * 2
    for i in range(start_idx, len(data)):
        window_start = i - norm_lookback + 1
        window_end = i + 1
        vol_window = norm_volume.iloc[window_start:window_end]
        range_window = norm_range.iloc[window_start:window_end]
        valid_mask = ~(pd.isna(vol_window) | pd.isna(range_window))
        if valid_mask.sum() < 5:
            continue
        vol_clean = vol_window[valid_mask]
        range_clean = range_window[valid_mask]

        try:
            slope, intercept, r_val, _, _ = stats.linregress(vol_clean, range_clean)
            if slope <= 0.0 or r_val < 0.2:
                range_dev[i] = 0.0
            else:
                pred = intercept + slope * norm_volume.iloc[i]
                range_dev[i] = norm_range.iloc[i] - pred
        except (ValueError, np.linalg.LinAlgError):
            range_dev[i] = 0.0

    return pd.Series(range_dev, index=data.index, name='vsa_deviation')


def find_signals(data: pd.DataFrame, threshold: float = 1.0):
    above_signals = data[data['dev'] > threshold].copy()
    below_signals = data[data['dev'] < -threshold].copy()
    return above_signals, below_signals


def plot_around(data: pd.DataFrame, idx: int, above: bool = True,
                threshold: float = 1.0, days_around: int = 1, output_dir: str = "vsa_outputs") -> None:
    """
    Plot around signal and save figure in output_dir.
    """
    import os
    above_signals, below_signals = find_signals(data, threshold)
    signals = above_signals if above else below_signals

    if len(signals) == 0:
        print(f"No {'above' if above else 'below'} threshold signals found for threshold {threshold}")
        return
    if idx >= len(signals):
        print(f"Index {idx} out of range for available signals: {len(signals)}")
        return

    signal_timestamp = signals.index[idx]
    time_window = pd.Timedelta(days=days_around)
    start_time = signal_timestamp - time_window
    end_time = signal_timestamp + time_window
    window_data = data.loc[start_time:end_time].copy()

    if len(window_data) == 0:
        print(f"No data available around signal at {signal_timestamp}")
        return

    plt.style.use('dark_background')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    for date, row in window_data.iterrows():
        color = 'green' if row['close'] >= row['open'] else 'red'
        alpha = 1.0 if date == signal_timestamp else 0.7
        ax1.plot([date, date], [row['low'], row['high']], color='white', alpha=alpha, linewidth=1)
        height = abs(row['close'] - row['open'])
        bottom = min(row['close'], row['open'])
        linewidth = 2 if date == signal_timestamp else 1
        if date == signal_timestamp:
            color = 'orange'
            alpha = 1.0
        ax1.bar(date, height, bottom=bottom, color=color, alpha=alpha,
                width=pd.Timedelta(hours=12), linewidth=linewidth, edgecolor='white')

    ax1.set_ylabel('Price')
    signal_dev = window_data.loc[signal_timestamp, 'dev']
    ax1.set_title(f'VSA Signal on {signal_timestamp.strftime("%Y-%m-%d")} (Dev: {signal_dev:.3f})')
    ax1.grid(True, alpha=0.3)

    bars = ax2.bar(window_data.index, window_data['volume'], color='blue', alpha=0.7)
    if signal_timestamp in window_data.index:
        signal_idx = window_data.index.get_loc(signal_timestamp)
        bars[signal_idx].set_color('orange')
        bars[signal_idx].set_alpha(1.0)
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)

    ax3.plot(window_data.index, window_data['dev'], color='cyan', linewidth=2)
    ax3.axhline(y=threshold, color='red', linestyle='--', alpha=0.7)
    ax3.axhline(y=-threshold, color='red', linestyle='--', alpha=0.7)
    ax3.axhline(y=0, color='white', linestyle='-', alpha=0.3)
    ax3.scatter(signal_timestamp, signal_dev, color='orange', s=150,
                edgecolor='white', linewidth=2)
    ax3.axvline(x=signal_timestamp, color='orange', linestyle=':', alpha=0.5)
    ax3.set_ylabel('VSA Deviation')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f'vsa_signal_{signal_timestamp.strftime("%Y%m%d_%H%M%S")}_{"above" if above else "below"}_{threshold}.png')
    plt.savefig(filename, dpi=300)
    plt.close()


def analyze_vsa_signals(data: pd.DataFrame, threshold: float = 1.0) -> None:
    above_signals, below_signals = find_signals(data, threshold)
    print(f"\nVSA Analysis Summary (Threshold: ±{threshold})")
    print("=" * 50)
    print(f"Total data points: {len(data)}")
    print(f"Valid VSA deviations: {data['dev'].notna().sum()}")
    print(f"Above threshold: {len(above_signals)}")
    print(f"Below threshold: {len(below_signals)}")
    if not above_signals.empty:
        print(f"Strongest positive: {above_signals['dev'].max():.3f} on {above_signals['dev'].idxmax().date()}")
    if not below_signals.empty:
        print(f"Strongest negative: {below_signals['dev'].min():.3f} on {below_signals['dev'].idxmin().date()}")
    print("\nDeviation stats:")
    print(data['dev'].describe().round(3).to_string())


def main():
    parser = argparse.ArgumentParser(description="VSA Signal Detector & Visualizer")
    parser.add_argument("-f", "--file", default="analyze.csv", help="Path to input OHLCV CSV (default: analyze.csv)")
    parser.add_argument("-t", "--thresholds", type=float, nargs="+", default=[1.0],
                        help="List of signal thresholds (e.g., -t 1.0 0.5)")
    parser.add_argument("-p", "--plot", action="store_true", help="Enable plotting of signals")
    parser.add_argument("-d", "--days", type=int, default=5, help="Days around signal to plot (default: 5)")
    parser.add_argument("-n", "--norm_lookback", type=int, default=20, help="Normalization lookback (default: 20)")
    parser.add_argument("-o", "--output-dir", default="vsa_outputs",
                    help="Directory to save output plots (default: vsa_outputs)")


    args = parser.parse_args()

    try:
        os.makedirs('vsa_outputs', exist_ok=True)
        print(f"Loading data from {args.file}...")
        df = pd.read_csv(args.file, parse_dates=['Date'])
        df.columns = [col.lower() for col in df.columns]
        df = df.rename(columns={'date': 'datetime'}).set_index('datetime')

        required = ['open', 'high', 'low', 'close', 'volume']
        if any(col not in df.columns for col in required):
            raise ValueError(f"Missing required columns: {required}")

        df = df.sort_index()
        print(f"Data loaded: {len(df)} rows from {df.index[0].date()} to {df.index[-1].date()}")

        print("Computing VSA deviation...")
        df['dev'] = vsa_indicator(df, norm_lookback=args.norm_lookback)

        for threshold in args.thresholds:
            analyze_vsa_signals(df, threshold)
            if args.plot:
                above_signals, below_signals = find_signals(df, threshold)
                for i in range(len(below_signals)):
                    plot_around(df, idx=i, above=False, threshold=threshold, days_around=args.days, output_dir=args.output_dir)
                for i in range(len(above_signals)):
                    plot_around(df, idx=i, above=True, threshold=threshold, days_around=args.days, output_dir=args.output_dir)

        print("\nSample VSA deviation values (last 10 non-NaN):")
        for dt, val in df['dev'].dropna().tail(10).items():
            print(f"  {dt.strftime('%Y-%m-%d')}: {val:.4f}")

    except FileNotFoundError:
        print(f"Error: '{args.file}' not found.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


