import numpy as np

def detect_sharp_points(prices,
                        lookback=150,
                        window=7,
                        min_move=0.025):

    prices = np.asarray(prices)
    N = len(prices)

    sharp_lows = []
    sharp_highs = []

    start = max(window, N - lookback)

    for i in range(start, N - window):

        local_window = prices[i-window:i+window+1]

        # ---- Local Low ----
        if prices[i] == np.min(local_window):

            left_high = np.max(prices[max(0, i-20):i])
            right_high = np.max(prices[i:min(N, i+20)])

            drop_left = (left_high - prices[i]) / left_high
            rise_right = (right_high - prices[i]) / prices[i]

            if drop_left >= min_move and rise_right >= min_move:
                sharp_lows.append(i)

        # ---- Local High ----
        if prices[i] == np.max(local_window):

            left_low = np.min(prices[max(0, i-20):i])
            right_low = np.min(prices[i:min(N, i+20)])

            rise_left = (prices[i] - left_low) / left_low
            drop_right = (prices[i] - right_low) / prices[i]

            if rise_left >= min_move and drop_right >= min_move:
                sharp_highs.append(i)

    return sharp_lows, sharp_highs


import matplotlib.pyplot as plt
import yfinance as yf

data = yf.download("ONESOURCE.NS", interval="15m", period="5d")
prices = data['Close'].values

lows, highs = detect_sharp_points(prices,
                                  lookback=150,
                                  window=3,
                                  min_move=0.02)

print("Sharp Lows:", lows)
print("Sharp Highs:", highs)

plt.plot(prices)

plt.scatter(lows, prices[lows], s=100)
plt.scatter(highs, prices[highs], s=100)

plt.title("Sharp Turning Points")
plt.show()
