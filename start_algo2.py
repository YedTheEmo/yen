"""
start_algo2.py - Cluster Stock Data Using K-Means

This script applies K-Means clustering to stock data, grouping stocks with similar 
price-volume behavior.

Usage:
    python start_algo2.py <input_csv> --clusters <num_clusters>

Arguments:
    input_csv   - Path to the cleaned CSV file containing stock data.
    --clusters  - (Optional) Number of clusters to form (default: 3).

Output:
    - Prints cluster centers for each group.
    - Saves a scatter plot of clusters as 'kmeans_clusters.png'.

Dependencies:
    - pandas
    - scikit-learn
    - matplotlib
    - seaborn
"""

import pandas as pd
import argparse
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    df = pd.read_csv(file_path)

    # Select features for clustering
    features = ["Open", "High", "Low", "Close", "Volume"]
    df = df.dropna()

    return df[features]

def perform_kmeans(X, num_clusters=3):
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    X["Cluster"] = kmeans.fit_predict(X)

    return X, kmeans

def visualize_clusters(X):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=X["Close"], y=X["Volume"], hue=X["Cluster"], palette="viridis")
    plt.title("K-Means Clustering of Stock Data (Close vs Volume)")
    plt.xlabel("Closing Price")
    plt.ylabel("Trading Volume")
    plt.legend(title="Cluster")

    # Save the plot as an image file
    plt.savefig("kmeans_clusters.png")
    print("Cluster visualization saved as 'kmeans_clusters.png'. Open it to view.")

    # If running in an interactive environment (like Jupyter), uncomment this:
    # plt.show()


def main():
    parser = argparse.ArgumentParser(description="Apply K-Means Clustering to stock data.")
    parser.add_argument("input_file", help="Path to the cleaned CSV file.")
    parser.add_argument("--clusters", type=int, default=3, help="Number of clusters (default: 3).")
    args = parser.parse_args()

    X = load_data(args.input_file)
    clustered_data, kmeans = perform_kmeans(X, args.clusters)

    print("Cluster Centers:\n", kmeans.cluster_centers_)
    visualize_clusters(clustered_data)

if __name__ == "__main__":
    main()

