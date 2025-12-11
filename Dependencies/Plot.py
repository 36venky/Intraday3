import matplotlib.pyplot as plt
import logging

def save_line_chart(df,ticker, column="Close", folder="Charts"):

    import os
    os.makedirs(folder, exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df[column], linewidth=2)
    plt.title(f"{ticker} - {column} Trend")
    plt.xlabel("Date")
    plt.ylabel(column)
    plt.grid(True)

    file_path = f"{folder}/{ticker}.png"
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()  # Important: prevents display
    logging.info("Chart Added")
    return file_path

# import yfinance as yf

# ticker = "ETERNAL.NS"
# df = yf.download(ticker, period="2d", interval="1m")

# save_path = save_line_chart(df, column="Close", ticker=ticker)
# print("Saved chart to:", save_path)
