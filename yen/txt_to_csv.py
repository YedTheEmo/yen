import argparse
import csv

def txt_to_csv(input_file, output_file):
    """
    Convert a tab- or space-delimited TXT file to CSV. If tabs are present, split on tabs;
    otherwise split on whitespace. Rows with mismatched column counts are skipped.
    """
    # Read and process the input file
    with open(input_file, 'r') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]

    if not lines:
        print(f"No data found in '{input_file}'.")
        return

    # Determine delimiter for header
    header_line = lines[0]
    if '\t' in header_line:
        header = header_line.split('\t')
        split_fn = lambda line: line.split('\t')
    else:
        header = header_line.split()
        split_fn = lambda line: line.split()

    # Process data lines
    data = [split_fn(line) for line in lines[1:]]

    # Validate column counts
    col_count = len(header)
    valid_data = []
    for i, row in enumerate(data, start=2):
        if len(row) != col_count:
            print(f"Line {i} has {len(row)} columns (expected {col_count}), skipping this row.")
            continue
        valid_data.append(row)

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(valid_data)

    print(f"CSV file '{output_file}' created successfully with {len(valid_data)} rows.")

def main():
    parser = argparse.ArgumentParser(description="Convert a tab- or space-delimited TXT file to CSV.")
    parser.add_argument("input_file", help="Path to the input .txt file")
    parser.add_argument("output_file", help="Path to the output .csv file")

    args = parser.parse_args()
    txt_to_csv(args.input_file, args.output_file)

if __name__ == '__main__':
    main()

