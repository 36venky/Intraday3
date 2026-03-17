"""
    Good !!

"""

import numpy as np

def detect_filtered_reversals(prices, min_move=0.01):
    """
    min_move = minimum percentage move between swings (e.g., 0.01 = 1%)
    """
    #print(data.head())
    prices = np.asarray(prices).flatten()
    prices = prices[~np.isnan(prices)]

    if len(prices) < 3:
        return [], []

    diff = np.diff(prices)

    raw_highs = []
    raw_lows = []

    # Step 1: detect all raw reversals
    for i in range(1, len(diff)):
        if diff[i-1] > 0 and diff[i] < 0:
            raw_highs.append(i)
        elif diff[i-1] < 0 and diff[i] > 0:
            raw_lows.append(i)

    # Step 2: filter weak ones
    filtered_highs = []
    filtered_lows = []

    last_kept_index = 0

    for idx in sorted(raw_highs + raw_lows):

        move = abs(prices[idx] - prices[last_kept_index]) / prices[last_kept_index]

        if move >= min_move:
            if idx in raw_highs:
                filtered_highs.append(idx)
            else:
                filtered_lows.append(idx)

            last_kept_index = idx

    return filtered_lows, filtered_highs

import matplotlib.pyplot as plt
import yfinance as yf

data = yf.download("ETERNAL.NS", interval="15m", period="10d")

data = data.dropna()
prices = data['Close'].dropna().to_numpy()

lows, highs = detect_filtered_reversals(prices, min_move=0.005)

plt.plot(prices)

plt.scatter(lows, prices[lows], s=30, color='red')
plt.scatter(highs, prices[highs], s=30, color='green')

plt.title("All Reversal Points")
plt.show()

