import pandas as pd
import logging

def Volume(data, ticker, length, default=False):
    # Validate input
    if (ticker not in data 
        or data[ticker].empty 
        or "Volume" not in data[ticker].columns):
        
        logging.warning(f"[{ticker}] No volume data available")
        return default, 0, 0

    df = data[ticker][["Volume"]].copy()

    # Remove duplicate indices (keep latest)
    df = df[~df.index.duplicated(keep="last")]

    # Compute rolling VMA
    df[f"VMA_{length}"] = df["Volume"].rolling(window=length).mean()

    latest_volume = df["Volume"].iloc[-1]
    latest_vma = df[f"VMA_{length}"].iloc[-1]

    # Convert numpy types if needed
    if hasattr(latest_volume, "item"):
        latest_volume = latest_volume.item()
    if hasattr(latest_vma, "item"):
        latest_vma = latest_vma.item()

    # If values are valid, return comparison
    if pd.notnull(latest_volume) and pd.notnull(latest_vma):
        return latest_volume >= latest_vma, latest_volume, latest_vma

    return default, 0, 0

# import yfinance as yf

# tickers = ["KPEL.NS"]

# data = yf.download(
#     tickers=tickers,
#     interval="15m",
#     period="5d",
#     group_by="ticker",
#     auto_adjust=True,
#     progress=False
# )

# for ticker in tickers:
#     is_high, vol, vma = Volume(data, ticker, length=5)
#     print(f"{ticker} Volume Check")
#     print("High Volume?", is_high)
#     print("Latest Volume:", vol)
#    print("VMA:", vma)
