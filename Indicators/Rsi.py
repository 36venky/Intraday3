import pandas as pd
import yfinance as yf

def RSI(df, length=14):
    # Make an explicit copy to avoid SettingWithCopyWarning
    df = df.copy()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/length, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1/length, min_periods=length).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Assign safely
    df.loc[:, 'RSI'] = rsi

    return df['RSI']

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

# # Compute RSI for each ticker
# for ticker in tickers:
#     rsi_series = RSI(data[ticker], 14)
#     print(f"{ticker} RSI: {rsi_series.iloc[-1]:.2f}")
