import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

from sklearn.linear_model import LinearRegression

# =========================================================
# 🔹 SWING DETECTION USING HIGH / LOW
# =========================================================
def swing_points(highs, lows, window=3):

    swing_highs = []
    swing_lows = []

    for i in range(window, len(highs) - window):

        # Swing High
        if highs[i] == max(highs[i-window:i+window+1]):
            swing_highs.append(i)

        # Swing Low
        if lows[i] == min(lows[i-window:i+window+1]):
            swing_lows.append(i)

    return swing_lows, swing_highs


# =========================================================
# 🔹 FILTER WEAK SWINGS
# =========================================================
def filter_swings(indices, values, min_move=0.005):

    if len(indices) == 0:
        return []

    filtered = [indices[0]]

    for idx in indices[1:]:

        prev = filtered[-1]

        move = abs(values[idx] - values[prev]) / values[prev]

        if move >= min_move:
            filtered.append(idx)

    return filtered


# =========================================================
# 🔹 TOUCH DETECTION
# =========================================================
def count_touches(series, start_idx, level, buffer_pct=0.001):

    touches = []

    for i in range(start_idx + 1, len(series)):

        diff = abs(series[i] - level) / level

        if diff <= buffer_pct:
            touches.append(i)

    return touches


# =========================================================
# 🔹 DUPLICATE LEVEL FILTER
# =========================================================
def is_far_from_existing(level, existing, tol=0.001):

    return all(abs(level - x) / x > tol for x in existing)


# =========================================================
# 🔹 FIT LINE
# =========================================================
def fit_line(indices, values):

    X = np.array(indices).reshape(-1, 1)

    y = values[indices]

    model = LinearRegression().fit(X, y)

    y_pred = model.predict(X)

    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)

    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    return model.coef_[0], model.intercept_, r2


# =========================================================
# 🔹 CHECK LINE QUALITY
# =========================================================
def is_good_fit(indices, values, slope, intercept, tol=0.003):

    for i in indices:

        expected = slope * i + intercept

        diff = abs(values[i] - expected) / abs(expected)

        if diff > tol:
            return False

    return True


# =========================================================
# 🔹 BUILD TRENDLINES
# =========================================================
def build_trendlines(indices,
                     values,
                     tol=0.003,
                     min_points=3,
                     r2_min=0.85):

    lines = []

    n = len(indices)

    i = 0

    while i < n - 1:

        current = [indices[i], indices[i+1]]

        j = i + 2

        while j < n:

            trial = current + [indices[j]]

            slope, intercept, r2 = fit_line(trial, values)

            if is_good_fit(trial, values, slope, intercept, tol):
                current.append(indices[j])
                j += 1
            else:
                break

        if len(current) >= min_points:

            slope, intercept, r2 = fit_line(current, values)

            if r2 >= r2_min:

                score = len(current) * r2

                lines.append(
                    (slope, intercept, current, r2, score)
                )

        i += 1

    return lines


# =========================================================
# 🔹 REMOVE OVERLAPS
# =========================================================
def remove_overlapping(lines,
                       slope_tol=1e-3,
                       intercept_tol=1.0):

    lines = sorted(lines,
                   key=lambda x: x[4],
                   reverse=True)

    filtered = []

    for line in lines:

        slope, intercept, pts, r2, score = line

        duplicate = False

        for f in filtered:

            s2, c2, pts2, _, _ = f

            # Similar line
            if abs(slope - s2) < slope_tol \
               and abs(intercept - c2) < intercept_tol:
                duplicate = True
                break

            # Common points
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

    ticker = "ETERNAL.NS"

    df = yf.download(
        ticker,
        interval="15m",
        period="5d",
        auto_adjust=False
    )

    df = df[['Open', 'High', 'Low', 'Close']]

    df = df.apply(pd.to_numeric,
                  errors='coerce').dropna()

    highs = df['High'].to_numpy()
    lows = df['Low'].to_numpy()
    closes = df['Close'].to_numpy()

    # =====================================================
    # PARAMETERS
    # =====================================================
    window = 3
    min_move = 0.005
    buffer_pct = 0.001
    min_touches = 2

    # =====================================================
    # SWING POINTS
    # =====================================================
    swing_lows, swing_highs = swing_points(
        highs,
        lows,
        window=window
    )

    # Filter weak swings
    swing_lows = filter_swings(
        swing_lows,
        lows,
        min_move=min_move
    )

    swing_highs = filter_swings(
        swing_highs,
        highs,
        min_move=min_move
    )

    # =====================================================
    # BUILD TRENDLINES
    # =====================================================
    support_lines = build_trendlines(
        swing_lows,
        lows,
        tol=0.004,
        r2_min=0.85
    )

    resistance_lines = build_trendlines(
        swing_highs,
        highs,
        tol=0.004,
        r2_min=0.85
    )

    support_lines = remove_overlapping(support_lines)
    resistance_lines = remove_overlapping(resistance_lines)

    # =====================================================
    # PLOT
    # =====================================================
    x = np.arange(len(closes))

    plt.figure(figsize=(16, 7))

    plt.plot(closes,
             label="Close Price",
             color='purple',
             linewidth=1.5,
             alpha=0.8)

    # =====================================================
    # SWING MARKERS
    # =====================================================
    plt.scatter(
        swing_lows,
        lows[swing_lows],
        color='red',
        s=35,
        label='Swing Lows'
    )

    plt.scatter(
        swing_highs,
        highs[swing_highs],
        color='lime',
        s=35,
        label='Swing Highs'
    )

    # =====================================================
    # HORIZONTAL SUPPORTS
    # =====================================================
    used_supports = []

    for idx in swing_lows:

        level = lows[idx]

        if not is_far_from_existing(
            level,
            used_supports,
            buffer_pct
        ):
            continue

        touches = count_touches(
            lows,
            idx,
            level,
            buffer_pct
        )

        if len(touches) >= min_touches:

            used_supports.append(level)

            plt.hlines(
                y=level,
                xmin=idx,
                xmax=touches[-1],
                colors='red',
                linestyles='dashed',
                alpha=0.5
            )

    # =====================================================
    # HORIZONTAL RESISTANCE
    # =====================================================
    used_resistance = []

    for idx in swing_highs:

        level = highs[idx]

        if not is_far_from_existing(
            level,
            used_resistance,
            buffer_pct
        ):
            continue

        touches = count_touches(
            highs,
            idx,
            level,
            buffer_pct
        )

        if len(touches) >= min_touches:

            used_resistance.append(level)

            plt.hlines(
                y=level,
                xmin=idx,
                xmax=touches[-1],
                colors='lime',
                linestyles='dashed',
                alpha=0.5
            )

    # =====================================================
    # TRENDLINES
    # =====================================================
    for slope, intercept, pts, r2, score in support_lines:

        xr = np.arange(pts[0], pts[-1] + 1)

        yr = slope * xr + intercept

        plt.plot(
            xr,
            yr,
            'r--',
            linewidth=2,
            alpha=0.9
        )

    for slope, intercept, pts, r2, score in resistance_lines:

        xr = np.arange(pts[0], pts[-1] + 1)

        yr = slope * xr + intercept

        plt.plot(
            xr,
            yr,
            'g--',
            linewidth=2,
            alpha=0.9
        )

    # =====================================================
    # FINAL
    # =====================================================
    plt.title(
        f"{ticker} | Support & Resistance + Trendlines"
    )

    plt.grid(alpha=0.2)

    plt.legend()

    plt.tight_layout()

    plt.show()

# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    main()