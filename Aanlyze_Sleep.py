import yfinance as yf 
import pandas as pd 
import numpy as np
import logging
from datetime import datetime, timedelta, time as dtime
import os , sys
from Dependencies import *
from Indicators import *
from Dependencies.Loggings import logger as L
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# --- MongoDB Setup ---
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["Trail1"]
buy_collection = db["buy_signals"]
sell_collection = db["sell_signals"]

# --- Global Buy State ---
buy_triggered = {}
sell_triggered = {}
#M.start_whatsapp_worker()

def analyze_real_time(tickers):
    now = datetime.now().time()
    start_time = dtime(11, 14)
    end_time   = dtime(14, 10)

    T = 0 #

    if T == 0:
        if not (start_time <= now <= end_time and 0 <= datetime.now().weekday() <= 4):
            return  # Market closed

    try:
        data = yf.download(
            tickers=tickers,
            interval='15m',
            period='6d',
            progress=False,
            auto_adjust=True,
            group_by='ticker'
        )
    except Exception as e:
        logging.error(f"YF batch download failed: {e}")
        return

    for ticker in tickers:

        # ---- GET DF SAFELY ----
        try:
            df = data[ticker][['Open','High','Low','Close','Volume']].copy()
            df = df.dropna(subset=['Open','High','Low','Close','Volume'])
        except Exception:
            L.invalid(f"{ticker},NO_DATA")
            continue

        if df.empty or len(df) < 60:
            L.invalid(f"{ticker},EMPTY_OR_SHORT")
            continue
        
        # ---- TIMEZONE FIX ----
        try:
            df.index = df.index.tz_convert("Asia/Kolkata")
        except:
            df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata")

        df = df.between_time("09:15","15:30")
        if len(df) < 20:
            L.invalid(f"{ticker},INSUFFICIENT_AFTER_FILTER")
            continue

        i = -1
        price = df["Close"].iloc[i]

        # ---- INDICATORS ----
        df["EMA5"]  = EMA(df,5)
        df["EMA9"]  = EMA(df,9)
        df["EMA21"] = EMA(df,21)

        # rsi = RSI(df,14)
        # vwap = VWAP(df)

        # Vol, vol_val, vol_vma = Volume1(ticker)
        # Frac = (vol_val / vol_vma) if vol_vma else 0

        # # -------- Volume ----------
        # vol_df = data[ticker][["Volume"]].dropna()

        # # Not enough data for rolling VMA
        # if vol_df.empty or len(vol_df) < 5:
        #     L.invalid(f"{ticker},VOLUME_NOT_ENOUGH_DATA")
        #     Vol = False
        #     Frac = 0
        # else:
        #     # Remove duplicated timestamps
        #     vol_df = vol_df[~vol_df.index.duplicated(keep="last")]

        #     # Rolling VMA
        #     vol_df["VMA_5"] = vol_df["Volume"].rolling(5).mean()

        #     latest_volume = vol_df["Volume"].iloc[-1]
        #     latest_vma5 = vol_df["VMA_5"].iloc[-1]

        #     # Convert numpy → python
        #     if hasattr(latest_volume, "item"):
        #         latest_volume = latest_volume.item()
        #     if hasattr(latest_vma5, "item"):
        #         latest_vma5 = latest_vma5.item()

        #     # Fraction (only valid if VMA is non-zero)
        #     if pd.isna(latest_vma5) or latest_vma5 == 0:
        #         Vol = False
        #         Frac = 0
        #     else:
        #         Frac = latest_volume / latest_vma5
        #         Vol = latest_volume >= latest_vma5


        X = Xval(price)
        threshold = gat_angle(price) * X

        # ---- ANGLE ----
        if df["EMA5"].isna().sum() > 0:
            L.invalid(f"{ticker},EMA_NAN")
            continue
        
        last5_ema5 = df["EMA5"].tail(5).round(2).tolist()
        ema_diff = df["EMA5"].iloc[i] - df["EMA5"].iloc[i-1]
        angle = math.degrees(math.atan(ema_diff))

        # --------------------------
        #   BUY
        # --------------------------
        if ticker not in buy_triggered:
            buy_triggered[ticker] = False

        strong_green = (
            df["Close"].iloc[i] > df["Open"].iloc[i] and
            abs(df["Close"].iloc[i] - df["Low"].iloc[i]) < 0.02 * price
        )

        BUY = (
            not buy_triggered[ticker] and
            strong_green and
            angle >= threshold and
            df["EMA9"].iloc[i] > df["EMA21"].iloc[i]
        )

        if BUY:
            signal_time = df.index[i].strftime('%Y-%m-%d %H:%M')

            intra = check_intraday_tradable_yf(ticker)
            fluctuate, r2 = is_fluctuation(ticker)

            if intra and fluctuate:
                write("1Buy.txt", f"{ticker},{price:.2f},{signal_time},{datetime.now().strftime('%H:%M:%S')},{last5_ema5},{ema_diff:.2f},{r2:.2f}\n")
                L.buy(f"{ticker},{price:.2f},{signal_time},{datetime.now().strftime('%H:%M:%S')},{ema_diff:.2f},{angle:.2f},{threshold:.2f}")

                save_line_chart(df, ticker=ticker, column="Close")

                buy_collection.insert_one({
                    "Ticker": ticker,
                    "Price": price,
                    "Time": datetime.now()
                })

                buy_triggered[ticker] = True
            else:
                L.isvalid(f"{ticker},{r2:.2f}")

        else:
            L.invalid(f"{ticker},{price:.2f},{angle:.2f},{threshold:.2f},{last5_ema5}")

        # --------------------------
        #   SELL
        # --------------------------
        if ticker not in sell_triggered:
            sell_triggered[ticker] = False

        strong_red = (
            df["Close"].iloc[i] < df["Open"].iloc[i] and
            abs(df["High"].iloc[i] - df["Close"].iloc[i]) < 0.02 * price
        )

        SELL = (
            not sell_triggered[ticker] and
            strong_red and
            angle <= -threshold and
            df['EMA9'].iloc[i] < df['EMA21'].iloc[i]
        )

        if SELL:
            signal_time = df.index[i].strftime('%Y-%m-%d %H:%M')

            intra = check_intraday_tradable_yf(ticker)
            fluctuate, r2 = is_fluctuation(ticker)

            if intra and fluctuate:
                write("1Sell.txt", f"{ticker},{price:.2f},{signal_time},{datetime.now().strftime('%H:%M:%S')},{last5_ema5},{ema_diff:.2f},{r2:.2f}\n")
                L.sell(f"{ticker},{price:.2f},{signal_time},{datetime.now().strftime('%H:%M:%S')},{ema_diff:.2f},{angle:.2f},{threshold:.2f}")
                
                save_line_chart(df, ticker=ticker, column="Close")

                sell_collection.insert_one({
                    "Ticker": ticker,
                    "Price": price,
                    "Time": datetime.now()
                })

                sell_triggered[ticker] = True

            else:
                L.isvalid(f"{ticker},{r2:.2f}")
        else:
            L.invalid(f"{ticker},{price:.2f},{angle:.2f},{-threshold:.2f},{last5_ema5}")


def wait_until_next_15_min():
    now = datetime.now()
    next_time = (now + timedelta(minutes=15)).replace(second=0, microsecond=0)
    next_time -= timedelta(minutes=next_time.minute % 15)
    wait_seconds = (next_time - now).total_seconds()
    logging.info(f"Waiting {int(wait_seconds)}s until next 15-min {next_time.strftime('%H:%M:%S')}")
    tm.sleep(wait_seconds)        
