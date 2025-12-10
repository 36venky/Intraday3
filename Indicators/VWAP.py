import pandas as pd
import yfinance as yf

def VWAP(df):
    # Handle MultiIndex (from yfinance with multiple tickers)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Validate required columns
    required = {"High", "Low", "Close", "Volume"}
    if not required.issubset(df.columns) or df.empty:
        return None  # or float("nan")

    # Make an explicit copy to avoid SettingWithCopyWarning
    df = df.copy()

    # Typical price
    tp = (df["High"] + df["Low"] + df["Close"]) / 3

    # VWAP calculation
    df["VWAP"] = (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()

    return df["VWAP"]

# # Download data
# tickers = ["ETERNAL.NS", "SCI.NS"]

# data = yf.download(
#     tickers=tickers,
#     interval="15m",
#     period="5d",
#     group_by="ticker",
#     auto_adjust=True,
#     progress=False
# )

# # Compute VWAP for each ticker
# for ticker in tickers:
#     vwap_series = VWAP(data[ticker])
#     if vwap_series is not None:
#         print(f"{ticker} VWAP: {vwap_series.iloc[-1]}")
#     else:
#         print(f"{ticker} VWAP: Data not available")
