import numpy as np
import yfinance as yf
import pandas as pd
import math
import logging
import os
from .Plot import *

def is_volatile(df_slice, threshold=0.002):
        returns = df_slice['Close'].pct_change().dropna()
        volatility = returns.std()
        return volatility > threshold, volatility

def is_fluctuation(ticker):
    try:
        # ✅ Download all tickers at once (much faster)
        data = yf.download(
            tickers=ticker,
            interval='1m',
            period='1d',
            progress=False,
            auto_adjust=True,
            group_by='ticker'
        )
    except Exception as e:
        logging.error(f"Download error for batch: {e}")

    try:
        df = data[ticker][['Open', 'High', 'Low', 'Close']].copy()
    except KeyError:
        logging.warning(f"[{ticker}] Data not found in batch download.")
    
    df.index = df.index.tz_convert('Asia/Kolkata')
    df = df.between_time("09:15", "15:30")
    
    if df.empty or len(df) < 5:
        logging.warning(f"[{ticker}] Not enough data for fluctuation check ({len(df)} rows)")
        return False
    
    from sklearn.linear_model import LinearRegression
    import numpy as np

    y = df['Close'].values.reshape(-1, 1)
    x = np.arange(len(y)).reshape(-1, 1)

    model = LinearRegression().fit(x, y)
    r2 = model.score(x, y)

    with open("Fluctuation.txt", "a", encoding="utf-8") as f:
        if r2 > 0.80:
            line = (f"{ticker} ✅ (R² = {r2:.2f})")
            #print(line)
            f.write(line + "\n")
            P.save_line_chart(df,ticker, column="Close")
            return True , r2
        else:
            line = (f"{ticker} ❌ (R² = {r2:.2f})")
            #print(line)
            f.write(line + "\n")
            return False , r2
        
#print(is_fluctuation("ETERNAL.NS"))


# import numpy as np
# import yfinance as yf
# import pandas as pd
# import math
# import logging
# from sklearn.linear_model import LinearRegression
# from datetime import datetime

# def is_fluctuation(ticker):
#     try:
#         data = yf.download(
#             tickers=ticker,
#             interval='1m',
#             period='1d',
#             progress=False,
#             auto_adjust=True,
#             group_by='ticker'
#         )
#     except Exception as e:
#         logging.error(f"Download error for {ticker}: {e}")
#         return False

#     try:
#         df = data[ticker][['Open', 'High', 'Low', 'Close']].copy()
#     except KeyError:
#         logging.warning(f"[{ticker}] Data not found.")
#         return False

#     # Convert to IST and filter market hours
#     df.index = df.index.tz_convert('Asia/Kolkata')
#     df = df.between_time("09:15", "15:30")

#     if df.empty or len(df) < 20:
#         logging.warning(f"[{ticker}] Not enough data ({len(df)} rows)")
#         return False

#     # Take last 60 candles
#     end_index = len(df)
#     start_index = max(0, end_index - 60)
#     df_slice = df.iloc[start_index:end_index]

#     # --- Volatility Calculation ---
#     returns = df_slice['Close'].pct_change().dropna()
#     volatility = returns.std()

#     # --- Linear regression ---
#     y = df_slice['Close'].values.reshape(-1, 1)
#     x = np.arange(len(y)).reshape(-1, 1)
#     model = LinearRegression().fit(x, y)

#     r2 = model.score(x, y)
#     slope = model.coef_[0][0]

#     # Convert slope to angle
#     angle = math.degrees(math.atan(slope))

#     # --- Sideways detection ---
#     price_range = df_slice['High'].max() - df_slice['Low'].min()
#     avg_price = df_slice['Close'].mean()
#     range_percent = (price_range / avg_price) * 100

#     # --- Time based volatility threshold ---
#     now = datetime.now().strftime("%H:%M")

#     if now < "10:00":
#         vol_threshold = 0.006
#     else:
#         vol_threshold = 0.004

#     # --- Final logic ---
#     if volatility < vol_threshold and r2 > 0.50 and range_percent > 0.15:

#         line = (f"{ticker} ✅ Stable | Vol={volatility:.4f} | R²={r2:.2f} "
#                 f"| Angle={angle:.2f}° | Range={range_percent:.2f}%")

#         print(line)

#         with open("Fluctuation.txt", "a", encoding="utf-8") as f:
#             f.write(line + "\n")

#         return True

#     else:
#         line = (f"{ticker} ❌ Volatile/Sideways | Vol={volatility:.4f} | R²={r2:.2f} "
#                 f"| Angle={angle:.2f}° | Range={range_percent:.2f}%")

#         print(line)

#         with open("Fluctuation.txt", "a", encoding="utf-8") as f:
#             f.write(line + "\n")

#         return False
