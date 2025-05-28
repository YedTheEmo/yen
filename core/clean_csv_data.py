import argparse
import pandas as pd

def clean_csv(input_file, output_file):
    """
    Cleans the given CSV by skipping unnecessary rows, reassigning columns,
    and ensuring correct data types (e.g., Date and numeric columns).
    """
    # Load the CSV file into a DataFrame, skipping the first three rows (as we did before)
    df = pd.read_csv(input_file, skiprows=3)
    
    # Reassign the proper column names
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    
    # Check if 'Date' and 'Volume' columns exist
    if 'Date' not in df.columns or 'Volume' not in df.columns:
        print("Error: 'Date' or 'Volume' column not found in the CSV.")
        return
    
    # Convert the "Date" column to datetime format
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    
    # Drop any rows with missing values in critical columns like 'Date' or 'Volume'
    df.dropna(subset=["Date", "Volume"], inplace=True)

    # Convert relevant columns to numeric values (to avoid issues with non-numeric entries)
    numeric_columns = ["Close", "High", "Low", "Open", "Volume"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    # Drop rows that have missing or non-numeric data in the numeric columns
    df.dropna(subset=numeric_columns, inplace=True)
    
    # Save the cleaned data to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Cleaned CSV saved to: {output_file}")

def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Clean CSV data by removing unnecessary headers and rows with missing data.")
    parser.add_argument("input_file", help="The raw CSV file to clean.")
    parser.add_argument("output_file", help="The path to save the cleaned CSV file.")
    return parser.parse_args()

def main():
    # Parse the arguments
    args = parse_args()
    
    # Clean the CSV file
    clean_csv(args.input_file, args.output_file)

if __name__ == "__main__":
    main()

