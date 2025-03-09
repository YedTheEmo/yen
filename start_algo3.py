"""
start_algo3.py - Detect Unusual Trading Volume Using Random Forest

This script trains a Random Forest model to detect volume anomalies in stock data. 
Anomalies are defined as trading volumes that significantly exceed historical trends.

Usage:
    python start_algo3.py <input_csv>

Arguments:
    input_csv - Path to the cleaned CSV file containing stock data.

Output:
    - Prints accuracy and classification report of the Random Forest model.
    - Identifies potential high-volume anomaly periods.

Dependencies:
    - pandas
    - numpy
    - scikit-learn
"""

import pandas as pd
import numpy as np
import argparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def load_data(file_path):
    df = pd.read_csv(file_path)

    # Create anomaly labels (1 for high volume spikes, 0 otherwise)
    threshold = df["Volume"].mean() + 2 * df["Volume"].std()
    df["Anomaly"] = (df["Volume"] > threshold).astype(int)

    # Feature selection
    features = ["Open", "High", "Low", "Close", "Volume"]
    df = df.dropna()

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(df[features], df["Anomaly"], test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

def train_random_forest(X_train, X_test, y_train, y_test):
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Predictions
    y_pred = rf.predict(X_test)

    # Evaluation
    print("Random Forest Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

def main():
    parser = argparse.ArgumentParser(description="Train Random Forest for volume anomaly detection.")
    parser.add_argument("input_file", help="Path to the cleaned CSV file.")
    args = parser.parse_args()

    X_train, X_test, y_train, y_test = load_data(args.input_file)
    train_random_forest(X_train, X_test, y_train, y_test)

if __name__ == "__main__":
    main()

