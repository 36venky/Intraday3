import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import logging


def save_line_chart(df, ticker, column="Close", folder="Charts"):
    """
    Saves a gap-less intraday line chart (no overnight gaps).
    Safe for yfinance MultiIndex data.
    """

    os.makedirs(folder, exist_ok=True)

    # -------------------------------
    # FIX 1: Handle yfinance MultiIndex
    # -------------------------------
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)

    if column not in df.columns:
        logging.error(f"{ticker} - Column '{column}' not found. Available: {df.columns.tolist()}")
        return None

    # -------------------------------
    # FIX 2: Drop NaNs safely
    # -------------------------------
    df = df.dropna(subset=[column]).copy()

    if df.empty:
        logging.error(f"{ticker} - DataFrame empty after NaN removal")
        return None

    # -------------------------------
    # FIX 3: Remove time gaps (core)
    # -------------------------------
    x = np.arange(len(df))   # continuous index → NO gaps

    # -------------------------------
    # Plot
    # -------------------------------
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(10, 5))

    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    ax.plot(x, df[column].values, linewidth=2, color="green")

    ax.set_title(f"{ticker} - {column} Trend", color="white")
    ax.set_xlabel("Candles (15 min)", color="white")
    ax.set_ylabel(column, color="white")

    ax.grid(True, color="#333333")
    ax.tick_params(colors="white")

    # -------------------------------
    # X-axis labels only at day change
    # -------------------------------
    day_change = df.index.date != pd.Series(df.index.date).shift(1)
    ticks = np.where(day_change)[0]

    ax.set_xticks(ticks)
    ax.set_xticklabels(
        [df.index[i].strftime("%d %b") for i in ticks],
        rotation=45,
        color="white"
    )

    # -------------------------------
    # Save
    # -------------------------------
    file_path = f"{folder}/{ticker}.png"
    plt.savefig(file_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()

    logging.info(f"{ticker} - Chart saved")
    return file_path


# # =====================================================
# # TEST / USAGE
# # =====================================================
# if __name__ == "__main__":

#     logging.basicConfig(level=logging.INFO)

#     ticker = "ETERNAL.NS"

#     df = yf.download(
#         ticker,
#         period="5d",
#         interval="15m",
#         progress=False,
#         auto_adjust=True
#     )

#     path = save_line_chart(df, ticker=ticker, column="Close")

#     print("Saved chart to:", path)
