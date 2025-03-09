"""
start_algo1.py - Predict Stock Price Movement Using Decision Tree

This script trains a Decision Tree model to predict whether a stock's closing price 
will go up or down based on historical Open, High, Low, Close (OHLC), and Volume data.

Usage:
    python start_algo1.py <input_csv>

Arguments:
    input_csv - Path to the cleaned CSV file containing stock data.

Output:
    - Prints accuracy and classification report of the Decision Tree model.
    - Uses past stock data to classify the next movement as Up (1) or Down (0).

Dependencies:
    - pandas
    - numpy
    - scikit-learn
"""


import pandas as pd
import numpy as np
import argparse
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

def load_data(file_path):
    df = pd.read_csv(file_path)

    # Generate price movement labels: 1 (Up) or 0 (Down)
    df["Price_Movement"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    
    # Feature selection
    features = ["Open", "High", "Low", "Close", "Volume"]
    df = df.dropna()

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(df[features], df["Price_Movement"], test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

def train_decision_tree(X_train, X_test, y_train, y_test):
    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    # Predictions
    y_pred = clf.predict(X_test)

    # Evaluation
    print("Decision Tree Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

def main():
    parser = argparse.ArgumentParser(description="Train Decision Tree for stock price movement prediction.")
    parser.add_argument("input_file", help="Path to the cleaned CSV file.")
    args = parser.parse_args()

    X_train, X_test, y_train, y_test = load_data(args.input_file)
    train_decision_tree(X_train, X_test, y_train, y_test)

if __name__ == "__main__":
    main()

