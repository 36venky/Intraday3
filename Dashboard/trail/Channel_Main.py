import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.linear_model import LinearRegression

# =========================================================
# 🔹 SWING POINTS
# =========================================================
def swing_points(prices, window=3):
    highs, lows = [], []

    for i in range(window, len(prices) - window):
        if prices[i] == max(prices[i-window:i+window+1]):
            highs.append(i)

        if prices[i] == min(prices[i-window:i+window+1]):
            lows.append(i)

    return lows, highs


# =========================================================
# 🔹 FIT LINE + R2
# =========================================================
def fit_line(indices, prices):
    X = np.array(indices).reshape(-1, 1)
    y = prices[indices]

    model = LinearRegression().fit(X, y)

    y_pred = model.predict(X)

    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)

    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    return model.coef_[0], model.intercept_, r2


# =========================================================
# 🔹 CHECK FIT QUALITY
# =========================================================
def is_good_fit(indices, prices, slope, intercept, tol=0.003):
    for i in indices:
        expected = slope * i + intercept
        diff = abs(prices[i] - expected) / abs(expected)

        if diff > tol:
            return False
    return True


# =========================================================
# 🔹 BUILD TRENDLINES (PROGRESSIVE)
# =========================================================
def build_trendlines(indices, prices, tol=0.003, min_points=3, r2_min=0.95):

    lines = []
    n = len(indices)

    i = 0

    while i < n - 1:

        current_points = [indices[i], indices[i+1]]
        j = i + 2

        while j < n:
            trial = current_points + [indices[j]]

            slope, intercept, r2 = fit_line(trial, prices)

            if is_good_fit(trial, prices, slope, intercept, tol):
                current_points.append(indices[j])
                j += 1
            else:
                break

        if len(current_points) >= min_points:
            slope, intercept, r2 = fit_line(current_points, prices)

            if r2 >= r2_min:
                score = len(current_points) * r2
                lines.append((slope, intercept, current_points, r2, score))

        i += 1

    return lines


# =========================================================
# 🔹 REMOVE OVERLAPPING LINES
# =========================================================
def remove_overlapping(lines, slope_tol=1e-3, intercept_tol=1.0):

    lines = sorted(lines, key=lambda x: x[4], reverse=True)  # sort by score

    filtered = []

    for line in lines:
        slope, intercept, pts, r2, score = line

        duplicate = False

        for f in filtered:
            s2, c2, pts2, _, _ = f

            # similar slope/intercept
            if abs(slope - s2) < slope_tol and abs(intercept - c2) < intercept_tol:
                duplicate = True
                break

            # overlapping points
            common = set(pts).intersection(set(pts2))
            if len(common) >= 2:
                duplicate = True
                break

        if not duplicate:
            filtered.append(line)

    return filtered


# =========================================================
# 🔹 MAIN
# =========================================================
def main():

    ticker = "ABREL.NS"

    df = yf.download(ticker, period="15d", interval="15m", auto_adjust=False)
    df = df[['Open','High','Low','Close']].apply(pd.to_numeric, errors='coerce').dropna()

    prices = df['Close'].to_numpy()

    lows, highs = swing_points(prices, window=3)

    # =====================================================
    # 🔹 BUILD LINES
    # =====================================================
    low_lines = build_trendlines(lows, prices, tol=0.004, r2_min=0.85)
    high_lines = build_trendlines(highs, prices, tol=0.004, r2_min=0.85)

    # Remove overlaps
    low_lines = remove_overlapping(low_lines)
    high_lines = remove_overlapping(high_lines)

    # =====================================================
    # 🔹 PLOT
    # =====================================================
    x = np.arange(len(prices))

    plt.figure(figsize=(14,6))
    plt.plot(prices, alpha=0.6, label="Price")

    plt.scatter(lows, prices[lows], color='red', s=20, label="Lows")
    plt.scatter(highs, prices[highs], color='green', s=20, label="Highs")

    # 🔴 SUPPORT
    for slope, intercept, pts, r2, score in low_lines:
        start = pts[0]
        end = pts[-1]

        xr = np.arange(start, end+1)
        yr = slope * xr + intercept

        plt.plot(xr, yr, 'r--', alpha=0.8)

    # 🟢 RESISTANCE
    for slope, intercept, pts, r2, score in high_lines:
        start = pts[0]
        end = pts[-1]

        xr = np.arange(start, end+1)
        yr = slope * xr + intercept

        plt.plot(xr, yr, 'g--', alpha=0.8)

    plt.title("Clean Trendlines (R² + Overlap Filtered)")
    plt.legend()
    plt.grid(alpha=0.2)
    plt.show()


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    main()