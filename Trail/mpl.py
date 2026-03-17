import yfinance as yf
import mplfinance as mpf    
import logging
import matplotlib.pyplot as plt
import pandas as pd

def Download(tickers):
    try:
        data = yf.download(
            tickers=tickers,
            interval='5m',
            period='1d',
            progress=False,
            auto_adjust=True,
            group_by='ticker'
        )
    except Exception as e:
        logging.error(f"Download error : {e}")
        return
    
    for ticker in tickers:
        try:
            df = data[ticker][['Open', 'High', 'Low', 'Close']].copy()
        except KeyError:
            logging.warning(f"[{ticker}] Data not found.")
            continue

        # Convert to IST
        try:
            df.index = df.index.tz_convert('Asia/Kolkata')
        except:
            df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')

        # Filter market hours
        df = df.between_time("09:15", "15:30")

        if df.empty:
            continue
        
        #print(df.iloc[-55])
        #print(df.head())
        #print(df.index[-1])
        # ✅ Now plot directly (DO NOT overwrite df)
        mc = mpf.make_marketcolors(
            up='lime',
            down='red',
            edge='inherit',
            wick='white',
            volume='inherit'
        )

        dark_style = mpf.make_mpf_style(
            base_mpf_style='nightclouds',
            marketcolors=mc,
            facecolor='black',
            figcolor='black',
            gridcolor='gray'
        )

        mpf.plot(
            df,
            type='candle',
            style=dark_style,
            figratio=(16, 9),     # widescreen ratio
            figscale=1.0          # increases overall size
        )

Download(["ETERNAL.NS"])