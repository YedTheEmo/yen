import argparse
import pandas as pd
import numpy as np

def detect_volume_anomalies(input_file, output_file, threshold=2.0):
    """
    Detects volume anomalies based on price spread-to-volume mismatches.
    """
    # Load the cleaned CSV
    df = pd.read_csv(input_file)
    
    # Ensure required columns exist
    required_columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Missing required column '{col}' in CSV.")
            return
    
    # Compute price spread
    df["Spread"] = df["High"] - df["Low"]
    
    # Avoid division by zero
    df = df[df["Spread"] > 0]
    
    # Compute volume-to-spread ratio
    df["Volume_Spread_Ratio"] = df["Volume"] / df["Spread"]
    
    # Calculate mean and standard deviation for volume-spread ratio
    mean_ratio = df["Volume_Spread_Ratio"].mean()
    std_ratio = df["Volume_Spread_Ratio"].std()
    
    # Identify anomalies where the ratio deviates significantly
    df["Anomaly_Score"] = np.abs((df["Volume_Spread_Ratio"] - mean_ratio) / std_ratio)
    df_anomalies = df[df["Anomaly_Score"] > threshold]
    
    # Save detected anomalies to CSV
    if not df_anomalies.empty:
        df_anomalies.to_csv(output_file, index=False)
        print(f"Volume anomalies saved to: {output_file}")
    else:
        print("No significant volume anomalies detected.")

def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Detect volume anomalies in cleaned CSV data.")
    parser.add_argument("input_file", help="The cleaned CSV file to analyze.")
    parser.add_argument("output_file", help="The path to save the anomaly report.")
    parser.add_argument("--threshold", type=float, default=2.0, help="Z-score threshold for anomalies (default: 2.0).")
    return parser.parse_args()

def main():
    args = parse_args()
    detect_volume_anomalies(args.input_file, args.output_file, args.threshold)

if __name__ == "__main__":
    main()

