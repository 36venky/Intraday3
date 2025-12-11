import matplotlib.pyplot as plt
import logging

def save_line_chart(df, ticker, column="Close", folder="Charts"):

    import os
    os.makedirs(folder, exist_ok=True)

    # --- Set background to black ---
    plt.style.use("default")
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    # --- Plot line in green ---
    ax.plot(df.index, df[column], linewidth=2, color="green")

    # --- Title + labels in white ---
    ax.set_title(f"{ticker} - {column} Trend", color="white")
    ax.set_xlabel("Date", color="white")
    ax.set_ylabel(column, color="white")

    # --- Grid in dark grey ---
    ax.grid(True, color="#333333")

    # --- Set tick color ---
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    file_path = f"{folder}/{ticker}.png"
    plt.savefig(file_path, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

    logging.info("Chart Added")
    return file_path

# import yfinance as yf

# ticker = "ETERNAL.NS"
# df = yf.download(ticker, period="1d", interval="1m")

# save_path = save_line_chart(df, column="Close", ticker=ticker)
# print("Saved chart to:", save_path)
