import json
import numpy as np
import os
import sys
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Dependencies import *
from Dependencies.Write import write


def load_stock_data(filename):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    target_dir = os.path.join(project_root, "Signals")

    filepath = os.path.join(target_dir, filename)

    # File missing
    if not os.path.exists(filepath):
        return {}

    # Empty file
    if os.path.getsize(filepath) == 0:
        return {}

    stock_data = {}

    try:

        with open(filepath, "r") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                try:
                    # Expected format:
                    # timestamp,ticker,smooth_val,r2,signal

                    parts = [x.strip() for x in line.split(",")]

                    if len(parts) < 5:
                        continue

                    timestamp = parts[0]
                    ticker = parts[1]
                    smooth_val = float(parts[2])
                    r2 = float(parts[3])
                    signal = parts[4]

                    stock_data[ticker] = {
                        "timestamp": timestamp,
                        "smooth_val": smooth_val,
                        "r2": r2,
                        "signal": signal
                    }

                except Exception:
                    continue

        return stock_data

    except Exception as e:
        print(f"TXT Load Error: {e}")
        return {}


def extract_features(data):
    """
    data:
    {
        "r2": value,
        "smooth_val": value
    }
    """

    r2 = data.get("r2", 0.0)
    smooth = data.get("smooth_val", 0.0)

    # Normalize values
    r2_strength = np.tanh(r2 / 100)

    smooth_strength = -np.tanh(smooth)

    return np.array([
        r2_strength,
        smooth_strength
    ])


def model_predict(all_stocks):
    """
    all_stocks:
    {
        "AAPL": {
            "r2": 192.44,
            "smooth_val": 1.82
        }
    }
    """

    scores = {}

    for ticker, data in all_stocks.items():

        features = extract_features(data)

        # weights for:
        # [r2, smooth]
        weights = np.array([0.6, 0.4])

        raw_score = np.dot(features, weights)

        # sigmoid probability
        prob = 1 / (1 + np.exp(-raw_score))

        scores[ticker] = prob

    return scores


def select_top(scores, k=10):

    sorted_items = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_items[:k]


# ------------------------------------------------
# MAIN
# ------------------------------------------------

def QuantFiltering(filename="1Breakouts.txt"):

    all_stocks = load_stock_data(filename)

    scores = model_predict(all_stocks)

    top_stocks = select_top(scores)

    # Output file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    target_dir = os.path.join(project_root, "Top")

    filepath = os.path.join(target_dir, "top_picks.txt")
    filename = "Top_" + filename
    for ticker, score in top_stocks:

        write(
            filename,
            f"{datetime.now().strftime('%H:%M:%S')},{ticker},{all_stocks[ticker]['smooth_val']:.4f},{all_stocks[ticker]['r2']:.2f}\n"
        )

    # Wait for queued writes if needed
    # write_queue.join()


if __name__ == "__main__":
    QuantFiltering("1Smooth.txt")