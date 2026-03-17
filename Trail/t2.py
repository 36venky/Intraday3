import numpy as np

def detect_all_v_shapes(prices, lookback=100, min_drop=0.03, min_rise=0.03,
                        left_window=20, right_window=20):

    prices = np.asarray(prices)
    N = len(prices)
    
    v_pivots = []

    start = max(1, N - lookback)

    for i in range(start, N-1):

        # ---- Pivot Condition ----
        if prices[i] < prices[i-1] and prices[i] < prices[i+1]:

            # ----- Left Side -----
            left_start = max(0, i - left_window)
            left_slice = prices[left_start:i]

            if len(left_slice) == 0:
                continue

            left_high = np.max(left_slice)
            drop = (left_high - prices[i]) / left_high

            if drop < min_drop:
                continue

            # ----- Right Side -----
            right_end = min(N, i + right_window)
            right_slice = prices[i:right_end]

            if len(right_slice) == 0:
                continue

            right_high = np.max(right_slice)
            rise = (right_high - prices[i]) / prices[i]

            if rise < min_rise:
                continue

            # ---- Valid V Found ----
            v_pivots.append(i)

    return v_pivots

import matplotlib.pyplot as plt
import yfinance as yf

data = yf.download("IRCTC.NS", interval="15m", period="5d")
prices = data['Close'].values

pivots = detect_all_v_shapes(prices, lookback=150,
                             min_drop=0.025,
                             min_rise=0.025)

print("Total V Shapes Found:", len(pivots))
print("Pivot Indexes:", pivots)

plt.plot(prices)

for p in pivots:
    plt.scatter(p, prices[p], s=100)

plt.title("All Detected V Shapes")
plt.show()
