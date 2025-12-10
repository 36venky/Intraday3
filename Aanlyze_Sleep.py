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
    start_time = dtime(9, 55)
    end_time   = dtime(14, 50)

    T = 1 # test flag to force run anytime

    if (start_time <= now <= end_time and 0 <= datetime.now().weekday() <= 4) or T == 1:
        try:
            data = yf.download(
                tickers=tickers,
                interval='15m',
                period='5d',
                progress=False,
                auto_adjust=True,
                group_by='ticker'
            )
        except Exception as e:
            logging.error(f"Download error for batch: {e}")
            return

        for ticker in tickers:
            try:
                df = data[ticker][['Open', 'High', 'Low', 'Close','Volume']].copy()
                #logging.info(f"[{ticker}] Data downloaded successfully with {len(df)} records.")
            except KeyError:
                logging.warning(f"[{ticker}] Data not found in batch download.")
                continue

            if df.empty or len(df) < 55:
                continue

            if df.index.tz is None:
                df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
            else:
                df.index = df.index.tz_convert("Asia/Kolkata")

            df = df.between_time("09:15", "15:30")

            i = -1  # Last row index
            price = df["Close"].iloc[i] # Current price

            # Calculate indicators
            df["EMA5"] = EMA(df, 5)
            df["EMA9"] = EMA(df, 9)
            df["EMA21"] = EMA(df, 21)

            Vol , vol_val , vol_vma = Volume(data, ticker, length=5)
            Frac = vol_val / vol_vma if vol_val != 0 else 0
            Rsi = RSI(df, 14)
            Vwap = VWAP(df)
            diff = df['EMA5'].iloc[i] - df['EMA5'].iloc[i-1]

            # X for specific price levels
            X = int(1)
            X = Xval(price)

            # Angle calculations
            try:
                ema_diff = df['EMA5'].iloc[i] - df['EMA5'].iloc[i - 1]
                angle = math.degrees(math.atan(ema_diff))
            except IndexError:
                logging.error(f"[{ticker}] Not enough candles for angle calculation.")
                continue
            
            # --- BUY Logic ---
            threshold = gat_angle(price) * X
            strong_green = (
                df['Close'].iloc[i] > df['Open'].iloc[i]
                and abs(df['Close'].iloc[i] - df['Low'].iloc[i]) < 0.02 * df['Close'].iloc[i]  # body near low
            )

            if ticker not in buy_triggered:
                buy_triggered[ticker] = False

            BUY = strong_green and angle >= threshold and df['EMA9'].iloc[i] > df['EMA21'].iloc[i] and not buy_triggered[ticker]

            if BUY:
                signal_time = df.index[i].strftime('%Y-%m-%d %H:%M')

                url = get_company_name(ticker)
                intra = check_intraday_tradable_yf(ticker)
                comfirmed = comfirm(ticker)
                fluctuate , r2  = is_fluctuation(ticker)

                if intra and fluctuate:
                    write("1Buy.txt", f"{ticker},{price:.2f},{signal_time},{datetime.now().strftime('%H:%M:%S')},{Vol},{Frac:.2f},{Rsi.iloc[i]:.2f},{r2:.2f}\n")
                    L.buy(f"{ticker},{price:.2f},{signal_time},{diff:.2f},{angle:.2f},{threshold:.2f},{Vwap.iloc[i]:.2f},{Rsi.iloc[i]:.2f},{Frac:.2f},{r2:.2f},{url}")
                
                    buy_signal = {
                        "Ticker": ticker,
                        "Price": price,
                        "Time": datetime.now(),
                    }
                    buy_collection.insert_one(buy_signal)
                    buy_triggered[ticker] = True
                else:
                    L.isvalid(f"{ticker},{price:.2f},{signal_time},{diff:.2f},{angle:.2f},{threshold:.2f},{Vwap.iloc[i]:.2f},{Rsi.iloc[i]:.2f},{Frac:.2f},{r2:.2f},{url}")
            else:
                L.invalid(f"{ticker},{price:.2f},{angle:.2f},{threshold:.2f}")

            # --- SELL Logic ---
            if ticker not in sell_triggered:
                sell_triggered[ticker] = False
            
            strong_red_current = (
                df['Close'].iloc[i] < df['Open'].iloc[i]
                and abs(df['High'].iloc[i] - df['Close'].iloc[i]) < 0.02 * df['Close'].iloc[i] 
            )

            SELL = strong_red_current and angle <= -threshold and df['EMA9'].iloc[i] < df['EMA21'].iloc[i] and not sell_triggered[ticker]
            if SELL:
                signal_time = df.index[i].strftime('%Y-%m-%d %H:%M')

                url = get_company_name(ticker)
                intra = check_intraday_tradable_yf(ticker)
                comfirmed = comfirm(ticker)
                fluctuate , r2  = is_fluctuation(ticker)

                if intra  and fluctuate:
                    write("1Sell.txt", f"{ticker},{price:.2f},{signal_time},{datetime.now().strftime('%H:%M:%S')},{Vol},{Frac:.2f},{Rsi.iloc[i]:.2f},{r2:.2f}\n")
                    L.sell(f"{ticker},{price:.2f},{signal_time},{diff:.2f},{angle:.2f},{-threshold:.2f},{Vwap.iloc[i]:.2f},{Rsi.iloc[i]:.2f},{Frac:.2f},{r2:.2f},{url}")
                    sell_signal = {
                        "Ticker": ticker,
                        "Price": price,
                        "Time": datetime.now(),
                    }
                    sell_collection.insert_one(sell_signal)
                    sell_triggered[ticker] = True
                else:
                    L.isvalid(f"{ticker},{price:.2f},{signal_time},{diff:.2f},{angle:.2f},{-threshold:.2f},{Vwap.iloc[i]:.2f},{Rsi.iloc[i]:.2f},{Frac:.2f},{r2:.2f},{url}")
            else:
                L.invalid(f"{ticker},{price:.2f},{angle:.2f},{-threshold:.2f}")
    else:
        logging.info("Market is closed. Analysis skipped.")


def wait_until_next_15_min():
    now = datetime.now()
    next_time = (now + timedelta(minutes=15)).replace(second=0, microsecond=0)
    next_time -= timedelta(minutes=next_time.minute % 15)
    wait_seconds = (next_time - now).total_seconds()
    logging.info(f"Waiting {int(wait_seconds)}s until next 15-min {next_time.strftime('%H:%M:%S')}")
    tm.sleep(wait_seconds)          