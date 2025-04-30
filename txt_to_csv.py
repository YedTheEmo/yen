import argparse
import csv

def txt_to_csv(input_file, output_file):
    # Read and process the input file
    with open(input_file, "r") as file:
        lines = file.readlines()

    # Split the header and data
    header = lines[0].split()
    data = [line.split() for line in lines[1:] if line.strip()]

    # Write to CSV
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)

    print(f"✅ CSV file '{output_file}' created successfully.")

def main():
    parser = argparse.ArgumentParser(description="Convert a space-separated TXT file to CSV.")
    parser.add_argument("input_file", help="Path to the input .txt file")
    parser.add_argument("output_file", help="Path to the output .csv file")

    args = parser.parse_args()
    txt_to_csv(args.input_file, args.output_file)

if __name__ == "__main__":
    main()

