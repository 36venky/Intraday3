import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# =========================================================
# 🔹 REVERSAL DETECTION
# =========================================================
def detect_filtered_reversals(prices, min_move=0.005):
    prices = np.asarray(prices).flatten()
    prices = prices[~np.isnan(prices)]

    if len(prices) < 3:
        return [], []

    diff = np.diff(prices)

    raw_highs, raw_lows = [], []

    # Detect raw reversals
    for i in range(1, len(diff)):
        if diff[i-1] > 0 and diff[i] < 0:
            raw_highs.append(i)
        elif diff[i-1] < 0 and diff[i] > 0:
            raw_lows.append(i)

    # Filter weak moves
    filtered_highs, filtered_lows = [], []
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


# =========================================================
# 🔹 TOUCH DETECTION
# =========================================================
def count_touches(prices, start_idx, level, buffer_pct):
    touches = []

    for i in range(start_idx + 1, len(prices)):
        diff = abs(prices[i] - level) / level

        if diff <= buffer_pct:
            touches.append(i)

    return touches


# =========================================================
# 🔹 DUPLICATE LEVEL FILTER
# =========================================================
def is_far_from_existing(level, existing_levels, tol=0.001):
    return all(abs(level - l) / l > tol for l in existing_levels)


# =========================================================
# 🔹 MAIN
# =========================================================
def main():

    ticker = "ABREL.NS"
    data = yf.download(ticker, interval="15m", period="15d")

    data = data.dropna()
    prices = data['Close'].to_numpy()

    # PARAMETERS
    min_move = 0.005     # swing filter
    buffer_pct = 0.001   # 0.1% tolerance
    min_touches = 2      # minimum confirmations

    lows, highs = detect_filtered_reversals(prices, min_move)

    plt.figure(figsize=(14, 6))
    plt.plot(prices, label="Price", alpha=0.6)

    support_levels = []
    resistance_levels = []

    # =====================================================
    # 🔴 SUPPORT LEVELS
    # =====================================================
    for idx in lows:
        level = prices[idx]

        # avoid duplicate nearby levels
        if not is_far_from_existing(level, support_levels, buffer_pct):
            continue

        touches = count_touches(prices, idx, level, buffer_pct)

        if len(touches) >= min_touches:
            support_levels.append(level)

            end_idx = touches[-1]

            plt.hlines(
                y=level,
                xmin=idx,
                xmax=end_idx,
                colors='red',
                linestyles='dashed',
                alpha=0.7
            )

    # =====================================================
    # 🟢 RESISTANCE LEVELS
    # =====================================================
    for idx in highs:
        level = prices[idx]

        if not is_far_from_existing(level, resistance_levels, buffer_pct):
            continue

        touches = count_touches(prices, idx, level, buffer_pct)

        if len(touches) >= min_touches:
            resistance_levels.append(level)

            end_idx = touches[-1]

            plt.hlines(
                y=level,
                xmin=idx,
                xmax=end_idx,
                colors='green',
                linestyles='dashed',
                alpha=0.7
            )

    plt.title("Support & Resistance (Multi-Touch Filtered)")
    plt.legend()
    plt.grid(alpha=0.2)
    plt.show()


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    main()